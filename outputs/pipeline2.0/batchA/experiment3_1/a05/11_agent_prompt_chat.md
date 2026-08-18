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
- Keep the user-facing structure stable across answers: use explicit headings such as `Scenari proposti`, `Conclusione provvisoria` and `Conclusione finale` whenever they are relevant.
- The ordinary reasoning should stay concise and readable; the scenario list should look operational, not like a long free-form essay.
- If executed scenario evidence is available, use it to answer questions about which scenario explains or resolves the problem.
- When discussing executed scenarios, distinguish the controlled action from the diagnostic outcome.
- For questions about which scenario resolves the problem, do not merely list scenarios: identify the strongest scenario and justify it from scenario_comparison.json.
- Treat `resolved_candidate` with `stop_automation=true` as the strongest executed-scenario outcome.
- Treat `partially_resolved` as supporting diagnostic evidence, not as the main resolving scenario when a resolved_candidate exists.
- Treat `not_resolved` as not sufficient by itself, not automatically useless.
- A `not_resolved` scenario may still be an enabling condition for a combined scenario when it closes a switch, creates a reference path, completes a current path, or supplies a precondition missing in another scenario.
- In the initial answer for a circuit, propose only first-pass scenarios and do not propose combined scenarios.
- Combined scenarios are allowed only after scenario evidence exists and the user explicitly asks what to try next.
- Every next scenario must be executable from the base run on its own, because scenario runs do not inherit modifications from earlier scenario folders.
- If a next scenario needs an enabling condition demonstrated by an earlier scenario, include that enabling action again in the new scenario JSON.
- If the user asks what to try next after executed scenarios, propose the next most informative scenario based on scenario_comparison.json.
- If the user explicitly asks for a final conclusion, a final diagnosis, a summary of executed scenarios, or whether it makes sense to stop, switch to final-conclusion mode instead of default next-scenario mode.
- In final-conclusion mode, use the executed scenarios and their comparisons as the primary evidence, together with the base run.
- In final-conclusion mode, do not automatically generate another scenario just because the budget is not exhausted.
- In final-conclusion mode, suggest one more scenario only if it is clearly the single remaining decisive test and explain why the already executed scenarios are not enough without it.
- In final-conclusion mode, if the executed evidence already points to a structural limit, a topological ambiguity, or an inconclusive but bounded diagnosis, say that clearly instead of forcing another electrical scenario.
- If one executed scenario already changed the nodes, branches or currents most closely tied to the user symptom, prefer extending that proven direction before proposing a weaker exploratory source-value change.
- Prefer a minimal combined scenario built around the strongest symptom-linked evidence before proposing a generic source-value variation, unless the source itself is the strongest evidence-backed hypothesis.
- Prefer `change_component_value` when the hypothesis can be tested by varying the value of an already emitted resistor, capacitor, inductor or equivalent simple component.
- Use `change_source_value` only for existing SPICE sources, not for passive components.
- Use `add_voltage_source_between_nodes` when the base netlist lacks a realistic external excitation and the natural diagnostic move is to power the circuit from existing interface nodes such as connector pins, supply labels or input/return nodes.
- Prefer `add_voltage_source_between_nodes` over `drive_node_voltage` when the goal is to energize the whole circuit or a whole input path, not only to isolate a single internal branch node.
- Use `drive_node_voltage` mainly for controlled isolation tests or when no more natural value/source/state action is available.
- Use `add_resistor_between_nodes` when the hypothesis is not a missing ideal continuity, but a missing or too-weak resistive branch such as a pull-up, pull-down, shunt or additional bias path between two existing nodes.
- For `add_resistor_between_nodes`, provide a concrete resistor value and prefer simple plausible values already present in the circuit scale, for example `1k`, `10k`, `33k`, `47k`, `100k`, rather than arbitrary uncommon numbers.
- Do not use `add_resistor_between_nodes` when the real hypothesis is only to vary the value of an already emitted resistor; in that case prefer `change_component_value`.
- Use `feed_nodes_from_source_node` when a node is already powered in the base run, or made powered by another action in the same scenario, and the hypothesis is that this supply should propagate to one or more target branch-input nodes.
- Prefer `feed_nodes_from_source_node` over multiple separate `connect_nodes` only when the diagnostic idea is explicitly supply propagation from one source node to one or more targets.
- Do not use `feed_nodes_from_source_node` when the base netlist has no active source node; in that case prefer `add_voltage_source_between_nodes` for realistic circuit excitation, or `drive_node_voltage` only for a later isolation test.
- Never exceed the scenario budget declared in the manifest.
- If `scenario_budget.last_scenario_available` is true, propose only one final executable scenario.
- If `scenario_budget.budget_exhausted` is true, do not propose any new scenario and provide a final diagnostic conclusion.
- If no executed scenario resolved the problem, consider combined scenarios when previous outcomes provide complementary evidence, including `not_resolved` actions that are electrically enabling.
- Do not combine every previous scenario blindly; explain why each included action is useful and why excluded actions are not included.
- A next combined scenario must be self-contained and use only supported action types.
- A next combined scenario should repeat only the enabling actions it actually needs, not every previously proposed or executed action.
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
- The global budget is at most 5 executed scenarios per circuit.
- In the initial diagnostic answer, the first set of up to 3 scenarios must be simple first-pass candidates, not combined scenarios.
- Each scenario must be readable by a non-SPICE user first, and machine-oriented only in a short technical block after the explanation.
- The user-facing scenario title should describe the diagnostic idea naturally, for example `Alimentare il ramo della lampada`, not only `drive_node_voltage`.
- The technical block should be concise and should not replace the human explanation.
- For executable scenario JSON, use only action types currently supported by the scenario runner unless clearly marked as future/not executable.
- Current scenario families are electrical/drive scenarios (`drive_node_voltage`, `add_voltage_source_between_nodes`, `change_source_value`, `change_component_value`, `close_switch`) and controlled topological scenarios (`connect_nodes`, `add_resistor_between_nodes`, `feed_nodes_from_source_node`).
- Never put `unknown` in `actions[].value`; use a concrete SPICE value such as `5V`, `10V`, `DC 3.3`, or `SIN(0 1 100)`.
- Prefer natural scenarios that directly test the user's symptom using existing nodes, states and values before proposing graph-correction scenarios.
- Prefer `change_component_value` when the hypothesis is about an already emitted resistor, capacitor, inductor, RC constant, bias network or equivalent simple load value.
- Use `change_source_value` only for real SPICE sources already present in the netlist.
- Use `add_voltage_source_between_nodes` when the base netlist lacks a realistic external excitation and the natural diagnostic move is to power the circuit from existing interface nodes such as connector pins, supply labels or input/return nodes.
- Prefer `add_voltage_source_between_nodes` over `drive_node_voltage` when the goal is to energize the whole circuit or a whole input path, not only to isolate a single internal branch node.
- Place `add_voltage_source_between_nodes` on existing external interface nodes whenever possible, not directly on internal load nodes, unless no more natural input nodes exist.
- Use `drive_node_voltage` mainly as an isolation action when a value/source/switch scenario would be less natural.
- Use `connect_nodes` when the hypothesis is a missing continuity, jumper, bridge, wire, connector-to-branch link or controlled path between two nodes that already exist in the node map.
- Use `add_resistor_between_nodes` when the hypothesis requires a new resistive branch between two existing nodes, for example an added bias path, pull-up, pull-down, shunt or weak coupling branch that is not already present in the netlist.
- For `add_resistor_between_nodes`, choose a concrete resistor value and prefer simple circuit-scale values that are already plausible in the current schematic family.
- Prefer `connect_nodes` only when this is more natural than closing an existing switch or driving a real upstream input node.
- Do not use `add_resistor_between_nodes` when the only goal is changing the value of a resistor that already exists in the emitted netlist; use `change_component_value` for that case.
- Use `feed_nodes_from_source_node` when there is a source node that is already powered in the base run, or made powered by another action in the same self-contained scenario, and the hypothesis is that this supply should propagate to one or more target branch-input nodes.
- Prefer `feed_nodes_from_source_node` over multiple separate `connect_nodes` only when the diagnostic idea is explicitly supply propagation from one source node to one or more targets.
- Do not use `feed_nodes_from_source_node` when the base netlist has no active source node; in that case prefer `add_voltage_source_between_nodes` for realistic circuit excitation, or `drive_node_voltage` only for a later isolation test.
- If ngspice failed and the evidence shows strong topology problems, do not stay in simple electrical-test mode: switch to image-guided topology-correction reasoning.
- Prefer acting on existing external inputs, supply labels, connector pins and recognized component states before directly forcing internal load nodes.
- If an upstream input node feeds a load, drive the upstream input first; direct forcing of the load node is a later model-isolation test, not an early natural scenario.
- The top 3 scenarios should be independently executable: if a scenario needs another action first, include that action in the same scenario JSON or present it only as a later follow-up.
- Do not propose combined scenarios in the initial top 3. Combined scenarios are allowed only after earlier scenarios have been executed and the user asks what to try next.
- Because every scenario run starts again from the base run, any next scenario proposed after executed evidence must be executable from the base run on its own.
- If a next scenario depends on an enabling condition demonstrated by an earlier scenario, include that enabling action again in the same `actions` array.
- Do not propose a follow-up scenario that relies on the user mentally carrying over actions from a previous scenario run.
- Do not propose `run_tran` alone when the base operating point does not power the relevant branch; include the required drive/source/state actions in the same scenario.
- If all initially proposed scenarios have been executed and none is a resolved candidate, propose the next most informative scenario instead of stopping.
- If only one executable scenario remains in the budget, propose only one final scenario and make it explicit that a final conclusion must follow after its execution.
- If no executable scenario remains in the budget, do not propose any new scenario: provide a final diagnostic conclusion from the accumulated evidence.
- If the user explicitly asks for a final conclusion, a final diagnosis, a summary of executed scenarios, or whether it makes sense to stop, switch from next-scenario reasoning to final-conclusion reasoning.
- In final-conclusion reasoning, use the executed scenario evidence as the primary basis and do not automatically force a new scenario just because budget still exists.
- In final-conclusion reasoning, propose one more scenario only when it is clearly the single remaining decisive test.
- The next scenario may combine actions, but only combine assumptions that were supported by previous scenario evidence; do not combine all scenarios blindly.
- `not_resolved` means that a scenario was not sufficient by itself; it does not automatically mean the action is useless.
- A `not_resolved` scenario can still be an enabling action in a combined scenario if it closes a switch, creates a reference path, completes a current path, or supplies a missing precondition for another useful action.
- When a `not_resolved` scenario is enabling for the next hypothesis, the next hypothesis must be proposed as a new self-contained scenario that includes both the enabling action and the new action.
- When one executed scenario has already changed the symptom-linked nodes or branches, prefer extending that proven direction before proposing a weaker exploratory source-change scenario.
- Prefer combining the strongest symptom-linked scenario with an enabling action before proposing a generic source-value variation, unless the source itself is the strongest evidence-backed hypothesis.
- When proposing a combined scenario, explain why each included action is justified and why excluded actions are not included yet.
- If ngspice succeeds and graph/node-map evidence is internally coherent, the first scenarios should be value, source, analysis or state tests, not topology rewrites.
- If ngspice failed and the evidence shows no ground/reference, critical singleton nodes, skipped critical components, or isolated branches, prefer topology-correction scenarios over simple drive/source scenarios.
- In topology-correction mode, the first 3 scenarios may include future graph-correction or image-guided reconstruction scenarios even if the current runner cannot execute them yet.
- When a topology-correction scenario is not executable yet, clearly mark it as future/not executable instead of pretending it can already be run by the current pipeline.
- Avoid `disconnect_terminal` and `move_terminal` in the top 3 scenarios unless structured evidence strongly suggests a graph/topology error.
- Use `connect_nodes` in the top 3 only when the main hypothesis is a missing continuity between already recognized nodes, not as a generic shortcut for powering a branch.
- Use `feed_nodes_from_source_node` in the top 3 only when the base evidence clearly identifies one powered source node and one or more unpowered branch-input target nodes.
- If topology repair is only a later possibility, mention it as a next step instead of making it one of the first 3 scenarios.
- Do not propose graph-correction scenarios in the top 3 unless there is strong structured evidence that the Graph JSON is wrong.
- Scenarios can be iterative: if one scenario does not explain the problem, propose the next one or a combination of previous validated assumptions.

