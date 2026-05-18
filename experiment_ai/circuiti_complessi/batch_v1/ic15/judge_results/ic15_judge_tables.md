# Tabelle judge — ic15

File sorgente:

`ic15__judge_summary_gpt-5.5_20260518_173025.json`

## Sintesi rapida

- Esecuzioni valutate: **16**
- Score medio `JSON + datasheet`: **13.00 / 21**
- Score medio `JSON + immagine + datasheet`: **11.88 / 21**
- Delta medio dovuto all'immagine: **-1.12 punti**
- Miglior run: **`gpt-5-mini`**, input **JSON + datasheet**, score **20 / 21**
- Peggior run: **`gpt-4.1-mini`**, input **JSON + datasheet**, score **8 / 21**
- Costo judge stimato totale: **$1.88**

---

## 1. Risultati dettagliati per run

| Circuito | Modello | Input | Score / 21 | Score norm. | Verdict | Top-1 | Top-3 | Errori gravi | Allucinazioni | Latenza modello (s) | Input tokens | Output tokens | Costo modello ($) |
| --- | --- | --- | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ic15 | `gpt-4o-mini` | JSON + datasheet | 10 | 0.476 | Parziale | No | Sì | 5 | 2 | 42.55 | 10873 | 916 | 0.00218 |
| ic15 | `gpt-4o-mini` | JSON + immagine + datasheet | 10 | 0.476 | Parziale | No | No | 3 | 2 | 30.77 | 36456 | 958 | 0.00604 |
| ic15 | `gpt-4.1-mini` | JSON + datasheet | 8 | 0.381 | No | No | No | 5 | 3 | 52.85 | 10873 | 2064 | 0.00765 |
| ic15 | `gpt-4.1-mini` | JSON + immagine + datasheet | 10 | 0.476 | Parziale | No | No | 4 | 4 | 45.88 | 12615 | 1829 | 0.00797 |
| ic15 | `gpt-4.1-nano` | JSON + datasheet | 9 | 0.429 | Parziale | No | No | 4 | 3 | 18.88 | 10873 | 1738 | 0.00178 |
| ic15 | `gpt-4.1-nano` | JSON + immagine + datasheet | 9 | 0.429 | Parziale | No | No | 4 | 2 | 14.54 | 13476 | 1442 | 0.00192 |
| ic15 | `gpt-5-nano` | JSON + datasheet | 8 | 0.381 | Parziale | No | No | 5 | 5 | 29.90 | 10872 | 3780 | 0.00206 |
| ic15 | `gpt-5-nano` | JSON + immagine + datasheet | 9 | 0.429 | Parziale | No | No | 5 | 4 | 34.86 | 12490 | 4255 | 0.00233 |
| ic15 | `gpt-5-mini` | JSON + datasheet | 20 | 0.952 | Sì | Sì | Sì | 0 | 2 | 43.24 | 10872 | 3054 | 0.00883 |
| ic15 | `gpt-5-mini` | JSON + immagine + datasheet | 15 | 0.714 | Parziale | No | Sì | 3 | 2 | 53.56 | 12183 | 3601 | 0.01025 |
| ic15 | `gpt-5.4-nano` | JSON + datasheet | 10 | 0.476 | Parziale | No | No | 4 | 3 | 24.55 | 10872 | 3450 | 0.00649 |
| ic15 | `gpt-5.4-nano` | JSON + immagine + datasheet | 10 | 0.476 | Parziale | No | No | 4 | 3 | 21.48 | 12183 | 2805 | 0.00594 |
| ic15 | `gpt-5.4-mini` | JSON + datasheet | 19 | 0.905 | Sì | Sì | Sì | 2 | 2 | 27.21 | 10872 | 3217 | 0.02263 |
| ic15 | `gpt-5.4-mini` | JSON + immagine + datasheet | 13 | 0.619 | Parziale | No | Sì | 3 | 2 | 18.44 | 12183 | 2185 | 0.01897 |
| ic15 | `gpt-5.4` | JSON + datasheet | 20 | 0.952 | Sì | Sì | Sì | 0 | 1 | 53.15 | 10872 | 3446 | 0.07887 |
| ic15 | `gpt-5.4` | JSON + immagine + datasheet | 19 | 0.905 | Parziale | No | Sì | 2 | 0 | 52.13 | 12183 | 3298 | 0.07993 |

---

## 2. Confronto JSON-only vs JSON + immagine

| Modello | JSON + datasheet | JSON + immagine + datasheet | Delta immagine | Top-1 JSON | Top-1 JSON+img | Errori JSON | Errori JSON+img |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: |
| `gpt-4o-mini` | 10 | 10 | +0 | No | No | 5 | 3 |
| `gpt-4.1-mini` | 8 | 10 | +2 | No | No | 5 | 4 |
| `gpt-4.1-nano` | 9 | 9 | +0 | No | No | 4 | 4 |
| `gpt-5-nano` | 8 | 9 | +1 | No | No | 5 | 5 |
| `gpt-5-mini` | 20 | 15 | -5 | Sì | No | 0 | 3 |
| `gpt-5.4-nano` | 10 | 10 | +0 | No | No | 4 | 4 |
| `gpt-5.4-mini` | 19 | 13 | -6 | Sì | No | 2 | 3 |
| `gpt-5.4` | 20 | 19 | -1 | Sì | No | 0 | 2 |

---

## 3. Aggregazione per input type

