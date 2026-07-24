# Pipeline 2.0 scenario registry

- Batch: `batchChatAgentEvaluation`
- Experiment: `chat_agent_evaluation`
- Circuit: `b02`
- Max executable scenarios: `5`
- Created at: `2026-07-24T11:04:49`
- Updated at: `2026-07-24T11:05:54`

## Scenario 1 - Rompere la simmetria iniziale dei due nodi base

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `resolved_candidate`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b02\scenarios\scenario_1`

### Hypothesis

The circuit may be stuck in a symmetric startup state, so a small asymmetry on N004 and N006 could trigger oscillation.

### Actions

```json
[
  {
    "type": "set_initial_node_voltage",
    "target": "N004",
    "value": "0.6V",
    "skip_operating_point": true
  },
  {
    "type": "set_initial_node_voltage",
    "target": "N006",
    "value": "1.0V",
    "skip_operating_point": true
  }
]
```

## Scenario 2 - Ridurre la resistenza di base del ramo Q1

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

The present base bias through Rresistor22_2 may help keep the circuit in a symmetric steady-on state; changing that bias may alter startup or oscillation behavior.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_2",
    "value": "1k"
  }
]
```

## Scenario 3 - Ridurre la resistenza di base del ramo Q2

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

The present base bias through Rresistor22_3 may help keep the circuit in a symmetric steady-on state; changing the opposite branch bias tests that hypothesis independently.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_3",
    "value": "1k"
  }
]
```
