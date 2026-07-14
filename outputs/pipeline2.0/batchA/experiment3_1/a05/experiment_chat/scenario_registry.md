# Pipeline 2.0 scenario registry

- Batch: `batchA`
- Experiment: `experiment3_1`
- Circuit: `a05`
- Max executable scenarios: `5`
- Created at: `2026-07-14T12:31:58`
- Updated at: `2026-07-14T12:32:40`

## Scenario 1 - Alimentare l’ingresso VMON_INPUT dal connettore

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `resolved_candidate`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment3_1\a05\scenarios\scenario_1`

### Hypothesis

VMON reads 0 V because node N003 is not externally driven in the base netlist.

### Actions

```json
[
  {
    "type": "add_voltage_source_between_nodes",
    "positive": "N003",
    "negative": "0",
    "value": "5V"
  }
]
```

## Scenario 2 - Chiudere lo switch TEST riconosciuto

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

The open switch state may be keeping the extracted circuit in an inactive test condition.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```

## Scenario 3 - Pilotare direttamente il nodo letto da VMON

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

The measurement node itself is valid, but it remains at 0 V only because no upstream excitation reaches it.

### Actions

```json
[
  {
    "type": "drive_node_voltage",
    "target": "N001",
    "value": "5V"
  }
]
```

## Scenario 4 - Nessun nuovo scenario necessario

- Scenario id: `scenario_4`
- Status: `proposed`
- Outcome: `None`
- Executable: `False`
- Kind: `non_executable_proposal`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `None`

### Hypothesis

The main symptom is already explained by the lack of external drive on N003 (VMON_INPUT) in the base run.
