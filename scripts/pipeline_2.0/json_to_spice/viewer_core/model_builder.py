"""
Costruisce il modello dati del viewer per una run della Pipeline 2.0.

Il modello resta intenzionalmente guidato dalla netlist: `07_netlist.cir`
descrive il circuito che ngspice ha realmente simulato, mentre
`03_node_map.json` e `06_component_rules.json` aggiungono il contesto
strutturale utile al viewer, come connector, masse e switch aperti non emessi
in SPICE.
"""

from __future__ import annotations

import csv
from datetime import datetime
import re
from pathlib import Path
from statistics import median
from typing import Any

from run_sources import get_run_source_path

from .contracts import (
    NETLIST_NAME,
    PROJECT_ROOT,
    VIEWER_MODEL_NAME,
    VIEWER_MODEL_SCHEMA_VERSION,
)
from .json_io import read_json, write_json

TRANSIENT_VARIATION_EPSILON = 1e-5
MAX_TRANSIENT_VIEWER_SAMPLES = 800
LED_FORWARD_THRESHOLD_V = 0.6
LED_VISIBLE_CURRENT_A = 1e-4
LED_BRANCH_SIGNAL_MIN_SPAN_V = 0.5
LED_PLAYBACK_SLOWDOWN = 10.0
LED_PERIOD_RELATIVE_TOLERANCE = 0.15


def led_current_states_with_hysteresis(
    currents: list[float],
) -> tuple[list[bool], float, float]:
    """
    Converte la corrente LED in stati stabili con una soglia isteretica.

    ngspice puo oscillare numericamente attorno alla soglia di visibilita e
    produrre false commutazioni a ogni campione. Le due soglie si adattano
    all'escursione misurata. Una modulazione ad alto contrasto distingue inoltre
    uno stato luminoso da uno molto piu debole, anche quando il modello SPICE
    ideale non porta la corrente esattamente a zero.
    """
    if not currents:
        return [], LED_VISIBLE_CURRENT_A, LED_VISIBLE_CURRENT_A
    current_min = min(currents)
    current_max = max(currents)
    if current_max < LED_VISIBLE_CURRENT_A:
        return [False] * len(currents), LED_VISIBLE_CURRENT_A, LED_VISIBLE_CURRENT_A
    current_span = current_max - current_min
    high_contrast_modulation = (
        current_span >= LED_VISIBLE_CURRENT_A
        and current_min <= 0.25 * current_max
    )
    if current_min >= LED_VISIBLE_CURRENT_A and not high_contrast_modulation:
        return [True] * len(currents), LED_VISIBLE_CURRENT_A, LED_VISIBLE_CURRENT_A

    turn_on_threshold = max(
        LED_VISIBLE_CURRENT_A,
        current_min + 0.40 * current_span,
    )
    relative_turn_off = current_min + 0.15 * current_span
    turn_off_threshold = (
        relative_turn_off
        if high_contrast_modulation
        else min(LED_VISIBLE_CURRENT_A, relative_turn_off)
    )
    state = currents[0] >= LED_VISIBLE_CURRENT_A
    states: list[bool] = []
    for current in currents:
        if state and current <= turn_off_threshold:
            state = False
        elif not state and current >= turn_on_threshold:
            state = True
        states.append(state)
    return states, turn_on_threshold, turn_off_threshold


def normalize_node(node: str) -> str:
    """Normalizza il nome di un nodo SPICE mantenendo `0` come massa."""
    node = str(node).strip()
    return "0" if node == "0" else node.upper()


def spice_kind(name: str) -> str:
    """Ricava il tipo logico di componente dal prefisso SPICE."""
    prefix = name[:1].upper()
    return {
        "R": "resistor",
        "C": "capacitor",
        "L": "inductor",
        "V": "voltage_source",
        "I": "current_source",
        "D": "diode",
        "Q": "bjt",
        "X": "subcircuit",
    }.get(prefix, "unknown")


def is_variable_voltage_source(component: dict[str, Any]) -> bool:
    """Riconosce una sorgente di segnale dalla forma d'onda dichiarata in SPICE."""
    if str(component.get("kind") or "").lower() != "voltage_source":
        return False
    value = str(component.get("value") or "").strip()
    return bool(re.match(r"^(?:SIN|PULSE|PWL|EXP|SFFM|AM)\s*\(", value, flags=re.IGNORECASE))


def expected_node_count(name: str) -> int:
    """Restituisce quanti nodi leggere dalla riga SPICE del componente."""
    prefix = name[:1].upper()
    if prefix == "Q":
        return 3
    return 2


def source_component_id(spice_name: str) -> str | None:
    """Prova a ricostruire l'id del componente originale dal nome SPICE."""
    prefix = spice_name[:1].upper()
    if prefix not in {"R", "C", "L", "D", "Q", "V", "I", "X"}:
        return None
    base = spice_name[1:]
    if spice_name.lower().startswith("rmeter_"):
        # Lo step 07 usa `Rmeter_` per il proxy resistivo degli strumenti analogici.
        base = spice_name[len("Rmeter_") :]
    match = re.match(r"(.+)_([0-9]+)$", base)
    if not match:
        return None
    return f"{match.group(1).lower()}.{match.group(2)}"


def enrich_components_with_rules(
    components: list[dict[str, Any]],
    rules: dict[str, Any],
) -> list[dict[str, Any]]:
    """Aggiunge classe, parametri e label dichiarati nelle regole Pipeline 2.0."""
    component_rules = rules.get("components") or {}
    enriched: list[dict[str, Any]] = []
    for component in components:
        item = dict(component)
        source_id = str(item.get("source_component_id") or "")
        rule = component_rules.get(source_id) or {}
        if isinstance(rule, dict) and rule:
            item["class_name"] = rule.get("class_name")
            item["parameters"] = rule.get("parameters") or {}
            item["display_label"] = (rule.get("parameters") or {}).get("label_text")
            item["terminal_names"] = [str(name) for name in (rule.get("node_order") or [])]
            if rule.get("status") == "measurement_only":
                item["viewer_proxy_for"] = source_id
                item["viewer_role"] = "simulation_measurement_proxy"
        enriched.append(item)
    return enriched


