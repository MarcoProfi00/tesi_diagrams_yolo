# YOLOv7 — Risultati sperimentali

## Obiettivo

Questo documento raccoglie **solo** gli esperimenti eseguiti con **YOLOv7** sul dataset dei diagrammi elettrici, così da separare in modo chiaro:

- baseline
- preprocessing grayscale
- augmentation
- confronto interno alla famiglia YOLOv7

---

# 1. Setup comune

## Dataset

- **Numero immagini totali:** 628
- **Classi:** 32
- **Split:** train 70%, validation 20%, test 10%
- **Resize:** 1024x1024
- **Formato annotazioni:** YOLO
- **Task:** object detection con bounding box

## Ambiente

- **Piattaforma:** Google Colab
- **GPU:** Tesla T4 16 GB
- **Python:** 3.11.13
- **Torch:** 2.6.0+cu124

## Regola metodologica

Gli esperimenti YOLOv7 sono stati costruiti cambiando **una sola variabile alla volta**:

1. baseline RGB
2. grayscale
3. augmentation leggera
4. augmentation compose
5. augmentation strong

---

# 2. Tabella riassuntiva esperimenti YOLOv7

| Exp ID | Input     | Augmentation   | Epochs | Batch | Precision | Recall | F1-score | mAP@0.5 | mAP@0.5:0.95 | Best epoch | Note                            |
| ------ | --------- | -------------- | -----: | ----: | --------: | -----: | -------: | ------: | -----------: | ---------: | ------------------------------- |
| exp01  | RGB       | No             |    100 |     4 |    0.8945 | 0.7935 |   0.8410 |  0.8245 |       0.5702 |         87 | Baseline RGB                    |
| exp02  | Grayscale | No             |    100 |     4 |    0.8864 | 0.7657 |   0.8216 |  0.8272 |       0.5765 |         93 | Lieve vantaggio su mAP@0.5:0.95 |
| exp03  | RGB       | aug_v1         |    100 |     4 |    0.8791 | 0.8563 |   0.8676 |  0.8836 |       0.5928 |         69 | Variante più equilibrata        |
| exp04  | RGB       | aug_v2_compose |    100 |     4 |    0.8443 | 0.8481 |   0.8462 |  0.8587 |       0.5832 |         74 | Composizione di diagrammi       |
| exp03b | RGB       | aug_v3 strong  |    100 |     4 |    0.8568 | 0.8854 |   0.8709 |  0.8972 |       0.6059 |         97 | Miglior recall e migliori mAP   |

---

# 3. Baseline RGB — exp01

## Metriche finali

| Metrica           | Valore |
| ----------------- | -----: |
| Precision         | 0.8945 |
| Recall            | 0.7935 |
| F1-score          | 0.8410 |
| mAP@0.5           | 0.8245 |
| mAP@0.5:0.95      | 0.5702 |
| Best epoch        |     87 |

## Sintesi

La baseline YOLOv7 RGB mostra un comportamento stabile e rappresenta il riferimento iniziale per tutti i confronti successivi. La precisione è alta, mentre la recall è più contenuta.

# 4. Analisi qualitativa della baseline

## 4.1 Osservazioni generali

- La confusion matrix mostra una diagonale principale ben marcata, segnale di una buona separazione tra molte classi.
- Gli errori residui sembrano concentrarsi soprattutto:
  - sulle classi con poche istanze;
  - sui falsi negativi verso background;
  - su alcune classi graficamente simili o poco rappresentate.
- Le classi più frequenti risultano in generale più stabili.
- Le classi rare richiederanno particolare attenzione nei prossimi esperimenti, soprattutto con grayscale e augmentation.

## 4.2 Curve di training e validazione

### Andamento complessivo del training

![Andamento training YOLOv7 RGB](/outputs/yolo7/exp01_yolov7_rgb_1024_baseline/exp01_yolov7_rgb_1024_baseline/results.png)

**Figura X.** Andamento delle loss di training/validation e delle metriche principali durante l’addestramento della baseline YOLOv7 RGB. Le loss di training (`box`, `objectness`, `classification`) e di validation diminuiscono progressivamente, mentre precision, recall e mAP aumentano fino a raggiungere un plateau nelle epoche finali. Questo comportamento indica una convergenza stabile.

### Confusion matrix

