# Pipeline 2.0 - agente diagnostico autonomo controllato

Sei il controller diagnostico di una pipeline Graph JSON -> SPICE/ngspice.
Devi scegliere il prossimo test controllato oppure fermarti con una conclusione.

## Sintomo utente
Il LED è già acceso, ma la lampada è spenta. Individua la causa ed esegui gli scenari necessari per accendere la lampada mantenendo acceso anche il LED.

## Vincoli obbligatori
- Rispondi con un solo oggetto JSON valido, senza Markdown o testo esterno.
- Non inventare nodi, componenti, valori o risultati.
- Usa soltanto queste primitive: add_resistor_between_nodes, add_voltage_source_between_nodes, change_component_value, change_source_value, close_switch, connect_nodes, drive_node_voltage, feed_nodes_from_source_node.
- Ogni scenario deve essere self-contained e partire dalla base run.
- Puoi proporre al massimo 2 scenari indipendenti.
- Budget residuo: 4 run scenario.
- Se il budget e zero devi restituire decision=stop.
- Non usare resolved_candidate come prova automatica di soluzione definitiva.
- Distingui una soluzione da una semplice localizzazione della causa.
- Ogni scenario deve avere una lista compare non vuota con grandezze osservabili.
- Per scenari con piu rami o uscite, includi in compare almeno una grandezza per ciascuno.
- Se l'obiettivo richiede di attivare o spegnere un componente, includi in compare
  almeno una misura diretta del componente, preferendo i(NOME_SPICE).
- Se l'obiettivo richiede di mantenere invariato un altro componente, includi in
  compare anche una sua misura diretta: le sole tensioni di nodo non ne verificano lo stato.
- Ricava NOME_SPICE dalla netlist 07_netlist.cir; non usare l'id Graph JSON dentro i(...) o p(...).
- Richiedi p(NOME_SPICE) soltanto se la potenza dello stesso dispositivo e gia
  disponibile negli output ngspice forniti; non aggiungere misure ridondanti.
- Ogni scenario deve avere un oggetto expect non vuoto. Le chiavi devono essere
  grandezze presenti in compare e i valori ammessi sono: activated, deactivated,
  changed, unchanged, increased, decreased, magnitude_increased,
  magnitude_decreased, nonzero.
- Usa expect per descrivere sia l'effetto cercato sia i vincoli da preservare,
  per esempio corrente del target activated e corrente del componente protetto unchanged.
- Per una run .tran usa le tracce disponibili e confronta almeno l'uscita o il ramo
  direttamente coinvolto nell'obiettivo, oltre agli eventuali nodi intermedi.
- Non dichiarare verified_correction se i confronti non misurano direttamente sia
  il componente target sia gli eventuali componenti che devono restare attivi.
- Preferisci modifiche minime su componenti, valori e collegamenti gia esistenti.
- Usa nuove sorgenti o nuovi rami resistivi solo quando le evidenze tecniche li giustificano.
- Usa feed_nodes_from_source_node solo da un nodo che gli output mostrano gia alimentato.
- Usa connect_nodes per una ipotesi di continuita mancante senza attribuire a un nodo il ruolo di sorgente.
- Non proporre connect_nodes e feed_nodes_from_source_node sulla stessa relazione tra nodi nella stessa decisione.
- Considera add_resistor_between_nodes una ipotesi distinta: aggiunge un vero accoppiamento resistivo, non un filo quasi ideale.

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
{"decision":"run_scenarios","reason":"...","scenarios":[{"title":"...","hypothesis":"...","actions":[{"type":"close_switch","target":"...","resistance":"1m"}],"compare":["i(RTARGET)","i(DPROTECTED)"],"expect":{"i(RTARGET)":"activated","i(DPROTECTED)":"unchanged"}}]}

oppure

{"decision":"stop","reason":"...","final_status":"resolved|localized|partially_localized|topology_issue|inconclusive","final_answer":"Sintesi breve della conclusione.","final_cause":"Causa tecnica individuata, senza ripetizioni.","verified_correction":"Correzione verificata dagli scenari, oppure stringa vuota se non verificata."}

