# Pipeline 2.0 scenario registry

- Batch: `batchDemo`
- Experiment: `demo_batch`
- Circuit: `b02`
- Max executable scenarios: `5`
- Created at: `2026-07-22T09:24:15`
- Updated at: `2026-07-22T09:25:44`

## Scenario 1 - Rompere la simmetria iniziale dei due nodi di base

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `resolved_candidate`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\demo_batch\web\chat\b02\scenarios\scenario_1`

### Hypothesis

The transient may be stuck in a symmetric non-oscillating state because N004 and N006 start from identical conditions.

### Actions

```json
[
  {
    "type": "set_initial_node_voltage",
    "target": "N004",
    "value": "0V",
    "skip_operating_point": true
  },
  {
    "type": "set_initial_node_voltage",
    "target": "N006",
    "value": "1V",
    "skip_operating_point": true
  }
]
```

## Scenario 2 - Introdurre una lieve asimmetria su Rresistor22_2

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

A small bias asymmetry on one base resistor may break the symmetric operating state and allow oscillation to start.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_2",
    "value": "2k"
  }
]
```

## Scenario 3 - Introdurre una lieve asimmetria su Cpolarized_capacitor20_1

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

A small timing asymmetry on one capacitor may break the symmetric transient behavior and allow alternating LED blinking.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Cpolarized_capacitor20_1",
    "value": "33u"
  }
]
```
