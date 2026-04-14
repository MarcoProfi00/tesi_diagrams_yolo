"""
06_match_terminals_to_nets.py

Scopo:
    Assegnare a ogni terminale una net finale, a partire dalla label map del passo 05.

Pipeline:
    1. carica label_map e nets
    2. costruisce la preferred net dal passo 05
    3. prova una sequenza di search stages:
       - directional_primary
       - circle_primary
       - directional_fallback
       - circle_fallback
    4. sceglie la net migliore
    5. assegna confidence e warning
    6. aggiorna components / terminals / connections
"""

from pathlib import Path
import os
import json
import cv2
import numpy as np

# =========================================================
# PATHS / INPUT-OUTPUT
# =========================================================
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PIPELINE_DATASET = os.environ.get("PIPELINE_DATASET", "topology_v6_opamp")

INPUT_DIR = PROJECT_ROOT / "outputs" / PIPELINE_DATASET / "05_build_nets"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / PIPELINE_DATASET / "06_match_terminals_to_nets"
DEBUG_DIR = OUTPUT_DIR / "debug_images"

OPAMP_AUX_VERTICAL_OUTWARD = 56
OPAMP_AUX_VERTICAL_INWARD = 8
OPAMP_AUX_VERTICAL_X_TOL = 6
OPAMP_AUX_VERTICAL_MIN_PIXELS = 2
OPAMP_AUX_VERTICAL_X_PENALTY = 1.6
OPAMP_AUX_VERTICAL_COUNT_WEIGHT = 0.30
OPAMP_AUX_PREFERRED_BONUS = 8.0

OPAMP_AUX_MAX_OK_DISTANCE = 48.0
OPAMP_AUX_MAX_PREFERRED_DISTANCE = 160.0

# =========================================================
# BASE SEARCH PARAMETERS
# =========================================================
# Ricerca base attorno al terminale.
# Idea: non usare solo un cerchio, ma prima una ricerca direzionale coerente
# con il lato del terminale (left/right/top/bottom), poi fallback circolari.
BASE_DIRECTIONAL_OUTWARD = 18
BASE_DIRECTIONAL_INWARD = 5
BASE_DIRECTIONAL_HALFSPAN = 6
BASE_CIRCLE_RADIUS = 10
BASE_FALLBACK_RADIUS = 24

# =========================================================
# CLASS-SPECIFIC SEARCH OVERRIDES
# =========================================================
# Override per classi in cui il terminale può essere più lontano dal wire
# o il match è più ambiguo.
CLASS_SEARCH_OVERRIDES = {
    "Switch": {
        "directional_outward": 30,
        "directional_inward": 8,
        "directional_halfspan": 10,
        "circle_radius": 14,
        "fallback_radius": 30,
    },
    "Inductor": {
        "directional_outward": 30,
        "directional_inward": 8,
        "directional_halfspan": 10,
        "circle_radius": 14,
        "fallback_radius": 30,
    },
    "Meter": {
        "directional_outward": 22,
        "directional_inward": 6,
        "directional_halfspan": 8,
        "circle_radius": 12,
        "fallback_radius": 26,
    },
    "Current_Source": {
        "directional_outward": 22,
        "directional_inward": 6,
        "directional_halfspan": 8,
        "circle_radius": 12,
        "fallback_radius": 26,
    },
    "Voltage_Source": {
        "directional_outward": 22,
        "directional_inward": 6,
        "directional_halfspan": 8,
        "circle_radius": 12,
        "fallback_radius": 26,
    },
    "Diode": {
        "directional_outward": 18,
        "directional_inward": 5,
        "directional_halfspan": 18,
        "circle_radius": 18,
        "fallback_radius": 38,
    },
}

# =========================================================
# MATCH CONFIDENCE THRESHOLDS
# =========================================================
MAX_OK_DISTANCE = 18.0
#DEBUG
SAVE_DEBUG_IMAGES = True
DEBUG_FONT_SCALE = 0.48
DEBUG_FONT_THICKNESS = 1


DEBUG_TEXT_COLOR_NONE = (80, 80, 80)      # grigio scuro

DEBUG_BOX_COLOR = (210, 255, 255)         # giallo chiaro
DEBUG_BOX_BORDER_COLOR = (120, 160, 160)


DEBUG_POINT_COLOR_NONE = (90, 90, 90)

DEBUG_SNAP_POINT_COLOR = (255, 0, 0)      # blu
DEBUG_LINE_THICKNESS = 2
DEBUG_TERMINAL_RADIUS = 4
DEBUG_SNAP_RADIUS = 3

DEBUG_TEXT_COLOR_OK = (0, 120, 0)
DEBUG_TEXT_COLOR_SUSPICIOUS = (0, 140, 220)

DEBUG_POINT_COLOR_OK = (0, 200, 0)
DEBUG_POINT_COLOR_SUSPICIOUS = (0, 165, 255)


