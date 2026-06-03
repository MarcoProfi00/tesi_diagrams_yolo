# Report verifica immagine ↔ Graph JSON

Generato: 2026-06-03 18:07:00

## Tabella sintetica

| Circuito | Batch | Score | Fedeltà | Critici | Maggiori | Minori | Usabile come graph base |
|---|---:|---:|---|---:|---:|---:|---|
| b01 | B | 64 | MEDIUM | 1 | 4 | 2 | True |
| b02 | B | 88 | HIGH | 0 | 2 | 2 | True |
| b03 | B | 77 | HIGH | 0 | 4 | 3 | True |
| b04 | B | 85 | HIGH | 0 | 2 | 3 | True |
| b05 | B | 63 | MEDIUM | 1 | 5 | 3 | True |
| b06 | B | 70 | MEDIUM | 1 | 5 | 3 | True |
| b07 | B | 94 | VERY_HIGH | 0 | 0 | 2 | True |
| b08 | B | 76 | HIGH | 0 | 3 | 2 | True |
| b09 | B | 86 | HIGH | 0 | 2 | 2 | True |
| b10 | B | 62 | MEDIUM | 1 | 4 | 2 | True |

## Dettagli per circuito

### b01

- Batch: `B`
- Score: `64`
- Fedeltà: `MEDIUM`
- Usabile come graph base: `True`
- Spiegazione: Il JSON contiene molti componenti principali visibili, ma presenta una fusione errata della rete di massa con terminali dei transistor e diverse connessioni importanti assegnate a nodi sbagliati. La struttura resta in parte recuperabile, ma la fedeltà topologica è solo parziale.

**Errori critici:**
- Il JSON unisce in un'unica rete GND, il terminale negativo di uscita, l'alimentazione inferiore dell'operazionale e diversi terminali di entrambi i transistor; nell'immagine la rete di massa include il nodo inferiore comune, ma non include i collettori/nodi superiori dei transistor né il nodo intermedio di Q2/R3.

**Errori maggiori:**
- Il JSON non rappresenta il ramo/simbolo di alimentazione VDD visibile sull'operazionale come terminale o sorgente dedicata, mentre introduce una sola sorgente associata a VOS.
- Il componente voltage_source31.1 corrisponde probabilmente alla sorgente VOS, ma nel JSON è collegato tra un ingresso dell'operazionale e la rete superiore dei resistori, mentre nell'immagine VOS è in serie tra il nodo sotto R2 e l'ingresso invertente dell'operazionale.
- Il nodo di uscita dell'operazionale e terminale positivo VREF è connesso alla barra superiore che alimenta le estremità superiori di R2 e R3; nel JSON l'uscita è connessa a resistor22.1_t1 e resistor22.2_t1, ma la rete superiore risulta spezzata o parzialmente assegnata in modo errato rispetto ai resistori dell'immagine.
- La rete del nodo comune tra R1 superiore, R2 inferiore, R3/Q2 e ingresso non invertente dell'operazionale è rappresentata solo parzialmente: il JSON connette npn_transistor18.1_E, resistor22.1_t2 e operational_amplifier19.1_in2, ma non include correttamente il ramo verso R2 e il collettore/nodo di Q2 visibile.

**Errori minori:**
- I terminali B/E/C dei transistor nel JSON hanno posizioni relative poco coerenti con il disegno: l'emettitore dei transistor è visivamente verso il basso/massa, non verso l'alto.
- Il JSON segnala operational_amplifier19.1_aux1 come terminale non connesso; nell'immagine è visibile una connessione superiore di alimentazione all'operazionale.

**Punti incerti:**
- La corrispondenza esatta tra resistor22.1, resistor22.2, resistor22.3 e i resistori R1, R2, R3 è deducibile solo dalla topologia del JSON, non da etichette di istanza.
- Il verso esatto e quindi la denominazione B/C/E dei due transistor è parzialmente difficile da verificare solo dall'immagine stilizzata, anche se alcuni terminali risultano chiaramente incompatibili con la rete di massa nel JSON.
- La distinzione tra ingressi in1/in2 dell'operazionale e i simboli '+'/'-' è presumibile dalla posizione ma non esplicitata con label funzionali nel JSON.

