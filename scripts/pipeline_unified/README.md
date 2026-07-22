# Pipeline unificata - guida progressiva

Questa directory contiene l'orchestratore che colleghera' Pipeline 1.0 e
Pipeline 2.0 senza duplicare la logica degli script numerati.

L'implementazione procede per fasi verificabili. Sono disponibili la Pipeline
1.0 completa, la Pipeline 2.0 tecnica fino a ngspice, la webchat con viewer e
workspace CHAT/AGENT indipendenti e il comando che orchestra l'intero flusso.

## Comandi previsti

| Comando | Stato | Funzione |
|---|---|---|
| `graph` | disponibile | Esegue Pipeline 1.0, step 01-06 |
| `spice` | disponibile | Usa i Graph del workspace e gli YAML del batch, esegue gli step 01-08 |
| `webchat` | disponibile | Prepara viewer e workspace CHAT/AGENT e apre un unico server |
| `all` | disponibile | Esegue l'intero flusso fino alla webchat |
| `status` | da implementare | Mostra lo stato persistente dei circuiti nel workspace |

I comandi non ancora disponibili non vengono esposti dalla CLI, cosi' non
possono essere confusi con funzionalita' gia' utilizzabili.

### Webchat disponibile

```powershell
# Un solo server con viewer e selettore CHAT/AGENT
.venv312\Scripts\python.exe scripts\pipeline_unified\run_pipeline.py webchat `
  --workspace demo_batch `
  --circuit b02 `
  --ngspice-executable "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

### Flusso completo disponibile

Su un solo circuito, `all` esegue in ordine Pipeline 1.0, Pipeline 2.0 con
ngspice e preparazione di CHAT/AGENT; infine avvia il server web:

```powershell
.venv312\Scripts\python.exe scripts\pipeline_unified\run_pipeline.py all `
  --workspace demo_a09_all `
  --input-dir data\batchDemo `
  --circuit a09 `
  --ngspice-executable "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

Per elaborare tutto il batch bisogna indicare esplicitamente quale circuito
aprire nel viewer al termine:

```powershell
# Flusso completo sul batch; al termine viene aperto b02
.venv312\Scripts\python.exe scripts\pipeline_unified\run_pipeline.py all `
  --workspace demo_batch `
  --input-dir data\batchDemo `
  --all `
  --open-circuit b02 `
  --ngspice-executable "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

Il server resta in primo piano e si arresta con `Ctrl+C`. L'opzione
`--prepare-only` completa entrambe le pipeline e prepara viewer, CHAT e AGENT
senza avviare il server. Se una fase fallisce, quelle successive non vengono
eseguite e il workspace conserva manifest e log utili per riprendere la run.

Il solo comando `status` resta ancora da implementare:

```powershell
# Stato persistente della run
.venv312\Scripts\python.exe scripts\pipeline_unified\run_pipeline.py status `
  --workspace demo_batch
```

## Workspace

Ogni esecuzione usa una directory separata:

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
|   `-- <circuit_id>/
|       |-- 01_graph.json
|       |-- 02_normalized_circuit.json
|       |-- 03_node_map.json
|       |-- 04_values_bound.json
|       |-- 06_component_rules.json
|       |-- 07_netlist.cir
|       `-- 08_spice_run.json
|-- web/
|   |-- chat/
|   |   `-- <circuit_id>/
|   `-- agent/
|       `-- <circuit_id>/
`-- logs/
```

Le immagini selezionate vengono copiate in `input/images`. Gli output
ufficiali di Batch A e Batch B non vengono modificati.

Ogni cartella batch contiene le immagini e una sottocartella `values` con un
file YAML omonimo per circuito:

```text
data/<batch>/
|-- circuito_1.jpg
|-- circuito_2.png
`-- values/
    |-- circuito_1_values.yaml
    `-- circuito_2_values.yaml
```

Il comando `spice` non legge mai i Graph storici sotto `outputs/pipeline1.0`:
usa soltanto `pipeline1.0/06_graph_report` del workspace selezionato.

`--workspace` viene usato esattamente come scritto: il launcher non aggiunge
prefissi impliciti. Per la demo usiamo nomi brevi e stabili:

```text
demo_b02
demo_batch
```

## Controllare la CLI

```powershell
.venv312\Scripts\python.exe scripts\pipeline_unified\run_pipeline.py --help
```

```powershell
.venv312\Scripts\python.exe scripts\pipeline_unified\run_pipeline.py graph --help
```

```powershell
.venv312\Scripts\python.exe scripts\pipeline_unified\run_pipeline.py spice --help
```

## Pipeline 1.0 su un solo circuito

Il comando seguente elabora soltanto `b02` e crea un workspace chiamato
`demo_b02`:

```powershell
.venv312\Scripts\python.exe scripts\pipeline_unified\run_pipeline.py graph `
  --workspace demo_b02 `
  --input-dir data\batchDemo `
  --circuit b02
```

