# Agent input preview

This file is a local preview of the evidence that will be provided to the read-only diagnostic agent.
The agent remains read-only: it can inspect base outputs and existing scenario artifacts, but it does not modify files.

## User problem

Concludi esperimento

## Circuit

- Batch: `batchChatAgentEvaluation`
- Circuit: `c03`
- Agent mode: `graph_grounded_readonly`

## Technical summary

```json
{
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_message": "ngspice completed successfully.",
  "emitted_elements": 15,
  "skipped_elements": 8,
  "emit_warnings_count": 0,
  "skipped_components_count": 8,
  "node_count": 10,
  "ground_groups_count": 5,
  "singleton_nodes_count": 0,
  "bound_components": 12,
  "missing_components": 0,
  "unsupported_components": 1,
  "spice_ready_components": 13,
  "rules_missing_components": 0,
  "has_tran_csv": true,
  "has_tran_plot": true,
  "led_profiles": {}
}
```

## Image policy

- Included by default: `False`
- Can be requested: `True`
- Path: `outputs\demo_workspaces\chat_agent_evaluation\input\images\c03.jpg`
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
  "best_scenario_id": "scenario_1",
  "best_outcome_status": "partially_resolved",
  "best_stop_automation": false,
  "ranking_status": "verified_best",
  "interpretation_rule": "If a user asks which scenario resolves the problem, prefer the scenario with outcome_status='resolved_candidate' and stop_automation=true. Partially resolved scenarios without verified expectations are supporting diagnostics and must not be ranked only by changed_count.",
  "scenarios": [
    {
      "scenario_id": "scenario_1",
      "title": "Aumentare controllatamente il livello di VAUDIO_IN",
      "status": "spice_success",
      "spice_status": "success",
      "outcome_status": "partially_resolved",
      "outcome_label": "Ipotesi diagnostica confermata",
      "outcome_technical_label": "Diagnostic hypothesis confirmed",
      "outcome_reason": "I criteri dichiarati dal test diagnostico sono soddisfatti, ma lo scenario non applica una correzione del sintomo utente.",
      "stop_automation": false,
      "comparison_summary": {
        "requested_count": 3,
        "changed_count": 3,
        "activated_count": 0,
        "missing_count": 0,
        "expected_count": 2,
        "expectations_met_count": 2,
        "expectations_failed_count": 0,
        "expectations_missing_count": 0,
        "meaningful_improvement_count": 2,
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
          "v(N005)",
          "v(N008)",
          "v(N004)"
        ],
        "unchanged": [],
        "missing": []
      },
      "led_profiles": {},
      "ranking_verified": true,
      "score": 50
    }
  ]
}
```


## Executed scenarios

### scenario_1

- Title: `Aumentare controllatamente il livello di VAUDIO_IN`
- Status: `spice_success`
- SPICE status: `success`
- Outcome: `partially_resolved`
- Stop automation: `False`
- Comparison: `3/3` changed
- LED profiles: `{}`

#### scenario_definition

- Role: Scenario selected by the user and saved before execution.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\c03\scenarios\scenario_1\scenario.json`

```json
{
  "scenario_id": "scenario_1",
  "title": "Aumentare controllatamente il livello di VAUDIO_IN",
  "hypothesis": "The simulated low output may be caused mainly by the very small existing input source amplitude.",
  "intent": "diagnostic",
  "actions": [
    {
      "type": "change_source_value",
      "target": "VAUDIO_IN",
      "value": "SIN(0 0.05 1000)"
    }
  ],
  "rerun_from": "07",
  "analysis": "tran",
  "compare": [
    "v(N005)",
    "v(N008)",
    "v(N004)"
  ],
  "expect": {
    "v(N008)": "magnitude_increased",
    "v(N004)": "magnitude_increased"
  }
}
```

#### scenario_status

- Role: Current scenario status, SPICE status and diagnostic outcome.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\c03\scenarios\scenario_1\scenario_status.json`

```json
{
  "status": "spice_success",
  "stage": "scenario_spice_executed",
  "scenario_id": "scenario_1",
  "source": "guided_chat",
  "spice_executed": true,
  "created_or_updated_at": "2026-07-27T16:32:03",
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\c03\\scenarios\\scenario_1\\run\\08_spice_run.json",
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\c03\\scenarios\\scenario_1\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 3,
    "changed_count": 3,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 2,
    "expectations_met_count": 2,
    "expectations_failed_count": 0,
    "expectations_missing_count": 0,
    "meaningful_improvement_count": 2,
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
  "controlled_scenario_report": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\c03\\scenarios\\scenario_1\\12_controlled_scenarios.json",
  "executed_scenarios_count": 1,
  "scenario_budget_exhausted": false,
  "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
}
```

#### controlled_scenario_report

- Role: Report produced by the controlled scenario runner.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\c03\scenarios\scenario_1\12_controlled_scenarios.json`

```json
{
  "source_format": "pipeline2.0_controlled_scenario_report",
  "status": "spice_success",
  "scenario_id": "scenario_1",
  "scenario_title": "Aumentare controllatamente il livello di VAUDIO_IN",
  "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\c03\\scenarios\\scenario_1",
  "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\c03\\scenarios\\scenario_1\\run",
  "netlist": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\c03\\scenarios\\scenario_1\\run\\07_netlist.cir",
  "applied_actions": [
    {
      "status": "applied",
      "type": "change_source_value",
      "target": "VAUDIO_IN",
      "resolved_source_name": "VAUDIO_IN",
      "tried_source_names": [
        "VAUDIO_IN"
      ],
      "value": "SIN(0 0.05 1000)",
      "normalized_source_definition": "SIN(0 0.05 1000)",
      "old_line": "VAUDIO_IN N005 0 SIN(0 0.02 1000)",
      "new_line": "VAUDIO_IN N005 0 SIN(0 0.05 1000)",
      "operation": "updated",
      "spice_executed": false,
      "index": 1
    }
  ],
  "unsupported_actions": [],
  "failed_actions": [],
  "spice_executed": true,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\c03\\scenarios\\scenario_1\\run\\08_spice_run.json",
  "spice_status": "success",
  "spice_exit_code": 0,
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\c03\\scenarios\\scenario_1\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 3,
    "changed_count": 3,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 2,
    "expectations_met_count": 2,
    "expectations_failed_count": 0,
    "expectations_missing_count": 0,
    "meaningful_improvement_count": 2,
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
  "created_or_updated_at": "2026-07-27T16:32:03"
}
```

#### scenario_comparison

- Role: Base-vs-scenario comparison used to evaluate the scenario.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\c03\scenarios\scenario_1\scenario_comparison.json`

```json
{
  "source_format": "pipeline2.0_scenario_comparison",
  "scenario_id": "scenario_1",
  "scenario_title": "Aumentare controllatamente il livello di VAUDIO_IN",
  "scenario_intent": "diagnostic",
  "base_output_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\c03",
  "scenario_run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\c03\\scenarios\\scenario_1\\run",
  "base_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\c03\\08_ngspice_stdout.txt",
  "scenario_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\c03\\scenarios\\scenario_1\\run\\08_ngspice_stdout.txt",
  "base_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\c03\\08_ngspice_stderr.txt",
  "scenario_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\c03\\scenarios\\scenario_1\\run\\08_ngspice_stderr.txt",
  "quantities": [
    {
      "quantity": "v(N005)",
      "base_value": 0.0399988024,
      "scenario_value": 0.0999986278,
      "delta": 0.059999825400000005,
      "change": "changed",
      "expectation": null,
      "expectation_met": null,
      "relative_change": 1.5000405462139539,
      "meaningful_improvement": false,
      "metric": "v(n005).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": -0.0199994012,
        "max": 0.0199994012,
        "mean": 6.47852009990011e-07,
        "vpp": 0.0399988024,
        "final": -9.79717439e-17,
        "abs_peak": 0.0199994012
      },
      "scenario_details": {
        "min": -0.0499993139,
        "max": 0.0499993139,
        "mean": 1.5265326378726415e-06,
        "vpp": 0.0999986278,
        "final": -2.4492936e-16,
        "abs_peak": 0.0499993139
      }
    },
    {
      "quantity": "v(N008)",
      "base_value": 4.05576527,
      "scenario_value": 10.13823537,
      "delta": 6.0824701,
      "change": "changed",
      "expectation": "magnitude_increased",
      "expectation_met": true,
      "relative_change": 1.4997095973456076,
      "meaningful_improvement": true,
      "metric": "v(n008).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": -2.06123533,
        "max": 1.99452994,
        "mean": -0.015691408985354375,
        "vpp": 4.05576527,
        "final": -0.026393949,
        "abs_peak": 2.06123533
      },
      "scenario_details": {
        "min": -5.15248028,
        "max": 4.98575509,
        "mean": -0.03923117687946769,
        "vpp": 10.13823537,
        "final": -0.0660039101,
        "abs_peak": 5.15248028
      }
    },
    {
      "quantity": "v(N004)",
      "base_value": 3.9947576499999995,
      "scenario_value": 9.98515868,
      "delta": 5.99040103,
      "change": "changed",
      "expectation": "magnitude_increased",
      "expectation_met": true,
      "relative_change": 1.499565569390674,
      "meaningful_improvement": true,
      "metric": "v(n004).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": 6.99449945,
        "max": 10.9892571,
        "mean": 8.991863124840954,
        "vpp": 3.9947576499999995,
        "final": 8.88664627,
        "abs_peak": 10.9892571
      },
      "scenario_details": {
        "min": 3.99925812,
        "max": 13.9844168,
        "mean": 8.991786664135189,
        "vpp": 9.98515868,
        "final": 8.72875603,
        "abs_peak": 13.9844168
      }
    }
  ],
  "summary": {
    "requested_count": 3,
    "changed_count": 3,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 2,
    "expectations_met_count": 2,
    "expectations_failed_count": 0,
    "expectations_missing_count": 0,
    "meaningful_improvement_count": 2,
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
  "created_or_updated_at": "2026-07-27T16:32:03"
}
```


## Loaded artifacts

### graph

- Step: `01`
- Role: Graph JSON copied from Pipeline 1.0.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\c03\01_graph.json`

