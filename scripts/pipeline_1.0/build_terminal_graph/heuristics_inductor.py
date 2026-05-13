import numpy as np

from .config import (
    HORIZONTAL_STUB_LABEL_MAX_GAP,
    HORIZONTAL_STUB_LABEL_Y_TOL,
    HORIZONTAL_STUB_SOURCE_CLASSES,
)
from .geometry import label_bbox
from .ids import normalize_class_name

# Unisce piccoli stub orizzontali vicini a una label principale per diodi e led
def merge_near_horizontal_stub_labels(
    label_to_terminal_ids: dict,
    terminals: list[dict],
    terminal_match_debug: dict,
    labels: np.ndarray,
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

    boxes = {
        int(label): label_bbox(labels, int(label))
        for label in label_to_terminal_ids.keys()
    }

    for source_label, terminal_ids in label_to_terminal_ids.items():
        source_label = int(source_label)
        unique_ids = sorted(set(terminal_ids))
        if len(unique_ids) != 1:
            continue

        terminal_id = unique_ids[0]
        term = terminal_by_id.get(terminal_id)
        if term is None:
            continue

        class_name = normalize_class_name(term.get("component_class_name"))
        if class_name not in HORIZONTAL_STUB_SOURCE_CLASSES:
            continue

        relative_position = str(term.get("relative_position") or "").lower()
        if relative_position not in {"left", "right"}:
            continue

        source_box = boxes.get(source_label)
        if source_box is None:
            continue

        tx = float(term.get("x"))
        ty = float(term.get("y"))
        best = None

        for target_label, target_ids in label_to_terminal_ids.items():
            target_label = int(target_label)
            if target_label == source_label:
                continue

            target_box = boxes.get(target_label)
            if target_box is None:
                continue

            sx1, sy1, sx2, sy2 = source_box
            tx1, ty1, tx2, ty2 = target_box
            if relative_position == "right":
                gap = float(tx1 - sx2)
                direction_ok = tx1 >= sx2
            else:
                gap = float(sx1 - tx2)
                direction_ok = tx2 <= sx1

            if not direction_ok or gap < 0 or gap > HORIZONTAL_STUB_LABEL_MAX_GAP:
                continue

            if ty < ty1:
                y_gap = float(ty1) - ty
            elif ty > ty2:
                y_gap = ty - float(ty2)
            else:
                y_gap = 0.0

            if y_gap > HORIZONTAL_STUB_LABEL_Y_TOL:
                continue

            score = (gap, y_gap, len(set(target_ids)))
            if best is None or score < best[0]:
                best = (score, target_label)

        if best is not None:
            union(source_label, best[1])

    merged = {}
    for label, terminal_ids in label_to_terminal_ids.items():
        root = find(int(label))
        merged.setdefault(root, []).extend(terminal_ids)

    return {
        int(label): sorted(set(terminal_ids))
        for label, terminal_ids in merged.items()
    }
