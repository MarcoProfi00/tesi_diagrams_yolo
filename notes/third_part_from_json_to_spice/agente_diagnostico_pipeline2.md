# Agente diagnostico per Pipeline 2.0

Questo documento descrive il ruolo dell'agente AI nella Pipeline 2.0, cioe
nella parte che estende il progetto dal Graph JSON alla generazione SPICE, alla
simulazione e alla diagnosi assistita.

L'idea centrale e semplice:

```text
pipeline tecnica -> risultati SPICE -> contesto diagnostico -> agente AI
```

L'agente non sostituisce la pipeline e non deve inventare collegamenti, valori o
modelli. Deve usare gli output prodotti dalla pipeline come evidenze
controllate, spiegare i risultati all'utente e, in una fase successiva, proporre
scenari simulativi verificabili.

## Obiettivo

La Pipeline 2.0 produce molti output tecnici: nodi elettrici, valori associati,
regole sui componenti, netlist SPICE, log ngspice e report. Questi file sono
utili per la validazione scientifica, ma non sono immediati per un utente finale.

L'agente serve a trasformare questi output in una interfaccia interrogabile.

L'utente deve poter fare domande naturali, ad esempio:

```text
Perche la lampada non si accende?
Il LED e alimentato?
La simulazione SPICE e andata a buon fine?
Quali valori mancano?
Quale nodo devo controllare fisicamente?
```

L'agente finale puo quindi essere descritto come:

```text
una chat diagnostica grounded su Graph JSON, node map, valori dichiarati,
regole componenti, netlist, risultati SPICE, report elettrico, device profile
e datasheet.
```

La parola chiave e `grounded`: ogni risposta deve distinguere tra dati certi,
risultati simulati, assunzioni manuali, vincoli da datasheet e ipotesi non
ancora verificate.

## Punto di aggancio nella pipeline

L'agente deve essere agganciato dopo l'esecuzione SPICE.

La sequenza di riferimento e:

```text
01_io
-> 02_normalize
-> 03_node_map
-> 04_values
-> 05_device_profiles
-> 06_component_rules
-> 07_spice_emit
-> 08_spice_run
-> 10_build_diagnostic_context
-> 11_agent_readonly
-> agente AI
```

Il punto minimo per attivare l'agente e dopo `08_spice_run.py`, perche prima di
quello esiste solo una netlist generata, mentre dopo `08` esiste anche il
risultato reale di ngspice.

Per ora lo step `09_summarize_spice.py` viene lasciato come placeholder o
saltato. La scelta corrente e non creare un riassunto intermedio troppo
filtrato: l'agente deve poter ricevere gli output reali della pipeline, raccolti
e ordinati dallo step `10_build_diagnostic_context.py`.

Lo step `10` non deve essere trattato come una sintesi interpretativa che
sostituisce i file originali. Deve essere un contenitore di evidenze:

```text
10_diagnostic_context.json = output 01-08 raccolti e ordinati
```

L'agente deve usare il contenuto grezzo incorporato nel context e i path ai file
originali come fonte di verita. Se una conclusione dipende da un dettaglio
specifico, deve riferirsi alla sezione/file originale: node map, component
rules, netlist, stdout, stderr o report SPICE.

Lo step `08` produce fatti grezzi come:

```text
08_spice_run.json
08_ngspice_stdout.txt
08_ngspice_stderr.txt
```

Questi file, insieme agli output precedenti, permettono all'agente di
confrontare il circuito riconosciuto con il comportamento simulato.

## Input dell'agente

Per ogni circuito, l'agente dovrebbe ricevere un pacchetto diagnostico costruito
dalla pipeline.

Input principali:

```text
problema utente
01_graph.json
02_normalized_circuit.json
03_node_map.json
04_values_bound.json
05_device_profiles.json / device_profiles.yaml
06_component_rules.json
07_netlist.cir
07_spice_emit_report.json
08_spice_run.json
08_ngspice_stdout.txt
08_ngspice_stderr.txt
09_spice_summary.json
10_diagnostic_context.json
11_agent_response.md, quando l'agente viene eseguito
datasheet_extract.txt, se disponibile
```

