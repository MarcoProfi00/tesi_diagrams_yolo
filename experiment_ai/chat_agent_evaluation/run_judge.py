#!/usr/bin/env python3
"""Prepara, valida ed eventualmente valuta il pacchetto anonimo del judge.

Senza ``--run`` esegue soltanto il preflight locale. Con ``--run`` accetta
esclusivamente la configurazione congelata dell'esperimento e salva una
risposta strutturata dopo averla validata.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import time
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]
DEFAULT_EVALUATION_DIR = SCRIPT_DIR / "evaluation"
PROMPT_PATH = SCRIPT_DIR / "judge_prompt_v1.md"
RESPONSE_SCHEMA_PATH = SCRIPT_DIR / "judge_response_schema_v1.json"
DEFAULT_ENV_FILES = (PROJECT_ROOT / ".env", PROJECT_ROOT / "scripts" / "GPT" / ".env")
MODES = ("chat", "agent")
TASK_TYPES = ("diagnosis", "functional_verification", "configuration_goal")
OUTCOMES = ("success", "partial_success", "failure", "inconclusive")
CRITERIA = (
    "task_achievement",
    "technical_correctness",
    "scenario_quality",
    "evidence_interpretation",
    "conclusion_quality",
)
CRITICAL_ERRORS = ("false_success", "unsupported_claims", "wrong_interpretation")
PROMPT_VERSION = "v1"
PACKET_SCHEMA_VERSION = 3
FROZEN_JUDGE_MODEL = "gpt-5.5"
FROZEN_REASONING_EFFORT = "medium"
FROZEN_PROMPT_SHA256 = (
    "d17f518aca6f6b3505a98982020c735e8c8472457e1ad7689f19388f580e916f"
)
FROZEN_RESPONSE_SCHEMA_SHA256 = (
    "aeb6c6559232490d3b870ef82e3870ea1e200eace7ae4d06ed10128cdf2f2a3c"
)
MODE_PATH_PATTERN = re.compile(
    r"(?i)([\\/]+web[\\/]+)(?:chat|agent)([\\/]+)"
)


class JudgeValidationError(ValueError):
    """Risposta del judge assente, incompleta o incoerente con lo schema."""


def load_env_file(path: Path) -> None:
    """Carica un file .env locale senza sovrascrivere l'ambiente corrente."""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def load_default_env_files() -> None:
    for path in DEFAULT_ENV_FILES:
        load_env_file(path)


