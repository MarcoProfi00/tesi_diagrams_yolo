"""
Scenari simulativi controllati.

Questo script applica modifiche di scenario solo dentro la cartella scenario,
senza toccare mai la base run originale della Pipeline 2.0.

Versione attuale minimale:

- legge `scenario.json`;
- lavora sulla netlist copiata in `run/07_netlist.cir`;
- supporta le azioni generali `drive_node_voltage`, `change_source_value`,
  `change_component_value` e `close_switch`;
- aggiunge o aggiorna una sorgente SPICE di scenario;
- modifica il valore di una sorgente SPICE esistente;
- modifica il valore di un componente semplice gia emesso in netlist;
- chiude uno switch riconosciuto inserendo una piccola resistenza nella netlist scenario;
- salva `12_controlled_scenarios.json`;
- aggiorna `scenario_status.json`;
- crea `scenario_comparison.json` quando esistono i dati per il confronto;
- esegue ngspice solo se richiesto con `--run-spice`.

Esempio di azione supportata:

```json
{
  "type": "drive_node_voltage",
  "target": "N002",
  "value": "5V"
}
```

Questa azione, con valore DC, diventa una riga SPICE del tipo:

```spice
VSCENARIO_N002 N002 0 DC 5
```

Se invece il valore e gia una forma sorgente SPICE, per esempio `SIN(...)` o
`PULSE(...)`, la sorgente scenario viene emessa mantenendo quella forma:

```spice
VSCENARIO_N001 N001 0 SIN(0 5 50)
```
"""

from __future__ import annotations

import argparse
import csv
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
MAX_EXECUTABLE_SCENARIOS = 5


