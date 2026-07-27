# Agent input preview

This file is a local preview of the evidence that will be provided to the read-only diagnostic agent.
The agent remains read-only: it can inspect base outputs and existing scenario artifacts, but it does not modify files.

## User problem

Concludi esperimento

## Circuit

- Batch: `batchChatAgentEvaluation`
- Circuit: `c02`
- Agent mode: `graph_grounded_readonly`

## Technical summary

```json
{
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_message": "ngspice completed successfully.",
  "emitted_elements": 12,
  "skipped_elements": 0,
  "emit_warnings_count": 0,
  "skipped_components_count": 0,
  "node_count": 8,
  "ground_groups_count": 0,
  "singleton_nodes_count": 0,
  "bound_components": 11,
  "missing_components": 0,
  "unsupported_components": 0,
  "spice_ready_components": 11,
  "rules_missing_components": 0,
  "has_tran_csv": true,
  "has_tran_plot": true,
  "led_profiles": {
    "Dled12_1": {
      "state": "blinking",
      "regular_period": true,
      "frequency_hz": 1.6682002709791153,
      "duty_cycle": 0.51736989343253,
      "on_fraction": 0.56591796875,
      "pulse_count": 6,
      "voltage_min": 1.0354889700000003,
      "voltage_max": 1.7242087499999998,
      "anode_node": "N002",
      "cathode_node": "N003"
    },
    "Dled12_2": {
      "state": "blinking",
      "regular_period": true,
      "frequency_hz": 1.6683042880583607,
      "duty_cycle": 0.5169728732137875,
      "on_fraction": 0.53076171875,
      "pulse_count": 7,
      "voltage_min": 1.0810698500000004,
      "voltage_max": 1.7242138599999999,
      "anode_node": "N002",
      "cathode_node": "N004"
    }
  }
}
```

## Image policy

- Included by default: `False`
- Can be requested: `True`
- Path: `outputs\demo_workspaces\chat_agent_evaluation\input\images\c02.jpg`
- Policy: Only request the image if structured outputs suggest that the Graph JSON may be incomplete or wrong.

## Agent rules

- Treat this file as a manifest, not as the full diagnostic evidence.
- Load the referenced artifacts needed for the answer.
- Use graph, node map, component rules, netlist, stdout and stderr as evidence.
- If executed_scenarios are available, use them as evidence for questions about scenario outcomes.
- Do not invent values, connections, models or simulation results.
- Do not use the image unless image_access is explicitly requested.
- If Graph JSON inconsistency is suspected, explain which structured outputs suggest it.
- In read-only mode, do not modify netlists and do not execute scenarios.
- Never exceed 5 executed scenarios for the same circuit.
- When the scenario budget is exhausted, stop proposing new scenarios and provide a final diagnostic conclusion.

## Scenario outcome summary

```json
{
  "available": true,
  "best_scenario_id": "scenario_3",
  "best_outcome_status": "partially_resolved",
  "best_stop_automation": false,
  "ranking_status": "verified_best",
  "interpretation_rule": "If a user asks which scenario resolves the problem, prefer the scenario with outcome_status='resolved_candidate' and stop_automation=true. Partially resolved scenarios without verified expectations are supporting diagnostics and must not be ranked only by changed_count.",
  "scenarios": [
    {
      "scenario_id": "scenario_3",
      "title": "Ridurre il condensatore di accoppiamento C1",
      "status": "spice_success",
      "spice_status": "success",
      "outcome_status": "partially_resolved",
      "outcome_label": "Ipotesi diagnostica confermata",
      "outcome_technical_label": "Diagnostic hypothesis confirmed",
      "outcome_reason": "I criteri dichiarati dal test diagnostico sono soddisfatti, ma lo scenario non applica una correzione del sintomo utente.",
      "stop_automation": false,
      "comparison_summary": {
        "requested_count": 4,
        "changed_count": 4,
        "activated_count": 0,
        "missing_count": 0,
        "expected_count": 2,
        "expectations_met_count": 2,
        "expectations_failed_count": 0,
        "expectations_missing_count": 0,
        "meaningful_improvement_count": 0,
        "quality_required": false,
        "quality_available": false,
        "quality_improved": false,
        "quality_acceptable": false,
        "quality_output_preserved": false,
        "base_thd": null,
        "scenario_thd": null,
        "gain_required": false,
        "gain_available": false,
        "gain_sufficient": false,
        "scenario_gain": null,
        "min_gain_ratio": null,
        "temporal_required": true,
        "temporal_available": true,
        "temporal_met": true
      },
      "quantity_summary": {
        "changed": [
          "v(N006)",
          "v(N007)",
          "@dled12_1[id]",
          "@dled12_2[id]"
        ],
        "unchanged": [],
        "missing": []
      },
      "led_profiles": {
        "Dled12_1": {
          "state": "blinking",
          "regular_period": true,
          "frequency_hz": 2.2732357077255294,
          "duty_cycle": 0.3326985027098868,
          "on_fraction": 0.4922170803533866,
          "pulse_count": 8,
          "voltage_min": 0.9520402299999997,
          "voltage_max": 1.7242454699999996,
          "anode_node": "N002",
          "cathode_node": "N003"
        },
        "Dled12_2": {
          "state": "blinking",
          "regular_period": true,
          "frequency_hz": 2.274458394026308,
          "duty_cycle": 0.7028213018767853,
          "on_fraction": 0.6123264619267985,
          "pulse_count": 8,
          "voltage_min": 1.0912965899999998,
          "voltage_max": 1.7242338000000004,
          "anode_node": "N002",
          "cathode_node": "N004"
        }
      },
      "ranking_verified": true,
      "score": 30
    }
  ]
}
```


## Executed scenarios

### scenario_3

- Title: `Ridurre il condensatore di accoppiamento C1`
- Status: `spice_success`
- SPICE status: `success`
- Outcome: `partially_resolved`
- Stop automation: `False`
- Comparison: `4/4` changed
- LED profiles: `{"Dled12_1": {"state": "blinking", "regular_period": true, "frequency_hz": 2.2732357077255294, "duty_cycle": 0.3326985027098868, "on_fraction": 0.4922170803533866, "pulse_count": 8, "voltage_min": 0.9520402299999997, "voltage_max": 1.7242454699999996, "anode_node": "N002", "cathode_node": "N003"}, "Dled12_2": {"state": "blinking", "regular_period": true, "frequency_hz": 2.274458394026308, "duty_cycle": 0.7028213018767853, "on_fraction": 0.6123264619267985, "pulse_count": 8, "voltage_min": 1.0912965899999998, "voltage_max": 1.7242338000000004, "anode_node": "N002", "cathode_node": "N004"}}`

#### scenario_definition

- Role: Scenario selected by the user and saved before execution.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\c02\scenarios\scenario_3\scenario.json`

```json
{
  "scenario_id": "scenario_3",
  "title": "Ridurre il condensatore di accoppiamento C1",
  "hypothesis": "Il comportamento osservato potrebbe dipendere dal valore assunto di Cpolarized_capacitor20_1, che non è confermato direttamente dall'evidenza visiva.",
  "intent": "diagnostic",
  "actions": [
    {
      "type": "change_component_value",
      "target": "Cpolarized_capacitor20_1",
      "value": "4.7u"
    }
  ],
  "rerun_from": "07",
  "analysis": "tran",
  "compare": [
    "v(N006)",
    "v(N007)",
    "@dled12_1[id]",
    "@dled12_2[id]"
  ],
  "expect": {
    "v(N007)": "changed",
    "@dled12_1[id]": "changed"
  },
  "measure": {
    "@dled12_1[id]": "tran_abs_peak",
    "@dled12_2[id]": "tran_abs_peak"
  },
  "temporal_expect": {
    "target": "Dled12_1",
    "required_state": "blinking",
    "require_regular_period": true
  }
}
```

#### scenario_status

- Role: Current scenario status, SPICE status and diagnostic outcome.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\c02\scenarios\scenario_3\scenario_status.json`

```json
{
  "status": "spice_success",
  "stage": "scenario_spice_executed",
  "scenario_id": "scenario_3",
  "source": "guided_chat",
  "spice_executed": true,
  "created_or_updated_at": "2026-07-27T14:01:22",
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\c02\\scenarios\\scenario_3\\run\\08_spice_run.json",
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\c02\\scenarios\\scenario_3\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 4,
    "changed_count": 4,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 2,
    "expectations_met_count": 2,
    "expectations_failed_count": 0,
    "expectations_missing_count": 0,
    "meaningful_improvement_count": 0,
    "quality_required": false,
    "quality_available": false,
    "quality_improved": false,
    "quality_acceptable": false,
    "quality_output_preserved": false,
    "base_thd": null,
    "scenario_thd": null,
    "gain_required": false,
    "gain_available": false,
    "gain_sufficient": false,
    "scenario_gain": null,
    "min_gain_ratio": null,
    "temporal_required": true,
    "temporal_available": true,
    "temporal_met": true
  },
  "diagnostic_outcome": {
    "status": "partially_resolved",
    "technical_label": "Diagnostic hypothesis confirmed",
    "label": "Ipotesi diagnostica confermata",
    "reason": "I criteri dichiarati dal test diagnostico sono soddisfatti, ma lo scenario non applica una correzione del sintomo utente.",
    "user_message": "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato.",
    "stop_automation": false,
    "confidence": "low",
    "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
  },
  "controlled_scenario_report": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\c02\\scenarios\\scenario_3\\12_controlled_scenarios.json",
  "executed_scenarios_count": 1,
  "scenario_budget_exhausted": false,
  "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
}
```

