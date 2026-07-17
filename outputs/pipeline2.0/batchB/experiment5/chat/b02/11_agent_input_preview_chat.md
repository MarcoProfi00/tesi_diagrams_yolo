# Agent input preview

This file is a local preview of the evidence that will be provided to the read-only diagnostic agent.
The agent remains read-only: it can inspect base outputs and existing scenario artifacts, but it does not modify files.

## User problem

Il circuito dovrebbe far lampeggiare alternativamente i due LED, ma nella simulazione restano entrambi accesi. Come mai?

## Circuit

- Batch: `batchB`
- Circuit: `b02`
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
  "node_count": 8,
  "ground_groups_count": 1,
  "singleton_nodes_count": 0,
  "bound_components": 10,
  "missing_components": 0,
  "unsupported_components": 0,
  "spice_ready_components": 10,
  "rules_missing_components": 0,
  "has_tran_csv": true,
  "has_tran_plot": true,
  "led_profiles": {
    "Dled12_1": {
      "state": "steady_on",
      "regular_period": false,
      "frequency_hz": null,
      "duty_cycle": 1.0,
      "on_fraction": 1.0,
      "pulse_count": 1,
      "voltage_min": 0.7259810499999997,
      "voltage_max": 0.7259810499999997,
      "anode_node": "N001",
      "cathode_node": "N002"
    },
    "Dled12_2": {
      "state": "steady_on",
      "regular_period": false,
      "frequency_hz": null,
      "duty_cycle": 1.0,
      "on_fraction": 1.0,
      "pulse_count": 1,
      "voltage_min": 0.7259810499999997,
      "voltage_max": 0.7259810499999997,
      "anode_node": "N001",
      "cathode_node": "N003"
    }
  }
}
```

## Image policy

- Included by default: `False`
- Can be requested: `True`
- Path: `data\batchB\b02.jpg`
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
  "ranking_status": "no_verified_best",
  "interpretation_rule": "If a user asks which scenario resolves the problem, prefer the scenario with outcome_status='resolved_candidate' and stop_automation=true. Partially resolved scenarios without verified expectations are supporting diagnostics and must not be ranked only by changed_count.",
  "scenarios": []
}
```


## Executed scenarios

No executed scenarios are available in this manifest.


## Loaded artifacts

### graph

