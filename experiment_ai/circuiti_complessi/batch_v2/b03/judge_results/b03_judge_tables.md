# Tabelle judge — b03

File sorgente:

`b03__judge_summary_gpt-5.5_20260605_114136.json`

## Sintesi rapida

- Esecuzioni valutate: **16**
- Score medio `JSON + datasheet`: **14.88 / 21**
- Score medio `JSON + immagine + datasheet`: **15.00 / 21**
- Delta medio dovuto all'immagine: **+0.12 punti**
- Miglior run: **`gpt-5.4-mini`**, input **JSON + immagine + datasheet**, score **21 / 21**
- Peggior run: **`gpt-4o-mini`**, input **JSON + datasheet**, score **10 / 21**
- Costo judge stimato totale: **$1.33**

---

## 1. Risultati dettagliati per run

| Circuito | Modello | Input | Score / 21 | Score norm. | Verdict | Top-1 | Top-3 | Errori gravi | Allucinazioni | Latenza modello (s) | Input tokens | Output tokens | Costo modello ($) |
| --- | --- | --- | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| b03 | `gpt-4o-mini` | JSON + datasheet | 10 | 0.476 | Parziale | No | No | 4 | 3 | 14.09 | 4783 | 921 | 0.00127 |
| b03 | `gpt-4o-mini` | JSON + immagine + datasheet | 10 | 0.476 | No | No | No | 4 | 3 | 15.73 | 30366 | 848 | 0.00506 |
| b03 | `gpt-4.1-mini` | JSON + datasheet | 12 | 0.571 | Parziale | No | No | 3 | 2 | 25.52 | 4783 | 1688 | 0.00461 |
| b03 | `gpt-4.1-mini` | JSON + immagine + datasheet | 18 | 0.857 | Sì | Sì | Sì | 2 | 2 | 17.71 | 6525 | 1436 | 0.00491 |
| b03 | `gpt-4.1-nano` | JSON + datasheet | 14 | 0.667 | Parziale | Sì | Sì | 3 | 2 | 15.19 | 4783 | 1444 | 0.00106 |
| b03 | `gpt-4.1-nano` | JSON + immagine + datasheet | 11 | 0.524 | Parziale | No | No | 3 | 4 | 13.65 | 7386 | 1363 | 0.00128 |
| b03 | `gpt-5-nano` | JSON + datasheet | 16 | 0.762 | Parziale | Sì | Sì | 3 | 3 | 25.84 | 4782 | 3041 | 0.00146 |
| b03 | `gpt-5-nano` | JSON + immagine + datasheet | 12 | 0.571 | Parziale | No | Sì | 3 | 3 | 23.88 | 6400 | 3535 | 0.00173 |
| b03 | `gpt-5-mini` | JSON + datasheet | 20 | 0.952 | Sì | Sì | Sì | 0 | 2 | 37.42 | 4782 | 3082 | 0.00736 |
| b03 | `gpt-5-mini` | JSON + immagine + datasheet | 17 | 0.810 | Parziale | No | Sì | 2 | 2 | 25.18 | 6093 | 2300 | 0.00612 |
| b03 | `gpt-5.4-nano` | JSON + datasheet | 13 | 0.619 | Parziale | No | Sì | 3 | 2 | 20.43 | 4782 | 3104 | 0.00484 |
| b03 | `gpt-5.4-nano` | JSON + immagine + datasheet | 12 | 0.571 | Parziale | No | No | 3 | 3 | 16.31 | 6093 | 2282 | 0.00407 |
| b03 | `gpt-5.4-mini` | JSON + datasheet | 17 | 0.810 | Sì | Sì | Sì | 2 | 2 | 16.89 | 4782 | 1964 | 0.01242 |
| b03 | `gpt-5.4-mini` | JSON + immagine + datasheet | 21 | 1.000 | Sì | Sì | Sì | 0 | 0 | 16.80 | 6093 | 2413 | 0.01543 |
| b03 | `gpt-5.4` | JSON + datasheet | 17 | 0.810 | Sì | Sì | Sì | 2 | 2 | 55.68 | 4782 | 3982 | 0.07168 |
| b03 | `gpt-5.4` | JSON + immagine + datasheet | 19 | 0.905 | Sì | Sì | Sì | 2 | 2 | 52.48 | 6093 | 3234 | 0.06374 |

---

## 2. Confronto JSON-only vs JSON + immagine

| Modello | JSON + datasheet | JSON + immagine + datasheet | Delta immagine | Top-1 JSON | Top-1 JSON+img | Errori JSON | Errori JSON+img |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: |
| `gpt-4o-mini` | 10 | 10 | +0 | No | No | 4 | 4 |
| `gpt-4.1-mini` | 12 | 18 | +6 | No | Sì | 3 | 2 |
| `gpt-4.1-nano` | 14 | 11 | -3 | Sì | No | 3 | 3 |
| `gpt-5-nano` | 16 | 12 | -4 | Sì | No | 3 | 3 |
| `gpt-5-mini` | 20 | 17 | -3 | Sì | No | 0 | 2 |
| `gpt-5.4-nano` | 13 | 12 | -1 | No | No | 3 | 3 |
| `gpt-5.4-mini` | 17 | 21 | +4 | Sì | Sì | 2 | 0 |
| `gpt-5.4` | 17 | 19 | +2 | Sì | Sì | 2 | 2 |

---

## 3. Aggregazione per input type