| Input type | N | Score medio | Mediana | Std | Top-1 accuracy | Top-3 accuracy | Errori gravi medi | Allucinazioni medie | Latenza media modello (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| JSON + datasheet | 8 | 13.00 | 10.00 | 5.22 | 37.5% | 50.0% | 3.12 | 2.62 | 36.54 |
| JSON + immagine + datasheet | 8 | 11.88 | 10.00 | 3.33 | 0.0% | 37.5% | 3.50 | 2.38 | 33.96 |

---

## 4. Aggregazione per modello

| Modello | N | Score medio | Mediana | Std | Top-1 accuracy | Top-3 accuracy | Errori gravi medi | Allucinazioni medie | Costo medio modello ($) | Latenza media modello (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 2 | 10.00 | 10.00 | 0.00 | 0.0% | 50.0% | 4.00 | 2.00 | 0.00411 | 36.66 |
| `gpt-4.1-mini` | 2 | 9.00 | 9.00 | 1.00 | 0.0% | 0.0% | 4.50 | 3.50 | 0.00781 | 49.36 |
| `gpt-4.1-nano` | 2 | 9.00 | 9.00 | 0.00 | 0.0% | 0.0% | 4.00 | 2.50 | 0.00185 | 16.71 |
| `gpt-5-nano` | 2 | 8.50 | 8.50 | 0.50 | 0.0% | 0.0% | 5.00 | 4.50 | 0.00219 | 32.38 |
| `gpt-5-mini` | 2 | 17.50 | 17.50 | 2.50 | 50.0% | 100.0% | 1.50 | 2.00 | 0.00954 | 48.41 |
| `gpt-5.4-nano` | 2 | 10.00 | 10.00 | 0.00 | 0.0% | 0.0% | 4.00 | 3.00 | 0.00621 | 23.02 |
| `gpt-5.4-mini` | 2 | 16.00 | 16.00 | 3.00 | 50.0% | 100.0% | 2.50 | 2.00 | 0.02080 | 22.82 |
| `gpt-5.4` | 2 | 19.50 | 19.50 | 0.50 | 50.0% | 100.0% | 1.00 | 0.50 | 0.07940 | 52.64 |

---

## 5. Score medi per criterio e modello

| Modello | Comprensione circuito | Uso datasheet | Uso JSON/immagine | Accuratezza diagnostica | Priorità cause | Controlli pratici | Assenza allucinazioni |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 2.00 | 2.00 | 1.00 | 1.00 | 0.50 | 2.00 | 1.50 |
| `gpt-4.1-mini` | 2.00 | 1.50 | 1.00 | 1.00 | 0.50 | 2.00 | 1.00 |
| `gpt-4.1-nano` | 2.00 | 2.00 | 1.00 | 1.00 | 0.00 | 2.00 | 1.00 |
| `gpt-5-nano` | 2.00 | 1.50 | 1.00 | 1.00 | 0.00 | 2.00 | 1.00 |
| `gpt-5-mini` | 3.00 | 3.00 | 2.00 | 2.50 | 2.00 | 3.00 | 2.00 |
| `gpt-5.4-nano` | 2.00 | 2.00 | 1.50 | 1.00 | 0.50 | 2.00 | 1.00 |
| `gpt-5.4-mini` | 3.00 | 2.50 | 1.50 | 2.00 | 2.00 | 3.00 | 2.00 |
| `gpt-5.4` | 3.00 | 3.00 | 3.00 | 2.50 | 2.50 | 3.00 | 2.50 |

---

## 6. Token, costo e latenza del judge

| Modello | Input | Judge input tokens | Judge output tokens | Judge total tokens | Costo judge stimato ($) | Latenza judge (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | JSON + datasheet | 13610 | 1381 | 14991 | 0.1095 | 27.57 |
| `gpt-4o-mini` | JSON + immagine + datasheet | 13655 | 1293 | 14948 | 0.1071 | 25.80 |
| `gpt-4.1-mini` | JSON + datasheet | 14758 | 1425 | 16183 | 0.1165 | 26.05 |
| `gpt-4.1-mini` | JSON + immagine + datasheet | 14526 | 1533 | 16059 | 0.1186 | 24.50 |
| `gpt-4.1-nano` | JSON + datasheet | 14432 | 1458 | 15890 | 0.1159 | 25.88 |
| `gpt-4.1-nano` | JSON + immagine + datasheet | 14137 | 1381 | 15518 | 0.1121 | 22.75 |
| `gpt-5-nano` | JSON + datasheet | 15864 | 1941 | 17805 | 0.1376 | 34.95 |
| `gpt-5-nano` | JSON + immagine + datasheet | 16402 | 1487 | 17889 | 0.1266 | 24.93 |
| `gpt-5-mini` | JSON + datasheet | 14927 | 1161 | 16088 | 0.1095 | 20.32 |
| `gpt-5-mini` | JSON + immagine + datasheet | 15306 | 1503 | 16809 | 0.1216 | 24.70 |
| `gpt-5.4-nano` | JSON + datasheet | 14927 | 1452 | 16379 | 0.1182 | 23.46 |
| `gpt-5.4-nano` | JSON + immagine + datasheet | 14954 | 1544 | 16498 | 0.1211 | 28.56 |
| `gpt-5.4-mini` | JSON + datasheet | 14573 | 1767 | 16340 | 0.1259 | 30.91 |
| `gpt-5.4-mini` | JSON + immagine + datasheet | 14833 | 1308 | 16141 | 0.1134 | 23.37 |
| `gpt-5.4` | JSON + datasheet | 15337 | 1151 | 16488 | 0.1112 | 20.05 |
| `gpt-5.4` | JSON + immagine + datasheet | 15404 | 1260 | 16664 | 0.1148 | 23.63 |

---

## Nota sui costi

Il costo del modello rappresenta il costo operativo della diagnosi automatica, cioè quanto costerebbe eseguire il sistema di troubleshooting sul circuito.

Il costo del judge è riportato separatamente perché riguarda solo la fase di valutazione automatica offline e non farebbe parte del costo operativo del sistema finale.
