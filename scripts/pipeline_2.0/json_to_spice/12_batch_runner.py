"""
Esecuzione della pipeline 2.0 su batch di circuiti.

Questo modulo gestisce l'applicazione della stessa pipeline ai diversi insiemi
di test: Batch A, Batch B, Batch C1 e Batch C2.

La pipeline deve essere unica. I batch rappresentano livelli crescenti di
difficolta, non sistemi diversi.

Responsabilita previste:

- individuare i Graph JSON prodotti dalla pipeline_1.0;
- creare cartelle di output per ogni circuito;
- eseguire in ordine i moduli della pipeline 2.0;
- raccogliere stati READY/PARTIAL/NOT_READY;
- produrre riepiloghi per batch;
- permettere esecuzioni su un singolo circuito o su tutto un batch.
"""
