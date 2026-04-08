# =========================================================
# hover / labels / sorting
# =========================================================
from typing import Any

from .config import REL_POS_ORDER
from .io_utils import bbox_center, safe_float, short_diagram_name


def make_node_hover(node: dict[str, Any]) -> str:
    keys = [
        "node_type",
        "label",
        "class_name",
        "component_class_name",
        "instance_id",
        "terminal_id",
        "terminal_name",
        "net_id",
        "matched_net_id",
        "match_confidence",
        "is_suspicious_match",
        "estimated_orientation",
        "relative_position",
        "terminal_point_mode",
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
