"""
Scenari simulativi controllati.

Questo modulo gestira, in una fase successiva, scenari generali proposti
dall'agente o dall'utente per verificare ipotesi diagnostiche tramite SPICE.

Gli scenari non devono modificare il circuito base. Devono produrre netlist e
risultati separati, cosi da poter confrontare simulazione base e simulazione
scenario in modo riproducibile.

Responsabilita previste:

- leggere scenari in formato JSON;
- validare azioni generiche e consentite;
- tradurre azioni come drive_node_voltage o close_switch in modifiche SPICE;
- generare una netlist scenario separata;
- rieseguire ngspice sullo scenario;
- confrontare risultati base e risultati scenario;
- salvare un report tracciabile per l'agente.

L'output principale sara 12_controlled_scenarios.json, con eventuali netlist e
risultati SPICE separati per ogni scenario.
"""
