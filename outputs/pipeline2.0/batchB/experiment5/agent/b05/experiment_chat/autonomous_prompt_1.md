# Pipeline 2.0 - agente diagnostico autonomo controllato

Sei il controller diagnostico di una pipeline Graph JSON -> SPICE/ngspice.
Devi scegliere il prossimo test controllato oppure fermarti con una conclusione.

## Sintomo utente
Ho acceso questa radio, ma nelle cuffie non sento nulla. Puoi trovare il problema e provare a risolverlo?

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
  `op` per tensioni, correnti o potenze lette dal punto di lavoro.
- `tran_vpp` accetta sia `v(NODO)` rispetto a massa sia `v(NODO1,NODO2)` per
  carichi flottanti: nel secondo caso usa la differenza campione per campione.
- Se `measure` non e presente resta valido il comportamento standard: le tensioni
  sono confrontate sul Vpp, mentre correnti e potenze restano osservazioni OP.
- In uno scenario misto puoi usare una corrente come criterio expect soltanto
  dichiarandola esplicitamente con `measure: {"i(R...)":"op"}`.
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
  "circuit_id": "b05",
  "source_format": "pipeline2.0_node_map",
  "nodes": [
    {
      "node_id": "0",
      "kind": "ground",
      "terminals": [
        "battery2.1_positive",
        "gnd9.1_t1",
        "inductor10.1_t2",
        "npn_transistor18.1_E",
        "npn_transistor18.2_E",
        "polarized_capacitor20.1_negative"
      ],
      "terminal_count": 6,
      "source_groups": [
        [
          "battery2.1_positive",
          "gnd9.1_t1",
          "inductor10.1_t2",
          "npn_transistor18.1_E",
          "npn_transistor18.2_E",
          "polarized_capacitor20.1_negative"
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
        "battery2.1_negative",
        "switch25.1_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N003",
      "kind": "normal",
      "terminals": [
        "breaker3.1_t1",
        "npn_transistor18.2_C",
        "polarized_capacitor20.4_positive"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N004",
      "kind": "normal",
      "terminals": [
        "breaker3.1_t2",
        "polarized_capacitor20.4_negative",
        "resistor22.1_t2",
        "resistor22.2_t2",
        "resistor22.3_t2",
        "switch25.1_t2"
      ],
      "terminal_count": 6
    },
    {
      "node_id": "N005",
      "kind": "normal",
      "terminals": [
        "diode7.1_cathode",
        "polarized_capacitor20.2_positive"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N006",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.1_B",
        "polarized_capacitor20.2_negative",
        "resistor22.1_t1"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N007",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.1_C",
        "polarized_capacitor20.3_positive",
        "resistor22.2_t1"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N008",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.2_B",
        "polarized_capacitor20.3_negative",
        "resistor22.3_t1"
      ],
      "terminal_count": 3
    }
  ],
  "terminal_to_node": {
    "antenna1.1_t1": "N001",
    "battery2.1_negative": "N002",
    "battery2.1_positive": "0",
    "breaker3.1_t1": "N003",
    "breaker3.1_t2": "N004",
    "diode7.1_anode": "N001",
    "diode7.1_cathode": "N005",
    "gnd9.1_t1": "0",
    "inductor10.1_t1": "N001",
    "inductor10.1_t2": "0",
    "npn_transistor18.1_B": "N006",
    "npn_transistor18.1_C": "N007",
    "npn_transistor18.1_E": "0",
    "npn_transistor18.2_B": "N008",
    "npn_transistor18.2_C": "N003",
    "npn_transistor18.2_E": "0",
    "polarized_capacitor20.1_negative": "0",
    "polarized_capacitor20.1_positive": "N001",
    "polarized_capacitor20.2_negative": "N006",
    "polarized_capacitor20.2_positive": "N005",
    "polarized_capacitor20.3_negative": "N008",
    "polarized_capacitor20.3_positive": "N007",
    "polarized_capacitor20.4_negative": "N004",
    "polarized_capacitor20.4_positive": "N003",
    "resistor22.1_t1": "N006",
    "resistor22.1_t2": "N004",
    "resistor22.2_t1": "N007",
    "resistor22.2_t2": "N004",
    "resistor22.3_t1": "N008",
    "resistor22.3_t2": "N004",
    "switch25.1_t1": "N002",
    "switch25.1_t2": "N004"
  },
  "component_terminal_nodes": {
    "antenna1.1": {
      "t1": "N001"
    },
    "battery2.1": {
      "positive": "0",
      "negative": "N002"
    },
    "breaker3.1": {
      "t1": "N003",
      "t2": "N004"
    },
    "diode7.1": {
      "anode": "N001",
      "cathode": "N005"
    },
    "gnd9.1": {
      "t1": "0"
    },
    "inductor10.1": {
      "t1": "N001",
      "t2": "0"
    },
    "npn_transistor18.1": {
      "B": "N006",
      "C": "N007",
      "E": "0"
    },
    "npn_transistor18.2": {
      "B": "N008",
      "C": "N003",
      "E": "0"
    },
    "polarized_capacitor20.1": {
      "positive": "N001",
      "negative": "0"
    },
    "polarized_capacitor20.2": {
      "positive": "N005",
      "negative": "N006"
    },
    "polarized_capacitor20.3": {
      "positive": "N007",
      "negative": "N008"
    },
    "polarized_capacitor20.4": {
      "positive": "N003",
      "negative": "N004"
    },
    "resistor22.1": {
      "t1": "N006",
      "t2": "N004"
    },
    "resistor22.2": {
      "t1": "N007",
      "t2": "N004"
    },
    "resistor22.3": {
      "t1": "N008",
      "t2": "N004"
    },
    "switch25.1": {
      "t1": "N002",
      "t2": "N004"
    }
  },
  "warnings": {
    "ground_groups_count": 1,
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
    "nodes_count": 9,
    "normal_nodes_count": 8,
    "ground_nodes_count": 1,
    "ground_groups_count": 1,
    "terminal_to_node_count": 32,
    "singleton_nodes_count": 0
  }
}

```

## 06_component_rules.json
```text
{
  "circuit_id": "b05",
  "source_format": "pipeline2.0_component_rules",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_manual_values\\batchB\\b05_values.yaml",
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
        "0",
        "N002"
      ],
      "parameters": {
        "type": "dc",
        "value": 9,
        "unit": "V",
        "source": "manual_assumption_battery_voltage",
        "label_text": "B1 assunta: 9 V"
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
        "N004"
      ],
      "parameters": {
        "spice_override": {
          "emit_as": "resistive_load",
          "equivalent_resistance": 2,
          "resistance_unit": "kohm",
          "node_order": [
            "t1",
            "t2"
          ],
          "semantic_role": "headset_equivalent"
        },
        "source": "manual_interpretation_headset_from_image",
        "label_text": "Cuffia J1/J2 equivalente: 2 kohm",
        "viewer_override": {
          "visual_class": "headset",
          "label": "Headset J1/J2",
          "display_value": "2 kohm eq."
        },
        "equivalent_resistance": 2,
        "resistance_unit": "kohm"
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
        "N005"
      ],
      "parameters": {
        "model": "D_GENERIC",
        "source": "manual_spice_generic_detector_diode",
        "label_text": "CR1; modello diodo SPICE generico"
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
        "value": 0.00025,
        "unit": "H",
        "source": "manual_assumption_am_tuning_model",
        "label_text": "L1 assunta: 250 uH"
      }
    },
    "npn_transistor18.1": {
      "class_name": "PNP_Transistor",
      "status": "spice_ready",
      "spice_support": "model",
      "spice_prefix": "Q",
      "emit_as": "bjt_pnp",
      "node_order": [
        "C",
        "B",
        "E"
      ],
      "nodes": [
        "N007",
        "N006",
        "0"
      ],
      "parameters": {
        "model": "PNP_GENERIC",
        "source": "manual_validation_pnp_from_image",
        "label_text": "Q1 PNP"
      }
    },
    "npn_transistor18.2": {
      "class_name": "PNP_Transistor",
      "status": "spice_ready",
      "spice_support": "model",
      "spice_prefix": "Q",
      "emit_as": "bjt_pnp",
      "node_order": [
        "C",
        "B",
        "E"
      ],
      "nodes": [
        "N003",
        "N008",
        "0"
      ],
      "parameters": {
        "model": "PNP_GENERIC",
        "source": "manual_validation_pnp_from_image",
        "label_text": "Q2 PNP"
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
        "N001",
        "0"
      ],
      "parameters": {
        "value": 375,
        "unit": "pf",
        "source": "manual_from_image_range_midpoint",
        "label_text": "C1 variabile 250-500 pF; base run a 375 pF",
        "viewer_override": {
          "visual_class": "variable_polarized_capacitor",
          "label": "C1",
          "display_value": "375 pF"
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
        "N005",
        "N006"
      ],
      "parameters": {
        "value": 0.022,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C2 0.022 uF"
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
        "N007",
        "N008"
      ],
      "parameters": {
        "value": 0.022,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C3 0.022 uF"
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
        "N004"
      ],
      "parameters": {
        "value": 0.001,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C4 0.001 uF"
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
        "N006",
        "N004"
      ],
      "parameters": {
        "value": 220,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R1 220 kohm"
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
        "N004"
      ],
      "parameters": {
        "value": 4.7,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R2 4.7 kohm"
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
        "N008",
        "N004"
      ],
      "parameters": {
        "value": 220,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R3 220 kohm"
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
        "N002",
        "N004"
      ],
      "parameters": {
        "state": "open",
        "state_source": "graph_json_state",
        "state_confidence": 0.95,
        "source": "graph_json_state_validated_from_image",
        "label_text": "S1 aperto"
      },
      "strategy": "open_circuit"
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
    "components_total": 16,
    "spice_ready_components": 14,
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
* circuit: b05

Vbattery2_1 0 N002 DC 9
Rbreaker3_1 N003 N004 2k
Ddiode7_1 N001 N005 D_GENERIC
Linductor10_1 N001 0 0.00025
Qnpn_transistor18_1 N007 N006 0 PNP_GENERIC
Qnpn_transistor18_2 N003 N008 0 PNP_GENERIC
Cpolarized_capacitor20_1 N001 0 375p
Cpolarized_capacitor20_2 N005 N006 0.022u
Cpolarized_capacitor20_3 N007 N008 0.022u
Cpolarized_capacitor20_4 N003 N004 0.001u
Rresistor22_1 N006 N004 220k
Rresistor22_2 N007 N004 4.7k
Rresistor22_3 N008 N004 220k
* switch25.1 open: not emitted

.model D_GENERIC D
.model PNP_GENERIC PNP

.op
.save all
.tran 1us 5ms

.control
set wr_singlescale
set wr_vecnames
run
wrdata 08_tran.csv time v(N001) v(N002) v(N003) v(N004) v(N005) v(N006) v(N007) v(N008)
.endc
.end

```

## 07_spice_emit_report.json
```text
{
  "circuit_id": "b05",
  "source_format": "pipeline2.0_spice_emit_report",
  "emitted_elements": 13,
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
      "N008"
    ]
  },
  "models": [
    "D_GENERIC",
    "PNP_GENERIC"
  ],
  "warnings": [
    "antenna1.1: class not yet supported by SPICE emit",
    "switch25.1: open switch not emitted"
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
n002                                        -9
n003                              -3.93119e-24
n004                              -3.93119e-24
n001                                         0
n005                              -1.22429e-16
n007                              -3.93119e-24
n006                              -3.93119e-24
n008                              -3.93119e-24
linductor10_1#branch              -2.24208e-44
vbattery2_1#branch                           0


No. of Data Rows : 5008
Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

No. of Data Rows : 1

Initial Transient Solution
--------------------------

Node                                   Voltage
----                                   -------
n002                                        -9
n003                              -3.93119e-24
n004                              -3.93119e-24
n001                                         0
n005                              -1.22429e-16
n007                              -3.93119e-24
n006                              -3.93119e-24
n008                              -3.93119e-24
linductor10_1#branch              -2.24208e-44
vbattery2_1#branch                           0


No. of Data Rows : 5008
	Node                                  Voltage
	----                                  -------
	----	-------
	n008                             -3.93119e-24
	n006                             -3.93119e-24
	n007                             -3.93119e-24
	n005                             -1.22429e-16
	n001                             0.000000e+00
	n004                             -3.93119e-24
	n003                             -3.93119e-24
	n002                             -9.00000e+00

	Source	Current
	------	-------

	vbattery2_1#branch               0.000000e+00
	linductor10_1#branch             -2.24208e-44

 BJT models (Bipolar Junction Transistor)
      model           pnp_generic

       type                   pnp
       tnom                    27
         is                 1e-16
        ibe                     0
        ibc                     0
         bf                   100
         nf                     1
        vaf                     0
        ikf                     0
        ise                     0
         ne                   1.5
         br                     1
         nr                     1
        var                     0
        ikr                     0
        isc                     0
         nc                     2
         rb                     0
        irb                     0
        rbm                     0
         re                     0
         rc                     0
        cje                     0
        vje                  0.75
        mje                  0.33
         tf                     0
        xtf                     0
        vtf                     0
        itf                     0
        ptf                     0
        cjc                     0
        vjc                  0.75
        mjc                  0.33
       xcjc                     1
         tr                     0
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
         cn                   2.2
          d                  0.52
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
     device   qnpn_transistor18_2   qnpn_transistor18_1
      model           pnp_generic           pnp_generic
         ic           1.22133e-31            1.2211e-31
         ib           1.21231e-33           1.23528e-33
         ie          -3.16655e-29          -3.16655e-29
        vbe          -3.15421e-17          -3.15421e-17
        vbc           8.93671e-24          -1.40386e-23
         gm          -4.73317e-30          -4.73317e-30
        gpi           1.00004e-12           1.00004e-12
        gmu           1.00387e-12           1.00387e-12
         gx                     0                     0
         go           3.86624e-15           3.86624e-15
        cpi                     0                     0
        cmu                     0                     0
        cbx                     0                     0
       csub                     0                     0

 Capacitor: Fixed capacitor
     device cpolarized_capacitor2 cpolarized_capacitor2 cpolarized_capacitor2
      model                     C                     C                     C
capacitance                 1e-09               2.2e-08               2.2e-08
      dtemp                     0                     0                     0
     bv_max                 1e+99                 1e+99                 1e+99
          i          -4.31767e-36           2.24626e-29           1.26415e-28
          p           1.05473e-63           1.98363e-52          -1.54768e-44

 Capacitor: Fixed capacitor
     device cpolarized_capacitor2
      model                     C
capacitance              3.75e-10
      dtemp                     0
     bv_max                 1e+99
          i           3.82726e-29
          p           3.76043e-54

 Diode: Junction Diode model
     device             ddiode7_1
      model             d_generic
    thermal                     0
         vd           9.08868e-17
         id           1.26414e-28
         gd           1.38662e-12
         cd                     0

 Inductor: Fixed inductor
     device         linductor10_1
      model                     L
 inductance               0.00025
      dtemp                     0
         nt                     0
       flux          -4.11716e-32
          v            9.8254e-26
          i          -1.64686e-28
          p          -1.61811e-53

 Resistor: Simple linear resistor
     device         rresistor22_3         rresistor22_2         rresistor22_1
      model                     R                     R                     R
 resistance                220000                  4700                220000
         ac                220000                  4700                220000
      dtemp                     0                     0                     0
     bv_max                 1e+99                 1e+99                 1e+99
      noisy                     1                     1                     1
          i          -4.06225e-29          -2.25847e-29           6.33294e-29
          p           3.63041e-52           2.39732e-54           8.82334e-52

 Resistor: Simple linear resistor
     device           rbreaker3_1
      model                     R
 resistance                  2000
         ac                  2000
      dtemp                     0
     bv_max                 1e+99
      noisy                     1
          i          -1.22141e-31
          p           2.98368e-59

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
          i                     0
          p                     0


Total analysis time (seconds) = 0.0421063

Total elapsed time (seconds) = 0.108 

Total DRAM available = 32239.535 MB.
DRAM currently available = 16190.289 MB.
Maximum ngspice program size =   16.086 MB.
Current ngspice program size =   15.910 MB.


```

## 08_ngspice_stderr.txt
```text

```

## 10_diagnostic_context.json
```text
{
  "source_format": "pipeline2.0_diagnostic_context_manifest",
  "batch_name": "batchB",
  "experiment_name": "experiment5",
  "circuit_id": "b05",
  "user_problem": "Ho acceso questa radio, ma nelle cuffie non sento nulla. Puoi trovare il problema e provare a risolverlo?",
  "pipeline2_output_dir": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b05",
  "summary": {
    "spice_status": "success",
    "spice_exit_code": 0,
    "spice_message": "ngspice completed successfully.",
    "emitted_elements": 13,
    "skipped_elements": 2,
    "emit_warnings_count": 2,
    "skipped_components_count": 2,
    "node_count": 9,
    "ground_groups_count": 1,
    "singleton_nodes_count": 0,
    "bound_components": 14,
    "missing_components": 0,
    "unsupported_components": 1,
    "spice_ready_components": 14,
    "rules_missing_components": 0,
    "has_tran_csv": true,
    "has_tran_plot": true,
    "led_profiles": {}
  },
  "artifacts": {
    "graph": {
      "step": "01",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b05\\01_graph.json",
      "role": "Graph JSON copied from Pipeline 1.0."
    },
    "normalized_circuit": {
      "step": "02",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b05\\02_normalized_circuit.json",
      "role": "Normalized circuit representation used by Pipeline 2.0."
    },
    "node_map": {
      "step": "03",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b05\\03_node_map.json",
      "role": "Maps component terminals to SPICE node names."
    },
    "values_bound": {
      "step": "04",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b05\\04_values_bound.json",
      "role": "Values and labels bound to graph components."
    },
    "component_rules": {
      "step": "06",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b05\\06_component_rules.json",
      "role": "SPICE conversion rules for each component."
    },
    "netlist": {
      "step": "07",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b05\\07_netlist.cir",
      "role": "Generated SPICE netlist."
    },
    "spice_emit_report": {
      "step": "07",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b05\\07_spice_emit_report.json",
      "role": "Report of emitted, skipped and warning components."
    },
    "spice_run": {
      "step": "08",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b05\\08_spice_run.json",
      "role": "Structured ngspice execution report."
    },
    "ngspice_stdout": {
      "step": "08",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b05\\08_ngspice_stdout.txt",
      "role": "Raw ngspice stdout log."
    },
    "ngspice_stderr": {
      "step": "08",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b05\\08_ngspice_stderr.txt",
      "role": "Raw ngspice stderr log."
    },
    "tran_csv": {
      "step": "08",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b05\\08_tran.csv",
      "role": "Clean transient CSV, when .tran data is available."
    },
    "tran_plot_png": {
      "step": "08",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b05\\08_tran_plot.png",
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
    "path": "data\\batchB\\b05.jpg",
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
