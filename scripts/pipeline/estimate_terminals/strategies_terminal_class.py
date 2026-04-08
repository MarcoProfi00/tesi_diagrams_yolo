from .config import *
from .probes import get_terminal_border_preference, get_terminal_class_far_probe_scores, get_terminal_class_probe_scores, is_terminal_near_border
# =========================================================
# STRATEGY: VARIABLE TERMINAL CLASS ("Terminal")
# =========================================================
def classify_terminal_cardinality(binary, bbox, default_side="right"):
    local_scores = get_terminal_class_probe_scores(binary, bbox)
    far_scores = get_terminal_class_far_probe_scores(binary, bbox)
    border_pref = get_terminal_border_preference(binary.shape, bbox)

    # -------------------------------------------------
    # 1) Porta esterna: vicino al bordo -> forza 1 lato
    # -------------------------------------------------
    if is_terminal_near_border(binary.shape, bbox):
        local_scores["far_scores"] = far_scores
        local_scores["decision_mode"] = "terminal_cardinality_border_forced_one"
        local_scores["border_preference"] = border_pref
        return 1, border_pref if border_pref is not None else default_side, local_scores

    # Lato attivo solo se confermato anche dal probe far
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
    # 2) Due terminali solo se davvero molto chiaro
    # -------------------------------------------------
    if (
        active["left"] and active["right"] and
        lr_pair >= TERMINAL_CLASS_TWO_SIDE_MIN and
        lr_score > tb_score * TERMINAL_CLASS_TWO_AXIS_MARGIN and
        min(left_val, right_val) >= TERMINAL_CLASS_TWO_BALANCE_RATIO * max(left_val, right_val) and
        not active["top"] and not active["bottom"]
    ):
        local_scores["far_scores"] = far_scores
        local_scores["decision_mode"] = "terminal_cardinality_two_horizontal"
        return 2, "horizontal", local_scores

    if (
        active["top"] and active["bottom"] and
        tb_pair >= TERMINAL_CLASS_TWO_SIDE_MIN and
        tb_score > lr_score * TERMINAL_CLASS_TWO_AXIS_MARGIN and
        min(top_val, bottom_val) >= TERMINAL_CLASS_TWO_BALANCE_RATIO * max(top_val, bottom_val) and
        not active["left"] and not active["right"]
    ):
        local_scores["far_scores"] = far_scores
        local_scores["decision_mode"] = "terminal_cardinality_two_vertical"
        return 2, "vertical", local_scores

    # -------------------------------------------------
    # 3) Altrimenti uno
    # -------------------------------------------------
    candidate_sides = [s for s in ("top", "bottom", "left", "right") if active[s]]
    if candidate_sides:
        best_side = max(candidate_sides, key=lambda s: local_scores[s])
    else:
        best_side = max(("top", "bottom", "left", "right"), key=lambda s: local_scores[s])

    local_scores["far_scores"] = far_scores
    local_scores["decision_mode"] = "terminal_cardinality_default_one"
    return 1, best_side, local_scores

def detect_terminal_one_side(binary, bbox, default_side="right", precomputed_scores=None):
    scores = precomputed_scores if precomputed_scores is not None else get_terminal_class_probe_scores(binary, bbox)

    border_pref = get_terminal_border_preference(binary.shape, bbox)
    if border_pref is not None:
        return [{"name": "t1", "relative_position": border_pref}], border_pref

    best_side = max(("top", "bottom", "left", "right"), key=lambda s: scores[s])
    if scores[best_side] >= TERMINAL_CLASS_ONE_SIDE_MIN:
        return [{"name": "t1", "relative_position": best_side}], best_side

    return [{"name": "t1", "relative_position": default_side}], default_side

def detect_terminal_two_sides(binary, bbox, precomputed_scores=None):
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
        terminals_def, orientation = detect_terminal_one_side(
            binary, bbox, default_side=default_side, precomputed_scores=scores
        )
        scores["final_mode"] = "one_terminal"
        return terminals_def, orientation, scores

    terminals_def, orientation = detect_terminal_two_sides(
        binary, bbox, precomputed_scores=scores
    )
    scores["final_mode"] = "two_terminal"
    return terminals_def, orientation, scores