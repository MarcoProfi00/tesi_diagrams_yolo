# Script 06 — `06_render_graph_report.py`

## Scopo del passo 06

Lo script `06_render_graph_report.py` è il passo finale di visualizzazione della pipeline. Prende in ingresso i JSON prodotti dal passo **05 — `05_build_terminal_graph.py`** e genera un report navigabile per ogni circuito.

Il passo 05 produce già il grafo topologico finale del circuito, cioè una struttura dati che descrive quali terminali sono collegati tra loro. Il passo 06 non ricostruisce la topologia e non modifica il grafo: il suo compito è rendere quel risultato più leggibile attraverso:

- una pagina HTML riepilogativa dell’intero batch;
- una pagina HTML per ogni circuito;
- una vista completa del grafo;
- una vista compatta componenti/net;
- immagini PNG statiche delle viste;
- una copia del JSON finale del passo 05 dentro la cartella del report;
- una copia dell’immagine del circuito, quando disponibile.

L’obiettivo è avere un output comodo per ispezionare rapidamente se il grafo prodotto dal passo 05 è coerente con lo schema elettrico.

---

## Filosofia generale

Il passo 06 nasce come strumento di verifica e documentazione.

Durante lo sviluppo della pipeline, leggere direttamente il JSON del passo 05 può diventare difficile, soprattutto quando il circuito contiene molti componenti, molti terminali e molti nodi elettrici. Per questo motivo lo script costruisce due rappresentazioni grafiche diverse:

### 1. Vista completa

La vista completa mantiene tutta la gerarchia informativa:

```text
circuito → classi → componenti → terminali → net
```

Questa vista è utile per debug dettagliato, perché permette di vedere:

- a quale classe appartiene ogni componente;
- quali terminali appartengono a ciascun componente;
- quali terminali confluiscono nello stesso nodo elettrico;
- quali terminali sono segnalati nei warning.

### 2. Vista compatta

La vista compatta elimina la gerarchia intermedia e mostra solo:

```text
componenti ↔ net
```

Questa è la vista più leggibile per l’analisi topologica, perché mette in evidenza i nodi elettrici comuni. Se due o più componenti arrivano alla stessa net gialla, allora condividono lo stesso collegamento elettrico.

La vista compatta evita anche un problema tipico dei grafi componente-componente: quando tre componenti sono collegati allo stesso filo, non bisogna rappresentarli come tre collegamenti indipendenti, ma come un unico nodo comune. La net serve proprio a questo.

---

## Input dello script

Lo script legge i file JSON presenti nella cartella del passo 05:

```text
outputs/<PIPELINE_DATASET>/05_build_terminal_graph
```

Ogni JSON deve contenere almeno:

- `image_id` o `image_name`;
- `components`;
- `graph`;
- eventuale `terminal_metadata`;
- eventuale `warnings`.

Il campo più importante è `graph`, che rappresenta il grafo finale prodotto dal passo 05. La struttura attesa è una mappa terminale → terminali collegati:

```json
{
  "resistor22.1_t1": ["capacitor4.1_t1", "ic11.1_left_2"],
  "capacitor4.1_t1": ["resistor22.1_t1", "ic11.1_left_2"]
}
```

Il passo 06 trasforma questa rappresentazione a lista di adiacenza in gruppi di terminali connessi, chiamati `net_groups`.

---

## Output prodotto

Per ogni file JSON del passo 05 lo script crea una sottocartella dedicata:

```text
outputs/<PIPELINE_DATASET>/06_graph_report/<image_id>/
```

Dentro questa cartella vengono prodotti:

```text
<file>.json
```

Copia del JSON finale del passo 05.

```text
graph.html
```

Pagina HTML della vista completa.

```text
graph.png
```

Immagine PNG statica della vista completa.

```text
graph_compact.html
```

Pagina HTML della vista compatta componenti/net.

```text
graph_compact.png
```

Immagine PNG statica della vista compatta.

```text
<immagine originale o debug>
```

Copia dell’immagine del circuito, se lo script riesce a trovarla.

Alla fine dell’esecuzione viene inoltre generata una pagina indice:

```text
outputs/<PIPELINE_DATASET>/06_graph_report/index.html
```