def read_json(path: Path) -> dict[str, Any]:
    """Legge un JSON e restituisce un dizionario."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    """Scrive un JSON leggibile e stabile."""
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def count_scenarios_for_circuit(scenario_dir: Path) -> int:
    """Conta quante cartelle scenario esistono per il circuito corrente."""
    scenarios_root = scenario_dir.parent
    if not scenarios_root.exists() or not scenarios_root.is_dir():
        return 0
    return sum(1 for path in scenarios_root.iterdir() if path.is_dir())


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
    if not text or text.lower() in {"unknown", "none", "null", "n/a", "na"}:
        raise ValueError("Empty voltage value")
    return text


def normalize_spice_source_value(value: Any) -> str:
    """
    Normalizza il nuovo valore di una sorgente SPICE.

    Per valori scalari come `10V` o `2.5` produce una definizione `DC`.
    Per forme gia SPICE-like come `SIN(...)`, `PULSE(...)` o `DC 10` conserva
    la forma dichiarata dallo scenario.
    """
    text = str(value).strip()
    if not text or text.lower() in {"unknown", "none", "null", "n/a", "na"}:
        raise ValueError("Source value must be concrete, not unknown")

    compact = re.sub(r"\s+", " ", text)
    if re.match(r"(?i)^dc\s+", compact):
        dc_value = normalize_spice_dc_value(compact.split(maxsplit=1)[1])
        return f"DC {dc_value}"
    if re.match(r"(?i)^(sin|pulse|pwl|exp|sffm|am)\s*\(", compact):
        return compact

    return f"DC {normalize_spice_dc_value(compact)}"


def normalize_spice_resistance_value(value: Any) -> str:
    """
    Normalizza una resistenza semplice per SPICE.

    Per `close_switch` usiamo di default `1m`, cioe 1 milliohm. Questo modella
    uno switch chiuso senza introdurre un corto ideale troppo aggressivo.
    """
    text = str(value).strip() if value is not None else "1m"
    text = re.sub(r"\s+", "", text)
    text = re.sub(r"(?i)ohms?$", "", text)
    if not text or text.lower() in {"unknown", "none", "null", "n/a", "na"}:
        raise ValueError("Switch resistance must be concrete, not unknown")
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
    """
    Applica l'azione `drive_node_voltage` alla netlist scenario.

    La stessa azione deve supportare sia valori DC semplici (`5V`, `DC 3.3`)
    sia forme sorgente SPICE (`SIN(...)`, `PULSE(...)`), senza forzarle sempre
    dentro una definizione `DC ...`.
    """
    node_map = read_json(run_dir / "03_node_map.json")
    target_node = validate_node_target(action.get("target"), node_map)
    source_definition = normalize_spice_source_value(action.get("value"))

    source_name = f"VSCENARIO_{sanitize_spice_name(target_node)}"
    source_line = f"{source_name} {target_node} 0 {source_definition}"
    updated_netlist, operation = insert_or_replace_source(netlist_text, source_name, source_line)

    result = {
        "status": "applied",
        "type": "drive_node_voltage",
        "target": target_node,
        "value": action.get("value"),
        "normalized_source_definition": source_definition,
        "normalized_dc_value": source_definition[3:] if source_definition.upper().startswith("DC ") else None,
        "inserted_line": source_line,
        "operation": operation,
        "spice_executed": False,
    }
    return updated_netlist, result


def normalize_source_target(target: Any) -> str:
    """Normalizza il nome sorgente richiesto dallo scenario."""
    source_name = str(target).strip()
    if not source_name:
        raise ValueError("Missing target source")
    source_name = re.sub(r"(?i)#branch$", "", source_name)
    return source_name


def source_target_candidates(target: Any) -> list[str]:
    """
    Crea possibili nomi sorgente a partire dal target dello scenario.

    L'agente puo indicare sia il nome SPICE (`Vbattery2_1`) sia l'id componente
    (`battery2.1`). Per rendere lo scenario piu robusto proviamo entrambe le
    forme, senza inventare sorgenti nuove.
    """
    source_name = normalize_source_target(target)
    candidates = [source_name]

    if "." in source_name and not re.match(r"(?i)^[vi]", source_name):
        candidates.append(f"V{sanitize_spice_name(source_name)}")

    sanitized = sanitize_spice_name(source_name)
    if sanitized != source_name:
        candidates.append(sanitized)
        if not re.match(r"(?i)^[vi]", sanitized):
            candidates.append(f"V{sanitized}")

    unique_candidates: list[str] = []
    for candidate in candidates:
        if candidate and candidate not in unique_candidates:
            unique_candidates.append(candidate)
    return unique_candidates


def component_target_candidates(target: Any) -> list[str]:
    """
    Crea possibili nomi componente a partire dal target dello scenario.

    L'agente puo indicare sia il nome SPICE emesso (`Rresistor22_4`) sia l'id
    componente originario (`resistor22.4`). Proviamo poche varianti semplici,
    senza inventare nuovi componenti.
    """
    component_name = str(target).strip()
    if not component_name:
        raise ValueError("Missing target component")

    sanitized = sanitize_spice_name(component_name)
    candidates = [component_name]

    if sanitized != component_name:
        candidates.append(sanitized)

    lower_target = component_name.lower()
    lower_sanitized = sanitized.lower()
    prefixed_candidates: list[str] = []

    if ("resistor" in lower_target or "resistor" in lower_sanitized) and not lower_sanitized.startswith("rresistor"):
        prefixed_candidates.append(f"R{sanitized}")
    if ("capacitor" in lower_target or "capacitor" in lower_sanitized) and not lower_sanitized.startswith("ccapacitor"):
        prefixed_candidates.append(f"C{sanitized}")
    if ("inductor" in lower_target or "inductor" in lower_sanitized) and not lower_sanitized.startswith("linductor"):
        prefixed_candidates.append(f"L{sanitized}")

    for candidate in prefixed_candidates:
        if candidate not in candidates:
            candidates.append(candidate)

    return candidates


def replace_source_value(
    netlist_text: str,
    source_names: list[str],
    source_definition: str,
) -> tuple[str, dict[str, Any]]:
    """
    Sostituisce il valore di una sorgente gia presente nella netlist.

    La sostituzione e volutamente semplice: preserva nome sorgente e due nodi,
    poi rimpiazza la definizione elettrica rimanente con il nuovo valore.
    """
    lines = netlist_text.splitlines()

    for source_name in source_names:
        source_pattern = re.compile(rf"^\s*{re.escape(source_name)}\s+", flags=re.IGNORECASE)

        for index, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or stripped.startswith(("*", ".")):
                continue
            if not source_pattern.match(line):
                continue

            parts = stripped.split(maxsplit=3)
            if len(parts) < 4:
                raise ValueError(f"Source {source_name} does not have a replaceable value")

            old_line = line
            new_line = f"{parts[0]} {parts[1]} {parts[2]} {source_definition}"
            lines[index] = new_line
            return "\n".join(lines) + "\n", {
                "source_name": parts[0],
                "old_line": old_line,
                "new_line": new_line,
                "operation": "updated",
            }

    raise ValueError(f"Source not found in 07_netlist.cir. Tried: {', '.join(source_names)}")


def apply_change_source_value(
    action: dict[str, Any],
    netlist_text: str,
) -> tuple[str, dict[str, Any]]:
    """Applica l'azione `change_source_value` a una sorgente SPICE esistente."""
    source_names = source_target_candidates(action.get("target"))
    source_definition = normalize_spice_source_value(action.get("value"))
    updated_netlist, operation = replace_source_value(netlist_text, source_names, source_definition)

    result = {
        "status": "applied",
        "type": "change_source_value",
        "target": action.get("target"),
        "resolved_source_name": operation["source_name"],
        "tried_source_names": source_names,
        "value": action.get("value"),
        "normalized_source_definition": source_definition,
        "old_line": operation["old_line"],
        "new_line": operation["new_line"],
        "operation": operation["operation"],
        "spice_executed": False,
    }
    return updated_netlist, result


