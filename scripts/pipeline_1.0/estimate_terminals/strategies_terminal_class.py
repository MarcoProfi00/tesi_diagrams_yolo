import cv2
import numpy as np

from .config import *
from .geometry import (
    geom_terminal_point_by_side_peak,
    geom_clamp_bbox_to_image,
)
from .probes import (
    get_terminal_class_far_probe_scores,
    get_terminal_class_probe_scores,
    score_point_directional_support,
)

# =========================================================
# STRATEGY: VARIABLE TERMINAL CLASS ("Terminal")
# Filosofia:
# - default = 1 terminale
# - 2 terminali solo se l'evidenza è davvero forte
# - nessun forcing dal bordo immagine
# =========================================================

# Score terminal one side candidate by points.
def _score_terminal_one_side_candidate_by_points(binary, bbox, side):
    point, peak_debug = geom_terminal_point_by_side_peak(binary, bbox, side)
    px, py = point

    dir_score = score_point_directional_support(
        binary,
        px,
        py,
        side,
        outward=10,
        inward=0,
        halfspan=2,
    )

    return dir_score, point, peak_debug


# Handle combined side scores.
def _combined_side_scores(local_scores, far_scores):
    return {
        side: float(local_scores.get(side, 0)) + 1.2 * float(far_scores.get(side, 0))
        for side in ("top", "bottom", "left", "right")
    }

# Terminal bounding box shape info.
def _terminal_bbox_shape_info(bbox):
    x1, y1, x2, y2 = bbox
    w = max(float(x2 - x1), 1.0)
    h = max(float(y2 - y1), 1.0)

    ratio_hw = h / w
    ratio_wh = w / h
    major_ratio = max(ratio_hw, ratio_wh)

    return {
        "width": w,
        "height": h,
        "ratio_hw": ratio_hw,
        "ratio_wh": ratio_wh,
        "major_ratio": major_ratio,
        "is_near_square": major_ratio <= TERMINAL_CLASS_NEAR_SQUARE_RATIO,
        "is_vertical": ratio_hw > TERMINAL_CLASS_NEAR_SQUARE_RATIO,
        "is_horizontal": ratio_wh > TERMINAL_CLASS_NEAR_SQUARE_RATIO,
    }


# Handle range overlap ratio.
def _range_overlap_ratio(a1, a2, b1, b2):
    inter = max(0, min(a2, b2) - max(a1, b1) + 1)
    base = max(1, min(a2 - a1 + 1, b2 - b1 + 1))
    return float(inter) / float(base)


# Handle component is side aligned external.
def _component_is_side_aligned_external(component_bbox, bbox):
    cx1, cy1, cx2, cy2 = component_bbox
    x1, y1, x2, y2 = bbox
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)
    comp_w = max(cx2 - cx1 + 1, 1)
    comp_h = max(cy2 - cy1 + 1, 1)

    central_x1 = x1 + int(round(0.20 * width))
    central_x2 = x2 - int(round(0.20 * width))
    central_y1 = y1 + int(round(0.20 * height))
    central_y2 = y2 - int(round(0.20 * height))

    gap_limit = TERMINAL_CLASS_EXTERNAL_KEEP_GAP
    overlap_limit = TERMINAL_CLASS_EXTERNAL_KEEP_OVERLAP_RATIO
    min_long_span = TERMINAL_CLASS_EXTERNAL_MIN_LONG_SPAN
    long_short_ratio = TERMINAL_CLASS_EXTERNAL_LONG_TO_SHORT_RATIO

    # Handle is horizontal stub.
    def is_horizontal_stub():
        return comp_w >= max(min_long_span, int(round(long_short_ratio * comp_h)))

    # Handle is vertical stub.
    def is_vertical_stub():
        return comp_h >= max(min_long_span, int(round(long_short_ratio * comp_w)))

    if (
        cx1 >= x2 + 1
        and (cx1 - x2) <= gap_limit
        and _range_overlap_ratio(cy1, cy2, central_y1, central_y2) >= overlap_limit
        and is_horizontal_stub()
    ):
        return True

    if (
        cx2 <= x1 - 1
        and (x1 - cx2) <= gap_limit
        and _range_overlap_ratio(cy1, cy2, central_y1, central_y2) >= overlap_limit
        and is_horizontal_stub()
    ):
        return True

    if (
        cy1 >= y2 + 1
        and (cy1 - y2) <= gap_limit
        and _range_overlap_ratio(cx1, cx2, central_x1, central_x2) >= overlap_limit
        and is_vertical_stub()
    ):
        return True

    if (
        cy2 <= y1 - 1
        and (y1 - cy2) <= gap_limit
        and _range_overlap_ratio(cx1, cx2, central_x1, central_x2) >= overlap_limit
        and is_vertical_stub()
    ):
        return True

    return False


