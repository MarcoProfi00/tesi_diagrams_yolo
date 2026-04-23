# Documentazione tecnica del passo `02_assign_instances`

## Scopo del modulo

Il passo `02_assign_instances` ha il compito di prendere l’output del passo `01_detect_components` e trasformarlo in una rappresentazione in cui ogni componente rilevato possiede un **identificatore di istanza stabile e leggibile**. Lo script non modifica la detection, non cambia i bounding box e non stima ancora i terminali: il suo obiettivo è **ordinare i componenti e assegnare a ciascuno un `instance_id` univoco all’interno della propria classe**.

In termini pratici, questo stadio risponde a una domanda molto semplice ma fondamentale per tutta la pipeline successiva:

> dato un insieme di componenti rilevati nell’immagine, come assegno a ciascuno un nome di istanza coerente, riproducibile e facile da usare nei passi successivi?

Il risultato di questo passo viene poi usato direttamente dallo script 03, che si appoggia agli `instance_id` per costruire identificatori terminali del tipo `instance_id:nome_terminale`.

---

## Ruolo del passo 02 nella pipeline

Il passo 02 si colloca fra:

- **01 — detect components**: produce i componenti rilevati con bbox, classe e confidenza;
- **03 — estimate terminals**: usa i componenti già istanziati per stimare orientazione, terminali e semantica.

Quindi il passo 02 è uno stadio di **normalizzazione e indicizzazione delle detection**. Il suo compito è rendere il dataset in uscita dal detector più ordinato e utilizzabile dai moduli successivi.

Più precisamente, per ogni file JSON in input lo script:

1. legge l’elenco dei componenti rilevati;
2. li raggruppa per `class_id`;
3. ordina gli elementi di ogni gruppo secondo una convenzione geometrica scelta;
4. assegna gli identificatori di istanza nel formato `class_id.indice`;
5. ricompone la lista globale dei componenti;
6. salva il JSON aggiornato;
7. opzionalmente genera un’immagine di debug con bbox e `instance_id` sovrapposti. fileciteturn27file0

---

## Perimetro di questo documento

Questo documento descrive il file:

- `02_assign_instances.py`

Si tratta di uno script relativamente compatto, ma importante perché fissa le convenzioni di naming delle istanze che poi vengono propagate in tutta la pipeline.

---

# 1. Filosofia generale dello script 02

## Perché serve assegnare le istanze

Il detector del passo 01 restituisce componenti come entità separate, ma senza una numerazione strutturata di istanza. Per esempio, può dire che nell’immagine ci sono tre resistori e due condensatori, ma non ha ancora deciso quale sia:

- `22.1`
- `22.2`
- `22.3`

oppure:

- `4.1`
- `4.2`

Lo script 02 introduce questa convenzione.

## Obiettivo principale

L’obiettivo non è trovare un “ordine elettrico” del circuito, ma definire un **ordine geometrico coerente e ripetibile** basato sulla posizione dei componenti nell’immagine.

Questa scelta ha diversi vantaggi:

- è semplice da implementare;
- è deterministica;
- è facile da capire in fase di debug;
- è sufficiente per collegare in modo robusto componenti, terminali e annotazioni nei passi successivi.

## Principio di ordinamento

Ogni istanza viene numerata **all’interno della propria classe**.

Questo significa che:

- tutti i resistori vengono ordinati fra loro;
- tutti i condensatori vengono ordinati fra loro;
- tutti i transistor vengono ordinati fra loro;
- e così via.

La numerazione quindi non è globale, ma **relativa alla classe**. Il formato finale è:

```text
<class_id>.<indice_progressivo>
```

per esempio:

```text
22.1
22.2
22.3
```

oppure:

```text
18.1
18.2
```

---

# 2. Struttura del file `02_assign_instances.py`

Il file è organizzato in quattro blocchi principali:

1. **configurazione di percorso e parametri generali**;
2. **funzioni di utilità per centro e ordinamento**;
3. **funzioni operative per assegnazione istanze e debug image**;
4. **funzione `main()`**, che esegue il passo su tutti i JSON della cartella di input. fileciteturn27file0

---

# 3. Configurazione iniziale

## Variabili di percorso

Lo script definisce innanzitutto i percorsi principali:

- `PROJECT_ROOT`: radice del progetto;
- `PIPELINE_DATASET`: nome del dataset di pipeline, preso da variabile d’ambiente oppure da un valore di default;
- `INPUT_DIR`: cartella `01_detect_components`;
- `OUTPUT_DIR`: cartella `02_assign_instances`;
- `DEBUG_IMAGES_DIR`: cartella in cui salvare le immagini di debug. fileciteturn27file0

### Significato pratico
Questa struttura riflette la convenzione generale della pipeline:

- ogni passo legge dall’output del passo precedente;
- ogni passo scrive in una propria cartella dedicata;
- le immagini di debug vengono separate dai JSON.

## Parametro `SORT_ORDER`

Lo script prevede un parametro configurabile:

```python
SORT_ORDER = "xy"
```

con due modalità possibili:

- `"yx"` → ordinamento dall’alto verso il basso, poi da sinistra a destra;
- `"xy"` → ordinamento da sinistra a destra, poi dall’alto verso il basso. fileciteturn27file0

### Interpretazione
Questo parametro definisce la regola geometrica con cui si assegnano gli indici di istanza.

### Conseguenza importante
A parità di detection, cambiare `SORT_ORDER` cambia il naming finale delle istanze. Per questo è importante che il parametro resti coerente lungo tutti gli esperimenti di una stessa pipeline.

## Parametro `SAVE_DEBUG_IMAGES`

Il booleano `SAVE_DEBUG_IMAGES = True` abilita la produzione delle immagini annotate con bbox e instance id. fileciteturn27file0

---

# 4. Funzioni di utilità geometriche

## Funzione `compute_center(bbox)`

### Scopo
Calcolare il centro geometrico di un bounding box.

### Input
Il bbox è nel formato:

```python
[x1, y1, x2, y2]
```

### Logica
La funzione calcola:

- `xc = (x1 + x2) / 2.0`
- `yc = (y1 + y2) / 2.0`

### Output
Restituisce la coppia:

```python
(xc, yc)
```

### Ruolo nella pipeline
Questa funzione è la base di tutto l’ordinamento. Lo script 02 non ordina i componenti usando l’angolo superiore del bbox, ma il **centro del bbox**, perché il centro è più stabile e più rappresentativo della posizione del simbolo nell’immagine. fileciteturn27file0

---

## Funzione `sort_components(components, sort_order="yx")`

### Scopo
Ordinare una lista di componenti in base alla posizione del centro del loro bounding box.

### Logica interna
La funzione definisce una helper locale `key_fn(comp)`:

1. legge `bbox` del componente;
2. calcola `(xc, yc)` con `compute_center(...)`;
3. sceglie la chiave di ordinamento in base a `sort_order`.

### Due modalità disponibili

#### Caso `sort_order == "xy"`
La chiave è:

```python
(xc, yc)
```

Quindi l’ordinamento privilegia prima la coordinata x, poi la y.

Interpretazione geometrica:
- prima da sinistra a destra;
- a parità, dall’alto verso il basso.

#### Caso `sort_order == "yx"`
La chiave è:

```python
(yc, xc)
```

Interpretazione geometrica:
- prima dall’alto verso il basso;
- a parità, da sinistra a destra.

### Output
Ritorna la lista ordinata tramite `sorted(...)`.

### Significato
Questa funzione è il cuore della convenzione di numerazione. Tutta l’assegnazione delle istanze dipende da questo ordinamento. fileciteturn27file0

---

# 5. Funzione principale di assegnazione: `assign_instances_to_image(data, sort_order="yx")`

## Scopo
Dato il contenuto di un JSON del passo 01, costruire un nuovo dizionario in cui tutti i componenti abbiano un `instance_id` assegnato in modo coerente.

## Input
Il parametro `data` è un dizionario che contiene almeno:

- `components`: lista dei componenti rilevati nell’immagine.

Ogni componente contiene tipicamente campi come:

- `class_id`
- `class_name`
- `bbox`
- `conf`

## Logica dettagliata

### 1. Estrazione della lista componenti
La funzione legge:

```python
components = data.get("components", [])
```

Se il campo non esiste, usa lista vuota.

### 2. Raggruppamento per classe
Viene creato un `defaultdict(list)` chiamato `grouped`.

Poi, per ogni componente:

- si legge `class_id`;
- il componente viene inserito nel gruppo corrispondente.

### Significato del raggruppamento
Questo passaggio è fondamentale perché la numerazione viene assegnata **per classe**, non globalmente.

Esempio:
- tutti i resistori vengono numerati indipendentemente dai condensatori;
- tutti i transistor vengono numerati indipendentemente dalle sorgenti.

### 3. Ordinamento interno a ciascun gruppo
Per ogni coppia `(class_id, comps)` nei gruppi:

- la lista `comps` viene ordinata con `sort_components(comps, sort_order=sort_order)`.

### Significato
Questo definisce la sequenza interna di numerazione per quella classe.

### 4. Assegnazione dell’indice progressivo
Per i componenti ordinati di una certa classe, la funzione fa:

```python
for idx, comp in enumerate(comps_sorted, start=1):
```

quindi l’indice parte da 1.

Per ogni componente:

- crea una copia superficiale `comp_copy = dict(comp)`;
- aggiunge:

```python
comp_copy["instance_id"] = f"{class_id}.{idx}"
```

### Formato dell’identificatore
Il formato finale è quindi:

```text
<class_id>.<indice>
```

per esempio:

```text
22.1
22.2
```

### Motivazione della copia
La copia serve a non modificare direttamente l’oggetto originale mentre si costruisce il nuovo output.

### 5. Ricomposizione della lista globale
Tutti i componenti con instance id vengono aggiunti a `updated_components`.

Una volta finiti tutti i gruppi, la lista globale viene nuovamente ordinata con:

```python
updated_components = sort_components(updated_components, sort_order=sort_order)
```

### Perché si riordina di nuovo
Perché dopo il raggruppamento per classe, i componenti sarebbero altrimenti ordinati “a blocchi di classe”. Invece il JSON finale deve restare leggibile anche come sequenza globale sull’immagine.

Questa è una scelta molto utile per il debug e per l’ispezione manuale del file JSON.

### 6. Costruzione dell’output finale
La funzione crea:

```python
output = dict(data)
```

poi aggiorna i campi:

- `output["components"] = updated_components`
- `output["instance_assignment_sort_order"] = sort_order`
- `output["n_components"] = len(updated_components)`

### Significato dei campi aggiunti

#### `instance_assignment_sort_order`
Serve a salvare esplicitamente nel JSON quale convenzione di ordinamento è stata usata. Questo rende il file autoesplicativo e facilita la riproducibilità.

#### `n_components`
Salva il numero totale di componenti presenti nell’immagine dopo il passo 02.

### Output
La funzione restituisce il dizionario completo aggiornato.

---

## Interpretazione concettuale di `assign_instances_to_image(...)`

Questa funzione realizza la logica fondamentale dello script 02:

- **separa i componenti per classe**;
- **assegna un indice locale a ciascuna classe**;
- **mantiene una vista globale ordinata dell’immagine**.

Dal punto di vista della pipeline, è la funzione che introduce il concetto di **istanza identificabile**.

---

# 6. Debug image: visualizzazione delle istanze

Lo script 02 non si limita a salvare il JSON. Può anche costruire un’immagine di debug che mostra chiaramente quali istanze sono state assegnate.

Questo è estremamente utile per verificare che:

- l’ordinamento sia coerente con quanto atteso;
- due componenti vicini non siano stati numerati in modo controintuitivo;
- la convenzione `xy` o `yx` sia quella desiderata.

---

## Funzione `draw_components_with_instances(image_bgr, components)`

### Scopo
Disegnare sull’immagine originale:

- il bbox di ogni componente;
- una label contenente:
  - `instance_id`
  - `class_name`
  - `conf`

### Passaggi principali

#### 1. Copia dell’immagine
La funzione crea:

```python
out = image_bgr.copy()
```

in modo da non modificare l’immagine originale.

#### 2. Definizione dei parametri grafici
Vengono scelti:

- colore dei bbox;
- colore del testo;
- colore dello sfondo label;
- font OpenCV;
- scale e thickness.

### 3. Loop sui componenti
Per ogni componente:

- legge il bbox;
- converte le coordinate in interi;
- legge:
  - `instance_id`
  - `class_name`
  - `conf`
- costruisce la stringa label nel formato:

```text
instance_id | class_name | conf
```

