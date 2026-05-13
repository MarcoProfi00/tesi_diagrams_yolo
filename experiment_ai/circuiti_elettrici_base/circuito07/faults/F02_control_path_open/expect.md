# Expected diagnosis — C07_F02_control_path_open

## Guasto inserito
È stato cancellato un collegamento nel ramo di controllo D1/Q1/D2.

## Sintomo dichiarato
Il controllo di carica non funziona.

## Componente o terminale di interesse
Da compilare dopo la pipeline usando la debug image.

Esempi possibili:
- diodo D1
- transistor Q1
- diodo D2
- terminale base del transistor
- terminale del ramo di controllo verso la rete resistiva

## Diagnosi attesa
Il modello dovrebbe rilevare che il percorso di controllo è interrotto o incompleto.

## Risposta considerata corretta
La diagnosi è corretta se il modello afferma che:
- il ramo D1/Q1/D2 non forma più un percorso completo;
- il transistor di controllo non è collegato correttamente al resto della rete;
- la rete di controllo della carica è interrotta o ambigua.

## Risposta parzialmente corretta
La diagnosi è parziale se il modello individua un problema nella rete di controllo ma non localizza chiaramente D1/Q1/D2.

## Risposta errata
La diagnosi è errata se il modello:
- inventa il funzionamento esatto dello SCR senza che sia rappresentato correttamente nel JSON;
- attribuisce il problema al fusibile o all’uscita senza evidenza;
- non rileva l’interruzione nel ramo di controllo.