"""
Costruisce il modello dati del viewer per una run della Pipeline 2.0.

Il modello resta intenzionalmente guidato dalla netlist: `07_netlist.cir`
descrive il circuito che ngspice ha realmente simulato, mentre
`03_node_map.json` e `06_component_rules.json` aggiungono il contesto
strutturale utile al viewer, come connector, masse e switch aperti non emessi
in SPICE.
"""

from __future__ import annotations

import csv
from datetime import datetime
import re
from pathlib import Path
from typing import Any

from .contracts import (
    NETLIST_NAME,
    PROJECT_ROOT,
    VIEWER_MODEL_NAME,
    VIEWER_MODEL_SCHEMA_VERSION,
)
from .json_io import read_json, write_json

TRANSIENT_VARIATION_EPSILON = 1e-5
MAX_TRANSIENT_VIEWER_SAMPLES = 800


def normalize_node(node: str) -> str:
    """Normalizza il nome di un nodo SPICE mantenendo `0` come massa."""
    node = str(node).strip()
    return "0" if node == "0" else node.upper()


def spice_kind(name: str) -> str:
    """Ricava il tipo logico di componente dal prefisso SPICE."""
    prefix = name[:1].upper()
    return {
        "R": "resistor",
        "C": "capacitor",
        "L": "inductor",
        "V": "voltage_source",
        "I": "current_source",
        "D": "diode",
        "Q": "bjt",
    }.get(prefix, "unknown")


def expected_node_count(name: str) -> int:
    """Restituisce quanti nodi leggere dalla riga SPICE del componente."""
    prefix = name[:1].upper()
    if prefix == "Q":
        return 3
    return 2


def source_component_id(spice_name: str) -> str | None:
    """Prova a ricostruire l'id del componente originale dal nome SPICE."""
    prefix = spice_name[:1].upper()
    if prefix not in {"R", "C", "L", "D", "Q", "V", "I"}:
        return None
    base = spice_name[1:]
    if spice_name.lower().startswith("rmeter_"):
        # Lo step 07 usa `Rmeter_` per il proxy resistivo degli strumenti analogici.
        base = spice_name[len("Rmeter_") :]
    match = re.match(r"(.+)_([0-9]+)$", base)
    if not match:
        return None
    return f"{match.group(1).lower()}.{match.group(2)}"


def enrich_components_with_rules(
    components: list[dict[str, Any]],
    rules: dict[str, Any],
) -> list[dict[str, Any]]:
    """Aggiunge classe, parametri e label dichiarati nelle regole Pipeline 2.0."""
    component_rules = rules.get("components") or {}
    enriched: list[dict[str, Any]] = []
    for component in components:
        item = dict(component)
        source_id = str(item.get("source_component_id") or "")
        rule = component_rules.get(source_id) or {}
        if isinstance(rule, dict) and rule:
            item["class_name"] = rule.get("class_name")
            item["parameters"] = rule.get("parameters") or {}
            item["display_label"] = (rule.get("parameters") or {}).get("label_text")
            if rule.get("status") == "measurement_only":
                item["viewer_proxy_for"] = source_id
                item["viewer_role"] = "simulation_measurement_proxy"
        enriched.append(item)
    return enriched


