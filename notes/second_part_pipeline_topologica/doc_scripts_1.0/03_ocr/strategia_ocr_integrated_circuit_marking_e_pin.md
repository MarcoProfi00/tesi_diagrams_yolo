# Strategia OCR per circuiti integrati nella pipeline di analisi degli schemi elettrici

## 1. Obiettivo del documento

Questo documento descrive la strategia utilizzata nella pipeline per gestire i **circuiti integrati** (`Integrated_Circuit`) negli schemi elettrici. In particolare vengono documentate due attività distinte:

1. la lettura del **nome del circuito integrato**, chiamato anche *marking* o *part number*, ad esempio `NE555`, `TDA7000`, `LM317T`, `TPS63061`;
2. la lettura delle informazioni associate ai **pin/terminali** del circuito integrato, cioè `pin_number` e `pin_label_text`, ad esempio `2`, `13`, `VIN`, `GND`, `FB`, `OUT`, `ADJ`.

L'obiettivo finale della pipeline non è soltanto disegnare dei rettangoli intorno ai componenti, ma costruire una rappresentazione strutturata dello schema elettrico. Questa rappresentazione dovrà poi essere usata da una fase successiva, eventualmente basata su un agente AI, per cercare datasheet, interpretare i pin e ragionare sul funzionamento del circuito.

Per questo motivo il JSON finale deve contenere sia informazioni geometriche, sia informazioni semantiche. La geometria serve per capire **dove sono collegati i fili**; l'OCR serve per capire **cosa è scritto vicino o dentro il componente**.

La distinzione principale è quindi:

```text
geometria  -> dove sono corpo, fili e terminali
OCR        -> cosa c'è scritto sull'integrato e sui pin
semantica  -> cosa significa quel testo, eventualmente tramite datasheet
```

La parte semantica completa, cioè l'associazione definitiva tra un pin e la sua funzione elettrica, non viene ancora risolta nello script 03. Lo script 03 raccoglie le evidenze utili: nome IC, numeri pin, label pin e terminali geometrici.

---

## 2. Contesto nella pipeline 01-05

La pipeline è organizzata in più passaggi. I circuiti integrati attraversano questi passaggi in modo progressivo.

### 2.1 Script 01: rilevazione con YOLO

Lo script 01 rileva i componenti nello schema elettrico tramite YOLO. In questa fase un circuito integrato viene riconosciuto come oggetto appartenente alla classe:

```text
Integrated_Circuit
```

L'output principale è un bounding box YOLO. Questo bbox è utile, ma non sempre coincide perfettamente con il corpo reale dell'integrato. In alcuni casi può includere fili, numeri dei pin, label dei pin o testo vicino.

### 2.2 Script 02: assegnazione degli identificativi

Lo script 02 assegna un identificativo stabile a ogni istanza, ad esempio:

```text
11.1
11.2
11.3
```

Questi identificativi sono importanti perché diventano la base per costruire gli ID dei terminali:

```text
11.1:left_1
11.1:right_2
11.1:bottom_1
```

Da questo momento in poi l'identità del componente deve restare stabile.

### 2.3 Script 03: stima dei terminali e OCR

Lo script 03 è il punto più adatto per gestire i circuiti integrati, perché dispone contemporaneamente di:

- immagine originale BGR;
- bounding box dei componenti;
- metadati YAML della classe;
- terminali geometrici stimati;
- body bbox raffinato, quando disponibile;
- possibilità di salvare immagini di debug.

Per questo lo script 03 svolge tre attività sugli IC:

1. stima i terminali geometrici osservando i contatti filo-corpo;
2. chiama `ocr_integrated_circuit.py` per leggere il nome/marking dell'IC;
3. chiama `ocr_integrated_circuit_pins.py` per arricchire i terminali con numero e label del pin.

### 2.4 Script 04: skeletonizzazione dei fili

Lo script 04 lavora sui fili e sulla skeletonizzazione. Questa fase non dovrebbe dipendere dall'OCR dei nomi o dei pin, perché la struttura del grafo deve essere robusta anche se l'OCR sbaglia.

Il body bbox dell'integrato viene usato anche dallo script 04 per mascherare meglio il corpo dell'IC durante l'estrazione dei fili. Questo evita che il rettangolo del package venga confuso con una pista o con una net dello schema.

### 2.5 Script 05: costruzione del grafo

Lo script 05 costruisce il grafo elettrico. Anche qui è importante che la topologia non dipenda direttamente dall'OCR. Il grafo deve collegare terminali geometrici a net geometriche.

L'OCR aggiunge metadati utili, ma non deve decidere da solo se un terminale esiste o se un filo è collegato.

---

## 3. Principio fondamentale: prima geometria, poi OCR

Il principio più importante della strategia è questo:

```text
I terminali non devono nascere dall'OCR.
I terminali devono nascere dalla geometria dei fili.
```

Questo significa che un terminale esiste perché un filo entra o esce dal corpo del circuito integrato, non perché Tesseract ha letto un numero vicino.

L'OCR può sbagliare facilmente, soprattutto con numeri piccoli come `1`, `7`, `13`, `15` o con label corte come `EN`, `FB`, `PG`. Se usassimo l'OCR per creare direttamente terminali, rischieremmo di introdurre molti falsi positivi nel grafo.

La strategia corretta è quindi:

```text
1. Trovo i terminali con la geometria.
2. Assegno a ogni terminale un nome geometrico stabile.
3. Leggo con OCR eventuali testi vicini.
4. Aggiungo questi testi come attributi del terminale.
5. Non modifico terminal_id, name o posizione geometrica.
```

Esempio:

```json
{
  "terminal_id": "11.1:left_2",
  "name": "left_2",
  "relative_position": "left",
  "x": 420.0,
  "y": 250.0,
  "pin_number": "2",
  "pin_label_text": "VIN"
}
```

In questo esempio `left_2` rimane il terminale geometrico. Il numero `2` e la label `VIN` sono informazioni OCR aggiuntive.

---

## 4. Differenza tra nome geometrico, numero pin e label pin

Per evitare confusione, nella pipeline vengono distinti tre livelli.

### 4.1 Nome geometrico del terminale

È il nome dato dallo script 03 in base alla posizione sul corpo dell'IC:

```text
left_1
left_2
right_1
top_1
bottom_1
```

Questo nome serve alla pipeline per mantenere una topologia stabile. Non dipende dall'OCR.

### 4.2 Numero del pin

È il numero scritto nello schema vicino al terminale, quando presente:

```text
1
2
3
10
13
16
31
40
```

Nel JSON viene salvato come:

```json
"pin_number": "2"
```

