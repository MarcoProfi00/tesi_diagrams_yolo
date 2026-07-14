# Pipeline 2.0 - riferimento script

Questo documento descrive gli script reali oggi usati nella Pipeline 2.0.

Non e un piano futuro: deve restare allineato al codice effettivamente presente
in `scripts/pipeline_2.0/`.

La Pipeline 2.0 parte dai Graph JSON della Pipeline 1.0 e oggi copre due
blocchi distinti:

```text
1. pipeline tecnica 01-08
   Graph JSON -> netlist SPICE -> ngspice

2. layer diagnostico/interattivo 09-12
   web chat -> contesto diagnostico -> agente -> scenari controllati
```

## Struttura generale

Script principali:

```text
scripts/pipeline_2.0/
|-- run_pipeline2.py
|-- prepare_experiment_outputs.py
`-- json_to_spice/
    |-- 01_io.py
    |-- 02_normalize.py
    |-- 03_node_map.py
    |-- 04_values.py
    |-- 05_device_profiles.py
    |-- 06_component_rules.py
    |-- 07_spice_emit.py
    |-- 08_spice_run.py
    |-- 09_web_chat.py
    |-- 10_build_diagnostic_context.py
    |-- 11_agent_readonly.py
    `-- 12_controlled_scenarios.py
```

Output possibili:

```text
outputs/pipeline2.0/<batch>/<circuit>/
outputs/pipeline2.0/<batch>/<experiment>/<circuit>/
```

La seconda forma serve quando vogliamo separare esperimenti diversi mantenendo
indipendenti chat, scenari, conclusioni e artefatti diagnostici.

Convenzione attuale:

- `outputs/pipeline2.0/<batch>/<circuit>/` resta la root canonica della run
  tecnica di base;
- `outputs/pipeline2.0/<batch>/<experiment>/<circuit>/` resta una root
  sperimentale separata, utile per congelare snapshot, confrontare varianti e
  mantenere indipendenti chat/scenari;
- nel Batch A teniamo volutamente entrambe le forme: la root canonica
  `a01...a10` e le cartelle esperimento come `experiment1`, `experiment2` e
  `experiment2_feed_nodes`.

## Due famiglie di script

### 1. Script di pipeline tecnica

Sono gli script che costruiscono gli output elettrici di base:

```text
01_io
02_normalize
03_node_map
04_values
05_device_profiles   # non ancora attivo nel flusso reale
06_component_rules
07_spice_emit
08_spice_run
```

Questa parte produce la base tecnica del circuito.

### 2. Script diagnostici e interattivi

Sono gli script che lavorano sopra una base gia generata:

```text
09_web_chat
10_build_diagnostic_context
11_agent_readonly
12_controlled_scenarios
```

Questa parte non sostituisce la pipeline tecnica. La usa come evidenza.

## Script orchestration

## run_pipeline2.py

Path:

```text
scripts/pipeline_2.0/run_pipeline2.py
```

Ruolo:

- e il punto di ingresso della Pipeline 2.0;
- carica dinamicamente gli step numerati;
- esegue gli step tecnici nell'ordine corretto;
- opzionalmente esegue ngspice;
- alla fine costruisce anche `10_diagnostic_context.json`.

Step oggi caricati davvero dal codice:

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

Nota importante:

- `05_device_profiles.py` esiste come scheletro, ma non viene ancora invocato
  da `run_pipeline2.py`;
- `09`, `11` e `12` non fanno parte della pipeline batch principale: si usano
  separatamente.

Input principali:

```text
outputs/pipeline1.0/<batch>/06_graph_report/<circuit>/<circuit>.json
metadata/pipeline2_manual_values/<batch>/<circuit>_values.yaml
metadata/pipeline2_spice_classes.yaml
metadata/pipeline2_spice_models.yaml
```

Output tipici:

```text
01_graph.json
02_normalized_circuit.json
03_node_map.json
04_values_bound.json
06_component_rules.json
07_netlist.cir
07_spice_emit_report.json
08_spice_run.json                  # se --run-spice
08_ngspice_stdout.txt              # se --run-spice
08_ngspice_stderr.txt              # se --run-spice
08_tran.csv / 08_tran_plot.*       # se disponibili
10_diagnostic_context.json
```

