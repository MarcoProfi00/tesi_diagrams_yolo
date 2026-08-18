# Pipeline 2.0 scenario registry

- Batch: `batchICChatAgentEvaluation`
- Experiment: `ic_chat_agent_evaluation`
- Circuit: `ic03`
- Max executable scenarios: `5`
- Created at: `2026-08-03T15:18:12`
- Updated at: `2026-08-03T15:25:12`

## Scenario 1 - Aumentare C2 per rallentare il lampeggio

- Scenario id: `scenario_1`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `None`

### Hypothesis

Il periodo di lampeggio dipende in modo sensibile da Cpolarized_capacitor20_3 nella rete di temporizzazione.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Cpolarized_capacitor20_3",
    "value": "22u"
  }
]
```

## Scenario 2 - Aumentare C3 per testare il ramo di temporizzazione su N004

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

Cpolarized_capacitor20_2 contribuisce in modo rilevante alla frequenza di lampeggio.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Cpolarized_capacitor20_2",
    "value": "22u"
  }
]
```

## Scenario 3 - Aumentare R1 per testare la costante di tempo resistiva

- Scenario id: `scenario_3`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic03\scenarios\scenario_3`

### Hypothesis

Rresistor22_3 è una delle resistenze che fissano il periodo e un suo valore troppo basso accelera il lampeggio.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_3",
    "value": "22k"
  }
]
```

## Scenario 4 - Aumentare ancora R1

- Scenario id: `scenario_4`
- Status: `executed`
- Outcome: `resolved_candidate`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic03\scenarios\scenario_4`

### Hypothesis

Poiche l'aumento di Rresistor22_3 da 10k a 22k ha gia rallentato il lampeggio senza raggiungere il target, un ulteriore aumento della stessa resistenza puo ridurre ancora la frequenza di Rlamp13_1.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_3",
    "value": "33k"
  }
]
```

## Scenario 5 - Aumentare R2

- Scenario id: `scenario_5`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

Rresistor22_1 partecipa alla rete di temporizzazione tra N004 e N005 e un suo aumento puo rallentare il lampeggio di Rlamp13_1.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_1",
    "value": "22k"
  }
]
```

## Scenario 6 - Aumentare R3

- Scenario id: `scenario_6`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

Rresistor22_2 fornisce il percorso resistivo verso massa del nodo N005 e un suo aumento puo allungare la costante di tempo della rete che controlla il lampeggio.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_2",
    "value": "22k"
  }
]
```
