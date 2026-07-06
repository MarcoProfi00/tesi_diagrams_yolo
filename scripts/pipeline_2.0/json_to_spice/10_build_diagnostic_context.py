"""
Costruzione del manifest diagnostico per l'agente.

Questo modulo crea un file leggero che indica all'agente dove trovare gli
output reali della Pipeline 2.0.

Lo step 10 non duplica Graph JSON, node map, netlist, stdout o stderr dentro un
unico file enorme. Mantiene invece una mappa ordinata dei file prodotti dagli
step 01-08, con un piccolo riepilogo tecnico e alcune regole operative.

Responsabilita:

- elencare gli artefatti disponibili e mancanti;
- indicare il ruolo di ogni file nella diagnosi;
- salvare uno stato minimo di SPICE e della netlist;
- dichiarare la policy sull'immagine originale;
- indicizzare gli scenari gia eseguiti, se presenti;
- dichiarare il budget massimo di scenari per il circuito;
- preparare un manifest semplice per lo step 11/agente read-only.

L'output principale e 10_diagnostic_context.json.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MAX_EXECUTABLE_SCENARIOS = 5


ARTIFACTS = {
    "graph": {
        "step": "01",
        "filename": "01_graph.json",
        "role": "Graph JSON copied from Pipeline 1.0.",
    },
    "normalized_circuit": {
        "step": "02",
        "filename": "02_normalized_circuit.json",
        "role": "Normalized circuit representation used by Pipeline 2.0.",
    },
    "node_map": {
        "step": "03",
        "filename": "03_node_map.json",
        "role": "Maps component terminals to SPICE node names.",
    },
    "values_bound": {
        "step": "04",
        "filename": "04_values_bound.json",
        "role": "Values and labels bound to graph components.",
    },
    "component_rules": {
        "step": "06",
        "filename": "06_component_rules.json",
        "role": "SPICE conversion rules for each component.",
    },
    "netlist": {
        "step": "07",
        "filename": "07_netlist.cir",
        "role": "Generated SPICE netlist.",
    },
    "spice_emit_report": {
        "step": "07",
        "filename": "07_spice_emit_report.json",
        "role": "Report of emitted, skipped and warning components.",
    },
    "spice_run": {
        "step": "08",
        "filename": "08_spice_run.json",
        "role": "Structured ngspice execution report.",
    },
    "ngspice_stdout": {
        "step": "08",
        "filename": "08_ngspice_stdout.txt",
        "role": "Raw ngspice stdout log.",
    },
    "ngspice_stderr": {
        "step": "08",
        "filename": "08_ngspice_stderr.txt",
        "role": "Raw ngspice stderr log.",
    },
    "tran_csv": {
        "step": "08",
        "filename": "08_tran.csv",
        "role": "Clean transient CSV, when .tran data is available.",
    },
    "tran_plot_png": {
        "step": "08",
        "filename": "08_tran_plot.png",
        "role": "Transient plot PNG, when generated.",
    },
    "tran_plot_svg": {
        "step": "08",
        "filename": "08_tran_plot.svg",
        "role": "Transient plot SVG fallback, when generated.",
    },
}

SCENARIO_ARTIFACTS = {
    "scenario_definition": {
        "filename": "scenario.json",
        "role": "Scenario selected by the user and saved before execution.",
    },
    "scenario_status": {
        "filename": "scenario_status.json",
        "role": "Current scenario status, SPICE status and diagnostic outcome.",
    },
    "controlled_scenario_report": {
        "filename": "12_controlled_scenarios.json",
        "role": "Report produced by the controlled scenario runner.",
    },
    "scenario_comparison": {
        "filename": "scenario_comparison.json",
        "role": "Base-vs-scenario comparison used to evaluate the scenario.",
    },
}


def read_json_safe(path: Path) -> dict[str, Any]:
    """Legge un JSON se esiste e se e valido, altrimenti restituisce {}."""
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def relative_or_absolute(path: Path, project_root: Path | None = None) -> str:
    """Restituisce un path relativo al progetto quando possibile."""
    if project_root is None:
        return str(path)
    try:
        return str(path.relative_to(project_root))
    except ValueError:
        return str(path)


def build_artifact_manifest(
    output_dir: Path,
    project_root: Path | None = None,
) -> dict[str, Any]:
    """Crea la lista degli artefatti disponibili per il circuito."""
    artifacts: dict[str, Any] = {}

    for key, metadata in ARTIFACTS.items():
        path = output_dir / str(metadata["filename"])
        artifacts[key] = {
            "step": metadata["step"],
            "available": path.exists(),
            "path": relative_or_absolute(path, project_root) if path.exists() else None,
            "role": metadata["role"],
        }

    return artifacts


def find_image_path(
    project_root: Path | None,
    batch_name: str,
    circuit_id: str,
) -> Path | None:
    """Trova l'immagine originale senza includerla nel manifest."""
    if project_root is None:
        return None

    image_dir = project_root / "data" / batch_name
    for extension in (".jpg", ".jpeg", ".png", ".bmp"):
        candidate = image_dir / f"{circuit_id}{extension}"
        if candidate.exists():
            return candidate
    return None