# ---------------------------------------------------------
# Utility base
# ---------------------------------------------------------
def load_label_map(path: Path) -> np.ndarray:
    if not path.exists():
        raise FileNotFoundError(f"Label map non trovata: {path}")
    return np.load(path)

def build_net_index_map(nets):
    out = {}
    for net in nets:
        out[int(net["net_index"])] = net
    return out

def build_source_label_to_net_index_map(nets):
    out = {}
    for net in nets:
        net_index = int(net["net_index"])
        source_labels = net.get("merged_source_labels", [net["source_label"]])
        for source_label in source_labels:
            out[int(source_label)] = net_index
    return out

def clamp_window(x1, y1, x2, y2, w, h):
    return (
        max(0, min(w, x1)),
        max(0, min(h, y1)),
        max(0, min(w, x2)),
        max(0, min(h, y2)),
    )

def draw_boxed_text(
    image,
    text,
    org,
    text_color,
    box_color=DEBUG_BOX_COLOR,
    border_color=DEBUG_BOX_BORDER_COLOR,
    font_scale=DEBUG_FONT_SCALE,
    thickness=DEBUG_FONT_THICKNESS,
    padding_x=4,
    padding_y=3,
):
    font = cv2.FONT_HERSHEY_SIMPLEX
    (tw, th), baseline = cv2.getTextSize(text, font, font_scale, thickness)

    x, y = org
    x1 = x - padding_x
    y1 = y - th - padding_y
    x2 = x + tw + padding_x
    y2 = y + baseline + padding_y

    h, w = image.shape[:2]
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(w - 1, x2)
    y2 = min(h - 1, y2)

    cv2.rectangle(image, (x1, y1), (x2, y2), box_color, -1)
    cv2.rectangle(image, (x1, y1), (x2, y2), border_color, 1)

    cv2.putText(
        image,
        text,
        (x, y),
        font,
        font_scale,
        text_color,
        thickness,
        cv2.LINE_AA,
    )

def is_opamp_aux_terminal(term: dict) -> bool:
    name = str(term.get("name") or "").lower()
    terminal_id = str(term.get("terminal_id") or "").lower()

    return (
        name in {"aux1", "aux2"}
        or terminal_id.endswith(":aux1")
        or terminal_id.endswith(":aux2")
    )


def get_max_ok_distance(term: dict) -> float:
    if is_opamp_aux_terminal(term):
        return OPAMP_AUX_MAX_OK_DISTANCE
    return MAX_OK_DISTANCE


def is_preferred_like_match_status(match_status: str) -> bool:
    return match_status in {"matched_preferred", "matched_implicit_supply"}


def get_preferred_match_status(preferred_is_implicit_supply: bool) -> str:
    if preferred_is_implicit_supply:
        return "matched_implicit_supply"
    return "matched_preferred"


def run_opamp_aux_vertical_stage(label_map: np.ndarray, term: dict, preferred_net_index=None):
    """
    Matcher dedicato per aux1/aux2:
    cerca in una capsula verticale e privilegia la net che:
    - va nella direzione outward (top/bottom)
    - resta vicina alla x del terminale
    - ha un minimo di supporto in pixel
    """
    if not is_opamp_aux_terminal(term):
        return None

    rel = term.get("relative_position")
    if rel not in {"top", "bottom"}:
        return None

    h, w = label_map.shape[:2]
    x = int(round(term["x"]))
    y = int(round(term["y"]))

    if rel == "top":
        rect = clamp_window(
            x - OPAMP_AUX_VERTICAL_X_TOL,
            y - OPAMP_AUX_VERTICAL_OUTWARD,
            x + OPAMP_AUX_VERTICAL_X_TOL + 1,
            y + OPAMP_AUX_VERTICAL_INWARD + 1,
            w, h
        )
    else:
        rect = clamp_window(
            x - OPAMP_AUX_VERTICAL_X_TOL,
            y - OPAMP_AUX_VERTICAL_INWARD,
            x + OPAMP_AUX_VERTICAL_X_TOL + 1,
            y + OPAMP_AUX_VERTICAL_OUTWARD + 1,
            w, h
        )

    candidate_labels = collect_labels_in_rect(label_map, rect)
    if not candidate_labels:
        return {
            "candidate_labels": [],
            "chosen_label": None,
            "distance": None,
            "snap_point": None,
            "decision_mode": None,
            "search_window": rect,
        }

    x1, y1, x2, y2 = rect
    roi = label_map[y1:y2, x1:x2]

    best = None
    for lbl in candidate_labels:
        ys, xs = np.where(roi == lbl)
        if len(xs) < OPAMP_AUX_VERTICAL_MIN_PIXELS:
            continue

        xs_global = xs + x1
        ys_global = ys + y1

        if rel == "top":
            outward_progress = y - ys_global
        else:
            outward_progress = ys_global - y

        valid = np.where(outward_progress >= -1)[0]
        if len(valid) == 0:
            continue

        x_penalty = np.abs(xs_global - x)
        scores = outward_progress - OPAMP_AUX_VERTICAL_X_PENALTY * x_penalty

        if preferred_net_index is not None and int(lbl) == int(preferred_net_index):
            scores = scores + OPAMP_AUX_PREFERRED_BONUS

        local_valid = valid[int(np.argmax(scores[valid]))]
        px = int(xs_global[local_valid])
        py = int(ys_global[local_valid])
        dist = float(np.sqrt((px - x) ** 2 + (py - y) ** 2))

        label_score = float(scores[local_valid] + OPAMP_AUX_VERTICAL_COUNT_WEIGHT * len(valid))

        cand = {
            "label": int(lbl),
            "distance": dist,
            "snap_point": [px, py],
            "label_score": label_score,
            "decision_mode": "preferred_label" if preferred_net_index is not None and int(lbl) == int(preferred_net_index) else "aux_vertical_corridor",
        }

        if best is None or cand["label_score"] > best["label_score"]:
            best = cand

    if best is None:
        return {
            "candidate_labels": candidate_labels,
            "chosen_label": None,
            "distance": None,
            "snap_point": None,
            "decision_mode": None,
            "search_window": rect,
        }

    return {
        "candidate_labels": candidate_labels,
        "chosen_label": best["label"],
        "distance": best["distance"],
        "snap_point": best["snap_point"],
        "decision_mode": best["decision_mode"],
        "search_window": rect,
    }

