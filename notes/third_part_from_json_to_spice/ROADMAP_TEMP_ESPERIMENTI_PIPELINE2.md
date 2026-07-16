# Roadmap temporanea esperimenti Pipeline 2.0

Questo file e una nota temporanea di lavoro.

Serve a tenere fisso il percorso deciso dopo la chiusura dell'Esperimento 1 sul
Batch A. I dettagli tecnici completi restano nei markdown principali:

```text
notes/third_part_from_json_to_spice/agente_diagnostico_pipeline2.md
scripts/pipeline_2.0/WEB_CHAT_TEMP_PLAN.md
experiment_ai/pipeline2_spice_analysis/batchA/
```

## Esperimento 1 - Batch A baseline

Stato: concluso.

Obiettivo:

- eseguire Pipeline 2.0 sul Batch A;
- arrivare fino a ngspice;
- collegare web chat e agente;
- proporre ed eseguire scenari controllati manuali;
- documentare ogni circuito `a01`-`a10`.

Risultato:

- `a01`-`a10` sono documentati;
- gli output SPICE sono stati analizzati;
- la web chat funziona come interfaccia locale;
- l'agente read-only propone scenari;
- lo step `12_controlled_scenarios.py` esegue scenari separati dalla base run;
- i markdown del Batch A sono il riferimento manuale del comportamento atteso.

## Esperimento 2 - Scenari piu potenti

Stato: sostanzialmente concluso sul Batch A.

Obiettivo:

ampliare le primitive scenario in modo che l'agente possa proporre modifiche
piu forti e piu utili alla netlist SPICE, senza modificare mai la base run
originale.

Idea principale:

```text
ogni scenario produce una netlist alternativa, eseguibile e confrontabile
```

Situazione reale raggiunta sul Batch A:

- la web chat experiment-aware e attiva;
- la chat history file-based di Experiment 2 e attiva;
- il registry scenari locale per circuito e attivo;
- le tre primitive candidate principali di questa fase sono tutte implementate
  nel runner;
- e stata anche validata una quarta primitiva strutturale, utile per casi di
  bias/accoppiamento analogico;
- i casi prioritari del Batch A per queste primitive sono gia stati coperti e
  documentati nei markdown `experiment2`.

In altre parole, Experiment 2 non e piu una fase di sola implementazione del
runner, ma una fase gia consolidata sul Batch A con primitive che cambiano in
modo controllato la netlist SPICE.

Possibili sviluppi:

- creare un piccolo file YAML o simile come catalogo delle primitive scenario;
- documentare per ogni primitiva:
  - nome;
  - descrizione;
  - parametri richiesti;
  - quando usarla;
  - come viene tradotta in netlist;
  - limiti e rischi;
- aggiungere primitive per modifiche piu strutturali.

Primitive gia presenti:

```text
drive_node_voltage
change_source_value
change_component_value
close_switch
```

Primitive forti validate in Esperimento 2:

```text
connect_nodes
feed_nodes_from_source_node
add_voltage_source_between_nodes
add_resistor_between_nodes
```

Queste tre primitive sono volutamente poche. L'obiettivo e aumentare la
capacita diagnostica senza far esplodere la complessita del runner.

### Primitive da implementare per prime

#### 1. connect_nodes

Collega due nodi gia esistenti con una resistenza molto piccola, come se nella
run scenario aggiungessimo un filo, un jumper, un ponte o un contatto chiuso.

Esempio:

```json
{
  "type": "connect_nodes",
  "from": "N002",
  "to": "N004",
  "resistance": "1m"
}
```

Serve per:

- `a02`: verificare se manca un percorso elettrico utile tra i nodi gia
  presenti;
- `a07`: eventualmente testare una continuita mancante tra ingresso e ramo;
- `a09`: combinare alimentazione e continuita nel ramo lampada;
- `a10`: testare collegamenti mancanti tra connector e rami finali.

Stato attuale della sottofase `connect_nodes`:

- implementata nel runner scenario;
- integrata nella web chat e nel prompt agente;
- validata su `a01`, `a02`, `a09`, `a10`;
- documentata nei markdown `experiment2` del Batch A;
- considerata sostanzialmente chiusa come prima primitiva di Esperimento 2.

#### 2. feed_nodes_from_source_node

Propaga una tensione da un nodo sorgente gia presente verso uno o piu nodi
target. Internamente puo essere implementata come una lista controllata di
`connect_nodes`.

Esempio:

```json
{
  "type": "feed_nodes_from_source_node",
  "source_node": "N002",
  "target_nodes": ["N003", "N004"],
  "resistance": "1m"
}
```

Serve per:

- `a01`: testare se il 5 V del pin 1 puo alimentare anche il ramo lampada sul
  pin 2;
- `a02`: testare se VCC deve propagarsi verso ramo resistivo o condensatore;
- `a09`: testare il mancato trasferimento della 9 V dal ramo batteria/fusibile
  verso LED e lampada;