def load_summary(path: Path) -> dict[str, Any]:
    """Carica un summary e controlla che contenga i blocchi indispensabili."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Summary non trovato: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON non valido in {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError(f"Il summary deve essere un oggetto JSON: {path}")

    missing = [key for key in ("case", "base_evidence", "scenarios", "final") if key not in data]
    if missing:
        raise ValueError(f"Campi mancanti in {path}: {', '.join(missing)}")

    return data


def is_executed_scenario(scenario: dict[str, Any]) -> bool:
    """Riconosce gli scenari realmente eseguiti, non quelli solo proposti."""
    execution = scenario.get("execution") or {}
    return (
        scenario.get("registry_status") == "executed"
        or execution.get("spice_executed") is True
    )


def select_quantity(quantity: Any) -> Any:
    """Conserva le misure, ma non i giudizi automatici sul loro significato."""
    if not isinstance(quantity, dict):
        return quantity

    return {
        "quantity": quantity.get("quantity"),
        "metric": quantity.get("metric"),
        "measurement": quantity.get("measurement"),
        "base_value": quantity.get("base_value"),
        "scenario_value": quantity.get("scenario_value"),
        "delta": quantity.get("delta"),
        "change": quantity.get("change"),
        "expectation": quantity.get("expectation"),
        "expectation_met": quantity.get("expectation_met"),
        "meaningful_improvement": quantity.get("meaningful_improvement"),
        "base_details": quantity.get("base_details"),
        "scenario_details": quantity.get("scenario_details"),
    }


def select_scenario(scenario: dict[str, Any]) -> dict[str, Any]:
    """Mantiene soltanto dati, azioni e risultati utili alla valutazione."""
    execution = scenario.get("execution") or {}
    return {
        "scenario_id": scenario.get("scenario_id"),
        "title": scenario.get("title"),
        "hypothesis": scenario.get("hypothesis"),
        "intent": scenario.get("intent"),
        "actions": scenario.get("actions"),
        "analysis": scenario.get("analysis"),
        "compare": scenario.get("compare"),
        "expect": scenario.get("expect"),
        "execution": {
            "status": execution.get("status"),
            "spice_executed": execution.get("spice_executed"),
            "spice_status": execution.get("spice_status"),
            "spice_exit_code": execution.get("spice_exit_code"),
            "diagnostic_outcome": execution.get("diagnostic_outcome"),
            "comparison_summary": execution.get("comparison_summary"),
            "quantities": [
                select_quantity(quantity)
                for quantity in execution.get("quantities") or []
            ],
            "comparison_evidence": execution.get("comparison_evidence") or {},
            "led_profiles": execution.get("led_profiles") or {},
        },
    }


def select_final(summary: dict[str, Any]) -> dict[str, Any]:
    """Mantiene il contenuto finale e le evidenze strutturate che lo supportano."""
    final = summary.get("final") or {}
    if not isinstance(final, dict):
        return {"content": final}

    selected: dict[str, Any] = {}
    for key, value in final.items():
        if key == "response_turn_id":
            continue
        if key == "best_verified_scenario" and isinstance(value, dict):
            selected[key] = {
                field: value.get(field)
                for field in (
                    "available",
                    "best_scenario_id",
                    "best_outcome_status",
                    "best_stop_automation",
                    "ranking_status",
                )
            }
            continue
        selected[key] = value
    return selected


def select_interaction_trace(
    summary: dict[str, Any],
    mode: str,
) -> list[dict[str, Any]]:
    """Rappresenta l'intera interazione senza duplicare scenari e finale."""
    initial = (summary.get("case") or {}).get("symptom")
    if mode == "chat":
        final_response = (summary.get("final") or {}).get("response")
        trace: list[dict[str, Any]] = []
        for turn in summary.get("conversation") or []:
            if not isinstance(turn, dict):
                continue
            role = turn.get("role")
            content = turn.get("content")
            if role == "assistant" and content == final_response:
                continue

            event: dict[str, Any] = {
                "step": turn.get("turn_id"),
                "actor": "user" if role == "user" else "system",
            }
            if role == "system" and turn.get("scenario_id"):
                event.update(
                    {
                        "event": "scenario_execution",
                        "scenario_id": turn.get("scenario_id"),
                        "scenario_outcome": turn.get("scenario_outcome"),
                    }
                )
            else:
                event["content"] = content
                if turn.get("selected_run") is not None:
                    event["selected_run"] = turn.get("selected_run")
            trace.append(event)
        return trace

    trace = [{"step": 0, "actor": "user", "content": initial}]
    for index, decision in enumerate(summary.get("decisions") or [], start=1):
        if not isinstance(decision, dict):
            continue
        trace.append(
            {
                "step": decision.get("decision_number") or index,
                "actor": "system",
                "event": "decision",
                "decision": decision.get("decision"),
                "reason": decision.get("reason"),
                "scenarios": decision.get("scenarios") or [],
                "scenario_results": decision.get("scenario_results") or [],
            }
        )
    return trace


def select_node_map(value: Any) -> Any:
    if not isinstance(value, dict):
        return value
    return {
        "component_terminal_nodes": value.get("component_terminal_nodes"),
        "warnings": value.get("warnings"),
        "stats": value.get("stats"),
    }


def select_value_data(value: Any) -> Any:
    if not isinstance(value, dict):
        return value
    return {
        key: item
        for key, item in value.items()
        if key not in {"source", "label_text"}
    }


def select_values_bound(value: Any) -> Any:
    if not isinstance(value, dict):
        return value
    components = value.get("components") or {}
    compact_components = {
        component_id: {
            "class_name": component.get("class_name"),
            "value_data": select_value_data(component.get("value_data")),
            "status": component.get("status"),
        }
        for component_id, component in components.items()
        if isinstance(component, dict)
    }
    return {
        "components": compact_components,
        "nodes": value.get("nodes"),
        "simulation": value.get("simulation"),
        "missing": value.get("missing"),
        "stats": value.get("stats"),
    }


