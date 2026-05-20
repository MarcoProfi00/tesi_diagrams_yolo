"""
Per ogni IC:
    1. prendi bbox IC
    2. considera quel bbox come body_bbox provvisorio
    3. scansiona quattro lati: left, right, top, bottom
    4. cerca fili che attraversano il bordo del rettangolo
    5. ogni attraversamento diventa un terminale
    6. fondi candidati troppo vicini
    7. ordina i terminali per lato
"""

"""
Strategia per Integrated_Circuit.

Prima versione:
- niente OCR;
- body_bbox raffinato in modo leggero cercando i lati rettangolari;
- terminali stimati dai fili che entrano/escono dal corpo IC;
- terminali variabili sui quattro lati.
"""

import cv2
import numpy as np

from .config import TERMINAL_OUTWARD_OFFSET
from .geometry import geom_clamp_bbox_to_image
# =========================================================
# LOW LEVEL HELPERS
# =========================================================
def _get_pin_cfg(meta: dict) -> dict:
    cfg = meta.get("pin_detection", {}) or {}

    return {
        "sides": cfg.get("sides", ["left", "right", "top", "bottom"]),
        "require_wire_contact": bool(cfg.get("require_wire_contact", True)),
        "scan_band_px": int(cfg.get("scan_band_px", 18)),
        "outward_probe_px": int(cfg.get("outward_probe_px", 28)),
        "inward_probe_px": int(cfg.get("inward_probe_px", 6)),
        "min_contact_run_px": int(cfg.get("min_contact_run_px", 5)),
        "min_wire_length_px": int(cfg.get("min_wire_length_px", 14)),
        "merge_gap_px": int(cfg.get("merge_gap_px", 10)),
        "corner_exclusion_ratio": float(cfg.get("corner_exclusion_ratio", 0.04)),
        "adaptive_upscale_enabled": bool(cfg.get("adaptive_upscale_enabled", True)),
        "adaptive_upscale_min_body_dim_px": int(cfg.get("adaptive_upscale_min_body_dim_px", 140)),
        "adaptive_upscale_target_body_dim_px": int(cfg.get("adaptive_upscale_target_body_dim_px", 180)),
        "adaptive_upscale_max_scale": float(cfg.get("adaptive_upscale_max_scale", 2.5)),
    }

def _get_naming_cfg(meta: dict) -> dict:
    cfg = meta.get("terminal_naming", {}) or {}

    return {
        "fallback_name_pattern": cfg.get("fallback_name_pattern", "{side}_{index}"),
        "side_order": cfg.get(
            "side_order",
            {
                "left": "top_to_bottom",
                "right": "top_to_bottom",
                "top": "left_to_right",
                "bottom": "left_to_right",
            },
        ),
    }

def _group_close_indices(indices, max_gap=1):
    if not indices:
        return []

    groups = [[int(indices[0])]]
    for idx in indices[1:]:
        idx = int(idx)
        if idx <= groups[-1][-1] + max_gap:
            groups[-1].append(idx)
        else:
            groups.append([idx])
    return groups

def _foreground_runs_1d(values):
    idxs = np.flatnonzero(values > 0)
    if idxs.size == 0:
        return []

    runs = []
    start = prev = int(idxs[0])

    for idx in idxs[1:]:
        idx = int(idx)
        if idx > prev + 1:
            runs.append((start, prev))
            start = idx
        prev = idx

    runs.append((start, prev))
    return runs

def _line_runs_row(binary, y, x_start, x_end):
    h, w = binary.shape[:2]
    y = int(round(y))
    if y < 0 or y >= h:
        return []

    xa = max(0, min(w - 1, int(round(min(x_start, x_end)))))
    xb = max(0, min(w - 1, int(round(max(x_start, x_end)))))
    if xb < xa:
        return []

    row = (binary[y, xa:xb + 1] > 0).astype(np.uint8)
    runs = []
    for s, e in _foreground_runs_1d(row):
        runs.append({
            "start": xa + s,
            "end": xa + e,
            "length": e - s + 1,
        })
    return runs

