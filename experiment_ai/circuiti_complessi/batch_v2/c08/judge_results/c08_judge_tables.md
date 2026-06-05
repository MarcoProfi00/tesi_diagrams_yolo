# Tabelle judge — c08

File sorgente:

`c08__judge_summary_gpt-5.5_20260605_160711.json`

## Sintesi rapida

- Esecuzioni valutate: **16**
- Score medio `JSON + datasheet`: **13.25 / 21**
- Score medio `JSON + immagine + datasheet`: **14.00 / 21**
- Delta medio dovuto all'immagine: **+0.75 punti**
- Miglior run: **`gpt-5.4`**, input **JSON + immagine + datasheet**, score **20 / 21**
- Peggior run: **`gpt-4.1-nano`**, input **JSON + datasheet**, score **9 / 21**
- Costo judge stimato totale: **$1.89**

---

## 1. Risultati dettagliati per run

| Circuito | Modello | Input | Score / 21 | Score norm. | Verdict | Top-1 | Top-3 | Errori gravi | Allucinazioni | Latenza modello (s) | Input tokens | Output tokens | Costo modello ($) |
| --- | --- | --- | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| c08 | `gpt-4o-mini` | JSON + datasheet | 11 | 0.524 | Parziale | No | No | 3 | 2 | 17.06 | 10577 | 1016 | 0.00220 |
| c08 | `gpt-4o-mini` | JSON + immagine + datasheet | 12 | 0.571 | Parziale | No | Sì | 4 | 2 | 19.14 | 36160 | 894 | 0.00596 |
| c08 | `gpt-4.1-mini` | JSON + datasheet | 11 | 0.524 | Parziale | No | No | 4 | 4 | 27.50 | 10577 | 1907 | 0.00728 |
| c08 | `gpt-4.1-mini` | JSON + immagine + datasheet | 12 | 0.571 | Parziale | No | No | 3 | 3 | 25.01 | 12319 | 1985 | 0.00810 |
| c08 | `gpt-4.1-nano` | JSON + datasheet | 9 | 0.429 | Parziale | No | Sì | 4 | 3 | 19.03 | 10577 | 1535 | 0.00167 |
| c08 | `gpt-4.1-nano` | JSON + immagine + datasheet | 12 | 0.571 | Parziale | No | No | 4 | 3 | 27.19 | 13180 | 1249 | 0.00182 |
| c08 | `gpt-5-nano` | JSON + datasheet | 12 | 0.571 | Parziale | No | Sì | 4 | 4 | 32.56 | 10576 | 3662 | 0.00199 |
| c08 | `gpt-5-nano` | JSON + immagine + datasheet | 14 | 0.667 | Parziale | No | No | 3 | 4 | 34.11 | 12194 | 3512 | 0.00201 |
| c08 | `gpt-5-mini` | JSON + datasheet | 18 | 0.857 | Sì | Sì | Sì | 2 | 2 | 39.22 | 10576 | 3460 | 0.00956 |
| c08 | `gpt-5-mini` | JSON + immagine + datasheet | 11 | 0.524 | Parziale | No | Sì | 4 | 2 | 39.69 | 11887 | 3304 | 0.00958 |
| c08 | `gpt-5.4-nano` | JSON + datasheet | 17 | 0.810 | Sì | Sì | Sì | 2 | 1 | 22.28 | 10576 | 3185 | 0.00610 |
| c08 | `gpt-5.4-nano` | JSON + immagine + datasheet | 15 | 0.714 | Parziale | No | Sì | 3 | 2 | 22.57 | 11887 | 2835 | 0.00592 |
| c08 | `gpt-5.4-mini` | JSON + datasheet | 11 | 0.524 | No | No | No | 3 | 2 | 20.70 | 10576 | 2821 | 0.02063 |
| c08 | `gpt-5.4-mini` | JSON + immagine + datasheet | 16 | 0.762 | Sì | Sì | Sì | 2 | 2 | 23.44 | 11887 | 2929 | 0.02210 |
| c08 | `gpt-5.4` | JSON + datasheet | 17 | 0.809 | Sì | Sì | Sì | 2 | 0 | 54.26 | 10576 | 3456 | 0.07828 |
| c08 | `gpt-5.4` | JSON + immagine + datasheet | 20 | 0.952 | Sì | Sì | Sì | 0 | 2 | 54.77 | 11887 | 3470 | 0.08177 |

---

## 2. Confronto JSON-only vs JSON + immagine

| Modello | JSON + datasheet | JSON + immagine + datasheet | Delta immagine | Top-1 JSON | Top-1 JSON+img | Errori JSON | Errori JSON+img |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: |
| `gpt-4o-mini` | 11 | 12 | +1 | No | No | 3 | 4 |
| `gpt-4.1-mini` | 11 | 12 | +1 | No | No | 4 | 3 |
| `gpt-4.1-nano` | 9 | 12 | +3 | No | No | 4 | 4 |
| `gpt-5-nano` | 12 | 14 | +2 | No | No | 4 | 3 |
| `gpt-5-mini` | 18 | 11 | -7 | Sì | No | 2 | 4 |
| `gpt-5.4-nano` | 17 | 15 | -2 | Sì | No | 2 | 3 |
| `gpt-5.4-mini` | 11 | 16 | +5 | No | Sì | 3 | 2 |
| `gpt-5.4` | 17 | 20 | +3 | Sì | Sì | 2 | 0 |

---

## 3. Aggregazione per input type

