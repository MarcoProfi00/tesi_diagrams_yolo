# Agent input preview

This file is a local preview of the evidence that will be provided to the read-only diagnostic agent.
The agent remains read-only: it can inspect base outputs and existing scenario artifacts, but it does not modify files.

## User problem

Abbiamo verificato il comportamento statico a batteria scarica, nominale e molto carica. Ora vorrei osservare come reagiscono nel tempo i LED se la tensione della batteria varia lentamente da scarica a molto carica: quale scenario transitorio proponi?

## Circuit

- Batch: `batchDemo`
- Circuit: `b03`
- Agent mode: `graph_grounded_readonly`

## Technical summary

```json
{
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_message": "ngspice completed successfully.",
  "emitted_elements": 23,
  "skipped_elements": 0,
  "emit_warnings_count": 0,
  "skipped_components_count": 0,
  "node_count": 17,
  "ground_groups_count": 0,
  "singleton_nodes_count": 0,
  "bound_components": 22,
  "missing_components": 0,
  "unsupported_components": 0,
  "spice_ready_components": 22,
  "rules_missing_components": 0,
  "has_tran_csv": true,
  "has_tran_plot": true,
  "led_profiles": {
    "Dled12_1": {
      "state": "off",
      "regular_period": false,
      "frequency_hz": null,
      "duty_cycle": 0.0,
      "on_fraction": 0.0,
      "pulse_count": 0,
      "voltage_min": 0.5181018000000002,
      "voltage_max": 0.5181018000000002,
      "anode_node": "N002",
      "cathode_node": "N011"
    },
    "Dled12_2": {
      "state": "steady_on",
      "regular_period": false,
      "frequency_hz": null,
      "duty_cycle": 1.0,
      "on_fraction": 1.0,
      "pulse_count": 1,
      "voltage_min": 1.8857979,
      "voltage_max": 1.8857979,
      "anode_node": "N002",
      "cathode_node": "N004"
    },
    "Dled12_3": {
      "state": "off",
      "regular_period": false,
      "frequency_hz": null,
      "duty_cycle": 0.0,
      "on_fraction": 0.0,
      "pulse_count": 0,
      "voltage_min": 1.16485884,
      "voltage_max": 1.16485887,
      "anode_node": "N012",
      "cathode_node": "N001"
    }
  }
}
```

## Image policy

