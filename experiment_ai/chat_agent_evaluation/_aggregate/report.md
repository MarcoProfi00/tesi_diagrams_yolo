# Risultati aggregati CHAT e AGENT

Report generato automaticamente dai judge ufficiali. Le cartelle di retry non vengono lette.

- Circuiti ufficiali: **17**
- Valutazioni ufficiali: **34**
- Circuiti: `a01, a02, a04, a05, a06, a07, a08, a09, a10, b02, b03, b04, b05, b06, b10, c02, c03`

## Risultati complessivi

| Modalità | N | Media | Mediana | Dev. std. | Successi | Parziali | Fallimenti | Scenari eseguiti medi |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CHAT | 17 | 87.94 | 90 | 13.70 | 11 | 6 | 0 | 2.00 |
| AGENT | 17 | 77.65 | 80 | 18.88 | 11 | 5 | 1 | 1.76 |

- Differenza media AGENT − CHAT: **-10.29** punti.
- Vittorie AGENT / pareggi / vittorie CHAT: **3 / 3 / 11**.

| Criterio | Significato | CHAT (0–4) | AGENT (0–4) |
|---|---|---:|---:|
| task_achievement | Quanto è stato raggiunto l'obiettivo richiesto dall'utente. | 3.47 | 3.29 |
| technical_correctness | Correttezza elettrica e diagnostica della risposta. | 3.53 | 2.88 |
| scenario_quality | Pertinenza e utilità degli scenari di verifica scelti. | 3.29 | 3.24 |
| evidence_interpretation | Coerenza delle conclusioni con le misure SPICE ottenute. | 3.65 | 3.18 |
| conclusion_quality | Chiarezza, completezza e solidità della conclusione finale. | 3.65 | 2.94 |

## Confronto per circuito

| Circuito | CHAT | AGENT | Δ AGENT−CHAT | Vincitore | Esito CHAT | Esito AGENT |
|---|---:|---:|---:|---|---|---|
| a01 | 100 | 100 | +0 | tie | success | success |
| a02 | 90 | 100 | +10 | agent | partial_success | success |
| a04 | 100 | 90 | -10 | chat | success | success |
| a05 | 100 | 100 | +0 | tie | success | success |
| a06 | 50 | 60 | +10 | agent | partial_success | partial_success |
| a07 | 100 | 95 | -5 | chat | success | success |
| a08 | 100 | 75 | -25 | chat | success | partial_success |
| a09 | 85 | 90 | +5 | agent | success | success |
| a10 | 90 | 85 | -5 | chat | success | success |
| b02 | 95 | 60 | -35 | chat | success | partial_success |
| b03 | 95 | 80 | -15 | chat | success | success |
| b04 | 85 | 35 | -50 | chat | partial_success | failure |
| b05 | 80 | 60 | -20 | chat | partial_success | partial_success |
| b06 | 95 | 80 | -15 | chat | success | success |
| b10 | 85 | 80 | -5 | chat | success | success |
| c02 | 65 | 50 | -15 | chat | partial_success | partial_success |
| c03 | 80 | 80 | +0 | tie | partial_success | success |

## File prodotti

- `runs.csv`: una riga per valutazione, con dati numerici e motivazioni.
- `pairs.csv`: confronto appaiato CHAT–AGENT per circuito.
- `criteria_long.csv`: formato lungo per grafici dei criteri.
- `mode_summary.csv`: statistiche descrittive per modalità.
- `paired_summary.csv`: differenze e vittorie appaiate.
- `criteria_summary.csv`: medie dei cinque criteri.
- `outcome_counts.csv`: distribuzione degli esiti.
- `critical_error_counts.csv`: frequenza degli errori critici.
- `aggregate_results.json`: copia strutturata di tutte le aggregazioni.
