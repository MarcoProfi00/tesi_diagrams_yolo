"""
Gestione dei device profile per componenti complessi e circuiti integrati.

Questo modulo riserva il contratto futuro per profili dichiarativi di IC e
blocchi funzionali che non possono sempre essere simulati internamente in
SPICE. Non e ancora importato da `run_pipeline2.py` e non produce artefatti.

I device profile potranno descrivere informazioni come:

- pin di alimentazione;
- pin di massa;
- reset;
- clock;
- enable;
- ingressi e uscite;
- pin non connessi;
- vincoli minimi di funzionamento;
- eventuale subcircuit o macromodello disponibile.

La funzione principale dei profili e permettere controlli pin-aware nei Batch
C1 e C2, anche quando non esiste un modello SPICE affidabile.
"""
