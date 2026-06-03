# Report verifica immagine ↔ Graph JSON

Generato: 2026-06-03 18:05:24

## Tabella sintetica

| Circuito | Batch | Score | Fedeltà | Critici | Maggiori | Minori | Usabile come graph base |
|---|---:|---:|---|---:|---:|---:|---|
| a01 | A | 94 | VERY_HIGH | 0 | 0 | 2 | True |
| a02 | A | 93 | VERY_HIGH | 0 | 0 | 2 | True |
| a03 | A | 72 | MEDIUM | 1 | 4 | 2 | True |
| a04 | A | 92 | VERY_HIGH | 0 | 1 | 2 | True |
| a05 | A | 94 | VERY_HIGH | 0 | 0 | 3 | True |
| a06 | A | 89 | HIGH | 0 | 1 | 2 | True |
| a07 | A | 74 | MEDIUM | 0 | 4 | 2 | True |
| a08 | A | 76 | HIGH | 0 | 3 | 2 | True |
| a09 | A | 83 | HIGH | 0 | 2 | 3 | True |
| a10 | A | 96 | VERY_HIGH | 0 | 0 | 2 | True |

## Dettagli per circuito

### a01

- Batch: `A`
- Score: `94`
- Fedeltà: `VERY_HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il Graph JSON riproduce molto fedelmente i componenti principali visibili: connettore a 4 pin, switch, tre simboli GND, due resistori, LED e lampada. I collegamenti principali corrispondono all'immagine: pin 1 verso resistore e LED, pin 2 verso resistore e lampada, pin 3 verso switch, pin 4 verso GND, switch verso GND, e ritorno comune di LED e lampada verso GND. Le discrepanze sono minori e riguardano soprattutto label/posizioni descrittive, non la topologia.

**Errori minori:**
- Il connettore visibile è etichettato J2 nell'immagine, mentre nel JSON è rappresentato genericamente come Connector senza label visibile associata.
- Nel JSON i pin 1 e 2 del connettore hanno relative_position 'right' e i pin 3 e 4 'left', ma nell'immagine i quattro terminali grafici sono sul lato interno destro del corpo del connettore; la numerazione dei pin è comunque corretta e i collegamenti risultano coerenti.

**Punti incerti:**
- La polarità anodo/catodo del LED è coerente con il simbolo visibile, ma la verifica dipende dall'interpretazione grafica del simbolo; non emergono comunque collegamenti incompatibili.
- Lo stato 'open' dello switch nel JSON appare coerente con il disegno, ma la distanza del contatto mobile dal terminale destro è una rappresentazione schematica e non un'informazione elettrica misurabile.

### a02

- Batch: `A`
- Score: `93`
- Fedeltà: `VERY_HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riproduce molto bene la topologia visibile: alimentazione verso il pin 1 del connettore, resistore tra il nodo superiore/switch e il pin 2, condensatore dal pin 3 a GND, pin 4 a GND, e switch aperto verso GND. I componenti principali e i collegamenti sono sostanzialmente corretti; restano solo lievi discrepanze semantiche sulla classe dell'alimentazione e su una label visibile non codificata.

**Errori minori:**
- Il simbolo di alimentazione a sinistra è rappresentato nel JSON come Battery; topologicamente i due terminali sono coerenti, ma la classe non corrisponde perfettamente alla label/simbolo di alimentazione visibile.
- La label topologica visibile associata allo switch non è riportata nel JSON; lo switch e il suo stato aperto sono comunque presenti.

**Punti incerti:**
- La polarità del condensatore non è indicata chiaramente nell'immagine e il JSON lo rappresenta come condensatore non polarizzato.
- La corrispondenza esatta tra la numerazione fisica del connettore J3 e i pin JSON è coerente visivamente, ma dipende dall'ordine dei terminali disegnati lungo il simbolo.

### a03

- Batch: `A`
- Score: `72`
- Fedeltà: `MEDIUM`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riconosce gran parte della struttura principale del lato DC: LDR/resistenze, due transistor, bobina del relè e nodi principali sono in parte coerenti. Tuttavia introduce due batterie al posto di una sorgente, modella D1 come LED, non rappresenta correttamente il relè come bobina con contatto associato e lascia incompleto il circuito AC di destra con sorgente, contatto e lampada. La topologia è ancora recuperabile, ma contiene errori importanti.

**Errori critici:**
- Il diodo D1 visibile in parallelo alla bobina del relè è rappresentato nel JSON come LED e collegato con polarità/nodi incoerenti rispetto all'immagine.

