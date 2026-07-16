# Agent input preview

This file is a local preview of the evidence that will be provided to the read-only diagnostic agent.
The agent remains read-only: it can inspect base outputs and existing scenario artifacts, but it does not modify files.

## User problem

Il circuito dovrebbe amplificare il segnale, ma in uscita vedo un segnale troppo debole o quasi nullo. Quale potrebbe essere il problema?

## Circuit

- Batch: `batchA`
- Circuit: `a04`
- Agent mode: `graph_grounded_readonly`

## Technical summary

```json
{
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_message": "ngspice completed successfully.",
  "emitted_elements": 11,
  "skipped_elements": 1,
  "emit_warnings_count": 0,
  "skipped_components_count": 1,
  "node_count": 7,
  "ground_groups_count": 1,
  "singleton_nodes_count": 0,
  "bound_components": 11,
  "missing_components": 0,
  "unsupported_components": 0,
  "spice_ready_components": 11,
  "rules_missing_components": 0,
  "has_tran_csv": true,
  "has_tran_plot": true
}
```

## Image policy

- Included by default: `False`
- Can be requested: `True`
- Path: `data\batchA\a04.jpg`
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
  "available": false,
  "best_scenario_id": null,
  "best_outcome_status": null,
  "best_stop_automation": null,
  "interpretation_rule": "If a user asks which scenario resolves the problem, prefer the scenario with outcome_status='resolved_candidate' and stop_automation=true. Partially resolved scenarios are supporting diagnostics, not the main solution.",
  "scenarios": []
}
```


## Executed scenarios

No executed scenarios are available in this manifest.


## Loaded artifacts

### graph

- Step: `01`
- Role: Graph JSON copied from Pipeline 1.0.
- Path: `outputs\pipeline2.0\batchA\experiment4\chat\a04\01_graph.json`

```json
{
  "image_id": "a04",
  "image_name": "a04.jpg",
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
      "component_id": "capacitor4.1",
      "instance_id": "4.1",
      "class_name": "Capacitor",
      "terminals": [
        {
          "terminal_id": "capacitor4.1_t1",
          "name": "t1",
          "relative_position": "left"
        },
        {
          "terminal_id": "capacitor4.1_t2",
          "name": "t2",
          "relative_position": "right"
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
      "component_id": "capacitor4.2",
      "instance_id": "4.2",
      "class_name": "Capacitor",
      "terminals": [
        {
          "terminal_id": "capacitor4.2_t1",
          "name": "t1",
          "relative_position": "top"
        },
        {
          "terminal_id": "capacitor4.2_t2",
          "name": "t2",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "capacitor4.3",
      "instance_id": "4.3",
      "class_name": "Capacitor",
      "terminals": [
        {
          "terminal_id": "capacitor4.3_t1",
          "name": "t1",
          "relative_position": "left"
        },
        {
          "terminal_id": "capacitor4.3_t2",
          "name": "t2",
          "relative_position": "right"
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
    }
  ],
  "terminal_metadata": {},
  "graph": {
    "battery2.1_negative": [
      "capacitor4.2_t2",
      "gnd9.1_t1",
      "resistor22.1_t2",
      "resistor22.4_t2",
      "resistor22.5_t2",
      "signal_source23.1_t2"
    ],
    "battery2.1_positive": [
      "resistor22.2_t1",
      "resistor22.3_t1"
    ],
    "capacitor4.1_t1": [
      "signal_source23.1_t1"
    ],
    "capacitor4.1_t2": [
      "npn_transistor18.1_B",
      "resistor22.1_t1",
      "resistor22.2_t2"
    ],
    "capacitor4.2_t1": [
      "npn_transistor18.1_E",
      "resistor22.4_t1"
    ],
    "capacitor4.2_t2": [
      "battery2.1_negative",
      "gnd9.1_t1",
      "resistor22.1_t2",
      "resistor22.4_t2",
      "resistor22.5_t2",
      "signal_source23.1_t2"
    ],
    "capacitor4.3_t1": [
      "npn_transistor18.1_C",
      "resistor22.3_t2"
    ],
    "capacitor4.3_t2": [
      "resistor22.5_t1"
    ],
    "gnd9.1_t1": [
      "battery2.1_negative",
      "capacitor4.2_t2",
      "resistor22.1_t2",
      "resistor22.4_t2",
      "resistor22.5_t2",
      "signal_source23.1_t2"
    ],
    "npn_transistor18.1_B": [
      "capacitor4.1_t2",
      "resistor22.1_t1",
      "resistor22.2_t2"
    ],
    "npn_transistor18.1_C": [
      "capacitor4.3_t1",
      "resistor22.3_t2"
    ],
    "npn_transistor18.1_E": [
      "capacitor4.2_t1",
      "resistor22.4_t1"
    ],
    "resistor22.1_t1": [
      "capacitor4.1_t2",
      "npn_transistor18.1_B",
      "resistor22.2_t2"
    ],
    "resistor22.1_t2": [
      "battery2.1_negative",
      "capacitor4.2_t2",
      "gnd9.1_t1",
      "resistor22.4_t2",
      "resistor22.5_t2",
      "signal_source23.1_t2"
    ],
    "resistor22.2_t1": [
      "battery2.1_positive",
      "resistor22.3_t1"
    ],
    "resistor22.2_t2": [
      "capacitor4.1_t2",
      "npn_transistor18.1_B",
      "resistor22.1_t1"
    ],
    "resistor22.3_t1": [
      "battery2.1_positive",
      "resistor22.2_t1"
    ],
    "resistor22.3_t2": [
      "capacitor4.3_t1",
      "npn_transistor18.1_C"
    ],
    "resistor22.4_t1": [
      "capacitor4.2_t1",
      "npn_transistor18.1_E"
    ],
    "resistor22.4_t2": [
      "battery2.1_negative",
      "capacitor4.2_t2",
      "gnd9.1_t1",
      "resistor22.1_t2",
      "resistor22.5_t2",
      "signal_source23.1_t2"
    ],
    "resistor22.5_t1": [
      "capacitor4.3_t2"
    ],
    "resistor22.5_t2": [
      "battery2.1_negative",
      "capacitor4.2_t2",
      "gnd9.1_t1",
      "resistor22.1_t2",
      "resistor22.4_t2",
      "signal_source23.1_t2"
    ],
    "signal_source23.1_t1": [
      "capacitor4.1_t1"
    ],
    "signal_source23.1_t2": [
      "battery2.1_negative",
      "capacitor4.2_t2",
      "gnd9.1_t1",
      "resistor22.1_t2",
      "resistor22.4_t2",
      "resistor22.5_t2"
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
- Path: `outputs\pipeline2.0\batchA\experiment4\chat\a04\03_node_map.json`

```json
{
  "circuit_id": "a04",
  "source_format": "pipeline2.0_node_map",
  "nodes": [
    {
      "node_id": "0",
      "kind": "ground",
      "terminals": [
        "battery2.1_negative",
        "capacitor4.2_t2",
        "gnd9.1_t1",
        "resistor22.1_t2",
        "resistor22.4_t2",
        "resistor22.5_t2",
        "signal_source23.1_t2"
      ],
      "terminal_count": 7,
      "source_groups": [
        [
          "battery2.1_negative",
          "capacitor4.2_t2",
          "gnd9.1_t1",
          "resistor22.1_t2",
          "resistor22.4_t2",
          "resistor22.5_t2",
          "signal_source23.1_t2"
        ]
      ]
    },
    {
      "node_id": "N001",
      "kind": "normal",
      "terminals": [
        "battery2.1_positive",
        "resistor22.2_t1",
        "resistor22.3_t1"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N002",
      "kind": "normal",
      "terminals": [
        "capacitor4.1_t1",
        "signal_source23.1_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N003",
      "kind": "normal",
      "terminals": [
        "capacitor4.1_t2",
        "npn_transistor18.1_B",
        "resistor22.1_t1",
        "resistor22.2_t2"
      ],
      "terminal_count": 4
    },
    {
      "node_id": "N004",
      "kind": "normal",
      "terminals": [
        "capacitor4.2_t1",
        "npn_transistor18.1_E",
        "resistor22.4_t1"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N005",
      "kind": "normal",
      "terminals": [
        "capacitor4.3_t1",
        "npn_transistor18.1_C",
        "resistor22.3_t2"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N006",
      "kind": "normal",
      "terminals": [
        "capacitor4.3_t2",
        "resistor22.5_t1"
      ],
      "terminal_count": 2
    }
  ],
  "terminal_to_node": {
    "battery2.1_negative": "0",
    "battery2.1_positive": "N001",
    "capacitor4.1_t1": "N002",
    "capacitor4.1_t2": "N003",
    "capacitor4.2_t1": "N004",
    "capacitor4.2_t2": "0",
    "capacitor4.3_t1": "N005",
    "capacitor4.3_t2": "N006",
    "gnd9.1_t1": "0",
    "npn_transistor18.1_B": "N003",
    "npn_transistor18.1_C": "N005",
    "npn_transistor18.1_E": "N004",
    "resistor22.1_t1": "N003",
    "resistor22.1_t2": "0",
    "resistor22.2_t1": "N001",
    "resistor22.2_t2": "N003",
    "resistor22.3_t1": "N001",
    "resistor22.3_t2": "N005",
    "resistor22.4_t1": "N004",
    "resistor22.4_t2": "0",
    "resistor22.5_t1": "N006",
    "resistor22.5_t2": "0",
    "signal_source23.1_t1": "N002",
    "signal_source23.1_t2": "0"
  },
  "component_terminal_nodes": {
    "battery2.1": {
      "positive": "N001",
      "negative": "0"
    },
    "capacitor4.1": {
      "t1": "N002",
      "t2": "N003"
    },
    "capacitor4.2": {
      "t1": "N004",
      "t2": "0"
    },
    "capacitor4.3": {
      "t1": "N005",
      "t2": "N006"
    },
    "gnd9.1": {
      "t1": "0"
    },
    "npn_transistor18.1": {
      "B": "N003",
      "C": "N005",
      "E": "N004"
    },
    "resistor22.1": {
      "t1": "N003",
      "t2": "0"
    },
    "resistor22.2": {
      "t1": "N001",
      "t2": "N003"
    },
    "resistor22.3": {
      "t1": "N001",
      "t2": "N005"
    },
    "resistor22.4": {
      "t1": "N004",
      "t2": "0"
    },
    "resistor22.5": {
      "t1": "N006",
      "t2": "0"
    },
    "signal_source23.1": {
      "t1": "N002",
      "t2": "0"
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
    "nodes_count": 7,
    "normal_nodes_count": 6,
    "ground_nodes_count": 1,
    "ground_groups_count": 1,
    "terminal_to_node_count": 24,
    "singleton_nodes_count": 0
  }
}
```

### values_bound

- Step: `04`
- Role: Values and labels bound to graph components.
- Path: `outputs\pipeline2.0\batchA\experiment4\chat\a04\04_values_bound.json`

```json
{
  "circuit_id": "a04",
  "source_format": "pipeline2.0_values_bound",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_manual_values\\batchA\\a04_values.yaml",
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
        "value": 5,
        "unit": "V",
        "source": "manual_from_image_label",
        "label_text": "V1 5 V"
      },
      "status": "bound"
    },
    "capacitor4.1": {
      "class_name": "Capacitor",
      "terminal_nodes": {
        "t1": "N002",
        "t2": "N003"
      },
      "value_data": {
        "value": 100,
        "unit": "nf",
        "source": "manual_from_image_label",
        "label_text": "C1 100 nF"
      },
      "status": "bound"
    },
    "capacitor4.2": {
      "class_name": "Capacitor",
      "terminal_nodes": {
        "t1": "N004",
        "t2": "0"
      },
      "value_data": {
        "value": 10,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C3 10 uF"
      },
      "status": "bound"
    },
    "capacitor4.3": {
      "class_name": "Capacitor",
      "terminal_nodes": {
        "t1": "N005",
        "t2": "N006"
      },
      "value_data": {
        "value": 1,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C2 1 uF"
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
    "npn_transistor18.1": {
      "class_name": "NPN_Transistor",
      "terminal_nodes": {
        "B": "N003",
        "C": "N005",
        "E": "N004"
      },
      "value_data": {
        "model": "2N2222",
        "source": "manual_from_image_label",
        "label_text": "Q1 2N2222"
      },
      "status": "bound"
    },
    "resistor22.1": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N003",
        "t2": "0"
      },
      "value_data": {
        "value": 10,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R4 10 kOhm"
      },
      "status": "bound"
    },
    "resistor22.2": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N001",
        "t2": "N003"
      },
      "value_data": {
        "value": 22,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R3 22 kOhm"
      },
      "status": "bound"
    },
    "resistor22.3": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N001",
        "t2": "N005"
      },
      "value_data": {
        "value": 2.2,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R1 2.2 kOhm"
      },
      "status": "bound"
    },
    "resistor22.4": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N004",
        "t2": "0"
      },
      "value_data": {
        "value": 1,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R2 1 kOhm"
      },
      "status": "bound"
    },
    "resistor22.5": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N006",
        "t2": "0"
      },
      "value_data": {
        "value": 33,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R5 33 kOhm"
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
        "type": "sin",
        "waveform": "sin",
        "value": 0.01,
        "unit": "V",
        "offset": 0,
        "amplitude": 0.01,
        "frequency": 100,
        "frequency_unit": "Hz",
        "source": "manual_from_image_label",
        "label_text": "SINE(0 10m 100 0.0 0.0)"
      },
      "status": "bound"
    }
  },
  "nodes": {
    "battery2.1_positive": {
      "label": "VCC",
      "source": "manual_from_image_label",
      "label_text": "V1 +5 V",
      "node": "N001"
    },
    "capacitor4.1_t2": {
      "label": "BASE_BIAS",
      "source": "inferred_from_image",
      "node": "N003"
    },
    "capacitor4.3_t2": {
      "label": "VOUT",
      "source": "inferred_from_image",
      "node": "N006"
    },
    "gnd9.1_t1": {
      "label": "GND",
      "spice_node": 0,
      "source": "graph_json_gnd",
      "node": "0"
    },
    "signal_source23.1_t1": {
      "label": "VIN",
      "source": "manual_from_image_label",
      "label_text": "V2",
      "node": "N002"
    }
  },
  "simulation": {
    "analyses": [
      "op",
      "tran"
    ],
    "tran": {
      "step": "0.1ms",
      "stop": "50ms"
    }
  },
  "missing": [],
  "stats": {
    "components_total": 12,
    "bound_components": 11,
    "missing_components": 0,
    "not_required_components": 1,
    "unsupported_components": 0,
    "supplies_count": 0,
    "manual_nodes_count": 5
  }
}
```

### component_rules

- Step: `06`
- Role: SPICE conversion rules for each component.
- Path: `outputs\pipeline2.0\batchA\experiment4\chat\a04\06_component_rules.json`

```json
{
  "circuit_id": "a04",
  "source_format": "pipeline2.0_component_rules",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_manual_values\\batchA\\a04_values.yaml",
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
        "value": 5,
        "unit": "V",
        "source": "manual_from_image_label",
        "label_text": "V1 5 V"
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
        "N003"
      ],
      "parameters": {
        "value": 100,
        "unit": "nf",
        "source": "manual_from_image_label",
        "label_text": "C1 100 nF"
      }
    },
    "capacitor4.2": {
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
        "N004",
        "0"
      ],
      "parameters": {
        "value": 10,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C3 10 uF"
      }
    },
    "capacitor4.3": {
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
        "N005",
        "N006"
      ],
      "parameters": {
        "value": 1,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C2 1 uF"
      }
    },
    "gnd9.1": {
      "class_name": "GND",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "GND terminals are already mapped to SPICE node 0."
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
        "N005",
        "N003",
        "N004"
      ],
      "parameters": {
        "model": "2N2222",
        "source": "manual_from_image_label",
        "label_text": "Q1 2N2222"
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
        "0"
      ],
      "parameters": {
        "value": 10,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R4 10 kOhm"
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
        "N003"
      ],
      "parameters": {
        "value": 22,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R3 22 kOhm"
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
        "N001",
        "N005"
      ],
      "parameters": {
        "value": 2.2,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R1 2.2 kOhm"
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
        "0"
      ],
      "parameters": {
        "value": 1,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R2 1 kOhm"
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
        "N006",
        "0"
      ],
      "parameters": {
        "value": 33,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R5 33 kOhm"
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
        "type": "sin",
        "waveform": "sin",
        "value": 0.01,
        "unit": "V",
        "offset": 0,
        "amplitude": 0.01,
        "frequency": 100,
        "frequency_unit": "Hz",
        "source": "manual_from_image_label",
        "label_text": "SINE(0 10m 100 0.0 0.0)"
      }
    }
  },
  "simulation": {
    "analyses": [
      "op",
      "tran"
    ],
    "tran": {
      "step": "0.1ms",
      "stop": "50ms"
    }
  },
  "stats": {
    "components_total": 12,
    "spice_ready_components": 11,
    "not_emitted_components": 1,
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
- Path: `outputs\pipeline2.0\batchA\experiment4\chat\a04\07_netlist.cir`

```spice
* pipeline2.0 netlist
* circuit: a04

Vbattery2_1 N001 0 DC 5
Ccapacitor4_1 N002 N003 100n
Ccapacitor4_2 N004 0 10u
Ccapacitor4_3 N005 N006 1u
Qnpn_transistor18_1 N005 N003 N004 2N2222
Rresistor22_1 N003 0 10k
Rresistor22_2 N001 N003 22k
Rresistor22_3 N001 N005 2.2k
Rresistor22_4 N004 0 1k
Rresistor22_5 N006 0 33k
Vsignal_source23_1 N002 0 SIN(0 0.01 100)

.model 2N2222 NPN(IS=14.34f BF=255.9 VAF=74.03 IKF=0.2847 ISE=14.34f NE=1.307 BR=6.092 NR=1.005 VAR=11.96 IKR=0.0 ISC=0.0 NC=2 RB=10 RC=1 RE=0.1 CJE=22.01p VJE=0.75 MJE=0.377 CJC=7.306p VJC=0.75 MJC=0.3416 TF=411.1p TR=46.91n)

.op
.save all
.tran 0.1ms 50ms

.control
set wr_singlescale
set wr_vecnames
run
wrdata 08_tran.csv time v(N001) v(N002) v(N003) v(N004) v(N005) v(N006)
.endc
.end

```

### spice_emit_report

- Step: `07`
- Role: Report of emitted, skipped and warning components.
- Path: `outputs\pipeline2.0\batchA\experiment4\chat\a04\07_spice_emit_report.json`

```json
{
  "circuit_id": "a04",
  "source_format": "pipeline2.0_spice_emit_report",
  "emitted_elements": 11,
  "skipped_elements": 1,
  "skipped_components": [
    "gnd9.1"
  ],
  "informational_skips": [
    "gnd9.1: structural component not emitted"
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
      "N006"
    ]
  },
  "models": [
    "2N2222"
  ],
  "warnings": []
}
```

### spice_run

- Step: `08`
- Role: Structured ngspice execution report.
- Path: `outputs\pipeline2.0\batchA\experiment4\chat\a04\08_spice_run.json`

```json
{
  "source_format": "pipeline2.0_spice_run",
  "status": "success",
  "netlist_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a04\\07_netlist.cir",
  "command": [
    "C:\\Users\\m.profilo\\Spice64\\bin\\ngspice_con.exe",
    "-b",
    "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a04\\07_netlist.cir"
  ],
  "exit_code": 0,
  "stdout_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a04\\08_ngspice_stdout.txt",
  "stderr_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a04\\08_ngspice_stderr.txt",
  "tran_raw_csv_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a04\\08_tran_raw.csv",
  "tran_csv_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a04\\08_tran.csv",
  "tran_plot_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a04\\08_tran_plot.png",
  "tran_plot_png_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a04\\08_tran_plot.png",
  "tran_plot_svg_path": null,
  "message": "ngspice completed successfully."
}
```

### ngspice_stdout

- Step: `08`
- Role: Raw ngspice stdout log.
- Path: `outputs\pipeline2.0\batchA\experiment4\chat\a04\08_ngspice_stdout.txt`

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
n001                                         5
n002                                         0
n003                                    1.5202
n004                                  0.876892
n005                                   3.08438
n006                                         0
vsignal_source23_1#branch                    0
vbattery2_1#branch                 -0.00102891


No. of Data Rows : 508
Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

No. of Data Rows : 1

Initial Transient Solution
--------------------------

Node                                   Voltage
----                                   -------
n001                                         5
n002                                         0
n003                                    1.5202
n004                                  0.876892
n005                                   3.08438
n006                                         0
vsignal_source23_1#branch                    0
vbattery2_1#branch                 -0.00102891


No. of Data Rows : 508
	Node                                  Voltage
	----                                  -------
	----	-------
	n006                             0.000000e+00
	n005                             3.084376e+00
	n004                             8.768916e-01
	n003                             1.520196e+00
	n002                             0.000000e+00
	n001                             5.000000e+00

	Source	Current
	------	-------

	vbattery2_1#branch               -1.02891e-03
	vsignal_source23_1#branch        0.000000e+00

 BJT models (Bipolar Junction Transistor)
      model                2n2222

       type                   npn
       tnom                    27
         is             1.434e-14
        ibe                     0
        ibc                     0
         bf                 255.9
         nf                     1
        vaf                 74.03
        ikf                0.2847
        ise             1.434e-14
         ne                 1.307
         br                 6.092
         nr                 1.005
        var                 11.96
        ikr                     0
        isc                     0
         nc                     2
         rb                    10
        irb                     0
        rbm                    10
         re                   0.1
         rc                     1
        cje             2.201e-11
        vje                  0.75
        mje                 0.377
         tf             4.111e-10
        xtf                     0
        vtf                     0
        itf                     0
        ptf                     0
        cjc             7.306e-12
        vjc                  0.75
        mjc                0.3416
       xcjc                     1
         tr             4.691e-08
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
      model                2n2222
         ic           0.000886595
         ib           6.25739e-06
         ie          -0.000892853
        vbe              0.643637
        vbc              -1.52774
         gm             0.0340791
        gpi           0.000218921
        gmu           1.16255e-07
         gx                   0.1
         go           1.23872e-05
        cpi           5.03175e-11
        cmu           4.99893e-12
        cbx                     0
       csub                     0

 Capacitor: Fixed capacitor
     device         ccapacitor4_3         ccapacitor4_2         ccapacitor4_1
      model                     C                     C                     C
capacitance                 1e-06                 1e-05                 1e-07
      dtemp                     0                     0                     0
     bv_max                 1e+99                 1e+99                 1e+99
          i          -9.53728e-07           1.36124e-05            5.1612e-07
          p           -2.9404e-06           1.19686e-05          -7.86066e-07

 Resistor: Simple linear resistor
     device         rresistor22_5         rresistor22_4         rresistor22_3
      model                     R                     R                     R
 resistance                 33000                  1000                  2200
         ac                 33000                  1000                  2200
      dtemp                     0                     0                     0
     bv_max                 1e+99                 1e+99                 1e+99
      noisy                     1                     1                     1
          i          -9.53728e-07            0.00087924           0.000885641
          p           3.00167e-08           0.000773063            0.00172559

 Resistor: Simple linear resistor
     device         rresistor22_2         rresistor22_1
      model                     R                     R
 resistance                 22000                 10000
         ac                 22000                 10000
      dtemp                     0                     0
     bv_max                 1e+99                 1e+99
      noisy                     1                     1
          i           0.000158044           0.000152303
          p           0.000549515           0.000231962

 Vsource: Independent voltage source
     device    vsignal_source23_1           vbattery2_1
         dc                     0                     5
      acmag                     0                     0
      pulse                     0         -
                             0.01          
                              100          
        sin                     0         -
                             0.01          
                              100          
        exp                     0         -
                             0.01          
                              100          
        pwl                     0         -
                             0.01          
                              100          
       sffm                     0         -
                             0.01          
                              100          
         am                     0         -
                             0.01          
                              100          
    trnoise                     0         -
                             0.01          
                              100          
   trrandom                     0         -
                             0.01          
                              100          
    portnum                     0                     0
         z0                     0                     0
        pwr                     0                     0
       freq                     0                     0
      phase                     0                     0
          i           -5.1612e-07           -0.00104369
          p           6.32065e-24           -0.00521843


Total analysis time (seconds) = 0.0118418

Total elapsed time (seconds) = 0.067 

Total DRAM available = 32239.535 MB.
DRAM currently available = 16420.027 MB.
Maximum ngspice program size =   15.465 MB.
Current ngspice program size =   15.465 MB.


```

### ngspice_stderr

- Step: `08`
- Role: Raw ngspice stderr log.
- Path: `outputs\pipeline2.0\batchA\experiment4\chat\a04\08_ngspice_stderr.txt`

```text

```

### tran_csv

- Step: `08`
- Role: Clean transient CSV, when .tran data is available.
- Path: `outputs\pipeline2.0\batchA\experiment4\chat\a04\08_tran.csv`

```csv
time,v(N001),v(N002),v(N003),v(N004),v(N005),v(N006)
0.0,5.0,0.0,1.5201957,0.876891599,3.08437585,0.0
1e-06,5.0,6.28318489e-06,1.52020193,0.87689162,3.08395993,-0.00041590983
2e-06,5.0,1.25663673e-05,1.52020815,0.87689166,3.08354622,-0.000829595481
4e-06,5.0,2.51327148e-05,1.52022053,0.876891782,3.08272427,-0.00165147136
8e-06,5.0,5.02652708e-05,1.52024504,0.876892262,3.08111291,-0.00326253121
1.6e-05,5.0,0.000100529272,1.52029305,0.876894141,3.07801672,-0.00635755952
3.2e-05,5.0,0.000201048383,1.52038521,0.876901331,3.07230245,-0.0120673594
6.4e-05,5.0,0.000402015494,1.52055559,0.876927724,3.06256,-0.0217933908
0.000128,5.0,0.000803381001,1.52085034,0.877017158,3.04859179,-0.0357058461
0.000228,5.0,0.00142767131,1.52121982,0.877217659,3.03705144,-0.0471207014
0.000328,5.0,0.00204632726,1.52151155,0.877453547,3.03317683,-0.0508468723
0.000428,5.0,0.00265690728,1.52175099,0.877695967,3.03337486,-0.0504952957
0.000528,5.0,0.00325700171,1.52195195,0.87792994,3.03564284,-0.0480779649
0.000628,5.0,0.00384424223,1.52212199,0.878148026,3.03894073,-0.0446395905
0.000728,5.0,0.00441631129,1.52226536,0.878346696,3.04272936,-0.040721624
0.000828,5.0,0.00497095119,1.5223846,0.87852444,3.0467295,-0.0366043254
0.000928,5.0,0.00550597301,1.52248134,0.878680795,3.05079672,-0.0324325073
0.001028,5.0,0.00601926528,1.52255674,0.878815832,3.05485624,-0.0282809894
0.001128,5.0,0.00650880225,1.52261174,0.8789299,3.05886922,-0.0241885183
0.001228,5.0,0.00697265196,1.52264712,0.879023487,3.06281502,-0.0201754949
0.001328,5.0,0.00740898379,1.52266363,0.879097155,3.06668225,-0.0162530738
0.001428,5.0,0.00781607575,1.52266197,0.879151503,3.07046389,-0.0124279707
0.001528,5.0,0.00819232123,1.52264285,0.879187155,3.07415502,-0.00870482986
0.001628,5.0,0.00853623536,1.52260698,0.87920475,3.07775143,-0.00508752124
0.001728,5.0,0.00884646086,1.52255507,0.879204948,3.08124657,-0.0015822743
0.001828,5.0,0.00912177343,1.52248787,0.879188404,3.0846452,0.00181600256
0.001928,5.0,0.00936108653,1.52240611,0.879155792,3.08793275,0.00509307989
0.002028,5.0,0.00956345569,1.52231058,0.879107815,3.09110905,0.00824916569
0.002128,5.0,0.00972808227,1.52220205,0.879045181,3.09416937,0.0112799044
0.002228,5.0,0.00985431655,1.52208134,0.878968612,3.09710885,0.0141807985
0.002328,5.0,0.00994166034,1.52194925,0.87887885,3.09992257,0.0169473585
0.002428,5.0,0.00998976894,1.52180664,0.878776651,3.10260557,0.0195750267
0.002528,5.0,0.00999845249,1.52165435,0.878662787,3.10515298,0.0220593488
0.002628,5.0,0.00996767671,1.52149326,0.878538047,3.10755992,0.0243959057
0.002728,5.0,0.00989756307,1.52132425,0.878403234,3.10982174,0.0265804847
0.002828,5.0,0.00978838826,1.52114822,0.878259168,3.11193388,0.0286090085
0.002928,5.0,0.00964058316,1.52096606,0.878106678,3.1138921,0.0304777017
0.003028,5.0,0.00945473108,1.52077869,0.877946609,3.11569235,0.0321830136
0.003128,5.0,0.0092315655,1.52058703,0.877779811,3.11733098,0.0337217794
0.003228,5.0,0.00897196715,1.52039199,0.877607148,3.11880459,0.0350911363
0.003328,5.0,0.00867696054,1.5201945,0.877429487,3.12011029,0.0362886777
0.003428,5.0,0.00834770994,1.51999546,0.877247701,3.12124549,0.0373123639
0.003528,5.0,0.00798551473,1.51979579,0.877062664,3.12220815,0.0381606696
0.003628,5.0,0.00759180435,1.5195964,0.876875251,3.12299662,0.0388324879
0.003728,5.0,0.00716813258,1.51939818,0.876686335,3.12360983,0.0393272719
0.003828,5.0,0.00671617147,1.519202,0.876496785,3.12404715,0.0396449324
0.003928,5.0,0.0062377047,1.51900873,0.876307461,3.12430854,0.0397859732
0.004028,5.0,0.00573462056,1.51881921,0.876119213,3.12439446,0.0397513827
0.004128,5.0,0.00520890449,1.51863428,0.875932882,3.12430598,0.0395427629
0.004228,5.0,0.00466263125,1.51845472,0.87574929,3.12404468,0.0391622156
0.004328,5.0,0.00409795674,1.5182813,0.875569244,3.12361277,0.0386124644
0.004428,5.0,0.00351710946,1.51811478,0.875393529,3.12301297,0.0378967356
0.004528,5.0,0.00292238177,1.51795586,0.875222911,3.12224861,0.0370188747
0.004628,5.0,0.00231612076,1.51780521,0.875058125,3.12132357,0.0359832206
0.004728,5.0,0.00170071909,1.51766348,0.874899884,3.12024231,0.034794717
0.004828,5.0,0.00107860545,1.51753126,0.874748867,3.11900978,0.033458781
0.004928,5.0,0.000452235051,1.51740911,0.874605722,3.11763156,0.0319814089
0.005028,5.0,-0.000175920113,1.51729756,0.874471063,3.11611366,0.0303690398
0.005128,5.0,-0.000803381001,1.51719707,0.874345466,3.11446267,0.0286286557
0.005228,5.0,-0.00142767131,1.51710806,0.874229468,3.11268559,0.0267676406
0.005328,5.0,-0.00204632726,1.51703091,0.874123566,3.11078995,0.0247938757
0.005428,5.0,-0.00265690728,1.51696596,0.874028215,3.10878365,0.0227155939
0.005528,5.0,-0.00325700171,1.51691348,0.873943824,3.10667507,0.0205414702
0.005628,5.0,-0.00384424223,1.5168737,0.873870758,3.10447289,0.0182804729
0.005728,5.0,-0.00441631129,1.51684679,0.873809335,3.10218622,0.0159419498
0.005828,5.0,-0.00497095119,1.51683288,0.873759825,3.09982441,0.0135354753
0.005928,5.0,-0.00550597301,1.51683204,0.873722447,3.09739715,0.0110709341
0.006028,5.0,-0.00601926528,1.51684429,0.873697373,3.09491432,0.00855836525
0.006128,5.0,-0.00650880225,1.51686959,0.873684724,3.09238607,0.00600804273
0.006228,5.0,-0.00697265196,1.51690785,0.873684568,3.08982265,0.00343031765
0.006328,5.0,-0.00740898379,1.51695894,0.873696925,3.08723449,0.000835696913
0.006428,5.0,-0.00781607575,1.51702267,0.873721763,3.08463207,-0.00176531626
0.006528,5.0,-0.00819232123,1.5170988,0.873758998,3.08202595,-0.00436214478
0.006628,5.0,-0.00853623536,1.51718703,0.873808497,3.07942667,-0.00694429789
0.006728,5.0,-0.00884646086,1.51728702,0.873870078,3.07684476,-0.00950129405
0.006828,5.0,-0.00912177343,1.51739839,0.873943507,3.07429062,-0.0120228211
0.006928,5.0,-0.00936108653,1.51752072,0.874028505,3.0717746,-0.0144986587
0.007028,5.0,-0.00956345569,1.51765352,0.874124745,3.06930681,-0.0169188379
0.007128,5.0,-0.00972808227,1.51779627,0.874231853,3.06689725,-0.019273562
0.007228,5.0,-0.00985431655,1.51794843,0.874349415,3.06455559,-0.0215533648
0.007328,5.0,-0.00994166034,1.51810939,0.87447697,3.06229129,-0.0237490298
0.007428,5.0,-0.00998976894,1.51827854,0.874614019,3.06011342,-0.0258517458
0.007528,5.0,-0.00999845249,1.5184552,0.874760026,3.05803077,-0.0278530233
0.007628,5.0,-0.00996767671,1.51863868,0.874914416,3.05605168,-0.0297448476
0.007728,5.0,-0.00989756307,1.51882827,0.875076582,3.05418411,-0.0315195917
0.007828,5.0,-0.00978838826,1.51902322,0.875245886,3.05243552,-0.0331701655
0.007928,5.0,-0.00964058316,1.51922277,0.87542166,3.05081294,-0.0346899258
0.008028,5.0,-0.00945473108,1.51942613,0.875603212,3.04932237,-0.0360732766
0.008128,5.0,-0.0092315655,1.5196325,0.875789824,3.04797135,-0.0373131066
0.008228,5.0,-0.00897196715,1.51984108,0.875980757,3.04676341,-0.038406325
0.008328,5.0,-0.00867696054,1.52005105,0.876175261,3.04570414,-0.0393477828
0.008428,5.0,-0.00834770994,1.52026157,0.876372565,3.04479771,-0.0401337877
0.008528,5.0,-0.00798551473,1.52047182,0.876571892,3.04404771,-0.0407612119
0.008628,5.0,-0.00759180435,1.52068097,0.876772453,3.04345708,-0.0412276162
0.008728,5.0,-0.00716813258,1.5208882,0.876973455,3.04302816,-0.0415311524
0.008828,5.0,-0.00671617147,1.52109269,0.877174106,3.04276257,-0.0416706791
0.008928,5.0,-0.0062377047,1.52129363,0.877373613,3.04266135,-0.0416456578
0.009028,5.0,-0.00573462056,1.52149024,0.877571188,3.04272483,-0.0414562619
0.009128,5.0,-0.00520890449,1.52168174,0.877766052,3.04295274,-0.0411032671
0.009228,5.0,-0.00466263125,1.52186736,0.877957435,3.04334408,-0.040588155
0.009328,5.0,-0.00409795674,1.52204639,0.878144584,3.04389726,-0.0399129978
0.009428,5.0,-0.00351710946,1.52221811,0.87832676,3.04461002,-0.0390805568
0.009528,5.0,-0.00292238177,1.52238184,0.878503246,3.04547948,-0.0380941622
0.009628,5.0,-0.00231612076,1.52253695,0.878673347,3.04650212,-0.0369578061
0.009728,5.0,-0.00170071909,1.52268281,0.878836394,3.04767386,-0.0356760178
0.009828,5.0,-0.00107860545,1.52281884,0.878991745,3.04898997,-0.0342539519
0.009928,5.0,-0.000452235051,1.52294452,0.87913879,3.05044522,-0.0326972596
0.010028,5.0,0.000175920113,1.52305935,0.879276951,3.05203378,-0.031012172
0.010128,5.0,0.000803381001,1.52316287,0.879405687,3.05374934,-0.0292053673
0.010228,5.0,0.00142767131,1.52325466,0.879524493,3.05558507,-0.0272840507
0.010328,5.0,0.00204632726,1.52333438,0.879632903,3.0575337,-0.0252558175
0.010428,5.0,0.00265690728,1.5234017,0.879730493,3.05958748,-0.0231287298
0.010528,5.0,0.00325700171,1.52345635,0.879816883,3.0617383,-0.020911177
0.010628,5.0,0.00384424223,1.52349812,0.879891734,3.06397765,-0.0186119486
0.010728,5.0,0.00441631129,1.52352685,0.879954756,3.0662967,-0.0162400929
0.010828,5.0,0.00497095119,1.52354242,0.880005703,3.06868628,-0.0138049876
0.010928,5.0,0.00550597301,1.52354477,0.880044378,3.07113701,-0.0113161962
0.011028,5.0,0.00601926528,1.52353389,0.880070633,3.07363921,-0.00878353669
0.011128,5.0,0.00650880225,1.52350982,0.880084366,3.07618308,-0.0062169372
0.011228,5.0,0.00697265196,1.52347266,0.880085527,3.0787586,-0.00362650309
0.011328,5.0,0.00740898379,1.52342255,0.880074114,3.08135569,-0.00102237183
0.011428,5.0,0.00781607575,1.52335969,0.880050174,3.08396414,0.00158522026
0.011528,5.0,0.00819232123,1.52328434,0.880013805,3.08657374,0.00418608344
0.011628,5.0,0.00853623536,1.52319678,0.879965151,3.08917427,0.0067700078
0.011728,5.0,0.00884646086,1.52309737,0.879904407,3.09175556,0.00932690827
0.011828,5.0,0.00912177343,1.52298649,0.879831811,3.09430749,0.0118467573
0.011928,5.0,0.00936108653,1.5228646,0.879747652,3.09682011,0.0143197291
0.012028,5.0,0.00956345569,1.52273216,0.879652262,3.09928356,0.0167361309
0.012128,5.0,0.00972808227,1.52258971,0.879546017,3.10168825,0.0190865458
0.012228,5.0,0.00985431655,1.52243781,0.879429334,3.10402476,0.021361763
0.012328,5.0,0.00994166034,1.52227705,0.879302674,3.10628396,0.0235529177
0.012428,5.0,0.00998976894,1.52210808,0.879166534,3.10845702,0.02565142
0.012528,5.0,0.00999845249,1.52193156,0.879021449,3.11053545,0.0276490923
0.012628,5.0,0.00996767671,1.52174818,0.87886799,3.1125111,0.0295380954
0.012728,5.0,0.00989756307,1.52155869,0.87870676,3.11437626,0.0313110631
0.012828,5.0,0.00978838826,1.52136382,0.878538391,3.11612361,0.0329610257
0.012928,5.0,0.00964058316,1.52116434,0.878363546,3.11774631,0.034481541
0.013028,5.0,0.00945473108,1.52096105,0.878182911,3.11923749,0.0358661346
0.013128,5.0,0.0092315655,1.52075475,0.877997195,3.12059294,0.0371110177
0.013228,5.0,0.00897196715,1.52054625,0.877807126,3.12180541,0.038209358
0.013328,5.0,0.00867696054,1.52033637,0.877613452,3.12287091,0.0391576375
0.013428,5.0,0.00834770994,1.52012595,0.877416935,3.12378519,0.0399520572
0.013528,5.0,0.00798551473,1.51991581,0.877218345,3.12454464,0.0405894694
0.013628,5.0,0.00759180435,1.51970679,0.877018465,3.12514618,0.0410672922
0.013728,5.0,0.00716813258,1.51949972,0.876818079,3.12558743,0.041383612
0.013828,5.0,0.00671617147,1.51929539,0.876617976,3.12586655,0.0415370973
0.013928,5.0,0.0062377047,1.51909464,0.876418943,3.1259824,0.0415270976
0.014028,5.0,0.00573462056,1.51889824,0.876221763,3.12593444,0.041353553
0.014128,5.0,0.00520890449,1.51870697,0.876027214,3.12572278,0.0410170896
0.014228,5.0,0.00466263125,1.51852158,0.875836062,3.12534815,0.0405189243
0.014328,5.0,0.00409795674,1.51834281,0.875649061,3.12481197,0.039860955
0.014428,5.0,0.00351710946,1.51817136,0.875466948,3.12411623,0.039045661
0.014528,5.0,0.00292238177,1.5180079,0.875290442,3.12326361,0.0380761885
0.014628,5.0,0.00231612076,1.51785308,0.875120241,3.12225735,0.0369562462
0.014728,5.0,0.00170071909,1.51770752,0.874957017,3.12110136,0.0356901853
0.014828,5.0,0.00107860545,1.51757177,0.874801416,3.11980009,0.0342828908
0.014928,5.0,0.000452235051,1.51744638,0.874654055,3.1183586,0.0327398572
0.015028,5.0,-0.000175920113,1.51733184,0.874515516,3.1167825,0.0310670744
0.015128,5.0,-0.000803381001,1.5172286,0.87438635,3.11507794,0.0292710989
0.015228,5.0,-0.00142767131,1.51713707,0.87426707,3.11325158,0.0273589357
0.015328,5.0,-0.00204632726,1.5170576,0.8741581
```

> Artifact truncated in this preview. The original file remains available through the manifest path.