## User problem

Adesso che VMON_INPUT e alimentato e il nodo letto dal voltmetro sale a 5 V, qual e la conclusione diagnostica piu probabile? Ha ancora senso provare un altro scenario, oppure il problema principale e gia localizzato?

## Circuit metadata

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

## Available artifacts

- `graph`: available, path=`outputs\pipeline2.0\batchA\experiment3_1\a05\01_graph.json`
- `normalized_circuit`: available, path=`outputs\pipeline2.0\batchA\experiment3_1\a05\02_normalized_circuit.json`
- `node_map`: available, path=`outputs\pipeline2.0\batchA\experiment3_1\a05\03_node_map.json`
- `values_bound`: available, path=`outputs\pipeline2.0\batchA\experiment3_1\a05\04_values_bound.json`
- `component_rules`: available, path=`outputs\pipeline2.0\batchA\experiment3_1\a05\06_component_rules.json`
- `netlist`: available, path=`outputs\pipeline2.0\batchA\experiment3_1\a05\07_netlist.cir`
- `spice_emit_report`: available, path=`outputs\pipeline2.0\batchA\experiment3_1\a05\07_spice_emit_report.json`
- `spice_run`: available, path=`outputs\pipeline2.0\batchA\experiment3_1\a05\08_spice_run.json`
- `ngspice_stdout`: available, path=`outputs\pipeline2.0\batchA\experiment3_1\a05\08_ngspice_stdout.txt`
- `ngspice_stderr`: available, path=`outputs\pipeline2.0\batchA\experiment3_1\a05\08_ngspice_stderr.txt`
- `tran_csv`: missing, path=`None`
- `tran_plot_png`: missing, path=`None`
- `tran_plot_svg`: missing, path=`None`

