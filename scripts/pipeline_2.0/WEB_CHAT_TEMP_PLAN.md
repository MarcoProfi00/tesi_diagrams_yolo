# Pipeline 2.0 - Web Chat Plan

Questa nota fissa il ruolo della web chat, il suo stato attuale e i prossimi
passi. Non descrive singoli circuiti: deve restare un promemoria generale
sull'interfaccia di `09_web_chat.py`.

## Idea generale

La Pipeline 2.0 resta divisa in due blocchi:

```text
01-08 = pipeline tecnica fino a ngspice
09    = interfaccia locale chat/web
10    = manifest diagnostico
11    = agente read-only
12    = scenari controllati
```

Lo step `09` non deve diventare un backend applicativo permanente. Deve avviare
un server locale temporaneo, senza database, login, deploy o API pubbliche.

Gli output tecnici della pipeline restano salvati nelle cartelle `outputs/`.

Stato attuale della conversazione:

- per la base storica e gli esperimenti non dedicati, la chat puo ancora usare
  una cache lato browser per batch/circuito;
- per `experiment2`, la conversazione ufficiale viene salvata lato server in
  file locali per circuito.

Gli output riproducibili restano invece nei file della pipeline:

```text
10_diagnostic_context.json
11_agent_input_preview_chat.md
11_agent_prompt_chat.md
11_agent_response_chat.md
scenarios/<scenario_id>/
```

Per Esperimento 2 si aggiunge anche:

```text
experiment2_chat/
  chat_history.json
  chat_history.md
  scenario_registry.json
  scenario_registry.md
```

Questi file diventano la sorgente ufficiale della conversazione per il circuito
selezionato nell'esperimento. La chat history salva il dialogo; il registry
salva invece gli scenari proposti ed eseguiti con una numerazione globale
user-friendly per circuito.

## Flusso generale

```text
run_pipeline2
-> esegue 01-08
-> opzionalmente si avvia 09_web_chat come script separato
-> si apre una pagina locale nel browser
-> utente sceglie o conferma batch/circuito
-> utente scrive il problema
-> 09 chiama 10_build_diagnostic_context.py
-> 09 chiama 11_agent_readonly.py
-> la risposta dell'agente viene mostrata nella chat
```

Scenari dalla chat:

```text
utente scrive "esegui scenario 1" oppure "esegui questo scenario"
-> 09 interpreta la scelta
-> 09 recupera lo scenario proposto da 11
-> 09 chiama 12_controlled_scenarios.py
-> 12 crea una cartella scenario separata
-> 12 modifica solo copie degli output originali
-> 12 applica la modifica alla netlist scenario
-> 12 esegue ngspice se 09 e stato avviato con ngspice disponibile
-> 12 crea scenario_comparison.json
-> 10 indicizza gli scenari eseguiti
-> 11 puo confrontare base run e scenario run nelle risposte successive
```

## Ruolo di 09_web_chat

Lo step `09` deve restare un orchestratore leggero.

Deve occuparsi di:

```text
server locale
lettura degli output pipeline
render dei frammenti dinamici
API temporanee della chat
aggancio a 10, 11 e 12
```

Non deve:

```text
sostituire la pipeline tecnica
duplicare la logica di 10, 11 o 12
diventare un backend persistente
salvare uno stato applicativo complesso
```

## Layout grafico

Il sito deve essere uno strumento diagnostico, non una pagina descrittiva.
La vista iniziale deve mostrare subito il circuito selezionato e gli output
della pipeline.

La parte HTML/CSS/JS deve stare fuori da `09_web_chat.py`, in una cartella
dedicata:

```text
scripts/pipeline_2.0/json_to_spice/web_chat/
|-- templates/
|   `-- index.html
`-- static/
    |-- app.css
    `-- app.js
