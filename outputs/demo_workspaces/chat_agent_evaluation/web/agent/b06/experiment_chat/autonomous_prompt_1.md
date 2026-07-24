# Pipeline 2.0 - agente diagnostico autonomo controllato

Sei il controller diagnostico di una pipeline Graph JSON -> SPICE/ngspice.
Devi scegliere il prossimo test controllato oppure fermarti con una conclusione.

## Sintomo utente
La radio si accende, ma dall’altoparlante non si sente nulla. Quale potrebbe essere il problema?

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
  "circuit_id": "b06",
  "source_format": "pipeline2.0_node_map",
  "nodes": [
    {
      "node_id": "0",
      "kind": "ground",
      "terminals": [
        "battery2.1_negative",
        "breaker3.1_t2",
        "gnd9.1_t1",
        "inductor10.1_t2",
        "npn_transistor18.1_E",
        "operational_amplifier19.1_aux2",
        "operational_amplifier19.1_in2",
        "polarized_capacitor20.1_negative",
        "polarized_capacitor20.2_negative",
        "polarized_capacitor20.6_negative",
        "resistor22.3_t2"
      ],
      "terminal_count": 11,
      "source_groups": [
        [
          "battery2.1_negative",
          "breaker3.1_t2",
          "gnd9.1_t1",
          "inductor10.1_t2",
          "npn_transistor18.1_E",
          "operational_amplifier19.1_aux2",
          "operational_amplifier19.1_in2",
          "polarized_capacitor20.1_negative",
          "polarized_capacitor20.2_negative",
          "polarized_capacitor20.6_negative",
          "resistor22.3_t2"
        ]
      ]
    },
    {
      "node_id": "N001",
      "kind": "normal",
      "terminals": [
        "antenna1.1_t1",
        "diode7.1_anode",
        "inductor10.1_t1",
        "polarized_capacitor20.1_positive"
      ],
      "terminal_count": 4
    },
    {
      "node_id": "N002",
      "kind": "normal",
      "terminals": [
        "battery2.1_positive",
        "switch25.1_t2"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N003",
      "kind": "normal",
      "terminals": [
        "breaker3.1_t1",
        "polarized_capacitor20.5_negative"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N004",
      "kind": "normal",
      "terminals": [
        "diode7.1_cathode",
        "polarized_capacitor20.2_positive",
        "polarized_capacitor20.3_positive"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N005",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.1_B",
        "polarized_capacitor20.3_negative",
        "resistor22.1_t1"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N006",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.1_C",
        "polarized_capacitor20.4_positive",
        "resistor22.1_t2",
        "resistor22.2_t2"
      ],
      "terminal_count": 4
    },
    {
      "node_id": "N007",
      "kind": "normal",
      "terminals": [
        "operational_amplifier19.1_aux1",
        "polarized_capacitor20.6_positive",
        "resistor22.2_t1",
        "switch25.1_t1"
      ],
      "terminal_count": 4
    },
    {
      "node_id": "N008",
      "kind": "normal",
      "terminals": [
        "operational_amplifier19.1_in1"
      ],
      "terminal_count": 1
    },
    {
      "node_id": "N009",
      "kind": "normal",
      "terminals": [
        "operational_amplifier19.1_out",
        "polarized_capacitor20.5_positive"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N010",
      "kind": "normal",
      "terminals": [
        "polarized_capacitor20.4_negative",
        "resistor22.3_t1"
      ],
      "terminal_count": 2
    }
  ],
  "terminal_to_node": {
    "antenna1.1_t1": "N001",
    "battery2.1_negative": "0",
    "battery2.1_positive": "N002",
    "breaker3.1_t1": "N003",
    "breaker3.1_t2": "0",
    "diode7.1_anode": "N001",
    "diode7.1_cathode": "N004",
    "gnd9.1_t1": "0",
    "inductor10.1_t1": "N001",
    "inductor10.1_t2": "0",
    "npn_transistor18.1_B": "N005",
    "npn_transistor18.1_C": "N006",
    "npn_transistor18.1_E": "0",
    "operational_amplifier19.1_aux1": "N007",
    "operational_amplifier19.1_aux2": "0",
    "operational_amplifier19.1_in1": "N008",
    "operational_amplifier19.1_in2": "0",
    "operational_amplifier19.1_out": "N009",
    "polarized_capacitor20.1_negative": "0",
    "polarized_capacitor20.1_positive": "N001",
    "polarized_capacitor20.2_negative": "0",
    "polarized_capacitor20.2_positive": "N004",
    "polarized_capacitor20.3_negative": "N005",
    "polarized_capacitor20.3_positive": "N004",
    "polarized_capacitor20.4_negative": "N010",
    "polarized_capacitor20.4_positive": "N006",
    "polarized_capacitor20.5_negative": "N003",
    "polarized_capacitor20.5_positive": "N009",
    "polarized_capacitor20.6_negative": "0",
    "polarized_capacitor20.6_positive": "N007",
    "resistor22.1_t1": "N005",
    "resistor22.1_t2": "N006",
    "resistor22.2_t1": "N007",
    "resistor22.2_t2": "N006",
    "resistor22.3_t1": "N010",
    "resistor22.3_t2": "0",
    "switch25.1_t1": "N007",
    "switch25.1_t2": "N002"
  },
  "component_terminal_nodes": {
    "antenna1.1": {
      "t1": "N001"
    },
    "battery2.1": {
      "positive": "N002",
      "negative": "0"
    },
    "breaker3.1": {
      "t1": "N003",
      "t2": "0"
    },
    "diode7.1": {
      "anode": "N001",
      "cathode": "N004"
    },
    "gnd9.1": {
      "t1": "0"
    },
    "inductor10.1": {
      "t1": "N001",
      "t2": "0"
    },
    "npn_transistor18.1": {
      "B": "N005",
      "C": "N006",
      "E": "0"
    },
    "operational_amplifier19.1": {
      "in1": "N008",
      "in2": "0",
      "out": "N009",
      "aux1": "N007",
      "aux2": "0"
    },
    "polarized_capacitor20.1": {
      "positive": "N001",
      "negative": "0"
    },
    "polarized_capacitor20.2": {
      "positive": "N004",
      "negative": "0"
    },
    "polarized_capacitor20.3": {
      "positive": "N004",
      "negative": "N005"
    },
    "polarized_capacitor20.4": {
      "positive": "N006",
      "negative": "N010"
    },
    "polarized_capacitor20.5": {
      "positive": "N009",
      "negative": "N003"
    },
    "polarized_capacitor20.6": {
      "positive": "N007",
      "negative": "0"
    },
    "resistor22.1": {
      "t1": "N005",
      "t2": "N006"
    },
    "resistor22.2": {
      "t1": "N007",
      "t2": "N006"
    },
    "resistor22.3": {
      "t1": "N010",
      "t2": "0"
    },
    "switch25.1": {
      "t1": "N007",
      "t2": "N002"
    }
  },
  "warnings": {
    "ground_groups_count": 1,
    "multiple_ground_groups_merged_as_node_0": false,
    "singleton_nodes": [
      "N008"
    ],
    "original_warnings": {
      "unconnected_terminals": [
        "operational_amplifier19.1_in1"
      ],
      "unmatched_terminals": [],
      "suspicious_matches": []
    },
    "normalization_warnings": []
  },
  "stats": {
    "nodes_count": 11,
    "normal_nodes_count": 10,
    "ground_nodes_count": 1,
    "ground_groups_count": 1,
    "terminal_to_node_count": 38,
    "singleton_nodes_count": 1
  }
}

```

## 06_component_rules.json
```text
{
  "circuit_id": "b06",
  "source_format": "pipeline2.0_component_rules",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\data\\batchPipeline2.0\\batchChatAgentEvaluation\\values\\b06_values.yaml",
  "spice_classes_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_spice_classes.yaml",
  "supplies": {},
  "components": {
    "antenna1.1": {
      "class_name": "Antenna",
      "status": "unsupported_for_now",
      "spice_support": "unsupported_for_now",
      "reason": "Conversion deferred to a later step."
    },
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
        "0"
      ],
      "parameters": {
        "type": "dc",
        "value": 9,
        "unit": "V",
        "source": "manual_from_image_label",
        "label_text": "B1 9 V"
      }
    },
    "breaker3.1": {
      "class_name": "Breaker",
      "status": "spice_ready",
      "spice_support": "equivalent",
      "spice_prefix": "R",
      "emit_as": "resistive_load",
      "node_order": [
        "t1",
        "t2"
      ],
      "nodes": [
        "N003",
        "0"
      ],
      "parameters": {
        "spice_override": {
          "emit_as": "resistive_load",
          "equivalent_resistance": 8,
          "resistance_unit": "ohm",
          "node_order": [
            "t1",
            "t2"
          ],
          "semantic_role": "speaker_equivalent"
        },
        "source": "manual_interpretation_Z1_speaker_equivalent",
        "label_text": "Z1 altoparlante equivalente: 8 ohm",
        "viewer_override": {
          "visual_class": "speaker",
          "label": "Z1 8 ohm",
          "tooltip": "Z1 altoparlante; carico SPICE equivalente da 8 ohm"
        },
        "equivalent_resistance": 8,
        "resistance_unit": "ohm"
      },
      "reason": "Explicit YAML override emitted as an equivalent resistive load."
    },
    "diode7.1": {
      "class_name": "Diode",
      "status": "spice_ready",
      "spice_support": "model",
      "spice_prefix": "D",
      "emit_as": "diode",
      "node_order": [
        "anode",
        "cathode"
      ],
      "nodes": [
        "N001",
        "N004"
      ],
      "parameters": {
        "model": "D_GENERIC",
        "source": "manual_image_part_number_with_generic_spice_detector_model",
        "label_text": "D1 AA119; modello SPICE rivelatore generico",
        "viewer_override": {
          "label": "D1",
          "display_value": "AA119",
          "tooltip": "D1 AA119; simulato con modello rivelatore generico"
        }
      }
    },
    "gnd9.1": {
      "class_name": "GND",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "GND terminals are already mapped to SPICE node 0."
    },
    "inductor10.1": {
      "class_name": "Inductor",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "L",
      "emit_as": "inductor",
      "node_order": [
        "t1",
        "t2"
      ],
      "nodes": [
        "N001",
        "0"
      ],
      "parameters": {
        "value": 0.00022,
        "unit": "H",
        "source": "manual_assumption_inductor_label_ambiguous_220uH",
        "label_text": "L1 assunta: 220 uH",
        "viewer_override": {
          "label": "L1",
          "display_value": "220 uH",
          "tooltip": "L1: valore assunto 220 uH dalla label ambigua dell'immagine"
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
        "0"
      ],
      "parameters": {
        "model": "2N3904",
        "source": "manual_from_image_label",
        "label_text": "Q1 2N3904",
        "viewer_override": {
          "label": "Q1",
          "display_value": "2N3904"
        }
      }
    },
    "operational_amplifier19.1": {
      "class_name": "Operational_Amplifier",
      "status": "spice_ready",
      "spice_support": "subcircuit",
      "spice_prefix": "X",
      "emit_as": "subcircuit",
      "node_order": [
        "INP",
        "INM",
        "VCC",
        "VEE",
        "OUT"
      ],
      "nodes": [
        "N010",
        "0",
        "N007",
        "0",
        "N009"
      ],
      "parameters": {
        "model": "LM386_SIMPLE",
        "source": "manual_image_validation_LM386_pin_mapping",
        "label_text": "IC1 LM386; equivalente SPICE semplice",
        "viewer_override": {
          "visual_class": "operational_amplifier",
          "label": "LM386",
          "tooltip": "IC1 LM386; equivalente SPICE lineare semplice"
        },
        "spice_override": {
          "emit_as": "subcircuit",
          "pin_order": [
            "INP",
            "INM",
            "VCC",
            "VEE",
            "OUT"
          ],
          "node_refs": {
            "INP": "operational_amplifier19.1_in1",
            "INM": "operational_amplifier19.1_in2",
            "VCC": "operational_amplifier19.1_aux1",
            "VEE": "operational_amplifier19.1_aux2",
            "OUT": "operational_amplifier19.1_out"
          },
          "resolved_node_refs": {
            "INP": "N010",
            "INM": "0",
            "VCC": "N007",
            "VEE": "0",
            "OUT": "N009"
          }
        }
      },
      "reason": "Explicit YAML override emitted as a SPICE subcircuit."
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
        "N001",
        "0"
      ],
      "parameters": {
        "value": 365,
        "unit": "pf",
        "source": "manual_from_image_label",
        "label_text": "C1 variabile 365 pF",
        "viewer_override": {
          "visual_class": "variable_capacitor",
          "label": "C1",
          "display_value": "365 pF"
        }
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
        "N004",
        "0"
      ],
      "parameters": {
        "value": 100,
        "unit": "nf",
        "source": "manual_from_image_label",
        "label_text": "C2 100 nF",
        "viewer_override": {
          "visual_class": "capacitor",
          "label": "C2",
          "display_value": "100 nF"
        }
      }
    },
    "polarized_capacitor20.3": {
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
        "N004",
        "N005"
      ],
      "parameters": {
        "value": 100,
        "unit": "nf",
        "source": "manual_from_image_label",
        "label_text": "C3 100 nF",
        "viewer_override": {
          "visual_class": "capacitor",
          "label": "C3",
          "display_value": "100 nF"
        }
      }
    },
    "polarized_capacitor20.4": {
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
        "N010"
      ],
      "parameters": {
        "value": 100,
        "unit": "nf",
        "source": "manual_from_image_label",
        "label_text": "C4 100 nF",
        "viewer_override": {
          "visual_class": "capacitor",
          "label": "C4",
          "display_value": "100 nF"
        }
      }
    },
    "polarized_capacitor20.5": {
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
        "N009",
        "N003"
      ],
      "parameters": {
        "value": 220,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C5 220 uF"
      }
    },
    "polarized_capacitor20.6": {
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
        "N007",
        "0"
      ],
      "parameters": {
        "value": 100,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C6 100 uF"
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
        "N005",
        "N006"
      ],
      "parameters": {
        "value": 100,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R1 100 kohm"
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
        "N007",
        "N006"
      ],
      "parameters": {
        "value": 10,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R2 10 kohm"
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
        "N010",
        "0"
      ],
      "parameters": {
        "value": 10,
        "unit": "kohm",
        "source": "manual_from_image_label_fixed_wiper_at_maximum",
        "label_text": "R3 potenziometro 10 kohm; base run al massimo volume",
        "viewer_override": {
          "label": "R3",
          "display_value": "10 kohm",
          "label_mode": "tooltip",
          "tooltip": "R3 potenziometro 10 kohm; cursore base run al massimo volume"
        }
      }
    },
    "switch25.1": {
      "class_name": "Switch",
      "status": "spice_ready",
      "spice_support": "simplified",
      "spice_prefix": null,
      "emit_as": null,
      "node_order": [
        "t1",
        "t2"
      ],
      "nodes": [
        "N007",
        "N002"
      ],
      "parameters": {
        "state": "closed",
        "state_source": "graph_json_state",
        "state_confidence": 0.95,
        "source": "graph_json_state_validated_from_image",
        "label_text": "S1 chiuso",
        "viewer_override": {
          "label": "S1",
          "label_mode": "reference_only",
          "tooltip": "S1 chiuso nella base run"
        }
      },
      "strategy": "short_circuit"
    }
  },
  "simulation": {
    "analyses": [
      "op",
      "tran"
    ],
    "tran": {
      "step": "1us",
      "stop": "5ms"
    }
  },
  "stats": {
    "components_total": 18,
    "spice_ready_components": 16,
    "not_emitted_components": 1,
    "measurement_components": 0,
    "missing_components": 0,
    "unsupported_components": 1,
    "pin_aware_components": 0,
    "invalid_components": 0,
    "supplies_ready_count": 0
  }
}

