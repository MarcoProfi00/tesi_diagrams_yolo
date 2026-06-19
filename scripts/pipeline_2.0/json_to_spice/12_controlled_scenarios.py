"""
Scenari simulativi controllati.

Questo script applica modifiche di scenario solo dentro la cartella scenario,
senza toccare mai la base run originale della Pipeline 2.0.

Versione attuale minimale:

- legge `scenario.json`;
- lavora sulla netlist copiata in `run/07_netlist.cir`;
- supporta solo l'azione generale `drive_node_voltage`;
- aggiunge o aggiorna una sorgente SPICE di scenario;
- salva `12_controlled_scenarios.json`;
- aggiorna `scenario_status.json`;
- esegue ngspice solo se richiesto con `--run-spice`.

Esempio di azione supportata:

```json
{
  "type": "drive_node_voltage",
  "target": "N002",
  "value": "5V"
}
```

Questa azione diventa una riga SPICE del tipo:

```spice
VSCENARIO_N002 N002 0 DC 5
```
"""

from __future__ import annotations

import argparse
from datetime import datetime
import importlib.util
import json
import re
from pathlib import Path
from typing import Any


NETLIST_NAME = "07_netlist.cir"
SCENARIO_NAME = "scenario.json"
STATUS_NAME = "scenario_status.json"
REPORT_NAME = "12_controlled_scenarios.json"
COMPARISON_NAME = "scenario_comparison.json"
SPICE_RUN_NAME = "08_spice_run.json"
STEP08_PATH = Path(__file__).resolve().parent / "08_spice_run.py"


def read_json(path: Path) -> dict[str, Any]:
    """Legge un JSON e restituisce un dizionario."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    """Scrive un JSON leggibile e stabile."""
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_step08_module() -> Any:
    """Carica lo step 08 per riusare la stessa esecuzione ngspice della pipeline."""
    spec = importlib.util.spec_from_file_location("pipeline2_step08", STEP08_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load step 08 from {STEP08_PATH}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalize_spice_dc_value(value: Any) -> str:
    """
    Normalizza un valore DC semplice per SPICE.

    Accetta valori come `5V`, `5 V`, `12`, `3.3v`. Per ora non interpreta
    espressioni complesse: le lascia quasi intatte, rimuovendo solo il suffisso V.
    """
    text = str(value).strip()
    text = re.sub(r"\s+", "", text)
    text = re.sub(r"(?i)v$", "", text)
    if not text:
        raise ValueError("Empty voltage value")
    return text


def sanitize_spice_name(text: str) -> str:
    """Crea un identificatore SPICE semplice partendo da un target di scenario."""
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip())
    return cleaned.strip("_") or "NODE"


def validate_node_target(target: Any, node_map: dict[str, Any]) -> str:
    """Controlla che il nodo target esista nella mappa nodi della run scenario."""
    node = str(target).strip()
    if not node:
        raise ValueError("Missing target node")
    if node == "0":
        raise ValueError("Cannot drive ground node 0")

    known_nodes = {str(item.get("node_id")) for item in node_map.get("nodes", []) if isinstance(item, dict)}
    if known_nodes and node not in known_nodes:
        raise ValueError(f"Target node {node} not found in 03_node_map.json")

    return node


def insert_or_replace_source(netlist_text: str, source_name: str, source_line: str) -> tuple[str, str]:
    """
    Inserisce o aggiorna una sorgente di scenario nella netlist.

    La riga viene messa prima della prima direttiva SPICE principale, cosi resta
    nella parte dichiarativa della netlist.
    """
    lines = netlist_text.splitlines()
    source_pattern = re.compile(rf"^\s*{re.escape(source_name)}\s+", flags=re.IGNORECASE)

    for index, line in enumerate(lines):
        if source_pattern.match(line):
            lines[index] = source_line
            return "\n".join(lines) + "\n", "updated"

    insert_at = len(lines)
    for index, line in enumerate(lines):
        stripped = line.strip().lower()
        if stripped in {".op", ".end"} or stripped.startswith((".tran", ".ac", ".dc", ".control")):
            insert_at = index
            break

    lines.insert(insert_at, source_line)
    return "\n".join(lines) + "\n", "inserted"


def apply_drive_node_voltage(
    action: dict[str, Any],
    run_dir: Path,
    netlist_text: str,
) -> tuple[str, dict[str, Any]]:
    """Applica l'azione `drive_node_voltage` alla netlist scenario."""
    node_map = read_json(run_dir / "03_node_map.json")
    target_node = validate_node_target(action.get("target"), node_map)
    dc_value = normalize_spice_dc_value(action.get("value"))

    source_name = f"VSCENARIO_{sanitize_spice_name(target_node)}"
    source_line = f"{source_name} {target_node} 0 DC {dc_value}"
    updated_netlist, operation = insert_or_replace_source(netlist_text, source_name, source_line)

    result = {
        "status": "applied",
        "type": "drive_node_voltage",
        "target": target_node,
        "value": action.get("value"),
        "normalized_dc_value": dc_value,
        "inserted_line": source_line,
        "operation": operation,
        "spice_executed": False,
    }
    return updated_netlist, result


