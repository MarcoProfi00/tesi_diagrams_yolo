# Capitolo 4 - Valutazione sperimentale: mappa concettuale

## Scopo e stato del documento

Questa è la **roadmap per scrivere il Capitolo 4**, non il capitolo già redatto. Organizza gli esperimenti e gli artefatti effettivamente presenti nel repository in una sequenza che permetta di valutare separatamente i singoli stadi e, infine, il comportamento dell'applicativo completo.

- **Titolo del capitolo:** `\chapter{Valutazione sperimentale}`.
- **Label:** `\label{chap:valutazione-sperimentale}`.
- **Ricognizione delle fonti:** 29 settembre 2026, branch `develop`, allineato al commit `67c01859`.
- **Modello editoriale:** [mappa del Capitolo 3](03_problem_statement_soluzione_proposta_mappa.md), dalla quale riprendere lessico, denominazioni degli stadi e livello di dettaglio.
- **Regola di evidenza:** riportare soltanto numeri ricavabili dai report consolidati, dai CSV finali o dagli output delle run; lasciare come punto da verificare ciò che non è dimostrato dagli artefatti.
- **Regola narrativa:** ogni blocco deve rispondere a una domanda sperimentale, descrivere il setup minimo necessario, presentare risultati e casi qualitativi, quindi dichiarare le cautele. Non trasformare il capitolo in un inventario di script o in una cronaca dello sviluppo.

Il capitolo deve seguire il percorso reale della tesi:

```text
dataset e detector
    -> Graph JSON e verifica topologica
    -> benchmark diagnostico preliminare
    -> Graph JSON parametrizzato, netlist e simulazione SPICE
    -> traiettorie CHAT e AGENT
    -> judge finale, discussione trasversale e limiti
```

La valutazione non è un unico esperimento end-to-end con una sola metrica. I cinque nuclei usano unità di analisi e riferimenti diversi: immagini annotate per il detector, coppie immagine–Graph JSON per la topologia, risposte diagnostiche per il benchmark preliminare, circuiti simulati per la Pipeline 2.0 e traiettorie complete per CHAT/AGENT. Questa distinzione va mantenuta esplicita per evitare di sommare score non confrontabili.

## Confine con i Capitoli 3 e 5

| Capitolo | Domanda centrale | Materiale da includere | Materiale da evitare |
| --- | --- | --- | --- |
| 3 — Problema e soluzione proposta | Quale problema viene affrontato e come funziona la soluzione? | Architettura, algoritmi, contratti dati, prompt e rubriche come metodo, configurazioni necessarie. | Classifiche complete, percentuali di successo, analisi degli errori e conclusioni prestazionali. |
| 4 — Valutazione sperimentale | Quanto funziona ciascuno stadio, in quali condizioni e con quali limiti? | Setup effettivi, metriche, risultati numerici, figure, casi positivi/negativi, costi, latenze e minacce alla validità. | Nuove scelte architetturali non motivate nel Capitolo 3; generalizzazioni oltre i campioni osservati. |
| 5 — Conclusioni e sviluppi futuri | Che cosa è stato dimostrato nel complesso e come proseguire? | Sintesi dei contributi, risposta finale agli obiettivi, sviluppi futuri prioritari. | Ripetizione di tutte le tabelle del Capitolo 4 o introduzione di risultati non presentati prima. |

Il Capitolo 4 può richiamare brevemente il funzionamento di YOLO, Graph JSON, SPICE e dei judge soltanto per rendere interpretabile l'esperimento. Le descrizioni algoritmiche complete restano nel Capitolo 3. Il Capitolo 5 dovrà ricevere da questo capitolo una sintesi già prudente: risultati osservati nel perimetro studiato, non una certificazione universale del sistema.

## Gerarchia delle fonti e distinzione tra risultati canonici e storici

Prima della stesura, applicare questa gerarchia:

1. **output grezzi e CSV finali della run**, quando identificano inequivocabilmente il campione e la configurazione;
2. **report consolidati**, quando dichiarano come sono stati selezionati e aggregati gli output;
3. **figure generate dai CSV finali**, controllando lo script generatore;
4. **documenti di lavoro, roadmap e presentazioni**, utili per ricostruire il percorso ma non per introdurre nuovi numeri.

| Nucleo | Fonti canoniche | Materiale storico o secondario da non usare come fonte numerica primaria |
| --- | --- | --- |
| Object detection | `CAPITOLO_RISULTATI_OBJECT_DETECTION.md`, `results_comparison_summary.md`, report per famiglia e `outputs/yolo*/.../results.*`; checkpoint operativo `exp11b1`. | PDF `electrical_symbols_yolo_thesis_summary.pdf`; run preliminare `exp11b_yolo11_rgb_aug_strong_v3`; slide. |
| Verifica topologica | Quattro `judge_results.csv` finali; per A esclusivamente `output_gpt5_4_final_curated`, per B/C1/C2 `output_gpt5_4`; report consolidato. | `batchA/_archive_runs`, rerun non selezionati, grafici di singole prove precedenti. |
| Benchmark diagnostico | `experiment_ai/circuiti_complessi/batch_v1/_aggregate` e `batch_v2/_aggregate`; report `RISULTATI_DIAGNOSI_CIRCUITI_COMPLESSI.md`; script di aggregazione/grafici. | Risposte isolate non incluse negli aggregati, slide e conclusioni provvisorie di un solo batch. |
| Pipeline 2.0 | Artefatti dei 21 casi finali nei workspace `chat_agent_evaluation` e `ic_chat_agent_evaluation`, `dataset/circuits.csv`, riferimenti tecnici e run SPICE; report finale CHAT/AGENT per i conteggi di scenario. | `ROADMAP_TEMP_ESPERIMENTI_PIPELINE2.md`, Experiment 1–5 e copie `batchA/experiment*` come storia dello sviluppo, salvo casi scelti e riallineati agli artefatti finali. |
| CHAT/AGENT e judge finale | 21 reference, 42 summary, 42 packet e 42 risultati in `experiment_ai/chat_agent_evaluation_21`; CSV in `results/tables`; `RESULTS_TABLES.md`. | `judge_results_process_calibrated`, piloti, README quando descrive ancora attività future; copie nelle presentazioni. |

**Discrepanze da esplicitare, non da nascondere:**

- il benchmark YOLO consolidato dichiara 628 immagini con split 440/126/62 e 1.625 istanze di validation; la revisione finale `dataset_v3` documentata nel Capitolo 3 contiene 627 immagini con split 439/126/62 e annotazioni aggiornate;
- `exp11b` nelle tabelle finali è la run corretta `exp11b1_yolo11_rgb_aug_strong_v3`; la precedente `exp11b_yolo11_rgb_aug_strong_v3` non va contata come sedicesima configurazione;
- nel Batch A della verifica topologica, `a07` e `a09` sono risultati curati provenienti da rerun a reasoning `medium`, mentre gli altri risultati selezionati sono a `low`;
- il benchmark preliminare sceglie `gpt-5.4-mini` come compromesso operativo, ma tutte le 42 traiettorie finali archiviate dichiarano `gpt-5.4`; il judge finale dichiara `gpt-5.5` con reasoning `medium`;
- i 21 judge CHAT e i 21 judge AGENT condividono lo stesso schema di risposta ma non lo stesso hash del prompt. Il confronto fra modalità è quindi descrittivo e secondario.

