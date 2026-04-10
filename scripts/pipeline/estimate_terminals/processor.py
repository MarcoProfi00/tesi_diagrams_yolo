from .config import *
from .dispatcher import get_terminals_definition, resolve_terminal_point_mode
from .geometry import (
    geom_terminal_point_from_bbox,
    geom_terminal_point_three_terminal,
    geom_terminal_point_by_side_peak,
    geom_terminal_point_opamp,
)
# =========================================================
# COMPONENT PROCESSING
# =========================================================
def estimate_terminals_for_component(component: dict, class_meta: dict, image_binary):
    class_id = component["class_id"]
    meta = class_meta.get(class_id, {})
    if not component.get("use_for_terminals", False):
        return [], None, None, None

    bbox = component["bbox"]
    instance_id = component["instance_id"]

    terminals_def, estimated_orientation, connected_side, side_scores = get_terminals_definition(
        meta,
        bbox,
        image_binary=image_binary
    )

    # Per quasi tutti i componenti useremo il centro del lato.
    # Per i 3-terminal invece usiamo una localizzazione più strutturata:
    # prima il lato singolo, poi la coppia ortogonale coerente con quel lato.
    point_mode = resolve_terminal_point_mode(meta)

    terminals = []
    for term_def in terminals_def:
        term_name = term_def["name"]
        rel_pos = term_def["relative_position"]

        point_debug = {
            "point_mode": point_mode
        }

        if point_mode == "three_terminal_structured":
            point, structured_debug = geom_terminal_point_three_terminal(
                image_binary,
                bbox,
                estimated_orientation,
                rel_pos
            )
            x, y = point
            point_debug.update(structured_debug)

        elif point_mode == OPAMP_POINT_MODE:
            point, opamp_debug = geom_terminal_point_opamp(
                image_binary,
                bbox,
                estimated_orientation,
                term_def,
            )
            x, y = point
            point_debug.update(opamp_debug)

        elif point_mode == "two_terminal_side_peak":
            point, peak_debug = geom_terminal_point_by_side_peak(
                image_binary,
                bbox,
                rel_pos
            )
            x, y = point
            point_debug.update(peak_debug)

        else:
            x, y = geom_terminal_point_from_bbox(bbox, rel_pos)

            x1, y1, x2, y2 = bbox
            width = max(x2 - x1, 1e-6)
            height = max(y2 - y1, 1e-6)

            if rel_pos in {"top", "bottom"}:
                point_debug["anchor_offset_ratio"] = round((x - x1) / width, 4)
            else:
                point_debug["anchor_offset_ratio"] = round((y - y1) / height, 4)

        terminals.append({
            "terminal_id": f"{instance_id}:{term_name}",
            "instance_id": instance_id,
            "component_class_id": class_id,
            "component_class_name": component.get("class_name"),
            "name": term_name,
            "relative_position": rel_pos,
            "estimated_orientation": estimated_orientation,
            "estimated_connection_side": connected_side,
            "terminal_point_mode": point_mode,
            "terminal_point_debug": point_debug,
            "x": x,
            "y": y,
        })
    return terminals, estimated_orientation, connected_side, side_scores