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

from scenario_actions import repeated_assignment_message, repeated_target_assignments
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
    "07_external_models.lib",
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
    """Calcola una firma stabile della modifica elettrica e della sua analisi."""
    actions = scenario.get("actions")
    # La stessa modifica puo' essere utile sia come punto operativo sia come
    # transitorio: le due run producono evidenze diverse e non sono duplicate.
    # Compare, expect e measure non entrano invece nella firma perche' non
    # modificano la netlist o l'analisi eseguita.
    normalized = {
        "actions": actions if isinstance(actions, list) else [],
        "analysis": str(scenario.get("analysis") or "op").strip().lower(),
    }
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
    errors.extend(
        repeated_assignment_message(conflict)
        for conflict in repeated_target_assignments(actions)
    )
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


def load_transient_component_profile(run_dir: Path, target: str) -> dict[str, Any]:
    """Legge il profilo transitorio di un componente dal modello viewer della run."""
    model = read_json_safe(run_dir / VIEWER_MODEL_NAME)
    transient = model.get("transient") if isinstance(model.get("transient"), dict) else {}
    profiles = transient.get("led_profiles") if isinstance(transient.get("led_profiles"), dict) else {}
    profile = profiles.get(target)
    return profile if isinstance(profile, dict) else {}


def evaluate_temporal_expectation(
    base_profile: dict[str, Any],
    scenario_profile: dict[str, Any],
    expectation: dict[str, Any],
) -> dict[str, Any]:
    """Valuta criteri temporali dichiarati confrontando base run e scenario."""
    target = str(expectation.get("target") or "")
    if not base_profile or not scenario_profile:
        return {
            "target": target,
            "available": False,
            "met": False,
            "reason": "Profilo transitorio del componente non disponibile nella base run o nello scenario.",
            "base_profile": base_profile,
            "scenario_profile": scenario_profile,
            "conditions": [],
        }

    conditions: list[dict[str, Any]] = []
    required_state = expectation.get("required_state")
    if required_state is not None:
        actual = str(scenario_profile.get("state") or "")
        conditions.append(
            {
                "criterion": "required_state",
                "expected": required_state,
                "actual": actual,
                "met": actual == required_state,
            }
        )

    required_regular = expectation.get("require_regular_period")
    if required_regular is not None:
        actual = bool(scenario_profile.get("regular_period"))
        conditions.append(
            {
                "criterion": "require_regular_period",
                "expected": required_regular,
                "actual": actual,
                "met": actual is required_regular,
            }
        )

    scenario_duty = scenario_profile.get("duty_cycle")
    base_duty = base_profile.get("duty_cycle")
    minimum_duty = expectation.get("min_duty_cycle")
    if minimum_duty is not None:
        conditions.append(
            {
                "criterion": "min_duty_cycle",
                "expected": minimum_duty,
                "actual": scenario_duty,
                "met": isinstance(scenario_duty, (int, float)) and scenario_duty >= minimum_duty,
            }
        )

    minimum_relative_increase = expectation.get("min_relative_duty_increase")
    if minimum_relative_increase is not None:
        relative_increase = None
        relative_increase_met = False
        if isinstance(base_duty, (int, float)) and isinstance(scenario_duty, (int, float)):
            if abs(base_duty) > 1e-12:
                relative_increase = (scenario_duty - base_duty) / abs(base_duty)
                relative_increase_met = relative_increase >= minimum_relative_increase
            elif scenario_duty > base_duty:
                relative_increase_met = True
        conditions.append(
            {
                "criterion": "min_relative_duty_increase",
                "expected": minimum_relative_increase,
                "actual": relative_increase,
                "met": relative_increase_met,
            }
        )

    return {
        "target": target,
        "available": True,
        "met": bool(conditions) and all(bool(item.get("met")) for item in conditions),
        "reason": "Criteri temporali verificati." if conditions and all(
            bool(item.get("met")) for item in conditions
        ) else "Almeno un criterio temporale non e soddisfatto.",
        "base_profile": base_profile,
        "scenario_profile": scenario_profile,
        "conditions": conditions,
    }


