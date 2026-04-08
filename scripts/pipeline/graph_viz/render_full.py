from pathlib import Path
from typing import Any
import matplotlib.pyplot as plt
import plotly.graph_objects as go

from .config import NODE_COLORS, EDGE_COLORS, SHOW_TERMINAL_LABELS_IN_FULL_PNG, SHOW_TERMINAL_LABELS_IN_FULL_HTML
from .layout import build_nx_graph, compute_layered_positions
from .labels import compact_node_label, make_node_hover
from .io_utils import short_diagram_name
# =========================================================
# RENDERING FULL GRAPH - PNG / HTML
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