# Roadmap temporanea esperimenti Pipeline 2.0

Questo file e una nota temporanea di lavoro.

Serve a tenere fisso il percorso deciso dopo la chiusura dell'Esperimento 1 sul
Batch A. I dettagli tecnici completi restano nei markdown principali:

```text
notes/third_part_from_json_to_spice/agente_diagnostico_pipeline2.md
scripts/pipeline_2.0/WEB_CHAT_TEMP_PLAN.md
experiment_ai/pipeline2_spice_analysis/batchA/
```

## Esperimento 1 - Batch A baseline

Stato: concluso.

Obiettivo:

- eseguire Pipeline 2.0 sul Batch A;
- arrivare fino a ngspice;
- collegare web chat e agente;
- proporre ed eseguire scenari controllati manuali;
- documentare ogni circuito `a01`-`a10`.

Risultato:

- `a01`-`a10` sono documentati;
- gli output SPICE sono stati analizzati;
- la web chat funziona come interfaccia locale;
- l'agente read-only propone scenari;
- lo step `12_controlled_scenarios.py` esegue scenari separati dalla base run;
- i markdown del Batch A sono il riferimento manuale del comportamento atteso.

## Esperimento 2 - Scenari piu potenti

Stato: prossimo esperimento.

Obiettivo:

ampliare le primitive scenario in modo che l'agente possa proporre modifiche
piu forti e piu utili alla netlist SPICE, senza modificare mai la base run
originale.

Idea principale:

```text
ogni scenario produce una netlist alternativa, eseguibile e confrontabile
```

Possibili sviluppi:

- creare un piccolo file YAML o simile come catalogo delle primitive scenario;
- documentare per ogni primitiva:
  - nome;
  - descrizione;
  - parametri richiesti;
  - quando usarla;
  - come viene tradotta in netlist;
  - limiti e rischi;
- aggiungere primitive per modifiche piu strutturali.

Primitive gia presenti:

```text
drive_node_voltage
change_source_value
change_component_value
close_switch
```

Primitive candidate future:

```text
connect_nodes
disconnect_nodes
bridge_connector_pins
add_voltage_source
add_current_source
add_resistor
add_equivalent_load
add_ground_reference
replace_or_add_component_model
```

Esempi di scenari desiderati:

- chiudere uno switch e alimentare i pin collegati del connector;
- aggiungere una batteria se il circuito non ha una sorgente utile;
- aggiungere una sorgente di corrente;
- aggiungere una resistenza equivalente o un carico minimo;
- collegare due nodi solo nella run scenario;
- aggiungere un riferimento a massa quando manca una reference SPICE utile.

Regola fondamentale:

```text
la base run non si modifica mai
```

Ogni scenario deve creare:

```text
scenarios/<scenario_id>/base_snapshot/
scenarios/<scenario_id>/run/
scenarios/<scenario_id>/scenario.json
scenarios/<scenario_id>/12_controlled_scenarios.json
scenarios/<scenario_id>/scenario_comparison.json
```

## Esperimento 3 - Automazione agentica

Stato: futuro, dopo Esperimento 2.

Obiettivo:

far eseguire all'agente piu scenari in sequenza, entro un limite controllato,
per arrivare a una diagnosi finale o a una localizzazione del problema.

Flusso desiderato:

```text
sintomo utente
-> agente propone scenario
-> pipeline crea run scenario
-> pipeline esegue ngspice
-> pipeline crea scenario_comparison.json
-> agente legge il confronto
-> agente decide se fermarsi o proporre altro
-> massimo 5 scenari
-> conclusione finale
```

Regole:

- l'agente non modifica file direttamente;
- la pipeline valida sempre lo scenario;
- ogni scenario deve essere tracciabile;
- se uno scenario risolve o localizza abbastanza il problema, l'agente si ferma;
- se il budget finisce, l'agente produce una conclusione finale;
- se serve correggere il Graph JSON, l'agente deve dichiararlo esplicitamente.

## Esperimento 4 - Viewer / simulatore visuale

Stato: futuro, dopo scenari e automazione.

Obiettivo:

creare una visualizzazione stile simulatore, ispirata a strumenti come Falstad,
ma basata sui nostri output Pipeline 1.0 / Pipeline 2.0 e sui risultati ngspice.

Regola centrale:

```text
il viewer parte dalla netlist della run selezionata
```

Questo e importante perche:

- la base run ha una netlist;
- ogni scenario puo avere una netlist diversa;
- se uno scenario cambia topologia, anche il circuito visualizzato cambia;
- quindi il viewer non deve assumere una sola topologia fissa.

Dati utili:

```text
run/07_netlist.cir
run/08_ngspice_stdout.txt
run/08_tran.csv
run/08_tran_plot.png
03_node_map.json
coordinate/componenti da Pipeline 1.0
immagine originale del circuito
```

Prima versione possibile:

- mostrare immagine del circuito;
- sovrapporre marker su componenti e terminali;
- colorare nodi in base alla tensione;
- animare componenti o rami con corrente non nulla;
- mostrare differenze tra base run e scenario run.

## Valutazione trasversale degli esperimenti

Questa parte va ripresa quando avremo completato piu esperimenti.

Idea:

```text
usare una griglia comune di valutazione per tutti gli esperimenti
```

In questo modo possiamo confrontare Esperimento 1, 2, 3 e 4 in modo numerico,
non solo descrittivo.

### Perche serve

Senza metriche comuni rischiamo di avere solo tanti markdown qualitativi.

Con metriche comuni possiamo invece mostrare:

- se l'agente migliora davvero passando da scenari semplici a scenari piu
  potenti;
- se l'automazione aiuta o peggiora;
- quanti casi restano bloccati per problemi topologici;
- quanti scenari servono mediamente per arrivare a una conclusione;
- quali primitive scenario sono piu utili;
- quanto il viewer aiuta nella lettura dei risultati, quando verra introdotto.

### Griglia minima per ogni circuito

Per ogni circuito e per ogni esperimento dovremmo salvare almeno:

```text
batch
circuit_id
experiment_id
base_spice_status
base_spice_warning_count
graph_issue_detected
image_used_by_agent
agent_initial_diagnosis_quality
scenario_count
scenario_types_used
best_scenario_id
best_scenario_outcome
final_diagnosis_category
final_diagnosis_quality
human_notes
```

Possibili categorie per `final_diagnosis_category`:

```text
resolved
localized
partially_localized
topology_issue
not_enough_information
inconclusive
```

Possibili valori per `final_diagnosis_quality`:

```text
correct
mostly_correct
partially_correct
wrong
not_applicable
```

### Metriche aggregate possibili

Da questa griglia potremo calcolare:

- percentuale di circuiti SPICE success/fail;
- percentuale di diagnosi corrette o parzialmente corrette;
- percentuale di casi risolti, localizzati o inconclusivi;
- numero medio di scenari per circuito;
- numero di casi che richiedono immagine;
- distribuzione delle primitive scenario usate;
- confronto tra Esperimento 1, 2 e 3;
- casi migliorati grazie agli scenari topologici;
- casi migliorati grazie all'automazione;
- casi ancora bloccati dal Graph JSON.

### Grafici utili per la tesi

Possibili grafici finali:

- barre `success/fail` ngspice per esperimento;
- barre impilate con categorie finali:
  `resolved`, `localized`, `topology_issue`, `inconclusive`;
- istogramma del numero di scenari usati;
- confronto Esperimento 1 vs 2 vs 3 sul tasso di diagnosi utile;
- heatmap circuiti/primitive scenario;
- tabella riassuntiva per circuito;
- grafico sull'uso dell'immagine:
  `senza immagine`, `image-assisted`, `richiesta ma non sufficiente`.

### Regola metodologica

La valutazione finale va fatta dopo aver completato gli esperimenti, ma la
struttura dei dati va pensata prima.

Quindi:

```text
durante ogni esperimento salviamo dati confrontabili;
alla fine produciamo CSV/JSON aggregati;
poi generiamo grafici e conclusioni numeriche.
```

Questa parte sara fondamentale per la tesi, perche permette di mostrare non
solo che il sistema funziona in alcuni esempi, ma anche come cambia la qualita
della diagnosi quando aumentano le capacita dell'agente.

## Sintesi del percorso

```text
Esperimento 1 = baseline Batch A chiusa
Esperimento 2 = scenari piu potenti e netlist editing controllato
Esperimento 3 = agente che prova scenari in autonomia controllata
Esperimento 4 = viewer visuale basato sulla netlist della run selezionata
Valutazione = metriche comuni, CSV/JSON aggregati e grafici finali
```

Frase guida:

```text
Ogni scenario produce una netlist SPICE alternativa, eseguibile e confrontabile;
l'agente usa queste netlist per diagnosticare, mentre il viewer le usa per
visualizzare il comportamento elettrico.
```
