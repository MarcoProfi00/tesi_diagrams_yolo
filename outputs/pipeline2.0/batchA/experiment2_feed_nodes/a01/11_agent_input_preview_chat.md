# Agent input preview

This file is a local preview of the evidence that will be provided to the read-only diagnostic agent.
The agent remains read-only: it can inspect base outputs and existing scenario artifacts, but it does not modify files.

## User problem

Dato che scenario 4 replicherebbe quasi lo stesso effetto di scenario 2, alla luce della topologia estratta possiamo già concludere che lo switch non è il candidato principale? Se no, qual è l’unico scenario davvero informativo rimasto?

## Circuit

- Batch: `batchA`
- Circuit: `a01`
- Agent mode: `graph_grounded_readonly`

## Technical summary

```json
{
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_message": "ngspice completed successfully.",
  "emitted_elements": 5,
  "skipped_elements": 4,
  "emit_warnings_count": 1,
  "skipped_components_count": 4,
  "node_count": 6,
  "ground_groups_count": 3,
  "singleton_nodes_count": 0,
  "bound_components": 5,
  "missing_components": 0,
  "unsupported_components": 0,
  "spice_ready_components": 5,
  "rules_missing_components": 0,
  "has_tran_csv": false,
  "has_tran_plot": false
}
```

## Image policy

