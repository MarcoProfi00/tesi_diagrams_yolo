# Trova il pixel etichettato più vicino al terminale dentro una finestra.
from __future__ import annotations

# Trova il pixel etichettato vicino al terminale in una finestra
# Return
#   label del pixel
#   snap point
#   distance
def find_nearest_labeled_pixel(labels: np.ndarray, term: dict, window):
    x1, y1, x2, y2 = window
    roi = labels[y1:y2, x1:x2]

    ys, xs = np.where(roi > 0)
    if len(xs) == 0:
        return None

    abs_xs = xs + x1
    abs_ys = ys + y1

    tx = float(term["x"])
    ty = float(term["y"])

    d2 = (abs_xs - tx) ** 2 + (abs_ys - ty) ** 2
    best_idx = int(np.argmin(d2))

    px = int(abs_xs[best_idx])
    py = int(abs_ys[best_idx])
    lbl = int(labels[py, px])
    dist = float(np.sqrt(d2[best_idx]))

    return {
        "label": lbl,
        "snap_point": [px, py],
        "snap_distance": round(dist, 3),
    }


# =========================================================
# MATCH DI UN SINGOLO TERMINALE
# =========================================================
# 1. prova finestra direzionale
# 2. se non trova nulla, prova finestra quadrata
# 3. se ancora nulla, terminale unmatched
#
# Return:
#   matched_label
#   match_mode
#   search_window
#   snap_point
#   snap_distance
#   is_suspicious
def match_terminal_to_skeleton_label(labels: np.ndarray, term: dict):
    # Primo tentativo: finestra direzionale
    dir_window = get_directional_window(
        term,
        labels.shape,
        outward=TERMINAL_SEARCH_OUTWARD,
        inward=TERMINAL_SEARCH_INWARD,
        halfspan=TERMINAL_DIRECTIONAL_HALFSPAN,
    )
    dir_labels = collect_labels_in_window(labels, dir_window)
    nearest = find_nearest_labeled_pixel(labels, term, dir_window)

    if nearest is not None:
        return {
            "terminal_id": term["terminal_id"],
            "candidate_labels": dir_labels,
            "matched_label": int(nearest["label"]),
            "match_mode": "directional",
            "search_window": [int(v) for v in dir_window],
            "snap_point": nearest["snap_point"],
            "snap_distance": nearest["snap_distance"],
            "is_suspicious": float(nearest["snap_distance"]) > float(MAX_REASONABLE_SNAP_DISTANCE),
        }

    # Secondo tentativo: piccolo quadrato attorno al terminale
    sq_window = get_square_window(term, labels.shape, radius=TERMINAL_SQUARE_FALLBACK_RADIUS)
    sq_labels = collect_labels_in_window(labels, sq_window)
    nearest = find_nearest_labeled_pixel(labels, term, sq_window)

    if nearest is not None:
        return {
            "terminal_id": term["terminal_id"],
            "candidate_labels": sq_labels,
            "matched_label": int(nearest["label"]),
            "match_mode": "square_fallback",
            "search_window": [int(v) for v in sq_window],
            "snap_point": nearest["snap_point"],
            "snap_distance": nearest["snap_distance"],
            "is_suspicious": float(nearest["snap_distance"]) > float(MAX_REASONABLE_SNAP_DISTANCE),
        }

    # Nessun match trovato.
    return {
        "terminal_id": term["terminal_id"],
        "candidate_labels": [],
        "matched_label": None,
        "match_mode": "unmatched",
        "search_window": None,
        "snap_point": None,
        "snap_distance": None,
        "is_suspicious": True,
    }