Non tutti gli input sono sempre disponibili. La pipeline deve produrre il
massimo livello possibile di analisi per ogni circuito.

### Uso dell'immagine originale

L'immagine originale non deve essere passata sempre all'agente.

La regola corrente e:

```text
Default: agente senza immagine.
Fallback: agente puo richiedere l'immagine se gli output strutturati indicano
un possibile errore del Graph JSON.
```

Questo e importante per non vanificare il lavoro della Pipeline 1.0. L'agente
deve prima ragionare sui dati strutturati prodotti dalla pipeline:

```text
Graph JSON
node map
values bound
component rules
netlist
risultati ngspice
stdout/stderr
```

Solo se questi dati mostrano incoerenze forti, l'agente puo chiedere accesso
all'immagine originale come supporto diagnostico.

Esempi di condizioni in cui l'agente puo richiedere l'immagine:

- terminali importanti scollegati;
- nodi singleton su sorgenti, carichi o switch;
- assenza di nodo di riferimento;
- SPICE fallito per matrice singolare o nodi flottanti;
- componenti importanti saltati per topologia o valori mancanti;
- differenza sospetta tra graph, netlist e risultato SPICE;
- componenti complessi rappresentati in modo parziale, come rele o
  trasformatore.

Nel caso `a03`, per esempio, l'agente dovrebbe prima leggere graph, node map,
netlist e stderr. Solo dopo aver rilevato batteria spezzata, nodi singleton,
ramo AC non chiuso e rele rappresentato come `Inductor` + `Switch`, puo
richiedere l'immagine per proporre scenari correttivi piu affidabili.

Questa distinzione crea due modalita:

```text
graph-grounded agent
image-assisted agent
```

La modalita base e `graph-grounded`: l'agente si fida della pipeline e lavora
sui suoi output. La modalita `image-assisted` e un fallback diagnostico, usato
solo quando ci sono evidenze che il graph potrebbe non rappresentare
correttamente il circuito.

## Cosa deve fare l'agente

L'agente deve aiutare l'utente a capire il circuito e i risultati della
pipeline.

Compiti principali:

- spiegare se ngspice e stato eseguito correttamente;
- interpretare tensioni, correnti e warning SPICE;
- collegare i nodi SPICE ai terminali reali tramite `03_node_map.json`;
- spiegare quali componenti sono stati emessi, semplificati, saltati o non
  supportati;
- rispondere al problema dell'utente usando solo le evidenze disponibili;
- dichiarare cosa e certo, cosa e simulato e cosa e solo ipotesi;
- proporre controlli pratici misurabili;
- proporre scenari simulativi controllati quando il risultato base non basta.

L'agente non deve:

- inventare collegamenti assenti nel Graph JSON;
- inventare valori assenti nei file di valori;
- fingere che un circuito `PARTIAL` sia stato simulato completamente;
- modificare liberamente la netlist SPICE;
- simulare mentalmente componenti complessi senza modello.

## Stati del circuito

L'agente deve sempre conoscere lo stato del circuito.

### READY

Il circuito ha valori e modelli sufficienti. La netlist e eseguibile e SPICE
produce risultati utilizzabili.

L'agente puo usare:

- Graph JSON;
- node map;
- valori;
- netlist SPICE;
- risultati SPICE;
- report elettrico;
- eventuali datasheet/device profile.

In questo stato puo rispondere anche con numeri simulati.

### PARTIAL

Il circuito e parzialmente analizzabile. Alcuni componenti possono essere
semplificati, saltati o non supportati.

L'agente deve essere prudente. Puo usare:

- nodi ricostruiti;
- warning;
- valori disponibili;
- netlist parziale;
- controlli statici;
- eventuali datasheet/device profile.