## Domande sperimentali del capitolo

Usare domande esplicite, richiamabili nella discussione finale.

| ID | Domanda sperimentale | Evidenza principale |
| --- | --- | --- |
| RQ1 | Quale famiglia YOLO e quale variante dei dati offrono il miglior compromesso fra riconoscimento e localizzazione dei simboli? | 15 training, metriche di validation, curve e analisi qualitativa. |
| RQ2 | Quanto fedelmente la Pipeline 1.0 conserva nel Graph JSON componenti, terminali e collegamenti visibili? | Judge multimodale su 38 circuiti, score/sottoscore, decisioni ed errori. |
| RQ3 | Quale modello linguistico e quale contesto risultano più adatti alla diagnosi preliminare per qualità, costo e latenza? | 256 risposte: 16 circuiti × 8 modelli × 2 condizioni informative. |
| RQ4 | La Pipeline 2.0 trasforma i grafi validati in netlist e run SPICE tecnicamente eseguibili? | 21 simulazioni di base, disponibilità degli output `.tran`, 4 casi IC e 81 scenari finali. |
| RQ5 | Le modalità CHAT e AGENT producono traiettorie diagnostiche utili, supportate dagli scenari eseguiti e dalle misure? | 42 traiettorie, judge finale a cinque criteri, esiti ed errori critici. |
| RQ6 | Quali errori persistono lungo la catena e quali conclusioni end-to-end sono giustificate? | Discussione trasversale, casi limite e minacce alla validità. |

## Indice proposto

```text
4  Valutazione sperimentale
   4.1 Obiettivi, domande e protocollo generale
       4.1.1 Articolazione della valutazione e unità di analisi
       4.1.2 Metriche, criteri di aggregazione e riproducibilità
   4.2 Valutazione dell'object detection
       4.2.1 Dataset, varianti e configurazione degli addestramenti
       4.2.2 Confronto tra YOLOv7, YOLOv8 e YOLO11
       4.2.3 Selezione del checkpoint e analisi qualitativa
   4.3 Valutazione della ricostruzione topologica
       4.3.1 Corpus e protocollo del judge immagine–Graph JSON
       4.3.2 Risultati aggregati e confronto tra batch
       4.3.3 Errori topologici e casi critici
   4.4 Benchmark preliminare dei modelli diagnostici
       4.4.1 Disegno del confronto e modelli valutati
       4.4.2 Qualità diagnostica, Top-1/Top-3 e contributo dell'immagine
       4.4.3 Costo, latenza e scelta operativa
   4.5 Verifica tecnica della Pipeline 2.0 e delle simulazioni
       4.5.1 Corpus e simulabilità delle configurazioni di base
       4.5.2 Robustezza dell'esecuzione degli scenari
   4.6 Valutazione delle modalità CHAT e AGENT
       4.6.1 Corpus finale, riferimenti tecnici e protocollo del judge
       4.6.2 Risultati complessivi e per modalità
       4.6.3 Analisi dei criteri, degli errori e dei casi rappresentativi
   4.7 Discussione trasversale
       4.7.1 Risposta alle domande sperimentali
       4.7.2 Relazione fra qualità degli stadi e prestazioni complessive
       4.7.3 Limiti e minacce alla validità
   4.8 Sintesi dei risultati e raccordo alle conclusioni
```

La struttura usa otto sezioni e diciannove sottosezioni. Il benchmark preliminare rimane prima della Pipeline 2.0 perché documenta la fase in cui è stata studiata l'utilità diagnostica del Graph JSON e del contesto multimodale; la valutazione CHAT/AGENT viene invece dopo SPICE perché giudica traiettorie che includono scenari realmente simulati.

---

## 4.1 Obiettivi, domande e protocollo generale

**Scopo:** dare al lettore la mappa della valutazione prima dei risultati e impedire che score eterogenei siano letti come un'unica misura di accuratezza.

### 4.1.1 Articolazione della valutazione e unità di analisi

**Domanda locale:** quali parti del sistema sono valutate e quale oggetto costituisce una singola osservazione?

**Sequenza dei paragrafi**

1. Richiamare in poche righe il percorso del Capitolo 3.
2. Presentare RQ1–RQ6 e spiegare la valutazione modulare.
3. Distinguere dataset, unità di analisi, riferimento e output per ogni esperimento.

| Livello | Unità di analisi | Campione | Riferimento | Output della valutazione |
| --- | --- | ---: | --- | --- |
| Detector | Predizioni su validation per una run | 15 configurazioni | bbox/classi annotate | Precision, recall, F1, mAP. |
| Pipeline 1.0 | Coppia immagine–Graph JSON | 38 circuiti | immagine + vocabolario terminali | Score 0–100, decisione, errori, usabilità. |
| Diagnosi preliminare | Risposta modello–circuito–input | 256 risposte | judge con immagine, grafo, sintomo e documentazione | Score 0–21, Top-1/Top-3, errori, costo e latenza. |
| Pipeline 2.0 | Circuito parametrizzato e run SPICE | 21 basi; 81 scenari finali | reference tecniche e artefatti elettrici | Esito tecnico e disponibilità degli output `.op`/`.tran`. |
| CHAT/AGENT | Traiettoria completa | 42 run | reference tecnica per circuito | 5 criteri 0–2, esito, criticità. |

**Cautela:** questi campioni si sovrappongono solo in parte. I 38 circuiti topologici, i 16 circuiti del benchmark e i 21 circuiti finali non devono essere descritti come un unico test set invariato dall'immagine alla diagnosi.

### 4.1.2 Metriche, criteri di aggregazione e riproducibilità

**Domanda locale:** come vengono calcolati e interpretati i risultati?

**Setup da dichiarare**

- versione o identificativo delle fonti usate;
- criterio di selezione del checkpoint YOLO: massimo `mAP@0.5:0.95` di validation;
- media, mediana, deviazione standard e conteggi soltanto quando presenti o ricalcolabili dai CSV finali;
- costo e latenza come proprietà delle chiamate osservate, non come listino o benchmark stabile;
- judge, reasoning effort, schema e hash quando disponibili;
- definizione distinta di riuscita tecnica, risultato utile e successo pieno.

**Tabella consigliata:** una tabella compatta “Matrice della valutazione” derivata da quella precedente, aggiungendo le principali minacce: singolo split/singola run, assenza di gold topologica, judge LLM, modelli SPICE e interazione utente.

**Non fare:** introdurre una media complessiva fra mAP, score topologico, score diagnostico 0–21 e punteggio finale 0–10.

---

## 4.2 Valutazione dell'object detection

**RQ1:** quale famiglia YOLO e quale variante dei dati offrono il miglior compromesso fra riconoscimento e localizzazione dei simboli?

### 4.2.1 Dataset, varianti e configurazione degli addestramenti

