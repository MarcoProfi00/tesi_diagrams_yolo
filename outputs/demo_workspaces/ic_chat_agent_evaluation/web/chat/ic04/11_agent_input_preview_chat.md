# Agent input preview

This file is a local preview of the evidence that will be provided to the read-only diagnostic agent.
The agent remains read-only: it can inspect base outputs and existing scenario artifacts, but it does not modify files.

## User problem

Ho eseguito lo scenario 2 e il cambio tra i due toni ora è più evidente. Interpreta il risultato e dammi la conclusione finale, senza proporre altri scenari.

## Circuit

- Batch: `batchICChatAgentEvaluation`
- Circuit: `ic04`
- Agent mode: `graph_grounded_readonly`

## Technical summary

```json
{
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_message": "ngspice completed successfully.",
  "emitted_elements": 14,
  "skipped_elements": 2,
  "emit_warnings_count": 0,
  "skipped_components_count": 2,
  "node_count": 11,
  "ground_groups_count": 1,
  "singleton_nodes_count": 0,
  "bound_components": 11,
  "missing_components": 0,
  "unsupported_components": 2,
  "spice_ready_components": 13,
  "rules_missing_components": 0,
  "has_tran_csv": true,
  "has_tran_plot": true,
  "led_profiles": {
    "Dled12_1": {
      "state": "transient_pulse",
      "regular_period": false,
      "frequency_hz": null,
      "duty_cycle": 0.35726052471018915,
      "on_fraction": 0.35726052471018915,
      "pulse_count": 7,
      "voltage_min": -7.999833428856001,
      "voltage_max": 0.4599163977,
      "anode_node": "N002",
      "cathode_node": "N003"
    }
  }
}
```

## Image policy

- Included by default: `False`
- Can be requested: `True`
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\input\images\ic04.jpg`
- Policy: Only request the image if structured outputs suggest that the Graph JSON may be incomplete or wrong.

## Agent rules

- Treat this file as a manifest, not as the full diagnostic evidence.
- Load the referenced artifacts needed for the answer.
- Use graph, node map, component rules, netlist, stdout and stderr as evidence.
- If executed_scenarios are available, use them as evidence for questions about scenario outcomes.
- Do not invent values, connections, models or simulation results.
- Do not use the image unless image_access is explicitly requested.
- If Graph JSON inconsistency is suspected, explain which structured outputs suggest it.
- In read-only mode, do not modify netlists and do not execute scenarios.
- Never exceed 5 executed scenarios for the same circuit.
- When the scenario budget is exhausted, stop proposing new scenarios and provide a final diagnostic conclusion.

## Scenario outcome summary

```json
{
  "available": true,
  "best_scenario_id": "scenario_2",
  "best_outcome_status": "partially_resolved",
  "best_stop_automation": false,
  "ranking_status": "verified_best",
  "interpretation_rule": "If a user asks which scenario resolves the problem, prefer the scenario with outcome_status='resolved_candidate' and stop_automation=true. Partially resolved scenarios without verified expectations are supporting diagnostics and must not be ranked only by changed_count.",
  "scenarios": [
    {
      "scenario_id": "scenario_2",
      "title": "Aumentare il collegamento di modulazione tra i due 555",
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
        "activated_count": 0,
        "missing_count": 0,
        "expected_count": 2,
        "expectations_met_count": 2,
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
        "gain_required": true,
        "gain_available": true,
        "gain_sufficient": true,
        "scenario_gain": 1.093607549735132,
        "min_gain_ratio": 0.05
      },
      "quantity_summary": {
        "changed": [
          "v(N004)",
          "v(N006)",
          "v(N009)",
          "v(N010)"
        ],
        "unchanged": [],
        "missing": []
      },
      "led_profiles": {
        "Dled12_1": {
          "state": "transient_pulse",
          "regular_period": false,
          "frequency_hz": null,
          "duty_cycle": 0.999971725254296,
          "on_fraction": 0.999971725254296,
          "pulse_count": 5,
          "voltage_min": -8.001213278246,
          "voltage_max": 0.45991638309999994,
          "anode_node": "N002",
          "cathode_node": "N003"
        }
      },
      "ranking_verified": true,
      "score": 30
    }
  ]
}
```


## Executed scenarios

### scenario_2

- Title: `Aumentare il collegamento di modulazione tra i due 555`
- Status: `spice_success`
- SPICE status: `success`
- Outcome: `partially_resolved`
- Stop automation: `False`
- Comparison: `4/4` changed
- LED profiles: `{"Dled12_1": {"state": "transient_pulse", "regular_period": false, "frequency_hz": null, "duty_cycle": 0.999971725254296, "on_fraction": 0.999971725254296, "pulse_count": 5, "voltage_min": -8.001213278246, "voltage_max": 0.45991638309999994, "anode_node": "N002", "cathode_node": "N003"}}`
- Temporal profiles: `{}`

#### scenario_definition

- Role: Scenario selected by the user and saved before execution.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic04\scenarios\scenario_2\scenario.json`

```json
{
  "scenario_id": "scenario_2",
  "title": "Aumentare il collegamento di modulazione tra i due 555",
  "hypothesis": "Il tono cambia poco perche la modulazione dal primo 555 al secondo, attraverso Rresistor22_3, e troppo debole.",
  "intent": "diagnostic",
  "actions": [
    {
      "type": "change_component_value",
      "target": "Rresistor22_3",
      "value": "4.7k"
    }
  ],
  "rerun_from": "04",
  "analysis": "tran",
  "compare": [
    "v(N004)",
    "v(N006)",
    "v(N009)",
    "v(N010)"
  ],
  "expect": {
    "v(N006)": "changed",
    "v(N010)": "changed"
  },
  "gain": {
    "input": "v(N004)",
    "output": "v(N010)",
    "min_ratio": 0.05
  }
}
```

#### scenario_status

- Role: Current scenario status, SPICE status and diagnostic outcome.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic04\scenarios\scenario_2\scenario_status.json`

```json
{
  "status": "spice_success",
  "stage": "scenario_spice_executed",
  "scenario_id": "scenario_2",
  "source": "guided_chat",
  "spice_executed": true,
  "created_or_updated_at": "2026-08-03T16:47:24",
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic04\\scenarios\\scenario_2\\run\\08_spice_run.json",
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic04\\scenarios\\scenario_2\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 4,
    "changed_count": 4,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 2,
    "expectations_met_count": 2,
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
    "gain_required": true,
    "gain_available": true,
    "gain_sufficient": true,
    "scenario_gain": 1.093607549735132,
    "min_gain_ratio": 0.05
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
  "controlled_scenario_report": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic04\\scenarios\\scenario_2\\12_controlled_scenarios.json",
  "executed_scenarios_count": 1,
  "scenario_budget_exhausted": false,
  "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
}
```

#### controlled_scenario_report

- Role: Report produced by the controlled scenario runner.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic04\scenarios\scenario_2\12_controlled_scenarios.json`

```json
{
  "source_format": "pipeline2.0_controlled_scenario_report",
  "status": "spice_success",
  "scenario_id": "scenario_2",
  "scenario_title": "Aumentare il collegamento di modulazione tra i due 555",
  "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic04\\scenarios\\scenario_2",
  "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic04\\scenarios\\scenario_2\\run",
  "netlist": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic04\\scenarios\\scenario_2\\run\\07_netlist.cir",
  "applied_actions": [
    {
      "status": "applied",
      "type": "change_component_value",
      "target": "Rresistor22_3",
      "resolved_component_name": "Rresistor22_3",
      "tried_component_names": [
        "Rresistor22_3"
      ],
      "value": "4.7k",
      "normalized_component_value": "4.7k",
      "old_value": "10k",
      "new_value": "4.7k",
      "old_line": "Rresistor22_3 N004 N006 10k",
      "new_line": "Rresistor22_3 N004 N006 4.7k",
      "operation": "updated",
      "spice_executed": false,
      "index": 1
    }
  ],
  "unsupported_actions": [],
  "failed_actions": [],
  "spice_executed": true,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic04\\scenarios\\scenario_2\\run\\08_spice_run.json",
  "spice_status": "success",
  "spice_exit_code": 0,
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic04\\scenarios\\scenario_2\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 4,
    "changed_count": 4,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 2,
    "expectations_met_count": 2,
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
    "gain_required": true,
    "gain_available": true,
    "gain_sufficient": true,
    "scenario_gain": 1.093607549735132,
    "min_gain_ratio": 0.05
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
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "created_or_updated_at": "2026-08-03T16:47:24"
}
```

#### scenario_comparison

