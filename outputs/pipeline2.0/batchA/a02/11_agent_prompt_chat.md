# Diagnostic agent prompt

## System instructions

- You are a read-only diagnostic assistant for electronic circuits.
- Your task is to explain the Pipeline 2.0 and ngspice results using only the provided evidence.
- The final answer must be written in Italian.
- Keep technical identifiers exactly as provided, for example node names, component IDs and file names.
- Do not invent component values, electrical connections, SPICE models, node voltages, currents or simulation results.
- Do not assume that a component exists if it is not present in the Graph JSON or in the generated netlist.
- Do not modify the netlist, do not execute SPICE and do not apply scenarios.
- New diagnostic scenarios may be suggested only as future SPICE-verifiable hypotheses, not as already verified facts.
- Already executed scenarios must be interpreted from the executed scenario evidence, not re-imagined.
- Use general electronics and SPICE knowledge only to interpret the provided evidence, not to create missing evidence.
- If the evidence is insufficient, say exactly what is missing.
- Do not describe a branch as floating unless the evidence shows a floating or singleton node with no DC reference path.
- If a branch has a resistive path to ground but no active source, describe it as not driven or not powered.

## Operating rules

- Treat the evidence sections below as the only technical evidence available in this prompt.
- When useful, cite component IDs, node IDs, file names or artifact sections.
- Use the original artifact paths only as traceability references.
- If an artifact is missing or truncated, mention the limitation before drawing conclusions from it.
- If executed scenario evidence is available, use it to answer questions about which scenario explains or resolves the problem.
- When discussing executed scenarios, distinguish the controlled action from the diagnostic outcome.
- For questions about which scenario resolves the problem, do not merely list scenarios: identify the strongest scenario and justify it from scenario_comparison.json.
- Treat `resolved_candidate` with `stop_automation=true` as the strongest executed-scenario outcome.
- Treat `partially_resolved` as supporting diagnostic evidence, not as the main resolving scenario when a resolved_candidate exists.
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
- For executable scenario JSON, use only action types currently supported by the scenario runner unless clearly marked as future/not executable.
- Currently executable action types are `drive_node_voltage`, `change_source_value` and `close_switch`.
- Never put `unknown` in `actions[].value`; use a concrete SPICE value such as `5V`, `10V`, `DC 3.3`, or `SIN(0 1 100)`.
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

Il circuito non produce l'uscita attesa, quale potrebbe essere il problema?

## Circuit metadata

- Batch: `batchA`
- Circuit: `a02`
- Agent mode: `graph_grounded_readonly`

## Technical summary

```json
{
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_message": "ngspice completed successfully.",
  "emitted_elements": 3,
  "skipped_elements": 4,
  "emit_warnings_count": 1,
  "skipped_components_count": 4,
  "node_count": 5,
  "ground_groups_count": 3,
  "singleton_nodes_count": 0,
  "bound_components": 4,
  "missing_components": 0,
  "unsupported_components": 0,
  "spice_ready_components": 4,
  "rules_missing_components": 0,
  "has_tran_csv": false,
  "has_tran_plot": false
}
```

## Available artifacts

- `graph`: available, path=`outputs\pipeline2.0\batchA\a02\01_graph.json`
- `normalized_circuit`: available, path=`outputs\pipeline2.0\batchA\a02\02_normalized_circuit.json`
- `node_map`: available, path=`outputs\pipeline2.0\batchA\a02\03_node_map.json`
- `values_bound`: available, path=`outputs\pipeline2.0\batchA\a02\04_values_bound.json`
- `component_rules`: available, path=`outputs\pipeline2.0\batchA\a02\06_component_rules.json`
- `netlist`: available, path=`outputs\pipeline2.0\batchA\a02\07_netlist.cir`
- `spice_emit_report`: available, path=`outputs\pipeline2.0\batchA\a02\07_spice_emit_report.json`
- `spice_run`: available, path=`outputs\pipeline2.0\batchA\a02\08_spice_run.json`
- `ngspice_stdout`: available, path=`outputs\pipeline2.0\batchA\a02\08_ngspice_stdout.txt`
- `ngspice_stderr`: available, path=`outputs\pipeline2.0\batchA\a02\08_ngspice_stderr.txt`
- `tran_csv`: missing, path=`None`
- `tran_plot_png`: missing, path=`None`
- `tran_plot_svg`: missing, path=`None`

## Executed scenarios index

No executed scenarios are available in the manifest.

## Scenario outcome summary

No scenario outcome summary available.

## Image access policy