**Setup verificato da riportare**

- benchmark consolidato: 628 immagini, 32 classi, split 440 training / 126 validation / 62 test;
- validation: 1.625 istanze secondo il report consolidato;
- input 1024 × 1024, 100 epoche, batch 4, GPU Tesla T4 16 GB;
- 3 famiglie × 5 varianti = 15 configurazioni;
- varianti training: RGB 440, grayscale 440, `aug_v1` 880, `aug_v2_compose` 726, `aug_v3 strong` 880;
- augmentation applicata offline soltanto al training; validation e test invariati;
- per YOLOv8/YOLO11: pesi pre-addestrati, optimizer automatico, seed 0 e modalità deterministica secondo il report; alcune sessioni riprese da `last.pt`.

**Metriche:** precision, recall, F1 armonico, `mAP@0.5`, `mAP@0.5:0.95`, best epoch.

**Risultati da non anticipare qui:** tenere setup e risultati in sottosezioni separate.

**Tabella 4.2-A:** split e varianti. Se il Capitolo 3 ha già una tabella completa del dataset finale, qui mostrare solo ciò che serve a capire il benchmark e aggiungere una nota sul diverso snapshot 628/627.

**Cautela fondamentale:** il repository non dimostra che tutte le run abbiano usato byte per byte lo stesso snapshot. Il report consolidato attribuisce il benchmark a 628 immagini; il nome della directory in `exp11b1/args.yaml` richiama l'export successivo. Finché non viene recuperato il manifest effettivo di ogni training, scrivere “split dichiarato dal report consolidato”, non “identico snapshot verificato per tutte le run”.

### 4.2.2 Confronto tra YOLOv7, YOLOv8 e YOLO11

**Risultati numerici principali**

| Famiglia/configurazione scelta per la famiglia | Precision | Recall | F1 | mAP@0.5 | mAP@0.5:0.95 |
| --- | ---: | ---: | ---: | ---: | ---: |
| YOLOv7 `exp03b`, strong | 0,8568 | 0,8854 | 0,8709 | 0,8972 | 0,6059 |
| YOLOv8 `exp08`, compose | 0,8515 | 0,8671 | 0,8592 | 0,8818 | 0,6024 |
| YOLO11 `exp11b`, strong | 0,9379 | 0,8967 | 0,9168 | 0,9559 | 0,6687 |

La tabella completa delle 15 configurazioni è già verificata nel report e deve comparire nel capitolo o in appendice. Nel testo evidenziare:

- YOLO11 occupa le prime cinque posizioni per `mAP@0.5:0.95`;
- `exp11` massimizza precision 0,9436, recall 0,9005 e F1 0,9215;
- `exp11b` massimizza `mAP@0.5` 0,9559 e `mAP@0.5:0.95` 0,6687;
- la migliore YOLO11 supera la migliore YOLOv7 di 0,0628 sulla mAP severa e la migliore YOLOv8 di 0,0662;
- grayscale migliora le mAP rispetto alle baseline RGB nelle tre famiglie, ma non migliora uniformemente precision/recall/F1;
- compose è competitivo in YOLOv8 ma peggiora YOLO11 rispetto alla sua baseline sulla mAP severa;
- strong favorisce YOLOv7 e YOLO11, non produce lo stesso beneficio complessivo in YOLOv8.

**Figure disponibili**

1. `bar_chart_map5095.png`: ranking delle 15 run per mAP severa;
2. `bar_chart_f1_score.png`: ranking per F1;
3. `scatter_precision_recall.png`: bilanciamento precision–recall, con dimensione legata alla mAP severa secondo il report;
4. evitare di usare simultaneamente tre grafici che ripetono la stessa classifica: tenere bar mAP + scatter nel corpo, F1 eventualmente in appendice.

**Analisi qualitativa:** spiegare che le differenze fra `exp11` e `exp11b` sono piccole e non supportate da repliche; è invece più solido il distacco fra famiglia YOLO11 e famiglie precedenti.

### 4.2.3 Selezione del checkpoint e analisi qualitativa

**Decisione verificata:** checkpoint operativo YOLO11 `exp11b`, cartella sorgente `exp11b1_yolo11_rgb_aug_strong_v3`, best epoch 59, selezionato per la migliore localizzazione media; la pipeline usa `weights/best.pt`.

**Confronto finale:** rispetto a `exp11`, `exp11b` perde 0,0057 in precision, 0,0037 in recall e 0,0047 in F1, ma guadagna 0,0046 in `mAP@0.5` e 0,0134 in `mAP@0.5:0.95`.

**Figure disponibili**

- `results.png`: andamento di loss e metriche nelle 100 epoche;
- `BoxPR_curve.png` e `BoxF1_curve.png`;
- `confusion_matrix_normalized.png`;
- coppia `val_batch0_labels.jpg` / `val_batch0_pred.jpg`.

**Analisi qualitativa da sviluppare**

- diagonale elevata della matrice per molte classi;
- fragilità su classi rare o ambigue, indicate nel report: `Antenna`, `Analog_Meter`, `Switch`, `Terminal`;
- impatto maggiore degli scostamenti di bbox su simboli piccoli e tratti sottili;
- soglia F1 aggregata prossima a confidence 0,467; soglia pipeline generale 0,40 con adattamenti per classe.

**Cautele**

- una run per configurazione e un solo split: nessuna deviazione tra seed o significatività statistica;
- forte sbilanciamento di classe;
- risultati riportati sul validation set, non sul test set;
- una migliore mAP di detection non dimostra automaticamente una migliore ricostruzione topologica.

---

## 4.3 Valutazione della ricostruzione topologica

**RQ2:** quanto fedelmente la Pipeline 1.0 conserva nel Graph JSON componenti, terminali e collegamenti visibili?

### 4.3.1 Corpus e protocollo del judge immagine–Graph JSON

**Setup verificato**

- 38 circuiti: A=10, B=10, C1=10, C2=8;
- ingressi: immagine, Graph JSON e vocabolario `class_terminals_v1.yaml`;
- judge `gpt-5.4`, dettaglio immagine `high`, output JSON vincolato;
- reasoning ordinario `low`; `a07` e `a09` del Batch A selezionati da rerun `medium` dopo audit;
- prompt hash abbreviato `19f1ee29c0c6`, vocabolario hash abbreviato `7e5491a8cdf0` secondo il report;
- nessuna netlist topologica gold indipendente.

**Rubrica**

| Criterio | Massimo |
| --- | ---: |
| Componenti | 10 |
| Terminali/pin | 25 |
| Collegamenti del grafo | 55 |
| Semantica visibile | 10 |
| Totale | 100 |

Decisioni: `VERY_HIGH` 90–100, `HIGH` 75–89, `MEDIUM` 55–74, `LOW` 0–54, con regole di coerenza; campo separato `usable_as_graph_base`.

**Figura disponibile:** `fig00_flusso_verifica_topologica.svg/png`. È una figura di metodo; inserirla solo se la spiegazione del Capitolo 3 non è sufficiente.

