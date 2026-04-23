
# Script 05 — `05_build_terminal_graph.py`

## Scopo del passo 05

Questo script è il passo della pipeline che trasforma:

- i **terminali semantici** stimati dal passo **03**
- lo **skeleton dei fili** estratto dal passo **04**

in un **JSON canonico del circuito**, pensato per essere semplice da leggere sia da un umano sia da un’AI.

L’idea centrale è questa:

1. ogni terminale viene **agganciato al filo più vicino** nello skeleton;
2. i terminali che cadono sulla **stessa connected component** dello skeleton vengono considerati sullo **stesso nodo elettrico**;
3. da questi gruppi viene costruito il grafo finale:

```json
{
  "resistor22.1_t1": ["capacitor4.1_t1", "diode7.1_anode"],
  "capacitor4.1_t1": ["resistor22.1_t1", "diode7.1_anode"]
}
```

Lo script **non salva net / net_id / net_index** nel JSON finale: usa le connected components solo come struttura tecnica interna.

---

## Filosofia generale del file

Il passo 05 ha due anime:

### 1. Parte geometrica
Lavora sullo skeleton dei fili:
- pulisce i corpi dei componenti;
- calcola le connected components;
- assegna ogni terminale a una label di filo.

### 2. Parte euristica
Corregge gli errori tipici dei diagrammi reali:
- fili spezzati da simboli complessi;
- crossing senza giunzione;
- ponticelli;
- gate MOSFET spezzate;
- basi BJT spezzate;
- terminali aux degli opamp che cadono dentro il simbolo;
- supply arrow tipo `VDD` e `VSS`.

Questa seconda parte è fondamentale: senza di essa lo skeleton grezzo spesso produrrebbe nodi sbagliati.

---

# Procedimento completo del passo 05

## 1. Caricamento dati
Per ogni immagine lo script legge il JSON del passo 04, che contiene:
- lista dei componenti;
- lista dei terminali;
- path dello skeleton;
- metadati dell’immagine.

Il punto di ingresso logico è:

- `build_terminal_graph_for_image(data)`

e il punto di ingresso eseguibile del file è:

- `main()`

---

## 2. Pulizia dello skeleton
Lo skeleton estratto dal 04 può contenere ancora pixel del **corpo dei componenti**.

Esempio classico:
- lo zig-zag del resistore;
- il corpo del condensatore;
- il simbolo del fusibile.

Se questi pixel non vengono rimossi, i due terminali del componente rischiano di finire nella **stessa connected component**, creando un falso corto.

Per questo il file:
- identifica i componenti a due terminali;
- cancella l’interno del loro bbox;
- lascia vivi solo gli stub vicino ai terminali.

Risultato: il corpo del componente **non viene trattato come filo**.

---

## 3. Connected components dello skeleton
Dopo la pulizia, lo script applica:

- `cv2.connectedComponentsWithStats(...)`

Ogni label positiva risultante rappresenta un **pezzo di filo connesso**.

Queste label non vengono salvate come output, ma diventano la base di tutta la costruzione del grafo.

---

## 4. Match terminale → label di filo
Per ogni terminale il file cerca un pixel di skeleton vicino.

La logica è a due livelli:

### 4.1 Finestra direzionale
Usa `relative_position` del terminale:
- se il terminale è a sinistra, cerca soprattutto a sinistra;
- se è a destra, cerca a destra;
- se è in alto, cerca verso l’alto;
- se è in basso, cerca verso il basso.

Questo riduce i match sbagliati verso fili non pertinenti.

### 4.2 Fallback quadrato
Se la ricerca direzionale non trova nulla, usa una finestra quadrata piccola attorno al terminale.

### 4.3 Esito
Per ogni terminale viene salvato:
- `matched_label`
- `candidate_labels`
- `snap_point`
- `snap_distance`
- `match_mode`
- `is_suspicious`

Se non trova nulla:
- il terminale resta `unmatched`.

---

## 5. Costruzione dei gruppi `label -> terminali`
Dopo il match, lo script trasforma il risultato in una struttura interna del tipo:

```python
{
    12: ["termA", "termB", "termC"],
    31: ["termD", "termE"]
}
```

