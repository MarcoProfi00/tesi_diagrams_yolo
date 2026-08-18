# Pipeline 2.0 - agente diagnostico autonomo controllato

Sei il controller diagnostico di una pipeline Graph JSON -> SPICE/ngspice.
Devi scegliere il prossimo test controllato oppure fermarti con una conclusione.

## Sintomo utente
Su A leggo 1 V, ma su B leggo quasi zero. È normale o c’è qualcosa che non va?

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
      "reason": "La base run suggerisce che B (N002) e quasi a zero perche il ramo verso B e modellato come percorso OFF ad altissima resistenza (Rresistor22_2=1 Gohm) mentre lo switch25.1 e aperto e quindi il percorso ON verso la sorgente interna non e attivo. Serve almeno uno scenario controllato per verificare se chiudendo lo switch B sale davvero vicino ad A.",
      "scenarios": [
        {
          "title": "Verifica chiusura switch verso B",
          "hypothesis": "Se la lettura quasi nulla su B e normale per interruttore aperto, allora chiudendo switch25.1 il nodo B/N002 deve aumentare nettamente rispetto alla base run.",
          "intent": "diagnostic",
          "analysis": "op",
          "actions": [
            {
              "type": "close_switch",
              "target": "switch25.1"
            }
          ],
          "compare": [
            "v(N002)",
            "v(N005)",
            "i(Rresistor22_1)",
            "i(Rresistor22_2)"
          ],
          "expect": {
            "v(N002)": "magnitude_increased",
            "i(Rresistor22_1)": "nonzero",
            "i(Rresistor22_2)": "decreased"
          }
        }
      ]
    },
    "prompt_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b10\\experiment_chat\\autonomous_prompt_1.md",
    "response_paths": [
      "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b10\\experiment_chat\\autonomous_response_1_attempt_1.txt"
    ],
    "scenario_results": [
      {
        "scenario_id": "agent_scenario_1",
        "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b10\\scenarios\\agent_scenario_1",
        "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b10\\scenarios\\agent_scenario_1\\run",
        "status": "spice_success",
        "spice_executed": true,
        "spice_status": "success",
        "spice_exit_code": 0,
        "comparison_summary": {
          "requested_count": 4,
          "changed_count": 4,
          "activated_count": 1,
          "missing_count": 0,
          "expected_count": 3,
          "expectations_met_count": 3,
          "expectations_failed_count": 0,
          "expectations_missing_count": 0,
          "meaningful_improvement_count": 3,
          "quality_required": false,
          "quality_available": false,
          "quality_improved": false,
          "quality_acceptable": false,
          "quality_output_preserved": false,
          "base_thd": null,
          "scenario_thd": null
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
          "model": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b10\\scenarios\\agent_scenario_1\\run\\13_viewer_model.json",
          "layout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b10\\scenarios\\agent_scenario_1\\run\\14_viewer_layout.json",
          "svg": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b10\\scenarios\\agent_scenario_1\\run\\15_viewer.svg"
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
  "circuit_id": "b10",
  "source_format": "pipeline2.0_node_map",
  "nodes": [
    {
      "node_id": "0",
      "kind": "ground",
      "terminals": [
        "current_source6.1_current_to",
        "current_source6.3_current_to",
        "gnd9.1_t1",
        "polarized_capacitor20.1_negative",
        "polarized_capacitor20.5_negative",
        "terminal26.2_t1"
      ],
      "terminal_count": 6,
      "source_groups": [
        [
          "current_source6.1_current_to",
          "current_source6.3_current_to",
          "gnd9.1_t1",
          "polarized_capacitor20.1_negative",
          "polarized_capacitor20.5_negative",
          "terminal26.2_t1"
        ]
      ]
    },
    {
      "node_id": "N001",
      "kind": "normal",
      "terminals": [
        "current_source6.1_current_from",
        "current_source6.2_current_from",
        "polarized_capacitor20.1_positive",
        "polarized_capacitor20.2_positive",
        "polarized_capacitor20.3_positive",
        "resistor22.1_t1",
        "resistor22.2_t1",
        "terminal26.1_t1"
      ],
      "terminal_count": 8
    },
    {
      "node_id": "N002",
      "kind": "normal",
      "terminals": [
        "current_source6.2_current_to",
        "current_source6.3_current_from",
        "polarized_capacitor20.3_negative",
        "polarized_capacitor20.4_negative",
        "polarized_capacitor20.5_positive",
        "resistor22.2_t2",
        "terminal26.4_t1",
        "voltage_source31.1_negative"
      ],
      "terminal_count": 8
    },
    {
      "node_id": "N003",
      "kind": "normal",
      "terminals": [
        "polarized_capacitor20.2_negative",
        "polarized_capacitor20.4_positive",
        "terminal26.3_t1"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N004",
      "kind": "normal",
      "terminals": [
        "resistor22.1_t2",
        "switch25.1_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N005",
      "kind": "normal",
      "terminals": [
        "switch25.1_t2",
        "voltage_source31.1_positive"
      ],
      "terminal_count": 2
    }
  ],
  "terminal_to_node": {
    "current_source6.1_current_from": "N001",
    "current_source6.1_current_to": "0",
    "current_source6.2_current_from": "N001",
    "current_source6.2_current_to": "N002",
    "current_source6.3_current_from": "N002",
    "current_source6.3_current_to": "0",
    "gnd9.1_t1": "0",
    "polarized_capacitor20.1_negative": "0",
    "polarized_capacitor20.1_positive": "N001",
    "polarized_capacitor20.2_negative": "N003",
    "polarized_capacitor20.2_positive": "N001",
    "polarized_capacitor20.3_negative": "N002",
    "polarized_capacitor20.3_positive": "N001",
    "polarized_capacitor20.4_negative": "N002",
    "polarized_capacitor20.4_positive": "N003",
    "polarized_capacitor20.5_negative": "0",
    "polarized_capacitor20.5_positive": "N002",
    "resistor22.1_t1": "N001",
    "resistor22.1_t2": "N004",
    "resistor22.2_t1": "N001",
    "resistor22.2_t2": "N002",
    "switch25.1_t1": "N004",
    "switch25.1_t2": "N005",
    "terminal26.1_t1": "N001",
    "terminal26.2_t1": "0",
    "terminal26.3_t1": "N003",
    "terminal26.4_t1": "N002",
    "voltage_source31.1_negative": "N002",
    "voltage_source31.1_positive": "N005"
  },
  "component_terminal_nodes": {
    "current_source6.1": {
      "current_from": "N001",
      "current_to": "0"
    },
    "current_source6.2": {
      "current_from": "N001",
      "current_to": "N002"
    },
    "current_source6.3": {
      "current_from": "N002",
      "current_to": "0"
    },
    "gnd9.1": {
      "t1": "0"
    },
    "polarized_capacitor20.1": {
      "positive": "N001",
      "negative": "0"
    },
    "polarized_capacitor20.2": {
      "positive": "N001",
      "negative": "N003"
    },
    "polarized_capacitor20.3": {
      "positive": "N001",
      "negative": "N002"
    },
    "polarized_capacitor20.4": {
      "positive": "N003",
      "negative": "N002"
    },
    "polarized_capacitor20.5": {
      "positive": "N002",
      "negative": "0"
    },
    "resistor22.1": {
      "t1": "N001",
      "t2": "N004"
    },
    "resistor22.2": {
      "t1": "N001",
      "t2": "N002"
    },
    "switch25.1": {
      "t1": "N004",
      "t2": "N005"
    },
    "terminal26.1": {
      "t1": "N001"
    },
    "terminal26.2": {
      "t1": "0"
    },
    "terminal26.3": {
      "t1": "N003"
    },
    "terminal26.4": {
      "t1": "N002"
    },
    "voltage_source31.1": {
      "positive": "N005",
      "negative": "N002"
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
    "nodes_count": 6,
    "normal_nodes_count": 5,
    "ground_nodes_count": 1,
    "ground_groups_count": 1,
    "terminal_to_node_count": 29,
    "singleton_nodes_count": 0
  }
}

```

## 06_component_rules.json
```text
{
  "circuit_id": "b10",
  "source_format": "pipeline2.0_component_rules",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_manual_values\\batchB\\b10_values.yaml",
  "spice_classes_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_spice_classes.yaml",
  "supplies": {
    "VTEST_A": {
      "status": "spice_ready",
      "spice_prefix": "V",
      "emit_as": "independent_voltage_source",
      "nodes": [
        "N001",
        "0"
      ],
      "parameters": {
        "terminal": "terminal26.1_t1",
        "type": "dc",
        "value": 1,
        "unit": "V",
        "reference": 0,
        "source": "manual_assumption_symbolic_switch_test_bench",
        "label_text": "A di test: 1 V",
        "node": "N001"
      }
    },
    "VTEST_C": {
      "status": "spice_ready",
      "spice_prefix": "V",
      "emit_as": "independent_voltage_source",
      "nodes": [
        "N003",
        "0"
      ],
      "parameters": {
        "terminal": "terminal26.3_t1",
        "type": "dc",
        "value": 0,
        "unit": "V",
        "reference": 0,
        "source": "manual_assumption_symbolic_switch_test_bench",
        "label_text": "C di test: 0 V",
        "node": "N003"
      }
    }
  },
  "components": {
    "current_source6.1": {
      "class_name": "Current_Source",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "I",
      "emit_as": "independent_current_source",
      "node_order": [
        "current_from",
        "current_to"
      ],
      "nodes": [
        "N001",
        "0"
      ],
      "parameters": {
        "type": "dc",
        "value": 0,
        "unit": "A",
        "source": "manual_assumption_symbolic_switch_test_bench",
        "label_text": "I_A assunto: 0 A"
      }
    },
    "current_source6.2": {
      "class_name": "Current_Source",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "I",
      "emit_as": "independent_current_source",
      "node_order": [
        "current_from",
        "current_to"
      ],
      "nodes": [
        "N001",
        "N002"
      ],
      "parameters": {
        "type": "dc",
        "value": 1e-12,
        "unit": "A",
        "source": "manual_assumption_symbolic_switch_model",
        "label_text": "I_OFF assunto: 1 pA"
      }
    },
    "current_source6.3": {
      "class_name": "Current_Source",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "I",
      "emit_as": "independent_current_source",
      "node_order": [
        "current_from",
        "current_to"
      ],
      "nodes": [
        "N002",
        "0"
      ],
      "parameters": {
        "type": "dc",
        "value": 1e-09,
        "unit": "A",
        "source": "manual_assumption_symbolic_switch_test_bench",
        "label_text": "I_B assunto: 1 nA"
      }
    },
    "gnd9.1": {
      "class_name": "GND",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "GND terminals are already mapped to SPICE node 0."
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
        "value": 5,
        "unit": "pf",
        "source": "manual_assumption_symbolic_switch_model",
        "label_text": "capacita parassita assunta: 5 pF"
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
        "N001",
        "N003"
      ],
      "parameters": {
        "value": 5,
        "unit": "pf",
        "source": "manual_assumption_symbolic_switch_model",
        "label_text": "capacita parassita assunta: 5 pF"
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
        "N002"
      ],
      "parameters": {
        "value": 5,
        "unit": "pf",
        "source": "manual_assumption_symbolic_switch_model",
        "label_text": "capacita parassita assunta: 5 pF"
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
        "N002"
      ],
      "parameters": {
        "value": 5,
        "unit": "pf",
        "source": "manual_assumption_symbolic_switch_model",
        "label_text": "capacita parassita assunta: 5 pF"
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
        "N002",
        "0"
      ],
      "parameters": {
        "value": 5,
        "unit": "pf",
        "source": "manual_assumption_symbolic_switch_model",
        "label_text": "capacita parassita assunta: 5 pF"
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
        "N001",
        "N004"
      ],
      "parameters": {
        "value": 10,
        "unit": "ohm",
        "source": "manual_assumption_symbolic_switch_model",
        "label_text": "r_ON assunto: 10 ohm"
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
        "N002"
      ],
      "parameters": {
        "value": 1000,
        "unit": "Mohm",
        "source": "manual_assumption_symbolic_switch_model",
        "label_text": "r_OFF assunto: 1 Gohm"
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
        "N004",
        "N005"
      ],
      "parameters": {
        "state": "open",
        "state_source": "graph_json_state",
        "state_confidence": 0.95,
        "source": "graph_json_state_validated_from_image",
        "label_text": "switch aperto"
      },
      "strategy": "open_circuit"
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
    },
    "terminal26.4": {
      "class_name": "Terminal",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "External terminal/label; useful for nodes and interface handling."
    },
    "voltage_source31.1": {
      "class_name": "Voltage_Source",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "V",
      "emit_as": "independent_voltage_source",
      "node_order": [
        "positive",
        "negative"
      ],
      "nodes": [
        "N005",
        "N002"
      ],
      "parameters": {
        "type": "dc",
        "value": 0.001,
        "unit": "V",
        "source": "manual_assumption_symbolic_switch_model",
        "label_text": "V_OS assunto: 1 mV"
      }
    }
  },
  "simulation": {
    "analyses": [
      "op",
      "tran"
    ],
    "tran": {
      "step": "1us",
      "stop": "100us"
    }
  },
  "stats": {
    "components_total": 17,
    "spice_ready_components": 12,
    "not_emitted_components": 5,
    "measurement_components": 0,
    "missing_components": 0,
    "unsupported_components": 0,
    "pin_aware_components": 0,
    "invalid_components": 0,
    "supplies_ready_count": 2
  }
}

```

## 07_netlist.cir
```text
* pipeline2.0 netlist
* circuit: b10

VVTEST_A N001 0 DC 1
VVTEST_C N003 0 DC 0
Icurrent_source6_1 N001 0 DC 0
Icurrent_source6_2 N001 N002 DC 1e-12
Icurrent_source6_3 N002 0 DC 1e-09
Cpolarized_capacitor20_1 N001 0 5p
Cpolarized_capacitor20_2 N001 N003 5p
Cpolarized_capacitor20_3 N001 N002 5p
Cpolarized_capacitor20_4 N003 N002 5p
Cpolarized_capacitor20_5 N002 0 5p
Rresistor22_1 N001 N004 10
Rresistor22_2 N001 N002 1000meg
* switch25.1 open: not emitted
Vvoltage_source31_1 N005 N002 DC 0.001

.op
.save all
.tran 1us 100us

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
  "circuit_id": "b10",
  "source_format": "pipeline2.0_spice_emit_report",
  "emitted_elements": 13,
  "skipped_elements": 5,
  "skipped_components": [
    "gnd9.1",
    "terminal26.1",
    "terminal26.2",
    "terminal26.3",
    "terminal26.4"
  ],
  "informational_skips": [
    "gnd9.1: structural component not emitted",
    "terminal26.1: structural component not emitted",
    "terminal26.2: structural component not emitted",
    "terminal26.3: structural component not emitted",
    "terminal26.4: structural component not emitted"
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
  "models": [],
  "warnings": [
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
n001                                         1
n003                                         0
n002                                     0.001
n004                                         1
n005                                     0.002
vvoltage_source31_1#branch                   0
vvtest_c#branch                              0
vvtest_a#branch                         -1e-09


No. of Data Rows : 108
Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

No. of Data Rows : 1

Initial Transient Solution
--------------------------

Node                                   Voltage
----                                   -------
n001                                         1
n003                                         0
n002                                     0.001
n004                                         1
n005                                     0.002
vvoltage_source31_1#branch                   0
vvtest_c#branch                              0
vvtest_a#branch                         -1e-09


No. of Data Rows : 108
	Node                                  Voltage
	----                                  -------
	----	-------
	n005                             2.000000e-03
	n004                             1.000000e+00
	n002                             1.000000e-03
	n003                             0.000000e+00
	n001                             1.000000e+00

	Source	Current
	------	-------

	vvtest_a#branch                  -1.00000e-09
	vvtest_c#branch                  0.000000e+00
	vvoltage_source31_1#branch       0.000000e+00

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

 Capacitor: Fixed capacitor
     device cpolarized_capacitor2 cpolarized_capacitor2 cpolarized_capacitor2
      model                     C                     C                     C
capacitance                 5e-12                 5e-12                 5e-12
      dtemp                     0                     0                     0
     bv_max                 1e+99                 1e+99                 1e+99
          i          -1.51854e-20           1.51854e-20          -3.02923e-20
          p          -1.51854e-23          -1.51854e-23           -3.0262e-20

 Capacitor: Fixed capacitor
     device cpolarized_capacitor2 cpolarized_capacitor2
      model                     C                     C
capacitance                 5e-12                 5e-12
      dtemp                     0                     0
     bv_max                 1e+99                 1e+99
          i                     0                     0
          p                     0                     0

 Isource: Independent current source
     device    icurrent_source6_3    icurrent_source6_2    icurrent_source6_1
         dc                 1e-09                 1e-12                     0
          m                     1                     1                     1
      acmag                     0                     0                     0
      pulse         -         -         -
        sin         -         -         -
        exp         -         -         -
        pwl         -         -         -
       sffm         -         -         -
         am         -         -         -
    trnoise         -         -         -
   trrandom         -         -         -
          v                -0.001                -0.999                    -1
          p                 1e-12              9.99e-13                     0
    current                 1e-09                 1e-12                     0

 Resistor: Simple linear resistor
     device         rresistor22_2         rresistor22_1
      model                     R                     R
 resistance                 1e+09                    10
         ac                 1e+09                    10
      dtemp                     0                     0
     bv_max                 1e+99                 1e+99
      noisy                     1                     1
          i              9.99e-10                     0
          p           9.98001e-10                     0

 Vsource: Independent voltage source
     device   vvoltage_source31_1              vvtest_c              vvtest_a
         dc                 0.001                     0                     1
      acmag                     0                     0                     0
      pulse         -         -         -
        sin         -         -         -
        exp         -         -         -
        pwl         -         -         -
       sffm         -         -         -
         am         -         -         -
    trnoise         -         -         -
   trrandom         -         -         -
    portnum                     0                     0                     0
         z0                     0                     0                     0
        pwr                     0                     0                     0
       freq                     0                     0                     0
      phase                     0                     0                     0
          i                     0          -1.60159e-20                -1e-09
          p                     0                    -0                -1e-09


Total analysis time (seconds) = 0.003978

Total elapsed time (seconds) = 0.141 

Total DRAM available = 32239.535 MB.
DRAM currently available = 16471.402 MB.
Maximum ngspice program size =   14.992 MB.
Current ngspice program size =   14.992 MB.


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
  "circuit_id": "b10",
  "user_problem": "Su A leggo 1 V, ma su B leggo quasi zero. È normale o c’è qualcosa che non va?",
  "pipeline2_output_dir": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b10",
  "summary": {
    "spice_status": "success",
    "spice_exit_code": 0,
    "spice_message": "ngspice completed successfully.",
    "emitted_elements": 13,
    "skipped_elements": 5,
    "emit_warnings_count": 1,
    "skipped_components_count": 5,
    "node_count": 6,
    "ground_groups_count": 1,
    "singleton_nodes_count": 0,
    "bound_components": 12,
    "missing_components": 0,
    "unsupported_components": 0,
    "spice_ready_components": 12,
    "rules_missing_components": 0,
    "has_tran_csv": true,
    "has_tran_plot": true,
    "led_profiles": {}
  },
  "artifacts": {
    "graph": {
      "step": "01",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b10\\01_graph.json",
      "role": "Graph JSON copied from Pipeline 1.0."
    },
    "normalized_circuit": {
      "step": "02",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b10\\02_normalized_circuit.json",
      "role": "Normalized circuit representation used by Pipeline 2.0."
    },
    "node_map": {
      "step": "03",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b10\\03_node_map.json",
      "role": "Maps component terminals to SPICE node names."
    },
    "values_bound": {
      "step": "04",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b10\\04_values_bound.json",
      "role": "Values and labels bound to graph components."
    },
    "component_rules": {
      "step": "06",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b10\\06_component_rules.json",
      "role": "SPICE conversion rules for each component."
    },
    "netlist": {
      "step": "07",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b10\\07_netlist.cir",
      "role": "Generated SPICE netlist."
    },
    "spice_emit_report": {
      "step": "07",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b10\\07_spice_emit_report.json",
      "role": "Report of emitted, skipped and warning components."
    },
    "spice_run": {
      "step": "08",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b10\\08_spice_run.json",
      "role": "Structured ngspice execution report."
    },
    "ngspice_stdout": {
      "step": "08",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b10\\08_ngspice_stdout.txt",
      "role": "Raw ngspice stdout log."
    },
    "ngspice_stderr": {
      "step": "08",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b10\\08_ngspice_stderr.txt",
      "role": "Raw ngspice stderr log."
    },
    "tran_csv": {
      "step": "08",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b10\\08_tran.csv",
      "role": "Clean transient CSV, when .tran data is available."
    },
    "tran_plot_png": {
      "step": "08",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b10\\08_tran_plot.png",
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
      "scenario_dir": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b10\\scenarios\\agent_scenario_1",
      "scenario_id": "agent_scenario_1",
      "title": "Verifica chiusura switch verso B",
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
        "requested_count": 4,
        "changed_count": 4,
        "activated_count": 1,
        "missing_count": 0,
        "expected_count": 3,
        "expectations_met_count": 3,
        "expectations_failed_count": 0,
        "expectations_missing_count": 0,
        "meaningful_improvement_count": 3,
        "quality_required": false,
        "quality_available": false,
        "quality_improved": false,
        "quality_acceptable": false,
        "quality_output_preserved": false,
        "base_thd": null,
        "scenario_thd": null
      },
      "led_profiles": {},
      "artifacts": {
        "scenario_definition": {
          "available": true,
          "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b10\\scenarios\\agent_scenario_1\\scenario.json",
          "role": "Scenario selected by the user and saved before execution."
        },
        "scenario_status": {
          "available": true,
          "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b10\\scenarios\\agent_scenario_1\\scenario_status.json",
          "role": "Current scenario status, SPICE status and diagnostic outcome."
        },
        "controlled_scenario_report": {
          "available": true,
          "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b10\\scenarios\\agent_scenario_1\\12_controlled_scenarios.json",
          "role": "Report produced by the controlled scenario runner."
        },
        "scenario_comparison": {
          "available": true,
          "path": "outputs\\pipeline2.0\\batchB\\experiment5\\agent\\b10\\scenarios\\agent_scenario_1\\scenario_comparison.json",
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
        "title": "Verifica chiusura switch verso B",
        "status": "spice_success",
        "spice_status": "success",
        "outcome_status": "partially_resolved",
        "outcome_label": "Ipotesi diagnostica confermata",
        "outcome_technical_label": "Diagnostic hypothesis confirmed",
        "outcome_reason": "I criteri dichiarati dal test diagnostico sono soddisfatti, ma lo scenario non applica una correzione del sintomo utente.",
        "stop_automation": false,
        "comparison_summary": {
          "requested_count": 4,
          "changed_count": 4,
          "activated_count": 1,
          "missing_count": 0,
          "expected_count": 3,
          "expectations_met_count": 3,
          "expectations_failed_count": 0,
          "expectations_missing_count": 0,
          "meaningful_improvement_count": 3,
          "quality_required": false,
          "quality_available": false,
          "quality_improved": false,
          "quality_acceptable": false,
          "quality_output_preserved": false,
          "base_thd": null,
          "scenario_thd": null
        },
        "quantity_summary": {
          "changed": [
            "v(N002)",
            "v(N005)",
            "i(Rresistor22_1)",
            "i(Rresistor22_2)"
          ],
          "unchanged": [],
          "missing": []
        },
        "led_profiles": {},
        "ranking_verified": true,
        "score": 65
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
    "path": "data\\batchB\\b10.jpg",
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