def select_spice_emit_report(value: Any) -> Any:
    if not isinstance(value, dict):
        return value
    return {
        key: value.get(key)
        for key in (
            "emitted_elements",
            "skipped_elements",
            "skipped_components",
            "informational_skips",
            "measurement_points",
            "analyses",
            "models",
            "warnings",
        )
    }


def parse_spice_number(value: str) -> float | str:
    try:
        number = float(value)
    except ValueError:
        return value
    return number if math.isfinite(number) else value


def select_base_operating_point(stdout: Any) -> dict[str, Any]:
    """Estrae le tabelle nodo/corrente evitando i lunghi dump dei modelli."""
    if not isinstance(stdout, str):
        return {"node_voltages": {}, "source_currents": {}}

    node_voltages: dict[str, Any] = {}
    source_currents: dict[str, Any] = {}
    active: dict[str, Any] | None = None

    for raw_line in stdout.splitlines():
        stripped = raw_line.strip()
        normalized = " ".join(stripped.lower().split())
        if normalized == "node voltage":
            active = node_voltages
            continue
        if normalized == "source current":
            active = source_currents
            continue
        if not stripped:
            active = None
            continue
        if active is None or stripped.startswith("-"):
            continue
        parts = stripped.split()
        if len(parts) != 2:
            active = None
            continue
        active[parts[0]] = parse_spice_number(parts[1])

    return {
        "node_voltages": node_voltages,
        "source_currents": source_currents,
    }


def anonymize_packet_value(value: Any) -> Any:
    """Rimuove dai contenuti eventuali marcatori tecnici della modalità."""
    if isinstance(value, dict):
        return {
            key: anonymize_packet_value(item)
            for key, item in value.items()
            if str(key).lower() != "mode"
        }
    if isinstance(value, list):
        return [anonymize_packet_value(item) for item in value]
    if isinstance(value, str):
        return MODE_PATH_PATTERN.sub(r"\1run\2", value)
    return value


def build_judge_packet(summary: dict[str, Any], mode: str) -> dict[str, Any]:
    """Costruisce il pacchetto essenziale e mode-blind per una singola run."""
    if mode not in MODES:
        raise ValueError(f"Modalità non valida: {mode}")

    base = summary.get("base_evidence") or {}
    diagnostic_context = base.get("diagnostic_context") or {}
    executed_scenarios = [
        select_scenario(scenario)
        for scenario in summary.get("scenarios") or []
        if isinstance(scenario, dict) and is_executed_scenario(scenario)
    ]

    packet = {
        "schema_version": PACKET_SCHEMA_VERSION,
        "interaction_trace": select_interaction_trace(summary, mode),
        "circuit_context": {
            "node_map": select_node_map(base.get("node_map")),
            "values_bound": select_values_bound(base.get("values_bound")),
            "netlist": base.get("netlist"),
            "spice_emit_report": select_spice_emit_report(
                base.get("spice_emit_report")
            ),
            "simulation_summary": diagnostic_context.get("summary"),
            "base_operating_point": select_base_operating_point(
                base.get("ngspice_stdout")
            ),
            "ngspice_stderr": base.get("ngspice_stderr"),
        },
        "executed_scenarios": executed_scenarios,
        "final": select_final(summary),
    }
    return anonymize_packet_value(packet)


def require_exact_keys(data: dict[str, Any], expected: tuple[str, ...], label: str) -> None:
    actual = set(data)
    expected_set = set(expected)
    missing = sorted(expected_set - actual)
    extra = sorted(actual - expected_set)
    problems = []
    if missing:
        problems.append(f"mancanti: {', '.join(missing)}")
    if extra:
        problems.append(f"non previsti: {', '.join(extra)}")
    if problems:
        raise JudgeValidationError(f"{label}: {'; '.join(problems)}")


