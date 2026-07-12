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
import math
from pathlib import Path
from typing import Any

from viewer_component_library import component_spec, normalize_component_type


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
    if component.get("viewer_label") is not None:
        return str(component.get("viewer_label") or "")
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
    if component.get("viewer_kind"):
        return str(component["viewer_kind"])
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
    geometry_component_ids = set(((model.get("geometry_seed") or {}).get("components") or {}).keys())
    structural_ids = {
        str(component.get("id") or "")
        for component in model.get("structural_components") or []
        if isinstance(component, dict)
    }
    connector_nodes = {
        str(node_id)
        for component in model.get("structural_components") or []
        if isinstance(component, dict) and "connector" in str(component.get("class_name") or "").lower()
        for node_id in component_nodes(component)
    }
    for source, is_structural in (
        (model.get("netlist_components") or [], False),
        (model.get("structural_components") or [], True),
    ):
        for component in source:
            if not isinstance(component, dict):
                continue
            source_id = str(component.get("source_component_id") or "")
            represented_structural_id = source_id.removeprefix("scenario_")
            if component.get("is_scenario_added") and represented_structural_id in structural_ids:
                # Lo switch strutturale rappresenta gia' il resistore SPICE usato per chiuderlo.
                continue
            component_node_ids = set(component_nodes(component))
            is_external_connector_source = (
                component.get("kind") == "voltage_source"
                and not component.get("is_scenario_added")
                and source_id not in geometry_component_ids
                and "0" in component_node_ids
                and bool(component_node_ids & connector_nodes)
            )
            if is_external_connector_source:
                # La sorgente sintetica e' gia' rappresentata dall'alimentazione esterna del connector.
                continue
            item = dict(component)
            item["layout_kind"] = classify_component(component)
            item["is_structural"] = is_structural
            item["label"] = component_label(item)
            item["nodes"] = component_nodes(component)
            items.append(item)
    return items


def canvas_transform(geometry_seed: dict[str, Any]) -> dict[str, float]:
    """Calcola la trasformazione uniforme dall'immagine al canvas del viewer."""
    image = geometry_seed.get("image") or {}
    width = max(float(image.get("width") or 1), 1.0)
    height = max(float(image.get("height") or 1), 1.0)
    canvas_width = 1040.0
    canvas_height = 620.0
    margin = 48.0
    scale = min((canvas_width - 2 * margin) / width, (canvas_height - 2 * margin) / height)
    offset_x = (canvas_width - width * scale) / 2
    offset_y = (canvas_height - height * scale) / 2
    return {
        "scale": scale,
        "offset_x": offset_x,
        "offset_y": offset_y,
        "canvas_width": canvas_width,
        "canvas_height": canvas_height,
    }


def transform_point(x: Any, y: Any, transform: dict[str, float]) -> dict[str, float]:
    """Converte una coordinata immagine nella coordinata equivalente del canvas."""
    return {
        "x": round(transform["offset_x"] + float(x) * transform["scale"], 2),
        "y": round(transform["offset_y"] + float(y) * transform["scale"], 2),
    }


def visual_source_id(component: dict[str, Any]) -> str:
    """Restituisce l'id Pipeline 1.0 associato a un componente del modello."""
    return str(component.get("source_component_id") or component.get("id") or "")


def normalize_orientation(value: Any) -> str:
    """Riduce le orientazioni della Pipeline 1.0 alle varianti del renderer."""
    orientation = str(value or "").lower()
    if orientation in {"vertical", "up", "down"}:
        return "vertical"
    return "horizontal"