def normalize_component_value(value: Any) -> str:
    """
    Normalizza un valore semplice per componenti R, C e L.

    Questa versione minimale accetta il testo quasi cosi come arriva, togliendo
    solo spazi superflui. In questo modo supportiamo suffissi SPICE come `k`,
    `u`, `m`, `meg` senza reinterpretarli a mano.
    """
    text = str(value).strip()
    text = re.sub(r"\s+", "", text)
    if not text or text.lower() in {"unknown", "none", "null", "n/a", "na"}:
        raise ValueError("Component value must be concrete, not unknown")
    return text


def replace_component_value(
    netlist_text: str,
    component_names: list[str],
    new_value: str,
) -> tuple[str, dict[str, Any]]:
    """
    Sostituisce il valore di un componente semplice gia presente nella netlist.

    Per ora supportiamo solo righe SPICE standard di resistori, condensatori e
    induttanze: nome, nodo1, nodo2, valore, eventuali parametri aggiuntivi.
    """
    lines = netlist_text.splitlines()

    for component_name in component_names:
        component_pattern = re.compile(rf"^\s*{re.escape(component_name)}\s+", flags=re.IGNORECASE)

        for index, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or stripped.startswith(("*", ".")):
                continue
            if not component_pattern.match(line):
                continue

            parts = stripped.split()
            if len(parts) < 4:
                raise ValueError(f"Component {component_name} does not have a replaceable value")

            prefix = parts[0][:1].upper()
            if prefix not in {"R", "C", "L"}:
                raise ValueError(
                    f"Component {parts[0]} is not supported by change_component_value. "
                    "Supported prefixes: R, C, L."
                )

            old_line = line
            old_value = parts[3]
            parts[3] = new_value
            new_line = " ".join(parts)
            lines[index] = new_line
            return "\n".join(lines) + "\n", {
                "component_name": parts[0],
                "old_line": old_line,
                "new_line": new_line,
                "old_value": old_value,
                "new_value": new_value,
                "operation": "updated",
            }

    raise ValueError(f"Component not found in 07_netlist.cir. Tried: {', '.join(component_names)}")


