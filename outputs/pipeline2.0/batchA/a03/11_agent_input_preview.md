# Agent input preview

This file is a local preview of the evidence that will be provided to the read-only diagnostic agent.
No scenario has been executed and no netlist has been modified.

## User problem

Quando alimento il circuito, il sistema non commuta correttamente e la lampada resta spenta. Quale potrebbe essere il problema?

## Circuit

- Batch: `batchA`
- Circuit: `a03`
- Agent mode: `graph_grounded_readonly`

## Technical summary

```json
{
  "spice_status": "failed",
  "spice_exit_code": 1,
  "spice_message": "ngspice exited with errors.",
  "emitted_elements": 9,
  "skipped_elements": 3,
  "emit_warnings_count": 3,
  "skipped_components_count": 3,
  "node_count": 11,
  "ground_groups_count": 0,
  "singleton_nodes_count": 4,
  "bound_components": 9,
  "missing_components": 1,
  "unsupported_components": 2,
  "spice_ready_components": 9,
  "rules_missing_components": 3,
  "has_tran_csv": false,
  "has_tran_plot": false
}
```

## Image policy

- Included by default: `False`
- Can be requested: `True`
- Path: `data\batchA\a03.jpg`
- Policy: Only request the image if structured outputs suggest that the Graph JSON may be incomplete or wrong.

## Agent rules

- Treat this file as a manifest, not as the full diagnostic evidence.
- Load the referenced artifacts needed for the answer.
- Use graph, node map, component rules, netlist, stdout and stderr as evidence.
- Do not invent values, connections, models or simulation results.
- Do not use the image unless image_access is explicitly requested.
- If Graph JSON inconsistency is suspected, explain which structured outputs suggest it.
- In read-only mode, do not modify netlists and do not execute scenarios.

## Loaded artifacts

### graph

- Step: `01`
- Role: Graph JSON copied from Pipeline 1.0.
- Path: `outputs\pipeline2.0\batchA\a03\01_graph.json`

