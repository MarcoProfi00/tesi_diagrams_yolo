"""
Euristiche per distinguere incroci, ponticelli e falsi corti nello skeleton.

Nel grafo terminale una connected component dello skeleton diventa un nodo
elettrico. Se uno crossing grafico viene letto come una singola component,
il circuito produce un falso corto. Questo modulo cerca di riconoscere:
  - ponticelli con gobba;
  - incroci piani senza pallino;
  - micro-bridge dovuti a skeletonizzazione;
  - nodi pieni reali che invece devono restare connessi.
"""

from __future__ import annotations

from itertools import combinations

import cv2
import numpy as np

from .config import (
    BRIDGE_CUT_HALF_HEIGHT,
    BRIDGE_CUT_HALF_WIDTH,
    BRIDGE_FILLED_NODE_AREA_MIN,
    BRIDGE_FILLED_NODE_CENTER_AREA_MIN,
    BRIDGE_FILLED_NODE_CENTER_RADIUS,
    BRIDGE_FILLED_NODE_RADIUS,
    BRIDGE_FILLED_NODE_STRONG_AREA_MIN,
    BRIDGE_BLUE_STYLE_MIN_BLUE_DELTA,
    BRIDGE_BLUE_STYLE_MIN_MEDIAN_BGR_DELTA,
    BRIDGE_BLUE_STYLE_MIN_PIXEL_FRACTION,
    BRIDGE_BLUE_STYLE_MIN_SATURATION,
    BRIDGE_BLUE_STYLE_THICK_HUMP_ONLY,
    BRIDGE_HUMP_X_MAX,
    BRIDGE_HUMP_X_MIN,
    BRIDGE_HUMP_Y_MAX,
    BRIDGE_HUMP_Y_MIN,
    BRIDGE_HUMP_COLLAPSE_RADIUS,
    BRIDGE_HUMP_MIN_ANCHOR_QUALITY,
    BRIDGE_MIN_PIXELS_PER_DIRECTION,
    BRIDGE_MIN_RUN,
    BRIDGE_PROBE_DISTANCE,
    BRIDGE_SINGLETON_MIN_HUMP_DISTANCE,
    BRIDGE_THICK_HUMP_ENABLE,
    BRIDGE_THICK_HUMP_FOOT_Y_MAX,
    BRIDGE_THICK_HUMP_MIN_SIDE_PIXELS,
    BRIDGE_THICK_HUMP_MIN_FOOT_PIXELS,
    BRIDGE_THICK_HUMP_RELAXED_MIN_SKELETON_Y_SPAN,
    BRIDGE_THICK_HUMP_STRONG_MIN_FOOT_PIXELS,
    BRIDGE_THICK_HUMP_STRONG_MIN_VERTICAL_PIXELS,
    BRIDGE_THICK_HUMP_STRONG_SCORE_MIN,
    BRIDGE_THICK_HUMP_MIN_SKELETON_Y_SPAN,
    BRIDGE_THICK_HUMP_MIN_VERTICAL_PIXELS,
    BRIDGE_THICK_HUMP_LOW_SPAN_SYMMETRY_REJECT_MIN,
    BRIDGE_THICK_HUMP_VERTICAL_SEARCH_RADIUS,
    BRIDGE_THICK_HUMP_X_MAX,
    BRIDGE_THICK_HUMP_Y_MAX,
    MICRO_BRIDGE_MAX_SIDE_GAP,
    MICRO_BRIDGE_COLUMN_MIN_Y_SPAN,
    MICRO_BRIDGE_COLUMN_X_TOL,
    MICRO_BRIDGE_MIN_HORIZONTAL_RUN,
    MICRO_BRIDGE_MIN_SIDE_GAP,
    MICRO_BRIDGE_MIN_VERTICAL_PIXELS,
    MICRO_BRIDGE_TERMINAL_HORIZONTAL_BAND,
    MICRO_BRIDGE_VERTICAL_BAND_DEPTH,
    MICRO_BRIDGE_VERTICAL_BAND_RADIUS,
    OFFSET_BRIDGE_ROW_MAX_X_GAP,
    OFFSET_BRIDGE_ROW_MIN_POINTS,
    OFFSET_BRIDGE_ROW_MIN_X_SPAN,
    OFFSET_BRIDGE_ROW_Y_TOL,
    PLAIN_CROSSING_SPLIT_ENABLE,
    PLAIN_CROSSING_SELF_SHORT_EXCLUDED_CLASSES,
    PLAIN_CROSSING_CUT_HALF_HEIGHT,
    PLAIN_CROSSING_CUT_HALF_WIDTH,
    PLAIN_CROSSING_DOT_AREA_MIN,
    PLAIN_CROSSING_DOT_RADIUS,
    PLAIN_CROSSING_MIN_PIXELS_PER_DIRECTION,
    PLAIN_CROSSING_MIN_RUN,
    PLAIN_CROSSING_PROBE_DISTANCE,
    RADIAL_CROSSING_AXIS_DOT_MAX,
    RADIAL_CROSSING_CLUSTER_RADIUS,
    RADIAL_CROSSING_CUT_HALF_SIZE,
    RADIAL_CROSSING_MIN_BRANCH_PIXELS,
    RADIAL_CROSSING_MIN_TERMINALS,
    RADIAL_CROSSING_OPPOSITE_DOT_MAX,
    TERMINAL_SQUARE_FALLBACK_RADIUS,
)
from .geometry import clamp_window
from .ids import normalize_class_name
from .label_union import LabelUnionFind
from .skeleton_ops import load_junction_support_binary


# Verifica la presenza del ponte
# Se c'è la gobba allora è un ponte
def has_bridge_hump(binary: np.ndarray, x: int, y: int):
    """Verifica se attorno a un candidato esiste una gobba da ponticello."""
    _, w = binary.shape[:2]
    left_count = 0
    right_count = 0

    for dy in range(BRIDGE_HUMP_Y_MIN, BRIDGE_HUMP_Y_MAX + 1):
        yy = int(y) - dy
        if yy < 0:
            continue

        for dx in range(BRIDGE_HUMP_X_MIN, BRIDGE_HUMP_X_MAX + 1):
            lx = int(x) - dx
            rx = int(x) + dx
            if 0 <= lx < w and binary[yy, lx] > 0:
                left_count += 1
            if 0 <= rx < w and binary[yy, rx] > 0:
                right_count += 1

    return left_count >= 1 and right_count >= 1


