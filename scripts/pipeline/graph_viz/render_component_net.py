from pathlib import Path
from typing import Any
import matplotlib.pyplot as plt
import networkx as nx
import plotly.graph_objects as go

from .config import NODE_COLORS
from .transform import derive_component_net_graph
from .layout import compute_component_net_positions
from .labels import make_node_hover
from .io_utils import short_diagram_name
# =========================================================
# RENDERING COMPONENT -> NET VIEW
# =========================================================
# Draw component net PNG.
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

# Draw component net HTML.
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