### b02

- Batch: `B`
- Score: `88`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riconosce correttamente i componenti principali e riproduce bene la topologia dell'astabile: due LED con resistori verso i collettori, due transistor NPN con emettitori a GND, due resistori di base verso la linea superiore e due condensatori incrociati. I collegamenti principali sono in larga parte fedeli. Le principali discrepanze sono l'assenza delle label/nodi visibili X1, X2, B1, B2 e una polarità/orientamento incoerente per uno dei condensatori polarizzati. Nel complesso il grafo è una buona base correggibile.

**Errori maggiori:**
- Il Graph JSON non rappresenta esplicitamente le etichette/terminali topologici visibili X1, X2, B1 e B2, che nell'immagine marcano nodi di collettore/base dei transistor e aiutano a identificare i collegamenti principali.
- La polarità dei condensatori polarizzati appare incoerente con l'immagine per almeno uno dei due condensatori: C1 mostra il lato positivo a sinistra, mentre C2 mostra il lato positivo a destra; nel JSON entrambi i condensatori hanno positive a sinistra e negative a destra.

**Errori minori:**
- Le istanze dei resistori non conservano le etichette visibili R1, R2, R3, R4, rendendo meno chiara la corrispondenza nominale pur mantenendo le classi e gran parte della topologia.
- Le istanze dei LED, transistor e condensatori non conservano le etichette visibili D1, D2, Q1, Q2, C1, C2; la corrispondenza resta deducibile dalla posizione/topologia, ma non è esplicitata.

**Punti incerti:**
- La corrispondenza esatta tra component_id generici e sigle visibili dei componenti è dedotta dalla topologia, perché il JSON non riporta le sigle schematiche originali.
- La denominazione B, C, E dei transistor nel JSON sembra coerente con il simbolo visibile, ma la verifica è limitata alla geometria del disegno e non a pinout fisici esterni.

### b03

- Batch: `B`
- Score: `77`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON contiene quasi tutti i componenti principali e molte reti principali sono riconoscibili: rail positivo e negativo, tre LED, tre transistor, otto resistori e le catene di diodi. La fedeltà è però ridotta da un errore importante sul tipo/terminali di Q3, dalla semantica generica dei diodi zener e da incertezze o possibili inversioni nella rappresentazione delle catene di diodi. Nel complesso resta una buona base topologica correggibile.

**Errori maggiori:**
- Il transistor Q3 nell'immagine è un transistor PNP, mentre nel JSON è classificato come NPN_Transistor.
- Nel JSON manca un diodo visibile nell'immagine: sono presenti D1-D10, con tre LED e sette diodi discreti, mentre il JSON contiene tre LED e solo sette diodi identificati come diode7.1-diodes7.7 ma uno di questi insiemi non rappresenta chiaramente tutti i diodi verticali della catena centrale e destra con semantica coerente; in particolare D10 non è distinguibile come zener/diode separato nella semantica del JSON.
- La rete inferiore/negativa nel JSON include anche il catodo del LED D7, ma nell'immagine D7 è in serie sotto R6 verso il rail inferiore: il terminale inferiore del LED è effettivamente al rail inferiore, mentre il terminale superiore è collegato a R6; la rappresentazione è plausibile solo se led12.3 è D7. Tuttavia il JSON collega anche diode7.5_anode allo stesso rail negativo, che corrisponde alla catena destra/centrale e può fondere reti differenti se diode7.5 non è D10.
- Q3 ha terminali e orientamento incompatibili con l'immagine: nell'immagine il terminale superiore va al rail positivo, il terminale sinistro/centrale va al nodo con R6 e D4, e il terminale destro va a R7; nel JSON il componente è trattato come NPN con E in alto, C in basso e B a destra, creando una semantica dei terminali non affidabile.

**Errori minori:**
- I diodi zener visibili sono rappresentati semplicemente come Diode; la classe generica conserva in parte la topologia ma perde una semantica visibile del simbolo.
- Il JSON non conserva le etichette visibili dei componenti come Q1, Q2, Q3, D1-D10 e R1-R8; ciò rende più difficile verificare la corrispondenza ma non altera direttamente la topologia dichiarata.
- Alcune relative_position dei terminali non corrispondono bene all'orientamento grafico dei simboli, specialmente per diodi verticali e transistor, pur non sempre producendo un collegamento errato nel graph.

