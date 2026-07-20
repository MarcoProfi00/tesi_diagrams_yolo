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

Variante di destinazione:

```powershell
python scripts\pipeline_2.0\prepare_experiment_outputs.py --batch batchA --experiment experiment4 --destination-variant chat --source-experiment experiment3_1 --circuits a01 a02 a04 a05 a06 a07 a08 a09 a10 --mode base-only
```

`--destination-variant` aggiunge una sottocartella tra esperimento e circuito.
La copia resta non distruttiva e il manifest registra anche la variante scelta.

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
- risolve `spice_override.node_refs` esclusivamente verso terminali gia
  presenti nel Graph JSON;
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

### Overlay SPICE dichiarativo nello YAML

Il Graph JSON non viene corretto o riscritto dalla Pipeline 2.0. Quando la
semantica elettrica richiede un arricchimento manuale, il singolo componente
puo dichiarare `spice_override` nel file valori:

- `node_order`: sceglie l'ordine di terminali gia disponibili, per esempio il
  secondario effettivo di un trasformatore equivalente;
- `terminal_map`: associa un pin elettrico atteso al terminale OCR validato,
  per esempio `C, B, E` di un BJT;
- `emit_as: subcircuit`, `pin_order` e `node_refs`: dichiarano in modo
  generale un dispositivo SPICE multipin.

Ogni `node_refs` deve citare un terminale del Graph. Se un pin indispensabile
non e ancora validato, l'override deve restare `pending`: lo step 06 produce
uno stato mancante e lo step 07 non emette un componente elettricamente
inventato.

Se la validazione immagine-graph dimostra un net merge errato, il YAML puo
aggiungere `spice_topology_overlay.terminal_node_overrides`. Ogni voce cita un
terminale esistente e un nodo SPICE nominato: modifica soltanto la vista
elettrica usata da 04-07, registra il passaggio in `04_values_bound.json` e
non riscrive mai il Graph JSON della Pipeline 1.0.

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
- gestisce i BJT `NPN_Transistor` e `PNP_Transistor` con ordine terminali
  SPICE `C, B, E`; il tipo effettivo e determinato dalla classe validata e dal
  modello dichiarato nel file valori.
- applica gli override YAML dichiarativi senza mutare il Graph sorgente;
- puo preparare una subcircuit a piu terminali quando tutti i `node_refs` sono
  risolti e il modello e disponibile.

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
- emette una subcircuit dichiarativa come elemento `X...`;
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