def get_class_search_params(term: dict):
    params = {
        "directional_outward": BASE_DIRECTIONAL_OUTWARD,
        "directional_inward": BASE_DIRECTIONAL_INWARD,
        "directional_halfspan": BASE_DIRECTIONAL_HALFSPAN,
        "circle_radius": BASE_CIRCLE_RADIUS,
        "fallback_radius": BASE_FALLBACK_RADIUS,
    }
    params.update(CLASS_SEARCH_OVERRIDES.get(term.get("component_class_name"), {}))
    return params

# ---------------------------------------------------------
# search geometry / search plan
# ---------------------------------------------------------
def build_directional_rect(term: dict, shape, outward: int, inward: int, halfspan: int):
    h, w = shape[:2]
    x = int(round(term["x"]))
    y = int(round(term["y"]))
    rel = term.get("relative_position")

    if rel == "left":
        return clamp_window(
            x - outward, y - halfspan,
            x + inward + 1, y + halfspan + 1,
            w, h
        )

    if rel == "right":
        return clamp_window(
            x - inward, y - halfspan,
            x + outward + 1, y + halfspan + 1,
            w, h
        )

    if rel == "top":
        return clamp_window(
            x - halfspan, y - outward,
            x + halfspan + 1, y + inward + 1,
            w, h
        )

    if rel == "bottom":
        return clamp_window(
            x - halfspan, y - inward,
            x + halfspan + 1, y + outward + 1,
            w, h
        )

    return clamp_window(
        x - outward, y - outward,
        x + outward + 1, y + outward + 1,
        w, h
    )

def collect_labels_in_rect(label_map: np.ndarray, rect):
    x1, y1, x2, y2 = rect
    roi = label_map[y1:y2, x1:x2]
    labels = np.unique(roi)
    labels = [int(v) for v in labels if int(v) > 0]
    return labels

def collect_labels_in_circle(label_map: np.ndarray, x: int, y: int, radius: int):
    h, w = label_map.shape[:2]
    x1 = max(0, x - radius)
    y1 = max(0, y - radius)
    x2 = min(w, x + radius + 1)
    y2 = min(h, y + radius + 1)

    roi = label_map[y1:y2, x1:x2]
    yy, xx = np.ogrid[y1:y2, x1:x2]
    mask = (xx - x) ** 2 + (yy - y) ** 2 <= radius ** 2

    vals = roi[mask]
    labels = np.unique(vals)
    labels = [int(v) for v in labels if int(v) > 0]
    return labels, [x1, y1, x2, y2]

def build_search_plan(term: dict):
    params = get_class_search_params(term)
    directional_outward = int(params["directional_outward"])
    directional_inward = int(params["directional_inward"])
    directional_halfspan = int(params["directional_halfspan"])
    circle_radius = int(params["circle_radius"])
    fallback_radius = int(params["fallback_radius"])

    return [
        {
            "name": "directional_primary",
            "kind": "directional",
            "outward": directional_outward,
            "inward": directional_inward,
            "halfspan": directional_halfspan,
        },
        {
            "name": "circle_primary",
            "kind": "circle",
            "radius": circle_radius,
        },
        {
            "name": "directional_fallback",
            "kind": "directional",
            "outward": max(directional_outward + 8, fallback_radius),
            "inward": directional_inward + 2,
            "halfspan": directional_halfspan + 3,
        },
        {
            "name": "circle_fallback",
            "kind": "circle",
            "radius": fallback_radius,
        },
    ]

