# Pipeline 2.0 - Temporary Web Chat Plan

Questa e una nota temporanea di lavoro. Serve solo a ricordare la scaletta per
la futura interfaccia chat/web della Pipeline 2.0. Potra essere eliminata quando
la struttura sara implementata o spostata nella documentazione definitiva.

## Idea generale

La Pipeline 2.0 resta divisa in due parti:

```text
01-08 = pipeline tecnica fino a ngspice
09    = interfaccia locale chat/web
10    = manifest diagnostico
11    = agente read-only
12    = scenari controllati
```

Lo step `09` non deve diventare un backend permanente. Deve avviare una
interfaccia locale temporanea, senza database e senza stato persistente
obbligatorio.

Quando il server locale viene chiuso, la chat in memoria si perde. Gli output
tecnici della pipeline restano invece salvati nelle cartelle `outputs/`.

## Flusso desiderato

```text
run_pipeline2
-> esegue 01-08
-> opzionalmente avvia 09_web_chat
-> apre una pagina locale nel browser
-> utente sceglie o conferma batch/circuito
-> utente scrive il problema
-> 09 chiama 10_build_diagnostic_context.py
-> 09 chiama 11_agent_readonly.py
-> la risposta dell'agente viene mostrata nella chat
```

In futuro:

```text
utente scrive "esegui scenario 1"
-> 09 interpreta la scelta
-> 09 recupera lo scenario proposto da 11
-> 09 chiama 12_controlled_scenarios.py
-> 12 crea una cartella scenario separata
-> 12 modifica solo copie degli output originali
-> 12 riesegue gli step necessari e ngspice
-> agente confronta base run e scenario run
-> agente dice se il problema sembra risolto o quale scenario provare dopo
```

## Prima versione minima

La prima implementazione di `09` dovrebbe fare solo questo:

```text
1. avviare una pagina locale;
2. ricevere batch e circuito;
3. mostrare lo stato minimo del circuito;
4. ricevere una domanda utente;
5. eseguire 10;
6. eseguire 11;
7. mostrare la risposta dell'agente.
```

Questa prima versione e stata superata: ora la web chat esegue gia la parte
read-only e prepara/applica il primo tipo di scenario controllato.

## Layout grafico

Il sito deve essere uno strumento diagnostico, non una pagina descrittiva.
La vista iniziale deve mostrare subito il circuito selezionato e gli output
della pipeline.

La parte HTML/CSS/JS deve stare fuori da `09_web_chat.py`, in una cartella
dedicata:

```text
scripts/pipeline_2.0/json_to_spice/web_chat/
`-- templates/
    `-- index.html
```

Lo script `09_web_chat.py` deve occuparsi solo di:

```text
server locale
lettura degli output pipeline
render dei frammenti dinamici
API temporanee della chat
```

Se il frontend cresce, potremo aggiungere:

```text
web_chat/static/app.css
web_chat/static/app.js
```

Layout base:

```text
┌─────────────────────────────────────────────────────────────┐
│ Header: Pipeline 2.0 Diagnostic Web Chat                    │
│ batch / circuit | active run | SPICE status                 │
├───────────────┬───────────────────────────────┬─────────────┤
│ Run selector  │ Evidence panel                │ Agent chat  │
│               │                               │             │
│ Base run      │ Main run title                │ messages    │
│ Scenario 1    │ Status summary                │             │
│ Scenario 2    │                               │ input       │
│ ...           │ Graph JSON                    │             │
│               │ Values                        │             │
│               │ Node Map                      │             │
│               │ Component Rules               │             │
│               │ SPICE Netlist                 │             │
│               │ SPICE stdout/stderr           │             │
│               │ Tran CSV / plot               │             │
└───────────────┴───────────────────────────────┴─────────────┘
```

### Colonna sinistra: run selector

La colonna sinistra serve a scegliere quale run guardare:

```text
Base run
Scenario 1
Scenario 2
Scenario N
```