Non deve fingere che SPICE abbia verificato tutto il circuito.

### NOT_READY

Il circuito non ha dati sufficienti per una simulazione utile.

L'agente deve spiegare il motivo, ad esempio:

- JSON incompleto;
- terminali scollegati;
- valori mancanti;
- modelli mancanti;
- IC troppo complesso;
- pin mapping non affidabile.

Anche in questo caso puo fornire una diagnosi topologica preliminare.

## Regole di risposta

Ogni risposta dell'agente dovrebbe separare chiaramente:

```text
fatti dal Graph JSON
valori dichiarati o assunti
risultati SPICE
vincoli da datasheet/device profile
ipotesi diagnostiche
controlli pratici consigliati
```

### Non inventare collegamenti

Se un collegamento non e nel JSON, l'agente deve dirlo:

```text
Il collegamento non risulta nel Graph JSON. Potrebbe essere un errore di
riconoscimento o una connessione assente nello schema.
```

### Non inventare valori

Se un valore manca, va dichiarato:

```text
Il valore di R3 non e disponibile, quindi non posso stimare numericamente la
corrente in quel ramo.
```

### Distinguere simulazione e ipotesi

Esempio:

```text
SPICE indica corrente nulla nel ramo LED. Una possibile causa e lo switch aperto,
ma questa resta una ipotesi diagnostica finche non viene verificata o simulata in
uno scenario dedicato.
```

### Proporre controlli pratici

L'agente deve essere utile anche in laboratorio.

Esempi:

- misura la tensione tra VCC e GND;
- controlla il pin RESET;
- misura la tensione sul nodo OUT;
- verifica continuita del carico;
- controlla polarita LED/diodo;
- controlla se lo switch e realmente aperto o chiuso;
- misura corrente nel ramo del carico.

## Contesto diagnostico

Prima di chiamare il modello AI, conviene costruire un file strutturato:

```text
10_diagnostic_context.json
```

Questo file deve raccogliere e sintetizzare gli output della pipeline.

Struttura logica possibile:

```text
[CIRCUIT STATUS]
[USER PROBLEM]
[IMAGE PATH]
[GRAPH SUMMARY]
[NODE MAP]
[VALUES AND ASSUMPTIONS]
[COMPONENT RULES]
[SPICE NETLIST]
[SPICE RUN REPORT]
[NGSPICE STDOUT]
[NGSPICE STDERR]
[ELECTRICAL CHECKS]
[DEVICE PROFILES]
[DATASHEET EXTRACTS]
[WARNINGS AND LIMITS]
[TASK]
```

Gli output tecnici e i prompt verso il modello possono essere in inglese. La
risposta all'utente puo essere in italiano.

## Esempio di risposta

Problema utente:

```text
La lampada non si accende.
```

Evidenze:

```text
Lamp current = 0 A
N002 = 0 V
N004 = 0 V
N002 = connector5.1_pin2
N004 = lamp13.1_t1 + resistor22.1_t2
```

Risposta attesa:

```text
La simulazione conferma che la lampada non conduce corrente. Il ramo lampada
parte da connector5.1_pin2, ma nella simulazione base quel pin non risulta
alimentato. La causa piu supportata dai dati e quindi l'assenza di alimentazione
sul ramo lampada. Per verificarlo, si puo simulare uno scenario in cui vengono
applicati 5 V a connector5.1_pin2.
```

## Scenari controllati

In una fase successiva, l'agente puo proporre scenari simulativi. Gli scenari
servono a verificare ipotesi diagnostiche, non a modificare il circuito base.

Regola fondamentale:

```text
base circuit != scenario circuit
```

Il circuito base resta quello riconosciuto e valorizzato dalla pipeline. Lo
scenario e una modifica simulativa controllata.

L'agente puo decidere cosa provare e perche, ma la pipeline deve decidere come
applicare lo scenario in SPICE.

### Scenari specifici vs primitive generali

