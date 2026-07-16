# Pipeline 2.0 - agente diagnostico autonomo controllato

Sei il controller diagnostico di una pipeline Graph JSON -> SPICE/ngspice.
Devi scegliere il prossimo test controllato oppure fermarti con una conclusione.

## Sintomo utente
Il LED dovrebbe lampeggiare in modo chiaramente visibile e regolare. Analizza la base run, individua la causa del duty cycle troppo basso ed esegui autonomamente solo gli scenari necessari per correggerlo.

## Vincoli obbligatori
- Rispondi con un solo oggetto JSON valido, senza Markdown o testo esterno.
- Non inventare nodi, componenti, valori o risultati.
- Usa soltanto queste primitive: add_resistor_between_nodes, add_voltage_source_between_nodes, change_component_value, change_source_value, close_switch, connect_nodes, drive_node_voltage, feed_nodes_from_source_node.
- Ogni scenario deve essere self-contained e partire dalla base run.
- Puoi proporre al massimo 2 scenari indipendenti.
- Budget residuo: 4 run scenario.
- Se il budget e zero devi restituire decision=stop.
- Prima di una conclusione diagnostica devi eseguire almeno uno scenario controllato
  quando il budget e disponibile: la sola base run localizza un sospetto, ma non lo verifica.
- Con budget disponibile usa final_status="resolved" solo dopo uno scenario con
  diagnostic_outcome.status=resolved_candidate e stop_automation=true.
- Puoi invece fermarti con final_status="localized" dopo uno scenario diagnostico
  forte che verifica la causa ma non rappresenta una riparazione del circuito.
- Se il sintomo utente richiede esplicitamente di correggere, risolvere, attivare,
  disattivare o ripristinare un comportamento, `localized` non basta finche resta
  budget: esegui un'altra correzione distinta e sostenuta dagli artefatti.
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
- Se `measure` non e presente resta valido il comportamento standard: le tensioni
  sono confrontate sul Vpp, mentre correnti e potenze restano osservazioni OP.
- In uno scenario misto puoi usare una corrente come criterio expect soltanto
  dichiarandola esplicitamente con `measure: {"i(R...)":"op"}`.
- Un voltmetro VAC, un segnale AC o una tensione alternata devono essere verificati
  con analysis="tran" e `tran_vpp`: un valore DC non dimostra il funzionamento AC.
