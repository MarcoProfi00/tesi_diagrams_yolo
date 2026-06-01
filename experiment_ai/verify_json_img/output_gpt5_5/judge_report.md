# Report verifica immagine ↔ Graph JSON

Generato: 2026-06-01 20:14:41

## Tabella sintetica

| Circuito | Batch | Score | Decisione | Critici | Maggiori | Minori | Usabile come graph base |
|---|---:|---:|---|---:|---:|---:|---|
| a01 | A | 93 | PASS | 0 | 0 | 2 | True |
| a02 | A | 76 | NEEDS_PATCH | 0 | 3 | 1 | False |
| a03 | A | 75 | NEEDS_PATCH | 0 | 3 | 2 | False |
| a04 | A | 88 | MINOR_ISSUES | 0 | 0 | 3 | True |
| a05 | A | 78 | NEEDS_PATCH | 0 | 3 | 2 | False |
| a06 | A | 86 | MINOR_ISSUES | 0 | 0 | 3 | True |
| a07 | A | 78 | NEEDS_PATCH | 0 | 3 | 1 | False |
| a08 | A | 70 | NEEDS_PATCH | 0 | 3 | 1 | False |
| a09 | A | 91 | PASS | 0 | 0 | 3 | True |
| a10 | A | 94 | PASS | 0 | 0 | 2 | True |

## Dettagli per circuito

### a01

- Batch: `A`
- Score: `93`
- Decisione: `PASS`
- Usabile come graph base: `True`
- Spiegazione: Il JSON rappresenta correttamente i componenti principali visibili: connettore a 4 pin, switch aperto, tre simboli GND, due resistori, LED e lampada. I collegamenti nel campo graph corrispondono alla topologia mostrata: pin 1 verso resistore e LED a massa comune, pin 2 verso resistore e lampada a massa comune, pin 3 verso switch e massa tramite l'altro lato dello switch, pin 4 a GND. Restano solo minori imprecisioni sui relative_position di alcuni pin del connettore e sull'assenza della label EN.

**Errori minori:**
- Nel JSON i pin del connettore hanno relative_position non coerenti con l'immagine: tutti i pin visibili di J2 sono sul lato sinistro del simbolo/connettore, mentre pin1 e pin2 sono indicati come right.
- La label topologica EN associata allo switch è visibile nell'immagine ma non è rappresentata nel JSON.

**Punti incerti:**
- La polarità/anodo-cathodo del LED nel JSON appare coerente con il simbolo visibile, ma la verifica dipende dall'interpretazione grafica del simbolo senza ulteriori marcature testuali.
- Lo stato open dello switch è visivamente plausibile dall'immagine, ma lo stato meccanico può essere letto solo dal simbolo statico.

### a02

- Batch: `A`
- Score: `76`
- Decisione: `NEEDS_PATCH`
- Usabile come graph base: `False`
- Spiegazione: Il JSON riconosce quasi tutti i componenti principali visibili: batteria, connettore J3 a 4 pin, resistore, condensatore, tre GND e switch aperto. Molti collegamenti locali sono corretti, inclusi pin 2-resistore, pin 3-condensatore-GND, pin 4-GND e switch verso GND. Tuttavia la batteria è rappresentata con terminali/polarità invertiti e il terminale superiore non è collegato al nodo superiore resistore-switch come nell'immagine; inoltre la label visibile sul nodo del pin 1 è diversa da quella riportata. Il grafo è quindi utilizzabile solo dopo correzioni topologiche.

**Errori maggiori:**
- Il terminale superiore della batteria è visivamente collegato al nodo superiore del resistore e al terminale sinistro dello switch, mentre nel JSON è collegato solo alla label VDD e non a quel nodo.
- Il terminale inferiore della batteria è visivamente collegato al pin 1 del connettore J3, ma nel JSON il collegamento a connector5.1_pin1 è assegnato al terminale positivo della batteria.
- La polarità/denominazione dei terminali della batteria nel JSON appare invertita rispetto al simbolo: il terminale superiore è la piastra lunga e quello inferiore la piastra corta, ma il JSON etichetta il superiore come negative e l'inferiore come positive.

