# <circuit> - Experiment 2

## Structured experiment record

```yaml
experiment_id: experiment2
batch: batchA
circuit: <circuit>
status: not_started
included: true
excluded_reason: null
base_reference: ../experiment1/<circuit>.md
primary_primitive: null
secondary_primitives: []
first_user_prompt: null
topological_scenario_proposed_in_first_response: null
topological_scenarios_count_first_response: null
proposed_scenarios_count_first_response: null
executed_scenarios_count: 0
topological_scenarios_executed_count: 0
best_outcome_status: not_tested
best_scenario_id: null
needs_image: null
notes_for_results: ""
```

## Riferimento base

- Base ufficiale Experiment 1: `../experiment1/<circuit>.md`
- Output runtime Experiment 2: `../../../../outputs/pipeline2.0/batchA/experiment2/<circuit>/`

## Obiettivo locale di Experiment 2

Descrivere in una frase:

- quale ipotesi topologica vogliamo testare;
- perche questo circuito e utile;
- quale primitiva e il focus principale.

## Prompt iniziale usato in chat

```text
<incollare qui il prompt utente iniziale>
```

## Prima risposta dell'agente

Descrivere in modo sintetico:

- cosa ha capito del sintomo;
- quali indizi ha usato;
- se ha gia introdotto o no una ipotesi topologica;
- se la prima risposta e convincente oppure no.

## Stato del contesto prima dei test

- Base run di riferimento:
- Prompt allineato: si/no
- History/registry attivi: si/no
- Note preliminari:

## Scenari proposti nella prima risposta

| Scenario | Titolo | Action types | Famiglia | Topologico | Eseguibile | Nota |
| --- | --- | --- | --- | --- | --- | --- |
| 1 |  |  |  |  |  |  |
| 2 |  |  |  |  |  |  |
| 3 |  |  |  |  |  |  |

## Scenari eseguiti

| Scenario | Actions | Outcome | Evidenza chiave | Utile per il passo successivo | Note |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |

## Cronologia domanda/risposta

Per mantenere lo stile di Experiment 1, conviene documentare i passaggi davvero
significativi in ordine temporale:

### Domanda 1

```text
<domanda utente>
```

### Risposta 1

- sintesi libera della risposta;
- eventuali scenari proposti;
- valutazione sintetica.

### Domanda 2

```text
<domanda utente successiva>
```

### Risposta 2

- sintesi libera della risposta;
- eventuale nuovo scenario o scenario combinato;
- perche e interessante per Experiment 2.

Ripetere solo per i passaggi che spostano davvero l'analisi in avanti.

## Cosa abbiamo imparato

### Sul comportamento dell'agente

- 

### Sulla primitiva in test

- 

### Sul circuito

- 

## Conclusione locale

Scrivere una conclusione breve ma confrontabile:

- il circuito richiedeva o no uno scenario topologico;
- la primitiva testata e stata utile oppure no;
- quale limite resta aperto.

## Artefatti da citare

```text
10_diagnostic_context.json
11_agent_prompt_chat.md
11_agent_response_chat.md
experiment2_chat/chat_history.md
experiment2_chat/scenario_registry.md
scenarios/<scenario_id>/
```

## Prossimo passo

- 
