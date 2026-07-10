"""
Genera un layout visuale semplice per il viewer della Pipeline 2.0.

Lo step 14 legge `13_viewer_model.json` e produce `14_viewer_layout.json`.
Il suo compito non e' ricostruire l'immagine originale, ma calcolare posizioni
leggibili per componenti, nodi e rami a partire dal modello netlist-first.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
from typing import Any


VIEWER_MODEL_NAME = "13_viewer_model.json"
VIEWER_LAYOUT_NAME = "14_viewer_layout.json"


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


def component_label(component: dict[str, Any]) -> str:
    """Restituisce una label compatta per un componente del viewer."""
    kind = str(component.get("kind") or component.get("class_name") or "").lower()
    value = str(component.get("value") or "")
    if kind == "resistor":
        return value or "R"
    if kind == "diode":
        return str(component.get("spice_name") or component.get("id") or "D")
    if kind == "voltage_source":
        return value or "V"
    if "switch" in kind:
        return "SW"
    if "connector" in kind:
        return str(component.get("id") or "J")
    return str(component.get("id") or kind or "component")


def component_nodes(component: dict[str, Any]) -> list[str]:
    """Estrae i nodi di un componente, gestendo sia liste sia mappe terminale-nodo."""
    nodes = component.get("nodes") or []
    if isinstance(nodes, dict):
        return [str(value) for value in nodes.values()]
    if isinstance(nodes, list):
        return [str(value) for value in nodes]
    return []


def classify_component(component: dict[str, Any]) -> str:
    """Classifica il componente in una categoria grafica semplice."""
    kind = str(component.get("kind") or component.get("class_name") or "").lower()
    component_id = str(component.get("id") or "").lower()
    if "connector" in kind or "connector" in component_id:
        return "connector"
    if "switch" in kind or "switch" in component_id:
        return "switch"
    if component_id.startswith("gnd") or "ground" in kind:
        return "ground"
    if kind in {"resistor", "diode", "voltage_source", "current_source", "capacitor", "inductor"}:
        return kind
    return "structural"


def collect_layout_components(model: dict[str, Any]) -> list[dict[str, Any]]:
    """Unisce componenti SPICE e strutturali in una lista adatta al layout."""
    items: list[dict[str, Any]] = []
    for source, is_structural in (
        (model.get("netlist_components") or [], False),
        (model.get("structural_components") or [], True),
    ):
        for component in source:
            if not isinstance(component, dict):
                continue
            item = dict(component)
            item["layout_kind"] = classify_component(component)
            item["is_structural"] = is_structural
            item["label"] = component_label(item)
            item["nodes"] = component_nodes(component)
            items.append(item)
    return items


def choose_anchor_nodes(model: dict[str, Any]) -> dict[str, str]:
    """Sceglie nodi speciali usati dal layout come riferimento."""
    node_ids = [str(node.get("id")) for node in model.get("nodes") or [] if isinstance(node, dict)]
    positive = next((node_id for node_id in node_ids if node_id != "0"), "")
    return {"ground": "0", "left_supply": positive}


def component_sort_key(component: dict[str, Any], anchors: dict[str, str]) -> tuple[int, str]:
    """Ordina i componenti in modo stabile da sinistra a destra."""
    kind = str(component.get("layout_kind") or "")
    nodes = set(component.get("nodes") or [])
    if kind == "connector":
        return (0, str(component.get("id") or ""))
    if kind == "voltage_source":
        return (1, str(component.get("id") or ""))
    if anchors.get("left_supply") in nodes:
        return (2, str(component.get("id") or ""))
    if anchors.get("ground") in nodes:
        return (4, str(component.get("id") or ""))
    if kind in {"switch", "ground"}:
        return (5, str(component.get("id") or ""))
    return (3, str(component.get("id") or ""))


def assign_component_positions(components: list[dict[str, Any]], anchors: dict[str, str]) -> dict[str, dict[str, Any]]:
    """Assegna una posizione iniziale ai componenti usando colonne e righe regolari."""
    positions: dict[str, dict[str, Any]] = {}
    sorted_components = sorted(components, key=lambda item: component_sort_key(item, anchors))
    row_y = 105
    row_step = 82
    columns = {
        "connector": 110,
        "voltage_source": 150,
        "switch": 90,
        "ground": 760,
        "default": 300,
    }
    branch_index = 0

    for component in sorted_components:
        component_id = str(component.get("id") or "")
        if not component_id:
            continue
        kind = str(component.get("layout_kind") or "default")
        if kind == "connector":
            positions[component_id] = {"x": columns["connector"], "y": 90, "orientation": "vertical"}
            continue
        if kind == "ground":
            positions[component_id] = {"x": columns["ground"], "y": 285 + len(positions) % 3 * 28, "orientation": "ground"}
            continue
        if kind == "switch":
            positions[component_id] = {"x": columns["switch"], "y": 285, "orientation": "horizontal"}
            continue

        x = columns.get(kind, columns["default"]) + (branch_index % 3) * 185
        y = row_y + (branch_index // 3) * row_step
        positions[component_id] = {"x": x, "y": y, "orientation": "horizontal"}
        branch_index += 1

    return positions


def assign_node_positions(model: dict[str, Any], component_positions: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Assegna una posizione ai nodi usando la media dei componenti collegati."""
    node_points: dict[str, list[tuple[float, float]]] = {}
    all_components = collect_layout_components(model)
    for component in all_components:
        position = component_positions.get(str(component.get("id") or ""))
        if not position:
            continue
        for node_id in component.get("nodes") or []:
            node_points.setdefault(str(node_id), []).append((float(position["x"]), float(position["y"])))

    node_positions: dict[str, dict[str, Any]] = {}
    for node in model.get("nodes") or []:
        if not isinstance(node, dict):
            continue
        node_id = str(node.get("id") or "")
        points = node_points.get(node_id) or []
        if not points:
            node_positions[node_id] = {"x": 80, "y": 360 if node_id == "0" else 80}
            continue
        avg_x = sum(point[0] for point in points) / len(points)
        avg_y = sum(point[1] for point in points) / len(points)
        node_positions[node_id] = {"x": round(avg_x), "y": round(avg_y)}
    return node_positions


