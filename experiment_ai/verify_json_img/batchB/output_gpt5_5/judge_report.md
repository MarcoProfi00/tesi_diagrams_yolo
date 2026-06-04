# Report verifica immagine ↔ Graph JSON

Generato: 2026-06-04 11:53:14

## Tabella sintetica

| Circuito | Batch | Score | Fedeltà | Critici | Maggiori | Minori | Usabile come graph base |
|---|---:|---:|---|---:|---:|---:|---|
| b01 | B | 55 | LOW | 2 | 5 | 2 | False |
| b02 | B | 78 | HIGH | 0 | 3 | 2 | True |
| b03 | B | 76 | HIGH | 0 | 4 | 4 | True |
| b04 | B | 86 | HIGH | 0 | 2 | 3 | True |
| b05 | B | 84 | HIGH | 0 | 3 | 3 | True |
| b06 | B | 54 | LOW | 2 | 7 | 3 | False |
| b07 | B | 71 | MEDIUM | 1 | 2 | 1 | True |
| b08 | B | 76 | HIGH | 0 | 3 | 2 | True |
| b09 | B | 88 | HIGH | 0 | 2 | 2 | True |
| b10 | B | 80 | HIGH | 0 | 3 | 3 | True |

## Dettagli per circuito

### b01

- Batch: `B`
- Score: `55`
- Fedeltà: `LOW`
- Usabile come graph base: `False`
- Spiegazione: Il JSON riconosce molti componenti principali, ma la topologia dei collegamenti è fortemente degradata: il net di massa cortocircuita terminali dei transistor che nell'immagine sono su nodi diversi, il nodo centrale con VOS e ingresso dell'operazionale è spezzato, e il pin superiore dell'operazionale collegato a VDD è lasciato aperto. Alcune parti, come sorgente VOS verso ingresso superiore e terminali di uscita, sono parzialmente riconoscibili, ma il grafo non è affidabile come base topologica.

**Errori critici:**
- Il JSON unisce alla massa diversi terminali dei due transistor che nell'immagine non appartengono tutti alla linea di massa; in particolare il nodo di massa visibile è la linea inferiore connessa ai terminali inferiori dei transistor, al pin inferiore dell'operazionale e al terminale di uscita negativo.
- Il JSON cortocircuita tra loro base/collettore di entrambi i transistor e li mette nello stesso net di massa, mentre nell'immagine i transistor hanno connessioni distinte: i terminali inferiori sono a massa, il nodo comune tra Q1 e Q2 è laterale, e un nodo superiore va verso resistori e ingresso dell'operazionale.

**Errori maggiori:**
- Il pin superiore dell'operazionale è visibilmente collegato a una label di alimentazione, ma nel JSON il terminale superiore dell'operazionale è lasciato non connesso.
- Il nodo di uscita positivo dell'operazionale è visibilmente collegato alla linea superiore di feedback e ai terminali superiori dei resistori superiori; nel JSON il nodo di uscita è collegato a due resistori ma la corrispondenza con i resistori visibili è incoerente e sembra includere un terminale non appartenente al top rail.
- Il nodo centrale visibile, comune al resistore inferiore, al resistore verticale centrale, al lato positivo della sorgente VOS e all'ingresso non invertente dell'operazionale, non è rappresentato correttamente come un singolo net coerente.
- La sorgente VOS è presente, ma il suo terminale positivo non risulta collegato nel JSON allo stesso nodo dell'ingresso non invertente dell'operazionale, come invece appare nell'immagine.
- Le tre resistenze sono presenti, ma le connessioni dei loro terminali non riproducono in modo affidabile la disposizione visibile dei resistori R1, R2 e R3 rispetto a top rail, nodo centrale, transistor e massa.

**Errori minori:**
- Le label topologiche visibili VDD e VREF non sono rappresentate come label o terminali semantici nel JSON, anche se i terminali di uscita positivo e negativo sono presenti.
- I terminali dei transistor sono nominati B/E/C nel JSON, ma dall'immagine la distinzione esatta tra i terminali fisici non è completamente verificabile senza interpretazione del simbolo; tuttavia alcune connessioni topologiche risultano comunque chiaramente errate.

