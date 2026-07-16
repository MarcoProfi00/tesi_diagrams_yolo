# Pipeline 2.0 scenario registry

- Batch: `batchA`
- Experiment: `experiment4`
- Circuit: `a07`
- Max executable scenarios: `5`
- Created at: `2026-07-16T16:36:17`
- Updated at: `2026-07-16T16:39:00`

## Scenario 1 - Alimentare il ramo PWR dal connettore

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `resolved_candidate`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment4\chat\a07\scenarios\scenario_1`

### Hypothesis

The LED branch is inactive because node N002, labeled PWR, is not driven in the base netlist.

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

## Scenario 2 - Alimentare l’ingresso misurato dal VAC

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

The VAC meter reads zero because node N001 is not excited in the base netlist.

### Actions

```json
[
  {
    "type": "add_voltage_source_between_nodes",
    "positive": "N001",
    "negative": "0",
    "value": "5V"
  }
]
```

## Scenario 3 - Chiudere lo switch RESET

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

The recognized open switch may be preventing a required operating condition.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```

## Scenario 4 - Propagare PWR verso il punto di misura VAC

- Scenario id: `scenario_4`
- Status: `executed`
- Outcome: `resolved_candidate`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment4\chat\a07\scenarios\scenario_4`

### Hypothesis

VAC remains inactive because N001 is not electrically reached by the supply that already activates N002; powering N002 and adding continuity from N002 to N001 should activate the measured node if that path is the missing condition.

### Actions

```json
[
  {
    "type": "add_voltage_source_between_nodes",
    "positive": "N002",
    "negative": "0",
    "value": "5V"
  },
  {
    "type": "connect_nodes",
    "from": "N002",
    "to": "N001",
    "resistance": "1m"
  }
]
```
