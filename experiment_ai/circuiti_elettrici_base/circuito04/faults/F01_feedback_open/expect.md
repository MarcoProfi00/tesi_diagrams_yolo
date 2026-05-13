# Expected diagnosis — C04_F01_feedback_open

## Guasto inserito
È stato cancellato un tratto del collegamento di feedback tra l’uscita dell’opamp e R2.

## Sintomo dichiarato
L’uscita dell’opamp non è stabile o satura.

## Componente o terminale di interesse
Da compilare dopo la pipeline usando la debug image.

Esempi possibili:
- componente opamp
- terminale di uscita dell’opamp
- componente R2
- terminale di R2 collegato all’uscita
- terminale di R2 collegato all’ingresso invertente

## Diagnosi attesa
Il modello dovrebbe rilevare che il percorso di feedback è interrotto.

## Risposta considerata corretta
La diagnosi è corretta se il modello afferma che:
- il collegamento tra uscita e ramo di feedback non è completo;
- R2 non collega più correttamente uscita e ingresso dell’opamp;
- l’opamp perde la retroazione topologica prevista.

## Risposta parzialmente corretta
La diagnosi è parziale se il modello indica un problema sul ramo R2/opamp ma non riconosce chiaramente il feedback interrotto.

## Risposta errata
La diagnosi è errata se il modello:
- assume che il feedback sia presente senza verificarlo;
- inventa valori di guadagno;
- conclude una saturazione certa senza distinguere tra topologia e comportamento elettrico.