**Punti incerti:**
- La corrispondenza esatta tra gli identificativi resistor22.1, resistor22.2 e resistor22.3 e i resistori disegnati non è esplicitata dal JSON e deve essere dedotta solo dalle connessioni.
- La distinzione precisa B/E/C dei transistor non è completamente verificabile senza interpretare il simbolo, quindi la valutazione si concentra soprattutto sui nodi fisicamente visibili.
- La sorgente voltage_source31.1 sembra rappresentare la sorgente VOS visibile, ma il JSON non conserva la label testuale.

### b02

- Batch: `B`
- Score: `78`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riconosce quasi tutti i componenti principali e ricostruisce gran parte della topologia dell'astabile: LED, resistori, transistor, condensatori e GND sono presenti e molte connessioni fondamentali sono coerenti. Le principali discrepanze riguardano la mancata rappresentazione esplicita della label di alimentazione superiore, ambiguità/scambi nella mappatura dei resistori centrali e una polarità errata del condensatore inferiore. Nel complesso è una base recuperabile e abbastanza fedele, ma non perfetta.

**Errori maggiori:**
- Il JSON non rappresenta esplicitamente il terminale/alimentazione superiore visibile come label +5V; la relativa net è solo implicita tramite i terminali collegati.
- I due resistori di polarizzazione centrali sono presenti ma la corrispondenza nominale/topologica appare scambiata rispetto alle etichette visibili R2/R4: il resistore sinistro scende alla base di Q1, quello destro al collettore/base-net di Q2, mentre nel JSON le istanze resistor22.2 e resistor22.3 sono collegate rispettivamente a Q1 base e Q2 base. Questo è recuperabile ma rende ambigua la mappatura dei resistori centrali.
- La polarità dei condensatori nel JSON non è pienamente coerente con i segni visibili: per C2 il terminale positivo è sul lato destro nell'immagine, mentre il JSON assegna il positivo al lato sinistro per entrambi i condensatori.

**Errori minori:**
- Le posizioni relative dei terminali dei transistor nel JSON sono semplificate e non sempre corrispondono chiaramente alla geometria del simbolo nell'immagine, anche se i collegamenti principali risultano interpretabili.
- Le istanze dei resistori non mantengono le designazioni visibili R1, R2, R3, R4; ciò non compromette da solo la topologia ma rende meno chiara la corrispondenza visiva.

**Punti incerti:**
- La corrispondenza esatta tra component_id generici del JSON e le designazioni visive D1/D2, R1-R4, C1/C2, Q1/Q2 non è dichiarata nel JSON e deve essere dedotta solo dalla topologia.
- Le etichette B1, B2, X1 e X2 sono callout di nodi/punti del circuito nell'immagine; il JSON non le rappresenta come terminali separati, ma potrebbero essere solo annotazioni e non componenti elettrici autonomi.

### b03

- Batch: `B`
- Score: `76`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riconosce quasi tutti i componenti principali e molte connessioni dei rami LED, resistori, transistor Q1/Q2 e barre di alimentazione. Tuttavia Q3 è classificato come NPN anziché PNP e la zona centrale con D3 e la catena verticale D4-D5-D6 contiene connessioni non fedeli o spezzate rispetto ai nodi visibili. La struttura complessiva resta correggibile e abbastanza aderente, ma con discrepanze topologiche localizzate importanti.

**Errori maggiori:**
- Il transistor Q3 visibile è di tipo PNP, mentre nel JSON è classificato come NPN_Transistor.
- Per Q3 il JSON assegna il terminale superiore come E e quello inferiore/centrale come C in modo non coerente con il simbolo visibile e con i collegamenti del ramo superiore.
- Il nodo centrale a destra di D3 e in alto alla colonna D4-D5-D6 dovrebbe unire anche il terminale superiore della catena di diodi verticale e il nodo di Q3/R6, ma nel JSON D3 è collegato direttamente al transistor Q3 e a R6 senza includere correttamente il terminale superiore della catena D4-D5-D6.
- La catena verticale D4-D5-D6 e R5 è rappresentata con connessioni spezzate o orientate su diodi non chiaramente corrispondenti, lasciando il nodo superiore della catena separato dal nodo superiore comune e il nodo inferiore della catena non chiaramente collegato a R4/R5 come in immagine.