def bridge_direction_support(binary: np.ndarray, x: int, y: int):
    """
    Conta il supporto orizzontale/verticale attorno a un candidato ponte.

    La gobba e il ramo verticale possono non cadere sullo stesso pixel dopo
    skeletonizzazione, quindi cerchiamo il supporto verticale in una piccola
    finestra locale.
    """
    h, w = binary.shape[:2]
    local_radius = max(2, BRIDGE_CUT_HALF_WIDTH // 2)

    left = int(np.sum(binary[y, max(0, x - BRIDGE_MIN_RUN):x]))
    right = int(np.sum(binary[y, x + 1:min(w, x + BRIDGE_MIN_RUN + 1)]))
    up = int(np.sum(binary[max(0, y - BRIDGE_MIN_RUN):y, x]))
    down = int(np.sum(binary[y + 1:min(h, y + BRIDGE_MIN_RUN + 1), x]))

    # La gobba e il tratto verticale possono cadere su pixel vicini ma non
    # identici dopo skeletonizzazione. Manteniamo orizzontale e gobba ancorate
    # al candidato, ma cerchiamo il supporto verticale in una piccola finestra.
    for dy in range(-local_radius, local_radius + 1):
        yy = int(y) + dy
        if yy < 0 or yy >= h:
            continue
        for dx in range(-local_radius, local_radius + 1):
            xx = int(x) + dx
            if xx < 0 or xx >= w or binary[yy, xx] == 0:
                continue

            up = max(up, int(np.sum(binary[max(0, yy - BRIDGE_MIN_RUN):yy, xx])))
            down = max(down, int(np.sum(binary[yy + 1:min(h, yy + BRIDGE_MIN_RUN + 1), xx])))

    return left, right, up, down


def count_pixels_in_window(binary: np.ndarray, x1: int, y1: int, x2: int, y2: int):
    h, w = binary.shape[:2]
    x1, y1, x2, y2 = clamp_window(x1, y1, x2, y2, w, h)
    if x2 <= x1 or y2 <= y1:
        return 0
    return int(np.count_nonzero(binary[y1:y2, x1:x2] > 0))


def count_pixels_fast(
    binary: np.ndarray,
    integral: np.ndarray | None,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
):
    if integral is None:
        return count_pixels_in_window(binary, x1, y1, x2, y2)

    h, w = binary.shape[:2]
    x1, y1, x2, y2 = clamp_window(x1, y1, x2, y2, w, h)
    if x2 <= x1 or y2 <= y1:
        return 0

    return int(
        integral[y2, x2]
        - integral[y1, x2]
        - integral[y2, x1]
        + integral[y1, x1]
    )


def has_filled_bridge_node(
    support_binary: np.ndarray | None,
    x: int,
    y: int,
    support_integral: np.ndarray | None = None,
):
    if support_binary is None:
        return False

    radius = int(BRIDGE_FILLED_NODE_RADIUS)
    center_radius = int(BRIDGE_FILLED_NODE_CENTER_RADIUS)
    local_area = count_pixels_fast(
        support_binary,
        support_integral,
        int(x) - radius,
        int(y) - radius,
        int(x) + radius + 1,
        int(y) + radius + 1,
    )
    center_area = count_pixels_fast(
        support_binary,
        support_integral,
        int(x) - center_radius,
        int(y) - center_radius,
        int(x) + center_radius + 1,
        int(y) + center_radius + 1,
    )
    if local_area >= BRIDGE_FILLED_NODE_STRONG_AREA_MIN:
        return True

    return (
        local_area >= BRIDGE_FILLED_NODE_AREA_MIN
        and center_area >= BRIDGE_FILLED_NODE_CENTER_AREA_MIN
    )


def thick_bridge_hump_score(
    support_binary: np.ndarray | None,
    support_integral: np.ndarray | None,
    x: int,
    y: int,
):
    """
    Valida una gobba sulla maschera spessa: deve esserci in modo esplicito
    materiale grafico sia a sinistra sia a destra del candidato, sopra o sotto
    il punto. Questo evita di inventare ponti da semplici incroci perpendicolari.
    """
    if support_binary is None:
        return None

    best = None

    for direction in (-1, 1):
        y_start = int(y) + direction * BRIDGE_HUMP_Y_MIN
        y_end = int(y) + direction * BRIDGE_THICK_HUMP_Y_MAX
        y1 = min(y_start, y_end)
        y2 = max(y_start, y_end) + 1

        left_pixels = count_pixels_fast(
            support_binary,
            support_integral,
            int(x) - BRIDGE_THICK_HUMP_X_MAX,
            y1,
            int(x) - BRIDGE_HUMP_X_MIN + 1,
            y2,
        )
        right_pixels = count_pixels_fast(
            support_binary,
            support_integral,
            int(x) + BRIDGE_HUMP_X_MIN,
            y1,
            int(x) + BRIDGE_THICK_HUMP_X_MAX + 1,
            y2,
        )
        if min(left_pixels, right_pixels) < BRIDGE_THICK_HUMP_MIN_SIDE_PIXELS:
            continue

        foot_y_start = int(y) + direction * BRIDGE_HUMP_Y_MIN
        foot_y_end = int(y) + direction * BRIDGE_THICK_HUMP_FOOT_Y_MAX
        foot_y1 = min(foot_y_start, foot_y_end)
        foot_y2 = max(foot_y_start, foot_y_end) + 1
        left_foot_pixels = count_pixels_fast(
            support_binary,
            support_integral,
            int(x) - BRIDGE_THICK_HUMP_X_MAX,
            foot_y1,
            int(x) - BRIDGE_HUMP_X_MIN + 1,
            foot_y2,
        )
        right_foot_pixels = count_pixels_fast(
            support_binary,
            support_integral,
            int(x) + BRIDGE_HUMP_X_MIN,
            foot_y1,
            int(x) + BRIDGE_THICK_HUMP_X_MAX + 1,
            foot_y2,
        )
        if min(left_foot_pixels, right_foot_pixels) < BRIDGE_THICK_HUMP_MIN_FOOT_PIXELS:
            continue

        score = min(left_pixels, right_pixels) + max(left_pixels, right_pixels) * 0.1
        candidate = {
            "hump_direction": int(direction),
            "hump_score": float(score),
            "left_pixels": int(left_pixels),
            "right_pixels": int(right_pixels),
            "left_foot_pixels": int(left_foot_pixels),
            "right_foot_pixels": int(right_foot_pixels),
        }
        if best is None or candidate["hump_score"] > best["hump_score"]:
            best = candidate

    return best


def nearby_vertical_bridge_support(binary: np.ndarray, x: int, y: int):
    radius = int(BRIDGE_THICK_HUMP_VERTICAL_SEARCH_RADIUS)
    h, w = binary.shape[:2]
    best = 0

    for yy in range(max(0, int(y) - radius), min(h, int(y) + radius + 1)):
        for xx in range(max(0, int(x) - radius), min(w, int(x) + radius + 1)):
            if binary[yy, xx] == 0:
                continue
            up = count_run(binary, xx, yy, 0, -1, BRIDGE_MIN_RUN)
            down = count_run(binary, xx, yy, 0, 1, BRIDGE_MIN_RUN)
            best = max(best, up, down, up + down)

    return best


def hump_side_skeleton_y_span(skeleton_binary: np.ndarray, x: int, y: int, direction: int):
    y_start = int(y) + int(direction) * BRIDGE_HUMP_Y_MIN
    y_end = int(y) + int(direction) * BRIDGE_THICK_HUMP_Y_MAX
    y1 = min(y_start, y_end)
    y2 = max(y_start, y_end) + 1
    h, w = skeleton_binary.shape[:2]

    left_x1 = max(0, int(x) - BRIDGE_THICK_HUMP_X_MAX)
    left_x2 = max(0, int(x) - BRIDGE_HUMP_X_MIN + 1)
    right_x1 = min(w, int(x) + BRIDGE_HUMP_X_MIN)
    right_x2 = min(w, int(x) + BRIDGE_THICK_HUMP_X_MAX + 1)

    def side_span(x1: int, x2: int):
        if x2 <= x1:
            return 0
        side_ys = []
        for yy in range(max(0, y1), min(h, y2)):
            if np.any(skeleton_binary[yy, x1:x2] > 0):
                side_ys.append(yy)
        if not side_ys:
            return 0
        return int(max(side_ys) - min(side_ys))

    return min(side_span(left_x1, left_x2), side_span(right_x1, right_x2))


def detect_thick_hump_bridge(
    skeleton_binary: np.ndarray,
    support_binary: np.ndarray | None,
    support_integral: np.ndarray | None,
    labels: np.ndarray,
    x: int,
    y: int,
):
    if not BRIDGE_THICK_HUMP_ENABLE or support_binary is None:
        return None

    if has_filled_junction_dot(support_binary, x, y) or has_filled_bridge_node(
        support_binary,
        x,
        y,
        support_integral,
    ):
        return None

    shape = thick_bridge_hump_score(support_binary, support_integral, x, y)
    if shape is None:
        return None

    vertical_support = nearby_vertical_bridge_support(skeleton_binary, x, y)
    if vertical_support < BRIDGE_THICK_HUMP_MIN_VERTICAL_PIXELS:
        return None

    skeleton_y_span = hump_side_skeleton_y_span(
        skeleton_binary,
        x,
        y,
        int(shape["hump_direction"]),
    )
    if skeleton_y_span < BRIDGE_THICK_HUMP_MIN_SKELETON_Y_SPAN:
        strong_low_hump = (
            skeleton_y_span >= BRIDGE_THICK_HUMP_RELAXED_MIN_SKELETON_Y_SPAN
            and float(shape["hump_score"]) >= float(BRIDGE_THICK_HUMP_STRONG_SCORE_MIN)
            and min(
                int(shape.get("left_foot_pixels", 0)),
                int(shape.get("right_foot_pixels", 0)),
            ) >= int(BRIDGE_THICK_HUMP_STRONG_MIN_FOOT_PIXELS)
            and int(vertical_support) >= int(BRIDGE_THICK_HUMP_STRONG_MIN_VERTICAL_PIXELS)
        )
        if not strong_low_hump:
            return None

    source_label = nearest_split_label(
        labels,
        x,
        y,
        radius=max(5, BRIDGE_THICK_HUMP_VERTICAL_SEARCH_RADIUS),
    )
    if source_label is None:
        return None

    return {
        "x": int(x),
        "y": int(y),
        "label": int(source_label),
        "bridge_style": "hump",
        "bridge_detector": "thick_hump",
        "hump_direction": int(shape["hump_direction"]),
        "hump_score": float(shape["hump_score"]) + float(vertical_support),
        "vertical_support": int(vertical_support),
        "skeleton_y_span": int(skeleton_y_span),
        "left_pixels": int(shape["left_pixels"]),
        "right_pixels": int(shape["right_pixels"]),
    }


def is_blue_wire_style(wire_extraction: dict | None, support_binary: np.ndarray | None):
    if not BRIDGE_BLUE_STYLE_THICK_HUMP_ONLY:
        return True
    if support_binary is None:
        return False

    image_path = (wire_extraction or {}).get("image_path")
    if not image_path:
        return False

    image = cv2.imread(str(image_path))
    if image is None:
        return False

    mask = support_binary > 0
    if not np.any(mask):
        return False

    pixels = image[mask]
    blue_delta = pixels[:, 0].astype(np.int16) - pixels[:, 2].astype(np.int16)
    saturation = pixels.max(axis=1).astype(np.int16) - pixels.min(axis=1).astype(np.int16)
    blue_like = (
        (blue_delta >= BRIDGE_BLUE_STYLE_MIN_BLUE_DELTA)
        & (saturation >= BRIDGE_BLUE_STYLE_MIN_SATURATION)
    )
    return (
        float(np.mean(blue_like)) >= BRIDGE_BLUE_STYLE_MIN_PIXEL_FRACTION
        and float(np.median(blue_delta)) >= BRIDGE_BLUE_STYLE_MIN_MEDIAN_BGR_DELTA
    )


def local_split_branch_labels(
    skeleton_binary: np.ndarray,
    x: int,
    y: int,
    cut_half_width: int,
    cut_half_height: int,
    probe_distance: int,
):
    h, w = skeleton_binary.shape[:2]
    roi_margin = int(probe_distance) + max(int(cut_half_width), int(cut_half_height)) + 12
    roi_x1, roi_y1, roi_x2, roi_y2 = clamp_window(
        int(x) - roi_margin,
        int(y) - roi_margin,
        int(x) + roi_margin + 1,
        int(y) + roi_margin + 1,
        w,
        h,
    )
    cut_skeleton = skeleton_binary[roi_y1:roi_y2, roi_x1:roi_x2].copy()
    local_x = int(x) - int(roi_x1)
    local_y = int(y) - int(roi_y1)

    cut_x1, cut_y1, cut_x2, cut_y2 = clamp_window(
        local_x - int(cut_half_width),
        local_y - int(cut_half_height),
        local_x + int(cut_half_width) + 1,
        local_y + int(cut_half_height) + 1,
        cut_skeleton.shape[1],
        cut_skeleton.shape[0],
    )
    cut_skeleton[cut_y1:cut_y2, cut_x1:cut_x2] = 0

    _, split_labels, _, _ = cv2.connectedComponentsWithStats(cut_skeleton, connectivity=8)
    return [
        nearest_split_label(split_labels, local_x, local_y - int(probe_distance)),
        nearest_split_label(split_labels, local_x, local_y + int(probe_distance)),
        nearest_split_label(split_labels, local_x - int(probe_distance), local_y),
        nearest_split_label(split_labels, local_x + int(probe_distance), local_y),
    ]


def bridge_split_branch_quality(skeleton_binary: np.ndarray, candidate: dict):
    branch_labels = local_split_branch_labels(
        skeleton_binary,
        int(candidate["x"]),
        int(candidate["y"]),
        BRIDGE_CUT_HALF_WIDTH,
        BRIDGE_CUT_HALF_HEIGHT,
        BRIDGE_PROBE_DISTANCE,
    )
    if any(label is None for label in branch_labels):
        return 0
    return len({int(label) for label in branch_labels})


def choose_hump_candidate(cluster: list[dict], skeleton_binary: np.ndarray | None):
    if skeleton_binary is None:
        return max(cluster, key=lambda item: float(item.get("hump_score", 0.0)))

    best = max(
        cluster,
        key=lambda item: (
            bridge_split_branch_quality(skeleton_binary, item),
            float(item.get("hump_score", 0.0)),
        ),
    )
    return refine_hump_split_anchor(best, skeleton_binary)


def refine_hump_split_anchor(candidate: dict, skeleton_binary: np.ndarray):
    radius = int(BRIDGE_THICK_HUMP_VERTICAL_SEARCH_RADIUS)
    cx = int(candidate["x"])
    cy = int(candidate["y"])
    best = dict(candidate)
    best_quality = bridge_split_branch_quality(skeleton_binary, best)
    best_distance = 0

    for yy in range(cy - radius, cy + radius + 1):
        for xx in range(cx - radius, cx + radius + 1):
            if yy < 0 or yy >= skeleton_binary.shape[0] or xx < 0 or xx >= skeleton_binary.shape[1]:
                continue
            probe = {**candidate, "x": int(xx), "y": int(yy)}
            quality = bridge_split_branch_quality(skeleton_binary, probe)
            distance = abs(int(xx) - cx) + abs(int(yy) - cy)
            if quality > best_quality or (quality == best_quality and distance < best_distance):
                best = probe
                best_quality = quality
                best_distance = distance

    if int(best["x"]) != cx or int(best["y"]) != cy:
        best["anchor_refined"] = True
        best["detected_x"] = cx
        best["detected_y"] = cy
        best["anchor_quality"] = int(best_quality)

    return best


def collapse_bridge_candidates(candidates: list[dict], skeleton_binary: np.ndarray | None = None):
    collapsed = []

    def style_radius(candidate: dict):
        if candidate.get("bridge_style") == "micro_gap":
            return 4
        return BRIDGE_HUMP_COLLAPSE_RADIUS

    hump_clusters = []
    micro_candidates = []
    for candidate in candidates:
        if candidate.get("bridge_style") == "micro_gap":
            micro_candidates.append(candidate)
            continue

        placed = False
        for cluster in hump_clusters:
            avg_x = sum(int(item["x"]) for item in cluster) / float(len(cluster))
            avg_y = sum(int(item["y"]) for item in cluster) / float(len(cluster))
            if (
                abs(int(candidate["x"]) - avg_x) <= BRIDGE_HUMP_COLLAPSE_RADIUS
                and abs(int(candidate["y"]) - avg_y) <= BRIDGE_HUMP_COLLAPSE_RADIUS
            ):
                cluster.append(candidate)
                placed = True
                break
        if not placed:
            hump_clusters.append([candidate])

    for cluster in hump_clusters:
        collapsed.append(choose_hump_candidate(cluster, skeleton_binary))

    for cand in sorted(micro_candidates, key=lambda item: (int(item["y"]), int(item["x"]))):
        radius = style_radius(cand)
        if any(
            abs(int(cand["x"]) - int(prev["x"])) <= max(radius, style_radius(prev))
            and abs(int(cand["y"]) - int(prev["y"])) <= max(radius, style_radius(prev))
            for prev in collapsed
        ):
            continue
        collapsed.append(cand)

    return sorted(collapsed, key=lambda item: (int(item["y"]), int(item["x"])))


def is_symmetric_low_span_thick_hump(candidate: dict):
    """
    Riconosce il falso arco prodotto dai bordi di una giunzione spessa.

    Il detector thick-hump deve restare tollerante prima del collapse: in
    questo modo i falsi archi assorbono i micro-gap della stessa giunzione.
    Dopo il collapse possiamo invece scartare il candidato se non mostra
    sviluppo verticale e i due lati sono quasi perfettamente simmetrici.
    """
    if candidate.get("bridge_detector") != "thick_hump":
        return False

    try:
        skeleton_y_span = int(candidate.get("skeleton_y_span", 0))
        left_pixels = int(candidate.get("left_pixels", 0))
        right_pixels = int(candidate.get("right_pixels", 0))
    except (TypeError, ValueError):
        return False

    if skeleton_y_span >= int(BRIDGE_THICK_HUMP_MIN_SKELETON_Y_SPAN):
        return False
    if min(left_pixels, right_pixels) <= 0:
        return False

    side_balance = min(left_pixels, right_pixels) / float(max(left_pixels, right_pixels))
    return side_balance >= float(BRIDGE_THICK_HUMP_LOW_SPAN_SYMMETRY_REJECT_MIN)


# Rileva ponte sullo skeleton
# Cerca punti con:
#   continuita nelle 4 dir
#   hump
#   label valida
def detect_wire_bridges(
    skeleton_binary: np.ndarray,
    labels: np.ndarray,
    junction_binary: np.ndarray | None = None,
    enable_thick_hump_detection: bool = True,
    enable_skeleton_hump_detection: bool = True,
):
    """
    Rileva candidati ponticello nello skeleton.

    Combina rilevazione classica, micro-bridge e, per stili di disegno spessi o
    blu, supporto dalla maschera binaria piena.
    """
    if not enable_thick_hump_detection and enable_skeleton_hump_detection:
        return detect_legacy_wire_bridges(skeleton_binary, labels, junction_binary)

    binary = np.where(skeleton_binary > 0, 1, 0).astype(np.uint8)
    support_binary = np.where(junction_binary > 0, 1, 0).astype(np.uint8) if junction_binary is not None else None
    support_integral = cv2.integral(support_binary, sdepth=cv2.CV_32S) if support_binary is not None else None
    h, w = binary.shape[:2]
    candidates = []

    ys, xs = np.where(binary > 0)
    for y, x in zip(ys, xs):
        y = int(y)
        x = int(x)
        if y < BRIDGE_HUMP_Y_MAX + 1 or y >= h - BRIDGE_PROBE_DISTANCE:
            continue
        if x < BRIDGE_PROBE_DISTANCE or x >= w - BRIDGE_PROBE_DISTANCE:
            continue

        if enable_thick_hump_detection:
            thick_candidate = detect_thick_hump_bridge(binary, support_binary, support_integral, labels, x, y)
            if thick_candidate is not None:
                candidates.append(thick_candidate)
                continue

        if not enable_skeleton_hump_detection:
            continue
        if not has_bridge_hump(binary, x, y):
            continue
        if support_binary is not None and (
            has_filled_junction_dot(support_binary, x, y)
            or has_filled_bridge_node(support_binary, x, y, support_integral)
        ):
            continue

        left, right, up, down = bridge_direction_support(binary, x, y)
        # Nei ponti a gobba il filo che "salta" e' continuo a sinistra e
        # destra, mentre lo stelo verticale puo' essere forte solo da un
        # lato del candidato dopo skeleton/closing. Non richiediamo quindi
        # quattro direzioni piene come per un normale crossing.
        if min(left, right) < BRIDGE_MIN_PIXELS_PER_DIRECTION:
            continue
        if max(up, down) < BRIDGE_MIN_PIXELS_PER_DIRECTION:
            continue

        source_label = nearest_split_label(labels, x, y, radius=5)
        if source_label is None:
            continue

        candidates.append({
            "x": int(x),
            "y": int(y),
            "label": int(source_label),
            "bridge_style": "hump",
            "bridge_detector": "skeleton_hump",
            "hump_score": float(min(left, right) + max(up, down)),
        })

    candidates.extend(detect_micro_wire_bridges(binary, labels, junction_binary))

    # Collassiamo piu' pixel dello stesso ponte in un solo candidato.
    collapsed = collapse_bridge_candidates(candidates, binary)
    return [
        candidate
        for candidate in collapsed
        if (
            candidate.get("bridge_style") == "micro_gap"
            or (
                not is_symmetric_low_span_thick_hump(candidate)
                and bridge_split_branch_quality(binary, candidate) >= BRIDGE_HUMP_MIN_ANCHOR_QUALITY
            )
        )
    ]


def detect_legacy_wire_bridges(
    skeleton_binary: np.ndarray,
    labels: np.ndarray,
    junction_binary: np.ndarray | None = None,
):
    binary = np.where(skeleton_binary > 0, 1, 0).astype(np.uint8)
    h, w = binary.shape[:2]
    candidates = []

    for y in range(BRIDGE_HUMP_Y_MAX + 1, h - BRIDGE_PROBE_DISTANCE):
        for x in range(BRIDGE_PROBE_DISTANCE, w - BRIDGE_PROBE_DISTANCE):
            if binary[y, x] == 0:
                continue

            if not has_bridge_hump(binary, x, y):
                continue

            left, right, up, down = bridge_direction_support(binary, x, y)
            if min(left, right) < BRIDGE_MIN_PIXELS_PER_DIRECTION:
                continue
            if max(up, down) < BRIDGE_MIN_PIXELS_PER_DIRECTION:
                continue

            source_label = nearest_split_label(labels, x, y, radius=5)
            if source_label is None:
                continue

            candidates.append({
                "x": int(x),
                "y": int(y),
                "label": int(source_label),
                "bridge_style": "hump",
            })

    candidates.extend(detect_micro_wire_bridges(binary, labels, junction_binary))

    collapsed = []
    for cand in candidates:
        if any(abs(cand["x"] - prev["x"]) <= 4 and abs(cand["y"] - prev["y"]) <= 4 for prev in collapsed):
            continue
        collapsed.append(cand)

    return collapsed


def detect_micro_wire_bridges(
    binary: np.ndarray,
    labels: np.ndarray,
    junction_binary: np.ndarray | None = None,
):
    h, w = binary.shape[:2]
    candidates = []

    for y in range(MICRO_BRIDGE_VERTICAL_BAND_DEPTH, h - MICRO_BRIDGE_VERTICAL_BAND_DEPTH):
        for x in range(BRIDGE_PROBE_DISTANCE, w - BRIDGE_PROBE_DISTANCE):
            if binary[y, x] == 0:
                continue

            if junction_binary is not None and has_filled_junction_dot(junction_binary, x, y):
                continue

            left_gap, left_run = count_run_after_gap(
                binary,
                x,
                y,
                -1,
                MICRO_BRIDGE_MAX_SIDE_GAP,
                BRIDGE_MIN_RUN,
            )
            right_gap, right_run = count_run_after_gap(
                binary,
                x,
                y,
                1,
                MICRO_BRIDGE_MAX_SIDE_GAP,
                BRIDGE_MIN_RUN,
            )
            if left_gap is None or right_gap is None:
                continue
            if min(left_gap, right_gap) < MICRO_BRIDGE_MIN_SIDE_GAP:
                continue
            if min(left_run, right_run) < MICRO_BRIDGE_MIN_HORIZONTAL_RUN:
                continue

            up_pixels = count_vertical_band_pixels(binary, x, y, -1)
            down_pixels = count_vertical_band_pixels(binary, x, y, 1)
            if min(up_pixels, down_pixels) < MICRO_BRIDGE_MIN_VERTICAL_PIXELS:
                continue

            source_label = nearest_split_label(labels, x, y, radius=6)
            if source_label is None:
                continue

            candidates.append({
                "x": int(x),
                "y": int(y),
                "label": int(source_label),
                "bridge_style": "micro_gap",
                "max_side_gap": int(max(left_gap, right_gap)),
            })

    return candidates


def count_run_after_gap(
    binary: np.ndarray,
    x: int,
    y: int,
    dx: int,
    max_gap: int,
    run_limit: int,
):
    h, w = binary.shape[:2]
    for offset in range(1, int(max_gap) + 1):
        sx = int(x) + int(dx) * offset
        if sx < 0 or sx >= w or y < 0 or y >= h:
            continue
        if binary[int(y), sx] == 0:
            continue

        return offset, 1 + count_run(binary, sx, int(y), int(dx), 0, int(run_limit))

    return None, 0


def count_vertical_band_pixels(binary: np.ndarray, x: int, y: int, direction: int):
    h, w = binary.shape[:2]
    if direction > 0:
        x1, y1, x2, y2 = clamp_window(
            int(x) - MICRO_BRIDGE_VERTICAL_BAND_RADIUS,
            int(y) + 1,
            int(x) + MICRO_BRIDGE_VERTICAL_BAND_RADIUS + 1,
            int(y) + MICRO_BRIDGE_VERTICAL_BAND_DEPTH + 1,
            w,
            h,
        )
    else:
        x1, y1, x2, y2 = clamp_window(
            int(x) - MICRO_BRIDGE_VERTICAL_BAND_RADIUS,
            int(y) + int(direction) * MICRO_BRIDGE_VERTICAL_BAND_DEPTH,
            int(x) + MICRO_BRIDGE_VERTICAL_BAND_RADIUS + 1,
            int(y),
            w,
            h,
        )

    return int(np.count_nonzero(binary[y1:y2, x1:x2] > 0))

# Un pallino pieno indica un nodo reale, quindi il crossing non va spezzato.
def has_filled_junction_dot(junction_binary: np.ndarray | None, x: int, y: int):
    if junction_binary is None:
        return False

    h, w = junction_binary.shape[:2]
    radius = PLAIN_CROSSING_DOT_RADIUS
    best_area = 0

    # Il candidato puo' cadere sul bordo del pallino per via dello spessore
    # della maschera. Cerchiamo quindi anche in una piccola griglia vicina.
    for dy in (-4, 0, 4):
        for dx in (-4, 0, 4):
            cx = int(x) + dx
            cy = int(y) + dy
            x1, y1, x2, y2 = clamp_window(
                cx - radius,
                cy - radius,
                cx + radius + 1,
                cy + radius + 1,
                w,
                h,
            )

            dot_area = int(np.count_nonzero(junction_binary[y1:y2, x1:x2] > 0))
            best_area = max(best_area, dot_area)

    return best_area >= PLAIN_CROSSING_DOT_AREA_MIN


# Rileva incroci ortogonali senza pallino di giunzione.
# Nota: questa euristica resta disponibile dietro flag, ma la convenzione
# principale della pipeline e' conservativa: un incrocio plain e' un nodo,
# mentre solo una gobba esplicita indica non-connessione.
def detect_plain_wire_crossings(
    skeleton_binary: np.ndarray,
    labels: np.ndarray,
    junction_binary: np.ndarray | None,
):
    """
    Rileva incroci piani che non devono essere cortocircuitati.

    Cerca geometrie a quattro direzioni nello skeleton e scarta i casi con
    pallino/nodo pieno nella maschera di supporto.
    """
    # Usiamo lo skeleton a un pixel per testare la geometria reale
    # dell'incrocio. La maschera piu' spessa serve solo a capire se esiste un
    # pallino pieno: usarla per i run direzionali trasformerebbe curve strette
    # o stub in falsi incroci a quattro vie.
    binary = np.where(skeleton_binary > 0, 1, 0).astype(np.uint8)
    h, w = binary.shape[:2]
    candidates = []

    run = PLAIN_CROSSING_MIN_RUN
    min_pixels = PLAIN_CROSSING_MIN_PIXELS_PER_DIRECTION

    for y in range(run, h - run):
        for x in range(run, w - run):
            if binary[y, x] == 0:
                continue

            source_label = nearest_split_label(labels, x, y, radius=3)
            if source_label is None:
                continue

            left = count_run(binary, x, y, -1, 0, run)
            right = count_run(binary, x, y, 1, 0, run)
            up = count_run(binary, x, y, 0, -1, run)
            down = count_run(binary, x, y, 0, 1, run)

            if min(left, right, up, down) < min_pixels:
                continue

            if has_filled_junction_dot(junction_binary, x, y):
                continue

            candidates.append({
                "x": int(x),
                "y": int(y),
                "label": int(source_label),
            })

    collapsed = []
    for cand in candidates:
        if any(abs(cand["x"] - prev["x"]) <= 5 and abs(cand["y"] - prev["y"]) <= 5 for prev in collapsed):
            continue
        collapsed.append(cand)

    return collapsed


def load_crossing_ink_binary(
    wire_extraction: dict,
    fallback_binary: np.ndarray | None,
):
    """
    Carica l'inchiostro originale, prima delle dilatazioni dello step 04.

    Nella maschera filtered due diagonali spesse riempiono naturalmente il
    centro della X e sembrano un pallino. La masked gray conserva invece la
    differenza fra la semplice sovrapposizione dei tratti e una giunzione
    esplicitamente marcata.
    """
    path = wire_extraction.get("masked_gray_path")
    if path:
        gray = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
        if gray is not None:
            _, ink_binary = cv2.threshold(
                gray,
                0,
                255,
                cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
            )
            return ink_binary

    return fallback_binary


def local_radial_split_branches(
    skeleton_binary: np.ndarray,
    x: int,
    y: int,
    cut_half_size: int,
    probe_distance: int,
):
    """
    Restituisce i rami che escono radialmente da uno split locale.

    Ogni ramo contiene la label locale e un versore diretto dal centro verso
    l'esterno. Non assumiamo pendenze orizzontali, verticali o a 45 gradi.
    """
    h, w = skeleton_binary.shape[:2]
    roi_margin = int(probe_distance) + int(cut_half_size) + 14
    roi_x1, roi_y1, roi_x2, roi_y2 = clamp_window(
        int(x) - roi_margin,
        int(y) - roi_margin,
        int(x) + roi_margin + 1,
        int(y) + roi_margin + 1,
        w,
        h,
    )
    cut_skeleton = skeleton_binary[roi_y1:roi_y2, roi_x1:roi_x2].copy()
    local_x = int(x) - int(roi_x1)
    local_y = int(y) - int(roi_y1)

    cut_x1, cut_y1, cut_x2, cut_y2 = clamp_window(
        local_x - int(cut_half_size),
        local_y - int(cut_half_size),
        local_x + int(cut_half_size) + 1,
        local_y + int(cut_half_size) + 1,
        cut_skeleton.shape[1],
        cut_skeleton.shape[0],
    )
    cut_skeleton[cut_y1:cut_y2, cut_x1:cut_x2] = 0

    _, split_labels, _, _ = cv2.connectedComponentsWithStats(
        np.where(cut_skeleton > 0, 1, 0).astype(np.uint8),
        connectivity=8,
    )
    yy, xx = np.indices(split_labels.shape)
    dx = xx.astype(np.float32) - float(local_x)
    dy = yy.astype(np.float32) - float(local_y)
    radius = np.hypot(dx, dy)
    inner_limit = float(np.sqrt(2.0) * (int(cut_half_size) + 1) + 2.0)
    outer_limit = float(int(probe_distance) + 10)
    branches = []

    for branch_label in np.unique(split_labels):
        if int(branch_label) <= 0:
            continue

        branch_mask = (
            (split_labels == int(branch_label))
            & (radius >= float(int(cut_half_size) + 1))
            & (radius <= outer_limit)
        )
        branch_pixels = int(np.count_nonzero(branch_mask))
        if branch_pixels < int(RADIAL_CROSSING_MIN_BRANCH_PIXELS):
            continue

        branch_radii = radius[branch_mask]
        if (
            float(np.min(branch_radii)) > inner_limit
            or float(np.max(branch_radii)) < float(probe_distance)
        ):
            continue

        direction_mask = branch_mask & (
            radius >= float(max(int(cut_half_size) + 2, int(probe_distance) // 2))
        )
        mean_dx = float(np.mean(dx[direction_mask]))
        mean_dy = float(np.mean(dy[direction_mask]))
        norm = float(np.hypot(mean_dx, mean_dy))
        if norm <= 1e-6:
            continue

        branches.append({
            "label": int(branch_label),
            "direction": [mean_dx / norm, mean_dy / norm],
            "pixels": branch_pixels,
        })

    return branches


def pair_opposite_radial_branches(branches: list[dict]):
    """
    Accoppia quattro rami scegliendo le due continuazioni piu' rettilinee.

    Lo split viene accettato solo se entrambi i tratti hanno direzioni
    opposte e i due assi risultanti non sono quasi paralleli.
    """
    if len(branches) != 4:
        return None

    directions = [
        np.asarray(branch["direction"], dtype=np.float64)
        for branch in branches
    ]
    pairings = (
        ((0, 1), (2, 3)),
        ((0, 2), (1, 3)),
        ((0, 3), (1, 2)),
    )
    best_pairs = min(
        pairings,
        key=lambda pairs: sum(
            float(np.dot(directions[index_a], directions[index_b]))
            for index_a, index_b in pairs
        ),
    )
    opposite_scores = [
        float(np.dot(directions[index_a], directions[index_b]))
        for index_a, index_b in best_pairs
    ]
    if any(
        score > float(RADIAL_CROSSING_OPPOSITE_DOT_MAX)
        for score in opposite_scores
    ):
        return None

    first_axis = directions[best_pairs[0][0]]
    second_axis = directions[best_pairs[1][0]]
    if abs(float(np.dot(first_axis, second_axis))) > float(RADIAL_CROSSING_AXIS_DOT_MAX):
        return None

    return [
        [int(index_a), int(index_b)]
        for index_a, index_b in best_pairs
    ]


def detect_radial_wire_crossings(
    skeleton_binary: np.ndarray,
    labels: np.ndarray,
    junction_ink_binary: np.ndarray | None,
):
    """
    Rileva crossing a quattro rami con orientazione arbitraria e senza pallino.

    I pixel di diramazione vicini vengono prima raggruppati: una X spessa puo'
    infatti produrre piu' branchpoint adiacenti durante la skeletonizzazione.
    """
    binary = np.where(skeleton_binary > 0, 1, 0).astype(np.uint8)
    neighbor_kernel = np.ones((3, 3), dtype=np.uint8)
    neighbor_count = cv2.filter2D(binary, cv2.CV_16S, neighbor_kernel) - binary
    branch_seed = np.where((binary > 0) & (neighbor_count >= 3), 255, 0).astype(np.uint8)
    if not np.any(branch_seed):
        return []

    cluster_radius = int(RADIAL_CROSSING_CLUSTER_RADIUS)
    cluster_kernel = np.ones(
        (2 * cluster_radius + 1, 2 * cluster_radius + 1),
        dtype=np.uint8,
    )
    clustered_seed = cv2.dilate(branch_seed, cluster_kernel, iterations=1)
    cluster_count, cluster_labels, _, _ = cv2.connectedComponentsWithStats(
        clustered_seed,
        connectivity=8,
    )
    crossings = []

    for cluster_label in range(1, int(cluster_count)):
        seed_y, seed_x = np.where(
            (cluster_labels == int(cluster_label))
            & (branch_seed > 0)
        )
        if len(seed_x) == 0:
            continue

        x = int(round(float(np.mean(seed_x))))
        y = int(round(float(np.mean(seed_y))))
        source_label = nearest_split_label(labels, x, y, radius=8)
        if source_label is None:
            continue
        if has_filled_junction_dot(junction_ink_binary, x, y):
            continue

        branches = local_radial_split_branches(
            skeleton_binary,
            x,
            y,
            RADIAL_CROSSING_CUT_HALF_SIZE,
            PLAIN_CROSSING_PROBE_DISTANCE,
        )
        branch_pairs = pair_opposite_radial_branches(branches)
        if branch_pairs is None:
            continue

        crossings.append({
            "x": int(x),
            "y": int(y),
            "label": int(source_label),
            "branch_directions": [
                list(branch["direction"])
                for branch in branches
            ],
            "branch_pairs": branch_pairs,
        })

    return crossings

def labels_with_multi_terminal_self_short(
    terminals: list[dict],
    terminal_match_debug: dict,
):
    """Trova label che contengono due o piu' terminali dello stesso componente."""
    by_component_and_label = {}

    for term in terminals:
        matched_label = terminal_match_debug.get(term["terminal_id"], {}).get("matched_label")
        if matched_label is None:
            continue

        class_name = normalize_class_name(term.get("component_class_name"))
        if class_name in PLAIN_CROSSING_SELF_SHORT_EXCLUDED_CLASSES:
            continue

        instance_id = term.get("instance_id")
        if instance_id is None:
            continue

        key = (str(instance_id), int(matched_label))
        by_component_and_label.setdefault(key, set()).add(term["terminal_id"])

    return {
        int(label)
        for (_, label), terminal_ids in by_component_and_label.items()
        if len(terminal_ids) >= 2
    }

def nearest_split_label(split_labels: np.ndarray, x: int, y: int, radius: int = 6):
    """Trova la nuova label piu' vicina a un punto dopo uno split locale."""
    h, w = split_labels.shape[:2]
    window = clamp_window(x - radius, y - radius, x + radius + 1, y + radius + 1, w, h)
    x1, y1, x2, y2 = window
    roi = split_labels[y1:y2, x1:x2]
    ys, xs = np.where(roi > 0)

    if len(xs) == 0:
        return None

    abs_xs = xs + x1
    abs_ys = ys + y1
    d2 = (abs_xs - float(x)) ** 2 + (abs_ys - float(y)) ** 2
    best_idx = int(np.argmin(d2))
    return int(split_labels[int(abs_ys[best_idx]), int(abs_xs[best_idx])])


def has_four_way_split_support(
    skeleton_binary: np.ndarray,
    x: int,
    y: int,
    cut_half_width: int,
    cut_half_height: int,
    probe_distance: int,
):
    """
    Accetta uno split plain solo se, dopo un taglio locale, restano quattro
    rami reali attorno al crossing. Cosi' evitiamo di spezzare nodi pieni o
    T-junction che il detector grezzo puo' scambiare per incroci.
    """
    branch_labels = local_split_branch_labels(
        skeleton_binary,
        x,
        y,
        cut_half_width,
        cut_half_height,
        probe_distance,
    )
    if any(label is None for label in branch_labels):
        return False

    return len({int(label) for label in branch_labels}) >= 2

def split_bridge_labels(
    label_to_terminal_ids: dict,
    terminals: list[dict],
    terminal_match_debug: dict,
    skeleton_binary: np.ndarray,
    labels: np.ndarray,
    wire_extraction: dict | None = None,
):
    """
    Divide gruppi di terminali quando una label contiene crossing o ponticelli.

    E' uno degli step piu' delicati: parte dalle label gia' raggruppate e prova
    a separare solo le geometrie che hanno evidenza locale sufficiente.
    """
    junction_binary = load_junction_support_binary(wire_extraction or {})
    enable_thick_hump_detection = is_blue_wire_style(wire_extraction or {}, junction_binary)
    raw_bridges = filter_micro_bridge_candidates(
        detect_wire_bridges(
            skeleton_binary,
            labels,
            junction_binary,
            enable_thick_hump_detection=enable_thick_hump_detection,
            enable_skeleton_hump_detection=True,
        ),
        label_to_terminal_ids,
        terminals,
        terminal_match_debug,
        skeleton_binary,
        allow_blue_diode_micro=enable_thick_hump_detection,
    )
    bridge_labels = {int(bridge["label"]) for bridge in raw_bridges}
    self_short_labels = labels_with_multi_terminal_self_short(
        terminals,
        terminal_match_debug,
    )
    crossing_ink_binary = load_crossing_ink_binary(
        wire_extraction or {},
        junction_binary,
    )

    # Nello stile blu/circuitstoday-like un incrocio semplice e' un nodo:
    # separiamo solo una gobba esplicita. Sugli altri stili manteniamo il
    # comportamento storico per non muovere immagini gia' validate.
    plain_crossings = []
    radial_crossings = []
    if PLAIN_CROSSING_SPLIT_ENABLE and not enable_thick_hump_detection:
        plain_crossings = [
            crossing
            for crossing in detect_plain_wire_crossings(skeleton_binary, labels, junction_binary)
            if int(crossing["label"]) in self_short_labels
            and int(crossing["label"]) not in bridge_labels
            and has_four_way_split_support(
                skeleton_binary,
                int(crossing["x"]),
                int(crossing["y"]),
                PLAIN_CROSSING_CUT_HALF_WIDTH,
                PLAIN_CROSSING_CUT_HALF_HEIGHT,
                PLAIN_CROSSING_PROBE_DISTANCE,
            )
        ]
        radial_crossings = [
            crossing
            for crossing in detect_radial_wire_crossings(
                skeleton_binary,
                labels,
                crossing_ink_binary,
            )
            if int(crossing["label"]) not in bridge_labels
            and len(
                set(label_to_terminal_ids.get(int(crossing["label"]), []))
            ) >= int(RADIAL_CROSSING_MIN_TERMINALS)
        ]

    split_points = []
    for bridge in raw_bridges:
        split_points.append({
            **bridge,
            "split_kind": "bridge_hump",
            "cut_half_width": int(bridge.get("cut_half_width", BRIDGE_CUT_HALF_WIDTH)),
            "cut_half_height": int(bridge.get("cut_half_height", BRIDGE_CUT_HALF_HEIGHT)),
            "probe_distance": BRIDGE_PROBE_DISTANCE,
        })

    for crossing in plain_crossings:
        split_points.append({
            **crossing,
            "split_kind": "plain_crossing_without_dot",
            "cut_half_width": PLAIN_CROSSING_CUT_HALF_WIDTH,
            "cut_half_height": PLAIN_CROSSING_CUT_HALF_HEIGHT,
            "probe_distance": PLAIN_CROSSING_PROBE_DISTANCE,
        })

    for crossing in radial_crossings:
        split_points.append({
            **crossing,
            "split_kind": "radial_crossing_without_dot",
            "cut_half_width": RADIAL_CROSSING_CUT_HALF_SIZE,
            "cut_half_height": RADIAL_CROSSING_CUT_HALF_SIZE,
            "probe_distance": PLAIN_CROSSING_PROBE_DISTANCE,
        })

    if not split_points:
        return label_to_terminal_ids

    split_labels_to_rebuild = {int(point["label"]) for point in split_points}
    if not split_labels_to_rebuild:
        return label_to_terminal_ids

    cut_skeleton = skeleton_binary.copy()
    h, w = cut_skeleton.shape[:2]
    for split_point in split_points:
        x = int(split_point["x"])
        y = int(split_point["y"])
        cut_half_width = int(split_point["cut_half_width"])
        cut_half_height = int(split_point["cut_half_height"])
        x1, y1, x2, y2 = clamp_window(
            x - cut_half_width,
            y - cut_half_height,
            x + cut_half_width + 1,
            y + cut_half_height + 1,
            w,
            h,
        )
        cut_skeleton[y1:y2, x1:x2] = 0

    _, split_labels, _, _ = cv2.connectedComponentsWithStats(cut_skeleton, connectivity=8)

    union_find = LabelUnionFind()

    for split_point in split_points:
        x = int(split_point["x"])
        y = int(split_point["y"])
        probe_distance = int(split_point["probe_distance"])
        if split_point.get("split_kind") == "radial_crossing_without_dot":
            branch_labels = []
            for direction_x, direction_y in split_point["branch_directions"]:
                probe_x = int(round(float(x) + float(direction_x) * probe_distance))
                probe_y = int(round(float(y) + float(direction_y) * probe_distance))
                branch_labels.append(
                    nearest_split_label(split_labels, probe_x, probe_y, radius=4)
                )

            for index_a, index_b in split_point["branch_pairs"]:
                union_find.union(
                    branch_labels[int(index_a)],
                    branch_labels[int(index_b)],
                )
            continue

        top_label = nearest_split_label(split_labels, x, y - probe_distance)
        bottom_label = nearest_split_label(split_labels, x, y + probe_distance)
        left_label = nearest_split_label(split_labels, x - probe_distance, y)
        right_label = nearest_split_label(split_labels, x + probe_distance, y)

        union_find.union(top_label, bottom_label)
        union_find.union(left_label, right_label)

    terminal_by_id = {term["terminal_id"]: term for term in terminals}
    split_groups = {}

    for original_label, terminal_ids in label_to_terminal_ids.items():
        if int(original_label) not in split_labels_to_rebuild:
            split_groups[(int(original_label), 0)] = list(terminal_ids)
            continue

        for terminal_id in terminal_ids:
            term = terminal_by_id.get(terminal_id)
            if term is None:
                continue

            anchor_x, anchor_y = get_terminal_split_anchor(
                term,
                terminal_match_debug,
            )

            split_label = nearest_split_label(
                split_labels,
                anchor_x,
                anchor_y,
                radius=max(
                    TERMINAL_SQUARE_FALLBACK_RADIUS,
                    BRIDGE_PROBE_DISTANCE,
                    PLAIN_CROSSING_PROBE_DISTANCE,
                ),
            )

            if split_label is None:
                matched_label = terminal_match_debug.get(terminal_id, {}).get("matched_label")
                split_key = ("unresolved", int(original_label), int(matched_label or original_label))
            else:
                split_key = ("split", int(original_label), union_find.find(split_label))

            split_groups.setdefault(split_key, []).append(terminal_id)

    final_groups = []
    handled_original_labels = set()

    for original_label, terminal_ids in label_to_terminal_ids.items():
        original_label = int(original_label)
        if original_label not in split_labels_to_rebuild:
            continue

        related_groups = [
            group_terminal_ids
            for key, group_terminal_ids in split_groups.items()
            if isinstance(key, tuple)
            and len(key) >= 2
            and key[0] in {"split", "unresolved"}
            and int(key[1]) == original_label
        ]

        if not related_groups:
            final_groups.append(list(terminal_ids))
            handled_original_labels.add(original_label)
            continue

        related_groups = merge_opamp_aux_singleton_groups(related_groups, terminal_by_id)
        creates_singleton = any(len(set(group)) < 2 for group in related_groups)
        allow_singleton = allow_singleton_split_for_label(
            original_label,
            related_groups,
            split_points,
            terminal_by_id,
        )

        if creates_singleton and not allow_singleton:
            final_groups.append(list(terminal_ids))
        else:
            final_groups.extend(related_groups)

        handled_original_labels.add(original_label)

    for key, terminal_ids in split_groups.items():
        if (
            isinstance(key, tuple)
            and len(key) >= 2
            and key[0] in {"split", "unresolved"}
            and int(key[1]) in handled_original_labels
        ):
            continue

        final_groups.append(terminal_ids)

    final_groups = split_ambiguous_micro_bridge_groups(
        final_groups,
        split_points,
        terminals,
        terminal_match_debug,
    )

    return {
        next_label: sorted(set(terminal_ids))
        for next_label, terminal_ids in enumerate(final_groups, start=1)
    }


def _foreground_count(binary: np.ndarray, x1: int, y1: int, x2: int, y2: int):
    """Conta i pixel dello skeleton in una finestra limitata all'immagine."""
    h, w = binary.shape[:2]
    x1, y1, x2, y2 = clamp_window(x1, y1, x2, y2, w, h)
    return int(np.count_nonzero(binary[y1:y2, x1:x2] > 0))


def _has_looped_crossing_signature(skeleton_binary: np.ndarray, x: int, y: int):
    """Riconosce un crossover con arco laterale e sottile tratto spurio centrale."""
    binary = np.where(skeleton_binary > 0, 1, 0).astype(np.uint8)
    horizontal_left = _foreground_count(binary, x - 30, y - 2, x - 5, y + 3)
    horizontal_right = _foreground_count(binary, x + 5, y - 2, x + 30, y + 3)
    vertical_up = _foreground_count(binary, x - 2, y - 30, x + 3, y - 5)
    vertical_down = _foreground_count(binary, x - 2, y + 5, x + 3, y + 30)
    if min(horizontal_left, horizontal_right, vertical_up, vertical_down) < 8:
        return False

    left_upper = _foreground_count(binary, x - 30, y - 20, x - 6, y - 5)
    left_lower = _foreground_count(binary, x - 30, y + 5, x - 6, y + 20)
    right_upper = _foreground_count(binary, x + 6, y - 20, x + 30, y - 5)
    right_lower = _foreground_count(binary, x + 6, y + 5, x + 30, y + 20)

    # Un nodo ortogonale normale non contiene due archi sullo stesso lato.
    # La doppia diagonale e' invece l'evidenza grafica del ponticello.
    return (
        min(left_upper, left_lower) >= 4
        or min(right_upper, right_lower) >= 4
    )


def split_looped_orthogonal_crossing_groups(
    label_to_terminal_ids: dict,
    terminals: list[dict],
    skeleton_binary: np.ndarray,
):
    """Divide solo gruppi a quattro terminali sostenuti da un crossover ad arco."""
    terminal_by_id = {term["terminal_id"]: term for term in terminals}
    output_groups = []

    for terminal_ids in label_to_terminal_ids.values():
        unique_ids = sorted(set(terminal_ids))
        split_pairs = None
        if len(unique_ids) == 4:
            for vertical_ids in combinations(unique_ids, 2):
                vertical_terms = [terminal_by_id.get(item) for item in vertical_ids]
                if any(term is None for term in vertical_terms):
                    continue
                if {
                    str(term.get("relative_position") or "").lower()
                    for term in vertical_terms
                } != {"top", "bottom"}:
                    continue

                remaining_ids = [item for item in unique_ids if item not in vertical_ids]
                horizontal_terms = [terminal_by_id.get(item) for item in remaining_ids]
                if any(term is None for term in horizontal_terms):
                    continue
                if {
                    str(term.get("relative_position") or "").lower()
                    for term in horizontal_terms
                } != {"left", "right"}:
                    continue

                vertical_x_delta = abs(float(vertical_terms[0]["x"]) - float(vertical_terms[1]["x"]))
                vertical_y_gap = abs(float(vertical_terms[0]["y"]) - float(vertical_terms[1]["y"]))
                horizontal_y_delta = abs(float(horizontal_terms[0]["y"]) - float(horizontal_terms[1]["y"]))
                horizontal_x_gap = abs(float(horizontal_terms[0]["x"]) - float(horizontal_terms[1]["x"]))
                if vertical_x_delta > 12 or horizontal_y_delta > 12:
                    continue
                if vertical_y_gap < 40 or horizontal_x_gap < 40:
                    continue

                crossing_x = int(round(sum(float(term["x"]) for term in vertical_terms) / 2.0))
                crossing_y = int(round(sum(float(term["y"]) for term in horizontal_terms) / 2.0))
                horizontal_xs = [float(term["x"]) for term in horizontal_terms]
                vertical_ys = [float(term["y"]) for term in vertical_terms]
                if not min(horizontal_xs) < crossing_x < max(horizontal_xs):
                    continue
                if not min(vertical_ys) < crossing_y < max(vertical_ys):
                    continue
                if not _has_looped_crossing_signature(skeleton_binary, crossing_x, crossing_y):
                    continue

                split_pairs = (list(vertical_ids), remaining_ids)
                break

        if split_pairs is None:
            output_groups.append(unique_ids)
        else:
            output_groups.extend(split_pairs)

    return {
        index: group
        for index, group in enumerate(output_groups, start=1)
    }


def merge_opamp_aux_singleton_groups(related_groups: list[list[str]], terminal_by_id: dict):
    groups = [list(group) for group in related_groups]
    if len(groups) < 2:
        return groups

    aux_singletons = []
    non_singletons = []
    for idx, group in enumerate(groups):
        unique_ids = sorted(set(group))
        if len(unique_ids) == 1:
            term = terminal_by_id.get(unique_ids[0])
            class_name = normalize_class_name((term or {}).get("component_class_name"))
            term_name = str((term or {}).get("name") or "").strip().lower()
            if class_name == "operational_amplifier" and term_name.startswith("aux"):
                aux_singletons.append(idx)
                continue
        non_singletons.append(idx)

    if not aux_singletons or not non_singletons:
        return groups

    target_idx = max(non_singletons, key=lambda idx: len(set(groups[idx])))
    merged_target = list(groups[target_idx])
    for idx in aux_singletons:
        merged_target.extend(groups[idx])
    groups[target_idx] = merged_target

    return [
        group
        for idx, group in enumerate(groups)
        if idx not in aux_singletons
    ]


def split_ambiguous_micro_bridge_groups(
    terminal_groups: list[list[str]],
    split_points: list[dict],
    terminals: list[dict],
    terminal_match_debug: dict,
):
    micro_points = [
        point
        for point in split_points
        if point.get("bridge_style") in {"micro_gap", "offset_gap"}
    ]
    if not micro_points:
        return terminal_groups

    terminal_by_id = {term["terminal_id"]: term for term in terminals}
    groups = [list(group) for group in terminal_groups]

    for point in micro_points:
        next_groups = []
        for terminal_ids in groups:
            if not any(
                int(terminal_match_debug.get(terminal_id, {}).get("matched_label") or -1)
                == int(point["label"])
                for terminal_id in terminal_ids
            ):
                next_groups.append(terminal_ids)
                continue

            split_groups = split_group_by_micro_bridge_geometry(
                terminal_ids,
                terminal_by_id,
                point,
            )
            next_groups.extend(split_groups)
        groups = next_groups

    return groups


def allow_singleton_split_for_label(
    original_label: int,
    related_groups: list[list[str]],
    split_points: list[dict],
    terminal_by_id: dict | None = None,
):
    if not has_allowed_bridge_group_sizes({
        idx: list(group)
        for idx, group in enumerate(related_groups)
    }):
        return False

    label_points = [
        point
        for point in split_points
        if int(point.get("label", -1)) == int(original_label)
    ]
    if not label_points:
        return False

    hump_points = [
        point
        for point in label_points
        if point.get("split_kind") == "bridge_hump"
        and point.get("bridge_style") == "hump"
    ]
    micro_points = [
        point
        for point in label_points
        if point.get("bridge_style") in {"micro_gap", "offset_gap"}
    ]
    if not hump_points:
        return bool(micro_points)
    # Uno split che crea singleton e' gia' una situazione delicata.
    # Se sullo stesso label compaiono piu' candidati hump, il detector non sta
    # fornendo un ancoraggio univoco: trattiamo il caso come ambiguo e
    # preferiamo mantenere il nodo originale invece di spezzarlo.
    if len(hump_points) != 1:
        return False

    singleton_groups = [
        list(group)
        for group in related_groups
        if len(set(group)) == 1
    ]
    if not singleton_groups:
        return True
    if terminal_by_id is None:
        return False

    max_hump_distance = float(BRIDGE_PROBE_DISTANCE) * 2.0

    for group in singleton_groups:
        terminal_id = str(group[0])
        term = terminal_by_id.get(terminal_id)
        if term is None:
            return False

        try:
            tx = float(term["x"])
            ty = float(term["y"])
        except (KeyError, TypeError, ValueError):
            return False

        nearest_hump = min(
            float(np.hypot(tx - float(point["x"]), ty - float(point["y"])))
            for point in hump_points
        )
        # Se il candidato hump cade quasi sul terminale singleton, e' piu'
        # probabile che stia leggendo il capolinea del ramo come un ponte.
        # In quel caso preferiamo non spezzare il net.
        if nearest_hump < float(BRIDGE_SINGLETON_MIN_HUMP_DISTANCE):
            return False
        if nearest_hump > max_hump_distance:
            return False

        if micro_points:
            nearest_micro = min(
                float(np.hypot(tx - float(point["x"]), ty - float(point["y"])))
                for point in micro_points
            )
            if nearest_micro <= nearest_hump + 4.0:
                return False

    return True


def split_group_by_micro_bridge_geometry(
    terminal_ids: list[str],
    terminal_by_id: dict,
    point: dict,
):
    if not any(
        normalize_class_name((terminal_by_id.get(terminal_id) or {}).get("component_class_name")) == "diode"
        for terminal_id in terminal_ids
    ):
        return [terminal_ids]

    horizontal_ids = []
    vertical_ids = []
    # La partizione usa la banda orizzontale, ma entrambe le coordinate del
    # candidato restano validate come nel comportamento storico.
    _, py = float(point["x"]), float(point["y"])

    for terminal_id in terminal_ids:
        term = terminal_by_id.get(terminal_id)
        if term is None:
            vertical_ids.append(terminal_id)
            continue

        try:
            _, ty = float(term["x"]), float(term["y"])
        except (KeyError, TypeError, ValueError):
            vertical_ids.append(terminal_id)
            continue

        if abs(ty - py) <= MICRO_BRIDGE_TERMINAL_HORIZONTAL_BAND:
            horizontal_ids.append(terminal_id)
        else:
            vertical_ids.append(terminal_id)

    if len(set(horizontal_ids)) >= 2 and len(set(vertical_ids)) >= 2:
        return [horizontal_ids, vertical_ids]

    return [terminal_ids]


def filter_micro_bridge_candidates(
    bridges: list[dict],
    label_to_terminal_ids: dict,
    terminals: list[dict],
    terminal_match_debug: dict,
    skeleton_binary: np.ndarray,
    allow_blue_diode_micro: bool = False,
):
    filtered = []
    micro_by_label = {}

    for bridge in bridges:
        if bridge.get("bridge_style") != "micro_gap":
            filtered.append(bridge)
            continue

        label = int(bridge["label"])
        if label_contains_class(label, terminals, terminal_match_debug, {"diode"}):
            if int(bridge.get("max_side_gap", 0)) >= 3:
                filtered.append(bridge)
            elif allow_blue_diode_micro and int(bridge.get("max_side_gap", 0)) >= 1:
                micro_by_label.setdefault(label, []).append(bridge)
            continue

        if int(bridge.get("max_side_gap", 0)) >= 1:
            micro_by_label.setdefault(label, []).append(bridge)

    for label, label_bridges in micro_by_label.items():
        if allow_blue_diode_micro:
            row_clusters = build_horizontal_micro_bridge_clusters(label_bridges)
            promoted = []
            for cluster in row_clusters:
                if not micro_bridge_points_create_valid_split(
                    int(label),
                    cluster,
                    label_to_terminal_ids,
                    terminals,
                    skeleton_binary,
                ):
                    continue
                promoted_candidate = promote_offset_bridge_cluster(cluster)
                if promoted_candidate is not None:
                    promoted.append(promoted_candidate)
            if not promoted:
                for cluster_group in build_aligned_horizontal_micro_bridge_cluster_groups(row_clusters):
                    cluster_points = [
                        point
                        for cluster in cluster_group
                        for point in cluster
                    ]
                    if not micro_bridge_points_create_valid_split(
                        int(label),
                        cluster_points,
                        label_to_terminal_ids,
                        terminals,
                        skeleton_binary,
                        terminal_match_debug=terminal_match_debug,
                    ):
                        continue
                    for cluster in cluster_group:
                        promoted_candidate = promote_offset_bridge_cluster(cluster)
                        if promoted_candidate is not None:
                            promoted.append(promoted_candidate)
            if promoted:
                filtered.extend(promoted)
                continue

        clusters = build_vertical_micro_bridge_clusters(label_bridges)
        if not clusters:
            continue

        cluster_points = []
        for cluster in clusters:
            cluster_points.extend(cluster)

        selected_points = select_micro_bridge_points_for_valid_split(
            int(label),
            cluster_points,
            label_to_terminal_ids,
            terminals,
            skeleton_binary,
            terminal_match_debug=terminal_match_debug,
        )
        if selected_points:
            filtered.extend(selected_points)

    return filtered


def build_vertical_micro_bridge_clusters(bridges: list[dict]):
    clusters = []
    for bridge in sorted(bridges, key=lambda item: (int(item["x"]), int(item["y"]))):
        placed = False
        for cluster in clusters:
            avg_x = sum(int(item["x"]) for item in cluster) / float(len(cluster))
            if abs(int(bridge["x"]) - avg_x) <= MICRO_BRIDGE_COLUMN_X_TOL:
                cluster.append(bridge)
                placed = True
                break
        if not placed:
            clusters.append([bridge])

    valid_clusters = []
    for cluster in clusters:
        cluster = trim_micro_bridge_cluster_end_outliers(cluster)
        if len(cluster) < 2:
            continue
        ys = [int(item["y"]) for item in cluster]
        if max(ys) - min(ys) < MICRO_BRIDGE_COLUMN_MIN_Y_SPAN and len(cluster) < 3:
            continue
        valid_clusters.append(cluster)

    return valid_clusters


def build_horizontal_micro_bridge_clusters(
    bridges: list[dict],
    min_points: int = OFFSET_BRIDGE_ROW_MIN_POINTS,
    min_x_span: int = OFFSET_BRIDGE_ROW_MIN_X_SPAN,
):
    if not bridges:
        return []

    sorted_points = sorted(bridges, key=lambda item: (int(item["y"]), int(item["x"])))
    row_groups: list[list[dict]] = []
    current: list[dict] = []

    for bridge in sorted_points:
        if not current:
            current = [bridge]
            continue

        prev = current[-1]
        same_row = abs(int(bridge["y"]) - int(prev["y"])) <= OFFSET_BRIDGE_ROW_Y_TOL
        close_x = int(bridge["x"]) - int(prev["x"]) <= OFFSET_BRIDGE_ROW_MAX_X_GAP
        if same_row and close_x:
            current.append(bridge)
            continue

        row_groups.append(current)
        current = [bridge]

    if current:
        row_groups.append(current)

    valid_groups = []
    for group in row_groups:
        if len(group) < int(min_points):
            continue
        xs = [int(item["x"]) for item in group]
        if max(xs) - min(xs) < int(min_x_span):
            continue
        valid_groups.append(group)

    return valid_groups


def build_aligned_horizontal_micro_bridge_cluster_groups(row_clusters: list[list[dict]]):
    cluster_groups = []

    def cluster_y(cluster: list[dict]):
        return sum(int(point["y"]) for point in cluster) / float(len(cluster))

    for cluster in sorted(row_clusters, key=lambda item: (cluster_y(item), int(item[0]["x"]))):
        avg_y = cluster_y(cluster)
        placed = False
        for group in cluster_groups:
            group_points = [point for group_cluster in group for point in group_cluster]
            group_y = sum(int(point["y"]) for point in group_points) / float(len(group_points))
            if abs(avg_y - group_y) <= OFFSET_BRIDGE_ROW_Y_TOL:
                group.append(cluster)
                placed = True
                break
        if not placed:
            cluster_groups.append([cluster])

    return [
        group
        for group in cluster_groups
        if len(group) >= 2
    ]


def promote_offset_bridge_cluster(cluster: list[dict]):
    if not cluster:
        return None

    xs = sorted(int(point["x"]) for point in cluster)
    ys = sorted(int(point["y"]) for point in cluster)
    mid_idx = len(xs) // 2
    x = xs[mid_idx]
    y = ys[mid_idx]
    return {
        "x": int(x),
        "y": int(y),
        "label": int(cluster[0]["label"]),
        "bridge_style": "offset_gap",
        "bridge_detector": "micro_offset",
        "hump_score": float(len(cluster)),
        "cluster_width": int(max(xs) - min(xs)),
        "cut_half_width": int(max(BRIDGE_CUT_HALF_WIDTH, ((max(xs) - min(xs)) // 2) + 2)),
        "cut_half_height": int(BRIDGE_CUT_HALF_HEIGHT),
    }


def has_allowed_bridge_group_sizes(groups: dict):
    sizes = sorted(len(set(group)) for group in groups.values())
    if len(sizes) < 2:
        return False
    if all(size >= 2 for size in sizes):
        return True

    singleton_count = sum(1 for size in sizes if size == 1)
    return singleton_count == 1 and all(size >= 2 for size in sizes if size != 1)


def trim_micro_bridge_cluster_end_outliers(cluster: list[dict]):
    trimmed = list(cluster)
    min_gap = max(20, BRIDGE_PROBE_DISTANCE * 2)

    while len(trimmed) >= 4:
        rows = {}
        for point in trimmed:
            rows.setdefault(int(point["y"]), []).append(point)
        unique_ys = sorted(rows)
        if len(unique_ys) < 2:
            break

        changed = False
        top_gap = unique_ys[1] - unique_ys[0]
        if top_gap >= min_gap and len(rows[unique_ys[0]]) == 1:
            trimmed = [point for point in trimmed if int(point["y"]) != unique_ys[0]]
            changed = True

        rows = {}
        for point in trimmed:
            rows.setdefault(int(point["y"]), []).append(point)
        unique_ys = sorted(rows)
        if len(unique_ys) < 2:
            break

        bottom_gap = unique_ys[-1] - unique_ys[-2]
        if bottom_gap >= min_gap and len(rows[unique_ys[-1]]) == 1:
            trimmed = [point for point in trimmed if int(point["y"]) != unique_ys[-1]]
            changed = True

        if not changed:
            break

    return trimmed


def micro_bridge_points_create_valid_split(
    label: int,
    points: list[dict],
    label_to_terminal_ids: dict,
    terminals: list[dict],
    skeleton_binary: np.ndarray,
    terminal_match_debug: dict | None = None,
):
    groups = build_micro_bridge_split_groups(
        label,
        points,
        label_to_terminal_ids,
        terminals,
        skeleton_binary,
        terminal_match_debug=terminal_match_debug,
    )
    if groups is None:
        return False

    return has_allowed_bridge_group_sizes(groups)


def select_micro_bridge_points_for_valid_split(
    label: int,
    points: list[dict],
    label_to_terminal_ids: dict,
    terminals: list[dict],
    skeleton_binary: np.ndarray,
    terminal_match_debug: dict | None = None,
):
    groups = build_micro_bridge_split_groups(
        label,
        points,
        label_to_terminal_ids,
        terminals,
        skeleton_binary,
        terminal_match_debug=terminal_match_debug,
    )
    if groups is None or not has_allowed_bridge_group_sizes(groups):
        return []

    if all(len(set(group)) >= 2 for group in groups.values()):
        return points

    best_points = []
    best_score = None
    row_segments = build_horizontal_micro_bridge_clusters(points, min_points=2, min_x_span=1)
    for segment in row_segments:
        segment_keys = {
            (int(point["x"]), int(point["y"]))
            for point in segment
        }
        remaining = [
            point
            for point in points
            if (int(point["x"]), int(point["y"])) not in segment_keys
        ]
        if not remaining:
            continue

        remaining_groups = build_micro_bridge_split_groups(
            label,
            remaining,
            label_to_terminal_ids,
            terminals,
            skeleton_binary,
            terminal_match_debug=terminal_match_debug,
        )
        if remaining_groups is None or not has_allowed_bridge_group_sizes(remaining_groups):
            continue
        if any(len(set(group)) < 2 for group in remaining_groups.values()):
            continue

        group_sizes = sorted(len(set(group)) for group in remaining_groups.values())
        score = (
            len(group_sizes),
            -max(group_sizes),
            -sum(size * size for size in group_sizes),
        )
        if best_score is None or score > best_score:
            best_points = remaining
            best_score = score

    return best_points or points


def build_micro_bridge_split_groups(
    label: int,
    points: list[dict],
    label_to_terminal_ids: dict,
    terminals: list[dict],
    skeleton_binary: np.ndarray,
    terminal_match_debug: dict | None = None,
):
    terminal_ids = label_to_terminal_ids.get(int(label), [])
    if len(set(terminal_ids)) < 4:
        return None

    terminal_by_id = {term["terminal_id"]: term for term in terminals}
    cut_skeleton = skeleton_binary.copy()
    h, w = cut_skeleton.shape[:2]
    for point in points:
        x = int(point["x"])
        y = int(point["y"])
        x1, y1, x2, y2 = clamp_window(
            x - BRIDGE_CUT_HALF_WIDTH,
            y - BRIDGE_CUT_HALF_HEIGHT,
            x + BRIDGE_CUT_HALF_WIDTH + 1,
            y + BRIDGE_CUT_HALF_HEIGHT + 1,
            w,
            h,
        )
        cut_skeleton[y1:y2, x1:x2] = 0

    _, split_labels, _, _ = cv2.connectedComponentsWithStats(cut_skeleton, connectivity=8)
    union_find = LabelUnionFind()

    for point in points:
        x = int(point["x"])
        y = int(point["y"])
        top_label = nearest_split_label(split_labels, x, y - BRIDGE_PROBE_DISTANCE)
        bottom_label = nearest_split_label(split_labels, x, y + BRIDGE_PROBE_DISTANCE)
        left_label = nearest_split_label(split_labels, x - BRIDGE_PROBE_DISTANCE, y)
        right_label = nearest_split_label(split_labels, x + BRIDGE_PROBE_DISTANCE, y)
        union_find.union(top_label, bottom_label)
        union_find.union(left_label, right_label)

    groups = {}
    for terminal_id in terminal_ids:
        term = terminal_by_id.get(terminal_id)
        if term is None:
            continue
        anchor_x, anchor_y = get_terminal_split_anchor(
            term,
            terminal_match_debug,
        )
        split_label = nearest_split_label(
            split_labels,
            anchor_x,
            anchor_y,
            radius=max(
                TERMINAL_SQUARE_FALLBACK_RADIUS,
                BRIDGE_PROBE_DISTANCE,
                PLAIN_CROSSING_PROBE_DISTANCE,
            ),
        )
        if split_label is None:
            return None
        groups.setdefault(union_find.find(split_label), []).append(terminal_id)

    return groups


def get_terminal_split_anchor(
    term: dict,
    terminal_match_debug: dict | None = None,
):
    if terminal_match_debug is not None:
        match = terminal_match_debug.get(term.get("terminal_id"), {})
        snap_point = match.get("snap_point")
        if (
            isinstance(snap_point, (list, tuple))
            and len(snap_point) == 2
        ):
            try:
                return int(round(float(snap_point[0]))), int(round(float(snap_point[1])))
            except (TypeError, ValueError):
                pass

    return int(round(float(term["x"]))), int(round(float(term["y"])))


def label_contains_class(
    label: int,
    terminals: list[dict],
    terminal_match_debug: dict,
    class_names: set[str],
):
    wanted = {normalize_class_name(class_name) for class_name in class_names}
    for term in terminals:
        matched_label = terminal_match_debug.get(term["terminal_id"], {}).get("matched_label")
        if matched_label is None or int(matched_label) != int(label):
            continue
        if normalize_class_name(term.get("component_class_name")) in wanted:
            return True

    return False

def count_run(binary: np.ndarray, x: int, y: int, dx: int, dy: int, limit: int):
    """Conta i pixel consecutivi lungo una direzione entro il limite dato."""
    h, w = binary.shape[:2]
    count = 0
    cx = int(x) + int(dx)
    cy = int(y) + int(dy)

    while 0 <= cx < w and 0 <= cy < h and count < limit:
        if binary[cy, cx] == 0:
            break
        count += 1
        cx += int(dx)
        cy += int(dy)

    return count
