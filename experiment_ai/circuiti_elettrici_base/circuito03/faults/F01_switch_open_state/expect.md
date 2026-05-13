# Expected diagnosis — C03_F01_switch_open_state

## Guasto / condizione inserita
Non è stata modificata l’immagine originale.

Il problema considerato è che lo switch centrale è in stato aperto. Di conseguenza, il percorso A-B attraverso il ramo dello switch non conduce.

## Sintomo dichiarato
Il percorso A-B tramite switch non conduce.

## Componente o terminale di interesse
Da compilare dopo la pipeline usando la debug image.

Esempi possibili:
- componente switch: `switch...`
- terminale sinistro dello switch: `switch..._t1`
- terminale destro dello switch: `switch..._t2`
- terminale del resistore collegato allo switch
- terminale della sorgente di tensione collegata allo switch

## Diagnosi attesa
Il modello dovrebbe rilevare che il ramo dello switch non garantisce continuità perché lo switch è aperto.

La diagnosi attesa non è necessariamente un filo interrotto, ma una condizione di stato: lo switch può avere terminali collegati ai fili, ma la continuità elettrica tra i due terminali dipende dallo stato `open/closed`.

## Risposta considerata corretta
La diagnosi è corretta se il modello afferma che:
- il componente di interesse è uno switch;
- lo switch risulta aperto oppure non risulta in stato conduttivo;
- il percorso A-B tramite lo switch non può essere considerato chiuso;
- il problema è coerente con uno switch aperto, non necessariamente con un filo mancante.

## Risposta parzialmente corretta
La diagnosi è parziale se il modello:
- individua il ramo centrale dello switch come zona problematica;
- capisce che manca continuità nel ramo;
- però non distingue chiaramente tra filo interrotto e switch aperto.

## Risposta errata
La diagnosi è errata se il modello:
- ignora lo stato dello switch;
- considera automaticamente i due terminali dello switch come cortocircuitati;
- inventa un filo interrotto non presente;
- attribuisce il problema a condensatori, sorgenti o GND senza evidenza nel JSON.