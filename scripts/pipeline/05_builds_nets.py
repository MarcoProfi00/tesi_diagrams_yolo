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
import json
import cv2
import numpy as np

# =========================================================
# PATHS / INPUT-OUTPUT
# =========================================================
PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_DIR = PROJECT_ROOT / "outputs" / "topology_v6_opamp" / "04_extract_wires"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "topology_v6_opamp" / "05_build_nets"

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

# Terminali auxiliary opamp: il punto del 03 è vicino al giunto interno,
# ma il wire utile può stare più lontano lungo lo stelo verticale.
OPAMP_AUX_SEARCH_OUTWARD = 40
OPAMP_AUX_SEARCH_INWARD = 10
OPAMP_AUX_DIRECTIONAL_HALFSPAN = 8
OPAMP_AUX_SQUARE_FALLBACK_RADIUS = 24
OPAMP_AUX_MATCH_OUTWARD = 46
OPAMP_AUX_MATCH_INWARD = 6
OPAMP_AUX_MATCH_X_TOL = 5
OPAMP_AUX_MATCH_MIN_PIXELS = 2
OPAMP_AUX_MATCH_X_PENALTY = 1.6
OPAMP_AUX_MATCH_COUNT_WEIGHT = 0.35

# utility base
def load_binary_image(path: Path):
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Immagine non trovata o non leggibile: {path}")

    binary = np.where(img > 0, 255, 0).astype(np.uint8)
    return binary


def get_sort_key(item, sort_order="xy"):
    x1, y1, x2, y2 = item["bbox"]
    xc = (x1 + x2) / 2.0
    yc = (y1 + y2) / 2.0

    if sort_order == "yx":
        return (yc, xc)
    return (xc, yc)

def clamp_window(x1, y1, x2, y2, w, h):
    return (
        max(0, min(w, x1)),
        max(0, min(h, y1)),
        max(0, min(w, x2)),
        max(0, min(h, y2)),
    )

def get_bbox_span(bbox):
    x1, y1, x2, y2 = bbox
    width = x2 - x1 + 1
    height = y2 - y1 + 1
    return max(width, height)

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
    """
    Disegna testo con un piccolo box dietro, più leggibile su immagini chiare.
    org = baseline del testo come in cv2.putText
    """
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
def find_connected_components(skeleton_binary: np.ndarray):
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        skeleton_binary, connectivity=8
    )
    return num_labels, labels, stats, centroids

def get_directional_window(term: dict, labels_shape, outward=16, inward=4, halfspan=5):
    """
    Finestra di ricerca orientata secondo il lato del terminale.

    Idea:
    - il terminal point del 03 è appena fuori dal bbox del componente
    - il wire reale continua quasi sempre nella direzione del lato:
        left   -> verso sinistra
        right  -> verso destra
        top    -> verso l'alto
        bottom -> verso il basso

    Quindi conviene cercare:
    - molto nella direzione "outward"
    - poco nel verso opposto
    """
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

def get_square_window(term: dict, labels_shape, radius=12):
    h, w = labels_shape[:2]
    x = int(round(term["x"]))
    y = int(round(term["y"]))
    return clamp_window(x - radius, y - radius, x + radius + 1, y + radius + 1, w, h)

def collect_labels_in_window(labels: np.ndarray, window):
    x1, y1, x2, y2 = window
    roi = labels[y1:y2, x1:x2]
    unique_labels = np.unique(roi)
    return [int(v) for v in unique_labels if int(v) > 0]

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

def is_opamp_aux_terminal(term: dict) -> bool:
    name = str(term.get("name", "")).lower()
    return name in {"aux1", "aux2"}


def get_terminal_search_params(term: dict, default_radius=12, default_halfspan=5):
    if is_opamp_aux_terminal(term):
        return {
            "outward": OPAMP_AUX_SEARCH_OUTWARD,
            "inward": OPAMP_AUX_SEARCH_INWARD,
            "halfspan": OPAMP_AUX_DIRECTIONAL_HALFSPAN,
            "radius": OPAMP_AUX_SQUARE_FALLBACK_RADIUS,
            "terminal_kind": "opamp_auxiliary",
        }

    return {
        "outward": TERMINAL_SEARCH_OUTWARD,
        "inward": TERMINAL_SEARCH_INWARD,
        "halfspan": default_halfspan,
        "radius": default_radius,
        "terminal_kind": "standard",
    }

def is_opamp_aux_terminal(term: dict) -> bool:
    name = str(term.get("name", "")).lower()
    return name in {"aux1", "aux2"}