- Included by default: `False`
- Can be requested: `True`
- Path: `data\batchA\a01.png`
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
  "interpretation_rule": "If a user asks which scenario resolves the problem, prefer the scenario with outcome_status='resolved_candidate' and stop_automation=true. Partially resolved scenarios are supporting diagnostics, not the main solution.",
  "scenarios": [
    {
      "scenario_id": "scenario_2",
      "title": "Portare il +5 V esistente al ramo lampada",
      "status": "spice_success",
      "spice_status": "success",
      "outcome_status": "partially_resolved",
      "outcome_label": "Partially resolved",
      "outcome_reason": "The scenario changed the circuit response, but the evidence is not strong enough to stop automatically.",
      "stop_automation": false,
      "comparison_summary": {
        "requested_count": 4,
        "changed_count": 3,
        "activated_count": 3,
        "missing_count": 0
      },
      "quantity_summary": {
        "changed": [
          "v(N002)",
          "v(N004)",
          "i(Rlamp13_1)"
        ],
        "unchanged": [
          "v(N001)"
        ],
        "missing": []
      },
      "score": 23
    }
  ]
}
```


## Executed scenarios

### scenario_2

- Title: `Portare il +5 V esistente al ramo lampada`
- Status: `spice_success`
- SPICE status: `success`
- Outcome: `partially_resolved`
- Stop automation: `False`
- Comparison: `3/4` changed

#### scenario_definition

- Role: Scenario selected by the user and saved before execution.
- Path: `outputs\pipeline2.0\batchA\experiment2_feed_nodes\a01\scenarios\scenario_2\scenario.json`

```json
{
  "scenario_id": "scenario_2",
  "title": "Portare il +5 V esistente al ramo lampada",
  "hypothesis": "La lampada resta spenta perché il nodo alimentato N001 non raggiunge N002.",
  "actions": [
    {
      "type": "feed_nodes_from_source_node",
      "source_node": "N001",
      "target_nodes": [
        "N002"
      ],
      "resistance": "1m"
    }
  ],
  "rerun_from": "07",
  "analysis": "op",
  "compare": [
    "v(N001)",
    "v(N002)",
    "v(N004)",
    "i(Rlamp13_1)"
  ]
}
```

#### scenario_status

- Role: Current scenario status, SPICE status and diagnostic outcome.
- Path: `outputs\pipeline2.0\batchA\experiment2_feed_nodes\a01\scenarios\scenario_2\scenario_status.json`

```json
{
  "status": "spice_success",
  "stage": "scenario_spice_executed",
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "scenario_id": "scenario_2",
  "requested_index": 2,
  "base_output_dir": "outputs\\pipeline2.0\\batchA\\experiment2_feed_nodes\\a01",
  "source_agent_response": "outputs\\pipeline2.0\\batchA\\experiment2_feed_nodes\\a01\\11_agent_response_chat.md",
  "scenario_file": "outputs\\pipeline2.0\\batchA\\experiment2_feed_nodes\\a01\\scenarios\\scenario_2\\scenario.json",
  "created_or_updated_at": "2026-07-07T17:10:26",
  "next_step": "Continue with another scenario or ask the agent for a refined hypothesis.",
  "spice_executed": true,
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment2_feed_nodes\\a01\\scenarios\\scenario_2\\run\\08_spice_run.json",
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment2_feed_nodes\\a01\\scenarios\\scenario_2\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 4,
    "changed_count": 3,
    "activated_count": 3,
    "missing_count": 0
  },
  "diagnostic_outcome": {
    "status": "partially_resolved",
    "label": "Partially resolved",
    "reason": "The scenario changed the circuit response, but the evidence is not strong enough to stop automatically.",
    "stop_automation": false,
    "confidence": "low",
    "next_step": "Continue with another scenario or ask the agent for a refined hypothesis."
  },
  "controlled_scenario_report": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment2_feed_nodes\\a01\\scenarios\\scenario_2\\12_controlled_scenarios.json",
  "executed_scenarios_count": 1,
  "scenario_budget_exhausted": false
}
```

#### controlled_scenario_report

- Role: Report produced by the controlled scenario runner.
- Path: `outputs\pipeline2.0\batchA\experiment2_feed_nodes\a01\scenarios\scenario_2\12_controlled_scenarios.json`

```json
{
  "source_format": "pipeline2.0_controlled_scenario_report",
  "status": "spice_success",
  "scenario_id": "scenario_2",
  "scenario_title": "Portare il +5 V esistente al ramo lampada",
  "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment2_feed_nodes\\a01\\scenarios\\scenario_2",
  "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment2_feed_nodes\\a01\\scenarios\\scenario_2\\run",
  "netlist": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment2_feed_nodes\\a01\\scenarios\\scenario_2\\run\\07_netlist.cir",
  "applied_actions": [
    {
      "status": "applied",
      "type": "feed_nodes_from_source_node",
      "source_node": "N001",
      "target_nodes": [
        "N002"
      ],
      "resistance": "1m",
      "inserted_lines": [
        "RSCENARIO_FEED_N001_N002 N001 N002 1m"
      ],
      "expanded_connections": [
        {
          "from": "N001",
          "to": "N002",
          "resistance": "1m",
          "inserted_line": "RSCENARIO_FEED_N001_N002 N001 N002 1m",
          "operation": "inserted"
        }
      ],
      "operation": "inserted_or_updated",
      "spice_executed": false,
      "index": 1
    }
  ],
  "unsupported_actions": [],
  "failed_actions": [],
  "spice_executed": true,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment2_feed_nodes\\a01\\scenarios\\scenario_2\\run\\08_spice_run.json",
  "spice_status": "success",
  "spice_exit_code": 0,
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment2_feed_nodes\\a01\\scenarios\\scenario_2\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 4,
    "changed_count": 3,
    "activated_count": 3,
    "missing_count": 0
  },
  "diagnostic_outcome": {
    "status": "partially_resolved",
    "label": "Partially resolved",
    "reason": "The scenario changed the circuit response, but the evidence is not strong enough to stop automatically.",
    "stop_automation": false,
    "confidence": "low",
    "next_step": "Continue with another scenario or ask the agent for a refined hypothesis."
  },
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "created_or_updated_at": "2026-07-07T17:10:26"
}
```

#### scenario_comparison

- Role: Base-vs-scenario comparison used to evaluate the scenario.
- Path: `outputs\pipeline2.0\batchA\experiment2_feed_nodes\a01\scenarios\scenario_2\scenario_comparison.json`

```json
{
  "source_format": "pipeline2.0_scenario_comparison",
  "scenario_id": "scenario_2",
  "scenario_title": "Portare il +5 V esistente al ramo lampada",
  "base_output_dir": "outputs\\pipeline2.0\\batchA\\experiment2_feed_nodes\\a01",
  "scenario_run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment2_feed_nodes\\a01\\scenarios\\scenario_2\\run",
  "base_stdout": "outputs\\pipeline2.0\\batchA\\experiment2_feed_nodes\\a01\\08_ngspice_stdout.txt",
  "scenario_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment2_feed_nodes\\a01\\scenarios\\scenario_2\\run\\08_ngspice_stdout.txt",
  "base_stderr": "outputs\\pipeline2.0\\batchA\\experiment2_feed_nodes\\a01\\08_ngspice_stderr.txt",
  "scenario_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment2_feed_nodes\\a01\\scenarios\\scenario_2\\run\\08_ngspice_stderr.txt",
  "quantities": [
    {
      "quantity": "v(N001)",
      "base_value": 5.0,
      "scenario_value": 5.0,
      "delta": 0.0,
      "change": "unchanged",
      "metric": "v(n001)",
      "base_details": {},
      "scenario_details": {}
    },
    {
      "quantity": "v(N002)",
      "base_value": 0.0,
      "scenario_value": 4.999995,
      "delta": 4.999995,
      "change": "activated",
      "metric": "v(n002)",
      "base_details": {},
      "scenario_details": {}
    },
    {
      "quantity": "v(N004)",
      "base_value": 0.0,
      "scenario_value": 0.238095,
      "delta": 0.238095,
      "change": "activated",
      "metric": "v(n004)",
      "base_details": {},
      "scenario_details": {}
    },
    {
      "quantity": "i(Rlamp13_1)",
      "base_value": 0.0,
      "scenario_value": 0.0047619,
      "delta": 0.0047619,
      "change": "activated",
      "metric": "i(rlamp13_1)",
      "base_details": {},
      "scenario_details": {}
    }
  ],
  "summary": {
    "requested_count": 4,
    "changed_count": 3,
    "activated_count": 3,
    "missing_count": 0
  },
  "diagnostic_outcome": {
    "status": "partially_resolved",
    "label": "Partially resolved",
    "reason": "The scenario changed the circuit response, but the evidence is not strong enough to stop automatically.",
    "stop_automation": false,
    "confidence": "low",
    "next_step": "Continue with another scenario or ask the agent for a refined hypothesis."
  },
  "created_or_updated_at": "2026-07-07T17:10:26"
}
```


## Loaded artifacts

### graph

- Step: `01`
- Role: Graph JSON copied from Pipeline 1.0.
- Path: `outputs\pipeline2.0\batchA\experiment2_feed_nodes\a01\01_graph.json`

```json
{
  "image_id": "a01",
  "image_name": "a01.png",
  "components": [
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
          "relative_position": "right"
        },
        {
          "terminal_id": "connector5.1_pin2",
          "name": "pin2",
          "relative_position": "right"
        },
        {
          "terminal_id": "connector5.1_pin3",
          "name": "pin3",
          "relative_position": "left"
        },
        {
          "terminal_id": "connector5.1_pin4",
          "name": "pin4",
          "relative_position": "left"
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
      "component_id": "lamp13.1",
      "instance_id": "13.1",
      "class_name": "Lamp",
      "terminals": [
        {
          "terminal_id": "lamp13.1_t1",
          "name": "t1",
          "relative_position": "left"
        },
        {
          "terminal_id": "lamp13.1_t2",
          "name": "t2",
          "relative_position": "right"
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
          "relative_position": "left"
        },
        {
          "terminal_id": "led12.1_cathode",
          "name": "cathode",
          "relative_position": "right"
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
    }
  ],
  "terminal_metadata": {},
  "graph": {
    "connector5.1_pin1": [
      "resistor22.2_t1"
    ],
    "connector5.1_pin2": [
      "resistor22.1_t1"
    ],
    "connector5.1_pin3": [
      "switch25.1_t2"
    ],
    "connector5.1_pin4": [
      "gnd9.2_t1"
    ],
    "gnd9.1_t1": [
      "switch25.1_t1"
    ],
    "gnd9.2_t1": [
      "connector5.1_pin4"
    ],
    "gnd9.3_t1": [
      "lamp13.1_t2",
      "led12.1_cathode"
    ],
    "lamp13.1_t1": [
      "resistor22.1_t2"
    ],
    "lamp13.1_t2": [
      "gnd9.3_t1",
      "led12.1_cathode"
    ],
    "led12.1_anode": [
      "resistor22.2_t2"
    ],
    "led12.1_cathode": [
      "gnd9.3_t1",
      "lamp13.1_t2"
    ],
    "resistor22.1_t1": [
      "connector5.1_pin2"
    ],
    "resistor22.1_t2": [
      "lamp13.1_t1"
    ],
    "resistor22.2_t1": [
      "connector5.1_pin1"
    ],
    "resistor22.2_t2": [
      "led12.1_anode"
    ],
    "switch25.1_t1": [
      "gnd9.1_t1"
    ],
    "switch25.1_t2": [
      "connector5.1_pin3"
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
- Path: `outputs\pipeline2.0\batchA\experiment2_feed_nodes\a01\03_node_map.json`

```json
{
  "circuit_id": "a01",
  "source_format": "pipeline2.0_node_map",
  "nodes": [
    {
      "node_id": "0",
      "kind": "ground",
      "terminals": [
        "connector5.1_pin4",
        "gnd9.1_t1",
        "gnd9.2_t1",
        "gnd9.3_t1",
        "lamp13.1_t2",
        "led12.1_cathode",
        "switch25.1_t1"
      ],
      "terminal_count": 7,
      "source_groups": [
        [
          "connector5.1_pin4",
          "gnd9.2_t1"
        ],
        [
          "gnd9.1_t1",
          "switch25.1_t1"
        ],
        [
          "gnd9.3_t1",
          "lamp13.1_t2",
          "led12.1_cathode"
        ]
      ]
    },
    {
      "node_id": "N001",
      "kind": "normal",
      "terminals": [
        "connector5.1_pin1",
        "resistor22.2_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N002",
      "kind": "normal",
      "terminals": [
        "connector5.1_pin2",
        "resistor22.1_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N003",
      "kind": "normal",
      "terminals": [
        "connector5.1_pin3",
        "switch25.1_t2"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N004",
      "kind": "normal",
      "terminals": [
        "lamp13.1_t1",
        "resistor22.1_t2"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N005",
      "kind": "normal",
      "terminals": [
        "led12.1_anode",
        "resistor22.2_t2"
      ],
      "terminal_count": 2
    }
  ],
  "terminal_to_node": {
    "connector5.1_pin1": "N001",
    "connector5.1_pin2": "N002",
    "connector5.1_pin3": "N003",
    "connector5.1_pin4": "0",
    "gnd9.1_t1": "0",
    "gnd9.2_t1": "0",
    "gnd9.3_t1": "0",
    "lamp13.1_t1": "N004",
    "lamp13.1_t2": "0",
    "led12.1_anode": "N005",
    "led12.1_cathode": "0",
    "resistor22.1_t1": "N002",
    "resistor22.1_t2": "N004",
    "resistor22.2_t1": "N001",
    "resistor22.2_t2": "N005",
    "switch25.1_t1": "0",
    "switch25.1_t2": "N003"
  },
  "component_terminal_nodes": {
    "connector5.1": {
      "pin1": "N001",
      "pin2": "N002",
      "pin3": "N003",
      "pin4": "0"
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
    "lamp13.1": {
      "t1": "N004",
      "t2": "0"
    },
    "led12.1": {
      "anode": "N005",
      "cathode": "0"
    },
    "resistor22.1": {
      "t1": "N002",
      "t2": "N004"
    },
    "resistor22.2": {
      "t1": "N001",
      "t2": "N005"
    },
    "switch25.1": {
      "t1": "0",
      "t2": "N003"
    }
  },
  "warnings": {
    "ground_groups_count": 3,
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
    "nodes_count": 6,
    "normal_nodes_count": 5,
    "ground_nodes_count": 1,
    "ground_groups_count": 3,
    "terminal_to_node_count": 17,
    "singleton_nodes_count": 0
  }
}
```

### values_bound

- Step: `04`
- Role: Values and labels bound to graph components.
- Path: `outputs\pipeline2.0\batchA\experiment2_feed_nodes\a01\04_values_bound.json`

```json
{
  "circuit_id": "a01",
  "source_format": "pipeline2.0_values_bound",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_manual_values\\batchA\\a01_values.yaml",
  "supplies": {
    "VCC": {
      "terminal": "connector5.1_pin1",
      "type": "dc",
      "value": 5,
      "unit": "V",
      "reference": 0,
      "source": "manual_from_image_label",
      "label_text": "+5 V DC",
      "node": "N001"
    }
  },
  "components": {
    "connector5.1": {
      "class_name": "Connector",
      "terminal_nodes": {
        "pin1": "N001",
        "pin2": "N002",
        "pin3": "N003",
        "pin4": "0"
      },
      "value_data": null,
      "status": "not_required"
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
    "lamp13.1": {
      "class_name": "Lamp",
      "terminal_nodes": {
        "t1": "N004",
        "t2": "0"
      },
      "value_data": {
        "nominal_voltage": 5,
        "equivalent_resistance": 50,
        "unit": "V",
        "resistance_unit": "ohm",
        "source": "manual_spice_annotation",
        "label_text": "Lamp 5V; Req = 50 ohm",
        "spice": "resistive_load"
      },
      "status": "bound"
    },
    "led12.1": {
      "class_name": "LED",
      "terminal_nodes": {
        "anode": "N005",
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
        "t1": "N002",
        "t2": "N004"
      },
      "value_data": {
        "value": 1000,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "1k"
      },
      "status": "bound"
    },
    "resistor22.2": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N001",
        "t2": "N005"
      },
      "value_data": {
        "value": 220,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "220R"
      },
      "status": "bound"
    },
    "switch25.1": {
      "class_name": "Switch",
      "terminal_nodes": {
        "t1": "0",
        "t2": "N003"
      },
      "value_data": {
        "state": "open",
        "state_source": "graph_json_state",
        "state_confidence": 0.95,
        "source": "graph_json_state"
      },
      "status": "bound"
    }
  },
  "nodes": {
    "connector5.1_pin4": {
      "label": "GND",
      "spice_node": 0,
      "source": "graph_json_gnd",
      "node": "0"
    }
  },
  "simulation": {},
  "missing": [],
  "stats": {
    "components_total": 9,
    "bound_components": 5,
    "missing_components": 0,
    "not_required_components": 4,
    "unsupported_components": 0,
    "supplies_count": 1,
    "manual_nodes_count": 1
  }
}
```

### component_rules

- Step: `06`
- Role: SPICE conversion rules for each component.
- Path: `outputs\pipeline2.0\batchA\experiment2_feed_nodes\a01\06_component_rules.json`

```json
{
  "circuit_id": "a01",
  "source_format": "pipeline2.0_component_rules",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_manual_values\\batchA\\a01_values.yaml",
  "spice_classes_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_spice_classes.yaml",
  "supplies": {
    "VCC": {
      "status": "spice_ready",
      "spice_prefix": "V",
      "emit_as": "independent_voltage_source",
      "nodes": [
        "N001",
        "0"
      ],
      "parameters": {
        "terminal": "connector5.1_pin1",
        "type": "dc",
        "value": 5,
        "unit": "V",
        "reference": 0,
        "source": "manual_from_image_label",
        "label_text": "+5 V DC",
        "node": "N001"
      }
    }
  },
  "components": {
    "connector5.1": {
      "class_name": "Connector",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "Connector used for nodes, labels, and external interfaces."
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
        "N004",
        "0"
      ],
      "parameters": {
        "nominal_voltage": 5,
        "equivalent_resistance": 50,
        "unit": "V",
        "resistance_unit": "ohm",
        "source": "manual_spice_annotation",
        "label_text": "Lamp 5V; Req = 50 ohm",
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
        "N005",
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
        "N002",
        "N004"
      ],
      "parameters": {
        "value": 1000,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "1k"
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
        "N005"
      ],
      "parameters": {
        "value": 220,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "220R"
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
        "0",
        "N003"
      ],
      "parameters": {
        "state": "open",
        "state_source": "graph_json_state",
        "state_confidence": 0.95,
        "source": "graph_json_state"
      },
      "strategy": "open_circuit"
    }
  },
  "simulation": {},
  "stats": {
    "components_total": 9,
    "spice_ready_components": 5,
    "not_emitted_components": 4,
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
- Path: `outputs\pipeline2.0\batchA\experiment2_feed_nodes\a01\07_netlist.cir`

```spice
* pipeline2.0 netlist
* circuit: a01

VVCC N001 0 DC 5
Rlamp13_1 N004 0 50
Dled12_1 N005 0 LED_RED
Rresistor22_1 N002 N004 1000
Rresistor22_2 N001 N005 220
* switch25.1 open: not emitted

.model LED_RED D

.op
.end

```

### spice_emit_report

- Step: `07`
- Role: Report of emitted, skipped and warning components.
- Path: `outputs\pipeline2.0\batchA\experiment2_feed_nodes\a01\07_spice_emit_report.json`

```json
{
  "circuit_id": "a01",
  "source_format": "pipeline2.0_spice_emit_report",
  "emitted_elements": 5,
  "skipped_elements": 4,
  "skipped_components": [
    "connector5.1",
    "gnd9.1",
    "gnd9.2",
    "gnd9.3"
  ],
  "informational_skips": [
    "connector5.1: structural component not emitted",
    "gnd9.1: structural component not emitted",
    "gnd9.2: structural component not emitted",
    "gnd9.3: structural component not emitted"
  ],
  "measurement_points": [],
  "analyses": [
    "op"
  ],
  "transient_export": {
    "path": null,
    "nodes": []
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
- Path: `outputs\pipeline2.0\batchA\experiment2_feed_nodes\a01\08_spice_run.json`

```json
{
  "source_format": "pipeline2.0_spice_run",
  "status": "success",
  "netlist_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a01\\07_netlist.cir",
  "command": [
    "C:\\Users\\m.profilo\\Spice64\\bin\\ngspice_con.exe",
    "-b",
    "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a01\\07_netlist.cir"
  ],
  "exit_code": 0,
  "stdout_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a01\\08_ngspice_stdout.txt",
  "stderr_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a01\\08_ngspice_stderr.txt",
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
- Path: `outputs\pipeline2.0\batchA\experiment2_feed_nodes\a01\08_ngspice_stdout.txt`

```text

Note: No compatibility mode selected!


Circuit: * pipeline2.0 netlist

Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

No. of Data Rows : 1
	Node                                  Voltage
	----                                  -------
	----	-------
	n002                             0.000000e+00
	n005                             7.318156e-01
	n004                             0.000000e+00
	n001                             5.000000e+00

	Source	Current
	------	-------

	vvcc#branch                      -1.94008e-02

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

 Diode: Junction Diode model
     device              dled12_1
      model               led_red
    thermal                     0
         vd              0.731816
         id             0.0194009
         gd              0.750084
         cd                     0

 Resistor: Simple linear resistor
     device         rresistor22_2         rresistor22_1             rlamp13_1
      model                     R                     R                     R
 resistance                   220                  1000                    50
         ac                   220                  1000                    50
      dtemp                     0                     0                     0
     bv_max                 1e+99                 1e+99                 1e+99
      noisy                     1                     1                     1
          i             0.0194008                     0                     0
          p             0.0828064                     0                     0

 Vsource: Independent voltage source
     device                  vvcc
         dc                     5
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
          i            -0.0194008
          p            -0.0970042


Total analysis time (seconds) = 0.0056283

Total elapsed time (seconds) = 0.159 

Total DRAM available = 32239.535 MB.
DRAM currently available = 16439.156 MB.
Maximum ngspice program size =   15.273 MB.
Current ngspice program size =   15.273 MB.


```

### ngspice_stderr

- Step: `08`
- Role: Raw ngspice stderr log.
- Path: `outputs\pipeline2.0\batchA\experiment2_feed_nodes\a01\08_ngspice_stderr.txt`

```text

```

### tran_csv

Artifact not available.
