# Tabelle judge — ic2

File sorgente:

`ic2__judge_summary_gpt-5.5_20260518_161705.json`

## Sintesi rapida

- Esecuzioni valutate: **16**
- Score medio `JSON + datasheet`: **14.25 / 21**
- Score medio `JSON + immagine + datasheet`: **15.62 / 21**
- Delta medio dovuto all'immagine: **+1.38 punti**
- Miglior run: **`gpt-5.4`**, input **JSON + immagine + datasheet**, score **21 / 21**
- Peggior run: **`gpt-4o-mini`**, input **JSON + datasheet**, score **8 / 21**
- Costo judge stimato totale: **$2.55**

---

## 1. Risultati dettagliati per run

| Circuito | Modello | Input | Score / 21 | Score norm. | Verdict | Top-1 | Top-3 | Errori gravi | Allucinazioni | Latenza modello (s) | Input tokens | Output tokens | Costo modello ($) |
| --- | --- | --- | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ic2 | `gpt-4o-mini` | JSON + datasheet | 8 | 0.381 | Parziale | No | No | 4 | 2 | 52.25 | 20118 | 981 | 0.00361 |
| ic2 | `gpt-4o-mini` | JSON + immagine + datasheet | 10 | 0.476 | Parziale | Sì | Sì | 4 | 3 | 39.24 | 45701 | 1079 | 0.00750 |
| ic2 | `gpt-4.1-mini` | JSON + datasheet | 16 | 0.762 | Parziale | No | Sì | 2 | 2 | 37.01 | 20118 | 2498 | 0.01204 |
| ic2 | `gpt-4.1-mini` | JSON + immagine + datasheet | 15 | 0.714 | Parziale | No | No | 3 | 3 | 29.85 | 21860 | 1561 | 0.01124 |
| ic2 | `gpt-4.1-nano` | JSON + datasheet | 8 | 0.381 | Parziale | No | Sì | 4 | 3 | 17.77 | 20118 | 1709 | 0.00270 |
| ic2 | `gpt-4.1-nano` | JSON + immagine + datasheet | 11 | 0.524 | Parziale | No | Sì | 3 | 4 | 26.75 | 22721 | 1617 | 0.00292 |
| ic2 | `gpt-5-nano` | JSON + datasheet | 9 | 0.429 | Parziale | Sì | Sì | 4 | 3 | 26.51 | 20117 | 3470 | 0.00239 |
| ic2 | `gpt-5-nano` | JSON + immagine + datasheet | 13 | 0.619 | Parziale | Sì | Sì | 4 | 3 | 33.92 | 21735 | 3471 | 0.00248 |
| ic2 | `gpt-5-mini` | JSON + datasheet | 16 | 0.762 | Parziale | No | No | 2 | 1 | 39.38 | 20117 | 3298 | 0.01163 |
| ic2 | `gpt-5-mini` | JSON + immagine + datasheet | 20 | 0.952 | Sì | Sì | Sì | 0 | 1 | 50.26 | 21428 | 3252 | 0.01186 |
| ic2 | `gpt-5.4-nano` | JSON + datasheet | 17 | 0.810 | Sì | Sì | Sì | 2 | 1 | 19.66 | 20117 | 2712 | 0.00741 |
| ic2 | `gpt-5.4-nano` | JSON + immagine + datasheet | 15 | 0.714 | Parziale | No | No | 2 | 1 | 21.16 | 21428 | 2720 | 0.00769 |
| ic2 | `gpt-5.4-mini` | JSON + datasheet | 20 | 0.952 | Sì | Sì | Sì | 0 | 0 | 15.73 | 20117 | 1980 | 0.02400 |
| ic2 | `gpt-5.4-mini` | JSON + immagine + datasheet | 20 | 0.952 | Sì | Sì | Sì | 0 | 0 | 14.39 | 21428 | 1702 | 0.02373 |
| ic2 | `gpt-5.4` | JSON + datasheet | 20 | 0.952 | Sì | Sì | Sì | 0 | 0 | 49.74 | 20117 | 3102 | 0.09682 |
| ic2 | `gpt-5.4` | JSON + immagine + datasheet | 21 | 1.000 | Sì | Sì | Sì | 0 | 0 | 49.12 | 21428 | 3103 | 0.10011 |

---

## 2. Confronto JSON-only vs JSON + immagine

| Modello | JSON + datasheet | JSON + immagine + datasheet | Delta immagine | Top-1 JSON | Top-1 JSON+img | Errori JSON | Errori JSON+img |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: |
| `gpt-4o-mini` | 8 | 10 | +2 | No | Sì | 4 | 4 |
| `gpt-4.1-mini` | 16 | 15 | -1 | No | No | 2 | 3 |
| `gpt-4.1-nano` | 8 | 11 | +3 | No | No | 4 | 3 |
| `gpt-5-nano` | 9 | 13 | +4 | Sì | Sì | 4 | 4 |
| `gpt-5-mini` | 16 | 20 | +4 | No | Sì | 2 | 0 |
| `gpt-5.4-nano` | 17 | 15 | -2 | Sì | No | 2 | 2 |
| `gpt-5.4-mini` | 20 | 20 | +0 | Sì | Sì | 0 | 0 |
| `gpt-5.4` | 20 | 21 | +1 | Sì | Sì | 0 | 0 |

---

## 3. Aggregazione per input type

