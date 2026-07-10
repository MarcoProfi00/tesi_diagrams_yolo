# Experiment 3 - Viewer e simulatore visuale da netlist SPICE

Questo documento definisce la mappa di lavoro per l'Esperimento 3 della
Pipeline 2.0.

L'obiettivo non e implementare subito codice, ma fissare bene:

- cosa vogliamo costruire;
- perche ha senso rispetto allo stato dell'arte;
- quali dati della Pipeline 2.0 useremo;
- quali circuiti del Batch A rientrano nella prima fase;
- quali deliverable devono essere prodotti;
- quali limiti dichiarare nella tesi.

## Obiettivo dell'Esperimento 3

L'Esperimento 3 riguarda la creazione di un viewer/simulatore visuale a partire
dalla netlist SPICE prodotta dalla Pipeline 2.0.

L'idea e avere una visualizzazione nello stile di strumenti come Falstad /
CircuitJS:

- schema equivalente del circuito;
- nodi e rami leggibili;
- colori legati alle tensioni;
- indicazione qualitativa o quantitativa delle correnti;
- eventuali grafici temporali quando la run contiene una `.tran`;
- confronto tra base run e scenario run.

La regola centrale e:

```text
il viewer parte sempre dalla netlist della run selezionata
```

Questo significa che:

- la base run ha il proprio circuito equivalente;
- ogni scenario ha il proprio circuito equivalente;
- se uno scenario modifica la topologia, anche il viewer deve mostrare la
  topologia modificata;
- il viewer non deve assumere che esista una sola topologia fissa per circuito.

Decisione UI:

```text
ogni run selezionabile nella web chat deve avere uno spazio dedicato al viewer
```

Quindi il viewer non sara solo una pagina separata da aprire manualmente, ma un
blocco stabile della pagina centrale della web chat.

Quando l'utente seleziona:

```text
Base run
scenario_1
scenario_2
...
```

la pagina centrale deve mostrare anche il circuito equivalente della run
selezionata. Questo vale per tutti gli scenari, non solo per quelli che cambiano
esplicitamente la topologia.

Motivo:

- uno scenario puo cambiare la netlist aggiungendo rami, sorgenti o
  collegamenti;
- uno scenario puo anche non cambiare la topologia, ma cambiare valori, stato
  switch, sorgenti o risultati elettrici;
- in entrambi i casi il viewer deve rappresentare cio che ngspice ha simulato
  in quella specifica run;
- l'utente deve poter passare da base run a scenario run senza perdere il
  contesto visivo.

## Perimetro iniziale

Per adesso il perimetro e:

```text
Batch A: a01, a02, a04, a05, a06, a07, a08, a09, a10
```

Il circuito `a03` resta escluso per ora.

Motivo:

- `a03` e un caso speciale con graph/topologia fortemente incompleti;
- la netlist base fallisce in ngspice;
- richiede una fase successiva di correzione graph o ragionamento
  image-assisted;
- inserirlo subito rischierebbe di confondere l'obiettivo dell'Esperimento 3,
  che e visualizzare correttamente netlist gia emesse o scenari gia eseguiti.

## Posizionamento rispetto alla tesi

La Pipeline 2.0 e gia arrivata a:

```text
Graph JSON -> node map -> netlist SPICE -> ngspice -> diagnosi AI -> scenari
```

Experiment 3 aggiunge il livello:

```text
netlist SPICE + risultati ngspice -> viewer/simulatore visuale
```

Questa fase e importante perche rende visibile il comportamento elettrico che
finora leggiamo tramite file tecnici, chat diagnostica e markdown.

La tesi puo quindi sostenere una progressione chiara:

```text
Experiment 1 = diagnosi con scenari semplici
Experiment 2 = scenari piu potenti e modifiche controllate della netlist
Experiment 3 = visualizzazione/simulazione delle netlist base e scenario
Experiment 4 = automazione agentica degli scenari
```

## Stato dell'arte rilevante

### 1. Pipeline image-to-netlist

Lo stato dell'arte recente mostra che il problema immagine -> netlist e molto
attivo. Sistemi come SINA, Netlistify e Image2Net lavorano sul passaggio da
immagini di schematici a netlist SPICE/HSPICE/Spectre.