Questa pagina contiene una card per ogni circuito del batch, con collegamenti diretti alle viste HTML, alle immagini PNG e al JSON copiato.

---

## Struttura delle cartelle

Con i percorsi di default, la struttura è questa:

```text
outputs/
└── <PIPELINE_DATASET>/
    ├── 01_detect_components/
    ├── 05_build_terminal_graph/
    │   ├── circuito_1.json
    │   ├── circuito_2.json
    │   └── ...
    └── 06_graph_report/
        ├── index.html
        ├── circuito_1/
        │   ├── circuito_1.json
        │   ├── graph.html
        │   ├── graph.png
        │   ├── graph_compact.html
        │   ├── graph_compact.png
        │   └── immagine_circuito.jpg
        └── circuito_2/
            ├── circuito_2.json
            ├── graph.html
            ├── graph.png
            ├── graph_compact.html
            ├── graph_compact.png
            └── immagine_circuito.jpg
```

---

## Esecuzione

Lo script può essere eseguito direttamente:

```bash
python scripts/pipeline_1.0/06_render_graph_report.py
```

Usa come dataset di default il valore della variabile d’ambiente `PIPELINE_DATASET`, se presente. In caso contrario usa il dataset impostato nel file:

```python
pipeline1.0/batch_v9_1_primo_set_analog_meter_connector_transformer
```

È possibile passare manualmente le cartelle tramite argomenti CLI:

```bash
python scripts/pipeline_1.0/06_render_graph_report.py \
  --input-dir outputs/pipeline1.0/batch_v10_ic/05_build_terminal_graph \
  --detect-dir outputs/pipeline1.0/batch_v10_ic/01_detect_components \
  --output-dir outputs/pipeline1.0/batch_v10_ic/06_graph_report
```

Gli argomenti disponibili sono:

| Argomento | Significato |
|---|---|
| `--input-dir` | Cartella contenente i JSON del passo 05 |
| `--detect-dir` | Cartella del passo 01, usata per recuperare l’immagine originale o l’immagine debug |
| `--output-dir` | Cartella dove salvare il report del passo 06 |

---

# Procedimento completo del passo 06

## 1. Lettura dei JSON del passo 05

La funzione `main()` individua tutti i file `.json` presenti nella cartella di input.

I file vengono ordinati con `path_sort_key`, che gestisce meglio i nomi con numeri. In questo modo un batch con file come:

```text
1.json
2.json
10.json
```

viene ordinato in modo naturale, evitando l’ordine lessicografico puro:

```text
1.json
10.json
2.json
```

Per ogni JSON viene chiamata:

```python
render_one_json(json_path, detect_dir, output_dir)
```

---

## 2. Costruzione delle strutture interne del grafo

Il JSON del passo 05 contiene un grafo terminale-terminale. Per visualizzarlo in modo più leggibile, lo script lo trasforma in gruppi di terminali connessi.

Questa parte viene gestita principalmente da:

```python
extract_graph_structures(data)
```

La funzione costruisce:

- lista dei componenti;
- indice terminale → componente;
- indice terminale → dati terminale;
- lista ordinata dei terminali;
- ordine delle classi;
- adiacenza non orientata;
- gruppi di net.

Il punto chiave è che il grafo del passo 05 viene interpretato come **non orientato**. Se il JSON dice che `A` è collegato a `B`, allora per la visualizzazione valgono entrambi:

```text
A ↔ B
```

Questo è coerente con un nodo elettrico, che non ha direzione.

---

## 3. Ricostruzione delle net

La funzione:

```python
build_net_groups(adjacency, terminal_order)
```

visita il grafo tramite BFS e trova le componenti connesse.

Ogni componente connessa del grafo diventa una net:

```json
{
  "net_id": "net_1",
  "label": "1",
  "terminal_ids": [
    "resistor22.1_t1",
    "capacitor4.1_t1",
    "ic11.1_left_2"
  ]
}
```

Questa trasformazione è importante perché la vista grafica non mostra archi terminale-terminale separati, ma nodi elettrici espliciti.

Quindi un gruppo:

```text
A, B, C
```

non viene disegnato come:

```text
A—B
A—C
B—C
```

ma come:

```text
A ─┐
B ─┼── net_1
C ─┘
```

