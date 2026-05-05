# Strategia OCR per circuiti integrati nella pipeline di analisi schemi elettrici

## 1. Scopo del documento

Questo documento descrive la strategia aggiornata per leggere, tramite OCR, il **nome/marking dei circuiti integrati** rilevati nella pipeline di analisi degli schemi elettrici.

Lo stato attuale è il seguente:

- gli `Integrated_Circuit` vengono rilevati da YOLO nello script 01;
- nello script 02 ricevono un `instance_id` univoco;
- nello script 03 vengono stimati i terminali geometrici dell'integrato guardando dove i fili toccano il corpo del componente;
- sempre nello script 03 viene chiamato il modulo `ocr_integrated_circuit.py`, che arricchisce il componente con il nome OCR dell'integrato;
- i pin singoli non vengono ancora letti con OCR: questa sarà la fase successiva.

Quindi, per ora, l'obiettivo non è ancora ottenere:

```text
pin 1 = GND
pin 2 = TRIGGER
pin 3 = OUT
...
```

ma ottenere in modo affidabile:

```text
IC 11.1 = NE555
IC 11.1 = TDA7000
IC 11.1 = LM317T
IC 11.1 = TPS63061
```

Questo nome verrà poi usato da un agente AI o da una fase successiva per cercare il datasheet e interpretare il significato dei pin.

---

## 2. Principio principale: geometria prima, OCR dopo

Il principio più importante rimane questo:

```text
I terminali non devono nascere dall'OCR.
I terminali devono nascere dalla geometria dei fili.
```

Questo significa che l'OCR non decide se un terminale esiste. Il terminale esiste se un filo entra o esce dal corpo del circuito integrato.

La sequenza corretta è:

```text
1. YOLO rileva il componente Integrated_Circuit.
2. Lo script 02 assegna un instance_id stabile.
3. Lo script 03 calcola o recupera il body_bbox del circuito integrato.
4. Lo script 03 trova i terminali geometrici sui quattro lati.
5. Solo dopo, l'OCR prova a leggere il marking dell'integrato.
6. Il testo OCR viene salvato come informazione semantica, senza alterare la topologia.
```

Questa separazione è fondamentale perché negli schemi elettrici ci sono moltissimi testi vicini agli IC che non sono nomi di integrati:

```text
IC1
IC2
U1
R1
C2
D3
Q1
10uF
100nF
+12V
GND
VIN
VOUT
OUT
ADJ
COM
www.circuitstoday.com
```

Se usassimo l'OCR per creare terminali o per prendere decisioni topologiche, rischieremmo molti falsi positivi. Per questo la topologia resta geometrica, mentre l'OCR aggiunge solo informazione descrittiva.

---

## 3. Responsabilità dei file coinvolti

### 3.1 `strategies_integrated_circuit.py`

Questo file si occupa della parte geometrica degli IC:

- recupera o raffina il `body_bbox`;
- scansiona i lati del corpo;
- cerca i contatti filo-corpo;
- crea terminali provvisori come `left_1`, `right_2`, `top_1`, `bottom_1`;
- non legge testo.

Questa fase deve restare indipendente dall'OCR.

### 3.2 `ocr_integrated_circuit.py`

Questo file si occupa dell'OCR del marking IC:

- recupera il `body_bbox`;
- costruisce ROI mirate;
- esegue Tesseract;
- eventualmente esegue EasyOCR come fallback;
- normalizza il testo letto;
- filtra parole non valide;
- assegna uno score ai candidati;
- calcola un consenso tra letture diverse;
- sceglie il miglior candidato;
- salva i campi OCR nel JSON del componente.

Attualmente legge solo il nome del circuito integrato, non i pin.

### 3.3 `03_estimate_terminals.py`

Questo script coordina la fase 03:

- legge il JSON prodotto dallo script 02;
- carica l'immagine originale;
- stima i terminali;
- chiama l'arricchimento OCR per gli `Integrated_Circuit`;
- salva il JSON aggiornato;
- salva le immagini di debug.

