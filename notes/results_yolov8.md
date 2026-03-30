# YOLOv8 — Risultati sperimentali

## Obiettivo

Questo documento raccoglie gli esperimenti svolti con **YOLOv8**, separandoli dal blocco YOLOv7 per mantenere più ordinato il materiale della tesi.

---

# 1. Setup comune

## Dataset

- **Numero classi:** 32
- **Validation images:** 126
- **Validation instances:** 1625
- **Resize:** 1024x1024
- **Task:** object detection

## Ambiente

- **Framework:** Ultralytics
- **Piattaforma:** Google Colab
- **GPU:** Tesla T4 16 GB
- **Python:** 3.11.13
- **Torch:** 2.6.0+cu124

## Nota tecnica

Nei dataset YOLOv8 usati finora Ultralytics ha segnalato la presenza contemporanea di **boxes** e **segments**, ma in validazione sono state considerate solo le **bounding box**.

---

# 2. Tabella riassuntiva esperimenti YOLOv8

| Exp ID | Input     | Augmentation   | Epochs | Batch | Precision | Recall | F1-score | mAP@0.5 | mAP@0.5:0.95 | Best epoch | Note                                                                  |
| ------ | --------- | -------------- | -----: | ----: | --------: | -----: | -------: | ------: | -----------: | ---------: | --------------------------------------------------------------------- |
| exp05  | RGB       | No             |    100 |     4 |    0.8846 | 0.8167 |   0.8493 |  0.8553 |       0.5856 |         80 | Baseline RGB                                                          |
| exp06  | Grayscale | No             |    100 |     4 |    0.8554 | 0.8279 |   0.8414 |  0.8759 |       0.6011 |         58 | Migliore mAP@0.5:0.95 tra le baseline                                 |
| exp07  | RGB       | aug_v1         |    100 |     4 |    0.8281 | 0.8445 |   0.8362 |  0.8878 |       0.5953 |         43 | Migliore mAP@0.5 complessiva YOLOv8 finora                            |
| exp08  | RGB       | aug_v2_compose |    100 |     4 |    0.8502 | 0.8581 |   0.8541 |  0.8734 |       0.5894 |         77 | Miglior F1-score e recall YOLOv8 finora                               |
| exp07b | RGB       | aug_strong_v3  |    100 |     4 |    0.8862 | 0.8200 |   0.8518 |  0.8660 |       0.5877 |       90 | Miglior precision tra le augmentation YOLOv8; strong rotation 25°–45° |


---

# 3. Baseline RGB — exp05

### Exp ID

**exp05_yolov8_rgb_1024_baseline**

### Configurazione

- **Modello:** YOLOv8
- **Framework:** Ultralytics
- **Input:** RGB originale
- **Grayscale:** No
- **Data augmentation aggiuntiva offline:** No
- **Resize:** 1024x1024
- **Epochs:** 100
- **Batch size:** 4
- **Checkpoint principale usato per la valutazione:** `best.pt`

### Hardware / ambiente

- **Piattaforma:** Google Colab
- **GPU:** Tesla T4 16 GB
- **VRAM disponibile:** circa 14913 MiB
- **Python:** 3.11.13
- **Torch:** 2.6.0+cu124
- **Ultralytics:** 8.4.26

### Model summary

- **Layers:** 73
- **Parameters:** 11,137,968
- **GFLOPs:** 28.5

### Dataset usato

- **Validation images:** 126
- **Validation instances:** 1625
- **Numero classi:** 32

## Metriche finali

| Metrica           |      Valore |
| ----------------- | ----------: |
| Precision         |      0.8846 |
| Recall            |      0.8167 |
| F1-score          |      0.8493 |
| mAP@0.5           |      0.8553 |
| mAP@0.5:0.95      |      0.5856 |
| Best epoch        |          80 |
| Speed preprocess  | 20.4 ms/img |
| Speed inference   | 22.7 ms/img |
| Speed postprocess |  8.2 ms/img |

### Commento sintetico

Il modello **YOLOv8 RGB baseline** mostra prestazioni complessivamente molto buone sul validation set.  
Rispetto alla baseline YOLOv7 RGB:

- la **precision** risulta leggermente inferiore;
- la **recall** migliora;
- migliorano in modo chiaro sia **mAP@0.5** sia **mAP@0.5:0.95**.

Questo suggerisce che YOLOv8 riesca a trovare più oggetti reali e, nel complesso, a produrre una detection più efficace, pur mantenendo una precisione ancora elevata.

## 3.1 Analisi qualitativa del training e della validazione

### Andamento complessivo del training

![Andamento training YOLOv8 RGB baseline](/outputs/yolo8/exp05_yolov8_rgb_1024_baseline/results.png)

**Figura X.** Andamento delle loss di training/validation e delle metriche principali durante il training della baseline YOLOv8 RGB. Le loss di training (`train/box_loss`, `train/cls_loss`, `train/dfl_loss`) diminuiscono in modo regolare; le metriche aggregate crescono rapidamente nelle prime epoche e tendono a stabilizzarsi nella seconda metà del training.

### Distribuzione labels e box

![Distribuzione labels YOLOv8 RGB baseline](/outputs/yolo8/exp05_yolov8_rgb_1024_baseline/labels.jpg)

**Figura X.** Distribuzione delle classi e delle bounding box nel dataset. Il grafico conferma lo sbilanciamento tra classi già osservato negli esperimenti precedenti e mostra una prevalenza di box relativamente piccole.

### Confusion matrix normalizzata