- `a10`: dopo la chiusura dello switch, testare se l'alimentazione arrivata a
  valle deve essere trasferita verso `N003` e `N004`.

Stato attuale della sottofase `feed_nodes_from_source_node`:

- implementata nel runner scenario;
- integrata nella web chat e nel prompt agente;
- validata su `a01`, `a09`, `a10`;
- documentata nei markdown `experiment2` del Batch A;
- considerata sostanzialmente chiusa come seconda primitiva di Esperimento 2.

#### 3. add_voltage_source_between_nodes

Aggiunge una sorgente di tensione tra due nodi gia esistenti. E piu generale di
`drive_node_voltage`, perche non obbliga sempre a riferire la sorgente a massa.

Esempio:

```json
{
  "type": "add_voltage_source_between_nodes",
  "positive": "N001",
  "negative": "0",
  "value": "DC 5"
}
```

Serve per:

- `a02`: simulare una sorgente esterna tra pin del connector;
- `a05`: alimentare il ramo VMON in modo piu esplicito, se necessario;
- `a07`: aggiungere una vera sorgente PWR o VAC, dato che la netlist base non
  contiene eccitazione reale;
- `a09` e `a10`: provare alimentazioni esterne sui rami finali quando non si
  vuole usare una sorgente gia presente.

Stato attuale della sottofase `add_voltage_source_between_nodes`:

- implementata nel runner scenario;
- integrata nella web chat e nel prompt agente;
- validata su `a05`, `a07`;
- documentata nei markdown `experiment2` del Batch A;
- considerata sostanzialmente chiusa come terza primitiva forte di
  Esperimento 2 sul Batch A;
- da usare soprattutto quando la netlist base non contiene una vera sorgente
  utile o quando vogliamo simulare in modo esplicito una eccitazione esterna
  tra pin gia esistenti;
- concettualmente distinta da:
  - `connect_nodes`, che aggiunge continuita;
  - `feed_nodes_from_source_node`, che propaga una sorgente gia presente.

Priorita attuale sui circuiti del Batch A:

- casi gia chiusi e documentati per questa prima ondata:
  - `a01`: `connect_nodes` e `feed_nodes_from_source_node`;
  - `a02`: `connect_nodes`;
  - `a05`: `add_voltage_source_between_nodes`;
  - `a07`: `add_voltage_source_between_nodes`;
  - `a09`: `connect_nodes` e `feed_nodes_from_source_node`;
  - `a10`: `connect_nodes` e `feed_nodes_from_source_node`.
- casi non prioritari per nuove primitive topologiche in questa fase:
  - `a04`, `a06`, `a08`, perche sono casi gia eccitati e piu orientati a
    comportamento analogico, bias, guadagno o temporizzazione che a
    continuita/alimentazione mancante;
- caso escluso dalla fase semplice:
  - `a03`, perche richiede una successiva fase di graph correction o
    ragionamento image-assisted.

Conclusione operativa attuale:

- per il Batch A la triade

```text
connect_nodes
feed_nodes_from_source_node
add_voltage_source_between_nodes
```

  puo essere considerata sostanzialmente completata come famiglia di scenari
  che cambia in modo controllato la netlist SPICE;
- `add_resistor_between_nodes` e stata inoltre validata come estensione
  strutturale utile sul caso `a08`, dove la domanda diagnostica riguardava un
  accoppiamento resistivo troppo debole tra due nodi gia esistenti;
- `a04` e `a06` non sono stati forzati dentro Experiment 2 con primitive
  artificiali, perche sul Batch A risultano casi gia ben spiegati da scenari
  analogici/elettrici di Experiment 1;
- `a08` non appartiene alla prima ondata di continuita/alimentazione mancante,
  ma costituisce un caso separato e gia concluso di modifica strutturale utile
  sul bias/accoppiamento;
- `a03` resta separato come caso successivo di correzione topologica o
  image-assisted, non come estensione diretta di questa seconda ondata.

### Seconda ondata candidata di primitive topologiche

Stato: parzialmente esplorata; non necessaria per chiudere Experiment 2 sul
Batch A.

Obiettivo:

- aggiungere 1-2 primitive nuove che restino generali;
- evitare primitive cucite su un singolo circuito;
- coprire casi in cui la domanda diagnostica non e "manca alimentazione?" ma
  "questo ramo analogico conta davvero come sottorete strutturale?".

Le due primitive candidate attuali erano:

```text
add_resistor_between_nodes
open_component
```

#### 4. add_resistor_between_nodes

Aggiunge una nuova resistenza tra due nodi gia esistenti.

Questa primitiva va letta come estensione naturale di `connect_nodes`:

- `connect_nodes` = collegamento quasi ideale tra due nodi;
- `add_resistor_between_nodes` = aggiunta di un nuovo ramo resistivo con valore
  arbitrario.

Esempio:

```json
{
  "type": "add_resistor_between_nodes",
  "from": "N001",
  "to": "N004",
  "value": "33k"
}
```

Perche e utile:

- permette di aggiungere pull-up, pull-down, shunt o rami di bias
  supplementari;
- cambia davvero la topologia della netlist, non solo il valore di un
  componente gia esistente;
- resta riusabile su molti batch futuri, non solo sul Batch A.

Primo caso pilota effettivamente validato:

- `a08`: aggiunta di un ramo resistivo supplementare tra nodo trigger e ramo di
  pilotaggio base, per verificare se il pilotaggio cambia in modo strutturale.

Esito sul Batch A:

- implementata nel runner scenario;
- integrata nella web chat e nel prompt agente;
- validata e documentata su `a08`;
- considerata utile come estensione strutturale generale, ma non necessaria da
  forzare su `a04` o `a06`.

Nota metodologica:

- questa primitiva ha senso solo se aggiunge una domanda diagnostica nuova;
- non va usata per duplicare banalmente `change_component_value` con una forma
  piu complicata.

#### 5. open_component

Rende aperto un componente gia emesso nella netlist di scenario, escludendolo
dal circuito della scenario run.

Questa primitiva introduce una seconda famiglia topologica molto generale:

- aggiunta di ramo -> `add_resistor_between_nodes`;
- rimozione/isolamento di ramo -> `open_component`.

Esempio:

```json
{
  "type": "open_component",
  "target": "Ccapacitor4_2"
}
```

Perche e utile:

- permette di isolare condensatori di coupling, condensatori di bypass, rami di
  feedback o elementi sospetti senza toccare la base run;
- cambia la struttura del circuito in modo leggibile e forte;
- e una primitiva generale, utile anche su futuri casi analogici.

Primi casi pilota candidati:

- `a06`: aprire `Ccapacitor4_2` (`CE`) per verificare quanto il bypass di
  emettitore pesi davvero nel comportamento osservato;
- `a08`: aprire `Ccapacitor4_1` (`C1`) per testare se il ramo RC e
  strutturalmente decisivo o solo una leva tra le altre.

Nota metodologica:

- questa primitiva e interessante solo quando l'isolamento di un ramo apre una
  distinzione diagnostica reale;
- non va usata come scenario distruttivo generico senza una ipotesi precisa.

Priorita attuale della seconda ondata:

- `add_resistor_between_nodes` e ormai da considerare gia implementata e
  validata su `a08`;
- `open_component` resta la prossima primitiva candidata solo se un batch
  futuro o un caso piu complesso formuleranno una domanda diagnostica nuova e
  davvero utile;
- non forzare `open_component` su `a04` o `a06` solo per estendere
  artificialmente Experiment 2;
- non riaprire il Batch A finche non emergera una motivazione sperimentale piu
  forte o un nuovo insieme di circuiti piu adatto.

Decisione metodologica attuale:

- non introdurre per ora una primitiva separata `add_current_source`;
- non introdurre per ora una primitiva separata `signal_source`;
- se servira una sorgente temporale, la stessa
  `add_voltage_source_between_nodes` potra accettare valori come:

```text
DC 5
SIN(0 5 50)
PULSE(0 5 0 1ms 1ms 50ms 100ms)
```

In questo modo manteniamo il runner semplice e generale:

- una primitiva per aggiungere una eccitazione esterna;
- valore SPICE abbastanza flessibile da coprire DC e forme d'onda;
- eventuali alias semantici futuri demandati al prompt o al catalogo
  descrittivo, non al moltiplicarsi delle primitive eseguibili.

### Casi esclusi o non prioritari per ora

`a03` resta fuori dall'Esperimento 2 iniziale.

Motivo:

- e un caso speciale con graph/topologia fortemente sbagliati;
- richiede ragionamento image-assisted piu profondo;
- include batteria letta come due batterie, rele, bobina/contatto e ramo AC;
- rischia di far crescere troppo la complessita prima di consolidare le
  primitive semplici.

`a03` verra ripreso in una fase successiva dedicata alla correzione del graph o
alla ricostruzione guidata dall'immagine.

`a04` e `a06` non vengono invece marcati come "fallimenti" di Experiment 2:

- sono casi gia ben spiegati dai risultati di Experiment 1;
- sul Batch A non hanno espresso una necessita forte di nuove primitive
  topologiche generali;
- restano quindi validi come esempi di circuiti per cui Experiment 1 basta gia
  a localizzare o spiegare il problema.

### Chat history dell'Esperimento 2

Per l'Esperimento 1 non serve recuperare la chat grezza, perche i report
`experiment1/a01.md`-`experiment1/a10.md` contengono gia domande, risposte,
scenari, risultati e conclusioni.

Per l'Esperimento 2, invece, vogliamo ripartire da conversazioni pulite e
salvare direttamente ogni interazione.

Scelta attuale:

```text
opzione 2 = file locali per circuito
```