```

Questa cartella puo crescere gradualmente; nella prima versione puo esistere
anche solo `templates/index.html`.

Stato attuale:

```text
esiste templates/index.html
CSS e JS sono ancora inline nel template
static/app.css e static/app.js restano una possibile rifinitura futura
```

Schema logico del layout:

```text
+----------------------------------------------------------------+
| Header: Pipeline 2.0 Diagnostic Web Chat                       |
| batch / circuit | active run | SPICE status                    |
+----------------+--------------------------------+--------------+
| Run selector   | Evidence panel                 | Agent chat   |
|                |                                |              |
| Base run       | Main run title                 | messages     |
| scenario_N     | Image / status summary         |              |
| ...            | Graph / values / node map      | input        |
|                | Netlist / stdout / stderr      | controls     |
|                | Tran CSV / plot                |              |
+----------------+--------------------------------+--------------+
```

## Colonna sinistra: run selector

La colonna sinistra serve a scegliere quale run guardare:

```text
Base run
Scenario 1
Scenario 2
Scenario N
```

Stato attuale:

```text
la sidebar mostra Base run e gli scenari gia creati
quando uno scenario viene creato, la pagina si ricarica sulla run selezionata
la chat resta unica per il circuito
la sidebar mostra anche un'etichetta sintetica dell'esito scenario
```

Ogni run dovrebbe mostrare uno stato sintetico:

```text
success
warning
failed
not run
```

La sidebar potra diventare richiudibile piu avanti.

## Parte centrale: evidence panel

La parte centrale contiene gli artefatti tecnici. Non devono essere tutti
aperti di default, altrimenti la vista diventa sporca.

Usare pannelli richiudibili:

```text
Graph JSON
Values / values_bound
Node Map
Component Rules
SPICE Netlist
SPICE Run Summary
stdout
stderr
Transient CSV
Transient Plot
Scenario Definition
Scenario Status
Scenario Comparison
```

Di default conviene tenere aperti solo:

```text
SPICE Run Summary
SPICE Netlist
stderr, se non e vuoto
Transient Plot, se esiste
```

Gli altri file restano disponibili ma chiusi.

Il pannello centrale deve mostrare anche l'immagine originale del circuito,
quando disponibile.

## Colonna destra: diagnostic chat

La chat deve restare visibile anche quando l'utente cambia run nella sidebar.

Flusso base:

```text
utente scrive problema
-> 09 prepara la richiesta
-> 09 chiama 10 e 11
-> risposta agente mostrata nella chat
```

Stato attuale:

```text
la chat grafica esiste
il messaggio utente viene inviato a /api/chat
/api/chat aggiorna 10_diagnostic_context.json con user_problem
/api/chat genera preview e prompt chat
/api/chat chiama OpenAI tramite lo step 11 read-only
/api/chat mostra la risposta nella chat
la risposta viene renderizzata come Markdown
la UI mostra un indicatore di attesa mentre l'agente lavora
```

Quindi, al momento, `09_web_chat.py` e:

```text
visualizzazione output pipeline
+ chat agente read-only
+ orchestrazione scenari controllati
```

La chat salva file separati per non sovrascrivere gli esperimenti:

```text
11_agent_input_preview_chat.md
11_agent_prompt_chat.md
11_agent_response_chat.md
```

La risposta in chat e pensata per essere leggibile dall'utente. I blocchi JSON
tecnici degli scenari non vengono mostrati come contenuto principale della chat:
restano accessibili negli artefatti centrali dello scenario.

La UI mostra anche un messaggio di attesa:

```text
Agent is thinking
Executing scenario
```

e un blocco tecnico richiudibile `Execution details`, utile durante lo sviluppo.

## Scenari dalla chat

Flusso attuale:

```text
utente scrive "esegui scenario 1"
-> 09 riconosce la scelta
-> 09 estrae il JSON scenario dall'ultima risposta agente
-> 09 crea scenarios/<scenario_id>/
-> 09 salva scenario.json e scenario_status.json
-> 09 copia la base run in base_snapshot/ e run/
-> 09 chiama 12_controlled_scenarios.py
-> 12 applica le azioni supportate solo alla netlist in run/
-> 12 esegue ngspice se 09 e stato avviato con --ngspice-executable
-> 12 crea scenario_comparison.json
-> la sidebar mostra la nuova run scenario
```

Lo scenario viene sempre creato in una cartella separata e la base run originale
non viene modificata. Se `09_web_chat.py` non riceve un eseguibile ngspice, la
chat puo comunque creare/applicare lo scenario, ma non puo completare la parte
di simulazione e confronto.

## Controlli chat

La chat dovrebbe avere controlli minimi ma chiari:

```text
model selector
send message
clear chat
image enable button / command
```

### Selettore modello

Il selettore modello deve permettere all'utente di scegliere quale modello usare
per la risposta dell'agente.

Stato attuale:

```text
implementato
la scelta viene passata a 11_agent_readonly.py
la preferenza puo essere mantenuta lato browser
```

Modelli disponibili:

```text
GPT 5.4
GPT 5.5
GPT 5.4 mini
GPT 5 mini
```

Default corrente:

```text
GPT 5.4
```

### Gestione immagine

La gestione immagine deve seguire la policy gia decisa:

```text
default = immagine non inclusa
fallback = immagine usata solo se serve davvero
```

Due modalita utili:

```text
1. richiesta esplicita dell'utente, per esempio "usa immagine"
2. fallback automatico se ngspice fallisce e il contesto mostra forti segnali
   di problema topologico
