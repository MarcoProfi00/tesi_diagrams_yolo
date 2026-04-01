# YOLOv11 — Risultati sperimentali

## Obiettivo

Questo documento raccoglie gli esperimenti svolti con **YOLOv11** sul dataset dei diagrammi elettrici, separandoli dai blocchi YOLOv7 e YOLOv8 per mantenere più ordinato il materiale della tesi.

---

# 1. Setup comune

## Dataset

- **Numero classi:** 32
- **Validation images:** 126
- **Validation instances:** 1625
- **Resize:** 1024x1024
- **Task:** object detection
- **Dataset detect-only:** sì

## Ambiente

- **Framework:** Ultralytics
- **Piattaforma:** Google Colab
- **GPU:** Tesla T4 16 GB
- **Python:** 3.11.13
- **Torch:** 2.6.0+cu124
- **Ultralytics:** 8.4.28

---

# 2. Tabella riassuntiva esperimenti YOLOv11

| Exp ID | Input     | Augmentation   | Epochs | Batch | Precision | Recall | F1-score | mAP@0.5 | mAP@0.5:0.95 | Best epoch | Note                 |
| ------ | --------- | -------------- | -----: | ----: | --------: | -----: | -------: | ------: | -----------: | ---------: | -------------------- |
| exp09  | RGB       | No             |    100 |     4 |    0.9062 | 0.8806 |   0.8932 |  0.9114 |       0.6472 |         70 | Baseline YOLOv11 RGB |
| exp10  | Grayscale | No             |    100 |     4 |    0.9387 | 0.8571 |   0.8960 |  0.9300 |       0.6492 |         78 | GrayScale            |
| exp11  | RGB       | aug_v1         |    100 |     4 |    0.9436 | 0.9004 |   0.9215 |  0.9513 |       0.6552 |         63 | Augmentation Lieve   |
| exp12  | RGB       | aug_v2_compose |    100 |     4 |    0.9201 | 0.8389 |   0.8776 |  0.9146 |       0.6442 |         34 | Compose of diagrams  |
| exp11b | RGB       | aug_v3 strong  |    100 |     4 |    0.9404 | 0.9049 |   0.9223 |  0.9476 |       0.6665 |         97 | Augmentation forte   |

---

# 3. Baseline RGB — exp09

## 3.1 Obiettivo

Valutare le prestazioni di **YOLOv11** sul dataset **RGB originale**, mantenendo una configurazione il più possibile confrontabile con gli esperimenti precedenti su YOLOv8: stessa risoluzione di input, stesso numero di epoche, stesso batch size e stesso validation set.

L’obiettivo è verificare se la nuova famiglia di modelli YOLOv11 possa offrire un miglioramento ulteriore in termini di:

- **precision**
- **recall**
- **F1-score**
- **mAP@0.5**
- **mAP@0.5:0.95**

---

## 3.2 Setup dettagliato

### Exp ID

**exp09_yolo11_rgb_1024_baseline**

### Configurazione

- **Modello:** YOLO11s
- **Framework:** Ultralytics
- **Input:** RGB originale
- **Grayscale:** No
- **Data augmentation aggiuntiva offline:** No
- **Resize:** 1024x1024
- **Epochs:** 100
- **Batch size:** 4
- **Checkpoint principale usato per la valutazione:** `best.pt`
- **Checkpoint periodici:** ogni 5 epoche
- **Resume da checkpoint:** sì, training ripreso da `last.pt` dopo interruzione del runtime

### Hardware / ambiente

- **Piattaforma:** Google Colab
- **GPU:** Tesla T4 16 GB
- **VRAM disponibile:** circa 14913 MiB
- **Python:** 3.11.13
- **Torch:** 2.6.0+cu124
- **Ultralytics:** 8.4.28

### Model summary

- **Layers:** 182
- **Parameters:** 9,440,176
- **GFLOPs:** 21.6

### Dataset usato

- **Validation images:** 126
- **Validation instances:** 1625
- **Numero classi:** 32

---

## 3.3 Metriche finali

> Le metriche sotto riportate fanno riferimento alla **validazione finale del best checkpoint** (`best.pt`).  
> La **best epoch = 70** è stata ricavata da `results.csv` sulla metrica `mAP@0.5:0.95`.

| Metrica                  |      Valore |
| ------------------------ | ----------: |
| Precision                |      0.9062 |
| Recall                   |      0.8806 |
| F1-score                 |      0.8932 |
| mAP@0.5                  |      0.9114 |
| mAP@0.5:0.95             |      0.6472 |
| Best epoch               |          70 |
| F1 massimo (dal grafico) |  circa 0.89 |
| Confidence al F1 massimo | circa 0.409 |
| Speed preprocess         | 18.0 ms/img |
| Speed inference          | 27.9 ms/img |
| Speed postprocess        |  3.4 ms/img |

### Commento sintetico

La baseline **YOLOv11 RGB** mostra prestazioni molto elevate già al primo esperimento completato.  
Le metriche aggregate sono tutte molto forti:

- **precision** superiore a 0.90
- **recall** vicina a 0.88
- **F1-score** vicino a 0.89
- **mAP@0.5** superiore a 0.91
- **mAP@0.5:0.95** superiore a 0.64

Nel complesso, questo esperimento suggerisce che **YOLOv11** rappresenti una baseline molto solida e già estremamente competitiva per il task di object detection sui diagrammi elettrici.

---

## 3.4 Analisi qualitativa del training e della validazione

### Andamento complessivo del training

![Andamento training YOLOv11 RGB baseline](/outputs/yolo11/exp09_yolo11_rgb_1024_baseline/results.png)

**Figura X.** Andamento delle loss di training/validation e delle metriche principali durante il training della baseline YOLOv11 RGB. Le loss di training (`train/box_loss`, `train/cls_loss`, `train/dfl_loss`) diminuiscono in modo regolare e continuo. Le metriche aggregate crescono molto rapidamente nelle prime epoche, poi entrano in una fase di plateau stabile già nella parte centrale del training.

### Distribuzione labels e box

![Distribuzione labels YOLOv11 RGB baseline](/outputs/yolo11/exp09_yolo11_rgb_1024_baseline/labels.jpg)

