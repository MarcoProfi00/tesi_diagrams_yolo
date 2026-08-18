# Agent input preview

This file is a local preview of the evidence that will be provided to the read-only diagnostic agent.
The agent remains read-only: it can inspect base outputs and existing scenario artifacts, but it does not modify files.

## User problem

Lo scenario combinato soddisfa entrambi i criteri: N001 ha un segnale sinusoidale di circa 10 Vpp e il LED conduce circa 6,32 mA con PWR a 5 V. Fornisci la conclusione finale: causa isolata, correzione combinata verificata e distinzione tra alimentazione DC del LED e segnale AC di VAC. Non proporre altri scenari.

## Circuit

- Batch: `batchChatAgentEvaluation`
- Circuit: `a07`
- Agent mode: `graph_grounded_readonly`

## Technical summary

```json
{
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_message": "ngspice completed successfully.",
  "emitted_elements": 3,
  "skipped_elements": 5,
  "emit_warnings_count": 1,
  "skipped_components_count": 5,
  "node_count": 5,
  "ground_groups_count": 4,
  "singleton_nodes_count": 0,
  "bound_components": 3,
  "missing_components": 0,
  "unsupported_components": 0,
  "spice_ready_components": 3,
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
      "voltage_min": 4.31204191e-244,
      "voltage_max": 1.2303479e-16,
      "anode_node": "N004",
      "cathode_node": "0"
    }
  }
}
```

## Image policy

- Included by default: `False`
- Can be requested: `True`
- Path: `outputs\demo_workspaces\chat_agent_evaluation\input\images\a07.png`
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
  "best_scenario_id": "scenario_4",
  "best_outcome_status": "resolved_candidate",
  "best_stop_automation": true,
  "ranking_status": "verified_best",
  "interpretation_rule": "If a user asks which scenario resolves the problem, prefer the scenario with outcome_status='resolved_candidate' and stop_automation=true. Partially resolved scenarios without verified expectations are supporting diagnostics and must not be ranked only by changed_count.",
  "scenarios": [
    {
      "scenario_id": "scenario_1",
      "title": "Alimentare il nodo PWR dal connettore",
      "status": "spice_success",
      "spice_status": "success",
      "outcome_status": "partially_resolved",
      "outcome_label": "Ipotesi diagnostica confermata",
      "outcome_technical_label": "Diagnostic hypothesis confirmed",
      "outcome_reason": "I criteri dichiarati dal test diagnostico sono soddisfatti, ma lo scenario non applica una correzione del sintomo utente.",
      "stop_automation": false,
      "comparison_summary": {
        "requested_count": 3,
        "changed_count": 3,
        "activated_count": 3,
        "missing_count": 0,
        "expected_count": 2,
        "expectations_met_count": 2,
        "expectations_failed_count": 0,
        "expectations_missing_count": 0,
        "meaningful_improvement_count": 2,
        "quality_required": false,
        "quality_available": false,
        "quality_improved": false,
        "quality_acceptable": false,
        "quality_output_preserved": false,
        "base_thd": null,
        "scenario_thd": null,
        "gain_required": false,
        "gain_available": false,
        "gain_sufficient": false,
        "scenario_gain": null,
        "min_gain_ratio": null
      },
      "quantity_summary": {
        "changed": [
          "v(N002)",
          "v(N004)",
          "@dled12_1[id]"
        ],
        "unchanged": [],
        "missing": []
      },
      "led_profiles": {
        "Dled12_1": {
          "state": "steady_on",
          "regular_period": false,
          "frequency_hz": null,
          "duty_cycle": 1.0,
          "on_fraction": 1.0,
          "pulse_count": 1,
          "voltage_min": 0.702803114,
          "voltage_max": 0.702803197,
          "anode_node": "N004",
          "cathode_node": "0"
        }
      },
      "ranking_verified": true,
      "score": 50
    },
    {
      "scenario_id": "scenario_2",
      "title": "Applicare un segnale AC all'ingresso VAC",
      "status": "spice_success",
      "spice_status": "success",
      "outcome_status": "partially_resolved",
      "outcome_label": "Ipotesi diagnostica confermata",
      "outcome_technical_label": "Diagnostic hypothesis confirmed",
      "outcome_reason": "I criteri dichiarati dal test diagnostico sono soddisfatti, ma lo scenario non applica una correzione del sintomo utente.",
      "stop_automation": false,
      "comparison_summary": {
        "requested_count": 1,
        "changed_count": 1,
        "activated_count": 1,
        "missing_count": 0,
        "expected_count": 1,
        "expectations_met_count": 1,
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
        "gain_required": false,
        "gain_available": false,
        "gain_sufficient": false,
        "scenario_gain": null,
        "min_gain_ratio": null
      },
      "quantity_summary": {
        "changed": [
          "v(N001)"
        ],
        "unchanged": [],
        "missing": []
      },
      "led_profiles": {
        "Dled12_1": {
          "state": "off",
          "regular_period": false,
          "frequency_hz": null,
          "duty_cycle": 0.0,
          "on_fraction": 0.0,
          "pulse_count": 0,
          "voltage_min": 4.31204191e-244,
          "voltage_max": 1.2303479e-16,
          "anode_node": "N004",
          "cathode_node": "0"
        }
      },
      "ranking_verified": true,
      "score": 25
    },
    {
      "scenario_id": "scenario_4",
      "title": "Alimentare PWR e pilotare VAC nella stessa simulazione",
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
        "expected_count": 2,
        "expectations_met_count": 2,
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
        "gain_required": false,
        "gain_available": false,
        "gain_sufficient": false,
        "scenario_gain": null,
        "min_gain_ratio": null
      },
      "quantity_summary": {
        "changed": [
          "v(N001)",
          "v(N004)",
          "@dled12_1[id]"
        ],
        "unchanged": [
          "v(N002)"
        ],
        "missing": []
      },
      "led_profiles": {
        "Dled12_1": {
          "state": "steady_on",
          "regular_period": false,
          "frequency_hz": null,
          "duty_cycle": 1.0,
          "on_fraction": 1.0,
          "pulse_count": 1,
          "voltage_min": 0.702803114,
          "voltage_max": 0.702803197,
          "anode_node": "N004",
          "cathode_node": "0"
        }
      },
      "ranking_verified": true,
      "score": 200
    }
  ]
}
```


## Executed scenarios

### scenario_1

- Title: `Alimentare il nodo PWR dal connettore`
- Status: `spice_success`
- SPICE status: `success`
- Outcome: `partially_resolved`
- Stop automation: `False`
- Comparison: `3/3` changed
- LED profiles: `{"Dled12_1": {"state": "steady_on", "regular_period": false, "frequency_hz": null, "duty_cycle": 1.0, "on_fraction": 1.0, "pulse_count": 1, "voltage_min": 0.702803114, "voltage_max": 0.702803197, "anode_node": "N004", "cathode_node": "0"}}`

#### scenario_definition

- Role: Scenario selected by the user and saved before execution.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a07\scenarios\scenario_1\scenario.json`

```json
{
  "scenario_id": "scenario_1",
  "title": "Alimentare il nodo PWR dal connettore",
  "hypothesis": "Il LED di alimentazione e spento perche il nodo N002 etichettato PWR non e alimentato nel netlist base.",
  "intent": "diagnostic",
  "actions": [
    {
      "type": "add_voltage_source_between_nodes",
      "positive": "N002",
      "negative": "0",
      "value": "5V"
    }
  ],
  "rerun_from": "07",
  "analysis": "op",
  "compare": [
    "v(N002)",
    "v(N004)",
    "@dled12_1[id]"
  ],
  "expect": {
    "v(N002)": "activated",
    "@dled12_1[id]": "nonzero"
  }
}
```

#### scenario_status

