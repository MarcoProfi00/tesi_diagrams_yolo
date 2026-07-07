# Pipeline 2.0 - Graph JSON to SPICE

Questo documento riassume cosa fa oggi la Pipeline 2.0, quali file usa e come
eseguirla da terminale.

La Pipeline 2.0 parte dai Graph JSON prodotti dalla Pipeline 1.0 e costruisce
una catena che porta a:

```text
graph json -> nodi elettrici -> valori -> regole SPICE -> netlist -> ngspice
-> contesto diagnostico -> agente -> scenari controllati
```

## Input principali

Per ogni circuito servono:

- Graph JSON della Pipeline 1.0:
  `outputs/pipeline1.0/<batch>/06_graph_report/<circuit>/<circuit>.json`
- valori manuali:
  `metadata/pipeline2_manual_values/<batch>/<circuit>_values.yaml`
- mapping classi SPICE:
  `metadata/pipeline2_spice_classes.yaml`

Esempio:

```text
outputs/pipeline1.0/batchA/06_graph_report/a01/a01.json
metadata/pipeline2_manual_values/batchA/a01_values.yaml
metadata/pipeline2_spice_classes.yaml
```

## Step implementati

### 01 - IO

Legge il Graph JSON della Pipeline 1.0 e crea la cartella output della
Pipeline 2.0.

Output:

```text
01_graph.json
```

### 02 - Normalize

Normalizza il Graph JSON:

- componenti
- terminali
- connessioni
- statistiche
- warning di normalizzazione

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

Questo step non genera ancora SPICE. Controlla solo se i componenti hanno i
valori necessari.

Output:

```text
04_values_bound.json
```

### 05 - Device Profiles

Per ora non e implementato.

Servira piu avanti per componenti complessi, per esempio integrati,
transistor, opamp o componenti con pin-map specifico.

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

Attualmente emette, tra gli altri:

- resistenze -> `R`
- lampade -> resistenza equivalente `R`
- batterie/supply -> `V`
- condensatori -> `C`
- LED/diodi -> `D` + `.model`

Alcuni componenti strutturali non vengono emessi direttamente, per esempio:

- GND
- connector
- switch aperti, che restano come commento

Output:

```text
07_netlist.cir
07_spice_emit_report.json
```

### 08 - SPICE Run

Esegue opzionalmente ngspice sulla netlist prodotta dallo step 07.

Lo step 08 parte solo se si usa `--run-spice`.

Output:

```text
08_spice_run.json
08_ngspice_stdout.txt
08_ngspice_stderr.txt
```

Se la netlist contiene una `.tran`, possono comparire anche:

```text
08_tran.csv
08_tran_plot.png
08_tran_plot.svg
```

Gli output tecnici dello step 08 sono in inglese.

### 09 - Web Chat

Avvia una piccola interfaccia web locale temporanea per:

- guardare gli output del circuito
- vedere l'immagine originale
- leggere netlist, stdout, stderr e plot
- parlare con l'agente diagnostico
- eseguire scenari controllati

L'immagine viene mostrata nel sito, ma non viene passata di default al modello:
la chat resta graph-grounded e usa l'immagine solo come fallback nei casi
topologicamente sospetti o quando serve davvero.

Lo step 09 non e un backend permanente:

- non usa database
- non espone API pubbliche
- non richiede login
- vive solo finche il comando resta in esecuzione

La chat salva file separati per non sovrascrivere altri output:

```text
11_agent_input_preview_chat.md
11_agent_prompt_chat.md
11_agent_response_chat.md
```

Quando la chat viene aperta su `--experiment experiment2`, salva anche una
history ufficiale locale per circuito in:

```text
outputs/pipeline2.0/<batch>/<experiment>/<circuit>/experiment2_chat/
  chat_history.json
  chat_history.md
```

In questa modalita:

- `chat_history.json` e la sorgente ufficiale e append-only della conversazione;
- `chat_history.md` e una vista leggibile rigenerata dal JSON;
- ogni messaggio utente viene salvato come evento `user`;
- ogni risposta agente viene salvata come evento `assistant`;
- ogni scenario eseguito viene salvato come evento `system`.

Quando l'utente scrive frasi come:

```text
esegui scenario 1
esegui questo scenario
esegui lo scenario appena proposto
esegui l'ultimo
mostra scenari
```

lo step `09` riconosce la scelta e, in `experiment2`, usa il
`scenario_registry.json` locale come sorgente ufficiale degli scenari
proposti/eseguiti. Il JSON tecnico non viene piu recuperato solo dall'ultima
risposta agente: viene letto dal registry globale del circuito e poi passato
allo step `12`.

