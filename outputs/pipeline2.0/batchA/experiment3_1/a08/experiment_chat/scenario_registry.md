# Pipeline 2.0 scenario registry

- Batch: `batchA`
- Experiment: `experiment3_1`
- Circuit: `a08`
- Max executable scenarios: `5`
- Created at: `2026-07-14T12:50:03`
- Updated at: `2026-07-14T12:53:37`

## Scenario 1 - Ridurre la resistenza di pilotaggio della base

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment3_1\a08\scenarios\scenario_1`

### Hypothesis

Rresistor22_4 may be too large, so N004 does not drive Qnpn_transistor18_1 strongly enough to create a clear LED switching behavior.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_4",
    "value": "33k"
  }
]
```

## Scenario 2 - Aumentare l'ampiezza della sorgente di ingresso

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

The assumed 0-5 V pulse on Vsignal_source23_1 may be insufficient for the extracted circuit to produce the expected LED blinking behavior.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "Vsignal_source23_1",
    "value": "PULSE(0 10 0 1ms 1ms 50ms 100ms)"
  }
]
```

## Scenario 3 - Forzare il nodo del collettore del LED per test di isolamento

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

The LED may fail to blink because N003 is not being driven to a useful level by the transistor branch.

### Actions

```json
[
  {
    "type": "drive_node_voltage",
    "target": "N003",
    "value": "0V"
  }
]
```

## Scenario 4 - Rafforzare l'accoppiamento resistivo tra TRIGGER e base

- Scenario id: `scenario_4`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment3_1\a08\scenarios\scenario_4`

### Hypothesis

The existing resistive coupling from N001 to N004 may be too weak; adding a parallel resistive branch between the trigger node and the transistor base should increase the base drive if weak coupling is the limiting factor.

### Actions

```json
[
  {
    "type": "add_resistor_between_nodes",
    "from": "N001",
    "to": "N004",
    "value": "33k"
  }
]
```
