# Pipeline 2.0 scenario registry

- Batch: `batchB`
- Experiment: `experiment5`
- Circuit: `b05`
- Max executable scenarios: `5`
- Created at: `2026-07-18T19:28:58`
- Updated at: `2026-07-18T19:39:15`

## Scenario 1 - Chiudere lo switch di alimentazione riconosciuto

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchB\experiment5\chat\b05\scenarios\scenario_1`

### Hypothesis

The open switch switch25.1 may be isolating battery2.1 from the rest of the circuit, leaving the headset branch unpowered.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```

## Scenario 2 - Collegare il nodo batteria al nodo del ramo audio

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

The circuit may be inactive because N002 is not electrically continuous with N004, which feeds the bias and headset branch.

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

## Scenario 3 - Applicare un segnale di prova al nodo antenna

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

The base run may stay silent because antenna1.1 is unsupported and no AC excitation reaches N001.

### Actions

```json
[
  {
    "type": "add_voltage_source_between_nodes",
    "positive": "N001",
    "negative": "0",
    "value": "SIN(0 1 1000)"
  }
]
```

## Scenario 4 - Iniettare un segnale sul nodo antenna con alimentazione inserita

- Scenario id: `scenario_4`
- Status: `executed`
- Outcome: `not_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchB\experiment5\chat\b05\scenarios\scenario_4`

### Hypothesis

With switch25.1 closed, the circuit may still be silent only because the base netlist has no AC excitation at N001; adding a sinusoidal input there should reveal whether useful signal reaches the headset output between N003 and N004.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  },
  {
    "type": "add_voltage_source_between_nodes",
    "positive": "N001",
    "negative": "0",
    "value": "SIN(0 100m 1000)"
  }
]
```

## Scenario 5 - Iniettare il segnale direttamente su N005 verso le cuffie

- Scenario id: `scenario_5`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_3`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchB\experiment5\chat\b05\scenarios\scenario_5`

### Hypothesis

With switch25.1 closed, injecting a sinusoidal signal directly at N005 should reveal whether the downstream path from N005 to the headset output v(N003,N004) can transfer useful signal.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  },
  {
    "type": "add_voltage_source_between_nodes",
    "positive": "N005",
    "negative": "0",
    "value": "SIN(0 100m 1000)"
  }
]
```

## Scenario 6 - Iniettare su N001 un segnale piu ampio con switch chiuso

- Scenario id: `scenario_6`
- Status: `executed`
- Outcome: `resolved_candidate`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_4`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchB\experiment5\chat\b05\scenarios\scenario_6`

### Hypothesis

With switch25.1 closed, the previous stimulus at N001 may have been too small to drive useful transfer through diode7.1; a larger sinusoidal input at N001 should test whether a usable signal can then reach v(N003,N004).

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  },
  {
    "type": "add_voltage_source_between_nodes",
    "positive": "N001",
    "negative": "0",
    "value": "SIN(0 1 1000)"
  }
]
```
