# Expected diagnosis — C03_F02_capacitor_branch_open

## Guasto inserito
È stato cancellato un collegamento di una capacità tra A, B o C.

## Sintomo dichiarato
Il nodo centrale non è più accoppiato correttamente agli altri nodi.

## Componente o terminale di interesse
Da compilare dopo la pipeline usando la debug image.

Esempi possibili:
- componente capacitor/polarized_capacitor coinvolto
- terminale positivo/negativo del condensatore
- terminale del nodo centrale C
- terminale verso A o B

## Diagnosi attesa
Il modello dovrebbe rilevare che uno dei rami capacitivi è interrotto.

## Risposta considerata corretta
La diagnosi è corretta se il modello afferma che:
- il condensatore indicato non è più collegato correttamente tra i due nodi previsti;
- il nodo centrale non è più accoppiato al nodo A o B tramite quel ramo;
- il ramo capacitivo è aperto/interrotto.

## Risposta parzialmente corretta
La diagnosi è parziale se il modello individua un problema su un condensatore ma non ricostruisce bene quali nodi sono coinvolti.

## Risposta errata
La diagnosi è errata se il modello:
- inventa valori capacitivi o effetti temporali non deducibili;
- ignora l’interruzione topologica;
- confonde il ramo capacitivo con un ramo resistivo o con una sorgente.