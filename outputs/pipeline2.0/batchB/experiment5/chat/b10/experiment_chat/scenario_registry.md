# Pipeline 2.0 scenario registry

- Batch: `batchB`
- Experiment: `experiment5`
- Circuit: `b10`
- Max executable scenarios: `5`
- Created at: `2026-07-17T12:35:26`
- Updated at: `2026-07-17T12:35:46`

## Scenario 1 - Chiudere lo switch riconosciuto

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchB\experiment5\chat\b10\scenarios\scenario_1`

### Hypothesis

The open switch25.1 may be preventing the branch around N004 and N005 from affecting node N002.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```

## Scenario 2 - Ridurre la resistenza tra A e B

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

Node N002 may stay near zero mainly because Rresistor22_2 is too large to transfer the 1 V from N001.

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

## Scenario 3 - Azzerare l'offset della sorgente tra N005 e N002

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

The small DC source Vvoltage_source31_1 may be contributing to the near-zero level seen around node B.

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