```json
{
  "image_id": "a03",
  "image_name": "a03.jpg",
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
      "component_id": "battery2.2",
      "instance_id": "2.2",
      "class_name": "Battery",
      "terminals": [
        {
          "terminal_id": "battery2.2_positive",
          "name": "positive",
          "relative_position": "top"
        },
        {
          "terminal_id": "battery2.2_negative",
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
      "component_id": "variable_resistor30.1",
      "instance_id": "30.1",
      "class_name": "Variable_Resistor",
      "terminals": [
        {
          "terminal_id": "variable_resistor30.1_t1",
          "name": "t1",
          "relative_position": "top"
        },
        {
          "terminal_id": "variable_resistor30.1_t2",
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
      "component_id": "led12.1",
      "instance_id": "12.1",
      "class_name": "LED",
      "terminals": [
        {
          "terminal_id": "led12.1_cathode",
          "name": "cathode",
          "relative_position": "top"
        },
        {
          "terminal_id": "led12.1_anode",
          "name": "anode",
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
      "component_id": "inductor10.1",
      "instance_id": "10.1",
      "class_name": "Inductor",
      "terminals": [
        {
          "terminal_id": "inductor10.1_t1",
          "name": "t1",
          "relative_position": "top"
        },
        {
          "terminal_id": "inductor10.1_t2",
          "name": "t2",
          "relative_position": "bottom"
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
          "relative_position": "top"
        },
        {
          "terminal_id": "switch25.1_t2",
          "name": "t2",
          "relative_position": "bottom"
        }
      ],
      "state": "closed",
      "state_confidence": 0.95
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
    }
  ],
  "terminal_metadata": {},
  "graph": {
    "battery2.1_negative": [],
    "battery2.1_positive": [
      "inductor10.1_t1",
      "led12.1_cathode",
      "resistor22.2_t1",
      "variable_resistor30.1_t1"
    ],
    "battery2.2_negative": [
      "npn_transistor18.1_E",
      "npn_transistor18.2_E",
      "resistor22.1_t2"
    ],
    "battery2.2_positive": [],
    "inductor10.1_t1": [
      "battery2.1_positive",
      "led12.1_cathode",
      "resistor22.2_t1",
      "variable_resistor30.1_t1"
    ],
    "inductor10.1_t2": [
      "led12.1_anode",
      "npn_transistor18.2_C"
    ],
    "lamp13.1_t1": [
      "signal_source23.1_t2"
    ],
    "lamp13.1_t2": [
      "switch25.1_t2"
    ],
    "led12.1_anode": [
      "inductor10.1_t2",
      "npn_transistor18.2_C"
    ],
    "led12.1_cathode": [
      "battery2.1_positive",
      "inductor10.1_t1",
      "resistor22.2_t1",
      "variable_resistor30.1_t1"
    ],
    "npn_transistor18.1_B": [
      "resistor22.1_t1",
      "variable_resistor30.1_t2"
    ],
    "npn_transistor18.1_C": [
      "npn_transistor18.2_B",
      "resistor22.2_t2"
    ],
    "npn_transistor18.1_E": [
      "battery2.2_negative",
      "npn_transistor18.2_E",
      "resistor22.1_t2"
    ],
    "npn_transistor18.2_B": [
      "npn_transistor18.1_C",
      "resistor22.2_t2"
    ],
    "npn_transistor18.2_C": [
      "inductor10.1_t2",
      "led12.1_anode"
    ],
    "npn_transistor18.2_E": [
      "battery2.2_negative",
      "npn_transistor18.1_E",
      "resistor22.1_t2"
    ],
    "resistor22.1_t1": [
      "npn_transistor18.1_B",
      "variable_resistor30.1_t2"
    ],
    "resistor22.1_t2": [
      "battery2.2_negative",
      "npn_transistor18.1_E",
      "npn_transistor18.2_E"
    ],
    "resistor22.2_t1": [
      "battery2.1_positive",
      "inductor10.1_t1",
      "led12.1_cathode",
      "variable_resistor30.1_t1"
    ],
    "resistor22.2_t2": [
      "npn_transistor18.1_C",
      "npn_transistor18.2_B"
    ],
    "signal_source23.1_t1": [],
    "signal_source23.1_t2": [
      "lamp13.1_t1"
    ],
    "switch25.1_t1": [],
    "switch25.1_t2": [
      "lamp13.1_t2"
    ],
    "variable_resistor30.1_t1": [
      "battery2.1_positive",
      "inductor10.1_t1",
      "led12.1_cathode",
      "resistor22.2_t1"
    ],
    "variable_resistor30.1_t2": [
      "npn_transistor18.1_B",
      "resistor22.1_t1"
    ]
  },
  "warnings": {
    "unconnected_terminals": [
      "battery2.1_negative",
      "battery2.2_positive",
      "signal_source23.1_t1",
      "switch25.1_t1"
    ],
    "unmatched_terminals": [],
    "suspicious_matches": []
  }
}
```

### node_map

- Step: `03`
- Role: Maps component terminals to SPICE node names.
- Path: `outputs\pipeline2.0\batchA\a03\03_node_map.json`

