"""
Gestione dei valori elettrici tramite YAML.

Questo modulo legge values.yaml e associa valori, modelli, sorgenti, stati
e assunzioni manuali ai componenti del Graph JSON.

Il file YAML serve a separare il problema topologico dal problema OCR/valori:
la pipeline 2.0 non deve inventare valori mancanti. Se un valore non e
disponibile, deve essere registrato nei parametri mancanti e nel report.

Responsabilita previste:

- leggere valori di resistenze, condensatori, sorgenti e carichi;
- leggere modelli per LED, diodi, BJT, MOSFET e componenti speciali;
- leggere stati manuali di switch quando necessario;
- leggere nodi manuali come VCC, VDD, GND, OUT;
- distinguere valori osservati, assunti e mancanti.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


VALUE_REQUIRED = {
    "Resistor": ("value",),
    "Capacitor": ("value",),
    # I condensatori polarizzati usano la stessa primitiva SPICE C, ma il
    # Graph JSON ne conserva la polarita come informazione semantica.
    "Polarized_Capacitor": ("value",),
    "Battery": ("value",),
    "Voltage_Source": ("value",),
    "Current_Source": ("value",),
    "Signal_Source": ("value",),
    "LED": ("model",),
    "Diode": ("model",),
    "NPN_Transistor": ("model",),
    "Lamp": ("equivalent_resistance", "value"),
    "Switch": ("state",),
    "Fuse": ("state",),
    "Transformer": ("model",),
}

NOT_REQUIRED = {
    "Analog_Meter",
    "GND",
    "Connector",
    "Meter",
    "Terminal",
}


def parse_scalar(value: str) -> Any:
    """Converte stringhe YAML semplici in bool, int, float, null o stringa."""
    text = value.strip()
    if text == "":
        return ""
    if text in ("null", "Null", "NULL", "~"):
        return None
    if text in ("true", "True", "TRUE"):
        return True
    if text in ("false", "False", "FALSE"):
        return False
    if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
        return text[1:-1]
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(item.strip()) for item in inner.split(",")]
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        return text


def load_simple_yaml(path: str | Path) -> dict[str, Any]:
    """
    Legge un sottoinsieme semplice di YAML.

    Supporta solo dizionari annidati con indentazione a spazi e valori scalari.
    Basta per i file manuali della pipeline 2.0 e non richiede dipendenze.
    """
    yaml_path = Path(path)
    if not yaml_path.exists():
        return {}

    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]

    for line_number, raw_line in enumerate(yaml_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()

        if ":" not in line:
            raise ValueError(f"YAML non supportato alla riga {line_number}: {raw_line}")

        key, raw_value = line.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()

        while stack and indent <= stack[-1][0]:
            stack.pop()

        if not stack:
            raise ValueError(f"Indentazione YAML non valida alla riga {line_number}: {raw_line}")

        parent = stack[-1][1]
        if raw_value == "":
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = parse_scalar(raw_value)

    return root


def find_manual_values_path(project_root: Path, batch_name: str, circuit_id: str) -> Path:
    """Restituisce il path atteso del file valori manuale."""
    return (
        project_root
        / "metadata"
        / "pipeline2_manual_values"
        / batch_name
        / f"{circuit_id}_values.yaml"
    )


def has_required_data(class_name: str, value_data: dict[str, Any]) -> bool:
    """Verifica se un componente ha almeno uno dei campi richiesti."""
    required_fields = VALUE_REQUIRED.get(class_name)
    if required_fields is None:
        return False
    return any(field in value_data and value_data.get(field) not in (None, "") for field in required_fields)


def classify_component(class_name: str, value_data: dict[str, Any] | None) -> str:
    """Assegna uno stato semplice al componente."""
    if class_name in NOT_REQUIRED:
        return "not_required"
    if class_name in VALUE_REQUIRED:
        if value_data and has_required_data(class_name, value_data):
            return "bound"
        return "missing"
    return "unsupported_for_now"


def graph_value_data(component: dict[str, Any]) -> dict[str, Any]:
    """
    Estrae valori elettrici gia presenti nel Graph JSON.

    Il Graph JSON ha priorita per campi prodotti dalla pipeline 1.0, come lo
    stato degli switch. Il values.yaml puo poi sovrascriverli quando serve.
    """
    data: dict[str, Any] = {}

    if component.get("state") not in (None, ""):
        data["state"] = component.get("state")
        data["state_source"] = "graph_json_state"
    if component.get("state_confidence") not in (None, ""):
        data["state_confidence"] = component.get("state_confidence")

    return data


def bind_supplies(
    supplies: dict[str, Any],
    terminal_to_node: dict[str, str],
) -> dict[str, Any]:
    """Aggiunge il nodo elettrico alle supply dichiarate nel YAML."""
    bound: dict[str, Any] = {}

    for supply_name, supply_data in supplies.items():
        if not isinstance(supply_data, dict):
            continue
        terminal_id = supply_data.get("terminal")
        entry = dict(supply_data)
        entry["node"] = terminal_to_node.get(str(terminal_id)) if terminal_id else None
        bound[str(supply_name)] = entry

    return dict(sorted(bound.items()))


def bind_manual_nodes(
    nodes: dict[str, Any],
    terminal_to_node: dict[str, str],
) -> dict[str, Any]:
    """Aggiunge il node_id ai nodi manuali dichiarati nel YAML."""
    bound: dict[str, Any] = {}

    for terminal_id, node_data in nodes.items():
        entry = dict(node_data) if isinstance(node_data, dict) else {"label": node_data}
        entry["node"] = terminal_to_node.get(str(terminal_id))
        bound[str(terminal_id)] = entry

    return dict(sorted(bound.items()))


def build_values_bound(
    normalized_circuit: dict[str, Any],
    node_map: dict[str, Any],
    values_data: dict[str, Any],
    values_source: str | Path | None = None,
) -> dict[str, Any]:
    """
    Associa valori YAML, componenti e nodi elettrici.

    Questo step non genera SPICE: prepara solo dati puliti per gli step
    successivi.
    """
    yaml_components = values_data.get("components") or {}
    yaml_supplies = values_data.get("supplies") or {}
    yaml_nodes = values_data.get("nodes") or {}
    yaml_simulation = values_data.get("simulation") or {}
    terminal_to_node = node_map.get("terminal_to_node") or {}
    component_terminal_nodes = node_map.get("component_terminal_nodes") or {}

    bound_components: dict[str, Any] = {}
    missing: list[dict[str, Any]] = []
    stats = {
        "components_total": 0,
        "bound_components": 0,
        "missing_components": 0,
        "not_required_components": 0,
        "unsupported_components": 0,
        "supplies_count": 0,
        "manual_nodes_count": 0,
    }

    for component in normalized_circuit.get("components") or []:
        component_id = str(component.get("component_id", ""))
        class_name = str(component.get("class_name", ""))
        if not component_id:
            continue

        yaml_value_data = yaml_components.get(component_id)
        if yaml_value_data is not None and not isinstance(yaml_value_data, dict):
            yaml_value_data = {"value": yaml_value_data}

        value_data = graph_value_data(component)
        if isinstance(yaml_value_data, dict):
            value_data.update(yaml_value_data)
        if not value_data:
            value_data = None

        status = classify_component(class_name, value_data)
        terminal_nodes = component_terminal_nodes.get(component_id, {})

        entry = {
            "class_name": class_name,
            "terminal_nodes": terminal_nodes,
            "value_data": value_data,
            "status": status,
        }
        bound_components[component_id] = entry

        stats["components_total"] += 1
        if status == "bound":
            stats["bound_components"] += 1
        elif status == "missing":
            stats["missing_components"] += 1
            missing.append({
                "component_id": component_id,
                "class_name": class_name,
                "required": list(VALUE_REQUIRED.get(class_name, ())),
            })
        elif status == "not_required":
            stats["not_required_components"] += 1
        elif status == "unsupported_for_now":
            stats["unsupported_components"] += 1

    bound_supplies = bind_supplies(yaml_supplies, terminal_to_node)
    bound_nodes = bind_manual_nodes(yaml_nodes, terminal_to_node)
    stats["supplies_count"] = len(bound_supplies)
    stats["manual_nodes_count"] = len(bound_nodes)

    return {
        "circuit_id": normalized_circuit.get("circuit_id"),
        "source_format": "pipeline2.0_values_bound",
        "values_source": str(values_source) if values_source else None,
        "supplies": bound_supplies,
        "components": dict(sorted(bound_components.items())),
        "nodes": bound_nodes,
        "simulation": yaml_simulation if isinstance(yaml_simulation, dict) else {},
        "missing": missing,
        "stats": stats,
    }
