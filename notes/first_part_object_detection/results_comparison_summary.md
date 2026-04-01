# Confronto globale tra famiglie YOLO

## Obiettivo

Questo documento raccoglie **solo le tabelle di confronto** tra tutti gli esperimenti completati, separandole dai file descrittivi delle singole famiglie di modelli.

---

# 1. Tabella master di tutti gli esperimenti completati

| Exp ID | Modello | Input     | Augmentation   | Img Size | Epochs | Batch | Precision | Recall | F1-score | mAP@0.5 | mAP@0.5:0.95 | Best epoch | Stato      | Note                 |
| ------ | ------- | --------- | -------------- | -------: | -----: | ----: | --------: | -----: | -------: | ------: | -----------: | ---------: | ---------- | -------------------- |
| exp01  | YOLOv7  | RGB       | No             |     1024 |    100 |     4 |    0.8945 | 0.7935 |   0.8410 |  0.8245 |       0.5702 |         87 | Completato | Baseline RGB         |
| exp02  | YOLOv7  | Grayscale | No             |     1024 |    100 |     4 |    0.8864 | 0.7657 |   0.8216 |  0.8272 |       0.5765 |         93 | Completato | Grayscale            |
| exp03  | YOLOv7  | RGB       | aug_v1         |     1024 |    100 |     4 |    0.8791 | 0.8563 |   0.8676 |  0.8836 |       0.5928 |         69 | Completato | Augmentation leggera |
| exp04  | YOLOv7  | RGB       | aug_v2_compose |     1024 |    100 |     4 |    0.8443 | 0.8481 |   0.8462 |  0.8587 |       0.5832 |         74 | Completato | Compose              |
| exp03b | YOLOv7  | RGB       | aug_v3 strong  |     1024 |    100 |     4 |    0.8568 | 0.8854 |   0.8709 |  0.8972 |       0.6059 |         97 | Completato | Augmentation strong  |
| exp05  | YOLOv8  | RGB       | No             |     1024 |    100 |     4 |    0.8846 | 0.8167 |   0.8493 |  0.8553 |       0.5856 |         80 | Completato | Baseline RGB         |
| exp06  | YOLOv8  | Grayscale | No             |     1024 |    100 |     4 |    0.8554 | 0.8279 |   0.8414 |  0.8759 |       0.6011 |         58 | Completato | Grayscale            |
| exp07  | YOLOv8  | RGB       | aug_v1         |     1024 |    100 |     4 |    0.8281 | 0.8445 |   0.8362 |  0.8878 |       0.5953 |         43 | Completato | Augmentation leggera |
| exp08  | YOLOv8  | RGB       | aug_v2_compose |     1024 |    100 |     4 |    0.8502 | 0.8581 |   0.8541 |  0.8734 |       0.5984 |         77 | Completato | Compose              |
| exp07b | YOLOv8  | RGB       | aug_v3_strong  |     1024 |    100 |     4 |    0.8866 | 0.8200 |   0.8518 |  0.8660 |       0.5877 |       n.d. | Completato | Augmentation strong  |
| exp09  | YOLOv11 | RGB       | No             |     1024 |    100 |     4 |    0.9062 | 0.8806 |   0.8932 |  0.9114 |       0.6472 |         70 | Completato | Baseline RGB         |
| exp10  | YOLOv11 | Grayscale | No             |     1024 |    100 |     4 |    0.9387 | 0.8571 |   0.8960 |  0.9300 |       0.6492 |         78 | Completato | Grayscale            |
| exp11  | YOLOv11 | RGB       | aug_v1         |     1024 |    100 |     4 |    0.9436 | 0.9004 |   0.9215 |  0.9513 |       0.6552 |         63 | Completato | Augmentation lieve   |
| exp12  | YOLOv11 | RGB       | aug_v2_compose |     1024 |    100 |     4 |    0.9201 | 0.8389 |   0.8776 |  0.9146 |       0.6442 |         34 | Completato | Compose of diagrams  |
| exp11b | YOLOv11 | RGB       | aug_v3 strong  |     1024 |    100 |     4 |    0.9404 | 0.9049 |   0.9223 |  0.9476 |       0.6665 |         97 | Completato | Augmentation forte   |

