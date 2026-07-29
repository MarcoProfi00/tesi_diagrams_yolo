#!/usr/bin/env python3
"""Aggrega le valutazioni ufficiali CHAT e AGENT.

Lo script legge esclusivamente le sottocartelle dirette di ``evaluation``:
cartelle esterne come ``retries`` non possono quindi entrare accidentalmente
nei risultati ufficiali. Prima di aggregare verifica completezza, metadati,
hash dei summary e coerenza dei punteggi.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_EVALUATION_DIR = SCRIPT_DIR / "evaluation"
DEFAULT_OUTPUT_DIR = SCRIPT_DIR / "_aggregate"

MODES = ("chat", "agent")
CRITERIA = (
    "task_achievement",
    "technical_correctness",
    "scenario_quality",
    "evidence_interpretation",
    "conclusion_quality",
)
CRITERION_DESCRIPTIONS = {
    "task_achievement": "Quanto è stato raggiunto l'obiettivo richiesto dall'utente.",
    "technical_correctness": "Correttezza elettrica e diagnostica della risposta.",
    "scenario_quality": "Pertinenza e utilità degli scenari di verifica scelti.",
    "evidence_interpretation": "Coerenza delle conclusioni con le misure SPICE ottenute.",
    "conclusion_quality": "Chiarezza, completezza e solidità della conclusione finale.",
}
CRITICAL_ERRORS = (
    "false_success",
    "unsupported_claims",
    "wrong_interpretation",
)
OUTCOMES = ("success", "partial_success", "failure", "inconclusive")


class AggregationError(ValueError):
    """Indica dati ufficiali mancanti o incoerenti."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Valida e aggrega i judge ufficiali CHAT/AGENT."
    )
    parser.add_argument(
        "--evaluation-dir",
        type=Path,
        default=DEFAULT_EVALUATION_DIR,
        help="Cartella con una sottocartella per circuito.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Destinazione dei CSV, del JSON e del report Markdown.",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise AggregationError(f"File mancante: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AggregationError(f"JSON non leggibile: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise AggregationError(f"Il JSON deve essere un oggetto: {path}")
    return data


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_mapping(parent: dict[str, Any], key: str, source: Path) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        raise AggregationError(f"Blocco '{key}' mancante o non valido: {source}")
    return value


def require_int(value: Any, label: str, source: Path) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise AggregationError(f"'{label}' deve essere un intero: {source}")
    return value


def integer_or_zero(value: Any) -> int:
    return int(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else 0


def bool_int(value: Any) -> int:
    return int(value is True)


def text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def discover_circuits(evaluation_dir: Path) -> list[str]:
    if not evaluation_dir.is_dir():
        raise AggregationError(f"Cartella evaluation inesistente: {evaluation_dir}")

    circuits: list[str] = []
    for child in evaluation_dir.iterdir():
        if not child.is_dir():
            continue
        if any((child / f"{mode}_judge.json").is_file() for mode in MODES):
            circuits.append(child.name)

    circuits.sort(key=str.casefold)
    if not circuits:
        raise AggregationError(f"Nessun judge trovato in {evaluation_dir}")
    return circuits


def extract_run(
    circuit_id: str,
    mode: str,
    summary_path: Path,
    judge_path: Path,
) -> dict[str, Any]:
    summary = load_json(summary_path)
    judge = load_json(judge_path)

    case = require_mapping(summary, "case", summary_path)
    execution = require_mapping(summary, "execution", summary_path)
    metadata = require_mapping(judge, "metadata", judge_path)
    task = require_mapping(judge, "task", judge_path)
    criteria = require_mapping(judge, "criteria", judge_path)
    critical_errors = require_mapping(judge, "critical_errors", judge_path)
    computed_score = require_mapping(judge, "computed_score", judge_path)

    expected_identity = {
        "summary case.circuit_id": case.get("circuit_id"),
        "summary case.mode": case.get("mode"),
        "judge metadata.circuit_id": metadata.get("circuit_id"),
        "judge metadata.mode": metadata.get("mode"),
    }
    expected_values = {
        "summary case.circuit_id": circuit_id,
        "summary case.mode": mode,
        "judge metadata.circuit_id": circuit_id,
        "judge metadata.mode": mode,
    }
    for label, actual in expected_identity.items():
        if actual != expected_values[label]:
            raise AggregationError(
                f"Identita incoerente per {label}: atteso "
                f"{expected_values[label]!r}, trovato {actual!r} in {judge_path.parent}"
            )

    recorded_hash = text(metadata.get("summary_sha256"))
    actual_hash = sha256_file(summary_path)
    if not recorded_hash or recorded_hash != actual_hash:
        raise AggregationError(
            f"Hash summary non valido per {circuit_id}/{mode}: "
            f"registrato={recorded_hash or '<mancante>'}, attuale={actual_hash}"
        )

    criterion_scores: dict[str, int] = {}
    criterion_reasons: dict[str, str] = {}
    for criterion in CRITERIA:
        block = require_mapping(criteria, criterion, judge_path)
        score = require_int(block.get("score"), f"criteria.{criterion}.score", judge_path)
        if not 0 <= score <= 4:
            raise AggregationError(
                f"Punteggio fuori intervallo per {circuit_id}/{mode}/{criterion}: {score}"
            )
        criterion_scores[criterion] = score
        criterion_reasons[criterion] = text(block.get("reason"))

    total = require_int(
        computed_score.get("weighted_total"),
        "computed_score.weighted_total",
        judge_path,
    )
    maximum = require_int(
        computed_score.get("maximum"),
        "computed_score.maximum",
        judge_path,
    )
    calculated_total = sum(criterion_scores.values()) * 5
    if maximum != 100 or total != calculated_total:
        raise AggregationError(
            f"Totale incoerente per {circuit_id}/{mode}: "
            f"salvato={total}/{maximum}, ricalcolato={calculated_total}/100"
        )

    task_type = text(task.get("type"))
    outcome = text(task.get("outcome"))
    if not task_type:
        raise AggregationError(f"Tipo di compito mancante: {judge_path}")
    if outcome not in OUTCOMES:
        raise AggregationError(f"Esito non valido in {judge_path}: {outcome!r}")

    critical_present: dict[str, int] = {}
    critical_reasons: dict[str, str] = {}
    for error_name in CRITICAL_ERRORS:
        block = require_mapping(critical_errors, error_name, judge_path)
        if not isinstance(block.get("present"), bool):
            raise AggregationError(
                f"critical_errors.{error_name}.present non booleano: {judge_path}"
            )
        critical_present[error_name] = bool_int(block.get("present"))
        critical_reasons[error_name] = text(block.get("reason"))

    final = summary.get("final") if isinstance(summary.get("final"), dict) else {}
    scenarios = summary.get("scenarios")
    if not isinstance(scenarios, list):
        raise AggregationError(f"Lista scenarios mancante: {summary_path}")

    row: dict[str, Any] = {
        "circuit_id": circuit_id,
        "batch": text(case.get("batch")),
        "mode": mode,
        "system_model": text(execution.get("model")),
        "judge_model": text(metadata.get("judge_model")),
        "reasoning_effort": text(metadata.get("reasoning_effort")),
        "prompt_version": text(metadata.get("prompt_version")),
        "prompt_sha256": text(metadata.get("prompt_sha256")),
        "response_schema_sha256": text(metadata.get("response_schema_sha256")),
        "packet_schema_version": metadata.get("packet_schema_version", ""),
        "packet_sha256": text(metadata.get("packet_sha256")),
        "summary_sha256": recorded_hash,
        "summary_hash_valid": 1,
        "task_type": task_type,
        "outcome": outcome,
        "outcome_reason": text(task.get("outcome_reason")),
        "score_total": total,
        "critical_error_count": sum(critical_present.values()),
        "evidence_count": len(judge.get("evidence") or []),
        "final_assessment": text(judge.get("final_assessment")),
        "symptom": text(case.get("symptom")),
        "scenarios_proposed": integer_or_zero(execution.get("scenarios_proposed")),
        "scenarios_executed": integer_or_zero(execution.get("scenarios_executed")),
        "successful_spice_runs": integer_or_zero(
            execution.get("successful_spice_runs")
        ),
        "failed_spice_runs": integer_or_zero(execution.get("failed_spice_runs")),
        "resolved_candidate_scenarios": integer_or_zero(
            execution.get("resolved_candidate_scenarios")
        ),
        "turns_count": integer_or_zero(execution.get("turns_count")),
        "user_turns_count": integer_or_zero(execution.get("user_turns_count")),
        "assistant_turns_count": integer_or_zero(
            execution.get("assistant_turns_count")
        ),
        "agent_decisions_count": integer_or_zero(
            execution.get("agent_decisions_count")
        ),
        "agent_stop_reason": text(execution.get("stop_reason")),
        "final_status": text(final.get("status")),
        "verified_correction_present": bool_int(
            bool(text(final.get("verified_correction")).strip())
        ),
        "best_verified_scenario_present": bool_int(
            bool(final.get("best_verified_scenario"))
        ),
        "summary_generated_at": text(summary.get("generated_at")),
    }
    for criterion in CRITERIA:
        row[f"{criterion}_score"] = criterion_scores[criterion]
        row[f"{criterion}_reason"] = criterion_reasons[criterion]
    for error_name in CRITICAL_ERRORS:
        row[f"{error_name}_present"] = critical_present[error_name]
        row[f"{error_name}_reason"] = critical_reasons[error_name]
    return row


def validate_protocol_uniformity(rows: list[dict[str, Any]]) -> None:
    fields = (
        "system_model",
        "judge_model",
        "reasoning_effort",
        "prompt_version",
        "prompt_sha256",
        "response_schema_sha256",
        "packet_schema_version",
    )
    for field in fields:
        values = {row[field] for row in rows}
        if len(values) != 1:
            formatted = ", ".join(sorted(map(str, values)))
            raise AggregationError(
                f"Protocollo non uniforme per '{field}': {formatted}"
            )


def build_pairs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_circuit: dict[str, dict[str, dict[str, Any]]] = {}
    for row in rows:
        by_circuit.setdefault(row["circuit_id"], {})[row["mode"]] = row

    pairs: list[dict[str, Any]] = []
    for circuit_id in sorted(by_circuit, key=str.casefold):
        modes = by_circuit[circuit_id]
        missing = [mode for mode in MODES if mode not in modes]
        if missing:
            raise AggregationError(
                f"Modalita mancanti per {circuit_id}: {', '.join(missing)}"
            )
        chat = modes["chat"]
        agent = modes["agent"]
        if chat["task_type"] != agent["task_type"]:
            raise AggregationError(
                f"Task type diverso tra CHAT e AGENT per {circuit_id}"
            )

        difference = agent["score_total"] - chat["score_total"]
        winner = "agent" if difference > 0 else "chat" if difference < 0 else "tie"
        pair: dict[str, Any] = {
            "circuit_id": circuit_id,
            "batch": chat["batch"],
            "task_type": chat["task_type"],
            "same_initial_text": int(chat["symptom"] == agent["symptom"]),
            "chat_score": chat["score_total"],
            "agent_score": agent["score_total"],
            "agent_minus_chat": difference,
            "winner": winner,
            "chat_outcome": chat["outcome"],
            "agent_outcome": agent["outcome"],
            "chat_critical_error_count": chat["critical_error_count"],
            "agent_critical_error_count": agent["critical_error_count"],
            "chat_scenarios_proposed": chat["scenarios_proposed"],
            "agent_scenarios_proposed": agent["scenarios_proposed"],
            "chat_scenarios_executed": chat["scenarios_executed"],
            "agent_scenarios_executed": agent["scenarios_executed"],
            "chat_successful_spice_runs": chat["successful_spice_runs"],
            "agent_successful_spice_runs": agent["successful_spice_runs"],
            "chat_failed_spice_runs": chat["failed_spice_runs"],
            "agent_failed_spice_runs": agent["failed_spice_runs"],
            "chat_user_turns": chat["user_turns_count"],
            "agent_decisions": agent["agent_decisions_count"],
        }
        for criterion in CRITERIA:
            chat_score = chat[f"{criterion}_score"]
            agent_score = agent[f"{criterion}_score"]
            pair[f"chat_{criterion}"] = chat_score
            pair[f"agent_{criterion}"] = agent_score
            pair[f"diff_{criterion}"] = agent_score - chat_score
        pairs.append(pair)
    return pairs


def safe_mean(values: Iterable[float]) -> float:
    items = list(values)
    return statistics.fmean(items) if items else 0.0


def safe_median(values: Iterable[float]) -> float:
    items = list(values)
    return statistics.median(items) if items else 0.0


def safe_sample_sd(values: Iterable[float]) -> float:
    items = list(values)
    return statistics.stdev(items) if len(items) > 1 else 0.0


def rounded(value: float) -> float:
    return round(value, 4)


def mode_summary_rows(
    rows: list[dict[str, Any]],
    sets: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    lookup = {(row["circuit_id"], row["mode"]): row for row in rows}
    output: list[dict[str, Any]] = []
    for set_name, pairs in sets.items():
        circuit_ids = {pair["circuit_id"] for pair in pairs}
        for mode in MODES:
            selected = [
                lookup[(circuit_id, mode)]
                for circuit_id in sorted(circuit_ids, key=str.casefold)
            ]
            scores = [row["score_total"] for row in selected]
            outcomes = Counter(row["outcome"] for row in selected)
            output.append(
                {
                    "analysis_set": set_name,
                    "mode": mode,
                    "n": len(selected),
                    "score_mean": rounded(safe_mean(scores)),
                    "score_median": rounded(safe_median(scores)),
                    "score_sample_sd": rounded(safe_sample_sd(scores)),
                    "score_min": min(scores),
                    "score_max": max(scores),
                    "success_count": outcomes["success"],
                    "partial_success_count": outcomes["partial_success"],
                    "failure_count": outcomes["failure"],
                    "inconclusive_count": outcomes["inconclusive"],
                    "success_rate": rounded(
                        outcomes["success"] / len(selected) if selected else 0.0
                    ),
                    "mean_scenarios_proposed": rounded(
                        safe_mean(row["scenarios_proposed"] for row in selected)
                    ),
                    "mean_scenarios_executed": rounded(
                        safe_mean(row["scenarios_executed"] for row in selected)
                    ),
                    "successful_spice_runs_total": sum(
                        row["successful_spice_runs"] for row in selected
                    ),
                    "failed_spice_runs_total": sum(
                        row["failed_spice_runs"] for row in selected
                    ),
                    "mean_critical_error_count": rounded(
                        safe_mean(row["critical_error_count"] for row in selected)
                    ),
                    "mean_user_turns": rounded(
                        safe_mean(row["user_turns_count"] for row in selected)
                    ),
                    "mean_agent_decisions": rounded(
                        safe_mean(row["agent_decisions_count"] for row in selected)
                    ),
                }
            )
    return output


def paired_summary_rows(
    sets: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for set_name, pairs in sets.items():
        differences = [pair["agent_minus_chat"] for pair in pairs]
        output.append(
            {
                "analysis_set": set_name,
                "n_pairs": len(pairs),
                "chat_score_mean": rounded(
                    safe_mean(pair["chat_score"] for pair in pairs)
                ),
                "agent_score_mean": rounded(
                    safe_mean(pair["agent_score"] for pair in pairs)
                ),
                "mean_agent_minus_chat": rounded(safe_mean(differences)),
                "median_agent_minus_chat": rounded(safe_median(differences)),
                "difference_sample_sd": rounded(safe_sample_sd(differences)),
                "agent_wins": sum(pair["winner"] == "agent" for pair in pairs),
                "ties": sum(pair["winner"] == "tie" for pair in pairs),
                "chat_wins": sum(pair["winner"] == "chat" for pair in pairs),
                "same_initial_text_pairs": sum(
                    pair["same_initial_text"] for pair in pairs
                ),
            }
        )
    return output


def criteria_summary_rows(
    rows: list[dict[str, Any]],
    sets: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    lookup = {(row["circuit_id"], row["mode"]): row for row in rows}
    output: list[dict[str, Any]] = []
    for set_name, pairs in sets.items():
        circuit_ids = {pair["circuit_id"] for pair in pairs}
        for mode in MODES:
            selected = [lookup[(circuit_id, mode)] for circuit_id in circuit_ids]
            for criterion in CRITERIA:
                scores = [row[f"{criterion}_score"] for row in selected]
                output.append(
                    {
                        "analysis_set": set_name,
                        "mode": mode,
                        "criterion": criterion,
                        "criterion_description": CRITERION_DESCRIPTIONS[criterion],
                        "n": len(scores),
                        "mean_score_0_4": rounded(safe_mean(scores)),
                        "mean_score_0_100": rounded(safe_mean(scores) * 25),
                        "median_score_0_4": rounded(safe_median(scores)),
                        "sample_sd_0_4": rounded(safe_sample_sd(scores)),
                    }
                )
    return output


def outcome_count_rows(
    rows: list[dict[str, Any]],
    sets: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    lookup = {(row["circuit_id"], row["mode"]): row for row in rows}
    output: list[dict[str, Any]] = []
    for set_name, pairs in sets.items():
        circuit_ids = {pair["circuit_id"] for pair in pairs}
        for mode in MODES:
            selected = [lookup[(circuit_id, mode)] for circuit_id in circuit_ids]
            counts = Counter(row["outcome"] for row in selected)
            for outcome in OUTCOMES:
                count = counts[outcome]
                output.append(
                    {
                        "analysis_set": set_name,
                        "mode": mode,
                        "outcome": outcome,
                        "count": count,
                        "rate": rounded(count / len(selected) if selected else 0.0),
                    }
                )
    return output


def critical_error_count_rows(
    rows: list[dict[str, Any]],
    sets: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    lookup = {(row["circuit_id"], row["mode"]): row for row in rows}
    output: list[dict[str, Any]] = []
    for set_name, pairs in sets.items():
        circuit_ids = {pair["circuit_id"] for pair in pairs}
        for mode in MODES:
            selected = [lookup[(circuit_id, mode)] for circuit_id in circuit_ids]
            for error_name in CRITICAL_ERRORS:
                count = sum(row[f"{error_name}_present"] for row in selected)
                output.append(
                    {
                        "analysis_set": set_name,
                        "mode": mode,
                        "critical_error": error_name,
                        "evaluations_with_error": count,
                        "rate": rounded(count / len(selected) if selected else 0.0),
                    }
                )
    return output


def criteria_long_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in rows:
        for criterion in CRITERIA:
            output.append(
                {
                    "circuit_id": row["circuit_id"],
                    "mode": row["mode"],
                    "task_type": row["task_type"],
                    "criterion": criterion,
                    "criterion_description": CRITERION_DESCRIPTIONS[criterion],
                    "score_0_4": row[f"{criterion}_score"],
                    "score_0_100": row[f"{criterion}_score"] * 25,
                    "reason": row[f"{criterion}_reason"],
                }
            )
    return output


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise AggregationError(f"Nessuna riga da scrivere in {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def format_number(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def build_report(
    circuits: list[str],
    mode_summaries: list[dict[str, Any]],
    paired_summaries: list[dict[str, Any]],
    criteria_summaries: list[dict[str, Any]],
    pairs: list[dict[str, Any]],
    sets: dict[str, list[dict[str, Any]]],
) -> str:
    lines = [
        "# Risultati aggregati CHAT e AGENT",
        "",
        "Report generato automaticamente dai judge ufficiali. Le cartelle di "
        "retry non vengono lette.",
        "",
        f"- Circuiti ufficiali: **{len(circuits)}**",
        f"- Valutazioni ufficiali: **{len(circuits) * len(MODES)}**",
        f"- Circuiti: `{', '.join(circuits)}`",
        "",
    ]

    for set_name in sets:
        pair_summary = next(
            row for row in paired_summaries if row["analysis_set"] == set_name
        )
        selected_modes = [
            row for row in mode_summaries if row["analysis_set"] == set_name
        ]
        lines.extend(
            [
                "## Risultati complessivi",
                "",
                "| Modalità | N | Media | Mediana | Dev. std. | Successi | "
                "Parziali | Fallimenti | Scenari eseguiti medi |",
                "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for row in selected_modes:
            lines.append(
                f"| {row['mode'].upper()} | {row['n']} | "
                f"{format_number(row['score_mean'])} | "
                f"{format_number(row['score_median'])} | "
                f"{format_number(row['score_sample_sd'])} | "
                f"{row['success_count']} | {row['partial_success_count']} | "
                f"{row['failure_count']} | "
                f"{format_number(row['mean_scenarios_executed'])} |"
            )
        lines.extend(
            [
                "",
                f"- Differenza media AGENT − CHAT: "
                f"**{format_number(pair_summary['mean_agent_minus_chat'])}** punti.",
                f"- Vittorie AGENT / pareggi / vittorie CHAT: "
                f"**{pair_summary['agent_wins']} / {pair_summary['ties']} / "
                f"{pair_summary['chat_wins']}**.",
                "",
                "| Criterio | Significato | CHAT (0–4) | AGENT (0–4) |",
                "|---|---|---:|---:|",
            ]
        )
        for criterion in CRITERIA:
            chat = next(
                row
                for row in criteria_summaries
                if row["analysis_set"] == set_name
                and row["mode"] == "chat"
                and row["criterion"] == criterion
            )
            agent = next(
                row
                for row in criteria_summaries
                if row["analysis_set"] == set_name
                and row["mode"] == "agent"
                and row["criterion"] == criterion
            )
            lines.append(
                f"| {criterion} | {CRITERION_DESCRIPTIONS[criterion]} | "
                f"{format_number(chat['mean_score_0_4'])} | "
                f"{format_number(agent['mean_score_0_4'])} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Confronto per circuito",
            "",
            "| Circuito | CHAT | AGENT | Δ AGENT−CHAT | Vincitore | "
            "Esito CHAT | Esito AGENT |",
            "|---|---:|---:|---:|---|---|---|",
        ]
    )
    for pair in pairs:
        lines.append(
            f"| {pair['circuit_id']} | {pair['chat_score']} | "
            f"{pair['agent_score']} | {pair['agent_minus_chat']:+d} | "
            f"{pair['winner']} | {pair['chat_outcome']} | "
            f"{pair['agent_outcome']} |"
        )

    lines.extend(
        [
            "",
            "## File prodotti",
            "",
            "- `runs.csv`: una riga per valutazione, con dati numerici e motivazioni.",
            "- `pairs.csv`: confronto appaiato CHAT–AGENT per circuito.",
            "- `criteria_long.csv`: formato lungo per grafici dei criteri.",
            "- `mode_summary.csv`: statistiche descrittive per modalità.",
            "- `paired_summary.csv`: differenze e vittorie appaiate.",
            "- `criteria_summary.csv`: medie dei cinque criteri.",
            "- `outcome_counts.csv`: distribuzione degli esiti.",
            "- `critical_error_counts.csv`: frequenza degli errori critici.",
            "- `aggregate_results.json`: copia strutturata di tutte le aggregazioni.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    evaluation_dir = args.evaluation_dir.resolve()
    output_dir = args.output_dir.resolve()

    circuits = discover_circuits(evaluation_dir)
    rows: list[dict[str, Any]] = []
    for circuit_id in circuits:
        circuit_dir = evaluation_dir / circuit_id
        for mode in MODES:
            rows.append(
                extract_run(
                    circuit_id,
                    mode,
                    circuit_dir / f"{mode}_summary.json",
                    circuit_dir / f"{mode}_judge.json",
                )
            )

    validate_protocol_uniformity(rows)
    pairs = build_pairs(rows)
    sets = {"all": pairs}
    mode_summaries = mode_summary_rows(rows, sets)
    paired_summaries = paired_summary_rows(sets)
    criteria_summaries = criteria_summary_rows(rows, sets)
    outcome_counts = outcome_count_rows(rows, sets)
    critical_error_counts = critical_error_count_rows(rows, sets)
    criteria_long = criteria_long_rows(rows)

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "runs.csv", rows)
    write_csv(output_dir / "pairs.csv", pairs)
    write_csv(output_dir / "criteria_long.csv", criteria_long)
    write_csv(output_dir / "mode_summary.csv", mode_summaries)
    write_csv(output_dir / "paired_summary.csv", paired_summaries)
    write_csv(output_dir / "criteria_summary.csv", criteria_summaries)
    write_csv(output_dir / "outcome_counts.csv", outcome_counts)
    write_csv(output_dir / "critical_error_counts.csv", critical_error_counts)

    aggregate_json = {
        "source": {
            "evaluation_dir": str(evaluation_dir),
            "circuits": circuits,
            "circuit_count": len(circuits),
            "evaluation_count": len(rows),
            "modes": list(MODES),
            "retries_included": False,
        },
        "protocol": {
            field: rows[0][field]
            for field in (
                "system_model",
                "judge_model",
                "reasoning_effort",
                "prompt_version",
                "prompt_sha256",
                "response_schema_sha256",
                "packet_schema_version",
            )
        },
        "runs": rows,
        "pairs": pairs,
        "mode_summary": mode_summaries,
        "paired_summary": paired_summaries,
        "criteria_summary": criteria_summaries,
        "outcome_counts": outcome_counts,
        "critical_error_counts": critical_error_counts,
    }
    (output_dir / "aggregate_results.json").write_text(
        json.dumps(aggregate_json, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output_dir / "report.md").write_text(
        build_report(
            circuits,
            mode_summaries,
            paired_summaries,
            criteria_summaries,
            pairs,
            sets,
        ),
        encoding="utf-8",
    )

    print(f"Validazione completata: {len(circuits)} circuiti, {len(rows)} judge.")
    print(f"Retry inclusi: no")
    print(f"Output: {output_dir}")
    for summary in paired_summaries:
        print(
            f"{summary['analysis_set']}: CHAT={summary['chat_score_mean']:.2f}, "
            f"AGENT={summary['agent_score_mean']:.2f}, "
            f"delta={summary['mean_agent_minus_chat']:.2f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
