# Comandi verifica immagine ↔ Graph JSON

Questo file raccoglie i comandi utili per eseguire il judge multimodale che confronta ogni immagine di circuito con il relativo **Graph JSON originale** prodotto dalla pipeline.

Il judge valuta solo la fedeltà tra immagine e JSON:

```text
immagine del circuito ↔ Graph JSON originale
```

Lo script non modifica il JSON, non trasforma il campo `graph` e non crea rappresentazioni alternative del grafo.

---

## 1. Struttura attesa della directory

Dalla root del progetto, la struttura attesa è:

```text
scripts/
└── GPT/
    └── verifica_json_img/
        └── judge_image_graph.py

experiment_ai/
└── verify_json_img/
    ├── prompt.txt
    ├── batchA/
    │   ├── images/
    │   │   ├── a01.png
    │   │   ├── a02.png
    │   │   └── ...
    │   └── json/
    │       ├── a01.json
    │       ├── a02.json
    │       └── ...
    ├── batchB/
    │   ├── images/
    │   └── json/
    ├── batchC1/
    │   ├── images/
    │   └── json/
    └── batchC2/
        ├── images/
        └── json/
```

Il nome dell'immagine e del JSON deve coincidere:

```text
a01.png ↔ a01.json
c16.jpg ↔ c16.json
```

---

## 2. Posizione del terminale

Questi comandi assumono che il terminale di VS Code sia aperto nella **root del progetto**, cioè nella cartella che contiene sia `scripts/` sia `experiment_ai/`.

Esempio:

```text
root_progetto/
├── scripts/
└── experiment_ai/
```

---

## 3. Controllo preliminare senza chiamare GPT

Da eseguire sempre per primo.

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --dry-run
```

Questo comando controlla che lo script trovi correttamente le coppie immagine/JSON.

Non consuma API.

Output atteso indicativo:

```text
Root: .../experiment_ai/verify_json_img
Prompt: .../experiment_ai/verify_json_img/prompt.txt
Output: .../experiment_ai/verify_json_img/output_gpt5_5
Modello: gpt-5.5
Coppie trovate: 10
- [A] a01: a01.png + a01.json
- [A] a02: a02.png + a02.json
...
```

---

## 4. Eseguire il judge su un solo circuito

Esempio su `a01`:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --only a01 --model gpt-5.5
```

Esempio su `c16`:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --only c16 --model gpt-5.5
```

Questo è il test più importante dopo il dry run. Serve per verificare che prompt, API key e output funzionino correttamente.

---

## 5. Eseguire il judge su più circuiti specifici

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --only a01,a02,a03 --model gpt-5.5
```

Lo script elabora solo i circuiti indicati nella lista separata da virgole.

---

## 6. Eseguire il judge su Batch A

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --batch A --model gpt-5.5
```

Forma equivalente:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --batch batchA --model gpt-5.5
```

---

## 7. Eseguire il judge su Batch B

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --batch B --model gpt-5.5
```

Forma equivalente:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --batch batchB --model gpt-5.5
```

---

## 8. Eseguire il judge su Batch C1

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --batch C1 --model gpt-5.5
```

Forma equivalente:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --batch batchC1 --model gpt-5.5
```

---

## 9. Eseguire il judge su Batch C2

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --batch C2 --model gpt-5.5
```

Forma equivalente:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --batch batchC2 --model gpt-5.5
```

---

## 10. Eseguire il judge su tutti i batch

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --model gpt-5.5
```

Elabora automaticamente tutti i batch trovati dentro:

```text
experiment_ai/verify_json_img/
```

quindi:

```text
batchA
batchB
batchC1
batchC2
```

se presenti.

---

## 11. Riprendere un'esecuzione interrotta

Se l'esecuzione si interrompe, puoi rilanciare usando `--resume`.

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --model gpt-5.5 --resume
```

Lo script riusa i risultati già presenti in:

```text
experiment_ai/verify_json_img/output_gpt5_5/raw_responses/
```

ed esegue solo quelli mancanti.

---

## 12. Limitare il numero di circuiti

Utile per fare test rapidi.

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --limit 3 --model gpt-5.5
```

Esegue solo i primi 3 circuiti trovati.

Puoi combinarlo anche con un batch:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --batch A --limit 3 --model gpt-5.5
```

---

## 13. Usare una cartella output personalizzata

Cartella output di default:

```text
experiment_ai/verify_json_img/output_gpt5_5/
```

Esempio con output dedicato al Batch A:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --batch A --model gpt-5.5 --out-dir experiment_ai/verify_json_img/output_batchA_gpt55
```

Esempio con output dedicato al Batch C2:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --batch C2 --model gpt-5.5 --out-dir experiment_ai/verify_json_img/output_batchC2_gpt55
```

