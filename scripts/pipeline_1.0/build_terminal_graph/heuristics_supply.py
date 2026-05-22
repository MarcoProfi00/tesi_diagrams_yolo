"""Heuristiche per alimentazioni, ground e rail impliciti."""

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

# Dice se un terminale appartiene a una battery.
def is_battery_terminal(term: dict) -> bool:
    class_name = normalize_class_name(term.get("component_class_name"))
    return class_name == "battery"

# unisce gruppi di batteria con gruppi di gate mosfet se sono allineati verticalmente (caso particolare)
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

# Inferenza: inferisce se un terminale singolo su uno stub verticale rappresenta una rail simbolica
# Esiti possibili: VDD - VSS
# Criteri:
#   altezza minima dello stub
#   larghezza ridotta
#   coerenza con relative_position
#   posizione rispetto ai bordi (alto/basso) dell'immagine
#   classe sorgente compatibile
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


def infer_supply_rail_connection_for_group(
    terms: list[dict],
    label_box: list[int],
    image_width: int | None,
    image_height: int | None,
):
    if len(terms) < 3:
        return None

    x1, y1, x2, y2 = map(float, label_box)
    width = max(0.0, x2 - x1)
    height = max(0.0, y2 - y1)
    if width < 120.0:
        return None
    if image_width is not None and width < image_width * 0.18:
        return None

    relative_positions = {
        str(term.get("relative_position") or "").strip().lower()
        for term in terms
    }

    top_border_limit = image_height * SUPPLY_ARROW_TOP_BORDER_RATIO if image_height else None
    bottom_border_limit = image_height * SUPPLY_ARROW_BOTTOM_BORDER_RATIO if image_height else None

    if relative_positions <= {"top"}:
        if top_border_limit is not None and y1 > top_border_limit:
            return None
        return {
            "type": "supply_rail",
            "label": "VDD",
            "direction": "up",
            "polarity": "positive_supply",
            "confidence": 0.84,
            "evidence_type": "group_geometry_heuristic",
            "reason": "top_border_horizontal_supply_rail_group",
        }

    if relative_positions <= {"bottom"}:
        if bottom_border_limit is not None and y2 < bottom_border_limit:
            return None
        return {
            "type": "supply_rail",
            "label": "VSS",
            "direction": "down",
            "polarity": "negative_supply",
            "confidence": 0.84,
            "evidence_type": "group_geometry_heuristic",
            "reason": "bottom_border_horizontal_supply_rail_group",
        }

    return None

# Costruisce gli archi terminali VDD e VSS
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
    image_width = labels.shape[1] if labels is not None else None

    for terminal_ids in label_to_terminal_ids.values():
        unique_terminal_ids = sorted(set(terminal_ids))
        known_terms = [
            terminal_by_id[terminal_id]
            for terminal_id in unique_terminal_ids
            if terminal_id in terminal_by_id
        ]
        if not known_terms:
            continue

        terminal_id = unique_terminal_ids[0]
        matched_label = terminal_match_debug.get(terminal_id, {}).get("matched_label")
        if matched_label is None:
            continue

        bbox = label_bbox(labels, int(matched_label))
        if bbox is None:
            continue

        connection = None
        if len(unique_terminal_ids) == 1:
            connection = infer_supply_arrow_connection_for_terminal(known_terms[0], bbox, image_height)
        if connection is None:
            connection = infer_supply_rail_connection_for_group(
                known_terms,
                bbox,
                image_width,
                image_height,
            )
        if connection is None:
            continue

        for member_terminal_id in unique_terminal_ids:
            simple_terminal_id = original_to_simple.get(member_terminal_id, member_terminal_id)
            supply_links.setdefault(simple_terminal_id, set()).add(connection["label"])

    return {
        terminal_id: sorted(labels)
        for terminal_id, labels in supply_links.items()
    }
