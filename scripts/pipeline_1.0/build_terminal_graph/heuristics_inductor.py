"""Euristiche per ricomporre stub orizzontali/verticali spezzati."""

import numpy as np

from .config import (
    HORIZONTAL_STUB_LABEL_MAX_GAP,
    HORIZONTAL_STUB_LABEL_Y_TOL,
    HORIZONTAL_STUB_SOURCE_CLASSES,
    VERTICAL_STUB_NETWORK_AMBIGUITY_MARGIN,
    VERTICAL_STUB_NETWORK_MAX_GAP,
    VERTICAL_STUB_NETWORK_MERGE_ENABLE,
    VERTICAL_STUB_NETWORK_MIN_Y_OVERLAP,
    VERTICAL_STUB_SOURCE_MAX_TERMINALS,
    VERTICAL_STUB_SOURCE_MAX_WIDTH,
    VERTICAL_STUB_SOURCE_MIN_HEIGHT,
    VERTICAL_STUB_TARGET_MIN_TERMINALS,
    VERTICAL_STUB_TARGET_MIN_WIDTH,
)
from .geometry import label_bbox
from .ids import normalize_class_name
from .label_union import LabelUnionFind, merge_label_groups


FACING_VERTICAL_LABEL_MAX_TERMINALS = 2
FACING_VERTICAL_LABEL_MAX_GAP = 44.0
FACING_VERTICAL_LABEL_MAX_OVERLAP = 24.0
FACING_VERTICAL_LABEL_X_TOL = 12.0
FACING_VERTICAL_LABEL_MIN_SUPPORT = 0.45

# Unisce piccoli stub orizzontali vicini a una label principale per diodi e led
def merge_near_horizontal_stub_labels(
    label_to_terminal_ids: dict,
    terminals: list[dict],
    labels: np.ndarray,
):
    """
    Unisce piccoli stub orizzontali vicini a una label principale.

    E' pensato soprattutto per diodi/LED, dove il filo orizzontale puo' essere
    tagliato dalla maschera del componente.
    """
    terminal_by_id = {term["terminal_id"]: term for term in terminals}
    union_find = LabelUnionFind(label_to_terminal_ids)

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

        # Mantiene la validazione storica di entrambe le coordinate.
        _, ty = float(term.get("x")), float(term.get("y"))
        best = None

        for target_label, target_ids in label_to_terminal_ids.items():
            target_label = int(target_label)
            if target_label == source_label:
                continue

            target_box = boxes.get(target_label)
            if target_box is None:
                continue

            sx1, _, sx2, _ = source_box
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
            union_find.union(source_label, best[1])

    return merge_label_groups(label_to_terminal_ids, union_find)


