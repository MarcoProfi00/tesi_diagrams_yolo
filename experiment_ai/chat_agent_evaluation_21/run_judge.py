#!/usr/bin/env python3
"""Valuta uno o entrambi i pacchetti di un circuito con un judge esterno."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import time
from typing import Any


ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parents[1]
INPUT_DIR = ROOT / "judge_inputs"
OUTPUT_DIR = ROOT / "judge_results"
PROMPT_PATH = ROOT / "protocol" / "judge_prompt.md"
SCHEMA_PATH = ROOT / "protocol" / "judge_response_schema.json"
MODES = ("chat", "agent")
CRITERIA = (
    "diagnostic_correctness",
    "test_quality",
    "evidence_interpretation",
    "goal_achievement",
    "conclusion_quality",
)
OUTCOMES = (
    "success",
    "partial_success",
    "failure",
    "inconclusive",
    "technical_failure",
)
CRITICAL_ERRORS = (
    "false_success",
    "unsupported_claim",
    "wrong_interpretation",
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_env() -> None:
    for path in (PROJECT_ROOT / ".env", PROJECT_ROOT / "scripts" / "GPT" / ".env"):
        if not path.exists():
            continue
        for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            if key and key not in os.environ:
                os.environ[key] = value.strip().strip('"').strip("'")


def validate_response(data: Any, packet_id: str) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError("La risposta del judge deve essere un oggetto JSON")
    required = {
        "packet_id",
        "outcome",
        "outcome_reason",
        "criteria",
        "critical_errors",
        "decisive_evidence",
        "confidence",
    }
    if set(data) != required:
        raise ValueError(f"Campi judge non validi: {sorted(set(data) ^ required)}")
    if data["packet_id"] != packet_id:
        raise ValueError("Il packet_id restituito dal judge non coincide")
    if data["outcome"] not in OUTCOMES:
        raise ValueError(f"Outcome non valido: {data['outcome']}")
    if not isinstance(data["outcome_reason"], str) or not data["outcome_reason"].strip():
        raise ValueError("outcome_reason mancante")
    if not isinstance(data["criteria"], dict) or set(data["criteria"]) != set(CRITERIA):
        raise ValueError("Criteri mancanti o inattesi")
    for name in CRITERIA:
        criterion = data["criteria"][name]
        if not isinstance(criterion, dict) or set(criterion) != {"score", "reason"}:
            raise ValueError(f"Formato non valido per il criterio {name}")
        if type(criterion["score"]) is not int or criterion["score"] not in (0, 1, 2):
            raise ValueError(f"Score non valido per il criterio {name}")
        if not isinstance(criterion["reason"], str) or not criterion["reason"].strip():
            raise ValueError(f"Motivazione mancante per il criterio {name}")
    errors = data["critical_errors"]
    if not isinstance(errors, list) or len(errors) != len(set(errors)):
        raise ValueError("critical_errors deve essere una lista senza duplicati")
    if any(item not in CRITICAL_ERRORS for item in errors):
        raise ValueError("critical_errors contiene un valore non valido")
    evidence = data["decisive_evidence"]
    if not isinstance(evidence, list) or not 1 <= len(evidence) <= 5:
        raise ValueError("decisive_evidence deve contenere da 1 a 5 elementi")
    if data["confidence"] not in ("high", "medium", "low"):
        raise ValueError("confidence non valida")
    return data


def response_schema() -> dict[str, Any]:
    schema = read_json(SCHEMA_PATH)
    schema.pop("$schema", None)
    return schema


def evaluate(
    packet: dict[str, Any],
    *,
    model: str,
    reasoning_effort: str,
    max_output_tokens: int,
) -> tuple[dict[str, Any], float, Any]:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("Pacchetto openai non installato") from exc

    load_env()
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY non trovata nei file .env o nell'ambiente")

    prompt = PROMPT_PATH.read_text(encoding="utf-8")
    request: dict[str, Any] = {
        "model": model,
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt
                        + "\n\nPACCHETTO DA VALUTARE:\n"
                        + json.dumps(packet, ensure_ascii=False, separators=(",", ":")),
                    }
                ],
            }
        ],
        "max_output_tokens": max_output_tokens,
        "text": {
            "format": {
                "type": "json_schema",
                "name": "chat_agent_evaluation_21_judge",
                "strict": True,
                "schema": response_schema(),
            }
        },
    }
    if model.startswith("gpt-5"):
        request["reasoning"] = {"effort": reasoning_effort}

    started = time.perf_counter()
    response = OpenAI().responses.create(**request)
    latency = time.perf_counter() - started
    output_text = (getattr(response, "output_text", None) or "").strip()
    if not output_text:
        raise RuntimeError("Il judge non ha restituito output_text")
    try:
        parsed_json = json.loads(output_text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Il judge ha restituito JSON incompleto o non valido "
            f"({len(output_text)} caratteri). Riprova aumentando "
            "--max-output-tokens."
        ) from exc
    parsed = validate_response(parsed_json, packet["packet_id"])
    return parsed, latency, getattr(response, "usage", None)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--circuit", required=True, help="Circuito, per esempio a01")
    parser.add_argument("--mode", choices=(*MODES, "both"), default="both")
    parser.add_argument("--run", action="store_true", help="Esegue davvero il judge")
    parser.add_argument("--judge-model", default="gpt-5.5")
    parser.add_argument(
        "--reasoning-effort",
        choices=("low", "medium", "high", "xhigh"),
        default="medium",
    )
    parser.add_argument("--max-output-tokens", type=int, default=5000)
    parser.add_argument(
        "--results-dir",
        default=str(OUTPUT_DIR),
        help=(
            "Directory dei risultati. Un percorso relativo viene risolto rispetto "
            "alla cartella chat_agent_evaluation_21."
        ),
    )
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    results_dir = Path(args.results_dir)
    if not results_dir.is_absolute():
        results_dir = ROOT / results_dir
    modes = MODES if args.mode == "both" else (args.mode,)
    for mode in modes:
        packet_path = INPUT_DIR / args.circuit / f"{mode}_packet.json"
        packet = read_json(packet_path)
        result_path = results_dir / args.circuit / f"{mode}_judge.json"
        print(
            f"{args.circuit} {mode}: {packet['packet_id']} | "
            f"{packet['run']['technical_status']} | {packet_path.stat().st_size} byte"
        )
        if not args.run:
            continue
        if result_path.exists() and not args.force:
            raise FileExistsError(f"{result_path} esiste gia'; usa --force per sostituirlo")

        judged, latency, usage = evaluate(
            packet,
            model=args.judge_model,
            reasoning_effort=args.reasoning_effort,
            max_output_tokens=args.max_output_tokens,
        )
        total = sum(judged["criteria"][name]["score"] for name in CRITERIA)
        saved = {
            "schema_version": 1,
            "metadata": {
                "circuit_id": args.circuit,
                "mode": mode,
                "judge_model": args.judge_model,
                "reasoning_effort": args.reasoning_effort,
                "latency_seconds": round(latency, 3),
                "packet_sha256": sha256(packet_path),
                "prompt_sha256": sha256(PROMPT_PATH),
                "response_schema_sha256": sha256(SCHEMA_PATH),
                "usage": str(usage),
            },
            **judged,
            "total_score": total,
            "maximum_score": 10,
        }
        result_path.parent.mkdir(parents=True, exist_ok=True)
        result_path.write_text(
            json.dumps(saved, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Salvato: {result_path.relative_to(ROOT)}")
    if not args.run:
        print("Preflight completato. Aggiungi --run per chiamare il judge.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