# Check whether a short external fragment is actually the bar of a polarity "+".
def _component_is_polarity_plus_marker(binary, component_bbox):
    cx1, cy1, cx2, cy2 = map(int, component_bbox)
    comp_w = max(cx2 - cx1 + 1, 1)
    comp_h = max(cy2 - cy1 + 1, 1)
    probe = TERMINAL_CLASS_POLARITY_MARKER_PROBE
    min_cross_pixels = TERMINAL_CLASS_POLARITY_MARKER_MIN_CROSS_PIXELS

    debug = {
        "enabled": True,
        "component_bbox": [cx1, cy1, cx2, cy2],
        "probe": int(probe),
        "min_cross_pixels": int(min_cross_pixels),
        "is_plus_marker": False,
    }

    # Horizontal bar of a "+": look for a vertical stroke crossing it.
    if comp_w >= comp_h:
        best_above = 0
        best_below = 0

        for x in range(cx1, cx2 + 1):
            above = int(np.count_nonzero(binary[max(0, cy1 - probe):cy1, x] > 0))
            below = int(np.count_nonzero(binary[cy2 + 1:min(binary.shape[0], cy2 + 1 + probe), x] > 0))
            best_above = max(best_above, above)
            best_below = max(best_below, below)

            if above >= min_cross_pixels and below >= min_cross_pixels:
                debug.update({
                    "axis": "horizontal_bar",
                    "cross_x": int(x),
                    "above_pixels": above,
                    "below_pixels": below,
                    "is_plus_marker": True,
                })
                return True, debug

        debug.update({
            "axis": "horizontal_bar",
            "best_above_pixels": best_above,
            "best_below_pixels": best_below,
        })
        return False, debug

    # Vertical bar of a "+": symmetric check for a horizontal stroke.
    best_left = 0
    best_right = 0

    for y in range(cy1, cy2 + 1):
        left = int(np.count_nonzero(binary[y, max(0, cx1 - probe):cx1] > 0))
        right = int(np.count_nonzero(binary[y, cx2 + 1:min(binary.shape[1], cx2 + 1 + probe)] > 0))
        best_left = max(best_left, left)
        best_right = max(best_right, right)

        if left >= min_cross_pixels and right >= min_cross_pixels:
            debug.update({
                "axis": "vertical_bar",
                "cross_y": int(y),
                "left_pixels": left,
                "right_pixels": right,
                "is_plus_marker": True,
            })
            return True, debug

    debug.update({
        "axis": "vertical_bar",
        "best_left_pixels": best_left,
        "best_right_pixels": best_right,
    })
    return False, debug


