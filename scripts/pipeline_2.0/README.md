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

### 09 - Web Chat

Avvia una piccola interfaccia web locale temporanea per guardare gli output del
circuito e parlare con l'agente diagnostico.

Lo step 09 non e un backend permanente:

- non usa database;
- non salva obbligatoriamente lo storico chat;
- non espone API pubbliche;
- vive solo finche il comando resta in esecuzione nel terminale.

Per ora mostra:

- run principale `Base run`;
- immagine originale del circuito;
- artefatti `01-08`;
- stato SPICE;
- netlist;
- stdout/stderr;
- eventuale plot `.tran`;
- chat diagnostica collegata agli step `10` e `11`.

La chat salva file separati per non sovrascrivere gli esperimenti da terminale:

```text
11_agent_input_preview_chat.md
11_agent_prompt_chat.md
11_agent_response_chat.md
```

Quando l'utente scrive frasi come `esegui scenario 1`, lo step `09` riconosce
la scelta, recupera lo scenario JSON dall'ultima risposta agente e chiama lo
step `12`.

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

Se esistono scenari gia creati in:

```text
outputs/pipeline2.0/<batch>/<circuit>/scenarios/
```

lo step 10 li indicizza in `executed_scenarios`, includendo path e riepilogo di:

```text
scenario.json
scenario_status.json
12_controlled_scenarios.json
scenario_comparison.json
```

In questo modo la chat puo rispondere anche a domande sugli scenari gia
eseguiti, per esempio quale scenario ha l'outcome piu forte.

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

### 12 - Controlled Scenarios

Applica scenari diagnostici controllati scelti dall'utente.

Lo step 12 non modifica mai la base run originale. Lavora solo dentro:

```text
outputs/pipeline2.0/<batch>/<circuit>/scenarios/<scenario_id>/
```

Struttura attuale:

```text
scenario.json
scenario_status.json
scenario_copy_manifest.json
12_controlled_scenarios.json
scenario_comparison.json
base_snapshot/
run/
```

Azioni scenario supportate per ora:

```text
drive_node_voltage
change_source_value
close_switch
```

`drive_node_voltage` aggiunge o aggiorna una sorgente di test su un nodo della
run scenario, per esempio `VSCENARIO_N002 N002 0 DC 5`.

`change_source_value` modifica il valore di una sorgente SPICE gia presente
nella netlist copiata dello scenario, per esempio `VVCC N001 0 DC 10`.

`close_switch` chiude uno switch gia riconosciuto in `06_component_rules.json`
inserendo nella netlist scenario una piccola resistenza tra i suoi due nodi, per
esempio `RSCENARIO_switch25_1 N001 0 1m`.

I valori devono essere concreti: uno scenario con `value: "unknown"` viene
fermato e marcato come non eseguibile.

`base_snapshot/` contiene una copia degli output originali. `run/` contiene la
copia modificabile dello scenario.

Esempio di primitiva `drive_node_voltage`:

```json
{
  "type": "drive_node_voltage",
  "target": "N002",
  "value": "5V"
}
```

Questa azione aggiunge nella netlist scenario una sorgente del tipo:

```spice
VSCENARIO_N002 N002 0 DC 5
```

Lo step 12 puo anche eseguire ngspice sulla run scenario con `--run-spice` e
creare un confronto automatico base vs scenario usando le grandezze elencate in
`scenario.json -> compare`.

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

## Web chat locale

La web chat si avvia separatamente dalla pipeline principale.

Quindi, se vuoi solo eseguire la pipeline tecnica `01-08`, non devi fare nulla
di speciale: basta usare `run_pipeline2.py` come nei comandi precedenti.

Per aprire il sito su un circuito gia generato, per esempio `a01`:

```powershell
python scripts\pipeline_2.0\json_to_spice\09_web_chat.py --batch batchA --circuit a01
```

Se vuoi eseguire anche gli scenari direttamente dalla chat, conviene passare
anche il path di ngspice:

