# Changelog pipeline topology_v3_three_terminals

## Obiettivo generale della versione
Questa variante della pipeline è stata aggiornata per gestire correttamente anche i **componenti a 3 terminali**, in particolare:

- **Mosfet**
- **NPN Transistor**

L’idea principale è stata:
1. mantenere la pipeline `01 -> 08` uguale come struttura;
2. migliorare soprattutto il passo **03** per stimare bene i terminali;
3. allineare poi i passi successivi (**05**, **06**, **07**, **08**) ai nuovi output.

---

# 01_detect_components.py

## Cambiamenti fatti
- È stato introdotto un filtro più restrittivo sulla **confidence** delle detection YOLO.
- In pratica vengono tenuti solo i componenti con confidence sopra la soglia scelta.
- Questo è servito a ridurre alcuni **falsi positivi**, ad esempio:
  - simboli numerici interni scambiati per `Current_Source`
  - testo o simboli vicino a `VDD` scambiati per componenti reali

## Motivazione
Nel batch dei diagrammi con transistor e mosfet erano comparsi componenti non reali.  
Invece di aggiungere subito euristiche complicate, è stato scelto prima un approccio semplice:
- filtrare le detection poco affidabili in ingresso.

## Nota
- In questa fase **non** sono state aggiunte euristiche semantiche avanzate sui componenti del `01`.
- La correzione principale è stata il filtro sulla confidence.

---

# 02_assign_instances.py

## Cambiamenti fatti
- Nessuna modifica strutturale importante.

## Nota
- Il file continua a fare l’assegnazione degli `instance_id` come prima.
- È rimasto compatibile con il nuovo output del `01`.

---

# 03_estimate_terminals.py

## Cambiamenti fatti
Questo è il file che è stato modificato di più.

### 1. Supporto ai componenti a 3 terminali
È stata aggiunta una nuova strategia per i componenti a 3 terminali:

- `three_terminal_by_side_pattern`

Questa strategia è stata usata per:
- `Mosfet`
- `NPN_Transistor`

### 2. Distinzione tra lato singolo e coppia ortogonale
Per i 3-terminali non basta più dire “i terminali stanno su certi lati del bbox”.  
È stato introdotto il concetto di:

- **lato singolo** = gate/base
- **coppia ortogonale** = gli altri due terminali

Quindi il flusso è diventato:
1. stimare il lato singolo;
2. ricavare il template coerente dei tre lati;
3. localizzare il punto preciso lungo il lato.

### 3. Localizzazione fine del terminale lungo il lato
È stata introdotta una stima più precisa del punto terminale con ricerca a **picco sul lato**:

- scansione lungo il lato del bbox
- scelta del picco più robusto
- fallback al centro del lato se il segnale è debole

Funzioni/logica principali:
- `geom_terminal_point_by_side_peak(...)`
- `_select_peak_index_from_scores(...)`

### 4. Modalità dedicata per i 3 terminali
È stata introdotta la modalità:

- `three_terminal_structured`

Questa modalità:
- usa la stima del lato singolo;
- poi cerca i due terminali opposti in una zona coerente con quel lato.

### 5. Euristiche specifiche per Mosfet
Per i Mosfet sono state aggiunte euristiche dedicate, perché il gate veniva spesso confuso con drain/source.

Sono stati introdotti:
- probe **near/far**
- probe stretti quasi solo **esterni** al bbox
- score specifico per il lato singolo del Mosfet
- score aggiuntivo per distinguere **gate sinistro** vs **gate destro**

Logica introdotta:
- `get_mosfet_single_side_scores(...)`
- `get_mosfet_lateral_gate_scores(...)`

### 6. Bias laterale per il gate del Mosfet
Nel dataset osservato, il gate dei Mosfet verticali è quasi sempre laterale.  
Per questo è stato introdotto un bias che forza il confronto principalmente tra:

- `left`
- `right`

invece di lasciare competere allo stesso modo anche `top` e `bottom`.

### 7. Debug più ricco
Per ogni terminale ora vengono salvate più informazioni:
- `terminal_point_mode`
- `terminal_point_debug`
- offset relativo sul lato
- tipo di ruolo del terminale nei 3-terminali
- informazioni sui punteggi usati in stima

### 8. Compatibilità mantenuta con le strategie precedenti
Sono rimaste compatibili anche le strategie già presenti:
- `fixed`
- `auto_by_aspect_ratio`
- `one_terminal_by_orientation`
- `two_terminal_by_connection_axis`
- `two_terminal_capacitor`
- `two_terminal_switch`
- `terminal_auto_one_or_two`

## Risultato pratico
Dopo queste modifiche:
- gli **NPN transistor** sono stati stimati bene;
- i **Mosfet** sono stati corretti molto meglio rispetto alla versione iniziale;
- la pipeline è diventata adatta ai diagrammi con componenti a 3 terminali.

---

# 04_extract_wires.py

## Cambiamenti fatti
- Nessuna modifica strutturale grossa in questa fase.

## Nota
- Il file è stato verificato come compatibile con il nuovo output del `03`.
- L’estrazione dei wire/skeleton continua a lavorare come prima.
- Le scritte/testi del diagramma non sono stati trattati come parte della logica di matching dei terminali.

---

# 05_build_nets.py

## Cambiamenti fatti

### 1. Allineamento al nuovo output del 03
Il `05` è stato adattato per lavorare bene con i terminali stimati dal nuovo `03`, soprattutto i terminali a 3 lati dei Mosfet e dei transistor.

