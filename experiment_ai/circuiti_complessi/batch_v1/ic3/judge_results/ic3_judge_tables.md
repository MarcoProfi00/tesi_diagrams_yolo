# Tabelle judge — ic3

File sorgente:

`ic3__judge_summary_gpt-5.5_20260514_170259.json`

## Sintesi rapida

- Esecuzioni valutate: **16**
- Score medio `JSON + datasheet`: **18.75 / 21**
- Score medio `JSON + immagine + datasheet`: **19.12 / 21**
- Delta medio dovuto all'immagine: **+0.38 punti**
- Miglior run: **`gpt-5-mini`**, input **JSON + immagine + datasheet**, score **21 / 21**
- Peggior run: **`gpt-4o-mini`**, input **JSON + immagine + datasheet**, score **16 / 21**
- Costo judge stimato totale: **$1.32**

---

## 1. Risultati dettagliati per run

| Circuito | Modello | Input | Score / 21 | Score norm. | Verdict | Top-1 | Top-3 | Errori gravi | Allucinazioni | Latenza modello (s) | Input tokens | Output tokens | Costo modello ($) |
| --- | --- | --- | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ic3 | `gpt-4o-mini` | JSON + datasheet | 18 | 0.857 | Sì | Sì | Sì | 3 | 1 | 27.70 | 5703 | 1140 | 0.00154 |
| ic3 | `gpt-4o-mini` | JSON + immagine + datasheet | 16 | 0.762 | Parziale | No | Sì | 2 | 0 | 30.73 | 31286 | 1003 | 0.00529 |
| ic3 | `gpt-4.1-mini` | JSON + datasheet | 19 | 0.905 | Sì | Sì | Sì | 1 | 2 | 29.18 | 5703 | 1736 | 0.00506 |
| ic3 | `gpt-4.1-mini` | JSON + immagine + datasheet | 19 | 0.905 | Sì | Sì | Sì | 0 | 3 | 28.35 | 7445 | 1690 | 0.00568 |
| ic3 | `gpt-4.1-nano` | JSON + datasheet | 19 | 0.905 | Sì | Sì | Sì | 0 | 2 | 23.97 | 5703 | 1675 | 0.00124 |
| ic3 | `gpt-4.1-nano` | JSON + immagine + datasheet | 19 | 0.905 | Sì | Sì | Sì | 1 | 2 | 27.25 | 8306 | 1433 | 0.00140 |
| ic3 | `gpt-5-nano` | JSON + datasheet | 19 | 0.905 | Sì | Sì | Sì | 2 | 2 | 32.55 | 5702 | 4100 | 0.00193 |
| ic3 | `gpt-5-nano` | JSON + immagine + datasheet | 19 | 0.905 | Sì | Sì | Sì | 0 | 4 | 31.66 | 7320 | 3805 | 0.00189 |
| ic3 | `gpt-5-mini` | JSON + datasheet | 20 | 0.952 | Sì | Sì | Sì | 0 | 2 | 48.71 | 5702 | 3062 | 0.00755 |
| ic3 | `gpt-5-mini` | JSON + immagine + datasheet | 21 | 1.000 | Sì | Sì | Sì | 0 | 0 | 42.64 | 7013 | 2517 | 0.00679 |
| ic3 | `gpt-5.4-nano` | JSON + datasheet | 17 | 0.809 | Sì | Sì | Sì | 2 | 1 | 31.34 | 5702 | 2713 | 0.00453 |
| ic3 | `gpt-5.4-nano` | JSON + immagine + datasheet | 18 | 0.857 | Sì | Sì | Sì | 2 | 2 | 22.96 | 7013 | 2900 | 0.00503 |
| ic3 | `gpt-5.4-mini` | JSON + datasheet | 20 | 0.952 | Sì | Sì | Sì | 0 | 1 | 16.13 | 5702 | 1981 | 0.01319 |
| ic3 | `gpt-5.4-mini` | JSON + immagine + datasheet | 21 | 1.000 | Sì | Sì | Sì | 0 | 0 | 12.92 | 7013 | 1755 | 0.01316 |
| ic3 | `gpt-5.4` | JSON + datasheet | 18 | 0.857 | Sì | Sì | Sì | 2 | 0 | 43.79 | 5702 | 3006 | 0.05934 |
| ic3 | `gpt-5.4` | JSON + immagine + datasheet | 20 | 0.952 | Sì | Sì | Sì | 0 | 1 | 58.56 | 7013 | 3205 | 0.06561 |

---

## 2. Confronto JSON-only vs JSON + immagine

| Modello | JSON + datasheet | JSON + immagine + datasheet | Delta immagine | Top-1 JSON | Top-1 JSON+img | Errori JSON | Errori JSON+img |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: |
| `gpt-4o-mini` | 18 | 16 | -2 | Sì | No | 3 | 2 |
| `gpt-4.1-mini` | 19 | 19 | +0 | Sì | Sì | 1 | 0 |
| `gpt-4.1-nano` | 19 | 19 | +0 | Sì | Sì | 0 | 1 |
| `gpt-5-nano` | 19 | 19 | +0 | Sì | Sì | 2 | 0 |
| `gpt-5-mini` | 20 | 21 | +1 | Sì | Sì | 0 | 0 |
| `gpt-5.4-nano` | 17 | 18 | +1 | Sì | Sì | 2 | 2 |
| `gpt-5.4-mini` | 20 | 21 | +1 | Sì | Sì | 0 | 0 |
| `gpt-5.4` | 18 | 20 | +2 | Sì | Sì | 2 | 0 |

---

## 3. Aggregazione per input type

