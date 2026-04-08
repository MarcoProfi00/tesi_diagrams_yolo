from pathlib import Path
from typing import Any
import matplotlib.pyplot as plt

from .io_utils import safe_float, bbox_center, short_diagram_name


# =========================================================
# RENDERING OVERLAY SUL DIAGRAMMA
# =========================================================

NET_NODE_COLOR = "#B279A2"
NET_NODE_EDGE = "#2F2F2F"
NET_TEXT_COLOR = "#5B2C6F"
NET_TEXT_BOX_FACE = "#FFF2B2"
NET_TEXT_BOX_EDGE = "#6E5A00"
NET_LEADER_COLOR = "#666666"

COMP_BOX_COLOR = "#00A651"
COMP_TEXT_COLOR = "#006D2C"


def terminal_overlay_color(node: dict[str, Any]) -> str:
    if bool(node.get("is_suspicious_match", False)):
        return "#D62728"   # rosso forte

    conf = node.get("match_confidence")

    # nuova logica
    if conf == "ok":
        return "#00A651"
    if conf == "unmatched":
        return "#7F8C8D"

    # compatibilità con vecchie versioni
    if conf == "high":
        return "#00A651"
    if conf == "medium":
        return "#F39C12"
    if conf == "low":
        return "#D62728"

    return "#7F8C8D"


def _label_offset(idx: int) -> tuple[float, float]:
    offsets = [
        (14, -12),
        (14, 12),
        (-34, -12),
        (-34, 12),
        (0, -18),
        (0, 18),
        (24, 0),
        (-24, 0),
    ]
    return offsets[idx % len(offsets)]


def draw_overlay(graph_data: dict[str, Any], out_png: Path) -> None:
    meta = graph_data.get("graph_metadata", {})
    image_path = meta.get("image_path")
    if not image_path:
        return

    image_file = Path(image_path)
    if not image_file.exists():
        return

    img = plt.imread(str(image_file))
    h, w = img.shape[:2]

    fig_w = 11
    fig_h = max(8, fig_w * h / max(w, 1))
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.imshow(img)

    # -----------------------------------------------------
    # Componenti: bbox + label
    # -----------------------------------------------------
    for node in graph_data["nodes"]:
        if node.get("node_type") != "Component":
            continue

        x1 = safe_float(node.get("bbox_x1"))
        y1 = safe_float(node.get("bbox_y1"))
        x2 = safe_float(node.get("bbox_x2"))
        y2 = safe_float(node.get("bbox_y2"))

        w_box = max(1.0, x2 - x1)
        h_box = max(1.0, y2 - y1)

        rect = plt.Rectangle(
            (x1, y1),
            w_box,
            h_box,
            fill=False,
            linewidth=1.6,
            edgecolor=COMP_BOX_COLOR,
            alpha=0.95,
            zorder=2,
        )
        ax.add_patch(rect)

        ax.text(
            x1,
            max(8.0, y1 - 7.0),
            f"{node.get('instance_id')} {node.get('class_name')}",
            fontsize=7,
            color=COMP_TEXT_COLOR,
            bbox=dict(
                boxstyle="round,pad=0.18",
                facecolor="white",
                alpha=0.82,
                edgecolor="none",
            ),
            zorder=3,
        )

    # -----------------------------------------------------
    # Net centers: bbox centro oppure media snap point
    # -----------------------------------------------------
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

    # -----------------------------------------------------
    # Net centers + net labels
    # -----------------------------------------------------
    for idx, (net_id, (cx, cy)) in enumerate(sorted(net_centers.items())):
        # halo bianco
        ax.scatter(
            [cx], [cy],
            s=120,
            c="white",
            edgecolors="white",
            linewidths=2.0,
            zorder=7,
        )

        # nodo principale
        ax.scatter(
            [cx], [cy],
            s=52,
            c=NET_NODE_COLOR,
            edgecolors=NET_NODE_EDGE,
            linewidths=0.8,
            zorder=8,
        )

        dx, dy = _label_offset(idx)
        lx = cx + dx
        ly = cy + dy

        # leader line con halo
        ax.plot(
            [cx, lx],
            [cy, ly],
            color="white",
            linewidth=3.0,
            alpha=0.95,
            zorder=6,
        )
        ax.plot(
            [cx, lx],
            [cy, ly],
            color=NET_LEADER_COLOR,
            linewidth=1.0,
            alpha=0.95,
            zorder=7,
        )

        ha = "left" if dx >= 0 else "right"

        ax.text(
            lx,
            ly,
            net_id,
            fontsize=9,
            fontweight="bold",
            color=NET_TEXT_COLOR,
            ha=ha,
            va="center",
            bbox=dict(
                boxstyle="round,pad=0.22",
                facecolor=NET_TEXT_BOX_FACE,
                edgecolor=NET_TEXT_BOX_EDGE,
                linewidth=0.8,
                alpha=0.98,
            ),
            zorder=9,
        )

    # -----------------------------------------------------
    # Terminali: punto + collegamento verso la net
    # -----------------------------------------------------
    for node in graph_data["nodes"]:
        if node.get("node_type") != "Terminal":
            continue

        x = node.get("x")
        y = node.get("y")
        net_id = node.get("matched_net_id")

        if x is None or y is None:
            continue

        x = safe_float(x)
        y = safe_float(y)

        suspicious = bool(node.get("is_suspicious_match", False))
        color = terminal_overlay_color(node)

        # punto terminale con halo
        ax.scatter(
            [x], [y],
            s=34,
            c="white",
            edgecolors="white",
            linewidths=1.4,
            zorder=10,
        )
        ax.scatter(
            [x], [y],
            s=16,
            c=color,
            edgecolors="#222222",
            linewidths=0.5,
            zorder=11,
        )

        if net_id in net_centers:
            cx, cy = net_centers[net_id]

            # halo sotto
            ax.plot(
                [x, cx],
                [y, cy],
                color="white",
                linewidth=2.8 if not suspicious else 3.2,
                alpha=0.92,
                zorder=4,
            )

            # linea vera sopra
            ax.plot(
                [x, cx],
                [y, cy],
                color=color,
                linewidth=1.2 if not suspicious else 1.8,
                alpha=0.85,
                zorder=5,
            )

    diagram_id = meta.get("diagram_id", out_png.stem)
    ax.set_title(f"Overlay graph elements - {short_diagram_name(diagram_id)}")
    ax.axis("off")

    plt.tight_layout()
    fig.savefig(out_png, dpi=260, bbox_inches="tight")
    plt.close(fig)