![Confusion matrix YOLOv8 RGB baseline](/outputs/yolo8/exp05_yolov8_rgb_1024_baseline/confusion_matrix_normalized.png)

**Figura X.** Confusion matrix normalizzata del best checkpoint YOLOv8 RGB. La diagonale principale è ben marcata, segnale di una buona separazione tra molte classi. Restano però falsi negativi verso background e alcune confusioni residue per classi più rare o più difficili.

### Precision curve

![Precision curve YOLOv8 RGB baseline](/outputs/yolo8/exp05_yolov8_rgb_1024_baseline/BoxP_curve.png)

**Figura X.** Curva Precision-Confidence. La precision cresce progressivamente all’aumentare della confidence threshold e raggiunge valori prossimi a **0.99** alle soglie più alte.

### Recall curve

![Recall curve YOLOv8 RGB baseline](/outputs/yolo8/exp05_yolov8_rgb_1024_baseline/BoxR_curve.png)

**Figura X.** Curva Recall-Confidence. La recall parte da circa **0.91** a confidence quasi nulla e decresce progressivamente, con un calo più marcato alle soglie elevate.

### F1 curve

![F1 curve YOLOv8 RGB baseline](/outputs/yolo8/exp05_yolov8_rgb_1024_baseline/BoxF1_curve.png)

**Figura X.** Curva F1-Confidence. Il miglior compromesso tra precision e recall si osserva a una confidence di circa **0.491**, con **F1 ≈ 0.84**.

### Precision-Recall curve

![PR curve YOLOv8 RGB baseline](/outputs/yolo8/exp05_yolov8_rgb_1024_baseline/BoxPR_curve.png)

**Figura X.** Curva Precision-Recall del best checkpoint YOLOv8 RGB. Il valore globale riportato dal grafico è coerente con **mAP@0.5 ≈ 0.855**.

---

## 3.2 Interpretazione delle curve

Le curve mostrano un comportamento complessivamente regolare e coerente con un training stabile.

### Osservazioni principali

- le loss di training decrescono in modo regolare;
- `val/box_loss` e `val/cls_loss` diminuiscono rapidamente e poi tendono a stabilizzarsi;
- `val/dfl_loss` mostra un minimo nelle epoche intermedie e una lieve risalita finale;
- **precision**, **recall**, **mAP@0.5** e **mAP@0.5:0.95** crescono rapidamente nella prima parte del training;
- le metriche entrano in plateau circa tra metà e fine addestramento.

### Interpretazione

Questo comportamento suggerisce che YOLOv8 apprenda rapidamente una rappresentazione utile del problema e raggiunga una buona convergenza già prima della fine del training. Il fatto che il **best checkpoint** non coincida necessariamente con l’ultima epoca è coerente con una fase finale di stabilizzazione o lieve oscillazione delle metriche.

---

## 3.3 Punti di forza e criticità

### Punti di forza

- miglioramento netto rispetto alla baseline YOLOv7 RGB su recall e mAP;
- buona qualità complessiva della localizzazione;
- buona separazione tra molte classi nella confusion matrix;
- training stabile e rapido;
- best checkpoint molto competitivo anche rispetto agli esperimenti YOLOv7 con augmentation.

### Criticità

- alcune classi rare restano molto instabili;
- `Terminal`, `LED`, `Capacitor` e alcune classi poco rappresentate continuano a essere problematiche;
- lieve perdita di precision rispetto a YOLOv7 baseline;
- presenza di warning sul dataset misto detect/segment, da tenere presente nella pulizia finale della pipeline.

---

## 3.4 Conclusione sull’esperimento YOLOv8 RGB baseline

Nel complesso, **YOLOv8 RGB baseline** rappresenta un risultato molto solido e un passo avanti rispetto alla baseline YOLOv7 RGB.

Le evidenze principali sono:

- **miglior recall**
- **miglior mAP@0.5**
- **miglior mAP@0.5:0.95**
- prestazioni molto competitive anche rispetto alla migliore variante YOLOv7 con augmentation

Questo rende YOLOv8 una candidata molto promettente per i prossimi confronti:

1. **YOLOv8 grayscale**
2. **YOLOv8 con augmentation**
3. confronto finale tra famiglie di modelli

La conclusione operativa è quindi che, allo stato attuale, **YOLOv8 RGB baseline** merita di essere considerata una delle configurazioni di riferimento più forti dell’intero studio.

---

# 4. Baseline grayscale — exp06

## 4.1 Obiettivo

Valutare le prestazioni di **YOLOv8** sul dataset completamente convertito in **grayscale**, mantenendo invariati modello, split del dataset, numero di epoche, batch size e risoluzione rispetto all’esperimento `exp05` su immagini RGB.

L’obiettivo è verificare se, anche nel caso di YOLOv8, la rimozione dell’informazione cromatica possa:

- aumentare la robustezza del modello sui simboli elettrici;
- migliorare recall e metriche mAP;
- favorire una localizzazione più precisa delle bounding box.

---

## 4.2 Setup dettagliato

### Exp ID

**exp06_yolov8_gray_1024_baseline**

### Configurazione

- **Modello:** YOLOv8
- **Framework:** Ultralytics
- **Input:** grayscale
- **Grayscale:** Sì, applicato all’intero dataset
- **Data augmentation aggiuntiva offline:** No
- **Resize:** 1024x1024
- **Epochs:** 100
- **Batch size:** 4
- **Checkpoint principale usato per la valutazione:** `best.pt`

### Hardware / ambiente

