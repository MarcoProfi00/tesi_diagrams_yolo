import numpy as np

from .config import (
    MOSFET_GATE_SUPPLY_ALIGN_Y_TOL,
    SUPPLY_ARROW_BOTTOM_BORDER_RATIO,
    SUPPLY_ARROW_EXCLUDED_CLASSES,
    SUPPLY_ARROW_MAX_STUB_WIDTH,
    SUPPLY_ARROW_MIN_STUB_HEIGHT,
    SUPPLY_ARROW_SOURCE_CLASSES,
    SUPPLY_ARROW_TOP_BORDER_RATIO,
    SUPPLY_ARROW_X_TOL,
    SUPPLY_ARROW_Y_GAP,
)
from .geometry import label_bbox
from .heuristics_mosfet import is_mosfet_gate_terminal
from .ids import normalize_class_name


def is_battery_terminal(term: dict) -> bool:
    class_name = normalize_class_name(term.get("component_class_name"))
    return class_name == "battery"


def merge_battery_gate_rail_groups(
    label_to_terminal_ids: dict,
    terminals: list[dict],
):
    terminal_by_id = {term["terminal_id"]: term for term in terminals}

    parent = {int(label): int(label) for label in label_to_terminal_ids.keys()}

    def find(label):
        label = int(label)
        parent.setdefault(label, label)
        while parent[label] != label:
            parent[label] = parent[parent[label]]
            label = parent[label]
        return label

    def union(label_a, label_b):
        root_a = find(label_a)
        root_b = find(label_b)
        if root_a != root_b:
            parent[max(root_a, root_b)] = min(root_a, root_b)

    def known_terms_for_label(label):
        return [
            terminal_by_id[terminal_id]
            for terminal_id in label_to_terminal_ids.get(int(label), [])
            if terminal_id in terminal_by_id
        ]

    def is_battery_only_group(label):
        known_terms = known_terms_for_label(label)
        return bool(known_terms) and all(is_battery_terminal(term) for term in known_terms)

    def is_gate_only_group(label):
        known_terms = known_terms_for_label(label)
        return bool(known_terms) and all(is_mosfet_gate_terminal(term) for term in known_terms)

    battery_groups = [
        (label, known_terms_for_label(label))
        for label in label_to_terminal_ids
        if is_battery_only_group(label)
    ]
    gate_groups = [
        (label, known_terms_for_label(label))
        for label in label_to_terminal_ids
        if is_gate_only_group(label)
    ]

    for battery_label, battery_terms in battery_groups:
        for battery_term in battery_terms:
            battery_y = float(battery_term["y"])

            for gate_label, gate_terms in gate_groups:
                gate_y_values = [float(term["y"]) for term in gate_terms]
                if not gate_y_values:
                    continue

                nearest_gate_dy = min(abs(gate_y - battery_y) for gate_y in gate_y_values)
                if nearest_gate_dy > MOSFET_GATE_SUPPLY_ALIGN_Y_TOL:
                    continue

                union(int(battery_label), int(gate_label))

    merged = {}
    for label, terminal_ids in label_to_terminal_ids.items():
        root = find(int(label))
        merged.setdefault(root, []).extend(terminal_ids)

    return {
        int(label): sorted(set(terminal_ids))
        for label, terminal_ids in merged.items()
    }

def infer_supply_arrow_connection_for_terminal(
    term: dict,
    label_box: list[int],
    image_height: int | None,
):
    class_name = normalize_class_name(term.get("component_class_name"))
    if class_name in SUPPLY_ARROW_EXCLUDED_CLASSES:
        return None

    x1, y1, x2, y2 = map(float, label_box)
    tx = float(term.get("x"))
    ty = float(term.get("y"))
    width = max(0.0, x2 - x1)
    height = max(0.0, y2 - y1)

    if height < SUPPLY_ARROW_MIN_STUB_HEIGHT:
        return None
    if width > max(float(SUPPLY_ARROW_MAX_STUB_WIDTH), height * 0.75):
        return None
    if tx < x1 - SUPPLY_ARROW_X_TOL or tx > x2 + SUPPLY_ARROW_X_TOL:
        return None

    relative_position = str(term.get("relative_position") or "").strip().lower()
    needs_border_evidence = class_name not in SUPPLY_ARROW_SOURCE_CLASSES
    top_border_limit = image_height * SUPPLY_ARROW_TOP_BORDER_RATIO if image_height else None
    bottom_border_limit = image_height * SUPPLY_ARROW_BOTTOM_BORDER_RATIO if image_height else None
    confidence = 0.86 if class_name in SUPPLY_ARROW_SOURCE_CLASSES else 0.78

    if relative_position == "top" and y1 < ty - SUPPLY_ARROW_Y_GAP:
        if needs_border_evidence and top_border_limit is not None and y1 > top_border_limit:
            return None
        return {
            "type": "supply_arrow",
            "label": "VDD",
            "direction": "up",
            "polarity": "positive_supply",
            "confidence": confidence,
            "evidence_type": "geometry_heuristic",
            "reason": "single_terminal_vertical_stub_to_up_supply_arrow",
        }

    if relative_position == "bottom" and y2 > ty + SUPPLY_ARROW_Y_GAP:
        if needs_border_evidence and bottom_border_limit is not None and y2 < bottom_border_limit:
            return None
        return {
            "type": "supply_arrow",
            "label": "VSS",
            "direction": "down",
            "polarity": "negative_supply",
            "confidence": confidence,
            "evidence_type": "geometry_heuristic",
            "reason": "single_terminal_vertical_stub_to_down_supply_arrow",
        }

    return None


def build_supply_graph_links(
    terminals: list[dict],
    label_to_terminal_ids: dict,
    terminal_match_debug: dict,
    labels: np.ndarray,
    image_height: int | None,
    original_to_simple: dict,
):
    terminal_by_id = {term["terminal_id"]: term for term in terminals}
    supply_links = {}

    for terminal_ids in label_to_terminal_ids.values():
        unique_terminal_ids = sorted(set(terminal_ids))
        if len(unique_terminal_ids) != 1:
            continue

        terminal_id = unique_terminal_ids[0]
        term = terminal_by_id.get(terminal_id)
        if term is None:
            continue

        matched_label = terminal_match_debug.get(terminal_id, {}).get("matched_label")
        if matched_label is None:
            continue

        bbox = label_bbox(labels, int(matched_label))
        if bbox is None:
            continue

        connection = infer_supply_arrow_connection_for_terminal(term, bbox, image_height)
        if connection is None:
            continue

        simple_terminal_id = original_to_simple.get(terminal_id, terminal_id)
        supply_links.setdefault(simple_terminal_id, set()).add(connection["label"])

    return {
        terminal_id: sorted(labels)
        for terminal_id, labels in supply_links.items()
    }
