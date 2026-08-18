#!/usr/bin/env python3
"""Genera pacchetti compatti e anonimi per il judge CHAT/AGENT."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parent
EVALUATION_DIR = ROOT / "evaluation"
REFERENCES_DIR = ROOT / "references"
OUTPUT_DIR = ROOT / "judge_inputs"
MODES = ("chat", "agent")


def anonymize(value: Any) -> Any:
    """Rimuove dai contenuti i nomi delle due modalita' e uniforma gli ID."""
    if isinstance(value, dict):
        return {key: anonymize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [anonymize(item) for item in value]
    if not isinstance(value, str):
        return value

    text = re.sub(r"(?i)agent_scenario_", "scenario_", value)
    text = re.sub(r"(?i)([\\/])(?:chat|agent)([\\/])", r"\1run\2", text)
    text = re.sub(r"(?i)(?:chat|agent)_", "run_", text)
    text = re.sub(r"(?i)\b(?:chat|agent)\b", "RUN", text)
    return text


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"YAML non valido: {path}")
    return data


def clean_reference(reference: dict[str, Any]) -> dict[str, Any]:
    """Esclude note di revisione che anticipano il giudizio sulle modalita'."""
    keep = (
        "schema_version",
        "circuit_id",
        "circuit_description",
        "task_type",
        "user_symptom",
        "circuit_inventory",
        "testbench_assumptions",
        "required_evidence",
        "success_conditions",
        "acceptable_solutions",
        "unsupported_conclusions",
    )
    return anonymize({key: reference[key] for key in keep if key in reference})


def clean_quantity(quantity: Any) -> Any:
    if not isinstance(quantity, dict):
        return quantity
    keep = (
        "quantity",
        "metric",
        "measurement",
        "base_value",
        "scenario_value",
        "delta",
        "change",
        "expectation",
        "base_details",
        "scenario_details",
    )
    return {key: quantity.get(key) for key in keep if key in quantity}


def clean_scenario(scenario: dict[str, Any]) -> dict[str, Any]:
    execution = scenario.get("execution") or {}
    executed = (
        scenario.get("registry_status") == "executed"
        or execution.get("spice_executed") is True
    )
    clean_execution: dict[str, Any] | None = None
    if executed:
        clean_execution = {
            "spice_status": execution.get("spice_status"),
            "spice_exit_code": execution.get("spice_exit_code"),
            "quantities": [
                clean_quantity(item) for item in execution.get("quantities") or []
            ],
            "comparison_evidence": execution.get("comparison_evidence") or {},
            "led_profiles": execution.get("led_profiles") or {},
        }
    return anonymize({
        "scenario_id": scenario.get("scenario_id"),
        "title": scenario.get("title"),
        "hypothesis": scenario.get("hypothesis"),
        "intent": scenario.get("intent"),
        "actions": scenario.get("actions") or [],
        "analysis": scenario.get("analysis"),
        "compare": scenario.get("compare") or [],
        "expect": scenario.get("expect") or {},
        "executed": executed,
        "execution": clean_execution,
    })


def clean_final(summary: dict[str, Any]) -> dict[str, Any]:
    final = summary.get("final") or {}
    if "response" in final:
        return anonymize({"response": final.get("response")})
    return anonymize({
        key: final.get(key)
        for key in ("answer", "cause", "verified_correction")
        if final.get(key) is not None
    })


def clean_user_followups(summary: dict[str, Any]) -> list[dict[str, Any]]:
    """Conserva i messaggi utente successivi alla richiesta iniziale.

    Gli scenari strutturati descrivono le azioni della pipeline, ma nella
    modalita' guidata l'utente puo' anche fornire misure, osservazioni o una
    richiesta esplicita di conclusione. Il primo messaggio utente coincide con
    ``case.symptom`` ed e' gia' incluso come ``initial_request``.
    """
    followups: list[dict[str, Any]] = []
    initial_user_seen = False
    for turn_index, item in enumerate(summary.get("conversation") or []):
        if not isinstance(item, dict) or item.get("role") != "user":
            continue
        content = item.get("content")
        if not isinstance(content, str) or not content.strip():
            continue
        if not initial_user_seen:
            initial_user_seen = True
            continue
        followups.append({
            "turn_index": turn_index,
            "content": content,
        })
    return anonymize(followups)


def technical_status(summary: dict[str, Any]) -> str:
    final = clean_final(summary)
    if not any(final.values()):
        return "technical_failure"
    if (summary.get("execution") or {}).get("failed_spice_runs", 0):
        return "completed_with_errors"
    return "completed"


def build_packet(circuit_id: str, mode: str) -> dict[str, Any]:
    summary_path = EVALUATION_DIR / circuit_id / f"{mode}_summary.json"
    reference_path = REFERENCES_DIR / f"{circuit_id}.yaml"
    summary = read_json(summary_path)
    reference = read_yaml(reference_path)
    execution = summary.get("execution") or {}
    base = summary.get("base_evidence") or {}
    spice_run = base.get("spice_run") or {}
    user_followups = clean_user_followups(summary) if mode == "chat" else []

    return {
        "packet_schema_version": 1,
        "packet_id": f"{circuit_id}_{'run_1' if mode == 'chat' else 'run_2'}",
        "reference": clean_reference(reference),
        "rubric": {
            "score_scale": {
                "0": "errato o assente",
                "1": "utile ma incompleto o con limiti rilevanti",
                "2": "corretto e adeguatamente verificato",
            },
            "criteria": [
                "diagnostic_correctness",
                "test_quality",
                "evidence_interpretation",
                "goal_achievement",
                "conclusion_quality",
            ],
        },
        "run": {
            "initial_request": (summary.get("case") or {}).get("symptom"),
            "technical_status": technical_status(summary),
            "base_spice": {
                "status": spice_run.get("status"),
                "exit_code": spice_run.get("exit_code"),
                "message": spice_run.get("message"),
                "analyses": (base.get("spice_emit_report") or {}).get("analyses"),
            },
            "execution_counts": {
                "scenarios_proposed": execution.get("scenarios_proposed"),
                "scenarios_executed": execution.get("scenarios_executed"),
                "successful_spice_runs": execution.get("successful_spice_runs"),
                "failed_spice_runs": execution.get("failed_spice_runs"),
            },
            **({
                "user_followups": {
                    "evidence_policy": (
                        "Questi messaggi documentano l'interazione guidata e "
                        "le istruzioni effettivamente ricevute dalla run. Non "
                        "sono ground truth: osservazioni e misure riportate "
                        "dall'utente valgono come evidenza della traiettoria "
                        "solo se sono compatibili con lo scenario eseguito e "
                        "con il riferimento tecnico."
                    ),
                    "messages": user_followups,
                },
            } if user_followups else {}),
            "scenarios": [clean_scenario(item) for item in summary.get("scenarios") or []],
            "final": clean_final(summary),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--circuit", help="ID del singolo circuito")
    group.add_argument("--all", action="store_true", help="Genera tutti i 42 pacchetti")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    circuit_ids = (
        [args.circuit]
        if args.circuit
        else sorted(path.name for path in EVALUATION_DIR.iterdir() if path.is_dir())
    )

    generated = 0
    for circuit_id in circuit_ids:
        for mode in MODES:
            packet = build_packet(circuit_id, mode)
            destination = OUTPUT_DIR / circuit_id / f"{mode}_packet.json"
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(
                json.dumps(packet, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            print(destination.relative_to(ROOT))
            generated += 1

    print(f"Pacchetti generati: {generated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
