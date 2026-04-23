# Documentazione completa dello script `04_extract_wires.py`

Questa documentazione descrive in modo sistematico la logica dello script `04_extract_wires.py`, con particolare attenzione a:

- obiettivo dello stage;
- flusso completo di elaborazione;
- significato di ogni parametro;
- ruolo di **ogni singola funzione**;
- logica di masking dei componenti;
- preservazione locale dei terminali;
- operazioni morfologiche;
- filtraggio del rumore;
- skeletonization finale.

La descrizione seguente è basata sulla **versione attuale dello script**.

---

# 1. Scopo generale dello script

Lo script `04_extract_wires.py` realizza lo stage della pipeline dedicato all’**estrazione dei wire** dal diagramma elettrico.

L’idea di fondo è la seguente:

1. partire dall’output dello stage precedente (`03_estimate_terminals`);
2. leggere immagine, componenti e terminali;
3. **mascherare i componenti**, così da rimuovere il “corpo” dei simboli dal diagramma;
4. **preservare localmente le zone dei terminali**, in modo da non spezzare i fili esattamente nei punti di connessione;
5. binarizzare e ripulire l’immagine risultante;
6. ottenere uno **skeleton** dei wire, cioè una rappresentazione sottile e topologicamente più semplice dei collegamenti.

In breve, questo script non serve a rilevare i componenti, ma a produrre una versione del diagramma in cui rimangano soprattutto i **fili di connessione**, già ripuliti dai simboli principali.

---

# 2. Input e output dello stage

## 2.1 Input

Lo script legge i JSON prodotti da `03_estimate_terminals`, cioè file che contengono almeno:

- `image_path`
- `components`
- `terminals`

Ogni file JSON corrisponde a una singola immagine del dataset.

## 2.2 Output

Per ogni immagine vengono generati più output intermedi e finali:

- `component_mask`
- `masked_gray`
- `binary`
- `closed`
- `bridged`
- `filtered`
- `skeleton`

Inoltre vengono salvati file di debug, per esempio:

- overlay della maschera componenti;
- overlay delle zone preservate attorno ai terminali.

Infine viene scritto un nuovo JSON che copia il contenuto precedente e aggiunge la sezione `wire_extraction` con:
- parametri usati;
- statistiche del filtraggio;
- path ai file generati.

---

# 3. Struttura generale del flusso

Il flusso completo su una singola immagine è:

1. lettura immagine;
2. conversione in grayscale;
3. costruzione della maschera dei componenti;
4. riapertura locale della maschera attorno ai terminali;
5. applicazione della maschera all’immagine grayscale;
6. binarizzazione con Otsu;
7. closing morfologico;
8. bridging opzionale dei fili frammentati;
9. rimozione delle componenti con area troppo piccola;
10. skeletonization;
11. salvataggio degli output intermedi e finali;
12. aggiornamento del JSON.

---

# 4. Parametri globali dello script

## 4.1 Path e cartelle

Le variabili iniziali definiscono:

- `PROJECT_ROOT`: root del progetto;
- `PIPELINE_DATASET`: dataset/pipeline attiva;
- `INPUT_DIR`: cartella di input, che punta a `03_estimate_terminals`;
- `OUTPUT_DIR`: cartella di output dello stage 04.

Poi vengono definite le sottocartelle di output, una per ogni tipo di immagine prodotta:

- `MASK_DEBUG_DIR`
- `COMPONENT_MASK_DIR`
- `TERMINAL_KEEP_DEBUG_DIR`
- `MASKED_DIR`
- `BINARY_DIR`
- `CLOSED_DIR`
- `BRIDGED_DIR`
- `FILTERED_DIR`
- `SKELETON_DIR`

Questa suddivisione è utile perché consente di analizzare separatamente ogni passaggio della pipeline.

---

## 4.2 Parametri di masking dei componenti

### `MASK_SHRINK_FACTOR = 1.0`
Controlla l’eventuale riduzione del bounding box del componente prima di costruire la maschera.