**Errori minori:**
- La label topologica VCC visibile vicino al collegamento della batteria al pin 1 non è rappresentata nel JSON; è presente invece una label VDD collegata al terminale superiore della batteria.

**Punti incerti:**
- La numerazione interna dei pin del connettore è visibile nell'immagine, ma l'associazione geometrica dei terminal_id pin1-pin4 nel JSON non specifica coordinate assolute; la corrispondenza è giudicata tramite i collegamenti dichiarati.
- Il simbolo dello switch è aperto e lo stato open nel JSON è coerente, ma i nomi t1/t2 dei due terminali sono verificabili solo per posizione relativa.

### a03

- Batch: `A`
- Score: `75`
- Decisione: `NEEDS_PATCH`
- Usabile come graph base: `False`
- Spiegazione: Il JSON rappresenta correttamente i componenti principali: connettore J5 a 4 pin, condensatore verso massa dal pin 3, pin 4 a massa, pin 2 tramite resistore al voltmetro, e voltmetro a massa. Le connessioni principali sono quindi in gran parte corrette. Restano però problemi topologici/semantici sulla sorgente a sinistra: la label visibile è VIN sul nodo del pin 1, mentre il JSON introduce VDD sul terminale superiore della batteria/sorgente, non visibile, e non rappresenta VIN.

**Errori maggiori:**
- Il componente verticale a sinistra dell'immagine appare come simbolo di sorgente/alimentazione con terminale inferiore collegato a VIN/J5 pin 1 e terminale superiore non collegato visibilmente; nel JSON è modellato come Battery con polarità negative in alto e positive in basso e con il terminale superiore collegato a una label VDD. La classe sorgente è plausibile, ma polarità/label non sono verificabili e il terminale superiore sembra non collegato nell'immagine.
- Il JSON dichiara un collegamento tra il terminale superiore della batteria/sorgente e una label VDD non visibile nell'immagine. Questo introduce un nodo topologico non riscontrabile visivamente.
- La label topologica VIN visibile accanto al collegamento tra sorgente e J5 pin 1 non è rappresentata nel JSON, mentre il JSON usa VDD su un altro terminale.

**Errori minori:**
- I terminali del voltmetro sono indicati entrambi con relative_position bottom; nell'immagine i due morsetti sono nella parte bassa del misuratore, ma il collegamento sinistro arriva lateralmente al morsetto sinistro e quello destro scende a massa. La posizione è solo parzialmente descrittiva.
- Le relative_position dei pin del connettore J5 non riflettono bene la disposizione visiva dei quattro pin, tutti lungo il lato sinistro/interno del connettore; tuttavia i numeri pin e i collegamenti principali sono coerenti.

**Punti incerti:**
- La polarità esatta del simbolo di sorgente/batteria a sinistra non è chiaramente deducibile dall'immagine senza interpretazione del simbolo; quindi la denominazione positive/negative nel JSON non è valutata come errore critico.
- Non è completamente chiaro se il terminale superiore della sorgente sia intenzionalmente un terminale esterno non mostrato o una connessione non etichettata; nell'immagine non compare però una label VDD.
- La corrispondenza dei due terminali del voltmetro con t1/t2 non può essere verificata nominalmente, ma i collegamenti sinistro a resistore e destro a GND risultano coerenti.

### a04

- Batch: `A`
- Score: `88`
- Decisione: `MINOR_ISSUES`
- Usabile come graph base: `True`
- Spiegazione: Il JSON rappresenta correttamente i componenti principali e quasi tutti i collegamenti visibili: switch verso GND e pin 3, pin 4 a GND, pin 2 al condensatore verso GND, pin 1 alla resistenza e allo strumento, con l'altro terminale dello strumento a GND. Non risultano collegamenti topologici errati gravi. Restano problemi minori su posizioni dei pin del connettore e omissione di label testuali visibili.