- Role: Base-vs-scenario comparison used to evaluate the scenario.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic04\scenarios\scenario_2\scenario_comparison.json`

```json
{
  "source_format": "pipeline2.0_scenario_comparison",
  "scenario_id": "scenario_2",
  "scenario_title": "Aumentare il collegamento di modulazione tra i due 555",
  "scenario_intent": "diagnostic",
  "base_output_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic04",
  "scenario_run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic04\\scenarios\\scenario_2\\run",
  "base_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic04\\08_ngspice_stdout.txt",
  "scenario_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic04\\scenarios\\scenario_2\\run\\08_ngspice_stdout.txt",
  "base_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic04\\08_ngspice_stderr.txt",
  "scenario_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic04\\scenarios\\scenario_2\\run\\08_ngspice_stderr.txt",
  "quantities": [
    {
      "quantity": "v(N004)",
      "base_value": 11.99156404371,
      "scenario_value": 11.99694163887,
      "delta": 0.005377595160000581,
      "change": "changed",
      "expectation": null,
      "expectation_met": null,
      "relative_change": 0.0004484481874423479,
      "meaningful_improvement": false,
      "metric": "v(n004).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": 0.00289055629,
        "max": 11.9944546,
        "mean": 4.287043773989828,
        "vpp": 11.99156404371,
        "final": 0.00423541708,
        "abs_peak": 11.9944546
      },
      "scenario_details": {
        "min": 0.00309086113,
        "max": 12.0000325,
        "mean": 3.1606997049928416,
        "vpp": 11.99694163887,
        "final": 0.00567372153,
        "abs_peak": 12.0000325
      }
    },
    {
      "quantity": "v(N006)",
      "base_value": 7.41443745,
      "scenario_value": 9.26342215,
      "delta": 1.8489847,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 0.24937626252413794,
      "meaningful_improvement": false,
      "metric": "v(n006).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": 3.31501805,
        "max": 10.7294555,
        "mean": 5.986207756919463,
        "vpp": 7.41443745,
        "final": 3.3519385,
        "abs_peak": 10.7294555
      },
      "scenario_details": {
        "min": 2.05959865,
        "max": 11.3230208,
        "mean": 4.532055880781302,
        "vpp": 9.26342215,
        "final": 2.11327647,
        "abs_peak": 11.3230208
      }
    },
    {
      "quantity": "v(N009)",
      "base_value": 10.252849737,
      "scenario_value": 10.772842872,
      "delta": 0.519993135,
      "change": "changed",
      "expectation": null,
      "expectation_met": null,
      "relative_change": 0.050716937079792884,
      "meaningful_improvement": false,
      "metric": "v(n009).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": 0.473667463,
        "max": 10.7265172,
        "mean": 4.621322911098185,
        "vpp": 10.252849737,
        "final": 0.495492839,
        "abs_peak": 10.7265172
      },
      "scenario_details": {
        "min": 0.245200828,
        "max": 11.0180437,
        "mean": 4.26015356420437,
        "vpp": 10.772842872,
        "final": 0.321696241,
        "abs_peak": 11.0180437
      }
    },
    {
      "quantity": "v(N010)",
      "base_value": 12.0909431,
      "scenario_value": 13.119945950000002,
      "delta": 1.0290028500000012,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 0.0851052594896424,
      "meaningful_improvement": false,
      "metric": "v(n010).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": -7.65971694,
        "max": 4.43122616,
        "mean": -0.5687921196580232,
        "vpp": 12.0909431,
        "final": -2.45156379,
        "abs_peak": 7.65971694
      },
      "scenario_details": {
        "min": -8.14925958,
        "max": 4.97068637,
        "mean": 0.15566341622092475,
        "vpp": 13.119945950000002,
        "final": -1.60428458,
        "abs_peak": 8.14925958
      }
    }
  ],
  "summary": {
    "requested_count": 4,
    "changed_count": 4,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 2,
    "expectations_met_count": 2,
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
    "gain_required": true,
    "gain_available": true,
    "gain_sufficient": true,
    "scenario_gain": 1.093607549735132,
    "min_gain_ratio": 0.05
  },
  "gain_comparison": {
    "input": "v(N004)",
    "output": "v(N010)",
    "base_gain": 1.0082874140460543,
    "scenario_gain": 1.093607549735132,
    "min_ratio": 0.05,
    "available": true,
    "sufficient": true,
    "relative_change": 0.08461886412595918
  },
  "quality_comparison": null,
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
  "created_or_updated_at": "2026-08-03T16:47:24"
}
```


## Loaded artifacts

### graph

- Step: `01`
- Role: Graph JSON copied from Pipeline 1.0.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic04\01_graph.json`

```json
{
  "image_id": "ic04",
  "image_name": "ic04.jpg",
  "components": [
    {
      "component_id": "led12.1",
      "instance_id": "12.1",
      "class_name": "LED",
      "terminals": [
        {
          "terminal_id": "led12.1_anode",
          "name": "anode",
          "relative_position": "top"
        },
        {
          "terminal_id": "led12.1_cathode",
          "name": "cathode",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "polarized_capacitor20.1",
      "instance_id": "20.1",
      "class_name": "Polarized_Capacitor",
      "terminals": [
        {
          "terminal_id": "polarized_capacitor20.1_positive",
          "name": "positive",
          "relative_position": "top"
        },
        {
          "terminal_id": "polarized_capacitor20.1_negative",
          "name": "negative",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "resistor22.1",
      "instance_id": "22.1",
      "class_name": "Resistor",
      "terminals": [
        {
          "terminal_id": "resistor22.1_t1",
          "name": "t1",
          "relative_position": "top"
        },
        {
          "terminal_id": "resistor22.1_t2",
          "name": "t2",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "resistor22.2",
      "instance_id": "22.2",
      "class_name": "Resistor",
      "terminals": [
        {
          "terminal_id": "resistor22.2_t1",
          "name": "t1",
          "relative_position": "top"
        },
        {
          "terminal_id": "resistor22.2_t2",
          "name": "t2",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "integrated_circuit11.1",
      "instance_id": "11.1",
      "class_name": "Integrated_Circuit",
      "terminals": [
        {
          "terminal_id": "integrated_circuit11.1_left_1",
          "name": "left_1",
          "relative_position": "left",
          "display_name": "NE555 left_1 pin7",
          "pin_number": "7"
        },
        {
          "terminal_id": "integrated_circuit11.1_left_2",
          "name": "left_2",
          "relative_position": "left",
          "display_name": "NE555 left_2 pin6",
          "pin_number": "6"
        },
        {
          "terminal_id": "integrated_circuit11.1_left_3",
          "name": "left_3",
          "relative_position": "left",
          "display_name": "NE555 left_3 pin2",
          "pin_number": "2"
        },
        {
          "terminal_id": "integrated_circuit11.1_right_1",
          "name": "right_1",
          "relative_position": "right",
          "display_name": "NE555 right_1 pin3",
          "pin_number": "3"
        },
        {
          "terminal_id": "integrated_circuit11.1_top_1",
          "name": "top_1",
          "relative_position": "top",
          "display_name": "NE555 top_1 pin4",
          "pin_number": "4"
        },
        {
          "terminal_id": "integrated_circuit11.1_top_2",
          "name": "top_2",
          "relative_position": "top",
          "display_name": "NE555 top_2 pin8",
          "pin_number": "8"
        },
        {
          "terminal_id": "integrated_circuit11.1_bottom_1",
          "name": "bottom_1",
          "relative_position": "bottom",
          "display_name": "NE555 bottom_1 pin1",
          "pin_number": "1"
        },
        {
          "terminal_id": "integrated_circuit11.1_bottom_2",
          "name": "bottom_2",
          "relative_position": "bottom",
          "display_name": "NE555 bottom_2 pin5",
          "pin_number": "5"
        }
      ],
      "display_name": "NE555",
      "ic_marking": "NE555"
    },
    {
      "component_id": "polarized_capacitor20.2",
      "instance_id": "20.2",
      "class_name": "Polarized_Capacitor",
      "terminals": [
        {
          "terminal_id": "polarized_capacitor20.2_positive",
          "name": "positive",
          "relative_position": "top"
        },
        {
          "terminal_id": "polarized_capacitor20.2_negative",
          "name": "negative",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "resistor22.3",
      "instance_id": "22.3",
      "class_name": "Resistor",
      "terminals": [
        {
          "terminal_id": "resistor22.3_t1",
          "name": "t1",
          "relative_position": "top"
        },
        {
          "terminal_id": "resistor22.3_t2",
          "name": "t2",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "gnd9.1",
      "instance_id": "9.1",
      "class_name": "GND",
      "terminals": [
        {
          "terminal_id": "gnd9.1_t1",
          "name": "t1",
          "relative_position": "top"
        }
      ]
    },
    {
      "component_id": "polarized_capacitor20.3",
      "instance_id": "20.3",
      "class_name": "Polarized_Capacitor",
      "terminals": [
        {
          "terminal_id": "polarized_capacitor20.3_positive",
          "name": "positive",
          "relative_position": "top"
        },
        {
          "terminal_id": "polarized_capacitor20.3_negative",
          "name": "negative",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "resistor22.4",
      "instance_id": "22.4",
      "class_name": "Resistor",
      "terminals": [
        {
          "terminal_id": "resistor22.4_t1",
          "name": "t1",
          "relative_position": "top"
        },
        {
          "terminal_id": "resistor22.4_t2",
          "name": "t2",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "resistor22.5",
      "instance_id": "22.5",
      "class_name": "Resistor",
      "terminals": [
        {
          "terminal_id": "resistor22.5_t1",
          "name": "t1",
          "relative_position": "top"
        },
        {
          "terminal_id": "resistor22.5_t2",
          "name": "t2",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "integrated_circuit11.2",
      "instance_id": "11.2",
      "class_name": "Integrated_Circuit",
      "terminals": [
        {
          "terminal_id": "integrated_circuit11.2_left_1",
          "name": "left_1",
          "relative_position": "left",
          "display_name": "NE555 left_1 pin7",
          "pin_number": "7"
        },
        {
          "terminal_id": "integrated_circuit11.2_left_2",
          "name": "left_2",
          "relative_position": "left",
          "display_name": "NE555 left_2 pin6",
          "pin_number": "6"
        },
        {
          "terminal_id": "integrated_circuit11.2_left_3",
          "name": "left_3",
          "relative_position": "left",
          "display_name": "NE555 left_3 pin2",
          "pin_number": "2"
        },
        {
          "terminal_id": "integrated_circuit11.2_right_1",
          "name": "right_1",
          "relative_position": "right",
          "display_name": "NE555 right_1 pin3",
          "pin_number": "3"
        },
        {
          "terminal_id": "integrated_circuit11.2_top_1",
          "name": "top_1",
          "relative_position": "top",
          "display_name": "NE555 top_1 pin4",
          "pin_number": "4"
        },
        {
          "terminal_id": "integrated_circuit11.2_top_2",
          "name": "top_2",
          "relative_position": "top",
          "display_name": "NE555 top_2 pin8",
          "pin_number": "8"
        },
        {
          "terminal_id": "integrated_circuit11.2_bottom_1",
          "name": "bottom_1",
          "relative_position": "bottom",
          "display_name": "NE555 bottom_1 pin1",
          "pin_number": "1"
        },
        {
          "terminal_id": "integrated_circuit11.2_bottom_2",
          "name": "bottom_2",
          "relative_position": "bottom",
          "display_name": "NE555 bottom_2 pin5",
          "pin_number": "5"
        }
      ],
      "display_name": "NE555",
      "ic_marking": "NE555"
    },
    {
      "component_id": "terminal26.1",
      "instance_id": "26.1",
      "class_name": "Terminal",
      "terminals": [
        {
          "terminal_id": "terminal26.1_t1",
          "name": "t1",
          "relative_position": "left"
        }
      ]
    },
    {
      "component_id": "polarized_capacitor20.4",
      "instance_id": "20.4",
      "class_name": "Polarized_Capacitor",
      "terminals": [
        {
          "terminal_id": "polarized_capacitor20.4_positive",
          "name": "positive",
          "relative_position": "top"
        },
        {
          "terminal_id": "polarized_capacitor20.4_negative",
          "name": "negative",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "speaker24.1",
      "instance_id": "24.1",
      "class_name": "Speaker",
      "terminals": [
        {
          "terminal_id": "speaker24.1_t1",
          "name": "t1",
          "relative_position": "left"
        },
        {
          "terminal_id": "speaker24.1_t2",
          "name": "t2",
          "relative_position": "left"
        }
      ]
    }
  ],
  "terminal_metadata": {
    "integrated_circuit11.1_bottom_1": {
      "display_name": "NE555 bottom_1 pin1",
      "pin_number": "1",
      "component_display_name": "NE555",
      "ic_marking": "NE555",
      "component_id": "integrated_circuit11.1",
      "class_name": "Integrated_Circuit"
    },
    "integrated_circuit11.1_bottom_2": {
      "display_name": "NE555 bottom_2 pin5",
      "pin_number": "5",
      "component_display_name": "NE555",
      "ic_marking": "NE555",
      "component_id": "integrated_circuit11.1",
      "class_name": "Integrated_Circuit"
    },
    "integrated_circuit11.1_left_1": {
      "display_name": "NE555 left_1 pin7",
      "pin_number": "7",
      "component_display_name": "NE555",
      "ic_marking": "NE555",
      "component_id": "integrated_circuit11.1",
      "class_name": "Integrated_Circuit"
    },
    "integrated_circuit11.1_left_2": {
      "display_name": "NE555 left_2 pin6",
      "pin_number": "6",
      "component_display_name": "NE555",
      "ic_marking": "NE555",
      "component_id": "integrated_circuit11.1",
      "class_name": "Integrated_Circuit"
    },
    "integrated_circuit11.1_left_3": {
      "display_name": "NE555 left_3 pin2",
      "pin_number": "2",
      "component_display_name": "NE555",
      "ic_marking": "NE555",
      "component_id": "integrated_circuit11.1",
      "class_name": "Integrated_Circuit"
    },
    "integrated_circuit11.1_right_1": {
      "display_name": "NE555 right_1 pin3",
      "pin_number": "3",
      "component_display_name": "NE555",
      "ic_marking": "NE555",
      "component_id": "integrated_circuit11.1",
      "class_name": "Integrated_Circuit"
    },
    "integrated_circuit11.1_top_1": {
      "display_name": "NE555 top_1 pin4",
      "pin_number": "4",
      "component_display_name": "NE555",
      "ic_marking": "NE555",
      "component_id": "integrated_circuit11.1",
      "class_name": "Integrated_Circuit"
    },
    "integrated_circuit11.1_top_2": {
      "display_name": "NE555 top_2 pin8",
      "pin_number": "8",
      "component_display_name": "NE555",
      "ic_marking": "NE555",
      "component_id": "integrated_circuit11.1",
      "class_name": "Integrated_Circuit"
    },
    "integrated_circuit11.2_bottom_1": {
      "display_name": "NE555 bottom_1 pin1",
      "pin_number": "1",
      "component_display_name": "NE555",
      "ic_marking": "NE555",
      "component_id": "integrated_circuit11.2",
      "class_name": "Integrated_Circuit"
    },
    "integrated_circuit11.2_bottom_2": {
      "display_name": "NE555 bottom_2 pin5",
      "pin_number": "5",
      "component_display_name": "NE555",
      "ic_marking": "NE555",
      "component_id": "integrated_circuit11.2",
      "class_name": "Integrated_Circuit"
    },
    "integrated_circuit11.2_left_1
```

