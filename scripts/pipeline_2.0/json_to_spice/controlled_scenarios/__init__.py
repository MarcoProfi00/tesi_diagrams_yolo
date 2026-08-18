"""Servizi interni per applicare e valutare scenari SPICE controllati."""

from .measurements import (
    classify_change,
    count_ngspice_stderr_warnings,
    is_internal_device_current_quantity,
    is_stderr_quantity,
    is_voltage_quantity,
    normalize_quantity_name,
    parse_float,
    parse_ngspice_stdout,
    parse_tran_csv_metrics,
    quantity_lookup_key,
    voltage_quantity_nodes,
)
from .outcome import evaluate_diagnostic_outcome

__all__ = [
    "classify_change",
    "count_ngspice_stderr_warnings",
    "evaluate_diagnostic_outcome",
    "is_internal_device_current_quantity",
    "is_stderr_quantity",
    "is_voltage_quantity",
    "normalize_quantity_name",
    "parse_float",
    "parse_ngspice_stdout",
    "parse_tran_csv_metrics",
    "quantity_lookup_key",
    "voltage_quantity_nodes",
]
