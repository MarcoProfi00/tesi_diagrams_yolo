import cv2
import numpy as np

from .config import TERMINAL_OUTWARD_OFFSET
from .geometry import geom_clamp_bbox_to_image


# Raggruppa indici vicini.
def _group_close_indices(indices, max_gap=1):
    if not indices:
        return []

    groups = [[indices[0]]]
    for idx in indices[1:]:
        if idx <= groups[-1][-1] + max_gap:
            groups[-1].append(idx)
        else:
            groups.append([idx])
    return groups


# Seleziona la coordinata di picco.
def _select_peak_coord(coords, scores, keep_ratio=0.58, min_score=4):
    if not coords or not scores:
        return None, {
            "max_score": 0,
            "keep_threshold": 0,
            "selected_run_start": None,
            "selected_run_end": None,
            "selected_run_length": 0,
        }

    max_score = max(int(score) for score in scores)
    if max_score <= 0:
        center_idx = len(coords) // 2
        return int(coords[center_idx]), {
            "max_score": int(max_score),
            "keep_threshold": 0,
            "selected_run_start": int(coords[center_idx]),
            "selected_run_end": int(coords[center_idx]),
            "selected_run_length": 1,
        }

    keep_threshold = max(int(min_score), int(round(float(max_score) * float(keep_ratio))))
    kept = [idx for idx, score in enumerate(scores) if int(score) >= keep_threshold]
    if not kept:
        best_idx = max(range(len(scores)), key=lambda idx: int(scores[idx]))
        return int(coords[best_idx]), {
            "max_score": int(max_score),
            "keep_threshold": int(keep_threshold),
            "selected_run_start": int(coords[best_idx]),
            "selected_run_end": int(coords[best_idx]),
            "selected_run_length": 1,
        }

    groups = _group_close_indices(kept, max_gap=2)
    best_group = max(
        groups,
        key=lambda group: (
            sum(int(scores[idx]) for idx in group),
            max(int(scores[idx]) for idx in group),
            len(group),
        ),
    )
    center_idx = int(round((best_group[0] + best_group[-1]) / 2.0))
    return int(coords[center_idx]), {
        "max_score": int(max_score),
        "keep_threshold": int(keep_threshold),
        "selected_run_start": int(coords[best_group[0]]),
        "selected_run_end": int(coords[best_group[-1]]),
        "selected_run_length": int(len(best_group)),
    }


