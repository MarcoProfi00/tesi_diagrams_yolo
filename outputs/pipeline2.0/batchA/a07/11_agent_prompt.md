# Diagnostic agent prompt

## System instructions

- You are a read-only diagnostic assistant for electronic circuits.
- Your task is to explain the Pipeline 2.0 and ngspice results using only the provided evidence.
- The final answer must be written in Italian.
- Keep technical identifiers exactly as provided, for example node names, component IDs and file names.
- Do not invent component values, electrical connections, SPICE models, node voltages, currents or simulation results.
- Do not assume that a component exists if it is not present in the Graph JSON or in the generated netlist.
- Do not modify the netlist, do not execute SPICE and do not apply scenarios.
- Diagnostic scenarios may be suggested only as future SPICE-verifiable hypotheses, not as already verified facts.
- Use general electronics and SPICE knowledge only to interpret the provided evidence, not to create missing evidence.
- If the evidence is insufficient, say exactly what is missing.
- Do not describe a branch as floating unless the evidence shows a floating or singleton node with no DC reference path.
- If a branch has a resistive path to ground but no active source, describe it as not driven or not powered.

## Operating rules

- Treat the evidence sections below as the only technical evidence available in this prompt.
- When useful, cite component IDs, node IDs, file names or artifact sections.
- Use the original artifact paths only as traceability references.
- If an artifact is missing or truncated, mention the limitation before drawing conclusions from it.
- Do not use the original image unless the structured evidence suggests that the Graph JSON may be wrong.
- If image access is needed, explain which structured evidence justifies it.
- Request image access only for strong structured reasons: Graph JSON warnings, suspicious or missing connections, important singleton nodes, missing critical components, unsupported critical topology, or ngspice failure caused by topology/convergence issues.
- If ngspice succeeds and graph/node-map evidence is internally coherent, do not request the image by default.
- In read-only mode, do not modify netlists, do not change values and do not execute scenarios.
- A diagnostic scenario is a controlled hypothesis that can be verified by generating a scenario-specific Pipeline 2.0 run and rerunning ngspice.
- A scenario must never overwrite the original Pipeline 2.0 outputs.
- A scenario must start from copied base artifacts, modify only the scenario copies, and save separate scenario artifacts for comparison.
- Scenario artifacts must be created only after the user explicitly chooses one proposed scenario to execute.
- Suggest at most 3 candidate scenarios, ordered from simplest to most informative.
- Each scenario must be readable by a non-SPICE user first, and machine-oriented only in a short technical block after the explanation.
- The user-facing scenario title should describe the diagnostic idea naturally, for example `Alimentare il ramo della lampada`, not only `drive_node_voltage`.
- The technical block should be concise and should not replace the human explanation.
- Prefer natural scenarios that directly test the user's symptom using existing nodes, states and values before proposing graph-correction scenarios.
- Prefer acting on existing external inputs, supply labels, connector pins and recognized component states before directly forcing internal load nodes.
- If an upstream input node feeds a load, drive the upstream input first; direct forcing of the load node is a later model-isolation test, not an early natural scenario.
- The top 3 scenarios should be independently executable: if a scenario needs another action first, include that action in the same scenario JSON or present it only as a later follow-up.
- Do not propose `run_tran` alone when the base operating point does not power the relevant branch; include the required drive/source/state actions in the same scenario.
- If ngspice succeeds and graph/node-map evidence is internally coherent, the first scenarios should be value, source, analysis or state tests, not topology rewrites.
- Avoid `connect_nodes`, `disconnect_terminal` and `move_terminal` in the top 3 scenarios unless structured evidence strongly suggests a graph/topology error.
- If topology repair is only a later possibility, mention it as a next step instead of making it one of the first 3 scenarios.
- Do not propose graph-correction scenarios in the top 3 unless there is strong structured evidence that the Graph JSON is wrong.
- Scenarios can be iterative: if one scenario does not explain the problem, propose the next one or a combination of previous validated assumptions.

## User problem

Il trasformatore sembra funzionare, ma il LED di alimentazione non si accende. Quale potrebbe essere il problema?

## Circuit metadata

- Batch: `batchA`
- Circuit: `a07`
- Agent mode: `graph_grounded_readonly`

## Technical summary

```json
{
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_message": "ngspice completed successfully.",
  "emitted_elements": 3,
  "skipped_elements": 6,
  "emit_warnings_count": 2,
  "skipped_components_count": 6,
  "node_count": 7,
  "ground_groups_count": 4,
  "singleton_nodes_count": 2,
  "bound_components": 4,
  "missing_components": 0,
  "unsupported_components": 0,
  "spice_ready_components": 4,
  "rules_missing_components": 0,
  "has_tran_csv": true,
  "has_tran_plot": true
}
```

## Available artifacts

- `graph`: available, path=`outputs\pipeline2.0\batchA\a07\01_graph.json`
- `normalized_circuit`: available, path=`outputs\pipeline2.0\batchA\a07\02_normalized_circuit.json`
- `node_map`: available, path=`outputs\pipeline2.0\batchA\a07\03_node_map.json`
- `values_bound`: available, path=`outputs\pipeline2.0\batchA\a07\04_values_bound.json`
- `component_rules`: available, path=`outputs\pipeline2.0\batchA\a07\06_component_rules.json`
- `netlist`: available, path=`outputs\pipeline2.0\batchA\a07\07_netlist.cir`
- `spice_emit_report`: available, path=`outputs\pipeline2.0\batchA\a07\07_spice_emit_report.json`
- `spice_run`: available, path=`outputs\pipeline2.0\batchA\a07\08_spice_run.json`
- `ngspice_stdout`: available, path=`outputs\pipeline2.0\batchA\a07\08_ngspice_stdout.txt`
- `ngspice_stderr`: available, path=`outputs\pipeline2.0\batchA\a07\08_ngspice_stderr.txt`
- `tran_csv`: available, path=`outputs\pipeline2.0\batchA\a07\08_tran.csv`
- `tran_plot_png`: available, path=`outputs\pipeline2.0\batchA\a07\08_tran_plot.png`
- `tran_plot_svg`: missing, path=`None`

