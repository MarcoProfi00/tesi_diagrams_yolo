# Report verifica immagine - Graph JSON

Generato: 2026-06-05 17:52:42

## Metodo

- Modello: `gpt-5.4`
- Prompt: `prompt.txt`
- Prompt SHA256: `19f1ee29c0c6`
- YAML: `class_terminals_v1.yaml`
- YAML SHA256: `7e5491a8cdf0`

## Tabella sintetica

| Circuito | Batch | Score | Fedelta | Critici | Maggiori | Minori | Usabile come graph base |
|---|---:|---:|---|---:|---:|---:|---|
| a01 | A | 98 | VERY_HIGH | 0 | 0 | 1 | True |
| a02 | A | 97 | VERY_HIGH | 0 | 0 | 2 | True |
| a03 | A | 78 | HIGH | 0 | 3 | 3 | True |
| a04 | A | 98 | VERY_HIGH | 0 | 0 | 1 | True |
| a05 | A | 96 | VERY_HIGH | 0 | 0 | 1 | True |
| a06 | A | 98 | VERY_HIGH | 0 | 0 | 1 | True |
| a07 | A | 72 | MEDIUM | 0 | 3 | 1 | True |
| a08 | A | 97 | VERY_HIGH | 0 | 0 | 1 | True |
| a09 | A | 71 | MEDIUM | 1 | 2 | 1 | True |
| a10 | A | 96 | VERY_HIGH | 0 | 0 | 2 | True |

## Dettagli per circuito

### a01

- Batch: `A`
- Score: `98`
- Fedelta: `VERY_HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il campo graph e sostanzialmente fedele all'immagine: pin1 del connettore va al resistore superiore e poi al LED verso il nodo comune di destra con GND; pin2 va al resistore inferiore e poi alla lampada verso lo stesso nodo comune con GND; pin3 va all'interruttore aperto verso GND; pin4 va direttamente a GND. Non risultano net fuse, net split o collegamenti inventati rilevanti.

**Errori minori:**
- La semantica anode/cathode del LED nel JSON appare coerente con l'immagine, ma il dettaglio grafico del simbolo LED non e perfettamente nitido; lieve riserva solo formale, senza impatto topologico.

**Punti incerti:**
- Il simbolo del LED e sufficientemente leggibile per supportare il mapping sinistra=anode, destra=cathode, ma il tratto del simbolo non e nitidissimo a livello di dettaglio fine.

### a02

- Batch: `A`
- Score: `97`
- Fedelta: `VERY_HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il campo graph e sostanzialmente fedele all'immagine: VCC/batteria verso J3 pin1, rail superiore comune tra batteria negativa, terminale alto del resistore e lato sinistro dello switch, resistore verso J3 pin2, condensatore tra J3 pin3 e GND, J3 pin4 a GND, e switch aperto verso un GND separato sul lato destro. Non risultano collegamenti mancanti, inventati, net fuse o net split; solo lievi imprecisioni nei metadati di posizione dei terminali.

**Errori minori:**
- Nel JSON alcuni pin del connettore J3 sono marcati con relative_position sinistra/destra non coerente con il simbolo visibile, ma i collegamenti topologici dei pin risultano comunque corretti.
- Alcune relative_position dei componenti a due terminali sono semplificate/non fedeli all'orientamento grafico reale, senza impatto sui collegamenti del graph.

**Punti incerti:**
- Il mapping pin1-pin4 del connettore e verificabile dai numeri visibili accanto a J3 e risulta coerente; non emergono ambiguita topologiche rilevanti.
- I simboli GND sono rappresentati come istanze separate nel JSON; questo e accettabile qui perche ciascuno rispetta il collegamento visibile locale e il graph non forza fusioni errate.

### a03