Il numero pin è utile per consultare un datasheet. Per esempio, se il marking è `NE555` e un terminale ha `pin_number = 3`, il datasheet può dire che il pin 3 è `OUT`.

### 4.3 Label del pin

È il nome funzionale scritto nello schema vicino al terminale, quando presente:

```text
VIN
VOUT
GND
EN
FB
PG
BOOT
COMP
OUT
IN
ADJ
D0
D1
P1.0
```

Nel JSON viene salvato come:

```json
"pin_label_text": "VIN"
```

La label può essere presente anche senza numero. Un esempio tipico è `LM317T`, dove nello schema possono comparire `IN`, `OUT`, `ADJ` senza numerazione dei pin.

---

## 5. File coinvolti nella strategia attuale

### 5.1 `ocr_integrated_circuit.py`

Questo modulo legge il nome del circuito integrato. È lo step OCR principale per il marking.

Le sue responsabilità sono:

- recuperare il `body_bbox` dell'IC;
- costruire regioni di ricerca OCR;
- eseguire Tesseract sulle ROI;
- usare EasyOCR come fallback/consenso quando il marking non e' abbastanza affidabile;
- normalizzare il testo letto;
- filtrare candidati non validi;
- assegnare uno score ai candidati;
- scegliere il miglior marking;
- riconoscere il sottotipo `seven_segment_display` quando un falso IC e' in realta' un display a 7 segmenti;
- salvare campi come `ic_marking`, `ic_marking_confidence`, `ic_marking_bbox`, `ic_marking_source_region`, `ic_ocr_debug`.

Questo modulo **non modifica i terminali**.

### 5.2 `ocr_integrated_circuit_pins.py`

Questo modulo legge informazioni associate ai pin. È separato dal modulo del marking perché il problema è diverso.

Le sue responsabilità sono:

- lavorare solo sui terminali IC già trovati geometricamente;
- costruire corsie OCR per i lati del body;
- eseguire Tesseract sulle regioni laterali;
- usare un fallback a componenti connessi per numeri piccoli o difficili;
- usare EasyOCR sulle label interne solo quando non e' presente `ic_marking`;
- classificare le parole lette come numero o label;
- associare ogni parola al terminale geometrico piu' plausibile sullo stesso lato;
- cancellare `pin_label_text` quando sono presenti sia `ic_marking` sia `pin_number`, per lasciare l'interpretazione al datasheet;
- trattare i display a 7 segmenti con la stessa pipeline OCR, ma con filtro finale sui terminali logici `a`-`h` e `com`;
- salvare `pin_number`, `pin_label_text` e debug sul terminale.

Questo modulo **non crea nuovi terminali** e **non cambia `terminal_id`**.

### 5.3 `03_estimate_terminals.py`

Lo script 03 coordina la stima dei terminali e le chiamate OCR.

Per ogni componente:

1. crea una copia del componente;
2. stima i terminali geometrici;
3. se il componente è `Integrated_Circuit`, chiama `enrich_ic_marking_ocr`;
4. poi chiama `enrich_ic_pin_ocr`;
5. salva il JSON pubblico;
6. salva le immagini di debug, se abilitate.

### 5.4 `debug_draw.py`

Il file di debug disegna le immagini di controllo. Attualmente è utile mantenere almeno due famiglie di immagini:

```text
debug_images/
  *_terminals.jpg

  ic_ocr/
    *_ic_ocr.jpg
```

Le immagini dei terminali servono per controllare la parte geometrica. Le immagini OCR IC servono invece per controllare sia la lettura del marking sia i valori finali selezionati per i pin.

Nel codice attuale `*_ic_ocr.jpg` evidenzia:

- bbox e testo del marking IC selezionato;
- bbox dei `pin_number` finali associati ai terminali;
- bbox dei `pin_label_text` finali associati ai terminali.

Queste immagini non mostrano tutte le parole grezze lette dall'OCR, ma solo quelle entrate nel JSON finale. Per questo sono adatte al controllo manuale dei risultati, mentre il debug JSON rimane il posto migliore per analizzare parole scartate, confidence e motivi di filtro.

---

## 6. `bbox`, `body_bbox` e ROI OCR

Per gli IC bisogna distinguere tre concetti.

### 6.1 `bbox` YOLO

È il bounding box prodotto da YOLO. Può essere largo e può includere elementi che non fanno parte del corpo reale dell'integrato:

- fili;
- numeri dei pin;
- label dei pin;
- componenti vicini;
- testo esterno;
- watermark.

È utile come riferimento iniziale, ma non è l'area migliore per cercare terminali o testo.

### 6.2 `body_bbox`

È il rettangolo che rappresenta il corpo reale del circuito integrato, cioè il rettangolo disegnato nello schema.

Il modulo OCR lo recupera con questa priorità:

```text
1. component["body_bbox"]
2. component["connection_side_scores"]["body_bbox"]
3. terminal_point_debug["body_bbox"] dentro i terminali
4. component["bbox"] come fallback
```

Questa priorità rende il sistema robusto. Se una fase precedente ha già raffinato il corpo dell'IC, l'OCR usa quel risultato. Se invece manca, usa il bbox YOLO come fallback.

### 6.3 ROI OCR

Le ROI OCR sono aree costruite a partire dal `body_bbox`.

Non conviene eseguire OCR su tutta l'immagine: sarebbe lento e pieno di falsi positivi. Conviene leggere solo zone mirate intorno all'IC.

Per il marking si leggono regioni come:

```text
body_inner
above_body
below_body
left_of_body
right_of_body
expanded_bbox
```

Per i pin si leggono invece corsie laterali costruite attorno al body bbox:

```text
left lanes
right lanes
top lanes
bottom lanes
```

Ogni corsia contiene la parte esterna e la parte interna vicino al lato del package. Questo permette di leggere sia numeri pin scritti fuori dal corpo sia label funzionali scritte dentro il simbolo.

---

## 7. OCR del marking IC: logica implementata

La funzione principale del modulo è:

```python
enrich_ic_marking_ocr(component, image_bgr, meta)
```

Questa funzione arricchisce il componente con il nome letto tramite OCR.

### 7.1 Controllo di abilitazione

La funzione legge il blocco YAML:

```text
ocr
ocr.ic_marking
```

Se l'OCR è disabilitato, il componente viene restituito senza marking e nel debug viene scritto:

```json
{
  "enabled": false,
  "reason": "ocr_disabled_in_yaml"
}
```

Questo è importante perché permette di disattivare l'OCR senza rompere la pipeline.

### 7.2 Recupero del `body_bbox`

Prima di creare le ROI, il modulo recupera il body bbox con `get_ic_body_bbox_from_component`.

Il body bbox viene anche salvato nel componente:

```json
"body_bbox": [x1, y1, x2, y2]
```