| Input type | N | Score medio | Mediana | Std | Top-1 accuracy | Top-3 accuracy | Errori gravi medi | Allucinazioni medie | Latenza media modello (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| JSON + datasheet | 8 | 18.75 | 19.00 | 0.97 | 100.0% | 100.0% | 1.25 | 1.38 | 31.67 |
| JSON + immagine + datasheet | 8 | 19.12 | 19.00 | 1.54 | 87.5% | 100.0% | 0.62 | 1.50 | 31.88 |

---

## 4. Aggregazione per modello

| Modello | N | Score medio | Mediana | Std | Top-1 accuracy | Top-3 accuracy | Errori gravi medi | Allucinazioni medie | Costo medio modello ($) | Latenza media modello (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 2 | 17.00 | 17.00 | 1.00 | 50.0% | 100.0% | 2.50 | 0.50 | 0.00342 | 29.21 |
| `gpt-4.1-mini` | 2 | 19.00 | 19.00 | 0.00 | 100.0% | 100.0% | 0.50 | 2.50 | 0.00537 | 28.77 |
| `gpt-4.1-nano` | 2 | 19.00 | 19.00 | 0.00 | 100.0% | 100.0% | 0.50 | 2.00 | 0.00132 | 25.61 |
| `gpt-5-nano` | 2 | 19.00 | 19.00 | 0.00 | 100.0% | 100.0% | 1.00 | 3.00 | 0.00191 | 32.11 |
| `gpt-5-mini` | 2 | 20.50 | 20.50 | 0.50 | 100.0% | 100.0% | 0.00 | 1.00 | 0.00717 | 45.67 |
| `gpt-5.4-nano` | 2 | 17.50 | 17.50 | 0.50 | 100.0% | 100.0% | 2.00 | 1.50 | 0.00478 | 27.15 |
| `gpt-5.4-mini` | 2 | 20.50 | 20.50 | 0.50 | 100.0% | 100.0% | 0.00 | 0.50 | 0.01317 | 14.52 |
| `gpt-5.4` | 2 | 19.00 | 19.00 | 1.00 | 100.0% | 100.0% | 1.00 | 0.50 | 0.06248 | 51.18 |

---

## 5. Score medi per criterio e modello

| Modello | Comprensione circuito | Uso datasheet | Uso JSON/immagine | Accuratezza diagnostica | Priorità cause | Controlli pratici | Assenza allucinazioni |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 3.00 | 3.00 | 1.50 | 2.50 | 1.50 | 3.00 | 2.50 |
| `gpt-4.1-mini` | 3.00 | 3.00 | 2.00 | 3.00 | 3.00 | 3.00 | 2.00 |
| `gpt-4.1-nano` | 3.00 | 3.00 | 2.00 | 3.00 | 3.00 | 3.00 | 2.00 |
| `gpt-5-nano` | 3.00 | 3.00 | 2.00 | 3.00 | 3.00 | 3.00 | 2.00 |
| `gpt-5-mini` | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 2.50 |
| `gpt-5.4-nano` | 3.00 | 3.00 | 2.00 | 2.00 | 2.50 | 3.00 | 2.00 |
| `gpt-5.4-mini` | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 2.50 |
| `gpt-5.4` | 3.00 | 3.00 | 2.50 | 2.50 | 3.00 | 3.00 | 2.00 |

---

## 6. Token, costo e latenza del judge

| Modello | Input | Judge input tokens | Judge output tokens | Judge total tokens | Costo judge stimato ($) | Latenza judge (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | JSON + datasheet | 8664 | 1363 | 10027 | 0.0842 | 24.56 |
| `gpt-4o-mini` | JSON + immagine + datasheet | 8530 | 1101 | 9631 | 0.0757 | 17.79 |
| `gpt-4.1-mini` | JSON + datasheet | 9260 | 1278 | 10538 | 0.0846 | 23.78 |
| `gpt-4.1-mini` | JSON + immagine + datasheet | 9217 | 1105 | 10322 | 0.0792 | 16.67 |
| `gpt-4.1-nano` | JSON + datasheet | 9199 | 1209 | 10408 | 0.0823 | 20.09 |
| `gpt-4.1-nano` | JSON + immagine + datasheet | 8960 | 1051 | 10011 | 0.0763 | 18.21 |
| `gpt-5-nano` | JSON + datasheet | 10995 | 1401 | 12396 | 0.0970 | 23.70 |
| `gpt-5-nano` | JSON + immagine + datasheet | 10631 | 1118 | 11749 | 0.0867 | 18.58 |
| `gpt-5-mini` | JSON + datasheet | 9545 | 1231 | 10776 | 0.0847 | 21.09 |
| `gpt-5-mini` | JSON + immagine + datasheet | 9638 | 924 | 10562 | 0.0759 | 16.77 |
| `gpt-5.4-nano` | JSON + datasheet | 9659 | 1432 | 11091 | 0.0913 | 26.07 |
| `gpt-5.4-nano` | JSON + immagine + datasheet | 10012 | 1081 | 11093 | 0.0825 | 18.04 |
| `gpt-5.4-mini` | JSON + datasheet | 9202 | 1116 | 10318 | 0.0795 | 18.50 |
| `gpt-5.4-mini` | JSON + immagine + datasheet | 8926 | 793 | 9719 | 0.0684 | 15.55 |
| `gpt-5.4` | JSON + datasheet | 10032 | 1327 | 11359 | 0.0900 | 24.30 |
| `gpt-5.4` | JSON + immagine + datasheet | 10390 | 910 | 11300 | 0.0793 | 15.07 |

---

## Nota sui costi

Il costo del modello rappresenta il costo operativo della diagnosi automatica, cioè quanto costerebbe eseguire il sistema di troubleshooting sul circuito.

Il costo del judge è riportato separatamente perché riguarda solo la fase di valutazione automatica offline e non farebbe parte del costo operativo del sistema finale.
