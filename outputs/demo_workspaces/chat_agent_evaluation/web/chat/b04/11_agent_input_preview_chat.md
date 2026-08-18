# Agent input preview

This file is a local preview of the evidence that will be provided to the read-only diagnostic agent.
The agent remains read-only: it can inspect base outputs and existing scenario artifacts, but it does not modify files.

## User problem

Ora che abbiamo provato 12 V, 10 V e 8 V, puoi dirmi cosa possiamo concludere sul comportamento del caricabatteria?

## Circuit

- Batch: `batchChatAgentEvaluation`
- Circuit: `b04`
- Agent mode: `graph_grounded_readonly`

## Technical summary

```json
{
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_message": "ngspice completed successfully.",
  "emitted_elements": 16,
  "skipped_elements": 4,
  "emit_warnings_count": 0,
  "skipped_components_count": 4,
  "node_count": 13,
  "ground_groups_count": 0,
  "singleton_nodes_count": 0,
  "bound_components": 14,
  "missing_components": 0,
  "unsupported_components": 0,
  "spice_ready_components": 14,
  "rules_missing_components": 0,
  "has_tran_csv": true,
  "has_tran_plot": true,
  "led_profiles": {}
}
```

## Image policy

- Included by default: `False`
- Can be requested: `True`
- Path: `outputs\demo_workspaces\chat_agent_evaluation\input\images\b04.jpg`
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
  "best_outcome_status": "partially_resolved",
  "best_stop_automation": false,
  "ranking_status": "verified_best",
  "interpretation_rule": "If a user asks which scenario resolves the problem, prefer the scenario with outcome_status='resolved_candidate' and stop_automation=true. Partially resolved scenarios without verified expectations are supporting diagnostics and must not be ranked only by changed_count.",
  "scenarios": [
    {
      "scenario_id": "scenario_4",
      "title": "Abbassare la batteria di prova e osservare D4 nel tempo",
      "status": "spice_success",
      "spice_status": "success",
      "outcome_status": "partially_resolved",
      "outcome_label": "Criteri verificati solo in parte",
      "outcome_technical_label": "Partially resolved",
      "outcome_reason": "Solo una parte dei comportamenti attesi dichiarati dallo scenario e stata verificata.",
      "stop_automation": false,
      "comparison_summary": {
        "requested_count": 3,
        "changed_count": 2,
        "activated_count": 0,
        "missing_count": 0,
        "expected_count": 2,
        "expectations_met_count": 1,
        "expectations_failed_count": 1,
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
          "v(N004)",
          "@ddiode7_4[id]"
        ],
        "unchanged": [
          "v(N009)"
        ],
        "missing": []
      },
      "led_profiles": {},
      "ranking_verified": true,
      "score": 25
    },
    {
      "scenario_id": "scenario_5",
      "title": "Portare la batteria di prova a un valore ancora piu basso",
      "status": "spice_success",
      "spice_status": "success",
      "outcome_status": "partially_resolved",
      "outcome_label": "Criteri verificati solo in parte",
      "outcome_technical_label": "Partially resolved",
      "outcome_reason": "Solo una parte dei comportamenti attesi dichiarati dallo scenario e stata verificata.",
      "stop_automation": false,
      "comparison_summary": {
        "requested_count": 3,
        "changed_count": 2,
        "activated_count": 0,
        "missing_count": 0,
        "expected_count": 2,
        "expectations_met_count": 1,
        "expectations_failed_count": 1,
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
          "v(N004)",
          "@ddiode7_4[id]"
        ],
        "unchanged": [
          "v(N009)"
        ],
        "missing": []
      },
      "led_profiles": {},
      "ranking_verified": true,
      "score": 25
    }
  ]
}
```


## Executed scenarios

### scenario_4

- Title: `Abbassare la batteria di prova e osservare D4 nel tempo`
- Status: `spice_success`
- SPICE status: `success`
- Outcome: `partially_resolved`
- Stop automation: `False`
- Comparison: `2/3` changed
- LED profiles: `{}`

#### scenario_definition

- Role: Scenario selected by the user and saved before execution.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b04\scenarios\scenario_4\scenario.json`

```json
{
  "scenario_id": "scenario_4",
  "title": "Abbassare la batteria di prova e osservare D4 nel tempo",
  "hypothesis": "Reducing VVBAT_TEST below the nominal 12 V changes the transient current through Ddiode7_4.",
  "intent": "diagnostic",
  "actions": [
    {
      "type": "change_source_value",
      "target": "VVBAT_TEST",
      "value": "DC 10V"
    }
  ],
  "rerun_from": "07",
  "analysis": "tran",
  "compare": [
    "v(N009)",
    "v(N004)",
    "@ddiode7_4[id]"
  ],
  "expect": {
    "v(N009)": "decreased",
    "@ddiode7_4[id]": "changed"
  },
  "measure": {
    "@ddiode7_4[id]": "tran_abs_peak"
  }
}
```

#### scenario_status

- Role: Current scenario status, SPICE status and diagnostic outcome.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b04\scenarios\scenario_4\scenario_status.json`

```json
{
  "status": "spice_success",
  "stage": "scenario_spice_executed",
  "scenario_id": "scenario_4",
  "source": "guided_chat",
  "spice_executed": true,
  "created_or_updated_at": "2026-07-24T11:33:51",
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b04\\scenarios\\scenario_4\\run\\08_spice_run.json",
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b04\\scenarios\\scenario_4\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 3,
    "changed_count": 2,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 2,
    "expectations_met_count": 1,
    "expectations_failed_count": 1,
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
    "technical_label": "Partially resolved",
    "label": "Criteri verificati solo in parte",
    "reason": "Solo una parte dei comportamenti attesi dichiarati dallo scenario e stata verificata.",
    "user_message": "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato.",
    "stop_automation": false,
    "confidence": "low",
    "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
  },
  "controlled_scenario_report": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b04\\scenarios\\scenario_4\\12_controlled_scenarios.json",
  "executed_scenarios_count": 1,
  "scenario_budget_exhausted": false,
  "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
}
```

#### controlled_scenario_report

- Role: Report produced by the controlled scenario runner.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b04\scenarios\scenario_4\12_controlled_scenarios.json`

```json
{
  "source_format": "pipeline2.0_controlled_scenario_report",
  "status": "spice_success",
  "scenario_id": "scenario_4",
  "scenario_title": "Abbassare la batteria di prova e osservare D4 nel tempo",
  "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b04\\scenarios\\scenario_4",
  "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b04\\scenarios\\scenario_4\\run",
  "netlist": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b04\\scenarios\\scenario_4\\run\\07_netlist.cir",
  "applied_actions": [
    {
      "status": "applied",
      "type": "change_source_value",
      "target": "VVBAT_TEST",
      "resolved_source_name": "VVBAT_TEST",
      "tried_source_names": [
        "VVBAT_TEST"
      ],
      "value": "DC 10V",
      "normalized_source_definition": "DC 10",
      "old_line": "VVBAT_TEST N009 0 DC 12",
      "new_line": "VVBAT_TEST N009 0 DC 10",
      "operation": "updated",
      "spice_executed": false,
      "index": 1
    }
  ],
  "unsupported_actions": [],
  "failed_actions": [],
  "spice_executed": true,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b04\\scenarios\\scenario_4\\run\\08_spice_run.json",
  "spice_status": "success",
  "spice_exit_code": 0,
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b04\\scenarios\\scenario_4\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 3,
    "changed_count": 2,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 2,
    "expectations_met_count": 1,
    "expectations_failed_count": 1,
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
    "technical_label": "Partially resolved",
    "label": "Criteri verificati solo in parte",
    "reason": "Solo una parte dei comportamenti attesi dichiarati dallo scenario e stata verificata.",
    "user_message": "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato.",
    "stop_automation": false,
    "confidence": "low",
    "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
  },
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "created_or_updated_at": "2026-07-24T11:33:51"
}
```

#### scenario_comparison

