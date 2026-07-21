# Pipeline 2.0 scenario registry

- Batch: `batchDemo`
- Experiment: `demo_batch`
- Circuit: `b03`
- Max executable scenarios: `5`
- Created at: `2026-07-21T16:56:37`
- Updated at: `2026-07-21T17:08:25`

## Scenario 1 - Abbassare la tensione della batteria per simulare una batteria scarica

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\demo_batch\web\chat\b03\scenarios\scenario_1`

### Hypothesis

If the monitor distinguishes a discharged battery, lowering the existing source Vbattery2_1 from its nominal 12 V should change the LED-related branch conditions.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "Vbattery2_1",
    "value": "10V"
  }
]
```

## Scenario 2 - Alzare la tensione della batteria per simulare una batteria molto carica

- Scenario id: `scenario_2`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\demo_batch\web\chat\b03\scenarios\scenario_2`

### Hypothesis

If the monitor distinguishes a very highly charged battery, increasing Vbattery2_1 above the nominal 12 V should change the green LED branch conditions and may activate Dled12_3.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "Vbattery2_1",
    "value": "14V"
  }
]
```

## Scenario 3 - Ridurre il bias della base di Q2 a 14 V

- Scenario id: `scenario_3`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_3`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\demo_batch\web\chat\b03\scenarios\scenario_3`

### Hypothesis

At 14 V, Qnpn_transistor18_2 may remain active because its base path through Rresistor22_4 still provides enough drive; increasing Rresistor22_4 should weaken Q2 and reduce the yellow LED branch current.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "Vbattery2_1",
    "value": "14V"
  },
  {
    "type": "change_component_value",
    "target": "Rresistor22_4",
    "value": "33k"
  }
]
```

## Scenario 4 - Alzare ancora la batteria per vedere se il verde prevale davvero

- Scenario id: `scenario_4`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_4`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\demo_batch\web\chat\b03\scenarios\scenario_4`

### Hypothesis

Since scenario_2 at 14V already activated Dled12_3 while Dled12_2 stayed on, increasing Vbattery2_1 further to 16V can verify whether the circuit is still in a mixed yellow+green region or whether the green branch becomes dominant.

### Actions

```json
[
  {
    "type": "change_source_value",
    "target": "Vbattery2_1",
    "value": "16V"
  }
]
```