![Confusion matrix YOLOv7 RGB](/outputs/yolo7/exp01_yolov7_rgb_1024_baseline/exp01_yolov7_rgb_1024_baseline/confusion_matrix.png)

**Figura X.** Confusion matrix normalizzata della baseline YOLOv7 RGB sul validation set. La diagonale dominante suggerisce una buona capacità discriminativa del modello. Gli errori residui sono concentrati soprattutto nelle classi meno rappresentate e in alcuni falsi negativi verso background.

### Precision curve

![Precision curve YOLOv7 RGB](/outputs/yolo7/exp01_yolov7_rgb_1024_baseline/exp01_yolov7_rgb_1024_baseline/P_curve.png)

**Figura X.** Precision in funzione della confidence threshold.

### Recall curve

![Recall curve YOLOv7 RGB](/outputs/yolo7/exp01_yolov7_rgb_1024_baseline/exp01_yolov7_rgb_1024_baseline/R_curve.png)

**Figura X.** Recall in funzione della confidence threshold.

### F1 curve

![F1 curve YOLOv7 RGB](/outputs/yolo7/exp01_yolov7_rgb_1024_baseline/exp01_yolov7_rgb_1024_baseline/F1_curve.png)

**Figura X.** Curva F1-score in funzione della confidence threshold. La curva F1 evidenzia il miglior compromesso tra precision e recall a una confidence threshold intermedia, utile per scegliere la soglia operativa in fase di inferenza.

### Precision-Recall curve

![PR curve YOLOv7 RGB](/outputs/yolo7/exp01_yolov7_rgb_1024_baseline/exp01_yolov7_rgb_1024_baseline/PR_curve.png)

**Figura X.** Curva Precision-Recall della baseline YOLOv7 RGB. La curva mostra buone prestazioni complessive del modello, con un valore globale di mAP@0.5 pari a circa 0.826.

## 4.3 Interpretazione delle curve

L’andamento delle curve di training mostra un comportamento complessivamente regolare e coerente con un processo di apprendimento stabile.

### Osservazioni principali

- **Box loss**, **objectness loss** e **classification loss** sul training diminuiscono progressivamente nel corso delle epoche.
- Anche le loss di validazione mostrano una tendenza generale alla diminuzione, senza oscillazioni anomale o divergenze evidenti.
- **Precision**, **Recall**, **mAP@0.5** e **mAP@0.5:0.95** crescono in modo progressivo durante il training.
- Le metriche sembrano stabilizzarsi nelle ultime epoche, suggerendo un avvicinamento alla convergenza.

## 4.4 Punti di forza e criticità

### Punti di forza

- buona capacità di rilevare correttamente molte classi frequenti;
- precisione complessiva elevata;
- buona separazione tra numerose classi nella confusion matrix;
- training stabile e regolare;
- ottime prestazioni su diverse classi ben rappresentate e visivamente distintive.

### Criticità

- classi rare con pochi esempi (`Analog_Meter`, `Antenna`, `Connector`, `Speaker`);
- classi con localizzazione ancora migliorabile (`Capacitor`, `Terminal`, `LED`, `Voltage_Source`);
- presenza di falsi negativi verso background, segnale che alcuni simboli non vengono rilevati;
- probabile impatto della dimensione ridotta di alcuni simboli e della somiglianza tra classi.

---

# 5. Baseline grayscale — exp02

## Metriche finali

| Metrica           | Valore |
| ----------------- | -----: |
| Precision         | 0.8864 |
| Recall            | 0.7657 |
| F1-score          | 0.8216 |
| mAP@0.5           | 0.8272 |
| mAP@0.5:0.95      | 0.5765 |
| Best epoch        |     93 |

## Sintesi

Il grayscale non migliora il quadro complessivo rispetto alla baseline RGB, ma ottiene un leggero vantaggio sulla metrica più severa **mAP@0.5:0.95**.


## 5.2 Analisi qualitativa del training grayscale

### Andamento complessivo del training

![Andamento training YOLOv7 grayscale](/outputs/yolo7/exp02_yolov7_greyscale_1024_baseline/results.png)

**Figura X.** Andamento delle loss di training/validation e delle metriche principali per YOLOv7 su dataset grayscale. Le loss di box e classification diminuiscono in modo regolare; precision, recall e mAP crescono progressivamente fino a un plateau nelle epoche finali. Si osserva invece una crescita della `val objectness loss`, che non impedisce tuttavia il miglioramento delle metriche aggregate.

