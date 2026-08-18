# Pipeline 2.0 scenario registry

- Batch: `batchChatAgentEvaluation`
- Experiment: `chat_agent_evaluation`
- Circuit: `a09`
- Max executable scenarios: `5`
- Created at: `2026-07-24T10:48:54`
- Updated at: `2026-07-24T10:49:47`

## Scenario 1 - Alimentare entrambi i rami dal nodo BAT_FUSED e chiudere SW2

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a09\scenarios\scenario_1`

### Hypothesis

The powered node N003 is not reaching the lamp-input node N004 nor the LED-input node N005, and the lamp branch is also blocked by open switch25.1.

### Actions

```json
[
  {
    "type": "feed_nodes_from_source_node",
    "source_node": "N003",
    "target_nodes": [
      "N004",
      "N005"
    ],
    "resistance": "1m"
  },
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```