**Punti incerti:**
- La corrispondenza esatta tra gli identificativi automatici diode7.1-diode7.7 e i diodi D3-D6/D8-D10 dell'immagine non è esplicitata, quindi alcune valutazioni su ordine e polarità dei diodi restano incerte.
- Le polarità precise di alcuni diodi piccoli sono parzialmente leggibili ma non sempre abbastanza nette da distinguere ogni anodo/catodo con assoluta sicurezza.
- La corrispondenza fra led12.1, led12.2, led12.3 e i tre LED dell'immagine è dedotta dalla topologia, non da etichette nel JSON.

### b04

- Batch: `B`
- Score: `85`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON include quasi tutti i componenti principali visibili e riproduce bene la maggior parte delle reti: trasformatore, resistenze, diodi, fusibile, terminali e nodo inferiore comune sono sostanzialmente coerenti. Le principali discrepanze riguardano la classificazione di H1 come transistor NPN invece che come dispositivo tipo SCR/thyristor e una rappresentazione semplificata del trasformatore e dei terminali esterni. La topologia è comunque recuperabile e abbastanza fedele all'immagine.

**Errori maggiori:**
- Il componente H1 visibile nell'immagine è un dispositivo a tre terminali con simbolo tipo SCR/thyristor, mentre nel JSON è rappresentato come NPN_Transistor. La connettività a tre terminali è in gran parte preservata, ma la classe del componente non corrisponde al simbolo visivo.
- Il trasformatore T1 appare con primario e secondario separati, ma il JSON modella il trasformatore con soli quattro terminali semplici senza esplicitare le due bobine visibili; ciò è accettabile topologicamente solo in modo parziale.

**Errori minori:**
- Alcune posizioni relative dei terminali dei diodi verticali non sembrano coerenti con l'orientamento grafico visibile, anche se la topologia dei collegamenti resta comprensibile.
- Le etichette visibili dei terminali del secondario del trasformatore e del carico batteria non sono rappresentate come semantica nel JSON.
- I terminali esterni sono rappresentati genericamente come Terminal senza distinguere visivamente ingresso AC e uscita batteria/carico.

**Punti incerti:**
- L'identificazione automatica tra i singoli diodi JSON diode7.1-diodes7.5 e i diodi etichettati D1-D4/D2 nell'immagine è deducibile dai collegamenti ma non esplicitata dai nomi component_id.
- La polarità esatta di alcuni diodi, in particolare D1 e D2, è visibile ma non sempre facilmente verificabile rispetto ai nomi anode/cathode del JSON senza ambiguità grafica.
- Il simbolo H1 potrebbe essere interpretato dalla pipeline come transistor per la somiglianza a tre terminali, ma visivamente è diverso da Q1.

### b05

- Batch: `B`
- Score: `63`
- Fedeltà: `MEDIUM`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riconosce molti componenti principali e buona parte della catena antenna-diodo-transistor-resistori-condensatori, ma presenta errori importanti: C1 variabile non è modellato correttamente, diversi condensatori sono classificati come polarizzati, la parte di uscita J1/J2 è sostituita da un Breaker e alcune net inferiori sono fuse in modo topologicamente discutibile con GND, alimentazione e ritorni. La struttura resta parzialmente recuperabile, ma la fedeltà complessiva è solo media.

**Errori critici:**
- Il componente di uscita/cuffia a destra è rappresentato come Breaker con due terminali entrambi a sinistra, mentre nell'immagine sono visibili due jack/contatti J1 e J2 collegati al conduttore e alla linea inferiore; questa errata modellazione altera una parte principale della topologia di uscita.

