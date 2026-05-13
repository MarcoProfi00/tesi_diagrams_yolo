# Expected diagnosis — C02_F01_top_rail_open

## Guasto inserito
È stato cancellato un tratto del rail superiore dopo la square source o prima del nodo B.

## Sintomo dichiarato
I rami a destra non ricevono alimentazione.

## Componente o terminale di interesse
Da compilare dopo la pipeline usando la debug image.

Esempi possibili:
- terminale della square source
- terminale del componente sul nodo B
- terminale del fotoresistore
- terminale dell’induttore
- terminale del ramo di output

## Diagnosi attesa
Il modello dovrebbe rilevare che il rail superiore è interrotto e che i rami a destra risultano isolati dalla parte di alimentazione.

## Risposta considerata corretta
La diagnosi è corretta se il modello afferma che:
- il rail superiore non forma più un nodo continuo;
- i rami a destra non sono più collegati al percorso di alimentazione;
- il problema è un’interruzione topologica sul nodo/rail superiore.

## Risposta parzialmente corretta
La diagnosi è parziale se il modello rileva un’interruzione generale del circuito ma non localizza chiaramente il rail superiore.

## Risposta errata
La diagnosi è errata se il modello:
- attribuisce il problema a un singolo componente senza evidenza topologica;
- inventa valori o tensioni non presenti;
- non rileva la separazione del rail superiore.