# Report verifica immagine ↔ Graph JSON

Generato: 2026-06-03 18:11:31

## Tabella sintetica

| Circuito | Batch | Score | Fedeltà | Critici | Maggiori | Minori | Usabile come graph base |
|---|---:|---:|---|---:|---:|---:|---|
| c09 | C2 | 76 | HIGH | 0 | 4 | 4 | True |
| c10 | C2 | 76 | HIGH | 0 | 5 | 4 | True |
| c11 | C2 | 83 | HIGH | 0 | 3 | 2 | True |
| c12 | C2 | 86 | HIGH | 0 | 2 | 3 | True |
| c13 | C2 | 82 | HIGH | 0 | 3 | 3 | True |
| c14 | C2 | 83 | HIGH | 0 | 2 | 3 | True |
| c15 | C2 | 78 | HIGH | 0 | 3 | 2 | True |
| c16 | C2 | 87 | HIGH | 0 | 2 | 2 | True |

## Dettagli per circuito

### c09

- Batch: `C2`
- Score: `76`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riconosce gran parte dei componenti principali e molte connessioni tra ADC, microcontrollore, reset, alimentazioni e masse locali. Tuttavia presenta errori topologici importanti nella sezione display/transistor: linee segmento aggregate o ponticellate impropriamente, basi dei transistor unite quando nell'immagine sono pilotate separatamente, ed emettitori non uniti sul nodo di massa comune. La struttura resta comunque ampiamente recuperabile come base.

**Errori maggiori:**
- Il JSON unisce i segmenti corrispondenti ai due display su alcune linee di segmento, mentre nell'immagine D1 e D2 non sono collegati tra loro direttamente sui pin a-h; D2 appare pilotato tramite proprie linee dal lato sinistro/area transistor, non da ponti diretti da D1.
- Le uscite dei resistori verso i segmenti sono aggregate in modo errato: alcuni resistori risultano collegati allo stesso pin segmento, mentre nell'immagine R1-R8 vanno a segmenti distinti del primo display.
- Le basi dei due transistor sono unite nello stesso nodo nel JSON, ma nell'immagine Q1 e Q2 sono pilotati da due linee distinte tramite due resistori distinti.
- Gli emettitori dei due transistor dovrebbero condividere lo stesso nodo di massa centrale, mentre il JSON li collega a due simboli GND separati senza dichiarare il collegamento comune tra gli emettitori.

**Errori minori:**
- I display a sette segmenti sono modellati come Integrated_Circuit invece che come una classe display dedicata; il subtype aiuta, ma la classe principale è poco coerente con il simbolo visibile.
- Diversi terminali di alimentazione etichettati in alto sono rappresentati come Terminal con relative_position bottom, scelta non aderente alla posizione grafica ma poco rilevante topologicamente.
- Il warning su integrated_circuit11.1_top_1 come non connesso è coerente con la scritta di assenza collegamento, ma il pin è comunque presente come terminale non connesso e richiede interpretazione visiva.
- Molti pin dei display e dei bus digitali sono indicati con label testuali; la corrispondenza esatta delle label è parzialmente leggibile ma non sempre verificabile senza deduzioni funzionali.

**Punti incerti:**
- La corrispondenza esatta tra le label a-h dei due display e i terminali left_1..left_8 del JSON non è completamente verificabile dall'immagine per tutti i segmenti.
- La polarità esatta dei condensatori polarizzati è visibile in parte, ma la resa grafica non consente di verificare con assoluta certezza tutti i terminali positive/negative dichiarati.
- I simboli +5V sono rappresentati come terminali separati nel JSON; dal solo campo graph non è possibile sapere se le label uguali debbano essere trattate come lo stesso nodo globale oppure come terminali separati.

### c10

- Batch: `C2`
- Score: `76`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riconosce gran parte dei componenti principali e molte reti attorno a IC1, pulsanti, LED, alimentazione e IC2. Tuttavia contiene errori localizzati ma importanti: il microfono è classificato come speaker, il ramo dello switch di alimentazione non è connesso alla rete IC2/C9, C5 ha un terminale lasciato aperto, e la rete dei pin laterali di IC2 è unita a massa in modo non coerente con l'immagine. Rimane comunque una base recuperabile per correzioni topologiche.

