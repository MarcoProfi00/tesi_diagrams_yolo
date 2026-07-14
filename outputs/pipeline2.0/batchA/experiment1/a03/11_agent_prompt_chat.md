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
- Treat `not_resolved` as not sufficient by itself, not automatically useless.
- A `not_resolved` scenario may still be an enabling condition for a combined scenario when it closes a switch, creates a reference path, completes a current path, or supplies a precondition missing in another scenario.
- In the initial answer for a circuit, propose only first-pass scenarios and do not propose combined scenarios.
- Combined scenarios are allowed only after scenario evidence exists and the user explicitly asks what to try next.
- If the user asks what to try next after executed scenarios, propose the next most informative scenario based on scenario_comparison.json.
- If one executed scenario already changed the nodes, branches or currents most closely tied to the user symptom, prefer extending that proven direction before proposing a weaker exploratory source-value change.
- Prefer a minimal combined scenario built around the strongest symptom-linked evidence before proposing a generic source-value variation, unless the source itself is the strongest evidence-backed hypothesis.
- If no executed scenario resolved the problem, consider combined scenarios when previous outcomes provide complementary evidence, including `not_resolved` actions that are electrically enabling.
- Do not combine every previous scenario blindly; explain why each included action is useful and why excluded actions are not included.
- A next combined scenario must be self-contained and use only supported action types.
- If ngspice failed and the structured evidence shows strong topology problems, do not remain in simple electrical-scenario mode.
- Strong topology problems include signals such as no ground/reference, critical singleton nodes, skipped critical components, isolated branches, split sources, or Graph JSON warnings that make the extracted circuit untrustworthy.
- In that case, explain the failure first, request the real image, and prefer topology-correction or graph-correction scenarios over simple node-driving or source-value scenarios.
- Do not use the original image unless the structured evidence suggests that the Graph JSON may be wrong.
- If image access is needed, explain which structured evidence justifies it.
- Request image access only for strong structured reasons: Graph JSON warnings, suspicious or missing connections, important singleton nodes, missing critical components, unsupported critical topology, or ngspice failure caused by topology/convergence issues.
- When ngspice failed and multiple strong topology signals are present, `Richiede immagine: si` should normally be the expected outcome.
- If ngspice succeeds and graph/node-map evidence is internally coherent, do not request the image by default.
- If ngspice failed with strong topology signals, the initial scenarios may be graph-correction or topology-correction proposals, and they may be marked as future/not yet executable when appropriate.
- In topology-failure mode, do not force every scenario into the current executable primitive set if the real bottleneck is an untrustworthy graph.
- In read-only mode, do not modify netlists, do not change values and do not execute scenarios.
- A diagnostic scenario is a controlled hypothesis that can be verified by generating a scenario-specific Pipeline 2.0 run and rerunning ngspice.
- A scenario must never overwrite the original Pipeline 2.0 outputs.
- A scenario must start from copied base artifacts, modify only the scenario copies, and save separate scenario artifacts for comparison.
- Scenario artifacts must be created only after the user explicitly chooses one proposed scenario to execute.
- Suggest at most 3 candidate scenarios, ordered from simplest to most informative.
- In the initial diagnostic answer, the first set of up to 3 scenarios must be simple first-pass candidates, not combined scenarios.
- Each scenario must be readable by a non-SPICE user first, and machine-oriented only in a short technical block after the explanation.
- The user-facing scenario title should describe the diagnostic idea naturally, for example `Alimentare il ramo della lampada`, not only `drive_node_voltage`.
- The technical block should be concise and should not replace the human explanation.
- For executable scenario JSON, use only action types currently supported by the scenario runner unless clearly marked as future/not executable.
- Currently executable action types are `drive_node_voltage`, `change_source_value` and `close_switch`.
- Never put `unknown` in `actions[].value`; use a concrete SPICE value such as `5V`, `10V`, `DC 3.3`, or `SIN(0 1 100)`.
- Prefer natural scenarios that directly test the user's symptom using existing nodes, states and values before proposing graph-correction scenarios.
- If ngspice failed and the evidence shows strong topology problems, do not stay in simple electrical-test mode: switch to image-guided topology-correction reasoning.
- Prefer acting on existing external inputs, supply labels, connector pins and recognized component states before directly forcing internal load nodes.
- If an upstream input node feeds a load, drive the upstream input first; direct forcing of the load node is a later model-isolation test, not an early natural scenario.
- The top 3 scenarios should be independently executable: if a scenario needs another action first, include that action in the same scenario JSON or present it only as a later follow-up.
- Do not propose combined scenarios in the initial top 3. Combined scenarios are allowed only after earlier scenarios have been executed and the user asks what to try next.
- Do not propose `run_tran` alone when the base operating point does not power the relevant branch; include the required drive/source/state actions in the same scenario.
- If all initially proposed scenarios have been executed and none is a resolved candidate, propose the next most informative scenario instead of stopping.
- The next scenario may combine actions, but only combine assumptions that were supported by previous scenario evidence; do not combine all scenarios blindly.
- `not_resolved` means that a scenario was not sufficient by itself; it does not automatically mean the action is useless.
- A `not_resolved` scenario can still be an enabling action in a combined scenario if it closes a switch, creates a reference path, completes a current path, or supplies a missing precondition for another useful action.
- When one executed scenario has already changed the symptom-linked nodes or branches, prefer extending that proven direction before proposing a weaker exploratory source-change scenario.
- Prefer combining the strongest symptom-linked scenario with an enabling action before proposing a generic source-value variation, unless the source itself is the strongest evidence-backed hypothesis.
- When proposing a combined scenario, explain why each included action is justified and why excluded actions are not included yet.
- If ngspice succeeds and graph/node-map evidence is internally coherent, the first scenarios should be value, source, analysis or state tests, not topology rewrites.
- If ngspice failed and the evidence shows no ground/reference, critical singleton nodes, skipped critical components, or isolated branches, prefer topology-correction scenarios over simple drive/source scenarios.
- In topology-correction mode, the first 3 scenarios may include future graph-correction or image-guided reconstruction scenarios even if the current runner cannot execute them yet.
- When a topology-correction scenario is not executable yet, clearly mark it as future/not executable instead of pretending it can already be run by the current pipeline.
- Avoid `connect_nodes`, `disconnect_terminal` and `move_terminal` in the top 3 scenarios unless structured evidence strongly suggests a graph/topology error.
- If topology repair is only a later possibility, mention it as a next step instead of making it one of the first 3 scenarios.
- Do not propose graph-correction scenarios in the top 3 unless there is strong structured evidence that the Graph JSON is wrong.
- Scenarios can be iterative: if one scenario does not explain the problem, propose the next one or a combination of previous validated assumptions.