**Cautela terminologica:** chiamare il numero “score di fedeltà assegnato dal judge”, non “accuratezza topologica percentuale”.

### 4.3.2 Risultati aggregati e confronto tra batch

**Risultati verificati**

| Batch | N | Media | Mediana | Dev. std. campionaria | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 10 | 93,000 | 97,000 | 9,043 | 74 | 98 |
| B | 10 | 89,500 | 92,000 | 8,114 | 70 | 95 |
| C1 | 10 | 93,600 | 95,000 | 5,777 | 78 | 98 |
| C2 | 8 | 93,625 | 94,500 | 3,420 | 86 | 97 |
| Totale | 38 | 92,368 | 95,000 | 7,023 | 70 | 98 |

Distribuzione complessiva:

- `VERY_HIGH`: 32/38 = 84,21%;
- `HIGH`: 4/38 = 10,53%;
- `MEDIUM`: 2/38 = 5,26%;
- `LOW`: 0/38;
- almeno `HIGH`: 36/38 = 94,74%;
- `usable_as_graph_base=true`: 38/38.

Sottopunteggi medi complessivi: componenti 9,763/10; terminali/pin 22,263/25; collegamenti 51,605/55; semantica visibile 8,737/10.

**Figure da usare**

1. `fig01_distribuzione_score_per_batch.svg`: boxplot + punti, con casi anomali annotati;
2. `fig02_distribuzione_decisioni_per_batch.svg`: barre normalizzate;
3. non inserire nel corpo tutti i grafici duplicati prodotti per i singoli batch; usarli per l'analisi o in appendice.

**Interpretazione:** la presenza dei componenti è il nucleo più stabile; terminali/pin e semantica richiedono lettura più fine. Il Batch B ha media più bassa e maggiore concentrazione di errori maggiori; C2 è il più compatto.

### 4.3.3 Errori topologici e casi critici

**Conteggi verificati**

- errori critici: 2;
- errori maggiori: 33;
- errori minori: 56;
- segnalazioni mancanti dal JSON: 24;
- segnalazioni aggiunte nel JSON: 11;
- collegamenti giudicati errati: 29.

I conteggi non sono mutuamente esclusivi e una run può contenere più errori. Non dividerli per 38 per produrre un'“error rate” non definita.

**Casi qualitativi da selezionare dal report**

- `a09` e `b06`: casi che abbassano maggiormente A e B e contengono gli errori critici;
- `a07`: esempio di falso positivo del judge iniziale corretto mediante audit;
- `c08` e `c09`: casi annotati nella figura complessiva;
- almeno un caso `VERY_HIGH` per mostrare che cosa conserva correttamente il Graph JSON.

**Analisi da sviluppare:** distinguere `net fuse`, `net split`, terminale mancante, ruolo/polarità errati e imprecisione semantica senza impatto sulla connettività. Collegare ogni tipologia al possibile effetto sul binding SPICE, senza affermare che l'errore si sia propagato in una diagnosi finale se non documentato.

**Cautele**

- riferimento visivo, non ground truth annotata arco per arco;
- judge multimodale singolo e rerun selettivi su due casi;
- 38 circuiti non casuali;
- immagine ambigua e incroci senza nodo possono richiedere interpretazione;
- “utilizzabile come base” non significa “simulabile senza correzioni”.

---

## 4.4 Benchmark preliminare dei modelli diagnostici

**RQ3:** quale modello e quale contesto risultano più adatti per qualità, costo e latenza?

### 4.4.1 Disegno del confronto e modelli valutati

**Setup verificato**

- due batch da 8 circuiti, per un totale di 16 circuiti differenti;
- 8 modelli: `gpt-5.4`, `gpt-5.4-mini`, `gpt-5-mini`, `gpt-4.1-mini`, `gpt-5.4-nano`, `gpt-5-nano`, `gpt-4o-mini`, `gpt-4.1-nano`;
- due input: Graph JSON + datasheet; Graph JSON + immagine + datasheet;
- 16 × 8 × 2 = 256 risposte, una per combinazione;
- nel Batch v2, `b03` e `b06` non dispongono dell'estratto datasheet; l'assenza è dichiarata al modello;
- judge multimodale con score massimo 21 su sette criteri, Top-1/Top-3, errori maggiori e allucinazioni;
- costi riportati per il modello generativo, judge escluso.

**Tabella consigliata:** matrice sperimentale con circuiti per batch, disponibilità datasheet e numero di risposte. Evitare una tabella lunga con tutte le 256 righe nel corpo.

**Figura disponibile:** `fig00_processo_sperimentale.svg/png`.

**Cautela:** Top-1 e Top-3 sono assegnate rispetto alle cause attese ricostruite dal judge, non rispetto alle reference tecniche congelate usate nel benchmark finale CHAT/AGENT.

### 4.4.2 Qualità diagnostica, Top-1/Top-3 e contributo dell'immagine

**Confronto fra batch**

| Indicatore | Batch v1 | Batch v2 |
| --- | ---: | ---: |
| Risposte | 128 | 128 |
| Score medio /21 | 15,805 | 15,125 |
| Top-1 | 60,2% | 53,1% |
| Top-3 | 85,2% | 85,2% |
| Errori maggiori medi | 2,125 | 2,320 |
| Allucinazioni medie | 2,070 | 2,219 |
| Costo medio modello [USD] | 0,015124 | 0,013743 |
| Latenza media [s] | 32,00 | 27,98 |

**Prestazioni aggregate sui 16 circuiti**

