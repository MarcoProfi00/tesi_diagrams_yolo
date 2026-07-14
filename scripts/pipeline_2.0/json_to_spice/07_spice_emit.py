"""
Generazione della netlist SPICE.

Questo modulo converte la rappresentazione normalizzata del circuito, la
node map e i valori YAML in una netlist SPICE completa o parziale.

La generazione non deve essere tutto-o-niente:

- in modalita READY produce una netlist eseguibile;
- in modalita PARTIAL produce una netlist parziale con commenti e warning;
- in modalita NOT_READY puo produrre solo un riepilogo delle cause di blocco.

Responsabilita previste:

- emettere righe SPICE per componenti supportati;
- includere modelli .model o .subckt quando dichiarati;
- aggiungere analisi base come .op o .tran quando richiesto;
- commentare componenti saltati per valori o modelli mancanti;
- produrre spice_netlist.cir e conversion_report.json.
"""

from __future__ import annotations

import re
import math
from pathlib import Path
from typing import Any


def build_model_lines(spice_models: dict[str, Any] | None = None) -> dict[str, str]:
    """Costruisce il dizionario dei modelli SPICE letti dai metadata."""
    model_lines: dict[str, str] = {}
    yaml_models = (spice_models or {}).get("models") or {}

    # I modelli SPICE non vengono definiti nel codice: lo step 07 legge solo il
    # file metadata/pipeline2_spice_models.yaml e usa le righe richieste.
    for model_name, model_data in yaml_models.items():
        if isinstance(model_data, dict):
            line = model_data.get("line")
        else:
            line = model_data
        if line:
            model_lines[str(model_name)] = str(line)

    return model_lines


def safe_name(raw_name: str) -> str:
    """Return a SPICE-safe element name fragment."""
    return re.sub(r"[^A-Za-z0-9_]", "_", raw_name)


def element_name(prefix: str, raw_name: str) -> str:
    """Build a SPICE element name with a valid prefix."""
    return f"{prefix}{safe_name(raw_name)}"


def spice_value(value: Any, unit: str | None = None) -> str:
    """
    Convert a simple scalar value to SPICE text.

    YAML values should preferably already be stored in base units. This helper
    only adds a few common suffixes when needed.
    """
    if value is None:
        return ""

    unit_text = (unit or "").strip().lower()
    suffix_by_unit = {
        "ohm": "",
        "kohm": "k",
        "mohm": "meg",
        "pf": "p",
        "nf": "n",
        "uf": "u",
        "µf": "u",
        "mf": "m",
        "khz": "k",
        "mhz": "meg",
    }
    suffix = suffix_by_unit.get(unit_text, "")
    return f"{value}{suffix}"


def source_kind(parameters: dict[str, Any]) -> str:
    """Return the minimal SPICE source kind, usually DC for now."""
    kind = str(parameters.get("type", "dc")).upper()
    if kind == "DC":
        return "DC"
    return kind


def voltage_source_expression(parameters: dict[str, Any]) -> str:
    """Costruisce l'espressione SPICE per una sorgente di tensione."""
    source_type = str(parameters.get("type", "dc")).lower()
    waveform = str(parameters.get("waveform", "")).lower()

    if source_type == "pulse" or waveform == "square":
        low_value = parameters.get("low_value", 0)
        high_value = parameters.get("high_value", parameters.get("value"))
        delay = parameters.get("delay", 0)
        rise_time = parameters.get("rise_time", 0)
        fall_time = parameters.get("fall_time", 0)
        pulse_width = parameters.get("pulse_width")
        period = parameters.get("period")
        if high_value in (None, "") or pulse_width in (None, "") or period in (None, ""):
            return f"DC {spice_value(parameters.get('value'), parameters.get('unit'))}"
        return f"PULSE({low_value} {high_value} {delay} {rise_time} {fall_time} {pulse_width} {period})"

    if source_type == "sin" or waveform == "sin":
        offset = parameters.get("offset", 0)
        amplitude = parameters.get("amplitude", parameters.get("value"))
        frequency = parameters.get("frequency")
        if amplitude in (None, "") or frequency in (None, ""):
            return f"DC {spice_value(parameters.get('value'), parameters.get('unit'))}"
        return f"SIN({offset} {amplitude} {frequency})"

    return f"{source_kind(parameters)} {spice_value(parameters.get('value'), parameters.get('unit'))}"