Nella prima versione ci sara solo `Base run`. La sidebar va comunque disegnata
subito, cosi l'aggiunta degli scenari sara naturale.

Ogni run dovrebbe mostrare uno stato sintetico:

```text
success
warning
failed
not run
```

La sidebar potra diventare richiudibile piu avanti.

### Parte centrale: evidence panel

La parte centrale contiene gli artefatti tecnici. Non devono essere tutti aperti
di default, altrimenti la vista diventa sporca.

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
```

Di default conviene tenere aperti solo:

```text
SPICE Run Summary
SPICE Netlist
stderr, se non e vuoto
Transient Plot, se esiste
```

Gli altri file restano disponibili ma chiusi.

### Colonna destra: diagnostic chat

La chat deve restare visibile anche quando l'utente cambia run nella sidebar.

Prima versione:

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
il pannello centrale mostra anche l'immagine originale del circuito
```

Quindi, al momento, `09_web_chat.py` e:

```text
visualizzazione output pipeline + chat agente read-only
```

La chat salva file separati per non sovrascrivere gli esperimenti:

```text
11_agent_input_preview_chat.md
11_agent_prompt_chat.md
11_agent_response_chat.md
```

Stato scenari dalla chat:

```text
utente scrive "esegui scenario 1"
-> 09 riconosce la scelta
-> 09 estrae il JSON scenario dall'ultima risposta agente
-> 09 crea scenarios/scenario_1/
-> 09 salva scenario.json e scenario_status.json
-> 09 copia la base run in base_snapshot/ e run/
-> 09 chiama 12_controlled_scenarios.py
-> 12 applica le azioni supportate solo alla netlist in run/
```

Per ora la chat non esegue automaticamente ngspice sullo scenario. Lo step 12
puo pero farlo da terminale con `--run-spice`.

### Controlli chat futuri

La chat dovra avere controlli minimi ma chiari:

```text
model selector
image enable button / command
send message
```

Il selettore modello deve permettere all'utente di scegliere quale modello usare
per la risposta dell'agente.

Modello default previsto:

```text
gpt-5.4
```

Altri modelli potranno essere disponibili come opzione, ma senza rifare per ora
tutta la griglia sperimentale.

La gestione immagine deve seguire la policy gia decisa:

```text
default = immagine non inclusa
se l'agente la richiede = l'utente puo abilitarla
```

Interazione futura possibile:

```text
Agente:
Per questa diagnosi potrebbe servire l'immagine originale.

Utente:
usa immagine

Sistema:
la prossima chiamata agente include l'immagine disponibile in data/<batch>/<circuit>.
```

Nella UI questo puo essere supportato anche da un tasto:

```text
Use image in next agent call
```

Il tasto non deve caricare sempre l'immagine. Deve solo abilitarla quando serve,
in modo da mantenere la modalita base `graph-grounded`.

Versione successiva:

```text
utente scrive "esegui scenario 1"
-> 09 interpreta la scelta
-> 09 chiama 12
-> scenario compare nella sidebar
-> agente confronta Base run e Scenario run
```

### Termini tecnici usati nel sito

```text
Base run       = esecuzione principale prodotta dagli step 01-08
Scenario run   = esecuzione derivata da uno scenario scelto dall'utente
Artifact       = file prodotto dalla pipeline
Evidence panel = pannello centrale con graph, values, netlist e risultati
Diagnostic chat = chat con l'agente
SPICE status   = stato dell'esecuzione ngspice
```

## Comandi possibili

Uso separato:

```powershell
python scripts\pipeline_2.0\json_to_spice\09_web_chat.py --batch batchA --circuit a10
```

Uso futuro integrato nella pipeline:

```powershell
python scripts\pipeline_2.0\run_pipeline2.py --batch batchA --circuits a10 --run-spice --open-web
```

La seconda forma e comoda, ma conviene implementarla solo dopo aver testato bene
`09_web_chat.py` come script separato.

## Nota sul backend

Tecnicamente una pagina web che chiama Python, OpenAI, 10, 11 e in futuro 12 ha
bisogno di un piccolo server locale.

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

