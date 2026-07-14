# BatchA - Agent Model Evaluation Grid

Questo file raccoglie i sintomi usati per interrogare l'agente diagnostico e i
punteggi assegnati alle risposte del modello usato come baseline.

Obiettivo:

```text
valutare la prima versione dell'agente diagnostico sul Batch A
```

In questa fase non confrontiamo piu modelli diversi. La baseline scelta e:

```text
gpt-5.4
```

I confronti con altri modelli possono essere aggiunti in futuro, ma per ora la
priorita e costruire la chat diagnostica e l'esecuzione controllata degli
scenari.

## Legenda

```text
5 = risposta utile, corretta e affidabile per l'utente
4 = buona risposta con piccoli limiti
3 = utilizzabile ma con limiti evidenti
2 = debole
1 = quasi inutilizzabile
0 = errata

PASS = 4-5
WARN = 2-3
FAIL = 0-1
```

## Criteri di valutazione

Per ogni risposta controlliamo:

- interpretazione corretta di `08_spice_run.json`;
- lettura corretta di `08_ngspice_stdout.txt`;
- lettura corretta di `08_ngspice_stderr.txt`;
- rispetto di `01_graph.json`, `03_node_map.json`, netlist e valori;
- richiesta immagine solo quando giustificata;
- scenari diagnostici naturali e verificabili;
- JSON tecnico degli scenari coerente;
- scenari trasformabili in run SPICE controllate;
- distinzione chiara tra scenari elettrici e scenari di correzione topologica;
- assenza di componenti, valori, connessioni o risultati inventati.

Nota importante sugli scenari:

```text
Gli scenari elettrici modificano valori, sorgenti, stati, analisi o modelli
equivalenti e possono spesso ripartire da 04/06/07/08.

Gli scenari topologici modificano connessioni, terminali o Graph JSON. In quel
caso bisogna creare una copia scenario del graph e rigenerare gli output della
Pipeline 2.0 senza sovrascrivere quelli originali.
```

Esempio:

```text
a03 richiede probabilmente scenari topologici/image-assisted:
non basta cambiare un valore SPICE, bisogna verificare/correggere il graph,
poi rigenerare node map, values binding, component rules, netlist e run SPICE.
```

## Griglia sintetica

Formato valutazione:

```text
LABEL score/5
```

| Circuito | Sintomo fissato | Valutazione gpt-5.4 | Note |
|---|---|---:|---|
| a01 | Perche la lampada non si accende? | PASS 5/5 | Diagnosi corretta; scenari naturali; immagine non richiesta. |
| a02 | Il circuito non produce l'uscita attesa, quale potrebbe essere il problema? | PASS 4/5 | Diagnosi corretta; scenari utilizzabili, con piccoli limiti. |
| a03 | Quando alimento il circuito, il sistema non commuta correttamente e la lampada resta spenta. Quale potrebbe essere il problema? | PASS 4/5 | Diagnosi corretta del fallimento SPICE; immagine richiesta correttamente. |
| a04 | Il circuito si accende ma il segnale in uscita non e quello atteso. Quale potrebbe essere il problema? | PASS 5/5 | Risposta utile e coerente; interpreta correttamente .op, .tran e uscita AC-coupled. |
| a05 | Quando collego il circuito, il voltmetro resta a zero. Quale potrebbe essere il problema? | PASS 4/5 | Diagnosi corretta; scenari buoni, con piccole priorita migliorabili. |
| a06 | Il circuito amplifica, ma il segnale in uscita sembra distorto o non come mi aspettavo. Quale potrebbe essere il problema? | WARN 3/5 | Risposta utile, ma interpreta in modo discutibile il punto operativo del transistor. |
| a07 | Il trasformatore sembra funzionare, ma il LED di alimentazione non si accende. Quale potrebbe essere il problema? | PASS 4/5 | Diagnosi corretta del LED collassato a massa; scenari migliorabili. |
| a08 | Il LED non sembra accendersi correttamente con il segnale square. Quale potrebbe essere il problema? | PASS 5/5 | Risposta centrata; interpreta correttamente square, ramo LED/transistor e scenari. |
| a09 | La batteria e presente, ma il LED non si accende e non sembra passare corrente. Quale potrebbe essere il problema? | PASS 4/5 | Diagnosi corretta del ramo LED non alimentato; scenari e richiesta immagine migliorabili. |
| a10 | La batteria e collegata, ma ne il LED ne la lampada si accendono. Quale potrebbe essere il problema? | PASS 5/5 | Risposta molto pulita; distingue bene switch, batteria e rami non alimentati. |

