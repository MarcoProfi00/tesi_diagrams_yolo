"""
Renderizza il viewer SVG generale di una run della Pipeline 2.0.

Legge il modello elettrico dello step 13 e il layout guidato
dalle bbox dello step 14, e disegna simboli semplici in stile simulatore Falstad.
"""

from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from .component_library import component_spec, normalize_component_type
from .contracts import VIEWER_LAYOUT_NAME, VIEWER_MODEL_NAME, VIEWER_RENDER_VERSION, VIEWER_SVG_NAME
from .json_io import read_json
from .svg_styles import render_svg_style_blocks


# Soglie visuali generali: non cambiano la simulazione, ma distinguono zero,
# leakage e corrente continua misurata in modo leggibile.
MIN_NUMERICAL_CURRENT_A = 1e-15
LEAKAGE_CURRENT_MAX_A = 1e-11
# La corrente del ramo puo' restare visibile anche a livelli molto piccoli, ma
# un LED emette luce apprezzabile soltanto oltre una soglia dedicata.
LED_VISIBLE_CURRENT_A = 1e-4


def format_number(value: Any) -> str:
    """Formatta un valore numerico senza aggiungere precisione inutile."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "0"
    return f"{number:.2f}".rstrip("0").rstrip(".")


def model_components(model: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Indicizza insieme componenti SPICE e componenti strutturali."""
    indexed: dict[str, dict[str, Any]] = {}
    for collection in (model.get("netlist_components") or [], model.get("structural_components") or []):
        for component in collection:
            if isinstance(component, dict) and component.get("id"):
                indexed[str(component["id"])] = component
    return indexed


def node_voltages(model: dict[str, Any]) -> dict[str, float | None]:
    """Indicizza le tensioni operative per nodo."""
    voltages: dict[str, float | None] = {}
    for node in model.get("nodes") or []:
        if isinstance(node, dict) and node.get("id") is not None:
            voltages[str(node["id"])] = node.get("voltage_op")
    return voltages


def node_is_active(node_id: str, voltages: dict[str, float | None]) -> bool:
    """Indica se il nodo ha una tensione significativa rispetto alla massa."""
    try:
        return abs(float(voltages.get(node_id))) >= 0.05
    except (TypeError, ValueError):
        return False


def measured_component_current(component_id: str, measurements: dict[str, Any]) -> float | None:
    """Cerca la corrente misurata di un componente usando gli id ngspice."""
    device_currents = measurements.get("device_currents") or {}
    branch_currents = measurements.get("branch_currents") or {}
    for key in (component_id.upper(), f"{component_id.upper()}#BRANCH"):
        value = device_currents.get(key, branch_currents.get(key))
        if value is not None:
            try:
                return float(value)
            except (TypeError, ValueError):
                return None
    # ngspice puo' troncare gli id lunghi degli elementi scenario nelle tabelle OP.
    for key, value in device_currents.items():
        normalized_key = str(key).upper()
        if len(normalized_key) >= 12 and component_id.upper().startswith(normalized_key):
            try:
                return float(value)
            except (TypeError, ValueError):
                return None
    return None


def declared_current_source_value(component: dict[str, Any]) -> float | None:
    """Legge il valore DC di una sorgente di corrente non esportata da ngspice."""
    if str(component.get("kind") or "").lower() != "current_source":
        return None
    match = re.search(r"\bDC\s+([^\s()]+)", str(component.get("value") or ""), flags=re.IGNORECASE)
    return parse_spice_scalar(match.group(1)) if match else None


def component_display_current(component: dict[str, Any], measurements: dict[str, Any]) -> float | None:
    """Preferisce la misura OP; per una sorgente ideale usa il suo valore DC noto."""
    measured = measured_component_current(str(component.get("id") or ""), measurements)
    return measured if measured is not None else declared_current_source_value(component)


def component_activity_ids(model: dict[str, Any]) -> tuple[set[str], set[str], set[str]]:
    """Classifica i rami OP in corrente continua, leakage e transitorio."""
    measurements = model.get("measurements") or {}
    components = [item for item in model.get("netlist_components") or [] if isinstance(item, dict)]
    steady_ids: set[str] = set()
    leakage_ids: set[str] = set()
    transient_ids: set[str] = set()
    active_nodes: set[str] = set()

    # Le misure dirette sono la fonte primaria; le sorgenti ideali di corrente
    # usano il loro valore DC solo quando ngspice non le riporta nel parser OP.
    for component in components:
        component_id = str(component.get("id") or "")
        current = component_display_current(component, measurements)
        if current is None or abs(current) <= MIN_NUMERICAL_CURRENT_A:
            continue
        if abs(current) < LEAKAGE_CURRENT_MAX_A:
            leakage_ids.add(component_id)
        else:
            steady_ids.add(component_id)
            active_nodes.update(str(node_id) for node_id in component.get("nodes") or [])

    # Il riepilogo TRAN permette di riconoscere anche condensatori e sorgenti AC.
    transient_activity = (model.get("transient") or {}).get("component_activity") or {}
    for component_id, activity in transient_activity.items():
        if isinstance(activity, dict) and activity.get("variable"):
            transient_ids.add(str(component_id))

    # Diodi e LED ereditano il flusso dal bipolo misurato sullo stesso ramo.
    for component in components:
        component_id = str(component.get("id") or "")
        nodes = {str(node_id) for node_id in component.get("nodes") or []}
        source_id = str(component.get("source_component_id") or "").lower()
        is_diode = component.get("kind") == "diode" or source_id.startswith("led")
        if is_diode and bool((nodes - {"0"}) & active_nodes):
            steady_ids.add(component_id)
    return steady_ids, leakage_ids, transient_ids


def electrical_class(
    kind: str,
    connection: dict[str, Any],
    steady_ids: set[str],
    leakage_ids: set[str],
    transient_ids: set[str],
    voltages: dict[str, float | None],
) -> str:
    """Sceglie la classe grafica usando corrente misurata e tensione del nodo."""
    if kind == "structural":
        return "wire guide"
    endpoints = {str((connection.get(side) or {}).get("component_id") or "") for side in ("from", "to")}
    has_steady = bool(endpoints & steady_ids)
    has_leakage = bool(endpoints & leakage_ids)
    has_transient = bool(endpoints & transient_ids)
    if has_steady and has_transient:
        return "wire mixed"
    if has_transient:
        return "wire transient"
    if has_steady:
        return "wire active"
    if has_leakage:
        return "wire leakage"
    node_id = str(connection.get("node_id") or "")
    return "wire energized" if node_is_active(node_id, voltages) else "wire idle"


def orthogonal_path(start: dict[str, Any], end: dict[str, Any]) -> str:
    """Costruisce un percorso ortogonale semplice tra due terminali."""
    x1, y1 = float(start["x"]), float(start["y"])
    x2, y2 = float(end["x"]), float(end["y"])
    start_is_connector = start.get("component_type") == "connector"
    end_is_connector = end.get("component_type") == "connector"
    if start_is_connector and not end_is_connector:
        return f"M{format_number(x1)} {format_number(y1)} H{format_number(x2)} V{format_number(y2)}"
    if end_is_connector and not start_is_connector:
        return f"M{format_number(x2)} {format_number(y2)} H{format_number(x1)} V{format_number(y1)}"
    if abs(x2 - x1) >= abs(y2 - y1):
        middle = (x1 + x2) / 2
        return f"M{format_number(x1)} {format_number(y1)} H{format_number(middle)} V{format_number(y2)} H{format_number(x2)}"
    middle = (y1 + y2) / 2
    return f"M{format_number(x1)} {format_number(y1)} V{format_number(middle)} H{format_number(x2)} V{format_number(y2)}"


def routed_path(connection: dict[str, Any], start: dict[str, Any], end: dict[str, Any]) -> str:
    """Usa il percorso calcolato dal layout, con fallback al router storico per file precedenti."""
    raw_route = connection.get("route") or []
    points = [
        (float(point.get("x") or 0), float(point.get("y") or 0))
        for point in raw_route
        if isinstance(point, dict) and "x" in point and "y" in point
    ]
    if len(points) < 2:
        return orthogonal_path(start, end)
    bridges_by_segment: dict[int, list[dict[str, Any]]] = {}
    for bridge in connection.get("wire_bridges") or []:
        if isinstance(bridge, dict):
            bridges_by_segment.setdefault(int(bridge.get("segment_index") or 0), []).append(bridge)

    commands = [f"M{format_number(points[0][0])} {format_number(points[0][1])}"]
    bridge_radius = 6.0
    for segment_index, (previous, current) in enumerate(zip(points, points[1:])):
        command = "H" if abs(previous[1] - current[1]) < 0.01 else "V"
        segment_bridges = bridges_by_segment.get(segment_index) or []
        if command == "H":
            direction = 1.0 if current[0] >= previous[0] else -1.0
            segment_bridges.sort(key=lambda item: float(item.get("x") or 0) * direction)
            for bridge in segment_bridges:
                crossing_x = float(bridge.get("x") or 0)
                lead_x = crossing_x - direction * bridge_radius
                exit_x = crossing_x + direction * bridge_radius
                commands.append(f"H{format_number(lead_x)}")
                commands.append(
                    f"Q{format_number(crossing_x)} {format_number(previous[1] - bridge_radius)} "
                    f"{format_number(exit_x)} {format_number(previous[1])}"
                )
        else:
            direction = 1.0 if current[1] >= previous[1] else -1.0
            segment_bridges.sort(key=lambda item: float(item.get("y") or 0) * direction)
            for bridge in segment_bridges:
                crossing_y = float(bridge.get("y") or 0)
                lead_y = crossing_y - direction * bridge_radius
                exit_y = crossing_y + direction * bridge_radius
                commands.append(f"V{format_number(lead_y)}")
                commands.append(
                    f"Q{format_number(previous[0] + bridge_radius)} {format_number(crossing_y)} "
                    f"{format_number(previous[0])} {format_number(exit_y)}"
                )
        coordinate = current[0] if command == "H" else current[1]
        commands.append(f"{command}{format_number(coordinate)}")
    return " ".join(commands)


