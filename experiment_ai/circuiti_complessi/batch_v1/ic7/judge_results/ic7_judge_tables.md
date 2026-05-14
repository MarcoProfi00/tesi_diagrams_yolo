# Tabelle judge — ic7

File sorgente:

`ic7__judge_summary_gpt-5.5_20260514_184028.json`

## Sintesi rapida

- Esecuzioni valutate: **16**
- Score medio `JSON + datasheet`: **14.88 / 21**
- Score medio `JSON + immagine + datasheet`: **17.00 / 21**
- Delta medio dovuto all'immagine: **+2.12 punti**
- Miglior run: **`gpt-5.4-mini`**, input **JSON + immagine + datasheet**, score **20 / 21**
- Peggior run: **`gpt-5.4-nano`**, input **JSON + datasheet**, score **11 / 21**
- Costo judge stimato totale: **$1.44**

---

## 1. Risultati dettagliati per run

| Circuito | Modello | Input | Score / 21 | Score norm. | Verdict | Top-1 | Top-3 | Errori gravi | Allucinazioni | Latenza modello (s) | Input tokens | Output tokens | Costo modello ($) |
| --- | --- | --- | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ic7 | `gpt-4o-mini` | JSON + datasheet | 16 | 0.762 | Parziale | Sì | Sì | 2 | 2 | 22.06 | 5197 | 999 | 0.00138 |
| ic7 | `gpt-4o-mini` | JSON + immagine + datasheet | 15 | 0.714 | Parziale | No | Sì | 3 | 3 | 23.58 | 30780 | 1208 | 0.00534 |
| ic7 | `gpt-4.1-mini` | JSON + datasheet | 14 | 0.667 | Parziale | No | Sì | 3 | 2 | 29.77 | 5197 | 1877 | 0.00508 |
| ic7 | `gpt-4.1-mini` | JSON + immagine + datasheet | 18 | 0.857 | Sì | Sì | Sì | 2 | 2 | 21.17 | 6939 | 1264 | 0.00480 |
| ic7 | `gpt-4.1-nano` | JSON + datasheet | 17 | 0.810 | Sì | Sì | Sì | 2 | 3 | 18.34 | 5197 | 1435 | 0.00109 |
| ic7 | `gpt-4.1-nano` | JSON + immagine + datasheet | 17 | 0.809 | Parziale | Sì | Sì | 2 | 2 | 13.24 | 7800 | 1333 | 0.00131 |
| ic7 | `gpt-5-nano` | JSON + datasheet | 12 | 0.571 | Parziale | No | Sì | 3 | 3 | 41.51 | 5196 | 4155 | 0.00192 |
| ic7 | `gpt-5-nano` | JSON + immagine + datasheet | 18 | 0.857 | Sì | Sì | Sì | 2 | 2 | 26.12 | 6814 | 3088 | 0.00158 |
| ic7 | `gpt-5-mini` | JSON + datasheet | 18 | 0.857 | Sì | Sì | Sì | 1 | 2 | 49.04 | 5196 | 3058 | 0.00741 |
| ic7 | `gpt-5-mini` | JSON + immagine + datasheet | 14 | 0.667 | Parziale | No | Sì | 3 | 3 | 44.33 | 6507 | 3064 | 0.00775 |
| ic7 | `gpt-5.4-nano` | JSON + datasheet | 11 | 0.524 | Parziale | No | Sì | 3 | 3 | 15.16 | 5196 | 2270 | 0.00388 |
| ic7 | `gpt-5.4-nano` | JSON + immagine + datasheet | 17 | 0.810 | Sì | Sì | Sì | 2 | 2 | 18.00 | 6507 | 2524 | 0.00446 |
| ic7 | `gpt-5.4-mini` | JSON + datasheet | 17 | 0.809 | Parziale | Sì | Sì | 3 | 2 | 23.65 | 5196 | 2871 | 0.01682 |
| ic7 | `gpt-5.4-mini` | JSON + immagine + datasheet | 20 | 0.952 | Sì | Sì | Sì | 0 | 0 | 20.84 | 6507 | 2525 | 0.01624 |
| ic7 | `gpt-5.4` | JSON + datasheet | 14 | 0.667 | Parziale | No | No | 4 | 3 | 53.56 | 5196 | 3486 | 0.06528 |
| ic7 | `gpt-5.4` | JSON + immagine + datasheet | 17 | 0.810 | Parziale | No | No | 2 | 2 | 49.95 | 6507 | 3282 | 0.06550 |