- Role: Base-vs-scenario comparison used to evaluate the scenario.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b04\scenarios\scenario_4\scenario_comparison.json`

```json
{
  "source_format": "pipeline2.0_scenario_comparison",
  "scenario_id": "scenario_4",
  "scenario_title": "Abbassare la batteria di prova e osservare D4 nel tempo",
  "scenario_intent": "diagnostic",
  "base_output_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b04",
  "scenario_run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b04\\scenarios\\scenario_4\\run",
  "base_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b04\\08_ngspice_stdout.txt",
  "scenario_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b04\\scenarios\\scenario_4\\run\\08_ngspice_stdout.txt",
  "base_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b04\\08_ngspice_stderr.txt",
  "scenario_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b04\\scenarios\\scenario_4\\run\\08_ngspice_stderr.txt",
  "quantities": [
    {
      "quantity": "v(N009)",
      "base_value": 0.0,
      "scenario_value": 0.0,
      "delta": 0.0,
      "change": "unchanged",
      "expectation": "decreased",
      "expectation_met": false,
      "relative_change": 0.0,
      "meaningful_improvement": false,
      "metric": "v(n009).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": 12.0,
        "max": 12.0,
        "mean": 12.0,
        "vpp": 0.0,
        "final": 12.0,
        "abs_peak": 12.0
      },
      "scenario_details": {
        "min": 10.0,
        "max": 10.0,
        "mean": 10.0,
        "vpp": 0.0,
        "final": 10.0,
        "abs_peak": 10.0
      }
    },
    {
      "quantity": "v(N004)",
      "base_value": 0.9987514999999991,
      "scenario_value": 2.9682211600000006,
      "delta": 1.9694696600000015,
      "change": "changed",
      "expectation": null,
      "expectation_met": null,
      "relative_change": 1.9719316166233574,
      "meaningful_improvement": false,
      "metric": "v(n004).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": 11.9875351,
        "max": 12.9862866,
        "mean": 12.155920647809523,
        "vpp": 0.9987514999999991,
        "final": 11.9875651,
        "abs_peak": 12.9862866
      },
      "scenario_details": {
        "min": 9.98950764,
        "max": 12.9577288,
        "mean": 10.650173785944391,
        "vpp": 2.9682211600000006,
        "final": 9.98971821,
        "abs_peak": 12.9577288
      }
    },
    {
      "quantity": "@ddiode7_4[id]",
      "base_value": 0.334752846,
      "scenario_value": 0.336066179,
      "delta": 0.0013133330000000276,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 0.003923291514002625,
      "meaningful_improvement": false,
      "metric": "@ddiode7_4[id].abs_peak",
      "measurement": "tran_abs_peak",
      "base_details": {
        "min": -8.0140838e-05,
        "max": 0.334752846,
        "mean": 0.06261003837421458,
        "vpp": 0.334832986838,
        "final": -4.25542834e-05,
        "abs_peak": 0.334752846
      },
      "scenario_details": {
        "min": -0.000174611517,
        "max": 0.336066179,
        "mean": 0.06783677617216666,
        "vpp": 0.336240790517,
        "final": 2.35739693e-05,
        "abs_peak": 0.336066179
      }
    }
  ],
  "summary": {
    "requested_count": 3,
    "changed_count": 2,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 2,
    "expectations_met_count": 1,
    "expectations_failed_count": 1,
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
    "technical_label": "Partially resolved",
    "label": "Criteri verificati solo in parte",
    "reason": "Solo una parte dei comportamenti attesi dichiarati dallo scenario e stata verificata.",
    "user_message": "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato.",
    "stop_automation": false,
    "confidence": "low",
    "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
  },
  "created_or_updated_at": "2026-07-24T11:33:51"
}
```

### scenario_5

- Title: `Portare la batteria di prova a un valore ancora piu basso`
- Status: `spice_success`
- SPICE status: `success`
- Outcome: `partially_resolved`
- Stop automation: `False`
- Comparison: `2/3` changed
- LED profiles: `{}`

#### scenario_definition

- Role: Scenario selected by the user and saved before execution.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b04\scenarios\scenario_5\scenario.json`

```json
{
  "scenario_id": "scenario_5",
  "title": "Portare la batteria di prova a un valore ancora piu basso",
  "hypothesis": "A lower VVBAT_TEST produces a different transient Ddiode7_4 current profile than the nominal case.",
  "intent": "diagnostic",
  "actions": [
    {
      "type": "change_source_value",
      "target": "VVBAT_TEST",
      "value": "DC 8V"
    }
  ],
  "rerun_from": "07",
  "analysis": "tran",
  "compare": [
    "v(N009)",
    "v(N004)",
    "@ddiode7_4[id]"
  ],
  "expect": {
    "v(N009)": "decreased",
    "@ddiode7_4[id]": "changed"
  },
  "measure": {
    "@ddiode7_4[id]": "tran_abs_peak"
  }
}
```

#### scenario_status

- Role: Current scenario status, SPICE status and diagnostic outcome.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b04\scenarios\scenario_5\scenario_status.json`

```json
{
  "status": "spice_success",
  "stage": "scenario_spice_executed",
  "scenario_id": "scenario_5",
  "source": "guided_chat",
  "spice_executed": true,
  "created_or_updated_at": "2026-07-24T11:35:44",
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b04\\scenarios\\scenario_5\\run\\08_spice_run.json",
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b04\\scenarios\\scenario_5\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 3,
    "changed_count": 2,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 2,
    "expectations_met_count": 1,
    "expectations_failed_count": 1,
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
    "technical_label": "Partially resolved",
    "label": "Criteri verificati solo in parte",
    "reason": "Solo una parte dei comportamenti attesi dichiarati dallo scenario e stata verificata.",
    "user_message": "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato.",
    "stop_automation": false,
    "confidence": "low",
    "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
  },
  "controlled_scenario_report": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b04\\scenarios\\scenario_5\\12_controlled_scenarios.json",
  "executed_scenarios_count": 2,
  "scenario_budget_exhausted": false,
  "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
}
```

#### controlled_scenario_report

- Role: Report produced by the controlled scenario runner.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b04\scenarios\scenario_5\12_controlled_scenarios.json`

```json
{
  "source_format": "pipeline2.0_controlled_scenario_report",
  "status": "spice_success",
  "scenario_id": "scenario_5",
  "scenario_title": "Portare la batteria di prova a un valore ancora piu basso",
  "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b04\\scenarios\\scenario_5",
  "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b04\\scenarios\\scenario_5\\run",
  "netlist": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b04\\scenarios\\scenario_5\\run\\07_netlist.cir",
  "applied_actions": [
    {
      "status": "applied",
      "type": "change_source_value",
      "target": "VVBAT_TEST",
      "resolved_source_name": "VVBAT_TEST",
      "tried_source_names": [
        "VVBAT_TEST"
      ],
      "value": "DC 8V",
      "normalized_source_definition": "DC 8",
      "old_line": "VVBAT_TEST N009 0 DC 12",
      "new_line": "VVBAT_TEST N009 0 DC 8",
      "operation": "updated",
      "spice_executed": false,
      "index": 1
    }
  ],
  "unsupported_actions": [],
  "failed_actions": [],
  "spice_executed": true,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b04\\scenarios\\scenario_5\\run\\08_spice_run.json",
  "spice_status": "success",
  "spice_exit_code": 0,
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b04\\scenarios\\scenario_5\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 3,
    "changed_count": 2,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 2,
    "expectations_met_count": 1,
    "expectations_failed_count": 1,
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
    "technical_label": "Partially resolved",
    "label": "Criteri verificati solo in parte",
    "reason": "Solo una parte dei comportamenti attesi dichiarati dallo scenario e stata verificata.",
    "user_message": "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato.",
    "stop_automation": false,
    "confidence": "low",
    "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
  },
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "created_or_updated_at": "2026-07-24T11:35:44"
}
```

#### scenario_comparison

- Role: Base-vs-scenario comparison used to evaluate the scenario.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b04\scenarios\scenario_5\scenario_comparison.json`

```json
{
  "source_format": "pipeline2.0_scenario_comparison",
  "scenario_id": "scenario_5",
  "scenario_title": "Portare la batteria di prova a un valore ancora piu basso",
  "scenario_intent": "diagnostic",
  "base_output_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b04",
  "scenario_run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b04\\scenarios\\scenario_5\\run",
  "base_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b04\\08_ngspice_stdout.txt",
  "scenario_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b04\\scenarios\\scenario_5\\run\\08_ngspice_stdout.txt",
  "base_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b04\\08_ngspice_stderr.txt",
  "scenario_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b04\\scenarios\\scenario_5\\run\\08_ngspice_stderr.txt",
  "quantities": [
    {
      "quantity": "v(N009)",
      "base_value": 0.0,
      "scenario_value": 0.0,
      "delta": 0.0,
      "change": "unchanged",
      "expectation": "decreased",
      "expectation_met": false,
      "relative_change": 0.0,
      "meaningful_improvement": false,
      "metric": "v(n009).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": 12.0,
        "max": 12.0,
        "mean": 12.0,
        "vpp": 0.0,
        "final": 12.0,
        "abs_peak": 12.0
      },
      "scenario_details": {
        "min": 8.0,
        "max": 8.0,
        "mean": 8.0,
        "vpp": 0.0,
        "final": 8.0,
        "abs_peak": 8.0
      }
    },
    {
      "quantity": "v(N004)",
      "base_value": 0.9987514999999991,
      "scenario_value": 4.95415869,
      "delta": 3.9554071900000007,
      "change": "changed",
      "expectation": null,
      "expectation_met": null,
      "relative_change": 3.9603516890838253,
      "meaningful_improvement": false,
      "metric": "v(n004).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": 11.9875351,
        "max": 12.9862866,
        "mean": 12.155920647809523,
        "vpp": 0.9987514999999991,
        "final": 11.9875651,
        "abs_peak": 12.9862866
      },
      "scenario_details": {
        "min": 7.99154431,
        "max": 12.945703,
        "mean": 9.223737259005736,
        "vpp": 4.95415869,
        "final": 7.99155945,
        "abs_peak": 12.945703
      }
    },
    {
      "quantity": "@ddiode7_4[id]",
      "base_value": 0.334752846,
      "scenario_value": 0.33659804,
      "delta": 0.0018451939999999944,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 0.005512108476592293,
      "meaningful_improvement": false,
      "metric": "@ddiode7_4[id].abs_peak",
      "measurement": "tran_abs_peak",
      "base_details": {
        "min": -8.0140838e-05,
        "max": 0.334752846,
        "mean": 0.06261003837421458,
        "vpp": 0.334832986838,
        "final": -4.25542834e-05,
        "abs_peak": 0.334752846
      },
      "scenario_details": {
        "min": -0.000198073885,
        "max": 0.33659804,
        "mean": 0.07180282364196779,
        "vpp": 0.33679611388499997,
        "final": -0.000191011172,
        "abs_peak": 0.33659804
      }
    }
  ],
  "summary": {
    "requested_count": 3,
    "changed_count": 2,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 2,
    "expectations_met_count": 1,
    "expectations_failed_count": 1,
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
    "technical_label": "Partially resolved",
    "label": "Criteri verificati solo in parte",
    "reason": "Solo una parte dei comportamenti attesi dichiarati dallo scenario e stata verificata.",
    "user_message": "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato.",
    "stop_automation": false,
    "confidence": "low",
    "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
  },
  "created_or_updated_at": "2026-07-24T11:35:44"
}
```


## Loaded artifacts

### graph

- Step: `01`
- Role: Graph JSON copied from Pipeline 1.0.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b04\01_graph.json`