La chat supporta anche un selettore modello.

Per Esperimento 2 la conversazione ufficiale vive nei file locali sopra. Il
browser continua a mantenere una cache locale della UI, ma quando riapri la
pagina il contenuto visibile viene ricostruito dalla history server-side.

### 10 - Diagnostic Context

Costruisce il manifest diagnostico leggero per l'agente.

Non duplica tutti gli output in un file enorme. Salva:

- path degli artefatti
- mini-summary tecnica
- regole operative per l'agente
- scenari gia eseguiti, se presenti
- budget scenari per il circuito

Output:

```text
10_diagnostic_context.json
```

Se esistono scenari in:

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

Lo step 10 include anche `scenario_budget`, con limite massimo di `5` scenari
eseguibili per circuito.

### 11 - Agent Readonly

Prima base dell'agente diagnostico.

Di default non chiama OpenAI. Legge `10_diagnostic_context.json`, carica gli
artefatti indicati nel manifest e genera:

```text
11_agent_input_preview.md
11_agent_prompt.md
```

Il preview serve a controllare cosa viene caricato. Il prompt e il testo che
viene mandato al modello quando si usa `--run-agent`.

Se viene passato `--run-agent`, lo step chiama OpenAI e salva:

```text
11_agent_response.md
```

Lo step 11 e read-only:

- non modifica i file originali
- non crea scenari
- non copia output
- non esegue ngspice
- interpreta la base run e gli eventuali scenari gia eseguiti

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
Scenari elettrici / di pilotaggio:
- drive_node_voltage
- change_source_value
- change_component_value
- close_switch

Scenari topologici controllati:
- connect_nodes
- feed_nodes_from_source_node
```

`drive_node_voltage` aggiunge o aggiorna una sorgente di test su un nodo della
run scenario.

`change_source_value` modifica il valore di una sorgente SPICE gia presente
nella netlist copiata dello scenario.

`change_component_value` modifica il valore di un componente semplice gia
emesso nella netlist scenario, per esempio una resistenza, un condensatore,
un'induttanza o un equivalente gia tradotto come `R`, `C` o `L`.

`close_switch` chiude uno switch gia riconosciuto inserendo una piccola
resistenza tra i suoi due nodi.

`connect_nodes` collega due nodi gia esistenti della node map con una piccola
resistenza di scenario. E la primitiva topologica minima per testare continuita,
jumper, bridge, wire o collegamenti mancanti tra nodi gia riconosciuti.

`feed_nodes_from_source_node` propaga in modo controllato un nodo sorgente gia
alimentato verso uno o piu nodi target. Internamente viene tradotta in
collegamenti resistivi quasi ideali nella netlist scenario, ma resta distinta da
`connect_nodes` perche rappresenta una ipotesi diagnostica di propagazione
dell'alimentazione.

I valori devono essere concreti: uno scenario con `value: "unknown"` viene
fermato e marcato come non eseguibile.

Lo step 12 puo anche eseguire ngspice sulla run scenario con `--run-spice` e
creare un confronto automatico base vs scenario usando le grandezze elencate in
`scenario.json -> compare`.

## Comando principale

Da terminale, nella root del progetto:

```powershell
python scripts\pipeline_2.0\run_pipeline2.py --batch <batch> --circuits <circuit_1> <circuit_2>
```

Questo comando esegue la pipeline fino alla generazione della netlist SPICE,
senza lanciare ngspice.

Gli output vengono creati in:

```text
outputs/pipeline2.0/<batch>/<circuit>/
```

Esempio:

```text
outputs/pipeline2.0/batchA/a01/
```

### Output per esperimento

Per mantenere separati esperimenti diversi, la Pipeline 2.0 puo usare anche una
root sperimentale:

```text
outputs/pipeline2.0/<batch>/<experiment>/<circuit>/
```

Esempio:

```text
outputs/pipeline2.0/batchA/experiment2/a01/
```

Questa struttura serve quando vogliamo confrontare piu esperimenti partendo
dalla stessa base tecnica `01-08`, ma con chat, scenari, budget e conclusioni
separati.

Per inizializzare una root esperimento senza rigenerare la pipeline tecnica si
usa:

```powershell
python scripts\pipeline_2.0\prepare_experiment_outputs.py --batch batchA --experiment experiment2 --circuits a01 a02 a03 a04 a05 a06 a07 a08 a09 a10 --mode base-only
```

`base-only` copia solo gli artefatti top-level `01-08` dalla root storica del
circuito. Non copia `10`, `11` o `scenarios`, quindi l'esperimento riparte con
manifest, agente e scenari puliti.

Per congelare invece uno stato sperimentale completo, inclusi `10`, `11` e
`scenarios`, si usa:

```powershell
python scripts\pipeline_2.0\prepare_experiment_outputs.py --batch batchA --experiment experiment1 --circuits a01 a02 a03 a04 a05 a06 a07 a08 a09 a10 --mode full
```

Lo script non sovrascrive file gia presenti nella destinazione.

Per eseguire anche ngspice su un circuito:

```powershell
python scripts\pipeline_2.0\run_pipeline2.py --batch <batch> --circuits <circuit> --run-spice
```

Per forzare esplicitamente l'eseguibile console di ngspice:

```powershell
python scripts\pipeline_2.0\run_pipeline2.py --batch <batch> --circuits <circuit> --run-spice --ngspice-executable ngspice_con
```

Nel nostro ambiente, se `ngspice_con` non e nel PATH, si puo usare direttamente
il path completo:

```powershell
python scripts\pipeline_2.0\run_pipeline2.py --batch <batch> --circuits <circuit> --run-spice --ngspice-executable "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