def apply_change_component_value(
    action: dict[str, Any],
    netlist_text: str,
) -> tuple[str, dict[str, Any]]:
    """Applica `change_component_value` a un componente semplice gia emesso."""
    component_names = component_target_candidates(action.get("target"))
    new_value = normalize_component_value(action.get("value"))
    updated_netlist, operation = replace_component_value(netlist_text, component_names, new_value)

    result = {
        "status": "applied",
        "type": "change_component_value",
        "target": action.get("target"),
        "resolved_component_name": operation["component_name"],
        "tried_component_names": component_names,
        "value": action.get("value"),
        "normalized_component_value": new_value,
        "old_value": operation["old_value"],
        "new_value": operation["new_value"],
        "old_line": operation["old_line"],
        "new_line": operation["new_line"],
        "operation": operation["operation"],
        "spice_executed": False,
    }
    return updated_netlist, result


def find_switch_rule(component_id: Any, run_dir: Path) -> tuple[str, dict[str, Any]]:
    """Recupera uno switch gia riconosciuto dalle regole componenti dello scenario."""
    target = str(component_id).strip()
    if not target:
        raise ValueError("Missing target switch")

    rules = read_json(run_dir / "06_component_rules.json")
    components = rules.get("components") or {}
    component = components.get(target)
    if not isinstance(component, dict):
        raise ValueError(f"Switch {target} not found in 06_component_rules.json")

    class_name = str(component.get("class_name") or "").lower()
    if class_name != "switch":
        raise ValueError(f"Target {target} is not a Switch component")

    nodes = component.get("nodes") or []
    if len(nodes) != 2:
        raise ValueError(f"Switch {target} must have exactly two SPICE nodes")

    return target, component


def apply_close_switch(
    action: dict[str, Any],
    run_dir: Path,
    netlist_text: str,
) -> tuple[str, dict[str, Any]]:
    """Applica `close_switch` inserendo una piccola resistenza tra i nodi dello switch."""
    switch_id, component = find_switch_rule(action.get("target"), run_dir)
    node_a, node_b = [str(node).strip() for node in component.get("nodes", [])]
    if not node_a or not node_b:
        raise ValueError(f"Switch {switch_id} has empty nodes")

    resistance = normalize_spice_resistance_value(action.get("resistance"))
    resistor_name = f"RSCENARIO_{sanitize_spice_name(switch_id)}"
    resistor_line = f"{resistor_name} {node_a} {node_b} {resistance}"
    updated_netlist, operation = insert_or_replace_source(netlist_text, resistor_name, resistor_line)
    updated_netlist = annotate_closed_switch_netlist(updated_netlist, switch_id, resistor_line)

    result = {
        "status": "applied",
        "type": "close_switch",
        "target": switch_id,
        "nodes": [node_a, node_b],
        "resistance": resistance,
        "inserted_line": resistor_line,
        "operation": operation,
        "spice_executed": False,
    }
    return updated_netlist, result


def annotate_closed_switch_netlist(netlist_text: str, switch_id: str, resistor_line: str) -> str:
    """
    Rende leggibile nella netlist scenario che uno switch open della base e stato chiuso.

    La netlist scenario parte dalla netlist base copiata, quindi puo contenere un
    commento tipo `* switch25.1 open: not emitted`. Quando applichiamo
    `close_switch`, quel commento resta storicamente vero per la base run ma e
    ambiguo nella run scenario. Lo trasformiamo in una nota esplicita.
    """
    lines = netlist_text.splitlines()
    base_note = f"* {switch_id} open in base run; closed by scenario close_switch"
    scenario_note = f"* scenario close_switch: {switch_id} modeled as {resistor_line}"
    open_comment_pattern = re.compile(
        rf"^\s*\*\s*{re.escape(switch_id)}\s+open:\s+not emitted\b.*$",
        flags=re.IGNORECASE,
    )

    for index, line in enumerate(lines):
        if open_comment_pattern.match(line):
            lines[index] = base_note
            break

    if scenario_note not in lines:
        for index, line in enumerate(lines):
            if line.strip().lower() == resistor_line.lower():
                lines.insert(index, scenario_note)
                break

    return "\n".join(lines) + "\n"


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
    if re.search(r"(?i)#branch$", text) and "(" not in text:
        return f"i({text})"
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
            # ngspice spesso lascia una riga vuota tra l'intestazione e i dati
            # delle tabelle, quindi non chiudiamo la sezione su una riga vuota.
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

        if parts[0].lower() == "device":
            current_devices = parts[1:]
            in_node_table = False
            in_source_table = False
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


