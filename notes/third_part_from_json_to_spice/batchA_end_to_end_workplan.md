# Batch A end-to-end workplan

Questo documento definisce il piano operativo deciso dopo il confronto con il
tutor.

L'obiettivo non e completare subito tutti i batch, ma costruire una demo solida
e difendibile su tutto Batch A, arrivando dalla Pipeline 2.0 fino a SPICE,
agente, scenari controllati e webapp.

## Obiettivo

Portare tutti i circuiti di Batch A attraverso una pipeline unica:

```text
Graph JSON
-> Pipeline 2.0
-> netlist SPICE
-> ngspice
-> sintesi SPICE
-> contesto diagnostico
-> agente AI
-> scenari controllati
-> webapp
```

La pipeline deve restare generale. Anche se il lavoro parte da Batch A, gli
script non devono essere scritti in modo specifico per `a01`, `a02`, `a10` o per
un singolo circuito.

## Cosa significa "funziona"

Non tutti i circuiti devono essere simulabili allo stesso livello.

Per ogni circuito Batch A vogliamo arrivare a uno stato chiaro:

```text
READY
```

Il circuito ha valori e modelli sufficienti, la netlist viene generata e ngspice
produce risultati utili.

```text
PARTIAL
```

Il circuito attraversa la pipeline, ma alcuni componenti sono semplificati,
saltati o non supportati. La simulazione puo essere parziale oppure utile solo
per alcune parti del circuito.

```text
NOT_READY
```

Il circuito non e ancora simulabile in modo utile, ma la pipeline produce un
motivo esplicito: valori mancanti, modelli mancanti, componente non supportato,
topologia incompleta o altro limite.

Quindi "funziona" non significa simulazione perfetta. Significa:

```text
stessa pipeline per tutti i circuiti
output sempre prodotti
stato sempre dichiarato
limiti sempre espliciti
```

## Fase 1 - Batch A fino a 08

Prima priorita: completare Batch A fino a SPICE.

Per ogni circuito Batch A:

```text
a01
a02
a03
a04
a05
a06
a07
a08
a09
a10
```

servono:

- Graph JSON gia prodotto dalla Pipeline 1.0;
- file `values.yaml` manuale quando necessario;
- output da `01_io.py` a `08_spice_run.py`;
- controllo del risultato ngspice;
- classificazione provvisoria READY / PARTIAL / NOT_READY.

Output attesi:

```text
01_graph.json
02_normalized_circuit.json
03_node_map.json
04_values_bound.json
06_component_rules.json
07_netlist.cir
07_spice_emit_report.json
08_spice_run.json
08_ngspice_stdout.txt
08_ngspice_stderr.txt
```

Questa fase serve a capire quali problemi reali compaiono nel Batch A prima di
sviluppare agente e webapp.

## Fase 2 - 09_summarize_spice.py

Implementare uno step minimale che riassume i risultati grezzi di SPICE.

Input principali:

```text
07_spice_emit_report.json
08_spice_run.json
08_ngspice_stdout.txt
08_ngspice_stderr.txt
06_component_rules.json
```

Output:

```text
09_spice_summary.json
```

Contenuti minimi:

- ngspice eseguito: si/no;
- stato: success, failed, timeout, ngspice_not_found, netlist_not_found;
- exit code;
- stderr presente: si/no;
- warning principali;
- componenti non emessi;
- componenti non supportati;
- switch aperti;
- riferimenti ai file stdout/stderr.

Questo step non deve fare diagnosi complessa. Deve solo rendere gli output di
SPICE piu leggibili e standardizzati.

## Fase 3 - 10_build_diagnostic_context.py

Costruire il pacchetto tecnico che verra dato all'agente.

Input principali:

```text
01_graph.json
02_normalized_circuit.json
03_node_map.json
04_values_bound.json
06_component_rules.json
07_netlist.cir
07_spice_emit_report.json
08_spice_run.json
09_spice_summary.json
immagine originale
```