- Role: Current scenario status, SPICE status and diagnostic outcome.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a07\scenarios\scenario_1\scenario_status.json`

```json
{
  "status": "spice_success",
  "stage": "scenario_spice_executed",
  "scenario_id": "scenario_1",
  "source": "guided_chat",
  "spice_executed": true,
  "created_or_updated_at": "2026-07-23T16:02:14",
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\scenarios\\scenario_1\\run\\08_spice_run.json",
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\scenarios\\scenario_1\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 3,
    "changed_count": 3,
    "activated_count": 3,
    "missing_count": 0,
    "expected_count": 2,
    "expectations_met_count": 2,
    "expectations_failed_count": 0,
    "expectations_missing_count": 0,
    "meaningful_improvement_count": 2,
    "quality_required": false,
    "quality_available": false,
    "quality_improved": false,
    "quality_acceptable": false,
    "quality_output_preserved": false,
    "base_thd": null,
    "scenario_thd": null,
    "gain_required": false,
    "gain_available": false,
    "gain_sufficient": false,
    "scenario_gain": null,
    "min_gain_ratio": null
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
  "controlled_scenario_report": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\scenarios\\scenario_1\\12_controlled_scenarios.json",
  "executed_scenarios_count": 1,
  "scenario_budget_exhausted": false,
  "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
}
```

#### controlled_scenario_report

- Role: Report produced by the controlled scenario runner.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a07\scenarios\scenario_1\12_controlled_scenarios.json`

```json
{
  "source_format": "pipeline2.0_controlled_scenario_report",
  "status": "spice_success",
  "scenario_id": "scenario_1",
  "scenario_title": "Alimentare il nodo PWR dal connettore",
  "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\scenarios\\scenario_1",
  "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\scenarios\\scenario_1\\run",
  "netlist": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\scenarios\\scenario_1\\run\\07_netlist.cir",
  "applied_actions": [
    {
      "status": "applied",
      "type": "add_voltage_source_between_nodes",
      "positive": "N002",
      "negative": "0",
      "nodes": [
        "N002",
        "0"
      ],
      "value": "5V",
      "normalized_source_definition": "DC 5",
      "normalized_dc_value": "5",
      "inserted_line": "VSCENARIO_SUPPLY_N002_0 N002 0 DC 5",
      "operation": "inserted",
      "spice_executed": false,
      "index": 1
    }
  ],
  "unsupported_actions": [],
  "failed_actions": [],
  "spice_executed": true,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\scenarios\\scenario_1\\run\\08_spice_run.json",
  "spice_status": "success",
  "spice_exit_code": 0,
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\scenarios\\scenario_1\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 3,
    "changed_count": 3,
    "activated_count": 3,
    "missing_count": 0,
    "expected_count": 2,
    "expectations_met_count": 2,
    "expectations_failed_count": 0,
    "expectations_missing_count": 0,
    "meaningful_improvement_count": 2,
    "quality_required": false,
    "quality_available": false,
    "quality_improved": false,
    "quality_acceptable": false,
    "quality_output_preserved": false,
    "base_thd": null,
    "scenario_thd": null,
    "gain_required": false,
    "gain_available": false,
    "gain_sufficient": false,
    "scenario_gain": null,
    "min_gain_ratio": null
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
  "created_or_updated_at": "2026-07-23T16:02:14"
}
```

#### scenario_comparison

- Role: Base-vs-scenario comparison used to evaluate the scenario.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a07\scenarios\scenario_1\scenario_comparison.json`

```json
{
  "source_format": "pipeline2.0_scenario_comparison",
  "scenario_id": "scenario_1",
  "scenario_title": "Alimentare il nodo PWR dal connettore",
  "scenario_intent": "diagnostic",
  "base_output_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07",
  "scenario_run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\scenarios\\scenario_1\\run",
  "base_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\08_ngspice_stdout.txt",
  "scenario_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\scenarios\\scenario_1\\run\\08_ngspice_stdout.txt",
  "base_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\08_ngspice_stderr.txt",
  "scenario_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\scenarios\\scenario_1\\run\\08_ngspice_stderr.txt",
  "quantities": [
    {
      "quantity": "v(N002)",
      "base_value": 1.230348e-16,
      "scenario_value": 5.0,
      "delta": 5.0,
      "change": "activated",
      "expectation": "activated",
      "expectation_met": true,
      "relative_change": 5000000000000.0,
      "meaningful_improvement": true,
      "metric": "v(n002)",
      "measurement": "op",
      "base_details": {},
      "scenario_details": {}
    },
    {
      "quantity": "v(N004)",
      "base_value": 1.230348e-16,
      "scenario_value": 0.7028032,
      "delta": 0.7028031999999999,
      "change": "activated",
      "expectation": null,
      "expectation_met": null,
      "relative_change": 702803199999.9999,
      "meaningful_improvement": false,
      "metric": "v(n004)",
      "measurement": "op",
      "base_details": {},
      "scenario_details": {}
    },
    {
      "quantity": "@dled12_1[id]",
      "base_value": 4.31204191e-256,
      "scenario_value": 0.00631940719,
      "delta": 0.00631940719,
      "change": "activated",
      "expectation": "nonzero",
      "expectation_met": true,
      "relative_change": 6319407190.0,
      "meaningful_improvement": true,
      "metric": "@dled12_1[id].final",
      "measurement": "op",
      "base_details": {
        "min": 4.31204191e-256,
        "max": 1.69664157e-28,
        "mean": 4.181446172248355e-31,
        "vpp": 1.69664157e-28,
        "final": 4.31204191e-256,
        "abs_peak": 1.69664157e-28
      },
      "scenario_details": {
        "min": 0.00631940719,
        "max": 0.00631942759,
        "mean": 0.006319407240000001,
        "vpp": 2.0400000000017626e-08,
        "final": 0.00631940719,
        "abs_peak": 0.00631942759
      }
    }
  ],
  "summary": {
    "requested_count": 3,
    "changed_count": 3,
    "activated_count": 3,
    "missing_count": 0,
    "expected_count": 2,
    "expectations_met_count": 2,
    "expectations_failed_count": 0,
    "expectations_missing_count": 0,
    "meaningful_improvement_count": 2,
    "quality_required": false,
    "quality_available": false,
    "quality_improved": false,
    "quality_acceptable": false,
    "quality_output_preserved": false,
    "base_thd": null,
    "scenario_thd": null,
    "gain_required": false,
    "gain_available": false,
    "gain_sufficient": false,
    "scenario_gain": null,
    "min_gain_ratio": null
  },
  "gain_comparison": null,
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
  "created_or_updated_at": "2026-07-23T16:02:14"
}
```

### scenario_2

- Title: `Applicare un segnale AC all'ingresso VAC`
- Status: `spice_success`
- SPICE status: `success`
- Outcome: `partially_resolved`
- Stop automation: `False`
- Comparison: `1/1` changed
- LED profiles: `{"Dled12_1": {"state": "off", "regular_period": false, "frequency_hz": null, "duty_cycle": 0.0, "on_fraction": 0.0, "pulse_count": 0, "voltage_min": 4.31204191e-244, "voltage_max": 1.2303479e-16, "anode_node": "N004", "cathode_node": "0"}}`

#### scenario_definition

- Role: Scenario selected by the user and saved before execution.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a07\scenarios\scenario_2\scenario.json`

```json
{
  "scenario_id": "scenario_2",
  "title": "Applicare un segnale AC all'ingresso VAC",
  "hypothesis": "Il voltmetro VAC non mostra nulla perche il nodo N001 non riceve alcun segnale nel netlist base.",
  "intent": "diagnostic",
  "actions": [
    {
      "type": "add_voltage_source_between_nodes",
      "positive": "N001",
      "negative": "0",
      "value": "SIN(0 5 50)"
    }
  ],
  "rerun_from": "07",
  "analysis": "tran",
  "compare": [
    "v(N001)"
  ],
  "expect": {
    "v(N001)": "changed"
  }
}
```

#### scenario_status

- Role: Current scenario status, SPICE status and diagnostic outcome.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a07\scenarios\scenario_2\scenario_status.json`

```json
{
  "status": "spice_success",
  "stage": "scenario_spice_executed",
  "scenario_id": "scenario_2",
  "source": "guided_chat",
  "spice_executed": true,
  "created_or_updated_at": "2026-07-23T16:03:06",
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\scenarios\\scenario_2\\run\\08_spice_run.json",
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\scenarios\\scenario_2\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 1,
    "changed_count": 1,
    "activated_count": 1,
    "missing_count": 0,
    "expected_count": 1,
    "expectations_met_count": 1,
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
    "gain_required": false,
    "gain_available": false,
    "gain_sufficient": false,
    "scenario_gain": null,
    "min_gain_ratio": null
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
  "controlled_scenario_report": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\scenarios\\scenario_2\\12_controlled_scenarios.json",
  "executed_scenarios_count": 2,
  "scenario_budget_exhausted": false,
  "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
}
```

