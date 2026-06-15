# Pipeline 2.0 - riferimento script

Questo documento riassume cosa fa ogni script della Pipeline 2.0.

Serve come riferimento rapido durante lo sviluppo: ogni volta che uno script
viene modificato, esteso o completato, questo file va aggiornato.

La Pipeline 2.0 parte dai Graph JSON prodotti dalla Pipeline 1.0 e costruisce
progressivamente una rappresentazione elettrica utile per SPICE, report e agente
diagnostico.

Sequenza attuale:

```text
run_pipeline2.py
  -> 01_io.py
  -> 02_normalize.py
  -> 03_node_map.py
  -> 04_values.py
  -> 05_device_profiles.py       # previsto, non sviluppato ora
  -> 06_component_rules.py
  -> 07_spice_emit.py
  -> 08_spice_run.py             # opzionale con --run-spice
```

## run_pipeline2.py

`run_pipeline2.py` e il punto di ingresso della Pipeline 2.0.

Si trova in:

```text
scripts/pipeline_2.0/run_pipeline2.py
```

Responsabilita:

- ricevere da terminale batch e circuiti da elaborare;
- caricare gli script numerati `01`, `02`, `03`, ecc.;
- eseguire gli step nell'ordine corretto;
- creare gli output nella cartella del circuito;
- opzionalmente eseguire ngspice con `--run-spice`.

Esempio:

```powershell
python scripts\pipeline_2.0\run_pipeline2.py --batch batchA --circuits a01 a02 a10
```

Con esecuzione SPICE:

```powershell
python scripts\pipeline_2.0\run_pipeline2.py --batch batchA --circuits a01 --run-spice --ngspice-executable ngspice_con
```

Output principale:

```text
outputs/pipeline2.0/<batch>/<circuit>/
```

## 01_io.py

`01_io.py` gestisce input, output e percorsi comuni.

Si trova in:

```text
scripts/pipeline_2.0/json_to_spice/01_io.py
```

Input principale:

```text
outputs/pipeline1.0/<batch>/06_graph_report/<circuit>/<circuit>.json
```

Responsabilita:

- trovare il Graph JSON prodotto dalla Pipeline 1.0;
- creare la cartella output della Pipeline 2.0;
- leggere file JSON;
- scrivere file JSON formattati;
- copiare il Graph JSON sorgente nella nuova cartella output.

Output prodotto:

```text
01_graph.json
```

Perche serve:

Questo step centralizza i percorsi e impedisce che ogni modulo gestisca file e
cartelle in modo diverso.

## 02_normalize.py

`02_normalize.py` trasforma il Graph JSON in una struttura interna piu comoda.

Si trova in:

```text
scripts/pipeline_2.0/json_to_spice/02_normalize.py
```

Input:

```text
01_graph.json
```

Responsabilita:

- normalizzare componenti e terminali;
- costruire lookup rapidi per componenti e terminali;
- rendere esplicito il grafo terminale-terminale;
- controllare eventuali riferimenti a terminali non presenti;
- produrre statistiche e warning di normalizzazione.

Output prodotto:

```text
02_normalized_circuit.json
```

Perche serve:

Il JSON della Pipeline 1.0 e corretto come output topologico, ma per SPICE
servono viste piu ordinate: componenti, terminali, classi, terminali per
componente e grafo normalizzato.

Questo step non genera ancora nodi SPICE e non produce netlist.

## 03_node_map.py

`03_node_map.py` costruisce la mappa dei nodi elettrici.

Si trova in:

```text
scripts/pipeline_2.0/json_to_spice/03_node_map.py
```

Input:

```text
02_normalized_circuit.json
```

Responsabilita:

- leggere il grafo dei terminali;
- trovare le componenti connesse del grafo;
- assegnare un nodo elettrico a ogni gruppo di terminali connessi;
- mappare i terminali collegati a GND nel nodo SPICE `0`;
- costruire la mappa terminale -> nodo;
- costruire la vista componente -> terminale -> nodo.

Output prodotto:

```text
03_node_map.json
```

