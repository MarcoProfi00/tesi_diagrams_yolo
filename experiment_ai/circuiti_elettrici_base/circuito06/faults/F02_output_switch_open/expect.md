# Expected diagnosis — C06_F02_secondary_switch_open

## Guasto inserito
Non è stata modificata l’immagine del circuito.

Il guasto è rappresentato dallo stato del componente di commutazione sul lato secondario: lo switch del ramo di destra è aperto. Di conseguenza, il percorso elettrico verso il ramo di uscita / lato Vgrid non è elettricamente chiuso.

## Sintomo dichiarato
Sul lato secondario non compare uscita verso il ramo di destra.

## Componente o terminale di interesse
Da compilare dopo la pipeline usando la debug image.

Esempi possibili:
- switch sul lato secondario
- switch del ramo di destra
- componente `switch...`
- eventuali terminali dello switch sul secondario

## Diagnosi attesa
Il modello dovrebbe rilevare che il ramo secondario verso destra è interrotto non per assenza di fili, ma perché lo switch presente in quel ramo è nello stato `open`.

La diagnosi attesa è quindi:
- il percorso sul secondario verso il ramo di uscita non è chiuso;
- lo switch del secondario è aperto;
- la continuità elettrica attraverso quel ramo non è disponibile.

## Risposta considerata corretta
La diagnosi è corretta se il modello afferma che:
- il ramo di uscita sul secondario dipende da uno switch;
- lo switch è aperto;
- per questo il percorso verso il lato destro / Vgrid / uscita non è elettricamente completo;
- il problema è di stato del componente, non necessariamente di collegamento grafico mancante.

## Risposta parzialmente corretta
La diagnosi è parziale se il modello:
- individua che il ramo secondario è interrotto;
- oppure dice che il percorso verso destra non è completo;
- ma non esplicita chiaramente che la causa è lo stato `open` dello switch.

## Risposta errata
La diagnosi è errata se il modello:
- considera il ramo chiuso solo perché i fili arrivano ai terminali dello switch;
- ignora completamente lo stato open/closed;
- attribuisce il problema a trasformatore, induttore o resistenza senza evidenza topologica;
- inventa tensioni, correnti o guasti funzionali non presenti nel JSON;
- dichiara con certezza che il secondario è fisicamente scollegato da un filo mancante, se il vero problema è lo switch aperto.

## Nota metodologica
Questo caso serve a verificare se il modello distingue correttamente tra:
- connettività topologica del grafo dei terminali
- continuità elettrica effettiva condizionata dallo stato di uno switch