def build_image_access(
    project_root: Path | None,
    batch_name: str,
    circuit_id: str,
) -> dict[str, Any]:
    """Definisce quando l'agente puo richiedere l'immagine originale."""
    image_path = find_image_path(project_root, batch_name, circuit_id)
    return {
        "included_by_default": False,
        "can_be_requested": image_path is not None,
        "path": relative_or_absolute(image_path, project_root) if image_path else None,
        "policy": (
            "Only request the image if structured outputs suggest that the "
            "Graph JSON may be incomplete or wrong."
        ),
    }


def build_summary(output_dir: Path) -> dict[str, Any]:
    """Estrae un riepilogo minimo senza duplicare i file completi."""
    node_map = read_json_safe(output_dir / "03_node_map.json")
    values_bound = read_json_safe(output_dir / "04_values_bound.json")
    component_rules = read_json_safe(output_dir / "06_component_rules.json")
    emit_report = read_json_safe(output_dir / "07_spice_emit_report.json")
    spice_run = read_json_safe(output_dir / "08_spice_run.json")

    return {
        "spice_status": spice_run.get("status"),
        "spice_exit_code": spice_run.get("exit_code"),
        "spice_message": spice_run.get("message"),
        "emitted_elements": emit_report.get("emitted_elements"),
        "skipped_elements": emit_report.get("skipped_elements"),
        "emit_warnings_count": len(emit_report.get("warnings") or []),
        "skipped_components_count": len(emit_report.get("skipped_components") or []),
        "node_count": (node_map.get("stats") or {}).get("nodes_count"),
        "ground_groups_count": (node_map.get("stats") or {}).get("ground_groups_count"),
        "singleton_nodes_count": (node_map.get("stats") or {}).get("singleton_nodes_count"),
        "bound_components": (values_bound.get("stats") or {}).get("bound_components"),
        "missing_components": (values_bound.get("stats") or {}).get("missing_components"),
        "unsupported_components": (values_bound.get("stats") or {}).get("unsupported_components"),
        "spice_ready_components": (component_rules.get("stats") or {}).get("spice_ready_components"),
        "rules_missing_components": (component_rules.get("stats") or {}).get("missing_components"),
        "has_tran_csv": (output_dir / "08_tran.csv").exists(),
        "has_tran_plot": (output_dir / "08_tran_plot.png").exists() or (output_dir / "08_tran_plot.svg").exists(),
    }


def build_agent_rules() -> list[str]:
    """Regole semplici per lo step 11/agente."""
    return [
        "Treat this file as a manifest, not as the full diagnostic evidence.",
        "Load the referenced artifacts needed for the answer.",
        "Use graph, node map, component rules, netlist, stdout and stderr as evidence.",
        "If executed_scenarios are available, use them as evidence for questions about scenario outcomes.",
        "Do not invent values, connections, models or simulation results.",
        "Do not use the image unless image_access is explicitly requested.",
        "If Graph JSON inconsistency is suspected, explain which structured outputs suggest it.",
        "In read-only mode, do not modify netlists and do not execute scenarios.",
        f"Never exceed {MAX_EXECUTABLE_SCENARIOS} executed scenarios for the same circuit.",
        "When the scenario budget is exhausted, stop proposing new scenarios and provide a final diagnostic conclusion.",
    ]


