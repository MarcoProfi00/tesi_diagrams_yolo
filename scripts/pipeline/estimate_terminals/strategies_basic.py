import numpy as np
from .config import *
from .geometry import (
    geom_clamp_bbox_to_image,
    geom_infer_orientation_from_bbox,
    geom_terminal_point_by_side_peak,
)
from .probes import (
    get_local_terminal_probe_scores_center,
    get_local_terminal_probe_scores_multi_anchor,
    get_round_source_probe_scores,
    get_round_source_far_probe_scores,
    get_led_probe_scores,
    get_led_far_probe_scores,
    img_count_foreground_pixels,
    probe_get_side_scores,
    score_point_directional_support,
)


# Group consecutive indices.
def _group_consecutive_indices(indices):
    if not indices:
        return []

    groups = [[int(indices[0])]]
    for idx in indices[1:]:
        idx = int(idx)
        if idx <= groups[-1][-1] + 1:
            groups[-1].append(idx)
        else:
            groups.append([idx])
    return groups

# =========================================================
# STRATEGY: ONE-TERMINAL COMPONENTS
# =========================================================
# Score one terminal candidate side.
def _score_one_terminal_candidate_side(binary, bbox, side):
    point, peak_debug = geom_terminal_point_by_side_peak(binary, bbox, side)
    px, py = point

    dir_score = score_point_directional_support(
        binary,
        px,
        py,
        side,
        outward=12,
        inward=0,
        halfspan=2,
    )

    return dir_score, point, peak_debug


# Handle strategy detect connected side.
def strategy_detect_connected_side(binary, bbox):
    # -------------------------------------------------
    # 1) Validazione diretta sui 4 lati candidati
    # -------------------------------------------------
    point_scores = {}
    point_debug = {}

    for side in ("top", "bottom", "left", "right"):
        score, point, peak_debug = _score_one_terminal_candidate_side(
            binary, bbox, side
        )
        point_scores[side] = score
        point_debug[side] = {
            "point": point,
            "directional_support": score,
            "peak_debug": peak_debug,
        }

    ordered = sorted(
        ("top", "bottom", "left", "right"),
        key=lambda s: point_scores[s],
        reverse=True
    )

    best_side = ordered[0]
    second_side = ordered[1]
    best_score = point_scores[best_side]
    second_score = point_scores[second_side]

    POINT_MIN_SIDE_SCORE = 2
    POINT_MARGIN = 1.15

    if best_score >= POINT_MIN_SIDE_SCORE and best_score > second_score * POINT_MARGIN:
        debug_scores = dict(point_scores)
        debug_scores["decision_mode"] = "one_terminal_point_validation"
        debug_scores["best_side"] = best_side
        debug_scores["best_score"] = best_score
        debug_scores["second_side"] = second_side
        debug_scores["second_side_score"] = second_score
        debug_scores["point_debug"] = point_debug
        return best_side, debug_scores

    # -------------------------------------------------
    # 2) Fallback: vecchia strategia a bande centrali
    # -------------------------------------------------
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)
    xc = int(round((x1 + x2) / 2))
    yc = int(round((y1 + y2) / 2))
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)
    half_band_x = max(4, int(width * SIDE_CENTER_RATIO / 2))
    half_band_y = max(4, int(height * SIDE_CENTER_RATIO / 2))

    side_scores = {
        "top": img_count_foreground_pixels(
            binary,
            xc - half_band_x,
            y1 - SIDE_SAMPLE_THICKNESS,
            xc + half_band_x + 1,
            y1
        ),
        "bottom": img_count_foreground_pixels(
            binary,
            xc - half_band_x,
            y2 + 1,
            xc + half_band_x + 1,
            y2 + 1 + SIDE_SAMPLE_THICKNESS
        ),
        "left": img_count_foreground_pixels(
            binary,
            x1 - SIDE_SAMPLE_THICKNESS,
            yc - half_band_y,
            x1,
            yc + half_band_y + 1
        ),
        "right": img_count_foreground_pixels(
            binary,
            x2 + 1,
            yc - half_band_y,
            x2 + 1 + SIDE_SAMPLE_THICKNESS,
            yc + half_band_y + 1
        ),
    }

    coarse_best_side = max(side_scores, key=side_scores.get)
    side_scores["point_scores"] = point_scores
    side_scores["point_debug"] = point_debug
    side_scores["decision_mode"] = "one_terminal_coarse_center_fallback"

    if side_scores[coarse_best_side] < SIDE_SCORE_MIN_PIXELS:
        return None, side_scores

    return coarse_best_side, side_scores

