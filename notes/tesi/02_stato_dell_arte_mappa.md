# Capitolo 2 - Stato dell'arte: mappa dei contenuti

## Scopo del documento

Questa è una mappa di lavoro, non una bozza del capitolo. Deve rimanere allineata alla struttura effettivamente adottata nel file `chapter2.tex` e serve a tenere traccia di:

- filo logico del capitolo;
- sezioni e sottosezioni effettive;
- contenuti già scritti;
- lavori e fonti realmente utilizzati;
- figure già inserite;
- argomenti ancora da sviluppare;
- confine con i Capitoli 3 e 4.

## Stato della ricognizione bibliografica

- **Data di chiusura provvisoria della ricerca:** 1 settembre 2026.
- I documenti Word, PowerPoint e Markdown della repository sono materiale di orientamento: nella tesi si citano paper, standard, dataset e documentazione ufficiale originari.
- I risultati quantitativi del progetto sviluppato nella tesi non appartengono a questo capitolo.
- I preprint molto recenti del 2026 devono essere qualificati come tali quando non esiste una versione pubblicata.
- La struttura viene mantenuta volutamente compatta, evitando sottosezioni ridondanti.

## Confine con gli altri capitoli

- **Capitolo 2 - Stato dell'arte:** lavori correlati, metodologie disponibili e relativi limiti.
- **Capitolo 3 - Definizione del problema e soluzione proposta:** dataset, addestramento, pipeline topologica, Graph JSON, conversione a SPICE, agente e interfaccia sviluppati nella tesi.
- **Capitolo 4 - Valutazione sperimentale:** metriche YOLO, verifica strutturale, benchmark dei modelli, valutazione CHAT/AGENT e risultati finali.

Il percorso logico usato per ordinare la letteratura è:

> dataset e annotazioni -> object detection -> ricostruzione topologica -> grafo -> netlist/SPICE -> diagnosi AI -> valutazione

## Stato attuale della stesura

- **§2.1 completata**
- **§2.2 completata**
- **§2.3 completata**
- **§2.4 completata**
- **§2.5 completata**
- **§2.6 completata**
- **§2.7 da scrivere**

---

## 2.1 Digitalizzazione automatica dei diagrammi elettrici

**Stato:** completata.

### 2.1.1 Dal documento grafico alla rappresentazione strutturata

**Contenuti effettivamente trattati**

- Differenza tra semplice acquisizione digitale e vera digitalizzazione dell'informazione circuitale.
- Passaggio da documento raster a rappresentazione strutturata.
- Integrazione di elaborazione dell'immagine, riconoscimento di componenti, testo e connessioni.
- Limiti delle pipeline che riconoscono soltanto gli elementi senza ricostruire le relazioni.

**Lavori citati**

- C. R. Kelly e J. M. Cole, *Digitizing Images of Electrical-Circuit Schematics*, 2024.
- S. Mani et al., *Automatic Digitization of Engineering Diagrams Using Deep Learning and Graph Search*, 2020.
- W. Cao et al., *A Layered Framework for Universal Extraction and Recognition of Electrical Diagrams*, 2025.

### 2.1.2 Schemi elettrici e diagrammi di cablaggio

**Contenuti effettivamente trattati**

- Differenza tra schema elettrico e wiring diagram.
- Simbologia standardizzata e importanza delle convenzioni grafiche.
- Differenza tra rappresentazione logico-funzionale e disposizione fisica.
- Conseguenze per riconoscimento automatico e ricostruzione delle connessioni.

**Fonti citate**

- IEC 61082-1:2014.
- IEC 60617.
- A. R. Putra et al., *Automatic Extraction of Cable Connection Information from 2D Drawings for Electrical Outfittings Design in Shipyards*, 2024.

**Figura utilizzata**

- `images/chapter2/cao_layered_framework.png`
- Framework a livelli di Cao et al. per elementi, testo e connessioni.

---

## 2.2 Dataset e annotazione dei diagrammi elettrici

**Stato:** completata.

### 2.2.1 Reperimento e costruzione dei dataset

**Contenuti effettivamente trattati**

- Dataset pubblici e costruzione di collezioni di diagrammi.
- Diagrammi completi rispetto a simboli isolati.
- Differenze tra circuiti disegnati a mano, schematici regolari e dataset analog/mixed-signal.
- Problemi di varietà, domain shift e separazione corretta tra training, validation e test.

**Lavori citati**

