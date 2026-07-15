"""Controller a singola iterazione per l'agente autonomo di Experiment 4."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import threading
from typing import Any, Callable

from agent_readonly.openai_runner import call_openai, load_default_env_files
from scenario_runtime import (
    ScenarioRuntimeError,
    count_executed_scenarios,
    execute_scenario,
    next_scenario_id,
)

from .contracts import ALLOWED_ACTION_TYPES, AutonomousDecisionError, parse_and_validate_decision
from .prompt_builder import build_autonomous_prompt, write_autonomous_prompt
from .state_store import (
    MAX_AGENT_DECISIONS,
    MAX_EXECUTABLE_SCENARIOS,
    clear_state,
    create_state,
    read_state,
    stop_state,
    write_state,
)


STEP10_PATH = Path(__file__).resolve().parents[1] / "10_build_diagnostic_context.py"
PROJECT_ROOT = Path(__file__).resolve().parents[4]
DecisionProvider = Callable[[str, str], str]
_CONTROLLER_LOCK = threading.Lock()


class AutonomousControllerError(RuntimeError):
    """Rappresenta un errore controllato del ciclo autonomo."""


def load_step10_module() -> Any:
    """Carica lo step 10 per rigenerare il contesto dopo ogni scenario."""
    spec = importlib.util.spec_from_file_location("pipeline2_step10_autonomous", STEP10_PATH)
    if spec is None or spec.loader is None:
        raise AutonomousControllerError(f"Impossibile caricare lo step 10: {STEP10_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def refresh_diagnostic_context(
    output_dir: Path,
    batch: str,
    circuit: str,
    experiment: str,
    symptom: str,
) -> Path:
    """Rigenera e salva il manifest diagnostico della modalità AGENT."""
    step10 = load_step10_module()
    context = step10.build_diagnostic_context(
        output_dir=output_dir,
        batch_name=batch,
        circuit_id=circuit,
        project_root=PROJECT_ROOT,
        user_problem=symptom,
        experiment_name=experiment,
    )
    path = output_dir / "10_diagnostic_context.json"
    path.write_text(json.dumps(context, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def default_decision_provider(prompt: str, model: str) -> str:
    """Chiama OpenAI usando il runner già configurato dalla Pipeline 2.0."""
    load_default_env_files()
    return call_openai(prompt=prompt, model=model)


def write_raw_response(output_dir: Path, response_text: str, decision_number: int, attempt: int) -> Path:
    """Salva la risposta grezza del modello per audit e debug."""
    path = output_dir / "experiment_chat" / (
        f"autonomous_response_{decision_number}_attempt_{attempt}.txt"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(response_text.rstrip() + "\n", encoding="utf-8")
    return path


def request_valid_decision(
    output_dir: Path,
    prompt: str,
    model: str,
    decision_number: int,
    remaining_budget: int,
    provider: DecisionProvider,
) -> tuple[dict[str, Any], list[str]]:
    """Richiede una decisione e consente un solo tentativo di correzione JSON."""
    response_paths: list[str] = []
    current_prompt = prompt
    last_error: Exception | None = None

    for attempt in (1, 2):
        response_text = provider(current_prompt, model)
        response_path = write_raw_response(output_dir, response_text, decision_number, attempt)
        response_paths.append(str(response_path))
        try:
            return parse_and_validate_decision(response_text, remaining_budget), response_paths
        except AutonomousDecisionError as exc:
            last_error = exc
            if attempt == 1:
                current_prompt = (
                    prompt
                    + "\n\nLa risposta precedente non rispettava il contratto: "
                    + str(exc)
                    + "\nRestituisci ora soltanto un oggetto JSON valido."
                )

    raise AutonomousControllerError(f"Decisione non valida dopo un retry: {last_error}")


def start_diagnosis(output_dir: Path, symptom: str, model: str) -> dict[str, Any]:
    """Inizializza un nuovo ciclo autonomo nel solo workspace AGENT."""
    clean_symptom = symptom.strip()
    if not clean_symptom:
        raise AutonomousControllerError("Il sintomo iniziale non puo essere vuoto")
    existing = read_state(output_dir)
    if existing.get("status") == "running":
        raise AutonomousControllerError("Esiste gia una diagnosi autonoma in corso")
    if count_executed_scenarios(output_dir) > 0:
        raise AutonomousControllerError(
            "Il workspace contiene scenari precedenti: usa Pulisci prima di una nuova diagnosi"
        )
    return create_state(output_dir, clean_symptom, model)


def complete_with_guardrail(
    output_dir: Path,
    state: dict[str, Any],
    reason: str,
) -> dict[str, Any]:
    """Chiude in modo prudente un ciclo che ha raggiunto un limite tecnico."""
    state["status"] = "completed"
    state["final_status"] = "inconclusive"
    state["final_reason"] = reason
    state["final_answer"] = (
        "Il ciclo autonomo si e fermato per un limite di sicurezza. "
        "Le evidenze raccolte restano disponibili, ma non consentono una conclusione affidabile."
    )
    state["stop_reason"] = reason
    write_state(output_dir, state)
    return state


def run_iteration(
    output_dir: Path,
    batch: str,
    circuit: str,
    experiment: str,
    ngspice_executable: str | None,
    provider: DecisionProvider | None = None,
) -> dict[str, Any]:
    """Esegue una sola decisione autonoma e persiste immediatamente l'esito."""
    with _CONTROLLER_LOCK:
        state = read_state(output_dir)
        if not state:
            raise AutonomousControllerError("Nessuna diagnosi autonoma avviata")
        if state.get("status") != "running":
            return state

        decision_count = int(state.get("agent_decisions_count") or 0)
        if decision_count >= MAX_AGENT_DECISIONS:
            return complete_with_guardrail(output_dir, state, "max_agent_decisions")

        executed_count = count_executed_scenarios(output_dir)
        remaining_budget = max(0, MAX_EXECUTABLE_SCENARIOS - executed_count)
        state["executed_scenarios_count"] = executed_count

        refresh_diagnostic_context(
            output_dir,
            batch,
            circuit,
            experiment,
            str(state.get("symptom") or ""),
        )
        decision_number = decision_count + 1
        prompt = build_autonomous_prompt(output_dir, state, remaining_budget)
        prompt_path = write_autonomous_prompt(output_dir, prompt, decision_number)

        try:
            decision, response_paths = request_valid_decision(
                output_dir=output_dir,
                prompt=prompt,
                model=str(state.get("model") or "gpt-5.4"),
                decision_number=decision_number,
                remaining_budget=remaining_budget,
                provider=provider or default_decision_provider,
            )
        except Exception as exc:
            state["status"] = "error"
            state["stop_reason"] = "decision_error"
            state["last_error"] = str(exc)
            write_state(output_dir, state)
            return state

        state["agent_decisions_count"] = decision_number
        iteration: dict[str, Any] = {
            "decision_number": decision_number,
            "decision": decision,
            "prompt_path": str(prompt_path),
            "response_paths": response_paths,
            "scenario_results": [],
        }

        if decision["decision"] == "stop":
            state["status"] = "completed"
            state["final_status"] = decision["final_status"]
            state["final_reason"] = decision["reason"]
            state["final_answer"] = decision["final_answer"]
            state["stop_reason"] = "agent_stop"
            state.setdefault("iterations", []).append(iteration)
            write_state(output_dir, state)
            return state

        for scenario in decision["scenarios"]:
            payload = dict(scenario)
            payload["scenario_id"] = next_scenario_id(output_dir)
            try:
                result = execute_scenario(
                    output_dir=output_dir,
                    scenario=payload,
                    ngspice_executable=ngspice_executable,
                    allowed_action_types=ALLOWED_ACTION_TYPES,
                    source_label="experiment4_autonomous_agent",
                    reject_duplicates=True,
                )
            except ScenarioRuntimeError as exc:
                result = {
                    "scenario_id": payload["scenario_id"],
                    "status": "rejected",
                    "error": str(exc),
                    "spice_executed": False,
                }
            iteration["scenario_results"].append(result)
            if result.get("spice_executed"):
                state["last_active_run"] = result.get("scenario_id")

        state.setdefault("iterations", []).append(iteration)
        state["executed_scenarios_count"] = count_executed_scenarios(output_dir)
        write_state(output_dir, state)
        return state


