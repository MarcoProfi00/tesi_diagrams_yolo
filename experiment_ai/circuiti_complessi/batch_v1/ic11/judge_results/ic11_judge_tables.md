# Tabelle judge — ic11

File sorgente:

`ic11__judge_summary_gpt-5.5_20260518_105909.json`

## Sintesi rapida

- Esecuzioni valutate: **16**
- Score medio `JSON + datasheet`: **13.88 / 21**
- Score medio `JSON + immagine + datasheet`: **15.12 / 21**
- Delta medio dovuto all'immagine: **+1.25 punti**
- Miglior run: **`gpt-5.4`**, input **JSON + immagine + datasheet**, score **21 / 21**
- Peggior run: **`gpt-4.1-nano`**, input **JSON + datasheet**, score **8 / 21**
- Costo judge stimato totale: **$1.49**

---

## 1. Risultati dettagliati per run

| Circuito | Modello | Input | Score / 21 | Score norm. | Verdict | Top-1 | Top-3 | Errori gravi | Allucinazioni | Latenza modello (s) | Input tokens | Output tokens | Costo modello ($) |
| --- | --- | --- | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ic11 | `gpt-4o-mini` | JSON + datasheet | 10 | 0.476 | Parziale | No | Sì | 4 | 3 | 21.31 | 5474 | 882 | 0.00135 |
| ic11 | `gpt-4o-mini` | JSON + immagine + datasheet | 11 | 0.524 | Parziale | Sì | Sì | 4 | 3 | 44.04 | 31057 | 1056 | 0.00529 |
| ic11 | `gpt-4.1-mini` | JSON + datasheet | 15 | 0.714 | Parziale | Sì | Sì | 3 | 2 | 51.86 | 5474 | 2035 | 0.00545 |
| ic11 | `gpt-4.1-mini` | JSON + immagine + datasheet | 13 | 0.619 | Parziale | Sì | Sì | 4 | 4 | 37.68 | 7216 | 1821 | 0.00580 |
| ic11 | `gpt-4.1-nano` | JSON + datasheet | 8 | 0.381 | Parziale | Sì | Sì | 5 | 3 | 12.65 | 5474 | 1480 | 0.00114 |
| ic11 | `gpt-4.1-nano` | JSON + immagine + datasheet | 13 | 0.619 | Parziale | No | Sì | 3 | 3 | 15.63 | 8077 | 1381 | 0.00136 |
| ic11 | `gpt-5-nano` | JSON + datasheet | 13 | 0.619 | Parziale | No | Sì | 4 | 4 | 32.21 | 5473 | 3694 | 0.00175 |
| ic11 | `gpt-5-nano` | JSON + immagine + datasheet | 13 | 0.619 | Parziale | No | Sì | 4 | 3 | 27.57 | 7091 | 3482 | 0.00175 |
| ic11 | `gpt-5-mini` | JSON + datasheet | 17 | 0.809 | Parziale | Sì | Sì | 3 | 2 | 27.78 | 5473 | 3265 | 0.00790 |
| ic11 | `gpt-5-mini` | JSON + immagine + datasheet | 17 | 0.809 | Parziale | Sì | Sì | 2 | 2 | 22.15 | 6784 | 2737 | 0.00717 |
| ic11 | `gpt-5.4-nano` | JSON + datasheet | 15 | 0.714 | Parziale | Sì | Sì | 2 | 2 | 17.06 | 5473 | 2681 | 0.00445 |
| ic11 | `gpt-5.4-nano` | JSON + immagine + datasheet | 13 | 0.619 | Parziale | No | Sì | 3 | 2 | 17.09 | 6784 | 2392 | 0.00435 |
| ic11 | `gpt-5.4-mini` | JSON + datasheet | 16 | 0.762 | Parziale | Sì | Sì | 3 | 2 | 19.60 | 5473 | 2468 | 0.01521 |
| ic11 | `gpt-5.4-mini` | JSON + immagine + datasheet | 20 | 0.952 | Sì | Sì | Sì | 0 | 2 | 21.28 | 6784 | 2580 | 0.01670 |
| ic11 | `gpt-5.4` | JSON + datasheet | 17 | 0.810 | Parziale | No | Sì | 2 | 2 | 60.45 | 5473 | 3423 | 0.06503 |
| ic11 | `gpt-5.4` | JSON + immagine + datasheet | 21 | 1.000 | Sì | Sì | Sì | 0 | 0 | 61.31 | 6784 | 4054 | 0.07777 |

