## 08_visualize_graph

### Valutazione generale
Il passo 08 è stato introdotto per aggiungere un livello di **visualizzazione esplicita** del grafo costruito nel passo 07.  
Mentre il passo 07 esporta la struttura topologica del diagramma in forma di `graph.json` e CSV, il passo 08 non modifica il grafo, ma lo rende **leggibile e ispezionabile** sia in forma statica sia in forma interattiva.

In altre parole:

- **07_export_graph**: costruisce ed esporta il grafo;
- **08_visualize_graph**: genera le visualizzazioni del grafo.

Questa separazione è utile perché mantiene distinto il livello dei dati dal livello della rappresentazione visiva.

---

### Obiettivo del passo 08
L’obiettivo dello script 08 non è creare un nuovo database o una nuova topologia, ma produrre una visualizzazione che permetta di:

- controllare rapidamente se la struttura del grafo è coerente;
- interpretare meglio le connessioni tra componenti e net;
- evidenziare eventuali collegamenti deboli o sospetti;
- collegare il grafo astratto al diagramma originale.

Il passo 08 è quindi un livello di **debug, interpretazione e documentazione** del graph database prodotto dalla pipeline.

---

### Input dello script
Lo script legge come input i file `*_graph.json` prodotti dal passo 07, cioè i grafi già esportati nella cartella:

- `outputs/topology_v1/07_export_graph/graph_json`

Ogni file contiene già:
- i nodi del grafo (`Diagram`, `Component`, `Terminal`, `Net`);
- gli archi (`HAS_COMPONENT`, `HAS_NET`, `HAS_TERMINAL`, `CONNECTED_TO`);
- i metadati e i summary del diagramma;
- le informazioni di affidabilità dei match terminale→net.

Di conseguenza, il passo 08 lavora sopra una struttura già completa, senza dover ricostruire la topologia.

---

### Output dello script
Per mantenere coerenza con il passo 07, anche il passo 08 è stato organizzato in modalità batch, con una cartella di output dedicata:

- `outputs/topology_v1/08_visualize_graph`

All’interno di questa cartella vengono salvate più visualizzazioni del grafo, in sottocartelle separate:

- `full_png`
- `full_html`
- `component_net_png`
- `component_net_html`
- `overlay`

e una pagina iniziale:

- `index.html`

Questa struttura rende il passo 08 coerente con il resto della pipeline e permette di generare tutte le visualizzazioni in modo automatico per l’intero batch.

---

### Tipi di visualizzazione generati

#### 1. Full graph
La prima vista generata è il **grafo completo**, che mantiene esplicitamente tutti i livelli del modello:

- `Diagram`
- `Component`
- `Terminal`
- `Net`

e tutte le relazioni:

- `HAS_COMPONENT`
- `HAS_NET`
- `HAS_TERMINAL`
- `CONNECTED_TO`

Questa è la vista più fedele al modello dati effettivamente esportato nel passo 07.  
Serve soprattutto come **vista di debug topologico**, perché permette di verificare che:

- i componenti siano presenti;
- i terminali siano stati creati correttamente;
- le net siano state esportate;
- i collegamenti terminale→net siano coerenti.

Per migliorare la leggibilità di questa vista sono stati introdotti alcuni accorgimenti:
- etichetta breve per il nodo `Diagram`;
- ordinamento più stabile dei componenti;
- ordinamento delle net per `net_index`;
- alleggerimento visivo degli archi strutturali (`HAS_*`);
- possibilità di non mostrare sempre il testo dei terminali, lasciandolo disponibile in hover.

In questo modo il grafo completo resta corretto dal punto di vista strutturale, ma diventa più leggibile rispetto a una semplice visualizzazione grezza.

---

#### 2. Component-Net view
La seconda vista è una **proiezione semplificata** del grafo, in cui i terminali non vengono mostrati come livello esplicito e si costruisce invece una relazione derivata del tipo:

- `Component -> Net`

Questa vista non sostituisce il grafo completo, ma ne rappresenta una versione più leggibile dal punto di vista umano.

Il motivo è che, nella vista completa, il livello `Terminal` è molto importante per il database e per il ragionamento automatico, ma tende a rendere il grafo troppo denso visivamente.  
La vista `Component-Net` consente invece di capire più rapidamente:

- a quali net è collegato un componente;
- quali componenti insistono sulla stessa net;
- quali connessioni sono sospette o deboli.

Questa è quindi la visualizzazione più utile per una lettura sintetica del circuito.

---

#### 3. Overlay sul diagramma originale
La terza vista è una **overlay** costruita sopra l’immagine originale del diagramma.