## Image access policy

- Included by default: `False`
- Can be requested: `True`
- Path: `data\batchA\a07.png`
- Policy: Only request the image if structured outputs suggest that the Graph JSON may be incomplete or wrong.

## Diagnostic scenario meaning

A diagnostic scenario is not generic advice.
It is a future, controlled, SPICE-verifiable test used to check whether a suspected cause explains the user's problem.

Conceptual flow:

```text
base Pipeline 2.0 outputs
-> agent proposes a diagnostic scenario
-> pipeline validates the scenario
-> pipeline creates separate scenario artifacts
-> ngspice runs on the scenario netlist
-> base result and scenario result are compared
-> the agent updates the diagnosis
```

The base circuit must remain unchanged.
A scenario run must be saved separately from the base run.
In the read-only agent step, scenarios are only proposed. No scenario folder, copied artifact or modified netlist should be created yet.
Scenario artifacts should be created later only when the user selects a specific proposed scenario, for example scenario 1, 2 or 3.
The scenario runner should copy the original artifacts into a scenario-specific folder, then apply controlled modifications only to those copies.
Original files such as `01_graph.json`, `03_node_map.json`, `04_values_bound.json`, `07_netlist.cir` and `08_spice_run.json` must remain unchanged.

Scenario priority:

1. Prefer the least invasive scenario that directly tests the observed symptom.
2. Prefer actions on existing connector pins, supply labels, source values and recognized switch states before forcing internal load nodes.
3. Prefer value/source/analysis/state scenarios before topology repair when the graph is coherent.
4. Test individual hypotheses before proposing combined scenarios.
5. Use combined scenarios only after the individual assumptions are meaningful, and include every required action in the same JSON block.
6. Use graph-correction or topology-rewrite scenarios only when graph or SPICE evidence strongly supports a recognition/topology error.

Naturalness caution:

- If a load is fed through an upstream resistor or connector node, prefer driving that upstream node before directly driving the load terminal.
- Directly driving a load terminal is useful only as a later isolation test for the load model, not as one of the first natural scenarios when an upstream input exists.
- If an existing switch is recognized, a scenario that opens/closes that switch is usually more natural than inventing a new internal drive point.
- A scenario must be executable on its own. Avoid wording such as `after scenario 1, run .tran` unless the technical JSON also includes the actions from scenario 1.
- If `.tran` is useful, make it part of a complete scenario, for example drive a node and run transient analysis in the same scenario.

Topology caution:

- `connect_nodes`, `disconnect_terminal` and `move_terminal` are topology-rewrite actions.
- Do not put topology-rewrite actions in the first 3 scenarios when ngspice succeeds and the graph/node map are coherent.
- In that case, propose electrical tests first, for example driving an input node, changing a source value, closing an existing switch or running another analysis.
- If topology may still be relevant, mention it as a possible later step after simpler scenarios are tested.
- If ngspice fails, nodes are floating/singleton, critical components are missing, or Graph JSON warnings indicate recognition problems, topology-rewrite scenarios can be proposed earlier.

Scenario presentation format:

- Start with a natural title that a user can understand.
- Explain why the scenario is proposed using concrete evidence from the base run.
- Explain what would be changed in simple words.
- Explain what SPICE result would confirm or reject the hypothesis.
- End the scenario with a short technical JSON block for the future pipeline.
- Keep the technical block small: it is a controlled hint for automation, not the main answer.

Example technical block shape:

```json
{
  "scenario_id": "scenario_1",
  "title": "Alimentare il ramo della lampada",
  "hypothesis": "The lamp branch is inactive because its input node is not driven.",
  "actions": [
    {
      "type": "drive_node_voltage",
      "target": "N002",
      "value": "5V"
    }
  ],
  "rerun_from": "04",
  "analysis": "op",
  "compare": ["v(N002)", "v(N004)", "i(Rlamp13_1)"]
}
```

When proposing a scenario, reason about which part of the pipeline would need to be rerun.

Pipeline rerun guidance:

- If the scenario only changes a value, source amplitude, model parameter or analysis command, it may reuse `01_graph.json`, `02_normalized_circuit.json` and `03_node_map.json`, then regenerate from `04_values.py`, `06_component_rules.py`, `07_spice_emit.py` and `08_spice_run.py` as needed.
- If the scenario changes the state of an already recognized component, for example closing an existing switch, it should create a scenario layer and then rerun the first affected step through `08`.
- If the scenario combines actions, for example driving an input node and closing a switch, list both actions in the same JSON block so the scenario is self-contained.
- If the scenario adds `.tran`, include the required electrical setup actions in the same scenario when the base circuit does not already energize the branch of interest.
- If the scenario changes electrical topology, for example connecting/disconnecting nodes, it should be treated as topology-rewrite and used only when justified by the evidence.
- If the scenario requires correcting the recognized Graph JSON itself, it is not just a normal electrical scenario. It should be treated as a graph-correction scenario, saved as a copied/modified scenario graph, and may need to restart from `01_io.py` or an equivalent scenario-specific graph input.
- If the evidence only suggests a possible Graph JSON error but does not prove it, request image access instead of silently changing the graph.

Image request policy:

- Request the image when ngspice fails because the generated circuit is not electrically meaningful, for example singular matrix, floating nodes or topology-related convergence failure.
- Request the image when Graph JSON warnings or node-map evidence indicate likely recognition errors.
- Do not request the image just because a circuit branch is inactive in a successful and coherent SPICE run.
- If image inspection would merely be useful for human confirmation, say so in the limitations but keep `Richiede immagine: no`.