def _line_runs_col(binary, x, y_start, y_end):
    h, w = binary.shape[:2]
    x = int(round(x))
    if x < 0 or x >= w:
        return []

    ya = max(0, min(h - 1, int(round(min(y_start, y_end)))))
    yb = max(0, min(h - 1, int(round(max(y_start, y_end)))))
    if yb < ya:
        return []

    col = (binary[ya:yb + 1, x] > 0).astype(np.uint8)
    runs = []
    for s, e in _foreground_runs_1d(col):
        runs.append({
            "start": ya + s,
            "end": ya + e,
            "length": e - s + 1,
        })
    return runs

# =========================================================
# BODY BBOX REFINEMENT
# =========================================================
def _smooth_projection(values, radius=2):
    if not values:
        return []

    arr = np.asarray(values, dtype=np.float32)
    if arr.size <= 2 * radius + 1:
        return arr.tolist()

    kernel = np.ones(2 * radius + 1, dtype=np.float32) / float(2 * radius + 1)
    return np.convolve(arr, kernel, mode="same").tolist()

def _select_body_edge_centers(centers, min_span, max_outer_gap_px=None):
    """
    Sceglie i due lati del corpo quando la proiezione contiene anche fili
    esterni paralleli al chip.

    Nei circuiti integrati i fili subito fuori dal package possono essere
    lunghi quanto i lati del rettangolo. Se prendiamo sempre il primo e
    l'ultimo picco, il body si allarga fino a includere quei fili e i pin
    laterali non attraversano piu' il bordo stimato.
    """
    if len(centers) < 2:
        return None, None, {"reason": "less_than_two_centers"}

    if max_outer_gap_px is None:
        max_outer_gap_px = max(18, int(round(float(min_span) * 0.12)))

    left_idx = 0
    right_idx = len(centers) - 1
    trimmed = []

    if len(centers) >= 3 and centers[1] - centers[0] <= max_outer_gap_px:
        left_idx = 1
        trimmed.append({
            "side": "left",
            "discarded_center": int(centers[0]),
            "kept_center": int(centers[1]),
            "gap": int(centers[1] - centers[0]),
        })

    if right_idx - left_idx >= 2 and centers[right_idx] - centers[right_idx - 1] <= max_outer_gap_px:
        trimmed.append({
            "side": "right",
            "discarded_center": int(centers[right_idx]),
            "kept_center": int(centers[right_idx - 1]),
            "gap": int(centers[right_idx] - centers[right_idx - 1]),
        })
        right_idx -= 1

    return centers[left_idx], centers[right_idx], {
        "reason": "ok",
        "max_outer_gap_px": int(max_outer_gap_px),
        "trimmed_outer_parallel_edges": trimmed,
    }