**Figura X.** Distribuzione delle classi e delle bounding box nel dataset utilizzato per YOLOv11 RGB baseline. Il grafico conferma lo sbilanciamento tra classi già osservato negli esperimenti precedenti e mostra una prevalenza di box relativamente piccole, coerente con la natura dei simboli elettrici presenti nei diagrammi.

### Confusion matrix normalizzata

![Confusion matrix YOLOv11 RGB baseline](/outputs/yolo11/exp09_yolo11_rgb_1024_baseline/confusion_matrix_normalized.png)

**Figura X.** Confusion matrix normalizzata del best checkpoint YOLOv11 RGB. La diagonale principale è molto ben marcata, segnale di una buona separazione tra molte classi. Restano alcuni errori residui sulle classi meno rappresentate e alcuni falsi negativi verso background.

### Precision curve

![Precision curve YOLOv11 RGB baseline](/outputs/yolo11/exp09_yolo11_rgb_1024_baseline/BoxP_curve.png)

**Figura X.** Curva Precision-Confidence. La precisione cresce progressivamente all’aumentare della confidence threshold e raggiunge valori prossimi a **1.00** alle soglie più elevate.

### Recall curve

![Recall curve YOLOv11 RGB baseline](/outputs/yolo11/exp09_yolo11_rgb_1024_baseline/BoxR_curve.png)

**Figura X.** Curva Recall-Confidence. La recall parte da circa **0.93** a confidence quasi nulla e decresce progressivamente, con un calo più marcato alle soglie elevate.

### F1 curve

![F1 curve YOLOv11 RGB baseline](/outputs/yolo11/exp09_yolo11_rgb_1024_baseline/BoxF1_curve.png)

**Figura X.** Curva F1-Confidence. Il miglior compromesso tra precision e recall si osserva a una confidence di circa **0.409**, con **F1 ≈ 0.89**.

### Precision-Recall curve

![PR curve YOLOv11 RGB baseline](/outputs/yolo11/exp09_yolo11_rgb_1024_baseline/BoxPR_curve.png)

**Figura X.** Curva Precision-Recall del best checkpoint YOLOv11 RGB. Il valore globale riportato dal grafico è coerente con **mAP@0.5 ≈ 0.911**.

---

## 3.5 Interpretazione delle curve

Le curve mostrano un comportamento complessivamente molto stabile e coerente con una buona convergenza del training.

### Osservazioni principali

- le loss di training diminuiscono in modo regolare lungo tutto il training;
- `val/box_loss` e `val/cls_loss` diminuiscono rapidamente nelle prime epoche e poi si stabilizzano;
- `val/dfl_loss` mostra un minimo nelle epoche intermedie e una lieve risalita finale;
- **precision**, **recall**, **mAP@0.5** e **mAP@0.5:0.95** crescono molto rapidamente nella prima parte del training;
- il best checkpoint si colloca nella seconda metà del training, ma il plateau delle metriche compare già piuttosto presto.

### Interpretazione

Questo andamento suggerisce che YOLOv11 apprenda rapidamente una rappresentazione utile del problema e raggiunga una qualità di detection elevata già dopo poche decine di epoche. La parte finale del training sembra soprattutto consolidare il risultato, con oscillazioni contenute e senza instabilità evidenti.

---

## 3.6 Punti di forza e criticità

### Punti di forza

- metriche aggregate molto elevate già nella baseline RGB;
- **precision** e **recall** entrambe molto alte;
- **F1-score** molto competitivo;
- **mAP@0.5** superiore a 0.91;
- **mAP@0.5:0.95** superiore a 0.64, segnale di buona qualità media di localizzazione;
- training stabile anche con runtime Colab interrotto e poi ripreso correttamente da `last.pt`;
- buona separazione tra molte classi nella confusion matrix.

### Criticità

- alcune classi rare restano poco stabili;
- classi come **Analog_Meter**, **Antenna** e **Speaker** mostrano ancora metriche inferiori rispetto alle classi più frequenti;
- **Terminal** e alcune classi con molte istanze o contorni più difficili mantengono una localizzazione meno precisa sulla metrica più severa;
- resta presente una quota di falsi negativi verso **background**, visibile anche nella confusion matrix.

---

## 3.7 Conclusione sull’esperimento YOLOv11 RGB baseline

Nel complesso, **YOLOv11 RGB baseline** rappresenta un risultato molto forte già al primo esperimento completato.

Le evidenze principali sono:

- **precision** molto alta;
- **recall** molto alta;
- **F1-score** molto elevato;
- **mAP@0.5** molto elevata;
- **mAP@0.5:0.95** molto elevata anche sulla metrica più severa.

Dal punto di vista operativo, questa configurazione costituisce una base di confronto molto solida per i prossimi esperimenti:

1. **YOLOv11 grayscale**
2. **YOLOv11 con augmentation leggera (`aug_v1`)**
3. **YOLOv11 con augmentation strutturale (`aug_v2_compose`)**
4. **YOLOv11 con augmentation forte (`aug_v3 strong`)**

La conclusione operativa è quindi che, allo stato attuale, **YOLOv11 RGB baseline** merita di essere considerata una delle configurazioni di riferimento più forti dell’intero studio.

---

# 4. Baseline grayscale — exp10

## 4.1 Obiettivo

Valutare le prestazioni di **YOLOv11** sul dataset completamente convertito in **grayscale**, mantenendo invariati modello, split del dataset, numero di epoche, batch size e risoluzione rispetto all’esperimento `exp09` su immagini RGB.

L’obiettivo è verificare se, anche nel caso di YOLOv11, la rimozione dell’informazione cromatica possa:

- aumentare la robustezza del modello sui simboli elettrici;
- migliorare precision e metriche mAP;
- mantenere un buon equilibrio complessivo tra precision e recall;
- favorire una localizzazione mediamente più accurata delle bounding box.

---

## 4.2 Setup dettagliato

### Exp ID

**exp10_yolo11_gray_1024_baseline**

### Configurazione

- **Modello:** YOLO11s
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
- **Python:** 3.12.13
- **Torch:** 2.10.0+cu128
- **Ultralytics:** 8.4.28

### Model summary

- **Layers:** 101 (modello fused in validazione)
- **Parameters:** 9,425,184
- **GFLOPs:** 21.4

### Dataset usato

- **Validation images:** 126
- **Validation instances:** 1625
- **Numero classi:** 32

---

## 4.3 Metriche finali