```json
{
  "circuit_id": "a03",
  "source_format": "pipeline2.0_node_map",
  "nodes": [
    {
      "node_id": "N001",
      "kind": "normal",
      "terminals": [
        "battery2.1_negative"
      ],
      "terminal_count": 1
    },
    {
      "node_id": "N002",
      "kind": "normal",
      "terminals": [
        "battery2.1_positive",
        "inductor10.1_t1",
        "led12.1_cathode",
        "resistor22.2_t1",
        "variable_resistor30.1_t1"
      ],
      "terminal_count": 5
    },
    {
      "node_id": "N003",
      "kind": "normal",
      "terminals": [
        "battery2.2_negative",
        "npn_transistor18.1_E",
        "npn_transistor18.2_E",
        "resistor22.1_t2"
      ],
      "terminal_count": 4
    },
    {
      "node_id": "N004",
      "kind": "normal",
      "terminals": [
        "battery2.2_positive"
      ],
      "terminal_count": 1
    },
    {
      "node_id": "N005",
      "kind": "normal",
      "terminals": [
        "inductor10.1_t2",
        "led12.1_anode",
        "npn_transistor18.2_C"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N006",
      "kind": "normal",
      "terminals": [
        "lamp13.1_t1",
        "signal_source23.1_t2"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N007",
      "kind": "normal",
      "terminals": [
        "lamp13.1_t2",
        "switch25.1_t2"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N008",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.1_B",
        "resistor22.1_t1",
        "variable_resistor30.1_t2"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N009",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.1_C",
        "npn_transistor18.2_B",
        "resistor22.2_t2"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N010",
      "kind": "normal",
      "terminals": [
        "signal_source23.1_t1"
      ],
      "terminal_count": 1
    },
    {
      "node_id": "N011",
      "kind": "normal",
      "terminals": [
        "switch25.1_t1"
      ],
      "terminal_count": 1
    }
  ],
  "terminal_to_node": {
    "battery2.1_negative": "N001",
    "battery2.1_positive": "N002",
    "battery2.2_negative": "N003",
    "battery2.2_positive": "N004",
    "inductor10.1_t1": "N002",
    "inductor10.1_t2": "N005",
    "lamp13.1_t1": "N006",
    "lamp13.1_t2": "N007",
    "led12.1_anode": "N005",
    "led12.1_cathode": "N002",
    "npn_transistor18.1_B": "N008",
    "npn_transistor18.1_C": "N009",
    "npn_transistor18.1_E": "N003",
    "npn_transistor18.2_B": "N009",
    "npn_transistor18.2_C": "N005",
    "npn_transistor18.2_E": "N003",
    "resistor22.1_t1": "N008",
    "resistor22.1_t2": "N003",
    "resistor22.2_t1": "N002",
    "resistor22.2_t2": "N009",
    "signal_source23.1_t1": "N010",
    "signal_source23.1_t2": "N006",
    "switch25.1_t1": "N011",
    "switch25.1_t2": "N007",
    "variable_resistor30.1_t1": "N002",
    "variable_resistor30.1_t2": "N008"
  },
  "component_terminal_nodes": {
    "battery2.1": {
      "positive": "N002",
      "negative": "N001"
    },
    "battery2.2": {
      "positive": "N004",
      "negative": "N003"
    },
    "inductor10.1": {
      "t1": "N002",
      "t2": "N005"
    },
    "lamp13.1": {
      "t1": "N006",
      "t2": "N007"
    },
    "led12.1": {
      "cathode": "N002",
      "anode": "N005"
    },
    "npn_transistor18.1": {
      "B": "N008",
      "C": "N009",
      "E": "N003"
    },
    "npn_transistor18.2": {
      "B": "N009",
      "C": "N005",
      "E": "N003"
    },
    "resistor22.1": {
      "t1": "N008",
      "t2": "N003"
    },
    "resistor22.2": {
      "t1": "N002",
      "t2": "N009"
    },
    "signal_source23.1": {
      "t1": "N010",
      "t2": "N006"
    },
    "switch25.1": {
      "t1": "N011",
      "t2": "N007"
    },
    "variable_resistor30.1": {
      "t1": "N002",
      "t2": "N008"
    }
  },
  "warnings": {
    "ground_groups_count": 0,
    "multiple_ground_groups_merged_as_node_0": false,
    "singleton_nodes": [
      "N001",
      "N004",
      "N010",
      "N011"
    ],
    "original_warnings": {
      "unconnected_terminals": [
        "battery2.1_negative",
        "battery2.2_positive",
        "signal_source23.1_t1",
        "switch25.1_t1"
      ],
      "unmatched_terminals": [],
      "suspicious_matches": []
    },
    "normalization_warnings": []
  },
  "stats": {
    "nodes_count": 11,
    "normal_nodes_count": 11,
    "ground_nodes_count": 0,
    "ground_groups_count": 0,
    "terminal_to_node_count": 26,
    "singleton_nodes_count": 4
  }
}
```