def node_tooltip(model: dict[str, Any], node_id: str) -> str:
    """Compone il testo breve mostrato passando su un ramo della netlist."""
    node = next(
        (
            item
            for item in model.get("nodes") or []
            if isinstance(item, dict) and str(item.get("id") or "") == node_id
        ),
        {},
    )
    voltage = node.get("voltage_op")
    try:
        voltage_text = f"{format_number(float(voltage))} V"
    except (TypeError, ValueError):
        voltage_text = "tensione non disponibile"
    terminal_count = int(node.get("terminal_count") or 0)
    terminal_text = "terminale" if terminal_count == 1 else "terminali"
    return f"{node_id} | {voltage_text} | {terminal_count} {terminal_text}"


def active_meter_ids(model: dict[str, Any]) -> set[str]:
    """Restituisce gli strumenti che stanno leggendo una tensione significativa."""
    active: set[str] = set()
    for component in model.get("structural_components") or []:
        if not isinstance(component, dict):
            continue
        if str(component.get("measurement_kind") or "").lower() != "voltage":
            continue
        try:
            if abs(float(component.get("measurement_value"))) >= 0.05:
                active.add(str(component.get("id") or ""))
        except (TypeError, ValueError):
            continue
    return {component_id for component_id in active if component_id}


def closed_switch_ids(layout: dict[str, Any]) -> set[str]:
    """Restituisce gli switch chiusi che rendono conduttivo un collegamento strutturale."""
    return {
        str(component_id)
        for component_id, position in (layout.get("components") or {}).items()
        if isinstance(position, dict)
        and normalize_component_type(
            position.get("component_type") or position.get("visual_class_name"),
            position.get("layout_kind"),
        ) == "switch"
        and str(position.get("state") or "").lower() == "closed"
    }


def active_closed_switch_ids(
    model: dict[str, Any], layout: dict[str, Any], steady_ids: set[str]
) -> set[str]:
    """Associa la corrente della resistenza SPICE di scenario allo switch chiuso originale."""
    active_switches: set[str] = set()
    for component in model.get("netlist_components") or []:
        if not isinstance(component, dict) or str(component.get("id") or "") not in steady_ids:
            continue
        source_id = str(component.get("source_component_id") or "")
        if source_id.startswith("scenario_switch"):
            active_switches.add(source_id.removeprefix("scenario_"))
    return active_switches & closed_switch_ids(layout)


def render_connections(
    layout: dict[str, Any],
    model: dict[str, Any],
    steady_ids: set[str],
    leakage_ids: set[str],
    transient_ids: set[str],
    voltages: dict[str, float | None],
) -> str:
    """Disegna tutti i collegamenti prodotti dallo step 14."""
    paths: list[str] = []
    active_meters = active_meter_ids(model)
    closed_switches = closed_switch_ids(layout)
    active_switches = active_closed_switch_ids(model, layout, steady_ids)
    for connection in layout.get("connections") or []:
        if not isinstance(connection, dict):
            continue
        start = connection.get("from") or {}
        end = connection.get("to") or {}
        if not all(key in start and key in end for key in ("x", "y")):
            continue
        node_id = str(connection.get("node_id") or "")
        endpoint_ids = {str(start.get("component_id") or ""), str(end.get("component_id") or "")}
        meter_reads_voltage = bool(endpoint_ids & active_meters) and node_id != "0"
        closed_switch_conducts = bool(endpoint_ids & closed_switches) and node_id != "0" and node_is_active(node_id, voltages)
        active_switch_conducts = bool(endpoint_ids & active_switches) and node_id != "0"
        css_class = (
            "wire active"
            if active_switch_conducts
            else "wire energized"
            if meter_reads_voltage or closed_switch_conducts
            else electrical_class(
                str(connection.get("kind") or "electrical"),
                connection,
                steady_ids,
                leakage_ids,
                transient_ids,
                voltages,
            )
        )
        tooltip = escape(node_tooltip(model, node_id)) if node_id and node_id != "0" else "Massa"
        path = routed_path(connection, start, end)
        if css_class == "wire mixed":
            wire_svg = f'<path class="wire mixed-signal" d="{path}"/>'
        else:
            wire_svg = f'<path class="{css_class}" d="{path}"/>'
        paths.append(f'<g class="node-wire"><title>{tooltip}</title>{wire_svg}</g>')
    return "".join(paths)


def two_terminal_geometry(position: dict[str, Any]) -> tuple[float, float, float, float]:
    """Calcola centro, angolo e lunghezza utile di un simbolo a due terminali."""
    terminals = position.get("terminals") or []
    if len(terminals) >= 2:
        first, second = terminals[0], terminals[1]
        dx = float(second["x"]) - float(first["x"])
        dy = float(second["y"]) - float(first["y"])
        center_x = (float(first["x"]) + float(second["x"])) / 2
        center_y = (float(first["y"]) + float(second["y"])) / 2
        return center_x, center_y, math.degrees(math.atan2(dy, dx)), max(math.hypot(dx, dy), 38.0)
    return float(position.get("x") or 0), float(position.get("y") or 0), 0.0, 72.0


def component_value(component: dict[str, Any], position: dict[str, Any]) -> str:
    """Restituisce la label principale, preferendo il valore SPICE."""
    if str(position.get("component_type") or "").lower() == "lamp":
        return "Lamp"
    if str(position.get("component_type") or "").lower() == "connection":
        return ""
    if str(position.get("component_type") or "").lower() == "signal_source":
        return signal_source_value(component)
    parameters = component.get("parameters") or {}
    component_type = str(position.get("component_type") or "").lower()
    if component_type == "dc_supply":
        label = str(component.get("display_label") or component.get("supply_name") or "DC")
        value = parameters.get("value")
        unit = str(parameters.get("unit") or "V")
        formatted = f"{value:g} {unit}" if isinstance(value, (int, float)) else str(value or "").strip()
        return f"{label} {formatted}".strip()
    if component_type == "fuse" and component.get("display_label"):
        return str(component["display_label"])
    capacitor_types = {
        "capacitor", "polarized_capacitor", "variable_capacitor", "variable_polarized_capacitor"
    }
    if component.get("is_scenario_modified") and component_type in {"resistor", "inductor", *capacitor_types}:
        display_label = str(component.get("display_label") or "").strip()
        reference = display_label.split()[0] if display_label else ""
        raw_value = str(component.get("value") or component.get("scenario_value") or "").strip()
        numeric_value = parse_spice_scalar(raw_value)
        units = {"resistor": "Ohm", "capacitor": "F", "inductor": "H"}
        current_value = format_engineering_value(numeric_value, units[component_type]) if numeric_value is not None else raw_value
        return f"{reference} {current_value}".strip()
    if component_type in {"resistor", *capacitor_types} and component.get("display_label"):
        return str(component["display_label"])
    if component_type in {"battery", "resistor", *capacitor_types} and parameters.get("value") is not None:
        value = parameters.get("value")
        unit = str(parameters.get("unit") or "")
        return f"{value:g} {unit}" if isinstance(value, (int, float)) else f"{value} {unit}".strip()
    value = str(component.get("value") or "").strip()
    if component_type in {"voltage_source", "scenario_voltage_source"}:
        dc_match = re.search(r"\bDC\s+([^\s()]+)", value, flags=re.IGNORECASE)
        dc_value = parse_spice_scalar(dc_match.group(1)) if dc_match else None
        if dc_value is not None:
            return format_engineering_value(dc_value, "V")
    if value:
        return value.split()[0]
    label = str(position.get("label") or "").strip()
    return label if label else str(component.get("id") or "")


def meter_scale_limit(value: float) -> float:
    """Sceglie un fondoscala 1-2-5 leggibile per una misura analogica."""
    magnitude = max(abs(value), 1e-9)
    exponent = math.floor(math.log10(magnitude))
    base = magnitude / (10 ** exponent)
    step = 1.0 if base <= 1 else 2.0 if base <= 2 else 5.0
    return step * (10 ** exponent)


def meter_reading(component: dict[str, Any]) -> tuple[str, float | None]:
    """Restituisce testo e valore numerico della misura preparata dallo step 13."""
    label = str(component.get("display_label") or (component.get("parameters") or {}).get("label_text") or "METER")
    value = component.get("measurement_value")
    try:
        return label, float(value)
    except (TypeError, ValueError):
        return label, None


def render_analog_meter(component: dict[str, Any], position: dict[str, Any]) -> str:
    """Disegna un voltmetro compatto con scala, lancetta e valore operativo."""
    center_x, center_y, _, length = two_terminal_geometry(position)
    half = max(length / 2, 54.0)
    label, value = meter_reading(component)
    if value is None:
        reading = "n/a"
        needle_angle = -150.0
        active = False
    else:
        limit = meter_scale_limit(value)
        lower, upper = (-limit, limit) if value < 0 else (0.0, limit)
        ratio = min(max((value - lower) / max(upper - lower, 1e-12), 0.0), 1.0)
        needle_angle = -150.0 + ratio * 120.0
        reading = format_engineering_value(value, "V")
        if str(component.get("measurement_mode") or "").lower() == "tran_vpp":
            reading += "pp"
        active = abs(value) >= 0.05
    glow = '<rect class="meter-glow" x="-48" y="-40" width="96" height="80" rx="8"/>' if active else ""
    if active:
        needle = (
            f'<g class="meter-needle-group meter-active" style="--needle-angle:{format_number(needle_angle)}deg">'
            '<path class="meter-needle" d="M0 9 H24"/></g>'
        )
        live_indicator = '<circle class="meter-live" cx="-36" cy="-29" r="3"/>'
        reading_class = "meter-reading meter-active"
    else:
        needle = (
            f'<g transform="rotate({format_number(needle_angle)} 0 9)">'
            '<path class="meter-needle" d="M0 9 H24"/></g>'
        )
        live_indicator = ""
        reading_class = "meter-reading"
    return (
        f'<g class="component meter" transform="translate({format_number(center_x)} {format_number(center_y)})">'
        f'{glow}<g class="symbol">'
        f'<path d="M{format_number(-half)} 0 H-48 M48 0 H{format_number(half)}"/>'
        '<rect class="meter-body" x="-48" y="-40" width="96" height="80" rx="8"/>'
        '<path class="meter-scale" d="M-29 8 Q0 -23 29 8"/>'
        '<path class="meter-tick" d="M-28 8 L-23 5 M0 -23 V-17 M28 8 L23 5"/>'
        f'{needle}'
        '<circle class="meter-pivot" cx="0" cy="9" r="3"/>'
        f'{live_indicator}'
        '</g>'
        f'<text class="meter-name" x="0" y="-48">{escape(label)}</text>'
        f'<text class="{reading_class}" x="0" y="31">{escape(reading)}</text>'
        '</g>'
    )