```

## 07_netlist.cir
```text
* pipeline2.0 netlist
* circuit: b06

Vbattery2_1 N002 0 DC 9
Rbreaker3_1 N003 0 8
Ddiode7_1 N001 N004 D_GENERIC
Linductor10_1 N001 0 0.00022
Qnpn_transistor18_1 N006 N005 0 2N3904
Xoperational_amplifier19_1 N010 0 N007 0 N009 LM386_SIMPLE
Cpolarized_capacitor20_1 N001 0 365p
Cpolarized_capacitor20_2 N004 0 100n
Cpolarized_capacitor20_3 N004 N005 100n
Cpolarized_capacitor20_4 N006 N010 100n
Cpolarized_capacitor20_5 N009 N003 220u
Cpolarized_capacitor20_6 N007 0 100u
Rresistor22_1 N005 N006 100k
Rresistor22_2 N007 N006 10k
Rresistor22_3 N010 0 10k
Rswitch25_1 N007 N002 1m

.model 2N3904 NPN(IS=6.734f BF=416.4 VAF=74.03 IKF=66.78m ISE=6.734f NE=1.259 BR=0.7371 VAR=12.11 IKR=0.0 ISC=0.0 NC=2 RB=10 RC=1 RE=0.1 CJE=4.493p VJE=0.75 MJE=0.2593 CJC=3.638p VJC=0.75 MJC=0.3085 TF=301.2p TR=239.5n)
.model D_GENERIC D
.subckt LM386_SIMPLE INP INM VCC VEE OUT
RIN INP INM 50k
EAMP NAMP VEE INP INM 20
ROUT NAMP OUT 5
RBLEED VCC VEE 100k
.ends LM386_SIMPLE

