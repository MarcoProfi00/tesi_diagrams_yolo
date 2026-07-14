# Tabelle judge — ic13

File sorgente:

`ic13__judge_summary_gpt-5.5_20260518_112259.json`

## Sintesi rapida

- Esecuzioni valutate: **16**
- Score medio `JSON + datasheet`: **18.00 / 21**
- Score medio `JSON + immagine + datasheet`: **17.88 / 21**
- Delta medio dovuto all'immagine: **-0.12 punti**
- Miglior run: **`gpt-5.4`**, input **JSON + immagine + datasheet**, score **21 / 21**
- Peggior run: **`gpt-4o-mini`**, input **JSON + datasheet**, score **13 / 21**
- Costo judge stimato totale: **$1.26**

---

## 1. Risultati dettagliati per run

| Circuito | Modello | Input | Score / 21 | Score norm. | Verdict | Top-1 | Top-3 | Errori gravi | Allucinazioni | Latenza modello (s) | Input tokens | Output tokens | Costo modello ($) |
| --- | --- | --- | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ic13 | `gpt-4o-mini` | JSON + datasheet | 13 | 0.619 | Parziale | No | Sì | 3 | 2 | 24.04 | 5082 | 901 | 0.00130 |
| ic13 | `gpt-4o-mini` | JSON + immagine + datasheet | 15 | 0.714 | Parziale | No | Sì | 2 | 2 | 18.40 | 30665 | 944 | 0.00517 |
| ic13 | `gpt-4.1-mini` | JSON + datasheet | 20 | 0.952 | Sì | Sì | Sì | 0 | 2 | 45.23 | 5082 | 1908 | 0.00509 |
| ic13 | `gpt-4.1-mini` | JSON + immagine + datasheet | 19 | 0.905 | Sì | Sì | Sì | 2 | 2 | 27.13 | 6824 | 1979 | 0.00590 |
| ic13 | `gpt-4.1-nano` | JSON + datasheet | 13 | 0.619 | Parziale | No | Sì | 3 | 2 | 12.96 | 5082 | 1596 | 0.00115 |
| ic13 | `gpt-4.1-nano` | JSON + immagine + datasheet | 15 | 0.714 | Parziale | No | Sì | 2 | 2 | 7.44 | 7685 | 1151 | 0.00123 |
| ic13 | `gpt-5-nano` | JSON + datasheet | 18 | 0.857 | Sì | Sì | Sì | 2 | 3 | 24.83 | 5081 | 3695 | 0.00173 |
| ic13 | `gpt-5-nano` | JSON + immagine + datasheet | 16 | 0.762 | Parziale | No | Sì | 3 | 3 | 24.61 | 6699 | 4153 | 0.00200 |
| ic13 | `gpt-5-mini` | JSON + datasheet | 20 | 0.952 | Sì | Sì | Sì | 0 | 2 | 53.67 | 5081 | 2955 | 0.00718 |
| ic13 | `gpt-5-mini` | JSON + immagine + datasheet | 18 | 0.857 | Parziale | No | Sì | 1 | 2 | 42.36 | 6392 | 2937 | 0.00747 |
| ic13 | `gpt-5.4-nano` | JSON + datasheet | 20 | 0.952 | Sì | Sì | Sì | 0 | 3 | 22.30 | 5081 | 3009 | 0.00478 |
| ic13 | `gpt-5.4-nano` | JSON + immagine + datasheet | 19 | 0.905 | Sì | Sì | Sì | 2 | 3 | 17.58 | 6392 | 2260 | 0.00410 |
| ic13 | `gpt-5.4-mini` | JSON + datasheet | 20 | 0.952 | Sì | Sì | Sì | 0 | 1 | 14.81 | 5081 | 2108 | 0.01330 |
| ic13 | `gpt-5.4-mini` | JSON + immagine + datasheet | 20 | 0.952 | Sì | Sì | Sì | 0 | 2 | 16.93 | 6392 | 2029 | 0.01392 |
| ic13 | `gpt-5.4` | JSON + datasheet | 20 | 0.952 | Sì | Sì | Sì | 0 | 1 | 47.72 | 5081 | 2778 | 0.05437 |
| ic13 | `gpt-5.4` | JSON + immagine + datasheet | 21 | 1.000 | Sì | Sì | Sì | 0 | 0 | 49.10 | 6392 | 3305 | 0.06556 |

---

## 2. Confronto JSON-only vs JSON + immagine

| Modello | JSON + datasheet | JSON + immagine + datasheet | Delta immagine | Top-1 JSON | Top-1 JSON+img | Errori JSON | Errori JSON+img |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: |
| `gpt-4o-mini` | 13 | 15 | +2 | No | No | 3 | 2 |
| `gpt-4.1-mini` | 20 | 19 | -1 | Sì | Sì | 0 | 2 |
| `gpt-4.1-nano` | 13 | 15 | +2 | No | No | 3 | 2 |
| `gpt-5-nano` | 18 | 16 | -2 | Sì | No | 2 | 3 |
| `gpt-5-mini` | 20 | 18 | -2 | Sì | No | 0 | 1 |
| `gpt-5.4-nano` | 20 | 19 | -1 | Sì | Sì | 0 | 2 |
| `gpt-5.4-mini` | 20 | 20 | +0 | Sì | Sì | 0 | 0 |
| `gpt-5.4` | 20 | 21 | +1 | Sì | Sì | 0 | 0 |

---

## 3. Aggregazione per input type

