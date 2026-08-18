# Pipeline 2.0 - agente diagnostico autonomo controllato

Sei il controller diagnostico di una pipeline Graph JSON -> SPICE/ngspice.
Devi scegliere il prossimo test controllato oppure fermarti con una conclusione.

## Sintomo utente
Il circuito dovrebbe far lampeggiare alternativamente i due LED, ma nella simulazione restano entrambi accesi. Come mai?

## Vincoli obbligatori
- Rispondi con un solo oggetto JSON valido, senza Markdown o testo esterno.
- Non inventare nodi, componenti, valori o risultati.
- Usa soltanto queste primitive: add_resistor_between_nodes, add_voltage_source_between_nodes, change_component_value, change_source_value, close_switch, connect_nodes, drive_node_voltage, feed_nodes_from_source_node, set_initial_node_voltage.
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
[
  {
    "decision_number": 1,
    "decision": {
      "decision": "run_scenarios",
      "reason": "La base run mostra un astabile perfettamente simmetrico bloccato in uno stato DC con entrambi i transistor e LED ugualmente polarizzati; serve un test controllato transitorio per verificare se il problema e la mancanza di una perturbazione iniziale che rompa la simmetria.",
      "scenarios": [
        {
          "title": "Rompere la simmetria con una condizione iniziale su una base",
          "hypothesis": "Con componenti identici e condizioni iniziali perfettamente simmetriche, il multivibratore puo restare nel punto di equilibrio metastabile con entrambi i transistor contemporaneamente in conduzione; imponendo una piccola asimmetria iniziale una base dovrebbe spegnersi temporaneamente e innescare il lampeggio alternato.",
          "intent": "diagnostic",
          "analysis": "tran",
          "actions": [
            {
              "type": "set_initial_node_voltage",
              "target": "N004",
              "value": "0V"
            }
          ],
          "compare": [
            "v(N004)",
            "v(N006)",
            "v(N005)",
            "v(N007)",
            "i(Rresistor22_1)",
            "i(Rresistor22_4)"
          ],
          "measure": {
            "i(Rresistor22_1)": "op",
            "i(Rresistor22_4)": "op"
          },
          "expect": {
            "v(N004)": "changed",
            "v(N006)": "changed",
            "v(N005)": "changed",
            "v(N007)": "changed",
            "i(Rresistor22_1)": "changed",
            "i(Rresistor22_4)": "changed"
          },
          "temporal_expect": {
            "target": "Dled12_1",
            "required_state": "blinking",
            "require_regular_period": true,
            "min_duty_cycle": 0.1
          }
        }
      ]
    },
    "prompt_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b02\\experiment_chat\\autonomous_prompt_1.md",
    "response_paths": [
      "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b02\\experiment_chat\\autonomous_response_1_attempt_1.txt"
    ],
    "scenario_results": [
      {
        "scenario_id": "agent_scenario_1",
        "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b02\\scenarios\\agent_scenario_1",
        "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b02\\scenarios\\agent_scenario_1\\run",
        "status": "spice_success",
        "spice_executed": true,
        "spice_status": "success",
        "spice_exit_code": 0,
        "comparison_summary": {
          "requested_count": 6,
          "changed_count": 6,
          "activated_count": 4,
          "missing_count": 0,
          "expected_count": 6,
          "expectations_met_count": 6,
          "expectations_failed_count": 0,
          "expectations_missing_count": 0,
          "meaningful_improvement_count": 0,
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
          "status": "partially_resolved",
          "technical_label": "Diagnostic hypothesis confirmed",
          "label": "Ipotesi diagnostica confermata",
          "reason": "I criteri dichiarati dal test diagnostico sono soddisfatti, ma lo scenario non applica una correzione del sintomo utente.",
          "user_message": "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato.",
          "stop_automation": false,
          "confidence": "low",
          "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
        },
        "viewer": {
          "model": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b02\\scenarios\\agent_scenario_1\\run\\13_viewer_model.json",
          "layout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b02\\scenarios\\agent_scenario_1\\run\\14_viewer_layout.json",
          "svg": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b02\\scenarios\\agent_scenario_1\\run\\15_viewer.svg"
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
  "circuit_id": "b02",
  "source_format": "pipeline2.0_node_map",
  "nodes": [
    {
      "node_id": "0",
      "kind": "ground",
      "terminals": [
        "gnd9.1_t1",
        "npn_transistor18.1_E",
        "npn_transistor18.2_E"
      ],
      "terminal_count": 3,
      "source_groups": [
        [
          "gnd9.1_t1",
          "npn_transistor18.1_E",
          "npn_transistor18.2_E"
        ]
      ]
    },
    {
      "node_id": "N001",
      "kind": "normal",
      "terminals": [
        "led12.1_anode",
        "led12.2_anode",
        "resistor22.2_t1",
        "resistor22.3_t1"
      ],
      "terminal_count": 4
    },
    {
      "node_id": "N002",
      "kind": "normal",
      "terminals": [
        "led12.1_cathode",
        "resistor22.1_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N003",
      "kind": "normal",
      "terminals": [
        "led12.2_cathode",
        "resistor22.4_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N004",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.1_B",
        "polarized_capacitor20.2_negative",
        "resistor22.2_t2"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N005",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.1_C",
        "polarized_capacitor20.1_positive",
        "resistor22.1_t2"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N006",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.2_B",
        "polarized_capacitor20.1_negative",
        "resistor22.3_t2"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N007",
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
    "gnd9.1_t1": "0",
    "led12.1_anode": "N001",
    "led12.1_cathode": "N002",
    "led12.2_anode": "N001",
    "led12.2_cathode": "N003",
    "npn_transistor18.1_B": "N004",
    "npn_transistor18.1_C": "N005",
    "npn_transistor18.1_E": "0",
    "npn_transistor18.2_B": "N006",
    "npn_transistor18.2_C": "N007",
    "npn_transistor18.2_E": "0",
    "polarized_capacitor20.1_negative": "N006",
    "polarized_capacitor20.1_positive": "N005",
    "polarized_capacitor20.2_negative": "N004",
    "polarized_capacitor20.2_positive": "N007",
    "resistor22.1_t1": "N002",
    "resistor22.1_t2": "N005",
    "resistor22.2_t1": "N001",
    "resistor22.2_t2": "N004",
    "resistor22.3_t1": "N001",
    "resistor22.3_t2": "N006",
    "resistor22.4_t1": "N003",
    "resistor22.4_t2": "N007"
  },
  "component_terminal_nodes": {
    "gnd9.1": {
      "t1": "0"
    },
    "led12.1": {
      "anode": "N001",
      "cathode": "N002"
    },
    "led12.2": {
      "anode": "N001",
      "cathode": "N003"
    },
    "npn_transistor18.1": {
      "B": "N004",
      "C": "N005",
      "E": "0"
    },
    "npn_transistor18.2": {
      "B": "N006",
      "C": "N007",
      "E": "0"
    },
    "polarized_capacitor20.1": {
      "positive": "N005",
      "negative": "N006"
    },
    "polarized_capacitor20.2": {
      "negative": "N004",
      "positive": "N007"
    },
    "resistor22.1": {
      "t1": "N002",
      "t2": "N005"
    },
    "resistor22.2": {
      "t1": "N001",
      "t2": "N004"
    },
    "resistor22.3": {
      "t1": "N001",
      "t2": "N006"
    },
    "resistor22.4": {
      "t1": "N003",
      "t2": "N007"
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
    "nodes_count": 8,
    "normal_nodes_count": 7,
    "ground_nodes_count": 1,
    "ground_groups_count": 1,
    "terminal_to_node_count": 23,
    "singleton_nodes_count": 0
  }
}

```

## 06_component_rules.json
```text
{
  "circuit_id": "b02",
  "source_format": "pipeline2.0_component_rules",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_manual_values\\batchB\\b02_values.yaml",
  "spice_classes_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_spice_classes.yaml",
  "supplies": {
    "VCC": {
      "status": "spice_ready",
      "spice_prefix": "V",
      "emit_as": "independent_voltage_source",
      "nodes": [
        "N001",
        "0"
      ],
      "parameters": {
        "terminal": "led12.1_anode",
        "type": "dc",
        "value": 5,
        "unit": "V",
        "reference": 0,
        "source": "manual_from_image_label",
        "label_text": "+5V",
        "node": "N001"
      }
    }
  },
  "components": {
    "gnd9.1": {
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
        "N001",
        "N002"
      ],
      "parameters": {
        "model": "LED_RED",
        "source": "manual_spice_generic_led_model",
        "label_text": "D1 LED; modello SPICE generico"
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
        "N001",
        "N003"
      ],
      "parameters": {
        "model": "LED_RED",
        "source": "manual_spice_generic_led_model",
        "label_text": "D2 LED; modello SPICE generico"
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
        "N005",
        "N004",
        "0"
      ],
      "parameters": {
        "model": "2N3904",
        "source": "manual_from_image_label",
        "label_text": "Q1 2N3904"
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
        "N007",
        "N006",
        "0"
      ],
      "parameters": {
        "model": "2N3904",
        "source": "manual_from_image_label",
        "label_text": "Q2 2N3904"
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
        "N005",
        "N006"
      ],
      "parameters": {
        "value": 47,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C1 47 uF"
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
        "N007",
        "N004"
      ],
      "parameters": {
        "value": 47,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C2 47 uF"
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
        "N005"
      ],
      "parameters": {
        "value": 270,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R1 270 ohm"
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
        "N001",
        "N004"
      ],
      "parameters": {
        "value": 2.2,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R2 2.2 kohm"
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
        "N001",
        "N006"
      ],
      "parameters": {
        "value": 2.2,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R4 2.2 kohm"
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
        "N003",
        "N007"
      ],
      "parameters": {
        "value": 270,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R3 270 ohm"
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
      "stop": "1s"
    }
  },
  "stats": {
    "components_total": 11,
    "spice_ready_components": 10,
    "not_emitted_components": 1,
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
* circuit: b02

VVCC N001 0 DC 5
Dled12_1 N001 N002 LED_RED
Dled12_2 N001 N003 LED_RED
Qnpn_transistor18_1 N005 N004 0 2N3904
Qnpn_transistor18_2 N007 N006 0 2N3904
Cpolarized_capacitor20_1 N005 N006 47u
Cpolarized_capacitor20_2 N007 N004 47u
Rresistor22_1 N002 N005 270
Rresistor22_2 N001 N004 2.2k
Rresistor22_3 N001 N006 2.2k
Rresistor22_4 N003 N007 270

.model 2N3904 NPN(IS=6.734f BF=416.4 VAF=74.03 IKF=66.78m ISE=6.734f NE=1.259 BR=0.7371 VAR=12.11 IKR=0.0 ISC=0.0 NC=2 RB=10 RC=1 RE=0.1 CJE=4.493p VJE=0.75 MJE=0.2593 CJC=3.638p VJC=0.75 MJC=0.3085 TF=301.2p TR=239.5n)
.model LED_RED D

.op
.save all
.tran 1ms 1s

.control
set wr_singlescale
set wr_vecnames
run
wrdata 08_tran.csv time v(N001) v(N002) v(N003) v(N004) v(N005) v(N006) v(N007)
.endc
.end

```

## 07_spice_emit_report.json
```text
{
  "circuit_id": "b02",
  "source_format": "pipeline2.0_spice_emit_report",
  "emitted_elements": 11,
  "skipped_elements": 1,
  "skipped_components": [
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
      "N007"
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
n001                                         5
n002                                   4.27402
n003                                   4.27402
n005                                 0.0936194
n004                                  0.769966
n007                                 0.0936194
n006                                  0.769966
vvcc#branch                         -0.0348114


No. of Data Rows : 1008
Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

No. of Data Rows : 1

Initial Transient Solution
--------------------------

Node                                   Voltage
----                                   -------
n001                                         5
n002                                   4.27402
n003                                   4.27402
n005                                 0.0936194
n004                                  0.769966
n007                                 0.0936194
n006                                  0.769966
vvcc#branch                         -0.0348114


No. of Data Rows : 1008
	Node                                  Voltage
	----                                  -------
	----	-------
	n006                             7.699664e-01
	n007                             9.361940e-02
	n004                             7.699664e-01
	n005                             9.361940e-02
	n003                             4.274019e+00
	n002                             4.274019e+00
	n001                             5.000000e+00

	Source	Current
	------	-------

	vvcc#branch                      -3.48114e-02

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
     device   qnpn_transistor18_2   qnpn_transistor18_1
      model                2n3904                2n3904
         ic              0.015483              0.015483
         ib            0.00192274            0.00192274
         ie            -0.0174057            -0.0174057
        vbe              0.748998              0.748998
        vbc              0.672603              0.672603
         gm              0.542628              0.542628
        gpi            0.00437446            0.00437446
        gmu               0.06947               0.06947
         gx                   0.1                   0.1
         go             0.0370062             0.0370062
        cpi            1.7928e-10            1.7928e-10
        cmu           1.22645e-08           1.22645e-08
        cbx                     0                     0
       csub                     0                     0

 Capacitor: Fixed capacitor
     device cpolarized_capacitor2 cpolarized_capacitor2
      model                     C                     C
capacitance               4.7e-05               4.7e-05
      dtemp                     0                     0
     bv_max                 1e+99                 1e+99
          i           6.60087e-17            2.3657e-17
          p          -4.46448e-17          -1.60004e-17

 Diode: Junction Diode model
     device              dled12_2              dled12_1
      model               led_red               led_red
    thermal                     0                     0
         vd              0.725981              0.725981
         id              0.015483              0.015483
         gd              0.598609              0.598609
         cd                     0                     0

 Resistor: Simple linear resistor
     device         rresistor22_4         rresistor22_3         rresistor22_2
      model                     R                     R                     R
 resistance                   270                  2200                  2200
         ac                   270                  2200                  2200
      dtemp                     0                     0                     0
     bv_max                 1e+99                 1e+99                 1e+99
      noisy                     1                     1                     1
          i              0.015483            0.00192274            0.00192274
          p              0.064725            0.00813327            0.00813327

 Resistor: Simple linear resistor
     device         rresistor22_1
      model                     R
 resistance                   270
         ac                   270
      dtemp                     0
     bv_max                 1e+99
      noisy                     1
          i              0.015483
          p              0.064725

 Vsource: Independent voltage source
     device                  vvcc
         dc                     5
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
          i            -0.0348114
          p             -0.174057


Total analysis time (seconds) = 0.0137146

Total elapsed time (seconds) = 0.098 

Total DRAM available = 32239.535 MB.
DRAM currently available = 16038.105 MB.
Maximum ngspice program size =   15.188 MB.
Current ngspice program size =   15.188 MB.


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
  "circuit_id": "b02",
  "user_problem": "Il circuito dovrebbe far lampeggiare alternativamente i due LED, ma nella simulazione restano entrambi accesi. Come mai?",
  "pipeline2_output_dir": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b02",
  "summary": {
    "spice_status": "success",
    "spice_exit_code": 0,
    "spice_message": "ngspice completed successfully.",
    "emitted_elements": 11,
    "skipped_elements": 1,
    "emit_warnings_count": 0,
    "skipped_components_count": 1,
    "node_count": 8,
    "ground_groups_count": 1,
    "singleton_nodes_count": 0,
    "bound_components": 10,
    "missing_components": 0,
    "unsupported_components": 0,
    "spice_ready_components": 10,
    "rules_missing_components": 0,
    "has_tran_csv": true,
    "has_tran_plot": true,
    "led_profiles": {
      "Dled12_1": {
        "state": "steady_on",
        "regular_period": false,
        "frequency_hz": null,
        "duty_cycle": 1.0,
        "on_fraction": 1.0,
        "pulse_count": 1,
        "voltage_min": 0.7259810499999997,
        "voltage_max": 0.7259810499999997,
        "anode_node": "N001",
        "cathode_node": "N002"
      },
      "Dled12_2": {
        "state": "steady_on",
        "regular_period": false,
        "frequency_hz": null,
        "duty_cycle": 1.0,
        "on_fraction": 1.0,
        "pulse_count": 1,
        "voltage_min": 0.7259810499999997,
        "voltage_max": 0.7259810499999997,
        "anode_node": "N001",
        "cathode_node": "N003"
      }
    }
  },
  "artifacts": {
    "graph": {
      "step": "01",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b02\\01_graph.json",
      "role": "Graph JSON copied from Pipeline 1.0."
    },
    "normalized_circuit": {
      "step": "02",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b02\\02_normalized_circuit.json",
      "role": "Normalized circuit representation used by Pipeline 2.0."
    },
    "node_map": {
      "step": "03",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b02\\03_node_map.json",
      "role": "Maps component terminals to SPICE node names."
    },
    "values_bound": {
      "step": "04",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b02\\04_values_bound.json",
      "role": "Values and labels bound to graph components."
    },
    "component_rules": {
      "step": "06",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b02\\06_component_rules.json",
      "role": "SPICE conversion rules for each component."
    },
    "netlist": {
      "step": "07",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b02\\07_netlist.cir",
      "role": "Generated SPICE netlist."
    },
    "spice_emit_report": {
      "step": "07",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b02\\07_spice_emit_report.json",
      "role": "Report of emitted, skipped and warning components."
    },
    "spice_run": {
      "step": "08",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b02\\08_spice_run.json",
      "role": "Structured ngspice execution report."
    },
    "ngspice_stdout": {
      "step": "08",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b02\\08_ngspice_stdout.txt",
      "role": "Raw ngspice stdout log."
    },
    "ngspice_stderr": {
      "step": "08",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b02\\08_ngspice_stderr.txt",
      "role": "Raw ngspice stderr log."
    },
    "tran_csv": {
      "step": "08",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b02\\08_tran.csv",
      "role": "Clean transient CSV, when .tran data is available."
    },
    "tran_plot_png": {
      "step": "08",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b02\\08_tran_plot.png",
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
      "scenario_dir": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b02\\scenarios\\agent_scenario_1",
      "scenario_id": "agent_scenario_1",
      "title": "Rompere la simmetria con una condizione iniziale su una base",
      "status": "spice_success",
      "spice_status": "success",
      "diagnostic_outcome": {
        "status": "partially_resolved",
        "technical_label": "Diagnostic hypothesis confirmed",
        "label": "Ipotesi diagnostica confermata",
        "reason": "I criteri dichiarati dal test diagnostico sono soddisfatti, ma lo scenario non applica una correzione del sintomo utente.",
        "user_message": "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato.",
        "stop_automation": false,
        "confidence": "low",
        "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
      },
      "comparison_summary": {
        "requested_count": 6,
        "changed_count": 6,
        "activated_count": 4,
        "missing_count": 0,
        "expected_count": 6,
        "expectations_met_count": 6,
        "expectations_failed_count": 0,
        "expectations_missing_count": 0,
        "meaningful_improvement_count": 0,
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
          "frequency_hz": 7.2621386520481535,
          "duty_cycle": 0.5760658443006331,
          "on_fraction": 0.6162196679438059,
          "pulse_count": 8,
          "voltage_min": 0.1734779099999999,
          "voltage_max": 0.7261731100000004,
          "anode_node": "N001",
          "cathode_node": "N002"
        },
        "Dled12_2": {
          "state": "blinking",
          "regular_period": true,
          "frequency_hz": 7.2533279175151515,
          "duty_cycle": 0.5644272754143008,
          "on_fraction": 0.6507024265644955,
          "pulse_count": 8,
          "voltage_min": 0.5572366300000002,
          "voltage_max": 0.7261472800000002,
          "anode_node": "N001",
          "cathode_node": "N003"
        }
      },
      "artifacts": {
        "scenario_definition": {
          "available": true,
          "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b02\\scenarios\\agent_scenario_1\\scenario.json",
          "role": "Scenario selected by the user and saved before execution."
        },
        "scenario_status": {
          "available": true,
          "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b02\\scenarios\\agent_scenario_1\\scenario_status.json",
          "role": "Current scenario status, SPICE status and diagnostic outcome."
        },
        "controlled_scenario_report": {
          "available": true,
          "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b02\\scenarios\\agent_scenario_1\\12_controlled_scenarios.json",
          "role": "Report produced by the controlled scenario runner."
        },
        "scenario_comparison": {
          "available": true,
          "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b02\\scenarios\\agent_scenario_1\\scenario_comparison.json",
          "role": "Base-vs-scenario comparison used to evaluate the scenario."
        }
      }
    }
  ],
  "scenario_outcome_summary": {
    "available": true,
    "best_scenario_id": "agent_scenario_1",
    "best_outcome_status": "partially_resolved",
    "best_stop_automation": false,
    "ranking_status": "verified_best",
    "interpretation_rule": "If a user asks which scenario resolves the problem, prefer the scenario with outcome_status='resolved_candidate' and stop_automation=true. Partially resolved scenarios without verified expectations are supporting diagnostics and must not be ranked only by changed_count.",
    "scenarios": [
      {
        "scenario_id": "agent_scenario_1",
        "title": "Rompere la simmetria con una condizione iniziale su una base",
        "status": "spice_success",
        "spice_status": "success",
        "outcome_status": "partially_resolved",
        "outcome_label": "Ipotesi diagnostica confermata",
        "outcome_technical_label": "Diagnostic hypothesis confirmed",
        "outcome_reason": "I criteri dichiarati dal test diagnostico sono soddisfatti, ma lo scenario non applica una correzione del sintomo utente.",
        "stop_automation": false,
        "comparison_summary": {
          "requested_count": 6,
          "changed_count": 6,
          "activated_count": 4,
          "missing_count": 0,
          "expected_count": 6,
          "expectations_met_count": 6,
          "expectations_failed_count": 0,
          "expectations_missing_count": 0,
          "meaningful_improvement_count": 0,
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
            "v(N004)",
            "v(N006)",
            "v(N005)",
            "v(N007)",
            "i(Rresistor22_1)",
            "i(Rresistor22_4)"
          ],
          "unchanged": [],
          "missing": []
        },
        "led_profiles": {
          "Dled12_1": {
            "state": "blinking",
            "regular_period": true,
            "frequency_hz": 7.2621386520481535,
            "duty_cycle": 0.5760658443006331,
            "on_fraction": 0.6162196679438059,
            "pulse_count": 8,
            "voltage_min": 0.1734779099999999,
            "voltage_max": 0.7261731100000004,
            "anode_node": "N001",
            "cathode_node": "N002"
          },
          "Dled12_2": {
            "state": "blinking",
            "regular_period": true,
            "frequency_hz": 7.2533279175151515,
            "duty_cycle": 0.5644272754143008,
            "on_fraction": 0.6507024265644955,
            "pulse_count": 8,
            "voltage_min": 0.5572366300000002,
            "voltage_max": 0.7261472800000002,
            "anode_node": "N001",
            "cathode_node": "N003"
          }
        },
        "ranking_verified": true,
        "score": 50
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
    "path": "data\\batchB\\b02.jpg",
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
