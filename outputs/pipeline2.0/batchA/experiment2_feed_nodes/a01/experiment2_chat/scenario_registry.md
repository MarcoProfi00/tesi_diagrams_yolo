# Experiment 2 scenario registry

- Batch: `batchA`
- Experiment: `experiment2_feed_nodes`
- Circuit: `a01`
- Max executable scenarios: `5`
- Created at: `2026-07-07T17:07:00`
- Updated at: `2026-07-07T17:11:57`

## Scenario 1 - Alimentare l'ingresso del ramo lampada

- Scenario id: `scenario_1`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `None`

### Hypothesis

La lampada non si accende perché N002 non è pilotato.

### Actions

```json
[
  {
    "type": "drive_node_voltage",
    "target": "N002",
    "value": "5V"
  }
]
```

## Scenario 2 - Portare il +5 V esistente al ramo lampada

- Scenario id: `scenario_2`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `outputs\pipeline2.0\batchA\experiment2_feed_nodes\a01\scenarios\scenario_2`

### Hypothesis

La lampada resta spenta perché il nodo alimentato N001 non raggiunge N002.

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

## Scenario 3 - Chiudere lo switch riconosciuto

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

Lo stato aperto di switch25.1 potrebbe impedire una condizione necessaria al funzionamento della lampada.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```

## Scenario 4 - Verificare la continuità diretta tra N001 e N002

- Scenario id: `scenario_4`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `None`

### Hypothesis

Il ramo lampada resta spento perché nel circuito base manca una continuità elettrica utile tra N001 e N002, indipendentemente dallo stato dello switch riconosciuto.

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
