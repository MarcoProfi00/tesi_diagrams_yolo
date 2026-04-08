# Changelog pipeline topology_v4_source_mosfet_transistor

## Obiettivo generale della versione
Questa evoluzione della pipeline è stata aggiornata per gestire in modo più robusto:

- **componenti a 3 terminali**, in particolare:
  - **Mosfet**
  - **NPN Transistor**
- **componenti a 2 terminali più difficili**, in particolare:
  - **Inductor**
  - **Diode / LED / Zener_Diode / Photodiode**
  - **Capacitor / Polarized_Capacitor / Trim_Capacitor**
- **source e strumenti circolari**, in particolare:
  - **Voltage_Source**
  - **Current_Source**
  - **Signal_Source**
  - **Battery**
  - **Meter**
  - **Lamp**

L’idea principale della versione è stata:
1. mantenere la struttura generale della pipeline `01 -> 08`;
2. migliorare soprattutto il passo **03** per stimare meglio orientazione e terminali;
3. allineare i passi successivi (**05**, **06**, **07**, **08**) ai nuovi output;
4. rendere più leggibili i debug e gli overlay finali.

---

# 01_detect_components.py

## Cambiamenti fatti
- È stato introdotto un filtro più restrittivo sulla **confidence** delle detection YOLO.
- In pratica vengono tenuti solo i componenti con confidence sopra la soglia scelta.
- Questo è servito a ridurre alcuni **falsi positivi**, ad esempio:
  - simboli numerici interni scambiati per `Current_Source`
  - testo o simboli vicino a `VDD` scambiati per componenti reali
  - detection spurie su scritte o simboli decorativi

## Motivazione
Nei batch con mosfet, transistor e simboli annotativi comparivano componenti non reali.  
Prima di introdurre euristiche più complesse, è stato scelto un approccio semplice:
- filtrare le detection poco affidabili già in ingresso.

## Nota
- In questa fase **non** sono state aggiunte euristiche semantiche avanzate nel `01`.
- La correzione principale è stata il filtro sulla confidence.

---

# 02_assign_instances.py

## Cambiamenti fatti
- Nessuna modifica strutturale importante.

## Nota
- Il file continua ad assegnare gli `instance_id` come prima.
- È rimasto compatibile con il nuovo output del `01`.

---

# 03_estimate_terminals.py

## Cambiamenti fatti
Questo è il file che è stato modificato di più.

## 1. Refactoring del passo 03
Il vecchio file monolitico è stato diviso in un piccolo package dedicato, per rendere il codice più leggibile e più facile da estendere.

### Struttura introdotta
- `estimate_terminals/config.py`
- `estimate_terminals/io_utils.py`
- `estimate_terminals/image_ops.py`
- `estimate_terminals/geometry.py`
- `estimate_terminals/probes.py`
- `estimate_terminals/dispatcher.py`
- `estimate_terminals/processor.py`
- `estimate_terminals/debug_draw.py`
- `estimate_terminals/strategies_basic.py`
- `estimate_terminals/strategies_terminal_class.py`
- `estimate_terminals/strategies_three_terminal.py`

Il file `03_estimate_terminals.py` è rimasto come entry point principale e richiama le funzioni del package.

## 2. Supporto ai componenti a 3 terminali
È stata consolidata una strategia dedicata per i componenti a 3 terminali:

- `three_terminal_by_side_pattern`

Questa strategia è stata usata in particolare per:
- `Mosfet`
- `NPN_Transistor`

## 3. Distinzione tra lato singolo e coppia ortogonale
Per i 3-terminali non basta più dire genericamente che “i terminali stanno su certi lati del bbox”.  
È stato introdotto il concetto di:

- **lato singolo** = gate / base
- **coppia ortogonale** = drain-source oppure collector-emitter

Il flusso è diventato:
1. stimare il lato singolo;
2. ricavare il template coerente dei tre lati;
3. localizzare in modo più preciso il punto terminale su ciascun lato.

## 4. Localizzazione fine del terminale lungo il lato
È stata introdotta una stima più precisa del punto terminale con ricerca a **picco sul lato**:

- scansione lungo il lato del bbox;
- scelta del picco più robusto;
- fallback al centro del lato se il segnale è debole.

Funzioni/logica principali:
- `geom_terminal_point_by_side_peak(...)`
- `_select_peak_index_from_scores(...)`

## 5. Modalità dedicata per i 3 terminali
È stata introdotta e consolidata la modalità:

- `three_terminal_structured`