def build_executed_scenarios(
    output_dir: Path,
    project_root: Path | None = None,
) -> list[dict[str, Any]]:
    """Indicizza gli scenari gia creati/eseguiti per renderli visibili all'agente."""
    scenarios_dir = output_dir / "scenarios"
    if not scenarios_dir.exists() or not scenarios_dir.is_dir():
        return []

    scenarios: list[dict[str, Any]] = []

    for scenario_dir in sorted(path for path in scenarios_dir.iterdir() if path.is_dir()):
        scenario = read_json_safe(scenario_dir / "scenario.json")
        status = read_json_safe(scenario_dir / "scenario_status.json")
        comparison = read_json_safe(scenario_dir / "scenario_comparison.json")
        report = read_json_safe(scenario_dir / "12_controlled_scenarios.json")
        outcome = status.get("diagnostic_outcome") or comparison.get("diagnostic_outcome") or {}
        summary = status.get("comparison_summary") or comparison.get("summary") or {}

        artifacts: dict[str, Any] = {}
        for artifact_name, metadata in SCENARIO_ARTIFACTS.items():
            path = scenario_dir / str(metadata["filename"])
            artifacts[artifact_name] = {
                "available": path.exists(),
                "path": relative_or_absolute(path, project_root) if path.exists() else None,
                "role": metadata["role"],
            }

        scenarios.append(
            {
                "scenario_dir": relative_or_absolute(scenario_dir, project_root),
                "scenario_id": status.get("scenario_id") or scenario.get("scenario_id") or scenario_dir.name,
                "title": scenario.get("title") or status.get("scenario_id") or scenario_dir.name,
                "status": status.get("status") or report.get("status") or "unknown",
                "spice_status": status.get("spice_status") or report.get("spice_status"),
                "diagnostic_outcome": outcome,
                "comparison_summary": summary,
                "artifacts": artifacts,
            }
        )

    return scenarios


def summarize_changed_quantities(comparison: dict[str, Any]) -> dict[str, list[str]]:
    """Riassume le grandezze cambiate e non cambiate in uno scenario."""
    changed: list[str] = []
    unchanged: list[str] = []
    missing: list[str] = []

    for item in comparison.get("quantities") or []:
        if not isinstance(item, dict):
            continue
        quantity = str(item.get("quantity") or "")
        change = item.get("change")
        if change in {"activated", "deactivated", "changed"}:
            changed.append(quantity)
        elif change == "unchanged":
            unchanged.append(quantity)
        elif change == "missing":
            missing.append(quantity)

    return {
        "changed": changed,
        "unchanged": unchanged,
        "missing": missing,
    }


def resolve_manifest_artifact(path_value: str | None, project_root: Path | None) -> Path | None:
    """Risolve un path salvato nel manifest, relativo al progetto quando serve."""
    if not path_value:
        return None
    path = Path(path_value)
    if path.is_absolute():
        return path
    return (project_root / path) if project_root is not None else path


