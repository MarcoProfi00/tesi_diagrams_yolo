"""Recupero conservativo di piccoli rami obliqui gia' presenti nei fili estratti."""

from __future__ import annotations

import math

import numpy as np

from .config import (
    OBLIQUE_BRANCH_MAX_ABS_DX,
    OBLIQUE_BRANCH_MAX_ABS_DY,
    OBLIQUE_BRANCH_MAX_DISTANCE,
    OBLIQUE_BRANCH_MIN_ABS_DY,
    OBLIQUE_BRANCH_MIN_DISTANCE,
    OBLIQUE_BRANCH_MIN_SUPPORT_PIXELS,
    OBLIQUE_BRANCH_MIN_SUPPORT_RATIO,
    OBLIQUE_BRANCH_RECOVERY_ENABLE,
    OBLIQUE_BRANCH_SEARCH_HALF_HEIGHT,
    OBLIQUE_BRANCH_SEARCH_HALF_WIDTH,
    OBLIQUE_BRANCH_SOURCE_CLASSES,
    OBLIQUE_BRANCH_SOURCE_SIDES,
)
from .geometry import clamp_window
from .ids import normalize_class_name


def merge_short_oblique_branch_labels(
    label_to_terminal_ids: dict,
    terminals: list[dict],
    terminal_match_debug: dict,
    labels: np.ndarray,
    filtered_binary: np.ndarray | None,
):
    if not OBLIQUE_BRANCH_RECOVERY_ENABLE or filtered_binary is None:
        return label_to_terminal_ids

    terminal_by_id = {term["terminal_id"]: term for term in terminals}
    terminals_by_label = {
        int(label): [terminal_by_id.get(terminal_id) for terminal_id in terminal_ids]
        for label, terminal_ids in label_to_terminal_ids.items()
    }
    parent = {int(label): int(label) for label in label_to_terminal_ids.keys()}

    def find(label: int):
        label = int(label)
        parent.setdefault(label, label)
        while parent[label] != label:
            parent[label] = parent[parent[label]]
            label = parent[label]
        return label

    def union(label_a: int, label_b: int):
        root_a = find(label_a)
        root_b = find(label_b)
        if root_a != root_b:
            parent[max(root_a, root_b)] = min(root_a, root_b)

    for term in terminals:
        class_name = normalize_class_name(term.get("component_class_name"))
        if class_name not in OBLIQUE_BRANCH_SOURCE_CLASSES:
            continue

        side = str(term.get("relative_position") or "").lower()
        if side not in OBLIQUE_BRANCH_SOURCE_SIDES:
            continue

        match = terminal_match_debug.get(term["terminal_id"], {})
        source_label = match.get("matched_label")
        snap_point = match.get("snap_point")
        if source_label is None or snap_point is None:
            continue

        source_label = int(source_label)
        sx = int(snap_point[0])
        sy = int(snap_point[1])
        best = _best_oblique_target(
            source_label,
            sx,
            sy,
            side,
            labels,
            filtered_binary,
            terminals_by_label,
        )
        if best is None:
            continue

        union(source_label, int(best["target_label"]))

    merged = {}
    for label, terminal_ids in label_to_terminal_ids.items():
        root = find(int(label))
        merged.setdefault(root, []).extend(terminal_ids)

    return {
        int(label): sorted(set(terminal_ids))
        for label, terminal_ids in merged.items()
    }


def _best_oblique_target(
    source_label: int,
    sx: int,
    sy: int,
    side: str,
    labels: np.ndarray,
    filtered_binary: np.ndarray,
    terminals_by_label: dict,
):
    h, w = labels.shape[:2]
    x1, y1, x2, y2 = clamp_window(
        sx - OBLIQUE_BRANCH_SEARCH_HALF_WIDTH,
        sy - OBLIQUE_BRANCH_SEARCH_HALF_HEIGHT,
        sx + OBLIQUE_BRANCH_SEARCH_HALF_WIDTH + 1,
        sy + OBLIQUE_BRANCH_SEARCH_HALF_HEIGHT + 1,
        w,
        h,
    )
    roi = labels[y1:y2, x1:x2]
    candidate_labels = [
        int(v)
        for v in np.unique(roi)
        if int(v) > 0 and int(v) != int(source_label)
    ]
    if not candidate_labels:
        return None

    best = None
    for target_label in candidate_labels:
        if not _label_has_compatible_side_terminal(terminals_by_label.get(int(target_label), []), side):
            continue

        target_points = np.column_stack(np.where(roi == int(target_label)))
        if len(target_points) == 0:
            continue

        for py, px in target_points:
            tx = int(px + x1)
            ty = int(py + y1)
            dx = int(tx - sx)
            dy = int(ty - sy)
            dist = float(math.hypot(dx, dy))
            if dist < OBLIQUE_BRANCH_MIN_DISTANCE or dist > OBLIQUE_BRANCH_MAX_DISTANCE:
                continue
            if abs(dx) > OBLIQUE_BRANCH_MAX_ABS_DX:
                continue
            if abs(dy) < OBLIQUE_BRANCH_MIN_ABS_DY or abs(dy) > OBLIQUE_BRANCH_MAX_ABS_DY:
                continue

            support_pixels, support_len, support_ratio = _line_support(filtered_binary, (sx, sy), (tx, ty))
            if support_pixels < OBLIQUE_BRANCH_MIN_SUPPORT_PIXELS:
                continue
            if support_ratio < OBLIQUE_BRANCH_MIN_SUPPORT_RATIO:
                continue

            score = (support_ratio, support_pixels, -dist)
            if best is None or score > best["score"]:
                best = {
                    "score": score,
                    "target_label": int(target_label),
                    "target_point": [int(tx), int(ty)],
                    "support_pixels": int(support_pixels),
                    "support_len": int(support_len),
                    "support_ratio": float(support_ratio),
                }

    return best


def _label_has_compatible_side_terminal(label_terms: list[dict | None], side: str):
    for term in label_terms:
        if term is None:
            continue
        class_name = normalize_class_name(term.get("component_class_name"))
        if class_name not in OBLIQUE_BRANCH_SOURCE_CLASSES:
            continue
        if str(term.get("relative_position") or "").lower() == side:
            return True
    return False


def _line_support(binary: np.ndarray, p0: tuple[int, int], p1: tuple[int, int]):
    x0, y0 = p0
    x1, y1 = p1
    steps = max(abs(int(x1) - int(x0)), abs(int(y1) - int(y0))) + 1
    xs = np.linspace(int(x0), int(x1), num=max(steps, 1))
    ys = np.linspace(int(y0), int(y1), num=max(steps, 1))
    hits = 0
    for x, y in zip(xs, ys):
        xx = int(round(float(x)))
        yy = int(round(float(y)))
        if 0 <= yy < binary.shape[0] and 0 <= xx < binary.shape[1] and binary[yy, xx] > 0:
            hits += 1
    return hits, int(max(steps, 1)), float(hits) / float(max(steps, 1))