def count_ngspice_stderr_warnings(stderr_path: Path) -> float | None:
    """
    Conta i warning nello stderr ngspice.

    Serve per scenari che vogliono verificare se una modifica riduce problemi
    numerici, per esempio `singular matrix`. Restituiamo un numero per riusare
    lo stesso confronto base/scenario gia usato per tensioni e correnti.
    """
    if not stderr_path.exists():
        return None

    lines = stderr_path.read_text(encoding="utf-8", errors="replace").splitlines()
    warning_count = 0
    for line in lines:
        if line.strip().lower().startswith("warning:"):
            warning_count += 1
    return float(warning_count)


def is_voltage_quantity(quantity: str) -> bool:
    """Riconosce una grandezza di tensione del tipo `v(N001)`."""
    return bool(re.match(r"(?i)^v\([^)]+\)$", quantity.strip()))


def is_stderr_quantity(quantity: str) -> bool:
    """Riconosce richieste di confronto sui warning stderr."""
    return quantity.strip().lower() in {"stderr", "ngspice_stderr", "stderr_warnings", "warning_count"}


def parse_tran_csv_metrics(csv_path: Path) -> dict[str, dict[str, float]]:
    """
    Estrae metriche semplici dal CSV transitorio pulito.

    Per ogni colonna tensione calcoliamo:
    - min
    - max
    - mean
    - vpp

    Questa prima versione resta volutamente semplice: per gli scenari `.tran`
    usiamo `vpp` come metrica principale da confrontare.
    """
    if not csv_path.exists():
        return {}

    try:
        with csv_path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
    except (OSError, csv.Error):
        return {}

    if not rows:
        return {}

    values_by_column: dict[str, list[float]] = {}
    for row in rows:
        for column_name, value_text in row.items():
            if column_name is None:
                continue
            column_key = column_name.strip().lower()
            if not column_key or column_key == "time":
                continue
            value = parse_float(str(value_text).strip())
            if value is None:
                continue
            values_by_column.setdefault(column_key, []).append(value)

    metrics: dict[str, dict[str, float]] = {}
    for column_key, values in values_by_column.items():
        if not values:
            continue
        minimum = min(values)
        maximum = max(values)
        mean = sum(values) / len(values)
        metrics[column_key] = {
            "min": minimum,
            "max": maximum,
            "mean": mean,
            "vpp": maximum - minimum,
        }

    return metrics


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