```json
{
  "image_id": "b04",
  "image_name": "b04.jpg",
  "components": [
    {
      "component_id": "terminal26.1",
      "instance_id": "26.1",
      "class_name": "Terminal",
      "terminals": [
        {
          "terminal_id": "terminal26.1_t1",
          "name": "t1",
          "relative_position": "top"
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
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "transformer28.1",
      "instance_id": "28.1",
      "class_name": "Transformer",
      "terminals": [
        {
          "terminal_id": "transformer28.1_t1",
          "name": "t1",
          "relative_position": "left"
        },
        {
          "terminal_id": "transformer28.1_t2",
          "name": "t2",
          "relative_position": "right"
        },
        {
          "terminal_id": "transformer28.1_t3",
          "name": "t3",
          "relative_position": "left"
        },
        {
          "terminal_id": "transformer28.1_t4",
          "name": "t4",
          "relative_position": "right"
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
      "component_id": "resistor22.2",
      "instance_id": "22.2",
      "class_name": "Resistor",
      "terminals": [
        {
          "terminal_id": "resistor22.2_t1",
          "name": "t1",
          "relative_position": "left"
        },
        {
          "terminal_id": "resistor22.2_t2",
          "name": "t2",
          "relative_position": "right"
        }
      ]
    },
    {
      "component_id": "diode7.1",
      "instance_id": "7.1",
      "class_name": "Diode",
      "terminals": [
        {
          "terminal_id": "diode7.1_anode",
          "name": "anode",
          "relative_position": "top"
        },
        {
          "terminal_id": "diode7.1_cathode",
          "name": "cathode",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "diode7.2",
      "instance_id": "7.2",
      "class_name": "Diode",
      "terminals": [
        {
          "terminal_id": "diode7.2_anode",
          "name": "anode",
          "relative_position": "left"
        },
        {
          "terminal_id": "diode7.2_cathode",
          "name": "cathode",
          "relative_position": "right"
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
          "relative_position": "right"
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
      "component_id": "diode7.3",
      "instance_id": "7.3",
      "class_name": "Diode",
      "terminals": [
        {
          "terminal_id": "diode7.3_anode",
          "name": "anode",
          "relative_position": "left"
        },
        {
          "terminal_id": "diode7.3_cathode",
          "name": "cathode",
          "relative_position": "right"
        }
      ]
    },
    {
      "component_id": "diode7.4",
      "instance_id": "7.4",
      "class_name": "Diode",
      "terminals": [
        {
          "terminal_id": "diode7.4_anode",
          "name": "anode",
          "relative_position": "left"
        },
        {
          "terminal_id": "diode7.4_cathode",
          "name": "cathode",
          "relative_position": "right"
        }
      ]
    },
    {
      "component_id": "diode7.5",
      "instance_id": "7.5",
      "class_name": "Diode",
      "terminals": [
        {
          "terminal_id": "diode7.5_cathode",
          "name": "cathode",
          "relative_position": "left"
        },
        {
          "terminal_id": "diode7.5_anode",
          "name": "anode",
          "relative_position": "right"
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
      "component_id": "resistor22.6",
      "instance_id": "22.6",
      "class_name": "Resistor",
      "terminals": [
        {
          "terminal_id": "resistor22.6_t1",
          "name": "t1",
          "relative_position": "left"
        },
        {
          "terminal_id": "resistor22.6_t2",
          "name": "t2",
          "relative_position": "right"
        }
      ]
    },
    {
      "component_id": "fuse8.1",
      "instance_id": "8.1",
      "class_name": "Fuse",
      "terminals": [
        {
          "terminal_id": "fuse8.1_t1",
          "name": "t1",
          "relative_position": "left"
        },
        {
          "terminal_id": "fuse8.1_t2",
          "name": "t2",
          "relative_position": "right"
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
          "relative_position": "top"
        }
      ]
    },
    {
      "component_id": "terminal26.4",
      "instance_id": "26.4",
      "class_name": "Terminal",
      "terminals": [
        {
          "terminal_id": "terminal26.4_t1",
          "name": "t1",
          "relative_position": "bottom"
        }
      ]
    }
  ],
  "terminal_metadata": {},
  "graph": {
    "diode7.1_anode": [
      "diode7.3_anode",
      "resistor22.2_t2"
    ],
    "diode7.1_cathode": [
      "npn_transistor18.1_C"
    ],
    "diode7.2_anode": [
      "resistor22.1_t1",
      "resistor22.2_t1",
      "transformer28.1_t2"
    ],
    "diode7.2_cathode": [
      "diode7.3_cathode",
      "diode7.4_cathode",
      "resistor22.3_t1",
      "resistor22.6_t1"
    ],
    "diode7.3_anode": [
      "diode7.1_anode",
      "resistor22.2_t2"
    ],
    "diode7.3_cathode": [
      "diode7.2_cathode",
      "diode7.4_cathode",
      "resistor22.3_t1",
      "resistor22.6_t1"
    ],
    "diode7.4_anode": [
      "resistor22.1_t2"
    ],
    "diode7.4_cathode": [
      "diode7.2_cathode",
      "diode7.3_cathode",
      "resistor22.3_t1",
      "resistor22.6_t1"
    ],
    "diode7.5_anode": [
      "resistor22.4_t1",
      "resistor22.5_t2"
    ],
    "diode7.5_cathode": [
      "npn_transistor18.1_B"
    ],
    "fuse8.1_t1": [
      "resistor22.6_t2"
    ],
    "fuse8.1_t2": [
      "terminal26.3_t1"
    ],
    "npn_transistor18.1_B": [
      "diode7.5_cathode"
    ],
    "npn_transistor18.1_C": [
      "diode7.1_cathode"
    ],
    "npn_transistor18.1_E": [
      "resistor22.4_t2",
      "terminal26.4_t1",
      "transformer28.1_t4"
    ],
    "resistor22.1_t1": [
      "diode7.2_anode",
      "resistor22.2_t1",
      "transformer28.1_t2"
    ],
    "resistor22.1_t2": [
      "diode7.4_anode"
    ],
    "resistor22.2_t1": [
      "diode7.2_anode",
      "resistor22.1_t1",
      "transformer28.1_t2"
    ],
    "resistor22.2_t2": [
      "diode7.1_anode",
      "diode7.3_anode"
    ],
    "resistor22.3_t1": [
      "diode7.2_cathode",
      "diode7.3_cathode",
      "diode7.4_cathode",
      "resistor22.6_t1"
    ],
    "resistor22.3_t2": [
      "resistor22.5_t1"
    ],
    "resistor22.4_t1": [
      "diode7.5_anode",
      "resistor22.5_t2"
    ],
    "resistor22.4_t2": [
      "npn_transistor18.1_E",
      "terminal26.4_t1",
      "transformer28.1_t4"
    ],
    "resistor22.5_t1": [
      "resistor22.3_t2"
    ],
    "resistor22.5_t2": [
      "diode7.5_anode",
      "resistor22.4_t1"
    ],
    "resistor22.6_t1": [
      "diode7.2_cathode",
      "diode7.3_cathode",
      "diode7.4_cathode",
      "resistor22.3_t1"
    ],
    "resistor22.6_t2": [
      "fuse8.1_t1"
    ],
    "terminal26.1_t1": [
      "transformer28.1_t1"
    ],
    "terminal26.2_t1": [
      "transformer28.1_t3"
    ],
    "terminal26.3_t1": [
      "fuse8.1_t2"
    ],
    "terminal26.4_t1": [
      "npn_transistor18.1_E",
      "resistor22.4_t2",
      "transformer28.1_t4"
    ],
    "transformer28.1_t1": [
      "terminal26.1_t1"
    ],
    "transformer28.1_t2": [
      "diode7.2_anode",
      "resistor22.1_t1",
      "resistor22.2_t1"
    ],
    "transformer28.1_t3": [
      "terminal26.2_t1"
    ],
    "transformer28.1_t4": [
      "npn_transistor18.1_E",
      "resistor22.4_t2",
      "terminal26.4_t1"
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
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b04\03_node_map.json`