### values_bound

- Step: `04`
- Role: Values and labels bound to graph components.
- Path: `outputs\pipeline2.0\batchA\a03\04_values_bound.json`

```json
{
  "circuit_id": "a03",
  "source_format": "pipeline2.0_values_bound",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_manual_values\\batchA\\a03_values.yaml",
  "supplies": {},
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
        "source": "manual_from_image_label",
        "label_text": "B1 12V"
      },
      "status": "bound"
    },
    "battery2.2": {
      "class_name": "Battery",
      "terminal_nodes": {
        "positive": "N004",
        "negative": "N003"
      },
      "value_data": {
        "type": "dc",
        "value": 12,
        "unit": "V",
        "source": "manual_from_image_label",
        "label_text": "B1 12V"
      },
      "status": "bound"
    },
    "inductor10.1": {
      "class_name": "Inductor",
      "terminal_nodes": {
        "t1": "N002",
        "t2": "N005"
      },
      "value_data": {
        "rated_voltage": 12,
        "unit": "V",
        "source": "manual_from_image_label",
        "label_text": "RL1 12V"
      },
      "status": "unsupported_for_now"
    },
    "lamp13.1": {
      "class_name": "Lamp",
      "terminal_nodes": {
        "t1": "N006",
        "t2": "N007"
      },
      "value_data": {
        "nominal_voltage": 220,
        "unit": "V",
        "source": "manual_from_image_label",
        "label_text": "L1 220V"
      },
      "status": "missing"
    },
    "led12.1": {
      "class_name": "LED",
      "terminal_nodes": {
        "cathode": "N002",
        "anode": "N005"
      },
      "value_data": {
        "model": "LED_RED",
        "source": "manual_from_image_label",
        "label_text": "D1 DIODE"
      },
      "status": "bound"
    },
    "npn_transistor18.1": {
      "class_name": "NPN_Transistor",
      "terminal_nodes": {
        "B": "N008",
        "C": "N009",
        "E": "N003"
      },
      "value_data": {
        "model": "BC547",
        "source": "manual_from_image_label",
        "label_text": "Q1 BC547"
      },
      "status": "bound"
    },
    "npn_transistor18.2": {
      "class_name": "NPN_Transistor",
      "terminal_nodes": {
        "B": "N009",
        "C": "N005",
        "E": "N003"
      },
      "value_data": {
        "model": "BC547",
        "source": "manual_from_image_label",
        "label_text": "Q2 BC547"
      },
      "status": "bound"
    },
    "resistor22.1": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N008",
        "t2": "N003"
      },
      "value_data": {
        "value": 100,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "RV1 100k"
      },
      "status": "bound"
    },
    "resistor22.2": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N002",
        "t2": "N009"
      },
      "value_data": {
        "value": 1,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R1 1k"
      },
      "status": "bound"
    },
    "signal_source23.1": {
      "class_name": "Signal_Source",
      "terminal_nodes": {
        "t1": "N010",
        "t2": "N006"
      },
      "value_data": {
        "type": "ac",
        "value": 220,
        "unit": "V",
        "source": "manual_from_image_label",
        "label_text": "V1 220VAC"
      },
      "status": "bound"
    },
    "switch25.1": {
      "class_name": "Switch",
      "terminal_nodes": {
        "t1": "N011",
        "t2": "N007"
      },
      "value_data": {
        "state": "closed",
        "state_source": "graph_json_state",
        "state_confidence": 0.95,
        "label": "RL1_CONTACT",
        "source": "manual_from_image_label",
        "label_text": "RL1"
      },
      "status": "bound"
    },
    "variable_resistor30.1": {
      "class_name": "Variable_Resistor",
      "terminal_nodes": {
        "t1": "N002",
        "t2": "N008"
      },
      "value_data": {
        "label": "LDR",
        "source": "manual_from_image_label",
        "label_text": "LDR SENSOR"
      },
      "status": "unsupported_for_now"
    }
  },
  "nodes": {},
  "simulation": {
    "analyses": [
      "op"
    ]
  },
  "missing": [
    {
      "component_id": "lamp13.1",
      "class_name": "Lamp",
      "required": [
        "equivalent_resistance",
        "value"
      ]
    }
  ],
  "stats": {
    "components_total": 12,
    "bound_components": 9,
    "missing_components": 1,
    "not_required_components": 0,
    "unsupported_components": 2,
    "supplies_count": 0,
    "manual_nodes_count": 0
  }
}
```

