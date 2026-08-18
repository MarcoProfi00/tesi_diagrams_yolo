# Agent input preview

This file is a local preview of the evidence that will be provided to the read-only diagnostic agent.
The agent remains read-only: it can inspect base outputs and existing scenario artifacts, but it does not modify files.

## User problem

Lo scenario 1 attiva entrambi i rami: lampada circa 100 mA, LED circa 25 mA, corrente totale circa 125 mA sotto il fusibile da 500 mA. Fornisci la conclusione finale: causa isolata, correzione combinata verificata e chiarisci che il partial outcome dipende da N004 assente nella base run con switch aperto. Non proporre altri scenari.

## Circuit

- Batch: `batchChatAgentEvaluation`
- Circuit: `a09`
- Agent mode: `graph_grounded_readonly`

## Technical summary

```json
{
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_message": "ngspice completed successfully.",
  "emitted_elements": 6,
  "skipped_elements": 6,
  "emit_warnings_count": 1,
  "skipped_components_count": 6,
  "node_count": 8,
  "ground_groups_count": 5,
  "singleton_nodes_count": 0,
  "bound_components": 7,
  "missing_components": 0,
  "unsupported_components": 0,
  "spice_ready_components": 7,
  "rules_missing_components": 0,
  "has_tran_csv": false,
  "has_tran_plot": false,
  "led_profiles": {}
}
```

## Image policy

- Included by default: `False`
- Can be requested: `True`
- Path: `outputs\demo_workspaces\chat_agent_evaluation\input\images\a09.png`
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
      "title": "Alimentare entrambi i rami dal nodo BAT_FUSED e chiudere SW2",
      "status": "spice_success",
      "spice_status": "success",
      "outcome_status": "partially_resolved",
      "outcome_label": "Criteri verificati solo in parte",
      "outcome_technical_label": "Partially resolved",
      "outcome_reason": "Almeno una misura necessaria ai criteri di successo non e disponibile negli output SPICE dello scenario.",
      "stop_automation": false,
      "comparison_summary": {
        "requested_count": 5,
        "changed_count": 4,
        "activated_count": 3,
        "missing_count": 1,
        "expected_count": 4,
        "expectations_met_count": 3,
        "expectations_failed_count": 0,
        "expectations_missing_count": 1,
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
          "v(N003)",
          "v(N005)",
          "v(N007)",
          "i(Rlamp13_1)"
        ],
        "unchanged": [],
        "missing": [
          "v(N004)"
        ]
      },
      "led_profiles": {},
      "ranking_verified": true,
      "score": 45
    }
  ]
}
```


## Executed scenarios

### scenario_1

- Title: `Alimentare entrambi i rami dal nodo BAT_FUSED e chiudere SW2`
- Status: `spice_success`
- SPICE status: `success`
- Outcome: `partially_resolved`
- Stop automation: `False`
- Comparison: `4/5` changed
- LED profiles: `{}`

#### scenario_definition

- Role: Scenario selected by the user and saved before execution.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a09\scenarios\scenario_1\scenario.json`

```json
{
  "scenario_id": "scenario_1",
  "title": "Alimentare entrambi i rami dal nodo BAT_FUSED e chiudere SW2",
  "hypothesis": "The powered node N003 is not reaching the lamp-input node N004 nor the LED-input node N005, and the lamp branch is also blocked by open switch25.1.",
  "intent": "diagnostic",
  "actions": [
    {
      "type": "feed_nodes_from_source_node",
      "source_node": "N003",
      "target_nodes": [
        "N004",
        "N005"
      ],
      "resistance": "1m"
    },
    {
      "type": "close_switch",
      "target": "switch25.1"
    }
  ],
  "rerun_from": "07",
  "analysis": "op",
  "compare": [
    "v(N003)",
    "v(N004)",
    "v(N005)",
    "v(N007)",
    "i(Rlamp13_1)"
  ],
  "expect": {
    "v(N004)": "changed",
    "v(N005)": "changed",
    "v(N007)": "changed",
    "i(Rlamp13_1)": "nonzero"
  }
}
```