```json
{
  "circuit_id": "b04",
  "source_format": "pipeline2.0_node_map",
  "nodes": [
    {
      "node_id": "N001",
      "kind": "normal",
      "terminals": [
        "diode7.1_anode",
        "diode7.3_anode",
        "resistor22.2_t2"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N002",
      "kind": "normal",
      "terminals": [
        "diode7.1_cathode",
        "npn_transistor18.1_C"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N003",
      "kind": "normal",
      "terminals": [
        "diode7.2_anode",
        "resistor22.1_t1",
        "resistor22.2_t1",
        "transformer28.1_t2"
      ],
      "terminal_count": 4
    },
    {
      "node_id": "N004",
      "kind": "normal",
      "terminals": [
        "diode7.2_cathode",
        "diode7.3_cathode",
        "diode7.4_cathode",
        "resistor22.3_t1",
        "resistor22.6_t1"
      ],
      "terminal_count": 5
    },
    {
      "node_id": "N005",
      "kind": "normal",
      "terminals": [
        "diode7.4_anode",
        "resistor22.1_t2"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N006",
      "kind": "normal",
      "terminals": [
        "diode7.5_anode",
        "resistor22.4_t1",
        "resistor22.5_t2"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N007",
      "kind": "normal",
      "terminals": [
        "diode7.5_cathode",
        "npn_transistor18.1_B"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N008",
      "kind": "normal",
      "terminals": [
        "fuse8.1_t1",
        "resistor22.6_t2"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N009",
      "kind": "normal",
      "terminals": [
        "fuse8.1_t2",
        "terminal26.3_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N010",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.1_E",
        "resistor22.4_t2",
        "terminal26.4_t1",
        "transformer28.1_t4"
      ],
      "terminal_count": 4
    },
    {
      "node_id": "N011",
      "kind": "normal",
      "terminals": [
        "resistor22.3_t2",
        "resistor22.5_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N012",
      "kind": "normal",
      "terminals": [
        "terminal26.1_t1",
        "transformer28.1_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N013",
      "kind": "normal",
      "terminals": [
        "terminal26.2_t1",
        "transformer28.1_t3"
      ],
      "terminal_count": 2
    }
  ],
  "terminal_to_node": {
    "diode7.1_anode": "N001",
    "diode7.1_cathode": "N002",
    "diode7.2_anode": "N003",
    "diode7.2_cathode": "N004",
    "diode7.3_anode": "N001",
    "diode7.3_cathode": "N004",
    "diode7.4_anode": "N005",
    "diode7.4_cathode": "N004",
    "diode7.5_anode": "N006",
    "diode7.5_cathode": "N007",
    "fuse8.1_t1": "N008",
    "fuse8.1_t2": "N009",
    "npn_transistor18.1_B": "N007",
    "npn_transistor18.1_C": "N002",
    "npn_transistor18.1_E": "N010",
    "resistor22.1_t1": "N003",
    "resistor22.1_t2": "N005",
    "resistor22.2_t1": "N003",
    "resistor22.2_t2": "N001",
    "resistor22.3_t1": "N004",
    "resistor22.3_t2": "N011",
    "resistor22.4_t1": "N006",
    "resistor22.4_t2": "N010",
    "resistor22.5_t1": "N011",
    "resistor22.5_t2": "N006",
    "resistor22.6_t1": "N004",
    "resistor22.6_t2": "N008",
    "terminal26.1_t1": "N012",
    "terminal26.2_t1": "N013",
    "terminal26.3_t1": "N009",
    "terminal26.4_t1": "N010",
    "transformer28.1_t1": "N012",
    "transformer28.1_t2": "N003",
    "transformer28.1_t3": "N013",
    "transformer28.1_t4": "N010"
  },
  "component_terminal_nodes": {
    "diode7.1": {
      "anode": "N001",
      "cathode": "N002"
    },
    "diode7.2": {
      "anode": "N003",
      "cathode": "N004"
    },
    "diode7.3": {
      "anode": "N001",
      "cathode": "N004"
    },
    "diode7.4": {
      "anode": "N005",
      "cathode": "N004"
    },
    "diode7.5": {
      "cathode": "N007",
      "anode": "N006"
    },
    "fuse8.1": {
      "t1": "N008",
      "t2": "N009"
    },
    "npn_transistor18.1": {
      "B": "N007",
      "C": "N002",
      "E": "N010"
    },
    "resistor22.1": {
      "t1": "N003",
      "t2": "N005"
    },
    "resistor22.2": {
      "t1": "N003",
      "t2": "N001"
    },
    "resistor22.3": {
      "t1": "N004",
      "t2": "N011"
    },
    "resistor22.4": {
      "t1": "N006",
      "t2": "N010"
    },
    "resistor22.5": {
      "t1": "N011",
      "t2": "N006"
    },
    "resistor22.6": {
      "t1": "N004",
      "t2": "N008"
    },
    "terminal26.1": {
      "t1": "N012"
    },
    "terminal26.2": {
      "t1": "N013"
    },
    "terminal26.3": {
      "t1": "N009"
    },
    "terminal26.4": {
      "t1": "N010"
    },
    "transformer28.1": {
      "t1": "N012",
      "t2": "N003",
      "t3": "N013",
      "t4": "N010"
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
    "nodes_count": 13,
    "normal_nodes_count": 13,
    "ground_nodes_count": 0,
    "ground_groups_count": 0,
    "terminal_to_node_count": 35,
    "singleton_nodes_count": 0
  }
}
```

### values_bound

