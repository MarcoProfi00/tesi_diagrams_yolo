# Guida Per Creare Un Nuovo Batch Di Circuiti Complessi

Questa guida spiega come usare gli script in `scripts/GPT` per eseguire un nuovo batch di esperimenti GPT su circuiti diversi.

La procedura vale per qualunque batch organizzato con la stessa struttura di `experiment_ai/circuiti_complessi/batch_v1`.

Nota: `scripts/GPT/verifica_json_img` e un esperimento separato. Non va usato per questa procedura.

---

## 1. Obiettivo Degli Script

Gli script servono a confrontare modelli GPT su un compito di troubleshooting circuitale.

Per ogni circuito vengono generate due risposte:

- `JSON + datasheet`
- `JSON + immagine + datasheet`

Poi le risposte vengono valutate da un judge e aggregate in CSV, tabelle e grafici.

---

## 2. Struttura Di Un Nuovo Batch

Crea una nuova cartella batch, ad esempio:

```text
experiment_ai/circuiti_complessi/batch_v2
```

Dentro il batch crea una cartella per ogni circuito:

```text
batch_v2/
|-- circuito_01/
|-- circuito_02/
`-- circuito_03/
```

Ogni circuito deve avere questa struttura:

```text
circuito_01/
|-- circuito_01.json
|-- circuito_01.jpg
|-- prompt_json.txt
|-- prompt_json_img.txt
`-- datasheet/
    `-- *.txt
