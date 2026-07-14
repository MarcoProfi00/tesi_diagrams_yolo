# Tabelle judge — c01

File sorgente:

`c01__judge_summary_gpt-5.5_20260605_143127.json`

## Sintesi rapida

- Esecuzioni valutate: **16**
- Score medio `JSON + datasheet`: **12.88 / 21**
- Score medio `JSON + immagine + datasheet`: **14.38 / 21**
- Delta medio dovuto all'immagine: **+1.50 punti**
- Miglior run: **`gpt-5.4`**, input **JSON + immagine + datasheet**, score **20 / 21**
- Peggior run: **`gpt-5-nano`**, input **JSON + datasheet**, score **8 / 21**
- Costo judge stimato totale: **$1.32**

---

## 1. Risultati dettagliati per run

| Circuito | Modello | Input | Score / 21 | Score norm. | Verdict | Top-1 | Top-3 | Errori gravi | Allucinazioni | Latenza modello (s) | Input tokens | Output tokens | Costo modello ($) |
| --- | --- | --- | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| c01 | `gpt-4o-mini` | JSON + datasheet | 10 | 0.476 | Parziale | No | Sì | 4 | 3 | 17.33 | 4694 | 955 | 0.00128 |
| c01 | `gpt-4o-mini` | JSON + immagine + datasheet | 10 | 0.476 | Parziale | No | No | 3 | 2 | 20.39 | 30277 | 876 | 0.00507 |
| c01 | `gpt-4.1-mini` | JSON + datasheet | 17 | 0.810 | Parziale | No | Sì | 3 | 2 | 69.50 | 4694 | 1761 | 0.00470 |
| c01 | `gpt-4.1-mini` | JSON + immagine + datasheet | 16 | 0.762 | Parziale | No | Sì | 3 | 3 | 49.22 | 6436 | 1545 | 0.00505 |
| c01 | `gpt-4.1-nano` | JSON + datasheet | 9 | 0.429 | Parziale | No | Sì | 4 | 5 | 20.13 | 4694 | 1618 | 0.00112 |
| c01 | `gpt-4.1-nano` | JSON + immagine + datasheet | 12 | 0.571 | Parziale | No | Sì | 4 | 4 | 15.68 | 7297 | 1232 | 0.00122 |
| c01 | `gpt-5-nano` | JSON + datasheet | 8 | 0.381 | Parziale | No | Sì | 4 | 6 | 21.95 | 4693 | 3468 | 0.00162 |
| c01 | `gpt-5-nano` | JSON + immagine + datasheet | 9 | 0.429 | Parziale | No | Sì | 5 | 6 | 19.05 | 6311 | 2863 | 0.00146 |
| c01 | `gpt-5-mini` | JSON + datasheet | 18 | 0.857 | Parziale | No | Sì | 2 | 2 | 32.90 | 4693 | 2905 | 0.00698 |
| c01 | `gpt-5-mini` | JSON + immagine + datasheet | 19 | 0.905 | Sì | Sì | Sì | 2 | 1 | 36.90 | 6004 | 3035 | 0.00757 |
| c01 | `gpt-5.4-nano` | JSON + datasheet | 13 | 0.619 | Parziale | No | No | 4 | 2 | 18.20 | 4693 | 2817 | 0.00446 |
| c01 | `gpt-5.4-nano` | JSON + immagine + datasheet | 13 | 0.619 | Parziale | No | Sì | 3 | 3 | 16.13 | 6004 | 2202 | 0.00395 |
| c01 | `gpt-5.4-mini` | JSON + datasheet | 9 | 0.429 | Parziale | No | No | 3 | 2 | 15.19 | 4693 | 2187 | 0.01336 |
| c01 | `gpt-5.4-mini` | JSON + immagine + datasheet | 16 | 0.762 | Parziale | No | No | 2 | 1 | 16.91 | 6004 | 2296 | 0.01483 |
| c01 | `gpt-5.4` | JSON + datasheet | 19 | 0.905 | Sì | Sì | Sì | 0 | 0 | 42.86 | 4693 | 3214 | 0.05994 |
| c01 | `gpt-5.4` | JSON + immagine + datasheet | 20 | 0.952 | Sì | Sì | Sì | 0 | 0 | 51.01 | 6004 | 3172 | 0.06259 |

---

## 2. Confronto JSON-only vs JSON + immagine

| Modello | JSON + datasheet | JSON + immagine + datasheet | Delta immagine | Top-1 JSON | Top-1 JSON+img | Errori JSON | Errori JSON+img |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: |
| `gpt-4o-mini` | 10 | 10 | +0 | No | No | 4 | 3 |
| `gpt-4.1-mini` | 17 | 16 | -1 | No | No | 3 | 3 |
| `gpt-4.1-nano` | 9 | 12 | +3 | No | No | 4 | 4 |
| `gpt-5-nano` | 8 | 9 | +1 | No | No | 4 | 5 |
| `gpt-5-mini` | 18 | 19 | +1 | No | Sì | 2 | 2 |
| `gpt-5.4-nano` | 13 | 13 | +0 | No | No | 4 | 3 |
| `gpt-5.4-mini` | 9 | 16 | +7 | No | No | 3 | 2 |
| `gpt-5.4` | 19 | 20 | +1 | Sì | Sì | 0 | 0 |

---

## 3. Aggregazione per input type