> Artifact truncated in this preview. The original file remains available through the manifest path.

### node_map

- Step: `03`
- Role: Maps component terminals to SPICE node names.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic04\03_node_map.json`

```json
{
  "circuit_id": "ic04",
  "source_format": "pipeline2.0_node_map",
  "nodes": [
    {
      "node_id": "0",
      "kind": "ground",
      "terminals": [
        "gnd9.1_t1",
        "integrated_circuit11.1_bottom_1",
        "integrated_circuit11.2_bottom_1",
        "polarized_capacitor20.1_negative",
        "polarized_capacitor20.2_negative",
        "polarized_capacitor20.3_negative",
        "speaker24.1_t2"
      ],
      "terminal_count": 7,
      "source_groups": [
        [
          "gnd9.1_t1",
          "integrated_circuit11.1_bottom_1",
          "integrated_circuit11.2_bottom_1",
          "polarized_capacitor20.1_negative",
          "polarized_capacitor20.2_negative",
          "polarized_capacitor20.3_negative",
          "speaker24.1_t2"
        ]
      ]
    },
    {
      "node_id": "N001",
      "kind": "normal",
      "terminals": [
        "integrated_circuit11.1_bottom_2",
        "polarized_capacitor20.2_positive"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N002",
      "kind": "normal",
      "terminals": [
        "integrated_circuit11.1_left_1",
        "led12.1_anode",
        "resistor22.1_t1",
        "resistor22.2_t2"
      ],
      "terminal_count": 4
    },
    {
      "node_id": "N003",
      "kind": "normal",
      "terminals": [
        "integrated_circuit11.1_left_2",
        "integrated_circuit11.1_left_3",
        "led12.1_cathode",
        "polarized_capacitor20.1_positive",
        "resistor22.1_t2"
      ],
      "terminal_count": 5
    },
    {
      "node_id": "N004",
      "kind": "normal",
      "terminals": [
        "integrated_circuit11.1_right_1",
        "resistor22.3_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N005",
      "kind": "normal",
      "terminals": [
        "integrated_circuit11.1_top_1",
        "integrated_circuit11.1_top_2",
        "integrated_circuit11.2_top_1",
        "integrated_circuit11.2_top_2",
        "resistor22.2_t1",
        "resistor22.5_t1",
        "terminal26.1_t1"
      ],
      "terminal_count": 7
    },
    {
      "node_id": "N006",
      "kind": "normal",
      "terminals": [
        "integrated_circuit11.2_bottom_2",
        "resistor22.3_t2"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N007",
      "kind": "normal",
      "terminals": [
        "integrated_circuit11.2_left_1",
        "resistor22.4_t1",
        "resistor22.5_t2"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N008",
      "kind": "normal",
      "terminals": [
        "integrated_circuit11.2_left_2",
        "integrated_circuit11.2_left_3",
        "polarized_capacitor20.3_positive",
        "resistor22.4_t2"
      ],
      "terminal_count": 4
    },
    {
      "node_id": "N009",
      "kind": "normal",
      "terminals": [
        "integrated_circuit11.2_right_1",
        "polarized_capacitor20.4_positive"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N010",
      "kind": "normal",
      "terminals": [
        "polarized_capacitor20.4_negative",
        "speaker24.1_t1"
      ],
      "terminal_count": 2
    }
  ],
  "terminal_to_node": {
    "gnd9.1_t1": "0",
    "integrated_circuit11.1_bottom_1": "0",
    "integrated_circuit11.1_bottom_2": "N001",
    "integrated_circuit11.1_left_1": "N002",
    "integrated_circuit11.1_left_2": "N003",
    "integrated_circuit11.1_left_3": "N003",
    "integrated_circuit11.1_right_1": "N004",
    "integrated_circuit11.1_top_1": "N005",
    "integrated_circuit11.1_top_2": "N005",
    "integrated_circuit11.2_bottom_1": "0",
    "integrated_circuit11.2_bottom_2": "N006",
    "integrated_circuit11.2_left_1": "N007",
    "integrated_circuit11.2_left_2": "N008",
    "integrated_circuit11.2_left_3": "N008",
    "integrated_circuit11.2_right_1": "N009",
    "integrated_circuit11.2_top_1": "N005",
    "integrated_circuit11.2_top_2": "N005",
    "led12.1_anode": "N002",
    "led12.1_cathode": "N003",
    "polarized_capacitor20.1_negative": "0",
    "polarized_capacitor20.1_positive": "N003",
    "polarized_capacitor20.2_negative": "0",
    "polarized_capacitor20.2_positive": "N001",
    "polarized_capacitor20.3_negative": "0",
    "polarized_capacitor20.3_positive": "N008",
    "polarized_capacitor20.4_negative": "N010",
    "polarized_capacitor20.4_positive": "N009",
    "resistor22.1_t1": "N002",
    "resistor22.1_t2": "N003",
    "resistor22.2_t1": "N005",
    "resistor22.2_t2": "N002",
    "resistor22.3_t1": "N004",
    "resistor22.3_t2": "N006",
    "resistor22.4_t1": "N007",
    "resistor22.4_t2": "N008",
    "resistor22.5_t1": "N005",
    "resistor22.5_t2": "N007",
    "speaker24.1_t1": "N010",
    "speaker24.1_t2": "0",
    "terminal26.1_t1": "N005"
  },
  "component_terminal_nodes": {
    "gnd9.1": {
      "t1": "0"
    },
    "integrated_circuit11.1": {
      "left_1": "N002",
      "left_2": "N003",
      "left_3": "N003",
      "right_1": "N004",
      "top_1": "N005",
      "top_2": "N005",
      "bottom_1": "0",
      "bottom_2": "N001"
    },
    "integrated_circuit11.2": {
      "left_1": "N007",
      "left_2": "N008",
      "left_3": "N008",
      "right_1": "N009",
      "top_1": "N005",
      "top_2": "N005",
      "bottom_1": "0",
      "bottom_2": "N006"
    },
    "led12.1": {
      "anode": "N002",
      "cathode": "N003"
    },
    "polarized_capacitor20.1": {
      "positive": "N003",
      "negative": "0"
    },
    "polarized_capacitor20.2": {
      "positive": "N001",
      "negative": "0"
    },
    "polarized_capacitor20.3": {
      "positive": "N008",
      "negative": "0"
    },
    "polarized_capacitor20.4": {
      "positive": "N009",
      "negative": "N010"
    },
    "resistor22.1": {
      "t1": "N002",
      "t2": "N003"
    },
    "resistor22.2": {
      "t1": "N005",
      "t2": "N002"
    },
    "resistor22.3": {
      "t1": "N004",
      "t2": "N006"
    },
    "resistor22.4": {
      "t1": "N007",
      "t2": "N008"
    },
    "resistor22.5": {
      "t1": "N005",
      "t2": "N007"
    },
    "speaker24.1": {
      "t1": "N010",
      "t2": "0"
    },
    "terminal26.1": {
      "t1": "N005"
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
    "nodes_count": 11,
    "normal_nodes_count": 10,
    "ground_nodes_count": 1,
    "ground_groups_count": 1,
    "terminal_to_node_count": 40,
    "singleton_nodes_count": 0
  }
}
```

### values_bound

- Step: `04`
- Role: Values and labels bound to graph components.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic04\04_values_bound.json`

```json
{
  "circuit_id": "ic04",
  "source_format": "pipeline2.0_values_bound",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\data\\batchPipeline2.0\\batchICChatAgentEvaluation\\values\\ic04_values.yaml",
  "supplies": {
    "VCC_12": {
      "terminal": "terminal26.1_t1",
      "type": "dc",
      "value": 12,
      "unit": "V",
      "reference": 0,
      "source": "manual_from_image_label",
      "label_text": "+12 V DC",
      "viewer_override": {
        "visual_class": "voltage_source",
        "label": "VCC",
        "display_value": "+12 V"
      },
      "node": "N005"
    }
  },
  "components": {
    "gnd9.1": {
      "class_name": "GND",
      "terminal_nodes": {
        "t1": "0"
      },
      "value_data": null,
      "status": "not_required"
    },
    "integrated_circuit11.1": {
      "class_name": "Integrated_Circuit",
      "terminal_nodes": {
        "left_1": "N002",
        "left_2": "N003",
        "left_3": "N003",
        "right_1": "N004",
        "top_1": "N005",
        "top_2": "N005",
        "bottom_1": "0",
        "bottom_2": "N001"
      },
      "value_data": {
        "model": "TLC555_6",
        "source": "ti_official_slfj002e_pspice_model",
        "label_text": "IC1 NE555; modello ufficiale TI TLC555_6 Rev. E",
        "viewer_override": {
          "label": "IC1",
          "display_value": "NE555",
          "tooltip": "NE555 simulato con il modello ufficiale TI TLC555_6 Rev. E SLFJ002E"
        },
        "spice_override": {
          "emit_as": "subcircuit",
          "pin_order": [
            "THRES",
            "CONT",
            "TRIG",
            "RESET",
            "OUT",
            "DISC",
            "VCC",
            "GND"
          ],
          "node_refs": {
            "THRES": "integrated_circuit11.1_left_2",
            "CONT": "integrated_circuit11.1_bottom_2",
            "TRIG": "integrated_circuit11.1_left_3",
            "RESET": "integrated_circuit11.1_top_1",
            "OUT": "integrated_circuit11.1_right_1",
            "DISC": "integrated_circuit11.1_left_1",
            "VCC": "integrated_circuit11.1_top_2",
            "GND": "integrated_circuit11.1_bottom_1"
          },
          "resolved_node_refs": {
            "THRES": "N003",
            "CONT": "N001",
            "TRIG": "N003",
            "RESET": "N005",
            "OUT": "N004",
            "DISC": "N002",
            "VCC": "N005",
            "GND": "0"
          }
        }
      },
      "status": "unsupported_for_now"
    },
    "integrated_circuit11.2": {
      "class_name": "Integrated_Circuit",
      "terminal_nodes": {
        "left_1": "N007",
        "left_2": "N008",
        "left_3": "N008",
        "right_1": "N009",
        "top_1": "N005",
        "top_2": "N005",
        "bottom_1": "0",
        "bottom_2": "N006"
      },
      "value_data": {
        "model": "TLC555_6",
        "source": "ti_official_slfj002e_pspice_model",
        "label_text": "Secondo NE555 (IC1 ripetuto nello schema); normalizzato a IC2",
        "viewer_override": {
          "label": "IC2",
          "display_value": "NE555",
          "tooltip": "Secondo NE555; modello ufficiale TI TLC555_6 Rev. E SLFJ002E"
        },
        "spice_override": {
          "emit_as": "subcircuit",
          "pin_order": [
            "THRES",
            "CONT",
            "TRIG",
            "RESET",
            "OUT",
            "DISC",
            "VCC",
            "GND"
          ],
          "node_refs": {
            "THRES": "integrated_circuit11.2_left_2",
            "CONT": "integrated_circuit11.2_bottom_2",
            "TRIG": "integrated_circuit11.2_left_3",
            "RESET": "integrated_circuit11.2_top_1",
            "OUT": "integrated_circuit11.2_right_1",
            "DISC": "integrated_circuit11.2_left_1",
            "VCC": "integrated_circuit11.2_top_2",
            "GND": "integrated_circuit11.2_bottom_1"
          },
          "resolved_node_refs": {
            "THRES": "N008",
            "CONT": "N006",
            "TRIG": "N008",
            "RESET": "N005",
            "OUT": "N009",
            "DISC": "N007",
            "VCC": "N005",
            "GND": "0"
          }
        }
      },
      "status": "unsupported_for_now"
    },
    "led12.1": {
      "class_name": "LED",
      "terminal_nodes": {
        "anode": "N002",
        "cathode": "N003"
      },
      "value_data": {
        "model": "D_1N4001_TYP",
        "source": "manual_from_image_label_and_registered_typical_model",
        "label_text": "D1 1N4001",
        "viewer_override": {
          "visual_class": "diode",
          "label": "D1",
          "display_value": "1N4001",
          "tooltip": "Diodo 1N4001; modello tipico semplificato registrato per SPICE"
        }
      },
      "status": "bound"
    },
    "polarized_capacitor20.1": {
      "class_name": "Polarized_Capacitor",
      "terminal_nodes": {
        "positive": "N003",
        "negative": "0"
      },
      "value_data": {
        "value": 10,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C1 10 uF polarizzato",
        "viewer_override": {
          "label": "C1",
          "display_value": "10 uF"
        }
      },
      "status": "bound"
    },
    "polarized_capacitor20.2": {
      "class_name": "Polarized_Capacitor",
      "terminal_nodes": {
        "positive": "N001",
        "negative": "0"
      },
      "value_data": {
        "value": 10,
        "unit": "nf",
        "source": "manual_from_image_label",
        "label_text": "C2 10 nF polarizzato",
        "viewer_override": {
          "label": "C2",
          "display_value": "10 nF"
        }
      },
      "status": "bound"
    },
    "polarized_capacitor20.3": {
      "class_name": "Polarized_Capacitor",
      "terminal_nodes": {
        "positive": "N008",
        "negative": "0"
      },
      "value_data": {
        "value": 100,
        "unit": "nf",
        "source": "manual_from_image_label",
        "label_text": "C3 100 nF polarizzato",
        "viewer_override": {
          "label": "C3",
          "display_value": "100 nF"
        }
      },
      "status": "bound"
    },
    "polarized_capacitor20.4": {
      "class_name": "Polarized_Capacitor",
      "terminal_nodes": {
        "positive": "N009",
        "negative": "N010"
      },
      "value_data": {
        "value": 100,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C4 100 uF polarizzato",
        "viewer_override": {
          "label": "C4",
          "display_value": "100 uF"
        }
      },
      "status": "bound"
    },
    "resistor22.1": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N002",
        "t2": "N003"
      },
      "value_data": {
        "value": 68,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R2 68 kohm",
        "viewer_override": {
          "label": "R2",
          "display_value": "68 kohm"
        }
      },
      "status": "bound"
    },
    "resistor22.2": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N005",
        "t2": "N002"
      },
      "value_data": {
        "value": 68,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R1 68 kohm",
        "viewer_override": {
          "label": "R1",
          "display_value": "68 kohm"
        }
      },
      "status": "bound"
    },
    "resistor22.3": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N004",
        "t2": "N006"
      },
      "value_data": {
        "value": 10,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R5 10 kohm",
        "viewer_override": {
          "label": "R5",
          "display_value": "10 kohm"
        }
      },
      "status": "bound"
    },
    "resistor22.4": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N007",
        "t2": "N008"
      },
      "value_data": {
        "value": 8.2,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R4 8.2 kohm",
        "viewer_override": {
          "label": "R4",
          "display_value": "8.2 kohm"
        }
      },
      "status": "bound"
    },
    "resistor22.5": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N005",
        "t2": "N007"
      },
      "value_data": {
        "value": 8.2,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R3 8.2 kohm",
        "viewer_override": {
          "label": "R3",
          "display_value": "8.2 kohm"
        }
      },
      "status": "bound"
    },
    "speaker24.1": {
      "class_name": "Speaker",
      "terminal_nodes": {
        "t1": "N010",
        "t2": "0"
      },
      "value_data": {
        "nominal_power": 500,
        "power_unit": "mW",
        "source": "manual_from_image_label",
        "label_text": "K1 speaker 64 ohm, 500 mW",
        "spice_override": {
          "emit_as": "resistive_load",
          "equivalent_resistance": 64,
          "resistance_unit": "ohm",
          "node_order": [
            "t1",
            "t2"
          ],
          "semantic_role": "speaker_equivalent"
        },
        "viewer_override": {
          "visual_class": "speaker",
          "label": "K1",
          "display_value": "64 ohm",
          "tooltip": "Speaker 64 ohm, 500 mW; equivalente SPICE resistivo"
        }
      },
      "status": "bound"
    },
    "terminal26.1": {
      "class_name": "Terminal",
      "terminal_nodes": {
        "t1": "N005"
      },
      "value_data": null,
      "status": "not_required"
    }
  },
  "nodes": {
    "gnd9.1_t1": {
      "label": "GND",
      "source": "graph_json_ground",
      "node": "0"
    },
    "integrated_circuit11.1_bottom_2": {
      "label": "SLOW_CONTROL",
      "source": "manual_from_validated_graph_pin5",
      "node": "N001"
    },
    "integrated_circuit11.1_left_1": {
      "label": "SLOW_DISCHARGE",
      "source": "manual_from_validated_graph_pin7",
      "node": "N002"
    },
    "integrated_circuit11.1_left_2": {
      "label": "SLOW_TIMING",
      "source": "manual_from_validated_graph_pins2_6",
      "node": "N003"
    },
    "integrated_circuit11.1_right_1": {
      "label": "MODULATOR_OUTPUT",
      "source": "manual_from_validated_graph_pin3",
      "node": "N004"
    },
    "integrated_circuit11.2_bottom_2": {
      "label": "AUDIO_CONTROL",
      "source": "manual_from_validated_graph_pin5",
      "node": "N006"
    },
    "integrated_circuit11.2_left_1": {
      "label": "AUDIO_DISCHARGE",
      "source": "manual_from_validated_graph_pin7",
      "node": "N007"
    },
    "integrated_circuit11.2_left_2": {
      "label": "AUDIO_TIMING",
      "source": "manual_from_validated_graph_pins2_6",
      "node": "N008"
    },
    "integrated_circuit11.2_right_1": {
      "label": "AUDIO_OUTPUT",
      "source": "manual_from_validated_graph_pin3",
      "node": "N009"
    },
    "speaker24.1_t1": {
      "label": "SPEAKER_INPUT",
      "source": "manual_from_validated_graph",
      "node": "N010"
    },
    "terminal26.1_t1": {
      "label": "VCC_12",
      "source": "manual_from_image_label",
      "label_text": "+12 V DC",
      "node": "N005"
    }
  },
  "spice_topology_overlay": [],
  "simulation": {
    "analyses": [
      "tran"
    ],
    "tran": {
      "step": "50us",
      "stop": "2s"
    }
  },
  "missing": [],
  "stats": {
    "components_total": 15,
    "bound_components": 11,
    "missing_components": 0,
    "not_required_components": 2,
    "unsupported_components": 2,
    "supplies_count": 1,
    "manual_nodes_count": 11
  }
}
```

### component_rules

- Step: `06`
- Role: SPICE conversion rules for each component.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic04\06_component_rules.json`

```json
{
  "circuit_id": "ic04",
  "source_format": "pipeline2.0_component_rules",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\data\\batchPipeline2.0\\batchICChatAgentEvaluation\\values\\ic04_values.yaml",
  "spice_classes_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_spice_classes.yaml",
  "supplies": {
    "VCC_12": {
      "status": "spice_ready",
      "spice_prefix": "V",
      "emit_as": "independent_voltage_source",
      "nodes": [
        "N005",
        "0"
      ],
      "parameters": {
        "terminal": "terminal26.1_t1",
        "type": "dc",
        "value": 12,
        "unit": "V",
        "reference": 0,
        "source": "manual_from_image_label",
        "label_text": "+12 V DC",
        "viewer_override": {
          "visual_class": "voltage_source",
          "label": "VCC",
          "display_value": "+12 V"
        },
        "node": "N005"
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
    "integrated_circuit11.1": {
      "class_name": "Integrated_Circuit",
      "status": "spice_ready",
      "spice_support": "subcircuit",
      "spice_prefix": "X",
      "emit_as": "subcircuit",
      "node_order": [
        "THRES",
        "CONT",
        "TRIG",
        "RESET",
        "OUT",
        "DISC",
        "VCC",
        "GND"
      ],
      "nodes": [
        "N003",
        "N001",
        "N003",
        "N005",
        "N004",
        "N002",
        "N005",
        "0"
      ],
      "parameters": {
        "model": "TLC555_6",
        "source": "ti_official_slfj002e_pspice_model",
        "label_text": "IC1 NE555; modello ufficiale TI TLC555_6 Rev. E",
        "viewer_override": {
          "label": "IC1",
          "display_value": "NE555",
          "tooltip": "NE555 simulato con il modello ufficiale TI TLC555_6 Rev. E SLFJ002E"
        },
        "spice_override": {
          "emit_as": "subcircuit",
          "pin_order": [
            "THRES",
            "CONT",
            "TRIG",
            "RESET",
            "OUT",
            "DISC",
            "VCC",
            "GND"
          ],
          "node_refs": {
            "THRES": "integrated_circuit11.1_left_2",
            "CONT": "integrated_circuit11.1_bottom_2",
            "TRIG": "integrated_circuit11.1_left_3",
            "RESET": "integrated_circuit11.1_top_1",
            "OUT": "integrated_circuit11.1_right_1",
            "DISC": "integrated_circuit11.1_left_1",
            "VCC": "integrated_circuit11.1_top_2",
            "GND": "integrated_circuit11.1_bottom_1"
          },
          "resolved_node_refs": {
            "THRES": "N003",
            "CONT": "N001",
            "TRIG": "N003",
            "RESET": "N005",
            "OUT": "N004",
            "DISC": "N002",
            "VCC": "N005",
            "GND": "0"
          }
        }
      },
      "reason": "Explicit YAML override emitted as a SPICE subcircuit."
    },
    "integrated_circuit11.2": {
      "class_name": "Integrated_Circuit",
      "status": "spice_ready",
      "spice_support": "subcircuit",
      "spice_prefix": "X",
      "emit_as": "subcircuit",
      "node_order": [
        "THRES",
        "CONT",
        "TRIG",
        "RESET",
        "OUT",
        "DISC",
        "VCC",
        "GND"
      ],
      "nodes": [
        "N008",
        "N006",
        "N008",
        "N005",
        "N009",
        "N007",
        "N005",
        "0"
      ],
      "parameters": {
        "model": "TLC555_6",
        "source": "ti_official_slfj002e_pspice_model",
        "label_text": "Secondo NE555 (IC1 ripetuto nello schema); normalizzato a IC2",
        "viewer_override": {
          "label": "IC2",
          "display_value": "NE555",
          "tooltip": "Secondo NE555; modello ufficiale TI TLC555_6 Rev. E SLFJ002E"
        },
        "spice_override": {
          "emit_as": "subcircuit",
          "pin_order": [
            "THRES",
            "CONT",
            "TRIG",
            "RESET",
            "OUT",
            "DISC",
            "VCC",
            "GND"
          ],
          "node_refs": {
            "THRES": "integrated_circuit11.2_left_2",
            "CONT": "integrated_circuit11.2_bottom_2",
            "TRIG": "integrated_circuit11.2_left_3",
            "RESET": "integrated_circuit11.2_top_1",
            "OUT": "integrated_circuit11.2_right_1",
            "DISC": "integrated_circuit11.2_left_1",
            "VCC": "integrated_circuit11.2_top_2",
            "GND": "integrated_circuit11.2_bottom_1"
          },
          "resolved_node_refs": {
            "THRES": "N008",
            "CONT": "N006",
            "TRIG": "N008",
            "RESET": "N005",
            "OUT": "N009",
            "DISC": "N007",
            "VCC": "N005",
            "GND": "0"
          }
        }
      },
      "reason": "Explicit YAML override emitted as a SPICE subcircuit."
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
        "model": "D_1N4001_TYP",
        "source": "manual_from_image_label_and_registered_typical_model",
        "label_text": "D1 1N4001",
        "viewer_override": {
          "visual_class": "diode",
          "label": "D1",
          "display_value": "1N4001",
          "tooltip": "Diodo 1N4001; modello tipico semplificato registrato per SPICE"
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
        "N003",
        "0"
      ],
      "parameters": {
        "value": 10,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C1 10 uF polarizzato",
        "viewer_override": {
          "label": "C1",
          "display_value": "10 uF"
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
        "N001",
        "0"
      ],
      "parameters": {
        "value": 10,
        "unit": "nf",
        "source": "manual_from_image_label",
        "label_text": "C2 10 nF polarizzato",
        "viewer_override": {
          "label": "C2",
          "display_value": "10 nF"
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
        "N008",
        "0"
      ],
      "parameters": {
        "value": 100,
        "unit": "nf",
        "source": "manual_from_image_label",
        "label_text": "C3 100 nF polarizzato",
        "viewer_override": {
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
        "N009",
        "N010"
      ],
      "parameters": {
        "value": 100,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C4 100 uF polarizzato",
        "viewer_override": {
          "label": "C4",
          "display_value": "100 uF"
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
        "N002",
        "N003"
      ],
      "parameters": {
        "value": 68,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R2 68 kohm",
        "viewer_override": {
          "label": "R2",
          "display_value": "68 kohm"
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
        "N005",
        "N002"
      ],
      "parameters": {
        "value": 68,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R1 68 kohm",
        "viewer_override": {
          "label": "R1",
          "display_value": "68 kohm"
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
        "N004",
        "N006"
      ],
      "parameters": {
        "value": 10,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R5 10 kohm",
        "viewer_override": {
          "label": "R5",
          "display_value": "10 kohm"
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
        "N007",
        "N008"
      ],
      "parameters": {
        "value": 8.2,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R4 8.2 kohm",
        "viewer_override": {
          "label": "R4",
          "display_value": "8.2 kohm"
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
        "N005",
        "N007"
      ],
      "parameters": {
        "value": 8.2,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R3 8.2 kohm",
        "viewer_override": {
          "label": "R3",
          "display_value": "8.2 kohm"
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
        "N010",
        "0"
      ],
      "parameters": {
        "nominal_power": 500,
        "power_unit": "mW",
        "source": "manual_from_image_label",
        "label_text": "K1 speaker 64 ohm, 500 mW",
        "spice_override": {
          "emit_as": "resistive_load",
          "equivalent_resistance": 64,
          "resistance_unit": "ohm",
          "node_order": [
            "t1",
            "t2"
          ],
          "semantic_role": "speaker_equivalent"
        },
        "viewer_override": {
          "visual_class": "speaker",
          "label": "K1",
          "display_value": "64 ohm",
          "tooltip": "Speaker 64 ohm, 500 mW; equivalente SPICE resistivo"
        },
        "equivalent_resistance": 64,
        "resistance_unit": "ohm"
      },
      "reason": "Explicit YAML override emit
```

> Artifact truncated in this preview. The original file remains available through the manifest path.

### netlist

- Step: `07`
- Role: Generated SPICE netlist.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic04\07_netlist.cir`

```spice
* pipeline2.0 netlist
* circuit: ic04

VVCC_12 N005 0 DC 12
Xintegrated_circuit11_1 N003 N001 N003 N005 N004 N002 N005 0 TLC555_6
Xintegrated_circuit11_2 N008 N006 N008 N005 N009 N007 N005 0 TLC555_6
Dled12_1 N002 N003 D_1N4001_TYP
Cpolarized_capacitor20_1 N003 0 10u
Cpolarized_capacitor20_2 N001 0 10n
Cpolarized_capacitor20_3 N008 0 100n
Cpolarized_capacitor20_4 N009 N010 100u
Rresistor22_1 N002 N003 68k
Rresistor22_2 N005 N002 68k
Rresistor22_3 N004 N006 10k
Rresistor22_4 N007 N008 8.2k
Rresistor22_5 N005 N007 8.2k
Rspeaker24_1 N010 0 64

.model D_1N4001_TYP D(IS=14n N=1.9 RS=0.08 BV=50 IBV=5u TT=2u CJO=25p)
.include "07_external_models.lib"

.save all
.tran 50us 2s

.control
set wr_singlescale
set wr_vecnames
save all @dled12_1[id]
run
wrdata 08_tran.csv time v(N001) v(N002) v(N003) v(N004) v(N005) v(N006) v(N007) v(N008) v(N009) v(N010) @dled12_1[id]
.endc
.end

```

### spice_emit_report

- Step: `07`
- Role: Report of emitted, skipped and warning components.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic04\07_spice_emit_report.json`

```json
{
  "circuit_id": "ic04",
  "source_format": "pipeline2.0_spice_emit_report",
  "emitted_elements": 14,
  "skipped_elements": 2,
  "skipped_components": [
    "gnd9.1",
    "terminal26.1"
  ],
  "informational_skips": [
    "gnd9.1: structural component not emitted",
    "terminal26.1: structural component not emitted"
  ],
  "measurement_points": [],
  "analyses": [
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
      "N010"
    ],
    "device_currents": [
      "@dled12_1[id]"
    ]
  },
  "models": [
    "D_1N4001_TYP",
    "TLC555_6"
  ],
  "warnings": [],
  "external_model_sources": [
    {
      "model": "TLC555_6",
      "kind": "file",
      "file": "spice_models/ti/tlc555/slfj002e/TLC555_6.LIB",
      "sha256": "7C091782CC4931DDA4FEBF25605083F47161C5E1592C076689B04B70DD749034",
      "encoding": "utf-8-sig"
    }
  ],
  "ngspice_defines": {
    "ngbehavior": "ps"
  }
}
```

### spice_run

- Step: `08`
- Role: Structured ngspice execution report.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic04\08_spice_run.json`

```json
{
  "source_format": "pipeline2.0_spice_run",
  "status": "success",
  "netlist_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\pipeline2.0\\ic04\\07_netlist.cir",
  "command": [
    "C:\\Users\\m.profilo\\Spice64\\bin\\ngspice_con.EXE",
    "-D",
    "ngbehavior=ps",
    "-b",
    "07_netlist.cir"
  ],
  "exit_code": 0,
  "stdout_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\pipeline2.0\\ic04\\08_ngspice_stdout.txt",
  "stderr_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\pipeline2.0\\ic04\\08_ngspice_stderr.txt",
  "tran_raw_csv_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\pipeline2.0\\ic04\\08_tran_raw.csv",
  "tran_csv_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\pipeline2.0\\ic04\\08_tran.csv",
  "tran_plot_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\pipeline2.0\\ic04\\08_tran_plot.png",
  "tran_plot_png_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\pipeline2.0\\ic04\\08_tran_plot.png",
  "tran_plot_svg_path": null,
  "message": "ngspice completed successfully."
}
```

### ngspice_stdout

- Step: `08`
- Role: Raw ngspice stdout log.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic04\08_ngspice_stdout.txt`

```text
Note: gnd in a subcircuit is not set to 0 automatically

Note: Compatibility modes selected: ps


Circuit: * pipeline2.0 netlist

Reducing trtol to 1 for xspice 'A' devices
Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

Initial Transient Solution
--------------------------

Node                                   Voltage
----                                   -------
n005                                        12
xintegrated_circuit11_1.resi                12
xintegrated_circuit11_1.trgi         0.0417684
n003                                 0.0417537
xintegrated_circuit11_1.thri         0.0417537
xintegrated_circuit11_1.conti          4.60841
n001                                   4.43178
xintegrated_circuit11_1.qff                  1
xintegrated_circuit11_1.gout       2.84871e-07
xintegrated_circuit11_1.trgo           2.95168
xintegrated_circuit11_1.xmn3.10            0.14
xintegrated_circuit11_1.23            0.163845
xintegrated_circuit11_1.thrs           4.01249
xintegrated_circuit11_1.xmn5.10            0.14
xintegrated_circuit11_1.25            0.150935
xintegrated_circuit11_1.reso       0.000240912
xintegrated_circuit11_1.15           0.0395409
xintegrated_circuit11_1.xmp9.10           11.15
xintegrated_circuit11_1.xmp6.10           11.15
xintegrated_circuit11_1.trgs           2.95219
xintegrated_circuit11_1.xmp5.10           11.15
xintegrated_circuit11_1.thro            11.995
xintegrated_circuit11_1.xmp1.10           11.86
xintegrated_circuit11_1.29             11.8135
xintegrated_circuit11_1.xib.gb_int1      3.9529e-08
xintegrated_circuit11_1.xrsff.xu1.out_vmeas_0               0
xintegrated_circuit11_1.xrsff.xu1.eout_int1               0
xintegrated_circuit11_1.30                   0
xintegrated_circuit11_1.xrsff.xu2.out_vmeas_2               1
xintegrated_circuit11_1.xrsff.xu2.eout_int1               1
xintegrated_circuit11_1.xrsff.xu2.1       0.0896861
xintegrated_circuit11_1.xrsff.xu2.e1_int1       0.0896861
n002                                  0.501331
n004                                   11.9932
xintegrated_circuit11_1.trgc            2.3042
xintegrated_circuit11_1.32             1.15211
xintegrated_circuit11_1.33             3.45631
xintegrated_circuit11_1.34              8.3042
xintegrated_circuit11_2.resi                12
xintegrated_circuit11_2.trgi           5.38425
n008                                   5.38426
xintegrated_circuit11_2.thri           5.38425
xintegrated_circuit11_2.conti          10.6344
n006                                   10.7261
xintegrated_circuit11_2.qff                  1
xintegrated_circuit11_2.gout       3.12258e-07
xintegrated_circuit11_2.trgo        0.00199402
xintegrated_circuit11_2.xmn3.10            0.14
xintegrated_circuit11_2.23            0.188721
xintegrated_circuit11_2.thrs           10.0383
xintegrated_circuit11_2.xmn5.10            0.14
xintegrated_circuit11_2.25            0.150924
xintegrated_circuit11_2.reso       0.000240912
xintegrated_circuit11_2.15           0.0395409
xintegrated_circuit11_2.xmp9.10           11.15
xintegrated_circuit11_2.xmp6.10           11.15
xintegrated_circuit11_2.trgs           5.98558
xintegrated_circuit11_2.xmp5.10           11.15
xintegrated_circuit11_2.thro            11.995
xintegrated_circuit11_2.xmp1.10           11.86
xintegrated_circuit11_2.29             11.8137
xintegrated_circuit11_2.xib.gb_int1      3.9529e-08
xintegrated_circuit11_2.xrsff.xu1.out_vmeas_0               0
xintegrated_circuit11_2.xrsff.xu1.eout_int1               0
xintegrated_circuit11_2.30                   0
xintegrated_circuit11_2.xrsff.xu2.out_vmeas_2               1
xintegrated_circuit11_2.xrsff.xu2.eout_int1               1
xintegrated_circuit11_2.xrsff.xu2.1       0.0896861
xintegrated_circuit11_2.xrsff.xu2.e1_int1       0.0896861
n007                                   8.69211
n009                                   9.18721
xintegrated_circuit11_2.trgc           5.31718
xintegrated_circuit11_2.32             2.65859
xintegrated_circuit11_2.33             7.97577
xintegrated_circuit11_2.34             11.3172
n010                                   2.92065
b.xintegrated_circuit11_2.xrsff.xu2.be1#branch               0
b.xintegrated_circuit11_2.xrsff.xu2.beout#branch               0
v.xintegrated_circuit11_2.xrsff.xu2.v_eout#branch    -1.99999e-12
b.xintegrated_circuit11_2.xrsff.xu1.beout#branch               0
v.xintegrated_circuit11_2.xrsff.xu1.v_eout#branch               0
b.xintegrated_circuit11_2.xib.bgb#branch               0
b.xintegrated_circuit11_1.xrsff.xu2.be1#branch               0
b.xintegrated_circuit11_1.xrsff.xu2.beout#branch               0
v.xintegrated_circuit11_1.xrsff.xu2.v_eout#branch    -1.99999e-12
b.xintegrated_circuit11_1.xrsff.xu1.beout#branch               0
v.xintegrated_circuit11_1.xrsff.xu1.v_eout#branch               0
b.xintegrated_circuit11_1.xib.bgb#branch               0
v.xintegrated_circuit11_2.xmp1.v1#branch     6.08863e-07
v.xintegrated_circuit11_2.xmn5.v1#branch     7.58977e-08
v.xintegrated_circuit11_2.xmn3.v1#branch     8.22001e-07
v.xintegrated_circuit11_1.xmp1.v1#branch     6.11347e-07
v.xintegrated_circuit11_1.xmn5.v1#branch     7.59709e-08
v.xintegrated_circuit11_1.xmn3.v1#branch      8.0431e-07
e.xintegrated_circuit11_2.xrsff.xu2.e1#branch               0
e.xintegrated_circuit11_2.xrsff.xu2.eout#branch    -1.99999e-12
e.xintegrated_circuit11_2.xrsff.xu1.eout#branch               0
e.xintegrated_circuit11_1.xrsff.xu2.e1#branch               0
e.xintegrated_circuit11_1.xrsff.xu2.eout#branch    -1.99999e-12
e.xintegrated_circuit11_1.xrsff.xu1.eout#branch               0
v.xintegrated_circuit11_2.xmp5.v1#branch     6.16441e-12
v.xintegrated_circuit11_2.xmp6.v1#branch     1.19991e-11
v.xintegrated_circuit11_2.xmp9.v1#branch     1.21498e-11
v.xintegrated_circuit11_1.xmp5.v1#branch     9.19781e-12
v.xintegrated_circuit11_1.xmp6.v1#branch     1.19991e-11
v.xintegrated_circuit11_1.xmp9.v1#branch     1.21498e-11
vvcc_12#branch                      -0.0466151

 Reference value :  3.11198e-02
 Reference value :  1.11825e-01
 Reference value :  1.65084e-01
 Reference value :  1.81305e-01
 Reference value :  2.43648e-01
 Reference value :  3.18811e-01
 Reference value :  4.09852e-01
 Reference value :  5.22398e-01
 Reference value :  5.84563e-01
 Reference value :  6.31810e-01
 Reference value :  6.87877e-01
 Reference value :  7.43459e-01
 Reference value :  8.01348e-01
 Reference value :  8.21064e-01
 Reference value :  8.38116e-01
 Reference value :  8.53685e-01
 Reference value :  8.69305e-01
 Reference value :  8.83706e-01
 Reference value :  8.97230e-01
 Reference value :  9.12749e-01
 Reference value :  9.25661e-01
 Reference value :  9.41768e-01
 Reference value :  9.57794e-01
 Reference value :  9.79813e-01
 Reference value :  9.96040e-01
 Reference value :  1.01072e+00
 Reference value :  1.02522e+00
 Reference value :  1.03982e+00
 Reference value :  1.04484e+00
 Reference value :  1.05420e+00
 Reference value :  1.07020e+00
 Reference value :  1.08638e+00
 Reference value :  1.09992e+00
 Reference value :  1.11671e+00
 Reference value :  1.13309e+00
 Reference value :  1.15403e+00
 Reference value :  1.16941e+00
 Reference value :  1.18603e+00
 Reference value :  1.20244e+00
 Reference value :  1.21859e+00
 Reference value :  1.23323e+00
 Reference value :  1.24875e+00
 Reference value :  1.26415e+00
 Reference value :  1.34356e+00
 Reference value :  1.45140e+00
 Reference value :  1.56253e+00
 Reference value :  1.65946e+00
 Reference value :  1.75252e+00
 Reference value :  1.78989e+00
 Reference value :  1.80564e+00
 Reference value :  1.82563e+00
 Reference value :  1.84076e+00
 Reference value :  1.85724e+00
 Reference value :  1.87188e+00
 Reference value :  1.88889e+00
 Reference value :  1.90406e+00
 Reference value :  1.92420e+00
 Reference value :  1.93931e+00
 Reference value :  1.95692e+00
 Reference value :  1.97268e+00
 Reference value :  1.98439e+00
 Reference value :  1.99454e+00

No. of Data Rows : 131120
Note: Simulation executed from .control section 

```

### ngspice_stderr

- Step: `08`
- Role: Raw ngspice stderr log.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic04\08_ngspice_stderr.txt`

```text
Warning: Model issue on line 118 :
  .model xintegrated_circuit11_1.xmn17:tlc55x_nmosd_hv nmos level=3 l=10u  ...
unrecognized parameter (lambda) - ignored

Warning: Model issue on line 118 :
  .model xintegrated_circuit11_1.xmn16:tlc55x_nmosd_hv nmos level=3 l=10u  ...
unrecognized parameter (lambda) - ignored

Warning: Model issue on line 204 :
  .model xintegrated_circuit11_1.xmp16:tlc55x_pmosd_hv pmos level=3 l=10u  ...
unrecognized parameter (lambda) - ignored

Warning: Model issue on line 118 :
  .model xintegrated_circuit11_2.xmn17:tlc55x_nmosd_hv nmos level=3 l=10u  ...
unrecognized parameter (lambda) - ignored

Warning: Model issue on line 118 :
  .model xintegrated_circuit11_2.xmn16:tlc55x_nmosd_hv nmos level=3 l=10u  ...
unrecognized parameter (lambda) - ignored

Warning: Model issue on line 204 :
  .model xintegrated_circuit11_2.xmp16:tlc55x_pmosd_hv pmos level=3 l=10u  ...
unrecognized parameter (lambda) - ignored

Note: Starting dynamic gmin stepping
Warning: Dynamic gmin stepping failed
Note: Starting true gmin stepping
Warning: True gmin stepping failed
Note: Starting source stepping
Warning: source stepping failed
Note: Transient op started
Note: Transient op finished successfully

```

### tran_csv

- Step: `08`
- Role: Clean transient CSV, when .tran data is available.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic04\08_tran.csv`

```csv
time,v(N001),v(N002),v(N003),v(N004),v(N005),v(N006),v(N007),v(N008),v(N009),v(N010),@dled12_1[id]
0.0,4.43177765,0.501330851,0.0417536562,11.9931729,12.0,10.726096,8.69210518,5.38425747,9.18720658,2.92064696,0.000162301397
5e-07,4.44392704,0.501407537,0.041762112,11.9931729,12.0,10.7260958,8.69311334,5.38627377,9.1873274,2.92053961,0.000162336587
1e-06,4.45602778,0.501470498,0.0417705678,11.9931729,12.0,10.7260957,8.69412118,5.38828945,9.18744821,2.92043227,0.000162335512
2e-06,4.48013248,0.501574474,0.0417874792,11.9931729,12.0,10.7260957,8.69613627,5.39231959,9.18768982,2.92021758,0.000162333723
4e-06,4.52776665,0.501694992,0.0418213019,11.9931729,12.0,10.7260957,8.70016276,5.40037251,9.188173,2.91978825,0.000162330409
8e-06,4.62078779,0.501805344,0.0418889463,11.9931729,12.0,10.7260957,8.70820102,5.41644891,9.1891391,2.91892975,0.000162327647
1.6e-05,4.79829152,0.5019398,0.0420242331,11.9931729,12.0,10.7260957,8.72421889,5.44848439,9.19107022,2.91721329,0.000162325559
3.13493887e-05,5.10977316,0.502198283,0.0422837975,11.9931729,12.0,10.7260957,8.75473421,5.50951454,9.1947717,2.91392224,0.000162321774
6.20481661e-05,5.63603797,0.502715053,0.0428029008,11.9931729,12.0,10.7260957,8.81491605,5.62987729,9.20215983,2.90734896,0.000162314208
7.43129304e-05,5.81411016,0.502921548,0.0430102835,11.9931729,12.0,10.7260957,8.83864595,5.67733702,9.20510807,2.90472816,0.000162311186
8.13143316e-05,5.90888347,0.503039397,0.0431286668,11.9931729,12.0,10.7260957,8.85211304,5.70427082,9.20678694,2.90323017,0.000162309459
8.5729923e-05,5.96642472,0.50311373,0.043203327,11.9931729,12.0,10.7260957,8.86057685,5.7211982,9.20784577,2.90228628,0.000162308372
9.19658954e-05,6.04476449,0.503218703,0.0433087658,11.9931729,12.0,10.7260957,8.87249116,5.74502663,9.20934105,2.90095431,0.000162306834
9.98987656e-05,6.13963986,0.503352239,0.0434428942,11.9931729,12.0,10.7260957,8.88758222,5.7752085,9.21124208,2.89926063,0.00016230488
0.000115764506,6.31462558,0.503619306,0.043711145,11.9931729,12.0,10.7260957,8.91754636,5.83513635,9.21504043,2.89587585,0.000162300969
0.000147495987,6.61354804,0.504153417,0.0442476237,11.9931729,12.0,10.7260957,8.97661329,5.95326934,9.22262201,2.8891163,0.00016229315
0.000197495987,6.97552701,0.504994967,0.0450929053,11.9931729,12.0,10.7260957,9.06740185,6.13484511,9.23452651,2.87849108,0.000162280829
0.000247495987,7.23841707,0.505836447,0.0459381167,11.9931729,12.0,10.7260957,9.15546397,6.310968,9.24637688,2.86789463,0.00016226851
0.000297495987,7.43181762,0.506677859,0.0467832604,11.9931729,12.0,10.7260957,9.24088166,6.48180207,9.25817576,2.85732936,0.00016225619
0.000347495987,7.57497281,0.507519205,0.0476283379,11.9931729,12.0,10.7260957,9.32373436,6.64750622,9.26992339,2.84679525,0.000162243873
0.000397495987,7.68142631,0.508360486,0.0484733505,11.9931729,12.0,10.7260957,9.40409911,6.80823449,9.28161999,2.83629229,0.000162231556
0.000447495987,7.76086148,0.509201703,0.0493182989,11.9931729,12.0,10.7260957,9.4820506,6.96413631,9.29326579,2.82582046,0.00016221924
0.000497495987,7.82028941,0.510042856,0.0501631838,11.9931729,12.0,10.7260957,9.55766131,7.11535661,9.30486102,2.81537976,0.000162206925
0.000547495987,7.86483585,0.510883946,0.0510080055,11.9931729,12.0,10.7260957,9.63100153,7.26203596,9.31640591,2.80497015,0.000162194611
0.000597495987,7.89827616,0.511724973,0.0518527645,11.9931729,12.0,10.7260957,9.70213944,7.40431073,9.32790067,2.79459163,0.000162182297
0.000647495987,7.92340689,0.512565938,0.0526974609,11.9931729,12.0,10.7260957,9.77114117,7.54231317,9.33934554,2.78424417,0.000162169986
0.000697495987,7.94230852,0.513406841,0.053542095,11.9931729,12.0,10.7260957,9.83807087,7.67617159,9.35074074,2.77392775,0.000162157674
0.000747495987,7.95653391,0.514247681,0.0543866668,11.9931729,12.0,10.7260957,9.90299076,7.80601041,9.36208648,2.76364237,0.000162145364
0.000797495987,7.96724498,0.515088459,0.0552311765,11.9931729,12.0,10.7260957,9.96596118,7.93195035,9.373383,2.75338798,0.000162133054
0.000847495987,7.97531278,0.515929175,0.0560756242,11.9931729,12.0,10.7260957,10.0270407,8.05410848,9.3846305,2.74316458,0.000162120746
0.000897495987,7.98139123,0.516769829,0.0569200098,11.9931729,12.0,10.7260957,10.0862861,8.17259836,9.39582922,2.73297213,0.000162108438
0.000947495987,7.98597179,0.517610421,0.0577643336,11.9931729,12.0,10.7260957,10.1437524,8.28753015,9.40697936,2.72281062,0.000162096132
0.000997495987,7.98942409,0.518450952,0.0586085954,11.9931729,12.0,10.7260957,10.199493,8.39901068,9.41808114,2.71268002,0.000162083825
0.00104749599,7.99202635,0.51929142,0.0594527954,11.9931729,12.0,10.7260957,10.2535599,8.50714361,9.42913478,2.7025803,0.000162071521
0.00109749599,7.99398803,0.520131826,0.0602969335,11.9931729,12.0,10.7260957,10.3060032,8.61202944,9.4401405,2.69251144,0.000162059216
0.00114749599,7.99546691,0.520972171,0.0611410097,11.9931729,12.0,10.7260957,10.3568716,8.7137657,9.4510985,2.68247341,0.000162046914
0.00119749599,7.99658187,0.521812454,0.0619850242,11.9931729,12.0,10.7260957,10.4062126,8.81244694,9.46200901,2.67246618,0.000162034611
0.00124749599,7.9974225,0.522652675,0.0628289768,11.9931729,12.0,10.7260957,10.4540719,8.90816492,9.47287222,2.66248972,0.00016202231
0.00129749599,7.99805631,0.523492834,0.0636728677,11.9931729,12.0,10.7260957,10.5004941,9.00100862,9.48368836,2.65254401,0.000162010009
0.00134749599,7.9985342,0.524332931,0.0645166968,11.9931729,12.0,10.7260957,10.5455223,9.09106434,9.49445763,2.64262901,0.000161997711
0.00139749599,7.99889452,0.525172967,0.065360464,11.9931729,12.0,10.7260957,10.5891983,9.17841581,9.50518024,2.6327447,0.000161985411
0.00144749599,7.99916621,0.526012941,0.0662041696,11.9931729,12.0,10.7260957,10.6315628,9.26314422,9.5158564,2.62289103,0.000161973114
0.00149749599,7.99937107,0.526852853,0.0670478133,11.9931729,12.0,10.7260957,10.6726552,9.34532836,9.52648632,2.61306798,0.000161960817
0.00154749599,7.99952554,0.527692703,0.0678913953,11.9931729,12.0,10.7260957,10.7125136,9.42504461,9.53707019,2.60327551,0.000161948522
0.00159749599,7.99964201,0.528532492,0.0687349155,11.9931729,12.0,10.7260957,10.7511751,9.50236709,9.54760823,2.5935136,0.000161936226
0.00164749599,7.99972983,0.529372219,0.069578374,11.9931729,12.0,10.7260957,10.7886756,9.57736768,9.55810064,2.58378219,0.000161923933
0.00169749599,7.99979605,0.530211884,0.0704217707,11.9931729,12.0,10.7260957,10.8250501,9.6501161,9.56854763,2.57408127,0.000161911639
0.00174749599,7.99984599,0.531051487,0.0712651057,11.9931729,12.0,10.7260957,10.8603323,9.72067998,9.57894938,2.5644108,0.000161899348
0.00179749599,7.99988364,0.531891028,0.072108379,11.9931729,12.0,10.7260957,10.894555,9.78912491,9.58930612,2.55477073,0.000161887055
0.00184749599,7.99991203,0.532730508,0.0729515905,11.9931729,12.0,10.7260957,10.92775,9.85551454,9.59961802,2.54516103,0.000161874766
0.00189749599,7.99993343,0.533569926,0.0737947404,11.9931729,12.0,10.7260957,10.9599483,9.91991057,9.60988531,2.53558166,0.000161862476
0.00194749599,7.99994958,0.534409283,0.0746378284,11.9931729,12.0,10.7260957,10.9911796,9.98237288,9.62010816,2.52603258,0.000161850188
0.00199749599,7.99996175,0.535248577,0.0754808548,11.9931729,12.0,10.7260957,11.0214732,10.0429595,9.63028678,2.51651376,0.000161837899
0.00204749599,7.99997093,0.53608781,0.0763238195,11.9931729,12.0,10.7260957,11.050857,10.1017269,9.64042137,2.50702515,0.000161825613
0.00209749599,7.99997785,0.536926981,0.0771667224,11.9931729,12.0,10.7260957,11.0793586,10.1587296,9.65051212,2.49756671,0.000161813327
0.00214749599,7.99998306,0.537766091,0.0780095637,11.9931729,12.0,10.7260957,11.1070044,10.2140208,9.66055923,2.4881384,0.000161801043
0.00219749599,7.999987,0.538605138,0.0788523433,11.9931729,12.0,10.7260957,11.13382,10.2676517,9.67056288,2.47874019,0.000161788758
0.00224749599,7.99998997,0.539444125,0.0796950611,11.9931729,12.0,10.7260957,11.1598305,10.3196723,9.68052328,2.46937202,0.000161776475
0.00229749599,7.9999922,0.540283049,0.0805377173,11.9931729,12.0,10.7260957,11.1850599,10.3701307,9.69044061,2.46003386,0.000161764193
0.0023442183,7.99999379,0.541066923,0.0813250785,11.9931729,12.0,10.7260957,11.20795,10.4159106,9.69966872,2.45133459,0.000161752717
0.0023942183,7.99999509,0.541905728,0.0821676153,11.9931729,12.0,10.7260957,11.2317344,10.4634792,9.70950362,2.44205469,0.000161740436
0.0024442183,7.99999607,0.542744471,0.0830100905,11.9931729,12.0,10.7260957,11.2548046,10.5096192,9.71929567,2.43280432,0.000161728157
0.0024942183,7.9999968,0.543583153,0.083852504,11.9931729,12.0,10.7260957,11.277182,10.5543737,9.7290454,2.42358378,0.000161715877
0.0025442183,7.99999736,0.544421773,0.0846948559,11.9931729,12.0,10.7260957,11.2988874,10.5977842,9.73875299,2.41439303,0.000161703601
0.00255808591,7.99999749,0.544654355,0.0849284731,11.9931729,12.0,10.7260953,0.0175186625,10.5149504,1.26823816,-6.0521806,0.000161700194
0.00256311682,7.99999753,0.54473873,0.0850132239,11.9931729,12.0,10.7260968,0.0171368601,10.4507437,1.26682545,-6.04883712,0.00016169896
0.00256559781,7.99999755,0.54478034,0.0850550185,11.9931729,12.0,10.7260942,0.0174444359,10.4192249,1.26694355,-6.04637464,0.00016169835
0.00256871262,7.99999758,0.544832579,0.0851074902,11.9931729,12.0,10.726098,0.017077234,10.3797885,1.26585562,-6.04452032,0.000161697586
0.00257160665,7.9999976,0.544881115,0.0851562424,11.9931729,12.0,10.7260933,0.0173854271,10.3432814,1.26590881,-6.04173447,0.000161696874
0.00257435489,7.99999762,0.544927206,0.0852025384,11.9931729,12.0,10.7260988,0.0170282579,10.3087324,1.26489295,-6.04015627,0.0001616962
0.00257649878,7.99999764,0.544963161,0.0852386536,11.9931729,12.0,10.7260923,0.0173375178,10.281861,1.26506677,-6.03795948,0.000161695673
0.00257785172,7.99999765,0.544985851,0.0852614447,11.9931729,12.0,10.7261,0.0169952548,10.2649395,1.26429293,-6.03745696,0.000161695342
0.00257885965,7.99999766,0.545002755,0.0852784238,11.9931729,12.0,10.7260904,0.01731365,10.2523512,1.26465945,-6.03613971,0.000161695094
0.00257938607,7.99999766,0.545011584,0.0852872917,11.9931729,12.0,10.7261026,0.0169823177,10.2457827,1.26403181,-6.03627086,0.000161694965
0.002579598,7.99999766,0.545015138,0.0852908618,11.9931728,12.0,10.7260862,0.0173023835,10.2431395,1.26452685,-6.03557594,0.000161694912
0.00257965075,7.99999766,0.545016023,0.0852917503,11.9931729,12.0,10.7261075,0.0169940965,10.2424818,1.26400605,-6.03604699,0.0001616949
0.00257965381,7.99999766,0.545016074,0.0852918019,11.9931729,12.0,10.7260976,0.0171733143,10.2424436,1.26433782,-6.03571234,0.000161694898
0.00257965569,7.99999766,0.545016106,0.0852918336,11.9931729,12.0,10.726097,0.0171476655,10.2424201,1.26422707,-6.03582132,0.000161694899
0.00257965637,7.99999766,0.545016117,0.0852918451,11.9931729,12.0,10.7260968,0.0171398708,10.2424117,1.26426642,-6.03578132,0.000161694898
0.00257965741,7.99999766,0.545016134,0.0852918625,11.9931729,12.0,10.7260966,0.0171433398,10.2423988,1.26424392,-6.03580285,0.000161694898
0.00257965862,7.99999766,0.545016155,0.0852918829,11.9931729,12.0,10.7260965,0.0171416025,10.2423836,1.26425903,-6.03578659,0.000161694897
0.00257966104,7.99999766,0.545016195,0.0852919237,11.9931729,12.0,10.7260962,0.0171426181,10.2423534,1.26424697,-6.03579637,0.000161694898
0.00257966589,7.99999766,0.545016277,0.0852920053,11.9931729,12.0,10.7260959,0.017141797,10.242293,1.26425636,-6.03578241,0.000161694896
0.00257967558,7.99999767,0.545016439,0.0852921686,11.9931729,12.0,10.7260958,0.0171423691,10.2421722,1.26424511,-6.03578452,0.000161694894
0.00257968644,7.99999767,0.545016621,0.0852923516,11.9931729,12.0,10.7260957,0.0171416616,10.2420367,1.26425245,-6.03576694,0.00016169489
0.00257969798,7.99999767,0.545016815,0.085292546,11.9931729,12.0,10.7260957,0.0171421,10.2418928,1.26424159,-6.03576691,0.000161694888
0.0025797095,7.99999767,0.545017008,0.0852927401,11.9931729,12.0,10.7260957,0.0171414889,10.2417492,1.26424817,-6.03574946,0.000161694885
0.0025797235,7.99999767,0.545017243,0.0852929758,11.9931729,12.0,10.7260957,0.0171418122,10.2415747,1.26423749,-6.03574695,0.0
```

> Artifact truncated in this preview. The original file remains available through the manifest path.
