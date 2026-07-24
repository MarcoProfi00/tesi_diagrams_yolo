# Pipeline 2.0 scenario registry

- Batch: `batchChatAgentEvaluation`
- Experiment: `chat_agent_evaluation`
- Circuit: `b05`
- Max executable scenarios: `5`
- Created at: `2026-07-24T12:07:16`
- Updated at: `2026-07-24T12:21:30`

## Scenario 1 - Chiudere l’interruttore di alimentazione riconosciuto

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b05\scenarios\scenario_1`

### Hypothesis

The circuit stays inactive because switch25.1 is open and prevents the battery from feeding node N004 and the bias/audio network.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```

## Scenario 2 - Iniettare un piccolo segnale sull’ingresso antenna

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

The base run has no useful RF/audio excitation because antenna1.1 is unsupported and no source drives node N001.

### Actions

```json
[
  {
    "type": "add_voltage_source_between_nodes",
    "positive": "N001",
    "negative": "0",
    "value": "SIN(0 10m 1000)"
  }
]
```

## Scenario 3 - Ridurre la resistenza di bias del primo stadio

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

The first transistor stage may remain insufficiently biased because Rresistor22_1 keeps node N006 too weakly referenced.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_1",
    "value": "33k"
  }
]
```

## Scenario 4 - Iniettare un piccolo segnale sull’ingresso antenna con interruttore chiuso

- Scenario id: `scenario_4`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b05\scenarios\scenario_4`

### Hypothesis

After closing switch25.1, the circuit may still need an explicit AC excitation at N001 to verify whether useful signal reaches the headset load between N003 and N004.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  },
  {
    "type": "add_voltage_source_between_nodes",
    "positive": "N001",
    "negative": "0",
    "value": "SIN(0 5m 1000)"
  }
]
```

## Scenario 5 - Pilotare direttamente N008 per isolare lo stadio finale

- Scenario id: `scenario_5`
- Status: `executed`
- Outcome: `not_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_3`
- Source local index: `3`
- Execution path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b05\scenarios\scenario_5`

### Hypothesis

If a small AC signal injected directly at N008 still does not produce useful output across N003-N004, the final stage around Qnpn_transistor18_2 and the headset-equivalent load is the likely signal-loss boundary.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  },
  {
    "type": "add_voltage_source_between_nodes",
    "positive": "N008",
    "negative": "0",
    "value": "SIN(0 5m 1000)"
  }
]
```