# ---------------------------------------------------------
# snap / label choice
# ---------------------------------------------------------
def nearest_label_by_pixel_distance(label_map: np.ndarray, x: int, y: int, candidate_labels, rect=None, radius=None):
    if rect is not None:
        x1, y1, x2, y2 = rect
    else:
        h, w = label_map.shape[:2]
        x1 = max(0, x - radius)
        y1 = max(0, y - radius)
        x2 = min(w, x + radius + 1)
        y2 = min(h, y + radius + 1)

    roi = label_map[y1:y2, x1:x2]

    best_label = None
    best_distance = None
    best_point = None

    for lbl in candidate_labels:
        ys, xs = np.where(roi == lbl)
        if len(xs) == 0:
            continue

        xs_global = xs + x1
        ys_global = ys + y1
        d2 = (xs_global - x) ** 2 + (ys_global - y) ** 2
        idx = int(np.argmin(d2))
        dist = float(np.sqrt(d2[idx]))

        if best_distance is None or dist < best_distance:
            best_distance = dist
            best_label = int(lbl)
            best_point = [int(xs_global[idx]), int(ys_global[idx])]

    return best_label, best_distance, best_point

def choose_best_label(label_map: np.ndarray, x: int, y: int, candidate_labels, preferred_label=None, rect=None, radius=None):
    if not candidate_labels:
        return None, None, None, None

    candidate_labels = sorted(set(int(v) for v in candidate_labels if int(v) > 0))

    if preferred_label is not None and preferred_label in candidate_labels:
        chosen_lbl, dist, point = nearest_label_by_pixel_distance(
            label_map, x, y, [preferred_label], rect=rect, radius=radius
        )
        return chosen_lbl, dist, point, "preferred_label"

    if len(candidate_labels) == 1:
        chosen_lbl, dist, point = nearest_label_by_pixel_distance(
            label_map, x, y, candidate_labels, rect=rect, radius=radius
        )
        return chosen_lbl, dist, point, "single_candidate"

    chosen_lbl, dist, point = nearest_label_by_pixel_distance(
        label_map, x, y, candidate_labels, rect=rect, radius=radius
    )
    return chosen_lbl, dist, point, "nearest_candidate"

def run_search_stage(label_map: np.ndarray, term: dict, stage: dict, preferred_net_index=None):
    x = int(round(term["x"]))
    y = int(round(term["y"]))

    if stage["kind"] == "directional":
        rect = build_directional_rect(
            term,
            label_map.shape,
            outward=stage["outward"],
            inward=stage["inward"],
            halfspan=stage["halfspan"],
        )
        candidate_labels = collect_labels_in_rect(label_map, rect)
        chosen_lbl, dist, point, decision = choose_best_label(
            label_map,
            x,
            y,
            candidate_labels,
            preferred_label=preferred_net_index,
            rect=rect,
        )
        search_window = [int(v) for v in rect]
    elif stage["kind"] == "circle":
        candidate_labels, search_window = collect_labels_in_circle(
            label_map,
            x,
            y,
            radius=stage["radius"],
        )
        chosen_lbl, dist, point, decision = choose_best_label(
            label_map,
            x,
            y,
            candidate_labels,
            preferred_label=preferred_net_index,
            radius=stage["radius"],
        )
    else:
        raise ValueError(f"Stage non supportato: {stage['kind']}")

    return {
        "candidate_labels": candidate_labels,
        "chosen_label": chosen_lbl,
        "distance": dist,
        "snap_point": point,
        "decision_mode": decision,
        "search_window": search_window,
    }


# ---------------------------------------------------------
# Confidence / warning del match
# ---------------------------------------------------------
def classify_match_confidence(
    term: dict,
    match_status: str,
    distance_px,
    search_stage: str,
    preferred_net_index,
):
    if match_status == "unmatched":
        return "unmatched", ["unmatched_terminal"]

    warnings = []
    distance = None if distance_px is None else float(distance_px)
    max_ok_distance = get_max_ok_distance(term)

    if (
        is_opamp_aux_terminal(term)
        and preferred_net_index is not None
        and is_preferred_like_match_status(match_status)
    ):
        max_ok_distance = max(max_ok_distance, OPAMP_AUX_MAX_PREFERRED_DISTANCE)

    if distance is None or distance > max_ok_distance:
        return "unmatched", ["distance_too_large"]

    if preferred_net_index is None:
        warnings.append("no_preferred_net_from_05")
    if not is_preferred_like_match_status(match_status):
        warnings.append("matched_without_preferred_label")
    if search_stage in {"directional_fallback", "circle_fallback"}:
        warnings.append("used_fallback_search")
    if search_stage == "circle_primary":
        warnings.append("used_circle_search")
    if search_stage == "opamp_aux_vertical":
        warnings.append("used_opamp_aux_vertical_search")

    return "ok", warnings


