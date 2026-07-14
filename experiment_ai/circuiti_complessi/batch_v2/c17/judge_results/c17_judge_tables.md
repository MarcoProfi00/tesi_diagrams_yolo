# Tabelle judge — c17

File sorgente:

`c17__judge_summary_gpt-5.5_20260605_171459.json`

## Sintesi rapida

- Esecuzioni valutate: **16**
- Score medio `JSON + datasheet`: **14.50 / 21**
- Score medio `JSON + immagine + datasheet`: **17.25 / 21**
- Delta medio dovuto all'immagine: **+2.75 punti**
- Miglior run: **`gpt-5-mini`**, input **JSON + immagine + datasheet**, score **20 / 21**
- Peggior run: **`gpt-4.1-nano`**, input **JSON + datasheet**, score **12 / 21**
- Costo judge stimato totale: **$1.28**

---

## 1. Risultati dettagliati per run

| Circuito | Modello | Input | Score / 21 | Score norm. | Verdict | Top-1 | Top-3 | Errori gravi | Allucinazioni | Latenza modello (s) | Input tokens | Output tokens | Costo modello ($) |
| --- | --- | --- | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| c17 | `gpt-4o-mini` | JSON + datasheet | 13 | 0.619 | Parziale | No | Sì | 3 | 1 | 42.17 | 3923 | 896 | 0.00113 |
| c17 | `gpt-4o-mini` | JSON + immagine + datasheet | 14 | 0.667 | Parziale | Sì | Sì | 3 | 3 | 19.24 | 29506 | 1083 | 0.00508 |
| c17 | `gpt-4.1-mini` | JSON + datasheet | 14 | 0.667 | Parziale | No | Sì | 2 | 2 | 21.97 | 3923 | 1751 | 0.00437 |
| c17 | `gpt-4.1-mini` | JSON + immagine + datasheet | 17 | 0.810 | Sì | Sì | Sì | 2 | 2 | 24.42 | 5665 | 1441 | 0.00457 |
| c17 | `gpt-4.1-nano` | JSON + datasheet | 12 | 0.571 | Parziale | No | Sì | 3 | 2 | 21.98 | 3923 | 1353 | 0.00093 |
| c17 | `gpt-4.1-nano` | JSON + immagine + datasheet | 14 | 0.667 | Parziale | Sì | Sì | 2 | 3 | 30.87 | 6526 | 1380 | 0.00120 |
| c17 | `gpt-5-nano` | JSON + datasheet | 14 | 0.667 | Parziale | No | Sì | 3 | 3 | 31.45 | 3922 | 3291 | 0.00151 |
| c17 | `gpt-5-nano` | JSON + immagine + datasheet | 17 | 0.810 | Parziale | Sì | Sì | 2 | 2 | 25.73 | 5540 | 3335 | 0.00161 |
| c17 | `gpt-5-mini` | JSON + datasheet | 18 | 0.857 | Parziale | Sì | Sì | 1 | 1 | 27.61 | 3922 | 2281 | 0.00554 |
| c17 | `gpt-5-mini` | JSON + immagine + datasheet | 20 | 0.952 | Sì | Sì | Sì | 0 | 0 | 46.95 | 5233 | 2959 | 0.00723 |
| c17 | `gpt-5.4-nano` | JSON + datasheet | 16 | 0.762 | Parziale | No | Sì | 3 | 3 | 20.43 | 3922 | 2822 | 0.00431 |
| c17 | `gpt-5.4-nano` | JSON + immagine + datasheet | 17 | 0.810 | Sì | Sì | Sì | 2 | 2 | 18.98 | 5233 | 2806 | 0.00455 |
| c17 | `gpt-5.4-mini` | JSON + datasheet | 14 | 0.667 | Parziale | No | Sì | 2 | 1 | 14.31 | 3922 | 2159 | 0.01266 |
| c17 | `gpt-5.4-mini` | JSON + immagine + datasheet | 19 | 0.905 | Sì | Sì | Sì | 0 | 2 | 16.64 | 5233 | 2015 | 0.01299 |
| c17 | `gpt-5.4` | JSON + datasheet | 15 | 0.714 | Parziale | No | Sì | 2 | 1 | 48.78 | 3922 | 3400 | 0.06080 |
| c17 | `gpt-5.4` | JSON + immagine + datasheet | 20 | 0.952 | Sì | Sì | Sì | 0 | 1 | 58.47 | 5233 | 3655 | 0.06791 |

