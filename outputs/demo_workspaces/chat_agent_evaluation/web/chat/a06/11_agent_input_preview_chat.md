# Agent input preview

This file is a local preview of the evidence that will be provided to the read-only diagnostic agent.
The agent remains read-only: it can inspect base outputs and existing scenario artifacts, but it does not modify files.

## User problem

Lo scenario 5 raggiunge THD 9,79% su N005, rispetto a 83,0% nella base run, e conserva un guadagno fondamentale circa 77×. Fornisci la conclusione finale: causa isolata, correzione verificata, dati prima/dopo e limite della metrica THD calcolata esternamente ai campi automatici. Non proporre altri scenari.

## Circuit

- Batch: `batchChatAgentEvaluation`
- Circuit: `a06`
- Agent mode: `graph_grounded_readonly`

## Technical summary

```json
{
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_message": "ngspice completed successfully.",
  "emitted_elements": 13,
  "skipped_elements": 7,
  "emit_warnings_count": 0,
  "skipped_components_count": 7,
  "node_count": 9,
  "ground_groups_count": 4,
  "singleton_nodes_count": 0,
  "bound_components": 11,
  "missing_components": 0,
  "unsupported_components": 0,
  "spice_ready_components": 11,
  "rules_missing_components": 0,
  "has_tran_csv": true,
  "has_tran_plot": true,
  "led_profiles": {}
}
```

## Image policy

- Included by default: `False`
- Can be requested: `True`
- Path: `outputs\demo_workspaces\chat_agent_evaluation\input\images\a06.jpg`
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
  "best_scenario_id": "scenario_1",
  "best_outcome_status": "partially_resolved",
  "best_stop_automation": false,
  "ranking_status": "verified_best",
  "interpretation_rule": "If a user asks which scenario resolves the problem, prefer the scenario with outcome_status='resolved_candidate' and stop_automation=true. Partially resolved scenarios without verified expectations are supporting diagnostics and must not be ranked only by changed_count.",
  "scenarios": [
    {
      "scenario_id": "scenario_1",
      "title": "Ridurre l’ampiezza della sorgente di ingresso",
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
        "gain_required": false,
        "gain_available": false,
        "gain_sufficient": false,
        "scenario_gain": null,
        "min_gain_ratio": null
      },
      "quantity_summary": {
        "changed": [
          "v(N006)",
          "v(N004)",
          "v(N005)"
        ],
        "unchanged": [],
        "missing": []
      },
      "led_profiles": {},
      "ranking_verified": true,
      "score": 30
    },
    {
      "scenario_id": "scenario_4",
      "title": "Ridurre ancora l’ampiezza d’ingresso per cercare una THD più bassa",
      "status": "spice_success",
      "spice_status": "success",
      "outcome_status": "partially_resolved",
      "outcome_label": "Variazione non ancora significativa",
      "outcome_technical_label": "Improvement too small",
      "outcome_reason": "I criteri direzionali sono soddisfatti, ma nessun effetto correttivo raggiunge la soglia relativa del 10%.",
      "stop_automation": false,
      "comparison_summary": {
        "requested_count": 2,
        "changed_count": 2,
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
        "scenario_gain": 62.74741298765466,
        "min_gain_ratio": 5.0
      },
      "quantity_summary": {
        "changed": [
          "v(N006)",
          "v(N005)"
        ],
        "unchanged": [],
        "missing": []
      },
      "led_profiles": {},
      "ranking_verified": true,
      "score": 30
    },
    {
      "scenario_id": "scenario_5",
      "title": "Ridurre l’ingresso a 20 mV mantenendo il controllo di guadagno",
      "status": "spice_success",
      "spice_status": "success",
      "outcome_status": "partially_resolved",
      "outcome_label": "Variazione non ancora significativa",
      "outcome_technical_label": "Improvement too small",
      "outcome_reason": "I criteri direzionali sono soddisfatti, ma nessun effetto correttivo raggiunge la soglia relativa del 10%.",
      "stop_automation": false,
      "comparison_summary": {
        "requested_count": 2,
        "changed_count": 2,
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
        "scenario_gain": 77.8932184755591,
        "min_gain_ratio": 5.0
      },
      "quantity_summary": {
        "changed": [
          "v(N006)",
          "v(N005)"
        ],
        "unchanged": [],
        "missing": []
      },
      "led_profiles": {},
      "ranking_verified": true,
      "score": 30
    }
  ]
}
```


## Executed scenarios

### scenario_1

- Title: `Ridurre l’ampiezza della sorgente di ingresso`
- Status: `spice_success`
- SPICE status: `success`
- Outcome: `partially_resolved`
- Stop automation: `False`
- Comparison: `3/3` changed
- LED profiles: `{}`

#### scenario_definition

- Role: Scenario selected by the user and saved before execution.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a06\scenarios\scenario_1\scenario.json`

```json
{
  "scenario_id": "scenario_1",
  "title": "Ridurre l’ampiezza della sorgente di ingresso",
  "hypothesis": "The output distortion may be caused by overdriving the transistor stage with the present input amplitude.",
  "intent": "diagnostic",
  "actions": [
    {
      "type": "change_source_value",
      "target": "Vsignal_source23_1",
      "value": "SIN(0 100m 100)"
    }
  ],
  "rerun_from": "07",
  "analysis": "tran",
  "compare": [
    "v(N006)",
    "v(N004)",
    "v(N005)"
  ],
  "expect": {
    "v(N004)": "changed",
    "v(N005)": "changed"
  }
}
```

#### scenario_status

- Role: Current scenario status, SPICE status and diagnostic outcome.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a06\scenarios\scenario_1\scenario_status.json`

```json
{
  "status": "spice_success",
  "stage": "scenario_spice_executed",
  "scenario_id": "scenario_1",
  "source": "guided_chat",
  "spice_executed": true,
  "created_or_updated_at": "2026-07-23T13:03:39",
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\scenarios\\scenario_1\\run\\08_spice_run.json",
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\scenarios\\scenario_1\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 3,
    "changed_count": 3,
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
  "controlled_scenario_report": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\scenarios\\scenario_1\\12_controlled_scenarios.json",
  "executed_scenarios_count": 1,
  "scenario_budget_exhausted": false,
  "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
}
```

#### controlled_scenario_report

- Role: Report produced by the controlled scenario runner.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a06\scenarios\scenario_1\12_controlled_scenarios.json`

```json
{
  "source_format": "pipeline2.0_controlled_scenario_report",
  "status": "spice_success",
  "scenario_id": "scenario_1",
  "scenario_title": "Ridurre l’ampiezza della sorgente di ingresso",
  "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\scenarios\\scenario_1",
  "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\scenarios\\scenario_1\\run",
  "netlist": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\scenarios\\scenario_1\\run\\07_netlist.cir",
  "applied_actions": [
    {
      "status": "applied",
      "type": "change_source_value",
      "target": "Vsignal_source23_1",
      "resolved_source_name": "Vsignal_source23_1",
      "tried_source_names": [
        "Vsignal_source23_1"
      ],
      "value": "SIN(0 100m 100)",
      "normalized_source_definition": "SIN(0 100m 100)",
      "old_line": "Vsignal_source23_1 N006 0 SIN(0 1 100)",
      "new_line": "Vsignal_source23_1 N006 0 SIN(0 100m 100)",
      "operation": "updated",
      "spice_executed": false,
      "index": 1
    }
  ],
  "unsupported_actions": [],
  "failed_actions": [],
  "spice_executed": true,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\scenarios\\scenario_1\\run\\08_spice_run.json",
  "spice_status": "success",
  "spice_exit_code": 0,
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\scenarios\\scenario_1\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 3,
    "changed_count": 3,
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
  "created_or_updated_at": "2026-07-23T13:03:39"
}
```

#### scenario_comparison