Per rigenerare la pipeline su piu circuiti:

```powershell
python scripts\pipeline_2.0\run_pipeline2.py --batch <batch> --circuits <circuit_1> <circuit_2> <circuit_3>
```

Per rigenerare anche SPICE sugli stessi circuiti:

```powershell
python scripts\pipeline_2.0\run_pipeline2.py --batch <batch> --circuits <circuit_1> <circuit_2> <circuit_3> --run-spice --ngspice-executable "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

Se si vuole rigenerare deliberatamente una root sperimentale, si puo aggiungere
`--experiment`:

```powershell
python scripts\pipeline_2.0\run_pipeline2.py --batch <batch> --experiment <experiment> --circuits <circuit> --run-spice --ngspice-executable "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

Per gli esperimenti di confronto e preferibile usare questa opzione solo quando
si vuole cambiare anche la baseline tecnica. Se l'obiettivo e confrontare
agente/scenari sulla stessa base `01-08`, usare prima
`prepare_experiment_outputs.py --mode base-only`.

## Web chat locale

La web chat si avvia separatamente dalla pipeline principale.

Se vuoi solo eseguire la pipeline tecnica `01-08`, basta usare
`run_pipeline2.py`.

Per aprire il sito su un circuito gia generato:

```powershell
python scripts\pipeline_2.0\json_to_spice\09_web_chat.py --batch <batch> --circuit <circuit>
```

Per aprire invece una root sperimentale separata:

```powershell
python scripts\pipeline_2.0\json_to_spice\09_web_chat.py --batch <batch> --experiment <experiment> --circuit <circuit>
```

Esempio:

```powershell
python scripts\pipeline_2.0\json_to_spice\09_web_chat.py --batch batchA --experiment experiment2 --circuit a01
```

Se vuoi eseguire anche gli scenari direttamente dalla chat, conviene passare
anche il path di ngspice:

```powershell
python scripts\pipeline_2.0\json_to_spice\09_web_chat.py --batch <batch> --circuit <circuit> --ngspice-executable "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

Con esperimento:

```powershell
python scripts\pipeline_2.0\json_to_spice\09_web_chat.py --batch <batch> --experiment <experiment> --circuit <circuit> --ngspice-executable "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

Lo script avvia un server locale temporaneo e apre il browser su:

```text
http://127.0.0.1:8765/
```

Per chiudere il sito:

```text
Ctrl+C nel terminale dove sta girando 09_web_chat.py
```

Se la porta `8765` e gia occupata:

```powershell
python scripts\pipeline_2.0\json_to_spice\09_web_chat.py --batch <batch> --circuit <circuit> --port 8766
```

Se non vuoi aprire automaticamente il browser:

```powershell
python scripts\pipeline_2.0\json_to_spice\09_web_chat.py --batch <batch> --circuit <circuit> --no-browser
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

oppure, quando si usa `--experiment`:

```text
outputs/pipeline2.0/<batch>/<experiment>/<circuit>/
```

Se quella cartella non esiste, prima bisogna eseguire la pipeline:

```powershell
python scripts\pipeline_2.0\run_pipeline2.py --batch <batch> --circuits <circuit> --run-spice --ngspice-executable "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
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