- Se vale `1.0`, il bbox non viene ristretto.
- Se fosse inferiore a `1.0`, il rettangolo verrebbe leggermente contratto.

### `CLASS_MASK_PADDING`
È un dizionario che aggiunge padding specifico per alcune classi:

- `Analog_Meter`: 8
- `Connector`: 6
- `Switch`: 4
- `Transformer`: 4

Il motivo è che alcuni simboli hanno geometria complessa o parti che escono dal bbox nominale; per questi casi conviene mascherare una zona un po’ più ampia.

---

## 4.3 Parametri di preservazione dei terminali

Le keep zones servono a evitare che la maschera dei componenti cancelli anche i piccoli tratti di wire immediatamente adiacenti ai terminali.

Parametri generali:

- `TERMINAL_KEEP_RADIUS = 10`
- `TERMINAL_KEEP_LINE_THICKNESS = 7`
- `TERMINAL_KEEP_INWARD_LEN = 14`
- `TERMINAL_KEEP_OUTWARD_LEN = 12`

Per i terminali ausiliari dell’operational amplifier (`aux1`, `aux2`) vengono usati parametri dedicati:

- `OPAMP_AUX_KEEP_RADIUS = 5`
- `OPAMP_AUX_KEEP_LINE_THICKNESS = 5`
- `OPAMP_AUX_KEEP_INWARD_LEN = 0`
- `OPAMP_AUX_KEEP_OUTWARD_LEN = 12`

Esistono anche override per classi particolari:

- `Analog_Meter`
- `Connector`
- `Switch`
- `Transformer`

L’idea è che questi simboli hanno molto “corpo” interno; se la keep zone fosse troppo aggressiva verso l’interno del bbox, si rischierebbe di riaprire il simbolo stesso invece di preservare soltanto il wire.

---

## 4.4 Parametri morfologici

### Closing standard
- `CLOSING_KERNEL_SIZE = 3`
- `CLOSING_ITERATIONS = 1`

Il closing serve a chiudere piccoli gap e a rendere più continui i wire dopo la binarizzazione.

### Bridging dei fili frammentati
- `ENABLE_FRAGMENTED_WIRE_BRIDGE = True`
- `FRAGMENTED_WIRE_BRIDGE_KERNEL_LENGTH = 15`
- `FRAGMENTED_WIRE_BRIDGE_KERNEL_THICKNESS = 3`
- `FRAGMENTED_WIRE_BRIDGE_ITERATIONS = 1`

Questo passaggio aggiuntivo è utile soprattutto per wire tratteggiati, spezzati o localmente frammentati.

---

## 4.5 Filtro delle componenti piccole

- `ENABLE_SMALL_COMPONENT_FILTER = True`
- `MIN_COMPONENT_AREA = 40`

Il filtro rimuove componenti con area troppo piccola, che di solito corrispondono a rumore residuo.

---

# 5. Utility geometriche di base

## `clamp_point(x, y, w, h)`

### Scopo
Porta un punto `(x, y)` dentro i limiti dell’immagine.

### Logica
- arrotonda le coordinate;
- le limita all’intervallo valido `[0, w-1]` e `[0, h-1]`.

### Perché serve
Quando si disegnano cerchi o segmenti attorno ai terminali, è fondamentale evitare coordinate fuori dall’immagine.

---

## `shrink_bbox(bbox, shrink_factor=0.88)`

### Scopo
Riduce un bounding box rispetto al suo centro.

### Logica
Dato il bbox `[x1, y1, x2, y2]`:
1. calcola il centro;
2. scala larghezza e altezza con `shrink_factor`;
3. ricostruisce il nuovo bbox intorno allo stesso centro.

### Uso nello script
È usata prima di costruire la maschera componenti.

### Nota
Nella versione attuale, `MASK_SHRINK_FACTOR = 1.0`, quindi di fatto non avviene alcuna riduzione, ma la funzione resta disponibile e rende la pipeline configurabile.