#### controlled_scenario_report

- Role: Report produced by the controlled scenario runner.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a07\scenarios\scenario_2\12_controlled_scenarios.json`

```json
{
  "source_format": "pipeline2.0_controlled_scenario_report",
  "status": "spice_success",
  "scenario_id": "scenario_2",
  "scenario_title": "Applicare un segnale AC all'ingresso VAC",
  "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\scenarios\\scenario_2",
  "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\scenarios\\scenario_2\\run",
  "netlist": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\scenarios\\scenario_2\\run\\07_netlist.cir",
  "applied_actions": [
    {
      "status": "applied",
      "type": "add_voltage_source_between_nodes",
      "positive": "N001",
      "negative": "0",
      "nodes": [
        "N001",
        "0"
      ],
      "value": "SIN(0 5 50)",
      "normalized_source_definition": "SIN(0 5 50)",
      "normalized_dc_value": null,
      "inserted_line": "VSCENARIO_SUPPLY_N001_0 N001 0 SIN(0 5 50)",
      "operation": "inserted",
      "spice_executed": false,
      "index": 1
    }
  ],
  "unsupported_actions": [],
  "failed_actions": [],
  "spice_executed": true,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\scenarios\\scenario_2\\run\\08_spice_run.json",
  "spice_status": "success",
  "spice_exit_code": 0,
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\scenarios\\scenario_2\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 1,
    "changed_count": 1,
    "activated_count": 1,
    "missing_count": 0,
    "expected_count": 1,
    "expectations_met_count": 1,
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
    "gain_required": false,
    "gain_available": false,
    "gain_sufficient": false,
    "scenario_gain": null,
    "min_gain_ratio": null
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
  "created_or_updated_at": "2026-07-23T16:03:06"
}
```

#### scenario_comparison

- Role: Base-vs-scenario comparison used to evaluate the scenario.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a07\scenarios\scenario_2\scenario_comparison.json`

```json
{
  "source_format": "pipeline2.0_scenario_comparison",
  "scenario_id": "scenario_2",
  "scenario_title": "Applicare un segnale AC all'ingresso VAC",
  "scenario_intent": "diagnostic",
  "base_output_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07",
  "scenario_run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\scenarios\\scenario_2\\run",
  "base_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\08_ngspice_stdout.txt",
  "scenario_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\scenarios\\scenario_2\\run\\08_ngspice_stdout.txt",
  "base_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\08_ngspice_stderr.txt",
  "scenario_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\scenarios\\scenario_2\\run\\08_ngspice_stderr.txt",
  "quantities": [
    {
      "quantity": "v(N001)",
      "base_value": 0.0,
      "scenario_value": 9.99961312,
      "delta": 9.99961312,
      "change": "activated",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 9999613120000.0,
      "meaningful_improvement": false,
      "metric": "v(n001).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": 0.0,
        "max": 0.0,
        "mean": 0.0,
        "vpp": 0.0,
        "final": 0.0,
        "abs_peak": 0.0
      },
      "scenario_details": {
        "min": -4.99980656,
        "max": 4.99980656,
        "mean": 0.00032724829681371947,
        "vpp": 9.99961312,
        "final": -2.4492936e-15,
        "abs_peak": 4.99980656
      }
    }
  ],
  "summary": {
    "requested_count": 1,
    "changed_count": 1,
    "activated_count": 1,
    "missing_count": 0,
    "expected_count": 1,
    "expectations_met_count": 1,
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
    "gain_required": false,
    "gain_available": false,
    "gain_sufficient": false,
    "scenario_gain": null,
    "min_gain_ratio": null
  },
  "gain_comparison": null,
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
  "created_or_updated_at": "2026-07-23T16:03:06"
}
```

### scenario_4

- Title: `Alimentare PWR e pilotare VAC nella stessa simulazione`
- Status: `spice_success`
- SPICE status: `success`
- Outcome: `resolved_candidate`
- Stop automation: `True`
- Comparison: `3/4` changed
- LED profiles: `{"Dled12_1": {"state": "steady_on", "regular_period": false, "frequency_hz": null, "duty_cycle": 1.0, "on_fraction": 1.0, "pulse_count": 1, "voltage_min": 0.702803114, "voltage_max": 0.702803197, "anode_node": "N004", "cathode_node": "0"}}`

#### scenario_definition

- Role: Scenario selected by the user and saved before execution.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a07\scenarios\scenario_4\scenario.json`

```json
{
  "scenario_id": "scenario_4",
  "title": "Alimentare PWR e pilotare VAC nella stessa simulazione",
  "hypothesis": "Le due ipotesi gia confermate separatamente sono compatibili nella stessa run: 5 V DC su N002 deve mantenere corrente non nulla nel LED, mentre SIN(0 5 50) su N001 deve rendere variabile la tensione VAC.",
  "intent": "correction",
  "actions": [
    {
      "type": "add_voltage_source_between_nodes",
      "positive": "N002",
      "negative": "0",
      "value": "5V"
    },
    {
      "type": "add_voltage_source_between_nodes",
      "positive": "N001",
      "negative": "0",
      "value": "SIN(0 5 50)"
    }
  ],
  "rerun_from": "07",
  "analysis": "tran",
  "compare": [
    "v(N001)",
    "v(N002)",
    "v(N004)",
    "@dled12_1[id]"
  ],
  "expect": {
    "v(N001)": "changed",
    "@dled12_1[id]": "nonzero"
  },
  "measure": {
    "@dled12_1[id]": "tran_abs_peak"
  }
}
```

#### scenario_status

- Role: Current scenario status, SPICE status and diagnostic outcome.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a07\scenarios\scenario_4\scenario_status.json`

```json
{
  "status": "spice_success",
  "stage": "scenario_spice_executed",
  "scenario_id": "scenario_4",
  "source": "guided_chat",
  "spice_executed": true,
  "created_or_updated_at": "2026-07-23T16:04:49",
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\scenarios\\scenario_4\\run\\08_spice_run.json",
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\scenarios\\scenario_4\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 4,
    "changed_count": 3,
    "activated_count": 3,
    "missing_count": 0,
    "expected_count": 2,
    "expectations_met_count": 2,
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
    "gain_required": false,
    "gain_available": false,
    "gain_sufficient": false,
    "scenario_gain": null,
    "min_gain_ratio": null
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
  "controlled_scenario_report": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\scenarios\\scenario_4\\12_controlled_scenarios.json",
  "executed_scenarios_count": 3,
  "scenario_budget_exhausted": false,
  "next_step": "Ci sono gia evidenze forti per fermarsi qui e passare alla conclusione diagnostica."
}
```

#### controlled_scenario_report

- Role: Report produced by the controlled scenario runner.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a07\scenarios\scenario_4\12_controlled_scenarios.json`

```json
{
  "source_format": "pipeline2.0_controlled_scenario_report",
  "status": "spice_success",
  "scenario_id": "scenario_4",
  "scenario_title": "Alimentare PWR e pilotare VAC nella stessa simulazione",
  "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\scenarios\\scenario_4",
  "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\scenarios\\scenario_4\\run",
  "netlist": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\scenarios\\scenario_4\\run\\07_netlist.cir",
  "applied_actions": [
    {
      "status": "applied",
      "type": "add_voltage_source_between_nodes",
      "positive": "N002",
      "negative": "0",
      "nodes": [
        "N002",
        "0"
      ],
      "value": "5V",
      "normalized_source_definition": "DC 5",
      "normalized_dc_value": "5",
      "inserted_line": "VSCENARIO_SUPPLY_N002_0 N002 0 DC 5",
      "operation": "inserted",
      "spice_executed": false,
      "index": 1
    },
    {
      "status": "applied",
      "type": "add_voltage_source_between_nodes",
      "positive": "N001",
      "negative": "0",
      "nodes": [
        "N001",
        "0"
      ],
      "value": "SIN(0 5 50)",
      "normalized_source_definition": "SIN(0 5 50)",
      "normalized_dc_value": null,
      "inserted_line": "VSCENARIO_SUPPLY_N001_0 N001 0 SIN(0 5 50)",
      "operation": "inserted",
      "spice_executed": false,
      "index": 2
    }
  ],
  "unsupported_actions": [],
  "failed_actions": [],
  "spice_executed": true,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\scenarios\\scenario_4\\run\\08_spice_run.json",
  "spice_status": "success",
  "spice_exit_code": 0,
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\scenarios\\scenario_4\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 4,
    "changed_count": 3,
    "activated_count": 3,
    "missing_count": 0,
    "expected_count": 2,
    "expectations_met_count": 2,
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
    "gain_required": false,
    "gain_available": false,
    "gain_sufficient": false,
    "scenario_gain": null,
    "min_gain_ratio": null
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
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "created_or_updated_at": "2026-07-23T16:04:49"
}
```

#### scenario_comparison

- Role: Base-vs-scenario comparison used to evaluate the scenario.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a07\scenarios\scenario_4\scenario_comparison.json`