def run_spice_for_scenario(
    run_dir: Path,
    executable: str | None = None,
    timeout_seconds: int = 30,
) -> dict[str, Any]:
    """Esegue ngspice sulla netlist della run scenario e salva il report 08."""
    step08 = load_step08_module()
    spice_report = step08.run_ngspice(
        output_dir=run_dir,
        netlist_filename=NETLIST_NAME,
        executable=executable,
        timeout_seconds=timeout_seconds,
    )
    write_json(run_dir / SPICE_RUN_NAME, spice_report)
    return spice_report


def normalize_quantity_name(name: str) -> str:
    """Normalizza una grandezza richiesta dallo scenario, ad esempio v(N002)."""
    text = str(name).strip()
    match = re.match(r"(?i)^([vip])\(([^)]+)\)$", text)
    if not match:
        return text
    kind = match.group(1).lower()
    target = match.group(2).strip()
    if kind == "v":
        return f"v({target.upper()})"
    return f"{kind}({target})"


def quantity_lookup_key(name: str) -> str:
    """Crea una chiave case-insensitive per confrontare grandezze SPICE."""
    return normalize_quantity_name(name).lower()


def parse_float(text: str) -> float | None:
    """Converte una stringa SPICE in float quando possibile."""
    try:
        return float(text)
    except ValueError:
        return None


def parse_ngspice_stdout(stdout_path: Path) -> dict[str, float]:
    """
    Estrae valori principali da uno stdout ngspice `.op`.

    Supporta:
    - tensioni nodo: `v(N001)`;
    - correnti sorgenti: `i(vvcc#branch)`;
    - correnti/potenze dispositivi nelle tabelle: `i(Rlamp13_1)`, `p(Rlamp13_1)`.
    """
    if not stdout_path.exists():
        return {}

    values: dict[str, float] = {}
    lines = stdout_path.read_text(encoding="utf-8", errors="replace").splitlines()
    in_node_table = False
    in_source_table = False
    current_devices: list[str] = []

    for raw_line in lines:
        line = raw_line.strip()
        lower = line.lower()

        if not line:
            in_node_table = False
            in_source_table = False
            current_devices = []
            continue

        if lower.startswith("node") and "voltage" in lower:
            in_node_table = True
            in_source_table = False
            current_devices = []
            continue

        if lower.startswith("source") and "current" in lower:
            in_source_table = True
            in_node_table = False
            current_devices = []
            continue

        if set(line.replace("\t", "").replace(" ", "")) <= {"-"}:
            continue

        parts = line.split()
        if len(parts) < 2:
            continue

        if in_node_table:
            value = parse_float(parts[-1])
            if value is not None:
                values[quantity_lookup_key(f"v({parts[0]})")] = value
            continue

        if in_source_table:
            value = parse_float(parts[-1])
            if value is not None:
                source_name = parts[0]
                values[quantity_lookup_key(f"i({source_name})")] = value
            continue

        if parts[0].lower() == "device":
            current_devices = parts[1:]
            continue

        if current_devices and len(parts) == len(current_devices) + 1:
            property_name = parts[0].lower()
            for device_name, value_text in zip(current_devices, parts[1:]):
                value = parse_float(value_text)
                if value is None:
                    continue
                if property_name in {"i", "id"}:
                    values[quantity_lookup_key(f"i({device_name})")] = value
                elif property_name == "p":
                    values[quantity_lookup_key(f"p({device_name})")] = value

    return values


