# Documentazione tecnica del passo `03_estimate_terminals`

## Scopo del modulo

Il passo `03_estimate_terminals` ha il compito di trasformare l’output del passo precedente della pipeline, cioè l’elenco dei componenti già rilevati e istanziati, in una rappresentazione più ricca in cui ogni componente possiede:

- i suoi terminali stimati;
- l’orientazione stimata del simbolo;
- eventuali informazioni sul lato di connessione;
- un insieme di punteggi e debug utili a capire **perché** una certa decisione è stata presa.

In altre parole, questo stadio non esegue la detection del componente, ma prende il **bounding box** del componente già noto e cerca di rispondere a quattro domande:

1. **quanti terminali ha il simbolo?**
2. **su quali lati del bounding box si trovano?**
3. **dove cadono esattamente lungo ciascun lato?**
4. **in alcuni casi, che significato semantico hanno?**  
   Ad esempio: positivo/negativo, current\_from/current\_to, gate/source/drain, ecc.

---

## Perimetro di questo documento

Questo documento descrive **solo i file attualmente forniti**:

- `03_estimate_terminals.py`
- `processor.py`
- `dispatcher.py`
- `strategies_basic.py`
- `geometry.py`
- `probes.py`
- `image_ops.py`
- `io_utils.py`
- `debug_draw.py`

Alcune parti del flusso delegano poi a moduli non descritti qui in dettaglio, ad esempio:

- `semantic_two_terminal.py`
- `strategies_three_terminal.py`
- `strategies_opamp.py`
- `strategies_connector.py`
- `strategies_structured_symbols.py`
- `strategies_terminal_class.py`

Quando i file qui analizzati chiamano questi moduli esterni, in questo documento si descrive **il punto in cui avviene la chiamata** e il **ruolo** che essa ha nel flusso, ma non si entra nel dettaglio interno del codice non fornito.

---

## Flusso generale del passo 03

L’elaborazione completa di questo stadio può essere riassunta così:

1. si legge il file YAML con i metadati delle classi;
2. si legge ogni JSON del passo `02_assign_instances`;
3. si carica l’immagine originale corrispondente;
4. si costruisce una versione binaria foreground/background dell’immagine;
5. per ogni componente:
   - si sceglie la strategia terminale appropriata;
   - si stima orientazione e struttura terminale;
   - si localizzano i punti terminali;
   - si applica, se prevista, una semantica ai terminali;
6. si salva il nuovo JSON arricchito;
7. opzionalmente si genera un’immagine di debug con bbox, terminali e label.

Dal punto di vista concettuale, il passo 03 è quindi un blocco di **reasoning geometrico e topologico locale sul simbolo**, basato sul bounding box e sulla binarizzazione dell’immagine.

---

# 1. `03_estimate_terminals.py`

## Ruolo del file

Questo file è l’**entry point** del passo 03.  
Non contiene le regole di stima dei terminali in sé, ma organizza l’esecuzione sull’intero dataset di input.

## Variabili di percorso e configurazione

Il file definisce:

- `PROJECT_ROOT`: radice del progetto;
- `PIPELINE_DATASET`: nome del dataset di pipeline, ricavato dall’ambiente oppure da un default;
- `INPUT_DIR`: cartella del passo `02_assign_instances`;
- `OUTPUT_DIR`: cartella di uscita del passo `03_estimate_terminals`;
- `DEBUG_IMAGES_DIR`: cartella in cui salvare le immagini di debug;
- `CLASS_TERMINALS_PATH`: file YAML con i metadati delle classi.

Queste variabili fissano la convenzione di I/O del passo 03.

## Funzione `main()`

### Scopo
Esegue l’intero stadio di pipeline su tutti i file JSON presenti nella cartella di input.

### Logica dettagliata
La funzione:

1. verifica che esistano:
   - la cartella di input;
   - il file YAML con i metadati delle classi;
2. crea, se necessario:
   - la cartella di output;
   - la cartella delle immagini di debug;
3. carica i metadati classe con `io_load_class_metadata(...)`;
4. elenca e ordina tutti i JSON in input;
5. per ogni JSON:
   - legge il contenuto;
   - ricava `image_path`;
   - carica l’immagine con OpenCV;
   - costruisce la binaria foreground con `img_build_foreground_binary(...)`;
   - scorre tutti i componenti;
   - per ogni componente invoca `estimate_terminals_for_component(...)`;
   - aggiorna il componente con:
     - `terminals`
     - `estimated_orientation`
     - `estimated_connection_side`
     - `connection_side_scores`
   - raccoglie in `all_terminals` tutti i terminali stimati;
6. dopo aver stimato tutti i componenti dell’immagine, richiama `snap_opamp_top_aux_to_nearby_terminal(...)` per una rifinitura specifica dei terminali ausiliari superiori degli opamp;
7. costruisce `output_data`, cioè il JSON finale con:
   - `components` aggiornati,
   - `terminals` globali,
   - `n_terminals_estimated`;
8. salva il JSON finale in output;
9. se `SAVE_DEBUG_IMAGES` è attivo, disegna l’immagine di debug con `draw_terminals(...)`;
10. stampa a terminale una riga di avanzamento.

### Output effettivo
Per ogni immagine si ottiene:
- un file JSON arricchito;
- opzionalmente un file immagine con annotazioni di debug.

### Osservazione importante
`main()` non decide **come** stimare i terminali: si limita a orchestrare il lavoro. La logica vera è incapsulata nei moduli `processor`, `dispatcher`, `strategies_basic`, `geometry`, `probes` e nei moduli specializzati importati.

---

# 2. `processor.py`

## Ruolo del file

`processor.py` è il livello che prende **un singolo componente** e lo trasforma in una lista di terminali con coordinate, metadati geometrici e metadati semantici.

## Funzione `estimate_terminals_for_component(component, class_meta, image_binary)`

### Scopo
Stimare i terminali di un singolo componente partendo da:
- il dizionario del componente;
- i metadati della classe;
- l’immagine binaria dell’intera figura.

### Input principali
- `component`: contiene almeno `class_id`, `bbox`, `instance_id`, `class_name`, `use_for_terminals`;
- `class_meta`: mapping `class_id -> metadati YAML`;
- `image_binary`: immagine binaria foreground/background.

### Passi della funzione

#### 1. Recupero dei metadati di classe
Viene letto `class_id`, poi si recupera `meta = class_meta.get(class_id, {})`.

Se il componente ha `use_for_terminals = False`, la funzione ritorna immediatamente:
- lista terminali vuota,
- orientazione `None`,
- connected side `None`,
- side scores `None`. fileciteturn20file8

#### 2. Definizione strutturale dei terminali
La funzione invoca `get_terminals_definition(...)` dal dispatcher.  
Questa chiamata restituisce quattro elementi:

- `terminals_def`: definizione astratta dei terminali prevista per il componente;
- `estimated_orientation`: orientazione stimata;
- `connected_side`: lato connesso, se applicabile;
- `side_scores`: debug dei punteggi usati per decidere.

Qui avviene la separazione fondamentale tra:
- **struttura terminale** del simbolo;
- **coordinate finali** dei punti terminali.

#### 3. Scelta della modalità di localizzazione del punto
Con `resolve_terminal_point_mode(meta)` si sceglie **come** localizzare il punto terminale concreto.

Le modalità possibili viste in questo file sono:

- `three_terminal_structured`
- `OPAMP_POINT_MODE`
- `two_terminal_side_peak`
- `bbox_side_anchor_ratio`
- `bbox_side_center`
- `strategy_absolute_point`

Per i tre terminali si costruisce anche `point_binary`, che può essere una binaria elaborata apposta da `get_three_terminal_working_binary(...)`.

#### 4. Costruzione dei terminali uno per uno
Per ogni terminale astratto in `terminals_def`, il codice costruisce un dizionario completo.

I casi sono:

##### a. Terminale con punto assoluto già noto
Se `term_def["point"]` esiste, il terminale usa direttamente quel punto.  
È il caso delle strategie che restituiscono coordinate assolute già pronte, ad esempio alcuni simboli strutturati.

##### b. Modalità `three_terminal_structured`
Viene chiamata `geom_terminal_point_three_terminal(...)`, che localizza in modo coerente:
- il terminale “singolo” del componente a 3 terminali;
- la coppia ortogonale.

##### c. Modalità opamp
Viene chiamata `geom_terminal_point_opamp(...)`, che gestisce terminali mandatory e terminali ausiliari degli opamp.

##### d. Modalità `two_terminal_side_peak`
Qui si usa `geom_terminal_point_by_side_peak(...)`, salvo due eccezioni importanti:

- **Diode**: usa il centro del lato, non il side-peak;
- **GND**: usa il centro del lato superiore, per non farsi influenzare dal testo vicino.

##### e. Modalità standard da bbox
Se non si ricade nei casi precedenti:
- se il terminale ha `anchor_offset_ratio`, si usa `geom_terminal_point_from_bbox_with_anchor(...)`;
- altrimenti si usa `geom_terminal_point_from_bbox(...)`.

In entrambi i casi vengono costruite informazioni di debug sul punto.

#### 5. Arricchimento semantico
Una volta costruiti i terminali geometrici:

- se il point mode è `three_terminal_structured`, si chiama `resolve_three_terminal_semantics(...)`;
- altrimenti si chiama `resolve_two_terminal_semantics(...)`.

Questo significa che la geometria viene risolta **prima**, la semantica **dopo**.

### Output
La funzione ritorna:
- lista dei terminali completi;
- orientazione stimata;
- lato connesso;
- side scores / debug.

### Significato architetturale
`estimate_terminals_for_component(...)` è il vero **ponte** fra:
- decisione strategica;
- localizzazione geometrica;
- arricchimento semantico.

---

# 3. `dispatcher.py`

## Ruolo del file

Il dispatcher sceglie **quale strategia usare** in base ai metadati YAML della classe.  
È quindi il modulo che traduce la configurazione dichiarativa del simbolo in logica effettiva.

## Funzione `_get_oriented_terminals(meta, orientation)`

### Scopo
Dato l’orientamento scelto, estrae dalla sezione `orientations` del metadata la definizione terminale corretta.

### Comportamento
- legge `meta["orientations"][orientation]`;
- se manca, solleva errore.

### Utilità
È il punto in cui una stima di orientazione viene trasformata nella lista concreta dei terminali previsti per quel verso.

---

## Funzione `resolve_terminal_point_mode(meta)`

### Scopo
Stabilire **come** saranno localizzati i punti terminali, indipendentemente da quanti terminali il simbolo abbia.

### Logica
La funzione:

1. controlla se nel metadata esiste `terminal_point_mode` esplicito;
2. altrimenti sceglie un mode implicito in base a:
   - `terminal_strategy`;
   - `class_name`.

### Regole principali
- `three_terminal_by_side_pattern` → `three_terminal_structured`
- `opamp_by_orientation_and_optional_supply` → `OPAMP_POINT_MODE`
- `connector_by_projection` → `bbox_side_center`
- `analog_meter_by_posts`, `transformer_external_wires` → `strategy_absolute_point`
- `two_terminal_led`, `two_terminal_variable_resistor`, `one_terminal_by_orientation` → `two_terminal_side_peak`
- `LED`, `Diode` → `two_terminal_side_peak`
- altrimenti → `bbox_side_center`

### Significato
Questa funzione separa la **decisione strutturale** dalla **modalità di localizzazione del punto**.

---

## Funzione `_resolve_two_terminal_orientation(strategy, class_name, image_binary, bbox, default_orientation)`

### Scopo
Scegliere il risolutore giusto per l’orientazione dei componenti a 2 terminali.

### Casi gestiti
- `Capacitor`, `Polarized_Capacitor` → `detect_two_terminal_orientation_capacitor`
- `Switch` → `strategy_detect_two_terminal_orientation_switch`
- `LED` → `detect_two_terminal_orientation_led`
- `Diode` → strategia generica
- `Signal_Source`, `Voltage_Source`, `Current_Source`, `Meter` → `detect_two_terminal_orientation_round_source`
- `Resistor` / variable resistor → `detect_two_terminal_orientation_variable_resistor`
- altrimenti → strategia generica

### Significato
Questo è il punto in cui la pipeline riconosce che un componente a 2 terminali “normale” e uno a 2 terminali “speciale” non vanno trattati allo stesso modo.

---

## Funzione `get_terminals_definition(meta, bbox, image_binary=None)`

### Scopo
Restituire la **definizione astratta dei terminali** e l’eventuale orientazione/lato connesso, scegliendo la strategia in base al metadata.

### Casi supportati

#### `fixed`
Ritorna direttamente `meta["terminals"]`.  
Nessuna stima.

#### `auto_by_aspect_ratio`
Usa il rapporto fra altezza e larghezza del bbox tramite `geom_infer_orientation_from_bbox(...)`.  
Eccezione: per `Transformer`, se c’è l’immagine binaria, usa la strategia generica a connessione invece del semplice bbox.

#### `one_terminal_by_orientation`
Usa `strategy_detect_connected_side(...)`, poi `resolve_one_terminal_orientation(...)`.

#### Strategie a 2 terminali basate sull’asse di connessione
Per:
- `two_terminal_by_connection_axis`
- `two_terminal_capacitor`
- `two_terminal_switch`
- `two_terminal_led`
- `two_terminal_round_source`
- `two_terminal_variable_resistor`

invoca `_resolve_two_terminal_orientation(...)` e poi `_get_oriented_terminals(...)`.

#### `terminal_auto_one_or_two`
Delega a `detect_terminal_auto_one_or_two(...)` per i simboli terminali che possono comportarsi da mono- o bi-terminale.

#### `connector_by_projection`
Delega a `detect_connector_terminals(...)`.

#### `analog_meter_by_posts`
Delega a `detect_analog_meter_terminals(...)`.

#### `transformer_external_wires`
Delega a `detect_transformer_terminals(...)`.

#### `opamp_by_orientation_and_optional_supply`
Delega a `detect_opamp_terminals(...)`.

#### `three_terminal_by_side_pattern`
Delega a `strategy_detect_three_terminal_orientation(...)`, poi estrae la definizione orientata.

### Significato architetturale
`get_terminals_definition(...)` è il **cuore del dispatch strategico** della pipeline.

---

# 4. `strategies_basic.py`

## Ruolo del file

Questo file contiene le strategie “base” per:

- componenti a un terminale;
- componenti a due terminali;
- alcune classi speciali a 2 terminali:
  - capacitor,
  - switch,
  - LED,
  - round source,
  - variable resistor.

Non tratta i simboli strutturati complessi come opamp, transformer o analog meter.

---

## Funzione `_group_consecutive_indices(indices)`

### Scopo
Raggruppare indici consecutivi in sottoliste.

### Uso
Serve per trasformare liste di picchi/indici “tenuti” in gruppi continui, per esempio nell’analisi delle proiezioni interne del condensatore.

---

## Sezione: componenti a un terminale

## Funzione `_score_one_terminal_candidate_side(binary, bbox, side)`

### Scopo
Valutare un lato candidato come lato connesso di un componente mono-terminale.

### Logica
1. localizza un punto candidato sul lato usando `geom_terminal_point_by_side_peak(...)`;
2. valuta il supporto direzionale attorno al punto con `score_point_directional_support(...)`;
3. ritorna:
   - punteggio,
   - punto,
   - debug del side-peak.

### Significato
Non valuta il lato in modo astratto, ma valuta un **punto terminale specifico** sul lato.