#### scenario_status

- Role: Current scenario status, SPICE status and diagnostic outcome.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a09\scenarios\scenario_1\scenario_status.json`

```json
{
  "status": "spice_success",
  "stage": "scenario_spice_executed",
  "scenario_id": "scenario_1",
  "source": "guided_chat",
  "spice_executed": true,
  "created_or_updated_at": "2026-07-24T10:49:46",
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a09\\scenarios\\scenario_1\\run\\08_spice_run.json",
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a09\\scenarios\\scenario_1\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 5,
    "changed_count": 4,
    "activated_count": 3,
    "missing_count": 1,
    "expected_count": 4,
    "expectations_met_count": 3,
    "expectations_failed_count": 0,
    "expectations_missing_count": 1,
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
    "technical_label": "Partially resolved",
    "label": "Criteri verificati solo in parte",
    "reason": "Almeno una misura necessaria ai criteri di successo non e disponibile negli output SPICE dello scenario.",
    "user_message": "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato.",
    "stop_automation": false,
    "confidence": "low",
    "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
  },
  "controlled_scenario_report": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a09\\scenarios\\scenario_1\\12_controlled_scenarios.json",
  "executed_scenarios_count": 1,
  "scenario_budget_exhausted": false,
  "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
}
```

#### controlled_scenario_report

- Role: Report produced by the controlled scenario runner.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a09\scenarios\scenario_1\12_controlled_scenarios.json`

```json
{
  "source_format": "pipeline2.0_controlled_scenario_report",
  "status": "spice_success",
  "scenario_id": "scenario_1",
  "scenario_title": "Alimentare entrambi i rami dal nodo BAT_FUSED e chiudere SW2",
  "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a09\\scenarios\\scenario_1",
  "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a09\\scenarios\\scenario_1\\run",
  "netlist": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a09\\scenarios\\scenario_1\\run\\07_netlist.cir",
  "applied_actions": [
    {
      "status": "applied",
      "type": "feed_nodes_from_source_node",
      "source_node": "N003",
      "target_nodes": [
        "N004",
        "N005"
      ],
      "resistance": "1m",
      "inserted_lines": [
        "RSCENARIO_FEED_N003_N004 N003 N004 1m",
        "RSCENARIO_FEED_N003_N005 N003 N005 1m"
      ],
      "expanded_connections": [
        {
          "from": "N003",
          "to": "N004",
          "resistance": "1m",
          "inserted_line": "RSCENARIO_FEED_N003_N004 N003 N004 1m",
          "operation": "inserted"
        },
        {
          "from": "N003",
          "to": "N005",
          "resistance": "1m",
          "inserted_line": "RSCENARIO_FEED_N003_N005 N003 N005 1m",
          "operation": "inserted"
        }
      ],
      "operation": "inserted_or_updated",
      "spice_executed": false,
      "index": 1
    },
    {
      "status": "applied",
      "type": "close_switch",
      "target": "switch25.1",
      "nodes": [
        "N004",
        "N006"
      ],
      "resistance": "1m",
      "inserted_line": "RSCENARIO_switch25_1 N004 N006 1m",
      "operation": "inserted",
      "spice_executed": false,
      "index": 2
    }
  ],
  "unsupported_actions": [],
  "failed_actions": [],
  "spice_executed": true,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a09\\scenarios\\scenario_1\\run\\08_spice_run.json",
  "spice_status": "success",
  "spice_exit_code": 0,
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a09\\scenarios\\scenario_1\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 5,
    "changed_count": 4,
    "activated_count": 3,
    "missing_count": 1,
    "expected_count": 4,
    "expectations_met_count": 3,
    "expectations_failed_count": 0,
    "expectations_missing_count": 1,
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
    "technical_label": "Partially resolved",
    "label": "Criteri verificati solo in parte",
    "reason": "Almeno una misura necessaria ai criteri di successo non e disponibile negli output SPICE dello scenario.",
    "user_message": "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato.",
    "stop_automation": false,
    "confidence": "low",
    "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
  },
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "created_or_updated_at": "2026-07-24T10:49:46"
}
```