```json
{
  "source_format": "pipeline2.0_scenario_comparison",
  "scenario_id": "scenario_4",
  "scenario_title": "Alimentare PWR e pilotare VAC nella stessa simulazione",
  "scenario_intent": "correction",
  "base_output_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07",
  "scenario_run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\scenarios\\scenario_4\\run",
  "base_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\08_ngspice_stdout.txt",
  "scenario_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\scenarios\\scenario_4\\run\\08_ngspice_stdout.txt",
  "base_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\08_ngspice_stderr.txt",
  "scenario_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a07\\scenarios\\scenario_4\\run\\08_ngspice_stderr.txt",
  "quantities": [
    {
      "quantity": "v(N001)",
      "base_value": 0.0,
      "scenario_value": 9.99961312,
      "delta": 9.99961312,
      "change": "activated",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 9999613120000.0,
      "meaningful_improvement": false,
      "metric": "v(n001).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": 0.0,
        "max": 0.0,
        "mean": 0.0,
        "vpp": 0.0,
        "final": 0.0,
        "abs_peak": 0.0
      },
      "scenario_details": {
        "min": -4.99980656,
        "max": 4.99980656,
        "mean": 0.00032724829681371947,
        "vpp": 9.99961312,
        "final": -2.4492936e-15,
        "abs_peak": 4.99980656
      }
    },
    {
      "quantity": "v(N002)",
      "base_value": 1.2303479e-16,
      "scenario_value": 0.0,
      "delta": -1.2303479e-16,
      "change": "unchanged",
      "expectation": null,
      "expectation_met": null,
      "relative_change": 0.00012303479,
      "meaningful_improvement": false,
      "metric": "v(n002).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": 4.31204191e-244,
        "max": 1.2303479e-16,
        "mean": 3.0385695300914917e-19,
        "vpp": 1.2303479e-16,
        "final": 4.31204191e-244,
        "abs_peak": 1.2303479e-16
      },
      "scenario_details": {
        "min": 5.0,
        "max": 5.0,
        "mean": 5.0,
        "vpp": 0.0,
        "final": 5.0,
        "abs_peak": 5.0
      }
    },
    {
      "quantity": "v(N004)",
      "base_value": 1.2303479e-16,
      "scenario_value": 8.300000009509034e-08,
      "delta": 8.299999997205555e-08,
      "change": "activated",
      "expectation": null,
      "expectation_met": null,
      "relative_change": 82999.99997205555,
      "meaningful_improvement": false,
      "metric": "v(n004).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": 4.31204191e-244,
        "max": 1.2303479e-16,
        "mean": 3.0385695300914917e-19,
        "vpp": 1.2303479e-16,
        "final": 4.31204191e-244,
        "abs_peak": 1.2303479e-16
      },
      "scenario_details": {
        "min": 0.702803114,
        "max": 0.702803197,
        "mean": 0.7028031142034313,
        "vpp": 8.300000009509034e-08,
        "final": 0.702803114,
        "abs_peak": 0.702803197
      }
    },
    {
      "quantity": "@dled12_1[id]",
      "base_value": 1.69664157e-28,
      "scenario_value": 0.00631942759,
      "delta": 0.00631942759,
      "change": "activated",
      "expectation": "nonzero",
      "expectation_met": true,
      "relative_change": 6319427590.0,
      "meaningful_improvement": true,
      "metric": "@dled12_1[id].abs_peak",
      "measurement": "tran_abs_peak",
      "base_details": {
        "min": 4.31204191e-256,
        "max": 1.69664157e-28,
        "mean": 4.181446172248355e-31,
        "vpp": 1.69664157e-28,
        "final": 4.31204191e-256,
        "abs_peak": 1.69664157e-28
      },
      "scenario_details": {
        "min": 0.00631940719,
        "max": 0.00631942759,
        "mean": 0.006319407240000001,
        "vpp": 2.0400000000017626e-08,
        "final": 0.00631940719,
        "abs_peak": 0.00631942759
      }
    }
  ],
  "summary": {
    "requested_count": 4,
    "changed_count": 3,
    "activated_count": 3,
    "missing_count": 0,
    "expected_count": 2,
    "expectations_met_count": 2,
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
    "gain_required": false,
    "gain_available": false,
    "gain_sufficient": false,
    "scenario_gain": null,
    "min_gain_ratio": null
  },
  "gain_comparison": null,
  "quality_comparison": null,
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
  "created_or_updated_at": "2026-07-23T16:04:49"
}
```


## Loaded artifacts

### graph

