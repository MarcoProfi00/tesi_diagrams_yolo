# Pipeline 2.0 scenario registry

- Batch: `batchA`
- Experiment: `experiment3_1`
- Circuit: `a04`
- Max executable scenarios: `5`
- Created at: `2026-07-14T12:12:55`
- Updated at: `2026-07-14T12:13:26`

## Scenario 1 - Aumentare l'ampiezza della sorgente di ingresso

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment3_1\a04\scenarios\scenario_1`

### Hypothesis

The output looks weak mainly because the existing source Vsignal_source23_1 drives the amplifier with only 10 mV amplitude.

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

## Scenario 2 - Ridurre la resistenza di emettitore Rresistor22_4

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

The output may be weak because emitter degeneration through Rresistor22_4 limits the stage gain.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_4",
    "value": "330"
  }
]
```

## Scenario 3 - Rafforzare il bias della base riducendo Rresistor22_2

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

The output may be weak because the base bias at N003 is not optimal for a larger collector swing.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_2",
    "value": "10k"
  }
]
```
