# Pipeline 2.0 scenario registry

- Batch: `batchA`
- Experiment: `experiment4`
- Circuit: `a02`
- Max executable scenarios: `5`
- Created at: `2026-07-16T09:37:00`
- Updated at: `2026-07-16T09:41:05`

## Scenario 1 - Chiudere lo switch SENSE

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `not_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment4\chat\a02\scenarios\scenario_1`

### Hypothesis

The open switch25.1 may be preventing a useful return/reference path for battery current.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```

## Scenario 2 - Alimentare il ramo del resistore dal nodo VCC

- Scenario id: `scenario_2`
- Status: `executed`
- Outcome: `resolved_candidate`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `outputs\pipeline2.0\batchA\experiment4\chat\a02\scenarios\scenario_2`

### Hypothesis

The battery positive node N002 may not be electrically reaching the branch ending at N004.

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

## Scenario 3 - Applicare una sorgente esterna sull’interfaccia del connettore

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

The extracted circuit may need an external excitation on the connector interface to become active.

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
