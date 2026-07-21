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
   Alla luce dello scenario eseguito, il problema è risolto? Spiegami in modo semplice la causa e la correzione verificata da SPICE.
   ```

### Risultato atteso da osservare

- stato SPICE dello scenario: `success`;
- base run: entrambi i LED `steady_on`;
- scenario: entrambi i LED `blinking` con periodo regolare;
- frequenza indicativa vicina a `7,3 Hz`, con circa 8 impulsi nella finestra da
  un secondo;
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