- Role: Base-vs-scenario comparison used to evaluate the scenario.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a06\scenarios\scenario_1\scenario_comparison.json`

```json
{
  "source_format": "pipeline2.0_scenario_comparison",
  "scenario_id": "scenario_1",
  "scenario_title": "Ridurre l’ampiezza della sorgente di ingresso",
  "scenario_intent": "diagnostic",
  "base_output_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06",
  "scenario_run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\scenarios\\scenario_1\\run",
  "base_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\08_ngspice_stdout.txt",
  "scenario_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\scenarios\\scenario_1\\run\\08_ngspice_stdout.txt",
  "base_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\08_ngspice_stderr.txt",
  "scenario_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\scenarios\\scenario_1\\run\\08_ngspice_stderr.txt",
  "quantities": [
    {
      "quantity": "v(N006)",
      "base_value": 1.999999632,
      "scenario_value": 0.199999999,
      "delta": -1.7999996329999999,
      "change": "changed",
      "expectation": null,
      "expectation_met": null,
      "relative_change": 0.8999999820999967,
      "meaningful_improvement": false,
      "metric": "v(n006).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": -0.999999816,
        "max": 0.999999816,
        "mean": 0.00203509394659454,
        "vpp": 1.999999632,
        "final": -1.2246468e-15,
        "abs_peak": 0.999999816
      },
      "scenario_details": {
        "min": -0.0999999995,
        "max": 0.0999999995,
        "mean": 8.977517480768592e-05,
        "vpp": 0.199999999,
        "final": -1.2246468e-16,
        "abs_peak": 0.0999999995
      }
    },
    {
      "quantity": "v(N004)",
      "base_value": 7.170986879999999,
      "scenario_value": 6.843207230000001,
      "delta": -0.3277796499999983,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 0.045709140943233514,
      "meaningful_improvement": false,
      "metric": "v(n004).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": 2.94564482,
        "max": 10.1166317,
        "mean": 8.084793870409356,
        "vpp": 7.170986879999999,
        "final": 10.1129477,
        "abs_peak": 10.1166317
      },
      "scenario_details": {
        "min": 3.06044296,
        "max": 9.90365019,
        "mean": 7.224606231666667,
        "vpp": 6.843207230000001,
        "final": 5.61031926,
        "abs_peak": 9.90365019
      }
    },
    {
      "quantity": "v(N005)",
      "base_value": 7.47417467,
      "scenario_value": 6.9551392100000005,
      "delta": -0.5190354599999996,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 0.06944384937688372,
      "meaningful_improvement": false,
      "metric": "v(n005).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": -4.2926905,
        "max": 3.18148417,
        "mean": 1.09695133535731,
        "vpp": 7.47417467,
        "final": 2.76984986,
        "abs_peak": 4.2926905
      },
      "scenario_details": {
        "min": -3.85571627,
        "max": 3.09942294,
        "mean": 0.40650892781729414,
        "vpp": 6.9551392100000005,
        "final": -1.36734842,
        "abs_peak": 3.85571627
      }
    }
  ],
  "summary": {
    "requested_count": 3,
    "changed_count": 3,
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
  "created_or_updated_at": "2026-07-23T13:03:39"
}
```

### scenario_4

- Title: `Ridurre ancora l’ampiezza d’ingresso per cercare una THD più bassa`
- Status: `spice_success`
- SPICE status: `success`
- Outcome: `partially_resolved`
- Stop automation: `False`
- Comparison: `2/2` changed
- LED profiles: `{}`

#### scenario_definition

- Role: Scenario selected by the user and saved before execution.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a06\scenarios\scenario_4\scenario.json`

```json
{
  "scenario_id": "scenario_4",
  "title": "Ridurre ancora l’ampiezza d’ingresso per cercare una THD più bassa",
  "hypothesis": "Since scenario_1 reduced distortion without suppressing output transfer, a further reduction of Vsignal_source23_1 to 50 mV may lower THD at N005 while preserving useful gain from N006 to N005.",
  "intent": "correction",
  "actions": [
    {
      "type": "change_source_value",
      "target": "Vsignal_source23_1",
      "value": "SIN(0 50m 100)"
    }
  ],
  "rerun_from": "07",
  "analysis": "tran",
  "compare": [
    "v(N006)",
    "v(N005)"
  ],
  "expect": {
    "v(N006)": "changed",
    "v(N005)": "changed"
  },
  "gain": {
    "input": "v(N006)",
    "output": "v(N005)",
    "min_ratio": 5
  }
}
```

#### scenario_status

- Role: Current scenario status, SPICE status and diagnostic outcome.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a06\scenarios\scenario_4\scenario_status.json`

```json
{
  "status": "spice_success",
  "stage": "scenario_spice_executed",
  "scenario_id": "scenario_4",
  "source": "guided_chat",
  "spice_executed": true,
  "created_or_updated_at": "2026-07-23T13:06:05",
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\scenarios\\scenario_4\\run\\08_spice_run.json",
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\scenarios\\scenario_4\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 2,
    "changed_count": 2,
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
    "scenario_gain": 62.74741298765466,
    "min_gain_ratio": 5.0
  },
  "diagnostic_outcome": {
    "status": "partially_resolved",
    "technical_label": "Improvement too small",
    "label": "Variazione non ancora significativa",
    "reason": "I criteri direzionali sono soddisfatti, ma nessun effetto correttivo raggiunge la soglia relativa del 10%.",
    "user_message": "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato.",
    "stop_automation": false,
    "confidence": "low",
    "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
  },
  "controlled_scenario_report": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\scenarios\\scenario_4\\12_controlled_scenarios.json",
  "executed_scenarios_count": 2,
  "scenario_budget_exhausted": false,
  "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
}
```

#### controlled_scenario_report

- Role: Report produced by the controlled scenario runner.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a06\scenarios\scenario_4\12_controlled_scenarios.json`

```json
{
  "source_format": "pipeline2.0_controlled_scenario_report",
  "status": "spice_success",
  "scenario_id": "scenario_4",
  "scenario_title": "Ridurre ancora l’ampiezza d’ingresso per cercare una THD più bassa",
  "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\scenarios\\scenario_4",
  "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\scenarios\\scenario_4\\run",
  "netlist": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\scenarios\\scenario_4\\run\\07_netlist.cir",
  "applied_actions": [
    {
      "status": "applied",
      "type": "change_source_value",
      "target": "Vsignal_source23_1",
      "resolved_source_name": "Vsignal_source23_1",
      "tried_source_names": [
        "Vsignal_source23_1"
      ],
      "value": "SIN(0 50m 100)",
      "normalized_source_definition": "SIN(0 50m 100)",
      "old_line": "Vsignal_source23_1 N006 0 SIN(0 1 100)",
      "new_line": "Vsignal_source23_1 N006 0 SIN(0 50m 100)",
      "operation": "updated",
      "spice_executed": false,
      "index": 1
    }
  ],
  "unsupported_actions": [],
  "failed_actions": [],
  "spice_executed": true,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\scenarios\\scenario_4\\run\\08_spice_run.json",
  "spice_status": "success",
  "spice_exit_code": 0,
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\scenarios\\scenario_4\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 2,
    "changed_count": 2,
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
    "scenario_gain": 62.74741298765466,
    "min_gain_ratio": 5.0
  },
  "diagnostic_outcome": {
    "status": "partially_resolved",
    "technical_label": "Improvement too small",
    "label": "Variazione non ancora significativa",
    "reason": "I criteri direzionali sono soddisfatti, ma nessun effetto correttivo raggiunge la soglia relativa del 10%.",
    "user_message": "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato.",
    "stop_automation": false,
    "confidence": "low",
    "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
  },
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "created_or_updated_at": "2026-07-23T13:06:05"
}
```

#### scenario_comparison

- Role: Base-vs-scenario comparison used to evaluate the scenario.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a06\scenarios\scenario_4\scenario_comparison.json`

```json
{
  "source_format": "pipeline2.0_scenario_comparison",
  "scenario_id": "scenario_4",
  "scenario_title": "Ridurre ancora l’ampiezza d’ingresso per cercare una THD più bassa",
  "scenario_intent": "correction",
  "base_output_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06",
  "scenario_run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\scenarios\\scenario_4\\run",
  "base_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\08_ngspice_stdout.txt",
  "scenario_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\scenarios\\scenario_4\\run\\08_ngspice_stdout.txt",
  "base_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\08_ngspice_stderr.txt",
  "scenario_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\scenarios\\scenario_4\\run\\08_ngspice_stderr.txt",
  "quantities": [
    {
      "quantity": "v(N006)",
      "base_value": 1.999999632,
      "scenario_value": 0.0999845248,
      "delta": -1.9000151072,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 0.950007728401422,
      "meaningful_improvement": false,
      "metric": "v(n006).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": -0.999999816,
        "max": 0.999999816,
        "mean": 0.00203509394659454,
        "vpp": 1.999999632,
        "final": -1.2246468e-15,
        "abs_peak": 0.999999816
      },
      "scenario_details": {
        "min": -0.0499922624,
        "max": 0.0499922624,
        "mean": 5.256541397637675e-06,
        "vpp": 0.0999845248,
        "final": -6.123234e-17,
        "abs_peak": 0.0499922624
      }
    },
    {
      "quantity": "v(N005)",
      "base_value": 7.47417467,
      "scenario_value": 6.27377027,
      "delta": -1.2004044,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 0.1606069503323502,
      "meaningful_improvement": false,
      "metric": "v(n005).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": -4.2926905,
        "max": 3.18148417,
        "mean": 1.09695133535731,
        "vpp": 7.47417467,
        "final": 2.76984986,
        "abs_peak": 4.2926905
      },
      "scenario_details": {
        "min": -3.62991237,
        "max": 2.6438579,
        "mean": 0.08632875838866141,
        "vpp": 6.27377027,
        "final": -1.62021803,
        "abs_peak": 3.62991237
      }
    }
  ],
  "summary": {
    "requested_count": 2,
    "changed_count": 2,
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
    "scenario_gain": 62.74741298765466,
    "min_gain_ratio": 5.0
  },
  "gain_comparison": {
    "input": "v(N006)",
    "output": "v(N005)",
    "base_gain": 3.7370880226241963,
    "scenario_gain": 62.74741298765466,
    "min_ratio": 5.0,
    "available": true,
    "sufficient": true,
    "relative_change": 15.790456261073885
  },
  "quality_comparison": null,
  "diagnostic_outcome": {
    "status": "partially_resolved",
    "technical_label": "Improvement too small",
    "label": "Variazione non ancora significativa",
    "reason": "I criteri direzionali sono soddisfatti, ma nessun effetto correttivo raggiunge la soglia relativa del 10%.",
    "user_message": "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato.",
    "stop_automation": false,
    "confidence": "low",
    "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
  },
  "created_or_updated_at": "2026-07-23T13:06:05"
}
```

### scenario_5

- Title: `Ridurre l’ingresso a 20 mV mantenendo il controllo di guadagno`
- Status: `spice_success`
- SPICE status: `success`
- Outcome: `partially_resolved`
- Stop automation: `False`
- Comparison: `2/2` changed
- LED profiles: `{}`

#### scenario_definition

- Role: Scenario selected by the user and saved before execution.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a06\scenarios\scenario_5\scenario.json`

