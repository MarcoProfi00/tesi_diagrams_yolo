import cv2

from .config import TERMINAL_OUTWARD_OFFSET
from .geometry import geom_clamp_bbox_to_image


# Group close indices.
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


# Handle select peak coord.
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

        holes.append({
            "cx": cx,
            "cy": cy,
            "width": int(hw),
            "height": int(hh),
            "area": float(area),
            "circularity": round(float(circularity), 4),
        })

    holes = sorted(holes, key=lambda hole: float(hole["area"]), reverse=True)
    selected = []
    for hole in holes:
        if all(
            abs(float(hole["cx"]) - float(other["cx"])) > 6.0
            or abs(float(hole["cy"]) - float(other["cy"])) > 6.0
            for other in selected
        ):
            selected.append(hole)
        if len(selected) == 3:
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


# Handle hough circle support.
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


# Choose best circle pair.
def _choose_best_circle_pair(circles, box_w, box_h):
    if len(circles) < 2:
        return circles[:2]

    same_edge_pair = _choose_same_edge_pair(circles, box_w, box_h)
    if same_edge_pair is not None:
        return same_edge_pair

    best_pair = None
    best_score = None

    for idx_a in range(len(circles)):
        for idx_b in range(idx_a + 1, len(circles)):
            circ_a = circles[idx_a]
            circ_b = circles[idx_b]
            dx = abs(float(circ_a["cx"]) - float(circ_b["cx"]))
            dy = abs(float(circ_a["cy"]) - float(circ_b["cy"]))
            main_sep = max(dx, dy)
            cross_sep = min(dx, dy)
            if main_sep < 12.0:
                continue
            if cross_sep > 0.25 * main_sep + 4.0:
                continue

            pair_score = (
                float(circ_a["support"]) +
                float(circ_b["support"]) +
                0.15 * float(main_sep) -
                0.05 * float(cross_sep)
            )
            key = (
                round(pair_score, 4),
                round(float(main_sep), 4),
                -round(float(cross_sep), 4),
            )
            if best_pair is None or key > best_score:
                best_pair = (circ_a, circ_b)
                best_score = key

    if best_pair is not None:
        return list(best_pair)

    best_pair = None
    best_distance = -1.0
    for idx_a in range(len(circles)):
        for idx_b in range(idx_a + 1, len(circles)):
            circ_a = circles[idx_a]
            circ_b = circles[idx_b]
            dx = float(circ_a["cx"]) - float(circ_b["cx"])
            dy = float(circ_a["cy"]) - float(circ_b["cy"])
            distance_sq = dx * dx + dy * dy
            if distance_sq > best_distance:
                best_pair = (circ_a, circ_b)
                best_distance = distance_sq
    return list(best_pair) if best_pair is not None else circles[:2]


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


# Handle merge meter post candidates.
def _merge_meter_post_candidates(candidates):
    merged = []
    for cand in candidates:
        merged_into_existing = False
        for existing in merged:
            if (
                abs(float(cand["cx"]) - float(existing["cx"])) <= 8.0
                and abs(float(cand["cy"]) - float(existing["cy"])) <= 8.0
            ):
                if float(cand.get("support", 0.0)) > float(existing.get("support", 0.0)):
                    existing.update(cand)
                merged_into_existing = True
                break
        if not merged_into_existing:
            merged.append(dict(cand))
    return merged


# Handle eligible edges for point.
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


# Build meter post candidates.
def _build_meter_post_candidates(binary, search_box, holes):
    x1, y1, x2, y2 = [int(round(v)) for v in search_box]
    box_w = max(int(x2 - x1 + 1), 1)
    box_h = max(int(y2 - y1 + 1), 1)

    candidates = []
    for hole in holes:
        local_cx = float(hole["cx"]) - float(x1)
        local_cy = float(hole["cy"]) - float(y1)
        eligible_edges, edge_distances = _eligible_edges_for_point(local_cx, local_cy, box_w, box_h)
        candidates.append({
            "cx": float(hole["cx"]),
            "cy": float(hole["cy"]),
            "radius": float(max(hole.get("width", 0), hole.get("height", 0)) / 2.0),
            "support": float(max(hole.get("width", 0), hole.get("height", 0), 8)),
            "source": "contour_hole",
            "eligible_edges": eligible_edges,
            "edge_distances": edge_distances,
            "area": float(hole.get("area", 0.0)),
        })

    for circle in _find_hough_post_circles(binary, search_box):
        local_cx = float(circle["cx"]) - float(x1)
        local_cy = float(circle["cy"]) - float(y1)
        eligible_edges, edge_distances = _eligible_edges_for_point(local_cx, local_cy, box_w, box_h)
        circle_copy = dict(circle)
        circle_copy["source"] = "hough_circle"
        circle_copy["eligible_edges"] = eligible_edges
        circle_copy["edge_distances"] = edge_distances
        candidates.append(circle_copy)

    return _merge_meter_post_candidates(candidates)


# Handle meter edge scan scores.
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


# Score meter edge pair.
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
    final_score = raw_circle_score * balance + 1.0 * scan_sum - 0.4 * scan_diff

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
    }


# Handle meter candidate side support.
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


# Score meter opposite pair.
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