---

## Funzione `strategy_detect_connected_side(binary, bbox)`

### Scopo
Determinare quale lato del bbox è realmente connesso per un simbolo a un solo terminale.

### Strategia in due fasi

#### Fase 1: validazione puntuale dei 4 lati
Per ciascuno dei lati:
- genera un punto candidato;
- misura il supporto direzionale.

Poi ordina i lati e controlla se:
- il miglior lato supera una soglia minima;
- il miglior lato è sufficientemente migliore del secondo.

Se sì, ritorna quel lato con `decision_mode = "one_terminal_point_validation"`.

#### Fase 2: fallback a bande centrali
Se la validazione puntuale non è conclusiva:
- campiona bande centrali sui quattro lati del bbox;
- sceglie il lato con più foreground;
- se il punteggio è troppo basso, ritorna `None`.

### Significato
La strategia moderna è “point-first”, con un fallback più grossolano a bande.

---

## Funzione `resolve_one_terminal_orientation(meta, connected_side)`

### Scopo
Dato il lato connesso, trovare quale orientazione del simbolo corrisponde a quel lato.

### Logica
Scorre `meta["orientations"]` e cerca la definizione in cui il terminale ha `relative_position == connected_side`.

Se non la trova:
- usa `default_orientation`.

### Utilità
Trasforma l’informazione “il terminale è a sinistra/destra/sopra/sotto” in una vera orientazione di classe.

---

## Sezione: componenti a due terminali

## Funzione `_decide_axis_from_scores(side_scores)`

### Scopo
Decidere se l’asse di connessione è:
- orizzontale,
- verticale,
- oppure indeterminato.

### Logica
Calcola:
- `lr_pair = min(left, right)`
- `tb_pair = min(top, bottom)`
- `lr_score = left + right`
- `tb_score = top + bottom`

Regola:
- se entrambi i lati `left/right` sono abbastanza attivi e dominano `top/bottom`, orientazione orizzontale;
- se `top/bottom` dominano, orientazione verticale;
- altrimenti `None`.

### Significato
La decisione non si basa sul singolo lato più forte, ma sulla **coerenza di una coppia di lati opposti**.

---

## Funzione `strategy_detect_two_terminal_orientation_generic(binary, bbox, default_orientation="horizontal")`

### Scopo
Stimare l’orientazione di un componente a 2 terminali senza assumere una struttura interna speciale.

### Strategia in tre livelli

#### 1. Probe locali centrati
Usa `get_local_terminal_probe_scores_center(...)` e `_decide_axis_from_scores(...)`.

#### 2. Fallback con bande laterali più grossolane
Usa `probe_get_side_scores(...)`.

#### 3. Fallback finale sul bbox
Usa `geom_infer_orientation_from_bbox(...)`.

### Significato
Questa è la strategia di base da cui si parte quando il simbolo non richiede euristiche speciali.

---

## Funzione `detect_two_terminal_orientation_capacitor(binary, bbox, default_orientation="horizontal")`

### Scopo
Riconoscere l’orientazione di condensatori sfruttando la struttura interna delle due piastre.

### Strategia

#### 1. Analisi interna del simbolo
Viene ritagliata una ROI interna e si calcolano:
- proiezione per righe,
- proiezione per colonne.

Poi si conta il numero di picchi:

- due picchi per righe → due piastre orizzontali → terminali `top/bottom` → orientazione `vertical`;
- due picchi per colonne → due piastre verticali → terminali `left/right` → orientazione `horizontal`.

#### 2. Override bilanciato
Se le proiezioni interne non bastano, si guardano i probe locali centrati:
- coppia `left/right` forte e molto più forte di `top/bottom` → `horizontal`;
- viceversa → `vertical`.

#### 3. Strategia generica
Se ancora ambiguo:
- prova la decisione con `_decide_axis_from_scores(...)`;
- poi `probe_get_side_scores(...)`;
- infine bbox fallback.

### Significato
Per il condensatore non si guarda solo la connessione esterna, ma anche la **morfologia interna del simbolo**.

---

## Funzione `strategy_detect_two_terminal_orientation_switch(binary, bbox, default_orientation="horizontal")`

### Scopo
Stimare l’orientazione degli switch, che spesso non hanno una massa di foreground distribuita in modo simmetrico.

### Strategia
1. usa `get_local_terminal_probe_scores_multi_anchor(...)`, cioè più punti di campionamento lungo i lati;
2. se non basta, usa `probe_get_side_scores(...)`;
3. se ancora non basta, invece del bbox usa direttamente `default_orientation`.

### Motivazione
Per uno switch aperto, il bounding box può essere fortemente fuorviante; per questo si preferisce il default alla semplice inferenza da aspect ratio.

---

## Funzione `_score_two_terminal_candidate_by_points(binary, bbox, orientation)`

### Scopo
Valutare una orientazione ipotetica (`horizontal` o `vertical`) attraverso due punti terminali candidati.

### Logica
Per i due lati previsti da quell’orientazione:
- localizza il punto con `geom_terminal_point_by_side_peak(...)`;
- valuta il supporto direzionale del punto;
- somma i punteggi.

### Output
Restituisce:
- `total_score`
- score per lato
- debug del punto

### Significato
Questa funzione permette di confrontare due orientazioni non in astratto, ma tramite la qualità dei **terminali concretamente localizzati**.

---

## Funzione `detect_two_terminal_orientation_led(binary, bbox, default_orientation="vertical")`

### Scopo
Stimare l’orientazione di un LED con una strategia dedicata.

### Fasi

#### 1. Validazione puntuale
Confronta:
- ipotesi orizzontale,
- ipotesi verticale

usando `_score_two_terminal_candidate_by_points(...)`.

#### 2. Probe LED near/far
Se la validazione puntuale non basta:
- usa `get_led_probe_scores(...)`;
- usa `get_led_far_probe_scores(...)`;
- combina i due insiemi di score.

#### 3. Fallback bbox invertito specifico LED
Se ancora ambiguo, usa il rapporto del bbox ma **invertendo l’interpretazione** rispetto a un componente standard:
- simbolo largo può implicare terminali `top/bottom`;
- simbolo alto può implicare terminali `left/right`.

#### 4. Default finale
Se tutto resta ambiguo, usa `default_orientation`.

### Significato
Il LED è un caso in cui forma interna e disposizione grafica rendono poco affidabile il semplice aspect ratio.

---

## Funzione `detect_two_terminal_orientation_round_source(binary, bbox, default_orientation="vertical")`

### Scopo
Gestire le sorgenti tonde e i simboli circolari simili:
- `Signal_Source`
- `Voltage_Source`
- `Current_Source`
- `Meter`

### Strategia
1. usa probe “near” (`get_round_source_probe_scores(...)`);
2. usa probe “far” (`get_round_source_far_probe_scores(...)`);
3. combina i punteggi;
4. decide l’asse con la regola delle coppie opposte;
5. se necessario usa bbox fallback;
6. altrimenti usa `default_orientation`.

### Significato
Per i simboli rotondi il bbox puro è spesso poco informativo; i probe esterni sono molto più utili.

---

## Funzione `_score_variable_resistor_candidate_by_points(binary, bbox, orientation)`

### Scopo
Valutare una possibile orientazione del resistore variabile tramite punti terminali candidati.

### Differenza rispetto al caso generico
Il supporto direzionale usa:
- `outward=10`
- `inward=0`

cioè privilegia quasi solo la parte esterna del lato, riducendo l’influenza della grafica interna del simbolo.

### Motivazione
Il resistore variabile ha un simbolo interno che può disturbare molto una sonda che guarda anche verso l’interno.

---

## Funzione `detect_two_terminal_orientation_variable_resistor(binary, bbox, default_orientation="horizontal")`

### Scopo
Stimare l’orientazione del resistore con una strategia robusta al testo e alla grafica interna.

### Fasi

#### 1. Validazione diretta per punti
Confronta orientazione verticale e orizzontale con `_score_variable_resistor_candidate_by_points(...)`.

#### 2. Bande esterne strette
Se la validazione diretta è insufficiente, usa piccole bande fuori dal bbox:
- sopra,
- sotto,
- sinistra,
- destra.

Questo riduce la sensibilità a testo vicino e grafica interna.

#### 3. Fallback generico
Se il risultato resta ambiguo, richiama `strategy_detect_two_terminal_orientation_generic(...)` e salva anche i punteggi esterni nel debug.

### Significato
È una strategia specializzata per simboli che spesso vengono perturbati da annotazioni o dalla diagonale del cursore.

---

# 5. `geometry.py`

## Ruolo del file

Questo file contiene tutta la geometria di basso livello per:
- clamp dei bounding box;
- localizzazione base dei punti terminali;
- localizzazione side-peak;
- localizzazione strutturata per 3 terminali;
- localizzazione dedicata dei terminali opamp.

È uno dei moduli più importanti dell’intero passo 03.

---

## Geometria generica

## Funzione `geom_clamp_bbox_to_image(bbox, image_shape)`

### Scopo
Forzare il bbox a rimanere dentro i limiti dell’immagine.

### Logica
Arrotonda le coordinate e le satura in:
- `[0, w-1]` per x;
- `[0, h-1]` per y.

### Utilità
Evita accessi fuori immagine nelle fasi di probing.

---

## Funzione `geom_terminal_point_from_bbox(bbox, relative_position)`

### Scopo
Restituire il terminale come **centro geometrico del lato** del bbox, spostato all’esterno di `TERMINAL_OUTWARD_OFFSET`.

### Regole
- `left` → punto a sinistra del bbox, centrato verticalmente;
- `right` → punto a destra;
- `top` → punto sopra;
- `bottom` → punto sotto.

### Significato
È la localizzazione più semplice e più neutra.

---

## Funzione `geom_terminal_point_from_bbox_with_anchor(bbox, relative_position, anchor_offset_ratio)`

### Scopo
Restituire un punto sul lato non nel centro, ma a una frazione specifica del lato.

### Logica
`anchor_offset_ratio` è clippato in `[0, 1]`.

Esempi:
- lato sinistro: y = `y1 + ratio * height`;
- lato superiore: x = `x1 + ratio * width`.

### Utilità
Serve quando il terminale non sta nel centro del lato ma in una posizione nota a priori.

---

## Funzione `geom_infer_orientation_from_bbox(bbox, default_orientation="horizontal")`

### Scopo
Inferire l’orientazione solo dal rapporto di forma del bbox.

### Regola
- se `height / width >= ASPECT_RATIO_THRESHOLD` → `vertical`;
- se `width / height >= ASPECT_RATIO_THRESHOLD` → `horizontal`;
- altrimenti → `default_orientation`.

### Significato
È un fallback semplice ma utile quando mancano segnali più affidabili.

---

## Side-peak localization

## Funzione `_side_peak_halfspan(width, height)`

### Scopo
Calcolare la semi-larghezza della finestra usata per i probe di side-peak.

### Logica
Parte dal lato minimo del bbox, poi applica:
- ratio,
- minimo,
- massimo.

### Utilità
Adatta la finestra alla scala del simbolo.

---

## Funzione `_side_peak_scan_margin(length)`

### Scopo
Calcolare il margine da lasciare alle estremità del lato durante la scansione side-peak.

### Motivazione
Evita che i bordi estremi del bbox dominino artificialmente la scansione.

---

## Funzione `_group_consecutive_indices(indices)`

### Scopo
Raggruppare indici consecutivi.  
È la versione usata internamente alla side-peak localization.

---

## Funzione `_select_peak_index_from_scores(scores, center_index)`

### Scopo
Scegliere il miglior indice lungo un lato, ma in modo robusto al rumore.

### Logica dettagliata
1. se non ci sono score, ritorna stato vuoto;
2. se il massimo è sotto `SIDE_PEAK_MIN_SCORE`, usa il centro;
3. altrimenti tiene solo i punti sopra una soglia `keep_threshold`;
4. raggruppa questi punti in run consecutive;
5. sceglie il gruppo migliore con un criterio che privilegia:
   - picco massimo,
   - somma degli score,
   - lunghezza della run,
   - vicinanza al centro in caso di parità;
6. ritorna l’indice centrale del gruppo migliore.

### Significato
Non usa il massimo puntuale puro: usa una run robusta di score alti.

---

## Funzione `geom_terminal_point_by_side_peak(binary, bbox, relative_position, scan_start=None, scan_end=None, center_coord=None)`

### Scopo
Localizzare un terminale cercando il picco di supporto lungo il lato indicato.

### Logica
Per il lato scelto:
1. definisce intervallo di scansione e margini;
2. per ogni coordinata della scansione calcola un punteggio di foreground in una piccola finestra che attraversa il bordo;
3. usa `_select_peak_index_from_scores(...)` per scegliere il picco robusto;
4. restituisce il punto terminale fuori dal bbox;
5. ritorna anche un dizionario di debug molto ricco.

### Due casi geometrici
- se il lato è `top/bottom`, si scansiona lungo x;
- se il lato è `left/right`, si scansiona lungo y.

### Significato
Questa è la funzione base più importante per localizzare terminali non centrati.

---

## Geometria per componenti a tre terminali

## Funzione `_three_terminal_pair_scan_window(x1, y1, x2, y2, orientation, same_side=False)`

### Scopo
Definire la finestra di scansione da usare per la coppia di terminali ortogonali nei simboli a 3 terminali.

### Logica
La finestra dipende da:
- orientazione del componente (`left`, `right`, `top`, `bottom`);
- scelta `same_side` o `opposite_side`.

### Significato
Permette di trattare i casi in cui la coppia di terminali è leggermente specchiata.

---

## Funzione `_resolve_three_terminal_pair_bias(binary, bbox, orientation)`

### Scopo
Capire se la coppia ortogonale va cercata secondo il modello:
- `opposite_side`
- oppure `same_side`.

### Logica
1. identifica le due posizioni della coppia ortogonale;
2. valuta due ipotesi:
   - scansione opposite-side,
   - scansione same-side;
3. usa per ciascuna un punteggio derivato da `geom_terminal_point_by_side_peak(...)`;
4. se l’ipotesi specchiata è significativamente migliore, la seleziona.

### Significato
È una correzione importante per simboli reali che non rispettano perfettamente il template ideale.

---

## Funzione `geom_terminal_point_three_terminal(binary, bbox, orientation, relative_position)`

### Scopo
Localizzare un terminale di un simbolo a 3 terminali coerentemente con la sua orientazione.

### Casi

#### 1. Terminale singolo
Se `relative_position == orientation`, il terminale viene cercato in una banda centrale del lato.

#### 2. Terminale della coppia ortogonale
Si stima prima il `pair_bias`, poi si usa la finestra corretta per cercare il punto sul lato ortogonale.

#### 3. Fallback
Se la combinazione non è gestita, usa `geom_terminal_point_by_side_peak(...)`.

### Output
Restituisce:
- punto;
- debug con:
  - ruolo terminale,
  - orientazione,
  - pair bias,
  - dettagli della scansione.

### Significato
Questa funzione costruisce una localizzazione strutturata e coerente, non una semplice localizzazione lato per lato.

---

## Geometria per opamp

L’opamp viene trattato in modo molto più raffinato, distinguendo:
- terminali **mandatory**;
- terminali **auxiliary**.

---

## Funzione `_opamp_count_horizontal_line(binary, x_start, x_end, y)`

### Scopo
Contare foreground su una linea orizzontale di lunghezza arbitraria.

### Utilità
È un helper di basso livello per i probe opamp.