- Step: `01`
- Role: Graph JSON copied from Pipeline 1.0.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a07\01_graph.json`

```json
{
  "image_id": "a07",
  "image_name": "a07.png",
  "components": [
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
      "component_id": "switch25.1",
      "instance_id": "25.1",
      "class_name": "Switch",
      "terminals": [
        {
          "terminal_id": "switch25.1_t1",
          "name": "t1",
          "relative_position": "left"
        },
        {
          "terminal_id": "switch25.1_t2",
          "name": "t2",
          "relative_position": "right"
        }
      ],
      "state": "open",
      "state_confidence": 0.95
    },
    {
      "component_id": "gnd9.2",
      "instance_id": "9.2",
      "class_name": "GND",
      "terminals": [
        {
          "terminal_id": "gnd9.2_t1",
          "name": "t1",
          "relative_position": "top"
        }
      ]
    },
    {
      "component_id": "connector5.1",
      "instance_id": "5.1",
      "class_name": "Connector",
      "terminals": [
        {
          "terminal_id": "connector5.1_pin1",
          "name": "pin1",
          "relative_position": "right"
        },
        {
          "terminal_id": "connector5.1_pin2",
          "name": "pin2",
          "relative_position": "right"
        },
        {
          "terminal_id": "connector5.1_pin3",
          "name": "pin3",
          "relative_position": "left"
        },
        {
          "terminal_id": "connector5.1_pin4",
          "name": "pin4",
          "relative_position": "left"
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
          "relative_position": "left"
        },
        {
          "terminal_id": "resistor22.1_t2",
          "name": "t2",
          "relative_position": "right"
        }
      ]
    },
    {
      "component_id": "gnd9.3",
      "instance_id": "9.3",
      "class_name": "GND",
      "terminals": [
        {
          "terminal_id": "gnd9.3_t1",
          "name": "t1",
          "relative_position": "top"
        }
      ]
    },
    {
      "component_id": "analog_meter0.1",
      "instance_id": "0.1",
      "class_name": "Analog_Meter",
      "terminals": [
        {
          "terminal_id": "analog_meter0.1_t1",
          "name": "t1",
          "relative_position": "bottom"
        },
        {
          "terminal_id": "analog_meter0.1_t2",
          "name": "t2",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "led12.1",
      "instance_id": "12.1",
      "class_name": "LED",
      "terminals": [
        {
          "terminal_id": "led12.1_anode",
          "name": "anode",
          "relative_position": "left"
        },
        {
          "terminal_id": "led12.1_cathode",
          "name": "cathode",
          "relative_position": "right"
        }
      ]
    },
    {
      "component_id": "gnd9.4",
      "instance_id": "9.4",
      "class_name": "GND",
      "terminals": [
        {
          "terminal_id": "gnd9.4_t1",
          "name": "t1",
          "relative_position": "top"
        }
      ]
    }
  ],
  "terminal_metadata": {},
  "graph": {
    "analog_meter0.1_t1": [
      "connector5.1_pin1"
    ],
    "analog_meter0.1_t2": [
      "gnd9.3_t1"
    ],
    "connector5.1_pin1": [
      "analog_meter0.1_t1"
    ],
    "connector5.1_pin2": [
      "resistor22.1_t1"
    ],
    "connector5.1_pin3": [
      "switch25.1_t2"
    ],
    "connector5.1_pin4": [
      "gnd9.2_t1"
    ],
    "gnd9.1_t1": [
      "switch25.1_t1"
    ],
    "gnd9.2_t1": [
      "connector5.1_pin4"
    ],
    "gnd9.3_t1": [
      "analog_meter0.1_t2"
    ],
    "gnd9.4_t1": [
      "led12.1_cathode"
    ],
    "led12.1_anode": [
      "resistor22.1_t2"
    ],
    "led12.1_cathode": [
      "gnd9.4_t1"
    ],
    "resistor22.1_t1": [
      "connector5.1_pin2"
    ],
    "resistor22.1_t2": [
      "led12.1_anode"
    ],
    "switch25.1_t1": [
      "gnd9.1_t1"
    ],
    "switch25.1_t2": [
      "connector5.1_pin3"
    ]
  },
  "warnings": {
    "unconnected_terminals": [],
    "unmatched_terminals": [],
    "suspicious_matches": []
  }
}
```

### node_map

- Step: `03`
- Role: Maps component terminals to SPICE node names.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a07\03_node_map.json`

```json
{
  "circuit_id": "a07",
  "source_format": "pipeline2.0_node_map",
  "nodes": [
    {
      "node_id": "0",
      "kind": "ground",
      "terminals": [
        "analog_meter0.1_t2",
        "connector5.1_pin4",
        "gnd9.1_t1",
        "gnd9.2_t1",
        "gnd9.3_t1",
        "gnd9.4_t1",
        "led12.1_cathode",
        "switch25.1_t1"
      ],
      "terminal_count": 8,
      "source_groups": [
        [
          "analog_meter0.1_t2",
          "gnd9.3_t1"
        ],
        [
          "connector5.1_pin4",
          "gnd9.2_t1"
        ],
        [
          "gnd9.1_t1",
          "switch25.1_t1"
        ],
        [
          "gnd9.4_t1",
          "led12.1_cathode"
        ]
      ]
    },
    {
      "node_id": "N001",
      "kind": "normal",
      "terminals": [
        "analog_meter0.1_t1",
        "connector5.1_pin1"
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
        "led12.1_anode",
        "resistor22.1_t2"
      ],
      "terminal_count": 2
    }
  ],
  "terminal_to_node": {
    "analog_meter0.1_t1": "N001",
    "analog_meter0.1_t2": "0",
    "connector5.1_pin1": "N001",
    "connector5.1_pin2": "N002",
    "connector5.1_pin3": "N003",
    "connector5.1_pin4": "0",
    "gnd9.1_t1": "0",
    "gnd9.2_t1": "0",
    "gnd9.3_t1": "0",
    "gnd9.4_t1": "0",
    "led12.1_anode": "N004",
    "led12.1_cathode": "0",
    "resistor22.1_t1": "N002",
    "resistor22.1_t2": "N004",
    "switch25.1_t1": "0",
    "switch25.1_t2": "N003"
  },
  "component_terminal_nodes": {
    "analog_meter0.1": {
      "t1": "N001",
      "t2": "0"
    },
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
    "gnd9.4": {
      "t1": "0"
    },
    "led12.1": {
      "anode": "N004",
      "cathode": "0"
    },
    "resistor22.1": {
      "t1": "N002",
      "t2": "N004"
    },
    "switch25.1": {
      "t1": "0",
      "t2": "N003"
    }
  },
  "warnings": {
    "ground_groups_count": 4,
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
    "nodes_count": 5,
    "normal_nodes_count": 4,
    "ground_nodes_count": 1,
    "ground_groups_count": 4,
    "terminal_to_node_count": 16,
    "singleton_nodes_count": 0
  }
}
```

### values_bound

- Step: `04`
- Role: Values and labels bound to graph components.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a07\04_values_bound.json`

```json
{
  "circuit_id": "a07",
  "source_format": "pipeline2.0_values_bound",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\data\\batchPipeline2.0\\batchChatAgentEvaluation\\values\\a07_values.yaml",
  "supplies": {},
  "components": {
    "analog_meter0.1": {
      "class_name": "Analog_Meter",
      "terminal_nodes": {
        "t1": "N001",
        "t2": "0"
      },
      "value_data": {
        "kind": "voltmeter",
        "measured_quantity": "voltage_ac",
        "input_resistance": 10000000,
        "resistance_unit": "ohm",
        "label": "VAC",
        "source": "manual_from_image_label",
        "label_text": "VAC"
      },
      "status": "not_required"
    },
    "connector5.1": {
      "class_name": "Connector",
      "terminal_nodes": {
        "pin1": "N001",
        "pin2": "N002",
        "pin3": "N003",
        "pin4": "0"
      },
      "value_data": null,
      "status": "not_required"
    },
    "gnd9.1": {
      "class_name": "GND",
      "terminal_nodes": {
        "t1": "0"
      },
      "value_data": null,
      "status": "not_required"
    },
    "gnd9.2": {
      "class_name": "GND",
      "terminal_nodes": {
        "t1": "0"
      },
      "value_data": null,
      "status": "not_required"
    },
    "gnd9.3": {
      "class_name": "GND",
      "terminal_nodes": {
        "t1": "0"
      },
      "value_data": null,
      "status": "not_required"
    },
    "gnd9.4": {
      "class_name": "GND",
      "terminal_nodes": {
        "t1": "0"
      },
      "value_data": null,
      "status": "not_required"
    },
    "led12.1": {
      "class_name": "LED",
      "terminal_nodes": {
        "anode": "N004",
        "cathode": "0"
      },
      "value_data": {
        "model": "LED_RED",
        "source": "manual_assumption",
        "label_text": "PWR"
      },
      "status": "bound"
    },
    "resistor22.1": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N002",
        "t2": "N004"
      },
      "value_data": {
        "value": 680,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "680R"
      },
      "status": "bound"
    },
    "switch25.1": {
      "class_name": "Switch",
      "terminal_nodes": {
        "t1": "0",
        "t2": "N003"
      },
      "value_data": {
        "state": "open",
        "state_source": "graph_json_state",
        "state_confidence": 0.95,
        "source": "graph_json_state",
        "label_text": "RESET"
      },
      "status": "bound"
    }
  },
  "nodes": {
    "connector5.1_pin1": {
      "label": "AC_INPUT",
      "source": "manual_from_image_label",
      "label_text": "VAC",
      "node": "N001"
    },
    "connector5.1_pin2": {
      "label": "PWR",
      "source": "manual_from_image_label",
      "label_text": "PWR",
      "node": "N002"
    },
    "connector5.1_pin3": {
      "label": "RESET",
      "source": "manual_from_image_label",
      "label_text": "RESET",
      "node": "N003"
    },
    "connector5.1_pin4": {
      "label": "GND",
      "spice_node": 0,
      "source": "graph_json_gnd",
      "node": "0"
    }
  },
  "spice_topology_overlay": [],
  "simulation": {
    "analyses": [
      "op",
      "tran"
    ],
    "tran": {
      "step": "0.1ms",
      "stop": "40ms"
    }
  },
  "missing": [],
  "stats": {
    "components_total": 9,
    "bound_components": 3,
    "missing_components": 0,
    "not_required_components": 6,
    "unsupported_components": 0,
    "supplies_count": 0,
    "manual_nodes_count": 4
  }
}
```

### component_rules

- Step: `06`
- Role: SPICE conversion rules for each component.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a07\06_component_rules.json`