**Errori maggiori:**
- Il condensatore variabile visibile in parallelo all'induttore non è rappresentato come tale nel JSON; è invece assimilato a un condensatore polarizzato della rete d'antenna/induttore.
- I condensatori C2, C3 e C4 nell'immagine sono condensatori non polarizzati, ma il JSON li classifica come Polarized_Capacitor.
- Il nodo inferiore dell'induttore e del condensatore variabile è collegato a terra nell'immagine, ma nel JSON è fuso con una grande net che include anche la linea di alimentazione positiva e molti ritorni dei resistori/emettitori.
- La batteria è orientata e connessa in modo topologicamente sospetto: nel JSON il terminale positivo è sulla grande net comune con GND e ritorni, mentre il negativo è collegato solo allo switch; nell'immagine B1 è in serie con S1 sulla linea inferiore, con i due terminali su nodi distinti.
- Il nodo del collettore di Q2 dovrebbe essere comune alla linea superiore, a C4 e al contatto superiore J1, mentre il JSON lo collega a un Breaker invece di modellare chiaramente il jack/uscita.

**Errori minori:**
- L'induttore L1 è disegnato accoppiato/adiacente all'antenna e al condensatore variabile; il JSON lo rappresenta come semplice Inductor, perdendo un dettaglio simbolico visibile ma mantenendo il componente principale.
- Alcune posizioni relative dei terminali non corrispondono bene al disegno, ad esempio la batteria è indicata con terminali sinistra/destra ma la sua relazione topologica nel disegno è lungo la linea inferiore; questo è secondario rispetto agli errori di connessione.
- Lo switch S1 è rappresentato come open, coerente visivamente, ma il JSON collega il suo terminale destro alla grande net comune in modo che la semantica dello stato non basta a descrivere correttamente la separazione dei nodi.

**Punti incerti:**
- La polarità dei transistor NPN è indicata nel JSON con B, C, E e corrisponde alle lettere visibili, ma non viene valutata alcuna funzione elettrica oltre alle etichette grafiche.
- La reale natura fisica dei due contatti di uscita a destra può essere interpretata come jack/headset/connettore; l'immagine però non supporta chiaramente la classe Breaker usata nel JSON.
- Alcuni incroci e connessioni nella parte bassa tra emettitori, ritorni resistivi, batteria e switch sono ravvicinati; la valutazione si basa sui punti di giunzione visibili.

### b06

- Batch: `B`
- Score: `70`
- Fedeltà: `MEDIUM`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riconosce buona parte dei componenti principali e molte net della sezione antenna, transistor, alimentazione e IC sono recuperabili. Tuttavia manca Z1, R3 è modellato come resistore a due terminali invece che variabile con cursore, il pin 3 dell'IC risulta scollegato, e vari condensatori non polarizzati sono classificati come polarizzati. La topologia è quindi solo parzialmente fedele ma ancora utilizzabile come base di correzione.

**Errori critici:**
- Il componente di uscita Z1 visibile nell'immagine, collegato al condensatore di uscita e alla linea inferiore, manca completamente nel JSON; al suo posto il percorso di uscita risulta interrotto o rappresentato con un collegamento errato verso un breaker.

**Errori maggiori:**
- Diversi condensatori non polarizzati visibili sono classificati nel JSON come condensatori polarizzati, introducendo terminali positive/negative non verificabili e semanticamente errati per C1, C2, C3 e C4.
- Il componente R3 visibile è un resistore variabile/potenziometro con cursore collegato all'ingresso dell'IC, ma il JSON lo rappresenta come semplice resistore a due terminali.
- Il nodo del pin 3 dell'IC dovrebbe essere collegato al cursore di R3, ma nel JSON operational_amplifier19.1_in1 risulta non connesso.
- Il pin 2 dell'IC è collegato direttamente alla linea inferiore comune, ma il JSON collega operational_amplifier19.1_in2 alla grande net di massa includendo anche molti terminali; questa parte è corretta come massa, ma l'assenza del collegamento del pin 3 rende la zona ingressi dell'IC topologicamente incompleta.
- Il ramo di uscita dell'IC verso C5 e Z1 non è rappresentato correttamente: il JSON collega l'uscita solo a polarized_capacitor20.5_positive e l'altro lato di C5 a breaker3.1_t1, componente non corrispondente a Z1.