def component_label_lines(component: dict[str, Any], position: dict[str, Any]) -> list[str]:
    """Divide riferimento e valore su due righe quando la label li contiene."""
    component_type = str(position.get("component_type") or "").lower()
    if component_type in {"diode", "zener", "led"} and component.get("display_label"):
        override_label = str(component.get("viewer_label") or "").strip()
        override_value = str(component.get("viewer_value") or "").strip()
        if override_label or override_value:
            return [line for line in (override_label, override_value) if line]
        label = str(component["display_label"]).strip()
        parts = label.split(maxsplit=1)
        return parts if len(parts) == 2 else [label]
    if component_type in {"antenna", "headset", "variable_capacitor", "variable_polarized_capacitor"}:
        label = str(component.get("viewer_label") or position.get("label") or component_type).strip()
        value = str(component.get("viewer_value") or "").strip()
        return [line for line in (label, value) if line]
    if component_type == "signal_source":
        return signal_source_label_lines(component)
    if component_type in {"voltage_source", "current_source"}:
        display_label = str(component.get("display_label") or "").strip()
        if display_label:
            manual_match = re.match(r"^(.+?)\s+assunto\s*:\s*(.+)$", display_label, flags=re.IGNORECASE)
            return [manual_match.group(1).strip(), manual_match.group(2).strip()] if manual_match else [display_label]
    if component_type == "dc_supply":
        parameters = component.get("parameters") or {}
        label = str(component.get("display_label") or component.get("supply_name") or "DC")
        value = parameters.get("value")
        unit = str(parameters.get("unit") or "V")
        formatted = f"{value:g} {unit}" if isinstance(value, (int, float)) else str(value or "").strip()
        if component.get("viewer_role") == "manual_ocr_dc_supply":
            # Il valore e' l'unica label esterna della sorgente dedotta da OCR.
            return [formatted] if formatted else []
        return [line for line in (label, formatted) if line]
    label = component_value(component, position).strip()
    if not label:
        return []
    # Le note metodologiche appartengono al YAML e agli artefatti, non alla
    # label grafica: nel viewer restano solo riferimento e valore elettrico.
    manual_match = re.match(r"^(.+?)\s+assunto\s*:\s*(.+)$", label, flags=re.IGNORECASE)
    if manual_match:
        return [manual_match.group(1).strip(), manual_match.group(2).strip()]
    if str(position.get("component_type") or "").lower() == "scenario_voltage_source":
        # Il colore del simbolo identifica gia' lo scenario: basta mostrare il valore elettrico.
        return [label]
    parts = label.split(maxsplit=1)
    if component_type in {
        "resistor", "capacitor", "polarized_capacitor",
        "variable_capacitor", "variable_polarized_capacitor", "fuse",
    } and len(parts) == 2 and re.fullmatch(r"[A-Za-z]+[0-9]*", parts[0]):
        return [parts[0], parts[1]]
    if len(parts) == 2 and re.fullmatch(r"[A-Za-z]+[0-9]+", parts[0]):
        return [parts[0], parts[1]]
    return [label]


def render_component_label(
    lines: list[str],
    x: float,
    y: float,
    anchor: str,
) -> str:
    """Renderizza una label SVG centrando una o due righe nello stesso punto."""
    if not lines:
        return ""
    line_height = 14.0
    first_y = y - line_height * (len(lines) - 1) / 2
    tspans = "".join(
        f'<tspan x="{format_number(x)}" y="{format_number(first_y + index * line_height)}">{escape(line)}</tspan>'
        for index, line in enumerate(lines)
    )
    return (
        f'<text class="component-label" style="text-anchor:{anchor}" '
        f'x="{format_number(x)}" y="{format_number(y)}">{tspans}</text>'
    )


def format_engineering_value(value: float, unit: str) -> str:
    """Formatta un valore con un prefisso ingegneristico compatto."""
    if value == 0:
        return f"0 {unit}"
    scales = ((1e9, "G"), (1e6, "M"), (1e3, "k"), (1.0, ""), (1e-3, "m"), (1e-6, "u"), (1e-9, "n"))
    absolute = abs(value)
    for scale, prefix in scales:
        if absolute >= scale or scale == 1e-9:
            scaled = value / scale
            return f"{format_number(scaled)} {prefix}{unit}"
    return f"{format_number(value)} {unit}"


def parse_spice_scalar(value: str) -> float | None:
    """Converte un numero SPICE con eventuale suffisso ingegneristico."""
    match = re.fullmatch(r"([-+0-9.eE]+)([a-zA-Z]+)?", str(value).strip())
    if not match:
        return None
    try:
        number = float(match.group(1))
    except ValueError:
        return None
    suffix = str(match.group(2) or "").lower()
    multipliers = {
        "": 1.0,
        "meg": 1e6,
        "k": 1e3,
        "m": 1e-3,
        "u": 1e-6,
        "n": 1e-9,
        "p": 1e-12,
        "f": 1e-15,
    }
    return number * multipliers[suffix] if suffix in multipliers else None


def signal_source_value(component: dict[str, Any]) -> str:
    """Crea la label principale della sorgente dalla netlist effettiva."""
    raw_value = str(component.get("value") or "")
    if re.search(r"\bPULSE\(", raw_value, flags=re.IGNORECASE):
        return "SQUARE"
    match = re.search(
        r"SIN\(\s*[^\s()]+\s+([^\s()]+)\s+([^\s()]+)",
        raw_value,
        flags=re.IGNORECASE,
    )
    if not match:
        return "SINE"
    amplitude = parse_spice_scalar(match.group(1))
    frequency = parse_spice_scalar(match.group(2))
    if amplitude is None or frequency is None:
        return "SINE"
    return f"{format_engineering_value(amplitude, 'V')} / {format_engineering_value(frequency, 'Hz')}"


def pulse_voltage_range(value: Any) -> str:
    """Estrae i livelli basso e alto di una sorgente PULSE in forma compatta."""
    match = re.search(r"PULSE\(\s*([^\s()]+)\s+([^\s()]+)", str(value or ""), flags=re.IGNORECASE)
    if not match:
        return ""
    low = parse_spice_scalar(match.group(1))
    high = parse_spice_scalar(match.group(2))
    if low is None or high is None:
        return ""
    low_text = format_engineering_value(low, "V").removesuffix(" V")
    high_text = format_engineering_value(high, "V")
    return f"{low_text}-{high_text}"


def signal_source_label_lines(component: dict[str, Any]) -> list[str]:
    """Mostra forma d'onda e livello elettrico corrente su due righe leggibili."""
    raw_value = str(component.get("value") or "")
    pulse_range = pulse_voltage_range(raw_value)
    if pulse_range:
        return ["SQUARE", pulse_range]
    value = signal_source_value(component)
    return ["SINE", value] if value and value != "SINE" else ["SINE"]


def battery_polarity_axis(position: dict[str, Any]) -> tuple[float, float]:
    """Posiziona positivo e negativo lungo l'asse definito dai terminali."""
    terminals = position.get("terminals") or []
    positive_aliases = {"positive", "pos", "+", "plus"}
    positive_index = next(
        (
            index
            for index, terminal in enumerate(terminals[:2])
            if str(terminal.get("name") or "").strip().lower() in positive_aliases
        ),
        0,
    )
    # Il primo terminale del bipolo si trova sul semiasse locale negativo.
    positive_x = -16.0 if positive_index == 0 else 16.0
    return positive_x, -positive_x


def current_source_arrow_axis(position: dict[str, Any]) -> tuple[float, float]:
    """Restituisce inizio e fine della freccia secondo l'ordine SPICE della corrente."""
    terminals = position.get("terminals") or []
    from_aliases = {"current_from", "from", "source", "in"}
    from_index = next(
        (
            index
            for index, terminal in enumerate(terminals[:2])
            if str(terminal.get("name") or "").strip().lower() in from_aliases
        ),
        0,
    )
    # Il primo terminale del bipolo e' sul semiasse locale negativo: la freccia
    # interna punta quindi dal terminale `current_from` a `current_to`.
    direction = 1.0 if from_index == 0 else -1.0
    return -13.0 * direction, 13.0 * direction


def led_color(component: dict[str, Any]) -> str:
    """Ricava il colore dichiarato del LED da modello e label disponibili."""
    searchable = " ".join(
        str(value or "")
        for value in (
            component.get("model"),
            component.get("display_label"),
            (component.get("parameters") or {}).get("model"),
            (component.get("parameters") or {}).get("label_text"),
        )
    ).lower()
    color_tokens = {
        "green": ("green", "verde"),
        "yellow": ("yellow", "giallo"),
        "red": ("red", "rosso"),
    }
    for color, tokens in color_tokens.items():
        if any(re.search(rf"(?:^|[^a-z]){token}(?:[^a-z]|$)", searchable) for token in tokens):
            return color
    return "red"


def led_is_luminous(
    component_id: str,
    component: dict[str, Any],
    measurements: dict[str, Any],
    fallback_active: bool,
) -> bool:
    """Separa la luce del LED dalla semplice presenza di corrente nel ramo."""
    current = measured_component_current(component_id, measurements)
    if current is not None:
        return abs(current) >= LED_VISIBLE_CURRENT_A
    # Il fallback conserva il comportamento per output ngspice privi della
    # tabella delle correnti dei diodi.
    return fallback_active