def temporal_correction_is_resolved(
    scenario: dict[str, Any],
    summary: dict[str, Any],
    evaluation: dict[str, Any],
) -> bool:
    """
    Verifica se uno scenario temporale corregge direttamente il sintomo.

    Il passaggio tra stati qualitativi, per esempio da acceso fisso a
    lampeggiante regolare, e gia una correzione misurabile e non richiede anche
    una variazione scalare relativa del 10%. Restano comunque obbligatori tutti
    i criteri elettrici, temporali, di guadagno e di qualita dichiarati.
    """
    if str(scenario.get("intent") or "").strip().lower() != "correction":
        return False
    if not evaluation.get("available") or not evaluation.get("met"):
        return False

    expected = int(summary.get("expected_count") or 0)
    expectations_met = int(summary.get("expectations_met_count") or 0)
    expectations_failed = int(summary.get("expectations_failed_count") or 0)
    expectations_missing = int(summary.get("expectations_missing_count") or 0)
    if (
        expected <= 0
        or expectations_met != expected
        or expectations_failed > 0
        or expectations_missing > 0
    ):
        return False

    if bool(summary.get("gain_required")) and not (
        bool(summary.get("gain_available")) and bool(summary.get("gain_sufficient"))
    ):
        return False
    if bool(summary.get("quality_required")) and not (
        bool(summary.get("quality_available"))
        and bool(summary.get("quality_improved"))
        and bool(summary.get("quality_acceptable"))
        and bool(summary.get("quality_output_preserved"))
    ):
        return False
    return True


def update_report_with_temporal_expectation(
    output_dir: Path,
    scenario_dir: Path,
    scenario: dict[str, Any],
    report: dict[str, Any],
    step12: Any,
) -> dict[str, Any]:
    """Integra l'esito scenario con i criteri temporali dichiarati dall'agente."""
    expectation = scenario.get("temporal_expect")
    if not isinstance(expectation, dict) or not report.get("spice_executed"):
        return report

    base_model_path = output_dir / VIEWER_MODEL_NAME
    if not base_model_path.exists():
        write_viewer_model(output_dir)

    run_dir = scenario_dir / "run"
    evaluation = evaluate_temporal_expectation(
        load_transient_component_profile(output_dir, str(expectation.get("target") or "")),
        load_transient_component_profile(run_dir, str(expectation.get("target") or "")),
        expectation,
    )
    comparison_path = scenario_dir / "scenario_comparison.json"
    comparison = read_json_safe(comparison_path)
    if not comparison:
        return report

    summary = comparison.get("summary") if isinstance(comparison.get("summary"), dict) else {}
    summary["temporal_required"] = True
    summary["temporal_available"] = bool(evaluation.get("available"))
    summary["temporal_met"] = bool(evaluation.get("met"))
    comparison["summary"] = summary
    comparison["temporal_expectation"] = evaluation

    outcome = comparison.get("diagnostic_outcome")
    outcome = dict(outcome) if isinstance(outcome, dict) else {}
    if not evaluation.get("available"):
        outcome.update(
            {
                "status": "partially_resolved",
                "technical_label": "Transient profile unavailable",
                "label": "Profilo transitorio non disponibile",
                "reason": str(evaluation.get("reason")),
                "stop_automation": False,
                "confidence": "low",
                "next_step": "Serve un altro scenario oppure una misura transitoria disponibile.",
            }
        )
    elif not evaluation.get("met"):
        outcome.update(
            {
                "status": "partially_resolved",
                "technical_label": "Temporal criteria not satisfied",
                "label": "Criteri temporali non soddisfatti",
                "reason": str(evaluation.get("reason")),
                "stop_automation": False,
                "confidence": "low",
                "next_step": "Il comportamento temporale non soddisfa ancora l'obiettivo: prova un'altra correzione.",
            }
        )
    elif temporal_correction_is_resolved(scenario, summary, evaluation):
        outcome.update(
            {
                "status": "resolved_candidate",
                "technical_label": "Transient correction verified",
                "label": "Criteri elettrici e temporali soddisfatti",
                "reason": "Le aspettative elettriche e il profilo transitorio richiesto sono verificati.",
                "stop_automation": True,
                "confidence": "medium",
                "next_step": "La correzione e verificata: puoi passare alla conclusione diagnostica.",
            }
        )

    comparison["diagnostic_outcome"] = outcome
    report["comparison_summary"] = summary
    report["diagnostic_outcome"] = outcome
    write_json(comparison_path, comparison)
    write_json(scenario_dir / "12_controlled_scenarios.json", report)
    step12.update_status_file(scenario_dir, report)
    return report


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

    report = update_report_with_temporal_expectation(
        output_dir=output_dir,
        scenario_dir=scenario_dir,
        scenario=payload,
        report=report,
        step12=step12,
    )

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