**Errori maggiori:**
- Il microfono visibile nell'immagine è rappresentato nel JSON come Speaker, quindi la classe del componente di ingresso audio è errata.
- La rete del nodo superiore di alimentazione attorno a IC1 pin14 comprende anche C6 e D2 verso massa; nel JSON C6 è modellato come polarized_capacitor20.4 sulla stessa rete, ma il diodo D2 risulta separato e connesso a massa sul lato opposto rispetto all'immagine.
- Il ramo di alimentazione verso IC2 e C9 è incompleto: il nodo dopo lo switch S5 e il terminale +4V alimenta anche IC2 pin8 e C9 positivo, mentre nel JSON lo switch è collegato solo al terminale e non alla rete IC2/C9.
- Il JSON unisce IC2 pin4, IC2 pin5, C9 negativo e GND, ma nell'immagine pin4 e pin5 sono su un nodo verticale collegato al lato superiore dello speaker; la massa è su un nodo separato inferiore.
- Il condensatore di accoppiamento tra la rete R8/R9/C4 e IC2 pin2 non è rappresentato con entrambi i terminali collegati correttamente: un lato risulta non connesso nel JSON.

**Errori minori:**
- Molti condensatori non polarizzati visibili sono classificati come Polarized_Capacitor nel JSON; ciò altera la semantica di polarità ma non sempre la topologia a due terminali.
- IC2 è rappresentato con 7 terminali invece degli 8 pin numerati visibili; il pin 6 non appare nel JSON, anche se nell'immagine sembra non cablato o non evidenziato funzionalmente.
- Il JSON usa molti componenti GND separati; ciò è coerente con simboli di massa multipli, ma non esplicita che siano la stessa rete globale.
- Il JSON segnala terminali non connessi; uno è coerente con il pin N/C di IC1, mentre l'altro riguarda un condensatore visibilmente cablato.

**Punti incerti:**
- La polarità esatta di alcuni condensatori e diodi non è sempre verificabile con assoluta certezza dalla risoluzione dell'immagine, quindi le discrepanze di polarità sono pesate meno della presenza dei collegamenti.
- La corrispondenza uno-a-uno tra component_id del JSON e reference designator dell'immagine è dedotta dalla posizione/topologia, poiché il JSON non riporta i designator R/C/D/S originali.
- Lo stato chiuso di switch25.1 nel JSON non è chiaramente verificabile dal simbolo S5 nell'immagine.

### c11

- Batch: `C2`
- Score: `83`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riconosce quasi tutti i componenti principali e gran parte della topologia dell'IC, alimentazione, masse, switch e speaker. Le connessioni principali a destra e in alto sono in larga parte fedeli. L'errore più rilevante riguarda la sezione di ingresso sinistra: mancano i terminali esterni e i due condensatori di ingresso risultano connessi direttamente al nodo GND/pin 2 invece che ai rispettivi ingressi visibili. Sono presenti anche classificazioni discutibili di condensatori come polarizzati. La struttura resta comunque una buona base correggibile.

**Errori maggiori:**
- I due condensatori di ingresso laterali sono rappresentati come Polarized_Capacitor, ma nell'immagine appaiono come condensatori non polarizzati.
- Nel JSON manca il terminale/ingresso esterno visibile a sinistra che collega i due condensatori di ingresso e il nodo comune verso massa.
- I condensatori di ingresso C4 e C5 sono collegati nel JSON direttamente al nodo GND/pin 2 sul loro lato positivo, mentre nell'immagine il loro lato esterno va ai terminali di ingresso; è il nodo comune tra i due ingressi che va a massa e al pin 2.

**Errori minori:**
- Un condensatore non polarizzato visibile sulla linea di alimentazione è rappresentato come Polarized_Capacitor.
- Lo stato open dello switch è coerente graficamente ma la certezza topologica del contatto mobile è limitata dall'immagine stilizzata.

**Punti incerti:**
- La polarità di alcuni condensatori non è verificabile o non è mostrata chiaramente per tutti i simboli; dove non visibile non è stata trattata come errore critico.
- La corrispondenza tra speaker24.1/speaker24.2 e K1/K2 è plausibile ma gli identificativi non sono deducibili dal solo JSON oltre ai collegamenti.
- La numerazione dei pin dell'IC appare complessivamente coerente con i numeri visibili, ma non viene valutato alcun significato funzionale dei pin.

### c12

- Batch: `C2`
- Score: `86`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riconosce quasi tutti i componenti principali e la maggior parte delle connessioni topologiche: IC, ingresso, masse, speaker, condensatori di alimentazione e rete superiore/inferiore sono in gran parte coerenti con l'immagine. Le discrepanze principali sono lo switch S1 dichiarato chiuso nonostante sia disegnato aperto e C3 classificato come polarizzato. Sono presenti anche piccole imprecisioni semantiche e di terminali, ma la struttura del grafo resta una buona base correggibile.

