"""
08_visualize_graph.py

Scopo:
    Generare visualizzazioni del grafo esportato dal passo 07.

Viste prodotte:
    - full graph
    - component -> net
    - overlay sul diagramma
    - index.html batch

Output:
    - PNG statiche
    - HTML interattive
    - dashboard index.html
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import networkx as nx
import plotly.graph_objects as go

# =========================================================
# PATHS / INPUT-OUTPUT
# =========================================================
PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_DIR = PROJECT_ROOT / "outputs" / "topology_v2" / "07_export_graph" / "graph_json"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "topology_v2" / "08_visualize_graph"

# =========================================================
# OUTPUT SUBDIRECTORIES
# =========================================================
FULL_PNG_DIR = OUTPUT_DIR / "full_png"
FULL_HTML_DIR = OUTPUT_DIR / "full_html"
COMPONENT_NET_PNG_DIR = OUTPUT_DIR / "component_net_png"
COMPONENT_NET_HTML_DIR = OUTPUT_DIR / "component_net_html"
OVERLAY_DIR = OUTPUT_DIR / "overlay"

# =========================================================
# SAVE FLAGS
# =========================================================
SAVE_FULL_PNG = True
SAVE_FULL_HTML = True
SAVE_COMPONENT_NET_PNG = True
SAVE_COMPONENT_NET_HTML = True
SAVE_OVERLAY = True
SAVE_INDEX_HTML = True

# =========================================================
# VIEW OPTIONS
# =========================================================
# Alleggerisce la vista completa: i terminali restano nel grafo ma il testo può stare solo in hover.
SHOW_TERMINAL_LABELS_IN_FULL_PNG = False
SHOW_TERMINAL_LABELS_IN_FULL_HTML = False

# =========================================================
# STYLE CONSTANTS
# =========================================================
NODE_COLORS = {
    "Diagram": "#4C78A8",
    "Component": "#54A24B",
    "Terminal": "#F58518",
    "Net": "#B279A2",
}

EDGE_COLORS = {
    "HAS_COMPONENT": "#BDBDBD",
    "HAS_NET": "#D0D0D0",
    "HAS_TERMINAL": "#B07D62",
    "CONNECTED_TO": "#E45756",
}

LAYER_X = {
    "Diagram": 0.0,
    "Component": 2.0,
    "Terminal": 4.0,
    "Net": 6.0,
}

REL_POS_ORDER = {
    "top": 0,
    "left": 1,
    "right": 2,
    "bottom": 3,
}


# =========================================================
# IO / UTILITY
# =========================================================
def load_graph_json(path: Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def short_diagram_name(diagram_id: str) -> str:
    if "_png" in diagram_id:
        return diagram_id.split("_png", 1)[0]
    if ".png" in diagram_id:
        return diagram_id.split(".png", 1)[0]
    return diagram_id[:24]

def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default

def bbox_center(node: dict[str, Any]) -> tuple[float, float]:
    x1 = safe_float(node.get("bbox_x1"), 0.0)
    y1 = safe_float(node.get("bbox_y1"), 0.0)
    x2 = safe_float(node.get("bbox_x2"), x1)
    y2 = safe_float(node.get("bbox_y2"), y1)
    return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)

# =========================================================
# hover / labels / sorting
# =========================================================
def make_node_hover(node: dict[str, Any]) -> str:
    keys = [
        "node_type",
        "label",
        "class_name",
        "instance_id",
        "terminal_id",
        "net_id",
        "matched_net_id",
        "match_confidence",
        "is_suspicious_match",
        "estimated_orientation",
        "relative_position",
        "search_stage",
        "search_kind",
    ]
    parts = [f"<b>{node.get('node_id')}</b>"]
    for key in keys:
        value = node.get(key)
        if value is not None and value != "":
            parts.append(f"{key}: {value}")
    warnings = node.get("match_warnings")
    if warnings:
        parts.append("match_warnings: " + ", ".join(map(str, warnings)))
    return "<br>".join(parts)

def make_edge_hover(edge: dict[str, Any]) -> str:
    keys = [
        "relation_type",
        "source",
        "target",
        "match_status",
        "match_confidence",
        "is_suspicious_match",
        "match_distance_px",
        "terminal_id",
        "net_id",
    ]
    parts: list[str] = []
    for key in keys:
        value = edge.get(key)
        if value is not None and value != "":
            parts.append(f"{key}: {value}")
    warnings = edge.get("match_warnings")
    if warnings:
        parts.append("match_warnings: " + ", ".join(map(str, warnings)))
    return "<br>".join(parts)


def compact_node_label(node: dict[str, Any], *, show_terminal_labels: bool) -> str:
    node_type = node.get("node_type")
    if node_type == "Diagram":
        return short_diagram_name(str(node.get("diagram_id", node.get("label", "diagram"))))
    if node_type == "Component":
        class_name = str(node.get("class_name", "Component"))
        instance_id = str(node.get("instance_id", node.get("label", "")))
        return f"{instance_id}\n{class_name}"
    if node_type == "Terminal":
        return str(node.get("terminal_id", "")) if show_terminal_labels else ""
    if node_type == "Net":
        return str(node.get("net_id", node.get("label", "net")))
    return str(node.get("label", node.get("node_id", "node")))

def sort_components_spatial(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(nodes, key=lambda n: (bbox_center(n)[1], bbox_center(n)[0], str(n.get("instance_id", ""))))

def sort_nets(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(nodes, key=lambda n: (safe_float(n.get("net_index"), 9999.0), str(n.get("net_id", ""))))

def sort_terminals(nodes: list[dict[str, Any]], component_order: dict[str, int]) -> list[dict[str, Any]]:
    def key(n: dict[str, Any]) -> tuple[Any, ...]:
        instance_id = str(n.get("instance_id", ""))
        rel_pos = str(n.get("relative_position", ""))
        return (
            component_order.get(instance_id, 9999),
            REL_POS_ORDER.get(rel_pos, 99),
            str(n.get("terminal_id", "")),
        )

    return sorted(nodes, key=key)


# =========================================================
# graph preparation
# =========================================================
def build_nx_graph(graph_data: dict[str, Any]) -> nx.DiGraph:
    G = nx.DiGraph()
    for node in graph_data["nodes"]:
        G.add_node(node["node_id"], **node)
    for edge in graph_data["edges"]:
        G.add_edge(edge["source"], edge["target"], **edge)
    return G

def compute_layered_positions(graph_data: dict[str, Any]) -> dict[str, tuple[float, float]]:
    by_type: dict[str, list[dict[str, Any]]] = {
        "Diagram": [],
        "Component": [],
        "Terminal": [],
        "Net": [],
    }
    for node in graph_data["nodes"]:
        by_type.setdefault(node.get("node_type", "Other"), []).append(node)

    component_nodes = sort_components_spatial(by_type.get("Component", []))
    component_order = {str(n.get("instance_id", "")): i for i, n in enumerate(component_nodes)}
    terminal_nodes = sort_terminals(by_type.get("Terminal", []), component_order)
    net_nodes = sort_nets(by_type.get("Net", []))
    diagram_nodes = by_type.get("Diagram", [])

    ordered = {
        "Diagram": diagram_nodes,
        "Component": component_nodes,
        "Terminal": terminal_nodes,
        "Net": net_nodes,
    }

    positions: dict[str, tuple[float, float]] = {}
    for node_type, nodes in ordered.items():
        if not nodes:
            continue
        x = LAYER_X.get(node_type, 8.0)
        n = len(nodes)
        if n == 1:
            ys = [0.0]
        else:
            spacing = 1.18 if node_type == "Terminal" else 1.35
            start = (n - 1) * spacing / 2.0
            ys = [start - i * spacing for i in range(n)]
        for node, y in zip(nodes, ys):
            positions[node["node_id"]] = (x, y)
    return positions

def derive_component_net_graph(graph_data: dict[str, Any]) -> dict[str, Any]:
    component_nodes = [n for n in graph_data["nodes"] if n.get("node_type") == "Component"]
    net_nodes = [n for n in graph_data["nodes"] if n.get("node_type") == "Net"]
    component_lookup = {str(n.get("instance_id")): n for n in component_nodes}
    net_lookup = {str(n.get("net_id")): n for n in net_nodes}

    edge_groups: dict[tuple[str, str], dict[str, Any]] = {}
    for edge in graph_data["edges"]:
        if edge.get("relation_type") != "CONNECTED_TO":
            continue
        source = str(edge.get("source", ""))
        if ":" not in source:
            continue
        # source is terminal:<diagram_id>:<instance_id>:tX
        parts = source.split(":")
        if len(parts) < 4:
            continue
        instance_id = parts[-2]
        net_id = str(edge.get("net_id", ""))
        key = (instance_id, net_id)
        payload = edge_groups.setdefault(
            key,
            {
                "instance_id": instance_id,
                "net_id": net_id,
                "terminal_ids": [],
                "has_suspicious": False,
                "confidences": [],
            },
        )
        term_id = edge.get("terminal_id")
        if term_id:
            payload["terminal_ids"].append(term_id)
        if edge.get("is_suspicious_match", False):
            payload["has_suspicious"] = True
        conf = edge.get("match_confidence")
        if conf:
            payload["confidences"].append(conf)

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    for comp in component_nodes:
        comp_copy = dict(comp)
        comp_copy["viz_node_type"] = "Component"
        nodes.append(comp_copy)
    for net in net_nodes:
        net_copy = dict(net)
        net_copy["viz_node_type"] = "Net"
        nodes.append(net_copy)

    for i, ((instance_id, net_id), payload) in enumerate(sorted(edge_groups.items()), start=1):
        comp = component_lookup.get(instance_id)
        net = net_lookup.get(net_id)
        if comp is None or net is None:
            continue
        edges.append(
            {
                "edge_id": f"component_net:{i}",
                "source": comp["node_id"],
                "target": net["node_id"],
                "relation_type": "COMPONENT_TO_NET",
                "instance_id": instance_id,
                "net_id": net_id,
                "n_terminals": len(payload["terminal_ids"]),
                "terminal_ids": sorted(payload["terminal_ids"]),
                "is_suspicious_match": payload["has_suspicious"],
                "match_confidences": sorted(set(payload["confidences"])),
            }
        )

    return {
        "graph_metadata": graph_data.get("graph_metadata", {}),
        "graph_summary": graph_data.get("graph_summary", {}),
        "nodes": nodes,
        "edges": edges,
    }

def compute_component_net_positions(graph_data: dict[str, Any]) -> dict[str, tuple[float, float]]:
    components = sort_components_spatial([n for n in graph_data["nodes"] if n.get("viz_node_type") == "Component"])
    nets = sort_nets([n for n in graph_data["nodes"] if n.get("viz_node_type") == "Net"])

    positions: dict[str, tuple[float, float]] = {}
    for x, nodes in [(0.0, components), (3.2, nets)]:
        if not nodes:
            continue
        n = len(nodes)
        if n == 1:
            ys = [0.0]
        else:
            spacing = 1.45
            start = (n - 1) * spacing / 2.0
            ys = [start - i * spacing for i in range(n)]
        for node, y in zip(nodes, ys):
            positions[node["node_id"]] = (x, y)
    return positions


# =========================================================
# RNDERING FULL GRAPH - PNG / HTML
# =========================================================
def draw_full_png(graph_data: dict[str, Any], out_png: Path) -> None:
    G = build_nx_graph(graph_data)
    pos = compute_layered_positions(graph_data)

    fig_h = max(8, 0.36 * max(len(graph_data["nodes"]), 12))
    fig, ax = plt.subplots(figsize=(16, fig_h))

    for u, v, data in G.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        relation = data.get("relation_type")
        color = EDGE_COLORS.get(relation, "#999999")
        alpha = 0.45 if relation in {"HAS_COMPONENT", "HAS_NET", "HAS_TERMINAL"} else 0.9
        width = 1.2 if relation in {"HAS_COMPONENT", "HAS_NET"} else 1.5 if relation == "HAS_TERMINAL" else 2.2
        style = "-"
        if relation == "CONNECTED_TO" and data.get("is_suspicious_match"):
            color = "#D62728"
            width = 2.8
            style = "--"
        ax.plot([x0, x1], [y0, y1], color=color, linewidth=width, alpha=alpha, linestyle=style, zorder=1)

    for node_type in ["Diagram", "Component", "Terminal", "Net"]:
        nodes = [n for n, attrs in G.nodes(data=True) if attrs.get("node_type") == node_type]
        if not nodes:
            continue
        xs = [pos[n][0] for n in nodes]
        ys = [pos[n][1] for n in nodes]
        size = 900 if node_type == "Diagram" else 520 if node_type == "Component" else 190 if node_type == "Terminal" else 420
        edgecolor = "black"
        linewidth = 1.0
        ax.scatter(xs, ys, s=size, c=NODE_COLORS[node_type], edgecolors=edgecolor, linewidths=linewidth, zorder=2, label=node_type)

    for n, attrs in G.nodes(data=True):
        x, y = pos[n]
        label = compact_node_label(attrs, show_terminal_labels=SHOW_TERMINAL_LABELS_IN_FULL_PNG)
        if not label:
            continue
        fontsize = 8 if attrs.get("node_type") != "Net" else 9
        ax.text(
            x,
            y,
            label,
            ha="center",
            va="center",
            fontsize=fontsize,
            color="black",
            zorder=3,
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8, edgecolor="none"),
        )

    summary = graph_data.get("graph_summary", {})
    diagram_id = graph_data.get("graph_metadata", {}).get("diagram_id", out_png.stem)
    suspicious = summary.get("n_suspicious_terminal_matches", 0)
    ax.set_title(
        f"Full graph - {short_diagram_name(diagram_id)}\n"
        f"nodes={summary.get('n_nodes_total')} | edges={summary.get('n_edges_total')} | suspicious={suspicious}",
        fontsize=14,
    )
    ax.legend(loc="upper right")
    ax.axis("off")
    plt.tight_layout()
    fig.savefig(out_png, dpi=220, bbox_inches="tight")
    plt.close(fig)

def draw_full_html(graph_data: dict[str, Any], out_html: Path) -> None:
    G = build_nx_graph(graph_data)
    pos = compute_layered_positions(graph_data)

    edge_traces: list[go.Scatter] = []
    for relation_type in ["HAS_COMPONENT", "HAS_NET", "HAS_TERMINAL", "CONNECTED_TO"]:
        for suspicious in [False, True]:
            xs, ys = [], []
            width = 1.5 if relation_type in {"HAS_COMPONENT", "HAS_NET"} else 2 if relation_type == "HAS_TERMINAL" else 2.5
            dash = "solid"
            color = EDGE_COLORS.get(relation_type, "#999999")
            opacity = 0.4 if relation_type in {"HAS_COMPONENT", "HAS_NET", "HAS_TERMINAL"} else 0.9
            name = relation_type
            for u, v, data in G.edges(data=True):
                if data.get("relation_type") != relation_type:
                    continue
                is_susp = bool(data.get("is_suspicious_match", False))
                if relation_type != "CONNECTED_TO" and suspicious:
                    continue
                if relation_type == "CONNECTED_TO" and is_susp != suspicious:
                    continue
                x0, y0 = pos[u]
                x1, y1 = pos[v]
                xs.extend([x0, x1, None])
                ys.extend([y0, y1, None])
                if relation_type == "CONNECTED_TO" and is_susp:
                    color = "#D62728"
                    dash = "dash"
                    width = 3
                    name = "CONNECTED_TO (suspicious)"
                    opacity = 1.0
            if xs:
                edge_traces.append(
                    go.Scatter(
                        x=xs,
                        y=ys,
                        mode="lines",
                        line=dict(color=color, width=width, dash=dash),
                        opacity=opacity,
                        hoverinfo="skip",
                        name=name,
                        showlegend=True,
                    )
                )

    node_traces: list[go.Scatter] = []
    for node_type in ["Diagram", "Component", "Terminal", "Net"]:
        nodes = [(n, attrs) for n, attrs in G.nodes(data=True) if attrs.get("node_type") == node_type]
        if not nodes:
            continue
        xs = [pos[n][0] for n, _ in nodes]
        ys = [pos[n][1] for n, _ in nodes]
        text = [compact_node_label(attrs, show_terminal_labels=SHOW_TERMINAL_LABELS_IN_FULL_HTML) for _, attrs in nodes]
        hover = [make_node_hover(attrs) for _, attrs in nodes]
        size = 34 if node_type == "Diagram" else 24 if node_type == "Component" else 14 if node_type == "Terminal" else 24
        node_traces.append(
            go.Scatter(
                x=xs,
                y=ys,
                mode="markers+text",
                text=text,
                textposition="middle center",
                hovertext=hover,
                hoverinfo="text",
                marker=dict(size=size, color=NODE_COLORS[node_type], line=dict(color="black", width=1)),
                name=node_type,
            )
        )

    summary = graph_data.get("graph_summary", {})
    meta = graph_data.get("graph_metadata", {})
    diagram_id = meta.get("diagram_id", out_html.stem)
    suspicious = summary.get("n_suspicious_terminal_matches", 0)

    fig = go.Figure(data=edge_traces + node_traces)
    fig.update_layout(
        title=(
            f"Full graph - {short_diagram_name(diagram_id)}<br>"
            f"<sup>nodes={summary.get('n_nodes_total')} | edges={summary.get('n_edges_total')} | suspicious={suspicious}</sup>"
        ),
        template="plotly_white",
        showlegend=True,
        hovermode="closest",
        margin=dict(l=20, r=20, t=80, b=20),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    fig.write_html(str(out_html), include_plotlyjs="cdn")


# =========================================================
# RENDERING COMPONENT -> NET VIEW
# =========================================================
def draw_component_net_png(graph_data: dict[str, Any], out_png: Path) -> None:
    simple = derive_component_net_graph(graph_data)
    G = nx.Graph()
    for node in simple["nodes"]:
        G.add_node(node["node_id"], **node)
    for edge in simple["edges"]:
        G.add_edge(edge["source"], edge["target"], **edge)
    pos = compute_component_net_positions(simple)

    fig_h = max(8, 0.34 * max(len(simple["nodes"]), 10))
    fig, ax = plt.subplots(figsize=(13, fig_h))

    for u, v, data in G.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        color = "#E45756" if data.get("is_suspicious_match") else "#7A7A7A"
        width = 2.8 if data.get("is_suspicious_match") else 1.8
        style = "--" if data.get("is_suspicious_match") else "-"
        ax.plot([x0, x1], [y0, y1], color=color, linewidth=width, linestyle=style, alpha=0.9, zorder=1)

    for viz_type in ["Component", "Net"]:
        nodes = [n for n, attrs in G.nodes(data=True) if attrs.get("viz_node_type") == viz_type]
        if not nodes:
            continue
        xs = [pos[n][0] for n in nodes]
        ys = [pos[n][1] for n in nodes]
        color = NODE_COLORS[viz_type]
        size = 650 if viz_type == "Component" else 460
        ax.scatter(xs, ys, s=size, c=color, edgecolors="black", linewidths=1.0, zorder=2, label=viz_type)

    for n, attrs in G.nodes(data=True):
        x, y = pos[n]
        if attrs.get("viz_node_type") == "Component":
            label = f"{attrs.get('instance_id')}\n{attrs.get('class_name')}"
        else:
            label = str(attrs.get("net_id", attrs.get("label", "Net")))
        ax.text(
            x,
            y,
            label,
            ha="center",
            va="center",
            fontsize=9,
            bbox=dict(boxstyle="round,pad=0.22", facecolor="white", alpha=0.85, edgecolor="none"),
            zorder=3,
        )

    meta = graph_data.get("graph_metadata", {})
    diagram_id = meta.get("diagram_id", out_png.stem)
    ax.set_title(f"Component-Net view - {short_diagram_name(diagram_id)}", fontsize=14)
    ax.legend(loc="upper right")
    ax.axis("off")
    plt.tight_layout()
    fig.savefig(out_png, dpi=220, bbox_inches="tight")
    plt.close(fig)

def draw_component_net_html(graph_data: dict[str, Any], out_html: Path) -> None:
    simple = derive_component_net_graph(graph_data)
    G = nx.Graph()
    for node in simple["nodes"]:
        G.add_node(node["node_id"], **node)
    for edge in simple["edges"]:
        G.add_edge(edge["source"], edge["target"], **edge)
    pos = compute_component_net_positions(simple)

    edge_traces: list[go.Scatter] = []
    for suspicious in [False, True]:
        xs, ys = [], []
        name = "COMPONENT_TO_NET"
        color = "#7A7A7A"
        dash = "solid"
        width = 2
        opacity = 0.75
        for u, v, data in G.edges(data=True):
            is_susp = bool(data.get("is_suspicious_match", False))
            if is_susp != suspicious:
                continue
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            xs.extend([x0, x1, None])
            ys.extend([y0, y1, None])
            if is_susp:
                name = "COMPONENT_TO_NET (suspicious)"
                color = "#D62728"
                dash = "dash"
                width = 3
                opacity = 1.0
        if xs:
            edge_traces.append(
                go.Scatter(
                    x=xs,
                    y=ys,
                    mode="lines",
                    line=dict(color=color, width=width, dash=dash),
                    opacity=opacity,
                    hoverinfo="skip",
                    name=name,
                    showlegend=True,
                )
            )

    node_traces: list[go.Scatter] = []
    for viz_type in ["Component", "Net"]:
        nodes = [(n, attrs) for n, attrs in G.nodes(data=True) if attrs.get("viz_node_type") == viz_type]
        if not nodes:
            continue
        xs = [pos[n][0] for n, _ in nodes]
        ys = [pos[n][1] for n, _ in nodes]
        if viz_type == "Component":
            text = [f"{attrs.get('instance_id')}<br>{attrs.get('class_name')}" for _, attrs in nodes]
        else:
            text = [str(attrs.get("net_id", attrs.get("label", "Net"))) for _, attrs in nodes]
        hover = [make_node_hover(attrs) for _, attrs in nodes]
        size = 26 if viz_type == "Component" else 24
        node_traces.append(
            go.Scatter(
                x=xs,
                y=ys,
                mode="markers+text",
                text=text,
                textposition="middle center",
                hovertext=hover,
                hoverinfo="text",
                marker=dict(size=size, color=NODE_COLORS[viz_type], line=dict(color="black", width=1)),
                name=viz_type,
            )
        )

    meta = graph_data.get("graph_metadata", {})
    diagram_id = meta.get("diagram_id", out_html.stem)
    fig = go.Figure(data=edge_traces + node_traces)
    fig.update_layout(
        title=f"Component-Net view - {short_diagram_name(diagram_id)}",
        template="plotly_white",
        showlegend=True,
        hovermode="closest",
        margin=dict(l=20, r=20, t=80, b=20),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    fig.write_html(str(out_html), include_plotlyjs="cdn")


# =========================================================
# REDENRING OVERLAY SUL DIAGRAMMA
# =========================================================
def draw_overlay(graph_data: dict[str, Any], out_png: Path) -> None:
    meta = graph_data.get("graph_metadata", {})
    image_path = meta.get("image_path")
    if not image_path:
        return

    image_file = Path(image_path)
    if not image_file.exists():
        return

    img = plt.imread(str(image_file))
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(img)

    # Componenti: bbox + label
    for node in graph_data["nodes"]:
        if node.get("node_type") != "Component":
            continue
        x1 = safe_float(node.get("bbox_x1"))
        y1 = safe_float(node.get("bbox_y1"))
        x2 = safe_float(node.get("bbox_x2"))
        y2 = safe_float(node.get("bbox_y2"))
        w = max(1.0, x2 - x1)
        h = max(1.0, y2 - y1)
        rect = plt.Rectangle((x1, y1), w, h, fill=False, linewidth=1.4, edgecolor="#00A651", alpha=0.9)
        ax.add_patch(rect)
        ax.text(
            x1,
            max(6.0, y1 - 6.0),
            f"{node.get('instance_id')} {node.get('class_name')}",
            fontsize=7,
            color="#006D2C",
            bbox=dict(boxstyle="round,pad=0.18", facecolor="white", alpha=0.7, edgecolor="none"),
        )

    # Net: usa il bbox della net se presente, altrimenti il centro medio degli snap point.
    net_centers: dict[str, tuple[float, float]] = {}
    for node in graph_data["nodes"]:
        if node.get("node_type") != "Net":
            continue
        x1 = node.get("bbox_x1")
        y1 = node.get("bbox_y1")
        x2 = node.get("bbox_x2")
        y2 = node.get("bbox_y2")
        if None not in (x1, y1, x2, y2):
            cx, cy = bbox_center(node)
            net_centers[str(node.get("net_id"))] = (cx, cy)

    if not net_centers:
        grouped: dict[str, list[tuple[float, float]]] = {}
        for node in graph_data["nodes"]:
            if node.get("node_type") != "Terminal":
                continue
            net_id = node.get("matched_net_id")
            sx = node.get("snap_x")
            sy = node.get("snap_y")
            if net_id is None or sx is None or sy is None:
                continue
            grouped.setdefault(str(net_id), []).append((safe_float(sx), safe_float(sy)))
        for net_id, pts in grouped.items():
            if pts:
                cx = sum(p[0] for p in pts) / len(pts)
                cy = sum(p[1] for p in pts) / len(pts)
                net_centers[net_id] = (cx, cy)

    for net_id, (cx, cy) in net_centers.items():
        ax.scatter([cx], [cy], s=50, c="#B279A2", edgecolors="black", linewidths=0.8, zorder=4)
        ax.text(
            cx + 6,
            cy - 6,
            net_id,
            fontsize=8,
            color="#7A2E8A",
            bbox=dict(boxstyle="round,pad=0.18", facecolor="white", alpha=0.8, edgecolor="none"),
            zorder=5,
        )

    # Terminali: punto + linea verso la net.
    for node in graph_data["nodes"]:
        if node.get("node_type") != "Terminal":
            continue
        x = node.get("x")
        y = node.get("y")
        net_id = node.get("matched_net_id")
        if x is None or y is None:
            continue
        suspicious = bool(node.get("is_suspicious_match", False))
        color = "#D62728" if suspicious else "#00BFC4"
        ax.scatter([x], [y], s=18, c=color, edgecolors="white", linewidths=0.6, zorder=6)
        if net_id in net_centers:
            cx, cy = net_centers[net_id]
            ax.plot([x, cx], [y, cy], color=color, linewidth=0.7 if not suspicious else 1.0, alpha=0.35, zorder=3)

    diagram_id = meta.get("diagram_id", out_png.stem)
    ax.set_title(f"Overlay graph elements - {short_diagram_name(diagram_id)}")
    ax.axis("off")
    plt.tight_layout()
    fig.savefig(out_png, dpi=220, bbox_inches="tight")
    plt.close(fig)


# =========================================================
# DASHBOARD INDEX HTML
# =========================================================
def save_index_html(index_rows: list[dict[str, Any]], out_path: Path) -> None:
    rows_sorted = sorted(
        index_rows,
        key=lambda r: (
            -int(r.get("n_suspicious_terminal_matches", 0)),
            str(r.get("diagram_id", "")),
        ),
    )

    total_diagrams = len(rows_sorted)
    total_nodes = sum(int(r.get("n_nodes_total", 0)) for r in rows_sorted)
    total_edges = sum(int(r.get("n_edges_total", 0)) for r in rows_sorted)
    total_suspicious = sum(int(r.get("n_suspicious_terminal_matches", 0)) for r in rows_sorted)
    diagrams_with_suspicious = sum(1 for r in rows_sorted if int(r.get("n_suspicious_terminal_matches", 0)) > 0)

    cards_html: list[str] = []
    for row in rows_sorted:
        diagram_id = str(row.get("diagram_id", ""))
        short_name = short_diagram_name(diagram_id)
        suspicious = int(row.get("n_suspicious_terminal_matches", 0))
        suspicious_badge = (
            f'<span class="badge badge-warn">{suspicious} suspicious</span>'
            if suspicious > 0 else
            '<span class="badge badge-ok">clean</span>'
        )

        def link(label: str, href: str | None, cls: str = "") -> str:
            if not href:
                return f'<span class="action disabled {cls}">{label}</span>'
            return f'<a class="action {cls}" href="{href}" target="_blank" rel="noopener">{label}</a>'

        full_png_rel = f"full_png/{row['full_png']}" if row.get("full_png") else None
        full_html_rel = f"full_html/{row['full_html']}" if row.get("full_html") else None
        component_png_rel = f"component_net_png/{row['component_net_png']}" if row.get("component_net_png") else None
        component_html_rel = f"component_net_html/{row['component_net_html']}" if row.get("component_net_html") else None
        overlay_png_rel = f"overlay/{row['overlay_png']}" if row.get("overlay_png") else None

        preview_rel = component_png_rel or overlay_png_rel or full_png_rel
        preview_html = (
            f'<a class="preview-link" href="{preview_rel}" target="_blank" rel="noopener">'
            f'  <img class="preview" src="{preview_rel}" alt="Preview {short_name}" loading="lazy" />'
            f'</a>'
            if preview_rel else
            '<div class="preview preview-empty">No preview</div>'
        )

        cards_html.append(
            f'''            <article class="diagram-card" data-name="{short_name.lower()} {diagram_id.lower()}" data-suspicious="{suspicious}">

              <div class="card-top">

                <div>

                  <div class="card-title-row">

                    <h2>{short_name}</h2>

                    {suspicious_badge}

                  </div>

                  <p class="card-subtitle">{diagram_id}</p>

                </div>

                <div class="metrics-grid">

                  <div class="metric"><span class="metric-value">{row.get('n_nodes_total', 0)}</span><span class="metric-label">nodes</span></div>

                  <div class="metric"><span class="metric-value">{row.get('n_edges_total', 0)}</span><span class="metric-label">edges</span></div>

                  <div class="metric"><span class="metric-value">{suspicious}</span><span class="metric-label">suspicious</span></div>

                </div>

              </div>



              <div class="card-body">

                <div class="preview-wrap">

                  {preview_html}

                </div>



                <div class="actions-wrap">

                  <div class="action-group">

                    <div class="group-title">Full graph</div>

                    <div class="action-row">

                      {link('PNG', full_png_rel)}

                      {link('HTML', full_html_rel, 'primary')}

                    </div>

                  </div>



                  <div class="action-group">

                    <div class="group-title">Component → Net</div>

                    <div class="action-row">

                      {link('PNG', component_png_rel)}

                      {link('HTML', component_html_rel, 'primary')}

                    </div>

                  </div>



                  <div class="action-group">

                    <div class="group-title">Overlay</div>

                    <div class="action-row">

                      {link('PNG', overlay_png_rel)}

                    </div>

                  </div>

                </div>

              </div>

            </article>
'''
        )

    html = f'''<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>08_visualize_graph</title>
  <style>
    :root {{
      --bg: #f6f8fb;
      --card: #ffffff;
      --card-2: #fbfcfe;
      --text: #1f2937;
      --muted: #667085;
      --border: #e5e7eb;
      --shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
      --primary: #2563eb;
      --primary-soft: #dbeafe;
      --ok: #15803d;
      --ok-soft: #dcfce7;
      --warn: #b45309;
      --warn-soft: #fef3c7;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, Arial, sans-serif;
      background: linear-gradient(180deg, #eff4ff 0%, var(--bg) 240px);
      color: var(--text);
    }}
    .page {{ max-width: 1500px; margin: 0 auto; padding: 28px 28px 40px; }}
    .hero {{
      background: rgba(255,255,255,0.88);
      backdrop-filter: blur(8px);
      border: 1px solid rgba(255,255,255,0.7);
      border-radius: 24px;
      padding: 26px 28px;
      box-shadow: var(--shadow);
      margin-bottom: 22px;
    }}
    .eyebrow {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      border-radius: 999px;
      background: var(--primary-soft);
      color: var(--primary);
      font-weight: 700;
      font-size: 13px;
      margin-bottom: 12px;
    }}
    h1 {{ margin: 0 0 8px; font-size: 32px; line-height: 1.1; }}
    .hero p {{ margin: 0; color: var(--muted); max-width: 980px; line-height: 1.55; }}

    .summary-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 14px;
      margin: 18px 0 0;
    }}
    .summary-card {{
      background: linear-gradient(180deg, var(--card) 0%, var(--card-2) 100%);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 16px 18px;
    }}
    .summary-value {{ display: block; font-size: 28px; font-weight: 800; line-height: 1; margin-bottom: 8px; }}
    .summary-label {{ color: var(--muted); font-size: 13px; text-transform: uppercase; letter-spacing: .04em; }}

    .toolbar {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
      justify-content: space-between;
      background: rgba(255,255,255,0.88);
      border: 1px solid rgba(255,255,255,0.7);
      border-radius: 20px;
      padding: 14px 16px;
      box-shadow: var(--shadow);
      margin-bottom: 18px;
      position: sticky;
      top: 12px;
      z-index: 5;
    }}
    .toolbar-left {{ display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }}
    .toolbar-right {{ color: var(--muted); font-size: 14px; }}
    input[type="search"] {{
      width: min(360px, 70vw);
      padding: 12px 14px;
      border-radius: 12px;
      border: 1px solid var(--border);
      font-size: 14px;
      background: white;
    }}
    .check {{ display: inline-flex; gap: 8px; align-items: center; color: var(--text); font-size: 14px; }}

    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(460px, 1fr));
      gap: 18px;
    }}
    .diagram-card {{
      background: rgba(255,255,255,0.92);
      border: 1px solid rgba(255,255,255,0.75);
      border-radius: 22px;
      box-shadow: var(--shadow);
      padding: 18px;
    }}
    .card-top {{ display: flex; gap: 16px; align-items: flex-start; justify-content: space-between; margin-bottom: 16px; }}
    .card-title-row {{ display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }}
    .card-title-row h2 {{ margin: 0; font-size: 22px; line-height: 1.1; }}
    .card-subtitle {{ margin: 8px 0 0; font-size: 13px; color: var(--muted); word-break: break-all; }}

    .badge {{ display: inline-flex; align-items: center; padding: 6px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; }}
    .badge-ok {{ background: var(--ok-soft); color: var(--ok); }}
    .badge-warn {{ background: var(--warn-soft); color: var(--warn); }}

    .metrics-grid {{ display: grid; grid-template-columns: repeat(3, minmax(72px, 1fr)); gap: 10px; min-width: 250px; }}
    .metric {{ background: #f8fafc; border: 1px solid var(--border); border-radius: 16px; padding: 12px 10px; text-align: center; }}
    .metric-value {{ display: block; font-size: 20px; font-weight: 800; }}
    .metric-label {{ display: block; margin-top: 4px; color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .04em; }}

    .card-body {{ display: grid; grid-template-columns: 1.15fr 1fr; gap: 16px; align-items: start; }}
    .preview-wrap {{ background: #f8fafc; border: 1px solid var(--border); border-radius: 18px; padding: 10px; min-height: 250px; display: flex; align-items: center; justify-content: center; }}
    .preview-link {{ display: block; width: 100%; }}
    .preview {{ width: 100%; max-height: 280px; object-fit: contain; border-radius: 12px; display: block; }}
    .preview-empty {{ color: var(--muted); font-size: 14px; }}

    .actions-wrap {{ display: flex; flex-direction: column; gap: 12px; }}
    .action-group {{ background: #f8fafc; border: 1px solid var(--border); border-radius: 18px; padding: 14px; }}
    .group-title {{ font-size: 14px; font-weight: 700; margin-bottom: 10px; }}
    .action-row {{ display: flex; flex-wrap: wrap; gap: 10px; }}
    .action {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 86px;
      padding: 10px 12px;
      border-radius: 12px;
      border: 1px solid var(--border);
      background: white;
      color: var(--text);
      text-decoration: none;
      font-weight: 600;
      font-size: 14px;
      transition: transform .12s ease, box-shadow .12s ease, border-color .12s ease;
    }}
    .action:hover {{ transform: translateY(-1px); box-shadow: 0 8px 18px rgba(15,23,42,.08); border-color: #cbd5e1; }}
    .action.primary {{ background: var(--primary); border-color: var(--primary); color: white; }}
    .action.disabled {{ opacity: .45; pointer-events: none; }}

    .empty {{
      display: none;
      padding: 30px 20px;
      text-align: center;
      color: var(--muted);
      background: rgba(255,255,255,0.85);
      border: 1px dashed var(--border);
      border-radius: 18px;
      margin-top: 18px;
    }}

    @media (max-width: 980px) {{
      .cards {{ grid-template-columns: 1fr; }}
      .card-body {{ grid-template-columns: 1fr; }}
      .metrics-grid {{ min-width: 0; width: 100%; }}
      .card-top {{ flex-direction: column; }}
    }}
  </style>
</head>
<body>
  <main class="page">
    <section class="hero">
      <div class="eyebrow">08_visualize_graph · browser dashboard</div>
      <h1>Graph visualization index</h1>
      <p>
        Dashboard delle visualizzazioni generate a partire dai file <code>*_graph.json</code> prodotti dal passo 07.
        Per ogni diagramma sono disponibili la <b>vista completa</b>, la <b>vista semplificata Component → Net</b>
        e l'<b>overlay sul diagramma originale</b>. La preview usa, quando disponibile, la vista Component → Net.
      </p>
      <div class="summary-grid">
        <div class="summary-card"><span class="summary-value">{total_diagrams}</span><span class="summary-label">diagrammi</span></div>
        <div class="summary-card"><span class="summary-value">{total_nodes}</span><span class="summary-label">nodi totali</span></div>
        <div class="summary-card"><span class="summary-value">{total_edges}</span><span class="summary-label">archi totali</span></div>
        <div class="summary-card"><span class="summary-value">{total_suspicious}</span><span class="summary-label">match sospetti totali</span></div>
        <div class="summary-card"><span class="summary-value">{diagrams_with_suspicious}</span><span class="summary-label">diagrammi con criticità</span></div>
      </div>
    </section>

    <section class="toolbar">
      <div class="toolbar-left">
        <input id="searchBox" type="search" placeholder="Cerca diagramma, id, nome corto..." />
        <label class="check"><input id="onlySuspicious" type="checkbox" /> Mostra solo diagrammi con suspicious &gt; 0</label>
      </div>
      <div class="toolbar-right">Risultati visibili: <span id="visibleCount">0</span></div>
    </section>

    <section id="cards" class="cards">
      {''.join(cards_html)}
    </section>

    <div id="emptyState" class="empty">Nessun diagramma corrisponde ai filtri selezionati.</div>
  </main>

  <script>
    const searchBox = document.getElementById('searchBox');
    const onlySuspicious = document.getElementById('onlySuspicious');
    const cards = Array.from(document.querySelectorAll('.diagram-card'));
    const visibleCount = document.getElementById('visibleCount');
    const emptyState = document.getElementById('emptyState');

    function applyFilters() {{
      const query = searchBox.value.trim().toLowerCase();
      const suspiciousOnly = onlySuspicious.checked;
      let visible = 0;

      for (const card of cards) {{
        const haystack = card.dataset.name || '';
        const suspicious = Number(card.dataset.suspicious || '0');
        const matchesText = !query || haystack.includes(query);
        const matchesSuspicious = !suspiciousOnly || suspicious > 0;
        const show = matchesText && matchesSuspicious;
        card.style.display = show ? '' : 'none';
        if (show) visible += 1;
      }}

      visibleCount.textContent = String(visible);
      emptyState.style.display = visible === 0 ? 'block' : 'none';
    }}

    searchBox.addEventListener('input', applyFilters);
    onlySuspicious.addEventListener('change', applyFilters);
    applyFilters();
  </script>
</body>
</html>
'''
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

# =========================================================
# MAIN
# =========================================================
def main() -> None:
    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"Cartella input non trovata: {INPUT_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if SAVE_FULL_PNG:
        FULL_PNG_DIR.mkdir(parents=True, exist_ok=True)
    if SAVE_FULL_HTML:
        FULL_HTML_DIR.mkdir(parents=True, exist_ok=True)
    if SAVE_COMPONENT_NET_PNG:
        COMPONENT_NET_PNG_DIR.mkdir(parents=True, exist_ok=True)
    if SAVE_COMPONENT_NET_HTML:
        COMPONENT_NET_HTML_DIR.mkdir(parents=True, exist_ok=True)
    if SAVE_OVERLAY:
        OVERLAY_DIR.mkdir(parents=True, exist_ok=True)

    json_files = sorted(INPUT_DIR.glob("*_graph.json"))
    if not json_files:
        raise FileNotFoundError(f"Nessun file *_graph.json trovato in: {INPUT_DIR}")

    print(f"Input directory : {INPUT_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"File trovati    : {len(json_files)}\\n")

    index_rows: list[dict[str, Any]] = []

    for i, json_path in enumerate(json_files, start=1):
        graph_data = load_graph_json(json_path)
        summary = graph_data.get("graph_summary", {})
        diagram_id = graph_data.get("graph_metadata", {}).get("diagram_id", json_path.stem.replace("_graph", ""))

        full_png_name = f"{diagram_id}_full_graph.png"
        full_html_name = f"{diagram_id}_full_graph.html"
        component_net_png_name = f"{diagram_id}_component_net.png"
        component_net_html_name = f"{diagram_id}_component_net.html"
        overlay_png_name = f"{diagram_id}_overlay.png"

        if SAVE_FULL_PNG:
            draw_full_png(graph_data, FULL_PNG_DIR / full_png_name)
        if SAVE_FULL_HTML:
            draw_full_html(graph_data, FULL_HTML_DIR / full_html_name)
        if SAVE_COMPONENT_NET_PNG:
            draw_component_net_png(graph_data, COMPONENT_NET_PNG_DIR / component_net_png_name)
        if SAVE_COMPONENT_NET_HTML:
            draw_component_net_html(graph_data, COMPONENT_NET_HTML_DIR / component_net_html_name)
        if SAVE_OVERLAY:
            draw_overlay(graph_data, OVERLAY_DIR / overlay_png_name)

        index_rows.append(
            {
                "diagram_id": diagram_id,
                "n_nodes_total": summary.get("n_nodes_total", 0),
                "n_edges_total": summary.get("n_edges_total", 0),
                "n_suspicious_terminal_matches": summary.get("n_suspicious_terminal_matches", 0),
                "full_png": full_png_name if SAVE_FULL_PNG else None,
                "full_html": full_html_name if SAVE_FULL_HTML else None,
                "component_net_png": component_net_png_name if SAVE_COMPONENT_NET_PNG else None,
                "component_net_html": component_net_html_name if SAVE_COMPONENT_NET_HTML else None,
                "overlay_png": overlay_png_name if SAVE_OVERLAY else None,
            }
        )

        print(
            f"[{i}/{len(json_files)}] {json_path.name} -> "
            f"nodes={summary.get('n_nodes_total')}, edges={summary.get('n_edges_total')}, "
            f"suspicious={summary.get('n_suspicious_terminal_matches', 0)}"
        )

    if SAVE_INDEX_HTML:
        index_path = OUTPUT_DIR / "index.html"
        save_index_html(index_rows, index_path)
        print(f"\nIndex HTML salvato in: {index_path}")

    print("\nCompletato.")
    if SAVE_FULL_PNG:
        print(f"Full PNG salvati in         : {FULL_PNG_DIR}")
    if SAVE_FULL_HTML:
        print(f"Full HTML salvati in        : {FULL_HTML_DIR}")
    if SAVE_COMPONENT_NET_PNG:
        print(f"Component-Net PNG salvati in: {COMPONENT_NET_PNG_DIR}")
    if SAVE_COMPONENT_NET_HTML:
        print(f"Component-Net HTML salvati in: {COMPONENT_NET_HTML_DIR}")
    if SAVE_OVERLAY:
        print(f"Overlay PNG salvati in      : {OVERLAY_DIR}")


if __name__ == "__main__":
    main()
