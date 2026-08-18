# Pipeline 2.0 scenario registry

- Batch: `batchB`
- Experiment: `experiment5`
- Circuit: `b06`
- Max executable scenarios: `5`
- Created at: `2026-07-20T15:58:25`
- Updated at: `2026-07-20T16:00:50`

## Scenario 1 - Iniettare un piccolo segnale all'ingresso del LM386_SIMPLE

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchB\experiment5\chat\b06\scenarios\scenario_1`

### Hypothesis

The audio stage may be functional but inactive because node N010 receives no useful signal in the base run.

### Actions

```json
[
  {
    "type": "add_voltage_source_between_nodes",
    "positive": "N010",
    "negative": "0",
    "value": "SIN(0 5m 1000)"
  }
]
```

## Scenario 2 - Iniettare un piccolo segnale sulla base del transistor Qnpn_transistor18_1

- Scenario id: `scenario_2`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `outputs\pipeline2.0\batchB\experiment5\chat\b06\scenarios\scenario_2`

### Hypothesis

The signal may be getting lost in or before the transistor stage, while the transistor still has a valid DC bias point.

### Actions

```json
[
  {
    "type": "add_voltage_source_between_nodes",
    "positive": "N005",
    "negative": "0",
    "value": "SIN(0.660106 5m 1000)"
  }
]
```
