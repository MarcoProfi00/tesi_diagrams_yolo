"""
Prepara cartelle esperimento per Pipeline 2.0.

La pipeline storica scrive gli output in:

outputs/pipeline2.0/<batch>/<circuit>/

Questo helper crea una root separata per esperimenti, per esempio:

outputs/pipeline2.0/<batch>/experiment2/<circuit>/

Puo anche creare varianti indipendenti dello stesso esperimento:

outputs/pipeline2.0/<batch>/experiment4/chat/<circuit>/
outputs/pipeline2.0/<batch>/experiment4/agent/<circuit>/

La copia e volutamente non distruttiva: i file gia presenti nella destinazione
non vengono sovrascritti.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import json
import re
import shutil
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PIPELINE2_ROOT = PROJECT_ROOT / "outputs" / "pipeline2.0"


def is_safe_path_name(name: str) -> bool:
    """Accetta solo nomi semplici per batch, esperimenti e circuiti."""
    return bool(re.fullmatch(r"[A-Za-z0-9_.-]+", name)) and name not in {".", ".."}


def require_safe_name(label: str, name: str) -> None:
    """Blocca nomi che potrebbero uscire dalla root attesa."""
    if not is_safe_path_name(name):
        raise SystemExit(f"Invalid {label}: {name}")


def source_circuit_dir(batch: str, circuit: str, source_experiment: str | None = None) -> Path:
    """Restituisce la cartella circuito sorgente."""
    if source_experiment:
        return PIPELINE2_ROOT / batch / source_experiment / circuit
    return PIPELINE2_ROOT / batch / circuit


def destination_circuit_dir(
    batch: str,
    experiment: str,
    circuit: str,
    destination_variant: str | None = None,
) -> Path:
    """Restituisce la cartella circuito, includendo l'eventuale variante."""
    experiment_dir = PIPELINE2_ROOT / batch / experiment
    if destination_variant:
        experiment_dir = experiment_dir / destination_variant
    return experiment_dir / circuit


def should_copy_base_file(path: Path) -> bool:
    """Seleziona gli artefatti tecnici della base run, cioe gli output 01-08."""
    return path.is_file() and bool(re.match(r"^0[1-8]_", path.name))


def copy_file_if_missing(source: Path, destination: Path, dry_run: bool) -> str:
    """Copia un file solo se manca, restituendo lo stato dell'operazione."""
    if destination.exists():
        return "skipped_existing"
    if not dry_run:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    return "copied"


def copy_tree_missing(source_dir: Path, destination_dir: Path, dry_run: bool) -> dict[str, list[str]]:
    """Copia ricorsivamente una directory, senza sovrascrivere file esistenti."""
    copied: list[str] = []
    skipped_existing: list[str] = []

    for source in sorted(path for path in source_dir.rglob("*") if path.is_file()):
        relative = source.relative_to(source_dir)
        destination = destination_dir / relative
        status = copy_file_if_missing(source, destination, dry_run)
        if status == "copied":
            copied.append(str(relative))
        else:
            skipped_existing.append(str(relative))

    return {
        "copied": copied,
        "skipped_existing": skipped_existing,
    }


def copy_base_files_missing(source_dir: Path, destination_dir: Path, dry_run: bool) -> dict[str, list[str]]:
    """Copia solo i file top-level 01-08 della base run."""
    copied: list[str] = []
    skipped_existing: list[str] = []

    for source in sorted(path for path in source_dir.iterdir() if should_copy_base_file(path)):
        destination = destination_dir / source.name
        status = copy_file_if_missing(source, destination, dry_run)
        if status == "copied":
            copied.append(source.name)
        else:
            skipped_existing.append(source.name)

    return {
        "copied": copied,
        "skipped_existing": skipped_existing,
    }