# Build terminal text suppressed binary image.
def _build_terminal_text_suppressed_binary(binary, bbox):
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)
    w = max(x2 - x1, 1)
    h = max(y2 - y1, 1)

    margin = max(
        TERMINAL_CLASS_TEXT_SUPPRESS_MARGIN_MIN,
        int(round(TERMINAL_CLASS_TEXT_SUPPRESS_MARGIN_RATIO * max(w, h))),
    )

    rx1 = max(0, x1 - margin)
    ry1 = max(0, y1 - margin)
    rx2 = min(binary.shape[1] - 1, x2 + margin)
    ry2 = min(binary.shape[0] - 1, y2 + margin)

    roi = binary[ry1:ry2 + 1, rx1:rx2 + 1]
    roi_fg = (roi > 0).astype(np.uint8)

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(roi_fg, connectivity=8)

    # seed = regione centrale del terminale:
    # tende a contenere il pallino vero, ma esclude testo/simboli
    # troppo vicini ai bordi del bbox.
    seed_w = max(TERMINAL_CLASS_SEED_MIN_SIZE, int(round(w * (1.0 - 2.0 * TERMINAL_CLASS_SEED_INSET_RATIO))))
    seed_h = max(TERMINAL_CLASS_SEED_MIN_SIZE, int(round(h * (1.0 - 2.0 * TERMINAL_CLASS_SEED_INSET_RATIO))))

    bbox_x1_in_roi = x1 - rx1
    bbox_y1_in_roi = y1 - ry1

    sx1 = max(0, bbox_x1_in_roi + int(round((w - seed_w) / 2.0)))
    sy1 = max(0, bbox_y1_in_roi + int(round((h - seed_h) / 2.0)))
    sx2 = min(roi.shape[1] - 1, sx1 + seed_w - 1)
    sy2 = min(roi.shape[0] - 1, sy1 + seed_h - 1)

    seed_labels = np.unique(labels[sy1:sy2 + 1, sx1:sx2 + 1])

    cleaned_roi = np.zeros_like(roi, dtype=np.uint8)
    kept_labels = []
    kept_external_labels = []
    rejected_external_labels = []
    external_label_debug = []

    for lab in seed_labels:
        if lab == 0:
            continue
        cleaned_roi[labels == lab] = 255
        kept_labels.append(int(lab))

    for lab in range(1, num_labels):
        if lab in seed_labels:
            continue

        left = int(stats[lab, cv2.CC_STAT_LEFT])
        top = int(stats[lab, cv2.CC_STAT_TOP])
        comp_w = int(stats[lab, cv2.CC_STAT_WIDTH])
        comp_h = int(stats[lab, cv2.CC_STAT_HEIGHT])
        comp_bbox = (
            rx1 + left,
            ry1 + top,
            rx1 + left + comp_w - 1,
            ry1 + top + comp_h - 1,
        )

        if not _component_is_side_aligned_external(comp_bbox, (x1, y1, x2, y2)):
            continue

        is_plus_marker, plus_debug = _component_is_polarity_plus_marker(binary, comp_bbox)
        external_label_debug.append({
            "label": int(lab),
            "component_bbox": [int(v) for v in comp_bbox],
            "polarity_plus_debug": plus_debug,
        })

        if is_plus_marker:
            rejected_external_labels.append(int(lab))
            continue

        cleaned_roi[labels == lab] = 255
        kept_external_labels.append(int(lab))

    cleaned = binary.copy()
    cleaned[ry1:ry2 + 1, rx1:rx2 + 1] = cleaned_roi

    debug = {
        "enabled": True,
        "roi": [int(rx1), int(ry1), int(rx2), int(ry2)],
        "seed_bbox_in_roi": [int(sx1), int(sy1), int(sx2), int(sy2)],
        "connected_components": int(num_labels - 1),
        "kept_labels": kept_labels,
        "kept_external_labels": kept_external_labels,
        "rejected_external_labels": rejected_external_labels,
        "external_label_debug": external_label_debug,
    }

    return cleaned, debug

# Apply terminal shape prior.
def _apply_terminal_shape_prior(bbox, side_scores):
    shape = _terminal_bbox_shape_info(bbox)
    adjusted = {k: float(v) for k, v in side_scores.items()}

    if shape["is_near_square"]:
        return adjusted

    if shape["ratio_hw"] >= TERMINAL_CLASS_SHAPE_RATIO_STRONG:
        adjusted["top"] += TERMINAL_CLASS_SHAPE_BONUS_STRONG
        adjusted["bottom"] += TERMINAL_CLASS_SHAPE_BONUS_STRONG
    elif shape["ratio_hw"] >= TERMINAL_CLASS_SHAPE_RATIO_WEAK:
        adjusted["top"] += TERMINAL_CLASS_SHAPE_BONUS_WEAK
        adjusted["bottom"] += TERMINAL_CLASS_SHAPE_BONUS_WEAK
    elif shape["ratio_wh"] >= TERMINAL_CLASS_SHAPE_RATIO_STRONG:
        adjusted["left"] += TERMINAL_CLASS_SHAPE_BONUS_STRONG
        adjusted["right"] += TERMINAL_CLASS_SHAPE_BONUS_STRONG
    elif shape["ratio_wh"] >= TERMINAL_CLASS_SHAPE_RATIO_WEAK:
        adjusted["left"] += TERMINAL_CLASS_SHAPE_BONUS_WEAK
        adjusted["right"] += TERMINAL_CLASS_SHAPE_BONUS_WEAK

    return adjusted