### component_rules

- Step: `06`
- Role: SPICE conversion rules for each component.
- Path: `outputs\pipeline2.0\batchA\a03\06_component_rules.json`

```json
{
  "circuit_id": "a03",
  "source_format": "pipeline2.0_component_rules",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_manual_values\\batchA\\a03_values.yaml",
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
        "N002",
        "N001"
      ],
      "parameters": {
        "type": "dc",
        "value": 12,
        "unit": "V",
        "source": "manual_from_image_label",
        "label_text": "B1 12V"
      }
    },
    "battery2.2": {
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
        "N004",
        "N003"
      ],
      "parameters": {
        "type": "dc",
        "value": 12,
        "unit": "V",
        "source": "manual_from_image_label",
        "label_text": "B1 12V"
      }
    },
    "inductor10.1": {
      "class_name": "Inductor",
      "status": "missing_parameters",
      "spice_support": "direct",
      "missing_fields": [
        "value"
      ]
    },
    "lamp13.1": {
      "class_name": "Lamp",
      "status": "missing_parameters",
      "spice_support": "equivalent",
      "missing_fields": [
        "equivalent_resistance"
      ]
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
        "N002"
      ],
      "parameters": {
        "model": "LED_RED",
        "source": "manual_from_image_label",
        "label_text": "D1 DIODE"
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
        "N009",
        "N008",
        "N003"
      ],
      "parameters": {
        "model": "BC547",
        "source": "manual_from_image_label",
        "label_text": "Q1 BC547"
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
        "N005",
        "N009",
        "N003"
      ],
      "parameters": {
        "model": "BC547",
        "source": "manual_from_image_label",
        "label_text": "Q2 BC547"
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
        "N008",
        "N003"
      ],
      "parameters": {
        "value": 100,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "RV1 100k"
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
        "N009"
      ],
      "parameters": {
        "value": 1,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R1 1k"
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
        "N010",
        "N006"
      ],
      "parameters": {
        "type": "ac",
        "value": 220,
        "unit": "V",
        "source": "manual_from_image_label",
        "label_text": "V1 220VAC"
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
        "N011",
        "N007"
      ],
      "parameters": {
        "state": "closed",
        "state_source": "graph_json_state",
        "state_confidence": 0.95,
        "label": "RL1_CONTACT",
        "source": "manual_from_image_label",
        "label_text": "RL1"
      },
      "strategy": "short_circuit"
    },
    "variable_resistor30.1": {
      "class_name": "Variable_Resistor",
      "status": "missing_parameters",
      "spice_support": "equivalent",
      "missing_fields": [
        "equivalent_resistance"
      ]
    }
  },
  "simulation": {
    "analyses": [
      "op"
    ]
  },
  "stats": {
    "components_total": 12,
    "spice_ready_components": 9,
    "not_emitted_components": 0,
    "measurement_components": 0,
    "missing_components": 3,
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
- Path: `outputs\pipeline2.0\batchA\a03\07_netlist.cir`

```spice
* pipeline2.0 netlist
* circuit: a03

Vbattery2_1 N002 N001 DC 12
Vbattery2_2 N004 N003 DC 12
Dled12_1 N005 N002 LED_RED
Qnpn_transistor18_1 N009 N008 N003 BC547
Qnpn_transistor18_2 N005 N009 N003 BC547
Rresistor22_1 N008 N003 100k
Rresistor22_2 N002 N009 1k
Vsignal_source23_1 N010 N006 AC 220
Rswitch25_1 N011 N007 1m

.model BC547 NPN
.model LED_RED D