---

## 14. Eseguire senza generare grafici

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --model gpt-5.5 --no-plots
```

Produce comunque:

```text
judge_results.jsonl
judge_results.csv
judge_report.md
raw_responses/
```

ma non crea la cartella `plots/`.

---

## 15. Impostare il dettaglio dell'immagine

Il default è:

```text
high
```

Comando esplicito:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --batch A --model gpt-5.5 --detail high
```

Per ridurre costo o latenza puoi usare:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --batch A --model gpt-5.5 --detail low
```

Oppure:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --batch A --model gpt-5.5 --detail auto
```

Per i circuiti elettrici, `high` è la scelta consigliata perché i pin e i collegamenti sono dettagli importanti.

---

## 16. Impostare reasoning effort

Il default dello script è:

```text
low
```

Comando esplicito:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --batch A --model gpt-5.5 --reasoning-effort low
```

Per circuiti più complessi puoi usare:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --batch C2 --model gpt-5.5 --reasoning-effort medium
```

Per un test particolarmente complesso:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --only c16 --model gpt-5.5 --reasoning-effort high
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

## 17. Aumentare il limite massimo dell'output

Default:

```text
3500 token
```

Per circuiti complessi:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --only c16 --model gpt-5.5 --max-output-tokens 5000
```

Per un intero batch complesso:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --batch C2 --model gpt-5.5 --max-output-tokens 5000
```

---

## 18. Usare un prompt personalizzato

Prompt di default:

```text
experiment_ai/verify_json_img/prompt.txt
```

Comando con prompt esplicito:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --prompt experiment_ai/verify_json_img/prompt.txt --batch A --model gpt-5.5
```

Esempio con prompt alternativo:

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --prompt experiment_ai/verify_json_img/prompt_v2.txt --batch A --model gpt-5.5
```

---

## 19. Comando consigliato per test completo minimo

Sequenza consigliata prima di lanciare tutto.

### Step 1 — Dry run

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --dry-run
```

### Step 2 — Test su un circuito semplice

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --only a01 --model gpt-5.5
```

### Step 3 — Test su un circuito complesso

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --only c16 --model gpt-5.5
```

### Step 4 — Batch A completo

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --batch A --model gpt-5.5
```

### Step 5 — Tutto il dataset

```bash
python scripts/GPT/verifica_json_img/judge_image_graph.py --root experiment_ai/verify_json_img --model gpt-5.5 --resume
```

---

## 20. File prodotti

Dopo l'esecuzione, nella cartella output vengono creati questi file:

```text
experiment_ai/verify_json_img/output_gpt5_5/
├── judge_results.jsonl
├── judge_results.csv
├── judge_report.md
├── raw_responses/
└── plots/
```

### `judge_results.jsonl`

Contiene il risultato completo circuito per circuito.

### `judge_results.csv`

Contiene la tabella sintetica usabile per analisi e grafici.

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
short_explanation
```

### `judge_report.md`

Report leggibile con score, decisioni, spiegazione breve ed errori circuito per circuito.

### `raw_responses/`

Contiene un file JSON per ogni circuito giudicato.

### `plots/`

Contiene i grafici finali:

```text
01_score_per_circuito.png
02_media_sottopunteggi_per_batch.png
03_distribuzione_decisioni_per_batch.png
```

---

## 21. Comandi per aprire i risultati da terminale

Aprire la cartella output su Windows:

```bash
explorer experiment_ai\verify_json_img\output_gpt5_5
```

Aprire il CSV con il programma predefinito:

```bash
start experiment_ai\verify_json_img\output_gpt5_5\judge_results.csv
```

Aprire il report Markdown con il programma predefinito:

```bash
start experiment_ai\verify_json_img\output_gpt5_5\judge_report.md
```

---

## 22. Variabile API key

Lo script cerca `OPENAI_API_KEY` in questi punti:

```text
scripts/GPT/verifica_json_img/.env
experiment_ai/verify_json_img/.env
experiment_ai/.env
root_progetto/.env
```

Esempio contenuto del file `.env`:

```env
OPENAI_API_KEY=la_tua_api_key
```

---

## 23. Nota metodologica

Questo judge valuta solo la corrispondenza tra:

```text
immagine originale del circuito
Graph JSON originale prodotto dalla pipeline
```

Valuta:

```text
componenti
terminali e pin
collegamenti dichiarati nel campo graph
semantica visibile
```

Produce un punteggio:

```text
image_graph_fidelity_score: 0–100
```

con decisione:

```text
PASS
MINOR_ISSUES
NEEDS_PATCH
FAIL
```

Lo script non modifica il JSON e non trasforma il campo `graph` in altri formati.