def _find_edge_pair_from_projection(values, min_span, min_density_ratio=0.35, keep_ratio=0.55, max_outer_gap_px=None):
    if not values:
        return None, None, {
            "reason": "empty_projection",
            "max_score": 0,
            "threshold": 0,
            "candidate_count": 0,
        }

    smoothed = _smooth_projection(values, radius=2)
    max_score = max(smoothed)

    if max_score <= 0:
        return None, None, {
            "reason": "zero_projection",
            "max_score": 0,
            "threshold": 0,
            "candidate_count": 0,
        }

    threshold = max(max_score * keep_ratio, min_span * min_density_ratio)
    candidates = [i for i, score in enumerate(smoothed) if score >= threshold]
    groups = _group_close_indices(candidates, max_gap=2)

    if len(groups) < 2:
        return None, None, {
            "reason": "less_than_two_edge_groups",
            "max_score": round(float(max_score), 3),
            "threshold": round(float(threshold), 3),
            "candidate_count": len(candidates),
            "group_count": len(groups),
        }

    centers = [int(round((g[0] + g[-1]) / 2.0)) for g in groups]
    left, right, selection_debug = _select_body_edge_centers(
        centers,
        min_span=min_span,
        max_outer_gap_px=max_outer_gap_px,
    )

    if right - left < max(20, int(round(min_span * 0.25))):
        return None, None, {
            "reason": "edge_pair_too_close",
            "max_score": round(float(max_score), 3),
            "threshold": round(float(threshold), 3),
            "candidate_count": len(candidates),
            "group_count": len(groups),
            "centers": centers,
            "selection_debug": selection_debug,
        }

    return left, right, {
        "reason": "ok",
        "max_score": round(float(max_score), 3),
        "threshold": round(float(threshold), 3),
        "candidate_count": len(candidates),
        "group_count": len(groups),
        "centers": centers,
        "selected_centers": [int(left), int(right)],
        "selection_debug": selection_debug,
    }

def refine_ic_body_bbox(binary, bbox, meta):
    """
    Cerca i lati rettangolari del corpo IC dentro il bbox YOLO.

    Se non trova abbastanza evidenza, torna al bbox YOLO.
    """
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)
    w = max(x2 - x1 + 1, 1)
    h = max(y2 - y1 + 1, 1)

    body_cfg = meta.get("body_refinement", {}) or {}
    enabled = bool(body_cfg.get("enabled", True))

    if not enabled:
        return (x1, y1, x2, y2), {
            "enabled": False,
            "used_fallback_bbox": True,
        }

    min_body_w = int(body_cfg.get("min_body_width_px", 35))
    min_body_h = int(body_cfg.get("min_body_height_px", 35))
    max_outer_gap_px = body_cfg.get("outer_parallel_edge_gap_px")
    if max_outer_gap_px is not None:
        max_outer_gap_px = int(max_outer_gap_px)

    roi = binary[y1:y2 + 1, x1:x2 + 1]
    if roi.size == 0:
        return (x1, y1, x2, y2), {
            "enabled": True,
            "used_fallback_bbox": True,
            "reason": "empty_roi",
        }

    # Proiezioni: un lato del corpo IC è una linea lunga e quasi continua.
    col_proj = np.count_nonzero(roi > 0, axis=0).tolist()
    row_proj = np.count_nonzero(roi > 0, axis=1).tolist()

    left_rel, right_rel, x_debug = _find_edge_pair_from_projection(
        col_proj,
        min_span=h,
        min_density_ratio=0.30,
        keep_ratio=0.55,
        max_outer_gap_px=max_outer_gap_px,
    )

    top_rel, bottom_rel, y_debug = _find_edge_pair_from_projection(
        row_proj,
        min_span=w,
        min_density_ratio=0.30,
        keep_ratio=0.55,
        max_outer_gap_px=max_outer_gap_px,
    )

    if left_rel is None or right_rel is None or top_rel is None or bottom_rel is None:
        return (x1, y1, x2, y2), {
            "enabled": True,
            "used_fallback_bbox": True,
            "reason": "edge_pair_not_found",
            "x_debug": x_debug,
            "y_debug": y_debug,
        }

    bx1 = x1 + left_rel
    bx2 = x1 + right_rel
    by1 = y1 + top_rel
    by2 = y1 + bottom_rel

    if bx2 - bx1 < min_body_w or by2 - by1 < min_body_h:
        return (x1, y1, x2, y2), {
            "enabled": True,
            "used_fallback_bbox": True,
            "reason": "refined_body_too_small",
            "candidate_body_bbox": [int(bx1), int(by1), int(bx2), int(by2)],
            "x_debug": x_debug,
            "y_debug": y_debug,
        }

    return (int(bx1), int(by1), int(bx2), int(by2)), {
        "enabled": True,
        "used_fallback_bbox": False,
        "body_bbox": [int(bx1), int(by1), int(bx2), int(by2)],
        "x_debug": x_debug,
        "y_debug": y_debug,
    }