- **Piattaforma:** Google Colab
- **GPU:** Tesla T4 16 GB
- **VRAM disponibile:** circa 14913 MiB
- **Python:** 3.11.13
- **Torch:** 2.6.0+cu124
- **Ultralytics:** 8.4.27

### Model summary

- **Layers:** 73
- **Parameters:** 11,137,968
- **GFLOPs:** 28.5

## Metriche finali

| Metrica           |      Valore |
| ----------------- | ----------: |
| Precision         |      0.8554 |
| Recall            |      0.8279 |
| F1-score          |      0.8414 |
| mAP@0.5           |      0.8759 |
| mAP@0.5:0.95      |      0.6011 |
| Best epoch        |          58 |
| Speed preprocess  |  5.1 ms/img |
| Speed inference   | 21.8 ms/img |
| Speed postprocess |  8.1 ms/img |

### Commento sintetico

La baseline **YOLOv8 grayscale** mostra un comportamento molto competitivo e, sulle metriche di detection aggregate, supera la baseline YOLOv8 RGB sia su **recall** sia su entrambe le metriche **mAP**. La precisione si riduce in modo più evidente, ma il modello risulta complessivamente più capace di trovare gli oggetti reali e di localizzarli con maggiore accuratezza media.


## 4.3 Analisi qualitativa del training e della validazione

### Andamento complessivo del training

![Andamento training YOLOv8 grayscale baseline](/outputs/yolo8/exp06_yolov8_gray_1024_baseline/results.png)

**Figura X.** Andamento delle loss di training/validation e delle metriche principali durante il training della baseline YOLOv8 grayscale. Le loss diminuiscono in modo regolare; le metriche aggregate crescono rapidamente nelle prime epoche e si stabilizzano successivamente. `mAP@0.5:0.95` raggiunge il suo massimo nelle epoche intermedie, coerentemente con il best checkpoint osservato.

### Distribuzione labels e box

![Distribuzione labels YOLOv8 grayscale baseline](/outputs/yolo8/exp06_yolov8_gray_1024_baseline/labels.jpg)

**Figura X.** Distribuzione delle classi e delle bounding box nel dataset grayscale. La distribuzione resta identica a quella del dataset RGB, confermando che il preprocessing modifica solo il dominio visivo e non la composizione semantica del dataset.

### Confusion matrix normalizzata

![Confusion matrix YOLOv8 grayscale baseline](/outputs/yolo8/exp06_yolov8_gray_1024_baseline/confusion_matrix_normalized.png)

**Figura X.** Confusion matrix normalizzata del best checkpoint YOLOv8 grayscale. La diagonale principale è ben marcata, con errori residui concentrati soprattutto nelle classi più rare e in alcuni falsi negativi verso background.

### Precision curve

![Precision curve YOLOv8 grayscale baseline](/outputs/yolo8/exp06_yolov8_gray_1024_baseline/BoxP_curve.png)

**Figura X.** Curva Precision-Confidence. La precisione cresce all’aumentare della confidence threshold e raggiunge valori prossimi a **1.00** alle soglie più elevate.

### Recall curve

![Recall curve YOLOv8 grayscale baseline](/outputs/yolo8/exp06_yolov8_gray_1024_baseline/BoxR_curve.png)

**Figura X.** Curva Recall-Confidence. La recall parte da circa **0.92** a soglia nulla e decresce progressivamente, con un calo più netto oltre le confidence intermedie.

### F1 curve

![F1 curve YOLOv8 grayscale baseline](/outputs/yolo8/exp06_yolov8_gray_1024_baseline/BoxF1_curve.png)

**Figura X.** Curva F1-Confidence. Il miglior compromesso tra precision e recall si osserva a una confidence di circa **0.395**, con **F1 ≈ 0.84**.

### Precision-Recall curve

![PR curve YOLOv8 grayscale baseline](/outputs/yolo8/exp06_yolov8_gray_1024_baseline/BoxPR_curve.png)

**Figura X.** Curva Precision-Recall del best checkpoint YOLOv8 grayscale. Il valore globale riportato dal grafico è coerente con **mAP@0.5 ≈ 0.876**.

## 4.4 Interpretazione delle curve

Le curve mostrano un comportamento stabile e coerente con una buona convergenza del training.

### Osservazioni principali

- le loss di training decrescono in modo regolare;
- `val/box_loss` e `val/cls_loss` diminuiscono rapidamente e poi si stabilizzano;
- `val/dfl_loss` mostra un minimo nelle epoche intermedie e una lieve risalita finale;
- le metriche **precision**, **recall**, **mAP@0.5** e **mAP@0.5:0.95** crescono velocemente nelle prime epoche;
- il best checkpoint non coincide con l’ultima epoca, ma con una fase intermedia più favorevole in termini di localizzazione media.

### Interpretazione

Questo andamento suggerisce che YOLOv8 grayscale apprenda rapidamente una rappresentazione utile del problema e che il vantaggio del preprocessing in scala di grigi emerga soprattutto sulla **qualità della localizzazione** più che sulla sola precisione finale.

---

## 4.5 Punti di forza e criticità

### Punti di forza

- miglioramento rispetto a YOLOv8 RGB su **recall** e metriche **mAP**;
- migliore **mAP@0.5:0.95** tra le baseline finora completate;
- training stabile;
- buona qualità della localizzazione su molte classi;
- forte competitività anche rispetto a YOLOv7 + aug_v1 sulla metrica più severa.

### Criticità

