# Pipeline 2.0 scenario registry

- Batch: `batchChatAgentEvaluation`
- Experiment: `chat_agent_evaluation`
- Circuit: `a08`
- Max executable scenarios: `5`
- Created at: `2026-07-23T16:09:48`
- Updated at: `2026-07-23T16:10:15`

## Scenario 1 - Verificare l'ampiezza della sorgente di ingresso

- Scenario id: `scenario_1`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `None`

### Hypothesis

The LED may fail to blink regularly because the assumed amplitude of Vsignal_source23_1 is not sufficient for the extracted bias network.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "Vsignal_source23_1",
    "value": "PULSE(0 10 0 1ms 1ms 50ms 100ms)"
  }
]
```

## Scenario 2 - Ridurre la resistenza di bias della base

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

The base drive through Rresistor22_4 may be too weak to produce a regular LED blinking behavior.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_4",
    "value": "33k"
  }
]
```

## Scenario 3 - Cambiare la costante di tempo del trigger

- Scenario id: `scenario_3`
- Status: `executed`
- Outcome: `resolved_candidate`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a08\scenarios\scenario_3`

### Hypothesis

The RC branch around Ccapacitor4_1 may be producing only edge transients instead of a timing behavior compatible with regular LED blinking.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Ccapacitor4_1",
    "value": "1u"
  }
]
```