Non conviene progettare manualmente tutti gli scenari possibili.

Gli scenari possono diventare migliaia, perche dipendono da:

- circuito;
- batch;
- componenti presenti;
- problema utente;
- valori disponibili;
- warning SPICE;
- eventuali errori topologici;
- comportamento simulato.

Per questo la pipeline non deve contenere scenari rigidi del tipo:

```text
scenario_a01_lamp_off
scenario_a09_led_bridge
scenario_b03_motor_not_running
```

Questa soluzione sarebbe fragile e non scalabile.

La scelta piu generale e definire poche primitive di modifica e simulazione,
poi lasciare all'agente il compito di combinarle in base al caso specifico.

In altre parole:

```text
noi standardizziamo le azioni base
l'agente propone lo scenario
la pipeline valida ed esegue solo azioni consentite
```

Questo rende il sistema piu adatto a Batch A, Batch B, C1, C2 e a circuiti
futuri non ancora visti.

Primitive generiche possibili:

```text
drive_node_voltage
close_switch
open_switch
add_pullup
add_pulldown
change_source_value
move_terminal
disconnect_terminal
connect_nodes
replace_with_equivalent
run_op
run_tran
```

L'agente non deve generare liberamente una netlist SPICE completa. Deve invece
proporre uno scenario strutturato usando queste primitive. La pipeline controlla
che lo scenario sia valido, applicabile e riproducibile.

Esempio concettuale:

```text
Problema: il LED non si accende.
Evidenza: SPICE mostra corrente LED nulla.
Ipotesi: il ramo LED non e alimentato o un terminale e collegato al nodo errato.
Scenario proposto dall'agente: applicare una tensione al nodo di ingresso del
ramo LED e rieseguire .op.
```

### Scenari multipli e ciclo iterativo

L'agente non deve essere pensato come un sistema che propone un solo scenario e
si ferma.

In molti circuiti il problema non dipende da una sola causa. Un fallimento SPICE
puo derivare da piu livelli:

- valori mancanti;
- nodi flottanti;
- componenti saltati;
- modello SPICE assente;
- topologia sospetta;
- componente complesso rappresentato in modo parziale;
- differenza tra graph riconosciuto e circuito visibile nell'immagine.

Per questo l'agente deve poter lavorare in modo iterativo:

```text
diagnosi iniziale
-> scenario candidato
-> netlist scenario
-> esecuzione ngspice
-> lettura stdout/stderr/risultati
-> confronto con il run precedente
-> nuova diagnosi
-> scenario successivo, se necessario
```

Questa logica e importante per casi come `a03`. Un singolo scenario potrebbe non
bastare: prima si puo dover introdurre un riferimento di massa, poi interpretare
la batteria come unica sorgente, poi modellare il rele, poi provare contatto
aperto/chiuso, poi confrontare luce/buio per la LDR.

Quindi l'agente dovrebbe mantenere una lista ordinata di scenari, eseguirli uno
alla volta e aggiornare la diagnosi dopo ogni run. Ogni scenario deve dichiarare:

- quale problema prova a verificare;
- quali assunzioni introduce;
- quali primitive usa;
- quale risultato atteso ha;
- quale risultato SPICE ha prodotto;
- se risolve, peggiora o lascia invariato il problema.

Il ciclo deve fermarsi quando:

- viene trovato uno scenario coerente con il sintomo utente;
- gli scenari ragionevoli sono esauriti;
- manca un dato essenziale che richiede input dell'utente;
- una modifica proposta non e validabile automaticamente.

In questo modo l'agente non e solo uno spiegatore del primo output SPICE, ma un
assistente diagnostico che esplora ipotesi controllate e confronta risultati.

Esempio scenario:

```json
{
  "scenario_id": "drive_lamp_input",
  "actions": [
    {
      "type": "drive_node_voltage",
      "target_terminal": "connector5.1_pin2",
      "value": 5,
      "unit": "V",
      "reason": "Test whether the lamp branch works when the connector pin is driven."
    }
  ]
}
```

