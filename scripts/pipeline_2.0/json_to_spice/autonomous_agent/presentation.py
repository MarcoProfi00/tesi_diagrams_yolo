"""Prepara il contratto di presentazione della modalita AGENT.

Il modulo traduce lo stato tecnico del controller e gli artefatti delle run in
dati stabili per il frontend. Non prende decisioni diagnostiche e non modifica
gli output della pipeline.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


VIEW_VERSION = "pipeline2.0_agent_view_v1"
MAX_VISIBLE_EVIDENCE = 4

STATUS_PRESENTATION = {
    "idle": ("Pronto", "neutral"),
    "running": ("In esecuzione", "running"),
    "completed": ("Completata", "success"),
    "stopped": ("Interrotta", "warning"),
    "error": ("Errore", "danger"),
}

FINAL_STATUS_PRESENTATION = {
    "resolved": ("Risolta", "success"),
    "localized": ("Causa localizzata", "success"),
    "partially_localized": ("Parzialmente localizzata", "warning"),
    "topology_issue": ("Problema topologico", "warning"),
    "inconclusive": ("Non conclusiva", "neutral"),
}

ACTION_LABELS = {
    "drive_node_voltage": "Forza tensione sul nodo",
    "set_initial_node_voltage": "Imposta tensione iniziale del nodo",
    "change_source_value": "Modifica valore della sorgente",
    "change_component_value": "Modifica valore del componente",
    "close_switch": "Chiude lo switch",
    "connect_nodes": "Collega due nodi",
    "feed_nodes_from_source_node": "Alimenta nodi da una sorgente esistente",
    "add_voltage_source_between_nodes": "Aggiunge una sorgente di tensione",
    "add_resistor_between_nodes": "Aggiunge una resistenza",
}

EXPECTATION_LABELS = {
    "activated": "attivazione",
    "deactivated": "disattivazione",
    "changed": "variazione",
    "unchanged": "valore invariato",
    "increased": "aumento",
    "decreased": "riduzione",
    "magnitude_increased": "aumento in valore assoluto",
    "magnitude_decreased": "riduzione in valore assoluto",
    "nonzero": "valore non nullo",
}


def read_json_object(path: Path) -> dict[str, Any]:
    """Legge un oggetto JSON senza propagare errori di file o formato."""
    if not path.exists() or not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def resolve_scenario_dir(
    output_dir: Path | None,
    result: dict[str, Any],
    scenario_id: str,
) -> Path | None:
    """Individua la cartella scenario usando prima la root nota della sessione."""
    if output_dir is not None:
        candidate = output_dir / "scenarios" / scenario_id
        if candidate.exists() and candidate.is_dir():
            return candidate

    raw_path = str(result.get("scenario_dir") or "").strip()
    if not raw_path:
        return None
    candidate = Path(raw_path)
    return candidate if candidate.exists() and candidate.is_dir() else None


def engineering_unit(quantity: str, metric: str) -> str:
    """Deduce l'unita elettrica dalla grandezza richiesta nel confronto."""
    normalized = f"{quantity} {metric}".strip().lower()
    if normalized.startswith("v(") or " v(" in normalized:
        return "V"
    if normalized.startswith("i(") or " i(" in normalized:
        return "A"
    if normalized.startswith("p(") or " p(" in normalized:
        return "W"
    return ""


def format_engineering_value(value: Any, unit: str = "") -> str:
    """Formatta un numero con prefisso ingegneristico mantenendo valori generali."""
    if value is None:
        return "n/d"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)

    absolute = abs(number)
    prefixes = (
        (1e9, "G"),
        (1e6, "M"),
        (1e3, "k"),
        (1.0, ""),
        (1e-3, "m"),
        (1e-6, "u"),
        (1e-9, "n"),
        (1e-12, "p"),
    )
    scale, prefix = 1.0, ""
    if absolute > 0:
        for candidate_scale, candidate_prefix in prefixes:
            if absolute >= candidate_scale:
                scale, prefix = candidate_scale, candidate_prefix
                break
    shown = number / scale
    text = f"{shown:.4g}"
    suffix = f" {prefix}{unit}" if unit else ""
    return text + suffix


