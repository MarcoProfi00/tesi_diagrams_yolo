"""Helper condivisi dai test conservativi della Pipeline 2.0."""

from __future__ import annotations

from contextlib import contextmanager
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
from types import ModuleType
from typing import Any, Iterator
from uuid import uuid4


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PIPELINE2_SCRIPT_DIR = PROJECT_ROOT / "scripts" / "pipeline_2.0"
JSON_TO_SPICE_DIR = PIPELINE2_SCRIPT_DIR / "json_to_spice"
BASELINE_PATH = Path(__file__).resolve().parent / "characterization_baseline.json"
TEST_TEMP_ROOT = PROJECT_ROOT / ".tmp" / "pipeline2_tests"

VOLATILE_KEYS = {
    "created_at",
    "created_or_updated_at",
    "generated_at",
    "updated_at",
}
ISO_TIMESTAMP_PATTERN = re.compile(
    r"20\d\d-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:[+-]\d\d:\d\d|Z)?"
)
CANONICAL_PATH_PATTERN = re.compile(
    r"<(?:TEMP|PROJECT)_ROOT>(?:[\\/][^\\/\s<>\"']+)*"
)


def load_baseline() -> dict[str, Any]:
    """Carica il manifest degli hash approvati per la caratterizzazione."""
    return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))


def load_numbered_module(filename: str, module_name: str | None = None) -> ModuleType:
    """Carica uno step numerato senza modificarne il meccanismo di import reale."""
    module_path = JSON_TO_SPICE_DIR / filename
    unique_name = module_name or f"pipeline2_test_{module_path.stem}_{uuid4().hex}"
    spec = importlib.util.spec_from_file_location(unique_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Impossibile caricare il modulo di test: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def replace_path(text: str, path: Path, replacement: str) -> str:
    """Sostituisce nello stesso modo i path Windows e quelli con slash."""
    raw_path = str(path.resolve())
    replaced = text.replace(raw_path, replacement).replace(
        raw_path.replace("\\", "/"),
        replacement,
    )
    return normalize_canonical_paths(replaced)


def normalize_canonical_paths(text: str) -> str:
    """Uniforma i separatori dei soli path sostituiti con marker canonici."""
    return CANONICAL_PATH_PATTERN.sub(
        lambda match: match.group(0).replace("/", "\\"),
        text,
    )


WINDOWS_PROJECT_ROOT_PATTERN = re.compile(
    r"(?i)^[a-z]:[\\/]+(?:[^\\/]+[\\/]+)*tesi_diagrams_yolo(?=[\\/]|$)"
)


def replace_legacy_project_root(text: str) -> str:
    """Canonizza un path assoluto appartenente alla vecchia clone Windows."""
    replaced = WINDOWS_PROJECT_ROOT_PATTERN.sub("<PROJECT_ROOT>", text)
    return normalize_canonical_paths(replaced)


def canonicalize(value: Any, temporary_root: Path | None = None) -> Any:
    """Rimuove soltanto dati volatili, preservando ogni informazione tecnica."""
    if isinstance(value, dict):
        return {
            key: canonicalize(item, temporary_root)
            for key, item in value.items()
            if key not in VOLATILE_KEYS
        }
    if isinstance(value, list):
        return [canonicalize(item, temporary_root) for item in value]
    if isinstance(value, str):
        text = value
        # Il path temporaneo va sostituito prima della root, perche e contenuto
        # fisicamente nel workspace del progetto.
        if temporary_root is not None:
            text = replace_path(text, temporary_root, "<TEMP_ROOT>")
            try:
                relative_temporary_root = temporary_root.resolve().relative_to(
                    PROJECT_ROOT.resolve()
                )
            except ValueError:
                relative_temporary_root = None
            if relative_temporary_root is not None:
                relative_text = str(relative_temporary_root)
                text = text.replace(relative_text, "<TEMP_ROOT>").replace(
                    relative_text.replace("\\", "/"),
                    "<TEMP_ROOT>",
                )
        text = replace_path(text, PROJECT_ROOT, "<PROJECT_ROOT>")
        text = replace_legacy_project_root(text)
        text = normalize_canonical_paths(text)
        return ISO_TIMESTAMP_PATTERN.sub("<TIMESTAMP>", text)
    return value


def stable_digest(value: Any, temporary_root: Path | None = None) -> str:
    """Calcola un SHA-256 stabile di testo o dati JSON canonici."""
    normalized = canonicalize(value, temporary_root)
    if isinstance(normalized, str):
        payload = normalized.replace("\r\n", "\n").encode("utf-8")
    else:
        payload = json.dumps(
            normalized,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def validated_run_dir(
    batch: str,
    experiment: str,
    circuit: str,
    workspace_mode: str = "chat",
) -> Path:
    """Restituisce una run validata usata come fixture in sola lettura."""
    return (
        PROJECT_ROOT
        / "outputs"
        / "pipeline2.0"
        / batch
        / experiment
        / workspace_mode
        / circuit
    )


@contextmanager
def isolated_directory(label: str) -> Iterator[Path]:
    """Crea una directory isolata nel workspace e la elimina a fine test."""
    TEST_TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    destination = TEST_TEMP_ROOT / f"{label}_{uuid4().hex}"
    destination.mkdir(parents=True, exist_ok=False)
    try:
        yield destination
    finally:
        resolved_destination = destination.resolve()
        resolved_root = TEST_TEMP_ROOT.resolve()
        if resolved_root not in resolved_destination.parents:
            raise RuntimeError(f"Directory temporanea non sicura: {resolved_destination}")
        shutil.rmtree(resolved_destination, ignore_errors=False)


def copy_validated_run(
    batch: str,
    experiment: str,
    circuit: str,
    destination_root: Path,
    workspace_mode: str = "chat",
) -> Path:
    """Copia una run validata in una root temporanea scrivibile."""
    source = validated_run_dir(batch, experiment, circuit, workspace_mode)
    destination = (
        destination_root
        / "outputs"
        / "pipeline2.0"
        / batch
        / experiment
        / workspace_mode
        / circuit
    )
    shutil.copytree(source, destination)
    return destination