**Errori maggiori:**
- Il contatto del relè RL1 visibile sul lato destro del circuito non è rappresentato correttamente come parte del relè o come interruttore collegato nel circuito di carico; il JSON contiene uno switch isolato solo parzialmente collegato.
- Il carico L1 visibile come lampada/carico AC è rappresentato come `Lamp`, ma i collegamenti al generatore AC e al contatto RL1 sono incompleti.
- La sorgente B1 visibile è una singola batteria/alimentazione DC; il JSON contiene due componenti Battery separati, con una batteria usata per il nodo positivo e l'altra per il nodo negativo.
- Il circuito AC di destra è spezzato nel JSON: il terminale superiore della sorgente AC e un terminale dello switch risultano non collegati, mentre nell'immagine formano il loop con contatto RL1 e lampada.

**Errori minori:**
- La bobina del relè è rappresentata come `Inductor`; topologicamente può corrispondere alla bobina, ma non preserva la semantica di relè con contatto associato.
- Il JSON assegna allo switch lo stato `closed`, ma nell'immagine il contatto RL1 appare graficamente aperto; lo stato elettrico comandato dal relè non è deducibile con certezza come stato fisso.

**Punti incerti:**
- La corrispondenza esatta tra `resistor22.1`, `variable_resistor30.1` e i simboli LDR/RV1 è parzialmente ambigua perché il JSON usa classi generiche e terminali a due pin, mentre l'immagine mostra un LDR e un potenziometro/regolazione.
- La polarità esatta del diodo D1 è visibile graficamente ma la resa del simbolo nell'immagine non consente una verifica robusta dei nomi anodo/catodo nel JSON senza ambiguità.
- La posizione dei terminali base/collettore/emettitore dei due transistor è coerente a grandi linee, ma il simbolo non permette di validare con assoluta certezza ogni terminal name oltre alla topologia dei collegamenti visibili.

### a04

- Batch: `A`
- Score: `92`
- Fedeltà: `VERY_HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON rappresenta molto bene la topologia principale: sorgente di segnale accoppiata tramite condensatore alla base del transistor, rete di polarizzazione con due resistori, collettore con resistore verso la linea superiore e condensatore di uscita verso il carico, emettitore con resistore e condensatore verso massa, batteria tra linea superiore e rete inferiore, e GND sulla rete inferiore. Non emergono collegamenti errati rilevanti nel campo graph. Le discrepanze sono soprattutto semantiche o di etichettatura visibile, non strutturali.

**Errori maggiori:**
- Il riferimento di massa visibile nell'immagine è etichettato come X1/GND sul nodo inferiore centrale; il JSON include correttamente un componente GND collegato alla rete inferiore, ma non conserva l'etichetta visibile X1. Questo non altera la connettività principale, ma perde una semantica topologica visibile.

**Errori minori:**
- Le sigle visibili dei componenti non sono preservate nei component_id/instance_id del JSON; la corrispondenza resta comunque deducibile per classe e posizione topologica.
- Alcune posizioni relative dei terminali sono semplificate rispetto al disegno, in particolare per condensatori accoppiati e sorgenti, ma senza evidente errore topologico nei collegamenti.

**Punti incerti:**
- La polarità dei condensatori polarizzati è visibile graficamente ma il JSON usa terminali generici t1/t2; senza coordinate o marcatori di polarità nel JSON la verifica della polarità esatta resta solo parziale.
- L'associazione tra i resistori JSON resistor22.1-22.5 e le sigle visive R1-R5 non è esplicitata, anche se la topologia consente una corrispondenza plausibile.

### a05

- Batch: `A`
- Score: `94`
- Fedeltà: `VERY_HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il Graph JSON rappresenta molto fedelmente la topologia visibile: sono presenti connettore a 4 pin, switch verso GND, condensatore verso GND, resistore verso misuratore analogico e ritorno a GND. I collegamenti nel campo graph corrispondono ai fili principali dell'immagine. Le discrepanze sono limitate a dettagli descrittivi di orientamento dei pin e a label visibili non riportate.

**Errori minori:**
- Nel JSON i pin 3 e 4 del connettore sono indicati con relative_position 'left', mentre nell'immagine i terminali del connettore J15 sono disegnati sul lato sinistro ma il collegamento elettrico prosegue verso sinistra; la distinzione di posizione/orientamento è comunque poco rilevante per la topologia.
- Nel JSON i pin 1 e 2 del connettore sono indicati con relative_position 'right', mentre nell'immagine i relativi contatti sono sul lato sinistro del simbolo J15 e i fili escono verso destra; è una discrepanza descrittiva dei terminali, non un errore di connessione.
- La label visibile del connettore e quella del misuratore non sono riportate come proprietà semantiche nel JSON, pur essendo le classi dei componenti riconosciute correttamente.

