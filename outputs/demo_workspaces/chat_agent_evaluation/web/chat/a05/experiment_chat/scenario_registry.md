# Pipeline 2.0 scenario registry

- Batch: `batchChatAgentEvaluation`
- Experiment: `chat_agent_evaluation`
- Circuit: `a05`
- Max executable scenarios: `5`
- Created at: `2026-07-23T12:17:13`
- Updated at: `2026-07-23T12:17:59`

## Scenario 1 - Alimentare VMON_INPUT dal connettore di ingresso

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a05\scenarios\scenario_1`

### Hypothesis

VMON reads 0 V because node N003 (VMON_INPUT) is not driven in the base netlist.

### Actions

```json
[
  {
    "type": "add_voltage_source_between_nodes",
    "positive": "N003",
    "negative": "0",
    "value": "5V"
  }
]
```

## Scenario 2 - Chiudere lo switch TEST

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

The open switch25.1 may be keeping node N004 inactive, and this may help determine whether the TEST branch is related to the 0 V reading.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```

## Scenario 3 - Alimentare il nodo TEST dal connettore

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

The useful excitation may be expected on node N004 (TEST), but the base netlist leaves it unpowered.

### Actions

```json
[
  {
    "type": "add_voltage_source_between_nodes",
    "positive": "N004",
    "negative": "0",
    "value": "5V"
  }
]
```
