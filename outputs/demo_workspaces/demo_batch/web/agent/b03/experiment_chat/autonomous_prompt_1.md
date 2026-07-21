# Pipeline 2.0 - agente diagnostico autonomo controllato

Sei il controller diagnostico di una pipeline Graph JSON -> SPICE/ngspice.
Devi scegliere il prossimo test controllato oppure fermarti con una conclusione.

## Sintomo utente
Nella base run a 12 V è acceso solo il LED giallo. Voglio verificare prima, con prove statiche separate, il comportamento a batteria scarica e a batteria molto carica. Solo dopo esegui una singola rampa transitoria per mostrare il passaggio tra gli stati. Mantieni invariati Graph JSON e topologia e concludi usando le evidenze SPICE.

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
- Inserisci in expect soltanto i comportamenti indispensabili per verificare
  l'obiettivo o preservare componenti richiesti dall'utente. Le altre misure
  possono restare in compare come osservazioni senza aspettativa.
- Una variazione direzionale minima non dimostra una correzione: per fermare
  il ciclo serve almeno un miglioramento relativo del 10%, oppure una vera
  attivazione/disattivazione del comportamento richiesto.
- Usa expect per descrivere sia l'effetto cercato sia i vincoli da preservare,
  per esempio corrente del target activated e corrente del componente protetto unchanged.
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
- set_initial_node_voltage: type, target, value (solo analysis=tran; condizione iniziale senza sorgente permanente e senza UIC)
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
  "circuit_id": "b03",
  "source_format": "pipeline2.0_node_map",
  "nodes": [
    {
      "node_id": "N001",
      "kind": "normal",
      "terminals": [
        "battery2.1_negative",
        "diode7.5_anode",
        "led12.3_cathode",
        "npn_transistor18.1_E",
        "npn_transistor18.2_E",
        "resistor22.5_t2"
      ],
      "terminal_count": 6
    },
    {
      "node_id": "N002",
      "kind": "normal",
      "terminals": [
        "battery2.1_positive",
        "diode7.3_anode",
        "led12.1_anode",
        "led12.2_anode",
        "npn_transistor18.3_E",
        "resistor22.8_t1"
      ],
      "terminal_count": 6
    },
    {
      "node_id": "N003",
      "kind": "normal",
      "terminals": [
        "diode7.1_anode",
        "npn_transistor18.3_C",
        "resistor22.6_t1"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N004",
      "kind": "normal",
      "terminals": [
        "diode7.1_cathode",
        "led12.2_cathode",
        "resistor22.3_t1"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N005",
      "kind": "normal",
      "terminals": [
        "diode7.2_anode",
        "resistor22.4_t2",
        "resistor22.5_t1"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N006",
      "kind": "normal",
      "terminals": [
        "diode7.2_cathode",
        "diode7.4_cathode"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N007",
      "kind": "normal",
      "terminals": [
        "diode7.3_cathode",
        "diode7.4_anode"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N008",
      "kind": "normal",
      "terminals": [
        "diode7.5_cathode",
        "diode7.7_cathode"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N009",
      "kind": "normal",
      "terminals": [
        "diode7.6_anode",
        "resistor22.7_t2",
        "resistor22.8_t2"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N010",
      "kind": "normal",
      "terminals": [
        "diode7.6_cathode",
        "diode7.7_anode"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N011",
      "kind": "normal",
      "terminals": [
        "led12.1_cathode",
        "resistor22.1_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N012",
      "kind": "normal",
      "terminals": [
        "led12.3_anode",
        "resistor22.6_t2"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N013",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.1_B",
        "resistor22.2_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N014",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.1_C",
        "resistor22.1_t2"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N015",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.2_B",
        "resistor22.4_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N016",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.2_C",
        "resistor22.2_t2",
        "resistor22.3_t2"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N017",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.3_B",
        "resistor22.7_t1"
      ],
      "terminal_count": 2
    }
  ],
  "terminal_to_node": {
    "battery2.1_negative": "N001",
    "battery2.1_positive": "N002",
    "diode7.1_anode": "N003",
    "diode7.1_cathode": "N004",
    "diode7.2_anode": "N005",
    "diode7.2_cathode": "N006",
    "diode7.3_anode": "N002",
    "diode7.3_cathode": "N007",
    "diode7.4_anode": "N007",
    "diode7.4_cathode": "N006",
    "diode7.5_anode": "N001",
    "diode7.5_cathode": "N008",
    "diode7.6_anode": "N009",
    "diode7.6_cathode": "N010",
    "diode7.7_anode": "N010",
    "diode7.7_cathode": "N008",
    "led12.1_anode": "N002",
    "led12.1_cathode": "N011",
    "led12.2_anode": "N002",
    "led12.2_cathode": "N004",
    "led12.3_anode": "N012",
    "led12.3_cathode": "N001",
    "npn_transistor18.1_B": "N013",
    "npn_transistor18.1_C": "N014",
    "npn_transistor18.1_E": "N001",
    "npn_transistor18.2_B": "N015",
    "npn_transistor18.2_C": "N016",
    "npn_transistor18.2_E": "N001",
    "npn_transistor18.3_B": "N017",
    "npn_transistor18.3_C": "N003",
    "npn_transistor18.3_E": "N002",
    "resistor22.1_t1": "N011",
    "resistor22.1_t2": "N014",
    "resistor22.2_t1": "N013",
    "resistor22.2_t2": "N016",
    "resistor22.3_t1": "N004",
    "resistor22.3_t2": "N016",
    "resistor22.4_t1": "N015",
    "resistor22.4_t2": "N005",
    "resistor22.5_t1": "N005",
    "resistor22.5_t2": "N001",
    "resistor22.6_t1": "N003",
    "resistor22.6_t2": "N012",
    "resistor22.7_t1": "N017",
    "resistor22.7_t2": "N009",
    "resistor22.8_t1": "N002",
    "resistor22.8_t2": "N009"
  },
  "component_terminal_nodes": {
    "battery2.1": {
      "positive": "N002",
      "negative": "N001"
    },
    "diode7.1": {
      "cathode": "N004",
      "anode": "N003"
    },
    "diode7.2": {
      "cathode": "N006",
      "anode": "N005"
    },
    "diode7.3": {
      "anode": "N002",
      "cathode": "N007"
    },
    "diode7.4": {
      "anode": "N007",
      "cathode": "N006"
    },
    "diode7.5": {
      "cathode": "N008",
      "anode": "N001"
    },
    "diode7.6": {
      "anode": "N009",
      "cathode": "N010"
    },
    "diode7.7": {
      "anode": "N010",
      "cathode": "N008"
    },
    "led12.1": {
      "anode": "N002",
      "cathode": "N011"
    },
    "led12.2": {
      "anode": "N002",
      "cathode": "N004"
    },
    "led12.3": {
      "anode": "N012",
      "cathode": "N001"
    },
    "npn_transistor18.1": {
      "B": "N013",
      "C": "N014",
      "E": "N001"
    },
    "npn_transistor18.2": {
      "B": "N015",
      "C": "N016",
      "E": "N001"
    },
    "npn_transistor18.3": {
      "B": "N017",
      "E": "N002",
      "C": "N003"
    },
    "resistor22.1": {
      "t1": "N011",
      "t2": "N014"
    },
    "resistor22.2": {
      "t1": "N013",
      "t2": "N016"
    },
    "resistor22.3": {
      "t1": "N004",
      "t2": "N016"
    },
    "resistor22.4": {
      "t1": "N015",
      "t2": "N005"
    },
    "resistor22.5": {
      "t1": "N005",
      "t2": "N001"
    },
    "resistor22.6": {
      "t1": "N003",
      "t2": "N012"
    },
    "resistor22.7": {
      "t1": "N017",
      "t2": "N009"
    },
    "resistor22.8": {
      "t1": "N002",
      "t2": "N009"
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
    "nodes_count": 17,
    "normal_nodes_count": 17,
    "ground_nodes_count": 0,
    "ground_groups_count": 0,
    "terminal_to_node_count": 47,
    "singleton_nodes_count": 0
  }
}

```

## 06_component_rules.json
```text
{
  "circuit_id": "b03",
  "source_format": "pipeline2.0_component_rules",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\data\\batchDemo\\values\\b03_values.yaml",
  "spice_classes_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_spice_classes.yaml",
  "supplies": {
    "VREF_B": {
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
        "label_text": "B: riferimento SPICE 0 V",
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
        "value": 12,
        "unit": "V",
        "source": "manual_from_original_circuit_context",
        "label_text": "batteria automobilistica nominale 12 V tra A e B"
      }
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
        "N003",
        "N004"
      ],
      "parameters": {
        "model": "D_1N4148_TYP",
        "source": "manual_from_image_label",
        "label_text": "D3 1N4148"
      }
    },
    "diode7.2": {
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
        "N005",
        "N006"
      ],
      "parameters": {
        "model": "BZX79C10_TYP",
        "source": "manual_from_image_label",
        "label_text": "D6 BZX79C10 zener 10 V",
        "viewer_override": {
          "visual_class": "zener",
          "label": "D6",
          "display_value": "BZX79C10 10 V"
        }
      }
    },
    "diode7.3": {
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
        "N002",
        "N007"
      ],
      "parameters": {
        "model": "D_1N4148_TYP",
        "source": "manual_from_image_label",
        "label_text": "D4 1N4148"
      }
    },
    "diode7.4": {
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
        "N007",
        "N006"
      ],
      "parameters": {
        "model": "D_1N4148_TYP",
        "source": "manual_from_image_label",
        "label_text": "D5 1N4148"
      }
    },
    "diode7.5": {
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
        "N008"
      ],
      "parameters": {
        "model": "BZX79C12_TYP",
        "source": "manual_from_image_label",
        "label_text": "D10 BZX79C12 zener 12 V",
        "viewer_override": {
          "visual_class": "zener",
          "label": "D10",
          "display_value": "BZX79C12 12 V"
        }
      }
    },
    "diode7.6": {
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
        "N009",
        "N010"
      ],
      "parameters": {
        "model": "D_1N4148_TYP",
        "source": "manual_from_image_label",
        "label_text": "D8 1N4148"
      }
    },
    "diode7.7": {
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
        "N010",
        "N008"
      ],
      "parameters": {
        "model": "D_1N4148_TYP",
        "source": "manual_from_image_label",
        "label_text": "D9 1N4148"
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
        "N011"
      ],
      "parameters": {
        "model": "LED_RED_TYP",
        "source": "manual_from_image_color",
        "label_text": "D1 LED rosso"
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
        "model": "LED_YELLOW_TYP",
        "source": "manual_from_image_color",
        "label_text": "D2 LED giallo"
      }
    },
    "led12.3": {
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
        "N012",
        "N001"
      ],
      "parameters": {
        "model": "LED_GREEN_TYP",
        "source": "manual_from_image_color",
        "label_text": "D7 LED verde"
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
        "N014",
        "N013",
        "N001"
      ],
      "parameters": {
        "model": "BC547_TYP",
        "source": "manual_from_image_label",
        "label_text": "Q1 BC547 NPN"
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
        "N016",
        "N015",
        "N001"
      ],
      "parameters": {
        "model": "BC547_TYP",
        "source": "manual_from_image_label",
        "label_text": "Q2 BC547 NPN"
      }
    },
    "npn_transistor18.3": {
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
        "N003",
        "N017",
        "N002"
      ],
      "parameters": {
        "model": "BC557_TYP",
        "source": "manual_from_image_label_semantic_correction",
        "label_text": "Q3 BC557 PNP"
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
        "N014"
      ],
      "parameters": {
        "value": 1,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R1 1 kohm"
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
        "N013",
        "N016"
      ],
      "parameters": {
        "value": 100,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R2 100 kohm"
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
        "N004",
        "N016"
      ],
      "parameters": {
        "value": 1,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R3 1 kohm"
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
        "N015",
        "N005"
      ],
      "parameters": {
        "value": 3.3,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R4 3.3 kohm"
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
        "N005",
        "N001"
      ],
      "parameters": {
        "value": 3.3,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R5 3.3 kohm"
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
        "N003",
        "N012"
      ],
      "parameters": {
        "value": 1,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R6 1 kohm"
      }
    },
    "resistor22.7": {
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
        "N017",
        "N009"
      ],
      "parameters": {
        "value": 3.3,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R7 3.3 kohm"
      }
    },
    "resistor22.8": {
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
        "N009"
      ],
      "parameters": {
        "value": 3.3,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R8 3.3 kohm"
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
    "components_total": 22,
    "spice_ready_components": 22,
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
* circuit: b03

VVREF_B N001 0 DC 0
Vbattery2_1 N002 N001 DC 12
Ddiode7_1 N003 N004 D_1N4148_TYP
Ddiode7_2 N005 N006 BZX79C10_TYP
Ddiode7_3 N002 N007 D_1N4148_TYP
Ddiode7_4 N007 N006 D_1N4148_TYP
Ddiode7_5 N001 N008 BZX79C12_TYP
Ddiode7_6 N009 N010 D_1N4148_TYP
Ddiode7_7 N010 N008 D_1N4148_TYP
Dled12_1 N002 N011 LED_RED_TYP
Dled12_2 N002 N004 LED_YELLOW_TYP
Dled12_3 N012 N001 LED_GREEN_TYP
Qnpn_transistor18_1 N014 N013 N001 BC547_TYP
Qnpn_transistor18_2 N016 N015 N001 BC547_TYP
Qnpn_transistor18_3 N003 N017 N002 BC557_TYP
Rresistor22_1 N011 N014 1k
Rresistor22_2 N013 N016 100k
Rresistor22_3 N004 N016 1k
Rresistor22_4 N015 N005 3.3k
Rresistor22_5 N005 N001 3.3k
Rresistor22_6 N003 N012 1k
Rresistor22_7 N017 N009 3.3k
Rresistor22_8 N002 N009 3.3k

.model BC547_TYP NPN(BF=250 VAF=50 IKF=100m)
.model BC557_TYP PNP(BF=250 VAF=50 IKF=100m)
.model BZX79C10_TYP D(BV=10 IBV=5m NBV=1.7)
.model BZX79C12_TYP D(BV=12 IBV=5m NBV=1.9)
.model D_1N4148_TYP D(IS=6n N=1.9 RS=0.65 BV=100 IBV=100u TT=4n CJO=4p)
.model LED_GREEN_TYP D(IS=1e-18 N=2 RS=10)
.model LED_RED_TYP D(IS=1e-15 N=2 RS=10)
.model LED_YELLOW_TYP D(IS=1e-17 N=2 RS=10)

.op
.save all
.tran 1ms 3s

.control
set wr_singlescale
set wr_vecnames
save all @ddiode7_1[id] @ddiode7_2[id] @ddiode7_3[id] @ddiode7_4[id] @ddiode7_5[id] @ddiode7_6[id] @ddiode7_7[id] @dled12_1[id] @dled12_2[id] @dled12_3[id]
run
wrdata 08_tran.csv time v(N001) v(N002) v(N003) v(N004) v(N005) v(N006) v(N007) v(N008) v(N009) v(N010) v(N011) v(N012) v(N013) v(N014) v(N015) v(N016) v(N017) @ddiode7_1[id] @ddiode7_2[id] @ddiode7_3[id] @ddiode7_4[id] @ddiode7_5[id] @ddiode7_6[id] @ddiode7_7[id] @dled12_1[id] @dled12_2[id] @dled12_3[id]
.endc
.end

```

## 07_spice_emit_report.json
```text
{
  "circuit_id": "b03",
  "source_format": "pipeline2.0_spice_emit_report",
  "emitted_elements": 23,
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
      "N008",
      "N009",
      "N010",
      "N011",
      "N012",
      "N013",
      "N014",
      "N015",
      "N016",
      "N017"
    ],
    "device_currents": [
      "@ddiode7_1[id]",
      "@ddiode7_2[id]",
      "@ddiode7_3[id]",
      "@ddiode7_4[id]",
      "@ddiode7_5[id]",
      "@ddiode7_6[id]",
      "@ddiode7_7[id]",
      "@dled12_1[id]",
      "@dled12_2[id]",
      "@dled12_3[id]"
    ]
  },
  "models": [
    "BC547_TYP",
    "BC557_TYP",
    "BZX79C10_TYP",
    "BZX79C12_TYP",
    "D_1N4148_TYP",
    "LED_GREEN_TYP",
    "LED_RED_TYP",
    "LED_YELLOW_TYP"
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
n002                                        12
n003                                   1.16486
n004                                   10.1142
n005                                   1.02973
n006                                   10.9153
n007                                   11.4577
n008                                   11.5524
n009                                   11.9982
n010                                   11.7753
n011                                   11.4819
n012                                   1.16486
n014                                   11.4819
n013                                  0.172628
n016                                  0.172626
n015                                  0.836539
n017                                   11.9982
vbattery2_1#branch                  -0.0103127
vvref_b#branch                    -2.36532e-11


No. of Data Rows : 3008
Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

No. of Data Rows : 1

Initial Transient Solution
--------------------------

Node                                   Voltage
----                                   -------
n001                                         0
n002                                        12
n003                                   1.16486
n004                                   10.1142
n005                                   1.02973
n006                                   10.9153
n007                                   11.4577
n008                                   11.5524
n009                                   11.9982
n010                                   11.7753
n011                                   11.4819
n012                                   1.16486
n014                                   11.4819
n013                                  0.172628
n016                                  0.172626
n015                                  0.836539
n017                                   11.9982
vbattery2_1#branch                  -0.0103127
vvref_b#branch                    -2.36532e-11


No. of Data Rows : 3008
	Node                                  Voltage
	----                                  -------
	----	-------
	n017                             1.199817e+01
	n015                             8.365391e-01
	n016                             1.726265e-01
	n013                             1.726276e-01
	n014                             1.148190e+01
	n012                             1.164859e+00
	n011                             1.148190e+01
	n010                             1.177528e+01
	n009                             1.199817e+01
	n008                             1.155238e+01
	n007                             1.145765e+01
	n006                             1.091531e+01
	n005                             1.029726e+00
	n004                             1.011420e+01
	n003                             1.164865e+00
	n002                             1.200000e+01
	n001                             0.000000e+00

	Source	Current
	------	-------

	@dled12_3[id]                    6.019785e-09
	@dled12_2[id]                    9.941582e-03
	@dled12_1[id]                    2.288834e-11
	@ddiode7_7[id]                   5.536755e-07
	@ddiode7_6[id]                   5.536755e-07
	@ddiode7_5[id]                   -5.53676e-07
	@ddiode7_4[id]                   3.705798e-04
	@ddiode7_3[id]                   3.705798e-04
	@ddiode7_2[id]                   -3.70580e-04
	@ddiode7_1[id]                   -6.00895e-09
	vvref_b#branch                   -2.36532e-11
	vbattery2_1#branch               -1.03127e-02

 BJT models (Bipolar Junction Transistor)
      model             bc557_typ             bc547_typ

       type                   pnp                   npn
       tnom                    27                    27
         is                 1e-16                 1e-16
        ibe                     0                     0
        ibc                     0                     0
         bf                   250                   250
         nf                     1                     1
        vaf                    50                    50
        ikf                   0.1                   0.1
        ise                     0                     0
         ne                   1.5                   1.5
         br                     1                     1
         nr                     1                     1
        var                     0                     0
        ikr                     0                     0
        isc                     0                     0
         nc                     2                     2
         rb                     0                     0
        irb                     0                     0
        rbm                     0                     0
         re                     0                     0
         rc                     0                     0
        cje                     0                     0
        vje                  0.75                  0.75
        mje                  0.33                  0.33
         tf                     0                     0
        xtf                     0                     0
        vtf                     0                     0
        itf                     0                     0
        ptf                     0                     0
        cjc                     0                     0
        vjc                  0.75                  0.75
        mjc                  0.33                  0.33
       xcjc                     1                     1
         tr                     0                     0
        cjs                     0                     0
        vjs                  0.75                  0.75
        mjs                     0                     0
        xtb                     0                     0
         eg                  1.11                  1.11
        xti                     3                     3
         fc                   0.5                   0.5
         kf                     0                     0
         af                     0                     0
        iss                     0                     0
         ns                     1                     1
        rco                  0.01                  0.01
         vo                    10                    10
      gamma                 1e-11                 1e-11
        qco                     0                     0
       tlev                     0                     0
      tlevc                     0                     0
       tbf1                     0                     0
       tbf2                     0                     0
       tbr1                     0                     0
       tbr2                     0                     0
      tikf1                     0                     0
      tikf2                     0                     0
      tikr1                     0                     0
      tikr2                     0                     0
      tirb1                     0                     0
      tirb2                     0                     0
       tnc1                     0                     0
       tnc2                     0                     0
       tne1                     0                     0
       tne2                     0                     0
       tnf1                     0                     0
       tnf2                     0                     0
       tnr1                     0                     0
       tnr2                     0                     0
       trb1                     0                     0
       trb2                     0                     0
       trc1                     0                     0
       trc2                     0                     0
       tre1                     0                     0
       tre2                     0                     0
       trm1                     0                     0
       trm2                     0                     0
      tvaf1                     0                     0
      tvaf2                     0                     0
      tvar1                     0                     0
      tvar2                     0                     0
        ctc                     0                     0
        cte                     0                     0
        cts                     0                     0
       tvjc                     0                     0
       tvje                     0                     0
       tvjs                     0                     0
      titf1                     0                     0
      titf2                     0                     0
       ttf1                     0                     0
       ttf2                     0                     0
       ttr1                     0                     0
       ttr2                     0                     0
      tmje1                     0                     0
      tmje2                     0                     0
      tmjc1                     0                     0
      tmjc2                     0                     0
      tmjs1                     0                     0
      tmjs2                     0                     0
       tns1                     0                     0
       tns2                     0                     0
        nkf                   0.5                   0.5
       tis1                     0                     0
       tis2                     0                     0
      tise1                     0                     0
      tise2                     0                     0
      tisc1                     0                     0
      tisc2                     0                     0
      tiss1                     0                     0
      tiss2                     0                     0
   quasimod                     0                     0
         vg                 1.206                 1.206
         cn                   2.2                  2.42
          d                  0.52                  0.87
    vbe_max                 1e+99                 1e+99
    vbc_max                 1e+99                 1e+99
    vce_max                 1e+99                 1e+99
     pd_max                 1e+99                 1e+99
     ic_max                 1e+99                 1e+99
     ib_max                 1e+99                 1e+99
     te_max                 1e+99                 1e+99
       rth0                     0                     0

 Diode models (Junction Diode model)
      model         led_green_typ        led_yellow_typ           led_red_typ

      level                     1                     1                     1
         is                 1e-18                 1e-17                 1e-15
        jsw                     0                     0                     0
         rs                    10                    10                    10
        rsw                     0                     0                     0
        trs                     0                     0                     0
       trs2                     0                     0                     0
          n                     2                     2                     2
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
        nbv                     2                     2                     2
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
         bv                     0                     0                     0
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
      model          bzx79c12_typ          bzx79c10_typ          d_1n4148_typ

      level                     1                     1                     1
         is                 1e-14                 1e-14                 6e-09
        jsw                     0                     0                     0
         rs                     0                     0                  0.65
        rsw                     0                     0                     0
        trs                     0                     0                     0
       trs2                     0                     0                     0
          n                     1                     1                   1.9
         ns                     1                     1                     1
         tt                     0                     0                 4e-09
       ttt1                     0                     0                     0
       ttt2                     0                     0                     0
        cjo                     0                     0                 4e-12
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
        nbv                   1.9                   1.7                   1.9
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
         bv                    12                    10                   100
        ibv                 0.005                 0.005                0.0001
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
     device   qnpn_transistor18_3   qnpn_transistor18_2   qnpn_transistor18_1
      model             bc557_typ             bc547_typ             bc547_typ
         ic          -1.08335e-11            0.00994158           1.14064e-11
         ib          -1.16659e-12           5.85416e-05          -1.11364e-11
         ie           1.95788e-15            -0.0100001          -1.17519e-11
        vbe            0.00182728              0.836539              0.172628
        vbc              -10.8333              0.663913              -11.3093
         gm           5.04612e-15              0.352358           3.75171e-12
        gpi           1.00002e-12            0.00172016           1.01224e-12
        gmu                 1e-12             0.0005432                 1e-12
         gx                     0                     0                     0
         go           2.14641e-18             0.0006886           1.58342e-15
        cpi                     0                     0                     0
        cmu                     0                     0                     0
        cbx                     0                     0                     0
       csub                     0                     0                     0

 Diode: Junction Diode model
     device              dled12_3              dled12_2              dled12_1
      model         led_green_typ        led_yellow_typ           led_red_typ
    thermal                     0                     0                     0
         vd               1.16486               1.78638              0.518102
         id           6.01978e-09            0.00994158           2.28883e-11
         gd           1.16348e-07              0.192183           4.33463e-10
         cd                     0                     0                     0

 Diode: Junction Diode model
     device             ddiode7_5             ddiode7_2             ddiode7_7
      model          bzx79c12_typ          bzx79c10_typ          d_1n4148_typ
    thermal                     0                     0                     0
         vd              -11.5524              -9.88558              0.222894
         id          -5.53676e-07           -0.00037058           5.53676e-07
         gd           1.12663e-05            0.00842795           1.13993e-05
         cd                     0                     0           4.58309e-12

 Diode: Junction Diode model
     device             ddiode7_6             ddiode7_4             ddiode7_3
      model          d_1n4148_typ          d_1n4148_typ          d_1n4148_typ
    thermal                     0                     0                     0
         vd              0.222894              0.542104              0.542104
         id           5.53676e-07            0.00037058            0.00037058
         gd           1.13993e-05              0.007541              0.007541
         cd           4.58309e-12           3.60587e-11           3.60587e-11

 Diode: Junction Diode model
     device             ddiode7_1
      model          d_1n4148_typ
    thermal                     0
         vd              -8.94934
         id          -6.00895e-09
         gd           2.95013e-09
         cd           1.26813e-12

 Resistor: Simple linear resistor
     device         rresistor22_8         rresistor22_7         rresistor22_6
      model                     R                     R                     R
 resistance                  3300                  3300                  1000
         ac                  3300                  3300                  1000
      dtemp                     0                     0                     0
     bv_max                 1e+99                 1e+99                 1e+99
      noisy                     1                     1                     1
          i           5.53698e-07          -2.28298e-11           6.01978e-09
          p           1.01172e-09           1.71995e-18           3.62378e-14

 Resistor: Simple linear resistor
     device         rresistor22_5         rresistor22_4         rresistor22_3
      model                     R                     R                     R
 resistance                  3300                  3300                  1000
         ac                  3300                  3300                  1000
      dtemp                     0                     0                     0
     bv_max                 1e+99                 1e+99                 1e+99
      noisy                     1                     1                     1
          i           0.000312038          -5.85416e-05            0.00994158
          p           0.000321314           1.13095e-05             0.0988349

 Resistor: Simple linear resistor
     device         rresistor22_2         rresistor22_1
      model                     R                     R
 resistance                100000                  1000
         ac                100000                  1000
      dtemp                     0                     0
     bv_max                 1e+99                 1e+99
      noisy                     1                     1
          i           1.11364e-11           2.28883e-11
          p            1.2402e-17           5.23877e-19

 Vsource: Independent voltage source
     device           vbattery2_1               vvref_b
         dc                    12                     0
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
          i            -0.0103127          -2.36478e-11
          p             -0.123753                    -0


Total analysis time (seconds) = 0.0372972

Total elapsed time (seconds) = 0.107 

Total DRAM available = 32239.535 MB.
DRAM currently available = 14329.281 MB.
Maximum ngspice program size =   16.891 MB.
Current ngspice program size =   16.617 MB.


```

## 08_ngspice_stderr.txt
```text

```

## 10_diagnostic_context.json
```text
{
  "source_format": "pipeline2.0_diagnostic_context_manifest",
  "batch_name": "batchDemo",
  "experiment_name": "demo_batch",
  "circuit_id": "b03",
  "user_problem": "Nella base run a 12 V è acceso solo il LED giallo. Voglio verificare prima, con prove statiche separate, il comportamento a batteria scarica e a batteria molto carica. Solo dopo esegui una singola rampa transitoria per mostrare il passaggio tra gli stati. Mantieni invariati Graph JSON e topologia e concludi usando le evidenze SPICE.",
  "pipeline2_output_dir": "outputs\\demo_workspaces\\demo_batch\\web\\agent\\b03",
  "summary": {
    "spice_status": "success",
    "spice_exit_code": 0,
    "spice_message": "ngspice completed successfully.",
    "emitted_elements": 23,
    "skipped_elements": 0,
    "emit_warnings_count": 0,
    "skipped_components_count": 0,
    "node_count": 17,
    "ground_groups_count": 0,
    "singleton_nodes_count": 0,
    "bound_components": 22,
    "missing_components": 0,
    "unsupported_components": 0,
    "spice_ready_components": 22,
    "rules_missing_components": 0,
    "has_tran_csv": true,
    "has_tran_plot": true,
    "led_profiles": {
      "Dled12_1": {
        "state": "off",
        "regular_period": false,
        "frequency_hz": null,
        "duty_cycle": 0.0,
        "on_fraction": 0.0,
        "pulse_count": 0,
        "voltage_min": 0.5181018000000002,
        "voltage_max": 0.5181018000000002,
        "anode_node": "N002",
        "cathode_node": "N011"
      },
      "Dled12_2": {
        "state": "steady_on",
        "regular_period": false,
        "frequency_hz": null,
        "duty_cycle": 1.0,
        "on_fraction": 1.0,
        "pulse_count": 1,
        "voltage_min": 1.8857979,
        "voltage_max": 1.8857979,
        "anode_node": "N002",
        "cathode_node": "N004"
      },
      "Dled12_3": {
        "state": "off",
        "regular_period": false,
        "frequency_hz": null,
        "duty_cycle": 0.0,
        "on_fraction": 0.0,
        "pulse_count": 0,
        "voltage_min": 1.16485884,
        "voltage_max": 1.16485887,
        "anode_node": "N012",
        "cathode_node": "N001"
      }
    }
  },
  "artifacts": {
    "graph": {
      "step": "01",
      "available": true,
      "path": "outputs\\demo_workspaces\\demo_batch\\web\\agent\\b03\\01_graph.json",
      "role": "Graph JSON copied from Pipeline 1.0."
    },
    "normalized_circuit": {
      "step": "02",
      "available": true,
      "path": "outputs\\demo_workspaces\\demo_batch\\web\\agent\\b03\\02_normalized_circuit.json",
      "role": "Normalized circuit representation used by Pipeline 2.0."
    },
    "node_map": {
      "step": "03",
      "available": true,
      "path": "outputs\\demo_workspaces\\demo_batch\\web\\agent\\b03\\03_node_map.json",
      "role": "Maps component terminals to SPICE node names."
    },
    "values_bound": {
      "step": "04",
      "available": true,
      "path": "outputs\\demo_workspaces\\demo_batch\\web\\agent\\b03\\04_values_bound.json",
      "role": "Values and labels bound to graph components."
    },
    "component_rules": {
      "step": "06",
      "available": true,
      "path": "outputs\\demo_workspaces\\demo_batch\\web\\agent\\b03\\06_component_rules.json",
      "role": "SPICE conversion rules for each component."
    },
    "netlist": {
      "step": "07",
      "available": true,
      "path": "outputs\\demo_workspaces\\demo_batch\\web\\agent\\b03\\07_netlist.cir",
      "role": "Generated SPICE netlist."
    },
    "spice_emit_report": {
      "step": "07",
      "available": true,
      "path": "outputs\\demo_workspaces\\demo_batch\\web\\agent\\b03\\07_spice_emit_report.json",
      "role": "Report of emitted, skipped and warning components."
    },
    "spice_run": {
      "step": "08",
      "available": true,
      "path": "outputs\\demo_workspaces\\demo_batch\\web\\agent\\b03\\08_spice_run.json",
      "role": "Structured ngspice execution report."
    },
    "ngspice_stdout": {
      "step": "08",
      "available": true,
      "path": "outputs\\demo_workspaces\\demo_batch\\web\\agent\\b03\\08_ngspice_stdout.txt",
      "role": "Raw ngspice stdout log."
    },
    "ngspice_stderr": {
      "step": "08",
      "available": true,
      "path": "outputs\\demo_workspaces\\demo_batch\\web\\agent\\b03\\08_ngspice_stderr.txt",
      "role": "Raw ngspice stderr log."
    },
    "tran_csv": {
      "step": "08",
      "available": true,
      "path": "outputs\\demo_workspaces\\demo_batch\\web\\agent\\b03\\08_tran.csv",
      "role": "Clean transient CSV, when .tran data is available."
    },
    "tran_plot_png": {
      "step": "08",
      "available": true,
      "path": "outputs\\demo_workspaces\\demo_batch\\web\\agent\\b03\\08_tran_plot.png",
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
    "path": "outputs\\demo_workspaces\\demo_batch\\input\\images\\b03.jpg",
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