# Resolve one terminal orientation.
def resolve_one_terminal_orientation(meta: dict, connected_side: str):
    orientations = meta.get("orientations", {})
    for orientation_name, terminals_def in orientations.items():
        for term_def in terminals_def:
            if term_def.get("relative_position") == connected_side:
                return terminals_def, orientation_name

    default_orientation = meta.get("default_orientation")
    if default_orientation is None:
        raise ValueError("Impossibile risolvere one_terminal_by_orientation e manca default_orientation.")
    terminals_def = orientations.get(default_orientation)
    if terminals_def is None:
        raise ValueError(f"Nessuna definizione terminali per default_orientation '{default_orientation}'")
    return terminals_def, default_orientation

# =========================================================
# STRATEGY: TWO-TERMINAL COMPONENTS
# =========================================================
# Handle decide axis from scores.
def _decide_axis_from_scores(side_scores):
    lr_pair = min(side_scores["left"], side_scores["right"])
    tb_pair = min(side_scores["top"], side_scores["bottom"])
    lr_score = side_scores["left"] + side_scores["right"]
    tb_score = side_scores["top"] + side_scores["bottom"]

    if lr_pair >= TERMINAL_PROBE_MIN_SIDE_SCORE and lr_score > tb_score * TERMINAL_PROBE_AXIS_MARGIN:
        return "horizontal"
    if tb_pair >= TERMINAL_PROBE_MIN_SIDE_SCORE and tb_score > lr_score * TERMINAL_PROBE_AXIS_MARGIN:
        return "vertical"
    return None

# Handle strategy detect two terminal orientation generic.
def strategy_detect_two_terminal_orientation_generic(binary, bbox, default_orientation="horizontal"):
    side_scores = get_local_terminal_probe_scores_center(binary, bbox)
    orientation = _decide_axis_from_scores(side_scores)
    if orientation is not None:
        side_scores["decision_mode"] = "local_terminal_probes_center"
        return orientation, side_scores

    coarse_scores = probe_get_side_scores(binary, bbox)
    coarse_orientation = None
    lr_score = coarse_scores["left"] + coarse_scores["right"]
    tb_score = coarse_scores["top"] + coarse_scores["bottom"]
    if coarse_scores["left"] >= SIDE_SCORE_MIN_PIXELS and coarse_scores["right"] >= SIDE_SCORE_MIN_PIXELS and lr_score > tb_score * AXIS_SCORE_MARGIN:
        coarse_orientation = "horizontal"
    elif coarse_scores["top"] >= SIDE_SCORE_MIN_PIXELS and coarse_scores["bottom"] >= SIDE_SCORE_MIN_PIXELS and tb_score > lr_score * AXIS_SCORE_MARGIN:
        coarse_orientation = "vertical"

    if coarse_orientation is not None:
        merged = dict(side_scores)
        merged["coarse_scores"] = coarse_scores
        merged["decision_mode"] = "coarse_side_bands_after_local"
        return coarse_orientation, merged

    side_scores["decision_mode"] = "bbox_fallback_after_local_probes"
    return geom_infer_orientation_from_bbox(bbox, default_orientation=default_orientation), side_scores


