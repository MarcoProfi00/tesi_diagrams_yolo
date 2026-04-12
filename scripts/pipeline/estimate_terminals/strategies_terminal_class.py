from .config import *
from .geometry import geom_terminal_point_by_side_peak
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

def _score_terminal_one_side_candidate_by_points(binary, bbox, side):
    """
    Valuta un lato candidato usando un punto stimato sul bordo
    e misurando il supporto direzionale verso l'esterno.
    """
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


def _combined_side_scores(local_scores, far_scores):
    return {
        side: float(local_scores.get(side, 0)) + 1.2 * float(far_scores.get(side, 0))
        for side in ("top", "bottom", "left", "right")
    }

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

def _apply_terminal_shape_prior(bbox, side_scores):
    """
    Bias geometrico molto leggero:
    - lo applichiamo solo se il bbox NON è quasi quadrato
    - terminali piccoli/quasi quadrati non devono essere forzati
      verso top/bottom o left/right
    """
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


def classify_terminal_cardinality(binary, bbox, default_side="right"):
    local_scores = get_terminal_class_probe_scores(binary, bbox)
    far_scores = get_terminal_class_far_probe_scores(binary, bbox)

    single_eval = _best_single_side(binary, bbox, local_scores, far_scores)
    horiz_eval = _horizontal_two_side_evidence(local_scores, far_scores)
    vert_eval = _vertical_two_side_evidence(local_scores, far_scores)

    local_scores["far_scores"] = far_scores
    local_scores["single_side_evaluation"] = single_eval
    local_scores["two_side_evaluations"] = {
        "horizontal": horiz_eval,
        "vertical": vert_eval,
    }

    # 2 terminali solo se batte chiaramente la migliore ipotesi mono-terminale
    TWO_VS_ONE_MIN_ADVANTAGE = 2.0
    TWO_SIDE_MARGIN = 1.10

    horiz_beats_one = horiz_eval["pair_score"] >= single_eval["best_score"] + TWO_VS_ONE_MIN_ADVANTAGE
    vert_beats_one = vert_eval["pair_score"] >= single_eval["best_score"] + TWO_VS_ONE_MIN_ADVANTAGE

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
        vert_eval["valid"]
        and vert_beats_one
        and (
            not horiz_eval["valid"]
            or vert_eval["pair_score"] > horiz_eval["pair_score"] * TWO_SIDE_MARGIN
        )
    ):
        local_scores["decision_mode"] = "terminal_cardinality_two_vertical"
        return 2, "vertical", local_scores

    local_scores["decision_mode"] = "terminal_cardinality_default_one"
    return 1, single_eval["best_side"], local_scores

def _opposite_side(side):
    return {
        "top": "bottom",
        "bottom": "top",
        "left": "right",
        "right": "left",
    }[side]


def _score_terminal_one_side_candidate_by_through_support(binary, bbox, side):
    """
    Misura quanto un lato sembri una vera connessione passante:
    supporto fuori dal bbox + un po' di continuità dentro il simbolo.
    Questo aiuta a scartare testo ('+', 'cc', ecc.).
    """
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


def detect_terminal_two_sides(binary, bbox, precomputed_scores=None):
    scores = precomputed_scores if precomputed_scores is not None else get_terminal_class_probe_scores(binary, bbox)
    far_scores = scores.get("far_scores")
    if far_scores is None:
        far_scores = get_terminal_class_far_probe_scores(binary, bbox)

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


def detect_terminal_auto_one_or_two(binary, bbox, default_side="right"):
    cardinality, mode, scores = classify_terminal_cardinality(binary, bbox, default_side=default_side)

    if cardinality == 1:
        terminals_def, orientation = detect_terminal_one_side(
            binary,
            bbox,
            default_side=default_side,
            precomputed_scores=scores,
        )
        scores["final_mode"] = "one_terminal"
        return terminals_def, orientation, scores

    terminals_def, orientation = detect_terminal_two_sides(
        binary,
        bbox,
        precomputed_scores=scores,
    )
    scores["final_mode"] = "two_terminal"
    return terminals_def, orientation, scores