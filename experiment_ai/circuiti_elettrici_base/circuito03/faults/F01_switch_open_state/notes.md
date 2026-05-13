# Notes - C03_F01_switch_open_state

## 1. Informazioni generali

| Campo | Valore |
|---|---|
| Circuito | C03_switch_capacitive_network |
| Fault ID | F01_switch_open_state |
| Tipo guasto | switch_state |
| Immagine modificata | no |
| Modifica apportata | Nessuna modifica all’immagine; viene sfruttato lo stato aperto dello switch centrale |
| Scenario | Il percorso principale del circuito non conduce come previsto |
| Componenti target | Non forniti nel prompt; target atteso `switch25.1` |
| Terminali rilevanti | Non forniti nel prompt; attesi `switch25.1_t1`, `switch25.1_t2`, `resistor22.1_t2`, `voltage_source31.1_positive` |
| Diagnosi attesa | Switch aperto: continuità assente tra i due lati del percorso tramite switch |
| Pipeline capture | 2/2 |

## 2. Verifica pipeline

| Criterio | Esito |
|---|---|
| Componente target rilevato | sì, `switch25.1` |
| Terminale target presente nel JSON | sì, `switch25.1_t1` e `switch25.1_t2` |
| Componente vicino rilevato | sì, `resistor22.1` e `voltage_source31.1` |
| Terminale vicino rilevante | sì, `resistor22.1_t2` e `voltage_source31.1_positive` |
| Terminali rilevanti presenti nel JSON | sì |
| Guasto rappresentato nel grafo | sì, tramite stato `open` dello switch |
| Warning coerenti | sì, nessun warning critico: i terminali dello switch sono collegati ai fili esterni, ma la continuità interna dipende dallo stato `open` |
| Test valutabile lato AI | sì |

## 3. Motivazione Pipeline capture

Il guasto è rappresentato correttamente nel JSON tramite lo stato dello switch.

Il componente `switch25.1` è rilevato come switch e possiede due terminali:


- switch25.1_t1
- switch25.1_t2

Nel grafo i due terminali sono collegati ai rispettivi lati esterni del circuito:
- resistor22.1_t2 <-> switch25.1_t1
- switch25.1_t2 <-> voltage_source31.1_positive

Tuttavia il componente ha stato:
- state: open
Questo significa che, anche se i fili arrivano ai due terminali dello switch, non si deve assumere continuità elettrica interna tra switch25.1_t1 e switch25.1_t2.

Il guasto quindi non è un terminale scollegato, ma una condizione topologica dipendente dallo stato del componente: il percorso tramite switch è aperto.

Pipeline capture: 2/2

## 4. Expected diagnosis

Il modello dovrebbe diagnosticare che il percorso A-B tramite lo switch centrale non conduce perché switch25.1 è in stato open.

In particolare, dovrebbe rilevare che:

switch25.1_t1 è collegato al lato proveniente da resistor22.1_t2;
switch25.1_t2 è collegato al lato verso voltage_source31.1_positive;
lo switch è però marcato come open;
quindi non si può assumere continuità interna tra i due terminali dello switch;
il percorso attraverso il ramo dello switch è interrotto per stato aperto del componente.

La risposta corretta deve distinguere la connettività dei fili esterni dallo stato interno dello switch.

## 5. Risultati modelli
| Modello         | Sintesi risultato | Totale AI /10 | End-to-end /12 | Giudizio |
| --------------- | ----------------- | ------------: | -------------: | -------- |
| GPT-5.4 | Con prompt generale individua autonomamente `switch25.1` come componente critico, riconosce lo stato `open` e diagnostica l’interruzione del percorso principale tramite switch. | 10 | 12 | Diagnosi corretta |
| GPT-5.3 Instant | Con prompt generale individua autonomamente `switch25.1` come componente critico, riconosce lo stato `open` e diagnostica l’interruzione del percorso principale tramite switch. | 10 | 12 | Diagnosi corretta |
| GPT-5.2 Instant | Con prompt generale individua autonomamente `switch25.1` come componente critico, riconosce lo stato `open` e diagnostica l’interruzione del percorso principale tramite switch. | 10 | 12 | Diagnosi corretta |


## 6. Osservazioni

Questo test è importante perché verifica se il modello considera correttamente lo stato dei componenti e non solo la connettività dei fili.

A differenza dei fault open_connection, qui non ci si aspetta necessariamente un warning unconnected_terminals. I terminali dello switch sono collegati a fili esterni, ma il percorso resta non conduttivo perché lo switch è aperto.

Il caso è utile per distinguere:

- connettività topologica del grafo;
- continuità interna del componente;
- stato operativo open/closed.

## GPT 5.4

GPT-5.4 fornisce una diagnosi corretta. Il modello, senza ricevere un componente target esplicito, individua autonomamente `switch25.1` come componente più rilevante per il sintomo.

Il modello ricostruisce correttamente i due nodi ai lati dello switch:

- `voltage_source31.1_positive` collegato a `switch25.1_t2`;
- `switch25.1_t1` collegato a `resistor22.1_t2`.

La diagnosi distingue correttamente la connettività dei fili esterni dalla continuità interna del componente: i terminali dello switch sono cablati ai rispettivi lati del circuito, ma lo switch è marcato come `open`, quindi non deve essere assunta continuità elettrica tra `switch25.1_t1` e `switch25.1_t2`.