Questo è utile non solo per l'OCR, ma anche per fasi successive, ad esempio per mascherare meglio il corpo dell'IC nella skeletonizzazione.

### 7.3 Costruzione delle regioni di ricerca

La funzione `build_ic_marking_regions` costruisce le ROI in base alla lista configurata nel YAML.

Le regioni supportate sono:

```text
body_inner
above_body
below_body
left_of_body
right_of_body
expanded_bbox
```

Nel codice attuale `body_inner` coincide con il `body_bbox` completo. Il nome `body_inner` indica la regione principale interna al corpo dell'integrato; in futuro potrà essere ristretta ulteriormente per escludere bordi e pin number.

#### `body_inner`

Serve per casi in cui il nome è scritto dentro il corpo:

```text
NE555
TDA7000
LM317T
LM1875
TDA1553
TC4423
L298
```

#### `above_body`

Serve per casi in cui il part number è sopra il corpo:

```text
TPS63061
ISL85410/ISL854102
```

Questi casi sono importanti perché alcuni schemi mostrano il marking in alto, sopra il rettangolo giallo o bianco del chip.

#### `below_body`, `left_of_body`, `right_of_body`

Sono regioni laterali opzionali. Possono essere utili quando il testo è scritto vicino al package, ma sono più rischiose perché possono includere componenti o net label vicine.

#### `expanded_bbox`

È una regione più ampia intorno al corpo. È utile come fallback, ma è anche la più pericolosa perché può contenere molti falsi positivi.

Per questo un candidato letto in `expanded_bbox` deve comunque superare i filtri di scoring.

### 7.4 Preprocessing per Tesseract

Il preprocessing attuale è leggero e adatto a schemi elettrici ad alto contrasto.

La funzione `_preprocess_for_ocr` esegue:

```text
1. conversione in grayscale
2. resize 3x
3. Gaussian blur leggero
4. soglia Otsu
5. eventuale inversione per ottenere testo scuro su sfondo chiaro
```

Il resize 3x è importante perché i testi tecnici negli schemi sono spesso piccoli. Ingrandire la ROI aiuta Tesseract a distinguere caratteri simili:

```text
5 / S
0 / O
1 / I / l
7 / /
8 / B
```

### 7.5 Esecuzione OCR

Il modulo usa Tesseract tramite `pytesseract.image_to_data` come motore principale.

Il vantaggio di `image_to_data` è che non restituisce soltanto testo, ma anche:

- confidence;
- bounding box locale;
- parole separate;
- informazioni utili per il debug.

La configurazione usa:

```text
--oem 3
--psm 6
```

più una whitelist di caratteri:

```text
ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_/-+.
```

La whitelist riduce la probabilità che vengano letti caratteri inutili per i codici IC.

### 7.6 Fallback con EasyOCR

Oltre a Tesseract, il modulo puo' usare EasyOCR come fallback selettivo per il marking.

EasyOCR non viene lanciato sempre, perche' e' piu' pesante. Viene usato solo quando:

- Tesseract non trova candidati validi;
- il candidato migliore e' debole o proviene da una regione rischiosa;
- il marking richiede la modalita' OCR piu' profonda.

Il lettore EasyOCR viene creato in modo lazy, cioe' solo quando serve davvero. Se EasyOCR non e' installato o non riesce a inizializzarsi, la pipeline non si ferma: il debug registra l'errore e il risultato rimane basato su Tesseract.

Nel JSON possono comparire informazioni come:

```json
"ic_marking_engine": "tesseract",
"ic_ocr_mode": "deep",
"ic_ocr_engines_used": ["tesseract", "easyocr"]
```

Questo permette di sapere quale motore ha prodotto il candidato selezionato e quali motori sono stati effettivamente provati.

### 7.7 Normalizzazione del testo

Il testo OCR viene normalizzato con `_normalize_text`.

La normalizzazione attuale è volutamente prudente:

```text
- uppercase
- rimozione spazi
- rimozione newline
- rimozione di punteggiatura esterna semplice
```

Esempio:

```text
" ne555 "  -> "NE555"
"LM 317T"  -> "LM317T"
```

Non vengono fatte correzioni aggressive. Per esempio, non si forza automaticamente `TDA7ON` in `TDA7000`. Questo tipo di correzione può essere utile, ma è meglio farla in una fase successiva, magari con un lookup su datasheet o con un agente AI.

### 7.8 Filtri anti falso positivo

Il modulo scarta candidati che non possono essere marking IC affidabili.

I principali filtri sono:

#### Testo troppo corto

Se il testo ha meno caratteri di `min_chars`, viene scartato.

#### Designator di componenti

Vengono scartate stringhe tipo:

```text
R1
C2
L1
D3
Q1
K1
S1
J1
TP1
IC1
U1
```

Queste stringhe identificano componenti o punti di test, non il modello dell'integrato.

#### Valori elettrici

Vengono scartati valori come:

```text
10UF
100NF
22PF
4.7K
12V
500MW
22UH
```

Questi testi sono tipici di resistori, condensatori, induttori, alimentazioni o note di circuito.

#### Testi senza lettere

Un marking IC deve contenere almeno una lettera. Una stringa solo numerica viene scartata.

### 7.9 Scoring dei candidati

Il candidato non viene scelto solo in base alla confidence OCR. Lo score combina più fattori.

La formula concettuale è:

```text
score = confidence OCR
      + bonus se contiene lettere e numeri
      + bonus se la lunghezza è realistica
      + bonus/penalità in base alla regione OCR
      - penalità per net label/pin label
```

I marking più comuni sono alfanumerici:

```text
NE555
TDA7000
LM317T
ADC0804
AT89S51
TPS63061
L298
```

Per questo il codice aggiunge un bonus quando il testo contiene sia lettere sia numeri.

Viene aggiunto anche un bonus se la lunghezza è realistica, indicativamente tra 4 e 14 caratteri.

La regione contribuisce allo score. In generale:

```text
body_inner     -> bonus alto
above_body     -> bonus medio
expanded_bbox  -> bonus basso
below_body     -> bonus basso
left/right     -> bonus nullo o molto basso
```

Questa scelta riflette il fatto che il nome dell'IC è più probabile dentro o sopra il corpo rispetto a zone laterali generiche.

### 7.10 Selezione finale

Tutti i candidati validi vengono ordinati per score. Il candidato con score più alto diventa:

```json
"ic_marking": "NE555"
```

Vengono salvati anche:

```json
"ic_marking_confidence": 0.91,
"ic_marking_bbox": [x1, y1, x2, y2],
"ic_marking_source_region": "body_inner",
"ic_marking_engine": "tesseract",
"ic_ocr_mode": "fast"
```

Se non viene trovato nessun candidato, il componente avrà:

```json
"ic_marking": null,
"ic_marking_confidence": 0.0
```

### 7.11 Debug OCR del marking

Il debug viene salvato in `ic_ocr_debug`.

Contiene:

```text
- enabled
- body_bbox
- selected
- candidate_count
- candidates
- regions
- engine_debug
- raw_words_easyocr, quando EasyOCR viene eseguito
```

Questo permette di capire se l'OCR ha fallito perché:

- non ha letto parole;
- ha letto parole ma sono state scartate;
- ha scelto un candidato sbagliato;
- la ROI non copriva bene il marking;
- il body_bbox era sbagliato.

---

## 8. OCR dei pin: logica implementata

La funzione principale del modulo pin è:

```python
enrich_ic_pin_ocr(component, image_bgr, meta)
```

Questa funzione lavora **dopo** la stima dei terminali geometrici e **dopo** la lettura del marking IC.

Il motivo è che il marking viene usato anche per evitare falsi positivi: se una parola OCR coincide con il nome dell'integrato, non deve essere assegnata come label di un pin.

### 8.1 Strategia scelta: `side_lane_candidates_v1`

La strategia attuale e' una strategia a corsie laterali:

```text
strategy: side_lane_candidates_v1
```

L'idea e' leggere il testo vicino ai lati dell'IC, ma assegnarlo sempre ai terminali geometrici gia' stimati. Il modulo non crea terminali nuovi: ogni parola OCR puo' solo arricchire un terminale esistente con `pin_number` o `pin_label_text`.

Rispetto alla prima idea a semplici strip laterali, la versione attuale usa:

- corsie associate ai terminali sul lato;
- Tesseract per numeri e label nelle bande laterali;
- fallback a componenti connessi per piccoli numeri difficili;
- EasyOCR per label interne solo se non e' gia' presente `ic_marking`;
- riparazioni post-OCR per duplicati, sequenze e assegnazioni incoerenti.

### 8.2 Perché non fare OCR per ogni pin

Fare OCR per ogni pin sembrerebbe più preciso, ma può diventare lento e instabile:

- ogni IC può avere molti terminali;
- ogni immagine può contenere più IC;
- ogni OCR ha overhead;
- i crop piccoli possono essere troppo poveri di contesto;
- i numeretti possono essere tagliati male.

Per questo la pipeline resta basata su OCR per regioni laterali e non su crop indipendenti per ogni terminale. I fallback locali vengono usati solo quando servono, ad esempio per recuperare numeri piccoli che Tesseract non ha letto bene nella banda principale.

### 8.3 Configurazione letta dal YAML

Il modulo legge i parametri da:

```text
ocr.pin_labels
```

I parametri principali sono:

```yaml
ocr:
  enabled: true

  pin_labels:
    enabled: true
    strategy: side_lane_candidates_v1
    engine: tesseract
    skip_component_subtypes: []
    number_ocr:
      enabled: true
      psm: 11
      min_confidence: 0.25
    label_ocr:
      enabled: true
      guard_numbers: true
      psm: 11
      min_confidence: 0.20
    lane_search:
      lane_padding_px: 6
      side_inside_px: 78
      side_outside_px: 42
      top_bottom_inside_px: 72
      top_bottom_outside_px: 42
      upscale: 3.0
      line_kernel_ratio: 0.33
      component_fallback_enabled: true
    attach:
      max_number_distance_px: 42
      max_label_distance_px: 86
      reject_overlap_ratio: 0.50
    number_pattern: '^[1-9][0-9]?$'
    label_pattern: '^[A-Za-z][A-Za-z0-9_./+\-]{0,15}$'
    easyocr_fallback:
      enabled: true
    store_debug: false
```

I valori possono essere modificati nel YAML senza cambiare codice.

La politica `skip_when_marking_and_number` ha default `true` nel codice: se non viene specificata nel YAML, resta comunque attiva.

### 8.4 Reset e skip iniziali

La funzione controlla prima se OCR e pin OCR sono abilitati. Se non lo sono, salva nel debug:

```json
{
  "enabled": false,
  "reason": "pin_ocr_disabled_in_yaml"
}
```

Poi controlla la strategia. Se la strategia configurata non e' quella supportata, il modulo non procede e registra il motivo nel debug.

Il campo `skip_component_subtypes` esiste ancora, ma nella configurazione attuale i display a 7 segmenti non vengono saltati. Passano nella stessa pipeline OCR degli altri IC e vengono filtrati dopo con regole di dominio molto generali.

### 8.5 Raggruppamento dei terminali per lato

Il modulo usa il campo:

```json
"relative_position": "left"
```

per raggruppare i terminali in quattro insiemi:

```text
left
right
top
bottom
```

Questa fase e' gestita dalla costruzione delle side lanes: ogni terminale sul lato genera una corsia OCR coerente con la sua posizione.

Se non ci sono terminali IC, il modulo non fa OCR e scrive:

```json
"reason": "no_ic_terminals"
```

### 8.6 Costruzione delle corsie laterali

La funzione `_build_side_lanes` costruisce le regioni OCR attorno ai lati del body bbox.

La regione include:

- una parte **interna** al corpo;
- una parte **esterna** al corpo;
- un piccolo padding lungo il lato.

Questo è necessario perché la posizione dei testi non è sempre uguale.

Esempio lato sinistro:

```text
        corpo IC
        +----------------+
numero  | label          |
  2  ---| VIN            |
        |                |
  3  ---| EN             |
        +----------------+
```

In alcuni schemi il numero è fuori dal corpo e la label è dentro. In altri casi il numero è sul bordo o addirittura dentro. Per questo la regione OCR deve attraversare il bordo del package.

Per il lato sinistro, concettualmente:

```text
x: da body_x1 - outside a body_x1 + inside
y: da body_y1 - pad     a body_y2 + pad
```

Per il lato destro:

```text
x: da body_x2 - inside  a body_x2 + outside
y: da body_y1 - pad     a body_y2 + pad
```

Per top e bottom si applica la stessa logica ruotata.

### 8.7 Preprocessing per pin OCR

Il preprocessing dei pin resta mirato a testi piccoli e tecnici:

```text
1. grayscale
2. aumento di scala
3. equalizzazione/contrasto quando utile
4. soglia binaria
5. rimozione di linee lunghe che possono disturbare le cifre
6. inversione se serve
```

Il principio e' togliere il piu' possibile fili e bordi lunghi, lasciando leggibili numeri e label brevi.

### 8.8 OCR con Tesseract, componenti connessi ed EasyOCR

La funzione `_run_tesseract_words` esegue Tesseract sulle regioni laterali.

Anche qui viene usato `image_to_data`, in modo da ottenere:

- testo;
- confidence;
- bbox locale;
- numero di parole lette.

La whitelist dei pin è:

```text
ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_./+-
```

Questa whitelist permette label come:

```text
VIN
VOUT
GND
VREF/2
P1.0
D0
D1
BOOT
FB
```

Per i numeri piccoli il modulo usa anche `_component_number_words`: prima cerca piccoli gruppi grafici compatibili con cifre, poi esegue Tesseract su quei micro-crop. Questo fallback e' utile per casi in cui il numero e' troppo sottile o vicino al bordo.

EasyOCR sui pin non viene usato come lettura universale. Viene usato come fallback per label interne al body solo quando non esiste `ic_marking`. Se invece il marking e' presente, la lettura EasyOCR delle label interne viene saltata con motivo:

```text
ic_marking_present_datasheet_preferred
```

Questa scelta riduce falsi positivi sul corpo dell'integrato e segue la politica datasheet-first.

In pratica l'ordine desiderato per ogni terminale e':

```text
1. prova a leggere pin_number;
2. se pin_number e ic_marking sono presenti, non serve conservare la label OCR;
3. se pin_number manca, prova a conservare pin_label_text come evidenza utile;
4. se manca anche la label, il terminale resta solo geometrico.
```

### 8.9 Normalizzazione del testo pin

Le funzioni di normalizzazione dei pin mantengono una logica prudente.

Fa operazioni leggere:

```text
- uppercase
- rimozione spazi
- rimozione newline
- rimozione punteggiatura esterna
- conversione di \ in /
- correzioni leggere di alias OCR frequenti
```

Per i pin non si scartano parole come `VIN`, `GND`, `FB`, `EN`, perché queste sono proprio label importanti.

Questa è una differenza fondamentale rispetto al marking: una parola come `VIN` non deve diventare nome IC, ma può essere una label pin corretta.

Sono previste anche normalizzazioni mirate, ad esempio:

```text
P17   -> P1.7
NTR   -> INTR
VREFI2 -> VREF/2
```

Per i display a 7 segmenti, e solo per quel sottotipo, vengono accettate anche correzioni compatibili con i segmenti, ad esempio `4 -> a` e `q -> g`.

---

## 9. Classificazione delle parole OCR dei pin

Ogni parola letta sulla strip viene classificata come:

```text
number
label
None
```

Nel codice attuale non e' una singola regola rigida: i numeri passano da pattern e scoring numerico, mentre le label passano da normalizzazione, filtri di guardia e validazione tramite `_is_label_candidate`.

### 9.1 Scarto del nome IC

Se la parola letta coincide con `ic_marking`, viene scartata.

Esempio:

```text
IC marking: LM317T
parola OCR: LM317T
```

Quella parola è il nome dell'integrato, non una label pin.

Questo filtro è importante perché le strip laterali possono includere anche una parte del corpo centrale del componente.

### 9.2 Scarto di watermark o siti web

Se il testo contiene stringhe come:

```text
WWW
CIRCUIT
```

viene scartato. Questo evita che watermark o testi del sito sorgente entrino nel JSON come label pin.

### 9.3 Scarto di valori elettrici

I valori elettrici vengono scartati:

```text
10UF
100NF
4.7K
12V
22UH
500MW
```

Questi testi appartengono a componenti vicini, non ai pin del circuito integrato.

### 9.4 Riconoscimento dei numeri pin

Una parola è considerata `pin_number` se rispetta il pattern:

```regex
^[1-9][0-9]?$
```

Esempi validi:

```text
1
2
3
10
13
16
31
40
```

La configurazione attuale accetta numeri da 1 a 99. Questo e' coerente con gli IC presenti nel batch e riduce falsi positivi come `0` isolato o numeri troppo grandi letti da testi esterni.

### 9.5 Riconoscimento delle label pin

Una parola è considerata `pin_label_text` se rispetta il pattern:

```regex
^[A-Za-z][A-Za-z0-9_./+\-]{0,15}$
```

Esempi validi:

```text
VIN
VOUT
GND
EN
FB
PG
BOOT
COMP
SYNC
PHASE
P1.0
D0
VREF/2
```

### 9.6 Designator fuori dal body

Il codice tratta con attenzione stringhe come:

```text
L1
D1
C1
R1
Q1
```

Queste possono essere designator di componenti esterni, ma in alcuni IC possono anche essere label pin interne. Esempio: in alcuni convertitori switching `L1`, `L2`, `D0`, `D1` possono comparire dentro il corpo del componente.

Per questo la regola è:

```text
se sembra un designator ed è fuori dal body -> scarta
se sembra un designator ma è dentro il body -> può essere label pin
```

Questa è una scelta prudente e utile, perché evita di scartare label valide dentro il package.

### 9.7 Politica datasheet-first

Una regola importante introdotta per evitare overfitting e falsi positivi e':

```text
se esistono ic_marking e pin_number, non serve conservare anche pin_label_text
```

In quel caso la label OCR viene cancellata dal terminale e il debug registra:

```text
label_cleared_reason = ic_marking_and_pin_number_present
```

Il motivo e' pratico: se conosco il componente (`ic_marking`) e conosco il numero del pin (`pin_number`), la funzione del pin puo' essere recuperata in modo piu' robusto dal datasheet. Questo riduce l'uso di OCR dove non serve.

La label viene invece cercata e conservata quando manca il `pin_number`. Esempi tipici:

```text
IN
OUT
ADJ
CS
P1.7
```

In questi casi la label e' l'unica evidenza disponibile nello schema.

---

## 10. Associazione parola OCR -> terminale geometrico

Dopo aver classificato una parola come `number` o `label`, bisogna associarla a un terminale.

La regola generale e':

```text
una parola può essere assegnata solo a un terminale dello stesso lato
```

Quindi una parola letta nella strip sinistra può essere assegnata solo a terminali con:

```json
"relative_position": "left"
```

### 10.1 Distanza lungo il lato

La funzione `_axis_distance_for_side` calcola una distanza 1D.

Per i lati verticali:

```text
left/right -> distanza verticale tra parola e terminale
```

quindi usa la coordinata `y`.

Per i lati orizzontali:

```text
top/bottom -> distanza orizzontale tra parola e terminale
```

quindi usa la coordinata `x`.

Questa scelta funziona perché su un lato i pin sono ordinati lungo una sola direzione.

### 10.2 Corsia piu' plausibile

La logica di assegnazione lavora sulle corsie laterali. Una parola letta su un lato viene confrontata con i terminali di quel lato e assegnata alla corsia piu' plausibile.

Se la distanza supera:

```text
max_attach_distance_px
```

la parola non viene assegnata a nessun terminale.

