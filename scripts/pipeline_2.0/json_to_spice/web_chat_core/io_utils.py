"""Operazioni pure di I/O e serializzazione usate dalla webchat locale."""

from __future__ import annotations

import html
import json
from pathlib import Path
import re
from typing import Any


def is_safe_path_name(name: str | None) -> bool:
    """Accetta solo nomi semplici per segmenti di path controllati da CLI."""
    if name is None:
        return True
    return bool(re.fullmatch(r"[A-Za-z0-9_.-]+", name)) and name not in {".", ".."}


def read_text_safe(path: Path) -> str:
    """Legge un file testuale senza far fallire il server se manca."""
    if not path.exists():
        return "File not available yet."
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def read_json_safe(path: Path) -> dict[str, Any]:
    """Legge un JSON quando possibile, altrimenti restituisce un dizionario vuoto."""
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def unescape_html_entities(value: Any) -> Any:
    """Decodifica entita HTML dentro stringhe, liste e dizionari semplici."""
    if isinstance(value, str):
        return html.unescape(value)
    if isinstance(value, list):
        return [unescape_html_entities(item) for item in value]
    if isinstance(value, dict):
        return {key: unescape_html_entities(item) for key, item in value.items()}
    return value


def escape_block(text: str) -> str:
    """Prepara testo tecnico da mostrare dentro un blocco pre."""
    return html.escape(text, quote=False)