.op
.save all
.tran 1us 5ms

.control
set wr_singlescale
set wr_vecnames
save all @ddiode7_1[id]
run
wrdata 08_tran.csv time v(N001) v(N002) v(N003) v(N004) v(N005) v(N006) v(N007) v(N009) v(N010) @ddiode7_1[id]
.endc
.end

```

## 07_spice_emit_report.json
```text
{
  "circuit_id": "b06",
  "source_format": "pipeline2.0_spice_emit_report",
  "emitted_elements": 16,
  "skipped_elements": 2,
  "skipped_components": [
    "antenna1.1",
    "gnd9.1"
  ],
  "informational_skips": [
    "gnd9.1: structural component not emitted"
  ],
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
      "N009",
      "N010"
    ],
    "device_currents": [
      "@ddiode7_1[id]"
    ]
  },
  "models": [
    "2N3904",
    "D_GENERIC",
    "LM386_SIMPLE"
  ],
  "warnings": [
    "antenna1.1: class not yet supported by SPICE emit"
  ]
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
n002                                         9
n003                                         0
n001                                         0
n004                              -1.22429e-16
n006                                   1.28179
n005                                  0.660106
n010                                         0
xoperational_amplifier19_1.namp               0
n009                                         0
n007                                         9
linductor10_1#branch              -2.24208e-44
e.xoperational_amplifier19_1.eamp#branch               0
vbattery2_1#branch                -0.000861821


