# Tabelle judge — ic8

File sorgente:

`ic8__judge_summary_gpt-5.5_20260518_165925.json`

## Sintesi rapida

- Esecuzioni valutate: **16**
- Score medio `JSON + datasheet`: **16.25 / 21**
- Score medio `JSON + immagine + datasheet`: **13.75 / 21**
- Delta medio dovuto all'immagine: **-2.50 punti**
- Miglior run: **`gpt-5.4-mini`**, input **JSON + datasheet**, score **20 / 21**
- Peggior run: **`gpt-4.1-nano`**, input **JSON + immagine + datasheet**, score **8 / 21**
- Costo judge stimato totale: **$2.07**

---

## 1. Risultati dettagliati per run

| Circuito | Modello | Input | Score / 21 | Score norm. | Verdict | Top-1 | Top-3 | Errori gravi | Allucinazioni | Latenza modello (s) | Input tokens | Output tokens | Costo modello ($) |
| --- | --- | --- | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ic8 | `gpt-4o-mini` | JSON + datasheet | 16 | 0.762 | Parziale | Sì | Sì | 3 | 2 | 68.68 | 13280 | 929 | 0.00255 |
| ic8 | `gpt-4o-mini` | JSON + immagine + datasheet | 10 | 0.476 | Parziale | No | Sì | 4 | 3 | 42.64 | 38863 | 1046 | 0.00646 |
| ic8 | `gpt-4.1-mini` | JSON + datasheet | 19 | 0.905 | Sì | Sì | Sì | 1 | 2 | 102.68 | 13280 | 2350 | 0.00907 |
| ic8 | `gpt-4.1-mini` | JSON + immagine + datasheet | 11 | 0.524 | Parziale | No | No | 3 | 4 | 34.44 | 15022 | 2030 | 0.00926 |
| ic8 | `gpt-4.1-nano` | JSON + datasheet | 9 | 0.429 | Parziale | No | No | 4 | 4 | 26.25 | 13280 | 2036 | 0.00214 |
| ic8 | `gpt-4.1-nano` | JSON + immagine + datasheet | 8 | 0.381 | Parziale | No | No | 4 | 3 | 16.54 | 15883 | 1778 | 0.00230 |
| ic8 | `gpt-5-nano` | JSON + datasheet | 9 | 0.429 | Parziale | No | No | 4 | 4 | 29.96 | 13279 | 3753 | 0.00217 |
| ic8 | `gpt-5-nano` | JSON + immagine + datasheet | 14 | 0.667 | Parziale | No | Sì | 3 | 2 | 27.95 | 14897 | 4174 | 0.00241 |
| ic8 | `gpt-5-mini` | JSON + datasheet | 18 | 0.857 | Parziale | No | Sì | 2 | 2 | 39.41 | 13279 | 2875 | 0.00907 |
| ic8 | `gpt-5-mini` | JSON + immagine + datasheet | 16 | 0.762 | Parziale | No | Sì | 3 | 2 | 54.06 | 14590 | 3845 | 0.01134 |
| ic8 | `gpt-5.4-nano` | JSON + datasheet | 19 | 0.905 | Sì | Sì | Sì | 2 | 2 | 23.16 | 13279 | 3235 | 0.00670 |
| ic8 | `gpt-5.4-nano` | JSON + immagine + datasheet | 12 | 0.571 | Parziale | No | Sì | 4 | 3 | 21.56 | 14590 | 2922 | 0.00657 |
| ic8 | `gpt-5.4-mini` | JSON + datasheet | 20 | 0.952 | Sì | Sì | Sì | 0 | 2 | 21.75 | 13279 | 2485 | 0.02114 |
| ic8 | `gpt-5.4-mini` | JSON + immagine + datasheet | 19 | 0.905 | Sì | Sì | Sì | 0 | 2 | 29.05 | 14590 | 3317 | 0.02587 |
| ic8 | `gpt-5.4` | JSON + datasheet | 20 | 0.952 | Sì | Sì | Sì | 0 | 2 | 53.63 | 13279 | 3653 | 0.08799 |
| ic8 | `gpt-5.4` | JSON + immagine + datasheet | 20 | 0.952 | Sì | Sì | Sì | 0 | 2 | 50.14 | 14590 | 3145 | 0.08365 |

---

## 2. Confronto JSON-only vs JSON + immagine

| Modello | JSON + datasheet | JSON + immagine + datasheet | Delta immagine | Top-1 JSON | Top-1 JSON+img | Errori JSON | Errori JSON+img |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: |
| `gpt-4o-mini` | 16 | 10 | -6 | Sì | No | 3 | 4 |
| `gpt-4.1-mini` | 19 | 11 | -8 | Sì | No | 1 | 3 |
| `gpt-4.1-nano` | 9 | 8 | -1 | No | No | 4 | 4 |
| `gpt-5-nano` | 9 | 14 | +5 | No | No | 4 | 3 |
| `gpt-5-mini` | 18 | 16 | -2 | No | No | 2 | 3 |
| `gpt-5.4-nano` | 19 | 12 | -7 | Sì | No | 2 | 4 |
| `gpt-5.4-mini` | 20 | 19 | -1 | Sì | Sì | 0 | 0 |
| `gpt-5.4` | 20 | 20 | +0 | Sì | Sì | 0 | 0 |

---

## 3. Aggregazione per input type