---

# 2. Ranking globale per metrica

## Precision

| Rank | Exp ID | Modello                      | Valore |
| ---- | ------ | ---------------------------- | ------ |
| 1    | exp11  | YOLOv11 RGB + aug_v1         | 0.9436 |
| 2    | exp11b | YOLOv11 RGB + aug_v3 strong  | 0.9404 |
| 3    | exp10  | YOLOv11 grayscale            | 0.9387 |
| 4    | exp12  | YOLOv11 RGB + aug_v2_compose | 0.9201 |
| 5    | exp09  | YOLOv11 RGB baseline         | 0.9062 |
| 6    | exp01  | YOLOv7 RGB baseline          | 0.8945 |
| 7    | exp07b | YOLOv8 RGB + aug_v3 strong   | 0.8866 |
| 8    | exp02  | YOLOv7 grayscale             | 0.8864 |
| 9    | exp05  | YOLOv8 RGB baseline          | 0.8846 |
| 10   | exp03  | YOLOv7 RGB + aug_v1          | 0.8791 |
| 11   | exp03b | YOLOv7 RGB + aug_v3 strong   | 0.8568 |
| 12   | exp06  | YOLOv8 grayscale             | 0.8554 |
| 13   | exp08  | YOLOv8 RGB + aug_v2_compose  | 0.8502 |
| 14   | exp04  | YOLOv7 RGB + aug_v2_compose  | 0.8443 |
| 15   | exp07  | YOLOv8 RGB + aug_v1          | 0.8281 |

## Recall

| Rank | Exp ID | Modello                      | Valore |
| ---- | ------ | ---------------------------- | ------ |
| 1    | exp11b | YOLOv11 RGB + aug_v3 strong  | 0.9049 |
| 2    | exp11  | YOLOv11 RGB + aug_v1         | 0.9004 |
| 3    | exp03b | YOLOv7 RGB + aug_v3 strong   | 0.8854 |
| 4    | exp09  | YOLOv11 RGB baseline         | 0.8806 |
| 5    | exp08  | YOLOv8 RGB + aug_v2_compose  | 0.8581 |
| 6    | exp10  | YOLOv11 grayscale            | 0.8571 |
| 7    | exp03  | YOLOv7 RGB + aug_v1          | 0.8563 |
| 8    | exp04  | YOLOv7 RGB + aug_v2_compose  | 0.8481 |
| 9    | exp07  | YOLOv8 RGB + aug_v1          | 0.8445 |
| 10   | exp12  | YOLOv11 RGB + aug_v2_compose | 0.8389 |
| 11   | exp06  | YOLOv8 grayscale             | 0.8279 |
| 12   | exp07b | YOLOv8 RGB + aug_v3 strong   | 0.8200 |
| 13   | exp05  | YOLOv8 RGB baseline          | 0.8167 |
| 14   | exp01  | YOLOv7 RGB baseline          | 0.7935 |
| 15   | exp02  | YOLOv7 grayscale             | 0.7657 |

## F1-score

| Rank | Exp ID | Modello                      | Valore |
| ---- | ------ | ---------------------------- | ------ |
| 1    | exp11b | YOLOv11 RGB + aug_v3 strong  | 0.9223 |
| 2    | exp11  | YOLOv11 RGB + aug_v1         | 0.9215 |
| 3    | exp10  | YOLOv11 grayscale            | 0.8960 |
| 4    | exp09  | YOLOv11 RGB baseline         | 0.8932 |
| 5    | exp12  | YOLOv11 RGB + aug_v2_compose | 0.8776 |
| 6    | exp03b | YOLOv7 RGB + aug_v3 strong   | 0.8709 |
| 7    | exp03  | YOLOv7 RGB + aug_v1          | 0.8676 |
| 8    | exp08  | YOLOv8 RGB + aug_v2_compose  | 0.8541 |
| 9    | exp07b | YOLOv8 RGB + aug_v3 strong   | 0.8518 |
| 10   | exp05  | YOLOv8 RGB baseline          | 0.8493 |
| 11   | exp04  | YOLOv7 RGB + aug_v2_compose  | 0.8462 |
| 12   | exp06  | YOLOv8 grayscale             | 0.8414 |
| 13   | exp01  | YOLOv7 RGB baseline          | 0.8410 |
| 14   | exp07  | YOLOv8 RGB + aug_v1          | 0.8362 |
| 15   | exp02  | YOLOv7 grayscale             | 0.8216 |

