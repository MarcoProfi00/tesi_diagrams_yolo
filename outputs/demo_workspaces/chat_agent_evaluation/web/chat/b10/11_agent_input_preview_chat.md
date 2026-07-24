# Agent input preview

This file is a local preview of the evidence that will be provided to the read-only diagnostic agent.
The agent remains read-only: it can inspect base outputs and existing scenario artifacts, but it does not modify files.

## User problem

Concludi esperimento.

## Circuit

- Batch: `batchChatAgentEvaluation`
- Circuit: `b10`
- Agent mode: `graph_grounded_readonly`

## Technical summary

```json
{
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_message": "ngspice completed successfully.",
  "emitted_elements": 13,
  "skipped_elements": 5,
  "emit_warnings_count": 1,
  "skipped_components_count": 5,
  "node_count": 6,
  "ground_groups_count": 1,
  "singleton_nodes_count": 0,
  "bound_components": 12,
  "missing_components": 0,
  "unsupported_components": 0,
  "spice_ready_components": 12,
  "rules_missing_components": 0,
  "has_tran_csv": true,
  "has_tran_plot": true,
  "led_profiles": {}
}
```

## Image policy

- Included by default: `False`
- Can be requested: `True`
- Path: `outputs\demo_workspaces\chat_agent_evaluation\input\images\b10.jpg`
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
      "title": "Chiudere lo switch riconosciuto",
      "status": "spice_success",
      "spice_status": "success",
      "outcome_status": "partially_resolved",
      "outcome_label": "Ipotesi diagnostica confermata",
      "outcome_technical_label": "Diagnostic hypothesis confirmed",
      "outcome_reason": "I criteri dichiarati dal test diagnostico sono soddisfatti, ma lo scenario non applica una correzione del sintomo utente.",
      "stop_automation": false,
      "comparison_summary": {
        "requested_count": 3,
        "changed_count": 2,
        "activated_count": 0,
        "missing_count": 0,
        "expected_count": 1,
        "expectations_met_count": 1,
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
          "v(N005)"
        ],
        "unchanged": [
          "v(N004)"
        ],
        "missing": []
      },
      "led_profiles": {},
      "ranking_verified": true,
      "score": 25
    }
  ]
}
```


## Executed scenarios

### scenario_1

- Title: `Chiudere lo switch riconosciuto`
- Status: `spice_success`
- SPICE status: `success`
- Outcome: `partially_resolved`
- Stop automation: `False`
- Comparison: `2/3` changed
- LED profiles: `{}`

#### scenario_definition

- Role: Scenario selected by the user and saved before execution.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b10\scenarios\scenario_1\scenario.json`

```json
{
  "scenario_id": "scenario_1",
  "title": "Chiudere lo switch riconosciuto",
  "hypothesis": "switch25.1 aperto isola il ramo che potrebbe trasferire il livello di A verso B.",
  "intent": "diagnostic",
  "actions": [
    {
      "type": "close_switch",
      "target": "switch25.1"
    }
  ],
  "rerun_from": "06",
  "analysis": "op",
  "compare": [
    "v(N002)",
    "v(N004)",
    "v(N005)"
  ],
  "expect": {
    "v(N002)": "changed"
  }
}
```

#### scenario_status

- Role: Current scenario status, SPICE status and diagnostic outcome.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b10\scenarios\scenario_1\scenario_status.json`

```json
{
  "status": "spice_success",
  "stage": "scenario_spice_executed",
  "scenario_id": "scenario_1",
  "source": "guided_chat",
  "spice_executed": true,
  "created_or_updated_at": "2026-07-24T17:16:54",
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b10\\scenarios\\scenario_1\\run\\08_spice_run.json",
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b10\\scenarios\\scenario_1\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 3,
    "changed_count": 2,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 1,
    "expectations_met_count": 1,
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
  "controlled_scenario_report": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b10\\scenarios\\scenario_1\\12_controlled_scenarios.json",
  "executed_scenarios_count": 1,
  "scenario_budget_exhausted": false,
  "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
}
```

#### controlled_scenario_report

- Role: Report produced by the controlled scenario runner.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b10\scenarios\scenario_1\12_controlled_scenarios.json`

```json
{
  "source_format": "pipeline2.0_controlled_scenario_report",
  "status": "spice_success",
  "scenario_id": "scenario_1",
  "scenario_title": "Chiudere lo switch riconosciuto",
  "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b10\\scenarios\\scenario_1",
  "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b10\\scenarios\\scenario_1\\run",
  "netlist": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b10\\scenarios\\scenario_1\\run\\07_netlist.cir",
  "applied_actions": [
    {
      "status": "applied",
      "type": "close_switch",
      "target": "switch25.1",
      "nodes": [
        "N004",
        "N005"
      ],
      "resistance": "1m",
      "inserted_line": "RSCENARIO_switch25_1 N004 N005 1m",
      "operation": "inserted",
      "spice_executed": false,
      "index": 1
    }
  ],
  "unsupported_actions": [],
  "failed_actions": [],
  "spice_executed": true,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b10\\scenarios\\scenario_1\\run\\08_spice_run.json",
  "spice_status": "success",
  "spice_exit_code": 0,
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b10\\scenarios\\scenario_1\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 3,
    "changed_count": 2,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 1,
    "expectations_met_count": 1,
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
  "created_or_updated_at": "2026-07-24T17:16:54"
}
```

#### scenario_comparison

