# Pipeline 2.0 scenario registry

- Batch: `batchICChatAgentEvaluation`
- Experiment: `ic_chat_agent_evaluation`
- Circuit: `ic04`
- Max executable scenarios: `5`
- Created at: `2026-08-03T16:44:25`
- Updated at: `2026-08-03T16:47:28`

## Scenario 1 - Rendere piu lenta la modulazione del primo 555

- Scenario id: `scenario_1`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `None`

### Hypothesis

Il cambio di tono e poco evidente perche il timing del primo stadio, centrato su Cpolarized_capacitor20_1, non modula abbastanza il secondo stadio.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Cpolarized_capacitor20_1",
    "value": "22u"
  }
]
```

## Scenario 2 - Aumentare il collegamento di modulazione tra i due 555

- Scenario id: `scenario_2`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic04\scenarios\scenario_2`

### Hypothesis

Il tono cambia poco perche la modulazione dal primo 555 al secondo, attraverso Rresistor22_3, e troppo debole.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_3",
    "value": "4.7k"
  }
]
```

## Scenario 3 - Spostare la frequenza del secondo 555 per separare meglio i due toni

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

Il cambio di suono e poco evidente perche il secondo stadio, legato a Rresistor22_4, Rresistor22_5 e Cpolarized_capacitor20_3, lavora in una gamma poco sensibile alla modulazione.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_4",
    "value": "4.7k"
  }
]
```