**Punti incerti:**
- Lo stato aperto dello switch è coerente con il disegno, ma la separazione grafica dei contatti non permette di valutare aspetti meccanici oltre alla connessione aperta visibile.
- La corrispondenza esatta tra i nomi pin1-pin4 del connettore nel JSON e la numerazione disegnata è sostanzialmente coerente, ma le relative_position non rappresentano perfettamente la geometria del simbolo.

### a06

- Batch: `A`
- Score: `89`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il Graph JSON riproduce molto bene la struttura principale: sorgente con massa, resistenza e condensatore di ingresso verso la base, partitore di bias, transistor NPN, rete di collettore, rete di emettitore con condensatore verso massa, condensatore di uscita e carico verso massa. I collegamenti del campo graph sono sostanzialmente coerenti con i fili visibili. Le principali carenze riguardano la semantica dei terminali etichettati, rappresentati come terminali generici, più che errori topologici.

**Errori maggiori:**
- Il nodo di alimentazione superiore etichettato Vcc è rappresentato come un generico Terminal; topologicamente il collegamento ai due resistori è corretto, ma la semantica visibile del terminale di alimentazione non è preservata.

**Errori minori:**
- Il terminale inferiore dell'emettitore, visivamente etichettato come nodo di riferimento/alimentazione inferiore, è rappresentato come Terminal generico.
- Il terminale di uscita a destra è rappresentato come Terminal generico senza conservare la semantica visibile di uscita.

**Punti incerti:**
- L'immagine mostra più simboli di massa separati; il JSON li rappresenta come componenti GND separati senza indicare esplicitamente se siano lo stesso nodo globale, ma nel campo graph non risultano cortocircuitati tra loro.
- La polarità dei condensatori non è codificata nel JSON; nell'immagine alcune polarità non sono marcate graficamente in modo univoco dal solo simbolo.

### a07

- Batch: `A`
- Score: `74`
- Fedeltà: `MEDIUM`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riconosce quasi tutti i componenti principali e molti collegamenti locali: connettore J7, switch RESET verso massa, massa del pin 4, resistore, misuratore, LED e masse. Tuttavia la topologia del trasformatore e della linea superiore è problematica: due terminali del trasformatore sono lasciati non connessi e i collegamenti al pin 1 e al misuratore non rispecchiano chiaramente i fili visibili. La rete del ramo inferiore è abbastanza fedele, ma ci sono discrepanze di polarità del LED e mancano alcune label topologiche visibili. Il grafo resta recuperabile come base, ma la fedeltà complessiva è solo media.

**Errori maggiori:**
- Il primario del trasformatore è visibilmente collegato tra il pin 1 del connettore J7 e il terminale superiore del misuratore VAC, ma nel JSON il trasformatore ha due terminali lasciati non connessi e il collegamento al pin 1 è assegnato a un terminale del secondario/lato opposto.
- Il terminale del misuratore VAC collegato alla linea superiore non risulta collegato direttamente alla stessa rete del pin 1 del connettore come appare nell'immagine, ma passa solo tramite terminali del trasformatore con due terminali non connessi.
- La rete del pin 2 del connettore, del resistore, del terminale inferiore del misuratore, della massa centrale e dell'anodo del LED è sostanzialmente riconosciuta, ma il collegamento del LED nel JSON usa polarità opposta rispetto al simbolo visibile.
- Il trasformatore è presente ma la corrispondenza dei suoi quattro terminali nel JSON non rappresenta chiaramente i terminali visibili: due terminali sono lasciati non connessi nonostante nell'immagine entrambe le parti del trasformatore siano attraversate da fili visibili.

**Errori minori:**
- La label topologica RESET è visibile vicino allo switch ma non è rappresentata nel JSON come etichetta o metadata.
- Le label visibili VAC e PWR non sono rappresentate nel JSON come label topologiche associate al misuratore o al LED.

**Punti incerti:**
- L'esatta associazione tra i terminal_id t1-t4 del trasformatore e le posizioni grafiche del simbolo non è completamente verificabile senza coordinate, ma la presenza di due terminali non connessi contrasta con i fili visibili.
- Lo stato open dello switch appare coerente visivamente, ma il disegno stilizzato non permette di verificare dettagli ulteriori dei terminali oltre alla separazione del contatto.

### a08

- Batch: `A`
- Score: `76`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riconosce quasi tutti i componenti principali e gran parte delle connessioni tra sorgente, resistori, condensatore, LED e transistor. La topologia principale è in larga misura recuperabile. Le discrepanze principali riguardano l'assenza delle label topologiche visibili IN, Trigger e LED e soprattutto la separazione dei due simboli GND, che nell'immagine rappresentano la massa comune. Per questo la fedeltà è buona ma non perfetta.