## Decisioni e risultati precedenti
```json
[
  {
    "decision_number": 1,
    "decision": {
      "decision": "run_scenarios",
      "reason": "Dalla base run il LED è effettivamente acceso: i(Dled12_1)≈19.4 mA e N005≈0.732 V tramite Rresistor22_2 da VVCC. La lampada è spenta perché il suo ramo non è alimentato: N004=0 V e i(Rlamp13_1)=0, mentre anche N002=0 V, quindi il resistore Rresistor22_1 collega la lampada a un nodo flottante/non alimentato. La causa più probabile è l’assenza di alimentazione su N002, che dovrebbe essere portato al nodo già alimentato N001 per accendere la lampada senza alterare il ramo LED. Propongo un solo scenario minimo e self-contained che alimenta N002 dal nodo sorgente già noto come attivo.",
      "scenarios": [
        {
          "title": "Alimenta il ramo lampada portando N002 a VCC",
          "hypothesis": "La lampada è spenta perché il nodo N002, ingresso del ramo Rresistor22_1-Rlamp13_1, non è collegato alla sorgente da 5 V. Alimentando N002 dal nodo N001 già attivo, la corrente dovrebbe fluire in Rresistor22_1 e Rlamp13_1 accendendo la lampada, mentre il LED deve restare acceso.",
          "actions": [
            {
              "type": "feed_nodes_from_source_node",
              "source_node": "N001",
              "target_nodes": [
                "N002"
              ]
            }
          ],
          "compare": [
            "i(Rlamp13_1)",
            "i(Dled12_1)",
            "v(N004)",
            "v(N002)"
          ],
          "expect": {
            "i(Rlamp13_1)": "activated",
            "i(Dled12_1)": "unchanged",
            "v(N004)": "increased",
            "v(N002)": "changed"
          }
        }
      ]
    },
    "prompt_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a01\\experiment_chat\\autonomous_prompt_1.md",
    "response_paths": [
      "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a01\\experiment_chat\\autonomous_response_1_attempt_1.txt"
    ],
    "scenario_results": [
      {
        "scenario_id": "agent_scenario_1",
        "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a01\\scenarios\\agent_scenario_1",
        "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a01\\scenarios\\agent_scenario_1\\run",
        "status": "spice_success",
        "spice_executed": true,
        "spice_status": "success",
        "spice_exit_code": 0,
        "comparison_summary": {
          "requested_count": 4,
          "changed_count": 3,
          "activated_count": 3,
          "missing_count": 0,
          "expected_count": 4,
          "expectations_met_count": 4,
          "expectations_failed_count": 0,
          "expectations_missing_count": 0
        },
        "diagnostic_outcome": {
          "status": "resolved_candidate",
          "technical_label": "Candidate resolved",
          "label": "Criteri di successo soddisfatti",
          "reason": "Tutti i comportamenti attesi dichiarati dallo scenario sono verificati dagli output SPICE.",
          "user_message": "Lo scenario fornisce una conferma forte dell'ipotesi testata.",
          "stop_automation": true,
          "confidence": "medium",
          "next_step": "Ci sono gia evidenze forti per fermarsi qui e passare alla conclusione diagnostica."
        },
        "viewer": {
          "model": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a01\\scenarios\\agent_scenario_1\\run\\13_viewer_model.json",
          "layout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a01\\scenarios\\agent_scenario_1\\run\\14_viewer_layout.json",
          "svg": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a01\\scenarios\\agent_scenario_1\\run\\15_viewer.svg"
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
  "circuit_id": "a01",
  "source_format": "pipeline2.0_node_map",
  "nodes": [
    {
      "node_id": "0",
      "kind": "ground",
      "terminals": [
        "connector5.1_pin4",
        "gnd9.1_t1",
        "gnd9.2_t1",
        "gnd9.3_t1",
        "lamp13.1_t2",
        "led12.1_cathode",
        "switch25.1_t1"
      ],
      "terminal_count": 7,
      "source_groups": [
        [
          "connector5.1_pin4",
          "gnd9.2_t1"
        ],
        [
          "gnd9.1_t1",
          "switch25.1_t1"
        ],
        [
          "gnd9.3_t1",
          "lamp13.1_t2",
          "led12.1_cathode"
        ]
      ]
    },
    {
      "node_id": "N001",
      "kind": "normal",
      "terminals": [
        "connector5.1_pin1",
        "resistor22.2_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N002",
      "kind": "normal",
      "terminals": [
        "connector5.1_pin2",
        "resistor22.1_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N003",
      "kind": "normal",
      "terminals": [
        "connector5.1_pin3",
        "switch25.1_t2"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N004",
      "kind": "normal",
      "terminals": [
        "lamp13.1_t1",
        "resistor22.1_t2"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N005",
      "kind": "normal",
      "terminals": [
        "led12.1_anode",
        "resistor22.2_t2"
      ],
      "terminal_count": 2
    }
  ],
  "terminal_to_node": {
    "connector5.1_pin1": "N001",
    "connector5.1_pin2": "N002",
    "connector5.1_pin3": "N003",
    "connector5.1_pin4": "0",
    "gnd9.1_t1": "0",
    "gnd9.2_t1": "0",
    "gnd9.3_t1": "0",
    "lamp13.1_t1": "N004",
    "lamp13.1_t2": "0",
    "led12.1_anode": "N005",
    "led12.1_cathode": "0",
    "resistor22.1_t1": "N002",
    "resistor22.1_t2": "N004",
    "resistor22.2_t1": "N001",
    "resistor22.2_t2": "N005",
    "switch25.1_t1": "0",
    "switch25.1_t2": "N003"
  },
  "component_terminal_nodes": {
    "connector5.1": {
      "pin1": "N001",
      "pin2": "N002",
      "pin3": "N003",
      "pin4": "0"
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
    "lamp13.1": {
      "t1": "N004",
      "t2": "0"
    },
    "led12.1": {
      "anode": "N005",
      "cathode": "0"
    },
    "resistor22.1": {
      "t1": "N002",
      "t2": "N004"
    },
    "resistor22.2": {
      "t1": "N001",
      "t2": "N005"
    },
    "switch25.1": {
      "t1": "0",
      "t2": "N003"
    }
  },
  "warnings": {
    "ground_groups_count": 3,
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
    "ground_groups_count": 3,
    "terminal_to_node_count": 17,
    "singleton_nodes_count": 0
  }
}

```

