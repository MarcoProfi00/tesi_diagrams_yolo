# Pipeline 2.0 scenario registry

- Batch: `batchB`
- Experiment: `experiment5`
- Circuit: `b05`
- Max executable scenarios: `5`
- Created at: `2026-07-18T18:29:31`
- Updated at: `2026-07-18T18:30:06`

## Scenario 1 - Chiudere lo switch di alimentazione

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `resolved_candidate`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchB\experiment5\chat\b05\scenarios\scenario_1`

### Hypothesis

The open switch25.1 is preventing the battery supply on N002 from reaching N004 and the headset branch.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```

## Scenario 2 - Collegare N002 a N004

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

The battery node N002 may need to be electrically continuous with N004 for the audio branch to become powered.

### Actions

```json
[
  {
    "type": "connect_nodes",
    "from": "N002",
    "to": "N004",
    "resistance": "1m"
  }
]
```

## Scenario 3 - Iniettare un segnale di prova sul nodo antenna

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

The radio path may be silent because antenna1.1 is not emitted, so N001 receives no excitation in the base run.

### Actions

```json
[
  {
    "type": "drive_node_voltage",
    "target": "N001",
    "value": "100mV"
  }
]
```