Do not directly decide implementation details as facts. State them as expected future pipeline behavior.
For every scenario, state what should be compared between the base run and scenario run, for example node voltage, branch current, SPICE convergence, emitted/skipped components, stdout/stderr changes, transient waveform or load current.

## Evidence to analyze

### graph

- Role: Graph JSON copied from Pipeline 1.0.
- Path: `outputs\pipeline2.0\batchA\a07\01_graph.json`

```json
{
  "image_id": "a07",
  "image_name": "a07.png",
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
      "component_id": "transformer28.1",
      "instance_id": "28.1",
      "class_name": "Transformer",
      "terminals": [
        {
          "terminal_id": "transformer28.1_t1",
          "name": "t1",
          "relative_position": "left"
        },
        {
          "terminal_id": "transformer28.1_t2",
          "name": "t2",
          "relative_position": "right"
        },
        {
          "terminal_id": "transformer28.1_t3",
          "name": "t3",
          "relative_position": "left"
        },
        {
          "terminal_id": "transformer28.1_t4",
          "name": "t4",
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
      "transformer28.1_t4"
    ],
    "analog_meter0.1_t2": [
      "gnd9.3_t1",
      "led12.1_anode",
      "resistor22.1_t2"
    ],
    "connector5.1_pin1": [
      "transformer28.1_t3"
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
      "analog_meter0.1_t2",
      "led12.1_anode",
      "resistor22.1_t2"
    ],
    "gnd9.4_t1": [
      "led12.1_cathode"
    ],
    "led12.1_anode": [
      "analog_meter0.1_t2",
      "gnd9.3_t1",
      "resistor22.1_t2"
    ],
    "led12.1_cathode": [
      "gnd9.4_t1"
    ],
    "resistor22.1_t1": [
      "connector5.1_pin2"
    ],
    "resistor22.1_t2": [
      "analog_meter0.1_t2",
      "gnd9.3_t1",
      "led12.1_anode"
    ],
    "switch25.1_t1": [
      "gnd9.1_t1"
    ],
    "switch25.1_t2": [
      "connector5.1_pin3"
    ],
    "transformer28.1_t1": [],
    "transformer28.1_t2": [],
    "transformer28.1_t3": [
      "connector5.1_pin1"
    ],
    "transformer28.1_t4": [
      "analog_meter0.1_t1"
    ]
  },
  "warnings": {
    "unconnected_terminals": [
      "transformer28.1_t1",
      "transformer28.1_t2"
    ],
    "unmatched_terminals": [],
    "suspicious_matches": []
  }
}
```

### node_map

- Role: Maps component terminals to SPICE node names.
- Path: `outputs\pipeline2.0\batchA\a07\03_node_map.json`

```json
{
  "circuit_id": "a07",
  "source_format": "pipeline2.0_node_map",
  "nodes": [
    {
      "node_id": "0",
      "kind": "ground",
      "terminals": [
        "analog_meter0.1_t2",
        "connector5.1_pin4",
        "gnd9.1_t1",
        "gnd9.2_t1",
        "gnd9.3_t1",
        "gnd9.4_t1",
        "led12.1_anode",
        "led12.1_cathode",
        "resistor22.1_t2",
        "switch25.1_t1"
      ],
      "terminal_count": 10,
      "source_groups": [
        [
          "analog_meter0.1_t2",
          "gnd9.3_t1",
          "led12.1_anode",
          "resistor22.1_t2"
        ],
        [
          "connector5.1_pin4",
          "gnd9.2_t1"
        ],
        [
          "gnd9.1_t1",
          "switch25.1_t1"
        ],
        [
          "gnd9.4_t1",
          "led12.1_cathode"
        ]
      ]
    },
    {
      "node_id": "N001",
      "kind": "normal",
      "terminals": [
        "analog_meter0.1_t1",
        "transformer28.1_t4"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N002",
      "kind": "normal",
      "terminals": [
        "connector5.1_pin1",
        "transformer28.1_t3"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N003",
      "kind": "normal",
      "terminals": [
        "connector5.1_pin2",
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
    },
    {
      "node_id": "N005",
      "kind": "normal",
      "terminals": [
        "transformer28.1_t1"
      ],
      "terminal_count": 1
    },
    {
      "node_id": "N006",
      "kind": "normal",
      "terminals": [
        "transformer28.1_t2"
      ],
      "terminal_count": 1
    }
  ],
  "terminal_to_node": {
    "analog_meter0.1_t1": "N001",
    "analog_meter0.1_t2": "0",
    "connector5.1_pin1": "N002",
    "connector5.1_pin2": "N003",
    "connector5.1_pin3": "N004",
    "connector5.1_pin4": "0",
    "gnd9.1_t1": "0",
    "gnd9.2_t1": "0",
    "gnd9.3_t1": "0",
    "gnd9.4_t1": "0",
    "led12.1_anode": "0",
    "led12.1_cathode": "0",
    "resistor22.1_t1": "N003",
    "resistor22.1_t2": "0",
    "switch25.1_t1": "0",
    "switch25.1_t2": "N004",
    "transformer28.1_t1": "N005",
    "transformer28.1_t2": "N006",
    "transformer28.1_t3": "N002",
    "transformer28.1_t4": "N001"
  },
  "component_terminal_nodes": {
    "analog_meter0.1": {
      "t1": "N001",
      "t2": "0"
    },
    "connector5.1": {
      "pin1": "N002",
      "pin2": "N003",
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
    "led12.1": {
      "anode": "0",
      "cathode": "0"
    },
    "resistor22.1": {
      "t1": "N003",
      "t2": "0"
    },
    "switch25.1": {
      "t1": "0",
      "t2": "N004"
    },
    "transformer28.1": {
      "t1": "N005",
      "t2": "N006",
      "t3": "N002",
      "t4": "N001"
    }
  },
  "warnings": {
    "ground_groups_count": 4,
    "multiple_ground_groups_merged_as_node_0": true,
    "singleton_nodes": [
      "N005",
      "N006"
    ],
    "original_warnings": {
      "unconnected_terminals": [
        "transformer28.1_t1",
        "transformer28.1_t2"
      ],
      "unmatched_terminals": [],
      "suspicious_matches": []
    },
    "normalization_warnings": []
  },
  "stats": {
    "nodes_count": 7,
    "normal_nodes_count": 6,
    "ground_nodes_count": 1,
    "ground_groups_count": 4,
    "terminal_to_node_count": 20,
    "singleton_nodes_count": 2
  }
}
```