def match_geometry_terminals(
    component: dict[str, Any],
    geometry_component: dict[str, Any],
    transform: dict[str, float],
) -> list[dict[str, Any]]:
    """Associa i nodi del modello ai terminali geometrici dello stesso componente."""
    geometry_terminals = geometry_component.get("terminals") or {}
    matched: list[dict[str, Any]] = []
    used_names: set[str] = set()

    # La corrispondenza per nodo evita di dipendere dai nomi t1, anode o pin1.
    for index, node_id in enumerate(component.get("nodes") or [], start=1):
        selected_name = ""
        selected: dict[str, Any] = {}
        for name, terminal in geometry_terminals.items():
            if name not in used_names and str(terminal.get("node_id") or "") == str(node_id):
                selected_name = str(name)
                selected = terminal
                break
        if not selected:
            remaining = [(name, item) for name, item in geometry_terminals.items() if name not in used_names]
            if remaining:
                selected_name, selected = remaining[0]
        if not selected:
            continue
        used_names.add(selected_name)
        point = transform_point(selected.get("x"), selected.get("y"), transform)
        matched.append(
            {
                "name": selected_name or f"t{index}",
                "terminal_id": str(selected.get("id") or ""),
                "node_id": str(node_id),
                "relative_position": str(selected.get("relative_position") or ""),
                **point,
            }
        )
    return matched


def standardize_terminals(
    terminals: list[dict[str, Any]],
    center: dict[str, float],
    component_type: str,
    orientation: str,
) -> list[dict[str, Any]]:
    """Porta i terminali sui punti di attacco standard del simbolo visuale."""
    if not terminals:
        return []
    spec = component_spec(component_type, component_type, len(terminals))
    center_x, center_y = float(center["x"]), float(center["y"])
    standardized = [dict(terminal) for terminal in terminals]

    if component_type == "connector":
        # Tutti i connector usano pin centrati, equidistanti e indipendenti dalla bbox.
        ordered = sorted(standardized, key=lambda item: float(item.get("y") or 0))
        spacing = spec["pin_spacing"]
        start_y = center_y - spacing * (len(ordered) - 1) / 2
        for index, terminal in enumerate(ordered):
            terminal["x"] = center_x
            terminal["y"] = start_y + index * spacing
            terminal["pin_number"] = index + 1
        return ordered

    if component_type == "ground":
        standardized[0]["x"] = center_x
        standardized[0]["y"] = center_y - spec["height"] / 2
        return standardized[:1]

    if len(standardized) == 2:
        # I bipoli usano sempre la stessa lunghezza e rispettano l'ordine rilevato.
        ordered = sorted(
            standardized,
            key=lambda item: float(item.get("y") or 0) if orientation == "vertical" else float(item.get("x") or 0),
        )
        if orientation == "vertical":
            # Il simbolo viene ruotato dal renderer: la lunghezza elettrica resta `width`.
            ordered[0].update({"x": center_x, "y": center_y - spec["width"] / 2})
            ordered[1].update({"x": center_x, "y": center_y + spec["width"] / 2})
        else:
            ordered[0].update({"x": center_x - spec["width"] / 2, "y": center_y})
            ordered[1].update({"x": center_x + spec["width"] / 2, "y": center_y})
        return ordered

    # I componenti multi-terminale mantengono il lato relativo attorno a un ingombro standard.
    for terminal in standardized:
        raw_x = float(terminal.get("x") or center_x)
        raw_y = float(terminal.get("y") or center_y)
        angle = math.atan2(raw_y - center_y, raw_x - center_x)
        terminal["x"] = center_x + math.cos(angle) * spec["width"] / 2
        terminal["y"] = center_y + math.sin(angle) * spec["height"] / 2
    return standardized


def move_component_to_lane(component: dict[str, Any], lane_y: float) -> None:
    """Sposta un componente orizzontale e tutti i suoi terminali sulla corsia indicata."""
    delta_y = lane_y - float(component.get("y") or lane_y)
    component["y"] = lane_y
    for terminal in component.get("terminals") or []:
        terminal["y"] = float(terminal.get("y") or 0) + delta_y