def render_led_glow(profile: dict[str, Any] | None, active: bool, color: str) -> str:
    """Disegna un alone LED statico o sincronizzato con il profilo TRAN."""
    color_class = f" led-color-{color}"
    if profile:
        state = str(profile.get("state") or "off")
        if state == "off":
            return ""
        if state == "steady_on":
            tooltip = "LED acceso in modo continuo secondo il transitorio SPICE"
            return (
                f'<ellipse class="led-glow led-steady{color_class}" cx="0" cy="0" rx="42" ry="30">'
                f'<title>{escape(tooltip)}</title></ellipse>'
            )

        duration = max(0.8, float(profile.get("playback_duration_s") or 1.25))
        duty_cycle = min(0.8, max(0.12, float(profile.get("display_duty_cycle") or 0.12)))
        fade_end = min(0.98, duty_cycle + 0.02)
        frequency = profile.get("frequency_hz")
        actual_duty = float(profile.get("duty_cycle") or 0.0) * 100.0
        if frequency is not None:
            tooltip = (
                f"LED: lampeggio misurato dal transitorio, {format_number(frequency)} Hz, "
                f"duty cycle {format_number(actual_duty)}%. Riproduzione rallentata."
            )
        else:
            pulse_count = int(profile.get("pulse_count") or 1)
            pulse_label = (
                "un impulso irregolare misurato"
                if pulse_count == 1
                else f"{pulse_count} impulsi irregolari misurati"
            )
            tooltip = (
                f"LED: {pulse_label} dal transitorio, acceso per il "
                f"{format_number(actual_duty)}% della finestra. Riproduzione rallentata."
            )
        return (
            f'<ellipse class="led-glow led-transient-profile{color_class}" cx="0" cy="0" rx="42" ry="30" opacity="0.08">'
            f'<title>{escape(tooltip)}</title>'
            '<animate attributeName="opacity" values="0.08;0.48;0.48;0.08;0.08" '
            f'keyTimes="0;0.02;{format_number(duty_cycle)};{format_number(fade_end)};1" '
            f'dur="{format_number(duration)}s" repeatCount="indefinite"/>'
            '</ellipse>'
        )

    if not active:
        return ""
    return (
        f'<ellipse class="led-glow led-steady{color_class}" cx="0" cy="0" rx="42" ry="30">'
        '<title>LED attivo; profilo transitorio non disponibile</title></ellipse>'
    )


def semantic_terminal_local_sign(
    position: dict[str, Any],
    terminal_name: str,
    default: float = 1.0,
) -> float:
    """Indica se un terminale semantico occupa il lato locale sinistro o destro.

    Il renderer ruota poi l'intero bipolo: `-1` rappresenta il primo estremo
    locale e `+1` il secondo. In questo modo anodo e catodo restano corretti
    tanto nei simboli orizzontali quanto in quelli verticali.
    """
    wanted = terminal_name.strip().lower()
    for index, terminal in enumerate((position.get("terminals") or [])[:2]):
        if str(terminal.get("name") or "").strip().lower() == wanted:
            return -1.0 if index == 0 else 1.0
    return default


def render_two_terminal_symbol(
    component_id: str,
    component: dict[str, Any],
    position: dict[str, Any],
    steady_ids: set[str],
    leakage_ids: set[str],
    transient_ids: set[str],
    led_profiles: dict[str, dict[str, Any]],
    measurements: dict[str, Any],
) -> str:
    """Disegna un componente a due terminali usando il vocabolario SVG comune."""
    center_x, center_y, angle, length = two_terminal_geometry(position)
    half = max(24.0, min(length / 2, 62.0))
    visual_class = str(position.get("component_type") or position.get("visual_class_name") or position.get("layout_kind") or "").lower()
    active = component_id in steady_ids or component_id in transient_ids
    leakage = component_id in leakage_ids
    transient = component_id in transient_ids
    stroke_class = "symbol"
    label_lines = component_label_lines(component, position)
    flow_path = ""

    if "switch" in visual_class:
        state = str(position.get("state") or (component.get("parameters") or {}).get("state") or "open").lower()
        blade = f'M{-half + 8} 0 H{half - 8}' if state == "closed" else f'M{-half + 8} 0 L{half - 8} -20'
        body = f'<circle cx="{-half}" cy="0" r="4"/><circle cx="{half}" cy="0" r="4"/><path d="{blade}"/>'
        flow_path = blade if state == "closed" else ""
    elif visual_class == "connection":
        flow_path = f'M{-half} 0 H{half}'
        body = "" if active else f'<path class="scenario-link-idle" d="{flow_path}"/>'
    elif visual_class == "resistor":
        flow_path = f'M{-half} 0 H-36 L-30 -14 L-18 14 L-6 -14 L6 14 L18 -14 L30 14 L36 0 H{half}'
        body = f'<path d="{flow_path}"/>'
    elif visual_class in {"polarized_capacitor", "variable_polarized_capacitor"}:
        # La piastra diritta e il segno + seguono sempre il terminale positive
        # del Graph JSON; la piastra opposta e curva e porta il segno -.
        positive_x, negative_x = battery_polarity_axis(position)
        positive_plate_x = -8.0 if positive_x < 0 else 8.0
        negative_plate_x = -positive_plate_x
        # La curva deve rivolgersi verso la piastra diritta: `|(` quando e' a
        # destra e `)|` quando e' a sinistra, senza alterare la polarita.
        curve_x = negative_plate_x - (12.0 if negative_plate_x > 0 else -12.0)
        flow_path = f'M{-half} 0 H-8 M8 0 H{half}'
        tuning_arrow = (
            '<path d="M-23 25 L23 -25 M14 -25 H23 V-16"/>'
            if visual_class == "variable_polarized_capacitor"
            else ""
        )
        body = (
            f'<path d="M{-half} 0 H-8 '
            f'M{format_number(negative_plate_x)} -20 Q{format_number(curve_x)} 0 {format_number(negative_plate_x)} 20 '
            f'M{format_number(positive_plate_x)} -20 V20 '
            f'M8 0 H{half}"/>'
            f'<text class="battery-polarity positive" x="{format_number(positive_x)}" y="5" '
            f'transform="rotate({format_number(-angle)} {format_number(positive_x)} 0)">+</text>'
            f'<text class="battery-polarity" x="{format_number(negative_x)}" y="5" '
            f'transform="rotate({format_number(-angle)} {format_number(negative_x)} 0)">-</text>'
            f'{tuning_arrow}'
        )
    elif visual_class == "variable_capacitor":
        # Condensatore regolabile: piastre dritte, nessuna polarita e freccia
        # diagonale secondo il simbolo circuitale standard.
        flow_path = f'M{-half} 0 H-8 M8 0 H{half}'
        body = (
            f'<path d="M{-half} 0 H-8 M-8 -20 V20 M8 -20 V20 M8 0 H{half} '
            'M-23 25 L23 -25 M14 -25 H23 V-16"/>'
        )
    elif "capacitor" in visual_class:
        flow_path = f'M{-half} 0 H-8 M-8 -20 V20 M8 -20 V20 M8 0 H{half}'
        body = f'<path d="{flow_path}"/>'
    elif "inductor" in visual_class:
        # Tre gobbe identiche rendono il simbolo stabile anche quando il
        # layout lo ruota per rappresentare un induttore verticale.
        body = (
            f'<path d="M{-half} 0 H-30 '
            'C-30 -20 -10 -20 -10 0 '
            'C-10 -20 10 -20 10 0 '
            'C10 -20 30 -20 30 0 '
            f'H{half}"/>'
        )
    elif "led" in visual_class or "diode" in visual_class or "zener" in visual_class:
        color = led_color(component) if "led" in visual_class else ""
        luminous = led_is_luminous(component_id, component, measurements, active) if "led" in visual_class else False
        glow = render_led_glow(led_profiles.get(component_id), luminous, color) if "led" in visual_class else ""
        cathode_sign = semantic_terminal_local_sign(position, "cathode")
        cathode_x = 18.0 * cathode_sign
        anode_x = -cathode_x
        ray_sign = cathode_sign
        rays = (
            f'<path class="led-rays" d="M{format_number(5.0 * ray_sign)} -20 '
            f'L{format_number(17.0 * ray_sign)} -34 '
            f'M{format_number(20.0 * ray_sign)} -16 '
            f'L{format_number(32.0 * ray_sign)} -30"/>'
            if "led" in visual_class
            else ""
        )
        cathode = (
            f'M{format_number(10.0 * cathode_sign)} -20 '
            f'L{format_number(cathode_x)} -14 V14 '
            f'L{format_number(26.0 * cathode_sign)} 20'
            if "zener" in visual_class
            else f'M{format_number(cathode_x)} -20 V20'
        )
        diode_body = (
            f'M{format_number(anode_x)} -18 '
            f'L{format_number(cathode_x)} 0 '
            f'L{format_number(anode_x)} 18 Z'
        )
        body = (
            f'{glow}<path d="M{-half} 0 H-18 {diode_body} '
            f'{cathode} M18 0 H{half}"/>{rays}'
        )
        flow_path = f'M{-half} 0 H{half}'
    elif "lamp" in visual_class:
        glow = '<ellipse class="lamp-glow" cx="0" cy="0" rx="46" ry="38"/>' if active else ""
        body = f'{glow}<path d="M{-half} 0 H-24 M24 0 H{half}"/><circle cx="0" cy="0" r="24"/><path d="M-14 -14 L14 14 M14 -14 L-14 14"/>'
        flow_path = f'M{-half} 0 H-24 M-14 -14 L14 14 M14 -14 L-14 14 M24 0 H{half}'
    elif "signal_source" in visual_class:
        body = (
            f'<path d="M{-half} 0 H-25 M25 0 H{half}"/>'
            '<circle cx="0" cy="0" r="25"/>'
            '<path class="source-wave" d="M-16 0 C-11 -12 -5 -12 0 0 C5 12 11 12 16 0"/>'
        )
        flow_path = f'M{-half} 0 H-25 M-16 0 C-11 -12 -5 -12 0 0 C5 12 11 12 16 0 M25 0 H{half}'
    elif visual_class in {"dc_supply", "voltage_source"}:
        positive_x, negative_x = battery_polarity_axis(position)
        body = (
            f'<path d="M{-half} 0 H-25 M25 0 H{half}"/>'
            '<circle cx="0" cy="0" r="25"/>'
            f'<text class="battery-polarity positive" x="{format_number(positive_x)}" y="5" '
            f'transform="rotate({format_number(-angle)} {format_number(positive_x)} 0)">+</text>'
            f'<text class="battery-polarity" x="{format_number(negative_x)}" y="5" '
            f'transform="rotate({format_number(-angle)} {format_number(negative_x)} 0)">-</text>'
        )
        flow_path = f'M{-half} 0 H-25' if active else ""
    elif visual_class == "current_source":
        arrow_start, arrow_end = current_source_arrow_axis(position)
        arrow_head_x = arrow_end - (8.0 if arrow_end > 0 else -8.0)
        body = (
            f'<path d="M{-half} 0 H-25 M25 0 H{half}"/>'
            '<circle cx="0" cy="0" r="25"/>'
            f'<path d="M{format_number(arrow_start)} 0 H{format_number(arrow_end)} '
            f'M{format_number(arrow_head_x)} -8 L{format_number(arrow_end)} 0 '
            f'L{format_number(arrow_head_x)} 8"/>'
        )
        flow_path = f'M{-half} 0 H-25 M25 0 H{half}' if active else ""
    elif visual_class in {"battery", "scenario_voltage_source"}:
        is_scenario_source = visual_class == "scenario_voltage_source"
        positive_x, negative_x = battery_polarity_axis(position)
        glow_class = "scenario-source-glow" if is_scenario_source else "battery-glow"
        glow = f'<rect class="{glow_class}" x="-38" y="-30" width="76" height="60" rx="8"/>' if active or is_scenario_source else ""
        body_class = "scenario-battery-body" if is_scenario_source else "battery-body"
        body = (
            f'{glow}<path d="M{-half} 0 H-32 M32 0 H{half}"/>'
            f'<rect class="{body_class}" x="-32" y="-24" width="64" height="48" rx="4"/>'
            f'<text class="battery-polarity positive" x="{format_number(positive_x)}" y="5" '
            f'transform="rotate({format_number(-angle)} {format_number(positive_x)} 0)">+</text>'
            f'<text class="battery-polarity" x="{format_number(negative_x)}" y="5" '
            f'transform="rotate({format_number(-angle)} {format_number(negative_x)} 0)">-</text>'
        )
        flow_path = f'M{-half} 0 H{-32}' if active else ""
    elif "fuse" in visual_class:
        body = f'<path d="M{-half} 0 H-24 M24 0 H{half}"/><rect x="-24" y="-10" width="48" height="20" rx="3"/>'
    else:
        body = f'<path d="M{-half} 0 H-24 M24 0 H{half}"/><rect x="-24" y="-18" width="48" height="36" rx="4"/><path d="M-14 0 C-8 -12 8 12 14 0"/>'

    is_vertical = 45 <= abs(angle) <= 135
    if is_vertical:
        label_side = str(position.get("label_side") or "right")
        if label_side in {"top", "bottom"}:
            label_height = max(len(label_lines), 1) * 14.0
            direction = -1.0 if label_side == "top" else 1.0
            label_x = center_x + float(position.get("label_offset_x") or 0)
            label_y = center_y + direction * (length / 2 + label_height / 2 + 8.0)
            label_anchor = "middle"
        else:
            label_x = center_x - 34 if label_side == "left" else center_x + 34
            label_y = center_y + 4 + float(position.get("label_offset_y") or 0)
            label_anchor = "end" if label_side == "left" else "start"
    else:
        label_side = str(position.get("label_side") or "top")
        label_height = max(len(label_lines), 1) * 14.0
        direction = 1.0 if label_side == "bottom" else -1.0
        symbol_height = float((position.get("symbol_size") or {}).get("height") or 46.0)
        label_x = center_x + float(position.get("label_offset_x") or 0)
        label_y = center_y + direction * (symbol_height / 2 + label_height / 2 + 8.0)
        label_anchor = "middle"
    label_svg = render_component_label(label_lines, label_x, label_y, label_anchor)
    mixed = component_id in steady_ids and component_id in transient_ids
    if (active or leakage) and flow_path:
        if mixed:
            flow_svg = f'<path class="component-flow mixed-signal" d="{flow_path}"/>'
        elif leakage:
            flow_svg = f'<path class="component-flow leakage" d="{flow_path}"/>'
        else:
            flow_class = "component-flow transient" if transient else "component-flow"
            flow_svg = f'<path class="{flow_class}" d="{flow_path}"/>'
    else:
        flow_svg = ""
    component_css = f"component led-color-{led_color(component)}" if "led" in visual_class else "component"
    return (
        f'<g class="{component_css}" transform="translate({format_number(center_x)} {format_number(center_y)}) rotate({format_number(angle)})">'
        f'<g class="{stroke_class}">{body}</g>'
        f'{flow_svg}'
        "</g>"
        f"{label_svg}"
    )