Il punto comune dei lavori piu solidi non e solo riconoscere i componenti, ma
separare la pipeline in blocchi:

- component detection;
- orientation / pin semantics;
- wire o net detection;
- node reconstruction;
- text/OCR extraction;
- netlist assembly;
- validazione strutturale della netlist.

Questo e coerente con la nostra impostazione, ma con una differenza importante:
noi non stiamo facendo una pipeline puramente image-first. Nel nostro caso
l'input operativo e gia un Graph JSON prodotto dalla Pipeline 1.0.

Quindi il contributo piu interessante diventa:

```text
graph JSON rumoroso -> circuito elettrico canonico -> netlist eseguibile
```

e non solo:

```text
immagine -> netlist
```

Questa scelta rende il sistema piu auditabile, perche ogni passaggio produce
artefatti leggibili e confrontabili.

Fonti utili per la tesi:

- SINA: `https://arxiv.org/html/2601.22114v1`
- Netlistify: `https://research.nvidia.com/labs/electronic-design-automation/papers/netlistify_mlcad25.pdf`
- Netlistify repository: `https://github.com/NYCU-AI-EDA/Netlistify`
- Image2Net: `https://arxiv.org/html/2508.13157v1`
- Circuit schematic image interpretation: `https://pubs.aip.org/aip/aml/article/2/1/016109/3132693/Digitizing-images-of-electrical-circuit-schematics`

### 2. SPICE come motore di verita numerica

Ngspice e il motore piu naturale per questa tesi, perche:

- e open source;
- usa netlist come input;
- supporta componenti passivi, diodi, transistor e circuiti mixed-signal;
- produce tensioni, correnti e risultati salvabili in file;
- non impone una interfaccia schematica proprietaria.

Questo e esattamente il ruolo che ci serve:

```text
ngspice = sorgente numerica della simulazione
viewer = rappresentazione visuale dei risultati ngspice
```

Il viewer non deve diventare un secondo simulatore indipendente che ricalcola
tutto da zero, perche questo aprirebbe il rischio di avere due verita diverse:
quella di ngspice e quella del viewer.

Fonte utile:

- ngspice: `https://ngspice.sourceforge.io/`

### 3. Viewer e simulatori interattivi esistenti

CircuitJS/Falstad e il riferimento visivo piu vicino a cio che vogliamo:

- gira nel browser;
- mostra il circuito in modo interattivo;
- visualizza correnti e tensioni in modo intuitivo;
- include grafici e oscilloscopi;
- e molto efficace didatticamente.

Pero va trattato con attenzione.

CircuitJS e un simulatore completo, non solo un viewer. Usarlo direttamente
come cuore dell'Esperimento 3 significherebbe introdurre un secondo motore di
simulazione, con modelli, formati e risultati potenzialmente diversi da
ngspice.

Inoltre il repository e GPL-2.0, quindi integrare direttamente codice nel
progetto richiederebbe attenzione di licenza.

Scelta consigliata:

```text
usare CircuitJS/Falstad come riferimento di UX, non come sorgente di verita
```

Possibili usi futuri:

- esportare un circuito in formato CircuitJS solo come prototipo o confronto;
- aprire CircuitJS con un circuito equivalente semplificato;
- usare la sua interfaccia come ispirazione per colori, animazioni e scope.

Fonti utili:

- CircuitJS app: `https://lushprojects.com/circuitjs/circuitjs.html`
- CircuitJS repository: `https://github.com/pfalstad/circuitjs1`

### 4. Schematic drawing e netlist-to-schematic

Altri strumenti utili non sono simulatori completi, ma aiutano a disegnare o
ricostruire schematici:

- Schemdraw genera schematici puliti da Python;
- Lcapy puo lavorare su netlist e produrre rappresentazioni circuitali;
- alcuni progetti sperimentali fanno netlist-to-schematic automatico;
- Weave propone una conversione deterministica da netlist a schematico LTspice
  con verifica di equivalenza topologica.

Per la nostra tesi questi strumenti sono utili come confronto metodologico, ma
non risolvono da soli tutto il problema.

