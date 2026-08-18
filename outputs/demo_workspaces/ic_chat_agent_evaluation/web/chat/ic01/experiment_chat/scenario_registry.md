# Pipeline 2.0 scenario registry

- Batch: `batchICChatAgentEvaluation`
- Experiment: `ic_chat_agent_evaluation`
- Circuit: `ic01`
- Max executable scenarios: `5`
- Created at: `2026-07-30T11:50:45`
- Updated at: `2026-07-30T11:54:46`

## Scenario 1 - Forzare un avvio asimmetrico del nodo di temporizzazione

- Scenario id: `scenario_1`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `None`

### Hypothesis

L'irregolarita del lampeggio in avvio dipende soprattutto dalle condizioni iniziali del nodo N001 (TRIG/THRES) e dalla fase di startup del 555.

### Actions

```json
[
  {
    "type": "set_initial_node_voltage",
    "target": "N001",
    "value": "0V",
    "skip_operating_point": true
  }
]
```

## Scenario 2 - Ridurre l'influenza del ramo di controllo sul pin CONT

- Scenario id: `scenario_2`
- Status: `executed`
- Outcome: `resolved_candidate`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic01\scenarios\scenario_2`

### Hypothesis

Il condensatore Ccapacitor4_2 sul nodo N002 (CONT) contribuisce all'irregolarita di startup del 555.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Ccapacitor4_2",
    "value": "100n"
  }
]
```

## Scenario 3 - Aumentare la costante di tempo del nodo di soglia e trigger

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

La rete di timing principale sul nodo N001 produce uno startup irregolare; aumentando Ccapacitor4_1 il lampeggio potrebbe diventare piu regolare.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Ccapacitor4_1",
    "value": "10u"
  }
]
```
