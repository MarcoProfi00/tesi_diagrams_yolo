"""
Sintesi standardizzata dei risultati SPICE.

Questo modulo prendera gli output grezzi prodotti da 08_spice_run.py e li
riassumera in una forma semplice, stabile e riutilizzabile per tutti i batch.

Non deve essere un agente e non deve fare diagnosi libera. Deve solo trasformare
stdout, stderr, report di emissione e regole componenti in una sintesi tecnica
chiara.

Responsabilita previste:

- indicare se ngspice e stato eseguito;
- registrare exit code, stato e presenza di stderr;
- riportare warning principali di ngspice;
- riportare componenti non emessi, semplificati o non supportati;
- indicare switch aperti o componenti strutturali saltati;
- mantenere i riferimenti ai file stdout/stderr originali.

L'output principale sara 09_spice_summary.json.
"""
