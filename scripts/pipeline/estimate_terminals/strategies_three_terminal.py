import cv2
import numpy as np

from .config import *
from .geometry import (
    geom_terminal_point_three_terminal,
    geom_clamp_bbox_to_image,
)
from .image_ops import img_count_foreground_pixels
from .probes import (
    get_local_terminal_probe_scores_center,
    get_local_terminal_probe_scores_multi_anchor,
    get_mosfet_lateral_gate_scores,
    get_mosfet_single_side_scores,
    score_mosfet_candidate_terminals,
)


def _build_three_terminal_support_binary(binary, bbox):
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)
    w = max(x2 - x1, 1)
    h = max(y2 - y1, 1)

    margin = max(
        THREE_TERMINAL_TEXT_SUPPRESS_MARGIN_MIN,
        int(round(THREE_TERMINAL_TEXT_SUPPRESS_MARGIN_RATIO * max(w, h))),
    )

    rx1 = max(0, x1 - margin)
    ry1 = max(0, y1 - margin)
    rx2 = min(binary.shape[1] - 1, x2 + margin)
    ry2 = min(binary.shape[0] - 1, y2 + margin)

    roi = binary[ry1:ry2 + 1, rx1:rx2 + 1]
    roi_fg = (roi > 0).astype(np.uint8)

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(roi_fg, connectivity=8)

    seed_pad = THREE_TERMINAL_TEXT_SUPPRESS_SEED_PAD
    seed_w = max(
        THREE_TERMINAL_SEED_MIN_SIZE,
        int(round(w * (1.0 - 2.0 * THREE_TERMINAL_SEED_INSET_RATIO))),
    )
    seed_h = max(
        THREE_TERMINAL_SEED_MIN_SIZE,
        int(round(h * (1.0 - 2.0 * THREE_TERMINAL_SEED_INSET_RATIO))),
    )

    bbox_x1_in_roi = x1 - rx1
    bbox_y1_in_roi = y1 - ry1

    sx1 = max(0, bbox_x1_in_roi + int(round((w - seed_w) / 2.0)) - seed_pad)
    sy1 = max(0, bbox_y1_in_roi + int(round((h - seed_h) / 2.0)) - seed_pad)
    sx2 = min(roi.shape[1] - 1, sx1 + seed_w - 1 + 2 * seed_pad)
    sy2 = min(roi.shape[0] - 1, sy1 + seed_h - 1 + 2 * seed_pad)

    seed_labels = np.unique(labels[sy1:sy2 + 1, sx1:sx2 + 1])

    cleaned_roi = np.zeros_like(roi, dtype=np.uint8)
    kept_labels = []
    for lab in seed_labels:
        if lab == 0:
            continue
        cleaned_roi[labels == lab] = 255
        kept_labels.append(int(lab))

    cleaned = binary.copy()
    cleaned[ry1:ry2 + 1, rx1:rx2 + 1] = cleaned_roi

    return cleaned, {
        "enabled": True,
        "roi": [int(rx1), int(ry1), int(rx2), int(ry2)],
        "seed_bbox_in_roi": [int(sx1), int(sy1), int(sx2), int(sy2)],
        "connected_components": int(num_labels - 1),
        "kept_labels": kept_labels,
    }


def candidate_mosfet_orientations_from_bbox(bbox):
    """
    Per ora testiamo sempre tutte e 4 le orientazioni.
    È il modo più semplice per capire se il problema nasce
    dal filtro iniziale sul bbox.
    """
    return ("left", "right", "top", "bottom")


def score_three_terminal_orientation_by_terminal_points(binary, bbox, orientation, single_weight):
    """
    Versione generica della validazione finale:
    genera i 3 terminali coerenti con l'orientazione candidata
    e li valuta con lo scoring locale attorno ai punti finali.
    """
    candidate_terminals = []
    point_debug = {}

    for rel_pos in THREE_TERMINAL_TEMPLATES[orientation]:
        point, term_point_debug = geom_terminal_point_three_terminal(
            binary,
            bbox,
            orientation,
            rel_pos
        )

        x, y = point

        candidate_terminals.append({
            "relative_position": rel_pos,
            "x": x,
            "y": y,
        })

        point_debug[rel_pos] = {
            "point": point,
            "point_debug": term_point_debug,
        }

    total_score, score_details = score_mosfet_candidate_terminals(
        binary,
        candidate_terminals,
        single_side=orientation,
        single_weight=single_weight,
    )

    debug = {
        "candidate_terminals": candidate_terminals,
        "score_details": score_details,
        "point_debug": point_debug,
    }

    return total_score, debug