def classify_change(base_value: float | None, scenario_value: float | None) -> str:
    """Classifica una variazione semplice tra base e scenario."""
    if base_value is None or scenario_value is None:
        return "missing"
    if abs(base_value) < 1e-12 and abs(scenario_value) >= 1e-12:
        return "activated"
    if abs(base_value) >= 1e-12 and abs(scenario_value) < 1e-12:
        return "deactivated"
    if abs(scenario_value - base_value) < 1e-12:
        return "unchanged"
    return "changed"


def build_scenario_comparison(scenario_dir: Path, scenario: dict[str, Any]) -> dict[str, Any]:
    """Confronta le grandezze richieste tra base run e scenario run."""
    status = read_json(scenario_dir / STATUS_NAME) if (scenario_dir / STATUS_NAME).exists() else {}
    base_output_dir = Path(status.get("base_output_dir") or scenario_dir.parent.parent)
    run_dir = scenario_dir / "run"

    base_values = parse_ngspice_stdout(base_output_dir / "08_ngspice_stdout.txt")
    scenario_values = parse_ngspice_stdout(run_dir / "08_ngspice_stdout.txt")

    requested = scenario.get("compare") or []
    if not isinstance(requested, list):
        requested = []

    quantities: list[dict[str, Any]] = []
    activated = 0
    changed = 0
    missing = 0

    for item in requested:
        quantity = normalize_quantity_name(str(item))
        lookup_key = quantity_lookup_key(quantity)
        base_value = base_values.get(lookup_key)
        scenario_value = scenario_values.get(lookup_key)
        delta = None
        if base_value is not None and scenario_value is not None:
            delta = scenario_value - base_value

        change = classify_change(base_value, scenario_value)
        if change == "activated":
            activated += 1
        if change in {"activated", "deactivated", "changed"}:
            changed += 1
        if change == "missing":
            missing += 1

        quantities.append(
            {
                "quantity": quantity,
                "base_value": base_value,
                "scenario_value": scenario_value,
                "delta": delta,
                "change": change,
            }
        )

    comparison = {
        "source_format": "pipeline2.0_scenario_comparison",
        "scenario_id": scenario.get("scenario_id"),
        "scenario_title": scenario.get("title"),
        "base_output_dir": str(base_output_dir),
        "scenario_run_dir": str(run_dir),
        "base_stdout": str(base_output_dir / "08_ngspice_stdout.txt"),
        "scenario_stdout": str(run_dir / "08_ngspice_stdout.txt"),
        "quantities": quantities,
        "summary": {
            "requested_count": len(quantities),
            "changed_count": changed,
            "activated_count": activated,
            "missing_count": missing,
        },
        "created_or_updated_at": datetime.now().isoformat(timespec="seconds"),
    }
    write_json(scenario_dir / COMPARISON_NAME, comparison)
    return comparison


