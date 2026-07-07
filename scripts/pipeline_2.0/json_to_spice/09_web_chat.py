"""
Interfaccia web locale temporanea per la chat diagnostica.

Questo script avvia un piccolo server locale, senza database e senza stato
persistente obbligatorio. Serve come step 09 della Pipeline 2.0 per
visualizzare gli output del circuito, parlare con l'agente e orchestrare gli
scenari controllati.

La parte HTML vive in `web_chat/templates/`, cosi il layout puo crescere senza
trasformare questo script in un file troppo grande.

Responsabilita della versione corrente:

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
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from agent_readonly.openai_runner import write_agent_response
from agent_readonly.preview_builder import write_agent_input_preview
from agent_readonly.prompt_builder import write_agent_prompt


PROJECT_ROOT = Path(__file__).resolve().parents[3]
WEB_CHAT_DIR = Path(__file__).resolve().parent / "web_chat"
TEMPLATE_DIR = WEB_CHAT_DIR / "templates"
INDEX_TEMPLATE = TEMPLATE_DIR / "index.html"
STEP10_PATH = Path(__file__).resolve().parent / "10_build_diagnostic_context.py"
STEP12_PATH = Path(__file__).resolve().parent / "12_controlled_scenarios.py"
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
CHAT_HISTORY_JSON_NAME = "chat_history.json"
CHAT_HISTORY_MD_NAME = "chat_history.md"
SCENARIO_REGISTRY_JSON_NAME = "scenario_registry.json"
SCENARIO_REGISTRY_MD_NAME = "scenario_registry.md"

SCENARIO_BASE_FILES = [
    "01_graph.json",
    "02_normalized_circuit.json",
    "03_node_map.json",
    "04_values_bound.json",
    "06_component_rules.json",
    "07_netlist.cir",
    "07_spice_emit_report.json",
    "08_spice_run.json",
    "08_ngspice_stdout.txt",
    "08_ngspice_stderr.txt",
    "08_tran.csv",
    "08_tran_plot.png",
    "08_tran_plot.svg",
]

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
    """
    Decodifica entita HTML dentro stringhe, liste e dizionari semplici.

    Ci serve per evitare che testi come `dell&#x27;emettitore` finiscano visibili
    nella UI quando uno scenario e stato salvato con caratteri gia escapati.
    """
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
    return repair_common_mojibake(normalized)


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
    """Abilita history/registry server-side per Esperimento 2 e sottofasi."""
    return bool(experiment) and str(experiment).startswith("experiment2")


def build_experiment2_chat_dir(output_dir: Path, experiment: str | None) -> Path | None:
    """Restituisce la cartella della chat history ufficiale di Esperimento 2."""
    if not is_experiment2_history_enabled(experiment):
        return None
    return output_dir / EXPERIMENT2_CHAT_DIRNAME


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
    """Azzera la chat history ufficiale di Esperimento 2."""
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
    """Azzera il registry scenari ufficiale di Esperimento 2."""
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
    Reset completo della sessione Experiment 2 per un circuito.

    Non tocca gli output base 01-08 copiati nell'esperimento. Azzera solo la
    conversazione, il registry, le run scenario e gli artefatti chat 10/11.
    """
    if not is_experiment2_history_enabled(experiment):
        return {
            "cleared": False,
            "reason": "Experiment 2 session clear is only enabled for experiment2.",
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
    """Costruisce il registro scenari file-based di Esperimento 2."""
    timestamp = datetime.now().isoformat(timespec="seconds")
    return {
        "source_format": "pipeline2.0_experiment2_scenario_registry",
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
    """Legge il registro scenari ufficiale di Esperimento 2."""
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

    data.setdefault("source_format", "pipeline2.0_experiment2_scenario_registry")
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
        "# Experiment 2 scenario registry",
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
    """Firma semplice per evitare di registrare duplicati identici."""
    comparable = {
        "title": scenario.get("title"),
        "hypothesis": scenario.get("hypothesis"),
        "actions": scenario.get("actions") or [],
        "analysis": scenario.get("analysis"),
        "compare": scenario.get("compare") or [],
    }
    return json.dumps(comparable, sort_keys=True, ensure_ascii=False)


def scenario_is_executable(scenario: dict[str, Any]) -> bool:
    """Uno scenario e eseguibile da step 12 solo se contiene azioni."""
    actions = scenario.get("actions")
    return isinstance(actions, list) and bool(actions)


def register_experiment2_scenarios_from_response(
    output_dir: Path,
    batch: str,
    circuit: str,
    experiment: str | None,
    response_text: str,
) -> dict[str, Any] | None:
    """Estrae gli scenari da una risposta agente e li accoda al registry."""
    registry = read_experiment2_scenario_registry(output_dir, batch, circuit, experiment)
    chat_dir = build_experiment2_chat_dir(output_dir, experiment)
    if registry is None or chat_dir is None:
        return None

    extracted = extract_scenarios_from_response(response_text)
    if not extracted:
        return {"added": [], "summary": ""}

    existing_signatures = {
        str(item.get("signature"))
        for item in registry.get("scenarios", [])
        if isinstance(item, dict) and item.get("signature")
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
            "analysis": scenario.get("analysis") or "op",
            "compare": scenario.get("compare") or [],
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


def build_output_dir(batch: str, circuit: str, experiment: str | None = None) -> Path:
    """Calcola la cartella output della Pipeline 2.0 per un circuito."""
    if experiment:
        return PROJECT_ROOT / "outputs" / "pipeline2.0" / batch / experiment / circuit
    return PROJECT_ROOT / "outputs" / "pipeline2.0" / batch / circuit


def find_input_image_path(batch: str, circuit: str, output_dir: Path) -> Path | None:
    """Trova l'immagine originale usata dalla Pipeline 1.0, quando disponibile."""
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


def render_run_selector(output_dir: Path, active_run: str) -> str:
    """Crea la sidebar con base run e scenari disponibili."""
    base_status = build_status(output_dir)
    base_active = " active" if active_run == "base" else ""
    sections = [
        f"""
        <a class="run-item{base_active}" href="/">
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
        sections.append(
            f"""
            <a class="run-item scenario-run{scenario_active}" href="/?run={html.escape(scenario["id"])}">
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


def render_artifacts(output_dir: Path, plot_url: str = "/artifact/08_tran_plot.png") -> str:
    """Crea i pannelli richiudibili con gli artefatti della pipeline."""
    sections: list[str] = [render_artifact_sections(output_dir, ARTIFACTS)]

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
    outcome_label = str(outcome.get("label") or "Outcome unknown")
    outcome_reason = str(outcome.get("reason") or "No diagnostic outcome available.")
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


def render_scenario_content(output_dir: Path, scenario_name: str) -> dict[str, str]:
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
    )

    return {
        "title": f"Scenario - {str(scenario_status.get('scenario_id') or scenario_name)}",
        "output_dir": project_relative(scenario_dir),
        "status_cards": render_status_cards(status),
        "artifacts": "\n".join([render_comparison_summary(scenario_dir), root_artifacts, run_artifacts]),
        "subtitle": title,
    }


def render_image_section(batch: str, circuit: str, output_dir: Path) -> str:
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

    return f"""
    <details class="artifact" open>
      <summary>
        <span>Circuit Image</span>
        <small>{html.escape(project_relative(image_path))}</small>
      </summary>
      <div class="image-wrap">
        <img src="/input-image" alt="Original circuit image">
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


def render_page(
    batch: str,
    circuit: str,
    output_dir: Path,
    active_run: str = "base",
    experiment: str | None = None,
) -> str:
    """Renderizza la pagina HTML principale usando il template esterno."""
    template = read_text_safe(INDEX_TEMPLATE)
    active_run = active_run if active_run else "base"
    circuit_label = f"{batch} / {experiment} / {circuit}" if experiment else f"{batch} / {circuit}"
    chat_storage_key = (
        f"pipeline2_chat_{batch}_{experiment}_{circuit}"
        if experiment
        else f"pipeline2_chat_{batch}_{circuit}"
    )
    model_storage_key = (
        f"pipeline2_chat_model_{batch}_{experiment}_{circuit}"
        if experiment
        else f"pipeline2_chat_model_{batch}_{circuit}"
    )
    server_chat_history_items = build_server_chat_history_items(output_dir, batch, circuit, experiment)
    chat_history_enabled = is_experiment2_history_enabled(experiment)

    if active_run == "base":
        status = build_status(output_dir)
        spice_status = str(status["spice_status"])
        header_meta = f"{circuit_label} - Base run - {spice_status}"
        title = "Base run"
        subtitle = project_relative(output_dir)
        status_cards = render_status_cards(status)
        image_section = render_image_section(batch, circuit, output_dir)
        artifacts = render_artifacts(output_dir)
    else:
        available_scenarios = {scenario["id"] for scenario in list_scenario_runs(output_dir)}
        if active_run not in available_scenarios:
            return render_page(batch, circuit, output_dir, active_run="base", experiment=experiment)
        scenario_content = render_scenario_content(output_dir, active_run)
        scenario_state = read_scenario_status(output_dir / "scenarios" / active_run).get("status") or "not available"
        header_meta = f"{circuit_label} - {active_run} - {scenario_state}"
        title = scenario_content["title"]
        subtitle = scenario_content.get("subtitle") or scenario_content["output_dir"]
        status_cards = scenario_content["status_cards"]
        image_section = render_image_section(batch, circuit, output_dir)
        artifacts = scenario_content["artifacts"]

    return fill_template(
        template,
        {
            "PAGE_TITLE": html.escape(f"Pipeline 2.0 Diagnostic Chat - {circuit}"),
            "HEADER_META": html.escape(header_meta),
            "CHAT_STORAGE_KEY": html.escape(chat_storage_key),
            "MODEL_STORAGE_KEY": html.escape(model_storage_key),
            "DEFAULT_CHAT_MODEL": html.escape(CHAT_MODEL),
            "ACTIVE_RUN_ID": html.escape(active_run),
            "SERVER_CHAT_HISTORY_JSON": json_for_html(server_chat_history_items),
            "SERVER_CHAT_HISTORY_ENABLED": "true" if chat_history_enabled else "false",
            "MODEL_OPTIONS": render_model_options(CHAT_MODEL),
            "RUN_SELECTOR": render_run_selector(output_dir, active_run),
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


def load_step12_module() -> Any:
    """Carica lo step 12 anche se il file inizia con un numero."""
    spec = importlib.util.spec_from_file_location("pipeline2_step12", STEP12_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load step 12 from {STEP12_PATH}")

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
    """Conta quante cartelle scenario esistono gia per il circuito."""
    scenarios_root = output_dir / "scenarios"
    if not scenarios_root.exists() or not scenarios_root.is_dir():
        return 0
    return sum(1 for path in scenarios_root.iterdir() if path.is_dir())


def is_safe_scenario_name(name: str) -> bool:
    """Accetta solo nomi scenario semplici usabili come directory locali."""
    return bool(re.fullmatch(r"[A-Za-z0-9_.-]+", name)) and name not in {".", ".."}


def prepare_scenario_folder(
    output_dir: Path,
    selected: dict[str, Any],
    requested_index: int | str,
    response_path: Path,
) -> dict[str, Path]:
    """
    Prepara la cartella dello scenario senza eseguirlo.

    Questo e lo step 2: salviamo solo i metadati necessari alla futura
    esecuzione controllata, senza modificare la base run e senza chiamare SPICE.
    """
    fallback_id = "scenario_latest" if requested_index == "latest" else f"scenario_{requested_index}"
    scenario_id = str(selected.get("scenario_id") or fallback_id)
    scenario_dir = output_dir / "scenarios" / safe_scenario_dir_name(scenario_id)
    scenario_dir.mkdir(parents=True, exist_ok=True)

    scenario_path = scenario_dir / "scenario.json"
    status_path = scenario_dir / "scenario_status.json"
    scenario_payload = {
        key: value
        for key, value in selected.items()
        if not str(key).startswith("_registry_")
    }

    status = {
        "status": "prepared",
        "stage": "scenario_folder_created",
        "message": "Scenario selected and saved. No pipeline files were modified and SPICE was not executed.",
        "scenario_id": scenario_id,
        "requested_index": requested_index,
        "base_output_dir": project_relative(output_dir),
        "source_agent_response": project_relative(response_path),
        "scenario_file": project_relative(scenario_path),
        "created_or_updated_at": datetime.now().isoformat(timespec="seconds"),
        "next_step": "Implement controlled scenario execution in 12_controlled_scenarios.py.",
    }

    scenario_path.write_text(json.dumps(scenario_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    status_path.write_text(json.dumps(status, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return {
        "scenario_dir": scenario_dir,
        "scenario_path": scenario_path,
        "status_path": status_path,
    }


def copy_base_run_for_scenario(output_dir: Path, scenario_dir: Path) -> dict[str, Any]:
    """
    Crea le cartelle base_snapshot e run dello scenario.

    base_snapshot conserva una copia degli output originali 01-08.
    run contiene la copia che in futuro potra essere modificata dallo scenario.
    """
    base_snapshot_dir = scenario_dir / "base_snapshot"
    run_dir = scenario_dir / "run"
    base_snapshot_dir.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)

    copied_files: list[str] = []
    missing_files: list[str] = []

    for filename in SCENARIO_BASE_FILES:
        source_path = output_dir / filename
        if not source_path.exists() or not source_path.is_file():
            missing_files.append(filename)
            continue

        shutil.copy2(source_path, base_snapshot_dir / filename)
        shutil.copy2(source_path, run_dir / filename)
        copied_files.append(filename)

    manifest = {
        "status": "copied",
        "message": "Base run copied into base_snapshot and run. No scenario action was applied.",
        "base_output_dir": project_relative(output_dir),
        "base_snapshot_dir": project_relative(base_snapshot_dir),
        "run_dir": project_relative(run_dir),
        "copied_files": copied_files,
        "missing_optional_files": missing_files,
        "created_or_updated_at": datetime.now().isoformat(timespec="seconds"),
    }
    manifest_path = scenario_dir / "scenario_copy_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return {
        "base_snapshot_dir": base_snapshot_dir,
        "run_dir": run_dir,
        "manifest_path": manifest_path,
        "copied_files": copied_files,
        "missing_files": missing_files,
    }


def apply_controlled_scenario(
    scenario_dir: Path,
    run_spice: bool = True,
    ngspice_executable: str | None = None,
) -> dict[str, Any]:
    """Chiama lo step 12 per applicare le azioni supportate ed eseguire SPICE."""
    step12 = load_step12_module()
    report = step12.apply_scenario(
        scenario_dir,
        run_spice=run_spice,
        ngspice_executable=ngspice_executable,
    )
    return report if isinstance(report, dict) else {}


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
            f"Questo scenario spiega bene il sintomo osservato e puo fermare l'automazione: "
            f"l'ipotesi testata da **{title}** risulta fortemente confermata."
        ),
        "partially_resolved": (
            f"Questo scenario ha dato un indizio utile ma non basta ancora da solo: "
            f"l'ipotesi testata da **{title}** e supportata solo in parte."
        ),
        "not_resolved": (
            f"Questo scenario non ha spiegato il sintomo: "
            f"l'ipotesi testata da **{title}** non e confermata dai risultati."
        ),
        "unknown": (
            f"Questo scenario resta inconcludente: "
            f"i risultati non bastano ancora per confermare o escludere l'ipotesi testata da **{title}**."
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
        lines.append(f"Ipotesi confermata: {hypothesis}")
    if changed_lines:
        lines.extend(
            [
                "",
                "Le grandezze piu importanti sono cambiate cosi:",
                *changed_lines,
            ]
        )
    lines.extend(
        [
            "",
            (
                "Interpretazione pratica: il comportamento osservato nello scenario spiega il sintomo meglio della run base, quindi per ora non serve continuare automaticamente con altri scenari."
                if stop_automation
                else "Interpretazione pratica: il comportamento osservato nello scenario aggiunge evidenza utile rispetto alla run base, ma non chiude ancora da solo la diagnosi."
            ),
        ]
    )
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

    scenario_paths = prepare_scenario_folder(
        output_dir=output_dir,
        selected=selected,
        requested_index=requested_index,
        response_path=response_path,
    )
    copy_result = copy_base_run_for_scenario(
        output_dir=output_dir,
        scenario_dir=scenario_paths["scenario_dir"],
    )
    apply_report = apply_controlled_scenario(
        scenario_paths["scenario_dir"],
        run_spice=True,
        ngspice_executable=ngspice_executable,
    )
    applied_actions = apply_report.get("applied_actions") or []
    failed_actions = apply_report.get("failed_actions") or []
    unsupported_actions = apply_report.get("unsupported_actions") or []
    spice_status = apply_report.get("spice_status") or "not executed"
    comparison_summary = apply_report.get("comparison_summary") or {}
    diagnostic_outcome = apply_report.get("diagnostic_outcome") or {}
    if not isinstance(diagnostic_outcome, dict):
        diagnostic_outcome = {}
    outcome_label = diagnostic_outcome.get("label") or "Outcome unknown"
    outcome_status = diagnostic_outcome.get("status") or "unknown"
    outcome_reason = diagnostic_outcome.get("reason") or "No diagnostic outcome available."
    outcome_next_step = diagnostic_outcome.get("next_step") or "Continue with the diagnostic workflow."
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
        outcome_next_step = "Scenario budget exhausted. Ask the agent for a final diagnostic conclusion."

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
            f"Esito diagnostico scenario: **{outcome_label}** (`{outcome_status}`).\n\n"
            f"Motivo: {outcome_reason}\n\n"
            f"Decisione automatica: **{'stop' if stop_automation else 'continue'}**.\n\n"
            f"Prossimo passo: {outcome_next_step}\n\n"
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
    """Gestisce la pagina web e le piccole API locali dello scheletro."""

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
        path = parsed.path

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
        if parsed.path == "/api/chat-history/clear":
            clear_result = clear_experiment2_session_state(
                output_dir=self.server.output_dir,
                batch=self.server.batch,
                circuit=self.server.circuit,
                experiment=self.server.experiment,
            )
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
    ) -> None:
        super().__init__(server_address, handler_class)
        self.batch = batch
        self.circuit = circuit
        self.experiment = experiment
        self.output_dir = output_dir
        self.ngspice_executable = ngspice_executable


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
    parser.add_argument("--host", default="127.0.0.1", help="Local host to bind.")
    parser.add_argument("--port", type=int, default=8765, help="Local port to use.")
    parser.add_argument("--no-browser", action="store_true", help="Do not open the browser automatically.")
    parser.add_argument("--ngspice-executable", default=None, help="Optional ngspice executable path for scenario runs.")
    return parser.parse_args()


def main() -> None:
    """Avvia il server locale temporaneo."""
    args = parse_args()
    if not is_safe_path_name(args.experiment):
        raise SystemExit(f"Invalid experiment name: {args.experiment}")

    output_dir = build_output_dir(args.batch, args.circuit, args.experiment)

    if not output_dir.exists():
        raise SystemExit(f"Pipeline 2.0 output directory not found: {output_dir}")
    if not INDEX_TEMPLATE.exists():
        raise SystemExit(f"Web chat template not found: {INDEX_TEMPLATE}")

    server = WebChatServer(
        (args.host, args.port),
        WebChatHandler,
        batch=args.batch,
        circuit=args.circuit,
        experiment=args.experiment,
        output_dir=output_dir,
        ngspice_executable=args.ngspice_executable,
    )

    url = f"http://{args.host}:{args.port}/"
    print(f"Pipeline 2.0 diagnostic web chat: {url}")
    if args.experiment:
        print(f"Experiment: {args.experiment}")
    print(f"Output directory: {output_dir}")
    print("Press Ctrl+C to stop the temporary local server.")

    if not args.no_browser and os.environ.get("PIPELINE2_NO_BROWSER") != "1":
        webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping web chat server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