def require_non_empty_string(value: Any, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise JudgeValidationError(f"{label}: deve essere una stringa non vuota")


def contains_mode_marker(value: Any) -> bool:
    if isinstance(value, dict):
        return any(
            str(key).lower() == "mode" or contains_mode_marker(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(contains_mode_marker(item) for item in value)
    return isinstance(value, str) and MODE_PATH_PATTERN.search(value) is not None


def validate_judge_packet(packet: Any) -> dict[str, Any]:
    """Blocca pacchetti incompleti o capaci di rivelare la modalità."""
    if not isinstance(packet, dict):
        raise JudgeValidationError("Il pacchetto del judge deve essere un oggetto")
    require_exact_keys(
        packet,
        (
            "schema_version",
            "interaction_trace",
            "circuit_context",
            "executed_scenarios",
            "final",
        ),
        "pacchetto",
    )
    if packet["schema_version"] != PACKET_SCHEMA_VERSION:
        raise JudgeValidationError("Versione del pacchetto non valida")

    interaction_trace = packet["interaction_trace"]
    if not isinstance(interaction_trace, list) or not interaction_trace:
        raise JudgeValidationError(
            "interaction_trace deve contenere almeno un evento"
        )
    for index, event in enumerate(interaction_trace):
        if not isinstance(event, dict):
            raise JudgeValidationError(
                f"interaction_trace[{index}] deve essere un oggetto"
            )
        if event.get("actor") not in {"user", "system"}:
            raise JudgeValidationError(
                f"interaction_trace[{index}].actor non valido"
            )
        if (
            event.get("event") not in {"scenario_execution", "decision"}
            and not isinstance(event.get("content"), str)
        ):
            raise JudgeValidationError(
                f"interaction_trace[{index}] non contiene testo o evento"
            )

    context = packet["circuit_context"]
    if not isinstance(context, dict):
        raise JudgeValidationError("circuit_context deve essere un oggetto")
    require_exact_keys(
        context,
        (
            "node_map",
            "values_bound",
            "netlist",
            "spice_emit_report",
            "simulation_summary",
            "base_operating_point",
            "ngspice_stderr",
        ),
        "circuit_context",
    )

    scenarios = packet["executed_scenarios"]
    if not isinstance(scenarios, list) or not scenarios:
        raise JudgeValidationError(
            "executed_scenarios deve contenere almeno uno scenario"
        )
    for index, scenario in enumerate(scenarios):
        if not isinstance(scenario, dict):
            raise JudgeValidationError(
                f"executed_scenarios[{index}] deve essere un oggetto"
            )
        execution = scenario.get("execution") or {}
        if execution.get("spice_executed") is not True:
            raise JudgeValidationError(
                f"executed_scenarios[{index}] non risulta eseguito"
            )

    if not isinstance(packet["final"], dict) or not packet["final"]:
        raise JudgeValidationError("final deve essere un oggetto non vuoto")
    if contains_mode_marker(packet):
        raise JudgeValidationError("Il pacchetto contiene un marcatore della modalità")
    return packet


def validate_frozen_protocol(model: str, reasoning_effort: str) -> None:
    """Impedisce di mescolare configurazioni diverse nell'esperimento."""
    if model != FROZEN_JUDGE_MODEL:
        raise JudgeValidationError(
            f"Modello non conforme al protocollo: usa {FROZEN_JUDGE_MODEL}"
        )
    if reasoning_effort != FROZEN_REASONING_EFFORT:
        raise JudgeValidationError(
            "Reasoning effort non conforme al protocollo: usa "
            f"{FROZEN_REASONING_EFFORT}"
        )

    prompt_sha256 = hashlib.sha256(PROMPT_PATH.read_bytes()).hexdigest()
    schema_sha256 = hashlib.sha256(RESPONSE_SCHEMA_PATH.read_bytes()).hexdigest()
    if prompt_sha256 != FROZEN_PROMPT_SHA256:
        raise JudgeValidationError(
            "Il prompt è cambiato rispetto alla versione congelata"
        )
    if schema_sha256 != FROZEN_RESPONSE_SCHEMA_SHA256:
        raise JudgeValidationError(
            "Lo schema di risposta è cambiato rispetto alla versione congelata"
        )
    if not load_judge_instructions().strip():
        raise JudgeValidationError("Il prompt del judge è vuoto")
    if not isinstance(load_response_schema(), dict):
        raise JudgeValidationError("Lo schema di risposta non è un oggetto JSON")


def validate_judge_response(response: Any) -> dict[str, Any]:
    """Valida la parte semantica restituita dal modello judge."""
    if not isinstance(response, dict):
        raise JudgeValidationError("La risposta del judge deve essere un oggetto JSON")

    require_exact_keys(
        response,
        ("task", "criteria", "critical_errors", "evidence", "final_assessment"),
        "risposta",
    )

    task = response["task"]
    if not isinstance(task, dict):
        raise JudgeValidationError("task: deve essere un oggetto")
    require_exact_keys(task, ("type", "outcome", "outcome_reason"), "task")
    if task["type"] not in TASK_TYPES:
        raise JudgeValidationError(f"task.type non valido: {task['type']!r}")
    if task["outcome"] not in OUTCOMES:
        raise JudgeValidationError(f"task.outcome non valido: {task['outcome']!r}")
    require_non_empty_string(task["outcome_reason"], "task.outcome_reason")

    criteria = response["criteria"]
    if not isinstance(criteria, dict):
        raise JudgeValidationError("criteria: deve essere un oggetto")
    require_exact_keys(criteria, CRITERIA, "criteria")
    for name in CRITERIA:
        criterion = criteria[name]
        if not isinstance(criterion, dict):
            raise JudgeValidationError(f"criteria.{name}: deve essere un oggetto")
        require_exact_keys(criterion, ("score", "reason"), f"criteria.{name}")
        score = criterion["score"]
        if type(score) is not int or not 0 <= score <= 4:
            raise JudgeValidationError(
                f"criteria.{name}.score: deve essere un intero tra 0 e 4"
            )
        require_non_empty_string(criterion["reason"], f"criteria.{name}.reason")

    critical_errors = response["critical_errors"]
    if not isinstance(critical_errors, dict):
        raise JudgeValidationError("critical_errors: deve essere un oggetto")
    require_exact_keys(critical_errors, CRITICAL_ERRORS, "critical_errors")
    for name in CRITICAL_ERRORS:
        error = critical_errors[name]
        if not isinstance(error, dict):
            raise JudgeValidationError(f"critical_errors.{name}: deve essere un oggetto")
        require_exact_keys(error, ("present", "reason"), f"critical_errors.{name}")
        if type(error["present"]) is not bool:
            raise JudgeValidationError(
                f"critical_errors.{name}.present: deve essere booleano"
            )
        if not isinstance(error["reason"], str):
            raise JudgeValidationError(
                f"critical_errors.{name}.reason: deve essere una stringa"
            )
        if error["present"] and not error["reason"].strip():
            raise JudgeValidationError(
                f"critical_errors.{name}.reason: obbligatoria quando present=true"
            )
        if not error["present"] and error["reason"]:
            raise JudgeValidationError(
                f"critical_errors.{name}.reason: deve essere vuota quando present=false"
            )

    evidence = response["evidence"]
    if not isinstance(evidence, list) or not 1 <= len(evidence) <= 5:
        raise JudgeValidationError("evidence: deve contenere da 1 a 5 elementi")
    for index, item in enumerate(evidence):
        require_non_empty_string(item, f"evidence[{index}]")

    require_non_empty_string(response["final_assessment"], "final_assessment")
    return response


def computed_score(response: dict[str, Any]) -> dict[str, int]:
    """Calcola il totale: cinque criteri uguali, ciascuno pesato al 20%."""
    total = sum(response["criteria"][name]["score"] for name in CRITERIA) * 5
    return {"weighted_total": total, "maximum": 100}


def canonical_json_sha256(data: Any) -> str:
    """Calcola un hash stabile indipendente da indentazione e ordine delle chiavi."""
    encoded = json.dumps(
        data,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_saved_judge_result(
    response: dict[str, Any],
    *,
    circuit_id: str,
    mode: str,
    judge_model: str,
    reasoning_effort: str,
    packet: dict[str, Any],
    summary_path: Path,
) -> dict[str, Any]:
    """Aggiunge soltanto metadati verificabili e il punteggio calcolato."""
    validate_judge_response(response)
    summary_sha256 = hashlib.sha256(summary_path.read_bytes()).hexdigest()
    prompt_sha256 = hashlib.sha256(PROMPT_PATH.read_bytes()).hexdigest()
    packet_sha256 = canonical_json_sha256(packet)
    return {
        "schema_version": 1,
        "metadata": {
            "circuit_id": circuit_id,
            "mode": mode,
            "judge_model": judge_model,
            "reasoning_effort": reasoning_effort,
            "prompt_version": PROMPT_VERSION,
            "packet_schema_version": PACKET_SCHEMA_VERSION,
            "prompt_sha256": prompt_sha256,
            "response_schema_sha256": hashlib.sha256(
                RESPONSE_SCHEMA_PATH.read_bytes()
            ).hexdigest(),
            "packet_sha256": packet_sha256,
            "summary_sha256": summary_sha256,
        },
        **response,
        "computed_score": computed_score(response),
    }


def load_judge_instructions() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def load_response_schema() -> dict[str, Any]:
    schema = json.loads(RESPONSE_SCHEMA_PATH.read_text(encoding="utf-8"))
    # Questa annotazione documenta il file, ma non fa parte del sottoinsieme
    # JSON Schema richiesto alla Responses API.
    schema.pop("$schema", None)
    return schema


def call_judge(
    packet: dict[str, Any],
    *,
    model: str,
    reasoning_effort: str,
    max_output_tokens: int,
) -> tuple[dict[str, Any], float]:
    """Esegue una singola valutazione e restituisce JSON validato e latenza."""
    validate_frozen_protocol(model, reasoning_effort)
    validate_judge_packet(packet)

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "Pacchetto 'openai' non installato nell'ambiente Python."
        ) from exc

    load_default_env_files()
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY non trovata nell'ambiente o nei file .env locali."
        )

    instructions = load_judge_instructions()
    packet_json = json.dumps(packet, ensure_ascii=False, separators=(",", ":"))
    request: dict[str, Any] = {
        "model": model,
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"{instructions}\n\nPACCHETTO DA VALUTARE:\n{packet_json}",
                    }
                ],
            }
        ],
        "max_output_tokens": max_output_tokens,
        "text": {
            "format": {
                "type": "json_schema",
                "name": "chat_agent_judge_v1",
                "description": "Valutazione semantica di una singola traiettoria.",
                "strict": True,
                "schema": load_response_schema(),
            }
        },
    }
    if model.startswith("gpt-5"):
        request["reasoning"] = {"effort": reasoning_effort}

    started = time.perf_counter()
    response = OpenAI().responses.create(**request)
    latency_seconds = time.perf_counter() - started
    output_text = (getattr(response, "output_text", None) or "").strip()
    if not output_text:
        raise RuntimeError("La Responses API non ha restituito output_text.")

    try:
        parsed = json.loads(output_text)
    except json.JSONDecodeError as exc:
        raise JudgeValidationError(f"Il judge non ha restituito JSON valido: {exc}") from exc

    return validate_judge_response(parsed), latency_seconds