# Detect two terminal orientation capacitor.
def detect_two_terminal_orientation_capacitor(binary, bbox, default_orientation="horizontal"):
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)
    width = max(x2 - x1 + 1, 1)
    height = max(y2 - y1 + 1, 1)

    inset_x = max(2, int(round(width * 0.18)))
    inset_y = max(2, int(round(height * 0.18)))
    rx1 = min(max(x1, x1 + inset_x), x2)
    rx2 = max(min(x2 + 1, x2 + 1 - inset_x), rx1 + 1)
    ry1 = min(max(y1, y1 + inset_y), y2)
    ry2 = max(min(y2 + 1, y2 + 1 - inset_y), ry1 + 1)
    inner = binary[ry1:ry2, rx1:rx2]

    if inner.size:
        row_proj = np.count_nonzero(inner > 0, axis=1)
        col_proj = np.count_nonzero(inner > 0, axis=0)

        # Handle peak count.
        def peak_count(proj):
            if len(proj) == 0:
                return 0, 0
            max_score = int(proj.max()) if len(proj) else 0
            if max_score <= 0:
                return 0, 0
            keep_threshold = max(2, int(round(max_score * 0.68)))
            kept = [idx for idx, value in enumerate(proj.tolist()) if int(value) >= keep_threshold]
            groups = _group_consecutive_indices(kept)
            filtered = [group for group in groups if len(group) <= max(10, int(round(len(proj) * 0.22)))]
            return len(filtered), max_score

        row_peaks, row_max = peak_count(row_proj)
        col_peaks, col_max = peak_count(col_proj)
        projection_debug = {
            "inner_roi": [int(rx1), int(ry1), int(rx2), int(ry2)],
            "row_peaks": int(row_peaks),
            "col_peaks": int(col_peaks),
            "row_max": int(row_max),
            "col_max": int(col_max),
        }

        # Due piastre orizzontali -> terminali top/bottom -> orientazione vertical.
        if row_peaks >= 2 and row_max >= col_max * 1.10:
            return "vertical", {
                "decision_mode": "capacitor_internal_plate_projection_vertical",
                **projection_debug,
            }

        # Due piastre verticali -> terminali left/right -> orientazione horizontal.
        if col_peaks >= 2 and col_max >= row_max * 1.10:
            return "horizontal", {
                "decision_mode": "capacitor_internal_plate_projection_horizontal",
                **projection_debug,
            }

    side_scores = get_local_terminal_probe_scores_center(binary, bbox)
    lr_min = min(side_scores["left"], side_scores["right"])
    tb_min = min(side_scores["top"], side_scores["bottom"])
    if lr_min >= TERMINAL_PROBE_MIN_SIDE_SCORE and tb_min < max(1.0, 0.45 * lr_min):
        side_scores["decision_mode"] = "capacitor_balanced_left_right_override"
        return "horizontal", side_scores
    if tb_min >= TERMINAL_PROBE_MIN_SIDE_SCORE and lr_min < max(1.0, 0.45 * tb_min):
        side_scores["decision_mode"] = "capacitor_balanced_top_bottom_override"
        return "vertical", side_scores

    orientation = _decide_axis_from_scores(side_scores)
    if orientation is not None:
        side_scores["decision_mode"] = "capacitor_center_probes"
        return orientation, side_scores

    coarse_scores = probe_get_side_scores(binary, bbox)
    lr_score = coarse_scores["left"] + coarse_scores["right"]
    tb_score = coarse_scores["top"] + coarse_scores["bottom"]
    if coarse_scores["left"] >= SIDE_SCORE_MIN_PIXELS and coarse_scores["right"] >= SIDE_SCORE_MIN_PIXELS and lr_score > tb_score * AXIS_SCORE_MARGIN:
        merged = dict(side_scores)
        merged["coarse_scores"] = coarse_scores
        merged["decision_mode"] = "capacitor_coarse_center_bands"
        return "horizontal", merged
    if coarse_scores["top"] >= SIDE_SCORE_MIN_PIXELS and coarse_scores["bottom"] >= SIDE_SCORE_MIN_PIXELS and tb_score > lr_score * AXIS_SCORE_MARGIN:
        merged = dict(side_scores)
        merged["coarse_scores"] = coarse_scores
        merged["decision_mode"] = "capacitor_coarse_center_bands"
        return "vertical", merged

    side_scores["decision_mode"] = "capacitor_bbox_fallback"
    return geom_infer_orientation_from_bbox(bbox, default_orientation=default_orientation), side_scores


