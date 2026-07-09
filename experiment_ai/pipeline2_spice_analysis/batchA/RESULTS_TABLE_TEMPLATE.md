# Batch A - Results Table Template

Questa e la tabella definitiva minima da usare per confrontare
`experiment1` e le diverse varianti reali di `experiment2` in modo semplice,
leggibile e riusabile anche per grafici futuri.

L'idea aggiornata e:

- una riga = una coppia `(circuito, variante sperimentale)`
- pochi campi stabili
- valori facili da capire anche per chi legge la tesi
- nessuna variante realmente eseguita di `experiment2` resta nascosta come
  "sottofase"

## Colonne scelte

| Colonna | Significato |
| --- | --- |
| `batch` | batch di riferimento |
| `circuit_id` | circuito (`a01`, `a02`, ...) |
| `experiment_id` | identificatore della variante sperimentale realmente documentata |
| `base_spice_status` | stato della base run SPICE |
| `scenario_count` | numero di scenari eseguiti davvero |
| `topological_scenarios_used` | se sono stati usati scenari topologici |
| `final_diagnosis_category` | esito finale sintetico del caso |
| `final_diagnosis_quality` | qualita complessiva della diagnosi finale |
| `notes_short` | nota breve, una sola riga |

## Valori ammessi consigliati

### `experiment_id`

```text
experiment1
experiment2
experiment2_connect_nodes
experiment2_feed_nodes_from_source_node
experiment2_add_voltage_source_between_nodes
experiment2_add_resistor_between_nodes
```

Nota:

- usare `experiment2` come placeholder solo quando la variante non e ancora
  stata decisa o il caso non e ancora stato eseguito;
- quando una variante specifica esiste davvero, conviene esplicitarla gia nella
  tabella principale.

### `base_spice_status`

```text
success
success_with_warnings
failed
not_started
excluded
```

### `topological_scenarios_used`

```text
yes
no
excluded
not_started
```

### `final_diagnosis_category`

```text
resolved
localized
topology_issue
inconclusive
excluded
not_started
```

### `final_diagnosis_quality`

```text
high
medium
low
not_applicable
```

## Tabella da compilare

| batch | circuit_id | experiment_id | base_spice_status | scenario_count | topological_scenarios_used | final_diagnosis_category | final_diagnosis_quality | notes_short |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| batchA | a01 | experiment1 | success | 1 | no | resolved | high | ramo lampada non pilotato nella base run |
| batchA | a01 | experiment2_connect_nodes | success | 2 | yes | resolved | high | connect_nodes N001-N002 conferma la continuita mancante verso la lampada |
| batchA | a01 | experiment2_feed_nodes_from_source_node | success | 1 | yes | resolved | high | propagazione N001-N002 attiva il ramo lampada |
| batchA | a02 | experiment1 | success_with_warnings | 4 | no | topology_issue | medium | batteria presente ma senza continuita utile verso il ramo resistivo |
| batchA | a02 | experiment2_connect_nodes | success_with_warnings | 2 | yes | resolved | high | continuita N002-N004 confermata con connect_nodes |
| batchA | a03 | experiment1 | failed | 0 | no | topology_issue | medium | netlist best-effort non simulabile per nodi flottanti e componenti mancanti |
| batchA | a03 | experiment2 | failed | 0 | excluded | excluded | not_applicable | escluso per ora da Experiment 2 per complessita topologica e image-assisted |
| batchA | a04 | experiment1 | success | 1 | no | resolved | high | uscita debole spiegata soprattutto da sorgente di ingresso troppo piccola |
| batchA | a04 | experiment2 | not_started | 0 | not_started | not_started | not_applicable | Experiment 2 non ancora eseguito su questo circuito |
| batchA | a05 | experiment1 | success_with_warnings | 2 | no | resolved | high | VMON a 0 V per assenza di pilotaggio su VMON_INPUT |
| batchA | a05 | experiment2_add_voltage_source_between_nodes | success_with_warnings | 2 | no | resolved | high | sorgente aggiunta su N003 conferma mancanza di eccitazione del circuito |
| batchA | a06 | experiment1 | success | 5 | no | localized | high | root cause localizzata sulla base N002 e sulla rete di bias/pilotaggio |
| batchA | a06 | experiment2 | not_started | 0 | not_started | not_started | not_applicable | Experiment 2 non ancora eseguito su questo circuito |
| batchA | a07 | experiment1 | success | 3 | no | resolved | high | circuito simulabile ma senza vera eccitazione su PWR e AC_INPUT |
| batchA | a07 | experiment2_add_voltage_source_between_nodes | success | 2 | no | resolved | high | sorgenti aggiunte su N002 e N001 confermano i due rami di ingresso |
| batchA | a08 | experiment1 | success | 3 | no | localized | high | il mancato lampeggio dipende dall'interazione tra sorgente e temporizzazione RC |
| batchA | a08 | experiment2_add_resistor_between_nodes | success | 5 | yes | localized | high | add_resistor_between_nodes rafforza la diagnosi sul ramo TRIGGER-base senza chiudere il caso |
| batchA | a09 | experiment1 | success_with_warnings | 4 | no | resolved | high | batteria e fusibile alimentano N003 ma i rami finali restano non pilotati |
| batchA | a09 | experiment2_connect_nodes | success_with_warnings | 3 | yes | resolved | high | connect_nodes conferma il trasferimento mancante verso lampada e LED |
| batchA | a09 | experiment2_feed_nodes_from_source_node | success_with_warnings | 4 | yes | resolved | high | feed_nodes propaga N003 verso i due rami e conferma LED e lampada |
| batchA | a10 | experiment1 | success | 3 | no | resolved | high | lo switch porta 5 V a N002 ma non ai rami finali LED e lampada |
| batchA | a10 | experiment2_connect_nodes | success | 4 | yes | resolved | high | connect_nodes self-contained da N002 conferma il trasferimento mancante verso N003 e N004 |
| batchA | a10 | experiment2_feed_nodes_from_source_node | success | 3 | yes | resolved | high | feed_nodes da N002 valida lampada e LED come rami sani ma non alimentati |

## Nota metodologica

Questa tabella non sostituisce i markdown dettagliati dei circuiti.

Serve invece a trasformare i risultati qualitativi in una forma minima comune
con cui poi possiamo:

- confrontare `experiment1` vs varianti reali di `experiment2`
- contare quanti casi sono `resolved`, `localized` o `topology_issue`
- vedere in quanti casi servono davvero scenari topologici
- confrontare primitive diverse senza nascondere quelle successive dentro note
  secondarie
- costruire grafici semplici senza perdere il significato dei casi
