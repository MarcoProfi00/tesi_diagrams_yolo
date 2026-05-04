import cv2

from .geometry import geom_clamp_bbox_to_image, geom_infer_orientation_from_bbox
from .image_ops import img_count_foreground_pixels
from .strategies_integrated_circuit import (
    _anchor_offset_ratio,
    _make_terminal_point,
    refine_ic_body_bbox,
)


CONNECTOR_CENTER_BAND_RATIO = 0.48
CONNECTOR_MIN_PROJECTION_SCORE = 2
CONNECTOR_KEEP_RATIO = 0.36
CONNECTOR_MAX_GAP = 6
CONNECTOR_SIDE_PROBE_OUT_LEN = 12
CONNECTOR_SIDE_PROBE_INSET = 2
CONNECTOR_SIDE_PROBE_HALFSPAN_MIN = 3
CONNECTOR_SIDE_PROBE_HALFSPAN_MAX = 8
CONNECTOR_EDGE_CONTACT_MIN_PINS = 2
CONNECTOR_EDGE_MIN_PROJECTION_SCORE = 3
CONNECTOR_EDGE_KEEP_RATIO = 0.45
CONNECTOR_EDGE_MAX_GAP = 3


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


# Handle projection groups.
def _projection_groups(values):
    if not values:
        return [], 0

    max_score = max(values)
    threshold = max(CONNECTOR_MIN_PROJECTION_SCORE, int(round(max_score * CONNECTOR_KEEP_RATIO)))
    kept = [i for i, score in enumerate(values) if score >= threshold]
    return _group_close_indices(kept, max_gap=CONNECTOR_MAX_GAP), threshold


# Handle merge close centers.
def _merge_close_centers(centers, min_separation):
    if not centers:
        return []

    merged = [float(centers[0])]
    for center in centers[1:]:
        if float(center) - merged[-1] < float(min_separation):
            merged[-1] = (merged[-1] + float(center)) / 2.0
        else:
            merged.append(float(center))
    return [int(round(c)) for c in merged]


# Detect connector hole centers.
def _detect_connector_hole_centers(binary, bbox, orientation):
    x1, y1, x2, y2 = bbox
    if x2 <= x1 or y2 <= y1:
        return []

    roi = binary[y1:y2 + 1, x1:x2 + 1]
    contours, hierarchy = cv2.findContours(
        roi,
        cv2.RETR_CCOMP,
        cv2.CHAIN_APPROX_SIMPLE,
    )
    if hierarchy is None:
        return []

    width = max(x2 - x1 + 1, 1)
    height = max(y2 - y1 + 1, 1)
    hierarchy = hierarchy[0]
    centers = []

    for idx, cnt in enumerate(contours):
        parent_idx = int(hierarchy[idx][3])
        if parent_idx < 0:
            continue

        hx, hy, hw, hh = cv2.boundingRect(cnt)
        area = float(cv2.contourArea(cnt))
        if hw < 10 or hh < 10:
            continue

        ratio = hw / float(max(hh, 1))
        if not (0.72 <= ratio <= 1.38):
            continue

        if orientation == "vertical":
            if hw > max(28, int(round(width * 0.38))) or hh > max(28, int(round(width * 0.38))):
                continue
            cx = hx + (hw / 2.0)
            if not (width * 0.28 <= cx <= width * 0.82):
                continue
        else:
            if hw > max(28, int(round(height * 0.38))) or hh > max(28, int(round(height * 0.38))):
                continue
            cy = hy + (hh / 2.0)
            if not (height * 0.28 <= cy <= height * 0.82):
                continue

        if area < 120.0 or area > 500.0:
            continue

        if orientation == "vertical":
            centers.append(int(round(y1 + hy + (hh / 2.0))))
        else:
            centers.append(int(round(x1 + hx + (hw / 2.0))))

    if orientation == "vertical":
        min_gap = max(18, int(round(height * 0.10)))
    else:
        min_gap = max(18, int(round(width * 0.10)))
    return _merge_close_centers(sorted(centers), min_separation=min_gap)


