# Pipeline 2.0 scenario registry

- Batch: `batchChatAgentEvaluation`
- Experiment: `chat_agent_evaluation`
- Circuit: `b03`
- Max executable scenarios: `5`
- Created at: `2026-07-24T11:13:05`
- Updated at: `2026-07-24T11:17:36`

## Scenario 1 - Provare una batteria più bassa per il caso scarica

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b03\scenarios\scenario_1`

### Hypothesis

Lowering Vbattery2_1 below the base 12 V level should change the active LED pattern and may reveal the low-battery indication.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "Vbattery2_1",
    "value": "DC 10V"
  }
]
```

## Scenario 2 - Provare una batteria più alta per il caso carica

- Scenario id: `scenario_2`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b03\scenarios\scenario_2`

### Hypothesis

Raising Vbattery2_1 above the base 12 V level should change the active LED pattern and may reveal the charged-battery indication.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "Vbattery2_1",
    "value": "DC 14V"
  }
]
```

## Scenario 3 - Applicare una rampa di batteria per osservare le soglie dei LED

- Scenario id: `scenario_3`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b03\scenarios\scenario_3`

### Hypothesis

A time-varying battery source should reveal when each LED turns on or off during a voltage sweep, unlike the constant 12 V base run.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "Vbattery2_1",
    "value": "PWL(0s 10V 3s 14V)"
  }
]
```

## Scenario 4 - Test statico a 16 V per verificare il solo LED verde

- Scenario id: `scenario_4`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b03\scenarios\scenario_4`

### Hypothesis

Raising Vbattery2_1 from the already tested 14 V to a static 16 V may switch the indication from yellow-plus-green to green-only.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "Vbattery2_1",
    "value": "DC 16V"
  }
]
```