- calo sensibile di **precision** rispetto a YOLOv8 RGB;
- **F1-score** leggermente inferiore alla baseline RGB;
- classi rare ancora instabili;
- **Terminal** resta una classe critica anche con YOLOv8 grayscale.

---

## 4.6 Conclusione sull’esperimento YOLOv8 grayscale baseline

Nel complesso, **YOLOv8 grayscale** rappresenta un risultato molto interessante.

Rispetto a YOLOv8 RGB:

- migliora **recall**;
- migliora **mAP@0.5**;
- migliora **mAP@0.5:0.95**;
- peggiora però in modo visibile la **precision**.

Questo suggerisce che, nel caso di YOLOv8, il grayscale possa effettivamente aiutare il modello a concentrarsi meglio sulla struttura geometrica dei simboli, producendo un vantaggio sulla detection complessiva e sulla localizzazione media.

Dal punto di vista operativo, si possono formulare due conclusioni:

1. se la priorità è il **miglior equilibrio globale precision/recall**, la baseline RGB resta molto competitiva;
2. se la priorità è la **migliore qualità media di detection e localizzazione**, **YOLOv8 grayscale** è attualmente la baseline più promettente tra quelle completate.

---

# 5. Augmentation v1 — exp07

## 5.1 Obiettivo

Valutare l'effetto di una **augmentation offline leggera e controllata** anche su **YOLOv8**, mantenendo invariati architettura, split del dataset, risoluzione, batch size e numero di epoche rispetto alla baseline YOLOv8 RGB.

L'obiettivo è verificare se una politica di augmentation già risultata efficace su YOLOv7 (`aug_v1`) riesca a:

- aumentare la robustezza del modello;
- migliorare **recall** e metriche **mAP**;
- mantenere un equilibrio accettabile con la precisione.

---

## 5.2 Setup dettagliato

### Exp ID

**exp07_yolov8_rgb_aug_v1_1024_baseline**

### Configurazione

- **Modello:** YOLOv8
- **Framework:** Ultralytics
- **Input:** RGB
- **Dataset base:** `rf_yolov8_1024_rgb_aug_v1`
- **Augmentation:** `aug_v1` offline sul training set
- **Validation set:** invariato
- **Test set:** invariato
- **Resize:** 1024x1024
- **Epochs:** 100
- **Batch size:** 4
- **Checkpoint principale usato per la valutazione:** `best.pt`

### Politica di augmentation usata

La variante `aug_v1` corrisponde alla stessa augmentation leggera già utilizzata negli esperimenti YOLOv7, basata su:

- **rotazione lieve**;
- **piccola traslazione**;
- **lieve scaling**;
- **modesta variazione di luminosità/contrasto**;
- **rumore leggero**.

L'augmentation è applicata **solo al training set**, mentre validation e test restano invariati per garantire un confronto corretto.

### Hardware / ambiente

- **Piattaforma:** Google Colab
- **GPU:** Tesla T4 16 GB
- **VRAM disponibile:** circa 14913 MiB
- **Python:** 3.11.13
- **Torch:** 2.6.0+cu124
- **Ultralytics:** 8.4.27

## Politica di augmentation

- rotazione lieve
- piccola traslazione
- lieve scaling
- lieve perturbazione fotometrica
- rumore leggero
- nessun flip

## Metriche finali

| Metrica           |      Valore |
| ----------------- | ----------: |
| Precision         |      0.8281 |
| Recall            |      0.8445 |
| F1-score          |      0.8362 |
| mAP@0.5           |      0.8878 |
| mAP@0.5:0.95      |      0.5953 |
| Best epoch        |          43 |
| Speed preprocess  |  5.0 ms/img |
| Speed inference   | 22.4 ms/img |
| Speed postprocess |  7.1 ms/img |

### Commento sintetico

L'esperimento **YOLOv8 RGB + aug_v1** migliora in modo chiaro le metriche di detection rispetto alla baseline YOLOv8 RGB, soprattutto su **recall** e **mAP@0.5**. La precisione cala rispetto alla baseline, ma il modello diventa più sensibile nel trovare i simboli reali e ottiene la **migliore mAP@0.5** tra tutti gli esperimenti completati finora.


## 5.3 Analisi qualitativa del training e della validazione

### Andamento complessivo del training

![Andamento training YOLOv8 RGB + aug_v1](/outputs/yolo8/exp07_yolov8_rgb_aug_v1_1024_baseline/results.png)

**Figura X.** Andamento delle loss di training/validation e delle metriche principali durante il training di YOLOv8 RGB con augmentation v1. Le loss di training diminuiscono in modo regolare; le metriche aggregate crescono rapidamente nella prima parte del training e si stabilizzano successivamente.

### Distribuzione labels e box

![Distribuzione labels YOLOv8 RGB + aug_v1](/outputs/yolo8/exp07_yolov8_rgb_aug_v1_1024_baseline/labels.jpg)

**Figura X.** Distribuzione delle classi e delle bounding box nel dataset augmentato. L'aumento del numero di campioni nel training set rende più densa la distribuzione osservata, pur mantenendo inalterato il validation set.

### Confusion matrix normalizzata

![Confusion matrix YOLOv8 RGB + aug_v1](/outputs/yolo8/exp07_yolov8_rgb_aug_v1_1024_baseline/confusion_matrix_normalized.png)

**Figura X.** Confusion matrix normalizzata del best checkpoint YOLOv8 RGB + aug_v1. La diagonale principale resta ben marcata, ma si osserva una presenza ancora significativa di falsi negativi verso background e alcune confusioni residue nelle classi più difficili.

### Precision curve

