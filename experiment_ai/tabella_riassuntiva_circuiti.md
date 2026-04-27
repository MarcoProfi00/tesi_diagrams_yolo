# Benchmark AI su JSON topologici

## Obiettivo

Valutare se diversi modelli linguistici sono in grado di ricostruire la topologia di un circuito elettrico a partire esclusivamente dal JSON prodotto dal passo 05 della pipeline.

## Criteri di valutazione

| Criterio | Descrizione |
|---|---|
| Componenti | Il modello riconosce correttamente i componenti presenti nel JSON |
| Nodi / topologia | Il modello ricostruisce correttamente i nodi principali e i collegamenti |
| Tipo di circuito | Il modello propone una classificazione funzionale prudente e coerente |
| Ambiguità | Il modello segnala correttamente limiti, incertezze e informazioni mancanti |
| Allucinazioni | Il modello evita di inventare valori, funzioni o collegamenti non presenti |
| Giudizio finale | Valutazione complessiva del report prodotto |

## Risultati sintetici

| Circuito | Modello | Componenti | Nodi / topologia | Tipo di circuito | Ambiguità | Assenza Allucinazioni | Totale/10 | Giudizio finale |
|---|---|---|---|---|---|---|---|---|
| Circuito 01 | GPT-5.4 / forte | 2 | 2 | 2 | 2 | 2 | 10 | Topologia chiara |
| Circuito 01 | GPT-5.3 Instant | 2 | 2 | 2 | 2 | 2 | 10 | Topologia chiara |
| Circuito 01 | GPT-5.2 Instant | 2 | 2 | 2 | 2 | 2 | 10 | Topologia chiara |
| Circuito 01 | GPT-o3 legacy | 2 | 2 | 2 | 2 | 2 | 10 | Topologia chiara |
| Circuito 02 | GPT-5.4 / forte | 2 | 2 | 2 | 2 | 2 | 10 | Topologia chiara |
| Circuito 02 | GPT-5.3 Instant | 2 | 2 | 2 | 2 | 2 | 10 | Topologia chiara |
| Circuito 02 | GPT-5.2 Instant | 2 | 2 | 2 | 2 | 2 | 10 | Topologia chiara |
| Circuito 02 | GPT-o3 legacy | 2 | 2 | 1 | 2 | 1 | 8 | Topologia chiara, interpretazione funzionale troppo specifica |
| Circuito 03 | GPT-5.4 / forte | 2 | 2 | 2 | 2 | 2 | 10 | Topologia chiara |
| Circuito 03 | GPT-5.3 Instant | 2 | 2 | 2 | 2 | 2 | 10 | Topologia chiara |
| Circuito 03 | GPT-5.2 Instant | 2 | 2 | 2 | 2 | 2 | 10 | Topologia chiara |
| Circuito 03 | GPT-o3 legacy | 2 | 2 | 1 | 2 | 1 | 8 | Topologia chiara, interpretazione funzionale troppo specifica |
| Circuito 04 | GPT-5.4 / forte | 2 | 2 | 2 | 2 | 2 | 10 | Topologia chiara |
| Circuito 04 | GPT-5.3 Instant | 2 | 2 | 2 | 2 | 2 | 10 | Topologia chiara |
| Circuito 04 | GPT-5.2 Instant | 2 | 2 | 2 | 2 | 2 | 10 | Topologia chiara |
| Circuito 04 | GPT-o3 legacy | 2 | 2 | 2 | 2 | 1 | 9 | Topologia chiara, interpretazione leggermente troppo assertiva |
| Circuito 05 | GPT-5.4 / forte | 2 | 1 | 2 | 2 | 1 | 8 | Topologia parzialmente chiara |
| Circuito 05 | GPT-5.3 Instant | 2 | 2 | 2 | 2 | 2 | 10 | Topologia chiara |
| Circuito 05 | GPT-5.2 Instant | 2 | 2 | 2 | 2 | 2 | 10 | Topologia chiara |
| Circuito 05 | GPT-o3 legacy | 2 | 2 | 1 | 2 | 1 | 8 | Topologia chiara, interpretazione funzionale troppo specifica |
| Circuito 06 | GPT-5.4 / forte | 2 | 1 | 2 | 2 | 2 | 10 | Topologia chiara |
| Circuito 06 | GPT-5.3 Instant | 2 | 2 | 2 | 2 | 2 | 10 | Topologia chiara |
| Circuito 06 | GPT-5.2 Instant | 2 | 2 | 2 | 2 | 2 | 10 | Topologia chiara |
| Circuito 06 | GPT-o3 legacy | 2 | 2 | 2 | 2 | 1 | 9 | Topologia chiara, interpretazione leggermente troppo specifica |
| Circuito 07 | GPT-5.4 / forte | 1 | 2 | 2 | 2 | 2 | 9 | Topologia chiara, ma componenti parzialmente corretti 
| Circuito 07 | GPT-5.3 Instant | 1 | 2 | 2 | 2 | 2 | 9 | Topologia chiara, ma componenti parzialmente corretti |
| Circuito 07 | GPT-5.2 Instant | 2 | 2 | 2 | 2 | 2 | 10 | Topologia chiara |
| Circuito 07 | GPT-o3 legacy | 2 | 2 | 1 | 2 | 1 | 8 | Topologia chiara, interpretazione funzionale troppo specifica |
