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

Stato: in corso.

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
- i casi prioritari del Batch A per queste primitive sono gia stati coperti e
  documentati nei markdown `experiment2`.

In altre parole, la prima sottofase di Experiment 2 non e piu una fase di sola
implementazione del runner, ma una fase gia consolidata su tre famiglie di
scenari che cambiano in modo controllato la netlist SPICE.

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

Primitive candidate per Esperimento 2:

```text
connect_nodes
feed_nodes_from_source_node
add_voltage_source_between_nodes
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
- il prossimo blocco di lavoro non e piu "aggiungere una quarta primitiva
  topologica semplice", ma scegliere se passare a:
  - scenari analogici/dinamici sui casi `a04`, `a06`, `a08`;
  - oppure una fase successiva di correzione topologica/image-assisted su
    `a03`.

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

### Casi esclusi per ora

`a03` resta fuori dall'Esperimento 2 iniziale.

Motivo:

- e un caso speciale con graph/topologia fortemente sbagliati;
- richiede ragionamento image-assisted piu profondo;
- include batteria letta come due batterie, rele, bobina/contatto e ramo AC;
- rischia di far crescere troppo la complessita prima di consolidare le
  primitive semplici.

`a03` verra ripreso in una fase successiva dedicata alla correzione del graph o
alla ricostruzione guidata dall'immagine.

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

## Esperimento 3 - Automazione agentica

Stato: futuro, dopo Esperimento 2.

Obiettivo:

far eseguire all'agente piu scenari in sequenza, entro un limite controllato,
per arrivare a una diagnosi finale o a una localizzazione del problema.

Flusso desiderato:

```text
sintomo utente
-> agente propone scenario
-> pipeline crea run scenario
-> pipeline esegue ngspice
-> pipeline crea scenario_comparison.json
-> agente legge il confronto
-> agente decide se fermarsi o proporre altro
-> massimo 5 scenari
-> conclusione finale
```

Regole:

- l'agente non modifica file direttamente;
- la pipeline valida sempre lo scenario;
- ogni scenario deve essere tracciabile;
- se uno scenario risolve o localizza abbastanza il problema, l'agente si ferma;
- se il budget finisce, l'agente produce una conclusione finale;
- se serve correggere il Graph JSON, l'agente deve dichiararlo esplicitamente.

## Esperimento 4 - Viewer / simulatore visuale

Stato: futuro, dopo scenari e automazione.

Obiettivo:

creare una visualizzazione stile simulatore, ispirata a strumenti come Falstad,
ma basata sui nostri output Pipeline 1.0 / Pipeline 2.0 e sui risultati ngspice.

Regola centrale:

```text
il viewer parte dalla netlist della run selezionata
```

Questo e importante perche:

- la base run ha una netlist;
- ogni scenario puo avere una netlist diversa;
- se uno scenario cambia topologia, anche il circuito visualizzato cambia;
- quindi il viewer non deve assumere una sola topologia fissa.

Dati utili:

```text
run/07_netlist.cir
run/08_ngspice_stdout.txt
run/08_tran.csv
run/08_tran_plot.png
03_node_map.json
coordinate/componenti da Pipeline 1.0
immagine originale del circuito
```

Prima versione possibile:

- mostrare immagine del circuito;
- sovrapporre marker su componenti e terminali;
- colorare nodi in base alla tensione;
- animare componenti o rami con corrente non nulla;
- mostrare differenze tra base run e scenario run.

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
Esperimento 3 = agente che prova scenari in autonomia controllata
Esperimento 4 = viewer visuale basato sulla netlist della run selezionata
Valutazione = metriche comuni, CSV/JSON aggregati e grafici finali
```

Frase guida:

```text
Ogni scenario produce una netlist SPICE alternativa, eseguibile e confrontabile;
l'agente usa queste netlist per diagnosticare, mentre il viewer le usa per
visualizzare il comportamento elettrico.
```
