# Pipeline 2.0 scenario registry

- Batch: `batchChatAgentEvaluation`
- Experiment: `chat_agent_evaluation`
- Circuit: `a10`
- Max executable scenarios: `5`
- Created at: `2026-07-24T10:56:42`
- Updated at: `2026-07-24T10:57:31`

## Scenario 1 - Chiudere lo switch e propagare l'alimentazione ai rami LED e lampada

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a10\scenarios\scenario_1`

### Hypothesis

The battery is present but the positive supply does not reach the LED and lamp branches because switch25.1 is open and the branch input nodes N003 and N004 are not fed from the switched supply path.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  },
  {
    "type": "feed_nodes_from_source_node",
    "source_node": "N002",
    "target_nodes": [
      "N003",
      "N004"
    ],
    "resistance": "1m"
  }
]
```
