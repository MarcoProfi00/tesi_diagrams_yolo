import numpy as np

from .config import BJT_BASE_ALIGN_Y_TOL, BJT_BASE_LABEL_MAX_GAP, BJT_BASE_MAX_DX
from .geometry import horizontal_bbox_gap, min_label_distance
from .grouping import build_component_bbox_by_instance
from .ids import get_preferred_terminal_public_name, normalize_class_name


# Dice se un terminale e' una base (B) del transistor.
def is_bjt_base_terminal(term: dict) -> bool:
    class_name = normalize_class_name(term.get("component_class_name"))
    terminal_name = str(get_preferred_terminal_public_name(term) or "").strip().upper()
    return "transistor" in class_name and terminal_name == "B"


# Unisce label spezzate che rappresentano la stessa linea della base (B)
# transistor, perche' la linea della B puo' essere spezzata dalla maschera.
def merge_bjt_base_aligned_labels(
    label_to_terminal_ids: dict,
    terminals: list[dict],
    components: list[dict],
    terminal_match_debug: dict,
    labels: np.ndarray,
):
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

    bbox_by_instance = build_component_bbox_by_instance(components)
    base_terms = [term for term in terminals if is_bjt_base_terminal(term)]

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

            union(int(label_a), int(label_b))

    merged = {}
    for label, terminal_ids in label_to_terminal_ids.items():
        root = find(int(label))
        merged.setdefault(root, []).extend(terminal_ids)

    return {
        int(label): sorted(set(terminal_ids))
        for label, terminal_ids in merged.items()
    }
