from .config import *
from .geometry import geom_terminal_point_by_side_peak
from .probes import (
    get_terminal_border_preference,
    get_terminal_class_far_probe_scores,
    get_terminal_class_probe_scores,
    is_terminal_near_border,
    score_point_directional_support,
)

# =========================================================
# STRATEGY: VARIABLE TERMINAL CLASS ("Terminal")
# =========================================================
def _score_terminal_two_side_candidate_by_points(binary, bbox, orientation):
    """
    Valuta una candidata orientazione a 2 terminali usando
    i due punti terminali stimati sui lati opposti.
    """
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
            inward=0,
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


def classify_terminal_cardinality(binary, bbox, default_side="right"):
    local_scores = get_terminal_class_probe_scores(binary, bbox)
    far_scores = get_terminal_class_far_probe_scores(binary, bbox)
    border_pref = get_terminal_border_preference(binary.shape, bbox)
    

    # -------------------------------------------------
    # 1) Prima validazione diretta a 2 terminali con point-scoring
    # -------------------------------------------------
    horizontal_total, horizontal_side_scores, horizontal_point_debug = (
        _score_terminal_two_side_candidate_by_points(binary, bbox, "horizontal")
    )
    vertical_total, vertical_side_scores, vertical_point_debug = (
        _score_terminal_two_side_candidate_by_points(binary, bbox, "vertical")
    )

    POINT_MIN_SIDE_SCORE = 2
    POINT_MARGIN = 1.15

    if (
        min(vertical_side_scores["top"], vertical_side_scores["bottom"]) >= POINT_MIN_SIDE_SCORE
        and vertical_total > horizontal_total * POINT_MARGIN
    ):
        local_scores["far_scores"] = far_scores
        local_scores["decision_mode"] = "terminal_cardinality_point_validation_vertical"
        local_scores["point_validation"] = {
            "horizontal_total": horizontal_total,
            "vertical_total": vertical_total,
            "horizontal_side_scores": horizontal_side_scores,
            "vertical_side_scores": vertical_side_scores,
            "horizontal_point_debug": horizontal_point_debug,
            "vertical_point_debug": vertical_point_debug,
        }
        return 2, "vertical", local_scores

    if (
        min(horizontal_side_scores["left"], horizontal_side_scores["right"]) >= POINT_MIN_SIDE_SCORE
        and horizontal_total > vertical_total * POINT_MARGIN
    ):
        local_scores["far_scores"] = far_scores
        local_scores["decision_mode"] = "terminal_cardinality_point_validation_horizontal"
        local_scores["point_validation"] = {
            "horizontal_total": horizontal_total,
            "vertical_total": vertical_total,
            "horizontal_side_scores": horizontal_side_scores,
            "vertical_side_scores": vertical_side_scores,
            "horizontal_point_debug": horizontal_point_debug,
            "vertical_point_debug": vertical_point_debug,
        }
        return 2, "horizontal", local_scores

    # lato attivo solo se confermato anche dal probe far
    active = {}
    for side in ("top", "bottom", "left", "right"):
        active[side] = (
            local_scores[side] >= TERMINAL_CLASS_ONE_SIDE_MIN and
            far_scores[side] >= TERMINAL_CLASS_FAR_MIN
        )

    left_val = local_scores["left"]
    right_val = local_scores["right"]
    top_val = local_scores["top"]
    bottom_val = local_scores["bottom"]

    lr_pair = min(left_val, right_val)
    tb_pair = min(top_val, bottom_val)
    lr_score = left_val + right_val
    tb_score = top_val + bottom_val

    # -------------------------------------------------
    # 2) Fallback classico: due terminali solo se molto chiaro
    # -------------------------------------------------
    clear_two_horizontal = (
        active["left"] and active["right"] and
        lr_pair >= TERMINAL_CLASS_TWO_SIDE_MIN and
        lr_score > tb_score * TERMINAL_CLASS_TWO_AXIS_MARGIN and
        min(left_val, right_val) >= TERMINAL_CLASS_TWO_BALANCE_RATIO * max(left_val, right_val) and
        not active["top"] and not active["bottom"]
    )

    clear_two_vertical = (
        active["top"] and active["bottom"] and
        tb_pair >= TERMINAL_CLASS_TWO_SIDE_MIN and
        tb_score > lr_score * TERMINAL_CLASS_TWO_AXIS_MARGIN and
        min(top_val, bottom_val) >= TERMINAL_CLASS_TWO_BALANCE_RATIO * max(top_val, bottom_val) and
        not active["left"] and not active["right"]
    )

    if clear_two_horizontal:
        local_scores["far_scores"] = far_scores
        local_scores["decision_mode"] = "terminal_cardinality_two_horizontal"
        return 2, "horizontal", local_scores

    if clear_two_vertical:
        local_scores["far_scores"] = far_scores
        local_scores["decision_mode"] = "terminal_cardinality_two_vertical"
        return 2, "vertical", local_scores

    # -------------------------------------------------
    # 3) Solo se NON è chiaramente a 2, bordo => 1
    # -------------------------------------------------
    if is_terminal_near_border(binary.shape, bbox):
        local_scores["far_scores"] = far_scores
        local_scores["decision_mode"] = "terminal_cardinality_border_forced_one"
        local_scores["border_preference"] = border_pref
        return 1, border_pref if border_pref is not None else default_side, local_scores

    # -------------------------------------------------
    # 4) Altrimenti uno
    # -------------------------------------------------
    candidate_sides = [s for s in ("top", "bottom", "left", "right") if active[s]]
    if candidate_sides:
        best_side = max(candidate_sides, key=lambda s: local_scores[s])
    else:
        best_side = max(("top", "bottom", "left", "right"), key=lambda s: local_scores[s])

    local_scores["far_scores"] = far_scores
    local_scores["decision_mode"] = "terminal_cardinality_default_one"
    return 1, best_side, local_scores