def build_scenario_outcome_summary(
    executed_scenarios: list[dict[str, Any]],
    project_root: Path | None = None,
) -> dict[str, Any]:
    """
    Crea una sintesi semplice per aiutare l'agente a capire quale scenario pesa di piu.

    La decisione resta motivata dagli artefatti scenario, ma questa sintesi evita
    che il modello tratti tutti gli scenari come un semplice elenco equivalente.
    """
    best: dict[str, Any] | None = None
    scenarios: list[dict[str, Any]] = []

    for scenario in executed_scenarios:
        artifacts = scenario.get("artifacts") or {}
        comparison_path = artifacts.get("scenario_comparison", {}).get("path")
        resolved_comparison_path = resolve_manifest_artifact(comparison_path, project_root)
        comparison = read_json_safe(resolved_comparison_path) if resolved_comparison_path else {}
        outcome = scenario.get("diagnostic_outcome") or {}
        comparison_summary = scenario.get("comparison_summary") or {}
        stop_automation = bool(outcome.get("stop_automation"))
        outcome_status = outcome.get("status")

        score = 0
        if stop_automation:
            score += 100
        if outcome_status == "resolved_candidate":
            score += 80
        elif outcome_status == "partially_resolved":
            score += 20
        score += int(comparison_summary.get("changed_count") or 0)

        compact = {
            "scenario_id": scenario.get("scenario_id"),
            "title": scenario.get("title"),
            "status": scenario.get("status"),
            "spice_status": scenario.get("spice_status"),
            "outcome_status": outcome_status,
            "outcome_label": outcome.get("label"),
            "outcome_reason": outcome.get("reason"),
            "stop_automation": stop_automation,
            "comparison_summary": comparison_summary,
            "quantity_summary": summarize_changed_quantities(comparison),
            "score": score,
        }
        scenarios.append(compact)

        if best is None or score > int(best.get("score") or 0):
            best = compact

    return {
        "available": bool(scenarios),
        "best_scenario_id": best.get("scenario_id") if best else None,
        "best_outcome_status": best.get("outcome_status") if best else None,
        "best_stop_automation": best.get("stop_automation") if best else None,
        "interpretation_rule": (
            "If a user asks which scenario resolves the problem, prefer the scenario "
            "with outcome_status='resolved_candidate' and stop_automation=true. "
            "Partially resolved scenarios are supporting diagnostics, not the main solution."
        ),
        "scenarios": scenarios,
    }


def build_scenario_budget(executed_scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    """Costruisce una politica semplice sul numero massimo di scenari eseguibili."""
    executed_count = len(executed_scenarios)
    remaining = max(0, MAX_EXECUTABLE_SCENARIOS - executed_count)
    return {
        "max_executable_scenarios": MAX_EXECUTABLE_SCENARIOS,
        "executed_scenarios_count": executed_count,
        "remaining_executable_scenarios": remaining,
        "budget_exhausted": remaining == 0,
        "last_scenario_available": remaining == 1,
        "policy": (
            "At most 5 scenarios can be executed for the same circuit. "
            "When only one scenario remains, the agent should propose a single final scenario. "
            "When no scenario remains, the agent must stop proposing new scenarios and provide a final diagnostic conclusion."
        ),
    }


def build_diagnostic_context(
    output_dir: str | Path,
    batch_name: str,
    circuit_id: str,
    project_root: str | Path | None = None,
    user_problem: str | None = None,
    experiment_name: str | None = None,
) -> dict[str, Any]:
    """
    Costruisce il manifest diagnostico leggero.

    Il manifest indica dove sono gli output veri. Lo step 11 decidera quali file
    caricare per costruire il prompt dell'agente.
    """
    circuit_dir = Path(output_dir)
    root = Path(project_root) if project_root is not None else None

    executed_scenarios = build_executed_scenarios(circuit_dir, root)

    return {
        "source_format": "pipeline2.0_diagnostic_context_manifest",
        "batch_name": batch_name,
        "experiment_name": experiment_name,
        "circuit_id": circuit_id,
        "user_problem": user_problem,
        "pipeline2_output_dir": relative_or_absolute(circuit_dir, root),
        "summary": build_summary(circuit_dir),
        "artifacts": build_artifact_manifest(circuit_dir, root),
        "executed_scenarios": executed_scenarios,
        "scenario_outcome_summary": build_scenario_outcome_summary(executed_scenarios, root),
        "scenario_budget": build_scenario_budget(executed_scenarios),
        "image_access": build_image_access(root, batch_name, circuit_id),
        "agent_mode": "graph_grounded_readonly",
        "agent_rules": build_agent_rules(),
    }