def match_opamp_aux_vertical(labels: np.ndarray, term: dict):
    """
    Matcher dedicato agli auxiliary dell'opamp.

    Idea:
    - il punto del 03 è vicino al giunto interno sul triangolo
    - la net utile però è spesso sullo stelo verticale verso Vcc / -Vcc
    - quindi cerchiamo in una capsula verticale e scegliamo il label
      che massimizza il progresso outward mantenendo x vicina al terminale
    """
    if not is_opamp_aux_terminal(term):
        return None

    rel = term.get("relative_position")
    if rel not in {"top", "bottom"}:
        return None

    h, w = labels.shape[:2]
    x = int(round(term["x"]))
    y = int(round(term["y"]))

    if rel == "top":
        window = clamp_window(
            x - OPAMP_AUX_MATCH_X_TOL,
            y - OPAMP_AUX_MATCH_OUTWARD,
            x + OPAMP_AUX_MATCH_X_TOL + 1,
            y + OPAMP_AUX_MATCH_INWARD + 1,
            w,
            h,
        )
    else:
        window = clamp_window(
            x - OPAMP_AUX_MATCH_X_TOL,
            y - OPAMP_AUX_MATCH_INWARD,
            x + OPAMP_AUX_MATCH_X_TOL + 1,
            y + OPAMP_AUX_MATCH_OUTWARD + 1,
            w,
            h,
        )

    x1, y1, x2, y2 = window
    roi = labels[y1:y2, x1:x2]
    candidate_labels = [int(v) for v in np.unique(roi) if int(v) > 0]

    if not candidate_labels:
        return {
            "candidate_labels": [],
            "primary_label": None,
            "snap_point": None,
            "snap_distance": None,
            "search_window": [int(v) for v in window],
            "match_mode": "opamp_aux_vertical_none",
        }

    best = None

    for lbl in candidate_labels:
        ys, xs = np.where(roi == lbl)
        if len(xs) < OPAMP_AUX_MATCH_MIN_PIXELS:
            continue

        xs_global = xs + x1
        ys_global = ys + y1

        if rel == "top":
            outward_progress = y - ys_global
        else:
            outward_progress = ys_global - y

        x_penalty = np.abs(xs_global - x)
        pixel_scores = outward_progress - OPAMP_AUX_MATCH_X_PENALTY * x_penalty

        valid = np.where(outward_progress >= -1)[0]
        if len(valid) == 0:
            continue

        best_idx_local = valid[int(np.argmax(pixel_scores[valid]))]

        px = int(xs_global[best_idx_local])
        py = int(ys_global[best_idx_local])
        dist = float(np.sqrt((px - x) ** 2 + (py - y) ** 2))

        label_score = float(
            pixel_scores[best_idx_local] +
            OPAMP_AUX_MATCH_COUNT_WEIGHT * len(valid)
        )

        cand = {
            "label": int(lbl),
            "snap_point": [px, py],
            "snap_distance": round(dist, 3),
            "label_score": label_score,
        }

        if best is None or cand["label_score"] > best["label_score"]:
            best = cand

    if best is None:
        return {
            "candidate_labels": candidate_labels,
            "primary_label": None,
            "snap_point": None,
            "snap_distance": None,
            "search_window": [int(v) for v in window],
            "match_mode": "opamp_aux_vertical_no_valid_label",
        }

    return {
        "candidate_labels": candidate_labels,
        "primary_label": best["label"],
        "snap_point": best["snap_point"],
        "snap_distance": best["snap_distance"],
        "search_window": [int(v) for v in window],
        "match_mode": "opamp_aux_vertical_corridor",
    }

def terminal_to_candidate_labels(labels: np.ndarray, terminals, radius=12, directional_halfspan=5):
    """
    Matching terminale -> source label candidata.

    Regola:
    - terminali normali: finestra direzionale + fallback quadrato
    - aux1/aux2 opamp: prima matcher verticale dedicato
    """
    primary_label_to_terminal_ids = {}
    terminal_debug = {}

    for term in terminals:
        term_id = term["terminal_id"]

        aux_match = match_opamp_aux_vertical(labels, term)

        if aux_match is not None and aux_match["primary_label"] is not None:
            primary_label = int(aux_match["primary_label"])
            snap_point = aux_match["snap_point"]
            snap_distance = aux_match["snap_distance"]
            candidate_labels = aux_match["candidate_labels"]
            used_window = aux_match["search_window"]
            match_mode = aux_match["match_mode"]

            primary_label_to_terminal_ids.setdefault(primary_label, set()).add(term_id)

            terminal_debug[term_id] = {
                "candidate_labels": candidate_labels,
                "primary_label": primary_label,
                "match_mode": match_mode,
                "search_window": [int(v) for v in used_window],
                "snap_point": snap_point,
                "snap_distance": snap_distance,
                "relative_position": term.get("relative_position"),
                "terminal_kind": "opamp_auxiliary",
            }
            continue

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
            primary_label_to_terminal_ids.setdefault(primary_label, set()).add(term_id)

        terminal_debug[term_id] = {
            "candidate_labels": candidate_labels,
            "primary_label": primary_label,
            "match_mode": match_mode,
            "search_window": [int(v) for v in used_window],
            "snap_point": snap_point,
            "snap_distance": snap_distance,
            "relative_position": term.get("relative_position"),
            "terminal_kind": "standard",
        }

    return primary_label_to_terminal_ids, terminal_debug