| Input type | N | Score medio | Mediana | Std | Top-1 accuracy | Top-3 accuracy | Errori gravi medi | Allucinazioni medie | Latenza media modello (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| JSON + datasheet | 8 | 18.00 | 20.00 | 2.96 | 75.0% | 100.0% | 1.00 | 2.00 | 30.69 |
| JSON + immagine + datasheet | 8 | 17.88 | 18.50 | 2.15 | 50.0% | 100.0% | 1.50 | 2.00 | 25.44 |

---

## 4. Aggregazione per modello

| Modello | N | Score medio | Mediana | Std | Top-1 accuracy | Top-3 accuracy | Errori gravi medi | Allucinazioni medie | Costo medio modello ($) | Latenza media modello (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 2 | 14.00 | 14.00 | 1.00 | 0.0% | 100.0% | 2.50 | 2.00 | 0.00323 | 21.22 |
| `gpt-4.1-mini` | 2 | 19.50 | 19.50 | 0.50 | 100.0% | 100.0% | 1.00 | 2.00 | 0.00549 | 36.18 |
| `gpt-4.1-nano` | 2 | 14.00 | 14.00 | 1.00 | 0.0% | 100.0% | 2.50 | 2.00 | 0.00119 | 10.20 |
| `gpt-5-nano` | 2 | 17.00 | 17.00 | 1.00 | 50.0% | 100.0% | 2.50 | 3.00 | 0.00186 | 24.72 |
| `gpt-5-mini` | 2 | 19.00 | 19.00 | 1.00 | 50.0% | 100.0% | 0.50 | 2.00 | 0.00733 | 48.01 |
| `gpt-5.4-nano` | 2 | 19.50 | 19.50 | 0.50 | 100.0% | 100.0% | 1.00 | 3.00 | 0.00444 | 19.94 |
| `gpt-5.4-mini` | 2 | 20.00 | 20.00 | 0.00 | 100.0% | 100.0% | 0.00 | 1.50 | 0.01361 | 15.87 |
| `gpt-5.4` | 2 | 20.50 | 20.50 | 0.50 | 100.0% | 100.0% | 0.00 | 0.50 | 0.05996 | 48.41 |

---

## 5. Score medi per criterio e modello

| Modello | Comprensione circuito | Uso datasheet | Uso JSON/immagine | Accuratezza diagnostica | Priorità cause | Controlli pratici | Assenza allucinazioni |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 2.50 | 2.50 | 1.50 | 2.00 | 1.00 | 2.50 | 2.00 |
| `gpt-4.1-mini` | 3.00 | 2.50 | 3.00 | 3.00 | 3.00 | 3.00 | 2.00 |
| `gpt-4.1-nano` | 3.00 | 2.00 | 1.50 | 2.00 | 1.00 | 3.00 | 1.50 |
| `gpt-5-nano` | 2.50 | 2.50 | 2.00 | 2.50 | 2.50 | 3.00 | 2.00 |
| `gpt-5-mini` | 3.00 | 3.00 | 3.00 | 2.50 | 2.50 | 3.00 | 2.00 |
| `gpt-5.4-nano` | 3.00 | 3.00 | 2.50 | 3.00 | 3.00 | 3.00 | 2.00 |
| `gpt-5.4-mini` | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 2.00 |
| `gpt-5.4` | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 2.50 |

---

## 6. Token, costo e latenza del judge

| Modello | Input | Judge input tokens | Judge output tokens | Judge total tokens | Costo judge stimato ($) | Latenza judge (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | JSON + datasheet | 7804 | 1065 | 8869 | 0.0710 | 22.84 |
| `gpt-4o-mini` | JSON + immagine + datasheet | 7850 | 1190 | 9040 | 0.0749 | 23.29 |
| `gpt-4.1-mini` | JSON + datasheet | 8811 | 918 | 9729 | 0.0716 | 17.09 |
| `gpt-4.1-mini` | JSON + immagine + datasheet | 8884 | 1266 | 10150 | 0.0824 | 23.30 |
| `gpt-4.1-nano` | JSON + datasheet | 8499 | 1336 | 9835 | 0.0826 | 24.48 |
| `gpt-4.1-nano` | JSON + immagine + datasheet | 8057 | 1156 | 9213 | 0.0750 | 21.24 |
| `gpt-5-nano` | JSON + datasheet | 10022 | 1162 | 11184 | 0.0850 | 22.10 |
| `gpt-5-nano` | JSON + immagine + datasheet | 10353 | 1430 | 11783 | 0.0947 | 29.52 |
| `gpt-5-mini` | JSON + datasheet | 9119 | 891 | 10010 | 0.0723 | 17.70 |
| `gpt-5-mini` | JSON + immagine + datasheet | 9413 | 1224 | 10637 | 0.0838 | 23.96 |
| `gpt-5.4-nano` | JSON + datasheet | 9325 | 853 | 10178 | 0.0722 | 16.92 |
| `gpt-5.4-nano` | JSON + immagine + datasheet | 8975 | 1556 | 10531 | 0.0916 | 31.06 |
| `gpt-5.4-mini` | JSON + datasheet | 8766 | 1073 | 9839 | 0.0760 | 20.73 |
| `gpt-5.4-mini` | JSON + immagine + datasheet | 8595 | 1175 | 9770 | 0.0782 | 23.99 |
| `gpt-5.4` | JSON + datasheet | 8776 | 1049 | 9825 | 0.0754 | 21.52 |
| `gpt-5.4` | JSON + immagine + datasheet | 9977 | 827 | 10804 | 0.0747 | 15.47 |

---

## Nota sui costi

Il costo del modello rappresenta il costo operativo della diagnosi automatica, cioè quanto costerebbe eseguire il sistema di troubleshooting sul circuito.

Il costo del judge è riportato separatamente perché riguarda solo la fase di valutazione automatica offline e non farebbe parte del costo operativo del sistema finale.