def parse_netlist(netlist_path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    """Estrae componenti, direttive e warning dal file `07_netlist.cir`."""
    components: list[dict[str, Any]] = []
    directives: list[dict[str, Any]] = []
    warnings: list[str] = []
    inside_control_block = False

    if not netlist_path.exists():
        warnings.append(f"Netlist mancante: {netlist_path}")
        return components, directives, warnings

    for line_number, raw_line in enumerate(netlist_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("*"):
            continue
        if line.startswith("."):
            directives.append({"line_number": line_number, "directive": line})
            if line.lower() == ".control":
                inside_control_block = True
            elif line.lower() == ".endc":
                inside_control_block = False
            continue
        if inside_control_block:
            # I comandi `run` e `wrdata` appartengono a ngspice e non sono componenti.
            directives.append({"line_number": line_number, "directive": line, "scope": "control"})
            continue

        parts = line.split()
        if not parts:
            continue
        name = parts[0]
        node_count = expected_node_count(name)
        if len(parts) < 1 + node_count:
            warnings.append(f"Impossibile interpretare la riga {line_number}: {line}")
            continue

        nodes = [normalize_node(item) for item in parts[1 : 1 + node_count]]
        value_tokens = parts[1 + node_count :]
        is_scenario_added = name.upper().startswith(("RSCENARIO", "VSCENARIO", "ISCENARIO"))
        component = {
            "id": name,
            "spice_name": name,
            "kind": spice_kind(name),
            "nodes": nodes,
            "value": " ".join(value_tokens),
            "model": value_tokens[-1] if value_tokens and name[:1].upper() in {"D", "Q"} else None,
            "source_component_id": source_component_id(name),
            "is_scenario_added": is_scenario_added,
            "source_line": raw_line,
            "line_number": line_number,
        }
        components.append(component)

    return components, directives, warnings


def parse_ngspice_stdout(stdout_path: Path) -> dict[str, Any]:
    """Legge tensioni e correnti operative dall'output testuale di ngspice."""
    measurements: dict[str, Any] = {
        "node_voltages": {},
        "branch_currents": {},
        "device_currents": {},
    }
    if not stdout_path.exists():
        measurements["status"] = "missing"
        return measurements

    lines = stdout_path.read_text(encoding="utf-8", errors="replace").splitlines()
    section: str | None = None
    pending_resistor_devices: list[str] = []

    for raw_line in lines:
        line = raw_line.strip()
        lower = line.lower()
        if not line:
            continue
        if lower.startswith("node") and "voltage" in lower:
            section = "node_voltage"
            continue
        if lower.startswith("source") and "current" in lower:
            section = "source_current"
            continue
        if lower.startswith("device"):
            tokens = line.split()[1:]
            pending_resistor_devices = [token.lower() for token in tokens]
            section = "device_table"
            continue
        if section == "node_voltage":
            match = re.match(r"^(n[0-9a-z_]+)\s+([-+0-9.eE]+)$", lower)
            if match:
                measurements["node_voltages"][match.group(1).upper()] = float(match.group(2))
            continue
        if section == "source_current":
            match = re.match(r"^([a-z0-9_#]+)\s+([-+0-9.eE]+)$", lower)
            if match:
                measurements["branch_currents"][match.group(1).upper()] = float(match.group(2))
            continue
        if section == "device_table" and lower.startswith("i ") and pending_resistor_devices:
            values = line.split()[1:]
            for device, value in zip(pending_resistor_devices, values):
                try:
                    measurements["device_currents"][device.upper()] = float(value)
                except ValueError:
                    continue

    measurements["node_voltages"].setdefault("0", 0.0)
    measurements["status"] = "loaded"
    return measurements


def transient_node_id(column_name: str) -> str | None:
    """Ricava il nodo SPICE da una colonna CSV nel formato `v(N001)`."""
    match = re.fullmatch(r"v\(([^)]+)\)", str(column_name).strip(), flags=re.IGNORECASE)
    return normalize_node(match.group(1)) if match else None


def numeric_series_span(values: list[float]) -> dict[str, float | bool]:
    """Riassume intervallo e attraversamento dello zero di una serie numerica."""
    if not values:
        return {"min": 0.0, "max": 0.0, "span": 0.0, "crosses_zero": False}
    minimum = min(values)
    maximum = max(values)
    return {
        "min": minimum,
        "max": maximum,
        "span": maximum - minimum,
        "crosses_zero": minimum < -TRANSIENT_VARIATION_EPSILON and maximum > TRANSIENT_VARIATION_EPSILON,
    }


def component_transient_activity(
    components: list[dict[str, Any]],
    node_series: dict[str, list[float]],
) -> dict[str, dict[str, Any]]:
    """Stima l'attivita' variabile di ogni componente dalle tensioni ai terminali."""
    activity: dict[str, dict[str, Any]] = {}
    for component in components:
        component_id = str(component.get("id") or "")
        nodes = [str(node_id) for node_id in component.get("nodes") or []]
        available = [node_id for node_id in nodes if node_id in node_series]
        if not component_id or len(available) < 2:
            continue

        # Per i bipoli usa la tensione differenziale; per i componenti a piu'
        # terminali conserva la coppia con la variazione maggiore.
        best: dict[str, Any] | None = None
        for first_index, first_node in enumerate(available):
            for second_node in available[first_index + 1 :]:
                differences = [
                    first - second
                    for first, second in zip(node_series[first_node], node_series[second_node])
                ]
                summary = numeric_series_span(differences)
                candidate = {
                    **summary,
                    "nodes": [first_node, second_node],
                }
                if best is None or float(candidate["span"]) > float(best["span"]):
                    best = candidate

        if best is None:
            continue
        variable = float(best["span"]) >= TRANSIENT_VARIATION_EPSILON
        kind = str(component.get("kind") or "").lower()
        source_id = str(component.get("source_component_id") or "").lower()
        alternating = bool(best["crosses_zero"]) or kind == "capacitor" or "signal_source" in source_id
        activity[component_id] = {
            **best,
            "variable": variable,
            "flow_mode": "alternating" if variable and alternating else "pulsating" if variable else "steady",
        }
    return activity


def downsample_indices(sample_count: int, maximum: int) -> list[int]:
    """Seleziona indici equidistanti preservando primo e ultimo campione."""
    if sample_count <= maximum:
        return list(range(sample_count))
    return sorted(
        {
            round(index * (sample_count - 1) / (maximum - 1))
            for index in range(maximum)
        }
    )


def build_transient_traces(
    times: list[float],
    node_series: dict[str, list[float]],
) -> dict[str, Any]:
    """Prepara serie compatte conservando il tempo reale di ogni campione."""
    indices = downsample_indices(len(times), MAX_TRANSIENT_VIEWER_SAMPLES)
    return {
        "time": [times[index] for index in indices],
        "series": {
            f"v({node_id})": [values[index] for index in indices]
            for node_id, values in node_series.items()
            if node_id != "0" and len(values) == len(times)
        },
    }


def parse_transient_csv(
    csv_path: Path,
    components: list[dict[str, Any]],
) -> dict[str, Any]:
    """Legge `08_tran.csv` e produce un riepilogo leggero per il viewer."""
    if not csv_path.exists():
        return {"status": "missing", "component_activity": {}}

    node_series: dict[str, list[float]] = {}
    times: list[float] = []
    try:
        with csv_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            columns = {
                column: transient_node_id(column)
                for column in (reader.fieldnames or [])
                if transient_node_id(column)
            }
            for node_id in columns.values():
                if node_id:
                    node_series.setdefault(node_id, [])
            node_series.setdefault("0", [])

            for row in reader:
                try:
                    time_value = float(row.get("time") or row.get("Time") or "")
                except (TypeError, ValueError):
                    continue
                sample_values: dict[str, float] = {}
                try:
                    for column, node_id in columns.items():
                        if node_id:
                            sample_values[node_id] = float(row.get(column) or "")
                except (TypeError, ValueError):
                    continue
                times.append(time_value)
                for node_id, value in sample_values.items():
                    node_series[node_id].append(value)
                node_series["0"].append(0.0)
    except (OSError, csv.Error):
        return {"status": "invalid", "component_activity": {}}

    node_activity = {
        node_id: numeric_series_span(values)
        for node_id, values in node_series.items()
        if values
    }
    return {
        "status": "loaded" if times else "empty",
        "sample_count": len(times),
        "time_start": times[0] if times else None,
        "time_end": times[-1] if times else None,
        "node_activity": node_activity,
        "component_activity": component_transient_activity(components, node_series),
        "traces": build_transient_traces(times, node_series),
    }


def select_transient_quantities(
    transient: dict[str, Any],
    scenario: dict[str, Any] | None,
) -> list[str]:
    """Sceglie le tracce dal `compare` o dalle tre variazioni maggiori."""
    series = ((transient.get("traces") or {}).get("series") or {})
    available = {str(name).lower(): str(name) for name in series}
    selected: list[str] = []
    compare = scenario.get("compare") if isinstance(scenario, dict) else []
    for quantity in compare if isinstance(compare, list) else []:
        canonical = available.get(str(quantity).strip().lower())
        if canonical and canonical not in selected:
            selected.append(canonical)
        if len(selected) == 3:
            return selected

    if selected:
        return selected
    node_activity = transient.get("node_activity") or {}
    ranked_nodes = sorted(
        (
            (str(node_id), float(activity.get("span") or 0.0))
            for node_id, activity in node_activity.items()
            if node_id != "0" and isinstance(activity, dict)
        ),
        key=lambda item: (-item[1], item[0]),
    )
    return [
        available[f"v({node_id})".lower()]
        for node_id, span in ranked_nodes
        if span >= TRANSIENT_VARIATION_EPSILON and f"v({node_id})".lower() in available
    ][:3]


def attach_transient_scope_data(
    transient: dict[str, Any],
    scenario: dict[str, Any] | None,
    scenario_dir: Path | None,
    components: list[dict[str, Any]],
) -> dict[str, Any]:
    """Aggiunge selezione scope e confronto base alla run corrente."""
    transient["selected_traces"] = select_transient_quantities(transient, scenario)
    transient["steady_start"] = (
        float(transient.get("time_start") or 0.0)
        + (float(transient.get("time_end") or 0.0) - float(transient.get("time_start") or 0.0)) * 0.2
    )
    if not scenario_dir:
        return transient

    base_csv = scenario_dir / "base_snapshot" / "08_tran.csv"
    base_transient = parse_transient_csv(base_csv, components)
    selected = transient["selected_traces"]
    base_traces = base_transient.get("traces") or {}
    base_series = base_traces.get("series") or {}
    transient["base_traces"] = {
        "time": base_traces.get("time") or [],
        "series": {
            quantity: base_series[quantity]
            for quantity in selected
            if quantity in base_series
        },
    }
    return transient


def measurement_voltage(
    nodes: dict[str, Any],
    measurements: dict[str, Any],
) -> float | None:
    """Calcola la lettura di un voltmetro differenziale dalle tensioni OP."""
    node_voltages = measurements.get("node_voltages") or {}
    ordered_nodes = [normalize_node(node_id) for node_id in nodes.values()]
    if len(ordered_nodes) < 2:
        return None
    first = node_voltages.get(ordered_nodes[0])
    second = node_voltages.get(ordered_nodes[1])
    if first is None or second is None:
        return None
    try:
        return float(first) - float(second)
    except (TypeError, ValueError):
        return None


def build_structural_components(
    node_map: dict[str, Any],
    rules: dict[str, Any],
    measurements: dict[str, Any],
) -> list[dict[str, Any]]:
    """Costruisce componenti strutturali e strumenti di misura non emessi in SPICE."""
    terminal_nodes = node_map.get("component_terminal_nodes") or {}
    components = rules.get("components") or {}
    structural: list[dict[str, Any]] = []

    for component_id, rule in components.items():
        if not isinstance(rule, dict):
            continue
        class_name = str(rule.get("class_name") or "Component")
        status = str(rule.get("status") or "")
        support = str(rule.get("spice_support") or "")
        emit_as = rule.get("emit_as")
        is_structural = status == "not_emitted" or support == "structural" or emit_as is None
        is_measurement = status == "measurement_only" or support == "measurement"
        if not is_structural and not is_measurement:
            continue
        parameters = dict(rule.get("parameters") or {})
        nodes = terminal_nodes.get(component_id) or rule.get("nodes") or {}
        measurement_kind = str(rule.get("measurement_kind") or parameters.get("kind") or "").lower()
        reading = measurement_voltage(nodes, measurements) if measurement_kind == "voltage" or parameters.get("kind") == "voltmeter" else None
        structural.append(
            {
                "id": component_id,
                "class_name": class_name,
                "nodes": nodes,
                "status": status,
                "spice_support": support,
                "parameters": parameters,
                "display_label": parameters.get("label_text") or parameters.get("label"),
                "measurement_kind": measurement_kind or None,
                "measurement_value": reading,
                "measurement_unit": "V" if reading is not None else None,
                "strategy": rule.get("strategy"),
                "reason": rule.get("reason"),
            }
        )

    return structural


def remove_emitted_simplified_duplicates(
    structural_components: list[dict[str, Any]],
    netlist_components: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Evita di disegnare due volte un componente semplificato gia' emesso."""
    emitted_source_ids = {
        str(component.get("source_component_id") or "")
        for component in netlist_components
        if component.get("source_component_id")
    }
    return [
        component
        for component in structural_components
        if not (
            str(component.get("spice_support") or "") == "simplified"
            and str(component.get("id") or "") in emitted_source_ids
        )
    ]


def scenario_closed_switches(scenario: dict[str, Any], components: list[dict[str, Any]]) -> set[str]:
    """Trova gli switch chiusi da uno scenario, usando azioni e netlist emessa."""
    closed: set[str] = set()
    actions = scenario.get("actions") if isinstance(scenario, dict) else []
    if isinstance(actions, list):
        for action in actions:
            if not isinstance(action, dict):
                continue
            if action.get("type") == "close_switch" and action.get("target"):
                closed.add(str(action["target"]))

    for component in components:
        source_id = str(component.get("source_component_id") or "")
        if component.get("is_scenario_added") and source_id.startswith("scenario_switch"):
            closed.add(source_id.removeprefix("scenario_"))
    return closed


def apply_scenario_visual_overrides(
    structural: list[dict[str, Any]],
    scenario: dict[str, Any],
    components: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Aggiorna lo stato visivo dei componenti strutturali modificati dallo scenario."""
    closed_switches = scenario_closed_switches(scenario, components)
    if not closed_switches:
        return structural

    updated: list[dict[str, Any]] = []
    for component in structural:
        item = dict(component)
        if str(item.get("id")) in closed_switches:
            parameters = dict(item.get("parameters") or {})
            parameters["state"] = "closed"
            parameters["state_source"] = "scenario_close_switch"
            item["parameters"] = parameters
            item["viewer_state"] = "closed_by_scenario"
        updated.append(item)
    return updated


def apply_scenario_component_roles(
    components: list[dict[str, Any]],
    scenario: dict[str, Any],
) -> list[dict[str, Any]]:
    """Distingue i componenti fisici dagli equivalenti numerici degli scenari."""
    connection_pairs: set[frozenset[str]] = set()
    voltage_clamps: dict[str, Any] = {}
    actions = scenario.get("actions") if isinstance(scenario, dict) else []
    for action in actions if isinstance(actions, list) else []:
        if not isinstance(action, dict):
            continue
        if action.get("type") == "drive_node_voltage" and action.get("target"):
            voltage_clamps[normalize_node(str(action["target"]))] = action.get("value")
            continue
        if action.get("type") not in {"connect_nodes", "feed_nodes_from_source_node"}:
            continue
        first = str(action.get("from") or action.get("source_node") or "")
        targets = action.get("target_nodes") or [action.get("to") or action.get("target_node")]
        for target in targets if isinstance(targets, list) else []:
            second = str(target or "")
            if first and second:
                connection_pairs.add(frozenset({normalize_node(first), normalize_node(second)}))

    updated: list[dict[str, Any]] = []
    for component in components:
        item = dict(component)
        component_nodes = frozenset(str(node_id) for node_id in item.get("nodes") or [])
        if item.get("is_scenario_added") and component_nodes in connection_pairs:
            item["viewer_kind"] = "connection"
            item["viewer_label"] = "link"
            item["viewer_reason"] = "scenario_numeric_continuity_element"
        if item.get("is_scenario_added") and item.get("kind") == "voltage_source":
            target_node = next(
                (
                    node_id for node_id in item.get("nodes") or []
                    if normalize_node(str(node_id)) in voltage_clamps
                ),
                None,
            )
            if target_node and "0" in {normalize_node(str(node_id)) for node_id in item.get("nodes") or []}:
                normalized_target = normalize_node(str(target_node))
                item["viewer_kind"] = "node_voltage_clamp"
                item["viewer_role"] = "scenario_control_constraint"
                item["viewer_target_node"] = normalized_target
                item["viewer_forced_value"] = voltage_clamps[normalized_target]
                item["viewer_reason"] = "drive_node_voltage_ideal_spice_source"
        updated.append(item)
    return updated


def mark_scenario_modified_components(
    components: list[dict[str, Any]],
    scenario: dict[str, Any],
    scenario_dir: Path | None,
) -> list[dict[str, Any]]:
    """Marca sorgenti e componenti modificati conservando il valore della base run."""
    actions = scenario.get("actions") if isinstance(scenario, dict) else []
    changed_values = {
        str(action.get("target") or "").lower(): action.get("value")
        for action in actions if isinstance(actions, list) and isinstance(action, dict)
        if action.get("type") in {"change_source_value", "change_component_value"} and action.get("target")
    }
    if not changed_values:
        return components

    base_components: list[dict[str, Any]] = []
    if scenario_dir:
        base_components, _, _ = parse_netlist(scenario_dir / "base_snapshot" / NETLIST_NAME)
    base_by_name = {
        str(component.get("spice_name") or component.get("id") or "").lower(): component
        for component in base_components
    }

    updated: list[dict[str, Any]] = []
    for component in components:
        item = dict(component)
        aliases = {
            str(item.get("id") or "").lower(),
            str(item.get("spice_name") or "").lower(),
            str(item.get("source_component_id") or "").lower(),
        }
        target = next((name for name in aliases if name in changed_values), None)
        if target:
            base_component = base_by_name.get(str(item.get("spice_name") or "").lower()) or {}
            item["is_scenario_modified"] = True
            item["scenario_previous_value"] = base_component.get("value")
            item["scenario_value"] = item.get("value") or changed_values[target]
        updated.append(item)
    return updated


def compact_source_value(value: Any, unit: str = "V") -> str:
    """Converte un valore di sorgente SPICE in una label visuale compatta."""
    text = str(value or "").strip()
    match = re.fullmatch(r"(?:DC\s+)?([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[a-zA-Z]+)?)", text, re.IGNORECASE)
    if not match:
        return text
    scalar = match.group(1)
    return scalar if scalar.lower().endswith(unit.lower()) else f"{scalar} {unit}"


def enrich_structural_terminals(
    structural: list[dict[str, Any]],
    components: list[dict[str, Any]],
    rules: dict[str, Any],
    values_bound: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Aggiunge label ai terminali e fonde le alimentazioni SPICE equivalenti."""
    node_labels = values_bound.get("nodes") or {}
    supplies = rules.get("supplies") or values_bound.get("supplies") or {}
    netlist = [dict(component) for component in components]
    enriched: list[dict[str, Any]] = []

    for component in structural:
        item = dict(component)
        component_id = str(item.get("id") or "")
        if "terminal" not in str(item.get("class_name") or "").lower():
            enriched.append(item)
            continue

        item["viewer_kind"] = "terminal"
        terminal_label = next(
            (
                data for terminal_id, data in node_labels.items()
                if str(terminal_id).startswith(f"{component_id}_") and isinstance(data, dict)
            ),
            {},
        )
        terminal_nodes = list((item.get("nodes") or {}).values())
        item["display_label"] = (
            terminal_label.get("label")
            or terminal_label.get("label_text")
            or (str(terminal_nodes[0]) if terminal_nodes else "PORT")
        )

        for supply_name, supply in supplies.items():
            if not isinstance(supply, dict):
                continue
            parameters = supply.get("parameters") if isinstance(supply.get("parameters"), dict) else supply
            terminal_id = str(parameters.get("terminal") or "")
            if not terminal_id.startswith(f"{component_id}_"):
                continue

            expected_name = f"V{supply_name}".lower()
            supply_nodes = {normalize_node(node) for node in supply.get("nodes") or []}
            source = next(
                (
                    candidate for candidate in netlist
                    if str(candidate.get("spice_name") or "").lower() == expected_name
                ),
                None,
            )
            if source is None and supply_nodes:
                source = next(
                    (
                        candidate for candidate in netlist
                        if candidate.get("kind") == "voltage_source"
                        and {normalize_node(node) for node in candidate.get("nodes") or []} == supply_nodes
                    ),
                    None,
                )
            if source is None:
                continue

            source["viewer_hidden_by_terminal"] = component_id
            item["is_supply_terminal"] = True
            item["supply_name"] = str(supply_name)
            item["display_label"] = str(supply_name)
            item["display_value"] = compact_source_value(source.get("value"), str(parameters.get("unit") or "V"))
            for field in ("is_scenario_modified", "scenario_previous_value", "scenario_value"):
                if source.get(field) is not None:
                    item[field] = source[field]
            break
        enriched.append(item)

    return enriched, netlist


def build_nodes(node_map: dict[str, Any], measurements: dict[str, Any]) -> list[dict[str, Any]]:
    """Unisce i nodi del node map con le tensioni operative misurate."""
    voltages = measurements.get("node_voltages") or {}
    nodes: list[dict[str, Any]] = []
    for item in node_map.get("nodes") or []:
        if not isinstance(item, dict):
            continue
        node_id = normalize_node(str(item.get("node_id") or ""))
        if not node_id:
            continue
        lookup = node_id.lower().upper() if node_id != "0" else "0"
        nodes.append(
            {
                "id": node_id,
                "label": "GND" if node_id == "0" else node_id,
                "is_ground": node_id == "0",
                "voltage_op": voltages.get(lookup),
                "terminals": item.get("terminals") or [],
                "terminal_count": item.get("terminal_count"),
                "source_groups": item.get("source_groups") or [],
            }
        )
    return nodes


def infer_batch_id(run_dir: Path) -> str | None:
    """Ricava il batch dalla posizione della run dentro `outputs/pipeline2.0`."""
    parts = list(run_dir.resolve().parts)
    try:
        pipeline_index = parts.index("pipeline2.0")
    except ValueError:
        return None
    return parts[pipeline_index + 1] if pipeline_index + 1 < len(parts) else None


def normalize_bbox(value: Any) -> list[float] | None:
    """Valida una bbox nel formato `[x1, y1, x2, y2]`."""
    if not isinstance(value, list) or len(value) != 4:
        return None
    try:
        bbox = [float(item) for item in value]
    except (TypeError, ValueError):
        return None
    if bbox[2] <= bbox[0] or bbox[3] <= bbox[1]:
        return None
    return bbox


def index_estimated_components(terminal_estimates: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Indicizza le stime geometriche della Pipeline 1.0 per `instance_id`."""
    indexed: dict[str, dict[str, Any]] = {}
    for component in terminal_estimates.get("components") or []:
        if not isinstance(component, dict):
            continue
        instance_id = str(component.get("instance_id") or "")
        if instance_id:
            indexed[instance_id] = component
    return indexed


def index_estimated_terminals(estimated_component: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Indicizza i terminali usando sia il nome tecnico sia quello semantico."""
    indexed: dict[str, dict[str, Any]] = {}
    for terminal in estimated_component.get("terminals") or []:
        if not isinstance(terminal, dict):
            continue
        for field in ("name", "semantic_terminal_name", "display_name"):
            name = str(terminal.get(field) or "")
            if name:
                indexed[name] = terminal
    return indexed


def build_geometry_component(
    graph_component: dict[str, Any],
    estimated_component: dict[str, Any],
    terminal_nodes: dict[str, Any],
) -> dict[str, Any] | None:
    """Unisce bbox, terminali e nodi elettrici di un componente rilevato."""
    component_id = str(graph_component.get("component_id") or "")
    bbox = normalize_bbox(estimated_component.get("bbox"))
    if not component_id or bbox is None:
        return None

    estimated_terminals = index_estimated_terminals(estimated_component)
    component_node_map = terminal_nodes.get(component_id) or {}
    terminals: dict[str, dict[str, Any]] = {}

    # Il terminal graph fornisce gli id stabili; le stime forniscono le coordinate.
    for terminal in graph_component.get("terminals") or []:
        if not isinstance(terminal, dict):
            continue
        name = str(terminal.get("name") or "")
        estimate = estimated_terminals.get(name) or {}
        try:
            x = float(estimate.get("x"))
            y = float(estimate.get("y"))
        except (TypeError, ValueError):
            continue
        terminals[name] = {
            "id": str(terminal.get("terminal_id") or f"{component_id}_{name}"),
            "name": name,
            "relative_position": str(
                estimate.get("relative_position") or terminal.get("relative_position") or ""
            ),
            "x": x,
            "y": y,
            "node_id": normalize_node(str(component_node_map.get(name) or "")) or None,
        }

    return {
        "component_id": component_id,
        "instance_id": str(graph_component.get("instance_id") or ""),
        "class_name": str(graph_component.get("class_name") or estimated_component.get("class_name") or "Component"),
        "bbox": bbox,
        "center": {"x": (bbox[0] + bbox[2]) / 2, "y": (bbox[1] + bbox[3]) / 2},
        "estimated_orientation": str(estimated_component.get("estimated_orientation") or "unknown"),
        "terminals": terminals,
        "state": graph_component.get("state") or estimated_component.get("state"),
    }


def load_geometry_seed(run_dir: Path, circuit_id: str, node_map: dict[str, Any]) -> dict[str, Any]:
    """Carica la geometria Pipeline 1.0 usata come seme dal layout automatico."""
    batch_id = infer_batch_id(run_dir)
    if not batch_id or not circuit_id:
        return {"status": "missing", "reason": "batch_or_circuit_unknown", "components": {}}

    pipeline1_dir = PROJECT_ROOT / "outputs" / "pipeline1.0" / batch_id
    estimate_path = pipeline1_dir / "03_estimate_terminals" / f"{circuit_id}.json"
    graph_path = pipeline1_dir / "05_build_terminal_graph" / f"{circuit_id}.json"
    terminal_estimates = read_json(estimate_path)
    terminal_graph = read_json(graph_path)
    if not terminal_estimates or not terminal_graph:
        return {
            "status": "missing",
            "reason": "pipeline1_geometry_not_found",
            "source_files": {"terminal_estimates": str(estimate_path), "terminal_graph": str(graph_path)},
            "components": {},
        }

    estimates_by_instance = index_estimated_components(terminal_estimates)
    terminal_nodes = node_map.get("component_terminal_nodes") or {}
    components: dict[str, dict[str, Any]] = {}
    for graph_component in terminal_graph.get("components") or []:
        if not isinstance(graph_component, dict):
            continue
        instance_id = str(graph_component.get("instance_id") or "")
        geometry_component = build_geometry_component(
            graph_component,
            estimates_by_instance.get(instance_id) or {},
            terminal_nodes,
        )
        if geometry_component:
            components[geometry_component["component_id"]] = geometry_component

    return {
        "status": "loaded" if components else "empty",
        "source_files": {"terminal_estimates": str(estimate_path), "terminal_graph": str(graph_path)},
        "image": {
            "id": terminal_estimates.get("image_id") or circuit_id,
            "path": terminal_estimates.get("image_path"),
            "width": terminal_estimates.get("image_width"),
            "height": terminal_estimates.get("image_height"),
        },
        "components": components,
        "terminal_graph": terminal_graph.get("graph") or {},
    }


def detect_run_type(run_dir: Path) -> tuple[str, str | None, Path | None]:
    """Capisce se la cartella rappresenta una base run o una run scenario."""
    if run_dir.name == "run" and run_dir.parent.parent.name == "scenarios":
        return "scenario", run_dir.parent.name, run_dir.parent
    return "base", None, None


def build_viewer_model(run_dir: Path) -> dict[str, Any]:
    """Costruisce il contratto dati completo del viewer per una run."""
    run_dir = run_dir.resolve()
    run_type, scenario_id, scenario_dir = detect_run_type(run_dir)
    node_map = read_json(run_dir / "03_node_map.json")
    values_bound = read_json(run_dir / "04_values_bound.json")
    rules = read_json(run_dir / "06_component_rules.json")
    components, directives, warnings = parse_netlist(run_dir / NETLIST_NAME)
    components = enrich_components_with_rules(components, rules)
    measurements = parse_ngspice_stdout(run_dir / "08_ngspice_stdout.txt")
    transient = parse_transient_csv(run_dir / "08_tran.csv", components)
    scenario = read_json(scenario_dir / "scenario.json") if scenario_dir else None
    transient = attach_transient_scope_data(transient, scenario, scenario_dir, components)
    if scenario:
        components = apply_scenario_component_roles(components, scenario)
        components = mark_scenario_modified_components(components, scenario, scenario_dir)
    structural_components = build_structural_components(node_map, rules, measurements)
    # Un fusibile chiuso, o un altro equivalente semplificato, resta nella
    # netlist per la simulazione ma deve avere un solo simbolo nel viewer.
    structural_components = remove_emitted_simplified_duplicates(structural_components, components)
    structural_components, components = enrich_structural_terminals(
        structural_components,
        components,
        rules,
        values_bound,
    )
    if scenario:
        structural_components = apply_scenario_visual_overrides(structural_components, scenario, components)
    circuit_id = str(node_map.get("circuit_id") or rules.get("circuit_id") or "")
    geometry_seed = load_geometry_seed(run_dir, circuit_id, node_map)
    model = {
        "source_format": "pipeline2.0_viewer_model",
        "schema_version": VIEWER_MODEL_SCHEMA_VERSION,
        "metadata": {
            "circuit_id": circuit_id,
            "run_type": run_type,
            "scenario_id": scenario_id,
            "run_dir": str(run_dir),
            "source_netlist_path": str(run_dir / NETLIST_NAME),
            "generated_at": datetime.now().isoformat(timespec="seconds"),
        },
        "nodes": build_nodes(node_map, measurements),
        "netlist_components": components,
        "structural_components": structural_components,
        "directives": directives,
        "measurements": measurements,
        "transient": transient,
        "geometry_seed": geometry_seed,
        "scenario": scenario,
        "warnings": warnings,
    }
    return model


def write_viewer_model(run_dir: Path) -> dict[str, Any]:
    """Genera e salva `13_viewer_model.json` nella cartella della run."""
    model = build_viewer_model(run_dir)
    write_json(run_dir / VIEWER_MODEL_NAME, model)
    return model

