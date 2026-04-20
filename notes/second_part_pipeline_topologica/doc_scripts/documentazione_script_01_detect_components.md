# Documentazione completa dello script `01_detect_components.py`

Questa documentazione descrive in modo sistematico la logica dello script `01_detect_components.py`, con particolare attenzione al **post-processing delle detection YOLO**, alle **regole euristiche** introdotte per correggere gli errori del modello e al ruolo di **ogni funzione** presente nel file.

---

# 1. Scopo generale dello script

Lo script realizza il **primo stadio della pipeline**: per ogni immagine di input carica il modello YOLO, esegue la detection dei simboli elettrici, applica una serie di regole di post-processing, salva un **JSON strutturato** con i componenti rilevati e produce anche un’immagine di debug con i bounding box.

In termini concettuali, il flusso è questo:

1. lettura immagine;
2. conversione in grayscale;
3. costruzione di una versione binaria foreground/background;
4. detection YOLO;
5. correzione di alcune classi ambigue;
6. secondo pass mirato su classi difficili;
7. aggiunta di componenti trovati con euristiche geometriche;
8. rimozione di conflitti e duplicati;
9. esportazione JSON e immagine debug.

---

# 2. Configurazione iniziale

## 2.1 Percorsi e dataset

Le variabili iniziali definiscono:

- la root del progetto;
- il dataset/pipeline attiva;
- la cartella di input;
- la cartella di output;
- il path del modello YOLO;
- il file YAML con i metadati delle classi.

## 2.2 Parametri di inferenza

I parametri principali sono:

- `IMG_SIZE = 1024`
- `CONF_THRES = 0.40`
- `IOU_THRES = 0.45`

## 2.3 Soglie specifiche per classe

Oltre alla soglia globale, alcune classi usano soglie dedicate tramite `CLASS_CONF_THRES`.

Nella versione attuale sono presenti soglie specifiche per:

- `Analog_Meter`
- `Battery`
- `Connector`
- `Inductor`
- `Lamp`
- `Memristor`
- `Switch`
- `Terminal`
- `Transformer`
- `Voltage_Source`

L’idea è semplice: alcune classi sono molto difficili e vanno tenute anche con confidenza più bassa, altre invece devono essere filtrate in modo più severo.

## 2.4 Secondo pass su classi difficili

La variabile `SECONDARY_CLASS_PREDICTION_SPECS` definisce un **secondo pass di inferenza** per classi problematiche.

In questa versione il secondo pass è attivo per:

- `Diode`
- `Connector`

Questo pass usa:

- immagine a risoluzione maggiore (`imgsz = 1536`);
- soglie più permissive in prediction;
- soglia finale di accettazione separata (`accept_conf`).

---

# 3. Utility geometriche di base

Queste funzioni non prendono decisioni semantiche sui simboli: servono come mattoni elementari per tutte le euristiche successive.

## `_clamp_bbox_to_image(box, image_shape)`

Riporta un bounding box dentro i limiti dell’immagine.  
Serve a evitare accessi fuori range quando si lavora su ROI locali.

## `_group_close_indices(indices, max_gap=1)`

Raggruppa indici vicini in gruppi contigui.  
È usata quando si analizzano proiezioni 1D per trovare picchi, barre o pin.

## `_merge_close_values(values, min_gap)`

Fonde coordinate troppo vicine tra loro.  
Serve a stabilizzare i centri trovati da proiezioni o cerchi, evitando doppi conteggi della stessa struttura.

## `_bbox_area(box)`

Calcola l’area del bounding box.

## `_bbox_intersection(box_a, box_b)`

Calcola l’area di intersezione tra due box.

## `_bbox_iou(box_a, box_b)`

Calcola l’Intersection over Union tra due box.  
È usata per capire quanto due detection coincidono.

## `_bbox_ioa(box_inner, box_outer)`

Calcola l’Intersection over Area di un box rispetto a un altro.  
È utile quando un box piccolo è contenuto quasi interamente dentro uno più grande.

## `_bbox_center(box)`

Restituisce il centro del bbox.  
È usata soprattutto per il filtraggio dei terminal annidati.

## `_point_in_box(point, box)`