## Executed scenarios index

- `scenario_1`: title=`Alimentare l’ingresso VMON_INPUT dal connettore`, status=`spice_success`, spice=`success`, outcome=`resolved_candidate`, stop_automation=`True`, changed=`2/2`

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

Interpretation rule for scenario questions:
- The best scenario is the one indicated by `best_scenario_id`, unless direct evidence contradicts it.
- A `resolved_candidate` with `stop_automation=true` is the main resolving candidate.
- `partially_resolved` scenarios can confirm supporting hypotheses but should not be presented as the scenario that solved the problem when a resolved candidate exists.

## Scenario budget

```json
{
  "max_executable_scenarios": 5,
  "executed_scenarios_count": 1,
  "remaining_executable_scenarios": 4,
  "budget_exhausted": false,
  "last_scenario_available": false,
  "policy": "At most 5 scenarios can be executed for the same circuit. When only one scenario remains, the agent should propose a single final scenario. When no scenario remains, the agent must stop proposing new scenarios and provide a final diagnostic conclusion."
}
```

## Image access policy

- Included by default: `False`
- Can be requested: `True`
- Path: `data\batchA\a05.png`
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
A single circuit should not exceed 5 executed scenarios in total.

Scenario priority:

1. Prefer the least invasive scenario that directly tests the observed symptom.
2. Prefer actions on existing connector pins, supply labels, source values and recognized switch states before forcing internal load nodes.
2b. When the uncertainty is mainly about a resistor, capacitor, inductor or equivalent load value already present in netlist, prefer `change_component_value` before inventing a new internal drive.
3. Prefer value/source/analysis/state scenarios before topology repair when the graph is coherent.
3b. If ngspice failed with strong topology evidence, request the image and move early to topology-correction reasoning instead of staying in simple electrical-test mode.
4. In the first response, propose only single-hypothesis scenarios, not combined scenarios.
5. Test individual hypotheses before proposing combined scenarios.
6. Use combined scenarios only after the individual assumptions are meaningful, and include every required action in the same JSON block.
7. Use graph-correction or topology-rewrite scenarios only when graph or SPICE evidence strongly supports a recognition/topology error.
8. After executed scenarios are available, use their outcomes to decide whether the next scenario should be single-action, combined, or a request for missing evidence.

