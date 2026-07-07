# Experiment 2 scenario registry

- Batch: `batchA`
- Experiment: `experiment2`
- Circuit: `a02`
- Max executable scenarios: `5`
- Created at: `2026-07-07T11:11:28`
- Updated at: `2026-07-07T11:15:09`

## Scenario 1 - Chiudere lo switch riconosciuto

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `not_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment2\a02\scenarios\scenario_1`

### Hypothesis

The open switch switch25.1 may be preventing the DC return path needed for battery current.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```

## Scenario 2 - Alimentare direttamente il nodo del ramo resistivo

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

The circuit may be inactive because node N004 is not being driven in the emitted netlist.

### Actions

```json
[
  {
    "type": "drive_node_voltage",
    "target": "N004",
    "value": "5V"
  }
]
```

## Scenario 3 - Collegare il nodo alimentato al ramo su N004

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

The inactive branch may be caused by missing continuity between the battery positive node N002 and the resistor branch node N004.

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

## Scenario 4 - Collegare il positivo della batteria al ramo su N004

- Scenario id: `scenario_4`
- Status: `executed`
- Outcome: `resolved_candidate`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment2\a02\scenarios\scenario_4`

### Hypothesis

The branch on N004 may be inactive because there is no electrical continuity between the battery positive node N002 and the branch node N004.

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
