# Pipeline 2.0 scenario registry

- Batch: `batchChatAgentEvaluation`
- Experiment: `chat_agent_evaluation`
- Circuit: `c03`
- Max executable scenarios: `5`
- Created at: `2026-07-27T16:30:14`
- Updated at: `2026-07-27T16:32:03`

## Scenario 1 - Aumentare controllatamente il livello di VAUDIO_IN

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\c03\scenarios\scenario_1`

### Hypothesis

The simulated low output may be caused mainly by the very small existing input source amplitude.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "VAUDIO_IN",
    "value": "SIN(0 0.05 1000)"
  }
]
```