Questa mappa significa:

- la label 12 contiene i terminali A, B, C;
- quindi A, B e C insistono sullo stesso tratto di filo;
- quindi devono diventare un nodo implicito del grafo finale.

---

## 6. Correzioni euristiche
Qui entra in gioco la parte più importante del file.

Lo skeleton e i bbox dei componenti non bastano quasi mai da soli. Per questo lo script applica una sequenza di fusioni e split mirati.

### 6.1 Fusioni
Vengono fuse label separate che in realtà dovrebbero essere lo stesso nodo:
- basi BJT allineate;
- gate MOSFET allineate;
- aux di opamp e terminali esterni;
- piccoli stub orizzontali;
- alcuni rami paralleli degli induttori;
- rail tra batteria e gate;
- rail di gate MOSFET.

### 6.2 Split
Vengono separate label che non devono essere lo stesso nodo:
- ponticelli;
- crossing senza pallino;
- pseudo-corti causati dal simbolo del componente;
- self-match interni a transformer o connector.

---

## 7. Costruzione del grafo finale
Una volta stabiliti i gruppi finali:

- se una label contiene almeno 2 terminali,
- ogni terminale viene collegato a tutti gli altri terminali della stessa label.

Quindi un gruppo:

```python
["A", "B", "C"]
```

diventa:

```python
A -> [B, C]
B -> [A, C]
C -> [A, B]
```

Questo è il motivo per cui nel JSON finale **non compaiono i nodi espliciti**:
il nodo è rappresentato implicitamente dalla clique dei terminali.

---

## 8. Collegamenti speciali extra
Dopo il grafo base lo script aggiunge:

- alcuni collegamenti diretti per rami paralleli verticali con induttori;
- collegamenti verso nodi simbolici come `VDD` e `VSS`, se riconosce una supply arrow.

---

## 9. Costruzione del JSON finale
Infine il file esporta:

- `image_id`
- `image_name`
- `components`
- `graph`
- `warnings`

Quindi il risultato finale è minimale e leggibile.

---

# Struttura del file, sezione per sezione

## Sezione: PATH / INPUT-OUTPUT

Questa sezione definisce:
- root del progetto;
- dataset di pipeline da usare;
- cartella input del 04;
- cartella output del 05;
- cartelle per le immagini di debug.

### Variabili principali
- `PROJECT_ROOT`
- `PIPELINE_DATASET`
- `INPUT_DIR`
- `OUTPUT_DIR`
- `DEBUG_TERMINAL_OVERLAY_DIR`
- `DEBUG_SKELETON_OVERLAY_DIR`

Il loro ruolo è puramente organizzativo.

---

## Sezione: costanti di match terminale → filo

Queste costanti controllano quanto grande è la finestra di ricerca intorno al terminale.

### `TERMINAL_SEARCH_OUTWARD`
Quanto lo script cerca **verso l’esterno** del componente.

### `TERMINAL_SEARCH_INWARD`
Quanto lo script cerca anche **verso l’interno**, per tollerare piccoli errori di localizzazione.

### `TERMINAL_DIRECTIONAL_HALFSPAN`
Semiampiezza trasversale della finestra direzionale.

### `TERMINAL_SQUARE_FALLBACK_RADIUS`
Raggio del fallback quadrato.

### `MAX_REASONABLE_SNAP_DISTANCE`
Se il pixel trovato è troppo lontano dal terminale, il match è marcato come sospetto.

### `ANALOG_METER_FALLBACK_RADIUS`
### `ANALOG_METER_MAX_SNAP_DISTANCE`
Parametri speciali per l’analog meter, perché i post del simbolo possono stare molto dentro il componente.

### `NON_SHORTING_MULTI_TERMINAL_CLASSES`
Classi multi-terminale che **non devono essere cortocircuitate** internamente:
- `connector`
- `transformer`

---

## Sezione: euristiche speciali

Queste costanti governano le varie fusioni/split:
- basi BJT;
- gate MOSFET;
- aux opamp;
- rami paralleli degli induttori;
- frecce di alimentazione;
- cancellazione dei corpi dei componenti;
- ponticelli;
- crossing senza dot.