# Handle side probe halfspan.
def _side_probe_halfspan(width, height):
    min_dim = max(1, min(width, height))
    halfspan = int(round(min_dim * 0.12))
    halfspan = max(CONNECTOR_SIDE_PROBE_HALFSPAN_MIN, halfspan)
    halfspan = min(CONNECTOR_SIDE_PROBE_HALFSPAN_MAX, halfspan)
    return halfspan


# Handle side score vertical.
def _side_score_vertical(binary, bbox, center_y, side, halfspan):
    x1, y1, x2, y2 = bbox
    if side == "left":
        return img_count_foreground_pixels(
            binary,
            x1 - CONNECTOR_SIDE_PROBE_OUT_LEN,
            center_y - halfspan,
            x1 + CONNECTOR_SIDE_PROBE_INSET + 1,
            center_y + halfspan + 1,
        )

    return img_count_foreground_pixels(
        binary,
        x2 - CONNECTOR_SIDE_PROBE_INSET,
        center_y - halfspan,
        x2 + CONNECTOR_SIDE_PROBE_OUT_LEN + 1,
        center_y + halfspan + 1,
    )


# Handle side score horizontal.
def _side_score_horizontal(binary, bbox, center_x, side, halfspan):
    x1, y1, x2, y2 = bbox
    if side == "top":
        return img_count_foreground_pixels(
            binary,
            center_x - halfspan,
            y1 - CONNECTOR_SIDE_PROBE_OUT_LEN,
            center_x + halfspan + 1,
            y1 + CONNECTOR_SIDE_PROBE_INSET + 1,
        )

    return img_count_foreground_pixels(
        binary,
        center_x - halfspan,
        y2 - CONNECTOR_SIDE_PROBE_INSET,
        center_x + halfspan + 1,
        y2 + CONNECTOR_SIDE_PROBE_OUT_LEN + 1,
    )


# Build connector body refinement meta.
def _connector_body_refinement_meta(bbox):
    x1, y1, x2, y2 = bbox
    width = max(int(round(x2 - x1 + 1)), 1)
    height = max(int(round(y2 - y1 + 1)), 1)
    min_dim = max(1, min(width, height))

    return {
        "body_refinement": {
            "enabled": True,
            "min_body_width_px": max(14, int(round(width * 0.40))),
            "min_body_height_px": max(14, int(round(height * 0.40))),
            "outer_parallel_edge_gap_px": max(6, int(round(min_dim * 0.12))),
        }
    }


# Build edge contact cfg.
def _connector_edge_contact_cfg(body_bbox):
    x1, y1, x2, y2 = body_bbox
    width = max(int(round(x2 - x1 + 1)), 1)
    height = max(int(round(y2 - y1 + 1)), 1)
    min_dim = max(1, min(width, height))
    max_dim = max(width, height)

    return {
        "sides": ["left", "right", "top", "bottom"],
        "outward_probe_px": max(12, int(round(max_dim * 0.22))),
        "corner_exclusion_ratio": 0.03,
    }


# Handle connector side order.
def _connector_side_order(orientation):
    if orientation == "horizontal":
        return ("left", "top", "bottom", "right")
    return ("top", "left", "right", "bottom")


# Handle external projection groups.
def _external_projection_groups(values):
    if not values:
        return [], 0

    max_score = max(values)
    threshold = max(CONNECTOR_EDGE_MIN_PROJECTION_SCORE, int(round(max_score * CONNECTOR_EDGE_KEEP_RATIO)))
    kept = [i for i, score in enumerate(values) if score >= threshold]
    return _group_close_indices(kept, max_gap=CONNECTOR_EDGE_MAX_GAP), threshold


