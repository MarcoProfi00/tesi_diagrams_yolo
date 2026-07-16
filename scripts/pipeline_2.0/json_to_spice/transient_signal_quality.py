"""Metriche di qualita per segnali transitori periodici."""

from __future__ import annotations

import csv
import math
import re
from pathlib import Path
from typing import Any, Final


ANALYZED_CYCLES: Final = 3
MIN_ANALYZED_CYCLES: Final = 2
HARMONIC_COUNT: Final = 5
SAMPLES_PER_CYCLE: Final = 256
MIN_THD_IMPROVEMENT: Final = 0.20
MAX_ACCEPTABLE_THD: Final = 0.10
MIN_GAIN_RETENTION: Final = 0.25
NUMERIC_TOLERANCE: Final = 1e-12


def parse_spice_number(value: str) -> float | None:
    """Converte un numero SPICE con suffisso ingegneristico in float."""
    match = re.fullmatch(
        r"\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?)\s*(meg|[tgkmunpf])?\s*",
        str(value or ""),
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    multipliers = {
        "": 1.0,
        "t": 1e12,
        "g": 1e9,
        "meg": 1e6,
        "k": 1e3,
        "m": 1e-3,
        "u": 1e-6,
        "n": 1e-9,
        "p": 1e-12,
        "f": 1e-15,
    }
    suffix = str(match.group(2) or "").lower()
    return float(match.group(1)) * multipliers[suffix]


def voltage_node_name(quantity: str) -> str | None:
    """Estrae il nodo da una grandezza di tensione."""
    match = re.fullmatch(r"\s*v\(\s*([^)]+?)\s*\)\s*", str(quantity or ""), re.IGNORECASE)
    return match.group(1).strip() if match else None


def find_sine_frequency(netlist_path: Path, input_quantity: str) -> float | None:
    """Trova la frequenza della sorgente SIN collegata al nodo d'ingresso."""
    input_node = voltage_node_name(input_quantity)
    if not input_node or not netlist_path.exists():
        return None

    for raw_line in netlist_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("*"):
            continue
        parts = line.split(None, 3)
        if len(parts) < 4 or not parts[0].lower().startswith("v"):
            continue
        if input_node.lower() not in {parts[1].lower(), parts[2].lower()}:
            continue
        waveform = re.search(r"(?i)\bSIN\s*\(([^)]*)\)", parts[3])
        if not waveform:
            continue
        arguments = [item for item in re.split(r"[\s,]+", waveform.group(1).strip()) if item]
        if len(arguments) < 3:
            continue
        frequency = parse_spice_number(arguments[2])
        if frequency is not None and frequency > 0:
            return frequency
    return None


def read_transient_columns(
    csv_path: Path,
    input_quantity: str,
    output_quantity: str,
) -> tuple[list[float], list[float], list[float]] | None:
    """Legge tempo, ingresso e uscita dal CSV transitorio."""
    if not csv_path.exists():
        return None
    try:
        with csv_path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            headers = {
                str(name or "").strip().lower(): str(name or "")
                for name in reader.fieldnames or []
            }
            time_header = headers.get("time")
            input_header = headers.get(input_quantity.strip().lower())
            output_header = headers.get(output_quantity.strip().lower())
            if not time_header or not input_header or not output_header:
                return None

            times: list[float] = []
            inputs: list[float] = []
            outputs: list[float] = []
            for row in reader:
                try:
                    time_value = float(row[time_header])
                    input_value = float(row[input_header])
                    output_value = float(row[output_header])
                except (KeyError, TypeError, ValueError):
                    continue
                times.append(time_value)
                inputs.append(input_value)
                outputs.append(output_value)
    except (OSError, csv.Error):
        return None

    if len(times) < 4:
        return None
    ordered = sorted(zip(times, inputs, outputs), key=lambda item: item[0])
    return (
        [item[0] for item in ordered],
        [item[1] for item in ordered],
        [item[2] for item in ordered],
    )


def select_stable_window(
    times: list[float],
    inputs: list[float],
    outputs: list[float],
    frequency_hz: float,
) -> tuple[list[float], list[float], list[float], int] | None:
    """Seleziona le ultime oscillazioni complete, escludendo l'avviamento."""
    period = 1.0 / frequency_hz
    available_cycles = int((times[-1] - times[0]) / period + 1e-9)
    cycle_count = min(ANALYZED_CYCLES, available_cycles)
    if cycle_count < MIN_ANALYZED_CYCLES:
        return None

    start_time = times[-1] - cycle_count * period
    selected = [
        (time_value, input_value, output_value)
        for time_value, input_value, output_value in zip(times, inputs, outputs)
        if time_value >= start_time - NUMERIC_TOLERANCE
    ]
    if len(selected) < cycle_count * 8:
        return None
    return (
        [item[0] for item in selected],
        [item[1] for item in selected],
        [item[2] for item in selected],
        cycle_count,
    )


def resample_uniform(
    times: list[float],
    values: list[float],
    sample_count: int,
) -> tuple[list[float], list[float]]:
    """Interpola una traccia su una griglia uniforme senza duplicare l'estremo."""
    start_time = times[0]
    end_time = times[-1]
    step = (end_time - start_time) / sample_count
    target_times = [start_time + index * step for index in range(sample_count)]
    target_values: list[float] = []
    source_index = 0

    for target_time in target_times:
        while source_index + 1 < len(times) and times[source_index + 1] < target_time:
            source_index += 1
        if source_index + 1 >= len(times):
            target_values.append(values[-1])
            continue
        left_time = times[source_index]
        right_time = times[source_index + 1]
        if abs(right_time - left_time) < NUMERIC_TOLERANCE:
            target_values.append(values[source_index])
            continue
        fraction = (target_time - left_time) / (right_time - left_time)
        target_values.append(
            values[source_index]
            + fraction * (values[source_index + 1] - values[source_index])
        )
    return target_times, target_values


def harmonic_trace_metrics(
    times: list[float],
    values: list[float],
    frequency_hz: float,
) -> dict[str, Any] | None:
    """Calcola fondamentale e THD sulle prime cinque armoniche."""
    if not times or len(times) != len(values):
        return None
    mean_value = sum(values) / len(values)
    centered = [value - mean_value for value in values]
    amplitudes: list[float] = []

    for harmonic in range(1, HARMONIC_COUNT + 1):
        angular_frequency = 2.0 * math.pi * frequency_hz * harmonic
        sine = 2.0 / len(values) * sum(
            value * math.sin(angular_frequency * time_value)
            for time_value, value in zip(times, centered)
        )
        cosine = 2.0 / len(values) * sum(
            value * math.cos(angular_frequency * time_value)
            for time_value, value in zip(times, centered)
        )
        amplitudes.append(math.hypot(sine, cosine))

    fundamental = amplitudes[0]
    if fundamental < NUMERIC_TOLERANCE:
        return None
    thd = math.sqrt(sum(amplitude**2 for amplitude in amplitudes[1:])) / fundamental
    return {
        "dc_mean": mean_value,
        "fundamental_peak": fundamental,
        "fundamental_vpp": 2.0 * fundamental,
        "harmonic_peaks": amplitudes,
        "thd": thd,
    }


def analyze_sine_quality(
    csv_path: Path,
    netlist_path: Path,
    input_quantity: str,
    output_quantity: str,
) -> dict[str, Any]:
    """Analizza guadagno fondamentale e THD di una coppia ingresso/uscita."""
    frequency_hz = find_sine_frequency(netlist_path, input_quantity)
    if frequency_hz is None:
        return {"available": False, "reason": "sine_source_not_found"}
    columns = read_transient_columns(csv_path, input_quantity, output_quantity)
    if columns is None:
        return {"available": False, "reason": "transient_columns_not_found"}
    stable = select_stable_window(*columns, frequency_hz)
    if stable is None:
        return {"available": False, "reason": "insufficient_complete_cycles"}

    times, inputs, outputs, cycle_count = stable
    sample_count = cycle_count * SAMPLES_PER_CYCLE
    uniform_times, uniform_inputs = resample_uniform(times, inputs, sample_count)
    _, uniform_outputs = resample_uniform(times, outputs, sample_count)
    input_metrics = harmonic_trace_metrics(uniform_times, uniform_inputs, frequency_hz)
    output_metrics = harmonic_trace_metrics(uniform_times, uniform_outputs, frequency_hz)
    if input_metrics is None or output_metrics is None:
        return {"available": False, "reason": "fundamental_not_measurable"}

    gain = output_metrics["fundamental_peak"] / input_metrics["fundamental_peak"]
    return {
        "available": True,
        "metric": "thd",
        "frequency_hz": frequency_hz,
        "analyzed_cycles": cycle_count,
        "window_start": times[0],
        "window_end": times[-1],
        "input": input_metrics,
        "output": output_metrics,
        "fundamental_gain": gain,
    }


def compare_sine_quality(
    base_metrics: dict[str, Any],
    scenario_metrics: dict[str, Any],
) -> dict[str, Any]:
    """Confronta THD e guadagno fondamentale tra base e scenario."""
    if not base_metrics.get("available") or not scenario_metrics.get("available"):
        return {
            "available": False,
            "reason": scenario_metrics.get("reason") or base_metrics.get("reason"),
            "base": base_metrics,
            "scenario": scenario_metrics,
        }

    base_thd = float(base_metrics["output"]["thd"])
    scenario_thd = float(scenario_metrics["output"]["thd"])
    thd_improvement = (
        (base_thd - scenario_thd) / base_thd
        if base_thd >= NUMERIC_TOLERANCE
        else None
    )
    base_gain = float(base_metrics["fundamental_gain"])
    scenario_gain = float(scenario_metrics["fundamental_gain"])
    gain_retention = (
        scenario_gain / base_gain
        if abs(base_gain) >= NUMERIC_TOLERANCE
        else None
    )
    improved = thd_improvement is not None and thd_improvement >= MIN_THD_IMPROVEMENT
    acceptable = scenario_thd <= MAX_ACCEPTABLE_THD
    output_preserved = (
        gain_retention is not None
        and gain_retention >= MIN_GAIN_RETENTION
        and scenario_metrics["output"]["fundamental_peak"] >= NUMERIC_TOLERANCE
    )
    return {
        "available": True,
        "metric": "thd",
        "base": base_metrics,
        "scenario": scenario_metrics,
        "base_thd": base_thd,
        "scenario_thd": scenario_thd,
        "relative_improvement": thd_improvement,
        "base_fundamental_gain": base_gain,
        "scenario_fundamental_gain": scenario_gain,
        "gain_retention": gain_retention,
        "improved": improved,
        "acceptable": acceptable,
        "output_preserved": output_preserved,
        "resolved": improved and acceptable and output_preserved,
        "thresholds": {
            "minimum_relative_improvement": MIN_THD_IMPROVEMENT,
            "maximum_acceptable_thd": MAX_ACCEPTABLE_THD,
            "minimum_gain_retention": MIN_GAIN_RETENTION,
        },
    }