Verifica se un punto cade dentro un bbox.  
Anche questa viene usata per rimuovere terminal falsi interni ad altri simboli.

---

# 4. Utility di analisi immagine

## `_count_hough_circles(image_gray, box, ...)`

Conta i cerchi presenti in una ROI usando `cv2.HoughCircles`.

È una funzione fondamentale per riconoscere oggetti con struttura circolare, per esempio:

- meter;
- signal source;
- switch con contatti circolari;
- connector con pin rotondi.

## `expand_led_bbox(box, image_shape)`

Allarga leggermente il bbox di un LED per includere le frecce luminose.  
Questo non modifica la classe, ma solo il bbox finale salvato nel JSON.

## `_component_areas_in_box(image_binary, box)`

Esegue connected components sulla ROI binaria e restituisce le aree delle componenti.

Questa informazione viene usata in molte euristiche:

- analog meter;
- signal source;
- memristor;
- LED;
- voltage source.

---

# 5. Helper geometrici per il `Connector`

Il `Connector` è uno dei simboli più difficili, perché può essere:

- verticale;
- orizzontale;
- stretto;
- con pin leggibili male;
- confuso con altri simboli strutturati.

Per questo nello script esiste un blocco dedicato.

## `_extract_connector_pin_centers(projection, axis_offset, axis_span, max_gap=6)`

Estrae i centri dei pin a partire da una proiezione monodimensionale.

L’idea è:

1. calcolare la proiezione di pixel attivi;
2. sogliare i picchi;
3. raggruppare gli indici vicini;
4. convertirli in coordinate reali;
5. fondere valori troppo vicini.

## `_find_connector_pin_circle_centers_vertical(image_gray, box)`

Fallback per connector verticali: cerca i pin usando i cerchi interni via Hough Transform.  
Serve quando la proiezione binaria non è sufficiente.

## `_find_connector_pin_centers_vertical(image_binary, box)`

Cerca i pin di un connector verticale usando due bande laterali strette.  
L’idea è che i pin di un connettore verticale si vedono bene vicino ai bordi laterali del simbolo.

## `_pick_best_three_centers(centers)`

Se vengono trovati troppi centri, seleziona la tripletta più plausibile in base a:

- regolarità della spaziatura;
- span totale.

## `_find_connector_pin_centers_horizontal(image_binary, box)`

Versione analoga per connettori orizzontali, usando bande superiore e inferiore.

## `_connector_spacing_regularity(centers)`

Misura quanto le distanze tra i pin sono regolari.  
Più il valore è basso, più la spaziatura è uniforme.

## `_count_connector_circles(image_gray, box)`

Conta i cerchi interni del connector con parametri adattivi.  
Serve come conferma supplementare della natura “multipin” del simbolo.

## `get_connector_layout(image_binary, box, image_gray=None)`

È la funzione centrale per il connector.

Restituisce una struttura con:

- `is_connector`
- `orientation`
- `pin_count`
- `pin_centers`
- `regularity`
- `circle_count`

La logica è:

1. scarta bbox quasi quadrati;
2. prova a leggere pin verticali e orizzontali;
3. usa i cerchi come fallback per i verticali;
4. calcola regolarità e numero di pin;
5. dichiara valido il connector solo se:
   - il numero di pin è plausibile;
   - la regolarità è buona;
   - la forma è coerente con verticale/orizzontale;
   - il numero di cerchi supporta l’ipotesi;
6. contiene anche un fallback “rilassato” per connector verticali stretti a 3 pin.

## `is_connector_like_bbox(image_binary, box, image_gray=None)`

È un semplice wrapper booleano attorno a `get_connector_layout(...)`.  
Rende più leggibile il codice nei blocchi di remap e soppressione.

---

# 6. Euristiche di classe per simboli ambigui

Questa è la parte più importante del post-processing: qui il sistema prova a correggere le confusioni tipiche di YOLO.

## `is_analog_meter_like_bbox(image_binary, box)`

Riconosce un analog meter sulla base di:

- rapporto d’aspetto quasi quadrato;
- presenza di bordo esterno marcato sui quattro lati;
- densità interna moderata;
- numero limitato di componenti interne.

Questa regola serve soprattutto a distinguere:

- `Analog_Meter`

da

