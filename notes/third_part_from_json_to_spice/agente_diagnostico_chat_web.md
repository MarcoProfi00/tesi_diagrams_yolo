# Agente diagnostico conversazionale per circuiti

## Obiettivo

L'obiettivo dell'agente e trasformare la pipeline tecnica JSON -> nodi elettrici -> SPICE -> report in una interfaccia con cui l'utente possa dialogare.

L'utente non deve leggere manualmente tutti i file prodotti dalla pipeline. Deve poter fare domande naturali sul circuito, sui collegamenti, sui warning, sui risultati SPICE e sui possibili guasti.

L'agente finale puo quindi essere descritto come:

> una chat diagnostica grounded su Graph JSON, node map, valori dichiarati, device profile, datasheet, report elettrico e risultati SPICE.

La parola chiave e grounded: l'agente non deve inventare collegamenti, valori o modelli. Deve distinguere sempre tra:

- dati certi estratti dal Graph JSON;
- valori inseriti manualmente nel file YAML;
- risultati numerici ottenuti da SPICE;
- vincoli ricavati da datasheet o device profile;
- ipotesi diagnostiche non ancora verificate.

## Perche serve un agente

La pipeline produce molti output tecnici:

- `graph.json`;
- `node_map.json`;
- `values.yaml`;
- `device_profiles.yaml`;
- `spice_netlist.cir`;
- `spice_results.json`;
- `electrical_check_report.json`;
- `conversion_report.json`;
- `missing_parameters.json`;
- eventuali immagini o grafi ricostruiti.

Questi file sono utili per una valutazione scientifica, ma non sono comodi per un utente finale.

L'agente serve a fare da ponte tra:

- rappresentazione tecnica del circuito;
- simulazione o analisi parziale;
- diagnosi pratica;
- interazione umana.

In pratica, l'agente diventa lo strato finale della tesi: non sostituisce la pipeline, ma la rende interrogabile.

## Forma dell'interfaccia

L'agente puo essere implementato in due forme progressive.

### Versione 1: chat da terminale

La prima versione puo essere una chat semplice lanciata da comando:

```powershell
python scripts\spice_agent\chat_agent.py --circuit a10
```

L'utente seleziona un circuito e poi scrive domande come:

- "Perche il LED non si accende?"
- "Il circuito ha massa e alimentazione?"
- "Quali terminali sono scollegati?"
- "La netlist SPICE e simulabile?"
- "Il transistor e polarizzato correttamente?"
- "Cosa devo controllare fisicamente sul circuito?"
- "Quali conclusioni derivano da SPICE e quali sono solo ipotesi?"

Questa versione e semplice da implementare e sufficiente per dimostrare il concetto di agente conversazionale.

### Versione 2: sito web diagnostico

La versione piu completa puo essere una piccola applicazione web.

Una struttura efficace potrebbe essere:

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

Il sito non deve essere una landing page. Deve aprirsi direttamente come strumento operativo.

Le viste principali possono essere:

- lista circuiti;
- stato del circuito: `READY`, `PARTIAL`, `NOT_READY`;
- immagine originale o grafo ricostruito;
- componenti e nodi principali;
- warning topologici;
- netlist generata;
- risultati SPICE, se disponibili;
- chat diagnostica.

## Esperienza utente ideale

Il flusso per l'utente dovrebbe essere questo:

1. L'utente apre la chat o il sito.
2. Seleziona un circuito.
3. Il sistema carica tutti gli output disponibili della pipeline.
4. Il sistema mostra uno stato sintetico:
   - circuito simulabile o no;
   - valori mancanti;
   - componenti non modellati;
   - warning principali;
   - risultati SPICE disponibili.
5. L'utente scrive un sintomo o una domanda.
6. L'agente risponde indicando:
   - cosa risulta dal JSON;
   - cosa risulta dal report elettrico;
   - cosa risulta da SPICE;
   - cosa dice il datasheet;
   - cosa resta incerto.
7. L'utente puo fare domande successive.
8. L'agente mantiene il contesto del circuito e del dialogo.

## Esempio di dialogo

Utente:

```text
Il LED non si accende. Quale potrebbe essere il problema?
```

Agente:

```text
Dal Graph JSON risulta che il LED led12.1 ha anodo collegato al nodo N003 e catodo collegato a GND.
Il file values.yaml assegna R1 = 330 ohm e V1 = 5 V.
La simulazione .op indica corrente molto bassa nel ramo del LED.

Le cause piu probabili sono:
1. lo switch switch25.1 risulta aperto, quindi il ramo non viene alimentato;
2. se lo switch e fisicamente chiuso, il JSON potrebbe non rappresentare correttamente lo stato reale;
3. se il valore del LED e assunto manualmente, va verificata la polarita reale.

Conclusione: la causa principale supportata dai dati e lo switch aperto. La polarita del LED e una verifica secondaria.
```