No. of Data Rows : 5008
Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

No. of Data Rows : 1

Initial Transient Solution
--------------------------

Node                                   Voltage
----                                   -------
n002                                         9
n003                                         0
n001                                         0
n004                              -1.22429e-16
n006                                   1.28179
n005                                  0.660106
n010                                         0
xoperational_amplifier19_1.namp               0
n009                                         0
n007                                         9
linductor10_1#branch              -2.24208e-44
e.xoperational_amplifier19_1.eamp#branch               0
vbattery2_1#branch                -0.000861821


No. of Data Rows : 5008
	Node                                  Voltage
	----                                  -------
	----	-------
	n007                             8.999999e+00
	n009                             0.000000e+00
	xoperational_amplifier19_1.namp   0.000000e+00
	n010                             0.000000e+00
	n005                             6.601064e-01
	n006                             1.281789e+00
	n004                             -1.22429e-16
	n001                             0.000000e+00
	n003                             0.000000e+00
	n002                             9.000000e+00

	Source	Current
	------	-------

	@ddiode7_1[id]                   1.690583e-28
	vbattery2_1#branch               -8.61821e-04
	e.xoperational_amplifier19_1.eamp#branch   0.000000e+00
	linductor10_1#branch             -2.24208e-44

 BJT models (Bipolar Junction Transistor)
      model                2n3904

       type                   npn
       tnom                    27
         is             6.734e-15
        ibe                     0
        ibc                     0
         bf                 416.4
         nf                     1
        vaf                 74.03
        ikf               0.06678
        ise             6.734e-15
         ne                 1.259
         br                0.7371
         nr                     1
        var                 12.11
        ikr                     0
        isc                     0
         nc                     2
         rb                    10
        irb                     0
        rbm                    10
         re                   0.1
         rc                     1
        cje             4.493e-12
        vje                  0.75
        mje                0.2593
         tf             3.012e-10
        xtf                     0
        vtf                     0
        itf                     0
        ptf                     0
        cjc             3.638e-12
        vjc                  0.75
        mjc                0.3085
       xcjc                     1
         tr             2.395e-07
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
      model             d_generic

      level                     1
         is                 1e-14
        jsw                     0
         rs                     0
        rsw                     0
        trs                     0
       trs2                     0
          n                     1
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
        nbv                     1
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

 Inductor models (Fixed inductor)
      model                     L

        ind                     0
        tc1                     0
        tc2                     0
      csect                     0
        dia                     0
     length                     0
         nt                     0
         mu                     1

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
     device   qnpn_transistor18_1
      model                2n3904
         ic           0.000765604
         ib           6.21683e-06
         ie          -0.000771821
        vbe              0.659967
        vbc              -0.62098
         gm             0.0291756
        gpi           0.000241841
        gmu           7.02387e-06
         gx                   0.1
         go           1.08417e-05
        cpi           1.52283e-11
        cmu           3.02026e-12
        cbx                     0
       csub                     0

 Capacitor: Fixed capacitor
     device cpolarized_capacitor2 cpolarized_capacitor2 cpolarized_capacitor2
      model                     C                     C                     C
