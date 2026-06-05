# Tabelle judge — b06

File sorgente:

`b06__judge_summary_gpt-5.5_20260605_120739.json`

## Sintesi rapida

- Esecuzioni valutate: **16**
- Score medio `JSON + datasheet`: **16.12 / 21**
- Score medio `JSON + immagine + datasheet`: **15.88 / 21**
- Delta medio dovuto all'immagine: **-0.25 punti**
- Miglior run: **`gpt-5-mini`**, input **JSON + immagine + datasheet**, score **20 / 21**
- Peggior run: **`gpt-4.1-nano`**, input **JSON + datasheet**, score **11 / 21**
- Costo judge stimato totale: **$1.35**

---

## 1. Risultati dettagliati per run

| Circuito | Modello | Input | Score / 21 | Score norm. | Verdict | Top-1 | Top-3 | Errori gravi | Allucinazioni | Latenza modello (s) | Input tokens | Output tokens | Costo modello ($) |
| --- | --- | --- | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| b06 | `gpt-4o-mini` | JSON + datasheet | 14 | 0.667 | Parziale | No | No | 3 | 2 | 16.77 | 5001 | 957 | 0.00132 |
| b06 | `gpt-4o-mini` | JSON + immagine + datasheet | 16 | 0.762 | Sì | Sì | Sì | 2 | 2 | 23.06 | 30584 | 1058 | 0.00522 |
| b06 | `gpt-4.1-mini` | JSON + datasheet | 18 | 0.857 | Sì | Sì | Sì | 2 | 2 | 22.45 | 5001 | 2020 | 0.00523 |
| b06 | `gpt-4.1-mini` | JSON + immagine + datasheet | 12 | 0.571 | Parziale | No | Sì | 4 | 4 | 16.47 | 6743 | 1645 | 0.00533 |
| b06 | `gpt-4.1-nano` | JSON + datasheet | 11 | 0.524 | Parziale | No | No | 3 | 2 | 15.22 | 5001 | 1541 | 0.00112 |
| b06 | `gpt-4.1-nano` | JSON + immagine + datasheet | 12 | 0.571 | Parziale | Sì | Sì | 3 | 3 | 10.07 | 7604 | 1377 | 0.00131 |
| b06 | `gpt-5-nano` | JSON + datasheet | 15 | 0.714 | Sì | Sì | Sì | 3 | 4 | 30.14 | 5000 | 3106 | 0.00149 |
| b06 | `gpt-5-nano` | JSON + immagine + datasheet | 14 | 0.667 | Sì | Sì | Sì | 3 | 3 | 19.65 | 6618 | 2980 | 0.00152 |
| b06 | `gpt-5-mini` | JSON + datasheet | 16 | 0.762 | Parziale | No | Sì | 2 | 2 | 31.31 | 5000 | 2743 | 0.00674 |
| b06 | `gpt-5-mini` | JSON + immagine + datasheet | 20 | 0.952 | Sì | Sì | Sì | 0 | 2 | 45.08 | 6311 | 2681 | 0.00694 |
| b06 | `gpt-5.4-nano` | JSON + datasheet | 15 | 0.714 | Parziale | No | Sì | 3 | 3 | 22.82 | 5000 | 2852 | 0.00456 |
| b06 | `gpt-5.4-nano` | JSON + immagine + datasheet | 16 | 0.762 | Parziale | Sì | Sì | 3 | 2 | 20.71 | 6311 | 2814 | 0.00478 |
| b06 | `gpt-5.4-mini` | JSON + datasheet | 20 | 0.952 | Sì | Sì | Sì | 0 | 2 | 14.93 | 5000 | 1997 | 0.01274 |
| b06 | `gpt-5.4-mini` | JSON + immagine + datasheet | 20 | 0.952 | Sì | Sì | Sì | 0 | 2 | 16.21 | 6311 | 2114 | 0.01425 |
| b06 | `gpt-5.4` | JSON + datasheet | 20 | 0.952 | Sì | Sì | Sì | 0 | 2 | 38.07 | 5000 | 2569 | 0.05103 |
| b06 | `gpt-5.4` | JSON + immagine + datasheet | 17 | 0.809 | Parziale | No | No | 3 | 0 | 52.14 | 6311 | 3395 | 0.06670 |

---

## 2. Confronto JSON-only vs JSON + immagine

| Modello | JSON + datasheet | JSON + immagine + datasheet | Delta immagine | Top-1 JSON | Top-1 JSON+img | Errori JSON | Errori JSON+img |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: |
| `gpt-4o-mini` | 14 | 16 | +2 | No | Sì | 3 | 2 |
| `gpt-4.1-mini` | 18 | 12 | -6 | Sì | No | 2 | 4 |
| `gpt-4.1-nano` | 11 | 12 | +1 | No | Sì | 3 | 3 |
| `gpt-5-nano` | 15 | 14 | -1 | Sì | Sì | 3 | 3 |
| `gpt-5-mini` | 16 | 20 | +4 | No | Sì | 2 | 0 |
| `gpt-5.4-nano` | 15 | 16 | +1 | No | Sì | 3 | 3 |
| `gpt-5.4-mini` | 20 | 20 | +0 | Sì | Sì | 0 | 0 |
| `gpt-5.4` | 20 | 17 | -3 | Sì | No | 0 | 3 |

---

## 3. Aggregazione per input type

