# Tabelle judge — c05

File sorgente:

`c05__judge_summary_gpt-5.5_20260605_153431.json`

## Sintesi rapida

- Esecuzioni valutate: **16**
- Score medio `JSON + datasheet`: **14.38 / 21**
- Score medio `JSON + immagine + datasheet`: **15.62 / 21**
- Delta medio dovuto all'immagine: **+1.25 punti**
- Miglior run: **`gpt-5.4-mini`**, input **JSON + immagine + datasheet**, score **21 / 21**
- Peggior run: **`gpt-4.1-nano`**, input **JSON + datasheet**, score **9 / 21**
- Costo judge stimato totale: **$1.84**

---

## 1. Risultati dettagliati per run

| Circuito | Modello | Input | Score / 21 | Score norm. | Verdict | Top-1 | Top-3 | Errori gravi | Allucinazioni | Latenza modello (s) | Input tokens | Output tokens | Costo modello ($) |
| --- | --- | --- | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| c05 | `gpt-4o-mini` | JSON + datasheet | 12 | 0.571 | Parziale | Sì | Sì | 3 | 2 | 17.45 | 11095 | 1045 | 0.00229 |
| c05 | `gpt-4o-mini` | JSON + immagine + datasheet | 11 | 0.524 | Parziale | Sì | Sì | 4 | 2 | 36.59 | 36678 | 1056 | 0.00614 |
| c05 | `gpt-4.1-mini` | JSON + datasheet | 17 | 0.809 | Sì | Sì | Sì | 2 | 2 | 30.85 | 11095 | 2481 | 0.00841 |
| c05 | `gpt-4.1-mini` | JSON + immagine + datasheet | 19 | 0.905 | Sì | Sì | Sì | 0 | 2 | 23.07 | 12837 | 1940 | 0.00824 |
| c05 | `gpt-4.1-nano` | JSON + datasheet | 9 | 0.429 | Parziale | No | Sì | 4 | 3 | 19.09 | 11095 | 1682 | 0.00178 |
| c05 | `gpt-4.1-nano` | JSON + immagine + datasheet | 14 | 0.667 | Parziale | Sì | Sì | 3 | 3 | 12.85 | 13698 | 1554 | 0.00199 |
| c05 | `gpt-5-nano` | JSON + datasheet | 11 | 0.524 | Parziale | No | Sì | 3 | 3 | 32.42 | 11094 | 3059 | 0.00178 |
| c05 | `gpt-5-nano` | JSON + immagine + datasheet | 10 | 0.476 | Parziale | No | Sì | 4 | 3 | 26.36 | 12712 | 3500 | 0.00204 |
| c05 | `gpt-5-mini` | JSON + datasheet | 16 | 0.762 | Parziale | No | Sì | 3 | 2 | 42.32 | 11094 | 2879 | 0.00853 |
| c05 | `gpt-5-mini` | JSON + immagine + datasheet | 16 | 0.762 | Parziale | Sì | Sì | 3 | 3 | 45.43 | 12405 | 3607 | 0.01032 |
| c05 | `gpt-5.4-nano` | JSON + datasheet | 12 | 0.571 | Parziale | No | Sì | 3 | 3 | 22.73 | 11094 | 3565 | 0.00668 |
| c05 | `gpt-5.4-nano` | JSON + immagine + datasheet | 13 | 0.619 | Parziale | Sì | Sì | 4 | 3 | 14.37 | 12405 | 2148 | 0.00517 |
| c05 | `gpt-5.4-mini` | JSON + datasheet | 19 | 0.905 | Sì | Sì | Sì | 1 | 0 | 21.64 | 11094 | 3041 | 0.02200 |
| c05 | `gpt-5.4-mini` | JSON + immagine + datasheet | 21 | 1.000 | Sì | Sì | Sì | 0 | 0 | 16.59 | 12405 | 2017 | 0.01838 |
| c05 | `gpt-5.4` | JSON + datasheet | 19 | 0.905 | Sì | Sì | Sì | 1 | 0 | 45.20 | 11094 | 3129 | 0.07467 |
| c05 | `gpt-5.4` | JSON + immagine + datasheet | 21 | 1.000 | Sì | Sì | Sì | 0 | 0 | 59.05 | 12405 | 3595 | 0.08494 |

---

## 2. Confronto JSON-only vs JSON + immagine

| Modello | JSON + datasheet | JSON + immagine + datasheet | Delta immagine | Top-1 JSON | Top-1 JSON+img | Errori JSON | Errori JSON+img |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: |
| `gpt-4o-mini` | 12 | 11 | -1 | Sì | Sì | 3 | 4 |
| `gpt-4.1-mini` | 17 | 19 | +2 | Sì | Sì | 2 | 0 |
| `gpt-4.1-nano` | 9 | 14 | +5 | No | Sì | 4 | 3 |
| `gpt-5-nano` | 11 | 10 | -1 | No | No | 3 | 4 |
| `gpt-5-mini` | 16 | 16 | +0 | No | Sì | 3 | 3 |
| `gpt-5.4-nano` | 12 | 13 | +1 | No | Sì | 3 | 4 |
| `gpt-5.4-mini` | 19 | 21 | +2 | Sì | Sì | 1 | 0 |
| `gpt-5.4` | 19 | 21 | +2 | Sì | Sì | 1 | 0 |

---

## 3. Aggregazione per input type

