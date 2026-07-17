"""Definisce il vocabolario visuale comune del viewer Pipeline 2.0."""

from __future__ import annotations

from typing import Any


# Ogni simbolo usa dimensioni stabili indipendenti dalla bbox dell'immagine.
COMPONENT_SPECS: dict[str, dict[str, float]] = {
    "resistor": {"width": 92.0, "height": 34.0},
    "capacitor": {"width": 58.0, "height": 48.0},
    "polarized_capacitor": {"width": 58.0, "height": 48.0},
    "inductor": {"width": 92.0, "height": 38.0},
    "diode": {"width": 82.0, "height": 46.0},
    "led": {"width": 82.0, "height": 52.0},
    "lamp": {"width": 76.0, "height": 52.0},
    "switch": {"width": 84.0, "height": 44.0},
    "battery": {"width": 92.0, "height": 58.0},
    "scenario_voltage_source": {"width": 92.0, "height": 58.0},
    "dc_supply": {"width": 62.0, "height": 62.0},
    "voltage_source": {"width": 62.0, "height": 62.0},
    "current_source": {"width": 62.0, "height": 62.0},
    "signal_source": {"width": 62.0, "height": 62.0},
    "connector": {"width": 54.0, "height": 150.0, "pin_spacing": 58.0},
    "ground": {"width": 50.0, "height": 34.0},
    "npn_transistor": {"width": 70.0, "height": 70.0},
    "bjt": {"width": 70.0, "height": 70.0},
    "analog_meter": {"width": 108.0, "height": 72.0},
    "fuse": {"width": 74.0, "height": 30.0},
    "terminal": {"width": 18.0, "height": 18.0},
    "connection": {"width": 68.0, "height": 68.0},
    "structural": {"width": 68.0, "height": 46.0},
}


def normalize_component_type(class_name: Any, layout_kind: Any = "") -> str:
    """Converte i nomi Pipeline 1.0 e SPICE nel tipo visuale della libreria."""
    value = str(class_name or layout_kind or "structural").strip().lower().replace(" ", "_")
    aliases = {
        "gnd": "ground",
        "ground": "ground",
        "npn": "npn_transistor",
        "transistor": "npn_transistor",
        "npn_transistor": "npn_transistor",
        "analogmeter": "analog_meter",
        "polarized_capacitor": "polarized_capacitor",
        "scenario_voltage_source": "scenario_voltage_source",
        "dc_supply": "dc_supply",
        "signal_generator": "signal_source",
        "source": "signal_source",
    }
    if value in aliases:
        return aliases[value]
    if value in COMPONENT_SPECS:
        return value
    if "connector" in value:
        return "connector"
    if "switch" in value:
        return "switch"
    if "transistor" in value:
        return "npn_transistor"
    if "meter" in value:
        return "analog_meter"
    return str(layout_kind or "structural").lower() if str(layout_kind or "").lower() in COMPONENT_SPECS else "structural"


def component_spec(class_name: Any, layout_kind: Any = "", terminal_count: int = 0) -> dict[str, float]:
    """Restituisce una copia delle dimensioni standard del componente richiesto."""
    component_type = normalize_component_type(class_name, layout_kind)
    spec = dict(COMPONENT_SPECS.get(component_type, COMPONENT_SPECS["structural"]))
    if component_type == "connector":
        pin_spacing = spec["pin_spacing"]
        spec["height"] = max(spec["height"], 42.0 + pin_spacing * max(terminal_count - 1, 0))
    return spec
