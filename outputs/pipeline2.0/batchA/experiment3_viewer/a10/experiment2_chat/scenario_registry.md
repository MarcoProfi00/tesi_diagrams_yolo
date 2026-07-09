# Experiment 2 scenario registry

- Batch: `batchA`
- Experiment: `experiment2`
- Circuit: `a10`
- Max executable scenarios: `5`
- Created at: `2026-07-07T09:45:15`
- Updated at: `2026-07-07T10:13:22`

## Scenario 1 - Chiudere l'interruttore riconosciuto

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `not_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment2\a10\scenarios\scenario_1`

### Hypothesis

The open switch is preventing battery voltage from reaching the downstream circuit.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```

## Scenario 2 - Alimentare direttamente l'ingresso del ramo LED

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

The LED branch is off because node N003 is not driven.

### Actions

```json
[
  {
    "type": "drive_node_voltage",
    "target": "N003",
    "value": "5V"
  }
]
```

## Scenario 3 - Alimentare direttamente il ramo della lampada

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

The lamp branch is off because node N004 is not driven.

### Actions

```json
[
  {
    "type": "drive_node_voltage",
    "target": "N004",
    "value": "5V"
  }
]
```

## Scenario 4 - Collegare l'uscita dello switch al ramo LED-resistenza

- Scenario id: `scenario_4`
- Status: `executed`
- Outcome: `not_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment2\a10\scenarios\scenario_4`

### Hypothesis

Dopo la chiusura di switch25.1, i rami finali restano spenti perché N002 non è elettricamente continuo con N003.

### Actions

```json
[
  {
    "type": "connect_nodes",
    "from": "N002",
    "to": "N003",
    "resistance": "1m"
  }
]
```

## Scenario 5 - Alimentare il ramo LED-resistenza con switch chiuso e continuità verso N003

- Scenario id: `scenario_5`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_3`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment2\a10\scenarios\scenario_5`

### Hypothesis

I due scenari precedenti erano complementari: il ramo Rresistor22_1-Dled12_1 resta spento nella base run perché serve sia chiudere switch25.1 sia collegare N002 a N003 nello stesso scenario.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  },
  {
    "type": "connect_nodes",
    "from": "N002",
    "to": "N003",
    "resistance": "1m"
  }
]
```

## Scenario 6 - Alimentare il ramo lampada con switch chiuso e continuità verso N004

- Scenario id: `scenario_6`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_4`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment2\a10\scenarios\scenario_6`

### Hypothesis

Come nel ramo LED, anche il ramo Rlamp13_1 resta spento nella base run perché serve sia chiudere switch25.1 sia collegare N002 a N004 nello stesso scenario.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  },
  {
    "type": "connect_nodes",
    "from": "N002",
    "to": "N004",
    "resistance": "1m"
  }
]
```
