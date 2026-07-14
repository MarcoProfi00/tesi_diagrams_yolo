# Pipeline 2.0 scenario registry

- Batch: `batchA`
- Experiment: `experiment3_1`
- Circuit: `a01`
- Max executable scenarios: `5`
- Created at: `2026-07-14T11:40:20`
- Updated at: `2026-07-14T11:41:04`

## Scenario 1 - Alimentare direttamente l'ingresso della lampada

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `resolved_candidate`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment3_1\a01\scenarios\scenario_1`

### Hypothesis

The lamp branch is inactive because node N002 is not driven in the base run.

### Actions

```json
[
  {
    "type": "add_voltage_source_between_nodes",
    "positive": "N002",
    "negative": "0",
    "value": "5V"
  }
]
```

## Scenario 2 - Chiudere lo switch riconosciuto

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

The open switch may represent a missing circuit state relevant to the observed symptom.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```

## Scenario 3 - Propagare l'alimentazione esistente verso l'ingresso della lampada

- Scenario id: `scenario_3`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `outputs\pipeline2.0\batchA\experiment3_1\a01\scenarios\scenario_3`

### Hypothesis

The lamp branch may be inactive because powered node N001 does not reach N002.

### Actions

```json
[
  {
    "type": "feed_nodes_from_source_node",
    "source_node": "N001",
    "target_nodes": [
      "N002"
    ],
    "resistance": "1m"
  }
]
```
