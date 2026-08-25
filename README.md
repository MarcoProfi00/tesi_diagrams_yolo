# AI for Electronic Circuit

Pipeline sperimentale per trasformare immagini di schemi elettronici in un
grafo dei collegamenti, generare una netlist SPICE, simularla con ngspice e
consultare i risultati nel viewer web. I comandi di questa guida si riferiscono
al branch `develop` e a Windows PowerShell.

La guida dettagliata del launcher e' in
[`scripts/pipeline_unified/README.md`](scripts/pipeline_unified/README.md).

## Prerequisiti

- Windows 10/11 a 64 bit.
- Git e Git LFS. Eseguire `git lfs install` almeno una volta per utente.
- CPython 3.12.7 a 64 bit, versione registrata anche in `.python-version`.
- ngspice con `ngspice_con.exe` o `ngspice.exe` disponibile nel `PATH`.
- Tesseract OCR con la lingua `eng` disponibile nel `PATH`, oppure il path
  completo impostato nella variabile `TESSERACT_CMD`.
- Accesso a Internet durante il primo setup per Git LFS, pip e il primo download
  dei modelli EasyOCR. Le funzioni OpenAI richiedono inoltre rete e API key.

Il checkout LFS contiene circa 1,1 GB di archivi dataset e il checkpoint YOLO
richiesto da Pipeline 1.0 pesa circa 19 MB. L'ambiente Python di riferimento
occupa circa 1,3 GB; Git LFS conserva anche una copia interna degli oggetti.
Riservare almeno **5 GB liberi** per clone, ambiente e cache, e spazio
aggiuntivo per dataset estratti, training e workspace in `outputs/`.

## Installazione su Windows

Clonare esplicitamente il branch di lavoro:

```powershell
git lfs install
git clone --branch develop URL_REPOSITORY tesi_diagrams_yolo
Set-Location .\tesi_diagrams_yolo
git lfs pull
git branch --show-current
```

Sostituire `URL_REPOSITORY` con l'URL HTTPS o SSH del remote da usare. L'ultimo
comando deve stampare `develop`. Su Windows conviene clonare in un percorso
corto, per esempio `C:\src\tesi_diagrams_yolo`; se si deve usare OneDrive o una
cartella profonda, abilitare prima `git config --global core.longpaths true`.

Creare un ambiente pulito e installare il lock CPU validato per Windows x64:

```powershell
py -3.12 --version
py -3.12 -m venv .venv312
.\.venv312\Scripts\python.exe -m pip install pip==26.1
.\.venv312\Scripts\python.exe -m pip install --only-binary=:all: `
  --index-url https://pypi.org/simple -r requirements-lock.txt
.\.venv312\Scripts\python.exe -m pip check
```

`py -3.12 --version` deve indicare Python 3.12.7. Il progetto dichiara
le dipendenze dirette in `requirements.txt`; `requirements-lock.txt` blocca
l'intera chiusura di 67 pacchetti risolta con pip 26.1. I pacchetti
`opencv-python` e `opencv-python-headless`, installati dalle dipendenze della
pipeline sugli stessi file `cv2`, sono bloccati entrambi a `4.13.0.92`.

Installare ngspice e Tesseract separatamente, aggiungendo le rispettive cartelle
al `PATH`. Verificare da una nuova PowerShell:

```powershell
Get-Command ngspice_con.exe
tesseract --version
tesseract --list-langs
```

Se Tesseract non e' nel `PATH`, impostarlo per la sessione corrente:

```powershell
$env:TESSERACT_CMD = "C:\Program Files\Tesseract-OCR\tesseract.exe"
```

Il checkpoint del detector deve essere stato materializzato da Git LFS:

```powershell
$model = Get-Item "outputs\yolo11\exp11b1_yolo11_rgb_aug_strong_v3\weights\best.pt"
if ($model.Length -lt 10MB) { throw "Checkpoint YOLO assente o ancora puntatore LFS" }
```

## Batch demo canonico

Gli esempi usano sempre:

```text
data\batchPipeline2.0\batchDemo\
|-- a04.jpg
|-- a08.jpg
|-- a09.png
|-- b02.jpg
|-- b03.jpg
`-- values\
    |-- a04_values.yaml
    |-- a08_values.yaml
    |-- a09_values.yaml
    |-- b02_values.yaml
    `-- b03_values.yaml
```

Il nome base dell'immagine deve coincidere con quello del file
`values\<circuito>_values.yaml`.
Provenienza, licenza e regole di estrazione sono documentate in
[`data/README.md`](data/README.md).

## Esecuzione

Eseguire tutti i comandi dalla root del repository.

Pipeline 1.0, dall'immagine al Graph JSON:

```powershell
.\.venv312\Scripts\python.exe -B scripts\pipeline_unified\run_pipeline.py graph `
  --workspace demo_a09 `
  --input-dir data\batchPipeline2.0\batchDemo `
  --circuit a09
```

Pipeline 2.0 e simulazione ngspice sullo stesso workspace:

```powershell
.\.venv312\Scripts\python.exe -B scripts\pipeline_unified\run_pipeline.py spice `
  --workspace demo_a09 `
  --circuit a09
```

Viewer, CHAT e AGENT:

```powershell
.\.venv312\Scripts\python.exe -B scripts\pipeline_unified\run_pipeline.py webchat `
  --workspace demo_a09 `
  --circuit a09
```

Il server locale resta attivo fino a `Ctrl+C`. Per preparare gli asset senza
avviarlo, aggiungere `--prepare-only`.

Flusso completo con un nuovo workspace:

```powershell
.\.venv312\Scripts\python.exe -B scripts\pipeline_unified\run_pipeline.py all `
  --workspace verifica_clone_a09_all `
  --input-dir data\batchPipeline2.0\batchDemo `
  --circuit a09
```

Il nome scelto per `--workspace` deve essere nuovo; per una seconda prova usare
un altro nome oppure aggiungere consapevolmente `--force` per rigenerarlo.

Se ngspice non puo' essere aggiunto al `PATH`, aggiungere ai comandi `spice`,
`webchat` e `all`:

```powershell
--ngspice-executable "C:\percorso\di\ngspice_con.exe"
```

## OpenAI

La chiave non e' necessaria per Pipeline 1.0, per la generazione tecnica SPICE
o per preparare il viewer. Serve quando si eseguono le funzioni AGENT che
chiamano l'API.

```powershell
Copy-Item .env.example .env
notepad .env
```

Inserire `OPENAI_API_KEY` nella sola copia locale. `.env` e' ignorato da Git e
non deve mai essere aggiunto ai commit. `OPENAI_MODEL` permette di cambiare il
modello predefinito.

## Preflight e test

Il controllo integrato non modifica gli output e termina con codice diverso da
zero se manca un requisito obbligatorio:

```powershell
$python = ".\.venv312\Scripts\python.exe"
& $python -B scripts\pipeline_unified\run_pipeline.py preflight
```

`preflight` controlla Python, import, coerenza pacchetti e versioni dei due
build OpenCV, script, metadati e modelli SPICE, batch e YAML, checkpoint YOLO e
relativo hash, Git LFS, ngspice, Tesseract con lingua inglese, cache EasyOCR e
configurazione OpenAI. La API key e la cache EasyOCR sono avvisi per il flusso
tecnico; usare `--require-openai` per rendere obbligatoria anche la chiave. Se
necessario si possono passare `--ngspice-executable` e
`--tesseract-executable` con path espliciti.

Il `--dry-run` di una singola fase permette inoltre di verificarne la selezione
senza creare il workspace:

```powershell
& $python -B scripts\pipeline_unified\run_pipeline.py graph `
  --workspace preflight_a09 `
  --input-dir data\batchPipeline2.0\batchDemo `
  --circuit a09 `
  --dry-run
```

Suite di regressione:

```powershell
& $python -B -m unittest discover -s tests\pipeline2 -v
& $python -B -m unittest discover -s tests\pipeline_unified -v
```

## CPU e GPU

La configurazione verificata funziona su CPU; una GPU NVIDIA non e' necessaria
per eseguire le pipeline, ma accelera detector ed EasyOCR. Controllare il
backend installato con:

```powershell
.\.venv312\Scripts\python.exe -B -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```

Per usare CUDA, installare wheel Torch/Torchvision compatibili con
`torch==2.11.0` e `torchvision==0.26.0` seguendo la matrice della propria
versione CUDA, quindi rieseguire `pip check` e le due suite. Non copiare la
`.venv312` da un altro PC: per CPU ricrearla sempre da
`requirements-lock.txt`. Per CUDA serve invece un lock dedicato, da validare
separatamente.

## Ambito della riproducibilita'

Il setup versionato copre il flusso di inferenza completo: immagine, Graph JSON,
SPICE/ngspice, viewer, CHAT e AGENT. Il detector usa `ultralytics` e il
checkpoint `best.pt` gestito da Git LFS; la copia locale ignorata
`repos/yolov7` non viene usata da questi comandi.

Il riaddestramento dei vecchi esperimenti YOLOv7 non e' invece ancora un flusso
self-contained della repository: non esiste un launcher di training versionato
che dipenda da quella copia esterna. Se servira' trasferire anche il workflow di
training storico, andra' preparato separatamente con codice, commit e comando di
addestramento espliciti.

Anche sei utility sotto `scripts/presentation/` automatizzano Microsoft
PowerPoint tramite COM e richiedono quindi PowerPoint desktop installato su
Windows. Sono strumenti di produzione delle slide, non dipendenze delle
pipeline di inferenza e simulazione controllate da `preflight`.

## Output principali

- Workspace persistenti: `outputs/demo_workspaces/<workspace>/`.
- Graph JSON: `pipeline1.0/06_graph_report/<circuito>/<circuito>.json` nel
  workspace.
- Netlist e risultati: `pipeline2.0/<circuito>/` nel workspace.
- Metadati SPICE e mapping: [`metadata/README.md`](metadata/README.md).

I manifest dei workspace usano lo schema v2 e salvano come repo-relative i path
interni al progetto. Quando viene aperto un manifest storico, il launcher
risolve automaticamente i vecchi path assoluti sul clone corrente e converte
l'alias `data/batchDemo` nel batch canonico; al successivo salvataggio il
manifest viene scritto in schema v2. Un workspace copiato puo' quindi essere
ripreso se input e artefatti referenziati sono presenti nel clone.