capacitance                0.0001               0.00022                 1e-07
      dtemp                     0                     0                     0
     bv_max                 1e+99                 1e+99                 1e+99
          i          -1.63891e-14          -1.82727e-12          -7.81012e-17
          p          -1.47502e-13          -1.90051e-23          -1.00109e-16

 Capacitor: Fixed capacitor
     device cpolarized_capacitor2 cpolarized_capacitor2 cpolarized_capacitor2
      model                     C                     C                     C
capacitance                 1e-07                 1e-07              3.65e-10
      dtemp                     0                     0                     0
     bv_max                 1e+99                 1e+99                 1e+99
          i          -3.43011e-17           2.08167e-18           2.56104e-27
          p           2.26424e-17          -2.06845e-32           1.70833e-51

 Diode: Junction Diode model
     device             ddiode7_1
      model             d_generic
    thermal                     0
         vd            9.9365e-15
         id           1.37779e-26
         gd           1.38662e-12
         cd                     0

 Inductor: Fixed inductor
     device         linductor10_1
      model                     L
 inductance               0.00022
      dtemp                     0
         nt                     0
       flux             -3.59e-30
          v           6.67047e-25
          i          -1.63182e-26
          p           -1.0885e-50

 Resistor: Simple linear resistor
     device           rswitch25_1         rresistor22_3         rresistor22_2
      model                     R                     R                     R
 resistance                 0.001                 10000                 10000
         ac                 0.001                 10000                 10000
      dtemp                     0                     0                     0
     bv_max                 1e+99                 1e+99                 1e+99
      noisy                     1                     1                     1
          i          -0.000861821          -6.67688e-17           0.000771821
          p           7.42735e-10           4.45807e-29            0.00595708

 Resistor: Simple linear resistor
     device         rresistor22_1 r.xoperational_amplif r.xoperational_amplif
      model                     R                     R                     R
 resistance                100000                100000                     5
         ac                100000                100000                     5
      dtemp                     0                     0                     0
     bv_max                 1e+99                 1e+99                 1e+99
      noisy                     1                     1                     1
          i          -6.21683e-06                 9e-05          -1.82727e-12
          p            3.8649e-06               0.00081           1.66946e-23

 Resistor: Simple linear resistor
     device r.xoperational_amplif           rbreaker3_1
      model                     R                     R
 resistance                 50000                     8
         ac                 50000                     8
      dtemp                     0                     0
     bv_max                 1e+99                 1e+99
      noisy                     1                     1
          i          -1.33538e-17          -1.82727e-12
          p           8.91615e-30           2.67114e-23

 VCVS: Voltage controlled voltage source
     device e.xoperational_amplif
          i           1.82727e-12
          v          -1.33538e-11
          p           -2.4401e-23

 Vsource: Independent voltage source
     device           vbattery2_1
         dc                     9
      acmag                     0
      pulse         -
        sin         -
        exp         -
        pwl         -
       sffm         -
         am         -
    trnoise         -
   trrandom         -
    portnum                     0
         z0                     0
        pwr                     0
       freq                     0
      phase                     0
          i          -0.000861821
          p           -0.00775639


