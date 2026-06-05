# Metadata della pipeline

Questa cartella contiene i file di metadati usati dalla pipeline per interpretare le classi dei componenti elettrici, stimare i terminali e costruire il grafo topologico.

Il file principale e:

```text
class_terminals_v1.yaml
```

I file CSV sono invece riepiloghi statistici delle classi nel dataset:

```text
class_summary_global.csv
class_summary_by_split.csv
```

## `class_terminals_v1.yaml`

`class_terminals_v1.yaml` e il vocabolario operativo della pipeline. Per ogni classe YOLO definisce:

- nome della classe;
- tipo di simbolo;
- se la classe deve essere usata per stimare terminali;
- se la classe deve essere usata per mascherare il componente durante l'estrazione fili;
- strategia geometrica per stimare i terminali;
- eventuale strategia semantica per rinominare terminali/pin;
- orientazioni previste;
- note operative specifiche.

La chiave numerica esterna corrisponde al `class_id` del dataset. Esempio:

```yaml
22:
  name: Resistor
  symbol_type: two_terminal
  use_for_terminals: true
  use_for_masking: true
  terminal_strategy: two_terminal_by_connection_axis
```

In questo caso la classe `22` e `Resistor`, viene usata per stimare terminali, viene mascherata durante la fase di estrazione dei fili, e usa la strategia `two_terminal_by_connection_axis`.

## Campi principali

### `name`

Nome leggibile della classe. Deve essere coerente con le classi prodotte dal detector e con i nomi attesi negli script.

Esempi:

```text
Resistor
GND
Integrated_Circuit
Operational_Amplifier
NPN_Transistor
```

### `symbol_type`

Descrive la struttura generale del simbolo:

| Valore | Significato |
|---|---|
| `one_terminal` | Componente con un solo terminale, per esempio `GND` o `Antenna`. |
| `two_terminal` | Componente a due terminali, per esempio resistori, condensatori, diodi. |
| `three_terminal` | Componente a tre terminali, per esempio transistor e MOSFET. |
| `multi_terminal` | Componente con numero variabile o multiplo di terminali, per esempio IC, connettori, trasformatori. |
| `variable_terminal` | Componente con numero terminali non fisso, per esempio `Terminal`. |

### `use_for_terminals`

Indica se la classe deve partecipare alla stima dei terminali.

Se e `true`, lo script di terminal estimation cerca endpoint per quel componente. Se e `false`, la classe puo essere riconosciuta ma non usata come nodo terminale del grafo.

### `use_for_masking`

Indica se il componente deve essere mascherato durante l'estrazione dei fili.

La maschera evita che il corpo del componente venga interpretato come filo. Per alcune classi e importante preservare piccole aree attorno ai terminali, in modo da non cancellare i contatti reali con lo skeleton dei fili.

### `terminal_strategy`

Definisce la strategia principale per stimare la posizione dei terminali.

Strategie principali:

| Strategia | Uso |
|---|---|
| `one_terminal_by_orientation` | Componenti a un terminale, con lato del contatto determinato dall'orientazione. |
| `two_terminal_by_connection_axis` | Componenti a due terminali: cerca l'asse reale di connessione, orizzontale o verticale. |
| `auto_by_aspect_ratio` | Usa il rapporto larghezza/altezza per scegliere tra orientazione orizzontale e verticale. |
| `three_terminal_by_side_pattern` | Componenti a tre terminali, come BJT e MOSFET, stimati tramite pattern laterale. |
| `connector_by_projection` | Connettori multi-pin, stimati tramite proiezione dei contatti. |
| `integrated_circuit_wire_contacts` | Integrati generici: terminali stimati dai fili che toccano il corpo IC. |
| `opamp_by_orientation_and_optional_supply` | Opamp: ingressi, uscita e pin supply opzionali in base all'orientazione. |
| `transformer_external_wires` | Trasformatori: terminali esterni sui lati del simbolo. |
| `terminal_auto_one_or_two` | Terminali generici con uno o due contatti possibili. |

Il principio generale e geometrico: prima si cercano i contatti fisici visibili, poi si aggiungono eventuali informazioni semantiche.

### `terminal_point_mode`

Campo opzionale che raffina il modo in cui viene scelto il punto terminale.

Esempi:

```text
two_terminal_side_peak
bbox_side_center
ic_body_side_contact
opamp_structured
```

Serve quando il solo `terminal_strategy` non basta a definire dove collocare esattamente il punto del terminale.

### `semantic_terminal_strategy`

Definisce una strategia semantica per rinominare i terminali stimati geometricamente.

Esempi:

| Strategia | Effetto |
|---|---|
| `diode_cathode_from_bar` | Usa la barra del diodo/LED per distinguere catodo e anodo. |
| `battery_positive_from_long_plate` | Usa la piastra lunga della batteria per riconoscere il positivo. |
| `voltage_source_positive_from_plus_marker` | Usa il marker `+` della sorgente di tensione. |
| `current_source_direction_from_arrow` | Usa la freccia della sorgente di corrente. |
| `npn_emitter_from_arrow_branch` | Usa la freccia del BJT per riconoscere l'emettitore. |
| `mosfet_gate_with_optional_source_drain` | Riconosce il gate e prova ad assegnare source/drain. |
| `polarized_capacitor_positive_from_marker` | Usa il marker di polarita del condensatore polarizzato. |