# Build side external projection.
def _build_side_external_projection(binary, body_bbox, side, cfg):
    x1, y1, x2, y2 = body_bbox
    width = max(int(round(x2 - x1 + 1)), 1)
    height = max(int(round(y2 - y1 + 1)), 1)
    corner_skip_y = max(1, int(round(height * cfg["corner_exclusion_ratio"])))
    corner_skip_x = max(1, int(round(width * cfg["corner_exclusion_ratio"])))
    outward = int(cfg["outward_probe_px"])

    if side == "left":
        return [
            img_count_foreground_pixels(binary, x1 - outward, y, x1, y + 1)
            for y in range(y1 + corner_skip_y, y2 - corner_skip_y + 1)
        ], y1 + corner_skip_y

    if side == "right":
        return [
            img_count_foreground_pixels(binary, x2 + 1, y, x2 + outward + 1, y + 1)
            for y in range(y1 + corner_skip_y, y2 - corner_skip_y + 1)
        ], y1 + corner_skip_y

    if side == "top":
        return [
            img_count_foreground_pixels(binary, x, y1 - outward, x + 1, y1)
            for x in range(x1 + corner_skip_x, x2 - corner_skip_x + 1)
        ], x1 + corner_skip_x

    return [
        img_count_foreground_pixels(binary, x, y2 + 1, x + 1, y2 + outward + 1)
        for x in range(x1 + corner_skip_x, x2 - corner_skip_x + 1)
    ], x1 + corner_skip_x


# Handle build connector edge contacts.
def _build_connector_edge_contacts(binary, bbox, orientation):
    body_meta = _connector_body_refinement_meta(bbox)
    body_bbox, body_debug = refine_ic_body_bbox(binary, bbox, body_meta)
    cfg = _connector_edge_contact_cfg(body_bbox)
    if orientation == "horizontal":
        cfg["sides"] = ["top", "bottom"]
    else:
        cfg["sides"] = ["left", "right"]

    rows_by_side = {}
    projection_debug = {}
    active_sides = []

    for side in cfg["sides"]:
        projection, start_coord = _build_side_external_projection(
            binary,
            body_bbox,
            side,
            cfg,
        )
        groups, threshold = _external_projection_groups(projection)
        centers = [
            start_coord + int(round((group[0] + group[-1]) / 2.0))
            for group in groups
        ]
        rows_by_side[side] = centers
        projection_debug[side] = {
            "max_score": int(max(projection) if projection else 0),
            "threshold": int(threshold),
            "group_count": len(groups),
            "centers": [int(center) for center in centers],
        }
        if centers:
            active_sides.append(side)

    terminals_def = []
    debug_rows = []
    pin_index = 1

    for side in _connector_side_order(orientation):
        centers = sorted(rows_by_side.get(side, []))

        for center in centers:
            anchor_ratio = _anchor_offset_ratio(body_bbox, side, center)
            point = _make_terminal_point(body_bbox, side, center)
            terminals_def.append({
                "name": f"pin{pin_index}",
                "relative_position": side,
                "anchor_offset_ratio": anchor_ratio,
                "point": point,
                "point_debug": {
                    "point_mode": "connector_body_edge_contact",
                    "body_bbox": [int(v) for v in body_bbox],
                    "side": side,
                    "coord": int(center),
                    "anchor_offset_ratio": anchor_ratio,
                    "external_projection": projection_debug.get(side, {}),
                },
            })
            debug_rows.append({
                "pin_name": f"pin{pin_index}",
                "side": side,
                "coord": int(center),
                "point": point,
                "anchor_offset_ratio": anchor_ratio,
                "external_projection": projection_debug.get(side, {}),
            })
            pin_index += 1

    total_best_score = sum(
        int(side_debug.get("max_score", 0))
        for side_debug in projection_debug.values()
    )
    estimated_orientation = "multi_side" if len(active_sides) > 1 else orientation

    return terminals_def, estimated_orientation, {
        "decision_mode": "connector_body_edge_contacts",
        "pin_count": len(terminals_def),
        "active_sides": active_sides,
        "body_bbox": [int(v) for v in body_bbox],
        "body_refinement": body_debug,
        "pin_detection_cfg": cfg,
        "external_side_projection": projection_debug,
        "total_best_score": int(total_best_score),
        "rows": debug_rows,
    }


