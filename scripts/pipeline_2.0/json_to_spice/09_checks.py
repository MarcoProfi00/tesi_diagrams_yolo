"""
Controlli elettrici automatici.

Questo modulo produce verifiche strutturali ed elettriche anche quando SPICE
non puo essere eseguito.

I controlli sono fondamentali per Batch B, C1 e C2, dove molti circuiti saranno
parzialmente simulabili o non simulabili internamente.

Controlli previsti:

- presenza di GND;
- presenza di alimentazioni;
- terminali scollegati;
- nodi flottanti;
- componenti senza valore;
- modelli mancanti;
- polarita di LED e diodi;
- stato degli switch;
- pin principali degli IC tramite device profile;
- componenti non convertibili in SPICE.

L'output principale sara electrical_check_report.json.
"""