- `Integrated_Circuit`
- `Meter`
- `Inductor`

quando la forma esterna e la grafica interna suggeriscono chiaramente un pannello analogico.

## `is_signal_source_like_bbox(image_gray, image_binary, box)`

Riconosce una sorgente di segnale circolare, tipicamente con sinusoide interna.

La logica usa:

- forma quasi circolare/quadrata;
- presenza del cerchio esterno;
- densità interna moderata;
- assenza di troppe linee dritte interne;
- numero ridotto di componenti centrali.

Questa funzione è usata per correggere i casi in cui YOLO classifica una `Signal_Source` come `Meter`.

## `is_memristor_like_bbox(image_binary, box)`

Riconosce il memristor usando caratteristiche geometriche del simbolo:

- bbox stretta e molto alta;
- densità ai lati;
- densità nella parte alta;
- densità centrale;
- poche connected components;
- una componente dominante sufficientemente grande.

Serve per correggere confusioni tra:

- `Mosfet`
- `Integrated_Circuit`

e

- `Memristor`.

## `is_switch_like_bbox(image_gray, box)`

Validator “strict” per lo switch.

Controlla:

- dimensioni minime plausibili;
- presenza di almeno 2 cerchi Hough;
- almeno 2 connected components grandi nella ROI binaria.

## `is_switch_like_bbox_relaxed(image_gray, box)`

Validator più permissivo per switch inclinati/aperti.

Richiede:

- bbox plausibile;
- almeno 2 cerchi Hough;
- presenza di una linea obliqua interna con angolo compatibile con la lama dello switch.

Questa funzione esiste per non perdere switch veri ma più difficili.

## `_extract_plate_peaks(projection, orthogonal_span)`

Estrae i picchi principali di una proiezione 1D associati alle piastre di batteria/capacitore.

## `classify_plate_symbol(image_binary, box)`

Distingue `Battery` da `Capacitor` analizzando:

- proiezioni di righe e colonne;
- picchi dominanti;
- rapporto tra le lunghezze delle piastre;
- eventuale struttura multisezione tipica delle batterie.

## `is_led_like_diode_box(image_binary, box)`

Verifica se un `Diode` sembra in realtà un `LED`.

La regola guarda nella ROI allargata e controlla la presenza di piccoli componenti compatibili con le frecce luminose, sul lato destro o sopra il simbolo principale.

## `is_voltage_source_like_bbox(image_binary, box)`

Valida le `Voltage_Source`.

Analizza la struttura interna del simbolo per riconoscere la coppia di marcatori tipo `+` e `-`, oppure una configurazione di piccole componenti coerente con la sorgente di tensione.

---

# 7. Ricerca di candidati strutturati nel binario

Questa parte non parte dalle classi YOLO, ma dalla **geometria del binario**.

## `_dedupe_candidate_boxes(candidates, max_overlap=0.55)`

Rimuove candidati strutturati duplicati o troppo sovrapposti, tenendo i più plausibili.

## `find_structured_symbol_candidates(image_gray, image_binary)`

Scansiona i contorni dell’immagine binaria e cerca due famiglie di candidati:

- `Analog_Meter`
- `Connector`

### Per gli `Analog_Meter`

La funzione richiede:

- bbox quasi quadrato;
- dimensioni grandi;
- alto extent;
- molti cerchi interni;
- poche componenti, ma con componenti medie significative.

### Per i `Connector`

Richiede:

- dimensioni compatibili;
- extent sufficiente;
- layout riconosciuto da `get_connector_layout(...)`;

poi assegna uno score basato su:

- extent;
- numero di pin;
- numero di cerchi;
- bonus per orientazione;
- bonus per regolarità.

## `_box_matches_candidate(box, candidate_box, min_iou=0.28, min_ioa=0.55)`

Verifica se una detection combacia con un candidato euristico.  
Viene usata nel remap e nell’aggiunta di simboli mancanti.

---

# 8. Remap e normalizzazione delle classi

## `remap_special_component(image_gray, image_binary, box, predicted_class_name, structured_candidates)`

Questa funzione è il cuore semantico del post-processing.  
Prende:

- la classe predetta da YOLO;
- il bbox;
- l’immagine grayscale e binaria;
- i candidati strutturati;