# Handle strategy detect two terminal orientation switch.
def strategy_detect_two_terminal_orientation_switch(binary, bbox, default_orientation="horizontal"):
    side_scores = get_local_terminal_probe_scores_multi_anchor(binary, bbox)
    orientation = _decide_axis_from_scores(side_scores)
    if orientation is not None:
        side_scores["decision_mode"] = "switch_multi_anchor_probes"
        return orientation, side_scores

    coarse_scores = probe_get_side_scores(binary, bbox)
    lr_score = coarse_scores["left"] + coarse_scores["right"]
    tb_score = coarse_scores["top"] + coarse_scores["bottom"]
    if coarse_scores["left"] >= SIDE_SCORE_MIN_PIXELS and coarse_scores["right"] >= SIDE_SCORE_MIN_PIXELS and lr_score > tb_score * AXIS_SCORE_MARGIN:
        merged = dict(side_scores)
        merged["coarse_scores"] = coarse_scores
        merged["decision_mode"] = "switch_coarse_side_bands"
        return "horizontal", merged
    if coarse_scores["top"] >= SIDE_SCORE_MIN_PIXELS and coarse_scores["bottom"] >= SIDE_SCORE_MIN_PIXELS and tb_score > lr_score * AXIS_SCORE_MARGIN:
        merged = dict(side_scores)
        merged["coarse_scores"] = coarse_scores
        merged["decision_mode"] = "switch_coarse_side_bands"
        return "vertical", merged

    # Per switch aperti il bbox è fuorviante: meglio default_orientation che aspect ratio.
    side_scores["decision_mode"] = "switch_default_orientation_fallback"
    return default_orientation, side_scores

# Score two terminal candidate by points.
def _score_two_terminal_candidate_by_points(binary, bbox, orientation):
    if orientation == "horizontal":
        sides = ("left", "right")
    else:
        sides = ("top", "bottom")

    total_score = 0
    side_scores = {}
    point_debug = {}

    for side in sides:
        point, peak_debug = geom_terminal_point_by_side_peak(
            binary,
            bbox,
            side
        )
        px, py = point

        dir_score = score_point_directional_support(
            binary,
            px,
            py,
            side,
            outward=12,
            inward=2,
            halfspan=3,
        )

        side_scores[side] = dir_score
        total_score += dir_score

        point_debug[side] = {
            "point": point,
            "directional_support": dir_score,
            "peak_debug": peak_debug,
        }

    return total_score, side_scores, point_debug