**Errori minori:**
- I diodi Zener visibili sono rappresentati genericamente come Diode; la topologia a due terminali resta in gran parte utilizzabile.
- Il JSON non mantiene etichette visibili dei componenti, rendendo difficile verificare univocamente la corrispondenza fra diode7.x e D3-D10.
- Alcune polarità/orientazioni dei diodi verticali nel JSON sono difficili da confermare visivamente e potrebbero non corrispondere esattamente al simbolo.
- I terminali esterni A e B visibili accanto alla batteria non sono modellati come terminali separati, anche se la batteria e le barre di alimentazione principali sono presenti.

**Punti incerti:**
- La polarità esatta di alcuni diodi piccoli e Zener non è sempre verificabile con certezza dall'immagine a causa della risoluzione e della sovrapposizione grafica.
- La corrispondenza esatta fra gli identificativi diode7.2-diode7.7 e le etichette visibili D4-D10 è parzialmente ambigua perché il JSON non conserva i designator originali.
- La denominazione dei terminali B/C/E dei transistor è valutabile solo dal simbolo visibile, ma senza usare pinout esterni.

### b04

- Batch: `B`
- Score: `86`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON ricostruisce bene molti componenti e la maggior parte delle reti principali: trasformatore, terminali esterni, resistori, diodi, fusibile e catena verso il carico sono in gran parte coerenti. Gli errori principali riguardano il riconoscimento dei due dispositivi attivi: H1 è classificato come NPN invece che SCR e Q1 manca come transistor a tre terminali, sostituito da un diodo. La topologia generale resta comunque in buona parte recuperabile.

**Errori maggiori:**
- Il componente H1 visibile nell'immagine è un SCR/thyristor, mentre nel JSON è classificato come NPN_Transistor. La topologia a tre terminali è in parte recuperabile, ma la classe del componente principale non corrisponde al simbolo visibile.
- Il componente Q1 visibile nell'immagine è un transistor BJT, mentre nel JSON il dispositivo equivalente è rappresentato come un diodo aggiuntivo, perdendo un componente attivo a tre terminali.

**Errori minori:**
- I terminali assegnati al componente H1/SCR sono etichettati come B, C, E da transistor NPN; la numerazione/funzione corretta non è verificata dal JSON e non corrisponde semanticamente al simbolo SCR.
- Alcune polarità dei diodi sono difficili da validare completamente; in particolare il ramo del diodo equivalente a D2/Q1 è rappresentato con una connessione semplificata che non conserva chiaramente la relazione visiva tra D2 e il transistor Q1.
- I terminali esterni della batteria/carico e della rete AC sono rappresentati come terminali singoli; ciò è accettabile topologicamente ma manca una descrizione semantica delle label visibili.

**Punti incerti:**
- La corrispondenza esatta tra gli identificativi resistor22.3, resistor22.4, resistor22.5 e i resistori verticali R3, R4, R5 è dedotta dalla posizione e dai collegamenti, ma il JSON non conserva le label originali dell'immagine.
- La polarità esatta di alcuni diodi è valutabile solo visivamente e può essere ambigua a causa della qualità dell'immagine; non tutti gli orientamenti sono penalizzati come errori certi.
- Le label testuali dei terminali esterni AC e batteria/carico sono visibili nell'immagine ma non codificate esplicitamente nel JSON.

### b05

- Batch: `B`
- Score: `84`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riproduce bene la struttura principale: antenna, induttore con condensatore parallelo, diodo, due transistor, tre resistori verso la linea comune, condensatori di accoppiamento, batteria e switch. Le reti principali sono per lo più coerenti. Gli errori maggiori riguardano la mancata rappresentazione esplicita dei terminali J1/J2/headset e l'uso di un 'Breaker' al loro posto, oltre alla classificazione polarizzata di condensatori che nell'immagine non mostrano polarità. Nel complesso il grafo è una buona base correggibile.

**Errori maggiori:**
- Il JSON non rappresenta esplicitamente i due terminali/connettori di uscita J1 e J2 visibili a destra; usa invece un componente 'breaker' non corrispondente al simbolo visibile.
- Il componente 'breaker3.1' non corrisponde chiaramente al simbolo visibile: l'immagine mostra terminali/connettori headset, non un interruttore automatico/breaker.
- I condensatori C2, C3 e C4 nell'immagine appaiono come condensatori non polarizzati, mentre il JSON li classifica come 'Polarized_Capacitor' con terminali positive/negative.

