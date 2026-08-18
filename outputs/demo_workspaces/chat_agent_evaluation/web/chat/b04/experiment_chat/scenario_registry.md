# Pipeline 2.0 scenario registry

- Batch: `batchChatAgentEvaluation`
- Experiment: `chat_agent_evaluation`
- Circuit: `b04`
- Max executable scenarios: `5`
- Created at: `2026-07-24T11:31:07`
- Updated at: `2026-07-24T11:35:44`

## Scenario 1 - Abbassare la tensione della batteria di prova

- Scenario id: `scenario_1`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `None`

### Hypothesis

If the battery is less charged, reducing VVBAT_TEST should change and possibly increase the magnitude of the battery-branch current.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "VVBAT_TEST",
    "value": "DC 10V"
  }
]
```

## Scenario 2 - Abbassare ulteriormente la tensione della batteria di prova

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `None`

### Hypothesis

A more discharged battery condition should produce a clearer current change in the battery branch if charging current depends on battery voltage.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "VVBAT_TEST",
    "value": "DC 8V"
  }
]
```

## Scenario 3 - Variare la regolazione equivalente di R4

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

The low battery-branch current may be set by the R4 equivalent adjustment rather than only by the battery voltage.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_5",
    "value": "20"
  }
]
```

## Scenario 4 - Abbassare la batteria di prova e osservare D4 nel tempo

- Scenario id: `scenario_4`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b04\scenarios\scenario_4`

### Hypothesis

Reducing VVBAT_TEST below the nominal 12 V changes the transient current through Ddiode7_4.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "VVBAT_TEST",
    "value": "DC 10V"
  }
]
```

## Scenario 5 - Portare la batteria di prova a un valore ancora piu basso

- Scenario id: `scenario_5`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `2`
- Execution path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b04\scenarios\scenario_5`

### Hypothesis

A lower VVBAT_TEST produces a different transient Ddiode7_4 current profile than the nominal case.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "VVBAT_TEST",
    "value": "DC 8V"
  }
]
```

## Scenario 6 - Cambiare il valore equivalente di R4 e osservare D4

- Scenario id: `scenario_6`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

The transient current through Ddiode7_4 may depend on the equivalent setting of Rresistor22_5.

### Actions

```json
[
  {
    "type": "change_component_value",
    "target": "Rresistor22_5",
    "value": "100"
  }
]
```

## Scenario 7 - Alzare la batteria di prova e vedere se D4 si riduce

- Scenario id: `scenario_7`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_3`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

If the observed branch current is linked to battery charging demand, increasing VVBAT_TEST above 12 V should alter the transient current through Ddiode7_4 in the opposite direction from the lower-battery test.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "VVBAT_TEST",
    "value": "DC 14V"
  }
]
```
