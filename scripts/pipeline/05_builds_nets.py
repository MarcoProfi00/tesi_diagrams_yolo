"""
05_builds_nets.py

Scopo:
    Costruire le net candidate a partire dallo skeleton del passo 04.

Pipeline:
    1. connected components dello skeleton
    2. matching locale terminale -> label candidata
    3. costruzione candidate nets
    4. filtraggio candidate
    5. rilabeling delle net mantenute
    6. salvataggio label map e debug images
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

PIPELINE_DATASET = os.environ.get(
    "PIPELINE_DATASET",
    "topology_v9.2_set_successivo",
)

INPUT_DIR = PROJECT_ROOT / "outputs" / PIPELINE_DATASET / "04_extract_wires"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / PIPELINE_DATASET / "05_build_nets"

# =========================================================
# TERMINAL -> LABEL MATCHING
# =========================================================
LABEL_MAP_DIR = OUTPUT_DIR / "label_maps"
NET_MAP_DIR = OUTPUT_DIR / "net_map"
OVERLAY_DIR = OUTPUT_DIR / "overlay"
TERMINAL_DEBUG_DIR = OUTPUT_DIR / "terminal_debug"

# Terminale -> componente connessa sullo skeleton
TERMINAL_SEARCH_OUTWARD = 16
TERMINAL_SEARCH_INWARD = 4

#Terminal Matching Params
TERMINAL_DIRECTIONAL_HALFSPAN = 5
TERMINAL_SQUARE_FALLBACK_RADIUS = 12

MIN_SINGLE_TERMINAL_NET_PIXELS = 20
MIN_SINGLE_TERMINAL_NET_SPAN = 12

OPAMP_AUX_SEARCH_OUTWARD = 240
OPAMP_AUX_SEARCH_INWARD = 20
OPAMP_AUX_HALFSPAN = 60
OPAMP_AUX_MIN_REACH = 6
OPAMP_AUX_AREA_WEIGHT = 0.12
OPAMP_AUX_REACH_WEIGHT = 3.0
OPAMP_AUX_XGAP_WEIGHT = 1.2
OPAMP_AUX_WRONG_SIDE_WEIGHT = 0.20
OPAMP_AUX_IMPLICIT_MAX_SNAP_DISTANCE = 12.0
OPAMP_AUX_IMPLICIT_MAX_XGAP = 8
OPAMP_AUX_IMPLICIT_MIN_EXTENSION_REACH = 45
OPAMP_AUX_IMPLICIT_MAX_CHAIN_GAP = 80

# =========================================================
# NET FILTERING
# =========================================================
MIN_NET_PIXELS = 8
MIN_CONNECTED_TERMINALS = 1

# =========================================================
# NET SORTING / VISUALIZATION
# =========================================================
# Ordinamento net:
# "xy" = da sinistra a destra, poi dall'alto verso il basso
# "yx" = dall'alto verso il basso, poi da sinistra a destra
NET_SORT_ORDER = "xy"

SAVE_DEBUG_IMAGES = True

# Palette più leggibile sia su sfondo nero sia su overlay chiaro.
# Formato OpenCV = BGR
NET_COLORS = [
    (0, 0, 255),      # rosso
    (255, 0, 0),      # blu
    (0, 180, 0),      # verde scuro
    (0, 200, 255),    # arancione/giallo caldo
    (255, 0, 255),    # magenta
    (255, 255, 0),    # ciano
    (180, 0, 255),    # viola
    (0, 128, 255),    # arancio
    (255, 255, 255),  # bianco
    (0, 255, 128),    # verde acqua
]

OVERLAY_ALPHA = 0.55

NET_LABEL_FONT_SCALE = 0.75
NET_LABEL_THICKNESS = 2
NET_LABEL_OUTLINE_THICKNESS = 4
NET_LABEL_TEXT_COLOR = (120, 40, 0)         # blu/marrone scuro leggibile su sfondo chiaro
NET_LABEL_BOX_COLOR = (210, 255, 255)       # giallo chiaro (BGR)
NET_LABEL_BOX_BORDER_COLOR = (80, 120, 120) # bordo soft
NET_LABEL_PADDING_X = 4
NET_LABEL_PADDING_Y = 3

TERMINAL_POINT_COLOR = (0, 0, 255)      # rosso
TERMINAL_POINT_RADIUS = 5
SNAP_POINT_COLOR = (255, 0, 0)          # blu
SNAP_POINT_RADIUS = 4
TERMINAL_LINK_COLOR = (255, 0, 255)     # magenta
TERMINAL_TEXT_COLOR = (0, 255, 255)     # giallo
TERMINAL_TEXT_OUTLINE = (0, 0, 0)       # nero
TERMINAL_TEXT_SCALE = 0.45
TERMINAL_TEXT_THICKNESS = 1
TERMINAL_TEXT_OUTLINE_THICKNESS = 3

# utility base
# Load binary image image.
def load_binary_image(path: Path):
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Immagine non trovata o non leggibile: {path}")

    binary = np.where(img > 0, 255, 0).astype(np.uint8)
    return binary


# Get sort key.
def get_sort_key(item, sort_order="xy"):
    x1, y1, x2, y2 = item["bbox"]
    xc = (x1 + x2) / 2.0
    yc = (y1 + y2) / 2.0

    if sort_order == "yx":
        return (yc, xc)
    return (xc, yc)

# Clamp window.
def clamp_window(x1, y1, x2, y2, w, h):
    return (
        max(0, min(w, x1)),
        max(0, min(h, y1)),
        max(0, min(w, x2)),
        max(0, min(h, y2)),
    )

# Get bounding box span.
def get_bbox_span(bbox):
    x1, y1, x2, y2 = bbox
    width = x2 - x1 + 1
    height = y2 - y1 + 1
    return max(width, height)

# Draw outlined text.
def draw_outlined_text(
    image,
    text,
    org,
    color,
    outline_color=(0, 0, 0),
    font_scale=0.6,
    thickness=1,
    outline_thickness=3,
):
    cv2.putText(
        image,
        text,
        org,
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        outline_color,
        outline_thickness,
        cv2.LINE_AA,
    )
    cv2.putText(
        image,
        text,
        org,
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        color,
        thickness,
        cv2.LINE_AA,
    )

# Draw boxed text.
def draw_boxed_text(
    image,
    text,
    org,
    text_color=(120, 40, 0),
    box_color=(210, 255, 255),
    border_color=(80, 120, 120),
    font_scale=0.75,
    thickness=2,
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

# connected components + terminal matching
# Find connected components.
def find_connected_components(skeleton_binary: np.ndarray):
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        skeleton_binary, connectivity=8
    )
    return num_labels, labels, stats, centroids

# Get directional window.
def get_directional_window(term: dict, labels_shape, outward=16, inward=4, halfspan=5):
    h, w = labels_shape[:2]
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

# Get square window.
def get_square_window(term: dict, labels_shape, radius=12):
    h, w = labels_shape[:2]
    x = int(round(term["x"]))
    y = int(round(term["y"]))
    return clamp_window(x - radius, y - radius, x + radius + 1, y + radius + 1, w, h)

# Collect labels in window.
def collect_labels_in_window(labels: np.ndarray, window):
    x1, y1, x2, y2 = window
    roi = labels[y1:y2, x1:x2]
    unique_labels = np.unique(roi)
    return [int(v) for v in unique_labels if int(v) > 0]

# Find nearest labeled pixel.
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

# Handle is op-amp aux terminal.
def is_opamp_aux_terminal(term: dict) -> bool:
    return (
        int(term.get("component_class_id", -1)) == 19 and
        str(term.get("name", "")).lower() in {"aux1", "aux2"}
    )


# Get label bounding box and area.
def get_label_bbox_and_area(stats: np.ndarray, lbl: int):
    row = stats[int(lbl)]
    x = int(row[cv2.CC_STAT_LEFT])
    y = int(row[cv2.CC_STAT_TOP])
    w = int(row[cv2.CC_STAT_WIDTH])
    h = int(row[cv2.CC_STAT_HEIGHT])
    area = int(row[cv2.CC_STAT_AREA])
    return x, y, x + w - 1, y + h - 1, area


# Handle axis gap 1d.
def axis_gap_1d(v: int, a: int, b: int) -> int:
    if v < a:
        return a - v
    if v > b:
        return v - b
    return 0


# Find nearest pixel for specific label.
def find_nearest_pixel_for_specific_label(labels: np.ndarray, term: dict, window, target_label: int):
    x1, y1, x2, y2 = window
    roi = labels[y1:y2, x1:x2]
    ys, xs = np.where(roi == int(target_label))
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

    return {
        "label": int(target_label),
        "snap_point": [px, py],
        "snap_distance": round(float(np.sqrt(d2[best_idx])), 3),
    }


# Score op-amp aux label.
def score_opamp_aux_label(term: dict, stats: np.ndarray, lbl: int):
    tx = int(round(term["x"]))
    ty = int(round(term["y"]))
    name = str(term.get("name", "")).lower()

    x1, y1, x2, y2, area = get_label_bbox_and_area(stats, lbl)
    xgap = axis_gap_1d(tx, x1, x2)

    if name == "aux1":
        reach = ty - y1
        wrong_side = max(0, y2 - ty)
    else:  # aux2
        reach = y2 - ty
        wrong_side = max(0, ty - y1)

    if reach < OPAMP_AUX_MIN_REACH:
        return None

    # Il punteggio cresce se la componente si sviluppa davvero nella direzione
    # attesa del supply e resta allineata con la x del terminale.
    score = (
        OPAMP_AUX_REACH_WEIGHT * float(reach) +
        OPAMP_AUX_AREA_WEIGHT * float(min(area, 300)) -
        OPAMP_AUX_XGAP_WEIGHT * float(xgap) -
        OPAMP_AUX_WRONG_SIDE_WEIGHT * float(wrong_side)
    )

    return {
        "label": int(lbl),
        "score": round(score, 3),
        "reach": int(reach),
        "wrong_side": int(wrong_side),
        "xgap": int(xgap),
        "bbox": [x1, y1, x2, y2],
        "area": int(area),
    }


# Build op-amp aux implicit supply match.
def build_opamp_aux_implicit_supply_match(
    labels: np.ndarray,
    term: dict,
    window,
    scored,
):
    if not scored:
        return None

    name = str(term.get("name", "")).lower()
    if name not in {"aux1", "aux2"}:
        return None

    scored_by_label = {int(info["label"]): dict(info) for info in scored}
    with_snap = []

    for info in scored:
        nearest = find_nearest_pixel_for_specific_label(
            labels,
            term,
            window,
            info["label"],
        )
        if nearest is None:
            continue

        info_copy = dict(info)
        info_copy["snap_point"] = nearest["snap_point"]
        info_copy["snap_distance"] = float(nearest["snap_distance"])
        with_snap.append(info_copy)

    if not with_snap:
        return None

    # Prima scegliamo un frammento molto vicino al pin come ancora locale.
    anchor_candidates = [
        info for info in with_snap
        if float(info["snap_distance"]) <= OPAMP_AUX_IMPLICIT_MAX_SNAP_DISTANCE
    ]
    if not anchor_candidates:
        return None

    anchor_candidates.sort(
        key=lambda info: (
            float(info["snap_distance"]),
            -float(info["score"]),
        )
    )
    anchor = anchor_candidates[0]

    if name == "aux1":
        extension_candidates = [
            info for info in scored
            if int(info["label"]) != int(anchor["label"])
            and int(info["xgap"]) <= OPAMP_AUX_IMPLICIT_MAX_XGAP
            and int(info["wrong_side"]) == 0
            and int(info["reach"]) >= OPAMP_AUX_IMPLICIT_MIN_EXTENSION_REACH
            and int(info["bbox"][3]) < int(anchor["bbox"][1])
        ]
        extension_candidates.sort(key=lambda info: int(info["bbox"][3]), reverse=True)
        chain_edge = int(anchor["bbox"][1])
    else:
        extension_candidates = [
            info for info in scored
            if int(info["label"]) != int(anchor["label"])
            and int(info["xgap"]) <= OPAMP_AUX_IMPLICIT_MAX_XGAP
            and int(info["wrong_side"]) == 0
            and int(info["reach"]) >= OPAMP_AUX_IMPLICIT_MIN_EXTENSION_REACH
            and int(info["bbox"][1]) > int(anchor["bbox"][3])
        ]
        extension_candidates.sort(key=lambda info: int(info["bbox"][1]))
        chain_edge = int(anchor["bbox"][3])

    merged_labels = [int(anchor["label"])]

    # Poi estendiamo la net implicita solo con segmenti coerenti lungo la stessa
    # direzione, cosi evitiamo di fondere componenti scollegate ma vicine.
    for info in extension_candidates:
        if name == "aux1":
            gap = int(chain_edge) - int(info["bbox"][3])
        else:
            gap = int(info["bbox"][1]) - int(chain_edge)

        if gap < 0 or gap > OPAMP_AUX_IMPLICIT_MAX_CHAIN_GAP:
            continue

        merged_labels.append(int(info["label"]))
        if name == "aux1":
            chain_edge = int(info["bbox"][1])
        else:
            chain_edge = int(info["bbox"][3])

    if len(merged_labels) <= 1:
        return None

    return {
        "primary_label": int(anchor["label"]),
        "candidate_labels": sorted(set(int(info["label"]) for info in scored)),
        "preferred_candidate_labels": [],
        "search_window": [int(v) for v in window],
        "snap_point": [int(v) for v in anchor["snap_point"]],
        "snap_distance": round(float(anchor["snap_distance"]), 3),
        "match_mode": "opamp_aux_implicit_supply_orphan",
        "aux_score_debug": [
            dict(scored_by_label[int(lbl)])
            for lbl in merged_labels
            if int(lbl) in scored_by_label
        ],
        "is_implicit_supply": True,
        "implicit_reason": "missing_terminal_symbol",
        "implicit_supply_anchor_label": int(anchor["label"]),
        "implicit_supply_source_labels": merged_labels,
    }


# Match op-amp aux terminal.
def match_opamp_aux_terminal(
    labels: np.ndarray,
    stats: np.ndarray,
    term: dict,
    preferred_labels=None,
    require_preferred_label=False,
):
    tx = int(round(term["x"]))
    ty = int(round(term["y"]))
    name = str(term.get("name", "")).lower()
    preferred_labels = {int(v) for v in (preferred_labels or [])}

    if name == "aux1":
        window = clamp_window(
            tx - OPAMP_AUX_HALFSPAN,
            ty - OPAMP_AUX_SEARCH_OUTWARD,
            tx + OPAMP_AUX_HALFSPAN + 1,
            ty + OPAMP_AUX_SEARCH_INWARD + 1,
            labels.shape[1],
            labels.shape[0],
        )
    else:  # aux2
        window = clamp_window(
            tx - OPAMP_AUX_HALFSPAN,
            ty - OPAMP_AUX_SEARCH_INWARD,
            tx + OPAMP_AUX_HALFSPAN + 1,
            ty + OPAMP_AUX_SEARCH_OUTWARD + 1,
            labels.shape[1],
            labels.shape[0],
        )

    candidate_labels = collect_labels_in_window(labels, window)
    if not candidate_labels:
        return {
            "primary_label": None,
            "candidate_labels": [],
            "preferred_candidate_labels": [],
            "search_window": [int(v) for v in window],
            "snap_point": None,
            "snap_distance": None,
            "match_mode": "opamp_aux_no_candidates",
            "aux_score_debug": [],
            "is_implicit_supply": False,
        }

    preferred_candidate_labels = [
        int(lbl) for lbl in candidate_labels
        if int(lbl) in preferred_labels
    ]

    scored = []
    for lbl in candidate_labels:
        info = score_opamp_aux_label(term, stats, lbl)
        if info is not None:
            scored.append(info)

    if require_preferred_label and not preferred_candidate_labels:
        implicit_match = build_opamp_aux_implicit_supply_match(
            labels,
            term,
            window,
            scored,
        )
        if implicit_match is not None:
            return implicit_match

        return {
            "primary_label": None,
            "candidate_labels": candidate_labels,
            "preferred_candidate_labels": [],
            "search_window": [int(v) for v in window],
            "snap_point": None,
            "snap_distance": None,
            "match_mode": "opamp_aux_missing_non_aux_anchor",
            "aux_score_debug": scored[:5],
            "is_implicit_supply": False,
        }

    scored_to_use = scored
    if preferred_candidate_labels:
        scored_to_use = [
            info for info in scored
            if int(info["label"]) in preferred_candidate_labels
        ]

    # ramo "normale": abbiamo candidati validi
    if scored_to_use:
        scored_to_use.sort(key=lambda x: x["score"], reverse=True)
        best = scored_to_use[0]

        nearest = find_nearest_pixel_for_specific_label(labels, term, window, best["label"])
        if nearest is None:
            return {
                "primary_label": None,
                "candidate_labels": candidate_labels,
                "preferred_candidate_labels": preferred_candidate_labels,
                "search_window": [int(v) for v in window],
                "snap_point": None,
                "snap_distance": None,
                "match_mode": "opamp_aux_missing_snap_point",
                "aux_score_debug": scored_to_use[:5],
                "is_implicit_supply": False,
            }

        return {
            "primary_label": int(best["label"]),
            "candidate_labels": candidate_labels,
            "preferred_candidate_labels": preferred_candidate_labels,
            "search_window": [int(v) for v in window],
            "snap_point": nearest["snap_point"],
            "snap_distance": nearest["snap_distance"],
            "match_mode": (
                "opamp_aux_preferred_non_aux_label"
                if preferred_candidate_labels
                else "opamp_aux_special"
            ),
            "aux_score_debug": scored_to_use[:5],
            "is_implicit_supply": False,
        }

    # fallback rilassato
    relaxed = []
    for lbl in candidate_labels:
        x1, y1, x2, y2, area = get_label_bbox_and_area(stats, lbl)
        xgap = axis_gap_1d(tx, x1, x2)

        if name == "aux1":
            reach = max(0, ty - y1)
            wrong_side = max(0, y2 - ty)
        else:
            reach = max(0, y2 - ty)
            wrong_side = max(0, ty - y1)

        score = (
            2.0 * float(reach) +
            0.08 * float(min(area, 300)) -
            1.2 * float(xgap) -
            0.15 * float(wrong_side)
        )

        relaxed.append({
            "label": int(lbl),
            "score": round(score, 3),
            "reach": int(reach),
            "wrong_side": int(wrong_side),
            "xgap": int(xgap),
            "bbox": [x1, y1, x2, y2],
            "area": int(area),
        })

    relaxed_to_use = relaxed
    if preferred_candidate_labels:
        relaxed_to_use = [
            info for info in relaxed
            if int(info["label"]) in preferred_candidate_labels
        ]

    if not relaxed_to_use:
        return {
            "primary_label": None,
            "candidate_labels": candidate_labels,
            "preferred_candidate_labels": preferred_candidate_labels,
            "search_window": [int(v) for v in window],
            "snap_point": None,
            "snap_distance": None,
            "match_mode": "opamp_aux_no_valid_candidate",
            "aux_score_debug": relaxed[:5],
            "is_implicit_supply": False,
        }

    relaxed_to_use.sort(key=lambda x: x["score"], reverse=True)
    best = relaxed_to_use[0]

    nearest = find_nearest_pixel_for_specific_label(labels, term, window, best["label"])
    if nearest is None:
        return {
            "primary_label": None,
            "candidate_labels": candidate_labels,
            "preferred_candidate_labels": preferred_candidate_labels,
            "search_window": [int(v) for v in window],
            "snap_point": None,
            "snap_distance": None,
            "match_mode": "opamp_aux_missing_snap_point",
            "aux_score_debug": relaxed_to_use[:5],
            "is_implicit_supply": False,
        }

    return {
        "primary_label": int(best["label"]),
        "candidate_labels": candidate_labels,
        "preferred_candidate_labels": preferred_candidate_labels,
        "search_window": [int(v) for v in window],
        "snap_point": nearest["snap_point"],
        "snap_distance": nearest["snap_distance"],
        "match_mode": (
            "opamp_aux_preferred_non_aux_label_relaxed"
            if preferred_candidate_labels
            else "opamp_aux_special_relaxed"
        ),
        "aux_score_debug": relaxed_to_use[:5],
        "is_implicit_supply": False,
    }

# Match standard terminal.
def match_standard_terminal(labels: np.ndarray, term: dict, radius=12, directional_halfspan=5):
    dir_window = get_directional_window(
        term,
        labels.shape,
        outward=TERMINAL_SEARCH_OUTWARD,
        inward=TERMINAL_SEARCH_INWARD,
        halfspan=directional_halfspan,
    )
    dir_labels = collect_labels_in_window(labels, dir_window)
    nearest = find_nearest_labeled_pixel(labels, term, dir_window)
    match_mode = "directional"

    if nearest is None:
        sq_window = get_square_window(term, labels.shape, radius=radius)
        sq_labels = collect_labels_in_window(labels, sq_window)
        nearest = find_nearest_labeled_pixel(labels, term, sq_window)
        match_mode = "square_fallback"
        candidate_labels = sq_labels
        used_window = sq_window
    else:
        candidate_labels = dir_labels
        used_window = dir_window

    primary_label = None
    snap_point = None
    snap_distance = None

    if nearest is not None:
        primary_label = int(nearest["label"])
        snap_point = nearest["snap_point"]
        snap_distance = nearest["snap_distance"]

    return {
        "candidate_labels": candidate_labels,
        "primary_label": primary_label,
        "match_mode": match_mode,
        "search_window": [int(v) for v in used_window],
        "snap_point": snap_point,
        "snap_distance": snap_distance,
        "relative_position": term.get("relative_position"),
    }


# Match op-amp aux via neighbor terminal.
def match_opamp_aux_via_neighbor_terminal(term: dict, terminal_debug_by_id: dict):
    point_debug = term.get("terminal_point_debug", {}) or {}
    if not point_debug.get("snapped_to_nearby_terminal", False):
        return None

    neighbor_terminal_id = point_debug.get("neighbor_terminal_id")
    if not neighbor_terminal_id:
        return None

    neighbor_debug = terminal_debug_by_id.get(neighbor_terminal_id)
    if not neighbor_debug:
        return None

    primary_label = neighbor_debug.get("primary_label")
    candidate_labels = neighbor_debug.get("candidate_labels", [])
    preferred_candidate_labels = (
        [int(primary_label)] if primary_label is not None else []
    )

    return {
        "primary_label": int(primary_label) if primary_label is not None else None,
        "candidate_labels": candidate_labels,
        "preferred_candidate_labels": preferred_candidate_labels,
        "search_window": neighbor_debug.get("search_window"),
        "snap_point": neighbor_debug.get("snap_point"),
        "snap_distance": neighbor_debug.get("snap_distance"),
        "match_mode": "opamp_aux_inherit_neighbor_terminal",
        "aux_score_debug": [],
        "neighbor_terminal_id": neighbor_terminal_id,
        "is_implicit_supply": False,
    }


# Terminal to candidate labels.
def terminal_to_candidate_labels(labels: np.ndarray, stats: np.ndarray, terminals, radius=12, directional_halfspan=5):
    primary_label_to_terminal_ids = {}
    terminal_debug_by_id = {}
    implicit_aux_merges = {}

    non_aux_terms = [term for term in terminals if not is_opamp_aux_terminal(term)]
    aux_terms = [term for term in terminals if is_opamp_aux_terminal(term)]

    for term in non_aux_terms:
        term_id = term["terminal_id"]
        match_info = match_standard_terminal(
            labels,
            term,
            radius=radius,
            directional_halfspan=directional_halfspan,
        )

        primary_label = match_info["primary_label"]
        if primary_label is not None:
            primary_label_to_terminal_ids.setdefault(primary_label, set()).add(term_id)

        terminal_debug_by_id[term_id] = match_info

    # Gli auxiliary dell'opamp devono preferire label già ancorate a terminali reali.
    # Se nel loro corridoio c'è solo uno stelo "orfano", meglio lasciarli unmatched
    # che creare una net artificiale.
    preferred_aux_labels = set(int(lbl) for lbl in primary_label_to_terminal_ids.keys())

    for term in aux_terms:
        term_id = term["terminal_id"]
        inherited_match = match_opamp_aux_via_neighbor_terminal(
            term,
            terminal_debug_by_id,
        )

        if inherited_match is not None:
            primary_label = inherited_match["primary_label"]
            if primary_label is not None:
                primary_label_to_terminal_ids.setdefault(primary_label, set()).add(term_id)

            terminal_debug_by_id[term_id] = {
                "candidate_labels": inherited_match["candidate_labels"],
                "preferred_candidate_labels": inherited_match.get("preferred_candidate_labels", []),
                "primary_label": primary_label,
                "display_terminal_id": term.get("display_terminal_id", term_id),
                "semantic_terminal_name": term.get("semantic_terminal_name"),
                "semantic_terminal_id": term.get("semantic_terminal_id"),
                "match_mode": inherited_match["match_mode"],
                "search_window": inherited_match["search_window"],
                "snap_point": inherited_match["snap_point"],
                "snap_distance": inherited_match["snap_distance"],
                "relative_position": term.get("relative_position"),
                "aux_score_debug": inherited_match.get("aux_score_debug", []),
                "neighbor_terminal_id": inherited_match.get("neighbor_terminal_id"),
                "is_implicit_supply": bool(inherited_match.get("is_implicit_supply", False)),
            }
            continue

        aux_match = match_opamp_aux_terminal(
            labels,
            stats,
            term,
            preferred_labels=preferred_aux_labels,
            require_preferred_label=True,
        )

        primary_label = aux_match["primary_label"]
        if primary_label is not None:
            primary_label_to_terminal_ids.setdefault(primary_label, set()).add(term_id)

        if aux_match.get("is_implicit_supply") and primary_label is not None:
            merged_labels = [
                int(lbl)
                for lbl in aux_match.get("implicit_supply_source_labels", [])
            ]
            implicit_aux_merges[int(primary_label)] = {
                "source_label": int(primary_label),
                "merged_source_labels": merged_labels or [int(primary_label)],
                "anchor_terminal_id": term_id,
                "implicit_reason": aux_match.get("implicit_reason", "missing_terminal_symbol"),
            }

        terminal_debug_by_id[term_id] = {
            "candidate_labels": aux_match["candidate_labels"],
            "preferred_candidate_labels": aux_match.get("preferred_candidate_labels", []),
            "primary_label": primary_label,
            "display_terminal_id": term.get("display_terminal_id", term_id),
            "semantic_terminal_name": term.get("semantic_terminal_name"),
            "semantic_terminal_id": term.get("semantic_terminal_id"),
            "match_mode": aux_match["match_mode"],
            "search_window": aux_match["search_window"],
            "snap_point": aux_match["snap_point"],
            "snap_distance": aux_match["snap_distance"],
            "relative_position": term.get("relative_position"),
            "aux_score_debug": aux_match.get("aux_score_debug", []),
            "is_implicit_supply": bool(aux_match.get("is_implicit_supply", False)),
            "implicit_reason": aux_match.get("implicit_reason"),
            "implicit_supply_anchor_label": aux_match.get("implicit_supply_anchor_label"),
            "implicit_supply_source_labels": aux_match.get("implicit_supply_source_labels", []),
        }

    terminal_debug = {
        term["terminal_id"]: terminal_debug_by_id[term["terminal_id"]]
        for term in terminals
    }

    return primary_label_to_terminal_ids, terminal_debug, implicit_aux_merges


# Build terminal index.
def build_terminal_index(terminals):
    return {term["terminal_id"]: term for term in terminals}


# Summarize connected terminals.
def summarize_connected_terminals(connected_terminal_ids, terminal_index):
    connected_terminal_names = []
    connected_terminal_display_ids = []
    connected_semantic_terminal_names = []
    auxiliary_terminal_ids = []

    for term_id in connected_terminal_ids:
        term = terminal_index.get(term_id, {})
        name = str(term.get("name", "")).lower()
        connected_terminal_names.append(name)
        connected_terminal_display_ids.append(term.get("display_terminal_id", term_id))

        semantic_name = term.get("semantic_terminal_name")
        if semantic_name:
            connected_semantic_terminal_names.append(semantic_name)

        if name in {"aux1", "aux2"}:
            auxiliary_terminal_ids.append(term_id)

    return {
        "connected_terminal_names": connected_terminal_names,
        "connected_terminal_display_ids": connected_terminal_display_ids,
        "connected_semantic_terminal_names": connected_semantic_terminal_names,
        "auxiliary_terminal_ids": auxiliary_terminal_ids,
        "n_auxiliary_terminals": len(auxiliary_terminal_ids),
        "all_connected_terminals_are_auxiliary": (
            len(connected_terminal_ids) > 0 and
            len(auxiliary_terminal_ids) == len(connected_terminal_ids)
        ),
    }

# candidate nets
# Build candidate nets.
def build_candidate_nets(stats, label_to_terminal_ids, terminal_index, implicit_aux_merges=None):
    raw_candidates = []

    for lbl, stat_row in enumerate(stats[1:], start=1):  # salto background
        x = int(stat_row[cv2.CC_STAT_LEFT])
        y = int(stat_row[cv2.CC_STAT_TOP])
        w = int(stat_row[cv2.CC_STAT_WIDTH])
        h = int(stat_row[cv2.CC_STAT_HEIGHT])
        area = int(stat_row[cv2.CC_STAT_AREA])

        connected_terminal_ids = sorted(label_to_terminal_ids.get(lbl, set()))
        bbox = [x, y, x + w - 1, y + h - 1]
        terminal_summary = summarize_connected_terminals(connected_terminal_ids, terminal_index)

        raw_candidates.append({
            "source_label": lbl,
            "pixel_count": area,
            "bbox": bbox,
            "connected_terminal_ids": connected_terminal_ids,
            "connected_terminal_display_ids": terminal_summary["connected_terminal_display_ids"],
            "n_connected_terminals": len(connected_terminal_ids),
            "connected_terminal_names": terminal_summary["connected_terminal_names"],
            "connected_semantic_terminal_names": terminal_summary["connected_semantic_terminal_names"],
            "auxiliary_terminal_ids": terminal_summary["auxiliary_terminal_ids"],
            "n_auxiliary_terminals": terminal_summary["n_auxiliary_terminals"],
            "all_connected_terminals_are_auxiliary": terminal_summary["all_connected_terminals_are_auxiliary"],
        })

    if not implicit_aux_merges:
        return raw_candidates

    raw_by_label = {int(cand["source_label"]): cand for cand in raw_candidates}
    merged_related_labels = set()
    merged_by_anchor = {}

    for anchor_label, merge_info in implicit_aux_merges.items():
        anchor_label = int(anchor_label)
        anchor_cand = raw_by_label.get(anchor_label)
        if anchor_cand is None:
            continue

        merged_labels = []
        merged_connected_terminal_ids = set(anchor_cand.get("connected_terminal_ids", []))
        pixel_count = int(anchor_cand["pixel_count"])
        x1, y1, x2, y2 = anchor_cand["bbox"]

        # Quando il supply e implicito, piu source_label spezzate possono
        # rappresentare una sola net logica e vanno aggregate qui.
        for lbl in merge_info.get("merged_source_labels", [anchor_label]):
            lbl = int(lbl)
            cand = raw_by_label.get(lbl)
            if cand is None:
                continue

            merged_labels.append(lbl)
            if lbl == anchor_label:
                continue

            merged_related_labels.add(lbl)
            pixel_count += int(cand["pixel_count"])
            cx1, cy1, cx2, cy2 = cand["bbox"]
            x1 = min(x1, cx1)
            y1 = min(y1, cy1)
            x2 = max(x2, cx2)
            y2 = max(y2, cy2)
            merged_connected_terminal_ids.update(cand.get("connected_terminal_ids", []))

        terminal_ids = sorted(merged_connected_terminal_ids)
        terminal_summary = summarize_connected_terminals(terminal_ids, terminal_index)

        merged_cand = dict(anchor_cand)
        merged_cand["pixel_count"] = pixel_count
        merged_cand["bbox"] = [x1, y1, x2, y2]
        merged_cand["merged_source_labels"] = merged_labels or [anchor_label]
        merged_cand["connected_terminal_ids"] = terminal_ids
        merged_cand["connected_terminal_display_ids"] = terminal_summary["connected_terminal_display_ids"]
        merged_cand["n_connected_terminals"] = len(terminal_ids)
        merged_cand["connected_terminal_names"] = terminal_summary["connected_terminal_names"]
        merged_cand["connected_semantic_terminal_names"] = terminal_summary["connected_semantic_terminal_names"]
        merged_cand["auxiliary_terminal_ids"] = terminal_summary["auxiliary_terminal_ids"]
        merged_cand["n_auxiliary_terminals"] = terminal_summary["n_auxiliary_terminals"]
        merged_cand["all_connected_terminals_are_auxiliary"] = terminal_summary["all_connected_terminals_are_auxiliary"]
        merged_cand["is_implicit_supply"] = True
        merged_cand["implicit_reason"] = merge_info.get("implicit_reason", "missing_terminal_symbol")
        merged_cand["implicit_anchor_terminal_id"] = merge_info.get("anchor_terminal_id")
        merged_by_anchor[anchor_label] = merged_cand

    if not merged_by_anchor:
        return raw_candidates

    final_candidates = []
    for cand in raw_candidates:
        lbl = int(cand["source_label"])
        if lbl in merged_related_labels:
            continue
        if lbl in merged_by_anchor:
            final_candidates.append(merged_by_anchor[lbl])
        else:
            final_candidates.append(cand)

    return final_candidates

# Filter candidate nets.
def filter_candidate_nets(candidates):
    kept = []
    rejected = []

    for cand in candidates:
        keep = True
        reject_reasons = []

        if cand["pixel_count"] < MIN_NET_PIXELS:
            keep = False
            reject_reasons.append("too_few_pixels")

        if cand["n_connected_terminals"] < MIN_CONNECTED_TERMINALS:
            keep = False
            reject_reasons.append("no_connected_terminals")

        # Filtro aggiuntivo:
        # se la net tocca un solo terminale, deve avere un minimo di consistenza.
        # Eccezione: se quel terminale è un auxiliary dell'opamp (aux1/aux2),
        # non applichiamo il filtro single-terminal "forte" perché la linea di
        # alimentazione può essere corta ma comunque valida.
        is_single_aux_net = (
            cand["n_connected_terminals"] == 1 and
            cand.get("all_connected_terminals_are_auxiliary", False)
        )

        if cand["n_connected_terminals"] == 1 and not is_single_aux_net:
            if cand["pixel_count"] < MIN_SINGLE_TERMINAL_NET_PIXELS:
                keep = False
                reject_reasons.append("weak_single_terminal_net")

            if get_bbox_span(cand["bbox"]) < MIN_SINGLE_TERMINAL_NET_SPAN:
                keep = False
                reject_reasons.append("single_terminal_net_too_short")

        cand_copy = dict(cand)
        cand_copy["reject_reasons"] = reject_reasons

        if keep:
            kept.append(cand_copy)
        else:
            rejected.append(cand_copy)

    return kept, rejected

# Relabel kept nets.
def relabel_kept_nets(original_labels: np.ndarray, kept_candidates, sort_order="xy"):
    kept_sorted = sorted(kept_candidates, key=lambda x: get_sort_key(x, sort_order=sort_order))

    relabeled = np.zeros_like(original_labels, dtype=np.int32)
    nets = []

    for idx, cand in enumerate(kept_sorted, start=1):
        source_labels = [
            int(v)
            for v in cand.get("merged_source_labels", [cand["source_label"]])
        ]

        # Se una net finale nasce dalla fusione di piu frammenti dello skeleton,
        # tutte le source_label originali ricevono lo stesso net_index finale.
        for old_label in source_labels:
            relabeled[original_labels == old_label] = idx

        net = {
            "net_id": f"N{idx}",
            "net_index": idx,
            "source_label": int(cand["source_label"]),
            "merged_source_labels": source_labels,
            "pixel_count": cand["pixel_count"],
            "bbox": cand["bbox"],
            "connected_terminal_ids": cand["connected_terminal_ids"],
            "connected_terminal_display_ids": cand.get("connected_terminal_display_ids", cand["connected_terminal_ids"]),
            "connected_terminal_names": cand.get("connected_terminal_names", []),
            "connected_semantic_terminal_names": cand.get("connected_semantic_terminal_names", []),
            "auxiliary_terminal_ids": cand.get("auxiliary_terminal_ids", []),
            "n_auxiliary_terminals": cand.get("n_auxiliary_terminals", 0),
            "all_connected_terminals_are_auxiliary": cand.get("all_connected_terminals_are_auxiliary", False),
            "n_connected_terminals": cand["n_connected_terminals"],
            "is_implicit_supply": bool(cand.get("is_implicit_supply", False)),
            "implicit_reason": cand.get("implicit_reason"),
            "implicit_anchor_terminal_id": cand.get("implicit_anchor_terminal_id"),
        }
        nets.append(net)

    return relabeled, nets

# debug / visualization
# Draw net map.
def draw_net_map(relabeled_map: np.ndarray, nets):
    h, w = relabeled_map.shape
    canvas = np.zeros((h, w, 3), dtype=np.uint8)

    for net in nets:
        idx = net["net_index"]
        color = NET_COLORS[(idx - 1) % len(NET_COLORS)]
        canvas[relabeled_map == idx] = color

        x1, y1, x2, y2 = net["bbox"]
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)

        draw_boxed_text(
            canvas,
            net["net_id"],
            (cx, cy),
            text_color=NET_LABEL_TEXT_COLOR,
            box_color=NET_LABEL_BOX_COLOR,
            border_color=NET_LABEL_BOX_BORDER_COLOR,
            font_scale=NET_LABEL_FONT_SCALE,
            thickness=NET_LABEL_THICKNESS,
            padding_x=NET_LABEL_PADDING_X,
            padding_y=NET_LABEL_PADDING_Y,
        )
    return canvas


# Draw overlay.
def draw_overlay(image_bgr, relabeled_map: np.ndarray, nets):
    overlay = image_bgr.copy()

    for net in nets:
        idx = net["net_index"]
        color = NET_COLORS[(idx - 1) % len(NET_COLORS)]

        mask = relabeled_map == idx
        overlay[mask] = color

    blended = cv2.addWeighted(image_bgr, 1.0 - OVERLAY_ALPHA, overlay, OVERLAY_ALPHA, 0)

    for net in nets:
        x1, y1, x2, y2 = net["bbox"]
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)

        draw_boxed_text(
            blended,
            net["net_id"],
            (cx, cy),
            text_color=NET_LABEL_TEXT_COLOR,
            box_color=NET_LABEL_BOX_COLOR,
            border_color=NET_LABEL_BOX_BORDER_COLOR,
            font_scale=NET_LABEL_FONT_SCALE,
            thickness=NET_LABEL_THICKNESS,
            padding_x=NET_LABEL_PADDING_X,
            padding_y=NET_LABEL_PADDING_Y,
        )

    return blended


# Draw terminal debug view.
def draw_terminal_debug(image_bgr, terminals, terminal_debug, relabeled_map, nets):
    out = image_bgr.copy()
    index_to_net_id = {net["net_index"]: net["net_id"] for net in nets}

    for term in terminals:
        term_id = term["terminal_id"]
        display_term_id = term.get("display_terminal_id", term_id)
        info = terminal_debug.get(term_id, {})

        tx = int(round(term["x"]))
        ty = int(round(term["y"]))

        cv2.circle(out, (tx, ty), TERMINAL_POINT_RADIUS, TERMINAL_POINT_COLOR, -1)
        cv2.circle(out, (tx, ty), TERMINAL_POINT_RADIUS + 1, (0, 0, 0), 1)

        snap_point = info.get("snap_point")
        primary_label = info.get("primary_label")

        if snap_point is None or primary_label is None:
            draw_outlined_text(
                out,
                f"{display_term_id}: none",
                (tx + 8, max(16, ty - 8)),
                color=(0, 0, 255),
                outline_color=(255, 255, 255),
                font_scale=TERMINAL_TEXT_SCALE,
                thickness=TERMINAL_TEXT_THICKNESS,
                outline_thickness=TERMINAL_TEXT_OUTLINE_THICKNESS,
            )
            continue

        sx, sy = map(int, snap_point)
        cv2.circle(out, (sx, sy), SNAP_POINT_RADIUS, SNAP_POINT_COLOR, -1)
        cv2.circle(out, (sx, sy), SNAP_POINT_RADIUS + 1, (255, 255, 255), 1)
        cv2.line(out, (tx, ty), (sx, sy), TERMINAL_LINK_COLOR, 2)

        net_idx = int(relabeled_map[sy, sx]) if 0 <= sy < relabeled_map.shape[0] and 0 <= sx < relabeled_map.shape[1] else 0
        net_id = index_to_net_id.get(net_idx, f"src{primary_label}")

        draw_outlined_text(
            out,
            f"{display_term_id}->{net_id}",
            (tx + 8, max(16, ty - 8)),
            color=TERMINAL_TEXT_COLOR,
            outline_color=TERMINAL_TEXT_OUTLINE,
            font_scale=TERMINAL_TEXT_SCALE,
            thickness=TERMINAL_TEXT_THICKNESS,
            outline_thickness=TERMINAL_TEXT_OUTLINE_THICKNESS,
        )

    return out

# main
# Run the entrypoint for this pipeline stage.
def main() -> None:
    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"Cartella input non trovata: {INPUT_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LABEL_MAP_DIR.mkdir(parents=True, exist_ok=True)
    NET_MAP_DIR.mkdir(parents=True, exist_ok=True)
    OVERLAY_DIR.mkdir(parents=True, exist_ok=True)
    TERMINAL_DEBUG_DIR.mkdir(parents=True, exist_ok=True)

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

        wire_extraction = data.get("wire_extraction", {})
        skeleton_path = Path(wire_extraction["skeleton_path"])

        skeleton_binary = load_binary_image(skeleton_path)
        terminals = data.get("terminals", [])
        terminal_index = build_terminal_index(terminals)

        num_labels, labels, stats, _ = find_connected_components(skeleton_binary)

        label_to_terminal_ids, terminal_to_labels, implicit_aux_merges = terminal_to_candidate_labels(
            labels,
            stats,
            terminals,
            radius=TERMINAL_SQUARE_FALLBACK_RADIUS,
            directional_halfspan=TERMINAL_DIRECTIONAL_HALFSPAN,
        )

        candidates = build_candidate_nets(
            stats,
            label_to_terminal_ids,
            terminal_index,
            implicit_aux_merges=implicit_aux_merges,
        )
        kept_candidates, rejected_candidates = filter_candidate_nets(candidates)

        relabeled_map, nets = relabel_kept_nets(
            labels,
            kept_candidates,
            sort_order=NET_SORT_ORDER,
        )

        stem = json_path.stem

        label_map_path = LABEL_MAP_DIR / f"{stem}_net_labels.npy"
        np.save(label_map_path, relabeled_map)

        output_data = dict(data)
        output_data["nets"] = nets
        output_data["n_nets"] = len(nets)
        output_data["net_building"] = {
            "terminal_search_outward": TERMINAL_SEARCH_OUTWARD,
            "terminal_search_inward": TERMINAL_SEARCH_INWARD,
            "terminal_square_fallback_radius": TERMINAL_SQUARE_FALLBACK_RADIUS,
            "terminal_directional_halfspan": TERMINAL_DIRECTIONAL_HALFSPAN,
            "min_net_pixels": MIN_NET_PIXELS,
            "min_connected_terminals": MIN_CONNECTED_TERMINALS,
            "net_sort_order": NET_SORT_ORDER,
            "n_connected_components_total": max(0, int(num_labels) - 1),
            "n_candidate_components": len(candidates),
            "n_kept_nets": len(kept_candidates),
            "n_rejected_components": len(rejected_candidates),
            "n_terminals": len(terminals),
            "n_terminals_with_primary_label": sum(1 for v in terminal_to_labels.values() if v.get("primary_label") is not None),
            "n_terminals_unmatched": sum(1 for v in terminal_to_labels.values() if v.get("primary_label") is None),
            "n_implicit_supply_matches": sum(1 for v in terminal_to_labels.values() if v.get("is_implicit_supply")),
            "label_map_path": str(label_map_path),
            "terminal_to_candidate_labels": terminal_to_labels,
            "implicit_aux_merges": list(implicit_aux_merges.values()),
            "rejected_candidates": rejected_candidates,
        }

        if SAVE_DEBUG_IMAGES:
            net_map = draw_net_map(relabeled_map, nets)
            overlay = draw_overlay(image_bgr, relabeled_map, nets)
            terminal_debug_img = draw_terminal_debug(image_bgr, terminals, terminal_to_labels, relabeled_map, nets)

            net_map_path = NET_MAP_DIR / f"{stem}_net_map.png"
            overlay_path = OVERLAY_DIR / f"{stem}_net_overlay.jpg"
            terminal_debug_path = TERMINAL_DEBUG_DIR / f"{stem}_terminal_debug.jpg"

            cv2.imwrite(str(net_map_path), net_map)
            cv2.imwrite(str(overlay_path), overlay)
            cv2.imwrite(str(terminal_debug_path), terminal_debug_img)

            output_data["net_building"]["net_map_path"] = str(net_map_path)
            output_data["net_building"]["overlay_path"] = str(overlay_path)
            output_data["net_building"]["terminal_debug_path"] = str(terminal_debug_path)

        out_json_path = OUTPUT_DIR / json_path.name
        with open(out_json_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(
            f"[{i}/{len(json_files)}] {json_path.name} -> "
            f"cc_total={max(0, int(num_labels) - 1)}, candidate={len(candidates)}, "
            f"nets={len(nets)}, rejected={len(rejected_candidates)}"
        )

    print("\nCompletato.")
    print(f"Risultati salvati in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