È corretto che l'OCR stia qui e non nello script 04 o 05, perché nello script 03 abbiamo ancora:

- immagine originale BGR;
- bbox componenti;
- body_bbox IC;
- terminali stimati;
- accesso alle informazioni del YAML.

### 3.4 `debug_draw.py`

Questo file disegna le immagini di debug.

Attualmente abbiamo due famiglie di immagini:

```text
debug_images/
  ic1_terminals.jpg
  ic2_terminals.jpg

  ic_ocr/
    ic1_ic_ocr.jpg
    ic2_ic_ocr.jpg
```

Le immagini `_terminals.jpg` mostrano terminali e componenti.

Le immagini `_ic_ocr.jpg` sono dedicate solo al controllo del marking OCR degli IC.

---

## 4. Differenza tra `bbox`, `body_bbox` e ROI OCR

Per gli IC dobbiamo distinguere tre aree diverse.

### 4.1 `bbox` YOLO

È il rettangolo prodotto dal modello YOLO.

Può includere:

- il corpo dell'integrato;
- fili entranti;
- numeri dei pin;
- label dei pin;
- scritte vicine;
- componenti molto vicini.

È utile come riferimento generale, ma non è ideale per OCR o mascheramento preciso.

### 4.2 `body_bbox`

È il rettangolo reale del corpo dell'integrato.

È molto più importante perché rappresenta il package/simbolo IC vero e proprio.

Il modulo OCR lo recupera con questa priorità:

```text
1. component["body_bbox"]
2. component["connection_side_scores"]["body_bbox"]
3. terminal_point_debug["body_bbox"] dentro i terminali
4. fallback su component["bbox"]
```

Questa priorità rende il modulo robusto: se in futuro cambiamo dove viene salvato il `body_bbox`, il sistema ha comunque più possibilità di trovarlo.

### 4.3 ROI OCR

Le ROI OCR sono aree più piccole o più specifiche costruite a partire dal `body_bbox`.

Non leggiamo tutto lo schema. Leggiamo solo regioni mirate attorno o dentro l'IC.

Questo è fondamentale perché il nome dell'integrato può stare:

- dentro il corpo;
- in alto dentro il package;
- sopra il corpo;
- in una riga centrale;
- molto vicino al bordo superiore;
- in una ROI più larga quando il testo è difficile.

---

## 5. ROI usate attualmente per leggere il marking

Il file `ocr_integrated_circuit.py` costruisce più regioni candidate.

Alcune regioni sono generiche e vengono lette anche in modalità `fast`; altre vengono aggiunte in modalità `deep` quando la lettura veloce non è sufficiente.

### 5.1 `body_inner`

È la ROI interna principale.

Non coincide con tutto il `body_bbox`: viene ristretta con margini percentuali, perché vicino ai bordi ci sono spesso:

- numeri dei pin;
- label dei pin;
- fili;
- bordo del rettangolo;
- scritte tipo `IC1`.

La ROI `body_inner` serve per casi come:

```text
NE555
TDA7000
LM317T
LM1875
TDA1553
TC4423
L298
```

### 5.2 `above_body`

È la regione sopra il corpo IC.

Serve quando il part number non è dentro il rettangolo, ma sopra.

Esempi:

```text
TPS63061
ISL85410 / ISL854102
```

### 5.3 `below_body`, `left_of_body`, `right_of_body`

Sono regioni laterali o inferiori.

Per il marking IC sono meno affidabili, ma possono essere utili in casi particolari.

Nel ranking ricevono meno peso rispetto alle regioni interne.

### 5.4 `expanded_bbox`

È una ROI più ampia attorno al corpo.

È utile perché alcuni motori OCR funzionano meglio quando hanno un po' più di contesto. Però è anche la regione più rischiosa, perché può contenere:

- valori di componenti vicini;
- watermark;
- testi di rete;
- nomi di altri componenti;
- sigle non collegate all'IC.

Per questo il codice applica un filtro speciale: se un candidato viene da `expanded_bbox`, il centro del suo bbox testuale deve cadere dentro o molto vicino al `body_bbox`.

In questo modo si evita che una parola lontana diventi marking dell'integrato.

### 5.5 `body_top_marking`

È una ROI stretta nella parte alta del corpo.

Serve soprattutto per package disegnati con part number in alto, come:

```text
TPS63061
ISL85410
```

Questa regione usa normalmente `psm 7`, perché il testo atteso è una riga breve.

### 5.6 `body_top_text_line`

Questa regione viene costruita dinamicamente in modalità `deep`.

Il codice non assume una posizione fissa. Cerca invece una banda orizzontale con abbastanza pixel scuri nella parte alta del corpo.

L'idea è:

```text
se il part number è in alto, dovrebbe formare una riga scura compatta.
```

Questa ROI è utile quando il testo non è perfettamente allineato alla fascia statica `body_top_marking`.

### 5.7 `body_top_marking_tight` e bande extra

In modalità `deep` vengono aggiunte anche ROI più strette e leggermente spostate:

```text
body_top_marking_tight
body_top_marking_1
body_top_marking_2
```

Queste regioni servono a catturare meglio marking piccoli o molto vicini al bordo superiore del package.

### 5.8 `body_line_1`, `body_line_2`, `body_line_3`

Sono bande orizzontali interne al corpo.

Servono perché molti marking stanno nella zona centrale, ma Tesseract può sbagliare se la ROI contiene troppe cose insieme.

Le bande interne provano a isolare righe come:

```text
IC1
NE555
TDA1553
LM1875
```

Anche queste vengono lette come riga singola, quindi sono adatte ai part number.

---

## 6. Modalità OCR: `fast` e `deep`

Il sistema attuale non fa subito il massimo lavoro possibile. Usa due livelli.

### 6.1 Modalità `fast`

La modalità `fast` è la prima lettura.

Caratteristiche:

- usa le ROI principali;
- usa Tesseract;
- usa varianti raw;
- non usa EasyOCR;
- è più veloce;
- serve a gestire i casi facili.

Esempi che spesso funzionano già in `fast`:

```text
TDA7000
TDA1553
LM1875
TDA1516BQ
TC4423
L298
```

### 6.2 Quando si passa a `deep`

Il codice passa alla modalità `deep` se:

- non ci sono candidati validi;
- il candidato migliore è debole;
- il fallback EasyOCR sarebbe utile;
- il candidato migliore arriva da `above_body`;
- il candidato migliore arriva da `expanded_bbox` con confidenza bassa.

Questa logica evita di pagare sempre il costo della modalità profonda, ma consente di recuperare i casi difficili.

### 6.3 Modalità `deep`

La modalità `deep` aggiunge:

- ROI superiori più strette;
- ROI dinamica `body_top_text_line`;
- bande extra nella parte alta;
- varianti immagine per alcune ROI;
- EasyOCR opzionale come fallback.

È pensata per casi come:

```text
TPS63061
ISL85410 / ISL854102
NE555 letto con confidenza bassa
ADC0804 letto da EasyOCR
AT89S51 letto da EasyOCR
```

---

## 7. Preprocessing e varianti immagine

### 7.1 Preprocessing base per Tesseract

Il preprocessing base fa:

```text
1. conversione in grayscale
2. resize x3
3. blur leggero
4. soglia Otsu
5. eventuale inversione testo nero / sfondo bianco
```

Questa scelta è adatta agli schemi elettrici, perché spesso sono immagini ad alto contrasto.

Il resize x3 è molto importante perché i testi sono piccoli.

### 7.2 Varianti in modalità `deep`

In modalità `deep`, per le regioni superiori del package, il codice crea varianti visive:

```text
raw
clahe
adaptive
upscaled_clahe
```

Queste varianti sono utili quando il part number è piccolo, poco contrastato o su sfondo colorato.

Non vengono applicate ovunque per non rallentare troppo la pipeline.

### 7.3 Gestione delle coordinate dopo le varianti

Quando una variante viene upscalata, il bbox OCR viene riportato alla scala originale della ROI.

Questo è importante perché nel JSON vogliamo salvare `ic_marking_bbox` in coordinate immagine originali, non in coordinate della ROI ingrandita.

---

## 8. Motori OCR usati

### 8.1 Tesseract

Tesseract è il motore principale.

Viene usato tramite `pytesseract.image_to_data`, così otteniamo:

- testo;
- confidenza;
- bbox locale;
- numero di parole lette;
- debug del motore.

Il codice usa una whitelist:

```text
ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_/-+.
```

Questo riduce caratteri inutili e rende la lettura più coerente con i part number.

Il PSM può cambiare in base alla regione:

- `psm 6` per blocchi più generici;
- `psm 7` per righe singole come `body_line_*` o `body_top_marking`.

È supportata anche la variabile ambiente:

```text
TESSERACT_CMD
```

utile su Windows quando `tesseract.exe` non è nel PATH.

### 8.2 EasyOCR come fallback

EasyOCR non è il motore principale. È un fallback opzionale.

Viene usato solo se abilitato nel YAML e se il candidato Tesseract è assente o debole.

Il codice usa un lazy singleton:

```text
_EASYOCR_READER
```

Questo significa che il reader EasyOCR viene caricato una sola volta e riutilizzato, evitando un costo enorme per ogni crop.

EasyOCR è limitato a poche regioni importanti:

- regioni interne al package;
- al massimo alcune ROI selezionate;
- varianti raw o CLAHE, non tutte le varianti.

Questo evita di rallentare troppo la pipeline.

È supportata anche la variabile ambiente:

```text
EASYOCR_MODEL_DIR
```

per controllare dove vengono salvati/caricati i modelli EasyOCR.

---

## 9. Normalizzazione del testo OCR

L'OCR può produrre stringhe quasi corrette ma sporche.

La normalizzazione attuale fa interventi prudenti:

```text
- strip degli spazi iniziali/finali
- maiuscolo
- rimozione spazi interni
- rimozione newline
- pulizia di caratteri ai bordi
- correzione dello slash tra cifre come possibile 7
- correzione LM31/T -> LM317T
- correzione di doppi 7 davanti a suffisso finale
```

Esempi:

```text
LM31/T  -> LM317T
LM18/5  -> LM1875
LM3177T -> LM317T, in casi compatibili
```

La normalizzazione non prova ancora a correggere casi più difficili come:

```text
TDA7ON -> TDA7000
```

Questa correzione richiede un livello successivo, probabilmente basato su fuzzy matching o ricerca datasheet.

È importante non rendere la normalizzazione troppo aggressiva, perché un part number inventato sarebbe peggio di un OCR incerto.

---

## 10. Filtri sui candidati OCR

Dopo l'OCR, ogni parola viene trasformata in candidato solo se supera una serie di filtri.

### 10.1 Deve contenere lettere e numeri

Un marking IC utile per datasheet di solito contiene sia lettere sia numeri:

```text
NE555
LM317T
TDA7000
ADC0804
AT89S51
TPS63061
ISL85410
L298
```

Parole senza numeri come queste vengono scartate come marking:

```text
COM
OUT
IN
ADJ
VIN
GND
PHASE
BOOT
SYNC
```

Queste parole saranno utili nella fase OCR dei pin, ma non devono diventare `ic_marking`.

### 10.2 Designator da scartare

Vengono scartati designator schematici come:

```text
IC1
U1
R1
C2
L1
D3
Q1
K1
S1
J1
TP1
```