**Errori minori:**
- Il componente variabile parallelo all'induttore è classificato come condensatore polarizzato nel JSON, mentre il simbolo visibile è un condensatore variabile/non polarizzato.
- Alcune posizioni relative dei terminali non sono coerenti con il disegno, ad esempio la batteria è disegnata con terminali sinistra/destra ma il positivo/negativo grafico non è chiaramente verificato dal JSON.
- Lo stato aperto dello switch S1 è coerente visivamente, ma il JSON collega comunque i due lati solo tramite reti separate; la modellazione è accettabile ma non esplicita il simbolo esterno del headset.

**Punti incerti:**
- La polarità esatta della batteria B1 nell'immagine è parzialmente visibile ma non è necessario dedurre la funzione elettrica dei terminali.
- L'orientamento anodo/catodo del diodo CR1 sembra coerente con la barra a destra, ma la valutazione della polarità resta limitata alla visibilità del simbolo.
- Il simbolo a destra del circuito rappresenta un doppio headset esterno; la sua modellazione topologica dettagliata non è completamente definibile dall'immagine.

### b06

- Batch: `B`
- Score: `54`
- Fedeltà: `LOW`
- Usabile come graph base: `False`
- Spiegazione: Il JSON riconosce diversi blocchi principali del circuito radio, ma manca Z1, classifica male vari condensatori e il potenziometro, e contiene errori topologici importanti nel ramo batteria/S1/alimentazione e nell'uscita IC1-C5-Z1. La rete inferiore e parte del front-end antenna-diodo-transistor sono parzialmente recuperabili, ma la fedeltà complessiva non è affidabile.

**Errori critici:**
- Il trasduttore/altoparlante Z1 visibile all'uscita dell'amplificatore manca completamente dal JSON; al suo posto non è presente un componente equivalente collegato tra il condensatore di uscita e la linea inferiore.
- La topologia batteria/interruttore/alimentazione è gravemente errata: nell'immagine il positivo della batteria passa attraverso S1 verso la barra superiore di alimentazione, mentre nel JSON il positivo batteria è collegato al terminale inferiore dello switch e lo switch non è connesso alla barra superiore ma a una rete interna dell'amplificatore.

**Errori maggiori:**
- C1 nell'immagine è un condensatore variabile/non polarizzato, ma nel JSON è rappresentato come condensatore polarizzato.
- C2, C3 e C4 sono condensatori non polarizzati nell'immagine, ma sono rappresentati nel JSON come Polarized_Capacitor.
- Il potenziometro R3 è riconosciuto come semplice resistore a due terminali, perdendo il terminale del cursore visibile e la connessione verso l'ingresso dell'amplificatore.
- Il circuito integrato IC1 LM386 è rappresentato come Operational_Amplifier generico a 5 terminali, mentre nell'immagine mostra pin numerati 2,3,4,5,6 con topologia specifica di alimentazione, ingresso e uscita visibile.
- L'uscita tramite C5 è collegata nel JSON a un breaker/interruttore anziché al trasduttore Z1 e alla barra inferiore come nell'immagine.
- Il cursore del potenziometro R3 verso l'ingresso pin 3 di IC1 è assente; nel JSON l'ingresso corrispondente dell'amplificatore è lasciato non connesso.
- Nel JSON è presente un componente Breaker che non corrisponde chiaramente a un componente discreto dell'immagine; sembra sostituire impropriamente parte del ramo di uscita o dello switch.

**Errori minori:**
- Lo stato 'closed' dello switch è dichiarato nel JSON, ma dall'immagine lo stato elettrico effettivo del simbolo non è completamente verificabile come contatto chiuso.
- Le polarità assegnate ad alcuni condensatori polarizzati nel JSON non sono tutte verificabili direttamente o sono confuse rispetto ai simboli visibili.
- Il JSON accorpa molti terminali alla rete inferiore; gran parte è coerente, ma l'inclusione di alcuni terminali di alimentazione/IC e breaker dipende da identificazioni non affidabili.

