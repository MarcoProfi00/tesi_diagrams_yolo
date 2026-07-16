# Pipeline 2.0 scenario registry

- Batch: `batchA`
- Experiment: `experiment4`
- Circuit: `a04`
- Max executable scenarios: `5`
- Created at: `2026-07-16T10:30:26`
- Updated at: `2026-07-16T10:30:37`

## Scenario 1 - Aumentare l'ampiezza della sorgente di ingresso

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment4\chat\a04\scenarios\scenario_1`

### Hypothesis

The output appears too weak mainly because Vsignal_source23_1 drives only 10 mV amplitude.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "Vsignal_source23_1",
    "value": "SIN(0 0.1 100)"
  }
]
```

## Scenario 2 - Rafforzare il bypass dell'emettitore

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

Ccapacitor4_2 may be too small at 100 Hz, so emitter degeneration through Rresistor22_4 reduces gain.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Ccapacitor4_2",
    "value": "100u"
  }
]
```

## Scenario 3 - Ridurre la resistenza di emettitore

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

Rresistor22_4 may be limiting stage gain more than expected.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_4",
    "value": "470"
  }
]
```