def score_mosfet_orientation_by_terminal_points(binary, bbox, orientation):
    return score_three_terminal_orientation_by_terminal_points(
        binary,
        bbox,
        orientation,
        single_weight=MOSFET_SINGLE_TERMINAL_WEIGHT,
    )


# =========================================================
# STRATEGY: THREE-TERMINAL COMPONENTS
# =========================================================
def _is_specular_pair(a, b):
    return {a, b} in ({"left", "right"}, {"top", "bottom"})


def _resolve_specular_tie(side_a, side_b, lateral_scores, single_side_scores):
    pair = {side_a, side_b}

    # Caso left/right: usa il probe gate laterale
    if pair == {"left", "right"} and lateral_scores is not None:
        return "left" if lateral_scores["left"] >= lateral_scores["right"] else "right"

    # Caso top/bottom: usa gli score del lato singolo già calcolati
    return side_a if single_side_scores[side_a] >= single_side_scores[side_b] else side_b

def get_bjt_base_side_scores(binary, bbox):
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)

    band_y1 = y1 + int(round(0.20 * height))
    band_y2 = y1 + int(round(0.80 * height))

    strip_w = max(2, int(round(0.14 * width)))
    inset = max(1, int(round(0.05 * width)))

    left_score = img_count_foreground_pixels(
        binary,
        x1 + inset,
        band_y1,
        x1 + inset + strip_w,
        band_y2 + 1,
    )

    right_score = img_count_foreground_pixels(
        binary,
        x2 - inset - strip_w,
        band_y1,
        x2 - inset,
        band_y2 + 1,
    )

    return {
        "left": float(left_score),
        "right": float(right_score),
    }


def _count_three_terminal_semantic_probe(binary, cx, cy, half_w, half_h):
    h, w = binary.shape[:2]
    xa = max(0, int(round(cx)) - half_w)
    xb = min(w, int(round(cx)) + half_w + 1)
    ya = max(0, int(round(cy)) - half_h)
    yb = min(h, int(round(cy)) + half_h + 1)

    if xb <= xa or yb <= ya:
        return 0

    return img_count_foreground_pixels(binary, xa, ya, xb, yb)


def _three_terminal_arrow_branch_probe(binary, bbox, orientation):
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)

    half_w = max(
        THREE_TERMINAL_ARROW_PROBE_HALFSPAN_MIN,
        int(round(width * THREE_TERMINAL_ARROW_PROBE_HALFSPAN_X_RATIO)),
    )
    half_h = max(
        THREE_TERMINAL_ARROW_PROBE_HALFSPAN_MIN,
        int(round(height * THREE_TERMINAL_ARROW_PROBE_HALFSPAN_Y_RATIO)),
    )

    def xr(ratio):
        return x1 + int(round(ratio * width))

    def yr(ratio):
        return y1 + int(round(ratio * height))

    scores = {}
    debug = {
        "probe_half_w": int(half_w),
        "probe_half_h": int(half_h),
        "orientation": orientation,
        "probe_points": {},
    }

    if orientation == "left":
        cx = xr(THREE_TERMINAL_ARROW_BRANCH_FAR_RATIO)
        probe_points = {
            "top": (cx, yr(THREE_TERMINAL_ARROW_PAIR_FIRST_RATIO)),
            "bottom": (cx, yr(THREE_TERMINAL_ARROW_PAIR_SECOND_RATIO)),
        }
    elif orientation == "right":
        cx = xr(THREE_TERMINAL_ARROW_BRANCH_NEAR_RATIO)
        probe_points = {
            "top": (cx, yr(THREE_TERMINAL_ARROW_PAIR_FIRST_RATIO)),
            "bottom": (cx, yr(THREE_TERMINAL_ARROW_PAIR_SECOND_RATIO)),
        }
    elif orientation == "top":
        cy = yr(THREE_TERMINAL_ARROW_BRANCH_FAR_RATIO)
        probe_points = {
            "left": (xr(THREE_TERMINAL_ARROW_PAIR_FIRST_RATIO), cy),
            "right": (xr(THREE_TERMINAL_ARROW_PAIR_SECOND_RATIO), cy),
        }
    elif orientation == "bottom":
        cy = yr(THREE_TERMINAL_ARROW_BRANCH_NEAR_RATIO)
        probe_points = {
            "left": (xr(THREE_TERMINAL_ARROW_PAIR_FIRST_RATIO), cy),
            "right": (xr(THREE_TERMINAL_ARROW_PAIR_SECOND_RATIO), cy),
        }
    else:
        probe_points = {}

    for rel_pos, (cx, cy) in probe_points.items():
        scores[rel_pos] = float(
            _count_three_terminal_semantic_probe(binary, cx, cy, half_w, half_h)
        )
        debug["probe_points"][rel_pos] = {
            "x": int(cx),
            "y": int(cy),
            "score": float(scores[rel_pos]),
        }

    return scores, debug


