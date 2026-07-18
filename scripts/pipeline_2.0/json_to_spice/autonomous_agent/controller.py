"""Controller a singola iterazione per l'agente autonomo di Experiment 4."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
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
from .presentation import build_agent_view
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
# Tre livelli falliti consentono una localizzazione piu robusta del limite di
# trasferimento; una risposta utile interrompe comunque subito lo sweep.
MIN_FAILED_SIGNAL_AMPLITUDES_BEFORE_LOCALIZATION = 3


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


def has_verified_resolution(state: dict[str, Any]) -> bool:
    """Riconosce uno scenario che ha soddisfatto i criteri SPICE dichiarati."""
    for iteration in state.get("iterations") or []:
        if not isinstance(iteration, dict):
            continue
        for result in iteration.get("scenario_results") or []:
            if not isinstance(result, dict):
                continue
            outcome = result.get("diagnostic_outcome") or {}
            if (
                outcome.get("status") == "resolved_candidate"
                and bool(outcome.get("stop_automation"))
            ):
                return True
    return False


def scenario_verifies_joint_objective(
    scenario: dict[str, Any],
    result: dict[str, Any],
) -> bool:
    """Verifica che segnale variabile e componente siano attivi nella stessa run."""
    measurements = scenario.get("measure") or {}
    expectations = scenario.get("expect") or {}
    if not isinstance(measurements, dict) or not isinstance(expectations, dict):
        return False

    positive_effects = {
        "activated",
        "changed",
        "increased",
        "magnitude_increased",
        "nonzero",
    }
    has_variable_signal = any(
        str(measurements.get(quantity) or "").strip().lower() == "tran_vpp"
        and str(expectation or "").strip().lower() in positive_effects
        for quantity, expectation in expectations.items()
    )
    has_direct_component = any(
        re.match(r"^[ip]\s*\(", str(quantity), flags=re.IGNORECASE)
        and str(measurements.get(quantity) or "").strip().lower() == "op"
        and str(expectation or "").strip().lower() in positive_effects
        for quantity, expectation in expectations.items()
    )
    summary = result.get("comparison_summary") or {}
    expectations_met = int(summary.get("expectations_met_count") or 0)
    expectations_failed = int(summary.get("expectations_failed_count") or 0)
    expectations_missing = int(summary.get("expectations_missing_count") or 0)
    return (
        has_variable_signal
        and has_direct_component
        and expectations_met >= 2
        and expectations_failed == 0
        and expectations_missing == 0
    )


def has_verified_joint_objective(state: dict[str, Any]) -> bool:
    """Cerca una singola run che verifichi insieme le due parti dell'obiettivo."""
    for iteration in state.get("iterations") or []:
        if not isinstance(iteration, dict):
            continue
        decision = iteration.get("decision") or {}
        scenarios = decision.get("scenarios") or []
        results = iteration.get("scenario_results") or []
        for scenario, result in zip(scenarios, results):
            if isinstance(scenario, dict) and isinstance(result, dict):
                if scenario_verifies_joint_objective(scenario, result):
                    return True
    return False


def symptom_requests_preservation(symptom: str) -> bool:
    """Rileva se l'obiettivo chiede esplicitamente di preservare un comportamento."""
    normalized = str(symptom or "").strip().lower()
    preservation_patterns = (
        r"\bmanten\w*",
        r"\bpreserv\w*",
        r"\bsenza\s+(?:spegnere|disattivare|alterare|modificare)",
        r"\b(?:resti|resta|rimanga|rimane)\s+(?:acces\w*|attiv\w*|invariat\w*)",
        r"\b(?:keep|maintain|preserve)\w*",
        r"\bremain\w*\s+(?:on|active|unchanged)",
        r"\bwithout\s+(?:turning\s+off|disabling|changing)",
    )
    return any(re.search(pattern, normalized) for pattern in preservation_patterns)


def symptom_requests_correction(symptom: str) -> bool:
    """Rileva se l'utente richiede anche una correzione, non la sola diagnosi."""
    normalized = str(symptom or "").strip().lower()
    correction_patterns = (
        r"\brisol\w*",
        r"\bcorregg\w*",
        r"\bripar\w*",
        r"\bripristin\w*",
        r"\baccend\w*",
        r"\battiv\w*",
        r"\bspegn\w*",
        r"\bdisattiv\w*",
        r"\bfix\w*",
        r"\bcorrect\w*",
        r"\brepair\w*",
        r"\brestore\w*",
        r"\bturn\s+(?:on|off)\b",
    )
    return any(re.search(pattern, normalized) for pattern in correction_patterns)


def symptom_requires_gain_comparison(symptom: str) -> bool:
    """Riconosce obiettivi che richiedono un confronto tra ingresso e uscita."""
    normalized = str(symptom or "").strip().lower()
    gain_patterns = (
        r"\bamplific\w*",
        r"\bguadagn\w*",
        r"\bgain\b",
        r"\bamplification\b",
        r"\btrasfer\w*\s+(?:del\s+)?segnale\b",
        r"\bsegnale\b.*\b(?:arriv\w*|uscita|carico|cuffi\w*)\b",
        r"\b(?:non\s+)?sent\w*\b.*\b(?:cuffi\w*|audio)\b",
        r"\bcuffi\w*\b.*\b(?:mut\w*|segnale|audio)\b",
        r"\bsignal\b.*\b(?:reach\w*|output|load|headset|headphone)\b",
        r"\b(?:headset|headphone)\w*\b.*\b(?:mute|signal|audio)\b",
    )
    return any(re.search(pattern, normalized) for pattern in gain_patterns)