- F. Thoma et al., 2021.
- H. Xu et al., Image2Net, 2025.
- Y. Shi et al., AMSnet 2.0, 2025.
- A. Roy et al., JUHCCR-v1, 2025.

### 2.2.2 Tassonomia e annotazione dei dati

**Contenuti effettivamente trattati**

- Granularità delle classi.
- Bounding box e annotazioni strutturali aggiuntive.
- Orientamento, junction, crossing e informazioni topologiche.
- Limiti delle annotazioni basate soltanto sulla posizione dei componenti.

### 2.2.3 Data augmentation e generalizzazione

**Contenuti effettivamente trattati**

- Trasformazioni geometriche e fotometriche.
- Ruolo della data augmentation in dataset piccoli o eterogenei.
- Rischio di trasformazioni non plausibili per il dominio circuitale.
- Esempi specifici dalla letteratura.

**Lavori citati**

- C. Shorten e T. M. Khoshgoftaar, 2019.
- A. Buslaev et al., 2020.
- A. Roy et al., 2025.
- Y. Shi et al., 2025.

**Figura utilizzata**

- `images/chapter2/thoma_dataset_sample.png`
- Esempio annotato del dataset di Thoma et al.

---

## 2.3 Rilevamento dei componenti elettrici

**Stato:** completata.

### 2.3.1 Dai metodi tradizionali al deep learning

**Contenuti effettivamente trattati**

- Template matching e descrittori progettati manualmente.
- HOG, LBP e classificatori tradizionali.
- Passaggio alle CNN.
- Differenza tra classificazione di simboli isolati e object detection sul diagramma completo.

**Lavori citati**

- A. Roy et al., JUHCCR-v1, 2025.
- S. Amraee et al., 2022.
- B. Bohara e H. S. Krishnamoorthy, 2024.

### 2.3.2 Detector one-stage e two-stage

**Contenuti effettivamente trattati**

- Differenza generale tra architetture one-stage e two-stage.
- YOLO e Faster R-CNN come riferimenti.
- Compromesso tra accuratezza, velocità e complessità.
- Difficoltà specifiche del dominio circuitale.

**Fonti citate**

- J. Redmon et al., 2016.
- S. Ren et al., 2015.
- S. Amraee et al., 2022.
- B. Bohara e H. S. Krishnamoorthy, 2024.

**Nota**

- Precision, recall, IoU e mAP vengono soltanto richiamate; la spiegazione sistematica resta nel Capitolo 4.

### 2.3.3 Riconoscimento dei componenti elettrici nella letteratura

**Contenuti effettivamente trattati**

- Detection come primo livello di pipeline più ampie.
- Rachala e Panicker: component detection + riconoscimento dei nodi.
- Amraee et al.: detection + boundary tracking.
- Bohara e Krishnamoorthy: detection fino a netlist e simulazione.
- Cao et al.: riconoscimento degli elementi in un framework a livelli.
- Limite centrale: una detection corretta non implica una ricostruzione corretta dell'intero circuito.

**Figura utilizzata**

- `images/chapter2/kelly_component_detection.png`
- Schema binarizzato/scheletrizzato con componenti rilevati e fili individuati.

---

## 2.4 Dalla detection alla rappresentazione topologica

**Stato:** completata.

La struttura effettiva è stata ridotta a **due sottosezioni**. La precedente articolazione in tre parti non viene più utilizzata.

### 2.4.1 Estrazione delle informazioni e ricostruzione delle connessioni

**Contenuti effettivamente trattati**

- Limiti delle sole bounding box.
- Orientamento dei simboli.
- Localizzazione dei terminali.
- Informazioni testuali.
- Segmentazione binaria e separazione delle linee.
- Connected components e thinning.
- Ricostruzione dei collegamenti come fase critica per la topologia.

**Lavori citati**

- J. Bayer, L. van Waveren e A. Dengel, *Modular Graph Extraction for Handwritten Circuit Diagram Images*, 2024.
- J. Bayer, A. K. Roy e A. Dengel, *Instance Segmentation Based Graph Extraction for Handwritten Circuit Diagram Images*, 2023.
- W. Hu, X. Zhan e M. Tong, *Parsing Netlists of Integrated Circuits from Images via Graph Attention Network*, 2024.

**Figura utilizzata**

- `images/chapter2/bayer_modular_graph_pipeline.png`
- Pipeline di Bayer et al. dall'immagine originale alla rettifica delle connessioni.

### 2.4.2 Rappresentazione a grafo e verifica topologica

**Contenuti effettivamente trattati**