Questo tipo di risposta e utile perche separa dati certi, simulazione e ipotesi.

## Architettura generale

L'agente non deve parlare direttamente con il solo `graph.json`.

Deve ricevere un pacchetto diagnostico costruito dalla pipeline:

```text
graph.json
  |
node_map.json
  |
values.yaml
  |
spice_netlist.cir
  |
spice_results.json
  |
electrical_check_report.json
  |
device_profiles.yaml / datasheet_extract.txt
  |
diagnostic_context.json / prompt_arricchito.txt
  |
chat agent
```

Il modulo piu importante prima della chat e quindi il costruttore del contesto diagnostico.

## Moduli dell'agente

### 1. Circuit loader

Carica tutti i file disponibili per un circuito.

Input:

- id circuito;
- path della cartella circuito.

Output:

- oggetto `CircuitContext`.

Esempio logico:

```text
load_circuit_context("a10")
```

Il loader deve verificare quali file esistono e quali mancano.

### 2. Context builder

Costruisce una sintesi ordinata per il modello AI.

Deve includere sezioni come:

```text
[CIRCUIT STATUS]
[GRAPH SUMMARY]
[NODE MAP]
[VALUES AND ASSUMPTIONS]
[SPICE NETLIST]
[SPICE RESULTS]
[ELECTRICAL CHECKS]
[DEVICE PROFILES]
[DATASHEET EXTRACTS]
[WARNINGS AND LIMITS]
[USER QUESTION]
```

Questa struttura rende il prompt piu controllabile e riduce il rischio di risposte generiche.

### 3. Chat memory

Mantiene la conversazione corrente.

Non deve sostituire il contesto tecnico. Deve solo ricordare:

- domande precedenti;
- ipotesi gia discusse;
- eventuali preferenze dell'utente;
- risultati gia spiegati.

Il contesto tecnico del circuito resta sempre la fonte principale.

### 4. Tool router

In una versione piu avanzata, l'agente puo richiamare strumenti interni.

Esempi:

```text
build_node_map(circuit_id)
emit_spice(circuit_id)
run_ngspice(circuit_id)
build_report(circuit_id)
show_missing_parameters(circuit_id)
explain_node(node_id)
explain_component(component_id)
```

Questa parte non e obbligatoria nel primo prototipo. Puo diventare una seconda fase.

### 5. Answer generator

Invia il contesto al modello GPT e produce la risposta finale.

La risposta deve seguire alcune regole:

- non inventare collegamenti assenti;
- non inventare valori assenti;
- non dichiarare simulabile un circuito `PARTIAL` o `NOT_READY`;
- distinguere fatti, simulazione, datasheet e ipotesi;
- proporre controlli pratici misurabili;
- indicare cosa manca per una diagnosi piu sicura.

## Stati del circuito

L'agente deve sempre conoscere lo stato del circuito.

### READY

Il circuito ha valori e modelli sufficienti.

L'agente puo usare:

- Graph JSON;
- node map;
- netlist SPICE;
- risultati SPICE;
- report elettrico.

In questo caso puo rispondere anche con numeri simulati.

### PARTIAL

Il circuito e parzialmente analizzabile.

L'agente deve essere prudente.

Puo usare:

- nodi ricostruiti;
- warning;
- valori disponibili;
- netlist parziale;
- controlli statici;
- datasheet/device profile.

Non deve fingere che SPICE abbia verificato tutto.

### NOT_READY

Il circuito non ha dati sufficienti per netlist utile o simulazione.

L'agente deve spiegare il motivo:

- JSON incompleto;
- terminali scollegati;
- valori mancanti;
- modelli mancanti;
- IC troppo complesso;
- pin mapping non affidabile.

Anche in questo caso puo fornire una diagnosi topologica preliminare.

## Regole di risposta dell'agente

L'agente deve rispettare queste regole metodologiche.

### 1. Non inventare collegamenti

Se un collegamento non e nel JSON, l'agente puo dire:

```text
Il collegamento non risulta nel Graph JSON. Potrebbe essere un errore di riconoscimento o una connessione assente nello schema.
```

Non deve dire:

```text
Il collegamento c'e sicuramente.
```

### 2. Non inventare valori

Se un valore non e in `values.yaml`, va segnalato come mancante.

Esempio:

```text
Il valore di R3 non e disponibile, quindi non posso stimare numericamente la corrente in quel ramo.
```

### 3. Non simulare mentalmente IC complessi

