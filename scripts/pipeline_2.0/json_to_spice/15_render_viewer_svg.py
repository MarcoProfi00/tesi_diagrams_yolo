"""
Renderizza il viewer SVG generale di una run della Pipeline 2.0.

Lo step 15 non ricostruisce l'immagine originale e non contiene coordinate di
singoli circuiti. Legge il modello elettrico dello step 13 e il layout guidato
dalle bbox dello step 14, quindi disegna simboli semplici in stile Falstad.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from viewer_component_library import component_spec, normalize_component_type


VIEWER_MODEL_NAME = "13_viewer_model.json"
VIEWER_LAYOUT_NAME = "14_viewer_layout.json"
VIEWER_SVG_NAME = "15_viewer.svg"


def read_json(path: Path) -> dict[str, Any]:
    """Legge un JSON e restituisce un dizionario vuoto in caso di errore."""
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


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


def active_component_ids(model: dict[str, Any]) -> set[str]:
    """Determina quali componenti appartengono a un ramo percorso da corrente."""
    measurements = model.get("measurements") or {}
    components = [item for item in model.get("netlist_components") or [] if isinstance(item, dict)]
    active_ids: set[str] = set()
    active_nodes: set[str] = set()

    # Le misure dirette sono la fonte primaria per stabilire l'attivita' del ramo.
    for component in components:
        component_id = str(component.get("id") or "")
        current = measured_component_current(component_id, measurements)
        if current is not None and abs(current) > 1e-6:
            active_ids.add(component_id)
            active_nodes.update(str(node_id) for node_id in component.get("nodes") or [])

    # Diodi e LED ereditano il flusso dal bipolo misurato sullo stesso ramo.
    for component in components:
        component_id = str(component.get("id") or "")
        nodes = {str(node_id) for node_id in component.get("nodes") or []}
        source_id = str(component.get("source_component_id") or "").lower()
        is_diode = component.get("kind") == "diode" or source_id.startswith("led")
        if is_diode and bool((nodes - {"0"}) & active_nodes):
            active_ids.add(component_id)
    return active_ids


def electrical_class(kind: str, connection: dict[str, Any], active_ids: set[str]) -> str:
    """Sceglie la classe grafica di un collegamento usando la corrente del ramo."""
    if kind == "structural":
        return "wire guide"
    endpoints = {str((connection.get(side) or {}).get("component_id") or "") for side in ("from", "to")}
    return "wire active" if bool(endpoints & active_ids) else "wire idle"


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


def render_connections(layout: dict[str, Any], active_ids: set[str]) -> str:
    """Disegna tutti i collegamenti prodotti dallo step 14."""
    paths: list[str] = []
    for connection in layout.get("connections") or []:
        if not isinstance(connection, dict):
            continue
        start = connection.get("from") or {}
        end = connection.get("to") or {}
        if not all(key in start and key in end for key in ("x", "y")):
            continue
        css_class = electrical_class(str(connection.get("kind") or "electrical"), connection, active_ids)
        paths.append(f'<path class="{css_class}" d="{orthogonal_path(start, end)}"/>')
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
    parameters = component.get("parameters") or {}
    component_type = str(position.get("component_type") or "").lower()
    if component_type in {"capacitor", "resistor"} and component.get("display_label"):
        return str(component["display_label"])
    if component_type in {"battery", "capacitor", "resistor"} and parameters.get("value") is not None:
        value = parameters.get("value")
        unit = str(parameters.get("unit") or "")
        return f"{value:g} {unit}" if isinstance(value, (int, float)) else f"{value} {unit}".strip()
    value = str(component.get("value") or "").strip()
    if value:
        return value.split()[0]
    label = str(position.get("label") or "").strip()
    return label if label else str(component.get("id") or "")


def render_two_terminal_symbol(
    component_id: str,
    component: dict[str, Any],
    position: dict[str, Any],
    active_ids: set[str],
) -> str:
    """Disegna un componente a due terminali usando il vocabolario SVG comune."""
    center_x, center_y, angle, length = two_terminal_geometry(position)
    half = max(24.0, min(length / 2, 62.0))
    visual_class = str(position.get("component_type") or position.get("visual_class_name") or position.get("layout_kind") or "").lower()
    active = component_id in active_ids
    stroke_class = "symbol"
    label = escape(component_value(component, position))
    flow_path = ""

    if "switch" in visual_class:
        state = str(position.get("state") or (component.get("parameters") or {}).get("state") or "open").lower()
        blade = f'M{-half + 8} 0 H{half - 8}' if state == "closed" else f'M{-half + 8} 0 L{half - 8} -20'
        body = f'<circle cx="{-half}" cy="0" r="4"/><circle cx="{half}" cy="0" r="4"/><path d="{blade}"/>'
        flow_path = blade if state == "closed" else ""
    elif visual_class == "connection":
        flow_path = f'M{-half} 0 H{half}'
        body = f'<path d="{flow_path}"/>'
    elif visual_class == "resistor":
        flow_path = f'M{-half} 0 H-36 L-30 -14 L-18 14 L-6 -14 L6 14 L18 -14 L30 14 L36 0 H{half}'
        body = f'<path d="{flow_path}"/>'
    elif "capacitor" in visual_class:
        body = f'<path d="M{-half} 0 H-8 M-8 -20 V20 M8 -20 V20 M8 0 H{half}"/>'
    elif "inductor" in visual_class:
        body = f'<path d="M{-half} 0 H{-half + 10} C{-half + 18} -20 {-half + 30} -20 {-half + 30} 0 C{-half + 38} -20 {-half + 50} -20 {-half + 50} 0 C{-half + 58} -20 {half - 10} -20 {half - 10} 0 H{half}"/>'
    elif "led" in visual_class or "diode" in visual_class:
        glow = '<ellipse class="led-glow" cx="0" cy="0" rx="42" ry="30"/>' if active and "led" in visual_class else ""
        rays = '<path class="led-rays" d="M5 -20 L17 -34 M20 -16 L32 -30"/>' if "led" in visual_class else ""
        body = f'{glow}<path d="M{-half} 0 H-18 M-18 -18 L18 0 L-18 18 Z M18 -20 V20 M18 0 H{half}"/>{rays}'
        flow_path = f'M{-half} 0 H{half}'
    elif "lamp" in visual_class:
        glow = '<ellipse class="lamp-glow" cx="0" cy="0" rx="46" ry="38"/>' if active else ""
        body = f'{glow}<path d="M{-half} 0 H-24 M24 0 H{half}"/><circle cx="0" cy="0" r="24"/><path d="M-14 -14 L14 14 M14 -14 L-14 14"/>'
        flow_path = f'M{-half} 0 H-24 M-14 -14 L14 14 M14 -14 L-14 14 M24 0 H{half}'
    elif "battery" in visual_class or "voltage_source" in visual_class:
        if visual_class == "battery":
            glow = '<rect class="battery-glow" x="-38" y="-30" width="76" height="60" rx="8"/>' if active else ""
            body = (
                f'{glow}<path d="M{-half} 0 H-32 M32 0 H{half}"/>'
                '<rect class="battery-body" x="-32" y="-24" width="64" height="48" rx="4"/>'
                f'<text class="battery-polarity" x="-16" y="5" transform="rotate({format_number(-angle)} -16 0)">−</text>'
                f'<text class="battery-polarity positive" x="16" y="5" transform="rotate({format_number(-angle)} 16 0)">+</text>'
            )
            flow_path = f'M{-half} 0 H{-32}' if active else ""
        else:
            body = f'<path d="M{-half} 0 H-9 M-9 -22 V22 M9 -13 V13 M9 0 H{half}"/>'
    elif "fuse" in visual_class:
        body = f'<path d="M{-half} 0 H-24 M24 0 H{half}"/><rect x="-24" y="-10" width="48" height="20" rx="3"/>'
    else:
        body = f'<path d="M{-half} 0 H-24 M24 0 H{half}"/><rect x="-24" y="-18" width="48" height="36" rx="4"/><path d="M-14 0 C-8 -12 8 12 14 0"/>'

    is_vertical = 45 <= abs(angle) <= 135
    if is_vertical:
        label_x = center_x + 34
        label_y = center_y + 4
        label_anchor = "start"
    else:
        label_x = center_x
        label_y = center_y - 31
        label_anchor = "middle"
    label_svg = (
        f'<text class="component-label" style="text-anchor:{label_anchor}" '
        f'x="{format_number(label_x)}" y="{format_number(label_y)}">{label}</text>'
        if label else ""
    )
    return (
        f'<g class="component" transform="translate({format_number(center_x)} {format_number(center_y)}) rotate({format_number(angle)})">'
        f'<g class="{stroke_class}">{body}</g>'
        f'{f"<path class=\"component-flow\" d=\"{flow_path}\"/>" if active and flow_path else ""}'
        "</g>"
        f"{label_svg}"
    )


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


def render_components(model: dict[str, Any], layout: dict[str, Any], active_ids: set[str]) -> str:
    """Renderizza ogni componente scegliendo il simbolo dal vocabolario comune."""
    indexed = model_components(model)
    rendered: list[str] = []
    for component_id, position in (layout.get("components") or {}).items():
        if not isinstance(position, dict):
            continue
        component = indexed.get(str(component_id)) or {}
        visual_class = normalize_component_type(position.get("component_type") or position.get("visual_class_name"), position.get("layout_kind"))
        terminal_count = len(position.get("terminals") or [])
        if "connector" in visual_class:
            rendered.append(render_connector(str(component_id), position))
        elif "gnd" in visual_class or "ground" in visual_class:
            rendered.append(render_ground(position))
        elif terminal_count > 2:
            rendered.append(render_multi_terminal(str(component_id), position))
        else:
            rendered.append(render_two_terminal_symbol(str(component_id), component, position, active_ids))
    return "".join(rendered)


def render_legend(width: int) -> str:
    """Disegna la legenda minima con le regole comuni del viewer."""
    x = width - 205
    return f'''<g class="legend" transform="translate({x} 24)"><rect width="180" height="116" rx="6"/><text class="legend-title" x="14" y="22">Legenda</text><path class="wire active" d="M14 42 H54"/><text x="68" y="46">ramo alimentato</text><path class="wire idle" d="M14 68 H54"/><text x="68" y="72">ramo fermo</text><path class="wire guide" d="M14 94 H54"/><text x="68" y="98">collegamento guida</text></g>'''


def render_svg(model: dict[str, Any], layout: dict[str, Any]) -> str:
    """Compone il documento SVG completo del viewer."""
    canvas = layout.get("canvas") or {}
    width = int(canvas.get("width") or 1040)
    height = int(canvas.get("height") or 620)
    voltages = node_voltages(model)
    active_ids = active_component_ids(model)
    return f'''<svg class="viewer-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="Circuito equivalente dalla netlist SPICE">
<defs><filter id="ledGlow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="8"/></filter></defs>
<style>.viewer-svg{{background:transparent;font-family:Arial,sans-serif}}.wire,.symbol path,.symbol circle,.symbol rect,.connector rect,.connector circle{{fill:none;stroke:#f4f7fb;stroke-width:3;stroke-linecap:round;stroke-linejoin:round}}.wire.active,.component-flow{{fill:none;stroke:#dce51a;stroke-width:3;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:9 10;animation:viewerCurrent 1s linear infinite}}.wire.idle{{stroke:#aeb9c9;stroke-dasharray:10 8;opacity:.9}}.wire.guide{{stroke:#52647c;stroke-dasharray:3 11;opacity:.8}}.component-label{{fill:#f4f7fb;font-size:13px;font-weight:700;text-anchor:middle;letter-spacing:0}}.pin-label{{fill:#f4f7fb;font-size:12px;font-weight:700;text-anchor:end;letter-spacing:0}}.battery-polarity{{fill:#cbd5e1;font-size:19px;font-weight:700;text-anchor:middle;letter-spacing:0}}.battery-polarity.positive{{fill:#f8fafc}}.battery-glow{{fill:#dce51a!important;opacity:.16;stroke:none!important;filter:url(#ledGlow);animation:viewerBatteryPulse 1.5s ease-in-out infinite}}.led-glow{{fill:#ef4444;opacity:.3;filter:url(#ledGlow);stroke:none;animation:viewerLedPulse 1.25s ease-in-out infinite}}.lamp-glow{{fill:#ffd84a;opacity:.24;filter:url(#ledGlow);stroke:none;animation:viewerLampPulse 1.4s ease-in-out infinite}}.led-rays{{stroke:#ff4d5a!important}}.legend rect{{fill:#06101d;stroke:#314257}}.legend text{{fill:#d7dfeb;font-size:11px;letter-spacing:0}}.legend-title{{font-weight:700}}.legend .wire{{stroke-width:3}}.connector rect{{fill:#0b1728}}.connector circle{{fill:#0b1728}}@keyframes viewerCurrent{{to{{stroke-dashoffset:-38}}}}@keyframes viewerLedPulse{{0%,100%{{opacity:.2}}50%{{opacity:.48}}}}@keyframes viewerLampPulse{{0%,100%{{opacity:.16}}50%{{opacity:.38}}}}@keyframes viewerBatteryPulse{{0%,100%{{opacity:.1}}50%{{opacity:.24}}}}@media (prefers-reduced-motion:reduce){{.wire.active,.component-flow,.led-glow,.lamp-glow,.battery-glow{{animation:none}}}}</style>
<g class="connections">{render_connections(layout, active_ids)}</g>
<g class="components">{render_components(model, layout, active_ids)}</g>
{render_legend(width)}
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


def main() -> None:
    """Gestisce l'esecuzione dello step 15 da riga di comando."""
    parser = argparse.ArgumentParser(description="Renderizza il viewer SVG generale della Pipeline 2.0.")
    parser.add_argument("--run-dir", required=True, help="Cartella run con gli artefatti 13 e 14.")
    args = parser.parse_args()
    run_dir = Path(args.run_dir)
    write_viewer_svg(run_dir)
    print(f"Scritto {run_dir / VIEWER_SVG_NAME}")


if __name__ == "__main__":
    main()
