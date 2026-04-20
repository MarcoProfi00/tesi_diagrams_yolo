from __future__ import annotations

import cv2
import numpy as np

from .geometry import geom_clamp_bbox_to_image


DEFAULT_FALLBACK_SIDE = {
    "horizontal": "left",
    "vertical": "top",
}


# Group consecutive indices.
def _group_consecutive_indices(indices: list[int]) -> list[list[int]]:
    if not indices:
        return []
    groups = [[indices[0]]]
    for idx in indices[1:]:
        if idx == groups[-1][-1] + 1:
            groups[-1].append(idx)
        else:
            groups.append([idx])
    return groups


# Handle bounding box dims.
def _bbox_dims(bbox, binary):
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)
    width = max(1, x2 - x1 + 1)
    height = max(1, y2 - y1 + 1)
    return x1, y1, x2, y2, width, height


# Count nonzero.
def _count_nonzero(binary, x1, y1, x2, y2) -> int:
    h, w = binary.shape[:2]
    x1 = max(0, min(w, int(round(x1))))
    y1 = max(0, min(h, int(round(y1))))
    x2 = max(0, min(w, int(round(x2))))
    y2 = max(0, min(h, int(round(y2))))
    if x2 <= x1 or y2 <= y1:
        return 0
    return int(cv2.countNonZero(binary[y1:y2, x1:x2]))