Comando tipico:

```powershell
python scripts\pipeline_2.0\run_pipeline2.py --batch batchA --circuits a01 a02 --run-spice --ngspice-executable ngspice_con
```

Supporta anche:

```text
--experiment <name>
```

per scrivere direttamente in:

```text
outputs/pipeline2.0/<batch>/<experiment>/<circuit>/
```

## prepare_experiment_outputs.py

Path:

```text
scripts/pipeline_2.0/prepare_experiment_outputs.py
```

Ruolo:

- prepara una root esperimento separata;
- copia in modo non distruttivo artefatti gia esistenti;
- permette di separare completamente due esperimenti senza rigenerare sempre la
  pipeline tecnica.

Modalita:

```text
base-only
full
```

`base-only`:

- copia solo i file top-level `01-08`;
- non copia `10`, `11`, `scenarios` o chat history;
- serve quando vogliamo ripartire da una stessa base tecnica con una nuova
  sessione sperimentale pulita.

`full`:

- copia tutta la cartella circuito;
- serve quando vogliamo congelare uno stato sperimentale completo.

Output aggiuntivo locale:

```text
experiment_manifest.json
```

Comando tipico:

```powershell
python scripts\pipeline_2.0\prepare_experiment_outputs.py --batch batchA --experiment experiment2 --circuits a01 a02 a03 --mode base-only
```

## Pipeline tecnica 01-08

## 01_io.py

Path:

```text
scripts/pipeline_2.0/json_to_spice/01_io.py
```

Ruolo:

- centralizza percorsi e I/O della Pipeline 2.0;
- trova il Graph JSON della Pipeline 1.0;
- prepara la cartella output del circuito;
- copia il Graph JSON sorgente nella nuova cartella;
- fornisce helper comuni per lettura/scrittura JSON.

Input principale:

```text
outputs/pipeline1.0/<batch>/06_graph_report/<circuit>/<circuit>.json
```

Output:

```text
01_graph.json
```

Perche e importante:

senza questo step ogni modulo gestirebbe path e cartelle in modo diverso.

## 02_normalize.py

Path:

```text
scripts/pipeline_2.0/json_to_spice/02_normalize.py
```

Ruolo:

- normalizza il Graph JSON in una struttura piu ordinata;
- costruisce lookup per componenti e terminali;
- esplicita il grafo terminale-terminale;
- registra statistiche e warning di normalizzazione.

Input:

```text
01_graph.json
```

Output:

```text
02_normalized_circuit.json
```

Perche serve:

il JSON della Pipeline 1.0 e topologicamente utile, ma non ancora comodo da
usare per i passaggi elettrici successivi.

## 03_node_map.py

Path:

```text
scripts/pipeline_2.0/json_to_spice/03_node_map.py
```

Ruolo:

- costruisce i nodi elettrici a partire dal grafo normalizzato;
- trova le componenti connesse;
- assegna un nodo SPICE a ogni gruppo di terminali;
- mappa i terminali di massa nel nodo `0`.

Input:

```text
02_normalized_circuit.json
```

Output:

```text
03_node_map.json
```

Perche serve:

SPICE ragiona in termini di nodi, non di linee disegnate.

## 04_values.py

Path:

```text
scripts/pipeline_2.0/json_to_spice/04_values.py
```

Ruolo:

- legge i valori manuali dal file YAML;
- associa valori, modelli e stati ai componenti;
- gestisce anche supply manuali e stato degli switch;
- distingue componenti `bound`, mancanti o non supportati.

Input:

```text
02_normalized_circuit.json
03_node_map.json
metadata/pipeline2_manual_values/<batch>/<circuit>_values.yaml
```

Output:

```text
04_values_bound.json
```

Perche serve:

la topologia da sola non basta a generare una netlist utilizzabile.

## 05_device_profiles.py

Path:

```text
scripts/pipeline_2.0/json_to_spice/05_device_profiles.py
```

