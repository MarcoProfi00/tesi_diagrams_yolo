"""Runtime condiviso per gli scenari controllati della Pipeline 2.0.

Il modulo contiene soltanto operazioni deterministiche. Non decide quale
scenario eseguire e non chiama direttamente un modello AI: valida, prepara,
esegue e registra una run scenario senza modificare la base.
"""

from __future__ import annotations

from datetime import datetime
import importlib.util
import json
import re
import shutil
from pathlib import Path
from typing import Any, Iterable

from viewer_core.layout_builder import write_viewer_layout
from viewer_core.model_builder import write_viewer_model
from viewer_core.svg_renderer import write_viewer_svg
from viewer_core.contracts import VIEWER_LAYOUT_NAME, VIEWER_MODEL_NAME, VIEWER_SVG_NAME


STEP12_PATH = Path(__file__).resolve().parent / "12_controlled_scenarios.py"
MAX_EXECUTABLE_SCENARIOS = 5
SCENARIO_BASE_FILES = (
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
)


class ScenarioRuntimeError(RuntimeError):
    """Rappresenta un errore controllato del runtime scenario."""


def read_json_safe(path: Path) -> dict[str, Any]:
    """Legge un oggetto JSON e restituisce un dizionario vuoto se manca."""
    if not path.exists() or not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def write_json(path: Path, data: dict[str, Any]) -> None:
    """Scrive un oggetto JSON leggibile creando la directory necessaria."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def safe_scenario_id(value: str) -> str:
    """Normalizza un identificatore scenario per usarlo come nome cartella."""
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value).strip())
    return cleaned.strip("._") or "scenario"


def scenario_signature(scenario: dict[str, Any]) -> str:
    """Calcola una firma stabile basata soltanto sulle azioni tecniche."""
    actions = scenario.get("actions")
    normalized = actions if isinstance(actions, list) else []
    return json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def scenario_was_executed(scenario_dir: Path) -> bool:
    """Indica se lo scenario ha realmente avviato una run SPICE."""
    report = read_json_safe(scenario_dir / "12_controlled_scenarios.json")
    status = read_json_safe(scenario_dir / "scenario_status.json")
    return bool(report.get("spice_executed") or status.get("spice_executed"))


def list_scenario_dirs(output_dir: Path) -> list[Path]:
    """Elenca in ordine stabile le cartelle scenario del circuito."""
    scenarios_root = output_dir / "scenarios"
    if not scenarios_root.exists() or not scenarios_root.is_dir():
        return []
    return sorted(path for path in scenarios_root.iterdir() if path.is_dir())


def count_executed_scenarios(output_dir: Path) -> int:
    """Conta soltanto gli scenari per cui SPICE e stato realmente avviato."""
    return sum(1 for path in list_scenario_dirs(output_dir) if scenario_was_executed(path))


def find_duplicate_scenario(output_dir: Path, scenario: dict[str, Any]) -> Path | None:
    """Cerca una run esistente con la stessa sequenza di azioni."""
    signature = scenario_signature(scenario)
    for scenario_dir in list_scenario_dirs(output_dir):
        existing = read_json_safe(scenario_dir / "scenario.json")
        if scenario_signature(existing) == signature:
            return scenario_dir
    return None


def validate_scenario(
    scenario: dict[str, Any],
    allowed_action_types: Iterable[str] | None = None,
) -> list[str]:
    """Valida la forma minima e l'eventuale whitelist delle azioni."""
    errors: list[str] = []
    actions = scenario.get("actions")
    if not isinstance(actions, list) or not actions:
        return ["scenario.actions deve essere una lista non vuota"]

    allowed = set(allowed_action_types or [])
    for index, action in enumerate(actions, start=1):
        if not isinstance(action, dict):
            errors.append(f"azione {index}: deve essere un oggetto JSON")
            continue
        action_type = str(action.get("type") or "").strip()
        if not action_type:
            errors.append(f"azione {index}: type mancante")
        elif allowed and action_type not in allowed:
            errors.append(f"azione {index}: tipo non consentito '{action_type}'")
    return errors


def next_scenario_id(output_dir: Path, prefix: str = "agent_scenario") -> str:
    """Genera il primo identificatore progressivo non ancora utilizzato."""
    existing = {path.name for path in list_scenario_dirs(output_dir)}
    index = 1
    while f"{prefix}_{index}" in existing:
        index += 1
    return f"{prefix}_{index}"


