# Copione demo — CHAT e AGENT

## Scopo

Questo documento contiene i messaggi da copiare e incollare durante la demo.
Ogni percorso e' stato scelto su un circuito gia' validato: le domande restano
umane, mentre CHAT o AGENT propongono ed eseguono gli scenari SPICE.

Regola operativa: inviare una riga alla volta e attendere la risposta o il
completamento dello scenario prima di inviare la successiva. Non cambiare la
formulazione dei prompt durante la demo.

## B02 — CHAT

### Obiettivo dimostrativo

Mostrare che il multivibratore astabile non richiede modifiche a componenti o
collegamenti: la base run resta bloccata perché ngspice parte da un punto di
lavoro perfettamente simmetrico. Una piccola asimmetria iniziale, applicata solo
alla copia scenario, deve avviare un lampeggio regolare dei due LED.

Prima della prova usare **Clean CHAT**. Gli scenari CHAT e AGENT sono copie
separate: un eventuale errore SPICE in uno scenario non modifica la base run.

### Sequenza da copiare e incollare

1. Domanda iniziale:

   ```text
   Il circuito dovrebbe far lampeggiare alternativamente i due LED, ma nella simulazione restano entrambi accesi. Come possiamo risolvere?
   ```

2. Controllare brevemente la proposta prima di eseguirla. Lo scenario corretto
   deve:

   - usare due condizioni iniziali distinte sui nodi di controllo simmetrici;
   - usare valori moderati, non l'intera alimentazione su un nodo di base;
   - abilitare l'avvio transitorio senza punto operativo (`UIC`);
   - non cambiare resistenze, condensatori, transistor o collegamenti;
   - dichiarare il criterio temporale di lampeggio regolare.

3. Se la proposta rispetta questi punti, eseguire:

   ```text
   esegui scenario 1
   ```

4. Dopo l'esecuzione chiedere la conclusione:

   ```text
   Lo scenario 1 ha risolto il problema? Qual era la causa e come è stato corretto il comportamento?
   ```

### Risultato atteso da osservare

- stato SPICE dello scenario: `success`;
- base run: entrambi i LED `steady_on`;
- scenario: entrambi i LED `blinking` con periodo regolare;
- scenario validato con condizioni iniziali `N004 = 0 V` e `N006 = 1 V`;
- frequenze misurate di circa `7,286 Hz` e `7,289 Hz`, con 8 impulsi per LED
  nella finestra da un secondo;
- `temporal_met: true`;
- esito dello scenario correttivo: `resolved_candidate`;
- nessuna modifica alla topologia o ai valori del circuito.

Se la proposta usa una condizione estrema come `0 V / 5 V`, non eseguirla:
pulire CHAT e ripetere esattamente la domanda sopra. Quel tentativo può causare
un errore numerico di ngspice, ma resta confinato alla copia scenario e non
danneggia alcun output di base.

### Chiusura della dimostrazione B02–CHAT

La prova mostra una distinzione importante: il circuito estratto è coerente,
mentre la run base idealmente simmetrica non rappresenta bene il transitorio di
accensione reale. La correzione riguarda quindi l'avvio della simulazione e
viene accettata soltanto dopo la verifica temporale prodotta da ngspice.

## B02 — AGENT

### Obiettivo dimostrativo

Mostrare una diagnosi autonoma prudente sullo stesso sintomo. Questa validazione
non deve essere presentata come correzione riuscita: AGENT esegue prove SPICE,
localizza una possibile causa e si ferma quando gli scenari successivi sarebbero
speculativi, senza consumare necessariamente tutto il budget.

Prima della prova usare **Clean AGENT**. Il workspace AGENT è indipendente dalla
sessione CHAT già risolta.

### Domanda unica da copiare e incollare

```text
Il circuito dovrebbe far lampeggiare alternativamente i due LED, ma nella simulazione restano entrambi accesi. Come mai?
```