def _score_terminal_one_side_candidate_by_points(binary, bbox, side):
    """
    Valuta un lato candidato per un Terminal mono-terminale
    usando il punto terminale stimato sul lato e supporto direzionale
    quasi solo esterno al bbox.
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


def detect_terminal_one_side(binary, bbox, default_side="right", precomputed_scores=None, preferred_side=None):
    # Se la classificazione ha già deciso in modo affidabile il lato, usalo.
    if preferred_side in {"top", "bottom", "left", "right"}:
        return [{"name": "t1", "relative_position": preferred_side}], preferred_side

    scores = precomputed_scores if precomputed_scores is not None else get_terminal_class_probe_scores(binary, bbox)
    far_scores = scores.get("far_scores", {})

    border_pref = get_terminal_border_preference(binary.shape, bbox)
    if border_pref is not None:
        return [{"name": "t1", "relative_position": border_pref}], border_pref

    # -------------------------------------------------
    # 1) Prima prova: point validation sui 4 lati
    # -------------------------------------------------
    point_scores = {}
    point_debug = {}

    for side in ("top", "bottom", "left", "right"):
        score, point, peak_debug = _score_terminal_one_side_candidate_by_points(binary, bbox, side)
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
        return [{"name": "t1", "relative_position": best_side}], best_side

    # -------------------------------------------------
    # 2) Fallback: usa solo lati confermati anche dai far_scores
    # -------------------------------------------------
    candidate_sides = []
    for side in ("top", "bottom", "left", "right"):
        local_ok = scores.get(side, 0) >= TERMINAL_CLASS_ONE_SIDE_MIN
        far_ok = far_scores.get(side, 0) >= TERMINAL_CLASS_FAR_MIN if far_scores else True
        if local_ok and far_ok:
            candidate_sides.append(side)

    if candidate_sides:
        best_side = max(candidate_sides, key=lambda s: scores.get(s, 0))
        return [{"name": "t1", "relative_position": best_side}], best_side

    best_side = max(("top", "bottom", "left", "right"), key=lambda s: scores.get(s, 0))
    return [{"name": "t1", "relative_position": best_side}], best_side


def detect_terminal_two_sides(binary, bbox, precomputed_scores=None, preferred_orientation=None):
    if preferred_orientation == "horizontal":
        return [
            {"name": "t1", "relative_position": "left"},
            {"name": "t2", "relative_position": "right"},
        ], "horizontal"

    if preferred_orientation == "vertical":
        return [
            {"name": "t1", "relative_position": "top"},
            {"name": "t2", "relative_position": "bottom"},
        ], "vertical"

    scores = precomputed_scores if precomputed_scores is not None else get_terminal_class_probe_scores(binary, bbox)

    lr_score = scores["left"] + scores["right"]
    tb_score = scores["top"] + scores["bottom"]

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
        decision_mode = scores.get("decision_mode", "")

        # Usa il lato già deciso SOLO quando è una decisione davvero affidabile.
        # Se è "default_one", lasciamo che detect_terminal_one_side faccia
        # border preference + point validation.
        preferred_side = None
        if decision_mode == "terminal_cardinality_border_forced_one":
            preferred_side = mode

        terminals_def, orientation = detect_terminal_one_side(
            binary,
            bbox,
            default_side=default_side,
            precomputed_scores=scores,
            preferred_side=preferred_side,
        )
        scores["final_mode"] = "one_terminal"
        return terminals_def, orientation, scores

    terminals_def, orientation = detect_terminal_two_sides(
        binary,
        bbox,
        precomputed_scores=scores,
        preferred_orientation=mode,
    )
    scores["final_mode"] = "two_terminal"
    return terminals_def, orientation, scores