def parse_sine_amplitude(value: Any) -> float | None:
    """Estrae l'ampiezza da una sorgente SIN usando i suffissi SPICE comuni."""
    match = re.match(
        r"(?i)^\s*sin\s*\(\s*[^\s,()]+[\s,]+"
        r"([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?)(meg|[tgkmunpf]?)",
        str(value or ""),
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
    return abs(float(match.group(1)) * multipliers[match.group(2).lower()])


def signal_gain_requires_amplitude_followup(state: dict[str, Any]) -> bool:
    """
    Rileva un trasferimento fallito provato con una sola ampiezza sinusoidale.

    La chiave comprende percorso di ingresso e confronto di guadagno: stimoli
    applicati a nodi diversi non vengono confusi tra loro.
    """
    failed_paths: set[tuple[str, str, str]] = set()
    amplitudes: dict[tuple[str, str, str], set[float]] = {}
    for iteration in state.get("iterations") or []:
        if not isinstance(iteration, dict):
            continue
        scenarios = (iteration.get("decision") or {}).get("scenarios") or []
        results = iteration.get("scenario_results") or []
        for scenario, result in zip(scenarios, results):
            if not isinstance(scenario, dict) or not isinstance(result, dict):
                continue
            if not result.get("spice_executed"):
                continue
            summary = result.get("comparison_summary") or {}
            if not summary.get("gain_required") or summary.get("gain_sufficient"):
                continue
            gain = scenario.get("gain") or {}
            gain_input = str(gain.get("input") or "").strip().lower()
            gain_output = str(gain.get("output") or "").strip().lower()
            for action in scenario.get("actions") or []:
                if not isinstance(action, dict):
                    continue
                action_type = str(action.get("type") or "")
                if action_type == "add_voltage_source_between_nodes":
                    source_path = (
                        f"{str(action.get('positive') or '').strip().upper()}->"
                        f"{str(action.get('negative') or '').strip().upper()}"
                    )
                elif action_type == "drive_node_voltage":
                    source_path = f"{str(action.get('target') or '').strip().upper()}->0"
                else:
                    continue
                amplitude = parse_sine_amplitude(action.get("value"))
                if amplitude is None or amplitude <= 0:
                    continue
                key = (source_path, gain_input, gain_output)
                failed_paths.add(key)
                amplitudes.setdefault(key, set()).add(amplitude)
    return any(
        len(amplitudes.get(path, set())) < MIN_FAILED_SIGNAL_AMPLITUDES_BEFORE_LOCALIZATION
        for path in failed_paths
    )


def symptom_requires_quality_analysis(symptom: str) -> bool:
    """Riconosce sintomi che richiedono una misura esplicita della distorsione."""
    normalized = str(symptom or "").strip().lower()
    quality_patterns = (
        r"\bdistors\w*",
        r"\bclipp\w*",
        r"\bsatur\w*",
        r"\bdeformat\w*",
        r"\bpoco\s+pulit\w*",
        r"\bnon\s+linear\w*",
    )
    return any(re.search(pattern, normalized) for pattern in quality_patterns)


def symptom_requires_variable_signal_measurement(symptom: str) -> bool:
    """Riconosce obiettivi che nominano esplicitamente una misura alternata o VAC."""
    normalized = str(symptom or "").strip().lower()
    variable_signal_patterns = (
        r"\bvac\b",
        r"\bvoltmetro\s+(?:ac|alternat\w*)\b",
        r"\btensione\s+alternat\w*\b",
        r"\bsegnale\s+(?:ac|alternat\w*|sinusoidal\w*)\b",
        r"\balternating\s+(?:voltage|signal)\b",
    )
    return any(re.search(pattern, normalized) for pattern in variable_signal_patterns)


def symptom_requires_direct_component_measurement(symptom: str) -> bool:
    """Rileva obiettivi che chiedono esplicitamente lo stato di LED o lampade."""
    normalized = str(symptom or "").strip().lower()
    component_patterns = (
        r"\bled\b",
        r"\blampad\w*\b",
        r"\blamp\b",
    )
    state_patterns = (
        r"\baccend\w*\b",
        r"\bspen\w*\b",
        r"\battiv\w*\b",
        r"\bdisattiv\w*\b",
        r"\b(?:on|off)\b",
    )
    return (
        any(re.search(pattern, normalized) for pattern in component_patterns)
        and any(re.search(pattern, normalized) for pattern in state_patterns)
    )


def symptom_requires_temporal_expectation(symptom: str) -> bool:
    """Rileva obiettivi che richiedono stato, regolarita o durata nel tempo."""
    normalized = str(symptom or "").strip().lower()
    temporal_patterns = (
        r"\blampegg\w*",
        r"\bblink\w*",
        r"\bduty\s*cycle\b",
        r"\bperiodic\w*",
        r"\bregolar\w*",
        r"\bfinestra\s+di\s+accensione\b",
        r"\bdurata\s+(?:dell'|di\s+)?accensione\b",
    )
    return any(re.search(pattern, normalized) for pattern in temporal_patterns)


def request_valid_decision(
    output_dir: Path,
    prompt: str,
    model: str,
    decision_number: int,
    remaining_budget: int,
    require_first_scenario: bool,
    require_verified_resolution: bool,
    require_verified_correction: bool,
    allow_unchanged_expectations: bool,
    require_gain_comparison: bool,
    require_quality_analysis: bool,
    require_variable_signal_measurement: bool,
    require_direct_component_measurement: bool,
    require_joint_objective_verification: bool,
    require_temporal_expectation: bool,
    require_signal_amplitude_followup: bool,
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
            return parse_and_validate_decision(
                response_text,
                remaining_budget,
                require_first_scenario=require_first_scenario,
                require_verified_resolution=require_verified_resolution,
                require_verified_correction=require_verified_correction,
                allow_unchanged_expectations=allow_unchanged_expectations,
                require_gain_comparison=require_gain_comparison,
                require_quality_analysis=require_quality_analysis,
                require_variable_signal_measurement=require_variable_signal_measurement,
                require_direct_component_measurement=require_direct_component_measurement,
                require_joint_objective_verification=require_joint_objective_verification,
                require_temporal_expectation=require_temporal_expectation,
                require_signal_amplitude_followup=require_signal_amplitude_followup,
            ), response_paths
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
    state["final_cause"] = ""
    state["verified_correction"] = ""
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
        # Experiment 4 richiede una verifica SPICE prima di accettare una diagnosi finale.
        require_first_scenario = executed_count == 0 and remaining_budget > 0
        # Solo lo stato resolved richiede una correzione misurata; una causa puo essere localizzata.
        require_verified_resolution = remaining_budget > 0 and not has_verified_resolution(state)
        # Se l'utente chiede anche una correzione, la sola localizzazione non chiude il ciclo.
        require_verified_correction = (
            remaining_budget > 0
            and symptom_requests_correction(str(state.get("symptom") or ""))
            and not has_verified_resolution(state)
        )
        # I vincoli invarianti sono ammessi solo quando fanno parte dell'obiettivo utente.
        allow_unchanged_expectations = symptom_requests_preservation(
            str(state.get("symptom") or "")
        )
        # I sintomi di amplificazione richiedono una misura esplicita del guadagno.
        require_gain_comparison = symptom_requires_gain_comparison(
            str(state.get("symptom") or "")
        )
        # Distorsione e clipping richiedono una metrica transitoria dedicata.
        require_quality_analysis = symptom_requires_quality_analysis(
            str(state.get("symptom") or "")
        )
        # Un obiettivo VAC deve essere verificato sull'ampiezza transitoria, non sul solo punto DC.
        require_variable_signal_measurement = symptom_requires_variable_signal_measurement(
            str(state.get("symptom") or "")
        )
        # LED e lampade richiedono una prova diretta della corrente o potenza del ramo.
        require_direct_component_measurement = symptom_requires_direct_component_measurement(
            str(state.get("symptom") or "")
        )
        # Un obiettivo composto resta aperto finche una singola run non verifica entrambi i target.
        require_joint_objective_verification = (
            remaining_budget > 0
            and require_variable_signal_measurement
            and require_direct_component_measurement
            and not has_verified_joint_objective(state)
        )
        # Un obiettivo temporale richiede una soglia esplicita sul profilo del componente.
        require_temporal_expectation = symptom_requires_temporal_expectation(
            str(state.get("symptom") or "")
        )
        # Un singolo livello di stimolo non basta per attribuire a un guasto
        # strutturale un trasferimento sotto soglia, se resta budget disponibile.
        require_signal_amplitude_followup = (
            remaining_budget > 0
            and require_gain_comparison
            and not has_verified_resolution(state)
            and signal_gain_requires_amplitude_followup(state)
        )
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
                require_first_scenario=require_first_scenario,
                require_verified_resolution=require_verified_resolution,
                require_verified_correction=require_verified_correction,
                allow_unchanged_expectations=allow_unchanged_expectations,
                require_gain_comparison=require_gain_comparison,
                require_quality_analysis=require_quality_analysis,
                require_variable_signal_measurement=require_variable_signal_measurement,
                require_direct_component_measurement=require_direct_component_measurement,
                require_joint_objective_verification=require_joint_objective_verification,
                require_temporal_expectation=require_temporal_expectation,
                require_signal_amplitude_followup=require_signal_amplitude_followup,
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
            state["final_cause"] = decision.get("final_cause") or ""
            state["verified_correction"] = decision.get("verified_correction") or ""
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


def summarize_state(state: dict[str, Any], output_dir: Path | None = None) -> dict[str, Any]:
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
        "agent_view": build_agent_view(state, output_dir),
    }
