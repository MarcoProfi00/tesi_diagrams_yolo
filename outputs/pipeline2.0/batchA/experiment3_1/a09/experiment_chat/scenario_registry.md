# Pipeline 2.0 scenario registry

- Batch: `batchA`
- Experiment: `experiment3_1`
- Circuit: `a09`
- Max executable scenarios: `5`
- Created at: `2026-07-14T12:59:41`
- Updated at: `2026-07-14T13:02:51`

## Scenario 1 - Chiudere lo switch della lampada

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `not_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment3_1\a09\scenarios\scenario_1`

### Hypothesis

The lamp branch is inactive because switch25.1 is open and prevents any current path to lamp13.1.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```

## Scenario 2 - Alimentare il ramo LED dal suo ingresso naturale

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

The LED branch is inactive because N005 (PWR_LED_INPUT) is not driven in the base netlist.

### Actions

```json
[
  {
    "type": "add_voltage_source_between_nodes",
    "positive": "N005",
    "negative": "0",
    "value": "9V"
  }
]
```

## Scenario 3 - Alimentare il ramo lampada dal suo ingresso naturale

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

The lamp branch input N004 is not powered in the base netlist, so the lamp cannot turn on.

### Actions

```json
[
  {
    "type": "add_voltage_source_between_nodes",
    "positive": "N004",
    "negative": "0",
    "value": "9V"
  }
]
```

## Scenario 4 - Portare BAT_FUSED all’ingresso dello switch della lampada

- Scenario id: `scenario_4`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment3_1\a09\scenarios\scenario_4`

### Hypothesis

The lamp branch stays inactive because N004 is not actually receiving supply from the powered node N003; if N003 is connected to N004 and switch25.1 is closed, voltage should propagate to N006 and activate Rlamp13_1.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  },
  {
    "type": "connect_nodes",
    "from": "N003",
    "to": "N004",
    "resistance": "1m"
  }
]
```

## Scenario 5 - Portare BAT_FUSED all’ingresso del ramo LED

- Scenario id: `scenario_5`
- Status: `executed`
- Outcome: `resolved_candidate`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_3`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment3_1\a09\scenarios\scenario_5`

### Hypothesis

The LED branch stays inactive because N005 is not receiving supply from the already powered node N003; if N003 is connected to N005, voltage should propagate to N007 through Rresistor22_1 and activate the LED branch.

### Actions

```json
[
  {
    "type": "connect_nodes",
    "from": "N003",
    "to": "N005",
    "resistance": "1m"
  }
]
```

## Scenario 6 - Alimentare contemporaneamente ramo lampada e ramo LED

- Scenario id: `scenario_6`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_4`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment3_1\a09\scenarios\scenario_6`

### Hypothesis

Both branches stay inactive in the base run because BAT_FUSED at N003 does not reach both branch inputs; if N003 is connected to N004 and N005 and switch25.1 is closed, both lamp and LED branches should activate together.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  },
  {
    "type": "connect_nodes",
    "from": "N003",
    "to": "N004",
    "resistance": "1m"
  },
  {
    "type": "connect_nodes",
    "from": "N003",
    "to": "N005",
    "resistance": "1m"
  }
]
```