Non usiamo ancora un database vero. Per ora salviamo file locali tracciabili,
semplici da leggere e facili da trasformare in markdown, CSV o JSON aggregati.

Struttura proposta:

```text
outputs/pipeline2.0/<batch>/experiment2/<circuit>/experiment2_chat/
  chat_history.json
  chat_history.md
  scenario_registry.json
  scenario_registry.md
```

Contenuto minimo di `chat_history.json`:

```text
turn_id
timestamp
role: user | assistant | system
content
model
selected_run
used_image
generated_files
scenario_id
scenario_outcome
scenario_path
```

Regole:

- ogni domanda utente viene salvata;
- ogni risposta agente viene salvata;
- ogni scenario eseguito viene salvato come evento `system`;
- la chat history e separata dagli output originali della base run;
- la base run continua a non essere modificata;
- in futuro questi file potranno essere letti da uno script di valutazione per
  produrre CSV, metriche e grafici.

### Scenario registry dell'Esperimento 2

Oltre alla chat history, Esperimento 2 salva un registro scenari locale per
circuito:

```text
scenario_registry.json
scenario_registry.md
```

Il registry non e un database esterno. E un file locale che rende esplicita la
lista degli scenari proposti ed eseguiti durante la conversazione.

Regola user-friendly:

```text
Scenario 1
Scenario 2
Scenario 3
Scenario 4
Scenario 5
```

La numerazione e globale per circuito. I primi scenari vengono registrati dopo
la prima risposta dell'agente; eventuali scenari successivi, anche combinati o
proposti dopo aver letto i risultati, vengono accodati come `Scenario 4` e
`Scenario 5`.

Semantica dei comandi:

```text
"scenario 1", "il primo"   -> Scenario 1 globale
"scenario 2", "il secondo" -> Scenario 2 globale
"scenario 4", "il quarto"  -> Scenario 4 globale
"l'ultimo", "quest'ultimo", "quello appena proposto"
                            -> ultimo scenario aggiunto al registry
```

Comandi di consultazione:

```text
mostra scenari
mostrami gli scenari
quali scenari restano?
riepilogo scenari
```

Regole operative:

- massimo 5 scenari SPICE eseguiti per circuito;
- il limite vale sulle run scenario realmente create/eseguite, non sul numero
  di proposte presenti nella risposta agente o nel registry;
- le proposte non eseguite restano disponibili;
- il registry viene sincronizzato con le cartelle scenario gia presenti su
  disco quando si chiede la lista o si esegue uno scenario;
- gli scenari non eseguibili, per esempio verifiche topologiche senza azioni,
  possono essere conservati come proposta diagnostica ma non devono modificare
  la base run.
- dopo scenari gia eseguiti, ogni nuovo scenario proposto deve essere
  self-contained e ripartire dalla base run;
- se il nuovo scenario dipende da una condizione abilitante gia dimostrata,
  per esempio uno switch chiuso, quella azione va reinserita nello stesso
  JSON del nuovo scenario;
- non bisogna combinare automaticamente tutti gli scenari precedenti, ma solo
  le azioni realmente necessarie alla nuova ipotesi.

Regola `Clear` per Esperimento 2:

```text
Clear = reset della sessione interattiva del circuito
```

Il reset non tocca gli output base 01-08 copiati nell'esperimento. Cancella o
azzera invece:

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

In questo modo si puo ripartire puliti con nuovi scenari, senza dover
rigenerare la parte tecnica fino a SPICE.

Esempi di scenari desiderati nel perimetro iniziale:

- chiudere uno switch e alimentare i pin collegati del connector;
- propagare la tensione di un nodo sorgente verso piu nodi target;
- aggiungere una sorgente di tensione tra due nodi gia presenti;
- collegare due nodi solo nella run scenario;
- distinguere se un carico e guasto oppure se semplicemente non riceve
  alimentazione nella netlist base.

Regola fondamentale:

```text
la base run non si modifica mai
```

Ogni scenario deve creare:

```text
scenarios/<scenario_id>/base_snapshot/
scenarios/<scenario_id>/run/
scenarios/<scenario_id>/scenario.json
scenarios/<scenario_id>/12_controlled_scenarios.json
scenarios/<scenario_id>/scenario_comparison.json
```

## Esperimento 3 - Viewer / simulatore visuale

Stato: concluso sul Batch A, con `a03` escluso dalla prima fase per il suo
caso topologico/SPICE non stabile.

Obiettivo:

creare una visualizzazione stile simulatore, ispirata a Falstad ma senza usarlo
come motore, basata sugli output Pipeline 1.0 / Pipeline 2.0 e su ngspice.

Regola centrale:

```text
il viewer parte dalla netlist della run selezionata
```

Questo e importante perche:

- la base run ha una netlist;
- ogni scenario puo avere una netlist diversa;
- se uno scenario cambia topologia, anche il circuito visualizzato cambia;
- quindi il viewer non deve assumere una sola topologia fissa.

