"""
Gestione dei device profile per componenti complessi e circuiti integrati.

Questo modulo gestisce profili dichiarativi per IC e blocchi funzionali che non
possono sempre essere simulati internamente in SPICE.

I device profile dovranno descrivere informazioni come:

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