### Confusion matrix

![Confusion matrix YOLOv7 grayscale](/outputs/yolo7/exp02_yolov7_greyscale_1024_baseline/confusion_matrix.png)

**Figura X.** Confusion matrix normalizzata del modello grayscale. La diagonale principale rimane ben marcata, segno che molte classi continuano a essere separate correttamente. Persistono però falsi negativi verso background distribuiti su più classi, in particolare tra quelle rare o con simboli più piccoli.

### Precision curve

![Precision curve YOLOv7 grayscale](/outputs/yolo7/exp02_yolov7_greyscale_1024_baseline/P_curve.png)

**Figura X.** Precision in funzione della confidence threshold. La curva mostra una precisione crescente all'aumentare della soglia e raggiunge il valore massimo di circa **1.00** attorno a confidence **0.789**, ma a costo di una forte riduzione della recall.

### Recall curve

![Recall curve YOLOv7 grayscale](/outputs/yolo7/exp02_yolov7_greyscale_1024_baseline/R_curve.png)

**Figura X.** Recall in funzione della confidence threshold. La recall parte da circa **0.91** a soglia nulla e decresce progressivamente; oltre una confidence intorno a 0.6 il calo diventa più netto.

### F1 curve

![F1 curve YOLOv7 grayscale](/outputs/yolo7/exp02_yolov7_greyscale_1024_baseline/F1_curve.png)

**Figura X.** Curva F1-score del modello grayscale. Il miglior compromesso tra precision e recall si osserva a una confidence di circa **0.382**, con **F1 ≈ 0.80**.

### Precision-Recall curve

![PR curve YOLOv7 grayscale](/outputs/yolo7/exp02_yolov7_greyscale_1024_baseline/PR_curve.png)

**Figura X.** Curva Precision-Recall del modello grayscale. Il valore aggregato riportato dal grafico è coerente con un **mAP@0.5 ≈ 0.825**, sostanzialmente allineato alla baseline RGB.

## 5.3 Conclusione sull'esperimento grayscale

Nel complesso, l'esperimento **YOLOv7 grayscale** conferma che il dominio dei diagrammi elettrici può essere affrontato efficacemente anche senza informazione cromatica. Tuttavia, rispetto alla baseline RGB, il vantaggio osservato è **modesto e selettivo**:

- non emerge un miglioramento generale su precision, recall e mAP@0.5;
- si osserva invece un piccolo vantaggio sulla metrica più severa **mAP@0.5:0.95**;
- alcune classi traggono beneficio dal grayscale, mentre altre peggiorano.

La conclusione operativa è quindi che il grayscale rappresenta una variante **interessante ma non risolutiva**. Per i prossimi esperimenti, sarà particolarmente utile verificare se una politica di augmentation controllata o un'architettura più recente riescano a trasformare questo piccolo vantaggio locale in un miglioramento complessivo più netto.

---

# 6. Augmentation v1 — exp03

## Politica di augmentation

Per ogni immagine del training set viene generata una versione augmentata con una combinazione di:

1. **rotazione leggera** (circa ±7°) per simulare piccoli disallineamenti o scansioni non perfettamente dritte;
2. **piccola traslazione** per rendere il modello meno sensibile alla posizione assoluta dei simboli;
3. **leggero scaling** per simulare piccole variazioni di dimensione dovute a esportazioni, scansioni o ridimensionamenti;
4. **moderata variazione di luminosità/contrasto**;
5. **rumore leggero** per simulare imperfezioni di acquisizione, compressione o rasterizzazione.

## 6.1 Obiettivo

Valutare se una politica di **data augmentation controllata** migliori la capacità di generalizzazione di YOLOv7 nel rilevamento dei simboli elettrici.

L’obiettivo dell’esperimento `exp03` è verificare se l’aumento artificiale della variabilità del **solo training set** consenta di:

- aumentare la **recall**, riducendo i falsi negativi;
- migliorare **mAP@0.5** e **mAP@0.5:0.95**;
- mantenere una precisione elevata senza introdurre rumore eccessivo.

## 6.2 Motivazione della scelta

Dopo il confronto tra:

- **baseline YOLOv7 RGB**
- **YOLOv7 grayscale**