## 06_component_rules.json
```text
{
  "circuit_id": "a01",
  "source_format": "pipeline2.0_component_rules",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_manual_values\\batchA\\a01_values.yaml",
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
        "terminal": "connector5.1_pin1",
        "type": "dc",
        "value": 5,
        "unit": "V",
        "reference": 0,
        "source": "manual_from_image_label",
        "label_text": "+5 V DC",
        "node": "N001"
      }
    }
  },
  "components": {
    "connector5.1": {
      "class_name": "Connector",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "Connector used for nodes, labels, and external interfaces."
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
    "lamp13.1": {
      "class_name": "Lamp",
      "status": "spice_ready",
      "spice_support": "equivalent",
      "spice_prefix": "R",
      "emit_as": "resistive_load",
      "node_order": [
        "t1",
        "t2"
      ],
      "nodes": [
        "N004",
        "0"
      ],
      "parameters": {
        "nominal_voltage": 5,
        "equivalent_resistance": 50,
        "unit": "V",
        "resistance_unit": "ohm",
        "source": "manual_spice_annotation",
        "label_text": "Lamp 5V; Req = 50 ohm",
        "spice": "resistive_load"
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
        "N005",
        "0"
      ],
      "parameters": {
        "model": "LED_RED",
        "source": "manual_assumption"
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
        "N004"
      ],
      "parameters": {
        "value": 1000,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "1k"
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
        "N005"
      ],
      "parameters": {
        "value": 220,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "220R"
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
        "0",
        "N003"
      ],
      "parameters": {
        "state": "open",
        "state_source": "graph_json_state",
        "state_confidence": 0.95,
        "source": "graph_json_state"
      },
      "strategy": "open_circuit"
    }
  },
  "simulation": {},
  "stats": {
    "components_total": 9,
    "spice_ready_components": 5,
    "not_emitted_components": 4,
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
* circuit: a01

VVCC N001 0 DC 5
Rlamp13_1 N004 0 50
Dled12_1 N005 0 LED_RED
Rresistor22_1 N002 N004 1000
Rresistor22_2 N001 N005 220
* switch25.1 open: not emitted

.model LED_RED D

.op
.end

```

