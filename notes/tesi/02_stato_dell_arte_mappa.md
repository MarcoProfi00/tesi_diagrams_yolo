# Capitolo 2 - Stato dell'arte: mappa dei contenuti

## Scopo del documento

Questa è una mappa di lavoro, non una bozza del capitolo. Serve a stabilire:

- il filo logico del capitolo;
- paragrafi e sottoparagrafi;
- argomenti da approfondire;
- fonti interne già disponibili;
- letteratura esterna da verificare;
- tabelle e figure candidate;
- confine con i capitoli 3 e 4.

## Stato della ricognizione bibliografica

- **Data di chiusura provvisoria della ricerca:** 1 settembre 2026.
- La data dovrà essere aggiornata solo se la stesura o la consegna avverranno molto più avanti.
- I documenti Word, PowerPoint e Markdown della repository sono materiale di orientamento e ricostruzione del progetto: nella tesi vanno citati i paper, gli standard, i dataset e la documentazione ufficiale originari.
- Per ogni dato quantitativo usare la versione più recente del paper consultata e annotarne versione/data; non copiare automaticamente i numeri dai vecchi appunti.
- I preprint molto recenti del 2026 vanno qualificati come tali oppure come lavori accettati, quando la pagina ufficiale lo dichiara.
- Questa mappa copre tutti i filoni necessari; il lavoro residuo è bibliografico e redazionale, non richiede nuovi esperimenti.

## Confine con gli altri capitoli

- **Capitolo 2 - Stato dell'arte:** descrive il problema generale e le soluzioni già presenti in letteratura.
- **Capitolo 3 - Problema e soluzione proposta:** descrive dataset, addestramento e pipeline sviluppati nella tesi.
- **Capitolo 4 - Valutazione sperimentale:** contiene metriche YOLO, valutazioni dei graph JSON, benchmark dei modelli e confronto CHAT-AGENT.

Nel capitolo 2 non inserire i risultati numerici dei nostri esperimenti. Il percorso del progetto viene usato soltanto per ordinare la letteratura:

> dataset e annotazioni -> object detection -> estrazione topologica -> graph/netlist/SPICE -> diagnosi AI -> valutazione

La struttura definitiva viene mantenuta volutamente compatta: **al massimo tre sottosezioni per ciascuna sezione**, accorpando gli argomenti strettamente collegati ed evitando una frammentazione eccessiva dello stato dell'arte.

---

## 2.1 Digitalizzazione automatica degli schemi elettrici

### 2.1.1 Dal documento grafico alla rappresentazione strutturata

**Contenuti da trattare**

- Ruolo di schemi elettrici e wiring diagram in progettazione, manutenzione e troubleshooting.
- Limiti dell'analisi manuale di documenti raster, scansioni e PDF tecnici.
- Obiettivo generale della digitalizzazione: trasformare pixel e testo in una rappresentazione strutturata interrogabile.
- Distinzione tra riconoscere simboli, ricostruire collegamenti e comprendere il comportamento elettrico.
- Pipeline modulari che separano elementi, testo e relazioni di connessione.

**Lavori principali**

- C. R. Kelly e J. M. Cole, *Digitizing Images of Electrical-Circuit Schematics*, 2024.
- S. Mani et al., *Automatic Digitization of Engineering Diagrams Using Deep Learning and Graph Search*, 2020.
- W. Cao et al., *A Layered Framework for Universal Extraction and Recognition of Electrical Diagrams*, 2025.

### 2.1.2 Schemi elettrici e diagrammi di cablaggio

**Contenuti da trattare**

- Differenze tra schema logico/funzionale e wiring diagram fisico.
- Simbologia standardizzata rispetto a icone pittoriche o dipendenti dal produttore.
- Layout logico rispetto a disposizione fisica.
- Conseguenze per computer vision, OCR ed estrazione dei collegamenti.
- Esempi di estrazione delle connessioni in diagrammi industriali.

**Lavori e fonti principali**