Risultato realizzato:

```text
13_build_viewer_model.py  -> contratto elettrico e strutturale della run
14_build_viewer_layout.py -> layout image-guided e routing generale
15_render_viewer_svg.py   -> SVG interattivo con vocabolario componenti
09_web_chat.py            -> carica/genera il viewer della run selezionata
```

Il viewer usa:

- `07_netlist.cir` come verita elettrica;
- `03_node_map.json` e `06_component_rules.json` per elementi strutturali;
- bbox, terminali e orientamenti della Pipeline 1.0 come geometry seed;
- output OP/TRAN ngspice per tensioni, correnti, animazioni e scope transienti.

Copertura Batch A:

- base run e run scenario di `a01`, `a02`, `a04`-`a10`;
- varianti topologiche `connect_nodes`, `feed_nodes_from_source_node`,
  `add_voltage_source_between_nodes` e `add_resistor_between_nodes`;
- switch aperti/chiusi, componenti aggiunti e modifiche di sorgenti/valori;
- zoom, pan, routing ortogonale e piccoli ponti per attraversamenti senza
  giunzione elettrica.

Il viewer non ricostruisce lo schema pixel-perfect: mantiene un circuito
equivalente leggibile, generale e coerente con la netlist simulata.

## Esperimento 3.1 - Validazione end-to-end agente e viewer

Stato: concluso sul Batch A.

Obiettivo raggiunto:

ripartire da workspace puliti per ogni circuito, chiedere la diagnosi
all'agente, far proporre scenari nuovi ed eseguirli dalla web chat, verificando
che ogni run scenario generi automaticamente il proprio viewer.

Flusso da validare:

```text
base run pulita
-> sintomo utente
-> agente propone scenario.json
-> utente conferma "esegui scenario ..."
-> 12_controlled_scenarios.py crea e simula la run
-> 09_web_chat.py genera 13/14/15 sulla run scenario
-> sidebar e pannello centrale mostrano il nuovo viewer
-> agente interpreta scenario_comparison.json
```

Esito:

- validati `a01`, `a02`, `a04`-`a10`; `a03` resta escluso per il noto limite
  topologico/SPICE;
- eseguite 18 run scenario, tutte con viewer della run effettivamente simulata;
- verificate proposte agente, scenario registry, esecuzione controllata,
  confronto base/scenario, sidebar e risposta successiva dell'agente;
- verificati scenari non topologici e topologici, inclusi switch chiusi,
  continuita, feed di nodi, sorgenti e resistenze aggiunte;
- le correzioni emerse dal viewer sono rimaste regole generali di layout e
  rendering, senza eccezioni legate a un singolo circuito.

Sessione interattiva:

- `experiment3_1` e abilitato nella web chat con history e scenario registry;
- i file della nuova sessione vivono in `experiment_chat/`, mentre le root
  `experiment2*` mantengono la cartella storica `experiment2_chat/`;
- base run e struttura dei file restano immutabili fino all'esecuzione di uno
  scenario confermato dall'utente.

## Esperimento 4 - Automazione agentica

Stato: implementata e validata in una prima passata OpenAI su `a01`, `a02`
e `a04`-`a10`; `a03` resta escluso per il noto limite topologico/SPICE.

Obiettivo:

confrontare il flusso guidato attuale con un agente che propone, esegue e
confronta scenari in autonomia controllata, fino a una conclusione o al limite
di 5 scenari.

### Due modalita separate

La stessa web app deve offrire due modalita selezionabili:

- `CHAT`: flusso guidato gia validato, con conferma umana prima dello scenario;
- `AGENT`: ciclo autonomo, con massimo due scenari indipendenti per decisione.

Le due modalita non condividono chat, registry, scenari, run selezionata o stato
diagnostico. Condividono soltanto la stessa base tecnica iniziale `01-08`.

Struttura prevista:

```text
outputs/pipeline2.0/batchA/experiment4/
|-- chat/<circuit>/
`-- agent/<circuit>/
```

Ogni workspace mantiene base run, viewer, `experiment_chat/` e `scenarios/`
indipendenti. La pagina cambia interamente contesto quando si passa da `CHAT`
a `AGENT`.

### Ciclo autonomo

Flusso implementato:

```text
sintomo utente
-> agente sceglie stop oppure uno/due scenari
-> pipeline valida scenario e budget
-> runner condiviso crea ed esegue la run
-> 13/14/15 generano il viewer della run
-> agente legge contesto e scenario_comparison.json aggiornati
-> agente decide stop oppure iterazione successiva
-> massimo 5 run scenario realmente eseguite
-> conclusione finale
```

Il browser deve richiedere una iterazione alla volta, mostrare l'avanzamento e
permettere l'arresto manuale. Lo stato persistente e
`experiment_chat/autonomous_diagnosis.json`.

La presentazione `AGENT` e ora distinta dalle bolle della modalita `CHAT`:

- riepilogo di run, scenari e decisioni;
- piano derivato dallo stato reale del controller;
- timeline di ipotesi, primitive, esito SPICE ed evidenze;
- riconoscimento uniforme di confronti OP e TRAN;
- collegamenti a viewer e grafici nella run centrale;
- conclusione separata in causa, correzione verificata e prove disponibili.

Questa vista e costruita da `autonomous_agent/presentation.py` usando gli
artefatti della sessione e non contiene regole specifiche per Batch A.

Decisioni strutturate dell'agente:

```json
{"decision":"run_scenarios","reason":"...","scenarios":[{}]}
{"decision":"stop","final_status":"resolved|localized|partially_localized|topology_issue|inconclusive","reason":"...","final_answer":"...","final_cause":"...","verified_correction":"..."}
```

`resolved_candidate` prodotto dallo step 12 resta un esito tecnico del
confronto: non basta da solo a dichiarare risolto il sintomo dell'utente.

### Regole e arresto

- l'agente non modifica direttamente netlist o output;
- ogni proposta passa dalla validazione della pipeline;
- base run e workspace dell'altra modalita restano immutati;
- scenari duplicati o non validi non consumano il budget;
- il budget conta soltanto run con SPICE realmente eseguito;
- il ciclo termina per conclusione sufficiente, budget esaurito, assenza di
  scenari validi, errore non recuperabile o arresto utente;
- una conclusione deve distinguere `resolved` da `localized`.

`09`, `10` e `12` contano ora in modo coerente soltanto gli scenari realmente
eseguiti.

### Primitive autonome

Primitive operative abilitate:

- `close_switch`;
- `connect_nodes`;
- `drive_node_voltage`;
- `change_component_value`;
- `change_source_value`;
- `feed_nodes_from_source_node`;
- `add_voltage_source_between_nodes`;
- `add_resistor_between_nodes`.

L'agente deve preferire modifiche minime su componenti e collegamenti
esistenti. Nuove sorgenti o nuovi rami resistivi sono ammessi solo quando
l'ipotesi e sostenuta dagli output tecnici della run corrente.

`feed_nodes_from_source_node` va usata quando un nodo e gia misurato come
alimentato e deve alimentare altri rami. `connect_nodes` resta il test di una
continuita generica. Le due primitive non possono descrivere la stessa
relazione nella stessa decisione. `add_resistor_between_nodes` resta distinta,
perche rappresenta un accoppiamento resistivo con valore significativo.

Per obiettivi che richiedono di attivare, spegnere o mantenere attivo un
componente, ogni scenario deve confrontare anche una misura diretta del
componente tramite il nome emesso in `07_netlist.cir`, per esempio
`i(Rlamp13_1)` o `i(Dled12_1)`. Le tensioni dei nodi restano utili per
localizzare la causa, ma da sole non dimostrano lo stato del componente.

Le decisioni autonome dichiarano inoltre un oggetto `expect` che assegna a
ogni misura decisiva il comportamento atteso, per esempio `activated` per il
carico da accendere e `unchanged` per il LED da preservare. Il comparatore usa
questi criteri per distinguere una correzione verificata da una variazione
generica. Gli scenari precedenti senza `expect` restano compatibili.

Ogni nuovo scenario AGENT dichiara anche `intent: correction | diagnostic`.
Una modifica che mira direttamente al sintomo deve essere una `correction`.
Un test `diagnostic` puo confermare la causa, ma non basta a chiudere un
obiettivo che richiede esplicitamente una riparazione: con budget residuo
l'agente deve cercare una correzione verificata. Se un test iniziale dichiara
esplicitamente i criteri dell'obiettivo e li soddisfa, il runtime lo promuove
senza ripetere la stessa azione come scenario duplicato.
`unchanged` e ammesso solo quando il sintomo chiede esplicitamente di
preservare un comportamento. In `tran`, correnti e potenze senza traccia CSV
restano osservazioni OP, oppure diventano criteri `expect` se la mappa
opzionale `measure` le seleziona esplicitamente come `op`. La stessa mappa
permette di verificare nello scenario una tensione `tran_vpp` insieme a
grandezze DC. Gli obiettivi AC/VAC richiedono almeno una misura `tran_vpp`.
Gli obiettivi sullo stato di LED o lampade richiedono inoltre una corrente o
potenza diretta tra i criteri di successo della correzione.
Quando lo stesso sintomo combina AC/VAC e LED/lampada, ogni test verifica
insieme i due obiettivi con una misura mista `tran_vpp` + `op`.
Una correzione richiede inoltre almeno un miglioramento relativo del 10% o
una vera attivazione/disattivazione. Per sintomi di amplificazione, gli
scenari correttivi dichiarano ingresso e uscita nel blocco `gain`, e il
confronto salva il rapporto `Vpp(output) / Vpp(input)`.

Per lampeggio, periodicita, regolarita, duty cycle o durata di accensione, lo
scenario `tran` dichiara anche `temporal_expect`. Il runtime confronta i
profili del viewer della base e della scenario run: stato del componente,
periodicita e soglie di duty cycle. Un miglioramento elettrico che perde una
periodicita richiesta resta parziale e non puo produrre `resolved_candidate`.

Limite noto: non sono ancora supportate sequenze temporali tra componenti,
per esempio "LED acceso prima, poi lampada lampeggiante", quando la base run
ha solo `.op`. Serviranno una `.tran` aggiungibile dallo scenario, profili
temporali per lampade e un criterio di ordine tra profili.

### Implementazione essenziale

1. preparare `experiment4/chat/` e `experiment4/agent/` dalla stessa base
   `experiment3_1`, senza scenari pre-caricati;
2. estrarre da `09_web_chat.py` un runtime scenario condiviso dal flusso
   guidato e da quello autonomo;
3. correggere e centralizzare conteggio budget, validazione e firma duplicati;
4. aggiungere controller e stato persistente del ciclo autonomo;
5. usare il selettore `CHAT` / `AGENT` gia collegato ai due workspace;
6. validare `a01`, `a02`, `a04`-`a10` con stesso sintomo, modello e budget
   nelle due modalita; completato nella prima passata Batch A;
7. aggiungere solo dopo il ciclo base il parser dei comandi diretti, riusando lo
   stesso runtime.

Script/moduli implementati:

```text
scenario_runtime.py
scenario_expectations.py
transient_signal_quality.py
16_autonomous_diagnosis.py
autonomous_agent/
autonomous_agent/presentation.py
```

Guardrail implementati:

- massimo 2 scenari per decisione, entrambi dalla base run;
- esecuzione sequenziale per evitare concorrenza ngspice inutile;
- massimo 5 run scenario e massimo 8 decisioni agentiche;
- un solo retry per JSON malformato;
- whitelist rigida delle otto primitive gia implementate e validate dal
  runner controllato;
- firma duplicati, stop manuale e persistenza file-based;
- le decisioni aggiuntive lasciano due tentativi di recupero per proposte
  rifiutate senza aumentare il budget delle simulazioni SPICE;
- gli scenari AGENT distinguono obbligatoriamente `op` e `tran`; per sintomi
  dinamici il confronto usa il Vpp delle tracce CSV e non il valore DC `.op`;
- gli scenari misti possono scegliere `op` o `tran_vpp` per singola grandezza
  tramite `measure`, senza separare artificialmente rami DC e uscite AC;
- pin distinti dello stesso connector non vengono uniti senza un'evidenza
  topologica esplicita negli artefatti;
- il viewer distingue automaticamente sorgenti DC e forme `SIN`/`PULSE`, e i
  meter AC ricavano attivita e lettura Vpp dalle tracce transitorie;
- gli scenari distinguono obbligatoriamente test `diagnostic` e modifiche
  `correction`; una richiesta esplicita di correzione non puo chiudere come
  sola localizzazione finche resta budget;
- i sintomi temporali richiedono `temporal_expect`; stato, periodicita e duty
  cycle del profilo viewer devono soddisfare le soglie dichiarate prima dello
  stop risolutivo;
- `final_status=resolved` richiede una `verified_correction` non vuota;
- una causa confermata puo terminare come `localized` senza forzare una
  correzione topologica non sostenuta dagli artefatti;
- una variazione inferiore al 10% resta evidenza utile ma non arresta il ciclo;
- le correzioni di guadagno confrontano esplicitamente ingresso e uscita;
- per sorgenti SIN, i sintomi di distorsione usano la THD sulle armoniche
  2-5 nelle ultime tre oscillazioni complete;
- una correzione della distorsione richiede almeno il 20% di riduzione della
  THD, THD finale non superiore al 10% e guadagno fondamentale preservato;
- forme d'onda non supportate restano parziali e non producono stop automatico;
- nessun database.

### Valutazione Experiment 4

Per ogni prova vanno salvati almeno:

```text
interaction_mode: chat | agent
model
symptom
executed_scenario_count
scenario_primitives
stop_reason
final_diagnosis_category
human_notes
```

Il confronto tra le due modalita deve usare lo stesso circuito, sintomo,
modello e budget.

## Esperimento 5 - Generalizzazione sul Batch B

Stato: pianificato; da avviare dopo la chiusura documentale di Experiment 4.

Obiettivo: verificare che pipeline, viewer, scenari controllati e modalita
`CHAT` / `AGENT` funzionino su circuiti non usati per progettare le regole del
Batch A.

Protocollo essenziale:

1. preparare per ogni circuito del Batch B la base run fino a `01-08` e il
   viewer della base;
2. studiare immagini, Graph JSON, node map, regole componenti, netlist e
   risultati SPICE prima di modificare il codice;
3. riusare inizialmente le otto primitive scenario gia disponibili e validare
   prima il flusso `CHAT`;
4. aggiungere una nuova primitiva soltanto se un limite compare in piu casi e
   puo essere espresso come operazione generale sulla netlist;
5. ripetere sugli stessi sintomi il flusso `AGENT`, confrontando numero di
   run, decisioni, esito SPICE, viewer e conclusione;
6. registrare gli esiti nella griglia di valutazione comune Batch A vs Batch B.

Regole metodologiche:

- non ricostruire il viewer per singolo circuito: si riusano `13-15` e il loro
  vocabolario componenti, intervenendo solo su lacune generali;
- non introdurre scenari cuciti su un solo schema; una nuova azione deve avere
  semantica netlist chiara, validazione, confronto e rappresentazione viewer;
- `a03` non definisce una regola per Batch B: eventuali problemi Graph/immagine
  vanno classificati separatamente da un problema delle primitive scenario;
- le sequenze temporali tra componenti restano fuori dal primo giro Batch B
  finche non verra progettata l'estensione `.tran` dedicata.

## Valutazione trasversale degli esperimenti

Questa parte va ripresa quando avremo completato piu esperimenti.

Idea:

```text
usare una griglia comune di valutazione per tutti gli esperimenti
```

In questo modo possiamo confrontare Esperimento 1, 2, 3 e 4 in modo numerico,
non solo descrittivo.

### Perche serve

Senza metriche comuni rischiamo di avere solo tanti markdown qualitativi.

Con metriche comuni possiamo invece mostrare:

- se l'agente migliora davvero passando da scenari semplici a scenari piu
  potenti;
- se l'automazione aiuta o peggiora;
- quanti casi restano bloccati per problemi topologici;
- quanti scenari servono mediamente per arrivare a una conclusione;
- quali primitive scenario sono piu utili;
- quanto il viewer aiuta nella lettura dei risultati, quando verra introdotto.

### Griglia minima per ogni circuito

Per ogni circuito e per ogni esperimento dovremmo salvare almeno:

```text
batch
circuit_id
experiment_id
base_spice_status
base_spice_warning_count
graph_issue_detected
image_used_by_agent
agent_initial_diagnosis_quality
scenario_count
scenario_types_used
best_scenario_id
best_scenario_outcome
final_diagnosis_category
final_diagnosis_quality
human_notes
```

Possibili categorie per `final_diagnosis_category`:

```text
resolved
localized
partially_localized
topology_issue
not_enough_information
inconclusive
```

Possibili valori per `final_diagnosis_quality`:

```text
correct
mostly_correct
partially_correct
wrong
not_applicable
```

### Metriche aggregate possibili

Da questa griglia potremo calcolare:

- percentuale di circuiti SPICE success/fail;
- percentuale di diagnosi corrette o parzialmente corrette;
- percentuale di casi risolti, localizzati o inconclusivi;
- numero medio di scenari per circuito;
- numero di casi che richiedono immagine;
- distribuzione delle primitive scenario usate;
- confronto tra Esperimento 1, 2 e 3;
- casi migliorati grazie agli scenari topologici;
- casi migliorati grazie all'automazione;
- casi ancora bloccati dal Graph JSON.

### Grafici utili per la tesi

Possibili grafici finali:

- barre `success/fail` ngspice per esperimento;
- barre impilate con categorie finali:
  `resolved`, `localized`, `topology_issue`, `inconclusive`;
- istogramma del numero di scenari usati;
- confronto Esperimento 1 vs 2 vs 3 sul tasso di diagnosi utile;
- heatmap circuiti/primitive scenario;
- tabella riassuntiva per circuito;
- grafico sull'uso dell'immagine:
  `senza immagine`, `image-assisted`, `richiesta ma non sufficiente`.

### Regola metodologica

La valutazione finale va fatta dopo aver completato gli esperimenti, ma la
struttura dei dati va pensata prima.

Quindi:

```text
durante ogni esperimento salviamo dati confrontabili;
alla fine produciamo CSV/JSON aggregati;
poi generiamo grafici e conclusioni numeriche.
```

Questa parte sara fondamentale per la tesi, perche permette di mostrare non
solo che il sistema funziona in alcuni esempi, ma anche come cambia la qualita
della diagnosi quando aumentano le capacita dell'agente.

## Sintesi del percorso

```text
Esperimento 1 = baseline Batch A chiusa
Esperimento 2 = scenari piu potenti e netlist editing controllato
Esperimento 3 = viewer visuale basato sulla netlist della run selezionata
Esperimento 4 = confronto CHAT vs AGENT con scenari autonomi controllati
Esperimento 5 = generalizzazione controllata su Batch B
Valutazione = metriche comuni, CSV/JSON aggregati e grafici finali
```

Frase guida:

```text
Ogni scenario produce una netlist SPICE alternativa, eseguibile e confrontabile;
l'agente usa queste netlist per diagnosticare, mentre il viewer le usa per
visualizzare il comportamento elettrico.
```
