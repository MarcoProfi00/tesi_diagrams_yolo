# Pipeline 2.0 scenario registry

- Batch: `batchA`
- Experiment: `experiment4`
- Circuit: `a06`
- Max executable scenarios: `5`
- Created at: `2026-07-16T13:16:39`
- Updated at: `2026-07-16T13:19:50`

## Scenario 1 - Ridurre l’ampiezza del segnale di ingresso

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment4\chat\a06\scenarios\scenario_1`

### Hypothesis

The output distortion may be caused mainly by an input amplitude that is too large for the current transistor bias point.

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

## Scenario 2 - Abbassare la resistenza di bias alta della base

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

The transistor may be biased too close to cutoff because the upper base-bias resistor is too large.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_2",
    "value": "47k"
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

The emitter branch may be keeping the transistor too weakly biased, contributing to nonlinear output behavior.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_5",
    "value": "1k"
  }
]
```

## Scenario 4 - Aumentare la resistenza di emettitore

- Scenario id: `scenario_4`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `2`
- Execution path: `outputs\pipeline2.0\batchA\experiment4\chat\a06\scenarios\scenario_4`

### Hypothesis

The output distortion may be dominated by the emitter bias and stabilization conditions rather than by the input amplitude.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_5",
    "value": "10k"
  }
]
```

## Scenario 5 - Alleggerire il carico di uscita

- Scenario id: `scenario_5`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `3`
- Execution path: `outputs\pipeline2.0\batchA\experiment4\chat\a06\scenarios\scenario_5`

### Hypothesis

The output branch may be contributing significantly to the large and unclean output waveform.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_6",
    "value": "47k"
  }
]
```