## User problem

Se dovessi correggere il graph per prima cosa, quali collegamenti o componenti sistemeresti subito? Dimmi in ordine di priorità quali errori topologici vanno corretti prima per rendere il circuito simulabile.

## Circuit metadata

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

## Available artifacts

- `graph`: available, path=`outputs\pipeline2.0\batchA\a03\01_graph.json`
- `normalized_circuit`: available, path=`outputs\pipeline2.0\batchA\a03\02_normalized_circuit.json`
- `node_map`: available, path=`outputs\pipeline2.0\batchA\a03\03_node_map.json`
- `values_bound`: available, path=`outputs\pipeline2.0\batchA\a03\04_values_bound.json`
- `component_rules`: available, path=`outputs\pipeline2.0\batchA\a03\06_component_rules.json`
- `netlist`: available, path=`outputs\pipeline2.0\batchA\a03\07_netlist.cir`
- `spice_emit_report`: available, path=`outputs\pipeline2.0\batchA\a03\07_spice_emit_report.json`
- `spice_run`: available, path=`outputs\pipeline2.0\batchA\a03\08_spice_run.json`
- `ngspice_stdout`: available, path=`outputs\pipeline2.0\batchA\a03\08_ngspice_stdout.txt`
- `ngspice_stderr`: available, path=`outputs\pipeline2.0\batchA\a03\08_ngspice_stderr.txt`
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
- Path: `data\batchA\a03.jpg`
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
3b. If ngspice failed with strong topology evidence, request the image and move early to topology-correction reasoning instead of staying in simple electrical-test mode.
4. In the first response, propose only single-hypothesis scenarios, not combined scenarios.
5. Test individual hypotheses before proposing combined scenarios.
6. Use combined scenarios only after the individual assumptions are meaningful, and include every required action in the same JSON block.
7. Use graph-correction or topology-rewrite scenarios only when graph or SPICE evidence strongly supports a recognition/topology error.
8. After executed scenarios are available, use their outcomes to decide whether the next scenario should be single-action, combined, or a request for missing evidence.

