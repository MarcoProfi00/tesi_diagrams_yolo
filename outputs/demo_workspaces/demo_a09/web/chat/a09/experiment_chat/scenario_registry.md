# Pipeline 2.0 scenario registry

- Batch: `batchDemo`
- Experiment: `demo_a09`
- Circuit: `a09`
- Max executable scenarios: `5`
- Created at: `2026-07-22T12:09:33`
- Updated at: `2026-07-22T12:11:01`

## Scenario 1 - Chiudere lo switch della lampada

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `not_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\demo_a09\web\chat\a09\scenarios\scenario_1`

### Hypothesis

The lamp branch is inactive because switch25.1 is open and blocks the path to N006.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```

## Scenario 2 - Alimentare il ramo LED dal nodo batteria protetto

- Scenario id: `scenario_2`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `outputs\demo_workspaces\demo_a09\web\chat\a09\scenarios\scenario_2`

### Hypothesis

The LED branch is inactive because N005 is not receiving supply from the powered node N003.

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

## Scenario 3 - Alimentare l'ingresso della lampada dal nodo batteria protetto

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

The lamp input node N004 may be unpowered because it is not connected to the available powered node N003.

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

## Scenario 4 - Alimentare insieme il ramo LED e il ramo lampada dal nodo batteria protetto

- Scenario id: `scenario_4`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\demo_a09\web\chat\a09\scenarios\scenario_4`

### Hypothesis

Both loads stay inactive together because the powered node N003 is not propagated to the LED input N005 and to the lamp path input N004; with switch25.1 closed, feeding both branches from N003 should activate LED and lamp simultaneously.

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
