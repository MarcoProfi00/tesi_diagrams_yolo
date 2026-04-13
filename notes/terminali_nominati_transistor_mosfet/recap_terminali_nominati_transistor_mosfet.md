# Recap tecnico - Terminali nominati per MOSFET e NPN Transistor

## Obiettivo

Questa modifica ha introdotto una rappresentazione piu` semantica dei terminali per:

- `Mosfet`
- `NPN_Transistor`

L'obiettivo era evitare di lasciare sempre i terminali come `t1`, `t2`, `t3`, almeno nei casi in cui il significato elettrico del pin puo` essere dedotto in modo affidabile dal simbolo.

In particolare:

- per il `Mosfet` si voleva distinguere `Gate (G)`, `Drain (D)` e `Source (S)`;
- per il `NPN_Transistor` si voleva distinguere `Base (B)`, `Collector (C)` ed `Emitter (E)`.

La modifica e` stata pensata per migliorare:

- la leggibilita` dei JSON intermedi e finali;
- la qualita` del grafo esportato;
- la comprensibilita` del `simplified.json` e del `llm_context.md`;
- la possibilita` futura di ragionare sul verso della corrente e sul ruolo dei terminali.

---

## Scelta progettuale

La scelta fatta non e` stata quella di rinominare sempre in modo rigido `t1/t2/t3`, ma di separare:

1. livello geometrico interno della pipeline;
2. livello semantico/elettrico mostrato all'utente.

Per questo motivo:

- `terminal_id` interno resta del tipo `16.1:t1`, `16.1:t2`, `18.2:t3`;
- vengono aggiunti campi semantici come:
  - `display_name`
  - `display_terminal_id`
  - `semantic_terminal_name`
  - `semantic_terminal_id`

In questo modo la pipeline mantiene stabilita` interna, ma negli output leggibili mostra i nomi corretti quando disponibili.

---

## Regole adottate

### 1. NPN Transistor

Per `NPN_Transistor` e` stata implementata una strategia semantica dedicata:

- il lato singolo del simbolo viene interpretato come `Base (B)`;
- tra gli altri due rami:
  - il ramo con la freccia viene interpretato come `Emitter (E)`;
  - l'altro ramo viene interpretato come `Collector (C)`.

Questa regola e` stata giudicata sufficientemente robusta sul dataset `topology_v7_npn_transistor_mosfet`.

Inoltre e` stato aggiunto un fallback specifico per i casi in cui il probe generico della freccia fosse ambiguo.

### 2. MOSFET

Per `Mosfet` e` stata adottata una strategia piu` conservativa.

Regola finale:

- il lato singolo viene sempre interpretato come `Gate (G)`;
- `Source (S)` e `Drain (D)` vengono assegnati solo se la freccia del simbolo e` abbastanza chiara;
- se la freccia non e` affidabile, i due terminali restano `t2` e `t3`.

Questa scelta e` stata presa per evitare di assegnare `Source` e `Drain` in modo arbitrario nei casi ambigui.

In pratica:

- casi buoni: `G`, `S`, `D`
- casi dubbi: `G`, `t2`, `t3`

---

## File modificati

### 1. `metadata/class_terminals_v1.yaml`

Sono state aggiunte le strategie semantiche per le due classi:

- `Mosfet`
- `NPN_Transistor`

Per il MOSFET la strategia finale e`:

- `mosfet_gate_with_optional_source_drain`

Per il transistor NPN la strategia finale e`:

- `npn_emitter_from_arrow_branch`

Inoltre sono stati definiti i ruoli semantici:

- `Mosfet`: `G`, `S`, `D`
- `NPN_Transistor`: `B`, `E`, `C`

### 2. `scripts/pipeline/estimate_terminals/config.py`

Sono stati aggiunti parametri per:

- soglia di confidenza della freccia;
- fallback specifico del transistor NPN;
- gestione conservativa di `Source/Drain` per i MOSFET.

### 3. `scripts/pipeline/estimate_terminals/strategies_three_terminal.py`

E` il file principale della modifica.

Qui e` stata implementata la logica che:

- risolve semanticamente i terminali dei componenti a 3 pin;
- assegna `B/C/E` per il transistor NPN;
- assegna `G` sempre per i MOSFET;
- assegna `S/D` ai MOSFET solo sopra soglia di confidenza.

### 4. `scripts/pipeline/estimate_terminals/processor.py`

Questo passo propaga i nuovi campi semantici nei terminali del `03`.

### 5. `scripts/pipeline/estimate_terminals/debug_draw.py`

Le immagini di debug del `03` ora mostrano `display_terminal_id` invece del solo `terminal_id`.

Quindi nei casi affidabili si vedono etichette come:

- `16.1:G`
- `16.1:D`
- `16.1:S`
- `18.2:B`
- `18.2:E`
- `18.2:C`

---

## Propagazione ai passi successivi

Dopo aver introdotto i nomi semantici nel `03`, sono stati riallineati anche i passi successivi.

### Passo 04 - `04_extract_wires.py`

Non e` stata necessaria una modifica logica: il passo 04 copia gia` i terminali dal `03`.

E` stato comunque rilanciato per mantenere i JSON aggiornati.