def render_antenna(component: dict[str, Any], position: dict[str, Any]) -> str:
    """Disegna un'antenna a stelo con elemento triangolare e un solo terminale."""
    center_x = float(position.get("x") or 0)
    center_y = float(position.get("y") or 0)
    terminals = position.get("terminals") or []
    terminal_y = float(terminals[0].get("y") or center_y + 48.0) if terminals else center_y + 48.0
    label = render_component_label(component_label_lines(component, position), center_x, center_y - 58.0, "middle")
    body = (
        f'<g class="component antenna"><g class="symbol">'
        f'<path d="M{format_number(center_x)} {format_number(terminal_y)} '
        f'V{format_number(center_y - 12.0)} '
        f'M{format_number(center_x)} {format_number(center_y - 12.0)} '
        f'L{format_number(center_x - 24.0)} {format_number(center_y - 46.0)} '
        f'H{format_number(center_x + 24.0)} Z"/>'
        # Le onde laterali identificano l'interfaccia RF senza aggiungere
        # una sorgente elettrica o modificare lo stato della simulazione.
        f'<path class="radio-wave wave-1" d="M{format_number(center_x - 30.0)} {format_number(center_y - 42.0)} '
        f'Q{format_number(center_x - 43.0)} {format_number(center_y - 29.0)} '
        f'{format_number(center_x - 33.0)} {format_number(center_y - 14.0)}"/>'
        f'<path class="radio-wave wave-2" d="M{format_number(center_x - 39.0)} {format_number(center_y - 50.0)} '
        f'Q{format_number(center_x - 58.0)} {format_number(center_y - 29.0)} '
        f'{format_number(center_x - 43.0)} {format_number(center_y - 5.0)}"/>'
        f'<path class="radio-wave wave-1" d="M{format_number(center_x + 30.0)} {format_number(center_y - 42.0)} '
        f'Q{format_number(center_x + 43.0)} {format_number(center_y - 29.0)} '
        f'{format_number(center_x + 33.0)} {format_number(center_y - 14.0)}"/>'
        f'<path class="radio-wave wave-2" d="M{format_number(center_x + 39.0)} {format_number(center_y - 50.0)} '
        f'Q{format_number(center_x + 58.0)} {format_number(center_y - 29.0)} '
        f'{format_number(center_x + 43.0)} {format_number(center_y - 5.0)}"/>'
        '</g></g>'
    )
    return body + label


def render_headset(
    component_id: str,
    component: dict[str, Any],
    position: dict[str, Any],
    steady_ids: set[str],
    leakage_ids: set[str],
    transient_ids: set[str],
) -> str:
    """Disegna una cuffia con due prese, padiglioni e archetto riconoscibili."""
    terminals = position.get("terminals") or []
    if len(terminals) < 2:
        return render_two_terminal_symbol(
            component_id, component, position, steady_ids, leakage_ids, transient_ids, {}, {}
        )
    ordered = sorted(terminals, key=lambda item: float(item.get("y") or 0))
    left_x = min(float(item.get("x") or 0) for item in ordered)
    top_y, bottom_y = float(ordered[0]["y"]), float(ordered[1]["y"])
    cup_x = left_x + 34.0
    arc_right = left_x + 88.0
    label_x = (left_x + arc_right) / 2
    label = render_component_label(component_label_lines(component, position), label_x, top_y - 36.0, "middle")
    body_path = (
        f'M{format_number(left_x)} {format_number(top_y)} H{format_number(cup_x - 10.0)} '
        f'M{format_number(left_x)} {format_number(bottom_y)} H{format_number(cup_x - 10.0)} '
        f'M{format_number(cup_x + 10.0)} {format_number(top_y)} H{format_number(cup_x + 22.0)} '
        f'M{format_number(cup_x + 10.0)} {format_number(bottom_y)} H{format_number(cup_x + 22.0)} '
        f'M{format_number(cup_x + 22.0)} {format_number(top_y)} '
        f'Q{format_number(arc_right)} {format_number((top_y + bottom_y) / 2)} '
        f'{format_number(cup_x + 22.0)} {format_number(bottom_y)}'
    )
    active = component_id in steady_ids or component_id in transient_ids
    leakage = component_id in leakage_ids
    flow_class = "component-flow leakage" if leakage else "component-flow"
    flow = f'<path class="{flow_class}" d="{body_path}"/>' if active or leakage else ""
    audio_state_class = " active" if active else ""
    middle_y = (top_y + bottom_y) / 2
    audio_waves = (
        f'<path class="audio-wave wave-1{audio_state_class}" '
        f'd="M{format_number(arc_right + 7.0)} {format_number(middle_y - 10.0)} '
        f'Q{format_number(arc_right + 16.0)} {format_number(middle_y)} '
        f'{format_number(arc_right + 7.0)} {format_number(middle_y + 10.0)}"/>'
        f'<path class="audio-wave wave-2{audio_state_class}" '
        f'd="M{format_number(arc_right + 15.0)} {format_number(middle_y - 17.0)} '
        f'Q{format_number(arc_right + 30.0)} {format_number(middle_y)} '
        f'{format_number(arc_right + 15.0)} {format_number(middle_y + 17.0)}"/>'
    )
    body = (
        f'<g class="component headset"><g class="symbol"><path d="{body_path}"/>'
        f'<ellipse cx="{format_number(cup_x)}" cy="{format_number(top_y)}" rx="10" ry="15"/>'
        f'<ellipse cx="{format_number(cup_x)}" cy="{format_number(bottom_y)}" rx="10" ry="15"/>'
        f'<ellipse cx="{format_number(cup_x)}" cy="{format_number(top_y)}" rx="5" ry="9"/>'
        f'<ellipse cx="{format_number(cup_x)}" cy="{format_number(bottom_y)}" rx="5" ry="9"/>'
        f'{audio_waves}</g>{flow}</g>'
    )
    return body + label