```json
{
  "scenario_id": "scenario_5",
  "title": "Ridurre l’ingresso a 20 mV mantenendo il controllo di guadagno",
  "hypothesis": "Since scenario_4 kept useful gain from N006 to N005 at 50 mV but the user reports THD on N005 is still 22.4%, reducing Vsignal_source23_1 to 20 mV may further lower distortion at N005 while preserving useful transfer.",
  "intent": "correction",
  "actions": [
    {
      "type": "change_source_value",
      "target": "Vsignal_source23_1",
      "value": "SIN(0 20m 100)"
    }
  ],
  "rerun_from": "07",
  "analysis": "tran",
  "compare": [
    "v(N006)",
    "v(N005)"
  ],
  "expect": {
    "v(N006)": "changed",
    "v(N005)": "changed"
  },
  "gain": {
    "input": "v(N006)",
    "output": "v(N005)",
    "min_ratio": 5
  }
}
```

#### scenario_status

- Role: Current scenario status, SPICE status and diagnostic outcome.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a06\scenarios\scenario_5\scenario_status.json`

```json
{
  "status": "spice_success",
  "stage": "scenario_spice_executed",
  "scenario_id": "scenario_5",
  "source": "guided_chat",
  "spice_executed": true,
  "created_or_updated_at": "2026-07-23T13:09:24",
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\scenarios\\scenario_5\\run\\08_spice_run.json",
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\scenarios\\scenario_5\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 2,
    "changed_count": 2,
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
    "scenario_gain": 77.8932184755591,
    "min_gain_ratio": 5.0
  },
  "diagnostic_outcome": {
    "status": "partially_resolved",
    "technical_label": "Improvement too small",
    "label": "Variazione non ancora significativa",
    "reason": "I criteri direzionali sono soddisfatti, ma nessun effetto correttivo raggiunge la soglia relativa del 10%.",
    "user_message": "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato.",
    "stop_automation": false,
    "confidence": "low",
    "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
  },
  "controlled_scenario_report": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\scenarios\\scenario_5\\12_controlled_scenarios.json",
  "executed_scenarios_count": 3,
  "scenario_budget_exhausted": false,
  "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
}
```

#### controlled_scenario_report

- Role: Report produced by the controlled scenario runner.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a06\scenarios\scenario_5\12_controlled_scenarios.json`

```json
{
  "source_format": "pipeline2.0_controlled_scenario_report",
  "status": "spice_success",
  "scenario_id": "scenario_5",
  "scenario_title": "Ridurre l’ingresso a 20 mV mantenendo il controllo di guadagno",
  "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\scenarios\\scenario_5",
  "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\scenarios\\scenario_5\\run",
  "netlist": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\scenarios\\scenario_5\\run\\07_netlist.cir",
  "applied_actions": [
    {
      "status": "applied",
      "type": "change_source_value",
      "target": "Vsignal_source23_1",
      "resolved_source_name": "Vsignal_source23_1",
      "tried_source_names": [
        "Vsignal_source23_1"
      ],
      "value": "SIN(0 20m 100)",
      "normalized_source_definition": "SIN(0 20m 100)",
      "old_line": "Vsignal_source23_1 N006 0 SIN(0 1 100)",
      "new_line": "Vsignal_source23_1 N006 0 SIN(0 20m 100)",
      "operation": "updated",
      "spice_executed": false,
      "index": 1
    }
  ],
  "unsupported_actions": [],
  "failed_actions": [],
  "spice_executed": true,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\scenarios\\scenario_5\\run\\08_spice_run.json",
  "spice_status": "success",
  "spice_exit_code": 0,
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\scenarios\\scenario_5\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 2,
    "changed_count": 2,
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
    "scenario_gain": 77.8932184755591,
    "min_gain_ratio": 5.0
  },
  "diagnostic_outcome": {
    "status": "partially_resolved",
    "technical_label": "Improvement too small",
    "label": "Variazione non ancora significativa",
    "reason": "I criteri direzionali sono soddisfatti, ma nessun effetto correttivo raggiunge la soglia relativa del 10%.",
    "user_message": "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato.",
    "stop_automation": false,
    "confidence": "low",
    "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
  },
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "created_or_updated_at": "2026-07-23T13:09:24"
}
```

#### scenario_comparison

- Role: Base-vs-scenario comparison used to evaluate the scenario.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a06\scenarios\scenario_5\scenario_comparison.json`

```json
{
  "source_format": "pipeline2.0_scenario_comparison",
  "scenario_id": "scenario_5",
  "scenario_title": "Ridurre l’ingresso a 20 mV mantenendo il controllo di guadagno",
  "scenario_intent": "correction",
  "base_output_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06",
  "scenario_run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\scenarios\\scenario_5\\run",
  "base_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\08_ngspice_stdout.txt",
  "scenario_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\scenarios\\scenario_5\\run\\08_ngspice_stdout.txt",
  "base_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\08_ngspice_stderr.txt",
  "scenario_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\a06\\scenarios\\scenario_5\\run\\08_ngspice_stderr.txt",
  "quantities": [
    {
      "quantity": "v(N006)",
      "base_value": 1.999999632,
      "scenario_value": 0.03999381,
      "delta": -1.960005822,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 0.9800030913205688,
      "meaningful_improvement": false,
      "metric": "v(n006).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": -0.999999816,
        "max": 0.999999816,
        "mean": 0.00203509394659454,
        "vpp": 1.999999632,
        "final": -1.2246468e-15,
        "abs_peak": 0.999999816
      },
      "scenario_details": {
        "min": -0.019996905,
        "max": 0.019996905,
        "mean": 2.1026165509842037e-06,
        "vpp": 0.03999381,
        "final": -2.4492936e-17,
        "abs_peak": 0.019996905
      }
    },
    {
      "quantity": "v(N005)",
      "base_value": 7.47417467,
      "scenario_value": 3.11524658,
      "delta": -4.35892809,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 0.58319858478769,
      "meaningful_improvement": false,
      "metric": "v(n005).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": -4.2926905,
        "max": 3.18148417,
        "mean": 1.09695133535731,
        "vpp": 7.47417467,
        "final": 2.76984986,
        "abs_peak": 4.2926905
      },
      "scenario_details": {
        "min": -1.69147012,
        "max": 1.42377646,
        "mean": 0.03290228024076378,
        "vpp": 3.11524658,
        "final": -0.852222712,
        "abs_peak": 1.69147012
      }
    }
  ],
  "summary": {
    "requested_count": 2,
    "changed_count": 2,
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
    "scenario_gain": 77.8932184755591,
    "min_gain_ratio": 5.0
  },
  "gain_comparison": {
    "input": "v(N006)",
    "output": "v(N005)",
    "base_gain": 3.7370880226241963,
    "scenario_gain": 77.8932184755591,
    "min_ratio": 5.0,
    "available": true,
    "sufficient": true,
    "relative_change": 19.843292425545332
  },
  "quality_comparison": null,
  "diagnostic_outcome": {
    "status": "partially_resolved",
    "technical_label": "Improvement too small",
    "label": "Variazione non ancora significativa",
    "reason": "I criteri direzionali sono soddisfatti, ma nessun effetto correttivo raggiunge la soglia relativa del 10%.",
    "user_message": "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato.",
    "stop_automation": false,
    "confidence": "low",
    "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
  },
  "created_or_updated_at": "2026-07-23T13:09:24"
}
```


## Loaded artifacts

### graph

- Step: `01`
- Role: Graph JSON copied from Pipeline 1.0.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a06\01_graph.json`