C'è però una protezione per non scartare marking plausibili di famiglia nota.

Per esempio `L298` inizia con `L`, ma non va trattato come un semplice induttore `L1`, perché ha una parte numerica forte e somiglia a un IC reale.

### 10.3 Valori elettrici da scartare

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

### 10.4 Transistor comuni da scartare

Vengono scartati candidati come:

```text
2N2222
BC547
BC107
```

Questi sono componenti validi, ma non sono marking di circuiti integrati nel contesto della classe `Integrated_Circuit`.

### 10.5 Watermark e testi di sito

Vengono scartati testi come:

```text
WWW
CIRCUITSTODAY
WWW.CIRCUITSTODAY
```

Questo evita che il watermark dello schema entri nel JSON come nome del componente.

---

## 11. Scoring dei candidati

Ogni candidato OCR riceve uno score.

Lo score non è solo la confidence del motore OCR.

Tiene conto di:

```text
confidence OCR
+ presenza di lettere e numeri
+ lunghezza realistica
+ prefisso IC noto
+ numero di cifre
+ lunghezza del gruppo numerico più lungo
+ marking strutturato tipo CODICE/CODICE
+ regione OCR da cui proviene
```

### 11.1 Prefissi IC noti

Il codice usa una lista di prefissi frequenti:

```text
NE, LM, TDA, TPS, ISL, ADC, AT, HT, TC, CD, L, TL, UA, MC, MAX
```

Questo aiuta a preferire stringhe come:

```text
NE555
LM317T
TDA1553
TPS63061
ADC0804
AT89S51
```

### 11.2 Bonus per cifre

I part number reali spesso hanno una parte numerica forte.

Per questo lo score aumenta se:

- ci sono almeno tre cifre;
- ci sono almeno quattro cifre;
- esiste una sequenza numerica lunga almeno tre caratteri.

Questo aiuta a preferire `TDA7000`, `ADC0804`, `AT89S51` rispetto a letture meno plausibili.

### 11.3 Bonus per marking strutturati

Il codice riconosce anche forme del tipo:

```text
ISL85410/ISL854102
```

Queste possono rappresentare varianti compatibili indicate nello schema. Non vengono corrette, ma ricevono un bonus perché sono plausibili come informazione di datasheet.

### 11.4 Peso della regione

Le regioni interne al package ricevono più fiducia.

Esempio di priorità concettuale:

```text
body_top_marking_tight
body_top_text_line
body_top_marking
body_line_1/2/3
body_inner
expanded_bbox
above_body
below/left/right
```

In generale:

- una lettura dentro il corpo è più affidabile;
- una lettura in `expanded_bbox` può essere buona, ma va trattata con cautela;
- regioni laterali o inferiori sono meno affidabili per il marking.

---

## 12. Consenso tra candidati

Dopo lo scoring individuale, il codice calcola un consenso.

L'idea è:

```text
Se lo stesso testo viene letto da più regioni o da più motori OCR,
allora è più affidabile di una lettura isolata.
```

Per esempio:

```text
body_inner       -> NE555
body_line_2      -> NE555
expanded_bbox    -> NE555
```

In questo caso `NE555` riceve un bonus di consenso.

Il candidato finale viene scelto considerando:

```text
consensus_score
score individuale
priorità della regione
confidence OCR
```

Questo è importante perché un OCR può produrre una singola lettura ad alta confidence ma sbagliata. Il consenso rende il sistema più stabile.

---

## 13. Separazione di suffissi che possono essere pin label

Il codice ha una normalizzazione specifica per casi in cui il part number viene fuso con una label di pin.

Esempio:

```text
ADC0804D
```

Può succedere che la `D` finale non faccia parte del marking, ma venga da una label vicina come `D0`, `D1`, `D6`.

La funzione di separazione è prudente:

- cerca un pattern compatibile con un part number;
- controlla che ci sia una parte numerica forte;
- verifica se nelle raw words dello stesso IC esiste evidenza di pin label della stessa famiglia;
- solo allora rimuove il suffisso.

Il JSON conserva anche un debug della normalizzazione:

```json
"marking_normalization": {
  "raw_text": "ADC0804D",
  "normalized_part_number": "ADC0804",
  "changed": true,
  "reason": "possible_trailing_pin_label_suffix",
  "removed_suffix": "D"
}
```

Questo è importante perché non vogliamo perdere l'evidenza originale.

---

## 14. Rilevamento dei display a 7 segmenti

Un problema reale emerso nei test è che alcuni display a 7 segmenti vengono rilevati da YOLO come `Integrated_Circuit`.

Geometricamente sono rettangoli multi-terminale, quindi possono somigliare a IC. Semanticamente però non devono essere trattati come IC da datasheet.

Il modulo attuale prova a riconoscerli quando non ci sono candidati IC validi.

La decisione usa due tipi di evidenza.

### 14.1 Evidenza OCR

Cerca parole tipiche dei display:

```text
a
b
c
d
e
f
g
com
D1
D2
```

In particolare:

- le lettere `A`-`G` suggeriscono segment labels;
- `COM` suggerisce common pin;
- `D1`, `D2` possono essere reference designator dei display.

### 14.2 Evidenza grafica

Il codice guarda dentro il `body_bbox` e cerca componenti scure grandi e compatte, più simili a segmenti LED/LCD che a testo sottile.

Misura:

- dark ratio;
- area del componente scuro più grande;
- numero di componenti scure grandi;
- presenza di componenti allungate.

### 14.3 Output per display

Se il componente sembra un display, vengono salvati campi come:

```json
"component_subtype": "seven_segment_display",
"display_type": "seven_segment",
"reference_designator_ocr": "D1"
```

In debug l'immagine `_ic_ocr.jpg` disegna questi componenti in viola con label:

```text
11.3: DISPLAY_7SEG
```

Questa parte è molto utile perché evita falsi positivi come `COM` come nome IC.

---

## 15. Output JSON attuale

Per ogni componente `Integrated_Circuit`, dopo l'OCR del marking, possono comparire questi campi:

```json
{
  "instance_id": "11.1",
  "class_name": "Integrated_Circuit",
  "body_bbox": [x1, y1, x2, y2],

  "ic_marking": "TDA7000",
  "ic_marking_confidence": 0.75,
  "ic_marking_bbox": [x1, y1, x2, y2],
  "ic_marking_source_region": "body_inner",
  "ic_marking_engine": "tesseract",
  "ic_marking_variant": "raw",
  "ic_ocr_mode": "fast",
  "ic_ocr_engines_used": ["tesseract"],

  "ic_ocr_debug": {
    "enabled": true,
    "ocr_mode": "fast",
    "body_bbox": [x1, y1, x2, y2],
    "selected": {...},
    "marking_normalization": {...},
    "candidate_count": 4,
    "candidates": [...],
    "regions": [...]
  }
}
```

Se non viene trovato nessun marking valido:

```json
{
  "ic_marking": null,
  "ic_marking_confidence": 0.0,
  "ic_marking_bbox": null,
  "ic_marking_source_region": null,
  "ic_marking_engine": null,
  "ic_marking_variant": null,
  "ic_ocr_mode": "deep"
}
```

Se il componente viene riconosciuto come display:

```json
{
  "component_subtype": "seven_segment_display",
  "display_type": "seven_segment",
  "reference_designator_ocr": "D1",
  "ic_marking": null
}
```

---

## 16. Debug immagini OCR IC

È stata aggiunta una debug image dedicata ai nomi OCR degli IC.

Queste immagini non vengono più mischiate con le immagini terminali.

La struttura consigliata è:

```text
03_estimate_terminals/
  debug_images/
    ic1_terminals.jpg
    ic2_terminals.jpg

    ic_ocr/
      ic1_ic_ocr.jpg
      ic2_ic_ocr.jpg
```

