# Pipeline 2.0 scenario registry

- Batch: `batchDemo`
- Experiment: `demo_batch`
- Circuit: `a04`
- Max executable scenarios: `5`
- Created at: `2026-07-22T09:59:04`
- Updated at: `2026-07-22T10:03:07`

## Scenario 1 - Alleggerire il carico su VOUT

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `outputs\demo_workspaces\demo_batch\web\chat\a04\scenarios\scenario_1`

### Hypothesis

Il segnale a VOUT è troppo debole perché il ramo di uscita con Rresistor22_5 carica troppo il nodo N006.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_5",
    "value": "100k"
  }
]
```

## Scenario 2 - Ridurre la resistenza di bias verso la base

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

Il transistor conduce, ma il bias della base potrebbe non essere ottimale per ottenere una escursione utile del segnale in uscita.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_2",
    "value": "10k"
  }
]
```

## Scenario 3 - Aumentare moderatamente VIN e misurare il guadagno verso VOUT

- Scenario id: `scenario_3`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\demo_batch\web\chat\a04\scenarios\scenario_3`

### Hypothesis

L'uscita sembra debole soprattutto perche la sorgente Vsignal_source23_1 ha ampiezza di soli 10 mV; aumentando moderatamente VIN, il rapporto Vpp tra N006 e N002 chiarira se il trasferimento utile e limitato dall'ingresso troppo piccolo.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "Vsignal_source23_1",
    "value": "SIN(0 0.05 100)"
  }
]
```
