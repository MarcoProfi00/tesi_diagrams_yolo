"""
Costruisce il modello dati del viewer per una run della Pipeline 2.0.

Il modello resta intenzionalmente guidato dalla netlist: `07_netlist.cir`
descrive il circuito che ngspice ha realmente simulato, mentre
`03_node_map.json` e `06_component_rules.json` aggiungono il contesto
strutturale utile al viewer, come connector, masse e switch aperti non emessi
in SPICE.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import json
import re
from pathlib import Path
from typing import Any


NETLIST_NAME = "07_netlist.cir"
VIEWER_MODEL_NAME = "13_viewer_model.json"


def read_json(path: Path) -> dict[str, Any]:
    """Legge un file JSON e restituisce un dizionario vuoto se non e' valido."""
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def write_json(path: Path, data: dict[str, Any]) -> None:
    """Scrive un dizionario JSON in modo leggibile e stabile."""
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


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
    if prefix not in {"R", "C", "L", "D", "Q"}:
        return None
    base = spice_name[1:]
    match = re.match(r"(.+)_([0-9]+)$", base)
    if not match:
        return None
    return f"{match.group(1).lower()}.{match.group(2)}"


def parse_netlist(netlist_path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    """Estrae componenti, direttive e warning dal file `07_netlist.cir`."""
    components: list[dict[str, Any]] = []
    directives: list[dict[str, Any]] = []
    warnings: list[str] = []

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


def build_structural_components(node_map: dict[str, Any], rules: dict[str, Any]) -> list[dict[str, Any]]:
    """Costruisce i componenti visivi che non compaiono nella netlist SPICE."""
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
        if status != "not_emitted" and support != "structural" and emit_as is not None:
            continue
        structural.append(
            {
                "id": component_id,
                "class_name": class_name,
                "nodes": terminal_nodes.get(component_id) or rule.get("nodes") or {},
                "status": status,
                "spice_support": support,
                "parameters": rule.get("parameters") or {},
                "strategy": rule.get("strategy"),
                "reason": rule.get("reason"),
            }
        )

    return structural


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
            }
        )
    return nodes


def infer_a01_layout(node_map: dict[str, Any], components: list[dict[str, Any]]) -> dict[str, Any]:
    """Produce il layout provvisorio del circuito pilota `a01`.

    Questo blocco e' temporaneo: serve a mantenere usabile il viewer attuale
    finche' lo step 14 non generera' un layout automatico generale.
    """
    component_nodes = node_map.get("component_terminal_nodes") or {}
    if "connector5.1" not in component_nodes:
        return {"layout_status": "generic_pending", "node_positions": {}, "component_positions": {}}

    component_positions = {
        "connector5.1": {"x": 130, "y": 150, "orientation": "vertical"},
        "VVCC": {"x": 130, "y": 55, "orientation": "vertical"},
        "Rresistor22_2": {"x": 335, "y": 92, "orientation": "horizontal"},
        "Dled12_1": {"x": 575, "y": 92, "orientation": "horizontal"},
        "Rresistor22_1": {"x": 335, "y": 190, "orientation": "horizontal"},
        "Rlamp13_1": {"x": 575, "y": 190, "orientation": "horizontal"},
        "switch25.1": {"x": 45, "y": 285, "orientation": "horizontal"},
        "gnd9.1": {"x": 40, "y": 355, "orientation": "ground"},
        "gnd9.2": {"x": 130, "y": 370, "orientation": "ground"},
        "gnd9.3": {"x": 760, "y": 285, "orientation": "ground"},
    }
    node_positions = {
        "N001": {"x": 170, "y": 92},
        "N002": {"x": 170, "y": 190},
        "N003": {"x": 130, "y": 285},
        "N004": {"x": 475, "y": 190},
        "N005": {"x": 475, "y": 92},
        "0": {"x": 760, "y": 285},
    }
    for component in components:
        if component.get("is_scenario_added") and component.get("id") not in component_positions:
            component_positions[str(component.get("id"))] = {"x": 255, "y": 135, "orientation": "horizontal"}
    return {
        "layout_status": "a01_seeded",
        "width": 860,
        "height": 430,
        "node_positions": node_positions,
        "component_positions": component_positions,
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
    rules = read_json(run_dir / "06_component_rules.json")
    components, directives, warnings = parse_netlist(run_dir / NETLIST_NAME)
    measurements = parse_ngspice_stdout(run_dir / "08_ngspice_stdout.txt")
    scenario = read_json(scenario_dir / "scenario.json") if scenario_dir else None
    structural_components = build_structural_components(node_map, rules)
    if scenario:
        structural_components = apply_scenario_visual_overrides(structural_components, scenario, components)
    model = {
        "source_format": "pipeline2.0_viewer_model",
        "schema_version": 1,
        "metadata": {
            "circuit_id": node_map.get("circuit_id") or rules.get("circuit_id"),
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
        "layout": infer_a01_layout(node_map, components),
        "scenario": scenario,
        "warnings": warnings,
    }
    return model


def write_viewer_model(run_dir: Path) -> dict[str, Any]:
    """Genera e salva `13_viewer_model.json` nella cartella della run."""
    model = build_viewer_model(run_dir)
    write_json(run_dir / VIEWER_MODEL_NAME, model)
    return model


def main() -> None:
    """Gestisce l'esecuzione da riga di comando dello step 13."""
    parser = argparse.ArgumentParser(description="Genera il viewer model Pipeline 2.0 per una cartella run.")
    parser.add_argument("--run-dir", required=True, help="Cartella run che contiene 07_netlist.cir.")
    args = parser.parse_args()
    model = write_viewer_model(Path(args.run_dir))
    print(f"Scritto {Path(args.run_dir) / VIEWER_MODEL_NAME}")
    print(f"Componenti: {len(model.get('netlist_components') or [])}")


if __name__ == "__main__":
    main()
