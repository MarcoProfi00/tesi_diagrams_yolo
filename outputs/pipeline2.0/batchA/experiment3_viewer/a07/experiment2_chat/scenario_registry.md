# Experiment 2 scenario registry

- Batch: `batchA`
- Experiment: `experiment2`
- Circuit: `a07`
- Max executable scenarios: `5`
- Created at: `2026-07-08T16:21:56`
- Updated at: `2026-07-08T16:23:23`

## Scenario 1 - Alimentare il ramo PWR dal connettore

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `resolved_candidate`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment2\a07\scenarios\scenario_1`

### Hypothesis

Il LED PWR e inattivo perche il nodo N002 non e alimentato nel run base.

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

## Scenario 2 - Alimentare il nodo misurato dal VAC

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

Il voltmetro VAC non legge nulla perche N001 non riceve alcuna eccitazione nel run base.

### Actions

```json
[
  {
    "type": "add_voltage_source_between_nodes",
    "positive": "N001",
    "negative": "0",
    "value": "5V"
  }
]
```

## Scenario 3 - Chiudere il ramo RESET

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

Lo switch RESET aperto potrebbe influire sulla condizione del nodo N003, ma potrebbe non essere la causa principale dell'inattivita generale.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```

## Scenario 4 - Alimentare l’ingresso misurato da VAC

- Scenario id: `scenario_4`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment2\a07\scenarios\scenario_4`

### Hypothesis

Il voltmetro VAC non mostra nulla nel caso base perche il nodo N001, etichettato AC_INPUT, non e pilotato da alcuna sorgente nel netlist base.

### Actions

```json
[
  {
    "type": "add_voltage_source_between_nodes",
    "positive": "N001",
    "negative": "0",
    "value": "5V"
  }
]
```