# Handle projection selected scores.
def _projection_selected_scores(debug_rows):
    scores = []

    for row in debug_rows:
        if "left_score" in row and "right_score" in row:
            scores.append(max(int(row.get("left_score", 0)), int(row.get("right_score", 0))))
        elif "top_score" in row and "bottom_score" in row:
            scores.append(max(int(row.get("top_score", 0)), int(row.get("bottom_score", 0))))

    return scores


# Handle should use edge contacts.
def _should_use_edge_contacts(projection_debug, edge_debug):
    if bool(projection_debug.get("used_hole_detection")):
        return False, "hole_detection_already_reliable"

    projection_pin_count = int(projection_debug.get("pin_count", 0))
    edge_pin_count = int(edge_debug.get("pin_count", 0))

    if edge_pin_count < CONNECTOR_EDGE_CONTACT_MIN_PINS:
        return False, "edge_contact_pin_count_too_low"

    projection_scores = _projection_selected_scores(projection_debug.get("rows", []))
    projection_max_score = max(projection_scores, default=0)
    projection_total_score = sum(projection_scores)
    projection_zero_rows = sum(1 for score in projection_scores if score <= 0)

    if projection_max_score <= 0 and edge_pin_count >= projection_pin_count:
        return True, "projection_side_scores_missing"

    if (
        edge_pin_count >= projection_pin_count + 2
        and projection_zero_rows * 2 >= max(projection_pin_count, 1)
    ):
        return True, "projection_pin_count_incomplete"

    edge_total_score = int(edge_debug.get("total_best_score", 0))
    if (
        edge_pin_count >= projection_pin_count
        and edge_total_score > 0
        and projection_total_score <= 0
    ):
        return True, "edge_contacts_have_real_wire_support"

    return False, "projection_result_kept"


# Build vertical connector.
def _build_vertical_connector(binary, bbox):
    x1, y1, x2, y2 = bbox
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)

    band_half = max(2, int(round(width * CONNECTOR_CENTER_BAND_RATIO / 2.0)))
    xc = int(round((x1 + x2) / 2))
    bx1 = max(x1, xc - band_half)
    bx2 = min(x2, xc + band_half)

    centers = _detect_connector_hole_centers(binary, bbox, orientation="vertical")
    threshold = None
    projection = []
    used_hole_detection = bool(centers)

    if not centers:
        projection = [
            img_count_foreground_pixels(binary, bx1, y, bx2 + 1, y + 1)
            for y in range(y1, y2 + 1)
        ]
        groups, threshold = _projection_groups(projection)
        if not groups:
            mid = int(round((y1 + y2) / 2))
            groups = [[mid - y1]]

        centers = [
            y1 + int(round((group[0] + group[-1]) / 2.0))
            for group in groups
        ]
        centers = _merge_close_centers(
            centers,
            min_separation=max(18, int(round(height * 0.10))),
        )

    halfspan = _side_probe_halfspan(width, height)
    terminals_def = []
    row_debug = []

    for idx, center_y in enumerate(centers, start=1):
        left_score = _side_score_vertical(binary, bbox, center_y, "left", halfspan)
        right_score = _side_score_vertical(binary, bbox, center_y, "right", halfspan)
        relative_position = "left" if left_score > right_score else "right"

        terminals_def.append({
            "name": f"pin{idx}",
            "relative_position": relative_position,
            "anchor_offset_ratio": round((center_y - y1) / float(max(height, 1)), 4),
        })
        row_debug.append({
            "pin_name": f"pin{idx}",
            "center_y": center_y,
            "left_score": int(left_score),
            "right_score": int(right_score),
            "selected_side": relative_position,
        })

    return terminals_def, {
        "decision_mode": "connector_vertical_holes" if used_hole_detection else "connector_vertical_projection",
        "projection_axis": "y",
        "projection_threshold": threshold,
        "projection_band_x1": bx1,
        "projection_band_x2": bx2,
        "pin_count": len(terminals_def),
        "used_hole_detection": bool(used_hole_detection),
        "rows": row_debug,
    }


