# b05 CHAT - tentativo 01

Archivio della sessione CHAT conservata prima della correzione del gate
`intent` degli scenari.

## Motivo dell'archiviazione

Lo scenario che chiudeva lo switch verificava alimentazione e corrente di
batteria, ma non misurava direttamente un segnale audio sulla cuffia. Poiche il
JSON non dichiarava `intent`, il runtime precedente lo interpretava come
`correction` e produceva erroneamente `resolved_candidate` con stop attivo.

Questi artefatti restano disponibili come evidenza per la futura valutazione
di Experiment 5; non devono essere usati come stato corrente della nuova
sessione CHAT.

## Contenuto

- history e registro della conversazione in `experiment_chat/`;
- run eseguite in `scenarios/`;
- contesto, prompt e risposta CHAT negli artefatti `10` e `11`.

La base run `01-08`, il viewer `13-15` e il workspace `agent/b05` non fanno
parte dell'archivio e non sono stati modificati dal reset.