### Passo 05 - `05_builds_nets.py`

Sono stati propagati:

- `display_terminal_id`
- `semantic_terminal_name`
- `semantic_terminal_id`

Inoltre:

- il debug `terminal_debug` usa il nome leggibile del terminale;
- le net salvano anche:
  - `connected_terminal_display_ids`
  - `connected_semantic_terminal_names`

### Passo 06 - `06_match_terminals_to_nets.py`

Sono stati propagati gli stessi campi nei terminali finali e nelle `connections`.

Anche il debug finale del matching terminale-net ora usa il nome leggibile.

### Passo 07 - `07_export_graph.py`

Qui e` stata fatta la parte piu` importante lato esportazione:

- i nodi terminale del `graph_json` hanno label leggibili;
- il `simplified.json` usa i nomi semantici nei terminali e nelle frasi;
- il `llm_context.md` descrive le connessioni usando `G/S/D` e `B/C/E` quando disponibili.

### Passo 08 - `08_visualize_graph.py`

Non e` stata necessaria una logica nuova: e` stato rigenerato tutto il materiale visivo e scaricabile usando gli export aggiornati del passo 07.

---

## Comportamento finale della pipeline

### NPN Transistor

Output atteso:

- `t1` geometrico -> `B`
- ramo con freccia -> `E`
- altro ramo -> `C`

Negli output leggibili:

- `18.2:B`
- `18.2:E`
- `18.2:C`

### MOSFET

Output atteso:

- lato singolo -> `G`
- se la freccia e` affidabile:
  - `S`
  - `D`
- se la freccia non e` affidabile:
  - il gate resta `G`
  - gli altri due restano `t2` e `t3`

Negli output leggibili si hanno quindi due situazioni:

1. caso affidabile:
   - `16.1:G`
   - `16.1:D`
   - `16.1:S`

2. caso ambiguo:
   - `16.1:G`
   - `16.1:t2`
   - `16.1:t3`

---

## Dataset usato per sviluppo e verifica

Le modifiche sono state sviluppate e testate principalmente sul dataset:

- `topology_v7_npn_transistor_mosfet`

Questo dataset e` stato utile perche' contiene:

- casi con molti MOSFET;
- casi con transistor NPN;
- casi misti;
- casi facili e casi ambigui.

In particolare:

- `img2` e `img4` sono stati usati per verificare l'assegnazione di `Source/Drain` nei MOSFET quando la freccia era presente;
- `img7` e` stato usato come caso limite per lasciare `t2/t3` quando la freccia non era abbastanza affidabile;
- i transistor NPN dello stesso batch sono stati usati per verificare la coerenza di `Base/Emitter/Collector`.

---

## Effetto sugli output finali

Dopo questa modifica, la pipeline `03 -> 08` produce output piu` leggibili.

### Esempi di miglioramento

Prima:

- `16.1:t1`
- `16.1:t2`
- `16.1:t3`

Dopo, nei casi affidabili:

- `16.1:G`
- `16.1:D`
- `16.1:S`

Per i transistor NPN:

- `18.2:B`
- `18.2:E`
- `18.2:C`

Questo migliora:

- il debug visivo;
- la lettura dei JSON;
- il grafo esportato;
- il `simplified.json`;
- il `llm_context.md`;
- l'uso finale dei dati come input per un LLM.

---

## Considerazioni finali

La modifica non si limita a un cambio estetico dei nomi dei terminali.

Ha introdotto una distinzione importante tra:

- localizzazione geometrica del terminale;
- interpretazione elettrica del terminale.

Questa distinzione permette di:

- mantenere robusta la pipeline;
- non rompere gli ID interni gia` usati nei passaggi intermedi;
- rendere gli output finali piu` vicini al linguaggio con cui un umano legge il circuito.

La scelta piu` importante e` stata quella di essere:

- robusti per i transistor NPN;
- conservativi per i MOSFET.

Quindi:

- il transistor viene nominato semanticamente quando la regola e` affidabile;
- il MOSFET viene nominato completamente solo quando la freccia supporta davvero la scelta;
- nei casi dubbi si evita di introdurre etichette sbagliate.

Questo e` un buon compromesso tra accuratezza topologica e correttezza semantica.
