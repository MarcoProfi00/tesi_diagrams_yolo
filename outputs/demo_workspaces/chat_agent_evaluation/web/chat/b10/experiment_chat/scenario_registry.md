# Pipeline 2.0 scenario registry

- Batch: `batchChatAgentEvaluation`
- Experiment: `chat_agent_evaluation`
- Circuit: `b10`
- Max executable scenarios: `5`
- Created at: `2026-07-24T17:14:30`
- Updated at: `2026-07-24T17:16:54`

## Scenario 1 - Chiudere lo switch riconosciuto

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b10\scenarios\scenario_1`

### Hypothesis

switch25.1 aperto isola il ramo che potrebbe trasferire il livello di A verso B.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```

## Scenario 2 - Azzerare il piccolo offset tra N005 e N002

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

Il quasi-zero su B è principalmente determinato da voltage_source31.1 e non da un trasferimento utile dal nodo A.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "Vvoltage_source31_1",
    "value": "0V"
  }
]
```

## Scenario 3 - Ridurre l'isolamento resistivo tra A e B

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

Rresistor22_2 troppo alta impedisce a N002 di seguire N001.

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