def save_judge_result(path: Path, result: dict[str, Any], *, force: bool) -> None:
    """Salva il risultato soltanto dopo la validazione completa."""
    if path.exists() and not force:
        raise FileExistsError(f"{path} esiste già; usa --force per sostituirlo")
    path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def packet_preview(
    circuit_id: str,
    mode: str,
    summary_path: Path,
    packet: dict[str, Any],
) -> dict[str, Any]:
    """Restituisce un riepilogo leggibile senza stampare tutto il pacchetto."""
    packet_json = json.dumps(packet, ensure_ascii=False, separators=(",", ":"))
    encoded = packet_json.encode("utf-8")
    request_characters = len(load_judge_instructions()) + len(packet_json)
    scenarios = packet["executed_scenarios"]
    return {
        "circuit_id": circuit_id,
        "mode": mode,
        "summary_path": str(summary_path),
        "packet_size_bytes": len(encoded),
        "approximate_input_tokens": math.ceil(request_characters / 4),
        "packet_sha256": canonical_json_sha256(packet),
        "executed_scenarios_count": len(scenarios),
        "executed_scenario_ids": [item.get("scenario_id") for item in scenarios],
        "circuit_context_fields": list(packet["circuit_context"]),
        "final_fields": list(packet["final"]),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepara l'input anonimo del judge senza chiamare il modello."
    )
    parser.add_argument("--circuit", required=True, help="ID del circuito, per esempio a01")
    parser.add_argument(
        "--mode",
        choices=(*MODES, "both"),
        default="both",
        help="Summary da preparare (default: both)",
    )
    parser.add_argument(
        "--evaluation-dir",
        type=Path,
        default=DEFAULT_EVALUATION_DIR,
        help="Cartella contenente evaluation/<circuito>/",
    )
    parser.add_argument(
        "--show-packet",
        action="store_true",
        help="Stampa il pacchetto completo invece della sola anteprima.",
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Chiama il judge e salva <mode>_judge.json.",
    )
    parser.add_argument(
        "--judge-model",
        help="Modello del judge; obbligatorio insieme a --run.",
    )
    parser.add_argument(
        "--reasoning-effort",
        choices=("low", "medium", "high", "xhigh"),
        default="medium",
        help="Reasoning effort per i modelli GPT-5 (default: medium).",
    )
    parser.add_argument(
        "--max-output-tokens",
        type=int,
        default=4000,
        help="Limite dell'output del judge (default: 4000).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Sostituisce un file judge già esistente.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.run and not args.judge_model:
        raise SystemExit("Errore: --judge-model è obbligatorio insieme a --run.")
    if args.max_output_tokens < 1:
        raise SystemExit("Errore: --max-output-tokens deve essere positivo.")

    modes = MODES if args.mode == "both" else (args.mode,)
    packets: dict[str, dict[str, Any]] = {}
    previews: list[dict[str, Any]] = []
    summary_paths: dict[str, Path] = {}

    try:
        for mode in modes:
            summary_path = args.evaluation_dir / args.circuit / f"{mode}_summary.json"
            summary = load_summary(summary_path)
            packet = build_judge_packet(summary, mode)
            validate_judge_packet(packet)
            packets[mode] = packet
            summary_paths[mode] = summary_path
            previews.append(packet_preview(args.circuit, mode, summary_path, packet))
    except ValueError as exc:
        raise SystemExit(f"Errore: {exc}") from exc

    if args.run:
        completed = []
        try:
            validate_frozen_protocol(args.judge_model, args.reasoning_effort)
            output_paths = {
                mode: args.evaluation_dir / args.circuit / f"{mode}_judge.json"
                for mode in modes
            }
            existing = [
                path for path in output_paths.values()
                if path.exists()
            ]
            if existing and not args.force:
                joined = ", ".join(str(path) for path in existing)
                raise FileExistsError(
                    f"File judge già esistenti: {joined}. Usa --force per sostituirli"
                )

            for mode in modes:
                output_path = output_paths[mode]
                response, latency_seconds = call_judge(
                    packets[mode],
                    model=args.judge_model,
                    reasoning_effort=args.reasoning_effort,
                    max_output_tokens=args.max_output_tokens,
                )
                result = build_saved_judge_result(
                    response,
                    circuit_id=args.circuit,
                    mode=mode,
                    judge_model=args.judge_model,
                    reasoning_effort=args.reasoning_effort,
                    packet=packets[mode],
                    summary_path=summary_paths[mode],
                )
                save_judge_result(output_path, result, force=args.force)
                completed.append(
                    {
                        "circuit_id": args.circuit,
                        "mode": mode,
                        "output_path": str(output_path),
                        "weighted_total": result["computed_score"]["weighted_total"],
                        "latency_seconds": round(latency_seconds, 3),
                    }
                )
        except (FileExistsError, JudgeValidationError, RuntimeError) as exc:
            raise SystemExit(f"Errore: {exc}") from exc

        print(json.dumps(completed, ensure_ascii=False, indent=2))
        return 0

    output: Any
    if args.show_packet:
        output = packets if len(packets) > 1 else packets[modes[0]]
    else:
        output = previews

    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
