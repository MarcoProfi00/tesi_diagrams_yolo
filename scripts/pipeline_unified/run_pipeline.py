"""Orchestratore progressivo delle Pipeline 1.0 e 2.0.

I comandi ``graph`` e ``spice`` condividono uno stesso workspace persistente:
il secondo usa esclusivamente i Graph JSON appena prodotti dal primo.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PIPELINE1_SCRIPTS_DIR = PROJECT_ROOT / "scripts" / "pipeline_1.0"
PIPELINE2_LAUNCHER_PATH = PROJECT_ROOT / "scripts" / "pipeline_2.0" / "run_pipeline2.py"
PIPELINE2_JSON_DIR = PROJECT_ROOT / "scripts" / "pipeline_2.0" / "json_to_spice"
WEBCHAT_ENTRY_PATH = PIPELINE2_JSON_DIR / "09_web_chat.py"
WORKSPACES_ROOT = PROJECT_ROOT / "outputs" / "demo_workspaces"
REQUIRED_DETECTOR_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "yolo11"
    / "exp11b1_yolo11_rgb_aug_strong_v3"
    / "weights"
    / "best.pt"
)
REQUIRED_DETECTOR_SHA256 = (
    "325d619c6e9ee4d992e6eb141d21c0641cbf72e1c0a6e03cc9bdd9ec0b22fe6a"
)
EASYOCR_REQUIRED_MODELS_MD5 = {
    "craft_mlt_25k.pth": "2f8227d2def4037cdb3b34389dcf9ec1",
    "english_g2.pth": "5864788e1821be9e454ec108d61b887d",
}
PREFLIGHT_METADATA_PATHS = (
    PROJECT_ROOT / "metadata" / "class_terminals_v1.yaml",
    PROJECT_ROOT / "metadata" / "pipeline2_spice_classes.yaml",
    PROJECT_ROOT / "metadata" / "pipeline2_spice_models.yaml",
)
PREFLIGHT_IMPORTS = (
    "albumentations",
    "cv2",
    "dotenv",
    "easyocr",
    "matplotlib",
    "numpy",
    "openai",
    "pandas",
    "PIL",
    "pytesseract",
    "skimage",
    "torch",
    "torchvision",
    "ultralytics",
    "yaml",
)
NGSPICE_CANDIDATES = ("ngspice_con", "ngspice_con.exe", "ngspice", "ngspice.exe")
SUPPORTED_IMAGE_EXTENSIONS = {".bmp", ".jpeg", ".jpg", ".png", ".tif", ".tiff", ".webp"}
SAFE_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")
WINDOWS_ABSOLUTE_PATH_PATTERN = re.compile(r"^(?:[A-Za-z]:[\\/]|\\\\)")
MANIFEST_SCHEMA_VERSION = 2
LEGACY_PROJECT_PATH_ANCHORS = (
    "data",
    "experiment_ai",
    "metadata",
    "notes",
    "outputs",
    "scripts",
    "tests",
)
MANIFEST_PATH_KEYS = {
    "base_output_dir",
    "diagnostic_context",
    "graph_json",
    "input_dir",
    "log",
    "output_dir",
    "report_html",
    "source_image",
    "sources",
    "values_dir",
    "values_yaml",
    "viewer_layout",
    "viewer_model",
    "viewer_svg",
    "workspace_image",
}

PIPELINE1_STEPS = (
    ("01_detect_components", "01_detect_components.py"),
    ("02_assign_instances", "02_assign_instances.py"),
    ("03_estimate_terminals", "03_estimate_terminals.py"),
    ("04_extract_wires", "04_extract_wires.py"),
    ("05_build_terminal_graph", "05_build_terminal_graph.py"),
    ("06_graph_report", "06_render_graph_report.py"),
)

PIPELINE2_REQUIRED_ARTIFACTS = (
    "01_graph.json",
    "02_normalized_circuit.json",
    "03_node_map.json",
    "04_values_bound.json",
    "06_component_rules.json",
    "07_netlist.cir",
    "07_external_models.lib",
    "07_spice_emit_report.json",
    "08_spice_run.json",
    "08_ngspice_stdout.txt",
    "08_ngspice_stderr.txt",
)
PIPELINE2_BASE_ARTIFACT_PATTERN = re.compile(r"^0[1-8]_.*")


class PipelineStepError(RuntimeError):
    """Rappresenta il fallimento controllato di uno step figlio."""

    def __init__(self, step_name: str, return_code: int) -> None:
        super().__init__(f"Lo step {step_name} e' terminato con codice {return_code}.")
        self.step_name = step_name
        self.return_code = return_code


def current_timestamp() -> str:
    """Restituisce un timestamp locale leggibile e privo di microsecondi."""
    return datetime.now().astimezone().isoformat(timespec="seconds")


def require_safe_name(label: str, value: str) -> str:
    """Valida un identificativo usato per costruire directory del workspace."""
    clean_value = str(value).strip()
    if not clean_value or not SAFE_NAME_PATTERN.fullmatch(clean_value):
        raise ValueError(
            f"{label} non valido: {value!r}. Usa soltanto lettere, numeri, punto, trattino e underscore."
        )
    if clean_value in {".", ".."}:
        raise ValueError(f"{label} non valido: {value!r}.")
    return clean_value


def load_pipeline2_module() -> Any:
    """Carica pigramente l'entry point tecnico della Pipeline 2.0."""
    spec = importlib.util.spec_from_file_location(
        "pipeline2_unified_runtime",
        PIPELINE2_LAUNCHER_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare la Pipeline 2.0: {PIPELINE2_LAUNCHER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_webchat_module() -> Any:
    """Carica la webchat preservando i suoi moduli interni riusabili."""
    module_dir = str(PIPELINE2_JSON_DIR)
    if module_dir not in sys.path:
        sys.path.insert(0, module_dir)
    spec = importlib.util.spec_from_file_location(
        "pipeline2_unified_webchat",
        WEBCHAT_ENTRY_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare la webchat: {WEBCHAT_ENTRY_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def resolve_project_path(raw_path: str | Path) -> Path:
    """Risolve un path assoluto oppure relativo alla root del progetto."""
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


def _canonical_legacy_relative_path(relative_path: Path) -> Path:
    """Converte i pochi alias storici noti nel layout canonico corrente."""
    normalized = relative_path.as_posix()
    legacy_demo = "data/batchDemo"
    if normalized == legacy_demo or normalized.startswith(legacy_demo + "/"):
        suffix = normalized[len(legacy_demo) :].lstrip("/")
        target = Path("data") / "batchPipeline2.0" / "batchDemo"
        return target / suffix if suffix else target
    return Path(normalized)


def _legacy_project_relative_path(raw_path: str | Path) -> Path | None:
    """Recupera la parte interna al progetto da un vecchio path assoluto."""
    normalized = str(raw_path).replace("\\", "/")
    parts = [part for part in normalized.split("/") if part]
    lowered = [part.lower() for part in parts]
    for anchor in LEGACY_PROJECT_PATH_ANCHORS:
        try:
            index = lowered.index(anchor.lower())
        except ValueError:
            continue
        return _canonical_legacy_relative_path(Path(*parts[index:]))
    return None


def resolve_manifest_path(raw_path: str | Path) -> Path:
    """Risolve sia i path portabili sia quelli assoluti dei manifest storici."""
    raw_value = str(raw_path)
    path = Path(raw_value).expanduser()
    windows_absolute = bool(WINDOWS_ABSOLUTE_PATH_PATTERN.match(raw_value))
    if not path.is_absolute() and not windows_absolute:
        relative = _canonical_legacy_relative_path(path)
        return (PROJECT_ROOT / relative).resolve()

    # Su Linux/macOS pathlib non riconosce un vecchio path assoluto Windows.
    # In quel caso recuperiamo comunque la porzione interna alla repository.
    if windows_absolute and not path.is_absolute():
        legacy_relative = _legacy_project_relative_path(raw_value)
        if legacy_relative is not None:
            return (PROJECT_ROOT / legacy_relative).resolve()
        return path

    resolved = path.resolve()
    try:
        current_relative = resolved.relative_to(PROJECT_ROOT.resolve())
    except ValueError:
        current_relative = None
    if current_relative is not None:
        canonical_relative = _canonical_legacy_relative_path(current_relative)
        return (PROJECT_ROOT / canonical_relative).resolve()
    if resolved.exists():
        return resolved

    legacy_relative = _legacy_project_relative_path(raw_path)
    if legacy_relative is not None:
        return (PROJECT_ROOT / legacy_relative).resolve()
    return resolved


def portable_manifest_path(raw_path: str | Path) -> str:
    """Serializza come path repo-relative tutto cio' che vive nel progetto."""
    resolved = resolve_manifest_path(raw_path)
    try:
        return resolved.relative_to(PROJECT_ROOT.resolve()).as_posix()
    except ValueError:
        return str(resolved)


def make_manifest_paths_portable(value: Any, key: str | None = None) -> Any:
    """Normalizza ricorsivamente soltanto i campi che rappresentano path."""
    if isinstance(value, dict):
        for child_key, child_value in list(value.items()):
            if child_key == "artifacts" and isinstance(child_value, dict):
                value[child_key] = {
                    name: portable_manifest_path(path_value)
                    if isinstance(path_value, (str, Path))
                    else path_value
                    for name, path_value in child_value.items()
                }
            else:
                value[child_key] = make_manifest_paths_portable(
                    child_value,
                    child_key,
                )
        return value
    if key in MANIFEST_PATH_KEYS and isinstance(value, (str, Path)):
        return portable_manifest_path(value)
    if isinstance(value, list):
        return [make_manifest_paths_portable(item) for item in value]
    return value


def workspace_dir(workspace_id: str) -> Path:
    """Restituisce la root isolata associata a una singola esecuzione."""
    safe_workspace_id = require_safe_name("workspace", workspace_id)
    return WORKSPACES_ROOT / safe_workspace_id


def path_is_within(path: Path, parent: Path) -> bool:
    """Verifica che un path risolto appartenga alla directory attesa."""
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def discover_images(input_dir: Path) -> dict[str, Path]:
    """Indicizza le immagini supportate, bloccando identificativi duplicati."""
    if not input_dir.is_dir():
        raise FileNotFoundError(f"Cartella immagini non trovata: {input_dir}")

    images: dict[str, Path] = {}
    for path in sorted(input_dir.iterdir(), key=lambda item: item.name.lower()):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
            continue
        circuit_id = require_safe_name("circuito", path.stem)
        if circuit_id in images:
            raise ValueError(
                f"Due immagini condividono l'identificativo {circuit_id!r}: "
                f"{images[circuit_id].name} e {path.name}."
            )
        images[circuit_id] = path.resolve()

    if not images:
        raise FileNotFoundError(f"Nessuna immagine supportata trovata in: {input_dir}")
    return images


def select_images(
    available_images: dict[str, Path],
    circuit_id: str | None,
    select_all: bool,
) -> dict[str, Path]:
    """Seleziona un solo circuito oppure l'intero batch indicizzato."""
    if select_all:
        return dict(available_images)

    selected_id = require_safe_name("circuito", circuit_id or "")
    selected_path = available_images.get(selected_id)
    if selected_path is None:
        available = ", ".join(sorted(available_images))
        raise FileNotFoundError(
            f"Circuito {selected_id!r} non trovato. Circuiti disponibili: {available}"
        )
    return {selected_id: selected_path}


def sha256_file(path: Path) -> str:
    """Calcola l'hash SHA-256 di un file senza caricarlo interamente in memoria."""
    digest = hashlib.sha256()
    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def md5_file(path: Path) -> str:
    """Calcola l'MD5 richiesto dai metadati ufficiali dei modelli EasyOCR."""
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolve_executable(
    requested: str | None,
    candidates: tuple[str, ...],
) -> str | None:
    """Risolve un eseguibile passato come path oppure disponibile nel PATH."""
    if requested:
        explicit = Path(requested).expanduser()
        if explicit.is_file():
            return str(explicit.resolve())
        return shutil.which(requested)
    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def _run_preflight_process(
    command: list[str],
    *,
    timeout: int = 120,
    environment: dict[str, str] | None = None,
) -> tuple[bool, str]:
    """Esegue un controllo esterno senza ereditare output interattivo."""
    try:
        completed = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
            env=environment,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return False, str(error)

    combined = "\n".join(
        part.strip() for part in (completed.stdout, completed.stderr) if part.strip()
    )
    lines = [line.strip() for line in combined.splitlines() if line.strip()]
    informative_lines = [line for line in lines if line.strip("*=-_ ")]
    detail = (
        informative_lines[0]
        if informative_lines
        else (lines[-1] if lines else f"exit {completed.returncode}")
    )
    return completed.returncode == 0, detail


def _local_openai_key_is_configured() -> bool:
    """Controlla la presenza della chiave senza leggerla ad alta voce o stamparla."""
    if os.environ.get("OPENAI_API_KEY", "").strip():
        return True
    for env_path in (PROJECT_ROOT / ".env", PROJECT_ROOT / "scripts" / "GPT" / ".env"):
        if not env_path.is_file():
            continue
        for raw_line in env_path.read_text(
            encoding="utf-8",
            errors="replace",
        ).splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, value = line.split("=", 1)
            if name.strip() == "OPENAI_API_KEY" and value.strip().strip("\"'"):
                return True
    return False


def _configured_easyocr_model_directory() -> Path:
    """Usa lo stesso override e lo stesso YAML letti dalla Pipeline 1.0."""
    environment_value = os.environ.get("EASYOCR_MODEL_DIR", "").strip()
    if environment_value:
        return resolve_project_path(environment_value)

    yaml_module = importlib.import_module("yaml")
    metadata = yaml_module.safe_load(
        PREFLIGHT_METADATA_PATHS[0].read_text(encoding="utf-8-sig")
    )
    integrated_circuit = next(
        (
            entry
            for entry in metadata.values()
            if isinstance(entry, dict) and entry.get("name") == "Integrated_Circuit"
        ),
        None,
    )
    if integrated_circuit is None:
        raise ValueError("Configurazione Integrated_Circuit assente dai metadati.")
    easyocr_config = (
        ((integrated_circuit.get("ocr") or {}).get("ic_marking") or {}).get(
            "easyocr_fallback"
        )
        or {}
    )
    configured = str(easyocr_config.get("model_storage_directory") or ".tmp/easyocr")
    return resolve_project_path(configured)


def _easyocr_cache_status() -> tuple[bool, str]:
    """Controlla presenza e checksum dei due modelli usati con lingua inglese."""
    model_directory = _configured_easyocr_model_directory()
    missing: list[str] = []
    invalid: list[str] = []
    for filename, expected_md5 in EASYOCR_REQUIRED_MODELS_MD5.items():
        model_path = model_directory / filename
        if not model_path.is_file():
            missing.append(filename)
        elif md5_file(model_path) != expected_md5:
            invalid.append(filename)

    portable_directory = portable_manifest_path(model_directory)
    if missing or invalid:
        parts = []
        if missing:
            parts.append("mancanti: " + ", ".join(missing))
        if invalid:
            parts.append("checksum non valido: " + ", ".join(invalid))
        return False, f"{portable_directory}; " + "; ".join(parts)
    return True, f"2 modelli validi in {portable_directory}"


def preflight_command(args: argparse.Namespace) -> int:
    """Verifica in sola lettura tutto cio' che serve al flusso completo."""
    failures: list[str] = []
    warnings: list[str] = []

    def report(
        label: str,
        ok: bool,
        detail: str,
        *,
        required: bool = True,
    ) -> None:
        if ok:
            marker = "OK"
        elif required:
            marker = "ERRORE"
            failures.append(label)
        else:
            marker = "AVVISO"
            warnings.append(label)
        print(f"[{marker}] {label}: {detail}")

    python_ok = sys.version_info[:2] == (3, 12)
    report(
        "Python",
        python_ok,
        f"{sys.version.split()[0]} ({sys.executable})",
    )

    required_scripts = [
        *(PIPELINE1_SCRIPTS_DIR / script_name for _, script_name in PIPELINE1_STEPS),
        PIPELINE2_LAUNCHER_PATH,
        WEBCHAT_ENTRY_PATH,
    ]
    missing_scripts = [
        path.relative_to(PROJECT_ROOT).as_posix()
        for path in required_scripts
        if not path.is_file()
    ]
    report(
        "Script pipeline",
        not missing_scripts,
        "tutti presenti" if not missing_scripts else ", ".join(missing_scripts),
    )

    if not REQUIRED_DETECTOR_PATH.is_file():
        report(
            "Checkpoint YOLO",
            False,
            f"file assente: {REQUIRED_DETECTOR_PATH.relative_to(PROJECT_ROOT)}",
        )
    else:
        with REQUIRED_DETECTOR_PATH.open("rb") as model_handle:
            model_header = model_handle.read(160)
        if model_header.startswith(b"version https://git-lfs.github.com/spec"):
            report(
                "Checkpoint YOLO",
                False,
                "e' ancora un puntatore Git LFS; eseguire git lfs pull",
            )
        else:
            detector_sha256 = sha256_file(REQUIRED_DETECTOR_PATH)
            report(
                "Checkpoint YOLO",
                detector_sha256 == REQUIRED_DETECTOR_SHA256,
                (
                    f"{REQUIRED_DETECTOR_PATH.stat().st_size} byte, "
                    f"sha256={detector_sha256}"
                ),
            )

    missing_metadata = [
        path.relative_to(PROJECT_ROOT).as_posix()
        for path in PREFLIGHT_METADATA_PATHS
        if not path.is_file()
    ]
    report(
        "Metadati",
        not missing_metadata,
        "tutti presenti" if not missing_metadata else ", ".join(missing_metadata),
    )

    import_environment = os.environ.copy()
    import_environment.setdefault("NO_ALBUMENTATIONS_UPDATE", "1")
    import_statement = "; ".join(f"import {module}" for module in PREFLIGHT_IMPORTS)
    imports_ok, imports_detail = _run_preflight_process(
        [sys.executable, "-B", "-c", import_statement],
        environment=import_environment,
    )
    report(
        "Import Python",
        imports_ok,
        "moduli caricati correttamente" if imports_ok else imports_detail,
    )

    opencv_check = """
import cv2
from importlib.metadata import version

opencv_python = version("opencv-python")
opencv_headless = version("opencv-python-headless")
active = cv2.__version__
active_expected = ".".join(opencv_python.split(".")[:3])
print(
    f"opencv-python={opencv_python}, "
    f"opencv-python-headless={opencv_headless}, cv2={active}"
)
raise SystemExit(
    0 if opencv_python == opencv_headless and active == active_expected else 1
)
"""
    opencv_ok, opencv_detail = _run_preflight_process(
        [sys.executable, "-B", "-c", opencv_check],
        environment=import_environment,
    )
    report("Build OpenCV", opencv_ok, opencv_detail)

    pip_ok, pip_detail = _run_preflight_process(
        [sys.executable, "-B", "-m", "pip", "check"]
    )
    report("Coerenza pacchetti", pip_ok, pip_detail)

    if not missing_metadata:
        try:
            yaml_module = importlib.import_module("yaml")
            for metadata_path in PREFLIGHT_METADATA_PATHS:
                metadata = yaml_module.safe_load(
                    metadata_path.read_text(encoding="utf-8-sig")
                )
                if not isinstance(metadata, dict) or not metadata:
                    raise ValueError(f"YAML vuoto o non valido: {metadata_path.name}")

            pipeline2_module = load_pipeline2_module()
            models_path = PREFLIGHT_METADATA_PATHS[2]
            models = pipeline2_module.values.load_simple_yaml(models_path)
            resolved_models = pipeline2_module.spice_emit.resolve_model_entries(
                spice_models=models,
                spice_models_source=models_path,
            )
            report(
                "Modelli SPICE",
                bool(resolved_models),
                f"{len(resolved_models)} modelli validati, inclusi file e hash esterni",
            )
        except Exception as error:  # noqa: BLE001 - il preflight deve elencare ogni problema.
            report("Metadati e modelli SPICE", False, str(error))

    input_dir = resolve_project_path(args.input_dir)
    try:
        images = discover_images(input_dir)
        values_dir = input_dir / "values"
        missing_values = [
            f"{circuit_id}_values.yaml"
            for circuit_id in images
            if not (values_dir / f"{circuit_id}_values.yaml").is_file()
        ]
        report(
            "Batch immagini",
            True,
            f"{len(images)} immagini in {portable_manifest_path(input_dir)}",
        )
        report(
            "YAML valori",
            not missing_values,
            "uno per ogni immagine" if not missing_values else ", ".join(missing_values),
        )
    except (FileNotFoundError, ValueError) as error:
        report("Batch immagini", False, str(error))

    git_path = shutil.which("git")
    if git_path is None:
        report("Git LFS", False, "git non trovato nel PATH")
    else:
        lfs_version_ok, lfs_version_detail = _run_preflight_process(
            [git_path, "lfs", "version"]
        )
        if not lfs_version_ok:
            report("Git LFS", False, lfs_version_detail)
        else:
            lfs_ok, lfs_detail = _run_preflight_process(
                [git_path, "lfs", "fsck"],
                timeout=180,
            )
            report("Git LFS", lfs_ok, lfs_detail)

    ngspice_path = _resolve_executable(args.ngspice_executable, NGSPICE_CANDIDATES)
    if ngspice_path is None:
        report("ngspice", False, "eseguibile non trovato")
    else:
        ngspice_ok, ngspice_detail = _run_preflight_process([ngspice_path, "-v"])
        report("ngspice", ngspice_ok, ngspice_detail)

    tesseract_requested = args.tesseract_executable or os.environ.get("TESSERACT_CMD")
    tesseract_path = _resolve_executable(tesseract_requested, ("tesseract", "tesseract.exe"))
    if tesseract_path is None:
        report("Tesseract OCR", False, "eseguibile non trovato")
    else:
        tesseract_ok, tesseract_detail = _run_preflight_process(
            [tesseract_path, "--list-langs"]
        )
        if tesseract_ok:
            try:
                language_result = subprocess.run(
                    [tesseract_path, "--list-langs"],
                    cwd=PROJECT_ROOT,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=30,
                    check=False,
                )
            except (OSError, subprocess.TimeoutExpired) as error:
                report("Tesseract OCR", False, str(error))
                language_result = None
            if language_result is None:
                languages: set[str] = set()
            else:
                languages = {
                    line.strip()
                    for line in language_result.stdout.splitlines()
                    if line.strip() and not line.lower().startswith("list of available")
                }
            if language_result is not None:
                report(
                    "Tesseract OCR",
                    "eng" in languages,
                    f"{tesseract_path}; lingue: {', '.join(sorted(languages)) or 'nessuna'}",
                )
        else:
            report("Tesseract OCR", False, tesseract_detail)

    openai_configured = _local_openai_key_is_configured()
    report(
        "OpenAI API key",
        openai_configured,
        "configurata" if openai_configured else "non configurata (serve solo alle funzioni AGENT)",
        required=bool(args.require_openai),
    )

    try:
        easyocr_ok, easyocr_detail = _easyocr_cache_status()
    except Exception as error:  # noqa: BLE001 - il preflight deve restare diagnostico.
        easyocr_ok, easyocr_detail = False, str(error)
    report(
        "Cache EasyOCR",
        easyocr_ok,
        easyocr_detail
        if easyocr_ok
        else f"{easyocr_detail}; download automatico al primo utilizzo",
        required=False,
    )

    print()
    if failures:
        print(f"Preflight NON superato: {len(failures)} controllo/i obbligatorio/i falliti.")
        return 1
    print(
        "Preflight superato"
        + (f" con {len(warnings)} avviso/i." if warnings else ".")
    )
    return 0


def read_manifest(path: Path, workspace_id: str) -> dict[str, Any]:
    """Legge il manifest esistente oppure crea la struttura minima iniziale."""
    if path.exists():
        # Alcuni manifest storici sono stati salvati con BOM UTF-8 da editor
        # Windows. utf-8-sig gestisce sia quei file sia i normali UTF-8.
        with path.open("r", encoding="utf-8-sig") as file_handle:
            data = json.load(file_handle)
        if not isinstance(data, dict):
            raise ValueError(f"Manifest non valido: {path}")
        make_manifest_paths_portable(data)
        data["schema_version"] = MANIFEST_SCHEMA_VERSION
        return data

    timestamp = current_timestamp()
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "created_at": timestamp,
        "updated_at": timestamp,
        "circuits": {},
    }


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    """Aggiorna il manifest con una sostituzione atomica del file precedente."""
    path.parent.mkdir(parents=True, exist_ok=True)
    make_manifest_paths_portable(manifest)
    manifest["schema_version"] = MANIFEST_SCHEMA_VERSION
    manifest["updated_at"] = current_timestamp()
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    temporary_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(path)


def record_batch_input(
    manifest: dict[str, Any],
    source_input_dir: Path,
    force: bool,
) -> None:
    """Registra la cartella batch da riutilizzare nei comandi successivi."""
    resolved_input_dir = source_input_dir.resolve()
    previous_value = manifest.get("input_dir")
    if previous_value:
        previous_dir = resolve_manifest_path(str(previous_value))
        if previous_dir != resolved_input_dir and not force:
            raise ValueError(
                "Il workspace appartiene gia' a un'altra cartella batch: "
                f"{previous_dir}. Usa --force soltanto per sostituirla."
            )
    manifest["input_dir"] = portable_manifest_path(resolved_input_dir)
    manifest["values_dir"] = portable_manifest_path(resolved_input_dir / "values")


def snapshot_images(
    selected_images: dict[str, Path],
    destination_dir: Path,
    manifest: dict[str, Any],
    force: bool,
) -> dict[str, Path]:
    """Copia nel workspace le immagini scelte e ne registra origine e hash."""
    destination_dir.mkdir(parents=True, exist_ok=True)
    manifest_circuits = manifest.setdefault("circuits", {})
    snapshots: dict[str, Path] = {}

    for circuit_id, source_path in selected_images.items():
        source_hash = sha256_file(source_path)
        destination_path = destination_dir / source_path.name

        if destination_path.exists():
            destination_hash = sha256_file(destination_path)
            if destination_hash != source_hash and not force:
                raise ValueError(
                    f"L'immagine {circuit_id} nel workspace e' diversa dalla sorgente. "
                    "Usa --force per sostituirla oppure scegli un nuovo workspace."
                )
        if force or not destination_path.exists():
            shutil.copy2(source_path, destination_path)

        circuit_manifest = manifest_circuits.setdefault(circuit_id, {})
        circuit_manifest.update(
            {
                "source_image": str(source_path),
                "workspace_image": str(destination_path),
                "image_sha256": source_hash,
            }
        )
        circuit_manifest.setdefault("pipeline1", {"status": "pending"})
        snapshots[circuit_id] = destination_path

    return snapshots


def completed_graph_path(pipeline1_dir: Path, circuit_id: str) -> Path:
    """Calcola il Graph JSON finale atteso per un circuito."""
    return pipeline1_dir / "06_graph_report" / circuit_id / f"{circuit_id}.json"


def circuits_requiring_execution(
    selected_ids: list[str],
    pipeline1_dir: Path,
    manifest: dict[str, Any],
    force: bool,
) -> tuple[list[str], list[str]]:
    """Separa i circuiti da elaborare da quelli gia' completati."""
    pending: list[str] = []
    skipped: list[str] = []
    manifest_circuits = manifest.get("circuits") or {}

    for circuit_id in selected_ids:
        pipeline1_state = (manifest_circuits.get(circuit_id) or {}).get("pipeline1") or {}
        graph_path = completed_graph_path(pipeline1_dir, circuit_id)
        if not force and pipeline1_state.get("status") == "completed" and graph_path.is_file():
            skipped.append(circuit_id)
        else:
            pending.append(circuit_id)
    return pending, skipped


def update_pipeline1_state(
    manifest: dict[str, Any],
    circuit_ids: list[str],
    **state: Any,
) -> None:
    """Applica lo stesso avanzamento Pipeline 1.0 ai circuiti selezionati."""
    manifest_circuits = manifest.setdefault("circuits", {})
    for circuit_id in circuit_ids:
        circuit_manifest = manifest_circuits.setdefault(circuit_id, {})
        pipeline1_state = circuit_manifest.setdefault("pipeline1", {})
        pipeline1_state.update(state)


def child_environment(
    pipeline1_dir: Path,
    input_images_dir: Path,
    circuit_ids: list[str],
) -> dict[str, str]:
    """Costruisce l'ambiente isolato passato agli script Pipeline 1.0."""
    environment = os.environ.copy()
    dataset_relative = pipeline1_dir.relative_to(PROJECT_ROOT / "outputs")
    environment.update(
        {
            "PIPELINE_DATASET": str(dataset_relative),
            "PIPELINE_INPUT_DIR": str(input_images_dir),
            "PIPELINE_IMAGE_IDS": ",".join(circuit_ids),
            "PYTHONUTF8": "1",
            "PYTHONIOENCODING": "utf-8",
        }
    )
    return environment


def run_child_step(
    step_name: str,
    script_name: str,
    environment: dict[str, str],
    circuit_ids: list[str],
    log_handle: Any,
) -> None:
    """Esegue uno step, mostrando e salvando lo stesso output testuale."""
    command = [sys.executable, "-B", str(PIPELINE1_SCRIPTS_DIR / script_name)]
    if step_name == "06_graph_report":
        command.extend(["--image-ids", *circuit_ids])

    command_line = subprocess.list2cmdline(command)
    heading = f"\n=== {step_name} ===\n{command_line}\n"
    print(heading, end="")
    log_handle.write(heading)
    log_handle.flush()

    process = subprocess.Popen(
        command,
        cwd=PROJECT_ROOT,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert process.stdout is not None
    try:
        for line in process.stdout:
            print(line, end="")
            log_handle.write(line)
    except KeyboardInterrupt:
        process.terminate()
        process.wait()
        raise

    return_code = process.wait()
    log_handle.flush()
    if return_code != 0:
        raise PipelineStepError(step_name, return_code)


def graph_command(args: argparse.Namespace) -> int:
    """Esegue gli step 01-06 della Pipeline 1.0 nel workspace richiesto."""
    workspace_id = require_safe_name("workspace", args.workspace)
    source_input_dir = resolve_project_path(args.input_dir)
    available_images = discover_images(source_input_dir)
    selected_images = select_images(available_images, args.circuit, args.all)
    selected_ids = sorted(selected_images)
    target_workspace_dir = workspace_dir(workspace_id)
    pipeline1_dir = target_workspace_dir / "pipeline1.0"
    input_images_dir = target_workspace_dir / "input" / "images"
    manifest_path = target_workspace_dir / "workspace_manifest.json"

    print(f"Workspace       : {target_workspace_dir}")
    print(f"Input sorgente  : {source_input_dir}")
    print(f"Circuiti        : {', '.join(selected_ids)}")
    print(f"Output Pipeline1: {pipeline1_dir}")

    if args.dry_run:
        print("\nDry-run: nessun file verra' creato e nessuno step verra' eseguito.")
        for step_name, script_name in PIPELINE1_STEPS:
            print(f"  {step_name}: {PIPELINE1_SCRIPTS_DIR / script_name}")
        return 0

    manifest = read_manifest(manifest_path, workspace_id)
    record_batch_input(manifest, source_input_dir, args.force)
    snapshot_images(selected_images, input_images_dir, manifest, args.force)
    pending_ids, skipped_ids = circuits_requiring_execution(
        selected_ids,
        pipeline1_dir,
        manifest,
        args.force,
    )
    write_manifest(manifest_path, manifest)

    if skipped_ids:
        print(f"Gia' completati  : {', '.join(skipped_ids)}")
    if not pending_ids:
        print("\nPipeline 1.0 gia' completa. Usa --force soltanto se vuoi rigenerarla.")
        return 0

    environment = child_environment(pipeline1_dir, input_images_dir, pending_ids)
    logs_dir = target_workspace_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = logs_dir / f"graph_{log_timestamp}.log"

    update_pipeline1_state(
        manifest,
        pending_ids,
        status="running",
        started_at=current_timestamp(),
        current_step=None,
        error=None,
    )
    write_manifest(manifest_path, manifest)

    try:
        with log_path.open("w", encoding="utf-8") as log_handle:
            for step_name, script_name in PIPELINE1_STEPS:
                update_pipeline1_state(
                    manifest,
                    pending_ids,
                    status="running",
                    current_step=step_name,
                )
                write_manifest(manifest_path, manifest)
                run_child_step(
                    step_name,
                    script_name,
                    environment,
                    pending_ids,
                    log_handle,
                )
    except PipelineStepError as error:
        update_pipeline1_state(
            manifest,
            pending_ids,
            status="failed",
            current_step=error.step_name,
            return_code=error.return_code,
            error=str(error),
        )
        write_manifest(manifest_path, manifest)
        print(f"\nErrore: {error}", file=sys.stderr)
        print(f"Log: {log_path}", file=sys.stderr)
        return error.return_code or 1
    except KeyboardInterrupt:
        update_pipeline1_state(
            manifest,
            pending_ids,
            status="interrupted",
            error="Esecuzione interrotta dall'utente.",
        )
        write_manifest(manifest_path, manifest)
        print(f"\nEsecuzione interrotta. Log: {log_path}", file=sys.stderr)
        return 130

    for circuit_id in pending_ids:
        graph_path = completed_graph_path(pipeline1_dir, circuit_id)
        report_path = pipeline1_dir / "06_graph_report" / circuit_id / "graph.html"
        if not graph_path.is_file():
            update_pipeline1_state(
                manifest,
                [circuit_id],
                status="failed",
                current_step="06_graph_report",
                error=f"Graph JSON finale non trovato: {graph_path}",
            )
            write_manifest(manifest_path, manifest)
            print(f"Errore: Graph JSON finale non trovato: {graph_path}", file=sys.stderr)
            return 1

        update_pipeline1_state(
            manifest,
            [circuit_id],
            status="completed",
            current_step=None,
            completed_at=current_timestamp(),
            return_code=0,
            graph_json=str(graph_path),
            graph_sha256=sha256_file(graph_path),
            report_html=str(report_path) if report_path.is_file() else None,
            log=str(log_path),
            error=None,
        )

    write_manifest(manifest_path, manifest)
    index_path = pipeline1_dir / "06_graph_report" / "index.html"
    print("\nPipeline 1.0 completata.")
    for circuit_id in pending_ids:
        print(f"  {circuit_id}: {completed_graph_path(pipeline1_dir, circuit_id)}")
    print(f"Report batch: {index_path}")
    print(f"Manifest    : {manifest_path}")
    print(f"Log         : {log_path}")
    return 0


def resolve_manifest_input_dir(manifest: dict[str, Any]) -> Path:
    """Recupera la cartella batch registrata, anche per manifest meno recenti."""
    configured = manifest.get("input_dir")
    if configured:
        input_dir = resolve_manifest_path(str(configured))
        if input_dir.is_dir():
            return input_dir
        raise FileNotFoundError(f"Cartella batch registrata non trovata: {input_dir}")

    source_parents = {
        resolve_manifest_path(str(circuit.get("source_image"))).parent
        for circuit in (manifest.get("circuits") or {}).values()
        if isinstance(circuit, dict) and circuit.get("source_image")
    }
    if len(source_parents) == 1:
        input_dir = source_parents.pop()
        if input_dir.is_dir():
            return input_dir
    raise ValueError(
        "Il manifest non identifica una sola cartella batch. "
        "Riesegui il comando graph sul workspace."
    )


def select_workspace_circuits(
    manifest: dict[str, Any],
    circuit_id: str | None,
    select_all: bool,
) -> list[str]:
    """Seleziona uno o tutti i circuiti registrati nel workspace."""
    available = sorted(str(item) for item in (manifest.get("circuits") or {}))
    if not available:
        raise ValueError("Il workspace non contiene circuiti registrati.")
    if select_all:
        return available

    selected_id = require_safe_name("circuito", circuit_id or "")
    if selected_id not in available:
        raise FileNotFoundError(
            f"Circuito {selected_id!r} non trovato nel workspace. "
            f"Circuiti disponibili: {', '.join(available)}"
        )
    return [selected_id]


def read_json_object(path: Path) -> dict[str, Any]:
    """Legge un oggetto JSON usato per verificare uno stato persistente."""
    if not path.is_file():
        raise FileNotFoundError(f"JSON non trovato: {path}")
    # Accetta anche artefatti JSON storici con BOM UTF-8.
    with path.open("r", encoding="utf-8-sig") as file_handle:
        data = json.load(file_handle)
    if not isinstance(data, dict):
        raise ValueError(f"Il JSON deve contenere un oggetto: {path}")
    return data


def build_spice_plans(
    workspace_path: Path,
    manifest: dict[str, Any],
    circuit_ids: list[str],
    pipeline2_module: Any,
) -> list[dict[str, Any]]:
    """Valida Graph e YAML e costruisce un piano SPICE senza scrivere file."""
    input_dir = resolve_manifest_input_dir(manifest)
    configured_values_dir = manifest.get("values_dir")
    values_dir = (
        resolve_manifest_path(str(configured_values_dir))
        if configured_values_dir
        else input_dir / "values"
    )
    if not values_dir.is_dir():
        raise FileNotFoundError(
            f"Cartella dei valori manuali non trovata: {values_dir}. "
            "Crea values/<circuit_id>_values.yaml dentro il batch."
        )

    pipeline1_dir = workspace_path / "pipeline1.0"
    pipeline2_dir = workspace_path / "pipeline2.0"
    manifest_circuits = manifest.get("circuits") or {}
    spice_models_path = PROJECT_ROOT / "metadata" / "pipeline2_spice_models.yaml"
    spice_models = pipeline2_module.values.load_simple_yaml(spice_models_path)
    spice_models_sha256 = pipeline2_module.spice_emit.build_model_registry_fingerprint(
        spice_models,
        spice_models_path,
    )
    plans: list[dict[str, Any]] = []

    for circuit_id in circuit_ids:
        circuit_manifest = manifest_circuits.get(circuit_id) or {}
        pipeline1_state = circuit_manifest.get("pipeline1") or {}
        if pipeline1_state.get("status") != "completed":
            raise ValueError(
                f"Pipeline 1.0 non completata per {circuit_id}: "
                f"stato={pipeline1_state.get('status', 'missing')}."
            )

        graph_path = completed_graph_path(pipeline1_dir, circuit_id).resolve()
        if not path_is_within(graph_path, pipeline1_dir) or not graph_path.is_file():
            raise FileNotFoundError(f"Graph JSON del workspace non trovato: {graph_path}")

        values_path = (values_dir / f"{circuit_id}_values.yaml").resolve()
        if not path_is_within(values_path, values_dir) or not values_path.is_file():
            raise FileNotFoundError(f"YAML dei valori non trovato: {values_path}")
        values_data = pipeline2_module.values.load_simple_yaml(values_path)
        declared_circuit_id = str(values_data.get("circuit_id") or "").strip()
        if declared_circuit_id != circuit_id:
            raise ValueError(
                f"Lo YAML {values_path.name} dichiara circuit_id={declared_circuit_id!r}; "
                f"atteso {circuit_id!r}."
            )

        plans.append(
            {
                "circuit_id": circuit_id,
                "graph_path": graph_path,
                "graph_sha256": sha256_file(graph_path),
                "values_path": values_path,
                "values_sha256": sha256_file(values_path),
                "spice_models_sha256": spice_models_sha256,
                "output_dir": (pipeline2_dir / circuit_id).resolve(),
            }
        )
    return plans


def pipeline2_state_is_current(
    state: dict[str, Any],
    plan: dict[str, Any],
) -> bool:
    """Verifica che una run completata appartenga ancora agli stessi input."""
    if state.get("status") != "completed":
        return False
    if state.get("graph_sha256") != plan["graph_sha256"]:
        return False
    if state.get("values_sha256") != plan["values_sha256"]:
        return False
    if (
        plan.get("spice_models_sha256") is not None
        and state.get("spice_models_sha256") != plan["spice_models_sha256"]
    ):
        return False

    output_dir = Path(plan["output_dir"])
    if not all((output_dir / filename).is_file() for filename in PIPELINE2_REQUIRED_ARTIFACTS):
        return False
    try:
        run_report = read_json_object(output_dir / "08_spice_run.json")
    except (FileNotFoundError, ValueError, json.JSONDecodeError):
        return False
    return run_report.get("status") == "success" and run_report.get("exit_code") == 0


def update_pipeline2_state(
    manifest: dict[str, Any],
    circuit_id: str,
    **state: Any,
) -> None:
    """Aggiorna lo stato tecnico 01-08 di un solo circuito."""
    circuit_manifest = manifest.setdefault("circuits", {}).setdefault(circuit_id, {})
    pipeline2_state = circuit_manifest.setdefault("pipeline2", {})
    pipeline2_state.update(state)


def collect_pipeline2_artifacts(output_dir: Path) -> dict[str, str]:
    """Indicizza gli artefatti tecnici realmente presenti dopo ngspice."""
    filenames = [
        *PIPELINE2_REQUIRED_ARTIFACTS,
        "08_tran_raw.csv",
        "08_tran.csv",
        "08_tran_plot.png",
        "08_tran_plot.svg",
    ]
    return {
        filename: str(output_dir / filename)
        for filename in filenames
        if (output_dir / filename).is_file()
    }


def web_source_plan(
    workspace_path: Path,
    manifest: dict[str, Any],
    circuit_id: str,
) -> dict[str, Any]:
    """Valida e raccoglie le sorgenti della sessione web di un circuito."""
    circuit_state = (manifest.get("circuits") or {}).get(circuit_id) or {}
    pipeline2_state = circuit_state.get("pipeline2") or {}
    if pipeline2_state.get("status") != "completed":
        raise ValueError(
            f"Pipeline 2.0 non completata per {circuit_id}: "
            f"stato={pipeline2_state.get('status', 'missing')}."
        )

    pipeline1_root = (workspace_path / "pipeline1.0").resolve()
    pipeline2_root = (workspace_path / "pipeline2.0").resolve()
    base_dir = (pipeline2_root / circuit_id).resolve()
    if base_dir.parent != pipeline2_root or not base_dir.is_dir():
        raise FileNotFoundError(f"Base Pipeline 2.0 non trovata: {base_dir}")
    if not all((base_dir / filename).is_file() for filename in PIPELINE2_REQUIRED_ARTIFACTS):
        raise FileNotFoundError(
            f"La base Pipeline 2.0 di {circuit_id} non contiene tutti gli artefatti richiesti."
        )

    run_report = read_json_object(base_dir / "08_spice_run.json")
    if run_report.get("status") != "success" or run_report.get("exit_code") != 0:
        raise ValueError(
            f"La base ngspice di {circuit_id} non e' valida: "
            f"status={run_report.get('status')}, exit_code={run_report.get('exit_code')}."
        )

    graph_path = completed_graph_path(pipeline1_root, circuit_id).resolve()
    terminal_estimates = (
        pipeline1_root / "03_estimate_terminals" / f"{circuit_id}.json"
    ).resolve()
    terminal_graph = (
        pipeline1_root / "05_build_terminal_graph" / f"{circuit_id}.json"
    ).resolve()
    for label, path in (
        ("Graph JSON", graph_path),
        ("stima terminali Pipeline 1.0", terminal_estimates),
        ("terminal graph Pipeline 1.0", terminal_graph),
    ):
        if not path_is_within(path, pipeline1_root) or not path.is_file():
            raise FileNotFoundError(f"{label} non trovato nella run corrente: {path}")

    workspace_image_value = circuit_state.get("workspace_image")
    if not workspace_image_value:
        raise ValueError(f"Immagine del workspace non registrata per {circuit_id}.")
    workspace_image = resolve_manifest_path(str(workspace_image_value))
    input_images_root = (workspace_path / "input" / "images").resolve()
    if not path_is_within(workspace_image, input_images_root) or not workspace_image.is_file():
        raise FileNotFoundError(
            f"Immagine della run corrente non trovata: {workspace_image}"
        )
    current_image_hash = sha256_file(workspace_image)
    if circuit_state.get("image_sha256") != current_image_hash:
        raise ValueError(
            f"L'immagine di {circuit_id} e' cambiata dopo la Pipeline 1.0. "
            "Riesegui prima il comando graph con --force."
        )

    graph_hash = sha256_file(graph_path)
    if pipeline2_state.get("graph_sha256") != graph_hash:
        raise ValueError(
            f"Il Graph di {circuit_id} e' cambiato dopo la run SPICE. "
            "Riesegui prima il comando spice con --force."
        )
    if sha256_file(base_dir / "01_graph.json") != graph_hash:
        raise ValueError(
            f"La copia 01_graph.json di {circuit_id} non coincide con il Graph della run corrente."
        )

    values_path_value = pipeline2_state.get("values_yaml")
    if not values_path_value:
        raise ValueError(f"YAML dei valori non registrato per {circuit_id}.")
    values_path = resolve_manifest_path(str(values_path_value))
    if not values_path.is_file():
        raise FileNotFoundError(f"YAML dei valori non trovato: {values_path}")
    if pipeline2_state.get("values_sha256") != sha256_file(values_path):
        raise ValueError(
            f"Lo YAML di {circuit_id} e' cambiato dopo la run SPICE. "
            "Riesegui prima il comando spice con --force."
        )

    base_files = {
        path.name: sha256_file(path)
        for path in sorted(base_dir.iterdir(), key=lambda item: item.name)
        if path.is_file() and PIPELINE2_BASE_ARTIFACT_PATTERN.fullmatch(path.name)
    }
    if not base_files:
        raise FileNotFoundError(f"Nessun artefatto 01-08 trovato in: {base_dir}")

    fingerprints = {
        "input_image": current_image_hash,
        "terminal_estimates": sha256_file(terminal_estimates),
        "terminal_graph": sha256_file(terminal_graph),
        "graph": graph_hash,
        "values": sha256_file(values_path),
        "base_files": base_files,
    }
    return {
        "circuit_id": circuit_id,
        "base_dir": base_dir,
        "workspace_image": workspace_image,
        "terminal_estimates": terminal_estimates,
        "terminal_graph": terminal_graph,
        "values_path": values_path,
        "base_files": base_files,
        "fingerprints": fingerprints,
    }


def session_relative_path(session_dir: Path, source_path: Path) -> str:
    """Crea un riferimento relativo e quindi trasportabile dentro il workspace."""
    return os.path.relpath(source_path.resolve(), session_dir.resolve())


def build_run_sources_descriptor(
    session_dir: Path,
    mode: str,
    plan: dict[str, Any],
) -> dict[str, Any]:
    """Costruisce il contratto locale condiviso da viewer, CHAT e AGENT."""
    return {
        "source_format": "pipeline2.0_run_sources",
        "schema_version": 1,
        "circuit_id": plan["circuit_id"],
        "workspace_mode": mode,
        "input_image": session_relative_path(session_dir, plan["workspace_image"]),
        "pipeline1": {
            "terminal_estimates": session_relative_path(
                session_dir,
                plan["terminal_estimates"],
            ),
            "terminal_graph": session_relative_path(
                session_dir,
                plan["terminal_graph"],
            ),
        },
        "pipeline2_base_dir": session_relative_path(session_dir, plan["base_dir"]),
        "fingerprints": plan["fingerprints"],
        "created_or_updated_at": current_timestamp(),
    }


def validate_existing_web_session(
    session_dir: Path,
    expected_descriptor: dict[str, Any],
) -> None:
    """Blocca una sessione incompleta o derivata da una base differente."""
    descriptor_path = session_dir / "pipeline2_sources.json"
    if not descriptor_path.is_file():
        raise ValueError(
            f"La sessione esistente non ha un descrittore verificabile: {session_dir}. "
            "Usa --force per ricrearla."
        )
    descriptor = read_json_object(descriptor_path)
    if descriptor.get("fingerprints") != expected_descriptor.get("fingerprints"):
        raise ValueError(
            f"Le sorgenti della sessione sono cambiate: {session_dir}. "
            "Usa --force per ricreare CHAT e AGENT dalla nuova base."
        )

    for filename, expected_hash in (expected_descriptor.get("fingerprints") or {}).get(
        "base_files", {}
    ).items():
        copied_path = session_dir / filename
        if not copied_path.is_file() or sha256_file(copied_path) != expected_hash:
            raise ValueError(
                f"Artefatto base mancante o modificato nella sessione: {copied_path}. "
                "Usa --force per ricrearla."
            )


def reset_web_session(session_dir: Path, mode_root: Path) -> None:
    """Rimuove soltanto la sessione selezionata quando ``--force`` lo autorizza."""
    if not session_dir.exists():
        return
    if session_dir.parent.resolve() != mode_root.resolve():
        raise ValueError(f"Directory sessione web non sicura: {session_dir}")
    shutil.rmtree(session_dir)


def prepare_web_session(
    session_dir: Path,
    mode: str,
    plan: dict[str, Any],
    webchat_module: Any,
    batch_name: str,
    workspace_id: str,
    force: bool,
) -> dict[str, str]:
    """Crea o riapre una copia web e prepara viewer e contesto diagnostico."""
    mode_root = session_dir.parent
    if force:
        reset_web_session(session_dir, mode_root)

    descriptor = build_run_sources_descriptor(session_dir, mode, plan)
    if session_dir.exists() and any(session_dir.iterdir()):
        validate_existing_web_session(session_dir, descriptor)
    else:
        session_dir.mkdir(parents=True, exist_ok=True)
        for filename in plan["base_files"]:
            shutil.copy2(plan["base_dir"] / filename, session_dir / filename)

    descriptor_path = session_dir / "pipeline2_sources.json"
    descriptor_path.write_text(
        json.dumps(descriptor, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    # Il viewer viene generato nella copia specifica: anche gli scenari futuri
    # troveranno lo stesso descrittore risalendo dalla propria cartella run.
    webchat_module.load_or_build_viewer_model(session_dir)
    webchat_module.load_or_build_viewer_layout(session_dir)
    webchat_module.load_or_build_viewer_svg(session_dir)

    context_path = session_dir / "10_diagnostic_context.json"
    if not context_path.is_file():
        webchat_module.write_chat_context(
            batch=batch_name,
            circuit=plan["circuit_id"],
            output_dir=session_dir,
            user_problem="",
            experiment=workspace_id,
        )

    return {
        "status": "ready",
        "output_dir": str(session_dir),
        "sources": str(descriptor_path),
        "diagnostic_context": str(context_path),
        "viewer_model": str(session_dir / "13_viewer_model.json"),
        "viewer_layout": str(session_dir / "14_viewer_layout.json"),
        "viewer_svg": str(session_dir / "15_viewer.svg"),
    }


def spice_command(args: argparse.Namespace) -> int:
    """Esegue gli step 01-08 sui Graph appena creati nel workspace."""
    workspace_id = require_safe_name("workspace", args.workspace)
    target_workspace_dir = workspace_dir(workspace_id).resolve()
    manifest_path = target_workspace_dir / "workspace_manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(
            f"Workspace non inizializzato: {target_workspace_dir}. "
            "Esegui prima il comando graph."
        )

    manifest = read_manifest(manifest_path, workspace_id)
    selected_ids = select_workspace_circuits(manifest, args.circuit, args.all)
    pipeline2_module = load_pipeline2_module()
    plans = build_spice_plans(
        target_workspace_dir,
        manifest,
        selected_ids,
        pipeline2_module,
    )
    ngspice_path = pipeline2_module.spice_run.find_ngspice_executable(
        args.ngspice_executable
    )
    if ngspice_path is None:
        requested = args.ngspice_executable or "PATH di sistema"
        raise FileNotFoundError(f"Eseguibile ngspice non trovato: {requested}")

    print(f"Workspace       : {target_workspace_dir}")
    print(f"Circuiti        : {', '.join(selected_ids)}")
    print(f"Output Pipeline2: {target_workspace_dir / 'pipeline2.0'}")
    print(f"ngspice         : {ngspice_path}")
    for plan in plans:
        print(
            f"  {plan['circuit_id']}: {plan['graph_path']} "
            f"+ {plan['values_path']}"
        )

    if args.dry_run:
        print("\nDry-run: Graph, YAML e ngspice sono validi; nessun file verra' creato.")
        return 0

    # Migra in modo trasparente i manifest creati dalla prima versione del
    # comando graph, che registrava le singole immagini ma non la root batch.
    manifest_input_dir = resolve_manifest_input_dir(manifest)
    manifest.setdefault("input_dir", portable_manifest_path(manifest_input_dir))
    manifest.setdefault(
        "values_dir",
        portable_manifest_path(manifest_input_dir / "values"),
    )
    write_manifest(manifest_path, manifest)

    stale = []
    for plan in plans:
        circuit_state = (
            (manifest.get("circuits") or {}).get(plan["circuit_id"], {}).get("pipeline2")
            or {}
        )
        if circuit_state.get("status") == "completed" and not pipeline2_state_is_current(
            circuit_state,
            plan,
        ):
            stale.append(plan["circuit_id"])
    if stale and not args.force:
        raise ValueError(
            "Gli input sono cambiati oppure mancano artefatti per: "
            f"{', '.join(stale)}. Usa --force per rigenerare la Pipeline 2.0."
        )

    logs_dir = target_workspace_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = logs_dir / f"spice_{log_timestamp}.log"
    failures: list[str] = []
    executed: list[str] = []
    skipped: list[str] = []

    with log_path.open("w", encoding="utf-8") as log_handle:
        for plan in plans:
            circuit_id = str(plan["circuit_id"])
            circuit_state = (
                (manifest.get("circuits") or {}).get(circuit_id, {}).get("pipeline2")
                or {}
            )
            if not args.force and pipeline2_state_is_current(circuit_state, plan):
                message = f"{circuit_id}: gia' completato, nessuna riesecuzione."
                print(message)
                log_handle.write(message + "\n")
                skipped.append(circuit_id)
                continue

            output_dir = Path(plan["output_dir"])
            pipeline2_root = target_workspace_dir / "pipeline2.0"
            if args.force and output_dir.exists():
                if output_dir.parent.resolve() != pipeline2_root.resolve():
                    raise ValueError(f"Output Pipeline 2.0 non sicuro: {output_dir}")
                # --force autorizza soltanto la rigenerazione della cartella
                # tecnica del circuito selezionato, mai dell'intero workspace.
                shutil.rmtree(output_dir)

            update_pipeline2_state(
                manifest,
                circuit_id,
                status="running",
                started_at=current_timestamp(),
                completed_at=None,
                graph_json=str(plan["graph_path"]),
                graph_sha256=plan["graph_sha256"],
                values_yaml=str(plan["values_path"]),
                values_sha256=plan["values_sha256"],
                spice_models_sha256=plan["spice_models_sha256"],
                output_dir=str(output_dir),
                error=None,
            )
            write_manifest(manifest_path, manifest)

            try:
                result = pipeline2_module.run_technical_pipeline(
                    input_json=plan["graph_path"],
                    output_dir=output_dir,
                    values_path=plan["values_path"],
                    run_spice=True,
                    ngspice_executable=ngspice_path,
                )
                run_report = result.get("spice_run_report") or {}
                if run_report.get("status") != "success" or run_report.get("exit_code") != 0:
                    raise RuntimeError(
                        "ngspice non ha completato la simulazione: "
                        f"status={run_report.get('status')}, "
                        f"exit_code={run_report.get('exit_code')}."
                    )

                artifacts = collect_pipeline2_artifacts(output_dir)
                update_pipeline2_state(
                    manifest,
                    circuit_id,
                    status="completed",
                    completed_at=current_timestamp(),
                    return_code=0,
                    artifacts=artifacts,
                    log=str(log_path),
                    error=None,
                )
                write_manifest(manifest_path, manifest)
                message = f"{circuit_id}: Pipeline 2.0 e ngspice completati."
                print(message)
                log_handle.write(message + "\n")
                log_handle.flush()
                executed.append(circuit_id)
            except KeyboardInterrupt:
                update_pipeline2_state(
                    manifest,
                    circuit_id,
                    status="interrupted",
                    error="Esecuzione interrotta dall'utente.",
                )
                write_manifest(manifest_path, manifest)
                print(f"\nEsecuzione interrotta. Log: {log_path}", file=sys.stderr)
                return 130
            except Exception as error:  # noqa: BLE001 - il batch deve registrare ogni fallimento.
                update_pipeline2_state(
                    manifest,
                    circuit_id,
                    status="failed",
                    completed_at=current_timestamp(),
                    return_code=1,
                    artifacts=collect_pipeline2_artifacts(output_dir),
                    log=str(log_path),
                    error=str(error),
                )
                write_manifest(manifest_path, manifest)
                message = f"{circuit_id}: errore: {error}"
                print(message, file=sys.stderr)
                log_handle.write(message + "\n")
                log_handle.flush()
                failures.append(circuit_id)

    print(f"\nManifest: {manifest_path}")
    print(f"Log     : {log_path}")
    if executed:
        print(f"Eseguiti: {', '.join(executed)}")
    if skipped:
        print(f"Saltati : {', '.join(skipped)}")
    if failures:
        print(f"Falliti : {', '.join(failures)}", file=sys.stderr)
        return 1
    return 0


def webchat_command(args: argparse.Namespace) -> int:
    """Prepara due copie isolate e avvia un'unica webchat CHAT/AGENT."""
    workspace_id = require_safe_name("workspace", args.workspace)
    circuit_id = require_safe_name("circuito", args.circuit)
    if not 1 <= int(args.port) <= 65535:
        raise ValueError(f"Porta web non valida: {args.port}.")
    target_workspace_dir = workspace_dir(workspace_id).resolve()
    manifest_path = target_workspace_dir / "workspace_manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(
            f"Workspace non inizializzato: {target_workspace_dir}. "
            "Esegui prima i comandi graph e spice."
        )

    manifest = read_manifest(manifest_path, workspace_id)
    select_workspace_circuits(manifest, circuit_id, False)
    source_plan = web_source_plan(target_workspace_dir, manifest, circuit_id)
    batch_name = resolve_manifest_input_dir(manifest).name
    web_root = (target_workspace_dir / "web").resolve()
    session_dirs = {
        "chat": (web_root / "chat" / circuit_id).resolve(),
        "agent": (web_root / "agent" / circuit_id).resolve(),
    }
    if not args.force:
        for mode, session_dir in session_dirs.items():
            if session_dir.exists() and any(session_dir.iterdir()):
                validate_existing_web_session(
                    session_dir,
                    build_run_sources_descriptor(session_dir, mode, source_plan),
                )

    print(f"Workspace       : {target_workspace_dir}")
    print(f"Circuito        : {circuit_id}")
    print(f"Base SPICE      : {source_plan['base_dir']}")
    print(f"Geometria step03: {source_plan['terminal_estimates']}")
    print(f"Geometria step05: {source_plan['terminal_graph']}")
    print(f"Copia CHAT      : {session_dirs['chat']}")
    print(f"Copia AGENT     : {session_dirs['agent']}")

    if args.dry_run:
        print("\nDry-run: sorgenti validate; nessuna copia e nessun server creati.")
        return 0

    ngspice_path: str | None = None
    if not args.prepare_only:
        pipeline2_module = load_pipeline2_module()
        ngspice_path = pipeline2_module.spice_run.find_ngspice_executable(
            args.ngspice_executable
        )
        if ngspice_path is None:
            requested = args.ngspice_executable or "PATH di sistema"
            raise FileNotFoundError(f"Eseguibile ngspice non trovato: {requested}")

    webchat_module = load_webchat_module()
    circuit_manifest = manifest.setdefault("circuits", {}).setdefault(circuit_id, {})
    web_state = circuit_manifest.setdefault("web", {})
    web_state.update(
        {
            "status": "preparing",
            "started_at": current_timestamp(),
            "error": None,
        }
    )
    write_manifest(manifest_path, manifest)

    try:
        prepared = {
            mode: prepare_web_session(
                session_dir=session_dir,
                mode=mode,
                plan=source_plan,
                webchat_module=webchat_module,
                batch_name=batch_name,
                workspace_id=workspace_id,
                force=args.force,
            )
            for mode, session_dir in session_dirs.items()
        }
    except Exception as error:  # noqa: BLE001 - il manifest deve registrare il fallimento.
        web_state.update(
            {
                "status": "failed",
                "completed_at": current_timestamp(),
                "error": str(error),
            }
        )
        write_manifest(manifest_path, manifest)
        raise

    web_state.update(
        {
            "status": "ready",
            "completed_at": current_timestamp(),
            "base_output_dir": str(source_plan["base_dir"]),
            "source_fingerprints": source_plan["fingerprints"],
            "chat": prepared["chat"],
            "agent": prepared["agent"],
            "error": None,
        }
    )
    write_manifest(manifest_path, manifest)

    print("\nWorkspace web pronti.")
    print(f"Manifest: {manifest_path}")
    if args.prepare_only:
        print("Preparazione completata senza avviare il server.")
        return 0

    assert ngspice_path is not None
    web_state["last_opened_at"] = current_timestamp()
    write_manifest(manifest_path, manifest)
    webchat_module.serve_web_chat(
        batch=batch_name,
        circuit=circuit_id,
        experiment=workspace_id,
        output_dir=session_dirs["chat"],
        host=args.host,
        port=args.port,
        ngspice_executable=str(ngspice_path),
        workspace_dirs=session_dirs,
        default_workspace_mode="chat",
        open_browser=not args.no_browser,
    )
    return 0


def all_command(args: argparse.Namespace) -> int:
    """Esegue in sequenza Graph, SPICE e webchat sullo stesso workspace."""
    circuit_id = args.circuit
    if args.all:
        if not args.open_circuit:
            raise ValueError(
                "Con --all devi indicare --open-circuit per scegliere quale "
                "circuito aprire nella webchat."
            )
        available_images = discover_images(resolve_project_path(args.input_dir))
        web_circuit = require_safe_name("circuito", args.open_circuit)
        if web_circuit not in available_images:
            available = ", ".join(sorted(available_images))
            raise FileNotFoundError(
                f"Circuito {web_circuit!r} non trovato. Circuiti disponibili: {available}"
            )
    else:
        web_circuit = require_safe_name("circuito", circuit_id or "")
        if args.open_circuit and args.open_circuit != web_circuit:
            raise ValueError(
                "Con --circuit la webchat apre lo stesso circuito; "
                "non usare un --open-circuit differente."
            )

    shared_selection = {
        "circuit": circuit_id,
        "all": bool(args.all),
    }
    stages = (
        (
            "Pipeline 1.0: immagini -> Graph JSON",
            graph_command,
            argparse.Namespace(
                workspace=args.workspace,
                input_dir=args.input_dir,
                force=args.force,
                dry_run=False,
                **shared_selection,
            ),
        ),
        (
            "Pipeline 2.0: Graph JSON -> ngspice",
            spice_command,
            argparse.Namespace(
                workspace=args.workspace,
                ngspice_executable=args.ngspice_executable,
                force=args.force,
                dry_run=False,
                **shared_selection,
            ),
        ),
        (
            "Viewer e workspace CHAT/AGENT",
            webchat_command,
            argparse.Namespace(
                workspace=args.workspace,
                circuit=web_circuit,
                host=args.host,
                port=args.port,
                ngspice_executable=args.ngspice_executable,
                prepare_only=args.prepare_only,
                no_browser=args.no_browser,
                force=args.force,
                dry_run=False,
            ),
        ),
    )

    for stage_number, (stage_name, handler, stage_args) in enumerate(stages, start=1):
        print(f"\n{'=' * 72}")
        print(f"FASE {stage_number}/3 - {stage_name}")
        print("=" * 72)
        return_code = int(handler(stage_args))
        if return_code != 0:
            print(
                f"\nFlusso completo interrotto nella fase {stage_number}: {stage_name}.",
                file=sys.stderr,
            )
            return return_code

    return 0


def build_parser() -> argparse.ArgumentParser:
    """Costruisce la CLI pubblica dell'orchestratore progressivo."""
    parser = argparse.ArgumentParser(
        description="Orchestratore progressivo delle Pipeline 1.0 e 2.0."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    preflight_parser = subparsers.add_parser(
        "preflight",
        help="Controlla ambiente, LFS, modello, input e programmi esterni senza creare output.",
    )
    preflight_parser.add_argument(
        "--input-dir",
        default="data/batchPipeline2.0/batchDemo",
        help="Batch da validare per il flusso completo (default: batchDemo canonico).",
    )
    preflight_parser.add_argument(
        "--ngspice-executable",
        default=None,
        help="Path o nome di ngspice; se omesso viene cercato nel PATH.",
    )
    preflight_parser.add_argument(
        "--tesseract-executable",
        default=None,
        help="Path o nome di Tesseract; precede TESSERACT_CMD e il PATH.",
    )
    preflight_parser.add_argument(
        "--require-openai",
        action="store_true",
        help="Considera obbligatoria anche OPENAI_API_KEY per le funzioni AGENT.",
    )
    preflight_parser.set_defaults(handler=preflight_command)

    graph_parser = subparsers.add_parser(
        "graph",
        help="Esegue la Pipeline 1.0 completa, dallo step 01 allo step 06.",
    )
    graph_parser.add_argument(
        "--workspace",
        required=True,
        help="Nome della run persistente sotto outputs/demo_workspaces/.",
    )
    graph_parser.add_argument(
        "--input-dir",
        required=True,
        help="Cartella contenente le immagini, assoluta o relativa al progetto.",
    )
    selection = graph_parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--circuit", help="Identificativo di un solo circuito.")
    selection.add_argument(
        "--all",
        action="store_true",
        help="Elabora tutte le immagini supportate presenti nella cartella input.",
    )
    graph_parser.add_argument(
        "--force",
        action="store_true",
        help="Rigenera anche i circuiti gia' completati nel workspace.",
    )
    graph_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostra la selezione e gli step senza creare file o eseguire la pipeline.",
    )
    graph_parser.set_defaults(handler=graph_command)

    spice_parser = subparsers.add_parser(
        "spice",
        help="Esegue la Pipeline 2.0 tecnica, dagli step 01 a 08.",
    )
    spice_parser.add_argument(
        "--workspace",
        required=True,
        help="Workspace persistente gia' inizializzato dal comando graph.",
    )
    spice_selection = spice_parser.add_mutually_exclusive_group(required=True)
    spice_selection.add_argument(
        "--circuit",
        help="Identificativo di un solo circuito registrato nel workspace.",
    )
    spice_selection.add_argument(
        "--all",
        action="store_true",
        help="Elabora tutti i circuiti registrati nel workspace.",
    )
    spice_parser.add_argument(
        "--ngspice-executable",
        default=None,
        help="Path o nome dell'eseguibile ngspice; se omesso viene cercato nel PATH.",
    )
    spice_parser.add_argument(
        "--force",
        action="store_true",
        help="Rigenera la cartella Pipeline 2.0 dei circuiti selezionati.",
    )
    spice_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Valida workspace, Graph, YAML e ngspice senza creare output.",
    )
    spice_parser.set_defaults(handler=spice_command)

    webchat_parser = subparsers.add_parser(
        "webchat",
        help="Prepara viewer e copie isolate, poi apre CHAT e AGENT nello stesso server.",
    )
    webchat_parser.add_argument(
        "--workspace",
        required=True,
        help="Workspace persistente con Pipeline 1.0 e Pipeline 2.0 completate.",
    )
    webchat_parser.add_argument(
        "--circuit",
        required=True,
        help="Circuito da aprire nella webchat.",
    )
    webchat_parser.add_argument("--host", default="127.0.0.1", help="Host locale del server.")
    webchat_parser.add_argument("--port", type=int, default=8765, help="Porta locale del server.")
    webchat_parser.add_argument(
        "--ngspice-executable",
        default=None,
        help="Path o nome di ngspice usato dalle future run scenario.",
    )
    webchat_parser.add_argument(
        "--prepare-only",
        action="store_true",
        help="Prepara copie e viewer senza avviare il server.",
    )
    webchat_parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Avvia il server senza aprire automaticamente il browser.",
    )
    webchat_parser.add_argument(
        "--force",
        action="store_true",
        help="Ricrea entrambe le copie, eliminando history e scenari web esistenti.",
    )
    webchat_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Valida base SPICE, immagine e geometria senza creare file.",
    )
    webchat_parser.set_defaults(handler=webchat_command)

    all_parser = subparsers.add_parser(
        "all",
        help="Esegue Pipeline 1.0, Pipeline 2.0 e webchat nello stesso workspace.",
    )
    all_parser.add_argument(
        "--workspace",
        required=True,
        help="Nome della run persistente sotto outputs/demo_workspaces/.",
    )
    all_parser.add_argument(
        "--input-dir",
        required=True,
        help="Cartella contenente immagini e sottocartella values/.",
    )
    all_selection = all_parser.add_mutually_exclusive_group(required=True)
    all_selection.add_argument("--circuit", help="Elabora e apre un solo circuito.")
    all_selection.add_argument(
        "--all",
        action="store_true",
        help="Elabora tutte le immagini presenti nella cartella input.",
    )
    all_parser.add_argument(
        "--open-circuit",
        help="Con --all, identifica il circuito da aprire nella webchat.",
    )
    all_parser.add_argument("--host", default="127.0.0.1", help="Host locale del server.")
    all_parser.add_argument("--port", type=int, default=8765, help="Porta locale del server.")
    all_parser.add_argument(
        "--ngspice-executable",
        default=None,
        help="Path o nome dell'eseguibile ngspice.",
    )
    all_parser.add_argument(
        "--prepare-only",
        action="store_true",
        help="Completa entrambe le pipeline e prepara il web senza avviare il server.",
    )
    all_parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Avvia il server senza aprire automaticamente il browser.",
    )
    all_parser.add_argument(
        "--force",
        action="store_true",
        help="Rigenera tutte le fasi, incluse le copie web del circuito aperto.",
    )
    all_parser.set_defaults(handler=all_command)
    return parser


def main() -> int:
    """Legge gli argomenti, esegue il comando scelto e normalizza gli errori."""
    parser = build_parser()
    args = parser.parse_args()
    try:
        return int(args.handler(args))
    except (FileNotFoundError, RuntimeError, ValueError) as error:
        parser.error(str(error))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