## TODO operativo

Questa e la scaletta da implementare nelle prossime iterazioni.

### TODO 1 - Collegare la chat a 10 e 11

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

Per non sovrascrivere gli esperimenti gia fatti, la risposta prodotta dalla chat
dovrebbe andare in un file dedicato:

```text
11_agent_response_chat.md
```

In questo modo gli output usati per la valutazione del Batch A restano
separati.

Stato:

```text
implementato nella forma minima con modello fisso gpt-5.4.
```

### TODO 2 - Mostrare cosa viene eseguito

Durante lo sviluppo, la chat dovrebbe mostrare o salvare un piccolo log tecnico:

```text
Executed:
- 10_build_diagnostic_context.py
- 11_agent_readonly.py --run-agent --model gpt-5.4

Output:
- 10_diagnostic_context.json
- 11_agent_response_chat.md
```

Questo serve a validare insieme che il sito stia davvero chiamando gli step
giusti.

### TODO 3 - Scelta modello

Aggiungere nella chat un selettore modello.

Default:

```text
gpt-5.4
```

Il modello scelto deve essere passato a `11_agent_readonly.py`.

### TODO 4 - Immagine su richiesta

Non includere l'immagine di default.

Quando l'agente la richiede o l'utente scrive un comando tipo:

```text
usa immagine
```

la chat deve abilitare una futura chiamata image-assisted.

Per ora basta ricordare la logica; l'implementazione concreta verra fatta piu
avanti.

### TODO 5 - Parsing scelta scenario

Dopo che l'agente propone scenari, l'utente puo scrivere:

```text
esegui scenario 1
prova lo scenario 2
facciamo il terzo
```

La chat deve riconoscere la scelta e recuperare il JSON tecnico dello scenario
proposto nella risposta precedente.

Prima versione semplice:

```text
"scenario 1" / "primo"  -> scenario_1
"scenario 2" / "secondo" -> scenario_2
"scenario 3" / "terzo"   -> scenario_3
```

Stato:

```text
implementato nella web chat per richieste semplici.
```

### TODO 6 - Collegare 12 controlled scenarios

Quando l'utente sceglie uno scenario:

```text
09 passa lo scenario a 12_controlled_scenarios.py
-> 12 crea una cartella scenario separata
-> 12 copia gli output originali
-> 12 modifica solo le copie
-> 12 rigenera gli step necessari
-> 12 riesegue ngspice
-> 12 salva risultato scenario
```

Gli output originali non devono mai essere sovrascritti.

Stato:

```text
implementato parzialmente.

09:
- crea cartella scenario;
- salva scenario.json;
- copia base_snapshot/ e run/;
- chiama 12.

12:
- supporta drive_node_voltage;
- supporta change_source_value su sorgenti SPICE esistenti;
- supporta close_switch su switch gia riconosciuti;
- modifica solo run/07_netlist.cir;
- salva 12_controlled_scenarios.json;
- puo eseguire ngspice con --run-spice;
- crea scenario_comparison.json dopo SPICE.
```

Esempio attuale `a01/scenario_1`:

```text
azione:
drive_node_voltage N002 5V

netlist scenario:
VSCENARIO_N002 N002 0 DC 5

confronto:
v(N002):       0 -> 5
v(N004):       0 -> 0.2380952
i(Rlamp13_1):  0 -> 0.0047619
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

Questo e il comportamento finale desiderato:

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

Estensione futura importante:

```text
modalita manuale:
utente sceglie esplicitamente "esegui scenario 1"

modalita semi-automatica:
utente autorizza "prova gli scenari finche trovi una soluzione"
```

Nella modalita semi-automatica l'agente/controller non deve fermarsi al primo
scenario proposto. Deve poter eseguire piu scenari in sequenza:

```text
1. esegue scenario 1;
2. confronta base run e scenario 1;
3. valuta se il sintomo sembra risolto;
4. se non e risolto, sceglie/prova scenario 2;
5. ripete il ciclo finche trova una spiegazione convincente o raggiunge un limite.
```

Esempio:

```text
problema utente:
"la lampada non si accende"