si è osservato che il preprocessing grayscale non ha prodotto un vantaggio netto e generalizzato. La variante grayscale ha mostrato un lieve miglioramento su **mAP@0.5:0.95**, ma la baseline RGB è rimasta il riferimento più equilibrato per precision, recall e semplicità metodologica.

Per questo motivo, l’esperimento con augmentation è stato costruito a partire dal **dataset RGB originale**, in modo da isolare l’effetto della sola augmentation.

## 6.3 Setup dell’esperimento `exp03`

### Exp ID

**exp03 – YOLOv7 RGB + aug_v1**

### Configurazione

- **Modello:** YOLOv7
- **Input:** RGB
- **Dataset base:** `rf_yolov7_1024_rgb_v1`
- **Training set:** originale + immagini augmentate offline
- **Validation set:** invariato
- **Test set:** invariato
- **Img size:** 1024x1024
- **Epochs:** 100
- **Batch size:** 4
- **Workers:** 2

### Nota metodologica

Le trasformazioni sono applicate **solo al training set**. Validation e test restano invariati, così da garantire un confronto corretto con gli esperimenti precedenti.

## Metriche finali

| Metrica                   |      Valore |
| ------------------------- | ----------: |
| Precision                 |      0.8791 |
| Recall                    |      0.8563 |
| F1-score                  |      0.8676 |
| mAP@0.5                   |      0.8836 |
| mAP@0.5:0.95              |      0.5928 |
| Best epoch (mAP@0.5:0.95) |          69 |
| F1 massimo (dal grafico)  |  circa 0.86 |
| Confidence al F1 massimo  | circa 0.434 |

### Commento sintetico

L’esperimento con **augmentation v1** mostra un miglioramento evidente rispetto alla baseline RGB, soprattutto in termini di **recall** e **mAP**. La precisione finale rimane molto alta e si riduce solo in modo marginale rispetto alla baseline, suggerendo che l’aumento di variabilità del training set ha migliorato la capacità del modello di trovare più simboli senza degradare in modo sostanziale la pulizia delle predizioni.

---

# 7. Augmentation v2 compose — exp04

## Politica di augmentation v2 (`aug_v2_compose`)

La seconda politica di augmentation è stata progettata come variante **più forte e più strutturale** rispetto ad `aug_v1`.

### Idea di base

Invece di limitarsi a piccole perturbazioni geometriche e fotometriche, `aug_v2_compose` introduce una fase di **composizione di diagrammi / porzioni di diagramma**, con l’obiettivo di generare scene più dense o combinazioni più complesse di simboli.

### Trasformazioni caratteristiche

La configurazione sperimentale usata può essere riassunta come segue:

1. **composizione offline** di immagini/regioni per creare diagrammi più complessi;
2. **traslazione implicita** dovuta al processo di composizione;
3. **resize finale** per riportare il campione a 1024x1024;
4. **piccole perturbazioni finali opzionali** su contrasto/luminosità;
5. **rumore leggero opzionale**.

## 7.1 Setup dell’esperimento `exp04`

### Exp ID

**exp04 – YOLOv7 RGB + aug_v2_compose**

### Configurazione

- **Modello:** YOLOv7
- **Input:** RGB
- **Dataset base:** `rf_yolov7_1024_rgb_v1`
- **Training set:** originale + immagini composte/augmentate offline
- **Validation set:** invariato
- **Test set:** invariato
- **Img size:** 1024x1024
- **Epochs:** 100
- **Batch size:** 4
- **Workers:** 2

## Metriche finali

| Metrica                   |      Valore |
| ------------------------- | ----------: |
| Precision                 |      0.8443 |
| Recall                    |      0.8481 |
| F1-score                  |      0.8462 |
| mAP@0.5                   |      0.8587 |
| mAP@0.5:0.95              |      0.5832 |
| Best epoch (mAP@0.5:0.95) |          74 |
| F1 massimo (dal grafico)  |  circa 0.82 |
| Confidence al F1 massimo  | circa 0.485 |

### Commento sintetico

L’esperimento con **augmentation v2 basata su composizione** produce risultati **migliori della baseline solo in misura molto limitata**, ma rimane chiaramente **inferiore ad aug_v1**. La precisione resta alta, la recall migliora leggermente rispetto alla baseline, mentre i guadagni sulle metriche mAP finali sono piccoli e non stabili fino alla fine del training.


## 7.3 Analisi qualitativa di curve e confusion matrix per `aug_v1`

