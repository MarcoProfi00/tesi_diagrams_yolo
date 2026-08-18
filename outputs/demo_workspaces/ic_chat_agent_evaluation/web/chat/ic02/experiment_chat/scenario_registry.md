# Pipeline 2.0 scenario registry

- Batch: `batchICChatAgentEvaluation`
- Experiment: `ic_chat_agent_evaluation`
- Circuit: `ic02`
- Max executable scenarios: `5`
- Created at: `2026-08-03T11:28:43`
- Updated at: `2026-08-03T11:35:29`

## Scenario 1 - Misurare il guadagno utile all’uscita con il circuito invariato

- Scenario id: `scenario_1`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `None`

### Hypothesis

Il circuito trasferisce il segnale ma con guadagno troppo basso tra N011 e N007.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "VAUDIO_IN",
    "value": "SIN(0 0.02 1000)"
  }
]
```

## Scenario 2 - Alleggerire il carico di uscita

- Scenario id: `scenario_2`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic02\scenarios\scenario_2`

### Hypothesis

Il volume basso dipende dal carico Rspeaker24_1 da 4 ohm che riduce troppo l'ampiezza utile su N007.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rspeaker24_1",
    "value": "8"
  }
]
```

## Scenario 3 - Ridurre la resistenza di feedback principale

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

Rresistor22_5 potrebbe imporre un guadagno troppo basso nel circuito estratto.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_5",
    "value": "100k"
  }
]
```

## Scenario 4 - Ridurre la resistenza verso N009 nella rete di feedback

- Scenario id: `scenario_4`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic02\scenarios\scenario_4`

### Hypothesis

Il volume basso e determinato soprattutto dalla rete di guadagno attorno a N006/N009, non dal carico Rspeaker24_1.

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

## Scenario 5 - Aumentare la resistenza di feedback tra N007 e N006

- Scenario id: `scenario_5`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

La retroazione esterna tramite Rresistor22_5 limita piu del carico l'ampiezza utile di uscita.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_5",
    "value": "220k"
  }
]
```

## Scenario 6 - Aumentare il condensatore di ingresso sul ramo N005-N008

- Scenario id: `scenario_6`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

Il volume basso puo dipendere da attenuazione nel ramo di ingresso non invertente attorno a Cpolarized_capacitor20_1.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Cpolarized_capacitor20_1",
    "value": "2.2u"
  }
]
```