Sono soglie geometriche:
- tolleranze in x/y;
- gap massimi;
- raggi di taglio;
- run minimi.

Non producono output da sole, ma controllano il comportamento delle funzioni euristiche.

---

## Sezione: debug visivo

Questa sezione contiene:
- flag per salvare immagini di debug;
- font e dimensioni del testo;
- colori di terminali, snap point e link.

Serve solo per rendere leggibili gli overlay finali.

---

# Spiegazione dettagliata di ogni funzione

# 1. Utility base

## `load_binary_image(path: Path) -> np.ndarray`
**Scopo:** caricare da disco un’immagine binaria.

### Cosa fa
- legge l’immagine in grayscale;
- controlla che esista;
- normalizza tutto a `0/255`.

### Perché serve
Garantisce che tutte le immagini binarie usate nel 05 abbiano una codifica coerente.

---

## `clamp_window(x1, y1, x2, y2, w, h)`
**Scopo:** limitare una finestra ai bordi dell’immagine.

### Cosa fa
Taglia le coordinate della finestra in modo che restino sempre dentro:
- larghezza `w`
- altezza `h`

### Perché serve
Evita index error quando una ricerca cade vicino ai bordi.

---

## `draw_outlined_text(...)`
**Scopo:** disegnare testo con bordo.

### Cosa fa
- prima disegna il testo in outline;
- poi lo ridisegna nel colore finale.

### Perché serve
Rende leggibili le label sugli overlay anche quando lo sfondo è complesso.

---

## `normalize_class_name(class_name: str) -> str`
**Scopo:** normalizzare il nome classe.

### Cosa fa
- converte in lowercase;
- sostituisce gli spazi con underscore.

### Esempio
`"Voltage Source"` → `"voltage_source"`

### Perché serve
Permette confronti coerenti tra classi.

---

## `make_simple_component_id(instance_id: str, class_name: str) -> str`
**Scopo:** costruire un id umano semplice per il componente.

### Esempio
`Mosfet + 16.2` → `mosfet16.2`

### Perché serve
È l’id usato nel JSON finale.

---

## `normalize_public_terminal_id(value: str) -> str`
**Scopo:** normalizzare un id pubblico di terminale.

### Esempio
`16.2:G` → `16.2_G`

### Nota
Mantiene le maiuscole di terminali come:
- `G`
- `S`
- `D`
- `B`
- `C`
- `E`

### Perché serve
Non vuole perdere informazione semantica.

---

## `get_preferred_terminal_public_id(term: dict) -> str`
**Scopo:** scegliere il miglior id pubblico disponibile per un terminale.

### Ordine di priorità
- `display_terminal_id`
- `semantic_terminal_id`
- `terminal_id`
- fallback costruito con `instance_id:name`

### Perché serve
Recupera il nome più semantico possibile dal passo 03.

---

## `get_preferred_terminal_public_name(term: dict) -> str`
**Scopo:** scegliere il miglior nome corto del terminale.

### Priorità
- `display_name`
- `semantic_terminal_name`
- `name`
- fallback `"t"`

### Perché serve
Serve nella parte finale del JSON canonico.

---

## `make_simple_terminal_key(term: dict) -> str`
**Scopo:** costruire la chiave umana del terminale.

### Esempi
- `mosfet16.2_G`
- `battery2.1_positive`
- `resistor22.1_t1`

### Perché serve
È la chiave del grafo finale.

---

# 2. Pulizia dello skeleton dentro i componenti

## `should_erase_component_body_from_skeleton(component: dict)`
**Scopo:** decidere se cancellare il corpo del componente dallo skeleton.

### Regola
- non cancella `terminal`, `gnd`, `ground`;
- cancella solo componenti con **esattamente 2 terminali**.

### Perché serve
I due terminali di un due-terminali non devono risultare cortocircuitati dal corpo del simbolo.

---

## `erase_component_bodies_from_skeleton(skeleton_binary, components)`
**Scopo:** cancellare i corpi dei componenti a due terminali dallo skeleton.

