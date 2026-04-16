from .config import *
from .geometry import (
    geom_terminal_point_opamp,
    _opamp_aux_make_refine_binary,
    _opamp_refine_aux_y_to_diagonal,
)
from .probes import score_point_directional_support


# Get op-amp orientation defs.
def _get_opamp_orientation_defs(meta: dict, orientation: str):
    terminals_def = meta.get("orientations", {}).get(orientation)
    if terminals_def is None:
        raise ValueError(f"Nessuna definizione opamp per orientazione '{orientation}'")
    return terminals_def


# Score op-amp terminal.
def _score_opamp_terminal(binary, bbox, orientation: str, term_def: dict):
    point, point_debug = geom_terminal_point_opamp(
        binary,
        bbox,
        orientation,
        term_def,
    )
    x, y = point
    relative_position = term_def["relative_position"]

    directional_score = score_point_directional_support(
        binary,
        x,
        y,
        relative_position,
        outward=OPAMP_DIRECTIONAL_OUTWARD,
        inward=OPAMP_DIRECTIONAL_INWARD,
        halfspan=OPAMP_DIRECTIONAL_HALFSPAN,
    )

    weight = OPAMP_OUTPUT_WEIGHT if term_def.get("terminal_role") == "output" else 1.0
    weighted_score = weight * directional_score

    return weighted_score, {
        "name": term_def.get("name"),
        "relative_position": relative_position,
        "terminal_role": term_def.get("terminal_role"),
        "slot": term_def.get("slot"),
        "point": point,
        "directional_score": directional_score,
        "weight": weight,
        "weighted_score": weighted_score,
        "point_debug": point_debug,
    }


# Detect op-amp terminals.
def detect_opamp_terminals(meta: dict, binary, bbox, default_orientation="right"):
    candidate_orientations = ("right", "left", "top", "bottom")

    orientation_scores = {}
    orientation_debug = {}

    for orientation in candidate_orientations:
        terminals_def = _get_opamp_orientation_defs(meta, orientation)
        mandatory_defs = [t for t in terminals_def if not t.get("optional", False)]

        total_score = 0.0
        score_details = []

        for term_def in mandatory_defs:
            weighted_score, debug = _score_opamp_terminal(
                binary,
                bbox,
                orientation,
                term_def,
            )
            total_score += weighted_score
            score_details.append(debug)

        orientation_scores[orientation] = total_score
        orientation_debug[orientation] = {
            "mandatory_terminals": [t["name"] for t in mandatory_defs],
            "score_details": score_details,
        }

    ordered = sorted(
        candidate_orientations,
        key=lambda o: orientation_scores[o],
        reverse=True,
    )

    best_orientation = ordered[0]
    second_orientation = ordered[1]
    best_score = orientation_scores[best_orientation]
    second_score = orientation_scores[second_orientation]

    chosen_orientation = best_orientation
    decision_mode = "opamp_mandatory_only_orientation"

    if best_score <= second_score * OPAMP_ORIENTATION_MARGIN:
        chosen_orientation = (
            default_orientation
            if default_orientation in candidate_orientations
            else best_orientation
        )
        decision_mode = "opamp_default_fallback_after_close_scores"

    chosen_defs = _get_opamp_orientation_defs(meta, chosen_orientation)

    active_terminals = []
    optional_debug = {}

    for term_def in chosen_defs:
        if not term_def.get("optional", False):
            active_terminals.append(dict(term_def))
            continue

        point, point_debug = geom_terminal_point_opamp(
            binary,
            bbox,
            chosen_orientation,
            term_def,
        )

        is_active = bool(point_debug.get("aux_detected", False))
        optional_debug[term_def["name"]] = {
            "name": term_def.get("name"),
            "point": point,
            "point_debug": point_debug,
            "is_active": is_active,
        }

        if is_active:
            active_terminals.append(dict(term_def))

    debug_scores = {
        "decision_mode": decision_mode,
        "chosen_orientation": chosen_orientation,
        "best_orientation": best_orientation,
        "best_score": round(float(best_score), 4),
        "second_orientation": second_orientation,
        "second_score": round(float(second_score), 4),
        "orientation_scores": {
            k: round(float(v), 4) for k, v in orientation_scores.items()
        },
        "orientation_debug": orientation_debug,
        "optional_debug": optional_debug,
        "optional_terminals_disabled": False,
        "active_terminal_names": [t["name"] for t in active_terminals],
    }

    return active_terminals, chosen_orientation, debug_scores