---

## Funzione `_opamp_count_vertical_line(binary, x, y_start, y_end)`

### Scopo
Analogo al precedente, ma su linea verticale.

---

## Funzione `_select_opamp_mandatory_best_index(scores, coords, center_coord)`

### Scopo
Scegliere la coordinata migliore per un terminale mandatory dell’opamp.

### Logica
- tiene gli score sopra una soglia relativa al massimo;
- se non ci sono, prende il massimo puro;
- in caso di più candidati “buoni”, preferisce quello più vicino al centro atteso.

### Significato
Garantisce stabilità e coerenza slot-aware.

---

## Funzione `_opamp_slot_scan_range(x1, y1, x2, y2, relative_position, slot)`

### Scopo
Restituire l’intervallo di scansione corretto per un certo slot dell’opamp:
- `upper`, `lower`, `center` sui lati verticali;
- `left`, `right`, `center` sui lati orizzontali.

### Significato
Permette di distinguere, ad esempio, ingresso invertente, non invertente e alimentazioni.

---

## Funzione `_opamp_mandatory_probe_score(binary, bbox, relative_position, coord)`

### Scopo
Calcolare il punteggio di un candidato terminale mandatory dell’opamp.

### Componenti del punteggio
Per una coordinata candidata si combinano:
- `near`: supporto subito fuori dal bordo;
- `far`: continuità più distante;
- `border`: supporto a cavallo del bordo.

Questi termini vengono pesati con costanti di config.

### Significato
L’idea è misurare non solo il contatto col bordo, ma anche la continuità del wire.

---

## Funzione `_geom_opamp_mandatory_terminal(binary, bbox, relative_position, slot)`

### Scopo
Localizzare un terminale mandatory dell’opamp.

### Logica
1. ricava l’intervallo di scansione dal `slot`;
2. genera candidati coordinata per coordinata;
3. li valuta con `_opamp_mandatory_probe_score(...)`;
4. seleziona il migliore con `_select_opamp_mandatory_best_index(...)`;
5. restituisce il punto terminale fuori dal bbox e un debug esteso.

---

## Funzione `_opamp_aux_scan_x_range(bbox)`

### Scopo
Definire l’intervallo di x in cui cercare i terminali ausiliari superiori/inferiori dell’opamp.

### Motivazione
Restringe la ricerca alla zona plausibile del ramo ausiliario.

---

## Funzione `_opamp_vertical_run_from_edge(binary, bbox, x, side)`

### Scopo
Cercare una run verticale di foreground che parte dal bordo superiore o inferiore del bbox.

### Logica
- per `top` cerca la prima riga valida vicino al bordo alto e poi scende;
- per `bottom` fa l’analogo verso l’alto;
- tollera piccoli gap;
- limita la profondità massima.

### Significato
Serve a individuare lo stelo verticale di un terminale ausiliario.

---

## Funzione `_opamp_diagonal_support(binary, x, y, diag_kind, radius=4)`

### Scopo
Valutare quanta struttura diagonale passa attorno a un punto.

### Utilità
Aiuta a riconoscere il punto in cui il ramo verticale si innesta sulla diagonale del triangolo opamp.

---

## Funzione `_opamp_aux_segment_density(binary, x, y1, y2, side, y, halfspan=1)`

### Scopo
Calcolare la densità di foreground lungo il segmento verticale dell’aux.

### Utilità
Serve a filtrare falsi positivi durante il raffinamento del punto ausiliario.

---

## Funzione `_opamp_refine_aux_y_to_diagonal(binary, bbox, orientation, relative_position, x, base_y)`

### Scopo
Raffinare la coordinata y di un terminale ausiliario cercando il giunto con la diagonale del simbolo.

### Strategia
1. definisce il tipo di diagonale atteso in funzione dell’orientazione;
2. costruisce una lista di y da scandire dal bordo verso l’interno;
3. cerca il **primo giunto valido** con:
   - supporto diagonale sufficiente,
   - densità di segmento sufficiente;
4. se non trova un first-hit buono, usa il miglior candidato globale.

### Significato
Questa è la vera rifinitura che sposta il terminale ausiliario dal semplice “ramo verticale” al giunto reale con il triangolo.

---

## Funzione `_opamp_vertical_band_density(binary, x, y_start, y_end, halfspan=1)`

### Scopo
Misurare la densità di una banda verticale.  
È un helper ausiliario di basso livello.

---

## Funzione `_opamp_aux_make_refine_binary(binary, bbox, orientation)`

### Scopo
Costruire una versione della binaria in cui alcune regioni interne dell’opamp vengono mascherate.

### Motivazione
Testo o etichette interne possono disturbare il raffinamento dei terminali ausiliari.

### Comportamento
- se la maschera è disabilitata, ritorna l’immagine originale;
- se l’orientazione non è supportata, ritorna l’originale con debug;
- altrimenti maschera due rettangoli interni, uno superiore e uno inferiore.

---

## Funzione `_geom_opamp_aux_terminal_v1(binary, bbox, orientation, relative_position)`

### Scopo
Localizzare un terminale ausiliario dell’opamp.

### Strategia
1. controlla che orientazione e lato siano supportati;
2. ricava la fascia di scansione lungo x;
3. cerca run verticali candidate con `_opamp_vertical_run_from_edge(...)`;
4. tiene i candidati abbastanza lunghi;
5. sceglie il ramo più interno:
   - per opamp `right`, quello più a sinistra;
   - per opamp `left`, quello più a destra;
6. costruisce una binaria raffinata con `_opamp_aux_make_refine_binary(...)`;
7. mantiene la x della run;
8. rifinisce la y con `_opamp_refine_aux_y_to_diagonal(...)`.

### Significato
È una pipeline completa per localizzare terminali ausiliari che non stanno su lati “banali”.

---

## Funzione `geom_terminal_point_opamp(binary, bbox, orientation, term_def)`

### Scopo
API pubblica per localizzare un terminale opamp.

### Logica
- se `terminal_role == "auxiliary"`, usa `_geom_opamp_aux_terminal_v1(...)`;
- altrimenti usa `_geom_opamp_mandatory_terminal(...)`.

In entrambi i casi arricchisce il debug con:
- orientazione opamp,
- nome terminale,
- ruolo,
- slot.

---

# 6. `probes.py`

## Ruolo del file

Questo file raccoglie tutte le primitive di probing locale sull’immagine binaria.  
Sono funzioni che non decidono direttamente la semantica o l’orientazione finale, ma producono **misure locali di supporto** che altri moduli usano per decidere.

---

## Funzione `probe_get_side_scores(binary, bbox)`

### Scopo
Calcolare i punteggi di foreground in quattro bande centrali attorno ai lati del bbox.

### Significato
È una sonda semplice e grossolana, usata come fallback.

---

## Funzione `_probe_halfspan(width, height)`

### Scopo
Determinare la semiampiezza del probe locale standard.

---

## Funzione `get_local_terminal_probe_scores_center(binary, bbox)`

### Scopo
Calcolare punteggi locali centrati sui 4 lati del bbox.

### Logica
Per ciascun lato misura una piccola finestra che attraversa il bordo, con una porzione esterna e una piccola porzione interna.

### Significato
È la sonda locale standard per capire su quali lati arrivano i wire.

---

## Funzione `get_local_terminal_probe_scores_multi_anchor(binary, bbox, anchor_ratios=SWITCH_ANCHOR_RATIOS)`

### Scopo
Versione multi-anchor della sonda precedente.

### Logica
Invece di sondare solo al centro del lato, sonda in più ancoraggi distribuiti lungo il lato e tiene il massimo.

### Utilità
È particolarmente utile per simboli come gli switch, in cui il terminale può non cadere nel centro del lato.

---

## Funzione `_led_probe_halfspan(width, height)`

### Scopo
Calcolare la semiampiezza specifica del probe LED.

---

## Funzione `get_led_probe_scores(binary, bbox)`

### Scopo
Calcolare i probe “near” per LED usando bande centrali strette.

### Significato
La strettezza della banda riduce il rumore dovuto alla grafica interna.

---

## Funzione `get_led_far_probe_scores(binary, bbox)`

### Scopo
Calcolare probe più lontani dal bbox per i LED.

### Utilità
Misura la continuità del wire al di là del simbolo, complementare ai probe vicini.

---

## Funzione `_mosfet_single_side_halfspan(width, height)`

### Scopo
Calcolare la semiampiezza per i probe dedicati al lato singolo dei MOSFET.

---

## Funzione `get_mosfet_single_side_scores(binary, bbox)`

### Scopo
Valutare quale lato del MOSFET è il lato singolo.

### Strategia
Per ciascun lato calcola:
- `near_scores`: supporto immediatamente fuori dal bbox;
- `far_scores`: continuità più lontana.

Poi combina i due contributi.

### Significato
Il lato singolo del MOSFET deve avere sia contatto vicino sia continuità esterna.

---

## Funzione `get_mosfet_lateral_gate_scores(binary, bbox)`

### Scopo
Distinguere i casi speculari dei MOSFET laterali, specialmente gate sinistro vs gate destro.

### Logica
Combina:
- supporto esterno del lato;
- massa interna nella banda del gate;
- massa esterna lungo tutto il lato;
- rapporto di focalizzazione;
- penalità sugli angoli.

### Significato
Non guarda solo “quanto foreground c’è”, ma **che tipo di distribuzione** ha il foreground sul lato.

---

## Funzione `_terminal_class_probe_halfspan(width, height)`

### Scopo
Calcolare la semiampiezza dei probe dedicati alla classe `Terminal`.

---

## Funzione `get_terminal_class_probe_scores(binary, bbox)`

### Scopo
Calcolare i probe vicini per la classe `Terminal`.

### Caratteristica
I probe guardano quasi esclusivamente fuori dal bbox, perché per il simbolo terminale interessa soprattutto il lato da cui esce la connessione.

---

## Funzione `get_terminal_class_far_probe_scores(binary, bbox)`

### Scopo
Calcolare i probe lontani per la classe `Terminal`.

### Utilità
Aiuta a verificare che la connessione continui anche oltre l’immediato intorno del bbox.

---

## Funzione `get_terminal_border_preference(binary_shape, bbox, margin=TERMINAL_CLASS_BORDER_MARGIN)`

### Scopo
Se il simbolo terminale è vicino a un bordo immagine, suggerire quale lato opposto sia più plausibile come lato connesso.

### Logica
- trova il bordo immagine più vicino;
- se è abbastanza vicino, ritorna il lato opposto.

### Significato
È una euristica utile per terminali posti ai bordi del foglio.

---

## Funzione `is_terminal_near_border(binary_shape, bbox)`

### Scopo
Verificare se il terminale è vicino a un bordo dell’immagine.

---

## Funzione `score_point_local_support(binary, x, y, radius=MOSFET_POINT_SUPPORT_RADIUS)`

### Scopo
Calcolare il supporto locale di foreground attorno a un punto.

### Utilità
Serve come misura grezza di “massa” locale attorno a un candidato terminale.

---

## Funzione `score_point_directional_support(binary, x, y, relative_position, outward=10, inward=3, halfspan=4)`

### Scopo
Misurare il supporto orientato di un punto rispetto a una direzione.

### Logica
La finestra di campionamento dipende dal lato:
- a sinistra si estende verso sinistra;
- a destra verso destra;
- sopra verso l’alto;
- sotto verso il basso.

### Significato
È una misura molto importante: verifica che un punto non sia solo su foreground, ma che abbia foreground **nella direzione giusta**.

---

## Funzione `score_point_orthogonal_support(binary, x, y, relative_position)`

### Scopo
Misurare il supporto nelle direzioni ortogonali a quella principale del punto.

### Utilità
È usato, ad esempio, per penalizzare candidate terminali che hanno troppo supporto ortogonale quando non dovrebbero averlo.

---

## Funzione `score_mosfet_candidate_terminals(binary, terminals, single_side, single_weight=1.35)`

### Scopo
Assegnare un punteggio complessivo a una configurazione candidata di terminali MOSFET.

### Componenti del punteggio
Per ogni terminale valuta:
- supporto locale;
- supporto direzionale;
- supporto ortogonale;
- eventuale penalità ortogonale sul lato singolo;
- peso maggiore per il lato singolo.

### Output
Restituisce:
- punteggio totale;
- dettagli per ciascun terminale.

### Significato
Permette di confrontare orientazioni candidate complete del MOSFET.

---

## Funzione `get_round_source_probe_scores(binary, bbox)`

### Scopo
Calcolare i probe vicini per simboli rotondi.

### Utilità
Serve per sorgenti e meter circolari.

---

## Funzione `get_round_source_far_probe_scores(binary, bbox)`

### Scopo
Calcolare i probe lontani per simboli rotondi.

### Utilità
Completa la misura “near” con la continuità più esterna del wire.

---

# 7. `image_ops.py`

## Ruolo del file

Contiene una utility minimale per contare foreground in una ROI.

## Funzione `img_count_foreground_pixels(binary, x1, y1, x2, y2)`

### Scopo
Contare quanti pixel foreground sono presenti in un rettangolo della binaria.

### Logica
- clippa la ROI ai bordi immagine;
- se la ROI è vuota ritorna 0;
- altrimenti usa `cv2.countNonZero(...)`.

### Significato
È la primitive fondamentale su cui si appoggiano quasi tutti i probe.

---

# 8. `io_utils.py`

## Ruolo del file

Gestisce il caricamento dei metadati YAML e la costruzione della binaria.

## Funzione `io_load_yaml(path)`

### Scopo
Leggere un file YAML e restituirne il contenuto deserializzato.

---

## Funzione `io_load_class_metadata(class_terminals_path)`

### Scopo
Caricare il file dei metadati classi e convertire le chiavi in interi.

### Utilità
Permette di indicizzare i metadati direttamente con `class_id`.

---

## Funzione `img_build_foreground_binary(image_bgr)`

### Scopo
Convertire l’immagine BGR in una binaria foreground/background.

### Procedura
1. conversione a grayscale;
2. thresholding Otsu;
3. inversione binaria (`THRESH_BINARY_INV`).

### Significato
I simboli neri e i fili diventano foreground bianco su fondo nero, il che semplifica tutte le operazioni successive di conteggio.

---

# 9. `debug_draw.py`

## Ruolo del file

Disegna la visualizzazione di debug dei risultati del passo 03.

## Funzione `draw_terminals(image_bgr, components, terminals)`

### Scopo
Produrre un’immagine annotata con:
- bbox dei componenti;
- terminali stimati;
- label di componenti e terminali.

### Logica
1. copia l’immagine;
2. definisce colori e parametri grafici;
3. definisce una helper interna `draw_label(...)` che:
   - misura il testo,
   - disegna un rettangolo di sfondo semi-trasparente,
   - disegna il bordo,
   - stampa il testo;
4. per ogni componente:
   - disegna il bbox;
   - disegna l’etichetta con `instance_id`;
   - se disponibile, aggiunge l’iniziale dell’orientazione stimata;
5. per ogni terminale:
   - disegna un cerchio rosso sul punto;
   - disegna la label del terminale (`display_terminal_id` se presente).

### Significato
Non modifica il risultato numerico, ma è fondamentale per la verifica qualitativa del comportamento della pipeline.

---

# Considerazioni architetturali finali

## Separazione dei livelli

Il codice del passo 03 è organizzato in livelli abbastanza netti:

### 1. Livello di orchestrazione
- `03_estimate_terminals.py`