Il problema vero non e solo disegnare un circuito bello, ma costruire un viewer
che mantenga:

- equivalenza topologica con la netlist scelta;
- collegamento ai risultati ngspice;
- tracciabilita verso base run o scenario run;
- possibilita di confronto tra esperimenti.

Fonti utili:

- Schemdraw: `https://schemdraw.readthedocs.io/en/latest/`
- Lcapy: `https://lcapy.readthedocs.io/en/latest/`
- Weave: `https://arxiv.org/abs/2607.03835`

### 5. AI diagnosis grounded su simulazione

I lavori recenti su SPICE + AI indicano una direzione chiara: l'agente e piu
affidabile quando ragiona su struttura e risultati simulativi, non quando deve
indovinare da testo libero.

Per la nostra pipeline questo significa:

```text
agente = legge graph, netlist, warning, risultati SPICE, scenari e viewer
```

Il viewer puo quindi diventare anche uno strumento per:

- spiegare meglio la diagnosi;
- far vedere perche uno scenario e utile;
- confrontare base e scenario;
- rendere piu leggibili le differenze topologiche.

Fonti utili:

- Auto-SPICE / Masala-CHAI: `https://arxiv.org/html/2411.14299v1`
- SPICEAssistant: `https://arxiv.org/html/2507.10639v1`
- AMSnet-q: `https://arxiv.org/html/2605.01404v1`

## Decisione architetturale

La scelta piu solida per Experiment 3 e:

```text
viewer nativo leggero, alimentato da netlist e risultati ngspice
```

Non vogliamo ricreare Falstad.

Vogliamo costruire una versione tesi-friendly:

- piu piccola;
- controllabile;
- leggibile nei file;
- coerente con la Pipeline 2.0;
- generale per batch futuri;
- capace di visualizzare sia base run sia scenario run.

Schema:

```text
run selezionata
  |
  |-- 07_netlist.cir
  |-- 08_ngspice_stdout.txt
  |-- 08_tran.csv
  |-- 03_node_map.json
  |-- 04_values_bound.json
  |-- scenario.json              # solo per scenario run
  |-- scenario_comparison.json   # solo per scenario run
  |
  v
13_build_viewer_model.py
  |
  v
13_viewer_model.json
  |
  v
14_viewer.html / viewer web panel
```

Il cuore non deve essere HTML/CSS, ma il modello intermedio:

```text
13_viewer_model.json
```

Questo file deve diventare l'oggetto confrontabile e testabile.

## Decisione architetturale aggiornata: niente renderer hardcoded per circuito

Il prototipo costruito su `a01` serve solo come riferimento visivo e come
prima grammatica grafica dei componenti.

Non deve diventare il modello finale.

In particolare, non vogliamo introdurre funzioni del tipo:

```text
render_a01_viewer_svg
render_a02_viewer_svg
render_a09_viewer_svg
...
```

perche i circuiti del Batch A e dei batch futuri hanno topologie diverse e
anche gli scenari possono modificare la netlist.

La regola da fissare e:

```text
per ogni circuito e per ogni scenario, il viewer deve essere generato dalla run
selezionata, non scritto a mano per quel circuito.
```

Quindi il lavoro fatto manualmente su `a01` va trasformato in una pipeline
automatica:

```text
07_netlist.cir + 03_node_map.json + 06_component_rules.json + risultati 08
  -> 13_viewer_model.json
  -> 14_viewer_layout.json
  -> renderer SVG/HTML generico
```

`09_web_chat.py` non deve contenere a regime la logica specifica del circuito.
Deve limitarsi a caricare e mostrare il viewer della run attiva:

- base run: viewer della root del circuito;
- scenario run: viewer della cartella `scenarios/<scenario_id>/run/`.

Il renderer generale deve applicare regole riusabili:

- disegnare i connector verticali con numero di pin dinamico;
- disegnare componenti SPICE sui rami della netlist;
- aggiungere i componenti strutturali utili da `03_node_map.json`;
- mostrare switch aperti/chiusi in base al modello della run;
- mostrare componenti aggiunti dagli scenari;
- usare tensioni e correnti ngspice come overlay informativo;
- mantenere un layout leggibile anche quando la topologia cambia.