Questa rappresentazione è molto più leggibile e più fedele al concetto elettrico di nodo.

---

## 4. Gestione dei terminali non presenti nella lista componenti

La funzione:

```python
attach_unknown_terminals(...)
```

serve a gestire un caso anomalo: il grafo può contenere terminali che non compaiono più nella lista dei componenti.

Può succedere durante lo sviluppo della pipeline, ad esempio se:

- un terminale è stato creato da una fase precedente ma poi non è più presente nel componente;
- un collegamento speciale ha introdotto un terminale simbolico;
- c’è una discrepanza tra `graph` e `components`.

In questi casi lo script non interrompe l’esecuzione. Crea invece componenti fittizi:

```text
unknown_component_1
unknown_component_2
...
```

con classe:

```text
Unknown
```

Questo permette al report di mostrare comunque l’informazione e rende più facile individuare l’incoerenza.

---

## 5. Costruzione della vista completa

La funzione:

```python
build_visual_model(data)
```

costruisce il modello grafico completo.

La struttura logica è:

```text
root → classi → componenti → terminali → net
```

I nodi prodotti sono di cinque tipi:

| Tipo nodo | Significato | Colore nel report |
|---|---|---|
| `root` | circuito corrente | rosso |
| `class` | classe del componente | beige |
| `component` | componente rilevato | verde |
| `terminal` | terminale del componente | rosa |
| `net` | nodo elettrico | giallo |

Se un terminale compare nei warning `unconnected_terminals` o `unmatched_terminals`, viene disegnato come:

```text
warning_terminal
```

con uno stile più evidente.

### Informazioni mostrate nei tooltip

I tooltip della vista completa contengono informazioni utili al debug.

Per i componenti possono comparire:

- id componente;
- classe;
- instance id;
- display name;
- `ic_marking`, se presente;
- `component_subtype`, se presente;
- `state`, se presente.

Per i terminali possono comparire:

- terminal id;
- componente associato;
- nome terminale;
- posizione relativa;
- display name;
- pin number;
- pin label.

Questa parte è particolarmente utile per gli Integrated Circuit, perché permette di vedere nel grafo anche le informazioni OCR aggiunte nei passi precedenti.

---

## 6. Costruzione della vista compatta

La funzione:

```python
build_compact_visual_model(data)
```

costruisce una seconda rappresentazione più semplice.

In questa vista ci sono solo due tipi principali di nodi:

```text
component
net
```

La logica è:

- ogni componente diventa un nodo verde;
- ogni net diventa un nodo giallo;
- un arco componente → net viene creato se almeno un terminale di quel componente appartiene a quella net.

Se più terminali dello stesso componente appartengono alla stessa net, viene creato comunque un solo arco, ma nel tooltip dell’arco vengono elencati tutti i terminali coinvolti.

Esempio:

```text
TDA7000 → net_3
```

Tooltip:

```text
TDA7000 -> net_3
Terminali del componente su questa net:
pin13 (ic11.1_left_1)
pin14 (ic11.1_left_2)
```

Questa scelta evita grafi troppo densi e rende la vista compatta adatta all’ispezione rapida.

---

## 7. Calcolo delle posizioni dei nodi

Lo script non usa un layout automatico tipo force-directed. Usa invece un layout deterministico a colonne.

### Vista completa

Le colonne sono definite da `LAYER_X`:

```python
LAYER_X = {
    "root": 90,
    "class": 270,
    "component": 500,
    "terminal": 780,
    "net": 1080,
}
```

Quindi la lettura è sempre da sinistra verso destra:

```text
circuito → classe → componente → terminale → net
```

La funzione che calcola queste posizioni è:

```python
compute_positions(...)
```

La distanza verticale tra i terminali è adattiva. Se il circuito ha tanti terminali, la spaziatura viene ridotta entro limiti ragionevoli; se ha pochi terminali, la spaziatura aumenta per rendere il grafico più leggibile.

### Vista compatta

La vista compatta usa:

```python
compute_compact_component_positions(...)
compute_compact_net_positions(...)
```

I componenti vengono disposti in una colonna a sinistra. Le net vengono disposte in una colonna a destra, cercando di allinearle alla media verticale dei componenti collegati.