### Cosa fa
Per ogni componente eleggibile:
- prende il bbox;
- applica un piccolo padding interno;
- azzera i pixel interni.

### Perché serve
Rompe i falsi “mega nodi” generati dal simbolo del componente.

---

# 3. Geometria di ricerca attorno al terminale

## `get_directional_window(term, labels_shape, outward=16, inward=4, halfspan=5)`
**Scopo:** costruire una finestra di ricerca direzionale.

### Logica
Usa `relative_position`:
- `left`
- `right`
- `top`
- `bottom`

### Perché serve
Un terminale dovrebbe cercare il filo soprattutto dal proprio lato di uscita.

---

## `get_square_window(term, labels_shape, radius=12)`
**Scopo:** costruire una finestra quadrata centrata sul terminale.

### Perché serve
È il fallback semplice se la ricerca direzionale non trova nulla.

---

# 4. Lettura delle label dentro una finestra

## `collect_labels_in_window(labels: np.ndarray, window)`
**Scopo:** raccogliere le label positive presenti in una finestra.

### Cosa restituisce
La lista delle label > 0 trovate nella ROI.

### Perché serve
Aiuta a sapere quali candidati di filo esistono vicino al terminale.

---

## `find_nearest_labeled_pixel(labels: np.ndarray, term: dict, window)`
**Scopo:** trovare il pixel etichettato più vicino al terminale in una finestra.

### Restituisce
- label del pixel;
- snap point;
- distanza.

### Perché serve
È la base del match terminale → filo.

---

# 5. Match di un singolo terminale

## `match_terminal_to_skeleton_label(labels: np.ndarray, term: dict)`
**Scopo:** agganciare un singolo terminale a una label di skeleton.

### Procedura
1. prova finestra direzionale;
2. se non trova nulla, prova finestra quadrata;
3. se non trova nulla neanche lì, terminale unmatched.

### Restituisce
Un dizionario di debug con:
- `matched_label`
- `match_mode`
- `search_window`
- `snap_point`
- `snap_distance`
- `is_suspicious`

### Perché serve
È la funzione base di tutto il 05.

---

## `attach_unmatched_analog_meter_terminals(components, terminal_match_debug, labels)`
**Scopo:** recuperare terminali di analog meter rimasti unmatched.

### Logica
Per gli `analog_meter` usa una finestra molto più grande.

### Perché serve
I post del meter possono trovarsi lontani dai veri fili o dentro il simbolo.

---

# 6. Costruzione dei gruppi interni di filo

## `build_label_to_terminal_ids(match_debug_by_terminal_id: dict)`
**Scopo:** costruire la mappa interna `label -> [terminal_ids]`.

### Cosa fa
- legge `matched_label` di ogni terminale;
- raggruppa i terminali per label;
- deduplica e ordina.

### Perché serve
È la rappresentazione interna dei nodi elettrici grezzi.

---

# 7. Fusione label spezzate da simboli BJT

## `is_bjt_base_terminal(term: dict)`
**Scopo:** dire se un terminale è una base di BJT.

### Regola
- classe contiene `transistor`
- nome del terminale = `B`

---

## `build_component_bbox_by_instance(components: list[dict])`
**Scopo:** costruire una mappa `instance_id -> bbox`.

### Perché serve
Molte euristiche confrontano distanze tra componenti.

---

## `horizontal_bbox_gap(bbox_a, bbox_b)`
**Scopo:** calcolare il gap orizzontale tra due bbox.

### Perché serve
Serve per capire se due componenti sono abbastanza vicini da essere probabilmente sullo stesso filo.

---

## `min_label_distance(labels: np.ndarray, label_a: int, label_b: int)`
**Scopo:** calcolare la distanza minima reale tra due label di skeleton.

### Perché serve
Evita di fondere pezzi di filo troppo lontani.

---

## `merge_bjt_base_aligned_labels(...)`
**Scopo:** fondere label spezzate che in realtà rappresentano la stessa linea di base di BJT.

### Criteri
- entrambe le terminali sono basi;
- y simile;
- bbox vicine;
- distanza minima tra label sotto soglia.

### Perché serve
La linea di base può venire spezzata dalla maschera del transistor.