## Sintesi risultati

```text
Circuiti valutati: 10
PASS: 9
WARN: 1
FAIL: 0
Punteggio medio: 4.3 / 5
```

## Dettaglio valutazioni

### a01

Sintomo:

```text
Perche la lampada non si accende?
```

Modello valutato:

```text
gpt-5.4
```

Output valutato:

```text
outputs/pipeline2.0/batchA/a01/11_agent_response_v5.md
```

Punteggio:

```text
PASS 5/5
```

Motivo:

- interpreta correttamente la run `.op`;
- riconosce che ngspice ha successo e `stderr` e vuoto;
- identifica il ramo lampada come non alimentato;
- non descrive il ramo come flottante;
- non richiede l'immagine;
- propone scenari leggibili e JSON tecnici coerenti.

### a02

Sintomo:

```text
Il circuito non produce l'uscita attesa, quale potrebbe essere il problema?
```

Modello valutato:

```text
gpt-5.4
```

Output valutato:

```text
outputs/pipeline2.0/batchA/a02/11_agent_response.md
```

Punteggio:

```text
PASS 4/5
```

Motivo:

- diagnosi principale corretta;
- riconosce `success` con warning numerici su `N001`;
- interpreta correttamente assenza di percorso attivo di corrente;
- non richiede l'immagine, coerentemente con graph e node map;
- scenario 1, chiusura di `switch25.1`, e molto coerente;
- scenari 2-3 sono utilizzabili, anche se non perfettamente allineati alla
  priorita ideale discussa nel markdown umano `a02.md`.

### a03

Sintomo:

```text
Quando alimento il circuito, il sistema non commuta correttamente e la lampada resta spenta. Quale potrebbe essere il problema?
```

Modello valutato:

```text
gpt-5.4
```

Output valutato:

```text
outputs/pipeline2.0/batchA/a03/11_agent_response_commuta.md
```

Punteggio:

```text
PASS 4/5
```

Motivo:

- riconosce correttamente che ngspice fallisce;
- non interpreta la run come simulazione valida della lampada;
- collega il fallimento a singleton, assenza di ground e ramo lampada/contatto incompleto;
- riconosce che `lamp13.1`, `inductor10.1` e `variable_resistor30.1` non vengono emessi;
- chiede l'immagine in modo giustificato;
- scenari utili e coerenti con il sintomo, anche se non enfatizza pienamente la possibile batteria fisica letta come due batterie.

Nota:

```text
Questo e un caso in cui l'immagine puo diventare importante nella fase image-assisted.
Con accesso all'immagine, l'agente dovrebbe avere piu elementi per verificare se
la batteria fisica e stata letta come due Battery separate e se il rele e stato
rappresentato in modo incompleto come bobina/induttore + switch.
```

### a04

Sintomo:

```text
Il circuito si accende ma il segnale in uscita non e quello atteso. Quale potrebbe essere il problema?
```

Modello valutato:

```text
gpt-5.4
```

Output valutato:

```text
outputs/pipeline2.0/batchA/a04/11_agent_response.md
```

Punteggio:

```text
PASS 5/5
```

Motivo:

- riconosce correttamente che ngspice ha successo;
- usa sia `.op` sia `.tran`;
- non chiede immagine, coerentemente con graph e node map;
- interpreta correttamente la polarizzazione del transistor;
- distingue il nodo collettore `N005` dall'uscita accoppiata in AC `N006`;
- propone scenari diagnostici coerenti con il sintomo utente.

