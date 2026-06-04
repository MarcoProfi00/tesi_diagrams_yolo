# Report verifica immagine - Graph JSON

Generato: 2026-06-04 16:35:45

## Metodo

- Modello: `gpt-5.4`
- Prompt: `prompt.txt`
- Prompt SHA256: `19f1ee29c0c6`
- YAML: `class_terminals_v1.yaml`
- YAML SHA256: `7e5491a8cdf0`

## Tabella sintetica

| Circuito | Batch | Score | Fedelta | Critici | Maggiori | Minori | Usabile come graph base |
|---|---:|---:|---|---:|---:|---:|---|
| c09 | C2 | 86 | HIGH | 0 | 4 | 2 | True |
| c10 | C2 | 92 | VERY_HIGH | 0 | 1 | 2 | True |
| c11 | C2 | 95 | VERY_HIGH | 0 | 1 | 1 | True |
| c12 | C2 | 96 | VERY_HIGH | 0 | 0 | 2 | True |
| c13 | C2 | 95 | VERY_HIGH | 0 | 1 | 2 | True |
| c14 | C2 | 94 | VERY_HIGH | 0 | 1 | 1 | True |
| c15 | C2 | 94 | VERY_HIGH | 0 | 1 | 1 | True |
| c16 | C2 | 97 | VERY_HIGH | 0 | 0 | 2 | True |

## Dettagli per circuito

### c09

- Batch: `C2`
- Score: `86`
- Fedelta: `HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il graph JSON cattura bene la struttura principale: potenziometro/ingresso ADC0804, bus D0-D7 verso AT89S51, reset RC, reti verso i due display e transistor di pilotaggio. Gli errori principali sono nella zona bassa destra, dove il nodo comune P3.1/emettitori/massa risulta spezzato, e in alcune fusioni non visibili tra uscite resistive e pin del display sinistro. Base comunque utile e in gran parte fedele.

**Errori maggiori:**
- Il nodo comune/emettitore dei due transistor e la massa sono visivamente un unico nodo condiviso, ma nel JSON sono modellati come due masse separate senza collegamento tra gnd9.6, gnd9.7 e il nodo comune con P3.1.
- Il nodo visibile che unisce base di Q2, uscita di R12 e linea P3.1 e anche il montante comune in basso; nel JSON il lato base di Q2 e separato dal ramo P3.1/resistore R13-equivalente.
- Il JSON fonde tra loro due uscite di resistenza verso il display sinistro che nell'immagine risultano su segmenti distinti.
- Il JSON fonde due uscite di resistenza anche su un altro ingresso del display sinistro, non supportato chiaramente dall'immagine.

**Errori minori:**
- Le associazioni tra i singoli resistori orizzontali e i pin a..h dei display non sono tutte affidabili; parte del mapping sembra permutato ma con struttura generale corretta.
- I display a sette segmenti sono modellati come Integrated_Circuit; semanticamente imperfetto ma topologicamente accettabile.

**Punti incerti:**
- Il wiring locale attorno a Q2/P3.1/base Q2 e al montante inferiore e molto fitto; la presenza della junction rende probabile il nodo unico, ma alcuni tratti corti sono visivamente compressi.
- Il mapping esatto tra resistor22.4..22.11 e i resistori etichettati R1..R8 nell'immagine non e verificabile uno a uno senza ambiguita completa; valutato con permutazione topologica migliore.
- Il pin integrated_circuit11.1_left_1 (Vref/2) appare non connesso nel JSON e nell'immagine sembra anch'esso non cablato direttamente, quindi non trattato come errore.

### c10

- Batch: `C2`
- Score: `92`
- Fedelta: `VERY_HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il field graph riproduce molto bene quasi tutti i collegamenti visibili tra i due IC, pulsanti, rete LED/zener, altoparlanti, condensatori e resistenze. L’unica omissione topologica rilevante è il microfono M1 con il suo nodo condiviso con C1 e R5, lasciando anche polarized_capacitor20.8_positive non connesso. Per il resto la struttura terminale-terminale è fedele all’immagine.

**Errori maggiori:**
- Il microfono M1 visibile nell'immagine non compare come componente nel JSON; di conseguenza manca il collegamento topologico del nodo M1 superiore con C1, R5 e il ramo inferiore a GND.

**Errori minori:**
- I terminali del LED e del diodo sono modellati con polarità semantiche; la corrispondenza appare plausibile ma l'orientazione grafica è piccola e non completamente verificabile con certezza assoluta.
- Le etichette/testi +4V DC, N/C e valori componenti non sono rappresentati nel graph, ma non alterano la topologia terminale-terminale principale.

**Punti incerti:**
- Il mapping tra resistor22.1/resistor22.2/resistor22.3 e le resistenze R1/R2/R3 è risolvibile topologicamente e non genera errore certo.
- La polarità del LED D1 e dello zener D2 è visibile ma piuttosto piccola; non emergono inversioni certe nel graph oltre alle connessioni già coerenti.
- Il contatto dello switch S5 è rappresentato come switch chiuso tra il ramo di alimentazione e il terminale +4V; l'immagine mostra un interruttore inserito in serie e la connettività adottata nel JSON è plausibile.