### values_bound

- Role: Values and labels bound to graph components.
- Path: `outputs\pipeline2.0\batchA\a07\04_values_bound.json`

```json
{
  "circuit_id": "a07",
  "source_format": "pipeline2.0_values_bound",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_manual_values\\batchA\\a07_values.yaml",
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
        "measured_quantity": "voltage_ac",
        "input_resistance": 10000000,
        "resistance_unit": "ohm",
        "label": "VAC",
        "source": "manual_from_image_label",
        "label_text": "VAC"
      },
      "status": "not_required"
    },
    "connector5.1": {
      "class_name": "Connector",
      "terminal_nodes": {
        "pin1": "N002",
        "pin2": "N003",
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
    "led12.1": {
      "class_name": "LED",
      "terminal_nodes": {
        "anode": "0",
        "cathode": "0"
      },
      "value_data": {
        "model": "LED_RED",
        "source": "manual_assumption",
        "label_text": "PWR"
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
        "value": 680,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "680R"
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
        "label_text": "RESET"
      },
      "status": "bound"
    },
    "transformer28.1": {
      "class_name": "Transformer",
      "terminal_nodes": {
        "t1": "N005",
        "t2": "N006",
        "t3": "N002",
        "t4": "N001"
      },
      "value_data": {
        "model": "equivalent_ac_source",
        "secondary_voltage_rms": 12,
        "unit": "V",
        "frequency": 50,
        "frequency_unit": "Hz",
        "source": "manual_from_image_label",
        "label_text": "T1 12 V AC"
      },
      "status": "bound"
    }
  },
  "nodes": {
    "connector5.1_pin1": {
      "label": "TRANSFORMER_INPUT",
      "source": "inferred_from_transformer_branch",
      "node": "N002"
    },
    "connector5.1_pin2": {
      "label": "PWR",
      "source": "manual_from_image_label",
      "label_text": "PWR",
      "node": "N003"
    },
    "connector5.1_pin3": {
      "label": "RESET",
      "source": "manual_from_image_label",
      "label_text": "RESET",
      "node": "N004"
    },
    "connector5.1_pin4": {
      "label": "GND",
      "spice_node": 0,
      "source": "graph_json_gnd",
      "node": "0"
    }
  },
  "simulation": {
    "analyses": [
      "op",
      "tran"
    ],
    "tran": {
      "step": "0.1ms",
      "stop": "40ms"
    }
  },
  "missing": [],
  "stats": {
    "components_total": 10,
    "bound_components": 4,
    "missing_components": 0,
    "not_required_components": 6,
    "unsupported_components": 0,
    "supplies_count": 0,
    "manual_nodes_count": 4
  }
}
```

### component_rules

- Role: SPICE conversion rules for each component.
- Path: `outputs\pipeline2.0\batchA\a07\06_component_rules.json`

```json
{
  "circuit_id": "a07",
  "source_format": "pipeline2.0_component_rules",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_manual_values\\batchA\\a07_values.yaml",
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
        "measured_quantity": "voltage_ac",
        "input_resistance": 10000000,
        "resistance_unit": "ohm",
        "label": "VAC",
        "source": "manual_from_image_label",
        "label_text": "VAC"
      },
      "reason": "Voltmeter/probe only: not emitted as a physical SPICE component; read the voltage between its nodes."
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
        "0",
        "0"
      ],
      "parameters": {
        "model": "LED_RED",
        "source": "manual_assumption",
        "label_text": "PWR"
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
        "value": 680,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "680R"
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
        "label_text": "RESET"
      },
      "strategy": "open_circuit"
    },
    "transformer28.1": {
      "class_name": "Transformer",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "V",
      "emit_as": "equivalent_ac_source",
      "node_order": [
        "t3",
        "t4"
      ],
      "nodes": [
        "N002",
        "N001"
      ],
      "parameters": {
        "model": "equivalent_ac_source",
        "secondary_voltage_rms": 12,
        "unit": "V",
        "frequency": 50,
        "frequency_unit": "Hz",
        "source": "manual_from_image_label",
        "label_text": "T1 12 V AC"
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
      "stop": "40ms"
    }
  },
  "stats": {
    "components_total": 10,
    "spice_ready_components": 4,
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

- Role: Generated SPICE netlist.
- Path: `outputs\pipeline2.0\batchA\a07\07_netlist.cir`

```spice
* pipeline2.0 netlist
* circuit: a07

Rmeter_analog_meter0_1 N001 0 10000000
Rresistor22_1 N003 0 680
* switch25.1 open: not emitted
Vtransformer28_1 N002 N001 SIN(0 16.9706 50)

.op
.save all
.tran 0.1ms 40ms

.control
set wr_singlescale
set wr_vecnames
run
wrdata 08_tran.csv time v(N001) v(N002) v(N003)
.endc
.end