def align_horizontal_branches(positioned: dict[str, dict[str, Any]]) -> None:
    """Propaga le quote dei pin connector lungo i rami di bipoli orizzontali."""
    node_lanes: dict[str, float] = {}
    for component in positioned.values():
        if component.get("component_type") != "connector":
            continue
        for terminal in component.get("terminals") or []:
            node_id = str(terminal.get("node_id") or "")
            if node_id and node_id != "0":
                node_lanes[node_id] = float(terminal["y"])

    # Ogni passaggio estende la corsia oltre un componente appena allineato.
    aligned: set[str] = set()
    for _ in range(max(len(positioned), 1)):
        changed = False
        for component_id, component in positioned.items():
            if component_id in aligned or component.get("orientation") != "horizontal":
                continue
            terminals = component.get("terminals") or []
            if len(terminals) != 2:
                continue
            known_lanes = [node_lanes[str(item.get("node_id"))] for item in terminals if str(item.get("node_id")) in node_lanes]
            if not known_lanes:
                continue
            lane_y = sum(known_lanes) / len(known_lanes)
            move_component_to_lane(component, lane_y)
            for terminal in terminals:
                node_id = str(terminal.get("node_id") or "")
                if node_id and node_id != "0":
                    node_lanes.setdefault(node_id, lane_y)
            aligned.add(component_id)
            changed = True
        if not changed:
            break


