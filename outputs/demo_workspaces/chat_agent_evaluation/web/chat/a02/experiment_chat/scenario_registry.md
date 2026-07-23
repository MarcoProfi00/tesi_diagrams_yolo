# Pipeline 2.0 scenario registry

- Batch: `batchChatAgentEvaluation`
- Experiment: `chat_agent_evaluation`
- Circuit: `a02`
- Max executable scenarios: `5`
- Created at: `2026-07-23T11:12:23`
- Updated at: `2026-07-23T11:13:56`

## Scenario 1 - Chiudere lo switch di ritorno switch25.1

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `not_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a02\scenarios\scenario_1`

### Hypothesis

The open switch switch25.1 is preventing a DC reference or return path for N001, contributing to zero battery current.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```

## Scenario 2 - Alimentare il ramo su connector5.1_pin2

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

The extracted circuit may be inactive because node N004 is an unpowered interface node; energizing it against ground should reveal whether the resistor branch can conduct.

### Actions

```json
[
  {
    "type": "add_voltage_source_between_nodes",
    "positive": "N004",
    "negative": "0",
    "value": "5V"
  }
]
```

## Scenario 3 - Collegare il positivo N002 al ramo resistivo N004

- Scenario id: `scenario_3`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a02\scenarios\scenario_3`

### Hypothesis

Battery current is zero because the positive node N002 does not reach the resistor branch at N004.

### Actions

```json
[
  {
    "type": "connect_nodes",
    "from": "N002",
    "to": "N004",
    "resistance": "1m"
  }
]
```
