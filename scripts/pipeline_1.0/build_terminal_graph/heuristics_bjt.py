"""Euristiche per ricomporre label spezzate sui terminali base dei BJT."""

import numpy as np

from .config import BJT_BASE_ALIGN_Y_TOL, BJT_BASE_LABEL_MAX_GAP, BJT_BASE_MAX_DX
from .geometry import horizontal_bbox_gap, min_label_distance
from .grouping import build_component_bbox_by_instance
from .ids import get_preferred_terminal_public_name, normalize_class_name
from .label_union import LabelUnionFind, merge_label_groups


# Dice se un terminale e' una base (B) del transistor.
def is_bjt_base_terminal(term: dict) -> bool:
    class_name = normalize_class_name(term.get("component_class_name"))
    terminal_name = str(get_preferred_terminal_public_name(term) or "").strip().upper()
    return "transistor" in class_name and terminal_name == "B"


def is_bjt_non_base_terminal(term: dict) -> bool:
    """Riconosce terminali BJT diversi dalla base, quindi C/E o equivalenti."""
    class_name = normalize_class_name(term.get("component_class_name"))
    terminal_name = str(get_preferred_terminal_public_name(term) or "").strip().upper()
    return "transistor" in class_name and terminal_name != "B"


# Unisce label spezzate che rappresentano la stessa linea della base (B)
# transistor, perche' la linea della B puo' essere spezzata dalla maschera.
def merge_bjt_base_aligned_labels(
    label_to_terminal_ids: dict,
    terminals: list[dict],
    components: list[dict],
    terminal_match_debug: dict,
    labels: np.ndarray,
):
    """
    Unisce label spezzate che rappresentano la stessa linea della base.

    La maschera dei componenti puo' spezzare il tratto che collega due basi
    allineate. Uniamo solo se non trasciniamo dentro C/E o reti esterne gia'
    complete.
    """
    union_find = LabelUnionFind(label_to_terminal_ids)

    bbox_by_instance = build_component_bbox_by_instance(components)
    terminal_by_id = {term["terminal_id"]: term for term in terminals}
    base_terms = [term for term in terminals if is_bjt_base_terminal(term)]

    def label_has_non_base_bjt(label):
        for terminal_id in label_to_terminal_ids.get(int(label), []):
            term = terminal_by_id.get(terminal_id)
            if term is not None and is_bjt_non_base_terminal(term):
                return True
        return False

    def label_has_non_bjt_terminal(label):
        for terminal_id in label_to_terminal_ids.get(int(label), []):
            term = terminal_by_id.get(terminal_id)
            if term is None:
                continue
            class_name = normalize_class_name(term.get("component_class_name"))
            if "transistor" not in class_name:
                return True
        return False

    for i, term_a in enumerate(base_terms):
        info_a = terminal_match_debug.get(term_a["terminal_id"], {})
        label_a = info_a.get("matched_label")
        if label_a is None:
            continue

        bbox_a = bbox_by_instance.get(str(term_a.get("instance_id")))
        if bbox_a is None:
            continue

        for term_b in base_terms[i + 1:]:
            info_b = terminal_match_debug.get(term_b["terminal_id"], {})
            label_b = info_b.get("matched_label")
            if label_b is None or int(label_a) == int(label_b):
                continue

            # Non fondere una base con una label che contiene gia' C/E di un
            # transistor: in quel caso trascineremmo un terminale attivo nel
            # net della base.
            if label_has_non_base_bjt(label_a) or label_has_non_base_bjt(label_b):
                continue

            # Se entrambe le label hanno gia' un terminale esterno, sono reti
            # di base complete e distinte: non vanno fuse solo per allineamento.
            if label_has_non_bjt_terminal(label_a) and label_has_non_bjt_terminal(label_b):
                continue

            bbox_b = bbox_by_instance.get(str(term_b.get("instance_id")))
            if bbox_b is None:
                continue

            if abs(float(term_a["y"]) - float(term_b["y"])) > BJT_BASE_ALIGN_Y_TOL:
                continue

            if horizontal_bbox_gap(bbox_a, bbox_b) > BJT_BASE_MAX_DX:
                continue

            label_gap = min_label_distance(labels, int(label_a), int(label_b))
            if label_gap is None or label_gap > BJT_BASE_LABEL_MAX_GAP:
                continue

            union_find.union(int(label_a), int(label_b))

    return merge_label_groups(label_to_terminal_ids, union_find)