## Pipeline 1.0 su tutto il Batch Demo

```powershell
.venv312\Scripts\python.exe scripts\pipeline_unified\run_pipeline.py graph `
  --workspace demo_batch `
  --input-dir data\batchDemo `
  --all
```

Il batch attuale contiene:

- `a04`;
- `a08`;
- `a09`;
- `b02`;
- `b03`.

## Controllo senza esecuzione

`--dry-run` verifica cartella e selezione, ma non carica YOLO e non crea file:

```powershell
.venv312\Scripts\python.exe scripts\pipeline_unified\run_pipeline.py graph `
  --workspace prova_configurazione `
  --input-dir data\batchDemo `
  --all `
  --dry-run
```

## Riesecuzione

Se un circuito risulta gia' completato, il comando non lo sovrascrive. Per
rigenerarlo intenzionalmente bisogna aggiungere `--force`:

```powershell
.venv312\Scripts\python.exe scripts\pipeline_unified\run_pipeline.py graph `
  --workspace demo_b02 `
  --input-dir data\batchDemo `
  --circuit b02 `
  --force
```

Una run interrotta o fallita puo' invece essere rilanciata senza `--force`.
Il manifest e il log indicano lo step raggiunto.

## Output finale della fase Graph

Per `b02`:

```text
outputs/demo_workspaces/demo_b02/pipeline1.0/06_graph_report/b02/b02.json
outputs/demo_workspaces/demo_b02/pipeline1.0/06_graph_report/b02/graph.html
outputs/demo_workspaces/demo_b02/pipeline1.0/06_graph_report/index.html
```

## Pipeline 2.0 e ngspice

Eseguire tutti i circuiti gia' completati dalla Pipeline 1.0:

```powershell
.venv312\Scripts\python.exe scripts\pipeline_unified\run_pipeline.py spice `
  --workspace demo_batch `
  --all `
  --ngspice-executable "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

Eseguire un solo circuito:

```powershell
.venv312\Scripts\python.exe scripts\pipeline_unified\run_pipeline.py spice `
  --workspace demo_batch `
  --circuit b02 `
  --ngspice-executable "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

Controllare Graph, YAML e disponibilita' di ngspice senza creare output:

```powershell
.venv312\Scripts\python.exe scripts\pipeline_unified\run_pipeline.py spice `
  --workspace demo_batch `
  --all `
  --ngspice-executable "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe" `
  --dry-run
```

Una run gia' completa viene saltata se gli hash del Graph e dello YAML non
sono cambiati. `--force` rigenera soltanto la cartella Pipeline 2.0 del
circuito selezionato. Lo stato e gli hash vengono salvati nello stesso
`workspace_manifest.json` usato dal comando `graph`.

## Viewer, CHAT e AGENT

Preparare le due copie e aprire il server unico:

```powershell
.venv312\Scripts\python.exe scripts\pipeline_unified\run_pipeline.py webchat `
  --workspace demo_batch `
  --circuit b02 `
  --ngspice-executable "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

Preparare copie e viewer senza aprire il server:

```powershell
.venv312\Scripts\python.exe scripts\pipeline_unified\run_pipeline.py webchat `
  --workspace demo_batch `
  --circuit b02 `
  --prepare-only
```

Controllare soltanto prerequisiti e provenienza degli artefatti:

```powershell
.venv312\Scripts\python.exe scripts\pipeline_unified\run_pipeline.py webchat `
  --workspace demo_batch `
  --circuit b02 `
  --dry-run
```

Il viewer usa sempre `03_estimate_terminals/<circuit>.json` e
`05_build_terminal_graph/<circuit>.json` presenti nella `pipeline1.0` dello
stesso workspace. I riferimenti vengono salvati in `pipeline2_sources.json`
all'interno di entrambe le copie e valgono anche per le run scenario.

Riaprire il comando conserva history e scenari. Se immagine, Graph, YAML,
geometria o base 01-08 sono cambiati, il comando si ferma per evitare di
mescolare run incompatibili. `--force` ricrea esplicitamente entrambe le copie
e quindi elimina le precedenti history e gli scenari web del circuito.