def render_connector(component_id: str, position: dict[str, Any]) -> str:
    """Disegna un connector compatto dimensionato sul numero dei terminali."""
    terminals = position.get("terminals") or []
    if not terminals:
        return ""
    ys = [float(item["y"]) for item in terminals]
    spec = component_spec("connector", "connector", len(terminals))
    center_x = float(position.get("x") or 0)
    left, right = center_x - spec["width"] / 2, center_x + spec["width"] / 2
    top, bottom = min(ys) - 24, max(ys) + 24
    pins: list[str] = []
    for terminal in terminals:
        name = escape(str(terminal.get("name") or ""))
        pin_number = escape(str(terminal.get("pin_number") or name))
        pins.append(
            f'<circle cx="{format_number(terminal["x"])}" cy="{format_number(terminal["y"])}" r="7"/>'
            f'<text class="pin-label" x="{format_number(left-14)}" y="{format_number(float(terminal["y"])+4)}">{pin_number}</text>'
            f'<title>{name}</title>'
        )
    label = "J"
    return f'<g class="connector"><rect x="{format_number(left)}" y="{format_number(top)}" width="{format_number(right-left)}" height="{format_number(bottom-top)}" rx="4"/>{"".join(pins)}<text class="component-label" x="{format_number((left+right)/2)}" y="{format_number(top-10)}">{label}</text></g>'


def render_ground(position: dict[str, Any]) -> str:
    """Disegna una massa centrata sul proprio terminale."""
    terminal = (position.get("terminals") or [{}])[0]
    x = float(terminal.get("x", position.get("x") or 0))
    y = float(terminal.get("y", position.get("y") or 0))
    return f'<g class="symbol ground" transform="translate({format_number(x)} {format_number(y)})"><path d="M0 0 V12 M-22 12 H22 M-14 21 H14 M-6 30 H6"/></g>'


def render_terminal_port(component: dict[str, Any], position: dict[str, Any]) -> str:
    """Disegna un terminale esterno pulito, orientato secondo la bbox."""
    terminal = (position.get("terminals") or [{}])[0]
    x = float(terminal.get("x", position.get("x") or 0))
    y = float(terminal.get("y", position.get("y") or 0))
    side = str(terminal.get("relative_position") or "right").lower()
    outward = {
        "bottom": (0.0, -1.0),
        "top": (0.0, 1.0),
        "left": (1.0, 0.0),
        "right": (-1.0, 0.0),
    }.get(side, (1.0, 0.0))
    label = escape(str(component.get("display_label") or position.get("label") or ""))
    value = escape(str(component.get("display_value") or ""))

    if outward[1] < 0:
        text_x, text_y, anchor = x, y - 34.0, "middle"
    elif outward[1] > 0:
        text_x, text_y, anchor = x, y + 20.0, "middle"
    elif outward[0] > 0:
        text_x, text_y, anchor = x + 14.0, y - (4.0 if value else -4.0), "start"
    else:
        text_x, text_y, anchor = x - 14.0, y - (4.0 if value else -4.0), "end"

    value_line = f'<tspan x="{format_number(text_x)}" dy="15">{value}</tspan>' if value else ""
    return (
        '<g class="symbol terminal-port">'
        f'<circle cx="{format_number(x)}" cy="{format_number(y)}" r="5"/>'
        f'<text class="terminal-label" text-anchor="{anchor}" x="{format_number(text_x)}" '
        f'y="{format_number(text_y)}"><tspan x="{format_number(text_x)}">{label}</tspan>{value_line}</text>'
        '</g>'
    )


def terminal_by_name(position: dict[str, Any], name: str) -> dict[str, Any] | None:
    """Trova un terminale posizionato usando il suo nome semantico."""
    wanted = name.upper()
    for terminal in position.get("terminals") or []:
        if str(terminal.get("name") or "").upper() == wanted:
            return terminal
    return None


def transistor_reference_label(component: dict[str, Any]) -> str:
    """Restituisce solo il riferimento del BJT, senza mostrare il modello."""
    display_label = str(component.get("display_label") or "").strip()
    first_token = display_label.split()[0] if display_label else ""
    return first_token if first_token.upper().startswith("Q") else "Q"


def render_bjt_transistor(
    component_id: str,
    component: dict[str, Any],
    position: dict[str, Any],
    steady_ids: set[str],
    transient_ids: set[str],
    transistor_kind: str = "npn",
) -> str:
    """Disegna un BJT NPN o PNP usando i terminali semantici B, C ed E."""
    base = terminal_by_name(position, "B")
    collector = terminal_by_name(position, "C")
    emitter = terminal_by_name(position, "E")
    if not base or not collector or not emitter:
        return render_multi_terminal(component_id, position)

    center_x = float(position.get("x") or 0)
    center_y = float(position.get("y") or 0)
    # La base puo' trovarsi a sinistra oppure a destra del simbolo. La barra
    # interna segue quel lato, mentre collettore ed emettitore partono verso
    # il lato opposto senza incrociarsi.
    base_side = 1.0 if float(base["x"]) >= center_x else -1.0
    base_x = center_x + base_side * 6.0
    base_top = center_y - 18.0
    base_bottom = center_y + 18.0
    collector_x = float(collector["x"])
    collector_y = float(collector["y"])
    emitter_x = float(emitter["x"])
    emitter_y = float(emitter["y"])
    emitter_is_upper = emitter_y < collector_y
    emitter_start_y = base_top if emitter_is_upper else base_bottom
    collector_start_y = base_bottom if emitter_is_upper else base_top

    # Per l'NPN la freccia punta verso l'esterno; per il PNP punta verso la base.
    direction_x = emitter_x - base_x
    direction_y = emitter_y - emitter_start_y
    length = max(math.hypot(direction_x, direction_y), 1.0)
    unit_x, unit_y = direction_x / length, direction_y / length
    arrow_fraction = 0.28 if transistor_kind == "pnp" else 0.72
    arrow_direction = -1.0 if transistor_kind == "pnp" else 1.0
    tip_x = base_x + direction_x * arrow_fraction
    tip_y = emitter_start_y + direction_y * arrow_fraction
    back_x = tip_x - unit_x * 11.0 * arrow_direction
    back_y = tip_y - unit_y * 11.0 * arrow_direction
    normal_x, normal_y = -unit_y * 5.0, unit_x * 5.0

    body_path = (
        f'M{format_number(base["x"])} {format_number(base["y"])} H{format_number(base_x)} '
        f'M{format_number(base_x)} {format_number(base_top)} V{format_number(base_bottom)} '
        f'M{format_number(base_x)} {format_number(collector_start_y)} '
        f'L{format_number(collector_x)} {format_number(collector_y)} '
        f'M{format_number(base_x)} {format_number(emitter_start_y)} '
        f'L{format_number(emitter_x)} {format_number(emitter_y)}'
    )
    arrow_path = (
        f'M{format_number(back_x + normal_x)} {format_number(back_y + normal_y)} '
        f'L{format_number(tip_x)} {format_number(tip_y)} '
        f'L{format_number(back_x - normal_x)} {format_number(back_y - normal_y)}'
    )
    active = component_id in steady_ids or component_id in transient_ids
    mixed = component_id in steady_ids and component_id in transient_ids
    if active:
        if mixed:
            flow = f'<path class="transistor-flow mixed-signal" d="{body_path}"/>'
        else:
            flow_class = "transistor-flow transient" if component_id in transient_ids else "transistor-flow"
            flow = f'<path class="{flow_class}" d="{body_path}"/>'
    else:
        flow = ""
    label = escape(transistor_reference_label(component))
    return (
        '<g class="symbol transistor">'
        f'<circle cx="{format_number(center_x)}" cy="{format_number(center_y)}" r="31"/>'
        f'<path d="{body_path}"/><path d="{arrow_path}"/>{flow}'
        f'<text class="component-label" x="{format_number(center_x)}" y="{format_number(center_y-40)}">{label}</text>'
        '</g>'
    )


def render_multi_terminal(component_id: str, position: dict[str, Any]) -> str:
    """Disegna un simbolo generico leggibile per componenti con tre o più terminali."""
    x = float(position.get("x") or 0)
    y = float(position.get("y") or 0)
    terminals = position.get("terminals") or []
    leads = "".join(
        f'<path d="M{format_number(x)} {format_number(y)} L{format_number(item["x"])} {format_number(item["y"])}"/>'
        for item in terminals
    )
    label = escape(component_id.split(".")[0])
    return f'<g class="symbol multi">{leads}<circle cx="{format_number(x)}" cy="{format_number(y)}" r="25"/><text class="component-label" x="{format_number(x)}" y="{format_number(y-34)}">{label}</text></g>'


def rectangles_overlap(first: tuple[float, float, float, float], second: tuple[float, float, float, float]) -> float:
    """Restituisce l'area di sovrapposizione tra due rettangoli."""
    width = max(0.0, min(first[2], second[2]) - max(first[0], second[0]))
    height = max(0.0, min(first[3], second[3]) - max(first[1], second[1]))
    return width * height


def component_obstacle(position: dict[str, Any]) -> tuple[float, float, float, float]:
    """Stima l'ingombro visuale di un simbolo posizionato nel layout."""
    x = float(position.get("x") or 0)
    y = float(position.get("y") or 0)
    size = position.get("symbol_size") or {}
    width = float(size.get("width") or 50)
    height = float(size.get("height") or 40)
    if position.get("orientation") == "vertical":
        width, height = height, width
    return (x - width / 2 - 6, y - height / 2 - 6, x + width / 2 + 6, y + height / 2 + 6)


