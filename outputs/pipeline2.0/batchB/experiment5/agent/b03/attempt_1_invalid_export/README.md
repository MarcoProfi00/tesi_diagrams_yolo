# Tentativo AGENT 1 — non valido per la verifica transitoria

Questo archivio conserva senza modifiche la cronologia e gli scenari della prima esecuzione AGENT di b03.

Le prove statiche a 9 V e 15 V sono artefatti SPICE validi. La rampa transitoria non deve invece essere usata per valutare la sequenza dei LED: la netlist di quel tentativo non salvava esplicitamente i vettori di corrente interna dei diodi (`@d...[id]`), quindi ngspice ripeteva il valore finale nel CSV temporale.

La root attiva `agent/b03/` e stata rigenerata con l'export corretto. Il nuovo tentativo AGENT deve partire da quella root, con budget e cronologia separati.