Output:

```text
10_diagnostic_context.json
```

Contenuti minimi:

- stato del circuito;
- path immagine;
- componenti principali;
- node map sintetica;
- valori e assunzioni;
- componenti emessi, semplificati, saltati o non supportati;
- netlist SPICE;
- esito ngspice;
- sintesi stdout/stderr;
- limiti noti;
- possibili domande diagnostiche.

Questo file e il ponte tra pipeline tecnica e agente AI.

## Fase 4 - 11_agent_readonly.py

Implementare la prima versione dell'agente in sola lettura.

Input:

```text
10_diagnostic_context.json
domanda utente
```

Output:

```text
11_agent_response.md
```

Responsabilita:

- leggere il contesto diagnostico;
- leggere il problema o la domanda dell'utente;
- costruire un prompt controllato;
- chiamare il modello AI;
- rispondere distinguendo fatti, risultati SPICE, assunzioni e ipotesi;
- salvare la risposta.

In questa fase l'agente non deve:

- modificare `values.yaml`;
- modificare la netlist;
- rieseguire ngspice;
- creare scenari;
- agire in autonomia sui file.

Questa e la prima demo utile dell'agente.

## Fase 5 - 12_controlled_scenarios.py

Aggiungere scenari simulativi controllati.

Gli scenari servono a verificare ipotesi diagnostiche, non a cambiare il
circuito base.

Regola:

```text
base circuit != scenario circuit
```

Azioni iniziali da supportare:

```text
drive_node_voltage
close_switch
open_switch
change_source_value
```

Azioni successive possibili:

```text
add_pullup
add_pulldown
change_load_value
```

Output possibili:

```text
12_controlled_scenarios.json
scenario_<id>_netlist.cir
scenario_<id>_spice_run.json
scenario_<id>_comparison.json
```

L'agente puo proporre uno scenario, ma la pipeline deve validarlo e tradurlo in
SPICE in modo riproducibile.

## Fase 6 - Webapp

La webapp deve essere uno strumento operativo, non una landing page.

Prima versione minima:

- lista circuiti Batch A;
- stato READY / PARTIAL / NOT_READY;
- immagine originale;
- netlist SPICE;
- stdout/stderr ngspice;
- sintesi SPICE;
- contesto diagnostico;
- domanda all'agente;
- risposta agente;
- eventuali scenari disponibili.

Layout concettuale:

```text
-------------------------------------------------------------
| Circuiti Batch A | Immagine / Netlist / Report | Chat AI   |
-------------------------------------------------------------
| Stato circuito   | SPICE stdout/stderr         | Scenari   |
-------------------------------------------------------------
```

La webapp deve leggere gli output prodotti dalla pipeline, non duplicare la
logica degli script.

## Ordine di lavoro consigliato

Ordine pratico:

```text
1. completare Batch A fino a 08
2. implementare 09_summarize_spice.py
3. implementare 10_build_diagnostic_context.py
4. implementare 11_agent_readonly.py
5. implementare 12_controlled_scenarios.py
6. creare webapp minima
7. migliorare scenari e interazione
```

## Cosa non fare per ora

Per mantenere il progetto gestibile:

- non passare subito a tutti i batch;
- non costruire subito un agente completamente autonomo;
- non permettere all'agente di modificare liberamente la netlist;
- non implementare scenari troppo complessi;
- non costruire una webapp grande prima di avere output stabili;
- non cercare simulazione perfetta per ogni circuito.

## Sintesi

Il lavoro immediato e:

```text
rendere Batch A attraversabile end-to-end
```

Poi:

```text
usare gli output SPICE per costruire il contesto dell'agente
```

Infine:

```text
rendere tutto interrogabile tramite agente e webapp
```

La tesi diventa cosi piu chiara: non solo riconoscimento topologico, ma una
pipeline completa che arriva a simulazione, diagnosi assistita e interazione con
l'utente.
