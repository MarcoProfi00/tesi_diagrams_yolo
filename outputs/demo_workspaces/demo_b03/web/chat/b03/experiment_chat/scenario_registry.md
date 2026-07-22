# Pipeline 2.0 scenario registry

- Batch: `batchDemo`
- Experiment: `demo_b03`
- Circuit: `b03`
- Max executable scenarios: `5`
- Created at: `2026-07-22T11:40:43`
- Updated at: `2026-07-22T11:50:41`

## Scenario 1 - Simulare batteria scarica

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\demo_b03\web\chat\b03\scenarios\scenario_1`

### Hypothesis

Abbassando la sorgente Vbattery2_1 il monitor dovrebbe modificare lo stato dei LED se il circuito riconosce la condizione di batteria scarica.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "Vbattery2_1",
    "value": "10V"
  }
]
```

## Scenario 2 - Simulare batteria molto carica

- Scenario id: `scenario_2`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `outputs\demo_workspaces\demo_b03\web\chat\b03\scenarios\scenario_2`

### Hypothesis

Alzando la sorgente Vbattery2_1 il monitor dovrebbe modificare lo stato dei LED se il circuito riconosce la condizione di batteria molto carica.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "Vbattery2_1",
    "value": "14.4V"
  }
]
```

## Scenario 3 - Far variare la batteria nel tempo

- Scenario id: `scenario_3`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `outputs\demo_workspaces\demo_b03\web\chat\b03\scenarios\scenario_3`

### Hypothesis

Una sorgente variabile nel tempo su Vbattery2_1 dovrebbe produrre una risposta temporale osservabile nei LED se il monitor segue la tensione batteria.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "Vbattery2_1",
    "value": "SIN(12 2 0.2)"
  }
]
```