# =========================================================
# PIN CONTACT SCORING
# =========================================================
def _score_horizontal_contact(binary, body_bbox, y, side, cfg, halfspan):
    x1, y1, x2, y2 = body_bbox
    edge_x = x1 if side == "left" else x2
    outward = cfg["outward_probe_px"]
    inward = cfg["inward_probe_px"]
    min_run = cfg["min_contact_run_px"]
    min_wire = cfg["min_wire_length_px"]

    if side == "left":
        xs = edge_x - outward
        xe = edge_x + inward
    else:
        xs = edge_x - inward
        xe = edge_x + outward

    best_score = 0
    best_run = None

    for yy in range(int(y) - halfspan, int(y) + halfspan + 1):
        for run in _line_runs_row(binary, yy, xs, xe):
            if side == "left":
                touches_edge = run["start"] <= edge_x + inward and run["end"] >= edge_x - 1
                outward_len = max(0, edge_x - run["start"] + 1)
            else:
                touches_edge = run["start"] <= edge_x + 1 and run["end"] >= edge_x - inward
                outward_len = max(0, run["end"] - edge_x + 1)

            if not touches_edge:
                continue
            if run["length"] < min_run:
                continue
            if outward_len < min_wire:
                continue

            score = run["length"] + 2 * outward_len
            if score > best_score:
                best_score = score
                best_run = {
                    **run,
                    "row": int(yy),
                    "outward_len": int(outward_len),
                }

    return best_score, best_run

def _score_vertical_contact(binary, body_bbox, x, side, cfg, halfspan):
    x1, y1, x2, y2 = body_bbox
    edge_y = y1 if side == "top" else y2
    outward = cfg["outward_probe_px"]
    inward = cfg["inward_probe_px"]
    min_run = cfg["min_contact_run_px"]
    min_wire = cfg["min_wire_length_px"]

    if side == "top":
        ys = edge_y - outward
        ye = edge_y + inward
    else:
        ys = edge_y - inward
        ye = edge_y + outward

    best_score = 0
    best_run = None

    for xx in range(int(x) - halfspan, int(x) + halfspan + 1):
        for run in _line_runs_col(binary, xx, ys, ye):
            if side == "top":
                touches_edge = run["start"] <= edge_y + inward and run["end"] >= edge_y - 1
                outward_len = max(0, edge_y - run["start"] + 1)
            else:
                touches_edge = run["start"] <= edge_y + 1 and run["end"] >= edge_y - inward
                outward_len = max(0, run["end"] - edge_y + 1)

            if not touches_edge:
                continue
            if run["length"] < min_run:
                continue
            if outward_len < min_wire:
                continue

            score = run["length"] + 2 * outward_len
            if score > best_score:
                best_score = score
                best_run = {
                    **run,
                    "col": int(xx),
                    "outward_len": int(outward_len),
                }

    return best_score, best_run

def _candidate_coords_for_side(binary, body_bbox, side, cfg):
    x1, y1, x2, y2 = body_bbox
    w = max(x2 - x1, 1)
    h = max(y2 - y1, 1)

    corner_skip_y = max(2, int(round(h * cfg["corner_exclusion_ratio"])))
    corner_skip_x = max(2, int(round(w * cfg["corner_exclusion_ratio"])))

    # halfspan piccolo: serve solo a tollerare antialiasing/spessore filo.
    halfspan = max(1, min(4, int(round(cfg["scan_band_px"] / 6.0))))

    candidates = []

    if side in {"left", "right"}:
        start = y1 + corner_skip_y
        end = y2 - corner_skip_y
        for y in range(start, end + 1):
            score, run = _score_horizontal_contact(
                binary,
                body_bbox,
                y,
                side,
                cfg,
                halfspan,
            )
            if score > 0:
                candidates.append({
                    "coord": int(y),
                    "score": int(score),
                    "run": run,
                })

    elif side in {"top", "bottom"}:
        start = x1 + corner_skip_x
        end = x2 - corner_skip_x
        for x in range(start, end + 1):
            score, run = _score_vertical_contact(
                binary,
                body_bbox,
                x,
                side,
                cfg,
                halfspan,
            )
            if score > 0:
                candidates.append({
                    "coord": int(x),
                    "score": int(score),
                    "run": run,
                })

    return candidates