- Step: `04`
- Role: Values and labels bound to graph components.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b04\04_values_bound.json`

```json
{
  "circuit_id": "b04",
  "source_format": "pipeline2.0_values_bound",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\data\\batchPipeline2.0\\batchChatAgentEvaluation\\values\\b04_values.yaml",
  "supplies": {
    "VBAT_TEST": {
      "terminal": "terminal26.3_t1",
      "return_terminal": "terminal26.4_t1",
      "type": "dc",
      "value": 12,
      "unit": "V",
      "reference": 0,
      "source": "manual_assumption_nominal_12v_battery_testbench",
      "label_text": "Batteria esterna di prova: 12 V nominali",
      "viewer_override": {
        "visual_class": "battery",
        "label": "",
        "display_value": "12 V",
        "label_mode": "value_only",
        "tooltip": "Batteria esterna in carica; tensione di prova 12 V"
      },
      "node": "N009",
      "return_node": "N010"
    },
    "VREF_BATTERY_NEGATIVE": {
      "terminal": "terminal26.4_t1",
      "type": "dc",
      "value": 0,
      "unit": "V",
      "reference": 0,
      "source": "manual_reference_for_floating_charger_circuit",
      "label_text": "Negativo batteria e ritorno secondario: riferimento SPICE",
      "node": "N010"
    }
  },
  "components": {
    "diode7.1": {
      "class_name": "Diode",
      "terminal_nodes": {
        "anode": "N001",
        "cathode": "N002"
      },
      "value_data": {
        "model": "D_1N4001_TYP",
        "source": "manual_from_image_label",
        "label_text": "D1 1N4001"
      },
      "status": "bound"
    },
    "diode7.2": {
      "class_name": "Diode",
      "terminal_nodes": {
        "anode": "N003",
        "cathode": "N004"
      },
      "value_data": {
        "model": "SCR_2N3668_TYP",
        "source": "manual_semantic_correction_from_image_label",
        "label_text": "H1 2N3668 SCR",
        "viewer_override": {
          "visual_class": "scr",
          "label": "H1",
          "display_value": "2N3668 SCR"
        },
        "spice_override": {
          "emit_as": "subcircuit",
          "pin_order": [
            "anode",
            "gate",
            "cathode"
          ],
          "node_refs": {
            "anode": "diode7.2_anode",
            "gate": "diode7.3_cathode",
            "cathode": "diode7.2_cathode"
          },
          "resolved_node_refs": {
            "anode": "N003",
            "gate": "H1_GATE",
            "cathode": "N004"
          }
        }
      },
      "status": "bound"
    },
    "diode7.3": {
      "class_name": "Diode",
      "terminal_nodes": {
        "anode": "N001",
        "cathode": "H1_GATE"
      },
      "value_data": {
        "model": "D_1N4001_TYP",
        "source": "manual_from_image_label",
        "label_text": "D3 1N4001"
      },
      "status": "bound"
    },
    "diode7.4": {
      "class_name": "Diode",
      "terminal_nodes": {
        "anode": "N005",
        "cathode": "N004"
      },
      "value_data": {
        "model": "D_1N4001_TYP",
        "source": "manual_from_image_label",
        "label_text": "D4 1N4001"
      },
      "status": "bound"
    },
    "diode7.5": {
      "class_name": "Diode",
      "terminal_nodes": {
        "cathode": "N007",
        "anode": "N006"
      },
      "value_data": {
        "model": "D_GENERIC",
        "source": "manual_generic_model_for_image_label_SD50",
        "label_text": "D2 SD50; modello diodo generico per la prima base run",
        "viewer_override": {
          "visual_class": "diode",
          "label": "D2",
          "display_value": "SD50"
        }
      },
      "status": "bound"
    },
    "fuse8.1": {
      "class_name": "Fuse",
      "terminal_nodes": {
        "t1": "N008",
        "t2": "N009"
      },
      "value_data": {
        "state": "closed",
        "current_rating": 2,
        "current_rating_unit": "A",
        "source": "manual_from_image_label",
        "label_text": "F1 2 A, chiuso"
      },
      "status": "bound"
    },
    "npn_transistor18.1": {
      "class_name": "NPN_Transistor",
      "terminal_nodes": {
        "B": "N007",
        "C": "N002",
        "E": "N010"
      },
      "value_data": {
        "model": "BC148_TYP",
        "source": "manual_from_image_label_and_functional_spice_validation",
        "label_text": "Q1 BC148 NPN"
      },
      "status": "bound"
    },
    "resistor22.1": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N003",
        "t2": "N005"
      },
      "value_data": {
        "value": 22,
        "unit": "ohm",
        "power": 5,
        "power_unit": "W",
        "source": "manual_from_image_label",
        "label_text": "R2 22 ohm 5 W"
      },
      "status": "bound"
    },
    "resistor22.2": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N003",
        "t2": "N001"
      },
      "value_data": {
        "value": 330,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R1 330 ohm"
      },
      "status": "bound"
    },
    "resistor22.3": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N004",
        "t2": "N011"
      },
      "value_data": {
        "value": 820,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R3 820 ohm"
      },
      "status": "bound"
    },
    "resistor22.4": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N006",
        "t2": "N010"
      },
      "value_data": {
        "value": 100,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R5 100 ohm"
      },
      "status": "bound"
    },
    "resistor22.5": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N011",
        "t2": "N006"
      },
      "value_data": {
        "value": 50,
        "unit": "ohm",
        "nominal_total_value": 100,
        "nominal_total_unit": "ohm",
        "source": "manual_from_image_label_midpoint_assumption",
        "label_text": "R4 variabile 100 ohm; equivalente base run 50 ohm",
        "viewer_override": {
          "visual_class": "resistor",
          "label": "R4",
          "display_value": "100 ohm",
          "tooltip": "R4; potenziometro 100 ohm, equivalente SPICE base run 50 ohm"
        },
        "spice_override": {
          "emit_as": "resistive_load",
          "equivalent_resistance": 50,
          "resistance_unit": "ohm",
          "node_order": [
            "t1",
            "t2"
          ]
        }
      },
      "status": "bound"
    },
    "resistor22.6": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N004",
        "t2": "N008"
      },
      "value_data": {
        "value": 1,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R6 1 ohm"
      },
      "status": "bound"
    },
    "terminal26.1": {
      "class_name": "Terminal",
      "terminal_nodes": {
        "t1": "N012"
      },
      "value_data": null,
      "status": "not_required"
    },
    "terminal26.2": {
      "class_name": "Terminal",
      "terminal_nodes": {
        "t1": "N013"
      },
      "value_data": null,
      "status": "not_required"
    },
    "terminal26.3": {
      "class_name": "Terminal",
      "terminal_nodes": {
        "t1": "N009"
      },
      "value_data": null,
      "status": "not_required"
    },
    "terminal26.4": {
      "class_name": "Terminal",
      "terminal_nodes": {
        "t1": "N010"
      },
      "value_data": null,
      "status": "not_required"
    },
    "transformer28.1": {
      "class_name": "Transformer",
      "terminal_nodes": {
        "t1": "N012",
        "t2": "N003",
        "t3": "N013",
        "t4": "N010"
      },
      "value_data": {
        "model": "T1_230VAC_TO_15VAC_EQ",
        "secondary_voltage_rms": 15,
        "frequency": 50,
        "source": "manual_from_image_label",
        "label_text": "T1: primario 230 V AC, secondario 15-0 V AC",
        "viewer_override": {
          "visual_class": "transformer",
          "label": "T1",
          "display_value": "230 V AC / 15-0 V AC",
          "label_mode": "reference_only",
          "tooltip": "T1; trasformatore 230 V AC / 15-0 V AC",
          "include_graph_terminals": true
        },
        "spice_override": {
          "emit_as": "equivalent_ac_source",
          "node_order": [
            "t2",
            "t4"
          ],
          "waveform": "sin",
          "source": "manual_transformer_secondary_pinout_from_image"
        }
      },
      "status": "bound"
    }
  },
  "nodes": {
    "terminal26.1_t1": {
      "label": "AC_L",
      "source": "manual_from_image_label",
      "label_text": "Ingresso T1: 230 V AC, conduttore superiore",
      "node": "N012"
    },
    "terminal26.2_t1": {
      "label": "AC_N",
      "source": "manual_from_image_label",
      "label_text": "Ingresso T1: 230 V AC, conduttore inferiore",
      "node": "N013"
    },
    "terminal26.3_t1": {
      "label": "BAT_POSITIVE",
      "source": "manual_from_image_context",
      "label_text": "Morsetto positivo batteria esterna",
      "node": "N009"
    },
    "terminal26.4_t1": {
      "label": "BAT_NEGATIVE",
      "source": "manual_from_image_context",
      "label_text": "Morsetto negativo batteria esterna e riferimento SPICE",
      "node": "N010"
    },
    "transformer28.1_t2": {
      "label": "SEC_15VAC",
      "source": "manual_from_image_label",
      "label_text": "Secondario T1: 15 V AC",
      "node": "N003"
    },
    "transformer28.1_t4": {
      "label": "SEC_0V_BAT_NEG",
      "source": "manual_from_image_label",
      "label_text": "Secondario T1: 0 V e negativo batteria",
      "node": "N010"
    }
  },
  "spice_topology_overlay": [
    {
      "terminal_id": "diode7.3_cathode",
      "from_node": "N004",
      "to_node": "H1_GATE",
      "status": "applied",
      "source": "manual_image_validation_H1_gate_via_D3"
    }
  ],
  "simulation": {
    "analyses": [
      "op",
      "tran"
    ],
    "tran": {
      "step": "100us",
      "stop": "100ms"
    },
    "readiness": "ready"
  },
  "missing": [],
  "stats": {
    "components_total": 18,
    "bound_components": 14,
    "missing_components": 0,
    "not_required_components": 4,
    "unsupported_components": 0,
    "supplies_count": 2,
    "manual_nodes_count": 6
  }
}
```

### component_rules

- Step: `06`
- Role: SPICE conversion rules for each component.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b04\06_component_rules.json`

```json
{
  "circuit_id": "b04",
  "source_format": "pipeline2.0_component_rules",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\data\\batchPipeline2.0\\batchChatAgentEvaluation\\values\\b04_values.yaml",
  "spice_classes_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_spice_classes.yaml",
  "supplies": {
    "VBAT_TEST": {
      "status": "spice_ready",
      "spice_prefix": "V",
      "emit_as": "independent_voltage_source",
      "nodes": [
        "N009",
        "0"
      ],
      "parameters": {
        "terminal": "terminal26.3_t1",
        "return_terminal": "terminal26.4_t1",
        "type": "dc",
        "value": 12,
        "unit": "V",
        "reference": 0,
        "source": "manual_assumption_nominal_12v_battery_testbench",
        "label_text": "Batteria esterna di prova: 12 V nominali",
        "viewer_override": {
          "visual_class": "battery",
          "label": "",
          "display_value": "12 V",
          "label_mode": "value_only",
          "tooltip": "Batteria esterna in carica; tensione di prova 12 V"
        },
        "node": "N009",
        "return_node": "N010"
      }
    },
    "VREF_BATTERY_NEGATIVE": {
      "status": "spice_ready",
      "spice_prefix": "V",
      "emit_as": "independent_voltage_source",
      "nodes": [
        "N010",
        "0"
      ],
      "parameters": {
        "terminal": "terminal26.4_t1",
        "type": "dc",
        "value": 0,
        "unit": "V",
        "reference": 0,
        "source": "manual_reference_for_floating_charger_circuit",
        "label_text": "Negativo batteria e ritorno secondario: riferimento SPICE",
        "node": "N010"
      }
    }
  },
  "components": {
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
        "N002"
      ],
      "parameters": {
        "model": "D_1N4001_TYP",
        "source": "manual_from_image_label",
        "label_text": "D1 1N4001"
      }
    },
    "diode7.2": {
      "class_name": "Diode",
      "status": "spice_ready",
      "spice_support": "subcircuit",
      "spice_prefix": "X",
      "emit_as": "subcircuit",
      "node_order": [
        "anode",
        "gate",
        "cathode"
      ],
      "nodes": [
        "N003",
        "H1_GATE",
        "N004"
      ],
      "parameters": {
        "model": "SCR_2N3668_TYP",
        "source": "manual_semantic_correction_from_image_label",
        "label_text": "H1 2N3668 SCR",
        "viewer_override": {
          "visual_class": "scr",
          "label": "H1",
          "display_value": "2N3668 SCR"
        },
        "spice_override": {
          "emit_as": "subcircuit",
          "pin_order": [
            "anode",
            "gate",
            "cathode"
          ],
          "node_refs": {
            "anode": "diode7.2_anode",
            "gate": "diode7.3_cathode",
            "cathode": "diode7.2_cathode"
          },
          "resolved_node_refs": {
            "anode": "N003",
            "gate": "H1_GATE",
            "cathode": "N004"
          }
        }
      },
      "reason": "Explicit YAML override emitted as a SPICE subcircuit."
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
        "N001",
        "H1_GATE"
      ],
      "parameters": {
        "model": "D_1N4001_TYP",
        "source": "manual_from_image_label",
        "label_text": "D3 1N4001"
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
        "N005",
        "N004"
      ],
      "parameters": {
        "model": "D_1N4001_TYP",
        "source": "manual_from_image_label",
        "label_text": "D4 1N4001"
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
        "N006",
        "N007"
      ],
      "parameters": {
        "model": "D_GENERIC",
        "source": "manual_generic_model_for_image_label_SD50",
        "label_text": "D2 SD50; modello diodo generico per la prima base run",
        "viewer_override": {
          "visual_class": "diode",
          "label": "D2",
          "display_value": "SD50"
        }
      }
    },
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
        "N008",
        "N009"
      ],
      "parameters": {
        "state": "closed",
        "current_rating": 2,
        "current_rating_unit": "A",
        "source": "manual_from_image_label",
        "label_text": "F1 2 A, chiuso"
      },
      "strategy": "short_circuit"
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
        "N002",
        "N007",
        "N010"
      ],
      "parameters": {
        "model": "BC148_TYP",
        "source": "manual_from_image_label_and_functional_spice_validation",
        "label_text": "Q1 BC148 NPN"
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
        "N003",
        "N005"
      ],
      "parameters": {
        "value": 22,
        "unit": "ohm",
        "power": 5,
        "power_unit": "W",
        "source": "manual_from_image_label",
        "label_text": "R2 22 ohm 5 W"
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
        "N003",
        "N001"
      ],
      "parameters": {
        "value": 330,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R1 330 ohm"
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
        "N011"
      ],
      "parameters": {
        "value": 820,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R3 820 ohm"
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
        "N010"
      ],
      "parameters": {
        "value": 100,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R5 100 ohm"
      }
    },
    "resistor22.5": {
      "class_name": "Resistor",
      "status": "spice_ready",
      "spice_support": "equivalent",
      "spice_prefix": "R",
      "emit_as": "resistive_load",
      "node_order": [
        "t1",
        "t2"
      ],
      "nodes": [
        "N011",
        "N006"
      ],
      "parameters": {
        "value": 50,
        "unit": "ohm",
        "nominal_total_value": 100,
        "nominal_total_unit": "ohm",
        "source": "manual_from_image_label_midpoint_assumption",
        "label_text": "R4 variabile 100 ohm; equivalente base run 50 ohm",
        "viewer_override": {
          "visual_class": "resistor",
          "label": "R4",
          "display_value": "100 ohm",
          "tooltip": "R4; potenziometro 100 ohm, equivalente SPICE base run 50 ohm"
        },
        "spice_override": {
          "emit_as": "resistive_load",
          "equivalent_resistance": 50,
          "resistance_unit": "ohm",
          "node_order": [
            "t1",
            "t2"
          ]
        },
        "equivalent_resistance": 50,
        "resistance_unit": "ohm"
      },
      "reason": "Explicit YAML override emitted as an equivalent resistive load."
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
        "N004",
        "N008"
      ],
      "parameters": {
        "value": 1,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "R6 1 ohm"
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
    },
    "terminal26.4": {
      "class_name": "Terminal",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "External terminal/label; useful for nodes and interface handling."
    },
    "transformer28.1": {
      "class_name": "Transformer",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "V",
      "emit_as": "equivalent_ac_source",
      "node_order": [
        "t2",
        "t4"
      ],
      "nodes": [
        "N003",
        "N010"
      ],
      "parameters": {
        "model": "T1_230VAC_TO_15VAC_EQ",
        "secondary_voltage_rms": 15,
        "frequency": 50,
        "source": "manual_from_image_label",
        "label_text": "T1: primario 230 V AC, secondario 15-0 V AC",
        "viewer_override": {
          "visual_class": "transformer",
          "label": "T1",
          "display_value": "230 V AC / 15-0 V AC",
          "label_mode": "reference_only",
          "tooltip": "T1; trasformatore 230 V AC / 15-0 V AC",
          "include_graph_terminals": true
        },
        "spice_override": {
          "emit_as": "equivalent_ac_source",
          "node_order": [
            "t2",
            "t4"
          ],
          "waveform": "sin",
          "source": "manual_transformer_secondary_pinout_from_image"
        }
      }
    }
  },
  "simulation": {
    "analyses": [
      "op",
      "tran"
    ],
    "tran": {
      "step": "100us",
      "stop": "100ms"
    },
    "readiness": "ready"
  },
  "stats": {
    "components_total": 18,
    "spice_ready_components": 14,
    "not_emitted_components": 4,
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
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b04\07_netlist.cir`

