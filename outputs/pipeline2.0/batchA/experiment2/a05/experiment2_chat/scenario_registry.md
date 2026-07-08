# Experiment 2 scenario registry

- Batch: `batchA`
- Experiment: `experiment2`
- Circuit: `a05`
- Max executable scenarios: `5`
- Created at: `2026-07-08T10:43:43`
- Updated at: `2026-07-08T10:50:21`

## Scenario 1 - Alimentare l’ingresso VMON_INPUT dal connettore

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment2\a05\scenarios\scenario_1`

### Hypothesis

VMON legge 0 V perché il nodo N003 (VMON_INPUT) non è alimentato nel netlist base.

### Actions

```json
[
  {
    "type": "add_voltage_source_between_nodes",
    "positive": "N003",
    "negative": "0",
    "value": "5V"
  }
]
```

## Scenario 2 - Chiudere lo switch TEST riconosciuto

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

Il ramo TEST aperto potrebbe impedire una condizione necessaria al funzionamento del circuito.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```

## Scenario 3 - Pilotare direttamente il nodo misurato dal voltmetro

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

VMON legge 0 V perché il nodo N001 non riceve alcun pilotaggio; il ramo di misura in sé potrebbe essere corretto.

### Actions

```json
[
  {
    "type": "drive_node_voltage",
    "target": "N001",
    "value": "5V"
  }
]
```

## Scenario 4 - Chiudere TEST mentre si alimenta VMON_INPUT

- Scenario id: `scenario_4`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchA\experiment2\a05\scenarios\scenario_4`

### Hypothesis

Il problema principale è già l'assenza di alimentazione su N003; la chiusura di switch25.1 serve solo a verificare se il ramo TEST modifica ulteriormente la lettura su N001.

### Actions

```json
[
  {
    "type": "add_voltage_source_between_nodes",
    "positive": "N003",
    "negative": "0",
    "value": "5V"
  },
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```