def _merge_candidate_coords(candidates, max_gap):
    if not candidates:
        return []

    coords = sorted(set(c["coord"] for c in candidates))
    groups = _group_close_indices(coords, max_gap=max_gap)

    merged = []
    score_by_coord = {}
    run_by_coord = {}

    for c in candidates:
        score_by_coord[c["coord"]] = max(score_by_coord.get(c["coord"], 0), c["score"])
        run_by_coord[c["coord"]] = c.get("run")

    for group in groups:
        weighted_num = 0.0
        weighted_den = 0.0
        best_coord = group[0]
        best_score = -1

        for coord in group:
            score = float(score_by_coord.get(coord, 1.0))
            weighted_num += coord * score
            weighted_den += score

            if score > best_score:
                best_score = score
                best_coord = coord

        center = int(round(weighted_num / max(weighted_den, 1.0)))
        merged.append({
            "coord": center,
            "group_start": int(group[0]),
            "group_end": int(group[-1]),
            "group_len": int(group[-1] - group[0] + 1),
            "best_coord": int(best_coord),
            "best_score": int(best_score),
            "run": run_by_coord.get(best_coord),
        })

    return merged

def _make_terminal_point(body_bbox, side, coord):
    x1, y1, x2, y2 = body_bbox

    if side == "left":
        return [round(float(x1 - TERMINAL_OUTWARD_OFFSET), 2), round(float(coord), 2)]
    if side == "right":
        return [round(float(x2 + TERMINAL_OUTWARD_OFFSET), 2), round(float(coord), 2)]
    if side == "top":
        return [round(float(coord), 2), round(float(y1 - TERMINAL_OUTWARD_OFFSET), 2)]
    if side == "bottom":
        return [round(float(coord), 2), round(float(y2 + TERMINAL_OUTWARD_OFFSET), 2)]

    raise ValueError(f"side non supportato: {side}")


def _anchor_offset_ratio(body_bbox, side, coord):
    x1, y1, x2, y2 = body_bbox
    if side in {"left", "right"}:
        return round((float(coord) - y1) / float(max(y2 - y1, 1)), 4)
    return round((float(coord) - x1) / float(max(x2 - x1, 1)), 4)


def _scale_pin_cfg(cfg, scale):
    if abs(float(scale) - 1.0) < 1e-6:
        return dict(cfg)

    scaled = dict(cfg)
    for key in (
        "scan_band_px",
        "outward_probe_px",
        "inward_probe_px",
        "min_contact_run_px",
        "min_wire_length_px",
        "merge_gap_px",
    ):
        scaled[key] = max(1, int(round(float(cfg[key]) * float(scale))))
    return scaled


def _effective_local_upscale(body_bbox, cfg):
    if not cfg.get("adaptive_upscale_enabled", True):
        return 1.0

    x1, y1, x2, y2 = [float(v) for v in body_bbox]
    body_w = max(1.0, x2 - x1 + 1.0)
    body_h = max(1.0, y2 - y1 + 1.0)
    min_dim = min(body_w, body_h)
    if min_dim >= float(cfg["adaptive_upscale_min_body_dim_px"]):
        return 1.0

    target_dim = max(float(cfg["adaptive_upscale_target_body_dim_px"]), min_dim)
    scale = target_dim / max(min_dim, 1.0)
    return max(1.0, min(float(cfg["adaptive_upscale_max_scale"]), scale))