```json
{
  "image_id": "a06",
  "image_name": "a06.jpg",
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
      "component_id": "signal_source23.1",
      "instance_id": "23.1",
      "class_name": "Signal_Source",
      "terminals": [
        {
          "terminal_id": "signal_source23.1_t1",
          "name": "t1",
          "relative_position": "top"
        },
        {
          "terminal_id": "signal_source23.1_t2",
          "name": "t2",
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
      "component_id": "capacitor4.1",
      "instance_id": "4.1",
      "class_name": "Capacitor",
      "terminals": [
        {
          "terminal_id": "capacitor4.1_t1",
          "name": "t1",
          "relative_position": "left"
        },
        {
          "terminal_id": "capacitor4.1_t2",
          "name": "t2",
          "relative_position": "right"
        }
      ]
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
      "component_id": "terminal26.1",
      "instance_id": "26.1",
      "class_name": "Terminal",
      "terminals": [
        {
          "terminal_id": "terminal26.1_t1",
          "name": "t1",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "npn_transistor18.1",
      "instance_id": "18.1",
      "class_name": "NPN_Transistor",
      "terminals": [
        {
          "terminal_id": "npn_transistor18.1_B",
          "name": "B",
          "relative_position": "left"
        },
        {
          "terminal_id": "npn_transistor18.1_C",
          "name": "C",
          "relative_position": "top"
        },
        {
          "terminal_id": "npn_transistor18.1_E",
          "name": "E",
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
      "component_id": "terminal26.2",
      "instance_id": "26.2",
      "class_name": "Terminal",
      "terminals": [
        {
          "terminal_id": "terminal26.2_t1",
          "name": "t1",
          "relative_position": "top"
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
      "component_id": "capacitor4.2",
      "instance_id": "4.2",
      "class_name": "Capacitor",
      "terminals": [
        {
          "terminal_id": "capacitor4.2_t1",
          "name": "t1",
          "relative_position": "top"
        },
        {
          "terminal_id": "capacitor4.2_t2",
          "name": "t2",
          "relative_position": "bottom"
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
      "component_id": "capacitor4.3",
      "instance_id": "4.3",
      "class_name": "Capacitor",
      "terminals": [
        {
          "terminal_id": "capacitor4.3_t1",
          "name": "t1",
          "relative_position": "left"
        },
        {
          "terminal_id": "capacitor4.3_t2",
          "name": "t2",
          "relative_position": "right"
        }
      ]
    },
    {
      "component_id": "resistor22.6",
      "instance_id": "22.6",
      "class_name": "Resistor",
      "terminals": [
        {
          "terminal_id": "resistor22.6_t1",
          "name": "t1",
          "relative_position": "top"
        },
        {
          "terminal_id": "resistor22.6_t2",
          "name": "t2",
          "relative_position": "bottom"
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
    },
    {
      "component_id": "terminal26.3",
      "instance_id": "26.3",
      "class_name": "Terminal",
      "terminals": [
        {
          "terminal_id": "terminal26.3_t1",
          "name": "t1",
          "relative_position": "left"
        }
      ]
    }
  ],
  "terminal_metadata": {},
  "graph": {
    "capacitor4.1_t1": [
      "resistor22.1_t2"
    ],
    "capacitor4.1_t2": [
      "npn_transistor18.1_B",
      "resistor22.2_t2",
      "resistor22.3_t1"
    ],
    "capacitor4.2_t1": [
      "npn_transistor18.1_E",
      "resistor22.5_t1"
    ],
    "capacitor4.2_t2": [
      "gnd9.3_t1"
    ],
    "capacitor4.3_t1": [
      "npn_transistor18.1_C",
      "resistor22.4_t2"
    ],
    "capacitor4.3_t2": [
      "resistor22.6_t1",
      "terminal26.3_t1"
    ],
    "gnd9.1_t1": [
      "signal_source23.1_t2"
    ],
    "gnd9.2_t1": [
      "resistor22.3_t2"
    ],
    "gnd9.3_t1": [
      "capacitor4.2_t2"
    ],
    "gnd9.4_t1": [
      "resistor22.6_t2"
    ],
    "npn_transistor18.1_B": [
      "capacitor4.1_t2",
      "resistor22.2_t2",
      "resistor22.3_t1"
    ],
    "npn_transistor18.1_C": [
      "capacitor4.3_t1",
      "resistor22.4_t2"
    ],
    "npn_transistor18.1_E": [
      "capacitor4.2_t1",
      "resistor22.5_t1"
    ],
    "resistor22.1_t1": [
      "signal_source23.1_t1"
    ],
    "resistor22.1_t2": [
      "capacitor4.1_t1"
    ],
    "resistor22.2_t1": [
      "resistor22.4_t1",
      "terminal26.1_t1"
    ],
    "resistor22.2_t2": [
      "capacitor4.1_t2",
      "npn_transistor18.1_B",
      "resistor22.3_t1"
    ],
    "resistor22.3_t1": [
      "capacitor4.1_t2",
      "npn_transistor18.1_B",
      "resistor22.2_t2"
    ],
    "resistor22.3_t2": [
      "gnd9.2_t1"
    ],
    "resistor22.4_t1": [
      "resistor22.2_t1",
      "terminal26.1_t1"
    ],
    "resistor22.4_t2": [
      "capacitor4.3_t1",
      "npn_transistor18.1_C"
    ],
    "resistor22.5_t1": [
      "capacitor4.2_t1",
      "npn_transistor18.1_E"
    ],
    "resistor22.5_t2": [
      "terminal26.2_t1"
    ],
    "resistor22.6_t1": [
      "capacitor4.3_t2",
      "terminal26.3_t1"
    ],
    "resistor22.6_t2": [
      "gnd9.4_t1"
    ],
    "signal_source23.1_t1": [
      "resistor22.1_t1"
    ],
    "signal_source23.1_t2": [
      "gnd9.1_t1"
    ],
    "terminal26.1_t1": [
      "resistor22.2_t1",
      "resistor22.4_t1"
    ],
    "terminal26.2_t1": [
      "resistor22.5_t2"
    ],
    "terminal26.3_t1": [
      "capacitor4.3_t2",
      "resistor22.6_t1"
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
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a06\03_node_map.json`

```json
{
  "circuit_id": "a06",
  "source_format": "pipeline2.0_node_map",
  "nodes": [
    {
      "node_id": "0",
      "kind": "ground",
      "terminals": [
        "capacitor4.2_t2",
        "gnd9.1_t1",
        "gnd9.2_t1",
        "gnd9.3_t1",
        "gnd9.4_t1",
        "resistor22.3_t2",
        "resistor22.6_t2",
        "signal_source23.1_t2"
      ],
      "terminal_count": 8,
      "source_groups": [
        [
          "capacitor4.2_t2",
          "gnd9.3_t1"
        ],
        [
          "gnd9.1_t1",
          "signal_source23.1_t2"
        ],
        [
          "gnd9.2_t1",
          "resistor22.3_t2"
        ],
        [
          "gnd9.4_t1",
          "resistor22.6_t2"
        ]
      ]
    },
    {
      "node_id": "N001",
      "kind": "normal",
      "terminals": [
        "capacitor4.1_t1",
        "resistor22.1_t2"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N002",
      "kind": "normal",
      "terminals": [
        "capacitor4.1_t2",
        "npn_transistor18.1_B",
        "resistor22.2_t2",
        "resistor22.3_t1"
      ],
      "terminal_count": 4
    },
    {
      "node_id": "N003",
      "kind": "normal",
      "terminals": [
        "capacitor4.2_t1",
        "npn_transistor18.1_E",
        "resistor22.5_t1"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N004",
      "kind": "normal",
      "terminals": [
        "capacitor4.3_t1",
        "npn_transistor18.1_C",
        "resistor22.4_t2"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N005",
      "kind": "normal",
      "terminals": [
        "capacitor4.3_t2",
        "resistor22.6_t1",
        "terminal26.3_t1"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N006",
      "kind": "normal",
      "terminals": [
        "resistor22.1_t1",
        "signal_source23.1_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N007",
      "kind": "normal",
      "terminals": [
        "resistor22.2_t1",
        "resistor22.4_t1",
        "terminal26.1_t1"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N008",
      "kind": "normal",
      "terminals": [
        "resistor22.5_t2",
        "terminal26.2_t1"
      ],
      "terminal_count": 2
    }
  ],
  "terminal_to_node": {
    "capacitor4.1_t1": "N001",
    "capacitor4.1_t2": "N002",
    "capacitor4.2_t1": "N003",
    "capacitor4.2_t2": "0",
    "capacitor4.3_t1": "N004",
    "capacitor4.3_t2": "N005",
    "gnd9.1_t1": "0",
    "gnd9.2_t1": "0",
    "gnd9.3_t1": "0",
    "gnd9.4_t1": "0",
    "npn_transistor18.1_B": "N002",
    "npn_transistor18.1_C": "N004",
    "npn_transistor18.1_E": "N003",
    "resistor22.1_t1": "N006",
    "resistor22.1_t2": "N001",
    "resistor22.2_t1": "N007",
    "resistor22.2_t2": "N002",
    "resistor22.3_t1": "N002",
    "resistor22.3_t2": "0",
    "resistor22.4_t1": "N007",
    "resistor22.4_t2": "N004",
    "resistor22.5_t1": "N003",
    "resistor22.5_t2": "N008",
    "resistor22.6_t1": "N005",
    "resistor22.6_t2": "0",
    "signal_source23.1_t1": "N006",
    "signal_source23.1_t2": "0",
    "terminal26.1_t1": "N007",
    "terminal26.2_t1": "N008",
    "terminal26.3_t1": "N005"
  },
  "component_terminal_nodes": {
    "capacitor4.1": {
      "t1": "N001",
      "t2": "N002"
    },
    "capacitor4.2": {
      "t1": "N003",
      "t2": "0"
    },
    "capacitor4.3": {
      "t1": "N004",
      "t2": "N005"
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
    "npn_transistor18.1": {
      "B": "N002",
      "C": "N004",
      "E": "N003"
    },
    "resistor22.1": {
      "t1": "N006",
      "t2": "N001"
    },
    "resistor22.2": {
      "t1": "N007",
      "t2": "N002"
    },
    "resistor22.3": {
      "t1": "N002",
      "t2": "0"
    },
    "resistor22.4": {
      "t1": "N007",
      "t2": "N004"
    },
    "resistor22.5": {
      "t1": "N003",
      "t2": "N008"
    },
    "resistor22.6": {
      "t1": "N005",
      "t2": "0"
    },
    "signal_source23.1": {
      "t1": "N006",
      "t2": "0"
    },
    "terminal26.1": {
      "t1": "N007"
    },
    "terminal26.2": {
      "t1": "N008"
    },
    "terminal26.3": {
      "t1": "N005"
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
    "nodes_count": 9,
    "normal_nodes_count": 8,
    "ground_nodes_count": 1,
    "ground_groups_count": 4,
    "terminal_to_node_count": 30,
    "singleton_nodes_count": 0
  }
}
```

