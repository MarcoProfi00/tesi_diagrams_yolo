# Strategia OCR per circuiti integrati nella pipeline di analisi schemi elettrici

## 1. Obiettivo

L’obiettivo di questa fase è arricchire i componenti di tipo `Integrated_Circuit` con informazioni testuali lette direttamente dallo schema elettrico.

In particolare vogliamo ottenere due livelli di informazione:

1. **Nome o marking del circuito integrato**, ad esempio:
   - `NE555`
   - `LM317T`
   - `LM1875`
   - `TDA7000`
   - `TDA1553`
   - `ADC0804`
   - `AT89S51`
   - `TPS63061`
   - `ISL85410`
   - `HT8950A`
   - `L298`

2. **Informazioni associate ai pin**, ad esempio:
   - numero pin: `1`, `2`, `3`, `10`, `11`, ecc.;
   - label pin: `VIN`, `VOUT`, `GND`, `FB`, `EN`, `PG`, `OUT`, `ADJ`, ecc.

In questa prima fase si lavora solo sul primo obiettivo: **riconoscere il marking dell’integrato**. La lettura dei pin verrà aggiunta successivamente.

La motivazione è semplice: prima bisogna stabilizzare l’identificazione del componente, poi si può passare alla semantica dei suoi terminali.

---

## 2. Principio fondamentale: geometria prima, OCR dopo

La pipeline non deve usare l’OCR per decidere se un terminale esiste.

Il terminale di un circuito integrato nasce dalla geometria, cioè dal fatto che un filo entra o esce dal corpo del componente.

La logica corretta è quindi:

text
1. YOLO rileva il circuito integrato.
2. Lo script 02 assegna un instance_id.
3. Lo script 03 raffina il body_bbox e trova i terminali dai contatti filo-corpo.
4. Solo dopo, l’OCR legge il testo vicino al componente.
5. Il testo OCR arricchisce il JSON, ma non crea terminali da solo.

Questa scelta è importante perché negli schemi ci sono molti testi vicini agli IC che non rappresentano terminali reali. Alcuni esempi:
- IC1
- IC2
- R1
- C3
- D1
- 100nF
- 10uF
- +12V
- GND
- Audio out
- No connection
- www.circuitstoday.com

Se partissimo dall’OCR per creare terminali, rischieremmo molti falsi positivi.

La strategia già adottata è quindi corretta:
- prima trovo i terminali dai fili,
- poi associo a ciascun terminale il testo più vicino.

Per ora si è implementata solo la parte di OCR del marking, ma la filosofia rimane la stessa anche per i pin.

## 3. Separazione tra bbox YOLO, body_bbox e search_bbox

Per gli IC è fondamentale distinguere tre concetti:
- bbox_yolo    = bbox grezzo prodotto dal rilevatore YOLO
- body_bbox    = rettangolo reale del corpo dell’integrato
- search_bbox  = area espansa usata per cercare testo vicino

Il bbox YOLO può includere più cose:

- corpo dell’integrato;
- fili;
- numeri dei pin;
- label dei pin;
- nome del componente;
- testo vicino;
- altri simboli molto prossimi.

Per questo non conviene usare direttamente il bbox YOLO come area OCR principale.

Il **body_bbox** è invece il rettangolo reale del simbolo IC. È molto più utile perché:

- delimita il corpo vero dell’integrato;
- permette di sapere dove sono i lati sinistro, destro, alto e basso;
- consente di costruire ROI OCR più intelligenti;
- può essere usato anche nello script 04 per mascherare il corpo senza cancellare troppi fili.

Nel modulo OCR attuale la funzione recupera il body_bbox con una logica a priorità:
1. component["body_bbox"]
2. component["connection_side_scores"]["body_bbox"]
3. terminal_point_debug["body_bbox"]
4. fallback: bbox YOLO

4. Perché il marking IC non va cercato in una sola ROI

Il nome dell’integrato può trovarsi in posizioni diverse.

Esempi:
NE555      → spesso dentro il corpo
TDA7000    → dentro il corpo
LM317T     → dentro il corpo, ma vicino a IC1
TPS63061   → sopra il corpo
ISL85410   → sopra il corpo
ADC0804    → dentro il corpo
AT89S51    → dentro o vicino al corpo