e decide se la classe va lasciata invariata oppure corretta.

### Regole di remap presenti

#### 1. `Integrated_Circuit -> Connector`

Se la detection `Integrated_Circuit` coincide con un candidato `Connector` oppure se `is_connector_like_bbox(...)` restituisce vero, la classe viene rimappata a `Connector`.

#### 2. `Meter -> Signal_Source`

Se una detection `Meter` soddisfa `is_signal_source_like_bbox(...)`, viene trasformata in `Signal_Source`.

#### 3. `{Meter, Integrated_Circuit, Inductor} -> Analog_Meter`

Se la detection combacia con un candidato `Analog_Meter`, oppure la forma soddisfa `is_analog_meter_like_bbox(...)`, la classe viene trasformata in `Analog_Meter`.

#### 4. `{Mosfet, Integrated_Circuit} -> Memristor`

Se la forma è coerente con memristor, la classe viene rimappata a `Memristor`.

#### 5. `Capacitor <-> Battery`

Il simbolo viene riclassificato in base alla struttura delle piastre letta da `classify_plate_symbol(...)`.

#### 6. `Diode -> LED`

Se il diodo presenta frecce luminose compatibili con `is_led_like_diode_box(...)`, viene rimappato a `LED`.

Se nessuna regola si applica, la classe resta invariata.

---

# 9. Costruzione del record di output

## `_build_component_record(...)`

Costruisce il dizionario standard di un componente da salvare nel JSON.

I campi principali sono:

- `class_id`
- `class_name`
- `model_class_name`
- `source_class_id`
- `source_class_name`
- `conf`
- `bbox`
- `symbol_type`
- `use_for_terminals`
- `use_for_masking`

Questo standard è importante perché rende omogeneo l’output anche per:

- classi remappate;
- classi aggiunte da euristica;
- classi trovate nel secondo pass.

---

# 10. Aggiunta di componenti mancanti trovati con euristiche

## `add_missing_structured_components(components, structured_candidates, class_meta, class_id_by_name)`

Questa funzione aggiunge simboli che YOLO potrebbe non avere visto ma che le euristiche geometriche hanno trovato con buona sicurezza.

Nella versione attuale può aggiungere:

- `Connector`
- `Analog_Meter`

Per ciascun candidato:

1. controlla se esiste già un componente simile;
2. se non esiste, costruisce un nuovo record euristico;
3. assegna una confidenza artificiale di default:
   - `Connector: 0.72`
   - `Analog_Meter: 0.58`

---

# 11. Soppressione dei conflitti

## `suppress_conflicting_components(components, image_binary, image_gray)`

Questa funzione risolve i casi in cui due detection occupano quasi la stessa regione ma rappresentano interpretazioni diverse dello stesso simbolo.

Per ogni coppia con forte overlap, applica regole specifiche.

### Regole presenti

#### `Analog_Meter` contro `{Integrated_Circuit, Meter, Inductor}`

Viene tenuto `Analog_Meter` e viene eliminata l’altra classe.

#### `Analog_Meter` contro `Connector`

Se il box analog meter è coerente con `is_analog_meter_like_bbox(...)`, oppure il box connector non è coerente con `is_connector_like_bbox(...)`, viene eliminato il `Connector`; altrimenti viene eliminato l’`Analog_Meter`.

#### `Connector` contro `{Meter, Signal_Source}`

Se il connector è poco allungato, viene considerato falso e soppresso.  
Questa regola serve a evitare connector quasi quadrati sopra simboli circolari.

#### `Connector` contro `Integrated_Circuit`

Viene eliminato `Integrated_Circuit`.

#### `LED` contro `Diode`

Viene eliminato `Diode`.

#### `Battery` contro `Capacitor`

La decisione viene presa usando `classify_plate_symbol(...)`; se la classificazione è incerta, si elimina quello con confidenza minore.

#### `{Battery, Capacitor}` contro `GND`

Se il `GND` è quasi completamente dentro l’altro simbolo, viene eliminato il `GND`.

---

# 12. Rimozione dei duplicati

## `dedupe_overlapping_same_class(components)`

Elimina duplicati della **stessa classe** quando l’overlap è molto forte.

La regola è:

- ordinare per confidenza decrescente;
- tenere il più sicuro;
- sopprimere i successivi con overlap alto.

---

# 13. Rimozione dei terminal annidati

## `suppress_nested_terminals(components)`

Rimuove detection di `Terminal` che in realtà sono parte grafica interna di simboli più grandi.

Le classi bloccanti sono:

- `Connector`
- `Switch`
- `Analog_Meter`
- `Meter`
- `Integrated_Circuit`

La regola elimina un terminal se:

- è quasi interamente contenuto nel simbolo grande;
- oppure il suo centro cade dentro il bbox dell’altro simbolo.

---

# 14. Gestione delle soglie

## `get_required_confidence(class_name)`

Restituisce la soglia di confidenza della classe:

- specifica, se presente in `CLASS_CONF_THRES`;
- altrimenti la soglia globale `CONF_THRES`.

## `get_model_inference_confidence(class_meta)`

Sceglie la soglia da dare al pass principale di YOLO.

La logica usa la **minima** soglia necessaria tra quelle delle classi abilitate, così il modello non scarta in partenza classi difficili che richiedono threshold bassi. Il filtraggio fine viene fatto dopo.

---

# 15. Secondo pass mirato su classi difficili

## `add_secondary_class_predictions(...)`

Questa funzione esegue un secondo pass di detection solo su classi selezionate in `SECONDARY_CLASS_PREDICTION_SPECS`, cioè:

- `Diode`
- `Connector`

La logica è:

1. per ogni classe target, esegue una nuova inferenza con `imgsz` più alta;
2. usa una soglia di prediction dedicata;
3. accetta solo box con confidenza sopra `accept_conf`;
4. applica di nuovo il remap;
5. per `Connector`, richiede anche `is_connector_like_bbox(...)`;
6. per `LED`, espande il bbox se necessario;
7. aggiunge le detection al set finale.

Questa funzione serve a recuperare classi che nel pass principale tendono a perdersi per risoluzione o dimensione del simbolo.

---

# 16. Filtro specifico per i `Terminal`

## `is_terminal_detection_valid(image_binary, bbox)`

I `Terminal` sono molto rumorosi e facili da confondere con piccoli dettagli grafici.

La funzione usa due set di probe:

- vicini;
- lontani.

La score finale per lato è:

\[
score(side) = near(side) + 0.8 \cdot far(side)
\]

La detection è considerata valida se:

- il punteggio migliore è almeno 18;
- oppure se il migliore è almeno 10 e il secondo almeno 5.

Questo serve a verificare che attorno al terminal ci sia davvero una connessione grafica coerente.

---

# 17. I/O e supporto ai metadati

## `load_yaml(path)`

Legge un file YAML.

## `load_class_metadata(class_terminals_path)`

Carica i metadati delle classi da `class_terminals_v1.yaml` e costruisce:

- `class_meta`
- `detect_class_ids`
- `terminal_class_ids`
- `masking_class_ids`

## `normalize_model_names(model_names)`

Normalizza `model.names` in un dizionario `class_id -> class_name`.

## `get_input_images()`

Recupera e ordina le immagini di input ammesse in base all’estensione.

---

# 18. Generazione dell’immagine di debug

## `draw_components(image_bgr, components)`

Disegna:

- bounding box;
- etichetta con `class_id`, `class_name`, `conf`;
- suffisso `T` o `M` a seconda del ruolo del simbolo.

Questa funzione non influisce sulla detection: serve solo a produrre un output visivo utile per la verifica qualitativa.

---

# 19. Funzione principale per una singola immagine

## `predict_components_on_image(image_path, model, detect_class_ids, model_names, class_meta)`

Questa è la funzione che orchestra tutta la pipeline su una singola immagine.

La sequenza è:

### 1. Preparazione immagine

- carica l’immagine;
- calcola `image_gray`;
- calcola `image_binary`;
- estrae i candidati strutturati con `find_structured_symbol_candidates(...)`.

### 2. Inferenza YOLO principale

Esegue `model.predict(...)` usando:

- `imgsz = IMG_SIZE`
- `conf = get_model_inference_confidence(class_meta)`
- `iou = IOU_THRES`
- classi abilitate del dataset.

