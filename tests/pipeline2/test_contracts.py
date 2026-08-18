"""Test dei contratti condivisi da CHAT, scenari e AGENT."""

from __future__ import annotations

import hashlib
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
    validate_decision,
    validate_scenario,
)
from autonomous_agent.controller import (  # noqa: E402
    apply_temporal_correction_policy,
    expose_verified_correction_in_answer,
    guard_initial_condition_conclusion,
    symptom_forbids_source_stimulus_changes,
    symptom_requests_correction,
    temporal_correction_policy_for_symptom,
)
from autonomous_agent.prompt_builder import build_autonomous_prompt  # noqa: E402
from agent_readonly.scenario_prompt import build_scenario_answer_format  # noqa: E402
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
    apply_supply_visibility_overrides,
    enrich_structural_terminals,
    led_current_states_with_hysteresis,
    led_transient_profiles,
    pulsating_load_transient_profiles,
)
from viewer_core.component_library import normalize_component_type  # noqa: E402
from viewer_core.layout_builder import (  # noqa: E402
    align_near_perpendicular_leads,
    build_image_guided_components,
    component_symbol_bounds,
    rectangle_overlap_area,
    separate_ground_symbol_collisions,
)
from viewer_core.svg_renderer import (  # noqa: E402
    render_integrated_circuit,
    render_terminal_port,
    render_two_terminal_symbol,
)


