# <circuit> - Experiment 1

## Structured experiment record

```yaml
experiment_id: experiment1
batch: batchA
circuit: <circuit>
status: not_started
included: true
excluded_reason: null
base_reference: null
runtime_experiment_root: ../../../../outputs/pipeline2.0/batchA/<circuit>/
additional_runtime_roots: []
primary_primitive: null
secondary_primitives: []
first_user_prompt: null
topological_scenario_proposed_in_first_response: false
topological_scenarios_count_first_response: 0
proposed_scenarios_count_first_response: 0
executed_scenarios_count: 0
topological_scenarios_executed_count: 0
best_outcome_status: not_tested
best_scenario_id: null
needs_image: null
notes_for_results: ""
```

## Riferimenti

- Runtime root Experiment 1:
  `../../../../outputs/pipeline2.0/batchA/<circuit>/`
- Immagine circuito:
  `../../../../data/batchA/<circuit>.png`
- Eventuali riferimenti successivi:
  `../experiment2/<circuit>.md`

## Obiettivo locale di Experiment 1

Descrivere in una frase:

- cosa vogliamo capire della base run;
- perche questo circuito e importante nel batch;
- quale famiglia di scenari non topologici o quale limite SPICE emerge.

## Contesto iniziale

- Base run di riferimento:
- Prompt allineato: si/no/non applicabile
- History/registry attivi: si/no/non applicabile
- Note preliminari:

## Domanda iniziale

### Domanda utente

```text
<sintomo iniziale usato nella chat, oppure "non applicabile" se il caso e solo tecnico>
```

## Valutazione della prima risposta

Descrivere in modo sintetico:

- cosa ha capito l'agente oppure cosa emerge dai risultati SPICE;
- quali evidenze sono state usate;
- se la prima lettura del caso e convincente;
- se emerge gia una direzione forte oppure no.

## Prima tripletta di scenari proposti

| Scenario | Titolo | Action types | Famiglia | Topologico | Eseguibile | Valutazione |
| --- | --- | --- | --- | --- | --- | --- |
| 1 |  |  |  | no |  |  |
| 2 |  |  |  | no |  |  |
| 3 |  |  |  | no |  |  |

## Scenari eseguiti

| Scenario | Actions | Outcome | Evidenza chiave | Valutazione |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## Cronologia domanda/risposta

Documentare solo i passaggi che spostano davvero in avanti l'analisi:

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
- eventuale scenario eseguito;
- perche e utile per chiudere il caso.

## Cosa abbiamo imparato

### Sul comportamento dell'agente

- 

### Sulla primitiva o famiglia di scenari

- 

### Sul circuito

- 

## Conclusione locale

Scrivere una conclusione breve ma confrontabile:

- il circuito richiedeva o no uno scenario topologico;
- la famiglia di scenari usata in Experiment 1 e stata utile oppure no;
- quale limite resta aperto.

## Artefatti da citare

```text
07_netlist.cir
07_spice_emit_report.json
08_spice_run.json
08_ngspice_stdout.txt
08_ngspice_stderr.txt
10_diagnostic_context.json
11_agent_prompt_chat.md
11_agent_response_chat.md
scenarios/<scenario_id>/
```

## Appendice tecnica opzionale

Qui possono vivere i dettagli piu specifici di Experiment 1:

- netlist completa;
- mappa nodi;
- stdout/stderr commentati;
- dettagli numerici della base run;
- note storiche o metodologiche.