- Included by default: `False`
- Can be requested: `True`
- Path: `data\batchA\a02.png`
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
- The executable technical JSON should currently use only `drive_node_voltage`, `change_source_value` or `close_switch`.
- For `change_source_value`, choose a concrete value that makes the diagnostic comparison meaningful; do not write `unknown`.
- For `close_switch`, target an existing recognized switch component such as `switch25.1`; do not invent a switch.
- If no concrete source value is justified, describe the idea in the prose and do not include it as an executable JSON action.

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

Example source-value scenario action:

```json
{
  "scenario_id": "scenario_2",
  "title": "Variare la sorgente principale",
  "hypothesis": "Changing the existing supply should affect only the branches connected to that supply.",
  "actions": [
    {
      "type": "change_source_value",
      "target": "VVCC",
      "value": "10V"
    }
  ],
  "rerun_from": "07",
  "analysis": "op",
  "compare": ["v(N001)", "i(vvcc#branch)"]
}
```

Example close-switch scenario action:

```json
{
  "scenario_id": "scenario_1",
  "title": "Chiudere lo switch riconosciuto",
  "hypothesis": "The open switch may be preventing a useful reference or current path.",
  "actions": [
    {
      "type": "close_switch",
      "target": "switch25.1"
    }
  ],
  "rerun_from": "06",
  "analysis": "op",
  "compare": ["v(N001)", "i(vbattery2_1#branch)"]
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
- Path: `outputs\pipeline2.0\batchA\a02\01_graph.json`

```json
{
  "image_id": "a02",
  "image_name": "a02.png",
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
      "component_id": "battery2.1",
      "instance_id": "2.1",
      "class_name": "Battery",
      "terminals": [
        {
          "terminal_id": "battery2.1_negative",
          "name": "negative",
          "relative_position": "top"
        },
        {
          "terminal_id": "battery2.1_positive",
          "name": "positive",
          "relative_position": "bottom"
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
    "battery2.1_negative": [
      "resistor22.1_t1",
      "switch25.1_t1"
    ],
    "battery2.1_positive": [
      "connector5.1_pin1"
    ],
    "capacitor4.1_t1": [
      "connector5.1_pin3"
    ],
    "capacitor4.1_t2": [
      "gnd9.2_t1"
    ],
    "connector5.1_pin1": [
      "battery2.1_positive"
    ],
    "connector5.1_pin2": [
      "resistor22.1_t2"
    ],
    "connector5.1_pin3": [
      "capacitor4.1_t1"
    ],
    "connector5.1_pin4": [
      "gnd9.1_t1"
    ],
    "gnd9.1_t1": [
      "connector5.1_pin4"
    ],
    "gnd9.2_t1": [
      "capacitor4.1_t2"
    ],
    "gnd9.3_t1": [
      "switch25.1_t2"
    ],
    "resistor22.1_t1": [
      "battery2.1_negative",
      "switch25.1_t1"
    ],
    "resistor22.1_t2": [
      "connector5.1_pin2"
    ],
    "switch25.1_t1": [
      "battery2.1_negative",
      "resistor22.1_t1"
    ],
    "switch25.1_t2": [
      "gnd9.3_t1"
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

- Role: Maps component terminals to SPICE node names.
- Path: `outputs\pipeline2.0\batchA\a02\03_node_map.json`

```json
{
  "circuit_id": "a02",
  "source_format": "pipeline2.0_node_map",
  "nodes": [
    {
      "node_id": "0",
      "kind": "ground",
      "terminals": [
        "capacitor4.1_t2",
        "connector5.1_pin4",
        "gnd9.1_t1",
        "gnd9.2_t1",
        "gnd9.3_t1",
        "switch25.1_t2"
      ],
      "terminal_count": 6,
      "source_groups": [
        [
          "capacitor4.1_t2",
          "gnd9.2_t1"
        ],
        [
          "connector5.1_pin4",
          "gnd9.1_t1"
        ],
        [
          "gnd9.3_t1",
          "switch25.1_t2"
        ]
      ]
    },
    {
      "node_id": "N001",
      "kind": "normal",
      "terminals": [
        "battery2.1_negative",
        "resistor22.1_t1",
        "switch25.1_t1"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N002",
      "kind": "normal",
      "terminals": [
        "battery2.1_positive",
        "connector5.1_pin1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N003",
      "kind": "normal",
      "terminals": [
        "capacitor4.1_t1",
        "connector5.1_pin3"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N004",
      "kind": "normal",
      "terminals": [
        "connector5.1_pin2",
        "resistor22.1_t2"
      ],
      "terminal_count": 2
    }
  ],
  "terminal_to_node": {
    "battery2.1_negative": "N001",
    "battery2.1_positive": "N002",
    "capacitor4.1_t1": "N003",
    "capacitor4.1_t2": "0",
    "connector5.1_pin1": "N002",
    "connector5.1_pin2": "N004",
    "connector5.1_pin3": "N003",
    "connector5.1_pin4": "0",
    "gnd9.1_t1": "0",
    "gnd9.2_t1": "0",
    "gnd9.3_t1": "0",
    "resistor22.1_t1": "N001",
    "resistor22.1_t2": "N004",
    "switch25.1_t1": "N001",
    "switch25.1_t2": "0"
  },
  "component_terminal_nodes": {
    "battery2.1": {
      "negative": "N001",
      "positive": "N002"
    },
    "capacitor4.1": {
      "t1": "N003",
      "t2": "0"
    },
    "connector5.1": {
      "pin1": "N002",
      "pin2": "N004",
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
    "resistor22.1": {
      "t1": "N001",
      "t2": "N004"
    },
    "switch25.1": {
      "t1": "N001",
      "t2": "0"
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
    "nodes_count": 5,
    "normal_nodes_count": 4,
    "ground_nodes_count": 1,
    "ground_groups_count": 3,
    "terminal_to_node_count": 15,
    "singleton_nodes_count": 0
  }
}
```

### values_bound

- Role: Values and labels bound to graph components.
- Path: `outputs\pipeline2.0\batchA\a02\04_values_bound.json`

```json
{
  "circuit_id": "a02",
  "source_format": "pipeline2.0_values_bound",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_manual_values\\batchA\\a02_values.yaml",
  "supplies": {},
  "components": {
    "battery2.1": {
      "class_name": "Battery",
      "terminal_nodes": {
        "negative": "N001",
        "positive": "N002"
      },
      "value_data": {
        "type": "dc",
        "value": 5,
        "unit": "V",
        "source": "manual_from_vcc_label",
        "label_text": "VCC +5 V DC"
      },
      "status": "bound"
    },
    "capacitor4.1": {
      "class_name": "Capacitor",
      "terminal_nodes": {
        "t1": "N003",
        "t2": "0"
      },
      "value_data": {
        "value": 100,
        "unit": "nF",
        "source": "manual_from_image_label",
        "label_text": "100nF"
      },
      "status": "bound"
    },
    "connector5.1": {
      "class_name": "Connector",
      "terminal_nodes": {
        "pin1": "N002",
        "pin2": "N004",
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
    "resistor22.1": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N001",
        "t2": "N004"
      },
      "value_data": {
        "value": 10000,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "10k"
      },
      "status": "bound"
    },
    "switch25.1": {
      "class_name": "Switch",
      "terminal_nodes": {
        "t1": "N001",
        "t2": "0"
      },
      "value_data": {
        "state": "open",
        "state_source": "graph_json_state",
        "state_confidence": 0.95,
        "source": "graph_json_state",
        "label_text": "SENSE"
      },
      "status": "bound"
    }
  },
  "nodes": {
    "connector5.1_pin1": {
      "label": "VCC",
      "source": "manual_from_image_label",
      "label_text": "VCC +5 V DC",
      "node": "N002"
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
    "components_total": 8,
    "bound_components": 4,
    "missing_components": 0,
    "not_required_components": 4,
    "unsupported_components": 0,
    "supplies_count": 0,
    "manual_nodes_count": 2
  }
}
```

### component_rules

- Role: SPICE conversion rules for each component.
- Path: `outputs\pipeline2.0\batchA\a02\06_component_rules.json`

```json
{
  "circuit_id": "a02",
  "source_format": "pipeline2.0_component_rules",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_manual_values\\batchA\\a02_values.yaml",
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
        "value": 5,
        "unit": "V",
        "source": "manual_from_vcc_label",
        "label_text": "VCC +5 V DC"
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
        "N003",
        "0"
      ],
      "parameters": {
        "value": 100,
        "unit": "nF",
        "source": "manual_from_image_label",
        "label_text": "100nF"
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
        "value": 10000,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "10k"
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
        "N001",
        "0"
      ],
      "parameters": {
        "state": "open",
        "state_source": "graph_json_state",
        "state_confidence": 0.95,
        "source": "graph_json_state",
        "label_text": "SENSE"
      },
      "strategy": "open_circuit"
    }
  },
  "simulation": {},
  "stats": {
    "components_total": 8,
    "spice_ready_components": 4,
    "not_emitted_components": 4,
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

- Role: Generated SPICE netlist.
- Path: `outputs\pipeline2.0\batchA\a02\07_netlist.cir`

```spice
* pipeline2.0 netlist
* circuit: a02

Vbattery2_1 N002 N001 DC 5
Ccapacitor4_1 N003 0 100n
Rresistor22_1 N001 N004 10000
* switch25.1 open: not emitted

.op
.end

```

### spice_emit_report

- Role: Report of emitted, skipped and warning components.
- Path: `outputs\pipeline2.0\batchA\a02\07_spice_emit_report.json`

```json
{
  "circuit_id": "a02",
  "source_format": "pipeline2.0_spice_emit_report",
  "emitted_elements": 3,
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
  "models": [],
  "warnings": [
    "switch25.1: open switch not emitted"
  ]
}
```

### spice_run

- Role: Structured ngspice execution report.
- Path: `outputs\pipeline2.0\batchA\a02\08_spice_run.json`

```json
{
  "source_format": "pipeline2.0_spice_run",
  "status": "success",
  "netlist_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a02\\07_netlist.cir",
  "command": [
    "C:\\Users\\m.profilo\\Spice64\\bin\\ngspice_con.exe",
    "-b",
    "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a02\\07_netlist.cir"
  ],
  "exit_code": 0,
  "stdout_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a02\\08_ngspice_stdout.txt",
  "stderr_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a02\\08_ngspice_stderr.txt",
  "tran_raw_csv_path": null,
  "tran_csv_path": null,
  "tran_plot_path": null,
  "tran_plot_png_path": null,
  "tran_plot_svg_path": null,
  "message": "ngspice completed successfully."
}
```

### ngspice_stdout

- Role: Raw ngspice stdout log.
- Path: `outputs\pipeline2.0\batchA\a02\08_ngspice_stdout.txt`

```text

Note: No compatibility mode selected!


Circuit: * pipeline2.0 netlist

Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

No. of Data Rows : 1
	Node                                  Voltage
	----                                  -------
	----	-------
	n004                             0.000000e+00
	n003                             0.000000e+00
	n001                             0.000000e+00
	n002                             5.000000e+00

	Source	Current
	------	-------

	vbattery2_1#branch               0.000000e+00

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
capacitance                 1e-07
      dtemp                     0
     bv_max                 1e+99
          i                     0
          p                     0

 Resistor: Simple linear resistor
     device         rresistor22_1
      model                     R
 resistance                 10000
         ac                 10000
      dtemp                     0
     bv_max                 1e+99
      noisy                     1
          i                     0
          p                     0

 Vsource: Independent voltage source
     device           vbattery2_1
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
          i                     0
          p                     0


Total analysis time (seconds) = 0.0067567

Total elapsed time (seconds) = 0.046 

Total DRAM available = 32239.535 MB.
DRAM currently available = 16442.617 MB.
Maximum ngspice program size =   15.207 MB.
Current ngspice program size =   15.207 MB.


```

### ngspice_stderr

- Role: Raw ngspice stderr log.
- Path: `outputs\pipeline2.0\batchA\a02\08_ngspice_stderr.txt`

```text
Warning: singular matrix:  check node n001

Note: Starting dynamic gmin stepping
Warning: singular matrix:  check node n001

Warning: Dynamic gmin stepping failed
Note: Starting true gmin stepping
Warning: singular matrix:  check node n001

Warning: singular matrix:  check node n001

Warning: singular matrix:  check node n001

Warning: singular matrix:  check node n001

Warning: True gmin stepping failed
Note: Starting source stepping
Warning: source stepping failed
Note: Transient op started
Note: Transient op finished successfully

```

### tran_csv

Evidence not available.


## Executed scenario evidence

No executed scenario evidence available.


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
   Se la domanda dell'utente riguarda scenari gia eseguiti, usa questa sezione per riassumere gli scenari eseguiti e indicare quale outcome e piu forte.
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
   Non usare `unknown` dentro `actions[].value`: uno scenario eseguibile deve avere valori concreti.
   Se un valore concreto non e deducibile, ometti l'azione eseguibile e descrivi lo scenario solo come follow-up non ancora eseguibile.

   Per ora, nel blocco JSON eseguibile preferisci le primitive supportate dalla pipeline:
   `drive_node_voltage`, `change_source_value`, `close_switch`.
   Primitive future, da citare solo se ben giustificate e non ancora eseguibili:
   `open_switch`, `connect_nodes`, `disconnect_terminal`, `move_terminal`, `replace_with_equivalent`,
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
If the question is about already executed scenarios, use the executed scenario evidence and clearly identify the strongest outcome.
When suggesting new future diagnostic scenarios, present them only as controlled SPICE-verifiable hypotheses.
Keep scenarios natural and minimally invasive before proposing topology or Graph JSON corrections.
