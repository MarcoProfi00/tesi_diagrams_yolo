# Pipeline 2.0 scenario registry

- Batch: `batchA`
- Experiment: `experiment4`
- Circuit: `a05`
- Max executable scenarios: `5`
- Created at: `2026-07-16T13:14:23`
- Updated at: `2026-07-16T13:14:34`

## Scenario 1 - Alimentare il nodo VMON_INPUT dal connettore

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `resolved_candidate`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment4\chat\a05\scenarios\scenario_1`

### Hypothesis

VMON reads 0 V because node N003 (VMON_INPUT) is not driven by any source in the base netlist.

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

The open switch switch25.1 may block a required operating condition or reference path.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```

## Scenario 3 - Pilotare direttamente il nodo misurato da VMON

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

The measured node N001 may simply be unpowered; directly driving it isolates the measurement point from upstream uncertainty.

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