| Input type | N | Score medio | Mediana | Std | Top-1 accuracy | Top-3 accuracy | Errori gravi medi | Allucinazioni medie | Latenza media modello (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| JSON + datasheet | 8 | 14.25 | 16.00 | 4.82 | 50.0% | 75.0% | 2.25 | 1.50 | 32.26 |
| JSON + immagine + datasheet | 8 | 15.62 | 15.00 | 4.00 | 62.5% | 75.0% | 2.00 | 1.88 | 33.09 |

---

## 4. Aggregazione per modello

| Modello | N | Score medio | Mediana | Std | Top-1 accuracy | Top-3 accuracy | Errori gravi medi | Allucinazioni medie | Costo medio modello ($) | Latenza media modello (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 2 | 9.00 | 9.00 | 1.00 | 50.0% | 50.0% | 4.00 | 2.50 | 0.00555 | 45.74 |
| `gpt-4.1-mini` | 2 | 15.50 | 15.50 | 0.50 | 0.0% | 50.0% | 2.50 | 2.50 | 0.01164 | 33.43 |
| `gpt-4.1-nano` | 2 | 9.50 | 9.50 | 1.50 | 0.0% | 100.0% | 3.50 | 3.50 | 0.00281 | 22.26 |
| `gpt-5-nano` | 2 | 11.00 | 11.00 | 2.00 | 100.0% | 100.0% | 4.00 | 3.00 | 0.00243 | 30.21 |
| `gpt-5-mini` | 2 | 18.00 | 18.00 | 2.00 | 50.0% | 50.0% | 1.00 | 1.00 | 0.01174 | 44.82 |
| `gpt-5.4-nano` | 2 | 16.00 | 16.00 | 1.00 | 50.0% | 50.0% | 2.00 | 1.00 | 0.00755 | 20.41 |
| `gpt-5.4-mini` | 2 | 20.00 | 20.00 | 0.00 | 100.0% | 100.0% | 0.00 | 0.00 | 0.02386 | 15.06 |
| `gpt-5.4` | 2 | 20.50 | 20.50 | 0.50 | 100.0% | 100.0% | 0.00 | 0.00 | 0.09847 | 49.43 |

---

## 5. Score medi per criterio e modello

| Modello | Comprensione circuito | Uso datasheet | Uso JSON/immagine | Accuratezza diagnostica | Priorità cause | Controlli pratici | Assenza allucinazioni |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 2.00 | 1.00 | 1.00 | 1.50 | 0.50 | 2.00 | 1.00 |
| `gpt-4.1-mini` | 3.00 | 2.00 | 2.50 | 2.00 | 1.00 | 3.00 | 2.00 |
| `gpt-4.1-nano` | 2.00 | 1.50 | 1.00 | 1.50 | 0.50 | 2.00 | 1.00 |
| `gpt-5-nano` | 1.50 | 1.00 | 1.50 | 2.00 | 1.50 | 2.50 | 1.00 |
| `gpt-5-mini` | 3.00 | 2.50 | 3.00 | 2.50 | 2.00 | 3.00 | 2.00 |
| `gpt-5.4-nano` | 3.00 | 2.00 | 2.50 | 2.00 | 1.50 | 3.00 | 2.00 |
| `gpt-5.4-mini` | 3.00 | 2.00 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 |
| `gpt-5.4` | 3.00 | 2.50 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 |

---

## 6. Token, costo e latenza del judge

| Modello | Input | Judge input tokens | Judge output tokens | Judge total tokens | Costo judge stimato ($) | Latenza judge (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | JSON + datasheet | 22920 | 1360 | 24280 | 0.1554 | 27.68 |
| `gpt-4o-mini` | JSON + immagine + datasheet | 23021 | 1542 | 24563 | 0.1614 | 31.83 |
| `gpt-4.1-mini` | JSON + datasheet | 24436 | 1325 | 25761 | 0.1619 | 27.46 |
| `gpt-4.1-mini` | JSON + immagine + datasheet | 23503 | 1661 | 25164 | 0.1673 | 32.39 |
| `gpt-4.1-nano` | JSON + datasheet | 23648 | 1511 | 25159 | 0.1636 | 29.73 |
| `gpt-4.1-nano` | JSON + immagine + datasheet | 23559 | 1396 | 24955 | 0.1597 | 28.73 |
| `gpt-5-nano` | JSON + datasheet | 24630 | 1768 | 26398 | 0.1762 | 33.17 |
| `gpt-5-nano` | JSON + immagine + datasheet | 24758 | 1528 | 26286 | 0.1696 | 28.71 |
| `gpt-5-mini` | JSON + datasheet | 24220 | 1391 | 25611 | 0.1628 | 25.18 |
| `gpt-5-mini` | JSON + immagine + datasheet | 24269 | 1062 | 25331 | 0.1532 | 23.37 |
| `gpt-5.4-nano` | JSON + datasheet | 24137 | 1363 | 25500 | 0.1616 | 26.72 |
| `gpt-5.4-nano` | JSON + immagine + datasheet | 23986 | 1285 | 25271 | 0.1585 | 24.64 |
| `gpt-5.4-mini` | JSON + datasheet | 23398 | 1042 | 24440 | 0.1482 | 17.46 |
| `gpt-5.4-mini` | JSON + immagine + datasheet | 23123 | 1209 | 24332 | 0.1519 | 23.65 |
| `gpt-5.4` | JSON + datasheet | 24520 | 1025 | 25545 | 0.1534 | 18.80 |
| `gpt-5.4` | JSON + immagine + datasheet | 24365 | 862 | 25227 | 0.1477 | 16.39 |

---

## Nota sui costi

Il costo del modello rappresenta il costo operativo della diagnosi automatica, cioè quanto costerebbe eseguire il sistema di troubleshooting sul circuito.

Il costo del judge è riportato separatamente perché riguarda solo la fase di valutazione automatica offline e non farebbe parte del costo operativo del sistema finale.