**Errori minori:**
- Le posizioni relative dei pin del connettore non sono completamente coerenti: nell'immagine tutti i quattro pin di J15 sono disposti sul lato sinistro del corpo del connettore, mentre nel JSON pin1 e pin2 sono indicati con relative_position 'right'.
- Lo switch è disegnato aperto e il JSON riporta state 'open', ma il campo graph collega comunque i due terminali dello switch alle rispettive reti; questo è accettabile come connettività dei morsetti, ma lo stato aperto richiede cautela nell'interpretazione elettrica.
- Alcune label topologiche/testuali visibili utili all'identificazione, come J15, TEST e VMON, non sono riportate nel JSON.

**Punti incerti:**
- La corrispondenza esatta tra pin fisici del connettore e terminal_id pin1-pin4 nel JSON è coerente con le numerazioni visibili, ma le relative_position non descrivono fedelmente il lato grafico dei pin.
- La polarità del condensatore non è indicata visivamente e non è valutabile.
- Il terminale sinistro dello strumento analogico appare non collegato nell'immagine e non è presente in graph; il JSON usa due terminali, collegando quello destro a GND e quello sinistro alla resistenza, coerente con la topologia visibile ma senza polarità verificabile.

### a05

- Batch: `A`
- Score: `78`
- Decisione: `NEEDS_PATCH`
- Usabile come graph base: `False`
- Spiegazione: Il JSON include quasi tutti i componenti principali e rappresenta correttamente reset, pin 4 a GND, nodo del resistore/meter/LED/GND e GND destro del LED. Tuttavia i collegamenti del trasformatore sono significativamente errati: due terminali risultano non connessi e i pin 1 e 2 del connettore non sono collegati alla bobina come visibile. Per questo il grafo richiede correzioni topologiche.

**Errori maggiori:**
- Il primario del trasformatore visibile a sinistra è collegato ai pin 1 e 2 del connettore, ma nel JSON i terminali transformer28.1_t1 e transformer28.1_t2 risultano non connessi.
- Il pin 2 del connettore è collegato al trasformatore nell'immagine, non direttamente al resistore.
- Il terminale superiore del lato destro del trasformatore è collegato alla linea del pin 1 e al terminale sinistro dello strumento, non al pin 1 tramite il terminale t3 come unico collegamento separato dal meter.

**Errori minori:**
- Il componente diode7.1 è visivamente un LED, ma è classificato genericamente come Diode; la topologia a due terminali resta comunque utilizzabile.
- Le label topologiche/testuali RESET, VAC e PWR visibili nell'immagine non sono rappresentate nel JSON.

**Punti incerti:**
- La corrispondenza esatta tra i terminal_id t1-t4 del trasformatore e le posizioni fisiche delle quattro estremità non è completamente verificabile dal JSON, perché i terminali sono nominati genericamente e le relative_position sono ambigue per due terminali a sinistra e due a destra.
- La polarità anodo/catodo del LED è visibile solo dal simbolo; la classificazione come Diode con anode a sinistra e cathode a destra sembra coerente, ma il JSON non distingue esplicitamente LED.

### a06

- Batch: `A`
- Score: `86`
- Decisione: `MINOR_ISSUES`
- Usabile come graph base: `True`
- Spiegazione: Il JSON rappresenta correttamente quasi tutti i componenti principali e i collegamenti visibili: VIN verso pin 1 di J8, pin 2 verso isolatore/trasformatore e poi resistore e monitor, pin 3 verso condensatore a GND, pin 4 a GND, e terminale inferiore del monitor a GND. Non emergono collegamenti topologici errati nel campo graph. Le criticità sono soprattutto di classificazione/semantica del simbolo VIN e di metadati di posizione dei terminali, con alcune corrispondenze interne non pienamente verificabili.

