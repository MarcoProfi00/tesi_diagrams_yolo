"""
Interfaccia web locale per CHAT e AGENT.

Questo script avvia un piccolo server locale, senza database e senza stato
persistente obbligatorio. Serve come step 09 della Pipeline 2.0 per
visualizzare gli output del circuito, parlare con l'agente e orchestrare gli
scenari controllati.

La parte HTML vive in `web_chat/templates/`, cosi il layout puo crescere senza
trasformare questo script in un file troppo grande.

Responsabilita:

- aprire una pagina locale nel browser;
- mostrare la base run e le eventuali scenario run del circuito selezionato;
- visualizzare gli artefatti prodotti dagli step 01-08;
- lasciare una chat sempre visibile a destra;
- chiamare lo step 10 per aggiornare il contesto diagnostico;
- chiamare lo step 11 per ottenere la risposta dell'agente;
- riconoscere richieste semplici di esecuzione scenario;
- chiamare lo step 12 per applicare uno scenario su copia separata;
- mostrare il confronto base/scenario quando disponibile.

La chat resta locale e leggera: non sostituisce la pipeline tecnica, non usa
database e non salva uno stato applicativo complesso lato server.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import html
import importlib.util
import json
import mimetypes
import os
import re
import shutil
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

from agent_readonly.openai_runner import write_agent_response
from agent_readonly.preview_builder import write_agent_input_preview
from agent_readonly.prompt_builder import write_agent_prompt
from autonomous_agent.controller import (
    AutonomousControllerError,
    clear_diagnosis,
    read_state as read_autonomous_state,
    run_iteration as run_autonomous_iteration,
    start_diagnosis as start_autonomous_diagnosis,
    stop_diagnosis as stop_autonomous_diagnosis,
    summarize_state as summarize_autonomous_state,
)
from scenario_runtime import (
    ScenarioRuntimeError,
    count_executed_scenarios,
    execute_scenario as execute_shared_scenario,
    scenario_signature,
)
from scenario_expectations import ALLOWED_EXPECTATIONS
from run_sources import get_run_source_path
from viewer_core.contracts import (
    VIEWER_LAYOUT_NAME,
    VIEWER_LAYOUT_SCHEMA_VERSION,
    VIEWER_MODEL_NAME,
    VIEWER_MODEL_SCHEMA_VERSION,
    VIEWER_RENDER_VERSION,
    VIEWER_SVG_NAME,
)
from web_chat_core import (
    escape_block,
    is_safe_path_name,
    read_json_safe,
    read_text_safe,
    unescape_html_entities,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
WEB_CHAT_DIR = Path(__file__).resolve().parent / "web_chat"
TEMPLATE_DIR = WEB_CHAT_DIR / "templates"
INDEX_TEMPLATE = TEMPLATE_DIR / "index.html"
AGENT_VIEW_STYLE = WEB_CHAT_DIR / "agent_view.css"
AGENT_VIEW_SCRIPT = WEB_CHAT_DIR / "agent_view.js"
STEP10_PATH = Path(__file__).resolve().parent / "10_build_diagnostic_context.py"
STEP13_PATH = Path(__file__).resolve().parent / "13_build_viewer_model.py"
STEP14_PATH = Path(__file__).resolve().parent / "14_build_viewer_layout.py"
STEP15_PATH = Path(__file__).resolve().parent / "15_render_viewer_svg.py"
CHAT_MODEL = "gpt-5.4"
CHAT_MODELS = [
    "gpt-5.4",
    "gpt-5.5",
    "gpt-5.4-mini",
    "gpt-5-mini",
]
CHAT_MODEL_LABELS = {
    "gpt-5.4": "GPT 5.4",
    "gpt-5.5": "GPT 5.5",
    "gpt-5.4-mini": "GPT 5.4 mini",
    "gpt-5-mini": "GPT 5 mini",
}
CHAT_CONTEXT_NAME = "10_diagnostic_context.json"
CHAT_PREVIEW_NAME = "11_agent_input_preview_chat.md"
CHAT_PROMPT_NAME = "11_agent_prompt_chat.md"
CHAT_RESPONSE_NAME = "11_agent_response_chat.md"
MAX_EXECUTABLE_SCENARIOS = 5
EXPERIMENT2_CHAT_DIRNAME = "experiment2_chat"
INTERACTIVE_CHAT_DIRNAME = "experiment_chat"
MULTI_WORKSPACE_EXPERIMENTS = {"experiment4", "experiment5"}
CHAT_HISTORY_JSON_NAME = "chat_history.json"
CHAT_HISTORY_MD_NAME = "chat_history.md"
SCENARIO_REGISTRY_JSON_NAME = "scenario_registry.json"
SCENARIO_REGISTRY_MD_NAME = "scenario_registry.md"

SCENARIO_WORD_TO_INDEX = {
    "primo": 1,
    "prima": 1,
    "secondo": 2,
    "seconda": 2,
    "terzo": 3,
    "terza": 3,
    "quarto": 4,
    "quarta": 4,
    "quinto": 5,
    "quinta": 5,
}


ARTIFACTS = [
    ("Graph JSON", "01_graph.json", "json"),
    ("Normalized Circuit", "02_normalized_circuit.json", "json"),
    ("Node Map", "03_node_map.json", "json"),
    ("Values Bound", "04_values_bound.json", "json"),
    ("Component Rules", "06_component_rules.json", "json"),
    ("SPICE Netlist", "07_netlist.cir", "spice"),
    ("SPICE Emit Report", "07_spice_emit_report.json", "json"),
    ("SPICE Run Summary", "08_spice_run.json", "json"),
    ("ngspice stdout", "08_ngspice_stdout.txt", "text"),
    ("ngspice stderr", "08_ngspice_stderr.txt", "text"),
    ("Transient CSV", "08_tran.csv", "csv"),
]

SCENARIO_ROOT_ARTIFACTS = [
    ("Scenario Definition", "scenario.json", "json"),
    ("Scenario Status", "scenario_status.json", "json"),
    ("Scenario Copy Manifest", "scenario_copy_manifest.json", "json"),
    ("Controlled Scenario Report", "12_controlled_scenarios.json", "json"),
    ("Base vs Scenario Comparison", "scenario_comparison.json", "json"),
]


IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg"]


def repair_common_mojibake(text: str) -> str:
    """
    Corregge alcuni artefatti UTF-8/Latin-1 osservati nelle risposte chat.

    La correzione e volutamente conservativa: tocchiamo solo sequenze comuni
    gia viste nei testi italiani, senza trasformare arbitrariamente tutto il
    contenuto.
    """
    replacements = {
        "Ã¨": "è",
        "Ã©": "é",
        "Ã ": "à",
        "Ã¹": "ù",
        "Ã¬": "ì",
        "Ã²": "ò",
        "â€™": "’",
        "â€˜": "‘",
        "â€œ": "“",
        "â€": "”",
        "â€“": "–",
        "â€”": "—",
        "Â°": "°",
        "Â": "",
    }
    repaired = text
    for source, target in replacements.items():
        repaired = repaired.replace(source, target)
    return repaired


def normalize_human_text(text: str) -> str:
    """
    Normalizza testo umano con una riparazione conservativa del mojibake.

    Prima prova uno o due passaggi UTF-8/Latin-1 solo se il testo contiene
    marker tipici di corruzione. Poi applica le sostituzioni locali gia note.
    """
    normalized = text
    suspicious_markers = ("Ã", "â", "Â")
    for _ in range(2):
        if not any(marker in normalized for marker in suspicious_markers):
            break
        try:
            candidate = normalized.encode("latin-1").decode("utf-8")
        except UnicodeError:
            break
        if candidate == normalized:
            break
        normalized = candidate
    if any(marker in normalized for marker in ("Ã", "â€", "Â")):
        try:
            fallback_candidate = normalized.encode("latin-1").decode("utf-8")
        except UnicodeError:
            fallback_candidate = normalized
        if fallback_candidate != normalized:
            normalized = fallback_candidate

    normalized = repair_common_mojibake(normalized)
    normalized = (
        normalized
        .replace("Ã¨", "è")
        .replace("Ã©", "é")
        .replace("Ã ", "à")
        .replace("Ã¹", "ù")
        .replace("Ã¬", "ì")
        .replace("Ã²", "ò")
        .replace("â€™", "'")
        .replace("â€˜", "'")
        .replace("â€œ", "\"")
        .replace("â€", "\"")
        .replace("â€“", "-")
        .replace("â€”", "-")
        .replace("Â°", "°")
    )
    normalized = (
        normalized
        .replace("Ã¨", "è")
        .replace("Ã©", "é")
        .replace("Ã ", "à")
        .replace("Ã¹", "ù")
        .replace("Ã¬", "ì")
        .replace("Ã²", "ò")
        .replace("â€™", "'")
        .replace("â€˜", "'")
        .replace("â€œ", "\"")
        .replace("â€", "\"")
        .replace("â€“", "-")
        .replace("â€”", "-")
        .replace("Â°", "°")
    )
    return normalized


def cleanup_chat_reply(text: str) -> str:
    """
    Rimuove dalla chat i blocchi tecnici troppo grezzi.

    La risposta completa dell'agente resta salvata su file, ma nella UI chat
    vogliamo un'interazione piu naturale, senza mostrare JSON di servizio come
    scenario tecnico o blocco tecnico finale per pipeline.
    """
    cleaned = normalize_human_text(text).replace("\r\n", "\n")

    patterns = [
        r"\n*Scenario tecnico recuperato:\s*\n\s*```json\s*.*?```",
        r"\n*#{0,6}\s*\d+\.\s*\*?Blocco tecnico per pipeline\*?\s*\n\s*```json\s*.*?```",
        r"\n*#{0,6}\s*Blocco tecnico per pipeline\s*\n\s*```json\s*.*?```",
    ]

    for pattern in patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.DOTALL | re.IGNORECASE)

    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned


def json_for_html(value: Any) -> str:
    """Serializza dati JSON in modo sicuro per embedding dentro uno script."""
    return (
        json.dumps(value, ensure_ascii=False)
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
    )


def project_relative(path: Path) -> str:
    """Restituisce un path leggibile relativo alla root del progetto."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def is_experiment2_history_enabled(experiment: str | None) -> bool:
    """Abilita history e registry per ogni sessione interattiva nominata."""
    return bool(str(experiment or "").strip())


def build_experiment2_chat_dir(output_dir: Path, experiment: str | None) -> Path | None:
    """Restituisce la cartella sessione mantenendo compatibilita con Experiment 2."""
    if not is_experiment2_history_enabled(experiment):
        return None
    if str(experiment or "").startswith("experiment2"):
        return output_dir / EXPERIMENT2_CHAT_DIRNAME
    return output_dir / INTERACTIVE_CHAT_DIRNAME


def empty_experiment2_chat_history(batch: str, circuit: str, experiment: str) -> dict[str, Any]:
    """Costruisce una history vuota ma gia strutturata."""
    timestamp = datetime.now().isoformat(timespec="seconds")
    return {
        "source_format": "pipeline2.0_experiment_chat_history",
        "batch_name": batch,
        "experiment_name": experiment,
        "circuit_id": circuit,
        "created_at": timestamp,
        "updated_at": timestamp,
        "turns": [],
    }