## mAP@0.5

| Rank | Exp ID | Modello                      | Valore |
| ---- | ------ | ---------------------------- | ------ |
| 1    | exp11  | YOLOv11 RGB + aug_v1         | 0.9513 |
| 2    | exp11b | YOLOv11 RGB + aug_v3 strong  | 0.9476 |
| 3    | exp10  | YOLOv11 grayscale            | 0.9300 |
| 4    | exp12  | YOLOv11 RGB + aug_v2_compose | 0.9146 |
| 5    | exp09  | YOLOv11 RGB baseline         | 0.9114 |
| 6    | exp03b | YOLOv7 RGB + aug_v3 strong   | 0.8972 |
| 7    | exp07  | YOLOv8 RGB + aug_v1          | 0.8878 |
| 8    | exp03  | YOLOv7 RGB + aug_v1          | 0.8836 |
| 9    | exp06  | YOLOv8 grayscale             | 0.8759 |
| 10   | exp08  | YOLOv8 RGB + aug_v2_compose  | 0.8734 |
| 11   | exp07b | YOLOv8 RGB + aug_v3 strong   | 0.8660 |
| 12   | exp04  | YOLOv7 RGB + aug_v2_compose  | 0.8587 |
| 13   | exp05  | YOLOv8 RGB baseline          | 0.8553 |
| 14   | exp02  | YOLOv7 grayscale             | 0.8272 |
| 15   | exp01  | YOLOv7 RGB baseline          | 0.8245 |

## mAP@0.5:0.95

| Rank | Exp ID | Modello                      | Valore |
| ---- | ------ | ---------------------------- | ------ |
| 1    | exp11b | YOLOv11 RGB + aug_v3 strong  | 0.6665 |
| 2    | exp11  | YOLOv11 RGB + aug_v1         | 0.6552 |
| 3    | exp10  | YOLOv11 grayscale            | 0.6492 |
| 4    | exp09  | YOLOv11 RGB baseline         | 0.6472 |
| 5    | exp12  | YOLOv11 RGB + aug_v2_compose | 0.6442 |
| 6    | exp03b | YOLOv7 RGB + aug_v3 strong   | 0.6059 |
| 7    | exp06  | YOLOv8 grayscale             | 0.6011 |
| 8    | exp08  | YOLOv8 RGB + aug_v2_compose  | 0.5984 |
| 9    | exp07  | YOLOv8 RGB + aug_v1          | 0.5953 |
| 10   | exp03  | YOLOv7 RGB + aug_v1          | 0.5928 |
| 11   | exp07b | YOLOv8 RGB + aug_v3 strong   | 0.5877 |
| 12   | exp05  | YOLOv8 RGB baseline          | 0.5856 |
| 13   | exp04  | YOLOv7 RGB + aug_v2_compose  | 0.5832 |
| 14   | exp02  | YOLOv7 grayscale             | 0.5765 |
| 15   | exp01  | YOLOv7 RGB baseline          | 0.5702 |

---

# 3. Migliore configurazione per famiglia

| Famiglia | Miglior precision | Miglior recall | Miglior F1-score | Miglior mAP@0.5 | Miglior mAP@0.5:0.95 |
| -------- | ----------------- | -------------- | ---------------- | --------------- | -------------------- |
| YOLOv7   | exp01             | exp03b         | exp03b           | exp03b          | exp03b               |
| YOLOv8   | exp07b            | exp08          | exp08            | exp07           | exp06                |
| YOLOv11  | exp11             | exp11b         | exp11b           | exp11           | exp11b               |

---

# 4. Confronti chiave

## 4.1 Baseline RGB: YOLOv7 vs YOLOv8 vs YOLOv11