- Rappresentazione del circuito mediante nodi e archi.
- Differenza tra rappresentazioni centrate sui componenti e rappresentazioni a livello di terminale.
- Costruzione geometrica del grafo.
- Link prediction come approccio appreso per inferire le connessioni.
- Uso di Graph Attention Network per la previsione delle relazioni tra terminali.
- Grafo come livello intermedio ispezionabile prima della netlist.
- Verifica topologica tramite confronto con una rappresentazione strutturata di riferimento.

**Lavori citati**

- Bayer et al., 2023.
- Bayer et al., 2024.
- Hu et al., 2024.
- H. Xu et al., Image2Net, 2025.

**Figura utilizzata**

- `images/chapter2/hu_port_link_prediction.png`
- Flusso di Hu et al. da component detection e localizzazione dei terminali alla link prediction.

**Da non anticipare**

- Graph JSON specifico della soluzione sviluppata nella tesi.
- Metriche e risultati della verifica topologica del progetto.

---

## 2.5 Dalla rappresentazione topologica alla netlist e alla simulazione SPICE

**Stato:** completata.

La struttura effettiva è stata ridotta a **due sottosezioni**. La precedente sottosezione autonoma sui sistemi image-to-netlist è stata assorbita nella trattazione dei lavori correlati.

### 2.5.1 Dal grafo alla netlist

**Contenuti effettivamente trattati**

- Trasformazione delle relazioni topologiche in associazioni esplicite componente-terminale-nodo.
- Identificatori e nodi elettrici.
- Irrilevanza del nome o della numerazione dei nodi quando la connettività rimane equivalente.
- Approcci recenti image-to-netlist.
- Ruolo dell'orientamento, dei terminali e della connectivity extraction.
- Differenza tra netlist strutturalmente ricostruita e netlist già utilizzabile per la simulazione.

**Lavori citati**

- B. Bohara e H. S. Krishnamoorthy, 2024, come raccordo alla pipeline completa.
- A. Mathur e R. Achar, *Hand-Drawn Circuit Schematic Digitization and Netlisting Using Machine Learning with Emphasis on Signal Integrity Applications*, 2024.
- S. Aldowaish et al., *SINA: A Circuit Schematic Image-to-Netlist Generator Using Artificial Intelligence*, DATE 2026.
- C.-Y. Huang et al., *Netlistify: Transforming Circuit Schematics into Netlists with Deep Learning*, MLCAD 2025.
- H. Xu et al., Image2Net, 2025.

**Figura utilizzata**

- `images/chapter2/sina_image_to_netlist.png`
- Esempio SINA: schema -> componenti -> nodi/connessioni -> netlist finale.

### 2.5.2 Simulazione SPICE e requisiti di simulabilità

**Contenuti effettivamente trattati**

- Netlist come ingresso a un simulatore SPICE.
- Richiamo essenziale alle analisi `.op`, `.dc`, `.ac` e `.tran`.
- Necessità di valori, parametri, sorgenti, nodo di riferimento, modelli e sottocircuiti.
- Corretta associazione tra terminali dello schema e pin del modello.
- Differenza tra correttezza sintattica, simulabilità e correttezza topologica/elettrica.
- Simulazione come ulteriore verifica, senza considerarla prova sufficiente di equivalenza con lo schema originale.
- Distinzione tra HSPICE commerciale e ngspice open source mediante nota esplicativa.

**Fonti citate**

- Documentazione e manuale ufficiale ngspice.
- Mathur e Achar, 2024.

**Figura utilizzata**

- `images/chapter2/mathur_netlist_simulation.png`
- Schema disegnato a mano -> connessioni/netlist -> simulazione HSPICE.

**Raccordo con la §2.6**

- Z. Huang et al., *PCBnet: A Dataset and Automatic Constructing of SPICE Netlists from Schematic Images*, preprint arXiv 2026.
- PCBnet è ripreso nella §2.6.2 per la correzione multi-agent e multimodale basata su conoscenza di dominio.

**Da non anticipare**

- Regole specifiche della conversione Graph JSON -> SPICE sviluppata nella tesi.
- Modelli SPICE e datasheet effettivamente usati nel progetto.
- Risultati `.op` e `.tran` ottenuti sperimentalmente.
- Strategia dell'agente diagnostico.

---

## 2.6 Diagnosi circuitale con modelli linguistici

**Stato:** completata.

La sezione parte dal limite emerso nella §2.5: una simulazione o una netlist corretta non costituiscono ancora una diagnosi. Il passo successivo riguarda l'uso di modelli linguistici e multimodali per interpretare dati strutturati, documentazione tecnica e risultati elettrici.