#### scenario_comparison

- Role: Base-vs-scenario comparison used to evaluate the scenario.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a09\scenarios\scenario_1\scenario_comparison.json`

```json
{
  "source_format": "pipeline2.0_scenario_comparison",
  "scenario_id": "scenario_1",
  "scenario_title": "Alimentare entrambi i rami dal nodo BAT_FUSED e chiudere SW2",
  "scenario_intent": "diagnostic",
  "base_output_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a09",
  "scenario_run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a09\\scenarios\\scenario_1\\run",
  "base_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a09\\08_ngspice_stdout.txt",
  "scenario_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a09\\scenarios\\scenario_1\\run\\08_ngspice_stdout.txt",
  "base_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a09\\08_ngspice_stderr.txt",
  "scenario_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a09\\scenarios\\scenario_1\\run\\08_ngspice_stderr.txt",
  "quantities": [
    {
      "quantity": "v(N003)",
      "base_value": 9.0,
      "scenario_value": 8.999875,
      "delta": -0.00012500000000059686,
      "change": "changed",
      "expectation": null,
      "expectation_met": null,
      "relative_change": 1.3888888888955205e-05,
      "meaningful_improvement": false,
      "metric": "v(n003)",
      "measurement": "op",
      "base_details": {},
      "scenario_details": {}
    },
    {
      "quantity": "v(N004)",
      "base_value": null,
      "scenario_value": 8.999775,
      "delta": null,
      "change": "missing",
      "expectation": "changed",
      "expectation_met": null,
      "relative_change": null,
      "meaningful_improvement": false,
      "metric": "v(n004)",
      "measurement": "op",
      "base_details": {},
      "scenario_details": {}
    },
    {
      "quantity": "v(N005)",
      "base_value": 1.552748e-176,
      "scenario_value": 8.99985,
      "delta": 8.99985,
      "change": "activated",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 8999850000000.0,
      "meaningful_improvement": false,
      "metric": "v(n005)",
      "measurement": "op",
      "base_details": {},
      "scenario_details": {}
    },
    {
      "quantity": "v(N007)",
      "base_value": 1.552748e-176,
      "scenario_value": 0.7384097,
      "delta": 0.7384097,
      "change": "activated",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 738409700000.0,
      "meaningful_improvement": false,
      "metric": "v(n007)",
      "measurement": "op",
      "base_details": {},
      "scenario_details": {}
    },
    {
      "quantity": "i(Rlamp13_1)",
      "base_value": 0.0,
      "scenario_value": 0.0999964,
      "delta": 0.0999964,
      "change": "activated",
      "expectation": "nonzero",
      "expectation_met": true,
      "relative_change": 99996400000.0,
      "meaningful_improvement": true,
      "metric": "i(rlamp13_1)",
      "measurement": "op",
      "base_details": {},
      "scenario_details": {}
    }
  ],
  "summary": {
    "requested_count": 5,
    "changed_count": 4,
    "activated_count": 3,
    "missing_count": 1,
    "expected_count": 4,
    "expectations_met_count": 3,
    "expectations_failed_count": 0,
    "expectations_missing_count": 1,
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
    "technical_label": "Partially resolved",
    "label": "Criteri verificati solo in parte",
    "reason": "Almeno una misura necessaria ai criteri di successo non e disponibile negli output SPICE dello scenario.",
    "user_message": "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato.",
    "stop_automation": false,
    "confidence": "low",
    "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
  },
  "created_or_updated_at": "2026-07-24T10:49:46"
}
```


## Loaded artifacts

### graph

- Step: `01`
- Role: Graph JSON copied from Pipeline 1.0.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a09\01_graph.json`

