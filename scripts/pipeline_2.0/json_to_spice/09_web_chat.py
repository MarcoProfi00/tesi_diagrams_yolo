"""
Interfaccia web locale temporanea per la chat diagnostica.

Questo script avvia un piccolo server locale, senza database e senza stato
persistente obbligatorio. Serve come primo scheletro del futuro step 09 della
Pipeline 2.0.

La parte HTML vive in `web_chat/templates/`, cosi il layout puo crescere senza
trasformare questo script in un file troppo grande.

Responsabilita previste:

- aprire una pagina locale nel browser;
- mostrare la run principale del circuito selezionato;
- visualizzare gli artefatti prodotti dagli step 01-08;
- lasciare una chat sempre visibile a destra;
- preparare il punto di aggancio futuro verso 10, 11 e 12.

Per ora la chat non chiama ancora l'agente. Risponde con un placeholder, cosi
possiamo validare layout, navigazione e lettura dei file senza aggiungere
complessita.
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
CHAT_CONTEXT_NAME = "10_diagnostic_context.json"
CHAT_PREVIEW_NAME = "11_agent_input_preview_chat.md"
CHAT_PROMPT_NAME = "11_agent_prompt_chat.md"
CHAT_RESPONSE_NAME = "11_agent_response_chat.md"

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


IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg"]

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


def escape_block(text: str) -> str:
    """Prepara testo tecnico da mostrare dentro un blocco pre."""
    return html.escape(text, quote=False)


def project_relative(path: Path) -> str:
    """Restituisce un path leggibile relativo alla root del progetto."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def build_output_dir(batch: str, circuit: str) -> Path:
    """Calcola la cartella output della Pipeline 2.0 per un circuito."""
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


def status_class(status: str) -> str:
    """Converte lo stato SPICE in una classe CSS semplice."""
    if status == "success":
        return "ok"
    if status in {"failed", "error"}:
        return "bad"
    return "warn"


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


def render_artifacts(output_dir: Path) -> str:
    """Crea i pannelli richiudibili con gli artefatti della pipeline."""
    sections: list[str] = []

    for title, filename, kind in ARTIFACTS:
        path = output_dir / filename
        text = read_text_safe(path)
        open_attr = " open" if filename in {"08_spice_run.json", "07_netlist.cir"} else ""
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

    plot_path = output_dir / "08_tran_plot.png"
    if plot_path.exists():
        sections.append(
            """
            <details class="artifact" open>
              <summary>
                <span>Transient Plot</span>
                <small>08_tran_plot.png</small>
              </summary>
              <div class="plot-wrap">
                <img src="/artifact/08_tran_plot.png" alt="Transient plot">
              </div>
            </details>
            """
        )

    return "\n".join(sections)


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


def fill_template(template: str, values: dict[str, str]) -> str:
    """Sostituisce placeholder semplici nel template HTML."""
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    return rendered