---

## `expand_bbox(bbox, pad=0)`

### Scopo
Espande il bounding box aggiungendo un padding uniforme.

### Logica
Semplicemente:
- sottrae `pad` a `x1` e `y1`;
- somma `pad` a `x2` e `y2`.

### Uso nello script
Viene usata durante la costruzione della maschera componenti, con padding dipendente dalla classe.

---

# 6. Costruzione della maschera dei componenti

Questa è una parte centrale dello stage 04.

L’obiettivo è creare una immagine binaria in cui i **componenti** siano coperti da una maschera piena, così da poterli rimuovere dall’immagine e lasciare emergere i wire.

## `build_base_component_mask(image_shape, components)`

### Scopo
Costruire la maschera rettangolare di base dei componenti.

### Logica
Per ogni componente:
1. verifica `use_for_masking`; se è `False`, il componente non viene mascherato;
2. prende il bbox del componente;
3. applica eventuale shrink;
4. applica eventuale padding specifico di classe;
5. clampa le coordinate all’immagine;
6. disegna un rettangolo pieno sulla maschera.

### Output
Restituisce una maschera binaria in cui:
- `255` indica zone coperte dai componenti;
- `0` indica zone non mascherate.

### Significato
Questa maschera rappresenta il “corpo” dei componenti che verrà eliminato dalla grayscale.

---

# 7. Logica delle keep zones sui terminali

La maschera dei componenti da sola non basta: se si coprisse interamente il bbox di un componente, spesso si cancellerebbe anche il piccolo tratto di wire che entra o esce dal terminale.

Per questo lo script introduce delle **keep zones**, cioè aree locali che vengono riaperte nella maschera.

## `terminal_keep_params(term)`

### Scopo
Restituire i parametri della keep zone per un singolo terminale.

### Logica
La funzione controlla:

1. **nome del terminale**  
   Se il nome è `aux1` oppure `aux2`, usa i parametri speciali dell’operational amplifier.

2. **classe del componente a cui appartiene il terminale**  
   Se il componente è in `CLASS_TERMINAL_KEEP_OVERRIDES`, usa i parametri specifici per quella classe.

3. **caso generale**  
   Altrimenti usa i parametri standard.

### Output
Un dizionario con:
- `radius`
- `thickness`
- `inward_len`
- `outward_len`

---

## `terminal_keep_segment(term)`

### Scopo
Calcolare il segmento orientato da preservare attorno al terminale.

### Logica
La funzione usa:
- coordinate del terminale `(x, y)`;
- posizione relativa del terminale (`left`, `right`, `top`, `bottom`);
- parametri restituiti da `terminal_keep_params`.

A seconda del lato:
- per `left` costruisce un segmento orizzontale che si estende un po’ verso fuori e un po’ verso dentro;
- per `right` idem, ma simmetrico;
- per `top` e `bottom` costruisce un segmento verticale;
- se la posizione relativa non è nota, restituisce un segmento degenerato nel solo punto.

### Perché serve
Il cerchio attorno al terminale da solo non basta: spesso il wire entra nel componente con una direzione ben precisa.  
Il segmento consente di preservare anche una piccola “capsula” direzionata lungo il lato corretto.

---

## `carve_terminal_keep_zones(mask, terminals)`

### Scopo
Riaprire nella maschera le zone da preservare attorno ai terminali.

### Logica
Per ogni terminale:
1. ottiene i parametri della keep zone;
2. disegna sulla maschera un cerchio nero centrato sul terminale;
3. calcola il segmento direzionale;
4. disegna sulla maschera una linea nera lungo tale segmento.

In parallelo costruisce anche `keep_debug`, una maschera di debug in cui le keep zones sono disegnate in bianco.

### Interpretazione
- sulla `mask`: disegnare in nero significa **togliere** maschera, cioè preservare immagine;
- su `keep_debug`: disegnare in bianco significa evidenziare le zone preservate.