---

## 2. Confronto JSON-only vs JSON + immagine

| Modello | JSON + datasheet | JSON + immagine + datasheet | Delta immagine | Top-1 JSON | Top-1 JSON+img | Errori JSON | Errori JSON+img |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: |
| `gpt-4o-mini` | 13 | 14 | +1 | No | Sì | 3 | 3 |
| `gpt-4.1-mini` | 14 | 17 | +3 | No | Sì | 2 | 2 |
| `gpt-4.1-nano` | 12 | 14 | +2 | No | Sì | 3 | 2 |
| `gpt-5-nano` | 14 | 17 | +3 | No | Sì | 3 | 2 |
| `gpt-5-mini` | 18 | 20 | +2 | Sì | Sì | 1 | 0 |
| `gpt-5.4-nano` | 16 | 17 | +1 | No | Sì | 3 | 2 |
| `gpt-5.4-mini` | 14 | 19 | +5 | No | Sì | 2 | 0 |
| `gpt-5.4` | 15 | 20 | +5 | No | Sì | 2 | 0 |

---

## 3. Aggregazione per input type

| Input type | N | Score medio | Mediana | Std | Top-1 accuracy | Top-3 accuracy | Errori gravi medi | Allucinazioni medie | Latenza media modello (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| JSON + datasheet | 8 | 14.50 | 14.00 | 1.73 | 12.5% | 100.0% | 2.38 | 1.75 | 28.59 |
| JSON + immagine + datasheet | 8 | 17.25 | 17.00 | 2.22 | 100.0% | 100.0% | 1.38 | 1.88 | 30.16 |

---

## 4. Aggregazione per modello

| Modello | N | Score medio | Mediana | Std | Top-1 accuracy | Top-3 accuracy | Errori gravi medi | Allucinazioni medie | Costo medio modello ($) | Latenza media modello (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 2 | 13.50 | 13.50 | 0.50 | 50.0% | 100.0% | 3.00 | 2.00 | 0.00310 | 30.70 |
| `gpt-4.1-mini` | 2 | 15.50 | 15.50 | 1.50 | 50.0% | 100.0% | 2.00 | 2.00 | 0.00447 | 23.20 |
| `gpt-4.1-nano` | 2 | 13.00 | 13.00 | 1.00 | 50.0% | 100.0% | 2.50 | 2.50 | 0.00107 | 26.42 |
| `gpt-5-nano` | 2 | 15.50 | 15.50 | 1.50 | 50.0% | 100.0% | 2.50 | 2.50 | 0.00156 | 28.59 |
| `gpt-5-mini` | 2 | 19.00 | 19.00 | 1.00 | 100.0% | 100.0% | 0.50 | 0.50 | 0.00638 | 37.28 |
| `gpt-5.4-nano` | 2 | 16.50 | 16.50 | 0.50 | 50.0% | 100.0% | 2.50 | 2.50 | 0.00443 | 19.71 |
| `gpt-5.4-mini` | 2 | 16.50 | 16.50 | 2.50 | 50.0% | 100.0% | 1.00 | 1.50 | 0.01282 | 15.47 |
| `gpt-5.4` | 2 | 17.50 | 17.50 | 2.50 | 50.0% | 100.0% | 1.00 | 1.00 | 0.06436 | 53.63 |

---

## 5. Score medi per criterio e modello

| Modello | Comprensione circuito | Uso datasheet | Uso JSON/immagine | Accuratezza diagnostica | Priorità cause | Controlli pratici | Assenza allucinazioni |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 2.00 | 2.00 | 2.00 | 2.00 | 1.50 | 2.00 | 2.00 |
| `gpt-4.1-mini` | 2.50 | 2.00 | 2.00 | 2.50 | 1.50 | 3.00 | 2.00 |
| `gpt-4.1-nano` | 2.00 | 2.00 | 1.50 | 2.00 | 1.00 | 3.00 | 1.50 |
| `gpt-5-nano` | 2.50 | 2.50 | 2.00 | 2.00 | 1.50 | 3.00 | 2.00 |
| `gpt-5-mini` | 3.00 | 3.00 | 3.00 | 2.50 | 2.00 | 3.00 | 2.50 |
| `gpt-5.4-nano` | 3.00 | 2.50 | 2.50 | 2.00 | 1.50 | 3.00 | 2.00 |
| `gpt-5.4-mini` | 2.50 | 2.50 | 2.50 | 2.50 | 1.50 | 3.00 | 2.00 |
| `gpt-5.4` | 2.50 | 2.50 | 3.00 | 2.50 | 2.00 | 3.00 | 2.00 |

---

## 6. Token, costo e latenza del judge

| Modello | Input | Judge input tokens | Judge output tokens | Judge total tokens | Costo judge stimato ($) | Latenza judge (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | JSON + datasheet | 6640 | 1378 | 8018 | 0.0745 | 32.84 |
| `gpt-4o-mini` | JSON + immagine + datasheet | 6830 | 1470 | 8300 | 0.0783 | 33.09 |
| `gpt-4.1-mini` | JSON + datasheet | 7495 | 1370 | 8865 | 0.0786 | 34.17 |
| `gpt-4.1-mini` | JSON + immagine + datasheet | 7188 | 1323 | 8511 | 0.0756 | 28.69 |
| `gpt-4.1-nano` | JSON + datasheet | 7097 | 1372 | 8469 | 0.0766 | 32.61 |
| `gpt-4.1-nano` | JSON + immagine + datasheet | 7127 | 1416 | 8543 | 0.0781 | 33.17 |
| `gpt-5-nano` | JSON + datasheet | 8414 | 1767 | 10181 | 0.0951 | 42.52 |
| `gpt-5-nano` | JSON + immagine + datasheet | 8470 | 1411 | 9881 | 0.0847 | 34.29 |
| `gpt-5-mini` | JSON + datasheet | 7566 | 1450 | 9016 | 0.0813 | 35.44 |
| `gpt-5-mini` | JSON + immagine + datasheet | 7926 | 1137 | 9063 | 0.0737 | 27.78 |
| `gpt-5.4-nano` | JSON + datasheet | 8018 | 1490 | 9508 | 0.0848 | 36.30 |
| `gpt-5.4-nano` | JSON + immagine + datasheet | 8092 | 1591 | 9683 | 0.0882 | 34.37 |
| `gpt-5.4-mini` | JSON + datasheet | 7518 | 1176 | 8694 | 0.0729 | 27.26 |
| `gpt-5.4-mini` | JSON + immagine + datasheet | 6997 | 1260 | 8257 | 0.0728 | 30.55 |
| `gpt-5.4` | JSON + datasheet | 8509 | 1379 | 9888 | 0.0839 | 30.69 |
| `gpt-5.4` | JSON + immagine + datasheet | 8773 | 1090 | 9863 | 0.0766 | 23.82 |

---

## Nota sui costi

Il costo del modello rappresenta il costo operativo della diagnosi automatica, cioè quanto costerebbe eseguire il sistema di troubleshooting sul circuito.

Il costo del judge è riportato separatamente perché riguarda solo la fase di valutazione automatica offline e non farebbe parte del costo operativo del sistema finale.
