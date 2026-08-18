# Pipeline 2.0 scenario registry

- Batch: `batchChatAgentEvaluation`
- Experiment: `chat_agent_evaluation`
- Circuit: `a06`
- Max executable scenarios: `5`
- Created at: `2026-07-23T13:03:11`
- Updated at: `2026-07-23T13:09:24`

## Scenario 1 - Ridurre l’ampiezza della sorgente di ingresso

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a06\scenarios\scenario_1`

### Hypothesis

The output distortion may be caused by overdriving the transistor stage with the present input amplitude.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "Vsignal_source23_1",
    "value": "SIN(0 100m 100)"
  }
]
```

## Scenario 2 - Rafforzare il bias di base riducendo Rresistor22_2

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

The transistor may be biased too close to cutoff because the base bias from VCC is too weak.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_2",
    "value": "47k"
  }
]
```

## Scenario 3 - Ridurre la degenerazione di emettitore variando Rresistor22_5

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

The emitter network may be setting an unfavorable operating point that contributes to output distortion.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_5",
    "value": "1k"
  }
]
```

## Scenario 4 - Ridurre ancora l’ampiezza d’ingresso per cercare una THD più bassa

- Scenario id: `scenario_4`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a06\scenarios\scenario_4`

### Hypothesis

Since scenario_1 reduced distortion without suppressing output transfer, a further reduction of Vsignal_source23_1 to 50 mV may lower THD at N005 while preserving useful gain from N006 to N005.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "Vsignal_source23_1",
    "value": "SIN(0 50m 100)"
  }
]
```

## Scenario 5 - Ridurre l’ingresso a 20 mV mantenendo il controllo di guadagno

- Scenario id: `scenario_5`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_3`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a06\scenarios\scenario_5`

### Hypothesis

Since scenario_4 kept useful gain from N006 to N005 at 50 mV but the user reports THD on N005 is still 22.4%, reducing Vsignal_source23_1 to 20 mV may further lower distortion at N005 while preserving useful transfer.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "Vsignal_source23_1",
    "value": "SIN(0 20m 100)"
  }
]
```