```json
{
  "circuit_id": "a07",
  "source_format": "pipeline2.0_component_rules",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\data\\batchPipeline2.0\\batchChatAgentEvaluation\\values\\a07_values.yaml",
  "spice_classes_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_spice_classes.yaml",
  "supplies": {},
  "components": {
    "analog_meter0.1": {
      "class_name": "Analog_Meter",
      "status": "measurement_only",
      "spice_support": "measurement",
      "emit_as": "voltage_probe",
      "measurement_kind": "voltage",
      "node_order": [
        "t1",
        "t2"
      ],
      "nodes": [
        "N001",
        "0"
      ],
      "parameters": {
        "kind": "voltmeter",
        "measured_quantity": "voltage_ac",
        "input_resistance": 10000000,
        "resistance_unit": "ohm",
        "label": "VAC",
        "source": "manual_from_image_label",
        "label_text": "VAC"
      },
      "reason": "Voltmeter/probe only: not emitted as a physical SPICE component; read the voltage between its nodes."
    },
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
    "gnd9.4": {
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
        "N004",
        "0"
      ],
      "parameters": {
        "model": "LED_RED",
        "source": "manual_assumption",
        "label_text": "PWR"
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
        "value": 680,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "680R"
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
        "source": "graph_json_state",
        "label_text": "RESET"
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
      "step": "0.1ms",
      "stop": "40ms"
    }
  },
  "stats": {
    "components_total": 9,
    "spice_ready_components": 3,
    "not_emitted_components": 5,
    "measurement_components": 1,
    "missing_components": 0,
    "unsupported_components": 0,
    "pin_aware_components": 0,
    "invalid_components": 0,
    "supplies_ready_count": 0
  }
}
```

### netlist

- Step: `07`
- Role: Generated SPICE netlist.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a07\07_netlist.cir`

```spice
* pipeline2.0 netlist
* circuit: a07

Rmeter_analog_meter0_1 N001 0 10000000
Dled12_1 N004 0 LED_RED
Rresistor22_1 N002 N004 680
* switch25.1 open: not emitted

.model LED_RED D

.op
.save all
.tran 0.1ms 40ms

.control
set wr_singlescale
set wr_vecnames
save all @dled12_1[id]
run
wrdata 08_tran.csv time v(N001) v(N002) v(N004) @dled12_1[id]
.endc
.end

```

### spice_emit_report

- Step: `07`
- Role: Report of emitted, skipped and warning components.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a07\07_spice_emit_report.json`

```json
{
  "circuit_id": "a07",
  "source_format": "pipeline2.0_spice_emit_report",
  "emitted_elements": 3,
  "skipped_elements": 5,
  "skipped_components": [
    "connector5.1",
    "gnd9.1",
    "gnd9.2",
    "gnd9.3",
    "gnd9.4"
  ],
  "informational_skips": [
    "connector5.1: structural component not emitted",
    "gnd9.1: structural component not emitted",
    "gnd9.2: structural component not emitted",
    "gnd9.3: structural component not emitted",
    "gnd9.4: structural component not emitted"
  ],
  "measurement_points": [
    {
      "component_id": "analog_meter0.1",
      "kind": "voltage",
      "nodes": [
        "N001",
        "0"
      ],
      "emit_as": "voltage_probe",
      "reason": "Voltmeter/probe only: not emitted as a physical SPICE component; read the voltage between its nodes."
    }
  ],
  "analyses": [
    "op",
    "tran"
  ],
  "transient_export": {
    "path": "08_tran.csv",
    "nodes": [
      "N001",
      "N002",
      "N004"
    ],
    "device_currents": [
      "@dled12_1[id]"
    ]
  },
  "models": [
    "LED_RED"
  ],
  "warnings": [
    "switch25.1: open switch not emitted"
  ]
}
```

### spice_run

- Step: `08`
- Role: Structured ngspice execution report.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a07\08_spice_run.json`

```json
{
  "source_format": "pipeline2.0_spice_run",
  "status": "success",
  "netlist_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\a07\\07_netlist.cir",
  "command": [
    "C:\\Users\\m.profilo\\Spice64\\bin\\ngspice_con.exe",
    "-b",
    "07_netlist.cir"
  ],
  "exit_code": 0,
  "stdout_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\a07\\08_ngspice_stdout.txt",
  "stderr_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\a07\\08_ngspice_stderr.txt",
  "tran_raw_csv_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\a07\\08_tran_raw.csv",
  "tran_csv_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\a07\\08_tran.csv",
  "tran_plot_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\a07\\08_tran_plot.png",
  "tran_plot_png_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\a07\\08_tran_plot.png",
  "tran_plot_svg_path": null,
  "message": "ngspice completed successfully."
}
```

### ngspice_stdout

- Step: `08`
- Role: Raw ngspice stdout log.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a07\08_ngspice_stdout.txt`

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
n004                               1.23035e-16
n002                               1.23035e-16


No. of Data Rows : 408
Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

No. of Data Rows : 1

Initial Transient Solution
--------------------------

Node                                   Voltage
----                                   -------
n001                                         0
n004                               1.23035e-16
n002                               1.23035e-16


No. of Data Rows : 408
	Node                                  Voltage
	----                                  -------
	----	-------
	n002                             1.230348e-16
	n004                             1.230348e-16
	n001                             0.000000e+00

	Source	Current
	------	-------

	@dled12_1[id]                    1.696642e-28

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
         vd          4.31204e-244
         id          4.31204e-256
         gd           1.38662e-12
         cd                     0

 Resistor: Simple linear resistor
     device         rresistor22_1 rmeter_analog_meter0_
      model                     R                     R
 resistance                   680                 1e+07
         ac                   680                 1e+07
      dtemp                     0                     0
     bv_max                 1e+99                 1e+99
      noisy                     1                     1
          i                     0                     0
          p                     0                     0


Total analysis time (seconds) = 0.0087979

Total elapsed time (seconds) = 0.172 

Total DRAM available = 32239.535 MB.
DRAM currently available = 15155.590 MB.
Maximum ngspice program size =   15.035 MB.
Current ngspice program size =   15.035 MB.


```

### ngspice_stderr

- Step: `08`
- Role: Raw ngspice stderr log.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a07\08_ngspice_stderr.txt`

```text

```

### tran_csv