### Effetto finale
La keep zone protegge:
- il punto esatto del terminale;
- un piccolo tratto di wire nella direzione corretta.

---

## `build_component_mask(image_shape, components, terminals)`

### Scopo
Costruire la maschera finale dei componenti già corretta con le keep zones dei terminali.

### Logica
1. chiama `build_base_component_mask(...)`;
2. applica `carve_terminal_keep_zones(...)`;
3. restituisce:
   - maschera finale dei componenti;
   - maschera di debug delle keep zones.

---

# 8. Funzioni di debug visivo

## `save_mask_debug(image_bgr, mask, out_path)`

### Scopo
Salvare una vista overlay della maschera componenti.

### Logica
- crea un layer rosso;
- fonde il rosso con l’immagine originale solo nelle zone dove `mask > 0`.

### Effetto
Produce un’immagine in cui si vede chiaramente quali regioni del diagramma vengono coperte dalla maschera.

---

## `save_terminal_keep_debug(image_bgr, keep_debug, out_path)`

### Scopo
Salvare una vista overlay delle terminal keep zones.

### Logica
- crea un layer verde;
- fonde il verde con l’immagine originale solo nelle zone dove `keep_debug > 0`.

### Effetto
Produce un’immagine che mostra dove la maschera è stata riaperta per salvare le connessioni locali ai terminali.

---

# 9. Post-processing dei wire

Dopo avere mascherato i componenti e preservato le zone dei terminali, lo script esegue una serie di operazioni per isolare i wire.

## `remove_small_connected_components(binary_img, min_area=40)`

### Scopo
Rimuovere piccole componenti connesse considerate rumore.

### Logica
1. esegue `connectedComponentsWithStats`;
2. per ogni componente:
   - se l’area è almeno `min_area`, la mantiene;
   - altrimenti la scarta.

### Output
Restituisce:
- immagine filtrata;
- numero di componenti mantenute;
- numero di componenti rimosse.

### Perché serve
Dopo threshold e morfologia possono rimanere piccoli blob isolati, dovuti a testo residuo, rumore o frammenti di simboli.  
Questo filtro riduce tali artefatti prima dello skeleton.

---

## `bridge_fragmented_wires(binary_img)`

### Scopo
Ricucire fili frammentati o tratteggiati.

### Logica
Se `ENABLE_FRAGMENTED_WIRE_BRIDGE` è `False`, restituisce l’immagine invariata con metadati che indicano che il bridging non è attivo.

Se invece è attivo:
1. costruisce un kernel rettangolare **orizzontale**;
2. costruisce un kernel rettangolare **verticale**;
3. applica un closing morfologico orizzontale;
4. applica un closing morfologico verticale.

### Perché due kernel anisotropi
I fili nel diagramma sono spesso:
- prevalentemente orizzontali;
- oppure verticali.

Usare prima un kernel orizzontale e poi uno verticale consente di ricucire gap lineari senza “gonfiare” troppo la struttura in tutte le direzioni.

### Output
Restituisce:
- immagine bridged;
- dizionario `bridge_info` con i parametri usati.

---

# 10. Funzione principale di estrazione wire

## `extract_wires_from_image(image_bgr, components, terminals)`

Questa è la funzione centrale dello stage.

### Passo 1 — grayscale
Converte l’immagine BGR in scala di grigi.

### Passo 2 — maschera componenti + keep zones
Chiama `build_component_mask(...)` per ottenere:
- `component_mask`
- `terminal_keep_debug`

### Passo 3 — applicazione maschera
Crea `masked_gray` come copia della grayscale e imposta a bianco (`255`) tutte le zone coperte dalla maschera.

### Significato
Poiché i componenti sono resi bianchi, il successivo threshold inverso farà emergere soprattutto i fili e le tracce residue non mascherate.

### Passo 4 — threshold
Applica una sogliatura con:
- `cv2.THRESH_BINARY_INV`
- `cv2.THRESH_OTSU`

