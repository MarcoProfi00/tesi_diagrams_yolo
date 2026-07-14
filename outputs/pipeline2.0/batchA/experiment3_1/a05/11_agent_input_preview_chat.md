# Agent input preview

This file is a local preview of the evidence that will be provided to the read-only diagnostic agent.
The agent remains read-only: it can inspect base outputs and existing scenario artifacts, but it does not modify files.

## User problem

Adesso che VMON_INPUT e alimentato e il nodo letto dal voltmetro sale a 5 V, qual e la conclusione diagnostica piu probabile? Ha ancora senso provare un altro scenario, oppure il problema principale e gia localizzato?

## Circuit

- Batch: `batchA`
- Circuit: `a05`
- Agent mode: `graph_grounded_readonly`

## Technical summary

```json
{
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_message": "ngspice completed successfully.",
  "emitted_elements": 2,
  "skipped_elements": 6,
  "emit_warnings_count": 1,
  "skipped_components_count": 6,
  "node_count": 5,
  "ground_groups_count": 4,
  "singleton_nodes_count": 0,
  "bound_components": 3,
  "missing_components": 0,
  "unsupported_components": 0,
  "spice_ready_components": 3,
  "rules_missing_components": 0,
  "has_tran_csv": false,
  "has_tran_plot": false
}
```

## Image policy

