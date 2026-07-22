"""Test dei contratti condivisi da CHAT, scenari e AGENT."""

from __future__ import annotations

import sys
import unittest
from unittest import mock

from tests.pipeline2.helpers import (
    JSON_TO_SPICE_DIR,
    isolated_directory,
    load_numbered_module,
)


if str(JSON_TO_SPICE_DIR) not in sys.path:
    sys.path.insert(0, str(JSON_TO_SPICE_DIR))

from autonomous_agent.contracts import (  # noqa: E402
    ACTION_REQUIRED_FIELDS,
    ALLOWED_ACTION_TYPES,
    AutonomousDecisionError,
    validate_scenario,
)
from autonomous_agent.controller import (  # noqa: E402
    guard_initial_condition_conclusion,
)
from autonomous_agent.prompt_builder import build_autonomous_prompt  # noqa: E402
from autonomous_agent.state_store import (  # noqa: E402
    MAX_EXECUTABLE_SCENARIOS as AGENT_SCENARIO_LIMIT,
)
from controlled_scenarios.outcome import (  # noqa: E402
    evaluate_diagnostic_outcome as evaluate_core_outcome,
)
import controlled_scenarios.measurements as scenario_measurements  # noqa: E402
import scenario_runtime  # noqa: E402
import web_chat_core  # noqa: E402
from viewer_core.model_builder import (  # noqa: E402
    led_current_states_with_hysteresis,
    led_transient_profiles,
)