After executed scenarios:

- If at least one scenario is `resolved_candidate` with `stop_automation=true`, do not propose a new scenario unless the user explicitly asks for further exploration.
- If only one executable scenario remains, propose only one final scenario and state that the next answer after execution must be a final diagnostic conclusion.
- If no executable scenario remains, stop proposing scenarios and provide a final diagnostic conclusion based on all executed evidence.
- If the user asks for a final conclusion before the budget is exhausted, switch to final-conclusion reasoning: summarize the executed scenarios, strengthen or weaken the hypotheses, and avoid proposing a new scenario by default.
- In that final-conclusion reasoning, suggest an additional scenario only if it is clearly the single remaining decisive test.
- If no scenario is resolved and at least one scenario is `partially_resolved`, propose a next scenario that combines only the useful partial assumptions.
- Do not exclude a scenario only because its outcome is `not_resolved`: first decide whether it is irrelevant, or whether it is an enabling condition that may become useful together with another action.
- Treat `not_resolved` but enabling actions as candidates for combined scenarios when they close a switch, create a DC reference, complete a path, or provide a precondition that another scenario lacked.
- If one scenario already changed the nodes or currents most closely tied to the user's symptom, treat that scenario as the main direction for the next step.
- In that case, prefer adding only the minimum enabling action needed around that main direction before testing broader source-value variations.
- If all scenarios are `not_resolved`, explain that the current hypotheses did not work and propose a different minimal hypothesis, or request missing evidence if needed.
- Do not combine all previously proposed scenarios automatically. Combining actions is useful only when the previous results show complementary evidence.
- A combined scenario must be self-contained: include every required action in the same `actions` array.
- Because each scenario run restarts from the base run, a next scenario must not depend on actions applied only in a previous scenario folder.
- If the next hypothesis needs an enabling action already tested earlier, repeat that action inside the new scenario JSON together with the new action.