La pipeline puo trasformare questo scenario in una netlist separata:

```spice
Vscenario_connector5_1_pin2 N002 0 DC 5
```

Esempio piu avanzato, utile quando si sospetta un errore topologico:

```json
{
  "scenario_id": "repair_led_resistor_bridge",
  "reason": "The LED current is zero and the resistor input is connected to ground. The image suggests this may be a bridge to an input node.",
  "actions": [
    {
      "type": "move_terminal",
      "terminal": "resistor22.1_t1",
      "from_node": "0",
      "to_node": "PWR_LED_INPUT"
    },
    {
      "type": "drive_node_voltage",
      "target_node": "PWR_LED_INPUT",
      "reference_node": "0",
      "value": 9,
      "unit": "V"
    },
    {
      "type": "run_op"
    }
  ]
}
```

Questo esempio non deve essere implementato come scenario fisso per un solo
circuito. Serve a mostrare come l'agente puo proporre una combinazione di
primitive generali.

## Ruolo dell'agente e ruolo della pipeline

La separazione dei ruoli e importante.

L'agente:

- legge il contesto;
- interpreta il problema utente;
- propone spiegazioni;
- propone scenari controllati;
- confronta risultati base e risultati scenario.

La pipeline:

- valida gli scenari;
- traduce azioni generiche in SPICE;
- genera netlist scenario;
- esegue ngspice;
- salva risultati riproducibili.

Flusso completo:

```text
utente descrive problema
-> agente legge output 08 e contesto tecnico
-> agente propone scenario JSON
-> pipeline valida lo scenario
-> pipeline genera netlist scenario
-> ngspice esegue lo scenario
-> agente confronta base vs scenario
-> agente spiega il risultato
```

Questa separazione evita che il modello generi netlist arbitrarie.

## Forma dell'interfaccia

L'agente puo essere implementato in modo progressivo.

### Versione 1: chat CLI

Prima versione semplice da terminale:

```powershell
python scripts\pipeline_2.0\agent\diagnostic_agent.py --batch batchA --circuit a10
```

Oppure con domanda diretta:

```powershell
python scripts\pipeline_2.0\agent\diagnostic_agent.py --batch batchA --circuit a10 --question "Perche il LED non si accende?"
```

Questa versione:

- carica gli output gia prodotti;
- costruisce il contesto diagnostico;
- chiama il modello;
- stampa la risposta;
- salva la conversazione.

### Versione 2: sito web diagnostico

La versione piu completa puo essere una piccola applicazione web.

Struttura possibile:

```text
-------------------------------------------------------------
| Circuiti / stato | Visualizzazione circuito | Chat agente  |
|------------------|--------------------------|--------------|
| a10 READY        | immagine originale       | domanda      |
| b03 PARTIAL      | graph/topologia          | risposta     |
| c13 NOT_READY    | nodi / warning           | follow-up    |
-------------------------------------------------------------
| Report elettrico | Netlist SPICE | Risultati / log ngspice |
-------------------------------------------------------------
```

Il sito non deve essere una landing page. Deve aprirsi direttamente come
strumento operativo.

Viste consigliate:

- lista circuiti;
- stato READY/PARTIAL/NOT_READY;
- immagine originale o grafo ricostruito;
- componenti e nodi principali;
- warning topologici;
- netlist generata;
- risultati SPICE;
- chat diagnostica.

## Moduli software

Possibile struttura:

```text
scripts/pipeline_2.0/agent/
|-- __init__.py
|-- diagnostic_agent.py
|-- chat_agent.py
|-- context_loader.py
|-- context_builder.py
|-- prompt_builder.py
|-- scenario_builder.py
|-- tool_router.py
|-- response_writer.py
`-- templates/
    |-- system_prompt.txt
    `-- diagnostic_prompt.txt
```

### Circuit loader

Carica tutti i file disponibili per un circuito e costruisce un oggetto
`CircuitContext`.