### a05

Sintomo:

```text
Quando collego il circuito, il voltmetro resta a zero. Quale potrebbe essere il problema?
```

Modello valutato:

```text
gpt-5.4
```

Output valutato:

```text
outputs/pipeline2.0/batchA/a05/11_agent_response.md
```

Punteggio:

```text
PASS 4/5
```

Motivo:

- riconosce correttamente che ngspice termina con `success`;
- segnala il warning numerico `singular matrix` sul nodo `N003`;
- capisce che la netlist non contiene sorgenti di alimentazione o segnale;
- interpreta `analog_meter0.1` come sonda di tensione, non come componente fisico;
- collega correttamente il valore nullo del voltmetro al fatto che `VMON_INPUT` / `N003` non e pilotato;
- non richiede l'immagine, coerentemente con graph, node map e run SPICE;
- propone come scenario principale l'alimentazione di `VMON_INPUT`, che e lo scenario piu naturale.

Limite:

```text
Gli scenari sono utili, ma non perfetti nella priorita. Lo scenario di chiusura
del ramo TEST e possibile ma probabilmente poco influente sul voltmetro; manca
invece lo scenario esplicito di modellare il voltmetro come carico reale ad alta
impedenza.
```

### a06

Sintomo:

```text
Il circuito amplifica, ma il segnale in uscita sembra distorto o non come mi aspettavo. Quale potrebbe essere il problema?
```

Modello valutato:

```text
gpt-5.4
```

Output valutato:

```text
outputs/pipeline2.0/batchA/a06/11_agent_response.md
```

Punteggio:

```text
WARN 3/5
```

Motivo:

- riconosce correttamente che ngspice termina con `success`;
- riconosce che `stderr` e vuoto;
- capisce che il circuito e un amplificatore NPN con `.op` e `.tran`;
- individua correttamente la sorgente `SIN(0 1 100)`;
- propone correttamente come primo scenario la riduzione dell'ampiezza di ingresso.

Limite:

```text
La risposta e troppo sbilanciata sull'idea che il transistor sia quasi spento.
Questa interpretazione usa parametri del blocco finale di stdout che sono
delicati da leggere, mentre i nodi esterni iniziali indicano una polarizzazione
piu plausibile: base circa 3.664 V, emettitore circa 3.024 V e collettore circa
6.763 V.
```

Nota:

```text
La diagnosi piu robusta per noi resta: il circuito e simulabile e amplifica, ma
l'ingresso da 1 V di ampiezza e grande per un test piccolo segnale e puo portare
a distorsione/non linearita.
```

### a07

Sintomo:

```text
Il trasformatore sembra funzionare, ma il LED di alimentazione non si accende. Quale potrebbe essere il problema?
```

Modello valutato:

```text
gpt-5.4
```

Output valutato:

```text
outputs/pipeline2.0/batchA/a07/11_agent_response.md
```

Punteggio:

```text
PASS 4/5
```

Motivo:

- riconosce correttamente che ngspice termina con `success`;
- riconosce che `stderr` e vuoto;
- capisce che il trasformatore equivalente produce una sinusoide valida;
- identifica il punto fondamentale: `led12.1` non viene emesso perche anodo e catodo collassano entrambi sul nodo `0`;
- collega correttamente il ramo PWR / `N003` alla mancanza di pilotaggio;
- distingue tra comportamento del circuito estratto e possibile circuito reale;
- non inventa correnti del LED, perche il LED non e presente nella netlist.

Limite:

```text
Gli scenari non sono ordinati in modo ideale. Lo scenario piu importante per noi
sarebbe una riparazione topologica del ramo PWR/LED; la risposta invece mette
prima il pilotaggio di N003. Inoltre, dato il sospetto topologico sul LED, una
richiesta immagine sarebbe stata giustificata.
```

### a08

Sintomo:

```text
Il LED non sembra accendersi correttamente con il segnale square. Quale potrebbe essere il problema?
```

Modello valutato:

```text
gpt-5.4
```

Output valutato:

```text
outputs/pipeline2.0/batchA/a08/11_agent_response.md
```

Punteggio:

```text
PASS 5/5
```

Motivo:

- riconosce correttamente che ngspice termina con `success`;
- riconosce che `stderr` e vuoto;
- interpreta correttamente la sorgente square come `PULSE(0 5 0 1ms 1ms 50ms 100ms)`;
- capisce che l'ampiezza 0-5 V e una assunzione manuale;
- identifica correttamente LED, transistor e nodi principali;
- nota che `N005` viene portato circa a meta ingresso dal partitore 560 ohm / 560 ohm;
- interpreta correttamente il fatto che il LED non riceve una polarizzazione diretta forte e stabile;
- non richiede l'immagine, coerentemente con graph, node map e run SPICE;
- propone scenari utili: cambiare ampiezza della square, provare ingresso fisso alto e verificare il ramo emettitore.

Limite minore:

```text
La risposta non enfatizza il dato dello stdout sulla corrente LED praticamente
nulla e non propone esplicitamente lo scenario con modello LED piu realistico.
Resta comunque una risposta molto coerente e utile.
```

### a09

Sintomo:

```text
La batteria e presente, ma il LED non si accende e non sembra passare corrente. Quale potrebbe essere il problema?
```

Modello valutato:

```text
gpt-5.4
```

Output valutato:

```text
outputs/pipeline2.0/batchA/a09/11_agent_response.md
```

Punteggio:

```text
PASS 4/5
```

Motivo:

- riconosce correttamente che ngspice termina con `success`;
- interpreta correttamente il warning `singular matrix` su `N002` come nodo del condensatore flottante in `.op`;
- capisce che la batteria da 9 V e presente;
- capisce che il fusibile porta la batteria fino a `N003`;
- identifica correttamente che il ramo LED/resistenza non e collegato alla batteria;
- interpreta correttamente la netlist `Rresistor22_1 0 N006 330` e `Dled12_1 N006 0 LED_RED`;
- non conclude che il LED sia fisicamente guasto;
- distingue tra circuito estratto e possibile circuito reale.

Limite:

```text
Lo scenario 1 riguarda lampada/interruttore, quindi e fuori priorita rispetto al
sintomo sul LED. Inoltre, dato il sospetto topologico sul ponte vicino al ramo
LED/resistenza, una richiesta immagine sarebbe stata giustificata.
```

### a10

Sintomo:

```text
La batteria e collegata, ma ne il LED ne la lampada si accendono. Quale potrebbe essere il problema?
```

Modello valutato:

```text
gpt-5.4
```

Output valutato:

```text
outputs/pipeline2.0/batchA/a10/11_agent_response.md
```

Punteggio:

```text
PASS 5/5
```

Motivo:

- riconosce correttamente che ngspice termina con `success`;
- riconosce che `stderr` e vuoto;
- legge correttamente `N001 = 5 V`;
- capisce che `switch25.1` e aperto e quindi non viene emesso;
- capisce che il positivo della batteria resta isolato su `N001`;
- interpreta correttamente i rami LED e lampada come non alimentati nella simulazione base;
- non attribuisce il problema a guasto fisico di LED o lampada;
- non richiede l'immagine, coerentemente con graph, node map e run SPICE;
- propone scenari ordinati e coerenti: chiudere lo switch, alimentare il ramo LED, alimentare il ramo lampada.

Nota:

```text
La risposta e particolarmente buona perche non si ferma alla sola chiusura dello
switch: riconosce che anche con lo switch chiuso non e dimostrato che
l'alimentazione raggiunga automaticamente i rami su N003 e N004.
```

## Comandi di riferimento

Esempio per rieseguire un circuito con modello di default `gpt-5.4`:

```powershell
python scripts\pipeline_2.0\json_to_spice\11_agent_readonly.py --batch batchA --circuit a02 --question "Il circuito non produce l'uscita attesa, quale potrebbe essere il problema?" --run-agent --response-output outputs\pipeline2.0\batchA\a02\11_agent_response.md
```

