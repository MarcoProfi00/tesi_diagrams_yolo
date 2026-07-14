"""Match tra terminali stimati e connected component dello skeleton dei fili."""

from __future__ import annotations

import numpy as np

from .config import (
    ANALOG_METER_FALLBACK_RADIUS,
    ANALOG_METER_MAX_SNAP_DISTANCE,
    LATERAL_TERMINAL_REMAP_MAX_GAP,
    LATERAL_TERMINAL_REMAP_MIN_GAP,
    LATERAL_TERMINAL_REMAP_Y_TOL,
    MAX_REASONABLE_SNAP_DISTANCE,
    OPAMP_AUX_EXTERNAL_MAX_DX,
    OPAMP_AUX_EXTERNAL_MAX_DY,
    OPAMP_AUX_LABEL_REMAP_MAX_GAP,
    OPAMP_AUX_LABEL_REMAP_MIN_GAP,
    OPAMP_AUX_LABEL_REMAP_X_TOL,
    OUTWARD_STUB_REMAP_MAX_GAP,
    OUTWARD_STUB_REMAP_MAX_LABEL_WIDTH,
    OUTWARD_STUB_REMAP_MIN_GAP,
    OUTWARD_STUB_REMAP_SOURCE_CLASSES,
    OUTWARD_STUB_REMAP_SOURCE_SIDES,
    OUTWARD_STUB_REMAP_X_TOL,
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

def find_nearest_labeled_pixel(labels: np.ndarray, term: dict, window):
    """
    Trova il pixel di skeleton etichettato piu' vicino al terminale.

    La ricerca e' limitata a una finestra gia' scelta dal chiamante. Ritorna la
    label della connected component, il punto di aggancio e la distanza dal
    terminale stimato.
    """
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


def match_terminal_to_skeleton_label(labels: np.ndarray, term: dict):
    """
    Aggancia un terminale alla label dello skeleton piu' plausibile.

    Ordine:
      1. finestra direzionale coerente con relative_position;
      2. fallback quadrato attorno al terminale;
      3. unmatched se non si trova nessuna label.
    """
    # Primo tentativo: finestra direzionale, cioe' spinta verso l'esterno del
    # componente lungo il lato del terminale.
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

    # Secondo tentativo: piccolo quadrato attorno al terminale, utile quando il
    # lato stimato e' impreciso o lo skeleton e' leggermente disallineato.
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


def attach_unmatched_analog_meter_terminals(
    components: list[dict],
    terminal_match_debug: dict,
    labels: np.ndarray,
):
    """
    Recupera terminali Analog_Meter rimasti unmatched con una finestra ampia.

    I post dell'analog meter possono essere distanti dal punto terminale stimato,
    quindi il fallback standard puo' non bastare.
    """
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

def attach_unmatched_opamp_aux_to_external_terminals(
    terminals: list[dict],
    terminal_match_debug: dict,
):
    """
    Match virtuale per aux opamp rimasti unmatched.

    Se un aux non trova skeleton ma c'e' un Terminal esterno allineato nella
    direzione corretta, eredita la label di quel terminale. Serve per pin di
    alimentazione disegnati vicino al triangolo dell'opamp.
    """
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


def attach_unmatched_lateral_terminal_labels(
    terminals: list[dict],
    terminal_match_debug: dict,
    labels: np.ndarray,
):
    """
    Recupera terminali top/bottom agganciandoli a label laterali vicine.

    Alcuni terminali cadono vicino alla fine di uno stub laterale e non dentro
    la finestra direzionale; qui cerchiamo label nella banda orizzontale.
    """
    label_to_terminal_ids = {}
    for terminal_id, match in terminal_match_debug.items():
        matched_label = match.get("matched_label")
        if matched_label is None:
            continue
        label_to_terminal_ids.setdefault(int(matched_label), []).append(str(terminal_id))

    h, w = labels.shape[:2]
    for term in terminals:
        terminal_id = term.get("terminal_id")
        if terminal_id is None:
            continue

        current_match = terminal_match_debug.get(terminal_id, {})
        if current_match.get("matched_label") is not None:
            continue

        side = str(term.get("relative_position") or "").strip().lower()
        if side not in {"top", "bottom"}:
            continue

        tx = int(round(float(term["x"])))
        ty = int(round(float(term["y"])))
        x1 = max(0, tx - int(LATERAL_TERMINAL_REMAP_MAX_GAP))
        x2 = min(w, tx + int(LATERAL_TERMINAL_REMAP_MAX_GAP) + 1)
        y1 = max(0, ty - int(LATERAL_TERMINAL_REMAP_Y_TOL))
        y2 = min(h, ty + int(LATERAL_TERMINAL_REMAP_Y_TOL) + 1)
        if x2 <= x1 or y2 <= y1:
            continue

        roi = labels[y1:y2, x1:x2]
        candidate_labels = [int(value) for value in np.unique(roi) if int(value) > 0]
        if not candidate_labels:
            continue

        best = None
        for candidate_label in candidate_labels:
            ys, xs = np.where(labels == int(candidate_label))
            if len(xs) == 0:
                continue

            band_mask = np.abs(ys - ty) <= int(LATERAL_TERMINAL_REMAP_Y_TOL)
            if not np.any(band_mask):
                continue

            band_xs = xs[band_mask]
            band_ys = ys[band_mask]
            lateral_deltas = np.abs(band_xs - tx)
            valid_mask = lateral_deltas >= int(LATERAL_TERMINAL_REMAP_MIN_GAP)
            if not np.any(valid_mask):
                continue

            cand_xs = band_xs[valid_mask]
            cand_ys = band_ys[valid_mask]
            cand_deltas = lateral_deltas[valid_mask]
            best_idx = int(np.argmin(cand_deltas))
            px = int(cand_xs[best_idx])
            py = int(cand_ys[best_idx])
            lateral_gap = float(cand_deltas[best_idx])
            vertical_gap = float(abs(py - ty))
            snap_distance = float(np.hypot(px - tx, py - ty))
            carries_other_terminal = 1 if label_to_terminal_ids.get(int(candidate_label)) else 0

            score = (
                carries_other_terminal,
                -vertical_gap,
                -lateral_gap,
                -snap_distance,
            )
            if best is None or score > best["score"]:
                best = {
                    "score": score,
                    "label": int(candidate_label),
                    "snap_point": [int(px), int(py)],
                    "snap_distance": snap_distance,
                    "search_window": [int(x1), int(y1), int(x2), int(y2)],
                }

        if best is None:
            continue

        terminal_match_debug[terminal_id] = {
            "terminal_id": terminal_id,
            "candidate_labels": [int(best["label"])],
            "matched_label": int(best["label"]),
            "match_mode": "lateral_terminal_remap",
            "search_window": best["search_window"],
            "snap_point": best["snap_point"],
            "snap_distance": round(float(best["snap_distance"]), 3),
            "is_suspicious": False,
            "virtual_match": True,
            "virtual_match_reason": "unmatched_terminal_lateral_label_remap",
        }


def remap_opamp_aux_to_aligned_label(
    terminals: list[dict],
    terminal_match_debug: dict,
    labels: np.ndarray,
):
    """
    Rimappa aux opamp unmatched verso una label verticale allineata.

    E' un fallback pixel-based diverso dal match virtuale con Terminal esterno:
    cerca direttamente una label dello skeleton sopra/sotto l'aux.
    """
    h, w = labels.shape[:2]

    for aux_term in terminals:
        aux_id = aux_term["terminal_id"]
        current_match = terminal_match_debug.get(aux_id, {})
        if current_match.get("matched_label") is not None:
            continue
        if not is_opamp_aux_terminal(aux_term):
            continue

        side = str(aux_term.get("relative_position") or "").strip().lower()
        if side not in {"top", "bottom"}:
            continue

        tx = int(round(float(aux_term["x"])))
        ty = int(round(float(aux_term["y"])))
        x1 = max(0, tx - int(OPAMP_AUX_LABEL_REMAP_X_TOL))
        x2 = min(w, tx + int(OPAMP_AUX_LABEL_REMAP_X_TOL) + 1)
        y1 = max(0, ty - int(OPAMP_AUX_LABEL_REMAP_MAX_GAP))
        y2 = min(h, ty + int(OPAMP_AUX_LABEL_REMAP_MAX_GAP) + 1)
        if x2 <= x1 or y2 <= y1:
            continue

        roi = labels[y1:y2, x1:x2]
        candidate_labels = [int(v) for v in np.unique(roi) if int(v) > 0]
        if not candidate_labels:
            continue

        best = None
        for candidate_label in candidate_labels:
            ys, xs = np.where(labels == int(candidate_label))
            if len(xs) == 0:
                continue

            min_x = int(xs.min())
            max_x = int(xs.max())
            min_y = int(ys.min())
            max_y = int(ys.max())
            if tx < min_x - int(OPAMP_AUX_LABEL_REMAP_X_TOL) or tx > max_x + int(OPAMP_AUX_LABEL_REMAP_X_TOL):
                continue

            if side == "top":
                edge_mask = ys <= ty - int(OPAMP_AUX_LABEL_REMAP_MIN_GAP)
                direction_ok = np.any(edge_mask)
            else:
                edge_mask = ys >= ty + int(OPAMP_AUX_LABEL_REMAP_MIN_GAP)
                direction_ok = np.any(edge_mask)
            if not direction_ok:
                continue

            edge_points = np.column_stack((xs[edge_mask], ys[edge_mask]))
            if len(edge_points) == 0:
                edge_points = np.column_stack((xs, ys))
            d2 = (edge_points[:, 0] - tx) ** 2 + (edge_points[:, 1] - ty) ** 2
            best_idx = int(np.argmin(d2))
            px = int(edge_points[best_idx, 0])
            py = int(edge_points[best_idx, 1])
            gap = float(abs(py - ty))
            if gap < float(OPAMP_AUX_LABEL_REMAP_MIN_GAP) or gap > float(OPAMP_AUX_LABEL_REMAP_MAX_GAP):
                continue
            snap_distance = float(np.hypot(px - tx, py - ty))

            score = (
                -abs(px - tx),
                -gap,
                -snap_distance,
                float(max_y - min_y + 1),
                float(max_x - min_x + 1),
            )
            if best is None or score > best["score"]:
                best = {
                    "score": score,
                    "label": int(candidate_label),
                    "snap_point": [int(px), int(py)],
                    "snap_distance": snap_distance,
                    "search_window": [int(x1), int(y1), int(x2), int(y2)],
                }

        if best is None:
            continue

        terminal_match_debug[aux_id] = {
            "terminal_id": aux_id,
            "candidate_labels": [int(best["label"])],
            "matched_label": int(best["label"]),
            "match_mode": "opamp_aux_aligned_label_remap",
            "search_window": best["search_window"],
            "snap_point": best["snap_point"],
            "snap_distance": round(float(best["snap_distance"]), 3),
            "is_suspicious": False,
            "virtual_match": True,
            "virtual_match_reason": "unmatched_opamp_aux_aligned_to_nearby_label",
        }


def remap_monoterminal_outward_stub_matches(
    terminals: list[dict],
    terminal_match_debug: dict,
    labels: np.ndarray,
):
    """
    Corregge match su stub interni per componenti monoterminali.

    Per classi come Antenna il primo match puo' cadere su un frammento vicino al
    simbolo invece che sul filo esterno. Questo remap cerca una label sottile e
    allineata verso l'esterno.
    """
    label_to_terminal_ids = {}
    for terminal_id, match in terminal_match_debug.items():
        matched_label = match.get("matched_label")
        if matched_label is None:
            continue
        label_to_terminal_ids.setdefault(int(matched_label), []).append(terminal_id)

    for term in terminals:
        class_name = normalize_class_name(term.get("component_class_name"))
        if class_name not in OUTWARD_STUB_REMAP_SOURCE_CLASSES:
            continue

        side = str(term.get("relative_position") or "").strip().lower()
        if side not in OUTWARD_STUB_REMAP_SOURCE_SIDES:
            continue

        terminal_id = term.get("terminal_id")
        if terminal_id is None:
            continue

        current_match = terminal_match_debug.get(terminal_id, {})
        current_label = current_match.get("matched_label")
        if current_label is None:
            continue

        best = _find_outward_stub_target_label(
            labels,
            term,
            int(current_label),
            label_to_terminal_ids,
            terminal_id,
        )
        if best is None:
            continue

        terminal_match_debug[terminal_id] = {
            "terminal_id": terminal_id,
            "candidate_labels": sorted(set(current_match.get("candidate_labels", [])) | {int(best["label"])}),
            "matched_label": int(best["label"]),
            "match_mode": "outward_stub_remap",
            "search_window": best["search_window"],
            "snap_point": best["snap_point"],
            "snap_distance": round(float(best["snap_distance"]), 3),
            "is_suspicious": False,
            "previous_matched_label": int(current_label),
            "previous_snap_point": current_match.get("snap_point"),
            "virtual_match": True,
            "virtual_match_reason": "monoterminal_outward_stub_remap",
        }


def _find_outward_stub_target_label(
    labels: np.ndarray,
    term: dict,
    current_label: int,
    label_to_terminal_ids: dict,
    terminal_id: str,
):
    """Cerca la migliore label esterna verso cui rimappare uno stub monoterminale."""
    tx = int(round(float(term["x"])))
    ty = int(round(float(term["y"])))
    side = str(term.get("relative_position") or "").strip().lower()
    h, w = labels.shape[:2]

    x1 = max(0, tx - int(OUTWARD_STUB_REMAP_X_TOL))
    x2 = min(w, tx + int(OUTWARD_STUB_REMAP_X_TOL) + 1)
    if side == "bottom":
        y1 = max(0, ty + int(OUTWARD_STUB_REMAP_MIN_GAP))
        y2 = min(h, ty + int(OUTWARD_STUB_REMAP_MAX_GAP) + 1)
    else:
        y1 = max(0, ty - int(OUTWARD_STUB_REMAP_MAX_GAP))
        y2 = min(h, ty - int(OUTWARD_STUB_REMAP_MIN_GAP) + 1)

    if y2 <= y1 or x2 <= x1:
        return None

    roi = labels[y1:y2, x1:x2]
    candidate_labels = [
        int(value)
        for value in np.unique(roi)
        if int(value) > 0 and int(value) != int(current_label)
    ]
    if not candidate_labels:
        return None

    best = None
    for candidate_label in candidate_labels:
        coords = np.column_stack(np.where(labels == int(candidate_label)))
        if len(coords) == 0:
            continue

        ys = coords[:, 0]
        xs = coords[:, 1]
        min_x = int(xs.min())
        max_x = int(xs.max())
        min_y = int(ys.min())
        max_y = int(ys.max())
        width = max_x - min_x + 1

        if width > int(OUTWARD_STUB_REMAP_MAX_LABEL_WIDTH):
            continue
        if tx < min_x - int(OUTWARD_STUB_REMAP_X_TOL) or tx > max_x + int(OUTWARD_STUB_REMAP_X_TOL):
            continue

        if side == "bottom":
            gap = float(min_y - ty)
            candidate_mask = ys == ys.min()
        else:
            gap = float(ty - max_y)
            candidate_mask = ys == ys.max()
        if gap < float(OUTWARD_STUB_REMAP_MIN_GAP) or gap > float(OUTWARD_STUB_REMAP_MAX_GAP):
            continue

        edge_points = coords[candidate_mask]
        if len(edge_points) == 0:
            edge_points = coords
        dxs = np.abs(edge_points[:, 1] - tx)
        best_idx = int(np.argmin(dxs))
        py = int(edge_points[best_idx, 0])
        px = int(edge_points[best_idx, 1])
        snap_distance = float(np.hypot(px - tx, py - ty))

        other_terminal_ids = [
            other_id
            for other_id in label_to_terminal_ids.get(int(candidate_label), [])
            if other_id != terminal_id
        ]
        carries_other_terminal = 1 if other_terminal_ids else 0

        score = (
            carries_other_terminal,
            -abs(px - tx),
            -gap,
            -snap_distance,
        )
        if best is None or score > best["score"]:
            best = {
                "score": score,
                "label": int(candidate_label),
                "snap_point": [int(px), int(py)],
                "snap_distance": snap_distance,
                "search_window": [int(x1), int(y1), int(x2), int(y2)],
            }

    return best
