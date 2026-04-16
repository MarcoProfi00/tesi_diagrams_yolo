# =========================================================
# IO / UTILITY
# =========================================================
import json
from pathlib import Path
from typing import Any


# Load graph json.
def load_graph_json(path: Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Handle short diagram name.
def short_diagram_name(diagram_id: str) -> str:
    if "_png" in diagram_id:
        return diagram_id.split("_png", 1)[0]
    if ".png" in diagram_id:
        return diagram_id.split(".png", 1)[0]
    return diagram_id[:24]

# Handle safe float.
def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default

# Handle bounding box center.
def bbox_center(node: dict[str, Any]) -> tuple[float, float]:
    x1 = safe_float(node.get("bbox_x1"), 0.0)
    y1 = safe_float(node.get("bbox_y1"), 0.0)
    x2 = safe_float(node.get("bbox_x2"), x1)
    y2 = safe_float(node.get("bbox_y2"), y1)
    return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)