![Precision curve YOLOv8 RGB + aug_v1](/outputs/yolo8/exp07_yolov8_rgb_aug_v1_1024_baseline/BoxP_curve.png)

**Figura X.** Curva Precision-Confidence. La precisione cresce progressivamente con la confidence threshold e raggiunge valori prossimi a **1.00** alle soglie più alte.

### Recall curve

![Recall curve YOLOv8 RGB + aug_v1](/outputs/yolo8/exp07_yolov8_rgb_aug_v1_1024_baseline/BoxR_curve.png)

**Figura X.** Curva Recall-Confidence. La recall parte da circa **0.92** a soglia nulla e decresce progressivamente, mostrando un buon livello iniziale di sensibilità del modello.

### F1 curve

![F1 curve YOLOv8 RGB + aug_v1](/outputs/yolo8/exp07_yolov8_rgb_aug_v1_1024_baseline/BoxF1_curve.png)

**Figura X.** Curva F1-Confidence. Il miglior compromesso tra precision e recall si osserva a una confidence di circa **0.221**, con **F1 ≈ 0.82**.

### Precision-Recall curve

![PR curve YOLOv8 RGB + aug_v1](/outputs/yolo8/exp07_yolov8_rgb_aug_v1_1024_baseline/BoxPR_curve.png)

**Figura X.** Curva Precision-Recall del best checkpoint YOLOv8 RGB + aug_v1. Il valore globale riportato dal grafico è coerente con **mAP@0.5 ≈ 0.888**, il migliore osservato finora.

## 5.4 Interpretazione delle curve

Le curve mostrano un comportamento stabile e coerente con una buona convergenza del training.

### Osservazioni principali

- le loss di training decrescono in modo regolare;
- `val/box_loss` e `val/cls_loss` diminuiscono rapidamente e poi si stabilizzano;
- `val/dfl_loss` mostra un minimo nelle epoche intermedie e una lieve risalita finale;
- le metriche aggregate crescono velocemente nelle prime epoche e poi si stabilizzano;
- il modello sembra beneficiare dell'augmentation soprattutto nella capacità di aumentare la copertura dei simboli reali.

### Interpretazione

Nel complesso, l'augmentation leggera applicata a YOLOv8 sembra produrre un effetto positivo soprattutto sulla **recall** e sulla **mAP@0.5**, mentre il vantaggio sulla localizzazione più severa (**mAP@0.5:0.95**) è presente ma più contenuto.

## 5.5 Punti di forza e criticità

### Punti di forza

- migliore **mAP@0.5** tra tutti gli esperimenti completati finora;
- miglioramento rispetto alla baseline YOLOv8 RGB su recall e metriche mAP;
- buona robustezza complessiva;
- training stabile;
- competitività elevata anche rispetto alla migliore variante YOLOv7 con augmentation.

### Criticità

- calo sensibile di **precision**;
- **F1-score** inferiore sia a YOLOv8 RGB baseline sia a YOLOv7 aug_v1;
- alcune classi rare restano instabili;
- la qualità media di localizzazione resta leggermente inferiore a YOLOv8 grayscale sulla metrica più severa.

---

## 5.6 Conclusione sull'esperimento YOLOv8 RGB + aug_v1

Nel complesso, **YOLOv8 RGB + aug_v1** conferma che una augmentation offline leggera e coerente con il dominio è utile anche per YOLOv8.

I principali risultati sono:

- incremento di **recall** rispetto alla baseline YOLOv8 RGB;
- miglioramento netto di **mAP@0.5**;
- miglioramento anche di **mAP@0.5:0.95**, seppur più contenuto;
- perdita però di **precision** e di **F1-score** rispetto alle migliori configurazioni più conservative.

Dal punto di vista operativo, l'esperimento suggerisce che:

1. se la priorità è la **migliore detection aggregata a IoU 0.5**, **YOLOv8 RGB + aug_v1** è attualmente la configurazione migliore;
2. se la priorità è la **localizzazione media più precisa**, **YOLOv8 grayscale** resta leggermente superiore su **mAP@0.5:0.95**;
3. se si cerca il miglior compromesso precision/recall, il confronto con YOLOv7 aug_v1 resta ancora aperto.

# 6. Augmentation v2_compose — exp08

## 6.1 Obiettivo

Valutare l'effetto della politica di augmentation **`aug_v2_compose`** anche su **YOLOv8**, mantenendo invariati modello, split del dataset, risoluzione, batch size e numero di epoche rispetto agli altri esperimenti YOLOv8.

L'obiettivo è verificare se una augmentation più strutturale, basata sulla **composizione di diagrammi affiancati** e su una perturbazione visiva molto lieve, possa:

- aumentare ulteriormente la **recall**;
- migliorare il compromesso globale tra precision, recall e metriche mAP;
- rendere il modello più robusto a scene più dense o a combinazioni di simboli più complesse.

---

## 6.2 Setup dettagliato

### Exp ID

**exp08_yolov8_rgb_aug_v2_compose_1024**

### Configurazione

- **Modello:** YOLOv8
- **Framework:** Ultralytics
- **Input:** RGB
- **Dataset base:** versione RGB con augmentation offline `aug_v2_compose`
- **Augmentation:** composizione di due diagrammi/porzioni di diagramma affiancati, con resize finale a 1024x1024
- **Validation set:** invariato
- **Test set:** invariato
- **Resize:** 1024x1024
- **Epochs:** 100
- **Batch size:** 4
- **Checkpoint principale usato per la valutazione:** `best.pt`

### Politica di augmentation usata