Questo produce `binary`.

### Interpretazione
- lo sfondo chiaro viene portato a nero;
- i tratti scuri del diagramma diventano bianchi;
- i componenti già mascherati restano soppressi.

### Passo 5 — closing standard
Applica un closing con kernel rettangolare `3x3` e una iterazione.

Produce `closed`.

### Obiettivo
Chiudere piccoli gap locali generati dalla maschera o dalla binarizzazione.

### Passo 6 — bridge dei fili frammentati
Chiama `bridge_fragmented_wires(closed)`.

Produce:
- `bridged`
- `bridge_info`

### Obiettivo
Ricucire fili tratteggiati o localmente interrotti.

### Passo 7 — small component filter
Se il filtro è abilitato:
- chiama `remove_small_connected_components(bridged, min_area=MIN_COMPONENT_AREA)`

Produce:
- `filtered`
- `kept_components`
- `removed_components`

Altrimenti `filtered = bridged.copy()`.

### Passo 8 — skeletonization
Applica `skeletonize(filtered > 0)` dalla libreria `skimage`.

Produce `skeleton`.

### Significato
Lo skeleton trasforma i wire in una rappresentazione a spessore minimo, utile per gli step topologici successivi.

### Metadati aggiuntivi
La funzione prepara anche:
- `filter_info`
- `keep_info`
- `bridge_info`

che descrivono parametri e statistiche dell’estrazione.

### Output complessivo
La funzione restituisce una tupla con:

1. `component_mask`
2. `terminal_keep_debug`
3. `masked_gray`
4. `binary`
5. `closed`
6. `bridged`
7. `filtered`
8. `skeleton`
9. `filter_info`
10. `keep_info`
11. `bridge_info`

---

# 11. Funzione `main()`

## Scopo
Orchestrare lo stage sull’intero dataset.

## Flusso
Per prima cosa:
1. verifica che `INPUT_DIR` esista;
2. crea tutte le cartelle di output;
3. cerca tutti i JSON in input.

Se non trova JSON, solleva errore.

Poi, per ogni file JSON:

1. legge il contenuto;
2. ricava `image_path`;
3. carica l’immagine;
4. estrae:
   - `components`
   - `terminals`
5. chiama `extract_wires_from_image(...)`;
6. salva tutte le immagini intermedie e finali;
7. costruisce `output_data` copiando il JSON originale;
8. aggiunge il blocco `wire_extraction`;
9. salva il nuovo JSON nella cartella di output;
10. stampa un messaggio di avanzamento.

Alla fine stampa il messaggio di completamento con il path dei risultati.

---

# 12. Significato dei file prodotti

Per ogni immagine, lo stage salva vari artefatti. Ognuno ha un ruolo specifico.

## `*_component_mask.png`
Maschera binaria dei componenti.

- bianco = componente mascherato
- nero = resto dell’immagine

## `*_mask_debug.jpg`
Overlay rosso della maschera componenti sull’immagine originale.

## `*_terminal_keep_debug.jpg`
Overlay verde delle zone preservate attorno ai terminali.

## `*_masked_gray.png`
Grayscale con componenti resi bianchi.

## `*_binary.png`
Risultato del threshold inverso con Otsu.

## `*_closed.png`
Risultato dopo il closing standard.

## `*_bridged.png`
Risultato dopo il bridging anisotropo dei fili frammentati.

## `*_filtered.png`
Immagine dopo rimozione delle piccole componenti connesse.

## `*_skeleton.png`
Skeleton finale dei wire.

---

# 13. Logica complessiva del masking

Dal punto di vista concettuale, la strategia dello script è molto precisa:

## 13.1 Perché si mascherano i componenti
Se si tentasse di estrarre i wire direttamente dal diagramma originale, il risultato conterrebbe anche:
- corpi dei simboli;
- testo;
- dettagli interni ai componenti.

