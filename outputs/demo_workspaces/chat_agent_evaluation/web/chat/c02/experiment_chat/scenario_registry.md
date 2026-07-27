# Pipeline 2.0 scenario registry

- Batch: `batchChatAgentEvaluation`
- Experiment: `chat_agent_evaluation`
- Circuit: `c02`
- Max executable scenarios: `5`
- Created at: `2026-07-27T14:00:33`
- Updated at: `2026-07-27T14:01:22`

## Scenario 1 - Ridurre la resistenza di bias verso Q2

- Scenario id: `scenario_1`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `None`

### Hypothesis

Il bilanciamento del multivibratore potrebbe dipendere dalla polarizzazione della base N007 tramite Rresistor22_2.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_2",
    "value": "33k"
  }
]
```

## Scenario 2 - Ridurre la resistenza di bias verso Q1

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

Il bilanciamento del multivibratore potrebbe dipendere dalla polarizzazione della base N005 tramite Rresistor22_3.

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

## Scenario 3 - Ridurre il condensatore di accoppiamento C1

- Scenario id: `scenario_3`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\c02\scenarios\scenario_3`

### Hypothesis

Il comportamento osservato potrebbe dipendere dal valore assunto di Cpolarized_capacitor20_1, che non è confermato direttamente dall'evidenza visiva.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Cpolarized_capacitor20_1",
    "value": "4.7u"
  }
]
```