### Esito validato da dichiarare correttamente

- stato del ciclo: `completed`;
- stato finale: `localized`;
- 3 decisioni autonome e 3 scenari eseguiti;
- tutte le run ngspice completate con `success`;
- arresto spontaneo prima del limite massimo di 5 scenari;
- causa proposta: polarizzazione forte e simmetrica dei due rami;
- nessuna correzione temporale verificata;
- `verified_correction` vuoto;
- non usare le parole `resolved` o "circuito corretto" per descrivere questo
  risultato.

### Chiusura della dimostrazione B02–AGENT

La prova valida l'esecuzione del ciclo diagnostico e la capacità di fermarsi con
una localizzazione non risolutiva. Il confronto con CHAT è intenzionale: CHAT ha
verificato una correzione di startup, mentre questa esecuzione AGENT ha prodotto
soltanto una diagnosi localizzata. Nelle statistiche i due esiti devono restare
distinti.

## B03 — CHAT

### Obiettivo dimostrativo

Mostrare con tre scenari indipendenti che il monitor reagisce a una batteria
scarica, a una batteria molto carica e a una tensione che varia nel tempo. Ogni
scenario modifica soltanto la sorgente della batteria già presente nella
netlist e riparte dalla base run.

Prima della prova usare **Clean CHAT** e selezionare la base run.

### Sequenza da copiare e incollare

1. Domanda iniziale:

   ```text
   Con la batteria a 12 V vedo acceso solo il LED giallo. Vorrei verificare il monitor in tre condizioni: batteria scarica, batteria molto carica e variazione della tensione nel tempo. Quali tre scenari controllati, indipendenti ed eseguibili proponi?
   ```

2. Controllare che siano stati registrati tre scenari eseguibili:

   - batteria scarica a `10 V`;
   - batteria molto carica a `14,4 V`;
   - batteria variabile con `SIN(12 2 0.2)`.

3. Eseguire il caso di batteria scarica:

   ```text
   esegui scenario 1
   ```

   Risultato da osservare: a 10 V il rosso è `steady_on`, mentre giallo e verde
   sono spenti.

4. Eseguire il caso di batteria molto carica:

   ```text
   esegui scenario 2
   ```

   Risultato da osservare: a 14,4 V il verde è `steady_on`, mentre rosso e
   giallo sono spenti.

5. Eseguire la variazione temporale:

   ```text
   esegui scenario 3
   ```

   Risultato da osservare: i tre LED attraversano stati `transient_pulse` in
   istanti diversi, seguendo i campioni prodotti da ngspice. La finestra di 3
   secondi mostra la salita fino al massimo e buona parte della discesa della
   sinusoide da 0,2 Hz.

### Risultato validato

- tre scenari registrati con `Executable: True`;
- tutte le run ngspice concluse con `success`;
- nessuna misura attesa fallita o mancante;
- misure `tran_abs_peak` presenti per tutte le correnti LED;
- scenario 1: rosso acceso;
- scenario 2: verde acceso;
- scenario 3: risposta temporale visibile su tutti e tre i LED;
- nessuna modifica al Graph JSON o alla topologia.

Gli outcome possono restare `partially_resolved`: gli scenari verificano il
comportamento del monitor, ma le aspettative `changed` non rappresentano una
correzione relativa del sintomo superiore alla soglia interna. Questo non
invalida gli stati LED misurati e mostrati dal viewer.

### Chiusura della dimostrazione B03–CHAT

La sequenza dimostra in modo compatto un controllo statico e dinamico della
stessa netlist. Le tre run rimangono separate e la base a 12 V non viene
modificata.

## B03 — AGENT

### Obiettivo dimostrativo

Far pianificare all'AGENT una verifica completa ma piccola: una condizione di
batteria scarica, una di batteria molto carica e una sola rampa transitoria.
L'AGENT sceglie gli scenari ed esegue ngspice autonomamente; non deve cambiare
Graph JSON o topologia.