**Errori maggiori:**
- Il JSON non rappresenta i terminali/etichette topologiche visibili 'IN', 'Trigger' e 'LED' come nodi o componenti separati; tali label sono utili per la topologia visibile del circuito.
- Il nodo inferiore della sorgente è collegato solo al proprio simbolo GND separato, mentre nell'immagine il riferimento di massa della sorgente dovrebbe corrispondere alla stessa massa inferiore del resto del circuito.
- La rete centrale che include il nodo Trigger, il terminale inferiore di R1, il terminale superiore di C1 e l'ingresso della resistenza verso la base del transistor è rappresentata in modo parziale: manca il terminale/label Trigger e la connessione è affidata solo ai componenti discreti.

**Errori minori:**
- La sorgente visibile è descritta genericamente come Signal_Source; la classe è accettabile ma non conserva alcuni dettagli simbolici visibili della sorgente.
- Alcune posizioni relative dei terminali nei componenti discreti sono semplificate rispetto al disegno, pur senza alterare necessariamente la connessione principale.

**Punti incerti:**
- La polarità esatta del condensatore non è chiaramente verificabile come informazione topologica dal JSON e dall'immagine.
- La distinzione funzionale dei pin del transistor è stata valutata solo in base alla disposizione grafica visibile, senza usare pinout esterni.

### a09

- Batch: `A`
- Score: `83`
- Fedeltà: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il JSON riconosce quasi tutti i componenti principali e gran parte delle connessioni: batteria-fusibile-J1 pin1, J1 pin5 a massa, J1 pin3 verso switch/lampada, e ramo resistore-LED-massa. Gli errori principali riguardano il condensatore, il cui terminale inferiore è unito erroneamente al nodo del pin4/resistore, e la massa mancante sul terminale inferiore della lampada. Nel complesso il grafo è abbastanza fedele e utilizzabile come base di correzione.

**Errori maggiori:**
- Il condensatore è collegato visivamente tra il nodo del pin 2 di J1 e massa; nel JSON il suo terminale inferiore è collegato al nodo di J1 pin4/resistore invece che solo a massa.
- Il terminale inferiore della lampada è visivamente collegato a massa, ma nel JSON risulta non connesso.

**Errori minori:**
- È presente un simbolo GND extra non collegato nel JSON, non chiaramente corrispondente a un terminale topologico distinto dell'immagine.
- Lo switch è indicato come open nel JSON; l'immagine mostra effettivamente contatti aperti, ma il collegamento grafico ai terminali resta rappresentato come due lati separati e non come conduzione interna, quindi lo stato è semanticamente solo parzialmente utile.
- Alcune relative_position dei pin del connettore non sono perfettamente coerenti con la disposizione visiva verticale del connettore, pur non alterando direttamente la topologia.

**Punti incerti:**
- La polarità/nominazione anode-cathode del LED non è verificabile con assoluta certezza solo dal simbolo e dall'orientamento nel JSON, anche se la connessione topologica resistore-LED-GND è presente.
- L'associazione esatta degli identificativi GND multipli ai singoli simboli di massa dell'immagine non è completamente verificabile, poiché i simboli GND sono separati e nel JSON sono modellati come componenti distinti.

### a10

- Batch: `A`
- Score: `96`
- Fedeltà: `VERY_HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il Graph JSON corrisponde molto bene alla topologia visibile: batteria verso switch, switch verso pin 1 del connettore, pin 2 verso resistore e LED a massa, pin 3 verso lampada a massa, pin 4 a massa. I componenti principali sono presenti e i collegamenti del campo graph risultano sostanzialmente fedeli. Restano solo lievi imprecisioni descrittive su orientamenti dei pin e semantica delle masse separate.

**Errori minori:**
- Nel JSON i pin del connettore hanno posizioni relative left/right non pienamente coerenti con il disegno, dove i quattro pin sono contatti sul lato destro del blocco con collegamenti esterni; questo non compromette la topologia.
- Il JSON rappresenta i simboli GND separati come istanze distinte; nell'immagine sono simboli di massa separati graficamente. La scelta è accettabile topologicamente, ma non esplicita un'eventuale equivalenza globale dei simboli GND.

**Punti incerti:**
- Lo stato aperto dello switch è visibile e coerente, ma la valutazione dello stato meccanico esatto resta limitata alla simbologia grafica.
- La polarità precisa del LED è indicata nel JSON come anodo in alto e catodo in basso; dall'immagine la connessione superiore arriva dal resistore e quella inferiore va a massa, ma la verifica dei nomi anodo/catodo dipende dall'interpretazione del simbolo.