scenario 1:
alimentare il nodo di ingresso della lampada

risultato:
la lampada riceve corrente -> problema probabilmente risolto

oppure:
la lampada resta senza corrente -> provare scenario 2
```

Regole di sicurezza:

```text
- nessuno scenario deve modificare la base run originale;
- ogni scenario deve creare una nuova cartella separata;
- il numero massimo di scenari automatici deve essere limitato;
- ogni scenario deve salvare cosa ha cambiato e da quale step e ripartito;
- l'agente deve spiegare perche passa allo scenario successivo;
- se i risultati sono ambigui, deve fermarsi e chiedere conferma all'utente;
- se serve correggere il graph, deve dichiararlo esplicitamente.
```

Possibile limite iniziale:

```text
max_auto_scenarios = 3
```

Questa modalita non sostituisce la scelta utente. La prima versione resta
manuale, perche e piu semplice da validare. Dopo aver validato `12`, potremo
aggiungere il ciclo semi-automatico.

### TODO 8 - Animated SPICE Viewer

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
+ puntini/indicatori animati sui rami attraversati da corrente
```

La finalita non e sostituire ngspice. ngspice resta il motore di simulazione.
Il viewer serve solo a rendere visibile il risultato della simulazione.

Esempio su `a01`:

```text
ramo LED       -> animato, perche passa corrente
ramo lampada   -> spento/grigio, perche la corrente e zero
N001           -> evidenziato come nodo alimentato
N004           -> evidenziato come nodo a 0 V
switch aperto  -> mostrato come ramo non conduttivo
```

## Dati necessari per il viewer

Le coordinate geometriche non sono nel `01_graph.json` usato da Pipeline 2.0.
Sono pero disponibili negli output intermedi della Pipeline 1.0, ad esempio:

```text
outputs/pipeline1.0/batchA/03_estimate_terminals/a01.json
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

## Versione minima proposta

Prima versione semplice:

```text
1. mostrare l'immagine originale nel pannello centrale;
2. disegnare un canvas trasparente sopra l'immagine;
3. disegnare box o marker sui componenti riconosciuti;
4. associare ogni terminale al nodo SPICE tramite 03_node_map.json;
5. colorare i terminali/nodi in base alla tensione;
6. animare puntini tra i terminali dei componenti con corrente non nulla;
7. lasciare grigi i componenti con corrente zero;
8. mostrare tooltip o label con V/I principali.
```

Questa versione non richiede ancora di ricostruire perfettamente tutti i fili
disegnati nell'immagine. L'animazione puo partire dai componenti:

```text
resistenza: puntini tra t1 e t2
lampada: puntini tra t1 e t2 se i != 0
LED: puntini tra anodo e catodo se i != 0
sorgente: marker di alimentazione
switch aperto: nessuna animazione
```

## Versione successiva

Dopo la versione minima:

```text
- disegnare collegamenti approssimati tra terminali dello stesso nodo;
- animare anche i tratti di collegamento, non solo i componenti;
- modulare velocita/spessore/colore in base alla corrente;
- supportare anche risultati transienti da 08_tran.csv;
- permettere il confronto visuale Base run vs Scenario run;
- aggiornare la visualizzazione quando l'utente seleziona uno scenario nella sidebar.
```

## Regola di priorita

Questo viewer non deve bloccare il lavoro sugli scenari.

Ordine consigliato:

```text
1. completare scelta scenario dalla chat;                    fatto per casi semplici
2. implementare 12_controlled_scenarios.py;                  fatto per drive_node_voltage e change_source_value
3. rieseguire ngspice su scenario separato;                  fatto da terminale con --run-spice
4. creare confronto base run vs scenario run;                fatto con scenario_comparison.json
5. far commentare il confronto all'agente in chat;           prossimo step
6. solo dopo aggiungere Animated SPICE Viewer.
```
