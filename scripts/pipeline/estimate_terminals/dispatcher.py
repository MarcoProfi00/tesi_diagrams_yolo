from .config import *
from .geometry import geom_infer_orientation_from_bbox
from .strategies_basic import (
    detect_two_terminal_orientation_capacitor,
    detect_two_terminal_orientation_led,
    detect_two_terminal_orientation_round_source,
    resolve_one_terminal_orientation,
    strategy_detect_connected_side,
    strategy_detect_two_terminal_orientation_generic,
    strategy_detect_two_terminal_orientation_switch,
)
from .strategies_terminal_class import detect_terminal_auto_one_or_two
from .strategies_three_terminal import strategy_detect_three_terminal_orientation
def resolve_terminal_point_mode(meta: dict):
    explicit_mode = meta.get("terminal_point_mode")
    if explicit_mode is not None:
        return explicit_mode

    strategy = meta.get("terminal_strategy", "")
    class_name = meta.get("name", "")

    if strategy == "three_terminal_by_side_pattern":
        return THREE_TERMINAL_POINT_MODE

    if strategy == "two_terminal_led" or class_name in {"LED", "Diode"}:
        return "two_terminal_side_peak"

    return "bbox_side_center"


# =========================================================
# STRATEGY DISPATCHER
# =========================================================
def get_terminals_definition(meta: dict, bbox, image_binary=None):
    strategy = meta.get("terminal_strategy", "fixed")

    if strategy == "fixed":
        return meta.get("terminals", []), None, None, None

    if strategy == "auto_by_aspect_ratio":
        default_orientation = meta.get("default_orientation", "horizontal")
        orientation = geom_infer_orientation_from_bbox(bbox, default_orientation=default_orientation)
        terminals_def = meta.get("orientations", {}).get(orientation)
        if terminals_def is None:
            raise ValueError(f"Nessuna definizione terminali per orientazione '{orientation}'")
        return terminals_def, orientation, None, None

    if strategy == "one_terminal_by_orientation":
        if image_binary is None:
            raise ValueError("one_terminal_by_orientation richiede image_binary.")
        connected_side, side_scores = strategy_detect_connected_side(image_binary, bbox)
        if connected_side is not None:
            terminals_def, orientation = resolve_one_terminal_orientation(meta, connected_side)
            return terminals_def, orientation, connected_side, side_scores
        default_orientation = meta.get("default_orientation")
        terminals_def = meta.get("orientations", {}).get(default_orientation)
        if terminals_def is None:
            raise ValueError(f"Nessuna definizione terminali per default_orientation '{default_orientation}'")
        return terminals_def, default_orientation, None, side_scores

    if strategy in {
        "two_terminal_by_connection_axis",
        "two_terminal_capacitor",
        "two_terminal_switch",
        "two_terminal_led",
        "two_terminal_round_source",
    }:
        if image_binary is None:
            raise ValueError(f"{strategy} richiede image_binary.")
        default_orientation = meta.get("default_orientation", "horizontal")
        class_name = meta.get("name", "")
        if strategy == "two_terminal_capacitor" or class_name in {"Capacitor", "Polarized_Capacitor"}:
            orientation, side_scores = detect_two_terminal_orientation_capacitor(
                image_binary, bbox, default_orientation=default_orientation
            )
        elif strategy == "two_terminal_switch" or class_name == "Switch":
            orientation, side_scores = strategy_detect_two_terminal_orientation_switch(
                image_binary, bbox, default_orientation=default_orientation
            )
        elif strategy == "two_terminal_led" or class_name == "LED":
            orientation, side_scores = detect_two_terminal_orientation_led(
                image_binary, bbox, default_orientation=default_orientation
            )
        elif (
            strategy == "two_terminal_round_source" or
            class_name in {"Signal_Source", "Voltage_Source", "Current_Source", "Meter"}
        ):
            orientation, side_scores = detect_two_terminal_orientation_round_source(
                image_binary, bbox, default_orientation=default_orientation
            )
        else:
            orientation, side_scores = strategy_detect_two_terminal_orientation_generic(
                image_binary, bbox, default_orientation=default_orientation
            )
        terminals_def = meta.get("orientations", {}).get(orientation)
        if terminals_def is None:
            raise ValueError(f"Nessuna definizione terminali per orientazione '{orientation}'")
        return terminals_def, orientation, None, side_scores
    
    if strategy == "terminal_auto_one_or_two":
        if image_binary is None:
            raise ValueError("terminal_auto_one_or_two richiede image_binary.")
        default_side = meta.get("default_orientation", "right")
        terminals_def, orientation, side_scores = detect_terminal_auto_one_or_two(image_binary, bbox, default_side=default_side)
        return terminals_def, orientation, None, side_scores

    # 3 terminali
    if strategy == "three_terminal_by_side_pattern":
        if image_binary is None:
            raise ValueError("three_terminal_by_side_pattern richiede image_binary.")

        default_orientation = meta.get("default_orientation", "right")
        class_name = meta.get("name", "")

        orientation, side_scores = strategy_detect_three_terminal_orientation(
            image_binary,
            bbox,
            class_name=class_name,
            default_orientation=default_orientation
        )

        terminals_def = meta.get("orientations", {}).get(orientation)
        if terminals_def is None:
            raise ValueError(f"Nessuna definizione terminali per orientazione '{orientation}'")

        return terminals_def, orientation, None, side_scores


    raise ValueError(f"Strategia terminali non supportata: {strategy}")