Questo riduce gli incroci e rende più semplice capire quali componenti condividono un nodo.

---

## 8. Rendering PNG

La funzione:

```python
render_png(model, png_path)
```

crea un’immagine statica del grafo usando Matplotlib.

Lo script imposta:

```python
matplotlib.use("Agg")
```

Questo backend permette di generare immagini anche in ambienti senza interfaccia grafica, ad esempio durante esecuzioni batch o su server.

Il PNG è utile per:

- documentazione veloce;
- controllo visivo senza aprire HTML;
- inserimento in report;
- confronto tra esecuzioni della pipeline.

---

## 9. Rendering SVG e HTML interattivo

Le pagine HTML non usano librerie JavaScript esterne. Lo script genera direttamente un SVG e una piccola logica JavaScript per navigarlo.

Le funzioni principali sono:

```python
svg_circle(node)
build_svg(model)
```

Ogni nodo SVG contiene un tag `<title>`, quindi passando con il mouse sopra un nodo si leggono le informazioni di debug.

La pagina HTML aggiunge:

- zoom con rotella del mouse;
- pan trascinando il grafo;
- tooltip nativi SVG;
- link al JSON;
- link alla vista alternativa;
- link al PNG.

Questa scelta è pratica perché il report resta completamente locale: basta aprire `index.html` nel browser.

---

## 10. Sezione warning

Lo script legge il campo:

```json
"warnings"
```

prodotto dal passo 05 e lo mostra nel report.

Le categorie visualizzate sono:

```text
unconnected_terminals
unmatched_terminals
suspicious_matches
```

La funzione responsabile è:

```python
build_warning_html(warnings)
```

Per ogni categoria viene creata una box HTML. Se non ci sono elementi, la box mostra:

```text
Nessun elemento.
```

Questa sezione è molto utile perché permette di capire subito se il grafo è pulito oppure se ci sono terminali problematici.

---

## 11. Pagina indice del batch

Alla fine dell’elaborazione viene generata:

```text
index.html
```

La funzione responsabile è:

```python
build_index_page(items, output_dir)
```

La pagina indice contiene una card per ogni circuito.

Ogni card mostra:

- anteprima dell’immagine del circuito;
- id immagine;
- numero di componenti;
- numero di terminali;
- numero di net;
- numero di terminali isolati;
- numero di terminali unmatched;
- numero di match sospetti;
- link alla vista compatta HTML;
- link alla vista compatta PNG;
- link alla vista completa HTML;
- link alla vista completa PNG;
- link al JSON del passo 05.

Questa pagina è il punto di ingresso principale del report.

---

# Spiegazione dettagliata delle funzioni

## `parse_args()`

**Scopo:** leggere gli argomenti da riga di comando.

### Cosa produce

Restituisce un oggetto `argparse.Namespace` con:

- `input_dir`;
- `detect_dir`;
- `output_dir`.

### Perché serve

Permette di usare lo script sia con i percorsi di default sia con percorsi manuali. Questo è utile quando si lavora su batch diversi.

---

## `load_json(path)`

**Scopo:** caricare un file JSON.

### Cosa fa

- apre il file in UTF-8;
- restituisce un dizionario Python.

---

## `save_json(path, data)`

**Scopo:** salvare un dizionario Python come JSON leggibile.

### Cosa fa

- usa `indent=2`;
- usa `ensure_ascii=False`;
- mantiene leggibili eventuali caratteri non ASCII.

Nel passo 06 viene usata per copiare il JSON finale del passo 05 dentro la cartella del report.

---

## `prettify_name(value)`

**Scopo:** rendere più leggibile un nome tecnico.

### Esempio

```text
Integrated_Circuit → Integrated Circuit
unconnected_terminals → unconnected terminals
```

---

## `short_component_label(component)`

**Scopo:** scegliere l’etichetta breve da mostrare sul nodo componente.

### Logica

Se il componente è un Integrated Circuit, la funzione dà priorità a:

1. `ic_marking`;
2. `display_name`;
3. `component_subtype`.

Questo significa che un componente IC può essere visualizzato come:

```text
NE555
TDA7000
LM317T
ADC0804
```

invece di mostrare solo l’id generico del componente.

Per gli altri componenti usa:

```text
component_id
```

