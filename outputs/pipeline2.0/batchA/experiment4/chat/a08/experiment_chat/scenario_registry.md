# Pipeline 2.0 scenario registry

- Batch: `batchA`
- Experiment: `experiment4`
- Circuit: `a08`
- Max executable scenarios: `5`
- Created at: `2026-07-16T18:12:29`
- Updated at: `2026-07-16T18:15:21`

## Scenario 1 - Ridurre la resistenza di base Rresistor22_4

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment4\chat\a08\scenarios\scenario_1`

### Hypothesis

Il lampeggio del LED e troppo stretto perche il pilotaggio della base tramite Rresistor22_4 e troppo debole o lento.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_4",
    "value": "33k"
  }
]
```

## Scenario 2 - Ridurre il condensatore Ccapacitor4_1

- Scenario id: `scenario_2`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `outputs\pipeline2.0\batchA\experiment4\chat\a08\scenarios\scenario_2`

### Hypothesis

La costante di tempo del ramo RC limita troppo la durata dell'accensione del LED.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Ccapacitor4_1",
    "value": "1u"
  }
]
```

## Scenario 3 - Aumentare l'ampiezza della sorgente Vsignal_source23_1

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

Il comportamento del LED dipende dall'assunzione di una sorgente 0-5 V, che potrebbe essere troppo bassa rispetto al circuito reale.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "Vsignal_source23_1",
    "value": "PULSE(0 10 0 1ms 1ms 50ms 100ms)"
  }
]
```