# Find structured inner box.
def _find_structured_inner_box(binary, bbox, min_size, ratio_min, ratio_max, extent_min, prefer_square=False):
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)
    roi = binary[y1:y2 + 1, x1:x2 + 1]
    contours, _ = cv2.findContours(roi, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    best_box = None
    best_key = None
    for cnt in contours:
        bx, by, bw, bh = cv2.boundingRect(cnt)
        if bw < min_size or bh < min_size:
            continue

        ratio = bw / float(max(bh, 1))
        if not (float(ratio_min) <= ratio <= float(ratio_max)):
            continue

        area = float(cv2.contourArea(cnt))
        extent = area / float(max(bw * bh, 1))
        if extent < float(extent_min):
            continue

        square_penalty = abs(1.0 - ratio) if prefer_square else 0.0
        key = (
            float(square_penalty),
            -float(extent),
            abs(int(bw) - int(bh)),
            -int(min(bw, bh)),
        )
        if best_box is None or key < best_key:
            best_box = [float(x1 + bx), float(y1 + by), float(x1 + bx + bw - 1), float(y1 + by + bh - 1)]
            best_key = key

    return best_box


# Find circular holes.
def _find_circular_holes(binary, box, min_area=25.0, max_area=320.0):
    x1, y1, x2, y2 = [int(round(v)) for v in box]
    roi = binary[y1:y2 + 1, x1:x2 + 1]
    contours, _ = cv2.findContours(roi, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return []

    holes = []
    box_w = max(x2 - x1, 1)
    box_h = max(y2 - y1, 1)

    for cnt in contours:
        hx, hy, hw, hh = cv2.boundingRect(cnt)
        if hw < 6 or hh < 6 or hw > 26 or hh > 26:
            continue

        ratio = hw / float(max(hh, 1))
        if not (0.65 <= ratio <= 1.5):
            continue

        area = float(cv2.contourArea(cnt))
        if not (float(min_area) <= area <= float(max_area)):
            continue

        perimeter = float(cv2.arcLength(cnt, True))
        if perimeter <= 0.0:
            continue

        circularity = 4.0 * 3.141592653589793 * area / float(perimeter * perimeter)
        if circularity < 0.35:
            continue

        cx = float(x1 + hx + (hw / 2.0))
        cy = float(y1 + hy + (hh / 2.0))
        norm_x = (cx - float(x1)) / float(box_w)
        norm_y = (cy - float(y1)) / float(box_h)
        if not (0.10 <= norm_x <= 0.90 and 0.08 <= norm_y <= 0.92):
            continue

        radius = float(max(hw, hh) / 2.0)
        ring_metrics = _measure_meter_post_ring(binary, cx, cy, radius)

        holes.append({
            "cx": cx,
            "cy": cy,
            "width": int(hw),
            "height": int(hh),
            "area": float(area),
            "circularity": round(float(circularity), 4),
            **ring_metrics,
        })

    holes = sorted(
        holes,
        key=lambda hole: (
            float(hole.get("ring_score", -999.0)),
            float(hole.get("annulus_fill_ratio", 0.0)),
            -float(hole.get("center_fill_ratio", 1.0)),
            float(hole.get("circularity", 0.0)),
            float(hole.get("area", 0.0)),
        ),
        reverse=True,
    )

    selected = []
    for hole in holes:
        if all(
            abs(float(hole["cx"]) - float(other["cx"])) > 6.0
            or abs(float(hole["cy"]) - float(other["cy"])) > 6.0
            for other in selected
        ):
            selected.append(hole)
        if len(selected) == 6:
            break

    return selected


# Count roi nonzero.
def _count_roi_nonzero(roi, xa, ya, xb, yb):
    xa = max(0, int(round(xa)))
    ya = max(0, int(round(ya)))
    xb = min(roi.shape[1], int(round(xb)))
    yb = min(roi.shape[0], int(round(yb)))
    if xb <= xa or yb <= ya:
        return 0
    return int(cv2.countNonZero(roi[ya:yb, xa:xb]))

def _masked_fill_ratio(roi, mask):
    mask_area = int(cv2.countNonZero(mask))
    if mask_area <= 0:
        return 0.0
    masked = cv2.bitwise_and(roi, roi, mask=mask)
    return float(cv2.countNonZero(masked)) / float(mask_area)


def _measure_meter_post_ring(binary, cx, cy, radius):
    cx_i = int(round(float(cx)))
    cy_i = int(round(float(cy)))
    radius_i = max(5, int(round(float(radius))))

    pad = max(12, int(round(radius_i * 2.2)))
    xa = max(0, cx_i - pad)
    xb = min(binary.shape[1], cx_i + pad + 1)
    ya = max(0, cy_i - pad)
    yb = min(binary.shape[0], cy_i + pad + 1)

    roi = binary[ya:yb, xa:xb]
    if roi.size == 0:
        return {
            "center_fill_ratio": 1.0,
            "annulus_fill_ratio": 0.0,
            "halo_fill_ratio": 1.0,
            "ring_score": -1.0,
        }

    local_cx = int(cx_i - xa)
    local_cy = int(cy_i - ya)

    center_r = max(2, int(round(radius_i * 0.40)))
    inner_r = max(center_r + 1, int(round(radius_i * 0.68)))
    outer_r = max(inner_r + 2, int(round(radius_i * 1.20)))
    halo_r = max(outer_r + 2, int(round(radius_i * 1.70)))

    center_mask = np.zeros(roi.shape[:2], dtype=np.uint8)
    inner_mask = np.zeros_like(center_mask)
    outer_mask = np.zeros_like(center_mask)
    halo_mask_full = np.zeros_like(center_mask)

    cv2.circle(center_mask, (local_cx, local_cy), center_r, 255, -1)
    cv2.circle(inner_mask, (local_cx, local_cy), inner_r, 255, -1)
    cv2.circle(outer_mask, (local_cx, local_cy), outer_r, 255, -1)
    cv2.circle(halo_mask_full, (local_cx, local_cy), halo_r, 255, -1)

    annulus_mask = cv2.subtract(outer_mask, inner_mask)
    halo_mask = cv2.subtract(halo_mask_full, outer_mask)

    center_fill_ratio = _masked_fill_ratio(roi, center_mask)
    annulus_fill_ratio = _masked_fill_ratio(roi, annulus_mask)
    halo_fill_ratio = _masked_fill_ratio(roi, halo_mask)

    ring_score = (
        1.25 * float(annulus_fill_ratio)
        - 1.35 * float(center_fill_ratio)
        - 0.30 * float(halo_fill_ratio)
    )

    return {
        "center_fill_ratio": round(float(center_fill_ratio), 4),
        "annulus_fill_ratio": round(float(annulus_fill_ratio), 4),
        "halo_fill_ratio": round(float(halo_fill_ratio), 4),
        "ring_score": round(float(ring_score), 4),
    }


def _compute_meter_candidate_quality(candidate):
    ring_score = float(candidate.get("ring_score", -1.0))
    annulus_fill = float(candidate.get("annulus_fill_ratio", 0.0))
    center_fill = float(candidate.get("center_fill_ratio", 1.0))
    halo_fill = float(candidate.get("halo_fill_ratio", 1.0))
    best_support = float(candidate.get("best_support", 0.0))
    source_bonus = 18.0 if candidate.get("source") == "contour_hole" else 0.0

    quality_score = (
        90.0 * ring_score
        + 26.0 * annulus_fill
        - 18.0 * center_fill
        - 8.0 * halo_fill
        + 0.55 * best_support
        + source_bonus
    )
    return round(float(quality_score), 4)


def _is_valid_meter_post_candidate(candidate):
    source = candidate.get("source")
    center_fill = float(candidate.get("center_fill_ratio", 1.0))
    annulus_fill = float(candidate.get("annulus_fill_ratio", 0.0))
    halo_fill = float(candidate.get("halo_fill_ratio", 1.0))
    ring_score = float(candidate.get("ring_score", -1.0))
    quality_score = float(candidate.get("quality_score", -999.0))

    if source == "contour_hole":
        return (
            center_fill <= 0.42
            and annulus_fill >= 0.16
            and halo_fill <= 0.72
            and ring_score >= -0.03
            and quality_score >= 8.0
        )

    return (
        center_fill <= 0.34
        and annulus_fill >= 0.22
        and halo_fill <= 0.62
        and ring_score >= 0.04
        and quality_score >= 16.0
    )


# Valuta il supporto dei cerchi Hough.
def _hough_circle_support(roi, cx, cy, radius):
    radius = max(5, int(round(radius)))
    band = max(3, int(round(radius * 0.32)))
    reach = max(8, int(round(radius * 0.85)))

    left = _count_roi_nonzero(roi, cx - radius - reach, cy - band, cx - radius + 1, cy + band + 1)
    right = _count_roi_nonzero(roi, cx + radius - 1, cy - band, cx + radius + reach, cy + band + 1)
    top = _count_roi_nonzero(roi, cx - band, cy - radius - reach, cx + band + 1, cy - radius + 1)
    bottom = _count_roi_nonzero(roi, cx - band, cy + radius - 1, cx + band + 1, cy + radius + reach)

    support_by_side = {
        "left": int(left),
        "right": int(right),
        "top": int(top),
        "bottom": int(bottom),
    }
    dominant_side = max(support_by_side, key=support_by_side.get)
    return int(support_by_side[dominant_side]), dominant_side, support_by_side


# Choose same edge pair.
def _choose_same_edge_pair(circles, box_w, box_h):
    edge_threshold = max(12.0, 0.18 * float(min(box_w, box_h)))
    best_pair = None
    best_score = None

    for edge in ("top", "bottom", "left", "right"):
        group = [
            circ for circ in circles
            if circ.get("nearest_edge") == edge and float(circ.get("edge_distance", 9999.0)) <= edge_threshold
        ]
        if len(group) < 2:
            continue

        for idx_a in range(len(group)):
            for idx_b in range(idx_a + 1, len(group)):
                circ_a = group[idx_a]
                circ_b = group[idx_b]
                dx = abs(float(circ_a["cx"]) - float(circ_b["cx"]))
                dy = abs(float(circ_a["cy"]) - float(circ_b["cy"]))
                if edge in {"top", "bottom"}:
                    main_sep = dx
                    cross_sep = dy
                else:
                    main_sep = dy
                    cross_sep = dx

                if main_sep < 12.0:
                    continue
                if cross_sep > 0.35 * main_sep + 6.0:
                    continue

                pair_score = (
                    float(circ_a["support"]) +
                    float(circ_b["support"]) +
                    0.25 * float(main_sep) -
                    0.12 * float(cross_sep) -
                    0.08 * (float(circ_a["edge_distance"]) + float(circ_b["edge_distance"]))
                )
                key = (
                    round(pair_score, 4),
                    round(float(main_sep), 4),
                    -round(float(cross_sep), 4),
                )
                if best_pair is None or key > best_score:
                    best_pair = (circ_a, circ_b)
                    best_score = key

    return list(best_pair) if best_pair is not None else None

# Find hough post circles.
def _find_hough_post_circles(binary, box):
    x1, y1, x2, y2 = [int(round(v)) for v in box]
    roi = binary[y1:y2 + 1, x1:x2 + 1]
    if roi.size == 0:
        return []

    blur = cv2.GaussianBlur(roi, (5, 5), 0)
    min_dim = max(1, min(roi.shape[0], roi.shape[1]))
    circles = cv2.HoughCircles(
        blur,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=max(12, int(round(min_dim * 0.12))),
        param1=60,
        param2=10,
        minRadius=max(4, int(round(min_dim * 0.05))),
        maxRadius=min(16, max(10, int(round(min_dim * 0.16)))),
    )
    if circles is None:
        return []

    deduped = []
    for cx, cy, radius in circles[0]:
        support, dominant_side, support_by_side = _hough_circle_support(roi, cx, cy, radius)
        if support < 8:
            continue
        candidate = {
            "cx": float(x1 + cx),
            "cy": float(y1 + cy),
            "width": int(round(radius * 2.0)),
            "height": int(round(radius * 2.0)),
            "area": round(float(3.141592653589793 * radius * radius), 2),
            "radius": round(float(radius), 2),
            "support": int(support),
            "dominant_side": dominant_side,
            "support_by_side": support_by_side,
        }
        edge_distances = {
            "left": float(cx),
            "right": float(max(0.0, roi.shape[1] - 1 - cx)),
            "top": float(cy),
            "bottom": float(max(0.0, roi.shape[0] - 1 - cy)),
        }
        nearest_edge = min(edge_distances, key=edge_distances.get)
        candidate["nearest_edge"] = nearest_edge
        candidate["edge_distance"] = round(float(edge_distances[nearest_edge]), 2)

        merged = False
        for existing in deduped:
            if (
                abs(float(candidate["cx"]) - float(existing["cx"])) <= 8.0 and
                abs(float(candidate["cy"]) - float(existing["cy"])) <= 8.0
            ):
                if int(candidate["support"]) > int(existing["support"]):
                    existing.update(candidate)
                merged = True
                break
        if not merged:
            deduped.append(candidate)

    return sorted(
        deduped,
        key=lambda circ: (
            int(circ["support"]),
            float(circ["radius"]),
        ),
        reverse=True,
    )[:12]


# Fonde i candidati post dell'analog meter.
def _merge_meter_post_candidates(candidates):
    merged = []

    for cand in candidates:
        merged_into_existing = False

        for existing in merged:
            if (
                abs(float(cand["cx"]) - float(existing["cx"])) <= 8.0
                and abs(float(cand["cy"]) - float(existing["cy"])) <= 8.0
            ):
                cand_is_contour = cand.get("source") == "contour_hole"
                existing_is_contour = existing.get("source") == "contour_hole"

                replace_existing = False
                if cand_is_contour and not existing_is_contour:
                    replace_existing = True
                elif cand_is_contour == existing_is_contour:
                    cand_key = (
                        float(cand.get("ring_score", -999.0)),
                        float(cand.get("support", 0.0)),
                        float(cand.get("area", 0.0)),
                    )
                    existing_key = (
                        float(existing.get("ring_score", -999.0)),
                        float(existing.get("support", 0.0)),
                        float(existing.get("area", 0.0)),
                    )
                    if cand_key > existing_key:
                        replace_existing = True

                if replace_existing:
                    existing.update(cand)

                merged_into_existing = True
                break

        if not merged_into_existing:
            merged.append(dict(cand))

    return merged


# Trova i bordi compatibili con un punto.
def _eligible_edges_for_point(cx, cy, box_w, box_h):
    edge_distances = {
        "left": float(cx),
        "right": float(max(0.0, box_w - 1 - cx)),
        "top": float(cy),
        "bottom": float(max(0.0, box_h - 1 - cy)),
    }
    min_distance = min(edge_distances.values())
    eligibility_threshold = max(14.0, float(min_distance) + 8.0)
    eligible_edges = [
        edge for edge, distance in edge_distances.items()
        if float(distance) <= float(eligibility_threshold)
    ]
    return eligible_edges, edge_distances


# Costruisce i candidati post dell'analog meter.
def _build_meter_post_candidates(binary, search_box, holes):
    x1, y1, x2, y2 = [int(round(v)) for v in search_box]
    box_w = max(int(x2 - x1 + 1), 1)
    box_h = max(int(y2 - y1 + 1), 1)

    raw_candidates = []

    for hole in holes:
        local_cx = float(hole["cx"]) - float(x1)
        local_cy = float(hole["cy"]) - float(y1)
        eligible_edges, edge_distances = _eligible_edges_for_point(local_cx, local_cy, box_w, box_h)
        nearest_edge = min(edge_distances, key=edge_distances.get)

        ring_metrics = {
            "center_fill_ratio": float(hole.get("center_fill_ratio", 1.0)),
            "annulus_fill_ratio": float(hole.get("annulus_fill_ratio", 0.0)),
            "halo_fill_ratio": float(hole.get("halo_fill_ratio", 1.0)),
            "ring_score": float(hole.get("ring_score", -1.0)),
        }

        raw_candidates.append({
            "cx": float(hole["cx"]),
            "cy": float(hole["cy"]),
            "radius": float(max(hole.get("width", 0), hole.get("height", 0)) / 2.0),
            "support": float(max(hole.get("width", 0), hole.get("height", 0), 8)),
            "source": "contour_hole",
            "eligible_edges": eligible_edges,
            "edge_distances": edge_distances,
            "nearest_edge": nearest_edge,
            "edge_distance": float(edge_distances[nearest_edge]),
            "area": float(hole.get("area", 0.0)),
            **ring_metrics,
        })

    for circle in _find_hough_post_circles(binary, search_box):
        local_cx = float(circle["cx"]) - float(x1)
        local_cy = float(circle["cy"]) - float(y1)
        eligible_edges, edge_distances = _eligible_edges_for_point(local_cx, local_cy, box_w, box_h)

        circle_copy = dict(circle)
        circle_copy["source"] = "hough_circle"
        circle_copy["eligible_edges"] = eligible_edges
        circle_copy["edge_distances"] = edge_distances

        circle_copy.update(
            _measure_meter_post_ring(
                binary,
                circle_copy["cx"],
                circle_copy["cy"],
                circle_copy.get("radius", max(circle_copy.get("width", 0), circle_copy.get("height", 0)) / 2.0),
            )
        )
        raw_candidates.append(circle_copy)

    candidates = _merge_meter_post_candidates(raw_candidates)

    annotated = []
    for candidate in candidates:
        candidate = _annotate_meter_candidate_external_support(binary, search_box, candidate)
        candidate["quality_score"] = _compute_meter_candidate_quality(candidate)
        annotated.append(candidate)

    annotated = sorted(
        annotated,
        key=lambda cand: (
            1 if cand.get("source") == "contour_hole" else 0,
            float(cand.get("quality_score", -999.0)),
            float(cand.get("ring_score", -999.0)),
            float(cand.get("best_support", 0.0)),
            float(cand.get("area", 0.0)),
        ),
        reverse=True,
    )

    strong_candidates = [cand for cand in annotated if _is_valid_meter_post_candidate(cand)]
    if len(strong_candidates) >= 2:
        return strong_candidates[:10]

    return annotated[:10]

# Calcola gli score di scansione bordo dell'analog meter.
def _meter_edge_scan_scores(binary, box):
    x1, y1, x2, y2 = [float(v) for v in box]
    width = max(float(x2 - x1), 1.0)
    height = max(float(y2 - y1), 1.0)
    center_x = float(x1 + x2) / 2.0
    center_y = float(y1 + y2) / 2.0
    mid_gap_y = max(8.0, 0.08 * height)
    mid_gap_x = max(8.0, 0.08 * width)
    top_range = (y1 + 0.10 * height, center_y - mid_gap_y)
    bottom_range = (center_y + mid_gap_y, y2 - 0.10 * height)
    left_range = (x1 + 0.10 * width, center_x - mid_gap_x)
    right_range = (center_x + mid_gap_x, x2 - 0.10 * width)

    _, top_left_debug = _scan_external_wire_x_in_range(binary, box, "top", left_range[0], left_range[1])
    _, top_right_debug = _scan_external_wire_x_in_range(binary, box, "top", right_range[0], right_range[1])
    _, bottom_left_debug = _scan_external_wire_x_in_range(binary, box, "bottom", left_range[0], left_range[1])
    _, bottom_right_debug = _scan_external_wire_x_in_range(binary, box, "bottom", right_range[0], right_range[1])
    _, left_top_debug = _scan_external_wire_y_in_range(binary, box, "left", top_range[0], top_range[1])
    _, left_bottom_debug = _scan_external_wire_y_in_range(binary, box, "left", bottom_range[0], bottom_range[1])
    _, right_top_debug = _scan_external_wire_y_in_range(binary, box, "right", top_range[0], top_range[1])
    _, right_bottom_debug = _scan_external_wire_y_in_range(binary, box, "right", bottom_range[0], bottom_range[1])

    return {
        "top": (top_left_debug, top_right_debug),
        "bottom": (bottom_left_debug, bottom_right_debug),
        "left": (left_top_debug, left_bottom_debug),
        "right": (right_top_debug, right_bottom_debug),
    }


# Valuta una coppia di bordi dell'analog meter.
def _score_meter_edge_pair(edge, cand_a, cand_b, scan_pair):
    dx = abs(float(cand_a["cx"]) - float(cand_b["cx"]))
    dy = abs(float(cand_a["cy"]) - float(cand_b["cy"]))

    if edge in {"top", "bottom"}:
        main_sep = dx
        cross_sep = dy
    else:
        main_sep = dy
        cross_sep = dx

    if main_sep < 18.0 or cross_sep > 0.45 * main_sep + 8.0:
        return None

    edge_distance_sum = (
        float(cand_a["edge_distances"][edge])
        + float(cand_b["edge_distances"][edge])
    )

    raw_circle_score = (
        float(cand_a.get("support", 0.0))
        + float(cand_b.get("support", 0.0))
        + 2.4 * float(main_sep)
        - 1.2 * float(cross_sep)
        - 0.35 * edge_distance_sum
    )

    scan_a = float(scan_pair[0].get("max_score", 0.0))
    scan_b = float(scan_pair[1].get("max_score", 0.0))
    scan_sum = scan_a + scan_b
    scan_diff = abs(scan_a - scan_b)
    balance = (min(scan_a, scan_b) + 6.0) / (max(scan_a, scan_b) + 6.0)

    ring_bonus = 55.0 * (
        float(cand_a.get("ring_score", 0.0))
        + float(cand_b.get("ring_score", 0.0))
    )
    annulus_bonus = 20.0 * (
        float(cand_a.get("annulus_fill_ratio", 0.0))
        + float(cand_b.get("annulus_fill_ratio", 0.0))
    )
    center_penalty = 16.0 * (
        float(cand_a.get("center_fill_ratio", 0.0))
        + float(cand_b.get("center_fill_ratio", 0.0))
    )

    contour_bonus = 70.0 if (
        cand_a.get("source") == "contour_hole"
        and cand_b.get("source") == "contour_hole"
    ) else 0.0

    best_side_bonus = 0.0
    if cand_a.get("best_side") == edge:
        best_side_bonus += 35.0
    if cand_b.get("best_side") == edge:
        best_side_bonus += 35.0

    quality_bonus = 0.35 * (
        float(cand_a.get("quality_score", 0.0))
        + float(cand_b.get("quality_score", 0.0))
    )

    final_score = (
        raw_circle_score * balance
        + 1.0 * scan_sum
        - 0.4 * scan_diff
        + ring_bonus
        + annulus_bonus
        - center_penalty
        + contour_bonus
        + best_side_bonus
        + quality_bonus
    )

    return {
        "edge": edge,
        "layout": "same_edge",
        "score": float(final_score),
        "balance": round(float(balance), 4),
        "raw_circle_score": round(float(raw_circle_score), 3),
        "main_sep": round(float(main_sep), 3),
        "cross_sep": round(float(cross_sep), 3),
        "scan_scores": [round(float(scan_a), 3), round(float(scan_b), 3)],
        "scan_sum": round(float(scan_sum), 3),
        "scan_diff": round(float(scan_diff), 3),
        "ring_bonus": round(float(ring_bonus), 3),
        "annulus_bonus": round(float(annulus_bonus), 3),
        "center_penalty": round(float(center_penalty), 3),
        "contour_bonus": round(float(contour_bonus), 3),
        "best_side_bonus": round(float(best_side_bonus), 3),
        "quality_bonus": round(float(quality_bonus), 3),
    }


# Valuta il supporto laterale del candidato analog meter.
def _meter_candidate_side_support(binary, box, candidate, side):
    x1, y1, x2, y2 = [int(round(v)) for v in box]
    cx = int(round(float(candidate["cx"])))
    cy = int(round(float(candidate["cy"])))
    span = max(4, int(round(max(float(candidate.get("radius", 0.0)), 5.0) * 0.9)))
    inward_len = max(8, int(round(span * 1.6)))
    outward_len = max(12, int(round(span * 2.4)))

    if side == "left":
        xa = max(0, x1 - outward_len)
        xb = min(binary.shape[1], x1 + inward_len)
        ya = max(0, cy - span)
        yb = min(binary.shape[0], cy + span + 1)
    elif side == "right":
        xa = max(0, x2 - inward_len + 1)
        xb = min(binary.shape[1], x2 + outward_len + 1)
        ya = max(0, cy - span)
        yb = min(binary.shape[0], cy + span + 1)
    elif side == "top":
        xa = max(0, cx - span)
        xb = min(binary.shape[1], cx + span + 1)
        ya = max(0, y1 - outward_len)
        yb = min(binary.shape[0], y1 + inward_len)
    else:
        xa = max(0, cx - span)
        xb = min(binary.shape[1], cx + span + 1)
        ya = max(0, y2 - inward_len + 1)
        yb = min(binary.shape[0], y2 + outward_len + 1)

    support = _count_roi_nonzero(binary, xa, ya, xb, yb)
    return {
        "side": side,
        "support": float(support),
        "probe": [int(xa), int(ya), int(xb), int(yb)],
    }

# Annotate meter candidate with real external wire support on each side.
def _annotate_meter_candidate_external_support(binary, search_box, candidate):
    side_debug = {}
    for side in ("left", "right", "top", "bottom"):
        side_debug[side] = _meter_candidate_side_support(
            binary,
            search_box,
            candidate,
            side,
        )

    ranked = sorted(
        side_debug.items(),
        key=lambda kv: float(kv[1]["support"]),
        reverse=True,
    )

    candidate_copy = dict(candidate)
    candidate_copy["side_support_debug"] = side_debug
    candidate_copy["best_side"] = ranked[0][0]
    candidate_copy["best_support"] = float(ranked[0][1]["support"])
    candidate_copy["second_side"] = ranked[1][0]
    candidate_copy["second_support"] = float(ranked[1][1]["support"])

    # Se un lato vince chiaramente, restringi eligible_edges a quel lato.
    if candidate_copy["best_support"] >= candidate_copy["second_support"] + 6.0:
        candidate_copy["eligible_edges"] = [candidate_copy["best_side"]]

    return candidate_copy

# Valuta una coppia opposta dell'analog meter.
def _score_meter_opposite_pair(binary, box, side_a, cand_a, side_b, cand_b):
    if {side_a, side_b} == {"left", "right"}:
        alignment = abs(float(cand_a["cy"]) - float(cand_b["cy"]))
        span = abs(float(cand_a["cx"]) - float(cand_b["cx"]))
        if span < 18.0 or alignment > 0.22 * span + 10.0:
            return None
    elif {side_a, side_b} == {"top", "bottom"}:
        alignment = abs(float(cand_a["cx"]) - float(cand_b["cx"]))
        span = abs(float(cand_a["cy"]) - float(cand_b["cy"]))
        if span < 18.0 or alignment > 0.22 * span + 10.0:
            return None
    else:
        return None

    support_a = _meter_candidate_side_support(binary, box, cand_a, side_a)
    support_b = _meter_candidate_side_support(binary, box, cand_b, side_b)
    support_sum = float(support_a["support"]) + float(support_b["support"])
    support_balance = (min(float(support_a["support"]), float(support_b["support"])) + 6.0) / (
        max(float(support_a["support"]), float(support_b["support"])) + 6.0
    )
    single_edge_penalty = 160.0 * float(
        sum(
            1
            for cand in (cand_a, cand_b)
            if len(cand.get("eligible_edges", [])) <= 1 and cand.get("source") != "contour_hole"
        )
    )
    support_overflow_penalty = (
        max(0.0, float(support_a["support"]) - 190.0)
        + max(0.0, float(support_b["support"]) - 190.0)
    ) * 2.4
    edge_penalty = float(cand_a["edge_distances"].get(side_a, 0.0)) + float(cand_b["edge_distances"].get(side_b, 0.0))
    shared_secondary_edges = sorted(
        set(cand_a.get("eligible_edges", []))
        .intersection(set(cand_b.get("eligible_edges", [])))
        .difference({side_a, side_b})
    )
    row_column_bonus = 0.0
    if {side_a, side_b} == {"left", "right"} and shared_secondary_edges:
        row_column_bonus = max(0.0, 260.0 - 8.0 * float(alignment))
    elif {side_a, side_b} == {"top", "bottom"} and shared_secondary_edges:
        row_column_bonus = max(0.0, 260.0 - 8.0 * float(alignment))
    final_score = (
        0.9 * support_sum * support_balance
        + 1.4 * float(span)
        - 0.9 * float(alignment)
        - 0.25 * float(edge_penalty)
        - float(single_edge_penalty)
        - float(support_overflow_penalty)
        + 0.35 * float(cand_a.get("support", 0.0) + cand_b.get("support", 0.0))
        + float(row_column_bonus)
    )
    return {
        "layout": "opposite_edges",
        "edge_pair": [side_a, side_b],
        "score": round(float(final_score), 3),
        "support_sum": round(float(support_sum), 3),
        "support_balance": round(float(support_balance), 4),
        "single_edge_penalty": round(float(single_edge_penalty), 3),
        "support_overflow_penalty": round(float(support_overflow_penalty), 3),
        "span": round(float(span), 3),
        "alignment": round(float(alignment), 3),
        "edge_penalty": round(float(edge_penalty), 3),
        "shared_secondary_edges": shared_secondary_edges,
        "row_column_bonus": round(float(row_column_bonus), 3),
        "support_debug": [support_a, support_b],
    }


# Seleziona la coppia di post dell'analog meter.
def _select_meter_post_pair(binary, search_box, candidates, allow_opposite=False):
    scan_scores = _meter_edge_scan_scores(binary, search_box)
    x1, y1, x2, y2 = [float(v) for v in search_box]
    width = max(float(x2 - x1), 1.0)
    height = max(float(y2 - y1), 1.0)

    vertical_edge_floor = max(
        float(min(scan_scores["left"][0].get("max_score", 0), scan_scores["left"][1].get("max_score", 0))),
        float(min(scan_scores["right"][0].get("max_score", 0), scan_scores["right"][1].get("max_score", 0))),
    )
    horizontal_edge_floor = max(
        float(min(scan_scores["top"][0].get("max_score", 0), scan_scores["top"][1].get("max_score", 0))),
        float(min(scan_scores["bottom"][0].get("max_score", 0), scan_scores["bottom"][1].get("max_score", 0))),
    )

    best_pair = None
    best_pair_debug = None
    best_key = None
    best_same_edge = {}

    # -------------------------------------------------
    # PASS PRINCIPALE: same-edge only.
    # Per l'analog meter i due post reali stanno sulla
    # stessa faccia del simbolo ruotato.
    # -------------------------------------------------
    for edge in ("top", "bottom", "left", "right"):
        group = [cand for cand in candidates if edge in cand.get("eligible_edges", [])]
        if len(group) < 2:
            continue

        for idx_a in range(len(group)):
            for idx_b in range(idx_a + 1, len(group)):
                cand_a = group[idx_a]
                cand_b = group[idx_b]

                pair_debug = _score_meter_edge_pair(edge, cand_a, cand_b, scan_scores[edge])
                if pair_debug is None:
                    continue

                elongation_bonus = 0.0
                if height >= width * 2.1 and edge in {"top", "bottom"}:
                    edge_floor = min(
                        float(scan_scores[edge][0].get("max_score", 0)),
                        float(scan_scores[edge][1].get("max_score", 0)),
                    )
                    if edge_floor >= max(24.0, vertical_edge_floor * 1.30):
                        elongation_bonus = 500.0
                elif width >= height * 2.1 and edge in {"left", "right"}:
                    edge_floor = min(
                        float(scan_scores[edge][0].get("max_score", 0)),
                        float(scan_scores[edge][1].get("max_score", 0)),
                    )
                    if edge_floor >= max(24.0, horizontal_edge_floor * 1.30):
                        elongation_bonus = 500.0

                pair_debug["elongation_bonus"] = round(float(elongation_bonus), 3)
                pair_debug["score"] = round(float(pair_debug["score"] + elongation_bonus), 3)

                key = (
                    round(float(pair_debug["score"]), 4),
                    round(float(pair_debug["main_sep"]), 4),
                    -round(float(pair_debug["cross_sep"]), 4),
                )

                if best_pair is None or key > best_key:
                    best_pair = (cand_a, cand_b)
                    best_pair_debug = pair_debug
                    best_key = key

                stored = best_same_edge.get(edge)
                if stored is None or key > stored["key"]:
                    best_same_edge[edge] = {
                        "pair": (cand_a, cand_b),
                        "debug": pair_debug,
                        "key": key,
                    }

    # -------------------------------------------------
    # Preferenza ulteriore fra left/right se entrambi forti.
    # -------------------------------------------------
    left_same_edge = best_same_edge.get("left")
    right_same_edge = best_same_edge.get("right")
    if left_same_edge is not None and right_same_edge is not None:
        left_score = float(left_same_edge["debug"].get("score", 0.0))
        right_score = float(right_same_edge["debug"].get("score", 0.0))
        left_scan_sum = sum(float(v) for v in left_same_edge["debug"].get("scan_scores", []))
        right_scan_sum = sum(float(v) for v in right_same_edge["debug"].get("scan_scores", []))
        left_balance = float(left_same_edge["debug"].get("balance", 0.0))
        right_balance = float(right_same_edge["debug"].get("balance", 0.0))

        preferred = None
        if (
            left_balance >= 0.50
            and left_scan_sum >= right_scan_sum + 20.0
            and left_score >= right_score - 140.0
        ):
            preferred = left_same_edge
        elif (
            right_balance >= 0.50
            and right_scan_sum >= left_scan_sum + 20.0
            and right_score >= left_score - 140.0
        ):
            preferred = right_same_edge

        if preferred is not None:
            best_pair = preferred["pair"]
            best_pair_debug = preferred["debug"]
            best_key = preferred["key"]

    if best_pair is not None or not allow_opposite:
        return best_pair, best_pair_debug, scan_scores

    # -------------------------------------------------
    # FALLBACK ESTREMO: opposite_edges.
    # Lo lasciamo solo come ultima chance.
    # -------------------------------------------------
    best_structured_opposite_pair = None
    best_structured_opposite_debug = None
    best_structured_opposite_key = None

    opposite_layouts = (
        ("left", "right"),
        ("top", "bottom"),
    )

    for side_a, side_b in opposite_layouts:
        group_a = [cand for cand in candidates if side_a in cand.get("eligible_edges", [])]
        group_b = [cand for cand in candidates if side_b in cand.get("eligible_edges", [])]
        if not group_a or not group_b:
            continue

        for cand_a in group_a:
            for cand_b in group_b:
                if cand_a is cand_b:
                    continue

                pair_debug = _score_meter_opposite_pair(binary, search_box, side_a, cand_a, side_b, cand_b)
                if pair_debug is None:
                    continue

                pair_debug["score"] = round(
                    float(pair_debug["score"])
                    + 18.0 * float(cand_a.get("ring_score", 0.0) + cand_b.get("ring_score", 0.0))
                    + 0.18 * float(cand_a.get("quality_score", 0.0) + cand_b.get("quality_score", 0.0)),
                    3,
                )

                key = (
                    round(float(pair_debug["score"]), 4),
                    round(float(pair_debug["span"]), 4),
                    -round(float(pair_debug["alignment"]), 4),
                )

                if (
                    best_structured_opposite_pair is None
                    or key > best_structured_opposite_key
                ):
                    best_structured_opposite_pair = (cand_a, cand_b)
                    best_structured_opposite_debug = pair_debug
                    best_structured_opposite_key = key

    return best_structured_opposite_pair, best_structured_opposite_debug, scan_scores

def _opposite_side(side):
    return {
        "top": "bottom",
        "bottom": "top",
        "left": "right",
        "right": "left",
    }[side]


def _meter_face_side_scores(binary, box):
    x1, y1, x2, y2 = [int(round(v)) for v in box]
    w = max(x2 - x1 + 1, 1)
    h = max(y2 - y1 + 1, 1)

    # restringo all'interno per ridurre il peso del bordo esterno
    ix1 = x1 + int(round(0.12 * w))
    ix2 = x2 - int(round(0.12 * w))
    iy1 = y1 + int(round(0.12 * h))
    iy2 = y2 - int(round(0.12 * h))

    if ix2 <= ix1 + 10 or iy2 <= iy1 + 10:
        ix1, iy1, ix2, iy2 = x1, y1, x2, y2

    iw = max(ix2 - ix1 + 1, 1)
    ih = max(iy2 - iy1 + 1, 1)

    def _density(rx1, ry1, rx2, ry2):
        xa = ix1 + int(round(rx1 * iw))
        xb = ix1 + int(round(rx2 * iw))
        ya = iy1 + int(round(ry1 * ih))
        yb = iy1 + int(round(ry2 * ih))

        xa = max(x1, min(x2, xa))
        xb = max(x1 + 1, min(x2 + 1, xb))
        ya = max(y1, min(y2, ya))
        yb = max(y1 + 1, min(y2 + 1, yb))

        area = max((xb - xa) * (yb - ya), 1)
        return float(_count_roi_nonzero(binary, xa, ya, xb, yb)) / float(area)

    scores = {
        "top": _density(0.20, 0.00, 0.80, 0.36),
        "bottom": _density(0.20, 0.64, 0.80, 1.00),
        "left": _density(0.00, 0.20, 0.36, 0.80),
        "right": _density(0.64, 0.20, 1.00, 0.80),
    }
    return scores




def _detect_meter_post_side(binary, box):
    scores = _meter_face_side_scores(binary, box)

    vertical_best = max(float(scores["top"]), float(scores["bottom"]))
    horizontal_best = max(float(scores["left"]), float(scores["right"]))

    if vertical_best >= horizontal_best:
        dial_side = "top" if float(scores["top"]) >= float(scores["bottom"]) else "bottom"
    else:
        dial_side = "left" if float(scores["left"]) >= float(scores["right"]) else "right"

    post_side = _opposite_side(dial_side)
    return post_side, dial_side, scores


def _meter_anchor_layout(box, post_side):
    x1, y1, x2, y2 = [float(v) for v in box]
    w = max(float(x2 - x1), 1.0)
    h = max(float(y2 - y1), 1.0)

    if post_side == "bottom":
        anchors = [
            (float(x1 + 0.28 * w), float(y1 + 0.79 * h)),
            (float(x1 + 0.72 * w), float(y1 + 0.79 * h)),
        ]
        orientation = "horizontal"
        relative_positions = ("bottom", "bottom")
        axis = "bottom_template_posts"

    elif post_side == "top":
        anchors = [
            (float(x1 + 0.28 * w), float(y1 + 0.21 * h)),
            (float(x1 + 0.72 * w), float(y1 + 0.21 * h)),
        ]
        orientation = "horizontal"
        relative_positions = ("top", "top")
        axis = "top_template_posts"

    elif post_side == "left":
        anchors = [
            (float(x1 + 0.23 * w), float(y1 + 0.31 * h)),
            (float(x1 + 0.23 * w), float(y1 + 0.72 * h)),
        ]
        orientation = "vertical"
        relative_positions = ("left", "left")
        axis = "left_template_posts"

    else:
        anchors = [
            (float(x1 + 0.77 * w), float(y1 + 0.31 * h)),
            (float(x1 + 0.77 * w), float(y1 + 0.72 * h)),
        ]
        orientation = "vertical"
        relative_positions = ("right", "right")
        axis = "right_template_posts"

    return anchors, orientation, relative_positions, axis


def _refine_meter_post_near_anchor(binary, box, anchor, expected_side):
    x1, y1, x2, y2 = [int(round(v)) for v in box]
    w = max(x2 - x1 + 1, 1)
    h = max(y2 - y1 + 1, 1)
    min_dim = max(1, min(w, h))

    ax = int(round(anchor[0]))
    ay = int(round(anchor[1]))

    search_r = max(5, int(round(0.10 * min_dim)))
    radius = max(5, int(round(0.060 * min_dim)))

    best = None
    best_score = None

    xa = max(x1 + 3, ax - search_r)
    xb = min(x2 - 3, ax + search_r)
    ya = max(y1 + 3, ay - search_r)
    yb = min(y2 - 3, ay + search_r)

    for cy in range(ya, yb + 1):
        for cx in range(xa, xb + 1):
            ring = _measure_meter_post_ring(binary, cx, cy, radius)
            side_support = _meter_candidate_side_support(
                binary,
                box,
                {"cx": float(cx), "cy": float(cy), "radius": float(radius)},
                expected_side,
            )["support"]

            dist_px = float(((cx - ax) ** 2 + (cy - ay) ** 2) ** 0.5)

            score = (
                120.0 * float(ring["ring_score"])
                + 28.0 * float(ring["annulus_fill_ratio"])
                - 18.0 * float(ring["center_fill_ratio"])
                - 8.0 * float(ring["halo_fill_ratio"])
                + 0.10 * float(side_support)
                - 1.60 * float(dist_px)
            )

            key = (
                round(float(score), 4),
                -round(float(dist_px), 4),
            )

            if best is None or key > best_score:
                best = {
                    "point": [float(cx), float(cy)],
                    "radius": float(radius),
                    "score": float(score),
                    "dist_px": float(dist_px),
                    "side_support": float(side_support),
                    **ring,
                }
                best_score = key

    if best is None:
        return {
            "point": [float(ax), float(ay)],
            "radius": float(radius),
            "score": -999.0,
            "dist_px": 0.0,
            "side_support": 0.0,
            "center_fill_ratio": 1.0,
            "annulus_fill_ratio": 0.0,
            "halo_fill_ratio": 1.0,
            "ring_score": -1.0,
        }

    # se la refine è troppo debole, torno all'anchor puro
    if float(best["score"]) < -8.0:
        return {
            "point": [float(ax), float(ay)],
            "radius": float(radius),
            "score": float(best["score"]),
            "dist_px": 0.0,
            "side_support": float(best["side_support"]),
            "center_fill_ratio": float(best["center_fill_ratio"]),
            "annulus_fill_ratio": float(best["annulus_fill_ratio"]),
            "halo_fill_ratio": float(best["halo_fill_ratio"]),
            "ring_score": float(best["ring_score"]),
            "fallback_anchor": True,
        }

    return best


def _snap_meter_post_to_candidate(candidates, anchor_point, box, expected_side, used_points=None):
    if not candidates:
        return None

    if used_points is None:
        used_points = []

    x1, y1, x2, y2 = [float(v) for v in box]
    w = max(float(x2 - x1), 1.0)
    h = max(float(y2 - y1), 1.0)

    ax = float(anchor_point[0])
    ay = float(anchor_point[1])

    best = None
    best_key = None

    for cand in candidates:
        cx = float(cand["cx"])
        cy = float(cand["cy"])

        # evita di riusare lo stesso candidato per i due post
        if any(abs(cx - px) <= 6.0 and abs(cy - py) <= 6.0 for px, py in used_points):
            continue

        dx = (cx - ax) / w
        dy = (cy - ay) / h
        dist_norm = float((dx * dx + dy * dy) ** 0.5)

        if dist_norm > 0.24:
            continue

        score = (
            float(cand.get("quality_score", 0.0))
            + 18.0 * float(1 if cand.get("source") == "contour_hole" else 0)
            + 10.0 * float(1 if cand.get("best_side") == expected_side else 0)
            + 12.0 * float(cand.get("ring_score", 0.0))
            - 220.0 * float(dist_norm)
        )

        key = (
            round(float(score), 4),
            -round(float(dist_norm), 4),
        )

        if best is None or key > best_key:
            best = {
                "point": [float(cx), float(cy)],
                "score": float(score),
                "dist_norm": float(dist_norm),
                "source": cand.get("source"),
                "best_side": cand.get("best_side"),
                "quality_score": float(cand.get("quality_score", 0.0)),
                "ring_score": float(cand.get("ring_score", 0.0)),
            }
            best_key = key

    if best is None:
        return None

    if float(best["score"]) < 4.0:
        return None

    return best

# Detect analog meter terminals.
def detect_analog_meter_terminals(meta: dict, binary, bbox):
    del meta

    det_box = [float(v) for v in geom_clamp_bbox_to_image(bbox, binary.shape)]
    inner_box = _find_structured_inner_box(
        binary,
        det_box,
        min_size=100,
        ratio_min=0.75,
        ratio_max=1.35,
        extent_min=0.88,
        prefer_square=True,
    )

    search_box = inner_box if inner_box is not None else det_box

    holes = _find_circular_holes(binary, search_box)
    if len(holes) < 2 and inner_box is not None:
        search_box = det_box
        holes = _find_circular_holes(binary, search_box)

    candidates = _build_meter_post_candidates(binary, search_box, holes)

    post_side, dial_side, face_scores = _detect_meter_post_side(binary, search_box)
    anchors, orientation, relative_positions, axis = _meter_anchor_layout(search_box, post_side)

    resolved_posts = []
    used_points = []

    for anchor in anchors:
        refined = _refine_meter_post_near_anchor(
            binary,
            search_box,
            anchor,
            expected_side=post_side,
        )

        snapped = _snap_meter_post_to_candidate(
            candidates,
            refined["point"],
            search_box,
            expected_side=post_side,
            used_points=used_points,
        )

        if snapped is not None:
            chosen_point = snapped["point"]
            chosen_debug = {
                "selection": "candidate_snap",
                "anchor": [round(float(anchor[0]), 2), round(float(anchor[1]), 2)],
                "refined_point": [round(float(refined["point"][0]), 2), round(float(refined["point"][1]), 2)],
                "snap_point": [round(float(snapped["point"][0]), 2), round(float(snapped["point"][1]), 2)],
                "snap_source": snapped.get("source"),
                "snap_best_side": snapped.get("best_side"),
                "snap_quality_score": round(float(snapped.get("quality_score", 0.0)), 3),
                "snap_ring_score": round(float(snapped.get("ring_score", 0.0)), 3),
            }
        else:
            chosen_point = refined["point"]
            chosen_debug = {
                "selection": "anchor_local_refine",
                "anchor": [round(float(anchor[0]), 2), round(float(anchor[1]), 2)],
                "refined_point": [round(float(refined["point"][0]), 2), round(float(refined["point"][1]), 2)],
                "refine_score": round(float(refined.get("score", 0.0)), 3),
                "ring_score": round(float(refined.get("ring_score", 0.0)), 3),
                "annulus_fill_ratio": round(float(refined.get("annulus_fill_ratio", 0.0)), 3),
                "center_fill_ratio": round(float(refined.get("center_fill_ratio", 0.0)), 3),
            }

        used_points.append((float(chosen_point[0]), float(chosen_point[1])))
        resolved_posts.append({
            "point": [round(float(chosen_point[0]), 2), round(float(chosen_point[1]), 2)],
            "debug": chosen_debug,
        })

    # ordinamento coerente
    if post_side in {"top", "bottom"}:
        resolved_posts = sorted(resolved_posts, key=lambda p: float(p["point"][0]))
    else:
        resolved_posts = sorted(resolved_posts, key=lambda p: float(p["point"][1]))

    terminals_def = []
    for term_name, rel_pos, post in zip(("t1", "t2"), relative_positions, resolved_posts):
        terminals_def.append(
            {
                "name": term_name,
                "relative_position": rel_pos,
                "point": post["point"],
            }
        )

    return terminals_def, orientation, None, {
        "strategy": "analog_meter_by_posts_template",
        "fallback": False,
        "inner_box": [round(float(v), 2) for v in inner_box] if inner_box is not None else None,
        "search_box": [round(float(v), 2) for v in search_box],
        "dial_side": dial_side,
        "post_side": post_side,
        "post_axis": axis,
        "face_side_scores": {
            side: round(float(score), 4)
            for side, score in face_scores.items()
        },
        "anchors": [
            [round(float(ax), 2), round(float(ay), 2)]
            for ax, ay in anchors
        ],
        "posts": [post["debug"] for post in resolved_posts],
        "n_candidates": int(len(candidates)),
        "candidate_debug": [
            {
                "cx": round(float(cand["cx"]), 2),
                "cy": round(float(cand["cy"]), 2),
                "source": cand.get("source"),
                "best_side": cand.get("best_side"),
                "quality_score": round(float(cand.get("quality_score", 0.0)), 3),
                "ring_score": round(float(cand.get("ring_score", 0.0)), 3),
            }
            for cand in candidates[:8]
        ],
    }


# Cerca un filo esterno su y dentro il range.
def _scan_external_wire_y_in_range(binary, box, side, y_start, y_end, outward_len=18, inward_len=8, halfspan=5):
    x1, y1, x2, y2 = [int(round(v)) for v in box]
    start = max(y1, min(y2, int(round(y_start))))
    end = max(y1, min(y2, int(round(y_end))))

    if end < start:
        start, end = end, start
    if end < start:
        start, end = y1, y2

    coords = list(range(start, end + 1))
    if not coords:
        coords = [int(round((start + end) / 2.0))]

    scores = []
    for cy in coords:
        ya = max(0, cy - halfspan)
        yb = min(binary.shape[0], cy + halfspan + 1)
        if side == "left":
            xa = max(0, x1 - outward_len)
            xb = min(binary.shape[1], x1 + inward_len)
        else:
            xa = max(0, x2 - inward_len + 1)
            xb = min(binary.shape[1], x2 + outward_len + 1)

        if xb <= xa or yb <= ya:
            scores.append(0)
            continue
        scores.append(int(cv2.countNonZero(binary[ya:yb, xa:xb])))

    best_coord, debug = _select_peak_coord(coords, scores, keep_ratio=0.58, min_score=4)
    return best_coord, {
        "side": side,
        "scan_start": int(start),
        "scan_end": int(end),
        "probe_outward_len": int(outward_len),
        "probe_inward_len": int(inward_len),
        "probe_halfspan": int(halfspan),
        "max_score": int(max(scores) if scores else 0),
        "raw_scores_sample": [int(score) for score in scores[:20]],
        **debug,
    }

# Cerca un filo esterno su x dentro il range.
def _scan_external_wire_x_in_range(binary, box, side, x_start, x_end, outward_len=18, inward_len=8, halfspan=5):
    x1, y1, x2, y2 = [int(round(v)) for v in box]
    start = max(x1, min(x2, int(round(x_start))))
    end = max(x1, min(x2, int(round(x_end))))

    if end < start:
        start, end = end, start
    if end < start:
        start, end = x1, x2

    coords = list(range(start, end + 1))
    if not coords:
        coords = [int(round((start + end) / 2.0))]

    scores = []
    for cx in coords:
        xa = max(0, cx - halfspan)
        xb = min(binary.shape[1], cx + halfspan + 1)
        if side == "top":
            ya = max(0, y1 - outward_len)
            yb = min(binary.shape[0], y1 + inward_len)
        else:
            ya = max(0, y2 - inward_len + 1)
            yb = min(binary.shape[0], y2 + outward_len + 1)

        if xb <= xa or yb <= ya:
            scores.append(0)
            continue
        scores.append(int(cv2.countNonZero(binary[ya:yb, xa:xb])))

    best_coord, debug = _select_peak_coord(coords, scores, keep_ratio=0.58, min_score=4)
    return best_coord, {
        "side": side,
        "scan_start": int(start),
        "scan_end": int(end),
        "probe_outward_len": int(outward_len),
        "probe_inward_len": int(inward_len),
        "probe_halfspan": int(halfspan),
        "max_score": int(max(scores) if scores else 0),
        "raw_scores_sample": [int(score) for score in scores[:20]],
        **debug,
    }


def _support_point_on_lateral_transformer_port(binary, box, side, y_coord, outward_len=18, inward_len=36, halfspan=5):
    x1, _, x2, _ = [int(round(v)) for v in box]
    cy = int(round(float(y_coord)))
    ya = max(0, cy - halfspan)
    yb = min(binary.shape[0], cy + halfspan + 1)
    if side == "left":
        xa = max(0, x1 - outward_len)
        xb = min(binary.shape[1], x1 + inward_len + 1)
    else:
        xa = max(0, x2 - inward_len)
        xb = min(binary.shape[1], x2 + outward_len + 1)

    if xb <= xa or yb <= ya:
        fallback_x = x1 - TERMINAL_OUTWARD_OFFSET if side == "left" else x2 + TERMINAL_OUTWARD_OFFSET
        return [round(float(fallback_x), 2), round(float(y_coord), 2)], {
            "point_source": "lateral_fallback_no_roi",
        }

    roi = binary[ya:yb, xa:xb]
    _, xs = np.nonzero(roi)
    if len(xs) == 0:
        fallback_x = x1 - TERMINAL_OUTWARD_OFFSET if side == "left" else x2 + TERMINAL_OUTWARD_OFFSET
        return [round(float(fallback_x), 2), round(float(y_coord), 2)], {
            "point_source": "lateral_fallback_no_support",
        }

    edge_x = int(xs.min()) if side == "left" else int(xs.max())
    support_x = xa + edge_x
    return [round(float(support_x), 2), round(float(y_coord), 2)], {
        "point_source": "lateral_support_pixel",
        "support_roi": [int(xa), int(ya), int(xb), int(yb)],
        "support_pixels": int(len(xs)),
    }


def _is_inner_quadrant_x_candidate(debug, inner_side, inner_ratio=0.78):
    start = debug.get("scan_start")
    end = debug.get("scan_end")
    run_start = debug.get("selected_run_start")
    run_end = debug.get("selected_run_end")
    if start is None or end is None or run_start is None or run_end is None:
        return False

    span = max(float(end) - float(start), 1.0)
    run_center = (float(run_start) + float(run_end)) / 2.0
    ratio = (run_center - float(start)) / span
    if inner_side == "right":
        return ratio >= float(inner_ratio)
    return ratio <= 1.0 - float(inner_ratio)


# Detect transformer terminals.
def detect_transformer_terminals(meta: dict, binary, bbox):
    del meta

    det_box = [float(v) for v in geom_clamp_bbox_to_image(bbox, binary.shape)]
    x1, y1, x2, y2 = det_box
    width = max(float(x2 - x1), 1.0)
    height = max(float(y2 - y1), 1.0)
    center_x = float(x1 + x2) / 2.0
    center_y = float(y1 + y2) / 2.0
    mid_gap_y = max(10.0, 0.08 * height)
    mid_gap_x = max(10.0, 0.08 * width)
    top_range = (y1 + 0.03 * height, center_y - mid_gap_y)
    bottom_range = (center_y + mid_gap_y, y2 - 0.03 * height)
    left_range = (x1 + 0.03 * width, center_x - mid_gap_x)
    right_range = (center_x + mid_gap_x, x2 - 0.03 * width)

    left_top_y, left_top_debug = _scan_external_wire_y_in_range(
        binary,
        det_box,
        side="left",
        y_start=top_range[0],
        y_end=top_range[1],
    )
    left_bottom_y, left_bottom_debug = _scan_external_wire_y_in_range(
        binary,
        det_box,
        side="left",
        y_start=bottom_range[0],
        y_end=bottom_range[1],
    )
    right_top_y, right_top_debug = _scan_external_wire_y_in_range(
        binary,
        det_box,
        side="right",
        y_start=top_range[0],
        y_end=top_range[1],
    )
    right_bottom_y, right_bottom_debug = _scan_external_wire_y_in_range(
        binary,
        det_box,
        side="right",
        y_start=bottom_range[0],
        y_end=bottom_range[1],
    )
    relaxed_left_top_y, relaxed_left_top_debug = _scan_external_wire_y_in_range(
        binary,
        det_box,
        side="left",
        y_start=top_range[0],
        y_end=top_range[1],
        inward_len=36,
    )
    relaxed_left_bottom_y, relaxed_left_bottom_debug = _scan_external_wire_y_in_range(
        binary,
        det_box,
        side="left",
        y_start=bottom_range[0],
        y_end=bottom_range[1],
        inward_len=36,
    )
    relaxed_right_top_y, relaxed_right_top_debug = _scan_external_wire_y_in_range(
        binary,
        det_box,
        side="right",
        y_start=top_range[0],
        y_end=top_range[1],
        inward_len=36,
    )
    relaxed_right_bottom_y, relaxed_right_bottom_debug = _scan_external_wire_y_in_range(
        binary,
        det_box,
        side="right",
        y_start=bottom_range[0],
        y_end=bottom_range[1],
        inward_len=36,
    )
    top_left_x, top_left_debug = _scan_external_wire_x_in_range(
        binary,
        det_box,
        side="top",
        x_start=left_range[0],
        x_end=left_range[1],
    )
    top_right_x, top_right_debug = _scan_external_wire_x_in_range(
        binary,
        det_box,
        side="top",
        x_start=right_range[0],
        x_end=right_range[1],
    )
    bottom_left_x, bottom_left_debug = _scan_external_wire_x_in_range(
        binary,
        det_box,
        side="bottom",
        x_start=left_range[0],
        x_end=left_range[1],
    )
    bottom_right_x, bottom_right_debug = _scan_external_wire_x_in_range(
        binary,
        det_box,
        side="bottom",
        x_start=right_range[0],
        x_end=right_range[1],
    )

    if left_bottom_y <= left_top_y:
        left_top_y = float(y1 + 0.24 * height)
        left_bottom_y = float(y2 - 0.24 * height)
        left_top_debug["fallback_quadrant_anchor"] = True
        left_bottom_debug["fallback_quadrant_anchor"] = True

    if right_bottom_y <= right_top_y:
        right_top_y = float(y1 + 0.24 * height)
        right_bottom_y = float(y2 - 0.24 * height)
        right_top_debug["fallback_quadrant_anchor"] = True
        right_bottom_debug["fallback_quadrant_anchor"] = True

    if top_right_x <= top_left_x:
        top_left_x = float(x1 + 0.24 * width)
        top_right_x = float(x2 - 0.24 * width)
        top_left_debug["fallback_quadrant_anchor"] = True
        top_right_debug["fallback_quadrant_anchor"] = True

    if bottom_right_x <= bottom_left_x:
        bottom_left_x = float(x1 + 0.24 * width)
        bottom_right_x = float(x2 - 0.24 * width)
        bottom_left_debug["fallback_quadrant_anchor"] = True
        bottom_right_debug["fallback_quadrant_anchor"] = True

    relaxed_lateral = {
        "t1": ("left", relaxed_left_top_y, relaxed_left_top_debug),
        "t2": ("right", relaxed_right_top_y, relaxed_right_top_debug),
        "t3": ("left", relaxed_left_bottom_y, relaxed_left_bottom_debug),
        "t4": ("right", relaxed_right_bottom_y, relaxed_right_bottom_debug),
    }
    top_bottom_debug_by_term = {
        "t1": ("top", top_left_debug, "right"),
        "t2": ("top", top_right_debug, "left"),
        "t3": ("bottom", bottom_left_debug, "right"),
        "t4": ("bottom", bottom_right_debug, "left"),
    }

    left_right_score = (
        float(left_top_debug.get("max_score", 0))
        + float(left_bottom_debug.get("max_score", 0))
        + float(right_top_debug.get("max_score", 0))
        + float(right_bottom_debug.get("max_score", 0))
    )
    top_bottom_score = (
        float(top_left_debug.get("max_score", 0))
        + float(top_right_debug.get("max_score", 0))
        + float(bottom_left_debug.get("max_score", 0))
        + float(bottom_right_debug.get("max_score", 0))
    )
    quadrant_choices = {
        "t1": {
            "left": {
                "score": float(left_top_debug.get("max_score", 0)),
                "relative_position": "left",
                "point": [round(float(x1 - TERMINAL_OUTWARD_OFFSET), 2), round(float(left_top_y), 2)],
            },
            "top": {
                "score": float(top_left_debug.get("max_score", 0)),
                "relative_position": "top",
                "point": [round(float(top_left_x), 2), round(float(y1 - TERMINAL_OUTWARD_OFFSET), 2)],
            },
        },
        "t2": {
            "right": {
                "score": float(right_top_debug.get("max_score", 0)),
                "relative_position": "right",
                "point": [round(float(x2 + TERMINAL_OUTWARD_OFFSET), 2), round(float(right_top_y), 2)],
            },
            "top": {
                "score": float(top_right_debug.get("max_score", 0)),
                "relative_position": "top",
                "point": [round(float(top_right_x), 2), round(float(y1 - TERMINAL_OUTWARD_OFFSET), 2)],
            },
        },
        "t3": {
            "left": {
                "score": float(left_bottom_debug.get("max_score", 0)),
                "relative_position": "left",
                "point": [round(float(x1 - TERMINAL_OUTWARD_OFFSET), 2), round(float(left_bottom_y), 2)],
            },
            "bottom": {
                "score": float(bottom_left_debug.get("max_score", 0)),
                "relative_position": "bottom",
                "point": [round(float(bottom_left_x), 2), round(float(y2 + TERMINAL_OUTWARD_OFFSET), 2)],
            },
        },
        "t4": {
            "right": {
                "score": float(right_bottom_debug.get("max_score", 0)),
                "relative_position": "right",
                "point": [round(float(x2 + TERMINAL_OUTWARD_OFFSET), 2), round(float(right_bottom_y), 2)],
            },
            "bottom": {
                "score": float(bottom_right_debug.get("max_score", 0)),
                "relative_position": "bottom",
                "point": [round(float(bottom_right_x), 2), round(float(y2 + TERMINAL_OUTWARD_OFFSET), 2)],
            },
        },
    }

    terminals_def = []
    quadrant_debug = {}
    side_counts = {"left": 0, "right": 0, "top": 0, "bottom": 0}
    for term_name in ("t1", "t2", "t3", "t4"):
        options = quadrant_choices[term_name]
        selected_side, selected_info = max(
            options.items(),
            key=lambda kv: (
                float(kv[1]["score"]),
                1 if kv[0] in {"top", "bottom"} and top_bottom_score >= left_right_score else 0,
                1 if kv[0] in {"left", "right"} and left_right_score > top_bottom_score else 0,
            ),
        )
        top_bottom_side, top_bottom_debug, inner_side = top_bottom_debug_by_term[term_name]
        relaxed_side, relaxed_y, relaxed_debug = relaxed_lateral[term_name]
        relaxed_score = float(relaxed_debug.get("max_score", 0))
        selected_score = float(selected_info["score"])
        if (
            selected_side == top_bottom_side
            and _is_inner_quadrant_x_candidate(top_bottom_debug, inner_side)
            and relaxed_score >= max(40.0, selected_score * 0.65)
        ):
            point, point_debug = _support_point_on_lateral_transformer_port(
                binary,
                det_box,
                relaxed_side,
                relaxed_y,
            )
            selected_side = relaxed_side
            selected_info = {
                "score": relaxed_score,
                "relative_position": relaxed_side,
                "point": point,
            }
            top_bottom_debug["relaxed_lateral_override"] = {
                "term_name": term_name,
                "side": relaxed_side,
                "score": round(float(relaxed_score), 3),
                **point_debug,
            }

        side_counts[selected_side] += 1
        terminals_def.append(
            {
                "name": term_name,
                "relative_position": selected_info["relative_position"],
                "point": selected_info["point"],
            }
        )
        quadrant_debug[term_name] = {
            "selected_side": selected_side,
            "selected_score": round(float(selected_info["score"]), 3),
            "options": {
                side: round(float(info["score"]), 3)
                for side, info in options.items()
            },
        }

    if side_counts["top"] + side_counts["bottom"] > side_counts["left"] + side_counts["right"]:
        estimated_orientation = "horizontal"
    elif side_counts["left"] + side_counts["right"] > side_counts["top"] + side_counts["bottom"]:
        estimated_orientation = "vertical"
    else:
        estimated_orientation = "horizontal" if top_bottom_score >= left_right_score else "vertical"

    selected_layout = "mixed_quadrants"
    if side_counts["top"] + side_counts["bottom"] == 4:
        selected_layout = "top_bottom"
    elif side_counts["left"] + side_counts["right"] == 4:
        selected_layout = "left_right"

    return terminals_def, estimated_orientation, None, {
        "strategy": "transformer_external_wires",
        "bbox": [round(float(v), 2) for v in det_box],
        "selected_layout": selected_layout,
        "quadrant_debug": quadrant_debug,
        "left_right_score": round(float(left_right_score), 2),
        "top_bottom_score": round(float(top_bottom_score), 2),
        "left_top_debug": left_top_debug,
        "left_bottom_debug": left_bottom_debug,
        "right_top_debug": right_top_debug,
        "right_bottom_debug": right_bottom_debug,
        "relaxed_left_top_debug": relaxed_left_top_debug,
        "relaxed_left_bottom_debug": relaxed_left_bottom_debug,
        "relaxed_right_top_debug": relaxed_right_top_debug,
        "relaxed_right_bottom_debug": relaxed_right_bottom_debug,
        "top_left_debug": top_left_debug,
        "top_right_debug": top_right_debug,
        "bottom_left_debug": bottom_left_debug,
        "bottom_right_debug": bottom_right_debug,
        "scan_ranges": {
            "top": [round(float(top_range[0]), 2), round(float(top_range[1]), 2)],
            "bottom": [round(float(bottom_range[0]), 2), round(float(bottom_range[1]), 2)],
            "left": [round(float(left_range[0]), 2), round(float(left_range[1]), 2)],
            "right": [round(float(right_range[0]), 2), round(float(right_range[1]), 2)],
        },
    }
