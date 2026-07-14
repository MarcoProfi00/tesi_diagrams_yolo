# Pipeline 2.0 scenario registry

- Batch: `batchA`
- Experiment: `experiment3_1`
- Circuit: `a10`
- Max executable scenarios: `5`
- Created at: `2026-07-14T13:03:36`
- Updated at: `2026-07-14T13:04:40`

## Scenario 1 - Chiudere lo switch riconosciuto

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `not_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment3_1\a10\scenarios\scenario_1`

### Hypothesis

The open switch may be preventing the battery voltage from reaching the downstream connector side.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```

## Scenario 2 - Collegare il nodo a valle dello switch al ramo della lampada

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

The lamp branch may be inactive because N004 is not electrically continuous with the switched supply node N002.

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

## Scenario 3 - Collegare il nodo a valle dello switch al ramo del LED

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

The LED branch may be inactive because N003 is not electrically continuous with the switched supply node N002.

### Actions

```json
[
  {
    "type": "connect_nodes",
    "from": "N002",
    "to": "N003",
    "resistance": "1m"
  }
]
```

## Scenario 4 - Propagare l’alimentazione commutata ai rami lampada e LED

- Scenario id: `scenario_4`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment3_1\a10\scenarios\scenario_4`

### Hypothesis

After closing switch25.1, the battery voltage reaches N002 but does not propagate to the branch input nodes N003 and N004; feeding both from N002 should energize the LED and lamp branches together.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  },
  {
    "type": "feed_nodes_from_source_node",
    "source_node": "N002",
    "target_nodes": [
      "N003",
      "N004"
    ],
    "resistance": "1m"
  }
]
```