**Errori minori:**
- Il componente a sinistra è rappresentato con simbolo di sorgente/ingresso VIN, mentre nel JSON è classificato come Battery; la topologia dei terminali principali è comunque compatibile.
- Il connettore J8 ha quattro pin visibili disposti verticalmente sul lato sinistro del corpo, ma nel JSON alcuni pin sono indicati con relative_position destra/sinistra non coerenti con la geometria visibile.
- L'analog meter MON mostra due terminali sul lato sinistro del simbolo, uno con collegamento laterale superiore e uno verso il basso a GND; il JSON assegna entrambi i terminali come relative_position left senza distinguere chiaramente il terminale inferiore.

**Punti incerti:**
- Il terminale sinistro della sorgente VIN prosegue fuori immagine o verso un nodo non mostrato; il JSON lascia battery2.1_negative non connesso, ma non è verificabile come errore dall'immagine ritagliata.
- La corrispondenza esatta tra i terminali interni del trasformatore/isolatore e gli identificativi t1-t4 del JSON non è completamente verificabile perché l'immagine non mostra nomi terminale, solo la topologia dei due lati.
- Il nome topologico VIN è visibile nell'immagine ma non è presente nel JSON come label; è rilevante solo semanticamente e non altera i collegamenti verificati.

### a07

- Batch: `A`
- Score: `78`
- Decisione: `NEEDS_PATCH`
- Usabile come graph base: `False`
- Spiegazione: Il JSON include quasi tutti i componenti visibili: sorgente, trasformatore, resistore, condensatore, lampada/load e due GND. La parte a destra con resistore, condensatore, lampada e masse è in larga parte coerente. Tuttavia i collegamenti del trasformatore e della sorgente AC sono rappresentati male o lasciati aperti: terminali che nell'immagine sono collegati risultano non connessi e altri sono collegati al terminale errato del trasformatore. Per questi errori topologici correggibili il grafo richiede patch.

**Errori maggiori:**
- Il terminale sinistro della sorgente AC è visibilmente collegato al terminale sinistro superiore del trasformatore, ma nel JSON entrambi risultano non collegati.
- Il JSON collega la sorgente AC al terminale sinistro inferiore del trasformatore, mentre l'immagine mostra il collegamento della sorgente al terminale sinistro superiore; il terminale inferiore sinistro del trasformatore non è chiaramente collegato alla sorgente.
- Il terminale destro superiore del trasformatore è visibilmente collegato al resistore in serie, ma nel JSON il resistore è collegato al terminale destro inferiore del trasformatore e transformer28.1_t2 risulta non collegato.

**Errori minori:**
- La sorgente è classificata genericamente come Signal_Source; l'immagine mostra specificamente una sorgente AC. La rappresentazione è comunque parzialmente coerente come sorgente.

**Punti incerti:**
- L'assegnazione esatta dei quattro terminali del trasformatore ai nomi t1, t2, t3, t4 non è visibile nell'immagine; la valutazione dei collegamenti del trasformatore dipende dalle relative_position dichiarate nel JSON, che distinguono solo left/right e non upper/lower.
- Il ramo inferiore/superiore dell'avvolgimento del trasformatore e la corrispondenza precisa dei terminali interni non sono completamente deducibili dal solo simbolo.

### a08

- Batch: `A`
- Score: `70`
- Decisione: `NEEDS_PATCH`
- Usabile come graph base: `False`
- Spiegazione: Il JSON riconosce quasi tutti i componenti principali visibili: sorgente SIG, trasformatore, meter, resistore e due GND. La parte secondaria con meter, resistore e massa è in gran parte coerente. Tuttavia lascia non connessi terminali visibilmente appartenenti al circuito sul lato sorgente/trasformatore e presenta un collegamento sorgente-trasformatore non chiaramente coerente con la topologia mostrata. Il grafo richiede correzioni topologiche prima di essere usato come base affidabile.

**Errori maggiori:**
- Il terminale sinistro della sorgente di segnale è collegato visivamente a un filo che prosegue verso sinistra, ma nel JSON è lasciato non connesso.
- Il primario del trasformatore appare collegato alla linea orizzontale proveniente dalla sorgente di segnale sul lato sinistro e al ritorno inferiore del circuito, ma due terminali del trasformatore sono lasciati non connessi nel JSON.
- Il JSON collega la sorgente di segnale direttamente al terminale t3 del trasformatore, ma nell'immagine la sorgente è sul lato sinistro del trasformatore, mentre il secondario destro va verso il meter e il ramo con resistore/GND.