- Included by default: `False`
- Can be requested: `True`
- Path: `data\batchA\a05.png`
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
  "best_outcome_status": "resolved_candidate",
  "best_stop_automation": true,
  "interpretation_rule": "If a user asks which scenario resolves the problem, prefer the scenario with outcome_status='resolved_candidate' and stop_automation=true. Partially resolved scenarios are supporting diagnostics, not the main solution.",
  "scenarios": [
    {
      "scenario_id": "scenario_1",
      "title": "Alimentare l’ingresso VMON_INPUT dal connettore",
      "status": "spice_success",
      "spice_status": "success",
      "outcome_status": "resolved_candidate",
      "outcome_label": "Ipotesi fortemente confermata",
      "outcome_technical_label": "Candidate resolved",
      "outcome_reason": "Tutte le grandezze richieste cambiano e almeno una grandezza prima inattiva si attiva davvero.",
      "stop_automation": true,
      "comparison_summary": {
        "requested_count": 2,
        "changed_count": 2,
        "activated_count": 2,
        "missing_count": 0
      },
      "quantity_summary": {
        "changed": [
          "v(N003)",
          "v(N001)"
        ],
        "unchanged": [],
        "missing": []
      },
      "score": 182
    }
  ]
}
```


## Executed scenarios

### scenario_1

- Title: `Alimentare l’ingresso VMON_INPUT dal connettore`
- Status: `spice_success`
- SPICE status: `success`
- Outcome: `resolved_candidate`
- Stop automation: `True`
- Comparison: `2/2` changed

#### scenario_definition

- Role: Scenario selected by the user and saved before execution.
- Path: `outputs\pipeline2.0\batchA\experiment3_1\a05\scenarios\scenario_1\scenario.json`

```json
{
  "scenario_id": "scenario_1",
  "title": "Alimentare l’ingresso VMON_INPUT dal connettore",
  "hypothesis": "VMON reads 0 V because node N003 is not externally driven in the base netlist.",
  "actions": [
    {
      "type": "add_voltage_source_between_nodes",
      "positive": "N003",
      "negative": "0",
      "value": "5V"
    }
  ],
  "rerun_from": "07",
  "analysis": "op",
  "compare": [
    "v(N003)",
    "v(N001)"
  ]
}
```

#### scenario_status

- Role: Current scenario status, SPICE status and diagnostic outcome.
- Path: `outputs\pipeline2.0\batchA\experiment3_1\a05\scenarios\scenario_1\scenario_status.json`

```json
{
  "status": "spice_success",
  "stage": "scenario_spice_executed",
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "scenario_id": "scenario_1",
  "requested_index": 1,
  "base_output_dir": "outputs\\pipeline2.0\\batchA\\experiment3_1\\a05",
  "source_agent_response": "outputs\\pipeline2.0\\batchA\\experiment3_1\\a05\\11_agent_response_chat.md",
  "scenario_file": "outputs\\pipeline2.0\\batchA\\experiment3_1\\a05\\scenarios\\scenario_1\\scenario.json",
  "created_or_updated_at": "2026-07-14T12:32:05",
  "next_step": "Ci sono gia evidenze forti per fermarsi qui e passare alla conclusione diagnostica.",
  "spice_executed": true,
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment3_1\\a05\\scenarios\\scenario_1\\run\\08_spice_run.json",
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment3_1\\a05\\scenarios\\scenario_1\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 2,
    "changed_count": 2,
    "activated_count": 2,
    "missing_count": 0
  },
  "diagnostic_outcome": {
    "status": "resolved_candidate",
    "technical_label": "Candidate resolved",
    "label": "Ipotesi fortemente confermata",
    "reason": "Tutte le grandezze richieste cambiano e almeno una grandezza prima inattiva si attiva davvero.",
    "user_message": "Lo scenario fornisce una conferma forte dell'ipotesi testata.",
    "stop_automation": true,
    "confidence": "medium",
    "next_step": "Ci sono gia evidenze forti per fermarsi qui e passare alla conclusione diagnostica."
  },
  "controlled_scenario_report": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment3_1\\a05\\scenarios\\scenario_1\\12_controlled_scenarios.json",
  "executed_scenarios_count": 1,
  "scenario_budget_exhausted": false
}
```

#### controlled_scenario_report

- Role: Report produced by the controlled scenario runner.
- Path: `outputs\pipeline2.0\batchA\experiment3_1\a05\scenarios\scenario_1\12_controlled_scenarios.json`

```json
{
  "source_format": "pipeline2.0_controlled_scenario_report",
  "status": "spice_success",
  "scenario_id": "scenario_1",
  "scenario_title": "Alimentare l’ingresso VMON_INPUT dal connettore",
  "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment3_1\\a05\\scenarios\\scenario_1",
  "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment3_1\\a05\\scenarios\\scenario_1\\run",
  "netlist": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment3_1\\a05\\scenarios\\scenario_1\\run\\07_netlist.cir",
  "applied_actions": [
    {
      "status": "applied",
      "type": "add_voltage_source_between_nodes",
      "positive": "N003",
      "negative": "0",
      "nodes": [
        "N003",
        "0"
      ],
      "value": "5V",
      "normalized_source_definition": "DC 5",
      "normalized_dc_value": "5",
      "inserted_line": "VSCENARIO_SUPPLY_N003_0 N003 0 DC 5",
      "operation": "inserted",
      "spice_executed": false,
      "index": 1
    }
  ],
  "unsupported_actions": [],
  "failed_actions": [],
  "spice_executed": true,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment3_1\\a05\\scenarios\\scenario_1\\run\\08_spice_run.json",
  "spice_status": "success",
  "spice_exit_code": 0,
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment3_1\\a05\\scenarios\\scenario_1\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 2,
    "changed_count": 2,
    "activated_count": 2,
    "missing_count": 0
  },
  "diagnostic_outcome": {
    "status": "resolved_candidate",
    "technical_label": "Candidate resolved",
    "label": "Ipotesi fortemente confermata",
    "reason": "Tutte le grandezze richieste cambiano e almeno una grandezza prima inattiva si attiva davvero.",
    "user_message": "Lo scenario fornisce una conferma forte dell'ipotesi testata.",
    "stop_automation": true,
    "confidence": "medium",
    "next_step": "Ci sono gia evidenze forti per fermarsi qui e passare alla conclusione diagnostica."
  },
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "created_or_updated_at": "2026-07-14T12:32:05"
}
```

#### scenario_comparison

- Role: Base-vs-scenario comparison used to evaluate the scenario.
- Path: `outputs\pipeline2.0\batchA\experiment3_1\a05\scenarios\scenario_1\scenario_comparison.json`

```json
{
  "source_format": "pipeline2.0_scenario_comparison",
  "scenario_id": "scenario_1",
  "scenario_title": "Alimentare l’ingresso VMON_INPUT dal connettore",
  "base_output_dir": "outputs\\pipeline2.0\\batchA\\experiment3_1\\a05",
  "scenario_run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment3_1\\a05\\scenarios\\scenario_1\\run",
  "base_stdout": "outputs\\pipeline2.0\\batchA\\experiment3_1\\a05\\08_ngspice_stdout.txt",
  "scenario_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment3_1\\a05\\scenarios\\scenario_1\\run\\08_ngspice_stdout.txt",
  "base_stderr": "outputs\\pipeline2.0\\batchA\\experiment3_1\\a05\\08_ngspice_stderr.txt",
  "scenario_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment3_1\\a05\\scenarios\\scenario_1\\run\\08_ngspice_stderr.txt",
  "quantities": [
    {
      "quantity": "v(N003)",
      "base_value": 0.0,
      "scenario_value": 5.0,
      "delta": 5.0,
      "change": "activated",
      "metric": "v(n003)",
      "base_details": {},
      "scenario_details": {}
    },
    {
      "quantity": "v(N001)",
      "base_value": 0.0,
      "scenario_value": 5.0,
      "delta": 5.0,
      "change": "activated",
      "metric": "v(n001)",
      "base_details": {},
      "scenario_details": {}
    }
  ],
  "summary": {
    "requested_count": 2,
    "changed_count": 2,
    "activated_count": 2,
    "missing_count": 0
  },
  "diagnostic_outcome": {
    "status": "resolved_candidate",
    "technical_label": "Candidate resolved",
    "label": "Ipotesi fortemente confermata",
    "reason": "Tutte le grandezze richieste cambiano e almeno una grandezza prima inattiva si attiva davvero.",
    "user_message": "Lo scenario fornisce una conferma forte dell'ipotesi testata.",
    "stop_automation": true,
    "confidence": "medium",
    "next_step": "Ci sono gia evidenze forti per fermarsi qui e passare alla conclusione diagnostica."
  },
  "created_or_updated_at": "2026-07-14T12:32:05"
}
```


## Loaded artifacts

### graph

- Step: `01`
- Role: Graph JSON copied from Pipeline 1.0.
- Path: `outputs\pipeline2.0\batchA\experiment3_1\a05\01_graph.json`

```json
{
  "image_id": "a05",
  "image_name": "a05.png",
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
      "component_id": "analog_meter0.1",
      "instance_id": "0.1",
      "class_name": "Analog_Meter",
      "terminals": [
        {
          "terminal_id": "analog_meter0.1_t1",
          "name": "t1",
          "relative_position": "bottom"
        },
        {
          "terminal_id": "analog_meter0.1_t2",
          "name": "t2",
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
    }
  ],
  "terminal_metadata": {},
  "graph": {
    "analog_meter0.1_t1": [
      "resistor22.1_t2"
    ],
    "analog_meter0.1_t2": [
      "gnd9.4_t1"
    ],
    "capacitor4.1_t1": [
      "connector5.1_pin2"
    ],
    "capacitor4.1_t2": [
      "gnd9.3_t1"
    ],
    "connector5.1_pin1": [
      "resistor22.1_t1"
    ],
    "connector5.1_pin2": [
      "capacitor4.1_t1"
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
      "capacitor4.1_t2"
    ],
    "gnd9.4_t1": [
      "analog_meter0.1_t2"
    ],
    "resistor22.1_t1": [
      "connector5.1_pin1"
    ],
    "resistor22.1_t2": [
      "analog_meter0.1_t1"
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
- Path: `outputs\pipeline2.0\batchA\experiment3_1\a05\03_node_map.json`

```json
{
  "circuit_id": "a05",
  "source_format": "pipeline2.0_node_map",
  "nodes": [
    {
      "node_id": "0",
      "kind": "ground",
      "terminals": [
        "analog_meter0.1_t2",
        "capacitor4.1_t2",
        "connector5.1_pin4",
        "gnd9.1_t1",
        "gnd9.2_t1",
        "gnd9.3_t1",
        "gnd9.4_t1",
        "switch25.1_t1"
      ],
      "terminal_count": 8,
      "source_groups": [
        [
          "analog_meter0.1_t2",
          "gnd9.4_t1"
        ],
        [
          "capacitor4.1_t2",
          "gnd9.3_t1"
        ],
        [
          "connector5.1_pin4",
          "gnd9.2_t1"
        ],
        [
          "gnd9.1_t1",
          "switch25.1_t1"
        ]
      ]
    },
    {
      "node_id": "N001",
      "kind": "normal",
      "terminals": [
        "analog_meter0.1_t1",
        "resistor22.1_t2"
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
        "resistor22.1_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N004",
      "kind": "normal",
      "terminals": [
        "connector5.1_pin3",
        "switch25.1_t2"
      ],
      "terminal_count": 2
    }
  ],
  "terminal_to_node": {
    "analog_meter0.1_t1": "N001",
    "analog_meter0.1_t2": "0",
    "capacitor4.1_t1": "N002",
    "capacitor4.1_t2": "0",
    "connector5.1_pin1": "N003",
    "connector5.1_pin2": "N002",
    "connector5.1_pin3": "N004",
    "connector5.1_pin4": "0",
    "gnd9.1_t1": "0",
    "gnd9.2_t1": "0",
    "gnd9.3_t1": "0",
    "gnd9.4_t1": "0",
    "resistor22.1_t1": "N003",
    "resistor22.1_t2": "N001",
    "switch25.1_t1": "0",
    "switch25.1_t2": "N004"
  },
  "component_terminal_nodes": {
    "analog_meter0.1": {
      "t1": "N001",
      "t2": "0"
    },
    "capacitor4.1": {
      "t1": "N002",
      "t2": "0"
    },
    "connector5.1": {
      "pin1": "N003",
      "pin2": "N002",
      "pin3": "N004",
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
    "gnd9.4": {
      "t1": "0"
    },
    "resistor22.1": {
      "t1": "N003",
      "t2": "N001"
    },
    "switch25.1": {
      "t1": "0",
      "t2": "N004"
    }
  },
  "warnings": {
    "ground_groups_count": 4,
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
    "nodes_count": 5,
    "normal_nodes_count": 4,
    "ground_nodes_count": 1,
    "ground_groups_count": 4,
    "terminal_to_node_count": 16,
    "singleton_nodes_count": 0
  }
}
```

### values_bound

- Step: `04`
- Role: Values and labels bound to graph components.
- Path: `outputs\pipeline2.0\batchA\experiment3_1\a05\04_values_bound.json`

```json
{
  "circuit_id": "a05",
  "source_format": "pipeline2.0_values_bound",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_manual_values\\batchA\\a05_values.yaml",
  "supplies": {},
  "components": {
    "analog_meter0.1": {
      "class_name": "Analog_Meter",
      "terminal_nodes": {
        "t1": "N001",
        "t2": "0"
      },
      "value_data": {
        "kind": "voltmeter",
        "label": "VMON",
        "source": "manual_from_image_label",
        "label_text": "VMON"
      },
      "status": "not_required"
    },
    "capacitor4.1": {
      "class_name": "Capacitor",
      "terminal_nodes": {
        "t1": "N002",
        "t2": "0"
      },
      "value_data": {
        "value": 47,
        "unit": "nF",
        "source": "manual_from_image_label",
        "label_text": "47nF"
      },
      "status": "bound"
    },
    "connector5.1": {
      "class_name": "Connector",
      "terminal_nodes": {
        "pin1": "N003",
        "pin2": "N002",
        "pin3": "N004",
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
    "gnd9.4": {
      "class_name": "GND",
      "terminal_nodes": {
        "t1": "0"
      },
      "value_data": null,
      "status": "not_required"
    },
    "resistor22.1": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N003",
        "t2": "N001"
      },
      "value_data": {
        "value": 1000,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "1k"
      },
      "status": "bound"
    },
    "switch25.1": {
      "class_name": "Switch",
      "terminal_nodes": {
        "t1": "0",
        "t2": "N004"
      },
      "value_data": {
        "state": "open",
        "state_source": "graph_json_state",
        "state_confidence": 0.95,
        "source": "graph_json_state",
        "label_text": "TEST"
      },
      "status": "bound"
    }
  },
  "nodes": {
    "connector5.1_pin1": {
      "label": "VMON_INPUT",
      "source": "inferred_from_image_label",
      "node": "N003"
    },
    "connector5.1_pin2": {
      "label": "FILTER_NODE",
      "source": "inferred_from_capacitor_branch",
      "node": "N002"
    },
    "connector5.1_pin3": {
      "label": "TEST",
      "source": "manual_from_image_label",
      "label_text": "TEST",
      "node": "N004"
    },
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
    "bound_components": 3,
    "missing_components": 0,
    "not_required_components": 6,
    "unsupported_components": 0,
    "supplies_count": 0,
    "manual_nodes_count": 4
  }
}
```

### component_rules

- Step: `06`
- Role: SPICE conversion rules for each component.
- Path: `outputs\pipeline2.0\batchA\experiment3_1\a05\06_component_rules.json`

```json
{
  "circuit_id": "a05",
  "source_format": "pipeline2.0_component_rules",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_manual_values\\batchA\\a05_values.yaml",
  "spice_classes_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_spice_classes.yaml",
  "supplies": {},
  "components": {
    "analog_meter0.1": {
      "class_name": "Analog_Meter",
      "status": "measurement_only",
      "spice_support": "measurement",
      "emit_as": "voltage_probe",
      "measurement_kind": "voltage",
      "node_order": [
        "t1",
        "t2"
      ],
      "nodes": [
        "N001",
        "0"
      ],
      "parameters": {
        "kind": "voltmeter",
        "label": "VMON",
        "source": "manual_from_image_label",
        "label_text": "VMON"
      },
      "reason": "Voltmeter/probe only: not emitted as a physical SPICE component; read the voltage between its nodes."
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
        "value": 47,
        "unit": "nF",
        "source": "manual_from_image_label",
        "label_text": "47nF"
      }
    },
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
    "gnd9.4": {
      "class_name": "GND",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "GND terminals are already mapped to SPICE node 0."
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
        "N001"
      ],
      "parameters": {
        "value": 1000,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "1k"
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
        "N004"
      ],
      "parameters": {
        "state": "open",
        "state_source": "graph_json_state",
        "state_confidence": 0.95,
        "source": "graph_json_state",
        "label_text": "TEST"
      },
      "strategy": "open_circuit"
    }
  },
  "simulation": {},
  "stats": {
    "components_total": 9,
    "spice_ready_components": 3,
    "not_emitted_components": 5,
    "measurement_components": 1,
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
- Path: `outputs\pipeline2.0\batchA\experiment3_1\a05\07_netlist.cir`

```spice
* pipeline2.0 netlist
* circuit: a05

Ccapacitor4_1 N002 0 47n
Rresistor22_1 N003 N001 1000
* switch25.1 open: not emitted

.op
.end

```

### spice_emit_report

- Step: `07`
- Role: Report of emitted, skipped and warning components.
- Path: `outputs\pipeline2.0\batchA\experiment3_1\a05\07_spice_emit_report.json`

```json
{
  "circuit_id": "a05",
  "source_format": "pipeline2.0_spice_emit_report",
  "emitted_elements": 2,
  "skipped_elements": 6,
  "skipped_components": [
    "analog_meter0.1",
    "connector5.1",
    "gnd9.1",
    "gnd9.2",
    "gnd9.3",
    "gnd9.4"
  ],
  "informational_skips": [
    "analog_meter0.1: voltage probe not emitted; read voltage between its nodes",
    "connector5.1: structural component not emitted",
    "gnd9.1: structural component not emitted",
    "gnd9.2: structural component not emitted",
    "gnd9.3: structural component not emitted",
    "gnd9.4: structural component not emitted"
  ],
  "measurement_points": [
    {
      "component_id": "analog_meter0.1",
      "kind": "voltage",
      "nodes": [
        "N001",
        "0"
      ],
      "emit_as": "voltage_probe",
      "reason": "Voltmeter/probe only: not emitted as a physical SPICE component; read the voltage between its nodes."
    }
  ],
  "analyses": [
    "op"
  ],
  "transient_export": {
    "path": null,
    "nodes": []
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
- Path: `outputs\pipeline2.0\batchA\experiment3_1\a05\08_spice_run.json`

```json
{
  "source_format": "pipeline2.0_spice_run",
  "status": "success",
  "netlist_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a05\\07_netlist.cir",
  "command": [
    "C:\\Users\\m.profilo\\Spice64\\bin\\ngspice_con.exe",
    "-b",
    "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a05\\07_netlist.cir"
  ],
  "exit_code": 0,
  "stdout_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a05\\08_ngspice_stdout.txt",
  "stderr_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a05\\08_ngspice_stderr.txt",
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
- Path: `outputs\pipeline2.0\batchA\experiment3_1\a05\08_ngspice_stdout.txt`

```text

Note: No compatibility mode selected!


Circuit: * pipeline2.0 netlist

Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

No. of Data Rows : 1
	Node                                  Voltage
	----                                  -------
	----	-------
	n001                             0.000000e+00
	n003                             0.000000e+00
	n002                             0.000000e+00

	Source	Current
	------	-------


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
     device         ccapacitor4_1
      model                     C
capacitance               4.7e-08
      dtemp                     0
     bv_max                 1e+99
          i                     0
          p                     0

 Resistor: Simple linear resistor
     device         rresistor22_1
      model                     R
 resistance                  1000
         ac                  1000
      dtemp                     0
     bv_max                 1e+99
      noisy                     1
          i                     0
          p                     0


Total analysis time (seconds) = 0.0104787

Total elapsed time (seconds) = 0.059 

Total DRAM available = 32239.535 MB.
DRAM currently available = 16354.766 MB.
Maximum ngspice program size =   15.168 MB.
Current ngspice program size =   15.168 MB.


```

### ngspice_stderr

- Step: `08`
- Role: Raw ngspice stderr log.
- Path: `outputs\pipeline2.0\batchA\experiment3_1\a05\08_ngspice_stderr.txt`

```text
Warning: singular matrix:  check node n003

Note: Starting dynamic gmin stepping
Warning: singular matrix:  check node n003

Warning: Dynamic gmin stepping failed
Note: Starting true gmin stepping
Warning: singular matrix:  check node n003

Warning: singular matrix:  check node n003

Warning: singular matrix:  check node n003

Warning: singular matrix:  check node n003

Warning: True gmin stepping failed
Note: Starting source stepping
Warning: source stepping failed
Note: Transient op started
Note: Transient op finished successfully

```

### tran_csv

Artifact not available.