```json
{
  "image_id": "a09",
  "image_name": "a09.png",
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
      "component_id": "fuse8.1",
      "instance_id": "8.1",
      "class_name": "Fuse",
      "terminals": [
        {
          "terminal_id": "fuse8.1_t1",
          "name": "t1",
          "relative_position": "left"
        },
        {
          "terminal_id": "fuse8.1_t2",
          "name": "t2",
          "relative_position": "right"
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
      "component_id": "connector5.1",
      "instance_id": "5.1",
      "class_name": "Connector",
      "terminals": [
        {
          "terminal_id": "connector5.1_pin1",
          "name": "pin1",
          "relative_position": "left"
        },
        {
          "terminal_id": "connector5.1_pin2",
          "name": "pin2",
          "relative_position": "right"
        },
        {
          "terminal_id": "connector5.1_pin3",
          "name": "pin3",
          "relative_position": "right"
        },
        {
          "terminal_id": "connector5.1_pin4",
          "name": "pin4",
          "relative_position": "right"
        },
        {
          "terminal_id": "connector5.1_pin5",
          "name": "pin5",
          "relative_position": "left"
        }
      ]
    },
    {
      "component_id": "capacitor4.1",
      "instance_id": "4.1",
      "class_name": "Capacitor",
      "terminals": [
        {
          "terminal_id": "capacitor4.1_t1",
          "name": "t1",
          "relative_position": "top"
        },
        {
          "terminal_id": "capacitor4.1_t2",
          "name": "t2",
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
      "component_id": "lamp13.1",
      "instance_id": "13.1",
      "class_name": "Lamp",
      "terminals": [
        {
          "terminal_id": "lamp13.1_t1",
          "name": "t1",
          "relative_position": "top"
        },
        {
          "terminal_id": "lamp13.1_t2",
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
    }
  ],
  "terminal_metadata": {},
  "graph": {
    "battery2.1_negative": [
      "gnd9.1_t1"
    ],
    "battery2.1_positive": [
      "fuse8.1_t1"
    ],
    "capacitor4.1_t1": [
      "connector5.1_pin2"
    ],
    "capacitor4.1_t2": [
      "gnd9.3_t1"
    ],
    "connector5.1_pin1": [
      "fuse8.1_t2"
    ],
    "connector5.1_pin2": [
      "capacitor4.1_t1"
    ],
    "connector5.1_pin3": [
      "switch25.1_t1"
    ],
    "connector5.1_pin4": [
      "resistor22.1_t1"
    ],
    "connector5.1_pin5": [
      "gnd9.2_t1"
    ],
    "fuse8.1_t1": [
      "battery2.1_positive"
    ],
    "fuse8.1_t2": [
      "connector5.1_pin1"
    ],
    "gnd9.1_t1": [
      "battery2.1_negative"
    ],
    "gnd9.2_t1": [
      "connector5.1_pin5"
    ],
    "gnd9.3_t1": [
      "capacitor4.1_t2"
    ],
    "gnd9.4_t1": [
      "led12.1_cathode"
    ],
    "gnd9.5_t1": [
      "lamp13.1_t2"
    ],
    "lamp13.1_t1": [
      "switch25.1_t2"
    ],
    "lamp13.1_t2": [
      "gnd9.5_t1"
    ],
    "led12.1_anode": [
      "resistor22.1_t2"
    ],
    "led12.1_cathode": [
      "gnd9.4_t1"
    ],
    "resistor22.1_t1": [
      "connector5.1_pin4"
    ],
    "resistor22.1_t2": [
      "led12.1_anode"
    ],
    "switch25.1_t1": [
      "connector5.1_pin3"
    ],
    "switch25.1_t2": [
      "lamp13.1_t1"
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
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a09\03_node_map.json`