Gestisce input, output, loop sui file, salvataggio e debug image.

### 2. Livello per-componente
- `processor.py`

Trasforma un singolo componente in terminali concreti.

### 3. Livello di dispatch strategico
- `dispatcher.py`

Sceglie la strategia corretta in base ai metadati.

### 4. Livello di strategia geometrica
- `strategies_basic.py`

Implementa le euristiche principali per 1 e 2 terminali.

### 5. Livello di geometria fine
- `geometry.py`

Localizza i punti terminali nel dettaglio.

### 6. Livello di misura locale
- `probes.py`
- `image_ops.py`

Fornisce i punteggi elementari usati dalle strategie.

### 7. Livello I/O e visualizzazione
- `io_utils.py`
- `debug_draw.py`

Gestisce caricamenti e render di debug.

---

## Filosofia generale del passo 03

La filosofia del codice non è “indovinare il terminale dal solo bbox”, ma usare una cascata di decisioni:

1. **metadato di classe**  
   decide quale famiglia di strategia usare;

2. **probe locali sui lati**  
   decidono quali lati sono realmente connessi;

3. **localizzazione side-peak o strutturata**  
   decide dove cade davvero il terminale lungo quel lato;

4. **semantica finale**  
   assegna eventualmente nomi come positivo/negativo o gate/source/drain.

Questa struttura rende il sistema:
- più interpretabile;
- più debuggabile;
- più facile da estendere per nuove classi simboliche.

---

## Limiti dichiarativi di questo documento

Questo testo descrive in dettaglio i file forniti, ma il comportamento completo del passo 03 dipende anche dai moduli esterni chiamati qui, in particolare:

- semantica dei due terminali;
- semantica dei tre terminali;
- strategie opamp;
- strategie per analog meter, transformer, connector e class `Terminal`.

Questi moduli andrebbero documentati in una seconda parte per ottenere una descrizione esaustiva dell’intero passo 03.

---

## Possibili estensioni del documento

La prossima estensione naturale di questa documentazione, per avere una base completa da tesi, è aggiungere:

1. `semantic_two_terminal.py`
2. `strategies_three_terminal.py`
3. `strategies_opamp.py`
4. `strategies_structured_symbols.py`
5. `strategies_connector.py`
6. `strategies_terminal_class.py`
7. `config.py`
8. `class_terminals_v1.yaml`

Con questi file si può arrivare a una descrizione davvero completa dell’intero passo 03, sia dal lato algoritmico sia dal lato configurativo.

---

# Estensione del documento: semantica dei due terminali e simboli strutturati

Questa estensione aggiunge la descrizione di due moduli fondamentali che nel documento precedente erano solo citati ma non ancora spiegati nel dettaglio:

- `semantic_two_terminal.py`
- `strategies_structured_symbols.py`

Questi due file sono particolarmente importanti per la tesi perché coprono due aspetti centrali del passo 03:

1. **come si assegna il significato semantico ai terminali già localizzati**, cioè la polarità o la direzione nei componenti a due terminali;
2. **come si trovano i terminali in simboli strutturati** come analog meter e transformer, nei quali il terminale non coincide semplicemente con il centro di un lato del bounding box.

In questa seconda parte il focus viene quindi spostato soprattutto su:

- il passaggio da **terminale geometrico** a **terminale semantico**;
- il ruolo delle **euristiche locali sulla grafica interna** del simbolo;
- la distinzione fra **riconoscimento della posizione del terminale** e **riconoscimento della sua polarità o funzione**.

---

# 10. Come il passo 03 trova i terminali e poi assegna la polarità

## Separazione fra geometria e semantica

Nel passo 03 è fondamentale distinguere due problemi diversi.

### Primo problema: trovare il terminale
In questa fase il sistema cerca di rispondere a domande del tipo:

- il componente è orientato in orizzontale o in verticale?
- i terminali stanno a sinistra/destra oppure sopra/sotto?
- il terminale cade nel centro del lato oppure in una posizione spostata?
- il simbolo ha 1, 2, 3 o più terminali?

Questa parte è gestita soprattutto da:

- `dispatcher.py`
- `strategies_basic.py`
- `geometry.py`
- `strategies_structured_symbols.py`

### Secondo problema: capire il significato del terminale
Una volta che il terminale geometrico è stato localizzato, si può chiedere:

- quale dei due lati è il **positivo** e quale il **negativo**?
- qual è il lato **marker side** e quale l’altro?
- nel current source, quale lato rappresenta la direzione `current_to` e quale `current_from`?
- nel diodo, quale terminale è `anode` e quale `cathode`?

Questa parte è gestita da `semantic_two_terminal.py`.

## Filosofia generale del sistema

Il sistema non cerca di fare tutto in un solo passaggio. La pipeline reale è invece:

1. **decidere la struttura del simbolo**;
2. **localizzare i terminali geometrici**;
3. **analizzare la grafica interna del simbolo**, se la classe lo richiede;
4. **mappare i lati trovati in ruoli semantici**.

Questo significa che un terminale nasce prima come:

- `left`, `right`, `top`, `bottom`

poi, solo se la classe lo richiede, viene arricchito in:

- `positive`, `negative`
- `anode`, `cathode`
- `current_from`, `current_to`

Questa separazione è molto importante, perché rende il sistema:

- più interpretabile;
- più facile da debuggare;
- più modulare;
- meno fragile, dato che una semantica sbagliata non implica necessariamente una localizzazione geometrica sbagliata.

---

# 11. `semantic_two_terminal.py`

## Ruolo del file

Questo modulo si occupa della **semantica dei componenti a due terminali**. In altre parole, prende terminali già localizzati geometricamente e prova a capire **quale significato assegnare loro** in base alla grafica interna del simbolo. fileciteturn21file1

Il modulo non decide dove si trovano i terminali: parte dal presupposto che il sistema abbia già stimato:

- l’orientazione del simbolo (`horizontal` o `vertical`);
- i terminali geometrici con il loro `relative_position`.

A quel punto prova a capire, per esempio:

- quale lato corrisponde al **marker**;
- quale lato è il **positivo**;
- quale lato è il **negativo**;
- quale lato è la **coda** e quale la **punta** della corrente;
- quale lato è `anode` e quale `cathode`.

## Architettura interna del modulo

Il modulo è organizzato in tre livelli.

### Livello 1: estrazione di score dalla grafica interna
Sono le funzioni che misurano la struttura del simbolo, ad esempio:

- proiezioni lungo x o y;
- gruppi di picchi vicini ai bordi;
- massa interna nella metà sinistra/destra o alta/bassa;
- riconoscimento del segno `+`.

### Livello 2: scelta del lato marker
Queste funzioni confrontano i punteggi dei due lati candidati e scelgono quale lato interpretare come “marker side”.

### Livello 3: scrittura dei campi semantici nei terminali
Alla fine il modulo aggiorna i terminali con campi come:

- `semantic_terminal_name`
- `semantic_terminal_id`
- `semantic_slot`
- `semantic_confidence`
- `semantic_resolution_mode`
- `semantic_evidence_type`
- `semantic_resolution_debug`

In più aggiorna anche i campi `display_name` e `display_terminal_id`, cioè quelli che poi vengono mostrati nei debug e nel JSON finale.

---

## Costanti iniziali

### `DEFAULT_FALLBACK_SIDE`
Questo dizionario stabilisce quale lato usare come fallback se l’evidenza grafica è nulla o troppo debole:

- per simboli orizzontali → `left`
- per simboli verticali → `top` fileciteturn21file1

Il significato è semplice: se non ci sono abbastanza informazioni, si applica una convenzione coerente con l’orientazione.

---

## Funzione `_group_consecutive_indices(indices)`

### Scopo
Raggruppare indici consecutivi in sottoliste continue.

### Perché serve
Quando una proiezione produce più pixel forti vicini tra loro, non conviene trattarli come picchi separati. È più corretto aggregarli in un unico gruppo continuo.

### Dove viene usata
Serve soprattutto nelle funzioni che lavorano con proiezioni e gruppi di bordo, come l’analisi del diodo e del condensatore polarizzato.

---

## Funzione `_bbox_dims(bbox, binary)`

### Scopo
Restituire una versione robusta del bbox con:

- coordinate clampate all’immagine;
- larghezza;
- altezza.

### Output
Ritorna:

- `x1, y1, x2, y2, width, height`

### Utilità
Evita di ripetere più volte il calcolo di dimensioni e clamp.

---

## Funzione `_count_nonzero(binary, x1, y1, x2, y2)`

### Scopo
Contare i pixel foreground in una ROI rettangolare.

### Differenza rispetto a `img_count_foreground_pixels`
Questa funzione svolge lo stesso ruolo concettuale, ma qui è locale al modulo semantico. Serve quando si vuole mantenere il codice della semantica autosufficiente per piccole ROI interne.

---

## Funzione `_projection_side_scores(binary, bbox, orientation, center_band_ratio=0.42, edge_inset_ratio=0.08)`

### Scopo
Calcolare un punteggio di proiezione per i due lati compatibili con l’orientazione del simbolo. fileciteturn21file1

### Idea geometrica
L’idea è questa:

- si ritaglia una ROI interna al simbolo;
- si restringe la ROI lasciando un piccolo inset dai bordi;
- si prende una banda centrale del simbolo;
- si proietta il foreground:
  - su asse `x` se il simbolo è orizzontale;
  - su asse `y` se il simbolo è verticale.

### Caso orizzontale
Se il simbolo è orizzontale:

- si costruisce una ROI interna centrata verticalmente;
- si calcola la proiezione per colonne;
- si divide la proiezione in metà sinistra e metà destra;
- si prende il massimo della metà sinistra come `left_score`;
- si prende il massimo della metà destra come `right_score`.

### Caso verticale
Se il simbolo è verticale:

- si costruisce una ROI interna centrata orizzontalmente;
- si calcola la proiezione per righe;
- si divide in metà superiore e inferiore;
- si prendono `top_score` e `bottom_score`.

### Significato
Questa funzione è utile quando il marker o la piastra lunga occupano una fascia più piena del simbolo.

### Dove viene usata
È usata per esempio per la batteria (`battery_positive_from_long_plate`).

---

## Funzione `_projection_edge_group_scores(binary, bbox, orientation, center_band_ratio=0.42, edge_inset_ratio=0.08)`

### Scopo
Versione più raffinata della precedente, che non si limita a guardare il massimo di metà simbolo, ma analizza i **gruppi di proiezione forti vicini ai bordi**. fileciteturn21file1

### Logica dettagliata
1. costruisce una ROI interna, come nella funzione precedente;
2. calcola la proiezione su asse `x` o `y`;
3. trova il valore massimo della proiezione;
4. costruisce una soglia relativa `keep_threshold`;
5. tiene gli indici sopra soglia;
6. li raggruppa in gruppi consecutivi;
7. valuta il primo gruppo e l’ultimo gruppo, cioè quelli più vicini ai due bordi opposti.

### Funzione interna `edge_group_score(group, side)`
Per ogni gruppo calcola un punteggio che combina:

- massimo del gruppo;
- lunghezza del gruppo;
- distanza dal bordo.

In pratica un gruppo è più forte se:

- è intenso;
- è abbastanza esteso;
- è vicino al bordo coerente con il lato che si sta testando.

### Significato
Questa funzione è più adatta quando il marker ha forma compatta e aderente a uno dei due lati, come:

- barra del diodo;
- marker del condensatore polarizzato.

---

## Funzione `_diode_bar_scores(score_map, orientation)`

### Scopo
Specializzare i punteggi della proiezione edge-group per riconoscere la **barra sottile del diodo**, cioè il lato del catodo. fileciteturn21file1

### Logica
La funzione parte da `score_map`, che contiene:

- `projection_values`
- `kept_groups`

Poi:

1. per ogni gruppo calcola il suo centro;
2. definisce una funzione `bar_score(group)` che premia:
   - gruppo intenso;
   - gruppo sottile;
   - gruppo vicino al centro ma ancora vicino a un bordo;
3. seleziona il gruppo migliore;
4. decide se quel gruppo è più a sinistra/destra oppure più in alto/in basso;
5. forza il lato del gruppo migliore ad avere score maggiore;
6. salva nel debug:
   - gruppo scelto;
   - centro scelto;
   - lato scelto.

### Significato elettrico
Nel diodo il lato con la barra è il **cathode**. Quindi questa funzione serve a capire quale dei due terminali dovrà ricevere il ruolo di `cathode`.

---

## Funzione `_plus_marker_scores_by_side(binary, bbox, orientation)`

### Scopo
Riconoscere il lato del simbolo in cui si trova il segno `+`, cioè il lato **positivo** delle voltage source. fileciteturn21file1

Questa è una delle funzioni più importanti per la polarità.

### Sottofunzione `plus_like_patch_score(cx, cy, half_w, half_h)`
Questa funzione valuta una piccola patch rettangolare centrata in `(cx, cy)` e prova a stimare quanto quella patch assomigli a un `+`.

#### Passaggi interni
1. ritaglia la ROI della patch;
2. calcola:
   - proiezione per righe;
   - proiezione per colonne;
3. ricava:
   - `row_max`
   - `col_max`;
4. misura un indice di equilibrio `balance`:
   - il `+` ha sia una barra orizzontale sia una verticale;
   - il `-` tende ad avere quasi solo la barra orizzontale;
5. misura il supporto nella colonna centrale della patch, per catturare la barretta verticale del `+`;
6. combina questi termini in uno score finale.

### Caso orizzontale
Se il simbolo è orizzontale:

- si usano due patch, una a sinistra e una a destra, nella parte alta del simbolo;
- si confrontano `left_score` e `right_score`.

### Caso verticale
Se il simbolo è verticale:

- si usano due patch strette e interne, una in alto e una in basso;
- si confrontano `top_score` e `bottom_score`.

### Scelta progettuale importante
Nel caso verticale le patch sono volutamente:

- più strette;
- più interne;
- meno sensibili al bordo esterno dell’ellisse e ai wire verticali.

Questo serve ad evitare che il segno `-` o i fili adiacenti alterino la decisione.

### Near tie bias
Se `top_score` e `bottom_score` sono quasi pari, la funzione aggiunge un piccolo bonus al `top_score`. Questo riflette una convenzione osservata nel dataset, in cui il `+` delle voltage source verticali è quasi sempre disegnato sopra.

### Significato
Questa funzione non assegna ancora i ruoli finali, ma produce lo score da cui si dedurrà quale lato è il `positive`.

---

## Funzione `_inner_half_mass_scores(binary, bbox, orientation)`

### Scopo
Misurare la massa di foreground nelle due metà interne del simbolo. fileciteturn21file1

### Caso orizzontale
Divide la ROI interna in:

- metà sinistra;
- metà destra.

### Caso verticale
Divide la ROI interna in:

- metà superiore;
- metà inferiore.

### Significato
Questa funzione è adatta ai current source, dove la freccia interna fa accumulare più massa nella metà verso cui punta la freccia.

---

## Funzione `_choose_side(score_map, positive_key, negative_key, fallback_side)`

### Scopo
Scegliere quale dei due lati candidati è il lato marker. fileciteturn21file1

### Logica
1. legge i due score candidati;
2. sceglie quello maggiore come `chosen`;
3. l’altro diventa `other`;
4. calcola una confidence normalizzata:

\[
\text{confidence} = \frac{best - second}{best + second}
\]