def render_page(batch: str, circuit: str, output_dir: Path) -> str:
    """Renderizza la pagina HTML principale usando il template esterno."""
    status = build_status(output_dir)
    output_dir_text = project_relative(output_dir)
    spice_status = str(status["spice_status"])

    template = read_text_safe(INDEX_TEMPLATE)
    header_meta = f"{batch} / {circuit} - Base run - {spice_status}"

    return fill_template(
        template,
        {
            "PAGE_TITLE": html.escape(f"Pipeline 2.0 Diagnostic Chat - {circuit}"),
            "HEADER_META": html.escape(header_meta),
            "SPICE_STATUS": html.escape(spice_status),
            "OUTPUT_DIR": html.escape(output_dir_text),
            "STATUS_CARDS": render_status_cards(status),
            "IMAGE_SECTION": render_image_section(batch, circuit, output_dir),
            "ARTIFACTS": render_artifacts(output_dir),
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
) -> Path:
    """Rigenera il manifest 10 con il problema scritto nella chat."""
    step10 = load_step10_module()
    context = step10.build_diagnostic_context(
        output_dir=output_dir,
        batch_name=batch,
        circuit_id=circuit,
        project_root=PROJECT_ROOT,
        user_problem=user_problem,
    )
    context_path = output_dir / CHAT_CONTEXT_NAME
    context_path.write_text(json.dumps(context, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return context_path


def run_readonly_agent_from_chat(
    batch: str,
    circuit: str,
    output_dir: Path,
    user_problem: str,
    model: str = CHAT_MODEL,
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
    )
    preview_path = output_dir / CHAT_PREVIEW_NAME
    prompt_path = output_dir / CHAT_PROMPT_NAME
    response_path = output_dir / CHAT_RESPONSE_NAME

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
    )

    return {
        "reply": read_text_safe(response_path),
        "debug": [
            f"Updated: {project_relative(context_path)}",
            f"Generated: {project_relative(preview_path)}",
            f"Generated: {project_relative(prompt_path)}",
            f"Generated: {project_relative(response_path)}",
            f"Model: {model}",
        ],
    }


def detect_scenario_request(user_message: str) -> int | None:
    """Riconosce richieste semplici tipo 'esegui scenario 1'."""
    normalized = user_message.lower().replace("_", " ")

    match = re.search(r"\bscenario\s*(\d+)\b", normalized)
    if match:
        return int(match.group(1))

    has_execution_intent = any(
        token in normalized
        for token in ["esegui", "prova", "facciamo", "lancia", "testa", "run", "execute"]
    )
    if not has_execution_intent:
        return None

    for word, index in SCENARIO_WORD_TO_INDEX.items():
        if re.search(rf"\b{re.escape(word)}\b", normalized):
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
            scenarios.append(data)

    return scenarios


def select_scenario(scenarios: list[dict[str, Any]], requested_index: int) -> dict[str, Any] | None:
    """Seleziona uno scenario per id tecnico o per posizione nella risposta."""
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


def prepare_scenario_folder(
    output_dir: Path,
    selected: dict[str, Any],
    requested_index: int,
    response_path: Path,
) -> dict[str, Path]:
    """
    Prepara la cartella dello scenario senza eseguirlo.

    Questo e lo step 2: salviamo solo i metadati necessari alla futura
    esecuzione controllata, senza modificare la base run e senza chiamare SPICE.
    """
    scenario_id = str(selected.get("scenario_id") or f"scenario_{requested_index}")
    scenario_dir = output_dir / "scenarios" / safe_scenario_dir_name(scenario_id)
    scenario_dir.mkdir(parents=True, exist_ok=True)

    scenario_path = scenario_dir / "scenario.json"
    status_path = scenario_dir / "scenario_status.json"

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

    scenario_path.write_text(json.dumps(selected, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
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


def apply_controlled_scenario(scenario_dir: Path) -> dict[str, Any]:
    """Chiama lo step 12 per applicare le azioni supportate senza eseguire SPICE."""
    step12 = load_step12_module()
    report = step12.apply_scenario(scenario_dir)
    return report if isinstance(report, dict) else {}


def handle_scenario_request(output_dir: Path, user_message: str) -> dict[str, Any] | None:
    """
    Gestisce gli step iniziali degli scenari.

    Per ora riconosce la scelta, recupera il JSON tecnico e prepara una cartella
    scenario separata. Non modifica la base run e non esegue SPICE.
    """
    requested_index = detect_scenario_request(user_message)
    if requested_index is None:
        return None

    response_path = output_dir / CHAT_RESPONSE_NAME
    if not response_path.exists():
        return {
            "reply": (
                f"Ho capito che vuoi eseguire lo scenario {requested_index}, "
                "ma non trovo ancora una risposta agente con scenari.\n\n"
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
                f"Ho riconosciuto la richiesta per lo scenario {requested_index}, "
                "ma non ho trovato uno scenario JSON corrispondente nell'ultima risposta agente.\n\n"
                f"Scenari JSON trovati: {len(scenarios)}"
            ),
            "debug": [f"Read: {project_relative(response_path)}"],
        }

    selected_json = json.dumps(selected, indent=2, ensure_ascii=False)
    title = selected.get("title") or selected.get("scenario_id") or f"scenario {requested_index}"
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
    apply_report = apply_controlled_scenario(scenario_paths["scenario_dir"])
    applied_actions = apply_report.get("applied_actions") or []
    failed_actions = apply_report.get("failed_actions") or []
    unsupported_actions = apply_report.get("unsupported_actions") or []

    return {
        "reply": (
            f"Ho riconosciuto la richiesta di eseguire **scenario {requested_index}**.\n\n"
            f"Scenario selezionato: **{title}**.\n\n"
            "Per ora siamo nello **step 5**: ho creato una cartella scenario separata, "
            "ho copiato la base run e ho applicato le azioni supportate solo alla netlist in `run/`.\n\n"
            "Non ho modificato la base run originale e non ho ancora rieseguito SPICE.\n\n"
            f"Cartella scenario:\n\n`{project_relative(scenario_paths['scenario_dir'])}`\n\n"
            f"Snapshot base:\n\n`{project_relative(copy_result['base_snapshot_dir'])}`\n\n"
            f"Run scenario modificata:\n\n`{project_relative(copy_result['run_dir'])}`\n\n"
            f"File copiati: **{len(copy_result['copied_files'])}**.\n\n"
            f"Azioni applicate: **{len(applied_actions)}**. "
            f"Azioni non supportate: **{len(unsupported_actions)}**. "
            f"Azioni fallite: **{len(failed_actions)}**.\n\n"
            "Scenario tecnico recuperato:\n\n"
            f"```json\n{selected_json}\n```"
        ),
        "debug": [
            f"Read: {project_relative(response_path)}",
            f"Scenarios found: {len(scenarios)}",
            f"Selected: {selected.get('scenario_id')}",
            f"Written: {project_relative(scenario_paths['scenario_path'])}",
            f"Written: {project_relative(scenario_paths['status_path'])}",
            f"Written: {project_relative(copy_result['manifest_path'])}",
            f"Written: {project_relative(scenario_paths['scenario_dir'] / '12_controlled_scenarios.json')}",
            f"Copied files: {len(copy_result['copied_files'])}",
            f"Applied actions: {len(applied_actions)}",
            f"Unsupported actions: {len(unsupported_actions)}",
            f"Failed actions: {len(failed_actions)}",
            "Action: scenario applied without SPICE execution",
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
            page = render_page(self.server.batch, self.server.circuit, self.server.output_dir)
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

        self.send_text(404, "Not found")

    def do_POST(self) -> None:
        """Riceve messaggi chat e restituisce una risposta placeholder."""
        parsed = urlparse(self.path)
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
        if not user_message:
            body = json.dumps({"reply": "Write a symptom before sending the message.", "debug": []}, ensure_ascii=False)
            self.send_text(200, body, "application/json; charset=utf-8")
            return

        scenario_result = handle_scenario_request(self.server.output_dir, user_message)
        if scenario_result is not None:
            body = json.dumps(scenario_result, ensure_ascii=False)
            self.send_text(200, body, "application/json; charset=utf-8")
            return

        try:
            result = run_readonly_agent_from_chat(
                batch=self.server.batch,
                circuit=self.server.circuit,
                output_dir=self.server.output_dir,
                user_problem=user_message,
                model=CHAT_MODEL,
            )
        except Exception as exc:
            result = {
                "reply": (
                    "Agent execution failed.\n\n"
                    f"Reason: {exc}\n\n"
                    "Check the terminal and the generated chat files, if any."
                ),
                "debug": [
                    f"Attempted model: {CHAT_MODEL}",
                    f"Circuit: {self.server.batch}/{self.server.circuit}",
                ],
            }

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
    ) -> None:
        super().__init__(server_address, handler_class)
        self.batch = batch
        self.circuit = circuit
        self.output_dir = output_dir


def parse_args() -> argparse.Namespace:
    """Legge gli argomenti da terminale."""
    parser = argparse.ArgumentParser(description="Launch the temporary Pipeline 2.0 diagnostic web chat.")
    parser.add_argument("--batch", required=True, help="Batch name, for example batchA.")
    parser.add_argument("--circuit", required=True, help="Circuit id, for example a10.")
    parser.add_argument("--host", default="127.0.0.1", help="Local host to bind.")
    parser.add_argument("--port", type=int, default=8765, help="Local port to use.")
    parser.add_argument("--no-browser", action="store_true", help="Do not open the browser automatically.")
    return parser.parse_args()


def main() -> None:
    """Avvia il server locale temporaneo."""
    args = parse_args()
    output_dir = build_output_dir(args.batch, args.circuit)

    if not output_dir.exists():
        raise SystemExit(f"Pipeline 2.0 output directory not found: {output_dir}")
    if not INDEX_TEMPLATE.exists():
        raise SystemExit(f"Web chat template not found: {INDEX_TEMPLATE}")

    server = WebChatServer(
        (args.host, args.port),
        WebChatHandler,
        batch=args.batch,
        circuit=args.circuit,
        output_dir=output_dir,
    )

    url = f"http://{args.host}:{args.port}/"
    print(f"Pipeline 2.0 diagnostic web chat: {url}")
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
