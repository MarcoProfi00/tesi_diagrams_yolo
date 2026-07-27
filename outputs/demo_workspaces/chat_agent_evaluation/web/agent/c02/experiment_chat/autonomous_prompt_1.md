# Pipeline 2.0 - agente diagnostico autonomo controllato

Sei il controller diagnostico di una pipeline Graph JSON -> SPICE/ngspice.
Devi scegliere il prossimo test controllato oppure fermarti con una conclusione.

## Sintomo utente
Ho montato questo circuito per far lampeggiare alternativamente i due LED, ma sembrano restare entrambi accesi senza alternarsi. Quale potrebbe essere il problema?

## Vincoli obbligatori
- Rispondi con un solo oggetto JSON valido, senza Markdown o testo esterno.
- Non inventare nodi, componenti, valori o risultati.
- Usa soltanto queste primitive: add_resistor_between_nodes, add_voltage_source_between_nodes, change_component_value, change_source_value, close_switch, connect_nodes, drive_node_voltage, feed_nodes_from_source_node, set_initial_node_voltage.
- Ogni scenario deve essere self-contained e partire dalla base run.
- Puoi proporre al massimo 2 scenari indipendenti.
- Budget residuo: 5 run scenario.
- Se il budget e zero devi restituire decision=stop.
- Prima di una conclusione diagnostica devi eseguire almeno uno scenario controllato
  quando il budget e disponibile: la sola base run localizza un sospetto, ma non lo verifica.
- Con budget disponibile usa final_status="resolved" solo dopo uno scenario con
  diagnostic_outcome.status=resolved_candidate e stop_automation=true.
- Puoi invece fermarti con final_status="localized" dopo uno scenario diagnostico
  forte che verifica la causa ma non rappresenta una riparazione del circuito.
- Se il sintomo utente richiede esplicitamente di correggere, risolvere, attivare,
  disattivare o ripristinare un comportamento, prova una correzione distinta e
  sostenuta dagli artefatti finche ne esiste una non ancora verificata.
- Se una correzione e gia fallita e restano soltanto scenari duplicati oppure
  modifiche non sostenute dagli artefatti, fermati con `localized`,
  `partially_localized` o `inconclusive` e lascia `verified_correction` vuoto.
