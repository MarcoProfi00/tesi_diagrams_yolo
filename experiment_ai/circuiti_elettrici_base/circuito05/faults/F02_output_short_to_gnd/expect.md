# Expected diagnosis — C05_F02_output_short_to_gnd

## Guasto inserito
È stato disegnato un corto tra il nodo VOUT e GND/rail negativo.

## Sintomo dichiarato
L’uscita resta bloccata bassa.

## Componente o terminale di interesse
Da compilare dopo la pipeline usando la debug image.

Esempi possibili:
- terminale VOUT
- terminale del transistor di uscita
- terminale GND
- terminale sul rail negativo
- collegamento tra uscita e massa

## Diagnosi attesa
Il modello dovrebbe rilevare che l’uscita è cortocircuitata verso massa o verso il rail negativo.

## Risposta considerata corretta
La diagnosi è corretta se il modello afferma che:
- il nodo di uscita è collegato impropriamente al nodo GND/rail negativo;
- l’uscita non è più indipendente dal riferimento basso;
- è presente un corto topologico tra uscita e massa/rail negativo.

## Risposta parzialmente corretta
La diagnosi è parziale se il modello capisce che l’uscita è bloccata o collegata a un nodo basso, ma non usa chiaramente il concetto di corto.

## Risposta errata
La diagnosi è errata se il modello:
- attribuisce il problema solo a un transistor guasto senza evidenza;
- inventa valori di tensione;
- non rileva la fusione tra uscita e nodo basso.