def _npn_arrow_branch_probe(binary, bbox, orientation):
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)

    half_w = max(
        THREE_TERMINAL_ARROW_PROBE_HALFSPAN_MIN,
        int(round(width * 0.10)),
    )
    half_h = max(
        THREE_TERMINAL_ARROW_PROBE_HALFSPAN_MIN,
        int(round(height * 0.10)),
    )

    def xr(ratio):
        return x1 + int(round(ratio * width))

    def yr(ratio):
        return y1 + int(round(ratio * height))

    if orientation == "left":
        cx = xr(NPN_ARROW_BRANCH_TRUNK_LEFT_RATIO)
    elif orientation == "right":
        cx = xr(NPN_ARROW_BRANCH_TRUNK_RIGHT_RATIO)
    else:
        return {}, {
            "probe_half_w": int(half_w),
            "probe_half_h": int(half_h),
            "orientation": orientation,
            "probe_points": {},
        }

    probe_points = {
        "top": (cx, yr(NPN_ARROW_BRANCH_TOP_RATIO)),
        "bottom": (cx, yr(NPN_ARROW_BRANCH_BOTTOM_RATIO)),
    }

    scores = {}
    debug = {
        "probe_half_w": int(half_w),
        "probe_half_h": int(half_h),
        "orientation": orientation,
        "probe_points": {},
        "probe_mode": "npn_trunk_arrow_probe",
    }

    for rel_pos, (px, py) in probe_points.items():
        scores[rel_pos] = float(
            _count_three_terminal_semantic_probe(binary, px, py, half_w, half_h)
        )
        debug["probe_points"][rel_pos] = {
            "x": int(px),
            "y": int(py),
            "score": float(scores[rel_pos]),
        }

    return scores, debug


def _semantic_pair_confidence(pair_scores, arrow_branch_position, other_branch_position):
    best_score = float(pair_scores.get(arrow_branch_position, 0.0))
    second_score = float(pair_scores.get(other_branch_position, 0.0))

    confidence = 0.0
    if best_score > 0.0 or second_score > 0.0:
        confidence = (best_score - second_score) / max(best_score + second_score, 1.0)
        confidence = max(0.0, min(1.0, float(confidence)))

    return best_score, second_score, confidence


