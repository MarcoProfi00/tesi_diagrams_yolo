# Tabelle judge — c13

File sorgente:

`c13__judge_summary_gpt-5.5_20260605_163919.json`

## Sintesi rapida

- Esecuzioni valutate: **16**
- Score medio `JSON + datasheet`: **16.38 / 21**
- Score medio `JSON + immagine + datasheet`: **16.00 / 21**
- Delta medio dovuto all'immagine: **-0.38 punti**
- Miglior run: **`gpt-5.4-mini`**, input **JSON + datasheet**, score **20 / 21**
- Peggior run: **`gpt-4o-mini`**, input **JSON + datasheet**, score **13 / 21**
- Costo judge stimato totale: **$1.50**

---

## 1. Risultati dettagliati per run

| Circuito | Modello | Input | Score / 21 | Score norm. | Verdict | Top-1 | Top-3 | Errori gravi | Allucinazioni | Latenza modello (s) | Input tokens | Output tokens | Costo modello ($) |
| --- | --- | --- | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| c13 | `gpt-4o-mini` | JSON + datasheet | 13 | 0.619 | Parziale | Sì | Sì | 3 | 2 | 24.73 | 6110 | 1097 | 0.00157 |
| c13 | `gpt-4o-mini` | JSON + immagine + datasheet | 13 | 0.619 | Parziale | No | Sì | 4 | 3 | 24.51 | 31693 | 1047 | 0.00538 |
| c13 | `gpt-4.1-mini` | JSON + datasheet | 17 | 0.810 | Parziale | Sì | Sì | 3 | 2 | 19.59 | 6110 | 1828 | 0.00537 |
| c13 | `gpt-4.1-mini` | JSON + immagine + datasheet | 17 | 0.810 | Sì | Sì | Sì | 3 | 2 | 19.16 | 7852 | 1642 | 0.00577 |
| c13 | `gpt-4.1-nano` | JSON + datasheet | 14 | 0.667 | Parziale | No | No | 3 | 3 | 11.74 | 6110 | 1433 | 0.00118 |
| c13 | `gpt-4.1-nano` | JSON + immagine + datasheet | 13 | 0.619 | Parziale | No | Sì | 3 | 3 | 18.69 | 8713 | 1292 | 0.00139 |
| c13 | `gpt-5-nano` | JSON + datasheet | 15 | 0.714 | Parziale | No | Sì | 3 | 3 | 30.99 | 6109 | 3194 | 0.00158 |
| c13 | `gpt-5-nano` | JSON + immagine + datasheet | 15 | 0.714 | Parziale | No | Sì | 3 | 3 | 31.21 | 7727 | 3748 | 0.00189 |
| c13 | `gpt-5-mini` | JSON + datasheet | 17 | 0.810 | Parziale | Sì | Sì | 2 | 2 | 38.33 | 6109 | 3218 | 0.00796 |
| c13 | `gpt-5-mini` | JSON + immagine + datasheet | 19 | 0.905 | Sì | Sì | Sì | 0 | 3 | 43.87 | 7420 | 3176 | 0.00821 |
| c13 | `gpt-5.4-nano` | JSON + datasheet | 16 | 0.762 | Parziale | No | Sì | 3 | 1 | 22.80 | 6109 | 3094 | 0.00509 |
| c13 | `gpt-5.4-nano` | JSON + immagine + datasheet | 13 | 0.619 | Parziale | Sì | Sì | 3 | 3 | 20.52 | 7420 | 2758 | 0.00493 |
| c13 | `gpt-5.4-mini` | JSON + datasheet | 20 | 0.952 | Sì | Sì | Sì | 0 | 1 | 25.83 | 6109 | 2738 | 0.01690 |
| c13 | `gpt-5.4-mini` | JSON + immagine + datasheet | 19 | 0.905 | Sì | Sì | Sì | 0 | 2 | 19.11 | 7420 | 2590 | 0.01722 |
| c13 | `gpt-5.4` | JSON + datasheet | 19 | 0.905 | Sì | Sì | Sì | 1 | 0 | 58.89 | 6109 | 3857 | 0.07313 |
| c13 | `gpt-5.4` | JSON + immagine + datasheet | 19 | 0.905 | Parziale | No | Sì | 1 | 2 | 70.44 | 7420 | 4204 | 0.08161 |

---

## 2. Confronto JSON-only vs JSON + immagine

| Modello | JSON + datasheet | JSON + immagine + datasheet | Delta immagine | Top-1 JSON | Top-1 JSON+img | Errori JSON | Errori JSON+img |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: |
| `gpt-4o-mini` | 13 | 13 | +0 | Sì | No | 3 | 4 |
| `gpt-4.1-mini` | 17 | 17 | +0 | Sì | Sì | 3 | 3 |
| `gpt-4.1-nano` | 14 | 13 | -1 | No | No | 3 | 3 |
| `gpt-5-nano` | 15 | 15 | +0 | No | No | 3 | 3 |
| `gpt-5-mini` | 17 | 19 | +2 | Sì | Sì | 2 | 0 |
| `gpt-5.4-nano` | 16 | 13 | -3 | No | Sì | 3 | 3 |
| `gpt-5.4-mini` | 20 | 19 | -1 | Sì | Sì | 0 | 0 |
| `gpt-5.4` | 19 | 19 | +0 | Sì | No | 1 | 1 |

---

## 3. Aggregazione per input type