```powershell
python scripts\pipeline_2.0\json_to_spice\09_web_chat.py --batch batchA --circuit a01 --ngspice-executable "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

Lo script avvia un server locale temporaneo e apre il browser su:

```text
http://127.0.0.1:8765/
```

Quando non vuoi usare il sito, semplicemente non eseguire `09_web_chat.py`.

Per chiudere il sito:

```text
Ctrl+C nel terminale dove sta girando 09_web_chat.py
```

Se la porta `8765` e gia occupata:

```powershell
python scripts\pipeline_2.0\json_to_spice\09_web_chat.py --batch batchA --circuit a01 --port 8766
```

Se non vuoi aprire automaticamente il browser:

```powershell
python scripts\pipeline_2.0\json_to_spice\09_web_chat.py --batch batchA --circuit a01 --no-browser
```

In quel caso puoi aprire manualmente:

```text
http://127.0.0.1:8765/
```

Per ora il sito non rilancia la pipeline tecnica `01-08`. Legge gli output gia
presenti in:

```text
outputs/pipeline2.0/<batch>/<circuit>/
```

Esempio:

```text
outputs/pipeline2.0/batchA/a01/
```

Se quella cartella non esiste, prima bisogna eseguire la pipeline:

```powershell
python scripts\pipeline_2.0\run_pipeline2.py --batch batchA --circuits a01 --run-spice --ngspice-executable "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

Quando scrivi un sintomo nella chat, il sito esegue il flusso agente read-only:

```text
/api/chat
-> aggiorna 10_diagnostic_context.json con user_problem
-> genera 11_agent_input_preview_chat.md
-> genera 11_agent_prompt_chat.md
-> chiama OpenAI tramite 11_agent_readonly
-> salva 11_agent_response_chat.md
-> mostra la risposta nella chat
```

Per esempio, su `a01` puoi scrivere:

```text
Perche la lampada non si accende?
```

La risposta viene mostrata nel sito e salvata anche in:

```text
outputs/pipeline2.0/batchA/a01/11_agent_response_chat.md
```

Quando scrivi:

```text
esegui scenario 1
```

il sito ora:

```text
crea la cartella scenario
copia base_snapshot/ e run/
applica lo scenario alla netlist in run/
esegue ngspice sulla run scenario
crea scenario_comparison.json
ricarica la pagina su ?run=scenario_1
```

Flusso corrente:

```text
run_pipeline2.py -> genera output 01-08/10
09_web_chat.py  -> apre sito locale, mostra gli output e chiama 10/11 dalla chat
```

Flusso futuro:

```text
run_pipeline2.py -> genera output 01-08/10
09_web_chat.py  -> chat utente
chat            -> chiama 10 e 11
utente          -> sceglie scenario in chat
chat            -> chiama 12
```

## Scenari controllati

Gli scenari controllati partono dalla risposta dell'agente.

Flusso attuale dalla web chat:

```text
utente scrive un sintomo
-> 09 chiama 10 e 11
-> agente propone scenari con blocchi JSON
-> utente scrive "esegui scenario 1"
-> 09 recupera lo scenario JSON scelto
-> 09 crea outputs/pipeline2.0/<batch>/<circuit>/scenarios/scenario_1/
-> 09 copia la base run in base_snapshot/ e run/
-> 09 chiama 12
-> 12 applica le azioni supportate alla netlist in run/
```

La base run originale resta invariata.

Esempio per `a01`:

```text
outputs/pipeline2.0/batchA/a01/scenarios/scenario_1/
```

File principali:

```text
scenario.json                       scenario scelto dall'utente
scenario_status.json                stato corrente dello scenario
scenario_copy_manifest.json         file copiati dalla base run
12_controlled_scenarios.json        report dello step 12
scenario_comparison.json            confronto base vs scenario, se SPICE e stato eseguito
base_snapshot/                      copia non modificata della base run
run/                                copia scenario modificabile
```

### Applicare uno scenario senza SPICE