def merge_near_vertical_stub_labels(
    label_to_terminal_ids: dict,
    terminals: list[dict],
    labels: np.ndarray,
    filtered_binary: np.ndarray | None = None,
):
    """
    Unisce stub verticali stretti con reti verticali vicine.

    Usa bbox delle label e, quando disponibile, filtered_binary per verificare
    che tra due spezzoni ci sia supporto reale nel binario spesso.
    """
    if not VERTICAL_STUB_NETWORK_MERGE_ENABLE:
        return label_to_terminal_ids

    terminal_by_id = {term["terminal_id"]: term for term in terminals}
    union_find = LabelUnionFind(label_to_terminal_ids)

    boxes = {
        int(label): label_bbox(labels, int(label))
        for label in label_to_terminal_ids.keys()
    }

    for source_label, terminal_ids in label_to_terminal_ids.items():
        source_label = int(source_label)
        unique_ids = sorted(set(terminal_ids))
        if len(unique_ids) == 0 or len(unique_ids) > VERTICAL_STUB_SOURCE_MAX_TERMINALS:
            continue

        terms = [terminal_by_id.get(terminal_id) for terminal_id in unique_ids]
        if any(term is None for term in terms):
            continue

        source_box = boxes.get(source_label)
        if source_box is None:
            continue
        sx1, sy1, sx2, sy2 = source_box
        source_width = float(sx2 - sx1 + 1)
        source_height = float(sy2 - sy1 + 1)
        if source_width > float(VERTICAL_STUB_SOURCE_MAX_WIDTH):
            continue
        if source_height < float(VERTICAL_STUB_SOURCE_MIN_HEIGHT):
            continue

        relative_positions = {
            str(term.get("relative_position") or "").strip().lower()
            for term in terms
        }
        if not relative_positions or not relative_positions <= {"top", "bottom"}:
            continue

        source_center_x = (float(sx1) + float(sx2)) / 2.0
        if any(abs(float(term.get("x", 0.0)) - source_center_x) > source_width + 8.0 for term in terms):
            continue

        candidates = []
        for target_label, target_ids in label_to_terminal_ids.items():
            target_label = int(target_label)
            if target_label == source_label:
                continue

            target_unique_ids = sorted(set(target_ids))
            if len(target_unique_ids) < VERTICAL_STUB_TARGET_MIN_TERMINALS:
                continue

            target_box = boxes.get(target_label)
            if target_box is None:
                continue
            tx1, ty1, tx2, ty2 = target_box
            target_width = float(tx2 - tx1 + 1)
            if target_width < float(VERTICAL_STUB_TARGET_MIN_WIDTH):
                continue

            overlap_y = min(float(sy2), float(ty2)) - max(float(sy1), float(ty1)) + 1.0
            if overlap_y < float(VERTICAL_STUB_NETWORK_MIN_Y_OVERLAP):
                continue

            left_gap = float(sx1 - tx2)
            right_gap = float(tx1 - sx2)
            side = None
            gap = None
            if 0.0 <= left_gap <= float(VERTICAL_STUB_NETWORK_MAX_GAP):
                side = "left"
                gap = left_gap
            if 0.0 <= right_gap <= float(VERTICAL_STUB_NETWORK_MAX_GAP):
                if gap is None or right_gap < gap:
                    side = "right"
                    gap = right_gap
            if side is None or gap is None:
                continue

            nearest = _find_lateral_edge_pair(labels, source_label, target_label, side)
            if nearest is None:
                continue
            support_ratio = 0.0
            if filtered_binary is not None:
                support_ratio = _line_support_ratio(
                    filtered_binary,
                    nearest["source_point"],
                    nearest["target_point"],
                )

            score = (
                float(support_ratio),
                -float(nearest["distance"]),
                float(overlap_y),
                float(target_width),
                float(len(target_unique_ids)),
            )
            candidates.append({
                "target_label": target_label,
                "score": score,
                "gap": float(gap),
                "overlap_y": float(overlap_y),
                "support_ratio": float(support_ratio),
                "distance": float(nearest["distance"]),
            })

        if not candidates:
            continue

        candidates.sort(key=lambda item: item["score"], reverse=True)
        best = candidates[0]
        if len(candidates) > 1:
            next_best = candidates[1]
            support_gap = float(best["support_ratio"]) - float(next_best["support_ratio"])
            distance_gap = float(next_best["distance"]) - float(best["distance"])
            if support_gap < 0.03 and distance_gap < float(VERTICAL_STUB_NETWORK_AMBIGUITY_MARGIN):
                best_gap = float(best["gap"])
                next_gap = float(next_best["gap"])
                if abs(best_gap - next_gap) <= float(VERTICAL_STUB_NETWORK_AMBIGUITY_MARGIN):
                    best_overlap = float(best["overlap_y"])
                    next_overlap = float(next_best["overlap_y"])
                    if abs(best_overlap - next_overlap) <= float(VERTICAL_STUB_NETWORK_MIN_Y_OVERLAP) * 0.35:
                        continue

        union_find.union(source_label, int(best["target_label"]))

    vertical_terminal_labels = []
    for source_label, terminal_ids in label_to_terminal_ids.items():
        source_label = int(source_label)
        unique_ids = sorted(set(terminal_ids))
        if len(unique_ids) == 0 or len(unique_ids) > FACING_VERTICAL_LABEL_MAX_TERMINALS:
            continue

        terms = [terminal_by_id.get(terminal_id) for terminal_id in unique_ids]
        if any(term is None for term in terms):
            continue

        relative_positions = {
            str(term.get("relative_position") or "").strip().lower()
            for term in terms
        }
        if not relative_positions or not relative_positions <= {"top", "bottom"}:
            continue

        source_box = boxes.get(source_label)
        if source_box is None:
            continue

        center_x = float(sum(float(term.get("x", 0.0)) for term in terms)) / float(len(terms))
        vertical_terminal_labels.append({
            "label": source_label,
            "terminal_ids": unique_ids,
            "terms": terms,
            "box": source_box,
            "center_x": center_x,
        })

    for idx, source_info in enumerate(vertical_terminal_labels):
        source_label = int(source_info["label"])
        sx1, sy1, sx2, sy2 = source_info["box"]

        for target_info in vertical_terminal_labels[idx + 1:]:
            target_label = int(target_info["label"])
            if union_find.find(source_label) == union_find.find(target_label):
                continue

            tx1, ty1, tx2, ty2 = target_info["box"]
            center_dx = abs(float(source_info["center_x"]) - float(target_info["center_x"]))
            if center_dx > float(FACING_VERTICAL_LABEL_X_TOL):
                continue

            x_box_gap = max(0.0, max(float(sx1), float(tx1)) - min(float(sx2), float(tx2)))
            if x_box_gap > float(FACING_VERTICAL_LABEL_X_TOL):
                continue

            down_gap = float(ty1) - float(sy2)
            up_gap = float(sy1) - float(ty2)
            if down_gap >= -float(FACING_VERTICAL_LABEL_MAX_OVERLAP):
                side = "down"
                gap = down_gap
            elif up_gap >= -float(FACING_VERTICAL_LABEL_MAX_OVERLAP):
                side = "up"
                gap = up_gap
            else:
                continue

            if gap > float(FACING_VERTICAL_LABEL_MAX_GAP):
                continue

            nearest = _find_vertical_edge_pair(labels, source_label, target_label, side)
            if nearest is None:
                continue

            support_ratio = 0.0
            if filtered_binary is not None:
                support_ratio = _line_support_ratio(
                    filtered_binary,
                    nearest["source_point"],
                    nearest["target_point"],
                )
            if support_ratio < float(FACING_VERTICAL_LABEL_MIN_SUPPORT):
                continue

            union_find.union(source_label, target_label)

    return merge_label_groups(label_to_terminal_ids, union_find)


