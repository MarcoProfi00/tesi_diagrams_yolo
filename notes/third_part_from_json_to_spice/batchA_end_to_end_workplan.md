# Batch A end-to-end workplan

Questo file non e piu un piano grezzo di implementazione.

Adesso serve come workplan compatto e aggiornato del percorso Batch A dopo la
chiusura di:

- Esperimento 1;
- Esperimento 2;
- riallineamento dei markdown di analisi;
- riallineamento della roadmap generale Pipeline 2.0.

## Obiettivo del documento

Tenere in una pagina sola il quadro operativo del Batch A:

- cosa e gia stato chiuso;
- quali artefatti sono il riferimento ufficiale;
- cosa resta da fare prima di passare davvero all'Esperimento 3;
- in che ordine conviene muoversi.

## Stato attuale del Batch A

Il Batch A e oggi il banco di prova end-to-end piu completo del progetto.

Abbiamo gia un flusso reale che copre:

```text
Graph JSON
-> Pipeline 2.0
-> netlist SPICE
-> ngspice
-> contesto diagnostico
-> chat locale
-> agente diagnostico
-> scenari controllati
-> documentazione manuale degli esperimenti
-> tabella risultati comparabile
```

In pratica il Batch A non e piu solo "set di test tecnico", ma il riferimento
principale per:

- qualita della pipeline;
- comportamento dell'agente;
- comportamento delle primitive scenario;
- struttura dei report della tesi.

## Convenzione cartelle output

Sul Batch A manteniamo volutamente sia la root canonica sia le root
sperimentali.

Struttura attesa:

```text
outputs/pipeline2.0/batchA/
  a01 ... a10
  experiment1/
  experiment2/
  experiment2_feed_nodes/
```

Significato:

- `a01 ... a10` = baseline tecnica canonica della Pipeline 2.0;
- `experiment1/` = copia esplicita dell'Esperimento 1;
- `experiment2/` e `experiment2_feed_nodes/` = workspace/snapshot separati
  usati per le varianti dell'Esperimento 2;
- questa duplicazione e metodologica e voluta, non va letta come disordine da
  pulire automaticamente.

## Riferimenti ufficiali

### 1. Roadmap generale

File principale:

```text
notes/third_part_from_json_to_spice/ROADMAP_TEMP_ESPERIMENTI_PIPELINE2.md
```

Qui vive la sequenza ufficiale degli esperimenti:

- Esperimento 1 = baseline Batch A
- Esperimento 2 = scenari piu potenti / netlist editing controllato
- Esperimento 3 = viewer / simulatore visuale
- Esperimento 4 = automazione agentica

### 2. Documento agente

File principale:

```text
notes/third_part_from_json_to_spice/agente_diagnostico_pipeline2.md
```

Qui vive la descrizione piu completa di:

- ruolo dell'agente;
- manifest diagnostico;
- chat locale;
- scenario registry;
- primitive scenario;
- ordine logico degli sviluppi futuri.

### 3. Report circuiti

Directory di riferimento:

```text
experiment_ai/pipeline2_spice_analysis/batchA/
```

Qui vivono:

- markdown `experiment1`
- markdown `experiment2`
- README locali
- tabella risultati minima comparabile

File chiave:

```text
experiment_ai/pipeline2_spice_analysis/batchA/RESULTS_TABLE_TEMPLATE.md
```

## Esperimento 1 - stato

Stato: chiuso.

Significato:

- Pipeline 2.0 eseguita sul Batch A;
- web chat locale attiva;
- agente read-only attivo;
- scenari controllati semplici eseguiti;
- documentazione manuale completata circuito per circuito.

Output ufficiali:

```text
experiment_ai/pipeline2_spice_analysis/batchA/experiment1/
```

Nota importante:

- `a03` resta un caso speciale di fallimento SPICE/topology issue;
- ma ora anche `a03` e stato riallineato al template strutturato degli altri
  circuiti.

## Esperimento 2 - stato

Stato: sostanzialmente chiuso sul Batch A.

Significato:

- i circuiti prioritari del Batch A sono stati provati con primitive piu forti;
- la chat e experiment-aware;
- la chat history file-based e attiva;
- il registry scenari locale e attivo;
- gli scenari restano sempre separati dalla base run;
- i risultati sono stati documentati e trasformati in tabella comparabile.

Primitive consolidate nel runner:

```text
drive_node_voltage
change_source_value
change_component_value
close_switch
connect_nodes
feed_nodes_from_source_node
add_voltage_source_between_nodes
add_resistor_between_nodes
```

Varianti realmente validate su Batch A:

- `a01`
  - `experiment2_connect_nodes`
  - `experiment2_feed_nodes_from_source_node`
- `a02`
  - `experiment2_connect_nodes`
- `a05`
  - `experiment2_add_voltage_source_between_nodes`
- `a07`
  - `experiment2_add_voltage_source_between_nodes`
- `a08`
  - `experiment2_add_resistor_between_nodes`
- `a09`
  - `experiment2_connect_nodes`
  - `experiment2_feed_nodes_from_source_node`
- `a10`
  - `experiment2_connect_nodes`
  - `experiment2_feed_nodes_from_source_node`

Casi non avviati o non prioritari in Experiment 2:

- `a04` = non avviato
- `a06` = non avviato
- `a03` = escluso per ora, per complessita topologica/image-assisted

## Struttura risultati consolidata

Oggi il Batch A ha una struttura minima confrontabile.

La tabella risultati usa una riga per:

```text
(circuito, variante sperimentale)
```

non piu semplicemente:

```text
(circuito, experiment2 generico)
```

Questo permette di distinguere correttamente, per esempio:

- `experiment2_connect_nodes`
- `experiment2_feed_nodes_from_source_node`
- `experiment2_add_voltage_source_between_nodes`
- `experiment2_add_resistor_between_nodes`

Questa scelta e importante per la tesi, perche evita di nascondere primitive o
varianti riuscite dentro note secondarie.

## Cosa e gia solido

Le parti oggi abbastanza stabili sono:

- output 01-08 della Pipeline 2.0;
- `10_diagnostic_context.json` come manifest leggero;
- `11_agent_readonly.py` come agente grounded;
- `12_controlled_scenarios.py` come runner scenario;
- chat history locale di Experiment 2;
- scenario registry locale di Experiment 2;
- markdown analitici Batch A;
- tabella minima comparabile dei risultati;
- roadmap generale degli esperimenti.

In altre parole, prima di passare oltre non serve "reinventare" il Batch A.

Serve usare bene quello che e gia stato consolidato.

## Prossimo blocco di lavoro

Il prossimo blocco non e piu Experiment 2.

Il prossimo blocco e:

```text
Esperimento 3 = viewer / simulatore visuale
```

Regola centrale:

```text
il viewer parte dalla netlist della run selezionata
```

Questo implica:

- base run e scenario run devono poter essere visualizzate entrambe;
- se cambia la topologia dello scenario, deve cambiare anche la topologia
  mostrata;
- il viewer non deve essere pensato come grafica fissa di un solo circuito.

## Dopo il viewer

Solo dopo il viewer conviene passare a:

```text
Esperimento 4 = automazione agentica
```

L'idea e:

- prima miglioriamo l'osservabilita umana del sistema;
- poi aumentiamo l'autonomia decisionale dell'agente.

Questo ordine oggi e considerato piu solido del precedente.

## Cosa non fare adesso

Per non far deragliare il progetto:

- non riaprire artificialmente Experiment 2 sul Batch A senza una nuova
  domanda sperimentale forte;
- non introdurre subito automazione agentica completa;
- non complicare il runner con troppe primitive nuove non ancora motivate;
- non moltiplicare documenti paralleli con stati diversi;
- non costruire il viewer assumendo una sola topologia fissa per circuito.

## Checklist pratica

Prima di partire davvero con Experiment 3, il progetto Batch A dovrebbe essere
considerato pronto se:

- [x] Esperimento 1 documentato
- [x] Esperimento 2 documentato
- [x] `a03` riallineato al template
- [x] tabella risultati compilata
- [x] roadmap aggiornata
- [x] documento agente aggiornato
- [ ] workplan viewer definito in modo operativo
- [ ] prima specifica concreta del viewer

## Sintesi finale

Il Batch A oggi va letto cosi:

```text
baseline chiusa
-> scenari forti consolidati
-> risultati documentati e confrontabili
-> prossimo passo = viewer
-> passo successivo = automazione agentica
```

Frase guida:

```text
Batch A non e piu il luogo in cui capire se la Pipeline 2.0 esiste;
e il luogo in cui stabilizzare come raccontarla, confrontarla e usarla per
aprire il viewer e poi l'automazione.
```