L’idea è mantenere il riferimento visivo con il circuito di partenza, mostrando sul diagramma:
- i componenti rilevati;
- i terminali;
- le net;
- i collegamenti principali.

Questa vista è utile perché collega il grafo astratto alla geometria del diagramma reale.  
Dal punto di vista pratico, aiuta molto a capire se la struttura topologica prodotta dalla pipeline è coerente con ciò che si vede nell’immagine.

---

### Output statico e output interattivo
Per ciascuna vista, lo script produce due tipi di output:

- **PNG**, utile per documentazione, report, tesi e slide;
- **HTML interattivo**, utile per l’ispezione locale nel browser.

Le versioni HTML permettono di:
- visualizzare hover informativi sui nodi;
- visualizzare hover sugli archi;
- distinguere meglio i tipi di nodo;
- controllare dettagli come `match_confidence`, `is_suspicious_match`, `match_warnings`, ecc.

Questa doppia esportazione è importante perché i PNG sono adatti alla documentazione statica, mentre gli HTML sono molto più utili per il controllo e il debug del grafo.

---

### Miglioramenti introdotti nella visualizzazione
Durante lo sviluppo del passo 08 non ci si è limitati a una semplice stampa del grafo, ma sono stati introdotti miglioramenti specifici per renderlo più leggibile.

In particolare:

#### 1. Ordinamento più leggibile dei nodi
I componenti vengono ordinati in modo più vicino alla disposizione spaziale del diagramma, invece di comparire in ordine puramente arbitrario.  
Le net vengono ordinate in modo stabile tramite `net_index`.  
Anche i terminali vengono organizzati in modo più coerente rispetto al componente di appartenenza.

#### 2. Alleggerimento della full view
Nella vista completa gli archi strutturali sono stati resi più leggeri, mentre gli archi `CONNECTED_TO` restano quelli visivamente più importanti.  
I terminali rimangono nel grafo, ma senza dominare la visualizzazione.

#### 3. Evidenziazione dei match sospetti
I collegamenti con `is_suspicious_match = true` vengono evidenziati in modo distinto, ad esempio con colore rosso o stile tratteggiato.  
Questo permette di individuare subito i casi più delicati emersi dal passo 06.

#### 4. Dashboard iniziale
È stata introdotta anche una `index.html` che funziona come pagina iniziale del batch.  
Questa pagina raccoglie i diagrammi elaborati e permette di accedere facilmente alle diverse viste generate.

Nella versione evoluta dell’index sono stati aggiunti:
- layout più leggibile;
- card per diagramma;
- preview delle immagini;
- summary numerici;
- evidenziazione dei casi con match sospetti;
- link diretti alle varie visualizzazioni.

---

### Perché il passo 08 è utile nel progetto
Il passo 08 è importante perché il graph database non deve essere solo corretto dal punto di vista strutturale, ma deve essere anche:

- **ispezionabile**
- **spiegabile**
- **controllabile**

Questo è particolarmente rilevante per l’obiettivo del progetto, che è usare il grafo del diagramma come supporto a un sistema di AI.  
Prima di arrivare all’integrazione con il graph DB e con l’AI, è fondamentale poter verificare visivamente che:

- i nodi siano corretti;
- le relazioni siano coerenti;
- le net siano ragionevoli;
- i match sospetti siano identificati chiaramente.

Il passo 08 svolge esattamente questa funzione intermedia.

---

### Ruolo rispetto al graph database finale
Lo script 08 non è ancora il graph database vero e proprio, ma rappresenta un passaggio importante verso di esso.

Più precisamente:
- il **passo 07** definisce il grafo in forma strutturata;
- il **passo 08** lo rende leggibile e validabile;
- un eventuale **passo successivo** potrà poi importare questo grafo in un sistema come Neo4j.

Quindi il passo 08 può essere visto come uno strato di **visual analytics** sopra l’output topologico della pipeline.

---

### Sintesi
In conclusione, il passo 08 è stato introdotto per visualizzare in modo strutturato i grafi esportati dal passo 07.

Lo script:
- legge i `graph.json` del batch;
- genera una vista completa del grafo;
- genera una vista semplificata `Component -> Net`;
- genera una overlay sul diagramma originale;
- salva tutto in una cartella dedicata con output PNG e HTML;
- crea una pagina iniziale `index.html` per navigare il batch.

Questa fase non modifica la topologia del circuito, ma migliora in modo sostanziale la possibilità di:
- controllare il risultato della pipeline;
- interpretare il grafo;
- preparare i dati a un futuro uso in un graph database e come supporto al ragionamento automatico dell’AI.