# Detect two terminal orientation LED.
def detect_two_terminal_orientation_led(binary, bbox, default_orientation="vertical"):

    # -------------------------------------------------
    # 1) Validazione diretta tramite terminali candidati
    # -------------------------------------------------
    horizontal_total, horizontal_side_scores, horizontal_point_debug = _score_two_terminal_candidate_by_points(
        binary, bbox, "horizontal"
    )
    vertical_total, vertical_side_scores, vertical_point_debug = _score_two_terminal_candidate_by_points(
        binary, bbox, "vertical"
    )

    LED_POINT_VALIDATION_MARGIN = 1.15
    LED_POINT_MIN_SIDE_SCORE = 2

    if (
        min(horizontal_side_scores["left"], horizontal_side_scores["right"]) >= LED_POINT_MIN_SIDE_SCORE
        and horizontal_total > vertical_total * LED_POINT_VALIDATION_MARGIN
    ):
        return "horizontal", {
            "decision_mode": "led_terminal_point_validation_horizontal",
            "horizontal_total": horizontal_total,
            "vertical_total": vertical_total,
            "horizontal_side_scores": horizontal_side_scores,
            "vertical_side_scores": vertical_side_scores,
            "horizontal_point_debug": horizontal_point_debug,
            "vertical_point_debug": vertical_point_debug,
        }

    if (
        min(vertical_side_scores["top"], vertical_side_scores["bottom"]) >= LED_POINT_MIN_SIDE_SCORE
        and vertical_total > horizontal_total * LED_POINT_VALIDATION_MARGIN
    ):
        return "vertical", {
            "decision_mode": "led_terminal_point_validation_vertical",
            "horizontal_total": horizontal_total,
            "vertical_total": vertical_total,
            "horizontal_side_scores": horizontal_side_scores,
            "vertical_side_scores": vertical_side_scores,
            "horizontal_point_debug": horizontal_point_debug,
            "vertical_point_debug": vertical_point_debug,
        }

    # -------------------------------------------------
    # 2) Probe LED near/far
    # -------------------------------------------------
    near_scores = get_led_probe_scores(binary, bbox)
    far_scores = get_led_far_probe_scores(binary, bbox)

    combined_scores = {
        "top": near_scores["top"] + LED_FAR_WEIGHT * far_scores["top"],
        "bottom": near_scores["bottom"] + LED_FAR_WEIGHT * far_scores["bottom"],
        "left": near_scores["left"] + LED_FAR_WEIGHT * far_scores["left"],
        "right": near_scores["right"] + LED_FAR_WEIGHT * far_scores["right"],
        "near_scores": near_scores,
        "far_scores": far_scores,
        "probe_mode": "led_near_far",
        "horizontal_total": horizontal_total,
        "vertical_total": vertical_total,
        "horizontal_side_scores": horizontal_side_scores,
        "vertical_side_scores": vertical_side_scores,
        "horizontal_point_debug": horizontal_point_debug,
        "vertical_point_debug": vertical_point_debug,
    }

    lr_pair = min(combined_scores["left"], combined_scores["right"])
    tb_pair = min(combined_scores["top"], combined_scores["bottom"])
    lr_score = combined_scores["left"] + combined_scores["right"]
    tb_score = combined_scores["top"] + combined_scores["bottom"]

    if (
        lr_pair >= LED_FAR_MIN_SIDE_SCORE and
        lr_score > tb_score * LED_NEAR_FAR_AXIS_MARGIN
    ):
        combined_scores["decision_mode"] = "led_near_far_horizontal"
        return "horizontal", combined_scores

    if (
        tb_pair >= LED_FAR_MIN_SIDE_SCORE and
        tb_score > lr_score * LED_NEAR_FAR_AXIS_MARGIN
    ):
        combined_scores["decision_mode"] = "led_near_far_vertical"
        return "vertical", combined_scores

    # -------------------------------------------------
    # 3) Fallback bbox invertito specifico LED
    # -------------------------------------------------
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)
    width = max(x2 - x1, 1e-6)
    height = max(y2 - y1, 1e-6)

    ratio_wh = width / height
    ratio_hw = height / width
    LED_BBOX_RATIO_MARGIN = 1.08

    combined_scores["bbox_width"] = round(width, 2)
    combined_scores["bbox_height"] = round(height, 2)

    if ratio_wh >= LED_BBOX_RATIO_MARGIN:
        combined_scores["decision_mode"] = "led_reversed_bbox_vertical"
        combined_scores["bbox_ratio_wh"] = round(ratio_wh, 4)
        return "vertical", combined_scores

    if ratio_hw >= LED_BBOX_RATIO_MARGIN:
        combined_scores["decision_mode"] = "led_reversed_bbox_horizontal"
        combined_scores["bbox_ratio_hw"] = round(ratio_hw, 4)
        return "horizontal", combined_scores

    # -------------------------------------------------
    # 4) Ultimo fallback
    # -------------------------------------------------
    combined_scores["decision_mode"] = "led_default_fallback"
    return default_orientation, combined_scores