### 4. Disegno del rettangolo
Usa `cv2.rectangle(...)` per disegnare il bbox.

### 5. Disegno della label
La funzione:

1. misura il testo con `cv2.getTextSize(...)`;
2. calcola il box della label;
3. crea un overlay;
4. disegna un rettangolo di sfondo semi-trasparente;
5. fonde overlay e immagine con `cv2.addWeighted(...)`;
6. disegna il bordo della label;
7. stampa il testo con `cv2.putText(...)`.

### Output
Ritorna l’immagine annotata.

### Significato
La debug image del passo 02 è una vista qualitativa del mapping:

```text
bbox -> instance_id
```

ed è lo strumento principale per verificare la correttezza dell’ordinamento. fileciteturn27file0

---

## Funzione `save_debug_image(updated_data, output_image_path)`

### Scopo
Caricare l’immagine originale, applicare `draw_components_with_instances(...)` e salvare il risultato su disco.

### Passaggi
1. legge `image_path` dal JSON aggiornato;
2. carica l’immagine con OpenCV;
3. se l’immagine non è leggibile, stampa un warning e si ferma;
4. altrimenti costruisce `debug_img`;
5. salva il file in `output_image_path`.

### Significato
Questa funzione separa la logica di rendering dalla logica di I/O, mantenendo il codice più ordinato.

---

# 7. Funzione `main()`

## Scopo
Eseguire il passo 02 su tutti i file JSON presenti nella cartella di input.

## Struttura completa

### 1. Controllo della cartella di input
Se `INPUT_DIR` non esiste, la funzione solleva:

```python
FileNotFoundError
```

### 2. Creazione cartelle di output
La funzione crea, se necessario:

- `OUTPUT_DIR`
- `DEBUG_IMAGES_DIR`

### 3. Raccolta dei file JSON
Viene costruita la lista ordinata di tutti i file `.json` presenti in input.

Se la lista è vuota, viene sollevato un errore.

### 4. Stampa delle informazioni iniziali
Lo script stampa:

- input directory;
- output directory;
- numero di file trovati;
- valore di `SORT_ORDER`.

### 5. Loop sui file
Per ogni file JSON:

1. apre il file;
2. legge il contenuto con `json.load(...)`;
3. richiama `assign_instances_to_image(...)`;
4. salva il nuovo JSON in output;
5. se `SAVE_DEBUG_IMAGES` è attivo, salva anche l’immagine annotata;
6. stampa una riga di avanzamento con il numero di componenti trovati.

### 6. Stampa finale
Al termine, stampa i percorsi in cui sono stati salvati:

- i JSON;
- le immagini di debug.

### Significato
`main()` è l’orchestratore dello stadio 02: si occupa del batch processing dell’intera cartella e delega la logica vera alle funzioni già descritte. fileciteturn27file0

---

# 8. Struttura dell’output del passo 02

Dopo l’esecuzione dello script, ogni JSON contiene:

- la lista dei componenti aggiornata;
- il campo `instance_id` per ogni componente;
- il campo `instance_assignment_sort_order`;
- il campo `n_components`.

## Esempio concettuale

Un componente che prima era descritto così:

```json
{
  "class_id": 22,
  "class_name": "Resistor",
  "bbox": [100, 80, 140, 160],
  "conf": 0.94
}
```

può diventare:

```json
{
  "class_id": 22,
  "class_name": "Resistor",
  "bbox": [100, 80, 140, 160],
  "conf": 0.94,
  "instance_id": "22.1"
}
```

## Importanza per il passo 03
Nel passo successivo, questi `instance_id` vengono usati per costruire identificatori più ricchi, per esempio:

```text
22.1:t1
22.1:t2
```

Quindi il naming introdotto dallo script 02 è la base di tutta la nomenclatura successiva dei terminali.

---

# 9. Scelte progettuali principali

## Numerazione per classe e non globale

### Vantaggio
Rende il naming più leggibile e semanticamente chiaro. Un ID come `22.3` dice subito che si tratta del terzo componente della classe 22.

### Svantaggio
L’indice non rappresenta la posizione globale nell’immagine, ma solo la posizione relativa all’interno della classe.

### Motivazione della scelta
Per la pipeline questo è un vantaggio, perché il tipo del componente rimane incorporato nell’identificatore.