def build_image_guided_components(
    components: list[dict[str, Any]],
    geometry_seed: dict[str, Any],
    transform: dict[str, float],
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """Posiziona i componenti usando bbox e terminali della Pipeline 1.0."""
    geometry_components = geometry_seed.get("components") or {}
    positioned: dict[str, dict[str, Any]] = {}
    warnings: list[str] = []
    pending: list[dict[str, Any]] = []

    for component in components:
        component_id = str(component.get("id") or "")
        source_id = visual_source_id(component)
        geometry_component = geometry_components.get(source_id)
        if not component_id:
            continue
        if not geometry_component:
            pending.append(component)
            continue
        center = geometry_component.get("center") or {}
        position = transform_point(center.get("x"), center.get("y"), transform)
        orientation = normalize_orientation(geometry_component.get("estimated_orientation"))
        visual_class_name = str(geometry_component.get("class_name") or component.get("layout_kind") or "structural")
        component_type = normalize_component_type(visual_class_name, component.get("layout_kind"))
        raw_terminals = match_geometry_terminals(component, geometry_component, transform)
        terminals = standardize_terminals(raw_terminals, position, component_type, orientation)
        spec = component_spec(component_type, component.get("layout_kind"), len(terminals))
        positioned[component_id] = {
            **position,
            "source_component_id": source_id,
            "layout_kind": component.get("layout_kind"),
            "visual_class_name": visual_class_name,
            "component_type": component_type,
            "symbol_size": {"width": spec["width"], "height": spec["height"]},
            "label": component.get("label"),
            "orientation": orientation,
            "terminals": terminals,
            "state": (component.get("parameters") or {}).get("state") or geometry_component.get("state"),
            "is_structural": bool(component.get("is_structural")),
        }

    align_horizontal_branches(positioned)

    # I terminali gia' posizionati permettono di stimare il centro visuale di ogni nodo.
    node_seed_points: dict[str, list[tuple[float, float]]] = {}
    for positioned_component in positioned.values():
        for terminal in positioned_component.get("terminals") or []:
            node_id = str(terminal.get("node_id") or "")
            if node_id:
                node_seed_points.setdefault(node_id, []).append((float(terminal["x"]), float(terminal["y"])))
    node_centers = {
        node_id: (
            sum(point[0] for point in points) / len(points),
            sum(point[1] for point in points) / len(points),
        )
        for node_id, points in node_seed_points.items()
        if points
    }

    # I componenti aggiunti dagli scenari non hanno bbox: vengono inseriti tra i nodi coinvolti.
    for index, component in enumerate(pending):
        component_id = str(component.get("id") or "")
        component_node_ids = [str(node_id) for node_id in component.get("nodes") or []]
        component_type = normalize_component_type(
            component.get("viewer_kind") or component.get("class_name") or component.get("kind"),
            component.get("layout_kind"),
        )
        first_point = node_centers.get(component_node_ids[0]) if component_node_ids else None
        second_point = node_centers.get(component_node_ids[1]) if len(component_node_ids) > 1 else None
        terminals: list[dict[str, Any]] = []
        connector_bridge: dict[str, Any] | None = None
        if component_type == "connection" and len(component_node_ids) == 2:
            for positioned_component in positioned.values():
                if positioned_component.get("component_type") != "connector":
                    continue
                connector_terminals = {
                    str(terminal.get("node_id") or ""): terminal
                    for terminal in positioned_component.get("terminals") or []
                }
                if all(node_id in connector_terminals for node_id in component_node_ids):
                    connector_bridge = {
                        "component": positioned_component,
                        "terminals": connector_terminals,
                    }
                    break

        if connector_bridge:
            # Un link tra pin dello stesso connector resta compatto e aderente al suo bordo.
            connector = connector_bridge["component"]
            connector_spec = component_spec("connector", "connector", len(connector.get("terminals") or []))
            x = float(connector.get("x") or 0) + connector_spec["width"] / 2 + 12.0
            first_y = float(connector_bridge["terminals"][component_node_ids[0]]["y"])
            second_y = float(connector_bridge["terminals"][component_node_ids[1]]["y"])
            y = (first_y + second_y) / 2
            terminals = [
                {"name": "t1", "node_id": component_node_ids[0], "x": x, "y": first_y},
                {"name": "t2", "node_id": component_node_ids[1], "x": x, "y": second_y},
            ]
        elif first_point and second_point:
            dx = second_point[0] - first_point[0]
            dy = second_point[1] - first_point[1]
            distance = max((dx * dx + dy * dy) ** 0.5, 1.0)
            normal_x, normal_y = -dy / distance, dx / distance
            offset = 34.0 + (index % 3) * 22.0
            x = (first_point[0] + second_point[0]) / 2 + normal_x * offset
            y = (first_point[1] + second_point[1]) / 2 + normal_y * offset
            direction_x, direction_y = dx / distance, dy / distance
            terminals = [
                {"name": "t1", "node_id": component_node_ids[0], "x": x - direction_x * 34, "y": y - direction_y * 34},
                {"name": "t2", "node_id": component_node_ids[1], "x": x + direction_x * 34, "y": y + direction_y * 34},
            ]
        else:
            x = 520.0 + (index % 3 - 1) * 120.0
            y = 310.0 + (index // 3) * 70.0
        positioned[component_id] = {
            "x": x,
            "y": y,
            "source_component_id": visual_source_id(component),
            "layout_kind": component.get("layout_kind"),
            "visual_class_name": component.get("class_name") or component.get("kind"),
            "component_type": component_type,
            "label": component.get("label"),
            "orientation": "horizontal",
            "terminals": terminals,
            "state": (component.get("parameters") or {}).get("state"),
            "is_structural": bool(component.get("is_structural")),
            "placement": "scenario_or_fallback",
        }
        warnings.append(f"Geometria assente per {component_id}: applicato posizionamento tra nodi.")
    return positioned, warnings


def collect_node_points(positioned: dict[str, dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Raggruppa per nodo tutti i terminali geometrici disponibili."""
    node_points: dict[str, list[dict[str, Any]]] = {}
    for component_id, component in positioned.items():
        for terminal in component.get("terminals") or []:
            node_id = str(terminal.get("node_id") or "")
            if not node_id:
                continue
            node_points.setdefault(node_id, []).append(
                {
                    "component_id": component_id,
                    "terminal": terminal.get("name"),
                    "terminal_id": terminal.get("terminal_id"),
                    "x": terminal.get("x"),
                    "y": terminal.get("y"),
                    "is_structural": component.get("is_structural"),
                    "component_type": component.get("component_type"),
                    "orientation": component.get("orientation"),
                }
            )
    return node_points


def build_node_positions(model: dict[str, Any], node_points: dict[str, list[dict[str, Any]]]) -> dict[str, dict[str, Any]]:
    """Calcola il punto di giunzione visuale di ogni nodo dalla media dei terminali."""
    positions: dict[str, dict[str, Any]] = {}
    for node in model.get("nodes") or []:
        if not isinstance(node, dict):
            continue
        node_id = str(node.get("id") or "")
        points = node_points.get(node_id) or []
        if not points:
            continue
        positions[node_id] = {
            "x": round(sum(float(point["x"]) for point in points) / len(points), 2),
            "y": round(sum(float(point["y"]) for point in points) / len(points), 2),
            "terminal_count": len(points),
        }
    return positions


def connect_point_group(node_id: str, points: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collega un gruppo fisico di terminali scegliendo il primo come riferimento."""
    if len(points) < 2:
        return []
    # Il pin del connector e' la giunzione visuale piu' stabile per i rami esterni.
    anchor = next(
        (point for point in points if str(point.get("component_id") or "").lower().startswith("connector")),
        points[0],
    )
    return [
        {
            "node_id": node_id,
            "from": anchor,
            "to": target,
            "kind": "structural" if anchor.get("is_structural") and target.get("is_structural") else "electrical",
        }
        for target in points
        if target is not anchor
    ]


def build_node_connections(
    node_points: dict[str, list[dict[str, Any]]],
    model: dict[str, Any],
) -> list[dict[str, Any]]:
    """Crea collegamenti terminale-terminale per ciascun nodo elettrico."""
    connections: list[dict[str, Any]] = []
    source_groups_by_node = {
        str(node.get("id") or ""): node.get("source_groups") or []
        for node in model.get("nodes") or []
        if isinstance(node, dict)
    }
    for node_id, points in node_points.items():
        source_groups = source_groups_by_node.get(node_id) or []
        if node_id != "0" or not source_groups:
            connections.extend(connect_point_group(node_id, points))
            continue

        # Le masse SPICE coincidono elettricamente, ma restano gruppi grafici separati.
        points_by_terminal = {str(point.get("terminal_id") or ""): point for point in points}
        grouped_terminal_ids: set[str] = set()
        for source_group in source_groups:
            group_points = [points_by_terminal[terminal_id] for terminal_id in source_group if terminal_id in points_by_terminal]
            grouped_terminal_ids.update(str(terminal_id) for terminal_id in source_group)
            connections.extend(connect_point_group(node_id, group_points))

        # Terminali scenario non presenti nella base vengono collegati alla massa visuale piu' vicina.
        ground_points = [point for point in points if str(point.get("component_id") or "").lower().startswith("gnd")]
        for point in points:
            if str(point.get("terminal_id") or "") in grouped_terminal_ids or not ground_points:
                continue
            nearest_ground = min(
                ground_points,
                key=lambda ground: (float(ground["x"]) - float(point["x"])) ** 2 + (float(ground["y"]) - float(point["y"])) ** 2,
            )
            if nearest_ground is not point:
                connections.extend(connect_point_group(node_id, [point, nearest_ground]))
    return connections


def build_viewer_layout(run_dir: Path) -> dict[str, Any]:
    """Costruisce il layout visuale a partire da `13_viewer_model.json`."""
    run_dir = run_dir.resolve()
    model = read_json(run_dir / VIEWER_MODEL_NAME)
    components = collect_layout_components(model)
    geometry_seed = model.get("geometry_seed") or {}
    transform = canvas_transform(geometry_seed)
    component_positions, warnings = build_image_guided_components(components, geometry_seed, transform)
    node_points = collect_node_points(component_positions)
    node_positions = build_node_positions(model, node_points)
    layout_status = "image_guided" if geometry_seed.get("status") == "loaded" else "fallback"
    return {
        "source_format": "pipeline2.0_viewer_layout",
        "schema_version": 2,
        "metadata": {
            "run_dir": str(run_dir),
            "source_model_path": str(run_dir / VIEWER_MODEL_NAME),
            "generated_at": datetime.now().isoformat(timespec="seconds"),
        },
        "layout_status": layout_status,
        "canvas": {"width": 1040, "height": 620, "grid": 40},
        "transform": transform,
        "components": component_positions,
        "nodes": node_positions,
        "connections": build_node_connections(node_points, model),
        "warnings": warnings if model else [f"Viewer model mancante: {run_dir / VIEWER_MODEL_NAME}"],
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