Stato reale:

```text
scheletro presente, non ancora integrato nel flusso run_pipeline2.py
```

Ruolo previsto:

- descrivere componenti complessi e IC tramite profili dichiarativi;
- modellare pin di alimentazione, GND, reset, clock, enable, ingressi e uscite;
- supportare controlli pin-aware nei batch futuri.

Output previsto:

```text
05_device_profiles.json
```

Nota:

oggi questo step va considerato documentato ma non operativo nel flusso reale.

## 06_component_rules.py

Path:

```text
scripts/pipeline_2.0/json_to_spice/06_component_rules.py
```

Ruolo:

- applica il mapping in `metadata/pipeline2_spice_classes.yaml`;
- decide come trattare ogni componente in SPICE;
- distingue componenti emettibili, strutturali, mancanti, semplificati o non
  supportati;
- prepara prefissi, nodi e parametri da usare nello step 07.

Input:

```text
04_values_bound.json
metadata/pipeline2_spice_classes.yaml
```

Output:

```text
06_component_rules.json
```

Perche serve:

non tutti i componenti del graph devono diventare una riga SPICE.

## 07_spice_emit.py

Path:

```text
scripts/pipeline_2.0/json_to_spice/07_spice_emit.py
```

Ruolo:

- genera la netlist SPICE vera e propria;
- emette resistenze, condensatori, sorgenti, LED, lampade equivalenti e altri
  elementi supportati;
- commenta o salta componenti strutturali e non emettibili;
- aggiunge modelli `.model` quando servono;
- aggiunge `.op` e, se richiesto, anche `.tran`;
- salva anche un report di emissione.

Input:

```text
06_component_rules.json
metadata/pipeline2_spice_models.yaml
```

Output:

```text
07_netlist.cir
07_spice_emit_report.json
```

Perche serve:

e il punto in cui la rappresentazione elettrica interna diventa una netlist
leggibile da ngspice.

## 08_spice_run.py

Path:

```text
scripts/pipeline_2.0/json_to_spice/08_spice_run.py
```

Ruolo:

- esegue ngspice in batch mode;
- cerca un eseguibile disponibile o usa quello passato da CLI;
- salva stdout, stderr, exit code e report;
- genera anche il plot transitorio se i dati `.tran` sono disponibili.

Input:

```text
07_netlist.cir
```

Output:

```text
08_spice_run.json
08_ngspice_stdout.txt
08_ngspice_stderr.txt
08_tran.csv
08_tran_plot.png
08_tran_plot.svg
```

Perche serve:

verifica se la netlist prodotta e davvero eseguibile e conserva il risultato
grezzo della simulazione.

Nota importante:

`08_spice_run.py` non interpreta la diagnosi. Esegue e salva.

## Layer diagnostico, interattivo e viewer 09-15

## 09_web_chat.py

Path:

```text
scripts/pipeline_2.0/json_to_spice/09_web_chat.py
```

Ruolo:

- avvia un server locale temporaneo;
- mostra gli artefatti del circuito in una pagina web;
- mantiene una chat diagnostica sempre visibile;
- chiama lo step 10 per aggiornare il contesto;
- chiama lo step 11 per ottenere la risposta dell'agente;
- riconosce richieste come `esegui scenario 1`, `esegui l'ultimo`,
  `mostra scenari`;
- chiama lo step 12 per eseguire scenari su copie separate.
- genera o aggiorna gli step viewer `13`, `14` e `15` per la run visualizzata e
  per ogni nuova run scenario.

Caratteristiche architetturali:

- niente database;
- niente backend persistente complesso;
- niente API pubbliche;
- server solo locale e temporaneo.

Artefatti chat principali:

```text
11_agent_input_preview_chat.md
11_agent_prompt_chat.md
11_agent_response_chat.md
```

Per root `experiment2*` salva anche memoria ufficiale locale:

```text
experiment2_chat/chat_history.json
experiment2_chat/chat_history.md
experiment2_chat/scenario_registry.json
experiment2_chat/scenario_registry.md
```

In questa modalita:

