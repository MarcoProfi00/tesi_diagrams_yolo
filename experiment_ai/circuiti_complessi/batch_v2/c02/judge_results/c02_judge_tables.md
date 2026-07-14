# Tabelle judge — c02

File sorgente:

`c02__judge_summary_gpt-5.5_20260605_145505.json`

## Sintesi rapida

- Esecuzioni valutate: **16**
- Score medio `JSON + datasheet`: **17.12 / 21**
- Score medio `JSON + immagine + datasheet`: **14.38 / 21**
- Delta medio dovuto all'immagine: **-2.75 punti**
- Miglior run: **`gpt-5.4`**, input **JSON + datasheet**, score **21 / 21**
- Peggior run: **`gpt-4.1-nano`**, input **JSON + immagine + datasheet**, score **9 / 21**
- Costo judge stimato totale: **$1.34**

---

## 1. Risultati dettagliati per run

| Circuito | Modello | Input | Score / 21 | Score norm. | Verdict | Top-1 | Top-3 | Errori gravi | Allucinazioni | Latenza modello (s) | Input tokens | Output tokens | Costo modello ($) |
| --- | --- | --- | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| c02 | `gpt-4o-mini` | JSON + datasheet | 13 | 0.619 | Parziale | Sì | Sì | 3 | 2 | 17.28 | 5174 | 1017 | 0.00139 |
| c02 | `gpt-4o-mini` | JSON + immagine + datasheet | 13 | 0.619 | Parziale | Sì | Sì | 2 | 2 | 21.30 | 30757 | 948 | 0.00518 |
| c02 | `gpt-4.1-mini` | JSON + datasheet | 19 | 0.905 | Sì | Sì | Sì | 0 | 3 | 40.28 | 5174 | 1779 | 0.00492 |
| c02 | `gpt-4.1-mini` | JSON + immagine + datasheet | 14 | 0.667 | Parziale | Sì | Sì | 3 | 3 | 19.57 | 6916 | 1667 | 0.00543 |
| c02 | `gpt-4.1-nano` | JSON + datasheet | 11 | 0.524 | Parziale | No | Sì | 3 | 2 | 13.60 | 5174 | 1352 | 0.00106 |
| c02 | `gpt-4.1-nano` | JSON + immagine + datasheet | 9 | 0.429 | Parziale | No | Sì | 4 | 4 | 11.59 | 7777 | 1555 | 0.00140 |
| c02 | `gpt-5-nano` | JSON + datasheet | 16 | 0.762 | Parziale | No | Sì | 2 | 3 | 25.45 | 5173 | 3238 | 0.00155 |
| c02 | `gpt-5-nano` | JSON + immagine + datasheet | 13 | 0.619 | Parziale | Sì | Sì | 3 | 3 | 21.40 | 6791 | 3082 | 0.00157 |
| c02 | `gpt-5-mini` | JSON + datasheet | 19 | 0.905 | Sì | Sì | Sì | 0 | 2 | 41.05 | 5173 | 2914 | 0.00712 |
| c02 | `gpt-5-mini` | JSON + immagine + datasheet | 15 | 0.714 | Sì | Sì | Sì | 2 | 2 | 35.90 | 6484 | 2896 | 0.00741 |
| c02 | `gpt-5.4-nano` | JSON + datasheet | 19 | 0.905 | Sì | Sì | Sì | 0 | 2 | 24.31 | 5173 | 3342 | 0.00521 |
| c02 | `gpt-5.4-nano` | JSON + immagine + datasheet | 14 | 0.667 | Parziale | Sì | Sì | 3 | 3 | 20.74 | 6484 | 2741 | 0.00472 |
| c02 | `gpt-5.4-mini` | JSON + datasheet | 19 | 0.905 | Sì | Sì | Sì | 1 | 0 | 12.45 | 5173 | 1789 | 0.01193 |
| c02 | `gpt-5.4-mini` | JSON + immagine + datasheet | 17 | 0.810 | Sì | Sì | Sì | 2 | 2 | 25.06 | 6484 | 3354 | 0.01996 |
| c02 | `gpt-5.4` | JSON + datasheet | 21 | 1.000 | Sì | Sì | Sì | 0 | 0 | 38.84 | 5173 | 2534 | 0.05094 |
| c02 | `gpt-5.4` | JSON + immagine + datasheet | 20 | 0.952 | Sì | Sì | Sì | 0 | 2 | 65.81 | 6484 | 3780 | 0.07291 |

---

## 2. Confronto JSON-only vs JSON + immagine

| Modello | JSON + datasheet | JSON + immagine + datasheet | Delta immagine | Top-1 JSON | Top-1 JSON+img | Errori JSON | Errori JSON+img |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: |
| `gpt-4o-mini` | 13 | 13 | +0 | Sì | Sì | 3 | 2 |
| `gpt-4.1-mini` | 19 | 14 | -5 | Sì | Sì | 0 | 3 |
| `gpt-4.1-nano` | 11 | 9 | -2 | No | No | 3 | 4 |
| `gpt-5-nano` | 16 | 13 | -3 | No | Sì | 2 | 3 |
| `gpt-5-mini` | 19 | 15 | -4 | Sì | Sì | 0 | 2 |
| `gpt-5.4-nano` | 19 | 14 | -5 | Sì | Sì | 0 | 3 |
| `gpt-5.4-mini` | 19 | 17 | -2 | Sì | Sì | 1 | 2 |
| `gpt-5.4` | 21 | 20 | -1 | Sì | Sì | 0 | 0 |

---

## 3. Aggregazione per input type