```

In entrambi i casi l'immagine non deve diventare input predefinito.

## Termini tecnici usati nel sito

```text
Base run        = esecuzione principale prodotta dagli step 01-08
Scenario run    = esecuzione derivata da uno scenario scelto dall'utente
Artifact        = file prodotto dalla pipeline
Evidence panel  = pannello centrale con graph, values, netlist e risultati
Diagnostic chat = chat con l'agente
SPICE status    = stato dell'esecuzione ngspice
```

## Comandi possibili

Uso separato:

```powershell
python scripts\pipeline_2.0\json_to_spice\09_web_chat.py --batch <batch> --circuit <circuit>
```

Uso su una root esperimento separata:

```powershell
python scripts\pipeline_2.0\json_to_spice\09_web_chat.py --batch <batch> --experiment <experiment> --circuit <circuit>
```

Esempio per Esperimento 2:

```powershell
python scripts\pipeline_2.0\json_to_spice\09_web_chat.py --batch batchA --experiment experiment2 --circuit a01 --ngspice-executable "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

Quando `--experiment` e presente, la chat legge e scrive in:

```text
outputs/pipeline2.0/<batch>/<experiment>/<circuit>/
```

La memoria browser usa una chiave distinta per batch, esperimento e circuito,
quindi le conversazioni di Esperimento 1 e Esperimento 2 non si mescolano.

Uso futuro integrato nella pipeline:

```powershell
python scripts\pipeline_2.0\run_pipeline2.py --batch <batch> --circuits <circuit> --run-spice --open-web
```

La seconda forma e comoda, ma conviene implementarla solo dopo aver testato bene
`09_web_chat.py` come script separato.

## Nota sul backend

Tecnicamente una pagina web che chiama Python, OpenAI, 10, 11 e 12 ha bisogno
di un piccolo server locale.

Pero questo non deve essere inteso come backend applicativo completo:

```text
no database
no login
no deploy
no stato permanente obbligatorio
no API pubblica
```

E solo un server locale temporaneo per la demo e per lo sviluppo.

## Regola importante

L'agente non deve modificare file direttamente.

```text
agente = interpreta, spiega, propone scenari
pipeline = valida, copia, modifica, riesegue SPICE
utente = sceglie esplicitamente quale scenario eseguire
```

Questa separazione serve a mantenere la Pipeline 2.0 riproducibile e difendibile
nella tesi.

## Stato operativo e TODO

Questa e la scaletta aggiornata. Alcuni punti sono gia implementati, altri
restano da completare. La parola `TODO` qui indica una checklist di progetto,
non necessariamente una funzione totalmente assente.

### TODO 1 - Chat collegata a 10 e 11

Quando l'utente scrive un sintomo nella chat:

```text
utente scrive problema/sintomo
-> 09 riceve il messaggio su /api/chat
-> 09 aggiorna o rigenera 10_diagnostic_context.json con user_problem
-> 09 esegue 11_agent_readonly.py con --run-agent
-> 11 produce una risposta agente
-> 09 legge la risposta
-> 09 la mostra nella chat
```

Per non sovrascrivere altri output, la risposta prodotta dalla chat va in un
file dedicato:

```text
11_agent_response_chat.md
```

Stato:

```text
implementato
```

### TODO 2 - Mostrare cosa viene eseguito

Durante lo sviluppo, la chat dovrebbe mostrare o salvare un piccolo log tecnico:

```text
Executed:
- 10_build_diagnostic_context.py
- 11_agent_readonly.py --run-agent --model <selected_model>

Output:
- 10_diagnostic_context.json
- 11_agent_response_chat.md
```

Questo serve a validare che il sito stia davvero chiamando gli step giusti.

### TODO 3 - Scelta modello

Il modello scelto deve essere passato a `11_agent_readonly.py`.

Stato:

```text
implementato
```

### Clear chat in experiment2

Per `experiment2`, il pulsante `Clear` e un reset della sessione sperimentale
del circuito corrente. Non modifica gli output base 01-08, ma azzera gli
artefatti prodotti dalla conversazione:

```text
experiment2_chat/chat_history.json
experiment2_chat/chat_history.md
experiment2_chat/scenario_registry.json
experiment2_chat/scenario_registry.md
scenarios/
10_diagnostic_context.json
11_agent_input_preview_chat.md
11_agent_prompt_chat.md
11_agent_response_chat.md
```

Questo permette di ripartire puliti sullo stesso circuito senza rigenerare gli
output tecnici iniziali dell'esperimento.

### TODO 4 - Immagine su richiesta

Non includere l'immagine di default.

Quando l'agente la richiede o l'utente scrive un comando tipo:

```text
usa immagine
```

la chat deve abilitare una chiamata image-assisted solo per il caso corrente.

Stato:

```text
parzialmente implementato
```

Nota:

```text
il fallback automatico con immagine nei casi di forte sospetto topologico e gia presente
la richiesta esplicita "usa immagine" come controllo conversazionale dedicato resta da consolidare meglio
```

### TODO 5 - Parsing scelta scenario

Dopo che l'agente propone scenari, l'utente puo scrivere:

```text
esegui scenario 1
prova lo scenario 2
facciamo il terzo
esegui questo scenario
esegui lo scenario appena proposto
```

La chat deve riconoscere la scelta e recuperare il JSON tecnico dello scenario
proposto nella risposta precedente.

Prima versione semplice:

```text
"scenario 1" / "primo" -> scenario_1
"scenario 2" / "secondo" -> scenario_2
"scenario 3" / "terzo" -> scenario_3
"questo scenario" -> ultimo scenario proposto
"scenario appena proposto" -> ultimo scenario proposto
```

Stato:

```text
implementato per richieste semplici
per experiment2: implementato registry scenari file-based
```

Per `experiment2`, la chat registra gli scenari in una lista globale per
circuito:

```text
Scenario 1
Scenario 2
Scenario 3
Scenario 4
Scenario 5
```

I primi tre scenari vengono normalmente salvati dopo la prima diagnosi. Se
l'agente propone scenari successivi, anche combinati, questi vengono accodati
come `Scenario 4` e `Scenario 5`. Le formule ordinali come `il primo`,
`il secondo`, `il quarto` puntano sempre alla numerazione globale. Le formule
come `l'ultimo`, `quest'ultimo` o `quello appena proposto` puntano invece
all'ultimo scenario aggiunto al registry.

### TODO 6 - Collegare 12 controlled scenarios

Quando l'utente sceglie uno scenario:

```text
09 passa lo scenario a 12_controlled_scenarios.py
-> 12 crea una cartella scenario separata
-> 12 copia gli output originali
-> 12 modifica solo le copie
-> 12 applica la modifica alla netlist copiata in run/
-> 12 riesegue ngspice se richiesto/disponibile
-> 12 salva risultato scenario
```

Gli output originali non devono mai essere sovrascritti.

Stato:

```text
implementato per primitive semplici e scenario run separata

09:
- crea cartella scenario
- salva scenario.json
- copia base_snapshot/ e run/
- chiama 12
- passa ngspice a 12 se disponibile
- ricarica la pagina sulla run scenario
- mantiene una chat unica per il circuito

12:
- supporta drive_node_voltage
- supporta change_source_value su sorgenti SPICE esistenti
- supporta change_component_value su componenti semplici gia emessi
- supporta close_switch su switch gia riconosciuti
- modifica solo run/07_netlist.cir
- salva 12_controlled_scenarios.json
- puo eseguire ngspice con --run-spice
- crea scenario_comparison.json dopo SPICE
- confronta anche stderr come warning count quando compare nel campo compare
```

