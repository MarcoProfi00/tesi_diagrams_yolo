
from .config import *
from .geometry import geom_terminal_point_opamp
from .probes import score_point_directional_support


def _get_opamp_orientation_defs(meta: dict, orientation: str):
    terminals_def = meta.get("orientations", {}).get(orientation)
    if terminals_def is None:
        raise ValueError(f"Nessuna definizione opamp per orientazione '{orientation}'")
    return terminals_def


def _score_opamp_terminal(binary, bbox, orientation: str, term_def: dict):
    point, point_debug = geom_terminal_point_opamp(
        binary,
        bbox,
        orientation,
        term_def,
    )
    x, y = point
    relative_position = term_def["relative_position"]

    directional_score = score_point_directional_support(
        binary,
        x,
        y,
        relative_position,
        outward=OPAMP_DIRECTIONAL_OUTWARD,
        inward=OPAMP_DIRECTIONAL_INWARD,
        halfspan=OPAMP_DIRECTIONAL_HALFSPAN,
    )

    weight = OPAMP_OUTPUT_WEIGHT if term_def.get("terminal_role") == "output" else 1.0
    weighted_score = weight * directional_score

    return weighted_score, {
        "name": term_def.get("name"),
        "relative_position": relative_position,
        "terminal_role": term_def.get("terminal_role"),
        "slot": term_def.get("slot"),
        "point": point,
        "directional_score": directional_score,
        "weight": weight,
        "weighted_score": weighted_score,
        "point_debug": point_debug,
    }


def detect_opamp_terminals(meta: dict, binary, bbox, default_orientation="right"):
    """
    Reset strategico dell'opamp.

    Fase attuale:
    1) stimiamo l'orientazione usando SOLO i 3 terminali obbligatori
    2) restituiamo SOLO i 3 terminali obbligatori
    3) ignoriamo temporaneamente gli auxiliary, così non inquinano né
       l'orientazione né la localizzazione dei pin principali
    """
    candidate_orientations = ("right", "left", "top", "bottom")

    orientation_scores = {}
    orientation_debug = {}

    for orientation in candidate_orientations:
        terminals_def = _get_opamp_orientation_defs(meta, orientation)
        mandatory_defs = [t for t in terminals_def if not t.get("optional", False)]

        total_score = 0.0
        score_details = []

        for term_def in mandatory_defs:
            weighted_score, debug = _score_opamp_terminal(
                binary,
                bbox,
                orientation,
                term_def,
            )
            total_score += weighted_score
            score_details.append(debug)

        orientation_scores[orientation] = total_score
        orientation_debug[orientation] = {
            "mandatory_terminals": [t["name"] for t in mandatory_defs],
            "score_details": score_details,
        }

    ordered = sorted(
        candidate_orientations,
        key=lambda o: orientation_scores[o],
        reverse=True,
    )

    best_orientation = ordered[0]
    second_orientation = ordered[1]
    best_score = orientation_scores[best_orientation]
    second_score = orientation_scores[second_orientation]

    chosen_orientation = best_orientation
    decision_mode = "opamp_mandatory_only_orientation"

    if best_score <= second_score * OPAMP_ORIENTATION_MARGIN:
        chosen_orientation = (
            default_orientation
            if default_orientation in candidate_orientations
            else best_orientation
        )
        decision_mode = "opamp_default_fallback_after_close_scores"

    chosen_defs = _get_opamp_orientation_defs(meta, chosen_orientation)

    active_terminals = []
    optional_debug = {}

    for term_def in chosen_defs:
        if not term_def.get("optional", False):
            active_terminals.append(dict(term_def))
            continue

        point, point_debug = geom_terminal_point_opamp(
            binary,
            bbox,
            chosen_orientation,
            term_def,
        )

        is_active = bool(point_debug.get("aux_detected", False))
        optional_debug[term_def["name"]] = {
            "name": term_def.get("name"),
            "point": point,
            "point_debug": point_debug,
            "is_active": is_active,
        }

        if is_active:
            active_terminals.append(dict(term_def))

    debug_scores = {
        "decision_mode": decision_mode,
        "chosen_orientation": chosen_orientation,
        "best_orientation": best_orientation,
        "best_score": round(float(best_score), 4),
        "second_orientation": second_orientation,
        "second_score": round(float(second_score), 4),
        "orientation_scores": {
            k: round(float(v), 4) for k, v in orientation_scores.items()
        },
        "orientation_debug": orientation_debug,
        "optional_debug": optional_debug,
        "optional_terminals_disabled": False,
        "active_terminal_names": [t["name"] for t in active_terminals],
    }

    return active_terminals, chosen_orientation, debug_scores