def enrich_bjt_kind_from_spice_models(
    components: list[dict[str, Any]],
    directives: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Distingue NPN e PNP usando il tipo dichiarato nelle direttive `.model`.

    Il Graph JSON puo' conservare una classe transistor generica o storicamente
    errata. La netlist simulata resta la fonte di verita': il viewer ricava la
    freccia del BJT dal modello realmente caricato da ngspice, senza dipendere
    dall'id del componente o dal circuito corrente.
    """
    model_kinds: dict[str, str] = {}
    for entry in directives:
        directive = str((entry or {}).get("directive") or "").strip()
        match = re.match(
            r"^\.model\s+(\S+)\s+(NPN|PNP)(?:\s|\()",
            directive,
            flags=re.IGNORECASE,
        )
        if match:
            model_kinds[match.group(1).upper()] = match.group(2).lower()

    enriched: list[dict[str, Any]] = []
    for component in components:
        item = dict(component)
        if str(item.get("kind") or "").lower() == "bjt":
            model_kind = model_kinds.get(str(item.get("model") or "").upper())
            if model_kind in {"npn", "pnp"}:
                item["viewer_kind"] = f"{model_kind}_transistor"
                item["viewer_bjt_kind_source"] = "spice_model_directive"
        enriched.append(item)
    return enriched


def enrich_manual_dc_supplies(
    components: list[dict[str, Any]],
    rules: dict[str, Any],
) -> list[dict[str, Any]]:
    """Rende esplicite nel viewer le sorgenti DC aggiunte dal file valori."""
    supplies = rules.get("supplies") or {}
    enriched = [dict(component) for component in components]
    for supply_name, supply in supplies.items():
        if not isinstance(supply, dict):
            continue
        parameters = supply.get("parameters") if isinstance(supply.get("parameters"), dict) else supply
        if str(parameters.get("type") or "").strip().lower() != "dc":
            continue

        expected_name = f"V{supply_name}".lower()
        supply_nodes = {normalize_node(node) for node in supply.get("nodes") or []}
        source = next(
            (item for item in enriched if str(item.get("spice_name") or "").lower() == expected_name),
            None,
        )
        if source is None and supply_nodes:
            source = next(
                (
                    item for item in enriched
                    if item.get("kind") == "voltage_source"
                    and {normalize_node(node) for node in item.get("nodes") or []} == supply_nodes
                ),
                None,
            )
        if source is None:
            continue

        source_origin = str(parameters.get("source") or "").strip().lower()
        viewer_override = parameters.get("viewer_override")
        viewer_override = viewer_override if isinstance(viewer_override, dict) else {}
        is_ocr_label = source_origin == "manual_from_image_label"
        try:
            reference_value = float(parameters.get("value") or 0.0)
        except (TypeError, ValueError):
            reference_value = None
        is_simulation_reference = (
            source_origin.startswith("manual_reference_for_")
            and reference_value == 0.0
            and str(parameters.get("reference") or "0").strip() == "0"
        )
        if is_simulation_reference:
            # Una sorgente ideale da 0 V usata soltanto per riferire una rete
            # flottante non e' un componente presente nell'immagine.
            source["viewer_hidden"] = True
            source["viewer_role"] = "simulation_reference"
            source["parameters"] = dict(parameters)
            source["supply_name"] = str(supply_name)
            continue

        # Lo YAML puo' chiedere una batteria esterna mantenendo separati il
        # modello elettrico e il simbolo. Il nodo di ritorno e' gia' risolto
        # dallo step 04 e non viene dedotto dal circuito corrente.
        source["viewer_kind"] = str(viewer_override.get("visual_class") or "dc_supply")
        source["viewer_role"] = "manual_ocr_dc_supply" if is_ocr_label else "manual_dc_supply"
        source["parameters"] = dict(parameters)
        source["display_label"] = str(viewer_override.get("label") or parameters.get("label_text") or supply_name)
        source["viewer_label"] = str(viewer_override.get("label") or "")
        if viewer_override.get("display_value") is not None:
            source["viewer_value"] = str(viewer_override.get("display_value") or "")
        if viewer_override.get("label_mode") is not None:
            source["viewer_label_mode"] = str(viewer_override.get("label_mode") or "")
        if viewer_override.get("tooltip") is not None:
            source["viewer_tooltip"] = str(viewer_override.get("tooltip") or "")
        source["supply_name"] = str(supply_name)
        return_node = parameters.get("return_node")
        supply_nodes = list(supply.get("nodes") or [])
        if supply_nodes and return_node not in (None, "") and viewer_override.get("visual_class") == "battery":
            source["simulation_nodes"] = list(source.get("nodes") or [])
            source["nodes"] = [str(supply_nodes[0]), normalize_node(str(return_node))]
            source["terminal_names"] = ["positive", "negative"]
            anchor_terminal_ids = [
                str(parameters.get("terminal") or ""),
                str(parameters.get("return_terminal") or ""),
            ]
            source["viewer_anchor_component_ids"] = [
                terminal_id.rsplit("_", 1)[0]
                for terminal_id in anchor_terminal_ids
                if "_" in terminal_id
            ]
    return enriched


def apply_supply_visibility_overrides(
    components: list[dict[str, Any]],
    rules: dict[str, Any],
) -> list[dict[str, Any]]:
    """Nasconde nel viewer gli stimoli numerici marcati esplicitamente.

    La sorgente continua a esistere nella netlist e nel transitorio. L'override
    riguarda soltanto la sua resa grafica ed evita di mostrare come componente
    fisico un ausilio di testbench gia' rappresentato dal Graph.
    """
    supplies = rules.get("supplies") or {}
    enriched = [dict(component) for component in components]
    for supply_name, supply in supplies.items():
        if not isinstance(supply, dict):
            continue
        parameters = supply.get("parameters") if isinstance(supply.get("parameters"), dict) else supply
        viewer_override = parameters.get("viewer_override")
        viewer_override = viewer_override if isinstance(viewer_override, dict) else {}
        if viewer_override.get("hidden") is not True:
            continue

        expected_name = f"V{supply_name}".lower()
        supply_nodes = {normalize_node(node) for node in supply.get("nodes") or []}
        source = next(
            (
                item for item in enriched
                if str(item.get("spice_name") or "").lower() == expected_name
            ),
            None,
        )
        if source is None and supply_nodes:
            source = next(
                (
                    item for item in enriched
                    if item.get("kind") == "voltage_source"
                    and {normalize_node(node) for node in item.get("nodes") or []} == supply_nodes
                ),
                None,
            )
        if source is None:
            continue

        source["viewer_hidden"] = True
        source["viewer_role"] = "hidden_testbench_stimulus"
        source["parameters"] = dict(parameters)
        source["supply_name"] = str(supply_name)
    return enriched


def parse_netlist(netlist_path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    """Estrae componenti, direttive e warning dal file `07_netlist.cir`."""
    components: list[dict[str, Any]] = []
    directives: list[dict[str, Any]] = []
    warnings: list[str] = []
    inside_control_block = False
    inside_subcircuit = False

    if not netlist_path.exists():
        warnings.append(f"Netlist mancante: {netlist_path}")
        return components, directives, warnings

    for line_number, raw_line in enumerate(netlist_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("*"):
            continue
        if line.startswith("."):
            directives.append({"line_number": line_number, "directive": line})
            if line.lower() == ".control":
                inside_control_block = True
            elif line.lower() == ".endc":
                inside_control_block = False
            elif line.lower().startswith(".subckt "):
                inside_subcircuit = True
            elif line.lower().startswith(".ends"):
                inside_subcircuit = False
            continue
        if inside_control_block:
            # I comandi `run` e `wrdata` appartengono a ngspice e non sono componenti.
            directives.append({"line_number": line_number, "directive": line, "scope": "control"})
            continue
        if inside_subcircuit:
            # Gli elementi interni appartengono al modello X e non devono
            # apparire come componenti fisici separati nel viewer.
            continue

        parts = line.split()
        if not parts:
            continue
        name = parts[0]
        # Le subcircuit emesse dalla Pipeline 2.0 hanno forma X + nodi + nome
        # modello. Il numero di pin resta quindi ricavabile senza conoscere il
        # dispositivo specifico o introdurre eccezioni per circuito.
        node_count = len(parts) - 2 if name[:1].upper() == "X" else expected_node_count(name)
        if len(parts) < 1 + node_count:
            warnings.append(f"Impossibile interpretare la riga {line_number}: {line}")
            continue

        nodes = [normalize_node(item) for item in parts[1 : 1 + node_count]]
        value_tokens = parts[1 + node_count :]
        is_scenario_added = name.upper().startswith(("RSCENARIO", "VSCENARIO", "ISCENARIO"))
        component = {
            "id": name,
            "spice_name": name,
            "kind": spice_kind(name),
            "nodes": nodes,
            "value": " ".join(value_tokens),
            "model": value_tokens[-1] if value_tokens and name[:1].upper() in {"D", "Q", "X"} else None,
            "source_component_id": source_component_id(name),
            "is_scenario_added": is_scenario_added,
            "source_line": raw_line,
            "line_number": line_number,
        }
        components.append(component)

    return components, directives, warnings


def parse_ngspice_stdout(stdout_path: Path) -> dict[str, Any]:
    """Legge tensioni e correnti operative dall'output testuale di ngspice."""
    measurements: dict[str, Any] = {
        "node_voltages": {},
        "branch_currents": {},
        "device_currents": {},
    }
    if not stdout_path.exists():
        measurements["status"] = "missing"
        return measurements

    lines = stdout_path.read_text(encoding="utf-8", errors="replace").splitlines()
    section: str | None = None
    pending_devices: list[str] = []

    for raw_line in lines:
        line = raw_line.strip()
        lower = line.lower()
        if not line:
            continue
        if lower.startswith("node") and "voltage" in lower:
            section = "node_voltage"
            continue
        if lower.startswith("source") and "current" in lower:
            section = "source_current"
            continue
        if lower.startswith("device"):
            tokens = line.split()[1:]
            pending_devices = [token.lower() for token in tokens]
            section = "device_table"
            continue
        if section == "node_voltage":
            match = re.match(r"^(n[0-9a-z_]+)\s+([-+0-9.eE]+)$", lower)
            if match:
                measurements["node_voltages"][match.group(1).upper()] = float(match.group(2))
            continue
        if section == "source_current":
            match = re.match(r"^([a-z0-9_#]+)\s+([-+0-9.eE]+)$", lower)
            if match:
                measurements["branch_currents"][match.group(1).upper()] = float(match.group(2))
            continue
        if section == "device_table" and pending_devices:
            quantity = lower.split(maxsplit=1)[0]
            # ngspice chiama `i` la corrente dei bipoli, `id` quella dei
            # diodi e `ic` quella di collettore dei BJT. Si conserva una sola
            # misura rappresentativa per dispositivo, evitando che `ib` o
            # `ie` sovrascrivano la corrente principale del transistor.
            expected_quantity = (
                "id"
                if all(device.startswith("d") for device in pending_devices)
                else "ic"
                if all(device.startswith("q") for device in pending_devices)
                else "i"
            )
            if quantity != expected_quantity:
                continue
            values = line.split()[1:]
            for device, value in zip(pending_devices, values):
                try:
                    measurements["device_currents"][device.upper()] = float(value)
                except ValueError:
                    continue

    measurements["node_voltages"].setdefault("0", 0.0)
    measurements["status"] = "loaded"
    return measurements


def transient_node_id(column_name: str) -> str | None:
    """Ricava il nodo SPICE da una colonna CSV nel formato `v(N001)`."""
    match = re.fullmatch(r"v\(([^)]+)\)", str(column_name).strip(), flags=re.IGNORECASE)
    return normalize_node(match.group(1)) if match else None


def transient_device_current_id(column_name: str) -> str | None:
    """Ricava il dispositivo da colonne `@D...[id]` oppure `i(D...)`."""
    text = str(column_name).strip()
    parameter_match = re.fullmatch(r"@([^\[]+)\[id\]", text, flags=re.IGNORECASE)
    if parameter_match:
        return parameter_match.group(1).upper()
    current_match = re.fullmatch(r"i\(([^)]+)\)", text, flags=re.IGNORECASE)
    return current_match.group(1).upper() if current_match else None


def numeric_series_span(values: list[float]) -> dict[str, float | bool]:
    """Riassume intervallo e attraversamento dello zero di una serie numerica."""
    if not values:
        return {"min": 0.0, "max": 0.0, "span": 0.0, "crosses_zero": False}
    minimum = min(values)
    maximum = max(values)
    return {
        "min": minimum,
        "max": maximum,
        "span": maximum - minimum,
        "crosses_zero": minimum < -TRANSIENT_VARIATION_EPSILON and maximum > TRANSIENT_VARIATION_EPSILON,
    }


def component_transient_activity(
    components: list[dict[str, Any]],
    node_series: dict[str, list[float]],
) -> dict[str, dict[str, Any]]:
    """Stima l'attivita' variabile di ogni componente dalle tensioni ai terminali."""
    activity: dict[str, dict[str, Any]] = {}
    for component in components:
        component_id = str(component.get("id") or "")
        nodes = [str(node_id) for node_id in component.get("nodes") or []]
        available = [node_id for node_id in nodes if node_id in node_series]
        if not component_id or len(available) < 2:
            continue

        # Per i bipoli usa la tensione differenziale; per i componenti a piu'
        # terminali conserva la coppia con la variazione maggiore.
        best: dict[str, Any] | None = None
        for first_index, first_node in enumerate(available):
            for second_node in available[first_index + 1 :]:
                differences = [
                    first - second
                    for first, second in zip(node_series[first_node], node_series[second_node])
                ]
                summary = numeric_series_span(differences)
                candidate = {
                    **summary,
                    "nodes": [first_node, second_node],
                }
                if best is None or float(candidate["span"]) > float(best["span"]):
                    best = candidate

        if best is None:
            continue
        variable = float(best["span"]) >= TRANSIENT_VARIATION_EPSILON
        kind = str(component.get("kind") or "").lower()
        source_id = str(component.get("source_component_id") or "").lower()
        alternating = bool(best["crosses_zero"]) or kind == "capacitor" or "signal_source" in source_id
        activity[component_id] = {
            **best,
            "variable": variable,
            "flow_mode": "alternating" if variable and alternating else "pulsating" if variable else "steady",
        }
    return activity


def is_led_component(component: dict[str, Any]) -> bool:
    """Riconosce i LED distinguendoli dai diodi privi di emissione luminosa."""
    viewer_kind = str(component.get("viewer_kind") or "").strip().lower()
    if viewer_kind:
        # La semantica risolta dal values.yaml prevale sulla classe riconosciuta
        # nell'immagine. In particolare, un simbolo rilevato come LED ma corretto
        # a diodo non deve produrre un profilo di lampeggio diagnostico.
        return viewer_kind in {"led", "indicator_led", "light_emitting_diode"}
    source_id = str(component.get("source_component_id") or "").lower()
    return str(component.get("kind") or "").lower() == "diode" and source_id.startswith("led")


def led_on_durations(
    times: list[float],
    states: list[bool],
    rising_indices: list[int],
) -> list[float]:
    """Misura la durata di ogni impulso acceso che inizia nel transitorio."""
    durations: list[float] = []
    for rising_index in rising_indices:
        falling_index = next(
            (
                index
                for index in range(rising_index + 1, len(states))
                if not states[index]
            ),
            None,
        )
        if falling_index is not None:
            durations.append(max(0.0, times[falling_index] - times[rising_index]))
    return durations


def led_state_timeline(times: list[float], states: list[bool]) -> tuple[list[float], list[bool]]:
    """Compatta le commutazioni LED in una timeline normalizzata fra 0 e 1."""
    if not times or not states or len(times) != len(states):
        return [], []
    time_start = times[0]
    time_span = max(times[-1] - time_start, 1e-12)
    key_times = [0.0]
    key_states = [states[0]]
    for index in range(1, len(states)):
        if states[index] == states[index - 1]:
            continue
        normalized_time = min(1.0, max(0.0, (times[index] - time_start) / time_span))
        if normalized_time <= key_times[-1]:
            key_states[-1] = states[index]
            continue
        key_times.append(normalized_time)
        key_states.append(states[index])
    if key_times[-1] < 1.0:
        key_times.append(1.0)
        key_states.append(key_states[-1])
    return key_times, key_states


def led_branch_control_signal(
    led_component: dict[str, Any],
    components: list[dict[str, Any]],
    node_series: dict[str, list[float]],
) -> dict[str, Any] | None:
    """
    Ricava un segnale del ramo LED quando il solo diodo ha un modello troppo semplice.

    Un LED in serie a una resistenza puo' conservare una piccola caduta diretta
    anche quando il ramo e' quasi spento. Se al suo anodo o catodo e' collegata
    una resistenza variabile verso un nodo remoto, la tensione dell'intero ramo
    e' una misura piu fedele della commutazione. La scelta e' topologica e non
    dipende da identificatori, circuiti o batch specifici.
    """
    led_nodes = [normalize_node(node_id) for node_id in led_component.get("nodes") or []]
    if len(led_nodes) < 2:
        return None
    anode_node, cathode_node = led_nodes[:2]
    anode_values = node_series.get(anode_node)
    cathode_values = node_series.get(cathode_node)
    if not anode_values or not cathode_values:
        return None

    cathode_candidates: list[dict[str, Any]] = []
    anode_candidates: list[dict[str, Any]] = []
    for candidate in components:
        if candidate is led_component or str(candidate.get("kind") or "").lower() != "resistor":
            continue
        candidate_nodes = [normalize_node(node_id) for node_id in candidate.get("nodes") or []]
        if len(candidate_nodes) != 2:
            continue

        remote_node: str | None = None
        signal_values: list[float] | None = None
        side: str | None = None
        if cathode_node in candidate_nodes and anode_node not in candidate_nodes:
            remote_node = candidate_nodes[1] if candidate_nodes[0] == cathode_node else candidate_nodes[0]
            remote_values = node_series.get(remote_node)
            if remote_values:
                signal_values = [anode - remote for anode, remote in zip(anode_values, remote_values)]
                side = "cathode"
        elif anode_node in candidate_nodes and cathode_node not in candidate_nodes:
            remote_node = candidate_nodes[1] if candidate_nodes[0] == anode_node else candidate_nodes[0]
            remote_values = node_series.get(remote_node)
            if remote_values:
                signal_values = [remote - cathode for remote, cathode in zip(remote_values, cathode_values)]
                side = "anode"
        if not signal_values or remote_node is None or side is None:
            continue

        span = max(signal_values) - min(signal_values)
        candidate_data = {
            "values": signal_values,
            "span": span,
            "series_component_id": str(candidate.get("id") or ""),
            "control_node": remote_node,
            "series_side": side,
        }
        if side == "cathode":
            cathode_candidates.append(candidate_data)
        else:
            anode_candidates.append(candidate_data)

    # Il lato catodo e' preferito: in una catena VCC -> LED -> R -> carico
    # evita di scambiare una resistenza di bias con la resistenza in serie LED.
    candidates = cathode_candidates or anode_candidates
    best_candidate = max(candidates, key=lambda item: float(item["span"]), default=None)
    if best_candidate is None or float(best_candidate["span"]) < LED_BRANCH_SIGNAL_MIN_SPAN_V:
        return None
    return best_candidate


def led_transient_profiles(
    components: list[dict[str, Any]],
    times: list[float],
    node_series: dict[str, list[float]],
    device_current_series: dict[str, list[float]] | None = None,
) -> dict[str, dict[str, Any]]:
    """Ricava lampeggio e duty cycle LED privilegiando la corrente diretta."""
    profiles: dict[str, dict[str, Any]] = {}
    current_series = device_current_series or {}
    if len(times) < 2:
        return profiles

    time_window = max(0.0, times[-1] - times[0])
    for component in components:
        if not is_led_component(component):
            continue
        component_id = str(component.get("id") or "")
        nodes = [normalize_node(node_id) for node_id in component.get("nodes") or []]
        if not component_id or len(nodes) < 2:
            continue
        anode_values = node_series.get(nodes[0])
        cathode_values = node_series.get(nodes[1])
        if not anode_values or not cathode_values:
            continue

        forward_voltages = [
            anode - cathode
            for anode, cathode in zip(anode_values, cathode_values)
        ]
        aliases = {
            str(component.get("id") or "").upper(),
            str(component.get("spice_name") or "").upper(),
        }
        measured_currents = next(
            (
                values for alias in aliases
                if alias and (values := current_series.get(alias)) and len(values) == len(times)
            ),
            None,
        )
        branch_control: dict[str, Any] | None = None
        threshold_v: float | None = None
        turn_on_current_a: float | None = None
        turn_off_current_a: float | None = None
        if measured_currents is not None:
            # La corrente diretta e' la misura fisica della luce emessa. Evita
            # falsi positivi quando il LED conserva Vf ma conduce solo leakage.
            # L'isteresi evita inoltre di contare il chattering numerico vicino
            # alla soglia come un lampeggio ad alta frequenza.
            states, turn_on_current_a, turn_off_current_a = led_current_states_with_hysteresis(
                measured_currents
            )
            current_min = min(measured_currents)
            current_max = max(measured_currents)
            uses_hysteresis = (
                current_min < LED_VISIBLE_CURRENT_A <= current_max
                or (
                    current_max >= LED_VISIBLE_CURRENT_A
                    and current_min <= 0.25 * current_max
                    and current_max - current_min >= LED_VISIBLE_CURRENT_A
                )
            )
            profile_method = "device_current_hysteresis" if uses_hysteresis else "device_current"
        else:
            states = [voltage >= LED_FORWARD_THRESHOLD_V for voltage in forward_voltages]
            profile_method = "terminal_forward_voltage"
            threshold_v = LED_FORWARD_THRESHOLD_V
            branch_control = led_branch_control_signal(component, components, node_series)
            if branch_control is not None:
                branch_values = list(branch_control["values"])
                # Il punto medio e' relativo al ramo osservato: evita di imporre una
                # soglia assoluta a LED con modelli o alimentazioni differenti.
                threshold_v = (min(branch_values) + max(branch_values)) / 2.0
                states = [value >= threshold_v for value in branch_values]
                profile_method = "series_branch_voltage"
        if not states:
            continue
        rising_indices = [
            index
            for index, state in enumerate(states)
            if state and (index == 0 or not states[index - 1])
        ]
        on_fraction = sum(states) / len(states)
        periods = [
            times[current] - times[previous]
            for previous, current in zip(rising_indices, rising_indices[1:])
            if times[current] > times[previous]
        ]
        period_candidate = median(periods) if periods else None
        coherent_periods = [
            current_period
            for current_period in periods
            if period_candidate
            and abs(current_period - period_candidate) / period_candidate
            <= LED_PERIOD_RELATIVE_TOLERANCE
        ]
        regular_period = bool(
            period_candidate
            and len(coherent_periods) >= 2
            # La prima semionda puo' essere intenzionalmente diversa per una
            # condizione iniziale; il resto del transitorio deve restare quasi
            # interamente periodico prima di dichiarare il lampeggio regolare.
            and len(coherent_periods) / len(periods) >= 0.75
        )
        period = period_candidate if regular_period else None
        durations = led_on_durations(times, states, rising_indices)
        duty_cycle = (
            min(1.0, max(0.0, median(durations) / period))
            if period and durations
            else on_fraction
        )

        if not any(states):
            state = "off"
        elif all(states):
            state = "steady_on"
        elif period:
            state = "blinking"
        else:
            state = "transient_pulse"

        reference_duration = period if period else time_window
        playback_duration = min(6.0, max(0.8, reference_duration * LED_PLAYBACK_SLOWDOWN))
        # La radice quadrata mantiene visibili gli impulsi brevi senza rendere
        # uguali duty cycle reali molto diversi tra loro.
        display_duty_cycle = min(0.8, 0.08 + 0.8 * (duty_cycle ** 0.5))
        timeline_key_times, timeline_states = led_state_timeline(times, states)
        profiles[component_id] = {
            "status": "measured",
            "state": state,
            "threshold_v": threshold_v,
            "profile_method": profile_method,
            "anode_node": nodes[0],
            "cathode_node": nodes[1],
            "on_fraction": on_fraction,
            "duty_cycle": duty_cycle,
            "display_duty_cycle": display_duty_cycle,
            "regular_period": regular_period,
            "period_s": period,
            "frequency_hz": (1.0 / period) if period else None,
            "playback_duration_s": playback_duration,
            "playback_slowdown": LED_PLAYBACK_SLOWDOWN,
            "pulse_count": len(rising_indices),
            "timeline_key_times": timeline_key_times,
            "timeline_states": timeline_states,
            "voltage_min": min(forward_voltages),
            "voltage_max": max(forward_voltages),
        }
        if measured_currents is not None:
            profiles[component_id].update(
                {
                    "threshold_current_a": LED_VISIBLE_CURRENT_A,
                    "current_min_a": min(measured_currents),
                    "current_max_a": max(measured_currents),
                }
            )
            if profile_method == "device_current_hysteresis":
                profiles[component_id].update(
                    {
                        "turn_on_current_a": turn_on_current_a,
                        "turn_off_current_a": turn_off_current_a,
                    }
                )
        if branch_control is not None:
            profiles[component_id].update(
                {
                    "branch_signal_min": min(branch_control["values"]),
                    "branch_signal_max": max(branch_control["values"]),
                    "series_component_id": branch_control["series_component_id"],
                    "control_node": branch_control["control_node"],
                    "series_side": branch_control["series_side"],
                }
            )
    return profiles


def is_profiled_pulsating_load(component: dict[str, Any]) -> bool:
    """Riconosce carichi visivi a due terminali per cui il ritmo e significativo.

    La selezione usa solo metadati semantici gia presenti nel modello viewer;
    non dipende da identificatori, batch o modelli SPICE specifici.
    """
    viewer_kind = str(component.get("viewer_kind") or "").strip().lower()
    class_name = str(component.get("class_name") or "").strip().lower()
    parameters = component.get("parameters") if isinstance(component.get("parameters"), dict) else {}
    spice_override = (
        parameters.get("spice_override")
        if isinstance(parameters.get("spice_override"), dict)
        else {}
    )
    semantic_role = str(spice_override.get("semantic_role") or "").strip().lower()
    return (
        viewer_kind in {"lamp", "indicator_lamp"}
        or class_name in {"lamp", "indicator lamp"}
        or semantic_role in {"lamp", "lamp_equivalent", "indicator_lamp"}
    )


def pulsating_load_transient_profiles(
    components: list[dict[str, Any]],
    times: list[float],
    node_series: dict[str, list[float]],
) -> dict[str, dict[str, Any]]:
    """Misura stato, periodo e duty cycle dei carichi visivi pulsanti.

    Per un carico a due terminali usa il modulo della tensione differenziale e
    una soglia relativa a meta dell'escursione misurata. Questo rende il profilo
    valido anche per carichi non riferiti direttamente a massa e non impone una
    soglia elettrica specifica del componente.
    """
    profiles: dict[str, dict[str, Any]] = {}
    if len(times) < 2:
        return profiles

    time_window = max(0.0, times[-1] - times[0])
    for component in components:
        if not is_profiled_pulsating_load(component):
            continue
        component_id = str(component.get("id") or "")
        nodes = [normalize_node(node_id) for node_id in component.get("nodes") or []]
        if not component_id or len(nodes) != 2:
            continue
        positive_values = node_series.get(nodes[0])
        negative_values = node_series.get(nodes[1])
        if not positive_values or not negative_values:
            continue

        differential_voltages = [
            positive - negative
            for positive, negative in zip(positive_values, negative_values)
        ]
        voltage_magnitudes = [abs(value) for value in differential_voltages]
        if not voltage_magnitudes:
            continue
        magnitude_min = min(voltage_magnitudes)
        magnitude_max = max(voltage_magnitudes)
        if magnitude_max - magnitude_min < TRANSIENT_VARIATION_EPSILON:
            continue
        threshold_v = magnitude_min + 0.5 * (magnitude_max - magnitude_min)
        states = [value >= threshold_v for value in voltage_magnitudes]
        rising_indices = [
            index
            for index, state in enumerate(states)
            if state and (index == 0 or not states[index - 1])
        ]
        periods = [
            times[current] - times[previous]
            for previous, current in zip(rising_indices, rising_indices[1:])
            if times[current] > times[previous]
        ]
        period_candidate = median(periods) if periods else None
        coherent_periods = [
            current_period
            for current_period in periods
            if period_candidate
            and abs(current_period - period_candidate) / period_candidate
            <= LED_PERIOD_RELATIVE_TOLERANCE
        ]
        regular_period = bool(
            period_candidate
            and len(coherent_periods) >= 2
            and len(coherent_periods) / len(periods) >= 0.75
        )
        period = period_candidate if regular_period else None
        on_fraction = sum(states) / len(states)
        durations = led_on_durations(times, states, rising_indices)
        duty_cycle = (
            min(1.0, max(0.0, median(durations) / period))
            if period and durations
            else on_fraction
        )
        if not any(states):
            state = "off"
        elif all(states):
            state = "steady_on"
        elif period:
            state = "blinking"
        else:
            state = "transient_pulse"

        timeline_key_times, timeline_states = led_state_timeline(times, states)
        profiles[component_id] = {
            "status": "measured",
            "source_component_id": str(component.get("source_component_id") or ""),
            "state": state,
            "profile_method": "differential_voltage_relative_threshold",
            "positive_node": nodes[0],
            "negative_node": nodes[1],
            "threshold_v": threshold_v,
            "on_fraction": on_fraction,
            "duty_cycle": duty_cycle,
            "regular_period": regular_period,
            "period_s": period,
            "frequency_hz": (1.0 / period) if period else None,
            "pulse_count": len(rising_indices),
            "timeline_key_times": timeline_key_times,
            "timeline_states": timeline_states,
            "voltage_min": min(differential_voltages),
            "voltage_max": max(differential_voltages),
            "voltage_magnitude_min": magnitude_min,
            "voltage_magnitude_max": magnitude_max,
            "time_window_s": time_window,
        }
    return profiles


def downsample_indices(sample_count: int, maximum: int) -> list[int]:
    """Seleziona indici equidistanti preservando primo e ultimo campione."""
    if sample_count <= maximum:
        return list(range(sample_count))
    return sorted(
        {
            round(index * (sample_count - 1) / (maximum - 1))
            for index in range(maximum)
        }
    )


def build_transient_traces(
    times: list[float],
    node_series: dict[str, list[float]],
) -> dict[str, Any]:
    """Prepara serie compatte conservando il tempo reale di ogni campione."""
    indices = downsample_indices(len(times), MAX_TRANSIENT_VIEWER_SAMPLES)
    return {
        "time": [times[index] for index in indices],
        "series": {
            f"v({node_id})": [values[index] for index in indices]
            for node_id, values in node_series.items()
            if node_id != "0" and len(values) == len(times)
        },
    }


def parse_transient_csv(
    csv_path: Path,
    components: list[dict[str, Any]],
) -> dict[str, Any]:
    """Legge `08_tran.csv` e produce un riepilogo leggero per il viewer."""
    if not csv_path.exists():
        return {"status": "missing", "component_activity": {}}

    node_series: dict[str, list[float]] = {}
    device_current_series: dict[str, list[float]] = {}
    times: list[float] = []
    try:
        with csv_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            columns = {
                column: transient_node_id(column)
                for column in (reader.fieldnames or [])
                if transient_node_id(column)
            }
            current_columns = {
                column: transient_device_current_id(column)
                for column in (reader.fieldnames or [])
                if transient_device_current_id(column)
            }
            for node_id in columns.values():
                if node_id:
                    node_series.setdefault(node_id, [])
            node_series.setdefault("0", [])
            for device_id in current_columns.values():
                if device_id:
                    device_current_series.setdefault(device_id, [])

            for row in reader:
                try:
                    time_value = float(row.get("time") or row.get("Time") or "")
                except (TypeError, ValueError):
                    continue
                sample_values: dict[str, float] = {}
                sample_currents: dict[str, float] = {}
                try:
                    for column, node_id in columns.items():
                        if node_id:
                            sample_values[node_id] = float(row.get(column) or "")
                    for column, device_id in current_columns.items():
                        if device_id:
                            sample_currents[device_id] = float(row.get(column) or "")
                except (TypeError, ValueError):
                    continue
                times.append(time_value)
                for node_id, value in sample_values.items():
                    node_series[node_id].append(value)
                for device_id, value in sample_currents.items():
                    device_current_series[device_id].append(value)
                node_series["0"].append(0.0)
    except (OSError, csv.Error):
        return {"status": "invalid", "component_activity": {}}

    node_activity = {
        node_id: numeric_series_span(values)
        for node_id, values in node_series.items()
        if values
    }
    transient = {
        "status": "loaded" if times else "empty",
        "sample_count": len(times),
        "time_start": times[0] if times else None,
        "time_end": times[-1] if times else None,
        "node_activity": node_activity,
        "device_current_activity": {
            device_id: numeric_series_span(values)
            for device_id, values in device_current_series.items()
            if values
        },
        "component_activity": component_transient_activity(components, node_series),
        "led_profiles": led_transient_profiles(
            components,
            times,
            node_series,
            device_current_series,
        ),
        "traces": build_transient_traces(times, node_series),
    }
    load_profiles = pulsating_load_transient_profiles(
        components,
        times,
        node_series,
    )
    if load_profiles:
        transient["load_profiles"] = load_profiles
    return transient


def select_transient_quantities(
    transient: dict[str, Any],
    scenario: dict[str, Any] | None,
) -> list[str]:
    """Sceglie le tracce dal `compare` o dalle tre variazioni maggiori."""
    series = ((transient.get("traces") or {}).get("series") or {})
    available = {str(name).lower(): str(name) for name in series}
    selected: list[str] = []
    compare = scenario.get("compare") if isinstance(scenario, dict) else []
    for quantity in compare if isinstance(compare, list) else []:
        canonical = available.get(str(quantity).strip().lower())
        if canonical and canonical not in selected:
            selected.append(canonical)
        if len(selected) == 3:
            return selected

    if selected:
        return selected
    node_activity = transient.get("node_activity") or {}
    ranked_nodes = sorted(
        (
            (str(node_id), float(activity.get("span") or 0.0))
            for node_id, activity in node_activity.items()
            if node_id != "0" and isinstance(activity, dict)
        ),
        key=lambda item: (-item[1], item[0]),
    )
    variable_traces = [
        available[f"v({node_id})".lower()]
        for node_id, span in ranked_nodes
        if span >= TRANSIENT_VARIATION_EPSILON and f"v({node_id})".lower() in available
    ][:3]
    if variable_traces:
        return variable_traces

    # Una run perfettamente simmetrica puo' avere solo tracce piatte. Il
    # grafico resta comunque informativo e non deve sparire dalla web chat.
    return [
        available[f"v({node_id})".lower()]
        for node_id, _span in ranked_nodes
        if f"v({node_id})".lower() in available
    ][:3]


def attach_transient_scope_data(
    transient: dict[str, Any],
    scenario: dict[str, Any] | None,
    scenario_dir: Path | None,
    components: list[dict[str, Any]],
) -> dict[str, Any]:
    """Aggiunge selezione scope e confronto base alla run corrente."""
    transient["selected_traces"] = select_transient_quantities(transient, scenario)
    transient["steady_start"] = (
        float(transient.get("time_start") or 0.0)
        + (float(transient.get("time_end") or 0.0) - float(transient.get("time_start") or 0.0)) * 0.2
    )
    if not scenario_dir:
        return transient

    base_csv = scenario_dir / "base_snapshot" / "08_tran.csv"
    base_transient = parse_transient_csv(base_csv, components)
    selected = transient["selected_traces"]
    base_traces = base_transient.get("traces") or {}
    base_series = base_traces.get("series") or {}
    transient["base_traces"] = {
        "time": base_traces.get("time") or [],
        "series": {
            quantity: base_series[quantity]
            for quantity in selected
            if quantity in base_series
        },
    }
    return transient


def measurement_voltage(
    nodes: dict[str, Any],
    measurements: dict[str, Any],
) -> float | None:
    """Calcola la lettura di un voltmetro differenziale dalle tensioni OP."""
    node_voltages = measurements.get("node_voltages") or {}
    ordered_nodes = [normalize_node(node_id) for node_id in nodes.values()]
    if len(ordered_nodes) < 2:
        return None
    first = node_voltages.get(ordered_nodes[0])
    second = node_voltages.get(ordered_nodes[1])
    if first is None or second is None:
        return None
    try:
        return float(first) - float(second)
    except (TypeError, ValueError):
        return None


def transient_measurement_voltage(
    nodes: dict[str, Any],
    transient: dict[str, Any],
) -> float | None:
    """Calcola il Vpp differenziale di un voltmetro usando le tracce transitorie."""
    ordered_nodes = [normalize_node(node_id) for node_id in nodes.values()]
    if len(ordered_nodes) < 2:
        return None
    series = ((transient.get("traces") or {}).get("series") or {})

    def node_series(node_id: str) -> list[float] | None:
        """Restituisce la traccia del nodo, usando una massa implicita a zero."""
        if node_id == "0":
            sample_count = len(next(iter(series.values()), []))
            return [0.0] * sample_count
        values = series.get(f"v({node_id})")
        return values if isinstance(values, list) else None

    first = node_series(ordered_nodes[0])
    second = node_series(ordered_nodes[1])
    if not first or not second or len(first) != len(second):
        return None
    differential = [float(left) - float(right) for left, right in zip(first, second)]
    return max(differential) - min(differential) if differential else None


def build_structural_components(
    node_map: dict[str, Any],
    rules: dict[str, Any],
    measurements: dict[str, Any],
    transient: dict[str, Any],
) -> list[dict[str, Any]]:
    """Costruisce componenti strutturali e strumenti di misura non emessi in SPICE."""
    terminal_nodes = node_map.get("component_terminal_nodes") or {}
    components = rules.get("components") or {}
    structural: list[dict[str, Any]] = []

    for component_id, rule in components.items():
        if not isinstance(rule, dict):
            continue
        class_name = str(rule.get("class_name") or "Component")
        status = str(rule.get("status") or "")
        support = str(rule.get("spice_support") or "")
        emit_as = rule.get("emit_as")
        is_structural = status == "not_emitted" or support == "structural" or emit_as is None
        is_measurement = status == "measurement_only" or support == "measurement"
        if not is_structural and not is_measurement:
            continue
        parameters = dict(rule.get("parameters") or {})
        nodes = terminal_nodes.get(component_id) or rule.get("nodes") or {}
        measurement_kind = str(rule.get("measurement_kind") or parameters.get("kind") or "").lower()
        is_voltage_meter = measurement_kind == "voltage" or parameters.get("kind") == "voltmeter"
        measured_quantity = str(parameters.get("measured_quantity") or "").strip().lower()
        transient_reading = (
            transient_measurement_voltage(nodes, transient)
            if is_voltage_meter and measured_quantity in {"voltage_ac", "ac_voltage", "vac"}
            else None
        )
        reading = transient_reading if transient_reading is not None else (
            measurement_voltage(nodes, measurements) if is_voltage_meter else None
        )
        measurement_mode = "tran_vpp" if transient_reading is not None else "op"
        structural.append(
            {
                "id": component_id,
                "class_name": class_name,
                "nodes": nodes,
                "status": status,
                "spice_support": support,
                "parameters": parameters,
                "display_label": parameters.get("label_text") or parameters.get("label"),
                "measurement_kind": measurement_kind or None,
                "measurement_value": reading,
                "measurement_unit": "V" if reading is not None else None,
                "measurement_mode": measurement_mode if is_voltage_meter else None,
                "strategy": rule.get("strategy"),
                "reason": rule.get("reason"),
            }
        )

    return structural


def apply_manual_viewer_overrides(
    components: list[dict[str, Any]],
    values_bound: dict[str, Any],
) -> list[dict[str, Any]]:
    """Applica override visuali espliciti senza modificare la semantica SPICE."""
    bound_components = values_bound.get("components") or {}
    updated: list[dict[str, Any]] = []
    for component in components:
        item = dict(component)
        source_id = str(item.get("source_component_id") or item.get("id") or "")
        value_entry = bound_components.get(source_id) or {}
        value_data = value_entry.get("value_data") if isinstance(value_entry, dict) else {}
        override = value_data.get("viewer_override") if isinstance(value_data, dict) else {}
        if isinstance(override, dict) and override:
            # Un override puo' intervenire solo su label o tooltip: il simbolo
            # non deve essere obbligatorio per applicare tali metadati visuali.
            if override.get("visual_class"):
                item["viewer_kind"] = str(override["visual_class"])
            item["viewer_override"] = dict(override)
            if override.get("label") is not None:
                item["viewer_label"] = str(override.get("label") or "")
            if override.get("display_value") is not None:
                item["viewer_value"] = str(override.get("display_value") or "")
            if override.get("label_mode") is not None:
                item["viewer_label_mode"] = str(override.get("label_mode") or "")
            if override.get("tooltip") is not None:
                item["viewer_tooltip"] = str(override.get("tooltip") or "")
            if override.get("include_graph_terminals"):
                terminal_nodes = value_entry.get("terminal_nodes") if isinstance(value_entry, dict) else {}
                if isinstance(terminal_nodes, dict) and terminal_nodes:
                    item["simulation_nodes"] = list(item.get("nodes") or [])
                    item["nodes"] = [str(node) for node in terminal_nodes.values()]
                    item["terminal_names"] = [str(name) for name in terminal_nodes]
        updated.append(item)
    return updated


def remove_emitted_simplified_duplicates(
    structural_components: list[dict[str, Any]],
    netlist_components: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Evita di disegnare due volte un componente semplificato gia' emesso."""
    emitted_source_ids = {
        str(component.get("source_component_id") or "")
        for component in netlist_components
        if component.get("source_component_id")
    }
    return [
        component
        for component in structural_components
        if not (
            str(component.get("spice_support") or "") == "simplified"
            and str(component.get("id") or "") in emitted_source_ids
        )
    ]


def scenario_closed_switches(scenario: dict[str, Any], components: list[dict[str, Any]]) -> set[str]:
    """Trova gli switch chiusi da uno scenario, usando azioni e netlist emessa."""
    closed: set[str] = set()
    actions = scenario.get("actions") if isinstance(scenario, dict) else []
    if isinstance(actions, list):
        for action in actions:
            if not isinstance(action, dict):
                continue
            if action.get("type") == "close_switch" and action.get("target"):
                closed.add(str(action["target"]))

    for component in components:
        source_id = str(component.get("source_component_id") or "")
        if component.get("is_scenario_added") and source_id.startswith("scenario_switch"):
            closed.add(source_id.removeprefix("scenario_"))
    return closed


def apply_scenario_visual_overrides(
    structural: list[dict[str, Any]],
    scenario: dict[str, Any],
    components: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Aggiorna lo stato visivo dei componenti strutturali modificati dallo scenario."""
    closed_switches = scenario_closed_switches(scenario, components)
    if not closed_switches:
        return structural

    updated: list[dict[str, Any]] = []
    for component in structural:
        item = dict(component)
        if str(item.get("id")) in closed_switches:
            parameters = dict(item.get("parameters") or {})
            parameters["state"] = "closed"
            parameters["state_source"] = "scenario_close_switch"
            item["parameters"] = parameters
            item["viewer_state"] = "closed_by_scenario"
        updated.append(item)
    return updated


def apply_scenario_component_roles(
    components: list[dict[str, Any]],
    scenario: dict[str, Any],
) -> list[dict[str, Any]]:
    """Distingue i componenti fisici dagli equivalenti numerici degli scenari."""
    connection_pairs: set[frozenset[str]] = set()
    voltage_clamps: dict[str, Any] = {}
    actions = scenario.get("actions") if isinstance(scenario, dict) else []
    for action in actions if isinstance(actions, list) else []:
        if not isinstance(action, dict):
            continue
        if action.get("type") == "drive_node_voltage" and action.get("target"):
            voltage_clamps[normalize_node(str(action["target"]))] = action.get("value")
            continue
        if action.get("type") not in {"connect_nodes", "feed_nodes_from_source_node"}:
            continue
        first = str(action.get("from") or action.get("source_node") or "")
        targets = action.get("target_nodes") or [action.get("to") or action.get("target_node")]
        for target in targets if isinstance(targets, list) else []:
            second = str(target or "")
            if first and second:
                connection_pairs.add(frozenset({normalize_node(first), normalize_node(second)}))

    updated: list[dict[str, Any]] = []
    for component in components:
        item = dict(component)
        component_nodes = frozenset(str(node_id) for node_id in item.get("nodes") or [])
        if item.get("is_scenario_added") and component_nodes in connection_pairs:
            item["viewer_kind"] = "connection"
            item["viewer_label"] = "link"
            item["viewer_reason"] = "scenario_numeric_continuity_element"
        if item.get("is_scenario_added") and item.get("kind") == "voltage_source":
            target_node = next(
                (
                    node_id for node_id in item.get("nodes") or []
                    if normalize_node(str(node_id)) in voltage_clamps
                ),
                None,
            )
            if target_node and "0" in {normalize_node(str(node_id)) for node_id in item.get("nodes") or []}:
                normalized_target = normalize_node(str(target_node))
                item["viewer_kind"] = "node_voltage_clamp"
                item["viewer_role"] = "scenario_control_constraint"
                item["viewer_target_node"] = normalized_target
                item["viewer_forced_value"] = voltage_clamps[normalized_target]
                item["viewer_reason"] = "drive_node_voltage_ideal_spice_source"
        updated.append(item)
    return updated


def mark_scenario_modified_components(
    components: list[dict[str, Any]],
    scenario: dict[str, Any],
    scenario_dir: Path | None,
) -> list[dict[str, Any]]:
    """Marca sorgenti e componenti modificati conservando il valore della base run."""
    actions = scenario.get("actions") if isinstance(scenario, dict) else []
    changed_values = {
        str(action.get("target") or "").lower(): action.get("value")
        for action in actions if isinstance(actions, list) and isinstance(action, dict)
        if action.get("type") in {"change_source_value", "change_component_value"} and action.get("target")
    }
    if not changed_values:
        return components

    base_components: list[dict[str, Any]] = []
    if scenario_dir:
        base_components, _, _ = parse_netlist(scenario_dir / "base_snapshot" / NETLIST_NAME)
    base_by_name = {
        str(component.get("spice_name") or component.get("id") or "").lower(): component
        for component in base_components
    }

    updated: list[dict[str, Any]] = []
    for component in components:
        item = dict(component)
        aliases = {
            str(item.get("id") or "").lower(),
            str(item.get("spice_name") or "").lower(),
            str(item.get("source_component_id") or "").lower(),
        }
        target = next((name for name in aliases if name in changed_values), None)
        if target:
            base_component = base_by_name.get(str(item.get("spice_name") or "").lower()) or {}
            item["is_scenario_modified"] = True
            item["scenario_previous_value"] = base_component.get("value")
            item["scenario_value"] = item.get("value") or changed_values[target]
        updated.append(item)
    return updated


def compact_source_value(value: Any, unit: str = "V") -> str:
    """Converte un valore di sorgente SPICE in una label visuale compatta."""
    text = str(value or "").strip()
    match = re.fullmatch(r"(?:DC\s+)?([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[a-zA-Z]+)?)", text, re.IGNORECASE)
    if not match:
        return text
    scalar = match.group(1)
    return scalar if scalar.lower().endswith(unit.lower()) else f"{scalar} {unit}"


def enrich_structural_terminals(
    structural: list[dict[str, Any]],
    components: list[dict[str, Any]],
    rules: dict[str, Any],
    values_bound: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Aggiunge label ai terminali e fonde le alimentazioni SPICE equivalenti."""
    node_labels = values_bound.get("nodes") or {}
    supplies = rules.get("supplies") or values_bound.get("supplies") or {}
    netlist = [dict(component) for component in components]
    enriched: list[dict[str, Any]] = []

    for component in structural:
        item = dict(component)
        component_id = str(item.get("id") or "")
        if "terminal" not in str(item.get("class_name") or "").lower():
            enriched.append(item)
            continue

        item["viewer_kind"] = "terminal"
        terminal_label = next(
            (
                data for terminal_id, data in node_labels.items()
                if str(terminal_id).startswith(f"{component_id}_") and isinstance(data, dict)
            ),
            {},
        )
        terminal_nodes = list((item.get("nodes") or {}).values())
        item["display_label"] = (
            terminal_label.get("label")
            or terminal_label.get("label_text")
            or (str(terminal_nodes[0]) if terminal_nodes else "PORT")
        )

        for supply_name, supply in supplies.items():
            if not isinstance(supply, dict):
                continue
            parameters = supply.get("parameters") if isinstance(supply.get("parameters"), dict) else supply
            terminal_id = str(parameters.get("terminal") or "")
            return_terminal_id = str(parameters.get("return_terminal") or "")
            viewer_override = parameters.get("viewer_override")
            viewer_override = viewer_override if isinstance(viewer_override, dict) else {}
            is_primary_terminal = bool(
                terminal_id and terminal_id.startswith(f"{component_id}_")
            )
            is_return_terminal = bool(
                return_terminal_id
                and return_terminal_id.startswith(f"{component_id}_")
            )
            belongs_to_visual_source = is_primary_terminal or is_return_terminal
            if not belongs_to_visual_source:
                continue

            if viewer_override.get("visual_class") == "battery":
                # La batteria a due terminali sostituisce i due port esterni
                # soltanto nel viewer; i Terminal originali restano nel Graph.
                item["viewer_hidden"] = True
                if not terminal_id.startswith(f"{component_id}_"):
                    break

            expected_name = f"V{supply_name}".lower()
            supply_nodes = {normalize_node(node) for node in supply.get("nodes") or []}
            source = next(
                (
                    candidate for candidate in netlist
                    if str(candidate.get("spice_name") or "").lower() == expected_name
                ),
                None,
            )
            if source is None and supply_nodes:
                source = next(
                    (
                        candidate for candidate in netlist
                        if candidate.get("kind") == "voltage_source"
                        and {normalize_node(node) for node in candidate.get("nodes") or []} == supply_nodes
                    ),
                    None,
                )
            if source is None:
                continue

            if (
                viewer_override.get("visual_class") != "battery"
                and is_primary_terminal
            ):
                source["viewer_hidden_by_terminal"] = component_id
                item["is_supply_terminal"] = True
                item["supply_name"] = str(supply_name)
                item["viewer_primary_terminal_id"] = terminal_id
                item["display_label"] = str(
                    viewer_override.get("label")
                    if viewer_override.get("label") is not None
                    else supply_name
                )
                item["display_value"] = str(
                    viewer_override.get("display_value")
                    if viewer_override.get("display_value") is not None
                    else compact_source_value(
                        source.get("value"),
                        str(parameters.get("unit") or "V"),
                    )
                )
                if viewer_override.get("tooltip") is not None:
                    item["viewer_tooltip"] = str(viewer_override.get("tooltip") or "")
                for field in (
                    "is_scenario_modified",
                    "scenario_previous_value",
                    "scenario_value",
                ):
                    if source.get(field) is not None:
                        item[field] = source[field]
            elif is_return_terminal:
                # Il ritorno resta elettricamente parte della sorgente, ma nel
                # viewer non ripete nome e valore del segnale. Il port resta
                # visibile e il simbolo GND adiacente ne chiarisce il ruolo.
                item["is_supply_return_terminal"] = True
                item["viewer_label_hidden"] = True
            break
        enriched.append(item)

    return enriched, netlist


def build_nodes(
    node_map: dict[str, Any],
    measurements: dict[str, Any],
    values_bound: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Unisce node map, overlay SPICE e tensioni operative misurate."""
    voltages = measurements.get("node_voltages") or {}
    nodes: list[dict[str, Any]] = []
    for item in node_map.get("nodes") or []:
        if not isinstance(item, dict):
            continue
        node_id = normalize_node(str(item.get("node_id") or ""))
        if not node_id:
            continue
        lookup = node_id.lower().upper() if node_id != "0" else "0"
        nodes.append(
            {
                "id": node_id,
                "label": "GND" if node_id == "0" else node_id,
                "is_ground": node_id == "0",
                "voltage_op": voltages.get(lookup),
                "terminals": item.get("terminals") or [],
                "terminal_count": item.get("terminal_count"),
                "source_groups": item.get("source_groups") or [],
            }
        )

    indexed = {str(item.get("id") or ""): item for item in nodes}
    for overlay in (values_bound or {}).get("spice_topology_overlay") or []:
        if not isinstance(overlay, dict) or overlay.get("status") != "applied":
            continue
        terminal_id = str(overlay.get("terminal_id") or "")
        from_node = normalize_node(str(overlay.get("from_node") or ""))
        to_node = normalize_node(str(overlay.get("to_node") or ""))
        if not terminal_id or not to_node:
            continue
        source = indexed.get(from_node)
        if source:
            source["terminals"] = [item for item in source.get("terminals") or [] if str(item) != terminal_id]
            source["terminal_count"] = len(source["terminals"])
        target = indexed.get(to_node)
        if target is None:
            target = {
                "id": to_node,
                "label": to_node,
                "is_ground": False,
                "voltage_op": voltages.get(to_node),
                "terminals": [],
                "terminal_count": 0,
                "source_groups": ["spice_topology_overlay"],
            }
            nodes.append(target)
            indexed[to_node] = target
        if terminal_id not in target["terminals"]:
            target["terminals"].append(terminal_id)
        target["terminal_count"] = len(target["terminals"])
    return nodes


def infer_batch_id(run_dir: Path) -> str | None:
    """Ricava il batch dalla posizione della run dentro `outputs/pipeline2.0`."""
    parts = list(run_dir.resolve().parts)
    try:
        pipeline_index = parts.index("pipeline2.0")
    except ValueError:
        return None
    return parts[pipeline_index + 1] if pipeline_index + 1 < len(parts) else None


def normalize_bbox(value: Any) -> list[float] | None:
    """Valida una bbox nel formato `[x1, y1, x2, y2]`."""
    if not isinstance(value, list) or len(value) != 4:
        return None
    try:
        bbox = [float(item) for item in value]
    except (TypeError, ValueError):
        return None
    if bbox[2] <= bbox[0] or bbox[3] <= bbox[1]:
        return None
    return bbox


def index_estimated_components(terminal_estimates: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Indicizza le stime geometriche della Pipeline 1.0 per `instance_id`."""
    indexed: dict[str, dict[str, Any]] = {}
    for component in terminal_estimates.get("components") or []:
        if not isinstance(component, dict):
            continue
        instance_id = str(component.get("instance_id") or "")
        if instance_id:
            indexed[instance_id] = component
    return indexed


def index_estimated_terminals(estimated_component: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Indicizza i terminali usando sia il nome tecnico sia quello semantico."""
    indexed: dict[str, dict[str, Any]] = {}
    for terminal in estimated_component.get("terminals") or []:
        if not isinstance(terminal, dict):
            continue
        for field in ("name", "semantic_terminal_name", "display_name"):
            name = str(terminal.get(field) or "")
            if name:
                indexed[name] = terminal
    return indexed


def build_geometry_component(
    graph_component: dict[str, Any],
    estimated_component: dict[str, Any],
    terminal_nodes: dict[str, Any],
) -> dict[str, Any] | None:
    """Unisce bbox, terminali e nodi elettrici di un componente rilevato."""
    component_id = str(graph_component.get("component_id") or "")
    bbox = normalize_bbox(estimated_component.get("bbox"))
    if not component_id or bbox is None:
        return None

    estimated_terminals = index_estimated_terminals(estimated_component)
    component_node_map = terminal_nodes.get(component_id) or {}
    terminals: dict[str, dict[str, Any]] = {}

    # Il terminal graph fornisce gli id stabili; le stime forniscono le coordinate.
    for terminal in graph_component.get("terminals") or []:
        if not isinstance(terminal, dict):
            continue
        name = str(terminal.get("name") or "")
        estimate = estimated_terminals.get(name) or {}
        try:
            x = float(estimate.get("x"))
            y = float(estimate.get("y"))
        except (TypeError, ValueError):
            continue
        terminals[name] = {
            "id": str(terminal.get("terminal_id") or f"{component_id}_{name}"),
            "name": name,
            "relative_position": str(
                estimate.get("relative_position") or terminal.get("relative_position") or ""
            ),
            "x": x,
            "y": y,
            "node_id": normalize_node(str(component_node_map.get(name) or "")) or None,
        }

    return {
        "component_id": component_id,
        "instance_id": str(graph_component.get("instance_id") or ""),
        "class_name": str(graph_component.get("class_name") or estimated_component.get("class_name") or "Component"),
        "bbox": bbox,
        "center": {"x": (bbox[0] + bbox[2]) / 2, "y": (bbox[1] + bbox[3]) / 2},
        "estimated_orientation": str(estimated_component.get("estimated_orientation") or "unknown"),
        "terminals": terminals,
        "state": graph_component.get("state") or estimated_component.get("state"),
    }


def resolve_geometry_image_path(
    estimate_path: Path,
    circuit_id: str,
    terminal_estimates: dict[str, Any],
) -> str | None:
    """Risolve l'immagine dalla stessa run, senza ereditare path di altri PC."""
    raw_path = terminal_estimates.get("image_path")
    image_name = str(terminal_estimates.get("image_name") or "").strip()
    image_name = image_name.replace("\\", "/").rsplit("/", 1)[-1]
    if not image_name and raw_path:
        image_name = str(raw_path).replace("\\", "/").rsplit("/", 1)[-1]

    if image_name:
        pipeline1_dir = estimate_path.resolve().parent.parent
        report_image = (
            pipeline1_dir
            / "06_graph_report"
            / circuit_id
            / image_name
        )
        if report_image.is_file():
            return str(report_image.resolve())

    if raw_path:
        candidate = Path(str(raw_path)).resolve()
        try:
            candidate.relative_to(PROJECT_ROOT.resolve())
        except ValueError:
            pass
        else:
            if candidate.is_file():
                return str(candidate)
    return image_name or None


def load_geometry_seed(run_dir: Path, circuit_id: str, node_map: dict[str, Any]) -> dict[str, Any]:
    """Carica la geometria Pipeline 1.0 usata come seme dal layout automatico."""
    # Nei workspace persistenti le sorgenti esplicite hanno priorita: in questo
    # modo il viewer usa sempre gli step 03 e 05 della stessa run Pipeline 1.0.
    estimate_path = get_run_source_path(run_dir, "pipeline1", "terminal_estimates")
    graph_path = get_run_source_path(run_dir, "pipeline1", "terminal_graph")

    if estimate_path is None or graph_path is None:
        batch_id = infer_batch_id(run_dir)
        if not batch_id or not circuit_id:
            return {"status": "missing", "reason": "batch_or_circuit_unknown", "components": {}}
        pipeline1_dir = PROJECT_ROOT / "outputs" / "pipeline1.0" / batch_id
        estimate_path = pipeline1_dir / "03_estimate_terminals" / f"{circuit_id}.json"
        graph_path = pipeline1_dir / "05_build_terminal_graph" / f"{circuit_id}.json"

    terminal_estimates = read_json(estimate_path)
    terminal_graph = read_json(graph_path)
    if not terminal_estimates or not terminal_graph:
        return {
            "status": "missing",
            "reason": "pipeline1_geometry_not_found",
            "source_files": {"terminal_estimates": str(estimate_path), "terminal_graph": str(graph_path)},
            "components": {},
        }

    estimates_by_instance = index_estimated_components(terminal_estimates)
    terminal_nodes = node_map.get("component_terminal_nodes") or {}
    components: dict[str, dict[str, Any]] = {}
    for graph_component in terminal_graph.get("components") or []:
        if not isinstance(graph_component, dict):
            continue
        instance_id = str(graph_component.get("instance_id") or "")
        geometry_component = build_geometry_component(
            graph_component,
            estimates_by_instance.get(instance_id) or {},
            terminal_nodes,
        )
        if geometry_component:
            components[geometry_component["component_id"]] = geometry_component

    return {
        "status": "loaded" if components else "empty",
        "source_files": {"terminal_estimates": str(estimate_path), "terminal_graph": str(graph_path)},
        "image": {
            "id": terminal_estimates.get("image_id") or circuit_id,
            "path": resolve_geometry_image_path(
                estimate_path,
                circuit_id,
                terminal_estimates,
            ),
            "width": terminal_estimates.get("image_width"),
            "height": terminal_estimates.get("image_height"),
        },
        "components": components,
        "terminal_graph": terminal_graph.get("graph") or {},
    }


def detect_run_type(run_dir: Path) -> tuple[str, str | None, Path | None]:
    """Capisce se la cartella rappresenta una base run o una run scenario."""
    if run_dir.name == "run" and run_dir.parent.parent.name == "scenarios":
        return "scenario", run_dir.parent.name, run_dir.parent
    return "base", None, None


def build_viewer_model(run_dir: Path) -> dict[str, Any]:
    """Costruisce il contratto dati completo del viewer per una run."""
    run_dir = run_dir.resolve()
    run_type, scenario_id, scenario_dir = detect_run_type(run_dir)
    node_map = read_json(run_dir / "03_node_map.json")
    values_bound = read_json(run_dir / "04_values_bound.json")
    rules = read_json(run_dir / "06_component_rules.json")
    components, directives, warnings = parse_netlist(run_dir / NETLIST_NAME)
    components = enrich_components_with_rules(components, rules)
    components = enrich_bjt_kind_from_spice_models(components, directives)
    components = enrich_manual_dc_supplies(components, rules)
    components = apply_supply_visibility_overrides(components, rules)
    # Il profiling transitorio deve vedere la classe semantica finale. Applicare
    # gli override dopo il parsing farebbe ancora apparire come LED un normale
    # diodo corretto nel values.yaml.
    components = apply_manual_viewer_overrides(components, values_bound)
    measurements = parse_ngspice_stdout(run_dir / "08_ngspice_stdout.txt")
    transient = parse_transient_csv(run_dir / "08_tran.csv", components)
    scenario = read_json(scenario_dir / "scenario.json") if scenario_dir else None
    transient = attach_transient_scope_data(transient, scenario, scenario_dir, components)
    if scenario:
        components = apply_scenario_component_roles(components, scenario)
        components = mark_scenario_modified_components(components, scenario, scenario_dir)
    structural_components = build_structural_components(node_map, rules, measurements, transient)
    # Un fusibile chiuso, o un altro equivalente semplificato, resta nella
    # netlist per la simulazione ma deve avere un solo simbolo nel viewer.
    structural_components = remove_emitted_simplified_duplicates(structural_components, components)
    structural_components, components = enrich_structural_terminals(
        structural_components,
        components,
        rules,
        values_bound,
    )
    # Gli override sono dichiarati per componente nel file valori: il meccanismo
    # resta generale e non introduce eccezioni legate a uno specifico circuito.
    structural_components = apply_manual_viewer_overrides(structural_components, values_bound)
    if scenario:
        structural_components = apply_scenario_visual_overrides(structural_components, scenario, components)
    circuit_id = str(node_map.get("circuit_id") or rules.get("circuit_id") or "")
    geometry_seed = load_geometry_seed(run_dir, circuit_id, node_map)
    model = {
        "source_format": "pipeline2.0_viewer_model",
        "schema_version": VIEWER_MODEL_SCHEMA_VERSION,
        "metadata": {
            "circuit_id": circuit_id,
            "run_type": run_type,
            "scenario_id": scenario_id,
            "run_dir": str(run_dir),
            "source_netlist_path": str(run_dir / NETLIST_NAME),
            "generated_at": datetime.now().isoformat(timespec="seconds"),
        },
        "nodes": build_nodes(node_map, measurements, values_bound),
        "netlist_components": components,
        "structural_components": structural_components,
        "directives": directives,
        "measurements": measurements,
        "transient": transient,
        "geometry_seed": geometry_seed,
        "scenario": scenario,
        "warnings": warnings,
    }
    return model


def write_viewer_model(run_dir: Path) -> dict[str, Any]:
    """Genera e salva `13_viewer_model.json` nella cartella della run."""
    model = build_viewer_model(run_dir)
    write_json(run_dir / VIEWER_MODEL_NAME, model)
    return model