5. se entrambi gli score sono nulli, usa il fallback side e assegna confidence minima `0.2`;
6. se la confidence è troppo bassa, marca l’evidenza come `orientation_fallback`.

### Output
Ritorna:

- lato scelto;
- lato opposto;
- confidence;
- tipo di evidenza.

### Significato
Questa funzione è il punto in cui un semplice confronto di score viene trasformato in una decisione formalizzata.

---

## Funzione `_set_term_semantic_fields(term, semantic_name, semantic_slot, confidence, resolution_mode, evidence_type, debug)`

### Scopo
Scrivere dentro un terminale tutti i campi semantici standard. fileciteturn21file1

### Campi aggiornati
La funzione imposta:

- `semantic_terminal_name`
- `semantic_terminal_id`
- `semantic_slot`
- `semantic_confidence`
- `semantic_resolution_mode`
- `semantic_evidence_type`
- `semantic_resolution_debug`
- `display_name`
- `display_terminal_id`

### Famiglie semantiche
In più, se il nome semantico è in certe classi speciali, aggiunge:

- `semantic_polarity` e `semantic_role_family = "polarity"` per:
  - `positive`
  - `negative`
  - `anode`
  - `cathode`

oppure:

- `semantic_direction` e `semantic_role_family = "current_direction"` per:
  - `current_from`
  - `current_to`

### Significato
Questa funzione è il punto in cui il terminale passa da “punto geometrico” a “entità semantica”.

---

## Funzione `_assign_pair_roles(...)`

### Scopo
Assegnare i ruoli semantici a una coppia di terminali, dati:

- il lato marker;
- il lato opposto;
- i nomi semantici da usare.

### Logica
1. costruisce un mapping fra `relative_position` e ruolo semantico;
2. scorre i terminali;
3. per ogni terminale che corrisponde a uno dei lati attesi, invoca `_set_term_semantic_fields(...)`.

### Significato
È il meccanismo standard per propagare la decisione “lato marker vs lato altro” sui due terminali reali del componente.

---

## Funzione `_assign_strategy_result(terminals, orientation, meta, score_map, resolution_mode)`

### Scopo
Applicare il flusso standard completo di risoluzione semantica per una strategia a due terminali. fileciteturn21file1

### Passaggi
1. in base all’orientazione decide quali sono i due lati candidati:
   - orizzontale → `left/right`
   - verticale → `top/bottom`
2. richiama `_choose_side(...)`;
3. costruisce un dizionario `debug` con:
   - orientazione;
   - scores;
   - lato marker scelto;
   - lato opposto;
   - confidence;
   - tipo di evidenza;
4. legge da `meta["semantic_roles"]` i nomi semantici dei due lati;
5. richiama `_assign_pair_roles(...)`.

### Significato
Questa funzione standardizza il comportamento delle varie strategie, così ogni classe speciale deve solo produrre gli score corretti.

---

## Funzione `resolve_two_terminal_semantics(binary, bbox, orientation, terminals, meta)`

### Scopo
È la **funzione pubblica principale** del modulo. Decide quale strategia semantica applicare a un componente a due terminali. fileciteturn21file1

### Condizioni di uscita immediata
Se:

- `semantic_terminal_strategy` non è definita;
- i terminali sono meno di due;
- l’orientazione non è `horizontal` o `vertical`;

allora la funzione non modifica nulla e ritorna i terminali originali.

### Strategie supportate

#### 1. `diode_cathode_from_bar`
Usa:

- `_projection_edge_group_scores(...)`
- `_diode_bar_scores(...)`
- `_assign_strategy_result(...)`

##### Significato fisico
Riconosce il lato con la barra del diodo e lo mappa su `cathode`, mentre l’altro diventa `anode`.

---

#### 2. `polarized_capacitor_positive_from_marker`
Usa:

- `_projection_edge_group_scores(...)`
- `_assign_strategy_result(...)`

##### Significato fisico
Riconosce il lato con il marker grafico del condensatore polarizzato e lo assegna come `positive`. L’altro diventa `negative`.

---

#### 3. `battery_positive_from_long_plate`
Usa:

- `_projection_side_scores(...)`
- `_assign_strategy_result(...)`

##### Significato fisico
La piastra lunga della batteria corrisponde al lato positivo. Questa strategia confronta i due lati usando la struttura delle proiezioni interne.

---

#### 4. `voltage_source_positive_from_plus_marker`
Usa:

- `_plus_marker_scores_by_side(...)`
- `_assign_strategy_result(...)`

##### Significato fisico
Riconosce il segno `+` nel simbolo della sorgente di tensione e assegna quel lato come `positive`. L’altro diventa `negative`.

##### Importanza pratica
Questa è la strategia che gestisce la **polarità delle voltage source** e quindi è una delle più importanti per la tesi.

---

#### 5. `current_source_direction_from_arrow`
Questa strategia è leggermente diversa dalle precedenti. Usa:

- `_inner_half_mass_scores(...)`
- `_choose_side(...)`

ma costruisce un debug specifico con:

- `selected_arrow_head_side`
- `selected_arrow_tail_side`

poi assegna i ruoli in base a `semantic_roles`.

##### Significato fisico
Nel current source il lato verso cui punta la freccia è il lato `current_to`, mentre l’altro è `current_from`.

##### Perché usa la massa interna
Perché la freccia dentro il cerchio genera una distribuzione di foreground sbilanciata nella metà del simbolo verso cui punta.

---

### Conclusione sul file `semantic_two_terminal.py`

Questo modulo è il cuore della **polarità e della semantica nei componenti a 2 terminali**. Il suo ruolo può essere riassunto così:

- **non trova i terminali da zero**;
- parte da terminali già trovati geometricamente;
- guarda il disegno interno del simbolo;
- produce una decisione su quale lato sia il marker;
- scrive il risultato nel JSON finale in modo strutturato e debuggabile.

---

# 12. `strategies_structured_symbols.py`

## Ruolo del file

Questo modulo gestisce simboli che non possono essere trattati bene con le strategie generiche a lato/bbox, perché hanno una struttura interna particolare e richiedono una localizzazione dei terminali più “modellata” sul simbolo. fileciteturn21file2

Nel codice fornito qui vengono gestiti in particolare:

- `Analog Meter`
- `Transformer`

Questi due casi hanno una caratteristica comune:

- il terminale non coincide con il semplice centro di un lato del bbox;
- la posizione terminale dipende da elementi grafici interni o da una struttura rigida del simbolo.

---

## Funzione `_group_close_indices(indices, max_gap=1)`

### Scopo
Raggruppare indici vicini, non necessariamente perfettamente consecutivi.

### Differenza rispetto ad altre grouping function
Qui è consentito un gap massimo configurabile. Questo è utile quando le scansioni producono picchi quasi contigui ma separati da piccoli buchi.

---

## Funzione `_select_peak_coord(coords, scores, keep_ratio=0.58, min_score=4)`

### Scopo
Selezionare una coordinata ottima lungo una scansione 1D. fileciteturn21file2

### Logica
1. se non ci sono coordinate o score, ritorna stato nullo;
2. se il massimo è nullo, usa il centro;
3. altrimenti tiene gli score sopra soglia;
4. raggruppa gli indici tenuti;
5. sceglie il gruppo migliore usando:
   - somma degli score;
   - massimo score;
   - lunghezza del gruppo;
6. ritorna la coordinata centrale del gruppo.

### Significato
È una versione generale del meccanismo di side-peak, riutilizzata per scansioni specifiche di meter e transformer.

---

## Funzione `_find_structured_inner_box(binary, bbox, min_size, ratio_min, ratio_max, extent_min, prefer_square=False)`

### Scopo
Trovare un rettangolo interno al bbox che corrisponda alla struttura centrale del simbolo. fileciteturn21file2

### Logica
1. ritaglia la ROI del bbox;
2. estrae i contorni con OpenCV;
3. per ogni contorno calcola il rettangolo contenitore;
4. filtra per:
   - dimensione minima;
   - rapporto di forma ammesso;
   - extent minimo (cioè quanto il contorno riempie il suo bbox);
5. opzionalmente premia forme più quadrate;
6. sceglie il box migliore.

### Dove viene usata
Nel meter analogico, per trovare il corpo interno del quadrante e restringere la ricerca dei post.

---

## Funzione `_find_circular_holes(binary, box, min_area=25.0, max_area=320.0)`

### Scopo
Trovare piccoli fori circolari all’interno di una box, che nei meter analogici corrispondono ai post di collegamento. fileciteturn21file2

### Logica
Per ogni contorno nella ROI:

1. calcola bbox locale del contorno;
2. filtra per dimensione;
3. filtra per rapporto larghezza/altezza;
4. filtra per area;
5. calcola il perimetro e la circolarità;
6. filtra per circolarità minima;
7. calcola posizione normalizzata nel box;
8. scarta candidati troppo vicini ai bordi o fuori dalle zone plausibili;
9. misura anche metriche ad anello con `_measure_meter_post_ring(...)`.

Alla fine ordina i candidati e ne tiene un piccolo numero dei migliori.

### Significato
È una funzione cruciale per il meter: cerca i due fori/occhielli veri dei terminali.

---

## Funzione `_count_roi_nonzero(roi, xa, ya, xb, yb)`

### Scopo
Contare il foreground in una ROI locale già estratta.

### Utilità
Helper usato da varie funzioni del meter.

---

## Funzione `_masked_fill_ratio(roi, mask)`

### Scopo
Calcolare quanta parte del foreground riempie una maschera specifica.

### Significato
Serve per misurare quanto una regione circolare si comporti come:

- centro pieno;
- anello;
- alone esterno.

---

## Funzione `_measure_meter_post_ring(binary, cx, cy, radius)`

### Scopo
Misurare se attorno a un punto esiste davvero una struttura “ad anello”, tipica di un post del meter. fileciteturn21file2

### Idea
Un post reale del meter ha spesso:

- centro relativamente vuoto;
- anello più pieno;
- alone esterno non troppo invadente.

### Logica
1. ritaglia una ROI attorno al candidato;
2. costruisce quattro maschere concentriche:
   - centro;
   - inner;
   - outer;
   - halo;
3. calcola:
   - `center_fill_ratio`
   - `annulus_fill_ratio`
   - `halo_fill_ratio`
4. combina questi valori in `ring_score`.

### Significato
Più il candidato assomiglia a un anello con centro relativamente vuoto, più è plausibile che sia un post vero.

---

## Funzione `_compute_meter_candidate_quality(candidate)`

### Scopo
Combinare più metriche in un quality score complessivo del candidato post.

### Termini usati
Il quality score combina:

- `ring_score`
- `annulus_fill_ratio`
- `center_fill_ratio`
- `halo_fill_ratio`
- `best_support`
- bonus se il candidato arriva da `contour_hole`

### Significato
Serve a ordinare i candidati e preferire quelli che sembrano davvero post fisici.

---

## Funzione `_is_valid_meter_post_candidate(candidate)`

### Scopo
Filtrare i candidati post deboli o troppo improbabili.

### Logica
Usa soglie diverse per:

- candidati da `contour_hole`
- candidati da `hough_circle`

### Significato
Rende più severa la selezione dei candidati prima della scelta finale della coppia.

---

## Funzione `_hough_circle_support(roi, cx, cy, radius)`

### Scopo
Misurare quanto un cerchio Hough abbia supporto di wire o grafica sui lati circostanti.

### Utilità
Aiuta a capire da quale lato il candidato è più plausibile e quanto è ben supportato.

---

## Funzione `_choose_same_edge_pair(circles, box_w, box_h)`

### Scopo
Scegliere due cerchi che stanno plausibilmente sulla stessa faccia del simbolo.

### Significato
I due post del meter, in certe orientazioni, stanno sulla stessa faccia del simbolo ruotato. La funzione cerca una coppia coerente con questo layout.

---

## Funzione `_find_hough_post_circles(binary, box)`

### Scopo
Trovare candidati circolari con la Hough Transform, come fallback o complemento rispetto ai contorni. fileciteturn21file2

### Logica
1. ritaglia la ROI;
2. sfoca l’immagine con Gaussian blur;
3. applica `cv2.HoughCircles`;
4. per ogni cerchio trovato:
   - misura il supporto con `_hough_circle_support(...)`;
   - calcola area, raggio, distanza dai bordi;
   - deduplica candidati vicini;
5. ordina i migliori.

### Significato
Questa funzione è un secondo canale di detection dei post, utile quando i contorni non bastano.

---

## Funzione `_merge_meter_post_candidates(candidates)`

### Scopo
Fondere candidati molto vicini provenienti da fonti diverse.

### Regola di fusione
Se due candidati sono quasi coincidenti:

- si preferisce il `contour_hole` rispetto all’Hough circle;
- a parità di tipo si usa un criterio basato su `ring_score`, `support`, `area`.

### Significato
Evita duplicati e rende la lista candidati più pulita.

---

## Funzione `_eligible_edges_for_point(cx, cy, box_w, box_h)`

### Scopo
Calcolare per un candidato quali lati del box sono geometricamente plausibili come lati associati a quel punto.

### Logica
1. misura la distanza del punto dai quattro bordi;
2. trova la distanza minima;
3. tiene tutti i bordi entro una soglia relativa a quella minima.

### Significato
Un candidato può essere compatibile con uno o più lati del simbolo, non necessariamente con uno solo.

---

## Funzione `_build_meter_post_candidates(binary, search_box, holes)`

### Scopo
Costruire la lista completa dei candidati post del meter. fileciteturn21file2

### Fasi
1. parte dai `holes` trovati per contorno;
2. per ciascuno costruisce un candidato con:
   - posizione;
   - raggio;
   - supporto;
   - lati eleggibili;
   - metriche ring;
3. aggiunge anche i candidati trovati con Hough circles;
4. fonde i candidati vicini;
5. annota il supporto esterno reale su ciascun lato con `_annotate_meter_candidate_external_support(...)`;
6. calcola `quality_score`;
7. ordina i candidati;
8. se ci sono almeno due candidati forti, ritorna quelli forti; altrimenti ritorna i migliori in generale.

### Significato
È il vero costruttore della popolazione di candidati per i terminali del meter.

---

## Funzione `_meter_edge_scan_scores(binary, box)`

### Scopo
Misurare il supporto dei wire esterni nelle varie zone dei lati del meter.

### Logica
Divide idealmente i lati in coppie di regioni:

- top-left e top-right;
- bottom-left e bottom-right;
- left-top e left-bottom;
- right-top e right-bottom.

Per ognuna usa funzioni di scansione esterna (`_scan_external_wire_x_in_range`, `_scan_external_wire_y_in_range`).

### Significato
Queste misure servono per capire su quale faccia del meter sono davvero presenti i due terminali.

---

## Funzione `_score_meter_edge_pair(edge, cand_a, cand_b, scan_pair)`

### Scopo
Valutare una coppia di candidati come possibili post reali su uno stesso lato del meter.

### Componenti del punteggio
Il punteggio combina:

- distanza principale lungo il lato;
- allineamento trasversale;
- supporto delle scansioni esterne;
- qualità ad anello;
- bonus per candidati da contour hole;
- bonus se il lato migliore del candidato coincide con il lato testato.

### Significato
La coppia ideale è:

- ben separata lungo il lato giusto;
- ben allineata;
- supportata da wire esterni;
- composta da candidati circolari credibili.

---

## Funzione `_meter_candidate_side_support(binary, box, candidate, side)`

### Scopo
Misurare il supporto esterno del candidato rispetto a un lato specifico.

