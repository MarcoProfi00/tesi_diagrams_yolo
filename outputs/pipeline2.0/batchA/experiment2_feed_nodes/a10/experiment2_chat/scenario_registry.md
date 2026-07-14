# Experiment 2 scenario registry

- Batch: `batchA`
- Experiment: `experiment2_feed_nodes`
- Circuit: `a10`
- Max executable scenarios: `5`
- Created at: `2026-07-08T09:25:28`
- Updated at: `2026-07-08T09:32:06`

## Scenario 1 - Chiudere lo switch riconosciuto

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `not_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment2_feed_nodes\a10\scenarios\scenario_1`

### Hypothesis

Il circuito non alimenta i carichi perche switch25.1 isola la batteria dal resto del circuito.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```

## Scenario 2 - Alimentare il ramo del LED dal nodo dopo lo switch

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

Il LED non si accende perche il nodo SW_VCC non raggiunge il ramo N003-Rresistor22_1-N005.

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

## Scenario 3 - Alimentare il ramo della lampada dal nodo dopo lo switch

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

La lampada non si accende perche il nodo SW_VCC non raggiunge il ramo della lampada su N004.

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

## Scenario 4 - Propagare N002 verso il ramo lampada

- Scenario id: `scenario_4`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment2_feed_nodes\a10\scenarios\scenario_4`

### Hypothesis

Dopo la chiusura di switch25.1, il ramo lampada resta spento perche il nodo alimentato N002 non raggiunge l'ingresso N004 della lampada.

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
      "N004"
    ],
    "resistance": "1m"
  }
]
```

## Scenario 5 - Propagare N002 verso il ramo LED

- Scenario id: `scenario_5`
- Status: `executed`
- Outcome: `resolved_candidate`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_3`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment2_feed_nodes\a10\scenarios\scenario_5`

### Hypothesis

Il ramo LED resta inattivo perche il nodo alimentato N002 non raggiunge l'ingresso N003 del ramo formato da Rresistor22_1 e Dled12_1.

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
      "N003"
    ],
    "resistance": "1m"
  }
]
```
