"""
Esecuzione opzionale di ngspice.

Questo modulo lancia ngspice sulle netlist generate quando il circuito e
simulabile e il simulatore e disponibile nel sistema.

La pipeline non deve fallire se ngspice manca o se la simulazione non converge.
In questi casi deve produrre un risultato strutturato con lo stato dell'errore.

Responsabilita previste:

- verificare disponibilita di ngspice;
- eseguire netlist in batch mode;
- raccogliere log, errori e codice di uscita;
- estrarre risultati .op, .tran o .measure quando disponibili;
- salvare spice_results.json.
"""