def evaluate_diagnostic_outcome(
    summary: dict[str, int],
    analysis: str = "op",
    quantities: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Valuta in modo prudente se uno scenario sembra risolvere il problema.

    Questa non e una diagnosi semantica definitiva: e un criterio automatico
    semplice basato sui confronti SPICE richiesti dallo scenario. Serve per
    capire se l'automazione puo fermarsi o se conviene provare un altro scenario.
    """
    requested = int(summary.get("requested_count") or 0)
    changed = int(summary.get("changed_count") or 0)
    activated = int(summary.get("activated_count") or 0)
    missing = int(summary.get("missing_count") or 0)

    if requested == 0:
        status = "unknown"
        label = "Outcome unknown"
        reason = "The scenario did not define quantities to compare."
        stop_automation = False
    elif missing == requested:
        status = "unknown"
        label = "Outcome unknown"
        reason = "None of the requested comparison quantities were found in the SPICE outputs."
        stop_automation = False
    elif changed == 0:
        status = "not_resolved"
        label = "Not resolved"
        reason = "The requested quantities did not change compared with the base run."
        stop_automation = False
    elif missing > 0:
        status = "partially_resolved"
        label = "Partially resolved"
        reason = "Some requested quantities changed, but at least one comparison quantity is missing."
        stop_automation = False
    elif analysis == "tran" and changed == requested:
        status = "partially_resolved"
        label = "Partially resolved"
        reason = (
            "The transient waveforms changed in all requested quantities, which supports "
            "the hypothesis, but waveform changes alone are not enough to mark the problem as resolved automatically."
        )
        stop_automation = False
    elif changed == requested and activated > 0:
        status = "resolved_candidate"
        label = "Candidate resolved"
        reason = "All requested quantities changed and at least one inactive quantity became active."
        stop_automation = True
    else:
        status = "partially_resolved"
        label = "Partially resolved"
        reason = "The scenario changed the circuit response, but the evidence is not strong enough to stop automatically."
        stop_automation = False

    return {
        "status": status,
        "label": label,
        "reason": reason,
        "stop_automation": stop_automation,
        "confidence": "medium" if status == "resolved_candidate" else "low",
        "next_step": (
            "Stop automatic scenario execution and ask the agent to explain the confirmed hypothesis."
            if stop_automation
            else "Continue with another scenario or ask the agent for a refined hypothesis."
        ),
    }


def build_scenario_comparison(scenario_dir: Path, scenario: dict[str, Any]) -> dict[str, Any]:
    """Confronta le grandezze richieste tra base run e scenario run."""
    status = read_json(scenario_dir / STATUS_NAME) if (scenario_dir / STATUS_NAME).exists() else {}
    base_output_dir = Path(status.get("base_output_dir") or scenario_dir.parent.parent)
    run_dir = scenario_dir / "run"
    analysis = str(scenario.get("analysis") or "op").strip().lower()

    base_values = parse_ngspice_stdout(base_output_dir / "08_ngspice_stdout.txt")
    scenario_values = parse_ngspice_stdout(run_dir / "08_ngspice_stdout.txt")
    base_tran_metrics = parse_tran_csv_metrics(base_output_dir / "08_tran.csv")
    scenario_tran_metrics = parse_tran_csv_metrics(run_dir / "08_tran.csv")
    base_stderr_warning_count = count_ngspice_stderr_warnings(base_output_dir / "08_ngspice_stderr.txt")
    scenario_stderr_warning_count = count_ngspice_stderr_warnings(run_dir / "08_ngspice_stderr.txt")

    requested = scenario.get("compare") or []
    if not isinstance(requested, list):
        requested = []

    quantities: list[dict[str, Any]] = []
    activated = 0
    changed = 0
    missing = 0

    for item in requested:
        quantity = normalize_quantity_name(str(item))
        if is_stderr_quantity(quantity):
            lookup_key = "stderr.warning_count"
            base_value = base_stderr_warning_count
            scenario_value = scenario_stderr_warning_count
            base_details: dict[str, Any] = {}
            scenario_details: dict[str, Any] = {}
        elif analysis == "tran" and is_voltage_quantity(quantity):
            lookup_key = quantity_lookup_key(quantity)
            base_metric_set = base_tran_metrics.get(lookup_key) or {}
            scenario_metric_set = scenario_tran_metrics.get(lookup_key) or {}
            base_value = base_metric_set.get("vpp")
            scenario_value = scenario_metric_set.get("vpp")
            lookup_key = f"{lookup_key}.vpp"
            base_details = base_metric_set
            scenario_details = scenario_metric_set
        else:
            lookup_key = quantity_lookup_key(quantity)
            base_value = base_values.get(lookup_key)
            scenario_value = scenario_values.get(lookup_key)
            base_details = {}
            scenario_details = {}
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
                "metric": lookup_key,
                "base_details": base_details,
                "scenario_details": scenario_details,
            }
        )

    summary = {
        "requested_count": len(quantities),
        "changed_count": changed,
        "activated_count": activated,
        "missing_count": missing,
    }
    diagnostic_outcome = evaluate_diagnostic_outcome(summary, analysis=analysis, quantities=quantities)

    comparison = {
        "source_format": "pipeline2.0_scenario_comparison",
        "scenario_id": scenario.get("scenario_id"),
        "scenario_title": scenario.get("title"),
        "base_output_dir": str(base_output_dir),
        "scenario_run_dir": str(run_dir),
        "base_stdout": str(base_output_dir / "08_ngspice_stdout.txt"),
        "scenario_stdout": str(run_dir / "08_ngspice_stdout.txt"),
        "base_stderr": str(base_output_dir / "08_ngspice_stderr.txt"),
        "scenario_stderr": str(run_dir / "08_ngspice_stderr.txt"),
        "quantities": quantities,
        "summary": summary,
        "diagnostic_outcome": diagnostic_outcome,
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
            elif action_type == "change_source_value":
                netlist_text, result = apply_change_source_value(action, netlist_text)
                result["index"] = index
                applied_actions.append(result)
            elif action_type == "change_component_value":
                netlist_text, result = apply_change_component_value(action, netlist_text)
                result["index"] = index
                applied_actions.append(result)
            elif action_type == "close_switch":
                netlist_text, result = apply_close_switch(action, run_dir, netlist_text)
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

    status = "applied_not_run" if applied_actions and not failed_actions and not unsupported_actions else "not_applied"
    if failed_actions or unsupported_actions:
        status = "partial_or_failed" if applied_actions else "failed"

    spice_report: dict[str, Any] | None = None
    comparison_report: dict[str, Any] | None = None
    if run_spice and applied_actions and not failed_actions and not unsupported_actions:
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
        "diagnostic_outcome": comparison_report.get("diagnostic_outcome") if comparison_report else None,
        "message": build_report_message(applied_actions, failed_actions, unsupported_actions, spice_report),
        "created_or_updated_at": datetime.now().isoformat(timespec="seconds"),
    }

    write_json(scenario_dir / REPORT_NAME, report)
    update_status_file(scenario_dir, report)
    return report


def build_report_message(
    applied_actions: list[dict[str, Any]],
    failed_actions: list[dict[str, Any]],
    unsupported_actions: list[dict[str, Any]],
    spice_report: dict[str, Any] | None,
) -> str:
    """Costruisce un messaggio sintetico coerente con l'esito dello scenario."""
    if spice_report is not None:
        return "Scenario actions were applied and ngspice was executed on the scenario run."
    if failed_actions or unsupported_actions:
        return "Scenario execution stopped because at least one action failed or is not supported."
    if applied_actions:
        return "Scenario actions were applied to the scenario run only. ngspice was not executed."
    return "No scenario action was applied."


def update_status_file(scenario_dir: Path, report: dict[str, Any]) -> None:
    """Aggiorna lo status dello scenario con lo stato dello step 12."""
    status_path = scenario_dir / STATUS_NAME
    status = read_json(status_path) if status_path.exists() else {}
    diagnostic_outcome = report.get("diagnostic_outcome")
    if not isinstance(diagnostic_outcome, dict):
        diagnostic_outcome = {}
    executed_scenarios_count = count_scenarios_for_circuit(scenario_dir)
    budget_exhausted = executed_scenarios_count >= MAX_EXECUTABLE_SCENARIOS
    next_step = diagnostic_outcome.get("next_step")
    if not next_step:
        next_step = (
            "Compare base vs scenario."
            if report["spice_executed"]
            else "Run ngspice on the scenario netlist and compare base vs scenario."
        )
    if budget_exhausted:
        next_step = "Scenario budget exhausted. Ask the agent for a final diagnostic conclusion."
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
            "diagnostic_outcome": report.get("diagnostic_outcome"),
            "controlled_scenario_report": str(scenario_dir / REPORT_NAME),
            "created_or_updated_at": report["created_or_updated_at"],
            "executed_scenarios_count": executed_scenarios_count,
            "scenario_budget_exhausted": budget_exhausted,
            "next_step": next_step,
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