def read_experiment2_chat_history(
    output_dir: Path,
    batch: str,
    circuit: str,
    experiment: str | None,
) -> dict[str, Any] | None:
    """Legge la chat history ufficiale, se la modalita esperimento la richiede."""
    chat_dir = build_experiment2_chat_dir(output_dir, experiment)
    if chat_dir is None:
        return None

    history_path = chat_dir / CHAT_HISTORY_JSON_NAME
    if not history_path.exists():
        return empty_experiment2_chat_history(batch, circuit, str(experiment))

    try:
        data = json.loads(history_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return empty_experiment2_chat_history(batch, circuit, str(experiment))

    if not isinstance(data, dict):
        return empty_experiment2_chat_history(batch, circuit, str(experiment))

    turns = data.get("turns")
    if not isinstance(turns, list):
        data["turns"] = []

    data.setdefault("source_format", "pipeline2.0_experiment_chat_history")
    data.setdefault("batch_name", batch)
    data.setdefault("experiment_name", experiment)
    data.setdefault("circuit_id", circuit)
    data.setdefault("created_at", datetime.now().isoformat(timespec="seconds"))
    data.setdefault("updated_at", datetime.now().isoformat(timespec="seconds"))
    return data


def write_experiment2_chat_history_files(chat_dir: Path, history: dict[str, Any]) -> None:
    """Salva JSON ufficiale e una vista Markdown leggibile."""
    chat_dir.mkdir(parents=True, exist_ok=True)
    history_path = chat_dir / CHAT_HISTORY_JSON_NAME
    markdown_path = chat_dir / CHAT_HISTORY_MD_NAME
    history_path.write_text(json.dumps(history, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown_path.write_text(build_experiment2_chat_history_markdown(history), encoding="utf-8")


def build_experiment2_chat_history_markdown(history: dict[str, Any]) -> str:
    """Crea una vista Markdown leggibile della chat history ufficiale."""
    lines = [
        "# Experiment 2 chat history",
        "",
        f"- Batch: `{history.get('batch_name')}`",
        f"- Experiment: `{history.get('experiment_name')}`",
        f"- Circuit: `{history.get('circuit_id')}`",
        f"- Created at: `{history.get('created_at')}`",
        f"- Updated at: `{history.get('updated_at')}`",
        "",
    ]

    turns = history.get("turns") or []
    if not turns:
        lines.extend(["No turns saved yet.", ""])
        return "\n".join(lines).rstrip() + "\n"

    for turn in turns:
        role = str(turn.get("role") or "unknown")
        turn_id = turn.get("turn_id")
        timestamp = str(turn.get("timestamp") or "")
        lines.extend(
            [
                f"## Turn {turn_id} - {role}",
                "",
                f"- Timestamp: `{timestamp}`",
                f"- Selected run: `{turn.get('selected_run')}`",
                f"- Model: `{turn.get('model')}`",
                f"- Used image: `{turn.get('used_image')}`",
                f"- Scenario id: `{turn.get('scenario_id')}`",
                f"- Scenario outcome: `{turn.get('scenario_outcome')}`",
                f"- Scenario path: `{turn.get('scenario_path')}`",
                "",
                "### Content",
                "",
                normalize_human_text(str(turn.get("content") or "")),
                "",
            ]
        )
        generated_files = turn.get("generated_files") or []
        if isinstance(generated_files, list) and generated_files:
            lines.extend(["### Generated files", ""])
            for path in generated_files:
                lines.append(f"- `{path}`")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def append_experiment2_chat_event(
    output_dir: Path,
    batch: str,
    circuit: str,
    experiment: str | None,
    role: str,
    content: str,
    model: str | None,
    selected_run: str,
    used_image: bool,
    generated_files: list[str] | None = None,
    scenario_id: str | None = None,
    scenario_outcome: Any = None,
    scenario_path: str | None = None,
) -> dict[str, Any] | None:
    """Aggiunge un evento alla chat history ufficiale di Esperimento 2."""
    history = read_experiment2_chat_history(output_dir, batch, circuit, experiment)
    chat_dir = build_experiment2_chat_dir(output_dir, experiment)
    if history is None or chat_dir is None:
        return None

    turns = history.get("turns") or []
    next_turn_id = max((int(item.get("turn_id") or 0) for item in turns if isinstance(item, dict)), default=0) + 1
    event = {
        "turn_id": next_turn_id,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "role": role,
        "content": normalize_human_text(content),
        "model": model,
        "selected_run": selected_run,
        "used_image": used_image,
        "generated_files": generated_files or [],
        "scenario_id": scenario_id,
        "scenario_outcome": scenario_outcome,
        "scenario_path": scenario_path,
    }
    turns.append(event)
    history["turns"] = turns
    history["updated_at"] = event["timestamp"]
    write_experiment2_chat_history_files(chat_dir, history)
    return event


def clear_experiment2_chat_history(
    output_dir: Path,
    batch: str,
    circuit: str,
    experiment: str | None,
) -> bool:
    """Azzera la chat history della sessione interattiva corrente."""
    chat_dir = build_experiment2_chat_dir(output_dir, experiment)
    if chat_dir is None:
        return False
    history = empty_experiment2_chat_history(batch, circuit, str(experiment))
    write_experiment2_chat_history_files(chat_dir, history)
    return True


def clear_experiment2_scenario_registry(
    output_dir: Path,
    batch: str,
    circuit: str,
    experiment: str | None,
) -> bool:
    """Azzera il registry scenari della sessione interattiva corrente."""
    chat_dir = build_experiment2_chat_dir(output_dir, experiment)
    if chat_dir is None:
        return False
    registry = empty_experiment2_scenario_registry(batch, circuit, str(experiment))
    write_experiment2_scenario_registry_files(chat_dir, registry)
    return True


def remove_directory_inside_output(output_dir: Path, target_dir: Path) -> bool:
    """Rimuove una directory solo se resta chiaramente dentro output_dir."""
    if not target_dir.exists():
        return False
    resolved_output = output_dir.resolve()
    resolved_target = target_dir.resolve()
    if resolved_target == resolved_output or resolved_output not in resolved_target.parents:
        raise ValueError(f"Refusing to remove path outside output dir: {target_dir}")
    if not resolved_target.is_dir():
        return False
    shutil.rmtree(resolved_target)
    return True


def clear_experiment2_session_state(
    output_dir: Path,
    batch: str,
    circuit: str,
    experiment: str | None,
) -> dict[str, Any]:
    """
    Reset completo della sessione interattiva per un circuito.

    Non tocca gli output base 01-08 copiati nell'esperimento. Azzera solo la
    conversazione, il registry, le run scenario e gli artefatti chat 10/11.
    """
    if not is_experiment2_history_enabled(experiment):
        return {
            "cleared": False,
            "reason": "Session clear is only enabled for supported interactive experiments.",
            "removed_files": [],
            "removed_dirs": [],
        }

    removed_files: list[str] = []
    removed_dirs: list[str] = []
    chat_history_cleared = clear_experiment2_chat_history(output_dir, batch, circuit, experiment)
    scenario_registry_cleared = clear_experiment2_scenario_registry(output_dir, batch, circuit, experiment)

    scenarios_dir = output_dir / "scenarios"
    if remove_directory_inside_output(output_dir, scenarios_dir):
        removed_dirs.append(project_relative(scenarios_dir))

    for filename in [CHAT_CONTEXT_NAME, CHAT_PREVIEW_NAME, CHAT_PROMPT_NAME, CHAT_RESPONSE_NAME]:
        path = output_dir / filename
        if path.exists() and path.is_file():
            path.unlink()
            removed_files.append(project_relative(path))

    return {
        "cleared": True,
        "chat_history_cleared": chat_history_cleared,
        "scenario_registry_cleared": scenario_registry_cleared,
        "removed_files": removed_files,
        "removed_dirs": removed_dirs,
    }


def empty_experiment2_scenario_registry(batch: str, circuit: str, experiment: str) -> dict[str, Any]:
    """Costruisce il registro scenari file-based della sessione interattiva."""
    timestamp = datetime.now().isoformat(timespec="seconds")
    return {
        "source_format": "pipeline2.0_experiment_scenario_registry",
        "batch_name": batch,
        "experiment_name": experiment,
        "circuit_id": circuit,
        "created_at": timestamp,
        "updated_at": timestamp,
        "max_executable_scenarios": MAX_EXECUTABLE_SCENARIOS,
        "next_scenario_number": 1,
        "last_added_scenario_id": None,
        "proposals": [],
        "scenarios": [],
    }


def read_experiment2_scenario_registry(
    output_dir: Path,
    batch: str,
    circuit: str,
    experiment: str | None,
) -> dict[str, Any] | None:
    """Legge il registro scenari della sessione interattiva corrente."""
    chat_dir = build_experiment2_chat_dir(output_dir, experiment)
    if chat_dir is None:
        return None

    registry_path = chat_dir / SCENARIO_REGISTRY_JSON_NAME
    if not registry_path.exists():
        return empty_experiment2_scenario_registry(batch, circuit, str(experiment))

    try:
        data = json.loads(registry_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return empty_experiment2_scenario_registry(batch, circuit, str(experiment))

    if not isinstance(data, dict):
        return empty_experiment2_scenario_registry(batch, circuit, str(experiment))

    data.setdefault("source_format", "pipeline2.0_experiment_scenario_registry")
    data.setdefault("batch_name", batch)
    data.setdefault("experiment_name", experiment)
    data.setdefault("circuit_id", circuit)
    data.setdefault("created_at", datetime.now().isoformat(timespec="seconds"))
    data.setdefault("updated_at", datetime.now().isoformat(timespec="seconds"))
    data.setdefault("max_executable_scenarios", MAX_EXECUTABLE_SCENARIOS)
    data.setdefault("next_scenario_number", 1)
    data.setdefault("last_added_scenario_id", None)
    if not isinstance(data.get("proposals"), list):
        data["proposals"] = []
    if not isinstance(data.get("scenarios"), list):
        data["scenarios"] = []
    return data


def write_experiment2_scenario_registry_files(chat_dir: Path, registry: dict[str, Any]) -> None:
    """Salva registro scenari JSON e vista Markdown leggibile."""
    chat_dir.mkdir(parents=True, exist_ok=True)
    registry_path = chat_dir / SCENARIO_REGISTRY_JSON_NAME
    markdown_path = chat_dir / SCENARIO_REGISTRY_MD_NAME
    registry_path.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown_path.write_text(build_experiment2_scenario_registry_markdown(registry), encoding="utf-8")


def build_experiment2_scenario_registry_markdown(registry: dict[str, Any]) -> str:
    """Crea una vista Markdown del registro scenari."""
    lines = [
        "# Pipeline 2.0 scenario registry",
        "",
        f"- Batch: `{registry.get('batch_name')}`",
        f"- Experiment: `{registry.get('experiment_name')}`",
        f"- Circuit: `{registry.get('circuit_id')}`",
        f"- Max executable scenarios: `{registry.get('max_executable_scenarios')}`",
        f"- Created at: `{registry.get('created_at')}`",
        f"- Updated at: `{registry.get('updated_at')}`",
        "",
    ]

    scenarios = registry.get("scenarios") or []
    if not scenarios:
        lines.extend(["No scenarios registered yet.", ""])
        return "\n".join(lines).rstrip() + "\n"

    for scenario in scenarios:
        if not isinstance(scenario, dict):
            continue
        scenario_id = str(scenario.get("scenario_id") or "")
        title = normalize_human_text(str(scenario.get("title") or scenario_id))
        lines.extend(
            [
                f"## Scenario {scenario.get('scenario_number')} - {title}",
                "",
                f"- Scenario id: `{scenario_id}`",
                f"- Status: `{scenario.get('status')}`",
                f"- Outcome: `{scenario.get('outcome')}`",
                f"- Executable: `{scenario.get('executable')}`",
                f"- Kind: `{scenario.get('kind')}`",
                f"- Source proposal: `{scenario.get('source_proposal_id')}`",
                f"- Source local index: `{scenario.get('source_local_index')}`",
                f"- Execution path: `{scenario.get('execution_path')}`",
                "",
            ]
        )
        hypothesis = normalize_human_text(str(scenario.get("hypothesis") or "").strip())
        if hypothesis:
            lines.extend(["### Hypothesis", "", hypothesis, ""])
        actions = scenario.get("actions") or []
        if isinstance(actions, list) and actions:
            lines.extend(["### Actions", "", "```json", json.dumps(actions, indent=2, ensure_ascii=False), "```", ""])

    return "\n".join(lines).rstrip() + "\n"


def next_proposal_id(registry: dict[str, Any]) -> str:
    """Restituisce il prossimo id proposal_N."""
    proposals = registry.get("proposals") or []
    return f"proposal_{len(proposals) + 1}"


def registered_scenario_signature(scenario: dict[str, Any]) -> str:
    """Firma uno scenario con la stessa logica tecnica usata dal runtime."""
    actions = scenario.get("actions")
    if isinstance(actions, list) and actions:
        return scenario_signature({"actions": actions})

    # Le proposte non eseguibili restano distinte tramite il loro significato.
    comparable = {
        "title": scenario.get("title"),
        "hypothesis": scenario.get("hypothesis"),
    }
    return json.dumps(comparable, sort_keys=True, ensure_ascii=False)


def scenario_requires_signal_gain(scenario: dict[str, Any]) -> bool:
    """Riconosce scenari transitori che dichiarano un obiettivo di trasferimento."""
    if str(scenario.get("analysis") or "").strip().lower() != "tran":
        return False
    text = " ".join(
        str(scenario.get(field) or "").strip().lower()
        for field in ("title", "hypothesis")
    )
    transfer_markers = (
        "gain",
        "guadagn",
        "amplif",
        "attenuat",
        "propagat",
        "trasfer",
        "signal transfer",
        "signal path",
        "percorso del segnale",
    )
    return any(marker in text for marker in transfer_markers)


def is_transient_diode_current(quantity: str) -> bool:
    """Riconosce una corrente interna di diodo esportabile nel CSV transitorio."""
    return bool(re.fullmatch(r"@d[^\[\]\s]+\[id\]", str(quantity or "").strip(), flags=re.IGNORECASE))


def scenario_is_executable(scenario: dict[str, Any]) -> bool:
    """Accetta scenari con azioni e criteri `expect` direttamente verificabili."""
    actions = scenario.get("actions")
    expectations = scenario.get("expect")
    gain = scenario.get("gain")
    compared = {
        str(item).strip().lower()
        for item in scenario.get("compare") or []
        if str(item).strip()
    }
    if not isinstance(actions, list) or not actions or not isinstance(expectations, dict) or not expectations:
        return False
    analysis = str(scenario.get("analysis") or "op").strip().lower()
    measurements = scenario.get("measure") or {}
    if not isinstance(measurements, dict):
        return False
    normalized_measures = {
        str(quantity).strip().lower(): str(measurement).strip().lower()
        for quantity, measurement in measurements.items()
        if str(quantity).strip()
    }
    # Una corrente interna di diodo e disponibile nel CSV soltanto come serie
    # temporale. In una run TRAN richiede quindi il picco assoluto esplicito,
    # altrimenti il confronto ricadrebbe impropriamente sul punto operativo.
    if analysis == "tran":
        for quantity in compared:
            if is_transient_diode_current(quantity) and normalized_measures.get(quantity) != "tran_abs_peak":
                return False
    gain_required = scenario_requires_signal_gain(scenario)
    if gain_required and not isinstance(gain, dict):
        return False
    if gain is not None:
        if not isinstance(gain, dict) or analysis != "tran":
            return False
        gain_input = str(gain.get("input") or "").strip().lower()
        gain_output = str(gain.get("output") or "").strip().lower()
        if not gain_input or not gain_output or gain_input == gain_output:
            return False
        if gain_input not in compared or gain_output not in compared:
            return False
        raw_min_ratio = gain.get("min_ratio")
        if gain_required and raw_min_ratio is None:
            return False
        if raw_min_ratio is not None:
            try:
                if float(raw_min_ratio) <= 0:
                    return False
            except (TypeError, ValueError):
                return False
    return all(
        str(quantity).strip().lower() in compared
        and str(expectation).strip().lower() in ALLOWED_EXPECTATIONS
        for quantity, expectation in expectations.items()
    )


def register_experiment2_scenarios_from_response(
    output_dir: Path,
    batch: str,
    circuit: str,
    experiment: str | None,
    response_text: str,
) -> dict[str, Any] | None:
    """Registra solo gli scenari con azioni tecniche realmente eseguibili."""
    registry = read_experiment2_scenario_registry(output_dir, batch, circuit, experiment)
    chat_dir = build_experiment2_chat_dir(output_dir, experiment)
    if registry is None or chat_dir is None:
        return None

    extracted = extract_scenarios_from_response(response_text)
    if not extracted:
        return {"added": [], "summary": ""}

    # Ricalcola anche le firme dei registry precedenti al formato action-only.
    existing_signatures = {
        registered_scenario_signature(
            item.get("scenario") if isinstance(item.get("scenario"), dict) else item
        )
        for item in registry.get("scenarios", [])
        if isinstance(item, dict)
    }
    proposal_id = next_proposal_id(registry)
    proposal = {
        "proposal_id": proposal_id,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "source_agent_response": project_relative(output_dir / CHAT_RESPONSE_NAME),
        "added_scenario_ids": [],
    }

    added: list[dict[str, Any]] = []
    next_number = int(registry.get("next_scenario_number") or 1)
    for local_index, raw_scenario in enumerate(extracted, start=1):
        scenario = normalize_human_text(json.dumps(unescape_html_entities(raw_scenario), ensure_ascii=False))
        scenario = json.loads(scenario)
        # Compatibilita prudente con risposte CHAT precedenti: se il modello
        # omette `intent`, lo scenario verifica un'ipotesi ma non puo fermare
        # la diagnosi come correzione del sintomo.
        scenario["intent"] = (
            "correction"
            if str(scenario.get("intent") or "").strip().lower() == "correction"
            else "diagnostic"
        )
        if not scenario_is_executable(scenario):
            # Una conclusione o un dato mancante non deve occupare un numero
            # scenario ne' essere suggerito come comando eseguibile.
            continue
        signature = registered_scenario_signature(scenario)
        if signature in existing_signatures:
            continue

        scenario_number = next_number
        next_number += 1
        scenario_id = f"scenario_{scenario_number}"
        original_scenario_id = str(scenario.get("scenario_id") or "")
        scenario["scenario_id"] = scenario_id

        entry = {
            "scenario_number": scenario_number,
            "scenario_id": scenario_id,
            "title": scenario.get("title") or scenario_id,
            "hypothesis": scenario.get("hypothesis"),
            "actions": scenario.get("actions") or [],
            "intent": scenario.get("intent"),
            "analysis": scenario.get("analysis") or "op",
            "compare": scenario.get("compare") or [],
            "measure": scenario.get("measure") or {},
            "gain": scenario.get("gain"),
            "expect": scenario.get("expect") or {},
            "rerun_from": scenario.get("rerun_from"),
            "status": "proposed",
            "outcome": None,
            "executable": scenario_is_executable(scenario),
            "kind": "spice_scenario" if scenario_is_executable(scenario) else "non_executable_proposal",
            "source_proposal_id": proposal_id,
            "source_local_index": local_index,
            "original_scenario_id": original_scenario_id,
            "execution_path": None,
            "created_at": proposal["created_at"],
            "updated_at": proposal["created_at"],
            "signature": signature,
            "scenario": scenario,
        }
        registry["scenarios"].append(entry)
        proposal["added_scenario_ids"].append(scenario_id)
        registry["last_added_scenario_id"] = scenario_id
        existing_signatures.add(signature)
        added.append(entry)

    if not added:
        return {"added": [], "summary": ""}

    registry["next_scenario_number"] = next_number
    registry["updated_at"] = datetime.now().isoformat(timespec="seconds")
    registry["proposals"].append(proposal)
    write_experiment2_scenario_registry_files(chat_dir, registry)
    return {
        "added": added,
        "summary": build_scenario_registration_summary(added),
        "registry_path": project_relative(chat_dir / SCENARIO_REGISTRY_JSON_NAME),
    }


def build_scenario_registration_summary(added: list[dict[str, Any]]) -> str:
    """Messaggio breve da aggiungere in chat dopo nuove proposte."""
    if not added:
        return ""

    heading = "Ho salvato questi nuovi scenari proposti:"
    lines = ["", "**Scenari registrati**", "", heading, ""]
    for item in added:
        lines.append(f"- Scenario {item.get('scenario_number')} - {item.get('title')}")
    lines.extend(["", build_scenario_command_hint(added)])
    return "\n".join(lines)


def build_scenario_command_hint(scenarios: list[dict[str, Any]] | None) -> str:
    """Crea un suggerimento breve con comandi coerenti agli scenari correnti."""
    valid_items = [item for item in (scenarios or []) if isinstance(item, dict)]
    numbers: list[int] = []
    for item in valid_items:
        try:
            number = int(item.get("scenario_number") or 0)
        except (TypeError, ValueError):
            continue
        if number > 0:
            numbers.append(number)

    if not numbers:
        return "Puoi scrivere `mostra scenari` per vedere la lista disponibile."

    unique_numbers: list[int] = []
    seen: set[int] = set()
    for number in numbers:
        if number in seen:
            continue
        seen.add(number)
        unique_numbers.append(number)

    if len(unique_numbers) == 1:
        scenario_number = unique_numbers[0]
        return (
            f"Puoi scrivere per esempio: `esegui scenario {scenario_number}`, "
            "`esegui l'ultimo` oppure `mostra scenari`."
        )

    example_commands = [f"`esegui scenario {number}`" for number in unique_numbers[:3]]
    commands_text = ", ".join(example_commands)
    return (
        f"Puoi scrivere per esempio: {commands_text}, "
        "`esegui l'ultimo` oppure `mostra scenari`."
    )


def build_scenario_registry_summary(registry: dict[str, Any] | None) -> str:
    """Riepilogo leggibile degli scenari registrati."""
    if not registry or not registry.get("scenarios"):
        return "Non ci sono ancora scenari registrati per questo circuito."

    lines = ["**Scenari disponibili**", ""]
    for item in registry.get("scenarios") or []:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or item.get("scenario_id") or "")
        status = str(item.get("status") or "unknown")
        outcome = item.get("outcome") or "not available"
        executable = "SPICE" if item.get("executable") else "non eseguibile"
        lines.append(f"- Scenario {item.get('scenario_number')} - {title}")
        lines.append(f"  Stato: `{status}`, outcome: `{outcome}`, tipo: `{executable}`")
    lines.append("")
    lines.append(build_scenario_command_hint(registry.get("scenarios") or []))
    return "\n".join(lines)


def detect_scenario_list_request(user_message: str) -> bool:
    """Riconosce richieste di riepilogo degli scenari senza esecuzione."""
    normalized = user_message.lower().replace("_", " ")
    patterns = [
        r"\bmostra(?:mi)?\s+(?:gli\s+)?scenari\b",
        r"\blista\s+(?:gli\s+)?scenari\b",
        r"\briepilogo\s+scenari\b",
        r"\bstato\s+scenari\b",
        r"\bquali\s+scenari\s+(?:ci\s+sono|sono\s+disponibili|abbiamo|restano)\b",
        r"\bquali\s+scenari\s+(?:non\s+ho\s+ancora\s+eseguito|sono\s+stati\s+eseguiti)\b",
        r"\bfammi\s+vedere\s+(?:gli\s+)?scenari\b",
    ]
    return any(re.search(pattern, normalized) for pattern in patterns)


def select_scenario_from_registry(registry: dict[str, Any], requested_index: int | str) -> dict[str, Any] | None:
    """Seleziona uno scenario dalla lista globale user-friendly."""
    scenarios = [item for item in registry.get("scenarios") or [] if isinstance(item, dict)]
    if not scenarios:
        return None

    selected_entry: dict[str, Any] | None = None
    if requested_index == "latest":
        last_added = registry.get("last_added_scenario_id")
        for item in reversed(scenarios):
            if item.get("scenario_id") == last_added:
                selected_entry = item
                break
        if selected_entry is None:
            selected_entry = scenarios[-1]
    else:
        for item in scenarios:
            if int(item.get("scenario_number") or 0) == int(requested_index):
                selected_entry = item
                break

    if selected_entry is None:
        return None
    scenario = dict(selected_entry.get("scenario") or {})
    scenario["scenario_id"] = selected_entry.get("scenario_id")
    scenario["_registry_scenario_id"] = selected_entry.get("scenario_id")
    scenario["_registry_scenario_number"] = selected_entry.get("scenario_number")
    scenario["_registry_executable"] = bool(selected_entry.get("executable"))
    return scenario


def update_scenario_registry_after_execution(
    output_dir: Path,
    batch: str,
    circuit: str,
    experiment: str | None,
    scenario_id: str,
    outcome: Any,
    execution_path: str,
) -> None:
    """Aggiorna status/outcome dello scenario eseguito nel registry."""
    registry = read_experiment2_scenario_registry(output_dir, batch, circuit, experiment)
    chat_dir = build_experiment2_chat_dir(output_dir, experiment)
    if registry is None or chat_dir is None:
        return

    timestamp = datetime.now().isoformat(timespec="seconds")
    for item in registry.get("scenarios") or []:
        if not isinstance(item, dict):
            continue
        if item.get("scenario_id") != scenario_id:
            continue
        item["status"] = "executed"
        item["outcome"] = outcome
        item["execution_path"] = execution_path
        item["updated_at"] = timestamp
        break

    registry["updated_at"] = timestamp
    write_experiment2_scenario_registry_files(chat_dir, registry)


def sync_scenario_registry_with_existing_runs(
    output_dir: Path,
    batch: str,
    circuit: str,
    experiment: str | None,
) -> dict[str, Any] | None:
    """Allinea il registry agli scenari gia presenti su disco."""
    registry = read_experiment2_scenario_registry(output_dir, batch, circuit, experiment)
    chat_dir = build_experiment2_chat_dir(output_dir, experiment)
    if registry is None or chat_dir is None:
        return None

    changed = False
    timestamp = datetime.now().isoformat(timespec="seconds")
    for item in registry.get("scenarios") or []:
        if not isinstance(item, dict):
            continue
        scenario_id = str(item.get("scenario_id") or "")
        if not scenario_id:
            continue
        scenario_dir = output_dir / "scenarios" / safe_scenario_dir_name(scenario_id)
        status_path = scenario_dir / "scenario_status.json"
        if not status_path.exists():
            continue

        status = read_json_safe(status_path)
        diagnostic_outcome = status.get("diagnostic_outcome")
        outcome_status = None
        if isinstance(diagnostic_outcome, dict):
            outcome_status = diagnostic_outcome.get("status")

        execution_path = project_relative(scenario_dir)
        new_status = "executed" if status.get("spice_executed") else str(status.get("status") or "prepared")
        if (
            item.get("status") != new_status
            or item.get("outcome") != outcome_status
            or item.get("execution_path") != execution_path
        ):
            item["status"] = new_status
            item["outcome"] = outcome_status
            item["execution_path"] = execution_path
            item["updated_at"] = timestamp
            changed = True

    if changed:
        registry["updated_at"] = timestamp
        write_experiment2_scenario_registry_files(chat_dir, registry)
    return registry


def build_server_chat_history_items(
    output_dir: Path,
    batch: str,
    circuit: str,
    experiment: str | None,
) -> list[dict[str, str]]:
    """Converte la history ufficiale in un formato semplice per la UI."""
    history = read_experiment2_chat_history(output_dir, batch, circuit, experiment)
    if not history:
        return []

    items: list[dict[str, str]] = []
    for turn in history.get("turns") or []:
        if not isinstance(turn, dict):
            continue
        role = str(turn.get("role") or "")
        kind = "user" if role == "user" else "agent"
        text = str(turn.get("content") or "")
        if not text:
            continue
        items.append({"kind": kind, "text": text})
    return items


def build_output_dir(
    batch: str,
    circuit: str,
    experiment: str | None = None,
    variant: str | None = None,
) -> Path:
    """Calcola la cartella output della Pipeline 2.0 per un circuito."""
    if experiment:
        experiment_dir = PROJECT_ROOT / "outputs" / "pipeline2.0" / batch / experiment
        if variant:
            experiment_dir = experiment_dir / variant
        return experiment_dir / circuit
    return PROJECT_ROOT / "outputs" / "pipeline2.0" / batch / circuit


def find_input_image_path(batch: str, circuit: str, output_dir: Path) -> Path | None:
    """Trova l'immagine originale usata dalla Pipeline 1.0, quando disponibile."""
    declared_image = get_run_source_path(output_dir, "input_image")
    if declared_image is not None and declared_image.is_file():
        return declared_image

    graph = read_json_safe(output_dir / "01_graph.json")
    image_name = graph.get("image_name")
    image_candidates: list[Path] = []

    if isinstance(image_name, str) and image_name.strip():
        image_candidates.append(PROJECT_ROOT / "data" / batch / image_name)

    for extension in IMAGE_EXTENSIONS:
        image_candidates.append(PROJECT_ROOT / "data" / batch / f"{circuit}{extension}")

    for candidate in image_candidates:
        if candidate.exists() and candidate.is_file():
            return candidate

    return None


def build_status(output_dir: Path) -> dict[str, Any]:
    """Estrae poche informazioni utili da mostrare nella barra superiore."""
    spice_run = read_json_safe(output_dir / "08_spice_run.json")
    emit_report = read_json_safe(output_dir / "07_spice_emit_report.json")
    node_map = read_json_safe(output_dir / "03_node_map.json")
    stderr_text = read_text_safe(output_dir / "08_ngspice_stderr.txt")
    stderr_has_content = bool(stderr_text.strip()) and stderr_text != "File not available yet."

    node_stats = node_map.get("stats") or {}

    return {
        "spice_status": spice_run.get("status") or "not available",
        "exit_code": spice_run.get("exit_code"),
        "stderr_state": "warning" if stderr_has_content else "empty",
        "emitted": emit_report.get("emitted_elements"),
        "skipped": emit_report.get("skipped_elements"),
        "nodes": node_stats.get("nodes_count"),
        "singletons": node_stats.get("singleton_nodes_count"),
        "has_tran": (output_dir / "08_tran.csv").exists(),
        "has_plot": (output_dir / "08_tran_plot.png").exists(),
    }


def read_scenario_status(scenario_dir: Path) -> dict[str, Any]:
    """Legge lo stato sintetico di uno scenario."""
    status = read_json_safe(scenario_dir / "scenario_status.json")
    if not status:
        report = read_json_safe(scenario_dir / "12_controlled_scenarios.json")
        status = report if report else {}
    return status


def list_scenario_runs(output_dir: Path) -> list[dict[str, str]]:
    """Elenca gli scenari disponibili per il circuito corrente."""
    scenarios_dir = output_dir / "scenarios"
    if not scenarios_dir.exists():
        return []

    runs: list[dict[str, str]] = []
    for scenario_dir in sorted(path for path in scenarios_dir.iterdir() if path.is_dir()):
        status = read_scenario_status(scenario_dir)
        scenario = unescape_html_entities(read_json_safe(scenario_dir / "scenario.json"))
        outcome = status.get("diagnostic_outcome") or {}
        if not isinstance(outcome, dict):
            outcome = {}
        scenario_id = str(status.get("scenario_id") or scenario.get("scenario_id") or scenario_dir.name)
        title = str(scenario.get("title") or scenario_id)
        state = str(status.get("status") or "prepared")
        runs.append(
            {
                "id": scenario_dir.name,
                "scenario_id": scenario_id,
                "title": title,
                "status": state,
                "outcome_status": str(outcome.get("status") or ""),
                "outcome_label": str(outcome.get("label") or ""),
            }
        )
    return runs


def status_class(status: str) -> str:
    """Converte lo stato SPICE in una classe CSS semplice."""
    if status == "success":
        return "ok"
    if status in {"failed", "error"}:
        return "bad"
    return "warn"


def run_status_class(status: str) -> str:
    """Converte lo stato di una run/scenario in una classe CSS."""
    if status in {"success", "spice_success"}:
        return "ok"
    if status in {"failed", "error", "spice_failed", "partial_or_failed"}:
        return "bad"
    return "warn"


def outcome_status_class(status: str) -> str:
    """Converte l'esito diagnostico dello scenario in una classe CSS."""
    if status == "resolved_candidate":
        return "ok"
    if status == "not_resolved":
        return "bad"
    if status in {"partially_resolved", "unknown"}:
        return "warn"
    return "neutral"


def append_workspace_mode(url: str, workspace_mode: str | None) -> str:
    """Aggiunge la modalita workspace a un URL interno della web chat."""
    if not workspace_mode:
        return url
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}mode={workspace_mode}"


def render_run_selector(
    output_dir: Path,
    active_run: str,
    workspace_mode: str | None = None,
) -> str:
    """Crea la sidebar con base run e scenari disponibili."""
    base_status = build_status(output_dir)
    base_active = " active" if active_run == "base" else ""
    base_url = append_workspace_mode("/", workspace_mode)
    sections = [
        f"""
        <a class="run-item{base_active}" href="{html.escape(base_url)}">
          <strong>Base run</strong>
          <span>{html.escape(str(base_status["spice_status"]))}</span>
        </a>
        """
    ]

    scenarios = list_scenario_runs(output_dir)
    if not scenarios:
        sections.append(
            """
            <div class="run-item muted-run">
              <strong>Scenario runs</strong>
              <span>No scenarios yet</span>
            </div>
            """
        )
        return "\n".join(sections)

    for scenario in scenarios:
        scenario_active = " active" if active_run == scenario["id"] else ""
        state_class = run_status_class(scenario["status"])
        scenario_url = append_workspace_mode(
            f"/?run={html.escape(scenario['id'])}",
            workspace_mode,
        )
        sections.append(
            f"""
            <a class="run-item scenario-run{scenario_active}" href="{scenario_url}">
              <strong>{html.escape(scenario["scenario_id"])}</strong>
              <span class="{state_class}">{html.escape(scenario["status"])}</span>
              <small>{html.escape(scenario["title"])}</small>
            </a>
            """
        )

    return "\n".join(sections)


def render_status_cards(status: dict[str, Any]) -> str:
    """Crea le card sintetiche in alto al pannello centrale."""
    spice_status = str(status["spice_status"])
    cards = [
        ("SPICE", spice_status, status_class(spice_status)),
        ("Exit code", str(status["exit_code"]), "neutral"),
        ("stderr", str(status["stderr_state"]), "warn" if status["stderr_state"] == "warning" else "ok"),
        ("Elements", f"{status['emitted']} emitted / {status['skipped']} skipped", "neutral"),
        ("Nodes", f"{status['nodes']} nodes / {status['singletons']} singletons", "neutral"),
        ("Transient", "available" if status["has_tran"] else "not available", "ok" if status["has_tran"] else "neutral"),
    ]

    return "\n".join(
        f'<div class="status-card {css}"><span>{html.escape(label)}</span><strong>{html.escape(value)}</strong></div>'
        for label, value, css in cards
    )


def render_artifact_sections(artifact_dir: Path, artifacts: list[tuple[str, str, str]]) -> str:
    """Crea i pannelli richiudibili con gli artefatti della pipeline."""
    sections: list[str] = []

    for title, filename, kind in artifacts:
        path = artifact_dir / filename
        text = read_text_safe(path)
        open_attr = " open" if filename in {"08_spice_run.json", "07_netlist.cir", "scenario_comparison.json"} else ""
        language_class = f"language-{kind}"

        sections.append(
            f"""
            <details class="artifact"{open_attr}>
              <summary>
                <span>{html.escape(title)}</span>
                <small>{html.escape(filename)}</small>
              </summary>
              <pre class="{language_class}">{escape_block(text)}</pre>
            </details>
            """
        )

    return "\n".join(sections)


def render_artifacts(
    output_dir: Path,
    plot_url: str = "/artifact/08_tran_plot.png",
    workspace_mode: str | None = None,
) -> str:
    """Crea i pannelli richiudibili con gli artefatti della pipeline."""
    sections: list[str] = [render_artifact_sections(output_dir, ARTIFACTS)]
    plot_url = append_workspace_mode(plot_url, workspace_mode)

    plot_path = output_dir / "08_tran_plot.png"
    if plot_path.exists():
        sections.append(
            f"""
            <details class="artifact" open>
              <summary>
                <span>Transient Plot</span>
                <small>08_tran_plot.png</small>
              </summary>
              <div class="plot-wrap">
                <img src="{html.escape(plot_url)}" alt="Transient plot">
              </div>
            </details>
            """
        )

    return "\n".join(sections)


def load_step13_module() -> Any:
    """Carica lo step 13 per generare il viewer model della run selezionata."""
    spec = importlib.util.spec_from_file_location("pipeline2_step13", STEP13_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare lo step 13 da {STEP13_PATH}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_step14_module() -> Any:
    """Carica lo step 14 per generare il layout del viewer della run."""
    spec = importlib.util.spec_from_file_location("pipeline2_step14", STEP14_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare lo step 14 da {STEP14_PATH}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_step15_module() -> Any:
    """Carica lo step 15 che renderizza l'artefatto SVG generale della run."""
    spec = importlib.util.spec_from_file_location("pipeline2_step15", STEP15_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare lo step 15 da {STEP15_PATH}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_or_build_viewer_model(run_dir: Path) -> dict[str, Any]:
    """Legge o genera `13_viewer_model.json` senza bloccare la web chat."""
    model_path = run_dir / VIEWER_MODEL_NAME
    model = read_json_safe(model_path)
    if model and int(model.get("schema_version") or 0) >= VIEWER_MODEL_SCHEMA_VERSION:
        return model
    step13 = load_step13_module()
    built = step13.write_viewer_model(run_dir)
    return built if isinstance(built, dict) else {}


def load_or_build_viewer_layout(run_dir: Path) -> dict[str, Any]:
    """Legge o genera `14_viewer_layout.json` nel formato generale corrente."""
    layout_path = run_dir / VIEWER_LAYOUT_NAME
    layout = read_json_safe(layout_path)
    if layout and int(layout.get("schema_version") or 0) >= VIEWER_LAYOUT_SCHEMA_VERSION:
        return layout
    step14 = load_step14_module()
    built = step14.write_viewer_layout(run_dir)
    return built if isinstance(built, dict) else {}


def load_or_build_viewer_svg(run_dir: Path) -> str:
    """Legge o genera `15_viewer.svg` senza inserire logica grafica nella web chat."""
    svg_path = run_dir / VIEWER_SVG_NAME
    model_path = run_dir / VIEWER_MODEL_NAME
    layout_path = run_dir / VIEWER_LAYOUT_NAME
    dependencies = [path for path in (model_path, layout_path) if path.exists()]
    if svg_path.exists() and dependencies and svg_path.stat().st_mtime >= max(path.stat().st_mtime for path in dependencies):
        svg = svg_path.read_text(encoding="utf-8")
        if f'data-viewer-version="{VIEWER_RENDER_VERSION}"' in svg:
            return svg
    step15 = load_step15_module()
    svg = step15.write_viewer_svg(run_dir)
    return svg if isinstance(svg, str) else ""


def transient_scope_payload(model: dict[str, Any]) -> dict[str, Any]:
    """Riduce il modello ai soli dati necessari agli oscilloscopi web."""
    transient = model.get("transient") or {}
    traces = transient.get("traces") or {}
    selected = [str(item) for item in transient.get("selected_traces") or []][:3]
    current_series = traces.get("series") or {}
    base_traces = transient.get("base_traces") or {}
    base_series = base_traces.get("series") or {}
    return {
        "selected": selected,
        "steady_start": transient.get("steady_start"),
        "current": {
            "time": traces.get("time") or [],
            "series": {
                quantity: current_series[quantity]
                for quantity in selected
                if quantity in current_series
            },
        },
        "base": {
            "time": base_traces.get("time") or [],
            "series": {
                quantity: base_series[quantity]
                for quantity in selected
                if quantity in base_series
            },
        },
    }


def render_transient_scopes(model: dict[str, Any]) -> str:
    """Crea il contenitore generico degli scope quando esistono tracce TRAN."""
    payload = transient_scope_payload(model)
    if not payload["selected"] or not payload["current"]["time"]:
        return ""
    comparison_label = (
        '<span class="viewer-scope-key"><i class="is-base"></i>base</span>'
        '<span class="viewer-scope-key"><i class="is-current"></i>run corrente</span>'
        if payload["base"]["series"]
        else '<span class="viewer-scope-key"><i class="is-current"></i>run corrente</span>'
    )
    return f"""
    <section class="viewer-scopes" aria-label="Oscilloscopi analisi transitoria">
      <div class="viewer-scope-toolbar">
        <button type="button" class="viewer-scope-play" data-scope-action="play" title="Play o pausa" aria-label="Play o pausa">&#10074;&#10074;</button>
        <span class="viewer-scope-time">t = 0 ms</span>
        <input class="viewer-scope-slider" type="range" min="0" max="1000" value="0" aria-label="Tempo transitorio">
        <select class="viewer-scope-window" aria-label="Finestra temporale">
          <option value="full">Intera simulazione</option>
          <option value="steady">Regime stabile</option>
        </select>
        <select class="viewer-scope-display" aria-label="Scala delle tensioni">
          <option value="centered">AC centrata</option>
          <option value="real">Tensione reale</option>
        </select>
        <select class="viewer-scope-speed" aria-label="Velocita riproduzione">
          <option value="0.5">0.5x</option>
          <option value="1" selected>1x</option>
          <option value="2">2x</option>
        </select>
        <div class="viewer-scope-keys">{comparison_label}</div>
      </div>
      <div class="viewer-scope-grid"></div>
      <script type="application/json" class="viewer-scope-data">{json_for_html(payload)}</script>
    </section>
    """


def render_viewer_section(run_dir: Path) -> str:
    """Renderizza il viewer della run selezionata, se possibile."""
    try:
        viewer_model = load_or_build_viewer_model(run_dir)
        load_or_build_viewer_layout(run_dir)
        viewer_svg = load_or_build_viewer_svg(run_dir)
    except Exception as exc:
        return f"""
        <details class="artifact" open>
          <summary>
            <span>Circuito equivalente dalla netlist SPICE</span>
            <small>viewer unavailable</small>
          </summary>
          <div class="viewer-wrap viewer-missing">
            Viewer non disponibile: {html.escape(str(exc))}
          </div>
        </details>
        """

    if not viewer_svg:
        return ""

    return f"""
    <details class="artifact" open>
      <summary>
        <span>Circuito equivalente dalla netlist SPICE</span>
        <small>15_viewer.svg</small>
      </summary>
      <div class="viewer-wrap">
        <div class="viewer-toolbar" aria-label="Controlli viewer circuito">
          <div class="viewer-toolbar-group">
            <button type="button" data-viewer-action="zoom-out" title="Zoom out" aria-label="Zoom out">-</button>
            <span class="viewer-zoom-readout">100%</span>
            <button type="button" data-viewer-action="zoom-in" title="Zoom in" aria-label="Zoom in">+</button>
            <button type="button" data-viewer-action="reset" title="Reset vista" aria-label="Reset vista">1:1</button>
          </div>
        </div>
        <div class="viewer-canvas">
          {viewer_svg}
        </div>
        {render_transient_scopes(viewer_model)}
      </div>
    </details>
    """


def render_comparison_summary(scenario_dir: Path) -> str:
    """Mostra un riepilogo leggibile del confronto base/scenario."""
    comparison = read_json_safe(scenario_dir / "scenario_comparison.json")
    quantities = comparison.get("quantities")
    if not isinstance(quantities, list) or not quantities:
        return ""

    outcome = comparison.get("diagnostic_outcome") or {}
    if not isinstance(outcome, dict):
        outcome = {}
    outcome_status = str(outcome.get("status") or "unknown")
    outcome_label = str(outcome.get("label") or "Esito non determinabile")
    outcome_reason = str(outcome.get("reason") or "Nessun esito diagnostico disponibile.")
    outcome_next_step = str(outcome.get("next_step") or "")
    outcome_class = outcome_status_class(outcome_status)

    rows: list[str] = []
    for item in quantities:
        if not isinstance(item, dict):
            continue
        rows.append(
            f"""
            <tr>
              <td>{html.escape(str(item.get("quantity")))}</td>
              <td>{html.escape(str(item.get("base_value")))}</td>
              <td>{html.escape(str(item.get("scenario_value")))}</td>
              <td>{html.escape(str(item.get("delta")))}</td>
              <td>{html.escape(str(item.get("change")))}</td>
            </tr>
            """
        )

    if not rows:
        return ""

    return f"""
    <details class="artifact" open>
      <summary>
        <span>Base vs Scenario</span>
        <small>scenario_comparison.json</small>
      </summary>
      <div class="comparison-wrap">
        <div class="outcome-banner {outcome_class}">
          <strong>{html.escape(outcome_label)}</strong>
          <span>{html.escape(outcome_reason)}</span>
          <small>{html.escape(outcome_next_step)}</small>
        </div>
        <table>
          <thead>
            <tr>
              <th>Quantity</th>
              <th>Base</th>
              <th>Scenario</th>
              <th>Delta</th>
              <th>Change</th>
            </tr>
          </thead>
          <tbody>
            {''.join(rows)}
          </tbody>
        </table>
      </div>
    </details>
    """


def render_scenario_content(
    output_dir: Path,
    scenario_name: str,
    workspace_mode: str | None = None,
) -> dict[str, str]:
    """Renderizza titolo, stato e artefatti per una scenario run."""
    if not is_safe_scenario_name(scenario_name):
        return {
            "title": "Scenario not found",
            "output_dir": scenario_name,
            "status_cards": "",
            "artifacts": "<p>Invalid scenario name.</p>",
        }

    scenario_dir = output_dir / "scenarios" / scenario_name
    run_dir = scenario_dir / "run"

    if not scenario_dir.exists() or not scenario_dir.is_dir():
        return {
            "title": "Scenario not found",
            "output_dir": project_relative(scenario_dir),
            "status_cards": "",
            "image_section": "",
            "artifacts": "<p>Scenario directory not found.</p>",
        }

    status = build_status(run_dir)
    scenario_status = read_scenario_status(scenario_dir)
    scenario = unescape_html_entities(read_json_safe(scenario_dir / "scenario.json"))
    title = str(scenario.get("title") or scenario_status.get("scenario_id") or scenario_name)
    root_artifacts = render_artifact_sections(scenario_dir, SCENARIO_ROOT_ARTIFACTS)
    run_artifacts = render_artifacts(
        run_dir,
        plot_url=f"/scenario-artifact/{html.escape(scenario_name)}/run/08_tran_plot.png",
        workspace_mode=workspace_mode,
    )

    return {
        "title": f"Scenario - {str(scenario_status.get('scenario_id') or scenario_name)}",
        "output_dir": project_relative(scenario_dir),
        "status_cards": render_status_cards(status),
        "artifacts": "\n".join([render_comparison_summary(scenario_dir), root_artifacts, run_artifacts]),
        "subtitle": title,
    }


def render_image_section(
    batch: str,
    circuit: str,
    output_dir: Path,
    workspace_mode: str | None = None,
) -> str:
    """Crea il pannello con l'immagine originale del circuito."""
    image_path = find_input_image_path(batch, circuit, output_dir)
    if image_path is None:
        return """
        <details class="artifact">
          <summary>
            <span>Circuit Image</span>
            <small>not available</small>
          </summary>
          <div class="image-wrap image-missing">
            Original input image not found.
          </div>
        </details>
        """

    image_url = append_workspace_mode("/input-image", workspace_mode)
    return f"""
    <details class="artifact" open>
      <summary>
        <span>Circuit Image</span>
        <small>{html.escape(project_relative(image_path))}</small>
      </summary>
      <div class="image-wrap">
        <img src="{html.escape(image_url)}" alt="Original circuit image">
      </div>
    </details>
    """


def render_model_options(selected_model: str) -> str:
    """Crea le option del selettore modello nella chat."""
    options: list[str] = []
    for model in CHAT_MODELS:
        selected_attr = " selected" if model == selected_model else ""
        label = CHAT_MODEL_LABELS.get(model, model)
        options.append(
            f'<option value="{html.escape(model)}"{selected_attr}>{html.escape(label)}</option>'
        )
    return "\n".join(options)


def fill_template(template: str, values: dict[str, str]) -> str:
    """Sostituisce placeholder semplici nel template HTML."""
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    return rendered


def render_workspace_switch(
    active_mode: str | None,
    available_modes: tuple[str, ...],
) -> str:
    """Crea lo switch CHAT/AGENT quando il server espone piu workspace."""
    if len(available_modes) < 2:
        return ""

    items: list[str] = []
    for mode in available_modes:
        active_class = " active" if mode == active_mode else ""
        label = "AGENT" if mode == "agent" else mode.upper()
        items.append(
            f'<a class="workspace-tab{active_class}" href="/?mode={html.escape(mode)}">'
            f"{html.escape(label)}</a>"
        )
    return '<nav class="workspace-switch" aria-label="Modalita diagnostica">' + "".join(items) + "</nav>"


def render_page(
    batch: str,
    circuit: str,
    output_dir: Path,
    active_run: str = "base",
    experiment: str | None = None,
    workspace_mode: str | None = None,
    available_workspace_modes: tuple[str, ...] = (),
) -> str:
    """Renderizza la pagina HTML principale usando il template esterno."""
    template = read_text_safe(INDEX_TEMPLATE)
    active_run = active_run if active_run else "base"
    circuit_label = f"{batch} / {experiment} / {circuit}" if experiment else f"{batch} / {circuit}"
    if workspace_mode:
        circuit_label = f"{batch} / {experiment} / {workspace_mode} / {circuit}"
    workspace_storage_suffix = f"_{workspace_mode}" if workspace_mode else ""
    chat_storage_key = (
        f"pipeline2_chat_{batch}_{experiment}_{circuit}{workspace_storage_suffix}"
        if experiment
        else f"pipeline2_chat_{batch}_{circuit}"
    )
    model_storage_key = (
        f"pipeline2_chat_model_{batch}_{experiment}_{circuit}{workspace_storage_suffix}"
        if experiment
        else f"pipeline2_chat_model_{batch}_{circuit}"
    )
    server_chat_history_items = build_server_chat_history_items(output_dir, batch, circuit, experiment)
    chat_history_enabled = is_experiment2_history_enabled(experiment)
    chat_panel_title = "Agente diagnostico" if workspace_mode == "agent" else "Chat diagnostica"
    chat_panel_description = (
        "Segui ipotesi, test controllati ed evidenze prodotte dalla diagnosi autonoma."
        if workspace_mode == "agent"
        else "Descrivi il sintomo e l'agente analizzera gli output SPICE e gli scenari gia eseguiti."
    )
    workspace_label = "AGENT" if workspace_mode == "agent" else "CHAT"
    layout_mode_class = " agent-layout" if workspace_mode == "agent" else ""
    chat_mode_class = " agent-workspace" if workspace_mode == "agent" else ""
    chat_actions_class = " agent-mode" if workspace_mode == "agent" else ""
    agent_header_status = (
        '<span class="agent-header-status neutral" id="agentHeaderStatus">'
        '<i aria-hidden="true"></i><span>Pronto</span></span>'
        if workspace_mode == "agent"
        else ""
    )
    agent_stop_button = (
        '<button class="agent-stop" id="stopAgentButton" type="button">Stop</button>'
        if workspace_mode == "agent"
        else ""
    )
    welcome_message = (
        "Descrivi il sintomo: l'agente eseguira test controllati fino alla conclusione o al limite di sicurezza."
        if workspace_mode == "agent"
        else "Descrivi il sintomo del circuito e analizzero gli output correnti della pipeline."
    )
    chat_input_placeholder = (
        "Descrivi il comportamento desiderato per il circuito..."
        if workspace_mode == "agent"
        else "Esempio: Perche il LED non si accende?"
    )

    if active_run == "base":
        status = build_status(output_dir)
        spice_status = str(status["spice_status"])
        header_meta = f"{circuit_label} - Base run - {spice_status}"
        title = "Base run"
        subtitle = project_relative(output_dir)
        status_cards = render_status_cards(status)
        image_section = render_viewer_section(output_dir) + render_image_section(
            batch,
            circuit,
            output_dir,
            workspace_mode,
        )
        artifacts = render_artifacts(output_dir, workspace_mode=workspace_mode)
    else:
        available_scenarios = {scenario["id"] for scenario in list_scenario_runs(output_dir)}
        if active_run not in available_scenarios:
            return render_page(
                batch,
                circuit,
                output_dir,
                active_run="base",
                experiment=experiment,
                workspace_mode=workspace_mode,
                available_workspace_modes=available_workspace_modes,
            )
        scenario_content = render_scenario_content(output_dir, active_run, workspace_mode)
        scenario_state = read_scenario_status(output_dir / "scenarios" / active_run).get("status") or "not available"
        header_meta = f"{circuit_label} - {active_run} - {scenario_state}"
        title = scenario_content["title"]
        subtitle = scenario_content.get("subtitle") or scenario_content["output_dir"]
        status_cards = scenario_content["status_cards"]
        scenario_run_dir = output_dir / "scenarios" / active_run / "run"
        image_section = render_viewer_section(scenario_run_dir) + render_image_section(
            batch,
            circuit,
            output_dir,
            workspace_mode,
        )
        artifacts = scenario_content["artifacts"]

    return fill_template(
        template,
        {
            "PAGE_TITLE": html.escape(f"Pipeline 2.0 Diagnostic Chat - {circuit}"),
            "AGENT_VIEW_STYLES": read_text_safe(AGENT_VIEW_STYLE),
            "AGENT_VIEW_SCRIPT": read_text_safe(AGENT_VIEW_SCRIPT),
            "HEADER_META": html.escape(header_meta),
            "WORKSPACE_SWITCH": render_workspace_switch(workspace_mode, available_workspace_modes),
            "ACTIVE_WORKSPACE_MODE": html.escape(workspace_mode or ""),
            "CHAT_PANEL_TITLE": html.escape(chat_panel_title),
            "CHAT_PANEL_DESCRIPTION": html.escape(chat_panel_description),
            "WORKSPACE_LABEL": html.escape(workspace_label),
            "LAYOUT_MODE_CLASS": layout_mode_class,
            "CHAT_MODE_CLASS": chat_mode_class,
            "CHAT_ACTIONS_CLASS": chat_actions_class,
            "AGENT_HEADER_STATUS": agent_header_status,
            "AGENT_STOP_BUTTON": agent_stop_button,
            "WELCOME_MESSAGE": html.escape(welcome_message),
            "CHAT_INPUT_PLACEHOLDER": html.escape(chat_input_placeholder),
            "CHAT_STORAGE_KEY": html.escape(chat_storage_key),
            "MODEL_STORAGE_KEY": html.escape(model_storage_key),
            "DEFAULT_CHAT_MODEL": html.escape(CHAT_MODEL),
            "ACTIVE_RUN_ID": html.escape(active_run),
            "SERVER_CHAT_HISTORY_JSON": json_for_html(server_chat_history_items),
            "SERVER_CHAT_HISTORY_ENABLED": "true" if chat_history_enabled else "false",
            "MODEL_OPTIONS": render_model_options(CHAT_MODEL),
            "RUN_SELECTOR": render_run_selector(output_dir, active_run, workspace_mode),
            "ACTIVE_RUN_TITLE": html.escape(title),
            "OUTPUT_DIR": html.escape(subtitle),
            "STATUS_CARDS": status_cards,
            "IMAGE_SECTION": image_section,
            "ARTIFACTS": artifacts,
        },
    )


def load_step10_module() -> Any:
    """Carica lo step 10 anche se il file inizia con un numero."""
    spec = importlib.util.spec_from_file_location("pipeline2_step10", STEP10_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load step 10 from {STEP10_PATH}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_chat_context(
    batch: str,
    circuit: str,
    output_dir: Path,
    user_problem: str,
    experiment: str | None = None,
) -> Path:
    """Rigenera il manifest 10 con il problema scritto nella chat."""
    step10 = load_step10_module()
    context = step10.build_diagnostic_context(
        output_dir=output_dir,
        batch_name=batch,
        circuit_id=circuit,
        project_root=PROJECT_ROOT,
        user_problem=user_problem,
        experiment_name=experiment,
    )
    context_path = output_dir / CHAT_CONTEXT_NAME
    context_path.write_text(json.dumps(context, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return context_path


def count_critical_skipped_components(output_dir: Path) -> int:
    """Conta componenti saltati che possono indicare un problema topologico forte."""
    report = read_json_safe(output_dir / "07_spice_emit_report.json")
    skipped = report.get("skipped_components")
    if not isinstance(skipped, list):
        return 0

    critical_prefixes = (
        "battery",
        "lamp",
        "inductor",
        "switch",
        "signal_source",
        "transformer",
    )
    count = 0
    for item in skipped:
        if not isinstance(item, dict):
            continue
        component_id = str(item.get("component_id") or "")
        if component_id.startswith(critical_prefixes):
            count += 1
    return count


def detect_topology_failure_mode(context: dict[str, Any], output_dir: Path) -> tuple[bool, list[str]]:
    """Decide se l'agente deve ricevere automaticamente anche l'immagine."""
    summary = context.get("summary") or {}
    if str(summary.get("spice_status")) != "failed":
        return False, []

    reasons: list[str] = []
    if int(summary.get("ground_groups_count") or 0) == 0:
        reasons.append("ground_groups_count=0")
    if int(summary.get("singleton_nodes_count") or 0) >= 2:
        reasons.append(f"singleton_nodes_count={summary.get('singleton_nodes_count')}")
    if int(summary.get("skipped_components_count") or 0) >= 2:
        reasons.append(f"skipped_components_count={summary.get('skipped_components_count')}")

    critical_skipped = count_critical_skipped_components(output_dir)
    if critical_skipped >= 1:
        reasons.append(f"critical_skipped_components={critical_skipped}")

    return len(reasons) >= 2, reasons


def run_readonly_agent_from_chat(
    batch: str,
    circuit: str,
    output_dir: Path,
    user_problem: str,
    model: str = CHAT_MODEL,
    experiment: str | None = None,
) -> dict[str, Any]:
    """
    Esegue il flusso minimo della chat:

    10_diagnostic_context.json -> preview/prompt chat -> risposta OpenAI.
    """
    context_path = write_chat_context(
        batch=batch,
        circuit=circuit,
        output_dir=output_dir,
        user_problem=user_problem,
        experiment=experiment,
    )
    context = read_json_safe(context_path)
    preview_path = output_dir / CHAT_PREVIEW_NAME
    prompt_path = output_dir / CHAT_PROMPT_NAME
    response_path = output_dir / CHAT_RESPONSE_NAME
    auto_use_image, auto_image_reasons = detect_topology_failure_mode(context, output_dir)
    image_path = find_input_image_path(batch, circuit, output_dir) if auto_use_image else None

    write_agent_input_preview(
        context_path=context_path,
        user_problem=user_problem,
        output_path=preview_path,
    )
    write_agent_prompt(
        context_path=context_path,
        user_problem=user_problem,
        output_path=prompt_path,
    )
    write_agent_response(
        prompt_path=prompt_path,
        model=model,
        output_path=response_path,
        image_path=image_path,
    )
    normalized_response = normalize_human_text(read_text_safe(response_path)).rstrip() + "\n"
    response_path.write_text(normalized_response, encoding="utf-8")

    debug_lines = [
        f"Updated: {project_relative(context_path)}",
        f"Generated: {project_relative(preview_path)}",
        f"Generated: {project_relative(prompt_path)}",
        f"Generated: {project_relative(response_path)}",
        f"Model: {model}",
    ]
    if auto_use_image and image_path is not None:
        debug_lines.append(f"Auto image: {project_relative(image_path)}")
        debug_lines.append(f"Auto image reasons: {', '.join(auto_image_reasons)}")
    elif auto_use_image:
        debug_lines.append("Auto image requested, but local input image was not found.")
        debug_lines.append(f"Auto image reasons: {', '.join(auto_image_reasons)}")
    else:
        debug_lines.append("Auto image: not used")

    return {
        "reply": cleanup_chat_reply(normalized_response),
        "debug": debug_lines,
        "used_image": image_path is not None,
        "generated_files": [
            project_relative(context_path),
            project_relative(preview_path),
            project_relative(prompt_path),
            project_relative(response_path),
        ],
    }


def normalize_chat_model(requested_model: str | None) -> str:
    """Valida il modello scelto nella chat e applica il default se serve."""
    if requested_model in CHAT_MODELS:
        return str(requested_model)
    return CHAT_MODEL


def detect_scenario_request(user_message: str) -> int | str | None:
    """Riconosce richieste semplici di esecuzione scenario."""
    normalized = user_message.lower().replace("_", " ")
    execution_verbs = r"(?:esegui|esequi|eseguire|lancia|avvia|run|execute|testa|prova|applica|facciamo|vai|procedi)"
    filler = r"(?:\s+(?:pure|per\s+favore|lo|la|il|uno|un|questo|questa|con|please))*"

    # La run parte solo se il verbo di esecuzione e legato allo scenario stesso.
    match = re.search(
        rf"\b{execution_verbs}\b{filler}\s+scenario\s*(\d+)\b",
        normalized,
    )
    if match:
        return int(match.group(1))

    # Supporta richieste naturali come "esegui lo scenario appena proposto".
    latest_markers = (
        r"l['’]?\s*ultimo",
        r"ultimo",
        r"quest['’]?\s*ultimo",
        r"questo\s+ultimo",
        r"ultimo\s+scenario",
        r"ultimo\s+proposto",
        r"scenario\s+appena\s+proposto",
        r"scenario\s+proposto",
        r"scenario\s+piu\s+recente",
        r"questo\s+scenario",
        r"quello\s+appena\s+proposto",
    )
    for marker in latest_markers:
        if re.search(rf"\b{execution_verbs}\b{filler}\s+{marker}\b", normalized):
            return "latest"

    for word, index in SCENARIO_WORD_TO_INDEX.items():
        if re.search(
            rf"\b{execution_verbs}\b{filler}\s+\b{re.escape(word)}\b",
            normalized,
        ):
            return index

    return None


def extract_scenarios_from_response(response_text: str) -> list[dict[str, Any]]:
    """Estrae gli scenari JSON dall'ultima risposta dell'agente."""
    scenarios: list[dict[str, Any]] = []
    json_blocks = re.findall(r"```json\s*(\{.*?\})\s*```", response_text, flags=re.DOTALL | re.IGNORECASE)

    for block in json_blocks:
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and data.get("scenario_id"):
            scenarios.append(unescape_html_entities(data))

    return scenarios


def select_scenario(scenarios: list[dict[str, Any]], requested_index: int | str) -> dict[str, Any] | None:
    """Seleziona uno scenario per id tecnico, posizione o ultimo scenario proposto."""
    if requested_index == "latest":
        return scenarios[-1] if scenarios else None

    requested_id = f"scenario_{requested_index}"
    for scenario in scenarios:
        if str(scenario.get("scenario_id")) == requested_id:
            return scenario

    position = requested_index - 1
    if 0 <= position < len(scenarios):
        return scenarios[position]

    return None


def safe_scenario_dir_name(scenario_id: str) -> str:
    """Normalizza il nome cartella dello scenario evitando caratteri strani."""
    cleaned = re.sub(r"[^a-zA-Z0-9_.-]+", "_", scenario_id.strip())
    return cleaned or "scenario"


def count_existing_scenario_dirs(output_dir: Path) -> int:
    """Conta le run scenario realmente eseguite, non le sole cartelle."""
    return count_executed_scenarios(output_dir)


def is_safe_scenario_name(name: str) -> bool:
    """Accetta solo nomi scenario semplici usabili come directory locali."""
    return bool(re.fullmatch(r"[A-Za-z0-9_.-]+", name)) and name not in {".", ".."}


def build_scenario_result_explanation(
    scenario_dir: Path,
    selected: dict[str, Any],
    diagnostic_outcome: dict[str, Any],
) -> str:
    """
    Costruisce una spiegazione automatica sintetica del risultato scenario.

    La usiamo sempre, cosi la chat non lascia l'utente solo con un'etichetta
    tecnica tipo `partially_resolved`.
    """
    comparison = read_json_safe(scenario_dir / "scenario_comparison.json")
    quantities = comparison.get("quantities")
    if not isinstance(quantities, list):
        quantities = []

    changed_lines: list[str] = []
    for item in quantities[:3]:
        if not isinstance(item, dict):
            continue
        quantity = str(item.get("quantity") or "")
        base_value = item.get("base_value")
        scenario_value = item.get("scenario_value")
        change = str(item.get("change") or "")
        if not quantity or base_value is None or scenario_value is None:
            continue
        changed_lines.append(
            f"- `{quantity}`: da **{base_value}** a **{scenario_value}** (`{change}`)"
        )

    hypothesis = str(selected.get("hypothesis") or "").strip()
    title = str(selected.get("title") or selected.get("scenario_id") or "scenario").strip()
    outcome_status = str(diagnostic_outcome.get("status") or "unknown")
    stop_automation = bool(diagnostic_outcome.get("stop_automation"))
    outcome_sentence = {
        "resolved_candidate": (
            f"Questo scenario fornisce una conferma forte: "
            f"l'ipotesi testata da **{title}** risulta fortemente supportata dai risultati."
        ),
        "partially_resolved": (
            f"Questo scenario aggiunge una conferma utile sul ramo testato: "
            f"l'ipotesi legata a **{title}** riceve evidenza concreta, anche se non esaurisce da sola tutta la diagnosi."
        ),
        "not_resolved": (
            f"Questo scenario non aggiunge evidenza utile: "
            f"l'ipotesi testata da **{title}** non e confermata dai risultati osservati."
        ),
        "unknown": (
            f"Questo scenario resta inconcludente: "
            f"i dati disponibili non bastano ancora per valutare bene l'ipotesi testata da **{title}**."
        ),
    }.get(
        outcome_status,
        f"Questo scenario ha prodotto un risultato tecnico da interpretare rispetto all'ipotesi testata da **{title}**.",
    )

    lines = [
        "**Spiegazione automatica**",
        "",
        outcome_sentence,
    ]
    if hypothesis:
        lines.append("")
        lines.append(f"Ipotesi testata: {hypothesis}")
    if changed_lines:
        lines.extend(
            [
                "",
                "Le grandezze piu importanti sono cambiate cosi:",
                *changed_lines,
            ]
        )
    practical_sentence = {
        "resolved_candidate": (
            "Interpretazione pratica: il comportamento osservato spiega il sintomo "
            "meglio della run base e fornisce evidenza sufficiente per fermare i test automatici."
            if stop_automation
            else "Interpretazione pratica: il comportamento osservato supporta fortemente l'ipotesi testata."
        ),
        "partially_resolved": (
            "Interpretazione pratica: lo scenario aggiunge evidenza utile sul ramo testato, "
            "ma non chiude ancora da solo la diagnosi."
        ),
        "not_resolved": (
            "Interpretazione pratica: lo scenario non supporta l'ipotesi testata; "
            "conviene valutare un'ipotesi diversa usando le evidenze gia raccolte."
        ),
        "unknown": (
            "Interpretazione pratica: il confronto resta inconcludente e non permette "
            "di confermare o escludere l'ipotesi testata."
        ),
    }.get(
        outcome_status,
        "Interpretazione pratica: il risultato richiede ancora una valutazione diagnostica mirata.",
    )
    lines.extend(["", practical_sentence])
    return "\n".join(lines)


def handle_scenario_request(
    output_dir: Path,
    user_message: str,
    batch: str,
    circuit: str,
    experiment: str | None,
    ngspice_executable: str | None = None,
) -> dict[str, Any] | None:
    """
    Gestisce gli step iniziali degli scenari.

    Per ora riconosce la scelta, recupera il JSON tecnico e prepara una cartella
    scenario separata. Non modifica la base run originale.
    """
    requested_index = detect_scenario_request(user_message)
    if requested_index is None:
        return None

    requested_label = "latest" if requested_index == "latest" else str(requested_index)

    response_path = output_dir / CHAT_RESPONSE_NAME
    if response_path.exists():
        register_experiment2_scenarios_from_response(
            output_dir=output_dir,
            batch=batch,
            circuit=circuit,
            experiment=experiment,
            response_text=read_text_safe(response_path),
        )
    registry = read_experiment2_scenario_registry(output_dir, batch, circuit, experiment)
    if registry is not None and not registry.get("scenarios") and response_path.exists():
        register_experiment2_scenarios_from_response(
            output_dir=output_dir,
            batch=batch,
            circuit=circuit,
            experiment=experiment,
            response_text=read_text_safe(response_path),
        )
        registry = read_experiment2_scenario_registry(output_dir, batch, circuit, experiment)
    if registry is not None:
        registry = sync_scenario_registry_with_existing_runs(output_dir, batch, circuit, experiment)
    selected = select_scenario_from_registry(registry, requested_index) if registry else None
    scenarios: list[dict[str, Any]] = []

    if selected is None:
        if not response_path.exists():
            return {
                "reply": (
                    f"Ho capito che vuoi eseguire lo scenario {requested_label}, "
                    "ma non trovo ancora scenari registrati o una risposta agente con scenari.\n\n"
                    "Prima scrivi un sintomo, aspetta la diagnosi e poi chiedi di eseguire uno scenario."
                ),
                "debug": [f"Missing: {project_relative(response_path)}"],
            }

        response_text = read_text_safe(response_path)
        scenarios = extract_scenarios_from_response(response_text)
        selected = select_scenario(scenarios, requested_index)

    if selected is None:
        return {
            "reply": (
                f"Ho riconosciuto la richiesta per lo scenario {requested_label}, "
                "ma non ho trovato uno scenario corrispondente.\n\n"
                "Puoi scrivere `mostra scenari` per vedere la lista disponibile."
            ),
            "debug": [f"Read: {project_relative(response_path)}"],
        }

    selected = unescape_html_entities(selected)
    if selected.get("_registry_executable") is False:
        return {
            "reply": (
                f"Ho trovato **Scenario {selected.get('_registry_scenario_number')}**, "
                "ma non e uno scenario SPICE eseguibile: non contiene azioni tecniche da applicare.\n\n"
                "Lo tengo nel registro come proposta diagnostica/topologica, ma non creo una run scenario."
            ),
            "debug": [f"Selected non-executable scenario: {selected.get('_registry_scenario_id')}"],
        }

    title = selected.get("title") or selected.get("scenario_id") or f"scenario {requested_label}"
    selected_scenario_id = str(selected.get("scenario_id") or "")
    selected_scenario_dir = output_dir / "scenarios" / safe_scenario_dir_name(selected_scenario_id or f"scenario_{requested_label}")
    existing_scenarios = count_existing_scenario_dirs(output_dir)

    if not selected_scenario_dir.exists() and existing_scenarios >= MAX_EXECUTABLE_SCENARIOS:
        return {
            "reply": (
                "Hai raggiunto il limite massimo di **5 scenari eseguibili** per questo circuito.\n\n"
                "Da questo punto in poi l'agente non dovrebbe piu proporre o lanciare nuovi scenari, "
                "ma deve fornire una conclusione diagnostica finale basata su tutte le evidenze raccolte."
            ),
            "debug": [
                f"Scenario budget reached: {existing_scenarios}/{MAX_EXECUTABLE_SCENARIOS}",
                f"Blocked new scenario id: {selected_scenario_id or requested_label}",
            ],
        }

    scenario_payload = {
        key: value
        for key, value in selected.items()
        if not str(key).startswith("_registry_")
    }
    try:
        runtime_result = execute_shared_scenario(
            output_dir=output_dir,
            scenario=scenario_payload,
            ngspice_executable=ngspice_executable,
            source_label="guided_chat",
            reject_duplicates=True,
        )
    except ScenarioRuntimeError as exc:
        return {
            "reply": f"Lo scenario non e stato eseguito: {exc}",
            "debug": [f"Scenario runtime rejected: {exc}"],
        }

    scenario_dir = Path(str(runtime_result["scenario_dir"]))
    run_dir = Path(str(runtime_result["run_dir"]))
    # Ricostruisce i percorsi prodotti dal runtime condiviso per la risposta CHAT.
    scenario_paths = {
        "scenario_dir": scenario_dir,
        "scenario_path": scenario_dir / "scenario.json",
        "status_path": scenario_dir / "scenario_status.json",
    }
    copy_manifest = read_json_safe(scenario_dir / "scenario_copy_manifest.json")
    copy_result = {
        "base_snapshot_dir": scenario_dir / "base_snapshot",
        "run_dir": run_dir,
        "manifest_path": scenario_dir / "scenario_copy_manifest.json",
        "copied_files": list(copy_manifest.get("copied_files") or []),
    }
    apply_report = read_json_safe(scenario_dir / "12_controlled_scenarios.json")
    viewer_data = runtime_result.get("viewer") if isinstance(runtime_result.get("viewer"), dict) else {}
    viewer_model_path = Path(str(viewer_data.get("model") or run_dir / VIEWER_MODEL_NAME))
    viewer_layout_path = Path(str(viewer_data.get("layout") or run_dir / VIEWER_LAYOUT_NAME))
    viewer_svg_path = Path(str(viewer_data.get("svg") or run_dir / VIEWER_SVG_NAME))
    viewer_debug = (
        f"Viewer model: {project_relative(Path(str(viewer_data.get('model'))))}; "
        f"layout: {project_relative(Path(str(viewer_data.get('layout'))))}"
        if viewer_data
        else f"Generazione viewer fallita: {runtime_result.get('viewer_error') or 'output non disponibile'}"
    )
    applied_actions = apply_report.get("applied_actions") or []
    failed_actions = apply_report.get("failed_actions") or []
    unsupported_actions = apply_report.get("unsupported_actions") or []
    spice_status = apply_report.get("spice_status") or "not executed"
    comparison_summary = apply_report.get("comparison_summary") or {}
    diagnostic_outcome = apply_report.get("diagnostic_outcome") or {}
    if not isinstance(diagnostic_outcome, dict):
        diagnostic_outcome = {}
    outcome_label = diagnostic_outcome.get("label") or "Esito non determinabile"
    outcome_status = diagnostic_outcome.get("status") or "unknown"
    outcome_reason = diagnostic_outcome.get("reason") or "Nessun esito diagnostico disponibile."
    outcome_next_step = diagnostic_outcome.get("next_step") or "Puo avere senso continuare con il flusso diagnostico."
    stop_automation = bool(diagnostic_outcome.get("stop_automation"))
    scenario_explanation = build_scenario_result_explanation(
        scenario_paths["scenario_dir"],
        selected,
        diagnostic_outcome,
    )
    executed_scenarios_count = count_existing_scenario_dirs(output_dir)
    budget_exhausted = executed_scenarios_count >= MAX_EXECUTABLE_SCENARIOS
    if budget_exhausted:
        stop_automation = True
        outcome_next_step = "Hai esaurito il budget scenari. Chiedi all'agente una conclusione diagnostica finale."

    update_scenario_registry_after_execution(
        output_dir=output_dir,
        batch=batch,
        circuit=circuit,
        experiment=experiment,
        scenario_id=str(selected.get("scenario_id") or ""),
        outcome=outcome_status,
        execution_path=project_relative(scenario_paths["scenario_dir"]),
    )

    return {
        "reply": (
            "Ho riconosciuto la richiesta di eseguire **lo scenario appena proposto**.\n\n"
            if requested_index == "latest"
            else f"Ho riconosciuto la richiesta di eseguire **scenario {selected.get('_registry_scenario_number') or requested_index}**.\n\n"
        ) + (
            "Ho selezionato l'ultimo scenario proposto dall'agente.\n\n"
            if requested_index == "latest"
            else ""
        ) + (
            f"Scenario selezionato: **{title}**.\n\n"
            "Ho creato una cartella scenario separata, ho copiato la base run, "
            "ho applicato le azioni supportate alla netlist in `run/` e ho eseguito ngspice sulla run scenario.\n\n"
            "La base run originale non e stata modificata.\n\n"
            f"Cartella scenario:\n\n`{project_relative(scenario_paths['scenario_dir'])}`\n\n"
            f"Snapshot base:\n\n`{project_relative(copy_result['base_snapshot_dir'])}`\n\n"
            f"Run scenario modificata:\n\n`{project_relative(copy_result['run_dir'])}`\n\n"
            f"File copiati: **{len(copy_result['copied_files'])}**.\n\n"
            f"Azioni applicate: **{len(applied_actions)}**. "
            f"Azioni non supportate: **{len(unsupported_actions)}**. "
            f"Azioni fallite: **{len(failed_actions)}**.\n\n"
            f"Stato SPICE scenario: **{spice_status}**.\n\n"
            f"Confronti attivati: **{comparison_summary.get('activated_count', 0)}** / "
            f"{comparison_summary.get('requested_count', 0)}.\n\n"
            f"Esito diagnostico scenario: **{outcome_label}**.\n\n"
            f"Motivo: {outcome_reason}\n\n"
            f"Suggerimento automatico: **{'fermarsi qui' if stop_automation else 'si puo continuare'}**.\n\n"
            f"Prossimo passo consigliato: {outcome_next_step}\n\n"
            + (
                f"{scenario_explanation}\n\n"
                if scenario_explanation
                else ""
            )
            + (
                "Hai raggiunto il limite massimo di **5 scenari eseguibili** per questo circuito.\n\n"
                "Da questo punto in poi non vanno proposti o eseguiti nuovi scenari: "
                "il prossimo messaggio deve essere una **conclusione diagnostica finale completa**.\n\n"
                if budget_exhausted
                else ""
            )
            + "Lo scenario ora e disponibile nella barra sinistra.\n\n"
            + "I dettagli tecnici restano disponibili nella pagina centrale, dentro gli artefatti dello scenario."
        ),
        "active_run": scenario_paths["scenario_dir"].name,
        "scenario_id": str(selected.get("scenario_id") or ""),
        "scenario_outcome": outcome_status,
        "scenario_path": project_relative(scenario_paths["scenario_dir"]),
        "generated_files": [
            project_relative(scenario_paths["scenario_path"]),
            project_relative(scenario_paths["status_path"]),
            project_relative(copy_result["manifest_path"]),
            project_relative(scenario_paths["scenario_dir"] / "12_controlled_scenarios.json"),
            project_relative(scenario_paths["scenario_dir"] / "scenario_comparison.json"),
            project_relative(viewer_model_path),
            project_relative(viewer_layout_path),
            project_relative(viewer_svg_path),
        ],
        "used_image": False,
        "debug": [
            f"Read: {project_relative(response_path)}",
            f"Scenarios found: {len(scenarios)}",
            f"Requested: {requested_label}",
            f"Selected: {selected.get('scenario_id')}",
            f"Written: {project_relative(scenario_paths['scenario_path'])}",
            f"Written: {project_relative(scenario_paths['status_path'])}",
            f"Written: {project_relative(copy_result['manifest_path'])}",
            f"Written: {project_relative(scenario_paths['scenario_dir'] / '12_controlled_scenarios.json')}",
            viewer_debug,
            f"Copied files: {len(copy_result['copied_files'])}",
            f"Applied actions: {len(applied_actions)}",
            f"Unsupported actions: {len(unsupported_actions)}",
            f"Failed actions: {len(failed_actions)}",
            f"SPICE status: {spice_status}",
            f"Diagnostic outcome: {outcome_status}",
            f"Stop automation: {stop_automation}",
            f"Scenario budget exhausted: {budget_exhausted}",
            f"Comparison: {project_relative(scenario_paths['scenario_dir'] / 'scenario_comparison.json')}",
            "Action: scenario applied and SPICE executed",
        ],
    }


class WebChatHandler(BaseHTTPRequestHandler):
    """Gestisce la pagina web e le API locali della sessione diagnostica."""

    server: "WebChatServer"

    def log_message(self, format: str, *args: object) -> None:
        """Riduce il rumore nel terminale."""
        return

    def send_text(self, status: int, body: str, content_type: str = "text/plain; charset=utf-8") -> None:
        """Invia una risposta testuale."""
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def send_bytes(self, status: int, body: bytes, content_type: str) -> None:
        """Invia una risposta binaria, utile per immagini e artefatti."""
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        """Serve pagina HTML principale e artefatti statici della run."""
        parsed = urlparse(self.path)
        workspace_mode = self.server.bind_request_workspace(parsed.query)
        path = parsed.path

        if path == "/api/agent/state":
            if workspace_mode != "agent":
                self.send_text(403, "AGENT workspace required")
                return
            body = json.dumps(
                summarize_autonomous_state(
                    read_autonomous_state(self.server.output_dir),
                    self.server.output_dir,
                ),
                ensure_ascii=False,
            )
            self.send_text(200, body, "application/json; charset=utf-8")
            return

        if path == "/":
            query = parsed.query
            active_run = "base"
            for part in query.split("&"):
                if part.startswith("run="):
                    active_run = unquote(part.removeprefix("run=")) or "base"
                    break
            page = render_page(
                self.server.batch,
                self.server.circuit,
                self.server.output_dir,
                active_run=active_run,
                experiment=self.server.experiment,
                workspace_mode=workspace_mode,
                available_workspace_modes=self.server.available_workspace_modes,
            )
            self.send_text(200, page, "text/html; charset=utf-8")
            return

        if path.startswith("/artifact/"):
            filename = unquote(path.removeprefix("/artifact/"))
            artifact_path = (self.server.output_dir / filename).resolve()
            output_dir = self.server.output_dir.resolve()
            if output_dir not in artifact_path.parents and artifact_path != output_dir:
                self.send_text(403, "Forbidden")
                return
            if not artifact_path.exists() or not artifact_path.is_file():
                self.send_text(404, "Artifact not found")
                return
            content_type = mimetypes.guess_type(str(artifact_path))[0] or "application/octet-stream"
            self.send_bytes(200, artifact_path.read_bytes(), content_type)
            return

        if path == "/input-image":
            image_path = find_input_image_path(self.server.batch, self.server.circuit, self.server.output_dir)
            if image_path is None:
                self.send_text(404, "Input image not found")
                return
            content_type = mimetypes.guess_type(str(image_path))[0] or "application/octet-stream"
            self.send_bytes(200, image_path.read_bytes(), content_type)
            return

        if path.startswith("/scenario-artifact/"):
            relative = unquote(path.removeprefix("/scenario-artifact/"))
            parts = relative.split("/", 2)
            if len(parts) != 3:
                self.send_text(404, "Scenario artifact not found")
                return

            scenario_name, area, filename = parts
            if not is_safe_scenario_name(scenario_name):
                self.send_text(403, "Forbidden")
                return
            if area not in {"run", "base_snapshot", "root"}:
                self.send_text(403, "Forbidden")
                return

            scenarios_root = (self.server.output_dir / "scenarios").resolve()
            scenario_dir = (scenarios_root / scenario_name).resolve()
            if scenarios_root not in scenario_dir.parents and scenario_dir != scenarios_root:
                self.send_text(403, "Forbidden")
                return
            base_dir = scenario_dir if area == "root" else (scenario_dir / area).resolve()
            artifact_path = (base_dir / filename).resolve()
            if base_dir not in artifact_path.parents and artifact_path != base_dir:
                self.send_text(403, "Forbidden")
                return
            if not artifact_path.exists() or not artifact_path.is_file():
                self.send_text(404, "Scenario artifact not found")
                return
            content_type = mimetypes.guess_type(str(artifact_path))[0] or "application/octet-stream"
            self.send_bytes(200, artifact_path.read_bytes(), content_type)
            return

        self.send_text(404, "Not found")

    def do_POST(self) -> None:
        """Riceve messaggi chat e restituisce una risposta placeholder."""
        parsed = urlparse(self.path)
        workspace_mode = self.server.bind_request_workspace(parsed.query)

        if parsed.path.startswith("/api/agent/"):
            if workspace_mode != "agent":
                self.send_text(403, "AGENT workspace required")
                return
            content_length = int(self.headers.get("Content-Length") or 0)
            raw_body = self.rfile.read(content_length) if content_length else b"{}"
            try:
                payload = json.loads(raw_body.decode("utf-8"))
            except json.JSONDecodeError:
                payload = {}
            if not isinstance(payload, dict):
                payload = {}

            try:
                if parsed.path == "/api/agent/start":
                    symptom = str(payload.get("message") or "").strip()
                    model = normalize_chat_model(str(payload.get("model") or "").strip() or None)
                    start_autonomous_diagnosis(self.server.output_dir, symptom, model)
                    append_experiment2_chat_event(
                        output_dir=self.server.output_dir,
                        batch=self.server.batch,
                        circuit=self.server.circuit,
                        experiment=self.server.experiment,
                        role="user",
                        content=symptom,
                        model=None,
                        selected_run="base",
                        used_image=False,
                    )
                    state = run_autonomous_iteration(
                        output_dir=self.server.output_dir,
                        batch=self.server.batch,
                        circuit=self.server.circuit,
                        experiment=str(self.server.experiment or "experiment4"),
                        ngspice_executable=self.server.ngspice_executable,
                    )
                elif parsed.path == "/api/agent/step":
                    state = run_autonomous_iteration(
                        output_dir=self.server.output_dir,
                        batch=self.server.batch,
                        circuit=self.server.circuit,
                        experiment=str(self.server.experiment or "experiment4"),
                        ngspice_executable=self.server.ngspice_executable,
                    )
                elif parsed.path == "/api/agent/stop":
                    state = stop_autonomous_diagnosis(self.server.output_dir)
                else:
                    self.send_text(404, "Not found")
                    return
            except AutonomousControllerError as exc:
                body = json.dumps({"status": "error", "continue": False, "reply": str(exc)}, ensure_ascii=False)
                self.send_text(400, body, "application/json; charset=utf-8")
                return

            summary = summarize_autonomous_state(state, self.server.output_dir)
            append_experiment2_chat_event(
                output_dir=self.server.output_dir,
                batch=self.server.batch,
                circuit=self.server.circuit,
                experiment=self.server.experiment,
                role="system" if parsed.path == "/api/agent/stop" else "assistant",
                content=str(summary.get("reply") or ""),
                model=str(state.get("model") or "") or None,
                selected_run=str(summary.get("last_active_run") or "base"),
                used_image=False,
            )
            body = json.dumps(summary, ensure_ascii=False)
            self.send_text(200, body, "application/json; charset=utf-8")
            return

        if parsed.path == "/api/chat-history/clear":
            clear_result = clear_experiment2_session_state(
                output_dir=self.server.output_dir,
                batch=self.server.batch,
                circuit=self.server.circuit,
                experiment=self.server.experiment,
            )
            if workspace_mode == "agent":
                clear_result["autonomous_state_cleared"] = clear_diagnosis(self.server.output_dir)
            body = json.dumps(clear_result, ensure_ascii=False)
            self.send_text(200, body, "application/json; charset=utf-8")
            return

        if parsed.path != "/api/chat":
            self.send_text(404, "Not found")
            return

        content_length = int(self.headers.get("Content-Length") or 0)
        raw_body = self.rfile.read(content_length)
        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            payload = {}

        user_message = str(payload.get("message") or "").strip()
        requested_model = normalize_chat_model(str(payload.get("model") or "").strip() or None)
        active_run = str(payload.get("active_run") or "base").strip() or "base"
        if not user_message:
            body = json.dumps({"reply": "Write a symptom before sending the message.", "debug": []}, ensure_ascii=False)
            self.send_text(200, body, "application/json; charset=utf-8")
            return

        append_experiment2_chat_event(
            output_dir=self.server.output_dir,
            batch=self.server.batch,
            circuit=self.server.circuit,
            experiment=self.server.experiment,
            role="user",
            content=user_message,
            model=None,
            selected_run=active_run,
            used_image=False,
        )

        if detect_scenario_list_request(user_message):
            registry = read_experiment2_scenario_registry(
                self.server.output_dir,
                self.server.batch,
                self.server.circuit,
                self.server.experiment,
            )
            response_path = self.server.output_dir / CHAT_RESPONSE_NAME
            if registry is not None and not registry.get("scenarios") and response_path.exists():
                register_experiment2_scenarios_from_response(
                    output_dir=self.server.output_dir,
                    batch=self.server.batch,
                    circuit=self.server.circuit,
                    experiment=self.server.experiment,
                    response_text=read_text_safe(response_path),
                )
                registry = read_experiment2_scenario_registry(
                    self.server.output_dir,
                    self.server.batch,
                    self.server.circuit,
                    self.server.experiment,
                )
            if registry is not None:
                registry = sync_scenario_registry_with_existing_runs(
                    self.server.output_dir,
                    self.server.batch,
                    self.server.circuit,
                    self.server.experiment,
                )
            reply = build_scenario_registry_summary(registry)
            append_experiment2_chat_event(
                output_dir=self.server.output_dir,
                batch=self.server.batch,
                circuit=self.server.circuit,
                experiment=self.server.experiment,
                role="system",
                content=reply,
                model=requested_model,
                selected_run=active_run,
                used_image=False,
            )
            body = json.dumps({"reply": reply, "debug": ["Action: scenario registry listed"]}, ensure_ascii=False)
            self.send_text(200, body, "application/json; charset=utf-8")
            return

        scenario_result = handle_scenario_request(
            self.server.output_dir,
            user_message,
            batch=self.server.batch,
            circuit=self.server.circuit,
            experiment=self.server.experiment,
            ngspice_executable=self.server.ngspice_executable,
        )
        if scenario_result is not None:
            append_experiment2_chat_event(
                output_dir=self.server.output_dir,
                batch=self.server.batch,
                circuit=self.server.circuit,
                experiment=self.server.experiment,
                role="system",
                content=str(scenario_result.get("reply") or ""),
                model=requested_model,
                selected_run=str(scenario_result.get("active_run") or active_run),
                used_image=bool(scenario_result.get("used_image")),
                generated_files=list(scenario_result.get("generated_files") or []),
                scenario_id=str(scenario_result.get("scenario_id") or "") or None,
                scenario_outcome=scenario_result.get("scenario_outcome"),
                scenario_path=str(scenario_result.get("scenario_path") or "") or None,
            )
            body = json.dumps(scenario_result, ensure_ascii=False)
            self.send_text(200, body, "application/json; charset=utf-8")
            return

        try:
            result = run_readonly_agent_from_chat(
                batch=self.server.batch,
                circuit=self.server.circuit,
                output_dir=self.server.output_dir,
                user_problem=user_message,
                model=requested_model,
                experiment=self.server.experiment,
            )
        except Exception as exc:
            result = {
                "reply": (
                    "Agent execution failed.\n\n"
                    f"Reason: {exc}\n\n"
                    "Check the terminal and the generated chat files, if any."
                ),
                "debug": [
                    f"Attempted model: {requested_model}",
                    (
                        f"Circuit: {self.server.batch}/{self.server.experiment}/{self.server.circuit}"
                        if self.server.experiment
                        else f"Circuit: {self.server.batch}/{self.server.circuit}"
                    ),
                ],
                "used_image": False,
                "generated_files": [],
            }

        registration = register_experiment2_scenarios_from_response(
            output_dir=self.server.output_dir,
            batch=self.server.batch,
            circuit=self.server.circuit,
            experiment=self.server.experiment,
            response_text=read_text_safe(self.server.output_dir / CHAT_RESPONSE_NAME),
        )
        if registration and registration.get("summary"):
            result["reply"] = str(result.get("reply") or "") + "\n\n" + str(registration.get("summary") or "")
            debug_items = list(result.get("debug") or [])
            debug_items.append(f"Scenario registry: {registration.get('registry_path')}")
            debug_items.append(f"Registered scenarios: {len(registration.get('added') or [])}")
            result["debug"] = debug_items

        append_experiment2_chat_event(
            output_dir=self.server.output_dir,
            batch=self.server.batch,
            circuit=self.server.circuit,
            experiment=self.server.experiment,
            role="assistant",
            content=str(result.get("reply") or ""),
            model=requested_model,
            selected_run=active_run,
            used_image=bool(result.get("used_image")),
            generated_files=list(result.get("generated_files") or []),
        )

        body = json.dumps(result, ensure_ascii=False)
        self.send_text(200, body, "application/json; charset=utf-8")


class WebChatServer(ThreadingHTTPServer):
    """Server locale con stato minimo della run selezionata."""

    def __init__(
        self,
        server_address: tuple[str, int],
        handler_class: type[BaseHTTPRequestHandler],
        batch: str,
        circuit: str,
        output_dir: Path,
        experiment: str | None = None,
        ngspice_executable: str | None = None,
        workspace_dirs: dict[str, Path] | None = None,
        default_workspace_mode: str | None = None,
    ) -> None:
        """Inizializza il server e gli eventuali workspace selezionabili."""
        super().__init__(server_address, handler_class)
        self.batch = batch
        self.circuit = circuit
        self.experiment = experiment
        self._default_output_dir = output_dir
        self.workspace_dirs = dict(workspace_dirs or {})
        self.default_workspace_mode = default_workspace_mode
        self._request_workspace = threading.local()
        self.ngspice_executable = ngspice_executable

    @property
    def output_dir(self) -> Path:
        """Restituisce la root associata alla richiesta HTTP corrente."""
        return getattr(self._request_workspace, "output_dir", self._default_output_dir)

    @property
    def available_workspace_modes(self) -> tuple[str, ...]:
        """Elenca in ordine stabile le modalita offerte dalla pagina."""
        return tuple(self.workspace_dirs.keys())

    def bind_request_workspace(self, query: str) -> str | None:
        """Associa la richiesta corrente al workspace indicato nell'URL."""
        if not self.workspace_dirs:
            self._request_workspace.output_dir = self._default_output_dir
            self._request_workspace.mode = None
            return None

        requested_mode = str((parse_qs(query).get("mode") or [""])[0]).strip().lower()
        selected_mode = requested_mode if requested_mode in self.workspace_dirs else self.default_workspace_mode
        if selected_mode not in self.workspace_dirs:
            selected_mode = next(iter(self.workspace_dirs))

        self._request_workspace.output_dir = self.workspace_dirs[selected_mode]
        self._request_workspace.mode = selected_mode
        return selected_mode


def serve_web_chat(
    *,
    batch: str,
    circuit: str,
    output_dir: Path,
    experiment: str | None = None,
    variant: str | None = None,
    host: str = "127.0.0.1",
    port: int = 8765,
    ngspice_executable: str | None = None,
    workspace_dirs: dict[str, Path] | None = None,
    default_workspace_mode: str | None = None,
    open_browser: bool = True,
) -> None:
    """Avvia la webchat su directory gia risolte dal chiamante.

    L'interfaccia esplicita permette all'orchestratore unificato di fornire le
    due copie CHAT/AGENT senza dipendere dalla struttura storica degli output.
    """
    resolved_output_dir = Path(output_dir).resolve()
    resolved_workspaces = {
        mode: Path(path).resolve()
        for mode, path in (workspace_dirs or {}).items()
    }
    missing_workspaces = [
        mode for mode, path in resolved_workspaces.items() if not path.is_dir()
    ]
    if missing_workspaces:
        raise FileNotFoundError(
            "Workspace web mancanti: " + ", ".join(missing_workspaces)
        )
    if not resolved_output_dir.is_dir():
        raise FileNotFoundError(
            f"Directory output Pipeline 2.0 non trovata: {resolved_output_dir}"
        )
    if not INDEX_TEMPLATE.is_file():
        raise FileNotFoundError(f"Template webchat non trovato: {INDEX_TEMPLATE}")

    server = WebChatServer(
        (host, port),
        WebChatHandler,
        batch=batch,
        circuit=circuit,
        experiment=experiment,
        output_dir=resolved_output_dir,
        ngspice_executable=ngspice_executable,
        workspace_dirs=resolved_workspaces,
        default_workspace_mode=default_workspace_mode,
    )

    url = f"http://{host}:{port}/"
    if default_workspace_mode:
        url += f"?mode={default_workspace_mode}"
    print(f"Pipeline 2.0 diagnostic web chat: {url}")
    if experiment:
        print(f"Experiment: {experiment}")
    if variant:
        print(f"Variant: {variant}")
    if resolved_workspaces:
        print(f"Workspace modes: {', '.join(resolved_workspaces)}")
    print(f"Output directory: {resolved_output_dir}")
    print("Press Ctrl+C to stop the temporary local server.")

    if open_browser and os.environ.get("PIPELINE2_NO_BROWSER") != "1":
        webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping web chat server.")
    finally:
        server.server_close()


def parse_args() -> argparse.Namespace:
    """Legge gli argomenti da terminale."""
    parser = argparse.ArgumentParser(description="Launch the temporary Pipeline 2.0 diagnostic web chat.")
    parser.add_argument("--batch", required=True, help="Batch name, for example batchA.")
    parser.add_argument("--circuit", required=True, help="Circuit id, for example a10.")
    parser.add_argument(
        "--experiment",
        default=None,
        help=(
            "Optional experiment name, for example experiment2. "
            "When set, reads outputs/pipeline2.0/<batch>/<experiment>/<circuit>."
        ),
    )
    parser.add_argument(
        "--variant",
        default=None,
        help="Optional subfolder inside the experiment, for example feed_nodes.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Local host to bind.")
    parser.add_argument("--port", type=int, default=8765, help="Local port to use.")
    parser.add_argument("--no-browser", action="store_true", help="Do not open the browser automatically.")
    parser.add_argument("--ngspice-executable", default=None, help="Optional ngspice executable path for scenario runs.")
    return parser.parse_args()


def main() -> None:
    """Avvia il server diagnostico locale."""
    args = parse_args()
    if not is_safe_path_name(args.experiment):
        raise SystemExit(f"Invalid experiment name: {args.experiment}")
    if not is_safe_path_name(args.variant):
        raise SystemExit(f"Invalid experiment variant: {args.variant}")
    if args.variant and not args.experiment:
        raise SystemExit("--variant requires --experiment.")

    workspace_dirs: dict[str, Path] = {}
    default_workspace_mode: str | None = None
    # CHAT e AGENT devono leggere due copie indipendenti della stessa base 01-08.
    if args.experiment in MULTI_WORKSPACE_EXPERIMENTS and not args.variant:
        workspace_dirs = {
            "chat": build_output_dir(args.batch, args.circuit, args.experiment, "chat"),
            "agent": build_output_dir(args.batch, args.circuit, args.experiment, "agent"),
        }
        default_workspace_mode = "chat"
        missing_workspaces = [mode for mode, path in workspace_dirs.items() if not path.is_dir()]
        if missing_workspaces:
            raise SystemExit(
                f"Missing {args.experiment} workspace(s): " + ", ".join(missing_workspaces)
            )
        output_dir = workspace_dirs[default_workspace_mode]
    else:
        output_dir = build_output_dir(args.batch, args.circuit, args.experiment, args.variant)

    try:
        serve_web_chat(
            batch=args.batch,
            circuit=args.circuit,
            experiment=args.experiment,
            variant=args.variant,
            output_dir=output_dir,
            host=args.host,
            port=args.port,
            ngspice_executable=args.ngspice_executable,
            workspace_dirs=workspace_dirs,
            default_workspace_mode=default_workspace_mode,
            open_browser=not args.no_browser,
        )
    except FileNotFoundError as error:
        raise SystemExit(str(error)) from error


if __name__ == "__main__":
    main()