### values_bound

- Step: `04`
- Role: Values and labels bound to graph components.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a06\04_values_bound.json`

```json
{
  "circuit_id": "a06",
  "source_format": "pipeline2.0_values_bound",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\data\\batchPipeline2.0\\batchChatAgentEvaluation\\values\\a06_values.yaml",
  "supplies": {
    "VCC": {
      "terminal": "terminal26.1_t1",
      "value": 12,
      "unit": "V",
      "reference": 0,
      "type": "dc",
      "source": "manual_from_image_label",
      "label_text": "VCC 12 V",
      "node": "N007"
    },
    "VEE": {
      "terminal": "terminal26.2_t1",
      "value": 0,
      "unit": "V",
      "reference": 0,
      "type": "dc",
      "source": "manual_from_image_label",
      "label_text": "VEE 0 V",
      "node": "N008"
    }
  },
  "components": {
    "capacitor4.1": {
      "class_name": "Capacitor",
      "terminal_nodes": {
        "t1": "N001",
        "t2": "N002"
      },
      "value_data": {
        "value": 1,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "Cc1 1 uF"
      },
      "status": "bound"
    },
    "capacitor4.2": {
      "class_name": "Capacitor",
      "terminal_nodes": {
        "t1": "N003",
        "t2": "0"
      },
      "value_data": {
        "value": 100,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "CE 100 uF"
      },
      "status": "bound"
    },
    "capacitor4.3": {
      "class_name": "Capacitor",
      "terminal_nodes": {
        "t1": "N004",
        "t2": "N005"
      },
      "value_data": {
        "value": 10,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "Cc2 10 uF"
      },
      "status": "bound"
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
    "npn_transistor18.1": {
      "class_name": "NPN_Transistor",
      "terminal_nodes": {
        "B": "N002",
        "C": "N004",
        "E": "N003"
      },
      "value_data": {
        "model": "2N2222",
        "source": "manual_assumption",
        "label_text": "NPN transistor"
      },
      "status": "bound"
    },
    "resistor22.1": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N006",
        "t2": "N001"
      },
      "value_data": {
        "value": 1,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "Rs 1 kOhm"
      },
      "status": "bound"
    },
    "resistor22.2": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N007",
        "t2": "N002"
      },
      "value_data": {
        "value": 100,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "100 kOhm"
      },
      "status": "bound"
    },
    "resistor22.3": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N002",
        "t2": "0"
      },
      "value_data": {
        "value": 47,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "47 kOhm"
      },
      "status": "bound"
    },
    "resistor22.4": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N007",
        "t2": "N004"
      },
      "value_data": {
        "value": 6.8,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "6.8 kOhm"
      },
      "status": "bound"
    },
    "resistor22.5": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N003",
        "t2": "N008"
      },
      "value_data": {
        "value": 3.9,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "3.9 kOhm"
      },
      "status": "bound"
    },
    "resistor22.6": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N005",
        "t2": "0"
      },
      "value_data": {
        "value": 10,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "RL 10 kOhm"
      },
      "status": "bound"
    },
    "signal_source23.1": {
      "class_name": "Signal_Source",
      "terminal_nodes": {
        "t1": "N006",
        "t2": "0"
      },
      "value_data": {
        "type": "sin",
        "waveform": "sin",
        "value": 1,
        "unit": "V",
        "offset": 0,
        "amplitude": 1,
        "frequency": 100,
        "frequency_unit": "Hz",
        "source": "manual_from_image_label",
        "label_text": "vs AC 1",
        "note": "Frequency not shown in the image; 100 Hz is assumed for transient simulation."
      },
      "status": "bound"
    },
    "terminal26.1": {
      "class_name": "Terminal",
      "terminal_nodes": {
        "t1": "N007"
      },
      "value_data": null,
      "status": "not_required"
    },
    "terminal26.2": {
      "class_name": "Terminal",
      "terminal_nodes": {
        "t1": "N008"
      },
      "value_data": null,
      "status": "not_required"
    },
    "terminal26.3": {
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
      "spice_node": 0,
      "source": "graph_json_gnd",
      "node": "0"
    },
    "signal_source23.1_t1": {
      "label": "VS",
      "source": "manual_from_image_label",
      "label_text": "vs AC 1",
      "node": "N006"
    },
    "terminal26.1_t1": {
      "label": "VCC",
      "source": "manual_from_image_label",
      "label_text": "VCC 12 V",
      "node": "N007"
    },
    "terminal26.2_t1": {
      "label": "VEE",
      "spice_node": 0,
      "source": "manual_from_image_label",
      "label_text": "VEE 0 V",
      "node": "N008"
    },
    "terminal26.3_t1": {
      "label": "VOUT",
      "source": "manual_from_image_label",
      "label_text": "vo",
      "node": "N005"
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
      "stop": "50ms"
    }
  },
  "missing": [],
  "stats": {
    "components_total": 18,
    "bound_components": 11,
    "missing_components": 0,
    "not_required_components": 7,
    "unsupported_components": 0,
    "supplies_count": 2,
    "manual_nodes_count": 5
  }
}
```

### component_rules

- Step: `06`
- Role: SPICE conversion rules for each component.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a06\06_component_rules.json`

```json
{
  "circuit_id": "a06",
  "source_format": "pipeline2.0_component_rules",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\data\\batchPipeline2.0\\batchChatAgentEvaluation\\values\\a06_values.yaml",
  "spice_classes_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_spice_classes.yaml",
  "supplies": {
    "VCC": {
      "status": "spice_ready",
      "spice_prefix": "V",
      "emit_as": "independent_voltage_source",
      "nodes": [
        "N007",
        "0"
      ],
      "parameters": {
        "terminal": "terminal26.1_t1",
        "value": 12,
        "unit": "V",
        "reference": 0,
        "type": "dc",
        "source": "manual_from_image_label",
        "label_text": "VCC 12 V",
        "node": "N007"
      }
    },
    "VEE": {
      "status": "spice_ready",
      "spice_prefix": "V",
      "emit_as": "independent_voltage_source",
      "nodes": [
        "N008",
        "0"
      ],
      "parameters": {
        "terminal": "terminal26.2_t1",
        "value": 0,
        "unit": "V",
        "reference": 0,
        "type": "dc",
        "source": "manual_from_image_label",
        "label_text": "VEE 0 V",
        "node": "N008"
      }
    }
  },
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
        "N002"
      ],
      "parameters": {
        "value": 1,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "Cc1 1 uF"
      }
    },
    "capacitor4.2": {
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
        "N003",
        "0"
      ],
      "parameters": {
        "value": 100,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "CE 100 uF"
      }
    },
    "capacitor4.3": {
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
        "N004",
        "N005"
      ],
      "parameters": {
        "value": 10,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "Cc2 10 uF"
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
        "N004",
        "N002",
        "N003"
      ],
      "parameters": {
        "model": "2N2222",
        "source": "manual_assumption",
        "label_text": "NPN transistor"
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
        "N001"
      ],
      "parameters": {
        "value": 1,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "Rs 1 kOhm"
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
        "N002"
      ],
      "parameters": {
        "value": 100,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "100 kOhm"
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
        "0"
      ],
      "parameters": {
        "value": 47,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "47 kOhm"
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
        "N004"
      ],
      "parameters": {
        "value": 6.8,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "6.8 kOhm"
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
        "N003",
        "N008"
      ],
      "parameters": {
        "value": 3.9,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "3.9 kOhm"
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
        "N005",
        "0"
      ],
      "parameters": {
        "value": 10,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "RL 10 kOhm"
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
        "N006",
        "0"
      ],
      "parameters": {
        "type": "sin",
        "waveform": "sin",
        "value": 1,
        "unit": "V",
        "offset": 0,
        "amplitude": 1,
        "frequency": 100,
        "frequency_unit": "Hz",
        "source": "manual_from_image_label",
        "label_text": "vs AC 1",
        "note": "Frequency not shown in the image; 100 Hz is assumed for transient simulation."
      }
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
      "step": "0.1ms",
      "stop": "50ms"
    }
  },
  "stats": {
    "components_total": 18,
    "spice_ready_components": 11,
    "not_emitted_components": 7,
    "measurement_components": 0,
    "missing_components": 0,
    "unsupported_components": 0,
    "pin_aware_components": 0,
    "invalid_components": 0,
    "supplies_ready_count": 2
  }
}
```