# Handle best single side.
def _best_single_side(binary, bbox, local_scores, far_scores):
    combined_raw = _combined_side_scores(local_scores, far_scores)
    combined = _apply_terminal_shape_prior(bbox, combined_raw)
    best_side = max(combined, key=combined.get)
    ordered = sorted(combined.items(), key=lambda kv: kv[1], reverse=True)

    second_side = ordered[1][0]
    second_score = ordered[1][1]

    return {
        "best_side": best_side,
        "best_score": combined[best_side],
        "second_side": second_side,
        "second_score": second_score,
        "combined_scores": combined,
    }


# Handle horizontal two side evidence.
def _horizontal_two_side_evidence(local_scores, far_scores):
    left_local = local_scores["left"]
    right_local = local_scores["right"]
    top_local = local_scores["top"]
    bottom_local = local_scores["bottom"]

    left_far = far_scores["left"]
    right_far = far_scores["right"]
    top_far = far_scores["top"]
    bottom_far = far_scores["bottom"]

    pair_local_min = min(left_local, right_local)
    pair_far_min = min(left_far, right_far)

    pair_score = (
        left_local + right_local
        + 1.0 * (left_far + right_far)
    )

    perpendicular_score = (
        top_local + bottom_local
        + 0.8 * (top_far + bottom_far)
    )

    valid = (
        pair_local_min >= TERMINAL_CLASS_TWO_SIDE_MIN
        and pair_far_min >= TERMINAL_CLASS_FAR_MIN
        and pair_score > perpendicular_score * TERMINAL_CLASS_TWO_AXIS_MARGIN
        and min(left_local, right_local) >= TERMINAL_CLASS_TWO_BALANCE_RATIO * max(left_local, right_local)
    )

    return {
        "valid": valid,
        "orientation": "horizontal",
        "pair_score": float(pair_score),
        "perpendicular_score": float(perpendicular_score),
        "pair_local_min": float(pair_local_min),
        "pair_far_min": float(pair_far_min),
    }


# Handle vertical two side evidence.
def _vertical_two_side_evidence(local_scores, far_scores):
    left_local = local_scores["left"]
    right_local = local_scores["right"]
    top_local = local_scores["top"]
    bottom_local = local_scores["bottom"]

    left_far = far_scores["left"]
    right_far = far_scores["right"]
    top_far = far_scores["top"]
    bottom_far = far_scores["bottom"]

    pair_local_min = min(top_local, bottom_local)
    pair_far_min = min(top_far, bottom_far)

    pair_score = (
        top_local + bottom_local
        + 1.0 * (top_far + bottom_far)
    )

    perpendicular_score = (
        left_local + right_local
        + 0.8 * (left_far + right_far)
    )

    valid = (
        pair_local_min >= TERMINAL_CLASS_TWO_SIDE_MIN
        and pair_far_min >= TERMINAL_CLASS_FAR_MIN
        and pair_score > perpendicular_score * TERMINAL_CLASS_TWO_AXIS_MARGIN
        and min(top_local, bottom_local) >= TERMINAL_CLASS_TWO_BALANCE_RATIO * max(top_local, bottom_local)
    )

    return {
        "valid": valid,
        "orientation": "vertical",
        "pair_score": float(pair_score),
        "perpendicular_score": float(perpendicular_score),
        "pair_local_min": float(pair_local_min),
        "pair_far_min": float(pair_far_min),
    }


# Handle relaxed two side evidence.
def _relaxed_two_side_evidence(local_scores, far_scores, orientation):
    if orientation == "horizontal":
        pair_sides = ("left", "right")
        perp_sides = ("top", "bottom")
    else:
        pair_sides = ("top", "bottom")
        perp_sides = ("left", "right")

    pair_combined = [
        float(local_scores[s]) + float(far_scores[s])
        for s in pair_sides
    ]
    perp_combined = [
        float(local_scores[s]) + 0.8 * float(far_scores[s])
        for s in perp_sides
    ]

    pair_score = sum(pair_combined)
    perpendicular_score = sum(perp_combined)

    valid = (
        min(pair_combined) >= TERMINAL_CLASS_TWO_SIDE_RELAXED_MIN
        and max(pair_combined) >= TERMINAL_CLASS_TWO_SIDE_RELAXED_STRONG
        and pair_score > max(1.0, perpendicular_score) * TERMINAL_CLASS_TWO_SIDE_RELAXED_AXIS_MARGIN
    )

    return {
        "valid": valid,
        "orientation": orientation,
        "pair_score": float(pair_score),
        "perpendicular_score": float(perpendicular_score),
        "pair_combined_min": float(min(pair_combined)),
        "pair_combined_max": float(max(pair_combined)),
    }


