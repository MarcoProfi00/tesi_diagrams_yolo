# Pipeline 2.0 scenario registry

- Batch: `batchChatAgentEvaluation`
- Experiment: `chat_agent_evaluation`
- Circuit: `b06`
- Max executable scenarios: `5`
- Created at: `2026-07-24T16:44:40`
- Updated at: `2026-07-24T16:47:53`

## Scenario 1 - Iniettare un piccolo segnale audio all'ingresso dell'LM386

- Scenario id: `scenario_1`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b06\scenarios\scenario_1`

### Hypothesis

L'uscita silenziosa dipende dall'assenza di segnale su N010, non necessariamente da un guasto dell'uscita audio.

### Actions

```json
[
  {
    "type": "add_voltage_source_between_nodes",
    "positive": "N010",
    "negative": "0",
    "value": "SIN(0 5m 1000)"
  }
]
```

## Scenario 2 - Applicare una eccitazione esterna al nodo antenna

- Scenario id: `scenario_2`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_1`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

La simulazione base e silenziosa soprattutto perche il nodo antenna N001 non riceve alcuna eccitazione SPICE.

### Actions

```json
[
  {
    "type": "add_voltage_source_between_nodes",
    "positive": "N001",
    "negative": "0",
    "value": "SIN(0 10m 1000)"
  }
]
```

## Scenario 3 - Iniettare un piccolo segnale sul nodo di base del transistor

- Scenario id: `scenario_3`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `1`
- Execution path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b06\scenarios\scenario_3`

### Hypothesis

Il segnale potrebbe interrompersi tra N005, N006 e N010, cioe nello stadio a transistor o nel condensatore Cpolarized_capacitor20_4 verso l'LM386.

### Actions

```json
[
  {
    "type": "add_voltage_source_between_nodes",
    "positive": "N005",
    "negative": "0",
    "value": "SIN(0.660106 5m 1000)"
  }
]
```

## Scenario 4 - Iniettare un piccolo segnale sul nodo rivelato dopo il diodo

- Scenario id: `scenario_4`
- Status: `executed`
- Outcome: `partially_resolved`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `2`
- Execution path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b06\scenarios\scenario_4`

### Hypothesis

Il segnale potrebbe interrompersi tra N004 e N005, cioe tra il rivelatore e l'ingresso dello stadio a transistor.

### Actions

```json
[
  {
    "type": "add_voltage_source_between_nodes",
    "positive": "N004",
    "negative": "0",
    "value": "SIN(0 5m 1000)"
  }
]
```

## Scenario 5 - Iniettare un segnale di prova sul nodo antenna N001

- Scenario id: `scenario_5`
- Status: `proposed`
- Outcome: `None`
- Executable: `True`
- Kind: `spice_scenario`
- Source proposal: `proposal_2`
- Source local index: `3`
- Execution path: `None`

### Hypothesis

La base run potrebbe non produrre audio solo perche manca una reale eccitazione d'ingresso su N001, dato che antenna1.1 non e emessa nel netlist.

### Actions

```json
[
  {
    "type": "add_voltage_source_between_nodes",
    "positive": "N001",
    "negative": "0",
    "value": "SIN(0 5m 1000)"
  }
]
```