| Input type | N | Score medio | Mediana | Std | Top-1 accuracy | Top-3 accuracy | Errori gravi medi | Allucinazioni medie | Latenza media modello (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| JSON + datasheet | 8 | 12.88 | 11.50 | 4.23 | 12.5% | 75.0% | 3.00 | 2.75 | 29.76 |
| JSON + immagine + datasheet | 8 | 14.38 | 14.50 | 3.77 | 25.0% | 75.0% | 2.75 | 2.50 | 28.16 |

---

## 4. Aggregazione per modello

| Modello | N | Score medio | Mediana | Std | Top-1 accuracy | Top-3 accuracy | Errori gravi medi | Allucinazioni medie | Costo medio modello ($) | Latenza media modello (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 2 | 10.00 | 10.00 | 0.00 | 0.0% | 50.0% | 3.50 | 2.50 | 0.00317 | 18.86 |
| `gpt-4.1-mini` | 2 | 16.50 | 16.50 | 0.50 | 0.0% | 100.0% | 3.00 | 2.50 | 0.00487 | 59.36 |
| `gpt-4.1-nano` | 2 | 10.50 | 10.50 | 1.50 | 0.0% | 100.0% | 4.00 | 4.50 | 0.00117 | 17.91 |
| `gpt-5-nano` | 2 | 8.50 | 8.50 | 0.50 | 0.0% | 100.0% | 4.50 | 6.00 | 0.00154 | 20.50 |
| `gpt-5-mini` | 2 | 18.50 | 18.50 | 0.50 | 50.0% | 100.0% | 2.00 | 1.50 | 0.00728 | 34.90 |
| `gpt-5.4-nano` | 2 | 13.00 | 13.00 | 0.00 | 0.0% | 50.0% | 3.50 | 2.50 | 0.00421 | 17.16 |
| `gpt-5.4-mini` | 2 | 12.50 | 12.50 | 3.50 | 0.0% | 0.0% | 2.50 | 1.50 | 0.01410 | 16.05 |
| `gpt-5.4` | 2 | 19.50 | 19.50 | 0.50 | 100.0% | 100.0% | 0.00 | 0.00 | 0.06127 | 46.94 |

---

## 5. Score medi per criterio e modello

| Modello | Comprensione circuito | Uso datasheet | Uso JSON/immagine | Accuratezza diagnostica | Priorità cause | Controlli pratici | Assenza allucinazioni |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 1.50 | 2.00 | 1.00 | 1.50 | 0.50 | 2.00 | 1.50 |
| `gpt-4.1-mini` | 3.00 | 3.00 | 2.50 | 2.00 | 1.00 | 3.00 | 2.00 |
| `gpt-4.1-nano` | 1.50 | 2.00 | 1.00 | 2.00 | 1.00 | 2.50 | 0.50 |
| `gpt-5-nano` | 1.00 | 2.00 | 1.00 | 1.50 | 1.00 | 2.00 | 0.00 |
| `gpt-5-mini` | 3.00 | 3.00 | 3.00 | 2.50 | 2.00 | 3.00 | 2.00 |
| `gpt-5.4-nano` | 2.00 | 3.00 | 1.00 | 1.50 | 1.00 | 3.00 | 1.50 |
| `gpt-5.4-mini` | 2.50 | 2.50 | 1.50 | 1.50 | 0.50 | 2.50 | 1.50 |
| `gpt-5.4` | 3.00 | 3.00 | 3.00 | 2.50 | 2.00 | 3.00 | 3.00 |

---

## 6. Token, costo e latenza del judge

| Modello | Input | Judge input tokens | Judge output tokens | Judge total tokens | Costo judge stimato ($) | Latenza judge (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | JSON + datasheet | 7470 | 1336 | 8806 | 0.0774 | 28.68 |
| `gpt-4o-mini` | JSON + immagine + datasheet | 7394 | 1236 | 8630 | 0.0741 | 27.32 |
| `gpt-4.1-mini` | JSON + datasheet | 8276 | 1384 | 9660 | 0.0829 | 30.94 |
| `gpt-4.1-mini` | JSON + immagine + datasheet | 8063 | 1326 | 9389 | 0.0801 | 27.23 |
| `gpt-4.1-nano` | JSON + datasheet | 8133 | 1238 | 9371 | 0.0778 | 27.46 |
| `gpt-4.1-nano` | JSON + immagine + datasheet | 7750 | 1385 | 9135 | 0.0803 | 27.38 |
| `gpt-5-nano` | JSON + datasheet | 9195 | 1357 | 10552 | 0.0867 | 27.71 |
| `gpt-5-nano` | JSON + immagine + datasheet | 8885 | 1459 | 10344 | 0.0882 | 27.19 |
| `gpt-5-mini` | JSON + datasheet | 8532 | 1488 | 10020 | 0.0873 | 31.59 |
| `gpt-5-mini` | JSON + immagine + datasheet | 8764 | 1450 | 10214 | 0.0873 | 31.36 |
| `gpt-5.4-nano` | JSON + datasheet | 8892 | 1547 | 10439 | 0.0909 | 33.17 |
| `gpt-5.4-nano` | JSON + immagine + datasheet | 8332 | 1476 | 9808 | 0.0859 | 32.96 |
| `gpt-5.4-mini` | JSON + datasheet | 7856 | 1295 | 9151 | 0.0781 | 29.82 |
| `gpt-5.4-mini` | JSON + immagine + datasheet | 7935 | 1241 | 9176 | 0.0769 | 27.13 |
| `gpt-5.4` | JSON + datasheet | 9352 | 1283 | 10635 | 0.0852 | 28.91 |
| `gpt-5.4` | JSON + immagine + datasheet | 9487 | 1073 | 10560 | 0.0796 | 24.14 |

---

## Nota sui costi

Il costo del modello rappresenta il costo operativo della diagnosi automatica, cioè quanto costerebbe eseguire il sistema di troubleshooting sul circuito.

Il costo del judge è riportato separatamente perché riguarda solo la fase di valutazione automatica offline e non farebbe parte del costo operativo del sistema finale.
