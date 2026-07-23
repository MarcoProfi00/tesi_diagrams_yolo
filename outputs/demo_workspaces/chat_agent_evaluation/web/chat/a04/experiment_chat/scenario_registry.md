# Pipeline 2.0 scenario registry

- Batch: `batchChatAgentEvaluation`
- Experiment: `chat_agent_evaluation`
- Circuit: `a04`
- Max executable scenarios: `5`
- Created at: `2026-07-23T11:36:15`
- Updated at: `2026-07-23T11:51:20`

## Scenario 1 - Alleggerire il carico di uscita

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a04\scenarios\scenario_1`

### Hypothesis

The output node N006 may be too weak because Rresistor22_5 loads the AC-coupled output too heavily.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_5",
    "value": "100k"
  }
]
```

## Scenario 2 - Modificare il bias della base

- Scenario id: `scenario_2`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a04\scenarios\scenario_2`

### Hypothesis

The current base bias set by Rresistor22_1 and Rresistor22_2 may limit useful output swing.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_2",
    "value": "10k"
  }
]
```

## Scenario 3 - Alleggerire il bias della base

- Scenario id: `scenario_3`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a04\scenarios\scenario_3`

### Hypothesis

Since lowering Rresistor22_2 to 10k almost suppresses the output, increasing Rresistor22_2 above the 22k base value may move the transistor to a more favorable operating point and materially increase Vpp at N006.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_2",
    "value": "33k"
  }
]
```

## Scenario 4 - Aumentare il condensatore di accoppiamento C1

- Scenario id: `scenario_4`
- Status: `executed`
- Outcome: `resolved_candidate`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_3`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a04\scenarios\scenario_4`

### Hypothesis

If Ccapacitor4_1 is causing excessive attenuation at 100 Hz, increasing its value should improve signal transfer from N002 to N003 and produce a larger output swing at N006.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Ccapacitor4_1",
    "value": "1u"
  }
]
```