oppure, se manca:

```text
instance_id
```

---

## `short_terminal_label(terminal, metadata)`

**Scopo:** scegliere l’etichetta breve da mostrare sul nodo terminale.

### Priorità

Se è disponibile `terminal_metadata`, la funzione prova a usare:

1. `pin_label`;
2. `pin_number`, visualizzato come `pinN`;
3. `display_name`.

Se nessuno di questi campi è disponibile, usa:

```text
terminal.name
```

oppure:

```text
terminal.terminal_id
```

Questo è utile soprattutto per gli Integrated Circuit, perché permette di vedere nel grafo label come:

```text
VIN
VOUT
GND
FB
EN
pin3
pin7
```

---

## `wrap_label(value, max_len=14)`

**Scopo:** spezzare un’etichetta lunga su più righe.

### Perché serve

I nodi del grafo sono disegnati come cerchi. Se un testo è troppo lungo, uscirebbe dal nodo. Questa funzione prova a dividere il testo in massimo tre righe.

---

## `edge_color(key)`

**Scopo:** assegnare un colore stabile agli archi di una net.

### Logica

Calcola un indice sulla base dei caratteri della chiave e sceglie un colore da `EDGE_PALETTE`.

Questo permette a una net di avere sempre lo stesso colore durante il rendering della stessa immagine.

---

## `unique_preserve_order(values)`

**Scopo:** rimuovere duplicati mantenendo l’ordine originale.

### Perché serve

L’ordine dei terminali è importante per mantenere stabile il layout. Questa funzione evita duplicati senza riordinare artificialmente la lista.

---

## `path_sort_key(path)`

**Scopo:** ordinare i file JSON in modo naturale.

### Esempio

Con questa funzione:

```text
1.json
2.json
10.json
```

rimangono nell’ordine atteso.

---

## `build_terminal_index(data)`

**Scopo:** costruire indici rapidi sui componenti e sui terminali.

### Restituisce

```python
components, terminal_to_component, terminal_lookup
```

Dove:

- `components` è la lista dei componenti;
- `terminal_to_component` mappa ogni terminale al suo componente;
- `terminal_lookup` mappa ogni terminale al suo dizionario dati.

Questi indici sono usati in quasi tutte le fasi successive.

---

## `attach_unknown_terminals(...)`

**Scopo:** gestire terminali presenti nel grafo ma assenti nei componenti.

### Cosa fa

- scansiona sorgenti e destinazioni del grafo;
- trova terminali non presenti in `terminal_lookup`;
- crea per ognuno un componente fittizio `Unknown`.

### Perché serve

Permette al report di non fallire in presenza di incoerenze e rende visibile il problema nella vista completa.

---

## `build_adjacency(graph, terminal_ids)`

**Scopo:** trasformare il grafo del JSON in una lista di adiacenza non orientata.

### Cosa fa

Per ogni collegamento:

```text
source → destination
```

aggiunge sia:

```text
source → destination
```

sia:

```text
destination → source
```

### Perché serve

I collegamenti elettrici non sono direzionali. Per ricostruire le net tramite BFS serve una rappresentazione non orientata.

---

## `extract_graph_structures(data)`

**Scopo:** preparare tutte le strutture necessarie alla visualizzazione.

### Cosa produce

Un dizionario con:

- `graph`;
- `components`;
- `terminal_to_component`;
- `terminal_lookup`;
- `ordered_terminal_ids`;
- `class_order`;
- `net_groups`.

### Perché è una funzione centrale

Questa funzione separa la lettura del JSON dalla costruzione del modello grafico. Sia la vista completa sia quella compatta partono da queste strutture.

---

## `build_net_groups(adjacency, terminal_order)`

**Scopo:** trovare le net elettriche a partire dall’adiacenza del grafo.

### Logica

Usa una BFS:

1. prende un terminale non visitato;
2. visita tutti i terminali raggiungibili;
3. li raggruppa in una net;
4. passa al terminale successivo.

### Output

Una lista di dizionari:

```json
{
  "net_id": "net_1",
  "label": "1",
  "terminal_ids": ["A", "B", "C"]
}
```

---

## `build_visual_model(data)`

**Scopo:** costruire il modello dati della vista completa.

### Cosa contiene il modello