---

## 2. Confronto JSON-only vs JSON + immagine

| Modello | JSON + datasheet | JSON + immagine + datasheet | Delta immagine | Top-1 JSON | Top-1 JSON+img | Errori JSON | Errori JSON+img |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: |
| `gpt-4o-mini` | 16 | 15 | -1 | Sì | No | 2 | 3 |
| `gpt-4.1-mini` | 14 | 18 | +4 | No | Sì | 3 | 2 |
| `gpt-4.1-nano` | 17 | 17 | +0 | Sì | Sì | 2 | 2 |
| `gpt-5-nano` | 12 | 18 | +6 | No | Sì | 3 | 2 |
| `gpt-5-mini` | 18 | 14 | -4 | Sì | No | 1 | 3 |
| `gpt-5.4-nano` | 11 | 17 | +6 | No | Sì | 3 | 2 |
| `gpt-5.4-mini` | 17 | 20 | +3 | Sì | Sì | 3 | 0 |
| `gpt-5.4` | 14 | 17 | +3 | No | No | 4 | 2 |

---

## 3. Aggregazione per input type

| Input type | N | Score medio | Mediana | Std | Top-1 accuracy | Top-3 accuracy | Errori gravi medi | Allucinazioni medie | Latenza media modello (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| JSON + datasheet | 8 | 14.88 | 15.00 | 2.37 | 50.0% | 87.5% | 2.62 | 2.50 | 31.64 |
| JSON + immagine + datasheet | 8 | 17.00 | 17.00 | 1.73 | 62.5% | 87.5% | 2.00 | 2.00 | 27.15 |

---

## 4. Aggregazione per modello

| Modello | N | Score medio | Mediana | Std | Top-1 accuracy | Top-3 accuracy | Errori gravi medi | Allucinazioni medie | Costo medio modello ($) | Latenza media modello (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 2 | 15.50 | 15.50 | 0.50 | 50.0% | 100.0% | 2.50 | 2.50 | 0.00336 | 22.82 |
| `gpt-4.1-mini` | 2 | 16.00 | 16.00 | 2.00 | 50.0% | 100.0% | 2.50 | 2.00 | 0.00494 | 25.47 |
| `gpt-4.1-nano` | 2 | 17.00 | 17.00 | 0.00 | 100.0% | 100.0% | 2.00 | 2.50 | 0.00120 | 15.79 |
| `gpt-5-nano` | 2 | 15.00 | 15.00 | 3.00 | 50.0% | 100.0% | 2.50 | 2.50 | 0.00175 | 33.82 |
| `gpt-5-mini` | 2 | 16.00 | 16.00 | 2.00 | 50.0% | 100.0% | 2.00 | 2.50 | 0.00758 | 46.69 |
| `gpt-5.4-nano` | 2 | 14.00 | 14.00 | 3.00 | 50.0% | 100.0% | 2.50 | 2.50 | 0.00417 | 16.58 |
| `gpt-5.4-mini` | 2 | 18.50 | 18.50 | 1.50 | 100.0% | 100.0% | 1.50 | 1.00 | 0.01653 | 22.25 |
| `gpt-5.4` | 2 | 15.50 | 15.50 | 1.50 | 0.0% | 0.0% | 3.00 | 2.50 | 0.06539 | 51.75 |

---

## 5. Score medi per criterio e modello

| Modello | Comprensione circuito | Uso datasheet | Uso JSON/immagine | Accuratezza diagnostica | Priorità cause | Controlli pratici | Assenza allucinazioni |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 3.00 | 2.00 | 2.00 | 2.00 | 1.50 | 3.00 | 2.00 |
| `gpt-4.1-mini` | 2.50 | 2.50 | 2.00 | 2.50 | 1.50 | 3.00 | 2.00 |
| `gpt-4.1-nano` | 3.00 | 3.00 | 2.00 | 2.00 | 2.00 | 3.00 | 2.00 |
| `gpt-5-nano` | 2.50 | 2.50 | 2.00 | 2.00 | 1.50 | 3.00 | 1.50 |
| `gpt-5-mini` | 3.00 | 2.50 | 2.50 | 2.00 | 1.50 | 3.00 | 1.50 |
| `gpt-5.4-nano` | 2.50 | 2.50 | 1.50 | 1.50 | 1.50 | 3.00 | 1.50 |
| `gpt-5.4-mini` | 3.00 | 2.50 | 3.00 | 2.50 | 2.00 | 3.00 | 2.50 |
| `gpt-5.4` | 3.00 | 2.50 | 2.50 | 2.00 | 1.00 | 3.00 | 1.50 |

---

## 6. Token, costo e latenza del judge

| Modello | Input | Judge input tokens | Judge output tokens | Judge total tokens | Costo judge stimato ($) | Latenza judge (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | JSON + datasheet | 8017 | 1381 | 9398 | 0.0815 | 24.06 |
| `gpt-4o-mini` | JSON + immagine + datasheet | 8229 | 1550 | 9779 | 0.0876 | 28.71 |
| `gpt-4.1-mini` | JSON + datasheet | 8895 | 1474 | 10369 | 0.0887 | 26.03 |
| `gpt-4.1-mini` | JSON + immagine + datasheet | 8285 | 1387 | 9672 | 0.0830 | 26.77 |
| `gpt-4.1-nano` | JSON + datasheet | 8452 | 1500 | 9952 | 0.0873 | 25.40 |
| `gpt-4.1-nano` | JSON + immagine + datasheet | 8354 | 1566 | 9920 | 0.0887 | 28.16 |
| `gpt-5-nano` | JSON + datasheet | 10176 | 1824 | 12000 | 0.1056 | 33.78 |
| `gpt-5-nano` | JSON + immagine + datasheet | 9658 | 1333 | 10991 | 0.0883 | 23.86 |
| `gpt-5-mini` | JSON + datasheet | 9268 | 1322 | 10590 | 0.0860 | 21.44 |
| `gpt-5-mini` | JSON + immagine + datasheet | 9127 | 1482 | 10609 | 0.0901 | 26.65 |
| `gpt-5.4-nano` | JSON + datasheet | 8961 | 1464 | 10425 | 0.0887 | 25.83 |
| `gpt-5.4-nano` | JSON + immagine + datasheet | 9230 | 1373 | 10603 | 0.0873 | 24.85 |
| `gpt-5.4-mini` | JSON + datasheet | 8902 | 1892 | 10794 | 0.1013 | 34.83 |
| `gpt-5.4-mini` | JSON + immagine + datasheet | 8787 | 986 | 9773 | 0.0735 | 16.39 |
| `gpt-5.4` | JSON + datasheet | 9983 | 1863 | 11846 | 0.1058 | 34.15 |
| `gpt-5.4` | JSON + immagine + datasheet | 9851 | 1552 | 11403 | 0.0958 | 28.22 |

---

## Nota sui costi

Il costo del modello rappresenta il costo operativo della diagnosi automatica, cioè quanto costerebbe eseguire il sistema di troubleshooting sul circuito.

Il costo del judge è riportato separatamente perché riguarda solo la fase di valutazione automatica offline e non farebbe parte del costo operativo del sistema finale.