Naturalness caution:

- If the base run has no realistic external excitation, first consider `add_voltage_source_between_nodes` on the natural circuit interface before directly forcing an internal node.
- If a load is fed through an upstream resistor or connector node, prefer driving that upstream node before directly driving the load terminal.
- Directly driving a load terminal is useful only as a later isolation test for the load model, not as one of the first natural scenarios when an upstream input exists.
- If an existing switch is recognized, a scenario that opens/closes that switch is usually more natural than inventing a new internal drive point.
- A scenario must be executable on its own. Avoid wording such as `after scenario 1, run .tran` unless the technical JSON also includes the actions from scenario 1.
- If `.tran` is useful, make it part of a complete scenario, for example drive a node and run transient analysis in the same scenario.

Topology caution:

- `connect_nodes`, `add_resistor_between_nodes`, `feed_nodes_from_source_node`, `disconnect_terminal` and `move_terminal` belong to controlled topological scenarios.
- `connect_nodes` is the minimal topological scenario: use it for controlled continuity hypotheses between nodes already recognized by the pipeline.
- `add_resistor_between_nodes` is the controlled resistive-branch scenario: use it when the diagnosis calls for adding a new resistor between two existing nodes instead of changing an already emitted resistor value.
- `feed_nodes_from_source_node` is the supply-propagation scenario: use it when a known powered node should feed one or more target branch-input nodes.
- Do not put heavy topology-rewrite actions in the first 3 scenarios when ngspice succeeds and the graph/node map are coherent.
- In coherent runs, `connect_nodes` can still appear among the first 3 scenarios when the evidence specifically suggests a missing bridge or continuity path between existing nodes.
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
- The executable technical JSON should use only the currently available scenario primitives: `drive_node_voltage`, `add_voltage_source_between_nodes`, `change_source_value`, `change_component_value`, `close_switch`, `connect_nodes`, `add_resistor_between_nodes`, `feed_nodes_from_source_node`.
- If the scenario is not executable yet, say so explicitly and use future-oriented actions only as a structured proposal.
- For `change_source_value`, choose a concrete value that makes the diagnostic comparison meaningful; do not write `unknown`.
- Use `change_source_value` as the next scenario only when varying the existing source is more evidence-backed than extending an already successful symptom-linked node or state test.
- For `change_component_value`, target a component name already visible in the emitted netlist, for example `Rresistor22_4`, or a component id that clearly resolves to it, for example `resistor22.4`.
- Use `change_component_value` for bias resistors, RC timing parts, simple loads or equivalent components, not for sources or transistor/diode models.
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