# Snap op-amp top aux to nearby terminal.
def snap_opamp_top_aux_to_nearby_terminal(components: list[dict], binary):
    if not OPAMP_AUX_SNAP_TO_NEARBY_TERMINAL:
        return []

    terminal_candidates = []
    for component in components:
        if component.get("symbol_type") != "variable_terminal":
            continue

        terminals = component.get("terminals", [])
        if len(terminals) != 1:
            continue

        terminal = terminals[0]
        terminal_candidates.append({
            "instance_id": component.get("instance_id"),
            "terminal_id": terminal.get("terminal_id"),
            "x": float(terminal.get("x", 0.0)),
            "y": float(terminal.get("y", 0.0)),
        })

    snap_updates = []

    for component in components:
        if component.get("class_id") != 19:
            continue

        if component.get("estimated_orientation") not in {"right", "left"}:
            continue

        bbox = component.get("bbox")
        if not bbox or len(bbox) != 4:
            continue

        x1, y1, x2, y2 = map(float, bbox)
        width = max(x2 - x1, 1.0)
        height = max(y2 - y1, 1.0)
        center_x = (x1 + x2) / 2.0

        band_x1 = x1 + OPAMP_AUX_CENTER_START_RATIO * width
        band_x2 = x1 + OPAMP_AUX_CENTER_END_RATIO * width
        top_region_y2 = y1 + OPAMP_AUX_NEARBY_TERMINAL_TOP_REGION_RATIO * height

        nearby_terminals = [
            candidate
            for candidate in terminal_candidates
            if band_x1 <= candidate["x"] <= band_x2
            and y1 <= candidate["y"] <= top_region_y2
        ]

        if not nearby_terminals:
            continue

        best_terminal = min(
            nearby_terminals,
            key=lambda candidate: (
                abs(candidate["x"] - center_x),
                abs(candidate["y"] - y1),
            ),
        )

        for terminal in component.get("terminals", []):
            if terminal.get("name") != "aux1" or terminal.get("relative_position") != "top":
                continue

            old_x = float(terminal.get("x", 0.0))
            old_y = float(terminal.get("y", 0.0))
            point_debug = terminal.setdefault("terminal_point_debug", {})
            new_x = float(best_terminal["x"])

            out_terminal = next(
                (item for item in component.get("terminals", []) if item.get("name") == "out"),
                None,
            )

            refine_debug = {}
            snap_mode = "nearby_variable_terminal_axis_to_diagonal"

            if out_terminal is not None:
                out_x = float(out_terminal.get("x", 0.0))
                out_y = float(out_terminal.get("y", 0.0))
                dx = out_x - old_x

                if abs(dx) >= 1.0:
                    slope = (out_y - old_y) / dx
                    projected_y = old_y + (new_x - old_x) * slope
                    new_y = float(projected_y)
                    snap_mode = "nearby_variable_terminal_project_to_output_diagonal"
                    refine_debug = {
                        "projected_output_terminal_id": out_terminal.get("terminal_id"),
                        "projected_output_terminal_point": [
                            round(out_x, 4),
                            round(out_y, 4),
                        ],
                        "projected_diagonal_slope": round(float(slope), 4),
                    }
                else:
                    out_terminal = None

            if out_terminal is None:
                base_y = float(point_debug.get("base_y", old_y))
                refine_binary, _ = _opamp_aux_make_refine_binary(
                    binary,
                    (x1, y1, x2, y2),
                    component.get("estimated_orientation"),
                )
                refined_y, refine_debug = _opamp_refine_aux_y_to_diagonal(
                    refine_binary,
                    (x1, y1, x2, y2),
                    component.get("estimated_orientation"),
                    terminal.get("relative_position"),
                    new_x,
                    base_y,
                )
                new_y = float(refined_y)

            terminal["x"] = new_x
            terminal["y"] = new_y

            point_debug.update({
                "snapped_to_nearby_terminal": True,
                "snap_mode": snap_mode,
                "neighbor_terminal_id": best_terminal["terminal_id"],
                "neighbor_terminal_instance_id": best_terminal["instance_id"],
                "neighbor_terminal_point": [
                    round(float(best_terminal["x"]), 4),
                    round(float(best_terminal["y"]), 4),
                ],
                "pre_snap_point": [round(old_x, 4), round(old_y, 4)],
                "snapped_point": [round(new_x, 4), round(new_y, 4)],
                "snap_center_band": [
                    round(float(band_x1), 2),
                    round(float(band_x2), 2),
                ],
                "snap_top_region_y2": round(float(top_region_y2), 2),
                "snap_refined_diag_support": refine_debug.get("refined_diag_support"),
                "snap_refine_mode": refine_debug.get("refine_mode"),
                **refine_debug,
            })

            snap_updates.append({
                "opamp_instance_id": component.get("instance_id"),
                "opamp_terminal_id": terminal.get("terminal_id"),
                "neighbor_terminal_id": best_terminal["terminal_id"],
                "from_point": [round(old_x, 4), round(old_y, 4)],
                "to_point": [round(new_x, 4), round(new_y, 4)],
            })

    return snap_updates