# Handle projection side scores.
def _projection_side_scores(
    binary,
    bbox,
    orientation: str,
    center_band_ratio: float = 0.42,
    edge_inset_ratio: float = 0.08,
):
    x1, y1, x2, y2, width, height = _bbox_dims(bbox, binary)

    if orientation == "horizontal":
        inset_x = max(1, int(round(width * edge_inset_ratio)))
        band_half = max(2, int(round(height * center_band_ratio / 2.0)))
        xc = int(round((x1 + x2) / 2.0))
        yc = int(round((y1 + y2) / 2.0))

        rx1 = min(max(x1, x1 + inset_x), x2)
        rx2 = max(min(x2 + 1, x2 + 1 - inset_x), rx1 + 1)
        ry1 = max(y1, yc - band_half)
        ry2 = min(y2 + 1, yc + band_half + 1)

        roi = binary[ry1:ry2, rx1:rx2]
        projection = np.count_nonzero(roi > 0, axis=0) if roi.size else np.array([], dtype=np.int32)
        mid = max(1, len(projection) // 2)
        left_score = int(projection[:mid].max()) if mid > 0 and len(projection[:mid]) > 0 else 0
        right_score = int(projection[mid:].max()) if len(projection[mid:]) > 0 else 0
        return {
            "left": left_score,
            "right": right_score,
            "projection_axis": "x",
            "roi": [int(rx1), int(ry1), int(rx2), int(ry2)],
        }

    inset_y = max(1, int(round(height * edge_inset_ratio)))
    band_half = max(2, int(round(width * center_band_ratio / 2.0)))
    xc = int(round((x1 + x2) / 2.0))
    yc = int(round((y1 + y2) / 2.0))

    rx1 = max(x1, xc - band_half)
    rx2 = min(x2 + 1, xc + band_half + 1)
    ry1 = min(max(y1, y1 + inset_y), y2)
    ry2 = max(min(y2 + 1, y2 + 1 - inset_y), ry1 + 1)

    roi = binary[ry1:ry2, rx1:rx2]
    projection = np.count_nonzero(roi > 0, axis=1) if roi.size else np.array([], dtype=np.int32)
    mid = max(1, len(projection) // 2)
    top_score = int(projection[:mid].max()) if mid > 0 and len(projection[:mid]) > 0 else 0
    bottom_score = int(projection[mid:].max()) if len(projection[mid:]) > 0 else 0
    return {
        "top": top_score,
        "bottom": bottom_score,
        "projection_axis": "y",
        "roi": [int(rx1), int(ry1), int(rx2), int(ry2)],
    }


# Handle projection edge group scores.
def _projection_edge_group_scores(
    binary,
    bbox,
    orientation: str,
    center_band_ratio: float = 0.42,
    edge_inset_ratio: float = 0.08,
):
    x1, y1, x2, y2, width, height = _bbox_dims(bbox, binary)

    if orientation == "horizontal":
        inset_x = max(1, int(round(width * edge_inset_ratio)))
        band_half = max(2, int(round(height * center_band_ratio / 2.0)))
        yc = int(round((y1 + y2) / 2.0))

        rx1 = min(max(x1, x1 + inset_x), x2)
        rx2 = max(min(x2 + 1, x2 + 1 - inset_x), rx1 + 1)
        ry1 = max(y1, yc - band_half)
        ry2 = min(y2 + 1, yc + band_half + 1)
        roi = binary[ry1:ry2, rx1:rx2]
        projection = np.count_nonzero(roi > 0, axis=0) if roi.size else np.array([], dtype=np.int32)
        axis_size = len(projection)
        keys = ("left", "right")
    else:
        inset_y = max(1, int(round(height * edge_inset_ratio)))
        band_half = max(2, int(round(width * center_band_ratio / 2.0)))
        xc = int(round((x1 + x2) / 2.0))

        rx1 = max(x1, xc - band_half)
        rx2 = min(x2 + 1, xc + band_half + 1)
        ry1 = min(max(y1, y1 + inset_y), y2)
        ry2 = max(min(y2 + 1, y2 + 1 - inset_y), ry1 + 1)
        roi = binary[ry1:ry2, rx1:rx2]
        projection = np.count_nonzero(roi > 0, axis=1) if roi.size else np.array([], dtype=np.int32)
        axis_size = len(projection)
        keys = ("top", "bottom")

    if axis_size == 0:
        return {
            keys[0]: 0.0,
            keys[1]: 0.0,
            "projection_axis": "x" if orientation == "horizontal" else "y",
            "roi": [int(rx1), int(ry1), int(rx2), int(ry2)],
            "projection_mode": "edge_group",
        }

    max_score = int(projection.max()) if axis_size > 0 else 0
    keep_threshold = max(2, int(round(max_score * 0.82)))
    kept = [idx for idx, value in enumerate(projection.tolist()) if value >= keep_threshold]
    groups = _group_consecutive_indices(kept)

    # Handle edge group score.
    def edge_group_score(group: list[int], side: str) -> float:
        group_max = max(int(projection[idx]) for idx in group)
        group_len = len(group)
        if side in {"left", "top"}:
            edge_distance = group[0]
        else:
            edge_distance = max(0, axis_size - 1 - group[-1])
        return float(group_max) + 0.25 * float(group_len) - 0.15 * float(edge_distance)

    first_group = groups[0] if groups else []
    last_group = groups[-1] if groups else []

    first_score = edge_group_score(first_group, keys[0]) if first_group else 0.0
    last_score = edge_group_score(last_group, keys[1]) if last_group else 0.0

    return {
        keys[0]: round(first_score, 4),
        keys[1]: round(last_score, 4),
        "projection_axis": "x" if orientation == "horizontal" else "y",
        "roi": [int(rx1), int(ry1), int(rx2), int(ry2)],
        "projection_mode": "edge_group",
        "keep_threshold": keep_threshold,
        "kept_groups": groups,
        "projection_values": projection.tolist(),
    }


# Handle diode bar scores.
def _diode_bar_scores(score_map: dict, orientation: str) -> dict:
    projection = score_map.get("projection_values") or []
    groups = score_map.get("kept_groups") or []
    axis_size = len(projection)

    if orientation == "horizontal":
        keys = ("left", "right")
    else:
        keys = ("top", "bottom")

    # Group center.
    def group_center(group: list[int]) -> float:
        return (float(group[0]) + float(group[-1])) / 2.0

    # Handle bar score.
    def bar_score(group: list[int]) -> float:
        if not group:
            return 0.0
        group_max = max(int(projection[idx]) for idx in group)
        group_len = len(group)
        axis_mid = float(max(axis_size - 1, 0)) / 2.0
        center_distance = abs(group_center(group) - axis_mid)
        edge_distance = min(group[0], max(0, axis_size - 1 - group[-1]))
        return 1.4 * float(group_max) - 0.8 * float(group_len) - 0.08 * float(center_distance) + 0.05 * float(edge_distance)

    best_group = max(groups, key=lambda group: (bar_score(group), group_center(group)), default=[])
    best_center = group_center(best_group) if best_group else 0.0
    axis_mid = float(max(axis_size - 1, 0)) / 2.0
    marker_side = keys[0] if best_center <= axis_mid else keys[1]
    other_side = keys[1] if marker_side == keys[0] else keys[0]

    adjusted = dict(score_map)
    adjusted[marker_side] = round(bar_score(best_group) + 10.0, 4)
    adjusted[other_side] = round(bar_score(best_group) - 10.0, 4)
    adjusted["projection_mode"] = "diode_bar_thin_group"
    adjusted["selected_bar_group"] = best_group
    adjusted["selected_bar_center"] = round(float(best_center), 4)
    adjusted["selected_bar_side"] = marker_side
    return adjusted


# Handle plus marker scores by side.
def _plus_marker_scores_by_side(binary, bbox, orientation: str):
    def plus_like_patch_score(cx: int, cy: int, half_w: int, half_h: int) -> float:
        xa = max(0, cx - half_w)
        xb = min(binary.shape[1], cx + half_w + 1)
        ya = max(0, cy - half_h)
        yb = min(binary.shape[0], cy + half_h + 1)
        roi = binary[ya:yb, xa:xb]
        if roi.size == 0:
            return 0.0

        row_proj = np.count_nonzero(roi > 0, axis=1)
        col_proj = np.count_nonzero(roi > 0, axis=0)

        row_max = float(row_proj.max()) if row_proj.size else 0.0
        col_max = float(col_proj.max()) if col_proj.size else 0.0

        # Il '+' ha sia barra orizzontale sia barra verticale.
        # Il '-' tende ad avere quasi solo la barra orizzontale.
        balance = min(row_max, col_max) / max(max(row_max, col_max), 1.0)

        # Supporto sulla colonna centrale: aiuta a riconoscere la barretta verticale del '+'
        cx_local = roi.shape[1] // 2
        band_x1 = max(0, cx_local - 1)
        band_x2 = min(roi.shape[1], cx_local + 2)
        center_col_support = float(np.count_nonzero(roi[:, band_x1:band_x2] > 0))

        return (
            0.90 * row_max
            + 1.55 * col_max
            + 1.80 * balance * min(row_max, col_max)
            + 0.06 * center_col_support
        )

    x1, y1, x2, y2, width, height = _bbox_dims(bbox, binary)

    # Lascio invariato il caso orizzontale, che nei tuoi batch sta andando bene.
    if orientation == "horizontal":
        patch_half_w = max(2, int(round(width * 0.18)))
        patch_half_h = max(2, int(round(height * 0.10)))

        left_cx = int(round(x1 + width * 0.10))
        right_cx = int(round(x1 + width * 0.90))
        top_cy = int(round(y1 + height * 0.20))

        left_score = plus_like_patch_score(left_cx, top_cy, patch_half_w, patch_half_h)
        right_score = plus_like_patch_score(right_cx, top_cy, patch_half_w, patch_half_h)

        return {
            "left": round(float(left_score), 4),
            "right": round(float(right_score), 4),
            "patch_half_w": patch_half_w,
            "patch_half_h": patch_half_h,
            "score_mode": "plus_marker_generic_horizontal",
        }

    # Caso verticale: patch più stretti e più interni,
    # per leggere il '+' e il '-' ed evitare wire/bordo ellisse.
    cx = int(round((x1 + x2) / 2.0))
    patch_half_w = max(2, int(round(width * 0.10)))
    patch_half_h = max(2, int(round(height * 0.07)))

    top_cy = int(round(y1 + height * 0.30))
    bottom_cy = int(round(y1 + height * 0.70))

    top_score = plus_like_patch_score(cx, top_cy, patch_half_w, patch_half_h)
    bottom_score = plus_like_patch_score(cx, bottom_cy, patch_half_w, patch_half_h)

    # Nei Voltage_Source verticali del tuo dataset il '+' è quasi sempre sopra.
    # Se i due score sono quasi pari, preferiamo top.
    near_tie_margin = max(4.0, 0.10 * max(top_score, bottom_score, 1.0))
    if abs(top_score - bottom_score) <= near_tie_margin:
        top_score += 4.0

    return {
        "top": round(float(top_score), 4),
        "bottom": round(float(bottom_score), 4),
        "patch_half_w": patch_half_w,
        "patch_half_h": patch_half_h,
        "top_cy": int(top_cy),
        "bottom_cy": int(bottom_cy),
        "score_mode": "plus_marker_voltage_source_vertical_tight",
    }


# Handle inner half mass scores.
def _inner_half_mass_scores(binary, bbox, orientation: str):
    x1, y1, x2, y2, width, height = _bbox_dims(bbox, binary)
    inset_x = max(2, int(round(width * 0.22)))
    inset_y = max(2, int(round(height * 0.22)))
    ix1 = min(max(x1, x1 + inset_x), x2)
    ix2 = max(min(x2 + 1, x2 + 1 - inset_x), ix1 + 1)
    iy1 = min(max(y1, y1 + inset_y), y2)
    iy2 = max(min(y2 + 1, y2 + 1 - inset_y), iy1 + 1)

    roi = binary[iy1:iy2, ix1:ix2]
    if roi.size == 0:
        return {
            "left": 0,
            "right": 0,
            "top": 0,
            "bottom": 0,
            "roi": [int(ix1), int(iy1), int(ix2), int(iy2)],
        }

    if orientation == "horizontal":
        mid = max(1, roi.shape[1] // 2)
        return {
            "left": int(np.count_nonzero(roi[:, :mid] > 0)),
            "right": int(np.count_nonzero(roi[:, mid:] > 0)),
            "roi": [int(ix1), int(iy1), int(ix2), int(iy2)],
        }

    mid = max(1, roi.shape[0] // 2)
    return {
        "top": int(np.count_nonzero(roi[:mid, :] > 0)),
        "bottom": int(np.count_nonzero(roi[mid:, :] > 0)),
        "roi": [int(ix1), int(iy1), int(ix2), int(iy2)],
    }


# Choose side.
def _choose_side(score_map: dict, positive_key: str, negative_key: str, fallback_side: str):
    positive_score = float(score_map.get(positive_key, 0.0))
    negative_score = float(score_map.get(negative_key, 0.0))

    if positive_score >= negative_score:
        chosen = positive_key
        other = negative_key
        best = positive_score
        second = negative_score
    else:
        chosen = negative_key
        other = positive_key
        best = negative_score
        second = positive_score

    confidence = 0.0
    if best > 0.0 or second > 0.0:
        confidence = (best - second) / max(best + second, 1.0)
        confidence = max(0.0, min(1.0, confidence))

    used_fallback = False
    if best <= 0.0:
        chosen = fallback_side
        other = negative_key if chosen == positive_key else positive_key
        confidence = 0.2
        used_fallback = True

    evidence_type = "symbol_heuristic"
    if used_fallback or confidence < 0.03:
        chosen = fallback_side if used_fallback else chosen
        other = negative_key if chosen == positive_key else positive_key
        confidence = max(0.2, confidence)
        evidence_type = "orientation_fallback"

    return chosen, other, round(float(confidence), 4), evidence_type


# Handle set term semantic fields.
def _set_term_semantic_fields(term: dict, semantic_name: str, semantic_slot: str, confidence: float, resolution_mode: str, evidence_type: str, debug: dict):
    term["semantic_terminal_name"] = semantic_name
    term["semantic_terminal_id"] = f"{term['instance_id']}:{semantic_name}"
    term["semantic_slot"] = semantic_slot
    term["semantic_confidence"] = round(float(confidence), 4)
    term["semantic_resolution_mode"] = resolution_mode
    term["semantic_evidence_type"] = evidence_type
    term["semantic_resolution_debug"] = debug
    term["display_name"] = semantic_name
    term["display_terminal_id"] = term["semantic_terminal_id"]

    if semantic_name in {"positive", "negative", "anode", "cathode"}:
        term["semantic_polarity"] = semantic_name
        term["semantic_role_family"] = "polarity"
    elif semantic_name in {"current_from", "current_to"}:
        term["semantic_direction"] = semantic_name
        term["semantic_role_family"] = "current_direction"


# Assign pair roles.
def _assign_pair_roles(
    terminals: list[dict],
    marker_side: str,
    other_side: str,
    marker_name: str | None,
    other_name: str | None,
    confidence: float,
    resolution_mode: str,
    evidence_type: str,
    debug: dict,
):
    role_by_position = {
        marker_side: ("marker_side", marker_name),
        other_side: ("other_side", other_name),
    }

    for term in terminals:
        relative_position = term.get("relative_position")
        semantic_slot, semantic_name = role_by_position.get(relative_position, (None, None))
        if semantic_name is None:
            continue
        _set_term_semantic_fields(
            term,
            semantic_name=semantic_name,
            semantic_slot=semantic_slot,
            confidence=confidence,
            resolution_mode=resolution_mode,
            evidence_type=evidence_type,
            debug=debug,
        )
    return terminals


# Assign strategy result.
def _assign_strategy_result(terminals, orientation, meta, score_map, resolution_mode):
    if orientation == "horizontal":
        primary_side = "left"
        secondary_side = "right"
    else:
        primary_side = "top"
        secondary_side = "bottom"

    marker_side, other_side, confidence, evidence_type = _choose_side(
        score_map,
        primary_side,
        secondary_side,
        DEFAULT_FALLBACK_SIDE.get(orientation, primary_side),
    )

    debug = {
        "orientation": orientation,
        "scores": score_map,
        "selected_marker_side": marker_side,
        "selected_other_side": other_side,
        "confidence": confidence,
        "evidence_type": evidence_type,
    }

    semantic_roles = meta.get("semantic_roles", {})
    return _assign_pair_roles(
        terminals,
        marker_side=marker_side,
        other_side=other_side,
        marker_name=semantic_roles.get("marker_side"),
        other_name=semantic_roles.get("other_side"),
        confidence=confidence,
        resolution_mode=resolution_mode,
        evidence_type=evidence_type,
        debug=debug,
    )


# Resolve two terminal semantics.
def resolve_two_terminal_semantics(binary, bbox, orientation, terminals, meta):
    semantic_strategy = meta.get("semantic_terminal_strategy")

    if semantic_strategy is None or len(terminals) < 2 or orientation not in {"horizontal", "vertical"}:
        return terminals

    if semantic_strategy == "diode_cathode_from_bar":
        score_map = _projection_edge_group_scores(
            binary,
            bbox,
            orientation,
            center_band_ratio=0.42,
            edge_inset_ratio=0.08,
        )
        score_map = _diode_bar_scores(score_map, orientation)
        return _assign_strategy_result(
            terminals,
            orientation,
            meta,
            score_map,
            resolution_mode=semantic_strategy,
        )

    if semantic_strategy == "polarized_capacitor_positive_from_marker":
        score_map = _projection_edge_group_scores(
            binary,
            bbox,
            orientation,
            center_band_ratio=0.50,
            edge_inset_ratio=0.10,
        )
        return _assign_strategy_result(
            terminals,
            orientation,
            meta,
            score_map,
            resolution_mode=semantic_strategy,
        )

    if semantic_strategy == "battery_positive_from_long_plate":
        score_map = _projection_side_scores(
            binary,
            bbox,
            orientation,
            center_band_ratio=0.60,
            edge_inset_ratio=0.10,
        )
        return _assign_strategy_result(
            terminals,
            orientation,
            meta,
            score_map,
            resolution_mode=semantic_strategy,
        )

    if semantic_strategy == "voltage_source_positive_from_plus_marker":
        score_map = _plus_marker_scores_by_side(binary, bbox, orientation)
        return _assign_strategy_result(
            terminals,
            orientation,
            meta,
            score_map,
            resolution_mode=semantic_strategy,
        )

    if semantic_strategy == "current_source_direction_from_arrow":
        score_map = _inner_half_mass_scores(binary, bbox, orientation)

        if orientation == "horizontal":
            marker_side, other_side, confidence, evidence_type = _choose_side(
                score_map,
                "left",
                "right",
                DEFAULT_FALLBACK_SIDE.get(orientation, "left"),
            )
        else:
            marker_side, other_side, confidence, evidence_type = _choose_side(
                score_map,
                "top",
                "bottom",
                DEFAULT_FALLBACK_SIDE.get(orientation, "top"),
            )

        semantic_roles = meta.get("semantic_roles", {})
        debug = {
            "orientation": orientation,
            "scores": score_map,
            "selected_arrow_head_side": marker_side,
            "selected_arrow_tail_side": other_side,
            "confidence": confidence,
            "evidence_type": evidence_type,
        }

        role_by_position = {
            marker_side: ("marker_side", semantic_roles.get("marker_side")),
            other_side: ("other_side", semantic_roles.get("other_side")),
        }

        for term in terminals:
            relative_position = term.get("relative_position")
            semantic_slot, semantic_name = role_by_position.get(relative_position, (None, None))
            if semantic_name is None:
                continue
            _set_term_semantic_fields(
                term,
                semantic_name=semantic_name,
                semantic_slot=semantic_slot,
                confidence=confidence,
                resolution_mode=semantic_strategy,
                evidence_type=evidence_type,
                debug=debug,
            )
        return terminals

    return terminals