| Input type | N | Score medio | Mediana | Std | Top-1 accuracy | Top-3 accuracy | Errori gravi medi | Allucinazioni medie | Latenza media modello (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| JSON + datasheet | 8 | 16.12 | 15.50 | 2.89 | 50.0% | 75.0% | 2.00 | 2.38 | 23.96 |
| JSON + immagine + datasheet | 8 | 15.88 | 16.00 | 2.93 | 75.0% | 87.5% | 2.25 | 2.25 | 25.42 |

---

## 4. Aggregazione per modello

| Modello | N | Score medio | Mediana | Std | Top-1 accuracy | Top-3 accuracy | Errori gravi medi | Allucinazioni medie | Costo medio modello ($) | Latenza media modello (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 2 | 15.00 | 15.00 | 1.00 | 50.0% | 50.0% | 2.50 | 2.00 | 0.00327 | 19.91 |
| `gpt-4.1-mini` | 2 | 15.00 | 15.00 | 3.00 | 50.0% | 100.0% | 3.00 | 3.00 | 0.00528 | 19.46 |
| `gpt-4.1-nano` | 2 | 11.50 | 11.50 | 0.50 | 50.0% | 50.0% | 3.00 | 2.50 | 0.00121 | 12.65 |
| `gpt-5-nano` | 2 | 14.50 | 14.50 | 0.50 | 100.0% | 100.0% | 3.00 | 3.50 | 0.00151 | 24.89 |
| `gpt-5-mini` | 2 | 18.00 | 18.00 | 2.00 | 50.0% | 100.0% | 1.00 | 2.00 | 0.00684 | 38.20 |
| `gpt-5.4-nano` | 2 | 15.50 | 15.50 | 0.50 | 50.0% | 100.0% | 3.00 | 2.50 | 0.00467 | 21.76 |
| `gpt-5.4-mini` | 2 | 20.00 | 20.00 | 0.00 | 100.0% | 100.0% | 0.00 | 2.00 | 0.01349 | 15.57 |
| `gpt-5.4` | 2 | 18.50 | 18.50 | 1.50 | 50.0% | 50.0% | 1.50 | 1.00 | 0.05887 | 45.10 |

---

## 5. Score medi per criterio e modello

| Modello | Comprensione circuito | Uso datasheet | Uso JSON/immagine | Accuratezza diagnostica | Priorità cause | Controlli pratici | Assenza allucinazioni |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 2.00 | 3.00 | 2.00 | 2.00 | 2.00 | 2.00 | 2.00 |
| `gpt-4.1-mini` | 2.00 | 2.00 | 2.50 | 2.50 | 2.00 | 2.50 | 1.50 |
| `gpt-4.1-nano` | 2.00 | 2.00 | 1.50 | 1.50 | 1.50 | 2.00 | 1.00 |
| `gpt-5-nano` | 2.00 | 2.00 | 2.50 | 2.00 | 3.00 | 2.00 | 1.00 |
| `gpt-5-mini` | 2.50 | 3.00 | 3.00 | 2.50 | 2.00 | 3.00 | 2.00 |
| `gpt-5.4-nano` | 2.00 | 3.00 | 2.00 | 2.00 | 1.50 | 3.00 | 2.00 |
| `gpt-5.4-mini` | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 2.00 |
| `gpt-5.4` | 3.00 | 3.00 | 2.50 | 2.50 | 2.00 | 3.00 | 2.50 |

---

## 6. Token, costo e latenza del judge

| Modello | Input | Judge input tokens | Judge output tokens | Judge total tokens | Costo judge stimato ($) | Latenza judge (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | JSON + datasheet | 7781 | 1247 | 9028 | 0.0763 | 31.29 |
| `gpt-4o-mini` | JSON + immagine + datasheet | 7885 | 1268 | 9153 | 0.0775 | 28.21 |
| `gpt-4.1-mini` | JSON + datasheet | 8845 | 1211 | 10056 | 0.0806 | 27.49 |
| `gpt-4.1-mini` | JSON + immagine + datasheet | 8472 | 1543 | 10015 | 0.0887 | 35.73 |
| `gpt-4.1-nano` | JSON + datasheet | 8365 | 1323 | 9688 | 0.0815 | 28.62 |
| `gpt-4.1-nano` | JSON + immagine + datasheet | 8204 | 1496 | 9700 | 0.0859 | 33.38 |
| `gpt-5-nano` | JSON + datasheet | 9585 | 1489 | 11074 | 0.0926 | 33.53 |
| `gpt-5-nano` | JSON + immagine + datasheet | 9371 | 1538 | 10909 | 0.0930 | 32.91 |
| `gpt-5-mini` | JSON + datasheet | 8889 | 1302 | 10191 | 0.0835 | 30.86 |
| `gpt-5-mini` | JSON + immagine + datasheet | 8913 | 1342 | 10255 | 0.0848 | 29.71 |
| `gpt-5.4-nano` | JSON + datasheet | 9366 | 1516 | 10882 | 0.0923 | 38.42 |
| `gpt-5.4-nano` | JSON + immagine + datasheet | 9299 | 1346 | 10645 | 0.0869 | 32.34 |
| `gpt-5.4-mini` | JSON + datasheet | 8081 | 1192 | 9273 | 0.0762 | 27.30 |
| `gpt-5.4-mini` | JSON + immagine + datasheet | 8236 | 1302 | 9538 | 0.0802 | 29.21 |
| `gpt-5.4` | JSON + datasheet | 8872 | 1074 | 9946 | 0.0766 | 27.08 |
| `gpt-5.4` | JSON + immagine + datasheet | 9902 | 1618 | 11520 | 0.0980 | 38.75 |

---

## Nota sui costi

Il costo del modello rappresenta il costo operativo della diagnosi automatica, cioè quanto costerebbe eseguire il sistema di troubleshooting sul circuito.

Il costo del judge è riportato separatamente perché riguarda solo la fase di valutazione automatica offline e non farebbe parte del costo operativo del sistema finale.