### Andamento complessivo del training

![Andamento training YOLOv7 RGB + aug_v1](/outputs/yolo7/exp03_yolov7_rgb_aug_v1_10242/results.png)

**Figura X.** Andamento delle loss e delle metriche principali durante l’addestramento con augmentation v1. Le loss di training (`box`, `objectness`, `classification`) diminuiscono in modo regolare; anche `val box` e `val classification` si riducono progressivamente. La `val objectness loss` cresce nel tempo, comportamento già osservato anche negli esperimenti precedenti, ma senza impedire il miglioramento delle metriche aggregate.

### Confusion matrix

![Confusion matrix YOLOv7 RGB + aug_v1](/outputs/yolo7/exp03_yolov7_rgb_aug_v1_10242/confusion_matrix.png)

**Figura X.** Confusion matrix normalizzata per l’esperimento `exp03`. La diagonale principale risulta ben marcata, segno di una buona separazione tra molte classi. Persistono alcuni falsi negativi verso background, ma il comportamento complessivo appare coerente con l’aumento di recall osservato nelle metriche aggregate.

### Precision curve

![Precision curve YOLOv7 RGB + aug_v1](/outputs/yolo7/exp03_yolov7_rgb_aug_v1_10242/P_curve.png)

**Figura X.** Precision in funzione della confidence threshold. La curva mostra che la precisione cresce fino a raggiungere circa **1.00** a confidence elevata (circa **0.824**), ma con la consueta perdita di recall.

### Recall curve

![Recall curve YOLOv7 RGB + aug_v1](/outputs/yolo7/exp03_yolov7_rgb_aug_v1_10242/R_curve.png)

**Figura X.** Recall in funzione della confidence threshold. La recall parte da circa **0.94** a soglia nulla e decresce progressivamente; il calo diventa più rapido oltre una confidence intermedia.

### F1 curve

![F1 curve YOLOv7 RGB + aug_v1](/outputs/yolo7/exp03_yolov7_rgb_aug_v1_10242/F1_curve.png)

**Figura X.** Curva F1-score. Il miglior compromesso tra precision e recall si osserva a una confidence di circa **0.434**, con **F1 ≈ 0.86**.

### Precision-Recall curve

![PR curve YOLOv7 RGB + aug_v1](/outputs/yolo7/exp03_yolov7_rgb_aug_v1_10242/PR_curve.png)

**Figura X.** Curva Precision-Recall dell’esperimento con augmentation v1. Il valore globale riportato dal grafico è coerente con **mAP@0.5 ≈ 0.876**, superiore sia alla baseline RGB sia alla variante grayscale.

## 13.17 Analisi qualitativa di curve e confusion matrix per `aug_v2_compose`

### Andamento complessivo del training

![Andamento training YOLOv7 RGB + aug_v2_compose](/outputs/yolo7/exp04_yolov7_rgb_aug_v2_compose_1024/results.png)

**Figura X.** Andamento delle loss e delle metriche principali durante l’addestramento con augmentation v2 basata su composizione. Le loss di training diminuiscono in modo regolare; `val box` e `val classification` scendono progressivamente, mentre `val objectness` cresce anche in questo caso. Le metriche migliorano bene nelle prime epoche e raggiungono il massimo tra circa epoch 70 e 75, per poi mostrare una lieve flessione nella parte finale.

### Confusion matrix

![Confusion matrix YOLOv7 RGB + aug_v2_compose](/outputs/yolo7/exp04_yolov7_rgb_aug_v2_compose_1024/confusion_matrix.png)

**Figura X.** Confusion matrix normalizzata del modello `aug_v2_compose`. La diagonale principale rimane ben visibile, segno che molte classi continuano a essere riconosciute correttamente. Tuttavia si osserva ancora una presenza non trascurabile di falsi negativi verso background, più coerente con una recall finale moderata rispetto a quanto visto con `aug_v1`.

### Precision curve

![Precision curve YOLOv7 RGB + aug_v2_compose](/outputs/yolo7/exp04_yolov7_rgb_aug_v2_compose_1024/P_curve.png)

**Figura X.** Precision in funzione della confidence threshold. La curva raggiunge circa **1.00** intorno a confidence **0.848**, confermando che il modello può essere reso molto selettivo, ma solo a costo di una forte riduzione della recall.

### Recall curve

