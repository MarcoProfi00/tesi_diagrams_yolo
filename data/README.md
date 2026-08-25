# Dati, provenienza e checkout

Gli archivi `data/datasets/**/*.zip` sono versionati con Git LFS. Le cartelle
estratte restano locali e sono escluse da Git; fanno eccezione i batch operativi
`batchPipeline1.0` e `batchPipeline2.0`, necessari ai test e alle pipeline.

Dopo il clone eseguire sempre:

```powershell
git lfs pull
git lfs fsck
```

## Dataset Roboflow

I file `README.dataset.txt` inclusi negli archivi base v1 e v3 identificano il
dataset **electrical-diagrams-detection**, workspace Roboflow:

<https://universe.roboflow.com/marcos-workspace-amrpv/electrical-diagrams-detection>

Gli stessi file dichiarano licenza **CC BY 4.0**. Le varianti gray e augmented
sono trasformazioni del dataset di partenza prodotte dagli script del progetto;
la licenza e l'attribuzione della fonte continuano quindi ad applicarsi.

## Batch operativi

Audit del 25 agosto 2026:

- 159 immagini versionate nei due batch corrispondono a 108 contenuti unici;
- 81 contenuti unici sono copie byte-identiche di immagini presenti negli
  archivi LFS sopra descritti;
- i restanti 27 file (18 contenuti unici) sono copie byte-identiche di fixture
  gia' presenti nella storia del repository, sotto `experiment_ai/` o
  `outputs/`.

Questa organizzazione non introduce nuove immagini rispetto al materiale gia'
versionato: rende soltanto canonici gli input richiesti da script e test. Per
un'eventuale pubblicazione o redistribuzione esterna resta comunque opportuno
conservare l'attribuzione Roboflow e verificare la provenienza originaria delle
fixture storiche che non compaiono negli archivi con metadati di licenza.

## Estrazione del dataset RGB v3

Lo script seguente valida lo ZIP, impedisce path traversal e controlla il layout
senza scrivere file:

```powershell
.\.venv312\Scripts\python.exe -B scripts\utils\unzip_dataset.py --check-only
```

Senza `--check-only` estrae in
`data/datasets/dataset_v3/rf_yolo_1024_rgb/`, il percorso usato dagli script di
augmentation e analisi.

Per validare o estrarre il dataset RGB v1 usato dalle utility bounding-box:

```powershell
.\.venv312\Scripts\python.exe -B scripts\utils\unzip_dataset.py `
  --archive data\datasets\dataset_v1\rf_yolov7_1024_rgb_v1.zip `
  --check-only
```

Rimuovendo `--check-only`, la destinazione dedotta e'
`data/datasets/dataset_v1/rf_yolov7_1024_rgb_v1/`, esattamente quella letta da
`convert_dataset_detection_only.py` e `count_box_greather_5.py`.