---

# 8. Fusione label spezzate tra gate MOSFET

## `is_mosfet_gate_terminal(term: dict)`
**Scopo:** dire se un terminale è una gate di MOSFET.

---

## `is_mosfet_terminal(term: dict)`
**Scopo:** dire se un terminale appartiene a un MOSFET.

---

## `is_battery_terminal(term: dict)`
**Scopo:** dire se un terminale appartiene a una batteria.

---

## `merge_mosfet_gate_aligned_labels(...)`
**Scopo:** fondere label spezzate che rappresentano la stessa rete di gate di MOSFET.

### Criteri
- label composte solo da gate MOSFET;
- gate quasi allineate;
- bbox vicine;
- distanza tra label piccola.

### Perché serve
Nei mirror o nei differenziali il filo di gate passa spesso vicino ai simboli e si spezza.

---

# 9. Match virtuale aux opamp → terminale esterno

## `is_opamp_aux_terminal(term: dict)`
**Scopo:** riconoscere `aux1`, `aux2`, ecc. di un opamp.

---

## `is_external_terminal_component(term: dict)`
**Scopo:** riconoscere i componenti `Terminal`.

---

## `is_terminal_in_aux_direction(aux_term: dict, candidate_term: dict)`
**Scopo:** verificare se un terminale esterno sta nella direzione giusta rispetto a un aux.

### Esempio
Se l’aux è `top`, il terminale deve stare sopra.

---

## `attach_unmatched_opamp_aux_to_external_terminals(terminals, terminal_match_debug)`
**Scopo:** dare un match virtuale a un aux opamp unmatched, se esiste un terminale esterno molto allineato.

### Perché serve
Gli aux possono cadere dentro il triangolo dell’opamp e perdere lo skeleton reale.

---

## `collect_opamp_aux_external_terminal_pairs(terminals, terminal_match_debug)`
**Scopo:** raccogliere le coppie plausibili `aux opamp ↔ terminale esterno`.

---

## `merge_opamp_aux_external_terminal_labels(...)`
**Scopo:** fondere le label degli aux opamp con quelle dei terminali esterni allineati.

### Perché serve
Ricuce il collegamento VCC/VEE degli opamp anche quando il filo è stato mascherato.

---

# 10. Fusione di piccoli stub orizzontali

## `merge_near_horizontal_stub_labels(...)`
**Scopo:** fondere piccoli stub orizzontali vicini a una label principale.

### Casi tipici
- diode
- led

### Perché serve
Piccoli segmenti laterali possono rimanere separati anche se sono parte dello stesso nodo.

---

# 11. Rami paralleli verticali con induttori

## `merge_vertical_inductor_parallel_branch_labels(...)`
**Scopo:** fondere label di rami paralleli legati a induttori verticali.

### Logica
Se un terminale di induttore verticale è vicino a:
- antenna;
- condensatore positivo/negativo;
- ground;

e la distanza tra label è piccola, le label possono essere fuse.

### Perché serve
Serve per casi tipo antenna–bobina–capacitore o rami paralleli di filtro.

---

## `build_vertical_inductor_parallel_direct_edges(...)`
**Scopo:** aggiungere collegamenti diretti per alcuni casi di rami paralleli verticali con induttori.

### Differenza rispetto alla funzione precedente
Qui non fonde label: aggiunge direttamente archi al grafo finale.

### Perché serve
In certi casi la fusione totale sarebbe troppo aggressiva, ma un edge diretto è utile.

---

# 12. Fusione di rail tra batteria e gate

## `merge_battery_gate_rail_groups(label_to_terminal_ids, terminals)`
**Scopo:** fondere gruppi di sola batteria con gruppi di sole gate MOSFET quando sono allineati verticalmente.

### Perché serve
Nei circuiti reali le rail di polarizzazione possono risultare spezzate ma semantica e allineamento suggeriscono che siano la stessa rete.

---

## `merge_mosfet_gate_rail_groups(label_to_terminal_ids, terminals, components)`
**Scopo:** fondere tra loro gruppi composti solo da terminali di MOSFET, se rappresentano la stessa rail di gate.

