# Expected diagnosis — C05_F01_base_q2_open

## Guasto inserito
È stato cancellato il collegamento tra il nodo di Q1 e la base di Q2.

## Sintomo dichiarato
Q2 non viene pilotato correttamente.

## Componente o terminale di interesse
Da compilare dopo la pipeline usando la debug image.

Esempi possibili:
- base di Q2
- collettore/base di Q1
- terminale del nodo di polarizzazione tra Q1 e Q2
- terminale del transistor Q2

## Diagnosi attesa
Il modello dovrebbe rilevare che il nodo di polarizzazione/base di Q2 è interrotto.

## Risposta considerata corretta
La diagnosi è corretta se il modello afferma che:
- la base di Q2 non è più collegata al nodo proveniente da Q1;
- il percorso di pilotaggio/polarizzazione di Q2 è aperto;
- Q2 non può essere pilotato tramite il collegamento previsto.

## Risposta parzialmente corretta
La diagnosi è parziale se il modello rileva un problema intorno a Q2 ma non identifica il collegamento base/nodo di polarizzazione.

## Risposta errata
La diagnosi è errata se il modello:
- inventa stati di conduzione certi dei transistor;
- attribuisce il problema a valori di resistenza non presenti;
- non rileva l’interruzione del collegamento verso la base di Q2.