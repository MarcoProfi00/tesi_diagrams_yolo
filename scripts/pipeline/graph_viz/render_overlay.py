from pathlib import Path
from typing import Any
import matplotlib.pyplot as plt

from .io_utils import safe_float, bbox_center, short_diagram_name
# =========================================================
# REDENRING OVERLAY SUL DIAGRAMMA
# =========================================================
def terminal_overlay_color(node: dict[str, Any]) -> str:
    if bool(node.get("is_suspicious_match", False)):
        return "#D62728"   # rosso forte

    conf = node.get("match_confidence")
    if conf == "high":
        return "#00A651"   # verde
    if conf == "medium":
        return "#F39C12"   # arancio
    if conf == "low":
        return "#D62728"   # rosso
    return "#7F8C8D"       # grigio

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
        color = terminal_overlay_color(node)
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