> Le metriche sotto riportate fanno riferimento alla **validazione finale del best checkpoint** (`best.pt`).  
> In questo blocco, la **best epoch precisa** non è stata ancora estratta dal `results.csv`, quindi per ora viene lasciata come `n.d.`.

| Metrica                  |      Valore |
| ------------------------ | ----------: |
| Precision                |      0.9387 |
| Recall                   |      0.8571 |
| F1-score                 |      0.8960 |
| mAP@0.5                  |      0.9300 |
| mAP@0.5:0.95             |      0.6495 |
| Best epoch               |          78 |
| F1 massimo (dal grafico) |  circa 0.89 |
| Confidence al F1 massimo | circa 0.584 |
| Speed preprocess         |  2.1 ms/img |
| Speed inference          | 22.8 ms/img |
| Speed postprocess        | 13.7 ms/img |

### Commento sintetico

La baseline **YOLOv11 grayscale** mostra un comportamento estremamente competitivo e, sulle metriche aggregate, supera la baseline RGB su:

- **precision**
- **F1-score**
- **mAP@0.5**
- **mAP@0.5:0.95**

L’unica metrica che peggiora rispetto a `exp09` è la **recall**, che cala in modo visibile. Tuttavia il bilancio complessivo resta molto positivo, perché il modello diventa più selettivo e mediamente più accurato nella detection, ottenendo al momento la **migliore mAP@0.5:0.95** tra gli esperimenti YOLOv11 completati finora.

---

## 4.5 Analisi qualitativa del training e della validazione

### Andamento complessivo del training

![Andamento training YOLOv11 grayscale baseline](/outputs/yolo11/exp10_yolo11_gray_1024_baseline/results.png)

**Figura X.** Andamento delle loss di training/validation e delle metriche principali durante il training della baseline YOLOv11 grayscale. Le loss di training (`train/box_loss`, `train/cls_loss`, `train/dfl_loss`) diminuiscono in modo regolare e continuo. Le metriche aggregate crescono molto rapidamente nelle prime epoche e poi si stabilizzano in una fase di plateau piuttosto alta.

### Distribuzione labels e box

![Distribuzione labels YOLOv11 grayscale baseline](/outputs/yolo11/exp10_yolo11_gray_1024_baseline/labels.jpg)

**Figura X.** Distribuzione delle classi e delle bounding box nel dataset grayscale. La distribuzione resta identica a quella del dataset RGB, confermando che il preprocessing modifica solo il dominio visivo e non la composizione semantica del dataset.

### Confusion matrix normalizzata

![Confusion matrix YOLOv11 grayscale baseline](/outputs/yolo11/exp10_yolo11_gray_1024_baseline/confusion_matrix_normalized.png)

**Figura X.** Confusion matrix normalizzata del best checkpoint YOLOv11 grayscale. La diagonale principale è molto ben marcata, segnale di una buona separazione tra classi. Restano alcuni errori residui sulle classi meno frequenti e una quota di falsi negativi verso background.

### Precision curve

![Precision curve YOLOv11 grayscale baseline](/outputs/yolo11/exp10_yolo11_gray_1024_baseline/BoxP_curve.png)

**Figura X.** Curva Precision-Confidence. La precisione cresce all’aumentare della confidence threshold e raggiunge valori prossimi a **1.00** alle soglie più elevate.

### Recall curve

![Recall curve YOLOv11 grayscale baseline](/outputs/yolo11/exp10_yolo11_gray_1024_baseline/BoxR_curve.png)

**Figura X.** Curva Recall-Confidence. La recall parte da circa **0.95** a confidence quasi nulla e decresce progressivamente, con un calo più marcato alle soglie elevate.

### F1 curve

![F1 curve YOLOv11 grayscale baseline](/outputs/yolo11/exp10_yolo11_gray_1024_baseline/BoxF1_curve.png)

**Figura X.** Curva F1-Confidence. Il miglior compromesso tra precision e recall si osserva a una confidence di circa **0.584**, con **F1 ≈ 0.89**.

### Precision-Recall curve

![PR curve YOLOv11 grayscale baseline](/outputs/yolo11/exp10_yolo11_gray_1024_baseline/BoxPR_curve.png)

**Figura X.** Curva Precision-Recall del best checkpoint YOLOv11 grayscale. Il valore globale riportato dal grafico è coerente con **mAP@0.5 ≈ 0.930**.

---

## 4.6 Interpretazione delle curve

Le curve mostrano un comportamento stabile e coerente con una buona convergenza del training.

### Osservazioni principali

- le loss di training diminuiscono in modo regolare;
- `val/box_loss` e `val/cls_loss` diminuiscono rapidamente e poi si stabilizzano;
- `val/dfl_loss` mostra un minimo nelle epoche intermedie e una lieve risalita finale;
- le metriche **precision**, **recall**, **mAP@0.5** e **mAP@0.5:0.95** crescono rapidamente nelle prime epoche;
- il modello entra in plateau senza instabilità marcate nella seconda metà del training.

### Interpretazione

Nel complesso, YOLOv11 grayscale sembra beneficiare della semplificazione del dominio visivo: il modello perde qualcosa in sensibilità pura, ma guadagna in precisione e nella qualità media della localizzazione. Il vantaggio del grayscale emerge quindi soprattutto sul lato della detection più pulita e della mAP complessiva.

---

## 4.7 Punti di forza e criticità

### Punti di forza

- migliore **precision** tra gli esperimenti YOLOv11 completati finora;
- migliore **F1-score** tra gli esperimenti YOLOv11 completati finora;
- migliore **mAP@0.5** tra gli esperimenti YOLOv11 completati finora;
- migliore **mAP@0.5:0.95** tra gli esperimenti YOLOv11 completati finora;
- training stabile;
- buona qualità media della localizzazione;
- forte separazione tra molte classi nella confusion matrix.

### Criticità

- **recall** inferiore rispetto alla baseline RGB;
- alcune classi rare restano instabili;
- classi come **Antenna**, **Connector**, **Speaker** e in parte **Terminal** restano ancora difficili;
- resta presente una quota di errori verso **background**, anche se contenuta.

---

## 4.8 Conclusione sull’esperimento YOLOv11 grayscale baseline

Nel complesso, **YOLOv11 grayscale** rappresenta un risultato molto forte e, allo stato attuale, anche leggermente migliore della baseline RGB sul piano complessivo.