def build_evidence_item(item: dict[str, Any]) -> dict[str, Any]:
    """Normalizza una grandezza OP o TRAN per la scheda scenario."""
    quantity = str(item.get("quantity") or item.get("metric") or "Grandezza")
    metric = str(item.get("metric") or quantity)
    unit = engineering_unit(quantity, metric)
    measurement = str(item.get("measurement") or "").strip().lower()
    is_transient = (
        measurement == "tran_vpp"
        or bool(item.get("base_details") or item.get("scenario_details"))
        or ".vpp" in metric.lower()
    )
    expectation = str(item.get("expectation") or "").strip().lower()
    return {
        "quantity": quantity,
        "metric": metric,
        "measurement": measurement or ("tran_vpp" if is_transient else "op"),
        "analysis": "tran" if is_transient else "op",
        "base_value": item.get("base_value"),
        "scenario_value": item.get("scenario_value"),
        "delta": item.get("delta"),
        "base_display": format_engineering_value(item.get("base_value"), unit),
        "scenario_display": format_engineering_value(item.get("scenario_value"), unit),
        "delta_display": format_engineering_value(item.get("delta"), unit),
        "change": str(item.get("change") or "unknown"),
        "expectation": expectation,
        "expectation_label": EXPECTATION_LABELS.get(expectation, expectation),
        "expectation_met": item.get("expectation_met"),
    }


def evidence_priority(item: dict[str, Any]) -> tuple[int, str]:
    """Ordina prima attivazioni e cambiamenti, lasciando in fondo gli invariati."""
    if item.get("expectation_met") is False:
        return -1, str(item.get("quantity") or "")
    priority = {
        "activated": 0,
        "changed": 1,
        "deactivated": 2,
        "missing": 3,
        "unchanged": 4,
    }
    return priority.get(str(item.get("change") or ""), 3), str(item.get("quantity") or "")


def build_action_summary(action: dict[str, Any]) -> dict[str, str]:
    """Crea una descrizione breve e verificabile per una primitiva scenario."""
    action_type = str(action.get("type") or "unknown")
    label = ACTION_LABELS.get(action_type, action_type)

    if action_type in {"drive_node_voltage", "set_initial_node_voltage", "change_source_value", "change_component_value"}:
        detail = f"{action.get('target', '?')} = {action.get('value', '?')}"
    elif action_type == "close_switch":
        detail = str(action.get("target") or "?")
    elif action_type in {"connect_nodes", "add_resistor_between_nodes"}:
        detail = f"{action.get('from', '?')} -> {action.get('to', '?')}"
        if action_type == "add_resistor_between_nodes":
            detail += f" ({action.get('value', '?')})"
    elif action_type == "feed_nodes_from_source_node":
        targets = action.get("target_nodes") if isinstance(action.get("target_nodes"), list) else []
        detail = f"{action.get('source_node', '?')} -> {', '.join(map(str, targets)) or '?'}"
    elif action_type == "add_voltage_source_between_nodes":
        detail = (
            f"{action.get('positive', '?')} -> {action.get('negative', '?')} "
            f"({action.get('value', '?')})"
        )
    else:
        detail = ""

    return {"type": action_type, "label": label, "detail": detail}


def scenario_tone(result: dict[str, Any]) -> str:
    """Converte esecuzione SPICE ed esito diagnostico in un tono visivo."""
    if str(result.get("status") or "") == "rejected":
        return "danger"
    if str(result.get("spice_status") or "") not in {"", "success"}:
        return "danger"
    outcome = result.get("diagnostic_outcome")
    outcome_status = str(outcome.get("status") or "") if isinstance(outcome, dict) else ""
    if outcome_status == "resolved_candidate":
        return "success"
    if outcome_status in {"partially_resolved", "topology_issue"}:
        return "warning"
    if result.get("spice_executed"):
        return "success"
    return "neutral"