La variante `aug_v2_compose` introduce una trasformazione più strutturale rispetto ad `aug_v1`. In particolare:

- vengono composte **due immagini del training set** in un unico campione più ricco;
- le bounding box vengono aggiornate coerentemente rispetto alla nuova immagine composta;
- il campione finale viene riportato a **1024x1024**;
- può essere applicata una **perturbazione finale molto lieve** su luminosità/contrasto.

L'augmentation è applicata **solo al training set**, mentre validation e test restano invariati.

### Hardware / ambiente

- **Piattaforma:** Google Colab
- **GPU:** Tesla T4 16 GB
- **VRAM disponibile:** circa 14913 MiB
- **Python:** 3.11.13
- **Torch:** 2.6.0+cu124
- **Ultralytics:** 8.4.27

## 6.3 Metriche finali

> Le metriche sotto riportate fanno riferimento al **best checkpoint**, con **best epoch = 77** ricavata da `results.csv` sulla metrica `mAP@0.5:0.95`.

| Metrica                  |      Valore |
| ------------------------ | ----------: |
| Precision                |      0.8502 |
| Recall                   |      0.8581 |
| F1-score                 |      0.8541 |
| mAP@0.5                  |      0.8734 |
| mAP@0.5:0.95             |      0.5894 |
| Best epoch               |          77 |
| Best mAP@0.5             |      0.8818 |
| Best mAP@0.5:0.95        |      0.6024 |
| F1 massimo (dal grafico) |  circa 0.85 |
| Confidence al F1 massimo | circa 0.307 |

### Commento sintetico

L'esperimento **YOLOv8 RGB + aug_v2_compose** mostra un comportamento molto interessante: non raggiunge il massimo assoluto di **mAP@0.5** ottenuto da `exp07`, ma ottiene il **miglior F1-score** e la **miglior recall** tra gli esperimenti YOLOv8 completati finora, mantenendo anche una **mAP@0.5:0.95** molto alta e quasi allineata alla variante grayscale.

In altre parole, `exp08` sembra offrire il compromesso più equilibrato tra copertura degli oggetti reali e qualità media della localizzazione.


## 6.7 Analisi qualitativa del training e della validazione

### Andamento complessivo del training

![Andamento training YOLOv8 RGB + aug_v2_compose](/outputs/yolo8/exp08_yolov8_1024_rgb_aug_v2_compose/results.png)

**Figura X.** Andamento delle loss di training/validation e delle metriche principali durante il training con `aug_v2_compose`. Le loss di training diminuiscono in modo regolare; le metriche aggregate crescono rapidamente nella prima parte del training e raggiungono un plateau stabile nella seconda metà.

### Distribuzione labels e box

![Distribuzione labels YOLOv8 RGB + aug_v2_compose](/outputs/yolo8/exp08_yolov8_1024_rgb_aug_v2_compose/labels.jpg)

**Figura X.** Distribuzione delle classi e delle bounding box nel dataset `aug_v2_compose`. Rispetto al dataset originale, la distribuzione appare più densa e mostra una concentrazione più marcata nella fascia centrale verticale dell'immagine, coerente con la composizione affiancata dei diagrammi.

### Confusion matrix normalizzata

![Confusion matrix YOLOv8 RGB + aug_v2_compose](/outputs/yolo8/exp08_yolov8_1024_rgb_aug_v2_compose/confusion_matrix_normalized.png)

**Figura X.** Confusion matrix normalizzata del best checkpoint `exp08`. La diagonale principale rimane ben marcata, segnale di una buona separazione tra molte classi. Restano alcune confusioni residue e falsi negativi verso background, ma il quadro complessivo è coerente con le buone metriche aggregate ottenute.

### Precision curve

![Precision curve YOLOv8 RGB + aug_v2_compose](/outputs/yolo8/exp08_yolov8_1024_rgb_aug_v2_compose/BoxP_curve.png)

**Figura X.** Curva Precision-Confidence. La precisione cresce progressivamente con la confidence threshold e raggiunge valori prossimi a **1.00** alle soglie più alte.

### Recall curve

![Recall curve YOLOv8 RGB + aug_v2_compose](/outputs/yolo8/exp08_yolov8_1024_rgb_aug_v2_compose/BoxR_curve.png)

**Figura X.** Curva Recall-Confidence. La recall parte da circa **0.91** a soglia nulla e decresce progressivamente; resta relativamente elevata fino a confidence intermedie, confermando una buona sensibilità del modello.

### F1 curve

![F1 curve YOLOv8 RGB + aug_v2_compose](/outputs/yolo8/exp08_yolov8_1024_rgb_aug_v2_compose/BoxF1_curve.png)

**Figura X.** Curva F1-Confidence. Il miglior compromesso tra precision e recall si osserva a una confidence di circa **0.307**, con **F1 ≈ 0.85**.

### Precision-Recall curve

![PR curve YOLOv8 RGB + aug_v2_compose](/outputs/yolo8/exp08_yolov8_1024_rgb_aug_v2_compose/BoxPR_curve.png)

**Figura X.** Curva Precision-Recall del best checkpoint `exp08`. Il valore globale riportato dal grafico è coerente con **mAP@0.5 ≈ 0.882**.

## 6.8 Interpretazione delle curve

Le curve mostrano un comportamento stabile e coerente con una buona convergenza del training.

### Osservazioni principali