- `chat_history.json` e la sorgente ufficiale della conversazione;
- `scenario_registry.json` e la sorgente ufficiale degli scenari proposti ed
  eseguiti;
- il bottone `Clear` resetta chat, registry, cartelle `scenarios/` e artefatti
  chat 10/11 della sessione, ma non tocca i file base `01-08`.

Sessione Experiment 3.1:

- `experiment3_1` usa lo stesso meccanismo di history e registry della chat;
- salva i file in `experiment_chat/` per non attribuirli artificialmente
  all'Esperimento 2;
- le root `experiment2*` conservano `experiment2_chat/` per compatibilita.

Input:

```text
outputs/pipeline2.0/<batch>/<circuit>/
outputs/pipeline2.0/<batch>/<experiment>/<circuit>/
```

Output:

- risposta visibile in chat;
- file chat `11_*_chat.md`;
- eventuale `10_diagnostic_context.json` aggiornato;
- eventuali cartelle `scenarios/scenario_<n>/`.

Comando tipico:

```powershell
python scripts\pipeline_2.0\json_to_spice\09_web_chat.py --batch batchA --experiment experiment2 --circuit a01 --ngspice-executable "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

Comando per aprire la workspace di Experiment 3 sul circuito pilota `a01`:

```powershell
python scripts\pipeline_2.0\json_to_spice\09_web_chat.py --batch batchA --experiment experiment3_viewer --circuit a01 --ngspice-executable "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

Nota:

- questo comando apre gli output in `outputs/pipeline2.0/batchA/experiment3_viewer/a01/`;
- la web chat mostra gia base run, immagine, artefatti e scenari disponibili;
- il viewer/simulatore visuale viene mostrato come blocco aggiuntivo della pagina centrale;
- `13_viewer_model.json` descrive cosa esiste nella run;
- `14_viewer_layout.json` descrive layout, terminali e route automatiche;
- `15_viewer.svg` e il viewer SVG generale mostrato nel pannello centrale.

Nota architetturale:

- il viewer e `netlist-grounded + image-guided`;
- bbox e terminali della Pipeline 1.0 sono geometry seed, non verita elettrica;
- `09_web_chat.py` non contiene coordinate o renderer di singoli circuiti;
- modello, layout e rendering derivano da `13_viewer_model.json`,
  `14_viewer_layout.json` e `15_viewer.svg`.

## 13_build_viewer_model.py

Path:

```text
scripts/pipeline_2.0/json_to_spice/13_build_viewer_model.py
```

Ruolo:

- costruisce il contratto dati del viewer per una base run o una scenario run;
- parte dalla netlist realmente simulata in `07_netlist.cir`;
- aggiunge contesto strutturale da `03_node_map.json` e `06_component_rules.json`;
- aggiunge misure operative e transienti da `08_*`;
- acquisisce geometry seed da Pipeline 1.0 (`03_estimate_terminals`).

Output:

```text
13_viewer_model.json
```

Comando:

```powershell
python scripts\pipeline_2.0\json_to_spice\13_build_viewer_model.py --run-dir outputs\pipeline2.0\batchA\experiment3_viewer\a01
```

Nota:

- lo step 13 dice cosa deve essere rappresentato;
- non contiene coordinate SVG o regole grafiche.

## 14_build_viewer_layout.py

Path:

```text
scripts/pipeline_2.0/json_to_spice/14_build_viewer_layout.py
```

Ruolo:

- legge `13_viewer_model.json`;
- normalizza bbox e terminali sul canvas viewer;
- assegna posizioni a componenti, nodi, pin e connessioni;
- calcola routes e fallback per componenti scenario senza bbox;
- prepara la separazione tra modello elettrico e coordinate SVG.

Output:

```text
14_viewer_layout.json
```

Comando:

```powershell
python scripts\pipeline_2.0\json_to_spice\14_build_viewer_layout.py --run-dir outputs\pipeline2.0\batchA\experiment3_viewer\a01
```

Nota:

- il layout non ricostruisce l'immagine originale pixel-perfect;
- e la base del renderer generale per tutti i circuiti e scenari;
- include route ortogonali, fallback scenario e ponti per attraversamenti senza
  giunzione elettrica.

