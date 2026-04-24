"""
Prende un singolo componente e lo trasforma in una lista di terminali con coordinate, metadati geometrici e metadati semantici
"""
from .config import *
from .dispatcher import get_terminals_definition, resolve_terminal_point_mode
from .geometry import (
    geom_terminal_point_from_bbox,
    geom_terminal_point_from_bbox_with_anchor,
    geom_terminal_point_three_terminal,
    geom_terminal_point_by_side_peak,
    geom_terminal_point_opamp,
)
from .strategies_three_terminal import (
    get_three_terminal_working_binary,
    resolve_three_terminal_semantics,
    snap_bjt_pair_terminal_to_lateral_wire,
)
from .semantic_two_terminal import resolve_two_terminal_semantics

# =========================================================
# COMPONENT PROCESSING
# =========================================================
# Stima i terminali di un singolo componente partendo da:
# dizionario del componente
# metadati della classe
# img binaria del diagramma
# Return: lista terminali, orientazione stimata, lato connesso
def estimate_terminals_for_component(component: dict, class_meta: dict, image_binary):
    class_id = component["class_id"]
    meta = class_meta.get(class_id, {})

    # Caso use_for_terminals = False
    if not component.get("use_for_terminals", False):
        return [], None, None, None

    bbox = component["bbox"]
    instance_id = component["instance_id"]
    
    # Definizione strutturale dei terminali
    terminals_def, estimated_orientation, connected_side, side_scores = get_terminals_definition(
        meta,
        bbox,
        image_binary=image_binary
    )

    # Per quasi tutti i componenti usa il centro del lato.
    # Per i 3-terminal invece usa una localizzazione più strutturata: prima il lato singolo, poi la coppia ortogonale coerente con quel lato.
    point_mode = resolve_terminal_point_mode(meta)
    point_binary = image_binary
    if point_mode == "three_terminal_structured":
        point_binary = get_three_terminal_working_binary(image_binary, bbox)

    terminals = []
    for term_def in terminals_def:
        term_name = term_def["name"]
        rel_pos = term_def["relative_position"]

        point_debug = {
            "point_mode": point_mode
        }

        #Se term_def["point"] esiste, il terminale usa direttamente quel punto.
        if term_def.get("point") is not None:
            x, y = [round(float(v), 2) for v in term_def["point"]]
            point_debug["point_mode"] = "strategy_absolute_point"
            point_debug["point_source"] = "term_def.point"

        elif point_mode == "three_terminal_structured":
            # localizza terminale "singolo" e coppia di terminali ortogonale
            point, structured_debug = geom_terminal_point_three_terminal(
                point_binary,
                bbox,
                estimated_orientation,
                rel_pos
            )
            if component.get("class_name") == "NPN_Transistor":
                point, snap_debug = snap_bjt_pair_terminal_to_lateral_wire(
                    point_binary,
                    bbox,
                    estimated_orientation,
                    rel_pos,
                    point,
                )
                if snap_debug is not None:
                    structured_debug.update(snap_debug)
            x, y = point
            point_debug.update(structured_debug)

        elif point_mode == OPAMP_POINT_MODE:
            # gestisce terminali obbligatori (in1 in2 e out) e terminali ausiliari (aux1 aux2)
            point, opamp_debug = geom_terminal_point_opamp(
                image_binary,
                bbox,
                estimated_orientation,
                term_def,
            )
            x, y = point
            point_debug.update(opamp_debug)

        elif point_mode == "two_terminal_side_peak":
            # Diode usa il centro del lato e non il side-peak
            if component.get("class_name") == "Diode":
                x, y = geom_terminal_point_from_bbox(bbox, rel_pos)
                point_debug["point_mode"] = "two_terminal_axis_center"
                if rel_pos in {"top", "bottom"}:
                    point_debug["anchor_offset_ratio"] = 0.5
                else:
                    point_debug["anchor_offset_ratio"] = 0.5
            elif component.get("class_name") == "GND":
                # GND usa il centro del lato superiore per non farsi influenzare dal testo vicino
                x, y = geom_terminal_point_from_bbox(bbox, rel_pos)
                point_debug["point_mode"] = "one_terminal_axis_center"
                point_debug["anchor_offset_ratio"] = 0.5
            else:
                # altrimenti usa la classica
                point, peak_debug = geom_terminal_point_by_side_peak(
                    image_binary,
                    bbox,
                    rel_pos
                )
                x, y = point
                point_debug.update(peak_debug)

        else:
            anchor_offset_ratio = term_def.get("anchor_offset_ratio")
            if anchor_offset_ratio is not None:
                x, y = geom_terminal_point_from_bbox_with_anchor(
                    bbox,
                    rel_pos,
                    anchor_offset_ratio,
                )
                point_debug["point_mode"] = "bbox_side_anchor_ratio"
                point_debug["anchor_offset_ratio"] = round(float(anchor_offset_ratio), 4)
            else:
                x, y = geom_terminal_point_from_bbox(bbox, rel_pos)

                x1, y1, x2, y2 = bbox
                width = max(x2 - x1, 1e-6)
                height = max(y2 - y1, 1e-6)

                if rel_pos in {"top", "bottom"}:
                    point_debug["anchor_offset_ratio"] = round((x - x1) / width, 4)
                else:
                    point_debug["anchor_offset_ratio"] = round((y - y1) / height, 4)

        #arricchimento semantico
        terminals.append({
            "terminal_id": f"{instance_id}:{term_name}",
            "instance_id": instance_id,
            "component_class_id": class_id,
            "component_class_name": component.get("class_name"),
            "name": term_name,
            "display_name": term_name,
            "display_terminal_id": f"{instance_id}:{term_name}",
            "relative_position": rel_pos,
            "estimated_orientation": estimated_orientation,
            "estimated_connection_side": connected_side,
            "terminal_point_mode": point_mode,
            "terminal_point_debug": point_debug,
            "x": x,
            "y": y,
        })

    if point_mode == "three_terminal_structured":
        terminals = resolve_three_terminal_semantics(
            point_binary,
            bbox,
            estimated_orientation,
            terminals,
            meta,
        )
    else:
        terminals = resolve_two_terminal_semantics(
            image_binary,
            bbox,
            estimated_orientation,
            terminals,
            meta,
        )
    return terminals, estimated_orientation, connected_side, side_scores