def finalize_match_result(term: dict, result: dict):
    confidence, warnings = classify_match_confidence(
        term=term,
        match_status=result["match_status"],
        distance_px=result["match_distance_px"],
        search_stage=result["search_stage"],
        preferred_net_index=result["preferred_net_index_from_05"],
    )
    result["match_confidence"] = confidence
    result["match_warnings"] = warnings

    result["is_suspicious_match"] = confidence != "ok"
    if confidence != "ok":
        result["matched_net_id"] = None
        result["matched_net_index"] = None
        result["matched_net_is_implicit_supply"] = False
        result["matched_net_implicit_reason"] = None
        result["match_status"] = "unmatched"
        result["snap_point"] = None
    return result

# ---------------------------------------------------------
# Matching terminal -> net
# ---------------------------------------------------------
def get_preferred_net_index(term: dict, source_label_to_net_index: dict, net_building_terminal_debug: dict):
    term_id = term["terminal_id"]
    debug = net_building_terminal_debug.get(term_id, {})
    source_label = debug.get("primary_label")
    if source_label is None:
        return None
    return source_label_to_net_index.get(int(source_label))


def run_preferred_from_05_window_stage(
    label_map: np.ndarray,
    term: dict,
    preferred_net_index,
    net_building_terminal_debug: dict,
):
    if preferred_net_index is None or not is_opamp_aux_terminal(term):
        return None

    term_id = term["terminal_id"]
    debug = net_building_terminal_debug.get(term_id, {})
    search_window = debug.get("search_window")
    if not search_window or len(search_window) != 4:
        return None

    rect = tuple(int(v) for v in search_window)
    x = int(round(term["x"]))
    y = int(round(term["y"]))

    chosen_lbl, dist, point = nearest_label_by_pixel_distance(
        label_map,
        x,
        y,
        [preferred_net_index],
        rect=rect,
    )
    if chosen_lbl is None:
        return None

    return {
        "candidate_labels": [int(preferred_net_index)],
        "chosen_label": int(chosen_lbl),
        "distance": dist,
        "snap_point": point,
        "decision_mode": "preferred_label",
        "search_window": [int(v) for v in rect],
    }