### Domanda unica da copiare e incollare

```text
Il monitor della batteria a 12 V mostra solo il LED giallo. Puoi controllare da solo se segnala correttamente una batteria scarica, una molto carica e anche cosa succede mentre la tensione cambia?
```

### Risultato atteso da osservare

- una prova statica a bassa tensione, con prevalenza del LED rosso;
- una prova statica ad alta tensione, con prevalenza del LED verde;
- una rampa transitoria, in cui il viewer mostra il passaggio sequenziale delle
  soglie LED;
- conclusione basata sulle run SPICE, senza correzioni topologiche inventate.

## A04 — CHAT

### Obiettivo dimostrativo

Mostrare che lo stadio a transistor e' correttamente polarizzato e amplifica,
ma l'uscita puo' sembrare debole perche' la sorgente sinusoidale di base ha
un'ampiezza di soli 10 mV. La prova modifica soltanto la sorgente gia' presente
e misura esplicitamente il guadagno transitorio tra ingresso e uscita.

Prima della prova usare **Clean CHAT**.

### Sequenza da copiare e incollare

1. Domanda iniziale:

   ```text
   Il circuito dovrebbe amplificare il segnale, ma in uscita vedo un segnale troppo debole. Vorrei verificare se dipende dal fatto che VIN e' di appena 10 mV: quale unico scenario transitorio controllato proponi, aumentando moderatamente l'ingresso e misurando esplicitamente il guadagno tra ingresso e uscita?
   ```

2. Controllare che lo scenario registrato:

   - modifichi soltanto `Vsignal_source23_1`;
   - porti la sinusoide da `SIN(0 0.01 100)` a `SIN(0 0.05 100)`;
   - confronti `v(N002)` e `v(N006)` in transitorio;
   - dichiari il guadagno `Vpp(N006) / Vpp(N002)` con una soglia minima.

3. Dopo avere verificato il numero realmente mostrato nella sezione
   **Scenari registrati**, eseguire lo scenario. In una CHAT pulita sara'
   normalmente:

   ```text
   esegui scenario 1
   ```

4. Chiedere la conclusione:

   ```text
   Il test conferma che lo stadio amplifica? Qual era la causa dell'uscita apparentemente debole?
   ```

### Risultato atteso da osservare

- stato ngspice: `success`;
- `v(N002)` da circa `0,020 Vpp` a circa `0,100 Vpp`;
- `v(N006)` da circa `0,092 Vpp` a circa `0,467 Vpp`;
- guadagno dello scenario di circa `4,67`;
- criterio minimo di guadagno soddisfatto;
- nessuna modifica a topologia, bias o componenti passivi;
- conclusione: il circuito amplifica gia', mentre l'uscita assoluta della base
  run appare debole perche' il segnale di ingresso e' molto piccolo.

### Nota sulla numerazione

Fare sempre riferimento alla sezione **Scenari registrati**, non al numero
usato nel testo descrittivo del modello. Gli scenari privi dei criteri tecnici
obbligatori non vengono registrati e quelli validi possono quindi essere
rinumerati.

## A04 — AGENT

### Obiettivo dimostrativo

Mostrare che l'AGENT distingue autonomamente un guasto dell'amplificatore da
una semplice eccitazione insufficiente. Deve controllare il punto di lavoro,
modificare soltanto la sorgente di ingresso e fermarsi appena ngspice verifica
la correzione.

Prima della prova usare **Clean AGENT**.

### Domanda unica da copiare e incollare

```text
Il circuito dovrebbe amplificare il segnale, ma in uscita vedo un segnale troppo debole o quasi nullo. Quale potrebbe essere il problema?
```

### Esito validato da osservare