### Significato
Aiuta a dire “questo candidato è davvero collegato dal lato sinistro / destro / alto / basso?”.

---

## Funzione `_annotate_meter_candidate_external_support(binary, search_box, candidate)`

### Scopo
Aggiungere al candidato il supporto misurato su tutti i lati e determinare:

- `best_side`
- `second_side`
- relativi punteggi.

### Extra
Se un lato vince chiaramente, la funzione restringe `eligible_edges` a quel lato.

### Significato
Questo passaggio trasforma un punto “circolare” in un candidato coerente con un lato di connessione reale.

---

## Funzione `_score_meter_opposite_pair(binary, box, side_a, cand_a, side_b, cand_b)`

### Scopo
Valutare una coppia di candidati che si trova su lati opposti del meter.

### Uso
È un fallback estremo, da usare solo se non si trova una buona coppia sulla stessa faccia.

### Significato
Serve a coprire casi molto anomali o layout non standard.

---

## Funzione `_select_meter_post_pair(binary, search_box, candidates, allow_opposite=False)`

### Scopo
Selezionare la coppia finale di post del meter.

### Strategia
1. calcola i punteggi di scansione esterna;
2. prova prima solo combinazioni `same-edge`;
3. valuta ogni coppia con `_score_meter_edge_pair(...)`;
4. applica bonus di elongazione in certe geometrie molto allungate;
5. mantiene la migliore coppia;
6. opzionalmente, se permesso e necessario, tenta il fallback `opposite_edges`.

### Significato
Questa è la funzione di decisione finale sulla coppia di post.

---

## Funzioni `_opposite_side(side)`, `_meter_face_side_scores(binary, box)`, `_detect_meter_post_side(binary, box)`

### Scopo complessivo
Capire su quale faccia del meter si trova il quadrante e, di conseguenza, su quale faccia opposta devono trovarsi i post.

### `_opposite_side(side)`
Restituisce semplicemente il lato opposto.

### `_meter_face_side_scores(binary, box)`
Misura la densità interna del meter in quattro zone:

- top
- bottom
- left
- right

### `_detect_meter_post_side(binary, box)`
1. calcola i face scores;
2. trova il lato del quadrante (`dial_side`), cioè la faccia più “piena” della grafica interna;
3. deduce `post_side` come faccia opposta.

### Significato
Se il quadrante sta sopra, i post tenderanno a stare sotto; se il quadrante sta a sinistra, i post tenderanno a stare a destra, e così via.

---

## Funzione `_meter_anchor_layout(box, post_side)`

### Scopo
Dato il lato atteso dei post, costruire due anchor teorici dove i terminali dovrebbero trovarsi. fileciteturn21file2

### Output
Restituisce:

- `anchors`
- `orientation`
- `relative_positions`
- `axis`

### Significato
Il meter viene trattato con un template geometrico: una volta noto il lato dei post, si definiscono due posizioni attese coerenti con quella faccia.

---

## Funzione `_refine_meter_post_near_anchor(binary, box, anchor, expected_side)`

### Scopo
Raffinare localmente un anchor del meter cercando il miglior punto vicino che assomigli a un post reale.

### Logica
1. definisce una finestra di ricerca attorno all’anchor;
2. per ogni punto della finestra misura:
   - `ring_score`
   - fill ratios
   - supporto sul lato atteso
   - distanza dall’anchor;
3. combina tutto in uno score;
4. sceglie il miglior punto;
5. se lo score è troppo debole, torna all’anchor iniziale.

### Significato
Questo è il passaggio che rende il template adattivo al simbolo reale.

---

## Funzione `_snap_meter_post_to_candidate(candidates, anchor_point, box, expected_side, used_points=None)`

### Scopo
Agganciare l’anchor raffinato a uno dei candidati post trovati prima.

### Logica
Per ogni candidato:

- evita di riusare candidati già scelti;
- scarta candidati troppo lontani dall’anchor;
- combina:
  - quality score;
  - source bonus;
  - coerenza col lato atteso;
  - ring score;
  - distanza normalizzata.

### Significato
L’idea è: prima si costruisce un anchor teorico + refine locale, poi lo si fa “snap” sul miglior candidato reale compatibile.

---

## Funzione `detect_analog_meter_terminals(meta, binary, bbox)`

### Scopo
API pubblica che trova i due terminali dell’analog meter. È una delle funzioni più importanti del file. fileciteturn21file2

### Passaggi completi
1. prende il bbox detection clampato;
2. prova a trovare un inner box strutturato con `_find_structured_inner_box(...)`;
3. cerca fori circolari con `_find_circular_holes(...)`;
4. se i fori non bastano e c’era inner box, allarga la ricerca al detection box;
5. costruisce i candidati con `_build_meter_post_candidates(...)`;
6. determina lato quadrante e lato post con `_detect_meter_post_side(...)`;
7. costruisce due anchor template con `_meter_anchor_layout(...)`;
8. per ciascun anchor:
   - fa refine locale con `_refine_meter_post_near_anchor(...)`;
   - tenta snap a un candidato con `_snap_meter_post_to_candidate(...)`;
9. ordina coerentemente i due post;
10. costruisce `terminals_def` con:
    - `t1`
    - `t2`
    - `relative_position`
    - `point`
11. ritorna anche un debug molto ricco.

### Significato
Il meter analogico non viene risolto per semplice lato del bbox: viene risolto come **simbolo strutturato con template, candidati e refine locale**.

---

## Funzione `_scan_external_wire_y_in_range(...)`

### Scopo
Scansionare una porzione verticale del lato sinistro o destro di un simbolo e trovare la coordinata `y` in cui il wire esterno è più forte.

### Logica
1. costruisce l’intervallo di scansione;
2. per ogni `cy` costruisce una finestra esterna+interna sul lato richiesto;
3. conta il foreground;
4. seleziona la coordinata migliore con `_select_peak_coord(...)`.

### Utilità
È usata soprattutto per il transformer.

---

## Funzione `_scan_external_wire_x_in_range(...)`

### Scopo
Versione duale della precedente, ma per i lati top e bottom, restituendo una coordinata `x`.

### Utilità
Anche questa è fondamentale per il transformer.

---

## Funzione `detect_transformer_terminals(meta, binary, bbox)`

### Scopo
Trovare i quattro terminali del transformer analizzando i wire esterni nelle quattro zone/quadranti del simbolo. fileciteturn21file2

### Idea di base
Il transformer è visto come simbolo a quattro quadranti terminali possibili:

- alto-sinistra
- alto-destra
- basso-sinistra
- basso-destra

Per ogni quadrante il sistema decide se il terminale è meglio rappresentato come:

- lato sinistro/destro
- oppure lato alto/basso

in base ai wire realmente presenti.

### Passaggi completi
1. clampa il detection box;
2. calcola dimensioni e regioni di scansione:
   - `top_range`
   - `bottom_range`
   - `left_range`
   - `right_range`
3. esegue otto scansioni:
   - quattro verticali ai lati sinistro/destro;
   - quattro orizzontali in alto/in basso;
4. se alcune coppie di coordinate risultano incoerenti, applica fallback ad anchor di quadrante;
5. calcola due score globali:
   - `left_right_score`
   - `top_bottom_score`
6. costruisce per ciascun terminale (`t1`, `t2`, `t3`, `t4`) due opzioni candidate;
7. sceglie per ciascun terminale l’opzione con score migliore, con una preferenza globale coerente col layout dominante;
8. conta quanti terminali sono finiti su lati verticali vs orizzontali;
9. deduce `estimated_orientation` del transformer;
10. costruisce `terminals_def` e il debug finale.

### Significato
Il transformer non viene trattato come “quattro punti fissi”, ma come **quattro terminali scelti localmente nei quadranti**, con decisione guidata dal wire esterno reale.

---

# 13. Sintesi finale focalizzata su terminali e polarità

## Come il sistema trova i terminali

Il ritrovamento dei terminali avviene in cascata.

### Caso semplice: componenti ordinari
Per un componente standard a 1 o 2 terminali:

1. si decide l’orientazione o il lato connesso;
2. si decide quali lati del bbox ospitano i terminali;
3. si localizza il punto finale sul lato:
   - centro del lato;
   - anchor ratio;
   - side peak.

In questo gruppo rientrano, per esempio:

- GND;
- resistori semplici;
- componenti a due terminali generici;
- molte sorgenti rotonde.

### Caso intermedio: componenti con simbolo interno informativo
Per componenti come:

- capacitor;
- LED;
- variable resistor;
- round source;

la localizzazione dell’orientazione usa già la grafica interna del simbolo, non solo il bbox.

### Caso avanzato: simboli strutturati
Per componenti come:

- analog meter;
- transformer;
- opamp;
- connettori;
- simboli a tre terminali;

si usa una procedura più complessa fatta di:

- template geometrici;
- scansioni orientate;
- analisi di candidati;
- refine locale;
- fallback strutturati.

## Come il sistema assegna la polarità

La polarità non viene dedotta dai wire esterni, ma dalla **grafica interna del simbolo**.

### Voltage source
Si cerca il segno `+` nelle patch coerenti con l’orientazione. Il lato con lo score `plus-like` maggiore diventa `positive`; l’altro diventa `negative`. fileciteturn21file1

### Polarized capacitor
Si cercano gruppi di proiezione forti vicini al bordo, compatibili con il marker del condensatore polarizzato. Il lato del marker diventa `positive`. fileciteturn21file1

### Battery
Si confronta la struttura interna per riconoscere la piastra lunga. Il lato della piastra lunga viene marcato come `positive`. fileciteturn21file1

### Diode
Si cerca la barra del diodo. Il lato della barra diventa `cathode`, l’altro `anode`. fileciteturn21file1

### Current source
Si usa la massa interna della freccia. Il lato verso cui punta la freccia viene assegnato come lato di arrivo della corrente (`current_to`), l’altro come `current_from`. fileciteturn21file1

## Punto chiave per la tesi

Il concetto più importante da sottolineare è questo:

> il passo 03 non usa una singola euristica universale, ma una famiglia di strategie specializzate che separano la **localizzazione geometrica del terminale** dalla **sua interpretazione semantica**.

Questa è la ragione per cui il sistema riesce a essere:

- flessibile su simboli molto diversi;
- spiegabile in fase di debug;
- estendibile a nuove classi;
- adatto a una pipeline di tipo tesi/prototipo, in cui conta molto poter motivare ogni decisione.

---

# 14. Completamento finale del documento

Nelle sezioni seguenti il documento viene completato con i moduli che chiudono davvero il ragionamento del passo 03:

- `strategies_three_terminal.py`
- `strategies_opamp.py`
- `config.py`
- `class_terminals_v1.yaml`

Questi file sono quelli che permettono di spiegare in modo completo:

- come vengono scelti orientazione e terminali nei simboli a tre terminali;
- come vengono attivati e rifiniti i pin opzionali degli opamp;
- quali costanti regolano tutte le euristiche del sistema;
- come il file YAML descrive in modo dichiarativo il comportamento di ogni classe.


---

# 15. `strategies_three_terminal.py`

## Ruolo del file

Questo modulo è il cuore del trattamento dei simboli a **tre terminali**. In pratica prende un componente per cui il dispatcher ha già deciso di usare la strategia `three_terminal_by_side_pattern` e si occupa di due problemi distinti:

1. **capire qual è l’orientazione corretta del simbolo**;
2. **assegnare, se richiesto, la semantica ai tre terminali**, cioè base/emettitore/collettore oppure gate/source/drain. 

Il file lavora quindi in stretta relazione con:

- `geometry.py`, che localizza i punti terminali coerenti con una certa orientazione;
- `probes.py`, che fornisce score locali e score specifici per MOSFET;
- `class_terminals_v1.yaml`, che specifica quali classi usano questa strategia e quali ruoli semantici vanno assegnati.

Dal punto di vista logico, il modulo implementa la pipeline seguente:

1. pulizia locale del binary attorno al componente;
2. generazione di più orientazioni candidate;
3. scoring di queste orientazioni;
4. scelta dell’orientazione finale;
5. eventuale risoluzione semantica dei tre terminali.

---

## Funzione `_build_three_terminal_support_binary(binary, bbox)`

### Scopo
Costruire una versione “ripulita” della binaria locale per i simboli a tre terminali.

### Motivazione
MOSFET e transistor sono spesso accompagnati da scritte molto vicine al bbox, per esempio:

- `M1`, `M2`
- `Q1`, `Q2`
- etichette di rete
- numeri o simboli vicini

Questi elementi non fanno parte del corpo del simbolo, ma possono alterare i probe laterali e i punteggi di orientazione.

### Logica dettagliata
1. si clampa il bbox all’immagine;
2. si costruisce una ROI più ampia del bbox, aggiungendo un margine definito da:
   - `THREE_TERMINAL_TEXT_SUPPRESS_MARGIN_RATIO`
   - `THREE_TERMINAL_TEXT_SUPPRESS_MARGIN_MIN`;
3. sulla ROI si calcolano i connected components;
4. si definisce una **seed box centrale** interna al bbox vero, cioè una regione che con alta probabilità cade sul simbolo e non sul testo;
5. si raccolgono le label dei componenti connessi che intersecano questa seed box;
6. si costruisce una nuova ROI in cui si mantengono solo quei connected components;
7. si reinserisce la ROI pulita nella binaria globale.

### Significato
Questa funzione non modifica la geometria del componente, ma produce una binaria di supporto più affidabile per tutte le decisioni successive. È quindi una forma di **soppressione locale del testo** mirata ai simboli a tre terminali.

---

## Funzione `get_three_terminal_working_binary(binary, bbox)`

### Scopo
Restituire il binary effettivamente da usare nel resto della pipeline tre-terminal.

### Logica
- se `THREE_TERMINAL_TEXT_SUPPRESS_ENABLE` è attivo, usa `_build_three_terminal_support_binary(...)`;
- altrimenti ritorna semplicemente il binary originale.

### Significato
Questa è l’API pubblica che collega il meccanismo di pulizia locale con il resto del sistema.

---

## Funzione `candidate_mosfet_orientations_from_bbox(bbox)`

### Scopo
Restituire l’insieme delle orientazioni candidate per il MOSFET.

### Output
Ritorna sempre:

- `left`
- `right`
- `top`
- `bottom`

### Significato
Nel codice attuale non fa pruning in base al bbox: lascia tutte e quattro le orientazioni possibili, così la scelta finale dipende dagli score reali.

---

## Funzione `score_three_terminal_orientation_by_terminal_points(binary, bbox, orientation, single_weight)`

### Scopo
Assegnare uno score a una orientazione candidata di un simbolo a tre terminali usando i **punti terminali concreti** previsti da quella orientazione.

### Logica
1. prende il template di lati associato a `orientation` tramite `THREE_TERMINAL_TEMPLATES`;
2. per ogni `relative_position` del template richiama `geom_terminal_point_three_terminal(...)`;
3. costruisce così una tripletta di terminali candidati;
4. passa questi terminali a `score_mosfet_candidate_terminals(...)`, che assegna uno score complessivo considerando:
   - supporto locale;
   - supporto direzionale;
   - penalità ortogonali;
   - maggior peso al lato singolo.

### Significato
La cosa importante è che l’orientazione non viene valutata solo sui lati teorici, ma sui **punti terminali realmente localizzati**. Questo rende la scelta molto più robusta.

---

## Funzione `score_mosfet_orientation_by_terminal_points(binary, bbox, orientation)`