### Perché serve
Ricuce rail di gate spezzate in più tronconi.

---

# 13. Split label in corrispondenza dei ponti

## `count_run(binary, x, y, dx, dy, limit)`
**Scopo:** contare quanti pixel attivi ci sono lungo una direzione.

### Perché serve
È una utility per capire se esistono davvero segmenti di filo sufficientemente lunghi nelle quattro direzioni.

---

## `has_bridge_hump(binary, x, y)`
**Scopo:** verificare la presenza della “gobba” tipica del ponticello.

### Perché serve
Un ponte grafico indica due fili che si incrociano senza connettersi.

---

## `detect_wire_bridges(skeleton_binary, labels)`
**Scopo:** rilevare ponticelli sullo skeleton.

### Logica
Cerca punti con:
- continuità a sinistra, destra, sopra, sotto;
- presenza di hump;
- label valida.

### Perché serve
Permette di tagliare un’unica connected component in due reti separate.

---

## `load_junction_support_binary(wire_extraction: dict)`
**Scopo:** caricare una maschera più piena del solo skeleton, se disponibile.

### Perché serve
Aiuta a distinguere:
- crossing senza giunzione
- crossing con pallino vero

---

## `has_filled_junction_dot(junction_binary, x, y)`
**Scopo:** verificare se esiste un pallino pieno di giunzione vicino a un crossing.

### Perché serve
Se c’è il pallino, il crossing rappresenta un nodo reale e non va spezzato.

---

## `detect_plain_wire_crossings(skeleton_binary, labels, junction_binary)`
**Scopo:** rilevare crossing ortogonali senza pallino.

### Perché serve
Lo skeleton li vede come croci connesse, ma elettricamente devono restare separati.

---

## `labels_with_multi_terminal_self_short(terminals, terminal_match_debug)`
**Scopo:** trovare label che contengono due o più terminali dello stesso componente.

### Perché serve
Sono candidati tipici a self-short o errori da corpo del componente.

---

## `nearest_split_label(split_labels, x, y, radius=6)`
**Scopo:** dopo uno split, trovare la nuova label più vicina a un certo punto.

### Perché serve
Serve per riassociare i terminali alle nuove connected components dopo il taglio.

---

## `split_bridge_labels(...)`
**Scopo:** funzione principale che esegue gli split dovuti a ponti e crossing senza dot.

### Cosa fa
1. rileva ponti;
2. rileva crossing da spezzare;
3. taglia localmente lo skeleton;
4. ricalcola le connected components;
5. riaggancia i terminali alle nuove label;
6. ricostruisce i gruppi finali.

### Perché serve
È una delle funzioni più importanti del 05 perché evita fusioni topologiche sbagliate.

---

# 14. Rimozione dei self-match non validi

## `remove_non_shorting_component_self_matches(label_to_terminal_ids, terminals, terminal_match_debug)`
**Scopo:** eliminare gruppi in cui più terminali dello stesso `connector` o `transformer` sono finiti sulla stessa label.

### Perché serve
Connettori e trasformatori non devono essere cortocircuitati internamente dal 05.

### Effetto
I terminali di quel gruppo vengono rimessi come unmatched.

---

# 15. Costruzione del grafo finale

## `build_terminal_graph(terminals, label_to_terminal_ids)`
**Scopo:** costruire il grafo interno terminale → terminali collegati.

### Logica
Per ogni label:
- prende i terminali del gruppo;
- crea una clique completa tra loro.

### Perché serve
Trasforma i nodi impliciti in archi espliciti tra terminali.

---

## `label_bbox(labels: np.ndarray, label: int)`
**Scopo:** calcolare il bbox di una label di skeleton.

### Perché serve
Usata in varie euristiche, soprattutto per supply arrows.

---

# 16. Conversione a id semplici

## `build_simple_id_map(terminals: list[dict])`
**Scopo:** costruire la mappa da `terminal_id` interno a id semplice umano.

---

## `build_simple_terminal_graph(terminal_graph: dict, original_to_simple: dict)`
**Scopo:** convertire il grafo interno in forma canonica leggibile.