# Detect two terminal orientation round source.
def detect_two_terminal_orientation_round_source(binary, bbox, default_orientation="vertical"):
    near_scores = get_round_source_probe_scores(binary, bbox)
    far_scores = get_round_source_far_probe_scores(binary, bbox)

    combined_scores = {
        "top": near_scores["top"] + ROUND_SOURCE_FAR_WEIGHT * far_scores["top"],
        "bottom": near_scores["bottom"] + ROUND_SOURCE_FAR_WEIGHT * far_scores["bottom"],
        "left": near_scores["left"] + ROUND_SOURCE_FAR_WEIGHT * far_scores["left"],
        "right": near_scores["right"] + ROUND_SOURCE_FAR_WEIGHT * far_scores["right"],
        "near_scores": near_scores,
        "far_scores": far_scores,
        "probe_mode": "round_source_near_far",
    }

    lr_pair = min(combined_scores["left"], combined_scores["right"])
    tb_pair = min(combined_scores["top"], combined_scores["bottom"])
    lr_score = combined_scores["left"] + combined_scores["right"]
    tb_score = combined_scores["top"] + combined_scores["bottom"]

    if (
        lr_pair >= ROUND_SOURCE_MIN_SIDE_SCORE and
        lr_score > tb_score * ROUND_SOURCE_AXIS_MARGIN
    ):
        combined_scores["decision_mode"] = "round_source_near_far_horizontal"
        return "horizontal", combined_scores

    if (
        tb_pair >= ROUND_SOURCE_MIN_SIDE_SCORE and
        tb_score > lr_score * ROUND_SOURCE_AXIS_MARGIN
    ):
        combined_scores["decision_mode"] = "round_source_near_far_vertical"
        return "vertical", combined_scores

    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)
    width = max(x2 - x1, 1e-6)
    height = max(y2 - y1, 1e-6)

    ratio_wh = width / height
    ratio_hw = height / width

    combined_scores["bbox_width"] = round(width, 2)
    combined_scores["bbox_height"] = round(height, 2)

    if ratio_wh >= ROUND_SOURCE_BBOX_RATIO_MARGIN:
        combined_scores["decision_mode"] = "round_source_bbox_fallback_horizontal"
        combined_scores["bbox_ratio_wh"] = round(ratio_wh, 4)
        return "horizontal", combined_scores

    if ratio_hw >= ROUND_SOURCE_BBOX_RATIO_MARGIN:
        combined_scores["decision_mode"] = "round_source_bbox_fallback_vertical"
        combined_scores["bbox_ratio_hw"] = round(ratio_hw, 4)
        return "vertical", combined_scores

    combined_scores["decision_mode"] = "round_source_default_fallback"
    return default_orientation, combined_scores

# Score variable resistor candidate by points.
def _score_variable_resistor_candidate_by_points(binary, bbox, orientation):
    if orientation == "horizontal":
        sides = ("left", "right")
    else:
        sides = ("top", "bottom")

    total_score = 0
    side_scores = {}
    point_debug = {}

    for side in sides:
        point, peak_debug = geom_terminal_point_by_side_peak(binary, bbox, side)
        px, py = point

        dir_score = score_point_directional_support(
            binary,
            px,
            py,
            side,
            outward=10,
            inward=0,   # quasi solo esterno: meno influenza da grafica interna
            halfspan=2,
        )

        side_scores[side] = dir_score
        total_score += dir_score

        point_debug[side] = {
            "point": point,
            "directional_support": dir_score,
            "peak_debug": peak_debug,
        }

    return total_score, side_scores, point_debug


