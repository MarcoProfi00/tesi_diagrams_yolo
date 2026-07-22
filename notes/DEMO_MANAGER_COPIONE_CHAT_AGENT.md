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

Mostrare che il monitor a tre LED reagisce a tre condizioni statiche della
batteria: scarica, molto carica e chiaramente oltre soglia. Il percorso usa
soltanto la sorgente della batteria gia' presente nella netlist e non modifica
la topologia del circuito.

### Sequenza da copiare e incollare

1. Domanda iniziale:

   ```text
   Con la batteria a 12 V vedo acceso solo il LED giallo. Vorrei verificare che il monitor distingua una batteria scarica: quale scenario controllato proponi come primo test?
   ```

2. Dopo la proposta, eseguire il primo scenario:

   ```text
   esegui scenario 1
   ```

   Risultato da osservare: a 10 V si accende il LED rosso.

3. Domanda per la condizione molto carica:

   ```text
   Con 10 V il LED rosso si è acceso. Per completare la verifica del monitor, quale scenario controllato proponi ora per una batteria molto carica?
   ```

4. Dopo la proposta, eseguire il secondo scenario:

   ```text
   esegui scenario 2
   ```

   Risultato da osservare: a 14 V possono restare accesi sia il LED giallo sia
   quello verde; questa e' l'evidenza da usare per la domanda seguente.

5. Domanda diagnostica sul comportamento a 14 V:

   ```text
   Con 14 V sono accesi sia il LED giallo sia il verde, ma il circuito dovrebbe mostrare solo il verde sopra 13,5 V. Quale scenario diagnostico minimo proponi per capire perché Q2 e il LED giallo restano accesi?
   ```

6. Dopo la proposta, eseguire il terzo scenario:

   ```text
   esegui scenario 3
   ```

   Risultato da osservare: il giallo puo' restare acceso; il test diagnostico
   non e' ancora una correzione risolutiva.

7. Domanda per verificare una condizione chiaramente oltre soglia:

   ```text
   A 14 V vedo ancora giallo e verde. Vorrei verificare il comportamento a una tensione chiaramente più alta: quale scenario controllato proponi?
   ```

8. Dopo la proposta, eseguire l'ultimo scenario proposto:

   ```text
   esegui ultimo
   ```

   Risultato finale da mostrare: a 16 V il LED verde prevale correttamente.

### Estensione transitoria opzionale

Dopo aver concluso i quattro test statici, si puo' mostrare anche la
transizione temporale tra batteria scarica e molto carica. Questo scenario usa
una rampa sulla sorgente della batteria: nel viewer i LED cambiano stato mentre
la tensione sale.

9. Domanda per il transitorio:

   ```text
   Abbiamo verificato il comportamento statico a batteria scarica, nominale e molto carica. Ora vorrei osservare come reagiscono nel tempo i LED se la tensione della batteria varia lentamente da scarica a molto carica: quale scenario transitorio proponi?
   ```

10. Dopo la proposta, eseguire lo scenario transitorio:

   ```text
   esegui ultimo
   ```

   Risultato da mostrare: la sorgente batteria varia nel tempo e il viewer
   riproduce i cambi di stato ricavati dal transitorio ngspice. Non e' un
   lampeggio artificiale: l'animazione e' derivata dai campioni SPICE.

### Chiusura della dimostrazione B03–CHAT

La sequenza dimostra un controllo progressivo e ripetibile: la stessa netlist
viene confrontata a 10 V, 14 V e 16 V in run scenario separate. La base run
non viene modificata.

## B03 — AGENT

### Obiettivo dimostrativo

Far pianificare all'AGENT una verifica completa ma piccola: una condizione di
batteria scarica, una di batteria molto carica e una sola rampa transitoria.
L'AGENT sceglie gli scenari ed esegue ngspice autonomamente; non deve cambiare
Graph JSON o topologia.

### Domanda unica da copiare e incollare

```text
Nella base run a 12 V è acceso solo il LED giallo. Voglio verificare prima, con prove statiche separate, il comportamento a batteria scarica e a batteria molto carica. Solo dopo esegui una singola rampa transitoria per mostrare il passaggio tra gli stati. Mantieni invariati Graph JSON e topologia e concludi usando le evidenze SPICE.
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