#### controlled_scenario_report

- Role: Report produced by the controlled scenario runner.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\c02\scenarios\scenario_3\12_controlled_scenarios.json`

```json
{
  "source_format": "pipeline2.0_controlled_scenario_report",
  "status": "spice_success",
  "scenario_id": "scenario_3",
  "scenario_title": "Ridurre il condensatore di accoppiamento C1",
  "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\c02\\scenarios\\scenario_3",
  "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\c02\\scenarios\\scenario_3\\run",
  "netlist": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\c02\\scenarios\\scenario_3\\run\\07_netlist.cir",
  "applied_actions": [
    {
      "status": "applied",
      "type": "change_component_value",
      "target": "Cpolarized_capacitor20_1",
      "resolved_component_name": "Cpolarized_capacitor20_1",
      "tried_component_names": [
        "Cpolarized_capacitor20_1",
        "CCpolarized_capacitor20_1"
      ],
      "value": "4.7u",
      "normalized_component_value": "4.7u",
      "old_value": "10u",
      "new_value": "4.7u",
      "old_line": "Cpolarized_capacitor20_1 N006 N007 10u",
      "new_line": "Cpolarized_capacitor20_1 N006 N007 4.7u",
      "operation": "updated",
      "spice_executed": false,
      "index": 1
    }
  ],
  "unsupported_actions": [],
  "failed_actions": [],
  "spice_executed": true,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\c02\\scenarios\\scenario_3\\run\\08_spice_run.json",
  "spice_status": "success",
  "spice_exit_code": 0,
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\c02\\scenarios\\scenario_3\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 4,
    "changed_count": 4,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 2,
    "expectations_met_count": 2,
    "expectations_failed_count": 0,
    "expectations_missing_count": 0,
    "meaningful_improvement_count": 0,
    "quality_required": false,
    "quality_available": false,
    "quality_improved": false,
    "quality_acceptable": false,
    "quality_output_preserved": false,
    "base_thd": null,
    "scenario_thd": null,
    "gain_required": false,
    "gain_available": false,
    "gain_sufficient": false,
    "scenario_gain": null,
    "min_gain_ratio": null,
    "temporal_required": true,
    "temporal_available": true,
    "temporal_met": true
  },
  "diagnostic_outcome": {
    "status": "partially_resolved",
    "technical_label": "Diagnostic hypothesis confirmed",
    "label": "Ipotesi diagnostica confermata",
    "reason": "I criteri dichiarati dal test diagnostico sono soddisfatti, ma lo scenario non applica una correzione del sintomo utente.",
    "user_message": "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato.",
    "stop_automation": false,
    "confidence": "low",
    "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
  },
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "created_or_updated_at": "2026-07-27T14:01:22"
}
```

#### scenario_comparison

- Role: Base-vs-scenario comparison used to evaluate the scenario.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\c02\scenarios\scenario_3\scenario_comparison.json`

```json
{
  "source_format": "pipeline2.0_scenario_comparison",
  "scenario_id": "scenario_3",
  "scenario_title": "Ridurre il condensatore di accoppiamento C1",
  "scenario_intent": "diagnostic",
  "base_output_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\c02",
  "scenario_run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\c02\\scenarios\\scenario_3\\run",
  "base_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\c02\\08_ngspice_stdout.txt",
  "scenario_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\c02\\scenarios\\scenario_3\\run\\08_ngspice_stdout.txt",
  "base_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\c02\\08_ngspice_stderr.txt",
  "scenario_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\c02\\scenarios\\scenario_3\\run\\08_ngspice_stderr.txt",
  "quantities": [
    {
      "quantity": "v(N006)",
      "base_value": 7.9058164904,
      "scenario_value": 7.9907786639,
      "delta": 0.08496217349999924,
      "change": "changed",
      "expectation": null,
      "expectation_met": null,
      "relative_change": 0.010746793022981049,
      "meaningful_improvement": false,
      "metric": "v(n006).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": 0.0584625696,
        "max": 7.96427906,
        "mean": 3.582716290773828,
        "vpp": 7.9058164904,
        "final": 2.11781146,
        "abs_peak": 7.96427906
      },
      "scenario_details": {
        "min": 0.0571348761,
        "max": 8.04791354,
        "mean": 4.171880247367122,
        "vpp": 7.9907786639,
        "final": 0.153041664,
        "abs_peak": 8.04791354
      }
    },
    {
      "quantity": "v(N007)",
      "base_value": 9.20831203,
      "scenario_value": 9.49570748,
      "delta": 0.28739545,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 0.03121043781571333,
      "meaningful_improvement": false,
      "metric": "v(n007).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": -7.09556555,
        "max": 2.11274648,
        "mean": -0.7313947796805942,
        "vpp": 9.20831203,
        "final": 1.89001456,
        "abs_peak": 7.09556555
      },
      "scenario_details": {
        "min": -7.15090801,
        "max": 2.34479947,
        "mean": -0.1812623007703618,
        "vpp": 9.49570748,
        "final": -3.5665416,
        "abs_peak": 7.15090801
      }
    },
    {
      "quantity": "@dled12_1[id]",
      "base_value": 0.0153560185,
      "scenario_value": 0.0153587652,
      "delta": 2.746700000000324e-06,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 0.00017886797935287222,
      "meaningful_improvement": false,
      "metric": "@dled12_1[id].abs_peak",
      "measurement": "tran_abs_peak",
      "base_details": {
        "min": 4.93560321e-07,
        "max": 0.0153560185,
        "mean": 0.008380737628104444,
        "vpp": 0.015355524939679,
        "final": 0.011105952,
        "abs_peak": 0.0153560185
      },
      "scenario_details": {
        "min": 9.83531466e-08,
        "max": 0.0153587652,
        "mean": 0.0072643306342186275,
        "vpp": 0.015358666846853402,
        "final": 0.015160361,
        "abs_peak": 0.0153587652
      }
    },
    {
      "quantity": "@dled12_2[id]",
      "base_value": 0.0153564011,
      "scenario_value": 0.0153578929,
      "delta": 1.4917999999995712e-06,
      "change": "changed",
      "expectation": null,
      "expectation_met": null,
      "relative_change": 9.714515727253121e-05,
      "meaningful_improvement": false,
      "metric": "@dled12_2[id].abs_peak",
      "measurement": "tran_abs_peak",
      "base_details": {
        "min": 1.19111177e-06,
        "max": 0.0153564011,
        "mean": 0.007849805817066033,
        "vpp": 0.01535520998823,
        "final": 0.015353888,
        "abs_peak": 0.0153564011
      },
      "scenario_details": {
        "min": 1.45140472e-06,
        "max": 0.0153578929,
        "mean": 0.009004261188867541,
        "vpp": 0.01535644149528,
        "final": 3.75110736e-05,
        "abs_peak": 0.0153578929
      }
    }
  ],
  "summary": {
    "requested_count": 4,
    "changed_count": 4,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 2,
    "expectations_met_count": 2,
    "expectations_failed_count": 0,
    "expectations_missing_count": 0,
    "meaningful_improvement_count": 0,
    "quality_required": false,
    "quality_available": false,
    "quality_improved": false,
    "quality_acceptable": false,
    "quality_output_preserved": false,
    "base_thd": null,
    "scenario_thd": null,
    "gain_required": false,
    "gain_available": false,
    "gain_sufficient": false,
    "scenario_gain": null,
    "min_gain_ratio": null,
    "temporal_required": true,
    "temporal_available": true,
    "temporal_met": true
  },
  "gain_comparison": null,
  "quality_comparison": null,
  "diagnostic_outcome": {
    "status": "partially_resolved",
    "technical_label": "Diagnostic hypothesis confirmed",
    "label": "Ipotesi diagnostica confermata",
    "reason": "I criteri dichiarati dal test diagnostico sono soddisfatti, ma lo scenario non applica una correzione del sintomo utente.",
    "user_message": "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato.",
    "stop_automation": false,
    "confidence": "low",
    "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
  },
  "created_or_updated_at": "2026-07-27T14:01:22",
  "temporal_expectation": {
    "target": "Dled12_1",
    "available": true,
    "met": true,
    "reason": "Criteri temporali verificati.",
    "base_profile": {
      "status": "measured",
      "state": "blinking",
      "threshold_v": null,
      "profile_method": "device_current_hysteresis",
      "anode_node": "N002",
      "cathode_node": "N003",
      "on_fraction": 0.56591796875,
      "duty_cycle": 0.51736989343253,
      "display_duty_cycle": 0.6554274339973888,
      "regular_period": true,
      "period_s": 0.5994484100000002,
      "frequency_hz": 1.6682002709791153,
      "playback_duration_s": 5.994484100000001,
      "playback_slowdown": 10.0,
      "pulse_count": 6,
      "timeline_key_times": [
        0.0,
        0.020331738566666667,
        0.10034534666666667,
        0.20366705766666668,
        0.3001461423333333,
        0.4035830366666667,
        0.5000142833333333,
        0.6034292133333333,
        0.6998304200000001,
        0.8032092733333333,
        0.8997032333333334,
        1.0
      ],
      "timeline_states": [
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        true
      ],
      "voltage_min": 1.0354889700000003,
      "voltage_max": 1.7242087499999998,
      "threshold_current_a": 0.0001,
      "current_min_a": 4.93560321e-07,
      "current_max_a": 0.0153560185,
      "turn_on_current_a": 0.006142703536192601,
      "turn_off_current_a": 0.00230382230127285
    },
    "scenario_profile": {
      "status": "measured",
      "state": "blinking",
      "threshold_v": null,
      "profile_method": "device_current_hysteresis",
      "anode_node": "N002",
      "cathode_node": "N003",
      "on_fraction": 0.4922170803533866,
      "duty_cycle": 0.3326985027098868,
      "display_duty_cycle": 0.5414401821843516,
      "regular_period": true,
      "period_s": 0.439901589,
      "frequency_hz": 2.2732357077255294,
      "playback_duration_s": 4.399015889999999,
      "playback_slowdown": 10.0,
      "pulse_count": 8,
      "timeline_key_times": [
        0.0,
        0.011758168566666666,
        0.10228765066666667,
        0.15131477166666665,
        0.24903730033333335,
        0.2976710786666667,
        0.39567116333333335,
        0.44450653999999995,
        0.5422057466666667,
        0.5910019566666667,
        0.6890019566666666,
        0.7375411266666667,
        0.8353923666666666,
        0.8841772333333333,
        0.9821773333333333,
        1.0
      ],
      "timeline_states": [
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        true
      ],
      "voltage_min": 0.9520402299999997,
      "voltage_max": 1.7242454699999996,
      "threshold_current_a": 0.0001,
      "current_min_a": 9.83531466e-08,
      "current_max_a": 0.0153587652,
      "turn_on_current_a": 0.006143565091887961,
      "turn_off_current_a": 0.00230389838017461
    },
    "conditions": [
      {
        "criterion": "required_state",
        "expected": "blinking",
        "actual": "blinking",
        "met": true
      },
      {
        "criterion": "require_regular_period",
        "expected": true,
        "actual": true,
        "met": true
      }
    ]
  }
}
```