def build_scenario_view(
    output_dir: Path | None,
    scenario: dict[str, Any],
    result: dict[str, Any],
    fallback_index: int,
) -> dict[str, Any]:
    """Unisce proposta, risultato e confronto in una singola scheda frontend."""
    scenario_id = str(result.get("scenario_id") or scenario.get("scenario_id") or f"scenario_{fallback_index}")
    scenario_dir = resolve_scenario_dir(output_dir, result, scenario_id)
    comparison = read_json_object(scenario_dir / "scenario_comparison.json") if scenario_dir else {}
    raw_quantities = comparison.get("quantities")
    quantities = raw_quantities if isinstance(raw_quantities, list) else []
    evidence = [build_evidence_item(item) for item in quantities if isinstance(item, dict)]
    evidence.sort(key=evidence_priority)

    outcome = result.get("diagnostic_outcome")
    if not isinstance(outcome, dict):
        outcome = comparison.get("diagnostic_outcome")
    if not isinstance(outcome, dict):
        outcome = {}

    actions = scenario.get("actions") if isinstance(scenario.get("actions"), list) else []
    run_dir = scenario_dir / "run" if scenario_dir else None
    viewer_available = bool(
        (run_dir and (run_dir / "15_viewer.svg").exists())
        or (isinstance(result.get("viewer"), dict) and result.get("viewer", {}).get("svg"))
    )
    transient_available = bool(run_dir and (run_dir / "08_tran.csv").exists())

    status = "rejected" if str(result.get("status") or "") == "rejected" else "completed"
    if result.get("spice_executed") and str(result.get("spice_status") or "") == "success":
        status = "spice_success"
    elif result.get("spice_executed"):
        status = "spice_failed"

    return {
        "scenario_id": scenario_id,
        "title": str(scenario.get("title") or f"Test {fallback_index}"),
        "hypothesis": str(scenario.get("hypothesis") or ""),
        "status": status,
        "tone": scenario_tone(result),
        "spice_status": str(result.get("spice_status") or "not_executed"),
        "spice_exit_code": result.get("spice_exit_code"),
        "actions": [build_action_summary(action) for action in actions if isinstance(action, dict)],
        "compare": [str(value) for value in scenario.get("compare") or []],
        "evidence": evidence[:MAX_VISIBLE_EVIDENCE],
        "evidence_count": len(evidence),
        "has_more_evidence": len(evidence) > MAX_VISIBLE_EVIDENCE,
        "has_transient": transient_available or any(item.get("analysis") == "tran" for item in evidence),
        "quality_comparison": comparison.get("quality_comparison"),
        "viewer_available": viewer_available,
        "outcome_status": str(outcome.get("status") or "unknown"),
        "outcome_label": str(outcome.get("label") or "Esito da valutare"),
        "outcome_reason": str(outcome.get("reason") or result.get("error") or ""),
        "next_step": str(outcome.get("next_step") or ""),
        "error": str(result.get("error") or ""),
    }


def build_iteration_view(output_dir: Path | None, iteration: dict[str, Any]) -> dict[str, Any]:
    """Costruisce una voce timeline a partire da una decisione persistita."""
    decision = iteration.get("decision") if isinstance(iteration.get("decision"), dict) else {}
    proposed = decision.get("scenarios") if isinstance(decision.get("scenarios"), list) else []
    results = iteration.get("scenario_results") if isinstance(iteration.get("scenario_results"), list) else []
    scenario_count = max(len(proposed), len(results))
    scenarios: list[dict[str, Any]] = []
    for index in range(scenario_count):
        scenario = proposed[index] if index < len(proposed) and isinstance(proposed[index], dict) else {}
        result = results[index] if index < len(results) and isinstance(results[index], dict) else {}
        scenarios.append(build_scenario_view(output_dir, scenario, result, index + 1))

    return {
        "decision_number": int(iteration.get("decision_number") or 0),
        "decision": str(decision.get("decision") or "unknown"),
        "reason": str(decision.get("reason") or ""),
        "scenarios": scenarios,
    }