def resolve_three_terminal_semantics(binary, bbox, orientation, terminals, meta):
    semantic_strategy = meta.get("semantic_terminal_strategy")
    semantic_roles = meta.get("semantic_roles", {})

    if semantic_strategy is None:
        return terminals

    if orientation not in THREE_TERMINAL_TEMPLATES or len(terminals) < 3:
        return terminals

    pair_positions = [
        rel_pos for rel_pos in THREE_TERMINAL_TEMPLATES[orientation]
        if rel_pos != orientation
    ]

    if len(pair_positions) != 2:
        return terminals

    working_binary = binary
    support_binary_debug = {
        "enabled": False,
    }
    if THREE_TERMINAL_TEXT_SUPPRESS_ENABLE:
        working_binary, support_binary_debug = _build_three_terminal_support_binary(
            binary,
            bbox,
        )

    if semantic_strategy == "three_terminal_gate_only":
        single_side_name = semantic_roles.get("single_side")
        for term in terminals:
            if term.get("relative_position") != orientation or single_side_name is None:
                continue
            term["semantic_terminal_name"] = single_side_name
            term["semantic_terminal_id"] = f"{term['instance_id']}:{single_side_name}"
            term["semantic_slot"] = "single_side"
            term["semantic_confidence"] = 1.0
            term["semantic_resolution_mode"] = semantic_strategy
            term["semantic_resolution_debug"] = {
                "orientation": orientation,
                "support_binary_debug": support_binary_debug,
            }
            term["display_name"] = single_side_name
            term["display_terminal_id"] = term["semantic_terminal_id"]
        return terminals

    if semantic_strategy == "mosfet_gate_with_optional_source_drain":
        single_side_name = semantic_roles.get("single_side")
        arrow_scores, arrow_debug = _three_terminal_arrow_branch_probe(
            working_binary,
            bbox,
            orientation,
        )
        arrow_branch_position = max(
            pair_positions,
            key=lambda rel_pos: arrow_scores.get(rel_pos, 0.0),
        )
        other_branch_position = next(
            rel_pos for rel_pos in pair_positions
            if rel_pos != arrow_branch_position
        )
        best_score, second_score, pair_confidence = _semantic_pair_confidence(
            arrow_scores,
            arrow_branch_position,
            other_branch_position,
        )
        assign_pair_semantics = pair_confidence >= MOSFET_ARROW_BRANCH_CONFIDENCE_MIN

        role_by_position = {
            orientation: ("single_side", single_side_name),
        }
        if assign_pair_semantics:
            role_by_position[arrow_branch_position] = (
                "arrow_branch",
                semantic_roles.get("arrow_branch"),
            )
            role_by_position[other_branch_position] = (
                "other_branch",
                semantic_roles.get("other_branch"),
            )

        for term in terminals:
            rel_pos = term.get("relative_position")
            semantic_slot, semantic_name = role_by_position.get(rel_pos, (None, None))

            term["semantic_resolution_mode"] = semantic_strategy
            term["semantic_resolution_debug"] = {
                "orientation": orientation,
                "arrow_branch_position": arrow_branch_position,
                "other_branch_position": other_branch_position,
                "arrow_scores": arrow_scores,
                "arrow_score_best": best_score,
                "arrow_score_second": second_score,
                "arrow_probe_debug": arrow_debug,
                "pair_confidence": round(pair_confidence, 4),
                "pair_confidence_threshold": MOSFET_ARROW_BRANCH_CONFIDENCE_MIN,
                "pair_semantics_assigned": assign_pair_semantics,
                "support_binary_debug": support_binary_debug,
            }

            if semantic_name is None:
                continue

            term["semantic_terminal_name"] = semantic_name
            term["semantic_terminal_id"] = f"{term['instance_id']}:{semantic_name}"
            term["semantic_slot"] = semantic_slot
            term["semantic_confidence"] = (
                1.0 if semantic_slot == "single_side" else round(pair_confidence, 4)
            )
            term["display_name"] = semantic_name
            term["display_terminal_id"] = term["semantic_terminal_id"]
        return terminals

    if semantic_strategy == "npn_emitter_from_arrow_branch":
        arrow_scores, arrow_debug = _three_terminal_arrow_branch_probe(
            working_binary,
            bbox,
            orientation,
        )
        arrow_branch_position = max(
            pair_positions,
            key=lambda rel_pos: arrow_scores.get(rel_pos, 0.0),
        )
        other_branch_position = next(
            rel_pos for rel_pos in pair_positions
            if rel_pos != arrow_branch_position
        )
        best_score, second_score, pair_confidence = _semantic_pair_confidence(
            arrow_scores,
            arrow_branch_position,
            other_branch_position,
        )

        fallback_scores = None
        fallback_debug = None
        fallback_used = False
        if pair_confidence < THREE_TERMINAL_ARROW_CONFIDENCE_MIN:
            fallback_scores, fallback_debug = _npn_arrow_branch_probe(
                working_binary,
                bbox,
                orientation,
            )
            fallback_arrow_branch = max(
                pair_positions,
                key=lambda rel_pos: fallback_scores.get(rel_pos, 0.0),
            )
            fallback_other_branch = next(
                rel_pos for rel_pos in pair_positions
                if rel_pos != fallback_arrow_branch
            )
            fb_best, fb_second, fb_conf = _semantic_pair_confidence(
                fallback_scores,
                fallback_arrow_branch,
                fallback_other_branch,
            )

            if fb_conf > pair_confidence:
                arrow_scores = fallback_scores
                arrow_debug = fallback_debug
                arrow_branch_position = fallback_arrow_branch
                other_branch_position = fallback_other_branch
                best_score = fb_best
                second_score = fb_second
                pair_confidence = fb_conf
                fallback_used = True

    else:
        return terminals

    role_by_position = {
        orientation: ("single_side", semantic_roles.get("single_side")),
        arrow_branch_position: ("arrow_branch", semantic_roles.get("arrow_branch")),
        other_branch_position: ("other_branch", semantic_roles.get("other_branch")),
    }

    for term in terminals:
        rel_pos = term.get("relative_position")
        semantic_slot, semantic_name = role_by_position.get(rel_pos, (None, None))

        if semantic_name is None:
            continue

        term["semantic_terminal_name"] = semantic_name
        term["semantic_terminal_id"] = f"{term['instance_id']}:{semantic_name}"
        term["semantic_slot"] = semantic_slot
        term["semantic_confidence"] = (
            1.0 if semantic_slot == "single_side" else round(pair_confidence, 4)
        )
        term["semantic_resolution_mode"] = semantic_strategy
        term["semantic_resolution_debug"] = {
            "orientation": orientation,
            "arrow_branch_position": arrow_branch_position,
            "other_branch_position": other_branch_position,
            "arrow_scores": arrow_scores,
            "arrow_score_best": best_score,
            "arrow_score_second": second_score,
            "arrow_probe_debug": arrow_debug,
            "fallback_used": fallback_used,
            "fallback_arrow_scores": fallback_scores,
            "fallback_arrow_probe_debug": fallback_debug,
            "support_binary_debug": support_binary_debug,
        }
        term["display_name"] = semantic_name
        term["display_terminal_id"] = term["semantic_terminal_id"]

    return terminals


