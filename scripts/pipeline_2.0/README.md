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

### 09 - SPICE Summary

Per ora e uno step placeholder.

La scelta corrente e non creare una sintesi intermedia obbligatoria: l'agente
deve leggere gli output reali della pipeline tramite il manifest dello step 10.

### 10 - Diagnostic Context

Costruisce il manifest diagnostico leggero per l'agente.

Lo step 10 viene eseguito da `run_pipeline2.py` dopo la generazione della
netlist e, se richiesto, dopo lo step 08. Non duplica tutti gli output dentro un
file enorme: salva un indice dei file disponibili, una mini-summary tecnica e
le regole operative per l'agente.

Output:

```text
10_diagnostic_context.json
```

### 11 - Agent Readonly

Prima base dell'agente diagnostico.

Di default non chiama OpenAI. Legge `10_diagnostic_context.json`, carica gli
artefatti indicati nel manifest e genera due file di controllo:

```text
11_agent_input_preview.md
11_agent_prompt.md
```

Il preview serve a noi per controllare cosa viene caricato. Il prompt e il testo
che verra mandato al modello AI quando collegheremo OpenAI.

Se viene passato `--run-agent`, lo step chiama OpenAI e salva:

```text
11_agent_response.md
```

Lo step 11 e read-only:

- non modifica i file originali;
- non crea scenari;
- non copia output;
- non esegue ngspice;
- propone solo eventuali scenari diagnostici futuri nel prompt.

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

Nel nostro ambiente, se `ngspice_con` non e nel PATH, si puo usare direttamente
il path completo:

```powershell
python scripts\pipeline_2.0\run_pipeline2.py --batch batchA --circuits a01 --run-spice --ngspice-executable "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

Per rigenerare tutta la pipeline 2.0 su Batch A, includendo lo step 10 ma senza
rilanciare SPICE:

```powershell
python scripts\pipeline_2.0\run_pipeline2.py --batch batchA --circuits a01 a02 a03 a04 a05 a06 a07 a08 a09 a10
```

Per rigenerare anche SPICE su tutto Batch A:

```powershell
python scripts\pipeline_2.0\run_pipeline2.py --batch batchA --circuits a01 a02 a03 a04 a05 a06 a07 a08 a09 a10 --run-spice --ngspice-executable "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

## Comandi agente read-only

Lo step 11 si esegue separatamente dal comando principale della pipeline.

Prima di eseguire l'agente, il circuito deve avere gia gli output della
Pipeline 2.0, in particolare:

```text
10_diagnostic_context.json
```

Se vuoi partire da zero su `a01`, esegui prima:

```powershell
python scripts\pipeline_2.0\run_pipeline2.py --batch batchA --circuits a01 --run-spice --ngspice-executable "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

### Solo prompt, senza OpenAI

Per generare preview e prompt dell'agente su `a01`, senza chiamare OpenAI:

```powershell
python scripts\pipeline_2.0\json_to_spice\11_agent_readonly.py --batch batchA --circuit a01 --question "Perche la lampada non si accende?"
```

Output:

```text
outputs/pipeline2.0/batchA/a01/11_agent_input_preview.md
outputs/pipeline2.0/batchA/a01/11_agent_prompt.md
```

Questa modalita serve per controllare cosa verra mandato al modello.

Si puo anche passare direttamente il manifest:

```powershell
python scripts\pipeline_2.0\json_to_spice\11_agent_readonly.py --context outputs\pipeline2.0\batchA\a01\10_diagnostic_context.json --question "Perche la lampada non si accende?"
```

### Agente con OpenAI

Per chiamare OpenAI bisogna aggiungere `--run-agent`.

Comando consigliato con modello default `gpt-5.4`:

```powershell
python scripts\pipeline_2.0\json_to_spice\11_agent_readonly.py --batch batchA --circuit a01 --question "Perche la lampada non si accende?" --run-agent
```

Output aggiuntivo:

```text
outputs/pipeline2.0/batchA/a01/11_agent_response.md
```

Per scegliere esplicitamente il modello default:

```powershell
python scripts\pipeline_2.0\json_to_spice\11_agent_readonly.py --batch batchA --circuit a01 --question "Perche la lampada non si accende?" --run-agent --model gpt-5.4
```

Per usare il modello piu forte come confronto:

```powershell
python scripts\pipeline_2.0\json_to_spice\11_agent_readonly.py --batch batchA --circuit a01 --question "Perche la lampada non si accende?" --run-agent --model gpt-5.5
```

Per test piu rapidi/economici:

```powershell
python scripts\pipeline_2.0\json_to_spice\11_agent_readonly.py --batch batchA --circuit a01 --question "Perche la lampada non si accende?" --run-agent --model gpt-5.4-mini
```

Modello default:

```text
gpt-5.4
```

Modelli consigliati:

```text
gpt-5.4       default operativo dell'agente
gpt-5.5       confronto di qualita / modello piu forte
gpt-5.4-mini  test piu rapidi ed economici
gpt-5-mini    baseline veloce/economica
```

La scelta del modello riguarda solo l'agente. La pipeline tecnica fino a SPICE
resta indipendente dal modello AI.

La API key viene cercata in questo ordine:

```text
OPENAI_API_KEY gia presente nell'ambiente
.env nella root del progetto
scripts/GPT/.env
```

Il valore della chiave non viene mai stampato.

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
10_diagnostic_context.json
```

Se viene passato `--run-spice`, vengono prodotti anche:

```text
08_spice_run.json
08_ngspice_stdout.txt
08_ngspice_stderr.txt
```

Se viene eseguito lo step 11, vengono prodotti anche:

```text
11_agent_input_preview.md
11_agent_prompt.md
```

Se viene passato anche `--run-agent`, viene prodotto:

```text
11_agent_response.md
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

## Nota su chat/agente

Quando la pipeline verra estesa a tutti i batch e a molte immagini, la chat o
l'agente diventeranno il livello interattivo sopra gli output tecnici.

L'idea non e sostituire la pipeline, ma guidarla:

```text
utente: Perche la lampada non si accende?
agente: legge 10_diagnostic_context.json e gli output 01-08
agente: spiega il risultato SPICE
agente: propone massimo 3 scenari diagnostici candidati
utente: scegli scenario 2
pipeline: crea una cartella scenario separata
pipeline: copia gli output originali
pipeline: modifica solo le copie
pipeline: rigenera gli step necessari e rilancia SPICE
agente: confronta run base e run scenario
```

Prima versione attuale:

- `10_build_diagnostic_context.py` crea il manifest;
- `11_agent_readonly.py` crea preview e prompt;
- OpenAI e collegato solo dietro flag `--run-agent`;
- `12_controlled_scenarios.py` resta placeholder.

Regole sugli scenari:

- `11` propone soltanto scenari;
- uno scenario parte solo se l'utente lo sceglie esplicitamente;
- gli output originali non vanno mai sovrascritti;
- lo scenario deve lavorare su copie degli output base;
- la cartella scenario deve essere separata dalla cartella base del circuito.

Flusso tecnico corrente:

```text
01 -> 02 -> 03 -> 04 -> 06 -> 07 -> 08 -> 10 -> 11
```

Per la tesi e una direzione interessante per descrivere un sistema interattivo
che aiuta l'utente a trasformare il circuito riconosciuto in una simulazione
SPICE eseguibile.

## Step futuri

I prossimi step saranno:

- `09_summarize_spice.py`: placeholder, per ora saltato;
- `10_build_diagnostic_context.py`: implementato come manifest leggero;
- `11_agent_readonly.py`: implementato fino a preview, prompt e chiamata
  OpenAI opzionale con `--run-agent`;
- `12_controlled_scenarios.py`: scenari SPICE controllati per verificare
  ipotesi.