Deve verificare quali file esistono e quali mancano.

### Context builder

Costruisce una sintesi ordinata per il modello AI.

Questo modulo dovrebbe corrispondere allo step:

```text
10_build_diagnostic_context.py
```

### Prompt builder

Trasforma il contesto diagnostico in un prompt controllato.

Regole principali:

- usare solo evidenze fornite;
- dichiarare dati mancanti;
- separare fatti, simulazione e ipotesi;
- rispondere nella lingua richiesta dall'utente.

### Chat memory

Mantiene la conversazione corrente.

Non deve sostituire il contesto tecnico. Deve solo ricordare:

- domande precedenti;
- ipotesi gia discusse;
- eventuali scenari gia simulati;
- preferenze dell'utente.

### Tool router

Modulo opzionale per versioni avanzate.

Puo permettere all'agente di richiamare strumenti interni:

```text
explain_node(node_id)
explain_component(component_id)
show_missing_parameters(circuit_id)
run_ngspice(circuit_id)
build_scenario(circuit_id, scenario_json)
compare_spice_runs(base_run, scenario_run)
```

## Prompt arricchito

Il prompt arricchito non deve essere scritto manualmente ogni volta. Deve essere
generato dalla pipeline.

Schema possibile:

```text
You are a diagnostic assistant for electronic circuits.
Use only the provided evidence.
Do not invent values, connections, component models or simulation results.
If something is missing, say it explicitly.

[CIRCUIT STATUS]
...

[USER PROBLEM]
...

[GRAPH SUMMARY]
...

[NODE MAP]
...

[VALUES AND ASSUMPTIONS]
...

[COMPONENT RULES]
...

[SPICE NETLIST]
...

[SPICE RESULTS]
...

[ELECTRICAL CHECKS]
...

[DEVICE PROFILES / DATASHEET]
...

[TASK]
Answer by distinguishing:
1. confirmed facts;
2. simulated results;
3. missing data;
4. diagnostic hypotheses;
5. suggested practical checks.
```

## API key

Per usare un agente basato su un modello OpenAI serve una API key.

Variabile ambiente:

```text
OPENAI_API_KEY
```

La prima implementazione puo essere uno script Python semplice che:

- legge i file del circuito;
- legge la domanda utente;
- costruisce il contesto;
- chiama il modello;
- salva risposta e chat history.

## Possibile struttura degli output

Una cartella circuito potrebbe contenere:

```text
outputs/pipeline2.0/batchA/a10/
|-- 01_graph.json
|-- 02_normalized_circuit.json
|-- 03_node_map.json
|-- 04_values_bound.json
|-- 06_component_rules.json
|-- 07_netlist.cir
|-- 07_spice_emit_report.json
|-- 08_spice_run.json
|-- 08_ngspice_stdout.txt
|-- 08_ngspice_stderr.txt
|-- 09_spice_summary.json
|-- 10_diagnostic_context.json
|-- 11_agent_response.md
|-- proposed_scenarios.json
`-- chat_history.json
```

Per circuiti con IC o componenti complessi possono comparire anche:

```text
device_profiles.yaml
datasheet_extract.txt
pin_aware_checks.json
```

## Livelli di implementazione

### Livello 1: agente diagnostico solo lettura

Legge i file prodotti dalla pipeline e risponde all'utente.

Non modifica niente e non rilancia SPICE.

Output possibile:

```text
agent_response.md
chat_history.json
```

Questo livello e sufficiente per una prima demo.

### Livello 2: agente che propone scenari

L'agente non esegue ancora nulla, ma produce scenari JSON.

Output possibile:

```text
proposed_scenarios.json
```

### Livello 3: agente con strumenti

L'agente puo chiedere alla pipeline di:

- creare uno scenario;
- rigenerare la netlist;
- eseguire ngspice;
- confrontare base e scenario;
- produrre una risposta finale.

### Livello 4: interfaccia web

Il sito permette di selezionare circuiti, vedere output tecnici e dialogare con
l'agente.

Questa fase va introdotta dopo aver verificato che il contesto diagnostico
funziona.

## Domande che l'agente deve gestire

### Domande topologiche

- Quali componenti sono collegati al nodo N003?
- Questo terminale e flottante?
- Dove va il pin reset?
- Il GND e presente?
- Il carico e collegato?

### Domande SPICE

- La netlist e eseguibile?
- Qual e la tensione sul nodo OUT?
- Passa corrente nel LED?
- La simulazione converge?
- Quali componenti impediscono la simulazione?

### Domande diagnostiche

- Perche il LED non si accende?
- Perche la lampada non si accende?
- Perche il motore non gira?
- Perche lo speaker non produce suono?
- Quale componente controllerei per primo?

### Domande sui limiti

- Quanto sei sicuro?
- Questa conclusione viene da SPICE o dal datasheet?
- Quali dati mancano?
- Cosa devo aggiungere al YAML?
- Questo IC e simulato internamente?

## Valutazione dell'agente

L'agente puo essere valutato confrontando diverse configurazioni:

1. GPT con solo JSON e datasheet;
2. GPT con JSON, datasheet e immagine;
3. agente con JSON, node map, valori, report elettrico, SPICE e datasheet.

Metriche possibili:

- accuratezza diagnostica;
- Top-1 correct;
- Top-3 contains correct;
- numero di allucinazioni;
- uso corretto dei warning;
- capacita di indicare dati mancanti;
- utilita dei controlli pratici;
- costo e latenza.

Questa valutazione si collega agli esperimenti GPT gia presenti nel progetto.

## Roadmap consigliata

### Fase 1: validazione Pipeline 2.0

- validare `08_spice_run.py` su piu circuiti;
- estendere gradualmente Batch A;
- poi passare a Batch B, C1 e C2;
- osservare quali problemi ricorrono.

### Fase 2: contesto diagnostico

- implementare `09_summarize_spice.py`;
- implementare `10_build_diagnostic_context.py`;
- implementare `11_agent_readonly.py`;
- produrre un contesto unico per circuito.

### Fase 3: agente statico

- leggere file gia generati;
- rispondere a domande;
- salvare `agent_response.md`;
- salvare `chat_history.json`.

### Fase 4: scenari controllati

- definire poche azioni scenario generali;
- far produrre all'agente `proposed_scenarios.json`;
- validare gli scenari nella pipeline;
- generare netlist scenario;
- confrontare base vs scenario.

### Fase 5: chat e web

- chat CLI su un circuito;
- storico conversazione;
- eventuale sito web diagnostico;
- pannelli per immagine, report, netlist, log ngspice e chat.

## Limiti da dichiarare

L'agente non garantisce diagnosi corretta in assoluto.

I suoi limiti dipendono da:

- qualita del Graph JSON;
- correttezza della node map;
- valori disponibili;
- modelli SPICE disponibili;
- affidabilita del datasheet/device profile;
- capacita del modello AI;
- completezza del sintomo fornito dall'utente.

Per questo deve sempre dichiarare il livello di evidenza delle sue conclusioni.

## Sintesi

L'agente finale e il modo piu naturale per rendere utilizzabile la Pipeline 2.0.

La pipeline tecnica produce una rappresentazione elettrica controllata. SPICE
verifica numericamente cio che e simulabile. L'agente usa questi risultati per
rispondere all'utente, spiegare limiti e proporre verifiche.

La forma piu difendibile per la tesi e:

```text
una chat diagnostica, eventualmente integrata in un sito, che usa Graph JSON,
node map, valori YAML, report elettrico, risultati SPICE e datasheet per
produrre risposte motivate, tracciabili e consapevoli dei limiti.
```

In breve:

```text
pipeline = produce fatti strutturati
ngspice = verifica numericamente
agente = spiega, dialoga e propone scenari controllati
```
