# Experiment 2 scenario registry

- Batch: `batchA`
- Experiment: `experiment2`
- Circuit: `a09`
- Max executable scenarios: `5`
- Created at: `2026-07-07T10:34:06`
- Updated at: `2026-07-07T10:46:52`

## Scenario 1 - Chiudere lo switch della lampada

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `not_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment2\a09\scenarios\scenario_1`

### Hypothesis

La lampada non si accende perché switch25.1 è aperto e interrompe il percorso verso N006.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```

## Scenario 2 - Alimentare l'ingresso del ramo LED

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

Il LED non si accende perché N005/PWR_LED_INPUT non è pilotato nel circuito base.

### Actions

```json
[
  {
    "type": "drive_node_voltage",
    "target": "N005",
    "value": "9V"
  }
]
```

## Scenario 3 - Collegare l'uscita del fusibile al ramo LED

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

Il ramo LED resta spento perché N005 non è elettricamente continuo con N003/BAT_FUSED.

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

## Scenario 4 - Collegare BAT_FUSED a SW2_INPUT e chiudere lo switch

- Scenario id: `scenario_4`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment2\a09\scenarios\scenario_4`

### Hypothesis

Il ramo della lampada resta spento perché N004 non ha continuità con il nodo alimentato N003; chiudere solo switch25.1 non basta senza alimentazione su N004.

### Actions

```json
[
  {
    "type": "connect_nodes",
    "from": "N003",
    "to": "N004",
    "resistance": "1m"
  },
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```

## Scenario 5 - Collegare BAT_FUSED a PWR_LED_INPUT

- Scenario id: `scenario_5`
- Status: `executed`
- Outcome: `resolved_candidate`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_3`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment2\a09\scenarios\scenario_5`

### Hypothesis

Il ramo LED resta inattivo perché N005 (PWR_LED_INPUT) non ha continuità con il nodo alimentato N003 (BAT_FUSED); collegandoli il ramo LED dovrebbe attivarsi.

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