### c11

- Batch: `C2`
- Score: `95`
- Fedelta: `VERY_HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il campo graph riproduce molto bene la topologia visibile: pin 12 con C3 a massa, pin 1 con C4 verso ingresso, pin 2 a massa comune con i lati sinistri di C4/C5, pin 13 con C5 verso ingresso, pin 5 e 8 entrambi a massa, pin 3 e 10 sul bus +12V comune con C1 e C2, pin 11 al Mode switch verso lo stesso bus, e le quattro uscite 4/6/9/7 ai due speaker. Non emergono net fuse o net split gravi; resta solo una lieve imprecisione nella rappresentazione del terminale dello switch.

**Errori maggiori:**
- Lo switch e rappresentato con terminali t1/t2 e stato open, ma la geometria del terminale t2 nel JSON (relative_position top) non e coerente con il vocabolario standard del simbolo a due terminali; inoltre il nodo di alimentazione collegato allo switch e plausibile ma il dettaglio terminale-lato resta leggermente imperfetto. La connettivita principale pero risulta corretta: pin 11 del IC e collegato al mode switch, e l'altro lato dello switch va al bus +12V.

**Errori minori:**
- Per lo switch il terminale t2 e marcato come relativo a top invece che al lato opposto lungo l'asse del componente; imprecisione semantica senza impatto topologico certo.

**Punti incerti:**
- I due simboli circolari a sinistra dei condensatori C4 e C5 non sono modellati come componenti nel JSON; sembrano terminali/ingressi grafici ausiliari, ma la loro assenza non altera i collegamenti terminale-terminale principali gia rappresentati tra C4/C5 e i pin 1/13 del IC.
- La polarita positiva/negativa assegnata ai condensatori C4 e C5 nel JSON e compatibile con il verso visibile, ma il giudizio topologico non dipende da tale polarita oltre ai nodi collegati.
- Il mapping dei due speaker JSON ai simboli K1/K2 e coerente topologicamente; anche se i reference designator non sono nel JSON, non emerge errore di scambio.

### c12

- Batch: `C2`
- Score: `96`
- Fedelta: `VERY_HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il campo graph e sostanzialmente fedele all'immagine: ingresso Audio IN tramite C1 al nodo comune dei pin 2/13, massa separata ai pin 3 e 7 come disegnato, rail +12V comune ai pin 6/8/10 e ai positivi di C2/C3, speaker tra pin 5 e 9, e pin 11 collegato al rail +12V attraverso S1. Non emergono errori topologici certi; solo piccole imprecisioni semantiche non strutturali.

**Errori minori:**
- C1 appare visivamente come condensatore non polarizzato, mentre nel JSON e rappresentato come Polarized_Capacitor; la topologia dei due terminali resta comunque corretta.
- Lo stato del deviatore S1 nel JSON e 'closed', ma dall'immagine simbolica il contatto e stilizzato e lo stato non e del tutto affidabile come informazione semantica; la connettivita usata nel graph risulta comunque coerente con il filo visibile tra rail 12V e pin 11 tramite S1.

**Punti incerti:**
- Il mapping dei terminali IC usa nomi geometrici (left_1, top_2, ecc.) con numeri pin OCR; tale mapping appare coerente con i fili visibili, ma senza ulteriore zoom non tutti i contatti lato corpo sono leggibili con la stessa nitidezza.
- La polarita di C2 e C3 nel JSON non e necessaria per la verifica topologica; i loro terminali alto/basso risultano comunque collegati ai nodi visibili corretti.

### c13

- Batch: `C2`
- Score: `95`
- Fedelta: `VERY_HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il graph JSON riproduce molto bene la topologia visibile: ingressi, rete di feedback, uscita verso speaker, e rail di alimentazione con fusibili e condensatori sono collegati correttamente. Non emergono net fuse/net split o collegamenti inventati. L'unico errore rilevante riguarda la semantica/polarita del condensatore di ingresso C4; alcune classi di condensatore sono semanticamente imprecise ma senza impatto topologico.

**Errori maggiori:**
- Il condensatore di ingresso C4 visibile in orizzontale ha il terminale positivo sul lato destro, mentre nel JSON polarized_capacitor20.1 e rappresentato con negative a sinistra e positive a destra. La topologia dei nodi collegati resta coerente, ma l'identita dei terminali polarizzati e invertita rispetto al simbolo visibile.

**Errori minori:**
- C6 e C2 sono condensatori non polarizzati nell'immagine ma nel JSON sono modellati come Polarized_Capacitor; i collegamenti ai nodi risultano comunque corretti.
- C7 sembra non polarizzato nell'immagine ma nel JSON e modellato come Polarized_Capacitor; la connessione serie R6-C7 verso massa resta topologicamente corretta.

**Punti incerti:**
- La corrispondenza esatta tra i reference designator visibili (R1..R6, C1..C7) e gli instance_id JSON e stata valutata tramite mapping topologico, non per nome.
- I pin IC 1..5 nel JSON risultano coerenti con le posizioni visibili; non e stato usato alcun datasheet per inferire funzioni ulteriori.

### c14

- Batch: `C2`
- Score: `94`
- Fedelta: `VERY_HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il campo graph e topologicamente molto fedele all'immagine: ingressi Power/Direction con pull-up a +5V, IC con pin 2/4/3 a sinistra e 7/6/5 a destra, nodo di alimentazione con i due condensatori, motore tra i due output estremi e rete di quattro diodi verso rail alto e GND sono rappresentati correttamente. L'unica deviazione rilevante e la classificazione dei due condensatori come polarizzati, ma i nodi collegati sono quelli giusti.

