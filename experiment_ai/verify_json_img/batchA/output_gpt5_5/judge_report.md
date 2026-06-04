# Report verifica immagine ↔ Graph JSON

Generato: 2026-06-04 11:47:41

## Tabella sintetica

| Circuito | Batch | Score | Fedeltà | Critici | Maggiori | Minori | Usabile come graph base |
|---|---:|---:|---|---:|---:|---:|---|
| a01 | A | 94 | VERY_HIGH | 0 | 0 | 3 | True |
| a02 | A | 89 | HIGH | 0 | 1 | 2 | True |
| a03 | A | 67 | MEDIUM | 1 | 4 | 2 | True |
| a04 | A | 95 | VERY_HIGH | 0 | 0 | 2 | True |
| a05 | A | 94 | VERY_HIGH | 0 | 0 | 3 | True |
| a06 | A | 86 | HIGH | 0 | 2 | 3 | True |
| a07 | A | 78 | HIGH | 0 | 3 | 2 | True |
| a08 | A | 67 | MEDIUM | 1 | 4 | 2 | True |
| a09 | A | 86 | HIGH | 0 | 2 | 3 | True |
| a10 | A | 93 | VERY_HIGH | 0 | 0 | 3 | True |

## Dettagli per circuito

### a01

- Batch: `A`
- Score: `94`
- Fedeltà: `VERY_HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il Graph JSON rispecchia molto bene la topologia visibile: sono presenti connettore a 4 pin, switch aperto verso GND, due resistori, LED, lampada e i tre riferimenti GND. I collegamenti principali da J2 ai due rami LED/lampada e ai GND sono corretti. Restano solo piccole incertezze su posizioni relative/polarità e sulla semantica dello switch aperto, senza compromettere la struttura del grafo.

**Errori minori:**
- Nel JSON i pin del connettore hanno relative_position incoerenti: pin1 e pin2 sono indicati a destra mentre nell'immagine i terminali di J2 escono a destra ma i fori/pin sono sul lato sinistro del simbolo; pin3 e pin4 sono indicati a sinistra pur essendo collegati verso sinistra/giù in modo parzialmente ambiguo. Questo non altera sostanzialmente la topologia.
- Il JSON assegna anodo a sinistra e catodo a destra per il LED; la direzione del simbolo nell'immagine è compatibile, ma la verifica puntuale della polarità può essere leggermente ambigua per la resa grafica.
- Lo switch è dichiarato open e l'immagine mostra un contatto aperto; tuttavia il campo graph collega comunque ciascun terminale al proprio nodo esterno, non rappresentando esplicitamente l'assenza di conduzione interna. Come descrizione topologica dei fili esterni è comunque coerente.

**Punti incerti:**
- La numerazione dei pin del connettore J2 è visibile e il JSON la rappresenta come pin1-pin4; l'orientamento relativo dei terminali nel JSON è però solo descrittivo e non sempre verificabile con precisione dall'immagine.
- L'associazione tra gli instance_id dei due resistori e le loro posizioni superiore/inferiore non è semanticamente nominata nel JSON; risulta comunque coerente tramite i collegamenti del graph.
- Il nome di classe Lamp per il simbolo della lampada è coerente, ma il simbolo include dettagli grafici interni non rappresentati nei terminali JSON, senza impatto topologico.

### a02

- Batch: `A`
- Score: `89`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riconosce correttamente quasi tutti i componenti principali e gran parte della topologia: connettore a 4 pin, resistore verso pin 2, condensatore tra pin 3 e GND, pin 4 a GND e switch aperto verso GND. La principale discrepanza è l'inversione topologica/polarità della batteria nel grafo rispetto al simbolo visibile, che assegna il nodo superiore al terminale negativo e il pin 1 al positivo. Per il resto la struttura è una buona base correggibile.

**Errori maggiori:**
- Il JSON collega il terminale negativo della batteria direttamente sia al terminale superiore del resistore sia al terminale sinistro dello switch. Nell'immagine il nodo superiore comune unisce batteria, resistore e lato sinistro dello switch, ma la polarità della batteria nel JSON sembra invertita rispetto al simbolo visibile: il terminale superiore del simbolo batteria è la piastra positiva e va al nodo superiore, mentre il terminale inferiore va al connettore J3 pin 1.

**Errori minori:**
- Le posizioni relative dei pin del connettore non sono pienamente coerenti con l'immagine: i pin del connettore J3 sono disposti verticalmente sul lato destro del corpo, mentre nel JSON alcuni sono dichiarati left e altri right.
- Il connettore visibile è etichettato J3 nell'immagine, mentre nel JSON è presente solo come Connector senza conservare tale label visibile.

**Punti incerti:**
- La corrispondenza esatta tra i terminali t1/t2 del resistore e i capi fisici è deducibile solo dalla posizione relativa riportata nel JSON, non da nomi terminali standardizzati nell'immagine.
- Lo stato aperto dello switch è coerente con il simbolo visibile, ma la denominazione t1/t2 dei suoi due terminali non è marcata nell'immagine.

### a03

- Batch: `A`
- Score: `67`
- Fedeltà: `MEDIUM`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riconosce diversi elementi principali del circuito di controllo, inclusi due transistor, resistori, RV1, bobina, diodo, sorgente e lampada, e molte connessioni centrali sono recuperabili. Tuttavia scambia la LDR con una batteria, lascia non connesso il negativo della batteria principale, modella il relè come induttore e switch separati con collegamenti del carico incompleti, e classifica il diodo come LED. La fedeltà topologica è quindi parziale ma ancora utilizzabile come base di correzione.

**Errori critici:**
- Il relè visibile nell'immagine, composto da bobina e contatti di commutazione, è rappresentato nel JSON come un induttore isolato più uno switch separato non collegato correttamente alla bobina e al circuito di carico. Questo altera una parte importante della topologia tra circuito di controllo e circuito di potenza.

**Errori maggiori:**
- Il componente LDR visibile nell'immagine non è rappresentato come LDR/fotoresistenza nel JSON; è stato modellato come una batteria aggiuntiva.
- Il JSON include una seconda batteria che non corrisponde a un secondo generatore DC separato nell'immagine; quella posizione corrisponde visivamente alla LDR.
- Il nodo inferiore comune dell'alimentazione DC è associato nel JSON al negativo della batteria sbagliata, lasciando non connesso il negativo della batteria principale.
- Il contatto del relè nel circuito di carico è incompleto: il ramo con sorgente AC, contatto RL1 e lampada dovrebbe formare un circuito chiuso, ma nel JSON una estremità della sorgente e una estremità dello switch risultano non connesse.

**Errori minori:**
- Il diodo D1 è rappresentato come LED; il simbolo visibile è un diodo generico, non un LED.
- Il resistore variabile RV1 è rappresentato con due terminali, mentre nell'immagine è visibile anche il cursore collegato al rail inferiore; tuttavia il cursore sembra cortocircuitato al terminale inferiore, quindi l'impatto topologico è limitato.

**Punti incerti:**
- La polarità esatta del diodo D1 è visibile solo parzialmente e non viene usata come errore principale.
- L'associazione dei nomi terminali t1/t2 per resistori, bobina, lampada e sorgente non è verificabile con certezza dall'immagine.
- Lo stato meccanico del contatto del relè è rappresentato nel JSON come switch chiuso, ma nell'immagine il simbolo del contatto non consente una verifica certa dello stato operativo.

### a04

- Batch: `A`
- Score: `95`
- Fedeltà: `VERY_HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il Graph JSON rappresenta molto fedelmente il circuito visibile: sono presenti sorgente di segnale, batteria, transistor NPN, cinque resistori, tre condensatori e GND. Le reti principali corrispondono all'immagine: nodo superiore di alimentazione, massa comune inferiore, rete di base con condensatore di ingresso e partitore, collettore con resistore verso alimentazione e condensatore di uscita, emettitore con resistore e condensatore verso massa. Restano solo lievi limiti semantici su polarità/etichette, senza compromissione topologica.