La struttura definitiva comprende le tre sottosezioni seguenti.

### 2.6.1 Modelli linguistici e multimodali per l'analisi circuitale

**Contenuti effettivamente trattati**

- Breve raccordo con diagnosi tradizionale e approcci model-based.
- Ragionamento diretto sull'immagine rispetto a ragionamento su testo, grafo o netlist.
- Uso congiunto di schema, netlist, datasheet e risultati elettrici.
- Limiti di LLM e VLM: allucinazioni, inferenze non verificabili, dipendenza dal contesto.

**Fonte di contesto tradizionale**

- D. Binu e B. S. Kariyappa, *A Survey on Fault Diagnosis of Analog Circuits: Taxonomy and State of the Art*, 2017.

### 2.6.2 Grounding mediante dati strutturati e simulazione

**Contenuti effettivamente trattati**

- Grafo e netlist come contesto strutturato.
- Datasheet e documentazione tecnica come fonti verificabili.
- Risultati SPICE come evidenza quantitativa.
- Differenza tra risposta generata soltanto dal modello e risposta grounded su dati o strumenti.
- RAG come principio generale, senza trasformare la sezione in una rassegna NLP.
- Workflow circuitali che includono simulatori o strumenti nel loop.

**Riferimenti della mappa bibliografica**

- P. Lewis et al., *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*, NeurIPS 2020.
- S. Nau, J. Krummenauer e A. Zimmermann, *Evaluating LLM-based Workflows for Switched-Mode Power Supply Design*; chiave bibliografica adottata: `nau2026smps`.
- AMSnet-KG.
- PCBnet 2026 per la correzione multi-agent grounded su conoscenza di dominio.

**Figura scelta per la §2.6.2**

- Figura 3 di Nau et al., dedicata ai workflow LLM con recupero di informazioni dal datasheet mediante RAG e feedback della simulazione SPICE.
- File previsto: `images/chapter2/nau_llm_workflow.png`.
- Label: `fig:nau-llm-workflow`.
- Collocazione nel testo: tra il secondo e il terzo paragrafo della §2.6.2, dopo la frase che termina con `...mentre un modello multimodale può essere utilizzato quando l'informazione visiva risulta ancora necessaria \cite{huang2026pcbnet}.` e prima del paragrafo che inizia con «Oltre alle informazioni strutturali e documentali, anche i risultati della simulazione possono essere utilizzati come fonte di evidenza per il modello».
- Sequenza: dati strutturati e AMSnet-KG -> RAG, datasheet e PCBnet -> figura di Nau -> approfondimento sul feedback SPICE.

**Frase di raccordo**

> Un esempio dell'integrazione tra modello linguistico, recupero di informazioni esterne e simulazione circuitale è riportato in Figura~\ref{fig:nau-llm-workflow}.

**Inserimento e caption concordati**

```latex
\begin{figure}[!htbp]
    \centering
    \includegraphics[width=0.95\textwidth]{images/chapter2/nau_llm_workflow.png}
    \caption{Esempio di workflow per l'analisi circuitale assistita da modelli linguistici, nel quale il modello può essere supportato dal recupero di informazioni dal datasheet mediante RAG e dal feedback ottenuto attraverso la simulazione SPICE. Riprodotto da \cite{nau2026smps}.}
    \label{fig:nau-llm-workflow}
\end{figure}
```

### 2.6.3 Assistenti, agenti e criteri di valutazione

**Contenuti effettivamente trattati**

- Differenza tra assistente conversazionale e agente tool-using.
- Pianificazione e selezione di azioni.
- Esecuzione di strumenti e simulatori.
- Stato persistente e tracciabilità della traiettoria.
- Errori cumulativi e maggiore variabilità dei workflow agentici.
- Criteri di qualità: correttezza tecnica, aderenza alle evidenze, utilità diagnostica, gestione dell'incertezza.
- Judge umano e LLM/VLM judge.
- Rubriche, pairwise evaluation e output strutturati.
- Threats to validity: prompt, ordine degli input, severità del judge, non determinismo.

**Riferimenti metodologici della mappa bibliografica**

- S. Yao et al., *ReAct: Synergizing Reasoning and Acting in Language Models*, 2022/2023.
- L. Zheng et al., *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*, 2023.
- Y. Liu et al., *G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment*, EMNLP 2023.
- D. Chen et al., *MLLM-as-a-Judge*, 2024.

**Materiale interno di orientamento**