**Punti incerti:**
- L'identificazione esatta dei terminali B/C/E del transistor non è completamente verificabile solo dal simbolo e dalla resa dell'immagine, anche se la connettività generale del transistor è in parte plausibile.
- La corrispondenza tra i terminali aux1/aux2/in1/in2 dell'amplificatore e i pin numerati visibili non è esplicitata nel JSON, quindi non è possibile verificarla come mapping funzionale.
- Alcune polarità dei condensatori elettrolitici C5 e C6 sono visibili, ma l'associazione precisa ai componenti JSON dipende dall'identificazione automatica degli elementi.

### b07

- Batch: `B`
- Score: `71`
- Fedeltà: `MEDIUM`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riconosce i componenti principali visibili, cioè due MOSFET, una massa, terminali e una sorgente/terminale, ma confonde la sorgente d'ingresso con il terminale superiore e contiene un errore topologico grave su M2, i cui due terminali di conduzione risultano collegati entrambi a massa. La struttura generale è parzialmente recuperabile, ma la fedeltà topologica è solo media.

**Errori critici:**
- Il JSON collega insieme drain e source di M2 sulla stessa net di massa, cortocircuitando i due terminali del MOSFET. Nell'immagine M2 ha un terminale superiore collegato al nodo di uscita superiore e un terminale inferiore collegato alla linea di massa, quindi i due terminali di conduzione non sono sulla stessa net.

**Errori maggiori:**
- Il terminale superiore indicato nell'immagine come alimentazione è rappresentato nel JSON come terminale positivo di un Voltage_Source insieme al terminale negativo del generatore d'ingresso. Visivamente ci sono un terminale di alimentazione superiore separato e una sorgente di ingresso a sinistra.
- Il JSON collega il gate di M1 al terminale26.1, ma nell'immagine il gate di M1 è collegato al terminale superiore di alimentazione, mentre il terminale d'ingresso a sinistra è collegato a un terminale di conduzione di M1.

**Errori minori:**
- Alcune relative_position dei terminali MOSFET nel JSON non sono coerenti con la disposizione visiva dei simboli, specialmente per M1 e M2; questo rende più difficile verificare l'identità dei terminali, pur non aggiungendo componenti extra.

**Punti incerti:**
- L'immagine non consente di verificare in modo univoco i nomi funzionali G, S e D dei MOSFET senza usare conoscenza esterna; la valutazione considera solo la posizione topologica dei terminali visibili.
- Il terminale26.1 del JSON potrebbe rappresentare il terminale superiore o il nodo d'ingresso sinistro, ma la sua identità grafica non è esplicitamente annotata nel JSON.

### b08

- Batch: `B`
- Score: `76`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riconosce quasi tutti i componenti principali: sorgente di corrente, batteria di bias, quattro MOSFET e tre GND. La maggior parte delle connessioni interne tra gate, source/drain e nodi comuni è coerente con l'immagine. Restano però due omissioni topologiche importanti: la sorgente di corrente non è collegata al nodo VDD e il MOSFET superiore destro non è collegato al nodo Rout. Questi terminali sono lasciati aperti nel JSON, mentre nell'immagine sono connessi a etichette topologiche visibili. Nel complesso il grafo è una buona base correggibile, ma non perfetto.

**Errori maggiori:**
- Il terminale superiore della sorgente di corrente è visibilmente collegato alla linea VDD, ma nel JSON è lasciato non connesso.
- Il drain/top del MOSFET in alto a destra è visibilmente collegato al nodo di uscita Rout, ma nel JSON è lasciato non connesso.
- Il nodo VDD e il nodo di uscita Rout sono visibili come terminali/etichette topologiche, ma non sono rappresentati nel JSON; questo causa terminali aperti dove l'immagine mostra connessioni a nodi etichettati.

**Errori minori:**
- I quattro MOSFET sono presenti, ma il JSON non conserva le etichette visibili M1, M2, M3, M4; ciò rende meno immediata la corrispondenza tra istanze JSON e simboli dell'immagine.
- Le direzioni/nomi D, S e G dei MOSFET nel JSON sono plausibili per la topologia disegnata, ma l'immagine non rende tutti i terminali D/S esplicitamente numerati o marcati.