After executed scenarios:

- If at least one scenario is `resolved_candidate` with `stop_automation=true`, do not propose a new scenario unless the user explicitly asks for further exploration.
- If no scenario is resolved and at least one scenario is `partially_resolved`, propose a next scenario that combines only the useful partial assumptions.
- Do not exclude a scenario only because its outcome is `not_resolved`: first decide whether it is irrelevant, or whether it is an enabling condition that may become useful together with another action.
- Treat `not_resolved` but enabling actions as candidates for combined scenarios when they close a switch, create a DC reference, complete a path, or provide a precondition that another scenario lacked.
- If one scenario already changed the nodes or currents most closely tied to the user's symptom, treat that scenario as the main direction for the next step.
- In that case, prefer adding only the minimum enabling action needed around that main direction before testing broader source-value variations.
- If all scenarios are `not_resolved`, explain that the current hypotheses did not work and propose a different minimal hypothesis, or request missing evidence if needed.
- Do not combine all previously proposed scenarios automatically. Combining actions is useful only when the previous results show complementary evidence.
- A combined scenario must be self-contained: include every required action in the same `actions` array.

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
- If ngspice fails and there is strong structured evidence of topology error, do not keep proposing only `drive_node_voltage` or `change_source_value` as if the extracted graph were already trustworthy.
- In that case, the agent should switch to topology-correction mode: explain the failure, request the real image, and propose correction scenarios for graph structure or missing interpreted components.
- In topology-correction mode, it is acceptable that a proposed scenario is not immediately executable by the current scenario runner, as long as this is stated clearly.
- In topology-correction mode, prefer scenarios such as reconstructing a split source, restoring a missing reference, reconnecting singleton terminals, or reinterpreting a relay/transformer/contact structure from the image.

Scenario presentation format:

- Start with a natural title that a user can understand.
- Explain why the scenario is proposed using concrete evidence from the base run.
- Explain what would be changed in simple words.
- Explain what SPICE result would confirm or reject the hypothesis.
- End the scenario with a short technical JSON block for the future pipeline.
- Keep the technical block small: it is a controlled hint for automation, not the main answer.
- The executable technical JSON should currently use only `drive_node_voltage`, `change_source_value` or `close_switch`.
- If the scenario is not executable yet, say so explicitly and use future-oriented actions only as a structured proposal.
- For `change_source_value`, choose a concrete value that makes the diagnostic comparison meaningful; do not write `unknown`.
- Use `change_source_value` as the next scenario only when varying the existing source is more evidence-backed than extending an already successful symptom-linked node or state test.
- For `change_source_value`, prefer the SPICE source name visible in the netlist, for example `Vbattery2_1`; component ids such as `battery2.1` are accepted only if the runner can resolve them.
- For `close_switch`, target an existing recognized switch component such as `switch25.1`; do not invent a switch.
- If no concrete source value is justified, describe the idea in the prose and do not include it as an executable JSON action.
- In `compare`, use SPICE quantities such as `v(N001)` or `i(vbattery2_1#branch)` that are directly tied to the user symptom.
- Use `stderr` in `compare` only when the scenario is explicitly testing convergence, warning reduction, missing reference conditions, or another numerical/topological issue.
- Do not add `stderr` as a default extra comparison when node voltages or branch currents already test the hypothesis directly.

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
- If the scenario depends on image-guided graph correction, state that it is a future scenario run that would start from a copied graph artifact before regenerating the downstream steps.
- If the evidence only suggests a possible Graph JSON error but does not prove it, request image access instead of silently changing the graph.