La chat riconosce anche richieste di esecuzione scenario:

```text
esegui scenario 1
esegui questo scenario
esegui lo scenario appena proposto
esegui l'ultimo
mostra scenari
```

Quando scrivi una richiesta di questo tipo, il sito:

```text
crea la cartella scenario
copia base_snapshot/ e run/
applica lo scenario alla netlist in run/
esegue ngspice sulla run scenario, se disponibile
crea scenario_comparison.json
ricarica la pagina sulla run scenario
```

Ogni scenario riparte sempre dalla base run, non dallo scenario precedente.
Quindi, quando l'agente propone un nuovo scenario dopo aver letto risultati gia
eseguiti, lo scenario deve essere autosufficiente: se una nuova ipotesi richiede
una condizione abilitante gia testata prima, quella azione deve essere inclusa
di nuovo nello stesso JSON dello scenario.

Esempio:

```text
scenario_1 chiude uno switch e porta alimentazione a N002;
il test successivo vuole collegare N002 a N003;
il nuovo scenario corretto e close_switch + connect_nodes N002 -> N003.
```

Non va trattato come se `scenario_1` restasse attivo automaticamente.

Il circuito mantiene un budget massimo di `5` scenari eseguiti/eseguibili.

Questo limite vale sulle run scenario realmente lanciate, non sul numero di
proposte che possono comparire nella conversazione o nel registry.

Raggiunto il limite di esecuzione, la chat non crea una sesta run scenario e
l'agente deve chiudere con una conclusione diagnostica finale.

Quando si usa `--experiment`, anche la memoria browser della chat viene separata
per batch, esperimento e circuito. Questo evita di mescolare conversazioni di
esperimenti diversi.

In particolare, con `--experiment experiment2`, il bottone `Clear` pulisce sia
la cache locale del browser sia la history ufficiale in
`experiment2_chat/chat_history.json` e il registry scenari ufficiale in
`experiment2_chat/scenario_registry.json`.

## Scenari controllati

Gli scenari controllati partono dalla risposta dell'agente.

Flusso attuale dalla web chat:

```text
utente scrive un sintomo
-> 09 chiama 10 e 11
-> agente propone scenari con blocchi JSON
-> utente sceglie uno scenario
-> 09 recupera lo scenario JSON scelto
-> 09 crea outputs/pipeline2.0/<batch>/<circuit>/scenarios/<scenario_id>/
-> 09 copia la base run in base_snapshot/ e run/
-> 09 chiama 12
-> 12 applica le azioni supportate alla netlist in run/
```

La base run originale resta invariata.

File principali di una scenario run:

```text
scenario.json
scenario_status.json
scenario_copy_manifest.json
12_controlled_scenarios.json
scenario_comparison.json
base_snapshot/
run/
```

### Applicare uno scenario senza SPICE

Se la cartella scenario esiste gia, si puo applicare lo scenario da terminale:

```powershell
python scripts\pipeline_2.0\json_to_spice\12_controlled_scenarios.py --scenario-dir outputs\pipeline2.0\<batch>\<circuit>\scenarios\<scenario_id>
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
python scripts\pipeline_2.0\json_to_spice\12_controlled_scenarios.py --scenario-dir outputs\pipeline2.0\<batch>\<circuit>\scenarios\<scenario_id> --run-spice --ngspice "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

Esempio di confronto atteso:

```text
v(<NODE>): cambia rispetto alla base run
v(<LOAD_NODE>): si attiva oppure resta invariato
i(<LOAD>): cresce, resta nulla oppure cambia solo parzialmente
```

## Comandi agente read-only

Lo step 11 si esegue separatamente dal comando principale della pipeline.

Prima di eseguire l'agente, il circuito deve avere gia gli output della
Pipeline 2.0, in particolare:

```text
10_diagnostic_context.json
```

Se vuoi partire da zero su un circuito, esegui prima:

```powershell
python scripts\pipeline_2.0\run_pipeline2.py --batch <batch> --circuits <circuit> --run-spice --ngspice-executable "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

### Solo prompt, senza OpenAI

Per generare preview e prompt dell'agente su un circuito, senza chiamare
OpenAI:

```powershell
python scripts\pipeline_2.0\json_to_spice\11_agent_readonly.py --batch <batch> --circuit <circuit> --question "Perche la lampada non si accende?"
```

Output:

```text
outputs/pipeline2.0/<batch>/<circuit>/11_agent_input_preview.md
outputs/pipeline2.0/<batch>/<circuit>/11_agent_prompt.md
```

