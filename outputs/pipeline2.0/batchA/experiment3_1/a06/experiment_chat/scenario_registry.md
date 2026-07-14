# Pipeline 2.0 scenario registry

- Batch: `batchA`
- Experiment: `experiment3_1`
- Circuit: `a06`
- Max executable scenarios: `5`
- Created at: `2026-07-14T12:41:37`
- Updated at: `2026-07-14T12:41:45`

## Scenario 1 - Ridurre l’ampiezza del segnale di ingresso

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment3_1\a06\scenarios\scenario_1`

### Hypothesis

The output distortion is mainly caused by an input amplitude that is too large for the present transistor bias point.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "Vsignal_source23_1",
    "value": "SIN(0 0.2 100)"
  }
]
```

## Scenario 2 - Ridurre il bypass dell’emettitore

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

Strong emitter bypassing may be increasing gain but worsening linearity.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Ccapacitor4_2",
    "value": "10u"
  }
]
```

## Scenario 3 - Ridurre la resistenza di bias superiore della base

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

The transistor bias point may be poorly centered because the present base bias network is not placing the device in a sufficiently linear region.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_2",
    "value": "68k"
  }
]
```