# Handle select meter post pair.
def _select_meter_post_pair(binary, search_box, candidates):
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
    best_structured_opposite_pair = None
    best_structured_opposite_debug = None
    best_structured_opposite_key = None
    best_same_edge = {}

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
                key = (
                    round(float(pair_debug["score"]), 4),
                    round(float(pair_debug["span"]), 4),
                    -round(float(pair_debug["alignment"]), 4),
                )
                if best_pair is None or key > best_key:
                    best_pair = (cand_a, cand_b)
                    best_pair_debug = pair_debug
                    best_key = key
                if pair_debug.get("shared_secondary_edges"):
                    if best_structured_opposite_pair is None or key > best_structured_opposite_key:
                        best_structured_opposite_pair = (cand_a, cand_b)
                        best_structured_opposite_debug = pair_debug
                        best_structured_opposite_key = key

    if (
        best_structured_opposite_pair is not None
        and best_pair is not None
        and float(best_structured_opposite_debug.get("score", 0.0)) >= float(best_pair_debug.get("score", 0.0)) - 25.0
    ):
        best_pair = best_structured_opposite_pair
        best_pair_debug = best_structured_opposite_debug
        best_key = best_structured_opposite_key

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

    return best_pair, best_pair_debug, scan_scores


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
    selected_pair, pair_debug, scan_scores = _select_meter_post_pair(binary, search_box, candidates)

    if selected_pair is None:
        x1, y1, x2, y2 = search_box
        width = max(float(x2 - x1), 1.0)
        height = max(float(y2 - y1), 1.0)
        return [
            {
                "name": "t1",
                "relative_position": "left",
                "point": [round(float(x1 - TERMINAL_OUTWARD_OFFSET), 2), round(float(y1 + 0.62 * height), 2)],
            },
            {
                "name": "t2",
                "relative_position": "bottom",
                "point": [round(float(x1 + 0.78 * width), 2), round(float(y2 + TERMINAL_OUTWARD_OFFSET), 2)],
            },
        ], None, None, {
            "strategy": "analog_meter_by_posts",
            "fallback": True,
            "reason": "post_holes_not_found",
            "inner_box": inner_box,
            "search_box": [round(float(v), 2) for v in search_box],
            "n_candidates": int(len(candidates)),
        }

    selected = list(selected_pair)
    hole_a, hole_b = selected[0], selected[1]
    dx = abs(float(hole_a["cx"]) - float(hole_b["cx"]))
    dy = abs(float(hole_a["cy"]) - float(hole_b["cy"]))
    if pair_debug.get("layout") == "opposite_edges":
        side_a, side_b = pair_debug["edge_pair"]
        if {side_a, side_b} == {"left", "right"}:
            selected = sorted(
                ((side_a, hole_a), (side_b, hole_b)),
                key=lambda item: 0 if item[0] == "left" else 1,
            )
            orientation = "horizontal"
            relative_positions = tuple(side for side, _ in selected)
            selected = [hole for _, hole in selected]
            axis = "left_right_posts"
        else:
            selected = sorted(
                ((side_a, hole_a), (side_b, hole_b)),
                key=lambda item: 0 if item[0] == "top" else 1,
            )
            orientation = "vertical"
            relative_positions = tuple(side for side, _ in selected)
            selected = [hole for _, hole in selected]
            axis = "top_bottom_posts"
    else:
        selected_edge = pair_debug["edge"]
        if selected_edge in {"top", "bottom"}:
            selected = sorted(selected, key=lambda hole: float(hole["cx"]))
            orientation = "horizontal"
            relative_positions = (selected_edge, selected_edge)
            axis = f"{selected_edge}_edge_posts"
        else:
            selected = sorted(selected, key=lambda hole: float(hole["cy"]))
            orientation = "vertical"
            relative_positions = (selected_edge, selected_edge)
            axis = f"{selected_edge}_edge_posts"

    terminals_def = []
    for term_name, rel_pos, hole in zip(("t1", "t2"), relative_positions, selected):
        terminals_def.append(
            {
                "name": term_name,
                "relative_position": rel_pos,
                "point": [
                    round(float(hole["cx"]), 2),
                    round(float(hole["cy"]), 2),
                ],
            }
        )

    return terminals_def, orientation, None, {
        "strategy": "analog_meter_by_posts",
        "fallback": False,
        "post_axis": axis,
        "inner_box": [round(float(v), 2) for v in inner_box] if inner_box is not None else None,
        "search_box": [round(float(v), 2) for v in search_box],
        "selected_pair_debug": pair_debug,
        "edge_scan_scores": {
            edge: [int(pair[0].get("max_score", 0)), int(pair[1].get("max_score", 0))]
            for edge, pair in scan_scores.items()
        },
        "n_candidates": int(len(candidates)),
        "posts": [
            {
                "cx": round(float(hole["cx"]), 2),
                "cy": round(float(hole["cy"]), 2),
                "area": round(float(hole["area"]), 2),
                "source": hole.get("source"),
            }
            for hole in selected
        ],
        "post_separation": {
            "dx": round(float(dx), 2),
            "dy": round(float(dy), 2),
        },
    }


# Handle scan external wire y.
def _scan_external_wire_y(binary, box, side, outward_len=18, inward_len=8, halfspan=5):
    x1, y1, x2, y2 = [int(round(v)) for v in box]
    height = max(y2 - y1, 1)
    margin = max(4, int(round(height * 0.03)))
    start = min(max(y1 + margin, y1), y2)
    end = max(min(y2 - margin, y2), start)
    coords = list(range(start, end + 1))
    if not coords:
        coords = [int(round((y1 + y2) / 2.0))]

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


# Handle scan external wire y in range.
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


# Handle scan external wire x in range.
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