Il report è prudente anche nei limiti: segnala che non è deducibile dal solo JSON se l’apertura dello switch sia intenzionale o guasta, né se il circuito completo si richiuderebbe correttamente una volta chiuso lo switch.

### Valutazione manuale GPT-5.4 - C03_F01_switch_open_state

| Criterio | Punteggio | Motivazione |
|---|---:|---|
| Sintomo capito | 2 | Capisce correttamente che il problema riguarda un percorso principale che non conduce. |
| Uso corretto JSON | 2 | Usa correttamente componenti, terminali, grafo e stato `open` dello switch, senza usare immagini o inventare collegamenti. |
| Ricostruzione topologica | 2 | Ricostruisce correttamente i due nodi ai lati dello switch: `voltage_source31.1_positive` / `switch25.1_t2` e `switch25.1_t1` / `resistor22.1_t2`. |
| Guasto individuato | 2 | Individua autonomamente il guasto atteso: percorso interrotto perché `switch25.1` è in stato `open`. |
| Limiti / no allucinazioni | 2 | Non inventa valori elettrici o collegamenti mancanti; distingue correttamente deduzioni certe, ipotesi plausibili e informazioni non deducibili. |

**Totale AI:** 10/10  
**Pipeline capture:** 2/2  
**End-to-end:** 12/12  
**Giudizio:** Diagnosi corretta.

## GPT 5.3 Instant

GPT-5.3 Instant fornisce una diagnosi corretta. Anche senza ricevere un componente target esplicito, individua autonomamente `switch25.1` come componente principale coinvolto nel problema.

Il modello ricostruisce correttamente i due nodi ai lati dello switch:

- `resistor22.1_t2` collegato a `switch25.1_t1`;
- `switch25.1_t2` collegato a `voltage_source31.1_positive`.

La diagnosi distingue correttamente la connettività esterna dei fili dallo stato interno del componente: i terminali dello switch sono collegati ai rispettivi lati del circuito, ma lo switch è in stato `open`, quindi non deve essere assunta continuità interna tra `switch25.1_t1` e `switch25.1_t2`.

Il report è sintetico ma corretto. Segnala correttamente che non ci sono warning della pipeline e che non è deducibile dal JSON se lo switch debba essere chiuso in condizioni normali.

### Valutazione manuale GPT-5.3 Instant - C03_F01_switch_open_state

| Criterio | Punteggio | Motivazione |
|---|---:|---|
| Sintomo capito | 2 | Capisce correttamente che il problema riguarda un percorso principale che non conduce. |
| Uso corretto JSON | 2 | Usa correttamente componenti, terminali, grafo, stato `open` dello switch e assenza di warning. |
| Ricostruzione topologica | 2 | Ricostruisce correttamente i due nodi ai lati dello switch: `resistor22.1_t2` / `switch25.1_t1` e `switch25.1_t2` / `voltage_source31.1_positive`. |
| Guasto individuato | 2 | Individua autonomamente il guasto atteso: percorso interrotto perché `switch25.1` è in stato `open`. |
| Limiti / no allucinazioni | 2 | Non inventa valori elettrici o collegamenti; distingue correttamente deduzioni certe, ipotesi plausibili e informazioni non deducibili. |

**Totale AI:** 10/10  
**Pipeline capture:** 2/2  
**End-to-end:** 12/12  
**Giudizio:** Diagnosi corretta.

## GPT 5.2 Instant

GPT-5.2 Instant fornisce una diagnosi corretta. Anche senza ricevere un componente target esplicito, identifica autonomamente `switch25.1` come componente critico per il sintomo.

Il modello ricostruisce correttamente i due nodi ai lati dello switch:

- `resistor22.1_t2` collegato a `switch25.1_t1`;
- `switch25.1_t2` collegato a `voltage_source31.1_positive`.

La diagnosi distingue correttamente tra collegamenti esterni e continuità interna del componente: i due terminali dello switch sono collegati ai rispettivi fili, ma lo switch è in stato `open`, quindi non esiste continuità elettrica tra `switch25.1_t1` e `switch25.1_t2`.

Il report è preciso anche nei limiti: segnala che non è deducibile se lo switch debba essere normalmente aperto o chiuso, né quali siano i valori elettrici o le condizioni operative. Non inventa collegamenti alternativi e non attribuisce il problema a warning assenti.

### Valutazione manuale GPT-5.2 Instant - C03_F01_switch_open_state

| Criterio | Punteggio | Motivazione |
|---|---:|---|
| Sintomo capito | 2 | Capisce correttamente che il problema riguarda un percorso principale che non conduce. |
| Uso corretto JSON | 2 | Usa correttamente componenti, terminali, grafo, stato `open` dello switch e assenza di warning. |
| Ricostruzione topologica | 2 | Ricostruisce correttamente i due nodi ai lati dello switch: `resistor22.1_t2` / `switch25.1_t1` e `switch25.1_t2` / `voltage_source31.1_positive`. |
| Guasto individuato | 2 | Individua autonomamente il guasto atteso: percorso interrotto perché `switch25.1` è in stato `open`. |
| Limiti / no allucinazioni | 2 | Non inventa valori elettrici, collegamenti o percorsi alternativi; distingue bene deduzioni certe, ipotesi plausibili e informazioni non deducibili. |

**Totale AI:** 10/10  
**Pipeline capture:** 2/2  
**End-to-end:** 12/12  
**Giudizio:** Diagnosi corretta.