```python
{
    "image_id": ...,
    "image_name": ...,
    "width": ...,
    "height": ...,
    "nodes": [...],
    "edges": [...],
    "summary": {...},
    "warnings": {...}
}
```

### Nodi creati

- nodo root del circuito;
- nodi classe;
- nodi componente;
- nodi terminale;
- nodi net.

### Archi creati

- archi gerarchici root → classe;
- archi gerarchici classe → componente;
- archi gerarchici componente → terminale;
- archi elettrici terminale → net.

---

## `build_compact_visual_model(data)`

**Scopo:** costruire il modello dati della vista compatta.

### Differenza rispetto alla vista completa

Non crea nodi per classi e terminali. Crea solo:

- componenti;
- net.

### Cosa conserva comunque

Anche se i terminali non sono disegnati come nodi, non vengono persi. Sono riportati nei tooltip degli archi componente → net.

Questa scelta rende la visualizzazione più pulita senza perdere informazione.

---

## `compute_compact_component_positions(components)`

**Scopo:** calcolare la posizione verticale dei componenti nella vista compatta.

### Logica

Ogni componente riceve una coordinata `y`. La distanza tra componenti dipende dal numero di terminali:

- componenti semplici: distanza minore;
- componenti con tanti terminali: distanza maggiore.

---

## `compute_compact_net_positions(...)`

**Scopo:** calcolare la posizione verticale delle net nella vista compatta.

### Logica

Per ogni net viene calcolata la media delle posizioni verticali dei componenti collegati. Poi viene applicata una distanza minima tra net successive.

Questo rende le net più vicine ai componenti che collegano e riduce gli incroci visivi.

---

## `compute_positions(...)`

**Scopo:** calcolare le posizioni della vista completa.

### Logica

Usa un layout a livelli, con colonne fisse:

```text
root      x = 90
class     x = 270
component x = 500
terminal  x = 780
net       x = 1080
```

La coordinata `y` viene calcolata in modo da mantenere vicini:

- terminali dello stesso componente;
- componenti della stessa classe;
- net collegate agli stessi terminali.

---

## `resolve_node_style(node)`

**Scopo:** recuperare lo stile grafico di un nodo.

### Cosa usa

La costante globale `NODE_STYLE`, che definisce:

- colore di riempimento;
- colore bordo;
- raggio;
- dimensione font.

---

## `node_label_max_len(node_type)`

**Scopo:** decidere la lunghezza massima delle label dentro i nodi.

### Logica

- componenti: label un po’ più lunghe;
- classi: label medie;
- terminali e net: label più corte.

---

## `render_png(model, png_path)`

**Scopo:** generare il PNG statico del grafo.

### Cosa fa

- crea una figura Matplotlib;
- disegna prima gli archi;
- disegna poi i nodi;
- scrive le label dentro i nodi;
- salva il PNG.

### Nota importante

Il rendering usa `matplotlib.use("Agg")`, quindi funziona anche senza GUI.

---

## `svg_circle(node)`

**Scopo:** generare il codice SVG di un nodo.

### Cosa include

- cerchio colorato;
- label del nodo;
- tooltip tramite `<title>`.

---

## `build_svg(model)`

**Scopo:** generare l’SVG completo del grafo.

### Cosa fa

- genera tutte le linee degli archi;
- genera tutti i nodi;
- imposta il `viewBox` iniziale;
- salva le dimensioni complete come attributi `data-full-width` e `data-full-height`.

Il `viewBox` iniziale viene centrato intorno al nodo root, così aprendo la pagina non si parte necessariamente dall’estremo superiore del grafico.

---

## `build_summary_html(model)`

**Scopo:** generare le card numeriche di riepilogo.

### Campi mostrati

- componenti;
- terminali;
- nodi elettrici;
- isolati;
- unmatched;
- suspicious.

---

## `build_warning_html(warnings)`

**Scopo:** generare la sezione warning della pagina HTML.

### Warning gestiti

- `unconnected_terminals`;
- `unmatched_terminals`;
- `suspicious_matches`.

---

## `build_graph_page(...)`

**Scopo:** generare la pagina HTML della vista completa.

### Contenuto della pagina

