"""
Package della pipeline 2.0 per la conversione JSON -> SPICE/report.

I moduli contenuti qui implementeranno il passaggio dal Graph JSON prodotto
dalla pipeline_1.0 a una rappresentazione elettrica piu vicina a SPICE.

Il package e volutamente separato dalla pipeline_1.0: la prima pipeline resta
responsabile della visione e della costruzione del grafo, mentre questa parte
lavora solo sul JSON topologico gia esportato.
"""