Questa distinzione e importante: la geometria stabilisce dove sono i terminali, la semantica prova a dare loro nomi elettricamente significativi.

### `semantic_roles`

Mappa i risultati della strategia semantica in ruoli terminali.

Esempio per un diodo:

```yaml
semantic_roles:
  marker_side: cathode
  other_side: anode
```

### `orientations`

Descrive i terminali attesi in base all'orientazione del simbolo.

Esempio per un componente a due terminali:

```yaml
orientations:
  horizontal:
    - name: t1
      relative_position: left
    - name: t2
      relative_position: right
  vertical:
    - name: t1
      relative_position: top
    - name: t2
      relative_position: bottom
```

Per componenti direzionali o multi-terminale, le orientazioni possono includere ruoli, slot o terminali opzionali.

### `notes`

Campo libero per note operative. Va usato con parsimonia per chiarire comportamenti particolari o decisioni storiche.

## Caso speciale: `Integrated_Circuit`

La classe `Integrated_Circuit` e la piu articolata. La pipeline non deve inventare pin usando solo l'OCR: prima deve trovare i contatti geometrici tra fili e corpo dell'integrato.

La logica e:

1. partire dal bbox YOLO;
2. raffinare il rettangolo reale del corpo IC (`body_bbox`);
3. cercare contatti filo-corpo sui lati sinistro, destro, alto e basso;
4. creare terminali solo dai contatti geometricamente visibili;
5. usare OCR per associare marking dell'IC e numeri/label dei pin;
6. salvare queste informazioni nel JSON senza dedurre funzioni interne da datasheet.

La configurazione IC contiene sezioni specifiche:

```yaml
body_refinement:
pin_detection:
terminal_naming:
ocr:
mask:
```

### `body_refinement`

Serve a distinguere:

```text
bbox_yolo    = bbox grezzo rilevato dal detector
body_bbox    = rettangolo reale del corpo IC
search_bbox  = area espansa usata per cercare fili e testi vicini
```

Questa distinzione riduce falsi contatti quando il bbox YOLO include testi, componenti vicini o fili esterni.

### `pin_detection`

Definisce come cercare i pin:

- lati da analizzare (`left`, `right`, `top`, `bottom`);
- bande di scansione;
- lunghezza minima dei contatti;
- fusione di segmenti vicini;
- esclusione degli angoli.

La regola metodologica e: un terminale IC nasce da un contatto filo-corpo, non da un numero OCR isolato.

### `terminal_naming`

Definisce come nominare i terminali:

- se c'e un numero pin OCR affidabile, puo essere usato;
- altrimenti si usa un fallback come `left_1`, `right_2`, `top_1`;
- l'ordine dei lati e definito da `side_order`.

### `ocr`

Gestisce due livelli separati:

1. `ic_marking`: nome o sigla dell'integrato, per esempio `NE555`, `CD4017`, `LM317`.
2. `pin_labels`: numeri o label vicino ai terminali.

L'OCR arricchisce il JSON, ma non deve creare collegamenti o terminali non supportati dalla geometria.

### `mask`

Per gli IC la maschera dovrebbe preferire il `body_bbox`, non necessariamente tutto il bbox YOLO. Questo evita di cancellare fili o numeri vicini al package durante l'estrazione dei fili.

## File CSV di riepilogo

### `class_summary_global.csv`

Contiene il conteggio totale delle istanze per classe nel dataset.

Campi:

```text
class_id
class_name
total_count
```

### `class_summary_by_split.csv`

Contiene il conteggio per split.

Campi:

```text
class_id
class_name
train_count
valid_count
test_count
total_count
```

Questi file non guidano direttamente la stima dei terminali, ma sono utili per capire la distribuzione delle classi e individuare classi rare o sbilanciate.

## Come modificare lo YAML

Quando si modifica `class_terminals_v1.yaml`, conviene seguire questa checklist:

1. Verificare che il `class_id` corrisponda alla classe YOLO.
2. Mantenere coerente il campo `name` con gli output della pipeline.
3. Scegliere il `symbol_type` piu appropriato.
4. Definire o aggiornare `terminal_strategy`.
5. Aggiungere `semantic_terminal_strategy` solo se esiste un marker visibile affidabile.
6. Aggiornare `orientations` e `relative_position`.
7. Controllare che gli script che leggono lo YAML supportino la nuova strategia.
8. Eseguire un test su pochi circuiti prima di rilanciare batch completi.

## Regola pratica

Il file YAML non deve correggere il circuito e non deve dedurre il funzionamento elettrico. Deve solo fornire alla pipeline le regole per riconoscere terminali, ruoli e metadati visibili.

Per informazioni funzionali piu avanzate, come mapping tra pin number e funzione di un IC tramite datasheet, usare uno step successivo dedicato e non inserirlo implicitamente nella stima geometrica dei terminali.