**Errori maggiori:**
- I due condensatori superiori visibili (C1 e C2) sono disegnati come condensatori non polarizzati, mentre nel JSON sono modellati come Polarized_Capacitor con terminali positive/negative. La topologia dei collegamenti resta pero coerente con l'immagine.

**Errori minori:**
- Il marking visibile nel corpo IC nell'immagine appare TC4423/TC4424 in modo non completamente coerente con il testo in basso, ma questo non altera i collegamenti del graph.

**Punti incerti:**
- Il testo nell'immagine riporta 'Motor driver using TC4424' mentre il corpo IC e il JSON riportano TC4423; la discrepanza di OCR/label non influisce sui collegamenti.
- La corrispondenza esatta R1/R2 con resistor22.1/resistor22.2 non e necessaria: entrambe le resistenze risultano correttamente collegate tra +5V e i due ingressi/terminali di controllo.
- I simboli di GND sono multipli e separati graficamente; il JSON li mantiene separati, coerentemente con la regola di non fonderli automaticamente oltre i fili visibili.

### c15

- Batch: `C2`
- Score: `94`
- Fedelta: `VERY_HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il graph JSON rappresenta molto bene la topologia visibile: +Vcc al pin 4 con C1, pin 9 con C2 e terminale +5V, pin 15 e un altro pin inferiore a GND, e i due nodi motore con i quattro diodi di ricircolo sono coerenti. L'unico errore topologico rilevante e l'assenza della connessione del pin 10 dell'IC al terminale esterno etichettato C.

**Errori maggiori:**
- Il pin superiore sinistro dell'IC etichettato 10 (nodo C) e visibilmente connesso a un terminale esterno, ma nel graph integrated_circuit11.1_top_1 risulta non connesso e manca il relativo Terminal.

**Errori minori:**
- C1 e C2 sono condensatori non polarizzati nell'immagine, ma nel JSON sono rappresentati come Polarized_Capacitor. La topologia dei due terminali resta comunque corretta.

**Punti incerti:**
- Il mapping dei terminali IC top_2/top_3/top_4 verso i pin visibili 13/14/12 dipende dall'estrazione automatica dei contatti sul bordo superiore, ma le connessioni principali ai due nodi motore e ai diodi risultano complessivamente coerenti.
- I diodi sono modellati con anodo/catodo e orientamento verticale; la corrispondenza catodo in alto verso +Vcc e anodo in basso verso GND/nodo motore appare coerente con il simbolo, senza contraddizioni certe.

### c16

- Batch: `C2`
- Score: `97`
- Fedelta: `VERY_HIGH`
- Usabile come graph base: `True`
- Spiegazione: Il campo graph riproduce fedelmente i nodi visibili principali: pin3 e il rail Vs, pin5 va a GND, pin6 e pin8 sono sui nodi intermedi della rete R1-R2-R3/C1, pin4 e sul nodo di uscita comune a motore, C2 e fondo di R3. Anche motore, C1 e C2 risultano collegati ai terminali corretti. Non emergono collegamenti inventati, mancanti o fuse/split di net; restano solo lievi imprecisioni di naming/semantica del componente variabile R3.

**Errori minori:**
- I terminali IC sono nominati come left/right/top/bottom invece che direttamente con i numeri pin visibili, ma il mapping pin3/pin4/pin5/pin6/pin8 risulta coerente con l'immagine e non altera la topologia.
- R3 e rappresentato come resistore a due terminali; nell'immagine e un potenziometro/rheostat con cursore collegato a un estremo. Topologicamente il graph conserva il collegamento visibile tra i due nodi principali, quindi l'impatto e minore.

**Punti incerti:**
- Il simbolo di R3 mostra un cursore collegato al nodo inferiore; nel graph questo e implicitamente assorbito come resistore a due terminali. Non cambia i nodi esterni visibili ma la semantica del componente e semplificata.
- I simboli di alimentazione/supply non sono modellati come componenti separati nel graph; la verifica topologica e stata fatta solo sui collegamenti terminale-terminale presenti nel JSON.