def _are_adjacent_sides(side_a: str, side_b: str) -> bool:
    return {side_a, side_b} in (
        {"top", "left"},
        {"top", "right"},
        {"bottom", "left"},
        {"bottom", "right"},
    )


# Handle adjacent two side evidence for corner-like Terminal symbols.
def _adjacent_two_side_evidence(local_scores, far_scores, shape_info, combined_scores):
    ordered = sorted(combined_scores.items(), key=lambda kv: kv[1], reverse=True)
    if len(ordered) < 3:
        return {
            "valid": False,
            "orientation": None,
            "reason": "not_enough_sides",
        }

    best_side, best_score = ordered[0]
    second_side, second_score = ordered[1]
    third_side, third_score = ordered[2]

    valid = (
        shape_info["is_near_square"]
        and _are_adjacent_sides(best_side, second_side)
        and best_score >= TERMINAL_CLASS_ADJACENT_TWO_SIDE_STRONG
        and second_score >= TERMINAL_CLASS_ADJACENT_TWO_SIDE_MIN
        and second_score >= max(
            TERMINAL_CLASS_ADJACENT_TWO_SIDE_MIN,
            third_score * TERMINAL_CLASS_ADJACENT_THIRD_MARGIN,
        )
        and float(local_scores.get(best_side, 0)) >= TERMINAL_CLASS_ADJACENT_LOCAL_MIN
        and float(local_scores.get(second_side, 0)) >= TERMINAL_CLASS_ADJACENT_LOCAL_MIN
        and float(far_scores.get(best_side, 0)) >= TERMINAL_CLASS_FAR_MIN
        and float(far_scores.get(second_side, 0)) >= TERMINAL_CLASS_FAR_MIN
    )

    orientation = f"corner_{best_side}_{second_side}" if valid else None
    return {
        "valid": valid,
        "orientation": orientation,
        "best_side": best_side,
        "second_side": second_side,
        "third_side": third_side,
        "best_score": float(best_score),
        "second_score": float(second_score),
        "third_score": float(third_score),
        "second_vs_third_margin": round(float(second_score) / max(float(third_score), 1.0), 4),
        "shape_is_near_square": bool(shape_info["is_near_square"]),
    }


