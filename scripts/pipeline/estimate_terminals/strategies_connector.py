import cv2

from .geometry import geom_clamp_bbox_to_image, geom_infer_orientation_from_bbox
from .image_ops import img_count_foreground_pixels


CONNECTOR_CENTER_BAND_RATIO = 0.48
CONNECTOR_MIN_PROJECTION_SCORE = 2
CONNECTOR_KEEP_RATIO = 0.36
CONNECTOR_MAX_GAP = 6
CONNECTOR_SIDE_PROBE_OUT_LEN = 12
CONNECTOR_SIDE_PROBE_INSET = 2
CONNECTOR_SIDE_PROBE_HALFSPAN_MIN = 3
CONNECTOR_SIDE_PROBE_HALFSPAN_MAX = 8


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


def _projection_groups(values):
    if not values:
        return [], 0

    max_score = max(values)
    threshold = max(CONNECTOR_MIN_PROJECTION_SCORE, int(round(max_score * CONNECTOR_KEEP_RATIO)))
    kept = [i for i, score in enumerate(values) if score >= threshold]
    return _group_close_indices(kept, max_gap=CONNECTOR_MAX_GAP), threshold


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


def _detect_connector_hole_centers(binary, bbox, orientation):
    """Trova i centri dei pin interni del connector usando i fori circolari visibili nel simbolo."""
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


def _side_probe_halfspan(width, height):
    min_dim = max(1, min(width, height))
    halfspan = int(round(min_dim * 0.12))
    halfspan = max(CONNECTOR_SIDE_PROBE_HALFSPAN_MIN, halfspan)
    halfspan = min(CONNECTOR_SIDE_PROBE_HALFSPAN_MAX, halfspan)
    return halfspan


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

    debug["estimated_orientation"] = orientation
    debug["strategy"] = meta.get("terminal_strategy", "connector_by_projection")
    return terminals_def, orientation, debug
