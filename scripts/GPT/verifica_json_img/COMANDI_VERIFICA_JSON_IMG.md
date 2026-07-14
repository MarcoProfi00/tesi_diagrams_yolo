# Comandi Verifica Immagine - Graph JSON

Questo file raccoglie i comandi utili per eseguire il judge multimodale che confronta ogni immagine di circuito con il relativo **Graph JSON originale** prodotto dalla pipeline.

Il judge valuta solo la fedelta topologica terminale-terminale:

```text
immagine del circuito -> collegamenti nel campo graph del Graph JSON
```

Lo script non modifica il JSON, non crea netlist, non valuta il funzionamento elettrico del circuito e non trasforma il campo `graph`.

---

## 1. Struttura Attesa

Dalla root del progetto:

```text
scripts/
`-- GPT/
    `-- verifica_json_img/
        |-- judge_image_graph.py
        `-- COMANDI_VERIFICA_JSON_IMG.md

metadata/
`-- class_terminals_v1.yaml

experiment_ai/
`-- verify_json_img/
    |-- prompt.txt
    |-- batchA/
    |   |-- images/
    |   `-- json/
    |-- batchB/
    |   |-- images/
    |   `-- json/
    |-- batchC1/
    |   |-- images/
    |   `-- json/
    `-- batchC2/
        |-- images/
        `-- json/
```

Il nome dell'immagine e del JSON deve coincidere:

```text
a01.png -> a01.json
c16.jpg -> c16.json
```

---

## 2. Input Usati Dal Judge

Lo script invia al modello:

```text
prompt.txt
immagine del circuito
Graph JSON originale
metadata/class_terminals_v1.yaml
```

Il file YAML viene usato solo come vocabolario della pipeline: classi disponibili, terminali attesi e ruoli terminali. Non deve essere usato per inventare componenti o collegamenti non visibili.

Default principali:

```text
root: experiment_ai/verify_json_img
prompt: experiment_ai/verify_json_img/prompt.txt
yaml: metadata/class_terminals_v1.yaml
model: gpt-5.4
detail: high
reasoning effort: low
max output tokens: 3500 con none/low, 7000 con medium/high/xhigh
```

---

## 3. Controllo Preliminare

Da eseguire sempre per primo. Non consuma API.

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --dry-run
```

Output atteso indicativo:

```text
Root: .../experiment_ai/verify_json_img
Prompt: .../experiment_ai/verify_json_img/prompt.txt
YAML: .../metadata/class_terminals_v1.yaml
Output: .../experiment_ai/verify_json_img/batchA/output_gpt5_4
Modello: gpt-5.4
Coppie trovate: 1
- [A] a01: a01.png + a01.json
```

Puoi comunque passare root, prompt e YAML espliciti:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --prompt experiment_ai/verify_json_img/prompt.txt --classes-yaml metadata/class_terminals_v1.yaml --dry-run
```

---

## 4. Un Solo Circuito

Esempio su `a01`:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --only a01 --model gpt-5.4
```

Esempio su `c16`:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --only c16 --model gpt-5.4
```

Questo e il test piu utile dopo il dry run, per verificare prompt, API key, YAML e output.

---

## 5. Piu Circuiti Specifici

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --only a01,a02,a03 --model gpt-5.4
```

Lo script elabora solo i circuiti indicati nella lista separata da virgole.

---

## 6. Batch A

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --batch A --model gpt-5.4
```

Forma equivalente:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --batch batchA --model gpt-5.4
```

---

## 7. Batch B

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --batch B --model gpt-5.4
```

Forma equivalente:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --batch batchB --model gpt-5.4
```

---

## 8. Batch C1

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --batch C1 --model gpt-5.4
```

Forma equivalente:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --batch batchC1 --model gpt-5.4
```

---

## 9. Batch C2

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --batch C2 --model gpt-5.4
```

Forma equivalente:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --batch batchC2 --model gpt-5.4
```

---

## 10. Tutti I Batch

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --model gpt-5.4
```

Elabora automaticamente tutti i batch trovati dentro:

```text
experiment_ai/verify_json_img/
```

---

## 11. Riprendere Una Esecuzione Interrotta

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --model gpt-5.4 --resume
```

Lo script riusa i risultati gia presenti in `raw_responses/` e chiama il modello solo per quelli mancanti.

Nota: `--resume` riusa file raw esistenti anche se prompt o YAML sono cambiati. Dopo una modifica metodologica importante conviene usare un output nuovo con `--out-dir`, oppure non usare `--resume`.

---

## 12. Limitare Il Numero Di Circuiti

Utile per test rapidi:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --limit 3 --model gpt-5.4
```

Con un batch:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --batch A --limit 3 --model gpt-5.4
```

---

## 13. Output Personalizzato

Se analizzi un solo batch senza `--out-dir`, l'output finisce dentro quel batch:

```text
experiment_ai/verify_json_img/batchA/output_gpt5_4/
```

Se analizzi piu batch insieme senza `--out-dir`, l'output finisce in:

```text
experiment_ai/verify_json_img/output_gpt5_4/
```

Esempio con output dedicato:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --batch A --model gpt-5.4 --out-dir experiment_ai/verify_json_img/batchA/output_terminal_graph_gpt54
```

---

## 14. Eseguire Senza Grafici

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --model gpt-5.4 --no-plots
```

Produce comunque:

```text
judge_results.jsonl
judge_results.csv
judge_report.md
raw_responses/
```

---

## 15. Dettaglio Immagine

Default consigliato:

```text
high
```

Comando esplicito:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --batch A --model gpt-5.4 --detail high
```