- Per sintomi di amplificazione o guadagno, ogni scenario con intent="correction" deve includere
  `gain: {"input":"v(NODO_IN)","output":"v(NODO_OUT)"}`; entrambe le
  tensioni devono essere presenti in compare. Valuta il guadagno come
  Vpp(output) / Vpp(input), senza confondere due nodi entrambi di uscita.
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
[
  {
    "decision_number": 1,
    "decision": {
      "decision": "run_scenarios",
      "reason": "La base run mostra che il LED gia lampeggia regolarmente a circa 10 Hz ma con duty cycle estremamente basso (0.0063). Dalla topologia e dai valori emerge un forte sospetto: Rresistor22_3=560 ohm tra ingresso e emettitore introduce una reazione/emitter drive molto forte che alza rapidamente N005 e riduce quasi subito la polarizzazione utile del transistor, lasciando il LED acceso solo per una piccola frazione del periodo. Serve un test controllato di correzione sul valore di questo ramo per verificare se il duty cycle cresce mantenendo la regolarita del lampeggio.",
      "scenarios": [
        {
          "title": "Aumentare R7 per ridurre il trascinamento dell'emettitore e allargare il tempo ON del LED",
          "hypothesis": "Il duty cycle troppo basso e causato principalmente da Rresistor22_3 troppo piccola rispetto a Rresistor22_1 e Rresistor22_4; aumentando R7 diminuisce il sollevamento rapido dell'emettitore e il transistor puo mantenere piu a lungo la conduzione del LED durante ciascun impulso.",
          "intent": "correction",
          "analysis": "tran",
          "actions": [
            {
              "type": "change_component_value",
              "target": "Rresistor22_3",
              "value": "10k"
            }
          ],
          "compare": [
            "v(N003)",
            "v(N004)",
            "v(N005)",
            "i(Rresistor22_3)"
          ],
          "measure": {
            "i(Rresistor22_3)": "op"
          },
          "expect": {
            "v(N003)": "changed",
            "v(N004)": "changed",
            "v(N005)": "changed",
            "i(Rresistor22_3)": "magnitude_decreased"
          },
          "temporal_expect": {
            "target": "Dled12_1",
            "required_state": "blinking",
            "require_regular_period": true,
            "min_duty_cycle": 0.1,
            "min_relative_duty_increase": 10.0
          }
        }
      ]
    },
    "prompt_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a08\\experiment_chat\\autonomous_prompt_1.md",
    "response_paths": [
      "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a08\\experiment_chat\\autonomous_response_1_attempt_1.txt"
    ],
    "scenario_results": [
      {
        "scenario_id": "agent_scenario_1",
        "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a08\\scenarios\\agent_scenario_1",
        "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a08\\scenarios\\agent_scenario_1\\run",
        "status": "spice_success",
        "spice_executed": true,
        "spice_status": "success",
        "spice_exit_code": 0,
        "comparison_summary": {
          "requested_count": 4,
          "changed_count": 4,
          "activated_count": 0,
          "missing_count": 0,
          "expected_count": 4,
          "expectations_met_count": 4,
          "expectations_failed_count": 0,
          "expectations_missing_count": 0,
          "meaningful_improvement_count": 1,
          "quality_required": false,
          "quality_available": false,
          "quality_improved": false,
          "quality_acceptable": false,
          "quality_output_preserved": false,
          "base_thd": null,
          "scenario_thd": null,
          "temporal_required": true,
          "temporal_available": true,
          "temporal_met": true
        },
        "diagnostic_outcome": {
          "status": "resolved_candidate",
          "technical_label": "Transient correction verified",
          "label": "Criteri elettrici e temporali soddisfatti",
          "reason": "Le aspettative elettriche e il profilo transitorio richiesto sono verificati.",
          "user_message": "Lo scenario fornisce una conferma forte dell'ipotesi testata.",
          "stop_automation": true,
          "confidence": "medium",
          "next_step": "La correzione e verificata: puoi passare alla conclusione diagnostica."
        },
        "viewer": {
          "model": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a08\\scenarios\\agent_scenario_1\\run\\13_viewer_model.json",
          "layout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a08\\scenarios\\agent_scenario_1\\run\\14_viewer_layout.json",
          "svg": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a08\\scenarios\\agent_scenario_1\\run\\15_viewer.svg"
        },
        "viewer_error": null,
        "executed_scenarios_count": 1
      }
    ]
  }
]
```

## Evidenze tecniche correnti
## 03_node_map.json
```text
{
  "circuit_id": "a08",
  "source_format": "pipeline2.0_node_map",
  "nodes": [
    {
      "node_id": "0",
      "kind": "ground",
      "terminals": [
        "capacitor4.1_t2",
        "gnd9.1_t1",
        "gnd9.2_t1",
        "resistor22.2_t2",
        "signal_source23.1_t2"
      ],
      "terminal_count": 5,
      "source_groups": [
        [
          "capacitor4.1_t2",
          "gnd9.2_t1",
          "resistor22.2_t2"
        ],
        [
          "gnd9.1_t1",
          "signal_source23.1_t2"
        ]
      ]
    },
    {
      "node_id": "N001",
      "kind": "normal",
      "terminals": [
        "capacitor4.1_t1",
        "resistor22.1_t2",
        "resistor22.4_t1"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N002",
      "kind": "normal",
      "terminals": [
        "led12.1_anode",
        "resistor22.1_t1",
        "resistor22.3_t1",
        "signal_source23.1_t1"
      ],
      "terminal_count": 4
    },
    {
      "node_id": "N003",
      "kind": "normal",
      "terminals": [
        "led12.1_cathode",
        "npn_transistor18.1_C"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N004",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.1_B",
        "resistor22.4_t2"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N005",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.1_E",
        "resistor22.2_t1",
        "resistor22.3_t2"
      ],
      "terminal_count": 3
    }
  ],
  "terminal_to_node": {
    "capacitor4.1_t1": "N001",
    "capacitor4.1_t2": "0",
    "gnd9.1_t1": "0",
    "gnd9.2_t1": "0",
    "led12.1_anode": "N002",
    "led12.1_cathode": "N003",
    "npn_transistor18.1_B": "N004",
    "npn_transistor18.1_C": "N003",
    "npn_transistor18.1_E": "N005",
    "resistor22.1_t1": "N002",
    "resistor22.1_t2": "N001",
    "resistor22.2_t1": "N005",
    "resistor22.2_t2": "0",
    "resistor22.3_t1": "N002",
    "resistor22.3_t2": "N005",
    "resistor22.4_t1": "N001",
    "resistor22.4_t2": "N004",
    "signal_source23.1_t1": "N002",
    "signal_source23.1_t2": "0"
  },
  "component_terminal_nodes": {
    "capacitor4.1": {
      "t1": "N001",
      "t2": "0"
    },
    "gnd9.1": {
      "t1": "0"
    },
    "gnd9.2": {
      "t1": "0"
    },
    "led12.1": {
      "anode": "N002",
      "cathode": "N003"
    },
    "npn_transistor18.1": {
      "B": "N004",
      "C": "N003",
      "E": "N005"
    },
    "resistor22.1": {
      "t1": "N002",
      "t2": "N001"
    },
    "resistor22.2": {
      "t1": "N005",
      "t2": "0"
    },
    "resistor22.3": {
      "t1": "N002",
      "t2": "N005"
    },
    "resistor22.4": {
      "t1": "N001",
      "t2": "N004"
    },
    "signal_source23.1": {
      "t1": "N002",
      "t2": "0"
    }
  },
  "warnings": {
    "ground_groups_count": 2,
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
    "nodes_count": 6,
    "normal_nodes_count": 5,
    "ground_nodes_count": 1,
    "ground_groups_count": 2,
    "terminal_to_node_count": 19,
    "singleton_nodes_count": 0
  }
}

```

## 06_component_rules.json
```text
{
  "circuit_id": "a08",
  "source_format": "pipeline2.0_component_rules",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_manual_values\\batchA\\a08_values.yaml",
  "spice_classes_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_spice_classes.yaml",
  "supplies": {},
  "components": {
    "capacitor4.1": {
      "class_name": "Capacitor",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "C",
      "emit_as": "capacitor",
      "node_order": [
        "t1",
        "t2"
      ],
      "nodes": [
        "N001",
        "0"
      ],
      "parameters": {
        "value": 10,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C1 10 uF"
      }
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
        "model": "LED_RED",
        "source": "manual_from_image_label",
        "label_text": "D1 LTL-307EE"
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
        "N003",
        "N004",
        "N005"
      ],
      "parameters": {
        "model": "2N3904",
        "source": "manual_from_image_label",
        "label_text": "Q1 2N3904"
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
        "N002",
        "N001"
      ],
      "parameters": {
        "value": 10,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R1 10 kOhm"
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
        "N005",
        "0"
      ],
      "parameters": {
        "value": 560,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R6 560 ohm"
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
        "value": 560,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R7 560 ohm"
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
        "N001",
        "N004"
      ],
      "parameters": {
        "value": 68,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R3 68 kOhm"
      }
    },
    "signal_source23.1": {
      "class_name": "Signal_Source",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "V",
      "emit_as": "independent_voltage_source",
      "node_order": [
        "t1",
        "t2"
      ],
      "nodes": [
        "N002",
        "0"
      ],
      "parameters": {
        "type": "pulse",
        "waveform": "square",
        "value": 5,
        "unit": "V",
        "low_value": 0,
        "high_value": 5,
        "delay": 0,
        "rise_time": "1ms",
        "fall_time": "1ms",
        "pulse_width": "50ms",
        "period": "100ms",
        "frequency": 10,
        "frequency_unit": "Hz",
        "source": "manual_assumption_from_image_label",
        "label_text": "V2 square 10 Hz",
        "note": "The image shows square 10 Hz but not the amplitude; 0-5 V is assumed for SPICE."
      }
    }
  },
  "simulation": {
    "analyses": [
      "op",
      "tran"
    ],
    "tran": {
      "step": "0.5ms",
      "stop": "300ms"
    }
  },
  "stats": {
    "components_total": 10,
    "spice_ready_components": 8,
    "not_emitted_components": 2,
    "measurement_components": 0,
    "missing_components": 0,
    "unsupported_components": 0,
    "pin_aware_components": 0,
    "invalid_components": 0,
    "supplies_ready_count": 0
  }
}