**Errori maggiori:**
- Il componente C3 visibile nell'immagine è rappresentato graficamente come condensatore non polarizzato, mentre nel JSON è classificato come Polarized_Capacitor.
- Lo switch S1 nell'immagine appare aperto, mentre il JSON lo dichiara chiuso.

**Errori minori:**
- Il condensatore C1 nell'immagine è disegnato come condensatore non chiaramente polarizzato, mentre nel JSON è classificato come Polarized_Capacitor.
- I due terminali dello speaker sono entrambi indicati con relative_position left nel JSON; visivamente sono due morsetti separati verticalmente sul lato sinistro dello speaker, ma la distinzione top/bottom non è rappresentata.
- La label visibile Audio IN non è rappresentata esplicitamente nel JSON; sono presenti solo due Terminal generici.

**Punti incerti:**
- La polarità di C1 non è chiaramente verificabile dall'immagine.
- La polarità di C2 è visibile solo parzialmente ma sembra coerente con il terminale superiore positivo nel JSON.
- La corrispondenza esatta tra i terminali generici terminal26.1/terminal26.2 e i due punti Audio IN è interpretabile ma non etichettata nel JSON.

### c13

- Batch: `C2`
- Score: `82`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON contiene quasi tutti i componenti principali e ricostruisce bene le reti di alimentazione, uscita, speaker e gran parte dell'ingresso. Sono presenti discrepanze localizzate ma importanti nell'area del pin 2/rete di retroazione e nel ramo R2-C1, oltre alla classificazione come polarizzati di alcuni condensatori visivamente non polarizzati. Nel complesso il grafo resta una buona base correggibile.

**Errori maggiori:**
- Alcuni condensatori non polarizzati visibili sono rappresentati nel JSON come Polarized_Capacitor.
- Il ramo di retroazione dall'uscita attraverso R1 verso il nodo di pin 2 è collegato nel JSON al pin 1 dell'IC, non al pin 2.
- Il ramo R2-C1 dovrebbe essere collegato al nodo del pin 2, ma nel JSON è collegato al nodo del pin 1 e al condensatore d'ingresso.

**Errori minori:**
- Le label topologiche visibili sui terminali di ingresso e alimentazione non sono riportate nel JSON come nomi o attributi semantici dei terminali.
- I terminali dello speaker nel JSON hanno entrambi relative_position left, mentre nell'immagine sono due connessioni laterali separate verso il simbolo dello speaker.
- La polarità di alcuni condensatori polarizzati nel JSON non è sempre direttamente verificabile o coerente con la simbologia visiva, specialmente nei rami di alimentazione negativa.

**Punti incerti:**
- L'associazione esatta tra gli identificativi resistor22.x/polarized_capacitor20.x e le sigle visive R1-R6/C1-C7 non è esplicitata nel JSON e deve essere inferita dalla topologia.
- Il simbolo del condensatore di ingresso mostra una polarità visibile, ma l'orientamento esatto dei terminali nel JSON dipende dall'associazione del componente alla posizione visiva.
- I pin_number dell'IC sono presenti e coerenti con i numeri visibili in immagine, ma non viene valutata alcuna funzione dei pin.

### c14

- Batch: `C2`
- Score: `83`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riconosce quasi tutti i componenti principali e gran parte della topologia: ingressi con due resistori, IC a 8 pin, condensatori, quattro diodi, motore, alimentazioni e GND. L'errore principale è una fusione di nodo sul lato destro dell'IC: il pin 6 viene collegato al nodo di alimentazione superiore invece che al nodo di uscita superiore con pin 7/motore. Inoltre C2 è classificato come polarizzato pur essendo visivamente non polarizzato. Nel complesso il grafo resta una buona base correggibile.

**Errori maggiori:**
- Il condensatore C2 è disegnato come condensatore non polarizzato, mentre nel JSON è classificato come Polarized_Capacitor con terminali positive/negative.
- Il pin destro intermedio dell'IC, pin 6, risulta collegato nel JSON alla linea di alimentazione alta, ai condensatori e al terminale di alimentazione motore, ma nell'immagine il pin 6 è collegato al pin 7/uscita superiore e non direttamente alla barra superiore di alimentazione.

**Errori minori:**
- Il marking dell'IC nel JSON è TC4423, mentre nell'immagine il testo interno appare TC4423 ma la didascalia inferiore cita TC4424; la discrepanza testuale non altera direttamente la topologia.
- Il terminale di alimentazione superiore a sinistra è modellato come terminale26.3 con relative_position bottom, mentre visivamente è un nodo/terminale sulla parte superiore del ramo delle resistenze.
- I tre simboli GND visibili sono rappresentati come tre componenti GND separati; questo è accettabile topologicamente se non si assume l'equipotenzialità globale, ma può non catturare l'identità semantica comune del simbolo GND.