Le evidenze principali sono:

- **precision** più alta rispetto a RGB;
- **F1-score** leggermente migliore;
- **mAP@0.5** migliore;
- **mAP@0.5:0.95** migliore;
- unica vera rinuncia: una **recall** un po’ più bassa.

Dal punto di vista operativo, si possono quindi formulare due conclusioni:

1. se la priorità è **non perdere oggetti reali**, `exp09` RGB resta leggermente migliore grazie alla recall più alta;
2. se la priorità è il **miglior equilibrio complessivo** e la **migliore qualità media di detection/localizzazione**, `exp10` grayscale è al momento la baseline YOLOv11 più promettente.

---

# 5. Esperimenti con augmentation

## 5.1 exp11 — aug_v1

### 5.1.1 Obiettivo

Valutare l’effetto della politica di augmentation **`aug_v1`** anche su **YOLOv11**, mantenendo invariati modello, validation set, risoluzione di input, batch size e numero di epoche rispetto agli altri esperimenti YOLOv11.

L’obiettivo è verificare se una augmentation offline leggera, applicata solo al training set, possa:

- aumentare la robustezza del modello;
- migliorare il compromesso tra precision e recall;
- aumentare le metriche aggregate di detection;
- migliorare anche la qualità media della localizzazione delle bounding box.

---

### 5.1.2 Setup dettagliato

#### Exp ID

**exp11_yolo11_rgb_aug_1024_baseline**

#### Configurazione

- **Modello:** YOLO11s
- **Framework:** Ultralytics
- **Input:** RGB
- **Dataset base:** `rf_yolo_1024_rgb_aug`
- **Augmentation:** `aug_v1` offline sul training set
- **Validation set:** invariato
- **Test set:** invariato
- **Resize:** 1024x1024
- **Epochs:** 100
- **Batch size:** 4
- **Checkpoint principale usato per la valutazione:** `best.pt`
- **Checkpoint periodici:** ogni 5 epoche
- **Resume da checkpoint:** sì, training ripreso da `last.pt` dopo interruzione del runtime

#### Politica di augmentation usata

La variante `aug_v1` corrisponde alla stessa augmentation leggera già usata negli esperimenti precedenti, basata su:

- **rotazione lieve**;
- **piccola traslazione**;
- **lieve scaling**;
- **modesta variazione di luminosità/contrasto**;
- **rumore leggero**;
- **nessun flip**.

L’augmentation è applicata **solo al training set**, mentre validation e test restano invariati per garantire un confronto corretto.

#### Hardware / ambiente

- **Piattaforma:** Google Colab
- **GPU:** Tesla T4 16 GB
- **VRAM disponibile:** circa 14913 MiB
- **Python:** 3.11.13
- **Torch:** 2.6.0+cu124
- **Ultralytics:** 8.4.29

#### Model summary

- **Layers:** 182
- **Parameters:** 9,440,176
- **GFLOPs:** 21.6

#### Dataset usato

- **Train images:** 880
- **Train backgrounds:** 2
- **Validation images:** 126
- **Validation instances:** 1625
- **Numero classi:** 32

---

### 5.1.3 Metriche finali

> Le metriche sotto riportate fanno riferimento alla **validazione finale del best checkpoint** (`best.pt`).  
> La **best epoch = 63** è stata ricavata da `results.csv` sulla metrica `mAP@0.5:0.95`.

| Metrica                  |      Valore |
| ------------------------ | ----------: |
| Precision                |      0.9436 |
| Recall                   |      0.9004 |
| F1-score                 |      0.9215 |
| mAP@0.5                  |      0.9513 |
| mAP@0.5:0.95             |      0.6552 |
| Best epoch               |          63 |
| F1 massimo (dal grafico) |  circa 0.91 |
| Confidence al F1 massimo | circa 0.483 |
| Speed preprocess         |  5.8 ms/img |
| Speed inference          | 28.6 ms/img |
| Speed postprocess        |  5.9 ms/img |

### Commento sintetico

L’esperimento **YOLOv11 RGB + aug_v1** mostra il miglior risultato complessivo tra tutti gli esperimenti YOLOv11 completati finora.

Rispetto alle due baseline già testate:

- aumenta ulteriormente la **precision**;
- migliora in modo netto la **recall**;
- ottiene il miglior **F1-score**;
- ottiene la miglior **mAP@0.5**;
- ottiene anche la miglior **mAP@0.5:0.95**.

In altre parole, `aug_v1` non migliora solo una singola metrica, ma produce il miglior equilibrio complessivo tra detection e localizzazione.

---


### 5.1.6 Analisi qualitativa del training e della validazione

#### Andamento complessivo del training

![Andamento training YOLOv11 RGB + aug_v1](/outputs/yolo11/exp11_yolo11_rgb_aug_1024_baseline/results.png)

**Figura X.** Andamento delle loss di training/validation e delle metriche principali durante il training di YOLOv11 con `aug_v1`. Le loss di training diminuiscono in modo regolare lungo tutto il training, mentre precision, recall e metriche mAP crescono rapidamente già nelle prime epoche e si stabilizzano su valori molto alti nella seconda metà del training.

#### Distribuzione labels e box

![Distribuzione labels YOLOv11 RGB + aug_v1](/outputs/yolo11/exp11_yolo11_rgb_aug_1024_baseline/labels.jpg)

**Figura X.** Distribuzione delle classi e delle bounding box nel dataset con augmentation `aug_v1`. Il numero di immagini di training risulta raddoppiato rispetto alla baseline RGB, mentre validation e test restano invariati.

#### Confusion matrix normalizzata

![Confusion matrix YOLOv11 RGB + aug_v1](/outputs/yolo11/exp11_yolo11_rgb_aug_1024_baseline/confusion_matrix_normalized.png)

**Figura X.** Confusion matrix normalizzata del best checkpoint YOLOv11 con `aug_v1`. La diagonale principale è molto marcata e conferma una separazione molto buona tra la maggior parte delle classi, con riduzione degli errori complessivi rispetto alle baseline.

#### Precision curve

![Precision curve YOLOv11 RGB + aug_v1](/outputs/yolo11/exp11_yolo11_rgb_aug_1024_baseline/BoxP_curve.png)