## Loaded artifacts

### graph

- Step: `01`
- Role: Graph JSON copied from Pipeline 1.0.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\c02\01_graph.json`

```json
{
  "image_id": "c02",
  "image_name": "c02.jpg",
  "components": [
    {
      "component_id": "battery2.1",
      "instance_id": "2.1",
      "class_name": "Battery",
      "terminals": [
        {
          "terminal_id": "battery2.1_positive",
          "name": "positive",
          "relative_position": "top"
        },
        {
          "terminal_id": "battery2.1_negative",
          "name": "negative",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "resistor22.1",
      "instance_id": "22.1",
      "class_name": "Resistor",
      "terminals": [
        {
          "terminal_id": "resistor22.1_t1",
          "name": "t1",
          "relative_position": "top"
        },
        {
          "terminal_id": "resistor22.1_t2",
          "name": "t2",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "npn_transistor18.1",
      "instance_id": "18.1",
      "class_name": "NPN_Transistor",
      "terminals": [
        {
          "terminal_id": "npn_transistor18.1_B",
          "name": "B",
          "relative_position": "right"
        },
        {
          "terminal_id": "npn_transistor18.1_C",
          "name": "C",
          "relative_position": "top"
        },
        {
          "terminal_id": "npn_transistor18.1_E",
          "name": "E",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "led12.1",
      "instance_id": "12.1",
      "class_name": "LED",
      "terminals": [
        {
          "terminal_id": "led12.1_anode",
          "name": "anode",
          "relative_position": "top"
        },
        {
          "terminal_id": "led12.1_cathode",
          "name": "cathode",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "polarized_capacitor20.1",
      "instance_id": "20.1",
      "class_name": "Polarized_Capacitor",
      "terminals": [
        {
          "terminal_id": "polarized_capacitor20.1_positive",
          "name": "positive",
          "relative_position": "left"
        },
        {
          "terminal_id": "polarized_capacitor20.1_negative",
          "name": "negative",
          "relative_position": "right"
        }
      ]
    },
    {
      "component_id": "resistor22.2",
      "instance_id": "22.2",
      "class_name": "Resistor",
      "terminals": [
        {
          "terminal_id": "resistor22.2_t1",
          "name": "t1",
          "relative_position": "top"
        },
        {
          "terminal_id": "resistor22.2_t2",
          "name": "t2",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "resistor22.3",
      "instance_id": "22.3",
      "class_name": "Resistor",
      "terminals": [
        {
          "terminal_id": "resistor22.3_t1",
          "name": "t1",
          "relative_position": "top"
        },
        {
          "terminal_id": "resistor22.3_t2",
          "name": "t2",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "polarized_capacitor20.2",
      "instance_id": "20.2",
      "class_name": "Polarized_Capacitor",
      "terminals": [
        {
          "terminal_id": "polarized_capacitor20.2_negative",
          "name": "negative",
          "relative_position": "left"
        },
        {
          "terminal_id": "polarized_capacitor20.2_positive",
          "name": "positive",
          "relative_position": "right"
        }
      ]
    },
    {
      "component_id": "npn_transistor18.2",
      "instance_id": "18.2",
      "class_name": "NPN_Transistor",
      "terminals": [
        {
          "terminal_id": "npn_transistor18.2_B",
          "name": "B",
          "relative_position": "left"
        },
        {
          "terminal_id": "npn_transistor18.2_C",
          "name": "C",
          "relative_position": "top"
        },
        {
          "terminal_id": "npn_transistor18.2_E",
          "name": "E",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "resistor22.4",
      "instance_id": "22.4",
      "class_name": "Resistor",
      "terminals": [
        {
          "terminal_id": "resistor22.4_t1",
          "name": "t1",
          "relative_position": "top"
        },
        {
          "terminal_id": "resistor22.4_t2",
          "name": "t2",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "led12.2",
      "instance_id": "12.2",
      "class_name": "LED",
      "terminals": [
        {
          "terminal_id": "led12.2_anode",
          "name": "anode",
          "relative_position": "top"
        },
        {
          "terminal_id": "led12.2_cathode",
          "name": "cathode",
          "relative_position": "bottom"
        }
      ]
    }
  ],
  "terminal_metadata": {},
  "graph": {
    "battery2.1_negative": [
      "npn_transistor18.1_E",
      "npn_transistor18.2_E"
    ],
    "battery2.1_positive": [
      "led12.1_anode",
      "led12.2_anode",
      "resistor22.2_t1",
      "resistor22.3_t1"
    ],
    "led12.1_anode": [
      "battery2.1_positive",
      "led12.2_anode",
      "resistor22.2_t1",
      "resistor22.3_t1"
    ],
    "led12.1_cathode": [
      "resistor22.1_t1"
    ],
    "led12.2_anode": [
      "battery2.1_positive",
      "led12.1_anode",
      "resistor22.2_t1",
      "resistor22.3_t1"
    ],
    "led12.2_cathode": [
      "resistor22.4_t1"
    ],
    "npn_transistor18.1_B": [
      "polarized_capacitor20.2_negative",
      "resistor22.3_t2"
    ],
    "npn_transistor18.1_C": [
      "polarized_capacitor20.1_positive",
      "resistor22.1_t2"
    ],
    "npn_transistor18.1_E": [
      "battery2.1_negative",
      "npn_transistor18.2_E"
    ],
    "npn_transistor18.2_B": [
      "polarized_capacitor20.1_negative",
      "resistor22.2_t2"
    ],
    "npn_transistor18.2_C": [
      "polarized_capacitor20.2_positive",
      "resistor22.4_t2"
    ],
    "npn_transistor18.2_E": [
      "battery2.1_negative",
      "npn_transistor18.1_E"
    ],
    "polarized_capacitor20.1_negative": [
      "npn_transistor18.2_B",
      "resistor22.2_t2"
    ],
    "polarized_capacitor20.1_positive": [
      "npn_transistor18.1_C",
      "resistor22.1_t2"
    ],
    "polarized_capacitor20.2_negative": [
      "npn_transistor18.1_B",
      "resistor22.3_t2"
    ],
    "polarized_capacitor20.2_positive": [
      "npn_transistor18.2_C",
      "resistor22.4_t2"
    ],
    "resistor22.1_t1": [
      "led12.1_cathode"
    ],
    "resistor22.1_t2": [
      "npn_transistor18.1_C",
      "polarized_capacitor20.1_positive"
    ],
    "resistor22.2_t1": [
      "battery2.1_positive",
      "led12.1_anode",
      "led12.2_anode",
      "resistor22.3_t1"
    ],
    "resistor22.2_t2": [
      "npn_transistor18.2_B",
      "polarized_capacitor20.1_negative"
    ],
    "resistor22.3_t1": [
      "battery2.1_positive",
      "led12.1_anode",
      "led12.2_anode",
      "resistor22.2_t1"
    ],
    "resistor22.3_t2": [
      "npn_transistor18.1_B",
      "polarized_capacitor20.2_negative"
    ],
    "resistor22.4_t1": [
      "led12.2_cathode"
    ],
    "resistor22.4_t2": [
      "npn_transistor18.2_C",
      "polarized_capacitor20.2_positive"
    ]
  },
  "warnings": {
    "unconnected_terminals": [],
    "unmatched_terminals": [],
    "suspicious_matches": []
  }
}
```

### node_map

- Step: `03`
- Role: Maps component terminals to SPICE node names.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\c02\03_node_map.json`

```json
{
  "circuit_id": "c02",
  "source_format": "pipeline2.0_node_map",
  "nodes": [
    {
      "node_id": "N001",
      "kind": "normal",
      "terminals": [
        "battery2.1_negative",
        "npn_transistor18.1_E",
        "npn_transistor18.2_E"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N002",
      "kind": "normal",
      "terminals": [
        "battery2.1_positive",
        "led12.1_anode",
        "led12.2_anode",
        "resistor22.2_t1",
        "resistor22.3_t1"
      ],
      "terminal_count": 5
    },
    {
      "node_id": "N003",
      "kind": "normal",
      "terminals": [
        "led12.1_cathode",
        "resistor22.1_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N004",
      "kind": "normal",
      "terminals": [
        "led12.2_cathode",
        "resistor22.4_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N005",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.1_B",
        "polarized_capacitor20.2_negative",
        "resistor22.3_t2"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N006",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.1_C",
        "polarized_capacitor20.1_positive",
        "resistor22.1_t2"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N007",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.2_B",
        "polarized_capacitor20.1_negative",
        "resistor22.2_t2"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N008",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.2_C",
        "polarized_capacitor20.2_positive",
        "resistor22.4_t2"
      ],
      "terminal_count": 3
    }
  ],
  "terminal_to_node": {
    "battery2.1_negative": "N001",
    "battery2.1_positive": "N002",
    "led12.1_anode": "N002",
    "led12.1_cathode": "N003",
    "led12.2_anode": "N002",
    "led12.2_cathode": "N004",
    "npn_transistor18.1_B": "N005",
    "npn_transistor18.1_C": "N006",
    "npn_transistor18.1_E": "N001",
    "npn_transistor18.2_B": "N007",
    "npn_transistor18.2_C": "N008",
    "npn_transistor18.2_E": "N001",
    "polarized_capacitor20.1_negative": "N007",
    "polarized_capacitor20.1_positive": "N006",
    "polarized_capacitor20.2_negative": "N005",
    "polarized_capacitor20.2_positive": "N008",
    "resistor22.1_t1": "N003",
    "resistor22.1_t2": "N006",
    "resistor22.2_t1": "N002",
    "resistor22.2_t2": "N007",
    "resistor22.3_t1": "N002",
    "resistor22.3_t2": "N005",
    "resistor22.4_t1": "N004",
    "resistor22.4_t2": "N008"
  },
  "component_terminal_nodes": {
    "battery2.1": {
      "positive": "N002",
      "negative": "N001"
    },
    "led12.1": {
      "anode": "N002",
      "cathode": "N003"
    },
    "led12.2": {
      "anode": "N002",
      "cathode": "N004"
    },
    "npn_transistor18.1": {
      "B": "N005",
      "C": "N006",
      "E": "N001"
    },
    "npn_transistor18.2": {
      "B": "N007",
      "C": "N008",
      "E": "N001"
    },
    "polarized_capacitor20.1": {
      "positive": "N006",
      "negative": "N007"
    },
    "polarized_capacitor20.2": {
      "negative": "N005",
      "positive": "N008"
    },
    "resistor22.1": {
      "t1": "N003",
      "t2": "N006"
    },
    "resistor22.2": {
      "t1": "N002",
      "t2": "N007"
    },
    "resistor22.3": {
      "t1": "N002",
      "t2": "N005"
    },
    "resistor22.4": {
      "t1": "N004",
      "t2": "N008"
    }
  },
  "warnings": {
    "ground_groups_count": 0,
    "multiple_ground_groups_merged_as_node_0": false,
    "singleton_nodes": [],
    "original_warnings": {
      "unconnected_terminals": [],
      "unmatched_terminals": [],
      "suspicious_matches": []
    },
    "normalization_warnings": []
  },
  "stats": {
    "nodes_count": 8,
    "normal_nodes_count": 8,
    "ground_nodes_count": 0,
    "ground_groups_count": 0,
    "terminal_to_node_count": 24,
    "singleton_nodes_count": 0
  }
}
```

### values_bound

- Step: `04`
- Role: Values and labels bound to graph components.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\c02\04_values_bound.json`

```json
{
  "circuit_id": "c02",
  "source_format": "pipeline2.0_values_bound",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\data\\batchPipeline2.0\\batchChatAgentEvaluation\\values\\c02_values.yaml",
  "supplies": {
    "VREF_BATTERY_NEGATIVE": {
      "terminal": "battery2.1_negative",
      "type": "dc",
      "value": 0,
      "unit": "V",
      "reference": 0,
      "source": "manual_reference_for_floating_battery_circuit",
      "label_text": "Negativo batteria: riferimento SPICE",
      "node": "N001"
    }
  },
  "components": {
    "battery2.1": {
      "class_name": "Battery",
      "terminal_nodes": {
        "positive": "N002",
        "negative": "N001"
      },
      "value_data": {
        "type": "dc",
        "value": 9,
        "unit": "V",
        "source": "manual_from_image_label",
        "label_text": "Batteria 9 V"
      },
      "status": "bound"
    },
    "led12.1": {
      "class_name": "LED",
      "terminal_nodes": {
        "anode": "N002",
        "cathode": "N003"
      },
      "value_data": {
        "model": "LED_RED_TYP",
        "source": "manual_testbench_assumption",
        "label_text": "L1 LED, colore non specificato",
        "viewer_override": {
          "label": "L1",
          "display_value": "LED"
        }
      },
      "status": "bound"
    },
    "led12.2": {
      "class_name": "LED",
      "terminal_nodes": {
        "anode": "N002",
        "cathode": "N004"
      },
      "value_data": {
        "model": "LED_RED_TYP",
        "source": "manual_testbench_assumption",
        "label_text": "L2 LED, colore non specificato",
        "viewer_override": {
          "label": "L2",
          "display_value": "LED"
        }
      },
      "status": "bound"
    },
    "npn_transistor18.1": {
      "class_name": "NPN_Transistor",
      "terminal_nodes": {
        "B": "N005",
        "C": "N006",
        "E": "N001"
      },
      "value_data": {
        "model": "BC548_TYP",
        "source": "manual_from_image_label",
        "label_text": "Q1 BC548",
        "viewer_override": {
          "label": "Q1",
          "display_value": "BC548"
        }
      },
      "status": "bound"
    },
    "npn_transistor18.2": {
      "class_name": "NPN_Transistor",
      "terminal_nodes": {
        "B": "N007",
        "C": "N008",
        "E": "N001"
      },
      "value_data": {
        "model": "BC548_TYP",
        "source": "manual_from_image_label",
        "label_text": "Q2 BC548",
        "viewer_override": {
          "label": "Q2",
          "display_value": "BC548"
        }
      },
      "status": "bound"
    },
    "polarized_capacitor20.1": {
      "class_name": "Polarized_Capacitor",
      "terminal_nodes": {
        "positive": "N006",
        "negative": "N007"
      },
      "value_data": {
        "value": 10,
        "unit": "uf",
        "source": "manual_testbench_assumption",
        "label_text": "C1 10 uF nominale (valore non visibile)"
      },
      "status": "bound"
    },
    "polarized_capacitor20.2": {
      "class_name": "Polarized_Capacitor",
      "terminal_nodes": {
        "negative": "N005",
        "positive": "N008"
      },
      "value_data": {
        "value": 10,
        "unit": "uf",
        "source": "manual_testbench_assumption",
        "label_text": "C2 10 uF nominale (valore non visibile)"
      },
      "status": "bound"
    },
    "resistor22.1": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N003",
        "t2": "N006"
      },
      "value_data": {
        "value": 470,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R1 470 ohm"
      },
      "status": "bound"
    },
    "resistor22.2": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N002",
        "t2": "N007"
      },
      "value_data": {
        "value": 47,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R2 47 kohm"
      },
      "status": "bound"
    },
    "resistor22.3": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N002",
        "t2": "N005"
      },
      "value_data": {
        "value": 47,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R3 47 kohm"
      },
      "status": "bound"
    },
    "resistor22.4": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N004",
        "t2": "N008"
      },
      "value_data": {
        "value": 470,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R4 470 ohm"
      },
      "status": "bound"
    }
  },
  "nodes": {
    "battery2.1_negative": {
      "label": "GND",
      "source": "manual_from_battery_reference",
      "label_text": "Polo negativo batteria",
      "node": "N001"
    },
    "battery2.1_positive": {
      "label": "VCC",
      "source": "manual_from_image_label",
      "label_text": "+9 V",
      "node": "N002"
    },
    "npn_transistor18.1_B": {
      "label": "Q1_BASE",
      "source": "inferred_from_validated_graph",
      "node": "N005"
    },
    "npn_transistor18.1_C": {
      "label": "Q1_COLLECTOR_L1",
      "source": "inferred_from_validated_graph",
      "node": "N006"
    },
    "npn_transistor18.2_B": {
      "label": "Q2_BASE",
      "source": "inferred_from_validated_graph",
      "node": "N007"
    },
    "npn_transistor18.2_C": {
      "label": "Q2_COLLECTOR_L2",
      "source": "inferred_from_validated_graph",
      "node": "N008"
    }
  },
  "spice_topology_overlay": [],
  "simulation": {
    "analyses": [
      "op",
      "tran"
    ],
    "tran": {
      "step": "1ms",
      "stop": "3s"
    }
  },
  "missing": [],
  "stats": {
    "components_total": 11,
    "bound_components": 11,
    "missing_components": 0,
    "not_required_components": 0,
    "unsupported_components": 0,
    "supplies_count": 1,
    "manual_nodes_count": 6
  }
}
```

### component_rules

- Step: `06`
- Role: SPICE conversion rules for each component.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\c02\06_component_rules.json`

```json
{
  "circuit_id": "c02",
  "source_format": "pipeline2.0_component_rules",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\data\\batchPipeline2.0\\batchChatAgentEvaluation\\values\\c02_values.yaml",
  "spice_classes_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_spice_classes.yaml",
  "supplies": {
    "VREF_BATTERY_NEGATIVE": {
      "status": "spice_ready",
      "spice_prefix": "V",
      "emit_as": "independent_voltage_source",
      "nodes": [
        "N001",
        "0"
      ],
      "parameters": {
        "terminal": "battery2.1_negative",
        "type": "dc",
        "value": 0,
        "unit": "V",
        "reference": 0,
        "source": "manual_reference_for_floating_battery_circuit",
        "label_text": "Negativo batteria: riferimento SPICE",
        "node": "N001"
      }
    }
  },
  "components": {
    "battery2.1": {
      "class_name": "Battery",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "V",
      "emit_as": "independent_voltage_source",
      "node_order": [
        "positive",
        "negative"
      ],
      "nodes": [
        "N002",
        "N001"
      ],
      "parameters": {
        "type": "dc",
        "value": 9,
        "unit": "V",
        "source": "manual_from_image_label",
        "label_text": "Batteria 9 V"
      }
    },
    "led12.1": {
      "class_name": "LED",
      "status": "spice_ready",
      "spice_support": "model",
      "spice_prefix": "D",
      "emit_as": "diode",
      "node_order": [
        "anode",
        "cathode"
      ],
      "nodes": [
        "N002",
        "N003"
      ],
      "parameters": {
        "model": "LED_RED_TYP",
        "source": "manual_testbench_assumption",
        "label_text": "L1 LED, colore non specificato",
        "viewer_override": {
          "label": "L1",
          "display_value": "LED"
        }
      }
    },
    "led12.2": {
      "class_name": "LED",
      "status": "spice_ready",
      "spice_support": "model",
      "spice_prefix": "D",
      "emit_as": "diode",
      "node_order": [
        "anode",
        "cathode"
      ],
      "nodes": [
        "N002",
        "N004"
      ],
      "parameters": {
        "model": "LED_RED_TYP",
        "source": "manual_testbench_assumption",
        "label_text": "L2 LED, colore non specificato",
        "viewer_override": {
          "label": "L2",
          "display_value": "LED"
        }
      }
    },
    "npn_transistor18.1": {
      "class_name": "NPN_Transistor",
      "status": "spice_ready",
      "spice_support": "model",
      "spice_prefix": "Q",
      "emit_as": "bjt_npn",
      "node_order": [
        "C",
        "B",
        "E"
      ],
      "nodes": [
        "N006",
        "N005",
        "N001"
      ],
      "parameters": {
        "model": "BC548_TYP",
        "source": "manual_from_image_label",
        "label_text": "Q1 BC548",
        "viewer_override": {
          "label": "Q1",
          "display_value": "BC548"
        }
      }
    },
    "npn_transistor18.2": {
      "class_name": "NPN_Transistor",
      "status": "spice_ready",
      "spice_support": "model",
      "spice_prefix": "Q",
      "emit_as": "bjt_npn",
      "node_order": [
        "C",
        "B",
        "E"
      ],
      "nodes": [
        "N008",
        "N007",
        "N001"
      ],
      "parameters": {
        "model": "BC548_TYP",
        "source": "manual_from_image_label",
        "label_text": "Q2 BC548",
        "viewer_override": {
          "label": "Q2",
          "display_value": "BC548"
        }
      }
    },
    "polarized_capacitor20.1": {
      "class_name": "Polarized_Capacitor",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "C",
      "emit_as": "capacitor",
      "node_order": [
        "positive",
        "negative"
      ],
      "nodes": [
        "N006",
        "N007"
      ],
      "parameters": {
        "value": 10,
        "unit": "uf",
        "source": "manual_testbench_assumption",
        "label_text": "C1 10 uF nominale (valore non visibile)"
      }
    },
    "polarized_capacitor20.2": {
      "class_name": "Polarized_Capacitor",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "C",
      "emit_as": "capacitor",
      "node_order": [
        "positive",
        "negative"
      ],
      "nodes": [
        "N008",
        "N005"
      ],
      "parameters": {
        "value": 10,
        "unit": "uf",
        "source": "manual_testbench_assumption",
        "label_text": "C2 10 uF nominale (valore non visibile)"
      }
    },
    "resistor22.1": {
      "class_name": "Resistor",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "R",
      "emit_as": "resistor",
      "node_order": [
        "t1",
        "t2"
      ],
      "nodes": [
        "N003",
        "N006"
      ],
      "parameters": {
        "value": 470,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R1 470 ohm"
      }
    },
    "resistor22.2": {
      "class_name": "Resistor",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "R",
      "emit_as": "resistor",
      "node_order": [
        "t1",
        "t2"
      ],
      "nodes": [
        "N002",
        "N007"
      ],
      "parameters": {
        "value": 47,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R2 47 kohm"
      }
    },
    "resistor22.3": {
      "class_name": "Resistor",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "R",
      "emit_as": "resistor",
      "node_order": [
        "t1",
        "t2"
      ],
      "nodes": [
        "N002",
        "N005"
      ],
      "parameters": {
        "value": 47,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R3 47 kohm"
      }
    },
    "resistor22.4": {
      "class_name": "Resistor",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "R",
      "emit_as": "resistor",
      "node_order": [
        "t1",
        "t2"
      ],
      "nodes": [
        "N004",
        "N008"
      ],
      "parameters": {
        "value": 470,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R4 470 ohm"
      }
    }
  },
  "simulation": {
    "analyses": [
      "op",
      "tran"
    ],
    "tran": {
      "step": "1ms",
      "stop": "3s"
    }
  },
  "stats": {
    "components_total": 11,
    "spice_ready_components": 11,
    "not_emitted_components": 0,
    "measurement_components": 0,
    "missing_components": 0,
    "unsupported_components": 0,
    "pin_aware_components": 0,
    "invalid_components": 0,
    "supplies_ready_count": 1
  }
}
```

### netlist

- Step: `07`
- Role: Generated SPICE netlist.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\c02\07_netlist.cir`

```spice
* pipeline2.0 netlist
* circuit: c02

VVREF_BATTERY_NEGATIVE N001 0 DC 0
Vbattery2_1 N002 N001 DC 9
Dled12_1 N002 N003 LED_RED_TYP
Dled12_2 N002 N004 LED_RED_TYP
Qnpn_transistor18_1 N006 N005 N001 BC548_TYP
Qnpn_transistor18_2 N008 N007 N001 BC548_TYP
Cpolarized_capacitor20_1 N006 N007 10u
Cpolarized_capacitor20_2 N008 N005 10u
Rresistor22_1 N003 N006 470
Rresistor22_2 N002 N007 47k
Rresistor22_3 N002 N005 47k
Rresistor22_4 N004 N008 470

.model BC548_TYP NPN(IS=1e-14 BF=250 VAF=30 IKF=100m RB=100 RC=1 RE=0.2 CJE=12p VJE=0.7 MJE=0.33 CJC=4p VJC=0.5 MJC=0.33 TF=0.5n TR=50n)
.model LED_RED_TYP D(IS=1e-15 N=2 RS=10)

.op
.save all
.tran 1ms 3s

.control
set wr_singlescale
set wr_vecnames
save all @dled12_1[id] @dled12_2[id]
run
wrdata 08_tran.csv time v(N001) v(N002) v(N003) v(N004) v(N005) v(N006) v(N007) v(N008) @dled12_1[id] @dled12_2[id]
.endc
.end

```

### spice_emit_report

- Step: `07`
- Role: Report of emitted, skipped and warning components.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\c02\07_spice_emit_report.json`

```json
{
  "circuit_id": "c02",
  "source_format": "pipeline2.0_spice_emit_report",
  "emitted_elements": 12,
  "skipped_elements": 0,
  "skipped_components": [],
  "informational_skips": [],
  "measurement_points": [],
  "analyses": [
    "op",
    "tran"
  ],
  "transient_export": {
    "path": "08_tran.csv",
    "nodes": [
      "N001",
      "N002",
      "N003",
      "N004",
      "N005",
      "N006",
      "N007",
      "N008"
    ],
    "device_currents": [
      "@dled12_1[id]",
      "@dled12_2[id]"
    ]
  },
  "models": [
    "BC548_TYP",
    "LED_RED_TYP"
  ],
  "warnings": []
}
```

### spice_run

- Step: `08`
- Role: Structured ngspice execution report.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\c02\08_spice_run.json`

```json
{
  "source_format": "pipeline2.0_spice_run",
  "status": "success",
  "netlist_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\c02\\07_netlist.cir",
  "command": [
    "C:\\Users\\m.profilo\\Spice64\\bin\\ngspice_con.exe",
    "-b",
    "07_netlist.cir"
  ],
  "exit_code": 0,
  "stdout_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\c02\\08_ngspice_stdout.txt",
  "stderr_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\c02\\08_ngspice_stderr.txt",
  "tran_raw_csv_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\c02\\08_tran_raw.csv",
  "tran_csv_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\c02\\08_tran.csv",
  "tran_plot_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\c02\\08_tran_plot.png",
  "tran_plot_png_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\c02\\08_tran_plot.png",
  "tran_plot_svg_path": null,
  "message": "ngspice completed successfully."
}
```

### ngspice_stdout

- Step: `08`
- Role: Raw ngspice stdout log.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\c02\08_ngspice_stdout.txt`

```text

Note: No compatibility mode selected!


Circuit: * pipeline2.0 netlist

Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

No. of Data Rows : 1

Initial Transient Solution
--------------------------

Node                                   Voltage
----                                   -------
n001                                         0
n002                                         9
n003                                   7.27838
n004                                   7.27838
n006                                  0.151939
n005                                  0.750666
n008                                  0.151939
n007                                  0.750666
vbattery2_1#branch                  -0.0306763
vvref_battery_negative#branch     -2.74216e-13

 Reference value :  2.65963e+00

No. of Data Rows : 4096
Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

No. of Data Rows : 1

Initial Transient Solution
--------------------------

Node                                   Voltage
----                                   -------
n001                                         0
n002                                         9
n003                                   7.27838
n004                                   7.27838
n006                                  0.151939
n005                                  0.750666
n008                                  0.151939
n007                                  0.750666
vbattery2_1#branch                  -0.0306763
vvref_battery_negative#branch     -2.74216e-13


No. of Data Rows : 4096
	Node                                  Voltage
	----                                  -------
	----	-------
	n007                             7.506657e-01
	n008                             1.519389e-01
	n005                             7.506657e-01
	n006                             1.519389e-01
	n004                             7.278381e+00
	n003                             7.278381e+00
	n002                             9.000000e+00
	n001                             0.000000e+00

	Source	Current
	------	-------

	@dled12_2[id]                    1.516264e-02
	@dled12_1[id]                    1.516264e-02
	vvref_battery_negative#branch    -2.74216e-13
	vbattery2_1#branch               -3.06763e-02

 BJT models (Bipolar Junction Transistor)
      model             bc548_typ

       type                   npn
       tnom                    27
         is                 1e-14
        ibe                     0
        ibc                     0
         bf                   250
         nf                     1
        vaf                    30
        ikf                   0.1
        ise                     0
         ne                   1.5
         br                     1
         nr                     1
        var                     0
        ikr                     0
        isc                     0
         nc                     2
         rb                   100
        irb                     0
        rbm                   100
         re                   0.2
         rc                     1
        cje               1.2e-11
        vje                   0.7
        mje                  0.33
         tf                 5e-10
        xtf                     0
        vtf                     0
        itf                     0
        ptf                     0
        cjc                 4e-12
        vjc                   0.5
        mjc                  0.33
       xcjc                     1
         tr                 5e-08
        cjs                     0
        vjs                  0.75
        mjs                     0
        xtb                     0
         eg                  1.11
        xti                     3
         fc                   0.5
         kf                     0
         af                     0
        iss                     0
         ns                     1
        rco                  0.01
         vo                    10
      gamma                 1e-11
        qco                     0
       tlev                     0
      tlevc                     0
       tbf1                     0
       tbf2                     0
       tbr1                     0
       tbr2                     0
      tikf1                     0
      tikf2                     0
      tikr1                     0
      tikr2                     0
      tirb1                     0
      tirb2                     0
       tnc1                     0
       tnc2                     0
       tne1                     0
       tne2                     0
       tnf1                     0
       tnf2                     0
       tnr1                     0
       tnr2                     0
       trb1                     0
       trb2                     0
       trc1                     0
       trc2                     0
       tre1                     0
       tre2                     0
       trm1                     0
       trm2                     0
      tvaf1                     0
      tvaf2                     0
      tvar1                     0
      tvar2                     0
        ctc                     0
        cte                     0
        cts                     0
       tvjc                     0
       tvje                     0
       tvjs                     0
      titf1                     0
      titf2                     0
       ttf1                     0
       ttf2                     0
       ttr1                     0
       ttr2                     0
      tmje1                     0
      tmje2                     0
      tmjc1                     0
      tmjc2                     0
      tmjs1                     0
      tmjs2                     0
       tns1                     0
       tns2                     0
        nkf                   0.5
       tis1                     0
       tis2                     0
      tise1                     0
      tise2                     0
      tisc1                     0
      tisc2                     0
      tiss1                     0
      tiss2                     0
   quasimod                     0
         vg                 1.206
         cn                  2.42
          d                  0.87
    vbe_max                 1e+99
    vbc_max                 1e+99
    vce_max                 1e+99
     pd_max                 1e+99
     ic_max                 1e+99
     ib_max                 1e+99
     te_max                 1e+99
       rth0                     0

 Capacitor models (Fixed capacitor)
      model                     C

        cap                     0
         cj                     0
       cjsw                     0
       defw                 1e-05
       defl                     0
     narrow                     0
      short                     0
        del                     0
        tc1                     0
        tc2                     0
         di                     0
      thick                     0
     bv_max                 1e+99

 Diode models (Junction Diode model)
      model           led_red_typ

      level                     1
         is                 1e-15
        jsw                     0
         rs                    10
        rsw                     0
        trs                     0
       trs2                     0
          n                     2
         ns                     1
         tt                     0
       ttt1                     0
       ttt2                     0
        cjo                     0
         vj                     1
          m                   0.5
        tm1                     0
        tm2                     0
        cjp                     0
        php                     1
       mjsw                  0.33
        ikf                     0
        ikr                     0
        ikp                     0
        nbv                     2
       area                     1
         pj                     0
       tlev                     0
      tlevc                     0
         eg                  1.11
       gap1              0.000702
       gap2                  1108
        xti                     3
        cta                     0
        ctp                     0
        tpb                     0
       tphp                     0
       jtun                     0
     jtunsw                     0
       ntun                    30
     xtitun                     3
        keg                     1
         kf                     0
         af                     1
         fc                   0.5
        fcs                   0.5
         bv                     0
        ibv                 0.001
        tcv                     0
        isr                 1e-14
         nr                     2
         vp                     0
     fv_max                 1e+99
     bv_max                 1e+99
     id_max                 1e+99
     te_max                 1e+99
     pd_max                 1e+99
       rth0                     0
       cth0                 1e-05
         lm                     0
         lp                     0
         wm                     0
         wp                     0
        xom                 10000
        xoi                 10000
         xm                     0
         xp                     0
         xw                     0

 Resistor models (Simple linear resistor)
      model                     R

        rsh                     0
     narrow                     0
      short                     0
        tc1                     0
        tc2                     0
        tce                     0
       defw                 1e-05
          l                 1e-05
         kf                     0
         af                     0
          r                     0
     bv_max                 1e+99
         lf                     1
         wf                     1
         ef                     1

 BJT: Bipolar Junction Transistor
     device   qnpn_transistor18_2   qnpn_transistor18_1
      model             bc548_typ             bc548_typ
         ic             0.0156536          -3.69626e-05
         ib             0.0112939           3.35936e-05
         ie            -0.0269475           3.36906e-06
        vbe              0.755738              -7.06324
        vbc              0.717297              -9.18109
         gm               0.82982           2.25912e-22
        gpi            0.00757202           6.27605e-08
        gmu              0.428142           1.74068e-08
         gx                  0.01                  0.01
         go              0.308085           1.40251e-22
        cpi           5.57675e-10           5.42437e-12
        cmu           2.14028e-08           1.50441e-12
        cbx                     0                     0
       csub                     0                     0

 Capacitor: Fixed capacitor
     device cpolarized_capacitor2 cpolarized_capacitor2
      model                     C                     C
capacitance                 1e-05                 1e-05
      dtemp                     0                     0
     bv_max                 1e+99                 1e+99
          i          -0.000308106             0.0111376
          p           -0.00219352            0.00253711

 Diode: Junction Diode model
     device              dled12_2              dled12_1
      model           led_red_typ           led_red_typ
    thermal                     0                     0
         vd               1.57064               1.55389
         id             0.0153539              0.011106
         gd              0.296809              0.214691
         cd                     0                     0

 Resistor: Simple linear resistor
     device         rresistor22_4         rresistor22_3         rresistor22_2
      model                     R                     R
```

> Artifact truncated in this preview. The original file remains available through the manifest path.

### ngspice_stderr

- Step: `08`
- Role: Raw ngspice stderr log.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\c02\08_ngspice_stderr.txt`

```text

```

### tran_csv

- Step: `08`
- Role: Clean transient CSV, when .tran data is available.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\c02\08_tran.csv`

```csv
time,v(N001),v(N002),v(N003),v(N004),v(N005),v(N006),v(N007),v(N008),@dled12_1[id],@dled12_2[id]
0.0,0.0,9.0,7.27838058,7.27838058,0.750665691,0.15193889,0.750665691,0.15193889,0.0151626419,0.0151626419
1e-05,0.0,9.0,7.27838058,7.27838058,0.7506657,0.1519389,0.7506657,0.1519389,0.0151626419,0.0151626419
2e-05,0.0,9.0,7.27838058,7.27838058,0.7506657,0.1519389,0.7506657,0.1519389,0.0151626419,0.0151626419
4e-05,0.0,9.0,7.27838058,7.27838058,0.7506657,0.1519389,0.7506657,0.1519389,0.0151626419,0.0151626419
8e-05,0.0,9.0,7.27838058,7.27838058,0.7506657,0.1519389,0.7506657,0.1519389,0.0151626419,0.0151626419
0.00016,0.0,9.0,7.27838058,7.27838058,0.7506657,0.151938901,0.7506657,0.151938901,0.0151626419,0.0151626419
0.00032,0.0,9.0,7.27838058,7.27838058,0.7506657,0.151938902,0.7506657,0.151938902,0.0151626419,0.0151626419
0.00064,0.0,9.0,7.27838058,7.27838058,0.750665699,0.151938904,0.750665699,0.151938904,0.0151626419,0.0151626419
0.00128,0.0,9.0,7.27838058,7.27838058,0.750665697,0.151938907,0.750665697,0.151938907,0.0151626419,0.0151626419
0.00228,0.0,9.0,7.27838058,7.27838058,0.750665696,0.151938911,0.750665696,0.151938911,0.0151626419,0.0151626419
0.00328,0.0,9.0,7.27838058,7.27838058,0.750665695,0.151938914,0.750665695,0.151938914,0.0151626418,0.0151626418
0.00428,0.0,9.0,7.27838058,7.27838058,0.750665694,0.151938916,0.750665694,0.151938916,0.0151626418,0.0151626418
0.00528,0.0,9.0,7.27838058,7.27838058,0.750665693,0.151938918,0.750665693,0.151938918,0.0151626418,0.0151626418
0.00628,0.0,9.0,7.27838058,7.27838058,0.750665692,0.151938919,0.750665692,0.151938919,0.0151626418,0.0151626418
0.00728,0.0,9.0,7.27838058,7.27838058,0.750665692,0.15193892,0.750665692,0.15193892,0.0151626418,0.0151626418
0.00828,0.0,9.0,7.27838058,7.27838058,0.750665692,0.151938921,0.750665692,0.151938921,0.0151626418,0.0151626418
0.00928,0.0,9.0,7.27838058,7.27838058,0.750665691,0.151938921,0.750665692,0.151938921,0.0151626418,0.0151626418
0.01028,0.0,9.0,7.27838058,7.27838058,0.750665691,0.151938922,0.750665691,0.151938921,0.0151626418,0.0151626418
0.01128,0.0,9.0,7.27838058,7.27838058,0.750665691,0.151938922,0.750665691,0.151938922,0.0151626418,0.0151626418
0.01228,0.0,9.0,7.27838058,7.27838058,0.750665691,0.151938922,0.750665691,0.151938922,0.0151626418,0.0151626418
0.01328,0.0,9.0,7.27838058,7.27838058,0.750665691,0.151938923,0.750665691,0.151938922,0.0151626418,0.0151626418
0.01428,0.0,9.0,7.27838058,7.27838058,0.75066569,0.151938924,0.750665692,0.151938921,0.0151626418,0.0151626418
0.01528,0.0,9.0,7.27838058,7.27838058,0.75066569,0.151938926,0.750665692,0.151938919,0.0151626418,0.0151626418
0.01628,0.0,9.0,7.27838058,7.27838058,0.750665688,0.15193893,0.750665694,0.151938915,0.0151626418,0.0151626418
0.01728,0.0,9.0,7.27838058,7.27838058,0.750665684,0.151938939,0.750665698,0.151938906,0.0151626418,0.0151626419
0.01828,0.0,9.0,7.27838058,7.27838058,0.750665675,0.151938959,0.750665707,0.151938886,0.0151626418,0.0151626419
0.01928,0.0,9.0,7.27838058,7.27838058,0.750665654,0.151939004,0.750665727,0.151938842,0.0151626417,0.015162642
0.02028,0.0,9.0,7.27838059,7.27838058,0.750665609,0.151939104,0.750665773,0.151938741,0.0151626415,0.0151626422
0.02128,0.0,9.0,7.27838059,7.27838057,0.750665508,0.15193933,0.750665874,0.151938515,0.015162641,0.0151626427
0.02228,0.0,9.0,7.27838061,7.27838056,0.75066528,0.151939836,0.750666102,0.151938009,0.0151626399,0.0151626437
0.02328,0.0,9.0,7.27838064,7.27838052,0.750664769,0.151940971,0.750666613,0.151936875,0.0151626376,0.0151626461
0.02428,0.0,9.0,7.27838071,7.27838045,0.750663623,0.151943517,0.750667759,0.151934329,0.0151626323,0.0151626513
0.02528,0.0,9.0,7.27838087,7.2783803,0.750661052,0.151949227,0.75067033,0.15192862,0.0151626205,0.0151626631
0.02628,0.0,9.0,7.27838122,7.27837994,0.750655288,0.151962036,0.750676097,0.151915815,0.015162594,0.0151626896
0.02728,0.0,9.0,7.27838202,7.27837914,0.750642364,0.151990774,0.750689036,0.151887103,0.0151625346,0.015162749
0.02828,0.0,9.0,7.27838381,7.27837736,0.750613395,0.152055266,0.750718078,0.151822739,0.0151624012,0.0151628822
0.02928,0.0,9.0,7.27838783,7.27837336,0.750548522,0.152200095,0.75078332,0.151678554,0.0151621016,0.0151631804
0.03028,0.0,9.0,7.27839686,7.27836441,0.750403534,0.152525829,0.750930162,0.151356058,0.0151614278,0.0151638476
0.03128,0.0,9.0,7.27841726,7.27834447,0.75008096,0.153260881,0.751262065,0.150637298,0.0151599073,0.0151653345
0.03228,0.0,9.0,7.27846361,7.27830039,0.749370877,0.154931538,0.752019037,0.149048544,0.0151564516,0.0151686213
0.03328,0.0,9.0,7.27857051,7.27820491,0.747848119,0.158784324,0.75377675,0.145606355,0.0151484834,0.0151757433
0.03428,0.0,9.0,7.27882907,7.27802644,0.74523719,0.168099903,0.758114436,0.139171599,0.015129211,0.0151890529
0.03528,0.0,9.0,7.27940791,7.27774455,0.741667646,0.188944777,0.767462004,0.129004873,0.0150860918,0.0152100844
0.03628,0.0,9.0,7.28056665,7.27741323,0.738928252,0.230628657,0.784831711,0.117050953,0.0149998681,0.0152348133
0.03728,0.0,9.0,7.2827421,7.27706916,0.737115709,0.308726699,0.815464072,0.104632196,0.0148383419,0.0152605043
0.03828,0.0,9.0,7.28726654,7.27667438,0.734106098,0.470462974,0.88247147,0.0903767422,0.0145038374,0.015289995
0.0391723151,0.0,9.0,7.2757924,7.32623908,1.94781393,0.0585042248,0.421917976,1.82147531,0.0153559323,0.0117126796
0.0398365496,0.0,9.0,7.27581267,7.34464071,1.82035723,0.0592369894,0.43476485,2.4302581,0.0153544163,0.0104622262
0.0404563892,0.0,9.0,7.27583549,7.36062737,1.71373669,0.0600619112,0.446877713,2.93922545,0.0153527097,0.00940737519
0.0412062853,0.0,9.0,7.27586614,7.3785239,1.59898948,0.0611703749,0.461621081,3.4875699,0.0153504165,0.00827887358
0.0422062853,0.0,9.0,7.27591379,7.4002882,1.46692155,0.0628928853,0.481488955,4.11846416,0.015346853,0.00698324264
0.0432062853,0.0,9.0,7.27596764,7.41997727,1.35562382,0.0648395044,0.501538033,4.65068405,0.0153428258,0.00589264427
0.0442062853,0.0,9.0,7.27602844,7.43789619,1.26159933,0.0670372193,0.521794396,5.09954321,0.0153382792,0.00497565671
0.0452062853,0.0,9.0,7.27609447,7.45429975,1.18207799,0.0694238858,0.542194433,5.47796014,0.0153333417,0.00420533334
0.0462062853,0.0,9.0,7.27616762,7.46935249,1.11418467,0.0720677442,0.562803539,5.79594449,0.0153278721,0.00356071887
0.0472062853,0.0,9.0,7.27624732,7.48311411,1.0552342,0.0749480077,0.583594973,6.06094516,0.0153219134,0.00302608305
0.0482062853,0.0,9.0,7.27634188,7.49537264,1.00118167,0.0783650028,0.604855458,6.27574418,0.0153148445,0.00259504042
0.0492062853,0.0,9.0,7.27646955,7.50528489,0.944944972,0.0829779041,0.627210683,6.43465501,0.0153053016,0.00227793611
0.0492235036,0.0,9.0,7.2778251,7.49409728,0.764377287,0.131910166,0.676432754,6.25430793,0.0152040743,0.00263785017
0.0492579403,0.0,9.0,7.27780085,7.49424087,0.766326116,0.131035705,0.676138545,6.2567306,0.0152058834,0.00263300503
0.0492759045,0.0,9.0,7.27779637,7.49420283,0.765427247,0.130874116,0.676279694,6.25608799,0.0152062176,0.00263428691
0.0492932935,0.0,9.0,7.27778126,7.49431572,0.767076069,0.130329151,0.676027809,6.25799115,0.015207345,0.00263048057
0.0493280715,0.0,9.0,7.27776755,7.49431401,0.766519425,0.129834387,0.676119295,6.25796145,0.0152083685,0.00263053736
0.0493976275,0.0,9.0,7.27772318,7.49454867,0.769342133,0.128233951,0.675691756,6.26191392,0.0152116796,0.002622639
0.0495367396,0.0,9.0,7.27764976,7.49482333,0.771371532,0.125585411,0.675390687,6.26652786,0.0152171592,0.00261341089
0.0498149638,0.0,9.0,7.27747276,7.49587838,0.782109298,0.119199148,0.673708211,6.28414715,0.0152303694,0.00257815427
0.0503714122,0.0,9.0,7.27700163,7.5001577,0.824111449,0.102194224,0.666183266,6.35409185,0.0152655477,0.00243843823
0.0507639169,0.0,9.0,7.32124355,7.27579442,-5.47928381,1.65313059,1.98371101,0.0585773169,0.012061948,0.0153557811
0.0510133898,0.0,9.0,7.32845206,7.27580184,-5.47133237,1.89593831,1.93191184,0.0588453207,0.0115606724,0.0153552266
0.0512411485,0.0,9.0,7.33490246,7.27580928,-5.46405225,2.11025362,1.88800787,0.059114469,0.0111162744,0.0153546701
0.0514925042,0.0,9.0,7.34176242,7.2758169,-5.45604356,2.33564796,1.8398319,0.0593899045,0.0106513074,0.0153541
0.0519952157,0.0,9.0,7.35497408,7.27583415,-5.43996609,2.76095975,1.75172937,0.0600137478,0.00977456021,0.0153528094
0.0529952157,0.0,9.0,7.37910758,7.2758752,-5.40779306,3.50511581,1.59503383,0.0614975797,0.00824329555,0.0153497396
0.0539952157,0.0,9.0,7.40084938,7.27592263,-5.37545749,4.13416255,1.464434,0.0632125994,0.00695103813,0.0153461916
0.0549952157,0.0,9.0,7.42046922,7.27597753,-5.34292166,4.66347512,1.35292953,0.06519691,0.00586647299,0.0153420864
0.0559952157,0.0,9.0,7.43840501,7.27603769,-5.31026479,5.11176353,1.26040571,0.0673716179,0.0049507456,0.0153375874
0.0569952157,0.0,9.0,7.45479979,7.27610436,-5.27744247,5.48898517,1.18098312,0.0697814544,0.00418294796,0.0153326019
0.0579952157,0.0,9.0,7.47001586,7.27617503,-5.24454579,5.80929898,1.11549576,0.0723355682,0.00353374655,0.015327318
0.0589952157,0.0,9.0,7.4840913,7.27625116,-5.21152201,6.07882629,1.05885482,0.0750869214,0.00299017348,0.0153216261
0.0599952157,0.0,9.0,7.49734784,7.27632984,-5.17847683,6.30850844,1.01256844,0.0779299724,0.00252965469,0.0153157444
0.0609952157,0.0,9.0,7.50973287,7.2764129,-5.1453439,6.50174963,0.972105123,0.0809311722,0.00214481195,0.0153095356
0.0619952157,0.0,9.0,7.52155693,7.27649692,-5.1122472,6.66721815,0.939454294,0.0839666042,0.00181788307,0.015303256
0.0629952157,0.0,9.0,7.53268154,7.2765843,-5.0791,6.80639185,0.910476054,0.0871230058,0.00154540737,0.0152967262
0.0639952157,0.0,9.0,7.54343271,7.27667094,-5.04604999,6.92633519,0.887505871,0.0902526582,0.00131306686,0.0152902517
0.0649952157,0.0,9.0,7.55358308,7.27676005,-5.01298158,7.02715771,0.866677038,0.0934710403,0.00112012504,0.0152835937
0.0659952157,0.0,9.0,7.56350014,7.27684667,-4.98007377,7.11479455,0.850576544,0.0965990105,0.000954753358,0.0152771227
0.0669952157,0.0,9.0,7.57285837,7.27693508,-4.94717164,7.18838016,0.835525588,0.0997913184,0.000818083279,0.0152705186
0.0679952157,0.0,9.0,7.58209335,7.27701917,-4.91449545,7.25305739,0.824297059,0.102827449,0.000700114823,0.0152642377
0.0689952157,0.0,9.0,7.59076715,7.27710468,-4.88183793,7.30726229,0.81333805,0.105914423,0.000603228744,0.0152578516
0.0699952157,0.0,9.0,7.59941099,7.27718401,-4.84947282,7.35558546,0.80556225,0.108778152,0.00051880121,0.0152519274
0.0709952157,0.0,9.0,7.60745723,7.27726477,-4.81712507,7.39595908,0.797497177,0.11169337,0.000450011696,0.0152458966
0.0719952157,0.0,9.0,7.61556031,7.2773375,-4.78513612,7.43259296,0.792166644,0.114318229,0.000389306184,0.0152404665
0.0729952157,0.0,9.0,7.62300463,7.27741215,-4.75314605,7.46305222,0.786145083,0.117012274,0.000340332959,0.0152348934
0.0739952157,0.0,9.0,7.63021998,7.27747462,-4.7216635,7.49119744,0.782484459,0.119266315,0.0002985841,0.0152302311
0.0749952157,0.0,9.0,7.6370952,7.27754181,-4.69007745,7.51446581,0.777917521,0.121690962,0.000263193059,0.0152252154
0.0759952157,0.0,9.0,7.64415942,7.27759896,-4.65892103,7.53658525,0.775547218,0.123752723,0.000231023683,0.01522095
0.0769952157,0.0,9.0,7.65049101,7.27765902,-4.62772579,7.55467482,0.771999518,0.125919635,0.000205399927,0.0152164674
0.0779952157,0.0,9.0,7.65707219,7.27770735,-4.59702002,7.5723745,0.770495596,0.127662927,0.000181691463,0.0152128609
0.0789952157,0.0,9.0,7.66283528,7.27776035,-4.56621123,7.58665479,0.767661181,0.129574681,0.000163106865,0.0152089062
0.0799952157,0.0,9.0,7.66895068,7.27780016,-4.53594316,7.60109072,0.766773665,0.131010685,0.000145417631,0.0152059353
0.0809952157,0.0,9.0,7.67416628,7.27784674,-4.50549544,7.61253582,0.764443182,0.132690939,0.000131808239,0.0152024596
0.0819952157,0.0,9.0,7.67984312,7.2778787,-4.47563936,7.62453066,0.763997283,0.133843702,0.000118416323,0.0152000747
0.0829952157,0.0,9.0,7.68454202,7.27791973,-4.44552011,7.6338364,0.762024504,0.135323439,0.000108339086,0.0151970137
0.0839952157,0.0,9.0,7.68981285,7.2779447,-4.41604366,7.64397969,0.761897705,0.136223784,9.80402966e-05,0.015195151
0.0849952157,0.0,9.0,7.69403282,7.27798108,-4.3862185,7.65164751,0.760180
```

> Artifact truncated in this preview. The original file remains available through the manifest path.