- Batch: `A`
- Score: `78`
- Fedelta: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il graph riproduce bene la topologia principale del ramo di controllo: rail superiore/inferiore, LDR-RV1 verso la base di Q1, accoppiamento Q1->Q2, R1, bobina del relay e diodo in parallelo alla bobina sono sostanzialmente coerenti. L'errore topologico principale è nel ramo AC a destra, dove manca il collegamento visibile tra la sorgente AC e il contatto RL1. Inoltre la batteria reale è stata spezzata in due componenti Battery distinti e lo stato dello switch è marcato closed mentre il simbolo appare open. Nel complesso il graph resta una buona base correggibile, ma non è una corrispondenza quasi perfetta dell'immagine.

**Errori maggiori:**
- Nel ramo AC a destra manca il collegamento visibile tra un terminale della sorgente AC e un terminale del contatto RL1. Nell'immagine il filo superiore collega chiaramente la sorgente V1 al contatto del relay.
- La batteria visibile B1 è stata spezzata in due componenti Battery distinti, uno usato solo per il nodo alto e uno solo per il nodo basso. Questo non corrisponde ai componenti endpoint visibili nell'immagine.
- Lo stato dichiarato dello switch è 'closed', ma il contatto RL1 nell'immagine appare aperto. Anche se il graph non unisce i due terminali dello switch, il metadato di stato è incompatibile con la connettività visibile.

**Errori minori:**
- D1 è un diodo ma nel JSON è rappresentato come LED; i due terminali risultano però collegati agli stessi due nodi visibili del ramo bobina.
- LDR e RV1 sono mappati come Variable_Resistor e Resistor; la topologia del partitore resta comunque coerente con l'immagine.
- Il contatto RL1 è modellato come Switch a 2 terminali senza esplicita associazione al relay/bobina; scelta semplificata ma ancora utilizzabile topologicamente.

**Punti incerti:**
- La polarità esatta di D1 è solo moderatamente leggibile; il lato superiore sembra il catodo, ma non la tratto come inversione certa.
- Nel ramo AC il mapping preciso tra i due terminali del contatto RL1 e i terminali t1/t2 del componente switch può essere permutato senza cambiare l'errore principale: manca comunque il collegamento della sorgente al contatto.
- La rappresentazione di RV1 come reostato/potenziometro è semplificata nel JSON; topologicamente il nodo del cursore sembra riportato al rail inferiore, quindi la riduzione a due terminali non altera chiaramente i collegamenti visibili.

### a04

- Batch: `A`
- Score: `98`
- Fedelta: `VERY_HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il campo graph e topologicamente coerente con l'immagine: ingresso V2 accoppiato tramite C1 al nodo di base, partitore R3-R4 sulla base, R1 dal collettore al rail positivo, R2 e C3 dall'emettitore a massa, C2 dal collettore al ramo con R5 verso massa, e batteria V1 tra rail superiore e rail inferiore/GND. Non emergono errori certi nei collegamenti terminale-terminale.

**Errori minori:**
- I terminali dei componenti a due poli sono nominati genericamente t1/t2 invece che con riferimenti visivi espliciti ai designator dell'immagine; la topologia pero resta coerente e verificabile tramite mapping.

**Punti incerti:**
- Il mapping tra resistor22.1..22.5 e i resistori visivi R1..R5 non e per designator ma esiste una permutazione topologicamente coerente: 22.2≈R3, 22.1≈R4, 22.3≈R1, 22.4≈R2, 22.5≈R5.
- Le polarita dei condensatori C2 e C3 non sono rappresentate semanticamente nel JSON, ma i loro due terminali risultano collegati ai nodi visibili corretti; non altera la fedelta topologica del graph.

### a05

- Batch: `A`
- Score: `96`
- Fedelta: `VERY_HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il campo graph e sostanzialmente fedele all'immagine: J15 pin1 va al resistore e poi al meter VMON con ritorno a GND, pin2 va al condensatore verso GND, pin3 va allo switch TEST aperto verso GND, pin4 va direttamente a GND. Nessun net fuse/split evidente e nessun collegamento inventato o mancante rilevante.

**Errori minori:**
- Il collegamento del ramo resistore->strumento e topologicamente corretto, ma nell'immagine il contatto lato ingresso del voltmetro e meno esplicito del post inferiore destro verso GND; lieve incertezza solo sull'esatta resa del terminale fisico del meter.

