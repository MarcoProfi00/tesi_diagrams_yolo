from .config import *
from .geometry import geom_terminal_point_three_terminal
from .probes import (
    get_local_terminal_probe_scores_center,
    get_local_terminal_probe_scores_multi_anchor,
    get_mosfet_lateral_gate_scores,
    get_mosfet_single_side_scores,
    score_mosfet_candidate_terminals,
)

def candidate_mosfet_orientations_from_bbox(bbox):
    """
    Per ora testiamo sempre tutte e 4 le orientazioni.
    È il modo più semplice per capire se il problema nasce
    dal filtro iniziale sul bbox.
    """
    return ("left", "right", "top", "bottom")

#def candidate_mosfet_orientations_from_bbox(bbox):
    """
    Filtro morbido:
    - bbox chiaramente alto  -> gate laterale -> left/right
    - bbox chiaramente largo -> gate sopra/sotto -> top/bottom
    - bbox ambiguo           -> tutte e 4
    """
    x1, y1, x2, y2 = bbox
    width = max(x2 - x1, 1e-6)
    height = max(y2 - y1, 1e-6)

    strong_ratio = 1.30

    if height / width >= strong_ratio:
        return ("left", "right")

    if width / height >= strong_ratio:
        return ("top", "bottom")

    return ("left", "right", "top", "bottom")


def score_mosfet_orientation_by_terminal_points(binary, bbox, orientation):
    """
    Valuta un'orientazione candidata del Mosfet usando i 3 terminali stimati.

    Flusso:
    - genero i 3 punti terminali coerenti con l'orientazione candidata
    - costruisco una lista di terminali candidati
    - delego lo scoring finale a score_mosfet_candidate_terminals(...)

    Questo è molto più robusto dei casi speculari left/right:
    non guarda solo il lato singolo in astratto, ma valuta direttamente
    i punti terminali finali che useremo davvero nel passo 03.
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
        single_weight=MOSFET_SINGLE_TERMINAL_WEIGHT,
    )

    debug = {
        "candidate_terminals": candidate_terminals,
        "score_details": score_details,
        "point_debug": point_debug,
    }

    return total_score, debug

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

def strategy_detect_three_terminal_orientation(binary, bbox, class_name="", default_orientation="right"):
    """
    Strategia per i 3-terminali.

    Idea generale:
    - NPN: la scelta del lato singolo funziona bene con i probe classici
    - Mosfet: oltre ai probe per il lato singolo, facciamo una validazione
      finale dell'orientazione usando i 3 punti terminali stimati

    Flusso:
    1. calcolo score del lato singolo
    2. calcolo fallback multi-anchor
    3. se classe Mosfet:
       - valuto direttamente le orientazioni candidate (left/right oppure top/bottom)
         usando il supporto locale attorno ai 3 terminali stimati
       - se una orientazione è chiaramente migliore, la uso
    4. altrimenti uso il lato singolo se è chiaro
    5. se non basta, fallback multi-anchor
    6. ultimo fallback: default_orientation YAML
    """
    # -------------------------------------------------
    # 1) Score per il lato singolo
    # -------------------------------------------------
    if class_name == "Mosfet":
        single_side_scores = get_mosfet_single_side_scores(binary, bbox)
        single_side_source = "mosfet_near_far"
        single_side_min_score = MOSFET_SINGLE_SIDE_MIN_SCORE
        single_side_margin = MOSFET_SINGLE_SIDE_MARGIN

        lateral_scores = get_mosfet_lateral_gate_scores(binary, bbox)
    else:
        single_side_scores = get_local_terminal_probe_scores_center(binary, bbox)
        single_side_source = "generic_center"
        single_side_min_score = THREE_TERMINAL_SINGLE_SIDE_MIN_SCORE
        single_side_margin = THREE_TERMINAL_SINGLE_SIDE_MARGIN
        lateral_scores = None

    # Score multi-anchor usati per il fallback template
    multi_scores = get_local_terminal_probe_scores_multi_anchor(
        binary,
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
            MOSFET_FORCE_LATERAL_GATE and
            best_lateral_score > best_vertical_score * MOSFET_LATERAL_MARGIN
        ):
            best_side = best_lateral_side
            second_side = "right" if best_side == "left" else "left"
            best_score = best_lateral_score
            second_score = lateral_scores[second_side]

    # -------------------------------------------------
    # 2) Validazione finale specifica per Mosfet
    # -------------------------------------------------
    mosfet_orientation_scores = None
    mosfet_orientation_point_debug = None

    if class_name == "Mosfet":
        candidate_orientations = candidate_mosfet_orientations_from_bbox(bbox)

        mosfet_orientation_scores = {}
        mosfet_orientation_point_debug = {}

        for cand in candidate_orientations:
            cand_score, cand_debug = score_mosfet_orientation_by_terminal_points(
                binary,
                bbox,
                cand
            )

            gate_bonus = 0.0
            #if lateral_scores is not None and cand in ("left", "right"):
            #    gate_bonus = 0.8 * lateral_scores[cand]
            #    cand_score += gate_bonus

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
        cand_second_score = (
            mosfet_orientation_scores[cand_second]
            if cand_second is not None else 0.0
        )

        # -------------------------------------------------
        # Tie-break per casi speculari quasi pari
        # -------------------------------------------------
        if cand_second is not None and _is_specular_pair(cand_best, cand_second):
            ratio = cand_best_score / max(cand_second_score, 1e-6)

            # Se sono molto vicini, risolviamo con un criterio dedicato
            #if ratio < 1.15:
            #    chosen = _resolve_specular_tie(
            #        cand_best,
            #        cand_second,
            #        lateral_scores=lateral_scores,
            #        single_side_scores=single_side_scores,
            #    )
            #    cand_best = chosen
            #    cand_best_score = mosfet_orientation_scores[cand_best]
            pass

        # Se una orientazione candidata è chiaramente migliore,
        # la usiamo direttamente.
        if (
            cand_second is None or
            cand_best_score > cand_second_score * MOSFET_ORIENTATION_VALIDATION_MARGIN
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

            return cand_best, debug_scores

    # -------------------------------------------------
    # 3) Se il lato singolo è abbastanza chiaro, usiamo quello
    # -------------------------------------------------
    if (
        best_score >= single_side_min_score and
        best_score > second_score * single_side_margin
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

    return default_orientation, multi_scores