| Metrica      | YOLOv7 RGB | YOLOv8 RGB | YOLOv11 RGB |
| ------------ | ---------- | ---------- | ----------- |
| Precision    | 0.8945     | 0.8846     | 0.9062      |
| Recall       | 0.7935     | 0.8167     | 0.8806      |
| F1-score     | 0.8410     | 0.8493     | 0.8932      |
| mAP@0.5      | 0.8245     | 0.8553     | 0.9114      |
| mAP@0.5:0.95 | 0.5702     | 0.5856     | 0.6472      |

## 4.2 Grayscale: YOLOv7 vs YOLOv8 vs YOLOv11

| Metrica      | YOLOv7 Gray | YOLOv8 Gray | YOLOv11 Gray |
| ------------ | ----------- | ----------- | ------------ |
| Precision    | 0.8864      | 0.8554      | 0.9387       |
| Recall       | 0.7657      | 0.8279      | 0.8571       |
| F1-score     | 0.8216      | 0.8414      | 0.8960       |
| mAP@0.5      | 0.8272      | 0.8759      | 0.9300       |
| mAP@0.5:0.95 | 0.5765      | 0.6011      | 0.6492       |

## 4.3 Augmentation leggera (`aug_v1`): YOLOv7 vs YOLOv8 vs YOLOv11

| Metrica      | YOLOv7 aug_v1 | YOLOv8 aug_v1 | YOLOv11 aug_v1 |
| ------------ | ------------- | ------------- | -------------- |
| Precision    | 0.8791        | 0.8281        | 0.9436         |
| Recall       | 0.8563        | 0.8445        | 0.9004         |
| F1-score     | 0.8676        | 0.8362        | 0.9215         |
| mAP@0.5      | 0.8836        | 0.8878        | 0.9513         |
| mAP@0.5:0.95 | 0.5928        | 0.5953        | 0.6552         |

## 4.4 Augmentation compose (`aug_v2_compose`): YOLOv7 vs YOLOv8 vs YOLOv11

| Metrica      | YOLOv7 aug_v2_compose | YOLOv8 aug_v2_compose | YOLOv11 aug_v2_compose |
| ------------ | --------------------- | --------------------- | ---------------------- |
| Precision    | 0.8443                | 0.8502                | 0.9201                 |
| Recall       | 0.8481                | 0.8581                | 0.8389                 |
| F1-score     | 0.8462                | 0.8541                | 0.8776                 |
| mAP@0.5      | 0.8587                | 0.8734                | 0.9146                 |
| mAP@0.5:0.95 | 0.5832                | 0.5984                | 0.6442                 |

## 4.5 Augmentation strong (`aug_v3 strong`): YOLOv7 vs YOLOv8 vs YOLOv11

| Metrica      | YOLOv7 aug_v3 strong | YOLOv8 aug_v3 strong | YOLOv11 aug_v3 strong |
| ------------ | -------------------- | -------------------- | --------------------- |
| Precision    | 0.8568               | 0.8866               | 0.9404                |
| Recall       | 0.8854               | 0.8200               | 0.9049                |
| F1-score     | 0.8709               | 0.8518               | 0.9223                |
| mAP@0.5      | 0.8972               | 0.8660               | 0.9476                |
| mAP@0.5:0.95 | 0.6059               | 0.5877               | 0.6665                |

## 4.6 Migliori configurazioni operative per famiglia a confronto

| Metrica      | YOLOv7 best family (exp03b) | YOLOv8 best family (exp08) | YOLOv11 best family (exp11b) |
| ------------ | --------------------------- | -------------------------- | ---------------------------- |
| Precision    | 0.8568                      | 0.8502                     | 0.9404                       |
| Recall       | 0.8854                      | 0.8581                     | 0.9049                       |
| F1-score     | 0.8709                      | 0.8541                     | 0.9223                       |
| mAP@0.5      | 0.8972                      | 0.8734                     | 0.9476                       |
| mAP@0.5:0.95 | 0.6059                      | 0.5984                     | 0.6665                       |

### Lettura sintetica