```json
{
  "circuit_id": "a09",
  "source_format": "pipeline2.0_node_map",
  "nodes": [
    {
      "node_id": "0",
      "kind": "ground",
      "terminals": [
        "battery2.1_negative",
        "capacitor4.1_t2",
        "connector5.1_pin5",
        "gnd9.1_t1",
        "gnd9.2_t1",
        "gnd9.3_t1",
        "gnd9.4_t1",
        "gnd9.5_t1",
        "lamp13.1_t2",
        "led12.1_cathode"
      ],
      "terminal_count": 10,
      "source_groups": [
        [
          "battery2.1_negative",
          "gnd9.1_t1"
        ],
        [
          "capacitor4.1_t2",
          "gnd9.3_t1"
        ],
        [
          "connector5.1_pin5",
          "gnd9.2_t1"
        ],
        [
          "gnd9.4_t1",
          "led12.1_cathode"
        ],
        [
          "gnd9.5_t1",
          "lamp13.1_t2"
        ]
      ]
    },
    {
      "node_id": "N001",
      "kind": "normal",
      "terminals": [
        "battery2.1_positive",
        "fuse8.1_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N002",
      "kind": "normal",
      "terminals": [
        "capacitor4.1_t1",
        "connector5.1_pin2"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N003",
      "kind": "normal",
      "terminals": [
        "connector5.1_pin1",
        "fuse8.1_t2"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N004",
      "kind": "normal",
      "terminals": [
        "connector5.1_pin3",
        "switch25.1_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N005",
      "kind": "normal",
      "terminals": [
        "connector5.1_pin4",
        "resistor22.1_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N006",
      "kind": "normal",
      "terminals": [
        "lamp13.1_t1",
        "switch25.1_t2"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N007",
      "kind": "normal",
      "terminals": [
        "led12.1_anode",
        "resistor22.1_t2"
      ],
      "terminal_count": 2
    }
  ],
  "terminal_to_node": {
    "battery2.1_negative": "0",
    "battery2.1_positive": "N001",
    "capacitor4.1_t1": "N002",
    "capacitor4.1_t2": "0",
    "connector5.1_pin1": "N003",
    "connector5.1_pin2": "N002",
    "connector5.1_pin3": "N004",
    "connector5.1_pin4": "N005",
    "connector5.1_pin5": "0",
    "fuse8.1_t1": "N001",
    "fuse8.1_t2": "N003",
    "gnd9.1_t1": "0",
    "gnd9.2_t1": "0",
    "gnd9.3_t1": "0",
    "gnd9.4_t1": "0",
    "gnd9.5_t1": "0",
    "lamp13.1_t1": "N006",
    "lamp13.1_t2": "0",
    "led12.1_anode": "N007",
    "led12.1_cathode": "0",
    "resistor22.1_t1": "N005",
    "resistor22.1_t2": "N007",
    "switch25.1_t1": "N004",
    "switch25.1_t2": "N006"
  },
  "component_terminal_nodes": {
    "battery2.1": {
      "positive": "N001",
      "negative": "0"
    },
    "capacitor4.1": {
      "t1": "N002",
      "t2": "0"
    },
    "connector5.1": {
      "pin1": "N003",
      "pin2": "N002",
      "pin3": "N004",
      "pin4": "N005",
      "pin5": "0"
    },
    "fuse8.1": {
      "t1": "N001",
      "t2": "N003"
    },
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
    "lamp13.1": {
      "t1": "N006",
      "t2": "0"
    },
    "led12.1": {
      "anode": "N007",
      "cathode": "0"
    },
    "resistor22.1": {
      "t1": "N005",
      "t2": "N007"
    },
    "switch25.1": {
      "t1": "N004",
      "t2": "N006"
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
    "nodes_count": 8,
    "normal_nodes_count": 7,
    "ground_nodes_count": 1,
    "ground_groups_count": 5,
    "terminal_to_node_count": 24,
    "singleton_nodes_count": 0
  }
}
```

### values_bound