### 2. Matching terminale -> connected component dello skeleton
È stata introdotta una ricerca più robusta tra terminale e componente connessa nello skeleton:
- prima con finestra **direzionale**
- poi con fallback a finestra **quadrata**

### 3. Ricerca direzionale asimmetrica
La finestra direzionale non è più simmetrica attorno al terminale.  
È stata resa coerente con il lato del terminale:

- `left` cerca soprattutto verso sinistra
- `right` cerca soprattutto verso destra
- `top` cerca soprattutto verso l’alto
- `bottom` cerca soprattutto verso il basso

Sono stati introdotti parametri tipo:
- `TERMINAL_SEARCH_OUTWARD`
- `TERMINAL_SEARCH_INWARD`
- `TERMINAL_DIRECTIONAL_HALFSPAN`
- `TERMINAL_SQUARE_FALLBACK_RADIUS`

### 4. Filtro sulle net troppo deboli con un solo terminale
È stato aggiunto un filtro per eliminare candidate net poco affidabili quando toccano un solo terminale:

- minimo numero di pixel
- minimo span del bbox

Parametri introdotti:
- `MIN_SINGLE_TERMINAL_NET_PIXELS`
- `MIN_SINGLE_TERMINAL_NET_SPAN`

### 5. Fix bug emersi durante l’esecuzione
Sono stati corretti errori come:
- `get_directional_window() got an unexpected keyword argument 'radius'`
- `NameError: TERMINAL_SEARCH_RADIUS is not defined`

Questi bug erano dovuti al fatto che la funzione era stata aggiornata da schema simmetrico a schema `outward/inward`, ma nel file erano rimasti riferimenti vecchi.

### 6. Miglioramento delle immagini debug
Sono stati migliorati:
- colori delle net
- leggibilità delle scritte `N1`, `N2`, ...
- overlay
- terminal debug

Per rendere più leggibili le immagini su sfondo bianco.

## Risultato pratico
Il `05` produce net coerenti e sufficientemente stabili per essere usate nel `06`.

---

# 06_match_terminals_to_nets.py

## Cambiamenti fatti

### 1. Allineamento ai path della variante v3
Il file è stato allineato alla pipeline:

- `topology_v3_three_terminals`

### 2. Matching più coerente col lato del terminale
La ricerca del match terminale -> net è stata resa coerente con:
- lato del terminale (`relative_position`)
- geometria del terminale stimata nel `03`

### 3. Match con confidence
È stata mantenuta / consolidata la classificazione del match in livelli di affidabilità:
- `high`
- `medium`
- `low`

Questo permette di capire subito se un aggancio terminale-net è forte oppure dubbio.

### 4. Visualizzazione debug migliorata
Sono stati migliorati:
- colore dei punti terminale
- colore dello snap point
- linee di collegamento
- testo del debug

L’obiettivo era rendere leggibili i match anche sopra diagrammi bianchi.

### 5. Risultati verificati sui batch
Dai test fatti:
- immagini 1, 2, 3: risultati molto buoni
- immagine 4: qualche `medium`, ma coerente
- immagini 5, 6, 7, 8: i Mosfet sono stati agganciati in modo sensato

## Risultato pratico
Il `06` è stato considerato **completato** e validato sui batch di prova.

---

# 07_export_graph.py

## Stato
Questo file richiede solo modifiche leggere.

## Cambiamenti previsti / consigliati

### 1. Aggiornamento path
Passare da:
- `topology_v2`

a:
- `topology_v3_three_terminals`

### 2. Aggiornamento metadata del grafo
Aggiornare i campi che descrivono lo stage sorgente, per riflettere la nuova pipeline.

### 3. Aggiunta dei nuovi dati terminale nel nodo Terminal
Conviene esportare nel grafo anche:
- `terminal_point_mode`
- `terminal_point_debug`

così il grafo mantiene anche le informazioni più avanzate della stima terminali del `03`.

### 4. Summary più ricco
Aggiungere nel summary del grafo:
- numero terminali matched
- numero terminali unmatched

## Nota
La struttura generale del `07` rimane valida:
- nodi `Diagram`
- nodi `Component`
- nodi `Terminal`
- nodi `Net`
- archi `HAS_COMPONENT`
- archi `HAS_NET`
- archi `HAS_TERMINAL`
- archi `CONNECTED_TO`

Quindi qui non serve una riscrittura completa.

---

# 08_visualize_graph.py

## Stato
Il file è già buono come struttura generale e genera:

- full graph PNG/HTML
- component -> net PNG/HTML
- overlay sul diagramma
- dashboard `index.html`

## Cambiamenti consigliati / previsti

### 1. Aggiornamento path
Passare da:
- `topology_v2`

a:
- `topology_v3_three_terminals`

### 2. Hover più ricco sui terminali
Aggiungere nei tooltip dei nodi terminale campi come:
- `component_class_name`
- `terminal_name`
- `terminal_point_mode`

per leggere meglio i casi dei Mosfet e dei transistor a 3 terminali.

### 3. Overlay con colori legati alla confidence
Attualmente l’overlay distingue soprattutto i suspicious.  
Conviene passare a colori basati su:
- `high` = verde
- `medium` = arancio
- `low` = rosso
- `none` = grigio
- `suspicious` = rosso forte

### 4. Etichetta opzionale per match non-high
Nei casi dubbi conviene mostrare vicino al terminale una piccola label con:
- `medium`
- `low`

per facilitare la lettura dell’overlay.

## Nota
Non serve modificare la logica centrale di:
- `build_nx_graph`
- `compute_layered_positions`
- `derive_component_net_graph`
- viste `component -> net`

perché sono già compatibili con la nuova struttura del grafo.
