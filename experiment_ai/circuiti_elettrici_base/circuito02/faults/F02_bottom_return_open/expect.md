# Expected diagnosis — C02_F02_bottom_return_open

## Guasto inserito
È stato cancellato un tratto del rail inferiore vicino allo shunt resistor o all’ohmmeter.

## Sintomo dichiarato
Il circuito non si chiude correttamente.

## Componente o terminale di interesse
Da compilare dopo la pipeline usando la debug image.

Esempi possibili:
- terminale dello shunt resistor
- terminale dell’ohmmeter
- terminale del ramo inferiore
- terminale del meter

## Diagnosi attesa
Il modello dovrebbe rilevare che il percorso di ritorno inferiore è interrotto.

## Risposta considerata corretta
La diagnosi è corretta se il modello afferma che:
- il rail inferiore non è più continuo;
- il percorso di ritorno del circuito è interrotto;
- uno o più rami non riescono a chiudere il circuito verso il nodo inferiore.

## Risposta parzialmente corretta
La diagnosi è parziale se il modello parla di circuito aperto ma non identifica chiaramente il ritorno inferiore.

## Risposta errata
La diagnosi è errata se il modello:
- ignora il percorso di ritorno;
- inventa problemi di misura non deducibili dal JSON;
- attribuisce il problema a valori mancanti invece che a un’interruzione topologica.