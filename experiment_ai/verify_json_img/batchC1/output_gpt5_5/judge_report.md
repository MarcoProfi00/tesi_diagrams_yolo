# Report verifica immagine ↔ Graph JSON

Generato: 2026-06-03 23:38:50

## Tabella sintetica

| Circuito | Batch | Score | Fedeltà | Critici | Maggiori | Minori | Usabile come graph base |
|---|---:|---:|---|---:|---:|---:|---|
| c01 | C1 | 96 | VERY_HIGH | 0 | 0 | 2 | True |
| c02 | C1 | 83 | HIGH | 0 | 3 | 3 | True |
| c03 | C1 | 88 | HIGH | 0 | 2 | 3 | True |
| c04 | C1 | 88 | HIGH | 0 | 2 | 3 | True |
| c05 | C1 | 80 | HIGH | 0 | 4 | 3 | True |
| c06 | C1 | 76 | HIGH | 0 | 3 | 3 | True |
| c07 | C1 | 78 | HIGH | 0 | 3 | 3 | True |
| c08 | C1 | 73 | MEDIUM | 1 | 5 | 3 | True |
| c17 | C1 | 86 | HIGH | 0 | 2 | 3 | True |
| c18 | C1 | 80 | HIGH | 0 | 3 | 2 | True |

## Dettagli per circuito

### c01

