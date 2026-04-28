# Expected diagnosis — C07_F01_fuse_to_output_open

## Guasto inserito
È stato cancellato il collegamento verso il fusibile F1 oppure subito dopo F1, nel ramo che porta al terminale finale di uscita.

## Sintomo dichiarato
Il ramo di uscita verso il terminale finale non conduce.

## Componente o terminale di interesse
Da compilare dopo la pipeline usando la debug image.

Esempi possibili:
- componente fuse / fusibile
- terminale del fusibile
- terminale di uscita finale
- terminale dopo il fusibile
- resistore R6 o terminale collegato al ramo di uscita

## Diagnosi attesa
Il modello dovrebbe rilevare che il percorso verso il terminale finale di uscita è interrotto.

La diagnosi attesa non richiede di sapere che quel terminale rappresenta una batteria o un carico. È sufficiente riconoscere che il ramo di uscita non è più topologicamente completo.

## Risposta considerata corretta
La diagnosi è corretta se il modello afferma che:
- il terminale finale di uscita risulta isolato o non raggiungibile dal resto del circuito;
- il percorso verso il terminale di uscita è interrotto nella zona del fusibile o del ramo finale;
- il fusibile, o il collegamento immediatamente vicino al fusibile, interrompe la continuità verso l’uscita;
- il problema è un’interruzione topologica del ramo di uscita.

## Risposta parzialmente corretta
La diagnosi è parziale se il modello:
- rileva un’interruzione nel ramo destro/finale;
- capisce che il terminale di uscita non è correttamente collegato;
- ma non localizza chiaramente il problema nella zona del fusibile.

## Risposta errata
La diagnosi è errata se il modello:
- assume informazioni non presenti, per esempio che il terminale sia certamente una batteria;
- inventa tensioni, correnti o valori elettrici;
- attribuisce il problema al trasformatore, al transistor o ai diodi senza evidenza topologica;
- non rileva che il ramo verso il terminale finale è interrotto.