**Errori minori:**
- Alcuni condensatori mostrano una polarità visibile nell'immagine, mentre nel JSON sono modellati genericamente come Capacitor con terminali t1/t2; la topologia dei collegamenti resta comunque coerente.
- Le etichette visibili dei nodi/componenti principali non sono preservate nel JSON, anche se le classi dei componenti e i collegamenti risultano sostanzialmente corretti.

**Punti incerti:**
- L'associazione esatta tra gli identificativi generici dei resistori nel JSON e le sigle visive R1-R5 è deducibile dalla posizione/topologia ma non è esplicitata nel JSON.
- La polarità precisa dei condensatori rispetto ai terminali t1/t2 non è completamente verificabile dal JSON perché non sono presenti metadati di polarità.

### a05

- Batch: `A`
- Score: `94`
- Fedeltà: `VERY_HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON rappresenta correttamente i componenti principali visibili: connettore a 4 pin, switch TEST, più simboli GND, condensatore, resistore e misuratore analogico. I collegamenti principali del graph corrispondono all'immagine: pin 1 tramite resistore al misuratore, pin 2 al condensatore verso massa, pin 3 allo switch verso massa, pin 4 a massa, e terminale destro del misuratore a massa. Le discrepanze sono minori e riguardano soprattutto dettagli di label/posizione dei terminali, non la topologia principale.

**Errori minori:**
- Il misuratore analogico visibile è etichettato VMON nell'immagine, mentre nel JSON è presente solo come Analog_Meter senza riportare la label visibile.
- I terminali del misuratore sono descritti entrambi come bottom; nell'immagine i due punti di connessione sono nella parte inferiore del simbolo, ma solo quello destro è effettivamente cablato verso massa e quello sinistro appare non collegato.
- Le posizioni relative dei pin del connettore J15 nel JSON sono semplificate e non riflettono perfettamente la disposizione grafica verticale dei pin visibile nell'immagine.

**Punti incerti:**
- La numerazione pin del connettore J15 è coerente visivamente con le etichette 1-4, ma l'associazione interna ai terminal_id dipende dalla convenzione adottata nel JSON.
- Lo stato del pulsante/switch TEST appare aperto nell'immagine ed è indicato open nel JSON; la verifica è visiva ma non implica comportamento elettrico.

### a06

- Batch: `A`
- Score: `86`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riconosce quasi tutti i componenti principali visibili e la topologia dei collegamenti è nel complesso fedele: sorgente, rete di ingresso, partitore di base, transistor, rete di collettore, emettitore con bypass, accoppiamento di uscita e carico risultano collegati coerentemente. Le discrepanze principali riguardano la perdita di label topologiche visibili sui terminali di alimentazione e uscita e la mancata codifica di alcune semantiche/polarità visibili o parzialmente visibili. Non emergono collegamenti del graph gravemente incompatibili con l'immagine.

**Errori maggiori:**
- Il terminale superiore di alimentazione indicato visivamente come Vcc è rappresentato nel JSON solo come Terminal generico, senza conservare la semantica topologica visibile della label.
- Il terminale inferiore dell'emettitore indicato visivamente come VEE/0 V è rappresentato nel JSON solo come Terminal generico, senza conservare la semantica topologica visibile della label.

**Errori minori:**
- Il terminale di uscita a destra è rappresentato come Terminal generico; la polarità/label visiva dell'uscita non è esplicitamente conservata.
- I simboli GND visibili sono rappresentati come istanze separate; questo è accettabile graficamente ma non esplicita che appartengano alla stessa reference topologica.
- Alcuni condensatori polarizzati appaiono con indicazione grafica o label di componente, ma il JSON usa terminali generici senza polarità.

**Punti incerti:**
- La polarità effettiva dei condensatori non è completamente verificabile dal solo schema per tutti i terminali e il JSON non la codifica.
- L'identificazione esatta di quale resistore JSON corrisponda a ciascun resistore fisico è dedotta dalla posizione e dai collegamenti, non dai valori ignorati.

### a07

- Batch: `A`
- Score: `78`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riconosce quasi tutti i componenti principali e molte connessioni secondarie, inclusi switch, connettore, resistore, misuratore, LED e masse. La parte più problematica è il trasformatore: il lato sinistro visibilmente collegato a J7 pin 1 e al nodo del resistore/J7 pin 2 è lasciato non connesso, mentre vengono usati terminali del lato destro. La topologia rimane in gran parte recuperabile ma richiede correzioni localizzate importanti.

**Errori maggiori:**
- Il primario del trasformatore visibile a sinistra è collegato tra il pin 1 del connettore e il nodo del resistore/pin 2; nel JSON i terminali transformer28.1_t1 e transformer28.1_t2 risultano non connessi.
- Il JSON collega il pin 1 del connettore al terminale transformer28.1_t3, che appare invece appartenere al lato destro del trasformatore, mentre nell'immagine il pin 1 è collegato al lato sinistro del trasformatore.
- Il JSON collega il resistore direttamente al pin 2 del connettore ma non include il collegamento del nodo del resistore al terminale sinistro del trasformatore visibile sull'immagine.

**Errori minori:**
- I terminali del connettore sono assegnati con relative_position mista destra/sinistra, mentre nell'immagine i quattro pin di J7 sono disposti sul lato sinistro del simbolo del connettore con collegamenti verso l'esterno.
- Il misuratore analogico è rappresentato come Analog_Meter ma la label visibile VAC non è riportata come semantica; questo non altera molto la topologia.

**Punti incerti:**
- La denominazione anode/cathode del LED nel JSON non è verificabile con assoluta certezza dall'immagine senza assumere convenzioni esterne; topologicamente i due terminali risultano comunque collegati ai nodi corretti.
- L'assegnazione esatta dei terminali t1-t4 del trasformatore non è etichettata nell'immagine; l'errore valutato riguarda la mancata connessione del lato sinistro e non il nome funzionale dei terminali.

### a08

- Batch: `A`
- Score: `67`
- Fedeltà: `MEDIUM`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riconosce quasi tutti i componenti principali e gran parte della topologia centrale: sorgente, LED, transistor, condensatore e resistori sono presenti e molti nodi sono coerenti. Tuttavia separa le masse in due reti distinte, omette le label topologiche visibili IN, Trigger e LED, e semplifica R1 come resistore a due terminali nonostante il simbolo variabile. La struttura resta recuperabile, ma la fedeltà topologica è solo parziale.

**Errori critici:**
- Il JSON collega il terminale inferiore della sorgente di segnale a un GND separato, mentre nell'immagine il riferimento a massa della sorgente è sullo stesso nodo di massa inferiore comune che comprende anche il condensatore e il resistore inferiore.

**Errori maggiori:**
- Le etichette topologiche visibili Trigger, IN e LED non sono rappresentate come terminali/net label nel JSON.
- Il nodo del terminale inferiore del LED e del collettore del transistor dovrebbe includere anche la label visibile LED, assente dal JSON.
- Il nodo di trigger che unisce condensatore, resistore superiore variabile e ingresso della resistenza verso la base non include la label Trigger visibile.
- Il componente R1 nell'immagine è disegnato come resistore variabile/potenziometro o trimmer con terminale laterale/slider, mentre nel JSON è rappresentato come semplice resistore a due terminali.

**Errori minori:**
- La polarità anodo/catodo del LED nel JSON è plausibile rispetto al disegno, ma l'immagine non rende tutti i dettagli terminali verificabili con assoluta certezza.
- Il JSON usa identificativi generici e non conserva i designator visibili dei componenti, pur mantenendo in gran parte le classi dei componenti principali.

**Punti incerti:**
- L'immagine mostra R1 come resistore variabile/trimmer; non è completamente verificabile dal solo JSON se la pipeline intendesse semplificarlo intenzionalmente come resistore a due terminali.
- La distinzione tra i due simboli GND potrebbe essere trattata graficamente come riferimento comune implicito; nel campo graph però non sono connessi, quindi la rete risulta separata.

### a09

- Batch: `A`
- Score: `86`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riconosce quasi tutti i componenti principali e gran parte della topologia: batteria, fusibile, connettore, switch, resistore, LED, lampada, condensatore e GND. La discrepanza principale è il nodo del condensatore, che nel JSON viene unito al nodo di J1 pin4/R3 mentre nell'immagine il terminale inferiore del condensatore va a GND. Inoltre manca il collegamento della lampada a GND. Nel complesso il grafo resta una buona base correggibile.

**Errori maggiori:**
- Il condensatore è collegato visivamente tra il nodo del pin 2 di J1 e il nodo del pin 4 di J1, con il terminale inferiore a GND; nel JSON il terminale inferiore del condensatore è unito anche al nodo di J1 pin4 e al resistore, mentre visivamente il GND del condensatore è separato dal nodo orizzontale di pin4/resistore.
- Il terminale inferiore della lampada è collegato visivamente a GND, ma nel JSON risulta non connesso.

**Errori minori:**
- Sono presenti più istanze GND separate, coerenti come simboli visibili, ma una istanza GND extra risulta non connessa.
- Le relative_position dei pin del connettore sono poco coerenti: nel disegno tutti i pin di J1 sono sul lato sinistro del connettore grafico, mentre nel JSON alcuni sono indicati a destra.
- Il JSON segnala gnd9.5_t1 come terminale non connesso; questo corrisponde a un GND extra non agganciato alla topologia.

**Punti incerti:**
- L'immagine mostra il simbolo dell'interruttore aperto; lo stato open nel JSON appare coerente, ma la verifica non dipende da dettagli funzionali.
- La polarità esatta del LED è visibile come simbolo, ma l'associazione anode/cathode nel JSON non è completamente verificabile senza interpretazione del verso del simbolo.

### a10

- Batch: `A`
- Score: `93`
- Fedeltà: `VERY_HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il Graph JSON rappresenta molto fedelmente i componenti visibili e i collegamenti principali: batteria a switch, switch a pin 1 del connettore, pin 2 a resistore e LED verso GND, pin 3 a lampada verso GND, pin 4 a GND, e negativo batteria a GND. Non risultano collegamenti topologici mancanti o extra nel campo graph. Le discrepanze sono limitate a dettagli accessori di orientamento dei terminali e verificabilità della polarità.

**Errori minori:**
- Gli orientamenti relativi dei pin del connettore sono parzialmente incoerenti: nell'immagine tutti i pin di J1 si collegano graficamente dal lato destro verso i rispettivi fili esterni o dal lato sinistro per il pin 4, mentre nel JSON pin1 e pin4 sono indicati left e pin2/pin3 right. Questo non altera la topologia del campo graph.
- Il JSON indica lo switch come open; l'immagine mostra effettivamente un contatto aperto, ma lo stato non è un collegamento nel campo graph e quindi resta una semantica visiva accessoria.
- La polarità dell'LED nel JSON è plausibile rispetto al simbolo, ma la verifica precisa anodo/catodo dal solo disegno può essere parzialmente ambigua.

**Punti incerti:**
- La corrispondenza esatta tra i terminali anode/cathode dell'LED e la geometria del simbolo è solo parzialmente verificabile dall'immagine.
- Gli orientamenti relativi left/right dei pin del connettore non sono essenziali per la topologia e sono in parte ambigui rispetto al disegno.