```

### spice_emit_report

- Role: Report of emitted, skipped and warning components.
- Path: `outputs\pipeline2.0\batchA\a07\07_spice_emit_report.json`

```json
{
  "circuit_id": "a07",
  "source_format": "pipeline2.0_spice_emit_report",
  "emitted_elements": 3,
  "skipped_elements": 6,
  "skipped_components": [
    "connector5.1",
    "gnd9.1",
    "gnd9.2",
    "gnd9.3",
    "gnd9.4",
    "led12.1"
  ],
  "informational_skips": [
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
    "op",
    "tran"
  ],
  "transient_export": {
    "path": "08_tran.csv",
    "nodes": [
      "N001",
      "N002",
      "N003"
    ]
  },
  "models": [],
  "warnings": [
    "led12.1: terminals collapse to the same SPICE node; not emitted",
    "switch25.1: open switch not emitted"
  ]
}
```

### spice_run

- Role: Structured ngspice execution report.
- Path: `outputs\pipeline2.0\batchA\a07\08_spice_run.json`

```json
{
  "source_format": "pipeline2.0_spice_run",
  "status": "success",
  "netlist_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a07\\07_netlist.cir",
  "command": [
    "C:\\Users\\m.profilo\\Spice64\\bin\\ngspice_con.exe",
    "-b",
    "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a07\\07_netlist.cir"
  ],
  "exit_code": 0,
  "stdout_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a07\\08_ngspice_stdout.txt",
  "stderr_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a07\\08_ngspice_stderr.txt",
  "tran_raw_csv_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a07\\08_tran_raw.csv",
  "tran_csv_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a07\\08_tran.csv",
  "tran_plot_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a07\\08_tran_plot.png",
  "tran_plot_png_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a07\\08_tran_plot.png",
  "tran_plot_svg_path": null,
  "message": "ngspice completed successfully."
}
```

### ngspice_stdout

- Role: Raw ngspice stdout log.
- Path: `outputs\pipeline2.0\batchA\a07\08_ngspice_stdout.txt`

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
n003                                         0
n002                                         0
vtransformer28_1#branch                      0


No. of Data Rows : 408
Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

No. of Data Rows : 1

Initial Transient Solution
--------------------------

Node                                   Voltage
----                                   -------
n001                                         0
n003                                         0
n002                                         0
vtransformer28_1#branch                      0


No. of Data Rows : 408
	Node                                  Voltage
	----                                  -------
	----	-------
	n002                             0.000000e+00
	n003                             0.000000e+00
	n001                             0.000000e+00

	Source	Current
	------	-------

	vtransformer28_1#branch          0.000000e+00

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

 Resistor: Simple linear resistor
     device         rresistor22_1 rmeter_analog_meter0_
      model                     R                     R
 resistance                   680                 1e+07
         ac                   680                 1e+07
      dtemp                     0                     0
     bv_max                 1e+99                 1e+99
      noisy                     1                     1
          i                     0                     0
          p                     0                     0

 Vsource: Independent voltage source
     device      vtransformer28_1
         dc                     0
      acmag                     0
      pulse                     0
                          16.9706
                               50
        sin                     0
                          16.9706
                               50
        exp                     0
                          16.9706
                               50
        pwl                     0
                          16.9706
                               50
       sffm                     0
                          16.9706
                               50
         am                     0
                          16.9706
                               50
    trnoise                     0
                          16.9706
                               50
   trrandom                     0
                          16.9706
                               50
    portnum                     0
         z0                     0
        pwr                     0
       freq                     0
      phase                     0
          i                     0
          p                    -0


Total analysis time (seconds) = 0.0055792

Total elapsed time (seconds) = 0.037 

Total DRAM available = 32239.535 MB.
DRAM currently available = 16362.160 MB.
Maximum ngspice program size =   15.223 MB.
Current ngspice program size =   15.223 MB.


```

### ngspice_stderr

- Role: Raw ngspice stderr log.
- Path: `outputs\pipeline2.0\batchA\a07\08_ngspice_stderr.txt`

```text

```

### tran_csv

- Role: Clean transient CSV, when .tran data is available.
- Path: `outputs\pipeline2.0\batchA\a07\08_tran.csv`