Questa modalità:
- usa la stima del lato singolo;
- poi cerca i due terminali opposti in una zona coerente con quel lato.

## 6. Euristiche specifiche per Mosfet
Per i Mosfet sono state aggiunte diverse euristiche dedicate, perché il gate veniva spesso confuso con drain/source.

Sono stati introdotti:
- probe **near/far**;
- probe stretti quasi solo **esterni** al bbox;
- score specifico per il lato singolo del Mosfet;
- score aggiuntivo per distinguere **gate sinistro** vs **gate destro**;
- validazione finale dell’orientazione usando i **tre punti terminali stimati**.

Logica introdotta:
- `get_mosfet_single_side_scores(...)`
- `get_mosfet_lateral_gate_scores(...)`
- `candidate_mosfet_orientations_from_bbox(...)`
- `score_mosfet_orientation_by_terminal_points(...)`

## 7. Bias laterale per il gate del Mosfet
Nel dataset osservato, per molti Mosfet verticali il gate è quasi sempre laterale.  
Per questo è stato introdotto un bias che forza il confronto soprattutto tra:

- `left`
- `right`

invece di lasciare competere allo stesso modo anche `top` e `bottom`.

Questo ha migliorato in particolare i casi in cui il bbox era disturbato da testo, etichette o simboli vicini.

## 8. Validazione e tie-break per casi quasi speculari
Nei casi difficili, soprattutto con simboli speculari o quasi simmetrici, è stata aggiunta una validazione finale dell’orientazione:

- confronto tra orientazioni candidate;
- uso dei terminal point stimati;
- tie-break dedicato nei casi quasi pari.

Questo è servito soprattutto per alcuni Mosfet in cui l’orientazione risultava “speculare al contrario”.

## 9. Miglioramenti specifici per NPN Transistor
La stessa logica dei 3-terminali è stata adattata bene anche agli **NPN Transistor**:
- base come lato singolo;
- collector/emitter come coppia ortogonale;
- stima più stabile sui diagrammi analogici.

In pratica, dopo le modifiche:
- i transistor NPN sono stati stimati bene nella maggior parte dei casi;
- i Mosfet sono risultati molto più stabili rispetto alle versioni iniziali.

## 10. Supporto migliore ai diodi e simboli affini
Sono state riviste anche le strategie per i componenti a 2 terminali di tipo diodo:
- `Diode`
- `LED`
- `Zener_Diode`
- `Photodiode`

Nei test, i LED restano ancora più sensibili alla forma del bbox e alla presenza delle frecce luminose, quindi la stima è stata resa più semplice e robusta senza introdurre euristiche troppo complesse.

## 11. Supporto migliore a induttori e componenti stretti
Per componenti come `Inductor` e alcuni resistori molto stretti è stato introdotto l’uso esplicito di modalità punto terminale più adatte, ad esempio:

- `two_terminal_side_peak`

Questo ha migliorato i casi in cui il semplice centro del lato del bbox non cadeva sul vero punto di connessione al filo.

## 12. Supporto ai source e strumenti circolari
È stato aggiunto il supporto e/o consolidato il comportamento per simboli circolari e sorgenti:

- `Voltage_Source`
- `Current_Source`
- `Signal_Source`
- `Battery`
- `Meter`
- `Lamp`

Per questi componenti è stata introdotta una strategia specifica per i simboli rotondi/orientati, in modo da evitare errori dovuti al testo interno o all’orientazione del simbolo.

Questo è servito soprattutto nei casi in cui due sorgenti apparentemente simili venivano trattate in modo diverso per colpa di piccoli dettagli grafici interni.

## 13. Debug più ricco
Per ogni terminale ora vengono salvate più informazioni:
- `terminal_point_mode`
- `terminal_point_debug`
- offset relativo sul lato;
- ruolo del terminale nei 3-terminali;
- informazioni sui punteggi usati nella stima.

## 14. Compatibilità mantenuta con le strategie precedenti
Sono rimaste compatibili anche le strategie già presenti o consolidate:
- `fixed`
- `auto_by_aspect_ratio`
- `one_terminal_by_orientation`
- `two_terminal_by_connection_axis`
- `two_terminal_capacitor`
- `two_terminal_switch`
- `terminal_auto_one_or_two`
- nuove modalità punto terminale come `two_terminal_side_peak`
- strategie per simboli rotondi / source