def _find_lateral_edge_pair(
    labels: np.ndarray,
    source_label: int,
    target_label: int,
    side: str,
):
    """Trova la coppia di punti piu' vicina tra bordi laterali di due label."""
    source_ys, source_xs = np.where(labels == int(source_label))
    target_ys, target_xs = np.where(labels == int(target_label))
    if len(source_xs) == 0 or len(target_xs) == 0:
        return None

    if side == "right":
        source_edge_mask = source_xs == source_xs.max()
        target_edge_mask = target_xs == target_xs.min()
    else:
        source_edge_mask = source_xs == source_xs.min()
        target_edge_mask = target_xs == target_xs.max()

    source_edge = np.column_stack((source_xs[source_edge_mask], source_ys[source_edge_mask]))
    target_edge = np.column_stack((target_xs[target_edge_mask], target_ys[target_edge_mask]))
    if len(source_edge) == 0 or len(target_edge) == 0:
        return None

    best = None
    for sx, sy in source_edge:
        y_deltas = np.abs(target_edge[:, 1] - sy)
        best_idx = int(np.argmin(y_deltas))
        tx, ty = target_edge[best_idx]
        distance = float(np.hypot(float(tx - sx), float(ty - sy)))
        if best is None or distance < best["distance"]:
            best = {
                "distance": distance,
                "source_point": [int(sx), int(sy)],
                "target_point": [int(tx), int(ty)],
            }

    return best


def _line_support_ratio(
    binary: np.ndarray,
    p0: list[int],
    p1: list[int],
):
    """Misura quanta parte del segmento tra due punti e' supportata dal binario."""
    x0, y0 = map(int, p0)
    x1, y1 = map(int, p1)
    steps = max(abs(x1 - x0), abs(y1 - y0)) + 1
    xs = np.linspace(x0, x1, num=max(steps, 1))
    ys = np.linspace(y0, y1, num=max(steps, 1))
    hits = 0
    for x, y in zip(xs, ys):
        xx = int(round(float(x)))
        yy = int(round(float(y)))
        if 0 <= yy < binary.shape[0] and 0 <= xx < binary.shape[1] and binary[yy, xx] > 0:
            hits += 1
    return float(hits) / float(max(steps, 1))


def _find_vertical_edge_pair(
    labels: np.ndarray,
    source_label: int,
    target_label: int,
    side: str,
):
    """Trova la coppia di punti piu' vicina tra bordi verticali di due label."""
    source_ys, source_xs = np.where(labels == int(source_label))
    target_ys, target_xs = np.where(labels == int(target_label))
    if len(source_xs) == 0 or len(target_xs) == 0:
        return None

    if side == "down":
        source_edge_mask = source_ys == source_ys.max()
        target_edge_mask = target_ys == target_ys.min()
    else:
        source_edge_mask = source_ys == source_ys.min()
        target_edge_mask = target_ys == target_ys.max()

    source_edge = np.column_stack((source_xs[source_edge_mask], source_ys[source_edge_mask]))
    target_edge = np.column_stack((target_xs[target_edge_mask], target_ys[target_edge_mask]))
    if len(source_edge) == 0 or len(target_edge) == 0:
        return None

    best = None
    for sx, sy in source_edge:
        x_deltas = np.abs(target_edge[:, 0] - sx)
        best_idx = int(np.argmin(x_deltas))
        tx, ty = target_edge[best_idx]
        distance = float(np.hypot(float(tx - sx), float(ty - sy)))
        if best is None or distance < best["distance"]:
            best = {
                "distance": distance,
                "source_point": [int(sx), int(sy)],
                "target_point": [int(tx), int(ty)],
            }

    return best