- le loss di training decrescono in modo regolare;
- `val/box_loss` e `val/cls_loss` diminuiscono rapidamente e poi si stabilizzano;
- `val/dfl_loss` mostra un minimo nelle epoche intermedie e una leggera risalita finale;
- le metriche aggregate crescono rapidamente nelle prime epoche e poi tendono a stabilizzarsi;
- il best checkpoint si colloca nella seconda metà del training, coerentemente con una convergenza più tardiva rispetto ad `exp07`.

### Interpretazione

Nel complesso, `aug_v2_compose` sembra fornire a YOLOv8 un vantaggio reale in termini di robustezza e copertura dei simboli, senza compromettere in modo forte la precisione. L'effetto finale appare più bilanciato rispetto alla versione `aug_v1`.

## 6.9 Punti di forza e criticità

### Punti di forza

- migliore **recall** tra gli esperimenti YOLOv8 completati finora;
- migliore **F1-score** tra gli esperimenti YOLOv8 completati finora;
- **mAP@0.5** molto alta, seconda solo a `exp07`;
- **mAP@0.5:0.95** molto alta e quasi allineata a `exp06`;
- configurazione complessivamente molto equilibrata.

### Criticità

- **precision** inferiore alla baseline RGB;
- **mAP@0.5** leggermente inferiore a `exp07`;
- la composizione di diagrammi modifica la distribuzione spaziale delle box, quindi sarà utile valutare se il vantaggio si conferma anche su ulteriori test o su dataset più puliti.

---

## 6.10 Conclusione sull'esperimento YOLOv8 RGB + aug_v2_compose

Nel complesso, **YOLOv8 RGB + aug_v2_compose** si presenta come una delle configurazioni più forti e bilanciate dell'intero blocco YOLOv8.

I risultati principali sono:

- **migliore recall** tra gli esperimenti YOLOv8 completati;
- **miglior F1-score** tra gli esperimenti YOLOv8 completati;
- **mAP@0.5** molto alta;
- **mAP@0.5:0.95** praticamente allineata alla migliore variante YOLOv8 finora sulla metrica severa.

Dal punto di vista operativo, si possono trarre queste conclusioni:

1. se la priorità è la **migliore mAP@0.5**, `exp07` resta leggermente davanti;
2. se la priorità è il **miglior equilibrio complessivo**, `exp08` è attualmente la configurazione YOLOv8 più convincente;
3. se la priorità è la **migliore mAP@0.5:0.95**, `exp06` grayscale resta ancora di pochissimo superiore.

---

# 7. Augmentation v3 strong — exp07b

## 7.1 Obiettivo

Valutare l’effetto di una **augmentation offline forte** su **YOLOv8**, costruita per aumentare in modo marcato la variabilità geometrica del training set tramite **rotazioni casuali comprese tra 25° e 45°**.

L’obiettivo è verificare se una politica più aggressiva rispetto ad `aug_v1` possa:

- mantenere il riconoscimento corretto dei simboli anche in condizioni geometriche più difficili;
- aumentare la robustezza del modello;
- migliorare la qualità complessiva della detection senza compromettere troppo il compromesso precision/recall.

---

## 7.2 Setup dettagliato

### Exp ID

**exp07b_rf_yolov8_1024_rgb_aug_strong_v3**

### Configurazione

- **Modello:** YOLOv8
- **Framework:** Ultralytics
- **Input:** RGB
- **Dataset base:** `rf_yolov7_1024_rgb_aug_strong_v3` esportato per YOLOv8
- **Augmentation:** `aug_strong_v3` offline sul training set
- **Politica dominante:** rotazioni casuali forti tra **25° e 45°**
- **Validation set:** invariato
- **Test set:** invariato
- **Resize:** 1024x1024
- **Epochs:** 100
- **Batch size:** 4
- **Checkpoint principale usato per la valutazione:** `best.pt`

### Politica di augmentation usata

La variante `aug_strong_v3` è stata progettata come versione più drastica rispetto ad `aug_v1`. In particolare:

- rotazioni casuali forti nel range **25°–45°**;
- aggiornamento coerente delle bounding box;
- maggiore variabilità geometrica del training set;
- nessuna modifica a validation e test per mantenere corretto il confronto sperimentale.

### Hardware / ambiente

- **Piattaforma:** Google Colab
- **GPU:** Tesla T4 16 GB
- **VRAM disponibile:** circa 14913 MiB
- **Python:** 3.11.13
- **Torch:** 2.6.0+cu124
- **Ultralytics:** 8.4.27

## 7.3 Metriche finali

| Metrica                  |      Valore |
| ------------------------ | ----------: |
| Precision                |      0.8862 |
| Recall                   |      0.8200 |
| F1-score                 |      0.8518 |
| mAP@0.5                  |      0.8660 |
| mAP@0.5:0.95             |      0.5877 |
| Best epoch               |        n.d. |
| F1 massimo (dal grafico) |  circa 0.84 |
| Confidence al F1 massimo | circa 0.512 |
| Speed preprocess         | 16.5 ms/img |
| Speed inference          | 22.6 ms/img |
| Speed postprocess        |  2.6 ms/img |

### Commento sintetico

L’esperimento **YOLOv8 RGB + aug_strong_v3** mostra un comportamento diverso rispetto alle augmentation più leggere: la **precisione** cresce in modo sensibile e diventa la migliore tra le augmentation YOLOv8 completate, mentre **recall** e **mAP@0.5** risultano leggermente inferiori rispetto ad `exp07` ed `exp08`. La metrica **mAP@0.5:0.95** rimane comunque molto competitiva e superiore a `exp07`, suggerendo una localizzazione mediamente più robusta.


## 7.8 Analisi qualitativa del training e della validazione

