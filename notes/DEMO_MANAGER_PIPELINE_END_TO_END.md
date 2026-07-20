# Demo manager - automazione modulare Pipeline 1.0 e Pipeline 2.0

## Stato del documento

- Data di avvio: 20 luglio 2026.
- Scadenza demo: mercoledì 22 luglio 2026.
- Stato: progettazione dell'orchestrazione.
- Obiettivo immediato: collegare gli script esistenti senza riscrivere gli
  algoritmi delle due pipeline.

## Obiettivo della demo

La demo deve mostrare un flusso reale e ripetibile che parte dall'immagine di
un circuito già validato e può arrivare fino alla simulazione e alla diagnosi:

```text
immagine
-> Pipeline 1.0
-> Graph JSON
-> YAML manuale dei valori
-> Pipeline 2.0
-> netlist SPICE
-> ngspice
-> viewer
-> CHAT / AGENT
```

L'esecuzione completa deve essere semplice, ma non obbligatoria. L'utente deve
poter fermare il flusso dopo Pipeline 1.0, dopo SPICE o dopo il viewer.

Decisione confermata per l'interfaccia pubblica:

```text
graph
  esegue soltanto Pipeline 1.0 e produce il Graph JSON

spice
  parte da un Graph JSON esistente, esegue Pipeline 2.0 fino a ngspice e si ferma

webchat --mode chat|agent
  parte da una base SPICE esistente e apre direttamente la modalità richiesta
```

L'utente non deve essere obbligato a rieseguire gli step precedenti.

## Principi da rispettare

1. Nessun hardcode per Batch A, Batch B o un circuito specifico.
2. Gli script esistenti restano eseguibili anche singolarmente.
3. L'orchestratore coordina gli script: non duplica la loro logica.
4. ngspice resta il motore di verità per i risultati elettrici.
5. I valori dei componenti restano manuali e tracciabili nello YAML.
6. La demo usa circuiti già validati e YAML già esistenti.
7. Gli output ufficiali di Batch A e Batch B non devono essere sovrascritti.
8. Ogni step deve dichiarare chiaramente successo, warning o errore.
9. Tutti i nuovi script, funzioni e metodi devono avere commenti in italiano.
10. Deve essere possibile riprendere una demo da uno step già completato.

## Cosa non automatizziamo adesso

Per la demo non cerchiamo di risolvere automaticamente problemi ancora aperti
di ricerca:

- lettura OCR affidabile di tutti i valori;
- generazione automatica dello YAML per immagini nuove;
- correzione autonoma di Graph JSON non validati;
- supporto universale per qualunque nuovo componente;
- judge e statistiche di Experiment 4/5;
- esecuzione automatica di una conversazione completa con domande prefissate.

L'automazione esegue la pipeline. Non deve inventare valori o correggere in
silenzio una topologia incerta.

## Circuiti candidati

Per la demo sceglieremo due o tre circuiti tra quelli già validati.

### Candidato principale: A08

Punti forti:

- circuito abbastanza compatto;
- sorgente impulsiva e transitorio;
- LED con comportamento visibile;
- YAML già presente;
- scenario diagnostico facilmente comprensibile.

Uso previsto: mostrare l'intero percorso e il comportamento temporale.

### Candidato visuale: B02

Punti forti:

- multivibratore astabile;
- due LED alternati;
- viewer molto efficace per una presentazione;
- CHAT e AGENT già validati.

Rischio da verificare:

- durante Experiment 5 il Graph e la polarità dei condensatori sono stati
  controllati e corretti; un nuovo passaggio di Pipeline 1.0 deve essere
  confrontato con il Graph validato prima di usarlo dal vivo.

### Candidato alternativo: B03

Punti forti:

- tre LED di colori diversi;
- prove statiche e transitorie;
- risultato visivo immediato;
- YAML e modelli SPICE già preparati.

Rischio:

- circuito più ricco di componenti e quindi più esposto a differenze nella
  detection rispetto ad A08.

### Decisione finale sui circuiti

La scelta definitiva verrà fatta dopo uno smoke test end-to-end. Per la demo
si userà:

- un circuito principale;
- un secondo circuito di confronto;
- un terzo circuito come fallback già precomputato.

## Workspace isolato per la demo

Le immagini e gli YAML possono provenire da Batch A o Batch B, ma una nuova
esecuzione non deve scrivere nelle cartelle ufficiali validate.

Decisione: ogni circuito dimostrativo usa un workspace persistente e
autosufficiente, identificato da un nome stabile scelto dall'utente.

