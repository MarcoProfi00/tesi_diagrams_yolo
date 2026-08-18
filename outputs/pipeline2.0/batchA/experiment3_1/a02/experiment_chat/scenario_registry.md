# Pipeline 2.0 scenario registry

- Batch: `batchA`
- Experiment: `experiment3_1`
- Circuit: `a02`
- Max executable scenarios: `5`
- Created at: `2026-07-14T11:53:30`
- Updated at: `2026-07-14T11:55:23`

## Scenario 1 - Chiudere lo switch riconosciuto

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `not_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment3_1\a02\scenarios\scenario_1`

### Hypothesis

The open switch25.1 may be preventing a useful reference or current path around N001.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```

## Scenario 2 - Collegare il nodo VCC al ramo del resistore

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

The battery current is zero because the powered node N002 does not electrically reach the branch at N004.

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

## Scenario 3 - Alimentare il circuito dal connettore VCC-GND

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

The extracted circuit may need a realistic external excitation on its natural interface nodes N002 and 0.

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

## Scenario 4 - Collegare il positivo della batteria al ramo su N004

- Scenario id: `scenario_4`
- Status: `executed`
- Outcome: `resolved_candidate`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment3_1\a02\scenarios\scenario_4`

### Hypothesis

The branch at N004 stays inactive because the extracted circuit lacks electrical continuity between battery positive N002 and node N004.

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