```

Regola importante: il nome della cartella, del JSON e dell'immagine deve coincidere.

Esempio valido:

```text
my_circuit/
|-- my_circuit.json
|-- my_circuit.jpg
```

Esempio non valido:

```text
my_circuit/
|-- graph.json
|-- image.jpg
```

Gli script cercano automaticamente:

```text
<CIRCUIT_NAME>/<CIRCUIT_NAME>.json
<CIRCUIT_NAME>/<CIRCUIT_NAME>.jpg
```

---

## 3. File Richiesti Per Ogni Circuito

### JSON

Il file:

```text
<CIRCUIT_NAME>.json
```

deve contenere il graph del circuito prodotto dalla pipeline.

### Immagine

Il file:

```text
<CIRCUIT_NAME>.jpg
```

viene usato solo nella configurazione `JSON + immagine + datasheet` e dal judge.

### Datasheet

La cartella:

```text
datasheet/
```

deve contenere almeno un file `.txt`.

Gli script leggono tutti i `.txt` presenti nella cartella e li concatenano.

### Prompt JSON

Il file:

```text
prompt_json.txt
```

deve contenere questi placeholder:

```text
[INSERIRE PROBLEMA]
[INCOLLARE DATASHEET O ESTRATTO]
[INCOLLARE JSON]
```

### Prompt JSON + Immagine

Il file:

```text
prompt_json_img.txt
```

deve contenere questi placeholder:

```text
[INSERIRE PROBLEMA]
[INCOLLARE DATASHEET O ESTRATTO]
[INCOLLARE JSON]
[CARICARE O INSERIRE IMMAGINE]
```

---

## 4. Configurazione Degli Script

Gli script principali sono configurati modificando variabili all'inizio del file.

Script per la run `JSON + datasheet`:

```text
scripts/GPT/run_one_json.py
```

Script per la run `JSON + immagine + datasheet`:

```text
scripts/GPT/run_one_json_image.py
```

In entrambi imposta:

```python
MODEL = "gpt-5.4"
PROBLEM = "Descrizione del problema da diagnosticare."
CIRCUIT_NAME = "circuito_01"
```

Se stai creando un batch diverso da `batch_v1`, modifica anche `CIRCUIT_DIR`.

Negli script attuali il percorso e costruito cosi:

```python
CIRCUIT_DIR = (
    PROJECT_ROOT
    / "experiment_ai"
    / "circuiti_complessi"
    / "batch_v1"
    / CIRCUIT_NAME
)
```

Per un secondo batch, ad esempio `batch_v2`, cambia:

```python
/ "batch_v1"
```

in:

```python
/ "batch_v2"
```

---

## 5. API Key

Gli script caricano la chiave API da:

```text
scripts/GPT/.env
```

Il file deve contenere:

```env
OPENAI_API_KEY=...
```

---

## 6. Eseguire Una Run JSON + Datasheet

Dalla root del progetto:

```powershell
python scripts\GPT\run_one_json.py
```

Lo script legge:

```text
<batch>/<CIRCUIT_NAME>/<CIRCUIT_NAME>.json
<batch>/<CIRCUIT_NAME>/datasheet/*.txt
<batch>/<CIRCUIT_NAME>/prompt_json.txt
```

e salva il risultato in:

```text
<batch>/<CIRCUIT_NAME>/results_json/
```

---

## 7. Eseguire Una Run JSON + Immagine + Datasheet

Dalla root del progetto:

```powershell
python scripts\GPT\run_one_json_image.py
```

Lo script legge:

```text
<batch>/<CIRCUIT_NAME>/<CIRCUIT_NAME>.json
<batch>/<CIRCUIT_NAME>/<CIRCUIT_NAME>.jpg
<batch>/<CIRCUIT_NAME>/datasheet/*.txt
<batch>/<CIRCUIT_NAME>/prompt_json_img.txt
```

e salva il risultato in:

```text
<batch>/<CIRCUIT_NAME>/results_json_img/
```

---

## 8. Ripetere Per Ogni Modello

Per confrontare piu modelli:

1. modifica `MODEL` in `run_one_json.py`;
2. esegui `python scripts\GPT\run_one_json.py`;
3. modifica lo stesso `MODEL` in `run_one_json_image.py`;
4. esegui `python scripts\GPT\run_one_json_image.py`;
5. ripeti per ogni modello.

Alla fine, per ogni circuito, dovresti avere:

```text
results_json/
results_json_img/
```

con una risposta per ogni modello e per ogni tipo di input.

---

## 9. Eseguire Il Judge Del Circuito

Apri:

```text
scripts/GPT/run_judge_one_circuit.py
```

Imposta:

```python
JUDGE_MODEL = "gpt-5.5"
CIRCUIT_NAME = "circuito_01"
PROBLEM = "Descrizione del problema da diagnosticare."
```

Se usi un batch diverso da `batch_v1`, modifica anche qui il percorso:

```python
/ "batch_v1"
```

in:

```python
/ "batch_v2"
```

Poi esegui:

```powershell
python scripts\GPT\run_judge_one_circuit.py
```

Lo script legge tutti i `.txt` in:

```text
results_json/
results_json_img/
```

e salva le valutazioni in:

```text
judge_results/
```

Produce:

```text
<result_file>__judge_<JUDGE_MODEL>.json
<CIRCUIT_NAME>__judge_summary_<JUDGE_MODEL>_<timestamp>.json
```

---

## 10. Generare Tabelle Locali Del Circuito

Apri:

```text
scripts/GPT/make_judge_tables.py
```

Imposta:

```python
CIRCUIT_NAME = "circuito_01"
```

Se usi un batch diverso da `batch_v1`, modifica anche qui il percorso del batch.

Poi esegui:

```powershell
python scripts\GPT\make_judge_tables.py
```

Output:

```text
<batch>/<CIRCUIT_NAME>/judge_results/<CIRCUIT_NAME>_judge_tables.md
```

---

## 11. Ripetere Per Tutti I Circuiti Del Batch

Per ogni circuito:

1. imposta `CIRCUIT_NAME` e `PROBLEM`;
2. esegui tutte le run `JSON + datasheet`;
3. esegui tutte le run `JSON + immagine + datasheet`;
4. esegui il judge;
5. genera le tabelle locali.

Quando tutti i circuiti hanno una cartella `judge_results/`, puoi aggregare il batch.

---

## 12. Aggregare Il Batch

Per aggregare un batch completo:

```powershell
python scripts\GPT\aggregate_judge_results.py --root experiment_ai\circuiti_complessi\batch_v2 --dedupe
```

`--dedupe` tiene la run piu recente per ogni combinazione:

```text
circuito + modello + input_type
```

Output:

```text
experiment_ai/circuiti_complessi/batch_v2/_aggregate/
```

File principali:

```text
all_runs.csv
all_runs.json
aggregate_by_model.csv
aggregate_by_model_input.csv
aggregate_by_circuit.csv
aggregate_by_circuit_input.csv
aggregate_by_input_type.csv
criteria_long.csv
deltas_image_vs_json.csv
cost_summary.csv
```

---

## 13. Generare CSV Per Grafici

Per generare CSV intermedi:

```powershell
python scripts\GPT\make_graph_csvs.py --batch-dir experiment_ai\circuiti_complessi\batch_v2
```

Per un solo circuito:

```powershell
python scripts\GPT\make_graph_csvs.py --batch-dir experiment_ai\circuiti_complessi\batch_v2 --circuit circuito_01
```

---

## 14. Generare Le Figure

Figure principali:

```powershell
python scripts\plot_graphics_result_gpt\make_main_figures.py --input-dir experiment_ai\circuiti_complessi\batch_v2\_aggregate
```

Figure appendice:

```powershell
python scripts\plot_graphics_result_gpt\make_appendix_figures.py --input-dir experiment_ai\circuiti_complessi\batch_v2\_aggregate
```

Output:

```text
experiment_ai/circuiti_complessi/batch_v2/_aggregate/figures_main/
experiment_ai/circuiti_complessi/batch_v2/_aggregate/figures_appendix/
```

---

## 15. Sequenza Riassunta

Per ogni circuito:

```text
1. Preparare cartella circuito con JSON, JPG, prompt e datasheet txt.
2. Impostare batch, MODEL, CIRCUIT_NAME e PROBLEM in run_one_json.py.
3. Eseguire python scripts\GPT\run_one_json.py.
4. Impostare batch, MODEL, CIRCUIT_NAME e PROBLEM in run_one_json_image.py.
5. Eseguire python scripts\GPT\run_one_json_image.py.
6. Ripetere gli step 2-5 per tutti i modelli da confrontare.
7. Impostare batch, CIRCUIT_NAME e PROBLEM in run_judge_one_circuit.py.
8. Eseguire python scripts\GPT\run_judge_one_circuit.py.
9. Impostare batch e CIRCUIT_NAME in make_judge_tables.py.
10. Eseguire python scripts\GPT\make_judge_tables.py.
```

Dopo tutti i circuiti:

```powershell
python scripts\GPT\aggregate_judge_results.py --root experiment_ai\circuiti_complessi\batch_v2 --dedupe
python scripts\GPT\make_graph_csvs.py --batch-dir experiment_ai\circuiti_complessi\batch_v2
python scripts\plot_graphics_result_gpt\make_main_figures.py --input-dir experiment_ai\circuiti_complessi\batch_v2\_aggregate
python scripts\plot_graphics_result_gpt\make_appendix_figures.py --input-dir experiment_ai\circuiti_complessi\batch_v2\_aggregate
```

---

## 16. Controlli Rapidi

Controllare output di un circuito:

```powershell
Get-ChildItem experiment_ai\circuiti_complessi\batch_v2\circuito_01\results_json
Get-ChildItem experiment_ai\circuiti_complessi\batch_v2\circuito_01\results_json_img
Get-ChildItem experiment_ai\circuiti_complessi\batch_v2\circuito_01\judge_results
```

Controllare aggregato:

```powershell
Get-ChildItem experiment_ai\circuiti_complessi\batch_v2\_aggregate
```

Il file finale principale e:

```text
experiment_ai/circuiti_complessi/batch_v2/_aggregate/all_runs.csv
```