---

## Ordinamento basato sul centro del bbox

### Vantaggio
Il centro del bbox è meno sensibile a piccole variazioni del box rispetto agli angoli.

### Motivazione
È una scelta semplice ma robusta per definire un ordine geometrico coerente.

---

## Riordinamento finale globale dei componenti

### Vantaggio
Mantiene il JSON leggibile secondo la disposizione nell’immagine, invece di avere tutti i componenti raggruppati a blocchi di classe.

### Effetto
La numerazione viene assegnata per classe, ma la lista finale nel JSON resta ordinata nello spazio dell’immagine.

---

## Produzione di immagini di debug

### Vantaggio
Permette una verifica qualitativa immediata.

### Ruolo pratico
Se un’istanza sembra “sbagliata”, il problema è quasi sempre riconducibile a:

- ordine `xy` vs `yx`;
- bbox anomalo;
- componenti molto vicini con centri quasi allineati.

---

# 10. Limiti dello script 02

Anche se il passo 02 è molto utile, è importante chiarire cosa **non** fa.

## Non risolve il significato elettrico
Lo script non cerca di capire:

- quale componente venga prima nel flusso del circuito;
- quale sia il verso della corrente;
- quale nodo sia logicamente precedente o successivo.

L’ordinamento è **puramente geometrico**, non elettrico.

## Non modifica i bbox
I bounding box vengono semplicemente copiati dall’output del detector. Lo script non fa refine geometrico.

## Non verifica collisioni semantiche
Se il detector ha sbagliato classe o ha duplicato componenti, lo script 02 assegnerà comunque un `instance_id`. Quindi la correttezza dell’assegnazione dipende dalla qualità del passo 01.

## L’ordine può cambiare se cambia `SORT_ORDER`
La convenzione di naming è coerente solo se il parametro di ordinamento resta fisso in tutti gli esperimenti.

---

# 11. Interpretazione del passo 02 in ottica tesi

Dal punto di vista della tesi, il passo `02_assign_instances` può essere descritto come uno stadio di **normalizzazione strutturale delle detection**.

## Formula sintetica
Il detector produce:

- componenti rilevati;
- bounding box;
- classi;
- score di confidenza.

Lo script 02 aggiunge:

- una **identità locale riproducibile** per ogni componente.

## Descrizione accademica possibile
Una formulazione chiara potrebbe essere:

> Il secondo passo della pipeline assegna a ogni componente rilevato un identificatore di istanza univoco, costruito tramite ordinamento geometrico dei bounding box all’interno di ciascuna classe. Questa fase non altera il risultato della detection, ma introduce una nomenclatura consistente e riproducibile che viene poi utilizzata dagli stadi successivi per la stima dei terminali e delle connessioni.

---

# 12. Considerazioni architetturali finali

## Livelli logici del file

Il file `02_assign_instances.py` è organizzato in tre livelli semplici ma chiari:

### 1. Livello geometrico minimale
- `compute_center(...)`
- `sort_components(...)`

Definisce l’ordinamento spaziale.

### 2. Livello di trasformazione dati
- `assign_instances_to_image(...)`

Trasforma il JSON del passo 01 nel JSON del passo 02.

### 3. Livello di visualizzazione e orchestrazione
- `draw_components_with_instances(...)`
- `save_debug_image(...)`
- `main()`

Gestisce output batch e debug qualitativo.

## Filosofia generale
Lo script è volutamente semplice: non cerca di fare reasoning elettrico, ma costruisce una base ordinata e stabile per i passi successivi.

Questa semplicità è un punto di forza, perché:

- rende il modulo molto robusto;
- rende il naming completamente interpretabile;
- riduce il rischio di introdurre euristiche troppo arbitrarie in una fase che ha solo bisogno di indicizzazione.

---

# 13. Riassunto finale

Il passo `02_assign_instances`:

- legge i componenti rilevati dal passo 01;
- li raggruppa per classe;
- li ordina geometricamente in base al centro del bbox;
- assegna un identificatore `class_id.indice`;
- salva il JSON aggiornato;
- produce una debug image con bbox e nomi di istanza.

In sintesi, questo stadio non “capisce” ancora il circuito, ma costruisce la struttura di naming necessaria perché i passi successivi possano farlo in modo consistente.