- ciclo autonomo: `completed`;
- 2 decisioni totali;
- un solo scenario eseguito;
- stato ngspice: `success`;
- 3 criteri attesi su 3 soddisfatti;
- sorgente portata da 10 mV a 50 mV, senza altre modifiche;
- guadagno transitorio misurato di circa `4,67`;
- esito dello scenario: `resolved_candidate`;
- arresto automatico: `stop_automation: true`;
- stato finale AGENT: `resolved`;
- causa finale: ingresso iniziale troppo piccolo, non errore topologico o di
  polarizzazione;
- correzione verificata presente e coerente con lo scenario SPICE.

### Chiusura della dimostrazione A04—AGENT

L'AGENT parte dal sintomo espresso dall'utente, verifica che il BJT sia
polarizzato, esegue una sola modifica controllata e conclude usando il guadagno
misurato. Il risultato e' una correzione verificata, non una semplice ipotesi
diagnostica.

## A08 — CHAT

### Obiettivo dimostrativo

Mostrare una diagnosi guidata sul lampeggio del LED. La base run produce
soltanto impulsi brevi e non regolari; una modifica controllata del pilotaggio
di base deve ottenere un lampeggio periodico verificato da ngspice.

Prima della prova usare **Clean CHAT**.

### Sequenza da copiare e incollare

1. Domanda iniziale:

   ```text
   Il LED non lampeggia come mi aspetterei. Quale potrebbe essere il problema?
   ```

2. Eseguire lo scenario che riduce `Rresistor22_4` da 68 kohm a 33 kohm. Nella
   run validata e' stato registrato come:

   ```text
   esegui scenario 1
   ```

3. Chiedere la conclusione:

   ```text
   Lo scenario ha reso il lampeggio regolare? Quale parte del circuito limitava il comportamento del LED?
   ```

### Risultato atteso da osservare

- stato ngspice: `success`;
- base run: `transient_pulse`, periodo non regolare;
- scenario: `blinking` regolare a circa `10,02 Hz`;
- esito formale: `resolved_candidate`;
- arresto consigliato: `stop_automation: true`;
- la prova valida il recupero della regolarita; il duty cycle fisico resta
  piccolo e puo' essere presentato come un affinamento distinto.

## A08 — AGENT

### Obiettivo dimostrativo

Far individuare autonomamente la causa dei lampi troppo brevi e ottenere una
correzione verificata sia elettricamente sia nel profilo temporale del LED.

Prima della prova usare **Clean AGENT**.

### Domanda unica da copiare e incollare

```text
Il LED produce soltanto lampi brevissimi e quasi non si vede. Puoi capire perché e provare a farlo lampeggiare in modo regolare e chiaramente visibile?
```

### Esito validato da osservare

- ciclo autonomo: `completed`;
- 3 decisioni totali;
- 3 scenari eseguiti, tutti con ngspice `success`;
- prime ipotesi su startup e rete RC correttamente scartate dai criteri
  temporali;
- correzione finale: `Rresistor22_3` / R7 da 560 ohm a 4,7 kohm;
- tutte le aspettative elettriche dell'ultimo scenario soddisfatte;
- stato LED finale: `blinking` con periodo regolare;
- duty cycle da circa `0,006` a circa `0,336`;
- esito ultimo scenario: `resolved_candidate`;
- `stop_automation: true`;
- stato finale AGENT: `resolved`;
- `verified_correction` valorizzato con la modifica di R7.

### Chiusura della dimostrazione A08—AGENT

La prova mostra un ciclo autonomo completo: due ipotesi vengono eliminate con
ngspice, la terza modifica un solo componente gia' presente e il ciclo si ferma
quando i criteri elettrici e temporali risultano entrambi soddisfatti.

## A09 — CHAT

### Obiettivo dimostrativo

Mostrare che la base run alimenta il solo nodo dopo il fusibile, mentre i rami
della lampada e del LED rimangono separati. CHAT verifica prima il ramo LED e
poi applica una correzione self-contained che alimenta entrambi i rami e chiude
lo switch della lampada. A09 usa soltanto il punto operativo DC: non richiedere
scenari transitori, perché la base run non contiene `08_tran.csv`.