.op
.end

```

### spice_emit_report

- Step: `07`
- Role: Report of emitted, skipped and warning components.
- Path: `outputs\pipeline2.0\batchA\a03\07_spice_emit_report.json`

```json
{
  "circuit_id": "a03",
  "source_format": "pipeline2.0_spice_emit_report",
  "emitted_elements": 9,
  "skipped_elements": 3,
  "skipped_components": [
    "inductor10.1",
    "lamp13.1",
    "variable_resistor30.1"
  ],
  "informational_skips": [],
  "measurement_points": [],
  "analyses": [
    "op"
  ],
  "transient_export": {
    "path": null,
    "nodes": []
  },
  "models": [
    "BC547",
    "LED_RED"
  ],
  "warnings": [
    "inductor10.1: missing parameters for SPICE emission",
    "lamp13.1: missing parameters for SPICE emission",
    "variable_resistor30.1: missing parameters for SPICE emission"
  ]
}
```

### spice_run

- Step: `08`
- Role: Structured ngspice execution report.
- Path: `outputs\pipeline2.0\batchA\a03\08_spice_run.json`

```json
{
  "source_format": "pipeline2.0_spice_run",
  "status": "failed",
  "netlist_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a03\\07_netlist.cir",
  "command": [
    "C:\\Users\\m.profilo\\Spice64\\bin\\ngspice_con.exe",
    "-b",
    "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a03\\07_netlist.cir"
  ],
  "exit_code": 1,
  "stdout_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a03\\08_ngspice_stdout.txt",
  "stderr_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a03\\08_ngspice_stderr.txt",
  "tran_raw_csv_path": null,
  "tran_csv_path": null,
  "tran_plot_path": null,
  "tran_plot_png_path": null,
  "tran_plot_svg_path": null,
  "message": "ngspice exited with errors."
}
```

### ngspice_stdout

- Step: `08`
- Role: Raw ngspice stdout log.
- Path: `outputs\pipeline2.0\batchA\a03\08_ngspice_stdout.txt`

```text

Note: No compatibility mode selected!


Circuit: * pipeline2.0 netlist

Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

DC solution failed -

Last Node Voltages
------------------

Node                                   Last Voltage        Previous Iter
----                                   ------------        -------------
n002                                              0            -nan(ind)
n001                                              0                    0
n004                                              0                    0
n003                                              0            -nan(ind)
n005                                              0            -nan(ind)
n009                                              0            -nan(ind)
n008                                              0                  nan
n010                                              0                    0
n006                                              0                    0
n011                                              0                    0
n007                                              0                    0
vsignal_source23_1#branch                         0                    0
vbattery2_2#branch                                0                   12 *
vbattery2_1#branch                                0                   12 *


Total analysis time (seconds) = 0.0085063

Total elapsed time (seconds) = 0.046 

Total DRAM available = 32239.535 MB.
DRAM currently available = 16429.074 MB.
Maximum ngspice program size =   15.266 MB.
Current ngspice program size =   15.266 MB.


```

### ngspice_stderr

- Step: `08`
- Role: Raw ngspice stderr log.
- Path: `outputs\pipeline2.0\batchA\a03\08_ngspice_stderr.txt`

```text
Note: vsignal_source23_1: has no value, DC 0 assumed
Warning: singular matrix:  check node n007

Note: Starting dynamic gmin stepping
Warning: singular matrix:  check node n006

Warning: singular matrix:  check node n006

Warning: singular matrix:  check node n006

Warning: singular matrix:  check node n006

Warning: singular matrix:  check node n006

Warning: Dynamic gmin stepping failed
Note: Starting true gmin stepping
Warning: True gmin stepping failed
Note: Starting source stepping
Warning: source stepping failed
Note: Transient op started
Error: Transient op failed, timestep too small


Error: The operating point could not be simulated successfully.
    Any of the following steps may fail.!

doAnalyses: OP:  Timestep too small; trouble with led_red-instance dled12_1


run simulation(s) aborted

```

### tran_csv

Artifact not available.
