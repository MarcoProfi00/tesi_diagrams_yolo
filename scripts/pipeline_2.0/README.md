# Pipeline 2.0 - Graph JSON to SPICE

Questo documento riassume, in modo breve, cosa fa per ora la pipeline 2.0 e
come eseguirla da terminale.

La pipeline 2.0 parte dai Graph JSON prodotti dalla pipeline 1.0 e prepara i
primi artefatti elettrici utili alla conversione SPICE.

## Input principali

Per ogni circuito servono:

- Graph JSON della pipeline 1.0:
  `outputs/pipeline1.0/<batch>/06_graph_report/<circuit>/<circuit>.json`
- valori manuali:
  `metadata/pipeline2_manual_values/<batch>/<circuit>_values.yaml`
- mapping classi SPICE:
  `metadata/pipeline2_spice_classes.yaml`

Esempio per `a01`:

```text
outputs/pipeline1.0/batchA/06_graph_report/a01/a01.json
metadata/pipeline2_manual_values/batchA/a01_values.yaml
metadata/pipeline2_spice_classes.yaml
```

## Step implementati

### 01 - IO

Legge il Graph JSON della pipeline 1.0 e crea la cartella output della pipeline
2.0.

Output:

```text
01_graph.json
```

### 02 - Normalize

Normalizza il Graph JSON:

- componenti;
- terminali;
- connessioni;
- statistiche;
- warning di normalizzazione.

Output:

```text
02_normalized_circuit.json
```

### 03 - Node Map

Costruisce i nodi elettrici.

Tutti i terminali collegati a GND vengono mappati nel nodo SPICE `0`.

Output:

```text
03_node_map.json
```

### 04 - Values

Legge i valori manuali dal file YAML e li associa ai componenti e ai nodi.

Questo step non genera SPICE. Controlla solo se i componenti hanno i valori
necessari.

Output:

```text
04_values_bound.json
```

### 05 - Device Profiles

Per ora non e implementato.

Servira piu avanti per componenti complessi, per esempio integrati, transistor,
opamp o componenti con pin-map specifico.

### 06 - Component Rules

Applica il mapping `pipeline2_spice_classes.yaml`.

Dice quali componenti sono pronti per SPICE e quali invece sono strutturali,
mancanti o non supportati.

Output:

```text
06_component_rules.json
```

### 07 - SPICE Emit

Genera una prima netlist SPICE leggibile.

Per ora:

- resistenze -> `R`;
- lampade -> resistenza equivalente `R`;
- batterie/supply -> sorgente `V`;
- condensatori -> `C`;
- LED/diodi -> `D` + `.model`;
- switch aperti -> commento, non emessi;
- GND e connector -> non emessi, perche strutturali.

Output:

```text
07_netlist.cir
07_spice_emit_report.json
```

### 08 - SPICE Run

Esegue opzionalmente ngspice sulla netlist prodotta dallo step 07.

Lo step 08 non parte automaticamente: viene eseguito solo passando il flag
`--run-spice` a `run_pipeline2.py`.

Quando viene eseguito, produce:

```text
08_spice_run.json
08_ngspice_stdout.txt
08_ngspice_stderr.txt
```

Gli output tecnici dello step 08 sono in inglese.

## Comando principale

Da terminale, nella root del progetto:

```powershell
python scripts\pipeline_2.0\run_pipeline2.py --batch batchA --circuits a01 a02 a10
```

Questo comando esegue gli step disponibili fino alla generazione della netlist
SPICE, senza lanciare ngspice.

```text
a01
a02
a10
```

Gli output vengono creati in:

```text
outputs/pipeline2.0/batchA/<circuit>/
```

Esempio:

```text
outputs/pipeline2.0/batchA/a01/
```

Per eseguire anche ngspice su un circuito:

```powershell
python scripts\pipeline_2.0\run_pipeline2.py --batch batchA --circuits a01 --run-spice
```

Per forzare esplicitamente l'eseguibile console di ngspice:

```powershell
python scripts\pipeline_2.0\run_pipeline2.py --batch batchA --circuits a01 --run-spice --ngspice-executable ngspice_con
```

## Ngspice su Windows e VS Code

Su Windows, VS Code non installa ngspice direttamente. VS Code usa il terminale
integrato, quindi deve riuscire a trovare `ngspice_con.exe`.

Nel nostro caso ngspice si trova qui:

```text
C:\Users\m.profilo\Spice64\bin
```

Dentro questa cartella ci sono:

```text
C:\Users\m.profilo\Spice64\bin\ngspice.exe
C:\Users\m.profilo\Spice64\bin\ngspice_con.exe
```

Per la pipeline conviene usare `ngspice_con.exe`, cioe la versione console. La
versione `ngspice.exe` puo aprire una finestra grafica.

### Verifica con path completo

Da terminale PowerShell in VS Code:

```powershell
& "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe" -v
```

Per eseguire manualmente la netlist di `a01`:

```powershell
& "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe" -b outputs\pipeline2.0\batchA\a01\07_netlist.cir
```

Questo comando usa:

```text
-b
```

cioe batch mode: ngspice esegue la netlist senza aprire l'interfaccia
interattiva.

### Comando veloce temporaneo