def connection_obstacles(layout: dict[str, Any]) -> list[tuple[float, float, float, float]]:
    """Converte i tratti ortogonali dei fili in piccoli ostacoli rettangolari."""
    obstacles: list[tuple[float, float, float, float]] = []
    for connection in layout.get("connections") or []:
        if not isinstance(connection, dict):
            continue
        start = connection.get("from") or {}
        end = connection.get("to") or {}
        if not all(axis in start and axis in end for axis in ("x", "y")):
            continue
        x1, y1 = float(start["x"]), float(start["y"])
        x2, y2 = float(end["x"]), float(end["y"])
        if start.get("component_type") == "connector" and end.get("component_type") != "connector":
            points = [(x1, y1), (x2, y1), (x2, y2)]
        elif end.get("component_type") == "connector" and start.get("component_type") != "connector":
            points = [(x2, y2), (x1, y2), (x1, y1)]
        elif abs(x2 - x1) >= abs(y2 - y1):
            middle = (x1 + x2) / 2
            points = [(x1, y1), (middle, y1), (middle, y2), (x2, y2)]
        else:
            middle = (y1 + y2) / 2
            points = [(x1, y1), (x1, middle), (x2, middle), (x2, y2)]
        for first, second in zip(points, points[1:]):
            obstacles.append(
                (
                    min(first[0], second[0]) - 3,
                    min(first[1], second[1]) - 3,
                    max(first[0], second[0]) + 3,
                    max(first[1], second[1]) + 3,
                )
            )
    return obstacles