Example external-supply scenario action:

```json
{
  "scenario_id": "scenario_2",
  "title": "Alimentare il circuito dal connettore di ingresso",
  "hypothesis": "The extracted netlist stays inactive because the circuit is not receiving a realistic external excitation on its natural interface nodes.",
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
  "compare": ["v(N003)", "v(N001)"]
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

Example component-value scenario action:

```json
{
  "scenario_id": "scenario_3",
  "title": "Ridurre la resistenza di bias della base",
  "hypothesis": "A lower bias resistance should increase the transistor drive if the current bias network is too weak.",
  "actions": [
    {
      "type": "change_component_value",
      "target": "Rresistor22_4",
      "value": "33k"
    }
  ],
  "rerun_from": "07",
  "analysis": "op",
  "compare": ["v(N004)", "v(N005)"]
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

Example connect-nodes scenario action:

```json
{
  "scenario_id": "scenario_2",
  "title": "Collegare il nodo alimentato al ramo LED",
  "hypothesis": "The branch may stay inactive because the powered node is not electrically continuous with the branch input.",
  "actions": [
    {
      "type": "connect_nodes",
      "from": "N002",
      "to": "N003",
      "resistance": "1m"
    }
  ],
  "rerun_from": "07",
  "analysis": "op",
  "compare": ["v(N002)", "v(N003)", "i(Rresistor22_1)"]
}
```

Example add-resistor-between-nodes scenario action:

```json
{
  "scenario_id": "scenario_3",
  "title": "Aggiungere un ramo resistivo di bias verso la base",
  "hypothesis": "The current branch may stay weak because the base or trigger path lacks a useful resistive coupling branch.",
  "actions": [
    {
      "type": "add_resistor_between_nodes",
      "from": "N001",
      "to": "N004",
      "value": "33k"
    }
  ],
  "rerun_from": "07",
  "analysis": "op",
  "compare": ["v(N001)", "v(N004)", "v(N003)"]
}
```

Example feed-nodes scenario action:

```json
{
  "scenario_id": "scenario_3",
  "title": "Propagare il nodo alimentato verso il ramo lampada",
  "hypothesis": "The lamp branch is inactive because the powered source node does not reach the branch input.",
  "actions": [
    {
      "type": "feed_nodes_from_source_node",
      "source_node": "N001",
      "target_nodes": ["N002"],
      "resistance": "1m"
    }
  ],
  "rerun_from": "07",
  "analysis": "op",
  "compare": ["v(N001)", "v(N002)", "v(N004)", "i(Rlamp13_1)"]
}
```

When proposing a scenario, reason about which part of the pipeline would need to be rerun.

Pipeline rerun guidance:

- If the scenario only changes a value, source amplitude, model parameter or analysis command, it may reuse `01_graph.json`, `02_normalized_circuit.json` and `03_node_map.json`, then regenerate from `04_values.py`, `06_component_rules.py`, `07_spice_emit.py` and `08_spice_run.py` as needed.
- If the scenario changes the state of an already recognized component, for example closing an existing switch, it should create a scenario layer and then rerun the first affected step through `08`.
- If the scenario combines actions, for example driving an input node and closing a switch, list both actions in the same JSON block so the scenario is self-contained.
- After scenarios have already been executed, do not write a next scenario as if previous scenario actions were still active; include the required prior action again in the new JSON block.
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

Evidence not available.


## Executed scenario evidence

### scenario_1

- Title: `Alimentare l’ingresso VMON_INPUT dal connettore`
- Scenario dir: `outputs\pipeline2.0\batchA\experiment3_1\a05\scenarios\scenario_1`
- Status: `spice_success`
- SPICE status: `success`

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


## Required answer format

La domanda chiede cosa provare dopo gli scenari gia eseguiti.
Usa gli executed scenario evidence: non ripartire dalla sola base run.
Rispondi in Markdown usando esattamente queste sezioni:

1. **Stato degli scenari eseguiti**
   Riassumi scenario per scenario: outcome, cosa ha cambiato, cosa non ha risolto.

2. **Ragionamento sul prossimo scenario**
   Spiega quali ipotesi precedenti sono utili e quali no.
   Non scartare uno scenario solo perche e `not_resolved`: valuta se e irrilevante oppure se e una condizione abilitante.
   Uno scenario `not_resolved` puo essere abilitante se chiude uno switch, crea un riferimento, completa un percorso di corrente o prepara un'altra azione.
   Non combinare tutti gli scenari automaticamente.
   Combina solo azioni supportate da evidenze complementari.

3. **Scenari proposti**
   Proponi un solo prossimo scenario, oppure dichiara che serve un dato mancante.
   Lo scenario deve essere eseguibile e self-contained.
   Il singolo scenario deve iniziare con `**scenario_X - Titolo naturale**`.
   Usa sempre i campi leggibili `Ipotesi`, `Cosa cambia`, `Cosa verifichiamo`, `Come lo leggiamo`, `Se non basta`.
   Ogni scenario riparte dalla base run: se la nuova ipotesi richiede una condizione abilitante gia vista in uno scenario precedente, reincludi quell'azione nello stesso array `actions`.
   Se e combinato, ogni azione necessaria deve comparire nello stesso array `actions`.

4. **Cosa mi aspetto di verificare**
   Indica quali grandezze o warning devono cambiare per considerarlo utile.

5. **Blocco tecnico per pipeline**
   Includi un blocco JSON breve con `scenario_id`, `title`, `hypothesis`, `actions`, `rerun_from`, `analysis`, `compare`.
   Usa solo primitive supportate: scenari elettrici / di pilotaggio (`drive_node_voltage`, `add_voltage_source_between_nodes`, `change_source_value`, `change_component_value`, `close_switch`) e scenari topologici controllati (`connect_nodes`, `add_resistor_between_nodes`, `feed_nodes_from_source_node`).
   Non usare `unknown` nei valori.

6. **Conclusione provvisoria**
   Chiudi con una sintesi breve: che cosa abbiamo capito finora e perche questo e il prossimo scenario migliore.

`Richiede immagine: si/no`

## Final task

Analyze the user problem using the evidence above.
Explain what the simulation result means, whether it supports the user problem, and what can or cannot be concluded.
If ngspice failed, focus on the error evidence and explain why the current circuit is not diagnostically reliable.
If ngspice failed with strong topology evidence, switch to topology-correction reasoning and make it explicit when a proposed scenario is future/not yet executable.
If ngspice succeeded, connect the simulated node voltages, currents, skipped components and warnings to the user problem.
If the question is about already executed scenarios, use the executed scenario evidence and clearly identify the strongest outcome.
When suggesting new future diagnostic scenarios, present them only as controlled SPICE-verifiable hypotheses.
Keep scenarios natural and minimally invasive before proposing topology or Graph JSON corrections.