```csv
time,v(N001),v(N002),v(N003)
0.0,0.0,0.0,0.0
1e-06,0.0,0.00533147114,0.0
2e-06,0.0,0.0106629418,0.0
4e-06,0.0,0.0213258793,0.0
8e-06,0.0,0.0426517249,0.0
1.6e-05,0.0,0.0853031804,0.0
3.2e-05,0.0,0.170604206,0.0
6.4e-05,0.0,0.341191169,0.0
0.000128,0.0,0.682244414,0.0
0.000228,0.0,1.21453627,0.0
0.000328,0.0,1.74562952,0.0
0.000428,0.0,2.27500004,0.0
0.000528,0.0,2.80212542,0.0
0.000628,0.0,3.32648543,0.0
0.000728,0.0,3.84756261,0.0
0.000828,0.0,4.3648427,0.0
0.000928,0.0,4.87781523,0.0
0.001028,0.0,5.38597394,0.0
0.001128,0.0,5.88881734,0.0
0.001228,0.0,6.38584919,0.0
0.001328,0.0,6.87657898,0.0
0.001428,0.0,7.36052241,0.0
0.001528,0.0,7.8372019,0.0
0.001628,0.0,8.30614702,0.0
0.001728,0.0,8.76689497,0.0
0.001828,0.0,9.21899106,0.0
0.001928,0.0,9.66198911,0.0
0.002028,0.0,10.0954519,0.0
0.002128,0.0,10.5189518,0.0
0.002228,0.0,10.9320707,0.0
0.002328,0.0,11.334401,0.0
0.002428,0.0,11.7255456,0.0
0.002528,0.0,12.1051185,0.0
0.002628,0.0,12.4727451,0.0
0.002728,0.0,12.8280626,0.0
0.002828,0.0,13.1707203,0.0
0.002928,0.0,13.5003802,0.0
0.003028,0.0,13.8167168,0.0
0.003128,0.0,14.119418,0.0
0.003228,0.0,14.408185,0.0
0.003328,0.0,14.6827328,0.0
0.003428,0.0,14.9427906,0.0
0.003528,0.0,15.1881017,0.0
0.003628,0.0,15.4184239,0.0
0.003728,0.0,15.63353,0.0
0.003828,0.0,15.8332077,0.0
0.003928,0.0,16.01726,0.0
0.004028,0.0,16.1855051,0.0
0.004128,0.0,16.3377771,0.0
0.004228,0.0,16.4739257,0.0
0.004328,0.0,16.5938165,0.0
0.004428,0.0,16.6973312,0.0
0.004528,0.0,16.7843677,0.0
0.004628,0.0,16.85484,0.0
0.004728,0.0,16.9086786,0.0
0.004828,0.0,16.9458304,0.0
0.004928,0.0,16.9662588,0.0
0.005028,0.0,16.9699434,0.0
0.005128,0.0,16.9568808,0.0
0.005228,0.0,16.9270838,0.0
0.005328,0.0,16.8805818,0.0
0.005428,0.0,16.8174207,0.0
0.005528,0.0,16.7376628,0.0
0.005628,0.0,16.6413869,0.0
0.005728,0.0,16.528688,0.0
0.005828,0.0,16.3996772,0.0
0.005928,0.0,16.2544819,0.0
0.006028,0.0,16.0932455,0.0
0.006128,0.0,15.9161269,0.0
0.006228,0.0,15.723301,0.0
0.006328,0.0,15.5149581,0.0
0.006428,0.0,15.2913039,0.0
0.006528,0.0,15.0525589,0.0
0.006628,0.0,14.798959,0.0
0.006728,0.0,14.5307542,0.0
0.006828,0.0,14.2482093,0.0
0.006928,0.0,13.9516032,0.0
0.007028,0.0,13.6412285,0.0
0.007128,0.0,13.3173915,0.0
0.007228,0.0,12.980412,0.0
0.007328,0.0,12.6306223,0.0
0.007428,0.0,12.2683677,0.0
0.007528,0.0,11.8940057,0.0
0.007628,0.0,11.5079058,0.0
0.007728,0.0,11.1104489,0.0
0.007828,0.0,10.7020274,0.0
0.007928,0.0,10.2830443,0.0
0.008028,0.0,9.85391302,0.0
0.008128,0.0,9.41505714,0.0
0.008228,0.0,8.96690974,0.0
0.008328,0.0,8.50991309,0.0
0.008428,0.0,8.04451818,0.0
0.008528,0.0,7.5711843,0.0
0.008628,0.0,7.09037857,0.0
0.008728,0.0,6.6025755,0.0
0.008828,0.0,6.10825648,0.0
0.008928,0.0,5.60790935,0.0
0.009028,0.0,5.10202789,0.0
0.009128,0.0,4.59111135,0.0
0.009228,0.0,4.07566393,0.0
0.009328,0.0,3.55619433,0.0
0.009428,0.0,3.03321519,0.0
0.009528,0.0,2.50724263,0.0
0.009628,0.0,1.97879573,0.0
0.009728,0.0,1.44839599,0.0
0.009828,0.0,0.916566864,0.0
0.009928,0.0,0.383833196,0.0
0.010028,0.0,-0.149279269,0.0
0.010128,0.0,-0.682244414,0.0
0.010228,0.0,-1.21453627,0.0
0.010328,0.0,-1.74562952,0.0
0.010428,0.0,-2.27500004,0.0
0.010528,0.0,-2.80212542,0.0
0.010628,0.0,-3.32648543,0.0
0.010728,0.0,-3.84756261,0.0
0.010828,0.0,-4.3648427,0.0
0.010928,0.0,-4.87781523,0.0
0.011028,0.0,-5.38597394,0.0
0.011128,0.0,-5.88881734,0.0
0.011228,0.0,-6.38584919,0.0
0.011328,0.0,-6.87657898,0.0
0.011428,0.0,-7.36052241,0.0
0.011528,0.0,-7.8372019,0.0
0.011628,0.0,-8.30614702,0.0
0.011728,0.0,-8.76689497,0.0
0.011828,0.0,-9.21899106,0.0
0.011928,0.0,-9.66198911,0.0
0.012028,0.0,-10.0954519,0.0
0.012128,0.0,-10.5189518,0.0
0.012228,0.0,-10.9320707,0.0
0.012328,0.0,-11.334401,0.0
0.012428,0.0,-11.7255456,0.0
0.012528,0.0,-12.1051185,0.0
0.012628,0.0,-12.4727451,0.0
0.012728,0.0,-12.8280626,0.0
0.012828,0.0,-13.1707203,0.0
0.012928,0.0,-13.5003802,0.0
0.013028,0.0,-13.8167168,0.0
0.013128,0.0,-14.119418,0.0
0.013228,0.0,-14.408185,0.0
0.013328,0.0,-14.6827328,0.0
0.013428,0.0,-14.9427906,0.0
0.013528,0.0,-15.1881017,0.0
0.013628,0.0,-15.4184239,0.0
0.013728,0.0,-15.63353,0.0
0.013828,0.0,-15.8332077,0.0
0.013928,0.0,-16.01726,0.0
0.014028,0.0,-16.1855051,0.0
0.014128,0.0,-16.3377771,0.0
0.014228,0.0,-16.4739257,0.0
0.014328,0.0,-16.5938165,0.0
0.014428,0.0,-16.6973312,0.0
0.014528,0.0,-16.7843677,0.0
0.014628,0.0,-16.85484,0.0
0.014728,0.0,-16.9086786,0.0
0.014828,0.0,-16.9458304,0.0
0.014928,0.0,-16.9662588,0.0
0.015028,0.0,-16.9699434,0.0
0.015128,0.0,-16.9568808,0.0
0.015228,0.0,-16.9270838,0.0
0.015328,0.0,-16.8805818,0.0
0.015428,0.0,-16.8174207,0.0
0.015528,0.0,-16.7376628,0.0
0.015628,0.0,-16.6413869,0.0
0.015728,0.0,-16.528688,0.0
0.015828,0.0,-16.3996772,0.0
0.015928,0.0,-16.2544819,0.0
0.016028,0.0,-16.0932455,0.0
0.016128,0.0,-15.9161269,0.0
0.016228,0.0,-15.723301,0.0
0.016328,0.0,-15.5149581,0.0
0.016428,0.0,-15.2913039,0.0
0.016528,0.0,-15.0525589,0.0
0.016628,0.0,-14.798959,0.0
0.016728,0.0,-14.5307542,0.0
0.016828,0.0,-14.2482093,0.0
0.016928,0.0,-13.9516032,0.0
0.017028,0.0,-13.6412285,0.0
0.017128,0.0,-13.3173915,0.0
0.017228,0.0,-12.980412,0.0
0.017328,0.0,-12.6306223,0.0
0.017428,0.0,-12.2683677,0.0
0.017528,0.0,-11.8940057,0.0
0.017628,0.0,-11.5079058,0.0
0.017728,0.0,-11.1104489,0.0
0.017828,0.0,-10.7020274,0.0
0.017928,0.0,-10.2830443,0.0
0.018028,0.0,-9.85391302,0.0
0.018128,0.0,-9.41505714,0.0
0.018228,0.0,-8.96690974,0.0
0.018328,0.0,-8.50991309,0.0
0.018428,0.0,-8.04451818,0.0
0.018528,0.0,-7.5711843,0.0
0.018628,0.0,-7.09037857,0.0
0.018728,0.0,-6.6025755,0.0
0.018828,0.0,-6.10825648,0.0
0.018928,0.0,-5.60790935,0.0
0.019028,0.0,-5.10202789,0.0
0.019128,0.0,-4.59111135,0.0
0.019228,0.0,-4.07566393,0.0
0.019328,0.0,-3.55619433,0.0
0.019428,0.0,-3.03321519,0.0
0.019528,0.0,-2.50724263,0.0
0.019628,0.0,-1.97879573,0.0
0.019728,0.0,-1.44839599,0.0
0.019828,0.0,-0.916566864,0.0
0.019928,0.0,-0.383833196,0.0
0.020028,0.0,0.149279269,0.0
0.020128,0.0,0.682244414,0.0
0.020228,0.0,1.21453627,0.0
0.020328,0.0,1.74562952,0.0
0.020428,0.0,2.27500004,0.0
0.020528,0.0,2.80212542,0.0
0.020628,0.0,3.32648543,0.0
0.020728,0.0,3.84756261,0.0
0.020828,0.0,4.3648427,0.0
0.020928,0.0,4.87781523,0.0
0.021028,0.0,5.38597394,0.0
0.021128,0.0,5.88881734,0.0
0.021228,0.0,6.38584919,0.0
0.021328,0.0,6.87657898,0.0
0.021428,0.0,7.36052241,0.0
0.021528,0.0,7.8372019,0.0
0.021628,0.0,8.30614702,0.0
0.021728,0.0,8.76689497,0.0
0.021828,0.0,9.21899106,0.0
0.021928,0.0,9.66198911,0.0
0.022028,0.0,10.0954519,0.0
0.022128,0.0,10.5189518,0.0
0.022228,0.0,10.9320707,0.0
0.022328,0.0,11.334401,0.0
0.022428,0.0,11.7255456,0.0
0.022528,0.0,12.1051185,0.0
0.022628,0.0,12.4727451,0.0
0.022728,0.0,12.8280626,0.0
0.022828,0.0,13.1707203,0.0
0.022928,0.0,13.5003802,0.0
0.023028,0.0,13.8167168,0.0
0.023128,0.0,14.119418,0.0
0.023228,0.0,14.408185,0.0
0.023328,0.0,14.6827328,0.0
0.023428,0.0,14.9427906,0.0
0.023528,0.0,15.1881017,0.0
0.023628,0.0,15.4184239,0.0
0.023728,0.0,15.63353,0.0
0.023828,0.0,15.8332077,0.0
0.023928,0.0,16.01726,0.0
0.024028,0.0,16.1855051,0.0
0.024128,0.0,16.3377771,0.0
0.024228,0.0,16.4739257,0.0
0.024328,0.0,16.5938165,0.0
0.024428,0.0,16.6973312,0.0
0.024528,0.0,16.7843677,0.0
0.024628,0.0,16.85484,0.0
0.024728,0.0,16.9086786,0.0
0.024828,0.0,16.9458304,0.0
0.024928,0.0,16.9662588,0.0
0.025028,0.0,16.9699434,0.0
0.025128,0.0,16.9568808,0.0
0.025228,0.0,16.9270838,0.0
0.025328,0.0,16.8805818,0.0
0.025428,0.0,16.8174207,0.0
0.025528,0.0,16.7376628,0.0
0.025628,0.0,16.6413869,0.0
0.025728,0.0,16.528688,0.0
0.025828,0.0,16.3996772,0.0
0.025928,0.0,16.2544819,0.0
0.026028,0.0,16.0932455,0.0
0.026128,0.0,15.9161269,0.0
0.026228,0.0,15.723301,0.0
0.026328,0.0,15.5149581,0.0
0.026428,0.0,15.2913039,0.0
0.026528,0.0,15.0525589,0.0
0.026628,0.0,14.798959,0.0
0.026728,0.0,14.5307542,0.0
0.026828,0.0,14.2482093,0.0
0.026928,0.0,13.9516032,0.0
0.027028,0.0,13.6412285,0.0
0.027128,0.0,13.3173915,0.0
0.027228,0.0,12.980412,0.0
0.027328,0.0,12.6306223,0.0
0.027428,0.0,12.2683677,0.0
0.027528,0.0,11.8940057,0.0
0.027628,0.0,11.5079058,0.0
0.027728,0.0,11.1104489,0.0
0.027828,0.0,10.7020274,0.0
0.027928,0.0,10.2830443,0.0
0.028028,0.0,9.85391302,0.0
0.028128,0.0,9.41505714,0.0
0.028228,0.0,8.96690974,0.0
0.028328,0.0,8.50991309,0.0
0.028428,0.0,8.04451818,0.0
0.028528,0.0,7.5711843,0.0
0.028628,0.0,7.09037857,0.0
0.028728,0.0,6.6025755,0.0
0.028828,0.0,6.10825648,0.0
0.028928,0.0,5.60790935,0.0
0.029028,0.0,5.10202789,0.0
0.029128,0.0,4.59111135,0.0
0.029228,0.0,4.07566393,0.0
0.029328,0.0,3.55619433,0.0
0.029428,0.0,3.03321519,0.0
0.029528,0.0,2.50724263,0.0
0.029628,0.0,1.97879573,0.0
0.029728,0.0,1.44839599,0.0
0.029828,0.0,0.916566864,0.0
0.029928,0.0,0.383833196,0.0
0.030028,0.0,-0.149279269,0.0
0.030128,0.0,-0.682244414,0.0
0.030228,0.0,-1.21453627,0.0
0.030328,0.0,-1.74562952,0.0
0.030428,0.0,-2.27500004,0.0
0.030528,0.0,-2.80212542,0.0
0.030628,0.0,-3.32648543,0.0
0.030728,0.0,-3.84756261,0.0
0.030828,0.0,-4.3648427,0.0
0.030928,0.0,-4.87781523,0.0
0.031028,0.0,-5.38597394,0.0
0.031128,
```