---

## 2. Confronto JSON-only vs JSON + immagine

| Modello | JSON + datasheet | JSON + immagine + datasheet | Delta immagine | Top-1 JSON | Top-1 JSON+img | Errori JSON | Errori JSON+img |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: |
| `gpt-4o-mini` | 10 | 11 | +1 | No | Sì | 4 | 4 |
| `gpt-4.1-mini` | 15 | 13 | -2 | Sì | Sì | 3 | 4 |
| `gpt-4.1-nano` | 8 | 13 | +5 | Sì | No | 5 | 3 |
| `gpt-5-nano` | 13 | 13 | +0 | No | No | 4 | 4 |
| `gpt-5-mini` | 17 | 17 | +0 | Sì | Sì | 3 | 2 |
| `gpt-5.4-nano` | 15 | 13 | -2 | Sì | No | 2 | 3 |
| `gpt-5.4-mini` | 16 | 20 | +4 | Sì | Sì | 3 | 0 |
| `gpt-5.4` | 17 | 21 | +4 | No | Sì | 2 | 0 |

---

## 3. Aggregazione per input type

| Input type | N | Score medio | Mediana | Std | Top-1 accuracy | Top-3 accuracy | Errori gravi medi | Allucinazioni medie | Latenza media modello (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| JSON + datasheet | 8 | 13.88 | 15.00 | 3.10 | 62.5% | 100.0% | 3.25 | 2.50 | 30.37 |
| JSON + immagine + datasheet | 8 | 15.12 | 13.00 | 3.48 | 62.5% | 100.0% | 2.50 | 2.38 | 30.84 |

---

## 4. Aggregazione per modello

| Modello | N | Score medio | Mediana | Std | Top-1 accuracy | Top-3 accuracy | Errori gravi medi | Allucinazioni medie | Costo medio modello ($) | Latenza media modello (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 2 | 10.50 | 10.50 | 0.50 | 50.0% | 100.0% | 4.00 | 3.00 | 0.00332 | 32.67 |
| `gpt-4.1-mini` | 2 | 14.00 | 14.00 | 1.00 | 100.0% | 100.0% | 3.50 | 3.00 | 0.00562 | 44.77 |
| `gpt-4.1-nano` | 2 | 10.50 | 10.50 | 2.50 | 50.0% | 100.0% | 4.00 | 3.00 | 0.00125 | 14.14 |
| `gpt-5-nano` | 2 | 13.00 | 13.00 | 0.00 | 0.0% | 100.0% | 4.00 | 3.50 | 0.00175 | 29.89 |
| `gpt-5-mini` | 2 | 17.00 | 17.00 | 0.00 | 100.0% | 100.0% | 2.50 | 2.00 | 0.00753 | 24.96 |
| `gpt-5.4-nano` | 2 | 14.00 | 14.00 | 1.00 | 50.0% | 100.0% | 2.50 | 2.00 | 0.00440 | 17.07 |
| `gpt-5.4-mini` | 2 | 18.00 | 18.00 | 2.00 | 100.0% | 100.0% | 1.50 | 2.00 | 0.01595 | 20.44 |
| `gpt-5.4` | 2 | 19.00 | 19.00 | 2.00 | 50.0% | 100.0% | 1.00 | 1.00 | 0.07140 | 60.88 |

---

## 5. Score medi per criterio e modello

| Modello | Comprensione circuito | Uso datasheet | Uso JSON/immagine | Accuratezza diagnostica | Priorità cause | Controlli pratici | Assenza allucinazioni |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 2.00 | 1.50 | 1.00 | 1.50 | 1.50 | 2.00 | 1.00 |
| `gpt-4.1-mini` | 2.00 | 2.00 | 2.00 | 2.00 | 1.50 | 3.00 | 1.50 |
| `gpt-4.1-nano` | 1.50 | 1.50 | 1.50 | 1.50 | 1.00 | 2.50 | 1.00 |
| `gpt-5-nano` | 2.00 | 2.00 | 2.00 | 2.00 | 1.00 | 3.00 | 1.00 |
| `gpt-5-mini` | 3.00 | 3.00 | 2.00 | 2.00 | 2.00 | 3.00 | 2.00 |
| `gpt-5.4-nano` | 2.00 | 2.50 | 1.50 | 2.00 | 1.50 | 3.00 | 1.50 |
| `gpt-5.4-mini` | 3.00 | 2.50 | 2.50 | 2.50 | 2.50 | 3.00 | 2.00 |
| `gpt-5.4` | 3.00 | 3.00 | 2.50 | 2.50 | 2.50 | 3.00 | 2.50 |

---

## 6. Token, costo e latenza del judge

| Modello | Input | Judge input tokens | Judge output tokens | Judge total tokens | Costo judge stimato ($) | Latenza judge (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | JSON + datasheet | 8178 | 1412 | 9590 | 0.0832 | 28.35 |
| `gpt-4o-mini` | JSON + immagine + datasheet | 8354 | 1715 | 10069 | 0.0932 | 37.71 |
| `gpt-4.1-mini` | JSON + datasheet | 9330 | 1511 | 10841 | 0.0920 | 33.50 |
| `gpt-4.1-mini` | JSON + immagine + datasheet | 9118 | 1649 | 10767 | 0.0951 | 33.94 |
| `gpt-4.1-nano` | JSON + datasheet | 8776 | 1546 | 10322 | 0.0903 | 30.87 |
| `gpt-4.1-nano` | JSON + immagine + datasheet | 8679 | 1523 | 10202 | 0.0891 | 30.92 |
| `gpt-5-nano` | JSON + datasheet | 10094 | 1658 | 11752 | 0.1002 | 31.93 |
| `gpt-5-nano` | JSON + immagine + datasheet | 9920 | 1947 | 11867 | 0.1080 | 41.84 |
| `gpt-5-mini` | JSON + datasheet | 9905 | 1575 | 11480 | 0.0968 | 33.34 |
| `gpt-5-mini` | JSON + immagine + datasheet | 9626 | 1458 | 11084 | 0.0919 | 30.68 |
| `gpt-5.4-nano` | JSON + datasheet | 9452 | 1714 | 11166 | 0.0987 | 34.68 |
| `gpt-5.4-nano` | JSON + immagine + datasheet | 9304 | 1663 | 10967 | 0.0964 | 33.47 |
| `gpt-5.4-mini` | JSON + datasheet | 9242 | 1538 | 10780 | 0.0924 | 32.34 |
| `gpt-5.4-mini` | JSON + immagine + datasheet | 9084 | 1420 | 10504 | 0.0880 | 30.69 |
| `gpt-5.4` | JSON + datasheet | 10197 | 1438 | 11635 | 0.0941 | 30.96 |
| `gpt-5.4` | JSON + immagine + datasheet | 10641 | 1080 | 11721 | 0.0856 | 20.02 |

---

## Nota sui costi

Il costo del modello rappresenta il costo operativo della diagnosi automatica, cioè quanto costerebbe eseguire il sistema di troubleshooting sul circuito.

Il costo del judge è riportato separatamente perché riguarda solo la fase di valutazione automatica offline e non farebbe parte del costo operativo del sistema finale.