Questa decisione evita di costruire un viewer "per a01" e sposta il lavoro
verso un motore generale incrementale: ogni nuovo circuito serve a migliorare
le regole di modello, layout e rendering, non ad aggiungere codice duplicato.

## Integrazione nella web chat

La web chat oggi presenta:

- colonna sinistra con `Base run` e scenari;
- pagina centrale con riepilogo tecnico, immagine originale e artefatti;
- colonna destra con chat diagnostica.

Experiment 3 deve aggiungere un nuovo blocco nella pagina centrale, idealmente
sotto l'immagine originale:

```text
Circuit Image
Circuito equivalente / simulatore
Artefatti tecnici SPICE
```

Il titolo del blocco deve essere metodologicamente chiaro:

```text
Circuito equivalente dalla netlist SPICE
```

oppure:

```text
Simulatore equivalente della run selezionata
```

Da evitare:

```text
Schema ricostruito originale
```

perche il viewer non promette di ricostruire lo schema grafico originale, ma
una rappresentazione equivalente alla netlist simulata.

### Base run

Per la base run, gli output viewer stanno nella root del circuito:

```text
outputs/pipeline2.0/<batch>/<experiment>/<circuit>/
  13_viewer_model.json
  14_viewer.html
```

Esempio:

```text
outputs/pipeline2.0/batchA/experiment2/a08/
  13_viewer_model.json
  14_viewer.html
```

### Scenario run

Per una scenario run, gli output viewer stanno nella cartella `run/` dello
scenario, accanto alla netlist effettivamente simulata:

```text
outputs/pipeline2.0/<batch>/<experiment>/<circuit>/scenarios/<scenario_id>/run/
  07_netlist.cir
  08_ngspice_stdout.txt
  13_viewer_model.json
  14_viewer.html
```

Esempio:

```text
outputs/pipeline2.0/batchA/experiment2/a08/scenarios/scenario_4/run/
  13_viewer_model.json
  14_viewer.html
```

Questa scelta e importante perche evita ambiguita:

```text
viewer della run = stesso posto della netlist della run
```

### Regola generale

Il viewer va generato per:

- base run;
- scenari topologici;
- scenari non topologici;
- scenari che cambiano solo valori;
- scenari che chiudono switch;
- scenari che aggiungono sorgenti;
- scenari con `.op`;
- scenari con `.tran`.

La distinzione tra scenario topologico e non topologico resta nei metadati, ma
non cambia la presenza del viewer.

### Rendering nella pagina

Ci sono due modi possibili:

1. generare `14_viewer.html` e inserirlo nella pagina come contenuto separato;
2. far leggere a `09_web_chat.py` il file `13_viewer_model.json` e renderizzare
   direttamente il blocco viewer dentro la pagina.

La seconda strada e preferibile a regime, perche mantiene il viewer integrato
nella UI della chat.

La prima strada puo essere utile per prototipo, debug e documentazione.

Quindi:

```text
13_viewer_model.json = contratto dati ufficiale
14_viewer.html = vista locale/prototipo/debug
web chat = integrazione finale del viewer
```

## Contratto dati del viewer

Una prima versione di `13_viewer_model.json` dovrebbe contenere:

```text
metadata
nodes
components
edges
measurements
time_series
layout
scenario
warnings
```

### metadata

Informazioni minime:

```text
batch
circuit_id
experiment
run_type: base | scenario
scenario_id
source_netlist_path
source_spice_stdout_path
source_tran_csv_path
generated_at
```

### nodes

Per ogni nodo:

```text
id
label
is_ground
voltage_op
aliases
members_from_node_map
```

### components

Per ogni componente emesso in netlist:

```text
id
kind
spice_name
nodes
value
model
is_scenario_added
source_line
```

Esempi di `kind`:

```text
resistor
capacitor
inductor
voltage_source
current_source
diode
led
lamp_equivalent
bjt
switch_equivalent
scenario_wire
unknown
```

### edges

Per la visualizzazione grafica:

```text
component_id
from_node
to_node
branch_current_op
```

Per componenti a piu terminali, come transistor, la prima versione puo usare
una rappresentazione semplificata:

```text
component_id
pins: collector/base/emitter oppure generic pin list
```

### measurements

Valori derivati da ngspice:

```text
node_voltages
branch_currents
component_estimates
spice_status
```

### time_series

Solo per circuiti con `.tran`:

```text
signals
time_column
csv_path
plot_path
```

### layout

Per la prima versione:

```text
node_positions
component_positions
wire_segments
layout_status
```

Il layout puo essere semplice e automatico. Non deve replicare la posizione
fisica dell'immagine originale.

### scenario

Solo per scenario run:

```text
scenario_id
scenario_type_list
scenario_actions
topology_changed
comparison_summary
```

## Strategia di layout

La ricostruzione automatica di uno schematico bello da una netlist e un problema
difficile. Non va sottovalutato.

Per questo la prima versione deve puntare a:

```text
correttezza topologica prima della bellezza grafica
```

Possibile strategia:

1. parsare la netlist;
2. costruire un grafo bipartito nodo-componente;
3. individuare nodi importanti:
   - ground;
   - alimentazioni;
   - nodi con molte connessioni;
   - nodi scenario-added;
4. assegnare posizioni su griglia;
5. disegnare componenti come blocchi/simboli tra nodi;
6. disegnare fili ortogonali semplici;
7. aggiungere colore e dati simulativi.

La prima visualizzazione puo essere equivalente, non identica allo schema
originale.

Frase da usare nella tesi:

```text
Il viewer non ricostruisce lo schematico grafico originale; costruisce una
rappresentazione elettricamente equivalente alla netlist selezionata.
```

## Visualizzazione stile Falstad/CircuitJS

Elementi desiderati:

- sfondo scuro;
- nodi evidenziati;
- fili con colore in base alla tensione;
- piccola animazione o frecce sui rami con corrente stimata;
- pannello laterale con lista componenti;
- pannello inferiore per segnali temporali;
- selettore `base run` / `scenario`;
- badge per scenari topologici;
- differenze evidenziate tra base e scenario.

Elementi non necessari nella prima versione:

- editor grafico completo;
- drag-and-drop componenti;
- simulazione interattiva in tempo reale;
- supporto completo a tutti i dispositivi SPICE;
- ricostruzione perfetta dello schema originale.

## Relazione con gli scenari di Experiment 2

Experiment 2 ha prodotto scenari che cambiano davvero la netlist:

```text
connect_nodes
feed_nodes_from_source_node
add_voltage_source_between_nodes
add_resistor_between_nodes
```

Experiment 3 deve visualizzare proprio questo passaggio:

```text
base netlist -> scenario netlist -> differenza topologica -> differenza nei risultati
```

Esempi:

- `connect_nodes`: deve comparire un ramo quasi ideale tra due nodi;
- `feed_nodes_from_source_node`: devono comparire uno o piu collegamenti di
  propagazione;
- `add_voltage_source_between_nodes`: deve comparire una nuova sorgente;
- `add_resistor_between_nodes`: deve comparire un nuovo ramo resistivo.

Questa e una delle parti piu forti della tesi, perche dimostra che gli scenari
non sono solo testo generato dall'agente, ma netlist alternative realmente
eseguite e visualizzabili.

## Batch A - Piano circuito per circuito

### a01

Uso in Experiment 3:

- visualizzare base run;
- visualizzare scenario con `connect_nodes`;
- visualizzare scenario con `feed_nodes_from_source_node`;
- mostrare che la netlist scenario contiene rami aggiunti rispetto alla base.

Priorita:

```text
alta
```

Motivo:

caso semplice e utile per mostrare continuita/propagazione verso ramo lampada.

### a02

Uso in Experiment 3:

- visualizzare base run;
- visualizzare scenario con `connect_nodes`;
- mostrare differenza tra circuito base e ramo collegato.

Priorita:

```text
media-alta
```

Motivo:

caso piccolo, buono per validare parser e layout senza troppa complessita.

### a04

Uso in Experiment 3:

- visualizzare base run;
- usare soprattutto risultati `.tran`;
- mostrare che il viewer puo gestire un circuito gia ben simulato senza
  scenario topologico.

Priorita:

```text
media
```

Motivo:

caso importante per transitorio e transistor, ma non centrale per scenari
topologici di Experiment 2.

### a05

Uso in Experiment 3:

- visualizzare base run minimale;
- visualizzare scenario con `add_voltage_source_between_nodes`;
- mostrare come una sorgente aggiunta cambia la lettura diagnostica.

Priorita:

```text
alta
```

Motivo:

caso semplice per sorgente esterna aggiunta.

### a06

Uso in Experiment 3:

- visualizzare base run;
- usare i risultati `.tran`;
- trattare transistor e segnali con una rappresentazione inizialmente
  semplificata.

Priorita:

```text
media
```

Motivo:

utile per dimostrare transitori, ma non e il primo caso per differenze
topologiche scenario.

### a07

Uso in Experiment 3:

- visualizzare base run;
- visualizzare scenari con sorgenti aggiunte;
- mostrare che rami apparentemente inattivi reagiscono quando vengono eccitati.

Priorita:

```text
alta
```

Motivo:

ottimo caso per spiegare la differenza tra `ngspice success` e circuito
diagnosticamente incompleto.

### a08

Uso in Experiment 3:

- visualizzare base run con `.tran`;
- visualizzare scenario con `add_resistor_between_nodes`;
- mostrare il nuovo ramo resistivo e l'effetto su pilotaggio/bias/lampeggio.

Priorita:

```text
alta
```

Motivo:

caso piu interessante per modifica strutturale analogica e comportamento nel
tempo.

### a09

Uso in Experiment 3:

- visualizzare base run;
- visualizzare scenario con `connect_nodes`;
- visualizzare scenario con `feed_nodes_from_source_node`;
- evidenziare trasferimento di alimentazione verso LED e lampada.

Priorita:

```text
alta
```

Motivo:

caso forte per scenari topologici e diagnosi su alimentazione mancante.

### a10

Uso in Experiment 3:

- visualizzare base run;
- visualizzare scenario con switch chiuso e collegamenti aggiunti;
- usare come primo prototipo consigliato.

Priorita:

```text
molto alta
```

Motivo:

e semplice, leggibile e gia contiene scenari topologici chiari. Conviene usarlo
come primo circuito pilota.

## Primo prototipo consigliato

Il primo prototipo dovrebbe partire da:

```text
outputs/pipeline2.0/batchA/experiment2/a10/
```

Run da confrontare:

```text
base run:
outputs/pipeline2.0/batchA/experiment2/a10/07_netlist.cir

scenario run:
outputs/pipeline2.0/batchA/experiment2/a10/scenarios/<scenario_id>/run/07_netlist.cir
```

Motivo:

- netlist piccola;
- scenario topologico evidente;
- differenza base/scenario facile da verificare;
- buon caso per non perdersi subito nei transistor.

## Fasi operative

### Fase 0 - Inventario artefatti

Obiettivo:

- elencare per ogni circuito Batch A quali run base e scenario esistono;
- distinguere scenari topologici e non topologici;
- verificare quali run hanno `.op`, `.tran`, CSV e plot.

Output:

```text
experiment3_batchA_inventory.json
experiment3_batchA_inventory.md
```

### Fase 1 - Parser netlist minimale

Obiettivo:

- leggere `07_netlist.cir`;
- riconoscere righe SPICE principali;
- creare componenti e nodi;
- ignorare in modo controllato `.model`, `.op`, `.tran`, commenti e direttive.

Componenti minimi da supportare:

```text
R, C, L, V, I, D, Q
```

Output:

```text
13_viewer_model.json
```

### Fase 2 - Lettura risultati ngspice

Obiettivo:

- leggere `08_ngspice_stdout.txt`;
- estrarre tensioni nodali quando disponibili;
- leggere `08_tran.csv` quando presente;
- collegare segnali e nodi al viewer model.

Output:

```text
measurements dentro 13_viewer_model.json
```

### Fase 3 - Layout automatico semplice

Obiettivo:

- posizionare nodi e componenti su una griglia;
- garantire che il circuito sia leggibile;
- accettare layout non identico all'immagine originale.

Output:

```text
layout dentro 13_viewer_model.json
```

### Fase 4 - Viewer HTML/SVG

Obiettivo:

