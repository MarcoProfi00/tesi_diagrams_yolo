from .config import *
from .geometry import geom_infer_orientation_from_bbox
from .strategies_basic import (
    detect_breaker_terminals,
    detect_two_terminal_orientation_capacitor,
    detect_two_terminal_orientation_led,
    detect_two_terminal_orientation_inductor,
    detect_two_terminal_orientation_round_source,
    detect_two_terminal_orientation_variable_resistor,
    resolve_one_terminal_orientation,
    strategy_detect_connected_side,
    strategy_detect_two_terminal_orientation_generic,
    strategy_detect_two_terminal_orientation_switch,
)
from .strategies_terminal_class import detect_terminal_auto_one_or_two
from .strategies_three_terminal import strategy_detect_three_terminal_orientation
from .strategies_opamp import detect_opamp_terminals
from .strategies_connector import detect_connector_terminals
from .strategies_structured_symbols import (
    detect_analog_meter_terminals,
    detect_transformer_terminals,
)


# Get oriented terminals.
def _get_oriented_terminals(meta: dict, orientation: str):
    terminals_def = meta.get("orientations", {}).get(orientation)
    if terminals_def is None:
        raise ValueError(f"Nessuna definizione terminali per orientazione '{orientation}'")
    return terminals_def


# Resolve terminal point mode.
def resolve_terminal_point_mode(meta: dict):
    explicit_mode = meta.get("terminal_point_mode")
    if explicit_mode is not None:
        return explicit_mode

    strategy = meta.get("terminal_strategy", "")
    class_name = meta.get("name", "")

    if strategy == "three_terminal_by_side_pattern":
        return THREE_TERMINAL_POINT_MODE

    if strategy == "opamp_by_orientation_and_optional_supply":
        return OPAMP_POINT_MODE

    if strategy == "connector_by_projection":
        return "bbox_side_center"

    if strategy in {"analog_meter_by_posts", "transformer_external_wires"}:
        return "strategy_absolute_point"

    if strategy in {
        "two_terminal_led",
        "two_terminal_variable_resistor",
        "one_terminal_by_orientation",
    }:
        return "two_terminal_side_peak"

    if class_name in {"LED", "Diode"}:
        return "two_terminal_side_peak"

    return "bbox_side_center"


# Resolve two terminal orientation.
def _resolve_two_terminal_orientation(strategy: str, class_name: str, image_binary, bbox, default_orientation: str):
    if strategy == "two_terminal_capacitor" or class_name in {"Capacitor", "Polarized_Capacitor"}:
        return detect_two_terminal_orientation_capacitor(
            image_binary,
            bbox,
            default_orientation=default_orientation,
        )

    if strategy == "two_terminal_switch" or class_name == "Switch":
        return strategy_detect_two_terminal_orientation_switch(
            image_binary,
            bbox,
            default_orientation=default_orientation,
        )

    if strategy == "two_terminal_led" or class_name == "LED":
        return detect_two_terminal_orientation_led(
            image_binary,
            bbox,
            default_orientation=default_orientation,
        )

    if class_name == "Diode":
        return strategy_detect_two_terminal_orientation_generic(
            image_binary,
            bbox,
            default_orientation=default_orientation,
        )

    if class_name == "Inductor":
        return detect_two_terminal_orientation_inductor(
            image_binary,
            bbox,
            default_orientation=default_orientation,
        )

    if (
        strategy == "two_terminal_round_source"
        or class_name in {"Signal_Source", "Voltage_Source", "Current_Source", "Meter"}
    ):
        return detect_two_terminal_orientation_round_source(
            image_binary,
            bbox,
            default_orientation=default_orientation,
        )

    if strategy == "two_terminal_variable_resistor" or class_name == "Resistor":
        return detect_two_terminal_orientation_variable_resistor(
            image_binary,
            bbox,
            default_orientation=default_orientation,
        )

    return strategy_detect_two_terminal_orientation_generic(
        image_binary,
        bbox,
        default_orientation=default_orientation,
    )