Esempio generale:

```text
azione:
drive_node_voltage su un nodo di ingresso

netlist scenario:
VSCENARIO_<NODE> <NODE> 0 DC <value>

confronto:
v(<NODE>): cambia rispetto alla base run
v(<LOAD_NODE>): si attiva oppure resta invariato
i(<LOAD>): cresce, resta nulla oppure cambia solo parzialmente
```

### TODO 7 - Ciclo ricorsivo agente/scenario

Dopo l'esecuzione dello scenario:

```text
09 mostra il nuovo scenario nella sidebar
-> agente riceve base run + scenario run
-> agente confronta i risultati
-> agente dice se il problema sembra risolto
-> se non e risolto, propone scenario successivo
-> utente puo continuare a parlare con l'agente
```

Comportamento desiderato:

```text
sintomo utente
-> diagnosi agente
-> scenari proposti
-> scelta utente
-> scenario SPICE controllato
-> confronto
-> nuova diagnosi
-> eventuali altri scenari
```

Stato attuale:

```text
implementato in modalita manuale guidata dall'utente

gia presente:
- scenario creato dalla chat
- scenario visibile nella sidebar
- scenario_comparison.json creato dopo ngspice
- 10 indicizza executed_scenarios
- 11 puo rispondere a domande sugli scenari gia eseguiti
- 09 blocca la creazione di una sesta run scenario
- 11 puo passare a conclusione finale quando l'utente la chiede o quando il budget e esaurito
```

Estensione futura importante:

```text
modalita manuale:
utente sceglie esplicitamente quale scenario eseguire

modalita semi-automatica:
utente autorizza la chat a provare piu scenari fino a un limite
```

Nella modalita semi-automatica il controller non deve fermarsi al primo
scenario proposto. Deve poter eseguire piu scenari in sequenza, ma sempre entro
un limite controllato.

Regole di sicurezza:

```text
- nessuno scenario deve modificare la base run originale
- ogni scenario deve creare una nuova cartella separata
- il numero massimo di scenari automatici deve essere limitato
- ogni scenario deve salvare cosa ha cambiato e da quale step e ripartito
- l'agente deve spiegare perche passa allo scenario successivo
- se i risultati sono ambigui, deve fermarsi e chiedere conferma all'utente
- se serve correggere il graph, deve dichiararlo esplicitamente
```

Limite iniziale consigliato:

```text
max_auto_scenarios = 5
```

Stato attuale:

```text
max scenari eseguibili per circuito = 5
modalita automatica multi-scenario non ancora implementata
```

## Stato dopo il primo esperimento Batch A

La web chat e stata usata nel primo esperimento completo su Batch A.

Sono stati verificati:

- apertura della pagina per i circuiti `a01`-`a10`;
- visualizzazione base run e scenari dalla sidebar;
- chat unica per circuito anche cambiando vista tra base run e scenario;
- selettore modello;
- invio sintomo utente;
- risposta agente renderizzata come Markdown;
- esecuzione scenario da frasi semplici come `esegui scenario 1`;
- esecuzione dell'ultimo scenario proposto con frasi come `esegui questo scenario`;
- creazione cartelle scenario separate;
- esecuzione ngspice sugli scenari quando `--ngspice-executable` e disponibile;
- confronto base/scenario;
- domande successive sugli scenari gia eseguiti;
- conclusione finale su richiesta dell'utente;
- fallback automatico image-assisted nei casi topologici forti.

Questa verifica non rende la web app un prodotto finito, ma conferma che il
flusso principale e dimostrabile:

```text
base run -> domanda utente -> agente -> scenario scelto -> SPICE scenario
-> confronto -> nuova diagnosi o conclusione finale
```

## Animated SPICE Viewer

Questo punto e uno sviluppo futuro, da affrontare dopo la prima versione degli
scenari controllati.

L'obiettivo e aggiungere nella webapp una visualizzazione animata del circuito,
ispirata al comportamento di simulatori visuali come Falstad, ma costruita sui
nostri output Pipeline 1.0 / Pipeline 2.0.

Non vogliamo integrare Falstad direttamente. Vogliamo invece creare un viewer
nostro, piu semplice e controllabile, che mostri:

```text
immagine originale del circuito
+ overlay grafico sopra l'immagine
+ componenti riconosciuti
+ nodi SPICE
+ tensioni calcolate da ngspice
+ correnti calcolate da ngspice
+ indicatori animati sui rami attraversati da corrente
```

La finalita non e sostituire ngspice. ngspice resta il motore di simulazione.
Il viewer serve solo a rendere visibile il risultato della simulazione.

Esempio generale:

```text
ramo attivo     -> animato, perche passa corrente
ramo spento     -> grigio o disattivato
nodo attivo     -> evidenziato come nodo alimentato
nodo spento     -> evidenziato come nodo a 0 V
switch aperto   -> mostrato come ramo non conduttivo
```

## Dati necessari per il viewer

Le coordinate geometriche non sono nel `01_graph.json` usato da Pipeline 2.0.
Sono pero disponibili negli output intermedi della Pipeline 1.0, ad esempio:

```text
outputs/pipeline1.0/<batch>/03_estimate_terminals/<circuit>.json
```

Quel file contiene:

```text
image_width
image_height
bbox dei componenti
coordinate x/y dei terminali
orientamento stimato
stato dello switch, se disponibile
```

Pipeline 2.0 fornisce invece:

```text
03_node_map.json          -> terminali associati ai nodi SPICE
07_netlist.cir            -> componenti emessi in SPICE
08_ngspice_stdout.txt     -> tensioni/correnti della simulazione .op
08_tran.csv               -> serie temporali quando esiste .tran
08_tran_plot.png/svg      -> plot transitorio gia generato
```

Il viewer dovra unire questi due mondi:

```text
coordinate Pipeline 1.0
+ topologia/nodi Pipeline 2.0
+ risultati ngspice
= visualizzazione animata
```

Regola importante per gli scenari:

```text
il viewer deve partire dalla netlist della run selezionata
```

Questo significa che:

- la base run usa `outputs/pipeline2.0/<batch>/<circuit>/07_netlist.cir`;
- uno scenario usa `outputs/pipeline2.0/<batch>/<circuit>/scenarios/<scenario_id>/run/07_netlist.cir`;
- se uno scenario modifica la topologia, il viewer deve rappresentare la
  topologia dello scenario, non quella della base run;
- il confronto visuale Base run vs Scenario run dovra quindi trattare le due
  netlist come due circuiti potenzialmente diversi.

## Versione minima proposta

Prima versione semplice:

```text
1. mostrare l'immagine originale nel pannello centrale
2. disegnare un canvas trasparente sopra l'immagine
3. disegnare box o marker sui componenti riconosciuti
4. associare ogni terminale al nodo SPICE tramite 03_node_map.json
5. colorare i terminali/nodi in base alla tensione
6. animare indicatori tra i terminali dei componenti con corrente non nulla
7. lasciare grigi i componenti con corrente zero
8. mostrare tooltip o label con V/I principali
```

Questa versione non richiede ancora di ricostruire perfettamente tutti i fili
disegnati nell'immagine. L'animazione puo partire dai componenti:

```text
resistenza: animazione tra t1 e t2
lampada: animazione tra t1 e t2 se i != 0
LED: animazione tra anodo e catodo se i != 0
sorgente: marker di alimentazione
switch aperto: nessuna animazione
```

## Versione successiva

Dopo la versione minima:

```text
- disegnare collegamenti approssimati tra terminali dello stesso nodo
- animare anche i tratti di collegamento, non solo i componenti
- modulare velocita, spessore o colore in base alla corrente
- supportare anche risultati transienti da 08_tran.csv
- permettere il confronto visuale Base run vs Scenario run
- aggiornare la visualizzazione quando l'utente seleziona uno scenario nella sidebar
```

## Ordine di priorita

Questo viewer non deve bloccare il lavoro sugli scenari.

Ordine consigliato:

```text
1. congelare i risultati del primo esperimento Batch A
2. Esperimento 2: ampliare le primitive scenario e le modifiche netlist/topologia
3. Esperimento 3: automatizzare il ciclo agente -> scenario -> confronto
4. Esperimento 4: aggiungere Animated SPICE Viewer basato sulla netlist della run selezionata
5. estendere poi i test agli altri batch
```