## 15_render_viewer_svg.py

Path:

```text
scripts/pipeline_2.0/json_to_spice/15_render_viewer_svg.py
```

Ruolo:

- leggere `13_viewer_model.json`;
- leggere `14_viewer_layout.json`;
- applicare il vocabolario dei componenti grafici;
- produrre `15_viewer.svg` embeddabile nella web chat;
- usare il vocabolario componenti comune, animazioni elettriche, legenda,
  tooltip scenario, zoom/pan e scope transienti forniti dalla pagina web.

Principio:

- `13` descrive cosa esiste;
- `14` descrive dove posizionarlo;
- `15` descrive come disegnarlo;
- `09` deve solo mostrare il viewer della run selezionata.

Copertura Experiment 3:

```text
a01 -> a10/a09 -> a02/a05/a07 -> a08 -> a04/a06
```

Ogni nuovo circuito deve aggiungere regole generali di modello/layout/rendering,
non un renderer dedicato.

## 10_build_diagnostic_context.py

Path:

```text
scripts/pipeline_2.0/json_to_spice/10_build_diagnostic_context.py
```

Ruolo:

- costruisce un manifest diagnostico leggero;
- non duplica tutti gli output in un file enorme;
- indica all'agente dove si trovano i file reali;
- riassume lo stato minimo del circuito;
- indicizza gli scenari gia eseguiti;
- costruisce anche una sintesi dell'esito scenari e un budget massimo.

Output:

```text
10_diagnostic_context.json
```

Contiene soprattutto:

- `summary`
- `artifacts`
- `executed_scenarios`
- `scenario_outcome_summary`
- `scenario_budget`
- `image_access`
- `agent_rules`

Perche serve:

lo step 11 parte da questo manifest, non da un hardcoding di file sparsi.

Nota importante:

oggi questo step e gia reale e viene chiamato sia da `run_pipeline2.py` sia da
`09_web_chat.py`.

## 11_agent_readonly.py

Path:

```text
scripts/pipeline_2.0/json_to_spice/11_agent_readonly.py
```

Ruolo:

- legge `10_diagnostic_context.json`;
- carica gli artefatti indicati dal manifest;
- costruisce un preview ordinato dell'input agente;
- costruisce il prompt finale;
- chiama OpenAI solo se richiesto esplicitamente;
- non modifica netlist e non esegue scenari.

Output base:

```text
11_agent_input_preview.md
11_agent_prompt.md
```

Con `--run-agent`:

```text
11_agent_response.md
```

Supporta:

- risoluzione del context per batch/circuito;
- root esperimento separata;
- scelta modello;
- domanda utente da CLI.

Modelli attualmente previsti dal codice e dalla chat:

```text
gpt-5.4
gpt-5.5
gpt-5.4-mini
gpt-5-mini
```

Perche si chiama read-only:

- interpreta;
- spiega;
- propone scenari;
- ma non tocca mai gli output tecnici.

Comando tipico:

```powershell
python scripts\pipeline_2.0\json_to_spice\11_agent_readonly.py --batch batchA --experiment experiment2 --circuit a01 --question "Perche la lampada non si accende?" --run-agent --model gpt-5.4
```

## 12_controlled_scenarios.py

Path:

```text
scripts/pipeline_2.0/json_to_spice/12_controlled_scenarios.py
```

Ruolo:

- applica uno scenario solo dentro una cartella scenario separata;
- modifica soltanto `run/07_netlist.cir`;
- opzionalmente rilancia ngspice sulla run scenario;
- costruisce un confronto base vs scenario;
- aggiorna `scenario_status.json`.

Regola centrale:

```text
la base run non viene mai modificata
```

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

Primitive oggi supportate:

```text
Scenari elettrici / di pilotaggio:
- drive_node_voltage
- add_voltage_source_between_nodes
- change_source_value
- change_component_value
- close_switch

Scenari topologici controllati:
- connect_nodes
- add_resistor_between_nodes
- feed_nodes_from_source_node
```