- Step: `04`
- Role: Values and labels bound to graph components.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a09\04_values_bound.json`

```json
{
  "circuit_id": "a09",
  "source_format": "pipeline2.0_values_bound",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\data\\batchPipeline2.0\\batchChatAgentEvaluation\\values\\a09_values.yaml",
  "supplies": {},
  "components": {
    "battery2.1": {
      "class_name": "Battery",
      "terminal_nodes": {
        "positive": "N001",
        "negative": "0"
      },
      "value_data": {
        "type": "dc",
        "value": 9,
        "unit": "V",
        "source": "manual_from_image_label",
        "label_text": "BAT2 9 V DC"
      },
      "status": "bound"
    },
    "capacitor4.1": {
      "class_name": "Capacitor",
      "terminal_nodes": {
        "t1": "N002",
        "t2": "0"
      },
      "value_data": {
        "value": 100,
        "unit": "nF",
        "source": "manual_from_image_label",
        "label_text": "C1 100 nF"
      },
      "status": "bound"
    },
    "connector5.1": {
      "class_name": "Connector",
      "terminal_nodes": {
        "pin1": "N003",
        "pin2": "N002",
        "pin3": "N004",
        "pin4": "N005",
        "pin5": "0"
      },
      "value_data": null,
      "status": "not_required"
    },
    "fuse8.1": {
      "class_name": "Fuse",
      "terminal_nodes": {
        "t1": "N001",
        "t2": "N003"
      },
      "value_data": {
        "state": "closed",
        "current_rating": 500,
        "current_unit": "mA",
        "source": "manual_from_image_label",
        "label_text": "F1 500 mA"
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
    "lamp13.1": {
      "class_name": "Lamp",
      "terminal_nodes": {
        "t1": "N006",
        "t2": "0"
      },
      "value_data": {
        "equivalent_resistance": 90,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "90 ohm",
        "spice": "resistive_load"
      },
      "status": "bound"
    },
    "led12.1": {
      "class_name": "LED",
      "terminal_nodes": {
        "anode": "N007",
        "cathode": "0"
      },
      "value_data": {
        "model": "LED_RED",
        "source": "manual_assumption"
      },
      "status": "bound"
    },
    "resistor22.1": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N005",
        "t2": "N007"
      },
      "value_data": {
        "value": 330,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R3 330R"
      },
      "status": "bound"
    },
    "switch25.1": {
      "class_name": "Switch",
      "terminal_nodes": {
        "t1": "N004",
        "t2": "N006"
      },
      "value_data": {
        "state": "open",
        "state_source": "graph_json_state",
        "state_confidence": 0.95,
        "source": "graph_json_state",
        "label_text": "SW2"
      },
      "status": "bound"
    }
  },
  "nodes": {
    "connector5.1_pin1": {
      "label": "BAT_FUSED",
      "source": "inferred_from_fuse_output",
      "node": "N003"
    },
    "connector5.1_pin2": {
      "label": "C1_TOP",
      "source": "inferred_from_capacitor_branch",
      "node": "N002"
    },
    "connector5.1_pin3": {
      "label": "SW2_INPUT",
      "source": "inferred_from_switch_branch",
      "node": "N004"
    },
    "connector5.1_pin4": {
      "label": "PWR_LED_INPUT",
      "source": "inferred_from_resistor_led_branch",
      "node": "N005"
    },
    "connector5.1_pin5": {
      "label": "GND",
      "spice_node": 0,
      "source": "graph_json_gnd",
      "node": "0"
    }
  },
  "spice_topology_overlay": [],
  "simulation": {},
  "missing": [],
  "stats": {
    "components_total": 13,
    "bound_components": 7,
    "missing_components": 0,
    "not_required_components": 6,
    "unsupported_components": 0,
    "supplies_count": 0,
    "manual_nodes_count": 5
  }
}
```

### component_rules

- Step: `06`
- Role: SPICE conversion rules for each component.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a09\06_component_rules.json`

