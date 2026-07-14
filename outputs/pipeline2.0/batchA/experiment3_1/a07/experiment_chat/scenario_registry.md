# Pipeline 2.0 scenario registry

- Batch: `batchA`
- Experiment: `experiment3_1`
- Circuit: `a07`
- Max executable scenarios: `5`
- Created at: `2026-07-14T12:42:38`
- Updated at: `2026-07-14T12:45:24`

## Scenario 1 - Alimentare il nodo PWR dal connettore

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment3_1\a07\scenarios\scenario_1`

### Hypothesis

Il ramo del LED PWR e inattivo perche N002 non e alimentato nel netlist base.

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

## Scenario 2 - Applicare una tensione di prova al nodo AC_INPUT

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

Il voltmetro VAC legge zero perche N001 non e eccitato nel netlist base.

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

## Scenario 3 - Chiudere lo switch RESET

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

Lo switch RESET aperto potrebbe impedire una condizione necessaria del circuito reale.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```

## Scenario 4 - Alimentare l’ingresso del voltmetro VAC

- Scenario id: `scenario_4`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment3_1\a07\scenarios\scenario_4`

### Hypothesis

Il voltmetro VAC non mostra nulla nel caso base perché il nodo N001, che rappresenta AC_INPUT ed è il nodo misurato da analog_meter0.1, non è pilotato nel netlist base.

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

## Scenario 5 - Alimentare insieme PWR e ingresso VAC

- Scenario id: `scenario_5`
- Status: `executed`
- Outcome: `resolved_candidate`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_3`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment3_1\a07\scenarios\scenario_5`

### Hypothesis

Nel netlist base i rami VAC e PWR sono separati; per ottenere simultaneamente misura su VAC e attivazione del LED occorre alimentare sia N001 sia N002 nella stessa run.

### Actions

```json
[
  {
    "type": "add_voltage_source_between_nodes",
    "positive": "N001",
    "negative": "0",
    "value": "5V"
  },
  {
    "type": "add_voltage_source_between_nodes",
    "positive": "N002",
    "negative": "0",
    "value": "5V"
  }
]
```
