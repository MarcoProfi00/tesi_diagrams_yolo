# Experiment 2 scenario registry

- Batch: `batchA`
- Experiment: `experiment2`
- Circuit: `a01`
- Max executable scenarios: `5`
- Created at: `2026-07-06T15:48:50`
- Updated at: `2026-07-07T11:42:23`

## Scenario 1 - Chiudere lo switch riconosciuto

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `not_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment2\a01\scenarios\scenario_1`

### Hypothesis

The open switch may be preventing the branch that should feed the lamp from becoming active.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```

## Scenario 2 - Verificare la continuità verso il ramo della lampada

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

The lamp may stay off because the powered path does not actually reach the lamp branch.

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

## Scenario 3 - Aumentare la sorgente principale

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

If the lamp branch is correctly connected, it should respond to a stronger VCC.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "VVCC",
    "value": "10V"
  }
]
```

## Scenario 4 - Collegare il nodo alimentato al ramo della lampada

- Scenario id: `scenario_4`
- Status: `executed`
- Outcome: `resolved_candidate`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment2\a01\scenarios\scenario_4`

### Hypothesis

The powered node N001 may not be continuously linked to the lamp branch; a controlled continuity test can verify whether the supply can reach N004 through the recognized path.

### Actions

```json
[
  {
    "type": "connect_nodes",
    "from": "N001",
    "to": "N002",
    "resistance": "1m"
  }
]
```