def match_terminal_to_net(term: dict, label_map: np.ndarray, net_index_map: dict, source_label_to_net_index: dict, net_building_terminal_debug: dict):
    preferred_net_index = get_preferred_net_index(term, source_label_to_net_index, net_building_terminal_debug)
    term_debug = net_building_terminal_debug.get(term["terminal_id"], {})
    preferred_net = net_index_map.get(preferred_net_index, {}) if preferred_net_index is not None else {}
    preferred_is_implicit_supply = bool(
        term_debug.get("is_implicit_supply", False)
        or preferred_net.get("is_implicit_supply", False)
    )
    preferred_implicit_reason = (
        term_debug.get("implicit_reason")
        or preferred_net.get("implicit_reason")
    )

    result = {
        "terminal_id": term["terminal_id"],
        "instance_id": term["instance_id"],
        "component_class_name": term.get("component_class_name"),
        "relative_position": term.get("relative_position"),
        "x": term["x"],
        "y": term["y"],
        "preferred_net_index_from_05": preferred_net_index,
        "preferred_net_id_from_05": net_index_map.get(preferred_net_index, {}).get("net_id") if preferred_net_index is not None else None,
        "preferred_from_05_is_implicit_supply": preferred_is_implicit_supply,
        "preferred_from_05_implicit_reason": preferred_implicit_reason,
        "candidate_net_ids": [],
        "candidate_net_indices": [],
        "matched_net_id": None,
        "matched_net_index": None,
        "matched_net_is_implicit_supply": False,
        "matched_net_implicit_reason": None,
        "match_status": "unmatched",
        "match_distance_px": None,
        "snap_point": None,
        "search_stage": None,
        "search_window": None,
        "search_kind": None,
        "match_confidence": "none",
        "match_warnings": ["unmatched_terminal"],
        "is_suspicious_match": True,
    }

    preferred_window_stage = run_preferred_from_05_window_stage(
        label_map,
        term,
        preferred_net_index,
        net_building_terminal_debug,
    )
    if preferred_window_stage is not None:
        result["candidate_net_indices"] = [int(preferred_net_index)]
        result["candidate_net_ids"] = [
            net_index_map[int(preferred_net_index)]["net_id"]
        ]
        result["matched_net_index"] = int(preferred_window_stage["chosen_label"])
        result["matched_net_id"] = net_index_map[int(preferred_window_stage["chosen_label"])]["net_id"]
        result["matched_net_is_implicit_supply"] = bool(
            net_index_map[int(preferred_window_stage["chosen_label"])].get("is_implicit_supply", False)
        )
        result["matched_net_implicit_reason"] = (
            net_index_map[int(preferred_window_stage["chosen_label"])].get("implicit_reason")
            if result["matched_net_is_implicit_supply"]
            else None
        )
        result["match_status"] = get_preferred_match_status(preferred_is_implicit_supply)
        result["match_distance_px"] = round(float(preferred_window_stage["distance"]), 3)
        result["snap_point"] = preferred_window_stage["snap_point"]
        result["search_stage"] = "preferred_from_05_window"
        result["search_window"] = preferred_window_stage["search_window"]
        result["search_kind"] = "directional"
        return finalize_match_result(term, result)

    aux_stage = run_opamp_aux_vertical_stage(
        label_map,
        term,
        preferred_net_index=preferred_net_index,
    )
        
    result["aux_stage_debug"] = aux_stage

    if aux_stage is not None:
        candidate_labels = aux_stage["candidate_labels"]
        if candidate_labels:
            result["candidate_net_indices"] = sorted(set(int(v) for v in candidate_labels))
            result["candidate_net_ids"] = [
                net_index_map[idx]["net_id"]
                for idx in result["candidate_net_indices"]
                if idx in net_index_map
            ]
            result["search_stage"] = "opamp_aux_vertical"
            result["search_window"] = aux_stage["search_window"]
            result["search_kind"] = "directional"

            chosen_idx = aux_stage["chosen_label"]
            if chosen_idx is not None:
                result["matched_net_index"] = int(chosen_idx)
                result["matched_net_id"] = net_index_map[int(chosen_idx)]["net_id"]
                result["matched_net_is_implicit_supply"] = bool(
                    net_index_map[int(chosen_idx)].get("is_implicit_supply", False)
                )
                result["matched_net_implicit_reason"] = (
                    net_index_map[int(chosen_idx)].get("implicit_reason")
                    if result["matched_net_is_implicit_supply"]
                    else None
                )
                result["match_distance_px"] = round(float(aux_stage["distance"]), 3)
                result["snap_point"] = aux_stage["snap_point"]

                if aux_stage["decision_mode"] == "preferred_label":
                    result["match_status"] = get_preferred_match_status(preferred_is_implicit_supply)
                else:
                    result["match_status"] = "matched_nearest"

                return finalize_match_result(term, result)

    for stage in build_search_plan(term):
        stage_result = run_search_stage(label_map, term, stage, preferred_net_index=preferred_net_index)
        candidate_labels = stage_result["candidate_labels"]

        if candidate_labels:
            result["candidate_net_indices"] = sorted(set(int(v) for v in candidate_labels))
            result["candidate_net_ids"] = [
                net_index_map[idx]["net_id"]
                for idx in result["candidate_net_indices"]
                if idx in net_index_map
            ]
            result["search_stage"] = stage["name"]
            result["search_window"] = stage_result["search_window"]
            result["search_kind"] = stage["kind"]

            chosen_idx = stage_result["chosen_label"]
            if chosen_idx is None:
                continue

            result["matched_net_index"] = int(chosen_idx)
            result["matched_net_id"] = net_index_map[int(chosen_idx)]["net_id"]
            result["matched_net_is_implicit_supply"] = bool(
                net_index_map[int(chosen_idx)].get("is_implicit_supply", False)
            )
            result["matched_net_implicit_reason"] = (
                net_index_map[int(chosen_idx)].get("implicit_reason")
                if result["matched_net_is_implicit_supply"]
                else None
            )
            result["match_distance_px"] = None if stage_result["distance"] is None else round(float(stage_result["distance"]), 3)
            result["snap_point"] = stage_result["snap_point"]

            decision_mode = stage_result["decision_mode"]
            if decision_mode == "preferred_label":
                result["match_status"] = get_preferred_match_status(preferred_is_implicit_supply)
            elif decision_mode == "single_candidate":
                result["match_status"] = "matched_single"
            else:
                result["match_status"] = "matched_nearest"

            return finalize_match_result(term, result)

    return finalize_match_result(term, result)


