"""Crea i riepiloghi CHAT e AGENT di un circuito già completato.

Lo script non contiene dati specifici dei circuiti e non interpreta i risultati:
estrae soltanto gli artefatti prodotti dalla pipeline unificata e li raccoglie
in due JSON facili da fornire al judge.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]
DEFAULT_OUTPUT_DIR = SCRIPT_DIR / "evaluation"
MAX_COMPARISON_SEQUENCE_ITEMS = 64
COMPARISON_ADMIN_FIELDS = {
    "source_format",
    "scenario_id",
    "scenario_title",
    "scenario_intent",
    "base_output_dir",
    "scenario_run_dir",
    "base_stdout",
    "scenario_stdout",
    "base_stderr",
    "scenario_stderr",
    "quantities",
    "summary",
    "diagnostic_outcome",
    "created_or_updated_at",
}


def read_json(path: Path, *, required: bool = True) -> Any:
    if not path.is_file():
        if required:
            raise FileNotFoundError(f"File richiesto non trovato: {path}")
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_text(path: Path, *, required: bool = True) -> str | None:
    if not path.is_file():
        if required:
            raise FileNotFoundError(f"File richiesto non trovato: {path}")
        return None
    return path.read_text(encoding="utf-8", errors="replace")


def project_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(resolved)


def resolve_workspace(value: str) -> Path:
    supplied = Path(value)
    candidates = [
        supplied if supplied.is_absolute() else PROJECT_ROOT / supplied,
        PROJECT_ROOT / "outputs" / "demo_workspaces" / value,
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate.resolve()
    raise FileNotFoundError(
        "Workspace non trovato. Percorsi controllati: "
        + ", ".join(str(path) for path in candidates)
    )


def resolve_output_dir(value: str | None) -> Path:
    if value is None:
        return DEFAULT_OUTPUT_DIR
    supplied = Path(value)
    return supplied if supplied.is_absolute() else PROJECT_ROOT / supplied


def compact_turn(turn: dict[str, Any]) -> dict[str, Any]:
    return {
        "turn_id": turn.get("turn_id"),
        "timestamp": turn.get("timestamp"),
        "role": turn.get("role"),
        "content": turn.get("content"),
        "model": turn.get("model"),
        "selected_run": turn.get("selected_run"),
        "used_image": turn.get("used_image"),
        "scenario_id": turn.get("scenario_id"),
        "scenario_outcome": turn.get("scenario_outcome"),
    }


def compact_comparison_value(value: Any) -> Any:
    """Mantiene le prove strutturate senza copiare sequenze temporali enormi."""
    if isinstance(value, dict):
        return {
            str(key): compact_comparison_value(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        if len(value) > MAX_COMPARISON_SEQUENCE_ITEMS:
            return {
                "sequence_omitted": True,
                "item_count": len(value),
            }
        return [compact_comparison_value(item) for item in value]
    return value


def select_comparison_evidence(comparison: dict[str, Any] | None) -> dict[str, Any]:
    """Seleziona dinamicamente le prove aggiuntive prodotte dal confronto."""
    if not isinstance(comparison, dict):
        return {}
    return {
        key: compact_comparison_value(value)
        for key, value in comparison.items()
        if key not in COMPARISON_ADMIN_FIELDS and value is not None
    }


def select_led_profiles(scenario_dir: Path | None) -> dict[str, Any]:
    """Raccoglie i profili temporali di tutti i LED dello scenario."""
    if scenario_dir is None:
        return {}
    viewer = read_json(
        scenario_dir / "run" / "13_viewer_model.json",
        required=False,
    )
    if not isinstance(viewer, dict):
        return {}
    profiles = ((viewer.get("transient") or {}).get("led_profiles") or {})
    if not isinstance(profiles, dict):
        return {}
    return {
        str(component_id): compact_comparison_value(profile)
        for component_id, profile in profiles.items()
        if isinstance(profile, dict)
    }


def base_evidence(run_dir: Path) -> tuple[dict[str, Any], list[str]]:
    json_files = {
        "graph": "01_graph.json",
        "node_map": "03_node_map.json",
        "values_bound": "04_values_bound.json",
        "component_rules": "06_component_rules.json",
        "spice_emit_report": "07_spice_emit_report.json",
        "spice_run": "08_spice_run.json",
        "diagnostic_context": "10_diagnostic_context.json",
    }
    text_files = {
        "netlist": "07_netlist.cir",
        "ngspice_stdout": "08_ngspice_stdout.txt",
        "ngspice_stderr": "08_ngspice_stderr.txt",
    }

    evidence: dict[str, Any] = {}
    sources: list[str] = []

    for key, filename in json_files.items():
        path = run_dir / filename
        evidence[key] = read_json(path)
        sources.append(project_path(path))

    for key, filename in text_files.items():
        path = run_dir / filename
        evidence[key] = read_text(path)
        sources.append(project_path(path))

    return evidence, sources


def scenario_summary(
    definition: dict[str, Any],
    scenario_dir: Path | None,
    registry_status: str | None = None,
) -> tuple[dict[str, Any], list[str]]:
    status: dict[str, Any] | None = None
    comparison: dict[str, Any] | None = None
    sources: list[str] = []

    if scenario_dir is not None:
        definition_path = scenario_dir / "scenario.json"
        status_path = scenario_dir / "scenario_status.json"
        comparison_path = scenario_dir / "scenario_comparison.json"
        viewer_path = scenario_dir / "run" / "13_viewer_model.json"

        saved_definition = read_json(definition_path, required=False)
        if isinstance(saved_definition, dict):
            definition = saved_definition
            sources.append(project_path(definition_path))

        status = read_json(status_path, required=False)
        if status is not None:
            sources.append(project_path(status_path))

        comparison = read_json(comparison_path, required=False)
        if comparison is not None:
            sources.append(project_path(comparison_path))
        if viewer_path.is_file():
            sources.append(project_path(viewer_path))

    return (
        {
            "scenario_id": definition.get("scenario_id"),
            "title": definition.get("title"),
            "hypothesis": definition.get("hypothesis"),
            "intent": definition.get("intent"),
            "actions": definition.get("actions", []),
            "analysis": definition.get("analysis"),
            "compare": definition.get("compare", []),
            "expect": definition.get("expect", {}),
            "registry_status": registry_status,
            "execution": {
                "status": status.get("status") if status else None,
                "spice_executed": status.get("spice_executed") if status else False,
                "spice_status": status.get("spice_status") if status else None,
                "spice_exit_code": status.get("spice_exit_code") if status else None,
                "diagnostic_outcome": (
                    status.get("diagnostic_outcome") if status else None
                ),
                "comparison_summary": (
                    comparison.get("summary") if comparison else None
                ),
                "quantities": comparison.get("quantities", []) if comparison else [],
                "comparison_evidence": select_comparison_evidence(comparison),
                "led_profiles": select_led_profiles(scenario_dir),
            },
        },
        sources,
    )


def chat_scenarios(
    run_dir: Path, registry: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[str]]:
    summaries: list[dict[str, Any]] = []
    sources: list[str] = []

    for entry in registry.get("scenarios", []):
        definition = entry.get("scenario") or entry
        scenario_id = entry.get("scenario_id") or definition.get("scenario_id")
        scenario_dir = run_dir / "scenarios" / str(scenario_id)
        if not scenario_dir.is_dir():
            scenario_dir = None
        summary, scenario_sources = scenario_summary(
            definition,
            scenario_dir,
            registry_status=entry.get("status"),
        )
        summaries.append(summary)
        sources.extend(scenario_sources)

    return summaries, sources


def agent_scenarios(run_dir: Path) -> tuple[list[dict[str, Any]], list[str]]:
    scenarios_dir = run_dir / "scenarios"
    if not scenarios_dir.is_dir():
        return [], []

    summaries: list[dict[str, Any]] = []
    sources: list[str] = []
    for scenario_dir in sorted(path for path in scenarios_dir.iterdir() if path.is_dir()):
        definition_path = scenario_dir / "scenario.json"
        definition = read_json(definition_path, required=False)
        if not isinstance(definition, dict):
            continue
        summary, scenario_sources = scenario_summary(
            definition,
            scenario_dir,
            registry_status="executed",
        )
        summaries.append(summary)
        sources.extend(scenario_sources)

    return summaries, sources


def scenario_metrics(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    executed = [
        scenario
        for scenario in scenarios
        if scenario["execution"].get("spice_executed")
    ]
    successful = [
        scenario
        for scenario in executed
        if scenario["execution"].get("spice_status") == "success"
    ]
    outcomes = [
        scenario["execution"]["diagnostic_outcome"]
        for scenario in executed
        if scenario["execution"].get("diagnostic_outcome")
    ]
    return {
        "scenarios_proposed": len(scenarios),
        "scenarios_executed": len(executed),
        "successful_spice_runs": len(successful),
        "failed_spice_runs": len(executed) - len(successful),
        "resolved_candidate_scenarios": sum(
            outcome.get("status") == "resolved_candidate" for outcome in outcomes
        ),
    }


def build_chat_summary(
    workspace_dir: Path, circuit_id: str
) -> tuple[dict[str, Any], list[str]]:
    run_dir = workspace_dir / "web" / "chat" / circuit_id
    history_path = run_dir / "experiment_chat" / "chat_history.json"
    registry_path = run_dir / "experiment_chat" / "scenario_registry.json"

    history = read_json(history_path)
    registry = read_json(registry_path)
    turns = history.get("turns", [])
    user_turns = [turn for turn in turns if turn.get("role") == "user"]
    assistant_turns = [turn for turn in turns if turn.get("role") == "assistant"]
    initial_symptom = user_turns[0].get("content") if user_turns else None
    final_response = assistant_turns[-1] if assistant_turns else None
    model = next(
        (
            turn.get("model")
            for turn in assistant_turns
            if turn.get("model")
        ),
        None,
    )

    evidence, evidence_sources = base_evidence(run_dir)
    scenarios, scenario_sources = chat_scenarios(run_dir, registry)
    diagnostic_context = evidence.get("diagnostic_context") or {}

    sources = [
        project_path(history_path),
        project_path(registry_path),
        *evidence_sources,
        *scenario_sources,
    ]

    return (
        {
            "source_format": "chat_agent_evaluation_summary",
            "schema_version": 1,
            "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "case": {
                "workspace": workspace_dir.name,
                "circuit_id": circuit_id,
                "batch": history.get("batch_name")
                or diagnostic_context.get("batch_name"),
                "experiment": history.get("experiment_name")
                or diagnostic_context.get("experiment_name"),
                "mode": "chat",
                "symptom": initial_symptom,
            },
            "execution": {
                "model": model,
                "turns_count": len(turns),
                "user_turns_count": len(user_turns),
                "assistant_turns_count": len(assistant_turns),
                **scenario_metrics(scenarios),
            },
            "base_evidence": evidence,
            "conversation": [compact_turn(turn) for turn in turns],
            "scenarios": scenarios,
            "final": {
                "response_turn_id": (
                    final_response.get("turn_id") if final_response else None
                ),
                "response": (
                    final_response.get("content") if final_response else None
                ),
                "best_verified_scenario": diagnostic_context.get(
                    "scenario_outcome_summary"
                ),
            },
            "source_files": sorted(set(sources)),
        },
        sources,
    )


def compact_agent_decision(iteration: dict[str, Any]) -> dict[str, Any]:
    decision = iteration.get("decision") or {}
    return {
        "decision_number": iteration.get("decision_number"),
        "decision": decision.get("decision"),
        "reason": decision.get("reason"),
        "scenarios": decision.get("scenarios", []),
        "final_status": decision.get("final_status"),
        "final_answer": decision.get("final_answer"),
        "final_cause": decision.get("final_cause"),
        "verified_correction": decision.get("verified_correction"),
        "scenario_results": iteration.get("scenario_results", []),
    }


def build_agent_summary(
    workspace_dir: Path, circuit_id: str
) -> tuple[dict[str, Any], list[str]]:
    run_dir = workspace_dir / "web" / "agent" / circuit_id
    state_path = run_dir / "experiment_chat" / "autonomous_diagnosis.json"
    history_path = run_dir / "experiment_chat" / "chat_history.json"

    state = read_json(state_path)
    history = read_json(history_path, required=False) or {}
    evidence, evidence_sources = base_evidence(run_dir)
    scenarios, scenario_sources = agent_scenarios(run_dir)
    diagnostic_context = evidence.get("diagnostic_context") or {}

    sources = [
        project_path(state_path),
        *evidence_sources,
        *scenario_sources,
    ]
    if history_path.is_file():
        sources.append(project_path(history_path))

    return (
        {
            "source_format": "chat_agent_evaluation_summary",
            "schema_version": 1,
            "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "case": {
                "workspace": workspace_dir.name,
                "circuit_id": circuit_id,
                "batch": diagnostic_context.get("batch_name"),
                "experiment": diagnostic_context.get("experiment_name"),
                "mode": "agent",
                "symptom": state.get("symptom"),
            },
            "execution": {
                "model": state.get("model"),
                "status": state.get("status"),
                "agent_decisions_count": state.get("agent_decisions_count"),
                "max_agent_decisions": state.get("max_agent_decisions"),
                "max_executable_scenarios": state.get("max_executable_scenarios"),
                **scenario_metrics(scenarios),
                "stop_reason": state.get("stop_reason"),
            },
            "base_evidence": evidence,
            "decisions": [
                compact_agent_decision(iteration)
                for iteration in state.get("iterations", [])
            ],
            "scenarios": scenarios,
            "final": {
                "status": state.get("final_status"),
                "reason": state.get("final_reason"),
                "answer": state.get("final_answer"),
                "cause": state.get("final_cause"),
                "verified_correction": state.get("verified_correction"),
            },
            "source_files": sorted(set(sources)),
        },
        sources,
    )


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Raccoglie gli artefatti CHAT e AGENT di un circuito in due JSON "
            "pronti per la successiva valutazione."
        )
    )
    parser.add_argument(
        "--workspace",
        required=True,
        help=(
            "Nome del workspace sotto outputs/demo_workspaces oppure percorso "
            "esplicito del workspace."
        ),
    )
    parser.add_argument(
        "--circuit",
        required=True,
        help="Identificativo del circuito già completato in CHAT e AGENT.",
    )
    parser.add_argument(
        "--output-dir",
        help=(
            "Cartella di destinazione. Default: "
            "experiment_ai/chat_agent_evaluation_21/evaluation."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    circuit_id = args.circuit.strip()
    if not circuit_id or Path(circuit_id).name != circuit_id:
        raise ValueError("--circuit deve essere un identificativo semplice.")

    workspace_dir = resolve_workspace(args.workspace)
    output_dir = resolve_output_dir(args.output_dir).resolve() / circuit_id

    chat_summary, _ = build_chat_summary(workspace_dir, circuit_id)
    agent_summary, _ = build_agent_summary(workspace_dir, circuit_id)

    chat_path = output_dir / "chat_summary.json"
    agent_path = output_dir / "agent_summary.json"
    write_json(chat_path, chat_summary)
    write_json(agent_path, agent_summary)

    print(f"CHAT : {chat_path}")
    print(f"AGENT: {agent_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
