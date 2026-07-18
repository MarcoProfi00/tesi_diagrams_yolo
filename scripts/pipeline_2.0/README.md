# Pipeline 2.0 - Graph JSON to SPICE

Questo README spiega come usare oggi la Pipeline 2.0 da terminale.

Per una descrizione piu analitica del ruolo di ogni script, vedere anche:

```text
notes/third_part_from_json_to_spice/pipeline2_scripts_reference.md
```

La Pipeline 2.0 oggi ha due livelli:

```text
1. pipeline tecnica
   Graph JSON -> netlist SPICE -> ngspice

2. layer diagnostico/interattivo
   web chat -> contesto diagnostico -> agente -> scenari controllati
```

## Architettura attuale

Catena logica:

```text
Graph JSON
-> 01_io
-> 02_normalize
-> 03_node_map
-> 04_values
-> 06_component_rules
-> 07_spice_emit
-> 08_spice_run
-> 10_build_diagnostic_context
-> 09_web_chat
-> 11_agent_readonly
-> 12_controlled_scenarios
```

Nota importante:

- `05_device_profiles.py` esiste, ma oggi non e ancora integrato nel flusso
  reale di `run_pipeline2.py`;
- `09`, `11` e `12` non vengono eseguiti automaticamente da
  `run_pipeline2.py`: si usano separatamente.

## Input richiesti

Per ogni circuito servono:

- Graph JSON della Pipeline 1.0:
  `outputs/pipeline1.0/<batch>/06_graph_report/<circuit>/<circuit>.json`
- valori manuali:
  `metadata/pipeline2_manual_values/<batch>/<circuit>_values.yaml`
- classi SPICE:
  `metadata/pipeline2_spice_classes.yaml`
- modelli SPICE:
  `metadata/pipeline2_spice_models.yaml`

Esempio:

```text
outputs/pipeline1.0/batchA/06_graph_report/a01/a01.json
metadata/pipeline2_manual_values/batchA/a01_values.yaml
metadata/pipeline2_spice_classes.yaml
metadata/pipeline2_spice_models.yaml
```

## Output supportati

Root standard:

```text
outputs/pipeline2.0/<batch>/<circuit>/
```

Root separata per esperimenti:

```text
outputs/pipeline2.0/<batch>/<experiment>/<circuit>/
```

La seconda forma serve quando vuoi tenere completamente separati:

- chat;
- scenari;
- manifest diagnostico;
- conclusioni;
- artefatti di esperimenti diversi.

Convenzione attuale del progetto:

- `outputs/pipeline2.0/<batch>/<circuit>/` resta la root canonica della base
  tecnica del circuito;
- le cartelle `outputs/pipeline2.0/<batch>/<experiment>/<circuit>/` sono root
  sperimentali separate create per comodita metodologica, confronto e
  tracciabilita;
- nel caso del Batch A, questo significa che `a01...a10` restano la baseline
  tecnica ufficiale, mentre `experiment1/`, `experiment2/` e
  `experiment2_feed_nodes/` restano copie/workspace sperimentali espliciti.

## Script principali

## 1. Orchestrazione base

### run_pipeline2.py

Path:

```text
scripts/pipeline_2.0/run_pipeline2.py
```

Fa questo:

- esegue gli step tecnici della pipeline;
- genera gli output `01-07`;
- opzionalmente esegue `08_spice_run`;
- costruisce anche `10_diagnostic_context.json`.

Gli step oggi caricati davvero dal codice sono:

```text
01_io.py
02_normalize.py
03_node_map.py
04_values.py
06_component_rules.py
07_spice_emit.py
08_spice_run.py
10_build_diagnostic_context.py
```

Il mapping elettrico supporta sia `NPN_Transistor` sia `PNP_Transistor` con
ordine nodi SPICE `C, B, E`. Il modello concreto resta dichiarato nel file
manuale dei valori; quando l'immagine non riporta un part number e disponibile
il modello minimale `PNP_GENERIC`.

### prepare_experiment_outputs.py

Path:

```text
scripts/pipeline_2.0/prepare_experiment_outputs.py
```

Fa questo:

- crea una root esperimento separata;
- copia artefatti gia esistenti senza sovrascriverli;
- permette di ripartire dalla stessa base `01-08` con una nuova sessione
  sperimentale pulita.

Modalita:

```text
base-only
full
```

`base-only` copia solo i file top-level `01-08`.

`full` copia tutta la cartella circuito.

## 2. Pipeline tecnica

### 01_io.py