Per questo una sola ROI non basta.

La strategia attuale usa più regioni:
- body_inner
- above_body
- below_body
- left_of_body
- right_of_body
- expanded_bbox
- body_line_1
- body_line_2
- body_line_3

## 5. ROI principali per il marking
### 5.1 body_inner

La ROI body_inner cerca il testo dentro il corpo dell’integrato.

Non conviene usare tutto il body_bbox, perché ai bordi del rettangolo spesso ci sono:

- numeri dei pin;
- label dei pin;
- linee del bordo;
- fili che entrano nel corpo;
- scritte come IC1.

Per questo la ROI viene ristretta verso il centro.
Esempio:
```text
+----------------------+
| 1                 8  |
|                      |
|      IC1             |
|      NE555           |
|                      |
| 2                 7  |
+----------------------+
```

### 5.2 above_body

La ROI above_body serve per i casi in cui il part number è sopra il corpo dell’integrato.
Esempio:
```text
      TPS63061
+----------------+
| L1         L2  |
| VIN       VOUT |
| EN         FB  |
+----------------+
```
In questo caso, se cercassimo solo dentro il body, potremmo leggere solo VIN, VOUT, EN, FB, perdendo TPS63061.

### 5.3 expanded_bbox

La ROI expanded_bbox è un fallback più ampio.

È utile perché a volte **Tesseract** legge meglio se vede un po’ più di contesto, ma è anche pericolosa perché può includere:

- valori di componenti vicini;
- watermark;
- fili;
- testi di rete;
- nomi di altri componenti.

Per questo è corretto filtrare i candidati provenienti da expanded_bbox: un testo letto lì deve comunque avere il centro vicino o dentro il body_bbox.

### 5.4 body_line_1, body_line_2, body_line_3

Questa è una buona aggiunta.

Tesseract spesso sbaglia se la ROI contiene insieme:

- bordo del rettangolo;
- numeri dei pin;
- linee verticali;
- fili;
- marking centrale.

Le ROI body_line_* provano a isolare bande orizzontali interne al body.

Esempio:
```text
      TPS63061
+----------------------+
|                      |
|      IC1             |  body_line_1
|      TDA1553         |  body_line_2
|                      |
+----------------------+
```
Queste ROI possono essere lette con **psm 7**, cioè come singola riga. Questo è utile perché un part number è spesso una riga breve, non un blocco di testo complesso.

## 6. Preprocessing OCR

Il preprocessing attuale è volutamente semplice:
1. conversione in grayscale
2. resize x3
3. blur leggero
4. soglia Otsu
5. eventuale inversione per avere testo nero su sfondo bianco

Questa è una scelta sensata per iniziare.

Gli schemi elettrici sono generalmente disegni ad alto contrasto. Quindi un preprocessing troppo complicato potrebbe introdurre più problemi che benefici.

Il resize x3 è importante perché molte scritte sono piccole. Ingrandire la ROI prima dell’OCR aiuta Tesseract a distinguere meglio caratteri come:
- 5, S
- 0, O
- 1, I, l
- 7, /
- 8, B

Il problema principale resta che alcuni marking sono molto piccoli o degradati. Per esempio TDA7000 può essere letto come qualcosa tipo TDA7ON, e LM317T può essere letto come LM31/T.

Per questo è utile avere una fase separata di normalizzazione.

## 7. Perché usare Tesseract

Tesseract è adatto come primo motore OCR perché:

- è leggero;
- è configurabile;
- consente whitelist di caratteri;
- consente di scegliere il PSM;
- è facile da debuggare;
- restituisce testo, confidenza e bounding box.

Nel nostro caso non stiamo leggendo testo naturale generico, ma stringhe tecniche corte:
- NE555
- LM317T
- TDA7000
- VIN
- GND
- FB
- 12
- 10

Quindi Tesseract è una buona scelta iniziale.

Per esempio possiamo usare configurazioni diverse:
- psm 6 → blocco di testo
- psm 7 → singola riga
- psm 8 → singola parola
- psm 10 → singolo carattere
Nel modulo attuale il PSM è già parametrizzato per Tesseract. Questo è positivo perché permette di provare strategie diverse in base alla ROI.

## 8. Perché aggiungere EasyOCR come fallback

