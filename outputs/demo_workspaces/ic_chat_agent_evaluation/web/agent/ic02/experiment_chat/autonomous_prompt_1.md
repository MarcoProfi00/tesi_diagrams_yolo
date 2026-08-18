# Pipeline 2.0 - agente diagnostico autonomo controllato

Sei il controller diagnostico di una pipeline Graph JSON -> SPICE/ngspice.
Devi scegliere il prossimo test controllato oppure fermarti con una conclusione.

## Sintomo utente
L’audio si sente ma il volume è troppo basso. Quali controlli e prove posso fare, senza modificare il segnale di ingresso, per capire la causa e aumentare il volume?

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
- Quando l'utente chiede una correzione e resta budget, `decision=stop` non e
  ammessa finche non esiste una correzione verificata: passa a un'ipotesi
  elettricamente distinta e sostenuta dagli artefatti. Se nessuna risolve il
  sintomo, fermati con `inconclusive` soltanto a budget esaurito e lascia
  `verified_correction` vuoto.
- Se uno scenario migliora il sintomo ma viola un vincolo richiesto (per esempio
  perde regolarita, spegne un componente da preservare o degrada l'uscita), trattalo
  come evidenza diagnostica e non come correzione finale.
- Rispetta alla lettera i vincoli negativi della richiesta. Se l'utente chiede di
  non modificare il segnale o la sorgente di ingresso, non usare
  `change_source_value`, `drive_node_voltage` o `add_voltage_source_between_nodes`,
  neppure su un nodo interno del percorso del segnale.
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
- Per sintomi di amplificazione, volume basso, propagazione o attenuazione di un
  segnale, **ogni scenario**, sia `correction` sia `diagnostic`, deve includere
  `gain: {"input":"v(NODO_IN)","output":"v(NODO_OUT)","min_ratio": NUMERO_POSITIVO}`.
  Entrambe le tensioni devono essere presenti in compare e possono anche usare la
  forma differenziale `v(NODO1,NODO2)`. `min_ratio` e' obbligatorio: scegli una
  soglia positiva motivata dall'obiettivo dello scenario. Valuta il guadagno come
  Vpp(output) / Vpp(input), senza confondere due nodi entrambi di uscita. Non usare
  il solo `changed` per concludere che un segnale non nullo ma trascurabile arrivi
  utilmente all'uscita.
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
- Prima di localizzare un'attenuazione su un tratto del circuito, confronta le
  ampiezze base ai suoi estremi: un rapporto gia prossimo all'unita non sostiene
  l'ipotesi di un collo di bottiglia significativo su quel tratto.
- Distingui sempre `expectations_met_count` da `meaningful_improvement_count`:
  una direzione corretta ma sotto la soglia relativa non verifica una correzione.
  Non riutilizzare in una correzione combinata un'azione che, provata da sola,
  non ha prodotto un miglioramento significativo, salvo che sia indispensabile
  per un altro vincolo esplicito e misurato.
- Per sintomi di distorsione, clipping, saturazione o segnale poco pulito,
  ogni scenario transitorio deve dichiarare quality="thd" e il blocco gain
  deve identificare ingresso e uscita.
- Usa `quality="thd"` soltanto quando il sintomo o un vincolo utente riguarda
  distorsione, clipping, saturazione o qualita del segnale. Non aggiungerla come
  requisito precauzionale a scenari che perseguono un obiettivo diverso.
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
  "circuit_id": "ic02",
  "source_format": "pipeline2.0_node_map",
  "nodes": [
    {
      "node_id": "0",
      "kind": "ground",
      "terminals": [
        "gnd9.1_t1",
        "gnd9.2_t1",
        "gnd9.3_t1",
        "gnd9.4_t1",
        "gnd9.5_t1",
        "gnd9.6_t1",
        "gnd9.7_t1",
        "gnd9.8_t1",
        "gnd9.9_t1",
        "polarized_capacitor20.2_negative",
        "polarized_capacitor20.3_negative",
        "polarized_capacitor20.4_negative",
        "polarized_capacitor20.5_negative",
        "polarized_capacitor20.6_negative",
        "polarized_capacitor20.7_negative",
        "resistor22.2_t2",
        "resistor22.3_t2",
        "speaker24.1_t2",
        "terminal26.1_t2"
      ],
      "terminal_count": 19,
      "source_groups": [
        [
          "gnd9.1_t1",
          "terminal26.1_t2"
        ],
        [
          "gnd9.2_t1",
          "resistor22.2_t2",
          "resistor22.3_t2"
        ],
        [
          "gnd9.3_t1",
          "polarized_capacitor20.2_negative"
        ],
        [
          "gnd9.4_t1",
          "polarized_capacitor20.3_negative"
        ],
        [
          "gnd9.5_t1",
          "polarized_capacitor20.4_negative"
        ],
        [
          "gnd9.6_t1",
          "polarized_capacitor20.6_negative"
        ],
        [
          "gnd9.7_t1",
          "polarized_capacitor20.5_negative"
        ],
        [
          "gnd9.8_t1",
          "polarized_capacitor20.7_negative"
        ],
        [
          "gnd9.9_t1",
          "speaker24.1_t2"
        ]
      ]
    },
    {
      "node_id": "N001",
      "kind": "normal",
      "terminals": [
        "fuse8.1_t1",
        "integrated_circuit11.1_bottom_1",
        "polarized_capacitor20.3_positive",
        "polarized_capacitor20.5_positive"
      ],
      "terminal_count": 4
    },
    {
      "node_id": "N002",
      "kind": "normal",
      "terminals": [
        "fuse8.1_t2",
        "terminal26.3_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N003",
      "kind": "normal",
      "terminals": [
        "fuse8.2_t1",
        "integrated_circuit11.1_top_1",
        "polarized_capacitor20.4_positive",
        "polarized_capacitor20.6_positive"
      ],
      "terminal_count": 4
    },
    {
      "node_id": "N004",
      "kind": "normal",
      "terminals": [
        "fuse8.2_t2",
        "terminal26.2_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N005",
      "kind": "normal",
      "terminals": [
        "integrated_circuit11.1_left_1",
        "polarized_capacitor20.1_positive",
        "resistor22.3_t1"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N006",
      "kind": "normal",
      "terminals": [
        "integrated_circuit11.1_left_2",
        "resistor22.4_t1",
        "resistor22.5_t1"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N007",
      "kind": "normal",
      "terminals": [
        "integrated_circuit11.1_right_1",
        "resistor22.5_t2",
        "resistor22.6_t1",
        "speaker24.1_t1"
      ],
      "terminal_count": 4
    },
    {
      "node_id": "N008",
      "kind": "normal",
      "terminals": [
        "polarized_capacitor20.1_negative",
        "resistor22.1_t2",
        "resistor22.2_t1"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N009",
      "kind": "normal",
      "terminals": [
        "polarized_capacitor20.2_positive",
        "resistor22.4_t2"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N010",
      "kind": "normal",
      "terminals": [
        "polarized_capacitor20.7_positive",
        "resistor22.6_t2"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N011",
      "kind": "normal",
      "terminals": [
        "resistor22.1_t1",
        "terminal26.1_t1"
      ],
      "terminal_count": 2
    }
  ],
  "terminal_to_node": {
    "fuse8.1_t1": "N001",
    "fuse8.1_t2": "N002",
    "fuse8.2_t1": "N003",
    "fuse8.2_t2": "N004",
    "gnd9.1_t1": "0",
    "gnd9.2_t1": "0",
    "gnd9.3_t1": "0",
    "gnd9.4_t1": "0",
    "gnd9.5_t1": "0",
    "gnd9.6_t1": "0",
    "gnd9.7_t1": "0",
    "gnd9.8_t1": "0",
    "gnd9.9_t1": "0",
    "integrated_circuit11.1_bottom_1": "N001",
    "integrated_circuit11.1_left_1": "N005",
    "integrated_circuit11.1_left_2": "N006",
    "integrated_circuit11.1_right_1": "N007",
    "integrated_circuit11.1_top_1": "N003",
    "polarized_capacitor20.1_negative": "N008",
    "polarized_capacitor20.1_positive": "N005",
    "polarized_capacitor20.2_negative": "0",
    "polarized_capacitor20.2_positive": "N009",
    "polarized_capacitor20.3_negative": "0",
    "polarized_capacitor20.3_positive": "N001",
    "polarized_capacitor20.4_negative": "0",
    "polarized_capacitor20.4_positive": "N003",
    "polarized_capacitor20.5_negative": "0",
    "polarized_capacitor20.5_positive": "N001",
    "polarized_capacitor20.6_negative": "0",
    "polarized_capacitor20.6_positive": "N003",
    "polarized_capacitor20.7_negative": "0",
    "polarized_capacitor20.7_positive": "N010",
    "resistor22.1_t1": "N011",
    "resistor22.1_t2": "N008",
    "resistor22.2_t1": "N008",
    "resistor22.2_t2": "0",
    "resistor22.3_t1": "N005",
    "resistor22.3_t2": "0",
    "resistor22.4_t1": "N006",
    "resistor22.4_t2": "N009",
    "resistor22.5_t1": "N006",
    "resistor22.5_t2": "N007",
    "resistor22.6_t1": "N007",
    "resistor22.6_t2": "N010",
    "speaker24.1_t1": "N007",
    "speaker24.1_t2": "0",
    "terminal26.1_t1": "N011",
    "terminal26.1_t2": "0",
    "terminal26.2_t1": "N004",
    "terminal26.3_t1": "N002"
  },
  "component_terminal_nodes": {
    "fuse8.1": {
      "t1": "N001",
      "t2": "N002"
    },
    "fuse8.2": {
      "t1": "N003",
      "t2": "N004"
    },
    "gnd9.1": {
      "t1": "0"
    },
    "gnd9.2": {
      "t1": "0"
    },
    "gnd9.3": {
      "t1": "0"
    },
    "gnd9.4": {
      "t1": "0"
    },
    "gnd9.5": {
      "t1": "0"
    },
    "gnd9.6": {
      "t1": "0"
    },
    "gnd9.7": {
      "t1": "0"
    },
    "gnd9.8": {
      "t1": "0"
    },
    "gnd9.9": {
      "t1": "0"
    },
    "integrated_circuit11.1": {
      "left_1": "N005",
      "left_2": "N006",
      "right_1": "N007",
      "top_1": "N003",
      "bottom_1": "N001"
    },
    "polarized_capacitor20.1": {
      "negative": "N008",
      "positive": "N005"
    },
    "polarized_capacitor20.2": {
      "positive": "N009",
      "negative": "0"
    },
    "polarized_capacitor20.3": {
      "positive": "N001",
      "negative": "0"
    },
    "polarized_capacitor20.4": {
      "positive": "N003",
      "negative": "0"
    },
    "polarized_capacitor20.5": {
      "positive": "N001",
      "negative": "0"
    },
    "polarized_capacitor20.6": {
      "positive": "N003",
      "negative": "0"
    },
    "polarized_capacitor20.7": {
      "positive": "N010",
      "negative": "0"
    },
    "resistor22.1": {
      "t1": "N011",
      "t2": "N008"
    },
    "resistor22.2": {
      "t1": "N008",
      "t2": "0"
    },
    "resistor22.3": {
      "t1": "N005",
      "t2": "0"
    },
    "resistor22.4": {
      "t1": "N006",
      "t2": "N009"
    },
    "resistor22.5": {
      "t1": "N006",
      "t2": "N007"
    },
    "resistor22.6": {
      "t1": "N007",
      "t2": "N010"
    },
    "speaker24.1": {
      "t1": "N007",
      "t2": "0"
    },
    "terminal26.1": {
      "t1": "N011",
      "t2": "0"
    },
    "terminal26.2": {
      "t1": "N004"
    },
    "terminal26.3": {
      "t1": "N002"
    }
  },
  "warnings": {
    "ground_groups_count": 9,
    "multiple_ground_groups_merged_as_node_0": true,
    "singleton_nodes": [],
    "original_warnings": {
      "unconnected_terminals": [],
      "unmatched_terminals": [],
      "suspicious_matches": []
    },
    "normalization_warnings": []
  },
  "stats": {
    "nodes_count": 12,
    "normal_nodes_count": 11,
    "ground_nodes_count": 1,
    "ground_groups_count": 9,
    "terminal_to_node_count": 50,
    "singleton_nodes_count": 0
  }
}

```

## 06_component_rules.json
```text
{
  "circuit_id": "ic02",
  "source_format": "pipeline2.0_component_rules",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\data\\batchPipeline2.0\\batchICChatAgentEvaluation\\values\\ic02_values.yaml",
  "spice_classes_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_spice_classes.yaml",
  "supplies": {
    "AUDIO_IN": {
      "status": "spice_ready",
      "spice_prefix": "V",
      "emit_as": "independent_voltage_source",
      "nodes": [
        "N011",
        "0"
      ],
      "parameters": {
        "terminal": "terminal26.1_t1",
        "return_terminal": "terminal26.1_t2",
        "type": "sin",
        "waveform": "sin",
        "value": 0.02,
        "unit": "V",
        "offset": 0,
        "amplitude": 0.02,
        "frequency": 1000,
        "frequency_unit": "Hz",
        "reference": 0,
        "source": "manual_testbench_assumption",
        "label_text": "Audio IN: sinusoidale 20 mV picco, 1 kHz",
        "viewer_override": {
          "label": "AUDIO IN",
          "display_value": "20 mVpk @ 1 kHz",
          "tooltip": "Testbench SPICE: SIN(0 20m 1k)"
        },
        "node": "N011",
        "return_node": "0"
      }
    },
    "VCC_25": {
      "status": "spice_ready",
      "spice_prefix": "V",
      "emit_as": "independent_voltage_source",
      "nodes": [
        "N004",
        "0"
      ],
      "parameters": {
        "terminal": "terminal26.2_t1",
        "type": "dc",
        "value": 25,
        "unit": "V",
        "reference": 0,
        "source": "manual_from_image_label",
        "label_text": "+25 V DC",
        "viewer_override": {
          "visual_class": "voltage_source",
          "label": "VCC",
          "display_value": "+25 V"
        },
        "node": "N004"
      }
    },
    "VEE_N25": {
      "status": "spice_ready",
      "spice_prefix": "V",
      "emit_as": "independent_voltage_source",
      "nodes": [
        "N002",
        "0"
      ],
      "parameters": {
        "terminal": "terminal26.3_t1",
        "type": "dc",
        "value": -25,
        "unit": "V",
        "reference": 0,
        "source": "manual_from_image_label",
        "label_text": "-25 V DC",
        "viewer_override": {
          "visual_class": "voltage_source",
          "label": "VEE",
          "display_value": "-25 V"
        },
        "node": "N002"
      }
    }
  },
  "components": {
    "fuse8.1": {
      "class_name": "Fuse",
      "status": "spice_ready",
      "spice_support": "simplified",
      "spice_prefix": null,
      "emit_as": null,
      "node_order": [
        "t1",
        "t2"
      ],
      "nodes": [
        "N001",
        "N002"
      ],
      "parameters": {
        "state": "closed",
        "current_rating": 2,
        "current_rating_unit": "A",
        "source": "manual_from_image_label",
        "label_text": "F2 2 A, chiuso",
        "viewer_override": {
          "label": "F2",
          "display_value": "2 A"
        }
      },
      "strategy": "short_circuit"
    },
    "fuse8.2": {
      "class_name": "Fuse",
      "status": "spice_ready",
      "spice_support": "simplified",
      "spice_prefix": null,
      "emit_as": null,
      "node_order": [
        "t1",
        "t2"
      ],
      "nodes": [
        "N003",
        "N004"
      ],
      "parameters": {
        "state": "closed",
        "current_rating": 2,
        "current_rating_unit": "A",
        "source": "manual_from_image_label",
        "label_text": "F1 2 A, chiuso",
        "viewer_override": {
          "label": "F1",
          "display_value": "2 A"
        }
      },
      "strategy": "short_circuit"
    },
    "gnd9.1": {
      "class_name": "GND",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "GND terminals are already mapped to SPICE node 0."
    },
    "gnd9.2": {
      "class_name": "GND",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "GND terminals are already mapped to SPICE node 0."
    },
    "gnd9.3": {
      "class_name": "GND",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "GND terminals are already mapped to SPICE node 0."
    },
    "gnd9.4": {
      "class_name": "GND",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "GND terminals are already mapped to SPICE node 0."
    },
    "gnd9.5": {
      "class_name": "GND",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "GND terminals are already mapped to SPICE node 0."
    },
    "gnd9.6": {
      "class_name": "GND",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "GND terminals are already mapped to SPICE node 0."
    },
    "gnd9.7": {
      "class_name": "GND",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "GND terminals are already mapped to SPICE node 0."
    },
    "gnd9.8": {
      "class_name": "GND",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "GND terminals are already mapped to SPICE node 0."
    },
    "gnd9.9": {
      "class_name": "GND",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "GND terminals are already mapped to SPICE node 0."
    },
    "integrated_circuit11.1": {
      "class_name": "Integrated_Circuit",
      "status": "spice_ready",
      "spice_support": "subcircuit",
      "spice_prefix": "X",
      "emit_as": "subcircuit",
      "node_order": [
        "VIN",
        "VIP",
        "VSS",
        "VDD",
        "VOUT"
      ],
      "nodes": [
        "N006",
        "N005",
        "N001",
        "N003",
        "N007"
      ],
      "parameters": {
        "model": "LM1875_0",
        "source": "ti_official_snam066a_pspice_model",
        "label_text": "IC1 LM1875; modello ufficiale TI Rev. A",
        "viewer_override": {
          "label": "IC1",
          "display_value": "LM1875",
          "tooltip": "IC1 LM1875; modello ufficiale TI PSpice Rev. A SNAM066A"
        },
        "spice_override": {
          "emit_as": "subcircuit",
          "pin_order": [
            "VIN",
            "VIP",
            "VSS",
            "VDD",
            "VOUT"
          ],
          "node_refs": {
            "VIN": "integrated_circuit11.1_left_2",
            "VIP": "integrated_circuit11.1_left_1",
            "VSS": "integrated_circuit11.1_bottom_1",
            "VDD": "integrated_circuit11.1_top_1",
            "VOUT": "integrated_circuit11.1_right_1"
          },
          "resolved_node_refs": {
            "VIN": "N006",
            "VIP": "N005",
            "VSS": "N001",
            "VDD": "N003",
            "VOUT": "N007"
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
        "N005",
        "N008"
      ],
      "parameters": {
        "value": 1,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C4 1 uF",
        "viewer_override": {
          "label": "C4",
          "display_value": "1 uF"
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
        "N009",
        "0"
      ],
      "parameters": {
        "value": 22,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C1 22 uF",
        "viewer_override": {
          "label": "C1",
          "display_value": "22 uF"
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
        "N001",
        "0"
      ],
      "parameters": {
        "value": 100,
        "unit": "nf",
        "source": "manual_from_image_label",
        "label_text": "C2 100 nF",
        "viewer_override": {
          "label": "C2",
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
        "N003",
        "0"
      ],
      "parameters": {
        "value": 100,
        "unit": "nf",
        "source": "manual_from_image_label",
        "label_text": "C6 100 nF",
        "viewer_override": {
          "label": "C6",
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
        "N001",
        "0"
      ],
      "parameters": {
        "value": 220,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C3 220 uF",
        "viewer_override": {
          "label": "C3",
          "display_value": "220 uF"
        }
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
        "N003",
        "0"
      ],
      "parameters": {
        "value": 220,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C5 220 uF",
        "viewer_override": {
          "label": "C5",
          "display_value": "220 uF"
        }
      }
    },
    "polarized_capacitor20.7": {
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
        "N010",
        "0"
      ],
      "parameters": {
        "value": 0.22,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C7 0.22 uF",
        "viewer_override": {
          "label": "C7",
          "display_value": "0.22 uF"
        }
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
        "N011",
        "N008"
      ],
      "parameters": {
        "value": 1,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R5 1 kohm",
        "viewer_override": {
          "label": "R5",
          "display_value": "1 kohm"
        }
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
        "N008",
        "0"
      ],
      "parameters": {
        "value": 1,
        "unit": "Mohm",
        "source": "manual_from_image_label",
        "label_text": "R4 1 Mohm",
        "viewer_override": {
          "label": "R4",
          "display_value": "1 Mohm"
        }
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
        "N005",
        "0"
      ],
      "parameters": {
        "value": 22,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R3 22 kohm",
        "viewer_override": {
          "label": "R3",
          "display_value": "22 kohm"
        }
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
        "N006",
        "N009"
      ],
      "parameters": {
        "value": 10,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R2 10 kohm",
        "viewer_override": {
          "label": "R2",
          "display_value": "10 kohm"
        }
      }
    },
    "resistor22.5": {
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
        "N006",
        "N007"
      ],
      "parameters": {
        "value": 180,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R1 180 kohm",
        "viewer_override": {
          "label": "R1",
          "display_value": "180 kohm"
        }
      }
    },
    "resistor22.6": {
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
        "N010"
      ],
      "parameters": {
        "value": 1,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R6 1 ohm",
        "viewer_override": {
          "label": "R6",
          "display_value": "1 ohm"
        }
      }
    },
    "speaker24.1": {
      "class_name": "Speaker",
      "status": "spice_ready",
      "spice_support": "equivalent",
      "spice_prefix": "R",
      "emit_as": "resistive_load",
      "node_order": [
        "t1",
        "t2"
      ],
      "nodes": [
        "N007",
        "0"
      ],
      "parameters": {
        "spice_override": {
          "emit_as": "resistive_load",
          "equivalent_resistance": 4,
          "resistance_unit": "ohm",
          "node_order": [
            "t1",
            "t2"
          ],
          "semantic_role": "speaker_equivalent"
        },
        "source": "manual_from_image_label",
        "label_text": "K1 speaker equivalente 4 ohm",
        "viewer_override": {
          "visual_class": "speaker",
          "label": "K1",
          "display_value": "4 ohm"
        },
        "equivalent_resistance": 4,
        "resistance_unit": "ohm"
      },
      "reason": "Explicit YAML override emitted as an equivalent resistive load."
    },
    "terminal26.1": {
      "class_name": "Terminal",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "External terminal/label; useful for nodes and interface handling."
    },
    "terminal26.2": {
      "class_name": "Terminal",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "External terminal/label; useful for nodes and interface handling."
    },
    "terminal26.3": {
      "class_name": "Terminal",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "External terminal/label; useful for nodes and interface handling."
    }
  },
  "simulation": {
    "analyses": [
      "op",
      "tran"
    ],
    "tran": {
      "step": "10us",
      "stop": "20ms"
    }
  },
  "stats": {
    "components_total": 29,
    "spice_ready_components": 17,
    "not_emitted_components": 12,
    "measurement_components": 0,
    "missing_components": 0,
    "unsupported_components": 0,
    "pin_aware_components": 0,
    "invalid_components": 0,
    "supplies_ready_count": 3
  }
}

```

## 07_netlist.cir
```text
* pipeline2.0 netlist
* circuit: ic02

VAUDIO_IN N011 0 SIN(0 0.02 1000)
VVCC_25 N004 0 DC 25
VVEE_N25 N002 0 DC -25
Rfuse8_1 N001 N002 1m
Rfuse8_2 N003 N004 1m
Xintegrated_circuit11_1 N006 N005 N001 N003 N007 LM1875_0
Cpolarized_capacitor20_1 N005 N008 1u
Cpolarized_capacitor20_2 N009 0 22u
Cpolarized_capacitor20_3 N001 0 100n
Cpolarized_capacitor20_4 N003 0 100n
Cpolarized_capacitor20_5 N001 0 220u
Cpolarized_capacitor20_6 N003 0 220u
Cpolarized_capacitor20_7 N010 0 0.22u
Rresistor22_1 N011 N008 1k
Rresistor22_2 N008 0 1meg
Rresistor22_3 N005 0 22k
Rresistor22_4 N006 N009 10k
Rresistor22_5 N006 N007 180k
Rresistor22_6 N007 N010 1
Rspeaker24_1 N007 0 4

.include "07_external_models.lib"

.op
.save all
.tran 10us 20ms

.control
set wr_singlescale
set wr_vecnames
run
wrdata 08_tran.csv time v(N001) v(N002) v(N003) v(N004) v(N005) v(N006) v(N007) v(N008) v(N009) v(N010) v(N011)
.endc
.end

```

## 07_spice_emit_report.json
```text
{
  "circuit_id": "ic02",
  "source_format": "pipeline2.0_spice_emit_report",
  "emitted_elements": 20,
  "skipped_elements": 12,
  "skipped_components": [
    "gnd9.1",
    "gnd9.2",
    "gnd9.3",
    "gnd9.4",
    "gnd9.5",
    "gnd9.6",
    "gnd9.7",
    "gnd9.8",
    "gnd9.9",
    "terminal26.1",
    "terminal26.2",
    "terminal26.3"
  ],
  "informational_skips": [
    "gnd9.1: structural component not emitted",
    "gnd9.2: structural component not emitted",
    "gnd9.3: structural component not emitted",
    "gnd9.4: structural component not emitted",
    "gnd9.5: structural component not emitted",
    "gnd9.6: structural component not emitted",
    "gnd9.7: structural component not emitted",
    "gnd9.8: structural component not emitted",
    "gnd9.9: structural component not emitted",
    "terminal26.1: structural component not emitted",
    "terminal26.2: structural component not emitted",
    "terminal26.3: structural component not emitted"
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
      "N008",
      "N009",
      "N010",
      "N011"
    ],
    "device_currents": []
  },
  "models": [
    "LM1875_0"
  ],
  "warnings": [],
  "external_model_sources": [
    {
      "model": "LM1875_0",
      "kind": "file",
      "file": "spice_models/ti/lm1875/snam066a/LM1875.lib",
      "sha256": "28BF3FC1D14AD5929C3151A7BCB6F97922BD59B38539FE334B7018522551B1F2"
    }
  ],
  "ngspice_defines": {
    "ngbehavior": "ps"
  }
}

```

## 08_ngspice_stdout.txt
```text
Note: gnd in a subcircuit is not set to 0 automatically

Note: Compatibility modes selected: ps


Circuit: * pipeline2.0 netlist

Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

No. of Data Rows : 1

Initial Transient Solution
--------------------------

Node                                   Voltage
----                                   -------
n011                                         0
n004                                        25
n002                                       -25
n001                                  -24.9999
n003                                   24.9999
xintegrated_circuit11_1.20           0.0054002
xintegrated_circuit11_1.19          0.00540124
xintegrated_circuit11_1.12           0.0044002
xintegrated_circuit11_1.gndf      -2.00002e-10
xintegrated_circuit11_1.xu4.1      0.000790567
xintegrated_circuit11_1.xu4.2     -2.00003e-10
xintegrated_circuit11_1.9           0.00495669
xintegrated_circuit11_1.8           0.00416612
xintegrated_circuit11_1.xu5.1      0.000444568
xintegrated_circuit11_1.xu5.2     -2.00002e-10
xintegrated_circuit11_1.10          0.00540126
xintegrated_circuit11_1.xu_vnoise.7        0.833786
xintegrated_circuit11_1.xu_vnoise.8        0.833786
xintegrated_circuit11_1.xu_vnoise.3               0
xintegrated_circuit11_1.xu_vnoise.6               0
xintegrated_circuit11_1.xu_vnoise.4               0
xintegrated_circuit11_1.xu_vnoise.5               0
xintegrated_circuit11_1.11           0.0044002
xintegrated_circuit11_1.14          -0.0326299
xintegrated_circuit11_1.xu2.g1_int1    -4.50187e-09
xintegrated_circuit11_1.13          0.00540124
xintegrated_circuit11_1.15           0.0054002
xintegrated_circuit11_1.xu2.gr1_int1    -4.45727e-09
xintegrated_circuit11_1.xu2.gr11_int1    -4.45727e-11
xintegrated_circuit11_1.17          -0.0326299
xintegrated_circuit11_1.16          -0.0318341
xintegrated_circuit11_1.xu3.gres_int1     -0.00795872
xintegrated_circuit11_1.xu_tf.vp1      -0.0326299
xintegrated_circuit11_1.xu_tf.grp1_int1    -3.26299e-05
xintegrated_circuit11_1.xu_tf.vp2      -0.0326299
xintegrated_circuit11_1.xu_tf.grp2_int1    -3.26299e-05
xintegrated_circuit11_1.xu_tf.vp3      -0.0326299
xintegrated_circuit11_1.xu_tf.grp3_int1    -3.26299e-05
xintegrated_circuit11_1.xu_tf.vp4      -0.0326299
xintegrated_circuit11_1.xu_tf.grp4_int1    -3.26299e-05
xintegrated_circuit11_1.xu_tf.vz1      -0.0326299
xintegrated_circuit11_1.xu_tf.vx1    -2.00002e-10
xintegrated_circuit11_1.xu_tf.grz1_int1    -3.26299e-05
xintegrated_circuit11_1.xu_tf.vz2      -0.0326299
xintegrated_circuit11_1.xu_tf.vx2    -2.00002e-10
xintegrated_circuit11_1.xu_tf.grz2_int1    -3.26299e-05
xintegrated_circuit11_1.xu_tf.vz3      -0.0326299
xintegrated_circuit11_1.xu_tf.vx3    -2.00002e-10
xintegrated_circuit11_1.xu_tf.grz3_int1    -3.26299e-05
xintegrated_circuit11_1.xu_tf.vz4      -0.0326299
xintegrated_circuit11_1.xu_tf.vx4    -2.00002e-10
xintegrated_circuit11_1.xu_tf.grz4_int1    -3.26299e-05
xintegrated_circuit11_1.18          -0.0326299
xintegrated_circuit11_1.xu_tf.vx5    -2.00002e-10
xintegrated_circuit11_1.xu_tf.grz5_int1    -3.26299e-05
xintegrated_circuit11_1.xu1.g1_int1            0.07
xintegrated_circuit11_1.xu_gnd.egndf_int1    -2.00002e-10
n007                                -0.0318341
xintegrated_circuit11_1.vimon      -0.00795872
xintegrated_circuit11_1.xu6.emeter_int1     -0.00795872
xintegrated_circuit11_1.xu_claw.vdd_clp         23.9999
xintegrated_circuit11_1.xu_claw.epclip_int1         23.9999
xintegrated_circuit11_1.xu_claw.vss_clp        -23.9999
xintegrated_circuit11_1.xu_claw.enclip_int1        -23.9999
xintegrated_circuit11_1.xu_claw.eclamp_int1      -0.0326299
xintegrated_circuit11_1.xu2_vclamp.eclamp_int1      0.00540124
xintegrated_circuit11_1.xu1_vclamp.eclamp_int1       0.0054002
xintegrated_circuit11_1.xu_cmrr.1     1.68803e-08
xintegrated_circuit11_1.xu_cmrr.2    -2.00002e-10
n005                                    0.0044
xintegrated_circuit11_1.xuinput.g1_int1          -2e-07
n006                                0.00416592
xintegrated_circuit11_1.xuinput.g2_int1          -2e-07
n008                                         0
n009                                0.00416592
n010                                -0.0318341
b.xintegrated_circuit11_1.xuinput.bg2#branch               0
b.xintegrated_circuit11_1.xuinput.bg1#branch               0
b.xintegrated_circuit11_1.xu1_vclamp.beclamp#branch               0
b.xintegrated_circuit11_1.xu2_vclamp.beclamp#branch               0
b.xintegrated_circuit11_1.xu_claw.beclamp#branch               0
b.xintegrated_circuit11_1.xu_claw.benclip#branch               0
b.xintegrated_circuit11_1.xu_claw.bepclip#branch               0
b.xintegrated_circuit11_1.xu6.bemeter#branch               0
v.xintegrated_circuit11_1.xu6.vsense#branch     -0.00795872
b.xintegrated_circuit11_1.xu_gnd.begndf#branch               0
b.xintegrated_circuit11_1.xu1.bg1#branch               0
b.xintegrated_circuit11_1.xu_tf.bgrz5#branch               0
b.xintegrated_circuit11_1.xu_tf.bgrz4#branch               0
b.xintegrated_circuit11_1.xu_tf.bgrz3#branch               0
b.xintegrated_circuit11_1.xu_tf.bgrz2#branch               0
b.xintegrated_circuit11_1.xu_tf.bgrz1#branch               0
b.xintegrated_circuit11_1.xu_tf.bgrp4#branch               0
b.xintegrated_circuit11_1.xu_tf.bgrp3#branch               0
b.xintegrated_circuit11_1.xu_tf.bgrp2#branch               0
b.xintegrated_circuit11_1.xu_tf.bgrp1#branch               0
b.xintegrated_circuit11_1.xu3.bgres#branch               0
b.xintegrated_circuit11_1.xu2.bgr11#branch               0
b.xintegrated_circuit11_1.xu2.bgr1#branch               0
b.xintegrated_circuit11_1.xu2.bg1#branch               0
l.xintegrated_circuit11_1.xu_cmrr.l1#branch     1.70803e-08
l.xintegrated_circuit11_1.xu_tf.lz5#branch    -3.26299e-05
l.xintegrated_circuit11_1.xu_tf.lz4#branch    -3.26299e-05
l.xintegrated_circuit11_1.xu_tf.lz3#branch    -3.26299e-05
l.xintegrated_circuit11_1.xu_tf.lz2#branch    -3.26299e-05
l.xintegrated_circuit11_1.xu_tf.lz1#branch    -3.26299e-05
l.xintegrated_circuit11_1.xu5.l1#branch     0.000444569
l.xintegrated_circuit11_1.xu4.l1#branch     0.000790567
e.xintegrated_circuit11_1.xu_cmrr.e1#branch          -2e-07
e.xintegrated_circuit11_1.xu1_vclamp.eclamp#branch               0
e.xintegrated_circuit11_1.xu2_vclamp.eclamp#branch               0
e.xintegrated_circuit11_1.xu_claw.eclamp#branch      0.00795872
e.xintegrated_circuit11_1.xu_claw.enclip#branch               0
e.xintegrated_circuit11_1.xu_claw.epclip#branch               0
e.xintegrated_circuit11_1.xu6.emeter#branch               0
e.xintegrated_circuit11_1.xu_gnd.egndf#branch      0.00795872
e.xintegrated_circuit11_1.xu_vnoise.e3#branch          -2e-07
e.xintegrated_circuit11_1.xu_vnoise.e2#branch               0
e.xintegrated_circuit11_1.xu_vnoise.e1#branch               0
e.xintegrated_circuit11_1.xu5.e1#branch           2e-07
e.xintegrated_circuit11_1.xu4.e1#branch           2e-07
v.xintegrated_circuit11_1.vos#branch           2e-07
vvee_n25#branch                      0.0699998
vvcc_25#branch                      -0.0700002
vaudio_in#branch                             0


No. of Data Rows : 2008
Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

No. of Data Rows : 1

Initial Transient Solution
--------------------------

Node                                   Voltage
----                                   -------
n011                                         0
n004                                        25
n002                                       -25
n001                                  -24.9999
n003                                   24.9999
xintegrated_circuit11_1.20           0.0054002
xintegrated_circuit11_1.19          0.00540124
xintegrated_circuit11_1.12           0.0044002
xintegrated_circuit11_1.gndf      -2.00002e-10
xintegrated_circuit11_1.xu4.1      0.000790567
xintegrated_circuit11_1.xu4.2     -2.00003e-10
xintegrated_circuit11_1.9           0.00495669
xintegrated_circuit11_1.8           0.00416612
xintegrated_circuit11_1.xu5.1      0.000444568
xintegrated_circuit11_1.xu5.2     -2.00002e-10
xintegrated_circuit11_1.10          0.00540126
xintegrated_circuit11_1.xu_vnoise.7        0.833786
xintegrated_circuit11_1.xu_vnoise.8        0.833786
xintegrated_circuit11_1.xu_vnoise.3               0
xintegrated_circuit11_1.xu_vnoise.6               0
xintegrated_circuit11_1.xu_vnoise.4               0
xintegrated_circuit11_1.xu_vnoise.5               0
xintegrated_circuit11_1.11           0.0044002
xintegrated_circuit11_1.14          -0.0326299
xintegrated_circuit11_1.xu2.g1_int1    -4.50187e-09
xintegrated_circuit11_1.13          0.00540124
xintegrated_circuit11_1.15           0.0054002
xintegrated_circuit11_1.xu2.gr1_int1    -4.45727e-09
xintegrated_circuit11_1.xu2.gr11_int1    -4.45727e-11
xintegrated_circuit11_1.17          -0.0326299
xintegrated_circuit11_1.16          -0.0318341
xintegrated_circuit11_1.xu3.gres_int1     -0.00795872
xintegrated_circuit11_1.xu_tf.vp1      -0.0326299
xintegrated_circuit11_1.xu_tf.grp1_int1    -3.26299e-05
xintegrated_circuit11_1.xu_tf.vp2      -0.0326299
xintegrated_circuit11_1.xu_tf.grp2_int1    -3.26299e-05
xintegrated_circuit11_1.xu_tf.vp3      -0.0326299
xintegrated_circuit11_1.xu_tf.grp3_int1    -3.26299e-05
xintegrated_circuit11_1.xu_tf.vp4      -0.0326299
xintegrated_circuit11_1.xu_tf.grp4_int1    -3.26299e-05
xintegrated_circuit11_1.xu_tf.vz1      -0.0326299
xintegrated_circuit11_1.xu_tf.vx1    -2.00002e-10
xintegrated_circuit11_1.xu_tf.grz1_int1    -3.26299e-05
xintegrated_circuit11_1.xu_tf.vz2      -0.0326299
xintegrated_circuit11_1.xu_tf.vx2    -2.00002e-10
xintegrated_circuit11_1.xu_tf.grz2_int1    -3.26299e-05
xintegrated_circuit11_1.xu_tf.vz3      -0.0326299
xintegrated_circuit11_1.xu_tf.vx3    -2.00002e-10
xintegrated_circuit11_1.xu_tf.grz3_int1    -3.26299e-05
xintegrated_circuit11_1.xu_tf.vz4      -0.0326299
xintegrated_circuit11_1.xu_tf.vx4    -2.00002e-10
xintegrated_circuit11_1.xu_tf.grz4_int1    -3.26299e-05
xintegrated_circuit11_1.18          -0.0326299
xintegrated_circuit11_1.xu_tf.vx5    -2.00002e-10
xintegrated_circuit11_1.xu_tf.grz5_int1    -3.26299e-05
xintegrated_circuit11_1.xu1.g1_int1            0.07
xintegrated_circuit11_1.xu_gnd.egndf_int1    -2.00002e-10
n007                                -0.0318341
xintegrated_circuit11_1.vimon      -0.00795872
xintegrated_circuit11_1.xu6.emeter_int1     -0.00795872
xintegrated_circuit11_1.xu_claw.vdd_clp         23.9999
xintegrated_circuit11_1.xu_claw.epclip_int1         23.9999
xintegrated_circuit11_1.xu_claw.vss_clp        -23.9999
xintegrated_circuit11_1.xu_claw.enclip_int1        -23.9999
xintegrated_circuit11_1.xu_claw.eclamp_int1      -0.0326299
xintegrated_circuit11_1.xu2_vclamp.eclamp_int1      0.00540124
xintegrated_circuit11_1.xu1_vclamp.eclamp_int1       0.0054002
xintegrated_circuit11_1.xu_cmrr.1     1.68803e-08
xintegrated_circuit11_1.xu_cmrr.2    -2.00002e-10
n005                                    0.0044
xintegrated_circuit11_1.xuinput.g1_int1          -2e-07
n006                                0.00416592
xintegrated_circuit11_1.xuinput.g2_int1          -2e-07
n008                                         0
n009                                0.00416592
n010                                -0.0318341
b.xintegrated_circuit11_1.xuinput.bg2#branch               0
b.xintegrated_circuit11_1.xuinput.bg1#branch               0
b.xintegrated_circuit11_1.xu1_vclamp.beclamp#branch               0
b.xintegrated_circuit11_1.xu2_vclamp.beclamp#branch               0
b.xintegrated_circuit11_1.xu_claw.beclamp#branch               0
b.xintegrated_circuit11_1.xu_claw.benclip#branch               0
b.xintegrated_circuit11_1.xu_claw.bepclip#branch               0
b.xintegrated_circuit11_1.xu6.bemeter#branch               0
v.xintegrated_circuit11_1.xu6.vsense#branch     -0.00795872
b.xintegrated_circuit11_1.xu_gnd.begndf#branch               0
b.xintegrated_circuit11_1.xu1.bg1#branch               0
b.xintegrated_circuit11_1.xu_tf.bgrz5#branch               0
b.xintegrated_circuit11_1.xu_tf.bgrz4#branch               0
b.xintegrated_circuit11_1.xu_tf.bgrz3#branch               0
b.xintegrated_circuit11_1.xu_tf.bgrz2#branch               0
b.xintegrated_circuit11_1.xu_tf.bgrz1#branch               0
b.xintegrated_circuit11_1.xu_tf.bgrp4#branch               0
b.xintegrated_circuit11_1.xu_tf.bgrp3#branch               0
b.xintegrated_circuit11_1.xu_tf.bgrp2#branch               0
b.xintegrated_circuit11_1.xu_tf.bgrp1#branch               0
b.xintegrated_circuit11_1.xu3.bgres#branch               0
b.xintegrated_circuit11_1.xu2.bgr11#branch               0
b.xintegrated_circuit11_1.xu2.bgr1#branch               0
b.xintegrated_circuit11_1.xu2.bg1#branch               0
l.xintegrated_circuit11_1.xu_cmrr.l1#branch     1.70803e-08
l.xintegrated_circuit11_1.xu_tf.lz5#branch    -3.26299e-05
l.xintegrated_circuit11_1.xu_tf.lz4#branch    -3.26299e-05
l.xintegrated_circuit11_1.xu_tf.lz3#branch    -3.26299e-05
l.xintegrated_circuit11_1.xu_tf.lz2#branch    -3.26299e-05
l.xintegrated_circuit11_1.xu_tf.lz1#branch    -3.26299e-05
l.xintegrated_circuit11_1.xu5.l1#branch     0.000444569
l.xintegrated_circuit11_1.xu4.l1#branch     0.000790567
e.xintegrated_circuit11_1.xu_cmrr.e1#branch          -2e-07
e.xintegrated_circuit11_1.xu1_vclamp.eclamp#branch               0
e.xintegrated_circuit11_1.xu2_vclamp.eclamp#branch               0
e.xintegrated_circuit11_1.xu_claw.eclamp#branch      0.00795872
e.xintegrated_circuit11_1.xu_claw.enclip#branch               0
e.xintegrated_circuit11_1.xu_claw.epclip#branch               0
e.xintegrated_circuit11_1.xu6.emeter#branch               0
e.xintegrated_circuit11_1.xu_gnd.egndf#branch      0.00795872
e.xintegrated_circuit11_1.xu_vnoise.e3#branch          -2e-07
e.xintegrated_circuit11_1.xu_vnoise.e2#branch               0
e.xintegrated_circuit11_1.xu_vnoise.e1#branch               0
e.xintegrated_circuit11_1.xu5.e1#branch           2e-07
e.xintegrated_circuit11_1.xu4.e1#branch           2e-07
v.xintegrated_circuit11_1.vos#branch           2e-07
vvee_n25#branch                      0.0699998
vvcc_25#branch                      -0.0700002
vaudio_in#branch                             0

 Reference value :  1.17604e-02

No. of Data Rows : 2008
	Node                                  Voltage
	----                                  -------
	----	-------
	n010                             -3.18341e-02
	n009                             4.165923e-03
	n008                             0.000000e+00
	xintegrated_circuit11_1.xuinput.g2_int1   -2.00000e-07
	n006                             4.165923e-03
	xintegrated_circuit11_1.xuinput.g1_int1   -2.00000e-07
	n005                             4.400000e-03
	xintegrated_circuit11_1.xu_cmrr.2   -2.00000e-10
	xintegrated_circuit11_1.xu_cmrr.1   1.688028e-08
	xintegrated_circuit11_1.xu1_vclamp.eclamp_int1   5.400200e-03
	xintegrated_circuit11_1.xu2_vclamp.eclamp_int1   5.401242e-03
	xintegrated_circuit11_1.xu_claw.eclamp_int1   -3.26299e-02
	xintegrated_circuit11_1.xu_claw.enclip_int1   -2.39999e+01
	xintegrated_circuit11_1.xu_claw.vss_clp   -2.39999e+01
	xintegrated_circuit11_1.xu_claw.epclip_int1   2.399993e+01
	xintegrated_circuit11_1.xu_claw.vdd_clp   2.399993e+01
	xintegrated_circuit11_1.xu6.emeter_int1   -7.95872e-03
	xintegrated_circuit11_1.vimon    -7.95872e-03
	n007                             -3.18341e-02
	xintegrated_circuit11_1.xu_gnd.egndf_int1   -2.00000e-10
	xintegrated_circuit11_1.xu1.g1_int1   7.000000e-02
	xintegrated_circuit11_1.xu_tf.grz5_int1   -3.26299e-05
	xintegrated_circuit11_1.xu_tf.vx5   -2.00000e-10
	xintegrated_circuit11_1.18       -3.26299e-02
	xintegrated_circuit11_1.xu_tf.grz4_int1   -3.26299e-05
	xintegrated_circuit11_1.xu_tf.vx4   -2.00000e-10
	xintegrated_circuit11_1.xu_tf.vz4   -3.26299e-02
	xintegrated_circuit11_1.xu_tf.grz3_int1   -3.26299e-05
	xintegrated_circuit11_1.xu_tf.vx3   -2.00000e-10
	xintegrated_circuit11_1.xu_tf.vz3   -3.26299e-02
	xintegrated_circuit11_1.xu_tf.grz2_int1   -3.26299e-05
	xintegrated_circuit11_1.xu_tf.vx2   -2.00000e-10
	xintegrated_circuit11_1.xu_tf.vz2   -3.26299e-02
	xintegrated_circuit11_1.xu_tf.grz1_int1   -3.26299e-05
	xintegrated_circuit11_1.xu_tf.vx1   -2.00000e-10
	xintegrated_circuit11_1.xu_tf.vz1   -3.26299e-02
	xintegrated_circuit11_1.xu_tf.grp4_int1   -3.26299e-05
	xintegrated_circuit11_1.xu_tf.vp4   -3.26299e-02
	xintegrated_circuit11_1.xu_tf.grp3_int1   -3.26299e-05
	xintegrated_circuit11_1.xu_tf.vp3   -3.26299e-02
	xintegrated_circuit11_1.xu_tf.grp2_int1   -3.26299e-05
	xintegrated_circuit11_1.xu_tf.vp2   -3.26299e-02
	xintegrated_circuit11_1.xu_tf.grp1_int1   -3.26299e-05
	xintegrated_circuit11_1.xu_tf.vp1   -3.26299e-02
	xintegrated_circuit11_1.xu3.gres_int1   -7.95872e-03
	xintegrated_circuit11_1.16       -3.18341e-02
	xintegrated_circuit11_1.17       -3.26299e-02
	xintegrated_circuit11_1.xu2.gr11_int1   -4.45727e-11
	xintegrated_circuit11_1.xu2.gr1_int1   -4.45727e-09
	xintegrated_circuit11_1.15       5.400200e-03
	xintegrated_circuit11_1.13       5.401242e-03
	xintegrated_circuit11_1.xu2.g1_int1   -4.50184e-09
	xintegrated_circuit11_1.14       -3.26299e-02
	xintegrated_circuit11_1.11       4.400200e-03
	xintegrated_circuit11_1.xu_vnoise.5   0.000000e+00
	xintegrated_circuit11_1.xu_vnoise.4   0.000000e+00
	xintegrated_circuit11_1.xu_vnoise.6   0.000000e+00
	xintegrated_circuit11_1.xu_vnoise.3   0.000000e+00
	xintegrated_circuit11_1.xu_vnoise.8   8.340133e-01
	xintegrated_circuit11_1.xu_vnoise.7   8.340133e-01
	xintegrated_circuit11_1.10       5.401259e-03
	xintegrated_circuit11_1.xu5.2    -2.00000e-10
	xintegrated_circuit11_1.xu5.1    4.445684e-04
	xintegrated_circuit11_1.8        4.166123e-03
	xintegrated_circuit11_1.9        4.956690e-03
	xintegrated_circuit11_1.xu4.2    -2.00000e-10
	xintegrated_circuit11_1.xu4.1    7.905670e-04
	xintegrated_circuit11_1.gndf     -2.00000e-10
	xintegrated_circuit11_1.12       4.400200e-03
	xintegrated_circuit11_1.19       5.401242e-03
	xintegrated_circuit11_1.20       5.400200e-03
	n003                             2.499993e+01
	n001                             -2.49999e+01
	n002                             -2.50000e+01
	n004                             2.500000e+01
	n011                             0.000000e+00

	Source	Current
	------	-------

	vaudio_in#branch                 0.000000e+00
	vvcc_25#branch                   -7.00002e-02
	vvee_n25#branch                  6.999980e-02
	v.xintegrated_circuit11_1.vos#branch   2.000000e-07
	e.xintegrated_circuit11_1.xu4.e1#branch   2.000000e-07
	e.xintegrated_circuit11_1.xu5.e1#branch   2.000000e-07
	e.xintegrated_circuit11_1.xu_vnoise.e1#branch   0.000000e+00
	e.xintegrated_circuit11_1.xu_vnoise.e2#branch   0.000000e+00
	e.xintegrated_circuit11_1.xu_vnoise.e3#branch   -2.00000e-07
	e.xintegrated_circuit11_1.xu_gnd.egndf#branch   7.958719e-03
	e.xintegrated_circuit11_1.xu6.emeter#branch   0.000000e+00
	e.xintegrated_circuit11_1.xu_claw.epclip#branch   0.000000e+00
	e.xintegrated_circuit11_1.xu_claw.enclip#branch   0.000000e+00
	e.xintegrated_circuit11_1.xu_claw.eclamp#branch   7.958719e-03
	e.xintegrated_circuit11_1.xu2_vclamp.eclamp#branch   0.000000e+00
	e.xintegrated_circuit11_1.xu1_vclamp.eclamp#branch   0.000000e+00
	e.xintegrated_circuit11_1.xu_cmrr.e1#branch   -2.00000e-07
	l.xintegrated_circuit11_1.xu4.l1#branch   7.905672e-04
	l.xintegrated_circuit11_1.xu5.l1#branch   4.445686e-04
	l.xintegrated_circuit11_1.xu_tf.lz1#branch   -3.26299e-05
	l.xintegrated_circuit11_1.xu_tf.lz2#branch   -3.26299e-05
	l.xintegrated_circuit11_1.xu_tf.lz3#branch   -3.26299e-05
	l.xintegrated_circuit11_1.xu_tf.lz4#branch   -3.26299e-05
	l.xintegrated_circuit11_1.xu_tf.lz5#branch   -3.26299e-05
	l.xintegrated_circuit11_1.xu_cmrr.l1#branch   1.708028e-08
	b.xintegrated_circuit11_1.xu2.bg1#branch   0.000000e+00
	b.xintegrated_circuit11_1.xu2.bgr1#branch   0.000000e+00
	b.xintegrated_circuit11_1.xu2.bgr11#branch   0.000000e+00
	b.xintegrated_circuit11_1.xu3.bgres#branch   0.000000e+00
	b.xintegrated_circuit11_1.xu_tf.bgrp1#branch   0.000000e+00
	b.xintegrated_circuit11_1.xu_tf.bgrp2#branch   0.000000e+00
	b.xintegrated_circuit11_1.xu_tf.bgrp3#branch   0.000000e+00
	b.xintegrated_circuit11_1.xu_tf.bgrp4#branch   0.000000e+00
	b.xintegrated_circuit11_1.xu_tf.bgrz1#branch   0.000000e+00
	b.xintegrated_circuit11_1.xu_tf.bgrz2#branch   0.000000e+00
	b.xintegrated_circuit11_1.xu_tf.bgrz3#branch   0.000000e+00
	b.xintegrated_circuit11_1.xu_tf.bgrz4#branch   0.000000e+00
	b.xintegrated_circuit11_1.xu_tf.bgrz5#branch   0.000000e+00
	b.xintegrated_circuit11_1.xu1.bg1#branch   0.000000e+00
	b.xintegrated_circuit11_1.xu_gnd.begndf#branch   0.000000e+00
	v.xintegrated_circuit11_1.xu6.vsense#branch   -7.95872e-03
	b.xintegrated_circuit11_1.xu6.bemeter#branch   0.000000e+00
	b.xintegrated_circuit11_1.xu_claw.bepclip#branch   0.000000e+00
	b.xintegrated_circuit11_1.xu_claw.benclip#branch   0.000000e+00
	b.xintegrated_circuit11_1.xu_claw.beclamp#branch   0.000000e+00
	b.xintegrated_circuit11_1.xu2_vclamp.beclamp#branch   0.000000e+00
	b.xintegrated_circuit11_1.xu1_vclamp.beclamp#branch   0.000000e+00
	b.xintegrated_circuit11_1.xuinput.bg1#branch   0.000000e+00
	b.xintegrated_circuit11_1.xuinput.bg2#branch   0.000000e+00

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
      model xintegrated_circuit11 xintegrated_circuit11 xintegrated_circuit11

      level                     1                     1                     1
         is                 1e-14                 1e-14                 1e-14
        jsw                     0                     0                     0
         rs                     0                     0                     0
        rsw                     0                     0                     0
        trs                     0                     0                     0
       trs2                     0                     0                     0
          n                  0.01                  0.01                  0.01
         ns                     1                     1                     1
         tt                     0                     0                     0
       ttt1                     0                     0                     0
       ttt2                     0                     0                     0
        cjo                     0                     0                     0
         vj                     1                     1                     1
          m                   0.5                   0.5                   0.5
        tm1                     0                     0                     0
        tm2                     0                     0                     0
        cjp                     0                     0                     0
        php                     1                     1                     1
       mjsw                  0.33                  0.33                  0.33
        ikf                     0                     0                     0
        ikr                     0                     0                     0
        ikp                     0                     0                     0
        nbv                  0.01                  0.01                  0.01
       area                     1                     1                     1
         pj                     0                     0                     0
       tlev                     0                     0                     0
      tlevc                     0                     0                     0
         eg                  1.11                  1.11                  1.11
       gap1              0.000702              0.000702              0.000702
       gap2                  1108                  1108                  1108
        xti                     3                     3                     3
        cta                     0                     0                     0
        ctp                     0                     0                     0
        tpb                     0                     0                     0
       tphp                     0                     0                     0
       jtun                     0                     0                     0
     jtunsw                     0                     0                     0
       ntun                    30                    30                    30
     xtitun                     3                     3                     3
        keg                     1                     1                     1
         kf                     0                     0                     0
         af                     1                     1                     1
         fc                   0.5                   0.5                   0.5
        fcs                   0.5                   0.5                   0.5
         bv                    60                    60                    60
        ibv                 0.001                 0.001                 0.001
        tcv                     0                     0                     0
        isr                 1e-14                 1e-14                 1e-14
         nr                     2                     2                     2
         vp                     0                     0                     0
     fv_max                 1e+99                 1e+99                 1e+99
     bv_max                 1e+99                 1e+99                 1e+99
     id_max                 1e+99                 1e+99                 1e+99
     te_max                 1e+99                 1e+99                 1e+99
     pd_max                 1e+99                 1e+99                 1e+99
       rth0                     0                     0                     0
       cth0                 1e-05                 1e-05                 1e-05
         lm                     0                     0                     0
         lp                     0                     0                     0
         wm                     0                     0                     0
         wp                     0                     0                     0
        xom                 10000                 10000                 10000
        xoi                 10000                 10000                 10000
         xm                     0                     0                     0
         xp                     0                     0                     0
         xw                     0                     0                     0

 Diode models (Junction Diode model)
      model xintegrated_circuit11 xintegrated_circuit11

      level                     1                     1
         is                 1e-14                 1e-16
        jsw                     0                     0
         rs                     0                     0
        rsw                     0                     0
        trs                     0                     0
       trs2                     0                     0
          n                  0.01                     1
         ns                     1                     1
         tt                     0                     0
       ttt1                     0                     0
       ttt2                     0                     0
        cjo                     0                     0
         vj                     1                     1
          m                   0.5                   0.5
        tm1                     0                     0
        tm2                     0                     0
        cjp                     0                     0
        php                     1                     1
       mjsw                  0.33                  0.33
        ikf                     0                     0
        ikr                     0                     0
        ikp                     0                     0
        nbv                  0.01                     1
       area                     1                     1
         pj                     0                     0
       tlev                     0                     0
      tlevc                     0                     0
         eg                  1.11                  1.11
       gap1              0.000702              0.000702
       gap2                  1108                  1108
        xti                     3                     3
        cta                     0                     0
        ctp                     0                     0
        tpb                     0                     0
       tphp                     0                     0
       jtun                     0                     0
     jtunsw                     0                     0
       ntun                    30                    30
     xtitun                     3                     3
        keg                     1                     1
         kf                     0                 2e-11
         af                     1                     1
         fc                   0.5                   0.5
        fcs                   0.5                   0.5
         bv                    60                     0
        ibv                 0.001                 0.001
        tcv                     0   
[truncated]
```

## 08_ngspice_stderr.txt
```text
Note: Starting dynamic gmin stepping
Warning: Dynamic gmin stepping failed
Note: Starting true gmin stepping
Warning: True gmin stepping failed
Note: Starting source stepping
Note: Source stepping completed
Note: Starting dynamic gmin stepping
Warning: Dynamic gmin stepping failed
Note: Starting true gmin stepping
Warning: True gmin stepping failed
Note: Starting source stepping
Note: Source stepping completed

```

## 10_diagnostic_context.json
```text
{
  "source_format": "pipeline2.0_diagnostic_context_manifest",
  "batch_name": "batchICChatAgentEvaluation",
  "experiment_name": "ic_chat_agent_evaluation",
  "circuit_id": "ic02",
  "user_problem": "L’audio si sente ma il volume è troppo basso. Quali controlli e prove posso fare, senza modificare il segnale di ingresso, per capire la causa e aumentare il volume?",
  "pipeline2_output_dir": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic02",
  "summary": {
    "spice_status": "success",
    "spice_exit_code": 0,
    "spice_message": "ngspice completed successfully.",
    "emitted_elements": 20,
    "skipped_elements": 12,
    "emit_warnings_count": 0,
    "skipped_components_count": 12,
    "node_count": 12,
    "ground_groups_count": 9,
    "singleton_nodes_count": 0,
    "bound_components": 16,
    "missing_components": 0,
    "unsupported_components": 1,
    "spice_ready_components": 17,
    "rules_missing_components": 0,
    "has_tran_csv": true,
    "has_tran_plot": true,
    "led_profiles": {}
  },
  "artifacts": {
    "graph": {
      "step": "01",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic02\\01_graph.json",
      "role": "Graph JSON copied from Pipeline 1.0."
    },
    "normalized_circuit": {
      "step": "02",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic02\\02_normalized_circuit.json",
      "role": "Normalized circuit representation used by Pipeline 2.0."
    },
    "node_map": {
      "step": "03",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic02\\03_node_map.json",
      "role": "Maps component terminals to SPICE node names."
    },
    "values_bound": {
      "step": "04",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic02\\04_values_bound.json",
      "role": "Values and labels bound to graph components."
    },
    "component_rules": {
      "step": "06",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic02\\06_component_rules.json",
      "role": "SPICE conversion rules for each component."
    },
    "netlist": {
      "step": "07",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic02\\07_netlist.cir",
      "role": "Generated SPICE netlist."
    },
    "spice_emit_report": {
      "step": "07",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic02\\07_spice_emit_report.json",
      "role": "Report of emitted, skipped and warning components."
    },
    "spice_run": {
      "step": "08",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic02\\08_spice_run.json",
      "role": "Structured ngspice execution report."
    },
    "ngspice_stdout": {
      "step": "08",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic02\\08_ngspice_stdout.txt",
      "role": "Raw ngspice stdout log."
    },
    "ngspice_stderr": {
      "step": "08",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic02\\08_ngspice_stderr.txt",
      "role": "Raw ngspice stderr log."
    },
    "tran_csv": {
      "step": "08",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic02\\08_tran.csv",
      "role": "Clean transient CSV, when .tran data is available."
    },
    "tran_plot_png": {
      "step": "08",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic02\\08_tran_plot.png",
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
    "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\input\\images\\ic02.jpg",
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