- Batch: `C1`
- Score: `96`
- Fedeltà: `VERY_HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il Graph JSON riproduce molto fedelmente componenti e collegamenti principali visibili: IC 555 con pin numerati, tre resistori, tre condensatori, LED, GND e terminale di alimentazione. Le net principali corrispondono all'immagine: pin 4 e 8 al nodo superiore, pin 1 al nodo inferiore/GND, pin 2 e 6 uniti con C1 e R2, pin 7 tra R1 e R2, pin 3 verso R3 e LED, pin 5 verso C2, C3 tra nodo superiore e inferiore. Restano solo lievi limiti semantici sul terminale di alimentazione e sulla conservazione della label visibile.

**Errori minori:**
- Il terminale di alimentazione superiore è descritto nel JSON come Terminal con relative_position bottom; è una scelta non perfettamente aderente al simbolo visivo, ma non altera la topologia.
- Il JSON rappresenta correttamente il terminale di alimentazione come Terminal, ma non conserva la label topologica visibile di alimentazione positiva.

**Punti incerti:**
- La polarità fisica del LED è graficamente indicata dal simbolo, ma l'associazione esatta anode/cathode nel JSON non è completamente verificabile senza assumere convenzioni esterne; il collegamento topologico serie resistore-LED-verso nodo inferiore risulta comunque coerente.
- Le polarità dei condensatori non sono valutate perché nell'immagine non risultano chiaramente marcate come polarizzati.

### c02

- Batch: `C1`
- Score: `83`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riconosce quasi tutti i componenti principali e la maggior parte delle reti visibili: alimentazione superiore/inferiore, pin dell'NE555, R1/S1, C1, C2, R4/R5, LED e resistori sono in gran parte presenti. Le principali discrepanze riguardano la classificazione di C1 come polarizzato, la rappresentazione incompleta del resistore variabile R5 e una probabile inversione/ambiguità della polarità e connessione del LED D1. Nel complesso la topologia è abbastanza fedele e utilizzabile come base di correzione.

**Errori maggiori:**
- C1 è disegnato come condensatore non polarizzato, mentre nel JSON è classificato come Polarized_Capacitor con terminali positive/negative.
- Il terminale inferiore del LED D1 dovrebbe essere collegato alla linea inferiore comune, non alla stessa rete del pin 6, del pin 7 e del nodo tra R4/R5/C2.
- Il potenziometro/variabile R5 è rappresentato solo come resistore a due terminali e collegato in serie con R4; il collegamento del cursore visibile non è modellato come terminale separato.

**Errori minori:**
- Il simbolo della batteria è presente e con polarità visibile, ma il JSON usa solo una classe Battery generica senza conservare eventuali etichette visive del componente.
- Le posizioni relative top/bottom/left/right di alcuni resistori verticali/orizzontali sono plausibili ma non sempre verificabili in modo univoco dall'immagine.
- L'IC è modellato con posizioni terminali aggregate per lato; i numeri di pin sono presenti e in gran parte coerenti, ma la disposizione fisica nel JSON non distingue pienamente l'ordine verticale dei pin sul lato destro.

**Punti incerti:**
- La polarità effettiva dei LED è dedotta dal simbolo visibile ma la qualità dell'immagine rende non completamente agevole distinguere anodo e catodo per entrambi.
- Il simbolo del pulsante S1 mostra due contatti su un ramo laterale; il JSON lo rappresenta come due terminali, ma lo stato aperto/chiuso non è esplicitato nel graph.
- Il contatto visibile vicino al nodo di C2/R4/D1 può essere interpretato come incrocio o giunzione; dall'immagine appare un nodo, ma la sovrapposizione grafica può generare ambiguità locale.

### c03

- Batch: `C1`
- Score: `88`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il Graph JSON riproduce bene la struttura principale: rete di ingresso con condensatore, diodo e resistori, transistor verso massa, IC con pin numerati, rete di temporizzazione, uscita con resistore e condensatore verso massa. Le connessioni principali del campo graph sono in larga parte coerenti con i fili visibili. Le discrepanze più rilevanti riguardano la classificazione/polarità di vari condensatori non polarizzati e la perdita delle etichette semantiche dei terminali esterni. Nel complesso il grafo è una buona base topologica, con errori localizzati.

**Errori maggiori:**
- Diversi condensatori non polarizzati visibili nell'immagine sono classificati nel JSON come Polarized_Capacitor. Questo riguarda i condensatori attorno all'IC e all'uscita; la topologia dei due terminali resta per lo più utilizzabile, ma la classe e la polarità non sono coerenti con il simbolo visivo.
- Il JSON unisce il terminale inferiore del condensatore di accoppiamento di ingresso direttamente al terminale di ingresso, mentre nell'immagine il condensatore è in serie tra il terminale di ingresso e il nodo con diodo/resistore; non è visibile un filo diretto che cortocircuiti i due lati del condensatore.

**Errori minori:**
- La polarità del condensatore di ingresso è rappresentata con positive a sinistra e negative a destra; il simbolo mostra un segno di polarità sul lato sinistro, quindi la polarità sembra coerente, ma l'identificazione dei terminali nel JSON non è completamente verificabile solo dagli ID.
- Le etichette topologiche visibili Signal in, Vout e alimentazione superiore sono rappresentate come terminali generici senza nomi semantici espliciti.
- Il JSON include un solo componente GND, mentre l'immagine mostra una barra di massa comune con simbolo GND esplicito; la net di massa è comunque sostanzialmente rappresentata.

**Punti incerti:**
- L'immagine mostra terminali/etichette esterne, ma il JSON usa terminal26.x senza display_name; l'associazione esatta di ciascun terminale esterno è dedotta dalla posizione e dai collegamenti.
- Non tutti i numeri di pin dell'IC sono graficamente leggibili con uguale chiarezza, anche se quelli principali riportati nel JSON sembrano coerenti con le posizioni visibili.
- La distinzione tra condensatori polarizzati e non polarizzati è visibile per alcuni simboli, ma l'automatismo ha usato una classe polarizzata uniforme per più condensatori.

### c04

- Batch: `C1`
- Score: `88`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riconosce quasi tutti i componenti principali e gran parte delle reti visibili: due NE555, resistori, diodo, condensatori principali, alimentazione, massa e speaker. La topologia generale è buona, inclusi i nodi di alimentazione, massa, reti dei pin 6/2 e collegamento allo speaker. La discrepanza più rilevante riguarda il ramo del pin 5 del secondo IC e il collegamento del resistore proveniente dal pin 3 del primo IC, dove manca un condensatore visibile e la rete risulta rappresentata in modo errato. Rimane comunque una base grafica utilizzabile per correzioni.

**Errori maggiori:**
- Il condensatore collegato al pin 5 del secondo IC è visibile nell'immagine ma non è rappresentato come componente separato nel JSON; al suo posto il pin 5 del secondo IC è collegato direttamente a un resistore.
- Il resistore di collegamento tra uscita del primo IC e pin 5 del secondo IC è rappresentato in modo incompleto/errato: nell'immagine collega il pin 3 del primo IC al nodo inferiore che poi raggiunge il pin 5 del secondo IC attraverso il ramo visibile, mentre nel JSON il resistore22.3 è spezzato come collegamento diretto tra pin 3 del primo IC e pin 5 del secondo IC senza includere correttamente il nodo inferiore condiviso.

**Errori minori:**
- Alcuni condensatori sono classificati come Polarized_Capacitor anche dove il simbolo non mostra chiaramente polarità o è un condensatore non polarizzato nell'immagine.
- Entrambi i terminali dello speaker sono indicati con relative_position left; la topologia è comunque sostanzialmente corretta.
- I due integrati sono entrambi etichettati come IC1 nel disegno, mentre nel JSON sono distinti come integrated_circuit11.1 e integrated_circuit11.2; la distinzione topologica è corretta ma la semantica visibile è ambigua.

**Punti incerti:**
- La polarità del diodo nel JSON sembra plausibile rispetto al simbolo, ma l'orientamento anodo/catodo non è completamente verificabile senza ambiguità dall'immagine raster.
- Le etichette funzionali dei pin degli IC non sono valutate; sono considerati solo i numeri di pin visibili.
- La classificazione polarizzata/non polarizzata di alcuni condensatori è parzialmente ambigua nella resa grafica.

### c05

- Batch: `C1`
- Score: `80`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riconosce quasi tutti i componenti principali e rappresenta bene la catena 555, 4026, resistori di segmento e display. Tuttavia contiene un errore topologico importante nella zona tra OUT del 555 e i pin sinistri del 4026, dove unisce indebitamente CLK, RST, INH e GND, e lascia non collegato il terminale superiore del resistore verso +Vcc. La parte display tramite sette resistori è invece sostanzialmente fedele.

**Errori maggiori:**
- Il terminale superiore del resistore di sinistra collegato a +Vcc nell'immagine risulta non collegato nel graph.
- Il pin di uscita del 555 è collegato al pin CLK del 4026 nell'immagine, ma nel JSON è unito anche a GND e ad altri pin del 4026.
- Il pin 15 del 4026 è collegato a GND nell'immagine, ma il JSON lo mette nella stessa net del pin 3 OUT del 555 e dei pin 2 e 1 del 4026.
- I pin inferiori 8, 14, 4 e 5 del 4026 sono tutti uniti a GND nel JSON, mentre nell'immagine solo 8, 14 e 4 sono sul nodo GND; il pin 5 è collegato localmente al pin 4 ma non mostra connessione diretta al simbolo GND se non tramite quel tratto comune ambiguo.

**Errori minori:**
- Il display a sette segmenti è modellato come Integrated_Circuit invece che come display dedicato, anche se il subtype e i pin di segmento sono presenti.
- Alcune liste del graph non sono perfettamente simmetriche per la stessa net, ad esempio integrated_circuit11.2_bottom_1 non elenca bottom_4 mentre gnd9.3_t1 lo elenca.
- Le label topologiche +Vcc visibili nell'immagine non sono rappresentate come terminali o nodi dedicati nel JSON; la connessione tra pin 4 e 8 del 555 e tra pin 3 e 16 del 4026 è però parzialmente catturata come net interne.

**Punti incerti:**
- La polarità del condensatore sul nodo dei pin 2/6 del 555 è visibile graficamente, ma il JSON usa terminali generici senza polarità; non è valutata come errore topologico principale.
- Il collegamento esatto del pin 5 inferiore del 4026 al nodo GND è graficamente poco chiaro per la posizione della linea orizzontale inferiore.
- I pin label del display a sette segmenti sono coerenti con le lettere visibili, ma l'ordine fisico dei terminali può essere verificato solo parzialmente dall'immagine.

### c06

- Batch: `C1`
- Score: `76`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riconosce quasi tutti i componenti principali e riproduce bene i sette collegamenti IC-resistori-display e le masse del display e dei pin inferiori 8/14. La parte sinistra del circuito attorno a pulsante, resistore, Vdd/CLK e pin 1/2/3/15/16 del CD4026 contiene però nodi uniti in modo errato, con il pin 3 collegato a Vdd nel JSON e il nodo del pulsante/resistore unito a pin che nell'immagine sono su altri rami. La struttura complessiva resta comunque recuperabile come base.

**Errori maggiori:**
- Il nodo del pulsante e del resistore a sinistra è collegato nel JSON a più pin sinistri dell'IC, mentre nell'immagine il nodo CLK esterno arriva al pin 3 e al resistore/pulsante, non ai pin 15, 2 e 1.
- Il JSON collega il pin 3 dell'IC, il pin 16 e il terminale superiore del pulsante nello stesso nodo, ma nell'immagine il pin 3 è sul nodo CLK laterale, mentre il pin 16/Vdd e il lato superiore del pulsante appartengono al nodo di alimentazione superiore.
- Il collegamento di massa dei pin 8 e 14 dell'IC è rappresentato, ma i pin 15, 2 e 1 risultano nel JSON tutti uniti al nodo del pulsante/resistore e a una GND, mentre nell'immagine almeno il pin 15 è collegato al simbolo GND laterale e i pin 2 e 1 seguono il bus verticale disegnato, non il nodo del pulsante.

**Errori minori:**
- Il display a sette segmenti è modellato come Integrated_Circuit; la topologia dei terminali è utilizzabile, ma la classe non descrive precisamente il simbolo visibile.
- Il JSON rappresenta sette resistori di segmento separati; nell'immagine sono visibili sette rami resistivi verso i segmenti, anche se una nota testuale del disegno può renderne ambigua la conta automatica.
- Il JSON segnala come non connessi i terminali bottom_3 e bottom_4 dell'IC; nell'immagine questi pin terminano con simboli di non connessione, quindi l'avviso non è grave ma indica una semantica non esplicitata come NC.

**Punti incerti:**
- La numerazione e le etichette funzionali dei pin del CD4026 sono leggibili nell'immagine, ma la verifica non deduce alcuna funzione dai numeri di pin.
- Lo stato aperto/chiuso del pulsante S1 è rappresentato come simbolo di pulsante/interruttore, ma il JSON non codifica uno stato; ciò non è valutato come errore topologico.
- Il simbolo di non connessione sui pin inferiori 4 e 5 è visibile; il JSON li lascia senza collegamenti e segnala warning, ma non distingue esplicitamente tra pin flottante e NC.

### c07

- Batch: `C1`
- Score: `78`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riconosce quasi tutti i componenti principali: due pulsanti, resistenza verso GND, IC CD4026, display a sette segmenti, resistori di segmento e GND. La parte destra IC-resistori-display è nel complesso fedele. Gli errori principali sono nella rete sinistra dei pulsanti/alimentazione: pin 3 e pin 16 sono uniti erroneamente, i terminali di un pulsante sono cortocircuitati nello stesso nodo e un terminale di S2 è lasciato scollegato. La struttura resta comunque recuperabile come base.

**Errori maggiori:**
- Il JSON unisce il pin 3 dell'IC CD4026 al pin 16, mentre nell'immagine il pin 3 è collegato alla linea CLK/debounce a sinistra e il pin 16 è collegato alla linea di alimentazione superiore; queste sono reti distinte visivamente.
- La rete dei pulsanti e della resistenza di pull-down è fusa impropriamente con due pin diversi dell'IC e con entrambi i terminali di un pulsante. Nell'immagine la linea CLK/RST con S1, S2 e la resistenza non è un unico nodo che cortocircuita direttamente i terminali del pulsante S1.
- Il terminale superiore di S2 risulta non collegato nel JSON, ma nell'immagine S2 ha un terminale collegato alla linea verticale superiore e l'altro al nodo RST/linea inferiore.

**Errori minori:**
- Il display a sette segmenti è modellato come Integrated_Circuit con subtype seven_segment_display; la topologia dei terminali è comunque riconoscibile.
- Nel gruppo delle resistenze verso il display sono presenti sette collegamenti grafici distinti, mentre il testo vicino indica un gruppo aggregato; il JSON usa sette resistori separati, scelta topologicamente accettabile ma non perfettamente aderente alla notazione grafica aggregata.
- Il JSON segnala come non collegati due pin inferiori dell'IC che nell'immagine sono marcati con simboli di non connessione; questo non è grave, ma il warning su push_button21.2_t1 riflette invece una discrepanza già conteggiata.

**Punti incerti:**
- La corrispondenza esatta tra ciascun terminale del display e il rispettivo terminale del resistore dipende dalla lettura delle etichette a-g; il JSON appare coerente con l'ordine visibile ma alcune etichette sono graficamente ravvicinate.
- Lo stato operativo dei pulsanti è rappresentato graficamente come aperto, ma il JSON non contiene uno stato esplicito separato oltre ai terminali e ai collegamenti.

### c08

- Batch: `C1`
- Score: `73`
- Fedeltà: `MEDIUM`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riconosce gran parte dei componenti principali e conserva abbastanza bene la sezione LED-transistor e diversi collegamenti IC2-resistenze. Tuttavia contiene errori topologici importanti: una rete di alimentazione è etichettata/collegata come GND, il pin inferiore di IC1 è unito al nodo sbagliato, R4 risulta aperto e lo switch SPDT è semplificato in modo non fedele. La struttura resta recuperabile come base, ma la fedeltà complessiva è solo parziale.

**Errori critici:**
- Il JSON collega il simbolo GND superiore alla rete di alimentazione superiore e ai pin superiori degli IC, mentre nell'immagine la barra superiore è la rete di alimentazione e il GND di C2 è separato e connesso al terminale inferiore del condensatore.

**Errori maggiori:**
- Il pin inferiore di IC1 è inserito nella stessa net dei pin laterali e del condensatore C1 positivo, invece nell'immagine è collegato alla linea inferiore di massa.
- Il condensatore C1 ha il terminale superiore collegato al nodo dei pin laterali di IC1 e il terminale inferiore a massa; nel JSON il terminale negativo è nella net di massa IC2 e il positivo è unito anche al pin inferiore di IC1.
- Il terminale superiore di R4 risulta non connesso nel JSON, ma nell'immagine è collegato alla rete superiore tramite il lato destro dello switch/linea superiore.
- Lo switch SPDT è modellato come switch a due terminali chiuso, ma nell'immagine ha tre contatti visibili R, comune e L; il contatto L alimenta R3 e il contatto destro alimenta R4, con stato meccanico non rappresentabile come semplice collegamento chiuso tra due soli terminali.
- IC2 nel JSON contiene un terminale destro duplicato per pin 7 e un terminale bottom_1 senza pin_number, mentre nell'immagine sono visibili pin inferiori/laterali distinti inclusi 8, 13, 15 e 7; questo degrada la corrispondenza dei terminali dell'IC.

**Errori minori:**
- Il terminale di alimentazione superiore visibile nell'immagine è rappresentato come Terminal generico senza conservare la label topologica visibile.
- Il marking dell'IC2 è riportato come CD401 invece della marcatura visibile più completa; ciò non altera direttamente i collegamenti.
- Le polarità dei LED sono dichiarate nel JSON, ma la verifica puntuale anodo/catodo per tutti gli otto LED è solo parzialmente supportata dalla chiarezza dell'immagine.

**Punti incerti:**
- L'immagine è uno schema raster con alcuni incroci e ponticelli; alcune connessioni tra le barre degli anodi dei LED e i resistori R3/R4 sono visivamente complesse ma la struttura principale a coppie di LED e transistor è riconoscibile.
- La corrispondenza esatta tra gli instance_id dei resistori/LED del JSON e le sigle grafiche R3-R8/D1-D8 è dedotta dalla posizione topologica, non da un mapping esplicito nel JSON.
- La polarità puntuale di ogni LED e dei condensatori è visibile solo in parte con sufficiente chiarezza; non tutte le polarità dichiarate sono state penalizzate.

### c17

- Batch: `C1`
- Score: `86`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riconosce quasi tutti i componenti principali e conserva la struttura topologica essenziale: ingresso tramite switch verso IN, C1 verso massa, LM317 con OUT su bus comune, lampada verso massa, tre rami condensatore verso la catena resistiva e GND comune. Le principali discrepanze riguardano lo stato dello switch dichiarato chiuso mentre il simbolo appare aperto e la polarità dichiarata/interpretata dei condensatori laterali C2-C4, oltre a qualche incertezza di mappatura dei designatori. Nel complesso è una base topologica buona e correggibile.

**Errori maggiori:**
- Le polarità dei condensatori C2, C3 e C4 risultano invertite rispetto all'immagine: nell'immagine il terminale positivo è sul lato destro collegato al bus OUT/lampada, mentre il terminale sinistro è collegato alla catena ADJ/R1/R2/R3. Il JSON assegna il lato sinistro come negative e il lato destro come positive, ma poi collega i terminali negativi a nodi della catena resistiva: la topologia dei nodi è coerente, ma la polarità dichiarata è sospetta/invertita per questi condensatori.
- Il JSON dichiara lo switch S1 come 'closed', ma nell'immagine il simbolo del deviatore/interruttore appare aperto, con contatto mobile non chiaramente chiuso sul terminale destro. Il collegamento topologico tra terminale di ingresso e nodo IN è però rappresentato tramite i due terminali dello switch, quindi l'errore riguarda soprattutto lo stato visibile dichiarato.

**Errori minori:**
- La lampada è rappresentata come class_name Lamp con due terminali, coerente nella sostanza; eventuali dettagli grafici interni del simbolo non sono modellati.
- L'IC è correttamente riconosciuto come LM317T con terminali IN, OUT e ADJ; non sono presenti numeri di pin visibili nell'immagine, quindi la verifica si limita alle posizioni/etichette mostrate.
- I due terminali di alimentazione sono modellati come Terminal generici; l'immagine mostra una sorgente/ingresso DC con due punti di connessione, quindi l'astrazione è accettabile ma non cattura la label testuale di polarità/alimentazione.

**Punti incerti:**
- L'associazione esatta tra resistor22.1/22.2/22.3 e i designatori visivi R1/R2/R3 non è verificabile dal solo JSON, anche se la catena resistiva a tre elementi è presente.
- L'associazione esatta tra polarized_capacitor20.2/20.3/20.4 e C2/C3/C4 non è esplicitata; i collegamenti indicano tre condensatori verso il bus di uscita, coerenti nella struttura generale.
- La polarità di C1 è visibile con '+' in alto nell'immagine e il JSON la rappresenta come positive top/negative bottom; questa parte appare coerente.

### c18

- Batch: `C1`
- Score: `80`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON cattura quasi tutti i componenti principali e gran parte della topologia: ingresso, due uscite, quattro operazionali, nove resistori, tre condensatori e quattro GND sono presenti, e molti nodi di feedback/interconnessione corrispondono all'immagine. Le principali discrepanze riguardano la classificazione dei condensatori come polarizzati, la rappresentazione incompleta/ambigua dei pin di alimentazione degli operazionali e la mancanza dei numeri di pin e delle label visibili. La struttura resta comunque una buona base topologica correggibile.

**Errori maggiori:**
- I condensatori C1, C2 e C3 sono disegnati come condensatori non polarizzati; nel JSON sono tutti classificati come Polarized_Capacitor con terminali positive/negative.
- Il pin di alimentazione superiore di IC1a è collegato visivamente a un terminale di alimentazione, ma nel JSON il collegamento al terminale di alimentazione è assegnato al terminale inferiore aux2; inoltre il terminale superiore aux1 non è presente per IC1a.
- Il pin di alimentazione inferiore di IC2b è collegato visivamente a un terminale di alimentazione, ma nel JSON il collegamento al terminale di alimentazione è assegnato al terminale inferiore aux2 senza preservare i numeri/posizioni visibili e non distingue chiaramente il pin 4 mostrato nell'immagine.

**Errori minori:**
- Alcuni terminali esterni hanno orientamento relativo non coerente con la posizione grafica visibile, ad esempio uscite a destra dichiarate con terminale a sinistra o top.
- Le label topologiche visibili Audio IN, High out e Low out non sono riportate nel JSON come metadati dei terminali.

**Punti incerti:**
- L'associazione degli identificativi resistor22.x ai resistori R1-R9 è deducibile solo dalla topologia del JSON e non dai nomi, quindi alcune corrispondenze di istanza restano non verificabili direttamente.
- Le label di alimentazione dei terminali terminal26.2 e terminal26.4 non sono memorizzate nel JSON; la topologia dei fili è comunque in parte verificabile visivamente.
- La denominazione in1/in2 degli ingressi degli operazionali non consente di verificare con certezza il segno +/− senza una convenzione esplicita nel JSON.
