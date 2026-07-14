# Experiment 2 scenario registry

- Batch: `batchA`
- Experiment: `experiment2`
- Circuit: `a08`
- Max executable scenarios: `5`
- Created at: `2026-07-09T09:30:22`
- Updated at: `2026-07-09T09:48:55`

## Scenario 1 - Variare l’ampiezza della sorgente quadra esistente

- Scenario id: `scenario_1`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `None`

### Hypothesis

Il comportamento anomalo del LED dipende dall'ampiezza assunta della sorgente Vsignal_source23_1.

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

## Scenario 2 - Ridurre la resistenza di base Rresistor22_4

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

La base del transistor potrebbe essere pilotata troppo debolmente da Rresistor22_4.

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

## Scenario 3 - Aumentare la resistenza di emettitore Rresistor22_2

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

Il ramo emettitore potrebbe impedire una commutazione netta del transistor e quindi del LED.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_2",
    "value": "1k"
  }
]
```

## Scenario 4 - Rinforzare l'accoppiamento resistivo tra TRIGGER e base

- Scenario id: `scenario_4`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment2\a08\scenarios\scenario_4`

### Hypothesis

The trigger-to-base coupling may be too weak because the existing resistive path between N001 and N004 is not sufficient by itself.

### Actions

```json
[
  {
    "type": "add_resistor_between_nodes",
    "from": "N001",
    "to": "N004",
    "value": "33k"
  }
]
```

## Scenario 5 - Aumentare l'ampiezza della sorgente di ingresso

- Scenario id: `scenario_5`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_3`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment2\a08\scenarios\scenario_5`

### Hypothesis

If a stronger excitation on the existing input source causes a clearer change on N004, N003 and N005, the missing blinking depends primarily on input excitation rather than only on the transistor-LED branch bias.

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

## Scenario 6 - Rinforzare il pilotaggio della base e aumentare insieme l'ingresso

- Scenario id: `scenario_6`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_4`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment2\a08\scenarios\scenario_6`

### Hypothesis

A clearer LED blinking may emerge if the trigger-to-base coupling and the input excitation amplitude are strengthened together, since both hypotheses were separately supported by scenario_4 and scenario_5.

### Actions

```json
[
  {
    "type": "add_resistor_between_nodes",
    "from": "N001",
    "to": "N004",
    "value": "33k"
  },
  {
    "type": "change_source_value",
    "target": "Vsignal_source23_1",
    "value": "PULSE(0 10 0 1ms 1ms 50ms 100ms)"
  }
]
```

## Scenario 7 - Ridurre la resistenza di bias tra TRIGGER e base

- Scenario id: `scenario_7`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_5`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment2\a08\scenarios\scenario_7`

### Hypothesis

The existing base-bias resistor Rresistor22_4 may be too large; lowering it should strengthen the drive from N001 to N004 and may produce a clearer LED-related transistor response.

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

## Scenario 8 - Ridurre la resistenza dell'emettitore verso massa

- Scenario id: `scenario_8`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_6`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment2\a08\scenarios\scenario_8`

### Hypothesis

The remaining limit may be in the emitter bias path: lowering Rresistor22_2 should change N005 more strongly and may produce a clearer transistor-LED switching response than further trigger-to-base strengthening.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_2",
    "value": "330"
  }
]
```