def emit_equivalent_ac_source(component_id: str, rule: dict[str, Any]) -> tuple[str | None, str | None]:
    """Emit a transformer equivalent as a sinusoidal voltage source."""
    nodes = rule.get("nodes") or []
    parameters = rule.get("parameters") or {}
    if len(nodes) != 2:
        return None, f"{component_id}: equivalent AC source does not have two nodes"

    rms_value = parameters.get("secondary_voltage_rms")
    frequency = parameters.get("frequency")
    if rms_value in (None, "") or frequency in (None, ""):
        return None, f"{component_id}: missing RMS voltage or frequency"

    peak_value = parameters.get("secondary_voltage_peak")
    if peak_value in (None, ""):
        peak_value = float(rms_value) * math.sqrt(2)

    offset = parameters.get("offset", 0)
    line = (
        f"{element_name('V', component_id)} {nodes[0]} {nodes[1]} "
        f"SIN({offset} {peak_value:.6g} {frequency})"
    )
    return line, None


def emit_supply(name: str, supply: dict[str, Any]) -> tuple[str | None, str | None]:
    """Emit a manual supply as a SPICE voltage source."""
    if supply.get("status") != "spice_ready":
        return None, f"{name}: supply not ready"

    nodes = supply.get("nodes") or []
    parameters = supply.get("parameters") or {}
    if len(nodes) != 2:
        return None, f"{name}: supply does not have two nodes"

    line = (
        f"{element_name('V', str(name))} "
        f"{nodes[0]} {nodes[1]} "
        f"{source_kind(parameters)} {spice_value(parameters.get('value'), parameters.get('unit'))}"
    )
    return line, None


def emit_direct(component_id: str, rule: dict[str, Any]) -> tuple[str | None, str | None]:
    """Emit direct SPICE primitives such as R, C, L, V, I."""
    prefix = rule.get("spice_prefix")
    nodes = rule.get("nodes") or []
    parameters = rule.get("parameters") or {}
    emit_as = rule.get("emit_as")

    if emit_as == "equivalent_ac_source":
        return emit_equivalent_ac_source(component_id, rule)

    if not prefix or len(nodes) < 2:
        return None, f"{component_id}: incomplete direct rule"

    if prefix in ("V", "I"):
        expression = voltage_source_expression(parameters) if prefix == "V" else (
            f"{source_kind(parameters)} {spice_value(parameters.get('value'), parameters.get('unit'))}"
        )
        line = f"{element_name(prefix, component_id)} {nodes[0]} {nodes[1]} {expression}"
        return line, None

    value = parameters.get("value")
    unit = parameters.get("unit")
    if emit_as in ("resistive_load", "resistor"):
        unit = parameters.get("resistance_unit") or unit
    line = f"{element_name(prefix, component_id)} {' '.join(nodes)} {spice_value(value, unit)}"
    return line, None


def emit_equivalent(component_id: str, rule: dict[str, Any]) -> tuple[str | None, str | None]:
    """Emit equivalent loads, currently as resistors."""
    nodes = rule.get("nodes") or []
    parameters = rule.get("parameters") or {}
    if len(nodes) != 2:
        return None, f"{component_id}: equivalent component does not have two nodes"

    value = parameters.get("equivalent_resistance")
    unit = parameters.get("resistance_unit") or parameters.get("unit")
    line = f"{element_name('R', component_id)} {nodes[0]} {nodes[1]} {spice_value(value, unit)}"
    return line, None