- Step: `01`
- Role: Graph JSON copied from Pipeline 1.0.
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b02\01_graph.json`

```json
{
  "image_id": "b02",
  "image_name": "b02.jpg",
  "components": [
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
    "gnd9.1_t1": [
      "npn_transistor18.1_E",
      "npn_transistor18.2_E"
    ],
    "led12.1_anode": [
      "led12.2_anode",
      "resistor22.2_t1",
      "resistor22.3_t1"
    ],
    "led12.1_cathode": [
      "resistor22.1_t1"
    ],
    "led12.2_anode": [
      "led12.1_anode",
      "resistor22.2_t1",
      "resistor22.3_t1"
    ],
    "led12.2_cathode": [
      "resistor22.4_t1"
    ],
    "npn_transistor18.1_B": [
      "polarized_capacitor20.2_negative",
      "resistor22.2_t2"
    ],
    "npn_transistor18.1_C": [
      "polarized_capacitor20.1_positive",
      "resistor22.1_t2"
    ],
    "npn_transistor18.1_E": [
      "gnd9.1_t1",
      "npn_transistor18.2_E"
    ],
    "npn_transistor18.2_B": [
      "polarized_capacitor20.1_negative",
      "resistor22.3_t2"
    ],
    "npn_transistor18.2_C": [
      "polarized_capacitor20.2_positive",
      "resistor22.4_t2"
    ],
    "npn_transistor18.2_E": [
      "gnd9.1_t1",
      "npn_transistor18.1_E"
    ],
    "polarized_capacitor20.1_negative": [
      "npn_transistor18.2_B",
      "resistor22.3_t2"
    ],
    "polarized_capacitor20.1_positive": [
      "npn_transistor18.1_C",
      "resistor22.1_t2"
    ],
    "polarized_capacitor20.2_negative": [
      "npn_transistor18.1_B",
      "resistor22.2_t2"
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
      "led12.1_anode",
      "led12.2_anode",
      "resistor22.3_t1"
    ],
    "resistor22.2_t2": [
      "npn_transistor18.1_B",
      "polarized_capacitor20.2_negative"
    ],
    "resistor22.3_t1": [
      "led12.1_anode",
      "led12.2_anode",
      "resistor22.2_t1"
    ],
    "resistor22.3_t2": [
      "npn_transistor18.2_B",
      "polarized_capacitor20.1_negative"
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
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b02\03_node_map.json`

```json
{
  "circuit_id": "b02",
  "source_format": "pipeline2.0_node_map",
  "nodes": [
    {
      "node_id": "0",
      "kind": "ground",
      "terminals": [
        "gnd9.1_t1",
        "npn_transistor18.1_E",
        "npn_transistor18.2_E"
      ],
      "terminal_count": 3,
      "source_groups": [
        [
          "gnd9.1_t1",
          "npn_transistor18.1_E",
          "npn_transistor18.2_E"
        ]
      ]
    },
    {
      "node_id": "N001",
      "kind": "normal",
      "terminals": [
        "led12.1_anode",
        "led12.2_anode",
        "resistor22.2_t1",
        "resistor22.3_t1"
      ],
      "terminal_count": 4
    },
    {
      "node_id": "N002",
      "kind": "normal",
      "terminals": [
        "led12.1_cathode",
        "resistor22.1_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N003",
      "kind": "normal",
      "terminals": [
        "led12.2_cathode",
        "resistor22.4_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N004",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.1_B",
        "polarized_capacitor20.2_negative",
        "resistor22.2_t2"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N005",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.1_C",
        "polarized_capacitor20.1_positive",
        "resistor22.1_t2"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N006",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.2_B",
        "polarized_capacitor20.1_negative",
        "resistor22.3_t2"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N007",
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
    "gnd9.1_t1": "0",
    "led12.1_anode": "N001",
    "led12.1_cathode": "N002",
    "led12.2_anode": "N001",
    "led12.2_cathode": "N003",
    "npn_transistor18.1_B": "N004",
    "npn_transistor18.1_C": "N005",
    "npn_transistor18.1_E": "0",
    "npn_transistor18.2_B": "N006",
    "npn_transistor18.2_C": "N007",
    "npn_transistor18.2_E": "0",
    "polarized_capacitor20.1_negative": "N006",
    "polarized_capacitor20.1_positive": "N005",
    "polarized_capacitor20.2_negative": "N004",
    "polarized_capacitor20.2_positive": "N007",
    "resistor22.1_t1": "N002",
    "resistor22.1_t2": "N005",
    "resistor22.2_t1": "N001",
    "resistor22.2_t2": "N004",
    "resistor22.3_t1": "N001",
    "resistor22.3_t2": "N006",
    "resistor22.4_t1": "N003",
    "resistor22.4_t2": "N007"
  },
  "component_terminal_nodes": {
    "gnd9.1": {
      "t1": "0"
    },
    "led12.1": {
      "anode": "N001",
      "cathode": "N002"
    },
    "led12.2": {
      "anode": "N001",
      "cathode": "N003"
    },
    "npn_transistor18.1": {
      "B": "N004",
      "C": "N005",
      "E": "0"
    },
    "npn_transistor18.2": {
      "B": "N006",
      "C": "N007",
      "E": "0"
    },
    "polarized_capacitor20.1": {
      "positive": "N005",
      "negative": "N006"
    },
    "polarized_capacitor20.2": {
      "negative": "N004",
      "positive": "N007"
    },
    "resistor22.1": {
      "t1": "N002",
      "t2": "N005"
    },
    "resistor22.2": {
      "t1": "N001",
      "t2": "N004"
    },
    "resistor22.3": {
      "t1": "N001",
      "t2": "N006"
    },
    "resistor22.4": {
      "t1": "N003",
      "t2": "N007"
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
    "nodes_count": 8,
    "normal_nodes_count": 7,
    "ground_nodes_count": 1,
    "ground_groups_count": 1,
    "terminal_to_node_count": 23,
    "singleton_nodes_count": 0
  }
}
```

### values_bound

- Step: `04`
- Role: Values and labels bound to graph components.
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b02\04_values_bound.json`

```json
{
  "circuit_id": "b02",
  "source_format": "pipeline2.0_values_bound",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_manual_values\\batchB\\b02_values.yaml",
  "supplies": {
    "VCC": {
      "terminal": "led12.1_anode",
      "type": "dc",
      "value": 5,
      "unit": "V",
      "reference": 0,
      "source": "manual_from_image_label",
      "label_text": "+5V",
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
    "led12.1": {
      "class_name": "LED",
      "terminal_nodes": {
        "anode": "N001",
        "cathode": "N002"
      },
      "value_data": {
        "model": "LED_RED",
        "source": "manual_spice_generic_led_model",
        "label_text": "D1 LED; modello SPICE generico"
      },
      "status": "bound"
    },
    "led12.2": {
      "class_name": "LED",
      "terminal_nodes": {
        "anode": "N001",
        "cathode": "N003"
      },
      "value_data": {
        "model": "LED_RED",
        "source": "manual_spice_generic_led_model",
        "label_text": "D2 LED; modello SPICE generico"
      },
      "status": "bound"
    },
    "npn_transistor18.1": {
      "class_name": "NPN_Transistor",
      "terminal_nodes": {
        "B": "N004",
        "C": "N005",
        "E": "0"
      },
      "value_data": {
        "model": "2N3904",
        "source": "manual_from_image_label",
        "label_text": "Q1 2N3904"
      },
      "status": "bound"
    },
    "npn_transistor18.2": {
      "class_name": "NPN_Transistor",
      "terminal_nodes": {
        "B": "N006",
        "C": "N007",
        "E": "0"
      },
      "value_data": {
        "model": "2N3904",
        "source": "manual_from_image_label",
        "label_text": "Q2 2N3904"
      },
      "status": "bound"
    },
    "polarized_capacitor20.1": {
      "class_name": "Polarized_Capacitor",
      "terminal_nodes": {
        "positive": "N005",
        "negative": "N006"
      },
      "value_data": {
        "value": 47,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C1 47 uF"
      },
      "status": "bound"
    },
    "polarized_capacitor20.2": {
      "class_name": "Polarized_Capacitor",
      "terminal_nodes": {
        "negative": "N004",
        "positive": "N007"
      },
      "value_data": {
        "value": 47,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C2 47 uF"
      },
      "status": "bound"
    },
    "resistor22.1": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N002",
        "t2": "N005"
      },
      "value_data": {
        "value": 270,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R1 270 ohm"
      },
      "status": "bound"
    },
    "resistor22.2": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N001",
        "t2": "N004"
      },
      "value_data": {
        "value": 2.2,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R2 2.2 kohm"
      },
      "status": "bound"
    },
    "resistor22.3": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N001",
        "t2": "N006"
      },
      "value_data": {
        "value": 2.2,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R4 2.2 kohm"
      },
      "status": "bound"
    },
    "resistor22.4": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N003",
        "t2": "N007"
      },
      "value_data": {
        "value": 270,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R3 270 ohm"
      },
      "status": "bound"
    }
  },
  "nodes": {},
  "simulation": {
    "analyses": [
      "op",
      "tran"
    ],
    "tran": {
      "step": "1ms",
      "stop": "1s"
    }
  },
  "missing": [],
  "stats": {
    "components_total": 11,
    "bound_components": 10,
    "missing_components": 0,
    "not_required_components": 1,
    "unsupported_components": 0,
    "supplies_count": 1,
    "manual_nodes_count": 0
  }
}
```

### component_rules

- Step: `06`
- Role: SPICE conversion rules for each component.
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b02\06_component_rules.json`

```json
{
  "circuit_id": "b02",
  "source_format": "pipeline2.0_component_rules",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_manual_values\\batchB\\b02_values.yaml",
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
        "terminal": "led12.1_anode",
        "type": "dc",
        "value": 5,
        "unit": "V",
        "reference": 0,
        "source": "manual_from_image_label",
        "label_text": "+5V",
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
        "N001",
        "N002"
      ],
      "parameters": {
        "model": "LED_RED",
        "source": "manual_spice_generic_led_model",
        "label_text": "D1 LED; modello SPICE generico"
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
        "N001",
        "N003"
      ],
      "parameters": {
        "model": "LED_RED",
        "source": "manual_spice_generic_led_model",
        "label_text": "D2 LED; modello SPICE generico"
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
        "N005",
        "N004",
        "0"
      ],
      "parameters": {
        "model": "2N3904",
        "source": "manual_from_image_label",
        "label_text": "Q1 2N3904"
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
        "N007",
        "N006",
        "0"
      ],
      "parameters": {
        "model": "2N3904",
        "source": "manual_from_image_label",
        "label_text": "Q2 2N3904"
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
        "N005",
        "N006"
      ],
      "parameters": {
        "value": 47,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C1 47 uF"
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
        "N007",
        "N004"
      ],
      "parameters": {
        "value": 47,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C2 47 uF"
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
        "N005"
      ],
      "parameters": {
        "value": 270,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R1 270 ohm"
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
        "N004"
      ],
      "parameters": {
        "value": 2.2,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R2 2.2 kohm"
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
        "N006"
      ],
      "parameters": {
        "value": 2.2,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R4 2.2 kohm"
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
        "N003",
        "N007"
      ],
      "parameters": {
        "value": 270,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R3 270 ohm"
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
      "stop": "1s"
    }
  },
  "stats": {
    "components_total": 11,
    "spice_ready_components": 10,
    "not_emitted_components": 1,
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
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b02\07_netlist.cir`

```spice
* pipeline2.0 netlist
* circuit: b02

VVCC N001 0 DC 5
Dled12_1 N001 N002 LED_RED
Dled12_2 N001 N003 LED_RED
Qnpn_transistor18_1 N005 N004 0 2N3904
Qnpn_transistor18_2 N007 N006 0 2N3904
Cpolarized_capacitor20_1 N005 N006 47u
Cpolarized_capacitor20_2 N007 N004 47u
Rresistor22_1 N002 N005 270
Rresistor22_2 N001 N004 2.2k
Rresistor22_3 N001 N006 2.2k
Rresistor22_4 N003 N007 270

.model 2N3904 NPN(IS=6.734f BF=416.4 VAF=74.03 IKF=66.78m ISE=6.734f NE=1.259 BR=0.7371 VAR=12.11 IKR=0.0 ISC=0.0 NC=2 RB=10 RC=1 RE=0.1 CJE=4.493p VJE=0.75 MJE=0.2593 CJC=3.638p VJC=0.75 MJC=0.3085 TF=301.2p TR=239.5n)
.model LED_RED D

.op
.save all
.tran 1ms 1s

.control
set wr_singlescale
set wr_vecnames
run
wrdata 08_tran.csv time v(N001) v(N002) v(N003) v(N004) v(N005) v(N006) v(N007)
.endc
.end

```

### spice_emit_report

- Step: `07`
- Role: Report of emitted, skipped and warning components.
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b02\07_spice_emit_report.json`

```json
{
  "circuit_id": "b02",
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
      "N006",
      "N007"
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
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b02\08_spice_run.json`

```json
{
  "source_format": "pipeline2.0_spice_run",
  "status": "success",
  "netlist_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\b02\\07_netlist.cir",
  "command": [
    "C:\\Users\\m.profilo\\Spice64\\bin\\ngspice_con.exe",
    "-b",
    "07_netlist.cir"
  ],
  "exit_code": 0,
  "stdout_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\b02\\08_ngspice_stdout.txt",
  "stderr_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\b02\\08_ngspice_stderr.txt",
  "tran_raw_csv_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\b02\\08_tran_raw.csv",
  "tran_csv_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\b02\\08_tran.csv",
  "tran_plot_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\b02\\08_tran_plot.png",
  "tran_plot_png_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\b02\\08_tran_plot.png",
  "tran_plot_svg_path": null,
  "message": "ngspice completed successfully."
}
```

### ngspice_stdout

- Step: `08`
- Role: Raw ngspice stdout log.
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b02\08_ngspice_stdout.txt`

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
n002                                   4.27402
n003                                   4.27402
n005                                 0.0936194
n004                                  0.769966
n007                                 0.0936194
n006                                  0.769966
vvcc#branch                         -0.0348114


No. of Data Rows : 1008
Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

No. of Data Rows : 1

Initial Transient Solution
--------------------------

Node                                   Voltage
----                                   -------
n001                                         5
n002                                   4.27402
n003                                   4.27402
n005                                 0.0936194
n004                                  0.769966
n007                                 0.0936194
n006                                  0.769966
vvcc#branch                         -0.0348114


No. of Data Rows : 1008
	Node                                  Voltage
	----                                  -------
	----	-------
	n006                             7.699664e-01
	n007                             9.361940e-02
	n004                             7.699664e-01
	n005                             9.361940e-02
	n003                             4.274019e+00
	n002                             4.274019e+00
	n001                             5.000000e+00

	Source	Current
	------	-------

	vvcc#branch                      -3.48114e-02

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
     device   qnpn_transistor18_2   qnpn_transistor18_1
      model                2n3904                2n3904
         ic              0.015483              0.015483
         ib            0.00192274            0.00192274
         ie            -0.0174057            -0.0174057
        vbe              0.748998              0.748998
        vbc              0.672603              0.672603
         gm              0.542628              0.542628
        gpi            0.00437446            0.00437446
        gmu               0.06947               0.06947
         gx                   0.1                   0.1
         go             0.0370062             0.0370062
        cpi            1.7928e-10            1.7928e-10
        cmu           1.22645e-08           1.22645e-08
        cbx                     0                     0
       csub                     0                     0

 Capacitor: Fixed capacitor
     device cpolarized_capacitor2 cpolarized_capacitor2
      model                     C                     C
capacitance               4.7e-05               4.7e-05
      dtemp                     0                     0
     bv_max                 1e+99                 1e+99
          i           6.60087e-17            2.3657e-17
          p          -4.46448e-17          -1.60004e-17

 Diode: Junction Diode model
     device              dled12_2              dled12_1
      model               led_red               led_red
    thermal                     0                     0
         vd              0.725981              0.725981
         id              0.015483              0.015483
         gd              0.598609              0.598609
         cd                     0                     0

 Resistor: Simple linear resistor
     device         rresistor22_4         rresistor22_3         rresistor22_2
      model                     R                     R                     R
 resistance                   270                  2200                  2200
         ac                   270                  2200                  2200
      dtemp                     0                     0                     0
     bv_max                 1e+99                 1e+99                 1e+99
      noisy                     1                     1
```

> Artifact truncated in this preview. The original file remains available through the manifest path.

### ngspice_stderr

- Step: `08`
- Role: Raw ngspice stderr log.
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b02\08_ngspice_stderr.txt`

```text

```

### tran_csv

- Step: `08`
- Role: Clean transient CSV, when .tran data is available.
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b02\08_tran.csv`

```csv
time,v(N001),v(N002),v(N003),v(N004),v(N005),v(N006),v(N007)
0.0,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
1e-05,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
2e-05,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
4e-05,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
8e-05,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.00016,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.00032,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.00064,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.00128,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.00228,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.00328,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.00428,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.00528,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.00628,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.00728,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.00828,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.00928,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.01028,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.01128,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.01228,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.01328,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.01428,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.01528,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.01628,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.01728,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.01828,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.01928,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.02028,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.02128,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.02228,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.02328,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.02428,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.02528,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.02628,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.02728,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.02828,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.02928,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.03028,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.03128,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.03228,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.03328,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.03428,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.03528,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.03628,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.03728,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.03828,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.03928,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.04028,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.04128,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.04228,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.04328,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.04428,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.04528,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.04628,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.04728,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.04828,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.04928,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.05028,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.05128,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.05228,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.05328,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.05428,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.05528,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.05628,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.05728,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.05828,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.05928,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.06028,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.06128,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.06228,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.06328,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.06428,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.06528,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.06628,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.06728,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.06828,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.06928,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.07028,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.07128,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.07228,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.07328,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.07428,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.07528,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.07628,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.07728,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.07828,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.07928,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.08028,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.08128,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.08228,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.08328,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.08428,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.08528,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.08628,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.08728,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.08828,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.08928,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.09028,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.09128,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.09228,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.09328,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.09428,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.09528,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.09628,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.09728,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.09828,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.09928,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.10028,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.10128,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.10228,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.10328,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.10428,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.10528,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.10628,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.10728,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.10828,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.10928,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.11028,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.11128,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.11228,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.11328,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.11428,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.11528,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.11628,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.11728,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.11828,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.11928,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.12028,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.12128,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.12228,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.12328,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.12428,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.12528,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.12628,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.12728,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.12828,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.12928,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.13028,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.13128,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.13228,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.13328,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.13428,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.13528,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.13628,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.13728,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.13828,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.13928,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.14028,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.14128,5.0,4.27401895,4.27401895,0.76996644,0.093619396,0.76996644,0.093619396
0.14228,5.0,4.27401895,4.274018
```

> Artifact truncated in this preview. The original file remains available through the manifest path.