Per evitare di scrivere ogni volta il path completo, si puo aggiungere la
cartella al `PATH` solo per il terminale aperto:

```powershell
$env:Path += ";C:\Users\m.profilo\Spice64\bin"
```

Poi si puo usare:

```powershell
ngspice_con -v
```

e:

```powershell
ngspice_con -b outputs\pipeline2.0\batchA\a01\07_netlist.cir
```

Questa modifica temporanea vale solo per il terminale corrente.

### Comando veloce permanente

Per rendere `ngspice_con` disponibile sempre:

1. Aprire `Environment Variables` da Windows.
2. Entrare in `Edit the system environment variables`.
3. Cliccare `Environment Variables`.
4. In `User variables`, selezionare `Path`.
5. Cliccare `Edit`.
6. Cliccare `New`.
7. Aggiungere:

```text
C:\Users\m.profilo\Spice64\bin
```

8. Confermare con `OK`.
9. Chiudere e riaprire VS Code.

Dopo il riavvio di VS Code, questo comando dovrebbe funzionare:

```powershell
ngspice_con -v
```

E questo comando esegue manualmente la netlist di `a01`:

```powershell
ngspice_con -b outputs\pipeline2.0\batchA\a01\07_netlist.cir
```

La pipeline puo fare la stessa cosa tramite lo step 08:

```powershell
python scripts\pipeline_2.0\run_pipeline2.py --batch batchA --circuits a01 --run-spice --ngspice-executable ngspice_con
```

## File prodotti per ogni circuito

Per ogni circuito, al momento, vengono prodotti:

```text
01_graph.json
02_normalized_circuit.json
03_node_map.json
04_values_bound.json
06_component_rules.json
07_netlist.cir
07_spice_emit_report.json
```

Se viene passato `--run-spice`, vengono prodotti anche:

```text
08_spice_run.json
08_ngspice_stdout.txt
08_ngspice_stderr.txt
```

## Come leggere gli output principali

### 03_node_map.json

Mostra i nodi elettrici.

Il nodo `0` e la massa SPICE.

Esempio:

```json
"terminal_to_node": {
  "battery2.1_positive": "N001",
  "battery2.1_negative": "0"
}
```

### 04_values_bound.json

Mostra i valori associati ai componenti.

Esempio:

```json
"resistor22.1": {
  "class_name": "Resistor",
  "value_data": {
    "value": 330,
    "unit": "ohm"
  },
  "status": "bound"
}
```

### 06_component_rules.json

Mostra se un componente e pronto per SPICE.

Esempio:

```json
"resistor22.1": {
  "status": "spice_ready",
  "spice_prefix": "R",
  "nodes": ["N003", "N005"]
}
```

### 07_netlist.cir

E il file SPICE generato.

Esempio:

```spice
Vbattery2_1 N001 0 DC 5
Rresistor22_1 N003 N005 330
Dled12_1 N005 0 LED_RED
.model LED_RED D
.op
.end
```

### 07_spice_emit_report.json

Riassume cosa e stato scritto nella netlist e cosa e stato saltato.

Esempio:

```json
{
  "emitted_elements": 4,
  "skipped_elements": 5,
  "models": ["LED_RED"],
  "warnings": [
    "switch25.1: open switch not emitted"
  ]
}
```

## Nota sugli switch

Per ora, se uno switch e aperto, viene scritto solo come commento nella netlist:

```spice
* switch25.1 open: not emitted
```

Piu avanti potremo aggiungere scenari simulativi, per esempio:

```text
base: switch aperto come riconosciuto dal grafo
switch_closed: stesso circuito, ma con switch chiuso per simulazione
```

In quel caso lo switch chiuso potra diventare:

```spice
Rswitch25_1 N001 N002 1m
```

cioe un collegamento quasi ideale.

## Nota futura su chat/agente

Quando la pipeline verra estesa a tutti i batch e a molte immagini, puo diventare
utile aggiungere una chat o un agente sopra la pipeline.

L'idea non e sostituire la pipeline, ma guidarla:

```text
utente: esegui spice
pipeline: ngspice fallisce
checks: probabile switch aperto o nodo flottante
utente: chiudi lo switch e riesegui
pipeline: crea scenario simulativo, rigenera netlist, rilancia spice
```

Prima versione possibile:

- comandi preimpostati;
- azioni semplici come `esegui spice`, `mostra errori`, `mostra netlist`,
  `chiudi switch25.1`, `riesegui`;
- scenari simulativi separati dalla versione originale del circuito.

Versione piu avanzata:

- agente vero e proprio;
- lettura automatica dei report `08` e `09`;
- proposta di correzioni o scenari;
- confronto tra circuito originale e circuito modificato per simulazione.

Questa parte va implementata solo dopo aver validato bene:

```text
01 -> 02 -> 03 -> 04 -> 06 -> 07 -> 08 -> 09
```

Per la tesi e una direzione interessante per descrivere un sistema interattivo
che aiuta l'utente a trasformare il circuito riconosciuto in una simulazione
SPICE eseguibile.

## Step futuri

I prossimi step saranno:

- `09_checks.py`: interpreta errori, nodi flottanti, switch aperti e problemi
  di simulazione;
- `10_report.py`: produce un report finale leggibile.
