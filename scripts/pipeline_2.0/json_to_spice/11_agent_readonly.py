"""
Agente diagnostico in sola lettura.

Questo modulo sara la prima versione minima dell'agente AI. Leggera il contesto
diagnostico prodotto dallo step 10 e rispondera a una domanda dell'utente senza
modificare file, valori o netlist.

La logica deve restare generale per tutti i batch: l'agente non deve conoscere
casi speciali come a01, a02 o a10, ma deve usare solo il contesto fornito dalla
pipeline.

Responsabilita previste:

- leggere 10_diagnostic_context.json;
- leggere una domanda o un sintomo dell'utente;
- costruire un prompt controllato per il modello AI;
- distinguere fatti, risultati SPICE, assunzioni e ipotesi;
- salvare una risposta diagnostica tracciabile;
- non eseguire scenari e non modificare la netlist.

L'output principale sara 11_agent_response.md.
"""
