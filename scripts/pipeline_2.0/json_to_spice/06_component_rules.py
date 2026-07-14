"""
Regole di conversione e classificazione dei componenti.

Questo modulo definisce come trattare ogni classe di componente riconosciuta
dalla pipeline_1.0 nella fase elettrica.

Esempi di decisioni previste:

- Resistor -> elemento SPICE R se il valore e disponibile;
- Capacitor -> elemento SPICE C se il valore e disponibile;
- Battery/Voltage source -> sorgente SPICE V;
- Diode/LED -> elemento D con modello dichiarato;
- Lamp/Speaker -> carico semplificato quando dichiarato;
- Switch -> gestione in base allo stato open/closed;
- BJT/MOSFET -> conversione se modello e pin-map sono disponibili;
- Connector/Terminal -> non simulabili direttamente, ma utili per nodi;
- Integrated_Circuit -> modello SPICE, modello semplificato o black box pin-aware.

Le regole dovranno contribuire a stabilire lo stato del circuito:
READY, PARTIAL o NOT_READY.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


READY_SUPPORT = {"direct", "model", "equivalent", "simplified"}
STRUCTURAL_SUPPORT = {"structural"}
MEASUREMENT_SUPPORT = {"measurement"}
DEFERRED_SUPPORT = {"pin_aware", "unsupported_for_now"}


def as_list(value: Any) -> list[Any]:
    """Converte valori scalari o mancanti in lista."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def has_field(data: dict[str, Any], field_name: str) -> bool:
    """Controlla se un campo richiesto e presente e valorizzato."""
    return field_name in data and data.get(field_name) not in (None, "")


def missing_fields(data: dict[str, Any], required_fields: list[str]) -> list[str]:
    """Restituisce i campi richiesti ma assenti."""
    return [field for field in required_fields if not has_field(data, field)]


def ordered_nodes(
    terminal_nodes: dict[str, str],
    node_order: list[str],
) -> tuple[list[str], list[str]]:
    """Ordina i nodi secondo l'ordine terminali richiesto dalla regola."""
    nodes: list[str] = []
    missing_terminals: list[str] = []

    for terminal_name in node_order:
        node_id = terminal_nodes.get(terminal_name)
        if node_id in (None, ""):
            missing_terminals.append(terminal_name)
        else:
            nodes.append(str(node_id))

    return nodes, missing_terminals


def build_supply_rules(values_bound: dict[str, Any]) -> dict[str, Any]:
    """
    Prepara le supply manuali come sorgenti SPICE potenziali.

    Per ora e volutamente minimale: una supply con nodo e valore diventa una
    sorgente di tensione indipendente verso il riferimento dichiarato o 0.
    """
    supply_rules: dict[str, Any] = {}

    for supply_name, supply_data in (values_bound.get("supplies") or {}).items():
        if not isinstance(supply_data, dict):
            continue

        node_id = supply_data.get("node")
        value = supply_data.get("value")
        reference = supply_data.get("reference", "0")
        status = "spice_ready" if node_id not in (None, "") and value not in (None, "") else "missing_parameters"

        supply_rules[str(supply_name)] = {
            "status": status,
            "spice_prefix": "V",
            "emit_as": "independent_voltage_source",
            "nodes": [str(node_id), str(reference)] if node_id not in (None, "") else [],
            "parameters": dict(supply_data),
        }

    return dict(sorted(supply_rules.items()))