**Punti incerti:**
- La corrispondenza esatta tra i quattro diodi del JSON e le sigle D1-D4 dell'immagine è parzialmente ambigua perché il JSON usa solo instance_id numerici; le connessioni generali dei diodi risultano comunque in larga parte coerenti.
- La polarità esatta di alcuni diodi è valutabile dal simbolo ma può essere difficile distinguere con assoluta certezza nelle zone di incrocio dei fili.
- I pin bottom_1 e bottom_2 dell'IC sono indicati come non connessi nel JSON e appaiono n/c nell'immagine; non sono considerati errore.

### c15

- Batch: `C2`
- Score: `78`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riproduce bene la struttura principale: IC L298, motore, quattro diodi di ricircolo, due condensatori, GND e terminali esterni sono presenti, e i collegamenti principali fra alimentazione superiore, nodi motore, pin 13/14, pin 4/11/9/15 e masse risultano sostanzialmente coerenti con l'immagine. Le principali discrepanze riguardano la classificazione dei condensatori come polarizzati e la perdita di alcune label topologiche visibili sui terminali esterni. Non emergono collegamenti graph chiaramente errati rispetto ai fili visibili.

**Errori maggiori:**
- I due condensatori visibili nell'immagine sono disegnati come condensatori non polarizzati, mentre nel JSON sono classificati come Polarized_Capacitor con terminali positive/negative.
- Il terminale superiore sinistro della linea di alimentazione è etichettato come +Vcc nell'immagine, ma nel JSON è rappresentato solo come terminale generico senza semantica visibile.
- Il terminale destro collegato al pin 9 è etichettato come +5V DC nell'immagine, ma nel JSON è rappresentato come terminale generico senza la label visibile.

**Errori minori:**
- Il terminale sinistro collegato al pin 11 è etichettato Ven nell'immagine, ma nel JSON è solo un terminale generico.
- Il JSON include due terminali IC non connessi corrispondenti ai pin superiori 10 e 12; nell'immagine sono effettivamente mostrati come pin con piccole derivazioni/label, ma non come fili connessi ad altri componenti.

**Punti incerti:**
- La polarità dei diodi è graficamente deducibile ma l'associazione fra istanze diode7.1-7.4 e sigle D1-D4 non è esplicitata nel JSON; la topologia dei nodi risulta comunque coerente.
- La presenza del nodo/pin superiore 10 e del nodo/pin superiore 12 come terminali non connessi nel JSON è compatibile con l'immagine, ma la loro semantica di label C e D non è codificata.

### c16

- Batch: `C2`
- Score: `87`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON contiene tutti i componenti principali visibili e ricostruisce correttamente la maggior parte dei nodi: alimentazione superiore, nodo pin 6/R1-R2/C1, nodo pin 8/R2-R3 e nodo inferiore pin 4/motore/C2/R3. L'errore principale è che R3, disegnato come regolabile con wiper collegato al nodo inferiore, è modellato come resistore a due terminali. Manca inoltre la label Vs. Nel complesso il grafo è una buona base topologica con discrepanze localizzate.

**Errori maggiori:**
- Il nodo del pin 3 dell'IC è unito nel JSON al nodo del terminale superiore del motore, al positivo di C2 e al terminale superiore di R1. Nell'immagine il pin 3 è collegato alla linea di alimentazione superiore, mentre il terminale superiore del motore, il positivo di C2 e il lato superiore di R1 sono anch'essi sulla stessa linea superiore: questa unione è sostanzialmente corretta; tuttavia nel JSON lo stesso nodo include anche il positivo di C1, coerente, ma la struttura non esplicita la label Vs visibile.
- Il cursore/lato regolabile di R3 visibile nell'immagine è collegato al nodo inferiore comune, ma il JSON modella R3 come semplice resistore a due terminali e non rappresenta il terzo terminale/wiper visibile del potenziometro.

**Errori minori:**
- R3 è riconosciuto come resistore semplice invece che come componente regolabile/potenziometro, pur mantenendo i nodi principali della catena resistiva.
- La label topologica Vs visibile sulla linea superiore non è rappresentata come terminale o label nel JSON.

**Punti incerti:**
- La polarità dei condensatori è visibile e sembra coerente con la denominazione positiva/negativa nel JSON, ma la verifica dipende dall'associazione spaziale esatta dei terminali estratti.
- I pin_number dell'IC presenti nel JSON corrispondono ai numeri visibili sul simbolo, ma la posizione relativa top_1/top_2 rispetto ai pin 6 e 8 è solo una codifica interna non completamente verificabile oltre alla connessione ai nodi visibili.