| Input type | N | Score medio | Mediana | Std | Top-1 accuracy | Top-3 accuracy | Errori gravi medi | Allucinazioni medie | Latenza media modello (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| JSON + datasheet | 8 | 16.25 | 18.50 | 4.35 | 62.5% | 75.0% | 2.00 | 2.50 | 45.69 |
| JSON + immagine + datasheet | 8 | 13.75 | 13.00 | 4.02 | 25.0% | 75.0% | 2.62 | 2.62 | 34.55 |

---

## 4. Aggregazione per modello

| Modello | N | Score medio | Mediana | Std | Top-1 accuracy | Top-3 accuracy | Errori gravi medi | Allucinazioni medie | Costo medio modello ($) | Latenza media modello (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 2 | 13.00 | 13.00 | 3.00 | 50.0% | 100.0% | 3.50 | 2.50 | 0.00450 | 55.66 |
| `gpt-4.1-mini` | 2 | 15.00 | 15.00 | 4.00 | 50.0% | 50.0% | 2.00 | 3.00 | 0.00916 | 68.56 |
| `gpt-4.1-nano` | 2 | 8.50 | 8.50 | 0.50 | 0.0% | 0.0% | 4.00 | 3.50 | 0.00222 | 21.40 |
| `gpt-5-nano` | 2 | 11.50 | 11.50 | 2.50 | 0.0% | 50.0% | 3.50 | 3.00 | 0.00229 | 28.95 |
| `gpt-5-mini` | 2 | 17.00 | 17.00 | 1.00 | 0.0% | 100.0% | 2.50 | 2.00 | 0.01020 | 46.74 |
| `gpt-5.4-nano` | 2 | 15.50 | 15.50 | 3.50 | 50.0% | 100.0% | 3.00 | 2.50 | 0.00664 | 22.36 |
| `gpt-5.4-mini` | 2 | 19.50 | 19.50 | 0.50 | 100.0% | 100.0% | 0.00 | 2.00 | 0.02351 | 25.40 |
| `gpt-5.4` | 2 | 20.00 | 20.00 | 0.00 | 100.0% | 100.0% | 0.00 | 2.00 | 0.08582 | 51.89 |

---

## 5. Score medi per criterio e modello

| Modello | Comprensione circuito | Uso datasheet | Uso JSON/immagine | Accuratezza diagnostica | Priorità cause | Controlli pratici | Assenza allucinazioni |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 2.50 | 2.00 | 1.50 | 1.50 | 2.00 | 2.00 | 1.50 |
| `gpt-4.1-mini` | 3.00 | 2.00 | 2.00 | 2.00 | 2.00 | 2.50 | 1.50 |
| `gpt-4.1-nano` | 2.00 | 1.50 | 1.00 | 1.00 | 0.00 | 2.00 | 1.00 |
| `gpt-5-nano` | 2.00 | 2.00 | 1.50 | 1.50 | 0.50 | 2.50 | 1.50 |
| `gpt-5-mini` | 3.00 | 3.00 | 2.50 | 2.00 | 1.50 | 3.00 | 2.00 |
| `gpt-5.4-nano` | 2.50 | 2.50 | 2.00 | 2.00 | 2.00 | 3.00 | 1.50 |
| `gpt-5.4-mini` | 3.00 | 3.00 | 3.00 | 3.00 | 2.50 | 3.00 | 2.00 |
| `gpt-5.4` | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 2.00 |

---

## 6. Token, costo e latenza del judge

| Modello | Input | Judge input tokens | Judge output tokens | Judge total tokens | Costo judge stimato ($) | Latenza judge (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | JSON + datasheet | 16030 | 1471 | 17501 | 0.1243 | 22.99 |
| `gpt-4o-mini` | JSON + immagine + datasheet | 16150 | 1532 | 17682 | 0.1267 | 26.04 |
| `gpt-4.1-mini` | JSON + datasheet | 17451 | 1347 | 18798 | 0.1277 | 23.18 |
| `gpt-4.1-mini` | JSON + immagine + datasheet | 17134 | 1605 | 18739 | 0.1338 | 28.99 |
| `gpt-4.1-nano` | JSON + datasheet | 17137 | 1612 | 18749 | 0.1340 | 25.31 |
| `gpt-4.1-nano` | JSON + immagine + datasheet | 16882 | 1426 | 18308 | 0.1272 | 23.99 |
| `gpt-5-nano` | JSON + datasheet | 17752 | 1618 | 19370 | 0.1373 | 27.60 |
| `gpt-5-nano` | JSON + immagine + datasheet | 18593 | 1438 | 20031 | 0.1361 | 24.44 |
| `gpt-5-mini` | JSON + datasheet | 17241 | 1449 | 18690 | 0.1297 | 27.48 |
| `gpt-5-mini` | JSON + immagine + datasheet | 17818 | 1357 | 19175 | 0.1298 | 24.70 |
| `gpt-5.4-nano` | JSON + datasheet | 17606 | 1401 | 19007 | 0.1301 | 27.36 |
| `gpt-5.4-nano` | JSON + immagine + datasheet | 17765 | 1611 | 19376 | 0.1372 | 27.04 |
| `gpt-5.4-mini` | JSON + datasheet | 17284 | 1299 | 18583 | 0.1254 | 23.78 |
| `gpt-5.4-mini` | JSON + immagine + datasheet | 17091 | 1337 | 18428 | 0.1256 | 21.70 |
| `gpt-5.4` | JSON + datasheet | 17779 | 1309 | 19088 | 0.1282 | 23.50 |
| `gpt-5.4` | JSON + immagine + datasheet | 17265 | 1080 | 18345 | 0.1187 | 18.77 |

---

## Nota sui costi

Il costo del modello rappresenta il costo operativo della diagnosi automatica, cioè quanto costerebbe eseguire il sistema di troubleshooting sul circuito.

Il costo del judge è riportato separatamente perché riguarda solo la fase di valutazione automatica offline e non farebbe parte del costo operativo del sistema finale.
