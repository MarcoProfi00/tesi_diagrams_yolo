# Pipeline 2.0 scenario registry

- Batch: `batchDemo`
- Experiment: `demo_batch`
- Circuit: `a08`
- Max executable scenarios: `5`
- Created at: `2026-07-22T10:09:47`
- Updated at: `2026-07-22T10:12:31`

## Scenario 1 - Ridurre la resistenza di base Rresistor22_4

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `resolved_candidate`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\demo_batch\web\chat\a08\scenarios\scenario_1`

### Hypothesis

The base drive of Qnpn_transistor18_1 may be too weak through Rresistor22_4, preventing regular LED blinking.

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

## Scenario 2 - Aumentare la costante di tempo di Ccapacitor4_1

- Scenario id: `scenario_2`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `outputs\demo_workspaces\demo_batch\web\chat\a08\scenarios\scenario_2`

### Hypothesis

The RC timing around N001 may be too short, causing only transient LED pulses instead of regular blinking.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Ccapacitor4_1",
    "value": "22u"
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

The assumed 0-5 V input on Vsignal_source23_1 may be insufficient or not representative for obtaining regular LED blinking in the extracted circuit.

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
