"""Euristiche per alimentazioni, ground e rail impliciti."""

from .config import MOSFET_GATE_SUPPLY_ALIGN_Y_TOL
from .heuristics_mosfet import is_mosfet_gate_terminal
from .ids import normalize_class_name
from .label_union import LabelUnionFind, merge_label_groups

def is_battery_terminal(term: dict) -> bool:
    """Riconosce un terminale appartenente a una Battery."""
    class_name = normalize_class_name(term.get("component_class_name"))
    return class_name == "battery"

def merge_battery_gate_rail_groups(
    label_to_terminal_ids: dict,
    terminals: list[dict],
):
    """
    Unisce gruppi Battery e gate MOSFET quando sono allineati verticalmente.

    E' una correzione di dominio per rail di alimentazione/gate che possono
    restare separati dopo skeletonizzazione.
    """
    terminal_by_id = {term["terminal_id"]: term for term in terminals}

    union_find = LabelUnionFind(label_to_terminal_ids)

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

                union_find.union(int(battery_label), int(gate_label))

    return merge_label_groups(label_to_terminal_ids, union_find)
