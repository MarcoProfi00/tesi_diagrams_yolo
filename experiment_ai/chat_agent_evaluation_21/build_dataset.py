#!/usr/bin/env python3
"""Genera il dataset descrittivo della valutazione unificata CHAT–AGENT.

Lo script legge esclusivamente i summary congelati in ``evaluation/`` e
produce file tabellari descrittivi e schede di riferimento vuote. Non assegna
punteggi e non usa le etichette interne della pipeline come ground truth.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_EVALUATION_DIR = SCRIPT_DIR / "evaluation"
DEFAULT_DATASET_DIR = SCRIPT_DIR / "dataset"
DEFAULT_REFERENCES_DIR = SCRIPT_DIR / "references"
MODES = ("chat", "agent")


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"JSON radice non valido: {path}")
    return data


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def ordered_unique(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = str(value or "").strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result


def analysis_types(summary: dict[str, Any]) -> list[str]:
    base = summary.get("base_evidence") or {}
    component_rules = base.get("component_rules") or {}
    simulation = component_rules.get("simulation") or {}
    configured = simulation.get("analyses") or []
    if isinstance(configured, str):
        configured = [configured]
    analyses = ordered_unique(str(item).lower() for item in configured)

    netlist = str(base.get("netlist") or "")
    for line in netlist.splitlines():
        directive = line.strip().lower().split(maxsplit=1)[0] if line.strip() else ""
        if directive in {".op", ".tran", ".ac", ".dc"}:
            analyses.append(directive[1:])
    return ordered_unique(analyses)


def integrated_circuit_models(summary: dict[str, Any]) -> list[str]:
    base = summary.get("base_evidence") or {}
    rules = (base.get("component_rules") or {}).get("components") or {}
    models: list[str] = []
    if not isinstance(rules, dict):
        return models
    for rule in rules.values():
        if not isinstance(rule, dict):
            continue
        class_name = str(rule.get("class_name") or "")
        if class_name.casefold() != "integrated_circuit":
            continue
        parameters = rule.get("parameters") or {}
        model = str(parameters.get("model") or "").strip()
        if model:
            models.append(model)
    return ordered_unique(models)


def scenario_execution_fields(summary: dict[str, Any]) -> dict[str, str]:
    executed_ids: list[str] = []
    outcomes: list[str] = []
    stop_flags: list[str] = []
    for scenario in summary.get("scenarios") or []:
        if not isinstance(scenario, dict) or scenario.get("registry_status") != "executed":
            continue
        executed_ids.append(str(scenario.get("scenario_id") or ""))
        execution = scenario.get("execution") or {}
        diagnostic = execution.get("diagnostic_outcome") or {}
        outcome = str(diagnostic.get("status") or "").strip()
        if outcome:
            outcomes.append(outcome)
        if diagnostic.get("stop_automation") is not None:
            stop_flags.append(bool_text(diagnostic.get("stop_automation")))
    return {
        "executed_scenario_ids": "|".join(executed_ids),
        "internal_scenario_outcomes": "|".join(outcomes),
        "internal_stop_automation_flags": "|".join(stop_flags),
    }


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def yaml_string(value: str) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def render_reference_template(circuit: dict[str, Any]) -> str:
    component_types = str(circuit["component_types"]).split("|") if circuit["component_types"] else []
    analysis = str(circuit["analysis_types"]).split("|") if circuit["analysis_types"] else []
    lines = [
        "schema_version: 1",
        f"circuit_id: {yaml_string(circuit['circuit_id'])}",
        "review_status: draft",
        'circuit_description: ""',
        'task_type: ""',
        "user_symptom: |",
    ]
    question = str(circuit["chat_question"] or circuit["agent_question"] or "")
    question_lines = question.splitlines() or [""]
    lines.extend(f"  {line}" for line in question_lines)
    lines.extend(
        [
            "",
            "circuit_inventory:",
            f"  component_count: {circuit['component_count']}",
            f"  node_count: {circuit['node_count']}",
            "  component_types:",
        ]
    )
    lines.extend(f"    - {yaml_string(item)}" for item in component_types)
    lines.append("  analysis_types:")
    lines.extend(f"    - {yaml_string(item)}" for item in analysis)
    lines.extend(
        [
            "",
            "required_evidence: []",
            "success_conditions: []",
            "acceptable_solutions: []",
            "unsupported_conclusions: []",
            'review_notes: ""',
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genera catalogo, metriche grezze e template di riferimento dai summary congelati."
    )
    parser.add_argument("--evaluation-dir", type=Path, default=DEFAULT_EVALUATION_DIR)
    parser.add_argument("--dataset-dir", type=Path, default=DEFAULT_DATASET_DIR)
    parser.add_argument("--references-dir", type=Path, default=DEFAULT_REFERENCES_DIR)
    parser.add_argument(
        "--force-reference-templates",
        action="store_true",
        help="Sovrascrive anche schede di riferimento già esistenti.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    evaluation_dir = args.evaluation_dir.resolve()
    dataset_dir = args.dataset_dir.resolve()
    references_dir = args.references_dir.resolve()

    if not evaluation_dir.is_dir():
        raise FileNotFoundError(f"Cartella evaluation non trovata: {evaluation_dir}")

    circuit_rows: list[dict[str, Any]] = []
    component_rows: list[dict[str, Any]] = []
    run_rows: list[dict[str, Any]] = []

    circuit_dirs = sorted(
        (path for path in evaluation_dir.iterdir() if path.is_dir()),
        key=lambda path: path.name.casefold(),
    )
    if not circuit_dirs:
        raise ValueError("Nessun circuito trovato.")

    for circuit_dir in circuit_dirs:
        summaries: dict[str, dict[str, Any]] = {}
        summary_paths: dict[str, Path] = {}
        for mode in MODES:
            path = circuit_dir / f"{mode}_summary.json"
            if not path.is_file():
                raise FileNotFoundError(f"Summary mancante: {path}")
            summary = read_json(path)
            case = summary.get("case") or {}
            if case.get("circuit_id") != circuit_dir.name:
                raise ValueError(f"ID circuito incoerente in {path}")
            if case.get("mode") != mode:
                raise ValueError(f"Modalità incoerente in {path}")
            summaries[mode] = summary
            summary_paths[mode] = path

        chat = summaries["chat"]
        agent = summaries["agent"]
        graph_components = (chat.get("base_evidence") or {}).get("graph", {}).get("components") or []
        class_counter = Counter(
            str(component.get("class_name") or "Unknown")
            for component in graph_components
            if isinstance(component, dict)
        )
        component_ids_by_class: dict[str, list[str]] = {}
        for component in graph_components:
            if not isinstance(component, dict):
                continue
            class_name = str(component.get("class_name") or "Unknown")
            component_ids_by_class.setdefault(class_name, []).append(
                str(component.get("component_id") or "")
            )

        node_stats = (chat.get("base_evidence") or {}).get("node_map", {}).get("stats") or {}
        analyses = analysis_types(chat)
        ic_models = integrated_circuit_models(chat)
        chat_question = str((chat.get("case") or {}).get("symptom") or "")
        agent_question = str((agent.get("case") or {}).get("symptom") or "")

        circuit_row = {
            "circuit_id": circuit_dir.name,
            "circuit_description": "",
            "chat_question": chat_question,
            "agent_question": agent_question,
            "same_initial_question": bool_text(chat_question == agent_question),
            "component_count": len(graph_components),
            "node_count": int(node_stats.get("nodes_count") or 0),
            "component_type_count": len(class_counter),
            "component_types": "|".join(sorted(class_counter, key=str.casefold)),
            "analysis_types": "|".join(analyses),
            "has_integrated_circuit": bool_text("Integrated_Circuit" in class_counter),
            "integrated_circuit_models": "|".join(ic_models),
        }
        circuit_rows.append(circuit_row)

        for class_name in sorted(class_counter, key=str.casefold):
            component_rows.append(
                {
                    "circuit_id": circuit_dir.name,
                    "component_class": class_name,
                    "count": class_counter[class_name],
                    "component_ids": "|".join(component_ids_by_class[class_name]),
                }
            )

        for mode in MODES:
            summary = summaries[mode]
            execution = summary.get("execution") or {}
            final = summary.get("final") or {}
            scenario_fields = scenario_execution_fields(summary)
            user_turns = int(execution.get("user_turns_count") or 0)
            final_text = final.get("response") if mode == "chat" else final.get("answer")
            best_verified = final.get("best_verified_scenario") or {}
            run_rows.append(
                {
                    "circuit_id": circuit_dir.name,
                    "mode": mode,
                    "model": execution.get("model") or "",
                    "summary_generated_at": summary.get("generated_at") or "",
                    "summary_sha256": sha256_file(summary_paths[mode]),
                    "initial_question": str((summary.get("case") or {}).get("symptom") or ""),
                    "scenarios_proposed": int(execution.get("scenarios_proposed") or 0),
                    "scenarios_executed": int(execution.get("scenarios_executed") or 0),
                    "successful_spice_runs": int(execution.get("successful_spice_runs") or 0),
                    "failed_spice_runs": int(execution.get("failed_spice_runs") or 0),
                    "all_executed_spice_runs_successful": bool_text(
                        int(execution.get("scenarios_executed") or 0)
                        == int(execution.get("successful_spice_runs") or 0)
                        and int(execution.get("failed_spice_runs") or 0) == 0
                    ),
                    "internal_resolved_candidate_count": int(
                        execution.get("resolved_candidate_scenarios") or 0
                    ),
                    "turns_count": int(execution.get("turns_count") or 0),
                    "user_turns_count": user_turns,
                    "intermediate_user_turns": max(user_turns - 1, 0) if mode == "chat" else 0,
                    "assistant_turns_count": int(execution.get("assistant_turns_count") or 0),
                    "agent_decisions_count": int(execution.get("agent_decisions_count") or 0),
                    "max_agent_decisions": int(execution.get("max_agent_decisions") or 0),
                    "max_executable_scenarios": int(execution.get("max_executable_scenarios") or 0),
                    "stop_reason": execution.get("stop_reason") or "",
                    "final_status": final.get("status") or "",
                    "final_response_present": bool_text(bool(str(final_text or "").strip())),
                    "final_declares_verified_correction": bool_text(
                        bool(str(final.get("verified_correction") or "").strip())
                    ),
                    "best_verified_scenario_available": bool_text(
                        bool(best_verified.get("available"))
                    ),
                    **scenario_fields,
                    "summary_relative_path": summary_paths[mode].relative_to(SCRIPT_DIR).as_posix(),
                }
            )

    write_csv(
        dataset_dir / "circuits.csv",
        [
            "circuit_id",
            "circuit_description",
            "chat_question",
            "agent_question",
            "same_initial_question",
            "component_count",
            "node_count",
            "component_type_count",
            "component_types",
            "analysis_types",
            "has_integrated_circuit",
            "integrated_circuit_models",
        ],
        circuit_rows,
    )
    write_csv(
        dataset_dir / "components.csv",
        ["circuit_id", "component_class", "count", "component_ids"],
        component_rows,
    )
    write_csv(
        dataset_dir / "runs.csv",
        [
            "circuit_id",
            "mode",
            "model",
            "summary_generated_at",
            "summary_sha256",
            "initial_question",
            "scenarios_proposed",
            "scenarios_executed",
            "successful_spice_runs",
            "failed_spice_runs",
            "all_executed_spice_runs_successful",
            "internal_resolved_candidate_count",
            "turns_count",
            "user_turns_count",
            "intermediate_user_turns",
            "assistant_turns_count",
            "agent_decisions_count",
            "max_agent_decisions",
            "max_executable_scenarios",
            "stop_reason",
            "final_status",
            "final_response_present",
            "final_declares_verified_correction",
            "best_verified_scenario_available",
            "executed_scenario_ids",
            "internal_scenario_outcomes",
            "internal_stop_automation_flags",
            "summary_relative_path",
        ],
        run_rows,
    )

    references_dir.mkdir(parents=True, exist_ok=True)
    created_templates = 0
    preserved_templates = 0
    for circuit in circuit_rows:
        path = references_dir / f"{circuit['circuit_id']}.yaml"
        if path.exists() and not args.force_reference_templates:
            preserved_templates += 1
            continue
        path.write_text(render_reference_template(circuit), encoding="utf-8")
        created_templates += 1

    print(f"Circuiti: {len(circuit_rows)}")
    print(f"Esecuzioni: {len(run_rows)}")
    print(f"Righe componenti: {len(component_rows)}")
    print(f"Template creati/aggiornati: {created_templates}")
    print(f"Template preservati: {preserved_templates}")
    print(f"Dataset: {dataset_dir}")
    print(f"References: {references_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