- trova il Graph JSON della Pipeline 1.0;
- prepara la cartella output;
- copia `01_graph.json`;
- centralizza helper di lettura/scrittura.

### 02_normalize.py

- normalizza il Graph JSON;
- costruisce una struttura piu comoda per i passaggi successivi;
- salva `02_normalized_circuit.json`.

### 03_node_map.py

- costruisce i nodi elettrici;
- mappa la massa SPICE nel nodo `0`;
- salva `03_node_map.json`.

### 04_values.py

- legge i valori manuali dal file YAML;
- associa valori, modelli e stati ai componenti;
- salva `04_values_bound.json`.

### 05_device_profiles.py

Stato attuale:

```text
presente come scheletro, non ancora attivo nel flusso reale
```

Servira piu avanti per:

- IC;
- pin-aware checks;
- profili dichiarativi di componenti complessi.

### 06_component_rules.py

- applica il mapping SPICE delle classi;
- decide cosa e emettibile, strutturale, mancante o non supportato;
- salva `06_component_rules.json`.

### 07_spice_emit.py

- genera la netlist SPICE;
- emette anche modelli quando servono;
- salva:

```text
07_netlist.cir
07_spice_emit_report.json
```

### 08_spice_run.py

- esegue ngspice in batch mode;
- salva stdout, stderr e report;
- genera anche artefatti `.tran` se disponibili.

Output tipici:

```text
08_spice_run.json
08_ngspice_stdout.txt
08_ngspice_stderr.txt
08_tran.csv
08_tran_plot.png
08_tran_plot.svg
```

### 10_build_diagnostic_context.py

- costruisce il manifest diagnostico leggero;
- non duplica gli output completi;
- salva:

```text
10_diagnostic_context.json
```

Questo manifest include:

- summary tecnica;
- path degli artefatti;
- scenari gia eseguiti;
- scenario budget;
- regole per l'agente.

## 3. Layer diagnostico e interattivo

### 09_web_chat.py

- apre un server locale temporaneo;
- mostra gli artefatti del circuito;
- mostra il viewer/simulatore della base run o dello scenario selezionato;
- avvia la chat diagnostica;
- riconosce comandi di scenario;
- chiama `10`, `11` e `12` quando necessario;
- genera automaticamente gli artefatti viewer `13-15` per una nuova run
  scenario.

File chat principali:

```text
11_agent_input_preview_chat.md
11_agent_prompt_chat.md
11_agent_response_chat.md
```

Per le root `experiment2*` salva anche:

```text
experiment2_chat/chat_history.json
experiment2_chat/chat_history.md
experiment2_chat/scenario_registry.json
experiment2_chat/scenario_registry.md
```

Per `experiment3_1` la stessa sessione file-based e disponibile nella cartella
`experiment_chat/`; le root `experiment2*` continuano a usare
`experiment2_chat/` per compatibilita.

Gli scenari CHAT eseguibili devono includere `expect` e dichiarare
`intent: diagnostic | correction`. Per compatibilita prudente, uno scenario
privo di `intent` viene registrato come `diagnostic`: puo confermare una causa
o una precondizione, ma non arresta la diagnosi come problema risolto. Solo
`intent: correction` esplicito puo produrre uno stop risolutivo, e le misure
devono verificare direttamente il sintomo. Per audio e altri segnali variabili
serve quindi una run `tran` con una misura `tran_vpp` sull'uscita; alimentazione
presente o corrente di batteria non nulla dimostrano soltanto la precondizione.

Per propagazione, attenuazione e amplificazione, lo scenario puo dichiarare
`gain: {"input":"v(...)","output":"v(...)","min_ratio":...}`. La soglia
positiva appartiene allo scenario ed e motivata dal suo obiettivo: non esiste
una soglia universale imposta a tutti i circuiti. Se il rapporto Vpp misurato e
inferiore, lo step 12 classifica il trasferimento come insufficiente anche se
l'uscita e numericamente non nulla o `changed`. Inoltre, se una risposta CHAT
interpreta scenari eseguiti senza trovare `stop_automation=true` e resta budget,
deve proporre un nuovo scenario autonomo, salvo richiesta esplicita di
conclusione finale o mancanza di evidenza esterna indispensabile.
Una nuova run non puo ripetere la stessa firma di azioni soltanto per aggiungere
`gain`, misure o soglie: questi campi reinterpretano risultati gia disponibili
ma non cambiano il circuito. Dopo un trasferimento insufficiente il nuovo test
deve spostare il confine di isolamento o applicare una azione elettricamente
distinta. Gli scenari CHAT/AGENT riconosciuti come test di trasferimento sono
validi soltanto con `gain.min_ratio` positivo.