**Figura X.** Curva Precision-Confidence. La precisione cresce progressivamente al crescere della soglia di confidence e raggiunge valori prossimi a **1.00** alle soglie più alte.

#### Recall curve

![Recall curve YOLOv11 RGB + aug_v1](/outputs/yolo11/exp11_yolo11_rgb_aug_1024_baseline/BoxR_curve.png)

**Figura X.** Curva Recall-Confidence. La recall parte da circa **0.96** a confidence quasi nulla e decresce gradualmente all’aumentare della soglia.

#### F1 curve

![F1 curve YOLOv11 RGB + aug_v1](/outputs/yolo11/exp11_yolo11_rgb_aug_1024_baseline/BoxF1_curve.png)

**Figura X.** Curva F1-Confidence. Il miglior compromesso tra precision e recall si osserva a una confidence di circa **0.483**, con **F1 ≈ 0.91**.

#### Precision-Recall curve

![PR curve YOLOv11 RGB + aug_v1](/outputs/yolo11/exp11_yolo11_rgb_aug_1024_baseline/BoxPR_curve.png)

**Figura X.** Curva Precision-Recall del best checkpoint YOLOv11 con `aug_v1`. Il valore globale riportato dal grafico è coerente con **mAP@0.5 ≈ 0.951**.

---

### 5.1.7 Interpretazione delle curve

#### Osservazioni principali

- le loss di training diminuiscono in modo regolare;
- `val/box_loss` e `val/cls_loss` diminuiscono rapidamente nelle prime epoche e poi si stabilizzano;
- `val/dfl_loss` mostra una crescita nella seconda metà del training, ma senza compromettere il miglioramento delle metriche aggregate;
- precision, recall, F1-score e metriche mAP crescono molto rapidamente nelle prime epoche;
- il best checkpoint si colloca attorno alla metà del training, segnalando che il modello raggiunge presto una configurazione molto forte.

#### Interpretazione

Nel complesso, le curve suggeriscono che `aug_v1` aiuti YOLOv11 a generalizzare meglio senza introdurre instabilità evidenti. Il modello migliora sia la capacità di trovare gli oggetti reali sia la qualità media della detection, ottenendo il miglior compromesso complessivo tra tutte le configurazioni testate finora.

---

### 5.1.8 Punti di forza e criticità

#### Punti di forza

- migliore **precision** tra gli esperimenti YOLOv11 completati finora;
- migliore **recall** tra gli esperimenti YOLOv11 completati finora;
- migliore **F1-score** tra gli esperimenti YOLOv11 completati finora;
- migliore **mAP@0.5** tra gli esperimenti YOLOv11 completati finora;
- migliore **mAP@0.5:0.95** tra gli esperimenti YOLOv11 completati finora;
- training stabile anche con resume da checkpoint;
- ottimo equilibrio complessivo tra sensibilità e precisione.

#### Criticità

- alcune classi rare restano instabili;
- classi come **Analog_Meter** e **Antenna** restano ancora difficili;
- **Terminal** continua a mostrare una localizzazione meno precisa rispetto alle classi più semplici;
- la `val/dfl_loss` cresce nella seconda parte del training, anche se il risultato finale resta ottimo.

---

### 5.1.9 Conclusione sull’esperimento YOLOv11 RGB + aug_v1

Nel complesso, **YOLOv11 + aug_v1** è, allo stato attuale, la configurazione più forte dell’intero blocco YOLOv11.

Le evidenze principali sono:

- migliore **precision**;
- migliore **recall**;
- migliore **F1-score**;
- migliore **mAP@0.5**;
- migliore **mAP@0.5:0.95**.

Dal punto di vista operativo, questo esperimento suggerisce che una augmentation offline leggera e controllata sia estremamente efficace anche su YOLOv11. Al momento, `exp11` rappresenta quindi il nuovo riferimento interno per i successivi confronti con `aug_v2_compose` e `aug_v3 strong`.

## 5.2 exp12 — aug_v2_compose

### 5.2.1 Obiettivo

Valutare l’effetto della politica di augmentation **`aug_v2_compose`** su **YOLOv11**, mantenendo invariati modello, validation set, risoluzione di input, batch size e numero di epoche rispetto agli altri esperimenti YOLOv11.

L’obiettivo è verificare se una augmentation più strutturale, basata sulla composizione artificiale di diagrammi, possa:

- aumentare la variabilità del training set;
- migliorare la robustezza del modello;
- aumentare precision, recall e metriche mAP;
- migliorare la generalizzazione rispetto a baseline e augmentation leggera.

---

### 5.2.2 Setup dettagliato

#### Exp ID

**exp12_yolo11_rgb_aug_v2_compose**

#### Configurazione

- **Modello:** YOLO11s
- **Framework:** Ultralytics
- **Input:** RGB
- **Dataset base:** `rf_yolo_1024_rgb_aug_v2_compose`
- **Augmentation:** `aug_v2_compose` offline sul training set
- **Validation set:** invariato
- **Test set:** invariato
- **Resize:** 1024x1024
- **Epochs:** 100
- **Batch size:** 4
- **Checkpoint principale usato per la valutazione:** `best.pt`
- **Checkpoint periodici:** ogni 5 epoche
- **Resume da checkpoint:** sì, training ripreso da `last.pt` dopo interruzione del runtime

#### Politica di augmentation usata

La variante `aug_v2_compose` corrisponde alla generazione di nuove immagini tramite **composizione artificiale di diagrammi**, con l’obiettivo di creare configurazioni più varie rispetto al dataset originale.

In questo caso, il training set non viene semplicemente raddoppiato come in `aug_v1`, ma viene trasformato in un dataset con distribuzione spaziale differente e con nuove combinazioni di simboli.

#### Hardware / ambiente

- **Piattaforma:** Google Colab
- **GPU:** Tesla T4 16 GB
- **VRAM disponibile:** circa 14913 MiB
- **Python:** 3.12.13
- **Torch:** 2.10.0+cu128
- **Ultralytics:** 8.4.29

#### Model summary

- **Layers:** 182
- **Parameters:** 9,440,176
- **GFLOPs:** 21.6

#### Dataset usato

- **Train images:** 726
- **Train backgrounds:** 1
- **Validation images:** 126
- **Validation instances:** 1625
- **Numero classi:** 32

---

### 5.2.3 Metriche finali