## Risultato pratico
Dopo queste modifiche:
- gli **NPN transistor** sono stati stimati bene;
- i **Mosfet** sono stati corretti molto meglio rispetto alla versione iniziale;
- gli **Inductor** hanno agganciato meglio i veri punti di contatto;
- i **source** (`Voltage_Source`, `Current_Source`, `Signal_Source`, `Battery`) sono diventati più stabili;
- anche strumenti come `Meter` e `Lamp` risultano meglio integrati nella pipeline.

---

# 04_extract_wires.py

## Cambiamenti fatti
- Nessuna modifica strutturale grossa in questa fase.

## Nota
- Il file è stato verificato come compatibile con il nuovo output del `03`.
- L’estrazione di wire e skeleton continua a lavorare come prima.
- Le scritte e i testi del diagramma non sono stati trattati come parte della logica di matching dei terminali.

---

# 05_build_nets.py

## Cambiamenti fatti

## 1. Allineamento al nuovo output del 03
Il `05` è stato adattato per lavorare bene con i terminali stimati dal nuovo `03`, soprattutto per:
- terminali a 3 lati di Mosfet e transistor;
- terminali di componenti stretti o con point mode dedicato.

## 2. Matching terminale -> connected component dello skeleton
È stata introdotta una ricerca più robusta tra terminale e connected component dello skeleton:
- prima con finestra **direzionale**;
- poi con fallback a finestra **quadrata**.

## 3. Ricerca direzionale asimmetrica
La finestra direzionale non è più simmetrica attorno al terminale.  
È stata resa coerente con il lato del terminale:

- `left` cerca soprattutto verso sinistra
- `right` cerca soprattutto verso destra
- `top` cerca soprattutto verso l’alto
- `bottom` cerca soprattutto verso il basso

Parametri introdotti / consolidati:
- `TERMINAL_SEARCH_OUTWARD`
- `TERMINAL_SEARCH_INWARD`
- `TERMINAL_DIRECTIONAL_HALFSPAN`
- `TERMINAL_SQUARE_FALLBACK_RADIUS`

## 4. Filtro sulle net troppo deboli con un solo terminale
È stato aggiunto un filtro per eliminare candidate net poco affidabili quando toccano un solo terminale:
- minimo numero di pixel;
- minimo span del bbox.

Parametri:
- `MIN_SINGLE_TERMINAL_NET_PIXELS`
- `MIN_SINGLE_TERMINAL_NET_SPAN`

## 5. Fix bug emersi durante l’esecuzione
Sono stati corretti errori come:
- `get_directional_window() got an unexpected keyword argument 'radius'`
- `NameError: TERMINAL_SEARCH_RADIUS is not defined`

Questi bug erano dovuti al passaggio da una finestra simmetrica a uno schema `outward/inward`.

## 6. Miglioramento delle immagini debug
Sono stati migliorati:
- colori delle net;
- leggibilità delle scritte `N1`, `N2`, ...;
- overlay;
- terminal debug.

L’obiettivo era rendere leggibili le immagini anche su sfondo bianco.

## Risultato pratico
Il `05` produce net coerenti e sufficientemente stabili per essere usate nel `06`.

---

# 06_match_terminals_to_nets.py

## Cambiamenti fatti

## 1. Allineamento ai path della nuova variante
Il file è stato riallineato alla pipeline corrente:

- `topology_v4_source_mosfet_transistor`

## 2. Matching più coerente col lato del terminale
La ricerca del match terminale -> net è stata resa coerente con:
- lato del terminale (`relative_position`)
- geometria del terminale stimata nel `03`
- point mode specifico usato per il componente

## 3. Ricerca locale migliorata
Sono stati mantenuti e rifiniti più stage di matching:
- punto diretto
- ricerca direzionale
- ricerca circolare / locale
- fallback finale

Questo ha aiutato soprattutto su:
- induttori;
- diodi;
- componenti piccoli;
- source e simboli rotondi.

## 4. Semplificazione della confidence
La classificazione del match è stata semplificata in una logica più netta:
- `ok`
- `unmatched`

Questa scelta è stata fatta per avere una lettura più semplice e più coerente del risultato finale.

## 5. Correzione del main e dei summary
Il `main()` è stato allineato alla nuova logica `ok/unmatched`, evitando incoerenze con il vecchio schema:
- `high`
- `medium`
- `low`

Ora i conteggi e i summary salvati nel JSON sono coerenti con la nuova classificazione.

## 6. Miglioramenti per gli override per classe
Sono stati introdotti o raffinati override per alcune classi più sensibili, ad esempio:
- `Inductor`
- classi di tipo diodo
- source / simboli circolari quando necessario

