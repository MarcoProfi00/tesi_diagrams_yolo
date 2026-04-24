import numpy as np

from .config import (
    HORIZONTAL_STUB_LABEL_MAX_GAP,
    HORIZONTAL_STUB_LABEL_Y_TOL,
    HORIZONTAL_STUB_SOURCE_CLASSES,
    INDUCTOR_PARALLEL_BRANCH_MAX_LABEL_DISTANCE,
    INDUCTOR_PARALLEL_BRANCH_MAX_TERMINAL_DISTANCE,
)
from .geometry import label_bbox, min_label_distance
from .ids import get_preferred_terminal_public_name, normalize_class_name

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

# Unisce lable di rami paralleli legati a inductors verticali
# Casi particolari:
#   antenna
#   capacitor positivo e negatico
#   gnd
def merge_vertical_inductor_parallel_branch_labels(
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

    def terms_for_label(label):
        return [
            terminal_by_id[terminal_id]
            for terminal_id in label_to_terminal_ids.get(int(label), [])
            if terminal_id in terminal_by_id
        ]

    def is_inductor_vertical_terminal(term):
        class_name = normalize_class_name(term.get("component_class_name"))
        relative_position = str(term.get("relative_position") or "").lower()
        return class_name == "inductor" and relative_position in {"top", "bottom"}

    def is_matching_parallel_target(inductor_term, target_terms):
        relative_position = str(inductor_term.get("relative_position") or "").lower()
        for target_term in target_terms:
            class_name = normalize_class_name(target_term.get("component_class_name"))
            public_name = str(get_preferred_terminal_public_name(target_term) or "").lower()
            polarity = str(target_term.get("semantic_polarity") or "").lower()

            if relative_position == "top":
                if class_name == "antenna":
                    return True
                if "capacitor" in class_name and (public_name == "positive" or polarity == "positive"):
                    return True

            if relative_position == "bottom":
                if class_name in {"gnd", "ground"}:
                    return True
                if "capacitor" in class_name and (public_name == "negative" or polarity == "negative"):
                    return True

        return False

    inductor_items = []
    for terminal_id, info in terminal_match_debug.items():
        label = info.get("matched_label")
        if label is None:
            continue
        term = terminal_by_id.get(terminal_id)
        if term is None or not is_inductor_vertical_terminal(term):
            continue
        inductor_items.append((term, int(label)))

    for inductor_term, inductor_label in inductor_items:
        for target_label in label_to_terminal_ids:
            target_label = int(target_label)
            if target_label == inductor_label:
                continue

            target_terms = terms_for_label(target_label)
            if not target_terms:
                continue
            if not is_matching_parallel_target(inductor_term, target_terms):
                continue

            distance = min_label_distance(labels, inductor_label, target_label)
            if distance is None or distance > INDUCTOR_PARALLEL_BRANCH_MAX_LABEL_DISTANCE:
                continue

            union(inductor_label, target_label)

    merged = {}
    for label, terminal_ids in label_to_terminal_ids.items():
        root = find(int(label))
        merged.setdefault(root, []).extend(terminal_ids)

    return {
        int(label): sorted(set(terminal_ids))
        for label, terminal_ids in merged.items()
    }

# Aggiunge collegamenti (edges) diretti per alcuni casi di rami paralleli verticali con induttori
def build_vertical_inductor_parallel_direct_edges(
    terminals: list[dict],
    terminal_match_debug: dict,
    labels: np.ndarray,
):
    edges = []

    def is_vertical_inductor_terminal(term):
        class_name = normalize_class_name(term.get("component_class_name"))
        relative_position = str(term.get("relative_position") or "").lower()
        return class_name == "inductor" and relative_position in {"top", "bottom"}

    def is_target_for_inductor_side(inductor_term, target_term):
        relative_position = str(inductor_term.get("relative_position") or "").lower()
        class_name = normalize_class_name(target_term.get("component_class_name"))
        public_name = str(get_preferred_terminal_public_name(target_term) or "").lower()
        polarity = str(target_term.get("semantic_polarity") or "").lower()

        if relative_position == "top":
            if class_name == "antenna":
                return True
            return "capacitor" in class_name and (public_name == "positive" or polarity == "positive")

        if relative_position == "bottom":
            if class_name in {"gnd", "ground"}:
                return True
            return "capacitor" in class_name and (public_name == "negative" or polarity == "negative")

        return False

    def terminal_distance(term_a, term_b):
        ax = float(term_a.get("x", 0.0))
        ay = float(term_a.get("y", 0.0))
        bx = float(term_b.get("x", 0.0))
        by = float(term_b.get("y", 0.0))
        return float(np.hypot(ax - bx, ay - by))

    inductor_terms = [term for term in terminals if is_vertical_inductor_terminal(term)]

    for inductor_term in inductor_terms:
        inductor_id = inductor_term["terminal_id"]
        inductor_label = terminal_match_debug.get(inductor_id, {}).get("matched_label")
        if inductor_label is None:
            continue

        for target_term in terminals:
            target_id = target_term["terminal_id"]
            if target_id == inductor_id:
                continue
            if not is_target_for_inductor_side(inductor_term, target_term):
                continue

            target_label = terminal_match_debug.get(target_id, {}).get("matched_label")
            if target_label is None:
                continue

            distance = min_label_distance(labels, int(inductor_label), int(target_label))
            if distance is None or distance > INDUCTOR_PARALLEL_BRANCH_MAX_LABEL_DISTANCE:
                continue
            target_class = normalize_class_name(target_term.get("component_class_name"))
            if (
                target_class != "antenna"
                and terminal_distance(inductor_term, target_term) > INDUCTOR_PARALLEL_BRANCH_MAX_TERMINAL_DISTANCE
            ):
                continue

            edges.append(tuple(sorted((inductor_id, target_id))))

    return sorted(set(edges))