def apply_scenario(
    scenario_dir: Path,
    run_spice: bool = False,
    ngspice_executable: str | None = None,
    timeout_seconds: int = 30,
) -> dict[str, Any]:
    """Applica le azioni supportate di uno scenario alla cartella `run`."""
    scenario_path = scenario_dir / SCENARIO_NAME
    run_dir = scenario_dir / "run"
    netlist_path = run_dir / NETLIST_NAME

    if not scenario_path.exists():
        raise FileNotFoundError(f"Missing scenario file: {scenario_path}")
    if not run_dir.exists():
        raise FileNotFoundError(f"Missing run directory: {run_dir}")
    if not netlist_path.exists():
        raise FileNotFoundError(f"Missing scenario netlist: {netlist_path}")

    scenario = read_json(scenario_path)
    actions = scenario.get("actions") or []
    if not isinstance(actions, list):
        raise ValueError("scenario.actions must be a list")

    netlist_text = netlist_path.read_text(encoding="utf-8")
    applied_actions: list[dict[str, Any]] = []
    unsupported_actions: list[dict[str, Any]] = []
    failed_actions: list[dict[str, Any]] = []

    for index, action in enumerate(actions, start=1):
        if not isinstance(action, dict):
            failed_actions.append({"index": index, "status": "failed", "reason": "Action is not an object"})
            continue

        action_type = str(action.get("type") or "").strip()
        try:
            if action_type == "drive_node_voltage":
                netlist_text, result = apply_drive_node_voltage(action, run_dir, netlist_text)
                result["index"] = index
                applied_actions.append(result)
            else:
                unsupported_actions.append({
                    "index": index,
                    "status": "unsupported",
                    "type": action_type or None,
                    "reason": "Action type is not supported in the current minimal version.",
                })
        except Exception as exc:
            failed_actions.append({
                "index": index,
                "status": "failed",
                "type": action_type or None,
                "reason": str(exc),
            })

    if applied_actions:
        netlist_path.write_text(netlist_text, encoding="utf-8")

    status = "applied_not_run" if applied_actions and not failed_actions else "not_applied"
    if failed_actions:
        status = "partial_or_failed" if applied_actions else "failed"

    spice_report: dict[str, Any] | None = None
    comparison_report: dict[str, Any] | None = None
    if run_spice and applied_actions and not failed_actions:
        spice_report = run_spice_for_scenario(
            run_dir=run_dir,
            executable=ngspice_executable,
            timeout_seconds=timeout_seconds,
        )
        status = "spice_success" if spice_report.get("status") == "success" else "spice_failed"
        if spice_report.get("status") == "success":
            comparison_report = build_scenario_comparison(scenario_dir, scenario)

    report = {
        "source_format": "pipeline2.0_controlled_scenario_report",
        "status": status,
        "scenario_id": scenario.get("scenario_id"),
        "scenario_title": scenario.get("title"),
        "scenario_dir": str(scenario_dir),
        "run_dir": str(run_dir),
        "netlist": str(netlist_path),
        "applied_actions": applied_actions,
        "unsupported_actions": unsupported_actions,
        "failed_actions": failed_actions,
        "spice_executed": spice_report is not None,
        "spice_report_path": str(run_dir / SPICE_RUN_NAME) if spice_report is not None else None,
        "spice_status": spice_report.get("status") if spice_report else None,
        "spice_exit_code": spice_report.get("exit_code") if spice_report else None,
        "comparison_report_path": str(scenario_dir / COMPARISON_NAME) if comparison_report is not None else None,
        "comparison_summary": comparison_report.get("summary") if comparison_report else None,
        "message": (
            "Scenario actions were applied and ngspice was executed on the scenario run."
            if spice_report is not None
            else "Scenario actions were applied to the scenario run only. ngspice was not executed."
        ),
        "created_or_updated_at": datetime.now().isoformat(timespec="seconds"),
    }

    write_json(scenario_dir / REPORT_NAME, report)
    update_status_file(scenario_dir, report)
    return report


def update_status_file(scenario_dir: Path, report: dict[str, Any]) -> None:
    """Aggiorna lo status dello scenario con lo stato dello step 12."""
    status_path = scenario_dir / STATUS_NAME
    status = read_json(status_path) if status_path.exists() else {}
    status.update(
        {
            "status": report["status"],
            "stage": "scenario_spice_executed" if report["spice_executed"] else "scenario_actions_applied",
            "message": report["message"],
            "spice_executed": report["spice_executed"],
            "spice_status": report.get("spice_status"),
            "spice_exit_code": report.get("spice_exit_code"),
            "spice_report_path": report.get("spice_report_path"),
            "comparison_report_path": report.get("comparison_report_path"),
            "comparison_summary": report.get("comparison_summary"),
            "controlled_scenario_report": str(scenario_dir / REPORT_NAME),
            "created_or_updated_at": report["created_or_updated_at"],
            "next_step": (
                "Compare base vs scenario."
                if report["spice_executed"]
                else "Run ngspice on the scenario netlist and compare base vs scenario."
            ),
        }
    )
    write_json(status_path, status)


def parse_args() -> argparse.Namespace:
    """Legge gli argomenti da terminale."""
    parser = argparse.ArgumentParser(description="Apply a controlled Pipeline 2.0 scenario.")
    parser.add_argument(
        "--scenario-dir",
        required=True,
        help="Scenario directory, for example outputs/pipeline2.0/batchA/a01/scenarios/scenario_1.",
    )
    parser.add_argument("--run-spice", action="store_true", help="Run ngspice on the scenario run after applying actions.")
    parser.add_argument("--ngspice", default=None, help="Optional ngspice executable path.")
    parser.add_argument("--timeout", type=int, default=30, help="ngspice timeout in seconds.")
    return parser.parse_args()


def main() -> None:
    """Entry point CLI."""
    args = parse_args()
    report = apply_scenario(
        Path(args.scenario_dir),
        run_spice=args.run_spice,
        ngspice_executable=args.ngspice,
        timeout_seconds=args.timeout,
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