```

## 07_netlist.cir
```text
* pipeline2.0 netlist
* circuit: a08

Ccapacitor4_1 N001 0 10u
Dled12_1 N002 N003 LED_RED
Qnpn_transistor18_1 N003 N004 N005 2N3904
Rresistor22_1 N002 N001 10k
Rresistor22_2 N005 0 560
Rresistor22_3 N002 N005 560
Rresistor22_4 N001 N004 68k
Vsignal_source23_1 N002 0 PULSE(0 5 0 1ms 1ms 50ms 100ms)

.model 2N3904 NPN(IS=6.734f BF=416.4 VAF=74.03 IKF=66.78m ISE=6.734f NE=1.259 BR=0.7371 VAR=12.11 IKR=0.0 ISC=0.0 NC=2 RB=10 RC=1 RE=0.1 CJE=4.493p VJE=0.75 MJE=0.2593 CJC=3.638p VJC=0.75 MJC=0.3085 TF=301.2p TR=239.5n)
.model LED_RED D

.op
.save all
.tran 0.5ms 300ms

.control
set wr_singlescale
set wr_vecnames
run
wrdata 08_tran.csv time v(N001) v(N002) v(N003) v(N004) v(N005)
.endc
.end

```

## 07_spice_emit_report.json
```text
{
  "circuit_id": "a08",
  "source_format": "pipeline2.0_spice_emit_report",
  "emitted_elements": 8,
  "skipped_elements": 2,
  "skipped_components": [
    "gnd9.1",
    "gnd9.2"
  ],
  "informational_skips": [
    "gnd9.1: structural component not emitted",
    "gnd9.2: structural component not emitted"
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
      "N005"
    ]
  },
  "models": [
    "2N3904",
    "LED_RED"
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
n001                               4.49946e-28
n002                                         0
n003                              -5.24852e-19
n004                               3.50958e-27
n005                               1.12204e-28
vsignal_source23_1#branch          3.24576e-31


No. of Data Rows : 669
Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

No. of Data Rows : 1

Initial Transient Solution
--------------------------

Node                                   Voltage
----                                   -------
n001                               4.49946e-28
n002                                         0
n003                              -5.24852e-19
n004                               3.50958e-27
n005                               1.12204e-28
vsignal_source23_1#branch          3.24576e-31


No. of Data Rows : 669
	Node                                  Voltage
	----                                  -------
	----	-------
	n005                             1.122036e-28
	n004                             3.509581e-27
	n003                             -5.24852e-19
	n002                             0.000000e+00
	n001                             4.499463e-28

	Source	Current
	------	-------

	vsignal_source23_1#branch        3.245763e-31

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
      model               led_red

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
         ic          -3.16904e-12
         ib           1.67654e-05
         ie          -1.67654e-05
        vbe               0.57415
        vbc              0.551121
         gm           0.000631687
        gpi           1.21549e-05
        gmu           0.000634169
         gx                   0.1
         go           0.000441466
        cpi           6.44107e-12
        cmu           1.17016e-10
        cbx                     0
       csub                     0

 Capacitor: Fixed capacitor
     device         ccapacitor4_1
      model                     C
capacitance                 1e-05
      dtemp                     0
     bv_max                 1e+99
          i          -0.000188668
          p          -0.000324326

 Diode: Junction Diode model
     device              dled12_1
      model               led_red
    thermal                     0
         vd            -0.0277254
         id           -3.4302e-14
         gd           1.13236e-12
         cd                     0

 Resistor: Simple linear resistor
     device         rresistor22_4         rresistor22_3         rresistor22_2
      model                     R                     R                     R
 resistance                 68000                   560                   560
         ac                 68000                   560                   560
      dtemp                     0                     0                     0
     bv_max                 1e+99                 1e+99                 1e+99
      noisy                     1                     1                     1
          i            1.6765e-05          -8.38248e-06           8.38248e-06
          p           1.91124e-05            3.9349e-08            3.9349e-08

 Resistor: Simple linear resistor
     device         rresistor22_1
      model                     R
 resistance                 10000
         ac                 10000
      dtemp                     0
     bv_max                 1e+99
      noisy                     1
          i          -0.000171903
          p           0.000295507

 Vsource: Independent voltage source
     device    vsignal_source23_1
         dc                     0
      acmag                     0
      pulse                     0
                                5
                                0
                            0.001
                            0.001
                             0.05
                              0.1
        sin                     0
                                5
                                0
                            0.001
                            0.001
                             0.05
                              0.1
        exp                     0
                                5
                                0
                            0.001
                            0.001
                             0.05
                              0.1
        pwl                     0
                                5
                                0
                            0.001
                            0.001
                             0.05
                              0.1
       sffm                     0
                                5
                                0
                            0.001
                            0.001
                             0.05
                              0.1
         am                     0
                                5
                                0
                            0.001
                            0.001
                             0.05
                              0.1
    trnoise                     0
                                5
                                0
                            0.001
                            0.001
                             0.05
                              0.1
   trrandom                     0
                                5
                                0
                            0.001
                            0.001
                             0.05
                              0.1
    portnum                     0
         z0                     0
        pwr                     0
       freq                     0
      phase                     0
          i           0.000180286
          p                     0


Total analysis time (seconds) = 0.0100049

Total elapsed time (seconds) = 0.055 

Total DRAM available = 32239.535 MB.
DRAM currently available = 16354.672 MB.
Maximum ngspice program size =   15.469 MB.
Current ngspice program size =   15.469 MB.


```

## 08_ngspice_stderr.txt
```text

```

## 10_diagnostic_context.json
```text
{
  "source_format": "pipeline2.0_diagnostic_context_manifest",
  "batch_name": "batchA",
  "experiment_name": "experiment4",
  "circuit_id": "a08",
  "user_problem": "Il LED dovrebbe lampeggiare in modo chiaramente visibile e regolare. Analizza la base run, individua la causa del duty cycle troppo basso ed esegui autonomamente solo gli scenari necessari per correggerlo.",
  "pipeline2_output_dir": "outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a08",
  "summary": {
    "spice_status": "success",
    "spice_exit_code": 0,
    "spice_message": "ngspice completed successfully.",
    "emitted_elements": 8,
    "skipped_elements": 2,
    "emit_warnings_count": 0,
    "skipped_components_count": 2,
    "node_count": 6,
    "ground_groups_count": 2,
    "singleton_nodes_count": 0,
    "bound_components": 8,
    "missing_components": 0,
    "unsupported_components": 0,
    "spice_ready_components": 8,
    "rules_missing_components": 0,
    "has_tran_csv": true,
    "has_tran_plot": true,
    "led_profiles": {
      "Dled12_1": {
        "state": "blinking",
        "regular_period": true,
        "frequency_hz": 10.023087329701543,
        "duty_cycle": 0.006339191789455449,
        "on_fraction": 0.014947683109118086,
        "pulse_count": 3,
        "voltage_min": -3.0242899399999996,
        "voltage_max": 0.6599744600000002,
        "anode_node": "N002",
        "cathode_node": "N003"
      }
    }
  },
  "artifacts": {
    "graph": {
      "step": "01",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a08\\01_graph.json",
      "role": "Graph JSON copied from Pipeline 1.0."
    },
    "normalized_circuit": {
      "step": "02",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a08\\02_normalized_circuit.json",
      "role": "Normalized circuit representation used by Pipeline 2.0."
    },
    "node_map": {
      "step": "03",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a08\\03_node_map.json",
      "role": "Maps component terminals to SPICE node names."
    },
    "values_bound": {
      "step": "04",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a08\\04_values_bound.json",
      "role": "Values and labels bound to graph components."
    },
    "component_rules": {
      "step": "06",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a08\\06_component_rules.json",
      "role": "SPICE conversion rules for each component."
    },
    "netlist": {
      "step": "07",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a08\\07_netlist.cir",
      "role": "Generated SPICE netlist."
    },
    "spice_emit_report": {
      "step": "07",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a08\\07_spice_emit_report.json",
      "role": "Report of emitted, skipped and warning components."
    },
    "spice_run": {
      "step": "08",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a08\\08_spice_run.json",
      "role": "Structured ngspice execution report."
    },
    "ngspice_stdout": {
      "step": "08",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a08\\08_ngspice_stdout.txt",
      "role": "Raw ngspice stdout log."
    },
    "ngspice_stderr": {
      "step": "08",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a08\\08_ngspice_stderr.txt",
      "role": "Raw ngspice stderr log."
    },
    "tran_csv": {
      "step": "08",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a08\\08_tran.csv",
      "role": "Clean transient CSV, when .tran data is available."
    },
    "tran_plot_png": {
      "step": "08",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a08\\08_tran_plot.png",
      "role": "Transient plot PNG, when generated."
    },
    "tran_plot_svg": {
      "step": "08",
      "available": false,
      "path": null,
      "role": "Transient plot SVG fallback, when generated."
    }
  },
  "executed_scenarios": [
    {
      "scenario_dir": "outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a08\\scenarios\\agent_scenario_1",
      "scenario_id": "agent_scenario_1",
      "title": "Aumentare R7 per ridurre il trascinamento dell'emettitore e allargare il tempo ON del LED",
      "status": "spice_success",
      "spice_status": "success",
      "diagnostic_outcome": {
        "status": "resolved_candidate",
        "technical_label": "Transient correction verified",
        "label": "Criteri elettrici e temporali soddisfatti",
        "reason": "Le aspettative elettriche e il profilo transitorio richiesto sono verificati.",
        "user_message": "Lo scenario fornisce una conferma forte dell'ipotesi testata.",
        "stop_automation": true,
        "confidence": "medium",
        "next_step": "La correzione e verificata: puoi passare alla conclusione diagnostica."
      },
      "comparison_summary": {
        "requested_count": 4,
        "changed_count": 4,
        "activated_count": 0,
        "missing_count": 0,
        "expected_count": 4,
        "expectations_met_count": 4,
        "expectations_failed_count": 0,
        "expectations_missing_count": 0,
        "meaningful_improvement_count": 1,
        "quality_required": false,
        "quality_available": false,
        "quality_improved": false,
        "quality_acceptable": false,
        "quality_output_preserved": false,
        "base_thd": null,
        "scenario_thd": null,
        "temporal_required": true,
        "temporal_available": true,
        "temporal_met": true
      },
      "led_profiles": {
        "Dled12_1": {
          "state": "blinking",
          "regular_period": true,
          "frequency_hz": 11.32668851263958,
          "duty_cycle": 0.585316653009984,
          "on_fraction": 0.43558282208588955,
          "pulse_count": 3,
          "voltage_min": -0.16400005000000029,
          "voltage_max": 0.6726678800000001,
          "anode_node": "N002",
          "cathode_node": "N003"
        }
      },
      "artifacts": {
        "scenario_definition": {
          "available": true,
          "path": "outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a08\\scenarios\\agent_scenario_1\\scenario.json",
          "role": "Scenario selected by the user and saved before execution."
        },
        "scenario_status": {
          "available": true,
          "path": "outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a08\\scenarios\\agent_scenario_1\\scenario_status.json",
          "role": "Current scenario status, SPICE status and diagnostic outcome."
        },
        "controlled_scenario_report": {
          "available": true,
          "path": "outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a08\\scenarios\\agent_scenario_1\\12_controlled_scenarios.json",
          "role": "Report produced by the controlled scenario runner."
        },
        "scenario_comparison": {
          "available": true,
          "path": "outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a08\\scenarios\\agent_scenario_1\\scenario_comparison.json",
          "role": "Base-vs-scenario comparison used to evaluate the scenario."
        }
      }
    }
  ],
  "scenario_outcome_summary": {
    "available": true,
    "best_scenario_id": "agent_scenario_1",
    "best_outcome_status": "resolved_candidate",
    "best_stop_automation": true,
    "ranking_status": "verified_best",
    "interpretation_rule": "If a user asks which scenario resolves the problem, prefer the scenario with outcome_status='resolved_candidate' and stop_automation=true. Partially resolved scenarios without verified expectations are supporting diagnostics and must not be ranked only by changed_count.",
    "scenarios": [
      {
        "scenario_id": "agent_scenario_1",
        "title": "Aumentare R7 per ridurre il trascinamento dell'emettitore e allargare il tempo ON del LED",
        "status": "spice_success",
        "spice_status": "success",
        "outcome_status": "resolved_candidate",
        "outcome_label": "Criteri elettrici e temporali soddisfatti",
        "outcome_technical_label": "Transient correction verified",
        "outcome_reason": "Le aspettative elettriche e il profilo transitorio richiesto sono verificati.",
        "stop_automation": true,
        "comparison_summary": {
          "requested_count": 4,
          "changed_count": 4,
          "activated_count": 0,
          "missing_count": 0,
          "expected_count": 4,
          "expectations_met_count": 4,
          "expectations_failed_count": 0,
          "expectations_missing_count": 0,
          "meaningful_improvement_count": 1,
          "quality_required": false,
          "quality_available": false,
          "quality_improved": false,
          "quality_acceptable": false,
          "quality_output_preserved": false,
          "base_thd": null,
          "scenario_thd": null,
          "temporal_required": true,
          "temporal_available": true,
          "temporal_met": true
        },
        "quantity_summary": {
          "changed": [
            "v(N003)",
            "v(N004)",
            "v(N005)",
            "i(Rresistor22_3)"
          ],
          "unchanged": [],
          "missing": []
        },
        "led_profiles": {
          "Dled12_1": {
            "state": "blinking",
            "regular_period": true,
            "frequency_hz": 11.32668851263958,
            "duty_cycle": 0.585316653009984,
            "on_fraction": 0.43558282208588955,
            "pulse_count": 3,
            "voltage_min": -0.16400005000000029,
            "voltage_max": 0.6726678800000001,
            "anode_node": "N002",
            "cathode_node": "N003"
          }
        },
        "ranking_verified": true,
        "score": 210
      }
    ]
  },
  "scenario_budget": {
    "max_executable_scenarios": 5,
    "executed_scenarios_count": 1,
    "remaining_executable_scenarios": 4,
    "budget_exhausted": false,
    "last_scenario_available": false,
    "policy": "At most 5 scenarios can be executed for the same circuit. When only one scenario remains, the agent should propose a single final scenario. When no scenario remains, the agent must stop proposing new scenarios and provide a final diagnostic conclusion."
  },
  "image_access": {
    "included_by_default": false,
    "can_be_requested": true,
    "path": "data\\batchA\\a08.jpg",
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