### Andamento complessivo del training

![Andamento training YOLOv8 RGB + aug_strong_v3](/outputs/yolo8/exp07b_rf_yolov8_1024_rgb_aug_strong_v3/results.png)

**Figura X.** Andamento delle loss di training/validation e delle metriche principali durante il training con `aug_strong_v3`. Le loss decrescono in modo regolare; le metriche aggregate crescono rapidamente nelle prime epoche e poi si stabilizzano, mostrando un training complessivamente stabile anche in presenza di una augmentation molto più aggressiva.

### Distribuzione labels e box

![Distribuzione labels YOLOv8 RGB + aug_strong_v3](/outputs/yolo8/exp07b_rf_yolov8_1024_rgb_aug_strong_v3/labels.jpg)

**Figura X.** Distribuzione delle classi e delle bounding box nel dataset `aug_strong_v3`. Rispetto alle versioni meno aggressive, la distribuzione spaziale delle box appare più dispersa diagonalmente, coerentemente con la presenza di diagrammi fortemente ruotati.

### Confusion matrix normalizzata

![Confusion matrix YOLOv8 RGB + aug_strong_v3](/outputs/yolo8/exp07b_rf_yolov8_1024_rgb_aug_strong_v3/confusion_matrix_normalized.png)

**Figura X.** Confusion matrix normalizzata del best checkpoint `exp07b`. La diagonale principale resta ben marcata e il modello mantiene una buona separazione tra molte classi. Persistono falsi negativi verso background, ma il quadro complessivo resta coerente con una forte precisione aggregata.

### Precision curve

![Precision curve YOLOv8 RGB + aug_strong_v3](/outputs/yolo8/exp07b_rf_yolov8_1024_rgb_aug_strong_v3/BoxP_curve.png)

**Figura X.** Curva Precision-Confidence. La precisione cresce progressivamente con la confidence threshold e raggiunge valori prossimi a **1.00** alle soglie più alte.

### Recall curve

![Recall curve YOLOv8 RGB + aug_strong_v3](/outputs/yolo8/exp07b_rf_yolov8_1024_rgb_aug_strong_v3/BoxR_curve.png)

**Figura X.** Curva Recall-Confidence. La recall parte da circa **0.91** a soglia nulla e decresce progressivamente, con una perdita più rapida alle confidence elevate rispetto alle versioni più bilanciate.

### F1 curve

![F1 curve YOLOv8 RGB + aug_strong_v3](/outputs/yolo8/exp07b_rf_yolov8_1024_rgb_aug_strong_v3/BoxF1_curve.png)

**Figura X.** Curva F1-Confidence. Il miglior compromesso tra precision e recall si osserva a una confidence di circa **0.512**, con **F1 ≈ 0.84**.

### Precision-Recall curve

![PR curve YOLOv8 RGB + aug_strong_v3](/outputs/yolo8/exp07b_rf_yolov8_1024_rgb_aug_strong_v3/BoxPR_curve.png)

**Figura X.** Curva Precision-Recall del best checkpoint `exp07b`. Il valore globale riportato dal grafico è coerente con **mAP@0.5 ≈ 0.874**.

## 7.9 Interpretazione delle curve

Le curve mostrano un comportamento stabile e coerente con una buona convergenza del training.

### Osservazioni principali

- le loss di training decrescono in modo regolare;
- `val/box_loss`, `val/cls_loss` e `val/dfl_loss` diminuiscono rapidamente e poi si stabilizzano;
- le metriche aggregate crescono rapidamente nelle prime epoche e poi entrano in plateau;
- la curva F1 raggiunge il massimo a una confidence più alta rispetto a `exp07` ed `exp08`, coerentemente con un modello più conservativo.

### Interpretazione

Nel complesso, `aug_strong_v3` non migliora tutte le metriche aggregate, ma rende YOLOv8 più selettivo e più forte in **precision**. Il comportamento osservato è coerente con un training robusto su un dataset più difficile e geometricamente più variabile.

## 7.10 Punti di forza e criticità

### Punti di forza

- migliore **precision** tra le augmentation YOLOv8 completate;
- **F1-score** elevato e secondo solo a `exp08`;
- **mAP@0.5:0.95** superiore a `exp07`;
- training stabile nonostante la forte perturbazione geometrica.

### Criticità

- **recall** inferiore rispetto ad `exp07` ed `exp08`;
- **mAP@0.5** inferiore rispetto alle altre augmentation YOLOv8;
- configurazione meno equilibrata di `exp08` se l’obiettivo è massimizzare tutte le metriche aggregate contemporaneamente.

---

## 7.11 Conclusione sull’esperimento YOLOv8 RGB + aug_strong_v3

Nel complesso, **YOLOv8 RGB + aug_strong_v3** conferma che una augmentation forte è utilizzabile anche su questo task senza destabilizzare l’addestramento.

I principali risultati sono:

- forte recupero della **precision**;
- **F1-score** molto competitivo;
- **mAP@0.5:0.95** buona e superiore alla variante `aug_v1`;
- lieve sacrificio di **recall** e **mAP@0.5** rispetto alle augmentation più bilanciate.

Dal punto di vista operativo, l’esperimento suggerisce che:

1. se la priorità è la **massima precisione**, `exp07b` è la migliore augmentation YOLOv8 finora provata;
2. se la priorità è il **miglior equilibrio complessivo**, `exp08` resta preferibile;
3. se la priorità è la **migliore localizzazione media**, `exp06` grayscale resta ancora leggermente superiore.

---