```json
{
  "circuit_id": "a09",
  "source_format": "pipeline2.0_component_rules",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\data\\batchPipeline2.0\\batchChatAgentEvaluation\\values\\a09_values.yaml",
  "spice_classes_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_spice_classes.yaml",
  "supplies": {},
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
        "N001",
        "0"
      ],
      "parameters": {
        "type": "dc",
        "value": 9,
        "unit": "V",
        "source": "manual_from_image_label",
        "label_text": "BAT2 9 V DC"
      }
    },
    "capacitor4.1": {
      "class_name": "Capacitor",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "C",
      "emit_as": "capacitor",
      "node_order": [
        "t1",
        "t2"
      ],
      "nodes": [
        "N002",
        "0"
      ],
      "parameters": {
        "value": 100,
        "unit": "nF",
        "source": "manual_from_image_label",
        "label_text": "C1 100 nF"
      }
    },
    "connector5.1": {
      "class_name": "Connector",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "Connector used for nodes, labels, and external interfaces."
    },
    "fuse8.1": {
      "class_name": "Fuse",
      "status": "spice_ready",
      "spice_support": "simplified",
      "spice_prefix": null,
      "emit_as": null,
      "node_order": [
        "t1",
        "t2"
      ],
      "nodes": [
        "N001",
        "N003"
      ],
      "parameters": {
        "state": "closed",
        "current_rating": 500,
        "current_unit": "mA",
        "source": "manual_from_image_label",
        "label_text": "F1 500 mA"
      },
      "strategy": "short_circuit"
    },
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
    "lamp13.1": {
      "class_name": "Lamp",
      "status": "spice_ready",
      "spice_support": "equivalent",
      "spice_prefix": "R",
      "emit_as": "resistive_load",
      "node_order": [
        "t1",
        "t2"
      ],
      "nodes": [
        "N006",
        "0"
      ],
      "parameters": {
        "equivalent_resistance": 90,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "90 ohm",
        "spice": "resistive_load"
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
        "N007",
        "0"
      ],
      "parameters": {
        "model": "LED_RED",
        "source": "manual_assumption"
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
        "N005",
        "N007"
      ],
      "parameters": {
        "value": 330,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R3 330R"
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
        "N006"
      ],
      "parameters": {
        "state": "open",
        "state_source": "graph_json_state",
        "state_confidence": 0.95,
        "source": "graph_json_state",
        "label_text": "SW2"
      },
      "strategy": "open_circuit"
    }
  },
  "simulation": {},
  "stats": {
    "components_total": 13,
    "spice_ready_components": 7,
    "not_emitted_components": 6,
    "measurement_components": 0,
    "missing_components": 0,
    "unsupported_components": 0,
    "pin_aware_components": 0,
    "invalid_components": 0,
    "supplies_ready_count": 0
  }
}
```

### netlist

- Step: `07`
- Role: Generated SPICE netlist.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a09\07_netlist.cir`

```spice
* pipeline2.0 netlist
* circuit: a09

Vbattery2_1 N001 0 DC 9
Ccapacitor4_1 N002 0 100n
Rfuse8_1 N001 N003 1m
Rlamp13_1 N006 0 90
Dled12_1 N007 0 LED_RED
Rresistor22_1 N005 N007 330
* switch25.1 open: not emitted

.model LED_RED D

.op
.end

```

### spice_emit_report

- Step: `07`
- Role: Report of emitted, skipped and warning components.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a09\07_spice_emit_report.json`

```json
{
  "circuit_id": "a09",
  "source_format": "pipeline2.0_spice_emit_report",
  "emitted_elements": 6,
  "skipped_elements": 6,
  "skipped_components": [
    "connector5.1",
    "gnd9.1",
    "gnd9.2",
    "gnd9.3",
    "gnd9.4",
    "gnd9.5"
  ],
  "informational_skips": [
    "connector5.1: structural component not emitted",
    "gnd9.1: structural component not emitted",
    "gnd9.2: structural component not emitted",
    "gnd9.3: structural component not emitted",
    "gnd9.4: structural component not emitted",
    "gnd9.5: structural component not emitted"
  ],
  "measurement_points": [],
  "analyses": [
    "op"
  ],
  "transient_export": {
    "path": null,
    "nodes": [],
    "device_currents": []
  },
  "models": [
    "LED_RED"
  ],
  "warnings": [
    "switch25.1: open switch not emitted"
  ]
}
```

