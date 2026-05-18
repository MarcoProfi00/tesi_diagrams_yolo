# Tabelle judge — ic9

File sorgente:

`ic9__judge_summary_gpt-5.5_20260518_102814.json`

## Sintesi rapida

- Esecuzioni valutate: **16**
- Score medio `JSON + datasheet`: **16.38 / 21**
- Score medio `JSON + immagine + datasheet`: **17.12 / 21**
- Delta medio dovuto all'immagine: **+0.75 punti**
- Miglior run: **`gpt-5.4`**, input **JSON + immagine + datasheet**, score **21 / 21**
- Peggior run: **`gpt-5.4-nano`**, input **JSON + datasheet**, score **12 / 21**
- Costo judge stimato totale: **$1.48**

---

## 1. Risultati dettagliati per run

| Circuito | Modello | Input | Score / 21 | Score norm. | Verdict | Top-1 | Top-3 | Errori gravi | Allucinazioni | Latenza modello (s) | Input tokens | Output tokens | Costo modello ($) |
| --- | --- | --- | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ic9 | `gpt-4o-mini` | JSON + datasheet | 15 | 0.714 | Parziale | Sì | Sì | 2 | 2 | 16.40 | 6981 | 817 | 0.00154 |
| ic9 | `gpt-4o-mini` | JSON + immagine + datasheet | 13 | 0.619 | Parziale | Sì | Sì | 3 | 2 | 29.36 | 32563 | 877 | 0.00541 |
| ic9 | `gpt-4.1-mini` | JSON + datasheet | 20 | 0.952 | Sì | Sì | Sì | 0 | 1 | 37.15 | 6981 | 1873 | 0.00579 |
| ic9 | `gpt-4.1-mini` | JSON + immagine + datasheet | 17 | 0.809 | Sì | Sì | Sì | 2 | 2 | 17.97 | 8722 | 1432 | 0.00578 |
| ic9 | `gpt-4.1-nano` | JSON + datasheet | 16 | 0.762 | Parziale | Sì | Sì | 2 | 2 | 9.51 | 6981 | 1571 | 0.00133 |
| ic9 | `gpt-4.1-nano` | JSON + immagine + datasheet | 16 | 0.762 | Sì | Sì | Sì | 2 | 2 | 13.21 | 9583 | 1315 | 0.00148 |
| ic9 | `gpt-5-nano` | JSON + datasheet | 16 | 0.762 | Parziale | Sì | Sì | 3 | 3 | 23.16 | 6980 | 3299 | 0.00167 |
| ic9 | `gpt-5-nano` | JSON + immagine + datasheet | 17 | 0.810 | Sì | Sì | Sì | 2 | 2 | 24.18 | 8597 | 2771 | 0.00154 |
| ic9 | `gpt-5-mini` | JSON + datasheet | 15 | 0.714 | Parziale | No | Sì | 3 | 3 | 50.65 | 6980 | 3597 | 0.00894 |
| ic9 | `gpt-5-mini` | JSON + immagine + datasheet | 18 | 0.857 | Sì | Sì | Sì | 2 | 2 | 42.20 | 8290 | 3569 | 0.00921 |
| ic9 | `gpt-5.4-nano` | JSON + datasheet | 12 | 0.571 | Parziale | No | Sì | 4 | 2 | 18.96 | 6980 | 2444 | 0.00445 |
| ic9 | `gpt-5.4-nano` | JSON + immagine + datasheet | 16 | 0.762 | Parziale | Sì | Sì | 3 | 2 | 19.71 | 8290 | 2891 | 0.00527 |
| ic9 | `gpt-5.4-mini` | JSON + datasheet | 17 | 0.810 | Sì | Sì | Sì | 1 | 1 | 22.12 | 6980 | 2993 | 0.01870 |
| ic9 | `gpt-5.4-mini` | JSON + immagine + datasheet | 19 | 0.905 | Sì | Sì | Sì | 1 | 1 | 20.66 | 8290 | 2080 | 0.01558 |
| ic9 | `gpt-5.4` | JSON + datasheet | 20 | 0.952 | Sì | Sì | Sì | 0 | 0 | 47.88 | 6980 | 3153 | 0.06474 |
| ic9 | `gpt-5.4` | JSON + immagine + datasheet | 21 | 1.000 | Sì | Sì | Sì | 0 | 0 | 57.32 | 8290 | 3822 | 0.07805 |