EasyOCR è utile come secondo motore, non necessariamente come motore principale.

**Tesseract** e **EasyOCR** sbagliano in modi diversi. Questo è utile perché se entrambi leggono lo stesso testo, il risultato è più affidabile.

La logica corretta è: 
- uso Tesseract come motore principale;
- se non trovo candidati o il candidato è debole, provo EasyOCR come fallback.

Questo evita di rallentare troppo la pipeline.

Nel file attuale hai già un lazy singleton per EasyOCR. Questa è una scelta corretta, perché caricare il reader EasyOCR per ogni crop sarebbe molto lento. Invece viene creato una volta e riutilizzato.

EasyOCR è particolarmente utile nei casi in cui:

- il testo è sfocato;
- il font è strano;
- il testo è piccolo;
- Tesseract spezza male la parola;
- la ROI contiene rumore grafico.

Però ha anche svantaggi:

- dipendenze più pesanti;
- possibile uso di PyTorch;
- tempi maggiori;
- più variabilità;
- eventuali problemi di installazione/modelli.

Quindi la strategia migliore è usarlo come fallback configurabile.

## 9. Normalizzazione del testo OCR

L’OCR può leggere stringhe quasi corrette ma non perfette.

Esempi:
- LM31/T  → LM317T
- LM18/5  → LM1875
- TDA7ON  → TDA7000

La normalizzazione attuale fa correzioni prudenti, ad esempio sostituisce uno slash tra cifre con 7.

Questa scelta ha senso perché Tesseract può leggere il tratto del 7 come slash.

Però bisogna fare attenzione a non correggere troppo.

Una correzione troppo aggressiva potrebbe trasformare un codice reale in uno sbagliato. Per questo è giusto che il modulo:
- conservi il raw_text;
- salvi il testo normalizzato;
- salvi il debug della normalizzazione;
- non cancelli l’evidenza originale.

In futuro, le correzioni più aggressive dovrebbero avvenire in una fase diversa, magari con un agente AI o un dizionario di part number validi.

## 10. Scoring dei candidati

Dopo l’OCR non bisogna scegliere automaticamente il testo con confidence più alta.

La confidence dell’OCR da sola non basta.

Per esempio una parola come COM può avere confidence altissima, ma non è il nome dell’integrato. È una label del display o di un pin.

Per questo il modulo assegna uno score combinando più fattori:
score OCR
```text
+ bonus lettere e numeri
+ bonus lunghezza realistica
+ bonus prefissi IC comuni
+ bonus quantità di cifre
+ bonus longest digit run
+ bonus/penalità in base alla regione
- reject per parole vietate
- reject per designator
- reject per valori elettrici
```

Questa logica è molto più robusta.

Un marking IC reale di solito ha sia lettere sia numeri:
- NE555
- TDA7000
- LM317T
- ADC0804
- AT89S51
- TPS63061
- ISL85410
- L298

Al contrario, testi come questi non devono diventare marking:
- COM
- OUT
- IN
- ADJ
- VIN
- VOUT
- GND
- FB
- PG
- R1
- C2
- 10uF
- 100nF
- 12V

Quindi la regola “deve contenere almeno una lettera e almeno un numero” è utile.

Non è perfetta in assoluto, perché esistono integrati con nomi solo alfabetici, ma per il dataset attuale è una buona semplificazione.

## 11. Filtri anti-falso positivo

Il modulo usa diversi filtri.

### 11.1 Designator dei componenti

Questi non sono marking IC:
- IC1
- U1
- R1
- C2
- L1
- D3
- Q1
- K1
- S1
- TP1

Vanno scartati.

### 11.2 Net label e pin label

Questi possono essere utili per i pin, ma non per il nome IC:
- VIN
- VOUT
- VCC
- VDD
- VSS
- GND
- EN
- FB
- PG
- COMP
- SYNC
- BOOT
- PHASE
- OUT
- IN
- ADJ
- COM
Vanno scartati dal marking, ma non dimenticati per sempre: saranno utili nella fase OCR dei pin.

### 11.3 Valori elettrici

Questi non sono marking IC:
- 10uF
- 100nF
- 22pF
- 4.7K
- 12V
- 500mW
- 22uH

Vanno scartati.

### 11.4 Transistor comuni