def classify_component_rule(
    component_id: str,
    component_data: dict[str, Any],
    class_rule: dict[str, Any] | None,
) -> dict[str, Any]:
    """Apply a single SPICE rule to an already value-bound component."""
    class_name = component_data.get("class_name")
    value_data = component_data.get("value_data") or {}
    terminal_nodes = component_data.get("terminal_nodes") or {}
    value_status = component_data.get("status")

    if class_rule is None:
        return {
            "class_name": class_name,
            "status": "unsupported_for_now",
            "reason": "Class not found in pipeline2_spice_classes.yaml.",
        }

    spice_support = class_rule.get("spice_support", "unsupported_for_now")

    if spice_support in STRUCTURAL_SUPPORT:
        return {
            "class_name": class_name,
            "status": "not_emitted",
            "spice_support": spice_support,
            "reason": class_rule.get("reason", "Structural component used for topology and not emitted."),
        }

    if spice_support in MEASUREMENT_SUPPORT:
        node_order = [str(node) for node in as_list(class_rule.get("node_order"))]
        nodes, terminals_missing = ordered_nodes(terminal_nodes, node_order)
        if terminals_missing:
            return {
                "class_name": class_name,
                "status": "invalid_node_order",
                "spice_support": spice_support,
                "missing_terminals": terminals_missing,
            }

        return {
            "class_name": class_name,
            "status": "measurement_only",
            "spice_support": spice_support,
            "emit_as": class_rule.get("emit_as"),
            "measurement_kind": class_rule.get("measurement_kind", "voltage"),
            "node_order": node_order,
            "nodes": nodes,
            "parameters": value_data,
            "reason": class_rule.get("reason", "Measurement point only; not emitted as a physical component."),
        }

    if spice_support in DEFERRED_SUPPORT:
        return {
            "class_name": class_name,
            "status": spice_support,
            "spice_support": spice_support,
            "reason": class_rule.get("reason", "Conversion deferred to a later step."),
        }

    if spice_support not in READY_SUPPORT:
        return {
            "class_name": class_name,
            "status": "unsupported_for_now",
            "spice_support": spice_support,
            "reason": "Unrecognized SPICE support strategy.",
        }

    if value_status == "missing":
        return {
            "class_name": class_name,
            "status": "missing_parameters",
            "spice_support": spice_support,
            "missing_fields": as_list(class_rule.get("required_fields")),
        }

    required_fields = [str(field) for field in as_list(class_rule.get("required_fields"))]
    fields_missing = missing_fields(value_data, required_fields)
    if fields_missing:
        return {
            "class_name": class_name,
            "status": "missing_parameters",
            "spice_support": spice_support,
            "missing_fields": fields_missing,
        }

    node_order = [str(node) for node in as_list(class_rule.get("node_order"))]
    nodes, terminals_missing = ordered_nodes(terminal_nodes, node_order)
    if terminals_missing:
        return {
            "class_name": class_name,
            "status": "invalid_node_order",
            "spice_support": spice_support,
            "missing_terminals": terminals_missing,
        }

    entry = {
        "class_name": class_name,
        "status": "spice_ready",
        "spice_support": spice_support,
        "spice_prefix": class_rule.get("spice_prefix"),
        "emit_as": class_rule.get("emit_as"),
        "node_order": node_order,
        "nodes": nodes,
        "parameters": value_data,
    }

    if spice_support == "simplified":
        strategies = class_rule.get("strategies") or {}
        state = str(value_data.get("state", "")).lower()
        entry["strategy"] = strategies.get(state)
        if entry["strategy"] is None:
            entry["status"] = "missing_parameters"
            entry["missing_fields"] = ["valid_state"]

    return entry


def build_component_rules(
    values_bound: dict[str, Any],
    spice_classes: dict[str, Any],
    spice_classes_source: str | Path | None = None,
) -> dict[str, Any]:
    """
    Costruisce il layer 06 della pipeline.

    Input principale: output dello step 04. Output: decisioni semplici per lo
    step 07, senza ancora scrivere la netlist SPICE.
    """
    component_rules: dict[str, Any] = {}
    stats = {
        "components_total": 0,
        "spice_ready_components": 0,
        "not_emitted_components": 0,
        "measurement_components": 0,
        "missing_components": 0,
        "unsupported_components": 0,
        "pin_aware_components": 0,
        "invalid_components": 0,
        "supplies_ready_count": 0,
    }

    for component_id, component_data in (values_bound.get("components") or {}).items():
        if not isinstance(component_data, dict):
            continue

        class_name = str(component_data.get("class_name", ""))
        class_rule = spice_classes.get(class_name)
        rule_entry = classify_component_rule(str(component_id), component_data, class_rule)
        component_rules[str(component_id)] = rule_entry

        stats["components_total"] += 1
        status = rule_entry.get("status")
        if status == "spice_ready":
            stats["spice_ready_components"] += 1
        elif status == "not_emitted":
            stats["not_emitted_components"] += 1
        elif status == "measurement_only":
            stats["measurement_components"] += 1
        elif status == "missing_parameters":
            stats["missing_components"] += 1
        elif status == "pin_aware":
            stats["pin_aware_components"] += 1
        elif status in ("unsupported_for_now",):
            stats["unsupported_components"] += 1
        elif status == "invalid_node_order":
            stats["invalid_components"] += 1

    supply_rules = build_supply_rules(values_bound)
    stats["supplies_ready_count"] = sum(
        1 for supply in supply_rules.values() if supply.get("status") == "spice_ready"
    )

    return {
        "circuit_id": values_bound.get("circuit_id"),
        "source_format": "pipeline2.0_component_rules",
        "values_source": values_bound.get("values_source"),
        "spice_classes_source": str(spice_classes_source) if spice_classes_source else None,
        "supplies": supply_rules,
        "components": dict(sorted(component_rules.items())),
        "simulation": values_bound.get("simulation") or {},
        "stats": stats,
    }
