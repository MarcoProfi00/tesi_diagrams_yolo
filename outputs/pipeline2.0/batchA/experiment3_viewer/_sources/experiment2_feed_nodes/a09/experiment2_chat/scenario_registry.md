# Experiment 2 scenario registry

- Batch: `batchA`
- Experiment: `experiment2_feed_nodes`
- Circuit: `a09`
- Max executable scenarios: `5`
- Created at: `2026-07-07T17:30:13`
- Updated at: `2026-07-07T17:45:14`

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

La lampada non si accende perché switch25.1 è aperto e interrompe il ramo verso N006.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```

## Scenario 2 - Alimentare l'ingresso del ramo LED

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

Il LED non si accende perché N005 non è pilotato nel circuito base.

### Actions

```json
[
  {
    "type": "drive_node_voltage",
    "target": "N005",
    "value": "9V"
  }
]
```

## Scenario 3 - Alimentare l'ingresso dello switch della lampada

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

La lampada non si accende perché il nodo N004 non riceve alimentazione nel circuito base.

### Actions

```json
[
  {
    "type": "drive_node_voltage",
    "target": "N004",
    "value": "9V"
  }
]
```

## Scenario 4 - Propagare N003 verso l’ingresso del ramo LED

- Scenario id: `scenario_4`
- Status: `executed`
- Outcome: `resolved_candidate`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment2_feed_nodes\a09\scenarios\scenario_4`

### Hypothesis

Il ramo LED e inattivo perche il nodo alimentato N003 non raggiunge il nodo di ingresso PWR_LED_INPUT N005.

### Actions

```json
[
  {
    "type": "feed_nodes_from_source_node",
    "source_node": "N003",
    "target_nodes": [
      "N005"
    ],
    "resistance": "1m"
  }
]
```

## Scenario 5 - Propagare N003 verso l’ingresso del ramo lampada

- Scenario id: `scenario_5`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_3`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment2_feed_nodes\a09\scenarios\scenario_5`

### Hypothesis

Il ramo lampada e inattivo perche il nodo alimentato N003 non raggiunge il nodo di ingresso SW2_INPUT N004.

### Actions

```json
[
  {
    "type": "feed_nodes_from_source_node",
    "source_node": "N003",
    "target_nodes": [
      "N004"
    ],
    "resistance": "1m"
  }
]
```

## Scenario 6 - Alimentare N004 e chiudere switch25.1

- Scenario id: `scenario_6`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_4`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment2_feed_nodes\a09\scenarios\scenario_6`

### Hypothesis

Il ramo lampada resta inattivo nonostante N004 sia alimentato perche switch25.1 e aperto e impedisce il passaggio da N004 a N006.

### Actions

```json
[
  {
    "type": "feed_nodes_from_source_node",
    "source_node": "N003",
    "target_nodes": [
      "N004"
    ],
    "resistance": "1m"
  },
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```

## Scenario 7 - Alimentare insieme i rami LED e lampada

- Scenario id: `scenario_7`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_5`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment2_feed_nodes\a09\scenarios\scenario_7`

### Hypothesis

Entrambi i rami diventano attivi se il nodo alimentato N003 viene propagato sia a N005 sia a N004, e se switch25.1 viene chiuso per completare il percorso verso N006.

### Actions

```json
[
  {
    "type": "feed_nodes_from_source_node",
    "source_node": "N003",
    "target_nodes": [
      "N005"
    ],
    "resistance": "1m"
  },
  {
    "type": "feed_nodes_from_source_node",
    "source_node": "N003",
    "target_nodes": [
      "N004"
    ],
    "resistance": "1m"
  },
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```