![Recall curve YOLOv7 RGB + aug_v2_compose](/outputs/yolo7/exp04_yolov7_rgb_aug_v2_compose_1024/R_curve.png)

**Figura X.** Recall in funzione della confidence threshold. La recall parte da circa **0.91** a soglia nulla e decresce progressivamente; il calo si accentua oltre la fascia di confidence intermedia, in linea con un comportamento più conservativo di `aug_v1`.

### F1 curve

![F1 curve YOLOv7 RGB + aug_v2_compose](/outputs/yolo7/exp04_yolov7_rgb_aug_v2_compose_1024/F1_curve.png)

**Figura X.** Curva F1-score del modello `aug_v2_compose`. Il miglior compromesso tra precision e recall si osserva a una confidence di circa **0.485**, con **F1 ≈ 0.82**.

### Precision-Recall curve

![PR curve YOLOv7 RGB + aug_v2_compose](/outputs/yolo7/exp04_yolov7_rgb_aug_v2_compose_1024/PR_curve.png)

**Figura X.** Curva Precision-Recall del modello `aug_v2_compose`. Il valore aggregato riportato dal grafico è coerente con **mAP@0.5 ≈ 0.831**, molto vicino alla baseline RGB ma nettamente inferiore a `aug_v1`.

## 7.4 Interpretazione dei risultati

La seconda politica di augmentation, basata su **composizione di diagrammi** e su una perturbazione più strutturale del training set, non porta il miglioramento atteso.

### Aspetti positivi

- aumento marcato della **recall**;
- aumento netto di **mAP@0.5**;
- miglioramento anche di **mAP@0.5:0.95**, quindi non solo detection più frequente ma anche localizzazione mediamente migliore;
- convergenza buona e raggiungimento del best checkpoint già all’epoch 69.

### Aspetti da notare

- la **precision** finale cala leggermente rispetto alla baseline;
- il miglioramento sembra derivare soprattutto da una maggiore capacità del modello di **non perdere simboli reali**;
- la politica usata appare sufficientemente conservativa da non introdurre rumore distruttivo.

Nel complesso, l’esperimento conferma l’ipotesi iniziale: una augmentation leggera ma coerente con il dominio dei diagrammi elettrici può produrre un miglioramento reale e misurabile.

---

# 8. Augmentation v3 strong — exp03b

### Exp ID

**exp03b – YOLOv7 RGB + aug_v3**

### Configurazione

- **Modello:** YOLOv7
- **Input:** RGB
- **Dataset base:** `rf_yolov7_1024_rgb_aug_strong_v3`
- **Training set:** originale + immagini augmentate offline con politica strong
- **Validation set:** invariato
- **Test set:** invariato
- **Img size:** 1024x1024
- **Epochs:** 100
- **Batch size:** 4
- **Workers:** 2

## Politica di augmentation

- rotazioni forti casuali
- traslazioni più marcate
- lieve rumore
- lieve perturbazione fotometrica
- validation e test invariati

## Metriche finali

| Metrica                   |      Valore |
| ------------------------- | ----------: |
| Precision                 |      0.8568 |
| Recall                    |      0.8854 |
| F1-score                  |      0.8709 |
| mAP@0.5                   |      0.8972 |
| mAP@0.5:0.95              |      0.6059 |
| Best epoch (mAP@0.5:0.95) |          97 |
| F1 massimo (dal grafico)  |  circa 0.86 |
| Confidence al F1 massimo  | circa 0.155 |

### Commento sintetico

L’esperimento `exp03b` mostra un comportamento molto interessante: rispetto alle precedenti varianti YOLOv7, la augmentation strong produce la **recall più alta** e i **migliori valori di mAP@0.5 e mAP@0.5:0.95**. La precisione cala rispetto alle versioni più conservative, ma il modello diventa sensibilmente più capace di individuare i simboli reali e di mantenere una qualità complessiva di detection superiore.

## 8.1 Analisi qualitativa di curve e confusion matrix per `aug_v3`

### Andamento complessivo del training

![Andamento training YOLOv7 RGB + aug_v3](/outputs/yolo7/exp03b_yolov7_rgb_aug_strong_v3_1024/results.png)

**Figura X.** Andamento delle loss e delle metriche principali durante l’addestramento con augmentation strong `aug_v3`. Le loss di training diminuiscono in modo regolare; `val box` e `val classification` mostrano un miglioramento progressivo, mentre `val objectness` cresce nel tempo, comportamento già osservato anche in altri esperimenti YOLOv7. Nonostante ciò, precision, recall e mAP continuano a migliorare fino alle epoche finali.

