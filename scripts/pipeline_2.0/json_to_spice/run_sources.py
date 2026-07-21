"""Risoluzione delle sorgenti esterne associate a una run Pipeline 2.0.

Il file ``pipeline2_sources.json`` permette a viewer e agente di usare
l'immagine e la geometria della stessa esecuzione Pipeline 1.0 senza dedurre
il batch dalla posizione storica sotto ``outputs/pipeline1.0``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


RUN_SOURCES_FILENAME = "pipeline2_sources.json"


def find_run_sources_path(run_dir: str | Path) -> Path | None:
    """Cerca il descrittore nella run o in una sua directory antenata.

    La risalita consente alle run scenario, annidate sotto ``scenarios/``, di
    riusare le sorgenti dichiarate dalla base CHAT o AGENT.
    """
    current = Path(run_dir).resolve()
    for directory in (current, *current.parents):
        candidate = directory / RUN_SOURCES_FILENAME
        if candidate.is_file():
            return candidate
    return None


def read_run_sources(run_dir: str | Path) -> tuple[dict[str, Any], Path | None]:
    """Legge il descrittore della run, restituendo un risultato vuoto se manca."""
    manifest_path = find_run_sources_path(run_dir)
    if manifest_path is None:
        return {}, None
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}, manifest_path
    return (data if isinstance(data, dict) else {}), manifest_path


def resolve_declared_path(manifest_path: Path | None, value: Any) -> Path | None:
    """Risolve un path assoluto o relativo alla cartella del descrittore."""
    raw_value = str(value or "").strip()
    if not raw_value:
        return None
    path = Path(raw_value)
    if not path.is_absolute():
        if manifest_path is None:
            return None
        path = manifest_path.parent / path
    return path.resolve()


def get_run_source_path(run_dir: str | Path, *keys: str) -> Path | None:
    """Restituisce un path annidato dichiarato in ``pipeline2_sources.json``."""
    sources, manifest_path = read_run_sources(run_dir)
    value: Any = sources
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return resolve_declared_path(manifest_path, value)


__all__ = [
    "RUN_SOURCES_FILENAME",
    "find_run_sources_path",
    "get_run_source_path",
    "read_run_sources",
    "resolve_declared_path",
]