def vertical_label_placements(
    layout: dict[str, Any],
    indexed: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Posiziona le label verticali minimizzando collisioni con simboli e testi."""
    components = {
        str(component_id): position
        for component_id, position in (layout.get("components") or {}).items()
        if isinstance(position, dict)
    }
    obstacles = {component_id: component_obstacle(position) for component_id, position in components.items()}
    wire_obstacles = connection_obstacles(layout)
    placed_labels: list[tuple[float, float, float, float]] = []
    fixed_label_obstacles: list[tuple[float, float, float, float]] = []
    placements: dict[str, dict[str, Any]] = {}

    # Le sorgenti verticali hanno una label laterale fissa: riservarne lo spazio
    # evita che il valore di una resistenza vicina finisca sopra SINE/SQUARE.
    for component_id, position in components.items():
        if str(position.get("component_type") or "").lower() != "signal_source":
            continue
        if position.get("orientation") != "vertical":
            continue
        lines = component_label_lines(indexed.get(component_id) or {}, position)
        if not lines:
            continue
        text_width = max(len(line) for line in lines) * 7.2 + 4.0
        text_height = max(len(lines), 1) * 14.0 + 4.0
        label_x = float(position.get("x") or 0) + 34.0
        label_y = float(position.get("y") or 0) + 4.0
        fixed_label_obstacles.append(
            (label_x, label_y - text_height / 2, label_x + text_width, label_y + text_height / 2)
        )

    for component_id, position in components.items():
        if position.get("orientation") != "vertical":
            continue
        component_type = str(position.get("component_type") or "").lower()
        if component_type not in {
            "resistor", "capacitor", "polarized_capacitor", "variable_capacitor",
            "variable_polarized_capacitor", "inductor", "diode", "lamp", "fuse",
        }:
            continue
        lines = component_label_lines(indexed.get(component_id) or {}, position)
        if not lines:
            continue
        text_width = max(len(line) for line in lines) * 7.2 + 4.0
        text_height = max(len(lines), 1) * 14.0 + 4.0
        center_x = float(position.get("x") or 0)
        center_y = float(position.get("y") or 0) + 4.0
        candidates: list[tuple[float, str, float, float, tuple[float, float, float, float]]] = []

        for side in ("left", "right"):
            label_x = center_x - 34.0 if side == "left" else center_x + 34.0
            for offset_y in (0.0, -20.0, 20.0, -38.0, 38.0):
                label_y = center_y + offset_y
                if side == "left":
                    box = (label_x - text_width, label_y - text_height / 2, label_x, label_y + text_height / 2)
                else:
                    box = (label_x, label_y - text_height / 2, label_x + text_width, label_y + text_height / 2)
                symbol_overlap = sum(
                    rectangles_overlap(box, obstacle)
                    for other_id, obstacle in obstacles.items()
                    if other_id != component_id
                )
                label_overlap = sum(rectangles_overlap(box, other) for other in placed_labels)
                fixed_label_overlap = sum(rectangles_overlap(box, other) for other in fixed_label_obstacles)
                wire_overlap = sum(rectangles_overlap(box, wire) for wire in wire_obstacles)
                score = symbol_overlap * 80.0 + label_overlap * 30.0 + fixed_label_overlap * 100.0 + wire_overlap * 12.0 + abs(offset_y) * 2.0
                candidates.append((score, side, 0.0, offset_y, box))

        vertical_half = float((position.get("symbol_size") or {}).get("width") or 72) / 2
        for side, direction in (("top", -1.0), ("bottom", 1.0)):
            label_y = center_y + direction * (vertical_half + text_height / 2 + 8.0)
            for offset_x in (-38.0, 38.0):
                label_x = center_x + offset_x
                box = (
                    label_x - text_width / 2,
                    label_y - text_height / 2,
                    label_x + text_width / 2,
                    label_y + text_height / 2,
                )
                symbol_overlap = sum(
                    rectangles_overlap(box, obstacle)
                    for other_id, obstacle in obstacles.items()
                    if other_id != component_id
                )
                label_overlap = sum(rectangles_overlap(box, other) for other in placed_labels)
                fixed_label_overlap = sum(rectangles_overlap(box, other) for other in fixed_label_obstacles)
                wire_overlap = sum(rectangles_overlap(box, wire) for wire in wire_obstacles)
                score = symbol_overlap * 80.0 + label_overlap * 30.0 + fixed_label_overlap * 100.0 + wire_overlap * 12.0 + 90.0
                candidates.append((score, side, offset_x, 0.0, box))

        # A parita' di spazio libero le label verticali stanno a destra, lontane dai pin numerati.
        _, side, offset_x, offset_y, selected_box = min(
            candidates,
            key=lambda candidate: (candidate[0], 0 if candidate[1] == "right" else 1),
        )
        placements[component_id] = {"side": side, "offset_x": offset_x, "offset_y": offset_y}
        placed_labels.append(selected_box)

    # Per i bipoli orizzontali si sceglie sopra o sotto valutando ingombri di
    # simboli, fili e label gia' assegnate. Cosi la lettura non dipende da un
    # circuito o da coordinate fissate a mano.
    horizontal_types = {
        "resistor", "capacitor", "polarized_capacitor", "variable_capacitor",
        "variable_polarized_capacitor", "inductor", "diode", "lamp", "fuse",
        "switch", "voltage_source", "current_source", "signal_source",
    }
    for component_id, position in components.items():
        if position.get("orientation") == "vertical":
            continue
        component_type = str(position.get("component_type") or "").lower()
        if component_type not in horizontal_types:
            continue
        lines = component_label_lines(indexed.get(component_id) or {}, position)
        if not lines:
            continue
        text_width = max(len(line) for line in lines) * 7.2 + 4.0
        text_height = max(len(lines), 1) * 14.0 + 4.0
        center_x = float(position.get("x") or 0)
        center_y = float(position.get("y") or 0)
        symbol_height = float((position.get("symbol_size") or {}).get("height") or 46.0)
        candidates: list[tuple[float, str, float, tuple[float, float, float, float]]] = []
        for side, direction in (("top", -1.0), ("bottom", 1.0)):
            label_y = center_y + direction * (symbol_height / 2 + text_height / 2 + 8.0)
            for offset_x in (0.0, -38.0, 38.0, -76.0, 76.0):
                label_x = center_x + offset_x
                box = (
                    label_x - text_width / 2,
                    label_y - text_height / 2,
                    label_x + text_width / 2,
                    label_y + text_height / 2,
                )
                symbol_overlap = sum(
                    rectangles_overlap(box, obstacle)
                    for other_id, obstacle in obstacles.items()
                    if other_id != component_id
                )
                label_overlap = sum(rectangles_overlap(box, other) for other in placed_labels)
                fixed_label_overlap = sum(rectangles_overlap(box, other) for other in fixed_label_obstacles)
                wire_overlap = sum(rectangles_overlap(box, wire) for wire in wire_obstacles)
                score = symbol_overlap * 80.0 + label_overlap * 30.0 + fixed_label_overlap * 100.0 + wire_overlap * 12.0
                candidates.append((score, side, offset_x, box))
        _, side, offset_x, selected_box = min(
            candidates,
            key=lambda candidate: (candidate[0], 0 if candidate[1] == "top" else 1, abs(candidate[2])),
        )
        placements[component_id] = {"side": side, "offset_x": offset_x, "offset_y": 0.0}
        placed_labels.append(selected_box)
    return placements


def scenario_component_tooltip(component: dict[str, Any], position: dict[str, Any]) -> str:
    """Descrive in modo specifico l'origine o la modifica del componente scenario."""
    if component.get("is_scenario_added"):
        kind = str(component.get("kind") or position.get("component_type") or "componente").lower()
        names = {"resistor": "Resistenza", "voltage_source": "Sorgente di tensione"}
        subject = names.get(kind, "Componente")
        value = str(component.get("value") or "").strip()
        nodes = [str(node_id) for node_id in component.get("nodes") or []]
        node_text = f" tra {nodes[0]} e {nodes[1]}" if len(nodes) >= 2 else ""
        value_text = f" da {value}" if value else ""
        return f"{subject}{value_text} aggiunta dallo scenario{node_text}"
    previous = str(component.get("scenario_previous_value") or "valore precedente")
    current = str(component.get("scenario_value") or component.get("display_value") or "nuovo valore")
    return f"Componente modificato dallo scenario: {previous} -> {current}"


def render_components(
    model: dict[str, Any],
    layout: dict[str, Any],
    steady_ids: set[str],
    leakage_ids: set[str],
    transient_ids: set[str],
) -> str:
    """Renderizza ogni componente scegliendo il simbolo dal vocabolario comune."""
    indexed = model_components(model)
    led_profiles = (model.get("transient") or {}).get("led_profiles") or {}
    label_placements = vertical_label_placements(layout, indexed)
    rendered: list[str] = []
    for component_id, position in (layout.get("components") or {}).items():
        if not isinstance(position, dict):
            continue
        label_placement = label_placements.get(str(component_id)) or {}
        position = {
            **position,
            "label_side": label_placement.get("side", position.get("label_side")),
            "label_offset_x": label_placement.get("offset_x", position.get("label_offset_x")),
            "label_offset_y": label_placement.get("offset_y", position.get("label_offset_y")),
        }
        component = indexed.get(str(component_id)) or {}
        visual_class = normalize_component_type(position.get("component_type") or position.get("visual_class_name"), position.get("layout_kind"))
        terminal_count = len(position.get("terminals") or [])
        if "connector" in visual_class:
            symbol = render_connector(str(component_id), position)
        elif "gnd" in visual_class or "ground" in visual_class:
            symbol = render_ground(position)
        elif visual_class == "terminal":
            symbol = render_terminal_port(component, position)
        elif visual_class == "analog_meter":
            symbol = render_analog_meter(component, position)
        elif visual_class == "antenna":
            symbol = render_antenna(component, position)
        elif visual_class == "headset":
            symbol = render_headset(
                str(component_id), component, position, steady_ids, leakage_ids, transient_ids
            )
        elif visual_class in {"npn_transistor", "pnp_transistor", "bjt"}:
            symbol = render_bjt_transistor(
                str(component_id),
                component,
                position,
                steady_ids,
                transient_ids,
                transistor_kind="pnp" if visual_class == "pnp_transistor" else "npn",
            )
        elif terminal_count > 2:
            symbol = render_multi_terminal(str(component_id), position)
        else:
            symbol = render_two_terminal_symbol(
                str(component_id),
                component,
                position,
                steady_ids,
                leakage_ids,
                transient_ids,
                led_profiles,
                model.get("measurements") or {},
            )
        if component.get("is_scenario_added"):
            # Il colore rende visibile l'origine senza una label testuale ingombrante.
            tooltip = escape(scenario_component_tooltip(component, position))
            wrapper_class = "scenario-link-component" if visual_class == "connection" else "scenario-added-component"
            symbol = (
                f'<g class="{wrapper_class}">'
                f'<title>{tooltip}</title>'
                f"{symbol}</g>"
            )
        elif component.get("is_scenario_modified"):
            # La sorgente mostra il valore corrente; colore e tooltip segnalano la variazione.
            tooltip = escape(scenario_component_tooltip(component, position))
            symbol = (
                '<g class="scenario-modified-component">'
                f'<title>{tooltip}</title>'
                f"{symbol}</g>"
            )
        rendered.append(symbol)
    return "".join(rendered)


def render_node_constraints(layout: dict[str, Any]) -> str:
    """Disegna i vincoli di tensione come annotazioni applicate ai nodi."""
    rendered: list[str] = []
    for constraint in layout.get("node_constraints") or []:
        if not isinstance(constraint, dict):
            continue
        x = float(constraint.get("x") or 0)
        y = float(constraint.get("y") or 0)
        label_x = float(constraint.get("label_x") or x)
        label_y = float(constraint.get("label_y") or y)
        node_id = escape(str(constraint.get("node_id") or "nodo"))
        value = escape(str(constraint.get("value") or ""))
        label = f"Forced: {value}" if value else "Forced node"
        tooltip = f"Nodo {node_id} forzato a {value} dallo scenario tramite sorgente ideale SPICE"
        rendered.append(
            '<g class="node-constraint">'
            f'<title>{tooltip}</title>'
            f'<path class="constraint-leader" d="M{format_number(x)} {format_number(y)} '
            f'L{format_number(label_x)} {format_number(label_y)}"/>'
            f'<circle class="constraint-halo" cx="{format_number(x)}" cy="{format_number(y)}" r="16"/>'
            f'<circle class="constraint-node" cx="{format_number(x)}" cy="{format_number(y)}" r="5"/>'
            f'<rect class="constraint-badge" x="{format_number(label_x-52)}" y="{format_number(label_y-14)}" '
            'width="104" height="28" rx="5"/>'
            f'<text class="constraint-label" x="{format_number(label_x)}" y="{format_number(label_y+4)}">{label}</text>'
            '</g>'
        )
    return "".join(rendered)


def node_badge_candidates(layout: dict[str, Any], node_id: str) -> list[tuple[float, float]]:
    """Ricava punti accanto ai segmenti abbastanza lunghi di uno stesso nodo."""
    candidates: list[tuple[float, float]] = []
    for connection in layout.get("connections") or []:
        if not isinstance(connection, dict) or str(connection.get("node_id") or "") != node_id:
            continue
        route = connection.get("route") or []
        points = [
            (float(point.get("x") or 0), float(point.get("y") or 0))
            for point in route
            if isinstance(point, dict) and "x" in point and "y" in point
        ]
        for first, second in zip(points, points[1:]):
            length = abs(second[0] - first[0]) + abs(second[1] - first[1])
            if length < 20.0:
                continue
            middle_x = (first[0] + second[0]) / 2
            middle_y = (first[1] + second[1]) / 2
            if abs(first[1] - second[1]) < 0.01:
                candidates.extend(((middle_x, middle_y - 16.0), (middle_x, middle_y + 16.0)))
            else:
                candidates.extend(((middle_x + 18.0, middle_y), (middle_x - 18.0, middle_y)))
    return candidates


def render_node_badges(model: dict[str, Any], layout: dict[str, Any]) -> str:
    """Disegna badge discreti per i nodi SPICE non di massa sui rami liberi."""
    canvas = layout.get("canvas") or {}
    legend = canvas.get("legend") or {}
    legend_x = float(legend.get("x") or 835.0)
    component_bounds = [
        component_obstacle(position)
        for position in (layout.get("components") or {}).values()
        if isinstance(position, dict)
    ]
    # I badge non devono mai occupare la fascia grafica destinata alla legenda.
    component_bounds.append((legend_x - 10.0, 14.0, legend_x + 190.0, 222.0))
    occupied: list[tuple[float, float, float, float]] = []
    rendered: list[str] = []
    for node in model.get("nodes") or []:
        if not isinstance(node, dict):
            continue
        node_id = str(node.get("id") or "")
        if not node_id or node_id == "0":
            continue
        width, height = max(42.0, len(node_id) * 7.2 + 16.0), 20.0
        candidates = node_badge_candidates(layout, node_id)
        scored: list[tuple[float, float, float, tuple[float, float, float, float]]] = []
        for x, y in candidates:
            bounds = (x - width / 2, y - height / 2, x + width / 2, y + height / 2)
            outside = max(0.0, 10.0 - bounds[0]) + max(0.0, bounds[2] - 1030.0)
            outside += max(0.0, 10.0 - bounds[1]) + max(0.0, bounds[3] - 610.0)
            overlap = sum(rectangles_overlap(bounds, obstacle) for obstacle in component_bounds + occupied)
            scored.append((overlap * 100.0 + outside * 10_000.0, x, y, bounds))
        if not scored:
            continue
        _, x, y, bounds = min(scored, key=lambda candidate: candidate[0])
        occupied.append(bounds)
        label = escape(node_id)
        tooltip = escape(node_tooltip(model, node_id))
        rendered.append(
            '<g class="node-badge">'
            f'<title>{tooltip}</title>'
            f'<rect x="{format_number(bounds[0])}" y="{format_number(bounds[1])}" '
            f'width="{format_number(width)}" height="{format_number(height)}" rx="4"/>'
            f'<text x="{format_number(x)}" y="{format_number(y + 4)}">{label}</text>'
            '</g>'
        )
    return "".join(rendered)


def render_legend(x: float, y: float) -> str:
    """Disegna un'unica legenda compatta degli stati elettrici generali."""
    return f'''<g class="legend" transform="translate({format_number(x)} {format_number(y)})"><rect width="180" height="188" rx="6"/><text class="legend-title" x="14" y="22">Stati</text><path class="wire energized" d="M14 42 H54"/><text x="68" y="46">tensione presente</text><path class="wire active" d="M14 68 H54"/><text x="68" y="72">corrente DC</text><path class="wire transient" d="M14 94 H54"/><text x="68" y="98">segnale variabile</text><path class="wire mixed-signal" d="M14 120 H54"/><text x="68" y="124">DC + segnale</text><path class="wire idle" d="M14 146 H54"/><text x="68" y="150">nessuna corrente</text><circle class="constraint-node" cx="34" cy="170" r="5"/><text x="68" y="174">vincolo scenario</text></g>'''


def render_svg(model: dict[str, Any], layout: dict[str, Any]) -> str:
    """Compone il documento SVG completo del viewer."""
    canvas = layout.get("canvas") or {}
    width = int(canvas.get("width") or 1040)
    height = int(canvas.get("height") or 620)
    legend = canvas.get("legend") or {}
    legend_x = float(legend.get("x") or width - 205)
    legend_y = float(legend.get("y") or 24)
    voltages = node_voltages(model)
    steady_ids, leakage_ids, transient_ids = component_activity_ids(model)
    return f'''<svg class="viewer-svg" data-viewer-version="{VIEWER_RENDER_VERSION}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="Circuito equivalente dalla netlist SPICE">
{render_svg_style_blocks()}
<g class="connections">{render_connections(layout, model, steady_ids, leakage_ids, transient_ids, voltages)}</g>
<g class="components">{render_components(model, layout, steady_ids, leakage_ids, transient_ids)}</g>
<g class="node-badges">{render_node_badges(model, layout)}</g>
<g class="node-constraints">{render_node_constraints(layout)}</g>
{render_legend(legend_x, legend_y)}
</svg>'''


def write_viewer_svg(run_dir: Path) -> str:
    """Genera e salva `15_viewer.svg` nella cartella della run."""
    run_dir = run_dir.resolve()
    model = read_json(run_dir / VIEWER_MODEL_NAME)
    layout = read_json(run_dir / VIEWER_LAYOUT_NAME)
    if not model or not layout:
        raise FileNotFoundError("Servono 13_viewer_model.json e 14_viewer_layout.json prima dello step 15.")
    svg = render_svg(model, layout)
    (run_dir / VIEWER_SVG_NAME).write_text(svg, encoding="utf-8")
    return svg