- Included by default: `False`
- Can be requested: `True`
- Path: `outputs\demo_workspaces\demo_batch\input\images\b03.jpg`
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
  "best_scenario_id": "scenario_2",
  "best_outcome_status": "partially_resolved",
  "best_stop_automation": false,
  "ranking_status": "verified_best",
  "interpretation_rule": "If a user asks which scenario resolves the problem, prefer the scenario with outcome_status='resolved_candidate' and stop_automation=true. Partially resolved scenarios without verified expectations are supporting diagnostics and must not be ranked only by changed_count.",
  "scenarios": [
    {
      "scenario_id": "scenario_1",
      "title": "Abbassare la tensione della batteria per simulare una batteria scarica",
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
        "expected_count": 4,
        "expectations_met_count": 4,
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
        "min_gain_ratio": null
      },
      "quantity_summary": {
        "changed": [
          "v(N002)",
          "v(N004)",
          "v(N011)",
          "v(N012)"
        ],
        "unchanged": [],
        "missing": []
      },
      "led_profiles": {
        "Dled12_1": {
          "state": "steady_on",
          "regular_period": false,
          "frequency_hz": null,
          "duty_cycle": 1.0,
          "on_fraction": 1.0,
          "pulse_count": 1,
          "voltage_min": 1.6208148199999997,
          "voltage_max": 1.6208148199999997,
          "anode_node": "N002",
          "cathode_node": "N011"
        },
        "Dled12_2": {
          "state": "off",
          "regular_period": false,
          "frequency_hz": null,
          "duty_cycle": 0.0,
          "on_fraction": 0.0,
          "pulse_count": 0,
          "voltage_min": 1.5347387500000007,
          "voltage_max": 1.5347387500000007,
          "anode_node": "N002",
          "cathode_node": "N004"
        },
        "Dled12_3": {
          "state": "off",
          "regular_period": false,
          "frequency_hz": null,
          "duty_cycle": 0.0,
          "on_fraction": 0.0,
          "pulse_count": 0,
          "voltage_min": 1.16482747,
          "voltage_max": 1.16482868,
          "anode_node": "N012",
          "cathode_node": "N001"
        }
      },
      "ranking_verified": true,
      "score": 40
    },
    {
      "scenario_id": "scenario_2",
      "title": "Alzare la tensione della batteria per simulare una batteria molto carica",
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
        "expected_count": 4,
        "expectations_met_count": 4,
        "expectations_failed_count": 0,
        "expectations_missing_count": 0,
        "meaningful_improvement_count": 1,
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
        "min_gain_ratio": null
      },
      "quantity_summary": {
        "changed": [
          "v(N012)",
          "v(N004)",
          "v(N011)",
          "@dled12_3[id]"
        ],
        "unchanged": [],
        "missing": []
      },
      "led_profiles": {
        "Dled12_1": {
          "state": "off",
          "regular_period": false,
          "frequency_hz": null,
          "duty_cycle": 0.0,
          "on_fraction": 0.0,
          "pulse_count": 0,
          "voltage_min": 0.5265480999999994,
          "voltage_max": 0.5265480999999994,
          "anode_node": "N002",
          "cathode_node": "N011"
        },
        "Dled12_2": {
          "state": "steady_on",
          "regular_period": false,
          "frequency_hz": null,
          "duty_cycle": 1.0,
          "on_fraction": 1.0,
          "pulse_count": 1,
          "voltage_min": 1.8787090000000006,
          "voltage_max": 1.8788961999999998,
          "anode_node": "N002",
          "cathode_node": "N004"
        },
        "Dled12_3": {
          "state": "steady_on",
          "regular_period": false,
          "frequency_hz": null,
          "duty_cycle": 1.0,
          "on_fraction": 1.0,
          "pulse_count": 1,
          "voltage_min": 2.01693405,
          "voltage_max": 2.01693538,
          "anode_node": "N012",
          "cathode_node": "N001"
        }
      },
      "ranking_verified": true,
      "score": 50
    },
    {
      "scenario_id": "scenario_3",
      "title": "Ridurre il bias della base di Q2 a 14 V",
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
        "expected_count": 4,
        "expectations_met_count": 4,
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
        "min_gain_ratio": null
      },
      "quantity_summary": {
        "changed": [
          "v(N015)",
          "v(N004)",
          "@dled12_2[id]",
          "@dled12_3[id]"
        ],
        "unchanged": [],
        "missing": []
      },
      "led_profiles": {
        "Dled12_1": {
          "state": "off",
          "regular_period": false,
          "frequency_hz": null,
          "duty_cycle": 0.0,
          "on_fraction": 0.0,
          "pulse_count": 0,
          "voltage_min": 0.5267522000000007,
          "voltage_max": 0.5268429000000001,
          "anode_node": "N002",
          "cathode_node": "N011"
        },
        "Dled12_2": {
          "state": "steady_on",
          "regular_period": false,
          "frequency_hz": null,
          "duty_cycle": 1.0,
          "on_fraction": 1.0,
          "pulse_count": 1,
          "voltage_min": 1.8771149000000005,
          "voltage_max": 1.8771149000000005,
          "anode_node": "N002",
          "cathode_node": "N004"
        },
        "Dled12_3": {
          "state": "steady_on",
          "regular_period": false,
          "frequency_hz": null,
          "duty_cycle": 1.0,
          "on_fraction": 1.0,
          "pulse_count": 1,
          "voltage_min": 2.01695809,
          "voltage_max": 2.01695809,
          "anode_node": "N012",
          "cathode_node": "N001"
        }
      },
      "ranking_verified": true,
      "score": 40
    },
    {
      "scenario_id": "scenario_4",
      "title": "Alzare ancora la batteria per vedere se il verde prevale davvero",
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
        "expected_count": 4,
        "expectations_met_count": 4,
        "expectations_failed_count": 0,
        "expectations_missing_count": 0,
        "meaningful_improvement_count": 1,
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
        "min_gain_ratio": null
      },
      "quantity_summary": {
        "changed": [
          "v(N012)",
          "v(N004)",
          "@dled12_2[id]",
          "@dled12_3[id]"
        ],
        "unchanged": [],
        "missing": []
      },
      "led_profiles": {
        "Dled12_1": {
          "state": "off",
          "regular_period": false,
          "frequency_hz": null,
          "duty_cycle": 0.0,
          "on_fraction": 0.0,
          "pulse_count": 0,
          "voltage_min": 0.5338402999999996,
          "voltage_max": 0.5338402999999996,
          "anode_node": "N002",
          "cathode_node": "N011"
        },
        "Dled12_2": {
          "state": "off",
          "regular_period": false,
          "frequency_hz": null,
          "duty_cycle": 0.0,
          "on_fraction": 0.0,
          "pulse_count": 0,
          "voltage_min": 0.8501128999999992,
          "voltage_max": 0.8501232999999999,
          "anode_node": "N002",
          "cathode_node": "N004"
        },
        "Dled12_3": {
          "state": "steady_on",
          "regular_period": false,
          "frequency_hz": null,
          "duty_cycle": 1.0,
          "on_fraction": 1.0,
          "pulse_count": 1,
          "voltage_min": 2.06077652,
          "voltage_max": 2.06077666,
          "anode_node": "N012",
          "cathode_node": "N001"
        }
      },
      "ranking_verified": true,
      "score": 50
    }
  ]
}
```


## Executed scenarios

### scenario_1

- Title: `Abbassare la tensione della batteria per simulare una batteria scarica`
- Status: `spice_success`
- SPICE status: `success`
- Outcome: `partially_resolved`
- Stop automation: `False`
- Comparison: `4/4` changed
- LED profiles: `{"Dled12_1": {"state": "steady_on", "regular_period": false, "frequency_hz": null, "duty_cycle": 1.0, "on_fraction": 1.0, "pulse_count": 1, "voltage_min": 1.6208148199999997, "voltage_max": 1.6208148199999997, "anode_node": "N002", "cathode_node": "N011"}, "Dled12_2": {"state": "off", "regular_period": false, "frequency_hz": null, "duty_cycle": 0.0, "on_fraction": 0.0, "pulse_count": 0, "voltage_min": 1.5347387500000007, "voltage_max": 1.5347387500000007, "anode_node": "N002", "cathode_node": "N004"}, "Dled12_3": {"state": "off", "regular_period": false, "frequency_hz": null, "duty_cycle": 0.0, "on_fraction": 0.0, "pulse_count": 0, "voltage_min": 1.16482747, "voltage_max": 1.16482868, "anode_node": "N012", "cathode_node": "N001"}}`

#### scenario_definition

- Role: Scenario selected by the user and saved before execution.
- Path: `outputs\demo_workspaces\demo_batch\web\chat\b03\scenarios\scenario_1\scenario.json`

```json
{
  "scenario_id": "scenario_1",
  "title": "Abbassare la tensione della batteria per simulare una batteria scarica",
  "hypothesis": "If the monitor distinguishes a discharged battery, lowering the existing source Vbattery2_1 from its nominal 12 V should change the LED-related branch conditions.",
  "intent": "diagnostic",
  "actions": [
    {
      "type": "change_source_value",
      "target": "Vbattery2_1",
      "value": "10V"
    }
  ],
  "rerun_from": "07",
  "analysis": "op",
  "compare": [
    "v(N002)",
    "v(N004)",
    "v(N011)",
    "v(N012)"
  ],
  "expect": {
    "v(N002)": "changed",
    "v(N004)": "changed",
    "v(N011)": "changed",
    "v(N012)": "changed"
  }
}
```

#### scenario_status

- Role: Current scenario status, SPICE status and diagnostic outcome.
- Path: `outputs\demo_workspaces\demo_batch\web\chat\b03\scenarios\scenario_1\scenario_status.json`

```json
{
  "status": "spice_success",
  "stage": "scenario_spice_executed",
  "scenario_id": "scenario_1",
  "source": "guided_chat",
  "spice_executed": true,
  "created_or_updated_at": "2026-07-21T16:57:39",
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_1\\run\\08_spice_run.json",
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_1\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 4,
    "changed_count": 4,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 4,
    "expectations_met_count": 4,
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
    "min_gain_ratio": null
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
  "controlled_scenario_report": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_1\\12_controlled_scenarios.json",
  "executed_scenarios_count": 1,
  "scenario_budget_exhausted": false,
  "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
}
```

#### controlled_scenario_report

- Role: Report produced by the controlled scenario runner.
- Path: `outputs\demo_workspaces\demo_batch\web\chat\b03\scenarios\scenario_1\12_controlled_scenarios.json`

```json
{
  "source_format": "pipeline2.0_controlled_scenario_report",
  "status": "spice_success",
  "scenario_id": "scenario_1",
  "scenario_title": "Abbassare la tensione della batteria per simulare una batteria scarica",
  "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_1",
  "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_1\\run",
  "netlist": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_1\\run\\07_netlist.cir",
  "applied_actions": [
    {
      "status": "applied",
      "type": "change_source_value",
      "target": "Vbattery2_1",
      "resolved_source_name": "Vbattery2_1",
      "tried_source_names": [
        "Vbattery2_1"
      ],
      "value": "10V",
      "normalized_source_definition": "DC 10",
      "old_line": "Vbattery2_1 N002 N001 DC 12",
      "new_line": "Vbattery2_1 N002 N001 DC 10",
      "operation": "updated",
      "spice_executed": false,
      "index": 1
    }
  ],
  "unsupported_actions": [],
  "failed_actions": [],
  "spice_executed": true,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_1\\run\\08_spice_run.json",
  "spice_status": "success",
  "spice_exit_code": 0,
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_1\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 4,
    "changed_count": 4,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 4,
    "expectations_met_count": 4,
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
    "min_gain_ratio": null
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
  "created_or_updated_at": "2026-07-21T16:57:39"
}
```

#### scenario_comparison

- Role: Base-vs-scenario comparison used to evaluate the scenario.
- Path: `outputs\demo_workspaces\demo_batch\web\chat\b03\scenarios\scenario_1\scenario_comparison.json`

```json
{
  "source_format": "pipeline2.0_scenario_comparison",
  "scenario_id": "scenario_1",
  "scenario_title": "Abbassare la tensione della batteria per simulare una batteria scarica",
  "scenario_intent": "diagnostic",
  "base_output_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03",
  "scenario_run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_1\\run",
  "base_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\08_ngspice_stdout.txt",
  "scenario_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_1\\run\\08_ngspice_stdout.txt",
  "base_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\08_ngspice_stderr.txt",
  "scenario_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_1\\run\\08_ngspice_stderr.txt",
  "quantities": [
    {
      "quantity": "v(N002)",
      "base_value": 12.0,
      "scenario_value": 10.0,
      "delta": -2.0,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 0.16666666666666666,
      "meaningful_improvement": false,
      "metric": "v(n002)",
      "measurement": "op",
      "base_details": {},
      "scenario_details": {}
    },
    {
      "quantity": "v(N004)",
      "base_value": 10.1142,
      "scenario_value": 8.465261,
      "delta": -1.6489390000000004,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 0.16303207371813888,
      "meaningful_improvement": false,
      "metric": "v(n004)",
      "measurement": "op",
      "base_details": {},
      "scenario_details": {}
    },
    {
      "quantity": "v(N011)",
      "base_value": 11.4819,
      "scenario_value": 8.379185,
      "delta": -3.102715,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 0.27022661754587657,
      "meaningful_improvement": false,
      "metric": "v(n011)",
      "measurement": "op",
      "base_details": {},
      "scenario_details": {}
    },
    {
      "quantity": "v(N012)",
      "base_value": 1.164859,
      "scenario_value": 1.164829,
      "delta": -3.0000000000196536e-05,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 2.5754189992262182e-05,
      "meaningful_improvement": false,
      "metric": "v(n012)",
      "measurement": "op",
      "base_details": {},
      "scenario_details": {}
    }
  ],
  "summary": {
    "requested_count": 4,
    "changed_count": 4,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 4,
    "expectations_met_count": 4,
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
    "min_gain_ratio": null
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
  "created_or_updated_at": "2026-07-21T16:57:39"
}
```

### scenario_2

- Title: `Alzare la tensione della batteria per simulare una batteria molto carica`
- Status: `spice_success`
- SPICE status: `success`
- Outcome: `partially_resolved`
- Stop automation: `False`
- Comparison: `4/4` changed
- LED profiles: `{"Dled12_1": {"state": "off", "regular_period": false, "frequency_hz": null, "duty_cycle": 0.0, "on_fraction": 0.0, "pulse_count": 0, "voltage_min": 0.5265480999999994, "voltage_max": 0.5265480999999994, "anode_node": "N002", "cathode_node": "N011"}, "Dled12_2": {"state": "steady_on", "regular_period": false, "frequency_hz": null, "duty_cycle": 1.0, "on_fraction": 1.0, "pulse_count": 1, "voltage_min": 1.8787090000000006, "voltage_max": 1.8788961999999998, "anode_node": "N002", "cathode_node": "N004"}, "Dled12_3": {"state": "steady_on", "regular_period": false, "frequency_hz": null, "duty_cycle": 1.0, "on_fraction": 1.0, "pulse_count": 1, "voltage_min": 2.01693405, "voltage_max": 2.01693538, "anode_node": "N012", "cathode_node": "N001"}}`

#### scenario_definition

- Role: Scenario selected by the user and saved before execution.
- Path: `outputs\demo_workspaces\demo_batch\web\chat\b03\scenarios\scenario_2\scenario.json`

```json
{
  "scenario_id": "scenario_2",
  "title": "Alzare la tensione della batteria per simulare una batteria molto carica",
  "hypothesis": "If the monitor distinguishes a very highly charged battery, increasing Vbattery2_1 above the nominal 12 V should change the green LED branch conditions and may activate Dled12_3.",
  "intent": "diagnostic",
  "actions": [
    {
      "type": "change_source_value",
      "target": "Vbattery2_1",
      "value": "14V"
    }
  ],
  "rerun_from": "07",
  "analysis": "op",
  "compare": [
    "v(N012)",
    "v(N004)",
    "v(N011)",
    "@dled12_3[id]"
  ],
  "expect": {
    "v(N012)": "changed",
    "v(N004)": "changed",
    "v(N011)": "changed",
    "@dled12_3[id]": "magnitude_increased"
  }
}
```

#### scenario_status

- Role: Current scenario status, SPICE status and diagnostic outcome.
- Path: `outputs\demo_workspaces\demo_batch\web\chat\b03\scenarios\scenario_2\scenario_status.json`

```json
{
  "status": "spice_success",
  "stage": "scenario_spice_executed",
  "scenario_id": "scenario_2",
  "source": "guided_chat",
  "spice_executed": true,
  "created_or_updated_at": "2026-07-21T16:58:52",
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_2\\run\\08_spice_run.json",
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_2\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 4,
    "changed_count": 4,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 4,
    "expectations_met_count": 4,
    "expectations_failed_count": 0,
    "expectations_missing_count": 0,
    "meaningful_improvement_count": 1,
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
    "min_gain_ratio": null
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
  "controlled_scenario_report": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_2\\12_controlled_scenarios.json",
  "executed_scenarios_count": 2,
  "scenario_budget_exhausted": false,
  "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
}
```

#### controlled_scenario_report

- Role: Report produced by the controlled scenario runner.
- Path: `outputs\demo_workspaces\demo_batch\web\chat\b03\scenarios\scenario_2\12_controlled_scenarios.json`

```json
{
  "source_format": "pipeline2.0_controlled_scenario_report",
  "status": "spice_success",
  "scenario_id": "scenario_2",
  "scenario_title": "Alzare la tensione della batteria per simulare una batteria molto carica",
  "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_2",
  "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_2\\run",
  "netlist": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_2\\run\\07_netlist.cir",
  "applied_actions": [
    {
      "status": "applied",
      "type": "change_source_value",
      "target": "Vbattery2_1",
      "resolved_source_name": "Vbattery2_1",
      "tried_source_names": [
        "Vbattery2_1"
      ],
      "value": "14V",
      "normalized_source_definition": "DC 14",
      "old_line": "Vbattery2_1 N002 N001 DC 12",
      "new_line": "Vbattery2_1 N002 N001 DC 14",
      "operation": "updated",
      "spice_executed": false,
      "index": 1
    }
  ],
  "unsupported_actions": [],
  "failed_actions": [],
  "spice_executed": true,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_2\\run\\08_spice_run.json",
  "spice_status": "success",
  "spice_exit_code": 0,
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_2\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 4,
    "changed_count": 4,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 4,
    "expectations_met_count": 4,
    "expectations_failed_count": 0,
    "expectations_missing_count": 0,
    "meaningful_improvement_count": 1,
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
    "min_gain_ratio": null
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
  "created_or_updated_at": "2026-07-21T16:58:52"
}
```

#### scenario_comparison

- Role: Base-vs-scenario comparison used to evaluate the scenario.
- Path: `outputs\demo_workspaces\demo_batch\web\chat\b03\scenarios\scenario_2\scenario_comparison.json`

```json
{
  "source_format": "pipeline2.0_scenario_comparison",
  "scenario_id": "scenario_2",
  "scenario_title": "Alzare la tensione della batteria per simulare una batteria molto carica",
  "scenario_intent": "diagnostic",
  "base_output_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03",
  "scenario_run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_2\\run",
  "base_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\08_ngspice_stdout.txt",
  "scenario_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_2\\run\\08_ngspice_stdout.txt",
  "base_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\08_ngspice_stderr.txt",
  "scenario_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_2\\run\\08_ngspice_stderr.txt",
  "quantities": [
    {
      "quantity": "v(N012)",
      "base_value": 1.164859,
      "scenario_value": 2.016934,
      "delta": 0.8520749999999999,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 0.7314833812504344,
      "meaningful_improvement": false,
      "metric": "v(n012)",
      "measurement": "op",
      "base_details": {},
      "scenario_details": {}
    },
    {
      "quantity": "v(N004)",
      "base_value": 10.1142,
      "scenario_value": 12.1211,
      "delta": 2.0069,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 0.1984239979434854,
      "meaningful_improvement": false,
      "metric": "v(n004)",
      "measurement": "op",
      "base_details": {},
      "scenario_details": {}
    },
    {
      "quantity": "v(N011)",
      "base_value": 11.4819,
      "scenario_value": 13.47345,
      "delta": 1.9915500000000002,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 0.17345125806704467,
      "meaningful_improvement": false,
      "metric": "v(n011)",
      "measurement": "op",
      "base_details": {},
      "scenario_details": {}
    },
    {
      "quantity": "@dled12_3[id]",
      "base_value": 6.01978179e-09,
      "scenario_value": 0.0107430289,
      "delta": 0.01074302288021821,
      "change": "changed",
      "expectation": "magnitude_increased",
      "expectation_met": true,
      "relative_change": 1784619.9837449938,
      "meaningful_improvement": true,
      "metric": "@dled12_3[id].final",
      "measurement": "op",
      "base_details": {
        "min": 6.01978142e-09,
        "max": 6.01978515e-09,
        "mean": 6.019781610545213e-09,
        "vpp": 3.729999999865528e-15,
        "final": 6.01978179e-09,
        "abs_peak": 6.01978515e-09
      },
      "scenario_details": {
        "min": 0.0107430286,
        "max": 0.0107431188,
        "mean": 0.010743028929787233,
        "vpp": 9.020000000040107e-08,
        "final": 0.0107430289,
        "abs_peak": 0.0107431188
      }
    }
  ],
  "summary": {
    "requested_count": 4,
    "changed_count": 4,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 4,
    "expectations_met_count": 4,
    "expectations_failed_count": 0,
    "expectations_missing_count": 0,
    "meaningful_improvement_count": 1,
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
    "min_gain_ratio": null
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
  "created_or_updated_at": "2026-07-21T16:58:52"
}
```

### scenario_3

- Title: `Ridurre il bias della base di Q2 a 14 V`
- Status: `spice_success`
- SPICE status: `success`
- Outcome: `partially_resolved`
- Stop automation: `False`
- Comparison: `4/4` changed
- LED profiles: `{"Dled12_1": {"state": "off", "regular_period": false, "frequency_hz": null, "duty_cycle": 0.0, "on_fraction": 0.0, "pulse_count": 0, "voltage_min": 0.5267522000000007, "voltage_max": 0.5268429000000001, "anode_node": "N002", "cathode_node": "N011"}, "Dled12_2": {"state": "steady_on", "regular_period": false, "frequency_hz": null, "duty_cycle": 1.0, "on_fraction": 1.0, "pulse_count": 1, "voltage_min": 1.8771149000000005, "voltage_max": 1.8771149000000005, "anode_node": "N002", "cathode_node": "N004"}, "Dled12_3": {"state": "steady_on", "regular_period": false, "frequency_hz": null, "duty_cycle": 1.0, "on_fraction": 1.0, "pulse_count": 1, "voltage_min": 2.01695809, "voltage_max": 2.01695809, "anode_node": "N012", "cathode_node": "N001"}}`

#### scenario_definition

- Role: Scenario selected by the user and saved before execution.
- Path: `outputs\demo_workspaces\demo_batch\web\chat\b03\scenarios\scenario_3\scenario.json`

```json
{
  "scenario_id": "scenario_3",
  "title": "Ridurre il bias della base di Q2 a 14 V",
  "hypothesis": "At 14 V, Qnpn_transistor18_2 may remain active because its base path through Rresistor22_4 still provides enough drive; increasing Rresistor22_4 should weaken Q2 and reduce the yellow LED branch current.",
  "intent": "diagnostic",
  "actions": [
    {
      "type": "change_source_value",
      "target": "Vbattery2_1",
      "value": "14V"
    },
    {
      "type": "change_component_value",
      "target": "Rresistor22_4",
      "value": "33k"
    }
  ],
  "rerun_from": "07",
  "analysis": "op",
  "compare": [
    "v(N015)",
    "v(N004)",
    "@dled12_2[id]",
    "@dled12_3[id]"
  ],
  "expect": {
    "v(N015)": "changed",
    "v(N004)": "changed",
    "@dled12_2[id]": "magnitude_decreased",
    "@dled12_3[id]": "nonzero"
  }
}
```

#### scenario_status

- Role: Current scenario status, SPICE status and diagnostic outcome.
- Path: `outputs\demo_workspaces\demo_batch\web\chat\b03\scenarios\scenario_3\scenario_status.json`

```json
{
  "status": "spice_success",
  "stage": "scenario_spice_executed",
  "scenario_id": "scenario_3",
  "source": "guided_chat",
  "spice_executed": true,
  "created_or_updated_at": "2026-07-21T17:00:28",
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_3\\run\\08_spice_run.json",
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_3\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 4,
    "changed_count": 4,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 4,
    "expectations_met_count": 4,
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
    "min_gain_ratio": null
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
  "controlled_scenario_report": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_3\\12_controlled_scenarios.json",
  "executed_scenarios_count": 3,
  "scenario_budget_exhausted": false,
  "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
}
```

#### controlled_scenario_report

- Role: Report produced by the controlled scenario runner.
- Path: `outputs\demo_workspaces\demo_batch\web\chat\b03\scenarios\scenario_3\12_controlled_scenarios.json`

```json
{
  "source_format": "pipeline2.0_controlled_scenario_report",
  "status": "spice_success",
  "scenario_id": "scenario_3",
  "scenario_title": "Ridurre il bias della base di Q2 a 14 V",
  "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_3",
  "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_3\\run",
  "netlist": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_3\\run\\07_netlist.cir",
  "applied_actions": [
    {
      "status": "applied",
      "type": "change_source_value",
      "target": "Vbattery2_1",
      "resolved_source_name": "Vbattery2_1",
      "tried_source_names": [
        "Vbattery2_1"
      ],
      "value": "14V",
      "normalized_source_definition": "DC 14",
      "old_line": "Vbattery2_1 N002 N001 DC 12",
      "new_line": "Vbattery2_1 N002 N001 DC 14",
      "operation": "updated",
      "spice_executed": false,
      "index": 1
    },
    {
      "status": "applied",
      "type": "change_component_value",
      "target": "Rresistor22_4",
      "resolved_component_name": "Rresistor22_4",
      "tried_component_names": [
        "Rresistor22_4"
      ],
      "value": "33k",
      "normalized_component_value": "33k",
      "old_value": "3.3k",
      "new_value": "33k",
      "old_line": "Rresistor22_4 N015 N005 3.3k",
      "new_line": "Rresistor22_4 N015 N005 33k",
      "operation": "updated",
      "spice_executed": false,
      "index": 2
    }
  ],
  "unsupported_actions": [],
  "failed_actions": [],
  "spice_executed": true,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_3\\run\\08_spice_run.json",
  "spice_status": "success",
  "spice_exit_code": 0,
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_3\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 4,
    "changed_count": 4,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 4,
    "expectations_met_count": 4,
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
    "min_gain_ratio": null
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
  "created_or_updated_at": "2026-07-21T17:00:28"
}
```

#### scenario_comparison

- Role: Base-vs-scenario comparison used to evaluate the scenario.
- Path: `outputs\demo_workspaces\demo_batch\web\chat\b03\scenarios\scenario_3\scenario_comparison.json`

```json
{
  "source_format": "pipeline2.0_scenario_comparison",
  "scenario_id": "scenario_3",
  "scenario_title": "Ridurre il bias della base di Q2 a 14 V",
  "scenario_intent": "diagnostic",
  "base_output_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03",
  "scenario_run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_3\\run",
  "base_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\08_ngspice_stdout.txt",
  "scenario_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_3\\run\\08_ngspice_stdout.txt",
  "base_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\08_ngspice_stderr.txt",
  "scenario_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_3\\run\\08_ngspice_stderr.txt",
  "quantities": [
    {
      "quantity": "v(N015)",
      "base_value": 0.8365391,
      "scenario_value": 0.8416777,
      "delta": 0.005138599999999993,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 0.006142689564659911,
      "meaningful_improvement": false,
      "metric": "v(n015)",
      "measurement": "op",
      "base_details": {},
      "scenario_details": {}
    },
    {
      "quantity": "v(N004)",
      "base_value": 10.1142,
      "scenario_value": 12.12289,
      "delta": 2.0086899999999996,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 0.1986009768444365,
      "meaningful_improvement": false,
      "metric": "v(n004)",
      "measurement": "op",
      "base_details": {},
      "scenario_details": {}
    },
    {
      "quantity": "@dled12_2[id]",
      "base_value": 0.00994158165,
      "scenario_value": 0.00937618082,
      "delta": -0.0005654008299999999,
      "change": "changed",
      "expectation": "magnitude_decreased",
      "expectation_met": true,
      "relative_change": 0.05687232171955253,
      "meaningful_improvement": false,
      "metric": "@dled12_2[id].final",
      "measurement": "op",
      "base_details": {
        "min": 0.00994158165,
        "max": 0.00994158165,
        "mean": 0.00994158165,
        "vpp": 0.0,
        "final": 0.00994158165,
        "abs_peak": 0.00994158165
      },
      "scenario_details": {
        "min": 0.00937618082,
        "max": 0.00937618082,
        "mean": 0.00937618082,
        "vpp": 0.0,
        "final": 0.00937618082,
        "abs_peak": 0.00937618082
      }
    },
    {
      "quantity": "@dled12_3[id]",
      "base_value": 6.01978179e-09,
      "scenario_value": 0.0107445617,
      "delta": 0.010744555680218211,
      "change": "changed",
      "expectation": "nonzero",
      "expectation_met": true,
      "relative_change": 1784874.6109147938,
      "meaningful_improvement": false,
      "metric": "@dled12_3[id].final",
      "measurement": "op",
      "base_details": {
        "min": 6.01978142e-09,
        "max": 6.01978515e-09,
        "mean": 6.019781610545213e-09,
        "vpp": 3.729999999865528e-15,
        "final": 6.01978179e-09,
        "abs_peak": 6.01978515e-09
      },
      "scenario_details": {
        "min": 0.0107445617,
        "max": 0.0107445617,
        "mean": 0.0107445617,
        "vpp": 0.0,
        "final": 0.0107445617,
        "abs_peak": 0.0107445617
      }
    }
  ],
  "summary": {
    "requested_count": 4,
    "changed_count": 4,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 4,
    "expectations_met_count": 4,
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
    "min_gain_ratio": null
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
  "created_or_updated_at": "2026-07-21T17:00:28"
}
```

### scenario_4

- Title: `Alzare ancora la batteria per vedere se il verde prevale davvero`
- Status: `spice_success`
- SPICE status: `success`
- Outcome: `partially_resolved`
- Stop automation: `False`
- Comparison: `4/4` changed
- LED profiles: `{"Dled12_1": {"state": "off", "regular_period": false, "frequency_hz": null, "duty_cycle": 0.0, "on_fraction": 0.0, "pulse_count": 0, "voltage_min": 0.5338402999999996, "voltage_max": 0.5338402999999996, "anode_node": "N002", "cathode_node": "N011"}, "Dled12_2": {"state": "off", "regular_period": false, "frequency_hz": null, "duty_cycle": 0.0, "on_fraction": 0.0, "pulse_count": 0, "voltage_min": 0.8501128999999992, "voltage_max": 0.8501232999999999, "anode_node": "N002", "cathode_node": "N004"}, "Dled12_3": {"state": "steady_on", "regular_period": false, "frequency_hz": null, "duty_cycle": 1.0, "on_fraction": 1.0, "pulse_count": 1, "voltage_min": 2.06077652, "voltage_max": 2.06077666, "anode_node": "N012", "cathode_node": "N001"}}`

#### scenario_definition

- Role: Scenario selected by the user and saved before execution.
- Path: `outputs\demo_workspaces\demo_batch\web\chat\b03\scenarios\scenario_4\scenario.json`

```json
{
  "scenario_id": "scenario_4",
  "title": "Alzare ancora la batteria per vedere se il verde prevale davvero",
  "hypothesis": "Since scenario_2 at 14V already activated Dled12_3 while Dled12_2 stayed on, increasing Vbattery2_1 further to 16V can verify whether the circuit is still in a mixed yellow+green region or whether the green branch becomes dominant.",
  "intent": "diagnostic",
  "actions": [
    {
      "type": "change_source_value",
      "target": "Vbattery2_1",
      "value": "16V"
    }
  ],
  "rerun_from": "07",
  "analysis": "op",
  "compare": [
    "v(N012)",
    "v(N004)",
    "@dled12_2[id]",
    "@dled12_3[id]"
  ],
  "expect": {
    "v(N012)": "changed",
    "v(N004)": "changed",
    "@dled12_2[id]": "changed",
    "@dled12_3[id]": "magnitude_increased"
  }
}
```

#### scenario_status

- Role: Current scenario status, SPICE status and diagnostic outcome.
- Path: `outputs\demo_workspaces\demo_batch\web\chat\b03\scenarios\scenario_4\scenario_status.json`

```json
{
  "status": "spice_success",
  "stage": "scenario_spice_executed",
  "scenario_id": "scenario_4",
  "source": "guided_chat",
  "spice_executed": true,
  "created_or_updated_at": "2026-07-21T17:01:55",
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_4\\run\\08_spice_run.json",
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_4\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 4,
    "changed_count": 4,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 4,
    "expectations_met_count": 4,
    "expectations_failed_count": 0,
    "expectations_missing_count": 0,
    "meaningful_improvement_count": 1,
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
    "min_gain_ratio": null
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
  "controlled_scenario_report": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_4\\12_controlled_scenarios.json",
  "executed_scenarios_count": 4,
  "scenario_budget_exhausted": false,
  "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
}
```

#### controlled_scenario_report

- Role: Report produced by the controlled scenario runner.
- Path: `outputs\demo_workspaces\demo_batch\web\chat\b03\scenarios\scenario_4\12_controlled_scenarios.json`

```json
{
  "source_format": "pipeline2.0_controlled_scenario_report",
  "status": "spice_success",
  "scenario_id": "scenario_4",
  "scenario_title": "Alzare ancora la batteria per vedere se il verde prevale davvero",
  "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_4",
  "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_4\\run",
  "netlist": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_4\\run\\07_netlist.cir",
  "applied_actions": [
    {
      "status": "applied",
      "type": "change_source_value",
      "target": "Vbattery2_1",
      "resolved_source_name": "Vbattery2_1",
      "tried_source_names": [
        "Vbattery2_1"
      ],
      "value": "16V",
      "normalized_source_definition": "DC 16",
      "old_line": "Vbattery2_1 N002 N001 DC 12",
      "new_line": "Vbattery2_1 N002 N001 DC 16",
      "operation": "updated",
      "spice_executed": false,
      "index": 1
    }
  ],
  "unsupported_actions": [],
  "failed_actions": [],
  "spice_executed": true,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_4\\run\\08_spice_run.json",
  "spice_status": "success",
  "spice_exit_code": 0,
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_4\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 4,
    "changed_count": 4,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 4,
    "expectations_met_count": 4,
    "expectations_failed_count": 0,
    "expectations_missing_count": 0,
    "meaningful_improvement_count": 1,
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
    "min_gain_ratio": null
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
  "created_or_updated_at": "2026-07-21T17:01:55"
}
```

#### scenario_comparison

- Role: Base-vs-scenario comparison used to evaluate the scenario.
- Path: `outputs\demo_workspaces\demo_batch\web\chat\b03\scenarios\scenario_4\scenario_comparison.json`

```json
{
  "source_format": "pipeline2.0_scenario_comparison",
  "scenario_id": "scenario_4",
  "scenario_title": "Alzare ancora la batteria per vedere se il verde prevale davvero",
  "scenario_intent": "diagnostic",
  "base_output_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03",
  "scenario_run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_4\\run",
  "base_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\08_ngspice_stdout.txt",
  "scenario_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_4\\run\\08_ngspice_stdout.txt",
  "base_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\08_ngspice_stderr.txt",
  "scenario_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\web\\chat\\b03\\scenarios\\scenario_4\\run\\08_ngspice_stderr.txt",
  "quantities": [
    {
      "quantity": "v(N012)",
      "base_value": 1.164859,
      "scenario_value": 2.060777,
      "delta": 0.8959179999999998,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 0.7691214129778795,
      "meaningful_improvement": false,
      "metric": "v(n012)",
      "measurement": "op",
      "base_details": {},
      "scenario_details": {}
    },
    {
      "quantity": "v(N004)",
      "base_value": 10.1142,
      "scenario_value": 15.14988,
      "delta": 5.035679999999999,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 0.49788218544224944,
      "meaningful_improvement": false,
      "metric": "v(n004)",
      "measurement": "op",
      "base_details": {},
      "scenario_details": {}
    },
    {
      "quantity": "@dled12_2[id]",
      "base_value": 0.00994158165,
      "scenario_value": 1.37959639e-10,
      "delta": -0.009941581512040361,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 0.9999999861229688,
      "meaningful_improvement": false,
      "metric": "@dled12_2[id].final",
      "measurement": "op",
      "base_details": {
        "min": 0.00994158165,
        "max": 0.00994158165,
        "mean": 0.00994158165,
        "vpp": 0.0,
        "final": 0.00994158165,
        "abs_peak": 0.00994158165
      },
      "scenario_details": {
        "min": 1.37959639e-10,
        "max": 1.37987309e-10,
        "mean": 1.3795964823304522e-10,
        "vpp": 2.7669999999985078e-14,
        "final": 1.37959639e-10,
        "abs_peak": 1.37987309e-10
      }
    },
    {
      "quantity": "@dled12_3[id]",
      "base_value": 6.01978179e-09,
      "scenario_value": 0.0138231218,
      "delta": 0.01382311578021821,
      "change": "changed",
      "expectation": "magnitude_increased",
      "expectation_met": true,
      "relative_change": 2296281.869083864,
      "meaningful_improvement": true,
      "metric": "@dled12_3[id].final",
      "measurement": "op",
      "base_details": {
        "min": 6.01978142e-09,
        "max": 6.01978515e-09,
        "mean": 6.019781610545213e-09,
        "vpp": 3.729999999865528e-15,
        "final": 6.01978179e-09,
        "abs_peak": 6.01978515e-09
      },
      "scenario_details": {
        "min": 0.0138231115,
        "max": 0.0138231218,
        "mean": 0.013823121796575797,
        "vpp": 1.0299999998741871e-08,
        "final": 0.0138231218,
        "abs_peak": 0.0138231218
      }
    }
  ],
  "summary": {
    "requested_count": 4,
    "changed_count": 4,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 4,
    "expectations_met_count": 4,
    "expectations_failed_count": 0,
    "expectations_missing_count": 0,
    "meaningful_improvement_count": 1,
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
    "min_gain_ratio": null
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
  "created_or_updated_at": "2026-07-21T17:01:55"
}
```


## Loaded artifacts

### graph

- Step: `01`
- Role: Graph JSON copied from Pipeline 1.0.
- Path: `outputs\demo_workspaces\demo_batch\web\chat\b03\01_graph.json`

```json
{
  "image_id": "b03",
  "image_name": "b03.jpg",
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
      "component_id": "resistor22.2",
      "instance_id": "22.2",
      "class_name": "Resistor",
      "terminals": [
        {
          "terminal_id": "resistor22.2_t1",
          "name": "t1",
          "relative_position": "left"
        },
        {
          "terminal_id": "resistor22.2_t2",
          "name": "t2",
          "relative_position": "right"
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
      "component_id": "npn_transistor18.2",
      "instance_id": "18.2",
      "class_name": "NPN_Transistor",
      "terminals": [
        {
          "terminal_id": "npn_transistor18.2_B",
          "name": "B",
          "relative_position": "right"
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
      "component_id": "diode7.1",
      "instance_id": "7.1",
      "class_name": "Diode",
      "terminals": [
        {
          "terminal_id": "diode7.1_cathode",
          "name": "cathode",
          "relative_position": "left"
        },
        {
          "terminal_id": "diode7.1_anode",
          "name": "anode",
          "relative_position": "right"
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
          "relative_position": "left"
        },
        {
          "terminal_id": "resistor22.4_t2",
          "name": "t2",
          "relative_position": "right"
        }
      ]
    },
    {
      "component_id": "diode7.2",
      "instance_id": "7.2",
      "class_name": "Diode",
      "terminals": [
        {
          "terminal_id": "diode7.2_cathode",
          "name": "cathode",
          "relative_position": "top"
        },
        {
          "terminal_id": "diode7.2_anode",
          "name": "anode",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "resistor22.5",
      "instance_id": "22.5",
      "class_name": "Resistor",
      "terminals": [
        {
          "terminal_id": "resistor22.5_t1",
          "name": "t1",
          "relative_position": "top"
        },
        {
          "terminal_id": "resistor22.5_t2",
          "name": "t2",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "diode7.3",
      "instance_id": "7.3",
      "class_name": "Diode",
      "terminals": [
        {
          "terminal_id": "diode7.3_anode",
          "name": "anode",
          "relative_position": "top"
        },
        {
          "terminal_id": "diode7.3_cathode",
          "name": "cathode",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "diode7.4",
      "instance_id": "7.4",
      "class_name": "Diode",
      "terminals": [
        {
          "terminal_id": "diode7.4_anode",
          "name": "anode",
          "relative_position": "top"
        },
        {
          "terminal_id": "diode7.4_cathode",
          "name": "cathode",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "resistor22.6",
      "instance_id": "22.6",
      "class_name": "Resistor",
      "terminals": [
        {
          "terminal_id": "resistor22.6_t1",
          "name": "t1",
          "relative_position": "top"
        },
        {
          "terminal_id": "resistor22.6_t2",
          "name": "t2",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "led12.3",
      "instance_id": "12.3",
      "class_name": "LED",
      "terminals": [
        {
          "terminal_id": "led12.3_anode",
          "name": "anode",
          "relative_position": "top"
        },
        {
          "terminal_id": "led12.3_cathode",
          "name": "cathode",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "npn_transistor18.3",
      "instance_id": "18.3",
      "class_name": "NPN_Transistor",
      "terminals": [
        {
          "terminal_id": "npn_transistor18.3_B",
          "name": "B",
          "relative_position": "right"
        },
        {
          "terminal_id": "npn_transistor18.3_E",
          "name": "E",
          "relative_position": "top"
        },
        {
          "terminal_id": "npn_transistor18.3_C",
          "name": "C",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "resistor22.7",
      "instance_id": "22.7",
      "class_name": "Resistor",
      "terminals": [
        {
          "terminal_id": "resistor22.7_t1",
          "name": "t1",
          "relative_position": "left"
        },
        {
          "terminal_id": "resistor22.7_t2",
          "name": "t2",
          "relative_position": "right"
        }
      ]
    },
    {
      "component_id": "resistor22.8",
      "instance_id": "22.8",
      "class_name": "Resistor",
      "terminals": [
        {
          "terminal_id": "resistor22.8_t1",
          "name": "t1",
          "relative_position": "top"
        },
        {
          "terminal_id": "resistor22.8_t2",
          "name": "t2",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "diode7.5",
      "instance_id": "7.5",
      "class_name": "Diode",
      "terminals": [
        {
          "terminal_id": "diode7.5_cathode",
          "name": "cathode",
          "relative_position": "top"
        },
        {
          "terminal_id": "diode7.5_anode",
          "name": "anode",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "diode7.6",
      "instance_id": "7.6",
      "class_name": "Diode",
      "terminals": [
        {
          "terminal_id": "diode7.6_anode",
          "name": "anode",
          "relative_position": "top"
        },
        {
          "terminal_id": "diode7.6_cathode",
          "name": "cathode",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "diode7.7",
      "instance_id": "7.7",
      "class_name": "Diode",
      "terminals": [
        {
          "terminal_id": "diode7.7_anode",
          "name": "anode",
          "relative_position": "top"
        },
        {
          "terminal_id": "diode7.7_cathode",
          "name": "cathode",
          "relative_position": "bottom"
        }
      ]
    }
  ],
  "terminal_metadata": {},
  "graph": {
    "battery2.1_negative": [
      "diode7.5_anode",
      "led12.3_cathode",
      "npn_transistor18.1_E",
      "npn_transistor18.2_E",
      "resistor22.5_t2"
    ],
    "battery2.1_positive": [
      "diode7.3_anode",
      "led12.1_anode",
      "led12.2_anode",
      "npn_transistor18.3_E",
      "resistor22.8_t1"
    ],
    "diode7.1_anode": [
      "npn_transistor18.3_C",
      "resistor22.6_t1"
    ],
    "diode7.1_cathode": [
      "led12.2_cathode",
      "resistor22.3_t1"
    ],
    "diode7.2_anode": [
      "resistor22.4_t2",
      "resistor22.5_t1"
    ],
    "diode7.2_cathode": [
      "diode7.4_cathode"
    ],
    "diode7.3_anode": [
      "battery2.1_positive",
      "led12.1_anode",
      "led12.2_anode",
      "npn_transistor18.3_E",
      "resistor22.8_t1"
    ],
    "diode7.3_cathode": [
      "diode7.4_anode"
    ],
    "diode7.4_anode": [
      "diode7.3_cathode"
    ],
    "diode7.4_cathode": [
      "diode7.2_cathode"
    ],
    "diode7.5_anode": [
      "battery2.1_negative",
      "led12.3_cathode",
      "npn_transistor18.1_E",
      "npn_transistor18.2_E",
      "resistor22.5_t2"
    ],
    "diode7.5_cathode": [
      "diode7.7_cathode"
    ],
    "diode7.6_anode": [
      "resistor22.7_t2",
      "resistor22.8_t2"
    ],
    "diode7.6_cathode": [
      "diode7.7_anode"
    ],
    "diode7.7_anode": [
      "diode7.6_cathode"
    ],
    "diode7.7_cathode": [
      "diode7.5_cathode"
    ],
    "led12.1_anode": [
      "battery2.1_positive",
      "diode7.3_anode",
      "led12.2_anode",
      "npn_transistor18.3_E",
      "resistor22.8_t1"
    ],
    "led12.1_cathode": [
      "resistor22.1_t1"
    ],
    "led12.2_anode": [
      "battery2.1_positive",
      "diode7.3_anode",
      "led12.1_anode",
      "npn_transistor18.3_E",
      "resistor22.8_t1"
    ],
    "led12.2_cathode": [
      "diode7.1_cathode",
      "resistor22.3_t1"
    ],
    "led12.3_anode": [
      "resistor22.6_t2"
    ],
    "led12.3_cathode": [
      "battery2.1_negative",
      "diode7.5_anode",
      "npn_transistor18.1_E",
      "npn_transistor18.2_E",
      "resistor22.5_t2"
    ],
    "npn_transistor18.1_B": [
      "resistor22.2_t1"
    ],
    "npn_transistor18.1_C": [
      "resistor22.1_t2"
    ],
    "npn_transistor18.1_E": [
      "battery2.1_negative",
      "diode7.5_anode",
      "led12.3_cathode",
      "npn_transistor18.2_E",
      "resistor22.5_t2"
    ],
    "npn_transistor18.2_B": [
      "resistor22.4_t1"
    ],
    "npn_transistor18.2_C": [
      "resistor22.2_t2",
      "resistor22.3_t2"
    ],
    "npn_transistor18.2_E": [
      "battery2.1_negative",
      "diode7.5_anode",
      "led12.3_cathode",
      "npn_transistor18.1_E",
      "resistor22.5_t2"
    ],
    "npn_
```

> Artifact truncated in this preview. The original file remains available through the manifest path.

### node_map

- Step: `03`
- Role: Maps component terminals to SPICE node names.
- Path: `outputs\demo_workspaces\demo_batch\web\chat\b03\03_node_map.json`

```json
{
  "circuit_id": "b03",
  "source_format": "pipeline2.0_node_map",
  "nodes": [
    {
      "node_id": "N001",
      "kind": "normal",
      "terminals": [
        "battery2.1_negative",
        "diode7.5_anode",
        "led12.3_cathode",
        "npn_transistor18.1_E",
        "npn_transistor18.2_E",
        "resistor22.5_t2"
      ],
      "terminal_count": 6
    },
    {
      "node_id": "N002",
      "kind": "normal",
      "terminals": [
        "battery2.1_positive",
        "diode7.3_anode",
        "led12.1_anode",
        "led12.2_anode",
        "npn_transistor18.3_E",
        "resistor22.8_t1"
      ],
      "terminal_count": 6
    },
    {
      "node_id": "N003",
      "kind": "normal",
      "terminals": [
        "diode7.1_anode",
        "npn_transistor18.3_C",
        "resistor22.6_t1"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N004",
      "kind": "normal",
      "terminals": [
        "diode7.1_cathode",
        "led12.2_cathode",
        "resistor22.3_t1"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N005",
      "kind": "normal",
      "terminals": [
        "diode7.2_anode",
        "resistor22.4_t2",
        "resistor22.5_t1"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N006",
      "kind": "normal",
      "terminals": [
        "diode7.2_cathode",
        "diode7.4_cathode"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N007",
      "kind": "normal",
      "terminals": [
        "diode7.3_cathode",
        "diode7.4_anode"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N008",
      "kind": "normal",
      "terminals": [
        "diode7.5_cathode",
        "diode7.7_cathode"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N009",
      "kind": "normal",
      "terminals": [
        "diode7.6_anode",
        "resistor22.7_t2",
        "resistor22.8_t2"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N010",
      "kind": "normal",
      "terminals": [
        "diode7.6_cathode",
        "diode7.7_anode"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N011",
      "kind": "normal",
      "terminals": [
        "led12.1_cathode",
        "resistor22.1_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N012",
      "kind": "normal",
      "terminals": [
        "led12.3_anode",
        "resistor22.6_t2"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N013",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.1_B",
        "resistor22.2_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N014",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.1_C",
        "resistor22.1_t2"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N015",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.2_B",
        "resistor22.4_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N016",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.2_C",
        "resistor22.2_t2",
        "resistor22.3_t2"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N017",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.3_B",
        "resistor22.7_t1"
      ],
      "terminal_count": 2
    }
  ],
  "terminal_to_node": {
    "battery2.1_negative": "N001",
    "battery2.1_positive": "N002",
    "diode7.1_anode": "N003",
    "diode7.1_cathode": "N004",
    "diode7.2_anode": "N005",
    "diode7.2_cathode": "N006",
    "diode7.3_anode": "N002",
    "diode7.3_cathode": "N007",
    "diode7.4_anode": "N007",
    "diode7.4_cathode": "N006",
    "diode7.5_anode": "N001",
    "diode7.5_cathode": "N008",
    "diode7.6_anode": "N009",
    "diode7.6_cathode": "N010",
    "diode7.7_anode": "N010",
    "diode7.7_cathode": "N008",
    "led12.1_anode": "N002",
    "led12.1_cathode": "N011",
    "led12.2_anode": "N002",
    "led12.2_cathode": "N004",
    "led12.3_anode": "N012",
    "led12.3_cathode": "N001",
    "npn_transistor18.1_B": "N013",
    "npn_transistor18.1_C": "N014",
    "npn_transistor18.1_E": "N001",
    "npn_transistor18.2_B": "N015",
    "npn_transistor18.2_C": "N016",
    "npn_transistor18.2_E": "N001",
    "npn_transistor18.3_B": "N017",
    "npn_transistor18.3_C": "N003",
    "npn_transistor18.3_E": "N002",
    "resistor22.1_t1": "N011",
    "resistor22.1_t2": "N014",
    "resistor22.2_t1": "N013",
    "resistor22.2_t2": "N016",
    "resistor22.3_t1": "N004",
    "resistor22.3_t2": "N016",
    "resistor22.4_t1": "N015",
    "resistor22.4_t2": "N005",
    "resistor22.5_t1": "N005",
    "resistor22.5_t2": "N001",
    "resistor22.6_t1": "N003",
    "resistor22.6_t2": "N012",
    "resistor22.7_t1": "N017",
    "resistor22.7_t2": "N009",
    "resistor22.8_t1": "N002",
    "resistor22.8_t2": "N009"
  },
  "component_terminal_nodes": {
    "battery2.1": {
      "positive": "N002",
      "negative": "N001"
    },
    "diode7.1": {
      "cathode": "N004",
      "anode": "N003"
    },
    "diode7.2": {
      "cathode": "N006",
      "anode": "N005"
    },
    "diode7.3": {
      "anode": "N002",
      "cathode": "N007"
    },
    "diode7.4": {
      "anode": "N007",
      "cathode": "N006"
    },
    "diode7.5": {
      "cathode": "N008",
      "anode": "N001"
    },
    "diode7.6": {
      "anode": "N009",
      "cathode": "N010"
    },
    "diode7.7": {
      "anode": "N010",
      "cathode": "N008"
    },
    "led12.1": {
      "anode": "N002",
      "cathode": "N011"
    },
    "led12.2": {
      "anode": "N002",
      "cathode": "N004"
    },
    "led12.3": {
      "anode": "N012",
      "cathode": "N001"
    },
    "npn_transistor18.1": {
      "B": "N013",
      "C": "N014",
      "E": "N001"
    },
    "npn_transistor18.2": {
      "B": "N015",
      "C": "N016",
      "E": "N001"
    },
    "npn_transistor18.3": {
      "B": "N017",
      "E": "N002",
      "C": "N003"
    },
    "resistor22.1": {
      "t1": "N011",
      "t2": "N014"
    },
    "resistor22.2": {
      "t1": "N013",
      "t2": "N016"
    },
    "resistor22.3": {
      "t1": "N004",
      "t2": "N016"
    },
    "resistor22.4": {
      "t1": "N015",
      "t2": "N005"
    },
    "resistor22.5": {
      "t1": "N005",
      "t2": "N001"
    },
    "resistor22.6": {
      "t1": "N003",
      "t2": "N012"
    },
    "resistor22.7": {
      "t1": "N017",
      "t2": "N009"
    },
    "resistor22.8": {
      "t1": "N002",
      "t2": "N009"
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
    "nodes_count": 17,
    "normal_nodes_count": 17,
    "ground_nodes_count": 0,
    "ground_groups_count": 0,
    "terminal_to_node_count": 47,
    "singleton_nodes_count": 0
  }
}
```

### values_bound

- Step: `04`
- Role: Values and labels bound to graph components.
- Path: `outputs\demo_workspaces\demo_batch\web\chat\b03\04_values_bound.json`

```json
{
  "circuit_id": "b03",
  "source_format": "pipeline2.0_values_bound",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\data\\batchDemo\\values\\b03_values.yaml",
  "supplies": {
    "VREF_B": {
      "terminal": "battery2.1_negative",
      "type": "dc",
      "value": 0,
      "unit": "V",
      "reference": 0,
      "source": "manual_reference_for_floating_battery_circuit",
      "label_text": "B: riferimento SPICE 0 V",
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
        "value": 12,
        "unit": "V",
        "source": "manual_from_original_circuit_context",
        "label_text": "batteria automobilistica nominale 12 V tra A e B"
      },
      "status": "bound"
    },
    "diode7.1": {
      "class_name": "Diode",
      "terminal_nodes": {
        "cathode": "N004",
        "anode": "N003"
      },
      "value_data": {
        "model": "D_1N4148_TYP",
        "source": "manual_from_image_label",
        "label_text": "D3 1N4148"
      },
      "status": "bound"
    },
    "diode7.2": {
      "class_name": "Diode",
      "terminal_nodes": {
        "cathode": "N006",
        "anode": "N005"
      },
      "value_data": {
        "model": "BZX79C10_TYP",
        "source": "manual_from_image_label",
        "label_text": "D6 BZX79C10 zener 10 V",
        "viewer_override": {
          "visual_class": "zener",
          "label": "D6",
          "display_value": "BZX79C10 10 V"
        }
      },
      "status": "bound"
    },
    "diode7.3": {
      "class_name": "Diode",
      "terminal_nodes": {
        "anode": "N002",
        "cathode": "N007"
      },
      "value_data": {
        "model": "D_1N4148_TYP",
        "source": "manual_from_image_label",
        "label_text": "D4 1N4148"
      },
      "status": "bound"
    },
    "diode7.4": {
      "class_name": "Diode",
      "terminal_nodes": {
        "anode": "N007",
        "cathode": "N006"
      },
      "value_data": {
        "model": "D_1N4148_TYP",
        "source": "manual_from_image_label",
        "label_text": "D5 1N4148"
      },
      "status": "bound"
    },
    "diode7.5": {
      "class_name": "Diode",
      "terminal_nodes": {
        "cathode": "N008",
        "anode": "N001"
      },
      "value_data": {
        "model": "BZX79C12_TYP",
        "source": "manual_from_image_label",
        "label_text": "D10 BZX79C12 zener 12 V",
        "viewer_override": {
          "visual_class": "zener",
          "label": "D10",
          "display_value": "BZX79C12 12 V"
        }
      },
      "status": "bound"
    },
    "diode7.6": {
      "class_name": "Diode",
      "terminal_nodes": {
        "anode": "N009",
        "cathode": "N010"
      },
      "value_data": {
        "model": "D_1N4148_TYP",
        "source": "manual_from_image_label",
        "label_text": "D8 1N4148"
      },
      "status": "bound"
    },
    "diode7.7": {
      "class_name": "Diode",
      "terminal_nodes": {
        "anode": "N010",
        "cathode": "N008"
      },
      "value_data": {
        "model": "D_1N4148_TYP",
        "source": "manual_from_image_label",
        "label_text": "D9 1N4148"
      },
      "status": "bound"
    },
    "led12.1": {
      "class_name": "LED",
      "terminal_nodes": {
        "anode": "N002",
        "cathode": "N011"
      },
      "value_data": {
        "model": "LED_RED_TYP",
        "source": "manual_from_image_color",
        "label_text": "D1 LED rosso"
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
        "model": "LED_YELLOW_TYP",
        "source": "manual_from_image_color",
        "label_text": "D2 LED giallo"
      },
      "status": "bound"
    },
    "led12.3": {
      "class_name": "LED",
      "terminal_nodes": {
        "anode": "N012",
        "cathode": "N001"
      },
      "value_data": {
        "model": "LED_GREEN_TYP",
        "source": "manual_from_image_color",
        "label_text": "D7 LED verde"
      },
      "status": "bound"
    },
    "npn_transistor18.1": {
      "class_name": "NPN_Transistor",
      "terminal_nodes": {
        "B": "N013",
        "C": "N014",
        "E": "N001"
      },
      "value_data": {
        "model": "BC547_TYP",
        "source": "manual_from_image_label",
        "label_text": "Q1 BC547 NPN"
      },
      "status": "bound"
    },
    "npn_transistor18.2": {
      "class_name": "NPN_Transistor",
      "terminal_nodes": {
        "B": "N015",
        "C": "N016",
        "E": "N001"
      },
      "value_data": {
        "model": "BC547_TYP",
        "source": "manual_from_image_label",
        "label_text": "Q2 BC547 NPN"
      },
      "status": "bound"
    },
    "npn_transistor18.3": {
      "class_name": "NPN_Transistor",
      "terminal_nodes": {
        "B": "N017",
        "E": "N002",
        "C": "N003"
      },
      "value_data": {
        "model": "BC557_TYP",
        "source": "manual_from_image_label_semantic_correction",
        "label_text": "Q3 BC557 PNP"
      },
      "status": "bound"
    },
    "resistor22.1": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N011",
        "t2": "N014"
      },
      "value_data": {
        "value": 1,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R1 1 kohm"
      },
      "status": "bound"
    },
    "resistor22.2": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N013",
        "t2": "N016"
      },
      "value_data": {
        "value": 100,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R2 100 kohm"
      },
      "status": "bound"
    },
    "resistor22.3": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N004",
        "t2": "N016"
      },
      "value_data": {
        "value": 1,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R3 1 kohm"
      },
      "status": "bound"
    },
    "resistor22.4": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N015",
        "t2": "N005"
      },
      "value_data": {
        "value": 3.3,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R4 3.3 kohm"
      },
      "status": "bound"
    },
    "resistor22.5": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N005",
        "t2": "N001"
      },
      "value_data": {
        "value": 3.3,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R5 3.3 kohm"
      },
      "status": "bound"
    },
    "resistor22.6": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N003",
        "t2": "N012"
      },
      "value_data": {
        "value": 1,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R6 1 kohm"
      },
      "status": "bound"
    },
    "resistor22.7": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N017",
        "t2": "N009"
      },
      "value_data": {
        "value": 3.3,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R7 3.3 kohm"
      },
      "status": "bound"
    },
    "resistor22.8": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N002",
        "t2": "N009"
      },
      "value_data": {
        "value": 3.3,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R8 3.3 kohm"
      },
      "status": "bound"
    }
  },
  "nodes": {
    "battery2.1_negative": {
      "label": "B",
      "source": "manual_from_image_label",
      "label_text": "B: negativo batteria e riferimento SPICE",
      "node": "N001"
    },
    "battery2.1_positive": {
      "label": "A",
      "source": "manual_from_image_label",
      "label_text": "A: positivo batteria",
      "node": "N002"
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
    "components_total": 22,
    "bound_components": 22,
    "missing_components": 0,
    "not_required_components": 0,
    "unsupported_components": 0,
    "supplies_count": 1,
    "manual_nodes_count": 2
  }
}
```

### component_rules

- Step: `06`
- Role: SPICE conversion rules for each component.
- Path: `outputs\demo_workspaces\demo_batch\web\chat\b03\06_component_rules.json`

```json
{
  "circuit_id": "b03",
  "source_format": "pipeline2.0_component_rules",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\data\\batchDemo\\values\\b03_values.yaml",
  "spice_classes_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_spice_classes.yaml",
  "supplies": {
    "VREF_B": {
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
        "label_text": "B: riferimento SPICE 0 V",
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
        "value": 12,
        "unit": "V",
        "source": "manual_from_original_circuit_context",
        "label_text": "batteria automobilistica nominale 12 V tra A e B"
      }
    },
    "diode7.1": {
      "class_name": "Diode",
      "status": "spice_ready",
      "spice_support": "model",
      "spice_prefix": "D",
      "emit_as": "diode",
      "node_order": [
        "anode",
        "cathode"
      ],
      "nodes": [
        "N003",
        "N004"
      ],
      "parameters": {
        "model": "D_1N4148_TYP",
        "source": "manual_from_image_label",
        "label_text": "D3 1N4148"
      }
    },
    "diode7.2": {
      "class_name": "Diode",
      "status": "spice_ready",
      "spice_support": "model",
      "spice_prefix": "D",
      "emit_as": "diode",
      "node_order": [
        "anode",
        "cathode"
      ],
      "nodes": [
        "N005",
        "N006"
      ],
      "parameters": {
        "model": "BZX79C10_TYP",
        "source": "manual_from_image_label",
        "label_text": "D6 BZX79C10 zener 10 V",
        "viewer_override": {
          "visual_class": "zener",
          "label": "D6",
          "display_value": "BZX79C10 10 V"
        }
      }
    },
    "diode7.3": {
      "class_name": "Diode",
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
        "N007"
      ],
      "parameters": {
        "model": "D_1N4148_TYP",
        "source": "manual_from_image_label",
        "label_text": "D4 1N4148"
      }
    },
    "diode7.4": {
      "class_name": "Diode",
      "status": "spice_ready",
      "spice_support": "model",
      "spice_prefix": "D",
      "emit_as": "diode",
      "node_order": [
        "anode",
        "cathode"
      ],
      "nodes": [
        "N007",
        "N006"
      ],
      "parameters": {
        "model": "D_1N4148_TYP",
        "source": "manual_from_image_label",
        "label_text": "D5 1N4148"
      }
    },
    "diode7.5": {
      "class_name": "Diode",
      "status": "spice_ready",
      "spice_support": "model",
      "spice_prefix": "D",
      "emit_as": "diode",
      "node_order": [
        "anode",
        "cathode"
      ],
      "nodes": [
        "N001",
        "N008"
      ],
      "parameters": {
        "model": "BZX79C12_TYP",
        "source": "manual_from_image_label",
        "label_text": "D10 BZX79C12 zener 12 V",
        "viewer_override": {
          "visual_class": "zener",
          "label": "D10",
          "display_value": "BZX79C12 12 V"
        }
      }
    },
    "diode7.6": {
      "class_name": "Diode",
      "status": "spice_ready",
      "spice_support": "model",
      "spice_prefix": "D",
      "emit_as": "diode",
      "node_order": [
        "anode",
        "cathode"
      ],
      "nodes": [
        "N009",
        "N010"
      ],
      "parameters": {
        "model": "D_1N4148_TYP",
        "source": "manual_from_image_label",
        "label_text": "D8 1N4148"
      }
    },
    "diode7.7": {
      "class_name": "Diode",
      "status": "spice_ready",
      "spice_support": "model",
      "spice_prefix": "D",
      "emit_as": "diode",
      "node_order": [
        "anode",
        "cathode"
      ],
      "nodes": [
        "N010",
        "N008"
      ],
      "parameters": {
        "model": "D_1N4148_TYP",
        "source": "manual_from_image_label",
        "label_text": "D9 1N4148"
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
        "N011"
      ],
      "parameters": {
        "model": "LED_RED_TYP",
        "source": "manual_from_image_color",
        "label_text": "D1 LED rosso"
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
        "model": "LED_YELLOW_TYP",
        "source": "manual_from_image_color",
        "label_text": "D2 LED giallo"
      }
    },
    "led12.3": {
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
        "N012",
        "N001"
      ],
      "parameters": {
        "model": "LED_GREEN_TYP",
        "source": "manual_from_image_color",
        "label_text": "D7 LED verde"
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
        "N014",
        "N013",
        "N001"
      ],
      "parameters": {
        "model": "BC547_TYP",
        "source": "manual_from_image_label",
        "label_text": "Q1 BC547 NPN"
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
        "N016",
        "N015",
        "N001"
      ],
      "parameters": {
        "model": "BC547_TYP",
        "source": "manual_from_image_label",
        "label_text": "Q2 BC547 NPN"
      }
    },
    "npn_transistor18.3": {
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
        "N003",
        "N017",
        "N002"
      ],
      "parameters": {
        "model": "BC557_TYP",
        "source": "manual_from_image_label_semantic_correction",
        "label_text": "Q3 BC557 PNP"
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
        "N011",
        "N014"
      ],
      "parameters": {
        "value": 1,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R1 1 kohm"
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
        "N013",
        "N016"
      ],
      "parameters": {
        "value": 100,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R2 100 kohm"
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
        "N004",
        "N016"
      ],
      "parameters": {
        "value": 1,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R3 1 kohm"
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
        "N015",
        "N005"
      ],
      "parameters": {
        "value": 3.3,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R4 3.3 kohm"
      }
    },
    "resistor22.5": {
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
        "N005",
        "N001"
      ],
      "parameters": {
        "value": 3.3,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R5 3.3 kohm"
      }
    },
    "resistor22.6": {
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
        "N012"
      ],
      "parameters": {
        "value": 1,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R6 1 kohm"
      }
    },
    "resistor22.7": {
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
        "N017",
        "N009"
      ],
      "parameters": {
        "value": 3.3,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R7 3.3 kohm"
      }
    },
    "resistor22.8": {
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
        "N009"
      ],
      "parameters": {
        "value": 3.3,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R8 3.3 kohm"
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
    "components_total": 22,
    "spice_ready_components": 22,
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
- Path: `outputs\demo_workspaces\demo_batch\web\chat\b03\07_netlist.cir`

```spice
* pipeline2.0 netlist
* circuit: b03

VVREF_B N001 0 DC 0
Vbattery2_1 N002 N001 DC 12
Ddiode7_1 N003 N004 D_1N4148_TYP
Ddiode7_2 N005 N006 BZX79C10_TYP
Ddiode7_3 N002 N007 D_1N4148_TYP
Ddiode7_4 N007 N006 D_1N4148_TYP
Ddiode7_5 N001 N008 BZX79C12_TYP
Ddiode7_6 N009 N010 D_1N4148_TYP
Ddiode7_7 N010 N008 D_1N4148_TYP
Dled12_1 N002 N011 LED_RED_TYP
Dled12_2 N002 N004 LED_YELLOW_TYP
Dled12_3 N012 N001 LED_GREEN_TYP
Qnpn_transistor18_1 N014 N013 N001 BC547_TYP
Qnpn_transistor18_2 N016 N015 N001 BC547_TYP
Qnpn_transistor18_3 N003 N017 N002 BC557_TYP
Rresistor22_1 N011 N014 1k
Rresistor22_2 N013 N016 100k
Rresistor22_3 N004 N016 1k
Rresistor22_4 N015 N005 3.3k
Rresistor22_5 N005 N001 3.3k
Rresistor22_6 N003 N012 1k
Rresistor22_7 N017 N009 3.3k
Rresistor22_8 N002 N009 3.3k

.model BC547_TYP NPN(BF=250 VAF=50 IKF=100m)
.model BC557_TYP PNP(BF=250 VAF=50 IKF=100m)
.model BZX79C10_TYP D(BV=10 IBV=5m NBV=1.7)
.model BZX79C12_TYP D(BV=12 IBV=5m NBV=1.9)
.model D_1N4148_TYP D(IS=6n N=1.9 RS=0.65 BV=100 IBV=100u TT=4n CJO=4p)
.model LED_GREEN_TYP D(IS=1e-18 N=2 RS=10)
.model LED_RED_TYP D(IS=1e-15 N=2 RS=10)
.model LED_YELLOW_TYP D(IS=1e-17 N=2 RS=10)

.op
.save all
.tran 1ms 3s

.control
set wr_singlescale
set wr_vecnames
save all @ddiode7_1[id] @ddiode7_2[id] @ddiode7_3[id] @ddiode7_4[id] @ddiode7_5[id] @ddiode7_6[id] @ddiode7_7[id] @dled12_1[id] @dled12_2[id] @dled12_3[id]
run
wrdata 08_tran.csv time v(N001) v(N002) v(N003) v(N004) v(N005) v(N006) v(N007) v(N008) v(N009) v(N010) v(N011) v(N012) v(N013) v(N014) v(N015) v(N016) v(N017) @ddiode7_1[id] @ddiode7_2[id] @ddiode7_3[id] @ddiode7_4[id] @ddiode7_5[id] @ddiode7_6[id] @ddiode7_7[id] @dled12_1[id] @dled12_2[id] @dled12_3[id]
.endc
.end

```

### spice_emit_report

- Step: `07`
- Role: Report of emitted, skipped and warning components.
- Path: `outputs\demo_workspaces\demo_batch\web\chat\b03\07_spice_emit_report.json`

```json
{
  "circuit_id": "b03",
  "source_format": "pipeline2.0_spice_emit_report",
  "emitted_elements": 23,
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
      "N008",
      "N009",
      "N010",
      "N011",
      "N012",
      "N013",
      "N014",
      "N015",
      "N016",
      "N017"
    ],
    "device_currents": [
      "@ddiode7_1[id]",
      "@ddiode7_2[id]",
      "@ddiode7_3[id]",
      "@ddiode7_4[id]",
      "@ddiode7_5[id]",
      "@ddiode7_6[id]",
      "@ddiode7_7[id]",
      "@dled12_1[id]",
      "@dled12_2[id]",
      "@dled12_3[id]"
    ]
  },
  "models": [
    "BC547_TYP",
    "BC557_TYP",
    "BZX79C10_TYP",
    "BZX79C12_TYP",
    "D_1N4148_TYP",
    "LED_GREEN_TYP",
    "LED_RED_TYP",
    "LED_YELLOW_TYP"
  ],
  "warnings": []
}
```

### spice_run

- Step: `08`
- Role: Structured ngspice execution report.
- Path: `outputs\demo_workspaces\demo_batch\web\chat\b03\08_spice_run.json`

```json
{
  "source_format": "pipeline2.0_spice_run",
  "status": "success",
  "netlist_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\pipeline2.0\\b03\\07_netlist.cir",
  "command": [
    "C:\\Users\\m.profilo\\Spice64\\bin\\ngspice_con.exe",
    "-b",
    "07_netlist.cir"
  ],
  "exit_code": 0,
  "stdout_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\pipeline2.0\\b03\\08_ngspice_stdout.txt",
  "stderr_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\pipeline2.0\\b03\\08_ngspice_stderr.txt",
  "tran_raw_csv_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\pipeline2.0\\b03\\08_tran_raw.csv",
  "tran_csv_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\pipeline2.0\\b03\\08_tran.csv",
  "tran_plot_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\pipeline2.0\\b03\\08_tran_plot.png",
  "tran_plot_png_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\demo_batch\\pipeline2.0\\b03\\08_tran_plot.png",
  "tran_plot_svg_path": null,
  "message": "ngspice completed successfully."
}
```

### ngspice_stdout

- Step: `08`
- Role: Raw ngspice stdout log.
- Path: `outputs\demo_workspaces\demo_batch\web\chat\b03\08_ngspice_stdout.txt`

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
n002                                        12
n003                                   1.16486
n004                                   10.1142
n005                                   1.02973
n006                                   10.9153
n007                                   11.4577
n008                                   11.5524
n009                                   11.9982
n010                                   11.7753
n011                                   11.4819
n012                                   1.16486
n014                                   11.4819
n013                                  0.172628
n016                                  0.172626
n015                                  0.836539
n017                                   11.9982
vbattery2_1#branch                  -0.0103127
vvref_b#branch                    -2.36532e-11


No. of Data Rows : 3008
Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

No. of Data Rows : 1

Initial Transient Solution
--------------------------

Node                                   Voltage
----                                   -------
n001                                         0
n002                                        12
n003                                   1.16486
n004                                   10.1142
n005                                   1.02973
n006                                   10.9153
n007                                   11.4577
n008                                   11.5524
n009                                   11.9982
n010                                   11.7753
n011                                   11.4819
n012                                   1.16486
n014                                   11.4819
n013                                  0.172628
n016                                  0.172626
n015                                  0.836539
n017                                   11.9982
vbattery2_1#branch                  -0.0103127
vvref_b#branch                    -2.36532e-11


No. of Data Rows : 3008
	Node                                  Voltage
	----                                  -------
	----	-------
	n017                             1.199817e+01
	n015                             8.365391e-01
	n016                             1.726265e-01
	n013                             1.726276e-01
	n014                             1.148190e+01
	n012                             1.164859e+00
	n011                             1.148190e+01
	n010                             1.177528e+01
	n009                             1.199817e+01
	n008                             1.155238e+01
	n007                             1.145765e+01
	n006                             1.091531e+01
	n005                             1.029726e+00
	n004                             1.011420e+01
	n003                             1.164865e+00
	n002                             1.200000e+01
	n001                             0.000000e+00

	Source	Current
	------	-------

	@dled12_3[id]                    6.019785e-09
	@dled12_2[id]                    9.941582e-03
	@dled12_1[id]                    2.288834e-11
	@ddiode7_7[id]                   5.536755e-07
	@ddiode7_6[id]                   5.536755e-07
	@ddiode7_5[id]                   -5.53676e-07
	@ddiode7_4[id]                   3.705798e-04
	@ddiode7_3[id]                   3.705798e-04
	@ddiode7_2[id]                   -3.70580e-04
	@ddiode7_1[id]                   -6.00895e-09
	vvref_b#branch                   -2.36532e-11
	vbattery2_1#branch               -1.03127e-02

 BJT models (Bipolar Junction Transistor)
      model             bc557_typ             bc547_typ

       type                   pnp                   npn
       tnom                    27                    27
         is                 1e-16                 1e-16
        ibe                     0                     0
        ibc                     0                     0
         bf                   250                   250
         nf                     1                     1
        vaf                    50                    50
        ikf                   0.1                   0.1
        ise                     0                     0
         ne                   1.5                   1.5
         br                     1                     1
         nr                     1                     1
        var                     0                     0
        ikr                     0                     0
        isc                     0                     0
         nc                     2                     2
         rb                     0                     0
        irb                     0                     0
        rbm                     0                     0
         re                     0                     0
         rc                     0                     0
        cje                     0                     0
        vje                  0.75                  0.75
        mje                  0.33                  0.33
         tf                     0                     0
        xtf                     0                     0
        vtf                     0                     0
        itf                     0                     0
        ptf                     0                     0
        cjc                     0                     0
        vjc                  0.75                  0.75
        mjc                  0.33                  0.33
       xcjc                     1                     1
         tr                     0                     0
        cjs                     0                     0
        vjs                  0.75                  0.75
        mjs                     0                     0
        xtb                     0                     0
         eg                  1.11                  1.11
        xti                     3                     3
         fc                   0.5                   0.5
         kf                     0                     0
         af                     0                     0
        iss                     0                     0
         ns                     1                     1
        rco                  0.01                  0.01
         vo                    10                    10
      gamma                 1e-11                 1e-11
        qco                     0                     0
       tlev                     0                     0
      tlevc                     0                     0
       tbf1                     0                     0
       tbf2                     0                     0
       tbr1                     0                     0
       tbr2                     0                     0
      tikf1                     0                     0
      tikf2                     0                     0
      tikr1                     0                     0
      tikr2                     0                     0
      tirb1                     0                     0
      tirb2                     0                     0
       tnc1                     0                     0
       tnc2                     0                     0
       tne1                     0                     0
       tne2                     0                     0
       tnf1                     0                     0
       tnf2                     0                     0
       tnr1                     0                     0
       tnr2                     0                     0
       trb1                     0                     0
       trb2                     0                     0
       trc1                     0                     0
       trc2                     0                     0
       tre1                     0                     0
       tre2                     0                     0
       trm1                     0                     0
       trm2                     0                     0
      tvaf1                     0                     0
      tvaf2                     0                     0
      tvar1                     0                     0
      tvar2                     0                     0
        ctc                     0                     0
        cte                     0                     0
        cts                     0                     0
       tvjc                     0                     0
       tvje                     0                     0
       tvjs                     0                     0
      titf1                     0                     0
      titf2                     0                     0
       ttf1                     0                     0
       ttf2                     0                     0
       ttr1                     0                     0
       ttr2                     0                     0
      tmje1                     0                     0
      tmje2                     0                     0
      tmjc1                     0                     0
      tmjc2                     0                     0
      tmjs1                     0                     0
      tmjs2                     0                     0
       tns1                     0                     0
       tns2                     0                     0
        nkf                   0.5                   0.5
       tis1                     0                     0
       tis2                     0                     0
      tise1                     0                     0
      tise2                     0                     0
      tisc1                     0                     0
      tisc2                     0                     0
      tiss1                     0                     0
      tiss2                     0                     0
   quasimod                     0                     0
         vg                 1.206                 1.206
         cn                   2.2                  2.42
          d                  0.52                  0.87
    vbe_max                 1e+99                 1e+99
    vbc_max                 1e+99                 1e+99
    vce_max                 1e+99                 1e+99
     pd_max                 1e+99                 1e+99
     ic_max                 1e+99                 1e+99
     ib_max                 1e+99                 1e+99
     te_max                 1e+99                 1e+99
       rth0                     0                     0

 Diode models (Junction Diode model)
      model         led_green_typ        led_yellow_typ           led_red_typ

      level                     1                     1                     1
         is                 1e-18                 1e-17                 1e-15
        jsw                     0                     0                     0
         rs                    10                    10                    10
        rsw                     0                     0                     0
        trs                     0                     0                     0
       trs2                     0                     0                     0
          n                     2                     2                     2
         ns                     1                     1                     1
         tt                     0                     0                     0
       ttt1                     0                     0                     0
       ttt2                     0                     0                     0
```

> Artifact truncated in this preview. The original file remains available through the manifest path.

### ngspice_stderr

- Step: `08`
- Role: Raw ngspice stderr log.
- Path: `outputs\demo_workspaces\demo_batch\web\chat\b03\08_ngspice_stderr.txt`

```text

```

### tran_csv

- Step: `08`
- Role: Clean transient CSV, when .tran data is available.
- Path: `outputs\demo_workspaces\demo_batch\web\chat\b03\08_tran.csv`

```csv
time,v(N001),v(N002),v(N003),v(N004),v(N005),v(N006),v(N007),v(N008),v(N009),v(N010),v(N011),v(N012),v(N013),v(N014),v(N015),v(N016),v(N017),@ddiode7_1[id],@ddiode7_2[id],@ddiode7_3[id],@ddiode7_4[id],@ddiode7_5[id],@ddiode7_6[id],@ddiode7_7[id],@dled12_1[id],@dled12_2[id],@dled12_3[id]
0.0,0.0,12.0,1.16486489,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485887,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.008948e-09,-0.000370579814,0.000370579814,0.000370579814,-5.53675541e-07,5.53675542e-07,5.53675541e-07,2.28883446e-11,0.00994158165,6.01978515e-09
1e-05,0.0,12.0,1.16486488,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485886,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.00894979e-09,-0.000370579814,0.000370579814,0.000370579814,-5.53675541e-07,5.53675541e-07,5.53675541e-07,2.28883453e-11,0.00994158165,6.01978351e-09
2e-05,0.0,12.0,1.16486487,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485885,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.00894895e-09,-0.000370579814,0.000370579814,0.000370579814,-5.53675542e-07,5.53675541e-07,5.53675542e-07,2.28883441e-11,0.00994158165,6.01978265e-09
4e-05,0.0,12.0,1.16486486,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485884,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.00894814e-09,-0.000370579814,0.000370579814,0.000370579814,-5.5367554e-07,5.53675543e-07,5.5367554e-07,2.28883453e-11,0.00994158165,6.01978166e-09
8e-05,0.0,12.0,1.16486486,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485884,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.00894796e-09,-0.000370579814,0.000370579814,0.000370579814,-5.53675542e-07,5.53675541e-07,5.53675542e-07,2.28883452e-11,0.00994158165,6.01978148e-09
0.00016,0.0,12.0,1.16486486,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485884,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.00894804e-09,-0.000370579814,0.000370579814,0.000370579814,-5.53675542e-07,5.53675541e-07,5.53675542e-07,2.28883462e-11,0.00994158165,6.01978149e-09
0.00032,0.0,12.0,1.16486486,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485884,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.00894791e-09,-0.000370579814,0.000370579814,0.000370579814,-5.53675541e-07,5.53675543e-07,5.53675541e-07,2.28883463e-11,0.00994158165,6.01978186e-09
0.00064,0.0,12.0,1.16486486,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485884,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.00894809e-09,-0.000370579814,0.000370579814,0.000370579814,-5.53675542e-07,5.53675541e-07,5.53675542e-07,2.28883448e-11,0.00994158165,6.0197818e-09
0.00128,0.0,12.0,1.16486486,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485884,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.00894792e-09,-0.000370579814,0.000370579814,0.000370579814,-5.53675541e-07,5.53675543e-07,5.53675541e-07,2.28883453e-11,0.00994158165,6.01978162e-09
0.00228,0.0,12.0,1.16486486,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485884,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.00894808e-09,-0.000370579814,0.000370579814,0.000370579814,-5.53675541e-07,5.53675542e-07,5.53675541e-07,2.28883437e-11,0.00994158165,6.0197818e-09
0.00328,0.0,12.0,1.16486486,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485884,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.00894793e-09,-0.000370579814,0.000370579814,0.000370579814,-5.53675541e-07,5.53675541e-07,5.53675541e-07,2.28883462e-11,0.00994158165,6.01978158e-09
0.00428,0.0,12.0,1.16486486,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485884,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.00894808e-09,-0.000370579814,0.000370579814,0.000370579814,-5.53675541e-07,5.53675542e-07,5.53675541e-07,2.28883475e-11,0.00994158165,6.01978167e-09
0.00528,0.0,12.0,1.16486486,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485884,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.00894793e-09,-0.000370579814,0.000370579814,0.000370579814,-5.53675541e-07,5.53675543e-07,5.53675541e-07,2.28883455e-11,0.00994158165,6.01978164e-09
0.00628,0.0,12.0,1.16486486,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485884,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.00894808e-09,-0.000370579814,0.000370579814,0.000370579814,-5.53675542e-07,5.53675541e-07,5.53675542e-07,2.28883442e-11,0.00994158165,6.01978156e-09
0.00728,0.0,12.0,1.16486486,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485884,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.00894793e-09,-0.000370579814,0.000370579814,0.000370579814,-5.53675541e-07,5.53675542e-07,5.53675541e-07,2.28883459e-11,0.00994158165,6.01978142e-09
0.00828,0.0,12.0,1.16486486,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485884,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.00894807e-09,-0.000370579814,0.000370579814,0.000370579814,-5.53675542e-07,5.53675541e-07,5.53675542e-07,2.28883477e-11,0.00994158165,6.01978173e-09
0.00928,0.0,12.0,1.16486486,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485884,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.00894794e-09,-0.000370579814,0.000370579814,0.000370579814,-5.53675541e-07,5.53675543e-07,5.53675541e-07,2.28883454e-11,0.00994158165,6.01978165e-09
0.01028,0.0,12.0,1.16486486,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485884,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.00894807e-09,-0.000370579814,0.000370579814,0.000370579814,-5.53675541e-07,5.53675542e-07,5.53675541e-07,2.28883459e-11,0.00994158165,6.01978158e-09
0.01128,0.0,12.0,1.16486486,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485884,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.00894794e-09,-0.000370579814,0.000370579814,0.000370579814,-5.53675541e-07,5.53675543e-07,5.53675541e-07,2.2888346e-11,0.00994158165,6.01978154e-09
0.01228,0.0,12.0,1.16486486,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485884,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.00894807e-09,-0.000370579814,0.000370579814,0.000370579814,-5.53675542e-07,5.53675541e-07,5.53675542e-07,2.28883466e-11,0.00994158165,6.01978159e-09
0.01328,0.0,12.0,1.16486486,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485884,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.00894794e-09,-0.000370579814,0.000370579814,0.000370579814,-5.53675541e-07,5.53675541e-07,5.53675541e-07,2.28883456e-11,0.00994158165,6.01978152e-09
0.01428,0.0,12.0,1.16486486,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485884,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.00894806e-09,-0.000370579814,0.000370579814,0.000370579814,-5.53675541e-07,5.53675542e-07,5.53675541e-07,2.28883478e-11,0.00994158165,6.01978172e-09
0.01528,0.0,12.0,1.16486486,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485884,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.00894795e-09,-0.000370579814,0.000370579814,0.000370579814,-5.53675542e-07,5.5367554e-07,5.53675542e-07,2.28883456e-11,0.00994158165,6.01978158e-09
0.01628,0.0,12.0,1.16486486,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485884,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.00894806e-09,-0.000370579814,0.000370579814,0.000370579814,-5.53675542e-07,5.53675541e-07,5.53675542e-07,2.28883445e-11,0.00994158165,6.01978164e-09
0.01728,0.0,12.0,1.16486486,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485884,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.00894795e-09,-0.000370579814,0.000370579814,0.000370579814,-5.53675541e-07,5.53675542e-07,5.53675541e-07,2.28883471e-11,0.00994158165,6.01978159e-09
0.01828,0.0,12.0,1.16486486,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485884,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.00894805e-09,-0.000370579814,0.000370579814,0.000370579814,-5.5367554e-07,5.53675543e-07,5.5367554e-07,2.28883459e-11,0.00994158165,6.01978161e-09
0.01928,0.0,12.0,1.16486486,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485884,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.00894795e-09,-0.000370579814,0.000370579814,0.000370579814,-5.5367554e-07,5.53675543e-07,5.5367554e-07,2.28883469e-11,0.00994158165,6.01978152e-09
0.02028,0.0,12.0,1.16486486,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485884,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.00894805e-09,-0.000370579814,0.000370579814,0.000370579814,-5.53675542e-07,5.53675541e-07,5.53675542e-07,2.28883471e-11,0.00994158165,6.01978161e-09
0.02128,0.0,12.0,1.16486486,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485884,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.00894796e-09,-0.000370579814,0.000370579814,0.000370579814,-5.53675541e-07,5.53675542e-07,5.53675541e-07,2.28883472e-11,0.00994158165,6.01978154e-09
0.02228,0.0,12.0,1.16486486,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485884,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.00894804e-09,-0.000370579814,0.000370579814,0.000370579814,-5.53675541e-07,5.53675542e-07,5.53675541e-07,2.28883433e-11,0.00994158165,6.01978177e-09
0.02328,0.0,12.0,1.16486486,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485884,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.00894796e-09,-0.000370579814,0.000370579814,0.000370579814,-5.53675542e-07,5.53675541e-07,5.53675542e-07,2.28883448e-11,0.00994158165,6.0197817e-09
0.02428,0.0,12.0,1.16486486,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485884,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.00894804e-09,-0.000370579814,0.000370579814,0.000370579814,-5.5367554e-07,5.53675543e-07,5.5367554e-07,2.28883476e-11,0.00994158165,6.01978166e-09
0.02528,0.0,12.0,1.16486486,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485884,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.00894796e-09,-0.000370579814,0.000370579814,0.000370579814,-5.53675542e-07,5.53675541e-07,5.53675542e-07,2.28883465e-11,0.00994158165,6.01978153e-09
0.02628,0.0,12.0,1.16486486,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485884,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.00894804e-09,-0.000370579814,0.000370579814,0.000370579814,-5.53675541e-07,5.53675542e-07,5.53675541e-07,2.28883451e-11,0.00994158165,6.01978153e-09
0.02728,0.0,12.0,1.16486486,10.1142021,1.02972622,10.9153099,11.4576549,11.5523832,11.9981728,11.775278,11.4818982,1.16485884,0.172627569,11.4818982,0.836539063,0.172626456,11.9981727,-6.00894797e-09,-0.000370579814,0.000370579814,0.000370579814,-5.53675541e-07,5.53675541e-07,5.53675541e-07,2.28883458e-11,0.009941
```

> Artifact truncated in this preview. The original file remains available through the manifest path.
