# Pipeline 2.0 scenario registry

- Batch: `batchChatAgentEvaluation`
- Experiment: `chat_agent_evaluation`
- Circuit: `a07`
- Max executable scenarios: `5`
- Created at: `2026-07-23T16:01:50`
- Updated at: `2026-07-23T16:04:50`

## Scenario 1 - Alimentare il nodo PWR dal connettore

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a07\scenarios\scenario_1`

### Hypothesis

Il LED di alimentazione e spento perche il nodo N002 etichettato PWR non e alimentato nel netlist base.

### Actions

```json
[
  {
    "type": "add_voltage_source_between_nodes",
    "positive": "N002",
    "negative": "0",
    "value": "5V"
  }
]
```

## Scenario 2 - Applicare un segnale AC all'ingresso VAC

- Scenario id: `scenario_2`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `2`
- Execution path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a07\scenarios\scenario_2`

### Hypothesis

Il voltmetro VAC non mostra nulla perche il nodo N001 non riceve alcun segnale nel netlist base.

### Actions

```json
[
  {
    "type": "add_voltage_source_between_nodes",
    "positive": "N001",
    "negative": "0",
    "value": "SIN(0 5 50)"
  }
]
```

## Scenario 3 - Chiudere lo switch RESET

- Scenario id: `scenario_3`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

Lo switch switch25.1 aperto potrebbe impedire una condizione necessaria al funzionamento del circuito estratto.

### Actions

```json
[
  {
    "type": "close_switch",
    "target": "switch25.1"
  }
]
```

## Scenario 4 - Alimentare PWR e pilotare VAC nella stessa simulazione

- Scenario id: `scenario_4`
- Status: `executed`
- Outcome: `resolved_candidate`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a07\scenarios\scenario_4`

### Hypothesis

Le due ipotesi gia confermate separatamente sono compatibili nella stessa run: 5 V DC su N002 deve mantenere corrente non nulla nel LED, mentre SIN(0 5 50) su N001 deve rendere variabile la tensione VAC.

### Actions

```json
[
  {
    "type": "add_voltage_source_between_nodes",
    "positive": "N002",
    "negative": "0",
    "value": "5V"
  },
  {
    "type": "add_voltage_source_between_nodes",
    "positive": "N001",
    "negative": "0",
    "value": "SIN(0 5 50)"
  }
]
```
