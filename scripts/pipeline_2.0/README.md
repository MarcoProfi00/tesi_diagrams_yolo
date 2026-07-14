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
- avvia la chat diagnostica;
- riconosce comandi di scenario;
- chiama `10`, `11` e `12` quando necessario.

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

## Primitive scenario oggi supportate

Scenari elettrici / di pilotaggio:

```text
drive_node_voltage
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

## Aprire la web chat locale

Root standard:

```powershell
python scripts\pipeline_2.0\json_to_spice\09_web_chat.py --batch <batch> --circuit <circuit>
```

Root esperimento:

```powershell
python scripts\pipeline_2.0\json_to_spice\09_web_chat.py --batch <batch> --experiment <experiment> --circuit <circuit>
```

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
- la web chat puo gia essere aperta su questa root sperimentale;
- il blocco viewer/simulatore visuale e disponibile nella pagina centrale;
- `13_build_viewer_model.py` genera `13_viewer_model.json`;
- `14_build_viewer_layout.py` genera `14_viewer_layout.json` come primo layout automatico grezzo;
- il renderer grafico e ancora basato sul prototipo `a01`, ma il layout e ora separato come contratto dati.

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

## Roadmap immediata

Lo stato attuale va letto cosi:

- la base tecnica `01-08` e consolidata;
- il manifest `10` e consolidato;
- la web chat `09`, l'agente `11` e gli scenari `12` sono attivi;
- gli esperimenti si gestiscono con root separate;
- il prossimo grande blocco non e un nuovo step di base, ma il viewer.

## Sintesi finale

La Pipeline 2.0 oggi va usata cosi:

```text
1. genero la base tecnica del circuito;
2. se serve, creo una root esperimento separata;
3. apro la chat locale;
4. faccio rispondere l'agente;
5. eseguo eventuali scenari su copie separate;
6. confronto base run e scenario run senza toccare l'originale.
```