def build_connections(components: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Costruisce una lista semplice di rami componente-nodo da disegnare."""
    connections: list[dict[str, Any]] = []
    for component in components:
        component_id = str(component.get("id") or "")
        for index, node_id in enumerate(component.get("nodes") or [], start=1):
            connections.append(
                {
                    "component_id": component_id,
                    "terminal": f"t{index}",
                    "node_id": str(node_id),
                    "kind": "structural" if component.get("is_structural") else "electrical",
                }
            )
    return connections


def build_viewer_layout(run_dir: Path) -> dict[str, Any]:
    """Costruisce il layout visuale a partire da `13_viewer_model.json`."""
    run_dir = run_dir.resolve()
    model = read_json(run_dir / VIEWER_MODEL_NAME)
    components = collect_layout_components(model)
    anchors = choose_anchor_nodes(model)
    component_positions = assign_component_positions(components, anchors)
    node_positions = assign_node_positions(model, component_positions)
    return {
        "source_format": "pipeline2.0_viewer_layout",
        "schema_version": 1,
        "metadata": {
            "run_dir": str(run_dir),
            "source_model_path": str(run_dir / VIEWER_MODEL_NAME),
            "generated_at": datetime.now().isoformat(timespec="seconds"),
        },
        "layout_status": "rough_auto",
        "canvas": {"width": 1040, "height": 430, "grid": 40},
        "anchors": anchors,
        "components": component_positions,
        "nodes": node_positions,
        "connections": build_connections(components),
        "warnings": [] if model else [f"Viewer model mancante: {run_dir / VIEWER_MODEL_NAME}"],
    }


def write_viewer_layout(run_dir: Path) -> dict[str, Any]:
    """Genera e salva `14_viewer_layout.json` nella cartella della run."""
    layout = build_viewer_layout(run_dir)
    write_json(run_dir / VIEWER_LAYOUT_NAME, layout)
    return layout


def main() -> None:
    """Gestisce l'esecuzione da riga di comando dello step 14."""
    parser = argparse.ArgumentParser(description="Genera il layout viewer Pipeline 2.0 per una cartella run.")
    parser.add_argument("--run-dir", required=True, help="Cartella run che contiene 13_viewer_model.json.")
    args = parser.parse_args()
    layout = write_viewer_layout(Path(args.run_dir))
    print(f"Scritto {Path(args.run_dir) / VIEWER_LAYOUT_NAME}")
    print(f"Componenti posizionati: {len(layout.get('components') or {})}")


if __name__ == "__main__":
    main()