Con una root sperimentale si puo usare:

```powershell
python scripts\pipeline_2.0\json_to_spice\11_agent_readonly.py --batch <batch> --experiment <experiment> --circuit <circuit> --question "Perche la lampada non si accende?"
```

Output:

```text
outputs/pipeline2.0/<batch>/<experiment>/<circuit>/11_agent_input_preview.md
outputs/pipeline2.0/<batch>/<experiment>/<circuit>/11_agent_prompt.md
```

Si puo anche passare direttamente il manifest:

```powershell
python scripts\pipeline_2.0\json_to_spice\11_agent_readonly.py --context outputs\pipeline2.0\<batch>\<circuit>\10_diagnostic_context.json --question "Perche la lampada non si accende?"
```

### Agente con OpenAI

Per chiamare OpenAI bisogna aggiungere `--run-agent`.

Comando consigliato con il modello default corrente:

```powershell
python scripts\pipeline_2.0\json_to_spice\11_agent_readonly.py --batch <batch> --circuit <circuit> --question "Perche la lampada non si accende?" --run-agent
```

Output aggiuntivo:

```text
outputs/pipeline2.0/<batch>/<circuit>/11_agent_response.md
```

Per scegliere esplicitamente un modello:

```powershell
python scripts\pipeline_2.0\json_to_spice\11_agent_readonly.py --batch <batch> --circuit <circuit> --question "Perche la lampada non si accende?" --run-agent --model gpt-5.4
```

Modello default attuale nel codice:

```text
gpt-5.4
```

Modelli supportati attualmente:

```text
gpt-5.4
gpt-5.5
gpt-5.4-mini
gpt-5-mini
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

Per eseguire manualmente una netlist:

```powershell
& "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe" -b outputs\pipeline2.0\<batch>\<circuit>\07_netlist.cir
```

Il flag:

```text
-b
```

indica batch mode: ngspice esegue la netlist senza aprire l'interfaccia
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
ngspice_con -b outputs\pipeline2.0\<batch>\<circuit>\07_netlist.cir
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

E questo comando esegue manualmente una netlist:

```powershell
ngspice_con -b outputs\pipeline2.0\<batch>\<circuit>\07_netlist.cir
```

La pipeline puo fare la stessa cosa tramite lo step 08:

```powershell
python scripts\pipeline_2.0\run_pipeline2.py --batch <batch> --circuits <circuit> --run-spice --ngspice-executable ngspice_con
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
scenario_comparison.json
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

Piu avanti si possono usare scenari simulativi per chiudere temporaneamente uno
switch riconosciuto.

## Nota su chat e agente

L'idea non e sostituire la pipeline, ma guidarla:

```text
utente: descrive il sintomo
agente: legge 10_diagnostic_context.json e gli output 01-08
agente: spiega il risultato SPICE
agente: propone scenari diagnostici candidati
utente: sceglie uno scenario
pipeline: crea una cartella scenario separata
pipeline: copia gli output originali
pipeline: modifica solo le copie
pipeline: rilancia SPICE sullo scenario
agente: confronta run base e run scenario
```

Versione attuale:

- `09_web_chat.py` avvia un sito locale temporaneo per leggere gli output
- `10_build_diagnostic_context.py` crea il manifest
- `11_agent_readonly.py` crea preview, prompt e risposta agente
- OpenAI e collegato sia da CLI sia dalla web chat
- `12_controlled_scenarios.py` applica scenari controllati
  elettrici/topologici (`drive_node_voltage`, `change_source_value`,
  `change_component_value`, `close_switch`, `connect_nodes`,
  `feed_nodes_from_source_node`), puo eseguire ngspice e crea un confronto
  base/scenario

Regole sugli scenari:

- `11` propone soltanto scenari
- uno scenario parte solo se l'utente lo sceglie esplicitamente
- gli output originali non vanno mai sovrascritti
- lo scenario lavora su copie degli output base
- la cartella scenario e separata dalla cartella base del circuito
- il budget massimo attuale e `5` scenari eseguibili per circuito

## Step futuri

I prossimi step saranno:

- migliorare ulteriormente la UI di `09_web_chat.py`
- estendere in futuro le primitive di `12_controlled_scenarios.py`
- consolidare la risposta agente dopo lo scenario, basata su
  `scenario_comparison.json`
- consolidare la chiusura finale dell'agente quando il budget scenari e esaurito
- aggiungere in seguito il viewer SPICE animato
