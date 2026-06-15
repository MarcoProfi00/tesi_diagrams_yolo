"""
Costruzione del contesto diagnostico per l'agente.

Questo modulo aggrega gli output della Pipeline 2.0 in un unico pacchetto
ordinato, pensato per essere letto da un agente AI o da una futura chat.

Il contesto deve essere generale: deve funzionare per Batch A, Batch B, Batch C1,
Batch C2 e per circuiti con livelli diversi di simulabilita.

Responsabilita previste:

- raccogliere Graph JSON, circuito normalizzato e node map;
- includere valori dichiarati, assunzioni e parametri mancanti;
- includere regole dei componenti e decisioni di conversione;
- includere netlist SPICE e risultati di ngspice;
- includere la sintesi prodotta da 09_summarize_spice.py;
- dichiarare limiti, warning e stato del circuito;
- preparare un input strutturato e tracciabile per l'agente.

L'output principale sara 10_diagnostic_context.json.
"""