La debug image OCR IC è volutamente semplice.

Mostra:

- bbox YOLO in grigio;
- `body_bbox` in cyan;
- bbox del testo selezionato nel colore dello status;
- label compatta con nome, confidenza, sorgente, motore e modalità;
- display a 7 segmenti in viola.

Esempi di label:

```text
11.1: TDA7000 (0.75) [inner/tess/fast]
11.1: TPS63061 (0.36) [top/tess/deep] ?
11.3: DISPLAY_7SEG
11.1: OCR NONE (cand=0)
```

I colori sono:

```text
verde    = lettura buona
small yellow/orange = lettura media o debole
rosso    = assente o molto bassa
viola    = display 7 segmenti
cyan     = body_bbox
grigio   = bbox YOLO
```

Questa immagine serve a rispondere rapidamente a quattro domande:

```text
1. Il body_bbox è giusto?
2. Il nome OCR è corretto?
3. Il testo selezionato è davvero dentro/vicino all'IC?
4. Il risultato è sicuro o incerto?
```

Tutti i dettagli lunghi restano nel JSON, non nella debug image.

---

## 17. Relazione con script 04 e script 05

### 17.1 Script 04

Lo script 04 si occupa della skeletonizzazione dei fili.

Non deve fare OCR.

Però in futuro potrà usare `body_bbox` degli IC per mascherare meglio il corpo dell'integrato, invece di usare il bbox YOLO completo.

Questo eviterà di cancellare fili o testi vicini.

### 17.2 Script 05

Lo script 05 costruisce il grafo elettrico.

Non deve fare OCR.

Dovrà usare:

- terminali geometrici;
- nodi elettrici;
- eventuali informazioni semantiche già presenti nel JSON.

Quando avremo anche i pin OCR, lo script 05 potrà portarsi dietro campi come `pin_number` e `pin_label_text`, ma non dovrà crearli.

---

## 18. Perché non cambiare `terminal_id`

Anche quando leggeremo i pin, non conviene cambiare il `terminal_id` principale.

Oggi un terminale IC può chiamarsi:

```text
11.1:left_1
11.1:left_2
11.1:right_1
11.1:bottom_1
```

Questi nomi sono geometrici e stabili.

Quando aggiungeremo OCR pin, conviene fare così:

```json
{
  "terminal_id": "11.1:left_2",
  "relative_position": "left",
  "x": 420.0,
  "y": 431.0,
  "pin_number": "2",
  "pin_label_text": "VIN"
}
```

Così:

- il grafo resta stabile;
- l'OCR può sbagliare senza rompere la topologia;
- l'agente AI può usare sia il terminale geometrico sia la semantica OCR.

Solo eventualmente potremo aggiungere un alias:

```json
"semantic_terminal_id": "11.1:pin_2"
```

ma non come ID principale.

---

## 19. Esempi osservati nei test

Dai test sulle immagini attuali, il sistema legge bene molti casi:

```text
TDA7000
TDA1553
LM1875
LM317T
TDA1516BQ
HT8950A
HT82V733
NE555
TC4423
L298
```

Alcuni casi vengono letti correttamente ma con confidenza bassa o media:

```text
TPS63061
ISL85410/ISL854102
ADC0804
AT89S51
```

Questi sono esattamente i casi in cui la debug image con colori e `?` è utile: il nome può essere corretto, ma il sistema deve dichiarare che la lettura è incerta.

---

## 20. Cose ancora da migliorare

### 20.1 Aggiungere uno status esplicito nel JSON

Attualmente il debug image usa la confidenza per colorare la label, ma nel JSON sarebbe utile avere anche un campo esplicito:

```json
"ic_marking_status": "accepted"
```

oppure:

```json
"ic_marking_status": "uncertain"
```

oppure:

```json
"ic_marking_status": "none"
```

Questo aiuterebbe l'agente AI finale a capire quanto fidarsi del marking.

### 20.2 Fuzzy matching o lookup datasheet

Alcuni errori OCR non sono risolvibili bene con regole locali.

Esempio:

```text
TDA7ON -> TDA7000
```

Per questi casi servirà una fase successiva:

```text
candidato OCR -> ricerca datasheet / fuzzy match -> part number probabile
```

Questa fase non dovrebbe stare nel modulo OCR base, ma in un modulo successivo o in un agente AI.

### 20.3 OCR dei pin

Il prossimo vero passo è leggere, per ogni terminale geometrico IC:

- numero pin;
- label pin;
- eventuale `NC` o `N/C`;
- bbox e confidenza OCR.

La logica sarà orientata per lato:

```text
left side:
  fuori corpo  -> numero pin
  dentro corpo -> label pin

right side:
  fuori corpo  -> numero pin
  dentro corpo -> label pin

top side:
  sopra / vicino bordo -> numero o label

bottom side:
  sotto / vicino bordo -> numero o label
```

I pin non collegati non devono entrare nel grafo elettrico come terminali connessi. Potranno essere salvati in una lista separata.

### 20.4 Migliorare il body_bbox quando YOLO include troppo

Alcuni casi mostrano bbox YOLO molto largo o body_bbox non perfetto.

La stima dei terminali e l'OCR dipendono molto dal body_bbox. Quindi migliorare il raffinamento geometrico del corpo IC migliorerà anche l'OCR.

### 20.5 Valutazione quantitativa

Per ora stiamo valutando visivamente.

Più avanti conviene creare una piccola tabella ground truth:

```text
immagine | instance_id | expected_marking | predicted_marking | confidence | ok/not ok
```

Questo permetterà di misurare:

- accuracy marking;
- falsi positivi;
- falsi null;
- casi deboli ma corretti;
- casi EasyOCR utili.

---

## 21. Strategia complessiva aggiornata

La strategia completa per gli IC, aggiornata allo stato attuale, è:

```text
1. Script 01
   - rileva Integrated_Circuit con YOLO.

2. Script 02
   - assegna instance_id stabile.

3. Script 03
   - stima terminali geometrici;
   - recupera o salva body_bbox;
   - chiama OCR marking IC;
   - salva ic_marking e debug OCR;
   - crea immagini debug terminali;
   - crea immagini debug OCR IC in debug_images/ic_ocr/.

4. Script 04
   - estrae/skeletonizza fili;
   - in futuro può usare body_bbox per mascherare meglio gli IC.

5. Script 05
   - costruisce il grafo;
   - mantiene la topologia indipendente dagli errori OCR.

6. Fase successiva
   - OCR pin_number e pin_label_text;
   - ricerca datasheet;
   - associazione pin -> funzione;
   - agente AI per interpretazione del circuito.
```

---

## 22. Conclusione

Lo stato attuale è buono perché la pipeline mantiene separati tre livelli:

```text
geometria  -> dove sono corpo e terminali
OCR        -> cosa c'è scritto sull'IC
semantica  -> cosa significa quel part number e cosa fanno i pin
```

Questa separazione è la scelta giusta.

Il modulo OCR è diventato più robusto rispetto alla prima versione perché ora include:

- più ROI;
- modalità `fast` e `deep`;
- Tesseract con PSM e whitelist;
- varianti immagine;
- EasyOCR opzionale;
- scoring severo;
- consenso tra letture;
- rilevamento display a 7 segmenti;
- debug JSON dettagliato;
- debug image OCR compatta e leggibile.

Il prossimo passo consigliato è:

```text
1. consolidare ic_marking_status nel JSON;
2. iniziare OCR dei pin per ogni terminale geometrico;
3. mantenere terminal_id stabile;
4. usare datasheet/AI solo dopo avere marking e pin OCR.
```