- A. R. Putra, S. Ha e K.-P. Park, *Automatic Extraction of Cable Connection Information from 2D Drawings for Electrical Outfittings Design in Shipyards*, 2024.
- [IEC 60617 - Graphical symbols for diagrams](https://std.iec.ch/iec60617).
- [IEC 61082-1:2014 - Preparation of Documents Used in Electrotechnology](https://webstore.iec.ch/en/publication/4469).
- [IEEE/ANSI 315-1975](https://standards.ieee.org/ieee/315/515/), solo se utile per discutere varianti di simbologia.

**Materiale interno**

- [Extraction and Recognition of Wiring Diagrams.pptx](<../Teoria_Papers/Extraction and Recognition of Wiring Diagrams.pptx>)
- [Spiegazione_HighLevel.docx](../Teoria_Papers/Spiegazione_HighLevel.docx)
- [Costruzione Dataset.docx](<../Teoria_Papers/Costruzione Dataset.docx>)
- [electronics-14-00833-with-cover.pdf](../Teoria_Papers/Papers/electronics-14-00833-with-cover.pdf)

**Figura utilizzata**

- Framework a livelli di Cao et al. per elementi, testo e connessioni.

**Da non anticipare**

- Le classi specifiche del nostro dataset.
- Le immagini di training e i risultati del detector.

---

## 2.2 Dataset e annotazione dei diagrammi elettrici

### 2.2.1 Reperimento e costruzione dei dataset

**Contenuti da trattare**

- Dataset pubblici, immagini da documentazione tecnica e generazione sintetica.
- Diagrammi completi rispetto a collezioni di simboli isolati.
- Differenze tra dataset di schematici regolari, wiring diagram e circuiti disegnati a mano.
- Problemi di licenza, provenienza, duplicati e domain shift.
- Separazione corretta tra training, validation e test, evitando leakage tra varianti dello stesso circuito.

**Dataset/lavori principali**

- F. Thoma et al., *A Public Ground-Truth Dataset for Handwritten Circuit Diagram Images*, 2021.
- H. Xu et al., *Image2Net: Datasets, Benchmark and Hybrid Framework to Convert Analog Circuit Diagrams into Netlists*, 2025.
- Y. Shi et al., *AMSnet 2.0: A Large AMS Database with AI Segmentation for Net Detection*, 2025.
- A. Roy et al., *JUHCCR-v1: A Database for Hand-Drawn Electrical and Electronics Circuit Component Recognition*, 2025.

### 2.2.2 Tassonomia e annotazione dei dati

**Contenuti da trattare**

- Definizione e granularità delle classi prima dell'annotazione.
- Ambiguità tra simboli visivamente simili, class imbalance e classi rare.
- Bounding box e formati di annotazione come Pascal VOC e YOLO.
- Limiti delle sole bounding box: non descrivono terminali, orientamento o connessioni.
- Annotazioni aggiuntive per junction, crossing, orientamento, reti elettriche e netlist.

### 2.2.3 Data augmentation e generalizzazione

**Contenuti da trattare**

- Trasformazioni geometriche e fotometriche.
- Utilità rispetto a dataset piccoli, variazioni di scansione/fotografia e classi poco rappresentate.
- Rischio di trasformazioni non plausibili per il dominio circuitale.
- Augmentation mirata a orientamento, rumore, contrasto, qualità del tratto e sovrapposizioni grafiche.

**Fonti principali**

- C. Shorten e T. M. Khoshgoftaar, *A Survey on Image Data Augmentation for Deep Learning*, 2019.
- A. Buslaev et al., *Albumentations: Fast and Flexible Image Augmentations*, 2020.
- A. Roy et al., JUHCCR-v1, 2025, come esempio specifico del dominio circuitale.
- Y. Shi et al., AMSnet 2.0, 2025, per perturbazioni grafiche su schematici.

**Materiale interno**

- [Costruzione Dataset.docx](<../Teoria_Papers/Costruzione Dataset.docx>)
- [data/README.md](../../data/README.md)
- script in [scripts/augmentation/](../../scripts/augmentation/)
- archivi versionati in [data/datasets/](../../data/datasets/)
- [class_summary_global.csv](../../metadata/class_summary_global.csv) e [class_summary_by_split.csv](../../metadata/class_summary_by_split.csv)

**Figura utilizzata**

- Esempio annotato del dataset di Thoma et al., con bounding box e annotazioni ausiliarie.

**Tabella candidata**

- Confronto sintetico tra dataset della letteratura: dominio, dimensione, classi, tipo di annotazione, disponibilità e limite principale. Valutare se mantenerla o assorbirne le informazioni nella tabella comparativa finale del §2.7.

---

## 2.3 Rilevamento dei componenti elettrici

### 2.3.1 Dai metodi tradizionali al deep learning

**Contenuti da trattare**

- Template matching, densità dei pixel, descrittori HOG/LBP e classificatori tradizionali.
- Fragilità rispetto a scala, rumore, stile, deformazioni e somiglianza tra simboli.
- Passaggio a CNN capaci di apprendere automaticamente le caratteristiche visive.
- Distinzione tra classificazione di simboli isolati e object detection sull'intero diagramma.

**Lavori principali**

- A. Roy et al., JUHCCR-v1, 2025.
- S. Amraee et al., *Handwritten Logic Circuits Analysis Using the YOLO Network and a New Boundary Tracking Algorithm*, 2022.
- B. Bohara e H. S. Krishnamoorthy, *Deep Learning-Based Framework for Power Converter Circuit Identification and Analysis*, 2024.

### 2.3.2 Detector one-stage e two-stage

**Contenuti da trattare**

- Differenza concettuale tra detector one-stage e two-stage.
- YOLO come riferimento one-stage e Faster R-CNN come riferimento two-stage.
- Compromesso tra accuratezza, complessità e velocità di inferenza.
- Difficoltà del dominio circuitale: simboli piccoli, densi e visivamente simili.
- Evoluzione della famiglia YOLO solo nella misura necessaria a contestualizzare YOLOv7, YOLOv8 e YOLO11; evitare una rassegna di tutte le versioni.

**Fonti principali**

- J. Redmon et al., *You Only Look Once: Unified, Real-Time Object Detection*, CVPR 2016.
- S. Ren et al., *Faster R-CNN: Towards Real-Time Object Detection with Region Proposal Networks*, NeurIPS 2015.
- C.-Y. Wang et al., *YOLOv7: Trainable Bag-of-Freebies Sets New State-of-the-Art for Real-Time Object Detectors*, 2022/2023.
- Documentazione ufficiale Ultralytics per YOLOv8 e YOLO11.
- S. Amraee et al., 2022, per confronto tra YOLO, Faster R-CNN, RetinaNet e Detectron2 in ambito circuitale.
- B. Bohara e H. S. Krishnamoorthy, 2024, per confronto YOLOR/YOLOv7/YOLOv8.

**Nota sulle metriche**

- Precision, recall, F1, IoU e mAP vengono richiamate solo quando necessario nello stato dell'arte.
- La spiegazione sistematica di mAP@0.5, mAP@0.5:0.95 e delle metriche dei nostri esperimenti appartiene al Capitolo 4.

### 2.3.3 Riconoscimento dei componenti elettrici nella letteratura

**Contenuti da trattare**

- R. R. Rachala e M. R. Panicker: YOLOv5 + riconoscimento dei nodi tramite trasformata di Hough.
- S. Amraee et al.: detection dei componenti + boundary tracking delle connessioni.
- B. Bohara e H. S. Krishnamoorthy: detection inserita in una pipeline fino a netlist e simulazione.
- W. Cao et al.: riconoscimento degli elementi come primo livello di un framework più ampio.
- Evidenziare che una detection accurata è necessaria ma non sufficiente per la digitalizzazione completa dello schema.

**Materiale interno**

- [Extraction and Recognition of Wiring Diagrams.pptx](<../Teoria_Papers/Extraction and Recognition of Wiring Diagrams.pptx>)
- [electronics-14-00833-with-cover.pdf](../Teoria_Papers/Papers/electronics-14-00833-with-cover.pdf)
- [Passi_da_seguire.docx](../Teoria_Papers/DetectionComponents/Passi_da_seguire.docx)
- risultati YOLO interni soltanto per ricostruire il contesto; numeri e confronto sperimentale rimangono nel Capitolo 4.

**Figura utilizzata**

- C. R. Kelly e J. M. Cole, figura con schema binarizzato/scheletrizzato, componenti rilevati mediante bounding box e fili individuati.

**Da non anticipare**

- Configurazioni `exp01`-`exp12`.
- Metriche del checkpoint finale.
- Motivazione sperimentale della scelta del detector sviluppato nella tesi.

---

## 2.4 Dalla detection alla rappresentazione topologica

### 2.4.1 Estrazione delle informazioni complementari

**Contenuti da trattare**

- Perché la bounding box di un componente non è sufficiente per ricostruire il circuito.
- Separazione tra layer dei componenti, layer testuale e layer delle connessioni.
- Text detection e text recognition senza trasformare la sezione in una rassegna generale sull'OCR.
- Testo ruotato, font tecnici, sovrapposizione con i fili e associazione spaziale testo-componente.
- Localizzazione dei terminali, orientamento, polarità e semantica dei pin.
- Componenti a due terminali rispetto a componenti multi-terminale.

**Fonti/lavori da usare**

- W. Cao et al., framework layered, 2025.
- C. R. Kelly e J. M. Cole, 2024.
- B. Bohara e H. S. Krishnamoorthy, 2024.
- H. Xu et al., Image2Net, 2025, per orientamento e annotazioni aggiuntive.
- [Tesseract User Manual](https://tesseract-ocr.github.io/tessdoc/).
- [EasyOCR](https://github.com/JaidedAI/EasyOCR).
- Y. Baek et al., *Character Region Awareness for Text Detection*, CVPR 2019, se serve approfondire CRAFT.

### 2.4.2 Ricostruzione delle connessioni

**Contenuti da trattare**

- Binarizzazione e mascheramento/rimozione di componenti e testo.
- Operazioni morfologiche, closing, thinning e skeletonization.
- Hough transform, connected components, line segment detection e wire tracing.
- Ripristino di linee interrotte o occluse tramite operazioni geometriche o inpainting.
- Differenza tra giunzioni a T, incroci connessi/non connessi e crossing/bridge.
- Effetto di un errore locale sulla topologia globale del circuito.

**Lavori principali**

- C. R. Kelly e J. M. Cole, 2024.
- S. Amraee et al., 2022.
- W. Cao et al., 2025.
- B. Bohara e H. S. Krishnamoorthy, 2024.
- A. R. Putra et al., 2024, per wiring diagram industriali.

### 2.4.3 Dalla connettività al grafo e verifica topologica

**Contenuti da trattare**

- Component graph, terminal graph e net graph.
- Nodi, componenti, terminali, archi e reti elettriche.
- Vantaggi di una rappresentazione intermedia modulare e ispezionabile rispetto alla conversione diretta immagine-netlist.
- Sistemi completi immagine-grafo e approcci basati su graph search, graph attention o instance segmentation.
- Verifica strutturale tramite confronto delle connessioni, exact match, precision/recall degli archi, Graph Edit Distance e metriche normalizzate.
- Verifica visuale/multimodale come supporto, distinguendola sempre da una ground truth strutturata.

**Lavori candidati**

- J. Bayer, L. van Waveren e A. Dengel, *Modular Graph Extraction for Handwritten Circuit Diagram Images*, 2024.
- J. Bayer et al., *Instance Segmentation Based Graph Extraction for Handwritten Circuit Diagram Images*, 2023.
- H. Xu et al., Image2Net, 2025.
- W. Cao et al., 2025.
- C. R. Kelly e J. M. Cole, 2024.
- S. Mani et al., 2020.
- W. Hu et al., *Parsing Netlists of Integrated Circuits from Images via Graph Attention Network*, 2023/2024.
- A. R. Putra et al., 2024.

**Fonti metodologiche per la verifica automatica, da usare solo se necessarie**

- L. Zheng et al., *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*, 2023.
- Y. Liu et al., *G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment*, EMNLP 2023.
- D. Chen et al., *MLLM-as-a-Judge*, 2024.
- Un judge automatico non sostituisce automaticamente una ground truth annotata.

**Materiale interno**

- [Extraction and Recognition of Wiring Diagrams.pptx](<../Teoria_Papers/Extraction and Recognition of Wiring Diagrams.pptx>)
- [electronics-14-00833-with-cover.pdf](../Teoria_Papers/Papers/electronics-14-00833-with-cover.pdf)
- [doc_scripts_1.0/](../second_part_pipeline_topologica/doc_scripts_1.0/) soltanto come materiale tecnico per comprendere i problemi.
- [RISULTATI_VERIFICA_TOPOLOGICA_GRAPH_JSON.md](../second_part_pipeline_topologica/RISULTATI_VERIFICA_TOPOLOGICA_GRAPH_JSON.md) soltanto per ricostruire il protocollo; risultati nel Capitolo 4.
- [deep-research-report.md](../third_part_from_json_to_spice/deep-research-report.md)

**Figura candidata**

- Una figura che mostri chiaramente il passaggio da componenti/terminali/connessioni a una rappresentazione a grafo. Evitare di duplicare la pipeline layered già mostrata nel §2.1.

---

## 2.5 Dal grafo alla netlist e alla simulazione SPICE

### 2.5.1 Dal grafo alla netlist

**Contenuti da trattare**

- Differenza tra grafo topologico, Graph JSON, netlist e schematico visuale.
- Identificatori canonici per componenti, terminali e nodi.
- Mapping terminale-net e trasformazione delle relazioni topologiche in una descrizione circuitale.
- Tracciabilità tra rappresentazioni successive e vantaggi di una rappresentazione intermedia strutturata.
- Netlist completa, netlist parziale e rappresentazione non ancora simulabile.

### 2.5.2 Simulazione SPICE e completamento semantico

**Contenuti da trattare**

- Netlist come descrizione dichiarativa di componenti, parametri e nodi.
- Introduzione essenziale alle analisi `.op`, `.dc`, `.ac` e `.tran`.
- Modelli primitivi, modelli vendor e sottocircuiti.
- Ruolo di massa, alimentazioni, valori, parametri e condizioni iniziali.
- Informazioni mancanti: valori non leggibili, modelli assenti, pin mapping di integrati e uso dei datasheet.
- Errori sintattici rispetto a errori elettrici/topologici; floating nodes e problemi di convergenza.
- Una simulazione riuscita non garantisce che il circuito ricostruito coincida con quello originale.

**Fonti primarie**

- [Ngspice documentation](https://ngspice.sourceforge.io/docs.html) e [Ngspice User's Manual](https://ngspice.sourceforge.io/docs/ngspice-manual.pdf).
- L. W. Nagel e D. O. Pederson, *SPICE (Simulation Program with Integrated Circuit Emphasis)*, UC Berkeley, 1973, solo per l'origine storica.

### 2.5.3 Sistemi image-to-netlist e verifica mediante simulazione

**Aspetti da confrontare**

- Tipologia di input e dominio circuitale.
- Riconoscimento di componenti, orientamento, testo e valori.
- Metodo di connectivity inference.
- Formato e completezza della netlist generata.
- Presenza di verifica strutturale o simulativa.
- Dataset, codice e riproducibilità.

**Lavori principali/candidati**

- H. Xu et al., Image2Net, 2025.
- B. Bohara e H. S. Krishnamoorthy, 2024.
- *Netlistify: Transforming Circuit Schematics into Netlists with Deep Learning*, MLCAD 2025.
- AMSNet e AMSnet 2.0.
- S. Aldowaish et al., *SINA: A Fully Automated Circuit Schematic Image to Netlist Generator Using Artificial Intelligence*, preprint 2026.
- Z. Huang et al., *PCBnet: A Dataset and Automatic Construction of SPICE Netlists from Schematic Images*, preprint/ICLAD 2026.
- J. Ma et al., *NetlistBench: Evaluating LLM Reliability in SPICE Netlist Recognition and Manipulation*, MLCAD 2026, soprattutto per la valutazione deterministica della struttura.
- Auto-SPICE / Masala-CHAI solo se la fonte primaria viene verificata e risulta realmente pertinente.

**Materiale interno**

- [deep-research-report.md](../third_part_from_json_to_spice/deep-research-report.md)
- [Teoria_Integrazione json - Spice.docx](<../third_part_from_json_to_spice/Teoria_Integrazione json - Spice.docx>)
- [Estensione della pipeline con SPICE a partire dal graph JSON.odt](<../third_part_from_json_to_spice/Estensione della pipeline con SPICE a partire dal graph JSON.odt>)
- [stato_dell_arte_spice_to_viewer.md](../third_part_from_json_to_spice/viewer_simulator/stato_dell_arte_spice_to_viewer.md)
- datasheet e README dei modelli in [metadata/spice_models/](../../metadata/spice_models/)

**Figura candidata**

- Pipeline di Bohara e Krishnamoorthy: schema -> detection/OCR -> nodi/connessioni -> netlist -> simulazione. È più adatta qui che nella sezione di sola object detection.

---

## 2.6 Diagnosi circuitale assistita da modelli linguistici

### 2.6.1 Modelli linguistici e multimodali per l'analisi circuitale

**Contenuti da trattare**

- Breve raccordo con diagnosi tradizionale, sistemi esperti e approcci model-based.
- Ragionamento diretto sull'immagine rispetto a ragionamento su descrizioni testuali o rappresentazioni strutturate.
- Uso congiunto di schema, netlist, datasheet e risultati elettrici.
- Limiti dei modelli linguistici: allucinazioni, inferenze non verificabili e dipendenza dal contesto fornito.

**Fonte di contesto tradizionale**

- D. Binu e B. S. Kariyappa, *A Survey on Fault Diagnosis of Analog Circuits: Taxonomy and State of the Art*, 2017.

### 2.6.2 Grounding mediante dati strutturati e simulazione

**Contenuti da trattare**

- Graph/netlist come contesto strutturato per il modello.
- Datasheet e documentazione tecnica come fonti esterne verificabili.
- Risultati SPICE come evidenza quantitativa per supportare o confutare ipotesi diagnostiche.
- Differenza tra risposta generata soltanto dal modello e risposta grounded su dati recuperati o prodotti da strumenti.
- RAG come principio generale di grounding, senza trasformare la sezione in una rassegna NLP.
- Sistemi e workflow circuitali che includono SPICE nel loop.

**Fonti metodologiche/circuitali**

- P. Lewis et al., *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*, NeurIPS 2020.
- S. Nau, J. Krummenauer e A. Zimmermann, *Evaluating LLM-based Workflows for Switched-Mode Power Supply Design*, 2025.
- SPICEAssistant, AMSnet-KG/AMSnet-q e Auto-SPICE solo dopo verifica della fonte primaria.

### 2.6.3 Assistenti, agenti e criteri di valutazione

**Contenuti da trattare**

- Differenza tra assistente conversazionale e agente tool-using.
- Pianificazione, selezione di azioni/scenari, esecuzione di simulatori e lettura dei risultati.
- Stato persistente, budget di strumenti e audit trail.
- Rischi di azioni non necessarie, errori cumulativi e maggiore variabilità nelle traiettorie agentiche.
- Criteri di qualità: correttezza tecnica, aderenza alle evidenze, utilità diagnostica, dichiarazione di incertezza e limiti.
- Confronto qualità/costo/latenza e risposta singola rispetto a traiettoria agente.
- Judge umano, LLM/VLM judge, rubriche, pairwise evaluation e output strutturati.
- Threats to validity: prompt, ordine degli input, severità del judge e non determinismo.

**Fonti metodologiche**

- S. Yao et al., *ReAct: Synergizing Reasoning and Acting in Language Models*, 2022/2023.
- L. Zheng et al., *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*, 2023.
- Y. Liu et al., *G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment*, EMNLP 2023.
- D. Chen et al., *MLLM-as-a-Judge*, 2024.

**Materiale interno**

- [agente_diagnostico_pipeline2.md](../third_part_from_json_to_spice/agent/agente_diagnostico_pipeline2.md)
- [README della valutazione CHAT/AGENT](../../experiment_ai/chat_agent_evaluation_21/README.md)
- [CAPITOLO_RISULTATI.md](../../experiment_ai/chat_agent_evaluation_21/results/CAPITOLO_RISULTATI.md) soltanto per ricostruire il disegno sperimentale; risultati nel Capitolo 4.
- [RISULTATI_DIAGNOSI_CIRCUITI_COMPLESSI.md](../second_part_pipeline_topologica/RISULTATI_DIAGNOSI_CIRCUITI_COMPLESSI.md) soltanto come riferimento al protocollo e alla terminologia.

**Figura candidata**

- Schema concettuale semplice: LLM diretto -> LLM grounded -> agente con strumenti. Inserire solo se aggiunge reale valore esplicativo.

---

## 2.7 Sintesi critica e posizionamento della tesi

### 2.7.1 Confronto tra i lavori correlati

**Tabella principale del capitolo**

Costruire una sola matrice comparativa end-to-end, evitando numerose tabelle parziali se non realmente necessarie.

**Colonne consigliate**

- dominio/dataset;
- component detection;
- OCR/testo;
- terminali/orientamento;
- wire e connectivity extraction;
- rappresentazione a grafo;
- generazione di netlist;
- simulazione SPICE;
- diagnosi AI;
- agente con strumenti;
- metodo di valutazione;
- codice/dati disponibili.

**Lavori da rappresentare almeno nella matrice**

- Mani et al.
- Kelly e Cole.
- Cao et al.
- Rachala e Panicker.
- Amraee et al.
- Bohara e Krishnamoorthy.
- Modular Graph Extraction / Instance Segmentation Based Graph Extraction.
- Image2Net.
- AMSnet 2.0.
- Netlistify.
- SINA e PCBnet, qualificati come lavori molto recenti del 2026.
- Eventuali lavori specifici su diagnosi/agentic workflow soltanto se direttamente confrontabili.

### 2.7.2 Limiti dello stato dell'arte e spazio per la soluzione proposta

**Limiti ricorrenti da verificare con le fonti durante la stesura**

- Pipeline spesso limitate a un singolo dominio o stile di diagramma.
- Dataset piccoli, sintetici o difficilmente confrontabili tra lavori differenti.
- Detection accurata che non implica automaticamente una topologia corretta.
- Gestione incompleta di terminali, valori, modelli e circuiti integrati.
- Metriche e protocolli di valutazione non sempre omogenei.
- Pochi sistemi integrano in modo tracciabile immagine, rappresentazione strutturata, netlist, simulazione e diagnosi.
- Validazione ancora limitata di assistenti e agenti su circuiti eterogenei e con evidenze simulabili.

**Paragrafo finale ammesso**

- Un solo raccordo verso il Capitolo 3.
- Evidenziare il bisogno di una pipeline modulare e verificabile.
- Sottolineare il ruolo di una rappresentazione strutturata intermedia.
- Presentare la simulazione come fonte di evidenza e non come semplice output finale.
- Motivare la successiva analisi di assistente conversazionale e agente con strumenti senza anticiparne i risultati.

---

## Piano sintetico delle figure del capitolo

Mantenere il capitolo visivamente sobrio: indicativamente 4--5 figure complessive, tutte con funzione esplicativa.

- **§2.1:** framework layered di Cao et al. -- già selezionato.
- **§2.2:** esempio annotato del dataset di Thoma et al. -- già selezionato.
- **§2.3:** esempio di component detection/wire extraction di Kelly e Cole -- già selezionato.
- **§2.4:** eventuale figura sul passaggio connessioni -> grafo, solo se realmente distinta dalle precedenti.
- **§2.5:** pipeline completa di Bohara e Krishnamoorthy come candidata principale per netlist/SPICE.
- **§2.6:** evitare figure decorative; aggiungere uno schema concettuale solo se necessario.

## Regola finale di stesura

Ogni sezione deve descrivere il problema, sintetizzare le principali soluzioni disponibili in letteratura, evidenziarne i limiti e preparare il passaggio logico alla sezione successiva. Evitare descrizioni da manuale, dettagli implementativi della soluzione sviluppata e risultati sperimentali propri, che appartengono rispettivamente ai Capitoli 3 e 4.