def write_experiment_manifest(
    destination_dir: Path,
    data: dict[str, Any],
    dry_run: bool,
) -> None:
    """Scrive un piccolo manifest locale dell'inizializzazione esperimento."""
    if dry_run:
        return
    destination_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = destination_dir / "experiment_manifest.json"
    manifest_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def prepare_circuit(
    batch: str,
    experiment: str,
    circuit: str,
    mode: str,
    source_experiment: str | None,
    destination_variant: str | None,
    dry_run: bool,
) -> dict[str, Any]:
    """Prepara una cartella circuito dentro un esperimento."""
    source_dir = source_circuit_dir(batch, circuit, source_experiment)
    destination_dir = destination_circuit_dir(
        batch,
        experiment,
        circuit,
        destination_variant,
    )

    if not source_dir.exists() or not source_dir.is_dir():
        raise FileNotFoundError(f"Source circuit directory not found: {source_dir}")

    if mode == "full":
        copy_result = copy_tree_missing(source_dir, destination_dir, dry_run)
    elif mode == "base-only":
        copy_result = copy_base_files_missing(source_dir, destination_dir, dry_run)
    else:
        raise ValueError(f"Unsupported mode: {mode}")

    manifest = {
        "source_format": "pipeline2.0_experiment_manifest",
        "batch": batch,
        "experiment": experiment,
        "circuit": circuit,
        "mode": mode,
        "source_experiment": source_experiment,
        "destination_variant": destination_variant,
        "source_dir": str(source_dir),
        "destination_dir": str(destination_dir),
        "copied_count": len(copy_result["copied"]),
        "skipped_existing_count": len(copy_result["skipped_existing"]),
        "dry_run": dry_run,
        "created_or_updated_at": datetime.now().isoformat(timespec="seconds"),
    }
    write_experiment_manifest(destination_dir, manifest, dry_run)

    return {
        **manifest,
        "copied": copy_result["copied"],
        "skipped_existing": copy_result["skipped_existing"],
    }


def parse_args() -> argparse.Namespace:
    """Legge argomenti CLI."""
    parser = argparse.ArgumentParser(description="Prepare isolated Pipeline 2.0 experiment outputs.")
    parser.add_argument("--batch", required=True, help="Batch name, for example batchA.")
    parser.add_argument("--experiment", required=True, help="Destination experiment name, for example experiment2.")
    parser.add_argument("--circuits", nargs="+", required=True, help="Circuit ids to prepare, for example a01 a02.")
    parser.add_argument(
        "--mode",
        choices=["base-only", "full"],
        default="base-only",
        help="base-only copies top-level 01-08 files; full copies the whole current circuit directory.",
    )
    parser.add_argument(
        "--source-experiment",
        default=None,
        help="Optional source experiment. Default source is outputs/pipeline2.0/<batch>/<circuit>/.",
    )
    parser.add_argument(
        "--destination-variant",
        default=None,
        help=(
            "Optional destination subfolder, for example chat or agent. "
            "The output becomes <batch>/<experiment>/<variant>/<circuit>/."
        ),
    )
    parser.add_argument("--dry-run", action="store_true", help="Print planned work without copying files.")
    return parser.parse_args()


def main() -> None:
    """Entry point CLI."""
    args = parse_args()
    for label, value in (
        ("batch", args.batch),
        ("experiment", args.experiment),
        *[("circuit", circuit) for circuit in args.circuits],
    ):
        require_safe_name(label, value)
    if args.source_experiment:
        require_safe_name("source_experiment", args.source_experiment)
    if args.destination_variant:
        require_safe_name("destination_variant", args.destination_variant)

    results: list[dict[str, Any]] = []
    for circuit in args.circuits:
        result = prepare_circuit(
            batch=args.batch,
            experiment=args.experiment,
            circuit=circuit,
            mode=args.mode,
            source_experiment=args.source_experiment,
            destination_variant=args.destination_variant,
            dry_run=args.dry_run,
        )
        results.append(result)
        print(
            f"{args.batch}/{args.experiment}/"
            f"{f'{args.destination_variant}/' if args.destination_variant else ''}{circuit}: "
            f"copied={result['copied_count']} skipped={result['skipped_existing_count']} "
            f"mode={args.mode}"
        )

    summary = {
        "batch": args.batch,
        "experiment": args.experiment,
        "destination_variant": args.destination_variant,
        "mode": args.mode,
        "circuits": args.circuits,
        "dry_run": args.dry_run,
        "copied_total": sum(int(result["copied_count"]) for result in results),
        "skipped_existing_total": sum(int(result["skipped_existing_count"]) for result in results),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