- Role: Base-vs-scenario comparison used to evaluate the scenario.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b10\scenarios\scenario_1\scenario_comparison.json`

```json
{
  "source_format": "pipeline2.0_scenario_comparison",
  "scenario_id": "scenario_1",
  "scenario_title": "Chiudere lo switch riconosciuto",
  "scenario_intent": "diagnostic",
  "base_output_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b10",
  "scenario_run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b10\\scenarios\\scenario_1\\run",
  "base_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b10\\08_ngspice_stdout.txt",
  "scenario_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b10\\scenarios\\scenario_1\\run\\08_ngspice_stdout.txt",
  "base_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b10\\08_ngspice_stderr.txt",
  "scenario_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b10\\scenarios\\scenario_1\\run\\08_ngspice_stderr.txt",
  "quantities": [
    {
      "quantity": "v(N002)",
      "base_value": 0.001,
      "scenario_value": 0.999,
      "delta": 0.998,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 998.0,
      "meaningful_improvement": false,
      "metric": "v(n002)",
      "measurement": "op",
      "base_details": {},
      "scenario_details": {}
    },
    {
      "quantity": "v(N004)",
      "base_value": 1.0,
      "scenario_value": 1.0,
      "delta": 0.0,
      "change": "unchanged",
      "expectation": null,
      "expectation_met": null,
      "relative_change": 0.0,
      "meaningful_improvement": false,
      "metric": "v(n004)",
      "measurement": "op",
      "base_details": {},
      "scenario_details": {}
    },
    {
      "quantity": "v(N005)",
      "base_value": 0.002,
      "scenario_value": 1.0,
      "delta": 0.998,
      "change": "changed",
      "expectation": null,
      "expectation_met": null,
      "relative_change": 499.0,
      "meaningful_improvement": false,
      "metric": "v(n005)",
      "measurement": "op",
      "base_details": {},
      "scenario_details": {}
    }
  ],
  "summary": {
    "requested_count": 3,
    "changed_count": 2,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 1,
    "expectations_met_count": 1,
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
  "created_or_updated_at": "2026-07-24T17:16:54"
}
```


## Loaded artifacts

### graph

- Step: `01`
- Role: Graph JSON copied from Pipeline 1.0.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b10\01_graph.json`

```json
{
  "image_id": "b10",
  "image_name": "b10.jpg",
  "components": [
    {
      "component_id": "terminal26.1",
      "instance_id": "26.1",
      "class_name": "Terminal",
      "terminals": [
        {
          "terminal_id": "terminal26.1_t1",
          "name": "t1",
          "relative_position": "right"
        }
      ]
    },
    {
      "component_id": "current_source6.1",
      "instance_id": "6.1",
      "class_name": "Current_Source",
      "terminals": [
        {
          "terminal_id": "current_source6.1_current_from",
          "name": "current_from",
          "relative_position": "top"
        },
        {
          "terminal_id": "current_source6.1_current_to",
          "name": "current_to",
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
          "relative_position": "top"
        },
        {
          "terminal_id": "polarized_capacitor20.1_negative",
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
          "relative_position": "left"
        },
        {
          "terminal_id": "resistor22.1_t2",
          "name": "t2",
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
      "component_id": "terminal26.3",
      "instance_id": "26.3",
      "class_name": "Terminal",
      "terminals": [
        {
          "terminal_id": "terminal26.3_t1",
          "name": "t1",
          "relative_position": "top"
        }
      ]
    },
    {
      "component_id": "switch25.1",
      "instance_id": "25.1",
      "class_name": "Switch",
      "terminals": [
        {
          "terminal_id": "switch25.1_t1",
          "name": "t1",
          "relative_position": "left"
        },
        {
          "terminal_id": "switch25.1_t2",
          "name": "t2",
          "relative_position": "right"
        }
      ],
      "state": "open",
      "state_confidence": 0.95
    },
    {
      "component_id": "current_source6.2",
      "instance_id": "6.2",
      "class_name": "Current_Source",
      "terminals": [
        {
          "terminal_id": "current_source6.2_current_from",
          "name": "current_from",
          "relative_position": "left"
        },
        {
          "terminal_id": "current_source6.2_current_to",
          "name": "current_to",
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
      "component_id": "polarized_capacitor20.3",
      "instance_id": "20.3",
      "class_name": "Polarized_Capacitor",
      "terminals": [
        {
          "terminal_id": "polarized_capacitor20.3_positive",
          "name": "positive",
          "relative_position": "left"
        },
        {
          "terminal_id": "polarized_capacitor20.3_negative",
          "name": "negative",
          "relative_position": "right"
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
          "relative_position": "left"
        },
        {
          "terminal_id": "polarized_capacitor20.4_negative",
          "name": "negative",
          "relative_position": "right"
        }
      ]
    },
    {
      "component_id": "voltage_source31.1",
      "instance_id": "31.1",
      "class_name": "Voltage_Source",
      "terminals": [
        {
          "terminal_id": "voltage_source31.1_positive",
          "name": "positive",
          "relative_position": "left"
        },
        {
          "terminal_id": "voltage_source31.1_negative",
          "name": "negative",
          "relative_position": "right"
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
      "component_id": "current_source6.3",
      "instance_id": "6.3",
      "class_name": "Current_Source",
      "terminals": [
        {
          "terminal_id": "current_source6.3_current_from",
          "name": "current_from",
          "relative_position": "top"
        },
        {
          "terminal_id": "current_source6.3_current_to",
          "name": "current_to",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "terminal26.4",
      "instance_id": "26.4",
      "class_name": "Terminal",
      "terminals": [
        {
          "terminal_id": "terminal26.4_t1",
          "name": "t1",
          "relative_position": "left"
        }
      ]
    }
  ],
  "terminal_metadata": {},
  "graph": {
    "current_source6.1_current_from": [
      "current_source6.2_current_from",
      "polarized_capacitor20.1_positive",
      "polarized_capacitor20.2_positive",
      "polarized_capacitor20.3_positive",
      "resistor22.1_t1",
      "resistor22.2_t1",
      "terminal26.1_t1"
    ],
    "current_source6.1_current_to": [
      "current_source6.3_current_to",
      "gnd9.1_t1",
      "polarized_capacitor20.1_negative",
      "polarized_capacitor20.5_negative",
      "terminal26.2_t1"
    ],
    "current_source6.2_current_from": [
      "current_source6.1_current_from",
      "polarized_capacitor20.1_positive",
      "polarized_capacitor20.2_positive",
      "polarized_capacitor20.3_positive",
      "resistor22.1_t1",
      "resistor22.2_t1",
      "terminal26.1_t1"
    ],
    "current_source6.2_current_to": [
      "current_source6.3_current_from",
      "polarized_capacitor20.3_negative",
      "polarized_capacitor20.4_negative",
      "polarized_capacitor20.5_positive",
      "resistor22.2_t2",
      "terminal26.4_t1",
      "voltage_source31.1_negative"
    ],
    "current_source6.3_current_from": [
      "current_source6.2_current_to",
      "polarized_capacitor20.3_negative",
      "polarized_capacitor20.4_negative",
      "polarized_capacitor20.5_positive",
      "resistor22.2_t2",
      "terminal26.4_t1",
      "voltage_source31.1_negative"
    ],
    "current_source6.3_current_to": [
      "current_source6.1_current_to",
      "gnd9.1_t1",
      "polarized_capacitor20.1_negative",
      "polarized_capacitor20.5_negative",
      "terminal26.2_t1"
    ],
    "gnd9.1_t1": [
      "current_source6.1_current_to",
      "current_source6.3_current_to",
      "polarized_capacitor20.1_negative",
      "polarized_capacitor20.5_negative",
      "terminal26.2_t1"
    ],
    "polarized_capacitor20.1_negative": [
      "current_source6.1_current_to",
      "current_source6.3_current_to",
      "gnd9.1_t1",
      "polarized_capacitor20.5_negative",
      "terminal26.2_t1"
    ],
    "polarized_capacitor20.1_positive": [
      "current_source6.1_current_from",
      "current_source6.2_current_from",
      "polarized_capacitor20.2_positive",
      "polarized_capacitor20.3_positive",
      "resistor22.1_t1",
      "resistor22.2_t1",
      "terminal26.1_t1"
    ],
    "polarized_capacitor20.2_negative": [
      "polarized_capacitor20.4_positive",
      "terminal26.3_t1"
    ],
    "polarized_capacitor20.2_positive": [
      "current_source6.1_current_from",
      "current_source6.2_current_from",
      "polarized_capacitor20.1_positive",
      "polarized_capacitor20.3_positive",
      "resistor22.1_t1",
      "resistor22.2_t1",
      "terminal26.1_t1"
    ],
    "polarized_capacitor20.3_negative": [
      "current_source6.2_current_to",
      "current_source6.3_current_from",
      "polarized_capacitor20.4_negative",
      "polarized_capacitor20.5_positive",
      "resistor22.2_t2",
      "terminal26.4_t1",
      "voltage_source31.1_negative"
    ],
    "polarized_capacitor20.3_positive": [
      "current_source6.1_current_from",
      "current_source6.2_current_from",
      "polarized_capacitor20.1_positive",
      "polarized_capacitor20.2_positive",
      "resistor22.1_t1",
      "resistor22.2_t1",
      "terminal26.1_t1"
    ],
    "polarized_capacitor20.4_negative": [
      "current_source6.2_current_to",
      "current_source6.3_current_from",
      "polarized_capacitor20.3_negative",
      "polarized_capacitor20.5_positive",
      "resistor22.2_t2",
      "terminal26.4_t1",
      "voltage_source31.1_negative"
    ],
    "polarized_capacitor20.4_positive": [
      "polarized_capacitor20.2_negative",
      "terminal26.3_t1"
    ],
    "polarized_capacitor20.5_negative": [
      "current_source6.1_current_to",
      "current_source6.3_current_to",
      "gnd9.1_t1",
      "polarized_capacitor20.1_negative",
      "terminal26.2_t1"
    ],
    "polarized_capacitor20.5_positive": [
      "current_source6.2_current_to",
      "current_source6.3_current_from",
      "polarized_capacitor20.3_negative",
      "polarized_capacitor20.4_negative",
      "resistor22.2_t2",
      "terminal26.4_t1",
      "voltage_source31.1_negative"
    ],
    "resistor22.1_t1": [
      "current_source6.1_current_from",
      "current_source6.2_current_from",
      "polarized_capacitor20.1_positive",
      "polarized_capacitor20.2_positive",
      "polarized_capacitor20.3_positive",
      "resistor22.2_t1",
      "terminal26.1_t1"
    ],
    "resistor22.1_t2": [
      "switch25.1_t1"
    ],
    "resistor22.2_t1": [
      "current_source6.1_current_from",
      "current_source6.2_current_from",
      "polarized_capacitor20.1_positive",
      "polarized_capacitor20.2_positive",
      "polarized_capacitor20.3_positive",
      "resistor22.1_t1",
      "terminal26.1_t1"
    ],
    "resistor22.2_t2": [
      "current_source6.2_current_to",
      "current_source6.3_current_from",
      "polarized_capacitor20.3_negative",
      "polarized_capacitor20.4_negative",
      "polarized_capacitor20.5_positive",
      "terminal26.4_t1",
      "voltage_source31.1_negative"
    ],
    "switch25.1_t1": [
      "resistor22.1_t2"
    ],
    "switch25.1_t2": [
      "voltage_source31.1
```

> Artifact truncated in this preview. The original file remains available through the manifest path.

### node_map

- Step: `03`
- Role: Maps component terminals to SPICE node names.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b10\03_node_map.json`

```json
{
  "circuit_id": "b10",
  "source_format": "pipeline2.0_node_map",
  "nodes": [
    {
      "node_id": "0",
      "kind": "ground",
      "terminals": [
        "current_source6.1_current_to",
        "current_source6.3_current_to",
        "gnd9.1_t1",
        "polarized_capacitor20.1_negative",
        "polarized_capacitor20.5_negative",
        "terminal26.2_t1"
      ],
      "terminal_count": 6,
      "source_groups": [
        [
          "current_source6.1_current_to",
          "current_source6.3_current_to",
          "gnd9.1_t1",
          "polarized_capacitor20.1_negative",
          "polarized_capacitor20.5_negative",
          "terminal26.2_t1"
        ]
      ]
    },
    {
      "node_id": "N001",
      "kind": "normal",
      "terminals": [
        "current_source6.1_current_from",
        "current_source6.2_current_from",
        "polarized_capacitor20.1_positive",
        "polarized_capacitor20.2_positive",
        "polarized_capacitor20.3_positive",
        "resistor22.1_t1",
        "resistor22.2_t1",
        "terminal26.1_t1"
      ],
      "terminal_count": 8
    },
    {
      "node_id": "N002",
      "kind": "normal",
      "terminals": [
        "current_source6.2_current_to",
        "current_source6.3_current_from",
        "polarized_capacitor20.3_negative",
        "polarized_capacitor20.4_negative",
        "polarized_capacitor20.5_positive",
        "resistor22.2_t2",
        "terminal26.4_t1",
        "voltage_source31.1_negative"
      ],
      "terminal_count": 8
    },
    {
      "node_id": "N003",
      "kind": "normal",
      "terminals": [
        "polarized_capacitor20.2_negative",
        "polarized_capacitor20.4_positive",
        "terminal26.3_t1"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N004",
      "kind": "normal",
      "terminals": [
        "resistor22.1_t2",
        "switch25.1_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N005",
      "kind": "normal",
      "terminals": [
        "switch25.1_t2",
        "voltage_source31.1_positive"
      ],
      "terminal_count": 2
    }
  ],
  "terminal_to_node": {
    "current_source6.1_current_from": "N001",
    "current_source6.1_current_to": "0",
    "current_source6.2_current_from": "N001",
    "current_source6.2_current_to": "N002",
    "current_source6.3_current_from": "N002",
    "current_source6.3_current_to": "0",
    "gnd9.1_t1": "0",
    "polarized_capacitor20.1_negative": "0",
    "polarized_capacitor20.1_positive": "N001",
    "polarized_capacitor20.2_negative": "N003",
    "polarized_capacitor20.2_positive": "N001",
    "polarized_capacitor20.3_negative": "N002",
    "polarized_capacitor20.3_positive": "N001",
    "polarized_capacitor20.4_negative": "N002",
    "polarized_capacitor20.4_positive": "N003",
    "polarized_capacitor20.5_negative": "0",
    "polarized_capacitor20.5_positive": "N002",
    "resistor22.1_t1": "N001",
    "resistor22.1_t2": "N004",
    "resistor22.2_t1": "N001",
    "resistor22.2_t2": "N002",
    "switch25.1_t1": "N004",
    "switch25.1_t2": "N005",
    "terminal26.1_t1": "N001",
    "terminal26.2_t1": "0",
    "terminal26.3_t1": "N003",
    "terminal26.4_t1": "N002",
    "voltage_source31.1_negative": "N002",
    "voltage_source31.1_positive": "N005"
  },
  "component_terminal_nodes": {
    "current_source6.1": {
      "current_from": "N001",
      "current_to": "0"
    },
    "current_source6.2": {
      "current_from": "N001",
      "current_to": "N002"
    },
    "current_source6.3": {
      "current_from": "N002",
      "current_to": "0"
    },
    "gnd9.1": {
      "t1": "0"
    },
    "polarized_capacitor20.1": {
      "positive": "N001",
      "negative": "0"
    },
    "polarized_capacitor20.2": {
      "positive": "N001",
      "negative": "N003"
    },
    "polarized_capacitor20.3": {
      "positive": "N001",
      "negative": "N002"
    },
    "polarized_capacitor20.4": {
      "positive": "N003",
      "negative": "N002"
    },
    "polarized_capacitor20.5": {
      "positive": "N002",
      "negative": "0"
    },
    "resistor22.1": {
      "t1": "N001",
      "t2": "N004"
    },
    "resistor22.2": {
      "t1": "N001",
      "t2": "N002"
    },
    "switch25.1": {
      "t1": "N004",
      "t2": "N005"
    },
    "terminal26.1": {
      "t1": "N001"
    },
    "terminal26.2": {
      "t1": "0"
    },
    "terminal26.3": {
      "t1": "N003"
    },
    "terminal26.4": {
      "t1": "N002"
    },
    "voltage_source31.1": {
      "positive": "N005",
      "negative": "N002"
    }
  },
  "warnings": {
    "ground_groups_count": 1,
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
    "nodes_count": 6,
    "normal_nodes_count": 5,
    "ground_nodes_count": 1,
    "ground_groups_count": 1,
    "terminal_to_node_count": 29,
    "singleton_nodes_count": 0
  }
}
```

### values_bound

- Step: `04`
- Role: Values and labels bound to graph components.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b10\04_values_bound.json`

```json
{
  "circuit_id": "b10",
  "source_format": "pipeline2.0_values_bound",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\data\\batchPipeline2.0\\batchChatAgentEvaluation\\values\\b10_values.yaml",
  "supplies": {
    "VTEST_A": {
      "terminal": "terminal26.1_t1",
      "type": "dc",
      "value": 1,
      "unit": "V",
      "reference": 0,
      "source": "manual_assumption_symbolic_switch_test_bench",
      "label_text": "A di test: 1 V",
      "node": "N001"
    },
    "VTEST_C": {
      "terminal": "terminal26.3_t1",
      "type": "dc",
      "value": 0,
      "unit": "V",
      "reference": 0,
      "source": "manual_assumption_symbolic_switch_test_bench",
      "label_text": "C di test: 0 V",
      "node": "N003"
    }
  },
  "components": {
    "current_source6.1": {
      "class_name": "Current_Source",
      "terminal_nodes": {
        "current_from": "N001",
        "current_to": "0"
      },
      "value_data": {
        "type": "dc",
        "value": 0,
        "unit": "A",
        "source": "manual_assumption_symbolic_switch_test_bench",
        "label_text": "I_A assunto: 0 A"
      },
      "status": "bound"
    },
    "current_source6.2": {
      "class_name": "Current_Source",
      "terminal_nodes": {
        "current_from": "N001",
        "current_to": "N002"
      },
      "value_data": {
        "type": "dc",
        "value": 1e-12,
        "unit": "A",
        "source": "manual_assumption_symbolic_switch_model",
        "label_text": "I_OFF assunto: 1 pA"
      },
      "status": "bound"
    },
    "current_source6.3": {
      "class_name": "Current_Source",
      "terminal_nodes": {
        "current_from": "N002",
        "current_to": "0"
      },
      "value_data": {
        "type": "dc",
        "value": 1e-09,
        "unit": "A",
        "source": "manual_assumption_symbolic_switch_test_bench",
        "label_text": "I_B assunto: 1 nA"
      },
      "status": "bound"
    },
    "gnd9.1": {
      "class_name": "GND",
      "terminal_nodes": {
        "t1": "0"
      },
      "value_data": null,
      "status": "not_required"
    },
    "polarized_capacitor20.1": {
      "class_name": "Polarized_Capacitor",
      "terminal_nodes": {
        "positive": "N001",
        "negative": "0"
      },
      "value_data": {
        "value": 5,
        "unit": "pf",
        "source": "manual_assumption_symbolic_switch_model",
        "label_text": "capacita parassita assunta: 5 pF"
      },
      "status": "bound"
    },
    "polarized_capacitor20.2": {
      "class_name": "Polarized_Capacitor",
      "terminal_nodes": {
        "positive": "N001",
        "negative": "N003"
      },
      "value_data": {
        "value": 5,
        "unit": "pf",
        "source": "manual_assumption_symbolic_switch_model",
        "label_text": "capacita parassita assunta: 5 pF"
      },
      "status": "bound"
    },
    "polarized_capacitor20.3": {
      "class_name": "Polarized_Capacitor",
      "terminal_nodes": {
        "positive": "N001",
        "negative": "N002"
      },
      "value_data": {
        "value": 5,
        "unit": "pf",
        "source": "manual_assumption_symbolic_switch_model",
        "label_text": "capacita parassita assunta: 5 pF"
      },
      "status": "bound"
    },
    "polarized_capacitor20.4": {
      "class_name": "Polarized_Capacitor",
      "terminal_nodes": {
        "positive": "N003",
        "negative": "N002"
      },
      "value_data": {
        "value": 5,
        "unit": "pf",
        "source": "manual_assumption_symbolic_switch_model",
        "label_text": "capacita parassita assunta: 5 pF"
      },
      "status": "bound"
    },
    "polarized_capacitor20.5": {
      "class_name": "Polarized_Capacitor",
      "terminal_nodes": {
        "positive": "N002",
        "negative": "0"
      },
      "value_data": {
        "value": 5,
        "unit": "pf",
        "source": "manual_assumption_symbolic_switch_model",
        "label_text": "capacita parassita assunta: 5 pF"
      },
      "status": "bound"
    },
    "resistor22.1": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N001",
        "t2": "N004"
      },
      "value_data": {
        "value": 10,
        "unit": "ohm",
        "source": "manual_assumption_symbolic_switch_model",
        "label_text": "r_ON assunto: 10 ohm"
      },
      "status": "bound"
    },
    "resistor22.2": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N001",
        "t2": "N002"
      },
      "value_data": {
        "value": 1000,
        "unit": "Mohm",
        "source": "manual_assumption_symbolic_switch_model",
        "label_text": "r_OFF assunto: 1 Gohm"
      },
      "status": "bound"
    },
    "switch25.1": {
      "class_name": "Switch",
      "terminal_nodes": {
        "t1": "N004",
        "t2": "N005"
      },
      "value_data": {
        "state": "open",
        "state_source": "graph_json_state",
        "state_confidence": 0.95,
        "source": "graph_json_state_validated_from_image",
        "label_text": "switch aperto"
      },
      "status": "bound"
    },
    "terminal26.1": {
      "class_name": "Terminal",
      "terminal_nodes": {
        "t1": "N001"
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
        "t1": "N003"
      },
      "value_data": null,
      "status": "not_required"
    },
    "terminal26.4": {
      "class_name": "Terminal",
      "terminal_nodes": {
        "t1": "N002"
      },
      "value_data": null,
      "status": "not_required"
    },
    "voltage_source31.1": {
      "class_name": "Voltage_Source",
      "terminal_nodes": {
        "positive": "N005",
        "negative": "N002"
      },
      "value_data": {
        "type": "dc",
        "value": 0.001,
        "unit": "V",
        "source": "manual_assumption_symbolic_switch_model",
        "label_text": "V_OS assunto: 1 mV"
      },
      "status": "bound"
    }
  },
  "nodes": {},
  "spice_topology_overlay": [],
  "simulation": {
    "analyses": [
      "op",
      "tran"
    ],
    "tran": {
      "step": "1us",
      "stop": "100us"
    }
  },
  "missing": [],
  "stats": {
    "components_total": 17,
    "bound_components": 12,
    "missing_components": 0,
    "not_required_components": 5,
    "unsupported_components": 0,
    "supplies_count": 2,
    "manual_nodes_count": 0
  }
}
```

### component_rules

- Step: `06`
- Role: SPICE conversion rules for each component.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b10\06_component_rules.json`

```json
{
  "circuit_id": "b10",
  "source_format": "pipeline2.0_component_rules",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\data\\batchPipeline2.0\\batchChatAgentEvaluation\\values\\b10_values.yaml",
  "spice_classes_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_spice_classes.yaml",
  "supplies": {
    "VTEST_A": {
      "status": "spice_ready",
      "spice_prefix": "V",
      "emit_as": "independent_voltage_source",
      "nodes": [
        "N001",
        "0"
      ],
      "parameters": {
        "terminal": "terminal26.1_t1",
        "type": "dc",
        "value": 1,
        "unit": "V",
        "reference": 0,
        "source": "manual_assumption_symbolic_switch_test_bench",
        "label_text": "A di test: 1 V",
        "node": "N001"
      }
    },
    "VTEST_C": {
      "status": "spice_ready",
      "spice_prefix": "V",
      "emit_as": "independent_voltage_source",
      "nodes": [
        "N003",
        "0"
      ],
      "parameters": {
        "terminal": "terminal26.3_t1",
        "type": "dc",
        "value": 0,
        "unit": "V",
        "reference": 0,
        "source": "manual_assumption_symbolic_switch_test_bench",
        "label_text": "C di test: 0 V",
        "node": "N003"
      }
    }
  },
  "components": {
    "current_source6.1": {
      "class_name": "Current_Source",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "I",
      "emit_as": "independent_current_source",
      "node_order": [
        "current_from",
        "current_to"
      ],
      "nodes": [
        "N001",
        "0"
      ],
      "parameters": {
        "type": "dc",
        "value": 0,
        "unit": "A",
        "source": "manual_assumption_symbolic_switch_test_bench",
        "label_text": "I_A assunto: 0 A"
      }
    },
    "current_source6.2": {
      "class_name": "Current_Source",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "I",
      "emit_as": "independent_current_source",
      "node_order": [
        "current_from",
        "current_to"
      ],
      "nodes": [
        "N001",
        "N002"
      ],
      "parameters": {
        "type": "dc",
        "value": 1e-12,
        "unit": "A",
        "source": "manual_assumption_symbolic_switch_model",
        "label_text": "I_OFF assunto: 1 pA"
      }
    },
    "current_source6.3": {
      "class_name": "Current_Source",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "I",
      "emit_as": "independent_current_source",
      "node_order": [
        "current_from",
        "current_to"
      ],
      "nodes": [
        "N002",
        "0"
      ],
      "parameters": {
        "type": "dc",
        "value": 1e-09,
        "unit": "A",
        "source": "manual_assumption_symbolic_switch_test_bench",
        "label_text": "I_B assunto: 1 nA"
      }
    },
    "gnd9.1": {
      "class_name": "GND",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "GND terminals are already mapped to SPICE node 0."
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
        "N001",
        "0"
      ],
      "parameters": {
        "value": 5,
        "unit": "pf",
        "source": "manual_assumption_symbolic_switch_model",
        "label_text": "capacita parassita assunta: 5 pF"
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
        "N001",
        "N003"
      ],
      "parameters": {
        "value": 5,
        "unit": "pf",
        "source": "manual_assumption_symbolic_switch_model",
        "label_text": "capacita parassita assunta: 5 pF"
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
        "N002"
      ],
      "parameters": {
        "value": 5,
        "unit": "pf",
        "source": "manual_assumption_symbolic_switch_model",
        "label_text": "capacita parassita assunta: 5 pF"
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
        "N003",
        "N002"
      ],
      "parameters": {
        "value": 5,
        "unit": "pf",
        "source": "manual_assumption_symbolic_switch_model",
        "label_text": "capacita parassita assunta: 5 pF"
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
        "N002",
        "0"
      ],
      "parameters": {
        "value": 5,
        "unit": "pf",
        "source": "manual_assumption_symbolic_switch_model",
        "label_text": "capacita parassita assunta: 5 pF"
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
        "N001",
        "N004"
      ],
      "parameters": {
        "value": 10,
        "unit": "ohm",
        "source": "manual_assumption_symbolic_switch_model",
        "label_text": "r_ON assunto: 10 ohm"
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
        "N001",
        "N002"
      ],
      "parameters": {
        "value": 1000,
        "unit": "Mohm",
        "source": "manual_assumption_symbolic_switch_model",
        "label_text": "r_OFF assunto: 1 Gohm"
      }
    },
    "switch25.1": {
      "class_name": "Switch",
      "status": "spice_ready",
      "spice_support": "simplified",
      "spice_prefix": null,
      "emit_as": null,
      "node_order": [
        "t1",
        "t2"
      ],
      "nodes": [
        "N004",
        "N005"
      ],
      "parameters": {
        "state": "open",
        "state_source": "graph_json_state",
        "state_confidence": 0.95,
        "source": "graph_json_state_validated_from_image",
        "label_text": "switch aperto"
      },
      "strategy": "open_circuit"
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
    },
    "terminal26.4": {
      "class_name": "Terminal",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "External terminal/label; useful for nodes and interface handling."
    },
    "voltage_source31.1": {
      "class_name": "Voltage_Source",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "V",
      "emit_as": "independent_voltage_source",
      "node_order": [
        "positive",
        "negative"
      ],
      "nodes": [
        "N005",
        "N002"
      ],
      "parameters": {
        "type": "dc",
        "value": 0.001,
        "unit": "V",
        "source": "manual_assumption_symbolic_switch_model",
        "label_text": "V_OS assunto: 1 mV"
      }
    }
  },
  "simulation": {
    "analyses": [
      "op",
      "tran"
    ],
    "tran": {
      "step": "1us",
      "stop": "100us"
    }
  },
  "stats": {
    "components_total": 17,
    "spice_ready_components": 12,
    "not_emitted_components": 5,
    "measurement_components": 0,
    "missing_components": 0,
    "unsupported_components": 0,
    "pin_aware_components": 0,
    "invalid_components": 0,
    "supplies_ready_count": 2
  }
}
```

### netlist

- Step: `07`
- Role: Generated SPICE netlist.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b10\07_netlist.cir`

```spice
* pipeline2.0 netlist
* circuit: b10

VVTEST_A N001 0 DC 1
VVTEST_C N003 0 DC 0
Icurrent_source6_1 N001 0 DC 0
Icurrent_source6_2 N001 N002 DC 1e-12
Icurrent_source6_3 N002 0 DC 1e-09
Cpolarized_capacitor20_1 N001 0 5p
Cpolarized_capacitor20_2 N001 N003 5p
Cpolarized_capacitor20_3 N001 N002 5p
Cpolarized_capacitor20_4 N003 N002 5p
Cpolarized_capacitor20_5 N002 0 5p
Rresistor22_1 N001 N004 10
Rresistor22_2 N001 N002 1000meg
* switch25.1 open: not emitted
Vvoltage_source31_1 N005 N002 DC 0.001

.op
.save all
.tran 1us 100us

.control
set wr_singlescale
set wr_vecnames
run
wrdata 08_tran.csv time v(N001) v(N002) v(N003) v(N004) v(N005)
.endc
.end

```

### spice_emit_report

- Step: `07`
- Role: Report of emitted, skipped and warning components.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b10\07_spice_emit_report.json`

```json
{
  "circuit_id": "b10",
  "source_format": "pipeline2.0_spice_emit_report",
  "emitted_elements": 13,
  "skipped_elements": 5,
  "skipped_components": [
    "gnd9.1",
    "terminal26.1",
    "terminal26.2",
    "terminal26.3",
    "terminal26.4"
  ],
  "informational_skips": [
    "gnd9.1: structural component not emitted",
    "terminal26.1: structural component not emitted",
    "terminal26.2: structural component not emitted",
    "terminal26.3: structural component not emitted",
    "terminal26.4: structural component not emitted"
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
      "N005"
    ],
    "device_currents": []
  },
  "models": [],
  "warnings": [
    "switch25.1: open switch not emitted"
  ]
}
```

### spice_run

- Step: `08`
- Role: Structured ngspice execution report.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b10\08_spice_run.json`

```json
{
  "source_format": "pipeline2.0_spice_run",
  "status": "success",
  "netlist_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\b10\\07_netlist.cir",
  "command": [
    "C:\\Users\\m.profilo\\Spice64\\bin\\ngspice_con.exe",
    "-b",
    "07_netlist.cir"
  ],
  "exit_code": 0,
  "stdout_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\b10\\08_ngspice_stdout.txt",
  "stderr_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\b10\\08_ngspice_stderr.txt",
  "tran_raw_csv_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\b10\\08_tran_raw.csv",
  "tran_csv_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\b10\\08_tran.csv",
  "tran_plot_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\b10\\08_tran_plot.png",
  "tran_plot_png_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\b10\\08_tran_plot.png",
  "tran_plot_svg_path": null,
  "message": "ngspice completed successfully."
}
```

### ngspice_stdout

- Step: `08`
- Role: Raw ngspice stdout log.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b10\08_ngspice_stdout.txt`

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
n001                                         1
n003                                         0
n002                                     0.001
n004                                         1
n005                                     0.002
vvoltage_source31_1#branch                   0
vvtest_c#branch                              0
vvtest_a#branch                         -1e-09


No. of Data Rows : 108
Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

No. of Data Rows : 1

Initial Transient Solution
--------------------------

Node                                   Voltage
----                                   -------
n001                                         1
n003                                         0
n002                                     0.001
n004                                         1
n005                                     0.002
vvoltage_source31_1#branch                   0
vvtest_c#branch                              0
vvtest_a#branch                         -1e-09


No. of Data Rows : 108
	Node                                  Voltage
	----                                  -------
	----	-------
	n005                             2.000000e-03
	n004                             1.000000e+00
	n002                             1.000000e-03
	n003                             0.000000e+00
	n001                             1.000000e+00

	Source	Current
	------	-------

	vvtest_a#branch                  -1.00000e-09
	vvtest_c#branch                  0.000000e+00
	vvoltage_source31_1#branch       0.000000e+00

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

 Capacitor: Fixed capacitor
     device cpolarized_capacitor2 cpolarized_capacitor2 cpolarized_capacitor2
      model                     C                     C                     C
capacitance                 5e-12                 5e-12                 5e-12
      dtemp                     0                     0                     0
     bv_max                 1e+99                 1e+99                 1e+99
          i          -1.51854e-20           1.51854e-20          -3.02923e-20
          p          -1.51854e-23          -1.51854e-23           -3.0262e-20

 Capacitor: Fixed capacitor
     device cpolarized_capacitor2 cpolarized_capacitor2
      model                     C                     C
capacitance                 5e-12                 5e-12
      dtemp                     0                     0
     bv_max                 1e+99                 1e+99
          i                     0                     0
          p                     0                     0

 Isource: Independent current source
     device    icurrent_source6_3    icurrent_source6_2    icurrent_source6_1
         dc                 1e-09                 1e-12                     0
          m                     1                     1                     1
      acmag                     0                     0                     0
      pulse         -         -         -
        sin         -         -         -
        exp         -         -         -
        pwl         -         -         -
       sffm         -         -         -
         am         -         -         -
    trnoise         -         -         -
   trrandom         -         -         -
          v                -0.001                -0.999                    -1
          p                 1e-12              9.99e-13                     0
    current                 1e-09                 1e-12                     0

 Resistor: Simple linear resistor
     device         rresistor22_2         rresistor22_1
      model                     R                     R
 resistance                 1e+09                    10
         ac                 1e+09                    10
      dtemp                     0                     0
     bv_max                 1e+99                 1e+99
      noisy                     1                     1
          i              9.99e-10                     0
          p           9.98001e-10                     0

 Vsource: Independent voltage source
     device   vvoltage_source31_1              vvtest_c              vvtest_a
         dc                 0.001                     0                     1
      acmag                     0                     0                     0
      pulse         -         -         -
        sin         -         -         -
        exp         -         -         -
        pwl         -         -         -
       sffm         -         -         -
         am         -         -         -
    trnoise         -         -         -
   trrandom         -         -         -
    portnum                     0                     0                     0
         z0                     0                     0                     0
        pwr                     0                     0                     0
       freq                     0                     0                     0
      phase                     0                     0                     0
          i                     0          -1.60159e-20                -1e-09
          p                     0                    -0                -1e-09


Total analysis time (seconds) = 0.0065118

Total elapsed time (seconds) = 0.154 

Total DRAM available = 32239.535 MB.
DRAM currently available = 15724.207 MB.
Maximum ngspice program size =   15.059 MB.
Current ngspice program size =   15.059 MB.


```

### ngspice_stderr

- Step: `08`
- Role: Raw ngspice stderr log.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b10\08_ngspice_stderr.txt`

```text

```

### tran_csv

- Step: `08`
- Role: Clean transient CSV, when .tran data is available.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b10\08_tran.csv`

```csv
time,v(N001),v(N002),v(N003),v(N004),v(N005)
0.0,1.0,0.001,0.0,1.0,0.002
1e-08,1.0,0.001,0.0,1.0,0.002
2e-08,1.0,0.001,0.0,1.0,0.002
4e-08,1.0,0.001,0.0,1.0,0.002
8e-08,1.0,0.001,0.0,1.0,0.002
1.6e-07,1.0,0.001,0.0,1.0,0.002
3.2e-07,1.0,0.001,0.0,1.0,0.002
6.4e-07,1.0,0.001,0.0,1.0,0.002
1.28e-06,1.0,0.001,0.0,1.0,0.002
2.28e-06,1.0,0.001,0.0,1.0,0.002
3.28e-06,1.0,0.001,0.0,1.0,0.002
4.28e-06,1.0,0.001,0.0,1.0,0.002
5.28e-06,1.0,0.001,0.0,1.0,0.002
6.28e-06,1.0,0.001,0.0,1.0,0.002
7.28e-06,1.0,0.001,0.0,1.0,0.002
8.28e-06,1.0,0.001,0.0,1.0,0.002
9.28e-06,1.0,0.001,0.0,1.0,0.002
1.028e-05,1.0,0.001,0.0,1.0,0.002
1.128e-05,1.0,0.001,0.0,1.0,0.002
1.228e-05,1.0,0.001,0.0,1.0,0.002
1.328e-05,1.0,0.001,0.0,1.0,0.002
1.428e-05,1.0,0.001,0.0,1.0,0.002
1.528e-05,1.0,0.001,0.0,1.0,0.002
1.628e-05,1.0,0.001,0.0,1.0,0.002
1.728e-05,1.0,0.001,0.0,1.0,0.002
1.828e-05,1.0,0.001,0.0,1.0,0.002
1.928e-05,1.0,0.001,0.0,1.0,0.002
2.028e-05,1.0,0.001,0.0,1.0,0.002
2.128e-05,1.0,0.001,0.0,1.0,0.002
2.228e-05,1.0,0.001,0.0,1.0,0.002
2.328e-05,1.0,0.001,0.0,1.0,0.002
2.428e-05,1.0,0.001,0.0,1.0,0.002
2.528e-05,1.0,0.001,0.0,1.0,0.002
2.628e-05,1.0,0.001,0.0,1.0,0.002
2.728e-05,1.0,0.001,0.0,1.0,0.002
2.828e-05,1.0,0.001,0.0,1.0,0.002
2.928e-05,1.0,0.001,0.0,1.0,0.002
3.028e-05,1.0,0.001,0.0,1.0,0.002
3.128e-05,1.0,0.001,0.0,1.0,0.002
3.228e-05,1.0,0.001,0.0,1.0,0.002
3.328e-05,1.0,0.001,0.0,1.0,0.002
3.428e-05,1.0,0.001,0.0,1.0,0.002
3.528e-05,1.0,0.001,0.0,1.0,0.002
3.628e-05,1.0,0.001,0.0,1.0,0.002
3.728e-05,1.0,0.001,0.0,1.0,0.002
3.828e-05,1.0,0.001,0.0,1.0,0.002
3.928e-05,1.0,0.001,0.0,1.0,0.002
4.028e-05,1.0,0.001,0.0,1.0,0.002
4.128e-05,1.0,0.001,0.0,1.0,0.002
4.228e-05,1.0,0.001,0.0,1.0,0.002
4.328e-05,1.0,0.001,0.0,1.0,0.002
4.428e-05,1.0,0.001,0.0,1.0,0.002
4.528e-05,1.0,0.001,0.0,1.0,0.002
4.628e-05,1.0,0.001,0.0,1.0,0.002
4.728e-05,1.0,0.001,0.0,1.0,0.002
4.828e-05,1.0,0.001,0.0,1.0,0.002
4.928e-05,1.0,0.001,0.0,1.0,0.002
5.028e-05,1.0,0.001,0.0,1.0,0.002
5.128e-05,1.0,0.001,0.0,1.0,0.002
5.228e-05,1.0,0.001,0.0,1.0,0.002
5.328e-05,1.0,0.001,0.0,1.0,0.002
5.428e-05,1.0,0.001,0.0,1.0,0.002
5.528e-05,1.0,0.001,0.0,1.0,0.002
5.628e-05,1.0,0.001,0.0,1.0,0.002
5.728e-05,1.0,0.001,0.0,1.0,0.002
5.828e-05,1.0,0.001,0.0,1.0,0.002
5.928e-05,1.0,0.001,0.0,1.0,0.002
6.028e-05,1.0,0.001,0.0,1.0,0.002
6.128e-05,1.0,0.001,0.0,1.0,0.002
6.228e-05,1.0,0.001,0.0,1.0,0.002
6.328e-05,1.0,0.001,0.0,1.0,0.002
6.428e-05,1.0,0.001,0.0,1.0,0.002
6.528e-05,1.0,0.001,0.0,1.0,0.002
6.628e-05,1.0,0.001,0.0,1.0,0.002
6.728e-05,1.0,0.001,0.0,1.0,0.002
6.828e-05,1.0,0.001,0.0,1.0,0.002
6.928e-05,1.0,0.001,0.0,1.0,0.002
7.028e-05,1.0,0.001,0.0,1.0,0.002
7.128e-05,1.0,0.001,0.0,1.0,0.002
7.228e-05,1.0,0.001,0.0,1.0,0.002
7.328e-05,1.0,0.001,0.0,1.0,0.002
7.428e-05,1.0,0.001,0.0,1.0,0.002
7.528e-05,1.0,0.001,0.0,1.0,0.002
7.628e-05,1.0,0.001,0.0,1.0,0.002
7.728e-05,1.0,0.001,0.0,1.0,0.002
7.828e-05,1.0,0.001,0.0,1.0,0.002
7.928e-05,1.0,0.001,0.0,1.0,0.002
8.028e-05,1.0,0.001,0.0,1.0,0.002
8.128e-05,1.0,0.001,0.0,1.0,0.002
8.228e-05,1.0,0.001,0.0,1.0,0.002
8.328e-05,1.0,0.001,0.0,1.0,0.002
8.428e-05,1.0,0.001,0.0,1.0,0.002
8.528e-05,1.0,0.001,0.0,1.0,0.002
8.628e-05,1.0,0.001,0.0,1.0,0.002
8.728e-05,1.0,0.001,0.0,1.0,0.002
8.828e-05,1.0,0.001,0.0,1.0,0.002
8.928e-05,1.0,0.001,0.0,1.0,0.002
9.028e-05,1.0,0.001,0.0,1.0,0.002
9.128e-05,1.0,0.001,0.0,1.0,0.002
9.228e-05,1.0,0.001,0.0,1.0,0.002
9.328e-05,1.0,0.001,0.0,1.0,0.002
9.428e-05,1.0,0.001,0.0,1.0,0.002
9.528e-05,1.0,0.001,0.0,1.0,0.002
9.628e-05,1.0,0.001,0.0,1.0,0.002
9.728e-05,1.0,0.001,0.0,1.0,0.002
9.828e-05,1.0,0.001,0.0,1.0,0.002
9.914e-05,1.0,0.001,0.0,1.0,0.002
0.0001,1.0,0.001,0.0,1.0,0.002

```