- generare una pagina locale;
- disegnare il circuito equivalente;
- colorare nodi e rami;
- mostrare pannello componenti;
- mostrare eventuali grafici `.tran`.

Output:

```text
14_viewer.html
```

### Fase 5 - Confronto base/scenario

Obiettivo:

- caricare due viewer model;
- evidenziare componenti aggiunti o modificati;
- mostrare differenze nei valori elettrici principali.

Output:

```text
14_viewer_compare.html
```

### Fase 6 - Documentazione e valutazione

Obiettivo:

- documentare per ogni circuito se il viewer e utile;
- registrare limiti del layout;
- preparare metriche per grafici finali.

Output:

```text
experiment_ai/pipeline2_spice_analysis/batchA/experiment3/
```

## Metriche semplici per Experiment 3

Per restare leggibili nella tesi, bastano pochi campi.

Tabella minima:

```text
batch
circuit_id
run_type
scenario_id
netlist_parse_status
viewer_model_status
layout_status
spice_values_loaded
tran_loaded
topology_change_visible
human_readability
notes
```

Valori suggeriti:

```text
netlist_parse_status: success | partial | failed
viewer_model_status: success | partial | failed
layout_status: readable | rough | failed
spice_values_loaded: yes | partial | no
tran_loaded: yes | no | not_available
topology_change_visible: yes | partial | no | not_applicable
human_readability: high | medium | low
```

## Criteri di successo

Experiment 3 puo essere considerato riuscito se:

- per i circuiti Batch A escluso `a03` viene creato un viewer model;
- almeno i casi topologici di Experiment 2 mostrano differenze visibili tra
  base e scenario;
- i circuiti con `.tran` mostrano almeno un collegamento ai segnali temporali;
- il viewer non contraddice i risultati ngspice;
- gli output sono salvati in modo ripetibile;
- la documentazione permette un confronto con Experiment 1 e Experiment 2.

## Limiti dichiarati

Questi limiti sono accettabili nella prima versione:

- il viewer non ricostruisce lo schematico originale pixel-perfect;
- il layout automatico puo essere semplice;
- alcuni componenti complessi possono essere rappresentati come blocchi;
- la corrente puo essere stimata solo dove i dati lo permettono;
- CircuitJS/Falstad resta un riferimento visivo, non il motore numerico;
- `a03` resta escluso finche non affrontiamo la correzione del graph.

## Decisione finale

La strategia consigliata e:

```text
costruire un viewer nativo piccolo, basato su netlist e risultati ngspice,
ispirato a CircuitJS ma integrato nella Pipeline 2.0.
```

Il primo passo concreto non e disegnare subito una pagina bella, ma creare il
modello intermedio:

```text
13_viewer_model.json
```

Solo dopo conviene costruire la UI.

## Prossimo passo operativo

Quando inizieremo davvero Experiment 3, il primo task sara:

```text
creare l'inventario Batch A delle run base/scenario da visualizzare
```

Poi:

```text
implementare un parser minimale per 07_netlist.cir su a10
```

Ordine consigliato:

1. inventario Batch A;
2. parser netlist minimale;
3. viewer model JSON per `a10`;
4. prima pagina HTML/SVG statica;
5. confronto base/scenario su `a10`;
6. estensione progressiva ad `a01`, `a09`, `a08`, `a05`, `a07`, `a02`,
   `a04`, `a06`.

Questa sequenza evita di partire dall'interfaccia grafica prima di avere un
contratto dati stabile.

## Workspace operativo `experiment3_viewer`

Per implementare Experiment 3 senza toccare gli output gia consolidati di
Experiment 2, conviene creare una nuova root di lavoro:

```text
outputs/pipeline2.0/batchA/experiment3_viewer/
```

Questa root deve essere una workspace tecnica per viewer e simulatore, non una
riscrittura dei risultati di Experiment 2.

### Cosa copiare

La base principale deve essere:

```text
outputs/pipeline2.0/batchA/experiment2/
```

Motivo:

- contiene le base run `01-08`;
- contiene la maggior parte degli scenari gia eseguiti;
- e la root piu vicina allo stato finale di Experiment 2;
- permette di aprire la web chat con `--experiment experiment3_viewer` senza
  lavorare direttamente su `experiment2`.

