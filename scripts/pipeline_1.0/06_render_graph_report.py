"""
Passo 06: rendering del report HTML/PNG del grafo.

Legge i JSON finali prodotti dal passo 05, genera una vista completa e una
vista compatta del grafo, copia gli artefatti utili nel report e costruisce
un indice batch navigabile.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from collections import defaultdict, deque
from html import escape
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PIPELINE_DATASET = os.environ.get(
    "PIPELINE_DATASET",
    "pipeline1.0/batchA_07_09",
)

DEFAULT_INPUT_DIR = PROJECT_ROOT / "outputs" / DEFAULT_PIPELINE_DATASET / "05_build_terminal_graph"
DEFAULT_DETECT_DIR = PROJECT_ROOT / "outputs" / DEFAULT_PIPELINE_DATASET / "01_detect_components"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "outputs" / DEFAULT_PIPELINE_DATASET / "06_graph_report"

LAYER_X = {
    "root": 90,
    "class": 270,
    "component": 500,
    "terminal": 780,
    "net": 1080,
}

NODE_STYLE = {
    "root": {"fill": "#f26a63", "stroke": "#d4534c", "radius": 36, "font_size": 14},
    "class": {"fill": "#dcc9a5", "stroke": "#bea77d", "radius": 32, "font_size": 11},
    "component": {"fill": "#85d68d", "stroke": "#57b766", "radius": 40, "font_size": 10},
    "terminal": {"fill": "#f4abc7", "stroke": "#d57ca0", "radius": 23, "font_size": 9},
    "net": {"fill": "#ffd65a", "stroke": "#d3a61d", "radius": 12, "font_size": 8},
    "warning_terminal": {"fill": "#ffd0d0", "stroke": "#d12f2f", "radius": 25, "font_size": 9},
}

EDGE_PALETTE = [
    "#7fb3d5",
    "#d98880",
    "#82e0aa",
    "#f8c471",
    "#c39bd3",
    "#76d7c4",
    "#f1948a",
    "#85c1e9",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render batch reports and simple graph visualizations from step 05 JSON files."
    )
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--detect-dir", type=Path, default=DEFAULT_DETECT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def prettify_name(value: str) -> str:
    return value.replace("_", " ")


def short_component_label(component: dict) -> str:
    if component.get("class_name") == "Integrated_Circuit":
        for key in ("ic_marking", "display_name", "component_subtype"):
            value = component.get(key)
            if value not in (None, ""):
                return str(value)
    return str(component.get("component_id") or component.get("instance_id") or "")


def short_terminal_label(terminal: dict, metadata: dict | None) -> str:
    if metadata:
        if metadata.get("pin_label") not in (None, ""):
            return str(metadata["pin_label"])[:10]
        if metadata.get("pin_number") not in (None, ""):
            return f"pin{metadata['pin_number']}"
        if metadata.get("display_name") not in (None, ""):
            display_name = str(metadata["display_name"])
            if len(display_name) <= 10:
                return display_name
    return str(terminal.get("name") or terminal.get("terminal_id") or "")[:10]


def wrap_label(value: str, max_len: int = 14) -> list[str]:
    value = str(value)
    if len(value) <= max_len:
        return [value]

    parts = value.replace("_", " ").split()
    if not parts:
        return [value[:max_len], value[max_len : max_len * 2]]

    lines: list[str] = []
    current = parts[0]
    for part in parts[1:]:
        if len(current) + 1 + len(part) <= max_len:
            current += " " + part
        else:
            lines.append(current)
            current = part
    lines.append(current)
    return lines[:3]


def edge_color(key: str) -> str:
    index = sum(ord(ch) for ch in key) % len(EDGE_PALETTE)
    return EDGE_PALETTE[index]


def unique_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def path_sort_key(path: Path) -> tuple[int, str]:
    stem = path.stem
    if stem.isdigit():
        return (0, f"{int(stem):08d}")
    parts = re.split(r"(\d+)", stem.lower())
    normalized = "".join(part.zfill(8) if part.isdigit() else part for part in parts)
    return (1, normalized)


def build_terminal_index(data: dict) -> tuple[list[dict], dict[str, dict], dict[str, dict]]:
    components = [dict(component) for component in data.get("components", [])]
    terminal_to_component: dict[str, dict] = {}
    terminal_lookup: dict[str, dict] = {}

    for component in components:
        for terminal in component.get("terminals", []):
            terminal_id = str(terminal.get("terminal_id"))
            terminal_to_component[terminal_id] = component
            terminal_lookup[terminal_id] = terminal

    return components, terminal_to_component, terminal_lookup


def attach_unknown_terminals(
    components: list[dict],
    terminal_to_component: dict[str, dict],
    terminal_lookup: dict[str, dict],
    graph: dict,
) -> None:
    missing_terminal_ids: list[str] = []
    for source, destinations in graph.items():
        if source not in terminal_lookup:
            missing_terminal_ids.append(source)
        for destination in destinations:
            if destination not in terminal_lookup:
                missing_terminal_ids.append(destination)

    for index, terminal_id in enumerate(sorted(set(missing_terminal_ids)), start=1):
        component = {
            "component_id": f"unknown_component_{index}",
            "instance_id": f"unknown_{index}",
            "class_name": "Unknown",
            "terminals": [
                {
                    "terminal_id": terminal_id,
                    "name": terminal_id,
                    "relative_position": None,
                }
            ],
        }
        components.append(component)
        terminal = component["terminals"][0]
        terminal_to_component[terminal_id] = component
        terminal_lookup[terminal_id] = terminal


def build_adjacency(graph: dict, terminal_ids: list[str]) -> dict[str, set[str]]:
    adjacency: dict[str, set[str]] = {terminal_id: set() for terminal_id in terminal_ids}

    for source, destinations in graph.items():
        source_id = str(source)
        adjacency.setdefault(source_id, set())
        for destination in destinations:
            destination_id = str(destination)
            adjacency.setdefault(destination_id, set())
            if source_id == destination_id:
                continue
            adjacency[source_id].add(destination_id)
            adjacency[destination_id].add(source_id)

    return adjacency


def extract_graph_structures(data: dict) -> dict:
    graph = data.get("graph", {}) or {}
    components, terminal_to_component, terminal_lookup = build_terminal_index(data)
    attach_unknown_terminals(components, terminal_to_component, terminal_lookup, graph)

    ordered_terminal_ids: list[str] = []
    class_order: dict[str, int] = {}

    for component in components:
        class_name = str(component.get("class_name", "Unknown"))
        class_order.setdefault(class_name, len(class_order))
        for terminal in component.get("terminals", []):
            ordered_terminal_ids.append(str(terminal.get("terminal_id")))

    for terminal_id in graph.keys():
        if terminal_id not in terminal_lookup:
            ordered_terminal_ids.append(str(terminal_id))
    for destinations in graph.values():
        for terminal_id in destinations:
            if terminal_id not in terminal_lookup:
                ordered_terminal_ids.append(str(terminal_id))

    ordered_terminal_ids = unique_preserve_order(ordered_terminal_ids)
    terminal_order = {terminal_id: index for index, terminal_id in enumerate(ordered_terminal_ids)}
    adjacency = build_adjacency(graph, ordered_terminal_ids)
    net_groups = build_net_groups(adjacency, terminal_order)

    return {
        "graph": graph,
        "components": components,
        "terminal_to_component": terminal_to_component,
        "terminal_lookup": terminal_lookup,
        "ordered_terminal_ids": ordered_terminal_ids,
        "class_order": class_order,
        "net_groups": net_groups,
    }


def build_net_groups(adjacency: dict[str, set[str]], terminal_order: dict[str, int]) -> list[dict]:
    visited: set[str] = set()
    net_groups: list[dict] = []

    for terminal_id in sorted(adjacency.keys(), key=lambda value: terminal_order.get(value, 10**9)):
        if terminal_id in visited:
            continue

        queue = deque([terminal_id])
        visited.add(terminal_id)
        terminals: list[str] = []

        while queue:
            current = queue.popleft()
            terminals.append(current)
            for neighbor in sorted(adjacency[current], key=lambda value: terminal_order.get(value, 10**9)):
                if neighbor in visited:
                    continue
                visited.add(neighbor)
                queue.append(neighbor)

        terminals.sort(key=lambda value: terminal_order.get(value, 10**9))
        net_groups.append(
            {
                "net_id": f"net_{len(net_groups) + 1}",
                "label": str(len(net_groups) + 1),
                "terminal_ids": terminals,
            }
        )

    return net_groups


def build_visual_model(data: dict) -> dict:
    terminal_metadata = data.get("terminal_metadata", {}) or {}
    warnings = data.get("warnings", {}) or {}
    graph_structures = extract_graph_structures(data)
    components = graph_structures["components"]
    ordered_terminal_ids = graph_structures["ordered_terminal_ids"]
    class_order = graph_structures["class_order"]
    net_groups = graph_structures["net_groups"]

    grouped_components: dict[str, list[dict]] = defaultdict(list)
    for component in components:
        grouped_components[str(component.get("class_name", "Unknown"))].append(component)

    class_names = sorted(grouped_components.keys(), key=lambda value: class_order.get(value, 10**9))
    problem_terminal_ids = set(warnings.get("unconnected_terminals", [])) | set(
        warnings.get("unmatched_terminals", [])
    )

    nodes: list[dict] = []
    edges: list[dict] = []

    image_id = str(data.get("image_id") or data.get("image_name") or "circuit")
    root_id = f"root::{image_id}"
    nodes.append(
        {
            "id": root_id,
            "type": "root",
            "label": image_id,
            "tooltip": (
                f"Circuito {image_id}\n"
                f"Componenti: {len(components)}\n"
                f"Terminali: {len(ordered_terminal_ids)}\n"
                f"Nodi elettrici: {len(net_groups)}"
            ),
        }
    )

    for class_name in class_names:
        class_id = f"class::{class_name}"
        nodes.append(
            {
                "id": class_id,
                "type": "class",
                "label": prettify_name(class_name),
                "tooltip": f"Classe: {class_name}\nComponenti: {len(grouped_components[class_name])}",
            }
        )
        edges.append({"source": root_id, "target": class_id, "kind": "hierarchy", "color": "#c8cdd4"})

        for component in grouped_components[class_name]:
            component_id = str(component.get("component_id"))
            component_label = short_component_label(component)
            component_lines = [
                f"Componente: {component_id}",
                f"Classe: {component.get('class_name')}",
                f"Instance: {component.get('instance_id')}",
            ]
            if component.get("display_name") not in (None, ""):
                component_lines.append(f"Display: {component.get('display_name')}")
            if component.get("ic_marking") not in (None, ""):
                component_lines.append(f"IC marking: {component.get('ic_marking')}")
            if component.get("component_subtype") not in (None, ""):
                component_lines.append(f"Subtype: {component.get('component_subtype')}")
            if component.get("state") not in (None, ""):
                component_lines.append(f"State: {component.get('state')}")
            nodes.append(
                {
                    "id": component_id,
                    "type": "component",
                    "label": component_label,
                    "tooltip": "\n".join(component_lines),
                }
            )
            edges.append({"source": class_id, "target": component_id, "kind": "hierarchy", "color": "#c8cdd4"})

            for terminal in component.get("terminals", []):
                terminal_id = str(terminal.get("terminal_id"))
                metadata = terminal_metadata.get(terminal_id) or {}
                terminal_type = "warning_terminal" if terminal_id in problem_terminal_ids else "terminal"
                tooltip_lines = [
                    f"Terminal: {terminal_id}",
                    f"Componente: {component_id}",
                    f"Nome: {terminal.get('name')}",
                ]
                if terminal.get("relative_position") not in (None, ""):
                    tooltip_lines.append(f"Posizione: {terminal.get('relative_position')}")
                if metadata.get("display_name") not in (None, ""):
                    tooltip_lines.append(f"Display: {metadata.get('display_name')}")
                if metadata.get("pin_number") not in (None, ""):
                    tooltip_lines.append(f"Pin: {metadata.get('pin_number')}")
                if metadata.get("pin_label") not in (None, ""):
                    tooltip_lines.append(f"Pin label: {metadata.get('pin_label')}")

                nodes.append(
                    {
                        "id": terminal_id,
                        "type": terminal_type,
                        "label": short_terminal_label(terminal, metadata),
                        "tooltip": "\n".join(tooltip_lines),
                    }
                )
                edges.append({"source": component_id, "target": terminal_id, "kind": "hierarchy", "color": "#c8cdd4"})

    for net in net_groups:
        net_label = net["label"]
        tooltip_lines = [f"Nodo elettrico {net_label}", f"Terminali collegati: {len(net['terminal_ids'])}"]
        tooltip_lines.extend(net["terminal_ids"])
        nodes.append(
            {
                "id": net["net_id"],
                "type": "net",
                "label": net_label,
                "tooltip": "\n".join(tooltip_lines),
            }
        )

        color = edge_color(net["net_id"])
        for terminal_id in net["terminal_ids"]:
            edges.append({"source": terminal_id, "target": net["net_id"], "kind": "net", "color": color})

    positions = compute_positions(root_id, class_names, grouped_components, net_groups)
    node_by_id = {node["id"]: node for node in nodes}
    for node_id, position in positions.items():
        if node_id in node_by_id:
            node_by_id[node_id]["x"] = position[0]
            node_by_id[node_id]["y"] = position[1]

    width = 1260
    height = max(int(max(node.get("y", 0) for node in nodes) + 90), 820)

    return {
        "image_id": image_id,
        "image_name": data.get("image_name"),
        "width": width,
        "height": height,
        "nodes": nodes,
        "edges": edges,
        "summary": {
            "component_count": len(components),
            "terminal_count": len(ordered_terminal_ids),
            "net_count": len(net_groups),
            "unconnected_terminals": len(warnings.get("unconnected_terminals", [])),
            "unmatched_terminals": len(warnings.get("unmatched_terminals", [])),
            "suspicious_matches": len(warnings.get("suspicious_matches", [])),
        },
        "warnings": warnings,
    }


def build_compact_visual_model(data: dict) -> dict:
    terminal_metadata = data.get("terminal_metadata", {}) or {}
    warnings = data.get("warnings", {}) or {}
    graph_structures = extract_graph_structures(data)
    components = graph_structures["components"]
    ordered_terminal_ids = graph_structures["ordered_terminal_ids"]
    terminal_to_component = graph_structures["terminal_to_component"]
    terminal_lookup = graph_structures["terminal_lookup"]
    net_groups = graph_structures["net_groups"]

    image_id = str(data.get("image_id") or data.get("image_name") or "circuit")
    component_by_id = {str(component.get("component_id")): component for component in components}
    component_positions = compute_compact_component_positions(components)

    terminal_to_net: dict[str, dict] = {}
    for net in net_groups:
        for terminal_id in net["terminal_ids"]:
            terminal_to_net[terminal_id] = net

    component_net_terminals: dict[tuple[str, str], list[str]] = defaultdict(list)
    for terminal_id in ordered_terminal_ids:
        component = terminal_to_component.get(terminal_id)
        net = terminal_to_net.get(terminal_id)
        if component is None or net is None:
            continue
        component_id = str(component.get("component_id"))
        component_net_terminals[(component_id, net["net_id"])].append(terminal_id)

    nodes: list[dict] = []
    edges: list[dict] = []

    for component in components:
        component_id = str(component.get("component_id"))
        tooltip_lines = [
            f"Componente: {component_id}",
            f"Classe: {component.get('class_name')}",
            f"Instance: {component.get('instance_id')}",
        ]
        if component.get("display_name") not in (None, ""):
            tooltip_lines.append(f"Display: {component.get('display_name')}")
        if component.get("ic_marking") not in (None, ""):
            tooltip_lines.append(f"IC marking: {component.get('ic_marking')}")
        if component.get("component_subtype") not in (None, ""):
            tooltip_lines.append(f"Subtype: {component.get('component_subtype')}")

        nodes.append(
            {
                "id": component_id,
                "type": "component",
                "label": short_component_label(component),
                "tooltip": "\n".join(tooltip_lines),
                "x": 260,
                "y": component_positions[component_id],
            }
        )

    net_positions = compute_compact_net_positions(net_groups, terminal_to_component, component_positions)
    for net in net_groups:
        terminal_ids = net["terminal_ids"]
        component_ids = sorted(
            {
                str(terminal_to_component[terminal_id].get("component_id"))
                for terminal_id in terminal_ids
                if terminal_id in terminal_to_component
            },
            key=lambda component_id: component_positions.get(component_id, 10**9),
        )
        tooltip_lines = [
            f"Net {net['label']}",
            "Una net e un nodo elettrico: raggruppa terminali collegati dallo stesso filo.",
            f"Componenti collegati: {len(component_ids)}",
            f"Terminali collegati: {len(terminal_ids)}",
        ]
        tooltip_lines.extend(terminal_ids)
        nodes.append(
            {
                "id": net["net_id"],
                "type": "net",
                "label": net["label"],
                "tooltip": "\n".join(tooltip_lines),
                "x": 760,
                "y": net_positions[net["net_id"]],
            }
        )

    for (component_id, net_id), terminal_ids in sorted(
        component_net_terminals.items(),
        key=lambda item: (
            component_positions.get(item[0][0], 10**9),
            net_positions.get(item[0][1], 10**9),
        ),
    ):
        terminal_labels: list[str] = []
        for terminal_id in terminal_ids:
            terminal = terminal_lookup.get(terminal_id, {})
            metadata = terminal_metadata.get(terminal_id) or {}
            terminal_label = short_terminal_label(terminal, metadata)
            terminal_labels.append(f"{terminal_label} ({terminal_id})")

        component = component_by_id.get(component_id, {})
        edge_tooltip = (
            f"{short_component_label(component)} -> {net_id}\n"
            "Terminali del componente su questa net:\n"
            + "\n".join(terminal_labels)
        )
        edges.append(
            {
                "source": component_id,
                "target": net_id,
                "kind": "net",
                "color": edge_color(net_id),
                "tooltip": edge_tooltip,
            }
        )

    width = 980
    height = max(int(max(node.get("y", 0) for node in nodes) + 100), 720)
    return {
        "image_id": image_id,
        "image_name": data.get("image_name"),
        "width": width,
        "height": height,
        "nodes": nodes,
        "edges": edges,
        "summary": {
            "component_count": len(components),
            "terminal_count": len(ordered_terminal_ids),
            "net_count": len(net_groups),
            "unconnected_terminals": len(warnings.get("unconnected_terminals", [])),
            "unmatched_terminals": len(warnings.get("unmatched_terminals", [])),
            "suspicious_matches": len(warnings.get("suspicious_matches", [])),
        },
        "warnings": warnings,
    }


def compute_compact_component_positions(components: list[dict]) -> dict[str, float]:
    positions: dict[str, float] = {}
    y_cursor = 90.0
    for component in components:
        component_id = str(component.get("component_id"))
        terminal_count = max(len(component.get("terminals", [])), 1)
        local_gap = 78.0 if terminal_count <= 3 else min(190.0, 54.0 + terminal_count * 8.0)
        positions[component_id] = y_cursor
        y_cursor += local_gap
    return positions


def compute_compact_net_positions(
    net_groups: list[dict],
    terminal_to_component: dict[str, dict],
    component_positions: dict[str, float],
) -> dict[str, float]:
    targets: list[tuple[str, float]] = []
    for net in net_groups:
        component_ys: list[float] = []
        for terminal_id in net["terminal_ids"]:
            component = terminal_to_component.get(terminal_id)
            if component is None:
                continue
            component_id = str(component.get("component_id"))
            if component_id in component_positions:
                component_ys.append(component_positions[component_id])
        target_y = sum(component_ys) / len(component_ys) if component_ys else 90.0
        targets.append((net["net_id"], target_y))

    positions: dict[str, float] = {}
    previous_y = 50.0
    for net_id, target_y in sorted(targets, key=lambda item: item[1]):
        net_y = max(target_y, previous_y + 38.0)
        positions[net_id] = net_y
        previous_y = net_y
    return positions


def compute_positions(
    root_id: str,
    class_names: list[str],
    grouped_components: dict[str, list[dict]],
    net_groups: list[dict],
) -> dict[str, tuple[float, float]]:
    terminal_count = sum(
        len(component.get("terminals", []))
        for components in grouped_components.values()
        for component in components
    )
    terminal_spacing = max(58.0, min(86.0, 2600.0 / max(terminal_count, 1)))
    component_gap = max(38.0, terminal_spacing * 0.55)
    class_gap = max(76.0, terminal_spacing * 0.95)
    net_gap = 34.0
    margin_y = 82.0

    positions: dict[str, tuple[float, float]] = {}
    class_centers: dict[str, float] = {}
    terminal_centers: dict[str, float] = {}
    y_cursor = margin_y

    for class_name in class_names:
        component_ys: list[float] = []
        class_id = f"class::{class_name}"
        for component in grouped_components[class_name]:
            component_id = str(component.get("component_id"))
            terminal_ys: list[float] = []

            for terminal in component.get("terminals", []):
                terminal_id = str(terminal.get("terminal_id"))
                positions[terminal_id] = (LAYER_X["terminal"], y_cursor)
                terminal_centers[terminal_id] = y_cursor
                terminal_ys.append(y_cursor)
                y_cursor += terminal_spacing

            if terminal_ys:
                component_y = sum(terminal_ys) / len(terminal_ys)
            else:
                component_y = y_cursor
                y_cursor += terminal_spacing

            positions[component_id] = (LAYER_X["component"], component_y)
            component_ys.append(component_y)
            y_cursor += component_gap

        if component_ys:
            class_y = sum(component_ys) / len(component_ys)
        else:
            class_y = y_cursor
            y_cursor += terminal_spacing

        positions[class_id] = (LAYER_X["class"], class_y)
        class_centers[class_id] = class_y
        y_cursor += class_gap

    if class_centers:
        root_y = sum(class_centers.values()) / len(class_centers)
    else:
        root_y = margin_y
    positions[root_id] = (LAYER_X["root"], root_y)

    net_targets: list[tuple[str, float]] = []
    for net in net_groups:
        terminal_ids = net["terminal_ids"]
        if terminal_ids:
            target_y = sum(terminal_centers[terminal_id] for terminal_id in terminal_ids) / len(terminal_ids)
        else:
            target_y = root_y
        net_targets.append((net["net_id"], target_y))

    net_targets.sort(key=lambda item: item[1])
    previous_y = margin_y - net_gap
    for net_id, target_y in net_targets:
        net_y = max(target_y, previous_y + net_gap)
        positions[net_id] = (LAYER_X["net"], net_y)
        previous_y = net_y

    return positions


def resolve_node_style(node: dict) -> dict:
    return NODE_STYLE.get(node["type"], NODE_STYLE["component"])


def node_label_max_len(node_type: str) -> int:
    if node_type == "component":
        return 16
    if node_type == "class":
        return 14
    return 10


def render_png(model: dict, png_path: Path) -> None:
    width_inches = model["width"] / 100.0
    height_inches = model["height"] / 100.0
    fig, ax = plt.subplots(figsize=(width_inches, height_inches), dpi=100)
    fig.patch.set_facecolor("#f7f9fc")
    ax.set_facecolor("#f7f9fc")
    ax.axis("off")

    nodes = {node["id"]: node for node in model["nodes"]}

    for edge in model["edges"]:
        source = nodes[edge["source"]]
        target = nodes[edge["target"]]
        ax.plot(
            [source["x"], target["x"]],
            [source["y"], target["y"]],
            color=edge["color"],
            linewidth=1.6 if edge["kind"] == "net" else 1.0,
            alpha=0.78 if edge["kind"] == "net" else 0.55,
            zorder=1,
        )

    for node in model["nodes"]:
        style = resolve_node_style(node)
        circle = Circle(
            (node["x"], node["y"]),
            radius=style["radius"],
            facecolor=style["fill"],
            edgecolor=style["stroke"],
            linewidth=2.0,
            zorder=2,
        )
        ax.add_patch(circle)

        lines = wrap_label(node["label"], max_len=node_label_max_len(node["type"]))
        if len(lines) == 1:
            ax.text(
                node["x"],
                node["y"],
                lines[0],
                ha="center",
                va="center",
                fontsize=style["font_size"],
                color="#304050",
                zorder=3,
            )
        else:
            top_y = node["y"] - (len(lines) - 1) * 7
            for index, line in enumerate(lines):
                ax.text(
                    node["x"],
                    top_y + index * 14,
                    line,
                    ha="center",
                    va="center",
                    fontsize=style["font_size"] - 1,
                    color="#304050",
                    zorder=3,
                )

    ax.set_xlim(0, model["width"])
    ax.set_ylim(model["height"], 0)
    fig.tight_layout(pad=0.2)
    fig.savefig(png_path, dpi=100, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


def svg_circle(node: dict) -> str:
    style = resolve_node_style(node)
    label_lines = wrap_label(node["label"], max_len=node_label_max_len(node["type"]))

    text_parts: list[str] = []
    if len(label_lines) == 1:
        text_parts.append(
            f'<text x="{node["x"]:.1f}" y="{node["y"] + 4:.1f}" text-anchor="middle" class="node-label">{escape(label_lines[0])}</text>'
        )
    else:
        start_y = node["y"] - (len(label_lines) - 1) * 7
        for index, line in enumerate(label_lines):
            text_parts.append(
                f'<text x="{node["x"]:.1f}" y="{start_y + index * 14 + 4:.1f}" text-anchor="middle" class="node-label small">{escape(line)}</text>'
            )

    return (
        f'<g class="node-group" data-node-type="{escape(node["type"])}">'
        f'<title>{escape(node["tooltip"])}</title>'
        f'<circle cx="{node["x"]:.1f}" cy="{node["y"]:.1f}" r="{style["radius"]:.1f}" '
        f'fill="{style["fill"]}" stroke="{style["stroke"]}" stroke-width="2"></circle>'
        f'{"".join(text_parts)}'
        f"</g>"
    )


def build_svg(model: dict) -> str:
    node_lookup = {node["id"]: node for node in model["nodes"]}
    edge_parts: list[str] = []
    initial_height = min(model["height"], 920)
    root_nodes = [node for node in model["nodes"] if node["type"] == "root"]
    root_y = root_nodes[0]["y"] if root_nodes else sum(node["y"] for node in model["nodes"]) / max(len(model["nodes"]), 1)
    initial_y = max(0, min(root_y - initial_height / 2, model["height"] - initial_height))

    for edge in model["edges"]:
        source = node_lookup[edge["source"]]
        target = node_lookup[edge["target"]]
        title = f"<title>{escape(edge['tooltip'])}</title>" if edge.get("tooltip") else ""
        edge_parts.append(
            f'<line x1="{source["x"]:.1f}" y1="{source["y"]:.1f}" x2="{target["x"]:.1f}" y2="{target["y"]:.1f}" '
            f'stroke="{edge["color"]}" stroke-width="{2 if edge["kind"] == "net" else 1.2}" '
            f'stroke-opacity="{0.82 if edge["kind"] == "net" else 0.55}">{title}</line>'
        )

    node_parts = [svg_circle(node) for node in model["nodes"]]
    return (
        f'<svg id="graph-svg" viewBox="0 {initial_y:.1f} {model["width"]} {initial_height}" '
        f'data-full-width="{model["width"]}" data-full-height="{model["height"]}" '
        f'xmlns="http://www.w3.org/2000/svg" aria-label="Graph">'
        f'{"".join(edge_parts)}'
        f'{"".join(node_parts)}'
        f"</svg>"
    )


def build_summary_html(model: dict) -> str:
    summary = model["summary"]
    return (
        '<div class="summary-grid">'
        f'<div class="summary-item"><span class="k">Componenti</span><span class="v">{summary["component_count"]}</span></div>'
        f'<div class="summary-item"><span class="k">Terminali</span><span class="v">{summary["terminal_count"]}</span></div>'
        f'<div class="summary-item"><span class="k">Nodi elettrici</span><span class="v">{summary["net_count"]}</span></div>'
        f'<div class="summary-item"><span class="k">Isolati</span><span class="v">{summary["unconnected_terminals"]}</span></div>'
        f'<div class="summary-item"><span class="k">Unmatched</span><span class="v">{summary["unmatched_terminals"]}</span></div>'
        f'<div class="summary-item"><span class="k">Suspicious</span><span class="v">{summary["suspicious_matches"]}</span></div>'
        "</div>"
    )


def build_warning_html(warnings: dict) -> str:
    blocks: list[str] = []
    for key in ("unconnected_terminals", "unmatched_terminals", "suspicious_matches"):
        values = warnings.get(key, [])
        label = prettify_name(key).title()
        if not values:
            blocks.append(f'<div class="warning-box"><h3>{escape(label)}</h3><p>Nessun elemento.</p></div>')
            continue
        items = "".join(f"<li>{escape(str(value))}</li>" for value in values)
        blocks.append(f'<div class="warning-box"><h3>{escape(label)}</h3><ul>{items}</ul></div>')
    return '<div class="warning-grid">' + "".join(blocks) + "</div>"


def build_graph_page(
    model: dict,
    image_rel: str | None,
    json_rel: str,
    png_rel: str,
    copied_json: dict,
    compact_html_rel: str | None = None,
    compact_png_rel: str | None = None,
) -> str:
    image_html = (
        f'<img src="{escape(image_rel)}" alt="Circuito {escape(model["image_id"])}" class="preview-image">'
        if image_rel
        else '<div class="preview-missing">Immagine non trovata</div>'
    )
    svg = build_svg(model)
    summary_html = build_summary_html(model)
    warning_html = build_warning_html(model["warnings"])
    json_pretty = escape(json.dumps(copied_json, indent=2, ensure_ascii=False))
    compact_links = ""
    if compact_html_rel and compact_png_rel:
        compact_links = (
            f'<a href="{escape(compact_html_rel)}">Vista compatta HTML</a>'
            f'<a href="{escape(compact_png_rel)}">Vista compatta PNG</a>'
        )

    return f"""<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Graph {escape(model["image_id"])}</title>
  <style>
    body {{
      margin: 0;
      font-family: "Segoe UI", Tahoma, sans-serif;
      background: linear-gradient(180deg, #f7f9fc 0%, #eef3f8 100%);
      color: #1f2d3a;
    }}
    .page {{
      max-width: 1600px;
      margin: 0 auto;
      padding: 24px;
    }}
    .topbar {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 18px;
    }}
    .topbar h1 {{
      margin: 0;
      font-size: 28px;
    }}
    .links {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .links a {{
      text-decoration: none;
      color: #144a7b;
      background: #ffffff;
      border: 1px solid #d8e1ea;
      border-radius: 999px;
      padding: 8px 14px;
      font-weight: 600;
    }}
    .summary-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 12px;
      margin-bottom: 20px;
    }}
    .summary-item {{
      background: rgba(255,255,255,0.88);
      border: 1px solid #d8e1ea;
      border-radius: 14px;
      padding: 14px 16px;
      display: flex;
      justify-content: space-between;
      align-items: baseline;
    }}
    .summary-item .k {{
      color: #5f7184;
      font-size: 13px;
    }}
    .summary-item .v {{
      font-size: 24px;
      font-weight: 700;
    }}
    .panel-grid {{
      display: grid;
      grid-template-columns: minmax(280px, 420px) 1fr;
      gap: 18px;
      align-items: start;
    }}
    .panel {{
      background: rgba(255,255,255,0.92);
      border: 1px solid #d8e1ea;
      border-radius: 18px;
      padding: 18px;
      box-shadow: 0 12px 24px rgba(27, 53, 82, 0.06);
    }}
    .panel h2 {{
      margin: 0 0 12px 0;
      font-size: 18px;
    }}
    .preview-image {{
      width: 100%;
      display: block;
      border-radius: 12px;
      border: 1px solid #d8e1ea;
      background: #fff;
    }}
    .preview-missing {{
      min-height: 220px;
      display: grid;
      place-items: center;
      border-radius: 12px;
      border: 1px dashed #c6d2de;
      color: #6f8093;
      background: #f9fbfd;
    }}
    .graph-wrap {{
      overflow: hidden;
      border: 1px solid #d8e1ea;
      border-radius: 14px;
      background: #f8fbff;
      cursor: grab;
      min-height: 720px;
    }}
    .graph-wrap:active {{
      cursor: grabbing;
    }}
    #graph-svg {{
      width: 100%;
      height: 760px;
      display: block;
      user-select: none;
    }}
    .node-label {{
      fill: #314457;
      font-size: 11px;
      font-weight: 600;
      pointer-events: none;
    }}
    .node-label.small {{
      font-size: 10px;
    }}
    .legend {{
      margin-top: 14px;
      display: flex;
      flex-wrap: wrap;
      gap: 10px 14px;
      font-size: 13px;
      color: #55687d;
    }}
    .legend span {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }}
    .dot {{
      width: 12px;
      height: 12px;
      border-radius: 50%;
      display: inline-block;
    }}
    .warning-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 12px;
      margin-top: 18px;
    }}
    .warning-box {{
      background: rgba(255,255,255,0.92);
      border: 1px solid #d8e1ea;
      border-radius: 14px;
      padding: 14px;
    }}
    .warning-box h3 {{
      margin: 0 0 10px 0;
      font-size: 15px;
    }}
    .warning-box p, .warning-box li {{
      color: #526274;
      font-size: 13px;
    }}
    details {{
      margin-top: 18px;
      background: rgba(255,255,255,0.92);
      border: 1px solid #d8e1ea;
      border-radius: 14px;
      padding: 14px 16px;
    }}
    summary {{
      cursor: pointer;
      font-weight: 700;
    }}
    pre {{
      margin: 14px 0 0 0;
      white-space: pre-wrap;
      word-break: break-word;
      font-size: 12px;
      color: #314457;
    }}
    .note {{
      color: #5c6f82;
      font-size: 13px;
      margin-top: 10px;
    }}
    @media (max-width: 980px) {{
      .panel-grid {{
        grid-template-columns: 1fr;
      }}
      #graph-svg {{
        height: 600px;
      }}
      .graph-wrap {{
        min-height: 560px;
      }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <div class="topbar">
      <h1>Graph {escape(model["image_id"])}</h1>
      <div class="links">
        {compact_links}
        <a href="{escape(json_rel)}">JSON finale 05</a>
        <a href="{escape(png_rel)}">Graph PNG</a>
        <a href="../index.html">Batch index</a>
      </div>
    </div>

    {summary_html}

    <div class="panel-grid">
      <section class="panel">
        <h2>Circuito</h2>
        {image_html}
        <p class="note">Il grafo sotto e costruito solo a partire dal JSON del passo 05. La lettura va da sinistra a destra: circuito, classi, componenti, terminali e nodi elettrici.</p>
      </section>

      <section class="panel">
        <h2>Graph interattivo</h2>
        <div class="graph-wrap" id="graph-wrap">{svg}</div>
        <div class="legend">
          <span><i class="dot" style="background:#f26a63"></i> circuito</span>
          <span><i class="dot" style="background:#dcc9a5"></i> classe</span>
          <span><i class="dot" style="background:#85d68d"></i> componente</span>
          <span><i class="dot" style="background:#f4abc7"></i> terminale</span>
          <span><i class="dot" style="background:#ffd65a"></i> nodo elettrico</span>
        </div>
      </section>
    </div>

    {warning_html}

    <details>
      <summary>Mostra JSON finale completo</summary>
      <pre>{json_pretty}</pre>
    </details>
  </div>

  <script>
    (() => {{
      const svg = document.getElementById("graph-svg");
      const viewBox = svg.viewBox.baseVal;
      let isDragging = false;
      let startX = 0;
      let startY = 0;
      let startViewX = viewBox.x;
      let startViewY = viewBox.y;

      function pointFromEvent(event) {{
        const rect = svg.getBoundingClientRect();
        return {{
          x: (event.clientX - rect.left) * (viewBox.width / rect.width),
          y: (event.clientY - rect.top) * (viewBox.height / rect.height),
        }};
      }}

      svg.addEventListener("wheel", (event) => {{
        event.preventDefault();
        const scale = event.deltaY < 0 ? 0.92 : 1.08;
        const point = pointFromEvent(event);
        const newWidth = viewBox.width * scale;
        const newHeight = viewBox.height * scale;
        viewBox.x = point.x - (point.x - viewBox.x) * scale;
        viewBox.y = point.y - (point.y - viewBox.y) * scale;
        viewBox.width = Math.max(480, newWidth);
        viewBox.height = Math.max(360, newHeight);
      }}, {{ passive: false }});

      svg.addEventListener("pointerdown", (event) => {{
        isDragging = true;
        svg.setPointerCapture(event.pointerId);
        startX = event.clientX;
        startY = event.clientY;
        startViewX = viewBox.x;
        startViewY = viewBox.y;
      }});

      svg.addEventListener("pointermove", (event) => {{
        if (!isDragging) return;
        const rect = svg.getBoundingClientRect();
        const dx = (event.clientX - startX) * (viewBox.width / rect.width);
        const dy = (event.clientY - startY) * (viewBox.height / rect.height);
        viewBox.x = startViewX - dx;
        viewBox.y = startViewY - dy;
      }});

      svg.addEventListener("pointerup", () => {{
        isDragging = false;
      }});

      svg.addEventListener("pointerleave", () => {{
        isDragging = false;
      }});
    }})();
  </script>
</body>
</html>
"""


def build_compact_graph_page(
    model: dict,
    image_rel: str | None,
    json_rel: str,
    png_rel: str,
    full_html_rel: str,
    full_png_rel: str,
) -> str:
    image_html = (
        f'<img src="{escape(image_rel)}" alt="Circuito {escape(model["image_id"])}" class="preview-image">'
        if image_rel
        else '<div class="preview-missing">Immagine non trovata</div>'
    )
    svg = build_svg(model)
    summary_html = build_summary_html(model)
    warning_html = build_warning_html(model["warnings"])

    return f"""<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Graph compatto {escape(model["image_id"])}</title>
  <style>
    body {{
      margin: 0;
      font-family: "Segoe UI", Tahoma, sans-serif;
      background: linear-gradient(180deg, #f7f9fc 0%, #eef3f8 100%);
      color: #1f2d3a;
    }}
    .page {{
      max-width: 1500px;
      margin: 0 auto;
      padding: 24px;
    }}
    .topbar {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 18px;
    }}
    .topbar h1 {{
      margin: 0;
      font-size: 28px;
    }}
    .links {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .links a {{
      text-decoration: none;
      color: #144a7b;
      background: #ffffff;
      border: 1px solid #d8e1ea;
      border-radius: 999px;
      padding: 8px 14px;
      font-weight: 600;
    }}
    .summary-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 12px;
      margin-bottom: 18px;
    }}
    .summary-item {{
      background: rgba(255,255,255,0.88);
      border: 1px solid #d8e1ea;
      border-radius: 14px;
      padding: 14px 16px;
      display: flex;
      justify-content: space-between;
      align-items: baseline;
    }}
    .summary-item .k {{
      color: #5f7184;
      font-size: 13px;
    }}
    .summary-item .v {{
      font-size: 24px;
      font-weight: 700;
    }}
    .explain-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 12px;
      margin-bottom: 18px;
    }}
    .explain-box {{
      background: rgba(255,255,255,0.94);
      border: 1px solid #d8e1ea;
      border-radius: 14px;
      padding: 14px 16px;
    }}
    .explain-box h2 {{
      margin: 0 0 8px 0;
      font-size: 16px;
    }}
    .explain-box p {{
      margin: 0;
      color: #526274;
      line-height: 1.45;
      font-size: 14px;
    }}
    .panel-grid {{
      display: grid;
      grid-template-columns: minmax(260px, 360px) 1fr;
      gap: 18px;
      align-items: start;
    }}
    .panel {{
      background: rgba(255,255,255,0.92);
      border: 1px solid #d8e1ea;
      border-radius: 18px;
      padding: 18px;
      box-shadow: 0 12px 24px rgba(27, 53, 82, 0.06);
    }}
    .panel h2 {{
      margin: 0 0 12px 0;
      font-size: 18px;
    }}
    .preview-image {{
      width: 100%;
      display: block;
      border-radius: 12px;
      border: 1px solid #d8e1ea;
      background: #fff;
    }}
    .preview-missing {{
      min-height: 220px;
      display: grid;
      place-items: center;
      border-radius: 12px;
      border: 1px dashed #c6d2de;
      color: #6f8093;
      background: #f9fbfd;
    }}
    .graph-wrap {{
      overflow: hidden;
      border: 1px solid #d8e1ea;
      border-radius: 14px;
      background: #f8fbff;
      cursor: grab;
      min-height: 720px;
    }}
    .graph-wrap:active {{
      cursor: grabbing;
    }}
    #graph-svg {{
      width: 100%;
      height: 760px;
      display: block;
      user-select: none;
    }}
    .node-label {{
      fill: #314457;
      font-size: 11px;
      font-weight: 600;
      pointer-events: none;
    }}
    .node-label.small {{
      font-size: 10px;
    }}
    .legend {{
      margin-top: 14px;
      display: flex;
      flex-wrap: wrap;
      gap: 10px 14px;
      font-size: 13px;
      color: #55687d;
    }}
    .legend span {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }}
    .dot {{
      width: 12px;
      height: 12px;
      border-radius: 50%;
      display: inline-block;
    }}
    .warning-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 12px;
      margin-top: 18px;
    }}
    .warning-box {{
      background: rgba(255,255,255,0.92);
      border: 1px solid #d8e1ea;
      border-radius: 14px;
      padding: 14px;
    }}
    .warning-box h3 {{
      margin: 0 0 10px 0;
      font-size: 15px;
    }}
    .warning-box p, .warning-box li {{
      color: #526274;
      font-size: 13px;
    }}
    @media (max-width: 980px) {{
      .panel-grid {{
        grid-template-columns: 1fr;
      }}
      #graph-svg {{
        height: 600px;
      }}
      .graph-wrap {{
        min-height: 560px;
      }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <div class="topbar">
      <h1>Graph compatto {escape(model["image_id"])}</h1>
      <div class="links">
        <a href="{escape(full_html_rel)}">Vista completa HTML</a>
        <a href="{escape(full_png_rel)}">Vista completa PNG</a>
        <a href="{escape(json_rel)}">JSON finale 05</a>
        <a href="{escape(png_rel)}">Compatto PNG</a>
        <a href="../index.html">Batch index</a>
      </div>
    </div>

    {summary_html}

    <div class="explain-grid">
      <section class="explain-box">
        <h2>Cosa stai guardando</h2>
        <p>Questa e una vista topologica compatta costruita dal JSON del passo 05. I nodi verdi sono componenti. I nodi gialli sono net, cioe nodi elettrici: gruppi di terminali collegati dallo stesso filo.</p>
      </section>
      <section class="explain-box">
        <h2>Come si legge</h2>
        <p>Se due componenti arrivano alla stessa net gialla, allora sono collegati allo stesso nodo elettrico. Per esempio: <code>resistor22.1 -> net 3 <- TDA7000</code> significa che un terminale del resistore e un pin del circuito integrato condividono quel collegamento.</p>
      </section>
      <section class="explain-box">
        <h2>Perche non solo componente-componente</h2>
        <p>Mostrare la net evita ambiguita: quando tre o piu componenti sono collegati allo stesso filo, una semplice linea componente-componente farebbe sembrare tanti collegamenti separati. La net dice che in realta e un unico nodo comune.</p>
      </section>
    </div>

    <div class="panel-grid">
      <section class="panel">
        <h2>Circuito</h2>
        {image_html}
      </section>

      <section class="panel">
        <h2>Vista componenti/net</h2>
        <div class="graph-wrap" id="graph-wrap">{svg}</div>
        <div class="legend">
          <span><i class="dot" style="background:#85d68d"></i> componente</span>
          <span><i class="dot" style="background:#ffd65a"></i> net / nodo elettrico</span>
          <span>Passa sopra archi e nodi per vedere terminali e pin esatti.</span>
        </div>
      </section>
    </div>

    {warning_html}
  </div>

  <script>
    (() => {{
      const svg = document.getElementById("graph-svg");
      const viewBox = svg.viewBox.baseVal;
      let isDragging = false;
      let startX = 0;
      let startY = 0;
      let startViewX = viewBox.x;
      let startViewY = viewBox.y;

      function pointFromEvent(event) {{
        const rect = svg.getBoundingClientRect();
        return {{
          x: (event.clientX - rect.left) * (viewBox.width / rect.width),
          y: (event.clientY - rect.top) * (viewBox.height / rect.height),
        }};
      }}

      svg.addEventListener("wheel", (event) => {{
        event.preventDefault();
        const scale = event.deltaY < 0 ? 0.92 : 1.08;
        const point = pointFromEvent(event);
        const newWidth = viewBox.width * scale;
        const newHeight = viewBox.height * scale;
        viewBox.x = point.x - (point.x - viewBox.x) * scale;
        viewBox.y = point.y - (point.y - viewBox.y) * scale;
        viewBox.width = Math.max(420, newWidth);
        viewBox.height = Math.max(320, newHeight);
      }}, {{ passive: false }});

      svg.addEventListener("pointerdown", (event) => {{
        isDragging = true;
        svg.setPointerCapture(event.pointerId);
        startX = event.clientX;
        startY = event.clientY;
        startViewX = viewBox.x;
        startViewY = viewBox.y;
      }});

      svg.addEventListener("pointermove", (event) => {{
        if (!isDragging) return;
        const rect = svg.getBoundingClientRect();
        const dx = (event.clientX - startX) * (viewBox.width / rect.width);
        const dy = (event.clientY - startY) * (viewBox.height / rect.height);
        viewBox.x = startViewX - dx;
        viewBox.y = startViewY - dy;
      }});

      svg.addEventListener("pointerup", () => {{
        isDragging = false;
      }});

      svg.addEventListener("pointerleave", () => {{
        isDragging = false;
      }});
    }})();
  </script>
</body>
</html>
"""


def build_index_page(items: list[dict], output_dir: Path) -> str:
    card_html = []
    for item in items:
        image_html = (
            f'<img src="{escape(item["image_rel"])}" alt="Circuito {escape(item["image_id"])}">'
            if item["image_rel"]
            else '<div class="thumb missing">Immagine non trovata</div>'
        )
        summary = item["summary"]
        card_html.append(
            f"""
            <article class="card">
              <div class="thumb-wrap">{image_html}</div>
              <div class="card-body">
                <h2>{escape(item["image_id"])}</h2>
                <p class="mini">
                  componenti {summary["component_count"]} ·
                  terminali {summary["terminal_count"]} ·
                  net {summary["net_count"]}
                </p>
                <div class="pill-row">
                  <span class="pill">isolati {summary["unconnected_terminals"]}</span>
                  <span class="pill">unmatched {summary["unmatched_terminals"]}</span>
                  <span class="pill">suspicious {summary["suspicious_matches"]}</span>
                </div>
                <div class="link-row">
                  <a href="{escape(item["compact_html_rel"])}">compatto html</a>
                  <a href="{escape(item["compact_png_rel"])}">compatto png</a>
                  <a href="{escape(item["graph_html_rel"])}">completo html</a>
                  <a href="{escape(item["graph_png_rel"])}">completo png</a>
                  <a href="{escape(item["json_rel"])}">json 05</a>
                </div>
              </div>
            </article>
            """
        )

    generated_from = escape(str(output_dir.parent / "05_build_terminal_graph"))
    return f"""<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Batch Graph Report</title>
  <style>
    body {{
      margin: 0;
      font-family: "Segoe UI", Tahoma, sans-serif;
      background:
        radial-gradient(circle at top left, rgba(255, 214, 90, 0.20), transparent 28%),
        radial-gradient(circle at top right, rgba(133, 214, 141, 0.20), transparent 22%),
        linear-gradient(180deg, #f7f9fc 0%, #edf3f9 100%);
      color: #1f2d3a;
    }}
    .page {{
      max-width: 1500px;
      margin: 0 auto;
      padding: 28px 24px 40px;
    }}
    h1 {{
      margin: 0 0 8px 0;
      font-size: 34px;
    }}
    .lead {{
      margin: 0 0 22px 0;
      color: #5c6f82;
      max-width: 920px;
    }}
    .meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 24px;
    }}
    .meta span {{
      background: rgba(255,255,255,0.88);
      border: 1px solid #d8e1ea;
      border-radius: 999px;
      padding: 8px 14px;
      color: #486078;
      font-size: 13px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(290px, 1fr));
      gap: 18px;
    }}
    .card {{
      background: rgba(255,255,255,0.92);
      border: 1px solid #d8e1ea;
      border-radius: 20px;
      overflow: hidden;
      box-shadow: 0 16px 30px rgba(27, 53, 82, 0.07);
    }}
    .thumb-wrap {{
      aspect-ratio: 1 / 1;
      background: #f8fbff;
      border-bottom: 1px solid #d8e1ea;
    }}
    .thumb-wrap img, .thumb {{
      width: 100%;
      height: 100%;
      object-fit: contain;
      display: block;
      background: #fff;
    }}
    .thumb.missing {{
      display: grid;
      place-items: center;
      color: #6f8093;
      font-size: 14px;
    }}
    .card-body {{
      padding: 16px 18px 18px;
    }}
    .card h2 {{
      margin: 0 0 6px 0;
      font-size: 21px;
    }}
    .mini {{
      margin: 0 0 12px 0;
      color: #5c6f82;
      font-size: 13px;
    }}
    .pill-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 14px;
    }}
    .pill {{
      background: #eef4fb;
      border: 1px solid #d7e2ee;
      border-radius: 999px;
      padding: 6px 10px;
      font-size: 12px;
      color: #476177;
    }}
    .link-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .link-row a {{
      text-decoration: none;
      color: #144a7b;
      font-weight: 700;
      background: #ffffff;
      border: 1px solid #d8e1ea;
      border-radius: 999px;
      padding: 8px 12px;
    }}
  </style>
