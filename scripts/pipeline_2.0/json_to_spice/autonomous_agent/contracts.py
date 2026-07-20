"""Contratti e validazione delle decisioni dell'agente autonomo."""

from __future__ import annotations

import json
import re
from typing import Any

from scenario_expectations import ALLOWED_EXPECTATIONS


ALLOWED_ACTION_TYPES = frozenset(
    {
        "drive_node_voltage",
        "set_initial_node_voltage",
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
ALLOWED_SCENARIO_INTENTS = frozenset({"correction", "diagnostic"})
ALLOWED_MEASUREMENT_TYPES = frozenset({"op", "tran_vpp", "tran_abs_peak"})
MAX_SCENARIOS_PER_DECISION = 2
MAX_ACTIONS_PER_SCENARIO = 5
ACTION_REQUIRED_FIELDS = {
    "drive_node_voltage": ("target", "value"),
    "set_initial_node_voltage": ("target", "value"),
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


def is_transient_voltage_quantity(quantity: str) -> bool:
    """Accetta per `tran_vpp` una tensione a uno o due nodi."""
    return bool(
        re.fullmatch(
            r"v\(\s*[^,()\s]+\s*(?:,\s*[^,()\s]+\s*)?\)",
            str(quantity or ""),
            flags=re.IGNORECASE,
        )
    )


def is_transient_internal_current_quantity(quantity: str) -> bool:
    """Accetta la corrente diretta interna di un diodo/LED esportata nel CSV."""
    return bool(
        re.fullmatch(
            r"@[^\s\[\]]+\[id\]",
            str(quantity or "").strip(),
            flags=re.IGNORECASE,
        )
    )


def is_direct_component_quantity(quantity: str) -> bool:
    """Riconosce correnti, potenze o correnti interne utili a un componente."""
    text = str(quantity or "").strip()
    return bool(
        re.match(r"^[ip]\s*\(", text, flags=re.IGNORECASE)
        or is_transient_internal_current_quantity(text)
    )


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


def validate_scenario(
    scenario: Any,
    scenario_index: int,
    allow_unchanged_expectations: bool = True,
    require_gain_comparison: bool = False,
    require_quality_analysis: bool = False,
    require_variable_signal_measurement: bool = False,
    require_direct_component_measurement: bool = False,
    require_temporal_expectation: bool = False,
) -> dict[str, Any]:
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
    intent = str(scenario.get("intent") or "").strip().lower()
    if intent not in ALLOWED_SCENARIO_INTENTS:
        raise AutonomousDecisionError(
            f"Scenario {scenario_index}: intent deve essere 'correction' oppure 'diagnostic'"
        )
    normalized["intent"] = intent
    analysis = str(scenario.get("analysis") or "").strip().lower()
    if analysis not in {"op", "tran"}:
        raise AutonomousDecisionError(
            f"Scenario {scenario_index}: analysis deve essere 'op' oppure 'tran'"
        )
    normalized["analysis"] = analysis

    # I criteri temporali usano i profili calcolati dal viewer dopo la run .tran.
    raw_temporal_expectation = scenario.get("temporal_expect")
    if raw_temporal_expectation is not None:
        if analysis != "tran":
            raise AutonomousDecisionError(
                f"Scenario {scenario_index}: temporal_expect richiede analysis='tran'"
            )
        if not isinstance(raw_temporal_expectation, dict):
            raise AutonomousDecisionError(
                f"Scenario {scenario_index}: temporal_expect deve essere un oggetto"
            )
        target = str(raw_temporal_expectation.get("target") or "").strip()
        if not target:
            raise AutonomousDecisionError(
                f"Scenario {scenario_index}: temporal_expect.target e obbligatorio"
            )
        normalized_temporal_expectation: dict[str, Any] = {"target": target}
        required_state = raw_temporal_expectation.get("required_state")
        if required_state is not None:
            required_state = str(required_state).strip()
            if not required_state:
                raise AutonomousDecisionError(
                    f"Scenario {scenario_index}: temporal_expect.required_state non puo essere vuoto"
                )
            normalized_temporal_expectation["required_state"] = required_state
        regular_period = raw_temporal_expectation.get("require_regular_period")
        if regular_period is not None:
            if not isinstance(regular_period, bool):
                raise AutonomousDecisionError(
                    f"Scenario {scenario_index}: temporal_expect.require_regular_period deve essere booleano"
                )
            normalized_temporal_expectation["require_regular_period"] = regular_period
        for field in ("min_duty_cycle", "min_relative_duty_increase"):
            value = raw_temporal_expectation.get(field)
            if value is None:
                continue
            if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
                raise AutonomousDecisionError(
                    f"Scenario {scenario_index}: temporal_expect.{field} deve essere un numero non negativo"
                )
            if field == "min_duty_cycle" and value > 1:
                raise AutonomousDecisionError(
                    f"Scenario {scenario_index}: temporal_expect.min_duty_cycle deve essere compreso tra 0 e 1"
                )
            normalized_temporal_expectation[field] = float(value)
        if len(normalized_temporal_expectation) == 1:
            raise AutonomousDecisionError(
                f"Scenario {scenario_index}: temporal_expect deve dichiarare almeno un criterio"
            )
        normalized["temporal_expect"] = normalized_temporal_expectation
    elif require_temporal_expectation:
        raise AutonomousDecisionError(
            f"Scenario {scenario_index}: il sintomo dinamico richiede temporal_expect"
        )
    compare = scenario.get("compare")
    if not isinstance(compare, list) or not compare:
        raise AutonomousDecisionError(f"Scenario {scenario_index}: compare non puo essere vuoto")
    normalized["compare"] = [str(item).strip() for item in compare if str(item).strip()]
    if not normalized["compare"]:
        raise AutonomousDecisionError(f"Scenario {scenario_index}: compare non contiene grandezze valide")
    for quantity in normalized["compare"]:
        if re.fullmatch(r"i\(\s*[Qq][^)]+\s*\)", quantity):
            raise AutonomousDecisionError(
                f"Scenario {scenario_index}: la corrente diretta BJT '{quantity}' non e "
                "disponibile; usa la corrente di una resistenza di collettore o emettitore"
            )

    # La mappa opzionale permette di combinare misure DC e transitorie nello stesso test.
    compare_names = {quantity.lower(): quantity for quantity in normalized["compare"]}
    raw_measurements = scenario.get("measure")
    normalized_measurements: dict[str, str] = {}
    if raw_measurements is not None:
        if not isinstance(raw_measurements, dict) or not raw_measurements:
            raise AutonomousDecisionError(
                f"Scenario {scenario_index}: measure deve essere un oggetto non vuoto"
            )
        for raw_quantity, raw_measurement in raw_measurements.items():
            quantity = str(raw_quantity or "").strip()
            measurement = str(raw_measurement or "").strip().lower()
            canonical_quantity = compare_names.get(quantity.lower())
            if canonical_quantity is None:
                raise AutonomousDecisionError(
                    f"Scenario {scenario_index}: la misura '{quantity}' non e presente in compare"
                )
            if measurement not in ALLOWED_MEASUREMENT_TYPES:
                allowed = ", ".join(sorted(ALLOWED_MEASUREMENT_TYPES))
                raise AutonomousDecisionError(
                    f"Scenario {scenario_index}: misura non valida '{measurement}'; usa {allowed}"
                )
            if measurement == "tran_vpp" and analysis != "tran":
                raise AutonomousDecisionError(
                    f"Scenario {scenario_index}: tran_vpp richiede analysis='tran'"
                )
            if measurement == "tran_vpp" and not is_transient_voltage_quantity(
                canonical_quantity
            ):
                raise AutonomousDecisionError(
                    f"Scenario {scenario_index}: tran_vpp richiede v(NODO) oppure v(NODO1,NODO2)"
                )
            if measurement == "tran_abs_peak" and analysis != "tran":
                raise AutonomousDecisionError(
                    f"Scenario {scenario_index}: tran_abs_peak richiede analysis='tran'"
                )
            if measurement == "tran_abs_peak" and not is_transient_internal_current_quantity(
                canonical_quantity
            ):
                raise AutonomousDecisionError(
                    f"Scenario {scenario_index}: tran_abs_peak richiede @dNOME[id]"
                )
            normalized_measurements[canonical_quantity] = measurement
        normalized["measure"] = normalized_measurements

    complete_mixed_objective = (
        require_variable_signal_measurement and require_direct_component_measurement
    )
    if require_variable_signal_measurement and (
        intent == "correction" or complete_mixed_objective
    ):
        if analysis != "tran" or "tran_vpp" not in normalized_measurements.values():
            raise AutonomousDecisionError(
                f"Scenario {scenario_index}: la verifica di un obiettivo AC/VAC richiede "
                "analysis='tran' e almeno una misura tran_vpp"
            )

    gain = scenario.get("gain")
    gain_required = (
        require_gain_comparison
        or (require_quality_analysis and analysis == "tran")
    )
    if gain_required or isinstance(gain, dict):
        if not isinstance(gain, dict):
            raise AutonomousDecisionError(
                f"Scenario {scenario_index}: una correzione del sintomo di "
                "amplificazione richiede gain con input e output"
            )
        gain_input = str(gain.get("input") or "").strip()
        gain_output = str(gain.get("output") or "").strip()
        compare_lookup = {quantity.lower(): quantity for quantity in normalized["compare"]}
        canonical_input = compare_lookup.get(gain_input.lower())
        canonical_output = compare_lookup.get(gain_output.lower())
        if canonical_input is None or canonical_output is None:
            raise AutonomousDecisionError(
                f"Scenario {scenario_index}: gain.input e gain.output devono essere presenti in compare"
            )
        if canonical_input.lower() == canonical_output.lower():
            raise AutonomousDecisionError(
                f"Scenario {scenario_index}: gain.input e gain.output devono essere grandezze distinte"
            )
        if not all(
            is_transient_voltage_quantity(quantity)
            for quantity in (canonical_input, canonical_output)
        ):
            raise AutonomousDecisionError(
                f"Scenario {scenario_index}: gain.input e gain.output devono essere tensioni a uno o due nodi"
            )
        if analysis != "tran":
            raise AutonomousDecisionError(
                f"Scenario {scenario_index}: il confronto di guadagno richiede analysis='tran'"
            )
        normalized_gain: dict[str, Any] = {
            "input": canonical_input,
            "output": canonical_output,
        }
        raw_min_ratio = gain.get("min_ratio")
        if require_gain_comparison and raw_min_ratio is None:
            raise AutonomousDecisionError(
                f"Scenario {scenario_index}: il test di trasferimento richiede gain.min_ratio"
            )
        if raw_min_ratio is not None:
            try:
                min_ratio = float(raw_min_ratio)
            except (TypeError, ValueError) as exc:
                raise AutonomousDecisionError(
                    f"Scenario {scenario_index}: gain.min_ratio deve essere un numero positivo"
                ) from exc
            if min_ratio <= 0:
                raise AutonomousDecisionError(
                    f"Scenario {scenario_index}: gain.min_ratio deve essere maggiore di zero"
                )
            normalized_gain["min_ratio"] = min_ratio
        normalized["gain"] = normalized_gain
    if require_quality_analysis:
        quality = str(scenario.get("quality") or "").strip().lower()
        if intent == "correction" and analysis != "tran":
            raise AutonomousDecisionError(
                f"Scenario {scenario_index}: una correzione della distorsione richiede analysis='tran'"
            )
        if analysis == "tran" and quality != "thd":
            raise AutonomousDecisionError(
                f"Scenario {scenario_index}: un test transitorio della distorsione richiede quality='thd'"
            )
        if analysis == "tran":
            normalized["quality"] = "thd"

    expectations = scenario.get("expect")
    if not isinstance(expectations, dict) or not expectations:
        raise AutonomousDecisionError(
            f"Scenario {scenario_index}: expect deve contenere almeno un criterio di successo"
        )
    normalized_expectations: dict[str, str] = {}
    for raw_quantity, raw_expectation in expectations.items():
        quantity = str(raw_quantity or "").strip()
        expectation = str(raw_expectation or "").strip().lower()
        canonical_quantity = compare_names.get(quantity.lower())
        if canonical_quantity is None:
            raise AutonomousDecisionError(
                f"Scenario {scenario_index}: la grandezza attesa '{quantity}' non e presente in compare"
            )
        if expectation not in ALLOWED_EXPECTATIONS:
            allowed = ", ".join(sorted(ALLOWED_EXPECTATIONS))
            raise AutonomousDecisionError(
                f"Scenario {scenario_index}: aspettativa non valida '{expectation}'; usa {allowed}"
            )
        selected_measurement = normalized_measurements.get(canonical_quantity)
        if (
            analysis == "tran"
            and is_direct_component_quantity(canonical_quantity)
            and selected_measurement != "op"
            and selected_measurement != "tran_abs_peak"
        ):
            raise AutonomousDecisionError(
                f"Scenario {scenario_index}: in analysis='tran' la grandezza "
                f"'{canonical_quantity}' puo restare in compare come osservazione OP, "
                "ma richiede measure='op' o measure='tran_abs_peak' per essere usata come criterio expect"
            )
        if expectation == "unchanged" and not allow_unchanged_expectations:
            raise AutonomousDecisionError(
                f"Scenario {scenario_index}: expect='unchanged' e consentito soltanto "
                "quando il sintomo chiede esplicitamente di preservare un altro comportamento"
            )
        normalized_expectations[canonical_quantity] = expectation
    if all(expectation == "unchanged" for expectation in normalized_expectations.values()):
        raise AutonomousDecisionError(
            f"Scenario {scenario_index}: expect deve verificare almeno un effetto oltre alle grandezze preservate"
        )
    if require_direct_component_measurement and (
        intent == "correction" or complete_mixed_objective
    ):
        direct_quantities = [
            quantity
            for quantity in normalized_expectations
            if is_direct_component_quantity(quantity)
        ]
        if not direct_quantities:
            raise AutonomousDecisionError(
                f"Scenario {scenario_index}: la verifica di LED o lampade richiede "
                "almeno una corrente o potenza diretta in expect"
            )
        if analysis == "tran" and not any(
            normalized_measurements.get(quantity) in {"op", "tran_abs_peak"}
            for quantity in direct_quantities
        ):
            raise AutonomousDecisionError(
                f"Scenario {scenario_index}: nello scenario misto la misura diretta del "
                "componente deve essere dichiarata come op o tran_abs_peak nella mappa measure"
            )
    normalized["expect"] = normalized_expectations
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


def validate_decision(
    data: dict[str, Any],
    remaining_budget: int,
    require_first_scenario: bool = False,
    require_verified_resolution: bool = False,
    require_verified_correction: bool = False,
    allow_unchanged_expectations: bool = True,
    require_gain_comparison: bool = False,
    require_quality_analysis: bool = False,
    require_variable_signal_measurement: bool = False,
    require_direct_component_measurement: bool = False,
    require_joint_objective_verification: bool = False,
    require_temporal_expectation: bool = False,
    require_signal_amplitude_followup: bool = False,
) -> dict[str, Any]:
    """Valida e normalizza una decisione `run_scenarios` oppure `stop`."""
    decision = str(data.get("decision") or "").strip()
    reason = str(data.get("reason") or "").strip()
    if not reason:
        raise AutonomousDecisionError("reason e obbligatorio")

    if decision == "stop":
        if require_first_scenario:
            raise AutonomousDecisionError(
                "Prima della conclusione serve almeno uno scenario controllato eseguito"
            )
        if require_joint_objective_verification:
            raise AutonomousDecisionError(
                "Prima della conclusione serve una singola run self-contained che verifichi "
                "insieme il segnale variabile e lo stato diretto del componente"
            )
        if require_signal_amplitude_followup:
            raise AutonomousDecisionError(
                "Il trasferimento e fallito senza uno sweep di ampiezza sufficiente: con budget "
                "disponibile serve un nuovo scenario self-contained sullo stesso percorso, "
                "con ampiezza significativamente diversa, prima di concludere un guasto strutturale"
            )
        final_status = str(data.get("final_status") or "").strip()
        final_answer = str(data.get("final_answer") or "").strip()
        final_cause = str(data.get("final_cause") or "").strip()
        verified_correction = str(data.get("verified_correction") or "").strip()
        if final_status not in FINAL_STATUSES:
            raise AutonomousDecisionError(f"final_status non valido: '{final_status}'")
        if require_verified_resolution and final_status == "resolved":
            raise AutonomousDecisionError(
                "Prima di final_status='resolved' serve una correzione verificata da uno scenario SPICE"
            )
        if not final_answer:
            raise AutonomousDecisionError("final_answer e obbligatorio per stop")
        if final_status == "resolved" and not verified_correction:
            raise AutonomousDecisionError(
                "verified_correction e obbligatorio quando final_status='resolved'"
            )
        if final_status != "resolved" and verified_correction:
            raise AutonomousDecisionError(
                "verified_correction deve restare vuoto quando la conclusione non e resolved"
            )
        return {
            "decision": "stop",
            "reason": reason,
            "final_status": final_status,
            "final_answer": final_answer,
            "final_cause": final_cause,
            "verified_correction": verified_correction,
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
        validate_scenario(
            scenario,
            index,
            allow_unchanged_expectations=allow_unchanged_expectations,
            require_gain_comparison=require_gain_comparison,
            require_quality_analysis=require_quality_analysis,
            require_variable_signal_measurement=require_variable_signal_measurement,
            require_direct_component_measurement=require_direct_component_measurement,
            require_temporal_expectation=require_temporal_expectation,
        )
        for index, scenario in enumerate(scenarios, start=1)
    ]
    validate_connect_feed_distinction(normalized_scenarios)
    return {
        "decision": "run_scenarios",
        "reason": reason,
        "scenarios": normalized_scenarios,
    }


def parse_and_validate_decision(
    response_text: str,
    remaining_budget: int,
    require_first_scenario: bool = False,
    require_verified_resolution: bool = False,
    require_verified_correction: bool = False,
    allow_unchanged_expectations: bool = True,
    require_gain_comparison: bool = False,
    require_quality_analysis: bool = False,
    require_variable_signal_measurement: bool = False,
    require_direct_component_measurement: bool = False,
    require_joint_objective_verification: bool = False,
    require_temporal_expectation: bool = False,
    require_signal_amplitude_followup: bool = False,
) -> dict[str, Any]:
    """Converte il testo del modello in una decisione autonoma valida."""
    return validate_decision(
        extract_json_object(response_text),
        remaining_budget,
        require_first_scenario=require_first_scenario,
        require_verified_resolution=require_verified_resolution,
        require_verified_correction=require_verified_correction,
        allow_unchanged_expectations=allow_unchanged_expectations,
        require_gain_comparison=require_gain_comparison,
        require_quality_analysis=require_quality_analysis,
        require_variable_signal_measurement=require_variable_signal_measurement,
        require_direct_component_measurement=require_direct_component_measurement,
        require_joint_objective_verification=require_joint_objective_verification,
        require_temporal_expectation=require_temporal_expectation,
        require_signal_amplitude_followup=require_signal_amplitude_followup,
    )