**Punti incerti:**
- La corrispondenza esatta tra gli instance_id mosfet16.1, mosfet16.2, mosfet16.3, mosfet16.4 e le etichette visive M1, M2, M3, M4 è deducibile dalla topologia ma non esplicitata nel JSON.
- La distinzione drain/source dei MOSFET non è verificabile in modo indipendente dall'immagine senza assumere convenzioni funzionali esterne.

### b09

- Batch: `B`
- Score: `88`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riproduce bene la topologia principale: due MOSFET in serie tra VDD e VSS, ingresso collegato al nodo centrale delle due sorgenti di polarizzazione, uscita comune ai drain e carico capacitivo/resistivo verso GND. I collegamenti principali del campo graph sono coerenti con i fili visibili. Le discrepanze riguardano soprattutto la semantica dei terminali esterni VIN/VOUT non preservata e la classificazione/polarità del condensatore, non chiaramente visibile nell'immagine.

**Errori maggiori:**
- Il condensatore di carico visibile non mostra una polarità chiaramente indicata, mentre nel JSON è classificato come Polarized_Capacitor con terminali positive/negative.
- Le label topologiche visibili VIN e VOUT non sono rappresentate esplicitamente come tali nel JSON, ma solo come terminali generici.

**Errori minori:**
- terminal_metadata è vuoto, quindi non documenta le label visibili dei terminali esterni.
- La distinzione D/S dei MOSFET è parzialmente basata sulla posizione e sul simbolo; nel JSON è plausibile, ma non completamente verificabile senza ambiguità dall'immagine.

**Punti incerti:**
- La polarità o non polarità del condensatore di carico non è del tutto verificabile dal disegno, anche se non sono visibili marcatori espliciti.
- L'identificazione esatta dei terminali drain/source dei MOSFET dal solo simbolo grafico può essere ambigua, ma i collegamenti di nodo principali risultano coerenti.

### b10

- Batch: `B`
- Score: `80`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riconosce quasi tutti i componenti principali visibili: terminali, sorgenti di corrente, sorgente di tensione, resistori, switch, GND e condensatori. La topologia principale A/B/massa è in parte ricostruita, ma ci sono discrepanze importanti: diversi condensatori non polarizzati sono modellati come polarizzati, il nodo centrale C/VC risulta probabilmente fuso con la rete destra B, e il ramo con switch aperto e sorgente di tensione è solo parzialmente coerente. Nel complesso il grafo resta una base recuperabile ma non è una rappresentazione perfetta dell'immagine.

**Errori maggiori:**
- I condensatori non polarizzati visibili tra A-C, A-B e B-C sono rappresentati nel JSON come Polarized_Capacitor, introducendo polarità non visibile per questi elementi.
- Il nodo centrale C/VC è erroneamente unito nel JSON al nodo destro B attraverso una rete più ampia, mentre nell'immagine C è separato da B dal condensatore tra C e B e dal terminale VC.
- Il ramo resistore r_ON, switch aperto e sorgente di tensione è collegato in modo incompleto/errato: nel JSON la sorgente di tensione positiva è collegata solo allo switch e la negativa alla rete B, ma il nodo tra switch e sorgente e la separazione prodotta dallo switch aperto non sono rappresentati in modo pienamente coerente con i fili visibili.

**Errori minori:**
- I quattro terminali esterni A, B, C/VC sono rappresentati come terminali generici senza conservare le label visibili.
- Alcune polarità positive/negative dei condensatori sono dichiarate nel JSON anche dove l'immagine non mostra una polarità verificabile.
- Le direzioni/terminali current_from e current_to delle sorgenti di corrente non sono sempre verificabili in modo certo dal solo JSON rispetto alla posizione grafica, anche se i componenti principali sono presenti.

**Punti incerti:**
- L'associazione esatta degli instance_id dei vari condensatori ai simboli C_A, C_B, C_AB, C_AC e C_BC non è esplicitata nel JSON e va dedotta solo dai collegamenti.
- La polarità dei condensatori laterali verso massa non è chiaramente indicata nell'immagine, quindi la polarità dichiarata nel JSON non è pienamente verificabile.
- La corrispondenza tra terminal26.2, terminal26.3 e terminal26.4 e i terminali visibili B, C/VC e il nodo inferiore non è completamente certa solo dai nomi JSON.