> Le metriche sotto riportate fanno riferimento alla **validazione finale del best checkpoint** (`best.pt`).  
> La **best epoch = 34** è stata ricavata da `results.csv` sulla metrica `mAP@0.5:0.95`.

| Metrica                  |      Valore |
| ------------------------ | ----------: |
| Precision                |      0.9201 |
| Recall                   |      0.8389 |
| F1-score                 |      0.8776 |
| mAP@0.5                  |      0.9146 |
| mAP@0.5:0.95             |      0.6442 |
| Best epoch               |          34 |
| F1 massimo (dal grafico) |  circa 0.86 |
| Confidence al F1 massimo | circa 0.529 |
| Speed preprocess         | 14.5 ms/img |
| Speed inference          | 29.2 ms/img |
| Speed postprocess        |  5.2 ms/img |

### Commento sintetico

L’esperimento **YOLOv11 RGB + aug_v2_compose** non conferma il miglioramento già osservato con `aug_v1`.

Rispetto ai risultati migliori ottenuti finora:

- la **precision** resta buona;
- la **recall** cala;
- il **F1-score** peggiora;
- **mAP@0.5** e **mAP@0.5:0.95** risultano inferiori rispetto a `exp11`;
- il risultato complessivo resta solo leggermente sopra o molto vicino alla baseline RGB, ma sotto alla baseline grayscale e soprattutto sotto `aug_v1`.

In sintesi, la composizione artificiale dei diagrammi non sembra portare, in questa configurazione, un vantaggio reale rispetto alle alternative già provate.

---

### 5.2.4 Confronto con exp11 aug_v1

| Metrica      | exp11 aug_v1 | exp12 aug_v2_compose | Differenza |
| ------------ | -----------: | -------------------: | ---------: |
| Precision    |       0.9438 |               0.9198 |    -0.0240 |
| Recall       |       0.9001 |               0.8395 |    -0.0606 |
| F1-score     |       0.9214 |               0.8778 |    -0.0436 |
| mAP@0.5      |       0.9508 |               0.9149 |    -0.0359 |
| mAP@0.5:0.95 |       0.6574 |               0.6447 |    -0.0127 |

### Interpretazione rispetto a exp11

Rispetto a `aug_v1`, la variante `aug_v2_compose` peggiora tutte le metriche aggregate. Il calo più evidente è sulla **recall** e, di conseguenza, anche su **F1-score** e **mAP@0.5**. Questo suggerisce che la composizione artificiale dei diagrammi introduca una distribuzione meno favorevole alla generalizzazione rispetto alla augmentation leggera.

---

### 5.2.5 Confronto con exp10 grayscale baseline

| Metrica      | exp10 Gray | exp12 aug_v2_compose | Differenza |
| ------------ | ---------: | -------------------: | ---------: |
| Precision    |     0.9391 |               0.9198 |    -0.0193 |
| Recall       |     0.8570 |               0.8395 |    -0.0175 |
| F1-score     |     0.8962 |               0.8778 |    -0.0184 |
| mAP@0.5      |     0.9297 |               0.9149 |    -0.0148 |
| mAP@0.5:0.95 |     0.6483 |               0.6447 |    -0.0036 |

### Interpretazione rispetto a exp10

Rispetto alla baseline grayscale, `exp12` è peggiore su tutte le metriche aggregate. Questo indica che, almeno nel caso di YOLOv11, la sola conversione in grayscale è più efficace della composizione artificiale dei diagrammi.

---

### 5.2.6 Confronto con exp09 RGB baseline

| Metrica      | exp09 RGB | exp12 aug_v2_compose | Differenza |
| ------------ | --------: | -------------------: | ---------: |
| Precision    |    0.9063 |               0.9198 |    +0.0135 |
| Recall       |    0.8806 |               0.8395 |    -0.0411 |
| F1-score     |    0.8932 |               0.8778 |    -0.0154 |
| mAP@0.5      |    0.9114 |               0.9149 |    +0.0035 |
| mAP@0.5:0.95 |    0.6430 |               0.6447 |    +0.0017 |

### Interpretazione rispetto a exp09

Rispetto alla baseline RGB, `exp12` migliora leggermente **precision** e metriche **mAP**, ma perde in modo evidente sulla **recall**, e questo porta anche a un **F1-score** inferiore. Nel complesso, il vantaggio rispetto a `exp09` è minimo e non abbastanza forte da giustificare la complessità maggiore della pipeline `compose`.

---

### 5.2.7 Analisi qualitativa del training e della validazione

#### Andamento complessivo del training

![Andamento training YOLOv11 RGB + aug_v2_compose](/outputs/yolo11/exp12_yolo11_rgb_aug_v2_compose/results.png)

**Figura X.** Andamento delle loss di training/validation e delle metriche principali durante il training di YOLOv11 con `aug_v2_compose`. Le loss di training diminuiscono in modo regolare, mentre le metriche aggregate crescono rapidamente nelle prime epoche e poi si stabilizzano su un plateau inferiore rispetto a `aug_v1`.

#### Distribuzione labels e box

![Distribuzione labels YOLOv11 RGB + aug_v2_compose](/outputs/yolo11/exp12_yolo11_rgb_aug_v2_compose/labels.jpg)

**Figura X.** Distribuzione delle classi e delle bounding box nel dataset con augmentation `aug_v2_compose`. Rispetto alle altre varianti, il grafico evidenzia una distribuzione spaziale meno uniforme, con maggiore concentrazione delle box in una fascia centrale dell’immagine.

#### Confusion matrix normalizzata

![Confusion matrix YOLOv11 RGB + aug_v2_compose](/outputs/yolo11/exp12_yolo11_rgb_aug_v2_compose/confusion_matrix_normalized.png)

**Figura X.** Confusion matrix normalizzata del best checkpoint YOLOv11 con `aug_v2_compose`. La diagonale principale resta marcata, ma si osservano più errori residui e più falsi negativi verso background rispetto a `exp11`.

#### Precision curve

![Precision curve YOLOv11 RGB + aug_v2_compose](/outputs/yolo11/exp12_yolo11_rgb_aug_v2_compose/BoxP_curve.png)

**Figura X.** Curva Precision-Confidence. La precisione cresce progressivamente con la confidence threshold e raggiunge valori prossimi a **1.00** alle soglie più alte.