def strategy_detect_three_terminal_orientation(binary, bbox, class_name="", default_orientation="right"):
    """
    Strategia per i 3-terminali.

    Idea generale:
    - NPN / altri 3-terminali: prima lato singolo, ma con validazione finale
      anche sui 3 punti terminali stimati
    - Mosfet: oltre ai probe per il lato singolo, facciamo una validazione
      finale dell'orientazione usando i 3 punti terminali stimati

    Flusso:
    1. calcolo score del lato singolo
    2. calcolo fallback multi-anchor
    3. se classe Mosfet:
       - valuto direttamente le orientazioni candidate usando i 3 punti terminali
    4. se non Mosfet:
       - valuto direttamente le orientazioni candidate usando i 3 punti terminali
    5. se il lato singolo è abbastanza chiaro, uso quello
    6. se non basta, fallback multi-anchor
    7. ultimo fallback: default_orientation YAML
    """
    working_binary = binary
    support_binary_debug = {
        "enabled": False,
    }

    if THREE_TERMINAL_TEXT_SUPPRESS_ENABLE:
        working_binary, support_binary_debug = _build_three_terminal_support_binary(
            binary,
            bbox,
        )

    # -------------------------------------------------
    # 1) Score per il lato singolo
    # -------------------------------------------------
    if class_name == "Mosfet":
        single_side_scores = get_mosfet_single_side_scores(working_binary, bbox)
        single_side_source = "mosfet_near_far"
        single_side_min_score = MOSFET_SINGLE_SIDE_MIN_SCORE
        single_side_margin = MOSFET_SINGLE_SIDE_MARGIN
        lateral_scores = get_mosfet_lateral_gate_scores(working_binary, bbox)
    else:
        single_side_scores = get_local_terminal_probe_scores_center(working_binary, bbox)
        single_side_source = "generic_center"
        single_side_min_score = THREE_TERMINAL_SINGLE_SIDE_MIN_SCORE
        single_side_margin = THREE_TERMINAL_SINGLE_SIDE_MARGIN
        lateral_scores = None

    # Score multi-anchor usati per il fallback template
    multi_scores = get_local_terminal_probe_scores_multi_anchor(
        working_binary,
        bbox,
        anchor_ratios=THREE_TERMINAL_ANCHOR_RATIOS
    )

    ordered_single = sorted(
        ("top", "bottom", "left", "right"),
        key=lambda side: single_side_scores[side],
        reverse=True
    )
    best_side = ordered_single[0]
    second_side = ordered_single[1]
    best_score = single_side_scores[best_side]
    second_score = single_side_scores[second_side]

    if class_name == "Mosfet" and lateral_scores is not None:
        best_lateral_side = "left" if lateral_scores["left"] >= lateral_scores["right"] else "right"
        best_lateral_score = lateral_scores[best_lateral_side]

        best_vertical_side = "top" if single_side_scores["top"] >= single_side_scores["bottom"] else "bottom"
        best_vertical_score = single_side_scores[best_vertical_side]

        if (
            MOSFET_FORCE_LATERAL_GATE
            and best_lateral_score > best_vertical_score * MOSFET_LATERAL_MARGIN
        ):
            best_side = best_lateral_side
            second_side = "right" if best_side == "left" else "left"
            best_score = best_lateral_score
            second_score = lateral_scores[second_side]

    # Queste due variabili DEVONO esistere sempre
    mosfet_orientation_scores = None
    mosfet_orientation_point_debug = None
    generic_orientation_scores = None
    generic_orientation_point_debug = None

    # -------------------------------------------------
    # 2) Validazione finale specifica per Mosfet
    # -------------------------------------------------
    if class_name == "Mosfet":
        candidate_orientations = candidate_mosfet_orientations_from_bbox(bbox)

        mosfet_orientation_scores = {}
        mosfet_orientation_point_debug = {}

        for cand in candidate_orientations:
            cand_score, cand_debug = score_mosfet_orientation_by_terminal_points(
                working_binary,
                bbox,
                cand
            )

            gate_bonus = 0.0
            # Se vuoi riattivarlo in futuro:
            # if lateral_scores is not None and cand in ("left", "right"):
            #     gate_bonus = 0.8 * lateral_scores[cand]
            #     cand_score += gate_bonus

            cand_debug["gate_bonus"] = gate_bonus
            mosfet_orientation_scores[cand] = cand_score
            mosfet_orientation_point_debug[cand] = cand_debug

        ordered_candidates = sorted(
            candidate_orientations,
            key=lambda o: mosfet_orientation_scores[o],
            reverse=True
        )

        cand_best = ordered_candidates[0]
        cand_second = ordered_candidates[1] if len(ordered_candidates) > 1 else None

        cand_best_score = mosfet_orientation_scores[cand_best]
        cand_second_score = mosfet_orientation_scores[cand_second] if cand_second is not None else 0.0

        # Tie-break per casi speculari quasi pari
        if cand_second is not None and _is_specular_pair(cand_best, cand_second):
            ratio = cand_best_score / max(cand_second_score, 1e-6)

            # Se vuoi riattivarlo in futuro:
            # if ratio < 1.15:
            #     chosen = _resolve_specular_tie(
            #         cand_best,
            #         cand_second,
            #         lateral_scores=lateral_scores,
            #         single_side_scores=single_side_scores,
            #     )
            #     cand_best = chosen
            #     cand_best_score = mosfet_orientation_scores[cand_best]
            pass

        if (
            cand_second is None
            or cand_best_score > cand_second_score * MOSFET_ORIENTATION_VALIDATION_MARGIN
        ):
            required_sides = THREE_TERMINAL_TEMPLATES[cand_best]

            debug_scores = dict(multi_scores)
            debug_scores["single_side_scores"] = {
                "top": single_side_scores["top"],
                "bottom": single_side_scores["bottom"],
                "left": single_side_scores["left"],
                "right": single_side_scores["right"],
            }
            debug_scores["single_side_source"] = single_side_source
            debug_scores["decision_mode"] = "three_terminal_mosfet_point_validation"
            debug_scores["single_side"] = cand_best
            debug_scores["single_side_score"] = cand_best_score
            debug_scores["second_side"] = cand_second
            debug_scores["second_side_score"] = cand_second_score
            debug_scores["required_sides"] = list(required_sides)
            debug_scores["missing_side"] = next(
                side for side in ("top", "bottom", "left", "right")
                if side not in required_sides
            )

            if lateral_scores is not None:
                debug_scores["mosfet_lateral_scores"] = lateral_scores
            debug_scores["mosfet_orientation_scores"] = mosfet_orientation_scores
            debug_scores["mosfet_orientation_point_debug"] = mosfet_orientation_point_debug
            debug_scores["three_terminal_support_binary_debug"] = support_binary_debug

            return cand_best, debug_scores

    # -------------------------------------------------
    # 2a) Validazione finale generica sui punti terminali
    #     per i 3-terminali non Mosfet
    # -------------------------------------------------
    if class_name != "Mosfet" and THREE_TERMINAL_POINT_VALIDATION_ENABLE:
        # Prefiltro sull'asse:
        # evitiamo che un transistor "right/left" venga ribaltato in "top/bottom"
        # per colpa di testo o grafica interna.
        if THREE_TERMINAL_AXIS_PREFILTER_ENABLE:
            horizontal_axis_score = max(
                single_side_scores["left"],
                single_side_scores["right"],
            )
            vertical_axis_score = max(
                single_side_scores["top"],
                single_side_scores["bottom"],
            )

            if horizontal_axis_score > vertical_axis_score * THREE_TERMINAL_AXIS_PREFILTER_MARGIN:
                candidate_orientations = ("left", "right")
                axis_prefilter = "horizontal"
            elif vertical_axis_score > horizontal_axis_score * THREE_TERMINAL_AXIS_PREFILTER_MARGIN:
                candidate_orientations = ("top", "bottom")
                axis_prefilter = "vertical"
            else:
                candidate_orientations = ("left", "right", "top", "bottom")
                axis_prefilter = "none"
        else:
            candidate_orientations = ("left", "right", "top", "bottom")
            axis_prefilter = "disabled"

        generic_orientation_scores = {}
        generic_orientation_point_debug = {}

        for cand in candidate_orientations:
            cand_score, cand_debug = score_three_terminal_orientation_by_terminal_points(
                working_binary,
                bbox,
                cand,
                single_weight=THREE_TERMINAL_POINT_VALIDATION_SINGLE_WEIGHT,
            )
            generic_orientation_scores[cand] = cand_score
            generic_orientation_point_debug[cand] = cand_debug

            bjt_base_side_scores = None
            if class_name == "NPN_Transistor":
                bjt_base_side_scores = get_bjt_base_side_scores(working_binary, bbox)

                if "left" in generic_orientation_scores:
                    generic_orientation_scores["left"] += 0.8 * bjt_base_side_scores["left"]

                if "right" in generic_orientation_scores:
                    generic_orientation_scores["right"] += 0.8 * bjt_base_side_scores["right"]

        ordered_candidates = sorted(
            candidate_orientations,
            key=lambda o: generic_orientation_scores[o],
            reverse=True
        )

        cand_best = ordered_candidates[0]
        cand_second = ordered_candidates[1] if len(ordered_candidates) > 1 else None

        cand_best_score = generic_orientation_scores[cand_best]
        cand_second_score = generic_orientation_scores[cand_second] if cand_second is not None else 0.0

        # tie-break solo tra orientazioni speculari
        if cand_second is not None and _is_specular_pair(cand_best, cand_second):
            ratio = cand_best_score / max(cand_second_score, 1e-6)
            if ratio < 1.10:
                cand_best = _resolve_specular_tie(
                    cand_best,
                    cand_second,
                    lateral_scores=None,
                    single_side_scores=single_side_scores,
                )
                cand_best_score = generic_orientation_scores[cand_best]

        if (
            cand_second is None
            or cand_best_score > cand_second_score * THREE_TERMINAL_POINT_VALIDATION_MARGIN
        ):
            required_sides = THREE_TERMINAL_TEMPLATES[cand_best]

            debug_scores = dict(multi_scores)
            debug_scores["single_side_scores"] = {
                "top": single_side_scores["top"],
                "bottom": single_side_scores["bottom"],
                "left": single_side_scores["left"],
                "right": single_side_scores["right"],
            }
            debug_scores["single_side_source"] = single_side_source
            debug_scores["decision_mode"] = "three_terminal_point_validation"
            debug_scores["axis_prefilter"] = axis_prefilter
            debug_scores["candidate_orientations"] = list(candidate_orientations)
            debug_scores["single_side"] = cand_best
            debug_scores["single_side_score"] = cand_best_score
            debug_scores["second_side"] = cand_second
            debug_scores["second_side_score"] = cand_second_score
            debug_scores["required_sides"] = list(required_sides)
            debug_scores["missing_side"] = next(
                side for side in ("top", "bottom", "left", "right")
                if side not in required_sides
            )
            debug_scores["three_terminal_orientation_scores"] = generic_orientation_scores
            debug_scores["three_terminal_orientation_point_debug"] = generic_orientation_point_debug
            if bjt_base_side_scores is not None:
                debug_scores["bjt_base_side_scores"] = bjt_base_side_scores
            debug_scores["three_terminal_support_binary_debug"] = support_binary_debug

            return cand_best, debug_scores

    # -------------------------------------------------
    # 3) Se il lato singolo è abbastanza chiaro, usiamo quello
    # -------------------------------------------------
    if (
        best_score >= single_side_min_score
        and best_score > second_score * single_side_margin
    ):
        required_sides = THREE_TERMINAL_TEMPLATES[best_side]

        debug_scores = dict(multi_scores)
        debug_scores["single_side_scores"] = {
            "top": single_side_scores["top"],
            "bottom": single_side_scores["bottom"],
            "left": single_side_scores["left"],
            "right": single_side_scores["right"],
        }
        debug_scores["single_side_source"] = single_side_source
        debug_scores["decision_mode"] = "three_terminal_single_side"
        debug_scores["single_side"] = best_side
        debug_scores["single_side_score"] = best_score
        debug_scores["second_side"] = second_side
        debug_scores["second_side_score"] = second_score
        debug_scores["required_sides"] = list(required_sides)
        debug_scores["missing_side"] = next(
            side for side in ("top", "bottom", "left", "right")
            if side not in required_sides
        )

        if lateral_scores is not None:
            debug_scores["mosfet_lateral_scores"] = lateral_scores
        if mosfet_orientation_scores is not None:
            debug_scores["mosfet_orientation_scores"] = mosfet_orientation_scores
        if mosfet_orientation_point_debug is not None:
            debug_scores["mosfet_orientation_point_debug"] = mosfet_orientation_point_debug

        if generic_orientation_scores is not None:
            debug_scores["three_terminal_orientation_scores"] = generic_orientation_scores
        if generic_orientation_point_debug is not None:
            debug_scores["three_terminal_orientation_point_debug"] = generic_orientation_point_debug
        debug_scores["three_terminal_support_binary_debug"] = support_binary_debug

        return best_side, debug_scores

    # -------------------------------------------------
    # 4) Fallback: template scoring multi-anchor
    # -------------------------------------------------
    candidate_scores = {}
    for orientation, required_sides in THREE_TERMINAL_TEMPLATES.items():
        missing_side = next(
            side for side in ("top", "bottom", "left", "right")
            if side not in required_sides
        )

        req_vals = [multi_scores[s] for s in required_sides]
        missing_val = multi_scores[missing_side]

        candidate_scores[orientation] = sum(req_vals) + min(req_vals) - missing_val

    best_orientation = max(candidate_scores, key=candidate_scores.get)
    required_sides = THREE_TERMINAL_TEMPLATES[best_orientation]
    missing_side = next(
        side for side in ("top", "bottom", "left", "right")
        if side not in required_sides
    )

    if min(multi_scores[s] for s in required_sides) >= THREE_TERMINAL_MIN_SIDE_SCORE:
        multi_scores["single_side_scores"] = {
            "top": single_side_scores["top"],
            "bottom": single_side_scores["bottom"],
            "left": single_side_scores["left"],
            "right": single_side_scores["right"],
        }
        multi_scores["single_side_source"] = single_side_source
        multi_scores["candidate_scores"] = candidate_scores
        multi_scores["decision_mode"] = "three_terminal_multi_anchor_fallback"
        multi_scores["required_sides"] = list(required_sides)
        multi_scores["missing_side"] = missing_side

        if lateral_scores is not None:
            multi_scores["mosfet_lateral_scores"] = lateral_scores
        if mosfet_orientation_scores is not None:
            multi_scores["mosfet_orientation_scores"] = mosfet_orientation_scores
        if mosfet_orientation_point_debug is not None:
            multi_scores["mosfet_orientation_point_debug"] = mosfet_orientation_point_debug

        if generic_orientation_scores is not None:
            multi_scores["three_terminal_orientation_scores"] = generic_orientation_scores
        if generic_orientation_point_debug is not None:
            multi_scores["three_terminal_orientation_point_debug"] = generic_orientation_point_debug
        multi_scores["three_terminal_support_binary_debug"] = support_binary_debug

        return best_orientation, multi_scores

    # -------------------------------------------------
    # 5) Ultimo fallback: default_orientation YAML
    # -------------------------------------------------
    multi_scores["single_side_scores"] = {
        "top": single_side_scores["top"],
        "bottom": single_side_scores["bottom"],
        "left": single_side_scores["left"],
        "right": single_side_scores["right"],
    }
    multi_scores["single_side_source"] = single_side_source
    multi_scores["candidate_scores"] = candidate_scores
    multi_scores["decision_mode"] = "three_terminal_default_fallback"

    if lateral_scores is not None:
        multi_scores["mosfet_lateral_scores"] = lateral_scores
    if mosfet_orientation_scores is not None:
        multi_scores["mosfet_orientation_scores"] = mosfet_orientation_scores
    if mosfet_orientation_point_debug is not None:
        multi_scores["mosfet_orientation_point_debug"] = mosfet_orientation_point_debug

    if generic_orientation_scores is not None:
        multi_scores["three_terminal_orientation_scores"] = generic_orientation_scores
    if generic_orientation_point_debug is not None:
        multi_scores["three_terminal_orientation_point_debug"] = generic_orientation_point_debug
    multi_scores["three_terminal_support_binary_debug"] = support_binary_debug

    return default_orientation, multi_scores
