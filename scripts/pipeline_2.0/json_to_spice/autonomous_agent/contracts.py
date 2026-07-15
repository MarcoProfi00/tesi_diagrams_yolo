"""Contratti e validazione delle decisioni dell'agente autonomo."""

from __future__ import annotations

import json
import re
from typing import Any


ALLOWED_ACTION_TYPES = frozenset(
    {
        "drive_node_voltage",
        "change_source_value",
        "change_component_value",
        "close_switch",
        "connect_nodes",
        "feed_nodes_from_source_node",
        "add_voltage_source_between_nodes",
        "add_resistor_between_nodes",
    }
)
FINAL_STATUSES = frozenset(
    {
        "resolved",
        "localized",
        "partially_localized",
        "topology_issue",
        "inconclusive",
    }
)
MAX_SCENARIOS_PER_DECISION = 2
MAX_ACTIONS_PER_SCENARIO = 5
ACTION_REQUIRED_FIELDS = {
    "drive_node_voltage": ("target", "value"),
    "change_source_value": ("target", "value"),
    "change_component_value": ("target", "value"),
    "close_switch": ("target",),
    "connect_nodes": ("from", "to"),
    "feed_nodes_from_source_node": ("source_node", "target_nodes"),
    "add_voltage_source_between_nodes": ("positive", "negative", "value"),
    "add_resistor_between_nodes": ("from", "to", "value"),
}


class AutonomousDecisionError(ValueError):
    """Segnala una decisione AI non conforme al contratto previsto."""


def action_field_is_missing(value: Any) -> bool:
    """Riconosce campi assenti, stringhe vuote e liste prive di valori."""
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, list):
        return not value or any(
            item is None or (isinstance(item, str) and not item.strip())
            for item in value
        )
    return False