# candidate nets
def build_candidate_nets(stats, label_to_terminal_ids):
    """
    Costruisce le candidate nets a partire dalle connected components
    dello skeleton e dalla mappa label -> terminal_id connessi.

    Parameters
    ----------
    stats : np.ndarray
        Output stats di cv2.connectedComponentsWithStats.
        Riga 0 = background.
    label_to_terminal_ids : dict[int, set[str]]
        Mappa da source_label a insieme di terminal_id agganciati.

    Returns
    -------
    list[dict]
        Lista di candidate nets.
    """
    candidates = []

    for lbl, stat_row in enumerate(stats[1:], start=1):  # salto background
        x = int(stat_row[cv2.CC_STAT_LEFT])
        y = int(stat_row[cv2.CC_STAT_TOP])
        w = int(stat_row[cv2.CC_STAT_WIDTH])
        h = int(stat_row[cv2.CC_STAT_HEIGHT])
        area = int(stat_row[cv2.CC_STAT_AREA])

        connected_terminal_ids = sorted(label_to_terminal_ids.get(lbl, set()))
        bbox = [x, y, x + w - 1, y + h - 1]

        candidates.append({
            "source_label": lbl,
            "pixel_count": area,
            "bbox": bbox,
            "connected_terminal_ids": connected_terminal_ids,
            "n_connected_terminals": len(connected_terminal_ids),
        })

    return candidates

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
        # se la net tocca un solo terminale, deve avere un minimo di consistenza
        if cand["n_connected_terminals"] == 1:
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

def relabel_kept_nets(original_labels: np.ndarray, kept_candidates, sort_order="xy"):
    kept_sorted = sorted(kept_candidates, key=lambda x: get_sort_key(x, sort_order=sort_order))

    relabeled = np.zeros_like(original_labels, dtype=np.int32)
    nets = []

    for idx, cand in enumerate(kept_sorted, start=1):
        old_label = cand["source_label"]
        relabeled[original_labels == old_label] = idx

        net = {
            "net_id": f"N{idx}",
            "net_index": idx,
            "source_label": old_label,
            "pixel_count": cand["pixel_count"],
            "bbox": cand["bbox"],
            "connected_terminal_ids": cand["connected_terminal_ids"],
            "n_connected_terminals": cand["n_connected_terminals"],
        }
        nets.append(net)

    return relabeled, nets

# debug / visualization
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


def draw_terminal_debug(image_bgr, terminals, terminal_debug, relabeled_map, nets):
    out = image_bgr.copy()
    index_to_net_id = {net["net_index"]: net["net_id"] for net in nets}

    for term in terminals:
        term_id = term["terminal_id"]
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
                f"{term_id}: none",
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
            f"{term_id}->{net_id}",
            (tx + 8, max(16, ty - 8)),
            color=TERMINAL_TEXT_COLOR,
            outline_color=TERMINAL_TEXT_OUTLINE,
            font_scale=TERMINAL_TEXT_SCALE,
            thickness=TERMINAL_TEXT_THICKNESS,
            outline_thickness=TERMINAL_TEXT_OUTLINE_THICKNESS,
        )

    return out

# main
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

        num_labels, labels, stats, _ = find_connected_components(skeleton_binary)

        label_to_terminal_ids, terminal_to_labels = terminal_to_candidate_labels(
            labels,
            terminals,
            radius=TERMINAL_SQUARE_FALLBACK_RADIUS,
            directional_halfspan=TERMINAL_DIRECTIONAL_HALFSPAN,
        )

        candidates = build_candidate_nets(stats, label_to_terminal_ids)
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

            "opamp_aux_search_outward": OPAMP_AUX_SEARCH_OUTWARD,
            "opamp_aux_search_inward": OPAMP_AUX_SEARCH_INWARD,
            "opamp_aux_directional_halfspan": OPAMP_AUX_DIRECTIONAL_HALFSPAN,
            "opamp_aux_square_fallback_radius": OPAMP_AUX_SQUARE_FALLBACK_RADIUS,
            "opamp_aux_match_outward": OPAMP_AUX_MATCH_OUTWARD,
            "opamp_aux_match_inward": OPAMP_AUX_MATCH_INWARD,
            "opamp_aux_match_x_tol": OPAMP_AUX_MATCH_X_TOL,

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
            "label_map_path": str(label_map_path),
            "terminal_to_candidate_labels": terminal_to_labels,
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