# Classify terminal cardinality.
def classify_terminal_cardinality(binary, bbox, default_side="right", text_suppression_debug=None):
    local_scores = get_terminal_class_probe_scores(binary, bbox)
    far_scores = get_terminal_class_far_probe_scores(binary, bbox)
    shape_info = _terminal_bbox_shape_info(bbox)

    single_eval = _best_single_side(binary, bbox, local_scores, far_scores)
    horiz_eval = _horizontal_two_side_evidence(local_scores, far_scores)
    vert_eval = _vertical_two_side_evidence(local_scores, far_scores)
    horiz_relaxed = _relaxed_two_side_evidence(local_scores, far_scores, "horizontal")
    vert_relaxed = _relaxed_two_side_evidence(local_scores, far_scores, "vertical")
    adjacent_eval = _adjacent_two_side_evidence(
        local_scores,
        far_scores,
        shape_info,
        single_eval["combined_scores"],
    )

    local_scores["far_scores"] = far_scores
    local_scores["single_side_evaluation"] = single_eval
    local_scores["two_side_evaluations"] = {
        "horizontal": horiz_eval,
        "vertical": vert_eval,
    }
    local_scores["two_side_relaxed_evaluations"] = {
        "horizontal": horiz_relaxed,
        "vertical": vert_relaxed,
    }
    if adjacent_eval["valid"]:
        local_scores["adjacent_two_side_evaluation"] = adjacent_eval

    relaxed_external_fragmented = False
    if text_suppression_debug is not None:
        connected_components = int(text_suppression_debug.get("connected_components", 0))
        kept_external_labels = text_suppression_debug.get("kept_external_labels", [])
        relaxed_external_fragmented = (
            connected_components >= 3
            or len(kept_external_labels) >= 2
        )
    local_scores["relaxed_external_fragmented"] = relaxed_external_fragmented

    # 2 terminali solo se batte chiaramente la migliore ipotesi mono-terminale
    TWO_VS_ONE_MIN_ADVANTAGE = 2.0
    TWO_SIDE_MARGIN = 1.10
    RELAXED_TWO_SINGLE_VETO_RATIO = 2.25
    RELAXED_TWO_SINGLE_VETO_DELTA = 48.0

    horiz_beats_one = horiz_eval["pair_score"] >= single_eval["best_score"] + TWO_VS_ONE_MIN_ADVANTAGE
    vert_beats_one = vert_eval["pair_score"] >= single_eval["best_score"] + TWO_VS_ONE_MIN_ADVANTAGE
    relaxed_single_veto = (
        single_eval["best_score"] >= max(
            RELAXED_TWO_SINGLE_VETO_DELTA,
            single_eval["second_score"] * RELAXED_TWO_SINGLE_VETO_RATIO,
        )
    )
    relaxed_fragmented_can_override_single_veto = (
        relaxed_external_fragmented
        and shape_info["is_near_square"]
        and single_eval["second_score"] >= TERMINAL_CLASS_FAR_MIN
    )
    local_scores["relaxed_fragmented_can_override_single_veto"] = relaxed_fragmented_can_override_single_veto
    horizontal_relaxed_shape_ok = shape_info["is_near_square"] or shape_info["is_horizontal"]
    vertical_relaxed_shape_ok = shape_info["is_near_square"] or shape_info["is_vertical"]
    relaxed_two_single_margin = 1.12

    if (
        horiz_eval["valid"]
        and horiz_beats_one
        and (
            not vert_eval["valid"]
            or horiz_eval["pair_score"] > vert_eval["pair_score"] * TWO_SIDE_MARGIN
        )
    ):
        local_scores["decision_mode"] = "terminal_cardinality_two_horizontal"
        return 2, "horizontal", local_scores

    if (
        horizontal_relaxed_shape_ok
        and relaxed_external_fragmented
        and horiz_relaxed["valid"]
        and not vert_relaxed["valid"]
        and (
            not relaxed_single_veto
            or relaxed_fragmented_can_override_single_veto
            or (
                shape_info["is_horizontal"]
                and horiz_relaxed["pair_score"] >= single_eval["best_score"] * relaxed_two_single_margin
            )
        )
    ):
        local_scores["decision_mode"] = "terminal_cardinality_two_horizontal_relaxed"
        return 2, "horizontal", local_scores

    if (
        vert_eval["valid"]
        and vert_beats_one
        and (
            not horiz_eval["valid"]
            or vert_eval["pair_score"] > horiz_eval["pair_score"] * TWO_SIDE_MARGIN
        )
    ):
        local_scores["decision_mode"] = "terminal_cardinality_two_vertical"
        return 2, "vertical", local_scores

    if (
        adjacent_eval["valid"]
        and not horiz_eval["valid"]
        and not vert_eval["valid"]
    ):
        local_scores["decision_mode"] = "terminal_cardinality_two_adjacent"
        return 2, adjacent_eval["orientation"], local_scores

    if (
        vertical_relaxed_shape_ok
        and relaxed_external_fragmented
        and vert_relaxed["valid"]
        and not horiz_relaxed["valid"]
        and (
            not relaxed_single_veto
            or relaxed_fragmented_can_override_single_veto
            or (
                shape_info["is_vertical"]
                and vert_relaxed["pair_score"] >= single_eval["best_score"] * relaxed_two_single_margin
            )
        )
    ):
        local_scores["decision_mode"] = "terminal_cardinality_two_vertical_relaxed"
        return 2, "vertical", local_scores

    if relaxed_single_veto:
        local_scores["relaxed_two_terminal_veto"] = {
            "enabled": True,
            "best_score": float(single_eval["best_score"]),
            "second_score": float(single_eval["second_score"]),
            "ratio_threshold": RELAXED_TWO_SINGLE_VETO_RATIO,
            "delta_threshold": RELAXED_TWO_SINGLE_VETO_DELTA,
        }

    local_scores["decision_mode"] = "terminal_cardinality_default_one"
    return 1, single_eval["best_side"], local_scores