### netlist

- Step: `07`
- Role: Generated SPICE netlist.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a06\07_netlist.cir`

```spice
* pipeline2.0 netlist
* circuit: a06

VVCC N007 0 DC 12
VVEE N008 0 DC 0
Ccapacitor4_1 N001 N002 1u
Ccapacitor4_2 N003 0 100u
Ccapacitor4_3 N004 N005 10u
Qnpn_transistor18_1 N004 N002 N003 2N2222
Rresistor22_1 N006 N001 1k
Rresistor22_2 N007 N002 100k
Rresistor22_3 N002 0 47k
Rresistor22_4 N007 N004 6.8k
Rresistor22_5 N003 N008 3.9k
Rresistor22_6 N005 0 10k
Vsignal_source23_1 N006 0 SIN(0 1 100)

.model 2N2222 NPN(IS=14.34f BF=255.9 VAF=74.03 IKF=0.2847 ISE=14.34f NE=1.307 BR=6.092 NR=1.005 VAR=11.96 IKR=0.0 ISC=0.0 NC=2 RB=10 RC=1 RE=0.1 CJE=22.01p VJE=0.75 MJE=0.377 CJC=7.306p VJC=0.75 MJC=0.3416 TF=411.1p TR=46.91n)

.op
.save all
.tran 0.1ms 50ms

.control
set wr_singlescale
set wr_vecnames
run
wrdata 08_tran.csv time v(N001) v(N002) v(N003) v(N004) v(N005) v(N006) v(N007) v(N008)
.endc
.end

```

### spice_emit_report

- Step: `07`
- Role: Report of emitted, skipped and warning components.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a06\07_spice_emit_report.json`

```json
{
  "circuit_id": "a06",
  "source_format": "pipeline2.0_spice_emit_report",
  "emitted_elements": 13,
  "skipped_elements": 7,
  "skipped_components": [
    "gnd9.1",
    "gnd9.2",
    "gnd9.3",
    "gnd9.4",
    "terminal26.1",
    "terminal26.2",
    "terminal26.3"
  ],
  "informational_skips": [
    "gnd9.1: structural component not emitted",
    "gnd9.2: structural component not emitted",
    "gnd9.3: structural component not emitted",
    "gnd9.4: structural component not emitted",
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
      "N008"
    ],
    "device_currents": []
  },
  "models": [
    "2N2222"
  ],
  "warnings": []
}
```

### spice_run

- Step: `08`
- Role: Structured ngspice execution report.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a06\08_spice_run.json`

```json
{
  "source_format": "pipeline2.0_spice_run",
  "status": "success",
  "netlist_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\a06\\07_netlist.cir",
  "command": [
    "C:\\Users\\m.profilo\\Spice64\\bin\\ngspice_con.exe",
    "-b",
    "07_netlist.cir"
  ],
  "exit_code": 0,
  "stdout_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\a06\\08_ngspice_stdout.txt",
  "stderr_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\a06\\08_ngspice_stderr.txt",
  "tran_raw_csv_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\a06\\08_tran_raw.csv",
  "tran_csv_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\a06\\08_tran.csv",
  "tran_plot_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\a06\\08_tran_plot.png",
  "tran_plot_png_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\a06\\08_tran_plot.png",
  "tran_plot_svg_path": null,
  "message": "ngspice completed successfully."
}
```

### ngspice_stdout

- Step: `08`
- Role: Raw ngspice stdout log.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a06\08_ngspice_stdout.txt`

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
n007                                        12
n008                                         0
n001                                         0
n002                                     3.664
n003                                   3.02446
n004                                   6.76332
n005                                         0
n006                                         0
vsignal_source23_1#branch                    0
vvee#branch                        0.000775502
vvcc#branch                        -0.00085346


No. of Data Rows : 513
Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

No. of Data Rows : 1

Initial Transient Solution
--------------------------

Node                                   Voltage
----                                   -------
n007                                        12
n008                                         0
n001                                         0
n002                                     3.664
n003                                   3.02446
n004                                   6.76332
n005                                         0
n006                                         0
vsignal_source23_1#branch                    0
vvee#branch                        0.000775502
vvcc#branch                        -0.00085346


No. of Data Rows : 513
	Node                                  Voltage
	----                                  -------
	----	-------
	n006                             0.000000e+00
	n005                             0.000000e+00
	n004                             6.763323e+00
	n003                             3.024458e+00
	n002                             3.664000e+00
	n001                             0.000000e+00
	n008                             0.000000e+00
	n007                             1.200000e+01

	Source	Current
	------	-------

	vvcc#branch                      -8.53460e-04
	vvee#branch                      7.755021e-04
	vsignal_source23_1#branch        0.000000e+00

 BJT models (Bipolar Junction Transistor)
      model                2n2222

       type                   npn
       tnom                    27
         is             1.434e-14
        ibe                     0
        ibc                     0
         bf                 255.9
         nf                     1
        vaf                 74.03
        ikf                0.2847
        ise             1.434e-14
         ne                 1.307
         br                 6.092
         nr                 1.005
        var                 11.96
        ikr                     0
        isc                     0
         nc                     2
         rb                    10
        irb                     0
        rbm                    10
         re                   0.1
         rc                     1
        cje             2.201e-11
        vje                  0.75
        mje                 0.377
         tf             4.111e-10
        xtf                     0
        vtf                     0
        itf                     0
        ptf                     0
        cjc             7.306e-12
        vjc                  0.75
        mjc                0.3416
       xcjc                     1
         tr             4.691e-08
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
      model                2n2222
         ic           5.22697e-07
         ib          -4.41586e-07
         ie           -8.1121e-08
        vbe              0.117031
        vbc              -7.10683
         gm           5.54364e-11
        gpi           9.29591e-07
        gmu           1.29741e-07
         gx                   0.1
         go           1.78726e-14
        cpi           2.34637e-11
        cmu            3.2748e-12
        cbx                     0
       csub                     0

 Capacitor: Fixed capacitor
     device         ccapacitor4_3         ccapacitor4_2         ccapacitor4_1
      model                     C                     C                     C
capacitance                 1e-05                0.0001                 1e-06
      dtemp                     0                     0                     0
     bv_max                 1e+99                 1e+99                 1e+99
          i           0.000276985          -0.000740712          -2.64208e-05
          p            0.00203393           -0.00213998           7.87259e-05

 Resistor: Simple linear resistor
     device         rresistor22_6         rresistor22_5         rresistor22_4
      model                     R                     R                     R
 resistance                 10000                  3900                  6800
         ac                 10000                  3900                  6800
      dtemp                     0                     0                     0
     bv_max                 1e+99                 1e+99                 1e+99
      noisy                     1                     1                     1
          i           0.000276985           0.000740793           0.000277508
          p           0.000767207            0.00214022           0.000523672

 Resistor: Simple linear resistor
     device         rresistor22_3         rresistor22_2         rresistor22_1
      model                     R                     R                     R
 resistance                 47000                100000                  1000
         ac                 47000                100000                  1000
      dtemp                     0                     0                     0
     bv_max                 1e+99                 1e+99                 1e+99
      noisy                     1                     1                     1
          i           6.39599e-05           8.99388e-05          -2.64208e-05
          p           0.000192271           0.000808899           6.98057e-07

 Vsource: Independent voltage source
     device    vsignal_source23_1                  vvee                  vvcc
         dc                     0                     0                    12
      acmag                     0                     0                     0
      pulse                     0         -         -
                                1                    
                              100                    
        sin                     0         -         -
                                1                    
                              100                    
        exp                     0         -         -
                                1                    
                              100                    
        pwl                     0         -         -
                                1                    
                              100                    
       sffm                     0         -         -
                                1                    
                              100                    
         am                     0         -         -
                                1                    
                              100                    
    trnoise                     0         -         -
                                1                    
                              100                    
   trrandom                     0         -         -
                                1                    
                              100                    
    portnum                     0                     0                     0