# Detect two terminal orientation variable resistor.
def detect_two_terminal_orientation_variable_resistor(binary, bbox, default_orientation="horizontal"):

    # -------------------------------------------------
    # 1) Validazione diretta tramite terminali candidati
    # -------------------------------------------------
    horizontal_total, horizontal_side_scores, horizontal_point_debug = (
        _score_variable_resistor_candidate_by_points(binary, bbox, "horizontal")
    )
    vertical_total, vertical_side_scores, vertical_point_debug = (
        _score_variable_resistor_candidate_by_points(binary, bbox, "vertical")
    )

    POINT_MARGIN = 1.15
    POINT_MIN_SIDE_SCORE = 2

    if (
        min(vertical_side_scores["top"], vertical_side_scores["bottom"]) >= POINT_MIN_SIDE_SCORE
        and vertical_total > horizontal_total * POINT_MARGIN
    ):
        return "vertical", {
            "decision_mode": "variable_resistor_point_validation_vertical",
            "horizontal_total": horizontal_total,
            "vertical_total": vertical_total,
            "horizontal_side_scores": horizontal_side_scores,
            "vertical_side_scores": vertical_side_scores,
            "horizontal_point_debug": horizontal_point_debug,
            "vertical_point_debug": vertical_point_debug,
        }

    if (
        min(horizontal_side_scores["left"], horizontal_side_scores["right"]) >= POINT_MIN_SIDE_SCORE
        and horizontal_total > vertical_total * POINT_MARGIN
    ):
        return "horizontal", {
            "decision_mode": "variable_resistor_point_validation_horizontal",
            "horizontal_total": horizontal_total,
            "vertical_total": vertical_total,
            "horizontal_side_scores": horizontal_side_scores,
            "vertical_side_scores": vertical_side_scores,
            "horizontal_point_debug": horizontal_point_debug,
            "vertical_point_debug": vertical_point_debug,
        }

    # -------------------------------------------------
    # 2) Bande esterne strette, meno sensibili al testo vicino
    # -------------------------------------------------
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)

    w = max(1, x2 - x1)
    h = max(1, y2 - y1)
    xc = int(round((x1 + x2) / 2))
    yc = int(round((y1 + y2) / 2))

    half_band_x = min(6, max(2, int(round(w * 0.10))))
    half_band_y = min(6, max(2, int(round(h * 0.10))))

    gap = 2
    thick = max(2, int(round(min(w, h) * 0.08)))

    side_scores = {
        "top": img_count_foreground_pixels(
            binary,
            xc - half_band_x,
            y1 - gap - thick,
            xc + half_band_x + 1,
            y1 - gap
        ),
        "bottom": img_count_foreground_pixels(
            binary,
            xc - half_band_x,
            y2 + gap,
            xc + half_band_x + 1,
            y2 + gap + thick
        ),
        "left": img_count_foreground_pixels(
            binary,
            x1 - gap - thick,
            yc - half_band_y,
            x1 - gap,
            yc + half_band_y + 1
        ),
        "right": img_count_foreground_pixels(
            binary,
            x2 + gap,
            yc - half_band_y,
            x2 + gap + thick,
            yc + half_band_y + 1
        ),
    }

    horizontal_score = side_scores["left"] + side_scores["right"]
    vertical_score = side_scores["top"] + side_scores["bottom"]
    horizontal_pair = min(side_scores["left"], side_scores["right"])
    vertical_pair = min(side_scores["top"], side_scores["bottom"])

    debug_scores = {
        **side_scores,
        "horizontal_score": horizontal_score,
        "vertical_score": vertical_score,
        "bbox_width": w,
        "bbox_height": h,
        "horizontal_total": horizontal_total,
        "vertical_total": vertical_total,
        "horizontal_side_scores": horizontal_side_scores,
        "vertical_side_scores": vertical_side_scores,
        "horizontal_point_debug": horizontal_point_debug,
        "vertical_point_debug": vertical_point_debug,
    }

    min_side = 2
    axis_margin = 1.20

    if vertical_pair >= min_side and vertical_score > horizontal_score * axis_margin:
        debug_scores["decision_mode"] = "variable_resistor_external_wire_vertical"
        return "vertical", debug_scores

    if horizontal_pair >= min_side and horizontal_score > vertical_score * axis_margin:
        debug_scores["decision_mode"] = "variable_resistor_external_wire_horizontal"
        return "horizontal", debug_scores

    # -------------------------------------------------
    # 3) Fallback finale
    # -------------------------------------------------
    orientation, generic_scores = strategy_detect_two_terminal_orientation_generic(
        binary,
        bbox,
        default_orientation=default_orientation,
    )

    generic_scores["external_wire_scores"] = debug_scores
    generic_scores["decision_mode"] = "variable_resistor_generic_fallback"
    return orientation, generic_scores