| Input type | N | Score medio | Mediana | Std | Top-1 accuracy | Top-3 accuracy | Errori gravi medi | Allucinazioni medie | Latenza media modello (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| JSON + datasheet | 8 | 14.88 | 15.00 | 3.02 | 62.5% | 75.0% | 2.50 | 2.25 | 26.38 |
| JSON + immagine + datasheet | 8 | 15.00 | 14.50 | 3.94 | 37.5% | 62.5% | 2.38 | 2.38 | 22.72 |

---

## 4. Aggregazione per modello

| Modello | N | Score medio | Mediana | Std | Top-1 accuracy | Top-3 accuracy | Errori gravi medi | Allucinazioni medie | Costo medio modello ($) | Latenza media modello (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 2 | 10.00 | 10.00 | 0.00 | 0.0% | 0.0% | 4.00 | 3.00 | 0.00317 | 14.91 |
| `gpt-4.1-mini` | 2 | 15.00 | 15.00 | 3.00 | 50.0% | 50.0% | 2.50 | 2.00 | 0.00476 | 21.62 |
| `gpt-4.1-nano` | 2 | 12.50 | 12.50 | 1.50 | 50.0% | 50.0% | 3.00 | 3.00 | 0.00117 | 14.42 |
| `gpt-5-nano` | 2 | 14.00 | 14.00 | 2.00 | 50.0% | 100.0% | 3.00 | 3.00 | 0.00159 | 24.86 |
| `gpt-5-mini` | 2 | 18.50 | 18.50 | 1.50 | 50.0% | 100.0% | 1.00 | 2.00 | 0.00674 | 31.30 |
| `gpt-5.4-nano` | 2 | 12.50 | 12.50 | 0.50 | 0.0% | 50.0% | 3.00 | 2.50 | 0.00445 | 18.37 |
| `gpt-5.4-mini` | 2 | 19.00 | 19.00 | 2.00 | 100.0% | 100.0% | 1.00 | 1.00 | 0.01393 | 16.84 |
| `gpt-5.4` | 2 | 18.00 | 18.00 | 1.00 | 100.0% | 100.0% | 2.00 | 2.00 | 0.06771 | 54.08 |

---

## 5. Score medi per criterio e modello

| Modello | Comprensione circuito | Uso datasheet | Uso JSON/immagine | Accuratezza diagnostica | Priorità cause | Controlli pratici | Assenza allucinazioni |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 2.00 | 2.50 | 1.00 | 1.00 | 0.50 | 2.00 | 1.00 |
| `gpt-4.1-mini` | 2.00 | 2.50 | 2.50 | 1.50 | 2.00 | 2.50 | 2.00 |
| `gpt-4.1-nano` | 2.00 | 3.00 | 1.00 | 1.50 | 1.50 | 2.00 | 1.50 |
| `gpt-5-nano` | 2.00 | 2.50 | 1.50 | 2.00 | 1.50 | 3.00 | 1.50 |
| `gpt-5-mini` | 3.00 | 3.00 | 3.00 | 2.50 | 2.00 | 3.00 | 2.00 |
| `gpt-5.4-nano` | 2.00 | 2.50 | 2.00 | 1.00 | 1.00 | 2.50 | 1.50 |
| `gpt-5.4-mini` | 2.50 | 3.00 | 3.00 | 2.50 | 2.50 | 3.00 | 2.50 |
| `gpt-5.4` | 2.50 | 3.00 | 3.00 | 2.00 | 2.50 | 3.00 | 2.00 |

---

## 6. Token, costo e latenza del judge

| Modello | Input | Judge input tokens | Judge output tokens | Judge total tokens | Costo judge stimato ($) | Latenza judge (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | JSON + datasheet | 7527 | 1484 | 9011 | 0.0822 | 37.09 |
| `gpt-4o-mini` | JSON + immagine + datasheet | 7457 | 1313 | 8770 | 0.0767 | 30.38 |
| `gpt-4.1-mini` | JSON + datasheet | 8293 | 1340 | 9633 | 0.0817 | 31.82 |
| `gpt-4.1-mini` | JSON + immagine + datasheet | 8046 | 1218 | 9264 | 0.0768 | 26.44 |
| `gpt-4.1-nano` | JSON + datasheet | 8049 | 1334 | 9383 | 0.0803 | 30.33 |
| `gpt-4.1-nano` | JSON + immagine + datasheet | 7972 | 1471 | 9443 | 0.0840 | 33.39 |
| `gpt-5-nano` | JSON + datasheet | 9032 | 1503 | 10535 | 0.0902 | 40.54 |
| `gpt-5-nano` | JSON + immagine + datasheet | 9749 | 1365 | 11114 | 0.0897 | 29.97 |
| `gpt-5-mini` | JSON + datasheet | 8975 | 1243 | 10218 | 0.0822 | 26.46 |
| `gpt-5-mini` | JSON + immagine + datasheet | 8606 | 1324 | 9930 | 0.0828 | 29.92 |
| `gpt-5.4-nano` | JSON + datasheet | 9336 | 1320 | 10656 | 0.0863 | 28.87 |
| `gpt-5.4-nano` | JSON + immagine + datasheet | 8627 | 1406 | 10033 | 0.0853 | 32.99 |
| `gpt-5.4-mini` | JSON + datasheet | 8212 | 1367 | 9579 | 0.0821 | 29.91 |
| `gpt-5.4-mini` | JSON + immagine + datasheet | 7992 | 1045 | 9037 | 0.0713 | 23.29 |
| `gpt-5.4` | JSON + datasheet | 9367 | 1427 | 10794 | 0.0896 | 33.58 |
| `gpt-5.4` | JSON + immagine + datasheet | 9669 | 1300 | 10969 | 0.0873 | 26.11 |

---

## Nota sui costi

Il costo del modello rappresenta il costo operativo della diagnosi automatica, cioè quanto costerebbe eseguire il sistema di troubleshooting sul circuito.

Il costo del judge è riportato separatamente perché riguarda solo la fase di valutazione automatica offline e non farebbe parte del costo operativo del sistema finale.