## Layer diagnostico, interattivo, viewer e autonomo 09-16

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
outputs/pipeline2.0/<batch>/<experiment>/<variant>/<circuit>/
```

L'opzione `--variant` e disponibile da CLI e richiede `--experiment`.
Con Experiment 4, se `--variant` non viene specificato, la stessa pagina
espone lo switch dinamico tra i workspace separati `chat` e `agent`.

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
- acquisisce geometry seed da Pipeline 1.0 (`03_estimate_terminals`);
- riconosce le istanze di subcircuito `X...` e ignora gli elementi interni
  compresi tra `.subckt` e `.ends`, che non appartengono allo schema utente;
- integra i `viewer_override` dello YAML senza modificare il Graph JSON.

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
- associa prima i terminali mediante i nomi logici dei pin, cosi dispositivi
  multipin come gli SCR mantengono anodo, catodo e gate distinti;
- sintetizza un pin dichiarato ma assente dalla geometria OCR prima di usare
  terminali geometrici residui;
- puo collocare una sorgente esterna tra due terminali del Graph dichiarati
  nello YAML, senza coordinate o identificativi di circuito nel codice;
- riserva una fascia destra stabile per la legenda del viewer;
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
  tooltip scenario, zoom/pan e scope transienti forniti dalla pagina web;
- disegnare SCR a tre terminali, trasformatori a due avvolgimenti e batterie
  esterne mediante primitive generali condivise da base, CHAT e AGENT.
- alleggerire le label tramite `viewer_override.label_mode` (`hidden`,
  `reference_only`, `value_only`) e spostare le informazioni descrittive nel
  `viewer_override.tooltip` SVG.
- posizionare i badge nodo su piu punti candidati e considerarli in collisione
  anche con le label dei bipoli, non soltanto con i simboli.

Principio:

- `13` descrive cosa esiste;
- `14` descrive dove posizionarlo;
- `15` descrive come disegnarlo;
- `09` deve solo mostrare il viewer della run selezionata.

Struttura interna condivisa:

```text
viewer_core/contracts.py          contratti e versioni degli artefatti
viewer_core/json_io.py            I/O JSON comune
viewer_core/component_library.py  catalogo dei componenti
viewer_core/model_builder.py      logica del modello
viewer_core/layout_builder.py     geometria e routing
viewer_core/svg_renderer.py       simboli e composizione SVG
viewer_core/svg_styles.py         CSS e animazioni SVG
```

I file `13_build_viewer_model.py`, `14_build_viewer_layout.py` e
`15_render_viewer_svg.py` sono gli entry point pubblici. Questa separazione
alleggerisce i comandi senza cambiare artefatti, CLI o integrazione web.

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
- set_initial_node_voltage
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
- per `set_initial_node_voltage` richiede `analysis: "tran"` ed emette una
  direttiva `.ic` senza sorgenti permanenti ne `UIC`;
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

## Experiment 4 - automazione implementata

Questa sezione descrive la prima versione implementata e validata in una prima
passata OpenAI su `a01`, `a02` e `a04`-`a10`; `a03` resta escluso per il noto
limite topologico/SPICE.

La stessa web app seleziona due workspace indipendenti:

```text
experiment4/chat/<circuit>
experiment4/agent/<circuit>
```

`09_web_chat.py` risolve il percorso `<experiment>/<variant>/<circuito>`. Per
Experiment 4, quando viene avviato senza `--variant`, espone nella stessa
sessione server lo switch tra `chat` e `agent`, mantenendo separati
conversazione, registry, scenari e run selezionata. Non usa un database.

Moduli implementati:

```text
scenario_runtime.py          # runtime condiviso per creare ed eseguire scenari
scenario_expectations.py     # criteri attesi condivisi tra contratto e confronto
16_autonomous_diagnosis.py   # una decisione/iterazione autonoma per chiamata
autonomous_agent/            # contratto, prompt, stato e controller separati
```

Dentro `autonomous_agent/`, `presentation.py` mantiene separata la UI dalla
logica decisionale. Produce il contratto generale `agent_view` leggendo stato,
`scenario.json`, `scenario_comparison.json`, output SPICE, viewer e presenza
del CSV transitorio. Non contiene condizioni per batch o circuiti specifici.

In `AGENT` la colonna destra mostra una dashboard persistente con avanzamento,
timeline dei test, azioni, evidenze e conclusione. I pulsanti delle schede
selezionano la run nel pannello centrale, dove rimangono viewer e grafici
`.tran`. In `CHAT` restano invariati renderer delle risposte, cronologia ed
esecuzione manuale degli scenari. Stili e renderer della dashboard vivono in
`web_chat/agent_view.css` e `web_chat/agent_view.js`, separati dal template
HTML generale.

Il runtime condiviso riusa gli step esistenti `10`-`15` ed e l'unica
implementazione del percorso:

```text
scenario validato
-> copia run separata
-> 12_controlled_scenarios.py
-> ngspice
-> scenario_comparison.json
-> 13/14/15
-> aggiornamento context, registry e history
```

Il controller autonomo accetta soltanto decisioni strutturate
`run_scenarios` o `stop`, esegue una iterazione alla volta e salva lo stato
in `experiment_chat/autonomous_diagnosis.json`.

Guardrail implementati:

- il budget conta soltanto scenari con SPICE realmente eseguito;
- scenari non validi o duplicati non consumano budget;
- `resolved_candidate` dello step 12 non equivale automaticamente a sintomo
  risolto;
- se l'utente chiede esplicitamente una correzione, l'agente non puo chiudere
  con la sola causa localizzata finche resta budget e non esiste una correzione
  verificata;
- il ciclo termina per stop motivato, limite di 5 run, assenza di azioni valide,
  errore non recuperabile o arresto utente;
- la base run e il workspace dell'altra modalita non vengono modificati.
- sono ammesse le nove primitive controllate `drive_node_voltage`,
  `set_initial_node_voltage`,
  `change_source_value`, `change_component_value`, `close_switch`,
  `connect_nodes`, `feed_nodes_from_source_node`,
  `add_voltage_source_between_nodes` e `add_resistor_between_nodes`;
- nuove sorgenti e nuovi rami vengono richiesti al modello soltanto in
  presenza di evidenze tecniche che li rendono diagnosticamente motivati;
- `feed_nodes_from_source_node` e riservata alla propagazione da un nodo gia
  alimentato; `connect_nodes` testa continuita generica e non puo sovrapporsi
  allo stesso feed nella medesima decisione;
- `add_resistor_between_nodes` non viene assimilata a questi collegamenti,
  perche modella un accoppiamento resistivo distinto;
- `set_initial_node_voltage` verifica un possibile equilibrio iniziale
  simmetrico soltanto in `tran`: non e una sorgente di alimentazione e non
  cambia il circuito della base run;
- quando l'obiettivo attiva, spegne o mantiene attivo un componente, `compare`
  deve includere una misura diretta `i(NOME_SPICE)` o `p(NOME_SPICE)` per il
  target e per gli eventuali componenti da preservare;
- i nomi delle misure dirette vengono ricavati da `07_netlist.cir`; le sole
  tensioni di nodo non bastano a dichiarare una correzione verificata;
- le nuove proposte autonome associano a `compare` un oggetto `expect`, per
  esempio `{"i(Rload)":"activated","i(Dled)":"unchanged"}`;
- ogni scenario autonomo dichiara obbligatoriamente `analysis: "op"` oppure
  `analysis: "tran"`; nel secondo caso le tensioni vengono confrontate sul
  Vpp ricavato da `08_tran.csv`;
- la mappa opzionale `measure` puo scegliere per ogni voce di `compare` la
  metrica `op`, `tran_vpp` oppure `tran_abs_peak`, quindi un singolo scenario
  puo verificare insieme un segnale AC e correnti o tensioni DC su altri rami;
- `tran_abs_peak` e riservata alle correnti interne `@dNOME[id]` dei diodi e
  LED esportate nel CSV: confronta il massimo valore assoluto della run e non
  il solo campione finale;
- nel registro CHAT una proposta `tran` che confronta `@dNOME[id]` viene
  accettata solo se dichiara esplicitamente quella misura, impedendo un fallback
  involontario al punto operativo;
- `tran_vpp` accetta `v(NODO)` e `v(NODO1,NODO2)`; la seconda forma calcola la
  tensione differenziale campione per campione prima di ricavare il Vpp ed e
  adatta a cuffie, altoparlanti e altri carichi non riferiti a massa;
- ogni scenario autonomo dichiara `intent: "correction"` oppure
  `intent: "diagnostic"`; un test diagnostico puo confermare un'ipotesi ma non
  produrre lo stop risolutivo senza criteri espliciti di correzione;
- anche il registro CHAT normalizza come `diagnostic` uno scenario legacy o
  una risposta priva di `intent`; soltanto `intent: "correction"` dichiarato
  esplicitamente puo produrre `stop_automation: true`;
- chiudere uno switch, alimentare un ramo o ottenere una corrente di sorgente
  non nulla resta diagnostico quando verifica solo una precondizione; per un
  sintomo audio o variabile la correzione deve osservare direttamente l'uscita
  in `tran`, con `tran_vpp` anche differenziale quando il carico ha due nodi;
- in analisi `tran`, correnti e potenze prive di una traccia CSV possono
  entrare in `expect` soltanto se dichiarate come `op` nella mappa `measure`;
- i sintomi che nominano esplicitamente AC o VAC impongono a una correzione
  almeno una misura `tran_vpp`; il solo punto di lavoro DC non e sufficiente;
- quando il sintomo riguarda l'accensione di un LED o di una lampada, almeno
  una loro corrente o potenza diretta deve comparire anche in `expect`;
- se il sintomo combina AC/VAC e LED/lampada, il contratto richiede nello stesso
  scenario sia `tran_vpp` sia una misura diretta `op` del componente;
- `expect: unchanged` e accettato solo se il sintomo chiede esplicitamente di
  preservare un altro componente o comportamento;
- `final_status: resolved` richiede una `verified_correction` non vuota;
- `final_status: localized` puo terminare dopo una conferma diagnostica forte,
  anche quando non esiste una riparazione fisica verificata;
- lo stop correttivo richiede almeno un effetto relativo del 10% oppure una
  vera attivazione/disattivazione; variazioni minori restano parziali;
- per sintomi di amplificazione, una correzione dichiara
  `gain: {"input":"v(NODO_IN)","output":"v(NODO_OUT)"}` e lo step 12 salva
  il guadagno base e scenario calcolato sui rispettivi Vpp;
- per test di propagazione o attenuazione, `gain` puo aggiungere
  `min_ratio`; se il rapporto Vpp uscita/ingresso resta sotto questa soglia
  dichiarata, lo scenario non conferma un trasferimento utile anche quando
  l'uscita passa da zero a un valore numericamente `changed`;
- `min_ratio` deve essere positivo e motivato dal singolo scenario: la pipeline
  non applica una soglia assoluta universale a circuiti e carichi diversi;
- nelle risposte CHAT sugli scenari eseguiti, `stop_automation=false` con
  budget residuo richiede una nuova proposta self-contained, salvo conclusione
  finale esplicitamente richiesta o dato esterno indispensabile mancante;
- una proposta non puo ripetere le stesse azioni con la stessa analisi soltanto
  per aggiungere `gain`, `measure`, `expect` o `min_ratio`; una stessa modifica
  e invece distinta e ammessa in `op` e in `tran` quando la seconda run verifica
  un comportamento temporale; dopo un trasferimento insufficiente deve cambiare
  il confine di isolamento o una causa elettrica verificata;
- i test di trasferimento riconosciuti nei flussi CHAT e AGENT richiedono
  `gain.min_ratio` positivo per essere accettati come scenari eseguibili;
- per distorsione o clipping con sorgente SIN, lo scenario dichiara
  quality=thd; transient_signal_quality.py analizza le ultime tre oscillazioni
  complete e calcola fondamentale, guadagno e THD sulle armoniche 2-5;
- lo stop richiede riduzione THD di almeno il 20%, THD finale al massimo del
  10% e conservazione del guadagno fondamentale;
- `i(Q...)` non viene accettata come misura diretta di un BJT: per osservare
  il ramo si usa una corrente disponibile, tipicamente quella della resistenza
  di collettore o di emettitore;
- `scenario_comparison.json` verifica ogni aspettativa e classifica lo scenario
  sui criteri soddisfatti; gli scenari storici senza `expect` mantengono la
  valutazione precedente;
- pin diversi dello stesso connector sono trattati come reti funzionali
  distinte finche gli artefatti non forniscono una ragione elettrica per unirli;
- nel viewer una sorgente scenario `SIN(...)`, `PULSE(...)` o equivalente usa
  il simbolo `signal_source`; soltanto una sorgente DC usa il simbolo batteria;
- i meter AC leggono il Vpp differenziale da `08_tran.csv`, mostrando stato
  attivo e valore `Vpp` anche quando il punto di lavoro medio vale zero;
- per sintomi di lampeggio, regolarita, duty cycle o durata di accensione, lo
  scenario dichiara `temporal_expect`; `scenario_runtime.py` confronta i
  profili transitori del viewer e richiede che stato, periodicita e soglie di
  duty siano soddisfatti prima di confermare una correzione;
- una sequenza temporale tra componenti richiede ancora un'estensione futura:
  oggi non viene verificata se la base contiene solo `.op` e manca `08_tran.csv`;
- ogni decisione contiene al massimo 2 scenari e il ciclo al massimo 8
  decisioni del modello;
- le run vengono eseguite in sequenza e sempre dalla base.

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
16_autonomous_diagnosis.py
scenario_runtime.py
scenario_expectations.py
transient_signal_quality.py
```

Presenti ma non ancora integrati nel flusso reale:

```text
05_device_profiles.py
```

Non fanno parte dello stato attuale di riferimento:

- `09_summarize_spice.py` non va piu considerato uno step reale della pipeline
  corrente;
- il riferimento ufficiale oggi e la catena `01-08` + `10` per la parte base e
  `09-16` per il layer diagnostico, interattivo, viewer e autonomo.

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
- `09-16` permettono di interrogarli, testarli, visualizzarli e confrontarli
  senza perdere la base run originale.