```text
outputs/demo_workspaces/<workspace_id>/
|-- workspace_manifest.json
|-- input/
|   |-- circuit_image.<ext>
|   `-- values.yaml
|-- pipeline1.0/
|   |-- 01_detect_components/
|   |-- 02_assign_instances/
|   |-- 03_estimate_terminals/
|   |-- 04_extract_wires/
|   |-- 05_build_terminal_graph/
|   `-- 06_graph_report/
|-- pipeline2.0/
|   `-- base/
|       |-- 01_graph.json
|       |-- ...
|       |-- 08_spice_run.json
|       `-- 10_diagnostic_context.json
|-- web/
|   |-- chat/
|   `-- agent/
`-- logs/
```

Esempio:

```text
outputs/demo_workspaces/manager_a08/
```

Il comando `graph` crea il workspace e completa soltanto `pipeline1.0/`. Il
giorno successivo `spice --workspace manager_a08` legge il Graph dal manifest
e completa `pipeline2.0/base/`. In un momento ancora successivo,
`webchat --workspace manager_a08 --mode agent` crea o riapre soltanto
`web/agent/`.

Lo YAML sorgente resta quello ufficiale:

```text
metadata/pipeline2_manual_values/batchA/a08_values.yaml
metadata/pipeline2_manual_values/batchB/b02_values.yaml
```

Alla prima esecuzione di `spice` viene copiato in `input/values.yaml`; il
manifest conserva sia il path sorgente sia l'hash della copia. Gli step
successivi usano la copia del workspace e non dipendono dallo YAML esterno.

Allo stesso modo, `graph` copia l'immagine in `input/` e registra path sorgente
e hash. Il workspace può quindi essere riaperto anche in un giorno diverso
senza dover ricostruire il comando originale.

### Regole di persistenza e ripresa

- Ogni comando riceve `--workspace <workspace_id>`.
- Il manifest è il contratto tra Pipeline 1.0, Pipeline 2.0 e webchat.
- `spice` richiede che lo stato `pipeline1` sia `completed`.
- `webchat` richiede che lo stato `spice` sia `completed`.
- CHAT e AGENT sono copie indipendenti della stessa base SPICE.
- Riaprire AGENT non modifica CHAT e viceversa.
- Un comando non sovrascrive artefatti completati senza `--force`.
- Gli output parziali restano ispezionabili e il manifest indica lo step
  preciso da cui ripartire.
- Hash di immagine, Graph e YAML impediscono di combinare per errore artefatti
  appartenenti a circuiti o revisioni diverse.

## Architettura dell'orchestratore

Si propone un launcher unico con tre sottocomandi pubblici principali,
mantenendo comunque disponibili gli script originali.

Path previsto:

```text
scripts/run_full_pipeline.py
```

Sottocomandi pubblici:

```text
graph
spice
webchat
```

Sono ammesse anche le scorciatoie di servizio `preflight` e `all`. La seconda
concatena i tre comandi pubblici, ma non è il solo modo supportato di usare il
sistema.

### Preflight condiviso

Controlla senza eseguire la pipeline:

- interprete Python;
- import di OpenCV, NumPy, scikit-image, matplotlib e ultralytics;
- modello YOLO;
- metadata delle classi;
- immagine sorgente;
- YAML manuale;
- eseguibile ngspice;
- disponibilità di `OPENAI_API_KEY` o di un `.env` locale;
- porte disponibili per la webchat.

La chiave API non deve mai essere stampata.

### `graph`

Esegue in ordine:

```text
01_detect_components.py
02_assign_instances.py
03_estimate_terminals.py
04_extract_wires.py
05_build_terminal_graph.py
06_render_graph_report.py
```

Output finale richiesto:

```text
outputs/demo_workspaces/<workspace_id>/pipeline1.0/06_graph_report/<circuit>/<circuit>.json
```

Al termine deve mostrare:

- componenti riconosciuti;
- terminali isolati o non associati;
- warning del Graph;
- path del report HTML e del Graph JSON;
- esito del checkpoint Pipeline 1.0.

L'utente può fermarsi qui e ispezionare il Graph. Questo comando non richiede
lo YAML, ngspice o la chiave OpenAI.

### `spice`

Prerequisiti:

- Graph JSON prodotto dalla Pipeline 1.0;
- YAML manuale scelto esplicitamente;
- file globali delle classi e dei modelli SPICE.

Esegue:

```text
01_io
02_normalize
03_node_map
04_values
06_component_rules
07_spice_emit
08_spice_run
10_build_diagnostic_context
```

Al termine deve mostrare:

- componenti con valore associato;
- componenti mancanti o non supportati;
- warning di emissione;
- path della netlist;
- stato ngspice ed exit code;
- presenza di analisi OP e/o TRAN;
- path del contesto diagnostico.

La modalità standard della demo deve considerare ngspice obbligatorio. Il
comando non apre il browser e non richiede la chiave OpenAI.

### Viewer come preparazione della webchat

Esegue gli step:

```text
13_build_viewer_model
14_build_viewer_layout
15_render_viewer_svg
```

Gli step possono essere richiamati internamente da `webchat`. Non serve
necessariamente esporre un quarto comando pubblico per la demo.

### Preparazione automatica dei workspace web

Prepara due workspace isolati copiando soltanto la base tecnica:

```text
.../<experiment>/chat/<circuit>/
.../<experiment>/agent/<circuit>/
```

Questa fase sostituisce i due comandi manuali attualmente necessari con
`prepare_experiment_outputs.py`.

### `webchat --mode chat|agent`

Parte da una base SPICE esistente, prepara il workspace richiesto e avvia
`09_web_chat.py`, aprendo il browser direttamente nella modalità selezionata.

```text
--mode chat
  usa la copia CHAT e abilita l'interazione guidata

--mode agent
  usa la copia AGENT e apre la modalità autonoma
```

Il comando non deve rieseguire Pipeline 1.0 o SPICE, salvo richiesta esplicita.
CHAT e AGENT devono continuare a usare copie indipendenti della stessa base.

La webchat deve riconoscere automaticamente una root con varianti `chat` e
`agent`, senza dipendere dai nomi hardcoded `experiment4` o `experiment5`.

### `all`

Esegue:

```text
preflight
-> graph
-> checkpoint Graph
-> spice
-> viewer
-> preparazione workspace
-> webchat
```

Prima della Pipeline 2.0 può essere previsto un flag per richiedere conferma
manuale dopo l'ispezione del Graph.

## Controllo degli step

I tre comandi pubblici rappresentano già i checkpoint principali. Il launcher
deve inoltre accettare almeno queste opzioni trasversali:

```text
--no-browser
--dry-run
--force
```

Non è obbligatorio che tutta la demo avvenga in un singolo processo. È invece
obbligatorio che i passaggi siano collegati da contratti chiari e che un output
valido possa diventare l'input dello step successivo.

## Contratto CLI desiderato

Esempio Pipeline 1.0 soltanto:

```powershell
python scripts\run_full_pipeline.py graph `
  --workspace manager_a08 `
  --image data\batchA\a08.jpg `
  --circuit a08
```

Esempio ripresa dalla Pipeline 2.0:

```powershell
python scripts\run_full_pipeline.py spice `
  --workspace manager_a08 `
  --values-yaml metadata\pipeline2_manual_values\batchA\a08_values.yaml `
  --ngspice-executable "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

Esempio apertura diretta della modalità CHAT:

```powershell
python scripts\run_full_pipeline.py webchat `
  --workspace manager_a08 `
  --mode chat `
  --ngspice-executable "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

Esempio apertura diretta della modalità AGENT:

```powershell
python scripts\run_full_pipeline.py webchat `
  --workspace manager_a08 `
  --mode agent `
  --ngspice-executable "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

Esempio completo:

```powershell
python scripts\run_full_pipeline.py all `
  --workspace manager_a08 `
  --image data\batchA\a08.jpg `
  --circuit a08 `
  --values-yaml metadata\pipeline2_manual_values\batchA\a08_values.yaml `
  --mode chat `
  --ngspice-executable "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

La sintassi definitiva potrà cambiare durante l'implementazione, ma questi
sono i dati che non devono essere dedotti implicitamente.

## Collegamenti attuali da sistemare

### Pipeline 1.0

- Gli step 01-05 usano `PIPELINE_DATASET` tramite variabile ambiente.
- Lo step 01 usa `PIPELINE_INPUT_BATCH` e legge una cartella sotto `data/`.
- Gli step 03-05 supportano già `PIPELINE_IMAGE_IDS`.
- Gli step 01 e 02 non filtrano ancora il singolo circuito.
- Lo step 06 possiede una CLI per le directory, ma non filtra il singolo JSON.

Intervento minimo:

- aggiungere filtro immagine generale agli step 01, 02 e 06;
- supportare una directory immagine esplicita nello step 01;
- usare lo stesso interprete Python dell'orchestratore;
- propagare le variabili ambiente soltanto ai processi figli.

### Pipeline 2.0

- `run_pipeline2.py` esegue già 01-08 e 10.
- Lo YAML viene cercato secondo la convenzione batch/circuito.
- Gli step 13-15 non sono richiamati direttamente dall'orchestratore base.
- I workspace CHAT e AGENT vengono preparati con comandi separati.
- `09_web_chat.py` riconosce automaticamente la doppia root soltanto per
  nomi di esperimento specifici.

Intervento minimo:

- permettere un riferimento YAML esplicito o una copia demo tracciata;
- aggiungere una funzione per costruire direttamente il viewer;
- preparare su richiesta il solo workspace CHAT o AGENT selezionato;
- riaprire un workspace interattivo esistente senza ricreare la base;
- rilevare in modo generale i workspace `chat/agent`.

## Manifest della demo

Ogni workspace mantiene un unico manifest aggiornato atomicamente dopo ogni
comando:

```text
outputs/demo_workspaces/<workspace_id>/workspace_manifest.json
```

Campi minimi:

```yaml
workspace_id: null
circuit: null
source_image: null
workspace_image: null
source_image_sha256: null
source_values_yaml: null
workspace_values_yaml: null
source_values_sha256: null
started_at: null
updated_at: null
stages:
  preflight: null
  pipeline1: null
  pipeline2: null
  spice: null
  viewer: null
  chat: null
  agent: null
artifacts:
  graph_json: null
  graph_sha256: null
  netlist: null
  spice_report: null
  viewer_svg: null
warnings: []
errors: []
```

Il manifest serve a riaprire il workspace in giorni diversi, controllare la
coerenza degli input e capire immediatamente dove si è fermata un'esecuzione.
Gli stati CHAT e AGENT sono separati e possono avanzare in momenti diversi.

## Strategia di affidabilità per mercoledì

Per ogni circuito scelto preparare:

1. run completa di prova;
2. confronto tra nuovo Graph e Graph validato;
3. verifica dello YAML sul nuovo Graph;
4. base run SPICE verificata;
5. viewer già generato;
6. workspace CHAT e AGENT puliti;
7. copia precomputata utilizzabile come fallback.

Durante la demo:

- eseguire dal vivo il circuito principale;
- tenere pronto un secondo circuito già arrivato al Graph;
- tenere pronto il viewer precomputato se YOLO o ngspice richiedono più tempo;
- mantenere una sessione webchat già predisposta come fallback per problemi di
  rete o configurazione OpenAI.

## Ambiente verificato il 20 luglio 2026

```text
Python 3.12.7: disponibile
dipendenze principali: disponibili
modello YOLO best.pt: disponibile
Tesseract 5.3.0: disponibile
ngspice 46: disponibile
OPENAI_API_KEY nel processo di controllo: non rilevata
```

Il preflight dovrà bloccare soltanto CHAT/AGENT se manca la chiave OpenAI;
Pipeline 1.0, Pipeline 2.0, SPICE e viewer devono restare utilizzabili.

## Ordine di implementazione

1. Aggiungere il filtro per singola immagine agli step Pipeline 1.0 mancanti.
2. Creare l'orchestratore e il preflight condiviso.
3. Collegare il sottocomando pubblico `graph`.
4. Collegare `spice` e lo YAML esplicito.
5. Collegare gli step viewer 13-15.
6. Automatizzare la preparazione indipendente di CHAT e AGENT.
7. Collegare `webchat --mode chat|agent` e generalizzare il rilevamento dei workspace.
8. Scrivere il manifest della demo.
9. Eseguire smoke test su A08, B02 e B03.
10. Scegliere circuito principale, confronto e fallback.

## Stato delle attività

```text
[x] Inventario degli script Pipeline 1.0 e Pipeline 2.0
[x] Verifica preliminare dell'ambiente locale
[x] Definizione del flusso modulare della demo
[ ] Filtri per singola immagine Pipeline 1.0
[ ] Orchestratore generale
[ ] Preflight automatico
[ ] Collegamento Pipeline 2.0 e YAML
[ ] Viewer automatico
[ ] Preparazione persistente e indipendente CHAT/AGENT
[ ] Apertura diretta webchat in modalità CHAT o AGENT
[ ] Manifest di esecuzione
[ ] Smoke test circuiti candidati
[ ] Comando definitivo e procedura fallback
```
