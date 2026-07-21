"""Entry point CLI della modalita AGENT autonoma e controllata."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_agent.controller import (
    run_iteration,
    start_diagnosis,
    stop_diagnosis,
    summarize_state,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def parse_args() -> argparse.Namespace:
    """Legge i parametri necessari a una singola operazione autonoma."""
    parser = argparse.ArgumentParser(description="Controlla una diagnosi autonoma Pipeline 2.0.")
    parser.add_argument("--batch", required=True)
    parser.add_argument("--experiment", default="experiment4")
    parser.add_argument("--variant", default="agent")
    parser.add_argument("--circuit", required=True)
    parser.add_argument("--action", choices=["start", "step", "stop"], required=True)
    parser.add_argument("--symptom", default=None)
    parser.add_argument("--model", default="gpt-5.4")
    parser.add_argument("--ngspice-executable", default=None)
    return parser.parse_args()


def output_dir_from_args(args: argparse.Namespace) -> Path:
    """Calcola la root del workspace autonomo selezionato da CLI."""
    return (
        PROJECT_ROOT
        / "outputs"
        / "pipeline2.0"
        / args.batch
        / args.experiment
        / args.variant
        / args.circuit
    )


def main() -> None:
    """Esegue start, step oppure stop senza introdurre un loop implicito."""
    args = parse_args()
    output_dir = output_dir_from_args(args)
    if not output_dir.is_dir():
        raise SystemExit(f"Workspace non trovato: {output_dir}")

    if args.action == "start":
        if not args.symptom:
            raise SystemExit("--symptom e obbligatorio con --action start")
        state = start_diagnosis(output_dir, args.symptom, args.model)
    elif args.action == "stop":
        state = stop_diagnosis(output_dir)
    else:
        state = run_iteration(
            output_dir=output_dir,
            batch=args.batch,
            circuit=args.circuit,
            experiment=args.experiment,
            ngspice_executable=args.ngspice_executable,
        )

    print(json.dumps(summarize_state(state, output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