- Se uno scenario migliora il sintomo ma viola un vincolo richiesto (per esempio
  perde regolarita, spegne un componente da preservare o degrada l'uscita), trattalo
  come evidenza diagnostica e non come correzione finale.
- Non consumare altro budget per trasformare una localizzazione gia verificata in
  una correzione topologica inventata o non sostenuta dagli artefatti.
- Non usare resolved_candidate come prova automatica di soluzione definitiva.
- Distingui una soluzione da una semplice localizzazione della causa.
- Ogni scenario deve dichiarare analysis="op" oppure analysis="tran".
- Ogni scenario deve dichiarare intent="correction" oppure intent="diagnostic".
- Usa intent="correction" soltanto per una modifica che mira a migliorare o
  risolvere direttamente il sintomo utente.
- Se una modifica mira direttamente a correggere il sintomo, dichiarala subito
  con intent="correction": non eseguire prima la stessa modifica come test
  diagnostico per poi tentare di ripeterla.
- Usa intent="diagnostic" per isolare o confermare una causa, compresi i test
  che riducono intenzionalmente una risposta o disattivano un comportamento.
- Uno scenario diagnostic puo confermare un'ipotesi, ma non puo giustificare
  final_status="resolved" ne arrestare il ciclo come correzione verificata.
- Usa analysis="tran" per ampiezza, Vpp, guadagno, frequenza, forma d'onda e
  qualsiasi sintomo dinamico. Usa analysis="op" soltanto per il punto di lavoro DC.
- Con analysis="tran" puoi dichiarare la mappa opzionale `measure` per scegliere
  la misura di ogni grandezza: `tran_vpp` per una tensione letta da 08_tran.csv,
  `op` per tensioni, correnti o potenze lette dal punto di lavoro, `tran_abs_peak` per
  il picco assoluto di una corrente interna `@dNOME[id]` letta da 08_tran.csv.
- `tran_vpp` accetta sia `v(NODO)` rispetto a massa sia `v(NODO1,NODO2)` per
  carichi flottanti: nel secondo caso usa la differenza campione per campione.
- Se `measure` non e presente resta valido il comportamento standard: le tensioni
  sono confrontate sul Vpp, mentre correnti e potenze restano osservazioni OP.
- In uno scenario misto puoi usare una corrente come criterio expect soltanto
  dichiarandola esplicitamente: `measure: {"i(R...)":"op"}` per una corrente
  OP oppure `measure: {"@dled...[id]":"tran_abs_peak"}` per verificare che
  un LED/diodo si sia attivato almeno una volta durante la run TRAN.
- Un voltmetro VAC, un segnale AC o una tensione alternata devono essere verificati
  con analysis="tran" e `tran_vpp`: un valore DC non dimostra il funzionamento AC.
- Per sintomi di amplificazione o guadagno, ogni scenario con intent="correction" deve includere
  `gain: {"input":"v(NODO_IN)","output":"v(NODO_OUT)"}`; entrambe le
  tensioni devono essere presenti in compare e possono anche usare la forma
  differenziale `v(NODO1,NODO2)`. Valuta il guadagno come
  Vpp(output) / Vpp(input), senza confondere due nodi entrambi di uscita.
- Per verificare propagazione o attenuazione di un segnale, anche uno scenario
  diagnostico deve aggiungere `gain.min_ratio` con una soglia positiva motivata
  dall'obiettivo dello scenario. Non usare il solo `changed` per concludere che
  un segnale non nullo ma trascurabile arrivi utilmente all'uscita.
- Quando aggiungi una sorgente `SIN(...)` a un nodo o tra due nodi gia esistenti,
  ricava prima dalla base run la tensione di punto operativo dello stesso nodo o
  della stessa coppia. Se la differenza DC e significativa, conserva quel valore
  come primo parametro di `SIN` e sovrapponi soltanto l'ampiezza AC richiesta.
  Usa offset zero solo se il nodo/la coppia e gia circa a 0 V oppure se lo
  scenario deve esplicitamente cambiare il bias DC.
- Per un test di propagazione iniettato direttamente sulla base di un BJT, usa
  un vero piccolo segnale di pochi millivolt (normalmente 1-10 mV di picco,
  salvo evidenze contrarie) e conserva il bias DC misurato. Decine di millivolt
  sulla base possono portare il transistor in interdizione o saturazione e non
  isolano piu il percorso lineare del segnale.
- Non ripetere le stesse azioni elettriche di una run gia eseguita soltanto per
  aggiungere gain, measure, expect o una soglia: reinterpreta le misure esistenti.
  Dopo un trasferimento insufficiente, sposta il confine di isolamento a un nodo
  intermedio giustificato oppure testa una causa elettricamente distinta.
- Non inserire due `change_source_value` sullo stesso target nella stessa run:
  la seconda assegnazione sovrascrive la prima e non costituisce uno sweep.
  Usa scenari separati per punti operativi statici diversi, oppure una sola
  sorgente `PWL(...)`/`SIN(...)` quando vuoi davvero una variazione temporale.
- Se il trasferimento fallisce con una sorgente SIN provata a una sola ampiezza,
  prima di concludere un guasto strutturale mantieni lo stesso percorso e la
  stessa frequenza e prova un'ampiezza significativamente diversa. Se anche il
  nuovo livello fallisce e resta budget, continua lo sweep; fermati appena il
  trasferimento diventa sufficiente. Non ripetere lo stesso stimolo aggiungendo
  soltanto una forzatura su un nodo di alimentazione.
- Prima di attribuire un'uscita assoluta debole a un guasto, verifica se il
  circuito sta gia amplificando un ingresso molto piccolo.
- Per sintomi di distorsione, clipping, saturazione o segnale poco pulito,
  ogni scenario transitorio deve dichiarare quality="thd" e il blocco gain
  deve identificare ingresso e uscita.
- La pipeline calcola la THD sulle armoniche 2-5 nelle ultime tre oscillazioni
  complete della sorgente SIN. Una correzione e risolutiva soltanto se la THD
  diminuisce almeno del 20%, scende sotto il 10% e il guadagno fondamentale
  non viene annullato.
- Se la metrica THD non e disponibile o resta sopra soglia, considera lo
  scenario parziale e continua con un test diverso, per esempio sul bias.
- Ogni scenario deve avere una lista compare non vuota con grandezze osservabili.
- Per scenari con piu rami o uscite, includi in compare almeno una grandezza per ciascuno.
- Se il sintomo combina un obiettivo AC/VAC e lo stato di un LED o di una
  lampada, ogni scenario deve verificarli insieme: usa un test misto con
  `tran_vpp` sul segnale e una misura diretta `op` sul componente.
- Due scenari separati che attivano un solo target ciascuno non verificano il
  funzionamento simultaneo: prima di fermarti esegui una singola run self-contained
  con entrambi gli stimoli e con entrambi i criteri soddisfatti.
- In questo caso non usare l'inattivita intenzionale di uno dei due target come
  prova sufficiente: lo scenario deve applicare gli stimoli indipendenti adatti.
- Se l'obiettivo richiede di attivare o spegnere un componente, includi in compare
  almeno una misura diretta del componente, preferendo i(NOME_SPICE).
- Se l'obiettivo richiede di mantenere invariato un altro componente, includi in
  compare anche una sua misura diretta: le sole tensioni di nodo non ne verificano lo stato.
- Ricava NOME_SPICE dalla netlist 07_netlist.cir; non usare l'id Graph JSON dentro i(...) o p(...).
- Non richiedere i(Q...) per un transistor BJT: questa misura diretta non e
  disponibile nel confronto corrente. Usa la corrente di una resistenza sul
  collettore o sull'emettitore come misura osservabile del ramo.
- Richiedi p(NOME_SPICE) soltanto se la potenza dello stesso dispositivo e gia
  disponibile negli output ngspice forniti; non aggiungere misure ridondanti.
- Ogni scenario deve avere un oggetto expect non vuoto. Le chiavi devono essere
  grandezze presenti in compare e i valori ammessi sono: activated, deactivated,
  changed, unchanged, increased, decreased, magnitude_increased,
  magnitude_decreased, nonzero.
- `activated` significa esclusivamente passaggio da una grandezza inattiva o
  nulla nella base run a una grandezza attiva nello scenario. Prima di usarlo,
  controlla sempre la misura base della stessa quantita negli artefatti o nella
  cronologia: se e gia diversa da zero, anche se debole, impulsiva o irregolare,
  `activated` e semanticamente errato e non potra essere soddisfatto.
- Quando la quantita base e gia non nulla, usa `changed`, `magnitude_increased`,
  `magnitude_decreased` o `nonzero` secondo l'effetto realmente richiesto. Per
  lampeggio, periodicita e duty cycle, affida la verifica dello stato dinamico a
  `temporal_expect`; non usare `activated` come suo sostituto.
- Inserisci in expect soltanto i comportamenti indispensabili per verificare
  l'obiettivo o preservare componenti richiesti dall'utente. Le altre misure
  possono restare in compare come osservazioni senza aspettativa.
- Una variazione direzionale minima non dimostra una correzione: per fermare
  il ciclo serve almeno un miglioramento relativo del 10%, oppure una vera
  attivazione/disattivazione del comportamento richiesto.
- Usa expect per descrivere sia l'effetto cercato sia i vincoli da preservare,
  per esempio corrente gia presente del target `magnitude_increased` e corrente
  del componente protetto `unchanged`. Usa `activated` soltanto se gli artefatti
  mostrano che la corrente base del target e davvero nulla o inattiva.
- Usa unchanged soltanto se il sintomo utente chiede esplicitamente di mantenere
  o preservare un altro componente o comportamento; altrimenti ometti quel
  vincolo e lascia la grandezza soltanto in compare.
- Se ngspice segnala nodi flottanti o matrice singolare, non usare la tensione
  assoluta di quei nodi come vincolo unchanged: il riferimento comune puo traslare.
  Preferisci correnti dirette e variazioni strettamente legate all'obiettivo.
- In analisi .op un condensatore non fornisce un percorso conduttivo DC: non
  proporre come chiusura del circuito un cammino che termina soltanto su un condensatore.
- Per una run .tran usa le tracce disponibili e confronta almeno l'uscita o il ramo
  direttamente coinvolto nell'obiettivo, oltre agli eventuali nodi intermedi.
- Per sintomi di ricarica o carica batteria, non usare la sola corrente di una
  sorgente `V...` come prova della carica: il suo segno dipende dalla convenzione
  SPICE e dalla sua polarita. Una correzione deve usare `.tran` e misurare anche
  un componente del percorso di carica direttamente giustificato dalla netlist
  (per esempio `@dNOME[id]` del raddrizzatore con `tran_abs_peak`). La corrente
  della sorgente puo essere soltanto un'evidenza di supporto, con segno spiegato.
- Per obiettivi che chiedono lampeggio, periodicita, regolarita, duty cycle o durata
  di accensione, ogni scenario deve dichiarare `temporal_expect`.
  Questo blocco usa il profilo transitorio del componente nel viewer: `target`,
  `required_state` opzionale, `require_regular_period` opzionale,
  `min_duty_cycle` opzionale tra 0 e 1 e `min_relative_duty_increase` opzionale.
- Scegli soglie coerenti con il sintomo: per esempio un lampeggio chiaramente visibile
  puo richiedere stato `blinking`, periodicita regolare e un duty cycle minimo.
  Se un test aumenta il duty cycle ma perde la periodicita richiesta, non e risolutivo.
- Quando usi `set_initial_node_voltage` per rompere un equilibrio simmetrico,
  scegli una tensione iniziale fisicamente ammissibile ma chiaramente separata
  dal punto di lavoro del nodo mostrato dagli artefatti. Una variazione di pochi
  punti percentuali attorno allo stesso bias non e un test sufficiente; preferisci
  un riferimento gia documentato nel circuito, senza inventarne uno.
- Se il sintomo riguarda l'avvio di un circuito dinamico e il punto operativo DC
  mantiene artificialmente la simmetria, puoi aggiungere
  `skip_operating_point: true` a `set_initial_node_voltage`. In questo caso ngspice
  usa `.tran ... UIC`: la condizione deve introdurre una reale asimmetria iniziale,
  per esempio un valore non nullo su uno dei nodi simmetrici. Non usare questa
  opzione per mascherare errori di topologia, alimentazione o componenti.
  Se esistono due nodi di controllo simmetrici, inizializzali nello stesso
  scenario a due livelli distinti e fisicamente ammissibili; lasciare entrambi
  implicitamente allo stesso valore non rompe la simmetria.
  Un nodo interno di controllo non e un ingresso di alimentazione: se una base
  BJT ha un punto di lavoro sotto il rail, non inizializzarla al rail completo.
  Ricava livelli moderati dal bias misurato e dal ruolo del dispositivo (per
  esempio, con una base al silicio attorno a 0.8 V e alimentazione a 5 V, usa
  un livello basso su un ramo e circa 1-1.5 V sull'altro, non 5 V).
  Per due basi BJT simmetriche, il primo test di avvio deve usare sul ramo basso
  il riferimento di massa gia presente, normalmente 0 V, e sull'altro un livello
  moderato vicino o poco sopra il bias misurato. Non scegliere un valore basso
  intermedio arbitrario se la massa e gia il riferimento elettrico documentato.
- Se un test iniziale `.ic` produce un profilo `transient_pulse`, oppure rende
  dinamiche grandezze prima statiche senza ottenere ancora periodicita regolare,
  considera promettente l'ipotesi di startup. Prima di cambiare componenti prova
  una sola seconda coppia di condizioni iniziali, materialmente diversa ma
  fisicamente ammissibile, sempre dalla base run. Solo se anche quel test non
  produce il comportamento richiesto passa a ipotesi sui valori dei componenti.
- Se un LED o un altro target presenta gia qualunque impulso o corrente non nulla
  nella base run, non usare `activated`, neppure se il profilo base e classificato
  `transient_pulse`, debole o irregolare. Confronta la sua traccia transitoria,
  scegli un'aspettativa di variazione coerente e usa `temporal_expect` per lo
  stato dinamico richiesto.
  `temporal_expect.target` deve contenere un solo identificatore testuale, non
  una lista; se sono coinvolti piu LED, confronta le correnti di tutti.
- Un solo scenario negativo basato esclusivamente su condizioni iniziali non
  dimostra un errore di valori o topologia. In assenza di altre evidenze
  strutturali, concludi `inconclusive` oppure continua con un test distinto.
- Non dichiarare verified_correction se i confronti non misurano direttamente sia
  il componente target sia gli eventuali componenti che devono restare attivi.
- Se final_status="resolved", verified_correction deve descrivere la correzione
  realmente verificata da uno scenario con intent="correction".
- Preferisci modifiche minime su componenti, valori e collegamenti gia esistenti.
- Usa nuove sorgenti o nuovi rami resistivi solo quando le evidenze tecniche li giustificano.
- Non usare `drive_node_voltage` su un nodo gia vincolato a una sorgente attiva,
  direttamente o tramite uno switch/collegamento quasi ideale chiuso nello stesso
  scenario: produrrebbe generatori in conflitto e correnti prive di significato.
- Usa feed_nodes_from_source_node solo da un nodo che gli output mostrano gia alimentato.
- Usa connect_nodes per una ipotesi di continuita mancante senza attribuire a un nodo il ruolo di sorgente.
- I pin distinti dello stesso connector rappresentano reti funzionali separate finche
  gli artefatti non dimostrano una continuita prevista. Se alimentano rami diversi,
  verifica prima ciascun ramo con la sorgente appropriata e non collegarli per comodita.
- Un pin collegato soltanto a uno switch verso massa non diventa un ingresso di
  alimentazione senza un'evidenza esplicita nella node map, nella netlist o nelle label.
- Non proporre connect_nodes e feed_nodes_from_source_node sulla stessa relazione tra nodi nella stessa decisione.
- Considera add_resistor_between_nodes una ipotesi distinta: aggiunge un vero accoppiamento resistivo, non un filo quasi ideale.
- Non riproporre azioni gia presenti nella cronologia cambiando soltanto titolo,
  aspettative o un valore quasi identico: uno scenario duplicato non produce nuova evidenza.
- Non usare add_resistor_between_nodes con pochi milliohm per imitare connect_nodes.
  Usalo per un vero ramo resistivo plausibile, come bias, pull-up, pull-down o shunt.
- Dopo uno scenario rifiutato come duplicato scegli una relazione, un componente
  o una ipotesi fisica realmente diversa.

## Schema delle azioni consentite
- drive_node_voltage: type, target, value
- set_initial_node_voltage: type, target, value, skip_operating_point opzionale booleano (solo analysis=tran; condizione iniziale senza sorgente permanente; con `true` abilita `.tran ... UIC`)
- change_source_value: type, target, value
- change_component_value: type, target, value
- close_switch: type, target, resistance opzionale
- connect_nodes: type, from, to, resistance opzionale
- feed_nodes_from_source_node: type, source_node, target_nodes, resistance opzionale
- add_voltage_source_between_nodes: type, positive, negative, value
- add_resistor_between_nodes: type, from, to, value

## Formati ammessi
{"decision":"run_scenarios","reason":"...","scenarios":[{"title":"...","hypothesis":"...","intent":"correction","analysis":"tran","actions":[{"type":"change_component_value","target":"Rtarget","value":"10k"}],"compare":["v(NOUT)"],"expect":{"v(NOUT)":"magnitude_increased"},"temporal_expect":{"target":"Dled1","required_state":"blinking","require_regular_period":true,"min_duty_cycle":0.10}}]}

oppure

{"decision":"stop","reason":"...","final_status":"resolved|localized|partially_localized|topology_issue|inconclusive","final_answer":"Sintesi breve della conclusione.","final_cause":"Causa tecnica individuata, senza ripetizioni.","verified_correction":"Correzione verificata dagli scenari, oppure stringa vuota se non verificata."}

## Decisioni e risultati precedenti
```json
[]
```

## Evidenze tecniche correnti
## 03_node_map.json
```text
{
  "circuit_id": "c02",
  "source_format": "pipeline2.0_node_map",
  "nodes": [
    {
      "node_id": "N001",
      "kind": "normal",
      "terminals": [
        "battery2.1_negative",
        "npn_transistor18.1_E",
        "npn_transistor18.2_E"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N002",
      "kind": "normal",
      "terminals": [
        "battery2.1_positive",
        "led12.1_anode",
        "led12.2_anode",
        "resistor22.2_t1",
        "resistor22.3_t1"
      ],
      "terminal_count": 5
    },
    {
      "node_id": "N003",
      "kind": "normal",
      "terminals": [
        "led12.1_cathode",
        "resistor22.1_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N004",
      "kind": "normal",
      "terminals": [
        "led12.2_cathode",
        "resistor22.4_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N005",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.1_B",
        "polarized_capacitor20.2_negative",
        "resistor22.3_t2"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N006",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.1_C",
        "polarized_capacitor20.1_positive",
        "resistor22.1_t2"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N007",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.2_B",
        "polarized_capacitor20.1_negative",
        "resistor22.2_t2"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N008",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.2_C",
        "polarized_capacitor20.2_positive",
        "resistor22.4_t2"
      ],
      "terminal_count": 3
    }
  ],
  "terminal_to_node": {
    "battery2.1_negative": "N001",
    "battery2.1_positive": "N002",
    "led12.1_anode": "N002",
    "led12.1_cathode": "N003",
    "led12.2_anode": "N002",
    "led12.2_cathode": "N004",
    "npn_transistor18.1_B": "N005",
    "npn_transistor18.1_C": "N006",
    "npn_transistor18.1_E": "N001",
    "npn_transistor18.2_B": "N007",
    "npn_transistor18.2_C": "N008",
    "npn_transistor18.2_E": "N001",
    "polarized_capacitor20.1_negative": "N007",
    "polarized_capacitor20.1_positive": "N006",
    "polarized_capacitor20.2_negative": "N005",
    "polarized_capacitor20.2_positive": "N008",
    "resistor22.1_t1": "N003",
    "resistor22.1_t2": "N006",
    "resistor22.2_t1": "N002",
    "resistor22.2_t2": "N007",
    "resistor22.3_t1": "N002",
    "resistor22.3_t2": "N005",
    "resistor22.4_t1": "N004",
    "resistor22.4_t2": "N008"
  },
  "component_terminal_nodes": {
    "battery2.1": {
      "positive": "N002",
      "negative": "N001"
    },
    "led12.1": {
      "anode": "N002",
      "cathode": "N003"
    },
    "led12.2": {
      "anode": "N002",
      "cathode": "N004"
    },
    "npn_transistor18.1": {
      "B": "N005",
      "C": "N006",
      "E": "N001"
    },
    "npn_transistor18.2": {
      "B": "N007",
      "C": "N008",
      "E": "N001"
    },
    "polarized_capacitor20.1": {
      "positive": "N006",
      "negative": "N007"
    },
    "polarized_capacitor20.2": {
      "negative": "N005",
      "positive": "N008"
    },
    "resistor22.1": {
      "t1": "N003",
      "t2": "N006"
    },
    "resistor22.2": {
      "t1": "N002",
      "t2": "N007"
    },
    "resistor22.3": {
      "t1": "N002",
      "t2": "N005"
    },
    "resistor22.4": {
      "t1": "N004",
      "t2": "N008"
    }
  },
  "warnings": {
    "ground_groups_count": 0,
    "multiple_ground_groups_merged_as_node_0": false,
    "singleton_nodes": [],
    "original_warnings": {
      "unconnected_terminals": [],
      "unmatched_terminals": [],
      "suspicious_matches": []
    },
    "normalization_warnings": []
  },
  "stats": {
    "nodes_count": 8,
    "normal_nodes_count": 8,
    "ground_nodes_count": 0,
    "ground_groups_count": 0,
    "terminal_to_node_count": 24,
    "singleton_nodes_count": 0
  }
}

```

## 06_component_rules.json
```text
{
  "circuit_id": "c02",
  "source_format": "pipeline2.0_component_rules",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\data\\batchPipeline2.0\\batchChatAgentEvaluation\\values\\c02_values.yaml",
  "spice_classes_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_spice_classes.yaml",
  "supplies": {
    "VREF_BATTERY_NEGATIVE": {
      "status": "spice_ready",
      "spice_prefix": "V",
      "emit_as": "independent_voltage_source",
      "nodes": [
        "N001",
        "0"
      ],
      "parameters": {
        "terminal": "battery2.1_negative",
        "type": "dc",
        "value": 0,
        "unit": "V",
        "reference": 0,
        "source": "manual_reference_for_floating_battery_circuit",
        "label_text": "Negativo batteria: riferimento SPICE",
        "node": "N001"
      }
    }
  },
  "components": {
    "battery2.1": {
      "class_name": "Battery",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "V",
      "emit_as": "independent_voltage_source",
      "node_order": [
        "positive",
        "negative"
      ],
      "nodes": [
        "N002",
        "N001"
      ],
      "parameters": {
        "type": "dc",
        "value": 9,
        "unit": "V",
        "source": "manual_from_image_label",
        "label_text": "Batteria 9 V"
      }
    },
    "led12.1": {
      "class_name": "LED",
      "status": "spice_ready",
      "spice_support": "model",
      "spice_prefix": "D",
      "emit_as": "diode",
      "node_order": [
        "anode",
        "cathode"
      ],
      "nodes": [
        "N002",
        "N003"
      ],
      "parameters": {
        "model": "LED_RED_TYP",
        "source": "manual_testbench_assumption",
        "label_text": "L1 LED, colore non specificato",
        "viewer_override": {
          "label": "L1",
          "display_value": "LED"
        }
      }
    },
    "led12.2": {
      "class_name": "LED",
      "status": "spice_ready",
      "spice_support": "model",
      "spice_prefix": "D",
      "emit_as": "diode",
      "node_order": [
        "anode",
        "cathode"
      ],
      "nodes": [
        "N002",
        "N004"
      ],
      "parameters": {
        "model": "LED_RED_TYP",
        "source": "manual_testbench_assumption",
        "label_text": "L2 LED, colore non specificato",
        "viewer_override": {
          "label": "L2",
          "display_value": "LED"
        }
      }
    },
    "npn_transistor18.1": {
      "class_name": "NPN_Transistor",
      "status": "spice_ready",
      "spice_support": "model",
      "spice_prefix": "Q",
      "emit_as": "bjt_npn",
      "node_order": [
        "C",
        "B",
        "E"
      ],
      "nodes": [
        "N006",
        "N005",
        "N001"
      ],
      "parameters": {
        "model": "BC548_TYP",
        "source": "manual_from_image_label",
        "label_text": "Q1 BC548",
        "viewer_override": {
          "label": "Q1",
          "display_value": "BC548"
        }
      }
    },
    "npn_transistor18.2": {
      "class_name": "NPN_Transistor",
      "status": "spice_ready",
      "spice_support": "model",
      "spice_prefix": "Q",
      "emit_as": "bjt_npn",
      "node_order": [
        "C",
        "B",
        "E"
      ],
      "nodes": [
        "N008",
        "N007",
        "N001"
      ],
      "parameters": {
        "model": "BC548_TYP",
        "source": "manual_from_image_label",
        "label_text": "Q2 BC548",
        "viewer_override": {
          "label": "Q2",
          "display_value": "BC548"
        }
      }
    },
    "polarized_capacitor20.1": {
      "class_name": "Polarized_Capacitor",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "C",
      "emit_as": "capacitor",
      "node_order": [
        "positive",
        "negative"
      ],
      "nodes": [
        "N006",
        "N007"
      ],
      "parameters": {
        "value": 10,
        "unit": "uf",
        "source": "manual_testbench_assumption",
        "label_text": "C1 10 uF nominale (valore non visibile)"
      }
    },
    "polarized_capacitor20.2": {
      "class_name": "Polarized_Capacitor",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "C",
      "emit_as": "capacitor",
      "node_order": [
        "positive",
        "negative"
      ],
      "nodes": [
        "N008",
        "N005"
      ],
      "parameters": {
        "value": 10,
        "unit": "uf",
        "source": "manual_testbench_assumption",
        "label_text": "C2 10 uF nominale (valore non visibile)"
      }
    },
    "resistor22.1": {
      "class_name": "Resistor",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "R",
      "emit_as": "resistor",
      "node_order": [
        "t1",
        "t2"
      ],
      "nodes": [
        "N003",
        "N006"
      ],
      "parameters": {
        "value": 470,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R1 470 ohm"
      }
    },
    "resistor22.2": {
      "class_name": "Resistor",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "R",
      "emit_as": "resistor",
      "node_order": [
        "t1",
        "t2"
      ],
      "nodes": [
        "N002",
        "N007"
      ],
      "parameters": {
        "value": 47,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R2 47 kohm"
      }
    },
    "resistor22.3": {
      "class_name": "Resistor",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "R",
      "emit_as": "resistor",
      "node_order": [
        "t1",
        "t2"
      ],
      "nodes": [
        "N002",
        "N005"
      ],
      "parameters": {
        "value": 47,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R3 47 kohm"
      }
    },
    "resistor22.4": {
      "class_name": "Resistor",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "R",
      "emit_as": "resistor",
      "node_order": [
        "t1",
        "t2"
      ],
      "nodes": [
        "N004",
        "N008"
      ],
      "parameters": {
        "value": 470,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R4 470 ohm"
      }
    }
  },
  "simulation": {
    "analyses": [
      "op",
      "tran"
    ],
    "tran": {
      "step": "1ms",
      "stop": "3s"
    }
  },
  "stats": {
    "components_total": 11,
    "spice_ready_components": 11,
    "not_emitted_components": 0,
    "measurement_components": 0,
    "missing_components": 0,
    "unsupported_components": 0,
    "pin_aware_components": 0,
    "invalid_components": 0,
    "supplies_ready_count": 1
  }
}

```

## 07_netlist.cir
```text
* pipeline2.0 netlist
* circuit: c02

VVREF_BATTERY_NEGATIVE N001 0 DC 0
Vbattery2_1 N002 N001 DC 9
Dled12_1 N002 N003 LED_RED_TYP
Dled12_2 N002 N004 LED_RED_TYP
Qnpn_transistor18_1 N006 N005 N001 BC548_TYP
Qnpn_transistor18_2 N008 N007 N001 BC548_TYP
Cpolarized_capacitor20_1 N006 N007 10u
Cpolarized_capacitor20_2 N008 N005 10u
Rresistor22_1 N003 N006 470
Rresistor22_2 N002 N007 47k
Rresistor22_3 N002 N005 47k
Rresistor22_4 N004 N008 470

.model BC548_TYP NPN(IS=1e-14 BF=250 VAF=30 IKF=100m RB=100 RC=1 RE=0.2 CJE=12p VJE=0.7 MJE=0.33 CJC=4p VJC=0.5 MJC=0.33 TF=0.5n TR=50n)
.model LED_RED_TYP D(IS=1e-15 N=2 RS=10)

.op
.save all
.tran 1ms 3s

.control
set wr_singlescale
set wr_vecnames
save all @dled12_1[id] @dled12_2[id]
run
wrdata 08_tran.csv time v(N001) v(N002) v(N003) v(N004) v(N005) v(N006) v(N007) v(N008) @dled12_1[id] @dled12_2[id]
.endc
.end

```

## 07_spice_emit_report.json
```text
{
  "circuit_id": "c02",
  "source_format": "pipeline2.0_spice_emit_report",
  "emitted_elements": 12,
  "skipped_elements": 0,
  "skipped_components": [],
  "informational_skips": [],
  "measurement_points": [],
  "analyses": [
    "op",
    "tran"
  ],
  "transient_export": {
    "path": "08_tran.csv",
    "nodes": [
      "N001",
      "N002",
      "N003",
      "N004",
      "N005",
      "N006",
      "N007",
      "N008"
    ],
    "device_currents": [
      "@dled12_1[id]",
      "@dled12_2[id]"
    ]
  },
  "models": [
    "BC548_TYP",
    "LED_RED_TYP"
  ],
  "warnings": []
}

```

## 08_ngspice_stdout.txt
```text

Note: No compatibility mode selected!


Circuit: * pipeline2.0 netlist

Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

No. of Data Rows : 1

Initial Transient Solution
--------------------------

Node                                   Voltage
----                                   -------
n001                                         0
n002                                         9
n003                                   7.27838
n004                                   7.27838
n006                                  0.151939
n005                                  0.750666
n008                                  0.151939
n007                                  0.750666
vbattery2_1#branch                  -0.0306763
vvref_battery_negative#branch     -2.74216e-13

 Reference value :  2.65963e+00

No. of Data Rows : 4096
Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

No. of Data Rows : 1

Initial Transient Solution
--------------------------

Node                                   Voltage
----                                   -------
n001                                         0
n002                                         9
n003                                   7.27838
n004                                   7.27838
n006                                  0.151939
n005                                  0.750666
n008                                  0.151939
n007                                  0.750666
vbattery2_1#branch                  -0.0306763
vvref_battery_negative#branch     -2.74216e-13


No. of Data Rows : 4096
	Node                                  Voltage
	----                                  -------
	----	-------
	n007                             7.506657e-01
	n008                             1.519389e-01
	n005                             7.506657e-01
	n006                             1.519389e-01
	n004                             7.278381e+00
	n003                             7.278381e+00
	n002                             9.000000e+00
	n001                             0.000000e+00

	Source	Current
	------	-------

	@dled12_2[id]                    1.516264e-02
	@dled12_1[id]                    1.516264e-02
	vvref_battery_negative#branch    -2.74216e-13
	vbattery2_1#branch               -3.06763e-02

 BJT models (Bipolar Junction Transistor)
      model             bc548_typ

       type                   npn
       tnom                    27
         is                 1e-14
        ibe                     0
        ibc                     0
         bf                   250
         nf                     1
        vaf                    30
        ikf                   0.1
        ise                     0
         ne                   1.5
         br                     1
         nr                     1
        var                     0
        ikr                     0
        isc                     0
         nc                     2
         rb                   100
        irb                     0
        rbm                   100
         re                   0.2
         rc                     1
        cje               1.2e-11
        vje                   0.7
        mje                  0.33
         tf                 5e-10
        xtf                     0
        vtf                     0
        itf                     0
        ptf                     0
        cjc                 4e-12
        vjc                   0.5
        mjc                  0.33
       xcjc                     1
         tr                 5e-08
        cjs                     0
        vjs                  0.75
        mjs                     0
        xtb                     0
         eg                  1.11
        xti                     3
         fc                   0.5
         kf                     0
         af                     0
        iss                     0
         ns                     1
        rco                  0.01
         vo                    10
      gamma                 1e-11
        qco                     0
       tlev                     0
      tlevc                     0
       tbf1                     0
       tbf2                     0
       tbr1                     0
       tbr2                     0
      tikf1                     0
      tikf2                     0
      tikr1                     0
      tikr2                     0
      tirb1                     0
      tirb2                     0
       tnc1                     0
       tnc2                     0
       tne1                     0
       tne2                     0
       tnf1                     0
       tnf2                     0
       tnr1                     0
       tnr2                     0
       trb1                     0
       trb2                     0
       trc1                     0
       trc2                     0
       tre1                     0
       tre2                     0
       trm1                     0
       trm2                     0
      tvaf1                     0
      tvaf2                     0
      tvar1                     0
      tvar2                     0
        ctc                     0
        cte                     0
        cts                     0
       tvjc                     0
       tvje                     0
       tvjs                     0
      titf1                     0
      titf2                     0
       ttf1                     0
       ttf2                     0
       ttr1                     0
       ttr2                     0
      tmje1                     0
      tmje2                     0
      tmjc1                     0
      tmjc2                     0
      tmjs1                     0
      tmjs2                     0
       tns1                     0
       tns2                     0
        nkf                   0.5
       tis1                     0
       tis2                     0
      tise1                     0
      tise2                     0
      tisc1                     0
      tisc2                     0
      tiss1                     0
      tiss2                     0
   quasimod                     0
         vg                 1.206
         cn                  2.42
          d                  0.87
    vbe_max                 1e+99
    vbc_max                 1e+99
    vce_max                 1e+99
     pd_max                 1e+99
     ic_max                 1e+99
     ib_max                 1e+99
     te_max                 1e+99
       rth0                     0

 Capacitor models (Fixed capacitor)
      model                     C

        cap                     0
         cj                     0
       cjsw                     0
       defw                 1e-05
       defl                     0
     narrow                     0
      short                     0
        del                     0
        tc1                     0
        tc2                     0
         di                     0
      thick                     0
     bv_max                 1e+99

 Diode models (Junction Diode model)
      model           led_red_typ

      level                     1
         is                 1e-15
        jsw                     0
         rs                    10
        rsw                     0
        trs                     0
       trs2                     0
          n                     2
         ns                     1
         tt                     0
       ttt1                     0
       ttt2                     0
        cjo                     0
         vj                     1
          m                   0.5
        tm1                     0
        tm2                     0
        cjp                     0
        php                     1
       mjsw                  0.33
        ikf                     0
        ikr                     0
        ikp                     0
        nbv                     2
       area                     1
         pj                     0
       tlev                     0
      tlevc                     0
         eg                  1.11
       gap1              0.000702
       gap2                  1108
        xti                     3
        cta                     0
        ctp                     0
        tpb                     0
       tphp                     0
       jtun                     0
     jtunsw                     0
       ntun                    30
     xtitun                     3
        keg                     1
         kf                     0
         af                     1
         fc                   0.5
        fcs                   0.5
         bv                     0
        ibv                 0.001
        tcv                     0
        isr                 1e-14
         nr                     2
         vp                     0
     fv_max                 1e+99
     bv_max                 1e+99
     id_max                 1e+99
     te_max                 1e+99
     pd_max                 1e+99
       rth0                     0
       cth0                 1e-05
         lm                     0
         lp                     0
         wm                     0
         wp                     0
        xom                 10000
        xoi                 10000
         xm                     0
         xp                     0
         xw                     0

 Resistor models (Simple linear resistor)
      model                     R

        rsh                     0
     narrow                     0
      short                     0
        tc1                     0
        tc2                     0
        tce                     0
       defw                 1e-05
          l                 1e-05
         kf                     0
         af                     0
          r                     0
     bv_max                 1e+99
         lf                     1
         wf                     1
         ef                     1

 BJT: Bipolar Junction Transistor
     device   qnpn_transistor18_2   qnpn_transistor18_1
      model             bc548_typ             bc548_typ
         ic             0.0156536          -3.69626e-05
         ib             0.0112939           3.35936e-05
         ie            -0.0269475           3.36906e-06
        vbe              0.755738              -7.06324
        vbc              0.717297              -9.18109
         gm               0.82982           2.25912e-22
        gpi            0.00757202           6.27605e-08
        gmu              0.428142           1.74068e-08
         gx                  0.01                  0.01
         go              0.308085           1.40251e-22
        cpi           5.57675e-10           5.42437e-12
        cmu           2.14028e-08           1.50441e-12
        cbx                     0                     0
       csub                     0                     0

 Capacitor: Fixed capacitor
     device cpolarized_capacitor2 cpolarized_capacitor2
      model                     C                     C
capacitance                 1e-05                 1e-05
      dtemp                     0                     0
     bv_max                 1e+99                 1e+99
          i          -0.000308106             0.0111376
          p           -0.00219352            0.00253711

 Diode: Junction Diode model
     device              dled12_2              dled12_1
      model           led_red_typ           led_red_typ
    thermal                     0                     0
         vd               1.57064               1.55389
         id             0.0153539              0.011106
         gd              0.296809              0.214691
         cd                     0                     0

 Resistor: Simple linear resistor
     device         rresistor22_4         rresistor22_3         rresistor22_2
      model                     R                     R                     R
 resistance                   470                 47000                 47000
         ac                   470                 47000                 47000
      dtemp                     0                     0                     0
     bv_max                 1e+99                 1e+99                 1e+99
      noisy                     1                     1                     1
          i             0.0153539             0.0003417           0.000151276
          p              0.110799            0.00548766            0.00107557

 Resistor: Simple linear resistor
     device         rresistor22_1
      model                     R
 resistance                   470
         ac                   470
      dtemp                     0
     bv_max                 1e+99
      noisy                     1
          i             0.0111006
          p             0.0579153

 Vsource: Independent voltage source
     device           vbattery2_1 vvref_battery_negativ
         dc                     9                     0
      acmag                     0                     0
      pulse         -         -
        sin         -         -
        exp         -         -
        pwl         -         -
       sffm         -         -
         am         -         -
    trnoise         -         -
   trrandom         -         -
    portnum                     0                     0
         z0                     0                     0
        pwr                     0                     0
       freq                     0                     0
      phase                     0                     0
          i            -0.0269475          -2.16168e-12
          p             -0.242527                    -0


Total analysis time (seconds) = 0.127984

Total elapsed time (seconds) = 0.341 

Total DRAM available = 32239.535 MB.
DRAM currently available = 16149.109 MB.
Maximum ngspice program size =   16.637 MB.
Current ngspice program size =   16.637 MB.


```

## 08_ngspice_stderr.txt
```text

```

## 10_diagnostic_context.json
```text
{
  "source_format": "pipeline2.0_diagnostic_context_manifest",
  "batch_name": "batchChatAgentEvaluation",
  "experiment_name": "chat_agent_evaluation",
  "circuit_id": "c02",
  "user_problem": "Ho montato questo circuito per far lampeggiare alternativamente i due LED, ma sembrano restare entrambi accesi senza alternarsi. Quale potrebbe essere il problema?",
  "pipeline2_output_dir": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\c02",
  "summary": {
    "spice_status": "success",
    "spice_exit_code": 0,
    "spice_message": "ngspice completed successfully.",
    "emitted_elements": 12,
    "skipped_elements": 0,
    "emit_warnings_count": 0,
    "skipped_components_count": 0,
    "node_count": 8,
    "ground_groups_count": 0,
    "singleton_nodes_count": 0,
    "bound_components": 11,
    "missing_components": 0,
    "unsupported_components": 0,
    "spice_ready_components": 11,
    "rules_missing_components": 0,
    "has_tran_csv": true,
    "has_tran_plot": true,
    "led_profiles": {
      "Dled12_1": {
        "state": "blinking",
        "regular_period": true,
        "frequency_hz": 1.6682002709791153,
        "duty_cycle": 0.51736989343253,
        "on_fraction": 0.56591796875,
        "pulse_count": 6,
        "voltage_min": 1.0354889700000003,
        "voltage_max": 1.7242087499999998,
        "anode_node": "N002",
        "cathode_node": "N003"
      },
      "Dled12_2": {
        "state": "blinking",
        "regular_period": true,
        "frequency_hz": 1.6683042880583607,
        "duty_cycle": 0.5169728732137875,
        "on_fraction": 0.53076171875,
        "pulse_count": 7,
        "voltage_min": 1.0810698500000004,
        "voltage_max": 1.7242138599999999,
        "anode_node": "N002",
        "cathode_node": "N004"
      }
    }
  },
  "artifacts": {
    "graph": {
      "step": "01",
      "available": true,
      "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\c02\\01_graph.json",
      "role": "Graph JSON copied from Pipeline 1.0."
    },
    "normalized_circuit": {
      "step": "02",
      "available": true,
      "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\c02\\02_normalized_circuit.json",
      "role": "Normalized circuit representation used by Pipeline 2.0."
    },
    "node_map": {
      "step": "03",
      "available": true,
      "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\c02\\03_node_map.json",
      "role": "Maps component terminals to SPICE node names."
    },
    "values_bound": {
      "step": "04",
      "available": true,
      "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\c02\\04_values_bound.json",
      "role": "Values and labels bound to graph components."
    },
    "component_rules": {
      "step": "06",
      "available": true,
      "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\c02\\06_component_rules.json",
      "role": "SPICE conversion rules for each component."
    },
    "netlist": {
      "step": "07",
      "available": true,
      "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\c02\\07_netlist.cir",
      "role": "Generated SPICE netlist."
    },
    "spice_emit_report": {
      "step": "07",
      "available": true,
      "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\c02\\07_spice_emit_report.json",
      "role": "Report of emitted, skipped and warning components."
    },
    "spice_run": {
      "step": "08",
      "available": true,
      "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\c02\\08_spice_run.json",
      "role": "Structured ngspice execution report."
    },
    "ngspice_stdout": {
      "step": "08",
      "available": true,
      "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\c02\\08_ngspice_stdout.txt",
      "role": "Raw ngspice stdout log."
    },
    "ngspice_stderr": {
      "step": "08",
      "available": true,
      "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\c02\\08_ngspice_stderr.txt",
      "role": "Raw ngspice stderr log."
    },
    "tran_csv": {
      "step": "08",
      "available": true,
      "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\c02\\08_tran.csv",
      "role": "Clean transient CSV, when .tran data is available."
    },
    "tran_plot_png": {
      "step": "08",
      "available": true,
      "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\c02\\08_tran_plot.png",
      "role": "Transient plot PNG, when generated."
    },
    "tran_plot_svg": {
      "step": "08",
      "available": false,
      "path": null,
      "role": "Transient plot SVG fallback, when generated."
    }
  },
  "executed_scenarios": [],
  "scenario_outcome_summary": {
    "available": false,
    "best_scenario_id": null,
    "best_outcome_status": null,
    "best_stop_automation": null,
    "ranking_status": "no_verified_best",
    "interpretation_rule": "If a user asks which scenario resolves the problem, prefer the scenario with outcome_status='resolved_candidate' and stop_automation=true. Partially resolved scenarios without verified expectations are supporting diagnostics and must not be ranked only by changed_count.",
    "scenarios": []
  },
  "scenario_budget": {
    "max_executable_scenarios": 5,
    "executed_scenarios_count": 0,
    "remaining_executable_scenarios": 5,
    "budget_exhausted": false,
    "last_scenario_available": false,
    "policy": "At most 5 scenarios can be executed for the same circuit. When only one scenario remains, the agent should propose a single final scenario. When no scenario remains, the agent must stop proposing new scenarios and provide a final diagnostic conclusion."
  },
  "image_access": {
    "included_by_default": false,
    "can_be_requested": true,
    "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\input\\images\\c02.jpg",
    "policy": "Only request the image if structured outputs suggest that the Graph JSON may be incomplete or wrong."
  },
  "agent_mode": "graph_grounded_readonly",
  "agent_rules": [
    "Treat this file as a manifest, not as the full diagnostic evidence.",
    "Load the referenced artifacts needed for the answer.",
    "Use graph, node map, component rules, netlist, stdout and stderr as evidence.",
    "If executed_scenarios are available, use them as evidence for questions about scenario outcomes.",
    "Do not invent values, connections, models or simulation results.",
    "Do not use the image unless image_access is explicitly requested.",
    "If Graph JSON inconsistency is suspected, explain which structured outputs suggest it.",
    "In read-only mode, do not modify netlists and do not execute scenarios.",
    "Never exceed 5 executed scenarios for the same circuit.",
    "When the scenario budget is exhausted, stop proposing new scenarios and provide a final diagnostic conclusion."
  ]
}

```
