# Pipeline 2.0 scenario registry

- Batch: `batchDemo`
- Experiment: `demo_a09_all`
- Circuit: `a09`
- Max executable scenarios: `5`
- Created at: `2026-07-22T11:19:33`
- Updated at: `2026-07-22T11:22:55`

## Scenario 1 - Chiudere lo switch della lampada

- Scenario id: `scenario_1`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `None`

### Hypothesis

The lamp branch is inactive because switch25.1 is open and prevents supply from reaching N006.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```

## Scenario 2 - Alimentare il ramo LED dal nodo BAT_FUSED

- Scenario id: `scenario_2`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `outputs\demo_workspaces\demo_a09_all\web\chat\a09\scenarios\scenario_2`

### Hypothesis

The LED branch is inactive because the powered node N003 does not reach the branch input N005.

### Actions

```json
[
  {
    "type": "connect_nodes",
    "from": "N003",
    "to": "N005",
    "resistance": "1m"
  }
]
```

## Scenario 3 - Alimentare l'ingresso della lampada dal nodo BAT_FUSED

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

The lamp branch input N004 may be inactive because the powered node N003 is not electrically continuous with it.

### Actions

```json
[
  {
    "type": "connect_nodes",
    "from": "N003",
    "to": "N004",
    "resistance": "1m"
  }
]
```

## Scenario 4 - Alimentare insieme i due rami e chiudere SW2

- Scenario id: `scenario_4`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\demo_a09_all\web\chat\a09\scenarios\scenario_4`

### Hypothesis

The full symptom is resolved if BAT_FUSED powers both branch inputs, keeping the LED branch fed through N005 and feeding the lamp branch through N004 while closing switch25.1 so current can flow in both Rresistor22_1 and Rlamp13_1 in the same simulation.

### Actions

```json
[
  {
    "type": "connect_nodes",
    "from": "N003",
    "to": "N005",
    "resistance": "1m"
  },
  {
    "type": "connect_nodes",
    "from": "N003",
    "to": "N004",
    "resistance": "1m"
  },
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```
