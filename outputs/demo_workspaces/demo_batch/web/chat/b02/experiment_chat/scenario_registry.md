# Pipeline 2.0 scenario registry

- Batch: `batchDemo`
- Experiment: `demo_batch`
- Circuit: `b02`
- Max executable scenarios: `5`
- Created at: `2026-07-21T18:14:31`
- Updated at: `2026-07-21T18:17:11`

## Scenario 1 - Rompere la simmetria iniziale dei due nodi di base

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\demo_batch\web\chat\b02\scenarios\scenario_1`

### Hypothesis

The astable may stay locked because the transient starts from a perfectly symmetric initial condition at N004 and N006.

### Actions

```json
[
  {
    "type": "set_initial_node_voltage",
    "target": "N004",
    "value": "0.6V",
    "skip_operating_point": true
  },
  {
    "type": "set_initial_node_voltage",
    "target": "N006",
    "value": "0.8V",
    "skip_operating_point": true
  }
]
```

## Scenario 2 - Alleggerire una sola resistenza di base per rompere il bilanciamento

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

The symmetric 2.2k base-bias network may be holding both transistor sides in the same state.

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

## Scenario 3 - Ridurre un solo condensatore d’accoppiamento per testare la rete temporale

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

The RC cross-coupling may not be producing a transition in the emitted netlist, keeping both LED branches steady.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Cpolarized_capacitor20_1",
    "value": "10u"
  }
]
```

## Scenario 4 - Ridurre leggermente una resistenza di bias per rompere la simmetria strutturale

- Scenario id: `scenario_4`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `3`
- Execution path: `outputs\demo_workspaces\demo_batch\web\chat\b02\scenarios\scenario_4`

### Hypothesis

The base run may stay locked because the two bias branches are too perfectly symmetric; a small bias mismatch on Rresistor22_2 may break the lock.

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
