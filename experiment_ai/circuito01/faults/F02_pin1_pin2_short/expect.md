# Expected diagnosis — C01_F02_pin1_pin2_short

## Guasto inserito
È stato disegnato un ponte tra il ramo superiore del LED e il ramo inferiore della lampada.

## Sintomo dichiarato
LED e lampada si attivano insieme.

## Componente o terminale di interesse
Da compilare dopo la pipeline usando la debug image.

Esempi possibili:
- `connector..._pin1`
- `connector..._pin2`
- terminale della resistenza del ramo LED
- terminale della resistenza del ramo lampada

## Diagnosi attesa
Il modello dovrebbe rilevare che i due rami, originariamente separati, risultano fusi o cortocircuitati.

## Risposta considerata corretta
La diagnosi è corretta se il modello afferma che:
- il ramo LED e il ramo lampada condividono impropriamente lo stesso nodo;
- `pin1` e `pin2`, o i rispettivi rami, non sono più indipendenti;
- è presente un corto o una fusione di nodi tra i due rami.

## Risposta parzialmente corretta
La diagnosi è parziale se il modello capisce che LED e lampada sono collegati insieme, ma non spiega chiaramente che il problema è un corto/fusione tra nodi.

## Risposta errata
La diagnosi è errata se il modello:
- interpreta l’attivazione simultanea come comportamento normale;
- attribuisce il problema a valori di resistenza non presenti;
- non rileva che i due rami sono stati collegati tra loro.