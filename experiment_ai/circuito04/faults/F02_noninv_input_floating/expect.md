# Expected diagnosis — C04_F02_noninv_input_floating

## Guasto inserito
È stato cancellato il ramo collegato all’ingresso positivo/non invertente dell’opamp.

In particolare, sono stati rimossi sia il filo di collegamento sia il riferimento a massa/GND. Di conseguenza, il terminale positivo dell’opamp non risulta più collegato a un riferimento elettrico.

## Sintomo dichiarato
L’opamp non ha riferimento sull’ingresso positivo.

## Componente o terminale di interesse
Da compilare dopo la pipeline usando la debug image.

Esempi possibili:
- terminale di ingresso positivo/non invertente dell’opamp
- terminale `in2` dell’opamp, se nel JSON corrisponde all’ingresso positivo
- componente opamp
- eventuale terminale isolato vicino all’ingresso positivo

## Diagnosi attesa
Il modello dovrebbe rilevare che l’ingresso positivo/non invertente dell’opamp è flottante o non collegato a nessun riferimento.

La diagnosi attesa non è soltanto “manca il collegamento a GND”, ma più precisamente:
- il ramo di riferimento dell’ingresso positivo è assente;
- il terminale dell’opamp non è collegato a massa;
- l’ingresso positivo risulta isolato, flottante o topologicamente ambiguo.

## Risposta considerata corretta
La diagnosi è corretta se il modello afferma che:
- l’ingresso positivo/non invertente dell’opamp non è collegato a GND;
- il ramo di riferimento è stato rimosso o risulta assente;
- il terminale indicato è flottante, isolato o privo di riferimento;
- il comportamento anomalo dell’opamp è compatibile con la mancanza del riferimento sull’ingresso positivo.

## Risposta parzialmente corretta
La diagnosi è parziale se il modello:
- rileva un problema sull’ingresso dell’opamp;
- parla di collegamento mancante o ingresso non riferito;
- ma non specifica chiaramente che il ramo positivo è completamente flottante/non collegato.

## Risposta errata
La diagnosi è errata se il modello:
- assume che l’ingresso positivo sia ancora collegato a GND;
- assume automaticamente che tutti i simboli GND siano equivalenti senza collegamento esplicito;
- attribuisce il problema al feedback R2 senza evidenza;
- inventa valori di guadagno, tensioni o saturazioni certe non deducibili dal JSON;
- ignora che il terminale positivo dell’opamp è privo di riferimento.