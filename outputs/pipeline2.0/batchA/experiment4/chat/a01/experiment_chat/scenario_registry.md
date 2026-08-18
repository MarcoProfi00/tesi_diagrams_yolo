# Pipeline 2.0 scenario registry

- Batch: `batchA`
- Experiment: `experiment4`
- Circuit: `a01`
- Max executable scenarios: `5`
- Created at: `2026-07-15T16:15:44`
- Updated at: `2026-07-15T16:17:32`

## Scenario 1 - Alimentare il ramo della lampada dal suo ingresso naturale

- Scenario id: `scenario_1`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `None`

### Hypothesis

The lamp branch is inactive because node N002 is not driven.

### Actions

```json
[
  {
    "type": "add_voltage_source_between_nodes",
    "positive": "N002",
    "negative": "0",
    "value": "5V"
  }
]
```

## Scenario 2 - Chiudere lo switch riconosciuto

- Scenario id: `scenario_2`
- Status: `executed`
- Outcome: `not_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `outputs\pipeline2.0\batchA\experiment4\chat\a01\scenarios\scenario_2`

### Hypothesis

The open switch may be preventing the intended circuit condition.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```

## Scenario 3 - Collegare il nodo alimentato al ramo lampada

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

The lamp branch may be inactive because N001 does not reach N002.

### Actions

```json
[
  {
    "type": "connect_nodes",
    "from": "N001",
    "to": "N002",
    "resistance": "1m"
  }
]
```

## Scenario 4 - Propagare il +5V esistente anche al ramo lampada

- Scenario id: `scenario_4`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment4\chat\a01\scenarios\scenario_4`

### Hypothesis

The lamp branch is off because N002 is not powered, while N001 is already powered. Feeding N002 from N001 should energize lamp and keep LED powered in the same run.

### Actions

```json
[
  {
    "type": "feed_nodes_from_source_node",
    "source_node": "N001",
    "target_nodes": [
      "N002"
    ],
    "resistance": "1m"
  }
]
```
