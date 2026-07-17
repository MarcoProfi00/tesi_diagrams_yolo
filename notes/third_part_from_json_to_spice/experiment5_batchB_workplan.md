# Experiment 5 — Batch B: ordine operativo delle immagini

Questa nota fissa l'ordine iniziale di lavoro per estendere la Pipeline 2.0 al
Batch B. Non costituisce ancora una modifica alla pipeline, ai Graph JSON o
alle netlist.

## Principio di validazione

Prima dell'inserimento dei valori manuali e della generazione SPICE, il Graph
JSON di ogni circuito deve corrispondere all'immagine a un livello
elettricamente affidabile:

- componenti essenziali e loro classe;
- terminali, polarita e pin funzionali;
- nodi elettrici, massa, alimentazioni e collegamenti;
- carichi e rami che influenzano la simulazione.

La fonte di verifica gia disponibile e:

```text
experiment_ai/verify_json_img/batchB/output_gpt5_4/judge_report.md
```

Un Graph JSON non deve essere pixel-perfect, ma non puo essere usato per una
base run affidabile quando contiene errori topologici o semantici essenziali.
I valori manuali non correggono un graph errato.

## Ordine operativo

L'ordine combina fedelta immagine-graph, disponibilita di valori e livello di
supporto attuale della Pipeline 2.0.

1. `b02` — pilota: graph molto fedele, valori leggibili, classi gia supportate.
2. `b10` — graph molto fedele e classi supportate; richiede parametri manuali
   dichiarati, perche il diagramma e simbolico.
3. `b05` — graph buono e circuito discreto; utile per verificare ingresso
   antenna e componenti rappresentati solo parzialmente.
4. `b03` — graph ottimo, ma introduce PNP, zener e riferimento SPICE manuale.
5. `b04` — graph ottimo, ma introduce trasformatore, SCR e assenza di massa
   esplicita.
6. `b07` — primo caso MOS semplice, dopo una gestione generale dei modelli MOS.
7. `b09` — MOS con carico RC e soglie, con topologia molto fedele.
8. `b08` — MOS piu complesso, con collegamento VDD mancante nel graph.
9. `b01` — richiede correzione dei pin BJT e degli ingressi op-amp.
10. `b06` — ultimo: graph MEDIUM, massa/alimentazione fuse e LM386/carico
    incompleti.

## Regola per il prossimo passo

Il primo circuito da aprire e validare in dettaglio e `b02`. Solo dopo la
conferma immagine-graph verranno creati i valori manuali e la prima base run
SPICE nel workspace:

```text
outputs/pipeline2.0/batchB/experiment5/b02/
```

## Correzioni manuali convalidate

### b02 — polarita C2

Confrontando l'immagine originale e il Graph JSON finale, il condensatore
`polarized_capacitor20.2` (C2) aveva i terminali semantici invertiti. La
correzione nel Graph JSON finale della Pipeline 1.0 stabilisce:

```text
terminale sinistro, collegato alla base di Q1  -> negative
terminale destro, collegato al collettore di Q2 -> positive
```

La topologia non cambia. Per il condensatore ideale SPICE l'ordine dei nodi
non altera il comportamento simulato, ma la correzione rende coerenti Graph
JSON, node map e simbolo polarizzato del viewer.

## Schema comune di documentazione e valutazione

Per ogni circuito Batch B completato in Experiment 5 va creata una scheda in:

```text
experiment_ai/pipeline2_spice_analysis/batchB/experiment5/<circuito>.md
```

Il caso pilota e `b02.md`. La struttura deve rimanere confrontabile, ma non
deve forzare artificialmente gli stessi scenari o la stessa diagnosi. Sono
stabili soltanto i gruppi di evidenze:

1. record strutturato: batch, circuito, modello, sintomo, riferimenti e stato;
2. immagine/Graph JSON, valori manuali, netlist e comportamento della base run;
3. domanda comune o sintomo specifico del circuito;
4. confronto CHAT / AGENT: decisioni, scenari eseguiti, budget e stop;
5. evidenze SPICE e viewer, incluse aspettative temporali quando pertinenti;
6. conclusioni separate fra causa localizzata e correzione fisica verificata;
7. artefatti e campi pronti per tabelle, grafici e judge finale.

Possono invece variare liberamente per circuito:

- primitive scenario e parametri usati;
- numero e tipo di scenari utili;
- necessita di immagine o correzioni Graph JSON;
- diagnosi, limiti, tipo di analisi SPICE e metriche del viewer;
- esito finale: risolto, localizzato, inconclusivo o problema topologico.

La valutazione con judge non viene assegnata circuito per circuito durante
l'esecuzione. Dopo il completamento del Batch B, le schede Batch A verranno
riallineate allo stesso schema. Solo allora verranno congelati rubrica,
artefatti, modello e budget, poi si produrranno tabelle/grafici aggregati e il
judge confrontera tutte le coppie `circuito x modalita` (CHAT e AGENT).