Total analysis time (seconds) = 0.058732

Total elapsed time (seconds) = 0.245 

Total DRAM available = 32239.535 MB.
DRAM currently available = 15780.355 MB.
Maximum ngspice program size =   16.477 MB.
Current ngspice program size =   16.344 MB.


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
  "circuit_id": "b06",
  "user_problem": "La radio si accende, ma dall’altoparlante non si sente nulla. Quale potrebbe essere il problema?",
  "pipeline2_output_dir": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\b06",
  "summary": {
    "spice_status": "success",
    "spice_exit_code": 0,
    "spice_message": "ngspice completed successfully.",
    "emitted_elements": 16,
    "skipped_elements": 2,
    "emit_warnings_count": 1,
    "skipped_components_count": 2,
    "node_count": 11,
    "ground_groups_count": 1,
    "singleton_nodes_count": 1,
    "bound_components": 15,
    "missing_components": 0,
    "unsupported_components": 2,
    "spice_ready_components": 16,
    "rules_missing_components": 0,
    "has_tran_csv": true,
    "has_tran_plot": true,
    "led_profiles": {}
  },
  "artifacts": {
    "graph": {
      "step": "01",
      "available": true,
      "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\b06\\01_graph.json",
      "role": "Graph JSON copied from Pipeline 1.0."
    },
    "normalized_circuit": {
      "step": "02",
      "available": true,
      "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\b06\\02_normalized_circuit.json",
      "role": "Normalized circuit representation used by Pipeline 2.0."
    },
    "node_map": {
      "step": "03",
      "available": true,
      "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\b06\\03_node_map.json",
      "role": "Maps component terminals to SPICE node names."
    },
    "values_bound": {
      "step": "04",
      "available": true,
      "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\b06\\04_values_bound.json",
      "role": "Values and labels bound to graph components."
    },
    "component_rules": {
      "step": "06",
      "available": true,
      "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\b06\\06_component_rules.json",
      "role": "SPICE conversion rules for each component."
    },
    "netlist": {
      "step": "07",
      "available": true,
      "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\b06\\07_netlist.cir",
      "role": "Generated SPICE netlist."
    },
    "spice_emit_report": {
      "step": "07",
      "available": true,
      "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\b06\\07_spice_emit_report.json",
      "role": "Report of emitted, skipped and warning components."
    },
    "spice_run": {
      "step": "08",
      "available": true,
      "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\b06\\08_spice_run.json",
      "role": "Structured ngspice execution report."
    },
    "ngspice_stdout": {
      "step": "08",
      "available": true,
      "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\b06\\08_ngspice_stdout.txt",
      "role": "Raw ngspice stdout log."
    },
    "ngspice_stderr": {
      "step": "08",
      "available": true,
      "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\b06\\08_ngspice_stderr.txt",
      "role": "Raw ngspice stderr log."
    },
    "tran_csv": {
      "step": "08",
      "available": true,
      "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\b06\\08_tran.csv",
      "role": "Clean transient CSV, when .tran data is available."
    },
    "tran_plot_png": {
      "step": "08",
      "available": true,
      "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\b06\\08_tran_plot.png",
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
    "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\input\\images\\b06.jpg",
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
