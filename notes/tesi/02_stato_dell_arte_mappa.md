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

> dataset e annotazioni -> object detection -> estrazione topologica -> verifica della struttura -> graph/netlist/SPICE -> diagnosi AI -> valutazione con judge

---

## 2.1 Digitalizzazione automatica degli schemi elettrici

### 2.1.1 Contesto applicativo

**Contenuti da trattare**

- Ruolo di schemi elettrici e wiring diagram in progettazione, manutenzione e troubleshooting.
- Limiti dell'analisi manuale di documenti raster, scansioni e PDF tecnici.
- Obiettivo generale della digitalizzazione: trasformare pixel e testo in una rappresentazione strutturata interrogabile.
- Distinzione tra riconoscere simboli, ricostruire collegamenti e comprendere il comportamento elettrico.

### 2.1.2 Schemi elettrici e wiring diagram

**Contenuti da trattare**

- Differenze tra schema logico/funzionale e wiring diagram fisico.
- Simbologia standardizzata rispetto a icone pittoriche o dipendenti dal produttore.
- Layout logico rispetto a disposizione fisica.
- Conseguenze per computer vision, OCR ed estrazione dei collegamenti.

**Materiale interno**

- [Extraction and Recognition of Wiring Diagrams.pptx](<../Teoria_Papers/Extraction and Recognition of Wiring Diagrams.pptx>)
- [Spiegazione_HighLevel.docx](../Teoria_Papers/Spiegazione_HighLevel.docx)
- [Costruzione Dataset.docx](<../Teoria_Papers/Costruzione Dataset.docx>)
- [electronics-14-00833-with-cover.pdf](../Teoria_Papers/Papers/electronics-14-00833-with-cover.pdf)

**Fonti normative da citare**