> Evidence truncated for prompt size. Use only the visible evidence, and mention if more detail may be needed.


## Required answer format

Rispondi in Markdown usando esattamente queste sezioni:

1. **Stato della simulazione**
   Spiega se ngspice e stato eseguito correttamente oppure no.

2. **Evidenze principali**
   Elenca le prove piu importanti, citando componenti, nodi, netlist, stdout/stderr o report.

3. **Diagnosi rispetto al problema utente**
   Collega le evidenze al problema scritto dall'utente.

4. **Limiti della diagnosi**
   Dichiara cosa non si puo concludere dai dati disponibili.

5. **Scenari diagnostici proposti**
   Proponi al massimo 3 scenari diagnostici candidati, pensati per essere trasformati in una nuova simulazione SPICE.
   Non proporre semplici consigli generici: ogni scenario deve essere una ipotesi verificabile.
   Non presentarli come certamente risolutivi: sono candidati da testare.
   Se servono piu scenari, ordinali dal piu semplice al piu utile.
   Se dai dati disponibili non serve uno scenario, scrivi: `Nessuno scenario necessario dai dati disponibili.`

   Per ogni scenario usa una forma a due livelli: prima una spiegazione user-friendly, poi un blocco tecnico breve.

   Livello user-friendly:
   - Titolo naturale: descrivi cosa si vuole provare, non solo la primitiva tecnica.
   - Perche lo propongo: collega lo scenario alle evidenze SPICE e al problema utente.
   - Cosa proverei: spiega in parole semplici la modifica simulativa.
   - Cosa mi aspetto: indica cosa dovrebbe cambiare se l'ipotesi e corretta.
   - Come lo verifichiamo: indica quali tensioni, correnti, log o grafici confrontare.
   - Prossimo passo: cosa provare se lo scenario non conferma l'ipotesi.

   Blocco tecnico per pipeline:
   Usa un blocco JSON breve e non inventare campi non deducibili dalle evidenze.
   Il blocco deve aiutare una futura pipeline a trasformare lo scenario in una run separata.
   Campi consigliati: `scenario_id`, `title`, `hypothesis`, `actions`, `rerun_from`, `analysis`, `compare`.
   Se un campo non e deducibile, usa `unknown` oppure omettilo.

   Quando possibile, esprimi la modifica controllata usando primitive generali come:
   `close_switch`, `open_switch`, `drive_node_voltage`, `change_source_value`,
   `connect_nodes`, `disconnect_terminal`, `move_terminal`, `replace_with_equivalent`,
   `run_op`, `run_tran`.

   Ricorda che nella versione read-only questi scenari NON sono eseguiti.
   Sono solo proposte per una fase successiva della pipeline.

Alla fine aggiungi una riga:

`Richiede immagine: si/no`

Metti `si` solo se gli output strutturati indicano una probabile incoerenza del Graph JSON oppure se SPICE non e eseguibile in modo utile.
Se l'immagine sarebbe solo una verifica opzionale, metti comunque `no` e cita la verifica opzionale nei limiti.

## Final task

Analyze the user problem using the evidence above.
Explain what the simulation result means, whether it supports the user problem, and what can or cannot be concluded.
If ngspice failed, focus on the error evidence and explain why the current circuit is not diagnostically reliable.
If ngspice succeeded, connect the simulated node voltages, currents, skipped components and warnings to the user problem.
Suggest future diagnostic scenarios only as controlled SPICE-verifiable hypotheses; do not claim that they have already been executed.
Keep scenarios natural and minimally invasive before proposing topology or Graph JSON corrections.