Mascherare i componenti serve a “svuotare” la scena e lasciare principalmente i collegamenti.

## 13.2 Perché non basta cancellare il bbox
Se si cancellasse brutalmente tutto il bbox del componente, si rischierebbe di interrompere i fili proprio nei punti in cui i wire si collegano al simbolo.

Per questo si introducono le keep zones dei terminali:
- un cerchio locale;
- un piccolo segmento direzionale.

## 13.3 Perché servono i parametri per classe
Simboli come:
- `Analog_Meter`
- `Connector`
- `Switch`
- `Transformer`

hanno struttura grafica interna complessa.  
Le keep zones devono quindi essere più conservative verso l’interno, altrimenti lo stage riaprirebbe porzioni del simbolo stesso.

---

# 14. Logica complessiva del post-processing morfologico

Dopo il masking, l’estrazione dei wire non è immediatamente perfetta. Lo script applica quindi più fasi di pulizia.

## 14.1 Threshold inverso
Serve a separare linee scure e sfondo chiaro.

## 14.2 Closing standard
Chiude piccoli vuoti locali.

## 14.3 Bridging anisotropo
Ricuce tratti orizzontali e verticali frammentati.

## 14.4 Rimozione delle piccole componenti
Elimina rumore residuo che altrimenti disturberebbe la topologia.

## 14.5 Skeletonization
Produce una mappa dei wire sottile e più adatta alle elaborazioni successive.

---

# 15. Perché lo skeleton è importante

Lo skeleton finale è una rappresentazione dei wire in cui le tracce vengono ridotte a uno spessore minimo.

Questo è utile perché:

- semplifica il riconoscimento dei nodi;
- riduce l’influenza dello spessore grafico del wire;
- rende più stabile l’analisi topologica;
- facilita il matching tra terminali e rete di connessione negli step successivi.

---

# 16. Riassunto funzione per funzione

Qui sotto trovi una sintesi rapida del ruolo di ogni funzione.

## Utility geometriche
- `clamp_point`: limita un punto ai bordi immagine.
- `shrink_bbox`: restringe un bbox attorno al centro.
- `expand_bbox`: aggiunge padding a un bbox.

## Maschera componenti
- `build_base_component_mask`: crea la maschera rettangolare dei componenti.
- `terminal_keep_params`: sceglie i parametri della keep zone per un terminale.
- `terminal_keep_segment`: costruisce il segmento orientato di keep zone.
- `carve_terminal_keep_zones`: riapre la maschera attorno ai terminali.
- `build_component_mask`: combina base mask e keep zones.

## Debug
- `save_mask_debug`: salva overlay rosso della maschera.
- `save_terminal_keep_debug`: salva overlay verde delle keep zones.

## Pulizia wire
- `remove_small_connected_components`: rimuove componenti piccole.
- `bridge_fragmented_wires`: ricuce fili spezzati.
- `extract_wires_from_image`: esegue l’intera pipeline locale su una immagine.

## Orchestrazione
- `main`: gestisce cartelle, lettura JSON, chiamate di elaborazione e salvataggi.

---

# 17. Conclusione tecnica

Dal punto di vista della tesi, lo script `04_extract_wires.py` implementa una pipeline di estrazione wire **ibrida tra masking geometrico e morfologia binaria**.

L’approccio è composto da tre idee fondamentali:

1. **Rimuovere i componenti** tramite maschera, così da non confondere i simboli con i fili.
2. **Preservare le connessioni locali ai terminali**, così da non spezzare artificialmente la topologia.
3. **Ripulire e scheletrizzare** il risultato, così da ottenere una rappresentazione finale dei wire semplice e robusta.

Questo rende lo stage 04 un passaggio cruciale tra:
- il riconoscimento dei simboli e dei terminali,
- e la successiva ricostruzione della connettività del circuito.

In altre parole, questo script trasforma l’immagine “ricca di simboli” in una rappresentazione molto più adatta all’analisi topologica dei collegamenti elettrici.