def apply_match_info_to_terminal(term: dict, match_info: dict):
    term_copy = dict(term)

    term_copy["candidate_net_ids"] = match_info.get("candidate_net_ids", [])
    term_copy["candidate_net_indices"] = match_info.get("candidate_net_indices", [])
    term_copy["preferred_net_index_from_05"] = match_info.get("preferred_net_index_from_05")
    term_copy["preferred_net_id_from_05"] = match_info.get("preferred_net_id_from_05")
    term_copy["preferred_from_05_is_implicit_supply"] = match_info.get("preferred_from_05_is_implicit_supply", False)
    term_copy["preferred_from_05_implicit_reason"] = match_info.get("preferred_from_05_implicit_reason")
    term_copy["matched_net_id"] = match_info.get("matched_net_id")
    term_copy["matched_net_index"] = match_info.get("matched_net_index")
    term_copy["matched_net_is_implicit_supply"] = match_info.get("matched_net_is_implicit_supply", False)
    term_copy["matched_net_implicit_reason"] = match_info.get("matched_net_implicit_reason")
    term_copy["match_status"] = match_info.get("match_status", "unmatched")
    term_copy["match_distance_px"] = match_info.get("match_distance_px")
    term_copy["snap_point"] = match_info.get("snap_point")
    term_copy["search_stage"] = match_info.get("search_stage")
    term_copy["search_window"] = match_info.get("search_window")
    term_copy["search_kind"] = match_info.get("search_kind")
    term_copy["match_confidence"] = match_info.get("match_confidence", "none")
    term_copy["match_warnings"] = match_info.get("match_warnings", [])
    term_copy["is_suspicious_match"] = match_info.get("is_suspicious_match", False)

    return term_copy

# ---------------------------------------------------------
# Update strutture output
# ---------------------------------------------------------
def update_components_with_terminal_matches(components, terminal_match_map):
    updated_components = []

    for comp in components:
        comp_copy = dict(comp)
        updated_terminals = []

        for term in comp.get("terminals", []):
            match_info = terminal_match_map.get(term["terminal_id"], {})
            term_copy = apply_match_info_to_terminal(term, match_info)
            updated_terminals.append(term_copy)

        comp_copy["terminals"] = updated_terminals
        updated_components.append(comp_copy)

    return updated_components

def build_connections(terminals_with_matches):
    connections = []
    for term in terminals_with_matches:
        if term.get("matched_net_id") is None:
            continue

        connections.append({
            "terminal_id": term["terminal_id"],
            "display_terminal_id": term.get("display_terminal_id", term["terminal_id"]),
            "display_name": term.get("display_name", term.get("name")),
            "semantic_terminal_name": term.get("semantic_terminal_name"),
            "semantic_terminal_id": term.get("semantic_terminal_id"),
            "semantic_slot": term.get("semantic_slot"),
            "semantic_confidence": term.get("semantic_confidence"),
            "semantic_evidence_type": term.get("semantic_evidence_type"),
            "semantic_resolution_mode": term.get("semantic_resolution_mode"),
            "semantic_role_family": term.get("semantic_role_family"),
            "semantic_polarity": term.get("semantic_polarity"),
            "semantic_direction": term.get("semantic_direction"),
            "instance_id": term["instance_id"],
            "component_class_name": term.get("component_class_name"),
            "net_id": term["matched_net_id"],
            "net_index": term["matched_net_index"],
            "net_is_implicit_supply": term.get("matched_net_is_implicit_supply", False),
            "net_implicit_reason": term.get("matched_net_implicit_reason"),
            "match_status": term["match_status"],
            "match_distance_px": term["match_distance_px"],
            "snap_point": term.get("snap_point"),
            "match_confidence": term.get("match_confidence"),
            "match_warnings": term.get("match_warnings", []),
            "is_suspicious_match": term.get("is_suspicious_match", False),
        })
    return connections

# ---------------------------------------------------------
# Debug images
# ---------------------------------------------------------
def get_debug_color(term: dict):
    if term.get("matched_net_id") is None:
        return DEBUG_POINT_COLOR_NONE
    if term.get("match_confidence") == "ok":
        return DEBUG_POINT_COLOR_OK
    return DEBUG_POINT_COLOR_SUSPICIOUS

def get_debug_text_color(term: dict):
    if term.get("matched_net_id") is None:
        return DEBUG_TEXT_COLOR_NONE
    if term.get("match_confidence") == "ok":
        return DEBUG_TEXT_COLOR_OK
    return DEBUG_TEXT_COLOR_SUSPICIOUS

def draw_debug_overlay(image_bgr, terminals_with_matches):
    out = image_bgr.copy()

    for term in terminals_with_matches:
        x = int(round(term["x"]))
        y = int(round(term["y"]))
        display_term_id = term.get("display_terminal_id", term["terminal_id"])
        matched_net_id = term.get("matched_net_id")
        confidence = term.get("match_confidence", "none")
        snap_point = term.get("snap_point")

        point_color = get_debug_color(term)
        text_color = get_debug_text_color(term)

        if matched_net_id is None:
            label = f"{display_term_id}: none"
        else:
            label = f"{display_term_id}->{matched_net_id} [{confidence}]"

        # punto terminale
        cv2.circle(out, (x, y), DEBUG_TERMINAL_RADIUS, point_color, -1)
        cv2.circle(out, (x, y), DEBUG_TERMINAL_RADIUS + 1, (255, 255, 255), 1)

        # snap point + linea
        if snap_point is not None:
            sx, sy = int(snap_point[0]), int(snap_point[1])
            cv2.circle(out, (sx, sy), DEBUG_SNAP_RADIUS, DEBUG_SNAP_POINT_COLOR, -1)
            cv2.circle(out, (sx, sy), DEBUG_SNAP_RADIUS + 1, (255, 255, 255), 1)
            cv2.line(out, (x, y), (sx, sy), point_color, DEBUG_LINE_THICKNESS, cv2.LINE_AA)

        # testo con box
        draw_boxed_text(
            out,
            label,
            (x + 8, max(y - 8, 18)),
            text_color=text_color,
        )

    return out

# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
def main() -> None:
    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"Cartella input non trovata: {INPUT_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DEBUG_DIR.mkdir(parents=True, exist_ok=True)

    json_files = sorted(INPUT_DIR.glob("*.json"))
    if not json_files:
        raise FileNotFoundError(f"Nessun file JSON trovato in: {INPUT_DIR}")

    print(f"Input directory : {INPUT_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"File trovati    : {len(json_files)}\n")

    for i, json_path in enumerate(json_files, start=1):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        image_path = Path(data["image_path"])
        image_bgr = cv2.imread(str(image_path))
        if image_bgr is None:
            print(f"Attenzione: immagine non leggibile -> {image_path}")
            continue

        nets = data.get("nets", [])
        net_building = data.get("net_building", {})
        label_map_path = Path(net_building["label_map_path"])
        label_map = load_label_map(label_map_path)

        net_index_map = build_net_index_map(nets)
        source_label_to_net_index = build_source_label_to_net_index_map(nets)
        net_building_terminal_debug = net_building.get("terminal_to_candidate_labels", {})
        terminals = data.get("terminals", [])

        terminals_with_matches = []
        terminal_match_map = {}

        for term in terminals:
            match_info = match_terminal_to_net(
                term,
                label_map,
                net_index_map,
                source_label_to_net_index,
                net_building_terminal_debug,
            )

            term_copy = apply_match_info_to_terminal(term, match_info)

            terminals_with_matches.append(term_copy)
            terminal_match_map[term["terminal_id"]] = match_info

        updated_components = update_components_with_terminal_matches(
            data.get("components", []),
            terminal_match_map,
        )

        connections = build_connections(terminals_with_matches)
        n_matched = sum(1 for t in terminals_with_matches if t.get("matched_net_id") is not None)
        n_unmatched = len(terminals_with_matches) - n_matched
        confidence_counts = {
            "ok": sum(1 for t in terminals_with_matches if t.get("match_confidence") == "ok"),
            "unmatched": sum(1 for t in terminals_with_matches if t.get("match_confidence") == "unmatched"),
        }
        suspicious_terminal_ids = [
            t["terminal_id"]
            for t in terminals_with_matches
            if t.get("is_suspicious_match", False)
        ]
        suspicious_terminal_display_ids = [
            t.get("display_terminal_id", t["terminal_id"])
            for t in terminals_with_matches
            if t.get("is_suspicious_match", False)
        ]

        output_data = dict(data)
        output_data["components"] = updated_components
        output_data["terminals"] = terminals_with_matches
        output_data["connections"] = connections
        output_data["n_connections"] = len(connections)
        output_data["terminal_net_matching"] = {
            "notes": "Matching con esito finale ok/unmatched. Prima usa la net preferita del 05, poi ricerca direzionale e fallback circolari.",
            "n_ok_matches": confidence_counts["ok"],
            "n_unmatched_matches": confidence_counts["unmatched"],
            "base_directional_outward": BASE_DIRECTIONAL_OUTWARD,
            "base_directional_inward": BASE_DIRECTIONAL_INWARD,
            "base_directional_halfspan": BASE_DIRECTIONAL_HALFSPAN,
            "base_circle_radius": BASE_CIRCLE_RADIUS,
            "base_fallback_radius": BASE_FALLBACK_RADIUS,
            "class_search_overrides": CLASS_SEARCH_OVERRIDES,
            "n_terminals": len(terminals_with_matches),
            "n_matched_terminals": n_matched,
            "n_unmatched_terminals": n_unmatched,
            "n_suspicious_matches": len(suspicious_terminal_ids),
            "suspicious_terminal_ids": suspicious_terminal_ids,
            "suspicious_terminal_display_ids": suspicious_terminal_display_ids,
        }

        if SAVE_DEBUG_IMAGES:
            debug_img = draw_debug_overlay(image_bgr, terminals_with_matches)
            debug_path = DEBUG_DIR / f"{json_path.stem}_terminal_net_matches.jpg"
            cv2.imwrite(str(debug_path), debug_img)
            output_data["terminal_net_matching"]["debug_image_path"] = str(debug_path)

        out_json_path = OUTPUT_DIR / json_path.name
        with open(out_json_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(
            f"[{i}/{len(json_files)}] {json_path.name} -> "
            f"matched={n_matched}, unmatched={n_unmatched}, "
        )

    print("\nCompletato.")
    print(f"Risultati salvati in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