---

## 2. Confronto JSON-only vs JSON + immagine

| Modello | JSON + datasheet | JSON + immagine + datasheet | Delta immagine | Top-1 JSON | Top-1 JSON+img | Errori JSON | Errori JSON+img |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: |
| `gpt-4o-mini` | 15 | 13 | -2 | Sì | Sì | 2 | 3 |
| `gpt-4.1-mini` | 20 | 17 | -3 | Sì | Sì | 0 | 2 |
| `gpt-4.1-nano` | 16 | 16 | +0 | Sì | Sì | 2 | 2 |
| `gpt-5-nano` | 16 | 17 | +1 | Sì | Sì | 3 | 2 |
| `gpt-5-mini` | 15 | 18 | +3 | No | Sì | 3 | 2 |
| `gpt-5.4-nano` | 12 | 16 | +4 | No | Sì | 4 | 3 |
| `gpt-5.4-mini` | 17 | 19 | +2 | Sì | Sì | 1 | 1 |
| `gpt-5.4` | 20 | 21 | +1 | Sì | Sì | 0 | 0 |

---

## 3. Aggregazione per input type

| Input type | N | Score medio | Mediana | Std | Top-1 accuracy | Top-3 accuracy | Errori gravi medi | Allucinazioni medie | Latenza media modello (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| JSON + datasheet | 8 | 16.38 | 16.00 | 2.50 | 75.0% | 100.0% | 1.88 | 1.75 | 28.23 |
| JSON + immagine + datasheet | 8 | 17.12 | 17.00 | 2.20 | 100.0% | 100.0% | 1.88 | 1.62 | 28.07 |

---

## 4. Aggregazione per modello

| Modello | N | Score medio | Mediana | Std | Top-1 accuracy | Top-3 accuracy | Errori gravi medi | Allucinazioni medie | Costo medio modello ($) | Latenza media modello (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 2 | 14.00 | 14.00 | 1.00 | 100.0% | 100.0% | 2.50 | 2.00 | 0.00347 | 22.88 |
| `gpt-4.1-mini` | 2 | 18.50 | 18.50 | 1.50 | 100.0% | 100.0% | 1.00 | 1.50 | 0.00578 | 27.56 |
| `gpt-4.1-nano` | 2 | 16.00 | 16.00 | 0.00 | 100.0% | 100.0% | 2.00 | 2.00 | 0.00141 | 11.36 |
| `gpt-5-nano` | 2 | 16.50 | 16.50 | 0.50 | 100.0% | 100.0% | 2.50 | 2.50 | 0.00160 | 23.67 |
| `gpt-5-mini` | 2 | 16.50 | 16.50 | 1.50 | 50.0% | 100.0% | 2.50 | 2.50 | 0.00907 | 46.42 |
| `gpt-5.4-nano` | 2 | 14.00 | 14.00 | 2.00 | 50.0% | 100.0% | 3.50 | 2.00 | 0.00486 | 19.34 |
| `gpt-5.4-mini` | 2 | 18.00 | 18.00 | 1.00 | 100.0% | 100.0% | 1.00 | 1.00 | 0.01714 | 21.39 |
| `gpt-5.4` | 2 | 20.50 | 20.50 | 0.50 | 100.0% | 100.0% | 0.00 | 0.00 | 0.07140 | 52.60 |

---

## 5. Score medi per criterio e modello

| Modello | Comprensione circuito | Uso datasheet | Uso JSON/immagine | Accuratezza diagnostica | Priorità cause | Controlli pratici | Assenza allucinazioni |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 2.00 | 2.00 | 1.50 | 2.00 | 1.50 | 3.00 | 2.00 |
| `gpt-4.1-mini` | 3.00 | 3.00 | 2.50 | 2.50 | 2.00 | 3.00 | 2.50 |
| `gpt-4.1-nano` | 2.00 | 2.50 | 2.00 | 2.50 | 2.00 | 3.00 | 2.00 |
| `gpt-5-nano` | 2.50 | 2.50 | 2.00 | 2.50 | 2.00 | 3.00 | 2.00 |
| `gpt-5-mini` | 3.00 | 2.50 | 2.50 | 2.50 | 1.50 | 3.00 | 1.50 |
| `gpt-5.4-nano` | 3.00 | 2.50 | 1.50 | 1.50 | 1.50 | 3.00 | 1.00 |
| `gpt-5.4-mini` | 3.00 | 2.50 | 2.50 | 2.50 | 2.50 | 3.00 | 2.00 |
| `gpt-5.4` | 3.00 | 3.00 | 3.00 | 3.00 | 2.50 | 3.00 | 3.00 |

---

## 6. Token, costo e latenza del judge

| Modello | Input | Judge input tokens | Judge output tokens | Judge total tokens | Costo judge stimato ($) | Latenza judge (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | JSON + datasheet | 9618 | 1284 | 10902 | 0.0866 | 25.90 |
| `gpt-4o-mini` | JSON + immagine + datasheet | 9681 | 1432 | 11113 | 0.0914 | 28.48 |
| `gpt-4.1-mini` | JSON + datasheet | 10674 | 1018 | 11692 | 0.0839 | 21.52 |
| `gpt-4.1-mini` | JSON + immagine + datasheet | 10236 | 1379 | 11615 | 0.0926 | 28.32 |
| `gpt-4.1-nano` | JSON + datasheet | 10372 | 1254 | 11626 | 0.0895 | 23.66 |
| `gpt-4.1-nano` | JSON + immagine + datasheet | 10118 | 1229 | 11347 | 0.0875 | 23.32 |
| `gpt-5-nano` | JSON + datasheet | 11553 | 1544 | 13097 | 0.1041 | 33.15 |
| `gpt-5-nano` | JSON + immagine + datasheet | 11343 | 1215 | 12558 | 0.0932 | 23.41 |
| `gpt-5-mini` | JSON + datasheet | 11201 | 1637 | 12838 | 0.1051 | 33.31 |
| `gpt-5-mini` | JSON + immagine + datasheet | 11440 | 1438 | 12878 | 0.1003 | 30.80 |
| `gpt-5.4-nano` | JSON + datasheet | 10857 | 1454 | 12311 | 0.0979 | 29.51 |
| `gpt-5.4-nano` | JSON + immagine + datasheet | 11306 | 1323 | 12629 | 0.0962 | 28.05 |
| `gpt-5.4-mini` | JSON + datasheet | 10872 | 1133 | 12005 | 0.0883 | 22.75 |
| `gpt-5.4-mini` | JSON + immagine + datasheet | 10410 | 1148 | 11558 | 0.0865 | 20.26 |
| `gpt-5.4` | JSON + datasheet | 11352 | 1191 | 12543 | 0.0925 | 26.40 |
| `gpt-5.4` | JSON + immagine + datasheet | 11869 | 885 | 12754 | 0.0859 | 16.39 |

---

## Nota sui costi

Il costo del modello rappresenta il costo operativo della diagnosi automatica, cioè quanto costerebbe eseguire il sistema di troubleshooting sul circuito.

Il costo del judge è riportato separatamente perché riguarda solo la fase di valutazione automatica offline e non farebbe parte del costo operativo del sistema finale.