```json
{
  "image_id": "c03",
  "image_name": "c03.jpg",
  "components": [
    {
      "component_id": "terminal26.1",
      "instance_id": "26.1",
      "class_name": "Terminal",
      "terminals": [
        {
          "terminal_id": "terminal26.1_t1",
          "name": "t1",
          "relative_position": "top"
        }
      ]
    },
    {
      "component_id": "gnd9.1",
      "instance_id": "9.1",
      "class_name": "GND",
      "terminals": [
        {
          "terminal_id": "gnd9.1_t1",
          "name": "t1",
          "relative_position": "top"
        }
      ]
    },
    {
      "component_id": "terminal26.2",
      "instance_id": "26.2",
      "class_name": "Terminal",
      "terminals": [
        {
          "terminal_id": "terminal26.2_t1",
          "name": "t1",
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
          "terminal_id": "polarized_capacitor20.1_negative",
          "name": "negative",
          "relative_position": "left"
        },
        {
          "terminal_id": "polarized_capacitor20.1_positive",
          "name": "positive",
          "relative_position": "right"
        }
      ]
    },
    {
      "component_id": "polarized_capacitor20.2",
      "instance_id": "20.2",
      "class_name": "Polarized_Capacitor",
      "terminals": [
        {
          "terminal_id": "polarized_capacitor20.2_positive",
          "name": "positive",
          "relative_position": "left"
        },
        {
          "terminal_id": "polarized_capacitor20.2_negative",
          "name": "negative",
          "relative_position": "right"
        }
      ]
    },
    {
      "component_id": "operational_amplifier19.1",
      "instance_id": "19.1",
      "class_name": "Operational_Amplifier",
      "terminals": [
        {
          "terminal_id": "operational_amplifier19.1_in1",
          "name": "in1",
          "relative_position": "left"
        },
        {
          "terminal_id": "operational_amplifier19.1_in2",
          "name": "in2",
          "relative_position": "left"
        },
        {
          "terminal_id": "operational_amplifier19.1_out",
          "name": "out",
          "relative_position": "right"
        },
        {
          "terminal_id": "operational_amplifier19.1_aux1",
          "name": "aux1",
          "relative_position": "top"
        },
        {
          "terminal_id": "operational_amplifier19.1_aux2",
          "name": "aux2",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "gnd9.2",
      "instance_id": "9.2",
      "class_name": "GND",
      "terminals": [
        {
          "terminal_id": "gnd9.2_t1",
          "name": "t1",
          "relative_position": "top"
        }
      ]
    },
    {
      "component_id": "polarized_capacitor20.3",
      "instance_id": "20.3",
      "class_name": "Polarized_Capacitor",
      "terminals": [
        {
          "terminal_id": "polarized_capacitor20.3_positive",
          "name": "positive",
          "relative_position": "top"
        },
        {
          "terminal_id": "polarized_capacitor20.3_negative",
          "name": "negative",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "gnd9.3",
      "instance_id": "9.3",
      "class_name": "GND",
      "terminals": [
        {
          "terminal_id": "gnd9.3_t1",
          "name": "t1",
          "relative_position": "top"
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
      "component_id": "polarized_capacitor20.4",
      "instance_id": "20.4",
      "class_name": "Polarized_Capacitor",
      "terminals": [
        {
          "terminal_id": "polarized_capacitor20.4_positive",
          "name": "positive",
          "relative_position": "top"
        },
        {
          "terminal_id": "polarized_capacitor20.4_negative",
          "name": "negative",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "polarized_capacitor20.5",
      "instance_id": "20.5",
      "class_name": "Polarized_Capacitor",
      "terminals": [
        {
          "terminal_id": "polarized_capacitor20.5_positive",
          "name": "positive",
          "relative_position": "top"
        },
        {
          "terminal_id": "polarized_capacitor20.5_negative",
          "name": "negative",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "gnd9.4",
      "instance_id": "9.4",
      "class_name": "GND",
      "terminals": [
        {
          "terminal_id": "gnd9.4_t1",
          "name": "t1",
          "relative_position": "top"
        }
      ]
    },
    {
      "component_id": "terminal26.3",
      "instance_id": "26.3",
      "class_name": "Terminal",
      "terminals": [
        {
          "terminal_id": "terminal26.3_t1",
          "name": "t1",
          "relative_position": "left"
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
      "component_id": "polarized_capacitor20.6",
      "instance_id": "20.6",
      "class_name": "Polarized_Capacitor",
      "terminals": [
        {
          "terminal_id": "polarized_capacitor20.6_positive",
          "name": "positive",
          "relative_position": "left"
        },
        {
          "terminal_id": "polarized_capacitor20.6_negative",
          "name": "negative",
          "relative_position": "right"
        }
      ]
    },
    {
      "component_id": "polarized_capacitor20.7",
      "instance_id": "20.7",
      "class_name": "Polarized_Capacitor",
      "terminals": [
        {
          "terminal_id": "polarized_capacitor20.7_positive",
          "name": "positive",
          "relative_position": "top"
        },
        {
          "terminal_id": "polarized_capacitor20.7_negative",
          "name": "negative",
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
      "component_id": "gnd9.5",
      "instance_id": "9.5",
      "class_name": "GND",
      "terminals": [
        {
          "terminal_id": "gnd9.5_t1",
          "name": "t1",
          "relative_position": "top"
        }
      ]
    },
    {
      "component_id": "speaker24.1",
      "instance_id": "24.1",
      "class_name": "Speaker",
      "terminals": [
        {
          "terminal_id": "speaker24.1_t1",
          "name": "t1",
          "relative_position": "left"
        },
        {
          "terminal_id": "speaker24.1_t2",
          "name": "t2",
          "relative_position": "left"
        }
      ]
    }
  ],
  "terminal_metadata": {},
  "graph": {
    "gnd9.1_t1": [
      "terminal26.2_t1"
    ],
    "gnd9.2_t1": [
      "operational_amplifier19.1_aux2"
    ],
    "gnd9.3_t1": [
      "polarized_capacitor20.3_negative"
    ],
    "gnd9.4_t1": [
      "polarized_capacitor20.5_negative"
    ],
    "gnd9.5_t1": [
      "resistor22.2_t2",
      "resistor22.4_t2",
      "speaker24.1_t2"
    ],
    "operational_amplifier19.1_aux1": [
      "polarized_capacitor20.3_positive",
      "polarized_capacitor20.5_positive",
      "terminal26.3_t1"
    ],
    "operational_amplifier19.1_aux2": [
      "gnd9.2_t1"
    ],
    "operational_amplifier19.1_in1": [
      "polarized_capacitor20.1_positive"
    ],
    "operational_amplifier19.1_in2": [
      "polarized_capacitor20.2_positive",
      "resistor22.1_t2"
    ],
    "operational_amplifier19.1_out": [
      "polarized_capacitor20.4_positive",
      "polarized_capacitor20.6_positive",
      "resistor22.3_t1"
    ],
    "polarized_capacitor20.1_negative": [
      "terminal26.1_t1"
    ],
    "polarized_capacitor20.1_positive": [
      "operational_amplifier19.1_in1"
    ],
    "polarized_capacitor20.2_negative": [
      "resistor22.2_t1",
      "resistor22.3_t2"
    ],
    "polarized_capacitor20.2_positive": [
      "operational_amplifier19.1_in2",
      "resistor22.1_t2"
    ],
    "polarized_capacitor20.3_negative": [
      "gnd9.3_t1"
    ],
    "polarized_capacitor20.3_positive": [
      "operational_amplifier19.1_aux1",
      "polarized_capacitor20.5_positive",
      "terminal26.3_t1"
    ],
    "polarized_capacitor20.4_negative": [
      "resistor22.1_t1"
    ],
    "polarized_capacitor20.4_positive": [
      "operational_amplifier19.1_out",
      "polarized_capacitor20.6_positive",
      "resistor22.3_t1"
    ],
    "polarized_capacitor20.5_negative": [
      "gnd9.4_t1"
    ],
    "polarized_capacitor20.5_positive": [
      "operational_amplifier19.1_aux1",
      "polarized_capacitor20.3_positive",
      "terminal26.3_t1"
    ],
    "polarized_capacitor20.6_negative": [
      "polarized_capacitor20.7_positive",
      "speaker24.1_t1"
    ],
    "polarized_capacitor20.6_positive": [
      "operational_amplifier19.1_out",
      "polarized_capacitor20.4_positive",
      "resistor22.3_t1"
    ],
    "polarized_capacitor20.7_negative": [
      "resistor22.4_t1"
    ],
    "polarized_capacitor20.7_positive": [
      "polarized_capacitor20.6_negative",
      "speaker24.1_t1"
    ],
    "resistor22.1_t1": [
      "polarized_capacitor20.4_negative"
    ],
    "resistor22.1_t2": [
      "operational_amplifier19.1_in2",
      "polarized_capacitor20.2_positive"
    ],
    "resistor22.2_t1": [
      "polarized_capacitor20.2_negative",
      "resistor22.3_t2"
    ],
    "resistor22.2_t2": [
      "gnd9.5_t1",
      "resistor22.4_t2",
      "speaker24.1_t2"
    ],
    "resistor22.3_t1": [
      "operational_amplifier19.1_out",
      "polarized_capacitor20.4_positive",
      "polarized_capacitor20.6_positive"
    ],
    "resistor22.3_t2": [
      "polarized_capacitor20.2_negative",
      "resistor22.2_t1"
    ],
    "resistor22.4_t1": [
      "polarized_capacitor20.7_negative"
    ],
    "resistor22.4_t2": [
      "gnd9.5_t1",
      "resistor22.2_t2",
      "speaker24.1_t2"
    ],
    "speaker24.1_t1": [
      "polarized_capacitor20.6_negative",
      "polarized_capacitor20.7_positive"
    ],
    "speaker24.1_t2": [
      "gnd9.5_t1",
      "resistor22.2_t2",
      "resistor22.4_t2"
    ],
    "terminal26.1_t1": [
      "polarized_capacitor20.1_negative"
    ],
    "terminal26.2_t1": [
      "gnd9.1_t1"
    ],
    "terminal26.3_t1": [
      "operational_amplifier19.1_aux1",
      "polarized_capacitor20.3_positive",
      "polarized_capacitor20.5_positive"
    ]
  },
  "warnings": {
    "unconnected_te
```