- **YOLOv7** resta competitivo soprattutto con `exp03b`, che massimizza **recall**, **F1-score**, **mAP@0.5** e **mAP@0.5:0.95** all’interno della famiglia, mentre `exp01` conserva la migliore **precision**.
- **YOLOv8** ha la configurazione più equilibrata in `exp08`, mentre `exp06` resta la migliore della famiglia su `mAP@0.5:0.95`, `exp07` sulla `mAP@0.5` ed `exp07b` sulla **precision**.
- **YOLOv11** domina il confronto complessivo: `exp11` è il migliore su **precision** e **mAP@0.5**, mentre `exp11b` è il migliore su **recall**, **F1-score** e **mAP@0.5:0.95**.

---

# 5. Migliori esperimenti complessivi

| Criterio     | Esperimento migliore | Valore | Interpretazione                         |
| ------------ | -------------------- | ------ | --------------------------------------- |
| Precision    | exp11                | 0.9436 | Predizioni più pulite a livello globale |
| Recall       | exp11b               | 0.9049 | Maggiore copertura dei simboli reali    |
| F1-score     | exp11b               | 0.9223 | Miglior compromesso complessivo         |
| mAP@0.5      | exp11                | 0.9513 | Migliore detection aggregata a IoU 0.5  |
| mAP@0.5:0.95 | exp11b               | 0.6665 | Migliore localizzazione media globale   |

## Top 3 complessivo per metrica

### Precision

1. **exp11** — 0.9436
2. **exp11b** — 0.9404
3. **exp10** — 0.9387

### Recall

1. **exp11b** — 0.9049
2. **exp11** — 0.9004
3. **exp03b** — 0.8854

### F1-score

1. **exp11b** — 0.9223
2. **exp11** — 0.9215
3. **exp10** — 0.8960

### mAP@0.5

1. **exp11** — 0.9513
2. **exp11b** — 0.9476
3. **exp10** — 0.9300

### mAP@0.5:0.95

1. **exp11b** — 0.6665
2. **exp11** — 0.6552
3. **exp10** — 0.6492

---

# 6. Interpretazione sintetica

## YOLOv7

- cresce in modo netto con l’introduzione della augmentation;
- `exp01` resta la baseline con la **precision** migliore della famiglia;
- `exp03b` è la variante più forte della famiglia su **recall**, **F1-score**, **mAP@0.5** e **mAP@0.5:0.95**;
- `exp04` risulta la meno convincente tra le augmentation YOLOv7.

## YOLOv8

- è competitivo già in baseline RGB;
- il **grayscale** ottiene la migliore metrica severa della famiglia (`mAP@0.5:0.95`);
- `aug_v1` porta la migliore `mAP@0.5` della famiglia;
- `aug_v2_compose` è la configurazione più equilibrata della famiglia in termini di **recall** e **F1-score**;
- `aug_v3 strong` migliora soprattutto la **precision**, ma non supera `exp08` nel bilancio complessivo.

## YOLOv11

- è la famiglia più forte dell’intero studio su tutte le metriche aggregate;
- già la baseline RGB (`exp09`) supera chiaramente YOLOv7 e YOLOv8;
- il **grayscale** (`exp10`) migliora la baseline RGB su precision e metriche mAP, pur sacrificando qualcosa in recall;
- `aug_v1` (`exp11`) è la migliore configurazione globale su **precision** e **mAP@0.5**;
- `aug_v3 strong` (`exp11b`) è la migliore configurazione globale su **recall**, **F1-score** e **mAP@0.5:0.95**;
- `aug_v2_compose` (`exp12`) è la variante meno convincente della famiglia.

## Conclusione globale

Il confronto complessivo tra famiglie mostra una gerarchia abbastanza chiara:

1. **YOLOv11** è la famiglia dominante sul piano delle prestazioni.
2. **YOLOv8** è intermedia, con risultati solidi ma inferiori a YOLOv11.
3. **YOLOv7** resta un riferimento utile, ma viene superata dalle famiglie più recenti.

Dal punto di vista operativo, i checkpoint più interessanti da portare avanti sono:

- **YOLOv11 exp11** se si vuole massimizzare **precision** e **mAP@0.5**;
- **YOLOv11 exp11b** se si vuole massimizzare **recall**, **F1-score** e **mAP@0.5:0.95**;
- **YOLOv8 exp08** come migliore alternativa più equilibrata all’interno della famiglia YOLOv8;
- **YOLOv7 exp03b** come migliore riferimento storico della famiglia YOLOv7.