### 11_agent_readonly.py

- legge `10_diagnostic_context.json`;
- costruisce preview e prompt dell'agente;
- puo chiamare OpenAI solo con `--run-agent`;
- non modifica netlist e non esegue scenari.

Output:

```text
11_agent_input_preview.md
11_agent_prompt.md
11_agent_response.md   # con --run-agent
```

### 12_controlled_scenarios.py

- applica scenari solo su una copia separata;
- modifica soltanto `run/07_netlist.cir`;
- puo eseguire ngspice sulla run scenario;
- crea confronto base vs scenario.
- puo inserire condizioni iniziali transitorie senza aggiungere componenti.

Struttura scenario:

```text
scenarios/<scenario_id>/
|-- scenario.json
|-- scenario_status.json
|-- scenario_copy_manifest.json
|-- 12_controlled_scenarios.json
|-- scenario_comparison.json
|-- base_snapshot/
`-- run/
```

### 13_build_viewer_model.py

- costruisce il modello del circuito realmente simulato;
- unisce netlist, node map, component rules, misure ngspice e geometry seed
  della Pipeline 1.0;
- salva `13_viewer_model.json`.

### 14_build_viewer_layout.py

- calcola posizione, terminali e route ortogonali dei componenti;
- usa bbox/orientamenti come seed e include fallback per componenti scenario;
- riserva una fascia destra stabile per la legenda, separata dal circuito;
- salva `14_viewer_layout.json`.

### 15_render_viewer_svg.py

- renderizza il circuito equivalente in `15_viewer.svg`;
- usa un vocabolario comune di simboli e stati elettrici;
- rappresenta rami attivi, segnali variabili, switch, componenti scenario,
  LED/lampade e attraversamenti senza giunzione.

Implementazione interna:

```text
json_to_spice/viewer_core/
|-- contracts.py          nomi e versioni degli artefatti
|-- json_io.py            lettura e scrittura JSON condivisa
|-- component_library.py  vocabolario generale dei componenti
|-- model_builder.py      implementazione dello step 13
|-- layout_builder.py     implementazione dello step 14
|-- svg_renderer.py       implementazione dello step 15
`-- svg_styles.py         CSS e animazioni incorporati nell'SVG
```

Gli script `13`, `14` e `15` restano entry point CLI piccoli e stabili. Il file
storico `viewer_component_library.py` resta un wrapper di compatibilita.

### scenario_runtime.py

- e il percorso tecnico condiviso da `CHAT` e `AGENT`;
- valida forma e whitelist delle azioni;
- rifiuta scenari duplicati;
- conta soltanto le run SPICE realmente eseguite;
- copia la base, richiama `12`, esegue ngspice e genera `13-15`;
- non sceglie autonomamente gli scenari.

### 16_autonomous_diagnosis.py

- espone da CLI `start`, `step` e `stop` del ciclo autonomo;
- esegue una sola decisione per chiamata;
- usa i moduli separati in `autonomous_agent/`;
- salva lo stato in `experiment_chat/autonomous_diagnosis.json`.

Il backend della web chat usa lo stesso controller tramite le API locali:

```text
/api/agent/start
/api/agent/step
/api/agent/stop
/api/agent/state
```

## Primitive scenario oggi supportate

Scenari elettrici / di pilotaggio:

```text
drive_node_voltage
set_initial_node_voltage
add_voltage_source_between_nodes
change_source_value
change_component_value
close_switch
```

Scenari topologici controllati:

```text
connect_nodes
add_resistor_between_nodes
feed_nodes_from_source_node
```

Nota importante:

```text
la base run non viene mai modificata
```

`set_initial_node_voltage` e disponibile solo con `analysis: "tran"`: emette
`.ic V(NODO)=valore` nella netlist scenario, non aggiunge una sorgente
permanente e non usa `UIC`. Serve per verificare un possibile equilibrio
iniziale artificiosamente simmetrico, non per alimentare il circuito.

Ogni scenario parte sempre dalla base run. Non resta attivo automaticamente lo
scenario precedente.

## Comandi principali

## Eseguire la pipeline tecnica

Senza SPICE:

```powershell
python scripts\pipeline_2.0\run_pipeline2.py --batch <batch> --circuits <circuit_1> <circuit_2>
```

Con SPICE:

```powershell
python scripts\pipeline_2.0\run_pipeline2.py --batch <batch> --circuits <circuit> --run-spice --ngspice-executable ngspice_con
```

Con path completo:

```powershell
python scripts\pipeline_2.0\run_pipeline2.py --batch <batch> --circuits <circuit> --run-spice --ngspice-executable "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

Con root esperimento:

```powershell
python scripts\pipeline_2.0\run_pipeline2.py --batch <batch> --experiment <experiment> --circuits <circuit> --run-spice --ngspice-executable "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

## Preparare una root esperimento separata

Ripartire dalla stessa base `01-08`:

```powershell
python scripts\pipeline_2.0\prepare_experiment_outputs.py --batch batchA --experiment experiment2 --circuits a01 a02 a03 a04 a05 a06 a07 a08 a09 a10 --mode base-only
```

Congelare uno stato completo:

```powershell
python scripts\pipeline_2.0\prepare_experiment_outputs.py --batch batchA --experiment experiment1 --circuits a01 a02 a03 a04 a05 a06 a07 a08 a09 a10 --mode full
```

Preparare una variante interna a un esperimento:

```powershell
python scripts\pipeline_2.0\prepare_experiment_outputs.py --batch <batch> --experiment <experiment> --destination-variant <variant> --source-experiment <source_experiment> --circuits <circuits> --mode base-only
```

Base di Experiment 4:

```powershell
python scripts\pipeline_2.0\prepare_experiment_outputs.py --batch batchA --experiment experiment4 --destination-variant chat --source-experiment experiment3_1 --circuits a01 a02 a04 a05 a06 a07 a08 a09 a10 --mode base-only
python scripts\pipeline_2.0\prepare_experiment_outputs.py --batch batchA --experiment experiment4 --destination-variant agent --source-experiment experiment3_1 --circuits a01 a02 a04 a05 a06 a07 a08 a09 a10 --mode base-only
```

Queste copie contengono soltanto gli artefatti tecnici `01-08`, inclusa la
base run ngspice gia eseguita. Contesto `10`, chat, scenari e viewer vengono
creati separatamente dentro ciascuna variante.

## Aprire la web chat locale

Root standard:

```powershell
python scripts\pipeline_2.0\json_to_spice\09_web_chat.py --batch <batch> --circuit <circuit>
```

Root esperimento:

```powershell
python scripts\pipeline_2.0\json_to_spice\09_web_chat.py --batch <batch> --experiment <experiment> --circuit <circuit>
```

Variante interna a una root esperimento:

```powershell
python scripts\pipeline_2.0\json_to_spice\09_web_chat.py --batch <batch> --experiment <experiment> --variant <variant> --circuit <circuit>
```

La variante risolve gli output in
`outputs/pipeline2.0/<batch>/<experiment>/<variant>/<circuit>/`.

Experiment 4 espone entrambe le varianti con un solo comando:

```powershell
python scripts\pipeline_2.0\json_to_spice\09_web_chat.py --batch batchA --experiment experiment4 --circuit a01 --ngspice-executable "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

Lo switch `CHAT` / `AGENT` nella barra superiore cambia l'intero workspace:

```text
CHAT  -> outputs/pipeline2.0/batchA/experiment4/chat/a01/
AGENT -> outputs/pipeline2.0/batchA/experiment4/agent/a01/
```

History, registry, scenari, viewer e artefatti generati restano separati. Non
serve un database: lo stato persistente vive nei file di ciascun workspace.

Con ngspice per eseguire scenari dalla chat:

```powershell
python scripts\pipeline_2.0\json_to_spice\09_web_chat.py --batch <batch> --experiment <experiment> --circuit <circuit> --ngspice-executable "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

Per aprire la workspace di Experiment 3 sul circuito pilota `a01`:

```powershell
python scripts\pipeline_2.0\json_to_spice\09_web_chat.py --batch batchA --experiment experiment3_viewer --circuit a01 --ngspice-executable "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

Nota:

- `experiment3_viewer` usa gli output in `outputs/pipeline2.0/batchA/experiment3_viewer/`;
- la web chat mostra il viewer/simulatore nella pagina centrale;
- ogni run usa `13_viewer_model.json`, `14_viewer_layout.json` e
  `15_viewer.svg`;
- i tre artefatti vengono generati o aggiornati automaticamente quando si apre
  una run e dopo l'esecuzione di uno scenario;
- il renderer e generale e non contiene coordinate hardcoded di `a01`.

Opzioni utili:

```text
--port 8766
--no-browser
```

URL default:

```text
http://127.0.0.1:8765/
```

## Generare preview e prompt agente

Senza OpenAI:

```powershell
python scripts\pipeline_2.0\json_to_spice\11_agent_readonly.py --batch <batch> --experiment <experiment> --circuit <circuit> --question "Perche la lampada non si accende?"
```

Con OpenAI:

```powershell
python scripts\pipeline_2.0\json_to_spice\11_agent_readonly.py --batch <batch> --experiment <experiment> --circuit <circuit> --question "Perche la lampada non si accende?" --run-agent --model gpt-5.4
```

Modelli previsti oggi:

```text
gpt-5.4
gpt-5.5
gpt-5.4-mini
gpt-5-mini
```

## Applicare uno scenario da terminale

Senza SPICE:

```powershell
python scripts\pipeline_2.0\json_to_spice\12_controlled_scenarios.py --scenario-dir outputs\pipeline2.0\<batch>\<experiment>\<circuit>\scenarios\<scenario_id>
```

Con SPICE:

```powershell
python scripts\pipeline_2.0\json_to_spice\12_controlled_scenarios.py --scenario-dir outputs\pipeline2.0\<batch>\<experiment>\<circuit>\scenarios\<scenario_id> --run-spice --ngspice "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

## Flussi d'uso consigliati

## 1. Generare la base tecnica

```text
run_pipeline2.py
-> output 01-08
-> 10_diagnostic_context.json
```

## 2. Separare un esperimento

```text
prepare_experiment_outputs.py --mode base-only
-> nuova root esperimento pulita
```

## 3. Aprire la chat

```text
09_web_chat.py
-> domanda utente
-> step 10
-> step 11
-> risposta agente
```

## 4. Eseguire uno scenario

```text
utente sceglie uno scenario
-> 09 crea scenarios/<scenario_id>/
-> copia base_snapshot/ e run/
-> chiama 12
-> ngspice scenario
-> scenario_comparison.json
-> 13_build_viewer_model.py
-> 14_build_viewer_layout.py
-> 15_render_viewer_svg.py
```

## Budget scenari

Regola attuale:

```text
massimo 5 scenari eseguibili per circuito
```

Il limite vale sulle run scenario realmente eseguite, non sul numero di
proposte presenti nella conversazione.

Quando il budget e esaurito:

- la chat non crea una sesta run scenario;
- l'agente deve chiudere con una conclusione diagnostica finale.

## Ngspice su Windows

Nel nostro ambiente:

```text
C:\Users\m.profilo\Spice64\bin\ngspice_con.exe
```

Verifica veloce:

```powershell
& "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe" -v
```

Per la pipeline conviene usare `ngspice_con.exe`, cioe la versione console.

## File piu importanti da leggere

Per capire il circuito:

```text
03_node_map.json
04_values_bound.json
06_component_rules.json
07_netlist.cir
07_spice_emit_report.json
08_ngspice_stdout.txt
08_ngspice_stderr.txt
10_diagnostic_context.json
```

Per capire la chat:

```text
11_agent_input_preview_chat.md
11_agent_prompt_chat.md
11_agent_response_chat.md
```

Per `experiment2*`:

```text
experiment2_chat/chat_history.json
experiment2_chat/scenario_registry.json
```

Per capire uno scenario:

```text
scenario.json
scenario_status.json
12_controlled_scenarios.json
scenario_comparison.json
```

Per capire il viewer della run selezionata:

```text
13_viewer_model.json
14_viewer_layout.json
15_viewer.svg
```

## Roadmap immediata

Lo stato attuale va letto cosi:

- la base tecnica `01-08` e consolidata;
- il manifest `10` e consolidato;
- la web chat `09`, l'agente `11` e gli scenari `12` sono attivi;
- il viewer `13-15` e integrato nella web chat per base run e scenari;
- gli esperimenti si gestiscono con root separate;
- Experiment 3.1 ha validato sul Batch A il flusso pulito
  agente -> scenario -> viewer;
- Experiment 4 contiene il confronto tra flusso guidato e automazione
  controllata multi-scenario, validato in prima passata su `a01`, `a02` e
  `a04`-`a10`; `a03` resta escluso per il limite topologico/SPICE noto.

Architettura di base di Experiment 4:

```text
outputs/pipeline2.0/batchA/experiment4/
|-- chat/<circuit>/
`-- agent/<circuit>/
```

La web app offre due modalita selezionabili:

- `CHAT`: proposta agente ed esecuzione confermata dall'utente;
- `AGENT`: ciclo autonomo controllato, con avanzamento e arresto manuale.

Le modalita condividono la stessa base tecnica iniziale, ma mantengono
separati chat, registry, scenari, viewer e stato diagnostico. Routing, switch,
runtime e prima versione del controller autonomo sono implementati.

Il runtime comune centralizza:

- creazione e validazione dello scenario;
- esecuzione dello step 12 e di ngspice;
- generazione viewer `13/14/15`;
- aggiornamento di registry, history e contesto diagnostico;
- conteggio del budget e rilevamento dei duplicati.

Moduli implementati:

```text
scenario_runtime.py
16_autonomous_diagnosis.py
autonomous_agent/contracts.py
autonomous_agent/prompt_builder.py
autonomous_agent/state_store.py
autonomous_agent/controller.py
autonomous_agent/presentation.py
web_chat/agent_view.css
web_chat/agent_view.js
```

La modalita `AGENT` usa una vista separata dalla chat tradizionale. Il
presenter costruisce `agent_view` a partire dallo stato persistente e dagli
artefatti reali delle run; il frontend mostra obiettivo, contatori, piano,
strumenti, timeline dei test, evidenze OP/TRAN e conclusione. Viewer e grafici
restano nel pannello centrale della run selezionata. La modalita `CHAT`
continua a usare cronologia e messaggi precedenti senza passare da questa
presentazione.

Le nuove conclusioni possono separare `final_cause` e
`verified_correction`; `final_answer` resta disponibile per sintesi e
compatibilita con gli stati gia salvati.

Guardrail della prima versione:

- primitive autonome ammesse: `drive_node_voltage`, `set_initial_node_voltage`, `change_source_value`,
  `change_component_value`, `close_switch`, `connect_nodes`,
  `feed_nodes_from_source_node`, `add_voltage_source_between_nodes`,
  `add_resistor_between_nodes`;
- l'agente preferisce modifiche minime e usa nuove sorgenti o rami soltanto
  quando sono giustificati dalle evidenze tecniche;
- `feed_nodes_from_source_node` distribuisce una alimentazione gia misurata,
  mentre `connect_nodes` testa una continuita mancante generica; non possono
  essere proposti sulla stessa relazione nella stessa decisione;
- `add_resistor_between_nodes` resta una ipotesi separata di accoppiamento
  resistivo reale;
- `set_initial_node_voltage` e riservata a scenari `tran` che verificano una
  perturbazione iniziale; non modifica topologia, valori o alimentazione;
- massimo 2 scenari indipendenti nella stessa decisione, eseguiti in sequenza;
- massimo 5 run SPICE scenario per diagnosi;
- massimo 8 decisioni del modello, inclusa la conclusione finale;
- un solo retry se la risposta JSON non rispetta il contratto;
- scenari non validi o duplicati non consumano budget;
- se l'utente richiede una correzione, l'agente non chiude come sola causa
  localizzata finche resta budget e manca una correzione verificata;
- per lampeggio, regolarita, duty cycle o durata di accensione, gli scenari
  `.tran` dichiarano `temporal_expect`: il runtime confronta i profili viewer
  base/scenario prima di accettare lo stop risolutivo;
- pulsante `Stop` e stato persistente riprendibile.

La macchina a stati e il runtime sono stati verificati con decisioni
controllate e con la prima passata OpenAI su `a01`, `a02` e `a04`-`a10`.
Le sequenze temporali tra componenti restano un'estensione futura: richiedono
una `.tran` aggiungibile dallo scenario e profili temporali anche per lampade.

## Prossima fase: Experiment 5 / Batch B

Experiment 5 usera il Batch B come prova di generalizzazione. Per ogni circuito
si prepara prima la base fino a `01-08` e il viewer, poi si prova `CHAT` con le
primitive esistenti e infine `AGENT` sugli stessi sintomi. Nuove primitive o
simboli viewer saranno aggiunti solo quando il limite e ricorrente e generale,
mai per adattare la pipeline a un singolo circuito.

I comandi diretti in linguaggio naturale verranno affrontati dopo il ciclo
autonomo di base e riuseranno lo stesso runtime.

## Sintesi finale

La Pipeline 2.0 oggi va usata cosi:

```text
1. genero la base tecnica del circuito;
2. se serve, creo una root esperimento separata;
3. apro la chat locale;
4. faccio rispondere l'agente;
5. eseguo eventuali scenari su copie separate;
6. confronto base run e scenario run senza toccare l'originale;
7. leggo il viewer della run selezionata, generato dalla netlist effettiva.
```
