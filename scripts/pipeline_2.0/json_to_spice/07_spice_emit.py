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
from pathlib import Path
from typing import Any


MODEL_LINES = {
    "LED_RED": ".model LED_RED D",
}


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

    if not prefix or len(nodes) < 2:
        return None, f"{component_id}: incomplete direct rule"

    if prefix in ("V", "I"):
        value = spice_value(parameters.get("value"), parameters.get("unit"))
        line = f"{element_name(prefix, component_id)} {nodes[0]} {nodes[1]} {source_kind(parameters)} {value}"
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

    if status != "spice_ready":
        return None, None, None

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


def build_spice_netlist(component_rules: dict[str, Any]) -> dict[str, Any]:
    """Build netlist text and a compact emission report."""
    circuit_id = component_rules.get("circuit_id") or "unknown"
    lines = [
        f"* pipeline2.0 netlist",
        f"* circuit: {circuit_id}",
        "",
    ]
    warnings: list[str] = []
    informational_skips: list[str] = []
    skipped: list[str] = []
    models: set[str] = set()
    emitted_elements = 0

    for supply_name, supply in (component_rules.get("supplies") or {}).items():
        line, warning = emit_supply(str(supply_name), supply)
        if line:
            lines.append(line)
            emitted_elements += 1
        if warning:
            warnings.append(warning)

    for component_id, rule in (component_rules.get("components") or {}).items():
        line, model, warning = emit_component(str(component_id), rule)
        if line:
            lines.append(line)
            if not line.startswith("*"):
                emitted_elements += 1
        else:
            skipped.append(str(component_id))
            if rule.get("status") == "not_emitted":
                informational_skips.append(f"{component_id}: structural component not emitted")
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
            lines.append(MODEL_LINES.get(model, f".model {model} D"))

    lines.extend(["", ".op", ".end"])

    report = {
        "circuit_id": circuit_id,
        "source_format": "pipeline2.0_spice_emit_report",
        "emitted_elements": emitted_elements,
        "skipped_elements": len(skipped),
        "skipped_components": skipped,
        "informational_skips": informational_skips,
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
) -> tuple[Path, dict[str, Any]]:
    """Write 07_netlist.cir and return the emission report."""
    output_path = Path(output_dir)
    result = build_spice_netlist(component_rules)
    netlist_path = output_path / "07_netlist.cir"
    netlist_path.write_text(result["netlist_text"], encoding="utf-8")
    return netlist_path, result["report"]