</head>
<body>
  <div class="page">
    <h1>Batch Graph Report</h1>
    <p class="lead">Vista batch costruita dal JSON finale del passo 05. La vista compatta mostra componenti e net: una net e un nodo elettrico, cioe un gruppo di terminali collegati dallo stesso filo. La vista completa mantiene anche classi e terminali per il debug.</p>
    <div class="meta">
      <span>Circuiti: {len(items)}</span>
      <span>Sorgente: {generated_from}</span>
      <span>Output: {escape(str(output_dir))}</span>
    </div>
    <div class="grid">
      {"".join(card_html)}
    </div>
  </div>
</body>
</html>
"""


def relative_href(source_dir: Path, target_path: Path | None) -> str | None:
    if target_path is None:
        return None
    return os.path.relpath(target_path, start=source_dir).replace("\\", "/")


def copy_circuit_image(image_path: Path | None, destination: Path) -> Path | None:
    if image_path is None or not image_path.exists():
        return None
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(image_path, destination)
    return destination


def resolve_image_path(detect_dir: Path, stem: str) -> Path | None:
    detect_json_path = detect_dir / f"{stem}.json"
    if detect_json_path.exists():
        detect_data = load_json(detect_json_path)
        image_path = detect_data.get("image_path")
        if image_path:
            candidate = Path(image_path)
            if candidate.exists():
                return candidate

    debug_candidates = [
        detect_dir / "debug_images" / f"{stem}_detect.jpg",
        detect_dir.parent / "05_build_terminal_graph" / "debug_terminal_overlay" / f"{stem}_terminal_overlay.jpg",
    ]
    for candidate in debug_candidates:
        if candidate.exists():
            return candidate
    return None


def render_one_json(json_path: Path, detect_dir: Path, output_dir: Path) -> dict:
    source_data = load_json(json_path)
    model = build_visual_model(source_data)
    compact_model = build_compact_visual_model(source_data)

    circuit_dir = output_dir / str(model["image_id"])
    circuit_dir.mkdir(parents=True, exist_ok=True)

    copied_json_path = circuit_dir / f"{json_path.stem}.json"
    save_json(copied_json_path, source_data)

    image_source_path = resolve_image_path(detect_dir, json_path.stem)
    image_output_path: Path | None = None
    if image_source_path is not None:
        image_output_path = copy_circuit_image(image_source_path, circuit_dir / image_source_path.name)

    png_path = circuit_dir / "graph.png"
    html_path = circuit_dir / "graph.html"
    compact_png_path = circuit_dir / "graph_compact.png"
    compact_html_path = circuit_dir / "graph_compact.html"

    render_png(compact_model, compact_png_path)
    compact_html = build_compact_graph_page(
        model=compact_model,
        image_rel=relative_href(circuit_dir, image_output_path),
        json_rel=relative_href(circuit_dir, copied_json_path) or f"{json_path.stem}.json",
        png_rel=relative_href(circuit_dir, compact_png_path) or "graph_compact.png",
        full_html_rel=relative_href(circuit_dir, html_path) or "graph.html",
        full_png_rel=relative_href(circuit_dir, png_path) or "graph.png",
    )
    with open(compact_html_path, "w", encoding="utf-8") as f:
        f.write(compact_html)

    render_png(model, png_path)
    graph_html = build_graph_page(
        model=model,
        image_rel=relative_href(circuit_dir, image_output_path),
        json_rel=relative_href(circuit_dir, copied_json_path) or f"{json_path.stem}.json",
        png_rel=relative_href(circuit_dir, png_path) or "graph.png",
        copied_json=source_data,
        compact_html_rel=relative_href(circuit_dir, compact_html_path),
        compact_png_rel=relative_href(circuit_dir, compact_png_path),
    )
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(graph_html)

    return {
        "image_id": model["image_id"],
        "summary": model["summary"],
        "graph_html_path": html_path,
        "graph_png_path": png_path,
        "compact_html_path": compact_html_path,
        "compact_png_path": compact_png_path,
        "json_path": copied_json_path,
        "image_path": image_output_path,
    }


def main() -> None:
    args = parse_args()
    input_dir = args.input_dir
    detect_dir = args.detect_dir
    output_dir = args.output_dir

    if not input_dir.exists():
        raise FileNotFoundError(f"Cartella input non trovata: {input_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    json_files = sorted(input_dir.glob("*.json"), key=path_sort_key)
    if not json_files:
        raise FileNotFoundError(f"Nessun JSON trovato in: {input_dir}")

    print(f"Input directory : {input_dir}")
    print(f"Detect directory: {detect_dir}")
    print(f"Output directory: {output_dir}")
    print(f"File trovati    : {len(json_files)}\n")

    index_items: list[dict] = []
    for index, json_path in enumerate(json_files, start=1):
        result = render_one_json(json_path, detect_dir, output_dir)
        index_items.append(
            {
                "image_id": result["image_id"],
                "summary": result["summary"],
                "graph_html_rel": relative_href(output_dir, result["graph_html_path"]) or "",
                "graph_png_rel": relative_href(output_dir, result["graph_png_path"]) or "",
                "compact_html_rel": relative_href(output_dir, result["compact_html_path"]) or "",
                "compact_png_rel": relative_href(output_dir, result["compact_png_path"]) or "",
                "json_rel": relative_href(output_dir, result["json_path"]) or "",
                "image_rel": relative_href(output_dir, result["image_path"]),
            }
        )
        print(
            f"[{index}/{len(json_files)}] {json_path.name} -> "
            f"graph_compact.html, graph_compact.png, graph.html, graph.png, json copiato"
        )

    index_html = build_index_page(index_items, output_dir)
    index_path = output_dir / "index.html"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_html)

    print("\nCompletato.")
    print(f"Index HTML: {index_path}")


if __name__ == "__main__":
    main()
