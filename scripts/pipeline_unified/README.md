# Pipeline unificata

Questo launcher permette di eseguire Pipeline 1.0 e Pipeline 2.0 nello stesso
workspace persistente. Le fasi possono essere lanciate separatamente, anche in
giorni diversi, oppure tutte insieme.

Eseguire sempre i comandi dalla root del progetto:

```powershell
Set-Location (git rev-parse --show-toplevel)
```

Gli esempi risolvono `ngspice_con.exe` dal `PATH`. Se l'eseguibile non e'
nel `PATH`, sostituire quel nome con un percorso valido sul proprio PC.

## Comandi disponibili

| Comando | Cosa esegue | Risultato principale |
|---|---|---|
| `preflight` | Controlli in sola lettura | Ambiente, asset e programmi validati |
| `graph` | Pipeline 1.0, step 01-06 | Graph JSON e sito di controllo |
| `spice` | Pipeline 2.0, step 01-08 | Netlist, ngspice e risultati SPICE |
| `webchat` | Viewer e copie web isolate | CHAT e AGENT nello stesso server |
| `all` | Tutte le fasi precedenti | Flusso completo dall'immagine alla webchat |

La scelta più importante è `--workspace`: identifica una run persistente sotto
`outputs/demo_workspaces/`. Per continuare una run esistente bisogna riutilizzare
sempre lo stesso nome.

## Preparare un batch

La cartella di input contiene le immagini. Per eseguire anche Pipeline 2.0 deve
contenere una sottocartella `values` con uno YAML per ogni circuito:

```text
data/<batch>/
|-- circuito_1.jpg
|-- circuito_2.png
`-- values/
    |-- circuito_1_values.yaml
    `-- circuito_2_values.yaml
```

Il nome dell'immagine, del circuito e dello YAML deve coincidere. Per esempio:

```text
a09.png
values/a09_values.yaml
```

Lo YAML contiene i valori manuali dei componenti e sostituisce la lettura OCR.
Pipeline 1.0 può essere eseguita anche senza YAML; `spice` e `all` richiedono
invece lo YAML del circuito selezionato.

## 1. Eseguire soltanto Pipeline 1.0

Il comando `graph` esegue gli step 01-06:

```text
immagine -> componenti -> istanze -> terminali -> fili -> Graph JSON -> sito web
```

### Un solo circuito

```powershell
.venv312\Scripts\python.exe -B scripts\pipeline_unified\run_pipeline.py graph `
  --workspace demo_a09 `
  --input-dir data\batchPipeline2.0\batchDemo `
  --circuit a09
```

### Tutto il batch

```powershell
.venv312\Scripts\python.exe -B scripts\pipeline_unified\run_pipeline.py graph `
  --workspace demo_batch `
  --input-dir data\batchPipeline2.0\batchDemo `
  --all
```

Il sito prodotto dallo step 06 si trova in:

```text
outputs/demo_workspaces/<workspace>/pipeline1.0/06_graph_report/index.html
```

Il Graph JSON di un circuito si trova in:

```text
outputs/demo_workspaces/<workspace>/pipeline1.0/06_graph_report/<circuito>/<circuito>.json
```

## 2. Eseguire soltanto Pipeline 2.0 e ngspice

Il comando `spice` riprende un workspace già completato da `graph` ed esegue
gli step 01-08 della Pipeline 2.0:

```text
Graph JSON -> normalizzazione -> node map -> valori YAML -> regole -> netlist -> ngspice
```

Non bisogna ripetere `--input-dir`: immagini e Graph vengono recuperati dal
workspace indicato.

### Un solo circuito

```powershell
.venv312\Scripts\python.exe -B scripts\pipeline_unified\run_pipeline.py spice `
  --workspace demo_a09 `
  --circuit a09 `
  --ngspice-executable ngspice_con.exe
```

### Tutti i circuiti presenti nel workspace

```powershell
.venv312\Scripts\python.exe -B scripts\pipeline_unified\run_pipeline.py spice `
  --workspace demo_batch `
  --all `
  --ngspice-executable ngspice_con.exe
```

Gli output di ogni circuito vengono salvati in:

```text
outputs/demo_workspaces/<workspace>/pipeline2.0/<circuito>/
```

I file principali sono `07_netlist.cir`, `08_spice_run.json` e gli output di
ngspice. Se il circuito prevede un transitorio sono presenti anche CSV e grafici
temporali.

## 3. Aprire viewer, CHAT e AGENT

Il comando `webchat` richiede che Pipeline 1.0 e Pipeline 2.0 siano già
completate nello stesso workspace. Prepara due copie indipendenti della base:

```text
web/chat/<circuito>/
web/agent/<circuito>/
```

Un solo server mostra il viewer e permette all'utente di scegliere tra CHAT e
AGENT. Le history e gli scenari delle due modalità rimangono separati.

```powershell
.venv312\Scripts\python.exe -B scripts\pipeline_unified\run_pipeline.py webchat `
  --workspace demo_a09 `
  --circuit a09 `
  --ngspice-executable ngspice_con.exe
```

Il server rimane attivo nel terminale e si arresta con `Ctrl+C`.

Per preparare viewer, CHAT e AGENT senza avviare il server:

```powershell
.venv312\Scripts\python.exe -B scripts\pipeline_unified\run_pipeline.py webchat `
  --workspace demo_a09 `
  --circuit a09 `
  --prepare-only
```

Per avviare il server senza aprire automaticamente il browser, aggiungere:

```text
--no-browser
```

Il viewer usa sempre geometria e collegamenti prodotti dagli step 03 e 05 della
Pipeline 1.0 appartenente allo stesso workspace.

## 4. Eseguire tutto con un solo comando

Il comando `all` esegue in ordine:

1. Pipeline 1.0, step 01-06;
2. Pipeline 2.0, step 01-08 e ngspice;
3. viewer e copie separate CHAT/AGENT;
4. server web.

### Flusso completo su un solo circuito

```powershell
.venv312\Scripts\python.exe -B scripts\pipeline_unified\run_pipeline.py all `
  --workspace verifica_clone_a09_all `
  --input-dir data\batchPipeline2.0\batchDemo `
  --circuit a09 `
  --ngspice-executable ngspice_con.exe
```

Il nome di `--workspace` deve essere nuovo. Per ripetere il controllo scegliere
un altro nome oppure aggiungere consapevolmente `--force` per rigenerarlo.

### Flusso completo su tutto il batch

Con `--all` bisogna indicare quale circuito aprire nella webchat al termine:

```powershell
.venv312\Scripts\python.exe -B scripts\pipeline_unified\run_pipeline.py all `
  --workspace demo_batch_all `
  --input-dir data\batchPipeline2.0\batchDemo `
  --all `
  --open-circuit a09 `
  --ngspice-executable ngspice_con.exe
```

Per completare tutte le fasi senza avviare il server, aggiungere:

```text
--prepare-only
```

## Esempio di esecuzione progressiva

Le tre fasi seguenti possono essere eseguite a distanza di ore o giorni. Il
collegamento tra le fasi è garantito dal nome `demo_a09`.

### Primo momento: creare il Graph

```powershell
.venv312\Scripts\python.exe -B scripts\pipeline_unified\run_pipeline.py graph `
  --workspace demo_a09 `
  --input-dir data\batchPipeline2.0\batchDemo `
  --circuit a09
```

### Secondo momento: arrivare fino a ngspice

```powershell
.venv312\Scripts\python.exe -B scripts\pipeline_unified\run_pipeline.py spice `
  --workspace demo_a09 `
  --circuit a09 `
  --ngspice-executable ngspice_con.exe
```

### Terzo momento: aprire CHAT e AGENT

```powershell
.venv312\Scripts\python.exe -B scripts\pipeline_unified\run_pipeline.py webchat `
  --workspace demo_a09 `
  --circuit a09 `
  --ngspice-executable ngspice_con.exe
```

## Riprendere o rigenerare una run

Se gli input e gli output sono ancora coerenti, i comandi riutilizzano il
workspace esistente e saltano le fasi già complete.

I manifest in schema v2 salvano come repo-relative i path interni al progetto.
I manifest storici con path assoluti vengono risolti automaticamente rispetto
al clone corrente; anche il vecchio alias `data/batchDemo` viene migrato a
`data/batchPipeline2.0/batchDemo`. La forma portabile viene salvata al
successivo aggiornamento del manifest.

Usare `--force` soltanto quando si vuole rigenerare esplicitamente una fase:

- con `graph`, rigenera gli output Pipeline 1.0 selezionati;
- con `spice`, rigenera gli output Pipeline 2.0 selezionati;
- con `webchat`, ricrea entrambe le copie web e cancella le relative history e
  gli scenari;
- con `all`, rigenera tutte le fasi selezionate.

Prima di usare `--force` sulla webchat, verificare quindi che le conversazioni
esistenti non servano più.

## Controllare senza eseguire

Prima della prima run su un nuovo PC, eseguire il controllo completo:

```powershell
.venv312\Scripts\python.exe -B scripts\pipeline_unified\run_pipeline.py preflight
```

Il comando usa di default `data\batchPipeline2.0\batchDemo` e verifica anche
checkpoint Git LFS, import, metadati, modelli SPICE, ngspice e Tesseract. Non
crea workspace. Aggiungere `--require-openai` se si vogliono usare subito anche
le funzioni AGENT.

`graph`, `spice` e `webchat` supportano `--dry-run`. Il comando controlla
selezione e prerequisiti senza creare nuovi output.

Esempio per Pipeline 1.0:

```powershell
.venv312\Scripts\python.exe -B scripts\pipeline_unified\run_pipeline.py graph `
  --workspace controllo_demo `
  --input-dir data\batchPipeline2.0\batchDemo `
  --circuit a09 `
  --dry-run
```

Esempio per Pipeline 2.0:

```powershell
.venv312\Scripts\python.exe -B scripts\pipeline_unified\run_pipeline.py spice `
  --workspace demo_a09 `
  --circuit a09 `
  --ngspice-executable ngspice_con.exe `
  --dry-run
```

## Struttura del workspace

```text
outputs/demo_workspaces/<workspace>/
|-- workspace_manifest.json
|-- input/
|   `-- images/
|-- pipeline1.0/
|   |-- 01_detect_components/
|   |-- 02_assign_instances/
|   |-- 03_estimate_terminals/
|   |-- 04_extract_wires/
|   |-- 05_build_terminal_graph/
|   `-- 06_graph_report/
|-- pipeline2.0/
|   `-- <circuito>/
|-- web/
|   |-- chat/
|   |   `-- <circuito>/
|   `-- agent/
|       `-- <circuito>/
`-- logs/
```

Ogni workspace è isolato. Gli output storici presenti sotto
`outputs/pipeline1.0` e `outputs/pipeline2.0` non vengono usati né modificati.

## Guida rapida della CLI

```powershell
.venv312\Scripts\python.exe -B scripts\pipeline_unified\run_pipeline.py --help
.venv312\Scripts\python.exe -B scripts\pipeline_unified\run_pipeline.py graph --help
.venv312\Scripts\python.exe -B scripts\pipeline_unified\run_pipeline.py spice --help
.venv312\Scripts\python.exe -B scripts\pipeline_unified\run_pipeline.py webchat --help
.venv312\Scripts\python.exe -B scripts\pipeline_unified\run_pipeline.py all --help
```