Prima della prova usare **Clean CHAT** e selezionare la base run.

### Sequenza da copiare e incollare

1. Domanda iniziale:

   ```text
   La lampada e il LED non si accendono. Come possiamo fare per accenderli contemporaneamente?
   ```

2. La risposta validata propone tre prove diagnostiche separate. Eseguire
   quella che alimenta il ramo LED dal nodo `BAT_FUSED`; in una CHAT pulita è:

   ```text
   esegui scenario 2
   ```

   Risultato da osservare: si accende soltanto il LED. La tensione su `N005`
   sale a circa 9 V e la corrente del ramo LED raggiunge circa 25 mA.

3. Chiedere ora la correzione completa:

   ```text
   Il test conferma che il ramo LED funziona quando viene alimentato. Ora proponi un unico scenario self-contained che mantenga acceso il LED e accenda anche la lampada, alimentando il suo ingresso e chiudendo lo switch. Considera risolto il problema solo se nella stessa simulazione passa corrente sia nel LED sia nella lampada.
   ```

4. Controllare che lo scenario combini nella stessa run:

   - collegamento di `N003` a `N005` per il ramo LED;
   - collegamento di `N003` a `N004` per il ramo lampada;
   - chiusura di `switch25.1`.

   Eseguire quindi l'ultimo scenario registrato:

   ```text
   esegui ultimo
   ```

### Risultato atteso da osservare

- stato ngspice: `success`;
- ramo LED alimentato, con corrente di circa `25 mA`;
- lampada alimentata, con corrente di circa `100 mA`;
- LED e lampada attivi contemporaneamente nel viewer;
- nessuna aspettativa elettrica fallita;
- base run non modificata.

L'esito formale può restare `partially_resolved` perché `v(N004)` non è
disponibile nella base run: il nodo era flottante. Questa misura mancante non
invalida le due correnti non nulle che dimostrano l'attivazione simultanea dei
carichi.

### Chiusura della dimostrazione A09—CHAT

La prova mostra una diagnosi guidata progressiva: prima viene verificato un
singolo ramo, poi la correzione completa viene applicata in una nuova copia
self-contained. I risultati sono letti dal punto operativo prodotto da
ngspice, senza introdurre un transitorio privo di significato per questo
circuito DC.

## A09 — AGENT

### Obiettivo dimostrativo

Mostrare che AGENT può partire dallo stesso sintomo umano, riconoscere entrambi
i percorsi non alimentati e verificare autonomamente la correzione completa in
una sola run SPICE.

Prima della prova usare **Clean AGENT**. Il workspace AGENT è indipendente
dalla sessione CHAT.

### Domanda unica da copiare e incollare

```text
La lampada e il LED non si accendono. Puoi capire perché e sistemare il circuito in modo che si accendano entrambi contemporaneamente?
```

### Esito validato da osservare

- ciclo autonomo: `completed`;
- 2 decisioni totali su 8;
- un solo scenario eseguito;
- stato ngspice: `success`;
- collegamento di `N003` a `N004` e `N005`;
- chiusura di `switch25.1`;
- corrente della lampada di circa `100 mA`;
- corrente del LED di circa `25 mA`;
- 4 criteri attesi su 4 soddisfatti;
- esito dello scenario: `resolved_candidate`;
- arresto automatico: `stop_automation: true`;
- stato finale AGENT: `resolved`;
- causa e correzione verificate riportate nella conclusione finale.

### Chiusura della dimostrazione A09—AGENT

AGENT applica direttamente la correzione combinata, verifica con ngspice che
le correnti dei due carichi siano entrambe attive e si ferma senza consumare
scenari ulteriori. Questo rende A09 un caso breve e leggibile per mostrare la
differenza tra il percorso guidato di CHAT e quello autonomo di AGENT.