def extract_json_object(response_text: str) -> dict[str, Any]:
    """Estrae un singolo oggetto JSON anche se racchiuso in un code fence."""
    text = str(response_text or "").strip()
    fenced = re.fullmatch(r"```(?:json)?\s*(\{.*\})\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        text = fenced.group(1)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise AutonomousDecisionError(f"Risposta non JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise AutonomousDecisionError("La decisione deve essere un oggetto JSON")
    return data


def validate_action(action: Any, scenario_index: int, action_index: int) -> dict[str, Any]:
    """Valida una singola azione rispetto alla whitelist autonoma."""
    if not isinstance(action, dict):
        raise AutonomousDecisionError(
            f"Scenario {scenario_index}, azione {action_index}: oggetto JSON richiesto"
        )
    action_type = str(action.get("type") or "").strip()
    if action_type not in ALLOWED_ACTION_TYPES:
        raise AutonomousDecisionError(
            f"Scenario {scenario_index}, azione {action_index}: tipo non consentito '{action_type}'"
        )
    for field in ACTION_REQUIRED_FIELDS.get(action_type, ()):
        if action_field_is_missing(action.get(field)):
            raise AutonomousDecisionError(
                f"Scenario {scenario_index}, azione {action_index}: campo '{field}' mancante"
            )
    if action_type == "feed_nodes_from_source_node" and not isinstance(
        action.get("target_nodes"), list
    ):
        raise AutonomousDecisionError(
            f"Scenario {scenario_index}, azione {action_index}: target_nodes deve essere una lista"
        )
    return dict(action)


def validate_scenario(scenario: Any, scenario_index: int) -> dict[str, Any]:
    """Valida uno scenario self-contained proposto dall'agente."""
    if not isinstance(scenario, dict):
        raise AutonomousDecisionError(f"Scenario {scenario_index}: oggetto JSON richiesto")
    actions = scenario.get("actions")
    if not isinstance(actions, list) or not actions:
        raise AutonomousDecisionError(f"Scenario {scenario_index}: actions non puo essere vuoto")
    if len(actions) > MAX_ACTIONS_PER_SCENARIO:
        raise AutonomousDecisionError(
            f"Scenario {scenario_index}: massimo {MAX_ACTIONS_PER_SCENARIO} azioni"
        )

    normalized = dict(scenario)
    normalized["title"] = str(scenario.get("title") or f"Scenario autonomo {scenario_index}").strip()
    normalized["hypothesis"] = str(scenario.get("hypothesis") or "").strip()
    compare = scenario.get("compare")
    if not isinstance(compare, list) or not compare:
        raise AutonomousDecisionError(f"Scenario {scenario_index}: compare non puo essere vuoto")
    normalized["compare"] = [str(item).strip() for item in compare if str(item).strip()]
    if not normalized["compare"]:
        raise AutonomousDecisionError(f"Scenario {scenario_index}: compare non contiene grandezze valide")
    normalized["actions"] = [
        validate_action(action, scenario_index, action_index)
        for action_index, action in enumerate(actions, start=1)
    ]
    return normalized


def normalized_connection_pair(first_node: Any, second_node: Any) -> frozenset[str]:
    """Normalizza una coppia di nodi per confrontare relazioni di continuita."""
    return frozenset(
        {
            str(first_node or "").strip().upper(),
            str(second_node or "").strip().upper(),
        }
    )


def validate_connect_feed_distinction(scenarios: list[dict[str, Any]]) -> None:
    """Impedisce che connect e feed testino la stessa relazione nella decisione."""
    seen_pairs: dict[frozenset[str], tuple[str, int, int]] = {}
    relevant_types = {"connect_nodes", "feed_nodes_from_source_node"}

    for scenario_index, scenario in enumerate(scenarios, start=1):
        for action_index, action in enumerate(scenario.get("actions") or [], start=1):
            action_type = str(action.get("type") or "")
            if action_type not in relevant_types:
                continue

            if action_type == "connect_nodes":
                pairs = [normalized_connection_pair(action.get("from"), action.get("to"))]
            else:
                pairs = [
                    normalized_connection_pair(action.get("source_node"), target_node)
                    for target_node in action.get("target_nodes") or []
                ]

            for pair in pairs:
                previous = seen_pairs.get(pair)
                if previous is not None and previous[0] != action_type:
                    nodes = " <-> ".join(sorted(pair))
                    raise AutonomousDecisionError(
                        "connect_nodes e feed_nodes_from_source_node non possono testare "
                        f"la stessa relazione ({nodes}) nella stessa decisione; scegline uno"
                    )
                seen_pairs[pair] = (action_type, scenario_index, action_index)


def validate_decision(data: dict[str, Any], remaining_budget: int) -> dict[str, Any]:
    """Valida e normalizza una decisione `run_scenarios` oppure `stop`."""
    decision = str(data.get("decision") or "").strip()
    reason = str(data.get("reason") or "").strip()
    if not reason:
        raise AutonomousDecisionError("reason e obbligatorio")

    if decision == "stop":
        final_status = str(data.get("final_status") or "").strip()
        final_answer = str(data.get("final_answer") or "").strip()
        if final_status not in FINAL_STATUSES:
            raise AutonomousDecisionError(f"final_status non valido: '{final_status}'")
        if not final_answer:
            raise AutonomousDecisionError("final_answer e obbligatorio per stop")
        return {
            "decision": "stop",
            "reason": reason,
            "final_status": final_status,
            "final_answer": final_answer,
        }

    if decision != "run_scenarios":
        raise AutonomousDecisionError("decision deve essere run_scenarios oppure stop")
    if remaining_budget <= 0:
        raise AutonomousDecisionError("Il budget e esaurito: e consentita solo decision=stop")

    scenarios = data.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise AutonomousDecisionError("scenarios deve essere una lista non vuota")
    maximum = min(MAX_SCENARIOS_PER_DECISION, remaining_budget)
    if len(scenarios) > maximum:
        raise AutonomousDecisionError(f"Sono consentiti al massimo {maximum} scenari in questa decisione")
    normalized_scenarios = [
        validate_scenario(scenario, index)
        for index, scenario in enumerate(scenarios, start=1)
    ]
    validate_connect_feed_distinction(normalized_scenarios)
    return {
        "decision": "run_scenarios",
        "reason": reason,
        "scenarios": normalized_scenarios,
    }


def parse_and_validate_decision(response_text: str, remaining_budget: int) -> dict[str, Any]:
    """Converte il testo del modello in una decisione autonoma valida."""
    return validate_decision(extract_json_object(response_text), remaining_budget)