def emit_model_component(component_id: str, rule: dict[str, Any]) -> tuple[str | None, str | None]:
    """Emit model-based components, currently LEDs and diodes."""
    prefix = rule.get("spice_prefix")
    nodes = rule.get("nodes") or []
    parameters = rule.get("parameters") or {}
    model = parameters.get("model")

    if not prefix or not model or len(nodes) < 2:
        return None, f"{component_id}: incomplete model-based component"

    line = f"{element_name(prefix, component_id)} {' '.join(nodes)} {model}"
    return line, None


def emit_simplified(component_id: str, rule: dict[str, Any]) -> tuple[str | None, str | None]:
    """Emit simplified components such as open or closed switches."""
    nodes = rule.get("nodes") or []
    strategy = rule.get("strategy")
    if len(nodes) != 2:
        return None, f"{component_id}: switch does not have two nodes"

    if strategy == "open_circuit":
        return f"* {component_id} open: not emitted", f"{component_id}: open switch not emitted"
    if strategy == "short_circuit":
        return f"{element_name('R', component_id)} {nodes[0]} {nodes[1]} 1m", None
    return None, f"{component_id}: unsupported switch strategy"


def emit_component(component_id: str, rule: dict[str, Any]) -> tuple[str | None, str | None, str | None]:
    """Emit a single SPICE line or comment."""
    status = rule.get("status")
    support = rule.get("spice_support")
    nodes = [str(node) for node in (rule.get("nodes") or [])]

    if status == "measurement_only":
        parameters = rule.get("parameters") or {}
        input_resistance = parameters.get("input_resistance")
        if input_resistance not in (None, "") and len(nodes) == 2:
            unit = parameters.get("resistance_unit") or "ohm"
            line = f"{element_name('Rmeter_', component_id)} {nodes[0]} {nodes[1]} {spice_value(input_resistance, unit)}"
            return line, None, None
        return None, None, None

    if status != "spice_ready":
        return None, None, None

    if len(nodes) >= 2 and len(set(nodes)) == 1:
        return None, None, f"{component_id}: terminals collapse to the same SPICE node; not emitted"

    if support == "direct":
        line, warning = emit_direct(component_id, rule)
    elif support == "equivalent":
        line, warning = emit_equivalent(component_id, rule)
    elif support == "model":
        line, warning = emit_model_component(component_id, rule)
    elif support == "simplified":
        line, warning = emit_simplified(component_id, rule)
    else:
        line, warning = None, f"{component_id}: unsupported SPICE support type ({support})"

    model = None
    parameters = rule.get("parameters") or {}
    if support == "model":
        model = parameters.get("model")

    return line, model, warning