| Input type | N | Score medio | Mediana | Std | Top-1 accuracy | Top-3 accuracy | Errori gravi medi | Allucinazioni medie | Latenza media modello (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| JSON + datasheet | 8 | 16.38 | 16.50 | 2.23 | 62.5% | 87.5% | 2.25 | 1.75 | 29.11 |
| JSON + immagine + datasheet | 8 | 16.00 | 16.00 | 2.65 | 50.0% | 100.0% | 2.12 | 2.62 | 30.94 |

---

## 4. Aggregazione per modello

| Modello | N | Score medio | Mediana | Std | Top-1 accuracy | Top-3 accuracy | Errori gravi medi | Allucinazioni medie | Costo medio modello ($) | Latenza media modello (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 2 | 13.00 | 13.00 | 0.00 | 50.0% | 100.0% | 3.50 | 2.50 | 0.00348 | 24.62 |
| `gpt-4.1-mini` | 2 | 17.00 | 17.00 | 0.00 | 100.0% | 100.0% | 3.00 | 2.00 | 0.00557 | 19.38 |
| `gpt-4.1-nano` | 2 | 13.50 | 13.50 | 0.50 | 0.0% | 50.0% | 3.00 | 3.00 | 0.00129 | 15.21 |
| `gpt-5-nano` | 2 | 15.00 | 15.00 | 0.00 | 0.0% | 100.0% | 3.00 | 3.00 | 0.00173 | 31.10 |
| `gpt-5-mini` | 2 | 18.00 | 18.00 | 1.00 | 100.0% | 100.0% | 1.00 | 2.50 | 0.00809 | 41.10 |
| `gpt-5.4-nano` | 2 | 14.50 | 14.50 | 1.50 | 50.0% | 100.0% | 3.00 | 2.00 | 0.00501 | 21.66 |
| `gpt-5.4-mini` | 2 | 19.50 | 19.50 | 0.50 | 100.0% | 100.0% | 0.00 | 1.50 | 0.01706 | 22.47 |
| `gpt-5.4` | 2 | 19.00 | 19.00 | 0.00 | 50.0% | 100.0% | 1.00 | 1.00 | 0.07737 | 64.67 |

---

## 5. Score medi per criterio e modello

| Modello | Comprensione circuito | Uso datasheet | Uso JSON/immagine | Accuratezza diagnostica | Priorità cause | Controlli pratici | Assenza allucinazioni |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 2.00 | 2.00 | 1.00 | 2.00 | 1.50 | 3.00 | 1.50 |
| `gpt-4.1-mini` | 2.50 | 3.00 | 2.00 | 2.00 | 2.50 | 3.00 | 2.00 |
| `gpt-4.1-nano` | 2.00 | 2.50 | 1.00 | 2.00 | 1.00 | 3.00 | 2.00 |
| `gpt-5-nano` | 2.00 | 3.00 | 2.00 | 2.00 | 1.00 | 3.00 | 2.00 |
| `gpt-5-mini` | 3.00 | 3.00 | 2.50 | 2.50 | 2.00 | 3.00 | 2.00 |
| `gpt-5.4-nano` | 2.50 | 2.50 | 1.50 | 2.00 | 1.50 | 3.00 | 1.50 |
| `gpt-5.4-mini` | 3.00 | 3.00 | 3.00 | 3.00 | 2.50 | 3.00 | 2.00 |
| `gpt-5.4` | 3.00 | 3.00 | 3.00 | 2.50 | 2.50 | 3.00 | 2.00 |

---

## 6. Token, costo e latenza del judge

| Modello | Input | Judge input tokens | Judge output tokens | Judge total tokens | Costo judge stimato ($) | Latenza judge (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | JSON + datasheet | 9028 | 1311 | 10339 | 0.0845 | 27.20 |
| `gpt-4o-mini` | JSON + immagine + datasheet | 8981 | 1585 | 10566 | 0.0925 | 36.84 |
| `gpt-4.1-mini` | JSON + datasheet | 9759 | 1396 | 11155 | 0.0907 | 32.63 |
| `gpt-4.1-mini` | JSON + immagine + datasheet | 9576 | 1294 | 10870 | 0.0867 | 27.65 |
| `gpt-4.1-nano` | JSON + datasheet | 9364 | 1471 | 10835 | 0.0910 | 35.16 |
| `gpt-4.1-nano` | JSON + immagine + datasheet | 9226 | 1486 | 10712 | 0.0907 | 31.11 |
| `gpt-5-nano` | JSON + datasheet | 10575 | 1421 | 11996 | 0.0955 | 31.98 |
| `gpt-5-nano` | JSON + immagine + datasheet | 10909 | 1832 | 12741 | 0.1095 | 40.84 |
| `gpt-5-mini` | JSON + datasheet | 10353 | 1828 | 12181 | 0.1066 | 45.84 |
| `gpt-5-mini` | JSON + immagine + datasheet | 10373 | 1157 | 11530 | 0.0866 | 24.82 |
| `gpt-5.4-nano` | JSON + datasheet | 10438 | 1928 | 12366 | 0.1100 | 46.05 |
| `gpt-5.4-nano` | JSON + immagine + datasheet | 10318 | 1523 | 11841 | 0.0973 | 29.39 |
| `gpt-5.4-mini` | JSON + datasheet | 9730 | 1257 | 10987 | 0.0864 | 28.63 |
| `gpt-5.4-mini` | JSON + immagine + datasheet | 9510 | 1341 | 10851 | 0.0878 | 28.40 |
| `gpt-5.4` | JSON + datasheet | 10607 | 1333 | 11940 | 0.0930 | 29.80 |
| `gpt-5.4` | JSON + immagine + datasheet | 11099 | 1327 | 12426 | 0.0953 | 28.99 |

---

## Nota sui costi

Il costo del modello rappresenta il costo operativo della diagnosi automatica, cioè quanto costerebbe eseguire il sistema di troubleshooting sul circuito.

Il costo del judge è riportato separatamente perché riguarda solo la fase di valutazione automatica offline e non farebbe parte del costo operativo del sistema finale.