- `third_part_from_json_to_spice/agent/agente_diagnostico_pipeline2.md`
- `experiment_ai/chat_agent_evaluation_21/README.md`
- `experiment_ai/chat_agent_evaluation_21/results/CAPITOLO_RISULTATI.md`
- `second_part_pipeline_topologica/RISULTATI_DIAGNOSI_CIRCUITI_COMPLESSI.md`

**Nota di stesura**

- La §2.6 è completata e mantiene tre sottosezioni, con i titoli riportati sopra. La struttura non è più da decidere.
- La trattazione resta dedicata alla letteratura; implementazione dell'agente e risultati della valutazione del progetto rimangono nei Capitoli 3 e 4.

---

## 2.7 Sintesi critica e posizionamento della tesi

**Stato:** da scrivere. La §2.6 è completata e costituisce il riferimento anche per la sintesi dei lavori su diagnosi e agenti.

### 2.7.1 Confronto tra i lavori correlati

Costruire una sola tabella comparativa end-to-end.

**Colonne candidate**

- dominio/dataset;
- component detection;
- OCR/testo;
- terminali/orientamento;
- wire/connectivity extraction;
- rappresentazione a grafo;
- generazione di netlist;
- simulazione SPICE;
- diagnosi AI;
- agente con strumenti;
- metodo di valutazione;
- codice/dati disponibili.

**Lavori da includere almeno**

- Mani et al.
- Kelly e Cole.
- Cao et al.
- Rachala e Panicker.
- Amraee et al.
- Bohara e Krishnamoorthy.
- Bayer et al. 2023/2024.
- Hu et al. 2024.
- Image2Net.
- AMSnet 2.0.
- Mathur e Achar.
- Netlistify.
- SINA.
- PCBnet, qualificato come preprint 2026.
- Lavori su diagnosi e agentic workflow trattati nella §2.6 completata.

### 2.7.2 Limiti dello stato dell'arte e spazio per la soluzione proposta

**Limiti da sintetizzare**

- Pipeline spesso limitate a un singolo dominio o stile di diagramma.
- Dataset piccoli, sintetici o difficilmente confrontabili.
- Detection accurata che non implica una topologia corretta.
- Gestione incompleta di terminali, valori, modelli e circuiti integrati.
- Metriche e protocolli di valutazione non sempre omogenei.
- Pochi sistemi integrano in modo tracciabile immagine, rappresentazione strutturata, netlist, simulazione e diagnosi.
- Validazione ancora limitata di assistenti e agenti su circuiti eterogenei con evidenze simulabili.

**Paragrafo finale ammesso**

- Un solo raccordo verso il Capitolo 3.
- Evidenziare il bisogno di una pipeline modulare e verificabile.
- Sottolineare il ruolo della rappresentazione strutturata intermedia.
- Presentare la simulazione come fonte di evidenza e non come semplice output finale.
- Motivare l'analisi successiva di assistente conversazionale e agente con strumenti senza anticipare i risultati.

---

## Piano aggiornato delle figure del Capitolo 2

Il piano aggiornato comprende otto figure: le sette già presenti fino alla §2.5 e la figura scelta per la §2.6.2.

1. **§2.1** - framework layered di Cao et al.
2. **§2.2** - esempio annotato del dataset di Thoma et al.
3. **§2.3** - component detection/wire extraction di Kelly e Cole.
4. **§2.4.1** - pipeline modulare di Bayer et al.
5. **§2.4.2** - port localization e link prediction di Hu et al.
6. **§2.5.1** - pipeline SINA fino alla netlist.
7. **§2.5.2** - netlist e simulazione HSPICE di Mathur e Achar.
8. **§2.6.2** - Figura 3 di Nau et al.: workflow LLM con RAG sul datasheet e feedback SPICE; file previsto `images/chapter2/nau_llm_workflow.png`, label `fig:nau-llm-workflow`, tra il secondo e il terzo paragrafo.

Per la **§2.6** è stata scelta una sola figura, quella di Nau et al. descritta nella §2.6.2. Alla fine del capitolo effettuare una revisione visiva complessiva delle otto figure.

## Regola finale di stesura

Ogni sezione deve:

1. introdurre il problema specifico;
2. sintetizzare le principali soluzioni presenti in letteratura;
3. evidenziarne i limiti;
4. preparare il passaggio logico alla sezione successiva.

Evitare descrizioni da manuale, dettagli implementativi della soluzione sviluppata e risultati sperimentali propri, che appartengono rispettivamente ai Capitoli 3 e 4.