| Input type | N | Score medio | Mediana | Std | Top-1 accuracy | Top-3 accuracy | Errori gravi medi | Allucinazioni medie | Latenza media modello (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| JSON + datasheet | 8 | 13.25 | 11.50 | 3.27 | 37.5% | 62.5% | 3.00 | 2.25 | 29.07 |
| JSON + immagine + datasheet | 8 | 14.00 | 13.00 | 2.78 | 25.0% | 62.5% | 2.88 | 2.50 | 30.74 |

---

## 4. Aggregazione per modello

| Modello | N | Score medio | Mediana | Std | Top-1 accuracy | Top-3 accuracy | Errori gravi medi | Allucinazioni medie | Costo medio modello ($) | Latenza media modello (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 2 | 11.50 | 11.50 | 0.50 | 0.0% | 50.0% | 3.50 | 2.00 | 0.00408 | 18.10 |
| `gpt-4.1-mini` | 2 | 11.50 | 11.50 | 0.50 | 0.0% | 0.0% | 3.50 | 3.50 | 0.00769 | 26.25 |
| `gpt-4.1-nano` | 2 | 10.50 | 10.50 | 1.50 | 0.0% | 50.0% | 4.00 | 3.00 | 0.00174 | 23.11 |
| `gpt-5-nano` | 2 | 13.00 | 13.00 | 1.00 | 0.0% | 50.0% | 3.50 | 4.00 | 0.00200 | 33.34 |
| `gpt-5-mini` | 2 | 14.50 | 14.50 | 3.50 | 50.0% | 100.0% | 3.00 | 2.00 | 0.00957 | 39.45 |
| `gpt-5.4-nano` | 2 | 16.00 | 16.00 | 1.00 | 50.0% | 100.0% | 2.50 | 1.50 | 0.00601 | 22.43 |
| `gpt-5.4-mini` | 2 | 13.50 | 13.50 | 2.50 | 50.0% | 50.0% | 2.50 | 2.00 | 0.02136 | 22.07 |
| `gpt-5.4` | 2 | 18.50 | 18.50 | 1.50 | 100.0% | 100.0% | 1.00 | 1.00 | 0.08002 | 54.51 |

---

## 5. Score medi per criterio e modello

| Modello | Comprensione circuito | Uso datasheet | Uso JSON/immagine | Accuratezza diagnostica | Priorità cause | Controlli pratici | Assenza allucinazioni |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 2.00 | 1.50 | 1.50 | 1.50 | 1.00 | 2.00 | 2.00 |
| `gpt-4.1-mini` | 2.00 | 2.50 | 1.00 | 1.50 | 1.00 | 2.50 | 1.00 |
| `gpt-4.1-nano` | 2.00 | 1.00 | 1.50 | 1.50 | 1.00 | 2.00 | 1.50 |
| `gpt-5-nano` | 2.00 | 2.00 | 2.00 | 2.00 | 1.00 | 3.00 | 1.00 |
| `gpt-5-mini` | 3.00 | 2.50 | 2.50 | 1.50 | 1.00 | 2.50 | 1.50 |
| `gpt-5.4-nano` | 3.00 | 2.50 | 2.50 | 1.50 | 1.50 | 3.00 | 2.00 |
| `gpt-5.4-mini` | 2.00 | 2.00 | 2.00 | 1.50 | 1.50 | 2.50 | 2.00 |
| `gpt-5.4` | 2.50 | 3.00 | 3.00 | 2.50 | 2.50 | 3.00 | 2.00 |

---

## 6. Token, costo e latenza del judge

| Modello | Input | Judge input tokens | Judge output tokens | Judge total tokens | Costo judge stimato ($) | Latenza judge (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | JSON + datasheet | 13414 | 1449 | 14863 | 0.1105 | 27.86 |
| `gpt-4o-mini` | JSON + immagine + datasheet | 13295 | 1514 | 14809 | 0.1119 | 33.65 |
| `gpt-4.1-mini` | JSON + datasheet | 14305 | 1474 | 15779 | 0.1157 | 33.10 |
| `gpt-4.1-mini` | JSON + immagine + datasheet | 14386 | 1650 | 16036 | 0.1214 | 39.67 |
| `gpt-4.1-nano` | JSON + datasheet | 13933 | 1505 | 15438 | 0.1148 | 30.36 |
| `gpt-4.1-nano` | JSON + immagine + datasheet | 13650 | 1695 | 15345 | 0.1191 | 638.78 |
| `gpt-5-nano` | JSON + datasheet | 15524 | 1686 | 17210 | 0.1282 | 35.00 |
| `gpt-5-nano` | JSON + immagine + datasheet | 15522 | 1494 | 17016 | 0.1224 | 32.75 |
| `gpt-5-mini` | JSON + datasheet | 14908 | 1495 | 16403 | 0.1194 | 34.04 |
| `gpt-5-mini` | JSON + immagine + datasheet | 14973 | 1489 | 16462 | 0.1195 | 32.11 |
| `gpt-5.4-nano` | JSON + datasheet | 14705 | 1301 | 16006 | 0.1126 | 28.30 |
| `gpt-5.4-nano` | JSON + immagine + datasheet | 14883 | 1671 | 16554 | 0.1245 | 36.14 |
| `gpt-5.4-mini` | JSON + datasheet | 14163 | 1517 | 15680 | 0.1163 | 32.62 |
| `gpt-5.4-mini` | JSON + immagine + datasheet | 14011 | 1435 | 15446 | 0.1131 | 29.74 |
| `gpt-5.4` | JSON + datasheet | 14728 | 1643 | 16371 | 0.1229 | 38.30 |
| `gpt-5.4` | JSON + immagine + datasheet | 15241 | 1350 | 16591 | 0.1167 | 30.12 |

---

## Nota sui costi

Il costo del modello rappresenta il costo operativo della diagnosi automatica, cioè quanto costerebbe eseguire il sistema di troubleshooting sul circuito.

Il costo del judge è riportato separatamente perché riguarda solo la fase di valutazione automatica offline e non farebbe parte del costo operativo del sistema finale.
