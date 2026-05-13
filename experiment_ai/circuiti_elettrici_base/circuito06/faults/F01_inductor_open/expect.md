# Expected diagnosis — C06_F01_inductor_open

## Guasto inserito
È stato cancellato un tratto tra lo stadio transistor e l’induttore L.

## Sintomo dichiarato
Il trasformatore non viene pilotato.

## Componente o terminale di interesse
Da compilare dopo la pipeline usando la debug image.

Esempi possibili:
- induttore L
- terminale dell’induttore lato transistor
- terminale dell’induttore lato primario
- terminale del primario del trasformatore

## Diagnosi attesa
Il modello dovrebbe rilevare che il percorso verso l’induttore L e il primario del trasformatore è interrotto.

## Risposta considerata corretta
La diagnosi è corretta se il modello afferma che:
- il collegamento tra stadio transistor, induttore e primario non è completo;
- l’induttore o il primario risultano isolati dal ramo di pilotaggio;
- il trasformatore non può essere pilotato perché il percorso topologico è aperto.

## Risposta parzialmente corretta
La diagnosi è parziale se il modello rileva un’interruzione nella zona LC/trasformatore ma non la localizza bene.

## Risposta errata
La diagnosi è errata se il modello:
- inventa condizioni di oscillazione non presenti;
- attribuisce il problema al secondario;
- non rileva l’interruzione del percorso verso L/primario.