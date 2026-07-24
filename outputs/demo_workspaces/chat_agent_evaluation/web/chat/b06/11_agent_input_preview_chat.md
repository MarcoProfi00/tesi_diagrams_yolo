# Agent input preview

This file is a local preview of the evidence that will be provided to the read-only diagnostic agent.
The agent remains read-only: it can inspect base outputs and existing scenario artifacts, but it does not modify files.

## User problem

Concludi esperimento.

## Circuit

- Batch: `batchChatAgentEvaluation`
- Circuit: `b06`
- Agent mode: `graph_grounded_readonly`

## Technical summary

```json
{
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_message": "ngspice completed successfully.",
  "emitted_elements": 16,
  "skipped_elements": 2,
  "emit_warnings_count": 1,
  "skipped_components_count": 2,
  "node_count": 11,
  "ground_groups_count": 1,
  "singleton_nodes_count": 1,
  "bound_components": 15,
  "missing_components": 0,
  "unsupported_components": 2,
  "spice_ready_components": 16,
  "rules_missing_components": 0,
  "has_tran_csv": true,
  "has_tran_plot": true,
  "led_profiles": {}
}
```

## Image policy

- Included by default: `False`
- Can be requested: `True`
- Path: `outputs\demo_workspaces\chat_agent_evaluation\input\images\b06.jpg`
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
      "title": "Iniettare un piccolo segnale audio all'ingresso dell'LM386",
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
          "v(N010)",
          "v(N009)",
          "v(N003)"
        ],
        "unchanged": [],
        "missing": []
      },
      "led_profiles": {},
      "ranking_verified": true,
      "score": 30
    },
    {
      "scenario_id": "scenario_3",
      "title": "Iniettare un piccolo segnale sul nodo di base del transistor",
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
        "activated_count": 2,
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
          "v(N005)",
          "v(N006)",
          "v(N010)"
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
      "title": "Iniettare un piccolo segnale sul nodo rivelato dopo il diodo",
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
        "activated_count": 2,
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
          "v(N004)",
          "v(N005)",
          "v(N010)"
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

- Title: `Iniettare un piccolo segnale audio all'ingresso dell'LM386`
- Status: `spice_success`
- SPICE status: `success`
- Outcome: `partially_resolved`
- Stop automation: `False`
- Comparison: `3/3` changed
- LED profiles: `{}`

#### scenario_definition

- Role: Scenario selected by the user and saved before execution.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b06\scenarios\scenario_1\scenario.json`

```json
{
  "scenario_id": "scenario_1",
  "title": "Iniettare un piccolo segnale audio all'ingresso dell'LM386",
  "hypothesis": "L'uscita silenziosa dipende dall'assenza di segnale su N010, non necessariamente da un guasto dell'uscita audio.",
  "intent": "diagnostic",
  "actions": [
    {
      "type": "add_voltage_source_between_nodes",
      "positive": "N010",
      "negative": "0",
      "value": "SIN(0 5m 1000)"
    }
  ],
  "rerun_from": "07",
  "analysis": "tran",
  "compare": [
    "v(N010)",
    "v(N009)",
    "v(N003)"
  ],
  "expect": {
    "v(N009)": "changed",
    "v(N003)": "changed"
  }
}
```

#### scenario_status

- Role: Current scenario status, SPICE status and diagnostic outcome.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b06\scenarios\scenario_1\scenario_status.json`

```json
{
  "status": "spice_success",
  "stage": "scenario_spice_executed",
  "scenario_id": "scenario_1",
  "source": "guided_chat",
  "spice_executed": true,
  "created_or_updated_at": "2026-07-24T16:45:22",
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\scenarios\\scenario_1\\run\\08_spice_run.json",
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\scenarios\\scenario_1\\scenario_comparison.json",
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
  "controlled_scenario_report": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\scenarios\\scenario_1\\12_controlled_scenarios.json",
  "executed_scenarios_count": 1,
  "scenario_budget_exhausted": false,
  "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
}
```

#### controlled_scenario_report

- Role: Report produced by the controlled scenario runner.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b06\scenarios\scenario_1\12_controlled_scenarios.json`

```json
{
  "source_format": "pipeline2.0_controlled_scenario_report",
  "status": "spice_success",
  "scenario_id": "scenario_1",
  "scenario_title": "Iniettare un piccolo segnale audio all'ingresso dell'LM386",
  "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\scenarios\\scenario_1",
  "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\scenarios\\scenario_1\\run",
  "netlist": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\scenarios\\scenario_1\\run\\07_netlist.cir",
  "applied_actions": [
    {
      "status": "applied",
      "type": "add_voltage_source_between_nodes",
      "positive": "N010",
      "negative": "0",
      "nodes": [
        "N010",
        "0"
      ],
      "value": "SIN(0 5m 1000)",
      "normalized_source_definition": "SIN(0 5m 1000)",
      "normalized_dc_value": null,
      "inserted_line": "VSCENARIO_SUPPLY_N010_0 N010 0 SIN(0 5m 1000)",
      "operation": "inserted",
      "spice_executed": false,
      "index": 1
    }
  ],
  "unsupported_actions": [],
  "failed_actions": [],
  "spice_executed": true,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\scenarios\\scenario_1\\run\\08_spice_run.json",
  "spice_status": "success",
  "spice_exit_code": 0,
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\scenarios\\scenario_1\\scenario_comparison.json",
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
  "created_or_updated_at": "2026-07-24T16:45:22"
}
```

#### scenario_comparison

- Role: Base-vs-scenario comparison used to evaluate the scenario.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b06\scenarios\scenario_1\scenario_comparison.json`

```json
{
  "source_format": "pipeline2.0_scenario_comparison",
  "scenario_id": "scenario_1",
  "scenario_title": "Iniettare un piccolo segnale audio all'ingresso dell'LM386",
  "scenario_intent": "diagnostic",
  "base_output_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06",
  "scenario_run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\scenarios\\scenario_1\\run",
  "base_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\08_ngspice_stdout.txt",
  "scenario_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\scenarios\\scenario_1\\run\\08_ngspice_stdout.txt",
  "base_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\08_ngspice_stderr.txt",
  "scenario_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\scenarios\\scenario_1\\run\\08_ngspice_stderr.txt",
  "quantities": [
    {
      "quantity": "v(N010)",
      "base_value": 1.2775336350000001e-11,
      "scenario_value": 0.00999998556,
      "delta": 0.009999985547224664,
      "change": "changed",
      "expectation": null,
      "expectation_met": null,
      "relative_change": 782757124.6078905,
      "meaningful_improvement": false,
      "metric": "v(n010).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": -3.3317793e-12,
        "max": 9.44355705e-12,
        "mean": 6.700634900279153e-13,
        "vpp": 1.2775336350000001e-11,
        "final": -6.67688127e-13,
        "abs_peak": 9.44355705e-12
      },
      "scenario_details": {
        "min": -0.00499999278,
        "max": 0.00499999278,
        "mean": 4.550778204308436e-09,
        "vpp": 0.00999998556,
        "final": -6.123234e-18,
        "abs_peak": 0.00499999278
      }
    },
    {
      "quantity": "v(N009)",
      "base_value": 1.572337199e-10,
      "scenario_value": 0.1249347616,
      "delta": 0.12493476144276627,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 794579950.9305273,
      "meaningful_improvement": false,
      "metric": "v(n009).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": -4.10046319e-11,
        "max": 1.16229088e-10,
        "mean": 1.1085349100145368e-11,
        "vpp": 1.572337199e-10,
        "final": -4.21739509e-12,
        "abs_peak": 1.16229088e-10
      },
      "scenario_details": {
        "min": -0.0612894961,
        "max": 0.0636452655,
        "mean": 0.001005235789310393,
        "vpp": 0.1249347616,
        "final": -0.00176228251,
        "abs_peak": 0.0636452655
      }
    },
    {
      "quantity": "v(N003)",
      "base_value": 1.572368115e-10,
      "scenario_value": 0.1247464258,
      "delta": 0.1247464256427632,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 793366543.4494213,
      "meaningful_improvement": false,
      "metric": "v(n003).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": -4.10095265e-11,
        "max": 1.16227285e-10,
        "mean": 3.705473117402556e-12,
        "vpp": 1.572368115e-10,
        "final": -1.46181879e-11,
        "abs_peak": 1.16227285e-10
      },
      "scenario_details": {
        "min": -0.0640781517,
        "max": 0.0606682741,
        "mean": -0.001608231637878011,
        "vpp": 0.1247464258,
        "final": 0.00281965202,
        "abs_peak": 0.0640781517
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
  "created_or_updated_at": "2026-07-24T16:45:22"
}
```

### scenario_3

- Title: `Iniettare un piccolo segnale sul nodo di base del transistor`
- Status: `spice_success`
- SPICE status: `success`
- Outcome: `partially_resolved`
- Stop automation: `False`
- Comparison: `3/3` changed
- LED profiles: `{}`

#### scenario_definition

- Role: Scenario selected by the user and saved before execution.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b06\scenarios\scenario_3\scenario.json`

```json
{
  "scenario_id": "scenario_3",
  "title": "Iniettare un piccolo segnale sul nodo di base del transistor",
  "hypothesis": "Il segnale potrebbe interrompersi tra N005, N006 e N010, cioe nello stadio a transistor o nel condensatore Cpolarized_capacitor20_4 verso l'LM386.",
  "intent": "diagnostic",
  "actions": [
    {
      "type": "add_voltage_source_between_nodes",
      "positive": "N005",
      "negative": "0",
      "value": "SIN(0.660106 5m 1000)"
    }
  ],
  "rerun_from": "07",
  "analysis": "tran",
  "compare": [
    "v(N005)",
    "v(N006)",
    "v(N010)"
  ],
  "expect": {
    "v(N006)": "changed",
    "v(N010)": "changed"
  }
}
```

#### scenario_status

- Role: Current scenario status, SPICE status and diagnostic outcome.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b06\scenarios\scenario_3\scenario_status.json`

```json
{
  "status": "spice_success",
  "stage": "scenario_spice_executed",
  "scenario_id": "scenario_3",
  "source": "guided_chat",
  "spice_executed": true,
  "created_or_updated_at": "2026-07-24T16:47:18",
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\scenarios\\scenario_3\\run\\08_spice_run.json",
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\scenarios\\scenario_3\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 3,
    "changed_count": 3,
    "activated_count": 2,
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
  "controlled_scenario_report": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\scenarios\\scenario_3\\12_controlled_scenarios.json",
  "executed_scenarios_count": 2,
  "scenario_budget_exhausted": false,
  "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
}
```

#### controlled_scenario_report

- Role: Report produced by the controlled scenario runner.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b06\scenarios\scenario_3\12_controlled_scenarios.json`

```json
{
  "source_format": "pipeline2.0_controlled_scenario_report",
  "status": "spice_success",
  "scenario_id": "scenario_3",
  "scenario_title": "Iniettare un piccolo segnale sul nodo di base del transistor",
  "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\scenarios\\scenario_3",
  "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\scenarios\\scenario_3\\run",
  "netlist": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\scenarios\\scenario_3\\run\\07_netlist.cir",
  "applied_actions": [
    {
      "status": "applied",
      "type": "add_voltage_source_between_nodes",
      "positive": "N005",
      "negative": "0",
      "nodes": [
        "N005",
        "0"
      ],
      "value": "SIN(0.660106 5m 1000)",
      "normalized_source_definition": "SIN(0.660106 5m 1000)",
      "normalized_dc_value": null,
      "inserted_line": "VSCENARIO_SUPPLY_N005_0 N005 0 SIN(0.660106 5m 1000)",
      "operation": "inserted",
      "spice_executed": false,
      "index": 1
    }
  ],
  "unsupported_actions": [],
  "failed_actions": [],
  "spice_executed": true,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\scenarios\\scenario_3\\run\\08_spice_run.json",
  "spice_status": "success",
  "spice_exit_code": 0,
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\scenarios\\scenario_3\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 3,
    "changed_count": 3,
    "activated_count": 2,
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
  "created_or_updated_at": "2026-07-24T16:47:18"
}
```

#### scenario_comparison

- Role: Base-vs-scenario comparison used to evaluate the scenario.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b06\scenarios\scenario_3\scenario_comparison.json`

```json
{
  "source_format": "pipeline2.0_scenario_comparison",
  "scenario_id": "scenario_3",
  "scenario_title": "Iniettare un piccolo segnale sul nodo di base del transistor",
  "scenario_intent": "diagnostic",
  "base_output_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06",
  "scenario_run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\scenarios\\scenario_3\\run",
  "base_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\08_ngspice_stdout.txt",
  "scenario_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\scenarios\\scenario_3\\run\\08_ngspice_stdout.txt",
  "base_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\08_ngspice_stderr.txt",
  "scenario_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\scenarios\\scenario_3\\run\\08_ngspice_stderr.txt",
  "quantities": [
    {
      "quantity": "v(N005)",
      "base_value": 0.0,
      "scenario_value": 0.009999992000000013,
      "delta": 0.009999992000000013,
      "change": "activated",
      "expectation": null,
      "expectation_met": null,
      "relative_change": 9999992000.000013,
      "meaningful_improvement": false,
      "metric": "v(n005).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": 0.66010638,
        "max": 0.66010638,
        "mean": 0.66010638,
        "vpp": 0.0,
        "final": 0.66010638,
        "abs_peak": 0.66010638
      },
      "scenario_details": {
        "min": 0.655106004,
        "max": 0.665105996,
        "mean": 0.6601060063274142,
        "vpp": 0.009999992000000013,
        "final": 0.660106,
        "abs_peak": 0.665105996
      }
    },
    {
      "quantity": "v(N006)",
      "base_value": 0.0,
      "scenario_value": 1.2508000630000002,
      "delta": 1.2508000630000002,
      "change": "activated",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 1250800063000.0002,
      "meaningful_improvement": false,
      "metric": "v(n006).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": 1.28178949,
        "max": 1.28178949,
        "mean": 1.28178949,
        "vpp": 0.0,
        "final": 1.28178949,
        "abs_peak": 1.28178949
      },
      "scenario_details": {
        "min": 0.565979127,
        "max": 1.81677919,
        "mean": 1.2211735745466878,
        "vpp": 1.2508000630000002,
        "final": 1.31205946,
        "abs_peak": 1.81677919
      }
    },
    {
      "quantity": "v(N010)",
      "base_value": 1.2775336350000001e-11,
      "scenario_value": 1.221923666,
      "delta": 1.2219236659872246,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 95647083764.43056,
      "meaningful_improvement": false,
      "metric": "v(n010).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": -3.3317793e-12,
        "max": 9.44355705e-12,
        "mean": 6.700634900279153e-13,
        "vpp": 1.2775336350000001e-11,
        "final": -6.67688127e-13,
        "abs_peak": 9.44355705e-12
      },
      "scenario_details": {
        "min": -0.624816877,
        "max": 0.597106789,
        "mean": 0.010043216926295586,
        "vpp": 1.221923666,
        "final": -0.0302544755,
        "abs_peak": 0.624816877
      }
    }
  ],
  "summary": {
    "requested_count": 3,
    "changed_count": 3,
    "activated_count": 2,
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
  "created_or_updated_at": "2026-07-24T16:47:18"
}
```

### scenario_4

- Title: `Iniettare un piccolo segnale sul nodo rivelato dopo il diodo`
- Status: `spice_success`
- SPICE status: `success`
- Outcome: `partially_resolved`
- Stop automation: `False`
- Comparison: `3/3` changed
- LED profiles: `{}`

#### scenario_definition

- Role: Scenario selected by the user and saved before execution.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b06\scenarios\scenario_4\scenario.json`

```json
{
  "scenario_id": "scenario_4",
  "title": "Iniettare un piccolo segnale sul nodo rivelato dopo il diodo",
  "hypothesis": "Il segnale potrebbe interrompersi tra N004 e N005, cioe tra il rivelatore e l'ingresso dello stadio a transistor.",
  "intent": "diagnostic",
  "actions": [
    {
      "type": "add_voltage_source_between_nodes",
      "positive": "N004",
      "negative": "0",
      "value": "SIN(0 5m 1000)"
    }
  ],
  "rerun_from": "07",
  "analysis": "tran",
  "compare": [
    "v(N004)",
    "v(N005)",
    "v(N010)"
  ],
  "expect": {
    "v(N005)": "changed",
    "v(N010)": "changed"
  }
}
```

#### scenario_status

- Role: Current scenario status, SPICE status and diagnostic outcome.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b06\scenarios\scenario_4\scenario_status.json`

```json
{
  "status": "spice_success",
  "stage": "scenario_spice_executed",
  "scenario_id": "scenario_4",
  "source": "guided_chat",
  "spice_executed": true,
  "created_or_updated_at": "2026-07-24T16:47:53",
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\scenarios\\scenario_4\\run\\08_spice_run.json",
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\scenarios\\scenario_4\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 3,
    "changed_count": 3,
    "activated_count": 2,
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
  "controlled_scenario_report": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\scenarios\\scenario_4\\12_controlled_scenarios.json",
  "executed_scenarios_count": 3,
  "scenario_budget_exhausted": false,
  "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
}
```

#### controlled_scenario_report

- Role: Report produced by the controlled scenario runner.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b06\scenarios\scenario_4\12_controlled_scenarios.json`

```json
{
  "source_format": "pipeline2.0_controlled_scenario_report",
  "status": "spice_success",
  "scenario_id": "scenario_4",
  "scenario_title": "Iniettare un piccolo segnale sul nodo rivelato dopo il diodo",
  "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\scenarios\\scenario_4",
  "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\scenarios\\scenario_4\\run",
  "netlist": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\scenarios\\scenario_4\\run\\07_netlist.cir",
  "applied_actions": [
    {
      "status": "applied",
      "type": "add_voltage_source_between_nodes",
      "positive": "N004",
      "negative": "0",
      "nodes": [
        "N004",
        "0"
      ],
      "value": "SIN(0 5m 1000)",
      "normalized_source_definition": "SIN(0 5m 1000)",
      "normalized_dc_value": null,
      "inserted_line": "VSCENARIO_SUPPLY_N004_0 N004 0 SIN(0 5m 1000)",
      "operation": "inserted",
      "spice_executed": false,
      "index": 1
    }
  ],
  "unsupported_actions": [],
  "failed_actions": [],
  "spice_executed": true,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\scenarios\\scenario_4\\run\\08_spice_run.json",
  "spice_status": "success",
  "spice_exit_code": 0,
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\scenarios\\scenario_4\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 3,
    "changed_count": 3,
    "activated_count": 2,
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
  "created_or_updated_at": "2026-07-24T16:47:53"
}
```

#### scenario_comparison

- Role: Base-vs-scenario comparison used to evaluate the scenario.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b06\scenarios\scenario_4\scenario_comparison.json`

```json
{
  "source_format": "pipeline2.0_scenario_comparison",
  "scenario_id": "scenario_4",
  "scenario_title": "Iniettare un piccolo segnale sul nodo rivelato dopo il diodo",
  "scenario_intent": "diagnostic",
  "base_output_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06",
  "scenario_run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\scenarios\\scenario_4\\run",
  "base_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\08_ngspice_stdout.txt",
  "scenario_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\scenarios\\scenario_4\\run\\08_ngspice_stdout.txt",
  "base_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\08_ngspice_stderr.txt",
  "scenario_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\chat\\b06\\scenarios\\scenario_4\\run\\08_ngspice_stderr.txt",
  "quantities": [
    {
      "quantity": "v(N004)",
      "base_value": 1.038058528e-14,
      "scenario_value": 0.00999997532,
      "delta": 0.00999997531998962,
      "change": "activated",
      "expectation": null,
      "expectation_met": null,
      "relative_change": 9999975319.98962,
      "meaningful_improvement": false,
      "metric": "v(n004).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": -9.93649607e-15,
        "max": 4.4408921e-16,
        "mean": -9.28549487274421e-15,
        "vpp": 1.038058528e-14,
        "final": -9.93649607e-15,
        "abs_peak": 9.93649607e-15
      },
      "scenario_details": {
        "min": -0.00499998766,
        "max": 0.00499998766,
        "mean": 5.7416136320817785e-09,
        "vpp": 0.00999997532,
        "final": -6.123234e-18,
        "abs_peak": 0.00499998766
      }
    },
    {
      "quantity": "v(N005)",
      "base_value": 0.0,
      "scenario_value": 0.004141652000000051,
      "delta": 0.004141652000000051,
      "change": "activated",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 4141652000.0000515,
      "meaningful_improvement": false,
      "metric": "v(n005).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": 0.66010638,
        "max": 0.66010638,
        "mean": 0.66010638,
        "vpp": 0.0,
        "final": 0.66010638,
        "abs_peak": 0.66010638
      },
      "scenario_details": {
        "min": 0.657984582,
        "max": 0.662126234,
        "mean": 0.6600502112470071,
        "vpp": 0.004141652000000051,
        "final": 0.662008434,
        "abs_peak": 0.662126234
      }
    },
    {
      "quantity": "v(N010)",
      "base_value": 1.2775336350000001e-11,
      "scenario_value": 0.49782287399999997,
      "delta": 0.49782287398722463,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 38967496459.47479,
      "meaningful_improvement": false,
      "metric": "v(n010).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": -3.3317793e-12,
        "max": 9.44355705e-12,
        "mean": 6.700634900279153e-13,
        "vpp": 1.2775336350000001e-11,
        "final": -6.67688127e-13,
        "abs_peak": 9.44355705e-12
      },
      "scenario_details": {
        "min": -0.252563475,
        "max": 0.245259399,
        "mean": 0.0019003565568700919,
        "vpp": 0.49782287399999997,
        "final": -0.242613253,
        "abs_peak": 0.252563475
      }
    }
  ],
  "summary": {
    "requested_count": 3,
    "changed_count": 3,
    "activated_count": 2,
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
  "created_or_updated_at": "2026-07-24T16:47:53"
}
```


## Loaded artifacts

### graph

- Step: `01`
- Role: Graph JSON copied from Pipeline 1.0.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b06\01_graph.json`

```json
{
  "image_id": "b06",
  "image_name": "b06.jpg",
  "components": [
    {
      "component_id": "inductor10.1",
      "instance_id": "10.1",
      "class_name": "Inductor",
      "terminals": [
        {
          "terminal_id": "inductor10.1_t1",
          "name": "t1",
          "relative_position": "top"
        },
        {
          "terminal_id": "inductor10.1_t2",
          "name": "t2",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "antenna1.1",
      "instance_id": "1.1",
      "class_name": "Antenna",
      "terminals": [
        {
          "terminal_id": "antenna1.1_t1",
          "name": "t1",
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
      "component_id": "diode7.1",
      "instance_id": "7.1",
      "class_name": "Diode",
      "terminals": [
        {
          "terminal_id": "diode7.1_anode",
          "name": "anode",
          "relative_position": "left"
        },
        {
          "terminal_id": "diode7.1_cathode",
          "name": "cathode",
          "relative_position": "right"
        }
      ]
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
      "component_id": "polarized_capacitor20.3",
      "instance_id": "20.3",
      "class_name": "Polarized_Capacitor",
      "terminals": [
        {
          "terminal_id": "polarized_capacitor20.3_positive",
          "name": "positive",
          "relative_position": "left"
        },
        {
          "terminal_id": "polarized_capacitor20.3_negative",
          "name": "negative",
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
      "component_id": "polarized_capacitor20.4",
      "instance_id": "20.4",
      "class_name": "Polarized_Capacitor",
      "terminals": [
        {
          "terminal_id": "polarized_capacitor20.4_positive",
          "name": "positive",
          "relative_position": "left"
        },
        {
          "terminal_id": "polarized_capacitor20.4_negative",
          "name": "negative",
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
      "component_id": "operational_amplifier19.1",
      "instance_id": "19.1",
      "class_name": "Operational_Amplifier",
      "terminals": [
        {
          "terminal_id": "operational_amplifier19.1_in1",
          "name": "in1",
          "relative_position": "left"
        },
        {
          "terminal_id": "operational_amplifier19.1_in2",
          "name": "in2",
          "relative_position": "left"
        },
        {
          "terminal_id": "operational_amplifier19.1_out",
          "name": "out",
          "relative_position": "right"
        },
        {
          "terminal_id": "operational_amplifier19.1_aux1",
          "name": "aux1",
          "relative_position": "top"
        },
        {
          "terminal_id": "operational_amplifier19.1_aux2",
          "name": "aux2",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "breaker3.1",
      "instance_id": "3.1",
      "class_name": "Breaker",
      "terminals": [
        {
          "terminal_id": "breaker3.1_t1",
          "name": "t1",
          "relative_position": "top"
        },
        {
          "terminal_id": "breaker3.1_t2",
          "name": "t2",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "polarized_capacitor20.5",
      "instance_id": "20.5",
      "class_name": "Polarized_Capacitor",
      "terminals": [
        {
          "terminal_id": "polarized_capacitor20.5_positive",
          "name": "positive",
          "relative_position": "top"
        },
        {
          "terminal_id": "polarized_capacitor20.5_negative",
          "name": "negative",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "polarized_capacitor20.6",
      "instance_id": "20.6",
      "class_name": "Polarized_Capacitor",
      "terminals": [
        {
          "terminal_id": "polarized_capacitor20.6_positive",
          "name": "positive",
          "relative_position": "top"
        },
        {
          "terminal_id": "polarized_capacitor20.6_negative",
          "name": "negative",
          "relative_position": "bottom"
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
          "relative_position": "top"
        },
        {
          "terminal_id": "switch25.1_t2",
          "name": "t2",
          "relative_position": "bottom"
        }
      ],
      "state": "closed",
      "state_confidence": 0.95
    },
    {
      "component_id": "battery2.1",
      "instance_id": "2.1",
      "class_name": "Battery",
      "terminals": [
        {
          "terminal_id": "battery2.1_positive",
          "name": "positive",
          "relative_position": "top"
        },
        {
          "terminal_id": "battery2.1_negative",
          "name": "negative",
          "relative_position": "bottom"
        }
      ]
    }
  ],
  "terminal_metadata": {},
  "graph": {
    "antenna1.1_t1": [
      "diode7.1_anode",
      "inductor10.1_t1",
      "polarized_capacitor20.1_positive"
    ],
    "battery2.1_negative": [
      "breaker3.1_t2",
      "gnd9.1_t1",
      "inductor10.1_t2",
      "npn_transistor18.1_E",
      "operational_amplifier19.1_aux2",
      "operational_amplifier19.1_in2",
      "polarized_capacitor20.1_negative",
      "polarized_capacitor20.2_negative",
      "polarized_capacitor20.6_negative",
      "resistor22.3_t2"
    ],
    "battery2.1_positive": [
      "switch25.1_t2"
    ],
    "breaker3.1_t1": [
      "polarized_capacitor20.5_negative"
    ],
    "breaker3.1_t2": [
      "battery2.1_negative",
      "gnd9.1_t1",
      "inductor10.1_t2",
      "npn_transistor18.1_E",
      "operational_amplifier19.1_aux2",
      "operational_amplifier19.1_in2",
      "polarized_capacitor20.1_negative",
      "polarized_capacitor20.2_negative",
      "polarized_capacitor20.6_negative",
      "resistor22.3_t2"
    ],
    "diode7.1_anode": [
      "antenna1.1_t1",
      "inductor10.1_t1",
      "polarized_capacitor20.1_positive"
    ],
    "diode7.1_cathode": [
      "polarized_capacitor20.2_positive",
      "polarized_capacitor20.3_positive"
    ],
    "gnd9.1_t1": [
      "battery2.1_negative",
      "breaker3.1_t2",
      "inductor10.1_t2",
      "npn_transistor18.1_E",
      "operational_amplifier19.1_aux2",
      "operational_amplifier19.1_in2",
      "polarized_capacitor20.1_negative",
      "polarized_capacitor20.2_negative",
      "polarized_capacitor20.6_negative",
      "resistor22.3_t2"
    ],
    "inductor10.1_t1": [
      "antenna1.1_t1",
      "diode7.1_anode",
      "polarized_capacitor20.1_positive"
    ],
    "inductor10.1_t2": [
      "battery2.1_negative",
      "breaker3.1_t2",
      "gnd9.1_t1",
      "npn_transistor18.1_E",
      "operational_amplifier19.1_aux2",
      "operational_amplifier19.1_in2",
      "polarized_capacitor20.1_negative",
      "polarized_capacitor20.2_negative",
      "polarized_capacitor20.6_negative",
      "resistor22.3_t2"
    ],
    "npn_transistor18.1_B": [
      "polarized_capacitor20.3_negative",
      "resistor22.1_t1"
    ],
    "npn_transistor18.1_C": [
      "polarized_capacitor20.4_positive",
      "resistor22.1_t2",
      "resistor22.2_t2"
    ],
    "npn_transistor18.1_E": [
      "battery2.1_negative",
      "breaker3.1_t2",
      "gnd9.1_t1",
      "inductor10.1_t2",
      "operational_amplifier19.1_aux2",
      "operational_amplifier19.1_in2",
      "polarized_capacitor20.1_negative",
      "polarized_capacitor20.2_negative",
      "polarized_capacitor20.6_negative",
      "resistor22.3_t2"
    ],
    "operational_amplifier19.1_aux1": [
      "polarized_capacitor20.6_positive",
      "resistor22.2_t1",
      "switch25.1_t1"
    ],
    "operational_amplifier19.1_aux2": [
      "battery2.1_negative",
      "breaker3.1_t2",
      "gnd9.1_t1",
      "inductor10.1_t2",
      "npn_transistor18.1_E",
      "operational_amplifier19.1_in2",
      "polarized_capacitor20.1_negative",
      "polarized_capacitor20.2_negative",
      "polarized_capacitor20.6_negative",
      "resistor22.3_t2"
    ],
    "operational_amplifier19.1_in1": [],
    "operational_amplifier19.1_in2": [
      "battery2.1_negative",
      "breaker3.1_t2",
      "gnd9.1_t1",
      "inductor10.1_t2",
      "npn_transistor18.1_E",
      "operational_amplifier19.1_aux2",
      "polarized_capacitor20.1_negative",
      "polarized_capacitor20.2_negative",
      "polarized_capacitor20.6_negative",
      "resistor22.3_t2"
    ],
    "operational_amplifier19.1_out": [
      "polarized_capacitor20.5_positive"
    ],
    "polarized_capacitor20.1_negative": [
      "battery2.1_negative",
      "breaker3.1_t2",
      "gnd9.1_t1",
      "inductor10.1_t2",
      "npn_transistor18.1_E",
      "operational_amplifier19.1_aux2",
      "operational_amplifier19.1_in2",
      "polarized_capacitor20.2_negative",
      "polarized_capacitor20.6_
```

> Artifact truncated in this preview. The original file remains available through the manifest path.

### node_map

- Step: `03`
- Role: Maps component terminals to SPICE node names.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b06\03_node_map.json`

```json
{
  "circuit_id": "b06",
  "source_format": "pipeline2.0_node_map",
  "nodes": [
    {
      "node_id": "0",
      "kind": "ground",
      "terminals": [
        "battery2.1_negative",
        "breaker3.1_t2",
        "gnd9.1_t1",
        "inductor10.1_t2",
        "npn_transistor18.1_E",
        "operational_amplifier19.1_aux2",
        "operational_amplifier19.1_in2",
        "polarized_capacitor20.1_negative",
        "polarized_capacitor20.2_negative",
        "polarized_capacitor20.6_negative",
        "resistor22.3_t2"
      ],
      "terminal_count": 11,
      "source_groups": [
        [
          "battery2.1_negative",
          "breaker3.1_t2",
          "gnd9.1_t1",
          "inductor10.1_t2",
          "npn_transistor18.1_E",
          "operational_amplifier19.1_aux2",
          "operational_amplifier19.1_in2",
          "polarized_capacitor20.1_negative",
          "polarized_capacitor20.2_negative",
          "polarized_capacitor20.6_negative",
          "resistor22.3_t2"
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
        "battery2.1_positive",
        "switch25.1_t2"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N003",
      "kind": "normal",
      "terminals": [
        "breaker3.1_t1",
        "polarized_capacitor20.5_negative"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N004",
      "kind": "normal",
      "terminals": [
        "diode7.1_cathode",
        "polarized_capacitor20.2_positive",
        "polarized_capacitor20.3_positive"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N005",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.1_B",
        "polarized_capacitor20.3_negative",
        "resistor22.1_t1"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N006",
      "kind": "normal",
      "terminals": [
        "npn_transistor18.1_C",
        "polarized_capacitor20.4_positive",
        "resistor22.1_t2",
        "resistor22.2_t2"
      ],
      "terminal_count": 4
    },
    {
      "node_id": "N007",
      "kind": "normal",
      "terminals": [
        "operational_amplifier19.1_aux1",
        "polarized_capacitor20.6_positive",
        "resistor22.2_t1",
        "switch25.1_t1"
      ],
      "terminal_count": 4
    },
    {
      "node_id": "N008",
      "kind": "normal",
      "terminals": [
        "operational_amplifier19.1_in1"
      ],
      "terminal_count": 1
    },
    {
      "node_id": "N009",
      "kind": "normal",
      "terminals": [
        "operational_amplifier19.1_out",
        "polarized_capacitor20.5_positive"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N010",
      "kind": "normal",
      "terminals": [
        "polarized_capacitor20.4_negative",
        "resistor22.3_t1"
      ],
      "terminal_count": 2
    }
  ],
  "terminal_to_node": {
    "antenna1.1_t1": "N001",
    "battery2.1_negative": "0",
    "battery2.1_positive": "N002",
    "breaker3.1_t1": "N003",
    "breaker3.1_t2": "0",
    "diode7.1_anode": "N001",
    "diode7.1_cathode": "N004",
    "gnd9.1_t1": "0",
    "inductor10.1_t1": "N001",
    "inductor10.1_t2": "0",
    "npn_transistor18.1_B": "N005",
    "npn_transistor18.1_C": "N006",
    "npn_transistor18.1_E": "0",
    "operational_amplifier19.1_aux1": "N007",
    "operational_amplifier19.1_aux2": "0",
    "operational_amplifier19.1_in1": "N008",
    "operational_amplifier19.1_in2": "0",
    "operational_amplifier19.1_out": "N009",
    "polarized_capacitor20.1_negative": "0",
    "polarized_capacitor20.1_positive": "N001",
    "polarized_capacitor20.2_negative": "0",
    "polarized_capacitor20.2_positive": "N004",
    "polarized_capacitor20.3_negative": "N005",
    "polarized_capacitor20.3_positive": "N004",
    "polarized_capacitor20.4_negative": "N010",
    "polarized_capacitor20.4_positive": "N006",
    "polarized_capacitor20.5_negative": "N003",
    "polarized_capacitor20.5_positive": "N009",
    "polarized_capacitor20.6_negative": "0",
    "polarized_capacitor20.6_positive": "N007",
    "resistor22.1_t1": "N005",
    "resistor22.1_t2": "N006",
    "resistor22.2_t1": "N007",
    "resistor22.2_t2": "N006",
    "resistor22.3_t1": "N010",
    "resistor22.3_t2": "0",
    "switch25.1_t1": "N007",
    "switch25.1_t2": "N002"
  },
  "component_terminal_nodes": {
    "antenna1.1": {
      "t1": "N001"
    },
    "battery2.1": {
      "positive": "N002",
      "negative": "0"
    },
    "breaker3.1": {
      "t1": "N003",
      "t2": "0"
    },
    "diode7.1": {
      "anode": "N001",
      "cathode": "N004"
    },
    "gnd9.1": {
      "t1": "0"
    },
    "inductor10.1": {
      "t1": "N001",
      "t2": "0"
    },
    "npn_transistor18.1": {
      "B": "N005",
      "C": "N006",
      "E": "0"
    },
    "operational_amplifier19.1": {
      "in1": "N008",
      "in2": "0",
      "out": "N009",
      "aux1": "N007",
      "aux2": "0"
    },
    "polarized_capacitor20.1": {
      "positive": "N001",
      "negative": "0"
    },
    "polarized_capacitor20.2": {
      "positive": "N004",
      "negative": "0"
    },
    "polarized_capacitor20.3": {
      "positive": "N004",
      "negative": "N005"
    },
    "polarized_capacitor20.4": {
      "positive": "N006",
      "negative": "N010"
    },
    "polarized_capacitor20.5": {
      "positive": "N009",
      "negative": "N003"
    },
    "polarized_capacitor20.6": {
      "positive": "N007",
      "negative": "0"
    },
    "resistor22.1": {
      "t1": "N005",
      "t2": "N006"
    },
    "resistor22.2": {
      "t1": "N007",
      "t2": "N006"
    },
    "resistor22.3": {
      "t1": "N010",
      "t2": "0"
    },
    "switch25.1": {
      "t1": "N007",
      "t2": "N002"
    }
  },
  "warnings": {
    "ground_groups_count": 1,
    "multiple_ground_groups_merged_as_node_0": false,
    "singleton_nodes": [
      "N008"
    ],
    "original_warnings": {
      "unconnected_terminals": [
        "operational_amplifier19.1_in1"
      ],
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
    "terminal_to_node_count": 38,
    "singleton_nodes_count": 1
  }
}
```

### values_bound

- Step: `04`
- Role: Values and labels bound to graph components.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b06\04_values_bound.json`

```json
{
  "circuit_id": "b06",
  "source_format": "pipeline2.0_values_bound",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\data\\batchPipeline2.0\\batchChatAgentEvaluation\\values\\b06_values.yaml",
  "supplies": {},
  "components": {
    "antenna1.1": {
      "class_name": "Antenna",
      "terminal_nodes": {
        "t1": "N001"
      },
      "value_data": {
        "source": "graph_json_external_input",
        "label_text": "Antenna esterna; nessuna sorgente RF nella base run",
        "viewer_override": {
          "visual_class": "antenna",
          "label": "Antenna"
        }
      },
      "status": "unsupported_for_now"
    },
    "battery2.1": {
      "class_name": "Battery",
      "terminal_nodes": {
        "positive": "N002",
        "negative": "0"
      },
      "value_data": {
        "type": "dc",
        "value": 9,
        "unit": "V",
        "source": "manual_from_image_label",
        "label_text": "B1 9 V"
      },
      "status": "bound"
    },
    "breaker3.1": {
      "class_name": "Breaker",
      "terminal_nodes": {
        "t1": "N003",
        "t2": "0"
      },
      "value_data": {
        "spice_override": {
          "emit_as": "resistive_load",
          "equivalent_resistance": 8,
          "resistance_unit": "ohm",
          "node_order": [
            "t1",
            "t2"
          ],
          "semantic_role": "speaker_equivalent"
        },
        "source": "manual_interpretation_Z1_speaker_equivalent",
        "label_text": "Z1 altoparlante equivalente: 8 ohm",
        "viewer_override": {
          "visual_class": "speaker",
          "label": "Z1 8 ohm",
          "tooltip": "Z1 altoparlante; carico SPICE equivalente da 8 ohm"
        }
      },
      "status": "bound"
    },
    "diode7.1": {
      "class_name": "Diode",
      "terminal_nodes": {
        "anode": "N001",
        "cathode": "N004"
      },
      "value_data": {
        "model": "D_GENERIC",
        "source": "manual_image_part_number_with_generic_spice_detector_model",
        "label_text": "D1 AA119; modello SPICE rivelatore generico",
        "viewer_override": {
          "label": "D1",
          "display_value": "AA119",
          "tooltip": "D1 AA119; simulato con modello rivelatore generico"
        }
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
    "inductor10.1": {
      "class_name": "Inductor",
      "terminal_nodes": {
        "t1": "N001",
        "t2": "0"
      },
      "value_data": {
        "value": 0.00022,
        "unit": "H",
        "source": "manual_assumption_inductor_label_ambiguous_220uH",
        "label_text": "L1 assunta: 220 uH",
        "viewer_override": {
          "label": "L1",
          "display_value": "220 uH",
          "tooltip": "L1: valore assunto 220 uH dalla label ambigua dell'immagine"
        }
      },
      "status": "bound"
    },
    "npn_transistor18.1": {
      "class_name": "NPN_Transistor",
      "terminal_nodes": {
        "B": "N005",
        "C": "N006",
        "E": "0"
      },
      "value_data": {
        "model": "2N3904",
        "source": "manual_from_image_label",
        "label_text": "Q1 2N3904",
        "viewer_override": {
          "label": "Q1",
          "display_value": "2N3904"
        }
      },
      "status": "bound"
    },
    "operational_amplifier19.1": {
      "class_name": "Operational_Amplifier",
      "terminal_nodes": {
        "in1": "N010",
        "in2": "0",
        "out": "N009",
        "aux1": "N007",
        "aux2": "0"
      },
      "value_data": {
        "model": "LM386_SIMPLE",
        "source": "manual_image_validation_LM386_pin_mapping",
        "label_text": "IC1 LM386; equivalente SPICE semplice",
        "viewer_override": {
          "visual_class": "operational_amplifier",
          "label": "LM386",
          "tooltip": "IC1 LM386; equivalente SPICE lineare semplice"
        },
        "spice_override": {
          "emit_as": "subcircuit",
          "pin_order": [
            "INP",
            "INM",
            "VCC",
            "VEE",
            "OUT"
          ],
          "node_refs": {
            "INP": "operational_amplifier19.1_in1",
            "INM": "operational_amplifier19.1_in2",
            "VCC": "operational_amplifier19.1_aux1",
            "VEE": "operational_amplifier19.1_aux2",
            "OUT": "operational_amplifier19.1_out"
          },
          "resolved_node_refs": {
            "INP": "N010",
            "INM": "0",
            "VCC": "N007",
            "VEE": "0",
            "OUT": "N009"
          }
        }
      },
      "status": "unsupported_for_now"
    },
    "polarized_capacitor20.1": {
      "class_name": "Polarized_Capacitor",
      "terminal_nodes": {
        "positive": "N001",
        "negative": "0"
      },
      "value_data": {
        "value": 365,
        "unit": "pf",
        "source": "manual_from_image_label",
        "label_text": "C1 variabile 365 pF",
        "viewer_override": {
          "visual_class": "variable_capacitor",
          "label": "C1",
          "display_value": "365 pF"
        }
      },
      "status": "bound"
    },
    "polarized_capacitor20.2": {
      "class_name": "Polarized_Capacitor",
      "terminal_nodes": {
        "positive": "N004",
        "negative": "0"
      },
      "value_data": {
        "value": 100,
        "unit": "nf",
        "source": "manual_from_image_label",
        "label_text": "C2 100 nF",
        "viewer_override": {
          "visual_class": "capacitor",
          "label": "C2",
          "display_value": "100 nF"
        }
      },
      "status": "bound"
    },
    "polarized_capacitor20.3": {
      "class_name": "Polarized_Capacitor",
      "terminal_nodes": {
        "positive": "N004",
        "negative": "N005"
      },
      "value_data": {
        "value": 100,
        "unit": "nf",
        "source": "manual_from_image_label",
        "label_text": "C3 100 nF",
        "viewer_override": {
          "visual_class": "capacitor",
          "label": "C3",
          "display_value": "100 nF"
        }
      },
      "status": "bound"
    },
    "polarized_capacitor20.4": {
      "class_name": "Polarized_Capacitor",
      "terminal_nodes": {
        "positive": "N006",
        "negative": "N010"
      },
      "value_data": {
        "value": 100,
        "unit": "nf",
        "source": "manual_from_image_label",
        "label_text": "C4 100 nF",
        "viewer_override": {
          "visual_class": "capacitor",
          "label": "C4",
          "display_value": "100 nF"
        }
      },
      "status": "bound"
    },
    "polarized_capacitor20.5": {
      "class_name": "Polarized_Capacitor",
      "terminal_nodes": {
        "positive": "N009",
        "negative": "N003"
      },
      "value_data": {
        "value": 220,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C5 220 uF"
      },
      "status": "bound"
    },
    "polarized_capacitor20.6": {
      "class_name": "Polarized_Capacitor",
      "terminal_nodes": {
        "positive": "N007",
        "negative": "0"
      },
      "value_data": {
        "value": 100,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C6 100 uF"
      },
      "status": "bound"
    },
    "resistor22.1": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N005",
        "t2": "N006"
      },
      "value_data": {
        "value": 100,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R1 100 kohm"
      },
      "status": "bound"
    },
    "resistor22.2": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N007",
        "t2": "N006"
      },
      "value_data": {
        "value": 10,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R2 10 kohm"
      },
      "status": "bound"
    },
    "resistor22.3": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N010",
        "t2": "0"
      },
      "value_data": {
        "value": 10,
        "unit": "kohm",
        "source": "manual_from_image_label_fixed_wiper_at_maximum",
        "label_text": "R3 potenziometro 10 kohm; base run al massimo volume",
        "viewer_override": {
          "label": "R3",
          "display_value": "10 kohm",
          "label_mode": "tooltip",
          "tooltip": "R3 potenziometro 10 kohm; cursore base run al massimo volume"
        }
      },
      "status": "bound"
    },
    "switch25.1": {
      "class_name": "Switch",
      "terminal_nodes": {
        "t1": "N007",
        "t2": "N002"
      },
      "value_data": {
        "state": "closed",
        "state_source": "graph_json_state",
        "state_confidence": 0.95,
        "source": "graph_json_state_validated_from_image",
        "label_text": "S1 chiuso",
        "viewer_override": {
          "label": "S1",
          "label_mode": "reference_only",
          "tooltip": "S1 chiuso nella base run"
        }
      },
      "status": "bound"
    }
  },
  "nodes": {},
  "spice_topology_overlay": [
    {
      "terminal_id": "operational_amplifier19.1_in1",
      "from_node": "N008",
      "to_node": "N010",
      "status": "applied",
      "source": "manual_image_validation_R3_wiper_at_maximum_volume"
    }
  ],
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
  "missing": [],
  "stats": {
    "components_total": 18,
    "bound_components": 15,
    "missing_components": 0,
    "not_required_components": 1,
    "unsupported_components": 2,
    "supplies_count": 0,
    "manual_nodes_count": 0
  }
}
```

### component_rules

- Step: `06`
- Role: SPICE conversion rules for each component.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b06\06_component_rules.json`

```json
{
  "circuit_id": "b06",
  "source_format": "pipeline2.0_component_rules",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\data\\batchPipeline2.0\\batchChatAgentEvaluation\\values\\b06_values.yaml",
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
        "N002",
        "0"
      ],
      "parameters": {
        "type": "dc",
        "value": 9,
        "unit": "V",
        "source": "manual_from_image_label",
        "label_text": "B1 9 V"
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
        "0"
      ],
      "parameters": {
        "spice_override": {
          "emit_as": "resistive_load",
          "equivalent_resistance": 8,
          "resistance_unit": "ohm",
          "node_order": [
            "t1",
            "t2"
          ],
          "semantic_role": "speaker_equivalent"
        },
        "source": "manual_interpretation_Z1_speaker_equivalent",
        "label_text": "Z1 altoparlante equivalente: 8 ohm",
        "viewer_override": {
          "visual_class": "speaker",
          "label": "Z1 8 ohm",
          "tooltip": "Z1 altoparlante; carico SPICE equivalente da 8 ohm"
        },
        "equivalent_resistance": 8,
        "resistance_unit": "ohm"
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
        "N004"
      ],
      "parameters": {
        "model": "D_GENERIC",
        "source": "manual_image_part_number_with_generic_spice_detector_model",
        "label_text": "D1 AA119; modello SPICE rivelatore generico",
        "viewer_override": {
          "label": "D1",
          "display_value": "AA119",
          "tooltip": "D1 AA119; simulato con modello rivelatore generico"
        }
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
        "value": 0.00022,
        "unit": "H",
        "source": "manual_assumption_inductor_label_ambiguous_220uH",
        "label_text": "L1 assunta: 220 uH",
        "viewer_override": {
          "label": "L1",
          "display_value": "220 uH",
          "tooltip": "L1: valore assunto 220 uH dalla label ambigua dell'immagine"
        }
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
        "N006",
        "N005",
        "0"
      ],
      "parameters": {
        "model": "2N3904",
        "source": "manual_from_image_label",
        "label_text": "Q1 2N3904",
        "viewer_override": {
          "label": "Q1",
          "display_value": "2N3904"
        }
      }
    },
    "operational_amplifier19.1": {
      "class_name": "Operational_Amplifier",
      "status": "spice_ready",
      "spice_support": "subcircuit",
      "spice_prefix": "X",
      "emit_as": "subcircuit",
      "node_order": [
        "INP",
        "INM",
        "VCC",
        "VEE",
        "OUT"
      ],
      "nodes": [
        "N010",
        "0",
        "N007",
        "0",
        "N009"
      ],
      "parameters": {
        "model": "LM386_SIMPLE",
        "source": "manual_image_validation_LM386_pin_mapping",
        "label_text": "IC1 LM386; equivalente SPICE semplice",
        "viewer_override": {
          "visual_class": "operational_amplifier",
          "label": "LM386",
          "tooltip": "IC1 LM386; equivalente SPICE lineare semplice"
        },
        "spice_override": {
          "emit_as": "subcircuit",
          "pin_order": [
            "INP",
            "INM",
            "VCC",
            "VEE",
            "OUT"
          ],
          "node_refs": {
            "INP": "operational_amplifier19.1_in1",
            "INM": "operational_amplifier19.1_in2",
            "VCC": "operational_amplifier19.1_aux1",
            "VEE": "operational_amplifier19.1_aux2",
            "OUT": "operational_amplifier19.1_out"
          },
          "resolved_node_refs": {
            "INP": "N010",
            "INM": "0",
            "VCC": "N007",
            "VEE": "0",
            "OUT": "N009"
          }
        }
      },
      "reason": "Explicit YAML override emitted as a SPICE subcircuit."
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
        "value": 365,
        "unit": "pf",
        "source": "manual_from_image_label",
        "label_text": "C1 variabile 365 pF",
        "viewer_override": {
          "visual_class": "variable_capacitor",
          "label": "C1",
          "display_value": "365 pF"
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
        "N004",
        "0"
      ],
      "parameters": {
        "value": 100,
        "unit": "nf",
        "source": "manual_from_image_label",
        "label_text": "C2 100 nF",
        "viewer_override": {
          "visual_class": "capacitor",
          "label": "C2",
          "display_value": "100 nF"
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
        "N004",
        "N005"
      ],
      "parameters": {
        "value": 100,
        "unit": "nf",
        "source": "manual_from_image_label",
        "label_text": "C3 100 nF",
        "viewer_override": {
          "visual_class": "capacitor",
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
        "N006",
        "N010"
      ],
      "parameters": {
        "value": 100,
        "unit": "nf",
        "source": "manual_from_image_label",
        "label_text": "C4 100 nF",
        "viewer_override": {
          "visual_class": "capacitor",
          "label": "C4",
          "display_value": "100 nF"
        }
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
        "N009",
        "N003"
      ],
      "parameters": {
        "value": 220,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C5 220 uF"
      }
    },
    "polarized_capacitor20.6": {
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
        "0"
      ],
      "parameters": {
        "value": 100,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C6 100 uF"
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
        "N005",
        "N006"
      ],
      "parameters": {
        "value": 100,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R1 100 kohm"
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
        "N006"
      ],
      "parameters": {
        "value": 10,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R2 10 kohm"
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
        "N010",
        "0"
      ],
      "parameters": {
        "value": 10,
        "unit": "kohm",
        "source": "manual_from_image_label_fixed_wiper_at_maximum",
        "label_text": "R3 potenziometro 10 kohm; base run al massimo volume",
        "viewer_override": {
          "label": "R3",
          "display_value": "10 kohm",
          "label_mode": "tooltip",
          "tooltip": "R3 potenziometro 10 kohm; cursore base run al massimo volume"
        }
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
        "N007",
        "N002"
      ],
      "parameters": {
        "state": "closed",
        "state_source": "graph_json_state",
        "state_confidence": 0.95,
        "source": "graph_json_state_validated_from_image",
        "label_text": "S1 chiuso",
        "viewer_override": {
          "label": "S1",
          "label_mode": "reference_only",
          "tooltip": "S1 chiuso nella base run"
        }
      },
      "strategy": "short_circuit"
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
    "components_total": 18,
    "spice_ready_components": 16,
    "not_emitted_components": 1,
    "measurement_components": 0,
    "missing_components": 0,
    "unsupported_components": 1,
    "pin_aware_components": 0,
    "invalid_components": 0,
    "sup
```

> Artifact truncated in this preview. The original file remains available through the manifest path.

### netlist

- Step: `07`
- Role: Generated SPICE netlist.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b06\07_netlist.cir`

```spice
* pipeline2.0 netlist
* circuit: b06

Vbattery2_1 N002 0 DC 9
Rbreaker3_1 N003 0 8
Ddiode7_1 N001 N004 D_GENERIC
Linductor10_1 N001 0 0.00022
Qnpn_transistor18_1 N006 N005 0 2N3904
Xoperational_amplifier19_1 N010 0 N007 0 N009 LM386_SIMPLE
Cpolarized_capacitor20_1 N001 0 365p
Cpolarized_capacitor20_2 N004 0 100n
Cpolarized_capacitor20_3 N004 N005 100n
Cpolarized_capacitor20_4 N006 N010 100n
Cpolarized_capacitor20_5 N009 N003 220u
Cpolarized_capacitor20_6 N007 0 100u
Rresistor22_1 N005 N006 100k
Rresistor22_2 N007 N006 10k
Rresistor22_3 N010 0 10k
Rswitch25_1 N007 N002 1m

.model 2N3904 NPN(IS=6.734f BF=416.4 VAF=74.03 IKF=66.78m ISE=6.734f NE=1.259 BR=0.7371 VAR=12.11 IKR=0.0 ISC=0.0 NC=2 RB=10 RC=1 RE=0.1 CJE=4.493p VJE=0.75 MJE=0.2593 CJC=3.638p VJC=0.75 MJC=0.3085 TF=301.2p TR=239.5n)
.model D_GENERIC D
.subckt LM386_SIMPLE INP INM VCC VEE OUT
RIN INP INM 50k
EAMP NAMP VEE INP INM 20
ROUT NAMP OUT 5
RBLEED VCC VEE 100k
.ends LM386_SIMPLE

.op
.save all
.tran 1us 5ms

.control
set wr_singlescale
set wr_vecnames
save all @ddiode7_1[id]
run
wrdata 08_tran.csv time v(N001) v(N002) v(N003) v(N004) v(N005) v(N006) v(N007) v(N009) v(N010) @ddiode7_1[id]
.endc
.end

```

### spice_emit_report

- Step: `07`
- Role: Report of emitted, skipped and warning components.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b06\07_spice_emit_report.json`

```json
{
  "circuit_id": "b06",
  "source_format": "pipeline2.0_spice_emit_report",
  "emitted_elements": 16,
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
      "N009",
      "N010"
    ],
    "device_currents": [
      "@ddiode7_1[id]"
    ]
  },
  "models": [
    "2N3904",
    "D_GENERIC",
    "LM386_SIMPLE"
  ],
  "warnings": [
    "antenna1.1: class not yet supported by SPICE emit"
  ]
}
```

### spice_run

- Step: `08`
- Role: Structured ngspice execution report.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b06\08_spice_run.json`

```json
{
  "source_format": "pipeline2.0_spice_run",
  "status": "success",
  "netlist_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\b06\\07_netlist.cir",
  "command": [
    "C:\\Users\\m.profilo\\Spice64\\bin\\ngspice_con.exe",
    "-b",
    "07_netlist.cir"
  ],
  "exit_code": 0,
  "stdout_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\b06\\08_ngspice_stdout.txt",
  "stderr_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\b06\\08_ngspice_stderr.txt",
  "tran_raw_csv_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\b06\\08_tran_raw.csv",
  "tran_csv_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\b06\\08_tran.csv",
  "tran_plot_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\b06\\08_tran_plot.png",
  "tran_plot_png_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\pipeline2.0\\b06\\08_tran_plot.png",
  "tran_plot_svg_path": null,
  "message": "ngspice completed successfully."
}
```

### ngspice_stdout

- Step: `08`
- Role: Raw ngspice stdout log.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b06\08_ngspice_stdout.txt`

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
n002                                         9
n003                                         0
n001                                         0
n004                              -1.22429e-16
n006                                   1.28179
n005                                  0.660106
n010                                         0
xoperational_amplifier19_1.namp               0
n009                                         0
n007                                         9
linductor10_1#branch              -2.24208e-44
e.xoperational_amplifier19_1.eamp#branch               0
vbattery2_1#branch                -0.000861821


No. of Data Rows : 5008
Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

No. of Data Rows : 1

Initial Transient Solution
--------------------------

Node                                   Voltage
----                                   -------
n002                                         9
n003                                         0
n001                                         0
n004                              -1.22429e-16
n006                                   1.28179
n005                                  0.660106
n010                                         0
xoperational_amplifier19_1.namp               0
n009                                         0
n007                                         9
linductor10_1#branch              -2.24208e-44
e.xoperational_amplifier19_1.eamp#branch               0
vbattery2_1#branch                -0.000861821


No. of Data Rows : 5008
	Node                                  Voltage
	----                                  -------
	----	-------
	n007                             8.999999e+00
	n009                             0.000000e+00
	xoperational_amplifier19_1.namp   0.000000e+00
	n010                             0.000000e+00
	n005                             6.601064e-01
	n006                             1.281789e+00
	n004                             -1.22429e-16
	n001                             0.000000e+00
	n003                             0.000000e+00
	n002                             9.000000e+00

	Source	Current
	------	-------

	@ddiode7_1[id]                   1.690583e-28
	vbattery2_1#branch               -8.61821e-04
	e.xoperational_amplifier19_1.eamp#branch   0.000000e+00
	linductor10_1#branch             -2.24208e-44

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
     device   qnpn_transistor18_1
      model                2n3904
         ic           0.000765604
         ib           6.21683e-06
         ie          -0.000771821
        vbe              0.659967
        vbc              -0.62098
         gm             0.0291756
        gpi           0.000241841
        gmu           7.02387e-06
         gx                   0.1
         go           1.08417e-05
        cpi           1.52283e-11
        cmu           3.02026e-12
        cbx                     0
       csub                     0

 Capacitor: Fixed capacitor
     device cpolarized_capacitor2 cpolarized_capacitor2 cpolarized_capacitor2
      model                     C                     C                     C
capacitance                0.0001               0.00022                 1e-07
      dtemp                     0                     0                     0
     bv_max                 1e+99                 1e+99                 1e+99
          i          -1.63891e-14          -1.82727e-12          -7.81012e-17
          p          -1.47502e-13          -1.90051e-23          -1.00109e-16

 Capacitor: Fixed capacitor
     device cpolarized_capacitor2 cpolariz
```

> Artifact truncated in this preview. The original file remains available through the manifest path.

### ngspice_stderr

- Step: `08`
- Role: Raw ngspice stderr log.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b06\08_ngspice_stderr.txt`

```text

```

### tran_csv

- Step: `08`
- Role: Clean transient CSV, when .tran data is available.
- Path: `outputs\demo_workspaces\chat_agent_evaluation\web\chat\b06\08_tran.csv`

```csv
time,v(N001),v(N002),v(N003),v(N004),v(N005),v(N006),v(N007),v(N009),v(N010),@ddiode7_1[id]
0.0,0.0,9.0,0.0,-1.22428978e-16,0.66010638,1.28178949,8.99999914,0.0,0.0,1.69058345e-28
1e-08,2.76297551e-27,9.0,4.85135021e-11,1.11022302e-16,0.66010638,1.28178949,8.99999914,4.85137777e-11,3.94173583e-12,-1.54321e-28
2e-08,1.3811441e-26,9.0,7.6229868e-11,2.77555756e-16,0.66010638,1.28178949,8.99999914,7.62305767e-11,6.19371221e-12,-3.8524739e-28
4e-08,4.14068393e-26,9.0,1.16227285e-10,4.4408921e-16,0.66010638,1.28178949,8.99999914,1.16229088e-10,9.44355705e-12,-6.16173779e-28
8e-08,9.32087804e-26,9.0,7.93077571e-11,2.77555756e-16,0.66010638,1.28178949,8.99999914,7.93117814e-11,6.44395648e-12,-3.85247389e-28
1.6e-07,9.41588851e-26,9.0,-4.10095265e-11,-1.66533454e-16,0.66010638,1.28178949,8.99999914,-4.10046319e-11,-3.3317793e-12,2.30926389e-28
3.2e-07,-5.80081227e-26,9.0,-6.28179392e-12,-2.77555756e-16,0.66010638,1.28178949,8.99999914,-6.27904884e-12,-5.10258502e-13,3.84137166e-28
6.4e-07,-2.75324332e-25,9.0,-7.32498395e-12,-2.22044605e-16,0.66010638,1.28178949,8.99999914,-7.32347586e-12,-5.95079541e-13,3.08642001e-28
1.28e-06,-8.77059448e-26,9.0,-1.98985444e-11,-2.77555756e-16,0.66010638,1.28178949,8.99999914,-1.9901986e-11,-1.61692881e-12,3.84137166e-28
2.28e-06,2.68459769e-25,9.0,1.17630225e-11,-2.77555756e-16,0.66010638,1.28178949,8.99999914,1.17572696e-11,9.55457935e-13,3.84137167e-28
3.28e-06,-2.72437992e-25,9.0,5.56156428e-13,-4.4408921e-16,0.66010638,1.28178949,8.99999914,5.53903328e-13,4.50750548e-14,6.15063555e-28
4.28e-06,-1.29048032e-25,9.0,9.64112213e-12,-6.10622664e-16,0.66010638,1.28178949,8.99999914,9.64176599e-12,7.83373366e-13,8.45989945e-28
5.28e-06,2.34439173e-25,9.0,1.58543083e-12,-7.77156117e-16,0.66010638,1.28178949,8.99999914,1.58926404e-12,1.29007915e-13,1.07691633e-27
6.28e-06,-2.88586543e-25,9.0,9.44319854e-12,-9.43689571e-16,0.66010638,1.28178949,8.99999914,9.45016489e-12,7.67608199e-13,1.30784272e-27
7.28e-06,-8.712381e-26,9.0,2.26467008e-12,-1.22124533e-15,0.66010638,1.28178949,8.99999914,2.27496253e-12,1.84519067e-13,1.69420034e-27
8.28e-06,1.45644551e-25,9.0,9.77518822e-12,-1.49880108e-15,0.66010638,1.28178949,8.99999914,9.78890108e-12,7.94919686e-13,2.0783375e-27
9.28e-06,-3.10221045e-25,9.0,3.81518472e-12,-1.72084569e-15,0.66010638,1.28178949,8.99999914,3.83275849e-12,3.10862447e-13,2.3869795e-27
1.028e-05,-8.75354678e-27,9.0,9.39883362e-12,-1.83186799e-15,0.66010638,1.28178949,8.99999914,9.42016137e-12,7.64721619e-13,2.54019028e-27
1.128e-05,1.72634831e-25,9.0,6.59212705e-12,-1.99840144e-15,0.66010638,1.28178949,8.99999914,6.61799769e-12,5.36903855e-13,2.77111667e-27
1.228e-05,-2.23205501e-25,9.0,9.55172134e-12,-1.99840144e-15,0.66010638,1.28178949,8.99999914,9.58217829e-12,7.77600206e-13,2.77111667e-27
1.328e-05,4.74224957e-26,9.0,7.27231046e-12,-2.0539126e-15,0.66010638,1.28178949,8.99999914,7.30754697e-12,5.92637051e-13,2.84883228e-27
1.428e-05,7.65179749e-26,9.0,9.53217794e-12,-2.1649349e-15,0.66010638,1.28178949,8.99999914,9.57218845e-12,7.76489983e-13,3.00204306e-27
1.528e-05,-1.73823029e-25,9.0,4.79636519e-12,-2.10942375e-15,0.66010638,1.28178949,8.99999914,4.84044631e-12,3.91908728e-13,2.92432745e-27
1.628e-05,2.23815968e-25,9.0,1.16065092e-11,-1.94289029e-15,0.66010638,1.28178949,8.99999914,1.16552503e-11,9.45465928e-13,2.69340106e-27
1.728e-05,5.31463458e-26,9.0,7.21971584e-12,-1.88737914e-15,0.66010638,1.28178949,8.99999914,7.27380523e-12,5.89306381e-13,2.61790589e-27
1.828e-05,-2.62697746e-25,9.0,1.10479872e-11,-1.88737914e-15,0.66010638,1.28178949,8.99999914,1.11072663e-11,9.00612918e-13,2.61790589e-27
1.928e-05,2.02222618e-25,9.0,4.90720178e-12,-1.94289029e-15,0.66010638,1.28178949,8.99999914,4.97101358e-12,4.01900735e-13,2.69340106e-27
2.028e-05,3.06129821e-26,9.0,8.21986199e-12,-1.94289029e-15,0.66010638,1.28178949,8.99999914,8.28740307e-12,6.71240841e-13,2.69340106e-27
2.128e-05,-2.84748154e-25,9.0,5.41356757e-12,-1.99840144e-15,0.66010638,1.28178949,8.99999914,5.48498179e-12,4.43423076e-13,2.77111667e-27
2.228e-05,2.13551574e-25,9.0,8.02656174e-12,-2.0539126e-15,0.66010638,1.28178949,8.99999914,8.10179417e-12,6.55919763e-13,2.84883228e-27
2.328e-05,2.47924437e-26,9.0,5.73948691e-12,-2.10942375e-15,0.66010638,1.28178949,8.99999914,5.81863015e-12,4.70290473e-13,2.92432745e-27
2.428e-05,-3.153852e-25,9.0,8.1747625e-12,-2.22044605e-15,0.66010638,1.28178949,8.99999914,8.25785865e-12,6.68354261e-13,3.07975867e-27
2.528e-05,1.95664638e-25,9.0,6.5843925e-12,-2.33146835e-15,0.66010638,1.28178949,8.99999914,6.67168159e-12,5.39346345e-13,3.23296945e-27
2.628e-05,6.76098053e-26,9.0,8.31441895e-12,-2.33146835e-15,0.66010638,1.28178949,8.99999914,8.40594066e-12,6.80122625e-13,3.23296945e-27
2.728e-05,-2.36501221e-25,9.0,6.19938336e-12,-2.22044605e-15,0.66010638,1.28178949,8.99999914,6.29502831e-12,5.08482145e-13,3.07975867e-27
2.828e-05,2.22390983e-25,9.0,7.75740452e-12,-2.22044605e-15,0.66010638,1.28178949,8.99999914,7.85701447e-12,6.35269615e-13,3.07975867e-27
2.928e-05,5.38784678e-26,9.0,6.34205268e-12,-2.22044605e-15,0.66010638,1.28178949,8.99999914,6.44566815e-12,5.20472554e-13,3.07975867e-27
3.028e-05,-2.29446398e-25,9.0,7.55301184e-12,-2.1649349e-15,0.66010638,1.28178949,8.99999914,7.66057477e-12,6.19060359e-13,3.00204306e-27
3.128e-05,1.85138894e-25,9.0,6.32080084e-12,-2.1649349e-15,0.66010638,1.28178949,8.99999914,6.4323052e-12,5.19140286e-13,3.00204306e-27
3.228e-05,5.76268338e-27,9.0,7.35962755e-12,-2.1649349e-15,0.66010638,1.28178949,8.99999914,7.4750184e-12,6.03739281e-13,3.00204306e-27
3.328e-05,-1.71098199e-25,9.0,5.94441477e-12,-2.10942375e-15,0.66010638,1.28178949,8.99999914,6.06358517e-12,4.8894222e-13,2.92432745e-27
3.428e-05,1.88788522e-25,9.0,7.15278056e-12,-2.10942375e-15,0.66010638,1.28178949,8.99999914,7.27567175e-12,5.8730798e-13,2.92432745e-27
3.528e-05,-2.97399004e-26,9.0,6.26225685e-12,-2.1649349e-15,0.66010638,1.28178949,8.99999914,6.38895914e-12,5.15143483e-13,3.00204306e-27
3.628e-05,-1.86485341e-25,9.0,7.12076701e-12,-2.1649349e-15,0.66010638,1.28178949,8.99999914,7.2512713e-12,5.85087534e-13,3.00204306e-27
3.728e-05,2.30321552e-25,9.0,8.86153546e-12,-2.10942375e-15,0.66010638,1.28178949,8.99999914,8.99658017e-12,7.26751992e-13,2.92432745e-27
3.828e-05,4.98039372e-26,9.0,6.92391324e-12,-1.99840144e-15,0.66010638,1.28178949,8.99999914,7.06344246e-12,5.69544412e-13,2.77111667e-27
3.928e-05,-1.9372551e-25,9.0,7.96799387e-12,-1.88737914e-15,0.66010638,1.28178949,8.99999914,8.11175374e-12,6.54587495e-13,2.61790589e-27
4.028e-05,2.00413877e-25,9.0,7.25478981e-12,-1.83186799e-15,0.66010638,1.28178949,8.99999914,7.40287433e-12,5.96855898e-13,2.54019028e-27
4.128e-05,-3.57127211e-26,9.0,5.83961368e-12,-1.94289029e-15,0.66010638,1.28178949,8.99999914,5.9914182e-12,4.82058837e-13,2.69340106e-27
4.228e-05,-2.50671643e-25,9.0,6.87314385e-12,-1.99840144e-15,0.66010638,1.28178949,8.99999914,7.02855995e-12,5.66213743e-13,2.77111667e-27
4.328e-05,2.96926386e-25,9.0,5.46083351e-12,-1.99840144e-15,0.66010638,1.28178949,8.99999914,5.61975358e-12,4.51638726e-13,2.77111667e-27
4.428e-05,-8.52984699e-26,9.0,7.20218226e-12,-2.10942375e-15,0.66010638,1.28178949,8.99999914,7.36469978e-12,5.93303184e-13,2.92432745e-27
4.528e-05,-2.92450697e-25,9.0,8.77078237e-12,-2.10942375e-15,0.66010638,1.28178949,8.99999914,8.93783766e-12,7.20978832e-13,2.92432745e-27
4.628e-05,4.52901414e-25,9.0,6.83319188e-12,-1.99840144e-15,0.66010638,1.28178949,8.99999914,7.00468012e-12,5.63771252e-13,2.77111667e-27
4.728e-05,-6.45521106e-26,9.0,7.87730422e-12,-1.88737914e-15,0.66010638,1.28178949,8.99999914,8.05297158e-12,6.48814336e-13,2.61790589e-27
4.828e-05,-3.3673716e-25,9.0,7.16413186e-12,-1.83186799e-15,0.66010638,1.28178949,8.99999914,7.34407235e-12,5.91082738e-13,2.54019028e-27
4.928e-05,4.42027212e-25,9.0,8.20812851e-12,-1.83186799e-15,0.66010638,1.28178949,8.99999914,8.39243612e-12,6.76125822e-13,2.54019028e-27
5.028e-05,-9.25927086e-26,9.0,6.97022373e-12,-1.83186799e-15,0.66010638,1.28178949,8.99999914,7.15884338e-12,5.75761661e-13,2.54019028e-27
5.128e-05,-3.89585581e-25,9.0,5.55514708e-12,-1.94289029e-15,0.66010638,1.28178949,8.99999914,5.74732507e-12,4.609646e-13,2.69340106e-27
5.228e-05,4.01924439e-25,9.0,6.76364895e-12,-1.99840144e-15,0.66010638,1.28178949,8.99999914,6.9593266e-12,5.5933036e-13,2.77111667e-27
5.328e-05,-3.83613973e-26,9.0,5.35410928e-12,-1.99840144e-15,0.66010638,1.28178949,8.99999914,5.55322947e-12,4.44977388e-13,2.77111667e-27
5.428e-05,-3.50193303e-25,9.0,9.5437069e-12,-1.99840144e-15,0.66010638,1.28178949,8.99999914,9.74705943e-12,7.85593812e-13,2.77111667e-27
5.528e-05,3.81685657e-25,9.0,6.03199591e-12,-2.0539126e-15,0.66010638,1.28178949,8.99999914,6.23977335e-12,5.0048854e-13,2.84883228e-27
5.628e-05,-9.52181996e-26,9.0,6.71571431e-12,-2.1649349e-15,0.66010638,1.28178949,8.99999914,6.92711326e-12,5.56221735e-13,3.00204306e-27
5.728e-05,-3.54609174e-25,9.0,6.17508791e-12,-2.1649349e-15,0.66010638,1.28178949,8.99999914,6.39014902e-12,5.12478948e-13,3.00204306e-27
5.828e-05,4.17581918e-25,9.0,6.85875629e-12,-2.1649349e-15,0.66010638,1.28178949,8.99999914,7.0775202e-12,5.68212144e-13,3.00204306e-27
5.928e-05,-8.00333188e-26,9.0,8.94936085e-12,-2.1649349e-15,0.66010638,1.28178949,8.99999914,9.1726157e-12,7.38298311e-13,3.00204306e-27
6.028e-05,-3.28783296e-25,9.0,7.01170792e-12,-2.1649349e-15,0.66010638,1.28178949,8.99999914,7.23949717e-12,5.81090731e-13,3.00204306e-27
6.128e-05,4.37940713e-25,9.0,8.58037463e-12,-2.10942375e-15,0.66010638,1.28178949,8.99999914,8.81259344e-12,7.08766379e-13,2.92432745e-27
6.228e-05,-2.32381766e-26,9.0,6.6428507e-12,-1.99840144e-15,0.66010638,1.28178949,8.99999914,6.87939429e-12,5.51558799e-13,2.77111667e-27
6.328e-05,-2.90708251e-25,9.0,7.68702958e-12,-1.88737914e-15,0.66010638,1.28178949,8.99999914,7.92764416e-12,6.36601882e-13,2.61790589e-27
6.428e-05,3.51123704e-25,9.0,6.97392374e-12,-1.83186799e-15,0.66010638,1.28178949,8.99999914,7.21870336e-12,5.78870285e-13,2.54019028e-27
6.528e-05,-1.13143716e-25,9.0,5.55884579e-12,-1.94289029e-15,0.66010638,1.28178949,8.99999914,5.80718586e-12,4.64073224e-13,2.69340106e-27
6.628e-05,-2.78144495e-25,9.0,6.24272961e-12,-1.99840144e-15,0.66010638,1.28178949,8.99999914,6.4944224e-12,5.1980642e-13,2.77111667e-27
6.728e-05,3.78296251e-25,9.0,5.53012868e-12,-1.99840144e-15,0.66010638,1.28178949,8.99999914,5.78516603e-12,4.62074823e-13,2.77111667e-27
6.828e-05,-9.3476806e-26,9.0,8.84803588e-12,-1.94289029e-15,0.66010638,1.28178949,8.99999914,9.10715793e-12,7.31859018e-13,2.69340106e-27
6.928e-05,-2.20993879e-25,9.0,5.1644282e-12,-1.88737914e-15,0.66010638,1.28178949,8.99999914,5.42753107e-12,4.32764935e-13,2.61790589e-27
7.028e-05,3.48933673e-25,9.0,9.00434763e-12,-1.88737914e-15,0.66010638,1.28178949,8.99999914,9.27147572e-12,7.4495965e-13,2.61790589e-27
7.128e-05,-2.12901016e-25,9.0,5.8425697e-12,-1.99840144e-15,0.66010638,1.28178949,8.99999914,6.11391566e-12,4.88276086e-13,2.77111667e-27
7.228e-05,-2.26891653e-25,9.0,6.52635432e-12,-2.10942375e-15,0.66010638,1.28178949,8.99999914,6.80121419e-12,5.44009282e-13,2.92432745e-27
7.328e-05,4.19218793e-25,9.0,6.16066637e-12,-2.10942375e-15,0.66010638,1.28178949,8.99999914,6.43913051e-12,5.1447735e-13,2.92432745e-27
7.428e-05,-2.15384284e-25,9.0,8.77613174e-12,-2.10942375e-15,0.66010638,1.28178949,8.99999914,9.05883928e-12,7.27196081e-13,2.92432745e-27
7.528e-05,-2.25615811e-25,9.0,6.48879487e-12,-2.10942375e-15,0.66010638,1.28178949,8.99999914,6.77583904e-12,5.41566791e-13,2.92432745e-27
7.628e-05,5.19445781e-25,9.0,8.05764437e-12,-1.99840144e-15,0.66010638,1.28178949,8.99999914,8.34882105e-12,6.69242439e-13,2.77111667e-27
7.728e-05,-1.99623451e-25,9.0,5.59568642e-12,-1.88737914e-15,0.66010638,1.28178949,8.99999914,5.89074188e-12,4.69402295e-13,2.61790589e-27
7.828e-05,-2.00085844e-25,9.0,7.86433716e-12,-1.77635684e-15,0.66010638,1.28178949,8.99999914,8.1632165e-12,6.53921362e-13,2.46247467e-27
7.928e-05,5.06329113e-25,9.0,5.92706355e-12,-1.72084569e-15,0.66010638,1.28178949,8.99999914,6.2298609e-12,4.96713781e-1
```

> Artifact truncated in this preview. The original file remains available through the manifest path.
