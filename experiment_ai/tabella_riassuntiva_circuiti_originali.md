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
| Circuito 06 | GPT-5.4 / forte | 2 | 2 | 2 | 2 | 2 | 10 | Topologia chiara |
| Circuito 06 | GPT-5.3 Instant | 2 | 2 | 2 | 2 | 2 | 10 | Topologia chiara |
| Circuito 06 | GPT-5.2 Instant | 2 | 2 | 2 | 2 | 2 | 10 | Topologia chiara |
| Circuito 06 | GPT-o3 legacy | 2 | 2 | 2 | 2 | 1 | 9 | Topologia chiara, interpretazione leggermente troppo specifica |
| Circuito 07 | GPT-5.4 / forte | 1 | 2 | 2 | 2 | 2 | 9 | Topologia chiara, ma componenti parzialmente corretti 
| Circuito 07 | GPT-5.3 Instant | 1 | 2 | 2 | 2 | 2 | 9 | Topologia chiara, ma componenti parzialmente corretti |
| Circuito 07 | GPT-5.2 Instant | 1 | 2 | 2 | 2 | 2 | 9 | Topologia chiara, ma componenti parzialmente corretti |
| Circuito 07 | GPT-o3 legacy | 1 | 1 | 1 | 2 | 1 | 6 | Topologia parzialmente chiara, interpretazione troppo assertiva |

| Modello | Totale su 70 | Media /10 | Osservazione |
|---|---:|---:|---|
| GPT-5.4 / forte | 67/70 | 9.57 | Molto buono, ma ha avuto una contraddizione interna sul Circuito 05 |
| GPT-5.3 Instant | 69/70 | 9.86 | Miglior compromesso: molto accurato e più leggero |
| GPT-5.2 Instant | 69/70 | 9.86 | Molto simile a 5.3, ottimo candidato economico |
| o3 / reasoning  | 58/70 | 8.29 | Capisce spesso i nodi, ma tende a interpretare troppo |

### Legenda

### Scala usata

| Valore | Significato |
|---:|---|
| 2 | Corretto o molto utile |
| 1 | Parziale, incompleto o ambiguo |
| 0 | Errato, insufficiente o non utile |
| N/D | Test non eseguito |

#### Componenti
| Punteggio | Criterio |
|---:|---|
| 2 | Elenca correttamente quasi tutti i componenti e le classi |
| 1 | Riconosce i componenti principali ma omette o confonde qualche elemento |
| 0 | Sbaglia componenti importanti o inventa componenti non presenti |

#### Nodi / topologia
| Punteggio | Criterio |
|---:|---|
| 2 | Ricostruisce correttamente i nodi principali e i collegamenti |
| 1 | Ricostruisce la maggior parte dei nodi ma perde qualche dettaglio |
| 0 | Sbaglia la struttura dei nodi o interpreta male i collegamenti |

#### Tipo di circuito
| Punteggio | Criterio |
|---:|---|
| 2 | Propone una classificazione plausibile e prudente |
| 1 | Capisce solo genericamente il circuito |
| 0 | Classifica il circuito in modo sbagliato o troppo inventato |

#### Ambiguità
| Punteggio | Criterio |
|---:|---|
| 2 | Segnala correttamente limiti importanti del JSON |
| 1 | Segnala solo alcune ambiguità |
| 0 | Non segnala limiti o dà tutto per certo |

#### Assenza allucinazioni
| Punteggio | Criterio |
|---:|---|
| 2 | Non inventa valori, connessioni o funzioni non presenti |
| 1 | Fa qualche ipotesi, ma la segnala come ipotesi |
| 0 | Inventa informazioni o dà per certe cose non presenti |

### Interpretazione del totale

| Totale /10 | Giudizio |
|---:|---|
| 8-10 | Topologia chiara |
| 5-7 | Topologia parzialmente chiara |
| 0-4 | Topologia insufficiente |


### Note
Alla luce dei risultati preliminari, i modelli GPT-5.3 Instant e GPT-5.2 Instant risultano i candidati principali per l’analisi topologica automatica da JSON, poiché ottengono il punteggio medio più alto e mantengono un buon equilibrio tra correttezza, prudenza interpretativa e costo computazionale.