Questo ha permesso di allargare solo dove serviva la finestra di matching, senza peggiorare il comportamento globale.

## 7. Visualizzazione debug migliorata
Sono stati migliorati:
- colore dei punti terminale;
- colore dello snap point;
- linee di collegamento;
- testo del debug.

## Risultato pratico
Il `06` è stato considerato completato e validato sui batch di prova, con buon comportamento anche per:
- Mosfet
- transistor
- source
- induttori
- componenti a 2 terminali più difficili

---

# 07_export_graph.py

## Cambiamenti fatti

## 1. Aggiornamento path e variante
Il file è stato aggiornato per lavorare con l’output della variante:

- `topology_v4_source_mosfet_transistor`

## 2. Aggiornamento metadata del grafo
Sono stati aggiornati i campi che descrivono lo stage sorgente e la pipeline usata.

## 3. Esportazione più ricca dei dati terminale
Conviene e/o è stato reso possibile esportare nel grafo anche informazioni più ricche sui terminali, ad esempio:
- `terminal_point_mode`
- `terminal_point_debug`
- stato del match terminale-net

## 4. Summary del grafo più utile
Il summary del grafo è stato reso più informativo, includendo meglio:
- nodi totali
- archi totali
- terminali matched/unmatched
- eventuali suspicious match

## Nota
La struttura generale del `07` è rimasta valida:
- nodi `Diagram`
- nodi `Component`
- nodi `Terminal`
- nodi `Net`
- archi `HAS_COMPONENT`
- archi `HAS_NET`
- archi `HAS_TERMINAL`
- archi `CONNECTED_TO`

Quindi qui non è servita una riscrittura completa.

---

# 08_visualize_graph.py

## Cambiamenti fatti

## 1. Ristrutturazione del file 08
La parte di visualizzazione è stata riorganizzata in moduli dedicati, separando meglio:
- configurazione;
- I/O;
- render del full graph;
- render component-net;
- render overlay;
- dashboard HTML.

In particolare è stato isolato il rendering overlay in un file dedicato, ad esempio:
- `graph_viz/render_overlay.py`

Questo ha reso più semplice modificare solo l’overlay senza toccare il resto del file 08.

## 2. Gestione più pulita degli import
Sono stati sistemati i problemi di import dovuti al passaggio da file singolo a package/moduli, evitando errori come:
- import relativi eseguiti fuori package;
- path risolti sulla cartella sbagliata.

## 3. Aggiornamento path
Il file è stato riallineato ai path della nuova variante:

- `topology_v4_source_mosfet_transistor`

## 4. Overlay più leggibile sul diagramma
L’overlay finale è stato migliorato parecchio per essere leggibile anche su sfondo chiaro.

Sono stati introdotti o migliorati:
- linee con maggiore contrasto;
- nodi net più evidenti;
- etichette `N1`, `N2`, ... più leggibili;
- halo / box di testo per separare meglio le label dal diagramma;
- collegamenti terminale -> net più visibili.

## 5. Migliore leggibilità delle net labels
Le etichette delle net non sono più semplici scritte piccole sul diagramma, ma vengono mostrate con box più evidenti e posizionamento più leggibile.

## 6. Overlay utile anche per source e simboli rotondi
I miglioramenti grafici dell’overlay aiutano molto anche a leggere meglio casi con:
- `Voltage_Source`
- `Current_Source`
- `Signal_Source`
- `Battery`
- `Meter`
- `Lamp`

cioè componenti spesso circolari o con terminali piccoli.

## Risultato pratico
Il file 08 ora genera viste più leggibili e più utili per il debug finale del grafo, senza modificare la logica centrale di costruzione del grafo.

---

# Risultato complessivo della versione

## Miglioramenti principali ottenuti
Con questa serie di modifiche la pipeline è diventata molto più robusta su diagrammi analogici e misti, in particolare per:

- **Mosfet**
- **NPN Transistor**
- **Inductor**
- **Diodi e varianti**
- **Source e strumenti circolari**

## In particolare
- il passo **03** è diventato il centro della logica di stima avanzata dei terminali;
- il passo **05** costruisce net più stabili;
- il passo **06** aggancia bene terminali e net con una logica finale semplice (`ok/unmatched`);
- il passo **08** produce overlay molto più leggibili.

## Stato attuale
La pipeline è pronta per continuare con nuove classi più complesse, ad esempio:
- `Operation_Amplifier`
- altri componenti multi-terminale
- ulteriori rifiniture su classi ancora sensibili come alcuni LED o simboli particolarmente disturbati dal testo.
