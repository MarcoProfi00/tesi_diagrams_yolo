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
-> 09_web_chat
-> 10_build_diagnostic_context
-> 11_agent_readonly
-> 12_controlled_scenarios
```

Il punto minimo per attivare l'agente e dopo `08_spice_run.py`, perche prima di
quello esiste solo una netlist generata, mentre dopo `08` esiste anche il
risultato reale di ngspice.

La decisione corrente e usare lo step `09` come punto di ingresso
dell'interfaccia utente:

```text
09_web_chat.py = avvia una chat web locale collegata agli output gia prodotti
dagli step 01-08.
```

Lo step `09` non deve diventare un riassunto SPICE intermedio. Non deve filtrare
troppo i dati e non deve sostituire `10` o `11`. Il suo ruolo e orchestrare
l'interazione:

```text
utente sceglie batch/circuito
-> utente scrive il problema
-> 09 chiama 10 per costruire/aggiornare il manifest
-> 09 chiama 11 per ottenere la risposta diagnostica
-> 09 mostra la risposta in chat
-> se l'utente sceglie uno scenario, 09 chiama 12
```

In questo modo la pipeline tecnica resta separata dall'interfaccia. `09` e il
ponte operativo tra utente, agente e strumenti controllati.

Lo step `10` non deve essere trattato come una sintesi interpretativa che
sostituisce i file originali. La decisione corrente e ancora piu semplice:
`10_diagnostic_context.json` e un manifest leggero.

```text
10_diagnostic_context.json = indice dei file 01-08 + mini-summary tecnico + regole agente
```

Il manifest non duplica Graph JSON, node map, netlist, stdout o stderr. Indica
solo dove si trovano i file reali e quale ruolo hanno. Lo step
`11_agent_readonly.py` deve leggere il manifest, caricare i file necessari e
costruire il prompt usando quegli output originali come fonte di verita.

Se una conclusione dipende da un dettaglio specifico, l'agente deve riferirsi al
file originale: node map, component rules, netlist, stdout, stderr o report
SPICE.

Lo step `08` produce fatti grezzi come:

```text
08_spice_run.json
08_ngspice_stdout.txt
08_ngspice_stderr.txt
```

Questi file, insieme agli output precedenti, permettono all'agente di
confrontare il circuito riconosciuto con il comportamento simulato.

## Input dell'agente

Per ogni circuito, l'agente non deve ricevere file sparsi in modo confuso. Deve
partire da un solo ingresso principale:

```text
10_diagnostic_context.json + problema utente
```

Il file `10_diagnostic_context.json` non contiene tutta la diagnosi, ma indica
dove si trovano gli output reali della pipeline. L'agente deve usarlo come
manifest, poi aprire i file originali necessari.

Input principali della prima versione:

```text
problema utente
10_diagnostic_context.json
01_graph.json
02_normalized_circuit.json
03_node_map.json
04_values_bound.json
06_component_rules.json
07_netlist.cir
07_spice_emit_report.json
08_spice_run.json
08_ngspice_stdout.txt
08_ngspice_stderr.txt
08_tran.csv, se disponibile
08_tran_plot.png, se disponibile
```

In modalita normale l'immagine del circuito non e un input predefinito del
modello. Nella versione attuale viene allegata solo nel fallback
`image-assisted`, cioe quando `09_web_chat.py` rileva insieme:

- fallimento ngspice;
- indizi forti di incoerenza topologica o graph sospetto;
- utilita reale dell'immagine per proporre scenari piu affidabili.

Il file piu importante per la struttura del circuito e `01_graph.json`, cioe il
Graph JSON originale prodotto dalla Pipeline 1.0 e portato nella Pipeline 2.0.
Questo file rappresenta cio che la prima pipeline ha riconosciuto: componenti,
terminali e connessioni topologiche.

Il secondo file fondamentale e `03_node_map.json`, perche traduce i terminali
del graph in nodi elettrici utilizzabili da SPICE.

`04_values_bound.json` serve invece a distinguere tra:

- valori letti o inseriti manualmente;
- stati dei componenti, per esempio switch aperto o chiuso;
- modelli assegnati, per esempio BJT o LED;
- valori mancanti.

`06_component_rules.json` e `07_spice_emit_report.json` aiutano l'agente a non
confondersi: spiegano quali componenti erano supportati, quali sono stati
emessi in netlist e quali sono stati saltati.

`07_netlist.cir` e cio che e stato realmente mandato a ngspice.

`08_spice_run.json`, `08_ngspice_stdout.txt` e `08_ngspice_stderr.txt`
rappresentano il risultato vero della simulazione.

Non tutti gli input sono sempre disponibili. La pipeline deve comunque produrre
il massimo livello possibile di analisi per ogni circuito.

## Prima versione dell'agente

La prima versione deve essere volutamente semplice e solo lettura.

Obiettivo:

```text
spiegare il risultato della pipeline e di ngspice rispetto al problema scritto
dall'utente, senza modificare il circuito e senza eseguire scenari.
```

Flusso operativo:

```text
1. l'utente sceglie batch e circuito;
2. l'utente scrive il problema;
3. lo script 11 legge 10_diagnostic_context.json;
4. lo script 11 carica gli artefatti indicati nel manifest;
5. l'agente analizza graph, node map, valori, netlist e risultato ngspice;
6. l'agente produce una diagnosi testuale;
7. l'agente salva la risposta in un file di output.
```

Nella prima versione l'agente deve fare:

- dire se ngspice e stato eseguito correttamente;
- spiegare stdout e stderr in modo comprensibile;
- collegare i risultati SPICE al problema utente;
- indicare quali componenti sono entrati davvero nella netlist;
- indicare quali componenti sono stati saltati e perche;
- distinguere tra dato certo, risultato simulato e ipotesi;
- proporre possibili scenari futuri, ma senza eseguirli.

Nella prima versione l'agente non deve fare:

- modificare la netlist;
- cambiare valori;
- aggiungere collegamenti;
- correggere automaticamente il Graph JSON;
- usare l'immagine originale di default;
- eseguire ngspice;
- applicare scenari.

La risposta dell'agente dovrebbe avere sempre una struttura stabile:

```text
1. Stato della simulazione
2. Evidenze principali
3. Diagnosi rispetto al problema utente
4. Limiti della diagnosi
5. Scenari diagnostici proposti
```

Gli scenari della prima versione sono solo proposte. Lo step `11` non deve
creare cartelle scenario, non deve copiare file, non deve modificare netlist e
non deve rieseguire ngspice. Deve solo descrivere al massimo tre scenari
candidati, ordinati dal piu semplice al piu utile.

Questa struttura aiuta il modello a non perdersi e rende piu semplice valutare
le risposte nella tesi.

### Chat naturale e scelta degli scenari

La forma finale desiderata non deve obbligare l'utente a cliccare bottoni o a
conoscere gli script interni. L'interazione puo restare una chat naturale.

Esempio:

```text
Utente:
La lampada non si accende, quale potrebbe essere il problema?