def stop_diagnosis(output_dir: Path) -> dict[str, Any]:
    """Espone l'arresto manuale del ciclo autonomo."""
    with _CONTROLLER_LOCK:
        return stop_state(output_dir, "user_stop")


def clear_diagnosis(output_dir: Path) -> bool:
    """Rimuove lo stato autonomo quando viene pulita la sessione AGENT."""
    with _CONTROLLER_LOCK:
        return clear_state(output_dir)


def summarize_state(state: dict[str, Any]) -> dict[str, Any]:
    """Riduce lo stato ai campi necessari al frontend della web chat."""
    status = str(state.get("status") or "idle")
    iterations = state.get("iterations") if isinstance(state.get("iterations"), list) else []
    last_results: list[dict[str, Any]] = []
    if iterations and isinstance(iterations[-1], dict):
        candidate = iterations[-1].get("scenario_results")
        if isinstance(candidate, list):
            last_results = candidate

    if status == "completed":
        reply = str(state.get("final_answer") or "Diagnosi autonoma completata.")
    elif status == "error":
        reply = f"Il ciclo autonomo si e fermato per errore: {state.get('last_error')}"
    elif status == "stopped":
        reply = "Il ciclo autonomo e stato fermato dall'utente."
    else:
        executed_ids = [
            str(item.get("scenario_id"))
            for item in last_results
            if isinstance(item, dict) and item.get("spice_executed")
        ]
        rejected = [
            str(item.get("error"))
            for item in last_results
            if isinstance(item, dict) and item.get("status") == "rejected"
        ]
        reply = "Iterazione completata."
        if executed_ids:
            reply += " Scenari eseguiti: " + ", ".join(executed_ids) + "."
        if rejected:
            reply += " Scenari rifiutati: " + "; ".join(rejected) + "."
        reply += " L'agente puo ora analizzare le nuove evidenze."

    return {
        "status": status,
        "continue": status == "running",
        "reply": reply,
        "executed_scenarios_count": int(state.get("executed_scenarios_count") or 0),
        "max_executable_scenarios": MAX_EXECUTABLE_SCENARIOS,
        "agent_decisions_count": int(state.get("agent_decisions_count") or 0),
        "last_active_run": str(state.get("last_active_run") or "base"),
        "last_scenario_results": last_results,
        "final_status": state.get("final_status"),
        "final_reason": state.get("final_reason"),
        "stop_reason": state.get("stop_reason"),
    }