class SharedContractTests(unittest.TestCase):
    """Impedisce divergenze tra validazione e runtime degli scenari."""

    @classmethod
    def setUpClass(cls) -> None:
        """Carica i moduli numerati coinvolti nei contratti condivisi."""
        cls.spice_emit = load_numbered_module("07_spice_emit.py")
        cls.spice_run = load_numbered_module("08_spice_run.py")
        cls.web_chat = load_numbered_module("09_web_chat.py")
        cls.context_builder = load_numbered_module("10_build_diagnostic_context.py")
        cls.step12 = load_numbered_module("12_controlled_scenarios.py")

    def test_integrated_circuit_viewer_preserves_bbox_and_pin_coordinates(self) -> None:
        """Il simbolo IC usa la bbox Pipeline 1.0 senza riposizionare i pin."""
        components = [
            {
                "id": "XU1",
                "source_component_id": "integrated_circuit1.1",
                "layout_kind": "structural",
                "nodes": ["N001", "N002", "0"],
                "terminal_names": ["left_1", "right_1", "bottom_1"],
                "viewer_label": "IC1",
                "viewer_value": "DEVICE",
            }
        ]
        geometry_seed = {
            "components": {
                "integrated_circuit1.1": {
                    "class_name": "Integrated_Circuit",
                    "bbox": [10.0, 20.0, 50.0, 80.0],
                    "center": {"x": 30.0, "y": 50.0},
                    "estimated_orientation": "multi_side",
                    "terminals": {
                        "left_1": {"id": "pin1", "x": 13.0, "y": 35.0, "relative_position": "left"},
                        "right_1": {"id": "pin2", "x": 47.0, "y": 35.0, "relative_position": "right"},
                        "bottom_1": {"id": "pin3", "x": 30.0, "y": 76.0, "relative_position": "bottom"},
                    },
                }
            }
        }
        transform = {"scale": 2.0, "offset_x": 5.0, "offset_y": -3.0}

        positioned, warnings = build_image_guided_components(components, geometry_seed, transform)
        integrated_circuit = positioned["XU1"]

        self.assertEqual(warnings, [])
        self.assertEqual(integrated_circuit["component_type"], "integrated_circuit")
        self.assertEqual(integrated_circuit["bbox"], [25.0, 37.0, 105.0, 157.0])
        self.assertEqual(integrated_circuit["symbol_size"], {"width": 80.0, "height": 120.0})
        self.assertEqual(
            [(terminal["x"], terminal["y"]) for terminal in integrated_circuit["terminals"]],
            [(25.0, 67.0), (105.0, 67.0), (65.0, 157.0)],
        )
        svg = render_integrated_circuit(components[0], integrated_circuit)
        self.assertIn('<rect x="25" y="37" width="80" height="120"/>', svg)
        self.assertIn("IC1", svg)

    def test_external_terminal_preserves_contacts_and_stays_outside_series_component(self) -> None:
        """Un jack conserva segnale/ritorno e non viene coperto dal bipolo adiacente."""
        components = [
            {
                "id": "terminal1",
                "source_component_id": "terminal1",
                "viewer_kind": "terminal",
                "layout_kind": "terminal",
                # L'ordine elettrico mette intenzionalmente prima il ritorno.
                "nodes": ["0", "NIN"],
                "terminal_names": ["t2", "t1"],
                "viewer_primary_terminal_id": "terminal1_t1",
                "display_label": "AUDIO IN",
                "display_value": "20 mVpk @ 1 kHz",
                "is_structural": True,
            },
            {
                "id": "R1",
                "source_component_id": "resistor1",
                "layout_kind": "resistor",
                "nodes": ["NIN", "N002"],
                "terminal_names": ["t1", "t2"],
            },
        ]
        geometry_seed = {
            "components": {
                "terminal1": {
                    "class_name": "Terminal",
                    "bbox": [0.0, 0.0, 20.0, 40.0],
                    "center": {"x": 10.0, "y": 20.0},
                    "estimated_orientation": "corner_right_bottom",
                    "terminals": {
                        "t1": {
                            "id": "terminal1_t1",
                            "x": 20.0,
                            "y": 20.0,
                            "relative_position": "right",
                            "node_id": "NIN",
                        },
                        "t2": {
                            "id": "terminal1_t2",
                            "x": 10.0,
                            "y": 40.0,
                            "relative_position": "bottom",
                            "node_id": "0",
                        },
                    },
                },
                "resistor1": {
                    "class_name": "Resistor",
                    "bbox": [30.0, 10.0, 70.0, 30.0],
                    "center": {"x": 50.0, "y": 20.0},
                    "estimated_orientation": "horizontal",
                    "terminals": {
                        "t1": {
                            "id": "resistor1_t1",
                            "x": 26.0,
                            "y": 20.0,
                            "relative_position": "left",
                            "node_id": "NIN",
                        },
                        "t2": {
                            "id": "resistor1_t2",
                            "x": 74.0,
                            "y": 20.0,
                            "relative_position": "right",
                            "node_id": "N002",
                        },
                    },
                },
            }
        }
        transform = {"scale": 1.0, "offset_x": 0.0, "offset_y": 0.0}

        positioned, warnings = build_image_guided_components(components, geometry_seed, transform)
        terminal = positioned["terminal1"]
        contacts = {item["name"]: item for item in terminal["terminals"]}

        self.assertEqual(warnings, [])
        self.assertEqual(contacts["t2"]["y"] - contacts["t1"]["y"], 20.0)
        self.assertLess(contacts["t1"]["x"], positioned["R1"]["terminals"][0]["x"])
        svg = render_terminal_port(components[0], terminal)
        self.assertIn(
            f'cx="{contacts["t1"]["x"]:g}" cy="{contacts["t1"]["y"]:g}"',
            svg,
        )

    def test_supply_terminal_uses_viewer_override_and_primary_contact(self) -> None:
        """Label compatte e contatto principale arrivano dal values.yaml."""
        structural = [
            {
                "id": "terminal1",
                "class_name": "Terminal",
                "nodes": {"t2": "0", "t1": "NIN"},
            }
        ]
        components = [
            {
                "id": "VAUDIO_IN",
                "spice_name": "VAUDIO_IN",
                "kind": "voltage_source",
                "nodes": ["NIN", "0"],
                "value": "SIN(0 0.02 1000)",
            }
        ]
        rules = {
            "supplies": {
                "AUDIO_IN": {
                    "nodes": ["NIN", "0"],
                    "parameters": {
                        "terminal": "terminal1_t1",
                        "return_terminal": "terminal1_t2",
                        "type": "sin",
                        "unit": "V",
                        "viewer_override": {
                            "label": "AUDIO IN",
                            "display_value": "20 mVpk @ 1 kHz",
                            "tooltip": "Testbench SPICE: SIN(0 20m 1k)",
                        },
                    },
                }
            }
        }

        enriched, netlist = enrich_structural_terminals(
            structural,
            components,
            rules,
            {},
        )

        terminal = enriched[0]
        self.assertEqual(terminal["viewer_primary_terminal_id"], "terminal1_t1")
        self.assertEqual(terminal["display_label"], "AUDIO IN")
        self.assertEqual(terminal["display_value"], "20 mVpk @ 1 kHz")
        self.assertEqual(terminal["viewer_tooltip"], "Testbench SPICE: SIN(0 20m 1k)")
        self.assertEqual(netlist[0]["viewer_hidden_by_terminal"], "terminal1")

    def test_hidden_testbench_supply_stays_out_of_viewer(self) -> None:
        """Uno stimolo numerico opt-in resta in netlist ma non nello schema."""
        components = [
            {
                "id": "VTRIGGER",
                "spice_name": "VTRIGGER",
                "kind": "voltage_source",
                "nodes": ["NTRIG", "0"],
                "value": "PULSE(9 0 1s 1ms 1ms 100ms 10s)",
            }
        ]
        rules = {
            "supplies": {
                "TRIGGER": {
                    "nodes": ["NTRIG", "0"],
                    "parameters": {
                        "type": "pulse",
                        "viewer_override": {"hidden": True},
                    },
                }
            }
        }

        enriched = apply_supply_visibility_overrides(components, rules)

        self.assertTrue(enriched[0]["viewer_hidden"])
        self.assertEqual(enriched[0]["viewer_role"], "hidden_testbench_stimulus")

    def test_push_button_has_a_dedicated_momentary_symbol(self) -> None:
        """Push_Button non ricade nel rettangolo strutturale generico."""
        self.assertEqual(normalize_component_type("Push_Button"), "push_button")
        component = {
            "id": "push_button1",
            "parameters": {"state": "open"},
        }
        position = {
            "x": 50.0,
            "y": 50.0,
            "component_type": "push_button",
            "state": "open",
            "terminals": [
                {"name": "t1", "x": 10.0, "y": 50.0},
                {"name": "t2", "x": 90.0, "y": 50.0},
            ],
        }

        svg = render_two_terminal_symbol(
            "push_button1",
            component,
            position,
            set(),
            set(),
            set(),
            {},
            {},
        )

        self.assertIn("push-button-contact", svg)
        self.assertIn("push-button-plunger", svg)

    def test_ground_layout_ignores_unrelated_zero_node_and_removes_symbol_overlap(self) -> None:
        """Masse graficamente separate non si allineano tra loro e non coprono componenti."""
        positioned = {
            "C1": {
                "x": 100.0,
                "y": 80.0,
                "component_type": "polarized_capacitor",
                "orientation": "vertical",
                "symbol_size": {"width": 58.0, "height": 48.0},
                "terminals": [
                    {
                        "name": "negative",
                        "node_id": "0",
                        "relative_position": "bottom",
                        "x": 100.0,
                        "y": 109.0,
                    }
                ],
            },
            "speaker": {
                "x": 170.0,
                "y": 80.0,
                "component_type": "speaker",
                "orientation": "horizontal",
                "symbol_size": {"width": 104.0, "height": 76.0},
                "terminals": [
                    {
                        "name": "t2",
                        "node_id": "0",
                        "relative_position": "left",
                        "x": 118.0,
                        "y": 102.0,
                    }
                ],
            },
            "gnd1": {
                "x": 112.0,
                "y": 117.0,
                "source_component_id": "gnd1",
                "component_type": "ground",
                "orientation": "vertical",
                "symbol_size": {"width": 50.0, "height": 34.0},
                "terminals": [
                    {
                        "name": "t1",
                        "node_id": "0",
                        "relative_position": "top",
                        "x": 112.0,
                        "y": 100.0,
                    }
                ],
            },
        }
        original_x = positioned["gnd1"]["x"]

        align_near_perpendicular_leads(positioned)
        self.assertEqual(positioned["gnd1"]["x"], original_x)

        separate_ground_symbol_collisions(positioned)
        ground_bounds = component_symbol_bounds(positioned["gnd1"])
        self.assertTrue(
            all(
                rectangle_overlap_area(ground_bounds, component_symbol_bounds(component)) <= 1.0
                for component_id, component in positioned.items()
                if component_id != "gnd1"
            )
        )

    def test_manual_sinusoidal_source_uses_the_shared_voltage_expression(self) -> None:
        """Una sorgente YAML sinusoidale viene emessa con sintassi SPICE valida."""
        line, warning = self.spice_emit.emit_supply(
            "AUDIO_IN",
            {
                "status": "spice_ready",
                "nodes": ["N001", "0"],
                "parameters": {
                    "value": 0.1,
                    "unit": "V",
                    "type": "sin",
                    "offset": 0,
                    "amplitude": 0.1,
                    "frequency": 1000,
                },
            },
        )

        self.assertIsNone(warning)
        self.assertEqual(line, "VAUDIO_IN N001 0 SIN(0 0.1 1000)")

    def test_external_spice_model_is_verified_inlined_and_declares_runtime(self) -> None:
        """Un modello su file resta generico, verificabile e autosufficiente."""
        with isolated_directory("external_spice_model") as temporary_root:
            models_dir = temporary_root / "models"
            models_dir.mkdir()
            model_path = models_dir / "device.lib"
            model_text = ".SUBCKT DEVICE IN OUT\nR1 IN OUT 1k\n.ENDS DEVICE\n"
            model_path.write_text(model_text, encoding="utf-8")
            model_sha256 = hashlib.sha256(model_path.read_bytes()).hexdigest()
            registry_path = temporary_root / "models.yaml"
            registry_path.write_text("# registry used as a relative path anchor\n", encoding="utf-8")
            registry = {
                "models": {
                    "DEVICE": {
                        "file": "models/device.lib",
                        "sha256": model_sha256,
                        "ngspice_defines": {"ngbehavior": "ps"},
                    }
                }
            }
            rules = {
                "circuit_id": "external_model_test",
                "components": {
                    "integrated_circuit1.1": {
                        "status": "spice_ready",
                        "spice_support": "subcircuit",
                        "nodes": ["N001", "N002"],
                        "parameters": {"model": "DEVICE"},
                    }
                },
                "simulation": {"analyses": ["op"]},
            }

            emitted = self.spice_emit.build_spice_netlist(
                rules,
                spice_models=registry,
                spice_models_source=registry_path,
            )

            self.assertIn("Xintegrated_circuit1_1 N001 N002 DEVICE", emitted["netlist_text"])
            self.assertIn('.include "07_external_models.lib"', emitted["netlist_text"])
            self.assertIn(
                ".SUBCKT DEVICE IN OUT",
                emitted["external_model_bundle_text"],
            )
            self.assertEqual(
                emitted["report"]["ngspice_defines"],
                {"ngbehavior": "ps"},
            )
            self.assertEqual(
                emitted["report"]["external_model_sources"][0]["sha256"],
                model_sha256.upper(),
            )

    def test_external_spice_model_rejects_a_hash_mismatch(self) -> None:
        """Il registro non puo caricare silenziosamente un file differente."""
        with isolated_directory("external_spice_model_bad_hash") as temporary_root:
            model_path = temporary_root / "device.lib"
            model_path.write_text(".SUBCKT DEVICE A B\n.ENDS DEVICE\n", encoding="utf-8")
            registry_path = temporary_root / "models.yaml"
            registry_path.write_text("# registry\n", encoding="utf-8")
            registry = {
                "models": {
                    "DEVICE": {
                        "file": "device.lib",
                        "sha256": "0" * 64,
                    }
                }
            }

            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                self.spice_emit.resolve_model_entries(
                    spice_models=registry,
                    spice_models_source=registry_path,
                    requested_models={"DEVICE"},
                )

    def test_external_spice_model_accepts_legacy_cp1252_text(self) -> None:
        """I modelli vendor legacy restano byte-identici e vengono decodificati."""
        with isolated_directory("external_spice_model_cp1252") as temporary_root:
            model_path = temporary_root / "device.lib"
            model_bytes = "* curva tensione–corrente\n.SUBCKT DEVICE A B\n.ENDS DEVICE\n".encode(
                "cp1252"
            )
            model_path.write_bytes(model_bytes)
            model_sha256 = hashlib.sha256(model_bytes).hexdigest()
            registry_path = temporary_root / "models.yaml"
            registry_path.write_text("# registry\n", encoding="utf-8")
            registry = {
                "models": {
                    "DEVICE": {
                        "file": "device.lib",
                        "sha256": model_sha256,
                    }
                }
            }

            resolved = self.spice_emit.resolve_model_entries(
                spice_models=registry,
                spice_models_source=registry_path,
                requested_models={"DEVICE"},
            )

            self.assertIn("tensione–corrente", resolved["DEVICE"]["text"])
            self.assertEqual(resolved["DEVICE"]["source"]["encoding"], "cp1252")
            self.assertEqual(
                resolved["DEVICE"]["source"]["sha256"],
                model_sha256.upper(),
            )

    def test_ngspice_command_uses_only_report_defines_before_batch_mode(self) -> None:
        """Le opzioni del modello vengono aggiunte senza conoscere il dispositivo."""
        self.assertEqual(
            self.spice_run.build_ngspice_command(
                "ngspice",
                "07_netlist.cir",
                {"ngbehavior": "ps"},
            ),
            ["ngspice", "-D", "ngbehavior=ps", "-b", "07_netlist.cir"],
        )

    def test_scenario_copy_keeps_the_external_model_bundle(self) -> None:
        """Una run scenario deve restare eseguibile nella propria cartella."""
        with isolated_directory("scenario_external_model_bundle") as temporary_root:
            output_dir = temporary_root / "base"
            scenario_dir = output_dir / "scenarios" / "scenario_1"
            output_dir.mkdir()
            bundle_name = "07_external_models.lib"
            (output_dir / bundle_name).write_text("* model bundle\n", encoding="utf-8")

            copied = scenario_runtime.copy_base_run(output_dir, scenario_dir)

            self.assertIn(bundle_name, copied["copied_files"])
            self.assertTrue((scenario_dir / "base_snapshot" / bundle_name).is_file())
            self.assertTrue((scenario_dir / "run" / bundle_name).is_file())

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

    def test_agent_prompt_requires_gain_threshold_for_all_signal_scenarios(self) -> None:
        """Il prompt deve allinearsi al validatore sui sintomi di guadagno."""
        prompt = build_autonomous_prompt(
            JSON_TO_SPICE_DIR,
            {"symptom": "L'audio e troppo basso", "iterations": []},
            remaining_budget=5,
        )

        self.assertIn("sia `correction` sia `diagnostic`", prompt)
        self.assertIn('"min_ratio": NUMERO_POSITIVO', prompt)
        self.assertIn("`min_ratio` e' obbligatorio", prompt)

    def test_agent_prompt_keeps_causality_and_quality_objective_driven(self) -> None:
        """Le regole generali evitano falsi colli di bottiglia e THD accessoria."""
        prompt = build_autonomous_prompt(
            JSON_TO_SPICE_DIR,
            {"symptom": "Il segnale e debole", "iterations": []},
            remaining_budget=5,
        )

        self.assertIn("rapporto gia prossimo all'unita", prompt)
        self.assertIn("meaningful_improvement_count", prompt)
        self.assertIn('Usa `quality="thd"` soltanto quando', prompt)

    def test_agent_prompt_does_not_use_diode_timing_as_audio_evidence(self) -> None:
        """Un diodo periodico non prova che la modulazione sonora sia migliorata."""
        prompt = build_autonomous_prompt(
            JSON_TO_SPICE_DIR,
            {
                "symptom": "La sirena emette quasi sempre lo stesso tono",
                "iterations": [],
            },
            remaining_budget=5,
        )

        self.assertIn("Un normale diodo non e un indicatore luminoso", prompt)
        self.assertIn("nodo che controlla la", prompt)
        self.assertIn("resistenza in serie tra un oscillatore modulante", prompt)

    def test_input_source_constraint_rejects_source_stimulus_actions(self) -> None:
        """Un vincolo esplicito sull'ingresso e applicato dal contratto, non dal modello."""
        self.assertTrue(
            symptom_forbids_source_stimulus_changes(
                "Aumenta il volume senza modificare il segnale in ingresso"
            )
        )
        scenario = {
            "title": "Iniezione interna",
            "hypothesis": "Isola uno stadio",
            "intent": "diagnostic",
            "analysis": "tran",
            "actions": [
                {
                    "type": "add_voltage_source_between_nodes",
                    "positive": "N001",
                    "negative": "0",
                    "value": "SIN(0 1m 1k)",
                }
            ],
            "compare": ["v(N001)", "v(N002)"],
            "gain": {"input": "v(N001)", "output": "v(N002)", "min_ratio": 1.0},
            "expect": {"v(N002)": "magnitude_increased"},
        }

        with self.assertRaisesRegex(AutonomousDecisionError, "vincolo utente"):
            validate_scenario(
                scenario,
                1,
                require_gain_comparison=True,
                forbid_source_stimulus_actions=True,
            )

    def test_optional_quality_does_not_become_unrequested_success_criterion(self) -> None:
        """La THD proposta spontaneamente viene ignorata fuori dai sintomi di qualita."""
        scenario = {
            "title": "Aumenta uscita",
            "hypothesis": "La modifica aumenta il trasferimento",
            "intent": "correction",
            "analysis": "tran",
            "actions": [{"type": "change_component_value", "target": "R1", "value": "2k"}],
            "compare": ["v(N001)", "v(N002)"],
            "gain": {"input": "v(N001)", "output": "v(N002)", "min_ratio": 2.0},
            "quality": "thd",
            "expect": {"v(N002)": "magnitude_increased"},
        }

        normalized = validate_scenario(scenario, 1, require_gain_comparison=True)

        self.assertNotIn("quality", normalized)
        self.assertTrue(symptom_requests_correction("Vorrei aumentare il volume"))

    def test_excessive_temporal_rate_implies_a_correction_request(self) -> None:
        """Un ritmo esplicitamente eccessivo non si chiude con la sola localizzazione."""
        self.assertTrue(
            symptom_requests_correction(
                "La lampada lampeggia troppo velocemente: quale parte conviene controllare?"
            )
        )
        self.assertTrue(symptom_requests_correction("Vorrei rallentare il lampeggio"))
        self.assertTrue(symptom_requests_correction("The indicator is blinking too fast"))
        self.assertFalse(
            symptom_requests_correction(
                "La lampada lampeggia: quale parte del circuito imposta il periodo?"
            )
        )

    def test_qualitative_blinking_policy_is_fixed_across_corrections(self) -> None:
        """Una richiesta qualitativa non permette soglie Hz variabili tra run."""
        policy = temporal_correction_policy_for_symptom(
            "La lampada lampeggia troppo velocemente."
        )
        self.assertEqual(policy["kind"], "min_relative_period_increase")
        self.assertEqual(policy["min_relative_period_increase"], 0.25)

        decision = {
            "decision": "run_scenarios",
            "scenarios": [
                {
                    "intent": "correction",
                    "temporal_expect": {
                        "target": "Rlamp1",
                        "required_state": "blinking",
                        "require_regular_period": True,
                        "max_frequency_hz": 2.53,
                        "min_relative_period_increase": 0.1,
                    },
                },
                {
                    "intent": "diagnostic",
                    "temporal_expect": {
                        "target": "Rlamp1",
                        "max_frequency_hz": 3.0,
                    },
                },
            ],
        }
        normalized = apply_temporal_correction_policy(decision, policy)
        correction = normalized["scenarios"][0]["temporal_expect"]
        diagnostic = normalized["scenarios"][1]["temporal_expect"]

        self.assertNotIn("max_frequency_hz", correction)
        self.assertEqual(correction["min_relative_period_increase"], 0.25)
        self.assertEqual(diagnostic["max_frequency_hz"], 3.0)

    def test_explicit_blinking_frequency_becomes_session_policy(self) -> None:
        """Una soglia numerica dichiarata dall'utente non viene sostituita."""
        policy = temporal_correction_policy_for_symptom(
            "La lampada lampeggia troppo velocemente: portala sotto 1,8 Hz."
        )
        self.assertEqual(policy["kind"], "max_frequency_hz")
        self.assertEqual(policy["max_frequency_hz"], 1.8)

        decision = {
            "decision": "run_scenarios",
            "scenarios": [
                {
                    "intent": "correction",
                    "temporal_expect": {
                        "target": "Rlamp1",
                        "max_frequency_hz": 2.5,
                        "min_relative_period_increase": 0.1,
                    },
                }
            ],
        }
        expectation = apply_temporal_correction_policy(
            decision, policy
        )["scenarios"][0]["temporal_expect"]
        self.assertEqual(expectation["max_frequency_hz"], 1.8)
        self.assertNotIn("min_relative_period_increase", expectation)

    def test_resolved_answer_exposes_verified_correction(self) -> None:
        """La UI non perde la modifica misurata presente nel campo strutturato."""
        decision = {
            "decision": "stop",
            "final_status": "resolved",
            "final_answer": "Controlla la rete di temporizzazione.",
            "verified_correction": "C4 da 10 uF a 22 uF riduce la frequenza.",
        }
        exposed = expose_verified_correction_in_answer(decision)
        self.assertIn("Correzione verificata:", exposed["final_answer"])
        self.assertIn("C4 da 10 uF a 22 uF", exposed["final_answer"])

    def test_chat_scenario_prompt_requires_gain_threshold_for_low_volume(self) -> None:
        """CHAT deve rendere esplicito il contratto applicato al registry."""
        prompt = "\n".join(build_scenario_answer_format())

        self.assertIn("volume basso", prompt)
        self.assertIn("sia `correction` sia `diagnostic`", prompt)
        self.assertIn("`min_ratio` e' obbligatorio", prompt)

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

    def test_diode_viewer_override_disables_led_temporal_profile(self) -> None:
        """La classe semantica risolta prevale su un falso rilevamento LED."""
        times = [index * 0.1 for index in range(12)]
        profiles = led_transient_profiles(
            [
                {
                    "id": "Dled12_1",
                    "source_component_id": "led12.1",
                    "kind": "diode",
                    "viewer_kind": "diode",
                    "nodes": ["N001", "N002"],
                }
            ],
            times,
            {
                "N001": [5.0, 5.0, 0.0, 0.0] * 3,
                "N002": [0.0] * 12,
            },
        )

        self.assertEqual(profiles, {})

    def test_pulsating_lamp_profile_uses_complete_differential_trace(self) -> None:
        """Una lampada espone periodo e frequenza senza dipendere da un profilo LED."""
        times = [index * 0.1 for index in range(24)]
        waveform = ([0.0, 0.0, 12.0, 12.0] * 6)
        profiles = pulsating_load_transient_profiles(
            [
                {
                    "id": "RLAMP1",
                    "source_component_id": "lamp1.1",
                    "kind": "resistor",
                    "nodes": ["N001", "0"],
                    "class_name": "Lamp",
                    "viewer_kind": "lamp",
                    "parameters": {
                        "spice_override": {"semantic_role": "lamp_equivalent"}
                    },
                }
            ],
            times,
            {"N001": waveform, "0": [0.0] * len(times)},
        )
        profile = profiles["RLAMP1"]
        self.assertEqual(profile["source_component_id"], "lamp1.1")
        self.assertEqual(profile["state"], "blinking")
        self.assertTrue(profile["regular_period"])
        self.assertAlmostEqual(profile["period_s"], 0.4)
        self.assertAlmostEqual(profile["frequency_hz"], 2.5)
        self.assertAlmostEqual(profile["duty_cycle"], 0.5)
        with isolated_directory("load_profile_alias") as run_dir:
            scenario_runtime.write_json(
                run_dir / "13_viewer_model.json",
                {"transient": {"load_profiles": profiles}},
            )
            self.assertEqual(
                scenario_runtime.load_transient_component_profile(run_dir, "lamp1.1"),
                profile,
            )

    def test_lamp_rate_scenario_requires_a_measurable_temporal_correction(self) -> None:
        """CHAT non registra un generico changed come prova di rallentamento."""
        scenario = {
            "title": "Rallentare il lampeggio della lampada",
            "hypothesis": "Aumentare la costante RC dovrebbe ridurre la frequenza della lampada",
            "intent": "correction",
            "analysis": "tran",
            "actions": [
                {"type": "change_component_value", "target": "C1", "value": "22u"}
            ],
            "compare": ["v(N001)"],
            "expect": {"v(N001)": "changed"},
        }
        self.assertFalse(self.web_chat.scenario_is_executable(scenario))

        scenario["temporal_expect"] = {
            "target": "RLAMP1",
            "required_state": "blinking",
            "require_regular_period": True,
            "max_frequency_hz": 1.5,
            "min_relative_period_increase": 0.5,
        }
        self.assertTrue(self.web_chat.scenario_is_executable(scenario))
        self.assertEqual(
            validate_scenario(
                scenario,
                1,
                require_temporal_expectation=True,
            ),
            scenario,
        )

        evaluation = scenario_runtime.evaluate_temporal_expectation(
            {
                "state": "blinking",
                "regular_period": True,
                "period_s": 0.35,
                "frequency_hz": 2.86,
            },
            {
                "state": "blinking",
                "regular_period": True,
                "period_s": 0.78,
                "frequency_hz": 1.28,
            },
            scenario["temporal_expect"],
        )
        self.assertTrue(evaluation["available"])
        self.assertTrue(evaluation["met"])
        self.assertEqual(
            [condition["criterion"] for condition in evaluation["conditions"]],
            [
                "required_state",
                "require_regular_period",
                "max_frequency_hz",
                "min_relative_period_increase",
            ],
        )

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

    def test_requested_correction_cannot_stop_while_budget_remains(self) -> None:
        """AGENT deve usare il budget per una correzione distinta prima dello stop."""
        decision = {
            "decision": "stop",
            "reason": "I test diagnostici non hanno risolto il sintomo.",
            "final_status": "inconclusive",
            "final_answer": "Non e stata verificata una correzione.",
            "final_cause": "",
            "verified_correction": "",
        }

        with self.assertRaisesRegex(
            AutonomousDecisionError,
            "scenario correttivo distinto",
        ):
            validate_decision(
                decision,
                remaining_budget=3,
                require_verified_correction=True,
            )

        accepted = validate_decision(
            decision,
            remaining_budget=3,
            require_verified_correction=False,
        )
        self.assertEqual(accepted["final_status"], "inconclusive")

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