```

> Artifact truncated in this preview. The original file remains available through the manifest path.

### ngspice_stderr

- Step: `08`
- Role: Raw ngspice stderr log.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a06\08_ngspice_stderr.txt`

```text

```

### tran_csv

- Step: `08`
- Role: Clean transient CSV, when .tran data is available.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\a06\08_tran.csv`

```csv
time,v(N001),v(N002),v(N003),v(N004),v(N005),v(N006),v(N007),v(N008)
0.0,0.0,3.66400021,3.02445816,6.76332305,0.0,0.0,12.0,0.0
1e-06,0.00036081169,3.66436076,3.02445826,6.72267119,-0.040651451,0.000628318489,12.0,0.0
2e-06,0.00082480557,3.66482432,3.0244585,6.66883839,-0.0944833077,0.00125663673,12.0,0.0
4e-06,0.00180985222,3.66580823,3.02445927,6.5513011,-0.212017535,0.00251327148,12.0,0.0
8e-06,0.00383800229,3.6678326,3.02446265,6.29629448,-0.467010575,0.00502652708,12.0,0.0
1.6e-05,0.00778510105,3.67176587,3.02447742,5.74893213,-1.01431367,0.0100529272,12.0,0.0
3.2e-05,0.0153806208,3.67930545,3.02454302,4.48385839,-2.27912393,0.0201048383,12.0,0.0
5.54392356e-05,0.0226787218,3.68640582,3.02471601,3.13071395,-3.63157567,0.0348264552,12.0,0.0
7.22382873e-05,0.0242267318,3.68767418,3.02486997,3.10383406,-3.65784328,0.0453730717,12.0,0.0
8.86174268e-05,0.0257151811,3.68874429,3.02502233,3.09082567,-3.67025153,0.0556512055,12.0,0.0
0.000109827468,0.0278691171,3.69014507,3.02522226,3.08259928,-3.67769867,0.0689518791,12.0,0.0
0.000152247551,0.0325117139,3.69258001,3.02562992,3.07367616,-3.68506014,0.0955141294,12.0,0.0
0.000224257162,0.0421851204,3.69644741,3.02634384,3.06413569,-3.69194453,0.140439134,12.0,0.0
0.000324257162,0.0588574664,3.70103342,3.02737676,3.05812111,-3.69426601,0.202330232,12.0,0.0
0.000424257162,0.0792817747,3.70507704,3.02845297,3.05493645,-3.69375666,0.263422825,12.0,0.0
0.000524257162,0.103094839,3.708664,3.02956751,3.05296401,-3.6920362,0.323475808,12.0,0.0
0.000624257162,0.129890834,3.71182288,3.03071572,3.05234014,-3.68896957,0.38225218,12.0,0.0
0.000724257162,0.159312307,3.7146159,3.03189317,3.05221344,-3.68540908,0.439519977,12.0,0.0
0.000824257162,0.191103022,3.71719872,3.03309565,3.05236769,-3.68157134,0.49505319,12.0,0.0
0.000924257162,0.224784684,3.71949048,3.03431912,3.05287091,-3.67738864,0.548632654,12.0,0.0
0.00102425716,0.260104856,3.72162115,3.03555969,3.05351334,-3.67307098,0.600046916,12.0,0.0
0.00112425716,0.296613858,3.72350909,3.03681364,3.05438269,-3.66853083,0.649093066,12.0,0.0
0.00122425716,0.334067361,3.72526312,3.0380774,3.05533362,-3.66391368,0.695577543,12.0,0.0
0.00132425716,0.372045916,3.72680262,3.03934755,3.05645069,-3.65913509,0.739316893,12.0,0.0
0.00142425716,0.410321133,3.72822342,3.04062085,3.05762055,-3.6543085,0.780138497,12.0,0.0
0.00152425716,0.448503196,3.72944571,3.04189415,3.05892596,-3.64935126,0.817881251,12.0,0.0
0.00162425716,0.486384138,3.73055715,3.0431645,3.06027085,-3.64435951,0.852396201,12.0,0.0
0.00172425716,0.523602871,3.73147806,3.04442906,3.06173896,-3.6392496,0.883547133,12.0,0.0
0.00182425716,0.55997484,3.73229101,3.04568516,3.0632442,-3.63410768,0.911211108,12.0,0.0
0.00192425716,0.595166769,3.73291551,3.04693024,3.064875,-3.62884541,0.935278948,12.0,0.0
0.00202425716,0.629019815,3.73343116,3.04816191,3.0665515,-3.62354271,0.955655671,12.0,0.0
0.00212425716,0.66122762,3.73375551,3.04937793,3.06837212,-3.61810126,0.972260856,12.0,0.0
0.00222425716,0.691659015,3.73396674,3.05057617,3.07026199,-3.61259605,0.985028973,12.0,0.0
0.00232425716,0.720033561,3.73397899,3.05175468,3.07233811,-3.60691018,0.99390963,12.0,0.0
0.00242425716,0.746249529,3.73387024,3.05291162,3.07453295,-3.60111133,0.99886778,12.0,0.0
0.00252425716,0.770051073,3.73354923,3.05404532,3.07699864,-3.59504756,0.999883855,12.0,0.0
0.00262425716,0.791367478,3.73309468,3.05515424,3.0796862,-3.58876809,0.996953845,12.0,0.0
0.00272425716,0.809965488,3.73240718,3.05623695,3.08282122,-3.58204766,0.990089314,12.0,0.0
0.00282425716,0.825806634,3.7315666,3.05729219,3.08641492,-3.5748755,0.979317353,12.0,0.0
0.00292425716,0.838676848,3.73046109,3.05831878,3.09088098,-3.56683858,0.964680473,12.0,0.0
0.00302425716,0.848570177,3.72917093,3.05931563,3.09647397,-3.55768333,0.946236441,12.0,0.0
0.00312425716,0.85518605,3.72745989,3.06028146,3.1062031,-3.54440316,0.924058045,12.0,0.0
0.00322425716,0.858720424,3.72557504,3.06121463,3.12104725,-3.5260238,0.898232815,12.0,0.0
0.00332425716,0.858718676,3.72309048,3.06210798,3.18666262,-3.45691696,0.86886267,12.0,0.0
0.00342425716,0.835951459,3.69981046,3.06250727,6.96099803,0.318987416,0.836063521,12.0,0.0
0.00352425716,0.803189301,3.66720392,3.06218494,8.98116504,2.33782602,0.799964811,12.0,0.0
0.00362425716,0.767108628,3.63160445,3.06153385,9.60728884,2.96130026,0.760709006,12.0,0.0
0.00372425716,0.725556375,3.59072745,3.06078277,9.78826666,3.13922782,0.718451029,12.0,0.0
0.00382425716,0.682811106,3.54881012,3.06000523,9.82377543,3.17158119,0.673357655,12.0,0.0
0.00392425716,0.635597685,3.50256891,3.05922214,9.83685495,3.18148417,0.625606846,12.0,0.0
0.00402425716,0.587786065,3.45587679,3.05843786,9.83742583,3.17887487,0.575387052,12.0,0.0
0.00412425716,0.535941358,3.40530427,3.05765353,9.84138435,3.17965412,0.522896468,12.0,0.0
0.00422425716,0.483900674,3.35469376,3.05686957,9.8387359,3.17382894,0.468342251,12.0,0.0
0.00432425716,0.428258215,3.30064514,3.05608584,9.84369345,3.17561176,0.411939701,12.0,0.0
0.00442425716,0.372836438,3.24698554,3.05530231,9.84126922,3.17001472,0.353911414,12.0,0.0
0.00452425716,0.314255915,3.19033975,3.05451898,9.84625196,3.17182654,0.294486399,12.0,0.0
0.00462425716,0.256339354,3.13453367,3.05373586,9.84383685,3.1662424,0.233899182,12.0,0.0
0.00472425716,0.195728819,3.07621214,3.05295294,9.84881385,3.16805225,0.172388871,12.0,0.0
0.00482425716,0.136243751,3.01919635,3.05217022,9.84640235,3.16247548,0.11019822,12.0,0.0
0.00492425716,0.0745434914,2.96014691,3.0513877,9.85137295,3.16428271,0.0475726666,12.0,0.0
0.00502425716,0.0144409126,2.90287695,3.05060538,9.84896492,3.15871317,-0.0152406341,12.0,0.0
0.00512425716,-0.0473915206,2.8440587,3.04982326,9.85392915,3.1605178,-0.0779937869,12.0,0.0
0.00522425716,-0.10715092,2.78749383,3.04904134,9.85152455,3.15495545,-0.140439134,12.0,0.0
0.00532425716,-0.168155828,2.72986205,3.04825963,9.85648245,3.1567575,-0.202330232,12.0,0.0
0.00542425716,-0.226616816,2.67495008,3.04747811,9.85408124,3.15120231,-0.263422825,12.0,0.0
0.00552425716,-0.285847491,2.61944112,3.0466968,9.85903285,3.15300181,-0.323475808,12.0,0.0
0.00562425716,-0.342075355,2.56710352,3.04591568,9.856635,3.14745374,-0.38225218,12.0,0.0
0.00572425716,-0.398613012,2.51462005,3.04513477,9.86158033,3.14925072,-0.439519977,12.0,0.0
0.00582425716,-0.451708296,2.46573736,3.04435406,9.85918582,3.14370972,-0.49505319,12.0,0.0
0.00592425716,-0.50467657,2.41713413,3.04357355,9.8641249,3.1455042,-0.548632654,12.0,0.0
0.00602425716,-0.553789258,2.37253213,3.04279323,9.86173369,3.13997025,-0.600046916,12.0,0.0
0.00612425716,-0.602368019,2.32860251,3.04201312,9.86666655,3.14176224,-0.649093066,12.0,0.0
0.00622425716,-0.646710942,2.28903917,3.04123321,9.86427861,3.1362353,-0.695577543,12.0,0.0
0.00632425716,-0.690149237,2.25050258,3.0404535,9.86920527,3.13802483,-0.739316893,12.0,0.0
0.00642425716,-0.72901048,2.21665612,3.03967399,9.86682057,3.13250487,-0.780138497,12.0,0.0
0.00652425716,-0.766638374,2.18414678,3.03889469,9.87174105,3.13429195,-0.817881251,12.0,0.0
0.00662425716,-0.799392508,2.15660497,3.03811558,9.86935957,3.12877894,-0.852396201,12.0,0.0
0.00672425716,-0.830631651,2.13066179,3.03733667,9.87427388,3.13056357,-0.883547133,12.0,0.0
0.00682425716,-0.856749592,2.10991269,3.03655796,9.87189559,3.12505748,-0.911211108,12.0,0.0
0.00692425716,-0.881122341,2.09097085,3.03577945,9.87680375,3.12683969,-0.935278948,12.0,0.0
0.00702425716,-0.900179693,2.07739513,3.03500115,9.87442864,3.12134049,-0.955655671,12.0,0.0
0.00712425716,-0.917316645,2.06577919,3.03422304,9.87933065,3.12312027,-0.972260856,12.0,0.0
0.00722425716,-0.929000397,2.05964407,3.03344513,9.8769587,3.11762794,-0.985028973,12.0,0.0
0.00732425716,-0.938646214,2.05556286,3.03266742,9.88185457,3.1194053,-0.99390963,12.0,0.0
0.00742425716,-0.94275967,2.05701798,3.03188992,9.87948576,3.11391983,-0.99886778,12.0,0.0
0.00752425716,-0.944777109,2.06056128,3.03111261,9.8843755,3.11569475,-0.999883855,12.0,0.0
0.00762425716,-0.941242994,2.06963628,3.0303355,9.88200982,3.11021612,-0.996953845,12.0,0.0
0.00772425716,-0.935615069,2.08077346,3.0295586,9.88689342,3.11198862,-0.990089314,12.0,0.0
0.00782425716,-0.924476746,2.09737752,3.02878189,9.88453086,3.10651681,-0.979317353,12.0,0.0
0.00792425716,-0.911306996,2.11595798,3.02800538,9.88940832,3.10828687,-0.964680473,12.0,0.0
0.00802425716,-0.892727783,2.13988129,3.02722907,9.88704888,3.10282187,-0.946236441,12.0,0.0
0.00812425716,-0.872238641,2.16563684,3.02645296,9.8919202,3.10458949,-0.924058045,12.0,0.0
0.00822425716,-0.846499236,2.19655389,3.02567705,9.88956387,3.09913129,-0.898232815,12.0,0.0
0.00832425716,-0.819028518,2.229103,3.02490134,9.89442904,3.10089645,-0.86886267,12.0,0.0
0.00842425716,-0.786522569,2.2665777,3.02412583,9.89207582,3.09544506,-0.836063521,12.0,0.0
0.00852425716,-0.752518149,2.3054315,3.02335052,9.89693483,3.09720775,-0.799964811,12.0,0.0
0.00862425716,-0.713746054,2.34892408,3.02257541,9.89458472,3.09176315,-0.760709006,12.0,0.0
0.00872425716,-0.673758797,2.3934941,3.0218005,9.89943757,3.09352335,-0.718451029,12.0,0.0
0.00882425716,-0.629319805,2.44236959,3.02102579,9.89709057,3.08808555,-0.673357655,12.0,0.0
0.00892425716,-0.583994882,2.49197701,3.02025127,9.90193723,3.08984325,-0.625606846,12.0,0.0
0.00902425716,-0.534577649,2.54551531,3.01947696,9.89959336,3.08441224,-0.575387052,12.0,0.0
0.00912425716,-0.48464436,2.59940167,3.01870284,9.90443382,3.08616742,-0.522896468,12.0,0.0
0.00922425716,-0.431016088,2.65680886,3.01792893,9.90209308,3.08074322,-0.468342251,12.0,0.0
0.00932425716,-0.377276357,2.71414806,3.01715521,9.90692733,3.08249585,-0.411939701,12.0,0.0
0.00942425716,-0.320270701,2.77456892,3.01638169,9.90458973,3.07707847,-0.353911414,12.0,0.0
0.00952425716,-0.26358643,2.83448023,3.01560837,9.90941775,3.07882853,-0.294486399,12.0,0.0
0.00962425716,-0.204090347,2.89701175,3.01483525,9.90708331,3.07341797,-0.233899182,12.0,0.0
0.00972425716,-0.145369822,2.95857367,3.01406233,9.91190508,3.07516544,-0.172388871,12.0,0.0
0.00982425716,-0.0843095944,3.02227928,3.0132896,9.90957381,3.06976171,-0.11019822,12.0,0.0
0.00992425716,-0.024493156,3.08454413,3.01251708,9.91438931,3.07150658,-0.0475726666,12.0,0.0
0.0100242572,0.0371802105,3.14846845,3.01174475,9.91206123,3.06610969,0.0152406341,12.0,0.0
0.0101242572,0.0971349959,3.21047727,3.01097262,9.91687041,3.06785189,0.0779937869,12.0,0.0
0.0102242572,0.158460745,3.27366116,3.01020069,9.9145451,3.06246143,0.140439134,12.0,0.0
0.0103242572,0.217594111,3.3344588,3.00942896,9.91934294,3.06419594,0.202330232,12.0,0.0
0.0104242572,0.277616361,3.39595392,3.00865744,9.91696675,3.05875827,0.263422825,12.0,0.0
0.0105242572,0.334978238,3.4546006,3.00788619,9.92118105,3.05991323,0.323475808,12.0,0.0
0.0106242572,0.392703808,3.51342387,3.00711754,9.90028423,3.03596847,0.38225218,12.0,0.0
0.0107242572,0.44705516,3.56867456,3.00636974,9.75808322,2.89080408,0.439519977,12.0,0.0
0.0108242572,0.499685446,3.62191322,3.00578175,8.61982102,1.75022137,0.49505319,12.0,0.0
0.0109242572,0.542628895,3.6647881,3.0059485,3.69211258,-3.1767738,0.548632654,12.0,0.0
0.0110242572,0.553063901,3.67257376,3.00682652,3.06157808,-3.80381801,0.600046916,12.0,0.0
0.0111242572,0.564053835,3.67696258,3.00782276,3.04852617,-3.81306148,0.649093066,12.0,0.0
0.0112242572,0.578090388,3.68087282,3.00885592,3.04188425,-3.81588892,0.695577543,12.0,0.0
0.0113242572,0.594266759,3.68392233,3.00991933,3.04042602,-3.81353244,0.739316893,12.0,0.0
0.0114242572,0.612654642,3.68668351,3.01100736,3.03889498,-3.81125109,0.780138497,12.0,0.0
0.0115242572,0.632568935,3.68895799,3.012115,3.0386094,-3.80772717,0.817881251,12.0,0.0
0.0116242572,0.653824503,3.69101936,3.01323749,3.03856383,-3.8039669,0.852396201,12.0,0.0
0.0117242572,0.675817179,3.69269695,3.01437039,3.03912814,-3.79960081,0.883547133,12.0,0.0
0.0118242572,0.698360417,3.69421116,3.01550956,3.03981762,-3.79511397,0.911211108,12.0,0.0
0.0119242572,0.720906227,3.6953958,3.01665112,3.04093587,-3.79020306,0.935278948,12.0,0.0
0.0120242572,0.74329118,3.69644389,3.01779144,3.04213378,-3.
```

> Artifact truncated in this preview. The original file remains available through the manifest path.
