"""
Scenari simulativi controllati.

Questo script applica modifiche di scenario solo dentro la cartella scenario,
senza toccare mai la base run originale della Pipeline 2.0.

Comportamento attuale:

- legge `scenario.json`;
- lavora sulla netlist copiata in `run/07_netlist.cir`;
- supporta le azioni generali `drive_node_voltage`, `set_initial_node_voltage`,
  `add_voltage_source_between_nodes`, `connect_nodes`,
  `add_resistor_between_nodes`,
  `feed_nodes_from_source_node`, `change_source_value`,
  `change_component_value` e `close_switch`;
- aggiunge o aggiorna una sorgente SPICE di scenario;
- modifica il valore di una sorgente SPICE esistente;
- modifica il valore di un componente semplice gia emesso in netlist;
- chiude uno switch riconosciuto inserendo una piccola resistenza nella netlist scenario;
- salva `12_controlled_scenarios.json`;
- aggiorna `scenario_status.json`;
- crea `scenario_comparison.json` quando esistono i dati per il confronto;
- verifica gli eventuali criteri espliciti dichiarati in `expect`;
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
from datetime import datetime
import importlib.util
import json
import re
from pathlib import Path
from typing import Any

from controlled_scenarios.measurements import (
    classify_change,
    count_ngspice_stderr_warnings,
    is_internal_device_current_quantity,
    is_stderr_quantity,
    is_voltage_quantity,
    normalize_quantity_name,
    parse_float,
    parse_ngspice_stdout,
    parse_tran_csv_metrics,
    quantity_lookup_key,
    voltage_quantity_nodes,
)
from controlled_scenarios.outcome import evaluate_diagnostic_outcome
from scenario_expectations import (
    COMPARISON_TOLERANCE,
    MIN_MEANINGFUL_RELATIVE_CHANGE,
    expectation_is_meaningful_improvement,
    expectation_matches,
    relative_change_ratio,
)
from transient_signal_quality import analyze_sine_quality, compare_sine_quality


NETLIST_NAME = "07_netlist.cir"
SCENARIO_NAME = "scenario.json"
STATUS_NAME = "scenario_status.json"
REPORT_NAME = "12_controlled_scenarios.json"
COMPARISON_NAME = "scenario_comparison.json"
SPICE_RUN_NAME = "08_spice_run.json"
STEP08_PATH = Path(__file__).resolve().parent / "08_spice_run.py"
MAX_EXECUTABLE_SCENARIOS = 5
# I collegamenti sotto questa soglia sono trattati come vincoli quasi ideali.
# Il limite serve soltanto al controllo preventivo dei generatori in conflitto:
# non modifica in alcun modo i valori elettrici emessi nella netlist.
MAX_NEAR_IDEAL_RESISTANCE_OHMS = 0.1


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
    """Conta le run scenario per cui SPICE e stato realmente avviato."""
    scenarios_root = scenario_dir.parent
    if not scenarios_root.exists() or not scenarios_root.is_dir():
        return 0

    executed = 0
    for path in scenarios_root.iterdir():
        if not path.is_dir():
            continue
        report_path = path / REPORT_NAME
        status_path = path / STATUS_NAME
        report = read_json(report_path) if report_path.exists() else {}
        status = read_json(status_path) if status_path.exists() else {}
        if report.get("spice_executed") or status.get("spice_executed"):
            executed += 1
    return executed


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


def validate_existing_node(node: Any, node_map: dict[str, Any], *, field_name: str) -> str:
    """
    Controlla che un nodo esista nella mappa nodi della run scenario.

    A differenza di `validate_node_target`, questa validazione e generica e non
    assume che il nodo debba essere pilotabile come sorgente: quindi accetta
    anche `0` se presente nella mappa nodi.
    """
    node_id = str(node).strip()
    if not node_id:
        raise ValueError(f"Missing {field_name} node")

    known_nodes = {str(item.get("node_id")) for item in node_map.get("nodes", []) if isinstance(item, dict)}
    if known_nodes and node_id not in known_nodes:
        raise ValueError(f"Node {node_id} from field {field_name} not found in 03_node_map.json")

    return node_id


def insert_or_replace_netlist_element(netlist_text: str, element_name: str, element_line: str) -> tuple[str, str]:
    """
    Inserisce o aggiorna un elemento di scenario nella netlist.

    La riga viene messa prima della prima direttiva SPICE principale, cosi resta
    nella parte dichiarativa della netlist.
    """
    lines = netlist_text.splitlines()
    element_pattern = re.compile(rf"^\s*{re.escape(element_name)}\s+", flags=re.IGNORECASE)

    for index, line in enumerate(lines):
        if element_pattern.match(line):
            lines[index] = element_line
            return "\n".join(lines) + "\n", "updated"

    insert_at = len(lines)
    for index, line in enumerate(lines):
        stripped = line.strip().lower()
        if stripped in {".op", ".end"} or stripped.startswith((".tran", ".ac", ".dc", ".control")):
            insert_at = index
            break

    lines.insert(insert_at, element_line)
    return "\n".join(lines) + "\n", "inserted"


def insert_or_replace_initial_node_voltage(netlist_text: str, node: str, voltage: str) -> tuple[str, str, str]:
    """
    Inserisce oppure aggiorna una condizione iniziale generata dalla pipeline.

    Le condizioni sono mantenute in una sola direttiva ``.ic`` identificata da
    un commento dedicato. In questo modo piu azioni possono inizializzare nodi
    diversi senza modificare eventuali direttive ``.ic`` gia presenti nella
    netlist originale. La scelta di saltare o meno il punto operativo resta
    separata, perche riguarda l'intera analisi transitoria e non il singolo nodo.
    """
    marker = "* pipeline2 scenario initial conditions"
    lines = netlist_text.splitlines()
    marker_index = next(
        (index for index, line in enumerate(lines) if line.strip().lower() == marker),
        None,
    )
    assignment = f"V({node})={voltage}"

    if marker_index is not None and marker_index + 1 < len(lines):
        directive_index = marker_index + 1
        directive = lines[directive_index].strip()
        if directive.lower().startswith(".ic "):
            assignments = directive[3:].strip().split()
            target_pattern = re.compile(rf"^v\(\s*{re.escape(node)}\s*\)=", flags=re.IGNORECASE)
            replaced = False
            for index, existing in enumerate(assignments):
                if target_pattern.match(existing):
                    assignments[index] = assignment
                    replaced = True
                    break
            if not replaced:
                assignments.append(assignment)
            lines[directive_index] = ".ic " + " ".join(assignments)
            return "\n".join(lines) + "\n", "updated", lines[directive_index]

    insert_at = len(lines)
    for index, line in enumerate(lines):
        stripped = line.strip().lower()
        if stripped in {".op", ".end"} or stripped.startswith((".tran", ".ac", ".dc", ".control")):
            insert_at = index
            break

    directive = f".ic {assignment}"
    lines[insert_at:insert_at] = [marker, directive]
    return "\n".join(lines) + "\n", "inserted", directive


def enable_transient_initial_conditions(netlist_text: str) -> tuple[str, str]:
    """
    Aggiunge ``UIC`` alla direttiva ``.tran`` esistente.

    Questa modalita rappresenta un avvio da condizioni iniziali, utile quando
    il punto operativo DC mantiene artificialmente simmetrico un circuito
    dinamico. Non cambia topologia o valori e non crea sorgenti permanenti.
    """
    lines = netlist_text.splitlines()
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.lower().startswith(".tran"):
            continue
        tokens = stripped.split()
        if any(token.lower() == "uic" for token in tokens[1:]):
            return "\n".join(lines) + "\n", "unchanged"
        lines[index] = f"{line.rstrip()} UIC"
        return "\n".join(lines) + "\n", "enabled"
    raise ValueError("skip_operating_point richiede una direttiva .tran nella netlist")


def parse_spice_scalar(value: str) -> float | None:
    """Converte un valore SPICE scalare usando i suffissi ingegneristici comuni."""
    match = re.fullmatch(
        r"([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?)\s*(meg|[tgkmunpf]?)",
        str(value or "").strip(),
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    multipliers = {
        "": 1.0,
        "t": 1e12,
        "g": 1e9,
        "meg": 1e6,
        "k": 1e3,
        "m": 1e-3,
        "u": 1e-6,
        "n": 1e-9,
        "p": 1e-12,
        "f": 1e-15,
    }
    return float(match.group(1)) * multipliers[match.group(2).lower()]


def voltage_constraint_adjacency(netlist_text: str) -> dict[str, set[str]]:
    """
    Costruisce il grafo dei vincoli di tensione gia presenti nella netlist.

    Sono inclusi i generatori ideali di tensione e le resistenze quasi ideali.
    Componenti ordinari, condensatori, induttori e rami ad alta impedenza non
    vengono assimilati a un vincolo, cosi il controllo resta conservativo.
    """
    adjacency: dict[str, set[str]] = {}

    def add_edge(node_a: str, node_b: str) -> None:
        adjacency.setdefault(node_a.upper(), set()).add(node_b.upper())
        adjacency.setdefault(node_b.upper(), set()).add(node_a.upper())

    for raw_line in netlist_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("*", ".")):
            continue
        parts = line.split()
        if len(parts) < 3:
            continue
        element_name = parts[0]
        if element_name[0].upper() == "V":
            add_edge(parts[1], parts[2])
            continue
        if element_name[0].upper() != "R" or len(parts) < 4:
            continue
        resistance = parse_spice_scalar(parts[3])
        if resistance is not None and abs(resistance) <= MAX_NEAR_IDEAL_RESISTANCE_OHMS:
            add_edge(parts[1], parts[2])
    return adjacency


def nodes_are_voltage_constrained(netlist_text: str, node_a: str, node_b: str) -> bool:
    """Verifica se due nodi sono gia legati da generatori o rami quasi ideali."""
    start = str(node_a).strip().upper()
    target = str(node_b).strip().upper()
    if start == target:
        return True
    adjacency = voltage_constraint_adjacency(netlist_text)
    pending = [start]
    visited: set[str] = set()
    while pending:
        current = pending.pop()
        if current in visited:
            continue
        visited.add(current)
        for neighbour in adjacency.get(current, set()):
            if neighbour == target:
                return True
            if neighbour not in visited:
                pending.append(neighbour)
    return False


def validate_new_voltage_source_path(netlist_text: str, positive: str, negative: str) -> None:
    """Rifiuta un nuovo generatore che chiuderebbe un conflitto quasi ideale."""
    if nodes_are_voltage_constrained(netlist_text, positive, negative):
        raise ValueError(
            "Generatore di scenario in conflitto: i nodi "
            f"{positive} e {negative} sono gia vincolati da una sorgente o da "
            "un percorso a bassissima impedenza"
        )


def apply_set_initial_node_voltage(
    action: dict[str, Any],
    run_dir: Path,
    netlist_text: str,
) -> tuple[str, dict[str, Any]]:
    """
    Imposta la tensione iniziale di un nodo per una simulazione transitoria.

    L'azione emette ``.ic V(nodo)=valore`` nella netlist dello scenario. Con
    ``skip_operating_point=true`` abilita anche ``UIC`` sulla ``.tran`` per
    simulare un vero avvio dalle condizioni iniziali. In entrambi i casi non
    altera la topologia e non crea una sorgente permanente.
    """
    node_map = read_json(run_dir / "03_node_map.json")
    target_node = validate_node_target(action.get("target"), node_map)
    voltage = normalize_spice_dc_value(action.get("value"))
    updated_netlist, operation, directive = insert_or_replace_initial_node_voltage(
        netlist_text,
        target_node,
        voltage,
    )
    skip_operating_point = action.get("skip_operating_point", False)
    if not isinstance(skip_operating_point, bool):
        raise ValueError("skip_operating_point deve essere booleano")
    transient_startup_operation = "not_requested"
    if skip_operating_point:
        updated_netlist, transient_startup_operation = enable_transient_initial_conditions(
            updated_netlist
        )

    result = {
        "status": "applied",
        "type": "set_initial_node_voltage",
        "target": target_node,
        "value": action.get("value"),
        "normalized_dc_value": voltage,
        "inserted_line": directive,
        "operation": operation,
        "skip_operating_point": skip_operating_point,
        "transient_startup_operation": transient_startup_operation,
        "spice_executed": False,
    }
    return updated_netlist, result


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
    validate_new_voltage_source_path(netlist_text, target_node, "0")

    source_name = f"VSCENARIO_{sanitize_spice_name(target_node)}"
    source_line = f"{source_name} {target_node} 0 {source_definition}"
    updated_netlist, operation = insert_or_replace_netlist_element(netlist_text, source_name, source_line)

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


def apply_add_voltage_source_between_nodes(
    action: dict[str, Any],
    run_dir: Path,
    netlist_text: str,
) -> tuple[str, dict[str, Any]]:
    """
    Applica `add_voltage_source_between_nodes` tra due nodi gia esistenti.

    Questa primitiva rappresenta una eccitazione esterna realistica del
    circuito: aggiunge una nuova sorgente tra due nodi di interfaccia gia
    presenti nella node map, invece di forzare direttamente un singolo nodo
    interno rispetto a massa come fa `drive_node_voltage`.
    """
    node_map = read_json(run_dir / "03_node_map.json")
    positive_node = validate_existing_node(
        action.get("positive", action.get("positive_node")),
        node_map,
        field_name="positive",
    )
    negative_node = validate_existing_node(
        action.get("negative", action.get("negative_node")),
        node_map,
        field_name="negative",
    )
    if positive_node == negative_node:
        raise ValueError("add_voltage_source_between_nodes requires two different nodes")

    source_definition = normalize_spice_source_value(action.get("value"))
    validate_new_voltage_source_path(netlist_text, positive_node, negative_node)
    source_name = (
        f"VSCENARIO_SUPPLY_{sanitize_spice_name(positive_node)}_"
        f"{sanitize_spice_name(negative_node)}"
    )
    source_line = f"{source_name} {positive_node} {negative_node} {source_definition}"
    updated_netlist, operation = insert_or_replace_netlist_element(netlist_text, source_name, source_line)

    result = {
        "status": "applied",
        "type": "add_voltage_source_between_nodes",
        "positive": positive_node,
        "negative": negative_node,
        "nodes": [positive_node, negative_node],
        "value": action.get("value"),
        "normalized_source_definition": source_definition,
        "normalized_dc_value": source_definition[3:] if source_definition.upper().startswith("DC ") else None,
        "inserted_line": source_line,
        "operation": operation,
        "spice_executed": False,
    }
    return updated_netlist, result


def apply_connect_nodes(
    action: dict[str, Any],
    run_dir: Path,
    netlist_text: str,
) -> tuple[str, dict[str, Any]]:
    """Applica `connect_nodes` inserendo una piccola resistenza tra due nodi esistenti."""
    node_map = read_json(run_dir / "03_node_map.json")
    from_node = validate_existing_node(action.get("from"), node_map, field_name="from")
    to_node = validate_existing_node(action.get("to"), node_map, field_name="to")
    if from_node == to_node:
        raise ValueError("connect_nodes requires two different nodes")

    resistance = normalize_spice_resistance_value(action.get("resistance"))
    resistor_name = f"RSCENARIO_CONNECT_{sanitize_spice_name(from_node)}_{sanitize_spice_name(to_node)}"
    resistor_line = f"{resistor_name} {from_node} {to_node} {resistance}"
    updated_netlist, operation = insert_or_replace_netlist_element(netlist_text, resistor_name, resistor_line)

    result = {
        "status": "applied",
        "type": "connect_nodes",
        "from": from_node,
        "to": to_node,
        "nodes": [from_node, to_node],
        "resistance": resistance,
        "inserted_line": resistor_line,
        "operation": operation,
        "spice_executed": False,
    }
    return updated_netlist, result


def apply_add_resistor_between_nodes(
    action: dict[str, Any],
    run_dir: Path,
    netlist_text: str,
) -> tuple[str, dict[str, Any]]:
    """
    Applica `add_resistor_between_nodes` aggiungendo un nuovo ramo resistivo.

    A differenza di `connect_nodes`, che modella una continuita quasi ideale,
    questa primitiva aggiunge una resistenza con valore arbitrario tra due nodi
    gia esistenti. Il caso d'uso tipico e un ramo di bias, uno shunt, un
    pull-up/pull-down o un collegamento resistivo supplementare.
    """
    node_map = read_json(run_dir / "03_node_map.json")
    from_node = validate_existing_node(action.get("from"), node_map, field_name="from")
    to_node = validate_existing_node(action.get("to"), node_map, field_name="to")
    if from_node == to_node:
        raise ValueError("add_resistor_between_nodes requires two different nodes")

    raw_value = action.get("value", action.get("resistance"))
    resistance = normalize_spice_resistance_value(raw_value)
    resistor_name = f"RSCENARIO_ADD_{sanitize_spice_name(from_node)}_{sanitize_spice_name(to_node)}"
    resistor_line = f"{resistor_name} {from_node} {to_node} {resistance}"
    updated_netlist, operation = insert_or_replace_netlist_element(netlist_text, resistor_name, resistor_line)

    result = {
        "status": "applied",
        "type": "add_resistor_between_nodes",
        "from": from_node,
        "to": to_node,
        "nodes": [from_node, to_node],
        "value": raw_value,
        "normalized_resistance_value": resistance,
        "inserted_line": resistor_line,
        "operation": operation,
        "spice_executed": False,
    }
    return updated_netlist, result


def apply_feed_nodes_from_source_node(
    action: dict[str, Any],
    run_dir: Path,
    netlist_text: str,
) -> tuple[str, dict[str, Any]]:
    """
    Applica `feed_nodes_from_source_node` come propagazione controllata.

    La primitiva resta semanticamente distinta da `connect_nodes`, ma la
    traduzione SPICE minimale e una resistenza quasi ideale dal nodo sorgente
    verso ciascun target dichiarato.
    """
    node_map = read_json(run_dir / "03_node_map.json")
    source_node = validate_existing_node(action.get("source_node"), node_map, field_name="source_node")
    if source_node == "0":
        raise ValueError("feed_nodes_from_source_node requires a non-ground source_node")

    raw_targets = action.get("target_nodes")
    if raw_targets is None:
        raw_targets = [action.get("target_node")]
    if not isinstance(raw_targets, list):
        raise ValueError("feed_nodes_from_source_node requires target_nodes as a list")

    resistance = normalize_spice_resistance_value(action.get("resistance"))
    updated_netlist = netlist_text
    inserted_lines: list[str] = []
    expanded_connections: list[dict[str, Any]] = []
    seen_targets: set[str] = set()

    for raw_target in raw_targets:
        target_node = validate_existing_node(raw_target, node_map, field_name="target_nodes")
        if target_node == "0":
            raise ValueError("feed_nodes_from_source_node target_nodes cannot include ground node 0")
        if target_node == source_node:
            raise ValueError("feed_nodes_from_source_node target_nodes cannot include source_node")
        if target_node in seen_targets:
            continue
        seen_targets.add(target_node)

        resistor_name = (
            f"RSCENARIO_FEED_{sanitize_spice_name(source_node)}_"
            f"{sanitize_spice_name(target_node)}"
        )
        resistor_line = f"{resistor_name} {source_node} {target_node} {resistance}"
        updated_netlist, operation = insert_or_replace_netlist_element(updated_netlist, resistor_name, resistor_line)
        inserted_lines.append(resistor_line)
        expanded_connections.append(
            {
                "from": source_node,
                "to": target_node,
                "resistance": resistance,
                "inserted_line": resistor_line,
                "operation": operation,
            }
        )

    if not expanded_connections:
        raise ValueError("feed_nodes_from_source_node requires at least one valid target node")

    result = {
        "status": "applied",
        "type": "feed_nodes_from_source_node",
        "source_node": source_node,
        "target_nodes": [item["to"] for item in expanded_connections],
        "resistance": resistance,
        "inserted_lines": inserted_lines,
        "expanded_connections": expanded_connections,
        "operation": "inserted_or_updated",
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
    updated_netlist, operation = insert_or_replace_netlist_element(netlist_text, resistor_name, resistor_line)
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


def apply_change_source_value_action(
    action: dict[str, Any],
    run_dir: Path,
    netlist_text: str,
) -> tuple[str, dict[str, Any]]:
    """Adapter uniforme per la registry delle action."""
    del run_dir
    return apply_change_source_value(action, netlist_text)


def apply_change_component_value_action(
    action: dict[str, Any],
    run_dir: Path,
    netlist_text: str,
) -> tuple[str, dict[str, Any]]:
    """Adapter uniforme per la registry delle action."""
    del run_dir
    return apply_change_component_value(action, netlist_text)


ACTION_HANDLERS = {
    "drive_node_voltage": apply_drive_node_voltage,
    "set_initial_node_voltage": apply_set_initial_node_voltage,
    "add_voltage_source_between_nodes": apply_add_voltage_source_between_nodes,
    "connect_nodes": apply_connect_nodes,
    "add_resistor_between_nodes": apply_add_resistor_between_nodes,
    "feed_nodes_from_source_node": apply_feed_nodes_from_source_node,
    "change_source_value": apply_change_source_value_action,
    "change_component_value": apply_change_component_value_action,
    "close_switch": apply_close_switch,
}


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


def build_scenario_comparison(scenario_dir: Path, scenario: dict[str, Any]) -> dict[str, Any]:
    """Confronta le grandezze richieste tra base run e scenario run."""
    status = read_json(scenario_dir / STATUS_NAME) if (scenario_dir / STATUS_NAME).exists() else {}
    base_output_dir = Path(status.get("base_output_dir") or scenario_dir.parent.parent)
    run_dir = scenario_dir / "run"
    analysis = str(scenario.get("analysis") or "op").strip().lower()
    # Uno scenario legacy privo di `intent` e un test diagnostico prudente.
    # La risoluzione automatica richiede sempre `intent: correction` esplicito.
    intent = (
        "correction"
        if str(scenario.get("intent") or "").strip().lower() == "correction"
        else "diagnostic"
    )

    requested = scenario.get("compare") or []
    if not isinstance(requested, list):
        requested = []

    base_values = parse_ngspice_stdout(base_output_dir / "08_ngspice_stdout.txt")
    scenario_values = parse_ngspice_stdout(run_dir / "08_ngspice_stdout.txt")
    base_tran_metrics = parse_tran_csv_metrics(
        base_output_dir / "08_tran.csv", requested_quantities=requested
    )
    scenario_tran_metrics = parse_tran_csv_metrics(
        run_dir / "08_tran.csv", requested_quantities=requested
    )
    base_stderr_warning_count = count_ngspice_stderr_warnings(base_output_dir / "08_ngspice_stderr.txt")
    scenario_stderr_warning_count = count_ngspice_stderr_warnings(run_dir / "08_ngspice_stderr.txt")

    raw_expectations = scenario.get("expect") or {}
    expectations = (
        {
            quantity_lookup_key(str(quantity)): str(expectation).strip().lower()
            for quantity, expectation in raw_expectations.items()
        }
        if isinstance(raw_expectations, dict)
        else {}
    )
    raw_measurements = scenario.get("measure") or {}
    measurements = (
        {
            quantity_lookup_key(str(quantity)): str(measurement).strip().lower()
            for quantity, measurement in raw_measurements.items()
        }
        if isinstance(raw_measurements, dict)
        else {}
    )

    quantities: list[dict[str, Any]] = []
    activated = 0
    changed = 0
    missing = 0
    expected = 0
    expectations_met = 0
    expectations_failed = 0
    expectations_missing = 0
    meaningful_improvements = 0

    for item in requested:
        quantity = normalize_quantity_name(str(item))
        measurement = measurements.get(quantity_lookup_key(quantity))
        if is_stderr_quantity(quantity):
            lookup_key = "stderr.warning_count"
            base_value = base_stderr_warning_count
            scenario_value = scenario_stderr_warning_count
            base_details: dict[str, Any] = {}
            scenario_details: dict[str, Any] = {}
        elif measurement == "tran_abs_peak":
            lookup_key = quantity_lookup_key(quantity)
            base_metric_set = base_tran_metrics.get(lookup_key) or {}
            scenario_metric_set = scenario_tran_metrics.get(lookup_key) or {}
            base_value = base_metric_set.get("abs_peak")
            scenario_value = scenario_metric_set.get("abs_peak")
            lookup_key = f"{lookup_key}.abs_peak"
            base_details = base_metric_set
            scenario_details = scenario_metric_set
        elif measurement == "tran_vpp" or (
            measurement is None and analysis == "tran" and is_voltage_quantity(quantity)
        ):
            lookup_key = quantity_lookup_key(quantity)
            base_metric_set = base_tran_metrics.get(lookup_key) or {}
            scenario_metric_set = scenario_tran_metrics.get(lookup_key) or {}
            base_value = base_metric_set.get("vpp")
            scenario_value = scenario_metric_set.get("vpp")
            lookup_key = f"{lookup_key}.vpp"
            base_details = base_metric_set
            scenario_details = scenario_metric_set
        elif (
            (measurement == "op" or (measurement is None and analysis == "op"))
            and is_internal_device_current_quantity(quantity)
        ):
            # I vettori `@d...[id]` sono esportati nello storico CSV, ma non
            # nella tabella .op dello stdout. Il campione finale e la migliore
            # evidenza stazionaria disponibile senza alterare la simulazione.
            lookup_key = quantity_lookup_key(quantity)
            base_metric_set = base_tran_metrics.get(lookup_key) or {}
            scenario_metric_set = scenario_tran_metrics.get(lookup_key) or {}
            base_value = base_metric_set.get("final")
            scenario_value = scenario_metric_set.get("final")
            lookup_key = f"{lookup_key}.final"
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

        expectation = expectations.get(quantity_lookup_key(quantity))
        expectation_met = None
        meaningful_improvement = False
        relative_change = relative_change_ratio(base_value, scenario_value)
        if expectation:
            expected += 1
            expectation_met = expectation_matches(
                expectation,
                base_value,
                scenario_value,
                change,
            )
            if expectation_met is True:
                expectations_met += 1
                meaningful_improvement = expectation_is_meaningful_improvement(
                    expectation,
                    base_value,
                    scenario_value,
                    change,
                )
                if meaningful_improvement:
                    meaningful_improvements += 1
            elif expectation_met is False:
                expectations_failed += 1
            else:
                expectations_missing += 1

        quantities.append(
            {
                "quantity": quantity,
                "base_value": base_value,
                "scenario_value": scenario_value,
                "delta": delta,
                "change": change,
                "expectation": expectation,
                "expectation_met": expectation_met,
                "relative_change": relative_change,
                "meaningful_improvement": meaningful_improvement,
                "metric": lookup_key,
                "measurement": measurement or (
                    "tran_vpp" if analysis == "tran" and is_voltage_quantity(quantity) else "op"
                ),
                "base_details": base_details,
                "scenario_details": scenario_details,
            }
        )

    summary = {
        "requested_count": len(quantities),
        "changed_count": changed,
        "activated_count": activated,
        "missing_count": missing,
        "expected_count": expected,
        "expectations_met_count": expectations_met,
        "expectations_failed_count": expectations_failed,
        "expectations_missing_count": expectations_missing,
        "meaningful_improvement_count": meaningful_improvements,
    }

    gain_config = scenario.get("gain") if isinstance(scenario.get("gain"), dict) else {}
    gain_input = quantity_lookup_key(str(gain_config.get("input") or ""))
    gain_output = quantity_lookup_key(str(gain_config.get("output") or ""))
    min_gain_ratio = None
    raw_min_gain_ratio = gain_config.get("min_ratio")
    if raw_min_gain_ratio is not None:
        try:
            parsed_min_gain_ratio = float(raw_min_gain_ratio)
        except (TypeError, ValueError) as exc:
            raise ValueError("scenario.gain.min_ratio deve essere un numero positivo") from exc
        if parsed_min_gain_ratio <= 0:
            raise ValueError("scenario.gain.min_ratio deve essere maggiore di zero")
        min_gain_ratio = parsed_min_gain_ratio
    base_gain = None
    scenario_gain = None
    if gain_input and gain_output:
        base_input = (base_tran_metrics.get(gain_input) or {}).get("vpp")
        base_output = (base_tran_metrics.get(gain_output) or {}).get("vpp")
        scenario_input = (scenario_tran_metrics.get(gain_input) or {}).get("vpp")
        scenario_output = (scenario_tran_metrics.get(gain_output) or {}).get("vpp")
        if base_input is not None and abs(base_input) >= COMPARISON_TOLERANCE and base_output is not None:
            base_gain = abs(base_output / base_input)
        if (
            scenario_input is not None
            and abs(scenario_input) >= COMPARISON_TOLERANCE
            and scenario_output is not None
        ):
            scenario_gain = abs(scenario_output / scenario_input)

    gain_comparison = {
        "input": gain_config.get("input"),
        "output": gain_config.get("output"),
        "base_gain": base_gain,
        "scenario_gain": scenario_gain,
        "min_ratio": min_gain_ratio,
        "available": scenario_gain is not None,
        "sufficient": (
            scenario_gain is not None
            and min_gain_ratio is not None
            and scenario_gain >= min_gain_ratio
        ) if min_gain_ratio is not None else None,
        "relative_change": relative_change_ratio(base_gain, scenario_gain),
    } if gain_config else None

    quality_requested = str(scenario.get("quality") or "").strip().lower() == "thd"
    quality_comparison: dict[str, Any] | None = None
    if quality_requested and gain_config:
        input_quantity = str(gain_config.get("input") or "")
        output_quantity = str(gain_config.get("output") or "")
        base_quality = analyze_sine_quality(
            base_output_dir / "08_tran.csv",
            base_output_dir / NETLIST_NAME,
            input_quantity,
            output_quantity,
        )
        scenario_quality = analyze_sine_quality(
            run_dir / "08_tran.csv",
            run_dir / NETLIST_NAME,
            input_quantity,
            output_quantity,
        )
        quality_comparison = compare_sine_quality(base_quality, scenario_quality)

    summary["quality_required"] = quality_requested
    summary["quality_available"] = bool(
        quality_comparison and quality_comparison.get("available")
    )
    summary["quality_improved"] = bool(
        quality_comparison and quality_comparison.get("improved")
    )
    summary["quality_acceptable"] = bool(
        quality_comparison and quality_comparison.get("acceptable")
    )
    summary["quality_output_preserved"] = bool(
        quality_comparison and quality_comparison.get("output_preserved")
    )
    summary["base_thd"] = (
        quality_comparison.get("base_thd") if quality_comparison else None
    )
    summary["scenario_thd"] = (
        quality_comparison.get("scenario_thd") if quality_comparison else None
    )
    summary["gain_required"] = min_gain_ratio is not None
    summary["gain_available"] = scenario_gain is not None
    summary["gain_sufficient"] = bool(
        min_gain_ratio is not None
        and scenario_gain is not None
        and scenario_gain >= min_gain_ratio
    )
    summary["scenario_gain"] = scenario_gain
    summary["min_gain_ratio"] = min_gain_ratio
    diagnostic_outcome = evaluate_diagnostic_outcome(
        summary,
        analysis=analysis,
        intent=intent,
    )

    comparison = {
        "source_format": "pipeline2.0_scenario_comparison",
        "scenario_id": scenario.get("scenario_id"),
        "scenario_title": scenario.get("title"),
        "scenario_intent": intent,
        "base_output_dir": str(base_output_dir),
        "scenario_run_dir": str(run_dir),
        "base_stdout": str(base_output_dir / "08_ngspice_stdout.txt"),
        "scenario_stdout": str(run_dir / "08_ngspice_stdout.txt"),
        "base_stderr": str(base_output_dir / "08_ngspice_stderr.txt"),
        "scenario_stderr": str(run_dir / "08_ngspice_stderr.txt"),
        "quantities": quantities,
        "summary": summary,
        "gain_comparison": gain_comparison,
        "quality_comparison": quality_comparison,
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
        handler = ACTION_HANDLERS.get(action_type)
        try:
            if handler is None:
                unsupported_actions.append({
                    "index": index,
                    "status": "unsupported",
                    "type": action_type or None,
                    "reason": "Action type is not supported in the current minimal version.",
                })
                continue

            if action_type == "set_initial_node_voltage" and str(scenario.get("analysis") or "").strip().lower() != "tran":
                raise ValueError("set_initial_node_voltage richiede analysis='tran'")

            netlist_text, result = handler(action, run_dir, netlist_text)
            result["index"] = index
            applied_actions.append(result)
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
        next_step = "Hai esaurito il budget scenari. Chiedi all'agente una conclusione diagnostica finale."
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