### Confusion matrix

![Confusion matrix YOLOv7 RGB + aug_v3](/outputs/yolo7/exp03b_yolov7_rgb_aug_strong_v3_1024/confusion_matrix.png)

**Figura X.** Confusion matrix normalizzata del modello `aug_v3`. La diagonale principale resta ben marcata e il modello mostra una capacità elevata di individuare correttamente molte classi. Persistono falsi negativi verso background, ma il comportamento complessivo è coerente con l’aumento di recall osservato nelle metriche aggregate.

### Precision curve

![Precision curve YOLOv7 RGB + aug_v3](/outputs/yolo7/exp03b_yolov7_rgb_aug_strong_v3_1024/P_curve.png)

**Figura X.** Precision in funzione della confidence threshold. La precisione raggiunge circa **1.00** a confidence elevata, ma con una soglia più severa.

### Recall curve

![Recall curve YOLOv7 RGB + aug_v3](/outputs/yolo7/exp03b_yolov7_rgb_aug_strong_v3_1024/R_curve.png)

**Figura X.** Recall in funzione della confidence threshold. La recall parte da circa **0.94** a soglia nulla e si mantiene elevata fino a soglie intermedie, confermando la forte sensibilità del modello.

### F1 curve

![F1 curve YOLOv7 RGB + aug_v3](/outputs/yolo7/exp03b_yolov7_rgb_aug_strong_v3_1024/F1_curve.png)

**Figura X.** Curva F1-score del modello `aug_v3`. Il miglior compromesso tra precision e recall si osserva a una confidence di circa **0.155**, con **F1 ≈ 0.86**.

### Precision-Recall curve

![PR curve YOLOv7 RGB + aug_v3](/outputs/yolo7/exp03b_yolov7_rgb_aug_strong_v3_1024/PR_curve.png)

**Figura X.** Curva Precision-Recall dell’esperimento `exp03b`. Il valore aggregato riportato dal grafico è coerente con **mAP@0.5 ≈ 0.893**, il migliore tra gli esperimenti YOLOv7 completati.

## 13.27 Interpretazione dei risultati di `exp03b`

L’esperimento con augmentation strong mostra un risultato molto chiaro: aumentare in modo deciso la variabilità geometrica del training set può migliorare in modo concreto la capacità del modello di generalizzare.

### Aspetti positivi

- **recall più alta** tra gli esperimenti YOLOv7 completati;
- **mAP@0.5** più alta;
- **mAP@0.5:0.95** più alta;
- **F1-score** sostanzialmente allineata alla migliore variante precedente (`aug_v1`);
- training stabile anche con augmentation più aggressiva.

### Aspetti critici

- la **precisione** cala in modo evidente rispetto a baseline, grayscale e `aug_v1`;
- il modello appare meno conservativo e quindi più incline a generare falsi positivi;
- il best checkpoint arriva più tardi, segnale di una convergenza un po’ più lenta.

### Interpretazione complessiva

Rispetto ad `aug_v1`, la variante `aug_v3` sacrifica pulizia delle predizioni ma guadagna in copertura e qualità aggregata della detection. Questo suggerisce che, per il dataset dei diagrammi elettrici, una augmentation forte ma ancora coerente con la struttura del dominio può essere molto utile quando l’obiettivo principale è massimizzare recall e metriche mAP.

## 8.2 Aggiornamento della conclusione complessiva sulle augmentation YOLOv7

Dopo l’inserimento di `exp03b`, il quadro complessivo delle augmentation YOLOv7 diventa il seguente:

- **aug_v1** resta la variante più equilibrata in termini di compromesso tra precision e recall;
- **aug_v2_compose** rimane la meno efficace tra le augmentation testate;
- **aug_v3** diventa la variante migliore se si considerano soprattutto **recall**, **mAP@0.5** e **mAP@0.5:0.95**.

### Conclusione operativa

Per YOLOv7 emergono quindi due letture possibili:

1. **se si privilegia il miglior equilibrio complessivo**, `aug_v1` resta molto forte;
2. **se si privilegiano recall e metriche mAP**, `aug_v3` è attualmente la migliore variante YOLOv7 completata.