**Punti incerti:**
- Nel voltmetro VMON il terminale verso il resistore appare collegato al lato sinistro del corpo dello strumento piu che a un post chiaramente disegnato; tuttavia la topologia visibile resta coerente con una connessione strumento-resistore.
- Non e necessario fondere i tre simboli GND in un'unica net globale: il JSON li mantiene separati come nell'immagine, e questo e accettabile secondo le regole.

### a06

- Batch: `A`
- Score: `98`
- Fedelta: `VERY_HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il campo graph e coerente con l'immagine: ingresso AC -> Rs -> Cc1 -> base del BJT; nodo base condiviso con 100 kΩ verso Vcc e 47 kΩ verso GND; collettore condiviso con 6.8 kΩ verso Vcc e Cc2 verso uscita; emettitore condiviso con 3.9 kΩ verso VEE e Ce verso GND; nodo di uscita condiviso con RL verso GND e terminale di uscita. Non emergono errori topologici certi nei collegamenti dichiarati.

**Errori minori:**
- Alcuni terminali/relative_position dei Terminal simbolici e dei GND separati non aggiungono semantica forte oltre ai fili visibili; lieve imprecisione descrittiva possibile ma senza impatto topologico.

**Punti incerti:**
- I quattro simboli di massa nel disegno possono rappresentare una massa comune elettrica, ma secondo le regole di verifica non vanno fusi automaticamente: il JSON li mantiene separati e questo non contraddice i fili visibili.
- Le etichette testuali Vcc 12 V, VEE 0 V, v_o, R_in e R_out sono usate solo come aiuto visivo; la loro mancata modellazione esplicita come net globali non cambia la correttezza del graph terminale-terminale.

### a07

- Batch: `A`
- Score: `72`
- Fedelta: `MEDIUM`
- Usabile come graph base: `True`
- Spiegazione: Il graph e in gran parte coerente per switch, resistor, LED, meter e GND locali, ma il ramo superiore principale e spezzato nel JSON: nell'immagine J7 pin1 e il terminale sinistro del meter sono sullo stesso filo, mentre il graph li separa tramite due terminali diversi del trasformatore. Questo errore topologico principale abbassa il giudizio a MEDIUM.

**Errori maggiori:**
- Il nodo superiore visibile che collega J7 pin1 al lato sinistro del voltmetro AC risulta spezzato nel graph: il JSON mette connector5.1_pin1 e analog_meter0.1_t1 su due terminali diversi del trasformatore invece di rappresentarli sullo stesso nodo visibile.
- Manca nel graph il collegamento visibile tra connector5.1_pin1 e analog_meter0.1_t1 sul ramo superiore.
- L'assegnazione dei terminali del trasformatore nel graph e incompatibile con la continuita del filo visibile sul ramo superiore: i due terminali transformer28.1_t3 e transformer28.1_t4 sono trattati come nodi distinti, mentre visivamente insistono sullo stesso ramo.

**Errori minori:**
- La lettura dei 4 terminali del trasformatore e ambigua dalla sola immagine; il warning sui terminali non connessi e plausibile, ma non chiarisce correttamente il nodo superiore continuo.

**Punti incerti:**
- La simbologia del trasformatore e resa in modo poco standard nell'immagine: non e completamente certo quali dei quattro terminali del componente JSON corrispondano ai contatti visibili del simbolo.
- Non e verificabile con certezza dalla sola immagine se il ramo superiore tocchi uno o due terminali inferiori del trasformatore; e pero chiaramente visibile la continuita tra J7 pin1 e il terminale sinistro del meter.
- Le masse sono rappresentate con simboli distinti; il JSON non le fonde globalmente e questo non va penalizzato.

### a08

- Batch: `A`
- Score: `97`
- Fedelta: `VERY_HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il campo graph e sostanzialmente coerente con i collegamenti visibili: nodo superiore comune tra sorgente, LED anodo, R1 e R7; nodo Trigger tra R1, C1 e lato sinistro di R3; nodo del transistor/emettitore condiviso con R7 e R6; LED catodo al collettore; base tramite R3; massa inferiore su C1 e R6. Nessun errore topologico certo nei collegamenti dichiarati; solo una lieve semplificazione di classe sul potenziometro usato come resistore.