- [IEC 60617 - Graphical symbols for diagrams](https://tc3.iec.ch/standard-as-database/): fonte normativa primaria per la simbologia elettrotecnica.
- [IEC 61082-1:2014 - Preparation of documents used in electrotechnology](https://webstore.iec.ch/en/publication/4469): regole e tipologie dei documenti elettrotecnici, inclusi circuit e connection diagram.
- [IEEE/ANSI 315-1975](https://standards.ieee.org/ieee/315/515/): riferimento storico statunitense, da usare solo se serve discutere varianti di simbologia rispetto allo standard IEC.

**Figura candidata**

- **Figura 2.1:** confronto concettuale tra schema elettrico regolare e wiring diagram irregolare.
- Preferire un'illustrazione originale o materiale con licenza verificata.

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

### 2.2.2 Tassonomia delle classi

**Contenuti da trattare**

- Definizione delle classi prima dell'annotazione.
- Granularità delle classi e ambiguità tra simboli visivamente simili.
- Class imbalance e classi rare.
- Coerenza tra tassonomia, obiettivo applicativo e output della pipeline.

### 2.2.3 Bounding box e formato YOLO

**Contenuti da trattare**

- Bounding box come rappresentazione dell'annotazione per object detection.
- Associazione immagine-label e coordinate normalizzate.
- Struttura train/validation/test.
- Controllo qualità delle annotazioni.
- Limiti delle bounding box: localizzano il componente ma non descrivono terminali, orientamento o connessioni.

### 2.2.4 Data augmentation e generalizzazione

**Contenuti da trattare**

- Trasformazioni geometriche e fotometriche.
- Augmentation moderata rispetto ad augmentation forte.
- Rischio di trasformazioni fisicamente o graficamente non plausibili.
- Utilità rispetto a dataset piccoli, classi rare e variazioni di scansione.

**Materiale interno**

- [Costruzione Dataset.docx](<../Teoria_Papers/Costruzione Dataset.docx>)
- [data/README.md](../../data/README.md)
- script in [scripts/augmentation/](../../scripts/augmentation/)
- archivi versionati in [data/datasets/](../../data/datasets/)
- [class_summary_global.csv](../../metadata/class_summary_global.csv) e [class_summary_by_split.csv](../../metadata/class_summary_by_split.csv).

**Tabella candidata**

- **Tabella 2.1:** dataset della letteratura con colonne: dominio, numero di immagini, numero di classi, tipo di annotazione, disponibilità, licenza e limite principale.

**Dataset e benchmark da includere nella tabella**

- F. Thoma, J. Bayer e Y. Li, [*A Public Ground-Truth Dataset for Handwritten Circuit Diagram Images*](https://arxiv.org/abs/2107.10373), 2021: dataset CGHD, utile per discutere annotazioni, condizioni di acquisizione e circuiti disegnati a mano.
- J. Bayer, L. van Waveren e A. Dengel, [*Modular Graph Extraction for Handwritten Circuit Diagram Images*](https://arxiv.org/abs/2402.11093), 2024: uso del dataset pubblico e baseline modulare immagine-grafo.
- H. Xu et al., [*Image2Net: Datasets, Benchmark and Hybrid Framework to Convert Analog Circuit Diagrams into Netlists*](https://arxiv.org/abs/2508.13157), 2025: dataset e benchmark schematico-netlist con valutazione strutturale.
- Z. Huang et al., [*PCBnet: A Dataset and Automatic Construction of SPICE Netlists from Schematic Images*](https://arxiv.org/abs/2608.27923), 2026: lavoro accettato a ICLAD 2026 e pubblicato come preprint il 28 agosto 2026; presentarlo come aggiornamento molto recente.
- AMSNet e AMSnet 2.0: recuperare le pagine ufficiali del progetto e distinguere chiaramente versione del dataset, dominio AMS e tipo di netlist associata.

**Figura candidata**

- **Figura 2.2:** esempio astratto di immagine, bounding box e record YOLO.
- Non usare qui grafici di distribuzione o risultati del nostro dataset: appartengono ai capitoli 3-4.

---

## 2.3 Rilevamento dei componenti elettrici

### 2.3.1 Metodi tradizionali e deep learning

**Contenuti da trattare**

- Template matching, descrittori geometrici e librerie di simboli.
- Fragilità dei metodi tradizionali rispetto a scala, rumore, stile e deformazioni.
- Passaggio a CNN e detector addestrabili.

### 2.3.2 Detector one-stage e two-stage

**Contenuti da trattare**

- Differenza concettuale tra YOLO e Faster R-CNN.
- Compromesso tra velocità, complessità e localizzazione di oggetti piccoli.
- Perché i diagrammi elettrici costituiscono un dominio difficile: simboli piccoli, densi e visivamente simili.

### 2.3.3 Evoluzione della famiglia YOLO

**Contenuti da trattare**

- Inquadramento storico essenziale di YOLO.
- YOLOv7, YOLOv8 e YOLO11 come famiglie considerate nel progetto.
- Cambiamenti architetturali rilevanti soltanto se utili a motivare il confronto.
- Distinzione tra paper scientifici e documentazione ufficiale delle implementazioni.

### 2.3.4 Metriche per l'object detection

**Contenuti da trattare**

- Precision, recall, F1, IoU e mAP.
- Differenza tra mAP@0.5 e mAP@0.5:0.95.
- Valutazione quantitativa e ispezione qualitativa delle confusioni.
- Effetto dello sbilanciamento delle classi sulle metriche aggregate.

### 2.3.5 Riconoscimento di simboli elettrici nella letteratura

**Lavori candidati da confrontare**

- Cao et al., *A Layered Framework for Universal Extraction and Recognition of Electrical Diagrams*.
- Kelly e Cole, *Digitizing Images of Electrical-Circuit Schematics*.
- Reddy e Panicker, riconoscimento di circuiti disegnati a mano.
- Modular Graph Extraction for Handwritten Circuit Diagram Images.
- Altri detector per schemi elettrici da verificare durante la ricerca bibliografica.

**Fonti fondamentali per detector e metriche**

- J. Redmon et al., [*You Only Look Once: Unified, Real-Time Object Detection*](https://openaccess.thecvf.com/content_cvpr_2016/html/Redmon_You_Only_Look_CVPR_2016_paper.html), CVPR 2016: riferimento storico per il paradigma one-stage.
- S. Ren et al., [*Faster R-CNN: Towards Real-Time Object Detection with Region Proposal Networks*](https://papers.nips.cc/paper/2015/hash/14bfa6bb14875e45bba028a21ed38046-Abstract.html), NeurIPS 2015: riferimento two-stage.
- C.-Y. Wang, A. Bochkovskiy e H.-Y. M. Liao, [*YOLOv7: Trainable Bag-of-Freebies Sets New State-of-the-Art for Real-Time Object Detectors*](https://arxiv.org/abs/2207.02696), 2022/2023.
- [Ultralytics YOLO11 - documentazione ufficiale](https://docs.ultralytics.com/models/yolo11/): YOLO11 non dispone di un paper scientifico formale; citarlo come software/documentazione, indicando versione e anno.
- [COCO Object Detection Task](https://cocodataset.org/#detection-eval): fonte per AP, IoU e convenzioni di valutazione COCO.

**Nota di impostazione**

- Non serve ricostruire ogni versione della famiglia YOLO. Descrivere soltanto il passaggio concettuale dal modello originale alle versioni effettivamente confrontate nella tesi: YOLOv7, YOLOv8 e YOLO11.
- Separare sempre le prestazioni riportate sui benchmark generali dalle prestazioni ottenute sul nostro dataset, che appartengono al capitolo 4.

**Materiale interno**

- [Extraction and Recognition of Wiring Diagrams.pptx](<../Teoria_Papers/Extraction and Recognition of Wiring Diagrams.pptx>), soprattutto le slide 2-5.
- [electronics-14-00833-with-cover.pdf](../Teoria_Papers/Papers/electronics-14-00833-with-cover.pdf)
- [Spiegazione.docx](../Teoria_Papers/Papers/Spiegazione.docx)
- [Spiegazione_HighLevel.docx](../Teoria_Papers/Spiegazione_HighLevel.docx)
- [results_yolov7.md](../first_part_object_detection/results_yolov7.md), [results_yolov8.md](../first_part_object_detection/results_yolov8.md) e [results_yolov11.md](../first_part_object_detection/results_yolov11.md) soltanto per ricostruire il contesto; i risultati vanno nel capitolo 4.

**Tabella candidata**

- **Tabella 2.2:** confronto tra approcci di detection: metodo, backbone/famiglia, dominio, dataset, oggetti piccoli, disponibilità del codice e principali limiti.

**Da non anticipare**

- Configurazioni `exp01`-`exp12`.
- Metriche del checkpoint `exp11b1`.
- Motivazione finale della scelta del nostro modello, che appartiene ai capitoli 3-4.

---

## 2.4 Dalla detection alla rappresentazione topologica

### 2.4.1 Pipeline a livelli

**Contenuti da trattare**

- Separazione tra layer dei componenti, layer testuale e layer delle connessioni.
- Riduzione dell'interferenza tra simboli, testo e linee.
- Approcci modulari rispetto a sistemi end-to-end.

### 2.4.2 OCR nei diagrammi tecnici

**Contenuti da trattare**

- Text detection e text recognition.
- Tesseract, EasyOCR e PaddleOCR come famiglie di strumenti.
- Testo ruotato, font tecnici, sovrapposizione con i fili e terminologia di dominio.
- Associazione spaziale tra testo riconosciuto e componente.

**Fonti da usare senza trasformare la sezione in una rassegna generale sull'OCR**

- [Tesseract User Manual](https://tesseract-ocr.github.io/tessdoc/): documentazione primaria del motore OCR classico usato nella pipeline.
- [EasyOCR](https://github.com/JaidedAI/EasyOCR): repository e documentazione ufficiale; il progetto usa CRAFT per la detection e CRNN per il riconoscimento.
- Y. Baek et al., [*Character Region Awareness for Text Detection*](https://arxiv.org/abs/1904.01941), CVPR 2019: riferimento CRAFT.
- C. Cui et al., [*PaddleOCR 3.0 Technical Report*](https://arxiv.org/abs/2507.05595), 2025: confronto moderno opzionale, non necessariamente parte della soluzione sviluppata.

### 2.4.3 Terminali, orientamento e semantica dei pin

**Contenuti da trattare**

- Perché il bounding box del componente non basta a ricostruire il circuito.
- Localizzazione dei terminali e stima dell'orientamento.
- Polarità, pin funzionali e componenti con più terminali.
- Strategie geometriche, template e classificatori dedicati.

### 2.4.4 Estrazione dei fili

**Contenuti da trattare**

- Binarizzazione e rimozione/mascheramento di testo e componenti.
- Operazioni morfologiche e skeletonization.
- Hough transform, connected components, segmentation e wire tracing.
- Interruzioni, rumore e ripristino delle linee tramite inpainting.

### 2.4.5 Junction, crossing e continuità elettrica

**Contenuti da trattare**

- Differenza tra incrocio connesso, incrocio non connesso, ponte e giunzione a T.
- Effetto di un errore locale sulla topologia completa.
- Regole geometriche e metodi appresi per la connectivity inference.

### 2.4.6 Costruzione del grafo

**Contenuti da trattare**

- Component graph, terminal graph e net graph.
- Nodi, terminali, archi e reti elettriche.
- Rappresentazioni intermedie modulari e ispezionabili.
- Vantaggi del grafo rispetto a una conversione diretta immagine-netlist.

### 2.4.7 Sistemi completi immagine-grafo

**Lavori candidati**

- CircuitSchematicImageInterpreter.
- Framework layered di Cao et al.
- Mani et al., per symbol detection, associazione del testo e graph search su P&ID.
- Putra et al., per l'estrazione delle connessioni fisiche dei cavi da wiring diagram industriali.
- Hu et al., per port localization e link prediction tramite Graph Attention Network.
- Modular Graph Extraction.
- Parsing tramite graph attention/link prediction.
- Image2Net, per rappresentazione e valutazione strutturale.
- J. Bayer et al., [*Instance Segmentation Based Graph Extraction for Handwritten Circuit Diagram Images*](https://arxiv.org/abs/2301.03155), per il confronto tra estrazione grafica tramite segmentazione e pipeline geometriche.

**Materiale interno**

- [Extraction and Recognition of Wiring Diagrams.pptx](<../Teoria_Papers/Extraction and Recognition of Wiring Diagrams.pptx>), in particolare la bibliografia della slide 5.
- [electronics-14-00833-with-cover.pdf](../Teoria_Papers/Papers/electronics-14-00833-with-cover.pdf)
- [Spiegazione.docx](../Teoria_Papers/Papers/Spiegazione.docx)
- [Spiegazione_HighLevel.docx](../Teoria_Papers/Spiegazione_HighLevel.docx)
- [doc_scripts_1.0/](../second_part_pipeline_topologica/doc_scripts_1.0/) come materiale tecnico per comprendere i problemi; non presentare qui la nostra implementazione.
- [deep-research-report.md](../third_part_from_json_to_spice/deep-research-report.md)

**Figure candidate**

- **Figura 2.3:** pipeline generale a livelli: componenti, testo, connessioni e grafo.
- **Figura 2.4:** differenza concettuale tra component graph, terminal graph e net graph.

**Tabella candidata**

- **Tabella 2.3:** lavori immagine-grafo con colonne: input, detection, OCR, terminali, fili, tipo di grafo, metrica topologica, dataset e codice disponibile.

---

## 2.5 Valutazione automatica della correttezza topologica

### 2.5.1 Metriche strutturali

**Contenuti da trattare**

- Exact match della netlist rispetto a equivalenza elettrica/topologica.
- Precision e recall delle connessioni.
- Graph Edit Distance e metriche normalizzate come NED.
- Limiti delle metriche puramente testuali.

### 2.5.2 Verifica visuale e multimodale

**Contenuti da trattare**

- Confronto tra immagine originale e rappresentazione strutturata.
- Uso di modelli multimodali come supporto alla revisione.
- Differenza tra validazione automatica, revisione umana e ground truth manuale.

### 2.5.3 LLM/VLM come judge

**Contenuti da trattare**

- Protocollo di valutazione basato su rubriche e output strutturati.
- Ripetibilità, bias, dipendenza dal prompt e coerenza della severità.
- Necessità di conservare input, risposta grezza e risultato aggregato.
- Un judge non sostituisce automaticamente una ground truth annotata.

**Fonti metodologiche essenziali**

- L. Zheng et al., [*Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*](https://arxiv.org/abs/2306.05685), 2023: single-answer grading, confronto pairwise, reference-guided grading e bias del judge.
- Y. Liu et al., [*G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment*](https://aclanthology.org/2023.emnlp-main.153/), EMNLP 2023: rubriche, passi di valutazione e correlazione con valutazioni umane.
- D. Chen et al., [*MLLM-as-a-Judge*](https://arxiv.org/abs/2402.04788), 2024: valutazione multimodale e limiti di scoring, ranking, allucinazioni e incoerenza.
- Usare questi lavori per motivare position bias, dipendenza dal prompt, necessità di una rubrica stabile, audit degli output e combinazione tra judge automatico e controlli deterministici/umani.

**Materiale interno**

- [RISULTATI_VERIFICA_TOPOLOGICA_GRAPH_JSON.md](../second_part_pipeline_topologica/RISULTATI_VERIFICA_TOPOLOGICA_GRAPH_JSON.md) soltanto per ricostruire il protocollo; numeri e risultati nel capitolo 4.
- output dei judge in [experiment_ai/](../../experiment_ai/).
- [deep-research-report.md](../third_part_from_json_to_spice/deep-research-report.md) per le metriche strutturali.

**Tabella candidata**

- **Tabella 2.4:** metodi di valutazione della topologia: ground truth manuale, metriche su archi, GED/NED, revisione visuale e LLM/VLM judge.

---

## 2.6 Dal grafo alla netlist e alla simulazione SPICE

### 2.6.1 Rappresentazioni circuitali intermedie

**Contenuti da trattare**

- Differenza tra grafo topologico, graph JSON, netlist e schematico visuale.
- Necessità di identificatori canonici per componenti, terminali e nodi.
- Tracciabilità delle trasformazioni tra una rappresentazione e la successiva.

### 2.6.2 Sistemi image-to-netlist

**Lavori candidati**

- SINA.
- Netlistify.
- Image2Net.
- Img2Sim.
- Auto-SPICE / Masala-CHAI.
- AMSNet e AMSnet 2.0.
- CircuitSchematicImageInterpreter.
- PCBnet, come aggiornamento recentissimo su dataset accoppiato schematico-netlist e correzione multi-agent.

**Aspetti da confrontare**

- Tipologia di input.
- Riconoscimento di componenti e orientamento.
- Metodo di connectivity inference.
- Gestione di testo e valori.
- Formato della netlist.
- Verifica strutturale o tramite simulazione.
- Dataset, codice e riproducibilità.

### 2.6.3 Fondamenti di SPICE e ngspice

**Contenuti da trattare**

- Netlist come descrizione dichiarativa di componenti e nodi.
- Analisi `.op`, `.dc`, `.ac` e `.tran` a livello introduttivo.
- Modelli primitivi, modelli vendor e sottocircuiti.
- Ruolo di massa, alimentazioni, parametri e condizioni iniziali.

**Fonti primarie**

- [Ngspice documentation](https://ngspice.sourceforge.io/docs.html) e [Ngspice User's Manual](https://ngspice.sourceforge.io/docs/ngspice-manual.pdf): fonti ufficiali per netlist, flusso di simulazione e analisi supportate.
- L. W. Nagel e D. O. Pederson, *SPICE (Simulation Program with Integrated Circuit Emphasis)*, UC Berkeley, 1973: riferimento storico da citare solo per l'origine di SPICE.

### 2.6.4 Informazioni mancanti e completamento semantico

**Contenuti da trattare**

- Valori non leggibili, modelli mancanti e pin mapping degli integrati.
- Uso di OCR, metadata, datasheet e configurazioni esterne.
- Netlist completa, netlist parziale e rappresentazione non simulabile.
- Importanza di non inventare valori o collegamenti.

### 2.6.5 Simulazione come verifica

**Contenuti da trattare**

- Errori sintattici rispetto a errori elettrici/topologici.
- Floating nodes, assenza di massa, modelli mancanti e convergenza.
- Uso dei risultati simulativi come evidenza per reporting e diagnosi.
- Limite: una simulazione riuscita non garantisce che il circuito ricostruito sia quello corretto.

**Materiale interno**

- [deep-research-report.md](../third_part_from_json_to_spice/deep-research-report.md)
- [Teoria_Integrazione json - Spice.docx](<../third_part_from_json_to_spice/Teoria_Integrazione json - Spice.docx>)
- [Estensione della pipeline con SPICE a partire dal graph JSON.odt](<../third_part_from_json_to_spice/Estensione della pipeline con SPICE a partire dal graph JSON.odt>)
- [stato_dell_arte_spice_to_viewer.md](../third_part_from_json_to_spice/viewer_simulator/stato_dell_arte_spice_to_viewer.md)
- datasheet e README dei modelli in [metadata/spice_models/](../../metadata/spice_models/).

**Figura candidata**

- **Figura 2.5:** livelli di rappresentazione: immagine -> grafo -> nodi elettrici -> netlist -> simulazione.

**Tabella candidata**

- **Tabella 2.5:** confronto dei sistemi image-to-netlist e netlist-to-simulation.

**Aggiornamenti 2026 da integrare**

- S. Aldowaish et al., [*SINA: A Fully Automated Circuit Schematic Image to Netlist Generator Using Artificial Intelligence*](https://arxiv.org/abs/2607.01609), luglio 2026.
- J. Ma et al., [*NetlistBench: Evaluating LLM Reliability in SPICE Netlist Recognition and Manipulation*](https://arxiv.org/abs/2608.12197), agosto 2026, accettato a MLCAD 2026: utile soprattutto per valutazione deterministica e conservazione della struttura.
- Z. Huang et al., [*PCBnet*](https://arxiv.org/abs/2608.27923), agosto 2026, accettato a ICLAD 2026: utile sia per dataset sia per confronto end-to-end.
- Questi lavori aggiornano il quadro ma non modificano l'architettura narrativa del capitolo.

---

## 2.7 Diagnosi circuitale assistita da modelli linguistici

### 2.7.1 Diagnosi tradizionale e sistemi esperti

**Contenuti da trattare**

- Controlli rule-based e sistemi esperti.
- Diagnosi basata su sintomi, misure e modelli circuitali.
- Limiti della sola conoscenza simbolica e della sola simulazione.

**Fonti da aggiungere**

- D. Binu e B. S. Kariyappa, [*A survey on fault diagnosis of analog circuits: Taxonomy and state of the art*](https://doi.org/10.1016/j.aeue.2017.01.002), 2017: tassonomia di fault dictionary, model-based diagnosis e metodi di apprendimento.
- Una sola ulteriore fonte classica model-based è sufficiente se necessaria; evitare una digressione storica non collegata ai circuiti valutati nella tesi.

### 2.7.2 Modelli linguistici e multimodali

**Contenuti da trattare**

- Ragionamento diretto sull'immagine rispetto a ragionamento su dati strutturati.
- Uso congiunto di schema, netlist, datasheet e risultati SPICE.
- Rischio di allucinazioni e necessità di grounding.

### 2.7.3 Assistente conversazionale

**Contenuti da trattare**

- Interazione domanda-risposta con contesto tecnico preassemblato.
- Vantaggi per spiegazione e troubleshooting.
- Limiti quando il modello non può verificare autonomamente le ipotesi.

### 2.7.4 Agenti con strumenti

**Contenuti da trattare**

- Differenza tra chat e agente tool-using.
- Pianificazione, selezione di scenari, esecuzione di simulatori e lettura dei risultati.
- Controllo degli strumenti, budget, stato persistente e audit trail.
- Rischi di azioni non necessarie, errori cumulativi e maggiore variabilità.

**Fonti metodologiche**

- S. Yao et al., [*ReAct: Synergizing Reasoning and Acting in Language Models*](https://arxiv.org/abs/2210.03629), 2022/2023: riferimento per alternanza tra ragionamento, azioni e osservazioni.
- P. Lewis et al., [*Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*](https://papers.nips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html), NeurIPS 2020: riferimento per grounding su conoscenza recuperata e provenienza delle informazioni.
- S. Nau, J. Krummenauer e A. Zimmermann, [*Evaluating LLM-based Workflows for Switched-Mode Power Supply Design*](https://arxiv.org/abs/2507.10639), versione 2 del 2025: caso circuitale con strumenti SPICE nel loop.

### 2.7.5 AI grounded sulla simulazione

**Lavori/filoni candidati**

- SPICEAssistant.
- Auto-SPICE / Masala-CHAI.
- AMSnet-KG e AMSnet-q.
- Sistemi di generazione/verifica di testbench da confermare nella ricerca bibliografica.

**Materiale interno**

- [deep-research-report.md](../third_part_from_json_to_spice/deep-research-report.md)
- [Teoria_Integrazione json - Spice.docx](<../third_part_from_json_to_spice/Teoria_Integrazione json - Spice.docx>)
- [agente_diagnostico_pipeline2.md](../third_part_from_json_to_spice/agent/agente_diagnostico_pipeline2.md)
- [stato_dell_arte_spice_to_viewer.md](../third_part_from_json_to_spice/viewer_simulator/stato_dell_arte_spice_to_viewer.md)

**Figura candidata**

- **Figura 2.6:** confronto concettuale tra LLM diretto, LLM grounded e agente con strumenti.

**Tabella candidata**

- **Tabella 2.6:** approcci alla diagnosi AI con colonne: input, accesso a SPICE, uso di strumenti, output, verificabilità e limite principale.

---

## 2.8 Valutazione di assistenti e agenti diagnostici

### 2.8.1 Criteri di qualità

**Contenuti da trattare**

- Correttezza tecnica.
- Aderenza alle evidenze disponibili.
- Utilità diagnostica.
- Capacità di dichiarare incertezza e limiti.
- Successo completo, parziale e fallimento.

### 2.8.2 Confronto tra modalità operative

**Contenuti da trattare**

- Qualità rispetto a costo e latenza.
- Risposta singola rispetto a traiettoria agente.
- Effetto della disponibilità dell'immagine.
- Effetto di strumenti e scenari simulativi.

### 2.8.3 Protocolli con judge

**Contenuti da trattare**

- Rubriche, ground truth e judge packet.
- Judge umano, LLM judge e combinazioni ibride.
- Pairwise evaluation rispetto a punteggio assoluto.
- Threats to validity: un solo judge, prompt differenti, ordine degli input e non determinismo.

**Raccordo bibliografico**

- Riutilizzare qui Zheng et al., G-Eval e MLLM-as-a-Judge introdotti nel §2.5.3, evitando una seconda rassegna separata.
- La sezione deve trasformare quei principi nel vocabolario necessario al confronto CHAT-AGENT: unità di valutazione, rubrica, evidenze disponibili, output strutturato, gestione dei pareggi/fallimenti e ripetibilità.

**Materiale interno**

- [RISULTATI_DIAGNOSI_CIRCUITI_COMPLESSI.md](../second_part_pipeline_topologica/RISULTATI_DIAGNOSI_CIRCUITI_COMPLESSI.md) soltanto per protocollo e terminologia.
- [README della valutazione CHAT/AGENT](../../experiment_ai/chat_agent_evaluation_21/README.md) e relativi script di costruzione dei judge packet.
- [CAPITOLO_RISULTATI.md](../../experiment_ai/chat_agent_evaluation_21/results/CAPITOLO_RISULTATI.md) soltanto per ricostruire il disegno sperimentale; risultati nel capitolo 4.

**Tabella candidata**

- **Tabella 2.7:** metodi di valutazione di sistemi diagnostici AI e relative minacce alla validità.

---

## 2.9 Sintesi critica e posizionamento della tesi

### 2.9.1 Matrice comparativa finale

**Tabella principale del capitolo**

- **Tabella 2.8:** copertura end-to-end dei lavori correlati.

Colonne consigliate:

- dataset disponibile;
- component detection;
- OCR;
- terminali/orientamento;
- wire e connectivity extraction;
- rappresentazione a grafo;
- generazione di netlist;
- simulazione SPICE;
- diagnosi AI;
- agente con strumenti;
- metodo di valutazione;
- codice/dati disponibili.

### 2.9.2 Limiti ricorrenti dello stato dell'arte

**Ipotesi da verificare con le fonti prima della stesura**

- Pipeline spesso limitate a un singolo dominio o stile di diagramma.
- Forte dipendenza da dataset sintetici o piccoli benchmark.
- Valutazioni non direttamente confrontabili.
- Detection accurata che non implica topologia corretta.
- Gestione incompleta di valori, modelli e circuiti integrati.
- Pochi sistemi integrano in modo tracciabile immagine, grafo, SPICE e diagnosi.
- Validazione limitata di assistenti e agenti su circuiti eterogenei.

### 2.9.3 Spazio per la soluzione proposta

**Contenuti ammessi**

- Un solo paragrafo di raccordo.
- Identificazione del bisogno di una pipeline modulare e verificabile.
- Centralità di una rappresentazione strutturata intermedia.
- Uso della simulazione come evidenza e non come semplice output.
- Necessità di confrontare assistente conversazionale e agente con strumenti.

**Da rimandare al capitolo 3**

- Architettura concreta della Pipeline 1.
- Architettura concreta della Pipeline 2.
- Formati JSON/YAML implementati.
- Euristiche, algoritmi e parametri sviluppati.
- Scelta del checkpoint e integrazione software.

**Da rimandare al capitolo 4**

- Tutte le metriche YOLO.
- Punteggi dei 38 circuiti per la topologia.
- Benchmark dei modelli diagnostici.
- Risultati CHAT-AGENT sui 21 circuiti.
- Costi, latenze, errori e distribuzioni degli esiti.

---

## Piano complessivo di figure e tabelle

### Figure prioritarie

1. **Figura 2.1 - Tipi di diagramma e livelli informativi:** schema circuitale rispetto a wiring diagram.
2. **Figura 2.2 - Pipeline generale dello stato dell'arte:** immagine, componenti/testo/connessioni, grafo, netlist e simulazione. Accorpa le vecchie figure 2.3 e 2.5.
3. **Figura 2.3 - Rappresentazioni strutturali:** component graph, terminal graph e net graph.
4. **Figura 2.4 - Sistemi diagnostici:** LLM diretto, LLM grounded e agente con strumenti.

L'esempio immagine/bounding box/formato YOLO è opzionale e può essere spostato nel capitolo 3, dove si descrive concretamente il dataset.

### Tabelle prioritarie

1. Tabella 2.1 - Dataset per diagrammi elettrici.
2. Tabella 2.2 - Approcci immagine-grafo-netlist, accorpando detection, OCR, connettività e SPICE.
3. Tabella 2.3 - Metodi di valutazione: detection, topologia/netlist e judge.
4. Tabella 2.4 - Matrice comparativa end-to-end e posizionamento della tesi.

Le tabelle specialistiche inizialmente previste restano come schemi di raccolta dei dati, ma non devono necessariamente comparire tutte nella tesi. La matrice end-to-end è la più importante perché prepara direttamente il posizionamento della soluzione proposta.

---

## Materiali interni principali e loro ruolo

| Materiale | Uso nel capitolo 2 | Stato |
|---|---|---|
| [Extraction and Recognition of Wiring Diagrams.pptx](<../Teoria_Papers/Extraction and Recognition of Wiring Diagrams.pptx>) | Idea end-to-end, caso d'uso e primo nucleo di sei lavori correlati | Indice bibliografico interno; citare i paper originali |
| [Costruzione Dataset.docx](<../Teoria_Papers/Costruzione Dataset.docx>) | Dataset, annotazione, split e augmentation | Appunti da riscrivere e verificare |
| [Spiegazione_HighLevel.docx](../Teoria_Papers/Spiegazione_HighLevel.docx) | Tipi di diagramma, detection, OCR, line tracking, grafi e analisi dei sei paper del PowerPoint | Appunti estesi utili per prima parte e Pipeline 1.0; non fonte bibliografica finale |
| [Spiegazione.docx](../Teoria_Papers/Papers/Spiegazione.docx) | Analisi del framework layered di Cao et al. | Utile, ma ripetitivo e da confrontare col paper |
| [electronics-14-00833-with-cover.pdf](../Teoria_Papers/Papers/electronics-14-00833-with-cover.pdf) | Fonte scientifica primaria sul riconoscimento layered | Fonte verificabile già disponibile |
| [deep-research-report.md](../third_part_from_json_to_spice/deep-research-report.md) | Lavori image-to-netlist, SPICE e AI grounded | Ottima base; citazioni da ricostruire |
| [stato_dell_arte_spice_to_viewer.md](../third_part_from_json_to_spice/viewer_simulator/stato_dell_arte_spice_to_viewer.md) | Netlist, viewer, simulatori e posizionamento | Buona mappa; fonti da verificare |
| [Teoria_Integrazione json - Spice.docx](<../third_part_from_json_to_spice/Teoria_Integrazione json - Spice.docx>) | Fondamenti e motivazioni JSON-SPICE | Appunti metodologici da separare dalla letteratura |
| [agente_diagnostico_pipeline2.md](../third_part_from_json_to_spice/agent/agente_diagnostico_pipeline2.md) | Concetti di chat, agente e strumenti | Fonte progettuale; non prova dello stato dell'arte |
| Capitoli e CSV dei risultati | Comprendere protocolli e terminologia | Da citare nei capitoli 3-4, non come related work |

## Correzioni e cautele sui materiali grezzi

- Il file [deep-research-report.md](../third_part_from_json_to_spice/deep-research-report.md) nasce da una deep research esportata: i vecchi token interni di citazione non costituiscono riferimenti bibliografici e devono essere sostituiti con il registro di fonti verificabili contenuto nel documento.
- Per **SINA**, usare il titolo ufficiale *A Fully Automated Circuit Schematic Image to Netlist Generator Using Artificial Intelligence* e il valore end-to-end riportato dalla versione consultata del paper: **96,67%**. Non riutilizzare il precedente 96,47% senza distinguere la metrica a cui si riferiva.
- Per il lavoro di Nau, Krummenauer e Zimmermann, usare il titolo ufficiale *Evaluating LLM-based Workflows for Switched-Mode Power Supply Design*. La versione 2 riporta **269 task** e un solve rate dal **15% al 91%**; i precedenti valori “256 questioni” e “+38%” non vanno copiati.
- Espressioni valutative contenute negli appunti, come “più solido”, “migliore” o “research-grade”, vanno trasformate in confronti neutrali sostenuti da metriche, disponibilità dei dati e limiti dichiarati.
- La deep research JSON-first restringeva intenzionalmente il contributo alla parte a valle del riconoscimento. La tesi completa, invece, comprende anche dataset, addestramento YOLO e Pipeline 1.0: il capitolo 2 deve quindi mantenere l'intera catena già fissata in questa mappa.

---

## Nucleo bibliografico già identificato per la prima parte e la Pipeline 1.0

Questo elenco nasce dalla slide 5 di [Extraction and Recognition of Wiring Diagrams.pptx](<../Teoria_Papers/Extraction and Recognition of Wiring Diagrams.pptx>) ed è sviluppato nelle ultime pagine di [Spiegazione_HighLevel.docx](../Teoria_Papers/Spiegazione_HighLevel.docx). I riferimenti e i DOI sono stati ricontrollati sulle pagine degli editori o degli autori. Nella tesi andranno citati i lavori originali, non il PowerPoint o il documento Word.

| Lavoro verificato | Pertinenza rispetto alla tesi | Collocazione candidata |
|---|---|---|
| W. Cao, Z. Chen, C. Wu e T. Li, “A Layered Framework for Universal Extraction and Recognition of Electrical Diagrams”, *Electronics*, 14(5), 833, 2025. [DOI](https://doi.org/10.3390/electronics14050833) | Framework a livelli: element detection con YOLOv7, OCR e ricostruzione delle connessioni. È il riferimento più diretto per l'impostazione della prima parte e per la separazione degli stage della Pipeline 1.0. | §2.3 e §2.4 |
| S. Mani, M. A. Haddad, D. Constantini, W. Douhard, Q. Li e L. Poirier, “Automatic Digitization of Engineering Diagrams Using Deep Learning and Graph Search”, *CVPR Workshops*, pp. 673-679, 2020. [DOI](https://doi.org/10.1109/CVPRW50498.2020.00096) | Pipeline per P&ID con symbol detection, riconoscimento/associazione del testo e graph search sulle linee. È molto pertinente alla struttura generale della Pipeline 1.0. | §2.4, in particolare OCR, connessioni e grafo |
| C.-Y. Huang, H.-I. Chen, H.-W. Ho, P.-H. Kang, M. P.-H. Lin, W.-H. Liu e H. Ren, “Netlistify: Transforming Circuit Schematics into Netlists with Deep Learning”, *ACM/IEEE MLCAD*, pp. 1-8, 2025. [DOI](https://doi.org/10.1109/MLCAD65511.2025.11189145) - [pagina degli autori](https://research.nvidia.com/labs/electronic-design-automation/publication/liu2025mlcad/) | Integra component detection, orientamento e connectivity analysis fino alla netlist. È soprattutto il ponte tra l'output topologico della Pipeline 1.0 e la parte JSON/netlist/SPICE. | §2.4 e §2.6 |
| A. R. Putra, S. Ha e K.-P. Park, “Automatic Extraction of Cable Connection Information from 2D Drawings for Electrical Outfittings Design in Shipyards”, *International Journal of Naval Architecture and Ocean Engineering*, 16, 100630, 2024. [DOI](https://doi.org/10.1016/j.ijnaoe.2024.100630) | Caso industriale centrato su wiring diagram, classificazione del testo e tracciamento delle cable route. Rafforza la motivazione e il problema del line tracking fisico nella Pipeline 1.0. | §2.1 e §2.4 |
| W. Hu, X. Zhan e M. Tong, “Parsing Netlists of Integrated Circuits from Images via Graph Attention Network”, *Sensors*, 24(1), 227, 2024. [DOI](https://doi.org/10.3390/s24010227) | Combina component detection, localizzazione delle porte e link prediction su grafo. Offre un confronto appreso con le strategie geometriche ed euristiche di ricostruzione topologica. | §2.4 e §2.5 |
| C. R. Kelly e J. M. Cole, “Digitizing Images of Electrical-Circuit Schematics”, *APL Machine Learning*, 2(1), 016109, 2024. [DOI](https://doi.org/10.1063/5.0177755) - [repository](https://github.com/C-R-Kelly/CircuitSchematicImageInterpreter) | Pipeline pratica con pattern recognition, OCR, network graph e possibile conversione in netlist SPICE. Copre la Pipeline 1.0 e anticipa il passaggio alla Pipeline 2.0. | §2.3, §2.4 e §2.6 |

### Come usare questo nucleo durante la scrittura

- **Prima parte - dataset e object detection:** partire soprattutto da Cao et al.; usare Kelly e gli altri lavori per mostrare come il detector si inserisce in una pipeline più ampia.
- **Pipeline 1.0 - OCR, terminali, fili e graph JSON:** confrontare soprattutto Cao, Mani, Putra, Hu e Kelly.
- **Ponte verso Pipeline 2.0:** usare Netlistify e Kelly per motivare il passaggio da grafo/connettività a netlist.
- Per ogni paper recuperare e verificare metodo, dataset, metriche, limiti e disponibilità del codice prima di scrivere affermazioni definitive.
- Le interpretazioni contenute in [Spiegazione_HighLevel.docx](../Teoria_Papers/Spiegazione_HighLevel.docx) sono appunti utili, ma vanno sempre confrontate con il paper originale: non devono diventare citazioni indirette o affermazioni non verificate.

---

## Checklist bibliografica prima della stesura

### Fonti già individuate e verificabili

- Standard: IEC 60617, IEC 61082-1 e, se utile, IEEE/ANSI 315.
- Detector: YOLO originale, Faster R-CNN, YOLOv7 e documentazione ufficiale YOLO11.
- Dataset/graph extraction: CGHD, Modular Graph Extraction, Image2Net e PCBnet.
- Pipeline elettriche: Cao, Mani, Putra, Hu, Kelly, Netlistify, SINA, Auto-SPICE/Masala-CHAI e famiglia AMSNet.
- Simulazione e AI: manuale ngspice, SPICEAssistant, AMSnet-KG, AMSnet-q e NetlistBench.
- Judge: MT-Bench/LLM-as-a-Judge, G-Eval e MLLM-as-a-Judge.
- Diagnosi e agenti: survey sulla fault diagnosis analogica, ReAct e RAG.

### Verifiche ancora da eseguire mentre si prepara la bibliografia finale

- Recuperare metadati completi, venue, versione e DOI di Img2Sim/Img2Sim-V2, AMSNet, AMSnet 2.0 e AMSnet-KG.
- Verificare il repository ufficiale e la licenza di ogni dataset o progetto dichiarato open source.
- Controllare sul PDF originale ogni numero che entrerà in tabella; non usare valori derivati soltanto dai riassunti locali.
- Decidere con il relatore se includere i lavori di agosto 2026 oppure fissare un cutoff bibliografico precedente.
- Recuperare una fonte primaria specifica per wire/junction extraction soltanto se i lavori end-to-end già selezionati non bastano a descrivere il confronto.

Per ogni lavoro conservare: riferimento completo, DOI/URL ufficiale, versione consultata, obiettivo, dataset, metodo, metriche, limiti, codice/dati disponibili e relazione con la tesi.

---

## Decisioni strutturali già fissate

- Ordine del capitolo coerente con l'evoluzione del progetto.
- Stato dell'arte organizzato per problemi tecnici, non come diario cronologico del lavoro.
- Nessun risultato sperimentale della tesi nel capitolo 2.
- La Pipeline 1 corrisponde ai temi di detection, OCR, terminali, fili e grafo.
- La sua verifica tramite judge corrisponde alla sezione sulla valutazione topologica.
- La Pipeline 2 corrisponde ai temi graph JSON, netlist e SPICE.
- CHAT e AGENT corrispondono ai sistemi diagnostici grounded e tool-using.
- Le valutazioni dei modelli e dei judge vengono introdotte metodologicamente qui e riportate numericamente nel capitolo 4.
- Il capitolo termina con il gap della letteratura e prepara il capitolo sulla soluzione proposta.