| Input type | N | Score medio | Mediana | Std | Top-1 accuracy | Top-3 accuracy | Errori gravi medi | Allucinazioni medie | Latenza media modello (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| JSON + datasheet | 8 | 17.12 | 19.00 | 3.26 | 75.0% | 100.0% | 1.12 | 1.75 | 26.66 |
| JSON + immagine + datasheet | 8 | 14.38 | 14.00 | 3.00 | 87.5% | 100.0% | 2.38 | 2.62 | 27.67 |

---

## 4. Aggregazione per modello

| Modello | N | Score medio | Mediana | Std | Top-1 accuracy | Top-3 accuracy | Errori gravi medi | Allucinazioni medie | Costo medio modello ($) | Latenza media modello (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 2 | 13.00 | 13.00 | 0.00 | 100.0% | 100.0% | 2.50 | 2.00 | 0.00328 | 19.29 |
| `gpt-4.1-mini` | 2 | 16.50 | 16.50 | 2.50 | 100.0% | 100.0% | 1.50 | 3.00 | 0.00517 | 29.93 |
| `gpt-4.1-nano` | 2 | 10.00 | 10.00 | 1.00 | 0.0% | 100.0% | 3.50 | 3.00 | 0.00123 | 12.60 |
| `gpt-5-nano` | 2 | 14.50 | 14.50 | 1.50 | 50.0% | 100.0% | 2.50 | 3.00 | 0.00156 | 23.42 |
| `gpt-5-mini` | 2 | 17.00 | 17.00 | 2.00 | 100.0% | 100.0% | 1.00 | 2.00 | 0.00727 | 38.48 |
| `gpt-5.4-nano` | 2 | 16.50 | 16.50 | 2.50 | 100.0% | 100.0% | 1.50 | 2.50 | 0.00497 | 22.53 |
| `gpt-5.4-mini` | 2 | 18.00 | 18.00 | 1.00 | 100.0% | 100.0% | 1.50 | 1.00 | 0.01594 | 18.76 |
| `gpt-5.4` | 2 | 20.50 | 20.50 | 0.50 | 100.0% | 100.0% | 0.00 | 1.00 | 0.06193 | 52.32 |

---

## 5. Score medi per criterio e modello

| Modello | Comprensione circuito | Uso datasheet | Uso JSON/immagine | Accuratezza diagnostica | Priorità cause | Controlli pratici | Assenza allucinazioni |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 2.00 | 2.00 | 1.00 | 2.00 | 2.00 | 2.00 | 2.00 |
| `gpt-4.1-mini` | 2.00 | 3.00 | 2.00 | 2.50 | 2.50 | 3.00 | 1.50 |
| `gpt-4.1-nano` | 1.50 | 2.00 | 1.00 | 1.00 | 1.00 | 2.00 | 1.50 |
| `gpt-5-nano` | 2.00 | 2.50 | 1.50 | 2.00 | 2.00 | 3.00 | 1.50 |
| `gpt-5-mini` | 2.00 | 3.00 | 2.00 | 2.50 | 3.00 | 3.00 | 1.50 |
| `gpt-5.4-nano` | 2.00 | 3.00 | 2.00 | 2.50 | 2.50 | 3.00 | 1.50 |
| `gpt-5.4-mini` | 2.50 | 3.00 | 2.00 | 2.50 | 3.00 | 3.00 | 2.00 |
| `gpt-5.4` | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 2.50 |

---

## 6. Token, costo e latenza del judge

| Modello | Input | Judge input tokens | Judge output tokens | Judge total tokens | Costo judge stimato ($) | Latenza judge (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | JSON + datasheet | 8012 | 1379 | 9391 | 0.0814 | 32.66 |
| `gpt-4o-mini` | JSON + immagine + datasheet | 7946 | 1346 | 9292 | 0.0801 | 31.05 |
| `gpt-4.1-mini` | JSON + datasheet | 8774 | 1307 | 10081 | 0.0831 | 31.36 |
| `gpt-4.1-mini` | JSON + immagine + datasheet | 8665 | 1608 | 10273 | 0.0916 | 34.53 |
| `gpt-4.1-nano` | JSON + datasheet | 8347 | 1283 | 9630 | 0.0802 | 28.18 |
| `gpt-4.1-nano` | JSON + immagine + datasheet | 8553 | 1447 | 10000 | 0.0862 | 31.19 |
| `gpt-5-nano` | JSON + datasheet | 9200 | 1398 | 10598 | 0.0879 | 31.77 |
| `gpt-5-nano` | JSON + immagine + datasheet | 9309 | 1460 | 10769 | 0.0903 | 30.66 |
| `gpt-5-mini` | JSON + datasheet | 9040 | 1127 | 10167 | 0.0790 | 22.37 |
| `gpt-5-mini` | JSON + immagine + datasheet | 9159 | 1330 | 10489 | 0.0857 | 30.69 |
| `gpt-5.4-nano` | JSON + datasheet | 9105 | 1385 | 10490 | 0.0871 | 31.12 |
| `gpt-5.4-nano` | JSON + immagine + datasheet | 9240 | 1475 | 10715 | 0.0905 | 32.99 |
| `gpt-5.4-mini` | JSON + datasheet | 8395 | 1153 | 9548 | 0.0766 | 24.37 |
| `gpt-5.4-mini` | JSON + immagine + datasheet | 8570 | 1381 | 9951 | 0.0843 | 29.69 |
| `gpt-5.4` | JSON + datasheet | 9008 | 874 | 9882 | 0.0713 | 18.69 |
| `gpt-5.4` | JSON + immagine + datasheet | 9585 | 1159 | 10744 | 0.0827 | 23.42 |

---

## Nota sui costi

Il costo del modello rappresenta il costo operativo della diagnosi automatica, cioè quanto costerebbe eseguire il sistema di troubleshooting sul circuito.

Il costo del judge è riportato separatamente perché riguarda solo la fase di valutazione automatica offline e non farebbe parte del costo operativo del sistema finale.