### Scopo
Versione specializzata della funzione precedente per il MOSFET.

### Differenza
Richiama `score_three_terminal_orientation_by_terminal_points(...)` fissando `single_weight` al valore di configurazione `MOSFET_SINGLE_TERMINAL_WEIGHT`.

### Significato
Nei MOSFET il lato singolo (gate) è particolarmente importante nella decisione di orientazione, quindi pesa di più nel punteggio complessivo.

---

## Funzione `_is_specular_pair(a, b)`

### Scopo
Capire se due orientazioni sono speculari.

### Regola
Le coppie considerate speculari sono:

- `{left, right}`
- `{top, bottom}`

### Utilità
Viene usata nei tie-break, quando due orientazioni quasi equivalenti differiscono solo per la specularità.

---

## Funzione `_resolve_specular_tie(side_a, side_b, lateral_scores, single_side_scores)`

### Scopo
Risolvere un pareggio quasi perfetto fra due orientazioni speculari.

### Casi
- per la coppia `left/right` usa, se disponibile, `lateral_scores`, cioè lo score specializzato del gate laterale dei MOSFET;
- per la coppia `top/bottom` usa gli score già calcolati del lato singolo.

### Significato
Questa funzione esiste per evitare che piccoli rumori numerici facciano oscillare l’orientazione fra due versioni speculari del medesimo simbolo.

---

## Funzione `get_bjt_base_side_scores(binary, bbox)`

### Scopo
Calcolare uno score specifico per capire se la **base** di un transistor BJT/NPN sta a sinistra oppure a destra.

### Logica
1. definisce una banda verticale centrale interna al bbox;
2. costruisce due strip strette interne:
   - una a sinistra;
   - una a destra;
3. misura il foreground in entrambe.

### Significato
La base dell’NPN genera spesso una massa grafica più marcata su uno dei due lati. Questo score viene usato come override per non confondere la base con i due rami emettitore/collettore.

---

## Funzione `_count_three_terminal_semantic_probe(binary, cx, cy, half_w, half_h)`

### Scopo
Contare il foreground in una piccola ROI centrata in un punto candidato.

### Utilità
È una primitive usata dai probe semantici per capire su quale ramo cade la freccia.

---

## Funzione `_three_terminal_arrow_branch_probe(binary, bbox, orientation)`

### Scopo
Stimare quale dei due rami della coppia ortogonale contiene la freccia semantica.

### Idea geometrica
Dopo aver fissato l’orientazione del simbolo, il sistema sa che esiste:

- un lato singolo;
- una coppia di lati opposti ortogonali.

La freccia di source/emitter cade tipicamente su uno di questi due rami. La funzione costruisce quindi due punti probe, uno per ciascun ramo, in posizioni coerenti con l’orientazione del simbolo.

### Esempi
- se il lato singolo è `left`, la coppia è `top/bottom` e i probe vengono messi nella metà destra del bbox;
- se il lato singolo è `right`, i probe vengono messi nella metà sinistra;
- se il lato singolo è `top` o `bottom`, i probe cadono nella parte bassa o alta, e distinguono `left/right`.

### Significato
È il probe semantico generico per capire quale dei due rami è il **ramo con freccia**.

---

## Funzione `_mosfet_arrow_branch_probe(binary, bbox, orientation)`

### Scopo
Versione specializzata del probe semantico per MOSFET.

### Perché serve
Nel MOSFET la freccia non sempre è catturata bene dal solo probe esterno. Per questo il codice combina:

- `outer_scores`, ottenuti col probe generico;
- `inner_scores`, ottenuti con un probe più vicino al canale interno.

### Output
Produce `combined_scores` come combinazione pesata:

- `70%` supporto interno
- `30%` supporto esterno

### Significato
Questa è una scelta importante: il MOSFET viene letto non solo dal bordo del bbox, ma anche dalla grafica più interna dove spesso la freccia è meglio visibile.

---

## Funzione `_npn_arrow_branch_probe(binary, bbox, orientation)`

### Scopo
Probe specifico per NPN, più vicino al trunk centrale.

### Motivazione
Nel transistor NPN la freccia dell’emettitore è spesso più vicina al tronco del simbolo che all’estremo più lontano del bbox. Il probe generico può quindi essere ambiguo. 

### Logica
1. per orientazioni `left/right` costruisce un `cx` vicino al trunk, usando:
   - `NPN_ARROW_BRANCH_TRUNK_LEFT_RATIO`
   - `NPN_ARROW_BRANCH_TRUNK_RIGHT_RATIO`;
2. costruisce i due probe `top` e `bottom` nelle posizioni verticali attese;
3. misura il foreground in entrambe le ROI.

### Significato
Questa funzione è il fallback intelligente per distinguere correttamente `E` e `C` nei transistor NPN.

---

## Funzione `_semantic_pair_confidence(pair_scores, arrow_branch_position, other_branch_position)`

### Scopo
Calcolare la confidence con cui uno dei due rami viene interpretato come ramo con freccia.

### Formula
La confidence è la differenza normalizzata fra il punteggio del ramo scelto e quello dell’altro ramo.

### Significato
Questa confidence viene poi scritta nel terminale semantico e permette di capire quanto la decisione sia forte o debole.

---

## Funzione `resolve_three_terminal_semantics(binary, bbox, orientation, terminals, meta)`

### Scopo
È la funzione pubblica che assegna i ruoli semantici ai tre terminali. 

### Struttura generale
La funzione:

1. legge `semantic_terminal_strategy` dal metadata YAML;
2. verifica che l’orientazione sia valida e che ci siano almeno tre terminali;
3. costruisce la coppia dei rami ortogonali rispetto al lato singolo;
4. opzionalmente costruisce una binaria ripulita di supporto;
5. applica la strategia semantica corretta.

### Strategia `three_terminal_gate_only`
Questa strategia assegna solo il ruolo del lato singolo, senza tentare di distinguere i due rami ortogonali.

Uso tipico:
- componenti in cui interessa sapere il gate/base ma non è affidabile distinguere sempre gli altri due.

### Strategia `mosfet_gate_with_optional_source_drain`
Questa è la strategia dei MOSFET.

#### Logica
1. il lato singolo prende sempre il nome definito in `semantic_roles.single_side`, cioè tipicamente `G`;
2. sui due rami ortogonali si applica `_mosfet_arrow_branch_probe(...)`;
3. il ramo con score maggiore diventa `arrow_branch`, tipicamente `S`;
4. l’altro diventa `other_branch`, tipicamente `D`;
5. però l’assegnazione dei ruoli `S/D` avviene solo se la confidence supera `MOSFET_ARROW_BRANCH_CONFIDENCE_MIN`.

#### Significato
Questo significa che il sistema può anche decidere di assegnare solo il gate, lasciando i due altri terminali geometrici ma non semanticamente nominati se l’evidenza non è abbastanza forte.

### Strategia `npn_emitter_from_arrow_branch`
Questa è la strategia del transistor NPN.

#### Logica
1. calcola un primo score con `_three_terminal_arrow_branch_probe(...)`;
2. se l’orientazione è `left/right`, calcola anche il probe NPN dedicato `_npn_arrow_branch_probe(...)`;
3. confronta le confidence dei due metodi;
4. se il probe NPN è sufficientemente buono o comunque migliore del generico in caso ambiguo, usa il probe NPN;
5. assegna:
   - `single_side` → `B`
   - `arrow_branch` → `E`
   - `other_branch` → `C`

#### Significato
Questa è la logica che consente di correggere i casi in cui emettitore e collettore vengono invertiti pur avendo un’orientazione geometrica corretta.

---

## Funzione `strategy_detect_three_terminal_orientation(binary, bbox, class_name="", default_orientation="right")`

### Scopo
Stimare l’orientazione di un simbolo a tre terminali. È la funzione più importante del file.

### Pipeline completa
La funzione segue una cascata a più livelli.

#### Livello 0: binary di supporto
Se attivata, usa la soppressione del testo con `_build_three_terminal_support_binary(...)`.

#### Livello 1: score del lato singolo
- per MOSFET usa `get_mosfet_single_side_scores(...)`;
- per gli altri simboli usa `get_local_terminal_probe_scores_center(...)`.

Per MOSFET calcola anche `lateral_scores` con `get_mosfet_lateral_gate_scores(...)`.

#### Livello 1b: override speciale per NPN
Per NPN usa `get_bjt_base_side_scores(...)` e, se la base sinistra/destra è abbastanza chiara, ritorna subito quella come orientazione del lato singolo.

#### Livello 2: validazione finale specifica per MOSFET
Per ogni orientazione candidata:
1. localizza i tre terminali coerenti con quella orientazione;
2. ne valuta il punteggio con `score_mosfet_orientation_by_terminal_points(...)`;
3. applica tie-break su coppie speculari;
4. se la migliore orientazione batte abbastanza la seconda, la seleziona.

#### Livello 2a: validazione finale generica sui punti terminali
Per le altre classi a tre terminali:
1. opzionalmente usa un prefiltro di asse (`horizontal` o `vertical`);
2. valuta le orientazioni candidate con `score_three_terminal_orientation_by_terminal_points(...)`;
3. applica eventuale bonus NPN per base lato sinistro/destra;
4. applica tie-break su orientazioni speculari;
5. se la migliore è sufficientemente migliore della seconda, la sceglie.

#### Livello 3: decisione solo dal lato singolo
Se la validazione puntuale non è conclusiva ma il lato singolo è molto più forte degli altri, l’orientazione viene fissata direttamente su quel lato.

#### Livello 4: fallback multi-anchor template
Se ancora c’è ambiguità, usa i `multi_scores` su ancoraggi multipli e valuta tutti i template di `THREE_TERMINAL_TEMPLATES`.

#### Livello 5: default finale
Se anche il fallback template non dà sufficiente evidenza, usa `default_orientation` dal YAML.

### Significato
Questa funzione mostra bene la filosofia del passo 03: non esiste una singola euristica per i tre terminali, ma una **cascata progressiva di regole** che va:

- da probe specifici e molto affidabili,
- a validazioni geometriche più costose,
- fino a fallback template e default YAML.

---

# 16. `strategies_opamp.py`

## Ruolo del file

Questo modulo si occupa di due cose:

1. scegliere l’orientazione dell’operational amplifier;
2. fare una rifinitura finale dei pin ausiliari superiori quando vicino all’opamp esiste un piccolo terminale esplicito di alimentazione.

Il file non localizza i punti terminali di basso livello da zero: quello è compito di `geometry.py`, in particolare `geom_terminal_point_opamp(...)`. Qui invece si lavora a un livello superiore:

- si confrontano orientazioni candidate;
- si decide quali terminali opzionali attivare;
- si effettua uno snap finale dell’aux superiore a terminali vicini, se presenti.

---

## Funzione `_get_opamp_orientation_defs(meta, orientation)`

### Scopo
Estrarre dal YAML la definizione dei terminali dell’opamp per una certa orientazione.

### Significato
Questa funzione è l’equivalente opamp di `_get_oriented_terminals(...)`, ma dedicato a un simbolo multi-terminale con struttura più ricca.

---

## Funzione `_score_opamp_terminal(binary, bbox, orientation, term_def)`

### Scopo
Valutare quanto un singolo terminale opamp sia compatibile con una data orientazione.

### Logica
1. localizza il terminale usando `geom_terminal_point_opamp(...)`;
2. legge il `relative_position` atteso;
3. misura il supporto direzionale del punto con `score_point_directional_support(...)`;
4. se il terminale è di tipo `output`, applica un peso maggiore `OPAMP_OUTPUT_WEIGHT`.

### Significato
L’idea è che, nell’opamp, l’uscita è spesso più informativa degli input per capire l’orientazione corretta, quindi pesa di più.

---

## Funzione `detect_opamp_terminals(meta, binary, bbox, default_orientation="right")`

### Scopo
Stimare l’orientazione dell’opamp e decidere quali terminali opzionali attivare.

### Pipeline
#### Fase 1: score delle orientazioni candidate
Per ciascuna orientazione fra:

- `right`
- `left`
- `top`
- `bottom`

la funzione:
1. prende la definizione dei terminali da YAML;
2. estrae solo i terminali **mandatory**, cioè quelli senza `optional: true`;
3. calcola per ciascuno uno score con `_score_opamp_terminal(...)`;
4. somma questi score in `orientation_scores`.

#### Fase 2: scelta dell’orientazione
- si ordina le orientazioni per score;
- si prende la migliore e la seconda migliore;
- se la migliore non vince con sufficiente margine (`OPAMP_ORIENTATION_MARGIN`), si usa il `default_orientation` del YAML;
- altrimenti si accetta la migliore.

#### Fase 3: attivazione dei terminali opzionali
Una volta scelta l’orientazione:
1. si scorrono tutti i terminali definiti in quella orientazione;
2. i terminali mandatory vengono sempre attivati;
3. i terminali opzionali vengono localizzati con `geom_terminal_point_opamp(...)`;
4. si controlla `point_debug["aux_detected"]`;
5. solo quelli effettivamente rilevati vengono aggiunti alla lista finale dei terminali attivi.

### Significato
L’opamp non è sempre uguale: può avere solo i tre pin obbligatori (`in1`, `in2`, `out`) oppure anche pin opzionali di supply. Questa funzione fa proprio questa distinzione.

---

## Funzione `snap_opamp_top_aux_to_nearby_terminal(components, binary)`

### Scopo
Rifinire il terminale `aux1` superiore degli opamp orizzontali (`right/left`) quando, sopra l’opamp, esiste un piccolo terminale variabile vicino. 

### Motivazione
In molti schemi il pin di supply superiore dell’opamp è collegato a un piccolo terminale separato, ad esempio `Vcc`, `Vdd` o simili. La localizzazione puramente interna dell’aux può cadere correttamente sul ramo, ma non essere perfettamente allineata al terminale esplicito del circuito.

### Pipeline dettagliata
1. costruisce una lista dei candidati terminale prendendo tutti i componenti con `symbol_type == "variable_terminal"` che hanno un solo terminale;
2. scorre tutti i componenti cercando gli opamp (`class_id == 19`) con orientazione `right` o `left`;
3. per ogni opamp definisce una banda centrale in x e una regione alta sopra il simbolo;
4. seleziona i terminali variabili vicini che cadono in quella regione;
5. sceglie il terminale vicino migliore, minimizzando la distanza dal centro alto dell’opamp;
6. cerca il terminale `aux1` del componente;
7. se esiste anche il terminale di uscita `out`, tenta una proiezione geometrica dell’aux sulla diagonale verso l’output;
8. altrimenti rifinisce la y con `_opamp_refine_aux_y_to_diagonal(...)`;
9. aggiorna `x`, `y` e arricchisce `terminal_point_debug` con tutti i dettagli dello snap.

### Significato
Questa è una rifinitura di alto livello molto utile nei casi reali: collega il terminale ausiliario dell’opamp non solo alla geometria del triangolo, ma anche alla presenza di terminali espliciti vicini nel circuito.

---

# 17. `config.py`

## Ruolo del file

`config.py` raccoglie tutte le costanti numeriche che regolano il comportamento del passo 03. Non contiene logica decisionale, ma definisce i parametri di tutte le euristiche. fileciteturn22file0

Dal punto di vista della tesi, questo file è importante perché mostra che il sistema è costruito come un insieme di:

- strategie modulari;
- parametri espliciti e leggibili;
- soglie e pesi separati dal codice funzionale.

