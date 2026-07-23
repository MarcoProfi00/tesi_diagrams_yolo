# Pipeline 2.0 scenario registry

- Batch: `batchChatAgentEvaluation`
- Experiment: `chat_agent_evaluation`
- Circuit: `a01`
- Max executable scenarios: `5`
- Created at: `2026-07-23T10:37:03`
- Updated at: `2026-07-23T10:41:13`

## Scenario 1 - Alimentare direttamente l’ingresso del ramo lampada

- Scenario id: `scenario_1`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `None`

### Hypothesis

The lamp branch is off because node N002 is not powered in the base netlist.

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

## Scenario 2 - Propagare l’alimentazione esistente da N001 al ramo lampada

- Scenario id: `scenario_2`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a01\scenarios\scenario_2`

### Hypothesis

The lamp branch is inactive because the powered node N001 does not electrically reach branch input N002.

### Actions

```json
[
  {
    "type": "feed_nodes_from_source_node",
    "source_node": "N001",
    "target_nodes": [
      "N002"
    ],
    "resistance": "1m"
  }
]
```

## Scenario 3 - Chiudere lo switch riconosciuto

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

The recognized open switch may influence the inactive condition of the circuit, even though no direct lamp-path link is visible in the base netlist.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```

## Scenario 4 - Ripristinare la continuità tra N001 e N002 mantenendo attivi lampada e LED

- Scenario id: `scenario_4`
- Status: `executed`
- Outcome: `resolved_candidate`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a01\scenarios\scenario_4`

### Hypothesis

The user symptom is caused by missing continuity between N001 and N002; restoring that continuity should activate the lamp branch while preserving current in the LED branch already fed from N001.

### Actions

```json
[
  {
    "type": "connect_nodes",
    "from": "N001",
    "to": "N002",
    "resistance": "1m"
  }
]
```