- titolo del circuito;
- link alla vista compatta;
- link al JSON;
- link al PNG;
- link all’indice batch;
- riepilogo numerico;
- immagine del circuito;
- grafo interattivo;
- legenda;
- warning;
- JSON completo in un blocco espandibile.

### Interattività

La pagina include JavaScript locale per:

- zoom con rotella del mouse;
- pan con trascinamento;
- navigazione del `viewBox` SVG.

---

## `build_compact_graph_page(...)`

**Scopo:** generare la pagina HTML della vista compatta.

### Differenze rispetto alla vista completa

La pagina compatta include anche tre box esplicativi:

1. cosa si sta guardando;
2. come si legge il grafo;
3. perché si usano le net invece dei soli collegamenti componente-componente.

Questa vista è pensata per essere più leggibile e più adatta alla consultazione rapida.

---

## `build_index_page(items, output_dir)`

**Scopo:** generare la pagina indice del batch.

### Cosa riceve

Una lista di `items`, uno per circuito elaborato.

### Cosa mostra

Per ogni circuito:

- miniatura;
- id;
- conteggio componenti, terminali e net;
- warning principali;
- link ai file prodotti.

---

## `relative_href(source_dir, target_path)`

**Scopo:** generare link relativi tra file HTML.

### Perché serve

Il report deve funzionare anche se la cartella viene spostata o copiata altrove. Usare percorsi relativi rende il report portabile.

---

## `copy_circuit_image(image_path, destination)`

**Scopo:** copiare l’immagine del circuito dentro la cartella del report.

### Cosa fa

- controlla che l’immagine esista;
- crea la cartella di destinazione;
- copia il file mantenendo i metadati con `shutil.copy2`.

---

## `resolve_image_path(detect_dir, stem)`

**Scopo:** trovare l’immagine da mostrare nel report.

### Ordine di ricerca

1. JSON del passo 01:

```text
01_detect_components/<stem>.json
```

Se esiste, legge `image_path` e usa l’immagine originale.

2. Immagine debug del passo 01:

```text
01_detect_components/debug_images/<stem>_detect.jpg
```

3. Overlay terminali del passo 05:

```text
05_build_terminal_graph/debug_terminal_overlay/<stem>_terminal_overlay.jpg
```

Se nessuna immagine viene trovata, la pagina HTML mostra un box “Immagine non trovata”.

---

## `render_one_json(json_path, detect_dir, output_dir)`

**Scopo:** elaborare un singolo circuito.

### Sequenza operativa

1. carica il JSON del passo 05;
2. costruisce il modello completo;
3. costruisce il modello compatto;
4. crea la cartella del circuito;
5. copia il JSON;
6. cerca e copia l’immagine del circuito;
7. genera `graph_compact.png`;
8. genera `graph_compact.html`;
9. genera `graph.png`;
10. genera `graph.html`;
11. restituisce i path e il riepilogo per l’indice batch.

Questa è la funzione che orchestra l’intera produzione dei file per un singolo JSON.

---

## `main()`

**Scopo:** punto di ingresso dello script.

### Cosa fa

- legge gli argomenti CLI;
- controlla che la cartella input esista;
- crea la cartella output;
- trova tutti i JSON;
- esegue `render_one_json` su ogni file;
- raccoglie i risultati;
- genera `index.html`;
- stampa a terminale un riepilogo dell’esecuzione.

---

# Modello dati interno

Il passo 06 usa un modello grafico intermedio indipendente dal JSON originale.

Ogni modello ha questa forma:

```python
{
    "image_id": "...",
    "image_name": "...",
    "width": 1260,
    "height": 820,
    "nodes": [...],
    "edges": [...],
    "summary": {...},
    "warnings": {...}
}
```

## Nodo

Un nodo è rappresentato così:

```python
{
    "id": "resistor22.1",
    "type": "component",
    "label": "resistor22.1",
    "tooltip": "...",
    "x": 500,
    "y": 120
}
```

## Arco

Un arco è rappresentato così:

```python
{
    "source": "resistor22.1_t1",
    "target": "net_3",
    "kind": "net",
    "color": "#7fb3d5",
    "tooltip": "..."
}
```

Gli archi possono essere di due tipi:

| Tipo arco | Significato |
|---|---|
| `hierarchy` | relazione informativa, per esempio componente → terminale |
| `net` | relazione elettrica terminale → net oppure componente → net |

---

# Come leggere il report

## Vista completa

La vista completa si legge da sinistra verso destra:

```text
circuito → classi → componenti → terminali → nodi elettrici
```

Questa vista è adatta per capire come il JSON è stato strutturato.

Esempio:

```text
Circuito
  → Integrated Circuit
    → NE555
      → pin3
        → net_5
```

significa che il terminale mostrato come `pin3` del componente `NE555` appartiene alla `net_5`.

## Vista compatta

La vista compatta si legge così:

```text
componente → net ← componente
```

Se due componenti sono collegati alla stessa net, allora condividono un nodo elettrico.

Esempio:

```text
R1 → net_2 ← NE555
```

significa che un terminale di `R1` e un terminale del `NE555` sono collegati allo stesso nodo.

Passando con il mouse sull’arco si vede quali terminali precisi del componente appartengono a quella net.

---

# Differenza tra grafo del passo 05 e report del passo 06

Il passo 05 produce un grafo terminale-terminale:

```json
{
  "A": ["B", "C"],
  "B": ["A", "C"],
  "C": ["A", "B"]
}
```

Il passo 06 lo visualizza come net esplicita:

```text
A ─┐
B ─┼── net_1
C ─┘
```

Quindi le net del passo 06 sono una rappresentazione grafica derivata. Non sono una nuova analisi elettrica e non sostituiscono il JSON del passo 05.

---

# Informazioni sugli Integrated Circuit

Lo script è predisposto per mostrare in modo leggibile le informazioni aggiunte agli Integrated Circuit nei passi precedenti.

Per i componenti IC, la label del nodo componente usa preferibilmente:

```text
ic_marking
```

Quindi un componente può comparire come:

```text
NE555
TDA7000
LM317T
TPS63061
```

Per i terminali IC, se `terminal_metadata` contiene informazioni sui pin, la vista può mostrare:

```text
VIN
GND
FB
pin3
pin7
```

Questa informazione è solo descrittiva nel report. Il passo 06 non consulta datasheet e non interpreta la funzione elettrica dei pin.

---

# Cosa lo script non fa

È importante chiarire i limiti del passo 06.

Lo script:

- non esegue object detection;
- non stima terminali;
- non esegue OCR;
- non skeletonizza fili;
- non corregge il grafo;
- non aggiunge collegamenti;
- non rimuove collegamenti;
- non interpreta datasheet;
- non fa diagnosi elettrica.

Lo script prende il risultato del passo 05 e lo trasforma in un report visuale.

---

# Utilità per la pipeline e per la tesi

Questo passo è utile per due motivi principali.

## 1. Debug della pipeline

Permette di verificare rapidamente:

- se i terminali sono stati collegati alla net corretta;
- se ci sono terminali isolati;
- se ci sono terminali unmatched;
- se componenti complessi come IC, display, opamp, trasformatori o connettori sono rappresentati correttamente;
- se il grafo è troppo frammentato;
- se qualche collegamento speciale del passo 05 ha prodotto un effetto inatteso.

## 2. Documentazione del processo

Il report crea un ponte tra il JSON tecnico e la comprensione visiva. Per la tesi è utile perché mostra chiaramente la trasformazione:

```text
schema elettrico → componenti/terminali → grafo topologico → report visuale
```

La vista compatta, in particolare, rende esplicito il concetto di nodo elettrico, che è fondamentale per spiegare come il circuito viene trasformato in una struttura dati utilizzabile da un agente AI.

---

# Sintesi finale

Lo script `06_render_graph_report.py` è un generatore di report per il grafo topologico prodotto dal passo 05.

La sua funzione principale è trasformare un JSON tecnico in un insieme di file facilmente consultabili:

```text
index.html
schema/graph_compact.html
schema/graph_compact.png
schema/graph.html
schema/graph.png
schema/schema.json
```

La vista completa serve al debug dettagliato della gerarchia circuito-classe-componente-terminale-net. La vista compatta serve alla lettura topologica componente-net, più vicina al modo in cui si interpreta elettricamente un circuito.

Il passo 06 non cambia la topologia: la rende leggibile, navigabile e documentabile.