class SharedContractTests(unittest.TestCase):
    """Impedisce divergenze tra validazione e runtime degli scenari."""

    @classmethod
    def setUpClass(cls) -> None:
        """Carica i moduli numerati coinvolti nei contratti condivisi."""
        cls.web_chat = load_numbered_module("09_web_chat.py")
        cls.context_builder = load_numbered_module("10_build_diagnostic_context.py")
        cls.step12 = load_numbered_module("12_controlled_scenarios.py")

    def test_action_registries_are_aligned(self) -> None:
        """Ogni azione ammessa dall'agente deve avere un handler eseguibile."""
        self.assertEqual(set(ALLOWED_ACTION_TYPES), set(ACTION_REQUIRED_FIELDS))
        self.assertEqual(set(ALLOWED_ACTION_TYPES), set(self.step12.ACTION_HANDLERS))

    def test_agent_prompt_reserves_activated_for_inactive_base_quantities(self) -> None:
        """Il prompt non confonde un segnale base debole con un target inattivo."""
        prompt = build_autonomous_prompt(
            JSON_TO_SPICE_DIR,
            {"symptom": "Il LED produce impulsi brevi", "iterations": []},
            remaining_budget=5,
        )

        self.assertIn(
            "`activated` significa esclusivamente passaggio da una grandezza inattiva o",
            prompt,
        )
        self.assertIn(
            "se e gia diversa da zero, anche se debole, impulsiva o irregolare",
            prompt,
        )
        self.assertIn(
            "non usare `activated`, neppure se il profilo base e classificato",
            prompt,
        )

    def test_transient_startup_uic_is_enabled_once(self) -> None:
        """La modalita di avvio aggiunge UIC senza duplicarlo sulla `.tran`."""
        netlist = "V1 N001 0 DC 5\n.tran 1ms 1s\n.end\n"
        updated, operation = self.step12.enable_transient_initial_conditions(netlist)
        repeated, repeated_operation = self.step12.enable_transient_initial_conditions(updated)

        self.assertEqual(operation, "enabled")
        self.assertEqual(repeated_operation, "unchanged")
        self.assertIn(".tran 1ms 1s UIC", repeated)
        self.assertEqual(repeated.lower().count("uic"), 1)

    def test_initial_condition_accepts_only_boolean_startup_flag(self) -> None:
        """Il contratto conserva il flag UIC valido e rifiuta stringhe ambigue."""
        scenario = {
            "title": "Avvio asimmetrico",
            "hypothesis": "Il punto operativo mantiene la simmetria",
            "intent": "correction",
            "analysis": "tran",
            "actions": [
                {
                    "type": "set_initial_node_voltage",
                    "target": "N004",
                    "value": "0.8V",
                    "skip_operating_point": True,
                }
            ],
            "compare": ["v(N004)"],
            "expect": {"v(N004)": "changed"},
        }
        self.assertEqual(validate_scenario(scenario, 1), scenario)

        scenario["actions"][0]["skip_operating_point"] = "true"
        with self.assertRaisesRegex(
            AutonomousDecisionError,
            "skip_operating_point deve essere booleano",
        ):
            validate_scenario(scenario, 1)

    def test_repeated_source_values_require_separate_scenarios(self) -> None:
        """Due punti operativi sulla stessa sorgente non diventano una falsa sweep."""
        scenario = {
            "title": "Batteria bassa e alta",
            "hypothesis": "Verificare due condizioni statiche",
            "intent": "diagnostic",
            "analysis": "op",
            "actions": [
                {
                    "type": "change_source_value",
                    "target": "Vbattery1",
                    "value": "8V",
                },
                {
                    "type": "change_source_value",
                    "target": "Vbattery1",
                    "value": "14.4V",
                },
            ],
            "compare": ["v(N001)"],
            "expect": {"v(N001)": "changed"},
        }

        with self.assertRaisesRegex(
            AutonomousDecisionError,
            "assegna piu volte il target 'Vbattery1'",
        ):
            validate_scenario(scenario, 1)

        runtime_errors = scenario_runtime.validate_scenario(scenario)
        self.assertTrue(
            any("usa scenari separati" in error for error in runtime_errors),
            runtime_errors,
        )
        self.assertFalse(self.web_chat.scenario_is_executable(scenario))

    def test_single_transient_source_sweep_remains_valid(self) -> None:
        """Una singola PWL conserva il modo corretto di rappresentare una sweep."""
        scenario = {
            "title": "Rampa della batteria",
            "hypothesis": "Osservare la risposta durante una variazione temporale",
            "intent": "diagnostic",
            "analysis": "tran",
            "actions": [
                {
                    "type": "change_source_value",
                    "target": "Vbattery1",
                    "value": "PWL(0s 8V 1s 12V 2s 14.4V)",
                }
            ],
            "compare": ["v(N001)"],
            "measure": {"v(N001)": "tran_vpp"},
            "expect": {"v(N001)": "changed"},
        }

        self.assertEqual(validate_scenario(scenario, 1), scenario)
        self.assertEqual(scenario_runtime.validate_scenario(scenario), [])
        self.assertTrue(self.web_chat.scenario_is_executable(scenario))

    def test_chat_led_startup_requires_a_temporal_correction(self) -> None:
        """CHAT registra un avvio LED solo se verifica davvero il lampeggio."""
        scenario = {
            "title": "Avviare il lampeggio alternato dei LED",
            "hypothesis": "La simmetria iniziale impedisce l'oscillazione",
            "intent": "correction",
            "analysis": "tran",
            "actions": [
                {
                    "type": "set_initial_node_voltage",
                    "target": "N001",
                    "value": "1V",
                    "skip_operating_point": True,
                }
            ],
            "compare": ["v(N001)", "@dled1[id]"],
            "measure": {"@dled1[id]": "tran_abs_peak"},
            "expect": {"v(N001)": "changed", "@dled1[id]": "changed"},
            "temporal_expect": {
                "target": "Dled1",
                "required_state": "blinking",
                "require_regular_period": True,
            },
        }
        self.assertTrue(self.web_chat.scenario_is_executable(scenario))

        without_temporal = dict(scenario)
        without_temporal.pop("temporal_expect")
        self.assertFalse(self.web_chat.scenario_is_executable(without_temporal))

        diagnostic = dict(scenario)
        diagnostic["intent"] = "diagnostic"
        self.assertFalse(self.web_chat.scenario_is_executable(diagnostic))

        operating_point = dict(scenario)
        operating_point["analysis"] = "op"
        self.assertFalse(self.web_chat.scenario_is_executable(operating_point))

        irregular = dict(scenario)
        irregular["temporal_expect"] = {
            "target": "Dled1",
            "required_state": "blinking",
            "require_regular_period": False,
        }
        self.assertFalse(self.web_chat.scenario_is_executable(irregular))

        multiple_targets = dict(scenario)
        multiple_targets["temporal_expect"] = {
            "target": ["Dled1", "Dled2"],
            "required_state": "blinking",
            "require_regular_period": True,
        }
        self.assertFalse(self.web_chat.scenario_is_executable(multiple_targets))
        with self.assertRaisesRegex(
            AutonomousDecisionError,
            "un singolo identificatore testuale",
        ):
            validate_scenario(multiple_targets, 1)

    def test_led_hysteresis_ignores_numeric_threshold_chatter(self) -> None:
        """Il rumore vicino alla soglia non diventa un falso lampeggio veloce."""
        times = [index * 0.01 for index in range(80)]
        one_cycle = [0.015] * 10 + [0.00008, 0.00012] * 5
        currents = one_cycle * 4
        states, turn_on, turn_off = led_current_states_with_hysteresis(currents)
        transitions = sum(
            current != previous
            for previous, current in zip(states, states[1:])
        )
        self.assertGreater(turn_on, turn_off)
        self.assertEqual(transitions, 7)

        profiles = led_transient_profiles(
            [
                {
                    "id": "Dled1",
                    "source_component_id": "led1.1",
                    "kind": "diode",
                    "nodes": ["N001", "N002"],
                }
            ],
            times,
            {"N001": [5.0] * 80, "N002": [4.2] * 80},
            {"DLED1": currents},
        )
        profile = profiles["Dled1"]
        self.assertEqual(profile["state"], "blinking")
        self.assertTrue(profile["regular_period"])
        self.assertEqual(profile["pulse_count"], 4)

    def test_scenario_limits_are_aligned(self) -> None:
        """CHAT, contesto, runtime e AGENT devono condividere lo stesso budget."""
        limits = {
            self.web_chat.MAX_EXECUTABLE_SCENARIOS,
            self.context_builder.MAX_EXECUTABLE_SCENARIOS,
            self.step12.MAX_EXECUTABLE_SCENARIOS,
            scenario_runtime.MAX_EXECUTABLE_SCENARIOS,
            AGENT_SCENARIO_LIMIT,
        }
        self.assertEqual(limits, {5})

    def test_chat_registry_distinguishes_op_and_transient_evidence(self) -> None:
        """Le stesse azioni restano eseguibili una volta in OP e una in TRAN."""
        operating_point = {
            "analysis": "op",
            "actions": [{"type": "close_switch", "target": "switch1.1"}],
        }
        transient = {
            "analysis": "tran",
            "actions": [{"type": "close_switch", "target": "switch1.1"}],
        }

        self.assertNotEqual(
            self.web_chat.registered_scenario_signature(operating_point),
            self.web_chat.registered_scenario_signature(transient),
        )
        self.assertEqual(
            self.web_chat.registered_scenario_signature(operating_point),
            scenario_runtime.scenario_signature(operating_point),
        )
        self.assertEqual(
            self.web_chat.registered_scenario_signature(transient),
            scenario_runtime.scenario_signature(transient),
        )

    def test_chat_completes_requested_transient_diode_measurements(self) -> None:
        """Una corrente TRAN gia richiesta riceve il metodo di lettura mancante."""
        scenario = {
            "analysis": "tran",
            "intent": "diagnostic",
            "actions": [
                {
                    "type": "change_source_value",
                    "target": "Vbattery1",
                    "value": "10V",
                }
            ],
            "compare": ["v(N001)", "@Dled1[id]"],
            "expect": {"@Dled1[id]": "changed"},
        }

        completed = self.web_chat.complete_transient_current_measurements(scenario)

        self.assertNotIn("measure", scenario)
        self.assertEqual(completed["measure"], {"@Dled1[id]": "tran_abs_peak"})
        self.assertTrue(self.web_chat.scenario_is_executable(completed))

    def test_chat_never_executes_a_scenario_rejected_by_the_registry(self) -> None:
        """Un JSON non registrabile non puo aggirare i guardrail via fallback."""
        invalid_response = """```json
{
  "scenario_id": "scenario_1",
  "analysis": "op",
  "actions": [{"type": "close_switch", "target": "switch1.1"}],
  "compare": ["v(N001)"],
  "expect": {}
}
```"""
        with isolated_directory("unregistered_chat_scenario") as temporary_root:
            output_dir = temporary_root / "run"
            output_dir.mkdir(parents=True)
            (output_dir / self.web_chat.CHAT_RESPONSE_NAME).write_text(
                invalid_response,
                encoding="utf-8",
            )

            with mock.patch.object(self.web_chat, "execute_shared_scenario") as execute:
                result = self.web_chat.handle_scenario_request(
                    output_dir=output_dir,
                    user_message="esegui scenario 1",
                    batch="batchTest",
                    circuit="circuitTest",
                    experiment="demo_test",
                )

            execute.assert_not_called()
            self.assertIn("non risulta registrato come eseguibile", result["reply"])

    def test_webchat_helpers_are_reexported_by_the_numbered_step(self) -> None:
        """La facciata web mantiene le utility pubbliche spostate internamente."""
        for name in (
            "escape_block",
            "is_safe_path_name",
            "read_json_safe",
            "read_text_safe",
            "unescape_html_entities",
        ):
            with self.subTest(name=name):
                self.assertIs(getattr(self.web_chat, name), getattr(web_chat_core, name))

    def test_scenario_outcome_is_reexported_by_the_numbered_step(self) -> None:
        """Lo step 12 mantiene il simbolo pubblico dopo l'estrazione interna."""
        self.assertIs(self.step12.evaluate_diagnostic_outcome, evaluate_core_outcome)

    def test_scenario_measurements_are_reexported_by_the_numbered_step(self) -> None:
        """Le funzioni di misura restano disponibili dallo step numerato."""
        public_names = (
            "classify_change",
            "count_ngspice_stderr_warnings",
            "is_internal_device_current_quantity",
            "is_stderr_quantity",
            "is_voltage_quantity",
            "normalize_quantity_name",
            "parse_float",
            "parse_ngspice_stdout",
            "parse_tran_csv_metrics",
            "quantity_lookup_key",
            "voltage_quantity_nodes",
        )
        for name in public_names:
            with self.subTest(name=name):
                self.assertIs(
                    getattr(self.step12, name),
                    getattr(scenario_measurements, name),
                )

    def test_scenario_outcome_keeps_guardrail_priority_and_messages(self) -> None:
        """La prima evidenza incompleta prevale sugli altri criteri presenti."""
        outcome = evaluate_core_outcome(
            {
                "requested_count": 2,
                "expected_count": 1,
                "expectations_missing_count": 1,
                "gain_required": True,
                "gain_available": False,
            },
            analysis="tran",
            intent="correction",
        )
        self.assertEqual(
            outcome,
            {
                "status": "partially_resolved",
                "technical_label": "Partially resolved",
                "label": "Criteri verificati solo in parte",
                "reason": (
                    "Almeno una misura necessaria ai criteri di successo non e "
                    "disponibile negli output SPICE dello scenario."
                ),
                "user_message": (
                    "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato."
                ),
                "stop_automation": False,
                "confidence": "low",
                "next_step": (
                    "Puo avere senso un altro scenario, oppure una conclusione "
                    "diagnostica piu mirata."
                ),
            },
        )

    def test_diagnostic_intent_never_stops_on_a_confirmed_hypothesis(self) -> None:
        """Un test diagnostico positivo non viene scambiato per correzione."""
        summary = {
            "requested_count": 1,
            "changed_count": 1,
            "expected_count": 1,
            "expectations_met_count": 1,
            "meaningful_improvement_count": 1,
        }
        correction = evaluate_core_outcome(summary, intent="correction")
        diagnostic = evaluate_core_outcome(summary, intent="diagnostic")

        self.assertEqual(correction["status"], "resolved_candidate")
        self.assertTrue(correction["stop_automation"])
        self.assertEqual(diagnostic["status"], "partially_resolved")
        self.assertEqual(
            diagnostic["technical_label"],
            "Diagnostic hypothesis confirmed",
        )
        self.assertFalse(diagnostic["stop_automation"])

    def test_failed_initial_condition_trial_cannot_claim_topology_issue(self) -> None:
        """Una sola prova `.ic` negativa resta inconclusiva sul piano strutturale."""
        state = {
            "symptom": "I LED dovrebbero lampeggiare regolarmente",
            "iterations": [
                {
                    "decision": {
                        "scenarios": [
                            {
                                "actions": [
                                    {
                                        "type": "set_initial_node_voltage",
                                        "target": "N001",
                                        "value": "0V",
                                    }
                                ]
                            }
                        ]
                    },
                    "scenario_results": [
                        {
                            "spice_executed": True,
                            "comparison_summary": {"temporal_met": False},
                            "diagnostic_outcome": {"status": "partially_resolved"},
                        }
                    ],
                }
            ],
        }
        decision = {
            "decision": "stop",
            "final_status": "topology_issue",
            "reason": "Topologia errata",
            "final_answer": "Il circuito e strutturalmente errato.",
            "final_cause": "Topologia",
            "verified_correction": "",
        }

        guarded = guard_initial_condition_conclusion(state, decision)

        self.assertEqual(guarded["final_status"], "inconclusive")
        self.assertEqual(guarded["final_cause"], "")
        self.assertIn("non si puo concludere", guarded["final_answer"])

    def test_successful_initial_condition_trial_keeps_the_agent_conclusion(self) -> None:
        """Una prova `.ic` che soddisfa il criterio temporale non viene alterata."""
        state = {
            "symptom": "Il LED dovrebbe lampeggiare",
            "iterations": [
                {
                    "decision": {
                        "scenarios": [
                            {
                                "actions": [
                                    {
                                        "type": "set_initial_node_voltage",
                                        "target": "N001",
                                        "value": "0V",
                                    }
                                ]
                            }
                        ]
                    },
                    "scenario_results": [
                        {
                            "spice_executed": True,
                            "comparison_summary": {"temporal_met": True},
                            "diagnostic_outcome": {"status": "partially_resolved"},
                        }
                    ],
                }
            ],
        }
        decision = {
            "decision": "stop",
            "final_status": "localized",
            "reason": "Simmetria iniziale verificata",
            "final_answer": "La causa e l'avvio simmetrico.",
            "final_cause": "Avvio simmetrico",
            "verified_correction": "",
        }

        self.assertIs(guard_initial_condition_conclusion(state, decision), decision)

    def test_temporal_correction_does_not_require_scalar_ten_percent_gain(self) -> None:
        """Un cambio di stato temporale verificato e gia una correzione diretta."""
        summary = {
            "expected_count": 4,
            "expectations_met_count": 4,
            "expectations_failed_count": 0,
            "expectations_missing_count": 0,
            "meaningful_improvement_count": 0,
            "gain_required": False,
            "quality_required": False,
        }
        evaluation = {"available": True, "met": True}

        self.assertTrue(
            scenario_runtime.temporal_correction_is_resolved(
                {"intent": "correction"},
                summary,
                evaluation,
            )
        )
        self.assertFalse(
            scenario_runtime.temporal_correction_is_resolved(
                {"intent": "diagnostic"},
                summary,
                evaluation,
            )
        )

    def test_temporal_correction_keeps_gain_and_quality_guardrails(self) -> None:
        """Il successo temporale non nasconde altri obiettivi obbligatori falliti."""
        base_summary = {
            "expected_count": 1,
            "expectations_met_count": 1,
            "expectations_failed_count": 0,
            "expectations_missing_count": 0,
        }
        evaluation = {"available": True, "met": True}

        gain_summary = {
            **base_summary,
            "gain_required": True,
            "gain_available": True,
            "gain_sufficient": False,
        }
        quality_summary = {
            **base_summary,
            "quality_required": True,
            "quality_available": True,
            "quality_improved": False,
            "quality_acceptable": True,
            "quality_output_preserved": True,
        }
        for summary in (gain_summary, quality_summary):
            with self.subTest(summary=summary):
                self.assertFalse(
                    scenario_runtime.temporal_correction_is_resolved(
                        {"intent": "correction"},
                        summary,
                        evaluation,
                    )
                )

    def test_valid_transient_scenario_preserves_contract(self) -> None:
        """Un contratto completo mantiene campi extra e ordine delle sezioni."""
        scenario = {
            "title": "Verifica trasferimento",
            "hypothesis": "Il segnale attraversa lo stadio",
            "intent": "correction",
            "analysis": "tran",
            "actions": [
                {"type": "change_component_value", "target": "R1", "value": "2k"}
            ],
            "compare": ["v(N001)", "v(N002)"],
            "measure": {"v(N001)": "tran_vpp", "v(N002)": "tran_vpp"},
            "gain": {"input": "v(N001)", "output": "v(N002)", "min_ratio": 1.1},
            "quality": "thd",
            "expect": {"v(N002)": "magnitude_increased"},
            "temporal_expect": {
                "target": "D1",
                "required_state": "blinking",
                "require_regular_period": True,
                "min_duty_cycle": 0.1,
            },
            "custom_metadata": {"keep": True},
        }
        normalized = validate_scenario(
            scenario,
            1,
            require_gain_comparison=True,
            require_quality_analysis=True,
            require_temporal_expectation=True,
        )
        self.assertEqual(normalized, scenario)

    def test_valid_operating_point_scenario_is_fully_normalized(self) -> None:
        """Blocca trimming, canonicalizzazione e campi predefiniti per OP."""
        normalized = validate_scenario(
            {
                "title": " Test statico ",
                "hypothesis": " Verifica ramo ",
                "intent": "DIAGNOSTIC",
                "analysis": "OP",
                "actions": [
                    {
                        "type": "change_source_value",
                        "target": "V1",
                        "value": "10V",
                    }
                ],
                "compare": [" V(N001) "],
                "expect": {"v(n001)": "increased"},
            },
            1,
        )
        self.assertEqual(
            normalized,
            {
                "title": "Test statico",
                "hypothesis": "Verifica ramo",
                "intent": "diagnostic",
                "analysis": "op",
                "actions": [
                    {
                        "type": "change_source_value",
                        "target": "V1",
                        "value": "10V",
                    }
                ],
                "compare": ["V(N001)"],
                "expect": {"V(N001)": "increased"},
            },
        )

    def test_validation_keeps_major_error_paths_stable(self) -> None:
        """Protegge priorita e messaggi dei principali guardrail scenario."""
        valid_action = {
            "type": "change_source_value",
            "target": "V1",
            "value": "10V",
        }
        transient_base = {
            "actions": [valid_action],
            "intent": "correction",
            "analysis": "tran",
            "compare": ["v(N001)", "v(N002)"],
            "measure": {"v(N001)": "tran_vpp", "v(N002)": "tran_vpp"},
            "expect": {"v(N002)": "increased"},
        }
        cases = (
            (
                None,
                {},
                "Scenario 1: oggetto JSON richiesto",
            ),
            (
                {},
                {},
                "Scenario 1: actions non puo essere vuoto",
            ),
            (
                {
                    "actions": [valid_action],
                    "intent": "diagnostic",
                    "analysis": "dc",
                },
                {},
                "Scenario 1: analysis deve essere 'op' oppure 'tran'",
            ),
            (
                {
                    "actions": [valid_action],
                    "intent": "diagnostic",
                    "analysis": "op",
                },
                {},
                "Scenario 1: compare non puo essere vuoto",
            ),
            (
                transient_base,
                {"require_gain_comparison": True},
                (
                    "Scenario 1: una correzione del sintomo di amplificazione "
                    "richiede gain con input e output"
                ),
            ),
            (
                transient_base,
                {"require_temporal_expectation": True},
                "Scenario 1: il sintomo dinamico richiede temporal_expect",
            ),
        )
        for scenario, options, expected_message in cases:
            with self.subTest(expected_message=expected_message):
                with self.assertRaises(AutonomousDecisionError) as raised:
                    validate_scenario(scenario, 1, **options)
                self.assertEqual(str(raised.exception), expected_message)

    def test_validation_keeps_the_first_error_stable(self) -> None:
        """L'ordine dei guardrail fa parte del comportamento osservabile."""
        with self.assertRaisesRegex(
            AutonomousDecisionError,
            "Scenario 1: intent deve essere 'correction' oppure 'diagnostic'",
        ):
            validate_scenario(
                {
                    "actions": [{"type": "unknown"}],
                    "intent": "",
                    "analysis": "invalid",
                },
                1,
            )


if __name__ == "__main__":
    unittest.main()