```spice
* pipeline2.0 netlist
* circuit: b04

VVBAT_TEST N009 0 DC 12
VVREF_BATTERY_NEGATIVE N010 0 DC 0
Ddiode7_1 N001 N002 D_1N4001_TYP
Xdiode7_2 N003 H1_GATE N004 SCR_2N3668_TYP
Ddiode7_3 N001 H1_GATE D_1N4001_TYP
Ddiode7_4 N005 N004 D_1N4001_TYP
Ddiode7_5 N006 N007 D_GENERIC
Rfuse8_1 N008 N009 1m
Qnpn_transistor18_1 N002 N007 N010 BC148_TYP
Rresistor22_1 N003 N005 22
Rresistor22_2 N003 N001 330
Rresistor22_3 N004 N011 820
Rresistor22_4 N006 N010 100
Rresistor22_5 N011 N006 50
Rresistor22_6 N004 N008 1
Vtransformer28_1 N003 N010 SIN(0 21.2132 50)

.model BC148_TYP NPN(BF=110 VAF=50 IKF=100m IS=1e-14)
.model D_1N4001_TYP D(IS=14n N=1.9 RS=0.08 BV=50 IBV=5u TT=2u CJO=25p)
.model D_GENERIC D
.subckt SCR_2N3668_TYP A G K
BMAIN A K I={V(A,K)*(1/10Meg+(1/0.05-1/10Meg)*(0.5+0.5*tanh((V(G,K)-0.75)/0.08)))}
RGK G K 100
.ends SCR_2N3668_TYP

.op
.save all
.tran 100us 100ms

.control
set wr_singlescale
set wr_vecnames
save all @ddiode7_1[id] @ddiode7_3[id] @ddiode7_4[id] @ddiode7_5[id]
run
wrdata 08_tran.csv time v(H1_GATE) v(N001) v(N002) v(N003) v(N004) v(N005) v(N006) v(N007) v(N008) v(N009) v(N010) v(N011) @ddiode7_1[id] @ddiode7_3[id] @ddiode7_4[id] @ddiode7_5[id]
.endc
.end

```

### spice_emit_report

- Step: `07`
- Role: Report of emitted, skipped and warning components.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b04\07_spice_emit_report.json`

```json
{
  "circuit_id": "b04",
  "source_format": "pipeline2.0_spice_emit_report",
  "emitted_elements": 16,
  "skipped_elements": 4,
  "skipped_components": [
    "terminal26.1",
    "terminal26.2",
    "terminal26.3",
    "terminal26.4"
  ],
  "informational_skips": [
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
      "H1_GATE",
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
    "device_currents": [
      "@ddiode7_1[id]",
      "@ddiode7_3[id]",
      "@ddiode7_4[id]",
      "@ddiode7_5[id]"
    ]
  },
  "models": [
    "BC148_TYP",
    "D_1N4001_TYP",
    "D_GENERIC",
    "SCR_2N3668_TYP"
  ],
  "warnings": []
}
```

### spice_run

- Step: `08`
- Role: Structured ngspice execution report.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b04\08_spice_run.json`

```json
{
  "source_format": "pipeline2.0_spice_run",
  "status": "success",
  "netlist_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\b04\\07_netlist.cir",
  "command": [
    "C:\\Users\\m.profilo\\Spice64\\bin\\ngspice_con.exe",
    "-b",
    "07_netlist.cir"
  ],
  "exit_code": 0,
  "stdout_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\b04\\08_ngspice_stdout.txt",
  "stderr_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\b04\\08_ngspice_stderr.txt",
  "tran_raw_csv_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\b04\\08_tran_raw.csv",
  "tran_csv_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\b04\\08_tran.csv",
  "tran_plot_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\b04\\08_tran_plot.png",
  "tran_plot_png_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\b04\\08_tran_plot.png",
  "tran_plot_svg_path": null,
  "message": "ngspice completed successfully."
}
```

### ngspice_stdout

- Step: `08`
- Role: Raw ngspice stdout log.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b04\08_ngspice_stdout.txt`

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
n009                                        12
n010                                         0
n001                               6.04824e-06
n002                                 0.0181194
n003                                         0
n004                                   11.9876
h1_gate                                11.9876
n005                               3.08264e-07
n006                                   1.22384
n007                                  0.620743
n008                                        12
n011                                   1.84244
vtransformer28_1#branch            2.95585e-06
vvref_battery_negative#branch        0.0123751
vvbat_test#branch                   -0.0123751


No. of Data Rows : 1050
Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

No. of Data Rows : 1

Initial Transient Solution
--------------------------

Node                                   Voltage
----                                   -------
n009                                        12
n010                                         0
n001                               6.04824e-06
n002                                 0.0181194
n003                                         0
n004                                   11.9876
h1_gate                                11.9876
n005                               3.08264e-07
n006                                   1.22384
n007                                  0.620743
n008                                        12
n011                                   1.84244
vtransformer28_1#branch            2.95585e-06
vvref_battery_negative#branch        0.0123751
vvbat_test#branch                   -0.0123751


No. of Data Rows : 1050
	Node                                  Voltage
	----                                  -------
	----	-------
	n011                             1.842444e+00
	n008                             1.199999e+01
	n007                             6.207428e-01
	n006                             1.223836e+00
	n005                             3.082637e-07
	h1_gate                          1.198761e+01
	n004                             1.198761e+01
	n003                             0.000000e+00
	n002                             1.811939e-02
	n001                             6.048240e-06
	n010                             0.000000e+00
	n009                             1.200000e+01

	Source	Current
	------	-------

	@ddiode7_5[id]                   1.337997e-04
	@ddiode7_4[id]                   -1.40120e-08
	@ddiode7_3[id]                   -1.40120e-08
	@ddiode7_1[id]                   -4.31601e-09
	vvbat_test#branch                -1.23751e-02
	vvref_battery_negative#branch    1.237511e-02
	vtransformer28_1#branch          2.955850e-06

 BJT models (Bipolar Junction Transistor)
      model             bc148_typ

       type                   npn
       tnom                    27
         is                 1e-14
        ibe                     0
        ibc                     0
         bf                   110
         nf                     1
        vaf                    50
        ikf                   0.1
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

 Diode models (Junction Diode model)
      model             d_generic          d_1n4001_typ

      level                     1                     1
         is                 1e-14               1.4e-08
        jsw                     0                     0
         rs                     0                  0.08
        rsw                     0                     0
        trs                     0                     0
       trs2                     0                     0
          n                     1                   1.9
         ns                     1                     1
         tt                     0                 2e-06
       ttt1                     0                     0
       ttt2                     0                     0
        cjo                     0               2.5e-11
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
        nbv                     1                   1.9
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
         kf                     0                     0
         af                     1                     1
         fc                   0.5                   0.5
        fcs                   0.5                   0.5
         bv                     0                    50
        ibv                 0.001                 5e-06
        tcv                     0                     0
        isr                 1e-14                 1e-14
         nr                     2                     2
         vp                     0                     0
     fv_max                 1e+99                 1e+99
     bv_max                 1e+99                 1e+99
     id_max                 1e+99                 1e+99
     te_max                 1e+99                 1e+99
     pd_max                 1e+99                 1e+99
       rth0                     0                     0
       cth0                 1e-05                 1e-05
         lm                     0                     0
         lp                     0                     0
         wm                     0                     0
         wp                     0                     0
        xom                 10000                 10000
        xoi                 10000                 10000
         xm                     0                     0
         xp                     0                     0
         xw                     0                     0

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

 ASRC: Arbitrary Source 
     device     b.xdiode7_2.bmain
      dtemp                     0
          i          -2.90363e-06
          v              -11.9876
   pos_node                     5
```