Per microcontrollori, ADC, driver audio, driver motore o IC complessi senza modello SPICE, l'agente deve usare controlli pin-aware.

Esempio:

```text
Non sto simulando internamente il microcontrollore. Posso pero verificare alimentazione, massa, reset, clock e collegamenti I/O.
```

### 4. Separare evidenza e ipotesi

Ogni diagnosi dovrebbe distinguere:

- evidenza dal JSON;
- evidenza da SPICE;
- evidenza da datasheet;
- ipotesi plausibile;
- controllo pratico consigliato.

### 5. Proporre controlli fisici

L'agente deve essere utile anche in laboratorio.

Esempi:

- misura la tensione tra VCC e GND;
- controlla il pin RESET;
- misura la tensione sul nodo OUT;
- verifica continuita del carico;
- controlla polarita LED/diodo;
- controlla se lo switch e realmente aperto o chiuso;
- misura corrente nel ramo del carico.

## Prompt arricchito

Il prompt arricchito non deve essere scritto ogni volta manualmente. Deve essere generato dalla pipeline.

Schema possibile:

```text
Sei un assistente diagnostico per circuiti elettronici.
Devi rispondere usando solo le evidenze fornite.
Non inventare valori, collegamenti o modelli.
Se qualcosa manca, dichiaralo.

[CIRCUIT STATUS]
...

[GRAPH SUMMARY]
...

[NODE MAP]
...

[VALUES AND ASSUMPTIONS]
...

[SPICE NETLIST]
...

[SPICE RESULTS]
...

[ELECTRICAL CHECKS]
...

[DEVICE PROFILES / DATASHEET]
...

[USER QUESTION]
...

[TASK]
Rispondi distinguendo:
1. fatti certi;
2. risultati simulati;
3. dati mancanti;
4. ipotesi diagnostiche;
5. controlli pratici consigliati.
```

## Possibile struttura dei file

Una cartella circuito potrebbe diventare:

```text
outputs/spice_agent/a10/
|-- graph.json
|-- values.yaml
|-- node_map.json
|-- conversion_report.json
|-- missing_parameters.json
|-- spice_netlist.cir
|-- spice_results.json
|-- electrical_check_report.json
|-- diagnostic_context.json
|-- prompt_arricchito.txt
|-- chat_history.json
`-- diagnosi_finale.txt
```

Per i circuiti con IC:

```text
outputs/spice_agent/c13/
|-- graph.json
|-- values.yaml
|-- device_profiles.yaml
|-- datasheet_extract.txt
|-- node_map.json
|-- electrical_check_report.json
|-- diagnostic_context.json
|-- chat_history.json
`-- diagnosi_finale.txt
```

## Possibile struttura software

```text
scripts/spice_agent/
|-- __init__.py
|-- chat_agent.py
|-- web_app.py
|-- context_loader.py
|-- context_builder.py
|-- prompt_builder.py
|-- tool_router.py
|-- response_writer.py
`-- templates/
    |-- system_prompt.txt
    `-- diagnostic_prompt.txt
```

La parte web puo essere introdotta dopo la chat CLI.

## Implementazione della chat CLI

La chat CLI puo funzionare cosi:

1. legge il circuito selezionato;
2. costruisce il contesto diagnostico;
3. mostra un riepilogo iniziale;
4. aspetta una domanda dell'utente;
5. invia contesto + domanda al modello;
6. stampa la risposta;
7. salva la conversazione;
8. permette altre domande.

Esempio:

```text
Circuito: a10
Stato: PARTIAL
Componenti: Battery, Switch, Connector, Lamp, Resistor, LED, GND
Warning: nessun terminale scollegato
SPICE: non eseguito, manca values.yaml completo

Domanda utente > Perche il LED non si accende?
```

## Implementazione del sito

Il sito puo essere costruito con un backend Python e una interfaccia semplice.

### Backend

Responsabilita:

- caricare i circuiti;
- leggere output della pipeline;
- costruire contesto diagnostico;
- chiamare il modello GPT;
- salvare conversazioni;
- opzionalmente lanciare ngspice.

### Frontend

Responsabilita:

- selezione circuito;
- visualizzazione stato;
- vista immagine/grafo;
- pannello report;
- pannello netlist;
- chat.

### Viste consigliate

1. **Circuit Explorer**
   - lista circuiti;
   - stato READY/PARTIAL/NOT_READY;
   - numero warning;
   - disponibilita SPICE.

2. **Circuit View**
   - immagine originale;
   - grafo topologico;
   - nodi principali;
   - componenti.

3. **Electrical Report**
   - missing values;
   - nodi flottanti;
   - componenti non simulabili;
   - log ngspice;
   - risultati principali.

