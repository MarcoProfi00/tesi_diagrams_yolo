"""
Costruzione del report elettrico finale.

Questo modulo aggrega gli output della pipeline 2.0 in un report unico e
leggibile.

Il report dovra essere prodotto sempre, anche quando la netlist non e completa
o ngspice non viene eseguito.

Contenuti previsti:

- stato del circuito: READY, PARTIAL o NOT_READY;
- componenti convertiti;
- componenti semplificati;
- componenti non simulabili;
- parametri mancanti;
- warning originali e nuovi warning elettrici;
- sintesi della node map;
- esito della generazione SPICE;
- esito della simulazione, se disponibile;
- limiti e assunzioni.
"""