Responsabilita aggiuntive:

- valida i nodi richiesti dallo scenario;
- normalizza valori SPICE;
- limita il budget a massimo `5` scenari eseguibili per circuito;
- crea `scenario_comparison.json`;
- classifica automaticamente l'esito con categorie come:
  - `resolved_candidate`
  - `partially_resolved`
  - `not_resolved`
  - `unknown`

Output principali:

```text
12_controlled_scenarios.json
scenario_status.json
scenario_comparison.json
```

Comando tipico:

```powershell
python scripts\pipeline_2.0\json_to_spice\12_controlled_scenarios.py --scenario-dir outputs\pipeline2.0\batchA\experiment2\a01\scenarios\scenario_1 --run-spice --ngspice "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

## Flussi reali oggi supportati

## Flusso 1 - pipeline tecnica base

```text
run_pipeline2.py
-> 01_io
-> 02_normalize
-> 03_node_map
-> 04_values
-> 06_component_rules
-> 07_spice_emit
-> 08_spice_run          # se richiesto
-> 10_build_diagnostic_context
```

## Flusso 2 - chat diagnostica locale

```text
09_web_chat
-> aggiorna 10_diagnostic_context.json
-> costruisce 11_agent_input_preview_chat.md
-> costruisce 11_agent_prompt_chat.md
-> chiama il runner agente
-> salva 11_agent_response_chat.md
```

## Flusso 3 - scenario controllato da chat

```text
utente sceglie uno scenario
-> 09_web_chat recupera il JSON scenario
-> crea scenarios/<scenario_id>/
-> copia base_snapshot/ e run/
-> chiama 12_controlled_scenarios.py
-> opzionalmente esegue ngspice sulla run scenario
-> costruisce scenario_comparison.json
-> genera 13_viewer_model.json
-> genera 14_viewer_layout.json
-> genera 15_viewer.svg
-> agente puo leggere il nuovo esito
```

## Stato attuale degli script

Implementati e usati davvero:

```text
run_pipeline2.py
prepare_experiment_outputs.py
01_io.py
02_normalize.py
03_node_map.py
04_values.py
06_component_rules.py
07_spice_emit.py
08_spice_run.py
09_web_chat.py
10_build_diagnostic_context.py
11_agent_readonly.py
12_controlled_scenarios.py
13_build_viewer_model.py
14_build_viewer_layout.py
15_render_viewer_svg.py
```

Presenti ma non ancora integrati nel flusso reale:

```text
05_device_profiles.py
```

Non fanno parte dello stato attuale di riferimento:

- `09_summarize_spice.py` non va piu considerato uno step reale della pipeline
  corrente;
- il riferimento ufficiale oggi e la catena `01-08` + `10` per la parte base e
  `09-15` per il layer diagnostico, interattivo e viewer.

## Quando aggiornare questo file

Questo riferimento va aggiornato quando:

- cambia l'ordine o il ruolo di uno script;
- `run_pipeline2.py` inizia a caricare nuovi step;
- `05_device_profiles.py` entra davvero nel flusso;
- vengono aggiunte o rimosse primitive scenario in `12_controlled_scenarios.py`;
- cambia la struttura output per batch/esperimento/circuito;
- cambia il contratto `13/14/15` o il vocabolario grafico del viewer;
- la web chat introduce nuove responsabilita strutturali.

## Sintesi finale

La Pipeline 2.0 oggi va letta cosi:

```text
run_pipeline2.py e il motore della base tecnica;
prepare_experiment_outputs.py separa gli esperimenti;
09_web_chat.py e l'interfaccia locale;
10_build_diagnostic_context.py costruisce il manifest;
11_agent_readonly.py interpreta senza modificare;
12_controlled_scenarios.py applica scenari su copie separate.
13/14/15 costruiscono modello, layout e SVG della run selezionata.
```

Questa distinzione e importante per tutta la tesi:

- `01-08` costruiscono i fatti elettrici;
- `09-15` permettono di interrogarli, testarli, visualizzarli e confrontarli
  senza perdere la base run originale.