- Step: `08`
- Role: Clean transient CSV, when .tran data is available.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a07\08_tran.csv`

```csv
time,v(N001),v(N002),v(N004),@dled12_1[id]
0.0,0.0,1.2303479e-16,1.2303479e-16,1.69664157e-28
1e-06,0.0,6.77073793e-19,6.77073793e-19,6.77073793e-31
2e-06,0.0,1.88784428e-19,1.88784428e-19,1.88784428e-31
4e-06,0.0,5.26376309e-20,5.26376309e-20,5.26376309e-32
8e-06,0.0,1.46766352e-20,1.46766352e-20,1.46766352e-32
1.6e-05,0.0,4.09219824e-21,4.09219824e-21,4.09219824e-33
3.2e-05,0.0,1.14100311e-21,1.14100311e-21,1.14100311e-33
6.4e-05,0.0,3.1813906e-22,3.1813906e-22,3.1813906e-34
0.000128,0.0,8.87048078e-23,8.87048078e-23,8.87048078e-35
0.000228,0.0,2.473303e-23,2.473303e-23,2.473303e-35
0.000328,0.0,6.89616254e-24,6.89616254e-24,6.89616254e-36
0.000428,0.0,1.92281567e-24,1.92281567e-24,1.92281567e-36
0.000528,0.0,5.36127172e-25,5.36127172e-25,5.36127172e-37
0.000628,0.0,1.49485127e-25,1.49485127e-25,1.49485127e-37
0.000728,0.0,4.16800421e-26,4.16800421e-26,4.16800421e-38
0.000828,0.0,1.16213964e-26,1.16213964e-26,1.16213964e-38
0.000928,0.0,3.24032431e-27,3.24032431e-27,3.24032431e-39
0.001028,0.0,9.03480209e-28,9.03480209e-28,9.03480209e-40
0.001128,0.0,2.51911972e-28,2.51911972e-28,2.51911972e-40
0.001228,0.0,7.02391057e-29,7.02391057e-29,7.02391057e-41
0.001328,0.0,1.95843489e-29,1.95843489e-29,1.95843489e-41
0.001428,0.0,5.46058665e-30,5.46058665e-30,5.46058665e-42
0.001528,0.0,1.52254265e-30,1.52254265e-30,1.52254265e-42
0.001628,0.0,4.24521444e-31,4.24521444e-31,4.24521444e-43
0.001728,0.0,1.1836677e-31,1.1836677e-31,1.1836677e-43
0.001828,0.0,3.30034973e-32,3.30034973e-32,3.30034973e-44
0.001928,0.0,9.20216737e-33,9.20216737e-33,9.20216737e-45
0.002028,0.0,2.56578518e-33,2.56578518e-33,2.56578518e-45
0.002128,0.0,7.15402507e-34,7.15402507e-34,7.15402507e-46
0.002228,0.0,1.99471394e-34,1.99471394e-34,1.99471394e-46
0.002328,0.0,5.56174135e-35,5.56174135e-35,5.56174135e-47
0.002428,0.0,1.55074701e-35,1.55074701e-35,1.55074701e-47
0.002528,0.0,4.32385496e-36,4.32385496e-36,4.32385496e-48
0.002628,0.0,1.20559457e-36,1.20559457e-36,1.20559457e-48
0.002728,0.0,3.36148709e-37,3.36148709e-37,3.36148709e-49
0.002828,0.0,9.37263302e-38,9.37263302e-38,9.37263302e-50
0.002928,0.0,2.6133151e-38,2.6133151e-38,2.6133151e-50
0.003028,0.0,7.28654988e-39,7.28654988e-39,7.28654988e-51
0.003128,0.0,2.03166504e-39,2.03166504e-39,2.03166504e-51
0.003228,0.0,5.66476988e-40,5.66476988e-40,5.66476988e-52
0.003328,0.0,1.57947384e-40,1.57947384e-40,1.57947384e-52
0.003428,0.0,4.40395226e-41,4.40395226e-41,4.40395226e-53
0.003528,0.0,1.22792762e-41,1.22792762e-41,1.22792762e-53
0.003628,0.0,3.42375699e-42,3.42375699e-42,3.42375699e-54
0.003728,0.0,9.54625645e-43,9.54625645e-43,9.54625645e-55
0.003828,0.0,2.66172548e-43,2.66172548e-43,2.66172548e-55
0.003928,0.0,7.42152965e-44,7.42152965e-44,7.42152965e-56
0.004028,0.0,2.06930064e-44,2.06930064e-44,2.06930064e-56
0.004128,0.0,5.76970697e-45,5.76970697e-45,5.76970697e-57
0.004228,0.0,1.60873282e-45,1.60873282e-45,1.60873282e-57
0.004328,0.0,4.48553332e-46,4.48553332e-46,4.48553332e-58
0.004428,0.0,1.25067438e-46,1.25067438e-46,1.25067438e-58
0.004528,0.0,3.48718041e-47,3.48718041e-47,3.48718041e-59
0.004628,0.0,9.72309618e-48,9.72309618e-48,9.72309618e-60
0.004728,0.0,2.71103264e-48,2.71103264e-48,2.71103264e-60
0.004828,0.0,7.55900986e-49,7.55900986e-49,7.55900986e-61
0.004928,0.0,2.10763342e-49,2.10763342e-49,2.10763342e-61
0.005028,0.0,5.87658797e-50,5.87658797e-50,5.87658797e-62
0.005128,0.0,1.63853381e-50,1.63853381e-50,1.63853381e-62
0.005228,0.0,4.56862562e-51,4.56862562e-51,4.56862562e-63
0.005328,0.0,1.27384251e-51,1.27384251e-51,1.27384251e-63
0.005428,0.0,3.55177872e-52,3.55177872e-52,3.55177872e-64
0.005528,0.0,9.90321177e-53,9.90321177e-53,9.90321177e-65
0.005628,0.0,2.76125319e-53,2.76125319e-53,2.76125319e-65
0.005728,0.0,7.69903681e-54,7.69903681e-54,7.69903681e-66
0.005828,0.0,2.1466763e-54,2.1466763e-54,2.1466763e-66
0.005928,0.0,5.98544888e-55,5.98544888e-55,5.98544888e-67
0.006028,0.0,1.66888684e-55,1.66888684e-55,1.66888684e-67
0.006128,0.0,4.65325718e-56,4.65325718e-56,4.65325718e-68
0.006228,0.0,1.29743981e-56,1.29743981e-56,1.29743981e-68
0.006328,0.0,3.61757368e-57,3.61757368e-57,3.61757368e-69
0.006428,0.0,1.00866639e-57,1.00866639e-57,1.00866639e-69
0.006528,0.0,2.81240406e-58,2.81240406e-58,2.81240406e-70
0.006628,0.0,7.8416577e-59,7.8416577e-59,7.8416577e-71
0.006728,0.0,2.18644242e-59,2.18644242e-59,2.18644242e-71
0.006828,0.0,6.09632639e-60,6.09632639e-60,6.09632639e-72
0.006928,0.0,1.69980215e-60,1.69980215e-60,1.69980215e-72
0.007028,0.0,4.73945649e-61,4.73945649e-61,4.73945649e-73
0.007128,0.0,1.32147425e-61,1.32147425e-61,1.32147425e-73
0.007228,0.0,3.68458747e-62,3.68458747e-62,3.68458747e-74
0.007328,0.0,1.02735144e-62,1.02735144e-62,1.02735144e-74
0.007428,0.0,2.86450246e-63,2.86450246e-63,2.86450246e-75
0.007528,0.0,7.98692057e-64,7.98692057e-64,7.98692057e-76
0.007628,0.0,2.2269452e-64,2.2269452e-64,2.2269452e-76
0.007728,0.0,6.20925785e-65,6.20925785e-65,6.20925785e-77
0.007828,0.0,1.73129016e-65,1.73129016e-65,1.73129016e-77
0.007928,0.0,4.8272526e-66,4.8272526e-66,4.8272526e-78
0.008028,0.0,1.34595391e-66,1.34595391e-66,1.34595391e-78
0.008128,0.0,3.75284264e-67,3.75284264e-67,3.75284264e-79
0.008228,0.0,1.04638263e-67,1.04638263e-67,1.04638263e-79
0.008328,0.0,2.91756597e-68,2.91756597e-68,2.91756597e-80
0.008428,0.0,8.13487436e-69,8.13487436e-69,8.13487436e-81
0.008528,0.0,2.26819827e-69,2.26819827e-69,2.26819827e-81
0.008628,0.0,6.32428131e-70,6.32428131e-70,6.32428131e-82
0.008728,0.0,1.76336146e-70,1.76336146e-70,1.76336146e-82
0.008828,0.0,4.91667509e-71,4.91667509e-71,4.91667509e-83
0.008928,0.0,1.37088705e-71,1.37088705e-71,1.37088705e-83
0.009028,0.0,3.82236222e-72,3.82236222e-72,3.82236222e-84
0.009128,0.0,1.06576635e-72,1.06576635e-72,1.06576635e-84
0.009228,0.0,2.97161245e-73,2.97161245e-73,2.97161245e-85
0.009328,0.0,8.28556892e-74,8.28556892e-74,8.28556892e-86
0.009428,0.0,2.31021553e-74,2.31021553e-74,2.31021553e-86
0.009528,0.0,6.44143552e-75,6.44143552e-75,6.44143552e-87
0.009628,0.0,1.79602687e-75,1.79602687e-75,1.79602687e-87
0.009728,0.0,5.00775409e-76,5.00775409e-76,5.00775409e-88
0.009828,0.0,1.39628206e-76,1.39628206e-76,1.39628206e-88
0.009928,0.0,3.8931696e-77,3.8931696e-77,3.8931696e-89
0.010028,0.0,1.08550915e-77,1.08550915e-77,1.08550915e-89
0.010128,0.0,3.02666012e-78,3.02666012e-78,3.02666012e-90
0.010228,0.0,8.43905503e-79,8.43905503e-79,8.43905503e-91
0.010328,0.0,2.35301114e-79,2.35301114e-79,2.35301114e-91
0.010428,0.0,6.56075996e-80,6.56075996e-80,6.56075996e-92
0.010528,0.0,1.82929739e-80,1.82929739e-80,1.82929739e-92
0.010628,0.0,5.10052028e-81,5.10052028e-81,5.10052028e-93
0.010728,0.0,1.4221475e-81,1.4221475e-81,1.4221475e-93
0.010828,0.0,3.96528866e-82,3.96528866e-82,3.96528866e-94
0.010928,0.0,1.10561768e-82,1.10561768e-82,1.10561768e-94
0.011028,0.0,3.08272751e-83,3.08272751e-83,3.08272751e-95
0.011128,0.0,8.59538439e-84,8.59538439e-84,8.59538439e-96
0.011228,0.0,2.39659952e-84,2.39659952e-84,2.39659952e-96
0.011328,0.0,6.68229483e-85,6.68229483e-85,6.68229483e-97
0.011428,0.0,1.86318422e-85,1.86318422e-85,1.86318422e-97
0.011528,0.0,5.19500492e-86,5.19500492e-86,5.19500492e-98
0.011628,0.0,1.44849209e-86,1.44849209e-86,1.44849209e-98
0.011728,0.0,4.03874369e-87,4.03874369e-87,4.03874369e-99
0.011828,0.0,1.1260987e-87,1.1260987e-87,1.1260987e-99
0.011928,0.0,3.13983353e-88,3.13983353e-88,3.13983353e-100
0.012028,0.0,8.75460967e-89,8.75460967e-89,8.75460967e-101
0.012128,0.0,2.44099535e-89,2.44099535e-89,2.44099535e-101
0.012228,0.0,6.80608107e-90,6.80608107e-90,6.80608107e-102
0.012328,0.0,1.8976988e-90,1.8976988e-90,1.8976988e-102
0.012428,0.0,5.29123984e-91,5.29123984e-91,5.29123984e-103
0.012528,0.0,1.4753247e-91,1.4753247e-91,1.4753247e-103
0.012628,0.0,4.11355944e-92,4.11355944e-92,4.11355944e-104
0.012728,0.0,1.14695913e-92,1.14695913e-92,1.14695913e-104
0.012828,0.0,3.19799741e-93,3.19799741e-93,3.19799741e-105
0.012928,0.0,8.91678453e-94,8.91678453e-94,8.91678453e-106
0.013028,0.0,2.4862136e-94,2.4862136e-94,2.4862136e-106
0.013128,0.0,6.93216039e-95,6.93216039e-95,6.93216039e-107
0.013228,0.0,1.93285274e-95,1.93285274e-95,1.93285274e-107
0.013328,0.0,5.38925747e-96,5.38925747e-96,5.38925747e-108
0.013428,0.0,1.50265436e-96,1.50265436e-96,1.50265436e-108
0.013528,0.0,4.18976112e-97,4.18976112e-97,4.18976112e-109
0.013628,0.0,1.16820599e-97,1.16820599e-97,1.16820599e-109
0.013728,0.0,3.25723874e-98,3.25723874e-98,3.25723874e-110
0.013828,0.0,9.0819636e-99,9.0819636e-99,9.0819636e-111
0.013928,0.0,2.53226949e-99,2.53226949e-99,2.53226949e-111
0.014028,0.0,7.06057526e-100,7.06057526e-100,7.06057526e-112
0.014128,0.0,1.96865789e-100,1.96865789e-100,1.96865789e-112
0.014228,0.0,5.48909082e-101,5.48909082e-101,5.48909082e-113
0.014328,0.0,1.5304903e-101,1.5304903e-101,1.5304903e-113
0.014428,0.0,4.26737439e-102,4.26737439e-102,4.26737439e-114
0.014528,0.0,1.18984643e-102,1.18984643e-102,1.18984643e-114
0.014628,0.0,3.3175775e-103,3.3175775e-103,3.3175775e-115
0.014728,0.0,9.25020253e-104,9.25020253e-104,9.25020253e-116
0.014828,0.0,2.57917854e-104,2.57917854e-104,2.57917854e-116
0.014928,0.0,7.19136896e-105,7.19136896e-105,7.19136896e-117
0.015028,0.0,2.00512631e-105,2.00512631e-105,2.00512631e-117
0.015128,0.0,5.59077354e-106,5.59077354e-106,5.59077354e-118
0.015228,0.0,1.55884188e-106,1.55884188e-106,1.55884188e-118
0.015328,0.0,4.34642541e-107,4.34642541e-107,4.34642541e-119
0.015428,0.0,1.21188775e-107,1.21188775e-107,1.21188775e-119
0.015528,0.0,3.37903399e-108,3.37903399e-108,3.37903399e-120
0.015628,0.0,9.421558e-109,9.421558e-109,9.421558e-121
0.015728,0.0,2.62695656e-109,2.62695656e-109,2.62695656e-121
0.015828,0.0,7.32458555e-110,7.32458555e-110,7.32458555e-122
0.015928,0.0,2.0422703e-110,2.0422703e-110,2.0422703e-122
0.016028,0.0,5.69433988e-111,5.69433988e-111,5.69433988e-123
0.016128,0.0,1.58771867e-111,1.58771867e-111,1.58771867e-123
0.016228,0.0,4.42694081e-112,4.42694081e-112,4.42694081e-124
0.016328,0.0,1.23433738e-112,1.23433738e-112,1.23433738e-124
0.016428,0.0,3.44162894e-113,3.44162894e-113,3.44162894e-125
0.016528,0.0,9.59608774e-114,9.59608774e-114,9.59608774e-126
0.016628,0.0,2.67561964e-114,2.67561964e-114,2.67561964e-126
0.016728,0.0,7.46026991e-115,7.46026991e-115,7.46026991e-127
0.016828,0.0,2.08010235e-115,2.08010235e-115,2.08010235e-127
0.016928,0.0,5.79982474e-116,5.79982474e-116,5.79982474e-128
0.017028,0.0,1.61713038e-116,1.61713038e-116,1.61713038e-128
0.017128,0.0,4.50894772e-117,4.50894772e-117,4.50894772e-129
0.017228,0.0,1.25720287e-117,1.25720287e-117,1.25720287e-129
0.017328,0.0,3.50538343e-118,3.50538343e-118,3.50538343e-130
0.017428,0.0,9.77385057e-119,9.77385057e-119,9.77385057e-131
0.017528,0.0,2.72518418e-119,2.72518418e-119,2.72518418e-131
0.017628,0.0,7.59846776e-120,7.59846776e-120,7.59846776e-132
0.017728,0.0,2.11863523e-120,2.11863523e-120,2.11863523e-132
0.017828,0.0,5.90726365e-121,5.90726365e-121,5.90726365e-133
0.017928,0.0,1.64708693e-121,1.64708693e-121,1.64708693e-133
0.018028,0.0,4.59247377e-122,4.59247377e-122,4.59247377e-134
0.018128,0.0,1.28049194e-122,1.28049194e-122,1.28049194e-134
0.018228,0.0,3.57031895e-123,3.57031895e-123,3.57031895e-135
0.018328,0.0,9.95490637e-124,9.95490637e-124,9.95490637e-136
0.018428,0.0,2.77566689e-124,2.77566689e-124,2.77566689e-136
0.018528,0.0,7.73922565e-125,7.73922565e-125,7.73922565e-137
0.018628,0.0,2.15788191e-125,2.15788191e-125,2.15788191e-137
0.018728,0.0,6.01669282e-126,6.01669282e-126,6.01669282e-138
0.018828,0.0,1.6775984e-126,1.6775984e-126,1.6775984e-138
0.018928,0.0,4.6775471e-127,4.6775471e-127,4.6775471e-139
0.019028,0.0,1.30421243e-127,1.30421243e-127,1.30421243e-139
0.019128,0.0,3.63645736e-128,3.63645736e-128,3.63645736e-140
0.019228,0.0,1.01393161e-128,1.01393161e-128,1.01393161e-140
0.019328,0.0,2.82708476e-129,2.82708476e-129,2.82708476e-141
0.019428,0.0,7.88259101e-130,7.88259101e-130,7.88259101e-142
0.019528,0.0,2.19785562e-130,2.19785562e-130,2.19785562e-142
0.019628,0.0,6.12814911e-131,6.12814911e-131,6.12814911e-143
0.019728,0.0,1.70867509e
```

> Artifact truncated in this preview. The original file remains available through the manifest path.