Image request policy:

- Request the image when ngspice fails because the generated circuit is not electrically meaningful, for example singular matrix, floating nodes or topology-related convergence failure.
- When ngspice fails together with strong topology evidence such as `ground_groups_count = 0`, critical singleton nodes, skipped critical components, isolated branches or split power sources, image request should normally be `Richiede immagine: si`.
- Request the image when Graph JSON warnings or node-map evidence indicate likely recognition errors.
- Do not request the image just because a circuit branch is inactive in a successful and coherent SPICE run.
- If image inspection would merely be useful for human confirmation, say so in the limitations but keep `Richiede immagine: no`.

Do not directly decide implementation details as facts. State them as expected future pipeline behavior.
For every scenario, state what should be compared between the base run and scenario run, for example node voltage, branch current, SPICE convergence, emitted/skipped components, stdout/stderr changes, transient waveform or load current.

## Evidence to analyze

### graph

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

Evidence not available.


## Executed scenario evidence

No executed scenario evidence available.


## Required answer format

Il circuito e in modalita di fallimento topologico: le evidenze strutturate indicano che il Graph JSON o la topologia estratta non sono ancora abbastanza affidabili.
Rispondi in Markdown usando esattamente queste sezioni:

1. **Stato della simulazione**
   Spiega che ngspice non ha prodotto una simulazione affidabile e riassumi il tipo di fallimento.

2. **Evidenze di errore topologico**
   Elenca le prove strutturate piu forti: mancanza di ground, nodi singleton, componenti critici saltati, sorgenti spezzate, rami isolati o warning che rendono il graph poco affidabile.

3. **Diagnosi rispetto al problema utente**
   Collega il fallimento topologico al sintomo utente e spiega perche il problema non puo essere attribuito con fiducia a una sola causa elettrica.

4. **Scenari di correzione proposti**
   Proponi al massimo 3 scenari candidati.
   In questa modalita gli scenari possono essere anche di correzione topologica o graph-correction.
   Ogni scenario deve dire chiaramente se e `eseguibile ora` oppure `futuro / non ancora eseguibile`.
   Se non e eseguibile ora, spiega quale informazione o quale correzione del graph servirebbe prima di rieseguire SPICE.
   Non proporre solo prove elettriche semplici se le evidenze dicono che la topologia di base non e affidabile.

5. **Limiti e dato mancante**
   Spiega qual e il dato mancante piu importante per sbloccare la diagnosi, per esempio l'immagine reale o una correzione della topologia riconosciuta.

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
   Per scenari di correzione topologica non ancora eseguibili puoi aggiungere anche `execution_mode` e `required_evidence`.
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

In questa modalita, se la correzione topologica dipende davvero dall'immagine, usa normalmente `si`.

## Final task

Analyze the user problem using the evidence above.
Explain what the simulation result means, whether it supports the user problem, and what can or cannot be concluded.
If ngspice failed, focus on the error evidence and explain why the current circuit is not diagnostically reliable.
If ngspice failed with strong topology evidence, switch to topology-correction reasoning and make it explicit when a proposed scenario is future/not yet executable.
If ngspice succeeded, connect the simulated node voltages, currents, skipped components and warnings to the user problem.
If the question is about already executed scenarios, use the executed scenario evidence and clearly identify the strongest outcome.
When suggesting new future diagnostic scenarios, present them only as controlled SPICE-verifiable hypotheses.
Keep scenarios natural and minimally invasive before proposing topology or Graph JSON corrections.