def collect_capabilities(output_dir: Path | None, iterations: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Elenca gli strumenti realmente disponibili nella sessione corrente."""
    capabilities: list[dict[str, str]] = [
        {"id": "spice", "label": "SPICE"},
        {"id": "history", "label": "Scenario history"},
    ]
    if output_dir is not None and (output_dir / "07_netlist.cir").exists():
        capabilities.insert(1, {"id": "netlist", "label": "Netlist"})
    if output_dir is not None and (output_dir / "08_ngspice_stdout.txt").exists():
        capabilities.append({"id": "op", "label": "Output .op"})

    has_transient = bool(output_dir is not None and (output_dir / "08_tran.csv").exists())
    has_viewer = bool(output_dir is not None and (output_dir / "15_viewer.svg").exists())
    for iteration in iterations:
        for scenario in iteration.get("scenarios") or []:
            has_transient = has_transient or bool(scenario.get("has_transient"))
            has_viewer = has_viewer or bool(scenario.get("viewer_available"))
    if has_transient:
        capabilities.append({"id": "tran", "label": "Output .tran"})
    if has_viewer:
        capabilities.append({"id": "viewer", "label": "Viewer"})
    return capabilities


def build_progress_steps(status: str, decisions: int, scenarios: int) -> list[dict[str, str]]:
    """Deriva un piano leggibile dai contatori reali della sessione."""
    return [
        {"label": "Analisi della base run", "status": "completed" if decisions else "active"},
        {
            "label": "Formulazione delle ipotesi",
            "status": "completed" if decisions else ("active" if status == "running" else "waiting"),
        },
        {
            "label": "Esecuzione degli scenari",
            "status": "completed" if scenarios else ("active" if decisions and status == "running" else "waiting"),
        },
        {
            "label": "Confronto delle evidenze",
            "status": "completed" if scenarios else "waiting",
        },
        {
            "label": "Conclusione diagnostica",
            "status": "completed" if status == "completed" else "waiting",
        },
    ]


def latest_diagnostic_reason(state: dict[str, Any], iterations: list[dict[str, Any]]) -> str:
    """Seleziona la valutazione piu recente senza generare nuovo testo AI."""
    if state.get("final_reason"):
        return str(state.get("final_reason"))
    for iteration in reversed(iterations):
        if iteration.get("reason"):
            return str(iteration.get("reason"))
    return "In attesa della prima analisi del circuito."


def build_final_view(state: dict[str, Any], iterations: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Prepara la conclusione separando stato, risposta e prove disponibili."""
    if str(state.get("status") or "") != "completed":
        return None
    final_status = str(state.get("final_status") or "inconclusive")
    label, tone = FINAL_STATUS_PRESENTATION.get(final_status, (final_status, "neutral"))

    evidence: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for iteration in reversed(iterations):
        for scenario in reversed(iteration.get("scenarios") or []):
            for item in scenario.get("evidence") or []:
                key = (
                    str(item.get("quantity") or ""),
                    str(item.get("base_display") or ""),
                    str(item.get("scenario_display") or ""),
                )
                if key in seen or str(item.get("change") or "") == "unchanged":
                    continue
                seen.add(key)
                evidence.append(item)
                if len(evidence) >= MAX_VISIBLE_EVIDENCE:
                    break
            if len(evidence) >= MAX_VISIBLE_EVIDENCE:
                break
        if len(evidence) >= MAX_VISIBLE_EVIDENCE:
            break

    successful_runs = [
        scenario
        for iteration in iterations
        for scenario in iteration.get("scenarios") or []
        if scenario.get("status") == "spice_success"
    ]
    last_run = successful_runs[-1].get("scenario_id") if successful_runs else "base"
    return {
        "status": final_status,
        "label": label,
        "tone": tone,
        "answer": str(state.get("final_answer") or "Diagnosi autonoma completata."),
        "cause": str(state.get("final_cause") or ""),
        "verified_correction": str(state.get("verified_correction") or ""),
        "reason": str(state.get("final_reason") or ""),
        "evidence": evidence,
        "last_run": str(last_run),
    }


def build_agent_view(state: dict[str, Any], output_dir: Path | None = None) -> dict[str, Any]:
    """Costruisce il contratto completo e generale consumato dal frontend AGENT."""
    status = str(state.get("status") or "idle")
    status_label, status_tone = STATUS_PRESENTATION.get(status, (status, "neutral"))
    raw_iterations = state.get("iterations") if isinstance(state.get("iterations"), list) else []
    iterations = [
        build_iteration_view(output_dir, item)
        for item in raw_iterations
        if isinstance(item, dict)
    ]
    visible_iterations = [item for item in iterations if item.get("scenarios")]
    decisions = int(state.get("agent_decisions_count") or 0)
    scenarios = int(state.get("executed_scenarios_count") or 0)

    return {
        "source_format": VIEW_VERSION,
        "status": status,
        "status_label": status_label,
        "status_tone": status_tone,
        "symptom": str(state.get("symptom") or ""),
        "model": str(state.get("model") or ""),
        "active_run": str(state.get("last_active_run") or "base"),
        "counters": {
            "decisions": decisions,
            "max_decisions": int(state.get("max_agent_decisions") or 8),
            "scenarios": scenarios,
            "max_scenarios": int(state.get("max_executable_scenarios") or 5),
        },
        "steps": build_progress_steps(status, decisions, scenarios),
        "capabilities": collect_capabilities(output_dir, iterations),
        "current_diagnosis": latest_diagnostic_reason(state, iterations),
        "iterations": visible_iterations,
        "final": build_final_view(state, iterations),
        "stop_reason": state.get("stop_reason"),
        "last_error": str(state.get("last_error") or ""),
    }