# Handle opposite side.
def _opposite_side(side):
    return {
        "top": "bottom",
        "bottom": "top",
        "left": "right",
        "right": "left",
    }[side]


# Score terminal one side candidate by through support.
def _score_terminal_one_side_candidate_by_through_support(binary, bbox, side):
    point, peak_debug = geom_terminal_point_by_side_peak(binary, bbox, side)
    px, py = point

    outside = score_point_directional_support(
        binary,
        px,
        py,
        side,
        outward=12,
        inward=0,
        halfspan=1,
    )

    inside = score_point_directional_support(
        binary,
        px,
        py,
        _opposite_side(side),
        outward=6,
        inward=0,
        halfspan=1,
    )

    return {
        "point": point,
        "outside": float(outside),
        "inside": float(inside),
        "through_score": float(outside + 0.9 * inside),
        "peak_debug": peak_debug,
    }


# Detect terminal one side.
def detect_terminal_one_side(binary, bbox, default_side="right", precomputed_scores=None):
    scores = precomputed_scores if precomputed_scores is not None else get_terminal_class_probe_scores(binary, bbox)
    far_scores = scores.get("far_scores")
    if far_scores is None:
        far_scores = get_terminal_class_far_probe_scores(binary, bbox)

    combined_raw = _combined_side_scores(scores, far_scores)
    combined = _apply_terminal_shape_prior(bbox, combined_raw)
    scores["combined_scores_raw"] = combined_raw
    scores["combined_scores_shape_adjusted"] = combined
    shape_info = _terminal_bbox_shape_info(bbox)
    scores["bbox_shape_debug"] = shape_info
    ordered = sorted(combined.items(), key=lambda kv: kv[1], reverse=True)

    best_side, best_score = ordered[0]
    second_side, second_score = ordered[1]

    CLEAR_MARGIN = 1.75
    CLEAR_SECOND_MAX = 12.0

    THROUGH_MARGIN = 1.20
    THROUGH_MIN_OUTSIDE = 4.0

    POINT_MARGIN = 1.15
    POINT_MIN_SCORE = 2
    POINT_FAR_WEIGHT = 0.6

    # -------------------------------------------------
    # 1) Caso davvero chiaro: solo se il secondo lato è molto basso
    # -------------------------------------------------
    if (
        far_scores.get(best_side, 0) >= TERMINAL_CLASS_FAR_MIN
        and second_score <= CLEAR_SECOND_MAX
        and best_score > max(8.0, second_score * CLEAR_MARGIN)
    ):
        return [{"name": "t1", "relative_position": best_side}], best_side

    # -------------------------------------------------
    # 2) Tie-break principale: continuità fuori+dentro sullo stesso asse
    # -------------------------------------------------
    # IMPORTANTE:
    # per terminali piccoli / quasi quadrati (tipici output terminal circolari/ovali),
    # il supporto "inside" è spesso rumore del simbolo stesso.
    # In quel caso saltiamo del tutto questo step.
    through_debug = {}
    scores["through_support_skipped_for_near_square"] = bool(shape_info["is_near_square"])

    if not shape_info["is_near_square"]:
        candidate_sides = [
            side
            for side, score in combined.items()
            if score >= max(10.0, 0.35 * best_score)
        ]

        for side in candidate_sides:
            through_debug[side] = _score_terminal_one_side_candidate_by_through_support(
                binary,
                bbox,
                side,
            )

        scores["through_support_debug"] = through_debug

        if through_debug:
            ordered_through = sorted(
                through_debug.items(),
                key=lambda kv: kv[1]["through_score"],
                reverse=True,
            )

            best_through_side, best_through = ordered_through[0]
            second_through_score = (
                ordered_through[1][1]["through_score"]
                if len(ordered_through) > 1 else 0.0
            )

            if (
                best_through["outside"] >= THROUGH_MIN_OUTSIDE
                and best_through["through_score"] > second_through_score * THROUGH_MARGIN
            ):
                return [{"name": "t1", "relative_position": best_through_side}], best_through_side
    else:
        scores["through_support_debug"] = {}

    # -------------------------------------------------
    # 3) Tie-break secondario: validazione point-based
    # -------------------------------------------------
    point_scores = {}
    point_debug = {}

    for side in ("top", "bottom", "left", "right"):
        p_score, point, peak_debug = _score_terminal_one_side_candidate_by_points(
            binary,
            bbox,
            side,
        )
        point_scores[side] = p_score
        point_debug[side] = {
            "point": point,
            "directional_support": p_score,
            "peak_debug": peak_debug,
        }

    scores["point_debug_one_side"] = point_debug

    if shape_info["is_near_square"]:
        # Per i terminali piccoli / circolari / quasi quadrati
        # pesiamo di più l'evidenza esterna reale.
        point_combined = {
            side: (
                1.00 * point_scores[side]
                + 1.00 * far_scores.get(side, 0)
                + 0.35 * scores.get(side, 0)
            )
            for side in ("top", "bottom", "left", "right")
        }
        point_margin_used = 1.08
    else:
        point_combined = {
            side: point_scores[side] + POINT_FAR_WEIGHT * far_scores.get(side, 0)
            for side in ("top", "bottom", "left", "right")
        }
        point_margin_used = POINT_MARGIN

    scores["point_combined_one_side"] = point_combined

    ordered_point = sorted(point_combined.items(), key=lambda kv: kv[1], reverse=True)
    best_point_side, best_point_score = ordered_point[0]
    second_point_score = ordered_point[1][1]

    if (
        point_scores.get(best_point_side, 0) >= POINT_MIN_SCORE
        and best_point_score > second_point_score * point_margin_used
    ):
        return [{"name": "t1", "relative_position": best_point_side}], best_point_side

    # -------------------------------------------------
    # 4) Fallback: migliore lato combinato
    # -------------------------------------------------
    return [{"name": "t1", "relative_position": best_side}], best_side


