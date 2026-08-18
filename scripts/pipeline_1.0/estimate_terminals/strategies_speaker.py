from .config import TERMINAL_OUTWARD_OFFSET
from .strategies_basic import strategy_detect_connected_side
from .strategies_integrated_circuit import (
    _candidate_coords_for_side,
    _merge_candidate_coords,
)


def _speaker_orientation_from_connected_side(connected_side: str) -> str:
    orientation_by_side = {
        "left": "right",
        "right": "left",
        "top": "down",
        "bottom": "up",
    }
    return orientation_by_side.get(connected_side, "right")


def _speaker_pin_cfg(meta: dict) -> dict:
    cfg = meta.get("pin_detection", {}) or {}
    return {
        "sides": cfg.get("sides", ["left", "right", "top", "bottom"]),
        "scan_band_px": int(cfg.get("scan_band_px", 18)),
        "outward_probe_px": int(cfg.get("outward_probe_px", 24)),
        "inward_probe_px": int(cfg.get("inward_probe_px", 4)),
        "min_contact_run_px": int(cfg.get("min_contact_run_px", 4)),
        "min_wire_length_px": int(cfg.get("min_wire_length_px", 8)),
        "merge_gap_px": int(cfg.get("merge_gap_px", 10)),
        "corner_exclusion_ratio": float(cfg.get("corner_exclusion_ratio", 0.08)),
    }


def _make_terminal_point(bbox, side, coord):
    x1, y1, x2, y2 = bbox

    if side == "left":
        return [round(float(x1 - TERMINAL_OUTWARD_OFFSET), 2), round(float(coord), 2)]
    if side == "right":
        return [round(float(x2 + TERMINAL_OUTWARD_OFFSET), 2), round(float(coord), 2)]
    if side == "top":
        return [round(float(coord), 2), round(float(y1 - TERMINAL_OUTWARD_OFFSET), 2)]
    if side == "bottom":
        return [round(float(coord), 2), round(float(y2 + TERMINAL_OUTWARD_OFFSET), 2)]

    raise ValueError(f"Speaker side non supportato: {side}")


def _anchor_offset_ratio(bbox, side, coord):
    x1, y1, x2, y2 = bbox
    if side in {"left", "right"}:
        return round((float(coord) - y1) / float(max(y2 - y1, 1)), 4)
    return round((float(coord) - x1) / float(max(x2 - x1, 1)), 4)


def _select_speaker_rows(rows):
    if len(rows) <= 2:
        return rows

    best_pair = None
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            spread = abs(int(rows[j]["coord"]) - int(rows[i]["coord"]))
            pair_score = int(rows[i]["best_score"]) + int(rows[j]["best_score"])
            candidate = (spread, pair_score, i, j)
            if best_pair is None or candidate > best_pair:
                best_pair = candidate

    _, _, i, j = best_pair
    return [rows[i], rows[j]]


def detect_speaker_terminals(meta: dict, binary, bbox):
    bbox = tuple(int(round(v)) for v in bbox)
    connected_side, side_scores = strategy_detect_connected_side(binary, bbox)
    if connected_side is None:
        connected_side = "left"
    estimated_orientation = _speaker_orientation_from_connected_side(connected_side)

    cfg = _speaker_pin_cfg(meta)
    raw_candidates = _candidate_coords_for_side(binary, bbox, connected_side, cfg)
    merged_rows = _merge_candidate_coords(raw_candidates, max_gap=cfg["merge_gap_px"])
    selected_rows = sorted(_select_speaker_rows(merged_rows), key=lambda row: row["coord"])

    terminals_def = []
    debug_rows = []

    for idx, row in enumerate(selected_rows, start=1):
        point = _make_terminal_point(bbox, connected_side, row["coord"])
        anchor_ratio = _anchor_offset_ratio(bbox, connected_side, row["coord"])
        terminals_def.append({
            "name": f"t{idx}",
            "relative_position": connected_side,
            "point": point,
            "anchor_offset_ratio": anchor_ratio,
            "point_debug": {
                "point_mode": "speaker_side_contact_pair",
                "bbox": [int(round(v)) for v in bbox],
                "connected_side": connected_side,
                "coord": int(row["coord"]),
                "group_start": int(row["group_start"]),
                "group_end": int(row["group_end"]),
                "group_len": int(row["group_len"]),
                "best_score": int(row["best_score"]),
                "run": row.get("run"),
            },
        })
        debug_rows.append({
            "name": f"t{idx}",
            "side": connected_side,
            "coord": int(row["coord"]),
            "group_start": int(row["group_start"]),
            "group_end": int(row["group_end"]),
            "group_len": int(row["group_len"]),
            "best_score": int(row["best_score"]),
        })

    debug = {
        "strategy": meta.get("terminal_strategy", "speaker_by_connected_side"),
        "decision_mode": "speaker_connected_side_contact_pair",
        "estimated_orientation": estimated_orientation,
        "connected_side": connected_side,
        "bbox": [int(round(v)) for v in bbox],
        "connected_side_scores": side_scores,
        "pin_detection_cfg": cfg,
        "raw_candidate_count": len(raw_candidates),
        "merged_candidate_count": len(merged_rows),
        "pin_count": len(terminals_def),
        "rows": debug_rows,
    }

    return terminals_def, estimated_orientation, connected_side, debug