## 07_spice_emit_report.json
```text
{
  "circuit_id": "a01",
  "source_format": "pipeline2.0_spice_emit_report",
  "emitted_elements": 5,
  "skipped_elements": 4,
  "skipped_components": [
    "connector5.1",
    "gnd9.1",
    "gnd9.2",
    "gnd9.3"
  ],
  "informational_skips": [
    "connector5.1: structural component not emitted",
    "gnd9.1: structural component not emitted",
    "gnd9.2: structural component not emitted",
    "gnd9.3: structural component not emitted"
  ],
  "measurement_points": [],
  "analyses": [
    "op"
  ],
  "transient_export": {
    "path": null,
    "nodes": []
  },
  "models": [
    "LED_RED"
  ],
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
	Node                                  Voltage
	----                                  -------
	----	-------
	n002                             0.000000e+00
	n005                             7.318156e-01
	n004                             0.000000e+00
	n001                             5.000000e+00

	Source	Current
	------	-------

	vvcc#branch                      -1.94008e-02

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

 Diode: Junction Diode model
     device              dled12_1
      model               led_red
    thermal                     0
         vd              0.731816
         id             0.0194009
         gd              0.750084
         cd                     0

 Resistor: Simple linear resistor
     device         rresistor22_2         rresistor22_1             rlamp13_1
      model                     R                     R                     R
 resistance                   220                  1000                    50
         ac                   220                  1000                    50
      dtemp                     0                     0                     0
     bv_max                 1e+99                 1e+99                 1e+99
      noisy                     1                     1                     1
          i             0.0194008                     0                     0
          p             0.0828064                     0                     0

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
          i            -0.0194008
          p            -0.0970042


Total analysis time (seconds) = 0.0056283

Total elapsed time (seconds) = 0.159 

Total DRAM available = 32239.535 MB.
DRAM currently available = 16439.156 MB.
Maximum ngspice program size =   15.273 MB.
Current ngspice program size =   15.273 MB.


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
  "circuit_id": "a01",
  "user_problem": "Il LED è già acceso, ma la lampada è spenta. Individua la causa ed esegui gli scenari necessari per accendere la lampada mantenendo acceso anche il LED.",
  "pipeline2_output_dir": "outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a01",
  "summary": {
    "spice_status": "success",
    "spice_exit_code": 0,
    "spice_message": "ngspice completed successfully.",
    "emitted_elements": 5,
    "skipped_elements": 4,
    "emit_warnings_count": 1,
    "skipped_components_count": 4,
    "node_count": 6,
    "ground_groups_count": 3,
    "singleton_nodes_count": 0,
    "bound_components": 5,
    "missing_components": 0,
    "unsupported_components": 0,
    "spice_ready_components": 5,
    "rules_missing_components": 0,
    "has_tran_csv": false,
    "has_tran_plot": false
  },
  "artifacts": {
    "graph": {
      "step": "01",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a01\\01_graph.json",
      "role": "Graph JSON copied from Pipeline 1.0."
    },
    "normalized_circuit": {
      "step": "02",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a01\\02_normalized_circuit.json",
      "role": "Normalized circuit representation used by Pipeline 2.0."
    },
    "node_map": {
      "step": "03",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a01\\03_node_map.json",
      "role": "Maps component terminals to SPICE node names."
    },
    "values_bound": {
      "step": "04",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a01\\04_values_bound.json",
      "role": "Values and labels bound to graph components."
    },
    "component_rules": {
      "step": "06",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a01\\06_component_rules.json",
      "role": "SPICE conversion rules for each component."
    },
    "netlist": {
      "step": "07",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a01\\07_netlist.cir",
      "role": "Generated SPICE netlist."
    },
    "spice_emit_report": {
      "step": "07",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a01\\07_spice_emit_report.json",
      "role": "Report of emitted, skipped and warning components."
    },
    "spice_run": {
      "step": "08",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a01\\08_spice_run.json",
      "role": "Structured ngspice execution report."
    },
    "ngspice_stdout": {
      "step": "08",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a01\\08_ngspice_stdout.txt",
      "role": "Raw ngspice stdout log."
    },
    "ngspice_stderr": {
      "step": "08",
      "available": true,
      "path": "outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a01\\08_ngspice_stderr.txt",
      "role": "Raw ngspice stderr log."
    },
    "tran_csv": {
      "step": "08",
      "available": false,
      "path": null,
      "role": "Clean transient CSV, when .tran data is available."
    },
    "tran_plot_png": {
      "step": "08",
      "available": false,
      "path": null,
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
      "scenario_dir": "outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a01\\scenarios\\agent_scenario_1",
      "scenario_id": "agent_scenario_1",
      "title": "Alimenta il ramo lampada portando N002 a VCC",
      "status": "spice_success",
      "spice_status": "success",
      "diagnostic_outcome": {
        "status": "resolved_candidate",
        "technical_label": "Candidate resolved",
        "label": "Criteri di successo soddisfatti",
        "reason": "Tutti i comportamenti attesi dichiarati dallo scenario sono verificati dagli output SPICE.",
        "user_message": "Lo scenario fornisce una conferma forte dell'ipotesi testata.",
        "stop_automation": true,
        "confidence": "medium",
        "next_step": "Ci sono gia evidenze forti per fermarsi qui e passare alla conclusione diagnostica."
      },
      "comparison_summary": {
        "requested_count": 4,
        "changed_count": 3,
        "activated_count": 3,
        "missing_count": 0,
        "expected_count": 4,
        "expectations_met_count": 4,
        "expectations_failed_count": 0,
        "expectations_missing_count": 0
      },
      "artifacts": {
        "scenario_definition": {
          "available": true,
          "path": "outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a01\\scenarios\\agent_scenario_1\\scenario.json",
          "role": "Scenario selected by the user and saved before execution."
        },
        "scenario_status": {
          "available": true,
          "path": "outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a01\\scenarios\\agent_scenario_1\\scenario_status.json",
          "role": "Current scenario status, SPICE status and diagnostic outcome."
        },
        "controlled_scenario_report": {
          "available": true,
          "path": "outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a01\\scenarios\\agent_scenario_1\\12_controlled_scenarios.json",
          "role": "Report produced by the controlled scenario runner."
        },
        "scenario_comparison": {
          "available": true,
          "path": "outputs\\pipeline2.0\\batchA\\experiment4\\agent\\a01\\scenarios\\agent_scenario_1\\scenario_comparison.json",
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
    "interpretation_rule": "If a user asks which scenario resolves the problem, prefer the scenario with outcome_status='resolved_candidate' and stop_automation=true. Partially resolved scenarios are supporting diagnostics, not the main solution.",
    "scenarios": [
      {
        "scenario_id": "agent_scenario_1",
        "title": "Alimenta il ramo lampada portando N002 a VCC",
        "status": "spice_success",
        "spice_status": "success",
        "outcome_status": "resolved_candidate",
        "outcome_label": "Criteri di successo soddisfatti",
        "outcome_technical_label": "Candidate resolved",
        "outcome_reason": "Tutti i comportamenti attesi dichiarati dallo scenario sono verificati dagli output SPICE.",
        "stop_automation": true,
        "comparison_summary": {
          "requested_count": 4,
          "changed_count": 3,
          "activated_count": 3,
          "missing_count": 0,
          "expected_count": 4,
          "expectations_met_count": 4,
          "expectations_failed_count": 0,
          "expectations_missing_count": 0
        },
        "quantity_summary": {
          "changed": [
            "i(Rlamp13_1)",
            "v(N004)",
            "v(N002)"
          ],
          "unchanged": [
            "i(Dled12_1)"
          ],
          "missing": []
        },
        "score": 183
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
    "path": "data\\batchA\\a01.png",
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