def copy_base_run(output_dir: Path, scenario_dir: Path) -> dict[str, Any]:
    """Copia gli artefatti base in snapshot e run senza alterare gli originali."""
    base_snapshot_dir = scenario_dir / "base_snapshot"
    run_dir = scenario_dir / "run"
    base_snapshot_dir.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)

    copied: list[str] = []
    missing: list[str] = []
    for filename in SCENARIO_BASE_FILES:
        source = output_dir / filename
        if not source.exists() or not source.is_file():
            missing.append(filename)
            continue
        shutil.copy2(source, base_snapshot_dir / filename)
        shutil.copy2(source, run_dir / filename)
        copied.append(filename)

    manifest = {
        "status": "copied",
        "base_output_dir": str(output_dir),
        "base_snapshot_dir": str(base_snapshot_dir),
        "run_dir": str(run_dir),
        "copied_files": copied,
        "missing_optional_files": missing,
        "created_or_updated_at": datetime.now().isoformat(timespec="seconds"),
    }
    write_json(scenario_dir / "scenario_copy_manifest.json", manifest)
    return {**manifest, "base_snapshot_dir": base_snapshot_dir, "run_dir": run_dir}


def load_step12_module() -> Any:
    """Carica lo step 12 mantenendo invariato il suo entry point numerico."""
    spec = importlib.util.spec_from_file_location("pipeline2_step12_runtime", STEP12_PATH)
    if spec is None or spec.loader is None:
        raise ScenarioRuntimeError(f"Impossibile caricare lo step 12: {STEP12_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def generate_scenario_viewer(run_dir: Path) -> dict[str, str]:
    """Genera modello, layout e SVG del viewer per la run scenario."""
    write_viewer_model(run_dir)
    write_viewer_layout(run_dir)
    write_viewer_svg(run_dir)
    return {
        "model": str(run_dir / VIEWER_MODEL_NAME),
        "layout": str(run_dir / VIEWER_LAYOUT_NAME),
        "svg": str(run_dir / VIEWER_SVG_NAME),
    }


def execute_scenario(
    output_dir: Path,
    scenario: dict[str, Any],
    ngspice_executable: str | None,
    allowed_action_types: Iterable[str] | None = None,
    source_label: str = "scenario_runtime",
    reject_duplicates: bool = True,
) -> dict[str, Any]:
    """Prepara ed esegue uno scenario completo applicando tutti i guardrail."""
    errors = validate_scenario(scenario, allowed_action_types)
    if errors:
        raise ScenarioRuntimeError("; ".join(errors))

    analysis = str(scenario.get("analysis") or "op").strip().lower()
    if analysis == "tran" and not (output_dir / "08_tran.csv").exists():
        raise ScenarioRuntimeError(
            "Scenario tran non eseguibile: la base run non contiene 08_tran.csv"
        )

    executed_count = count_executed_scenarios(output_dir)
    if executed_count >= MAX_EXECUTABLE_SCENARIOS:
        raise ScenarioRuntimeError("Budget esaurito: massimo 5 run scenario eseguite")

    duplicate_dir = find_duplicate_scenario(output_dir, scenario)
    if reject_duplicates and duplicate_dir is not None:
        raise ScenarioRuntimeError(f"Scenario duplicato: {duplicate_dir.name}")

    payload = dict(scenario)
    scenario_id = safe_scenario_id(
        str(payload.get("scenario_id") or next_scenario_id(output_dir))
    )
    payload["scenario_id"] = scenario_id
    scenario_dir = output_dir / "scenarios" / scenario_id
    if scenario_dir.exists():
        raise ScenarioRuntimeError(f"Cartella scenario gia esistente: {scenario_id}")

    scenario_dir.mkdir(parents=True, exist_ok=False)
    write_json(scenario_dir / "scenario.json", payload)
    write_json(
        scenario_dir / "scenario_status.json",
        {
            "status": "prepared",
            "stage": "scenario_folder_created",
            "scenario_id": scenario_id,
            "source": source_label,
            "spice_executed": False,
            "created_or_updated_at": datetime.now().isoformat(timespec="seconds"),
        },
    )
    copy_result = copy_base_run(output_dir, scenario_dir)

    step12 = load_step12_module()
    report = step12.apply_scenario(
        scenario_dir,
        run_spice=True,
        ngspice_executable=ngspice_executable,
    )
    if not isinstance(report, dict):
        report = {}

    viewer: dict[str, str] = {}
    viewer_error: str | None = None
    try:
        viewer = generate_scenario_viewer(copy_result["run_dir"])
    except Exception as exc:  # Il risultato SPICE resta valido anche senza viewer.
        viewer_error = str(exc)

    return {
        "scenario_id": scenario_id,
        "scenario_dir": str(scenario_dir),
        "run_dir": str(copy_result["run_dir"]),
        "status": report.get("status") or "unknown",
        "spice_executed": bool(report.get("spice_executed")),
        "spice_status": report.get("spice_status"),
        "spice_exit_code": report.get("spice_exit_code"),
        "comparison_summary": report.get("comparison_summary") or {},
        "diagnostic_outcome": report.get("diagnostic_outcome") or {},
        "viewer": viewer,
        "viewer_error": viewer_error,
        "executed_scenarios_count": count_executed_scenarios(output_dir),
    }