### 3. Remap delle classi

Per ogni box:

- recupera la classe originale;
- applica `remap_special_component(...)`;
- traduce il nome di classe finale nel relativo `class_id`.

### 4. Filtro per confidenza

Scarta la detection se `conf < required_conf`.

### 5. Filtro sui `Terminal`

Applica `is_terminal_detection_valid(...)`.

### 6. Filtro sugli `Switch`

La logica attuale è:

- prova `is_switch_like_bbox(...)`;
- se fallisce, accetta solo se:
  - `conf >= 0.75`
  - e `is_switch_like_bbox_relaxed(...)` restituisce vero.

### 7. Filtro sulle `Voltage_Source`

Una `Voltage_Source` viene accettata solo se `is_voltage_source_like_bbox(...)` è vera.

### 8. Espansione del bbox dei `LED`

Se la classe finale è `LED`, viene usata `expand_led_bbox(...)`.

### 9. Aggiunta del componente

Il componente viene salvato con classe finale, classe sorgente, bbox e metadati.

### 10. Secondo pass

Dopo il primo giro, la funzione applica:

- `add_secondary_class_predictions(...)`
- `add_missing_structured_components(...)`
- `suppress_conflicting_components(...)`
- `dedupe_overlapping_same_class(...)`
- `suppress_nested_terminals(...)`

### 11. Costruzione dell’output

Infine restituisce:

- immagine BGR;
- dizionario JSON finale con dimensioni immagine, classi attive e lista componenti.

---

# 20. Entrypoint dello script

## `main()`

La funzione `main()`:

1. controlla che modello e YAML esistano;
2. crea le cartelle di output;
3. carica i metadati;
4. inizializza il modello YOLO;
5. legge tutte le immagini di input;
6. per ogni immagine chiama `predict_components_on_image(...)`;
7. salva il JSON;
8. salva, se richiesto, l’immagine di debug.

---

# 21. Sintesi del post-processing YOLO

Il post-processing dello script `01` non è un semplice filtro di confidenza. È una pipeline composta da più livelli.

## Livello 1 — normalizzazione e soglie

- soglia globale;
- soglie specifiche per classe;
- soglia minima per il pass principale.

## Livello 2 — remap delle classi

Corregge errori sistematici di YOLO, per esempio:

- `Meter -> Signal_Source`
- `Integrated_Circuit -> Connector`
- `Integrated_Circuit / Meter / Inductor -> Analog_Meter`
- `Mosfet / Integrated_Circuit -> Memristor`
- `Capacitor <-> Battery`
- `Diode -> LED`

## Livello 3 — validator specifici

Applica regole locali solo ad alcune classi più ambigue:

- `Terminal`
- `Switch`
- `Voltage_Source`

## Livello 4 — secondo pass dedicato

Recupera classi difficili con inferenza ad alta risoluzione:

- `Diode`
- `Connector`

## Livello 5 — aggiunta euristica di simboli strutturati

Aggiunge:

- `Connector`
- `Analog_Meter`

quando la struttura geometrica è chiara ma YOLO non li ha inseriti.

## Livello 6 — risoluzione conflitti

Sceglie quale classe tenere quando più detection descrivono la stessa regione.

## Livello 7 — rimozione duplicati e terminal annidati

Pulisce l’output finale rendendolo più coerente e più adatto agli step successivi della pipeline.

---

# 22. Conclusione tecnica

Dal punto di vista della tesi, lo script `01_detect_components.py` implementa un approccio **ibrido**:

- **YOLO** svolge la detection primaria dei simboli;
- il **post-processing geometrico** corregge gli errori più frequenti;
- un **secondo pass specializzato** recupera alcune classi difficili;
- una fase finale di **soppressione conflitti e pulizia** rende l’output più stabile per gli step successivi.

In altre parole, il sistema non si affida solo alla rete neurale, ma combina:

1. classificazione neurale;
2. euristiche di forma;
3. analisi binaria locale;
4. regole di consistenza tra classi.

Questo è esattamente il motivo per cui lo script è più lungo di una normale detection YOLO: non si limita a “predire box”, ma cerca di produrre una rappresentazione dei componenti più pulita, robusta e coerente con i simboli elettrici reali.