**Errori minori:**
- C1 appare come condensatore variabile/trimmer, mentre nel JSON è trattato come condensatore polarizzato ordinario.
- La polarità positive/negative assegnata a vari condensatori non polarizzati non è supportata dal simbolo visibile.
- Il JSON dichiara lo switch S1 come closed, ma nell'immagine lo stato elettrico del contatto non è chiaramente verificabile come chiuso.

**Punti incerti:**
- Il JSON usa un Operational_Amplifier per IC1; dall'immagine è un blocco triangolare IC con pin numerati, quindi la forma topologica a ingressi/uscita/alimentazioni è verificabile, ma la classe funzionale esatta non viene valutata tramite conoscenza esterna.
- L'identificazione dei terminali B/C/E del transistor è plausibile dalla forma del simbolo, ma piccoli dettagli del disegno non consentono una verifica assoluta di ogni terminale.
- Lo stato chiuso di S1 dichiarato nel JSON non è confermabile con certezza dall'immagine statica.

### b07

- Batch: `B`
- Score: `94`
- Fedeltà: `VERY_HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riproduce molto bene la struttura visibile: due MOSFET, sorgente di ingresso, massa e tre terminali esterni sono presenti; i collegamenti principali tra ingresso, gate di M1, nodo di uscita, gate di M2 e massa corrispondono all'immagine. Restano solo piccole carenze semantiche nei nomi/ruoli dei terminali visibili e incertezze non penalizzate sull'orientamento S/D dei MOSFET.

**Errori minori:**
- Le etichette topologiche visibili per il nodo di ingresso e il nodo di uscita non sono rappresentate esplicitamente nel JSON, anche se i rispettivi terminali e collegamenti sono presenti.
- I terminali esterni visibili sono modellati come Terminal generici senza distinguere chiaramente i ruoli visivi dei nodi di alimentazione/uscita, ma ciò non altera in modo sostanziale la topologia.

**Punti incerti:**
- La denominazione S/D dei due MOSFET non è verificabile con certezza dalla sola immagine, quindi non è penalizzata.
- Il simbolo del MOSFET M2 mostra entrambi i terminali di conduzione collegati al nodo inferiore; questa connessione appare coerente con il JSON, anche se l'orientamento fisico S/D non è determinabile visivamente.

### b08

- Batch: `B`
- Score: `76`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riconosce quasi tutti i componenti principali: sorgente di corrente, batteria di bias, quattro MOSFET e tre GND. La struttura generale è in buona parte recuperabile, ma contiene discrepanze topologiche importanti: il nodo VDD della sorgente di corrente e il nodo Rout del MOSFET destro superiore sono lasciati non connessi, e una net centrale tra MOSFET appare assegnata in modo non coerente con i fili visibili. Per questo la fedeltà è buona ma non molto alta.

**Errori maggiori:**
- Il terminale superiore della sorgente di corrente è visibilmente collegato al nodo etichettato VDD, ma nel JSON è lasciato non connesso.
- Il nodo di uscita Rout visibile sul drain superiore del MOSFET destro superiore non è rappresentato nel JSON come terminale/label topologica, e il relativo drain risulta non connesso.
- Il collegamento tra il nodo inferiore del ramo sinistro superiore e il gate del MOSFET destro inferiore sembra mal rappresentato: nell'immagine il nodo centrale verticale collega il source/drain del MOSFET sinistro superiore con il gate del MOSFET destro inferiore, mentre nel JSON tale net è associata a un collegamento diretto tra source di mosfet16.3 e drain di mosfet16.4 e separata dal gate di mosfet16.2.

**Errori minori:**
- Il nodo VDD è rappresentato implicitamente solo tramite la sorgente di corrente, senza un terminale/label dedicato, pur essendo visibile come label topologica.
- L'assegnazione degli identificativi M1-M4 ai quattro MOSFET non è esplicita nel JSON e alcune posizioni dei gate/source/drain risultano difficili da verificare con certezza dall'immagine.

**Punti incerti:**
- La corrispondenza esatta tra mosfet16.1, mosfet16.2, mosfet16.3, mosfet16.4 e le etichette visive M1, M2, M3, M4 non è dichiarata nel JSON e va inferita solo dalla posizione dei terminali.
- Le polarità/tipi specifici dei MOSFET non sono valutabili con certezza oltre alla presenza dei simboli MOSFET e dei terminali principali.

### b09

- Batch: `B`
- Score: `86`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riproduce bene la struttura principale: due MOSFET in serie tra VDD e VSS, due sorgenti a sinistra che pilotano i gate, nodo intermedio VIN, nodo di uscita comune con condensatore e resistore verso GND e terminale VOUT. Non risultano collegamenti topologici palesemente errati nel campo graph. Le principali carenze riguardano la perdita di alcune label visibili e la rappresentazione generica dei terminali VIN/VOUT; alcuni dettagli di polarità e nomi dei terminali MOSFET non sono pienamente verificabili dall'immagine.

**Errori maggiori:**
- Il nodo/label visibile VIN è rappresentato come un generico Terminal collegato al nodo tra le due batterie; la topologia del punto è corretta, ma la semantica visibile VIN non è preservata nel componente.
- Il nodo/label visibile VOUT è rappresentato come un generico Terminal collegato al nodo di uscita; la topologia del punto è corretta, ma la semantica visibile VOUT non è preservata nel componente.

**Errori minori:**
- Le etichette topologiche visibili dei generatori VTR1 e VTR2 non sono conservate; sono presenti come due Battery generiche.
- Le etichette visibili dei MOSFET M1 e M2 non sono conservate negli identificativi; sono rappresentati come mosfet16.1 e mosfet16.2.

**Punti incerti:**
- La corrispondenza esatta tra mosfet16.1/mosfet16.2 e le etichette visive M1/M2 è deducibile dalla posizione ma non esplicitata nel JSON.
- La polarità del condensatore verso massa è indicata nel JSON come polarized_capacitor positivo sul nodo di uscita e negativo a GND; dall'immagine il simbolo mostra un condensatore verso massa, ma la polarità grafica non è completamente inequivocabile.
- I nomi D/S/G dei terminali dei MOSFET non sono verificabili senza usare conoscenza esterna del simbolo/pinout; è verificabile soprattutto la connettività geometrica dei tre terminali.

### b10

- Batch: `B`
- Score: `62`
- Fedeltà: `MEDIUM`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riconosce molti componenti principali e mantiene alcune net corrette, come B con la sorgente di tensione, il ramo verso massa e parte dei rami resistivi/sorgenti. Tuttavia contiene un errore topologico importante: fonde il nodo A con il nodo centrale C e di conseguenza collega in modo errato alcuni condensatori interni. La rappresentazione resta parzialmente recuperabile, ma non è fedele alla topologia completa dell'immagine.

**Errori critici:**
- Il JSON unisce sullo stesso nodo il terminale A con il nodo centrale C, mentre nell'immagine A e C sono separati da un condensatore e non sono lo stesso nodo.

**Errori maggiori:**
- Manca un terminale visibile associato al nodo centrale VC sotto C.
- Il condensatore tra A e C è collegato nel JSON tra la net A/C fusa e il nodo B, invece dovrebbe stare tra A e C.
- Il condensatore tra A e B nella parte centrale-superiore è interpretato con un lato collegato al nodo centrale C invece che al nodo A.
- I condensatori nell'immagine sono simboli non polarizzati, mentre il JSON li classifica tutti come Polarized_Capacitor con terminali positive/negative.

**Errori minori:**
- I quattro terminali A, B e VC sono rappresentati genericamente come Terminal senza label topologiche visibili A, B, VC.
- Le sorgenti di corrente sono presenti, ma la corrispondenza esatta delle tre istanze alle frecce visibili non è completamente verificabile dai soli ID e posizioni del JSON.

**Punti incerti:**
- La polarità delle sorgenti di tensione e dei condensatori non è pienamente valutabile come terminali elettrici oltre ai segni visibili della sorgente VOS; non è stato usato alcun pinout o significato funzionale esterno.
- La corrispondenza esatta tra gli ID dei componenti JSON e i singoli simboli omonimi dell'immagine è dedotta dalle connessioni e dalle posizioni relative, non da etichette ID visibili.