Agente:
La simulazione mostra che la batteria e presente, ma il ramo lampada non e
alimentato. Propongo tre scenari:

Scenario 1 - Chiudere lo switch.
Scenario 2 - Alimentare il ramo lampada.
Scenario 3 - Alimentare il ramo LED.

Utente:
Esegui lo scenario 1.
```

A questo punto l'agente non deve modificare file direttamente. Il sistema deve:

```text
1. riconoscere che l'utente ha scelto scenario_1;
2. recuperare il JSON tecnico dello scenario_1 generato nella risposta
   precedente;
3. passarlo allo step 12;
4. creare una cartella scenario separata;
5. rieseguire gli step necessari;
6. confrontare base run e scenario run;
7. far spiegare all'agente il nuovo risultato.
```

Quindi l'interfaccia puo essere completamente conversazionale:

```text
utente parla in linguaggio naturale
-> agente risponde in linguaggio naturale
-> pipeline esegue solo azioni strutturate e validate
```

Per la prima implementazione non serve un interprete complesso. Basta accettare
frasi semplici:

```text
esegui scenario 1
prova lo scenario 2
facciamo il terzo
esegui il primo
esegui questo scenario
esegui lo scenario appena proposto
```

Queste frasi possono essere tradotte con regole semplici:

```text
"scenario 1" oppure "primo"  -> scenario_1
"scenario 2" oppure "secondo" -> scenario_2
"scenario 3" oppure "terzo"   -> scenario_3
"questo scenario" oppure "scenario appena proposto" -> ultimo scenario proposto
```

Solo in una fase successiva si puo usare il modello AI anche come
`scenario_selector`, cioe per capire richieste meno esplicite come:

```text
proviamo quello dello switch
esegui l'ipotesi sul ramo LED
rifai la simulazione alimentando il pin del connettore
```

Anche in quel caso, la scelta deve sempre essere trasformata in un comando
strutturato e validato prima di arrivare a `12_controlled_scenarios.py`.

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

Nella web chat locale attuale esiste anche un fallback automatico lato sistema:
se ngspice fallisce e il contesto mostra piu segnali forti di problema
topologico, `09_web_chat.py` puo allegare automaticamente l'immagine locale al
modello. Questo non cambia la regola concettuale: l'immagine non e input
predefinito dell'agente, ma supporto aggiuntivo solo nei casi sospetti.

Esempi di condizioni in cui l'agente puo richiedere l'immagine:

- terminali importanti scollegati;
- nodi singleton su sorgenti, carichi o switch;
- assenza di nodo di riferimento;
- SPICE fallito in modo non utile per matrice singolare o nodi flottanti;
- warning numerici forti insieme a graph/node map incoerenti o incompleti;
- componenti importanti saltati per topologia o valori mancanti;
- differenza sospetta tra graph, netlist e risultato SPICE;
- componenti complessi rappresentati in modo parziale, come rele o
  trasformatore.

Se ngspice fallisce con forti segnali di topologia incoerente, l'agente deve
prima leggere graph, node map, netlist e stderr. Solo dopo aver rilevato
evidenze come sorgente spezzata, nodi singleton, ramo non chiuso o componente
complesso modellato in modo parziale, puo richiedere l'immagine per proporre
scenari correttivi piu affidabili.

Se invece ngspice produce warning numerici ma graph e node map appaiono
coerenti, l'agente non deve chiedere subito l'immagine: deve prima proporre
scenari elettrici controllati, per esempio chiusura di uno switch riconosciuto
oppure pilotaggio di un nodo di ingresso naturale.

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

## Manifest diagnostico

Prima di chiamare il modello AI, conviene costruire un manifest strutturato:

```text
10_diagnostic_context.json
```

Questo file non deve contenere tutti gli output duplicati. Deve essere un indice
leggero dei file prodotti dalla pipeline.

Struttura logica corrente:

```text
[SOURCE FORMAT]
[BATCH NAME]
[CIRCUIT ID]
[USER PROBLEM]
[PIPELINE2 OUTPUT DIR]
[MINI SUMMARY]
[ARTIFACT PATHS]
[IMAGE ACCESS POLICY]
[AGENT MODE]
[AGENT RULES]
```

Il mini-summary serve solo a orientare lo step 11:

```text
spice_status
spice_exit_code
emitted_elements
skipped_elements
emit_warnings_count
node_count
ground_groups_count
singleton_nodes_count
has_tran_csv
has_tran_plot
```

Gli artefatti puntano ai file reali:

```text
01_graph.json
02_normalized_circuit.json
03_node_map.json
04_values_bound.json
06_component_rules.json
07_netlist.cir
07_spice_emit_report.json
08_spice_run.json
08_ngspice_stdout.txt
08_ngspice_stderr.txt
08_tran.csv, se disponibile
08_tran_plot.png, se disponibile
```

Lo step `11_agent_readonly.py` deve quindi:

```text
1. leggere 10_diagnostic_context.json;
2. scegliere quali artefatti caricare;
3. leggere i file originali;
4. costruire il prompt;
5. chiamare il modello;
6. salvare la risposta.
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

Uno scenario non e un consiglio generico. E una ipotesi diagnostica controllata
che puo essere trasformata in una nuova simulazione SPICE.

Schema concettuale:

```text
problema utente
-> diagnosi sulla run base
-> scenario candidato proposto dall'agente
-> scelta esplicita dell'utente
-> copia degli output base in una cartella scenario
-> modifica controllata solo sulle copie
-> rigenerazione degli step necessari
-> nuova esecuzione ngspice
-> confronto base vs scenario
-> diagnosi aggiornata
```

Regola fondamentale:

```text
base circuit != scenario circuit
```

Il circuito base resta quello riconosciuto e valorizzato dalla pipeline. Lo
scenario e una modifica simulativa controllata.

Gli output originali non devono mai essere sovrascritti.

Per esempio:

```text
outputs/pipeline2.0/<batch>/<circuit>/
|-- 01_graph.json
|-- 03_node_map.json
|-- 04_values_bound.json
|-- 07_netlist.cir
`-- 08_spice_run.json

outputs/pipeline2.0/<batch>/<circuit>/scenarios/<scenario_id>/
|-- scenario.json
|-- scenario_status.json
|-- scenario_copy_manifest.json
|-- 12_controlled_scenarios.json
|-- scenario_comparison.json
|-- base_snapshot/
`-- run/
```

La cartella scenario deve nascere solo dopo che l'utente ha scelto
esplicitamente uno degli scenari proposti, per esempio scenario 1, 2 o 3. La
fase read-only dell'agente non deve creare nulla.

### Stato implementativo attuale degli scenari

La prima versione degli scenari controllati e stata implementata in modo
minimale ma generale.

Flusso attuale:

```text
utente scrive un sintomo nella web chat
-> 09_web_chat.py chiama 10 e 11
-> l'agente read-only propone scenari diagnostici
-> utente scrive "esegui scenario 1"
-> 09 riconosce la scelta
-> 09 estrae il JSON tecnico dello scenario dalla risposta agente
-> 09 crea la cartella scenario
-> 09 copia la base run in base_snapshot/ e run/
-> 09 chiama 12_controlled_scenarios.py
-> 12 applica le azioni supportate alla netlist in run/
```

Struttura attuale:

```text
outputs/pipeline2.0/<batch>/<circuit>/scenarios/<scenario_id>/
|-- scenario.json
|-- scenario_status.json
|-- scenario_copy_manifest.json
|-- 12_controlled_scenarios.json
|-- scenario_comparison.json, se SPICE scenario e stato eseguito
|-- base_snapshot/
`-- run/
```

`base_snapshot/` conserva una copia degli output base originali. `run/` e la
copia modificabile usata per lo scenario.

La base run originale non viene modificata.

Primitive attualmente supportate da `12_controlled_scenarios.py`:

```text
drive_node_voltage
change_source_value
change_component_value
close_switch
```

`drive_node_voltage` aggiunge una sorgente di test su un nodo gia presente
nella node map della run scenario.

Esempio:

```json
{
  "type": "drive_node_voltage",
  "target": "N002",
  "value": "5V"
}
```

Questa azione viene tradotta nella netlist scenario in:

```spice
VSCENARIO_N002 N002 0 DC 5
```

`change_source_value` modifica il valore di una sorgente SPICE gia presente
nella netlist copiata dello scenario.

Esempio:

```json
{
  "type": "change_source_value",
  "target": "VVCC",
  "value": "10V"
}
```

`change_component_value` modifica il valore di un componente semplice gia
emesso nella netlist scenario. Nella versione attuale e pensato per componenti
lineari a due terminali come resistori, condensatori, induttanze o componenti
equivalenti gia tradotti come `R`, `C` o `L`.

Esempio:

```json
{
  "type": "change_component_value",
  "target": "Rresistor22_4",
  "value": "33k"
}
```

Questa primitiva e importante per mantenere gli scenari naturali: se l'ipotesi
riguarda un valore gia presente, per esempio una resistenza di bias, una
costante RC o una resistenza equivalente, e preferibile modificare quel valore
invece di forzare subito un nodo interno con `drive_node_voltage`.

`close_switch` chiude uno switch gia riconosciuto dalla pipeline inserendo una
piccola resistenza tra i due nodi dello switch nella netlist scenario. Non
modifica il Graph JSON originale e, nella versione attuale, non rigenera la
node map: e una modifica controllata della netlist copiata in `run/`.

Esempio:

```json
{
  "type": "close_switch",
  "target": "switch25.1"
}
```

Il confronto automatico supporta grandezze SPICE numeriche come `v(N001)` e
`i(vbattery2_1#branch)`. Se nel campo `compare` compare `stderr`, lo step `12`
lo interpreta come conteggio dei warning ngspice, utile per capire se uno
scenario riduce problemi numerici come `singular matrix`.

Lo step `12_controlled_scenarios.py` puo essere eseguito anche da terminale con
`--run-spice`. In quel caso:

```text
1. applica lo scenario alla netlist in run/;
2. esegue ngspice sulla netlist scenario;
3. salva 08_spice_run.json, stdout e stderr dentro run/;
4. crea scenario_comparison.json confrontando base run e scenario run.
```

Esempio di confronto scenario:

```text
v(N002):       0 -> 5 V
v(N004):       0 -> 0.2380952 V
i(Rlamp13_1):  0 -> 0.0047619 A
```

Questo conferma l'ipotesi proposta dall'agente: alimentando `N002`, il ramo
della lampada riceve corrente.

L'agente puo decidere cosa provare e perche, ma la pipeline deve decidere come
applicare lo scenario in SPICE.

Ogni scenario proposto dovrebbe avere due livelli:

```text
1. livello user-friendly, leggibile dall'utente;
2. livello tecnico, utile alla futura pipeline per costruire la run scenario.
```

Il livello user-friendly deve spiegare:

- titolo naturale dello scenario;
- perche lo scenario viene proposto;
- cosa si proverebbe a modificare;
- cosa ci si aspetta da SPICE;
- come si verifica il risultato;
- quale sarebbe il prossimo passo se lo scenario non conferma l'ipotesi.

Il livello tecnico deve essere breve e controllato. Non deve sostituire la
spiegazione per l'utente, ma deve dare alla pipeline informazioni traducibili in
azioni future.

Esempio:

```json
{
  "scenario_id": "scenario_1",
  "title": "Alimentare il ramo della lampada",
  "hypothesis": "Il ramo della lampada non conduce perche il nodo di ingresso non e alimentato.",
  "actions": [
    {
      "type": "drive_node_voltage",
      "target": "N002",
      "value": "5V"
    }
  ],
  "rerun_from": "04",
  "analysis": "op",
  "compare": ["v(N002)", "v(N004)", "i(Rlamp13_1)"]
}
```

Questa forma e piu adatta alla chat: l'utente capisce cosa sta scegliendo, ma
la pipeline mantiene una rappresentazione abbastanza strutturata per poter
validare ed eseguire lo scenario in una fase successiva.

Regola di priorita:

```text
se ngspice riesce e graph/node_map sono internamente coerenti,
i primi scenari devono essere test elettrici, di valore, di analisi o di stato;
non devono essere subito correzioni topologiche.
```

Quindi azioni come:

```text
connect_nodes
disconnect_terminal
move_terminal
```

devono comparire tra i primi scenari solo quando ci sono prove strutturate di
errore topologico, per esempio:

- ngspice fallisce per topologia non valida;
- ci sono nodi singleton o flottanti importanti;
- mancano componenti critici;
- il Graph JSON contiene warning significativi;
- la pipeline produce una netlist non diagnostica;
- l'immagine viene richiesta perche gli output strutturati fanno sospettare un
  errore di riconoscimento.

Se invece il circuito base e simulabile e coerente, queste azioni possono essere
citate come possibile passo successivo, ma non devono sostituire scenari piu
naturali come alimentare un nodo di ingresso, cambiare il valore di una sorgente,
chiudere uno switch gia riconosciuto o rieseguire una analisi diversa.

Regola di naturalezza:

```text
prima si agisce su ingressi, connettori, sorgenti, label di alimentazione e
stati di componenti riconosciuti; solo dopo si forzano nodi interni del carico.
```

Per esempio, se una lampada e alimentata attraverso:

```text
connector pin -> resistor -> lamp -> ground
```

lo scenario piu naturale e pilotare il pin o il nodo di ingresso del ramo, non
applicare subito una sorgente direttamente sul terminale della lampada. Pilotare
direttamente il terminale del carico puo avere senso come test di isolamento del
modello, ma non dovrebbe essere uno dei primi scenari se esiste un ingresso a
monte piu naturale.

Regola di autosufficienza:

```text
ogni scenario proposto nei primi tre deve poter essere eseguito da solo.
```

Quindi uno scenario non dovrebbe dire soltanto "dopo lo scenario 1 esegui
`.tran`". Se la transitoria serve, lo scenario deve includere anche le azioni
necessarie per rendere il ramo elettricamente significativo, per esempio:

```json
{
  "analysis": "tran",
  "actions": [
    {"type": "drive_node_voltage", "target": "N002", "value": "5V"}
  ]
}
```

In questo modo la futura pipeline puo trasformare lo scenario in una run
separata senza dover interpretare dipendenze implicite tra scenari.

Se dai dati disponibili non serve uno scenario, l'agente puo dichiararlo.

### Da quale step ripartire

La scelta dello step da rigenerare dipende dal tipo di scenario.

Scenario sui valori o sui parametri:

```text
esempi:
- cambiare valore di una sorgente;
- cambiare resistenza equivalente;
- cambiare modello SPICE;
- aggiungere o rimuovere una analisi .tran.
```

In questo caso si possono riusare graph, normalizzazione e node map:

```text
01_graph.json
02_normalized_circuit.json
03_node_map.json
-> rigenerare 04/06/07/08
```

Scenario su stato o topologia elettrica:

```text
esempi:
- connettere due nodi;
- scollegare un terminale;
- spostare un terminale su un altro nodo.
```

Qui puo cambiare la mappa dei nodi, quindi bisogna ripartire dal primo livello
topologico interessato:

```text
graph base
-> scenario layer
-> 03_node_map
-> 04_values
-> 06_component_rules
-> 07_spice_emit
-> 08_spice_run
```

Nota sullo stato degli switch: nella versione attuale `close_switch` e gia
implementato come modifica netlist semplice nella cartella scenario. Non
rigenera la node map e non cambia il Graph JSON originale: inserisce una
resistenza piccola tra i due nodi dello switch gia presenti in
`06_component_rules.json`. In futuro, se serviranno scenari piu strutturali
come `open_switch` o cambi di topologia piu profondi, si potra usare il flusso
con scenario layer e rigenerazione da `03_node_map`.

Scenario di correzione del Graph JSON:

```text
esempi:
- componente riconosciuto male;
- batteria letta come due batterie;
- rele o switch non rappresentato correttamente;
- connessione importante mancante nel graph.
```

Questo non e uno scenario elettrico normale. E uno scenario di correzione del
graph. In questo caso non si modifica `01_graph.json` originale: si crea una
copia scenario del graph e si riparte da `01_io.py` o da un input graph
specifico dello scenario.

Se il graph sembra solo sospetto ma non ci sono prove sufficienti, l'agente deve
chiedere accesso all'immagine invece di correggere il graph in modo implicito.

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
scenario_case_001
scenario_case_002
scenario_case_003
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

Questo rende il sistema piu adatto a batch diversi e a circuiti futuri non
ancora visti.

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

Primitive attualmente implementate nella Pipeline 2.0:

```text
drive_node_voltage
change_source_value
change_component_value
close_switch
```

Questa e la lista controllata corrente. Per adesso l'agente puo proporre uno
scenario eseguibile solo se usa queste primitive.

Le semantiche operative dettagliate, con esempi JSON e traduzione SPICE, sono
gia state descritte nella sezione precedente `Stato implementativo attuale degli
scenari`. Qui basta fissare la regola generale:

- l'agente puo ragionare anche su primitive future o concettuali;
- la pipeline puo eseguire solo le primitive attualmente implementate;
- uno scenario con valori non concreti, per esempio `value: "unknown"`, non
  deve essere considerato eseguibile.

Questa lista non e definitiva: verra incrementata solo quando, analizzando nuove
immagini o nuovi batch, emergera davvero la necessita di una nuova primitiva.
In questo modo la complessita cresce per casi reali, non per ipotesi astratte.

L'agente non deve generare liberamente una netlist SPICE completa. Deve invece
proporre uno scenario strutturato usando queste primitive. La pipeline controlla
che lo scenario sia valido, applicabile e riproducibile.

Importante: le primitive controllate non vanno confuse con gli esiti
diagnostici.

Le primitive descrivono cosa viene modificato nello scenario:

```text
drive_node_voltage
change_source_value
change_component_value
close_switch
```

Gli esiti diagnostici descrivono cosa e successo dopo l'esecuzione e il
confronto base/scenario:

```text
resolved_candidate
partially_resolved
not_resolved
unknown
```

Questi restano identificatori tecnici interni. Nell'interfaccia web possono
essere mostrati con etichette piu leggibili:

```text
resolved_candidate -> Resolved
partially_resolved -> Partially resolved
not_resolved -> Not resolved
unknown -> Inconclusive
```

Esempio generale:

```text
scenario 1 -> drive_node_voltage su N002 -> resolved_candidate
scenario 2 -> change_source_value su VVCC -> partially_resolved
scenario 3 -> drive_node_voltage su N004 -> partially_resolved
```

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

Nella prima risposta read-only l'agente dovrebbe proporre al massimo tre
scenari candidati. L'esecuzione avviene solo dopo scelta dell'utente.

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
-> proposta di scenario 1/2/3
-> utente sceglie uno scenario
-> copia output base in cartella scenario
-> modifica controllata delle copie
-> netlist scenario
-> esecuzione ngspice
-> lettura stdout/stderr/risultati
-> confronto con il run precedente
-> nuova diagnosi
-> scenario successivo, se necessario
```

Questa logica e importante nei casi in cui un singolo scenario non basta:
prima si puo dover introdurre un riferimento di massa, poi chiarire una
sorgente ambigua, poi modellare un componente complesso, poi provare un
contatto aperto/chiuso, poi confrontare due condizioni di funzionamento.

Quindi l'agente dovrebbe mantenere una lista ordinata di scenari, eseguirli uno
alla volta solo dopo scelta o conferma dell'utente e aggiornare la diagnosi dopo
ogni run. Ogni scenario deve dichiarare:

- quale problema prova a verificare;
- quali assunzioni introduce;
- quali primitive usa;
- quale primo step pipeline va rigenerato;
- quale risultato atteso ha;
- quale risultato SPICE ha prodotto;
- quali grandezze sono state confrontate con la run base;
- se risolve, peggiora o lascia invariato il problema.

Il ciclo deve fermarsi quando:

- viene trovato uno scenario coerente con il sintomo utente;
- gli scenari ragionevoli sono esauriti;
- manca un dato essenziale che richiede input dell'utente;
- una modifica proposta non e validabile automaticamente.

Se gli scenari iniziali sono stati tutti eseguiti e nessuno risulta
`resolved_candidate`, l'agente non deve fermarsi automaticamente. Deve usare i
risultati gia ottenuti per decidere il prossimo scenario piu informativo.

Il prossimo scenario puo essere combinato, ma non deve essere una somma cieca di
tutto. L'agente deve combinare solo le azioni che hanno prodotto evidenze
complementari.

Importante: `not_resolved` non significa automaticamente "scenario inutile".
Significa solo che quello scenario non e sufficiente da solo. Prima di
scartarlo, l'agente deve capire se e:

- `not_resolved` e irrilevante: non cambia grandezze utili e non prepara
  nessuna condizione elettrica;
- `not_resolved` ma abilitante: non risolve da solo, pero chiude uno switch,
  crea un riferimento, completa un percorso di corrente o prepara una
  condizione necessaria per un altro scenario.

Gli scenari `not_resolved` ma abilitanti possono entrare in uno scenario
combinato. Gli scenari `not_resolved` irrilevanti vanno invece lasciati fuori.

Quando l'utente chiede una valutazione sugli scenari gia eseguiti, l'agente non
deve limitarsi a ripetere i titoli. Deve leggere i file scenario gia prodotti e
rispondere in modo grounded, per esempio:

- quale scenario ha dato l'effetto piu forte;
- quale scenario ha solo localizzato meglio la causa;
- quale scenario non basta da solo ma resta utile come indizio;
- se conviene proporre un nuovo scenario singolo, uno scenario combinato oppure
  chiudere il caso con una conclusione finale.

Esempio generale di scenari complementari:

```text
scenario_1 close_switch:
  non risolve da solo, ma puo essere abilitante per creare un percorso verso massa.

scenario_2 drive_node_voltage N004:
  attiva N004 e N001, ma non crea ancora una soluzione completa.

scenario_3 drive_node_voltage N003:
  attiva solo il ramo del condensatore, poco utile in .op per il problema principale.

prossimo scenario ragionevole:
  close_switch + drive_node_voltage N004

scenario da evitare come primo passo:
  close_switch + drive_node_voltage N004 + drive_node_voltage N003
  perche combina anche un ramo che non ha mostrato evidenza centrale rispetto al sintomo.
```

Quindi l'utente puo chiedere in chat:

```text
Gli scenari non hanno risolto. Quale scenario provo adesso?
Possiamo combinarne alcuni?
```

L'agente deve rispondere proponendo un nuovo scenario tecnico self-contained,
usando solo primitive supportate e spiegando perche include o esclude certe
azioni.

In questo modo l'agente non e solo uno spiegatore del primo output SPICE, ma un
assistente diagnostico che esplora ipotesi controllate e confronta risultati.

### Dopo l'esecuzione di uno scenario

Quando l'utente sceglie uno scenario in chat, la risposta successiva
dell'agente non deve limitarsi a dire che la simulazione e stata eseguita.
Deve confrontare il risultato dello scenario con la run base.

Domande che l'agente deve porsi dopo ogni scenario:

- SPICE prima falliva e ora riesce?
- `stderr` e migliorato, peggiorato o invariato?
- il nodo o ramo legato al problema utente e cambiato?
- la corrente nel carico interessato e diventata significativa?
- lo scenario conferma l'ipotesi, la smentisce o resta inconclusivo?
- conviene eseguire un altro scenario tra quelli gia proposti?
- serve proporre un nuovo scenario?
- serve chiedere un dato all'utente, per esempio valore mancante o immagine?

La risposta dopo uno scenario dovrebbe avere una forma semplice:

```text
1. Scenario eseguito
2. Cosa e cambiato rispetto alla run base
3. Il problema sembra risolto?
4. Interpretazione
5. Prossimo passo consigliato
```

Esempio:

```text
Ho eseguito lo scenario 1, cioe la chiusura dello switch.
Rispetto alla run base, N002 ora sale a 5 V, ma N003 e N004 restano a 0 V.
Quindi lo switch aperto era una parte del problema, ma non basta a far
accendere LED e lampada.
Il prossimo scenario piu utile e alimentare il ramo LED o il ramo lampada.
```

Questo rende l'agente iterativo: non produce una diagnosi unica e definitiva,
ma guida l'utente attraverso esperimenti SPICE controllati.

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

Esempio concettuale futuro, utile quando si sospetta un errore topologico:

```json
{
  "scenario_id": "repair_input_branch",
  "reason": "The current load path seems topologically inconsistent with the image and may require graph correction before a reliable rerun."
}
```

Questo esempio non rappresenta uno scenario oggi eseguibile nella Pipeline 2.0.
Serve solo a mostrare che, in futuro, l'agente potra proporre anche scenari di
correzione topologica o graph-correction. Nella versione attuale, gli scenari
eseguibili restano limitati alle primitive supportate e le correzioni di
topologia piu profonde devono essere trattate come scenari futuri o come casi
che richiedono immagine e revisione del graph.

## Ruolo dell'agente e ruolo della pipeline

La separazione dei ruoli e importante.

L'agente:

- legge il contesto;
- interpreta il problema utente;
- propone spiegazioni;
- propone al massimo tre scenari controllati nella fase read-only;
- aspetta la scelta dell'utente prima di far partire uno scenario;
- confronta risultati base e risultati scenario.

La pipeline:

- non sovrascrive mai gli output originali;
- valida gli scenari;
- copia gli output base in una cartella scenario;
- traduce azioni generiche in SPICE;
- genera netlist scenario;
- esegue ngspice;
- salva risultati riproducibili.

Flusso completo:

```text
utente descrive problema
-> agente legge output 08 e contesto tecnico
-> agente propone massimo 3 scenari candidati
-> utente sceglie uno scenario
-> pipeline copia gli output base in una cartella scenario
-> pipeline valida lo scenario
-> pipeline modifica solo le copie
-> pipeline genera netlist scenario
-> ngspice esegue lo scenario
-> agente confronta base vs scenario
-> agente spiega il risultato
```

Questa separazione evita che il modello generi netlist arbitrarie.

## Forma dell'interfaccia

L'agente puo essere implementato in modo progressivo.

### Versione 1: chat CLI

Possibile versione futura o alternativa da terminale:

```powershell
python scripts\pipeline_2.0\agent\diagnostic_agent.py --batch <batch> --circuit <circuit>
```

Oppure con domanda diretta:

```powershell
python scripts\pipeline_2.0\agent\diagnostic_agent.py --batch <batch> --circuit <circuit> --question "Perche il LED non si accende?"
```

Questa versione non e quella scelta come percorso principale attuale. Potrebbe
essere utile piu avanti per test rapidi senza aprire il sito.

Farebbe:

- carica gli output gia prodotti;
- costruisce il contesto diagnostico;
- chiama il modello;
- stampa la risposta;
- salva la conversazione.

### Versione 2: sito web diagnostico

La versione scelta come percorso principale attuale e una piccola applicazione
web locale.

Nella prima versione web non servono bottoni per gli scenari. Il sito funziona
come una chat:

```text
1. selezione batch/circuito;
2. campo testo per il problema utente;
3. risposta dell'agente;
4. utente scrive "esegui scenario 1";
5. backend interpreta la scelta;
6. backend chiama 12_controlled_scenarios.py;
7. agente spiega il confronto base vs scenario.
```

I bottoni potranno essere aggiunti piu avanti come comodita grafica, ma non sono
necessari per dimostrare il comportamento agentico. La parte importante e che
la conversazione mantenga memoria degli scenari proposti e che ogni scenario sia
eseguito solo dopo una richiesta esplicita dell'utente.

Struttura possibile:

```text
-------------------------------------------------------------
| Circuiti / stato | Visualizzazione circuito | Chat agente  |
|------------------|--------------------------|--------------|
| circuito READY   | immagine originale       | domanda      |
| circuito PARTIAL | graph/topologia          | risposta     |
| circuito NOT_READY | nodi / warning         | follow-up    |
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

Struttura attuale rilevante:

```text
scripts/pipeline_2.0/json_to_spice/
|-- 09_web_chat.py
|-- 10_build_diagnostic_context.py
|-- 11_agent_readonly.py
|-- 12_controlled_scenarios.py
|-- agent_readonly/
|   |-- openai_runner.py
|   |-- preview_builder.py
|   |-- prompt_builder.py
|   `-- scenario_prompt.py
`-- web_chat/
    `-- templates/
```

Questa e la struttura reale oggi in uso. In futuro potra ancora essere
rifattorizzata, ma per la tesi conviene descrivere prima cio che esiste davvero.

### Circuit loader

Nella versione attuale il caricamento del circuito e distribuito tra
`10_build_diagnostic_context.py`, `11_agent_readonly.py` e i moduli sotto
`agent_readonly/`.

Il comportamento atteso resta questo:

- capire quali file esistono;
- distinguere file base e file scenario;
- preparare un contesto coerente senza duplicare inutilmente gli artefatti.

### Manifest/context builder

Costruisce il manifest ordinato per il modello AI.

Questo modulo dovrebbe corrispondere allo step:

```text
10_build_diagnostic_context.py
```

Nella versione corrente non deve duplicare i contenuti dei file 01-08. Deve
produrre un manifest leggero con path, ruoli, mini-summary tecnico e regole
operative.

### Prompt builder

Trasforma manifest e artefatti originali in un prompt controllato.

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

Modulo ancora concettuale per versioni piu avanzate.

Puo permettere all'agente di richiamare strumenti interni del sistema:

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

Il comportamento operativo resta volutamente semplice:

- legge `10_diagnostic_context.json`;
- carica i file reali indicati dal manifest;
- legge la domanda utente;
- costruisce il prompt;
- chiama il modello;
- salva risposta e chat history.

Nella versione attuale questa parte e gia collegata tramite
`11_agent_readonly.py` e i moduli in `agent_readonly/`. La web chat passa il
modello scelto dall'utente allo step `11`.

Modelli selezionabili nella web chat:

```text
gpt-5.4
gpt-5.5
gpt-5.4-mini
gpt-5-mini
```

Il default corrente e `gpt-5.4`, scelto come compromesso tra qualita della
diagnosi e controllo del comportamento.

## Struttura attuale degli output principali

Nella versione attuale una cartella circuito contiene soprattutto output
tecnici della Pipeline 2.0 e file agent/chat generati su richiesta:

```text
outputs/pipeline2.0/<batch>/<circuit>/
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
|-- 10_diagnostic_context.json
|-- 11_agent_input_preview_chat.md
|-- 11_agent_prompt_chat.md
|-- 11_agent_response_chat.md
`-- scenarios/
    `-- scenario_1/
        |-- scenario.json
        |-- scenario_status.json
        |-- scenario_copy_manifest.json
        |-- 12_controlled_scenarios.json
        |-- scenario_comparison.json
        |-- base_snapshot/
        `-- run/
```

`proposed_scenarios.json` e `chat_history.json` restano possibili output futuri.
Per ora gli scenari proposti vivono nella risposta chat dell'agente, mentre lo
storico conversazione e mantenuto dal sito per batch/circuito.

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
11_agent_response.md / 11_agent_response_chat.md
chat history lato browser o file di supporto
```

Questo livello era gia sufficiente per una prima demo ed e tuttora la base piu
semplice del sistema.

Questo livello oggi esiste gia dentro la web chat locale: `11_agent_readonly.py`
resta read-only anche quando il sito e gia attivo.

### Livello 2: agente che propone scenari

L'agente non esegue ancora nulla, ma produce scenari candidati. Questi scenari
sono proposte diagnostiche: diventano run SPICE solo se l'utente ne sceglie uno.

Output possibile:

```text
scenari tecnici inclusi nella risposta agente
```

Anche questo livello e gia presente nella pratica: gli scenari vengono proposti
nella risposta chat e poi interpretati da `09_web_chat.py`.

### Livello 3: agente con strumenti

L'agente puo chiedere alla pipeline di:

- creare uno scenario;
- copiare gli output originali in una cartella scenario;
- rigenerare la netlist;
- eseguire ngspice;
- confrontare base e scenario;
- produrre una risposta finale.

Questo livello e oggi parzialmente implementato: l'agente non chiama strumenti
in autonomia generale, ma la web chat traduce richieste controllate come
"esegui scenario 1" nell'attivazione dello step `12`.

### Livello 4: interfaccia web

Il sito permette di selezionare circuiti, vedere output tecnici e dialogare con
l'agente.

Questa fase non e piu solo futura: una prima versione e gia attiva e viene
usata per i test reali sui circuiti del Batch A.

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

Stato attuale: completata sul primo esperimento Batch A.

- validare `08_spice_run.py` su piu circuiti;
- estendere gradualmente il numero di circuiti coperti;
- poi passare agli altri batch disponibili;
- osservare quali problemi ricorrono.

### Fase 2: contesto diagnostico

Stato attuale: implementata.

- trasformare `09` nel punto di ingresso della chat/web locale;
- implementare `10_build_diagnostic_context.py` come manifest leggero;
- implementare `11_agent_readonly.py`;
- produrre un manifest unico per circuito.

### Fase 3: chat diagnostica read-only

Stato attuale: implementata nella web chat locale.

- `09_web_chat.py` apre il sito locale sul circuito scelto;
- l'utente scrive un problema in chat;
- `09` chiama `10_build_diagnostic_context.py`;
- `09` chiama `11_agent_readonly.py`;
- la risposta viene mostrata nel sito;
- la risposta viene salvata come `11_agent_response_chat.md`;
- lo storico chat e mantenuto nel browser per batch/circuito;
- l'agente propone scenari, ma lo step `11` resta read-only.

### Fase 4: scenari controllati

Stato attuale: implementata in versione minimale e generale.

- definire poche azioni scenario generali;
- far produrre all'agente scenari tecnici nella risposta chat;
- richiedere scelta esplicita dell'utente in chat prima di eseguire uno scenario;
- interpretare frasi semplici come "esegui scenario 1" o "prova il secondo";
- validare gli scenari nella pipeline;
- copiare gli output originali in una cartella scenario;
- modificare solo le copie;
- generare netlist scenario;
- rieseguire gli step necessari a partire dal primo step interessato;
- confrontare base vs scenario.

Stato attuale:

```text
implementato il primo ciclo tecnico per drive_node_voltage, change_source_value,
change_component_value e close_switch:
scelta scenario -> copia base/run -> modifica netlist scenario -> ngspice scenario
-> scenario_comparison.json.
```

Implementato anche il rientro dei risultati scenario nell'agente:

```text
10_diagnostic_context.json ora include executed_scenarios.
11_agent_prompt include scenario.json, scenario_status.json,
12_controlled_scenarios.json e scenario_comparison.json per ogni scenario
gia presente nella cartella scenarios/.
```

`scenario_comparison.json` include anche `diagnostic_outcome`, cioe una prima
classificazione automatica dell'esito:

```text
resolved_candidate
partially_resolved
not_resolved
unknown
```

Se nel campo `compare` dello scenario compare `stderr`, lo step `12` confronta
il numero di warning ngspice tra base run e scenario run.

Questo permette alla chat di rispondere anche a domande successive, per esempio:

```text
Quale scenario risolve il problema?
Perche scenario 2 e solo parziale?
Che cosa ha confermato scenario 3?
```

La chat non deve limitarsi a elencare gli scenari. Quando la domanda riguarda
gli scenari gia eseguiti, il prompt passa a una modalita di confronto:

```text
1. identifica lo scenario con outcome piu forte;
2. usa scenario_comparison.json per motivare la scelta;
3. distingue lo scenario risolutivo dagli scenari solo parziali;
4. usa stop_automation per decidere se l'automazione puo fermarsi.
```

Esempio generale di riepilogo scenario:

```text
scenario_1 -> resolved_candidate, stop_automation=true
scenario_2 -> partially_resolved, stop_automation=false
scenario_3 -> partially_resolved, stop_automation=false
```

Quindi, alla domanda "Quale scenario risolve il problema?", la risposta attesa
e che `scenario_1` e il candidato risolutivo principale, mentre `scenario_2` e
`scenario_3` sono scenari diagnostici di supporto.

La logica reale pero deve restare prudente: un `resolved_candidate` non equivale
automaticamente a "problema sicuramente risolto" in senso fisico assoluto. E una
classificazione tecnica utile per l'agente, da confermare sempre collegando il
risultato al sintomo dell'utente e alle grandezze effettivamente cambiate.

### Budget scenari per circuito

Durante i test reali e emersa una regola pratica molto importante: senza un
limite massimo, l'agente rischia di proporre scenari sempre piu fini senza
arrivare mai a una chiusura diagnostica chiara.

Per questo la pipeline adotta ora una regola semplice:

- massimo `5` scenari eseguibili per ogni circuito;
- `10_diagnostic_context.json` include un blocco `scenario_budget` con:
  - massimo scenari;
  - scenari gia eseguiti;
  - scenari rimanenti;
  - `last_scenario_available`;
  - `budget_exhausted`;
- se resta **1 solo scenario**, l'agente deve proporre **un solo scenario finale**;
- se il budget e esaurito, l'agente **non deve piu proporre nuovi scenari**;
- a budget esaurito deve fornire una **conclusione diagnostica finale** basata
  su tutte le evidenze raccolte.

La conclusione finale puo essere attivata anche prima dell'esaurimento del
budget, se l'utente la chiede esplicitamente con domande del tipo:

```text
Qual e la diagnosi finale piu probabile?
Possiamo fermarci qui?
Dopo questi test, cosa possiamo concludere?
```

In quel caso l'agente deve passare a una modalita di chiusura:

- sintetizza gli scenari gia eseguiti;
- distingue ipotesi rafforzate, indebolite e ancora aperte;
- dice se conviene fermarsi oppure se resta un unico test davvero decisivo;
- evita di proporre automaticamente un nuovo scenario solo perche c'e ancora
  budget disponibile.

Questa regola non serve a garantire che ogni circuito sia completamente
"risolto" entro cinque prove. Serve a forzare una chiusura utile del caso, con
una delle seguenti uscite:

- problema risolto;
- causa localizzata;
- limite topologico / graph issue;
- risultato ancora inconclusivo.

La web chat applica anche un guardrail tecnico: la creazione di un sesto
scenario nuovo viene bloccata lato codice.

### Fase 5: chat iterativa e web completa

Stato attuale: avviata e usata nel primo esperimento Batch A, ma non ancora
completa come prodotto finale.

Gia presente:

- storico chat per batch/circuito nel browser;
- selettore modello nella chat web;
- sidebar con base run e scenari creati;
- esecuzione scenario dalla frase "esegui scenario 1/2/3";
- esecuzione anche dell'ultimo scenario appena proposto con formule come
  "esegui questo scenario";
- confronto base/scenario;
- domande successive sugli scenari gia eseguiti;
- modalita di risposta finale quando l'utente chiede una conclusione
  diagnostica;
- singola conversazione persistente per batch/circuito anche quando si cambia
  vista tra base run e scenari gia creati.

Prossimi esperimenti:

1. **Esperimento 2 - scenari piu potenti e modifiche netlist/topologia**

   Obiettivo: ampliare la libreria di primitive scenario in modo generale,
   senza legarla al solo Batch A.

   Direzioni previste:

   - creare un piccolo file di supporto, probabilmente YAML, che documenti le
     primitive scenario disponibili;
   - aggiungere scenari che modificano la netlist in modo piu strutturale;
   - supportare azioni come collegare nodi, alimentare gruppi di pin,
     aggiungere una batteria, aggiungere una sorgente, aggiungere una
     resistenza o un ramo equivalente;
   - mantenere sempre separata la base run dagli scenari;
   - salvare in modo esplicito cosa lo scenario ha cambiato.

   Esempi di scenario futuri:

   ```text
   chiudi lo switch e alimenta i pin collegati del connector
   aggiungi una batteria se il circuito non ha una sorgente utile
   aggiungi una sorgente di corrente controllata
   aggiungi una resistenza equivalente o un carico minimo
   collega due nodi solo nella run scenario
   ```

2. **Esperimento 3 - automazione agentica degli scenari**

   Obiettivo: far eseguire all'agente piu scenari in sequenza, entro un limite
   controllato, per provare a risolvere o localizzare il problema.

   Flusso desiderato:

   ```text
   sintomo utente
   -> agente propone scenario
   -> pipeline esegue scenario
   -> agente legge scenario_comparison.json
   -> agente decide se fermarsi o provare un altro scenario
   -> massimo 5 scenari
   -> conclusione finale
   ```

   Questa fase deve partire solo dopo aver reso solide le primitive
   dell'Esperimento 2.

3. **Esperimento 4 - visualizzatore/simulatore del circuito**

   Obiettivo: costruire una visualizzazione stile simulatore, non un nuovo
   motore SPICE.

   La regola centrale e:

   ```text
   il viewer parte dalla netlist della run selezionata
   ```

   Quindi:

   - base run e scenario run possono avere netlist diverse;
   - se uno scenario cambia topologia, il viewer deve visualizzare quella
     topologia scenario;
   - ngspice resta il motore di simulazione;
   - il viewer usa netlist, node map, coordinate immagine e risultati SPICE per
     mostrare nodi, tensioni, correnti e rami attivi.

## Stato dopo il primo esperimento Batch A

Il primo esperimento completo sul Batch A ha confermato che l'architettura
descritta in questo documento e praticabile.

Sono stati coperti i circuiti:

```text
a01, a02, a03, a04, a05, a06, a07, a08, a09, a10
```

Risultato operativo:

- gli step `01-08` producono output SPICE per tutti i circuiti;
- `a03` resta un caso di fallimento SPICE/topologia, utile per validare la
  modalita image-assisted e i limiti del Graph JSON;
- `09_web_chat.py` permette di interrogare l'agente da sito locale;
- `10_build_diagnostic_context.py` indicizza output base e scenari gia eseguiti;
- `11_agent_readonly.py` genera risposte diagnostiche e scenari candidati;
- `12_controlled_scenarios.py` crea run scenario separate e confronta base vs
  scenario;
- i markdown `experiment_ai/pipeline2_spice_analysis/batchA/a01.md` ...
  `a10.md` documentano il comportamento manuale atteso dall'agente.

Questa fase non dimostra ancora che l'agente sia perfetto. Dimostra pero che il
flusso e riproducibile:

```text
sintomo utente
-> risposta agente grounded
-> scenario scelto dall'utente
-> run scenario separata
-> confronto base/scenario
-> nuova risposta o conclusione diagnostica
```

La prossima validazione non deve cambiare continuamente il prompt circuito per
circuito. Deve invece misurare quanto bene lo stesso schema generale regge su
piu casi, usando i report Batch A come riferimento.

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
