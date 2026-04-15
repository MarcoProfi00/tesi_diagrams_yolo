import cv2

from .config import TERMINAL_OUTWARD_OFFSET
from .geometry import geom_clamp_bbox_to_image


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


def _find_circular_holes(binary, box, min_area=180.0, max_area=500.0):
    x1, y1, x2, y2 = [int(round(v)) for v in box]
    roi = binary[y1:y2 + 1, x1:x2 + 1]
    contours, hierarchy = cv2.findContours(roi, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    if hierarchy is None:
        return []

    holes = []
    hierarchy = hierarchy[0]
    for idx, cnt in enumerate(contours):
        if int(hierarchy[idx][3]) < 0:
            continue

        hx, hy, hw, hh = cv2.boundingRect(cnt)
        if hw < 12 or hh < 12 or hw > 32 or hh > 32:
            continue

        ratio = hw / float(max(hh, 1))
        if not (0.7 <= ratio <= 1.4):
            continue

        area = float(cv2.contourArea(cnt))
        if not (float(min_area) <= area <= float(max_area)):
            continue

        holes.append({
            "cx": float(x1 + hx + (hw / 2.0)),
            "cy": float(y1 + hy + (hh / 2.0)),
            "width": int(hw),
            "height": int(hh),
            "area": float(area),
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


def _bottom_stub_score(binary, box, hole):
    x1, y1, x2, y2 = [int(round(v)) for v in box]
    cx = int(round(float(hole["cx"])))
    cy = int(round(float(hole["cy"])))
    radius = max(int(hole["width"]), int(hole["height"])) // 2 + 2
    ya = min(binary.shape[0], cy + radius)
    yb = min(binary.shape[0], cy + radius + 40)
    xa = max(0, cx - 2)
    xb = min(binary.shape[1], cx + 3)
    if yb <= ya or xb <= xa:
        return 0
    return int(cv2.countNonZero(binary[ya:yb, xa:xb]))


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
    if inner_box is None:
        x1, y1, x2, y2 = det_box
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
            "reason": "inner_box_not_found",
        }

    holes = _find_circular_holes(binary, inner_box)
    if len(holes) < 2:
        x1, y1, x2, y2 = inner_box
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
        }

    selected = sorted(holes[:2], key=lambda hole: float(hole["area"]), reverse=True)
    for hole in selected:
        hole["bottom_stub_score"] = _bottom_stub_score(binary, inner_box, hole)

    output_hole = max(
        selected,
        key=lambda hole: (
            int(hole["bottom_stub_score"]),
            float(hole["cx"]),
            float(hole["cy"]),
        ),
    )
    input_hole = next(hole for hole in selected if hole is not output_hole)

    terminals_def = [
        {
            "name": "t1",
            "relative_position": "left",
            "point": [
                round(float(inner_box[0] - TERMINAL_OUTWARD_OFFSET), 2),
                round(float(input_hole["cy"]), 2),
            ],
        },
        {
            "name": "t2",
            "relative_position": "bottom",
            "point": [
                round(float(output_hole["cx"]), 2),
                round(float(inner_box[3] + TERMINAL_OUTWARD_OFFSET), 2),
            ],
        },
    ]

    return terminals_def, None, None, {
        "strategy": "analog_meter_by_posts",
        "fallback": False,
        "inner_box": [round(float(v), 2) for v in inner_box],
        "posts": [
            {
                "cx": round(float(hole["cx"]), 2),
                "cy": round(float(hole["cy"]), 2),
                "area": round(float(hole["area"]), 2),
                "bottom_stub_score": int(hole["bottom_stub_score"]),
            }
            for hole in selected
        ],
        "selected_input_post": {
            "cx": round(float(input_hole["cx"]), 2),
            "cy": round(float(input_hole["cy"]), 2),
        },
        "selected_output_post": {
            "cx": round(float(output_hole["cx"]), 2),
            "cy": round(float(output_hole["cy"]), 2),
        },
    }


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


def detect_transformer_terminals(meta: dict, binary, bbox):
    del meta

    det_box = [float(v) for v in geom_clamp_bbox_to_image(bbox, binary.shape)]
    left_y, left_debug = _scan_external_wire_y(binary, det_box, side="left")
    right_y, right_debug = _scan_external_wire_y(binary, det_box, side="right")
    x1, y1, x2, y2 = det_box
    height = max(float(y2 - y1), 1.0)

    left_score = int(left_debug.get("max_score", 0))
    right_score = int(right_debug.get("max_score", 0))
    if left_score <= 0 and right_score > 0:
        left_y = right_y
        left_debug["mirrored_from_opposite_side"] = True
    elif right_score <= 0 and left_score > 0:
        right_y = left_y
        right_debug["mirrored_from_opposite_side"] = True
    elif abs(float(left_y) - float(right_y)) > 0.18 * height:
        if right_score > left_score * 1.15:
            left_y = right_y
            left_debug["mirrored_from_opposite_side"] = True
        elif left_score > right_score * 1.15:
            right_y = left_y
            right_debug["mirrored_from_opposite_side"] = True

    terminals_def = [
        {
            "name": "t1",
            "relative_position": "left",
            "point": [round(float(x1 - TERMINAL_OUTWARD_OFFSET), 2), round(float(left_y), 2)],
        },
        {
            "name": "t2",
            "relative_position": "right",
            "point": [round(float(x2 + TERMINAL_OUTWARD_OFFSET), 2), round(float(right_y), 2)],
        },
    ]
    return terminals_def, "horizontal", None, {
        "strategy": "transformer_external_wires",
        "bbox": [round(float(v), 2) for v in det_box],
        "left_debug": left_debug,
        "right_debug": right_debug,
    }