def _build_local_upscaled_binary(binary, body_bbox, cfg):
    scale = _effective_local_upscale(body_bbox, cfg)
    if scale <= 1.01:
        return binary, tuple(int(v) for v in body_bbox), dict(cfg), {
            "enabled": False,
            "scale": 1.0,
        }

    margin = max(
        int(cfg["scan_band_px"]),
        int(cfg["outward_probe_px"]),
        int(cfg["inward_probe_px"]),
    ) + 6
    h, w = binary.shape[:2]
    bx1, by1, bx2, by2 = [int(round(v)) for v in body_bbox]
    rx1 = max(0, bx1 - margin)
    ry1 = max(0, by1 - margin)
    rx2 = min(w - 1, bx2 + margin)
    ry2 = min(h - 1, by2 + margin)

    roi = binary[ry1:ry2 + 1, rx1:rx2 + 1]
    if roi.size == 0:
        return binary, tuple(int(v) for v in body_bbox), dict(cfg), {
            "enabled": False,
            "scale": 1.0,
            "reason": "empty_local_roi",
        }

    local_binary = cv2.resize(
        roi,
        None,
        fx=scale,
        fy=scale,
        interpolation=cv2.INTER_NEAREST,
    )
    local_body_bbox = (
        int(round((bx1 - rx1) * scale)),
        int(round((by1 - ry1) * scale)),
        int(round((bx2 - rx1) * scale)),
        int(round((by2 - ry1) * scale)),
    )
    return local_binary, local_body_bbox, _scale_pin_cfg(cfg, scale), {
        "enabled": True,
        "scale": round(float(scale), 3),
        "roi_bbox": [int(rx1), int(ry1), int(rx2), int(ry2)],
        "local_body_bbox": [int(v) for v in local_body_bbox],
    }


def _descale_value(value, scale, offset=0):
    return int(round(float(offset) + (float(value) / max(float(scale), 1e-6))))


def _descale_run(run, scale, side, roi_bbox):
    if not isinstance(run, dict):
        return run

    rx1, ry1, _, _ = [int(v) for v in roi_bbox]
    mapped = dict(run)
    if side in {"left", "right"}:
        if mapped.get("start") is not None:
            mapped["start"] = _descale_value(mapped["start"], scale, rx1)
        if mapped.get("end") is not None:
            mapped["end"] = _descale_value(mapped["end"], scale, rx1)
        if mapped.get("row") is not None:
            mapped["row"] = _descale_value(mapped["row"], scale, ry1)
    else:
        if mapped.get("start") is not None:
            mapped["start"] = _descale_value(mapped["start"], scale, ry1)
        if mapped.get("end") is not None:
            mapped["end"] = _descale_value(mapped["end"], scale, ry1)
        if mapped.get("col") is not None:
            mapped["col"] = _descale_value(mapped["col"], scale, rx1)
    if mapped.get("outward_len") is not None:
        mapped["outward_len"] = _descale_value(mapped["outward_len"], scale, 0)
    if mapped.get("start") is not None and mapped.get("end") is not None:
        mapped["length"] = max(1, int(mapped["end"] - mapped["start"] + 1))
    return mapped


def _descale_merged_rows(rows, scale, side, roi_bbox):
    if scale <= 1.01:
        return rows

    rx1, ry1, _, _ = [int(v) for v in roi_bbox]
    axis_offset = ry1 if side in {"left", "right"} else rx1
    mapped_rows = []
    for row in rows:
        mapped_rows.append({
            **row,
            "coord": _descale_value(row["coord"], scale, axis_offset),
            "group_start": _descale_value(row["group_start"], scale, axis_offset),
            "group_end": _descale_value(row["group_end"], scale, axis_offset),
            "group_len": max(1, _descale_value(row["group_len"], scale, 0)),
            "best_coord": _descale_value(row["best_coord"], scale, axis_offset),
            "best_score": int(row["best_score"]),
            "run": _descale_run(row.get("run"), scale, side, roi_bbox),
        })
    return mapped_rows