| Input type | N | Score medio | Mediana | Std | Top-1 accuracy | Top-3 accuracy | Errori gravi medi | Allucinazioni medie | Latenza media modello (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| JSON + datasheet | 8 | 14.38 | 14.00 | 3.60 | 50.0% | 100.0% | 2.50 | 1.88 | 28.96 |
| JSON + immagine + datasheet | 8 | 15.62 | 15.00 | 4.06 | 87.5% | 100.0% | 2.25 | 2.00 | 29.29 |

---

## 4. Aggregazione per modello

| Modello | N | Score medio | Mediana | Std | Top-1 accuracy | Top-3 accuracy | Errori gravi medi | Allucinazioni medie | Costo medio modello ($) | Latenza media modello (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 2 | 11.50 | 11.50 | 0.50 | 100.0% | 100.0% | 3.50 | 2.00 | 0.00421 | 27.02 |
| `gpt-4.1-mini` | 2 | 18.00 | 18.00 | 1.00 | 100.0% | 100.0% | 1.00 | 2.00 | 0.00832 | 26.96 |
| `gpt-4.1-nano` | 2 | 11.50 | 11.50 | 2.50 | 50.0% | 100.0% | 3.50 | 3.00 | 0.00189 | 15.97 |
| `gpt-5-nano` | 2 | 10.50 | 10.50 | 0.50 | 0.0% | 100.0% | 3.50 | 3.00 | 0.00191 | 29.39 |
| `gpt-5-mini` | 2 | 16.00 | 16.00 | 0.00 | 50.0% | 100.0% | 3.00 | 2.50 | 0.00942 | 43.87 |
| `gpt-5.4-nano` | 2 | 12.50 | 12.50 | 0.50 | 50.0% | 100.0% | 3.50 | 3.00 | 0.00592 | 18.55 |
| `gpt-5.4-mini` | 2 | 20.00 | 20.00 | 1.00 | 100.0% | 100.0% | 0.50 | 0.00 | 0.02019 | 19.12 |
| `gpt-5.4` | 2 | 20.00 | 20.00 | 1.00 | 100.0% | 100.0% | 0.50 | 0.00 | 0.07980 | 52.12 |

---

## 5. Score medi per criterio e modello

| Modello | Comprensione circuito | Uso datasheet | Uso JSON/immagine | Accuratezza diagnostica | Priorità cause | Controlli pratici | Assenza allucinazioni |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 2.00 | 1.00 | 1.50 | 2.00 | 2.00 | 2.00 | 1.00 |
| `gpt-4.1-mini` | 3.00 | 2.50 | 2.00 | 3.00 | 2.50 | 3.00 | 2.00 |
| `gpt-4.1-nano` | 2.50 | 1.50 | 1.00 | 1.50 | 1.50 | 2.50 | 1.00 |
| `gpt-5-nano` | 2.00 | 1.00 | 1.50 | 2.00 | 1.00 | 2.00 | 1.00 |
| `gpt-5-mini` | 3.00 | 2.50 | 2.00 | 2.00 | 1.50 | 3.00 | 2.00 |
| `gpt-5.4-nano` | 2.00 | 2.00 | 1.00 | 2.00 | 1.50 | 3.00 | 1.00 |
| `gpt-5.4-mini` | 3.00 | 3.00 | 3.00 | 2.50 | 3.00 | 3.00 | 2.50 |
| `gpt-5.4` | 3.00 | 3.00 | 3.00 | 2.50 | 2.50 | 3.00 | 3.00 |

---

## 6. Token, costo e latenza del judge

| Modello | Input | Judge input tokens | Judge output tokens | Judge total tokens | Costo judge stimato ($) | Latenza judge (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | JSON + datasheet | 13961 | 1316 | 15277 | 0.1093 | 26.84 |
| `gpt-4o-mini` | JSON + immagine + datasheet | 13975 | 1386 | 15361 | 0.1115 | 29.85 |
| `gpt-4.1-mini` | JSON + datasheet | 15397 | 1376 | 16773 | 0.1183 | 30.12 |
| `gpt-4.1-mini` | JSON + immagine + datasheet | 14859 | 1218 | 16077 | 0.1108 | 24.02 |
| `gpt-4.1-nano` | JSON + datasheet | 14598 | 1425 | 16023 | 0.1157 | 28.73 |
| `gpt-4.1-nano` | JSON + immagine + datasheet | 14473 | 1325 | 15798 | 0.1121 | 28.24 |
| `gpt-5-nano` | JSON + datasheet | 15449 | 1349 | 16798 | 0.1177 | 37.56 |
| `gpt-5-nano` | JSON + immagine + datasheet | 15935 | 1578 | 17513 | 0.1270 | 35.60 |
| `gpt-5-mini` | JSON + datasheet | 14843 | 1470 | 16313 | 0.1183 | 30.41 |
| `gpt-5-mini` | JSON + immagine + datasheet | 15378 | 1639 | 17017 | 0.1261 | 35.37 |
| `gpt-5.4-nano` | JSON + datasheet | 15512 | 1394 | 16906 | 0.1194 | 31.07 |
| `gpt-5.4-nano` | JSON + immagine + datasheet | 14708 | 1415 | 16123 | 0.1160 | 30.30 |
| `gpt-5.4-mini` | JSON + datasheet | 14404 | 1180 | 15584 | 0.1074 | 26.62 |
| `gpt-5.4-mini` | JSON + immagine + datasheet | 14079 | 1040 | 15119 | 0.1016 | 21.14 |
| `gpt-5.4` | JSON + datasheet | 15233 | 1413 | 16646 | 0.1186 | 31.48 |
| `gpt-5.4` | JSON + immagine + datasheet | 16014 | 853 | 16867 | 0.1057 | 16.09 |

---

## Nota sui costi

Il costo del modello rappresenta il costo operativo della diagnosi automatica, cioè quanto costerebbe eseguire il sistema di troubleshooting sul circuito.

Il costo del judge è riportato separatamente perché riguarda solo la fase di valutazione automatica offline e non farebbe parte del costo operativo del sistema finale.
