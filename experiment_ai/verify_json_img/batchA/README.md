# Batch A - verifica immagine / Graph JSON

Questa cartella contiene il Batch A usato nella verifica di coerenza tra immagini dei circuiti e campo `graph` dei Graph JSON.

## Cartelle principali

```text
images/
json/
output_gpt5_4_final_curated/
_archive_runs/
```

## Output finale da usare

La cartella finale per tabelle, grafici e relazione e:

```text
output_gpt5_4_final_curated/
```

Questa versione contiene il Batch A completo con i risultati finali selezionati:

- `a01-a06`, `a08`, `a10`: risultati dal run finale con prompt aggiornato;
- `a07`: risultato del rerun con reasoning effort `medium`, usato per correggere il falso positivo del run `low`;
- `a09`: risultato del rerun singolo con reasoning effort `medium`, usato per confermare il caso problematico.

File principali:

```text
output_gpt5_4_final_curated/judge_results.csv
output_gpt5_4_final_curated/judge_results.jsonl
output_gpt5_4_final_curated/judge_report.md
output_gpt5_4_final_curated/plots/
output_gpt5_4_final_curated/raw_responses/
```

## Run archiviati

La cartella `_archive_runs/` contiene esecuzioni intermedie o di controllo. Non usarle come risultato finale del Batch A, salvo per ricostruire la storia metodologica.

Contenuto:

```text
_archive_runs/output_gpt5_4_prompt_final_low/
_archive_runs/output_a07_a09_rerun_medium/
_archive_runs/output_a09_rerun_medium/
```

Significato:

- `output_gpt5_4_prompt_final_low`: run completo Batch A con prompt finale ed effort `low`;
- `output_a07_a09_rerun_medium`: rerun di controllo su `a07` e `a09` con effort `medium`;
- `output_a09_rerun_medium`: rerun singolo di conferma su `a09` con effort `medium`.

## Nota metodologica

Il caso `a07` era stato valutato `72 MEDIUM` nel run `low`, ma la revisione manuale e il rerun `medium` hanno indicato che si trattava di un falso positivo legato alla lettura del trasformatore. Per questo nel risultato finale `a07` e considerato `98 VERY_HIGH`.

Il caso `a09` e rimasto `MEDIUM` anche dopo rerun: il grafo contiene una fusione errata tra il nodo basso di `C1`/GND e il nodo `J1 pin4`/`R3`, oltre al mancato collegamento della lampada al proprio GND.