**Errori minori:**
- Le posizioni relative dei quattro terminali del trasformatore nel JSON sono poco distinguibili: due terminali sono marcati left e due right senza indicazione alto/basso, rendendo ambigua la verifica dei collegamenti visibili.

**Punti incerti:**
- Non è completamente verificabile dall'immagine quale dei terminali numerati t1-t4 del trasformatore corrisponda a ciascun estremo fisico alto/basso dei due avvolgimenti.
- Il filo che esce a sinistra della sorgente SIG termina al margine dell'immagine; non è chiaro se rappresenti un terminale esterno aperto o una connessione fuori campo.

### a09

- Batch: `A`
- Score: `91`
- Decisione: `PASS`
- Usabile come graph base: `True`
- Spiegazione: Il JSON rappresenta correttamente quasi tutti i componenti principali e le connessioni visibili: batteria, fusibile, connettore a 5 pin, condensatore, interruttore aperto, resistore, LED, lampada e GND. La principale discrepanza topologica è il terminale inferiore della lampada lasciato non connesso invece che collegato al GND visibile. Sono presenti anche piccole incoerenze sulle posizioni relative di alcuni pin del connettore.

**Errori minori:**
- Le posizioni relative dei pin del connettore non sono tutte coerenti: nell'immagine i cinque pin di J1 sono sul lato destro del simbolo, mentre nel JSON pin1 e pin5 sono indicati come left.
- Il JSON include un simbolo GND separato non collegato, corrispondente probabilmente al riferimento sotto la lampada; la sua associazione al terminale della lampada è assente nel grafo.
- Il JSON segnala lamp13.1_t2 come non connesso, ma nell'immagine il terminale inferiore della lampada è collegato a un simbolo GND.

**Punti incerti:**
- La polarità esatta del LED non è marcata con etichette testuali nell'immagine; il simbolo suggerisce orientamento, ma la verifica anodo/catodo resta limitata alla lettura grafica.
- L'associazione esatta fra i simboli GND separati del disegno e gli identificativi gnd9.x del JSON non è sempre direttamente verificabile, anche se la topologia complessiva è quasi interamente coerente.

### a10

- Batch: `A`
- Score: `94`
- Decisione: `PASS`
- Usabile come graph base: `True`
- Spiegazione: Il JSON rappresenta correttamente i componenti principali visibili: batteria, switch aperto, connettore J1 a 4 pin, resistore, lampada, LED e riferimenti GND. I collegamenti nel campo graph corrispondono alla topologia disegnata: batteria negativa a GND, batteria positiva allo switch, switch al pin 1, pin 2 al resistore e poi LED a GND, pin 3 alla lampada e poi GND, pin 4 a GND. Restano solo piccole imprecisioni sulle posizioni relative dei terminali e una lieve ambiguità sulla polarità del LED.

**Errori minori:**
- Le posizioni relative dei pin del connettore nel JSON non sono pienamente coerenti con l'immagine: i quattro pin di J1 sono disegnati come terminali sul lato destro del corpo del connettore, mentre nel JSON pin1 e pin4 sono indicati come 'left'.
- Alcune posizioni terminali sono semplificate o non perfettamente aderenti al disegno, ad esempio il LED è disegnato verticalmente con collegamento superiore dal resistore e inferiore a GND, ma la verifica precisa di anodo/catodo dalla sola immagine resta parzialmente dipendente dal simbolo.

**Punti incerti:**
- La polarità esatta del LED è visibile come simbolo di diodo/LED, ma l'associazione anode/cathode ai terminali JSON non è completamente verificabile senza ambiguità dalla sola resa grafica.
- Lo stato aperto dello switch è coerente con il simbolo visibile, ma il contatto mobile e i terminali fisici non permettono una verifica più fine oltre alla topologia aperta rappresentata.
