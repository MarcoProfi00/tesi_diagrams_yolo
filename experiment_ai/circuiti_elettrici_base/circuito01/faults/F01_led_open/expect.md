# Expected diagnosis — C01_F01_led_open

## Guasto inserito
È stato cancellato un piccolo tratto del filo tra la resistenza del ramo superiore e il LED D1.

## Sintomo dichiarato
Il LED non si accende.

## Componente o terminale di interesse
Da compilare dopo la pipeline usando la debug image.

Esempi possibili:
- componente: `led...`
- terminale LED: `led..._anode`
- terminale resistenza: `resistor..._t2`

## Diagnosi attesa
Il modello dovrebbe rilevare che il ramo del LED è interrotto.

In particolare, dovrebbe individuare che il percorso tra il connettore, la resistenza superiore, il LED e il ritorno verso GND non è più completo.

## Risposta considerata corretta
La diagnosi è corretta se il modello afferma che:
- il ramo del LED è aperto/interrotto;
- il LED non ha un percorso elettrico completo;
- il problema riguarda il collegamento tra resistenza superiore e LED, oppure il tratto immediatamente vicino al LED.

## Risposta parzialmente corretta
La diagnosi è parziale se il modello individua un problema nel ramo LED ma non localizza bene il tratto interrotto.

## Risposta errata
La diagnosi è errata se il modello:
- attribuisce il problema alla lampada;
- inventa valori elettrici non presenti;
- assume un guasto interno del LED senza rilevare il problema topologico;
- ignora il ramo interrotto.