# Pipeline 2.0 scenario registry

- Batch: `batchB`
- Experiment: `experiment5`
- Circuit: `b03`
- Max executable scenarios: `5`
- Created at: `2026-07-20T10:09:07`
- Updated at: `2026-07-20T10:45:01`

## Scenario 1 - Abbassare la tensione della batteria

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchB\experiment5\chat\b03\scenarios\scenario_1`

### Hypothesis

Se il monitor distingue una batteria scarica, riducendo la sorgente Vbattery2_1 devono cambiare i nodi dei rami indicatori e il punto di lavoro del circuito.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "Vbattery2_1",
    "value": "DC 10V"
  }
]
```

## Scenario 2 - Aumentare la tensione della batteria verso una condizione di batteria molto carica

- Scenario id: `scenario_2`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchB\experiment5\chat\b03\scenarios\scenario_2`

### Hypothesis

Se il monitor distingue una batteria molto carica, aumentando Vbattery2_1 sopra 12 V devono cambiare i nodi dei rami indicatori e il punto di lavoro del circuito.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "Vbattery2_1",
    "value": "DC 14V"
  }
]
```

## Scenario 3 - Alleggerire la polarizzazione della base di Q2 in alta tensione

- Scenario id: `scenario_3`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_3`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchB\experiment5\chat\b03\scenarios\scenario_3`

### Hypothesis

A 14 V il LED giallo Dled12_2 resta acceso perché Qnpn_transistor18_2 continua a ricevere sufficiente polarizzazione di base tramite Rresistor22_4 e il nodo N005.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "Vbattery2_1",
    "value": "DC 14V"
  },
  {
    "type": "change_component_value",
    "target": "Rresistor22_4",
    "value": "10k"
  }
]
```

## Scenario 4 - Spingere la batteria ben oltre 14 V

- Scenario id: `scenario_4`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_4`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchB\experiment5\chat\b03\scenarios\scenario_4`

### Hypothesis

Se la soglia di commutazione alta del circuito è superiore a 14 V, portando Vbattery2_1 a 16 V devono cambiare i nodi dei rami indicatori ad alta tensione e il punto di lavoro del circuito.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "Vbattery2_1",
    "value": "DC 16V"
  }
]
```

## Scenario 5 - Far salire lentamente la batteria da scarica a molto carica

- Scenario id: `scenario_5`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_5`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchB\experiment5\chat\b03\scenarios\scenario_5`

### Hypothesis

Se gli indicatori dipendono dalla tensione della batteria, una salita lenta di Vbattery2_1 deve produrre transizioni temporali osservabili sui nodi dei tre rami LED e sulla corrente della sorgente.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "Vbattery2_1",
    "value": "PWL(0s 10V 3s 16V)"
  }
]
```
