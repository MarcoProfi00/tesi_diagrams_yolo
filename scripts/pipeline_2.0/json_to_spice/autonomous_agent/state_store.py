"""Persistenza file-based dello stato dell'agente autonomo."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from typing import Any


STATE_NAME = "autonomous_diagnosis.json"
MAX_EXECUTABLE_SCENARIOS = 5
MAX_AGENT_DECISIONS = 6


def now_iso() -> str:
    """Restituisce un timestamp locale leggibile e stabile."""
    return datetime.now().isoformat(timespec="seconds")


def state_path(output_dir: Path) -> Path:
    """Calcola il percorso dello stato dentro la sessione Experiment 4."""
    return output_dir / "experiment_chat" / STATE_NAME


def create_state(output_dir: Path, symptom: str, model: str) -> dict[str, Any]:
    """Crea e salva un nuovo ciclo autonomo vuoto."""
    timestamp = now_iso()
    state = {
        "source_format": "pipeline2.0_autonomous_diagnosis",
        "status": "running",
        "symptom": symptom.strip(),
        "model": model,
        "agent_decisions_count": 0,
        "max_agent_decisions": MAX_AGENT_DECISIONS,
        "executed_scenarios_count": 0,
        "max_executable_scenarios": MAX_EXECUTABLE_SCENARIOS,
        "iterations": [],
        "final_status": None,
        "final_reason": None,
        "final_answer": None,
        "stop_reason": None,
        "last_active_run": "base",
        "created_at": timestamp,
        "updated_at": timestamp,
    }
    write_state(output_dir, state)
    return state


def read_state(output_dir: Path) -> dict[str, Any]:
    """Legge lo stato corrente oppure restituisce un dizionario vuoto."""
    path = state_path(output_dir)
    if not path.exists() or not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def write_state(output_dir: Path, state: dict[str, Any]) -> Path:
    """Aggiorna timestamp e salva atomicamente lo stato corrente."""
    path = state_path(output_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = now_iso()
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)
    return path


def stop_state(output_dir: Path, reason: str = "user_stop") -> dict[str, Any]:
    """Ferma il ciclo corrente senza eliminare le evidenze gia raccolte."""
    state = read_state(output_dir)
    if not state:
        return {}
    if state.get("status") == "running":
        state["status"] = "stopped"
        state["stop_reason"] = reason
        write_state(output_dir, state)
    return state


def clear_state(output_dir: Path) -> bool:
    """Elimina stato, prompt e risposte autonome della sessione selezionata."""
    chat_dir = output_dir / "experiment_chat"
    if not chat_dir.exists() or not chat_dir.is_dir():
        return False
    removed = False
    for path in chat_dir.glob("autonomous_*"):
        if path.is_file():
            path.unlink()
            removed = True
    return removed