### spice_run

- Step: `08`
- Role: Structured ngspice execution report.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a09\08_spice_run.json`

```json
{
  "source_format": "pipeline2.0_spice_run",
  "status": "success",
  "netlist_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\a09\\07_netlist.cir",
  "command": [
    "C:\\Users\\m.profilo\\Spice64\\bin\\ngspice_con.exe",
    "-b",
    "07_netlist.cir"
  ],
  "exit_code": 0,
  "stdout_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\a09\\08_ngspice_stdout.txt",
  "stderr_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\a09\\08_ngspice_stderr.txt",
  "tran_raw_csv_path": null,
  "tran_csv_path": null,
  "tran_plot_path": null,
  "tran_plot_png_path": null,
  "tran_plot_svg_path": null,
  "message": "ngspice completed successfully."
}
```

### ngspice_stdout

- Step: `08`
- Role: Raw ngspice stdout log.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a09\08_ngspice_stdout.txt`

```text

Note: No compatibility mode selected!


Circuit: * pipeline2.0 netlist

Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver
 Reference value :  0.00000e+00

No. of Data Rows : 1
	Node                                  Voltage
	----                                  -------
	----	-------
	n005                            1.552748e-176
	n007                            1.552748e-176
	n006                             0.000000e+00
	n003                             9.000000e+00
	n002                             0.000000e+00
	n001                             9.000000e+00

	Source	Current
	------	-------

	vbattery2_1#branch               -9.09495e-12

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
      model               led_red

      level                     1
         is                 1e-14
        jsw                     0
         rs                     0
        rsw                     0
        trs                     0
       trs2                     0
          n                     1
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
        nbv                     1
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

 Capacitor: Fixed capacitor
     device         ccapacitor4_1
      model                     C
capacitance                 1e-07
      dtemp                     0
     bv_max                 1e+99
          i                     0
          p                     0

 Diode: Junction Diode model
     device              dled12_1
      model               led_red
    thermal                     0
         vd          1.55275e-176
         id          1.55275e-188
         gd           1.38662e-12
         cd                     0

 Resistor: Simple linear resistor
     device         rresistor22_1             rlamp13_1              rfuse8_1
      model                     R                     R                     R
 resistance                   330                    90                 0.001
         ac                   330                    90                 0.001
      dtemp                     0                     0                     0
     bv_max                 1e+99                 1e+99                 1e+99
      noisy                     1                     1                     1
          i         -1.55275e-188                     0           1.06581e-11
          p                     0                     0           1.13596e-25

 Vsource: Independent voltage source
     device           vbattery2_1
         dc                     9
      acmag                     0
      pulse         -
        sin         -
        exp         -
        pwl         -
       sffm         -
         am         -
    trnoise         -
   trrandom         -
    portnum                     0
         z0                     0
        pwr                     0
       freq                     0
      phase                     0
          i          -9.09495e-12
          p          -8.18545e-11


Total analysis time (seconds) = 0.0146735

Total elapsed time (seconds) = 0.356 

Total DRAM available = 32239.535 MB.
DRAM currently available = 14253.973 MB.
Maximum ngspice program size =   15.016 MB.
Current ngspice program size =   15.016 MB.


```

### ngspice_stderr

- Step: `08`
- Role: Raw ngspice stderr log.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a09\08_ngspice_stderr.txt`

```text
Warning: singular matrix:  check node n002

Note: Starting dynamic gmin stepping
Warning: singular matrix:  check node n002

Warning: Dynamic gmin stepping failed
Note: Starting true gmin stepping
Warning: singular matrix:  check node n002

Warning: singular matrix:  check node n002

Warning: singular matrix:  check node n002

Warning: singular matrix:  check node n002

Warning: True gmin stepping failed
Note: Starting source stepping
Warning: source stepping failed
Note: Transient op started
Note: Transient op finished successfully

```

### tran_csv

Artifact not available.