#### Recall curve

![Recall curve YOLOv11 RGB + aug_v2_compose](/outputs/yolo11/exp12_yolo11_rgb_aug_v2_compose/BoxR_curve.png)

**Figura X.** Curva Recall-Confidence. La recall parte da circa **0.95** a confidence quasi nulla e decresce progressivamente all’aumentare della soglia.

#### F1 curve

![F1 curve YOLOv11 RGB + aug_v2_compose](/outputs/yolo11/exp12_yolo11_rgb_aug_v2_compose/BoxF1_curve.png)

**Figura X.** Curva F1-Confidence. Il miglior compromesso tra precision e recall si osserva a una confidence di circa **0.529**, con **F1 ≈ 0.86**.

#### Precision-Recall curve

![PR curve YOLOv11 RGB + aug_v2_compose](/outputs/yolo11/exp12_yolo11_rgb_aug_v2_compose/BoxPR_curve.png)

**Figura X.** Curva Precision-Recall del best checkpoint YOLOv11 con `aug_v2_compose`. Il valore globale riportato dal grafico è coerente con **mAP@0.5 ≈ 0.915**.

---

### 5.2.8 Interpretazione delle curve

#### Osservazioni principali

- le loss di training diminuiscono in modo regolare;
- `val/box_loss` e `val/cls_loss` scendono rapidamente nelle prime epoche e poi si stabilizzano;
- `val/dfl_loss` mostra una crescita progressiva nella seconda parte del training;
- le metriche aggregate migliorano rapidamente all’inizio, ma poi si fermano su un plateau inferiore rispetto a `aug_v1`;
- il best checkpoint arriva relativamente presto, alla **epoch 34**.

#### Interpretazione

Nel complesso, le curve suggeriscono che `aug_v2_compose` non riesca a trasformarsi in un vantaggio reale per YOLOv11. Il modello converge, ma la qualità finale della detection non supera le configurazioni già disponibili e il beneficio della composizione artificiale appare limitato.

---

### 5.2.9 Punti di forza e criticità

#### Punti di forza

- precision buona e superiore alla baseline RGB;
- mAP@0.5 e mAP@0.5:0.95 leggermente superiori alla baseline RGB;
- training stabile anche con resume da checkpoint;
- buona separazione tra molte classi frequenti.

#### Criticità

- peggiore di `exp11` su tutte le metriche aggregate;
- peggiore anche di `exp10` su tutte le metriche aggregate;
- recall inferiore sia a `exp09` sia a `exp11`;
- **F1-score** inferiore anche alla baseline RGB;
- classi rare come **Analog_Meter** e **Antenna** restano molto difficili;
- la distribuzione spaziale artificiale introdotta dal compose potrebbe aver reso il training meno naturale.

---

### 5.2.10 Conclusione sull’esperimento YOLOv11 RGB + aug_v2_compose

Nel complesso, **YOLOv11 + aug_v2_compose** non rappresenta un miglioramento convincente.

Le evidenze principali sono:

- risultato inferiore a `exp11` su tutte le metriche principali;
- risultato inferiore a `exp10` su tutte le metriche principali;
- risultato solo marginalmente migliore o molto vicino a `exp09` su alcune metriche, ma con recall e F1-score peggiori.

Dal punto di vista operativo, questa variante **non sembra conveniente** come configurazione di riferimento. Allo stato attuale, `exp12` va considerato un esperimento utile per analizzare il comportamento del compose, ma non competitivo rispetto alle configurazioni migliori già ottenute.

## 5.3 exp11b — aug_v3 strong

### 5.3.1 Obiettivo

Valutare l’effetto della politica di augmentation **`aug_v3 strong`** su **YOLOv11**, mantenendo invariati modello, validation set, risoluzione di input, batch size e numero di epoche rispetto agli altri esperimenti YOLOv11.

L’obiettivo è verificare se una augmentation offline più aggressiva rispetto a `aug_v1` possa:

- aumentare ulteriormente la robustezza del modello;
- migliorare recall e F1-score;
- consolidare la qualità media della localizzazione;
- superare il miglior risultato finora ottenuto con `exp11`.

---

### 5.3.2 Setup dettagliato

#### Exp ID

**exp11b_yolo11_rgb_aug_strong_v3**

#### Configurazione

- **Modello:** YOLO11s
- **Framework:** Ultralytics
- **Input:** RGB
- **Dataset base:** `rf_yolo_1024_rgb_aug_strong_v3`
- **Augmentation:** `aug_v3 strong` offline sul training set
- **Validation set:** invariato
- **Test set:** invariato
- **Resize:** 1024x1024
- **Epochs:** 100
- **Batch size:** 4
- **Checkpoint principale usato per la valutazione:** `best.pt`

#### Politica di augmentation usata

La variante `aug_v3 strong` corrisponde alla versione **forte** della pipeline di augmentation offline.

Rispetto a `aug_v1`, introduce una variabilità più marcata nel training set, con l’obiettivo di aumentare la robustezza del modello e la capacità di generalizzazione, lasciando invariati validation e test set.

#### Hardware / ambiente

- **Piattaforma:** Google Colab
- **GPU:** Tesla T4 16 GB
- **VRAM disponibile:** circa 14913 MiB
- **Python:** 3.12.13
- **Torch:** 2.10.0+cu128
- **Ultralytics:** 8.4.30

#### Model summary

- **Layers:** 182
- **Parameters:** 9,440,176
- **GFLOPs:** 21.6

#### Dataset usato

- **Train images:** 880
- **Train backgrounds:** 2
- **Validation images:** 126
- **Validation instances:** 1625
- **Numero classi:** 32

---

### 5.3.3 Metriche finali

> Le metriche sotto riportate fanno riferimento alla **validazione finale del best checkpoint** (`best.pt`).  
> La **best epoch = 97** è stata ricavata dal log di training sulla metrica `mAP@0.5:0.95`.

| Metrica                  |      Valore |
| ------------------------ | ----------: |
| Precision                |      0.9404 |
| Recall                   |      0.9049 |
| F1-score                 |      0.9223 |
| mAP@0.5                  |      0.9476 |
| mAP@0.5:0.95             |      0.6665 |
| Best epoch               |          97 |
| F1 massimo (dal grafico) |  circa 0.92 |
| Confidence al F1 massimo | circa 0.467 |
| Speed preprocess         | 10.3 ms/img |
| Speed inference          | 26.5 ms/img |
| Speed postprocess        |  4.4 ms/img |