# =========================================================
# PUBLIC API
# =========================================================
def detect_integrated_circuit_terminals(meta: dict, binary, bbox):
    """
    Ritorna:
        terminals_def, estimated_orientation, debug

    terminals_def contiene già "point", quindi il processor userà
    coordinate assolute.
    """
    body_bbox, body_debug = refine_ic_body_bbox(binary, bbox, meta)
    cfg = _get_pin_cfg(meta)
    naming_cfg = _get_naming_cfg(meta)

    local_binary, local_body_bbox, local_cfg, upscale_debug = _build_local_upscaled_binary(
        binary,
        body_bbox,
        cfg,
    )
    local_scale = float(upscale_debug.get("scale") or 1.0)

    side_rows = {}
    raw_counts = {}
    terminals_by_side = {}

    for side in cfg["sides"]:
        raw_candidates = _candidate_coords_for_side(
            local_binary,
            local_body_bbox,
            side,
            local_cfg,
        )
        merged = _merge_candidate_coords(
            raw_candidates,
            max_gap=local_cfg["merge_gap_px"],
        )
        merged = _descale_merged_rows(
            merged,
            local_scale,
            side,
            upscale_debug.get("roi_bbox") or [0, 0, 0, 0],
        )

        raw_counts[side] = len(raw_candidates)
        side_rows[side] = merged
        terminals_by_side[side] = merged

    terminals_def = []
    debug_rows = []

    for side in ("left", "right", "top", "bottom"):
        if side not in terminals_by_side:
            continue

        rows = terminals_by_side[side]
        order = naming_cfg["side_order"].get(side)

        reverse = order in {"bottom_to_top", "right_to_left"}
        rows = sorted(rows, key=lambda r: r["coord"], reverse=reverse)

        for idx, row in enumerate(rows, start=1):
            term_name = naming_cfg["fallback_name_pattern"].format(
                side=side,
                index=idx,
            )
            point = _make_terminal_point(body_bbox, side, row["coord"])
            anchor_ratio = _anchor_offset_ratio(body_bbox, side, row["coord"])

            terminals_def.append({
                "name": term_name,
                "relative_position": side,
                "point": point,
                "anchor_offset_ratio": anchor_ratio,
                "point_debug": {
                    "point_mode": "ic_wire_contact",
                    "body_bbox": [int(v) for v in body_bbox],
                    "side": side,
                    "coord": int(row["coord"]),
                    "anchor_offset_ratio": anchor_ratio,
                    "group_start": int(row["group_start"]),
                    "group_end": int(row["group_end"]),
                    "group_len": int(row["group_len"]),
                    "best_score": int(row["best_score"]),
                    "run": row.get("run"),
                },
            })

            debug_rows.append({
                "name": term_name,
                "side": side,
                "coord": int(row["coord"]),
                "point": point,
                "anchor_offset_ratio": anchor_ratio,
                "group_start": int(row["group_start"]),
                "group_end": int(row["group_end"]),
                "group_len": int(row["group_len"]),
                "best_score": int(row["best_score"]),
            })

    debug = {
        "strategy": meta.get("terminal_strategy", "integrated_circuit_wire_contacts"),
        "decision_mode": "ic_body_side_wire_contacts",
        "estimated_orientation": "multi_side",
        "bbox": [int(round(v)) for v in bbox],
        "body_bbox": [int(v) for v in body_bbox],
        "body_refinement": body_debug,
        "adaptive_local_upscale": upscale_debug,
        "pin_detection_cfg": cfg,
        "raw_candidate_counts": raw_counts,
        "pin_count": len(terminals_def),
        "rows": debug_rows,
    }

    return terminals_def, "multi_side", debug