> Artifact truncated in this preview. The original file remains available through the manifest path.

### ngspice_stderr

- Step: `08`
- Role: Raw ngspice stderr log.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b04\08_ngspice_stderr.txt`

```text

```

### tran_csv

- Step: `08`
- Role: Clean transient CSV, when .tran data is available.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b04\08_tran.csv`

```csv
time,v(H1_GATE),v(N001),v(N002),v(N003),v(N004),v(N005),v(N006),v(N007),v(N008),v(N009),v(N010),v(N011),@ddiode7_1[id],@ddiode7_3[id],@ddiode7_4[id],@ddiode7_5[id]
0.0,11.9876111,6.04823973e-06,0.0181193877,0.0,11.9876125,3.08263699e-07,1.22383575,0.62074283,11.9999876,12.0,0.0,1.84244361,-4.31601287e-09,-1.40119863e-08,-1.40119863e-08,0.000133799746
1e-06,11.9876158,0.006600223,0.0181359433,0.00666432322,11.9876126,0.00666361457,1.22383882,0.620752494,11.9999876,12.0,0.0,1.84244651,1.63079591e-07,3.17056133e-08,3.22170113e-08,0.000133765638
2e-06,11.9876158,0.0132628459,0.0181364019,0.0133286458,11.9876126,0.0133279367,1.2238389,0.620752761,11.9999876,12.0,0.0,1.84244659,1.67768139e-07,3.22243447e-08,3.22366171e-08,0.000133764693
4e-06,11.9876158,0.0265898001,0.0181369059,0.0266572863,11.9876126,0.0266565768,1.22383899,0.620753055,11.9999876,12.0,0.0,1.84244667,1.74897979e-07,3.2272557e-08,3.2272257e-08,0.000133763655
8e-06,11.9876159,0.0532408107,0.0181387762,0.0533145305,11.9876126,0.0533138197,1.22383934,0.620754147,11.9999876,12.0,0.0,1.842447,1.91107595e-07,3.22857253e-08,3.23079501e-08,0.000133759801
1.6e-05,11.9876159,0.106530296,0.0181461933,0.106628724,11.9876126,0.106628011,1.22384071,0.620758475,11.9999876,12.0,0.0,1.84244829,2.65873273e-07,3.23940937e-08,3.24151856e-08,0.000133744517
3.2e-05,11.9876159,0.212898403,0.0182237202,0.213254754,11.9876127,0.213254037,1.22385504,0.620803705,11.9999876,12.0,0.0,1.8424618,1.04747376e-06,3.23900643e-08,3.25948453e-08,0.000133584835
5.08156973e-05,11.987616,0.335190412,0.0191498739,0.338637853,11.9876129,0.33863713,1.22402504,0.621343269,11.9999876,12.0,0.0,1.84262204,1.04161554e-05,3.07277971e-08,3.2833621e-08,0.000131689701
6.89381606e-05,11.9876161,0.436192188,0.0249333264,0.459390277,11.9876141,0.45938955,1.22504011,0.624682078,11.9999876,12.0,0.0,1.84357884,7.02978636e-05,1.9747974e-08,3.30413486e-08,0.000120374414
8.91614077e-05,11.9876175,0.51470894,0.0400656446,0.59412275,11.9876168,0.594122017,1.22733535,0.633158625,11.9999876,12.0,0.0,1.84574232,0.000240641569,7.10825129e-09,3.33006396e-08,9.4786089e-05
0.00011806539,11.9876202,0.588349739,0.0662744825,0.786645528,11.9876201,0.786644788,1.23022888,0.646810974,11.9999876,12.0,0.0,1.84846975,0.000602402566,9.91001448e-10,3.36467928e-08,6.25308976e-05
0.000171848257,11.9876226,0.677084946,0.111615588,1.14469609,11.9876232,1.14469534,1.23282792,0.665510124,11.9999876,12.0,0.0,1.8509196,0.00142067458,-5.54488392e-09,3.4335612e-08,3.35552068e-05
0.000234949703,11.9876252,0.807829427,0.218122511,1.5643594,11.9876245,1.56435863,1.23386111,0.677418884,11.9999876,12.0,0.0,1.85189348,0.00229255155,7.12738113e-09,3.51421888e-08,2.20368496e-05
0.000313830215,11.9876305,1.31443242,0.722742559,2.08807931,11.9876247,2.08807852,1.23388309,0.677730313,11.9999876,12.0,0.0,1.85191422,0.00234433822,5.78397911e-08,3.6210797e-08,2.17916194e-05
0.000392331511,11.9876257,1.82645875,1.23501917,2.60800897,11.9876248,2.60800818,1.2338831,0.677730317,11.9999876,12.0,0.0,1.85191423,0.00236835707,1.06638509e-08,3.73031033e-08,2.17916224e-05
0.000475125236,11.9876308,2.36477382,1.7721232,3.15464341,11.987625,3.15464259,1.23388312,0.677730327,11.9999876,12.0,0.0,1.85191426,0.00239423747,5.9827258e-08,3.85302798e-08,2.17916298e-05
0.000575125236,11.9876262,3.01213878,2.4194909,3.81200042,11.9876251,3.81199958,1.23388313,0.677730333,11.9999876,12.0,0.0,1.85191427,0.00242381169,1.30271347e-08,4.00819097e-08,2.17916343e-05
0.000675125236,11.9876314,3.65578548,3.06195993,4.46559545,11.9876253,4.46559457,1.23388315,0.677730343,11.9999876,12.0,0.0,1.85191431,0.00245463089,6.25480829e-08,4.17801846e-08,2.17916428e-05
0.000775125236,11.9876268,4.29510694,3.70120101,5.11478347,11.9876254,5.11478256,1.23388316,0.677730349,11.9999876,12.0,0.0,1.85191432,0.00248385743,1.59349742e-08,4.35985341e-08,2.17916472e-05
0.000875125236,11.987632,4.92944098,4.33447853,5.75892382,11.9876256,5.75892287,1.23388318,0.67773036,11.9999876,12.0,0.0,1.85191436,0.00251411624,6.56629809e-08,4.56223775e-08,2.17916556e-05
0.000975125236,11.9876274,5.55819569,4.96308723,6.39738081,11.9876257,6.39737982,1.23388319,0.677730366,11.9999876,12.0,0.0,1.85191437,0.00254297937,1.93204748e-08,4.78431186e-08,2.179166e-05
0.00107512524,11.9876326,6.18071387,5.58465369,7.02952435,11.9876259,7.02952332,1.23388321,0.677730377,11.9999876,12.0,0.0,1.8519144,0.00257258071,6.93584952e-08,5.03713231e-08,2.17916683e-05
0.00117512524,11.9876281,6.7964202,6.20016508,7.65473061,11.987626,7.65472952,1.23388322,0.677730382,11.9999876,12.0,0.0,1.85191442,0.00260094065,2.34239959e-08,5.32354471e-08,2.17916726e-05
0.00127512524,11.9876333,7.40466589,6.80755047,8.27238257,11.9876262,8.27238141,1.23388324,0.677730393,11.9999876,12.0,0.0,1.85191445,0.00262978691,7.39497039e-08,5.66016537e-08,2.17916808e-05
0.00137512524,11.9876288,8.00489373,7.40754815,8.88187068,11.9876263,8.88186946,1.23388325,0.677730399,11.9999876,12.0,0.0,1.85191447,0.0026575104,2.86681049e-08,6.05863818e-08,2.1791685e-05
0.00147512524,11.9876341,8.59646653,7.99834113,9.48259346,11.9876265,9.48259215,1.23388327,0.677730409,11.9999876,12.0,0.0,1.8519145,0.00268550409,8.00174332e-08,6.55012793e-08,2.17916931e-05
0.00157512524,11.9876297,9.17884685,8.58046736,10.0739581,11.9876266,10.0739567,1.23388329,0.677730415,11.9999876,12.0,0.0,1.85191451,0.00271246416,3.58775153e-08,7.17209348e-08,2.17916972e-05
0.00167512524,11.9876351,9.75141204,9.15232428,10.6553809,11.9876268,10.6553793,1.23388331,0.677730425,11.9999876,12.0,0.0,1.85191454,0.00273950864,8.87775484e-08,8.00549282e-08,2.17917053e-05
0.00177512524,11.9876309,10.3136461,9.71428965,11.2262882,11.9876269,11.2262864,1.23388332,0.67773043,11.9999876,12.0,0.0,1.85191456,0.00276558445,4.6937477e-08,9.19638863e-08,2.17917093e-05
0.00187512524,11.9876365,10.8649438,10.2649432,11.7861164,11.9876271,11.7861144,1.23388334,0.677730441,11.9999876,12.0,0.0,1.85191459,0.00279158457,1.03347798e-07,1.11343593e-07,2.17917176e-05
0.00197512524,11.9876508,11.4047788,10.8045018,12.3343132,11.987644,12.3339419,1.23388501,0.67773128,11.9999877,12.0,0.0,1.85191714,0.00281670333,6.7487741e-08,1.68782115e-05,2.17924243e-05
0.00207512524,11.9973341,11.9157375,11.3140302,12.8703375,11.9973216,12.6570573,1.23484604,0.678211796,11.9999973,12.0,0.0,1.85337912,0.00289260175,1.25413869e-07,0.00969471052,2.22010651e-05
0.00217512524,12.0200833,12.3862601,11.7824408,13.3936603,12.017567,12.7355175,1.23685438,0.679215963,12.0000175,12.0,0.0,1.85643557,0.0030275651,2.51631817e-05,0.0299283533,2.30799389e-05
0.00227512524,12.1062954,12.6377037,12.0315693,13.9037653,12.0391186,12.7857144,1.23898898,0.680283265,12.0000391,12.0,0.0,1.85968608,0.00316478461,0.000720668898,0.0514887536,2.4052243e-05
0.00237512524,12.2181062,12.7908847,12.1827456,14.4001488,12.0607589,12.8261876,1.24112884,0.681353192,12.0000607,12.0,0.0,1.86294666,0.00330308576,0.00162077532,0.0728488865,2.5068053e-05
0.00247512524,12.3309375,12.9247072,12.3143995,14.8823212,12.0821692,12.8615044,1.24324232,0.682409933,12.0000821,12.0,0.0,1.86616915,0.00344448125,0.00248768505,0.0933794164,2.6113447e-05
0.00257512524,12.4415663,13.0506618,12.4382797,15.3498065,12.1047185,12.8944644,1.24546421,0.683520876,12.0001046,12.0,0.0,1.86955928,0.00359863851,0.00337375738,0.111623855,2.72595021e-05
0.00267512524,12.5519846,13.1711293,12.5555459,15.8021434,12.1383218,12.9371283,1.24876725,0.685172397,12.0001382,12.0,0.0,1.87460372,0.00383614239,0.00413663094,0.130227964,2.90568416e-05
0.00277512524,12.6638613,13.2887679,12.6675534,16.2388855,12.2008693,13.0069948,1.25488811,0.688232828,12.0002007,12.0,0.0,1.88396749,0.00430985021,0.00462995532,0.146904151,3.27066237e-05
0.00287512524,12.770331,13.3978599,12.7692665,16.6596018,12.2816735,13.0938319,1.26273775,0.692157645,12.0002814,12.0,0.0,1.89600992,0.00499749579,0.00488658075,0.162080454,3.8065964e-05
0.00297512524,12.8696159,13.4990524,12.8631667,17.0638771,12.3629193,13.1806445,1.27059502,0.696086279,12.0003626,12.0,0.0,1.90808492,0.00579454984,0.00507078023,0.177209374,4.43100294e-05
0.00307512524,12.9500248,13.579854,12.9372999,17.4513124,12.4387814,13.261175,1.27778211,0.699679826,12.0004383,12.0,0.0,1.91921885,0.006619372,0.0051124457,0.190461199,5.09144236e-05
0.00317512524,13.0240665,13.6544308,13.0059539,17.8215253,12.5073493,13.3341906,1.28424341,0.702910475,12.0005068,12.0,0.0,1.9292495,0.00746046448,0.00516718311,0.203970154,5.76881036e-05
0.00327512524,13.0894032,13.7201193,13.0663323,18.1741505,12.5690034,13.3999457,1.28999142,0.705784478,12.0005684,12.0,0.0,1.93821049,0.00829313852,0.00520400234,0.217009593,6.4467864e-05
0.00337512524,13.1472931,13.7782567,13.1198261,18.5088401,12.6243323,13.4590346,1.29509577,0.708336656,12.0006237,12.0,0.0,1.94620132,0.0091055453,0.00522960967,0.22953681,7.11535496e-05
0.00347512524,13.1987736,13.8299078,13.1673232,18.8252637,12.6739967,13.5121641,1.29963104,0.710604291,12.0006733,12.0,0.0,1.95333022,0.00988971356,0.00524776909,0.241504671,7.76733711e-05
0.00357512524,13.2446721,13.8759323,13.2097048,19.123109,12.7185914,13.5599287,1.30366362,0.71262058,12.0007179,12.0,0.0,1.95969396,0.0106397548,0.00526080739,0.252871931,8.39706291e-05
0.00367512524,13.2856527,13.9170002,13.2475111,19.4020821,12.7586289,13.6028745,1.30725045,0.714413995,12.0007579,12.0,0.0,1.96537565,0.0113512414,0.00527023806,0.26360042,8.99995629e-05
0.00377512524,13.3229767,13.9543986,13.2819784,19.6619076,12.795182,13.6420999,1.31051015,0.716043843,12.0007944,12.0,0.0,1.97054876,0.0120381567,0.00527795279,0.273828517,9.58532788e-05
0.00387512524,13.3554106,13.9868754,13.3119083,19.9023293,12.8271516,13.676474,1.31332226,0.717449897,12.0008263,12.0,0.0,1.97503658,0.0126594426,0.0052825924,0.283156673,0.000101208233
0.00397512524,13.3842913,14.0157892,13.3386044,20.1231098,12.8556908,13.7071749,1.31581422,0.718695879,12.0008548,12.0,0.0,1.97902552,0.013234061,0.00528600645,0.291766486,0.000106203049
0.00407512524,13.4098457,14.0413658,13.3622019,20.3240312,12.8810018,13.7344331,1.3180088,0.719793167,12.0008801,12.0,0.0,1.98254862,0.0137607602,0.00528843957,0.299636833,0.000110805519
0.00417512524,13.4322941,14.0638311,13.382966,20.5048952,12.9032791,13.7584319,1.31992801,0.720752775,12.0009024,12.0,0.0,1.98563784,0.0142365072,0.00529015091,0.306743538,0.000114993704
0.00427512524,13.4518161,14.0833636,13.4010047,20.6655233,12.9226829,13.7793542,1.32159009,0.721583816,12.0009218,12.0,0.0,1.98831957,0.0146611978,0.00529133255,0.313075566,0.000118748453
0.00437512524,13.4685557,14.1001113,13.416498,20.8057571,12.9393429,13.7973205,1.32300991,0.722293726,12.0009384,12.0,0.0,1.99061526,0.0150327818,0.00529212831,0.318615623,0.000122052859
0.00447512524,13.4826305,14.1141904,13.4295093,20.9254581,12.9533656,13.8124547,1.32419972,0.72288863,12.0009524,12.0,0.0,1.99254259,0.0153510958,0.00529264864,0.32335519,0.000124892661
0.00457512524,13.494133,14.1256965,13.4401611,21.0245082,12.9648354,13.8248329,1.3251693,0.723373418,12.0009639,12.0,0.0,1.99411563,0.0156148208,0.00529297573,0.327282571,0.000127255611
0.00467512524,13.5031365,14.1347015,13.4484853,21.1028097,12.9738193,13.8345358,1.32592644,0.72375199,12.0009728,12.0,0.0,1.99534557,0.0158237958,0.00529317218,0.33039167,0.000129131884
0.00477512524,13.5096956,14.1412621,13.4545621,21.1602853,12.9803674,13.841606,1.32647701,0.724027272,12.0009794,12.0,0.0,1.99624082,0.0159772442,0.00529328244,0.332675422,0.000130513582
0.00487512524,13.5138497,14.1454162,13.4583992,21.1968781,12.9845159,13.8460902,1.32682523,0.724201383,12.0009835,12.0,0.0,1.99680745,0.0160750579,0.00529333811,0.334130163,0.000131395105
0.00497512524,13.5156224,14.1471895,13.4600433,21.2125523,12.9862866,13.8480031,1.32697369,0.724275615,12.0009853,12.0,0.0,1.99704915,0.0161168875,0.00529335754,0.334752846,0.000131772751
0.00507512524,13.5150244,14.146591,13.4594809,21.2072922,12.9856895,13.8473623,1.32692354,0.724250538,12.0009847,12.0,0.0,1.99696756,0.0161027192,0.00529334904,0.334542317,0.000131645052
0.00517512524,13.5120517,14.1
```

> Artifact truncated in this preview. The original file remains available through the manifest path.