Questo parametro è molto importante: se è troppo piccolo, perdiamo label corrette; se è troppo grande, assegniamo testi al terminale sbagliato.

### 10.3 Score del candidato

Se una parola è abbastanza vicina a un terminale, viene calcolato uno score:

```text
score = confidence OCR
      - penalità per distanza
      + bonus label dentro body
      + bonus number fuori body
```

Il bonus `label inside` riflette il fatto che le label funzionali dei pin sono spesso scritte dentro il corpo dell'IC.

Il bonus `number outside` riflette il fatto che i numeri pin sono spesso scritti vicino al bordo o fuori dal corpo.

Questi bonus sono leggeri, non assoluti, perché negli schemi reali la posizione può variare.

### 10.4 Miglior candidato per terminale

Per ogni terminale il modulo mantiene al massimo:

```text
miglior candidato number
miglior candidato label
```

Se due parole candidate competono per lo stesso campo, vince quella con score piu' alto.

Internamente questo permette anche di valutare contemporaneamente:

```json
"pin_number": "2",
"pin_label_text": "VIN"
```

ma evita di salvare piu' numeri o piu' label nello stesso terminale. Se poi sono presenti `ic_marking` e `pin_number`, la politica datasheet-first puo' cancellare la label dal JSON finale.

---

## 11. Output JSON dei pin

Quando l'OCR dei pin trova un numero, aggiunge al terminale:

```json
"pin_number": "2",
"pin_number_confidence": 0.71,
"pin_number_bbox": [x1, y1, x2, y2]
```

Quando trova una label, aggiunge:

```json
"pin_label_text": "VIN",
"pin_label_confidence": 0.82,
"pin_label_bbox": [x1, y1, x2, y2]
```

Se trova entrambi durante l'assegnazione interna:

```json
{
  "terminal_id": "11.1:left_2",
  "name": "left_2",
  "relative_position": "left",
  "x": 420.0,
  "y": 250.0,
  "pin_number": "2",
  "pin_label_text": "VIN",
  "pin_number_confidence": 0.71,
  "pin_label_confidence": 0.82
}
```

Nel JSON finale, pero', questo caso viene mantenuto solo quando non c'e' abbastanza contesto per usare il datasheet. Se il componente ha `ic_marking` e il terminale ha `pin_number`, `pin_label_text` viene riportato a `null` per evitare di fidarsi inutilmente di una label OCR potenzialmente rumorosa.

Se trova solo il numero:

```json
{
  "terminal_id": "11.1:right_1",
  "name": "right_1",
  "pin_number": "3",
  "pin_label_text": null
}
```

Se trova solo la label:

```json
{
  "terminal_id": "11.1:bottom_1",
  "name": "bottom_1",
  "pin_number": null,
  "pin_label_text": "ADJ"
}
```

Se non trova nulla:

```json
{
  "terminal_id": "11.1:left_1",
  "name": "left_1",
  "pin_number": null,
  "pin_label_text": null
}
```

Nel JSON pubblico è corretto mantenere `pin_number` e `pin_label_text` anche quando sono `null`, almeno per gli IC. In questo modo è immediatamente chiaro che il terminale è stato considerato, ma l'OCR non ha trovato quel campo.

---

## 12. Debug dell'OCR dei pin

Il modulo salva un debug compatto nel componente:

```json
"ic_pin_ocr_debug": {
  "enabled": true,
  "strategy": "side_lane_candidates_v1",
  "engine": "tesseract",
  "body_bbox": [x1, y1, x2, y2],
  "assigned_count": 5,
  "side_count": 4,
  "side_regions": [ ... ]
}
```

Per ogni lato viene salvato:

```text
side
bbox della regione/corsia OCR
numero terminali su quel lato
engine_debug
raw_words
accepted_words
rejected_words
assignments
component_number_fallback, quando usato
body_label_ocr, quando EasyOCR sulle label viene eseguito o saltato
```

Questo debug serve per capire rapidamente se il problema è:

- Tesseract non ha letto nulla;
- Tesseract ha letto male;
- la parola è stata scartata dal filtro;
- la parola era troppo lontana dal terminale;
- la parola è stata assegnata al terminale sbagliato;
- il body_bbox o la strip non coprono bene il testo.

A livello terminale viene salvato:

```json
"pin_ocr_debug": {
  "number": { ... },
  "label": { ... }
}
```

Questo è utile per controllare singolarmente ogni terminale.

---

## 13. Casi reali osservati

### 13.1 IC con solo numeri pin: TDA7000

Nel caso del `TDA7000`, molti schemi mostrano quasi solo numeri attorno al package:

```text
13, 1, 3, 4, 8, 12, 15, 17, 18, 11, 10, 7, 9, 2, 5, 6, 14, 16
```

Le label funzionali non sempre sono presenti nello schema. In questo caso il JSON ideale avrà molti `pin_number`, ma `pin_label_text` spesso `null`.

La funzione elettrica del pin verrà recuperata successivamente dal datasheet usando:

```text
ic_marking = TDA7000
pin_number = 13
```

### 13.2 IC con solo label: LM317T

Nel caso `LM317T`, spesso nello schema compaiono label funzionali:

```text
IN
OUT
ADJ
```

ma possono mancare i numeri fisici dei pin.

In questo caso il JSON ideale è:

```json
{
  "pin_number": null,
  "pin_label_text": "IN"
}
```

La mancanza del numero non è un errore: lo schema semplicemente non lo mostra.

### 13.3 IC con numero e label: TPS63061 / ISL85410

In molti schemi più moderni, specialmente per regolatori switching o microcontrollori, vengono mostrati sia numeri sia label:

```text
1 L1
2 VIN
3 EN
8 FB
9 VOUT
```

Questo è il caso migliore per la pipeline, perché permette di collegare direttamente geometria, numero e label.

### 13.4 IC con bus e pin digitali: ADC0804 / AT89S51

In schemi con convertitori ADC o microcontrollori possono comparire label come:

```text
D0
D1
D2
P1.0
P3.7
INTR
RD
WR
CS
```

Queste label sono importanti e non devono essere scartate come designator. Per questo il filtro sui designator viene applicato in modo prudente: fuori dal body vengono scartati, dentro il body possono essere accettati come label pin.

### 13.5 Display a 7 segmenti

I display a 7 segmenti possono essere rilevati come oggetti rettangolari multipin, quindi possono assomigliare a IC. Però semanticamente sono un caso diverso.

Un display con punto decimale può avere terminali logici:

```text
a
b
c
d
e
f
g
h / DP
com
```

quindi nello schema può apparire come un componente con 9 terminali logici. Fisicamente alcuni display hanno 10 pin perché il comune è duplicato, ma nello schema può essere rappresentato con un solo `com`.

Per la pipeline vengono trattati come sottotipo:

```json
"component_subtype": "seven_segment_display"
```

Non vengono pero' gestiti con una strategia separata e hardcoded. Passano nello stesso OCR pin degli altri `Integrated_Circuit`.

La differenza e' solo nel filtro di dominio applicato dopo:

- sono accettate label singole `a`, `b`, `c`, `d`, `e`, `f`, `g`, `h`;
- e' accettata la label `com`;
- vengono rimossi terminali extra non coerenti, mantenendo al massimo 9 terminali logici;
- non vengono creati campi separati come `semantic_terminal_name` o `semantic_terminal_id`.

Questa scelta mantiene il comportamento semplice: anche per un display il risultato resta un terminale geometrico (`left_1`, `right_2`, ecc.) arricchito, quando possibile, con `pin_label_text`.

---

## 14. Perché non affidarsi subito al datasheet

Una possibile alternativa sarebbe:

```text
prendo il crop dell'IC
lo mando a un agente AI
l'agente cerca il datasheet
l'agente deduce i pin
```

Questa idea può essere utile in futuro, ma non dovrebbe sostituire la pipeline locale.

Il motivo è che il datasheet descrive il package reale del componente, mentre lo schema elettrico può rappresentare il componente in modo logico o semplificato.

In uno schema:

- alcuni pin possono essere omessi;
- alcuni pin possono essere raggruppati;
- il simbolo può non rispettare la disposizione fisica del package;
- la label può essere più importante del numero;
- il `com` di un display può essere rappresentato una sola volta anche se fisicamente è duplicato;
- un alimentatore può mostrare solo `IN`, `OUT`, `ADJ` senza numeri.

Quindi il datasheet è utilissimo per interpretare, ma prima dobbiamo estrarre dallo schema:

```text
ic_marking
terminal_id geometrico
pin_number, se visibile
pin_label_text, se visibile
net collegata al terminale
```

Solo dopo ha senso chiedere a un agente:

```text
Dato l'IC LM317T, questo terminale è etichettato OUT e collegato a questa net: che funzione ha nel circuito?
```

Il datasheet deve essere una fase di interpretazione, non la fase che crea la topologia.

---

## 15. Perché usare Tesseract in questa fase

Tesseract resta il motore principale perché:

- è relativamente leggero;
- è configurabile;
- permette whitelist di caratteri;
- permette di scegliere il PSM;
- restituisce confidence e bounding box;
- è semplice da integrare nella pipeline;
- non richiede modelli pesanti come alcune OCR neurali.

Nel caso dei circuiti integrati non stiamo leggendo frasi naturali, ma testi tecnici brevi:

```text
NE555
LM317T
VIN
GND
FB
13
40
```

Questo tipo di testo è compatibile con una OCR configurata con whitelist e preprocessing mirato.

Il principale problema di Tesseract resta la lettura dei numeri piccoli dei pin. Per questo la strategia attuale resta volutamente conservativa: usa Tesseract come base, ma aggiunge fallback solo dove servono.

Per compensare questo limite, il codice attuale non usa solo la lettura Tesseract standard: aggiunge anche fallback grafici sui componenti connessi per recuperare cifre piccole e usa EasyOCR in modo selettivo.

---

## 16. Prestazioni e scelta progettuale

La pipeline deve rimanere abbastanza veloce. Per questo sono state fatte scelte conservative.

### 16.1 Marking IC

Per il marking vengono lette poche ROI per ogni IC. Questo è accettabile perché ogni componente ha un solo nome da leggere.

### 16.2 Pin OCR

Per i pin si usa una OCR per lato, non una OCR per terminale.

Questo riduce il numero di chiamate a Tesseract:

```text
massimo 4 OCR per IC
```

invece di:

```text
una OCR per ogni terminale
```

Su IC con molti pin la differenza è importante.

### 16.3 EasyOCR e altri motori

EasyOCR e' gia' integrato, ma in modo controllato.

Nel marking IC viene usato come fallback quando Tesseract non basta. Nei pin viene usato per leggere label interne solo quando non e' presente `ic_marking`.

La strategia attuale e':

```text
1. Tesseract veloce su tutti gli IC.
2. EasyOCR sul marking solo se serve.
3. EasyOCR sulle label pin solo se manca ic_marking.
4. Fallback locale sui numeri piccoli tramite componenti connessi.
```

Questa strategia evita di rallentare tutto il dataset.

---

## 17. Limiti attuali della strategia pin

La strategia a corsie laterali e' utile, ma ha limiti chiari.

### 17.1 Numeri pin molto piccoli

I numeri dei pin sono spesso piccoli, sottili e vicini al bordo dell'IC. Tesseract può leggere male:

```text
13 -> 1
15 -> 5
8  -> 0
1  -> I
7  -> /
```

Questo è il problema più difficile.

### 17.2 Testi sovrapposti ai fili

Se un numero è attraversato o vicino a un filo, l'OCR può confondere il filo con un tratto del carattere.

### 17.3 Distanza dal terminale

La soglia `max_attach_distance_px` è delicata. Se il testo è lontano dal terminale, può non essere associato. Se la soglia è troppo grande, può essere associato al terminale sbagliato.

### 17.4 Bbox del corpo non perfetto

Se il `body_bbox` è sbagliato, anche le strip OCR saranno sbagliate.

Il miglioramento del body bbox migliora direttamente sia la stima dei terminali sia l'OCR.

### 17.5 Schemi con molti pin ravvicinati

Su package molto densi, parole vicine possono cadere nella stessa area e diventare difficili da separare.

### 17.6 Label corte

Label come `EN`, `FB`, `PG`, `CS`, `RD`, `WR` sono utili ma corte. Le parole corte sono più facili da confondere con rumore.

---

## 18. Possibili miglioramenti futuri

La versione attuale e' una strategia locale e veloce. I miglioramenti possibili sono molti.

### 18.1 Debug image dei pin

La debug image `ic_ocr` mostra gia' il marking e i valori finali selezionati per `pin_number` e `pin_label_text`.

Un miglioramento futuro potrebbe essere una vista ancora piu' diagnostica con:

- body bbox in ciano;
- corsie OCR in grigio o viola;
- parole accettate in verde;
- parole scartate in rosso/arancione;
- terminali IC in arancione;
- linee leggere tra parola e terminale assegnato;
- etichetta finale `number/label` vicino al terminale.

Questo aiuterebbe molto a capire perché un pin è stato assegnato male.

### 18.2 OCR locale solo sui casi incerti

Invece di fare OCR per ogni pin, si potrebbe mantenere la strategia veloce e aggiungere un fallback solo dove serve:

```text
se un terminale non ha pin_number
oppure ha confidence bassa
oppure l'IC ha molti pin e il numero è sospetto
allora esegui OCR locale su un piccolo crop vicino al terminale
```

Questo migliorerebbe la precisione senza rallentare troppo.

### 18.3 Componenti connessi per i numeri

Per i numeri molto piccoli il codice usa gia' una logica grafica:

```text
1. binarizzare la strip;
2. rimuovere linee lunghe;
3. trovare piccoli componenti connessi;
4. raggruppare componenti vicini;
5. passare questi micro-crop a Tesseract.
```

Questa strategia aiuta soprattutto con numeri a due cifre come `13`, `15`, `16`. Un miglioramento futuro puo' essere renderla ancora piu' robusta su testi molto degradati o attaccati ai fili.

### 18.4 Post-processing con plausibilità del pin count

Se un IC ha 8 terminali geometrici e viene letto `pin_number = 40`, probabilmente c'è un errore OCR. Una fase futura potrebbe controllare la plausibilità rispetto al numero di terminali visibili.

Bisogna però essere cauti: non sempre lo schema mostra tutti i pin fisici del package.

### 18.5 Lookup datasheet

Una volta ottenuti:

```text
ic_marking
pin_number
pin_label_text
```

si può usare un agente AI o un modulo dedicato per cercare il datasheet e risolvere:

```text
NE555 pin 3 -> OUT
LM317T ADJ -> Adjust terminal
ADC0804 D0 -> data bit 0
```

Questa fase dovrebbe produrre campi nuovi, ad esempio:

```json
"pin_function_datasheet": "OUTPUT",
"pin_function_confidence": 0.95,
"datasheet_source": "..."
```

ma non dovrebbe modificare la topologia del grafo.

---

## 19. JSON pubblico consigliato per gli IC

Un componente `Integrated_Circuit` nel JSON pubblico dovrebbe contenere almeno:

```json
{
  "component_id": "11.1",
  "instance_id": "11.1",
  "class_name": "Integrated_Circuit",
  "bbox": [100, 100, 200, 300],
  "body_bbox": [110, 120, 190, 290],
  "ic_marking": "NE555",
  "ic_marking_confidence": 0.91,
  "ic_marking_bbox": [130, 180, 170, 200],
  "ic_marking_source_region": "body_inner",
  "terminals": [
    {
      "terminal_id": "11.1:left_1",
      "name": "left_1",
      "display_name": "left_1",
      "relative_position": "left",
      "x": 110,
      "y": 150,
      "pin_number": "2",
      "pin_label_text": null
    },
    {
      "terminal_id": "11.1:right_1",
      "name": "right_1",
      "display_name": "right_1",
      "relative_position": "right",
      "x": 190,
      "y": 180,
      "pin_number": "3",
      "pin_label_text": null
    }
  ]
}
```

Nel debug completo possono rimanere anche:

```text
ic_ocr_debug
ic_pin_ocr_debug
pin_ocr_debug
connection_side_scores
terminal_point_debug
```

Nel JSON pubblico, invece, conviene tenere solo ciò che serve alla fase successiva.

Se `ic_marking` e `pin_number` sono entrambi presenti, `pin_label_text` puo' essere `null` anche se l'OCR aveva letto una possibile label: in quel caso la funzione del pin verra' recuperata dal datasheet.

---

## 20. Ruolo del datasheet e dell'agente AI finale

La pipeline OCR non deve necessariamente capire tutto. Deve produrre un JSON abbastanza ricco e affidabile da permettere a un agente AI di ragionare.

L'agente finale potrebbe ricevere:

```json
{
  "ic_marking": "NE555",
  "terminals": [
    {
      "terminal_id": "11.1:right_1",
      "pin_number": "3",
      "pin_label_text": null,
      "connected_net": "net_12"
    }
  ]
}
```

Poi può cercare il datasheet e arricchire:

```json
{
  "terminal_id": "11.1:right_1",
  "pin_number": "3",
  "datasheet_pin_name": "OUT",
  "datasheet_pin_description": "Output pin of the timer"
}
```

Oppure, nel caso di `LM317T`:

```json
{
  "terminal_id": "11.1:left_1",
  "pin_number": null,
  "pin_label_text": "IN"
}
```

L'agente può usare direttamente la label `IN`, anche senza numero.

Quindi la regola è:

```text
se ho pin_number -> posso cercare nel datasheet per numero
se ho pin_label_text -> posso cercare nel datasheet per nome funzione
se ho ic_marking + pin_number -> preferisco il datasheet e posso ignorare la label OCR
se non ho nessuno dei due -> uso solo la posizione geometrica e la net
```

---

## 21. Stato attuale della strategia

Lo stato attuale è:

```text
- terminali IC stimati geometricamente;
- marking IC letto con Tesseract su ROI mirate;
- EasyOCR usato come fallback/consenso per il marking quando serve;
- pin OCR implementato con corsie laterali side_lane_candidates_v1;
- fallback a componenti connessi per piccoli numeri di pin;
- EasyOCR sulle label pin usato solo quando manca ic_marking;
- policy datasheet-first: se ci sono ic_marking e pin_number, la label OCR viene cancellata;
- display a 7 segmenti trattati come sottotipo, ma passati nella stessa OCR pin;
- output JSON arricchito con pin_number e pin_label_text;
- debug JSON disponibile;
- debug image ic_ocr con marking e valori finali dei pin selezionati.
```

La parte più solida al momento è la lettura del marking IC. La parte più difficile è la lettura dei numeri dei pin, soprattutto quando sono piccoli o degradati.

---

## 22. Conclusione

La strategia adottata è corretta perché mantiene separati i livelli:

```text
1. rilevamento oggetti
2. identificazione istanze
3. terminali geometrici
4. OCR marking
5. OCR pin
6. skeleton e grafo
7. datasheet e interpretazione AI
```

Questa separazione protegge il grafo dagli errori OCR. Anche se Tesseract legge male un numero, il terminale geometrico resta valido e collegato correttamente.

Il contributo principale dei moduli OCR è arricchire il JSON con evidenze utili:

```text
Integrated_Circuit 11.1 -> NE555
terminal left_2 -> pin_number 2
terminal bottom_1 -> pin_label_text ADJ, se il numero non e' visibile
```

Queste informazioni saranno fondamentali per la fase successiva, dove un agente AI potrà cercare datasheet, interpretare la funzione dei pin e ragionare sul possibile problema del circuito.

La direzione futura consigliata è:

```text
1. consolidare il debug dei pin con immagini dedicate;
2. mantenere veloce la strategia a corsie laterali;
3. aggiungere fallback locale solo sui pin incerti;
4. non creare terminali da OCR;
5. usare datasheet/AI solo dopo avere una base geometrica affidabile.
```