# Recupera terminali di analog meter rimasti unmatched
# Usa una finestra più grande
def attach_unmatched_analog_meter_terminals(
    components: list[dict],
    terminal_match_debug: dict,
    labels: np.ndarray,
):
    for component in components:
        if normalize_class_name(component.get("class_name")) != "analog_meter":
            continue

        for term in component.get("terminals", []):
            terminal_id = term.get("terminal_id")
            if terminal_id is None:
                continue

            current_match = terminal_match_debug.get(terminal_id, {})
            if current_match.get("matched_label") is not None:
                continue

            sq_window = get_square_window(
                term,
                labels.shape,
                radius=ANALOG_METER_FALLBACK_RADIUS,
            )
            sq_labels = collect_labels_in_window(labels, sq_window)
            nearest = find_nearest_labeled_pixel(labels, term, sq_window)

            if nearest is None:
                continue
            if float(nearest["snap_distance"]) > ANALOG_METER_MAX_SNAP_DISTANCE:
                continue

            terminal_match_debug[terminal_id] = {
                "terminal_id": terminal_id,
                "candidate_labels": sq_labels,
                "matched_label": int(nearest["label"]),
                "match_mode": "analog_meter_wide_fallback",
                "search_window": [int(v) for v in sq_window],
                "snap_point": nearest["snap_point"],
                "snap_distance": nearest["snap_distance"],
                "is_suspicious": False,
            }

# Matcha un aux opamp unmatched se esiste un terminale esterno allineato
# Gli aux degli opamp possono cadere dentro il traingolo dell'opamp e perdere lo skeleton reale
def attach_unmatched_opamp_aux_to_external_terminals(
    terminals: list[dict],
    terminal_match_debug: dict,
):
    terminal_candidates = [
        term
        for term in terminals
        if is_external_terminal_component(term)
        and terminal_match_debug.get(term["terminal_id"], {}).get("matched_label") is not None
    ]

    for aux_term in terminals:
        aux_id = aux_term["terminal_id"]
        aux_match = terminal_match_debug.get(aux_id, {})

        if aux_match.get("matched_label") is not None:
            continue

        if not is_opamp_aux_terminal(aux_term):
            continue

        candidates = []
        for candidate in terminal_candidates:
            if not is_terminal_in_aux_direction(aux_term, candidate):
                continue

            dx = abs(float(candidate["x"]) - float(aux_term["x"]))
            dy = abs(float(candidate["y"]) - float(aux_term["y"]))

            if dx > OPAMP_AUX_EXTERNAL_MAX_DX:
                continue
            if dy > OPAMP_AUX_EXTERNAL_MAX_DY:
                continue

            candidate_match = terminal_match_debug.get(candidate["terminal_id"], {})
            candidates.append({
                "term": candidate,
                "match": candidate_match,
                "dx": dx,
                "dy": dy,
            })

        if not candidates:
            continue

        best = min(candidates, key=lambda item: (item["dx"], item["dy"]))
        best_term = best["term"]
        best_match = best["match"]
        snap_point = best_match.get("snap_point")

        terminal_match_debug[aux_id] = {
            "terminal_id": aux_id,
            "candidate_labels": [int(best_match["matched_label"])],
            "matched_label": int(best_match["matched_label"]),
            "match_mode": "opamp_aux_external_terminal_virtual",
            "search_window": None,
            "snap_point": snap_point,
            "snap_distance": round(float(best["dy"]), 3),
            "is_suspicious": False,
            "virtual_match": True,
            "virtual_match_reason": "unmatched_opamp_aux_aligned_to_external_terminal",
            "external_terminal_id": best_term["terminal_id"],
            "external_terminal_point": [
                round(float(best_term["x"]), 3),
                round(float(best_term["y"]), 3),
            ],
            "axis_delta": [
                round(float(best["dx"]), 3),
                round(float(best["dy"]), 3),
            ],
        }
import numpy as np

from .config import (
    ANALOG_METER_FALLBACK_RADIUS,
    ANALOG_METER_MAX_SNAP_DISTANCE,
    MAX_REASONABLE_SNAP_DISTANCE,
    OPAMP_AUX_EXTERNAL_MAX_DX,
    OPAMP_AUX_EXTERNAL_MAX_DY,
    TERMINAL_DIRECTIONAL_HALFSPAN,
    TERMINAL_SEARCH_INWARD,
    TERMINAL_SEARCH_OUTWARD,
    TERMINAL_SQUARE_FALLBACK_RADIUS,
)
from .geometry import get_directional_window, get_square_window
from .heuristics_opamp import (
    is_external_terminal_component,
    is_opamp_aux_terminal,
    is_terminal_in_aux_direction,
)
from .ids import normalize_class_name
from .skeleton_ops import collect_labels_in_window
