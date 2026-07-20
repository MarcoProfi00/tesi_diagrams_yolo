# Pipeline 2.0 scenario registry

- Batch: `batchB`
- Experiment: `experiment5`
- Circuit: `b04`
- Max executable scenarios: `5`
- Created at: `2026-07-20T12:53:19`
- Updated at: `2026-07-20T13:00:25`

## Scenario 1 - Batteria un po' più scarica e confronto della corrente in D4

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchB\experiment5\chat\b04\scenarios\scenario_1`

### Hypothesis

Riducendo la tensione della batteria di prova, D4 dovrebbe condurre di più durante parte del ciclo se il ramo di carica è effettivamente attivo verso la batteria.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "VVBAT_TEST",
    "value": "10V"
  }
]
```

## Scenario 2 - Ridurre R4 da 50 ohm a 33 ohm

- Scenario id: `scenario_2`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `outputs\pipeline2.0\batchB\experiment5\chat\b04\scenarios\scenario_2`

### Hypothesis

Una riduzione moderata del potenziometro equivalente R4 dovrebbe aumentare la corrente nel ramo di carica se R4 e un controllo efficace della corrente verso la batteria.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_5",
    "value": "33"
  }
]
```

## Scenario 3 - Ridurre R4 da 50 ohm a 22 ohm

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

Una riduzione piu marcata del potenziometro equivalente R4 dovrebbe produrre un aumento piu evidente della corrente di carica se R4 governa realmente quel ramo.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_5",
    "value": "22"
  }
]
```

## Scenario 4 - Aumentare R4 da 50 ohm a 68 ohm come controprova

- Scenario id: `scenario_4`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

Se R4 controlla la corrente verso la batteria, aumentare il suo equivalente rispetto alla base run dovrebbe ridurre la conduzione del ramo di carica.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_5",
    "value": "68"
  }
]
```