| Modello | Score medio /21 | Top-1 | Top-3 | Errori maggiori | Allucinazioni | Costo medio USD | Latenza s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-5.4` | 19,125 | 78,1% | 90,6% | 0,812 | 0,875 | 0,071603 | 52,63 |
| `gpt-5.4-mini` | 18,094 | 84,4% | 90,6% | 0,969 | 1,281 | 0,017092 | 19,01 |
| `gpt-5-mini` | 17,562 | 62,5% | 96,9% | 1,562 | 1,875 | 0,008235 | 41,02 |
| `gpt-4.1-mini` | 15,719 | 59,4% | 78,1% | 2,312 | 2,500 | 0,006373 | 33,77 |
| `gpt-5.4-nano` | 14,844 | 50,0% | 84,4% | 2,688 | 2,281 | 0,005170 | 20,50 |
| `gpt-5-nano` | 13,562 | 40,6% | 87,5% | 3,156 | 3,312 | 0,001825 | 28,24 |
| `gpt-4o-mini` | 12,531 | 43,8% | 78,1% | 3,219 | 2,188 | 0,003671 | 27,52 |
| `gpt-4.1-nano` | 12,281 | 34,4% | 75,0% | 3,062 | 2,844 | 0,001501 | 17,23 |

**Effetto dell'immagine, aggregato su 128 coppie**

- JSON + datasheet: score 15,305, Top-1 54,7%, Top-3 85,2%, errori maggiori 2,258, allucinazioni 2,094, costo 0,013687 USD, latenza 30,60 s;
- JSON + immagine + datasheet: score 15,625, Top-1 58,6%, Top-3 85,2%, errori maggiori 2,188, allucinazioni 2,195, costo 0,015181 USD, latenza 29,38 s;
- l'immagine migliora 61 coppie, non cambia 23 e peggiora 44;
- delta medio: +0,320 punti e +3,9 p.p. Top-1, Top-3 invariata;
- costo multimodale +10,9%; la latenza osservata −1,22 s non va interpretata causalmente;
- delta modello: `gpt-5.4-mini` +1,438, `gpt-5.4` +1,250, `gpt-5-mini` −0,625.

**Figure consigliate dal materiale esistente**

1. unificare i due batch o usare una figura per score medio modello derivata dai CSV congiunti;
2. grafico Top-1/Top-3 per modello;
3. scatter score–costo;
4. grafico delta immagine per circuito, scegliendo eventualmente `c17` (+2,750 nel v2) e `c02` (−2,750) come casi opposti;
5. heatmap modello × circuito in appendice, non necessariamente nel corpo.

Gli script `make_main_figures.py` e `make_appendix_figures.py` producono attualmente figure separate per ciascun batch. Per una figura congiunta bisogna generare un nuovo CSV/plot a partire dai due `all_runs.csv`, conservando lo script e senza trascrivere manualmente i valori.

### 4.4.3 Costo, latenza e scelta operativa

**Conclusione verificata del benchmark:**

- `gpt-5.4` è il riferimento di qualità assoluta;
- `gpt-5.4-mini` viene scelto nel report come compromesso operativo: 94,6% dello score medio di `gpt-5.4`, Top-1 84,4%, Top-3 90,6%, costo −76,1%, latenza −63,9%;
- `gpt-5-mini` è l'alternativa più economica, ma ha Top-1 inferiore di 21,9 p.p., più errori e latenza più alta rispetto a `gpt-5.4-mini`.

**Cautela centrale per il raccordo:** questa è una scelta motivata dal benchmark esplorativo. Le traiettorie finali CHAT/AGENT archiviate risultano generate da `gpt-5.4`, non da `gpt-5.4-mini`. Non scrivere che il benchmark “ha selezionato il modello poi usato nell'agente finale” senza spiegare questa differenza.

**Altri limiti:** una sola risposta per combinazione; batch composti da circuiti differenti; due casi senza datasheet; prezzi e latenza temporalmente variabili; judge dinamico; possibile dipendenza fra modello candidato e modello valutatore.

---

## 4.5 Verifica tecnica della Pipeline 2.0 e delle simulazioni

**RQ4:** la Pipeline 2.0 trasforma i grafi parametrizzati in netlist e simulazioni SPICE tecnicamente eseguibili?

Questa sezione deve essere un ponte tecnico breve fra il benchmark su Graph JSON e la valutazione diagnostica finale. Non deve ripetere la parametrizzazione, il binding dei modelli o la generazione della netlist già descritti nel Capitolo 3, né anticipare l'analisi delle traiettorie della §4.6. La verifica riguarda la simulabilità osservata nel corpus finale: una run completata da ngspice attesta la riuscita tecnica dell'esecuzione, non la correttezza fisica del modello né quella della diagnosi.

### 4.5.1 Corpus e simulabilità delle configurazioni di base

**Risultati da riportare**

- 21 circuiti: 17 senza IC e 4 con IC;
- 21/21 run SPICE di base concluse con `status: success`;
- 16/21 configurazioni con output transitorio, coerentemente con i casi che prevedono un'analisi `.tran`.

I quattro casi con circuiti integrati e la disponibilità del viewer possono essere richiamati in una sola nota descrittiva del corpus, senza una sottosezione o una valutazione autonoma: non è stato svolto uno user study del viewer. Anche in presenza di convergenza e output, i modelli, i valori, il pin mapping, il testbench e gli eventuali override restano assunzioni controllate; il risultato non certifica il comportamento fisico del circuito reale.

### 4.5.2 Robustezza dell'esecuzione degli scenari

Nelle traiettorie finali sono stati eseguiti 81 scenari:

- CHAT: 40/40 run SPICE riuscite;
- AGENT: 40/41 run SPICE riuscite;
- totale: 80/81 run riuscite, pari al 98,8%;
- unico fallimento tecnico: `a08` AGENT, `agent_scenario_2`, con errore `Timestep too small` sul nodo `n003`.

Il tasso del 98,8% descrive la robustezza tecnica dell'orchestrazione nel campione osservato. Non misura la validità dello scenario scelto, la correttezza delle forme d'onda o l'interpretazione diagnostica: questi aspetti appartengono alla §4.6. Se utile alla leggibilità, riportare una sola tabella compatta con consistenza del corpus, successi delle basi e successi degli scenari per modalità. Non è richiesta alcuna figura.

---

## 4.6 Valutazione delle modalità CHAT e AGENT

**RQ5:** le traiettorie complete producono prove, interpretazioni e conclusioni tecnicamente utili?

### 4.6.1 Corpus finale, riferimenti tecnici e protocollo del judge

**Setup verificato**

- 21 circuiti × 2 modalità = 42 traiettorie;
- 21 reference tecniche YAML, 42 summary, 42 packet e 42 risultati ufficiali;
- tutte le traiettorie dichiarano modello `gpt-5.4`;
- judge `gpt-5.5`, reasoning `medium`, cinque criteri 0–2, massimo descrittivo 10;
- esito separato: `success`, `partial_success`, `failure`, `inconclusive`, `technical_failure`;
- criticità: `false_success`, `unsupported_claim`, `wrong_interpretation`;
- schema hash comune `2a6c8bb...`; prompt hash CHAT `c73bff5f...`, AGENT `05304a55...`;
- 20/21 domande iniziali identiche; `b03` adattata mantenendo l'obiettivo tecnico;
- CHAT contiene 83 turni intermedi dell'utente; AGENT 58 decisioni autonome.

**Definizione da mantenere:** “risultato utile” = successo + successo parziale. Un successo parziale può includere una criticità e richiede supervisione; non è sinonimo di diagnosi corretta e completa.

**Figure di metodo disponibili:** `fig01_flusso_applicativo.svg` e `fig02_processo_valutazione.svg`. La prima potrebbe essere già stata usata/adattata nel Capitolo 3; evitare duplicazioni. La seconda è più pertinente al setup del judge.

### 4.6.2 Risultati complessivi e per modalità

**Tabella principale verificata**

| Modalità | Run | Successi | Parziali | Fallimenti | Risultati utili | Media /10 | Mediana | Run critiche |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| CHAT | 21 | 11 (52,4%) | 10 (47,6%) | 0 | 21 (100,0%) | 7,81 | 8 | 5 (23,8%) |
| AGENT | 21 | 5 (23,8%) | 15 (71,4%) | 1 (4,8%) | 20 (95,2%) | 6,38 | 6 | 12 (57,1%) |
| Complessivo | 42 | 16 (38,1%) | 25 (59,5%) | 1 (2,4%) | 41 (97,6%) | 7,10 | 7 | 17 (40,5%) |

**Punteggi medi per criterio**

| Criterio | CHAT /2 | AGENT /2 | Totale /2 |
| --- | ---: | ---: | ---: |
| Correttezza diagnostica | 1,67 | 1,43 | 1,55 |
| Qualità dei test | 1,62 | 1,52 | 1,57 |
| Interpretazione delle evidenze | 1,57 | 1,24 | 1,40 |
| Raggiungimento dell'obiettivo | 1,52 | 1,29 | 1,40 |
| Qualità della conclusione | 1,43 | 0,90 | 1,17 |

**Errori critici**

- `false_success`: CHAT 0, AGENT 1;
- `unsupported_claim`: CHAT 1, AGENT 10;
- `wrong_interpretation`: CHAT 5, AGENT 10;
- le occorrenze non coincidono con il numero di run critiche.

**Figure disponibili**

1. `fig03_distribuzione_esiti` — indispensabile;
2. `fig04_punteggi_medi_criteri` — mostra chiaramente il punto debole della conclusione AGENT;
3. `fig05_distribuzione_punteggi_totali` — utile solo se non duplica la tabella appaiata;
4. costruire eventualmente dal `table_02_paired_results.csv` un grafico appaiato per circuito, mantenendo il confronto descrittivo.

**Judge cost:** 295.392 input token, 91.136 cached, 89.511 output di cui 45.412 reasoning; costo stimato totale 3,7522 USD secondo la tariffa dichiarata nel report. Presentarlo come costo del judge finale, separato dal costo di generazione delle traiettorie e dai costi del benchmark preliminare.

### 4.6.3 Analisi dei criteri, degli errori e dei casi rappresentativi

**Lettura principale**

- la qualità dei test è il criterio più forte di AGENT (1,52/2);
- la qualità della conclusione è il più debole (0,90/2);
- la fragilità principale non è l'esecuzione degli scenari, ma il passaggio da misura a causalità e conclusione;
- CHAT beneficia della selezione e dei follow-up dell'utente; non attribuire causalmente l'intero divario alla sola “superiorità” della modalità.

**Casi positivi da raccontare**

- `a05` CHAT: sorgente test 5 V su N003; N003 e N001 passano da 0 V a 5 V, localizzando l'ingresso non pilotato;
- `a01` AGENT: N002 passa da 0 a circa 5 V, corrente lampada da 0 a 4,76 mA e LED resta a circa 19,40 mA;
- `ic01` AGENT: tre scenari, ipotesi iniziali scartate e regolarizzazione del transitorio.

**Successi parziali**

- `a02` CHAT: localizzazione utile ma nessuno scenario unico verifica l'intera correzione;
- `b04` AGENT: scenari pertinenti ma uso della grandezza sbagliata; il transitorio di riferimento mostra corrente media batteria circa 0,164 A a 12 V, 0,678 A a 10 V e 1,281 A a 8 V, con picchi fino a circa 0,985/2,955/4,941 A.

**Fallimento**

- `c02` AGENT, 2/10: la base alterna già i LED con periodo circa 0,600 s e frequenza 1,668 Hz; la modifica da 10 µF a 1 µF accelera l'alternanza. Il profilo automatico 166,7 Hz è un artefatto, mentre il controllo stabile dà circa 16,69 Hz. La conclusione dichiara una falsa correzione: presenti tutte e tre le criticità.

**Cautela:** i valori dei casi vanno sempre ricontrollati nel summary, nella reference e nell'output SPICE della stessa run prima di copiarli nel `.tex`.

---

## 4.7 Discussione trasversale

### 4.7.1 Risposta alle domande sperimentali

Preparare una tabella finale RQ → risposta → evidenza → limite.

| RQ | Risposta sostenibile | Evidenza | Limite immediato |
| --- | --- | --- | --- |
| RQ1 | YOLO11 è la famiglia più forte; `exp11b` massimizza le mAP e viene integrato. | 15 run di validation. | Singola run/split; test non riportato. |
| RQ2 | I grafi sono generalmente fedeli e correggibili. | Score judge 92,368 medio; 36/38 almeno HIGH; 38/38 usable. | Non è graph accuracy contro gold. |
| RQ3 | `gpt-5.4` massimizza qualità; `gpt-5.4-mini` è il compromesso del benchmark. | 256 risposte, score/costo/latenza. | Una risposta per combinazione; judge e prezzi variabili. |
| RQ4 | Il flusso SPICE è tecnicamente eseguibile nel corpus finale. | 21/21 basi; 80/81 scenari. | Modelli/testbench controllati, non hardware reale. |
| RQ5 | Le due modalità producono quasi sempre un contributo utile; AGENT è più fragile nella conclusione. | 41/42 utili; criteri e criticità. | Successo parziale non equivale a soluzione completa; confronto descrittivo. |
| RQ6 | La modularità permette di localizzare gli errori, ma non elimina la propagazione e le integrazioni manuali. | Errori topologici, override, casi finali. | Nessun benchmark end-to-end totalmente non supervisionato. |

### 4.7.2 Relazione fra qualità degli stadi e prestazioni complessive

**Punti da argomentare con cautela**

1. La localizzazione YOLO è necessaria per terminali e maschere, ma il repository non contiene un ablation che colleghi quantitativamente mAP e score topologico.
2. Lo score topologico elevato rende il Graph JSON una base utile; non garantisce valori, modelli, pin mapping o riferimento di massa.
3. Il benchmark preliminare dimostra che il JSON contiene informazione diagnostica utile e che l'immagine può aiutare, ma non sempre.
4. La Pipeline 2.0 introduce conoscenza dichiarativa e correzioni controllate; la diagnosi finale parte da artefatti verificati, non da un flusso completamente cieco.
5. Il tasso tecnico 98,8% degli scenari è distinto dal 38,1% di successi pieni: la simulazione può riuscire mentre l'interpretazione è errata.
6. L'autonomia riduce l'interazione ma aumenta la necessità di controlli sulla conclusione; il dato osservato non autorizza una superiorità generale di CHAT su ogni possibile esecuzione.

**Figura facoltativa:** una matrice “stadio → errore → controllo → impatto possibile”, più utile di un nuovo diagramma di flusso generale.

### 4.7.3 Limiti e minacce alla validità

Organizzare le minacce in quattro gruppi.

**Validità interna**

- singola run/seed per training e per combinazione LLM;
- rerun selettivi `a07/a09` nella verifica topologica;
- prompt judge differenti fra CHAT e AGENT;
- interventi informativi dell'utente in CHAT;
- `b03` con domanda iniziale adattata;
- possibili artefatti numerici (`c02`).

**Validità di costrutto**

- mAP non equivale a qualità topologica;
- score LLM-as-a-Judge non equivale ad accuracy gold;
- `usable_as_graph_base` non equivale a simulabilità;
- run SPICE riuscita non equivale a comportamento fisico o diagnosi corretta;
- “risultato utile” include successi parziali;
- equivalenti elettrici non misurano direttamente luminosità o volume percepito.

**Validità esterna**

- dataset di 32 classi, sbilanciato e non rappresentativo di ogni stile di schema;
- 38 casi topologici, 16 casi benchmark e 21 casi finali selezionati, non campioni casuali;
- soltanto quattro casi IC e tre famiglie di macromodello;
- nessuna validazione sistematica su circuiti fisici;
- prezzi, modelli API e latenza possono cambiare.

**Validità conclusiva e riproducibilità**

- assenza di intervalli di confidenza e test statistici;
- snapshot dataset dei training non completamente ricostruito;
- reference tecniche costruite e controllate manualmente, senza più esperti indipendenti;
- judge LLM unico per ciascun protocollo e possibile variabilità;
- hash e artefatti migliorano l'audit ma non eliminano bias e dipendenze software.

---

## 4.8 Sintesi dei risultati e raccordo alle conclusioni

Chiudere in tre paragrafi, senza aggiungere nuove metriche:

1. ricomporre i risultati dei cinque nuclei, distinguendo sempre successo tecnico, fedeltà e utilità diagnostica;
2. identificare il punto di forza: catena modulare, ispezionabile e capace di trasformare ipotesi in scenari SPICE tracciati;
3. identificare il limite dominante: interpretazione e causalità della conclusione, insieme alla dipendenza da rappresentazioni validate e integrazioni manuali; rinviare al Capitolo 5 implicazioni e sviluppi.

Non concludere che il sistema “diagnostica correttamente nel 97,6% dei casi”. La formulazione sostenibile è: **41 delle 42 traiettorie osservate contengono almeno un contributo giudicato utile; soltanto 16 sono successi pieni e 17 presentano almeno una criticità.**

---

## Piano delle figure

Limitare il corpo del capitolo a circa 10–13 figure sostanziali, spostando heatmap e grafici per singolo batch in appendice. La §4.5 non richiede figure: un eventuale richiamo al viewer o ai casi IC resta testuale.

| ID proposto | Contenuto | Sezione | Fonte/stato |
| --- | --- | --- | --- |
| `fig:valutazione-mappa` | Livelli, campioni e riferimenti della valutazione | §4.1 | Da costruire, se la tabella non basta. |
| `fig:od-map5095` | Ranking mAP@0.5:0.95 delle 15 run | §4.2.2 | `bar_chart_map5095.png`. |
| `fig:od-pr` | Scatter precision–recall | §4.2.2 | `scatter_precision_recall.png`; verificare che la dimensione rappresenti davvero la mAP nello script/versione usata. |
| `fig:od-training` | Curve della run scelta | §4.2.3 | `exp11b1/.../results.png`. |
| `fig:od-confusion` | Matrice normalizzata | §4.2.3 | `confusion_matrix_normalized.png`. |
| `fig:topo-score` | Distribuzione score per batch | §4.3.2 | SVG finale dai quattro CSV canonici. |
| `fig:topo-decisioni` | Decisioni qualitative normalizzate | §4.3.2 | SVG finale. |
| `fig:benchmark-modelli` | Score/Top-1/Top-3 congiunti sui 16 circuiti | §4.4.2 | Da rigenerare sui due aggregati. |
| `fig:benchmark-immagine` | Delta immagine, con casi opposti | §4.4.2 | Figure per batch esistenti; valutare nuova figura congiunta. |
| `fig:benchmark-costo` | Score vs costo | §4.4.3 | Figure esistenti per batch; nuova figura congiunta preferibile. |
| `fig:judge-finale` | Summary + reference → packet → judge | §4.6.1 | `fig02_processo_valutazione.svg`. |
| `fig:esiti-chat-agent` | Distribuzione esiti | §4.6.2 | `fig03_distribuzione_esiti`. |
| `fig:criteri-chat-agent` | Medie dei cinque criteri | §4.6.2 | `fig04_punteggi_medi_criteri`. |

**Regole grafiche**

- preferire SVG/PDF quando disponibile;
- mantenere palette e terminologia coerenti;
- ogni figura deve dichiarare fonte, unità, aggregazione e denominatore;
- non usare grafici del Batch A archiviato o output pilota;
- controllare la leggibilità in stampa e non affidare l'informazione al solo colore.

## Piano delle tabelle

| ID proposto | Contenuto | Fonte |
| --- | --- | --- |
| `tab:valutazione-livelli` | Unità, campioni, riferimento, metriche | Questa mappa + fonti finali. |
| `tab:od-configurazioni` | 15 run YOLO | `results_comparison_summary.md`. |
| `tab:od-finalisti` | `exp11` vs `exp11b` | Report consolidato. |
| `tab:topologia-batch` | Media/mediana/deviazione/min/max e decisioni | Quattro CSV finali. |
| `tab:topologia-errori` | Severità e tipologie | Report consolidato/CSV. |
| `tab:benchmark-modelli` | Otto modelli, qualità/costo/latenza | Aggregati v1+v2. |
| `tab:benchmark-input` | JSON vs JSON+immagine | Aggregati congiunti. |
| `tab:pipeline2-indicatori` | Corpus, successi delle basi e successi tecnici degli scenari per modalità | Artefatti finali + `table_01_run_results.csv`. |
| `tab:chat-agent-summary` | Esiti e punteggi per modalità | `table_03_mode_summary.csv`. |
| `tab:chat-agent-criteri` | Cinque criteri | `table_04_criteria_summary.csv`. |
| `tab:minacce-validita` | Minaccia, effetto, mitigazione | Sintesi della §4.7.3. |

La tabella completa dei 42 punteggi può essere collocata in appendice; nel corpo usare il riepilogo compatto della Pipeline 2.0, i risultati CHAT/AGENT per criterio e 3–5 casi diagnostici rappresentativi.

## Fonti operative per la stesura

### Object detection

- [report consolidato](../first_part_object_detection/CAPITOLO_RISULTATI_OBJECT_DETECTION.md);
- [confronto globale](../first_part_object_detection/results_comparison_summary.md);
- [YOLOv7](../first_part_object_detection/results_yolov7.md), [YOLOv8](../first_part_object_detection/results_yolov8.md), [YOLO11](../first_part_object_detection/results_yolov11.md);
- `outputs/yolo7`, `outputs/yolo8`, `outputs/yolo11`;
- `scripts/results_yolo/plots_from_results.py` e script di augmentation.

### Pipeline 1.0 e verifica topologica

- [report consolidato](../second_part_pipeline_topologica/RISULTATI_VERIFICA_TOPOLOGICA_GRAPH_JSON.md);
- `experiment_ai/verify_json_img/batchA/output_gpt5_4_final_curated/judge_results.csv`;
- equivalenti finali per B/C1/C2;
- `scripts/GPT/verifica_json_img/judge_image_graph.py`;
- `scripts/GPT/verifica_json_img/make_thesis_figures.py`.

### Benchmark diagnostico preliminare

- [report consolidato](../second_part_pipeline_topologica/RISULTATI_DIAGNOSI_CIRCUITI_COMPLESSI.md);
- `experiment_ai/circuiti_complessi/batch_v1/_aggregate`;
- `experiment_ai/circuiti_complessi/batch_v2/_aggregate`;
- `scripts/GPT/aggregate_judge_results.py`, `make_judge_tables.py`, `make_graph_csvs.py`;
- `scripts/GPT/plot_graphics_result_gpt/make_main_figures.py` e `make_appendix_figures.py`.

### Pipeline 2.0 e corpus finale

- `experiment_ai/chat_agent_evaluation_21/dataset/circuits.csv`, `components.csv`, `runs.csv`;
- `experiment_ai/chat_agent_evaluation_21/references/*.yaml`;
- `outputs/demo_workspaces/chat_agent_evaluation/pipeline2.0`;
- `outputs/demo_workspaces/ic_chat_agent_evaluation/pipeline2.0`;
- [riferimento script Pipeline 2.0](../third_part_from_json_to_spice/pipeline2_scripts_reference.md);
- [README corpus finale](../../experiment_ai/chat_agent_evaluation_21/README.md), da verificare contro gli output quando parla di stato futuro.

### CHAT/AGENT e judge finale

- [tabelle finali e limiti](../third_part_from_json_to_spice/risultati_agente/RESULTS_TABLES.md);
- [bozza narrativa consolidata](../third_part_from_json_to_spice/risultati_agente/CAPITOLO_RISULTATI.md);
- `experiment_ai/chat_agent_evaluation_21/results/tables/*.csv`;
- `evaluation`, `judge_inputs`, `judge_results`, `references`;
- `build_case_summaries.py`, `build_judge_packets.py`, `build_dataset.py`, `run_judge.py`;
- `build_result_figures.py` e `build_application_flow.py`.

## Punti da verificare prima della stesura definitiva

1. **Snapshot dei training YOLO:** recuperare, se possibile, manifest/hash o log di scansione che confermino il dataset effettivo di ogni run; altrimenti mantenere la cautela 628/627.
2. **Test set object detection:** verificare se esiste una valutazione finale separata sui 62 test; non presentare i risultati di validation come test.
3. **Per-class metrics:** decidere se includere una tabella delle classi rare; ricavarla dal checkpoint selezionato, non da osservazioni visive soltanto.
4. **Scatter OD:** lo script mostrato nel repository non dimensiona i punti con la mAP, mentre la caption consolidata lo afferma. Rigenerare/correggere figura o caption.
5. **Pipeline 2.0:** verificare sugli artefatti finali i conteggi sintetici del corpus, delle run di base e degli output transitori; non costruire un inventario esteso se non serve alla tracciabilità.
6. **Scenario fallito:** ricontrollare e documentare `a08` AGENT `agent_scenario_2`, terminato con `Timestep too small` su `n003`; non confonderlo con `c02` AGENT, il cui scenario SPICE riuscì ma fu interpretato male.
7. **Modello diagnostico:** spiegare perché il benchmark seleziona `gpt-5.4-mini` ma il corpus finale usa `gpt-5.4`, se esiste una motivazione documentata; in assenza, limitarsi a dichiarare le configurazioni effettive.
8. **Judge finale:** mantenere i due hash di prompt e lo stesso hash di schema; non affermare prompt identico tra modalità.
9. **Costo:** specificare data/tariffa o dichiarare il calcolo come stima storica delle chiamate registrate.
10. **Reference tecniche:** preferire “riferimenti tecnici controllati” a “ground truth indipendente” se non viene documentato un processo cieco e multi-esperto.
11. **Numeri dei casi:** ricontrollare tutte le misure qualitative (`a01`, `a05`, `b04`, `c02`, `ic01`) sui JSON/CSV sorgente prima del LaTeX.
12. **Duplicati dei risultati finali:** scegliere come sorgente editoriale primaria `experiment_ai/chat_agent_evaluation_21/results`; le copie in `notes/.../risultati_agente` devono rimanere allineate ma non vanno contate due volte.
13. **Numero di figure:** decidere quali grafici congiunti rigenerare per evitare due serie quasi identiche Batch v1/v2.
14. **Raccordo al Capitolo 5:** concordare se “sviluppi futuri” includerà test end-to-end non supervisionato, gold topologica, repliche multi-seed, più IC e validazione hardware.

## Ordine operativo della futura stesura

1. Congelare le tabelle sorgente e risolvere i punti 1–9 sopra.
2. Generare i grafici congiunti del benchmark e verificare la tabella compatta degli indicatori della Pipeline 2.0.
3. Scrivere §4.1 e §4.2 usando i report consolidati.
4. Scrivere §4.3 direttamente dai quattro CSV finali.
5. Scrivere §4.4 dagli aggregati congiunti, separando qualità e costo.
6. Scrivere §4.5 come breve ponte tecnico dagli artefatti finali, con al massimo una tabella e senza figure obbligatorie.
7. Scrivere §4.6 dalle tabelle ufficiali e verificare i casi sul materiale sorgente.
8. Scrivere §4.7 soltanto dopo avere stabilizzato tutte le sezioni di risultato.
9. Uniformare decimali, percentuali, nomi dei modelli, label e caption.
10. Eseguire un audit finale numero → tabella/figura → file sorgente.

## Checklist finale

- [ ] Il capitolo usa titolo e label richiesti.
- [ ] Ogni sezione dichiara domanda, unità di analisi, campione e riferimento.
- [ ] I risultati YOLO sono indicati come validation, salvo prova separata sul test.
- [ ] `exp11b` è associato alla run corretta `exp11b1` e la run preliminare non è duplicata.
- [ ] Lo snapshot 628/627 è spiegato senza inventare equivalenze.
- [ ] Lo score topologico non è chiamato accuracy e sono dichiarati i rerun curati.
- [ ] Il benchmark preliminare distingue JSON da JSON+immagine e judge preliminare da reference finali.
- [ ] Costi e latenze hanno unità, denominatore e cautela temporale.
- [ ] La Pipeline 2.0 ha una sezione breve con due sole sottosezioni: simulabilità delle basi e robustezza degli scenari.
- [ ] Viewer e casi IC sono soltanto una nota del corpus; la valutazione diagnostica è rinviata alla §4.6.
- [ ] Riuscita ngspice, correttezza elettrica e successo diagnostico sono distinti.
- [ ] Le 42 traiettorie finali sono attribuite a `gpt-5.4` e il judge a `gpt-5.5`.
- [ ] CHAT e AGENT non sono presentati come confronto controllato perfettamente simmetrico.
- [ ] “Risultato utile” è definito come successo + parziale e non come diagnosi completa.
- [ ] Gli errori critici sono discussi insieme ai punteggi, non nascosti dalla media.
- [ ] Ogni misura di un caso qualitativo proviene dalla stessa run citata.
- [ ] Figure e tabelle hanno fonte, denominatore e caption coerenti.
- [ ] Nessun output pilota, archivio o documento temporaneo entra nei risultati canonici.
- [ ] Le minacce alla validità coprono aspetti interni, di costrutto, esterni e conclusivi.
- [ ] La sintesi risponde a RQ1–RQ6 senza generalizzare oltre i campioni.
- [ ] Il Capitolo 4 prepara le conclusioni del Capitolo 5 senza anticiparne la discussione progettuale futura.