### Commento sintetico

L’esperimento **YOLOv11 RGB + aug_v3 strong** è il nuovo risultato più forte sul piano del compromesso complessivo.

Rispetto a `exp11`:

- la **precision** cala leggermente;
- la **recall** migliora;
- il **F1-score** migliora, anche se di poco;
- **mAP@0.5** resta leggermente inferiore a `exp11`;
- **mAP@0.5:0.95** diventa invece la migliore tra tutti gli esperimenti YOLOv11 completati.

In sintesi, `aug_v3 strong` sembra produrre un modello leggermente più robusto e migliore sulla metrica più severa, pur senza dominare su tutte le metriche.

---


### 5.3.7 Analisi qualitativa del training e della validazione

#### Andamento complessivo del training

![Andamento training YOLOv11 RGB + aug_v3 strong](/outputs/yolo11/exp11b_yolo11_rgb_aug_strong_v3/results.png)

**Figura X.** Andamento delle loss di training/validation e delle metriche principali durante il training di YOLOv11 con `aug_v3 strong`. Le loss di training diminuiscono regolarmente, mentre le metriche aggregate crescono rapidamente nelle prime epoche e si stabilizzano su un plateau molto alto nella seconda metà del training.

#### Distribuzione labels e box

![Distribuzione labels YOLOv11 RGB + aug_v3 strong](/outputs/yolo11/exp11b_yolo11_rgb_aug_strong_v3/labels.jpg)

**Figura X.** Distribuzione delle classi e delle bounding box nel dataset con augmentation `aug_v3 strong`. Il dataset di training mantiene la stessa numerosità di `aug_v1`, ma mostra una maggiore variabilità nelle proporzioni delle bounding box, coerente con una pipeline di augmentation più aggressiva.

#### Confusion matrix normalizzata

![Confusion matrix YOLOv11 RGB + aug_v3 strong](/outputs/yolo11/exp11b_yolo11_rgb_aug_strong_v3/confusion_matrix_normalized.png)

**Figura X.** Confusion matrix normalizzata del best checkpoint YOLOv11 con `aug_v3 strong`. La diagonale principale resta molto marcata e gli errori verso background risultano contenuti, segnale di una buona robustezza complessiva.

#### Precision curve

![Precision curve YOLOv11 RGB + aug_v3 strong](/outputs/yolo11/exp11b_yolo11_rgb_aug_strong_v3/BoxP_curve.png)

**Figura X.** Curva Precision-Confidence. La precisione cresce progressivamente al crescere della confidence threshold e raggiunge valori prossimi a **1.00** alle soglie più alte.

#### Recall curve

![Recall curve YOLOv11 RGB + aug_v3 strong](/outputs/yolo11/exp11b_yolo11_rgb_aug_strong_v3/BoxR_curve.png)

**Figura X.** Curva Recall-Confidence. La recall parte da circa **0.96** a confidence quasi nulla e decresce progressivamente all’aumentare della soglia.

#### F1 curve

![F1 curve YOLOv11 RGB + aug_v3 strong](/outputs/yolo11/exp11b_yolo11_rgb_aug_strong_v3/BoxF1_curve.png)

**Figura X.** Curva F1-Confidence. Il miglior compromesso tra precision e recall si osserva a una confidence di circa **0.467**, con **F1 ≈ 0.92**.

#### Precision-Recall curve

![PR curve YOLOv11 RGB + aug_v3 strong](/outputs/yolo11/exp11b_yolo11_rgb_aug_strong_v3/BoxPR_curve.png)

**Figura X.** Curva Precision-Recall del best checkpoint YOLOv11 con `aug_v3 strong`. Il valore globale riportato dal grafico è coerente con **mAP@0.5 ≈ 0.948**.

---

### 5.3.8 Interpretazione delle curve

#### Osservazioni principali

- le loss di training diminuiscono in modo regolare;
- `val/box_loss` e `val/cls_loss` scendono rapidamente nelle prime epoche e poi si stabilizzano;
- `val/dfl_loss` mostra il consueto minimo nelle epoche intermedie e una lieve risalita finale;
- le metriche aggregate crescono molto rapidamente e restano su un plateau alto e stabile;
- il best checkpoint arriva tardi, alla **epoch 97**, segnale che il modello continua a rifinire il risultato fino alla fine del training.

#### Interpretazione

Nel complesso, le curve suggeriscono che `aug_v3 strong` non introduca instabilità e permetta anzi di consolidare un risultato molto forte fino alla parte finale del training. Il miglioramento rispetto a `exp11` non è enorme, ma appare coerente soprattutto sulla metrica più severa `mAP@0.5:0.95`.

---

### 5.3.9 Punti di forza e criticità

#### Punti di forza

- migliore **recall** tra gli esperimenti YOLOv11 completati;
- migliore **F1-score** tra gli esperimenti YOLOv11 completati;
- migliore **mAP@0.5:0.95** tra gli esperimenti YOLOv11 completati;
- training stabile;
- buona robustezza complessiva;
- miglioramento evidente rispetto a baseline RGB, baseline grayscale e `aug_v2_compose`.

#### Criticità

- **precision** leggermente inferiore a `exp11`;
- **mAP@0.5** leggermente inferiore a `exp11`;
- alcune classi rare, come **Antenna**, restano ancora instabili;
- classi come **Terminal** e in parte **Switch** continuano a mostrare margini di miglioramento sulla localizzazione.

---

### 5.3.10 Conclusione sull’esperimento YOLOv11 RGB + aug_v3 strong

Nel complesso, **YOLOv11 + aug_v3 strong** è il nuovo candidato più interessante del blocco YOLOv11 se si considera il compromesso globale.

Le evidenze principali sono:

- migliore **recall**;
- migliore **F1-score**;
- migliore **mAP@0.5:0.95**;
- risultato molto vicino a `exp11` anche su **precision** e **mAP@0.5**.

Dal punto di vista operativo, la conclusione è che `exp11b` e `exp11` siano le due configurazioni migliori, ma con una leggera preferenza per `exp11b` se si vuole privilegiare la metrica più severa e il bilancio complessivo tra detection e localizzazione.

---