### Esempio
`18.2:G` interno → `mosfet16.2_G`

---

## `build_simple_list(values: list[str], original_to_simple: dict)`
**Scopo:** convertire liste di id interni in liste di id semplici.

### Perché serve
Usata soprattutto nei warning.

---

# 17. Supply arrows

## `infer_supply_arrow_connection_for_terminal(term, label_box, image_height)`
**Scopo:** inferire se un terminale singolo su uno stub verticale rappresenta una rail simbolica.

### Possibili esiti
- `VDD`
- `VSS`

### Criteri
- altezza minima dello stub;
- larghezza ridotta;
- coerenza con `relative_position`;
- posizione rispetto ai bordi alto/basso dell’immagine;
- classe sorgente compatibile.

### Perché serve
Permette di creare nodi simbolici anche se il disegno non ha un componente esplicito.

---

## `build_supply_graph_links(...)`
**Scopo:** costruire gli archi terminale ↔ `VDD` / `VSS`.

### Cosa fa
Per ogni gruppo con un solo terminale:
- prova a capire se è una supply arrow;
- se sì, crea il link nel grafo finale.

---

# 18. Costruzione dei componenti canonici

## `build_canonical_components(components: list[dict])`
**Scopo:** creare la vista semplificata dei componenti da salvare nel JSON.

### Tiene solo
- `component_id`
- `instance_id`
- `class_name`
- `terminals` con:
  - `terminal_id`
  - `name`
  - `relative_position`

### Mantiene anche
- `state`
- `state_confidence`
per componenti come gli switch.

### Perché serve
Produce un JSON finale pulito e minimale.

---

# 19. Debug visivo

## `get_terminal_debug_color(match_info: dict)`
**Scopo:** scegliere il colore del terminale nel debug:
- verde = matched;
- rosso = unmatched;
- arancione = suspicious.

---

## `draw_terminal_overlay(image_bgr, terminals, terminal_match_debug, original_to_simple)`
**Scopo:** disegnare overlay sull’immagine originale.

### Disegna
- terminale;
- snap point;
- linea terminale → snap;
- label testuale.

---

## `draw_skeleton_overlay(skeleton_binary, terminals, terminal_match_debug, original_to_simple)`
**Scopo:** disegnare overlay sullo skeleton.

### Perché serve
È utile per vedere se il match cade davvero sul filo.

---

# 20. Funzione principale su una singola immagine

## `build_terminal_graph_for_image(data: dict)`
Questa è la **funzione centrale del file**.

### Sequenza completa
1. prende terminali, componenti e wire extraction dal JSON;
2. carica lo skeleton;
3. cancella i corpi dei componenti a due terminali;
4. calcola le connected components;
5. fa il match di tutti i terminali;
6. applica fallback analog meter;
7. applica fallback opamp aux;
8. costruisce `label_to_terminal_ids`;
9. applica tutte le fusioni euristiche;
10. applica gli split per ponti/crossing;
11. fonde rail MOSFET/battery dove serve;
12. rimuove self-short non validi;
13. costruisce il grafo finale;
14. aggiunge direct edges per induttori;
15. aggiunge `VDD` / `VSS`;
16. costruisce warning;
17. costruisce componenti canonici;
18. restituisce tutto il necessario per export e debug.

### Output
Restituisce un dizionario con:
- `components`
- `graph`
- `warnings`
- `skeleton_binary`
- `terminal_match_debug`
- `simple_id_map`

---

# 21. Entry point globale

## `main() -> None`
**Scopo:** eseguire il passo 05 su tutte le immagini della cartella input.

### Cosa fa
Per ogni JSON del passo 04:
1. carica i dati;
2. chiama `build_terminal_graph_for_image(...)`;
3. salva gli overlay di debug;
4. salva il JSON canonico finale;
5. stampa un riepilogo su terminale.

### Output finale
Ogni file JSON salvato contiene:
- `image_id`
- `image_name`
- `components`
- `graph`
- `warnings`

---

# Come nascono concretamente i collegamenti

## Esempio concettuale
Supponiamo che dopo il match succeda questo:

```python
label 17 -> [
    "resistor22.1_t1",
    "capacitor4.1_t1",
    "diode7.1_anode"
]
```

Allora il 05 costruisce:

```python
resistor22.1_t1 -> [capacitor4.1_t1, diode7.1_anode]
capacitor4.1_t1 -> [resistor22.1_t1, diode7.1_anode]
diode7.1_anode -> [resistor22.1_t1, capacitor4.1_t1]
```

Quindi:

- **non salva la label 17**
- ma usa la label 17 per creare il nodo implicito del grafo.

---

# Lettura corretta del `graph`

Una riga del tipo:

```json
"npn_transistor18.1_B": ["resistor22.1_t1", "polarized_capacitor20.2_negative"]
```

vuol dire:

- la base del transistor,
- il terminale superiore di `R1`,
- e il terminale negativo del condensatore `C2`

stanno sullo **stesso nodo di filo**.

Non vuol dire:
- che sono collegamenti interni del componente;
- né che il transistor collega internamente quei terminali.

Vuol dire solo:
- **nodo esterno comune nello skeleton finale**.

---

# Significato dei warning

## `unconnected_terminals`
Terminali presenti nel grafo ma senza vicini.

### Possibili cause
- filo realmente assente;
- crop dell’immagine;
- rail simbolica non modellata;
- fallimento del match;
- componente fuori specifica.

---

## `unmatched_terminals`
Terminali per cui il 05 non è riuscito ad assegnare alcuna `matched_label`.

### Possibili cause
- nessun pixel di skeleton vicino;
- terminale caduto dentro il simbolo;
- mascheratura troppo aggressiva;
- errore di detection del terminale.

---

## `suspicious_matches`
Terminali matched, ma con distanza di snap troppo alta.

### Significato
Lo script ha trovato un filo, ma il match potrebbe essere poco affidabile.

---

# Perché il 05 è forte ma anche delicato

Il 05 è potente perché:
- usa lo skeleton reale dei fili;
- riusa i terminali semantici del 03;
- corregge molti casi difficili con euristiche mirate;
- produce un JSON finale molto semplice.

Ma è delicato perché:
- tutto dipende dalla qualità del 03 e del 04;
- simboli fuori specifica possono rompere la topologia;
- transformer, connector, meter, opamp, MOSFET e crossing richiedono trattamenti speciali.

Per questo il file contiene molte funzioni euristiche: non sono “ornamenti”, ma pezzi necessari per evitare errori topologici seri.

---

# Sintesi finale

Il passo 05 funziona così:

1. carica lo skeleton dei fili;
2. rimuove i corpi dei componenti che non devono diventare fili;
3. calcola le connected components dello skeleton;
4. aggancia ogni terminale alla label del filo più vicino;
5. costruisce gruppi `label -> terminali`;
6. corregge fusioni e spezzature con euristiche;
7. trasforma ogni gruppo in collegamenti terminale ↔ terminali;
8. aggiunge supply symbol come `VDD` e `VSS` quando riconosciuti;
9. salva un JSON finale minimale e leggibile.

In una frase:

> il 05 trasforma uno skeleton di fili e una lista di terminali in una rappresentazione topologica del circuito sotto forma di grafo tra terminali.

---

# Formula breve da ricordare per la tesi

Puoi riassumere il cuore del 05 anche così:

```text
Terminali del passo 03
        +
Skeleton dei fili del passo 04
        ↓
match terminale → connected component
        ↓
gruppi di terminali sullo stesso filo
        ↓
correzioni euristiche (merge / split)
        ↓
grafo finale terminale → terminali collegati
```

---

# Osservazione finale utile per la tesi

L’output finale del 05 **non è un simulatore elettrico** e non vuole descrivere la fisica interna del componente.  
Vuole descrivere la **topologia esterna del diagramma**, cioè:

- quali terminali sono presenti;
- quali terminali risultano sullo stesso nodo di connessione;
- quali casi restano dubbi o isolati.

Per questo il JSON è adatto come rappresentazione intermedia per una AI che deve:
- ricostruire il diagramma;
- controllare se ci sono errori;
- ragionare sui collegamenti principali del circuito.