Perche serve:

SPICE non ragiona in termini di linee disegnate, ma in termini di nodi
elettrici. Questo step e il ponte tra il grafo topologico e la netlist.

Esempio concettuale:

```text
resistor22.1_t1 -> N002
lamp13.1_t1     -> N004
gnd9.1_t1       -> 0
```

## 04_values.py

`04_values.py` associa valori, modelli e stati manuali ai componenti.

Si trova in:

```text
scripts/pipeline_2.0/json_to_spice/04_values.py
```

Input:

```text
02_normalized_circuit.json
03_node_map.json
metadata/pipeline2_manual_values/<batch>/<circuit>_values.yaml
```

Responsabilita:

- leggere il file YAML dei valori manuali;
- associare valori ai componenti riconosciuti;
- associare eventuali supply manuali ai nodi;
- associare modelli semplici, per esempio `LED_RED`;
- leggere lo stato degli switch;
- distinguere componenti pronti, componenti senza valori e componenti che non
  richiedono valori;
- registrare assunzioni e sorgenti dei valori.

Output prodotto:

```text
04_values_bound.json
```

Perche serve:

La Pipeline 1.0 riconosce topologia e componenti, ma non sempre legge i valori
elettrici. Per ora i valori vengono scritti a mano nei file YAML; in futuro
potranno arrivare da OCR.

Questo step non inventa valori mancanti. Se un valore non e disponibile, lo
segnala.

## 05_device_profiles.py

`05_device_profiles.py` e previsto per componenti complessi e circuiti
integrati.

Si trova in:

```text
scripts/pipeline_2.0/json_to_spice/05_device_profiles.py
```

Stato attuale:

```text
scheletro creato, non implementato nella pipeline attuale
```

Responsabilita future:

- leggere profili dichiarativi per IC e blocchi funzionali;
- descrivere pin di alimentazione, GND, reset, clock, enable, ingressi e uscite;
- gestire pin non connessi;
- dichiarare vincoli minimi di funzionamento;
- collegare eventuali modelli SPICE o subcircuit disponibili;
- abilitare controlli pin-aware per Batch C1 e C2.

Output previsto:

```text
05_device_profiles.json
```

Perche servira:

Molti circuiti reali contengono IC o componenti non simulabili direttamente.
Anche senza un modello SPICE completo, sara utile controllare alimentazione,
GND, reset, clock e collegamenti principali.

## 06_component_rules.py

`06_component_rules.py` decide come trattare ogni componente in SPICE.

Si trova in:

```text
scripts/pipeline_2.0/json_to_spice/06_component_rules.py
```

Input:

```text
04_values_bound.json
metadata/pipeline2_spice_classes.yaml
```

Responsabilita:

- leggere il mapping delle classi SPICE;
- classificare ogni componente;
- decidere se un componente e emettibile in netlist;
- distinguere componenti diretti, equivalenti, semplificati, strutturali,
  non supportati o con parametri mancanti;
- preparare nodi, prefissi SPICE e parametri da usare nello step 07;
- produrre statistiche sullo stato del circuito.

Output prodotto:

```text
06_component_rules.json
```

Esempi di decisione:

```text
Resistor  -> emesso come R se ha valore
Capacitor -> emesso come C se ha valore
Battery   -> emessa come V se ha valore
LED       -> emesso come D se ha modello
Lamp      -> emessa come resistenza equivalente
Switch    -> gestito in base allo stato open/closed
Connector -> componente strutturale, non emesso
GND       -> componente strutturale, non emesso
```

Perche serve:

Non tutti i componenti riconosciuti devono diventare una riga SPICE. Alcuni
servono solo per la topologia, altri possono essere semplificati, altri ancora
devono essere saltati per ora.

Questo step rende esplicita la decisione prima della generazione della netlist.

## 07_spice_emit.py

`07_spice_emit.py` genera la netlist SPICE.

Si trova in:

```text
scripts/pipeline_2.0/json_to_spice/07_spice_emit.py
```

Input:

```text
06_component_rules.json
```

Responsabilita:

- leggere le regole pronte per SPICE;
- generare righe SPICE per componenti supportati;
- emettere sorgenti, resistenze, condensatori, LED, lampade equivalenti e
  switch chiusi quando disponibili;
- saltare componenti strutturali come connector e GND;
- commentare componenti non emessi o non supportati;
- aggiungere modelli `.model` quando necessari;
- aggiungere analisi base `.op`;
- aggiungere `.tran` quando richiesto dal file `values.yaml`;
- esportare automaticamente i dati transitori in `08_tran.csv`;
- salvare la netlist e un report di emissione.

Output prodotti:

```text
07_netlist.cir
07_spice_emit_report.json
```

Perche serve:

Questo step trasforma la rappresentazione elettrica interna in un file SPICE
leggibile da ngspice.

La netlist puo essere completa o parziale. Se alcuni componenti non sono
supportati, lo script non deve fallire: li registra nel report e, quando utile,
li commenta nella netlist.

## 08_spice_run.py

`08_spice_run.py` esegue ngspice sulla netlist generata.

Si trova in:

```text
scripts/pipeline_2.0/json_to_spice/08_spice_run.py
```

Input:

```text
07_netlist.cir
```

Responsabilita:

- cercare l'eseguibile ngspice disponibile nel sistema;
- supportare `ngspice_con`, `ngspice_con.exe`, `ngspice`, `ngspice.exe` o un
  path esplicito;
- eseguire ngspice in batch mode;
- salvare stdout e stderr;
- generare `08_tran_plot.svg` quando esiste un export transitorio;
- registrare codice di uscita e comando usato;
- non interpretare ancora il significato elettrico del risultato.

Output prodotti:

```text
08_spice_run.json
08_ngspice_stdout.txt
08_ngspice_stderr.txt
08_tran.csv, se il circuito richiede .tran
08_tran_plot.svg, se 08_tran.csv e disponibile
```

Perche serve:

Questo step verifica se la netlist generata e davvero eseguibile da ngspice.

Importante: `08_spice_run.py` non corregge il circuito e non interpreta a fondo
stdout/stderr. Salva solo il risultato grezzo. L'interpretazione sara compito
degli step successivi, soprattutto `09_summarize_spice.py`,
`10_build_diagnostic_context.py` e poi dell'agente diagnostico.

## Output complessivo per circuito

Per un circuito eseguito fino a SPICE, la cartella output ha questa forma:

```text
outputs/pipeline2.0/<batch>/<circuit>/
|-- 01_graph.json
|-- 02_normalized_circuit.json
|-- 03_node_map.json
|-- 04_values_bound.json
|-- 06_component_rules.json
|-- 07_netlist.cir
|-- 07_spice_emit_report.json
|-- 08_spice_run.json
|-- 08_ngspice_stdout.txt
`-- 08_ngspice_stderr.txt
```

Quando `05`, `09`, `10` e `11` saranno implementati, la cartella potra
contenere anche:

```text
05_device_profiles.json
09_spice_summary.json
10_diagnostic_context.json
11_agent_response.md
```

## Stato attuale

Implementati e usati:

```text
01_io.py
02_normalize.py
03_node_map.py
04_values.py
06_component_rules.py
07_spice_emit.py
08_spice_run.py
run_pipeline2.py
```

Creato come scheletro, ma non ancora sviluppato:

```text
05_device_profiles.py
```

Creati come scheletro per fasi successive:

```text
09_summarize_spice.py
10_build_diagnostic_context.py
11_agent_readonly.py
12_controlled_scenarios.py
```

## Prossimi aggiornamenti previsti

Questo documento andra aggiornato quando:

- aggiungiamo nuove classi in `metadata/pipeline2_spice_classes.yaml`;
- cambiamo lo schema dei file `values.yaml`;
- implementiamo `05_device_profiles.py`;
- implementiamo `09_summarize_spice.py`;
- implementiamo `10_build_diagnostic_context.py`;
- implementiamo `11_agent_readonly.py`;
- aggiungiamo scenari controllati o agente AI.