Se la cartella scenario esiste gia, si puo applicare lo scenario da terminale:

```powershell
python scripts\pipeline_2.0\json_to_spice\12_controlled_scenarios.py --scenario-dir outputs\pipeline2.0\batchA\a01\scenarios\scenario_1
```

Questo comando:

```text
legge scenario.json
modifica solo run/07_netlist.cir
salva 12_controlled_scenarios.json
non esegue ngspice
```

### Applicare ed eseguire SPICE

Per eseguire anche ngspice sulla run dello scenario:

```powershell
python scripts\pipeline_2.0\json_to_spice\12_controlled_scenarios.py --scenario-dir outputs\pipeline2.0\batchA\a01\scenarios\scenario_1 --run-spice --ngspice "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

Output in:

```text
outputs/pipeline2.0/batchA/a01/scenarios/scenario_1/run/08_spice_run.json
outputs/pipeline2.0/batchA/a01/scenarios/scenario_1/run/08_ngspice_stdout.txt
outputs/pipeline2.0/batchA/a01/scenarios/scenario_1/run/08_ngspice_stderr.txt
outputs/pipeline2.0/batchA/a01/scenarios/scenario_1/scenario_comparison.json
```

Per `a01/scenario_1`, il confronto atteso e:

```text
v(N002):        0 -> 5 V
v(N004):        0 -> 0.2380952 V
i(Rlamp13_1):   0 -> 0.0047619 A
```

Quindi lo scenario conferma che alimentando `N002` il ramo della lampada riceve
corrente.

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

Se viene usata la web chat, possono essere prodotti anche:

```text
11_agent_input_preview_chat.md
11_agent_prompt_chat.md
11_agent_response_chat.md
```

Se viene scelto uno scenario dalla chat, viene creata una cartella:

```text
scenarios/<scenario_id>/
```

con:

```text
scenario.json
scenario_status.json
scenario_copy_manifest.json
12_controlled_scenarios.json
scenario_comparison.json, se SPICE scenario e stato eseguito
base_snapshot/
run/
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

- `09_web_chat.py` avvia un sito locale temporaneo per leggere gli output;
- `10_build_diagnostic_context.py` crea il manifest;
- `11_agent_readonly.py` crea preview, prompt e risposta agente;
- OpenAI e collegato alla web chat tramite modello default `gpt-5.4`;
- `12_controlled_scenarios.py` applica scenari generali semplici
  (`drive_node_voltage`, `change_source_value`, `close_switch`), puo eseguire
  ngspice e crea un confronto base/scenario.

Regole sugli scenari:

- `11` propone soltanto scenari;
- uno scenario parte solo se l'utente lo sceglie esplicitamente;
- gli output originali non vanno mai sovrascritti;
- lo scenario deve lavorare su copie degli output base;
- la cartella scenario deve essere separata dalla cartella base del circuito.

Flusso tecnico corrente:

```text
01 -> 02 -> 03 -> 04 -> 06 -> 07 -> 08 -> 10
09 -> sito locale temporaneo + chat
11 -> agente read-only chiamato da terminale o dalla chat
12 -> scenario controllato su copia separata
```

Per la tesi e una direzione interessante per descrivere un sistema interattivo
che aiuta l'utente a trasformare il circuito riconosciuto in una simulazione
SPICE eseguibile.

## Step futuri

I prossimi step saranno:

- `09_web_chat.py`: migliorare sidebar scenari e scelta modello;
- `10_build_diagnostic_context.py`: implementato come manifest leggero;
- `11_agent_readonly.py`: implementato fino a preview, prompt e chiamata
  OpenAI opzionale con `--run-agent`;
- `12_controlled_scenarios.py`: estendere in futuro le primitive oltre
  `drive_node_voltage`, `change_source_value` e `close_switch`;
- aggiungere la risposta agente dopo lo scenario, basata su
  `scenario_comparison.json`;
- in seguito, aggiungere il viewer SPICE animato.
