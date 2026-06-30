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

Ho ridotto sia l'ingresso sia VVCC e l'uscita cambia davvero, ma resta ancora non pulita. Quale elemento del punto di lavoro o della rete di bias è adesso il più sospetto?

## Circuit metadata

- Batch: `batchA`
- Circuit: `a06`
- Agent mode: `graph_grounded_readonly`

## Technical summary

```json
{
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_message": "ngspice completed successfully.",
  "emitted_elements": 13,
  "skipped_elements": 7,
  "emit_warnings_count": 0,
  "skipped_components_count": 7,
  "node_count": 9,
  "ground_groups_count": 4,
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

## Available artifacts

- `graph`: available, path=`outputs\pipeline2.0\batchA\a06\01_graph.json`
- `normalized_circuit`: available, path=`outputs\pipeline2.0\batchA\a06\02_normalized_circuit.json`
- `node_map`: available, path=`outputs\pipeline2.0\batchA\a06\03_node_map.json`
- `values_bound`: available, path=`outputs\pipeline2.0\batchA\a06\04_values_bound.json`
- `component_rules`: available, path=`outputs\pipeline2.0\batchA\a06\06_component_rules.json`
- `netlist`: available, path=`outputs\pipeline2.0\batchA\a06\07_netlist.cir`
- `spice_emit_report`: available, path=`outputs\pipeline2.0\batchA\a06\07_spice_emit_report.json`
- `spice_run`: available, path=`outputs\pipeline2.0\batchA\a06\08_spice_run.json`
- `ngspice_stdout`: available, path=`outputs\pipeline2.0\batchA\a06\08_ngspice_stdout.txt`
- `ngspice_stderr`: available, path=`outputs\pipeline2.0\batchA\a06\08_ngspice_stderr.txt`
- `tran_csv`: available, path=`outputs\pipeline2.0\batchA\a06\08_tran.csv`
- `tran_plot_png`: available, path=`outputs\pipeline2.0\batchA\a06\08_tran_plot.png`
- `tran_plot_svg`: missing, path=`None`

## Executed scenarios index

- `scenario_1`: title=`Ridurre l'ampiezza del segnale di ingresso`, status=`spice_success`, spice=`success`, outcome=`partially_resolved`, stop_automation=`False`, changed=`3/3`
- `scenario_2`: title=`Ridurre l'alimentazione VVCC`, status=`spice_success`, spice=`success`, outcome=`partially_resolved`, stop_automation=`False`, changed=`3/3`

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
      "title": "Ridurre l'ampiezza del segnale di ingresso",
      "status": "spice_success",
      "spice_status": "success",
      "outcome_status": "partially_resolved",
      "outcome_label": "Partially resolved",
      "outcome_reason": "The scenario changed the circuit response, but the evidence is not strong enough to stop automatically.",
      "stop_automation": false,
      "comparison_summary": {
        "requested_count": 3,
        "changed_count": 3,
        "activated_count": 0,
        "missing_count": 0
      },
      "quantity_summary": {
        "changed": [
          "v(N006)",
          "v(N004)",
          "v(N005)"
        ],
        "unchanged": [],
        "missing": []
      },
      "score": 23
    },
    {
      "scenario_id": "scenario_2",
      "title": "Ridurre l'alimentazione VVCC",
      "status": "spice_success",
      "spice_status": "success",
      "outcome_status": "partially_resolved",
      "outcome_label": "Partially resolved",
      "outcome_reason": "The scenario changed the circuit response, but the evidence is not strong enough to stop automatically.",
      "stop_automation": false,
      "comparison_summary": {
        "requested_count": 3,
        "changed_count": 3,
        "activated_count": 0,
        "missing_count": 0
      },
      "quantity_summary": {
        "changed": [
          "v(N004)",
          "v(N005)",
          "i(vvcc#branch)"
        ],
        "unchanged": [],
        "missing": []
      },
      "score": 23
    }
  ]
}
```

Interpretation rule for scenario questions:
- The best scenario is the one indicated by `best_scenario_id`, unless direct evidence contradicts it.
- A `resolved_candidate` with `stop_automation=true` is the main resolving candidate.
- `partially_resolved` scenarios can confirm supporting hypotheses but should not be presented as the scenario that solved the problem when a resolved candidate exists.

## Image access policy

- Included by default: `False`
- Can be requested: `True`
- Path: `data\batchA\a06.jpg`
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
- Path: `outputs\pipeline2.0\batchA\a06\01_graph.json`

```json
{
  "image_id": "a06",
  "image_name": "a06.jpg",
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
      "component_id": "terminal26.1",
      "instance_id": "26.1",
      "class_name": "Terminal",
      "terminals": [
        {
          "terminal_id": "terminal26.1_t1",
          "name": "t1",
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
      "component_id": "terminal26.2",
      "instance_id": "26.2",
      "class_name": "Terminal",
      "terminals": [
        {
          "terminal_id": "terminal26.2_t1",
          "name": "t1",
          "relative_position": "top"
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
      "component_id": "resistor22.6",
      "instance_id": "22.6",
      "class_name": "Resistor",
      "terminals": [
        {
          "terminal_id": "resistor22.6_t1",
          "name": "t1",
          "relative_position": "top"
        },
        {
          "terminal_id": "resistor22.6_t2",
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
    },
    {
      "component_id": "terminal26.3",
      "instance_id": "26.3",
      "class_name": "Terminal",
      "terminals": [
        {
          "terminal_id": "terminal26.3_t1",
          "name": "t1",
          "relative_position": "left"
        }
      ]
    }
  ],
  "terminal_metadata": {},
  "graph": {
    "capacitor4.1_t1": [
      "resistor22.1_t2"
    ],
    "capacitor4.1_t2": [
      "npn_transistor18.1_B",
      "resistor22.2_t2",
      "resistor22.3_t1"
    ],
    "capacitor4.2_t1": [
      "npn_transistor18.1_E",
      "resistor22.5_t1"
    ],
    "capacitor4.2_t2": [
      "gnd9.3_t1"
    ],
    "capacitor4.3_t1": [
      "npn_transistor18.1_C",
      "resistor22.4_t2"
    ],
    "capacitor4.3_t2": [
      "resistor22.6_t1",
      "terminal26.3_t1"
    ],
    "gnd9.1_t1": [
      "signal_source23.1_t2"
    ],
    "gnd9.2_t1": [
      "resistor22.3_t2"
    ],
    "gnd9.3_t1": [
      "capacitor4.2_t2"
    ],
    "gnd9.4_t1": [
      "resistor22.6_t2"
    ],
    "npn_transistor18.1_B": [
      "capacitor4.1_t2",
      "resistor22.2_t2",
      "resistor22.3_t1"
    ],
    "npn_transistor18.1_C": [
      "capacitor4.3_t1",
      "resistor22.4_t2"
    ],
    "npn_transistor18.1_E": [
      "capacitor4.2_t1",
      "resistor22.5_t1"
    ],
    "resistor22.1_t1": [
      "signal_source23.1_t1"
    ],
    "resistor22.1_t2": [
      "capacitor4.1_t1"
    ],
    "resistor22.2_t1": [
      "resistor22.4_t1",
      "terminal26.1_t1"
    ],
    "resistor22.2_t2": [
      "capacitor4.1_t2",
      "npn_transistor18.1_B",
      "resistor22.3_t1"
    ],
    "resistor22.3_t1": [
      "capacitor4.1_t2",
      "npn_transistor18.1_B",
      "resistor22.2_t2"
    ],
    "resistor22.3_t2": [
      "gnd9.2_t1"
    ],
    "resistor22.4_t1": [
      "resistor22.2_t1",
      "terminal26.1_t1"
    ],
    "resistor22.4_t2": [
      "capacitor4.3_t1",
      "npn_transistor18.1_C"
    ],
    "resistor22.5_t1": [
      "capacitor4.2_t1",
      "npn_transistor18.1_E"
    ],
    "resistor22.5_t2": [
      "terminal26.2_t1"
    ],
    "resistor22.6_t1": [
      "capacitor4.3_t2",
      "terminal26.3_t1"
    ],
    "resistor22.6_t2": [
      "gnd9.4_t1"
    ],
    "signal_source23.1_t1": [
      "resistor22.1_t1"
    ],
    "signal_source23.1_t2": [
      "gnd9.1_t1"
    ],
    "terminal26.1_t1": [
      "resistor22.2_t1",
      "resistor22.4_t1"
    ],
    "terminal26.2_t1": [
      "resistor22.5_t2"
    ],
    "terminal26.3_t1": [
      "capacitor4.3_t2",
      "resistor22.6_t1"
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
- Path: `outputs\pipeline2.0\batchA\a06\03_node_map.json`

```json
{
  "circuit_id": "a06",
  "source_format": "pipeline2.0_node_map",
  "nodes": [
    {
      "node_id": "0",
      "kind": "ground",
      "terminals": [
        "capacitor4.2_t2",
        "gnd9.1_t1",
        "gnd9.2_t1",
        "gnd9.3_t1",
        "gnd9.4_t1",
        "resistor22.3_t2",
        "resistor22.6_t2",
        "signal_source23.1_t2"
      ],
      "terminal_count": 8,
      "source_groups": [
        [
          "capacitor4.2_t2",
          "gnd9.3_t1"
        ],
        [
          "gnd9.1_t1",
          "signal_source23.1_t2"
        ],
        [
          "gnd9.2_t1",
          "resistor22.3_t2"
        ],
        [
          "gnd9.4_t1",
          "resistor22.6_t2"
        ]
      ]
    },
    {
      "node_id": "N001",
      "kind": "normal",
      "terminals": [
        "capacitor4.1_t1",
        "resistor22.1_t2"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N002",
      "kind": "normal",
      "terminals": [
        "capacitor4.1_t2",
        "npn_transistor18.1_B",
        "resistor22.2_t2",
        "resistor22.3_t1"
      ],
      "terminal_count": 4
    },
    {
      "node_id": "N003",
      "kind": "normal",
      "terminals": [
        "capacitor4.2_t1",
        "npn_transistor18.1_E",
        "resistor22.5_t1"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N004",
      "kind": "normal",
      "terminals": [
        "capacitor4.3_t1",
        "npn_transistor18.1_C",
        "resistor22.4_t2"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N005",
      "kind": "normal",
      "terminals": [
        "capacitor4.3_t2",
        "resistor22.6_t1",
        "terminal26.3_t1"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N006",
      "kind": "normal",
      "terminals": [
        "resistor22.1_t1",
        "signal_source23.1_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N007",
      "kind": "normal",
      "terminals": [
        "resistor22.2_t1",
        "resistor22.4_t1",
        "terminal26.1_t1"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N008",
      "kind": "normal",
      "terminals": [
        "resistor22.5_t2",
        "terminal26.2_t1"
      ],
      "terminal_count": 2
    }
  ],
  "terminal_to_node": {
    "capacitor4.1_t1": "N001",
    "capacitor4.1_t2": "N002",
    "capacitor4.2_t1": "N003",
    "capacitor4.2_t2": "0",
    "capacitor4.3_t1": "N004",
    "capacitor4.3_t2": "N005",
    "gnd9.1_t1": "0",
    "gnd9.2_t1": "0",
    "gnd9.3_t1": "0",
    "gnd9.4_t1": "0",
    "npn_transistor18.1_B": "N002",
    "npn_transistor18.1_C": "N004",
    "npn_transistor18.1_E": "N003",
    "resistor22.1_t1": "N006",
    "resistor22.1_t2": "N001",
    "resistor22.2_t1": "N007",
    "resistor22.2_t2": "N002",
    "resistor22.3_t1": "N002",
    "resistor22.3_t2": "0",
    "resistor22.4_t1": "N007",
    "resistor22.4_t2": "N004",
    "resistor22.5_t1": "N003",
    "resistor22.5_t2": "N008",
    "resistor22.6_t1": "N005",
    "resistor22.6_t2": "0",
    "signal_source23.1_t1": "N006",
    "signal_source23.1_t2": "0",
    "terminal26.1_t1": "N007",
    "terminal26.2_t1": "N008",
    "terminal26.3_t1": "N005"
  },
  "component_terminal_nodes": {
    "capacitor4.1": {
      "t1": "N001",
      "t2": "N002"
    },
    "capacitor4.2": {
      "t1": "N003",
      "t2": "0"
    },
    "capacitor4.3": {
      "t1": "N004",
      "t2": "N005"
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
    "npn_transistor18.1": {
      "B": "N002",
      "C": "N004",
      "E": "N003"
    },
    "resistor22.1": {
      "t1": "N006",
      "t2": "N001"
    },
    "resistor22.2": {
      "t1": "N007",
      "t2": "N002"
    },
    "resistor22.3": {
      "t1": "N002",
      "t2": "0"
    },
    "resistor22.4": {
      "t1": "N007",
      "t2": "N004"
    },
    "resistor22.5": {
      "t1": "N003",
      "t2": "N008"
    },
    "resistor22.6": {
      "t1": "N005",
      "t2": "0"
    },
    "signal_source23.1": {
      "t1": "N006",
      "t2": "0"
    },
    "terminal26.1": {
      "t1": "N007"
    },
    "terminal26.2": {
      "t1": "N008"
    },
    "terminal26.3": {
      "t1": "N005"
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
    "nodes_count": 9,
    "normal_nodes_count": 8,
    "ground_nodes_count": 1,
    "ground_groups_count": 4,
    "terminal_to_node_count": 30,
    "singleton_nodes_count": 0
  }
}
```

### values_bound

- Role: Values and labels bound to graph components.
- Path: `outputs\pipeline2.0\batchA\a06\04_values_bound.json`

```json
{
  "circuit_id": "a06",
  "source_format": "pipeline2.0_values_bound",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_manual_values\\batchA\\a06_values.yaml",
  "supplies": {
    "VCC": {
      "terminal": "terminal26.1_t1",
      "value": 12,
      "unit": "V",
      "reference": 0,
      "type": "dc",
      "source": "manual_from_image_label",
      "label_text": "VCC 12 V",
      "node": "N007"
    },
    "VEE": {
      "terminal": "terminal26.2_t1",
      "value": 0,
      "unit": "V",
      "reference": 0,
      "type": "dc",
      "source": "manual_from_image_label",
      "label_text": "VEE 0 V",
      "node": "N008"
    }
  },
  "components": {
    "capacitor4.1": {
      "class_name": "Capacitor",
      "terminal_nodes": {
        "t1": "N001",
        "t2": "N002"
      },
      "value_data": {
        "value": 1,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "Cc1 1 uF"
      },
      "status": "bound"
    },
    "capacitor4.2": {
      "class_name": "Capacitor",
      "terminal_nodes": {
        "t1": "N003",
        "t2": "0"
      },
      "value_data": {
        "value": 100,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "CE 100 uF"
      },
      "status": "bound"
    },
    "capacitor4.3": {
      "class_name": "Capacitor",
      "terminal_nodes": {
        "t1": "N004",
        "t2": "N005"
      },
      "value_data": {
        "value": 10,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "Cc2 10 uF"
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
    "npn_transistor18.1": {
      "class_name": "NPN_Transistor",
      "terminal_nodes": {
        "B": "N002",
        "C": "N004",
        "E": "N003"
      },
      "value_data": {
        "model": "2N2222",
        "source": "manual_assumption",
        "label_text": "NPN transistor"
      },
      "status": "bound"
    },
    "resistor22.1": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N006",
        "t2": "N001"
      },
      "value_data": {
        "value": 1,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "Rs 1 kOhm"
      },
      "status": "bound"
    },
    "resistor22.2": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N007",
        "t2": "N002"
      },
      "value_data": {
        "value": 100,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "100 kOhm"
      },
      "status": "bound"
    },
    "resistor22.3": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N002",
        "t2": "0"
      },
      "value_data": {
        "value": 47,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "47 kOhm"
      },
      "status": "bound"
    },
    "resistor22.4": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N007",
        "t2": "N004"
      },
      "value_data": {
        "value": 6.8,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "6.8 kOhm"
      },
      "status": "bound"
    },
    "resistor22.5": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N003",
        "t2": "N008"
      },
      "value_data": {
        "value": 3.9,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "3.9 kOhm"
      },
      "status": "bound"
    },
    "resistor22.6": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N005",
        "t2": "0"
      },
      "value_data": {
        "value": 10,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "RL 10 kOhm"
      },
      "status": "bound"
    },
    "signal_source23.1": {
      "class_name": "Signal_Source",
      "terminal_nodes": {
        "t1": "N006",
        "t2": "0"
      },
      "value_data": {
        "type": "sin",
        "waveform": "sin",
        "value": 1,
        "unit": "V",
        "offset": 0,
        "amplitude": 1,
        "frequency": 100,
        "frequency_unit": "Hz",
        "source": "manual_from_image_label",
        "label_text": "vs AC 1",
        "note": "Frequency not shown in the image; 100 Hz is assumed for transient simulation."
      },
      "status": "bound"
    },
    "terminal26.1": {
      "class_name": "Terminal",
      "terminal_nodes": {
        "t1": "N007"
      },
      "value_data": null,
      "status": "not_required"
    },
    "terminal26.2": {
      "class_name": "Terminal",
      "terminal_nodes": {
        "t1": "N008"
      },
      "value_data": null,
      "status": "not_required"
    },
    "terminal26.3": {
      "class_name": "Terminal",
      "terminal_nodes": {
        "t1": "N005"
      },
      "value_data": null,
      "status": "not_required"
    }
  },
  "nodes": {
    "gnd9.1_t1": {
      "label": "GND",
      "spice_node": 0,
      "source": "graph_json_gnd",
      "node": "0"
    },
    "signal_source23.1_t1": {
      "label": "VS",
      "source": "manual_from_image_label",
      "label_text": "vs AC 1",
      "node": "N006"
    },
    "terminal26.1_t1": {
      "label": "VCC",
      "source": "manual_from_image_label",
      "label_text": "VCC 12 V",
      "node": "N007"
    },
    "terminal26.2_t1": {
      "label": "VEE",
      "spice_node": 0,
      "source": "manual_from_image_label",
      "label_text": "VEE 0 V",
      "node": "N008"
    },
    "terminal26.3_t1": {
      "label": "VOUT",
      "source": "manual_from_image_label",
      "label_text": "vo",
      "node": "N005"
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
    "components_total": 18,
    "bound_components": 11,
    "missing_components": 0,
    "not_required_components": 7,
    "unsupported_components": 0,
    "supplies_count": 2,
    "manual_nodes_count": 5
  }
}
```

### component_rules

- Role: SPICE conversion rules for each component.
- Path: `outputs\pipeline2.0\batchA\a06\06_component_rules.json`

```json
{
  "circuit_id": "a06",
  "source_format": "pipeline2.0_component_rules",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_manual_values\\batchA\\a06_values.yaml",
  "spice_classes_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_spice_classes.yaml",
  "supplies": {
    "VCC": {
      "status": "spice_ready",
      "spice_prefix": "V",
      "emit_as": "independent_voltage_source",
      "nodes": [
        "N007",
        "0"
      ],
      "parameters": {
        "terminal": "terminal26.1_t1",
        "value": 12,
        "unit": "V",
        "reference": 0,
        "type": "dc",
        "source": "manual_from_image_label",
        "label_text": "VCC 12 V",
        "node": "N007"
      }
    },
    "VEE": {
      "status": "spice_ready",
      "spice_prefix": "V",
      "emit_as": "independent_voltage_source",
      "nodes": [
        "N008",
        "0"
      ],
      "parameters": {
        "terminal": "terminal26.2_t1",
        "value": 0,
        "unit": "V",
        "reference": 0,
        "type": "dc",
        "source": "manual_from_image_label",
        "label_text": "VEE 0 V",
        "node": "N008"
      }
    }
  },
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
        "N002"
      ],
      "parameters": {
        "value": 1,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "Cc1 1 uF"
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
        "N003",
        "0"
      ],
      "parameters": {
        "value": 100,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "CE 100 uF"
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
        "N004",
        "N005"
      ],
      "parameters": {
        "value": 10,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "Cc2 10 uF"
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
        "N004",
        "N002",
        "N003"
      ],
      "parameters": {
        "model": "2N2222",
        "source": "manual_assumption",
        "label_text": "NPN transistor"
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
        "N006",
        "N001"
      ],
      "parameters": {
        "value": 1,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "Rs 1 kOhm"
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
        "N007",
        "N002"
      ],
      "parameters": {
        "value": 100,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "100 kOhm"
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
        "0"
      ],
      "parameters": {
        "value": 47,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "47 kOhm"
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
        "N007",
        "N004"
      ],
      "parameters": {
        "value": 6.8,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "6.8 kOhm"
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
        "N003",
        "N008"
      ],
      "parameters": {
        "value": 3.9,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "3.9 kOhm"
      }
    },
    "resistor22.6": {
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
        "value": 10,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "RL 10 kOhm"
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
        "N006",
        "0"
      ],
      "parameters": {
        "type": "sin",
        "waveform": "sin",
        "value": 1,
        "unit": "V",
        "offset": 0,
        "amplitude": 1,
        "frequency": 100,
        "frequency_unit": "Hz",
        "source": "manual_from_image_label",
        "label_text": "vs AC 1",
        "note": "Frequency not shown in the image; 100 Hz is assumed for transient simulation."
      }
    },
    "terminal26.1": {
      "class_name": "Terminal",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "External terminal/label; useful for nodes and interface handling."
    },
    "terminal26.2": {
      "class_name": "Terminal",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "External terminal/label; useful for nodes and interface handling."
    },
    "terminal26.3": {
      "class_name": "Terminal",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "External terminal/label; useful for nodes and interface handling."
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
    "components_total": 18,
    "spice_ready_components": 11,
    "not_emitted_components": 7,
    "measurement_components": 0,
    "missing_components": 0,
    "unsupported_components": 0,
    "pin_aware_components": 0,
    "invalid_components": 0,
    "supplies_ready_count": 2
  }
}
```

### netlist

- Role: Generated SPICE netlist.
- Path: `outputs\pipeline2.0\batchA\a06\07_netlist.cir`

```spice
* pipeline2.0 netlist
* circuit: a06

VVCC N007 0 DC 12
VVEE N008 0 DC 0
Ccapacitor4_1 N001 N002 1u
Ccapacitor4_2 N003 0 100u
Ccapacitor4_3 N004 N005 10u
Qnpn_transistor18_1 N004 N002 N003 2N2222
Rresistor22_1 N006 N001 1k
Rresistor22_2 N007 N002 100k
Rresistor22_3 N002 0 47k
Rresistor22_4 N007 N004 6.8k
Rresistor22_5 N003 N008 3.9k
Rresistor22_6 N005 0 10k
Vsignal_source23_1 N006 0 SIN(0 1 100)

.model 2N2222 NPN(IS=14.34f BF=255.9 VAF=74.03 IKF=0.2847 ISE=14.34f NE=1.307 BR=6.092 NR=1.005 VAR=11.96 IKR=0.0 ISC=0.0 NC=2 RB=10 RC=1 RE=0.1 CJE=22.01p VJE=0.75 MJE=0.377 CJC=7.306p VJC=0.75 MJC=0.3416 TF=411.1p TR=46.91n)

.op
.save all
.tran 0.1ms 50ms

.control
set wr_singlescale
set wr_vecnames
run
wrdata 08_tran.csv time v(N001) v(N002) v(N003) v(N004) v(N005) v(N006) v(N007) v(N008)
.endc
.end

```

### spice_emit_report

- Role: Report of emitted, skipped and warning components.
- Path: `outputs\pipeline2.0\batchA\a06\07_spice_emit_report.json`

```json
{
  "circuit_id": "a06",
  "source_format": "pipeline2.0_spice_emit_report",
  "emitted_elements": 13,
  "skipped_elements": 7,
  "skipped_components": [
    "gnd9.1",
    "gnd9.2",
    "gnd9.3",
    "gnd9.4",
    "terminal26.1",
    "terminal26.2",
    "terminal26.3"
  ],
  "informational_skips": [
    "gnd9.1: structural component not emitted",
    "gnd9.2: structural component not emitted",
    "gnd9.3: structural component not emitted",
    "gnd9.4: structural component not emitted",
    "terminal26.1: structural component not emitted",
    "terminal26.2: structural component not emitted",
    "terminal26.3: structural component not emitted"
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
      "N007",
      "N008"
    ]
  },
  "models": [
    "2N2222"
  ],
  "warnings": []
}
```

### spice_run

- Role: Structured ngspice execution report.
- Path: `outputs\pipeline2.0\batchA\a06\08_spice_run.json`

```json
{
  "source_format": "pipeline2.0_spice_run",
  "status": "success",
  "netlist_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a06\\07_netlist.cir",
  "command": [
    "C:\\Users\\m.profilo\\Spice64\\bin\\ngspice_con.exe",
    "-b",
    "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a06\\07_netlist.cir"
  ],
  "exit_code": 0,
  "stdout_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a06\\08_ngspice_stdout.txt",
  "stderr_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a06\\08_ngspice_stderr.txt",
  "tran_raw_csv_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a06\\08_tran_raw.csv",
  "tran_csv_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a06\\08_tran.csv",
  "tran_plot_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a06\\08_tran_plot.png",
  "tran_plot_png_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a06\\08_tran_plot.png",
  "tran_plot_svg_path": null,
  "message": "ngspice completed successfully."
}
```

### ngspice_stdout

- Role: Raw ngspice stdout log.
- Path: `outputs\pipeline2.0\batchA\a06\08_ngspice_stdout.txt`

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
n007                                        12
n008                                         0
n001                                         0
n002                                     3.664
n003                                   3.02446
n004                                   6.76332
n005                                         0
n006                                         0
vsignal_source23_1#branch                    0
vvee#branch                        0.000775502
vvcc#branch                        -0.00085346


No. of Data Rows : 513
Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

No. of Data Rows : 1

Initial Transient Solution
--------------------------

Node                                   Voltage
----                                   -------
n007                                        12
n008                                         0
n001                                         0
n002                                     3.664
n003                                   3.02446
n004                                   6.76332
n005                                         0
n006                                         0
vsignal_source23_1#branch                    0
vvee#branch                        0.000775502
vvcc#branch                        -0.00085346


No. of Data Rows : 513
	Node                                  Voltage
	----                                  -------
	----	-------
	n006                             0.000000e+00
	n005                             0.000000e+00
	n004                             6.763323e+00
	n003                             3.024458e+00
	n002                             3.664000e+00
	n001                             0.000000e+00
	n008                             0.000000e+00
	n007                             1.200000e+01

	Source	Current
	------	-------

	vvcc#branch                      -8.53460e-04
	vvee#branch                      7.755021e-04
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
         ic           5.22697e-07
         ib          -4.41586e-07
         ie           -8.1121e-08
        vbe              0.117031
        vbc              -7.10683
         gm           5.54364e-11
        gpi           9.29591e-07
        gmu           1.29741e-07
         gx                   0.1
         go           1.78726e-14
        cpi           2.34637e-11
        cmu            3.2748e-12
        cbx                     0
       csub                     0

 Capacitor: Fixed capacitor
     device         ccapacitor4_3         ccapacitor4_2         ccapacitor4_1
      model                     C                     C                     C
capacitance                 1e-05                0.0001                 1e-06
      dtemp                     0                     0                     0
     bv_max                 1e+99                 1e+99                 1e+99
          i           0.000276985          -0.000740712          -2.64208e-05
          p            0.00203393           -0.00213998           7.87259e-05

 Resistor: Simple linear resistor
     device         rresistor22_6         rresistor22_5         rresistor22_4
      model
```

> Evidence truncated for prompt size. Use only the visible evidence, and mention if more detail may be needed.

### ngspice_stderr

- Role: Raw ngspice stderr log.
- Path: `outputs\pipeline2.0\batchA\a06\08_ngspice_stderr.txt`

```text

```

### tran_csv

- Role: Clean transient CSV, when .tran data is available.
- Path: `outputs\pipeline2.0\batchA\a06\08_tran.csv`

```csv
time,v(N001),v(N002),v(N003),v(N004),v(N005),v(N006),v(N007),v(N008)
0.0,0.0,3.66400021,3.02445816,6.76332305,0.0,0.0,12.0,0.0
1e-06,0.00036081169,3.66436076,3.02445826,6.72267119,-0.040651451,0.000628318489,12.0,0.0
2e-06,0.00082480557,3.66482432,3.0244585,6.66883839,-0.0944833077,0.00125663673,12.0,0.0
4e-06,0.00180985222,3.66580823,3.02445927,6.5513011,-0.212017535,0.00251327148,12.0,0.0
8e-06,0.00383800229,3.6678326,3.02446265,6.29629448,-0.467010575,0.00502652708,12.0,0.0
1.6e-05,0.00778510105,3.67176587,3.02447742,5.74893213,-1.01431367,0.0100529272,12.0,0.0
3.2e-05,0.0153806208,3.67930545,3.02454302,4.48385839,-2.27912393,0.0201048383,12.0,0.0
5.54392356e-05,0.0226787218,3.68640582,3.02471601,3.13071395,-3.63157567,0.0348264552,12.0,0.0
7.22382873e-05,0.0242267318,3.68767418,3.02486997,3.10383406,-3.65784328,0.0453730717,12.0,0.0
8.86174268e-05,0.0257151811,3.68874429,3.02502233,3.09082567,-3.67025153,0.0556512055,12.0,0.0
0.000109827468,0.0278691171,3.69014507,3.02522226,3.08259928,-3.67769867,0.0689518791,12.0,0.0
0.000152247551,0.0325117139,3.69258001,3.02562992,3.07367616,-3.68506014,0.0955141294,12.0,0.0
0.000224257162,0.0421851204,3.69644741,3.02634384,3.06413569,-3.69194453,0.140439134,12.0,0.0
0.000324257162,0.0588574664,3.70103342,3.02737676,3.05812111,-3.69426601,0.202330232,12.0,0.0
0.000424257162,0.0792817747,3.70507704,3.02845297,3.05493645,-3.69375666,0.263422825,12.0,0.0
0.000524257162,0.103094839,3.708664,3.02956751,3.05296401,-3.6920362,0.323475808,12.0,0.0
0.000624257162,0.129890834,3.71182288,3.03071572,3.05234014,-3.68896957,0.38225218,12.0,0.0
0.000724257162,0.159312307,3.7146159,3.03189317,3.05221344,-3.68540908,0.439519977,12.0,0.0
0.000824257162,0.191103022,3.71719872,3.03309565,3.05236769,-3.68157134,0.49505319,12.0,0.0
0.000924257162,0.224784684,3.71949048,3.03431912,3.05287091,-3.67738864,0.548632654,12.0,0.0
0.00102425716,0.260104856,3.72162115,3.03555969,3.05351334,-3.67307098,0.600046916,12.0,0.0
0.00112425716,0.296613858,3.72350909,3.03681364,3.05438269,-3.66853083,0.649093066,12.0,0.0
0.00122425716,0.334067361,3.72526312,3.0380774,3.05533362,-3.66391368,0.695577543,12.0,0.0
0.00132425716,0.372045916,3.72680262,3.03934755,3.05645069,-3.65913509,0.739316893,12.0,0.0
0.00142425716,0.410321133,3.72822342,3.04062085,3.05762055,-3.6543085,0.780138497,12.0,0.0
0.00152425716,0.448503196,3.72944571,3.04189415,3.05892596,-3.64935126,0.817881251,12.0,0.0
0.00162425716,0.486384138,3.73055715,3.0431645,3.06027085,-3.64435951,0.852396201,12.0,0.0
0.00172425716,0.523602871,3.73147806,3.04442906,3.06173896,-3.6392496,0.883547133,12.0,0.0
0.00182425716,0.55997484,3.73229101,3.04568516,3.0632442,-3.63410768,0.911211108,12.0,0.0
0.00192425716,0.595166769,3.73291551,3.04693024,3.064875,-3.62884541,0.935278948,12.0,0.0
0.00202425716,0.629019815,3.73343116,3.04816191,3.0665515,-3.62354271,0.955655671,12.0,0.0
0.00212425716,0.66122762,3.73375551,3.04937793,3.06837212,-3.61810126,0.972260856,12.0,0.0
0.00222425716,0.691659015,3.73396674,3.05057617,3.07026199,-3.61259605,0.985028973,12.0,0.0
0.00232425716,0.720033561,3.73397899,3.05175468,3.07233811,-3.60691018,0.99390963,12.0,0.0
0.00242425716,0.746249529,3.73387024,3.05291162,3.07453295,-3.60111133,0.99886778,12.0,0.0
0.00252425716,0.770051073,3.73354923,3.05404532,3.07699864,-3.59504756,0.999883855,12.0,0.0
0.00262425716,0.791367478,3.73309468,3.05515424,3.0796862,-3.58876809,0.996953845,12.0,0.0
0.00272425716,0.809965488,3.73240718,3.05623695,3.08282122,-3.58204766,0.990089314,12.0,0.0
0.00282425716,0.825806634,3.7315666,3.05729219,3.08641492,-3.5748755,0.979317353,12.0,0.0
0.00292425716,0.838676848,3.73046109,3.05831878,3.09088098,-3.56683858,0.964680473,12.0,0.0
0.00302425716,0.848570177,3.72917093,3.05931563,3.09647397,-3.55768333,0.946236441,12.0,0.0
0.00312425716,0.85518605,3.72745989,3.06028146,3.1062031,-3.54440316,0.924058045,12.0,0.0
0.00322425716,0.858720424,3.72557504,3.06121463,3.12104725,-3.5260238,0.898232815,12.0,0.0
0.00332425716,0.858718676,3.72309048,3.06210798,3.18666262,-3.45691696,0.86886267,12.0,0.0
0.00342425716,0.835951459,3.69981046,3.06250727,6.96099803,0.318987416,0.836063521,12.0,0.0
0.00352425716,0.803189301,3.66720392,3.06218494,8.98116504,2.33782602,0.799964811,12.0,0.0
0.00362425716,0.767108628,3.63160445,3.06153385,9.60728884,2.96130026,0.760709006,12.0,0.0
0.00372425716,0.725556375,3.59072745,3.06078277,9.78826666,3.13922782,0.718451029,12.0,0.0
0.00382425716,0.682811106,3.54881012,3.06000523,9.82377543,3.17158119,0.673357655,12.0,0.0
0.00392425716,0.635597685,3.50256891,3.05922214,9.83685495,3.18148417,0.625606846,12.0,0.0
0.00402425716,0.587786065,3.45587679,3.05843786,9.83742583,3.17887487,0.575387052,12.0,0.0
0.00412425716,0.535941358,3.40530427,3.05765353,9.84138435,3.17965412,0.522896468,12.0,0.0
0.00422425716,0.483900674,3.35469376,3.05686957,9.8387359,3.17382894,0.468342251,12.0,0.0
0.00432425716,0.428258215,3.30064514,3.05608584,9.84369345,3.17561176,0.411939701,12.0,0.0
0.00442425716,0.372836438,3.24698554,3.05530231,9.84126922,3.17001472,0.353911414,12.0,0.0
0.00452425716,0.314255915,3.19033975,3.05451898,9.84625196,3.17182654,0.294486399,12.0,0.0
0.00462425716,0.256339354,3.13453367,3.05373586,9.84383685,3.1662424,0.233899182,12.0,0.0
0.00472425716,0.195728819,3.07621214,3.05295294,9.84881385,3.16805225,0.172388871,12.0,0.0
0.00482425716,0.136243751,3.01919635,3.05217022,9.84640235,3.16247548,0.11019822,12.0,0.0
0.00492425716,0.0745434914,2.96014691,3.0513877,9.85137295,3.16428271,0.0475726666,12.0,0.0
0.00502425716,0.0144409126,2.90287695,3.05060538,9.84896492,3.15871317,-0.0152406341,12.0,0.0
0.00512425716,-0.0473915206,2.8440587,3.04982326,9.85392915,3.1605178,-0.0779937869,12.0,0.0
0.00522425716,-0.10715092,2.78749383,3.04904134,9.85152455,3.15495545,-0.140439134,12.0,0.0
0.00532425716,-0.168155828,2.72986205,3.04825963,9.85648245,3.1567575,-0.202330232,12.0,0.0
0.00542425716,-0.226616816,2.67495008,3.04747811,9.85408124,3.15120231,-0.263422825,12.0,0.0
0.00552425716,-0.285847491,2.61944112,3.0466968,9.85903285,3.15300181,-0.323475808,12.0,0.0
0.00562425716,-0.342075355,2.56710352,3.04591568,9.856635,3.14745374,-0.38225218,12.0,0.0
0.00572425716,-0.398613012,2.51462005,3.04513477,9.86158033,3.14925072,-0.439519977,12.0,0.0
0.00582425716,-0.451708296,2.46573736,3.04435406,9.85918582,3.14370972,-0.49505319,12.0,0.0
0.00592425716,-0.50467657,2.41713413,3.04357355,9.8641249,3.1455042,-0.548632654,12.0,0.0
0.00602425716,-0.553789258,2.37253213,3.04279323,9.86173369,3.13997025,-0.600046916,12.0,0.0
0.00612425716,-0.602368019,2.32860251,3.04201312,9.86666655,3.14176224,-0.649093066,12.0,0.0
0.00622425716,-0.646710942,2.28903917,3.04123321,9.86427861,3.1362353,-0.695577543,12.0,0.0
0.00632425716,-0.690149237,2.25050258,3.0404535,9.86920527,3.13802483,-0.739316893,12.0,0.0
0.00642425716,-0.72901048,2.21665612,3.03967399,9.86682057,3.13250487,-0.780138497,12.0,0.0
0.00652425716,-0.766638374,2.18414678,3.03889469,9.87174105,3.13429195,-0.817881251,12.0,0.0
0.00662425716,-0.799392508,2.15660497,3.03811558,9.86935957,3.12877894,-0.852396201,12.0,0.0
0.00672425716,-0.830631651,2.13066179,3.03733667,9.87427388,3.13056357,-0.883547133,12.0,0.0
0.00682425716,-0.856749592,2.10991269,3.03655796,9.87189559,3.12505748,-0.911211108,12.0,0.0
0.00692425716,-0.881122341,2.09097085,3.03577945,9.87680375,3.12683969,-0.935278948,12.0,0.0
0.00702425716,-0.900179693,2.07739513,3.03500115,9.87442864,3.12134049,-0.955655671,12.0,0.0
0.00712425716,-0.917316645,2.06577919,3.03422304,9.87933065,3.12312027,-0.972260856,12.0,0.0
0.00722425716,-0.929000397,2.05964407,3.03344513,9.8769587,3.11762794,-0.985028973,12.0,0.0
0.00732425716,-0.938646214,2.05556286,3.03266742,9.88185457,3.1194053,-0.99390963,12.0,0.0
0.00742425716,-0.94275967,2.05701798,3.03188992,9.87948576,3.11391983,-0.99886778,12.0,0.0
0.00752425716,-0.944777109,2.06056128,3.03111261,9.8843755,3.11569475,-0.999883855,12.0,0.0
0.00762425716,-0.941242994,2.06963628,3.0303355,9.88200982,3.11021612,-0.996953845,12.0,0.0
0.00772425716,-0.935615069,2.08077346,3.0295586,9.88689342,3.11198862,-0.990089314,12.0,0.0
0.00782425716,-0.924476746,2.09737752,3.02878189,9.88453086,3.10651681,-0.979317353,12.0,0.0
0.00792425716,-0.911306996,2.11595798,3.02800538,9.88940832,3.10828687,-0.964680473,12.0,0.0
0.00802425716,-0.892727783,2.13988129,3.02722907,9.88704888,3.10282187,-0.946236441,12.0,0.0
0.00812425716,-0.872238641,2.16563684,3.02645296,9.8919202,3.10458949,-0.924058045,12.0,0.0
0.00822425716,-0.846499236,2.19655389,3.02567705,9.88956387,3.09913129,-0.898232815,12.0,0.0
0.00832425716,-0.819028518,2.229103,3.02490134,9.89442904,3.10089645,-0.86886267,12.0,0.0
0.00842425716,-0.786522569,2.2665777,3.02412583,9.89207582,3.09544506,-0.836063521,12.0,0.0
0.00852425716,-0.752518149,2.3054315,3.02335052,9.89693483,3.09720775,-0.799964811,12.0,0.0
0.00862425716,-0.713746054,2.34892408,3.02257541,9.89458472,3.09176315,-0.760709006,12.0,0.0
0.00872425716,-0.673758797,2.3934941,3.0218005,9.89943757,3.093523
```

> Evidence truncated for prompt size. Use only the visible evidence, and mention if more detail may be needed.


## Executed scenario evidence

### scenario_1

- Title: `Ridurre l'ampiezza del segnale di ingresso`
- Scenario dir: `outputs\pipeline2.0\batchA\a06\scenarios\scenario_1`
- Status: `spice_success`
- SPICE status: `success`

#### scenario_definition

- Role: Scenario selected by the user and saved before execution.
- Path: `outputs\pipeline2.0\batchA\a06\scenarios\scenario_1\scenario.json`

```json
{
  "scenario_id": "scenario_1",
  "title": "Ridurre l'ampiezza del segnale di ingresso",
  "hypothesis": "L'uscita e distorta principalmente perche il segnale di ingresso da Vsignal_source23_1 e troppo grande per la regione lineare dello stadio.",
  "actions": [
    {
      "type": "change_source_value",
      "target": "Vsignal_source23_1",
      "value": "SIN(0 0.1 100)"
    }
  ],
  "rerun_from": "07",
  "analysis": "tran",
  "compare": [
    "v(N006)",
    "v(N004)",
    "v(N005)"
  ]
}
```

#### scenario_status

- Role: Current scenario status, SPICE status and diagnostic outcome.
- Path: `outputs\pipeline2.0\batchA\a06\scenarios\scenario_1\scenario_status.json`

```json
{
  "status": "spice_success",
  "stage": "scenario_spice_executed",
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "scenario_id": "scenario_1",
  "requested_index": 1,
  "base_output_dir": "outputs\\pipeline2.0\\batchA\\a06",
  "source_agent_response": "outputs\\pipeline2.0\\batchA\\a06\\11_agent_response_chat.md",
  "scenario_file": "outputs\\pipeline2.0\\batchA\\a06\\scenarios\\scenario_1\\scenario.json",
  "created_or_updated_at": "2026-06-30T18:45:36",
  "next_step": "Continue with another scenario or ask the agent for a refined hypothesis.",
  "spice_executed": true,
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a06\\scenarios\\scenario_1\\run\\08_spice_run.json",
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a06\\scenarios\\scenario_1\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 3,
    "changed_count": 3,
    "activated_count": 0,
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
  "controlled_scenario_report": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a06\\scenarios\\scenario_1\\12_controlled_scenarios.json"
}
```

#### controlled_scenario_report

- Role: Report produced by the controlled scenario runner.
- Path: `outputs\pipeline2.0\batchA\a06\scenarios\scenario_1\12_controlled_scenarios.json`

```json
{
  "source_format": "pipeline2.0_controlled_scenario_report",
  "status": "spice_success",
  "scenario_id": "scenario_1",
  "scenario_title": "Ridurre l'ampiezza del segnale di ingresso",
  "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a06\\scenarios\\scenario_1",
  "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a06\\scenarios\\scenario_1\\run",
  "netlist": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a06\\scenarios\\scenario_1\\run\\07_netlist.cir",
  "applied_actions": [
    {
      "status": "applied",
      "type": "change_source_value",
      "target": "Vsignal_source23_1",
      "resolved_source_name": "Vsignal_source23_1",
      "tried_source_names": [
        "Vsignal_source23_1"
      ],
      "value": "SIN(0 0.1 100)",
      "normalized_source_definition": "SIN(0 0.1 100)",
      "old_line": "Vsignal_source23_1 N006 0 SIN(0 1 100)",
      "new_line": "Vsignal_source23_1 N006 0 SIN(0 0.1 100)",
      "operation": "updated",
      "spice_executed": false,
      "index": 1
    }
  ],
  "unsupported_actions": [],
  "failed_actions": [],
  "spice_executed": true,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a06\\scenarios\\scenario_1\\run\\08_spice_run.json",
  "spice_status": "success",
  "spice_exit_code": 0,
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a06\\scenarios\\scenario_1\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 3,
    "changed_count": 3,
    "activated_count": 0,
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
  "created_or_updated_at": "2026-06-30T18:45:36"
}
```

#### scenario_comparison

- Role: Base-vs-scenario comparison used to evaluate the scenario.
- Path: `outputs\pipeline2.0\batchA\a06\scenarios\scenario_1\scenario_comparison.json`

```json
{
  "source_format": "pipeline2.0_scenario_comparison",
  "scenario_id": "scenario_1",
  "scenario_title": "Ridurre l'ampiezza del segnale di ingresso",
  "base_output_dir": "outputs\\pipeline2.0\\batchA\\a06",
  "scenario_run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a06\\scenarios\\scenario_1\\run",
  "base_stdout": "outputs\\pipeline2.0\\batchA\\a06\\08_ngspice_stdout.txt",
  "scenario_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a06\\scenarios\\scenario_1\\run\\08_ngspice_stdout.txt",
  "base_stderr": "outputs\\pipeline2.0\\batchA\\a06\\08_ngspice_stderr.txt",
  "scenario_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a06\\scenarios\\scenario_1\\run\\08_ngspice_stderr.txt",
  "quantities": [
    {
      "quantity": "v(N006)",
      "base_value": 1.999999632,
      "scenario_value": 0.199999999,
      "delta": -1.7999996329999999,
      "change": "changed",
      "metric": "v(n006).vpp",
      "base_details": {
        "min": -0.999999816,
        "max": 0.999999816,
        "mean": 0.00203509394659454,
        "vpp": 1.999999632
      },
      "scenario_details": {
        "min": -0.0999999995,
        "max": 0.0999999995,
        "mean": 8.977517480768592e-05,
        "vpp": 0.199999999
      }
    },
    {
      "quantity": "v(N004)",
      "base_value": 7.170986879999999,
      "scenario_value": 6.843207230000001,
      "delta": -0.3277796499999983,
      "change": "changed",
      "metric": "v(n004).vpp",
      "base_details": {
        "min": 2.94564482,
        "max": 10.1166317,
        "mean": 8.084793870409356,
        "vpp": 7.170986879999999
      },
      "scenario_details": {
        "min": 3.06044296,
        "max": 9.90365019,
        "mean": 7.224606231666667,
        "vpp": 6.843207230000001
      }
    },
    {
      "quantity": "v(N005)",
      "base_value": 7.47417467,
      "scenario_value": 6.9551392100000005,
      "delta": -0.5190354599999996,
      "change": "changed",
      "metric": "v(n005).vpp",
      "base_details": {
        "min": -4.2926905,
        "max": 3.18148417,
        "mean": 1.09695133535731,
        "vpp": 7.47417467
      },
      "scenario_details": {
        "min": -3.85571627,
        "max": 3.09942294,
        "mean": 0.40650892781729414,
        "vpp": 6.9551392100000005
      }
    }
  ],
  "summary": {
    "requested_count": 3,
    "changed_count": 3,
    "activated_count": 0,
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
  "created_or_updated_at": "2026-06-30T18:45:36"
}
```

### scenario_2

- Title: `Ridurre l'alimentazione VVCC`
- Scenario dir: `outputs\pipeline2.0\batchA\a06\scenarios\scenario_2`
- Status: `spice_success`
- SPICE status: `success`

#### scenario_definition

- Role: Scenario selected by the user and saved before execution.
- Path: `outputs\pipeline2.0\batchA\a06\scenarios\scenario_2\scenario.json`

```json
{
  "scenario_id": "scenario_2",
  "title": "Ridurre l'alimentazione VVCC",
  "hypothesis": "L'uscita resta molto ampia soprattutto per la polarizzazione e l'escursione rese possibili da VVCC, non solo per l'ampiezza di Vsignal_source23_1.",
  "actions": [
    {
      "type": "change_source_value",
      "target": "VVCC",
      "value": "6V"
    }
  ],
  "rerun_from": "07",
  "analysis": "tran",
  "compare": [
    "v(N004)",
    "v(N005)",
    "i(vvcc#branch)"
  ]
}
```

#### scenario_status

- Role: Current scenario status, SPICE status and diagnostic outcome.
- Path: `outputs\pipeline2.0\batchA\a06\scenarios\scenario_2\scenario_status.json`

```json
{
  "status": "spice_success",
  "stage": "scenario_spice_executed",
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "scenario_id": "scenario_2",
  "requested_index": 2,
  "base_output_dir": "outputs\\pipeline2.0\\batchA\\a06",
  "source_agent_response": "outputs\\pipeline2.0\\batchA\\a06\\11_agent_response_chat.md",
  "scenario_file": "outputs\\pipeline2.0\\batchA\\a06\\scenarios\\scenario_2\\scenario.json",
  "created_or_updated_at": "2026-06-30T18:51:09",
  "next_step": "Continue with another scenario or ask the agent for a refined hypothesis.",
  "spice_executed": true,
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a06\\scenarios\\scenario_2\\run\\08_spice_run.json",
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a06\\scenarios\\scenario_2\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 3,
    "changed_count": 3,
    "activated_count": 0,
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
  "controlled_scenario_report": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a06\\scenarios\\scenario_2\\12_controlled_scenarios.json"
}
```

#### controlled_scenario_report

- Role: Report produced by the controlled scenario runner.
- Path: `outputs\pipeline2.0\batchA\a06\scenarios\scenario_2\12_controlled_scenarios.json`

```json
{
  "source_format": "pipeline2.0_controlled_scenario_report",
  "status": "spice_success",
  "scenario_id": "scenario_2",
  "scenario_title": "Ridurre l'alimentazione VVCC",
  "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a06\\scenarios\\scenario_2",
  "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a06\\scenarios\\scenario_2\\run",
  "netlist": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a06\\scenarios\\scenario_2\\run\\07_netlist.cir",
  "applied_actions": [
    {
      "status": "applied",
      "type": "change_source_value",
      "target": "VVCC",
      "resolved_source_name": "VVCC",
      "tried_source_names": [
        "VVCC"
      ],
      "value": "6V",
      "normalized_source_definition": "DC 6",
      "old_line": "VVCC N007 0 DC 12",
      "new_line": "VVCC N007 0 DC 6",
      "operation": "updated",
      "spice_executed": false,
      "index": 1
    }
  ],
  "unsupported_actions": [],
  "failed_actions": [],
  "spice_executed": true,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a06\\scenarios\\scenario_2\\run\\08_spice_run.json",
  "spice_status": "success",
  "spice_exit_code": 0,
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a06\\scenarios\\scenario_2\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 3,
    "changed_count": 3,
    "activated_count": 0,
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
  "created_or_updated_at": "2026-06-30T18:51:09"
}
```

#### scenario_comparison

- Role: Base-vs-scenario comparison used to evaluate the scenario.
- Path: `outputs\pipeline2.0\batchA\a06\scenarios\scenario_2\scenario_comparison.json`

```json
{
  "source_format": "pipeline2.0_scenario_comparison",
  "scenario_id": "scenario_2",
  "scenario_title": "Ridurre l'alimentazione VVCC",
  "base_output_dir": "outputs\\pipeline2.0\\batchA\\a06",
  "scenario_run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a06\\scenarios\\scenario_2\\run",
  "base_stdout": "outputs\\pipeline2.0\\batchA\\a06\\08_ngspice_stdout.txt",
  "scenario_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a06\\scenarios\\scenario_2\\run\\08_ngspice_stdout.txt",
  "base_stderr": "outputs\\pipeline2.0\\batchA\\a06\\08_ngspice_stderr.txt",
  "scenario_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\a06\\scenarios\\scenario_2\\run\\08_ngspice_stderr.txt",
  "quantities": [
    {
      "quantity": "v(N004)",
      "base_value": 7.170986879999999,
      "scenario_value": 3.9618966199999996,
      "delta": -3.2090902599999995,
      "change": "changed",
      "metric": "v(n004).vpp",
      "base_details": {
        "min": 2.94564482,
        "max": 10.1166317,
        "mean": 8.084793870409356,
        "vpp": 7.170986879999999
      },
      "scenario_details": {
        "min": 1.23435417,
        "max": 5.19625079,
        "mean": 4.136987396478599,
        "vpp": 3.9618966199999996
      }
    },
    {
      "quantity": "v(N005)",
      "base_value": 7.47417467,
      "scenario_value": 4.05584567,
      "delta": -3.418329,
      "change": "changed",
      "metric": "v(n005).vpp",
      "base_details": {
        "min": -4.2926905,
        "max": 3.18148417,
        "mean": 1.09695133535731,
        "vpp": 7.47417467
      },
      "scenario_details": {
        "min": -2.74703522,
        "max": 1.30881045,
        "mean": 0.23157705542898835,
        "vpp": 4.05584567
      }
    },
    {
      "quantity": "i(vvcc#branch)",
      "base_value": -0.00085346,
      "scenario_value": -0.000353063,
      "delta": 0.0005003970000000001,
      "change": "changed",
      "metric": "i(vvcc#branch)",
      "base_details": {},
      "scenario_details": {}
    }
  ],
  "summary": {
    "requested_count": 3,
    "changed_count": 3,
    "activated_count": 0,
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
  "created_or_updated_at": "2026-06-30T18:51:09"
}
```


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
   In questa prima risposta proponi solo scenari semplici di primo passaggio, non scenari combinati.
   Non proporre semplici consigli generici: ogni scenario deve essere una ipotesi verificabile.
   Non presentarli come certamente risolutivi: sono candidati da testare.
   Ogni scenario iniziale deve testare una singola ipotesi principale ed essere leggibile da solo.
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

Metti `si` solo se gli output strutturati indicano una probabile incoerenza del Graph JSON oppure se SPICE non e eseguibile in modo utile.
Se l'immagine sarebbe solo una verifica opzionale, metti comunque `no` e cita la verifica opzionale nei limiti.

## Final task

Analyze the user problem using the evidence above.
Explain what the simulation result means, whether it supports the user problem, and what can or cannot be concluded.
If ngspice failed, focus on the error evidence and explain why the current circuit is not diagnostically reliable.
If ngspice failed with strong topology evidence, switch to topology-correction reasoning and make it explicit when a proposed scenario is future/not yet executable.
If ngspice succeeded, connect the simulated node voltages, currents, skipped components and warnings to the user problem.
If the question is about already executed scenarios, use the executed scenario evidence and clearly identify the strongest outcome.
When suggesting new future diagnostic scenarios, present them only as controlled SPICE-verifiable hypotheses.
Keep scenarios natural and minimally invasive before proposing topology or Graph JSON corrections.