Per ridurre costo o latenza:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --batch A --model gpt-5.4 --detail low
```

Per i circuiti, `high` resta la scelta consigliata per leggere pin, fili, OCR e polarita.

---

## 16. Reasoning Effort

Default:

```text
low
```

Comando esplicito:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --batch A --model gpt-5.4 --reasoning-effort low
```

Per circuiti piu complessi:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --batch C2 --model gpt-5.4 --reasoning-effort medium
```

Valori ammessi:

```text
none
low
medium
high
xhigh
```

---

## 17. Max Output Tokens

Default:

```text
3500 con reasoning none/low
7000 con reasoning medium/high/xhigh
```

Per circuiti complessi:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --only c16 --model gpt-5.4 --max-output-tokens 5000
```

Se usi `--reasoning-effort medium`, lascia pure il default automatico oppure usa un valore esplicito alto:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --batch A --model gpt-5.4 --reasoning-effort medium --max-output-tokens 7000
```

---

## 18. Prompt O YAML Personalizzati

Prompt default:

```text
experiment_ai/verify_json_img/prompt.txt
```

YAML default:

```text
metadata/class_terminals_v1.yaml
```

Prompt esplicito:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --prompt experiment_ai/verify_json_img/prompt.txt --batch A --model gpt-5.4
```

YAML esplicito:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --classes-yaml metadata/class_terminals_v1.yaml --batch A --model gpt-5.4
```

Prompt alternativo:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --prompt experiment_ai/verify_json_img/prompt_v2.txt --batch A --model gpt-5.4
```

---

## 19. Sequenza Consigliata

### Step 1 - Dry Run

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --dry-run
```

### Step 2 - Test Su Un Circuito Semplice

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --only a01 --model gpt-5.4
```

### Step 3 - Test Su Un Circuito Complesso

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --only c16 --model gpt-5.4
```

### Step 4 - Batch A Completo

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --batch A --model gpt-5.4
```

### Step 5 - Tutti I Batch

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --model gpt-5.4
```

---

## 20. File Prodotti

Per un singolo batch, esempio `batchA`:

```text
experiment_ai/verify_json_img/batchA/output_gpt5_4/
|-- judge_results.jsonl
|-- judge_results.csv
|-- judge_report.md
|-- raw_responses/
`-- plots/
```

### `judge_results.jsonl`

Risultato completo circuito per circuito, inclusi metadata, raw output e usage.

### `judge_results.csv`

Tabella sintetica usabile per analisi e grafici.

Colonne principali:

```text
circuit_id
batch
image_file
json_file
score
decision
usable_as_graph_base
components_score
terminals_pins_score
graph_connections_score
visible_semantics_score
critical_errors_count
major_errors_count
minor_errors_count
missing_from_json_count
extra_in_json_count
wrong_graph_connections_count
judge_latency_seconds
input_json_valid
parsed_ok
prompt_file
prompt_sha256
classes_yaml_file
classes_yaml_sha256
short_explanation
```

### `judge_report.md`

Report leggibile con metodo usato, score, fedelta, spiegazione breve ed errori circuito per circuito.

### `raw_responses/`

Un file JSON per ogni circuito giudicato.

### `plots/`

Grafici generati:

```text
01_score_per_circuito.png
02_media_sottopunteggi_per_batch.png
03_distribuzione_decisioni_per_batch.png
```

Nota: i nomi `02_...` e `03_...` sono storici. Attualmente rappresentano il profilo errori e il breakdown dei sottopunteggi.

---

## 21. Aprire I Risultati Da Terminale

Aprire la cartella output su Windows:

```bash
explorer experiment_ai\verify_json_img\batchA\output_gpt5_4
```

Aprire il CSV:

```bash
start experiment_ai\verify_json_img\batchA\output_gpt5_4\judge_results.csv
```

Aprire il report Markdown:

```bash
start experiment_ai\verify_json_img\batchA\output_gpt5_4\judge_report.md
```

---

## 22. API Key

Lo script cerca `OPENAI_API_KEY` in questi punti:

```text
scripts/GPT/verifica_json_img/.env
experiment_ai/verify_json_img/.env
root_progetto/.env
```

Esempio:

```env
OPENAI_API_KEY=la_tua_api_key
```

---

## 23. Nota Metodologica

Questo judge valuta solo la corrispondenza tra:

```text
immagine originale del circuito
collegamenti terminale-terminale nel campo graph del Graph JSON
```

Il judge considera:

```text
endpoint/componenti necessari ai collegamenti
terminali, pin, polarita e ruoli terminali
collegamenti dichiarati nel campo graph
warning, OCR e semantica visibile solo se utili ai collegamenti
```

Punteggio:

```text
components: 0-10
terminals_pins: 0-25
graph_connections: 0-55
visible_semantics: 0-10
image_graph_fidelity_score: 0-100
```

Fedelta:

```text
VERY_HIGH
HIGH
MEDIUM
LOW
```

Non valuta:

```text
funzionamento elettrico del circuito
simulabilita
valori elettrici mancanti o diversi
reference designator mancanti
fusione globale dei simboli GND separati se il graph rispetta i fili visibili
```

Il JSON deve descrivere l'immagine, anche quando il circuito nell'immagine e elettricamente strano, incompleto o non simulabile.