Questo rende il sistema più facile da tarare e soprattutto più spiegabile.

---

## Gruppo 1: debug e visualizzazione

### `SAVE_DEBUG_IMAGES`
Attiva o disattiva il salvataggio delle immagini di debug.

### `TERMINAL_RADIUS`
Raggio del pallino rosso disegnato sui terminali nelle immagini annotate.

---

## Gruppo 2: coarse side sampling

Queste costanti regolano il fallback grossolano basato su bande centrali ai lati del bbox.

### `SIDE_SAMPLE_THICKNESS`
Spessore della banda campionata fuori dal lato.

### `SIDE_CENTER_RATIO`
Ampiezza relativa della banda centrale del lato usata nel campionamento grossolano.

### `SIDE_SCORE_MIN_PIXELS`
Numero minimo di pixel foreground richiesto per considerare valido un lato nel fallback grossolano.

### `AXIS_SCORE_MARGIN`
Margine richiesto fra score orizzontale e verticale per scegliere un asse.

---

## Gruppo 3: geometria generica dei terminali

### `TERMINAL_OUTWARD_OFFSET`
Distanza con cui il punto terminale viene spostato all’esterno del bbox.

### `ASPECT_RATIO_THRESHOLD`
Soglia di rapporto altezza/larghezza oltre la quale un bbox viene considerato verticale od orizzontale nel fallback geometrico.

---

## Gruppo 4: probe locali per i due terminali generici

Queste costanti regolano le finestre di campionamento usate per capire su quali lati si collegano i componenti a due terminali.

### `TERMINAL_PROBE_OUT_LEN`, `TERMINAL_PROBE_INSET`
Definiscono quanto il probe esce dal bbox e quanto rientra nel bbox.

### `TERMINAL_PROBE_HALFSPAN_RATIO`, `TERMINAL_PROBE_HALFSPAN_MIN`, `TERMINAL_PROBE_HALFSPAN_MAX`
Definiscono la semiampiezza del probe in modo adattivo rispetto alla scala del simbolo.

### `TERMINAL_PROBE_AXIS_MARGIN`, `TERMINAL_PROBE_MIN_SIDE_SCORE`
Definiscono le soglie decisionali per scegliere l’asse di connessione.

### `SWITCH_ANCHOR_RATIOS`
Definisce gli anchor multipli usati per gli switch aperti, che spesso non hanno il terminale esattamente al centro del lato.

---

## Gruppo 5: classe `Terminal`

Questo gruppo contiene costanti dedicate ai simboli terminali di bordo, che possono avere uno o due lati attivi.

### Blocchi principali
- probe vicini (`TERMINAL_CLASS_PROBE_*`)
- decisione uno-vs-due terminali (`TERMINAL_CLASS_TWO_*`)
- bias legato alla vicinanza ai bordi (`TERMINAL_CLASS_BORDER_MARGIN`, `TERMINAL_BORDER_MARGIN_*`)
- probe lontani (`TERMINAL_CLASS_FAR_*`)
- soppressione di testo locale e selezione del core del simbolo
- bonus/penalità geometriche legate alla forma quasi quadrata del terminale

### Significato
Queste costanti rendono la classe `Terminal` molto più conservativa rispetto agli altri simboli, proprio perché spesso si trova sui bordi dell’immagine e può confondersi con etichette o frammenti grafici esterni.

---

## Gruppo 6: LED

Qui sono definite tutte le costanti per:

- i probe near del LED;
- i probe far;
- i margini decisionali near/far;
- il rapporto della banda centrale.

### Significato
Nel LED la grafica interna e le frecce luminose possono falsare i probe generici. Per questo il file di configurazione usa parametri più stretti e più mirati.

---

## Gruppo 7: tre terminali

Questo è uno dei blocchi più importanti del file.

### `THREE_TERMINAL_ANCHOR_RATIOS`, `THREE_TERMINAL_MIN_SIDE_SCORE`
Servono per la lettura multi-anchor dei lati dei simboli a tre terminali.

### `THREE_TERMINAL_TEMPLATES`
Definisce esplicitamente il template dei lati attesi per ogni orientazione:

- `left -> (left, top, bottom)`
- `right -> (right, top, bottom)`
- `top -> (top, left, right)`
- `bottom -> (bottom, left, right)`

Questa struttura è fondamentale perché rende dichiarativa anche la logica dei tre terminali.

### Blocchi di validazione finale
- `THREE_TERMINAL_POINT_VALIDATION_*`
- `THREE_TERMINAL_AXIS_PREFILTER_*`
- `THREE_TERMINAL_SINGLE_SIDE_*`

Queste costanti regolano:
- il peso del lato singolo;
- il prefiltro di asse;
- il margine con cui una orientazione deve battere la seconda.

### Blocchi di localizzazione fine
- `SIDE_PEAK_*`
- `THREE_TERMINAL_SINGLE_SCAN_*`
- `THREE_TERMINAL_OPPOSITE_*`

Servono a localizzare nel dettaglio i terminali singoli e la coppia ortogonale.

### Soppressione del testo per i tre terminali
- `THREE_TERMINAL_TEXT_SUPPRESS_ENABLE`
- `THREE_TERMINAL_TEXT_SUPPRESS_MARGIN_*`
- `THREE_TERMINAL_SEED_*`

Servono a costruire il support binary ripulito.

### Probe semantici del ramo con freccia
- `THREE_TERMINAL_ARROW_*`
- `THREE_TERMINAL_ARROW_CONFIDENCE_MIN`
- `MOSFET_ARROW_BRANCH_CONFIDENCE_MIN`
- `NPN_ARROW_BRANCH_*`

Regolano i probe che distinguono source/drain oppure emitter/collector.

---

## Gruppo 8: MOSFET

Queste costanti controllano:

- stima del lato singolo (gate);
- conferma near/far;
- probe interni per il gate laterale;
- tie-break laterale;
- validazione finale con punteggio dei terminali;
- penalità ortogonali.

### Significato
Il MOSFET è una delle classi più difficili del dataset. Il file di configurazione lo riflette chiaramente, perché dedica un blocco ampio e specifico a questa classe.

---

## Gruppo 9: round sources e meters

### Costanti principali
- `ROUND_SOURCE_PROBE_OUT_LEN`
- `ROUND_SOURCE_CENTER_BAND_RATIO`
- `ROUND_SOURCE_FAR_GAP`
- `ROUND_SOURCE_FAR_LEN`
- `ROUND_SOURCE_FAR_WEIGHT`
- `ROUND_SOURCE_MIN_SIDE_SCORE`
- `ROUND_SOURCE_AXIS_MARGIN`
- `ROUND_SOURCE_BBOX_RATIO_MARGIN`

### Significato
Questi parametri governano tutte le classi circolari a due terminali come:

- `Signal_Source`
- `Voltage_Source`
- `Current_Source`
- `Meter`

---

## Gruppo 10: OPAMP

Questo è il blocco più esteso del file.

### Sottogruppi principali
1. **slot di scansione** per input, output e supply;
2. **scoring orientazione**;
3. **attivazione pin opzionali**;
4. **fase mandatory-only**;
5. **fase AUX V1**: rilevamento dello stelo verticale;
6. **fase AUX V2**: refine y verso la diagonale;
7. **fase AUX V3**: refine x dello stelo;
8. **fase AUX V4**: maschera locale dei numeri interni;
9. **fase AUX V5**: snap al terminale vicino.

### Significato
Il fatto che l’opamp occupi così tanto spazio in `config.py` riflette la complessità reale del suo trattamento: è un simbolo multi-terminale con terminali obbligatori e opzionali, e richiede una pipeline strutturata in fasi.

---

# 18. `class_terminals_v1.yaml`

## Ruolo del file

Questo file è la descrizione **dichiarativa** delle classi di simboli. In pratica dice al codice:

- quanti terminali ha ogni classe;
- quale strategia usare per trovarli;
- quale orientazione di default assumere;
- quali siano le definizioni terminali per ogni orientazione;
- quali classi richiedono una semantica aggiuntiva. fileciteturn25file0turn26file4turn26file9

Dal punto di vista architetturale, il YAML è ciò che rende il sistema configurabile: il codice contiene gli algoritmi, il YAML decide **quale algoritmo applicare a quale classe**.

---

## Struttura generale di una classe nel YAML

Ogni blocco di classe può contenere i seguenti campi.

### `name`
Nome simbolico della classe.

### `symbol_type`
Macro-tipologia del simbolo, per esempio:

- `one_terminal`
- `two_terminal`
- `three_terminal`
- `multi_terminal`
- `variable_terminal`

### `use_for_terminals`
Specifica se quella classe deve essere processata nel passo 03.

### `use_for_masking`
Specifica se il simbolo deve comunque essere usato nelle fasi di masking o pulizia binaria.

### `terminal_strategy`
È il campo più importante: dice al dispatcher quale strategia usare, per esempio:

- `one_terminal_by_orientation`
- `two_terminal_by_connection_axis`
- `two_terminal_round_source`
- `two_terminal_led`
- `two_terminal_variable_resistor`
- `three_terminal_by_side_pattern`
- `analog_meter_by_posts`
- `transformer_external_wires`
- `opamp_by_orientation_and_optional_supply`
- `connector_by_projection`
- `terminal_auto_one_or_two` 

### `terminal_point_mode`
Opzionale. Se presente, forza il metodo di localizzazione del punto, ad esempio:

- `two_terminal_side_peak`
- `opamp_structured`
- `bbox_side_center`

### `semantic_terminal_strategy`
Specifica l’euristica semantica da applicare dopo la localizzazione geometrica, per esempio:

- `battery_positive_from_long_plate`
- `current_source_direction_from_arrow`
- `diode_cathode_from_bar`
- `polarized_capacitor_positive_from_marker`
- `voltage_source_positive_from_plus_marker`
- `mosfet_gate_with_optional_source_drain`
- `npn_emitter_from_arrow_branch`

### `semantic_roles`
Dizionario che mappa i ruoli astratti usati dal codice ai nomi finali da assegnare ai terminali.

### `default_orientation`
Orientazione usata come fallback quando gli score non sono abbastanza conclusivi.

### `orientations`
Dizionario che, per ogni orientazione, definisce i terminali attesi con:

- `name`
- `relative_position`
- eventuali campi aggiuntivi come `slot`, `terminal_role`, `optional`.

### `notes`
Campo descrittivo utile per ricordare particolarità della classe o modifiche recenti.

---

## Esempi importanti di classi YAML

### `Analog_Meter` (classe 0)
Usa `terminal_strategy: analog_meter_by_posts`. Questo indica che non va trattato come semplice simbolo a due terminali, ma con una procedura strutturata basata sui due post interni del meter. fileciteturn25file0

### `Battery` (classe 2)
Usa:
- `terminal_strategy: two_terminal_by_connection_axis`
- `semantic_terminal_strategy: battery_positive_from_long_plate`

Quindi prima trova i due terminali geometrici e poi assegna la polarità guardando quale piastra è più lunga. fileciteturn25file0

### `Current_Source` (classe 6)
Usa:
- `terminal_strategy: two_terminal_round_source`
- `semantic_terminal_strategy: current_source_direction_from_arrow`
- `semantic_roles: marker_side=current_to, other_side=current_from`

Questa è la descrizione dichiarativa della direzione della corrente. fileciteturn25file0

### `Diode` e `LED` (classi 7 e 12)
Condividono la semantica `diode_cathode_from_bar`, quindi il codice tratta il lato con la barra come `cathode` e l’altro come `anode`. fileciteturn25file0

### `Mosfet` (classe 16)
Usa:
- `terminal_strategy: three_terminal_by_side_pattern`
- `semantic_terminal_strategy: mosfet_gate_with_optional_source_drain`
- `semantic_roles: G / S / D`

Questo mostra bene la separazione fra orientazione, terminali geometrici e semantica finale. fileciteturn25file0

### `NPN_Transistor` (classe 18)
Usa:
- `terminal_strategy: three_terminal_by_side_pattern`
- `semantic_terminal_strategy: npn_emitter_from_arrow_branch`
- `semantic_roles: B / E / C`

Anche qui prima si localizzano i tre terminali come lati geometrici, poi si distinguono i ruoli elettrici. fileciteturn26file14

### `Operational_Amplifier` (classe 19)
Usa:
- `terminal_strategy: opamp_by_orientation_and_optional_supply`
- `terminal_point_mode: opamp_structured`

In più, per ogni orientazione, il YAML definisce:
- terminali `in1`, `in2`, `out`;
- terminali opzionali `aux1`, `aux2`;
- `slot` e `terminal_role` per ciascuno. fileciteturn26file14turn26file15

### `Polarized_Capacitor` (classe 20)
Usa `polarized_capacitor_positive_from_marker`, quindi il lato del marker grafico diventa `positive`. fileciteturn26file4

### `Signal_Source` (classe 23)
Usa `two_terminal_round_source` ma **non** ha una semantica di polarità. Questo riflette la scelta progettuale di lasciare il segnale come componente a due morsetti non polarizzato semanticamente. fileciteturn26file4

### `Terminal` (classe 26)
Usa `terminal_auto_one_or_two`, cioè una strategia dinamica che decide se il simbolo si comporta da terminale mono-lato oppure bi-lato. fileciteturn24file4

### `Transformer` (classe 28)
Usa `transformer_external_wires`, che attiva la localizzazione a quattro terminali basata sulle scansioni dei fili esterni. fileciteturn24file0

### `Voltage_Source` (classe 31)
Usa:
- `terminal_strategy: two_terminal_round_source`
- `semantic_terminal_strategy: voltage_source_positive_from_plus_marker`

Questa è la dichiarazione esplicita che la polarità deve essere recuperata leggendo il segno `+` interno al simbolo. fileciteturn24file0

---

# 19. Sintesi conclusiva dell’intero passo 03

A questo punto il passo `03_estimate_terminals` può essere descritto come una pipeline completa composta da quattro livelli.

## Livello A: configurazione dichiarativa
Il file `class_terminals_v1.yaml` specifica per ogni classe:

- la strategia da usare;
- le orientazioni ammesse;
- i terminali attesi;
- le eventuali semantiche aggiuntive. 

## Livello B: decisione geometrica
Il dispatcher e le strategie di orientazione stabiliscono:

- quanti terminali aspettarsi;
- su quali lati cercarli;
- quale orientazione del simbolo è più plausibile.

## Livello C: localizzazione fine
La geometria localizza i punti terminali veri e propri, usando:

- centro lato;
- anchor ratio;
- side peak;
- scan strutturate;
- template specifici per simboli complessi.

## Livello D: semantica
Solo dopo la localizzazione geometrica il sistema assegna ruoli come:

- `positive / negative`
- `anode / cathode`
- `current_from / current_to`
- `G / S / D`
- `B / E / C`

## Conclusione concettuale per la tesi

Il valore principale del passo 03 non è solo nel trovare i terminali, ma nel farlo in modo:

- **modulare**, perché classi diverse usano strategie diverse;
- **interpretabile**, perché ogni decisione produce score e debug;
- **estensibile**, perché nuove classi possono essere aggiunte soprattutto dal lato YAML;
- **coerente con la simbologia elettrica**, perché la semantica viene assegnata leggendo marker reali del simbolo e non convenzioni arbitrarie.

In questo senso il passo 03 costituisce il ponte fra la semplice object detection dei componenti e una rappresentazione del circuito molto più vicina alla sua struttura elettrica reale.