**Errori minori:**
- Il componente visibile come potenziometro/variable resistor con wiper cortocircuitato a un estremo e rappresentato nel JSON come semplice resistore a 2 terminali; in questo caso la topologia dei nodi resta sostanzialmente corretta.

**Punti incerti:**
- L'immagine mostra due simboli GND separati; il JSON li mantiene come due endpoint distinti. Per le regole date questo non va penalizzato, anche se nello schema elettrico convenzionale potrebbero rappresentare la stessa massa.
- Le label testuali IN, Trigger e LED sono visibili nell'immagine ma non sono necessarie nel graph terminale-terminale e la loro assenza non cambia la topologia.

### a09

- Batch: `A`
- Score: `71`
- Fedelta: `MEDIUM`
- Usabile come graph base: `True`
- Spiegazione: Il graph riproduce bene gran parte della struttura visibile: batteria-fusibile-connettore, pin2 verso condensatore, pin3 verso switch e lampada, pin4 verso resistore e LED. Tuttavia contiene un errore topologico critico: fonde il nodo J1 pin4/R3 con la massa del condensatore, che nell'immagine e un nodo separato. Inoltre manca il collegamento della lampada al suo GND. Per questo la fedelta complessiva e solo MEDIA.

**Errori critici:**
- Il JSON fonde erroneamente il nodo di J1 pin4 / lato sinistro di R3 con il nodo di massa del condensatore C1. Nell'immagine il condensatore e collegato tra J1 pin2 e GND; il nodo J1 pin4-R3 e separato dalla massa.

**Errori maggiori:**
- Manca il collegamento visibile tra il terminale inferiore della lampada e il suo simbolo di massa.
- Il nodo del lato sinistro del resistore R3 dovrebbe essere solo J1 pin4; nel JSON e invece unito anche a massa e al terminale inferiore del condensatore.

**Errori minori:**
- La polarita semanticamente assegnata alla batteria non e verificabile con assoluta certezza dalla resa grafica; non altera la topologia dei collegamenti.

**Punti incerti:**
- L'orientamento/polarita positiva-negativa della batteria non e perfettamente leggibile dall'immagine, ma cio non cambia la topologia.
- La polarita LED appare compatibile con anodo in alto e catodo in basso, ma il dettaglio grafico della barra non e molto nitido.

### a10

- Batch: `A`
- Score: `96`
- Fedelta: `VERY_HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il graph JSON riproduce fedelmente i collegamenti visibili: batteria negativa a GND, batteria positiva al lato sinistro dello switch aperto, uscita switch a J1 pin1, J1 pin2 alla resistenza e poi all'anodo LED con catodo a GND, J1 pin3 alla lampada con ritorno a GND, e J1 pin4 a GND. Non emergono errori topologici certi nei collegamenti terminale-terminale.

**Errori minori:**
- Alcune relative_position dei pin del connettore non sono pienamente coerenti con la geometria visibile del simbolo J1, ma questo non altera i collegamenti topologici dichiarati nel graph.
- L'immagine usa piu simboli GND separati; il JSON li mantiene distinti. Questo e compatibile con le regole di valutazione, ma la reale equivalenza globale dei GND resta una convenzione esterna non verificata solo dal graph.

**Punti incerti:**
- Le posizioni relative left/right assegnate ai pin del connettore non sono tutte chiaramente verificabili dal solo lato grafico del simbolo, ma i fili visibili corrispondono correttamente ai pin 1-4.
- I diversi simboli GND nell'immagine potrebbero rappresentare la stessa massa elettrica, ma non va imposto; il JSON correttamente non li fonde automaticamente nel campo graph.
