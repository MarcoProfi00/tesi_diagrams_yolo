# Agent input preview

This file is a local preview of the evidence that will be provided to the read-only diagnostic agent.
The agent remains read-only: it can inspect base outputs and existing scenario artifacts, but it does not modify files.

## User problem

Se il problema non fosse solo nel valore di un resistore esistente ma in un accoppiamento resistivo troppo debole tra il nodo trigger e la base del transistor, quale scenario self-contained proporresti?

## Circuit

- Batch: `batchA`
- Circuit: `a08`
- Agent mode: `graph_grounded_readonly`

## Technical summary

```json
{
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_message": "ngspice completed successfully.",
  "emitted_elements": 8,
  "skipped_elements": 2,
  "emit_warnings_count": 0,
  "skipped_components_count": 2,
  "node_count": 6,
  "ground_groups_count": 2,
  "singleton_nodes_count": 0,
  "bound_components": 8,
  "missing_components": 0,
  "unsupported_components": 0,
  "spice_ready_components": 8,
  "rules_missing_components": 0,
  "has_tran_csv": true,
  "has_tran_plot": true
}
```

## Image policy

- Included by default: `False`
- Can be requested: `True`
- Path: `data\batchA\a08.jpg`
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
  "interpretation_rule": "If a user asks which scenario resolves the problem, prefer the scenario with outcome_status='resolved_candidate' and stop_automation=true. Partially resolved scenarios are supporting diagnostics, not the main solution.",
  "scenarios": [
    {
      "scenario_id": "scenario_1",
      "title": "Ridurre la resistenza di pilotaggio della base",
      "status": "spice_success",
      "spice_status": "success",
      "outcome_status": "partially_resolved",
      "outcome_label": "Ipotesi confermata sul ramo testato",
      "outcome_technical_label": "Partially resolved",
      "outcome_reason": "Le forme d'onda richieste cambiano tutte nel transitorio, quindi l'ipotesi e supportata, ma questo da solo non basta per fermare automaticamente la diagnosi.",
      "stop_automation": false,
      "comparison_summary": {
        "requested_count": 4,
        "changed_count": 4,
        "activated_count": 0,
        "missing_count": 0
      },
      "quantity_summary": {
        "changed": [
          "v(N001)",
          "v(N003)",
          "v(N004)",
          "v(N005)"
        ],
        "unchanged": [],
        "missing": []
      },
      "score": 24
    }
  ]
}
```


## Executed scenarios

### scenario_1

- Title: `Ridurre la resistenza di pilotaggio della base`
- Status: `spice_success`
- SPICE status: `success`
- Outcome: `partially_resolved`
- Stop automation: `False`
- Comparison: `4/4` changed

#### scenario_definition

- Role: Scenario selected by the user and saved before execution.
- Path: `outputs\pipeline2.0\batchA\experiment3_1\a08\scenarios\scenario_1\scenario.json`

```json
{
  "scenario_id": "scenario_1",
  "title": "Ridurre la resistenza di pilotaggio della base",
  "hypothesis": "Rresistor22_4 may be too large, so N004 does not drive Qnpn_transistor18_1 strongly enough to create a clear LED switching behavior.",
  "actions": [
    {
      "type": "change_component_value",
      "target": "Rresistor22_4",
      "value": "33k"
    }
  ],
  "rerun_from": "07",
  "analysis": "tran",
  "compare": [
    "v(N001)",
    "v(N003)",
    "v(N004)",
    "v(N005)"
  ]
}
```

#### scenario_status

- Role: Current scenario status, SPICE status and diagnostic outcome.
- Path: `outputs\pipeline2.0\batchA\experiment3_1\a08\scenarios\scenario_1\scenario_status.json`

```json
{
  "status": "spice_success",
  "stage": "scenario_spice_executed",
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "scenario_id": "scenario_1",
  "requested_index": 1,
  "base_output_dir": "outputs\\pipeline2.0\\batchA\\experiment3_1\\a08",
  "source_agent_response": "outputs\\pipeline2.0\\batchA\\experiment3_1\\a08\\11_agent_response_chat.md",
  "scenario_file": "outputs\\pipeline2.0\\batchA\\experiment3_1\\a08\\scenarios\\scenario_1\\scenario.json",
  "created_or_updated_at": "2026-07-14T12:50:12",
  "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata.",
  "spice_executed": true,
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment3_1\\a08\\scenarios\\scenario_1\\run\\08_spice_run.json",
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment3_1\\a08\\scenarios\\scenario_1\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 4,
    "changed_count": 4,
    "activated_count": 0,
    "missing_count": 0
  },
  "diagnostic_outcome": {
    "status": "partially_resolved",
    "technical_label": "Partially resolved",
    "label": "Ipotesi confermata sul ramo testato",
    "reason": "Le forme d'onda richieste cambiano tutte nel transitorio, quindi l'ipotesi e supportata, ma questo da solo non basta per fermare automaticamente la diagnosi.",
    "user_message": "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato.",
    "stop_automation": false,
    "confidence": "low",
    "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
  },
  "controlled_scenario_report": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment3_1\\a08\\scenarios\\scenario_1\\12_controlled_scenarios.json",
  "executed_scenarios_count": 1,
  "scenario_budget_exhausted": false
}
```

#### controlled_scenario_report

- Role: Report produced by the controlled scenario runner.
- Path: `outputs\pipeline2.0\batchA\experiment3_1\a08\scenarios\scenario_1\12_controlled_scenarios.json`

```json
{
  "source_format": "pipeline2.0_controlled_scenario_report",
  "status": "spice_success",
  "scenario_id": "scenario_1",
  "scenario_title": "Ridurre la resistenza di pilotaggio della base",
  "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment3_1\\a08\\scenarios\\scenario_1",
  "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment3_1\\a08\\scenarios\\scenario_1\\run",
  "netlist": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment3_1\\a08\\scenarios\\scenario_1\\run\\07_netlist.cir",
  "applied_actions": [
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
      "old_value": "68k",
      "new_value": "33k",
      "old_line": "Rresistor22_4 N001 N004 68k",
      "new_line": "Rresistor22_4 N001 N004 33k",
      "operation": "updated",
      "spice_executed": false,
      "index": 1
    }
  ],
  "unsupported_actions": [],
  "failed_actions": [],
  "spice_executed": true,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment3_1\\a08\\scenarios\\scenario_1\\run\\08_spice_run.json",
  "spice_status": "success",
  "spice_exit_code": 0,
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment3_1\\a08\\scenarios\\scenario_1\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 4,
    "changed_count": 4,
    "activated_count": 0,
    "missing_count": 0
  },
  "diagnostic_outcome": {
    "status": "partially_resolved",
    "technical_label": "Partially resolved",
    "label": "Ipotesi confermata sul ramo testato",
    "reason": "Le forme d'onda richieste cambiano tutte nel transitorio, quindi l'ipotesi e supportata, ma questo da solo non basta per fermare automaticamente la diagnosi.",
    "user_message": "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato.",
    "stop_automation": false,
    "confidence": "low",
    "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
  },
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "created_or_updated_at": "2026-07-14T12:50:12"
}
```

#### scenario_comparison

- Role: Base-vs-scenario comparison used to evaluate the scenario.
- Path: `outputs\pipeline2.0\batchA\experiment3_1\a08\scenarios\scenario_1\scenario_comparison.json`

```json
{
  "source_format": "pipeline2.0_scenario_comparison",
  "scenario_id": "scenario_1",
  "scenario_title": "Ridurre la resistenza di pilotaggio della base",
  "base_output_dir": "outputs\\pipeline2.0\\batchA\\experiment3_1\\a08",
  "scenario_run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment3_1\\a08\\scenarios\\scenario_1\\run",
  "base_stdout": "outputs\\pipeline2.0\\batchA\\experiment3_1\\a08\\08_ngspice_stdout.txt",
  "scenario_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment3_1\\a08\\scenarios\\scenario_1\\run\\08_ngspice_stdout.txt",
  "base_stderr": "outputs\\pipeline2.0\\batchA\\experiment3_1\\a08\\08_ngspice_stderr.txt",
  "scenario_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment3_1\\a08\\scenarios\\scenario_1\\run\\08_ngspice_stderr.txt",
  "quantities": [
    {
      "quantity": "v(N001)",
      "base_value": 2.93553164,
      "scenario_value": 2.87910468,
      "delta": -0.056426960000000026,
      "change": "changed",
      "metric": "v(n001).vpp",
      "base_details": {
        "min": 4.49946297e-28,
        "max": 2.93553164,
        "mean": 1.852321909051438,
        "vpp": 2.93553164
      },
      "scenario_details": {
        "min": 1.15434695e-27,
        "max": 2.87910468,
        "mean": 1.803688394318935,
        "vpp": 2.87910468
      }
    },
    {
      "quantity": "v(N003)",
      "base_value": 6.43514669,
      "scenario_value": 6.43547579,
      "delta": 0.0003291000000000821,
      "change": "changed",
      "metric": "v(n003).vpp",
      "base_details": {
        "min": -5.24852323e-19,
        "max": 6.43514669,
        "mean": 2.7356800189443153,
        "vpp": 6.43514669
      },
      "scenario_details": {
        "min": -3.35201886e-19,
        "max": 6.43547579,
        "mean": 2.7460161881203007,
        "vpp": 6.43547579
      }
    },
    {
      "quantity": "v(N004)",
      "base_value": 2.93119302,
      "scenario_value": 2.87477458,
      "delta": -0.05641843999999985,
      "change": "changed",
      "metric": "v(n004).vpp",
      "base_details": {
        "min": 3.50958111e-27,
        "max": 2.93119302,
        "mean": 1.2039837607388102,
        "vpp": 2.93119302
      },
      "scenario_details": {
        "min": 4.96369188e-27,
        "max": 2.87477458,
        "mean": 1.196499939969927,
        "vpp": 2.87477458
      }
    },
    {
      "quantity": "v(N005)",
      "base_value": 2.50003286,
      "scenario_value": 2.50000379,
      "delta": -2.9070000000075424e-05,
      "change": "changed",
      "metric": "v(n005).vpp",
      "base_details": {
        "min": 1.1220356e-28,
        "max": 2.50003286,
        "mean": 1.26730027397719,
        "vpp": 2.50003286
      },
      "scenario_details": {
        "min": 5.60083124e-29,
        "max": 2.50000379,
        "mean": 1.2680533491291814,
        "vpp": 2.50000379
      }
    }
  ],
  "summary": {
    "requested_count": 4,
    "changed_count": 4,
    "activated_count": 0,
    "missing_count": 0
  },
  "diagnostic_outcome": {
    "status": "partially_resolved",
    "technical_label": "Partially resolved",
    "label": "Ipotesi confermata sul ramo testato",
    "reason": "Le forme d'onda richieste cambiano tutte nel transitorio, quindi l'ipotesi e supportata, ma questo da solo non basta per fermare automaticamente la diagnosi.",
    "user_message": "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato.",
    "stop_automation": false,
    "confidence": "low",
    "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
  },
  "created_or_updated_at": "2026-07-14T12:50:12"
}
```


## Loaded artifacts

### graph

- Step: `01`
- Role: Graph JSON copied from Pipeline 1.0.
- Path: `outputs\pipeline2.0\batchA\experiment3_1\a08\01_graph.json`

```json
{
  "image_id": "a08",
  "image_name": "a08.jpg",
  "components": [
    {
      "component_id": "signal_source23.1",
      "instance_id": "23.1",
      "class_name": "Signal_Source",
      "terminals": [
        {
          "terminal_id": "signal_source23.1_t1",
          "name": "t1",
          "relative_position": "top"
        },
        {
          "terminal_id": "signal_source23.1_t2",
          "name": "t2",
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
      "component_id": "npn_transistor18.1",
      "instance_id": "18.1",
      "class_name": "NPN_Transistor",
      "terminals": [
        {
          "terminal_id": "npn_transistor18.1_B",
          "name": "B",
          "relative_position": "left"
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
    }
  ],
  "terminal_metadata": {},
  "graph": {
    "capacitor4.1_t1": [
      "resistor22.1_t2",
      "resistor22.4_t1"
    ],
    "capacitor4.1_t2": [
      "gnd9.2_t1",
      "resistor22.2_t2"
    ],
    "gnd9.1_t1": [
      "signal_source23.1_t2"
    ],
    "gnd9.2_t1": [
      "capacitor4.1_t2",
      "resistor22.2_t2"
    ],
    "led12.1_anode": [
      "resistor22.1_t1",
      "resistor22.3_t1",
      "signal_source23.1_t1"
    ],
    "led12.1_cathode": [
      "npn_transistor18.1_C"
    ],
    "npn_transistor18.1_B": [
      "resistor22.4_t2"
    ],
    "npn_transistor18.1_C": [
      "led12.1_cathode"
    ],
    "npn_transistor18.1_E": [
      "resistor22.2_t1",
      "resistor22.3_t2"
    ],
    "resistor22.1_t1": [
      "led12.1_anode",
      "resistor22.3_t1",
      "signal_source23.1_t1"
    ],
    "resistor22.1_t2": [
      "capacitor4.1_t1",
      "resistor22.4_t1"
    ],
    "resistor22.2_t1": [
      "npn_transistor18.1_E",
      "resistor22.3_t2"
    ],
    "resistor22.2_t2": [
      "capacitor4.1_t2",
      "gnd9.2_t1"
    ],
    "resistor22.3_t1": [
      "led12.1_anode",
      "resistor22.1_t1",
      "signal_source23.1_t1"
    ],
    "resistor22.3_t2": [
      "npn_transistor18.1_E",
      "resistor22.2_t1"
    ],
    "resistor22.4_t1": [
      "capacitor4.1_t1",
      "resistor22.1_t2"
    ],
    "resistor22.4_t2": [
      "npn_transistor18.1_B"
    ],
    "signal_source23.1_t1": [
      "led12.1_anode",
      "resistor22.1_t1",
      "resistor22.3_t1"
    ],
    "signal_source23.1_t2": [
      "gnd9.1_t1"
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
- Path: `outputs\pipeline2.0\batchA\experiment3_1\a08\03_node_map.json`

```json
{
  "circuit_id": "a08",
  "source_format": "pipeline2.0_node_map",
  "nodes": [
    {
      "node_id": "0",
      "kind": "ground",
      "terminals": [
        "capacitor4.1_t2",
        "gnd9.1_t1",
        "gnd9.2_t1",
        "resistor22.2_t2",
        "signal_source23.1_t2"
      ],
      "terminal_count": 5,
      "source_groups": [
        [
          "capacitor4.1_t2",
          "gnd9.2_t1",
          "resistor22.2_t2"
        ],
        [
          "gnd9.1_t1",
          "signal_source23.1_t2"
        ]
      ]
    },
    {
      "node_id": "N001",
      "kind": "normal",
      "terminals": [
        "capacitor4.1_t1",
        "resistor22.1_t2",
        "resistor22.4_t1"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N002",
      "kind": "normal",
      "terminals": [
        "led12.1_anode",
        "resistor22.1_t1",
        "resistor22.3_t1",
        "signal_source23.1_t1"
      ],
      "terminal_count": 4
    },
    {
      "node_id": "N003",
      "kind": "normal",
      "terminals": [
        "led12.1_cathode",
        "npn_transistor18.1_C"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N004",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.1_B",
        "resistor22.4_t2"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N005",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.1_E",
        "resistor22.2_t1",
        "resistor22.3_t2"
      ],
      "terminal_count": 3
    }
  ],
  "terminal_to_node": {
    "capacitor4.1_t1": "N001",
    "capacitor4.1_t2": "0",
    "gnd9.1_t1": "0",
    "gnd9.2_t1": "0",
    "led12.1_anode": "N002",
    "led12.1_cathode": "N003",
    "npn_transistor18.1_B": "N004",
    "npn_transistor18.1_C": "N003",
    "npn_transistor18.1_E": "N005",
    "resistor22.1_t1": "N002",
    "resistor22.1_t2": "N001",
    "resistor22.2_t1": "N005",
    "resistor22.2_t2": "0",
    "resistor22.3_t1": "N002",
    "resistor22.3_t2": "N005",
    "resistor22.4_t1": "N001",
    "resistor22.4_t2": "N004",
    "signal_source23.1_t1": "N002",
    "signal_source23.1_t2": "0"
  },
  "component_terminal_nodes": {
    "capacitor4.1": {
      "t1": "N001",
      "t2": "0"
    },
    "gnd9.1": {
      "t1": "0"
    },
    "gnd9.2": {
      "t1": "0"
    },
    "led12.1": {
      "anode": "N002",
      "cathode": "N003"
    },
    "npn_transistor18.1": {
      "B": "N004",
      "C": "N003",
      "E": "N005"
    },
    "resistor22.1": {
      "t1": "N002",
      "t2": "N001"
    },
    "resistor22.2": {
      "t1": "N005",
      "t2": "0"
    },
    "resistor22.3": {
      "t1": "N002",
      "t2": "N005"
    },
    "resistor22.4": {
      "t1": "N001",
      "t2": "N004"
    },
    "signal_source23.1": {
      "t1": "N002",
      "t2": "0"
    }
  },
  "warnings": {
    "ground_groups_count": 2,
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
    "ground_groups_count": 2,
    "terminal_to_node_count": 19,
    "singleton_nodes_count": 0
  }
}
```

### values_bound

- Step: `04`
- Role: Values and labels bound to graph components.
- Path: `outputs\pipeline2.0\batchA\experiment3_1\a08\04_values_bound.json`

```json
{
  "circuit_id": "a08",
  "source_format": "pipeline2.0_values_bound",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_manual_values\\batchA\\a08_values.yaml",
  "supplies": {},
  "components": {
    "capacitor4.1": {
      "class_name": "Capacitor",
      "terminal_nodes": {
        "t1": "N001",
        "t2": "0"
      },
      "value_data": {
        "value": 10,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C1 10 uF"
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
    "led12.1": {
      "class_name": "LED",
      "terminal_nodes": {
        "anode": "N002",
        "cathode": "N003"
      },
      "value_data": {
        "model": "LED_RED",
        "source": "manual_from_image_label",
        "label_text": "D1 LTL-307EE"
      },
      "status": "bound"
    },
    "npn_transistor18.1": {
      "class_name": "NPN_Transistor",
      "terminal_nodes": {
        "B": "N004",
        "C": "N003",
        "E": "N005"
      },
      "value_data": {
        "model": "2N3904",
        "source": "manual_from_image_label",
        "label_text": "Q1 2N3904"
      },
      "status": "bound"
    },
    "resistor22.1": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N002",
        "t2": "N001"
      },
      "value_data": {
        "value": 10,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R1 10 kOhm"
      },
      "status": "bound"
    },
    "resistor22.2": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N005",
        "t2": "0"
      },
      "value_data": {
        "value": 560,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R6 560 ohm"
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
        "value": 560,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R7 560 ohm"
      },
      "status": "bound"
    },
    "resistor22.4": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N001",
        "t2": "N004"
      },
      "value_data": {
        "value": 68,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R3 68 kOhm"
      },
      "status": "bound"
    },
    "signal_source23.1": {
      "class_name": "Signal_Source",
      "terminal_nodes": {
        "t1": "N002",
        "t2": "0"
      },
      "value_data": {
        "type": "pulse",
        "waveform": "square",
        "value": 5,
        "unit": "V",
        "low_value": 0,
        "high_value": 5,
        "delay": 0,
        "rise_time": "1ms",
        "fall_time": "1ms",
        "pulse_width": "50ms",
        "period": "100ms",
        "frequency": 10,
        "frequency_unit": "Hz",
        "source": "manual_assumption_from_image_label",
        "label_text": "V2 square 10 Hz",
        "note": "The image shows square 10 Hz but not the amplitude; 0-5 V is assumed for SPICE."
      },
      "status": "bound"
    }
  },
  "nodes": {
    "capacitor4.1_t1": {
      "label": "TRIGGER",
      "source": "manual_from_image_label",
      "label_text": "Trigger",
      "node": "N001"
    },
    "led12.1_cathode": {
      "label": "LED",
      "source": "manual_from_image_label",
      "label_text": "LED",
      "node": "N003"
    },
    "signal_source23.1_t1": {
      "label": "IN",
      "source": "manual_from_image_label",
      "label_text": "IN",
      "node": "N002"
    }
  },
  "simulation": {
    "analyses": [
      "op",
      "tran"
    ],
    "tran": {
      "step": "0.5ms",
      "stop": "300ms"
    }
  },
  "missing": [],
  "stats": {
    "components_total": 10,
    "bound_components": 8,
    "missing_components": 0,
    "not_required_components": 2,
    "unsupported_components": 0,
    "supplies_count": 0,
    "manual_nodes_count": 3
  }
}
```

### component_rules

- Step: `06`
- Role: SPICE conversion rules for each component.
- Path: `outputs\pipeline2.0\batchA\experiment3_1\a08\06_component_rules.json`

```json
{
  "circuit_id": "a08",
  "source_format": "pipeline2.0_component_rules",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_manual_values\\batchA\\a08_values.yaml",
  "spice_classes_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_spice_classes.yaml",
  "supplies": {},
  "components": {
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
        "N001",
        "0"
      ],
      "parameters": {
        "value": 10,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C1 10 uF"
      }
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
        "model": "LED_RED",
        "source": "manual_from_image_label",
        "label_text": "D1 LTL-307EE"
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
        "N003",
        "N004",
        "N005"
      ],
      "parameters": {
        "model": "2N3904",
        "source": "manual_from_image_label",
        "label_text": "Q1 2N3904"
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
        "N001"
      ],
      "parameters": {
        "value": 10,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R1 10 kOhm"
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
        "N005",
        "0"
      ],
      "parameters": {
        "value": 560,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R6 560 ohm"
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
        "value": 560,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R7 560 ohm"
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
        "N001",
        "N004"
      ],
      "parameters": {
        "value": 68,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R3 68 kOhm"
      }
    },
    "signal_source23.1": {
      "class_name": "Signal_Source",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "V",
      "emit_as": "independent_voltage_source",
      "node_order": [
        "t1",
        "t2"
      ],
      "nodes": [
        "N002",
        "0"
      ],
      "parameters": {
        "type": "pulse",
        "waveform": "square",
        "value": 5,
        "unit": "V",
        "low_value": 0,
        "high_value": 5,
        "delay": 0,
        "rise_time": "1ms",
        "fall_time": "1ms",
        "pulse_width": "50ms",
        "period": "100ms",
        "frequency": 10,
        "frequency_unit": "Hz",
        "source": "manual_assumption_from_image_label",
        "label_text": "V2 square 10 Hz",
        "note": "The image shows square 10 Hz but not the amplitude; 0-5 V is assumed for SPICE."
      }
    }
  },
  "simulation": {
    "analyses": [
      "op",
      "tran"
    ],
    "tran": {
      "step": "0.5ms",
      "stop": "300ms"
    }
  },
  "stats": {
    "components_total": 10,
    "spice_ready_components": 8,
    "not_emitted_components": 2,
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
- Path: `outputs\pipeline2.0\batchA\experiment3_1\a08\07_netlist.cir`

```spice
* pipeline2.0 netlist
* circuit: a08

Ccapacitor4_1 N001 0 10u
Dled12_1 N002 N003 LED_RED
Qnpn_transistor18_1 N003 N004 N005 2N3904
Rresistor22_1 N002 N001 10k
Rresistor22_2 N005 0 560
Rresistor22_3 N002 N005 560
Rresistor22_4 N001 N004 68k
Vsignal_source23_1 N002 0 PULSE(0 5 0 1ms 1ms 50ms 100ms)

.model 2N3904 NPN(IS=6.734f BF=416.4 VAF=74.03 IKF=66.78m ISE=6.734f NE=1.259 BR=0.7371 VAR=12.11 IKR=0.0 ISC=0.0 NC=2 RB=10 RC=1 RE=0.1 CJE=4.493p VJE=0.75 MJE=0.2593 CJC=3.638p VJC=0.75 MJC=0.3085 TF=301.2p TR=239.5n)
.model LED_RED D

.op
.save all
.tran 0.5ms 300ms

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
- Path: `outputs\pipeline2.0\batchA\experiment3_1\a08\07_spice_emit_report.json`

```json
{
  "circuit_id": "a08",
  "source_format": "pipeline2.0_spice_emit_report",
  "emitted_elements": 8,
  "skipped_elements": 2,
  "skipped_components": [
    "gnd9.1",
    "gnd9.2"
  ],
  "informational_skips": [
    "gnd9.1: structural component not emitted",
    "gnd9.2: structural component not emitted"
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
    ]
  },
  "models": [
    "2N3904",
    "LED_RED"
  ],
  "warnings": []
}
```

### spice_run

- Step: `08`
- Role: Structured ngspice execution report.
- Path: `outputs\pipeline2.0\batchA\experiment3_1\a08\08_spice_run.json`

```json
{
  "source_format": "pipeline2.0_spice_run",
  "status": "success",
  "netlist_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a08\\07_netlist.cir",
  "command": [
    "C:\\Users\\m.profilo\\Spice64\\bin\\ngspice_con.exe",
    "-b",
    "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a08\\07_netlist.cir"
  ],
  "exit_code": 0,
  "stdout_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a08\\08_ngspice_stdout.txt",
  "stderr_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a08\\08_ngspice_stderr.txt",
  "tran_raw_csv_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a08\\08_tran_raw.csv",
  "tran_csv_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a08\\08_tran.csv",
  "tran_plot_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a08\\08_tran_plot.png",
  "tran_plot_png_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a08\\08_tran_plot.png",
  "tran_plot_svg_path": null,
  "message": "ngspice completed successfully."
}
```

### ngspice_stdout

- Step: `08`
- Role: Raw ngspice stdout log.
- Path: `outputs\pipeline2.0\batchA\experiment3_1\a08\08_ngspice_stdout.txt`

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
n001                               4.49946e-28
n002                                         0
n003                              -5.24852e-19
n004                               3.50958e-27
n005                               1.12204e-28
vsignal_source23_1#branch          3.24576e-31


No. of Data Rows : 669
Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

No. of Data Rows : 1

Initial Transient Solution
--------------------------

Node                                   Voltage
----                                   -------
n001                               4.49946e-28
n002                                         0
n003                              -5.24852e-19
n004                               3.50958e-27
n005                               1.12204e-28
vsignal_source23_1#branch          3.24576e-31


No. of Data Rows : 669
	Node                                  Voltage
	----                                  -------
	----	-------
	n005                             1.122036e-28
	n004                             3.509581e-27
	n003                             -5.24852e-19
	n002                             0.000000e+00
	n001                             4.499463e-28

	Source	Current
	------	-------

	vsignal_source23_1#branch        3.245763e-31

 BJT models (Bipolar Junction Transistor)
      model                2n3904

       type                   npn
       tnom                    27
         is             6.734e-15
        ibe                     0
        ibc                     0
         bf                 416.4
         nf                     1
        vaf                 74.03
        ikf               0.06678
        ise             6.734e-15
         ne                 1.259
         br                0.7371
         nr                     1
        var                 12.11
        ikr                     0
        isc                     0
         nc                     2
         rb                    10
        irb                     0
        rbm                    10
         re                   0.1
         rc                     1
        cje             4.493e-12
        vje                  0.75
        mje                0.2593
         tf             3.012e-10
        xtf                     0
        vtf                     0
        itf                     0
        ptf                     0
        cjc             3.638e-12
        vjc                  0.75
        mjc                0.3085
       xcjc                     1
         tr             2.395e-07
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

 BJT: Bipolar Junction Transistor
     device   qnpn_transistor18_1
      model                2n3904
         ic          -3.16904e-12
         ib           1.67654e-05
         ie          -1.67654e-05
        vbe               0.57415
        vbc              0.551121
         gm           0.000631687
        gpi           1.21549e-05
        gmu           0.000634169
         gx                   0.1
         go           0.000441466
        cpi           6.44107e-12
        cmu           1.17016e-10
        cbx                     0
       csub                     0

 Capacitor: Fixed capacitor
     device         ccapacitor4_1
      model                     C
capacitance                 1e-05
      dtemp                     0
     bv_max                 1e+99
          i          -0.000188668
          p          -0.000324326

 Diode: Junction Diode model
     device              dled12_1
      model               led_red
    thermal                     0
         vd            -0.0277254
         id           -3.4302e-14
         gd           1.13236e-12
         cd                     0

 Resistor: Simple linear resistor
     device         rresistor22_4         rresistor22_3         rresistor22_2
      model                     R                     R                     R
 resistance                 68000                   560                   560
         ac                 68000                   560                   560
      dtemp                     0                     0                     0
     bv_max                 1e+99                 1e+99                 1e+99
      noisy                     1                     1                     1
          i            1.6765e-05          -8.38248e-06           8.38248e-06
          p           1.91124e-05            3.9349e-08            3.9349e-08

 Resistor: Simple linear resistor
     device         rresistor22_1
      model                     R
 resistance                 10000
         ac                 10000
      dtemp                     0
     bv_max                 1e+99
      noisy                     1
          i          -0.000171903
          p           0.000295507

 Vsource: Independent voltage source
     device    vsignal_source23_1
         dc                     0
      acmag                     0
      pulse                     0
                                5
                                0
                            0.001
                            0.001
                             0.05
                              0.1
        sin                     0
```

> Artifact truncated in this preview. The original file remains available through the manifest path.

### ngspice_stderr

- Step: `08`
- Role: Raw ngspice stderr log.
- Path: `outputs\pipeline2.0\batchA\experiment3_1\a08\08_ngspice_stderr.txt`

```text

```

### tran_csv

- Step: `08`
- Role: Clean transient CSV, when .tran data is available.
- Path: `outputs\pipeline2.0\batchA\experiment3_1\a08\08_tran.csv`

```csv
time,v(N001),v(N002),v(N003),v(N004),v(N005)
0.0,4.49946297e-28,0.0,-5.24852323e-19,3.50958111e-27,1.1220356e-28
5e-06,1.25522826e-06,0.025,0.00072098992,0.000720834607,0.012497037
5.4211354e-06,1.36983444e-06,0.027105677,0.000744839377,0.000744675255,0.0135497778
6.26340619e-06,1.6167935e-06,0.0313170309,0.000764892903,0.000764714189,0.0156553733
7.94794777e-06,2.21713656e-06,0.0397397389,0.000761108426,0.000760900278,0.0198667455
1.13170309e-05,3.84342415e-06,0.0565851547,0.000761974147,0.000761668411,0.0282894569
1.80551973e-05,8.7983504e-06,0.0902759864,0.000761136425,0.000760332658,0.0451348988
3.153153e-05,2.55170506e-05,0.15765765,0.000780558379,0.000770751138,0.0788257575
5.84841953e-05,8.61862202e-05,0.292420977,0.00351817067,0.000861281948,0.146207495
8.64432457e-05,0.000187499704,0.432216228,0.0647967841,0.00188848235,0.216105245
0.000113292277,0.0003215713,0.566461385,0.193387371,0.00228297041,0.283227754
0.000153956407,0.000593181102,0.769782035,0.401479421,0.00230770587,0.384888236
0.000195186174,0.000952843818,0.975930871,0.606995637,0.00269335981,0.487962649
0.000277645709,0.00192659407,1.38822854,1.02285515,0.0034848374,0.694111663
0.000442564777,0.00489074988,2.21282389,1.84931695,0.00635312334,1.10640945
0.000721282389,0.0129760248,3.60641194,3.24757465,0.0142282671,1.80320375
0.001,0.0249175134,5.0,4.64100505,0.0261227651,2.49999786
0.00105,0.0274038197,5.0,4.6857279,0.0275151854,2.50000002
0.00115,0.0323739387,5.0,4.73761632,0.0323695912,2.50000006
0.00135,0.0422992645,5.0,4.75733391,0.0422969551,2.50000003
0.00175,0.0620904801,5.0,4.78194536,0.0620762881,2.50000006
0.00225,0.0867184503,5.0,4.80547052,0.0867123496,2.50000002
0.00275,0.111223588,5.0,4.82838346,0.111209218,2.50000006
0.00325,0.135606505,5.0,4.85078302,0.13560023,2.50000002
0.00375,0.159867811,5.0,4.8728268,0.159853396,2.50000006
0.00425,0.184008114,5.0,4.8946531,0.184001822,2.50000002
0.00475,0.208028016,5.0,4.91628479,0.20801364,2.50000006
0.00525,0.231928118,5.0,4.93778148,0.231921852,2.50000002
0.00575,0.255709018,5.0,4.95912331,0.255694701,2.50000006
0.00625,0.279371309,5.0,4.98034839,0.279365077,2.50000002
0.00675,0.302915585,5.0,5.00142755,0.302901331,2.50000006
0.00725,0.326342432,5.0,5.0223948,0.326336236,2.50000002
0.00775,0.349652437,5.0,5.04321916,0.349638248,2.50000006
0.00825,0.372846183,5.0,5.06393354,0.372840023,2.50000002
0.00875,0.39592425,5.0,5.08450661,0.395910123,2.50000006
0.00925,0.418887214,5.0,5.10497111,0.418881088,2.50000002
0.00975,0.441735649,5.0,5.12529599,0.441721585,2.50000006
0.01025,0.464470127,5.0,5.14551358,0.464464037,2.50000002
0.01075,0.487091217,5.0,5.16559248,0.487077215,2.50000006
0.01125,0.509599482,5.0,5.18556523,0.509593426,2.50000002
0.01175,0.531995488,5.0,5.20540095,0.531981548,2.50000006
0.01225,0.554279792,5.0,5.22513187,0.55427377,2.50000002
0.01275,0.576452953,5.0,5.24472697,0.576439075,2.50000006
0.01325,0.598515524,5.0,5.26421825,0.598509535,2.50000002
0.01375,0.620468058,5.0,5.283575,0.620454241,2.50000006
0.01425,0.642311103,5.0,5.30282922,0.642305147,2.50000002
0.01475,0.664045205,5.0,5.32195003,0.664031448,2.50000006
0.01525,0.685670908,5.0,5.34096955,0.685664983,2.50000002
0.01575,0.707188751,5.0,5.35985712,0.707175054,2.50000005
0.01625,0.728599274,5.0,5.37864444,0.728593381,2.50000002
0.01675,0.749903011,5.0,5.39730103,0.749889373,2.50000005
0.01725,0.771100495,5.0,5.41585845,0.771094634,2.50000002
0.01775,0.792192256,5.0,5.4342863,0.792178677,2.50000005
0.01825,0.813178821,5.0,5.45261631,0.813172991,2.50000002
0.01875,0.834060715,5.0,5.4708181,0.834047195,2.50000005
0.01925,0.85483846,5.0,5.48892297,0.85483266,2.50000002
0.01975,0.875512576,5.0,5.50690077,0.875499113,2.50000005
0.02025,0.896083578,5.0,5.52478286,0.896077808,2.50000002
0.02075,0.916551982,5.0,5.54253913,0.916538577,2.50000005
0.02125,0.936918299,5.0,5.56020072,0.936912558,2.50000002
0.02175,0.957183039,5.0,5.57773773,0.957169691,2.50000005
0.02225,0.977346708,5.0,5.59518129,0.977340995,2.50000002
0.02275,0.997409809,5.0,5.61250134,0.997396518,2.50000005
0.02325,1.01737285,5.0,5.62972883,1.01736716,2.50000002
0.02375,1.03723632,5.0,5.64683415,1.03722308,2.50000005
0.02425,1.05700072,5.0,5.66384808,1.05699506,2.50000002
0.02475,1.07666654,5.0,5.68074083,1.07665336,2.50000005
0.02525,1.09623428,5.0,5.69754318,1.09622865,2.50000002
0.02575,1.11570443,5.0,5.71422561,1.1156913,2.50000005
0.02625,1.13507747,5.0,5.73081874,1.13507186,2.50000002
0.02675,1.15435388,5.0,5.74729303,1.15434081,2.50000005
0.02725,1.17353415,5.0,5.76367908,1.17352858,2.50000002
0.02775,1.19261877,5.0,5.7799476,1.19260575,2.50000005
0.02825,1.21160819,5.0,5.79612877,1.21160264,2.50000002
0.02875,1.23050291,5.0,5.81219333,1.23048994,2.50000005
0.02925,1.24930338,5.0,5.82817157,1.24929786,2.50000002
0.02975,1.26801009,5.0,5.84403433,1.26799718,2.50000005
0.03025,1.2866235,5.0,5.85981189,1.286618,2.50000002
0.03075,1.30514408,5.0,5.87547526,1.30513122,2.50000005
0.03125,1.32357228,5.0,5.89105427,1.3235668,2.50000002
0.03175,1.34190857,5.0,5.90651997,1.34189576,2.50000005
0.03225,1.36015341,5.0,5.92190246,1.36014796,2.50000002
0.03275,1.37830725,5.0,5.93717287,1.3782945,2.50000005
0.03325,1.39637055,5.0,5.95236085,1.39636512,2.50000002
0.03375,1.41434376,5.0,5.96743759,1.41433105,2.50000005
0.03425,1.43222732,5.0,5.98243288,1.43222191,2.50000002
0.03475,1.45002169,5.0,5.9973182,1.45000904,2.50000005
0.03525,1.46772731,5.0,6.0121231,1.46772193,2.50000002
0.03575,1.48534463,5.0,6.02681899,1.48533202,2.50000005
0.03625,1.50287407,5.0,6.04143527,1.50286871,2.50000002
0.03675,1.52031609,5.0,6.05594364,1.52030354,2.50000005
0.03725,1.53767112,5.0,6.07037352,1.53766577,2.50000002
0.03775,1.55493958,5.0,6.08469642,1.55492708,2.50000005
0.03825,1.57212192,5.0,6.09894153,1.5721166,2.50000002
0.03875,1.58921857,5.0,6.11308072,1.58920611,2.50000005
0.03925,1.60622994,5.0,6.12714307,1.60622463,2.50000002
0.03975,1.62315647,5.0,6.14110064,1.62314406,2.50000005
0.04025,1.63999857,5.0,6.15498228,1.63999328,2.50000002
0.04075,1.65675668,5.0,6.16876006,1.65674431,2.50000005
0.04125,1.6734312,5.0,6.18246285,1.67342593,2.50000002
0.04175,1.69002256,5.0,6.1960628,1.69001024,2.50000005
0.04225,1.70653117,5.0,6.20958856,1.70652592,2.50000002
0.04275,1.72295744,5.0,6.22301237,1.72294517,2.50000005
0.04325,1.73930179,5.0,6.23636295,1.73929655,2.50000002
0.04375,1.75556462,5.0,6.24961258,1.75555239,2.50000005
0.04425,1.77174633,5.0,6.26278961,1.77174111,2.50000002
0.04475,1.78784734,5.0,6.27586662,1.78783516,2.50000005
0.04525,1.80386805,5.0,6.28887206,1.80386284,2.50000002
0.04575,1.81980885,5.0,6.30177853,1.81979671,2.50000005
0.04625,1.83567014,5.0,6.31461419,1.83566495,2.50000002
0.04675,1.85145233,5.0,6.32735188,1.85144024,2.50000005
0.04725,1.8671558,5.0,6.34001978,1.86715063,2.50000002
0.04775,1.88278096,5.0,6.35259052,1.88276891,2.50000005
0.04825,1.89832818,5.0,6.36509209,1.89832302,2.50000002
0.04875,1.91379786,5.0,6.37749748,1.91378585,2.50000005
0.04925,1.92919038,5.0,6.38983457,1.92918523,2.50000002
0.04975,1.94450613,5.0,6.40207637,1.94449416,2.50000005
0.05025,1.9597455,5.0,6.41425058,1.95974036,2.50000002
0.050625,1.97112511,5.0,6.42331639,1.97111318,2.50000005
0.051,1.98246213,5.0,6.43235057,1.98245699,2.50000002
0.0510260479,1.98321399,4.86976029,6.43227698,1.98254568,2.43488289
0.0510781438,1.98464948,4.60928086,6.43335823,1.98395473,2.30464329
0.0511823356,1.98711135,4.088322,6.43514669,1.98641921,2.04416385
0.0513215237,1.98954979,3.39238153,6.41667147,1.98863493,1.69619453
0.0514789733,1.99112958,2.60513365,2.01696159,1.92332937,1.32354732
0.051590832,1.99147957,2.04584021,1.41605594,1.76960119,1.1278457
0.051696031,1.99120016,1.51984511,0.909103119,1.436511,0.812345104
0.0518424424,1.98980562,0.787788058,0.42102878,0.969634846,0.398098761
0.052,1.98701277,0.0,0.0289071308,0.58544954,0.00577114271
0.0520196619,1.98658166,0.0,0.0288109951,0.585489541,0.00576920284
0.0520589856,1.98571964,0.0,0.0288062516,0.585471356,0.0057657282
0.052137633,1.98399675,0.0,0.0288008021,0.585431807,0.00575879678
0.0522949278,1.98055561,0.0,0.0287852911,0.585355946,0.00574493976
0.0526095174,1.97369187,0.0,0.0287589491,0.58520111,0.00571731487
0.0531095174,1.96283351,0.0,0.0287133273,0.584957793,0.00567360587
0.0536095174,1.95203707,0.0,0.0286710264,0.584711801,0.00563016284
0.0541095174,1.94130219,0.0,0.0286259004,0.584467839,0.00558696496
0.0546095174,1.93062852,0.0,0.0285841251,0.584221618,0.00554402842
0.0551095174,1.92001572,0.0,0.0285394829,0.583977446,0.00550133406
0.0556095174,1.90946343,0.0,0.0284982277,0.583730979,0.00545889831
0.0561095174,1.89897131,0.0,0.0284540634,0.583486578,0.00541670181
0.0566095174,1.88853901,0.0,0.0284133231,0.583239846,0.00537476124
0.0571095174,1.87816619,0.0,0.0283696307,0.582995198,0.00533305701
0.0576095174,1.86785251,0.0,0.0283293999,0.582748181,0.00529160606
0.0581095174,1.85759764,0.0,0.0282861735,0.582503265,0.00525038858
0.0586095174,1.84740123,0.0,0.028246447,0.582255942,0.00520942175
0.0591095174,1.83726295,0.0,0.0282036808,0.582010739,0.00516868557
0.0596095174,1.82718247,0.0,0.0281644537,0.581763091,0.00512819744
0.0601095174,1.81715946,0.0,0.0281221418,0.581517581,0.00508793715
0.0606095174,1.80719359,0.0,0.0280834089,0.581269586,0.00504792237
0.0611095174,1.79728454,0.0,0.0280415457,0.581023748,0.00500813264
0.0616095174,1.78743197,0.0,0.0280033022,0.580775387,0.0049685859
0.0621095174,1.77763556,0.0,0.0279618818,0.5805292,0.00492926147
0.0626095174,1.767895,0.0,0.0279241228,0.58028045,0.00489017754
0.0631095174,1.75820996,0.0,0.0278831397,0.580033894,0.0048513132
0.0636095174,1.74858013,0.0,0.0278458603,0.579784734,0.00481268691
0.0641095174,1.73900519,0.0,0.0278053089,0.579537787,0.00477427751
0.0646095174,1.72948482,0.0,0.0277685044,0.579288195,0.00473610374
0.0651095174,1.72001872,0.0,0.0277283793,0.579040836,0.0046981442
0.0656095174,1.71060657,0.0,0.027692045,0.578790789,0.0046604179
0.0661095174,1.70124806,0.0,0.0276523405,0.578542997,0.0046229032
0.0666095174,1.6919429,0.0,0.0276164719,0.578292473,0.00458561938
0.0671095174,1.68269076,0.0,0.0275771827,0.578044223,0.00454854456
0.0676095174,1.67349136,0.0,0.0275417751,0.577793199,0.00451169828
0.0681095174,1.66434438,0.0,0.0275028958,0.577544471,0.00447505843
0.0686095174,1.65524953,0.0,0.0274679449,0.577292923,0.00443864483
0.0691095174,1.64620651,0.0,0.0274294701,0.577043692,0.0044024351
0.0696095174,1.63721502,0.0,0.0273949715,0.576791596,0.00436644936
0.0701095174,1.62827476,0.0,0.0273568959,0.57654184,0.00433066496
0.0706095174,1.61938546,0.0,0.0273228453,0.576289172,0.00429510232
0.0711095174,1.6105468,0.0,0.0272851637,0.576038866,0.00425973853
0.0716095174,1.60175851,0.0,0.0272515568,0.575785602,0.0042245943
0.0721095174,1.59302029,0.0,0.0272142639,0.575534722,0.00418964643
0.0726095174,1.58433186,0.0,0.0271810965,0.575280836,0.00415491595
0.0731095174,1.57569293,0.0,0.0271441872,0.575029357,0.0041203794
0.0736095174,1.56710322,0.0,0.0271114553,0.574774823,0.00408605809
0.0741095174,1.55856245,0.0,0.0270749244,0.57452272,0.00405192829
0.0746095174,1.55007034,0.0,0.0270426239,0.574267513,0.00401801162
0.0751095174,1.54162661,0.0,0.0270064664,0.57401476,0.00398428406
0.0756095174,1.53323098,0.0,0.0269745933,0.573758852,0.00395076755
0.0761095174,1.52488317,0.0,0.0269388041,0.573505423,0.00391743777
0.0766095174,1.51658292,0.0,0.0269073545,0.573248787,0.00388431701
0.0771095174,1.50832995,0.0,0.0268719286,0.572994655,0.00385138062
0.0776095174,1.50012399,0.0,0.0268408987,0.572737263,0.00381865122
0.0781095174,1.49196477,0.0,0.0268058311,0.572482401,0.00378610388
0.0786095174,1.48385203,0.0,0.0267752172,0.572224225,0.00375376154
0.0791095174,1.47578549,0.0,0.026740503,0.571968604,0.00372159894
0.0796095174,1.4677649,0.0,0.0267103013,0.571709615,0.00368963939
0.0801095174,1.45978999,0.0,0.0266759355,0.571453207,0.00365785731
0.0806095174,1.45186049,0.0,0.0266461424,0.571193375,0.00362627634
0.0811095174,1.44397615,0.0,0.0266121203,0.570936151,0.00359487059
0.0816095174,1.43613672,0.0,0.0265827322,0.570675446,0
```

> Artifact truncated in this preview. The original file remains available through the manifest path.