# =========================================================
# STRATEGY DISPATCHER
# =========================================================
# Get terminals definition.
def get_terminals_definition(meta: dict, bbox, image_binary=None):
    strategy = meta.get("terminal_strategy", "fixed")

    if strategy == "fixed":
        return meta.get("terminals", []), None, None, None

    if strategy == "auto_by_aspect_ratio":
        class_name = meta.get("name", "")
        default_orientation = meta.get("default_orientation", "horizontal")

        if image_binary is not None and class_name == "Transformer":
            orientation, side_scores = strategy_detect_two_terminal_orientation_generic(
                image_binary,
                bbox,
                default_orientation=default_orientation,
            )
            return _get_oriented_terminals(meta, orientation), orientation, None, side_scores

        orientation = geom_infer_orientation_from_bbox(
            bbox,
            default_orientation=default_orientation,
        )
        return _get_oriented_terminals(meta, orientation), orientation, None, None

    if strategy == "one_terminal_by_orientation":
        if image_binary is None:
            raise ValueError("one_terminal_by_orientation richiede image_binary.")

        connected_side, side_scores = strategy_detect_connected_side(image_binary, bbox)

        if connected_side is not None:
            terminals_def, orientation = resolve_one_terminal_orientation(meta, connected_side)
            return terminals_def, orientation, connected_side, side_scores

        default_orientation = meta.get("default_orientation")
        if default_orientation is None:
            raise ValueError("Manca default_orientation per one_terminal_by_orientation.")
        
        return _get_oriented_terminals(meta, default_orientation), default_orientation, None, side_scores

    if strategy in {
        "two_terminal_by_connection_axis",
        "two_terminal_capacitor",
        "two_terminal_switch",
        "two_terminal_led",
        "two_terminal_round_source",
        "two_terminal_variable_resistor",
    }:
        if image_binary is None:
            raise ValueError(f"{strategy} richiede image_binary.")

        default_orientation = meta.get("default_orientation", "horizontal")
        class_name = meta.get("name", "")

        if class_name == "Breaker":
            terminals_def, orientation, side_scores = detect_breaker_terminals(
                image_binary,
                bbox,
            )
            if terminals_def is not None:
                return terminals_def, orientation, None, side_scores

        orientation, side_scores = _resolve_two_terminal_orientation(
            strategy=strategy,
            class_name=class_name,
            image_binary=image_binary,
            bbox=bbox,
            default_orientation=default_orientation,
        )

        return _get_oriented_terminals(meta, orientation), orientation, None, side_scores

    if strategy == "terminal_auto_one_or_two":
        if image_binary is None:
            raise ValueError("terminal_auto_one_or_two richiede image_binary.")

        default_side = meta.get("default_orientation", "right")
        terminals_def, orientation, side_scores = detect_terminal_auto_one_or_two(
            image_binary,
            bbox,
            default_side=default_side,
        )
        return terminals_def, orientation, None, side_scores

    if strategy == "connector_by_projection":
        if image_binary is None:
            raise ValueError("connector_by_projection richiede image_binary.")

        default_orientation = meta.get("default_orientation", "vertical")
        terminals_def, orientation, side_scores = detect_connector_terminals(
            meta,
            image_binary,
            bbox,
            default_orientation=default_orientation,
        )
        return terminals_def, orientation, None, side_scores

    if strategy == "analog_meter_by_posts":
        if image_binary is None:
            raise ValueError("analog_meter_by_posts richiede image_binary.")

        terminals_def, orientation, connected_side, side_scores = detect_analog_meter_terminals(
            meta,
            image_binary,
            bbox,
        )
        return terminals_def, orientation, connected_side, side_scores

    if strategy == "transformer_external_wires":
        if image_binary is None:
            raise ValueError("transformer_external_wires richiede image_binary.")

        terminals_def, orientation, connected_side, side_scores = detect_transformer_terminals(
            meta,
            image_binary,
            bbox,
        )
        return terminals_def, orientation, connected_side, side_scores

    if strategy == "opamp_by_orientation_and_optional_supply":
        if image_binary is None:
            raise ValueError("opamp_by_orientation_and_optional_supply richiede image_binary.")

        default_orientation = meta.get("default_orientation", "right")
        terminals_def, orientation, side_scores = detect_opamp_terminals(
            meta,
            image_binary,
            bbox,
            default_orientation=default_orientation,
        )
        return terminals_def, orientation, None, side_scores

    if strategy == "three_terminal_by_side_pattern":
        if image_binary is None:
            raise ValueError("three_terminal_by_side_pattern richiede image_binary.")

        default_orientation = meta.get("default_orientation", "right")
        class_name = meta.get("name", "")

        orientation, side_scores = strategy_detect_three_terminal_orientation(
            image_binary,
            bbox,
            class_name=class_name,
            default_orientation=default_orientation,
        )
        return _get_oriented_terminals(meta, orientation), orientation, None, side_scores

    raise ValueError(f"Strategia terminali non supportata: {strategy}")