# Build horizontal connector.
def _build_horizontal_connector(binary, bbox):
    x1, y1, x2, y2 = bbox
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)

    band_half = max(2, int(round(height * CONNECTOR_CENTER_BAND_RATIO / 2.0)))
    yc = int(round((y1 + y2) / 2))
    by1 = max(y1, yc - band_half)
    by2 = min(y2, yc + band_half)

    centers = _detect_connector_hole_centers(binary, bbox, orientation="horizontal")
    threshold = None
    used_hole_detection = bool(centers)

    if not centers:
        projection = [
            img_count_foreground_pixels(binary, x, by1, x + 1, by2 + 1)
            for x in range(x1, x2 + 1)
        ]
        groups, threshold = _projection_groups(projection)
        if not groups:
            mid = int(round((x1 + x2) / 2))
            groups = [[mid - x1]]

        centers = [
            x1 + int(round((group[0] + group[-1]) / 2.0))
            for group in groups
        ]
        centers = _merge_close_centers(
            centers,
            min_separation=max(18, int(round(width * 0.10))),
        )

    halfspan = _side_probe_halfspan(width, height)
    terminals_def = []
    row_debug = []

    for idx, center_x in enumerate(centers, start=1):
        top_score = _side_score_horizontal(binary, bbox, center_x, "top", halfspan)
        bottom_score = _side_score_horizontal(binary, bbox, center_x, "bottom", halfspan)
        relative_position = "top" if top_score > bottom_score else "bottom"

        terminals_def.append({
            "name": f"pin{idx}",
            "relative_position": relative_position,
            "anchor_offset_ratio": round((center_x - x1) / float(max(width, 1)), 4),
        })
        row_debug.append({
            "pin_name": f"pin{idx}",
            "center_x": center_x,
            "top_score": int(top_score),
            "bottom_score": int(bottom_score),
            "selected_side": relative_position,
        })

    return terminals_def, {
        "decision_mode": "connector_horizontal_holes" if used_hole_detection else "connector_horizontal_projection",
        "projection_axis": "x",
        "projection_threshold": threshold,
        "projection_band_y1": by1,
        "projection_band_y2": by2,
        "pin_count": len(terminals_def),
        "used_hole_detection": bool(used_hole_detection),
        "rows": row_debug,
    }


# Detect connector terminals.
def detect_connector_terminals(meta: dict, binary, bbox, default_orientation="vertical"):
    bbox = geom_clamp_bbox_to_image(bbox, binary.shape)
    orientation = geom_infer_orientation_from_bbox(
        bbox,
        default_orientation=default_orientation,
    )

    if orientation == "vertical":
        terminals_def, debug = _build_vertical_connector(binary, bbox)
    else:
        terminals_def, debug = _build_horizontal_connector(binary, bbox)

    projection_debug = debug
    final_orientation = orientation
    selection_reason = "projection_result_kept"

    if not bool(projection_debug.get("used_hole_detection")):
        edge_terminals_def, edge_orientation, edge_debug = _build_connector_edge_contacts(
            binary,
            bbox,
            orientation,
        )
        use_edge_contacts, selection_reason = _should_use_edge_contacts(
            projection_debug,
            edge_debug,
        )

        projection_debug["edge_contact_candidate"] = {
            "pin_count": int(edge_debug.get("pin_count", 0)),
            "active_sides": edge_debug.get("active_sides", []),
            "total_best_score": int(edge_debug.get("total_best_score", 0)),
            "selection_reason": selection_reason,
        }

        if use_edge_contacts:
            terminals_def = edge_terminals_def
            debug = edge_debug
            final_orientation = edge_orientation
            debug["projection_candidate"] = {
                "pin_count": int(projection_debug.get("pin_count", 0)),
                "used_hole_detection": bool(projection_debug.get("used_hole_detection")),
                "decision_mode": projection_debug.get("decision_mode"),
                "rows": projection_debug.get("rows", []),
            }
        else:
            debug = projection_debug

    debug["estimated_orientation"] = orientation
    debug["resolved_orientation"] = final_orientation
    debug["selection_reason"] = selection_reason
    debug["strategy"] = meta.get("terminal_strategy", "connector_by_projection")
    return terminals_def, final_orientation, debug