4. **Diagnostic Chat**
   - domanda utente;
   - risposta agente;
   - storico conversazione;
   - eventuali citazioni a file o nodi.

## Livello di autonomia dell'agente

Per la tesi conviene evitare di presentare l'agente come completamente autonomo.

E meglio definirlo come:

> agente conversazionale assistito da strumenti, che interroga una rappresentazione elettrica strutturata e produce diagnosi motivate.

Nella prima versione l'agente puo solo leggere file gia generati.

Nella seconda versione puo lanciare tool interni:

- rigenerare node map;
- rigenerare report;
- lanciare SPICE;
- aggiornare il contesto.

Nella terza versione, futura, potrebbe suggerire modifiche a `values.yaml` o richiedere valori mancanti all'utente.

## Domande che l'agente deve saper gestire

### Domande topologiche

- "Quali componenti sono collegati al nodo N003?"
- "Questo terminale e flottante?"
- "Dove va il pin reset?"
- "Il GND e presente?"
- "Il carico e collegato?"

### Domande SPICE

- "La netlist e eseguibile?"
- "Qual e la tensione sul nodo OUT?"
- "Passa corrente nel LED?"
- "La simulazione converge?"
- "Quali componenti impediscono la simulazione?"

### Domande diagnostiche

- "Perche il LED non si accende?"
- "Perche il motore non gira?"
- "Perche lo speaker non produce suono?"
- "Perche la tensione di uscita e errata?"
- "Quale componente controllerei per primo?"

### Domande sui limiti

- "Quanto sei sicuro?"
- "Questa conclusione viene da SPICE o dal datasheet?"
- "Quali dati mancano?"
- "Cosa devo aggiungere al YAML?"
- "Questo IC e simulato internamente?"

## Valutazione dell'agente

L'agente puo essere valutato confrontando tre configurazioni:

1. GPT con solo JSON + datasheet;
2. GPT con JSON + datasheet + immagine;
3. agente con JSON + node map + report elettrico + SPICE + datasheet.

Metriche possibili:

- accuratezza diagnostica;
- Top-1 correct;
- Top-3 contains correct;
- numero di allucinazioni;
- uso corretto dei warning;
- capacita di indicare dati mancanti;
- utilita dei controlli pratici;
- costo e latenza.

Questa valutazione si collega bene agli esperimenti GPT gia presenti nel progetto.

## MVP consigliato

La prima versione realistica dovrebbe includere:

1. generazione di `node_map.json`;
2. generazione di `electrical_check_report.json`;
3. generazione di `diagnostic_context.json`;
4. chat CLI su un circuito;
5. salvataggio di `chat_history.json`;
6. test su 2-3 circuiti Batch A;
7. una demo su un circuito con IC in modalita pin-aware.

Il sito web puo essere una seconda fase, dopo aver verificato che il contesto diagnostico funziona.

## Roadmap

### Fase 1: agente statico

- legge file gia generati;
- risponde a domande;
- non lancia SPICE;
- non modifica YAML.

### Fase 2: agente con tool

- puo rigenerare report;
- puo lanciare ngspice se disponibile;
- puo spiegare nodi e componenti;
- puo indicare valori mancanti.

### Fase 3: interfaccia web

- visualizzazione circuito;
- pannello report;
- pannello netlist;
- chat;
- storico sessione.

### Fase 4: agente interattivo avanzato

- chiede all'utente valori mancanti;
- aggiorna `values.yaml`;
- rilancia SPICE;
- confronta simulazioni;
- produce una diagnosi finale revisionata.

## Limiti da dichiarare

L'agente non garantisce diagnosi corretta in assoluto.

I suoi limiti dipendono da:

- qualita del Graph JSON;
- correttezza della node map;
- valori disponibili;
- modelli SPICE disponibili;
- affidabilita del datasheet/device profile;
- capacita del modello GPT;
- completezza del sintomo fornito dall'utente.

Per questo deve sempre dichiarare il livello di evidenza delle sue conclusioni.

## Sintesi

L'agente finale e il modo piu naturale per rendere utilizzabile la pipeline.

La pipeline tecnica produce una rappresentazione elettrica controllata. La chat permette all'utente di interrogarla.

La forma piu difendibile per la tesi e:

> una chat diagnostica, eventualmente integrata in un sito, che usa Graph JSON, node map, valori YAML, report elettrico, risultati SPICE e datasheet per produrre risposte motivate, tracciabili e consapevoli dei limiti.

Questa scelta rende il progetto piu vicino a un sistema reale: non solo riconoscimento dello schema, ma assistenza interattiva al troubleshooting.
