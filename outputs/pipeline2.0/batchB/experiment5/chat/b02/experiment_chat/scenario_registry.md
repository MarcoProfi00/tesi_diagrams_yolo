# Pipeline 2.0 scenario registry

- Batch: `batchB`
- Experiment: `experiment5`
- Circuit: `b02`
- Max executable scenarios: `5`
- Created at: `2026-07-17T11:06:00`
- Updated at: `2026-07-17T11:07:25`

## Scenario 1 - Rompere la simmetria iniziale su una base

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchB\experiment5\chat\b02\scenarios\scenario_1`

### Hypothesis

The symmetric operating point may prevent startup; a small initial imbalance on N004 may trigger oscillation.

### Actions

```json
[
  {
    "type": "set_initial_node_voltage",
    "target": "N004",
    "value": "0.5V"
  }
]
```

## Scenario 2 - Rompere la simmetria iniziale su un collettore

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

The symmetric startup state may persist because the collector nodes start identically; an initial imbalance on N005 may trigger alternation.

### Actions

```json
[
  {
    "type": "set_initial_node_voltage",
    "target": "N005",
    "value": "0.2V"
  }
]
```

## Scenario 3 - Variare una resistenza di bias del ramo sinistro

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

The symmetric bias network may hold the circuit in a non-oscillating state; changing Rresistor22_2 may reveal whether bias strength is the cause.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_2",
    "value": "1k"
  }
]
```