def build_analysis_lines(simulation: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Costruisce le direttive di analisi SPICE richieste dal values.yaml."""
    analyses = simulation.get("analyses") or ["op"]
    if not isinstance(analyses, list):
        analyses = [analyses]

    lines: list[str] = []
    enabled = {str(item).lower() for item in analyses}

    if "op" in enabled:
        lines.append(".op")

    if "tran" in enabled:
        lines.append(".save all")
        tran = simulation.get("tran") or {}
        step = tran.get("step", "0.1ms") if isinstance(tran, dict) else "0.1ms"
        stop = tran.get("stop", "40ms") if isinstance(tran, dict) else "40ms"
        lines.append(f".tran {step} {stop}")

    return lines, sorted(enabled)


def build_control_lines(analyses: list[str], probe_nodes: list[str]) -> list[str]:
    """Aggiunge comandi ngspice per esportare dati transitori plottabili."""
    if "tran" not in analyses or not probe_nodes:
        return []

    voltage_vectors = " ".join(f"v({node})" for node in probe_nodes)
    return [
        "",
        ".control",
        "set wr_singlescale",
        "set wr_vecnames",
        "run",
        f"wrdata 08_tran.csv time {voltage_vectors}",
        ".endc",
    ]


def build_spice_netlist(
    component_rules: dict[str, Any],
    spice_models: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build netlist text and a compact emission report."""
    circuit_id = component_rules.get("circuit_id") or "unknown"
    model_lines = build_model_lines(spice_models)
    lines = [
        f"* pipeline2.0 netlist",
        f"* circuit: {circuit_id}",
        "",
    ]
    warnings: list[str] = []
    informational_skips: list[str] = []
    measurement_points: list[dict[str, Any]] = []
    skipped: list[str] = []
    models: set[str] = set()
    transient_nodes: set[str] = set()
    emitted_elements = 0

    for supply_name, supply in (component_rules.get("supplies") or {}).items():
        line, warning = emit_supply(str(supply_name), supply)
        if line:
            lines.append(line)
            emitted_elements += 1
            for node in supply.get("nodes") or []:
                if str(node) != "0":
                    transient_nodes.add(str(node))
        if warning:
            warnings.append(warning)

    for component_id, rule in (component_rules.get("components") or {}).items():
        line, model, warning = emit_component(str(component_id), rule)
        if rule.get("status") == "measurement_only":
            measurement_points.append({
                "component_id": str(component_id),
                "kind": rule.get("measurement_kind", "voltage"),
                "nodes": rule.get("nodes") or [],
                "emit_as": rule.get("emit_as"),
                "reason": rule.get("reason"),
            })
        if line:
            lines.append(line)
            if not line.startswith("*"):
                emitted_elements += 1
                for node in rule.get("nodes") or []:
                    if str(node) != "0":
                        transient_nodes.add(str(node))
        else:
            skipped.append(str(component_id))
            if rule.get("status") == "not_emitted":
                informational_skips.append(f"{component_id}: structural component not emitted")
            elif rule.get("status") == "measurement_only":
                informational_skips.append(f"{component_id}: voltage probe not emitted; read voltage between its nodes")
            elif rule.get("status") == "pin_aware":
                warnings.append(f"{component_id}: requires a device profile or dedicated model")
            elif rule.get("status") == "unsupported_for_now":
                warnings.append(f"{component_id}: class not yet supported by SPICE emit")
            elif rule.get("status") == "missing_parameters":
                warnings.append(f"{component_id}: missing parameters for SPICE emission")
            elif rule.get("status") == "invalid_node_order":
                warnings.append(f"{component_id}: incomplete nodes or invalid terminal order")
        if model:
            models.add(str(model))
        if warning:
            warnings.append(warning)

    if models:
        lines.append("")
        for model in sorted(models):
            model_line = model_lines.get(model)
            if model_line:
                lines.append(model_line)
            else:
                warnings.append(f"{model}: SPICE model not found in pipeline2_spice_models.yaml")
                lines.append(f"* missing model: {model}")

    analysis_lines, analyses = build_analysis_lines(component_rules.get("simulation") or {})
    probe_nodes = sorted(transient_nodes)
    control_lines = build_control_lines(analyses, probe_nodes)
    lines.extend(["", *analysis_lines, *control_lines, ".end"])

    report = {
        "circuit_id": circuit_id,
        "source_format": "pipeline2.0_spice_emit_report",
        "emitted_elements": emitted_elements,
        "skipped_elements": len(skipped),
        "skipped_components": skipped,
        "informational_skips": informational_skips,
        "measurement_points": measurement_points,
        "analyses": analyses,
        "transient_export": {
            "path": "08_tran.csv" if "tran" in analyses and probe_nodes else None,
            "nodes": probe_nodes if "tran" in analyses else [],
        },
        "models": sorted(models),
        "warnings": warnings,
    }

    return {
        "netlist_text": "\n".join(lines) + "\n",
        "report": report,
    }


def write_spice_outputs(
    output_dir: str | Path,
    component_rules: dict[str, Any],
    spice_models: dict[str, Any] | None = None,
) -> tuple[Path, dict[str, Any]]:
    """Write 07_netlist.cir and return the emission report."""
    output_path = Path(output_dir)
    result = build_spice_netlist(component_rules, spice_models=spice_models)
    netlist_path = output_path / "07_netlist.cir"
    netlist_path.write_text(result["netlist_text"], encoding="utf-8")
    return netlist_path, result["report"]