La root:

```text
outputs/pipeline2.0/batchA/experiment2_feed_nodes/
```

va invece conservata come sorgente aggiuntiva, non fusa automaticamente dentro
le cartelle `scenarios/` di `experiment3_viewer`.

Motivo:

- contiene solo alcuni circuiti (`a01`, `a09`, `a10`);
- gli scenari sono ripartiti da zero;
- gli id `scenario_1`, `scenario_2`, ecc. possono collidere con quelli gia
  presenti in `experiment2`;
- una fusione cieca renderebbe ambigua la cronologia sperimentale.

Struttura consigliata:

```text
outputs/pipeline2.0/batchA/experiment3_viewer/
  a01/
  a02/
  a03/                  # presente eventualmente, ma escluso dalla prima fase
  a04/
  a05/
  a06/
  a07/
  a08/
  a09/
  a10/
  _sources/
    experiment2_feed_nodes/
      a01/
      a09/
      a10/
```

In questo modo:

- `experiment3_viewer/aXX/` e la workspace attiva della web chat;
- `_sources/experiment2_feed_nodes/` resta materiale consultabile/importabile;
- non perdiamo nessuno scenario gia eseguito;
- evitiamo collisioni tra scenari con lo stesso nome.

### Circuiti della prima fase

La prima fase del viewer lavora su:

```text
a01, a02, a04, a05, a06, a07, a08, a09, a10
```

`a03` puo anche essere copiato per completezza della struttura Batch A, ma deve
restare marcato come:

```text
excluded_from_experiment3_initial_viewer = true
```

### Hook automatico dopo scenario

Il viewer deve essere generato automaticamente quando uno scenario viene
eseguito dalla chat.

Flusso desiderato:

```text
utente scrive "esegui scenario 4"
-> 09_web_chat crea/recupera lo scenario
-> 12_controlled_scenarios.py applica lo scenario
-> ngspice esegue la scenario run
-> 13_build_viewer_model.py genera 13_viewer_model.json
-> opzionalmente viene generato 14_viewer.html
-> 09_web_chat aggiorna il blocco viewer della run selezionata
```

Quindi Experiment 3 non deve richiedere un comando manuale separato per creare
il viewer di uno scenario appena eseguito.

Regola:

```text
ogni nuova run SPICE prodotta dalla chat deve produrre anche il viewer model
```

### Hook automatico sulla base run

Quando la web chat viene aperta su `experiment3_viewer`, la base run deve avere
lo stesso comportamento:

```text
se 13_viewer_model.json esiste -> viene mostrato
se non esiste -> viene generato automaticamente o mostrato un placeholder pulito
```

La generazione automatica e preferibile, purche il fallimento non blocchi la
chat diagnostica.

### Avvio della web chat su Experiment 3

La workspace `experiment3_viewer` puo gia essere aperta con lo stesso script
della chat diagnostica, cambiando solo il parametro `--experiment`.

Circuito pilota `a01`:

```powershell
python scripts\pipeline_2.0\json_to_spice\09_web_chat.py --batch batchA --experiment experiment3_viewer --circuit a01 --ngspice-executable "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

Questa command apre:

```text
outputs/pipeline2.0/batchA/experiment3_viewer/a01/
```

Stato attuale:

- la web chat puo mostrare la base run, l'immagine originale, gli artefatti
  tecnici e gli scenari gia presenti nella workspace;
- il viewer/simulatore visuale non e ancora implementato;
- il primo blocco viewer da aggiungere sara quello della base run;
- quando il viewer sara maturo, la stessa pagina dovra mostrare di default
  `13_viewer_model.json` della base run e, quando l'utente seleziona o crea uno
  scenario, il modello viewer della run scenario.

### Regola di robustezza

Il viewer e un layer aggiuntivo.

Quindi:

- se la generazione viewer riesce, la pagina mostra il circuito equivalente;
- se fallisce, la chat e gli scenari devono continuare a funzionare;
- il fallimento va salvato in un report viewer, non nascosto;
- la base netlist e la scenario netlist non devono mai essere modificate dal
  viewer.