> Artifact truncated in this preview. The original file remains available through the manifest path.

### node_map

- Step: `03`
- Role: Maps component terminals to SPICE node names.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\c03\03_node_map.json`

```json
{
  "circuit_id": "c03",
  "source_format": "pipeline2.0_node_map",
  "nodes": [
    {
      "node_id": "0",
      "kind": "ground",
      "terminals": [
        "gnd9.1_t1",
        "gnd9.2_t1",
        "gnd9.3_t1",
        "gnd9.4_t1",
        "gnd9.5_t1",
        "operational_amplifier19.1_aux2",
        "polarized_capacitor20.3_negative",
        "polarized_capacitor20.5_negative",
        "resistor22.2_t2",
        "resistor22.4_t2",
        "speaker24.1_t2",
        "terminal26.2_t1"
      ],
      "terminal_count": 12,
      "source_groups": [
        [
          "gnd9.1_t1",
          "terminal26.2_t1"
        ],
        [
          "gnd9.2_t1",
          "operational_amplifier19.1_aux2"
        ],
        [
          "gnd9.3_t1",
          "polarized_capacitor20.3_negative"
        ],
        [
          "gnd9.4_t1",
          "polarized_capacitor20.5_negative"
        ],
        [
          "gnd9.5_t1",
          "resistor22.2_t2",
          "resistor22.4_t2",
          "speaker24.1_t2"
        ]
      ]
    },
    {
      "node_id": "N001",
      "kind": "normal",
      "terminals": [
        "operational_amplifier19.1_aux1",
        "polarized_capacitor20.3_positive",
        "polarized_capacitor20.5_positive",
        "terminal26.3_t1"
      ],
      "terminal_count": 4
    },
    {
      "node_id": "N002",
      "kind": "normal",
      "terminals": [
        "operational_amplifier19.1_in1",
        "polarized_capacitor20.1_positive"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N003",
      "kind": "normal",
      "terminals": [
        "operational_amplifier19.1_in2",
        "polarized_capacitor20.2_positive",
        "resistor22.1_t2"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N004",
      "kind": "normal",
      "terminals": [
        "operational_amplifier19.1_out",
        "polarized_capacitor20.4_positive",
        "polarized_capacitor20.6_positive",
        "resistor22.3_t1"
      ],
      "terminal_count": 4
    },
    {
      "node_id": "N005",
      "kind": "normal",
      "terminals": [
        "polarized_capacitor20.1_negative",
        "terminal26.1_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N006",
      "kind": "normal",
      "terminals": [
        "polarized_capacitor20.2_negative",
        "resistor22.2_t1",
        "resistor22.3_t2"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N007",
      "kind": "normal",
      "terminals": [
        "polarized_capacitor20.4_negative",
        "resistor22.1_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N008",
      "kind": "normal",
      "terminals": [
        "polarized_capacitor20.6_negative",
        "polarized_capacitor20.7_positive",
        "speaker24.1_t1"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N009",
      "kind": "normal",
      "terminals": [
        "polarized_capacitor20.7_negative",
        "resistor22.4_t1"
      ],
      "terminal_count": 2
    }
  ],
  "terminal_to_node": {
    "gnd9.1_t1": "0",
    "gnd9.2_t1": "0",
    "gnd9.3_t1": "0",
    "gnd9.4_t1": "0",
    "gnd9.5_t1": "0",
    "operational_amplifier19.1_aux1": "N001",
    "operational_amplifier19.1_aux2": "0",
    "operational_amplifier19.1_in1": "N002",
    "operational_amplifier19.1_in2": "N003",
    "operational_amplifier19.1_out": "N004",
    "polarized_capacitor20.1_negative": "N005",
    "polarized_capacitor20.1_positive": "N002",
    "polarized_capacitor20.2_negative": "N006",
    "polarized_capacitor20.2_positive": "N003",
    "polarized_capacitor20.3_negative": "0",
    "polarized_capacitor20.3_positive": "N001",
    "polarized_capacitor20.4_negative": "N007",
    "polarized_capacitor20.4_positive": "N004",
    "polarized_capacitor20.5_negative": "0",
    "polarized_capacitor20.5_positive": "N001",
    "polarized_capacitor20.6_negative": "N008",
    "polarized_capacitor20.6_positive": "N004",
    "polarized_capacitor20.7_negative": "N009",
    "polarized_capacitor20.7_positive": "N008",
    "resistor22.1_t1": "N007",
    "resistor22.1_t2": "N003",
    "resistor22.2_t1": "N006",
    "resistor22.2_t2": "0",
    "resistor22.3_t1": "N004",
    "resistor22.3_t2": "N006",
    "resistor22.4_t1": "N009",
    "resistor22.4_t2": "0",
    "speaker24.1_t1": "N008",
    "speaker24.1_t2": "0",
    "terminal26.1_t1": "N005",
    "terminal26.2_t1": "0",
    "terminal26.3_t1": "N001"
  },
  "component_terminal_nodes": {
    "gnd9.1": {
      "t1": "0"
    },
    "gnd9.2": {
      "t1": "0"
    },
    "gnd9.3": {
      "t1": "0"
    },
    "gnd9.4": {
      "t1": "0"
    },
    "gnd9.5": {
      "t1": "0"
    },
    "operational_amplifier19.1": {
      "in1": "N002",
      "in2": "N003",
      "out": "N004",
      "aux1": "N001",
      "aux2": "0"
    },
    "polarized_capacitor20.1": {
      "negative": "N005",
      "positive": "N002"
    },
    "polarized_capacitor20.2": {
      "positive": "N003",
      "negative": "N006"
    },
    "polarized_capacitor20.3": {
      "positive": "N001",
      "negative": "0"
    },
    "polarized_capacitor20.4": {
      "positive": "N004",
      "negative": "N007"
    },
    "polarized_capacitor20.5": {
      "positive": "N001",
      "negative": "0"
    },
    "polarized_capacitor20.6": {
      "positive": "N004",
      "negative": "N008"
    },
    "polarized_capacitor20.7": {
      "positive": "N008",
      "negative": "N009"
    },
    "resistor22.1": {
      "t1": "N007",
      "t2": "N003"
    },
    "resistor22.2": {
      "t1": "N006",
      "t2": "0"
    },
    "resistor22.3": {
      "t1": "N004",
      "t2": "N006"
    },
    "resistor22.4": {
      "t1": "N009",
      "t2": "0"
    },
    "speaker24.1": {
      "t1": "N008",
      "t2": "0"
    },
    "terminal26.1": {
      "t1": "N005"
    },
    "terminal26.2": {
      "t1": "0"
    },
    "terminal26.3": {
      "t1": "N001"
    }
  },
  "warnings": {
    "ground_groups_count": 5,
    "multiple_ground_groups_merged_as_node_0": true,
    "singleton_nodes": [],
    "original_warnings": {
      "unconnected_terminals": [],
      "unmatched_terminals": [],
      "suspicious_matches": []
    },
    "normalization_warnings": []
  },
  "stats": {
    "nodes_count": 10,
    "normal_nodes_count": 9,
    "ground_nodes_count": 1,
    "ground_groups_count": 5,
    "terminal_to_node_count": 37,
    "singleton_nodes_count": 0
  }
}
```

### values_bound

- Step: `04`
- Role: Values and labels bound to graph components.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\c03\04_values_bound.json`

```json
{
  "circuit_id": "c03",
  "source_format": "pipeline2.0_values_bound",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\data\\batchPipeline2.0\\batchChatAgentEvaluation\\values\\c03_values.yaml",
  "supplies": {
    "AUDIO_IN": {
      "terminal": "terminal26.1_t1",
      "return_terminal": "terminal26.2_t1",
      "reference": 0,
      "type": "sin",
      "waveform": "sin",
      "value": 0.02,
      "unit": "V",
      "offset": 0,
      "amplitude": 0.02,
      "frequency": 1000,
      "frequency_unit": "Hz",
      "source": "manual_testbench_assumption",
      "label_text": "Audio IN: sinusoidale 20 mV picco, 1 kHz",
      "node": "N005",
      "return_node": "0"
    },
    "VCC_18": {
      "terminal": "terminal26.3_t1",
      "value": 18,
      "unit": "V",
      "reference": 0,
      "type": "dc",
      "source": "manual_from_image_label",
      "label_text": "+18 V DC",
      "node": "N001"
    }
  },
  "components": {
    "gnd9.1": {
      "class_name": "GND",
      "terminal_nodes": {
        "t1": "0"
      },
      "value_data": null,
      "status": "not_required"
    },
    "gnd9.2": {
      "class_name": "GND",
      "terminal_nodes": {
        "t1": "0"
      },
      "value_data": null,
      "status": "not_required"
    },
    "gnd9.3": {
      "class_name": "GND",
      "terminal_nodes": {
        "t1": "0"
      },
      "value_data": null,
      "status": "not_required"
    },
    "gnd9.4": {
      "class_name": "GND",
      "terminal_nodes": {
        "t1": "0"
      },
      "value_data": null,
      "status": "not_required"
    },
    "gnd9.5": {
      "class_name": "GND",
      "terminal_nodes": {
        "t1": "0"
      },
      "value_data": null,
      "status": "not_required"
    },
    "operational_amplifier19.1": {
      "class_name": "Operational_Amplifier",
      "terminal_nodes": {
        "in1": "N002",
        "in2": "N003",
        "out": "N004",
        "aux1": "N001",
        "aux2": "0"
      },
      "value_data": {
        "model": "TDA2003_SIMPLE",
        "source": "manual_image_validation_TDA2003_pin_mapping",
        "label_text": "IC1 TDA2003; modello funzionale SPICE",
        "viewer_override": {
          "visual_class": "operational_amplifier",
          "label": "IC1",
          "display_value": "TDA2003",
          "tooltip": "IC1 TDA2003; equivalente funzionale per il testbench"
        },
        "spice_override": {
          "emit_as": "subcircuit",
          "pin_order": [
            "INP",
            "INM",
            "VCC",
            "VEE",
            "OUT"
          ],
          "node_refs": {
            "INP": "operational_amplifier19.1_in1",
            "INM": "operational_amplifier19.1_in2",
            "VCC": "operational_amplifier19.1_aux1",
            "VEE": "operational_amplifier19.1_aux2",
            "OUT": "operational_amplifier19.1_out"
          },
          "resolved_node_refs": {
            "INP": "N002",
            "INM": "N003",
            "VCC": "N001",
            "VEE": "0",
            "OUT": "N004"
          }
        }
      },
      "status": "unsupported_for_now"
    },
    "polarized_capacitor20.1": {
      "class_name": "Polarized_Capacitor",
      "terminal_nodes": {
        "negative": "N005",
        "positive": "N002"
      },
      "value_data": {
        "value": 10,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C7 10 uF",
        "viewer_override": {
          "label": "C7",
          "display_value": "10 uF"
        }
      },
      "status": "bound"
    },
    "polarized_capacitor20.2": {
      "class_name": "Polarized_Capacitor",
      "terminal_nodes": {
        "positive": "N003",
        "negative": "N006"
      },
      "value_data": {
        "value": 470,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C4 470 uF",
        "viewer_override": {
          "label": "C4",
          "display_value": "470 uF"
        }
      },
      "status": "bound"
    },
    "polarized_capacitor20.3": {
      "class_name": "Polarized_Capacitor",
      "terminal_nodes": {
        "positive": "N001",
        "negative": "0"
      },
      "value_data": {
        "value": 1000,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C1 1000 uF",
        "viewer_override": {
          "label": "C1",
          "display_value": "1000 uF"
        }
      },
      "status": "bound"
    },
    "polarized_capacitor20.4": {
      "class_name": "Polarized_Capacitor",
      "terminal_nodes": {
        "positive": "N004",
        "negative": "N007"
      },
      "value_data": {
        "value": 39,
        "unit": "nf",
        "source": "manual_from_image_label",
        "label_text": "C3 39 nF",
        "viewer_override": {
          "label": "C3",
          "display_value": "39 nF"
        }
      },
      "status": "bound"
    },
    "polarized_capacitor20.5": {
      "class_name": "Polarized_Capacitor",
      "terminal_nodes": {
        "positive": "N001",
        "negative": "0"
      },
      "value_data": {
        "value": 100,
        "unit": "nf",
        "source": "manual_from_image_label",
        "label_text": "C2 100 nF",
        "viewer_override": {
          "label": "C2",
          "display_value": "100 nF"
        }
      },
      "status": "bound"
    },
    "polarized_capacitor20.6": {
      "class_name": "Polarized_Capacitor",
      "terminal_nodes": {
        "positive": "N004",
        "negative": "N008"
      },
      "value_data": {
        "value": 1000,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C5 1000 uF",
        "viewer_override": {
          "label": "C5",
          "display_value": "1000 uF"
        }
      },
      "status": "bound"
    },
    "polarized_capacitor20.7": {
      "class_name": "Polarized_Capacitor",
      "terminal_nodes": {
        "positive": "N008",
        "negative": "N009"
      },
      "value_data": {
        "value": 100,
        "unit": "nf",
        "source": "manual_from_image_label",
        "label_text": "C6 100 nF",
        "viewer_override": {
          "label": "C6",
          "display_value": "100 nF"
        }
      },
      "status": "bound"
    },
    "resistor22.1": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N007",
        "t2": "N003"
      },
      "value_data": {
        "value": 39,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R1 39 ohm",
        "viewer_override": {
          "label": "R1",
          "display_value": "39 ohm"
        }
      },
      "status": "bound"
    },
    "resistor22.2": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N006",
        "t2": "0"
      },
      "value_data": {
        "value": 2.2,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R3 2.2 ohm",
        "viewer_override": {
          "label": "R3",
          "display_value": "2.2 ohm"
        }
      },
      "status": "bound"
    },
    "resistor22.3": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N004",
        "t2": "N006"
      },
      "value_data": {
        "value": 220,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R2 220 ohm",
        "viewer_override": {
          "label": "R2",
          "display_value": "220 ohm"
        }
      },
      "status": "bound"
    },
    "resistor22.4": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N009",
        "t2": "0"
      },
      "value_data": {
        "value": 1,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R4 1 ohm",
        "viewer_override": {
          "label": "R4",
          "display_value": "1 ohm"
        }
      },
      "status": "bound"
    },
    "speaker24.1": {
      "class_name": "Speaker",
      "terminal_nodes": {
        "t1": "N008",
        "t2": "0"
      },
      "value_data": {
        "spice_override": {
          "emit_as": "resistive_load",
          "equivalent_resistance": 4,
          "resistance_unit": "ohm",
          "node_order": [
            "t1",
            "t2"
          ],
          "semantic_role": "speaker_equivalent"
        },
        "source": "manual_from_image_label",
        "label_text": "K1 speaker equivalente 4 ohm",
        "viewer_override": {
          "visual_class": "speaker",
          "label": "K1",
          "display_value": "4 ohm"
        }
      },
      "status": "bound"
    },
    "terminal26.1": {
      "class_name": "Terminal",
      "terminal_nodes": {
        "t1": "N005"
      },
      "value_data": null,
      "status": "not_required"
    },
    "terminal26.2": {
      "class_name": "Terminal",
      "terminal_nodes": {
        "t1": "0"
      },
      "value_data": null,
      "status": "not_required"
    },
    "terminal26.3": {
      "class_name": "Terminal",
      "terminal_nodes": {
        "t1": "N001"
      },
      "value_data": null,
      "status": "not_required"
    }
  },
  "nodes": {
    "operational_amplifier19.1_in2": {
      "label": "INVERTING_INPUT",
      "source": "manual_from_validated_graph",
      "node": "N003"
    },
    "operational_amplifier19.1_out": {
      "label": "IC_OUTPUT",
      "source": "manual_from_validated_graph",
      "node": "N004"
    },
    "polarized_capacitor20.2_negative": {
      "label": "FEEDBACK_DIVIDER",
      "source": "manual_from_validated_graph",
      "node": "N006"
    },
    "speaker24.1_t1": {
      "label": "AUDIO_OUT",
      "source": "manual_from_validated_graph",
      "node": "N008"
    },
    "terminal26.1_t1": {
      "label": "INPUT",
      "source": "manual_from_image_label",
      "label_text": "Ingresso audio",
      "node": "N005"
    },
    "terminal26.2_t1": {
      "label": "INPUT_RETURN",
      "spice_node": 0,
      "source": "manual_from_image_ground",
      "label_text": "Ritorno ingresso audio",
      "node": "0"
    },
    "terminal26.3_t1": {
      "label": "VCC_18",
      "source": "manual_from_image_label",
      "label_text": "+18 V DC",
      "node": "N001"
    }
  },
  "spice_topology_overlay": [],
  "simulation": {
    "analyses": [
      "op",
      "tran"
    ],
    "tran": {
      "step": "10us",
      "stop": "20ms"
    }
  },
  "missing": [],
  "stats": {
    "components_total": 21,
    "bound_components": 12,
    "missing_components": 0,
    "not_required_components": 8,
    "unsupported_components": 1,
    "supplies_count": 2,
    "manual_nodes_count": 7
  }
}
```

### component_rules

- Step: `06`
- Role: SPICE conversion rules for each component.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\c03\06_component_rules.json`

```json
{
  "circuit_id": "c03",
  "source_format": "pipeline2.0_component_rules",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\data\\batchPipeline2.0\\batchChatAgentEvaluation\\values\\c03_values.yaml",
  "spice_classes_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_spice_classes.yaml",
  "supplies": {
    "AUDIO_IN": {
      "status": "spice_ready",
      "spice_prefix": "V",
      "emit_as": "independent_voltage_source",
      "nodes": [
        "N005",
        "0"
      ],
      "parameters": {
        "terminal": "terminal26.1_t1",
        "return_terminal": "terminal26.2_t1",
        "reference": 0,
        "type": "sin",
        "waveform": "sin",
        "value": 0.02,
        "unit": "V",
        "offset": 0,
        "amplitude": 0.02,
        "frequency": 1000,
        "frequency_unit": "Hz",
        "source": "manual_testbench_assumption",
        "label_text": "Audio IN: sinusoidale 20 mV picco, 1 kHz",
        "node": "N005",
        "return_node": "0"
      }
    },
    "VCC_18": {
      "status": "spice_ready",
      "spice_prefix": "V",
      "emit_as": "independent_voltage_source",
      "nodes": [
        "N001",
        "0"
      ],
      "parameters": {
        "terminal": "terminal26.3_t1",
        "value": 18,
        "unit": "V",
        "reference": 0,
        "type": "dc",
        "source": "manual_from_image_label",
        "label_text": "+18 V DC",
        "node": "N001"
      }
    }
  },
  "components": {
    "gnd9.1": {
      "class_name": "GND",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "GND terminals are already mapped to SPICE node 0."
    },
    "gnd9.2": {
      "class_name": "GND",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "GND terminals are already mapped to SPICE node 0."
    },
    "gnd9.3": {
      "class_name": "GND",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "GND terminals are already mapped to SPICE node 0."
    },
    "gnd9.4": {
      "class_name": "GND",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "GND terminals are already mapped to SPICE node 0."
    },
    "gnd9.5": {
      "class_name": "GND",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "GND terminals are already mapped to SPICE node 0."
    },
    "operational_amplifier19.1": {
      "class_name": "Operational_Amplifier",
      "status": "spice_ready",
      "spice_support": "subcircuit",
      "spice_prefix": "X",
      "emit_as": "subcircuit",
      "node_order": [
        "INP",
        "INM",
        "VCC",
        "VEE",
        "OUT"
      ],
      "nodes": [
        "N002",
        "N003",
        "N001",
        "0",
        "N004"
      ],
      "parameters": {
        "model": "TDA2003_SIMPLE",
        "source": "manual_image_validation_TDA2003_pin_mapping",
        "label_text": "IC1 TDA2003; modello funzionale SPICE",
        "viewer_override": {
          "visual_class": "operational_amplifier",
          "label": "IC1",
          "display_value": "TDA2003",
          "tooltip": "IC1 TDA2003; equivalente funzionale per il testbench"
        },
        "spice_override": {
          "emit_as": "subcircuit",
          "pin_order": [
            "INP",
            "INM",
            "VCC",
            "VEE",
            "OUT"
          ],
          "node_refs": {
            "INP": "operational_amplifier19.1_in1",
            "INM": "operational_amplifier19.1_in2",
            "VCC": "operational_amplifier19.1_aux1",
            "VEE": "operational_amplifier19.1_aux2",
            "OUT": "operational_amplifier19.1_out"
          },
          "resolved_node_refs": {
            "INP": "N002",
            "INM": "N003",
            "VCC": "N001",
            "VEE": "0",
            "OUT": "N004"
          }
        }
      },
      "reason": "Explicit YAML override emitted as a SPICE subcircuit."
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
        "N002",
        "N005"
      ],
      "parameters": {
        "value": 10,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C7 10 uF",
        "viewer_override": {
          "label": "C7",
          "display_value": "10 uF"
        }
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
        "N003",
        "N006"
      ],
      "parameters": {
        "value": 470,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C4 470 uF",
        "viewer_override": {
          "label": "C4",
          "display_value": "470 uF"
        }
      }
    },
    "polarized_capacitor20.3": {
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
        "N001",
        "0"
      ],
      "parameters": {
        "value": 1000,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C1 1000 uF",
        "viewer_override": {
          "label": "C1",
          "display_value": "1000 uF"
        }
      }
    },
    "polarized_capacitor20.4": {
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
        "N004",
        "N007"
      ],
      "parameters": {
        "value": 39,
        "unit": "nf",
        "source": "manual_from_image_label",
        "label_text": "C3 39 nF",
        "viewer_override": {
          "label": "C3",
          "display_value": "39 nF"
        }
      }
    },
    "polarized_capacitor20.5": {
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
        "N001",
        "0"
      ],
      "parameters": {
        "value": 100,
        "unit": "nf",
        "source": "manual_from_image_label",
        "label_text": "C2 100 nF",
        "viewer_override": {
          "label": "C2",
          "display_value": "100 nF"
        }
      }
    },
    "polarized_capacitor20.6": {
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
        "N004",
        "N008"
      ],
      "parameters": {
        "value": 1000,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C5 1000 uF",
        "viewer_override": {
          "label": "C5",
          "display_value": "1000 uF"
        }
      }
    },
    "polarized_capacitor20.7": {
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
        "N009"
      ],
      "parameters": {
        "value": 100,
        "unit": "nf",
        "source": "manual_from_image_label",
        "label_text": "C6 100 nF",
        "viewer_override": {
          "label": "C6",
          "display_value": "100 nF"
        }
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
        "N007",
        "N003"
      ],
      "parameters": {
        "value": 39,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R1 39 ohm",
        "viewer_override": {
          "label": "R1",
          "display_value": "39 ohm"
        }
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
        "N006",
        "0"
      ],
      "parameters": {
        "value": 2.2,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R3 2.2 ohm",
        "viewer_override": {
          "label": "R3",
          "display_value": "2.2 ohm"
        }
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
        "N006"
      ],
      "parameters": {
        "value": 220,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R2 220 ohm",
        "viewer_override": {
          "label": "R2",
          "display_value": "220 ohm"
        }
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
        "N009",
        "0"
      ],
      "parameters": {
        "value": 1,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R4 1 ohm",
        "viewer_override": {
          "label": "R4",
          "display_value": "1 ohm"
        }
      }
    },
    "speaker24.1": {
      "class_name": "Speaker",
      "status": "spice_ready",
      "spice_support": "equivalent",
      "spice_prefix": "R",
      "emit_as": "resistive_load",
      "node_order": [
        "t1",
        "t2"
      ],
      "nodes": [
        "N008",
        "0"
      ],
      "parameters": {
        "spice_override": {
          "emit_as": "resistive_load",
          "equivalent_resistance": 4,
          "resistance_unit": "ohm",
          "node_order": [
            "t1",
            "t2"
          ],
          "semantic_role": "speaker_equivalent"
        },
        "source": "manual_from_image_label",
        "label_text": "K1 speaker equivalente 4 ohm",
        "viewer_override": {
          "visual_class": "speaker",
          "label": "K1",
          "display_value": "4 ohm"
        },
        "equivalent_resistance": 4,
        "resistance_unit": "ohm"
      },
      "reason": "Explicit YAML override emitted as an equivalent resistive load."
    },
    "terminal26.1": {
      "class_name": "Terminal",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "External terminal/label; useful for nodes and interface handling."
    },
    "terminal26.2": {
      "class_name": "Terminal",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "External terminal/label; useful for nodes and interface handling."
    },
    "terminal26.3": {
      "class_name": "Terminal",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "External terminal/label; useful for nodes and interface handling."
    }
  },
  "simulation": {
    "analyses": [
```

> Artifact truncated in this preview. The original file remains available through the manifest path.

### netlist

- Step: `07`
- Role: Generated SPICE netlist.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\c03\07_netlist.cir`

```spice
* pipeline2.0 netlist
* circuit: c03

VAUDIO_IN N005 0 SIN(0 0.02 1000)
VVCC_18 N001 0 DC 18
Xoperational_amplifier19_1 N002 N003 N001 0 N004 TDA2003_SIMPLE
Cpolarized_capacitor20_1 N002 N005 10u
Cpolarized_capacitor20_2 N003 N006 470u
Cpolarized_capacitor20_3 N001 0 1000u
Cpolarized_capacitor20_4 N004 N007 39n
Cpolarized_capacitor20_5 N001 0 100n
Cpolarized_capacitor20_6 N004 N008 1000u
Cpolarized_capacitor20_7 N008 N009 100n
Rresistor22_1 N007 N003 39
Rresistor22_2 N006 0 2.2
Rresistor22_3 N004 N006 220
Rresistor22_4 N009 0 1
Rspeaker24_1 N008 0 4

.subckt TDA2003_SIMPLE INP INM VCC VEE OUT
EREF VREF VEE VCC VEE 0.5
RINP INP VREF 1Meg
RINM INM VREF 1Meg
BAMP NAMP VEE V={0.75+(V(VCC,VEE)-1.5)*(0.5+0.5*tanh((100000*V(INP,INM))/(0.5*(V(VCC,VEE)-1.5))))}
ROUT NAMP OUT 0.2
RBLEED VCC VEE 100k
.ends TDA2003_SIMPLE

.op
.save all
.tran 10us 20ms

.control
set wr_singlescale
set wr_vecnames
run
wrdata 08_tran.csv time v(N001) v(N002) v(N003) v(N004) v(N005) v(N006) v(N007) v(N008) v(N009)
.endc
.end

```

### spice_emit_report

- Step: `07`
- Role: Report of emitted, skipped and warning components.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\c03\07_spice_emit_report.json`

```json
{
  "circuit_id": "c03",
  "source_format": "pipeline2.0_spice_emit_report",
  "emitted_elements": 15,
  "skipped_elements": 8,
  "skipped_components": [
    "gnd9.1",
    "gnd9.2",
    "gnd9.3",
    "gnd9.4",
    "gnd9.5",
    "terminal26.1",
    "terminal26.2",
    "terminal26.3"
  ],
  "informational_skips": [
    "gnd9.1: structural component not emitted",
    "gnd9.2: structural component not emitted",
    "gnd9.3: structural component not emitted",
    "gnd9.4: structural component not emitted",
    "gnd9.5: structural component not emitted",
    "terminal26.1: structural component not emitted",
    "terminal26.2: structural component not emitted",
    "terminal26.3: structural component not emitted"
  ],
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
      "N009"
    ],
    "device_currents": []
  },
  "models": [
    "TDA2003_SIMPLE"
  ],
  "warnings": []
}
```

### spice_run

- Step: `08`
- Role: Structured ngspice execution report.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\c03\08_spice_run.json`

```json
{
  "source_format": "pipeline2.0_spice_run",
  "status": "success",
  "netlist_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\c03\\07_netlist.cir",
  "command": [
    "C:\\Users\\m.profilo\\Spice64\\bin\\ngspice_con.exe",
    "-b",
    "07_netlist.cir"
  ],
  "exit_code": 0,
  "stdout_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\c03\\08_ngspice_stdout.txt",
  "stderr_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\c03\\08_ngspice_stderr.txt",
  "tran_raw_csv_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\c03\\08_tran_raw.csv",
  "tran_csv_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\c03\\08_tran.csv",
  "tran_plot_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\c03\\08_tran_plot.png",
  "tran_plot_png_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\c03\\08_tran_plot.png",
  "tran_plot_svg_path": null,
  "message": "ngspice completed successfully."
}
```

### ngspice_stdout

- Step: `08`
- Role: Raw ngspice stdout log.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\c03\08_ngspice_stdout.txt`

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
n005                                         0
n001                                        18
xoperational_amplifier19_1.vref               9
n002                                         9
n003                                         9
xoperational_amplifier19_1.namp               9
n004                                   8.99191
n006                                 0.0890288
n007                                         9
n008                                         0
n009                                         0
b.xoperational_amplifier19_1.bamp#branch      -0.0404676
e.xoperational_amplifier19_1.eref#branch    -9.00227e-18
vvcc_18#branch                        -0.00018
vaudio_in#branch                             0


No. of Data Rows : 2012
Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

No. of Data Rows : 1

Initial Transient Solution
--------------------------

Node                                   Voltage
----                                   -------
n005                                         0
n001                                        18
xoperational_amplifier19_1.vref               9
n002                                         9
n003                                         9
xoperational_amplifier19_1.namp               9
n004                                   8.99191
n006                                 0.0890288
n007                                         9
n008                                         0
n009                                         0
b.xoperational_amplifier19_1.bamp#branch      -0.0404676
e.xoperational_amplifier19_1.eref#branch    -9.00227e-18
vvcc_18#branch                        -0.00018
vaudio_in#branch                             0


No. of Data Rows : 2012
	Node                                  Voltage
	----                                  -------
	----	-------
	n009                             0.000000e+00
	n008                             0.000000e+00
	n007                             9.000000e+00
	n006                             8.902879e-02
	n004                             8.991907e+00
	xoperational_amplifier19_1.namp   9.000001e+00
	n003                             9.000000e+00
	n002                             9.000000e+00
	xoperational_amplifier19_1.vref   9.000000e+00
	n001                             1.800000e+01
	n005                             0.000000e+00

	Source	Current
	------	-------

	vaudio_in#branch                 0.000000e+00
	vvcc_18#branch                   -1.80000e-04
	e.xoperational_amplifier19_1.eref#branch   -9.00227e-18
	b.xoperational_amplifier19_1.bamp#branch   -4.04676e-02

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

 ASRC: Arbitrary Source 
     device b.xoperational_amplif
      dtemp                     0
          i            -0.0351284
          v               8.89367
   pos_node                     6
   neg_node                     0

 Capacitor: Fixed capacitor
     device cpolarized_capacitor2 cpolarized_capacitor2 cpolarized_capacitor2
      model                     C                     C                     C
capacitance                 1e-07                 0.001                 1e-07
      dtemp                     0                     0                     0
     bv_max                 1e+99                 1e+99                 1e+99
          i            0.00125404           -0.00534444                     0
          p          -3.46718e-05            -0.0476352                     0

 Capacitor: Fixed capacitor
     device cpolarized_capacitor2 cpolarized_capacitor2 cpolarized_capacitor2
      model                     C                     C                     C
capacitance               3.9e-08                 0.001               0.00047
      dtemp                     0                     0                     0
     bv_max                 1e+99                 1e+99                 1e+99
          i           0.000483676                     0           0.000483676
          p          -6.39508e-05                     0            0.00431002

 Capacitor: Fixed capacitor
     device cpolarized_capacitor2
      model                     C
capacitance                 1e-05
      dtemp                     0
     bv_max                 1e+99
          i          -2.88476e-15
          p          -2.59629e-14

 Resistor: Simple linear resistor
     device          rspeaker24_1         rresistor22_4         rresistor22_3
      model                     R                     R                     R
 resistance                     4                     1                   220
         ac                     4                     1                   220
      dtemp                     0                     0                     0
     bv_max                 1e+99                 1e+99                 1e+99
      noisy                     1                     1                     1
          i           -0.00659849            0.00125404             0.0399891
          p            0.00017416           1.57263e-06              0.351809

 Resistor: Simple linear resistor
     device         rresistor22_2         rresistor22_1 r.xoperational_amplif
      model                     R                     R                     R
 resistance                   2.2                    39                100000
         ac                   2.2                    39                100000
      dtemp                     0                     0                     0
     bv_max                 1e+99                 1e+99                 1e+99
      noisy                     1                     1                     1
          i             0.0404728           0.000483676               0.00018
          p             0.0036037           9.12378e-06               0.00324

 Resistor: Simple linear resistor
     device r.xoperational_amplif r.xoperational_amplif r.xoperational_amplif
      model                     R                     R                     R
 resistance                   0.2                 1e+06                 1e+06
         ac                   0.2                 1e+06                 1e+06
      dtemp                     0                     0                     0
     bv_max                 1e+99                 1e+99                 1e+99
      noisy                     1                     1                     1
          i             0.0351284           1.06385e-12           6.32626e-16
          p             0.0002468           1.13177e-18           4.00216e-25

 VCVS: Voltage controlled voltage source
     device e.xoperational_amplif
          i           1.06448e-12
          v                     9
          p           9.58032e-12

 Vsource: Independent voltage source
     device               vvcc_18             vaudio_in
         dc                    18                     0
      acmag                     0                     0
      pulse         -                     0
                                       0.02
                                       1000
        sin         -                     0
                                       0.02
                                       1000
        exp         -                     0
                                       0.02
                                       1000
        pwl         -                     0
                                       0.02
                                       1000
       sffm         -                     0
                                       0.02
                                       1000
         am         -                     0
                                       0.02
                                       1000
    trnoise         -                     0
                                       0.02
                                       1000
   trrandom         -                     0
                                       0.02
                                       1000
    portnum                     0                     0
         z0                     0                     0
        pwr                     0                     0
       freq                     0                     0
      phase                     0                     0
          i              -0.00018          -7.10543e-15
          p              -0.00324           6.96131e-31


Total analysis time (seconds) = 0.0365843

Total elapsed time (seconds) = 0.080 

Total DRAM available = 32239.535 MB.
DRAM currently available = 14623.043 MB.
Maximum ngspice program size =   15.664 MB.
Current ngspice program size =   15.664 MB.


```

### ngspice_stderr

- Step: `08`
- Role: Raw ngspice stderr log.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\c03\08_ngspice_stderr.txt`

```text

```

### tran_csv

- Step: `08`
- Role: Clean transient CSV, when .tran data is available.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\c03\08_tran.csv`

```csv
time,v(N001),v(N002),v(N003),v(N004),v(N005),v(N006),v(N007),v(N008),v(N009)
0.0,18.0,9.0,9.0,8.99190737,0.0,0.0890287859,9.0,0.0,0.0
1e-07,18.0,9.00001257,9.00001256,8.99211957,1.25663698e-05,0.0890413488,9.00019988,0.000212180114,0.000106090057
1.13006156e-07,18.0,9.0000142,9.0000142,8.99214734,1.42007712e-05,0.0890429827,9.00022585,0.000239952277,0.000118455688
1.39018469e-07,18.0,9.00001747,9.00001747,8.99220325,1.74695738e-05,0.0890462505,9.00027771,0.000295850385,0.000140653633
1.91043093e-07,18.0,9.00002401,9.000024,8.99231716,2.40071774e-05,0.089052786,9.00038107,0.000409752242,0.000172973755
2.95092343e-07,18.0,9.00003708,9.00003708,8.99255337,3.70823762e-05,0.0890658561,9.00058628,0.000645929819,0.000209941242
5.03190842e-07,18.0,9.00006323,9.00006322,8.99305889,6.32327207e-05,0.0890919926,9.00099078,0.00115135417,0.000243531062
8.53170452e-07,18.0,9.00010721,9.00010719,8.99400636,0.000107212048,0.0891359383,9.00165362,0.00209858824,0.000278050526
1.55312967e-06,18.0,9.00019517,9.00019512,8.99625129,0.000195168933,0.0892237899,9.00291653,0.00434274211,0.000344256544
2.95304812e-06,18.0,9.00037107,9.00037096,9.00202659,0.000371069678,0.0893993408,9.00521173,0.0101149397,0.000463373462
5.752885e-06,18.0,9.00072277,9.0007225,9.01792812,0.000722771435,0.0897498713,9.00902046,0.0260022651,0.00065762564
1.10766711e-05,18.0,9.00139081,9.00139009,9.05989979,0.00139081212,0.0904144122,9.01414596,0.0679072768,0.000907252588
1.87684675e-05,18.0,9.00235305,9.00235152,9.13730645,0.00235305254,0.0913697746,9.01849066,0.145101432,0.00109504591
2.87684675e-05,18.0,9.00359549,9.00359276,9.25203136,0.00359549788,0.0926017369,9.02145207,0.259309414,0.00118726926
3.87684675e-05,18.0,9.00482374,9.00481974,9.37252672,0.00482375343,0.0938188596,9.02311059,0.378994928,0.00120606511
4.87684675e-05,18.0,9.00603296,9.00602767,9.49378793,0.00603297183,0.0950168294,9.02427137,0.499146445,0.00119714365
5.87684675e-05,18.0,9.00721836,9.00721181,9.61382504,0.00721838085,0.0961910816,9.0252007,0.617775538,0.00117586382
6.87684675e-05,18.0,9.00837527,9.00836748,9.73165994,0.00837530222,0.0973370361,9.02598529,0.733909218,0.00114737946
7.87684675e-05,18.0,9.00949913,9.00949012,9.84665926,0.00949917009,0.0984501882,9.02665222,0.846921191,0.00111353684
8.87684675e-05,18.0,9.0105855,9.0105753,9.95831294,0.0105855491,0.0995261507,9.0272089,0.956309895,0.00107500782
9.87684675e-05,18.0,9.01163009,9.01161874,10.0661616,0.0116301517,0.100560679,9.02765652,1.06162559,0.00103216292
0.000108768467,18.0,9.01262878,9.01261632,10.1697733,0.0126288555,0.101549691,9.02799443,1.16244712,0.000985206959
0.000118768467,18.0,9.01357763,9.0135641,10.2687371,0.013577719,0.102489285,9.02822166,1.25837529,0.000934373025
0.000128768467,18.0,9.0144729,9.01445836,10.3626617,0.0144729973,0.103375751,9.02833745,1.34903158,0.000879843376
0.000138768467,18.0,9.01531104,9.01529554,10.4511763,0.0153111574,0.104205593,9.02834138,1.43405877,0.000821860171
0.000148768467,18.0,9.01608876,9.01607236,10.5339314,0.0160888914,0.104975535,9.02823346,1.51312203,0.000760629602
0.000158768467,18.0,9.01680298,9.01678574,10.6106006,0.0168031298,0.105682539,9.02801412,1.58591011,0.000696416227
0.000168768467,18.0,9.01745089,9.01743288,10.6808812,0.017451054,0.106323817,9.02768422,1.65213655,0.00062945194
0.000178768467,18.0,9.01802993,9.01801121,10.744496,0.0180301068,0.106896837,9.02724508,1.71154082,0.000560021909
0.000188768467,18.0,9.0185378,9.01851847,10.801194,0.018538003,0.107399339,9.02669842,1.76388928,0.000488380162
0.000198768467,18.0,9.01897252,9.01895263,10.8507515,0.0189727382,0.107829342,9.02604641,1.80897617,0.00041482864
0.000208768467,18.0,9.01933236,9.01931201,10.892973,0.0193325967,0.108185147,9.02529161,1.84662437,0.000339639126
0.000218768467,18.0,9.0196159,9.01959516,10.9276919,0.0196161582,0.108465352,9.02443701,1.87668611,0.000263126021
0.000228768467,18.0,9.01982203,9.01980099,10.9547712,0.0198223037,0.108668852,9.02348598,1.89904357,0.000185574165
0.000238768467,18.0,9.01994992,9.01992867,10.9741042,0.0199502197,0.108794843,9.02244227,1.9136093,0.00010730587
0.000248768467,18.0,9.01999909,9.0199777,10.9856147,0.0199994012,0.10884283,9.02131,1.92032661,2.86141674e-05
0.000258768467,18.0,9.01996932,9.0199479,10.9892571,0.0199696543,0.108812622,9.02009364,1.91916976,-5.0175421e-05
0.000268768467,18.0,9.01986074,9.01983937,10.9850171,0.0198610962,0.108704339,9.01879798,1.91014407,-0.000128766624
0.000278768467,18.0,9.01967378,9.01965255,10.9729116,0.0196741555,0.108518408,9.01742814,1.89328589,-0.000206835488
0.000288768467,18.0,9.01940917,9.01938817,10.9529881,0.0194095699,0.108255564,9.01598951,1.86866249,-0.00028408749
0.000298768467,18.0,9.01906797,9.01904728,10.9253255,0.0190683835,0.107916842,9.01448778,1.83637175,-0.000360204994
0.000308768467,18.0,9.01865151,9.01863122,10.8900327,0.018651943,0.107503579,9.01292887,1.7965418,-0.000434900153
0.000318768467,18.0,9.01816144,9.01814163,10.847249,0.0181618918,0.107017406,9.01131893,1.7493305,-0.00050786637
0.000328768467,18.0,9.01759969,9.01758044,10.7971433,0.0176001639,0.10646024,9.0096643,1.69492486,-0.000578827252
0.000338768467,18.0,9.01696849,9.01694987,10.7399131,0.0169689761,0.10583428,9.00797153,1.63354024,-0.000647491799
0.000348768467,18.0,9.01627032,9.01625241,10.6757843,0.0162708196,0.105141996,9.00624729,1.56541956,-0.000713599668
0.000358768467,18.0,9.01550793,9.0154908,10.6050099,0.0155084496,0.104386118,9.00449837,1.49083231,-0.000776879797
0.000368768467,18.0,9.01468434,9.01466806,10.5278692,0.0146848748,0.10356963,9.00273169,1.4100735,-0.000837092246
0.000378768467,18.0,9.0138028,9.01378742,10.4446664,0.0138033455,0.102695752,9.00095422,1.32346249,-0.000893989926
0.000388768467,18.0,9.01286678,9.01285237,10.35573,0.0128673408,0.101767934,8.99917297,1.23134176,-0.0009473573
0.000398768467,18.0,9.01187998,9.0118666,10.2614108,0.0118805545,0.100789836,8.99739497,1.13407553,-0.000996974967
0.000408768467,18.0,9.0108463,9.01083398,10.1620811,0.0108468811,0.0997653175,8.99562724,1.03204833,-0.0010426554
0.000418768467,18.0,9.0097698,9.00975861,10.0581327,0.00977039997,0.0986984227,8.99387676,0.925663498,-0.00108421016
0.000428768467,18.0,9.00865475,9.00864471,9.94997604,0.00865535957,0.0975933615,8.99215044,0.815341573,-0.00112148289
0.000438768467,18.0,9.00750555,9.0074967,9.83803781,0.00750616043,0.0964544951,8.99045509,0.701518646,-0.00115431894
0.000448768467,18.0,9.00632672,9.00631909,9.72275982,0.00632733789,0.0952863182,8.98879741,0.584644634,-0.00118259576
0.000458768467,18.0,9.00512292,9.00511655,9.60459703,0.00512354425,0.0940934413,8.98718393,0.465181508,-0.00120619478
0.000468768467,18.0,9.0038989,9.0038938,9.48401581,0.00389953031,0.0928805726,8.98562104,0.343601466,-0.00122502938
0.000478768467,18.0,9.00265949,9.00265569,9.36149207,0.00266012672,0.0916524992,8.9841149,0.220385068,-0.00123901879
0.000488768467,18.0,9.00140959,9.00140709,9.23750942,0.00141022481,0.0904140682,8.98267145,0.0960193405,-0.00124811385
0.000498768467,18.0,9.00015412,9.00015293,9.11255719,0.000154757396,0.0891701679,8.9812964,-0.0290041476,-0.00125227274
0.000508768467,18.0,8.99889804,8.99889817,8.9871286,-0.00110132078,0.0879257079,8.97999516,-0.154191229,-0.00125148465
0.000518768467,18.0,8.99764631,8.99764776,8.86171871,-0.00235305254,0.0866856002,8.97877289,-0.279047088,-0.00124574727
0.000528768467,18.0,8.99640387,8.99640663,8.73682252,-0.00359549788,0.0854547396,8.9776344,-0.403078217,-0.00123508848
0.000538768467,18.0,8.99517562,8.99517968,8.61293301,-0.00482375343,0.0842379845,8.97658419,-0.525794365,-0.00121954534
0.000548768467,18.0,8.99396641,8.99397176,8.49053917,-0.00603297183,0.0830401374,8.9756264,-0.646710475,-0.0011991841
0.000558768467,18.0,8.992781,8.99278763,8.3701241,-0.00721838085,0.0818659261,8.97476481,-0.765348603,-0.00117408052
0.000568768467,18.0,8.99162409,8.99163196,8.25216308,-0.00837530222,0.0807199853,8.97400283,-0.8812398,-0.00114433826
0.000578768467,18.0,8.99050023,8.99050932,8.13712168,-0.00949917009,0.0796068378,8.97334345,-0.99392597,-0.0011100705
0.000588768467,18.0,8.98941386,8.98942414,8.02545395,-0.0105855491,0.0785308769,8.97278927,-1.10296168,-0.00107141674
0.000598768467,18.0,8.98836927,8.9883807,7.91760063,-0.0116301517,0.0774963491,8.9723425,-1.20791591,-0.00102852568
0.000608768467,18.0,8.98737058,8.98738312,7.81398736,-0.0126288555,0.0765073371,8.97200487,-1.30837377,-0.00098157058
0.000618768467,18.0,8.98642173,8.98643533,7.71502305,-0.013577719,0.075567744,8.97177774,-1.40393812,-0.000930733185
0.000628768467,18.0,8.98552646,8.98554108,7.62109827,-0.0144729973,0.0746812778,8.97166198,-1.49423115,-0.000876217835
0.000638768467,18.0,8.98468832,8.9847039,7.53258366,-0.0153111574,0.0738514365,8.97165805,-1.57889588,-0.000818236399
0.000648768467,18.0,8.9839106,8.98392708,7.44982851,-0.0160888914,0.0730814945,8.97176598,-1.65759754,-0.000757021106
0.000658768467,18.0,8.98319638,8.9832137,7.37315936,-0.0168031298,0.0723744901,8.97198532,-1.73002491,-0.000692810508
0.000668768467,18.0,8.98254847,8.98256656,7.30287874,-0.017451054,0.0717332127,8.97231522,-1.79589155,-0.000625861136
0.000678768467,18.0,8.98196944,8.98198823,7.23926394,-0.0180301068,0.0711601924,8.97275436,-1.8549369,-0.000556434386
0.000688768467,18.0,8.98146156,8.98148097,7.18256596,-0.018538003,0.0706576901,8.97330102,-1.90692734,-0.000484807082
0.000698768467,18.0,8.98102684,8.98104681,7.13300848,-0.0189727382,0.0702276881,8.97395303,-1.95165711,-0.000411259253
0.000708768467,18.0,8.980667,8.98068743,7.09078701,-0.0193325967,0.0698718827,8.97470783,-1.98894908,-0.000336083716
0.000718768467,18.0,8.98038346,8.98040428,7.05606812,-0.0196161582,0.0695916775,8.97556243,-2.01865549,-0.000259574677
0.000728768467,18.0,8.98017734,8.98019845,7.02898875,-0.0198223037,0.0693881778,8.97651346,-2.04065851,-0.000182036382
0.000738768467,18.0,8.98004944,8.98007077,7.00965573,-0.0199502197,0.0692621862,8.97755717,-2.05487069,-0.000103772478
0.000748768467,18.0,8.98000028,8.98002174,6.99814531,-0.0199994012,0.0692141997,8.97868943,-2.06123533,-2.50939398e-05
0.000758768467,18.0,8.98003005,8.98005154,6.99450289,-0.0199696543,0.0692444073,8.9799058,-2.05972669,5.36909549e-05
0.000768768467,18.0,8.98013862,8.98016007,6.99874282,-0.0198610962,0.06935269,8.98120146,-2.0503501,0.000132269363
0.000778768467,18.0,8.98032558,8.98034689,7.01084836,-0.0196741555,0.0695386202,8.9825713,-2.0331419,0.000210333269
0.000788768467,18.0,8.98059019,8.98061127,7.03077176,-0.0194095699,0.0698014646,8.98400992,-2.00816936,0.000287572817
0.000798768467,18.0,8.98093139,8.98095216,7.0584344,-0.0190683835,0.0701401862,8.98551165,-1.97553035,0.00036368512
0.000808768467,18.0,8.98134785,8.98136822,7.09372715,-0.018651943,0.0705534486,8.98707056,-1.935353,0.000438368158
0.000818768467,18.0,8.98183792,8.98185781,7.13651078,-0.0181618918,0.0710396214,8.98868051,-1.88779519,0.000511328951
0.000828768467,18.0,8.98239967,8.982419,7.1866165,-0.0176001639,0.0715967867,8.99033513,-1.83304389,0.000582278025
0.000838768467,18.0,8.98303087,8.98304957,7.24384662,-0.0169689761,0.0722227461,8.9920279,-1.77131448,0.000650936945
0.000848768467,18.0,8.98372905,8.98374703,7.30797536,-0.0162708196,0.0729150302,8.99375214,-1.70284987,0.000717033293
0.000858768467,18.0,8.98449143,8.98450863,7.37874971,-0.0155084496,0.0736709074,8.99550106,-1.62791955,0.000780307637
0.000868768467,18.0,8.98531502,8.98533138,7.45589042,-0.0146848748,0.0744873954,8.99726773,-1.54681853,0.000840508825
0.000878768467,18.0,8.98619657,8.98621201,7.53909311,-0.0138033455,0.0753612726,8.99904521,-1.45986617,0.000897400553
0.000888768467,18.0,8.98713258,8.98714706,7.62802949,-0.0128673408,0.0762890905,9.00082646,-1.36740494,0.000950756935
0.000898768467,18.0,8.98811938,8.98813284,7.72234863,-0.0118805545,0.0772671882,9.00260446,-1.26979905,0.0010003685
0.000908768467,18.0,8.98915307,8.98916545,7.82167832,-0.0108468811,0.0782917057,9.00437218,-1.16743305,0.00104603818
0.000918768467,18.0,8.99022956,8.99024083,7.9256266,-0.00977039997,0.0793586001,
```

> Artifact truncated in this preview. The original file remains available through the manifest path.