# Detect terminal two sides.
def detect_terminal_two_sides(binary, bbox, precomputed_scores=None):
    scores = precomputed_scores if precomputed_scores is not None else get_terminal_class_probe_scores(binary, bbox)
    far_scores = scores.get("far_scores")
    if far_scores is None:
        far_scores = get_terminal_class_far_probe_scores(binary, bbox)

    adjacent_eval = scores.get("adjacent_two_side_evaluation") or {}
    orientation = adjacent_eval.get("orientation")
    if isinstance(orientation, str) and orientation.startswith("corner_"):
        _, side_a, side_b = orientation.split("_", 2)
        return [
            {"name": "t1", "relative_position": side_a},
            {"name": "t2", "relative_position": side_b},
        ], orientation

    lr_score = scores["left"] + scores["right"] + 1.0 * (far_scores["left"] + far_scores["right"])
    tb_score = scores["top"] + scores["bottom"] + 1.0 * (far_scores["top"] + far_scores["bottom"])

    if lr_score >= tb_score:
        return [
            {"name": "t1", "relative_position": "left"},
            {"name": "t2", "relative_position": "right"},
        ], "horizontal"

    return [
        {"name": "t1", "relative_position": "top"},
        {"name": "t2", "relative_position": "bottom"},
    ], "vertical"


# Detect terminal auto one or two.
def detect_terminal_auto_one_or_two(binary, bbox, default_side="right"):
    shape_info = _terminal_bbox_shape_info(bbox)

    # Per la classe Terminal applichiamo SEMPRE la pulizia locale:
    # il componente reale è il pallino/bubble + gli eventuali wire
    # che lo toccano, non il testo vicino.
    working_binary, text_suppression_debug = _build_terminal_text_suppressed_binary(
        binary,
        bbox,
    )

    text_suppression_debug["reason"] = "always_applied_for_terminal_class"

    cardinality, mode, scores = classify_terminal_cardinality(
        working_binary,
        bbox,
        default_side=default_side,
        text_suppression_debug=text_suppression_debug,
    )

    scores["bbox_shape_debug"] = shape_info
    scores["terminal_text_suppression_debug"] = text_suppression_debug

    if cardinality == 1:
        terminals_def, orientation = detect_terminal_one_side(
            working_binary,
            bbox,
            default_side=default_side,
            precomputed_scores=scores,
        )
        scores["final_mode"] = "one_terminal"
        return terminals_def, orientation, scores

    terminals_def, orientation = detect_terminal_two_sides(
        working_binary,
        bbox,
        precomputed_scores=scores,
    )
    scores["final_mode"] = "two_terminal"
    return terminals_def, orientation, scores