Questi sono componenti, ma non sono circuiti integrati:
- 2N2222
- BC547
- BC107

Se EasyOCR o Tesseract li leggono dentro un expanded_bbox, non devono diventare marking IC.


## 12. Consensus tra regioni ed engine

Una delle aggiunte migliori è il consenso.

L’idea è:
se lo stesso testo viene letto da più regioni o più motori OCR,
allora è più affidabile.

Esempio:
- body_inner     → NE555
- body_line_2    → NE555
- expanded_bbox  → NE555

Questo è più forte di una singola lettura isolata.

Il consenso è utile anche quando i punteggi individuali sono vicini.

Esempio:
- candidate A: NE555, score 1.30, letto da 3 ROI
- candidate B: R555,  score 1.35, letto da 1 ROI
Senza consenso vincerebbe forse R555. Con il consenso può vincere NE555.

Questa è una scelta corretta perché in immagini rumorose è meglio premiare la stabilità della lettura, non solo il singolo score.

## 13. Gestione dei display a 7 segmenti

Un problema emerso nei test è che alcuni display a 7 segmenti vengono rilevati come Integrated_Circuit.

Questi componenti sono rettangoli multipin, quindi geometricamente assomigliano a IC. Però semanticamente non sono IC da cercare nel datasheet come NE555 o LM317T.

Il testo interno o vicino ai display può essere:
- a
- b
- c
- d
- e
- f
- g
- com
- D1
- D2

Il modulo attuale prova a riconoscere questo caso usando:

- label OCR dei segmenti;
- presenza di COM;
- reference designator tipo D1, D2;
- evidenza grafica di segmenti scuri nel body.

Questa è una scelta molto buona perché evita di assegnare COM come marking dell’integrato.
Il risultato ideale è:

```text
{
  "class_name": "Integrated_Circuit",
  "component_subtype": "seven_segment_display",
  "display_type": "seven_segment",
  "ic_marking": null
}
```
In futuro sarebbe ancora meglio avere una classe YOLO dedicata: Seven_Segment_Display

## 14. Perché non modificare terminal_id

Per ora non bisogna cambiare terminal_id in base all’OCR.

Il terminal_id deve restare stabile e geometrico:
- 11.1:left_1
- 11.1:left_2
- 11.1:right_1
- 11.1:bottom_1

L’OCR deve aggiungere campi semantici, non sostituire l’identità topologica del terminale.

Quando leggeremo i pin, il terminale ideale sarà:
```text
{
  "terminal_id": "11.1:left_2",
  "name": "left_2",
  "relative_position": "left",
  "x": 420.0,
  "y": 431.0,

  "pin_number": "2",
  "pin_label_text": "VIN",
  "pin_ocr_confidence": 0.82
}
```
In questo modo:

- lo script 04 e 05 possono continuare a usare terminal_id stabili;
- l’OCR può sbagliare senza rompere il grafo;
- il debug rimane leggibile;
- l’agente AI finale può usare sia la topologia sia la semantica.

Solo in una fase successiva si potrà aggiungere un alias: "semantic_terminal_id": "11.1:pin_2"

## 15. Output JSON desiderato

Per un circuito integrato, il JSON dovrebbe contenere:
```text
{
  "instance_id": "11.1",
  "class_name": "Integrated_Circuit",
  "bbox": [ ... ],
  "body_bbox": [ ... ],

  "ic_marking": "NE555",
  "ic_marking_confidence": 0.91,
  "ic_marking_bbox": [ ... ],
  "ic_marking_source_region": "body_line_2",

  "ic_ocr_debug": {
    "enabled": true,
    "selected": {
      "text": "NE555",
      "engine": "tesseract",
      "source_region": "body_line_2",
      "score": 1.52,
      "consensus_score": 1.88
    },
    "candidate_count": 4,
    "candidates": [
      ...
    ],
    "regions": [
      ...
    ]
  },

  "terminals": [
    {
      "terminal_id": "11.1:left_1",
      "relative_position": "left",
      "x": 100.0,
      "y": 250.0
    }
  ]
}
```

Questo formato è buono perché conserva:

- risultato finale;
- confidenza;
- bbox del testo;
- regione sorgente;
- candidati alternativi;
- debug OCR.

Il debug è molto importante perché l’OCR sarà sempre imperfetto.