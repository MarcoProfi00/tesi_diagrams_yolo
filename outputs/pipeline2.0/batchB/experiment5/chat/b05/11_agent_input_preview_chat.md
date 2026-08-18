# Agent input preview

This file is a local preview of the evidence that will be provided to the read-only diagnostic agent.
The agent remains read-only: it can inspect base outputs and existing scenario artifacts, but it does not modify files.

## User problem

Alla luce di tutti gli scenari eseguiti, dammi la diagnosi finale del sintomo e spiega quali condizioni devono essere soddisfatte perché si senta il segnale nelle cuffie.

## Circuit

- Batch: `batchB`
- Circuit: `b05`
- Agent mode: `graph_grounded_readonly`

## Technical summary

```json
{
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
}
```

## Image policy

- Included by default: `False`
- Can be requested: `True`
- Path: `data\batchB\b05.jpg`
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
  "best_scenario_id": "scenario_6",
  "best_outcome_status": "resolved_candidate",
  "best_stop_automation": true,
  "ranking_status": "verified_best",
  "interpretation_rule": "If a user asks which scenario resolves the problem, prefer the scenario with outcome_status='resolved_candidate' and stop_automation=true. Partially resolved scenarios without verified expectations are supporting diagnostics and must not be ranked only by changed_count.",
  "scenarios": [
    {
      "scenario_id": "scenario_1",
      "title": "Chiudere lo switch di alimentazione riconosciuto",
      "status": "spice_success",
      "spice_status": "success",
      "outcome_status": "partially_resolved",
      "outcome_label": "Ipotesi diagnostica confermata",
      "outcome_technical_label": "Diagnostic hypothesis confirmed",
      "outcome_reason": "I criteri dichiarati dal test diagnostico sono soddisfatti, ma lo scenario non applica una correzione del sintomo utente.",
      "stop_automation": false,
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
          "v(N004)",
          "v(N003)",
          "i(vbattery2_1#branch)"
        ],
        "unchanged": [
          "v(N002)"
        ],
        "missing": []
      },
      "led_profiles": {},
      "ranking_verified": true,
      "score": 40
    },
    {
      "scenario_id": "scenario_4",
      "title": "Iniettare un segnale sul nodo antenna con alimentazione inserita",
      "status": "spice_success",
      "spice_status": "success",
      "outcome_status": "not_resolved",
      "outcome_label": "Trasferimento del segnale insufficiente",
      "outcome_technical_label": "Signal gain below threshold",
      "outcome_reason": "Il rapporto Vpp uscita/ingresso resta sotto la soglia dichiarata dallo scenario (2e-07 < 0.05).",
      "stop_automation": false,
      "comparison_summary": {
        "requested_count": 2,
        "changed_count": 2,
        "activated_count": 2,
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
        "gain_required": true,
        "gain_available": true,
        "gain_sufficient": false,
        "scenario_gain": 2.0000028778492166e-07,
        "min_gain_ratio": 0.05
      },
      "quantity_summary": {
        "changed": [
          "v(N001)",
          "v(N003,N004)"
        ],
        "unchanged": [],
        "missing": []
      },
      "led_profiles": {},
      "ranking_verified": true,
      "score": 20
    },
    {
      "scenario_id": "scenario_5",
      "title": "Iniettare il segnale direttamente su N005 verso le cuffie",
      "status": "spice_success",
      "spice_status": "success",
      "outcome_status": "partially_resolved",
      "outcome_label": "Ipotesi diagnostica confermata",
      "outcome_technical_label": "Diagnostic hypothesis confirmed",
      "outcome_reason": "I criteri dichiarati dal test diagnostico sono soddisfatti, ma lo scenario non applica una correzione del sintomo utente.",
      "stop_automation": false,
      "comparison_summary": {
        "requested_count": 2,
        "changed_count": 2,
        "activated_count": 2,
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
        "gain_required": true,
        "gain_available": true,
        "gain_sufficient": true,
        "scenario_gain": 22.083438483662764,
        "min_gain_ratio": 0.05
      },
      "quantity_summary": {
        "changed": [
          "v(N005)",
          "v(N003,N004)"
        ],
        "unchanged": [],
        "missing": []
      },
      "led_profiles": {},
      "ranking_verified": true,
      "score": 40
    },
    {
      "scenario_id": "scenario_6",
      "title": "Iniettare su N001 un segnale piu ampio con switch chiuso",
      "status": "spice_success",
      "spice_status": "success",
      "outcome_status": "resolved_candidate",
      "outcome_label": "Criteri di successo soddisfatti",
      "outcome_technical_label": "Candidate resolved",
      "outcome_reason": "Tutti i comportamenti attesi dichiarati dallo scenario sono verificati dagli output SPICE.",
      "stop_automation": true,
      "comparison_summary": {
        "requested_count": 2,
        "changed_count": 2,
        "activated_count": 2,
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
        "gain_required": true,
        "gain_available": true,
        "gain_sufficient": true,
        "scenario_gain": 4.479029628097813,
        "min_gain_ratio": 0.05
      },
      "quantity_summary": {
        "changed": [
          "v(N001)",
          "v(N003,N004)"
        ],
        "unchanged": [],
        "missing": []
      },
      "led_profiles": {},
      "ranking_verified": true,
      "score": 200
    }
  ]
}
```


## Executed scenarios

### scenario_1

- Title: `Chiudere lo switch di alimentazione riconosciuto`
- Status: `spice_success`
- SPICE status: `success`
- Outcome: `partially_resolved`
- Stop automation: `False`
- Comparison: `3/4` changed
- LED profiles: `{}`

#### scenario_definition

- Role: Scenario selected by the user and saved before execution.
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b05\scenarios\scenario_1\scenario.json`

```json
{
  "scenario_id": "scenario_1",
  "title": "Chiudere lo switch di alimentazione riconosciuto",
  "hypothesis": "The open switch switch25.1 may be isolating battery2.1 from the rest of the circuit, leaving the headset branch unpowered.",
  "intent": "diagnostic",
  "actions": [
    {
      "type": "close_switch",
      "target": "switch25.1"
    }
  ],
  "rerun_from": "06",
  "analysis": "op",
  "compare": [
    "v(N002)",
    "v(N004)",
    "v(N003)",
    "i(vbattery2_1#branch)"
  ],
  "expect": {
    "v(N004)": "changed",
    "i(vbattery2_1#branch)": "nonzero"
  }
}
```

#### scenario_status

- Role: Current scenario status, SPICE status and diagnostic outcome.
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b05\scenarios\scenario_1\scenario_status.json`

```json
{
  "status": "spice_success",
  "stage": "scenario_spice_executed",
  "scenario_id": "scenario_1",
  "source": "guided_chat",
  "spice_executed": true,
  "created_or_updated_at": "2026-07-18T19:29:44",
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_1\\run\\08_spice_run.json",
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_1\\scenario_comparison.json",
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
    "status": "partially_resolved",
    "technical_label": "Diagnostic hypothesis confirmed",
    "label": "Ipotesi diagnostica confermata",
    "reason": "I criteri dichiarati dal test diagnostico sono soddisfatti, ma lo scenario non applica una correzione del sintomo utente.",
    "user_message": "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato.",
    "stop_automation": false,
    "confidence": "low",
    "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
  },
  "controlled_scenario_report": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_1\\12_controlled_scenarios.json",
  "executed_scenarios_count": 1,
  "scenario_budget_exhausted": false,
  "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
}
```

#### controlled_scenario_report

- Role: Report produced by the controlled scenario runner.
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b05\scenarios\scenario_1\12_controlled_scenarios.json`

```json
{
  "source_format": "pipeline2.0_controlled_scenario_report",
  "status": "spice_success",
  "scenario_id": "scenario_1",
  "scenario_title": "Chiudere lo switch di alimentazione riconosciuto",
  "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_1",
  "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_1\\run",
  "netlist": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_1\\run\\07_netlist.cir",
  "applied_actions": [
    {
      "status": "applied",
      "type": "close_switch",
      "target": "switch25.1",
      "nodes": [
        "N002",
        "N004"
      ],
      "resistance": "1m",
      "inserted_line": "RSCENARIO_switch25_1 N002 N004 1m",
      "operation": "inserted",
      "spice_executed": false,
      "index": 1
    }
  ],
  "unsupported_actions": [],
  "failed_actions": [],
  "spice_executed": true,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_1\\run\\08_spice_run.json",
  "spice_status": "success",
  "spice_exit_code": 0,
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_1\\scenario_comparison.json",
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
  "created_or_updated_at": "2026-07-18T19:29:44"
}
```

#### scenario_comparison

- Role: Base-vs-scenario comparison used to evaluate the scenario.
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b05\scenarios\scenario_1\scenario_comparison.json`

```json
{
  "source_format": "pipeline2.0_scenario_comparison",
  "scenario_id": "scenario_1",
  "scenario_title": "Chiudere lo switch di alimentazione riconosciuto",
  "scenario_intent": "diagnostic",
  "base_output_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05",
  "scenario_run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_1\\run",
  "base_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\08_ngspice_stdout.txt",
  "scenario_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_1\\run\\08_ngspice_stdout.txt",
  "base_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\08_ngspice_stderr.txt",
  "scenario_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_1\\run\\08_ngspice_stderr.txt",
  "quantities": [
    {
      "quantity": "v(N002)",
      "base_value": -9.0,
      "scenario_value": -9.0,
      "delta": 0.0,
      "change": "unchanged",
      "expectation": null,
      "expectation_met": null,
      "relative_change": 0.0,
      "meaningful_improvement": false,
      "metric": "v(n002)",
      "measurement": "op",
      "base_details": {},
      "scenario_details": {}
    },
    {
      "quantity": "v(N004)",
      "base_value": -3.93119e-24,
      "scenario_value": -8.99999,
      "delta": -8.99999,
      "change": "activated",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 8999990000000.0,
      "meaningful_improvement": false,
      "metric": "v(n004)",
      "measurement": "op",
      "base_details": {},
      "scenario_details": {}
    },
    {
      "quantity": "v(N003)",
      "base_value": -3.93119e-24,
      "scenario_value": -1.55294,
      "delta": -1.55294,
      "change": "activated",
      "expectation": null,
      "expectation_met": null,
      "relative_change": 1552940000000.0,
      "meaningful_improvement": false,
      "metric": "v(n003)",
      "measurement": "op",
      "base_details": {},
      "scenario_details": {}
    },
    {
      "quantity": "i(vbattery2_1#branch)",
      "base_value": 0.0,
      "scenario_value": -0.00568727,
      "delta": -0.00568727,
      "change": "activated",
      "expectation": "nonzero",
      "expectation_met": true,
      "relative_change": 5687270000.0,
      "meaningful_improvement": true,
      "metric": "i(vbattery2_1#branch)",
      "measurement": "op",
      "base_details": {},
      "scenario_details": {}
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
    "status": "partially_resolved",
    "technical_label": "Diagnostic hypothesis confirmed",
    "label": "Ipotesi diagnostica confermata",
    "reason": "I criteri dichiarati dal test diagnostico sono soddisfatti, ma lo scenario non applica una correzione del sintomo utente.",
    "user_message": "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato.",
    "stop_automation": false,
    "confidence": "low",
    "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
  },
  "created_or_updated_at": "2026-07-18T19:29:44"
}
```

### scenario_4

- Title: `Iniettare un segnale sul nodo antenna con alimentazione inserita`
- Status: `spice_success`
- SPICE status: `success`
- Outcome: `not_resolved`
- Stop automation: `False`
- Comparison: `2/2` changed
- LED profiles: `{}`

#### scenario_definition

- Role: Scenario selected by the user and saved before execution.
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b05\scenarios\scenario_4\scenario.json`

```json
{
  "scenario_id": "scenario_4",
  "title": "Iniettare un segnale sul nodo antenna con alimentazione inserita",
  "hypothesis": "With switch25.1 closed, the circuit may still be silent only because the base netlist has no AC excitation at N001; adding a sinusoidal input there should reveal whether useful signal reaches the headset output between N003 and N004.",
  "intent": "diagnostic",
  "actions": [
    {
      "type": "close_switch",
      "target": "switch25.1"
    },
    {
      "type": "add_voltage_source_between_nodes",
      "positive": "N001",
      "negative": "0",
      "value": "SIN(0 100m 1000)"
    }
  ],
  "rerun_from": "06",
  "analysis": "tran",
  "compare": [
    "v(N001)",
    "v(N003,N004)"
  ],
  "expect": {
    "v(N001)": "activated",
    "v(N003,N004)": "changed"
  },
  "gain": {
    "input": "v(N001)",
    "output": "v(N003,N004)",
    "min_ratio": 0.05
  }
}
```

#### scenario_status

- Role: Current scenario status, SPICE status and diagnostic outcome.
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b05\scenarios\scenario_4\scenario_status.json`

```json
{
  "status": "spice_success",
  "stage": "scenario_spice_executed",
  "scenario_id": "scenario_4",
  "source": "guided_chat",
  "spice_executed": true,
  "created_or_updated_at": "2026-07-18T19:31:48",
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_4\\run\\08_spice_run.json",
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_4\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 2,
    "changed_count": 2,
    "activated_count": 2,
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
    "gain_required": true,
    "gain_available": true,
    "gain_sufficient": false,
    "scenario_gain": 2.0000028778492166e-07,
    "min_gain_ratio": 0.05
  },
  "diagnostic_outcome": {
    "status": "not_resolved",
    "technical_label": "Signal gain below threshold",
    "label": "Trasferimento del segnale insufficiente",
    "reason": "Il rapporto Vpp uscita/ingresso resta sotto la soglia dichiarata dallo scenario (2e-07 < 0.05).",
    "user_message": "Lo scenario non ha prodotto un cambiamento utile rispetto alla base.",
    "stop_automation": false,
    "confidence": "low",
    "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
  },
  "controlled_scenario_report": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_4\\12_controlled_scenarios.json",
  "executed_scenarios_count": 2,
  "scenario_budget_exhausted": false,
  "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
}
```

#### controlled_scenario_report

- Role: Report produced by the controlled scenario runner.
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b05\scenarios\scenario_4\12_controlled_scenarios.json`

```json
{
  "source_format": "pipeline2.0_controlled_scenario_report",
  "status": "spice_success",
  "scenario_id": "scenario_4",
  "scenario_title": "Iniettare un segnale sul nodo antenna con alimentazione inserita",
  "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_4",
  "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_4\\run",
  "netlist": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_4\\run\\07_netlist.cir",
  "applied_actions": [
    {
      "status": "applied",
      "type": "close_switch",
      "target": "switch25.1",
      "nodes": [
        "N002",
        "N004"
      ],
      "resistance": "1m",
      "inserted_line": "RSCENARIO_switch25_1 N002 N004 1m",
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
      "value": "SIN(0 100m 1000)",
      "normalized_source_definition": "SIN(0 100m 1000)",
      "normalized_dc_value": null,
      "inserted_line": "VSCENARIO_SUPPLY_N001_0 N001 0 SIN(0 100m 1000)",
      "operation": "inserted",
      "spice_executed": false,
      "index": 2
    }
  ],
  "unsupported_actions": [],
  "failed_actions": [],
  "spice_executed": true,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_4\\run\\08_spice_run.json",
  "spice_status": "success",
  "spice_exit_code": 0,
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_4\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 2,
    "changed_count": 2,
    "activated_count": 2,
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
    "gain_required": true,
    "gain_available": true,
    "gain_sufficient": false,
    "scenario_gain": 2.0000028778492166e-07,
    "min_gain_ratio": 0.05
  },
  "diagnostic_outcome": {
    "status": "not_resolved",
    "technical_label": "Signal gain below threshold",
    "label": "Trasferimento del segnale insufficiente",
    "reason": "Il rapporto Vpp uscita/ingresso resta sotto la soglia dichiarata dallo scenario (2e-07 < 0.05).",
    "user_message": "Lo scenario non ha prodotto un cambiamento utile rispetto alla base.",
    "stop_automation": false,
    "confidence": "low",
    "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
  },
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "created_or_updated_at": "2026-07-18T19:31:48"
}
```

#### scenario_comparison

- Role: Base-vs-scenario comparison used to evaluate the scenario.
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b05\scenarios\scenario_4\scenario_comparison.json`

```json
{
  "source_format": "pipeline2.0_scenario_comparison",
  "scenario_id": "scenario_4",
  "scenario_title": "Iniettare un segnale sul nodo antenna con alimentazione inserita",
  "scenario_intent": "diagnostic",
  "base_output_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05",
  "scenario_run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_4\\run",
  "base_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\08_ngspice_stdout.txt",
  "scenario_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_4\\run\\08_ngspice_stdout.txt",
  "base_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\08_ngspice_stderr.txt",
  "scenario_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_4\\run\\08_ngspice_stderr.txt",
  "quantities": [
    {
      "quantity": "v(N001)",
      "base_value": 2.0620898e-25,
      "scenario_value": 0.199999711,
      "delta": 0.199999711,
      "change": "activated",
      "expectation": "activated",
      "expectation_met": true,
      "relative_change": 199999711000.0,
      "meaningful_improvement": true,
      "metric": "v(n001).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": -1.03104259e-25,
        "max": 1.03104721e-25,
        "mean": -3.96578969441793e-29,
        "vpp": 2.0620898e-25
      },
      "scenario_details": {
        "min": -0.0999998555,
        "max": 0.0999998555,
        "mean": 9.10158181823379e-08,
        "vpp": 0.199999711
      }
    },
    {
      "quantity": "v(N003,N004)",
      "base_value": 1.0000000195414814e-25,
      "scenario_value": 3.999999975690116e-08,
      "delta": 3.999999975690116e-08,
      "change": "activated",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 39999.99975690116,
      "meaningful_improvement": false,
      "metric": "v(n003,n004).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": -1.0000000195414814e-25,
        "max": 0.0,
        "mean": -3.7939297204232894e-28,
        "vpp": 1.0000000195414814e-25
      },
      "scenario_details": {
        "min": 7.44705438,
        "max": 7.44705442,
        "mean": 7.447054398653232,
        "vpp": 3.999999975690116e-08
      }
    }
  ],
  "summary": {
    "requested_count": 2,
    "changed_count": 2,
    "activated_count": 2,
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
    "gain_required": true,
    "gain_available": true,
    "gain_sufficient": false,
    "scenario_gain": 2.0000028778492166e-07,
    "min_gain_ratio": 0.05
  },
  "gain_comparison": {
    "input": "v(N001)",
    "output": "v(N003,N004)",
    "base_gain": null,
    "scenario_gain": 2.0000028778492166e-07,
    "min_ratio": 0.05,
    "available": true,
    "sufficient": false,
    "relative_change": null
  },
  "quality_comparison": null,
  "diagnostic_outcome": {
    "status": "not_resolved",
    "technical_label": "Signal gain below threshold",
    "label": "Trasferimento del segnale insufficiente",
    "reason": "Il rapporto Vpp uscita/ingresso resta sotto la soglia dichiarata dallo scenario (2e-07 < 0.05).",
    "user_message": "Lo scenario non ha prodotto un cambiamento utile rispetto alla base.",
    "stop_automation": false,
    "confidence": "low",
    "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
  },
  "created_or_updated_at": "2026-07-18T19:31:48"
}
```

### scenario_5

- Title: `Iniettare il segnale direttamente su N005 verso le cuffie`
- Status: `spice_success`
- SPICE status: `success`
- Outcome: `partially_resolved`
- Stop automation: `False`
- Comparison: `2/2` changed
- LED profiles: `{}`

#### scenario_definition

- Role: Scenario selected by the user and saved before execution.
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b05\scenarios\scenario_5\scenario.json`

```json
{
  "scenario_id": "scenario_5",
  "title": "Iniettare il segnale direttamente su N005 verso le cuffie",
  "hypothesis": "With switch25.1 closed, injecting a sinusoidal signal directly at N005 should reveal whether the downstream path from N005 to the headset output v(N003,N004) can transfer useful signal.",
  "intent": "diagnostic",
  "actions": [
    {
      "type": "close_switch",
      "target": "switch25.1"
    },
    {
      "type": "add_voltage_source_between_nodes",
      "positive": "N005",
      "negative": "0",
      "value": "SIN(0 100m 1000)"
    }
  ],
  "rerun_from": "06",
  "analysis": "tran",
  "compare": [
    "v(N005)",
    "v(N003,N004)"
  ],
  "expect": {
    "v(N005)": "activated",
    "v(N003,N004)": "changed"
  },
  "gain": {
    "input": "v(N005)",
    "output": "v(N003,N004)",
    "min_ratio": 0.05
  }
}
```

#### scenario_status

- Role: Current scenario status, SPICE status and diagnostic outcome.
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b05\scenarios\scenario_5\scenario_status.json`

```json
{
  "status": "spice_success",
  "stage": "scenario_spice_executed",
  "scenario_id": "scenario_5",
  "source": "guided_chat",
  "spice_executed": true,
  "created_or_updated_at": "2026-07-18T19:35:54",
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_5\\run\\08_spice_run.json",
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_5\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 2,
    "changed_count": 2,
    "activated_count": 2,
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
    "gain_required": true,
    "gain_available": true,
    "gain_sufficient": true,
    "scenario_gain": 22.083438483662764,
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
  "controlled_scenario_report": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_5\\12_controlled_scenarios.json",
  "executed_scenarios_count": 3,
  "scenario_budget_exhausted": false,
  "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
}
```

#### controlled_scenario_report

- Role: Report produced by the controlled scenario runner.
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b05\scenarios\scenario_5\12_controlled_scenarios.json`

```json
{
  "source_format": "pipeline2.0_controlled_scenario_report",
  "status": "spice_success",
  "scenario_id": "scenario_5",
  "scenario_title": "Iniettare il segnale direttamente su N005 verso le cuffie",
  "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_5",
  "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_5\\run",
  "netlist": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_5\\run\\07_netlist.cir",
  "applied_actions": [
    {
      "status": "applied",
      "type": "close_switch",
      "target": "switch25.1",
      "nodes": [
        "N002",
        "N004"
      ],
      "resistance": "1m",
      "inserted_line": "RSCENARIO_switch25_1 N002 N004 1m",
      "operation": "inserted",
      "spice_executed": false,
      "index": 1
    },
    {
      "status": "applied",
      "type": "add_voltage_source_between_nodes",
      "positive": "N005",
      "negative": "0",
      "nodes": [
        "N005",
        "0"
      ],
      "value": "SIN(0 100m 1000)",
      "normalized_source_definition": "SIN(0 100m 1000)",
      "normalized_dc_value": null,
      "inserted_line": "VSCENARIO_SUPPLY_N005_0 N005 0 SIN(0 100m 1000)",
      "operation": "inserted",
      "spice_executed": false,
      "index": 2
    }
  ],
  "unsupported_actions": [],
  "failed_actions": [],
  "spice_executed": true,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_5\\run\\08_spice_run.json",
  "spice_status": "success",
  "spice_exit_code": 0,
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_5\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 2,
    "changed_count": 2,
    "activated_count": 2,
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
    "gain_required": true,
    "gain_available": true,
    "gain_sufficient": true,
    "scenario_gain": 22.083438483662764,
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
  "created_or_updated_at": "2026-07-18T19:35:54"
}
```

#### scenario_comparison

- Role: Base-vs-scenario comparison used to evaluate the scenario.
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b05\scenarios\scenario_5\scenario_comparison.json`

```json
{
  "source_format": "pipeline2.0_scenario_comparison",
  "scenario_id": "scenario_5",
  "scenario_title": "Iniettare il segnale direttamente su N005 verso le cuffie",
  "scenario_intent": "diagnostic",
  "base_output_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05",
  "scenario_run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_5\\run",
  "base_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\08_ngspice_stdout.txt",
  "scenario_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_5\\run\\08_ngspice_stdout.txt",
  "base_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\08_ngspice_stderr.txt",
  "scenario_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_5\\run\\08_ngspice_stderr.txt",
  "quantities": [
    {
      "quantity": "v(N005)",
      "base_value": 3.1542267099999994e-17,
      "scenario_value": 0.1999996904,
      "delta": 0.19999969039999999,
      "change": "activated",
      "expectation": "activated",
      "expectation_met": true,
      "relative_change": 199999690400.0,
      "meaningful_improvement": true,
      "metric": "v(n005).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": -1.22428978e-16,
        "max": -9.08867109e-17,
        "mean": -9.089322804333067e-17,
        "vpp": 3.1542267099999994e-17
      },
      "scenario_details": {
        "min": -0.0999998452,
        "max": 0.0999998452,
        "mean": 1.0664350802713211e-07,
        "vpp": 0.1999996904
      }
    },
    {
      "quantity": "v(N003,N004)",
      "base_value": 1.0000000195414814e-25,
      "scenario_value": 4.416680859699999,
      "delta": 4.416680859699999,
      "change": "activated",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 4416680859699.999,
      "meaningful_improvement": false,
      "metric": "v(n003,n004).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": -1.0000000195414814e-25,
        "max": 0.0,
        "mean": -3.7939297204232894e-28,
        "vpp": 1.0000000195414814e-25
      },
      "scenario_details": {
        "min": 4.491745580000001,
        "max": 8.9084264397,
        "mean": 7.436321795046006,
        "vpp": 4.416680859699999
      }
    }
  ],
  "summary": {
    "requested_count": 2,
    "changed_count": 2,
    "activated_count": 2,
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
    "gain_required": true,
    "gain_available": true,
    "gain_sufficient": true,
    "scenario_gain": 22.083438483662764,
    "min_gain_ratio": 0.05
  },
  "gain_comparison": {
    "input": "v(N005)",
    "output": "v(N003,N004)",
    "base_gain": null,
    "scenario_gain": 22.083438483662764,
    "min_ratio": 0.05,
    "available": true,
    "sufficient": true,
    "relative_change": null
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
  "created_or_updated_at": "2026-07-18T19:35:54"
}
```

### scenario_6

- Title: `Iniettare su N001 un segnale piu ampio con switch chiuso`
- Status: `spice_success`
- SPICE status: `success`
- Outcome: `resolved_candidate`
- Stop automation: `True`
- Comparison: `2/2` changed
- LED profiles: `{}`

#### scenario_definition

- Role: Scenario selected by the user and saved before execution.
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b05\scenarios\scenario_6\scenario.json`

```json
{
  "scenario_id": "scenario_6",
  "title": "Iniettare su N001 un segnale piu ampio con switch chiuso",
  "hypothesis": "With switch25.1 closed, the previous stimulus at N001 may have been too small to drive useful transfer through diode7.1; a larger sinusoidal input at N001 should test whether a usable signal can then reach v(N003,N004).",
  "intent": "correction",
  "actions": [
    {
      "type": "close_switch",
      "target": "switch25.1"
    },
    {
      "type": "add_voltage_source_between_nodes",
      "positive": "N001",
      "negative": "0",
      "value": "SIN(0 1 1000)"
    }
  ],
  "rerun_from": "06",
  "analysis": "tran",
  "compare": [
    "v(N001)",
    "v(N003,N004)"
  ],
  "expect": {
    "v(N001)": "activated",
    "v(N003,N004)": "changed"
  },
  "gain": {
    "input": "v(N001)",
    "output": "v(N003,N004)",
    "min_ratio": 0.05
  }
}
```

#### scenario_status

- Role: Current scenario status, SPICE status and diagnostic outcome.
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b05\scenarios\scenario_6\scenario_status.json`

```json
{
  "status": "spice_success",
  "stage": "scenario_spice_executed",
  "scenario_id": "scenario_6",
  "source": "guided_chat",
  "spice_executed": true,
  "created_or_updated_at": "2026-07-18T19:39:15",
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_6\\run\\08_spice_run.json",
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_6\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 2,
    "changed_count": 2,
    "activated_count": 2,
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
    "gain_required": true,
    "gain_available": true,
    "gain_sufficient": true,
    "scenario_gain": 4.479029628097813,
    "min_gain_ratio": 0.05
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
  "controlled_scenario_report": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_6\\12_controlled_scenarios.json",
  "executed_scenarios_count": 4,
  "scenario_budget_exhausted": false,
  "next_step": "Ci sono gia evidenze forti per fermarsi qui e passare alla conclusione diagnostica."
}
```

#### controlled_scenario_report

- Role: Report produced by the controlled scenario runner.
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b05\scenarios\scenario_6\12_controlled_scenarios.json`

```json
{
  "source_format": "pipeline2.0_controlled_scenario_report",
  "status": "spice_success",
  "scenario_id": "scenario_6",
  "scenario_title": "Iniettare su N001 un segnale piu ampio con switch chiuso",
  "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_6",
  "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_6\\run",
  "netlist": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_6\\run\\07_netlist.cir",
  "applied_actions": [
    {
      "status": "applied",
      "type": "close_switch",
      "target": "switch25.1",
      "nodes": [
        "N002",
        "N004"
      ],
      "resistance": "1m",
      "inserted_line": "RSCENARIO_switch25_1 N002 N004 1m",
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
      "value": "SIN(0 1 1000)",
      "normalized_source_definition": "SIN(0 1 1000)",
      "normalized_dc_value": null,
      "inserted_line": "VSCENARIO_SUPPLY_N001_0 N001 0 SIN(0 1 1000)",
      "operation": "inserted",
      "spice_executed": false,
      "index": 2
    }
  ],
  "unsupported_actions": [],
  "failed_actions": [],
  "spice_executed": true,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_6\\run\\08_spice_run.json",
  "spice_status": "success",
  "spice_exit_code": 0,
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_6\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 2,
    "changed_count": 2,
    "activated_count": 2,
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
    "gain_required": true,
    "gain_available": true,
    "gain_sufficient": true,
    "scenario_gain": 4.479029628097813,
    "min_gain_ratio": 0.05
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
  "created_or_updated_at": "2026-07-18T19:39:15"
}
```

#### scenario_comparison

- Role: Base-vs-scenario comparison used to evaluate the scenario.
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b05\scenarios\scenario_6\scenario_comparison.json`

```json
{
  "source_format": "pipeline2.0_scenario_comparison",
  "scenario_id": "scenario_6",
  "scenario_title": "Iniettare su N001 un segnale piu ampio con switch chiuso",
  "scenario_intent": "correction",
  "base_output_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05",
  "scenario_run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_6\\run",
  "base_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\08_ngspice_stdout.txt",
  "scenario_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_6\\run\\08_ngspice_stdout.txt",
  "base_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\08_ngspice_stderr.txt",
  "scenario_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\scenarios\\scenario_6\\run\\08_ngspice_stderr.txt",
  "quantities": [
    {
      "quantity": "v(N001)",
      "base_value": 2.0620898e-25,
      "scenario_value": 1.99999711,
      "delta": 1.99999711,
      "change": "activated",
      "expectation": "activated",
      "expectation_met": true,
      "relative_change": 1999997110000.0,
      "meaningful_improvement": true,
      "metric": "v(n001).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": -1.03104259e-25,
        "max": 1.03104721e-25,
        "mean": -3.96578969441793e-29,
        "vpp": 2.0620898e-25
      },
      "scenario_details": {
        "min": -0.999998555,
        "max": 0.999998555,
        "mean": 9.101581818233791e-07,
        "vpp": 1.99999711
      }
    },
    {
      "quantity": "v(N003,N004)",
      "base_value": 1.0000000195414814e-25,
      "scenario_value": 8.9580463118,
      "delta": 8.9580463118,
      "change": "activated",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 8958046311800.0,
      "meaningful_improvement": false,
      "metric": "v(n003,n004).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": -1.0000000195414814e-25,
        "max": 0.0,
        "mean": -3.7939297204232894e-28,
        "vpp": 1.0000000195414814e-25
      },
      "scenario_details": {
        "min": 2.999999892949745e-08,
        "max": 8.9580463418,
        "mean": 2.8694904120307463,
        "vpp": 8.9580463118
      }
    }
  ],
  "summary": {
    "requested_count": 2,
    "changed_count": 2,
    "activated_count": 2,
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
    "gain_required": true,
    "gain_available": true,
    "gain_sufficient": true,
    "scenario_gain": 4.479029628097813,
    "min_gain_ratio": 0.05
  },
  "gain_comparison": {
    "input": "v(N001)",
    "output": "v(N003,N004)",
    "base_gain": null,
    "scenario_gain": 4.479029628097813,
    "min_ratio": 0.05,
    "available": true,
    "sufficient": true,
    "relative_change": null
  },
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
  "created_or_updated_at": "2026-07-18T19:39:15"
}
```


## Loaded artifacts

### graph

- Step: `01`
- Role: Graph JSON copied from Pipeline 1.0.
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b05\01_graph.json`

```json
{
  "image_id": "b05",
  "image_name": "b05.jpg",
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
          "relative_position": "left"
        },
        {
          "terminal_id": "polarized_capacitor20.2_negative",
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
      "component_id": "npn_transistor18.1",
      "instance_id": "18.1",
      "class_name": "PNP_Transistor",
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
      "component_id": "npn_transistor18.2",
      "instance_id": "18.2",
      "class_name": "PNP_Transistor",
      "terminals": [
        {
          "terminal_id": "npn_transistor18.2_B",
          "name": "B",
          "relative_position": "left"
        },
        {
          "terminal_id": "npn_transistor18.2_C",
          "name": "C",
          "relative_position": "top"
        },
        {
          "terminal_id": "npn_transistor18.2_E",
          "name": "E",
          "relative_position": "bottom"
        }
      ]
    },
    {
      "component_id": "battery2.1",
      "instance_id": "2.1",
      "class_name": "Battery",
      "terminals": [
        {
          "terminal_id": "battery2.1_positive",
          "name": "positive",
          "relative_position": "left"
        },
        {
          "terminal_id": "battery2.1_negative",
          "name": "negative",
          "relative_position": "right"
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
      "component_id": "breaker3.1",
      "instance_id": "3.1",
      "class_name": "Breaker",
      "terminals": [
        {
          "terminal_id": "breaker3.1_t1",
          "name": "t1",
          "relative_position": "left"
        },
        {
          "terminal_id": "breaker3.1_t2",
          "name": "t2",
          "relative_position": "left"
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
      "switch25.1_t1"
    ],
    "battery2.1_positive": [
      "gnd9.1_t1",
      "inductor10.1_t2",
      "npn_transistor18.1_E",
      "npn_transistor18.2_E",
      "polarized_capacitor20.1_negative"
    ],
    "breaker3.1_t1": [
      "npn_transistor18.2_C",
      "polarized_capacitor20.4_positive"
    ],
    "breaker3.1_t2": [
      "polarized_capacitor20.4_negative",
      "resistor22.1_t2",
      "resistor22.2_t2",
      "resistor22.3_t2",
      "switch25.1_t2"
    ],
    "diode7.1_anode": [
      "antenna1.1_t1",
      "inductor10.1_t1",
      "polarized_capacitor20.1_positive"
    ],
    "diode7.1_cathode": [
      "polarized_capacitor20.2_positive"
    ],
    "gnd9.1_t1": [
      "battery2.1_positive",
      "inductor10.1_t2",
      "npn_transistor18.1_E",
      "npn_transistor18.2_E",
      "polarized_capacitor20.1_negative"
    ],
    "inductor10.1_t1": [
      "antenna1.1_t1",
      "diode7.1_anode",
      "polarized_capacitor20.1_positive"
    ],
    "inductor10.1_t2": [
      "battery2.1_positive",
      "gnd9.1_t1",
      "npn_transistor18.1_E",
      "npn_transistor18.2_E",
      "polarized_capacitor20.1_negative"
    ],
    "npn_transistor18.1_B": [
      "polarized_capacitor20.2_negative",
      "resistor22.1_t1"
    ],
    "npn_transistor18.1_C": [
      "polarized_capacitor20.3_positive",
      "resistor22.2_t1"
    ],
    "npn_transistor18.1_E": [
      "battery2.1_positive",
      "gnd9.1_t1",
      "inductor10.1_t2",
      "npn_transistor18.2_E",
      "polarized_capacitor20.1_negative"
    ],
    "npn_transistor18.2_B": [
      "polarized_capacitor20.3_negative",
      "resistor22.3_t1"
    ],
    "npn_transistor18.2_C": [
      "breaker3.1_t1",
      "polarized_capacitor20.4_positive"
    ],
    "npn_transistor18.2_E": [
      "battery2.1_positive",
      "gnd9.1_t1",
      "inductor10.1_t2",
      "npn_transistor18.1_E",
      "polarized_capacitor20.1_negative"
    ],
    "polarized_capacitor20.1_negative": [
      "battery2.1_positive",
      "gnd9.1_t1",
      "inductor10.1_t2",
      "npn_transistor18.1_E",
      "npn_transistor18.2_E"
    ],
    "polarized_capacitor20.1_positive": [
      "antenna1.1_t1",
      "diode7.1_anode",
      "inductor10.1_t1"
    ],
    "polarized_capacitor20.2_negative": [
      "npn_transistor18.1_B",
      "resistor22.1_t1"
    ],
    "polarized_capacitor20.2_positive": [
      "diode7.1_cathode"
    ],
    "polarized_capacitor20.3_negative": [
      "npn_transistor18.2_B",
      "resistor22.3_t1"
    ],
    "polarized_capacitor20.3_positive": [
      "npn_transistor18.1_C",
      "resistor22.2_t1"
    ],
    "polarized_capacitor20.4_negative": [
      "breaker3.1_t2",
      "resistor22.1_t2",
      "resistor22.2_t2",
      "resistor22.3_t2",
      "switch25.1_t2"
    ],
    "polarized_capacitor20.4_positive": [
      "breaker3.1_t1",
      "npn_transistor18.2_C"
    ],
    "resistor22.1_t1": [
      "npn_transistor18.1_B",
      "polarized_capacitor20.2_negative"
    ],
    "resistor22.1_t2": [
      "breaker3.1_t2",
      "polarized_capacitor20.4_negative",
      "resistor22.2_t2",
      "resistor22.3_t2",
      "switch25.1_t2"
    ],
    "resistor22.2_t1": [
      "npn_transistor18.1_C",
      "polarized_capacitor20.3_positive"
    ],
    "resistor22.2_t2": [
      "breaker3.1_t2",
      "polarized_capacitor20.4_negative",
      "resistor22.1_t2",
      "resistor22.3_t2",
      "switch25.1_t2"
    ],
    "resistor22.3_t1": [
      "npn_transistor18.2_B",
      "polarized_capacitor20.3_negative"
    ],
    "resistor22.3_t2": [
      "breaker3.1_t2",
      "polarized_capacitor20.4_negative",
      "resistor22.1_t2",
      "resistor22.2_t2",
      "switch25.1_t2"
    ],
    "switch25.1_t1": [
      "battery2.1_negative"
    ],
    "switch25.1_t2": [
      "breaker3.1_t2",
      "polarized_capacitor20.4_negative",
      "resistor22.1_t2",
      "resistor22.2_t2",
      "resistor22.3_t2"
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
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b05\03_node_map.json`

```json
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

### values_bound

- Step: `04`
- Role: Values and labels bound to graph components.
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b05\04_values_bound.json`

```json
{
  "circuit_id": "b05",
  "source_format": "pipeline2.0_values_bound",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_manual_values\\batchB\\b05_values.yaml",
  "supplies": {},
  "components": {
    "antenna1.1": {
      "class_name": "Antenna",
      "terminal_nodes": {
        "t1": "N001"
      },
      "value_data": {
        "source": "graph_json_external_input",
        "label_text": "Antenna esterna; nessuna sorgente AC nella base run",
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
        "positive": "0",
        "negative": "N002"
      },
      "value_data": {
        "type": "dc",
        "value": 9,
        "unit": "V",
        "source": "manual_assumption_battery_voltage",
        "label_text": "B1 assunta: 9 V"
      },
      "status": "bound"
    },
    "breaker3.1": {
      "class_name": "Breaker",
      "terminal_nodes": {
        "t1": "N003",
        "t2": "N004"
      },
      "value_data": {
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
        }
      },
      "status": "bound"
    },
    "diode7.1": {
      "class_name": "Diode",
      "terminal_nodes": {
        "anode": "N001",
        "cathode": "N005"
      },
      "value_data": {
        "model": "D_GENERIC",
        "source": "manual_spice_generic_detector_diode",
        "label_text": "CR1; modello diodo SPICE generico"
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
        "value": 0.00025,
        "unit": "H",
        "source": "manual_assumption_am_tuning_model",
        "label_text": "L1 assunta: 250 uH"
      },
      "status": "bound"
    },
    "npn_transistor18.1": {
      "class_name": "PNP_Transistor",
      "terminal_nodes": {
        "B": "N006",
        "C": "N007",
        "E": "0"
      },
      "value_data": {
        "model": "PNP_GENERIC",
        "source": "manual_validation_pnp_from_image",
        "label_text": "Q1 PNP"
      },
      "status": "bound"
    },
    "npn_transistor18.2": {
      "class_name": "PNP_Transistor",
      "terminal_nodes": {
        "B": "N008",
        "C": "N003",
        "E": "0"
      },
      "value_data": {
        "model": "PNP_GENERIC",
        "source": "manual_validation_pnp_from_image",
        "label_text": "Q2 PNP"
      },
      "status": "bound"
    },
    "polarized_capacitor20.1": {
      "class_name": "Polarized_Capacitor",
      "terminal_nodes": {
        "positive": "N001",
        "negative": "0"
      },
      "value_data": {
        "value": 375,
        "unit": "pf",
        "source": "manual_from_image_range_midpoint",
        "label_text": "C1 variabile 250-500 pF; base run a 375 pF",
        "viewer_override": {
          "visual_class": "variable_polarized_capacitor",
          "label": "C1",
          "display_value": "375 pF"
        }
      },
      "status": "bound"
    },
    "polarized_capacitor20.2": {
      "class_name": "Polarized_Capacitor",
      "terminal_nodes": {
        "positive": "N005",
        "negative": "N006"
      },
      "value_data": {
        "value": 0.022,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C2 0.022 uF"
      },
      "status": "bound"
    },
    "polarized_capacitor20.3": {
      "class_name": "Polarized_Capacitor",
      "terminal_nodes": {
        "positive": "N007",
        "negative": "N008"
      },
      "value_data": {
        "value": 0.022,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C3 0.022 uF"
      },
      "status": "bound"
    },
    "polarized_capacitor20.4": {
      "class_name": "Polarized_Capacitor",
      "terminal_nodes": {
        "positive": "N003",
        "negative": "N004"
      },
      "value_data": {
        "value": 0.001,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C4 0.001 uF"
      },
      "status": "bound"
    },
    "resistor22.1": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N006",
        "t2": "N004"
      },
      "value_data": {
        "value": 220,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R1 220 kohm"
      },
      "status": "bound"
    },
    "resistor22.2": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N007",
        "t2": "N004"
      },
      "value_data": {
        "value": 4.7,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R2 4.7 kohm"
      },
      "status": "bound"
    },
    "resistor22.3": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N008",
        "t2": "N004"
      },
      "value_data": {
        "value": 220,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R3 220 kohm"
      },
      "status": "bound"
    },
    "switch25.1": {
      "class_name": "Switch",
      "terminal_nodes": {
        "t1": "N002",
        "t2": "N004"
      },
      "value_data": {
        "state": "open",
        "state_source": "graph_json_state",
        "state_confidence": 0.95,
        "source": "graph_json_state_validated_from_image",
        "label_text": "S1 aperto"
      },
      "status": "bound"
    }
  },
  "nodes": {},
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
    "components_total": 16,
    "bound_components": 14,
    "missing_components": 0,
    "not_required_components": 1,
    "unsupported_components": 1,
    "supplies_count": 0,
    "manual_nodes_count": 0
  }
}
```

### component_rules

- Step: `06`
- Role: SPICE conversion rules for each component.
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b05\06_component_rules.json`

```json
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

### netlist

- Step: `07`
- Role: Generated SPICE netlist.
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b05\07_netlist.cir`

```spice
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

### spice_emit_report

- Step: `07`
- Role: Report of emitted, skipped and warning components.
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b05\07_spice_emit_report.json`

```json
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

### spice_run

- Step: `08`
- Role: Structured ngspice execution report.
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b05\08_spice_run.json`

```json
{
  "source_format": "pipeline2.0_spice_run",
  "status": "success",
  "netlist_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\07_netlist.cir",
  "command": [
    "C:\\Users\\m.profilo\\Spice64\\bin\\ngspice_con.exe",
    "-b",
    "07_netlist.cir"
  ],
  "exit_code": 0,
  "stdout_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\08_ngspice_stdout.txt",
  "stderr_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\08_ngspice_stderr.txt",
  "tran_raw_csv_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\08_tran_raw.csv",
  "tran_csv_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\08_tran.csv",
  "tran_plot_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\08_tran_plot.png",
  "tran_plot_png_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\pipeline2.0\\batchB\\experiment5\\chat\\b05\\08_tran_plot.png",
  "tran_plot_svg_path": null,
  "message": "ngspice completed successfully."
}
```

### ngspice_stdout

- Step: `08`
- Role: Raw ngspice stdout log.
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b05\08_ngspice_stdout.txt`

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
          i           3
```

> Artifact truncated in this preview. The original file remains available through the manifest path.

### ngspice_stderr

- Step: `08`
- Role: Raw ngspice stderr log.
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b05\08_ngspice_stderr.txt`

```text

```

### tran_csv

- Step: `08`
- Role: Clean transient CSV, when .tran data is available.
- Path: `outputs\pipeline2.0\batchB\experiment5\chat\b05\08_tran.csv`

```csv
time,v(N001),v(N002),v(N003),v(N004),v(N005),v(N006),v(N007),v(N008)
0.0,0.0,-9.0,-3.93119182e-24,-3.93119181e-24,-1.22428978e-16,-3.9311901e-24,-3.93119185e-24,-3.9311901e-24
1e-08,-3.34577667e-27,-9.0,3.13407682e-17,3.13407682e-17,-9.10881918e-17,3.13407821e-17,3.13407679e-17,3.13407679e-17
2e-08,-6.70504326e-27,-9.0,3.15144262e-17,3.15144262e-17,-9.09145338e-17,3.15144401e-17,3.15144259e-17,3.15144259e-17
4e-08,-1.34032421e-26,-9.0,3.15327059e-17,3.15327059e-17,-9.08962541e-17,3.15327199e-17,3.15327056e-17,3.15327056e-17
8e-08,-2.65880426e-26,-9.0,3.15418458e-17,3.15418458e-17,-9.08871142e-17,3.15418598e-17,3.15418455e-17,3.15418455e-17
1.6e-07,-5.12871548e-26,-9.0,3.15414314e-17,3.15414314e-17,-9.08875286e-17,3.15414453e-17,3.15414311e-17,3.15414311e-17
3.2e-07,-8.84862765e-26,-9.0,3.15412242e-17,3.15412242e-17,-9.08877358e-17,3.15412381e-17,3.15412239e-17,3.15412239e-17
6.4e-07,-9.3975889e-26,-9.0,3.15422098e-17,3.15422098e-17,-9.08867501e-17,3.15422238e-17,3.15422095e-17,3.15422095e-17
1.28e-06,4.65242492e-26,-9.0,3.15421581e-17,3.15421581e-17,-9.08868019e-17,3.1542172e-17,3.15421578e-17,3.15421578e-17
2.28e-06,6.08111578e-26,-9.0,3.15419635e-17,3.15419635e-17,-9.08869965e-17,3.15419774e-17,3.15419632e-17,3.15419632e-17
3.28e-06,-1.01807183e-25,-9.0,3.15419634e-17,3.15419634e-17,-9.08869966e-17,3.15419773e-17,3.15419631e-17,3.15419631e-17
4.28e-06,3.17409264e-26,-9.0,3.15421062e-17,3.15421062e-17,-9.08868537e-17,3.15421202e-17,3.1542106e-17,3.15421059e-17
5.28e-06,7.29517756e-26,-9.0,3.15419634e-17,3.15419634e-17,-9.08869965e-17,3.15419774e-17,3.15419632e-17,3.15419631e-17
6.28e-06,-9.80607223e-26,-9.0,3.15421062e-17,3.15421062e-17,-9.08868537e-17,3.15421201e-17,3.15421059e-17,3.15421059e-17
7.28e-06,1.61944076e-26,-9.0,3.15421062e-17,3.15421062e-17,-9.08868537e-17,3.15421202e-17,3.15421059e-17,3.15421059e-17
8.28e-06,8.33384414e-26,-9.0,3.15419634e-17,3.15419634e-17,-9.08869965e-17,3.15419774e-17,3.15419631e-17,3.15419631e-17
9.28e-06,-9.19566069e-26,-9.0,3.15421062e-17,3.15421062e-17,-9.08868537e-17,3.15421201e-17,3.15421059e-17,3.15421059e-17
1.028e-05,2.58546048e-28,-9.0,3.15421062e-17,3.15421062e-17,-9.08868537e-17,3.15421201e-17,3.15421059e-17,3.15421059e-17
1.128e-05,9.17214729e-26,-9.0,3.15419634e-17,3.15419634e-17,-9.08869965e-17,3.15419773e-17,3.15419631e-17,3.15419631e-17
1.228e-05,-8.36416831e-26,-9.0,3.15421062e-17,3.15421062e-17,-9.08868537e-17,3.15421201e-17,3.15421059e-17,3.15421058e-17
1.328e-05,-1.56835071e-26,-9.0,3.15421062e-17,3.15421062e-17,-9.08868537e-17,3.15421201e-17,3.15421059e-17,3.15421059e-17
1.428e-05,9.78993247e-26,-9.0,3.15419634e-17,3.15419634e-17,-9.08869965e-17,3.15419773e-17,3.15419631e-17,3.15419631e-17
1.528e-05,-7.33158588e-26,-9.0,3.15421062e-17,3.15421062e-17,-9.08868537e-17,3.15421201e-17,3.15421059e-17,3.15421058e-17
1.628e-05,-3.12483999e-26,-9.0,3.1542249e-17,3.1542249e-17,-9.08867109e-17,3.15422629e-17,3.15422487e-17,3.15422486e-17
1.728e-05,1.01723383e-25,-9.0,3.15419634e-17,3.15419634e-17,-9.08869965e-17,3.15419773e-17,3.15419631e-17,3.1541963e-17
1.828e-05,-6.12274546e-26,-9.0,3.15421061e-17,3.15421061e-17,-9.08868537e-17,3.15421201e-17,3.15421059e-17,3.15421058e-17
1.928e-05,-4.60619683e-26,-9.0,3.15421061e-17,3.15421061e-17,-9.08868537e-17,3.15421201e-17,3.15421059e-17,3.15421058e-17
2.028e-05,1.03101879e-25,-9.0,3.15419634e-17,3.15419634e-17,-9.08869965e-17,3.15419773e-17,3.15419631e-17,3.1541963e-17
2.128e-05,-4.76669206e-26,-9.0,3.15422489e-17,3.15422489e-17,-9.08867109e-17,3.15422629e-17,3.15422486e-17,3.15422486e-17
2.228e-05,-5.9768263e-26,-9.0,3.15421061e-17,3.15421061e-17,-9.08868537e-17,3.15421201e-17,3.15421058e-17,3.15421058e-17
2.328e-05,1.02001541e-25,-9.0,3.15419633e-17,3.15419633e-17,-9.08869965e-17,3.15419773e-17,3.15419631e-17,3.1541963e-17
2.428e-05,-3.29603704e-26,-9.0,3.15421061e-17,3.15421061e-17,-9.08868537e-17,3.154212e-17,3.15421058e-17,3.15421058e-17
2.528e-05,-7.20374237e-26,-9.0,3.15422489e-17,3.15422489e-17,-9.08867109e-17,3.15422628e-17,3.15422486e-17,3.15422485e-17
2.628e-05,9.84488972e-26,-9.0,3.15421061e-17,3.15421061e-17,-9.08868537e-17,3.15421201e-17,3.15421058e-17,3.15421058e-17
2.728e-05,-1.74616458e-26,-9.0,3.15421061e-17,3.15421061e-17,-9.08868537e-17,3.154212e-17,3.15421058e-17,3.15421057e-17
2.828e-05,-8.25746536e-26,-9.0,3.15421061e-17,3.15421061e-17,-9.08868537e-17,3.154212e-17,3.15421058e-17,3.15421057e-17
2.928e-05,9.25295127e-26,-9.0,3.15421061e-17,3.15421061e-17,-9.08868537e-17,3.15421201e-17,3.15421058e-17,3.15421057e-17
3.028e-05,-1.54301316e-27,-9.0,3.15422489e-17,3.15422489e-17,-9.08867109e-17,3.15422628e-17,3.15422486e-17,3.15422485e-17
3.128e-05,-9.11267934e-26,-9.0,3.15421061e-17,3.15421061e-17,-9.08868537e-17,3.154212e-17,3.15421058e-17,3.15421057e-17
3.228e-05,8.43854086e-26,-9.0,3.15419633e-17,3.15419633e-17,-9.08869965e-17,3.15419772e-17,3.1541963e-17,3.15419629e-17
3.328e-05,1.44128258e-26,-9.0,3.15421061e-17,3.15421061e-17,-9.08868537e-17,3.154212e-17,3.15421058e-17,3.15421057e-17
3.428e-05,-9.74878334e-26,-9.0,3.15422488e-17,3.15422488e-17,-9.08867109e-17,3.15422628e-17,3.15422486e-17,3.15422485e-17
3.528e-05,7.42124371e-26,-9.0,3.15421061e-17,3.15421061e-17,-9.08868537e-17,3.154212e-17,3.15421058e-17,3.15421057e-17
3.628e-05,3.00219094e-26,-9.0,3.15421061e-17,3.15421061e-17,-9.08868537e-17,3.154212e-17,3.15421058e-17,3.15421057e-17
3.728e-05,-1.01505062e-25,-9.0,3.1542106e-17,3.1542106e-17,-9.08868538e-17,3.154212e-17,3.15421057e-17,3.15421056e-17
3.828e-05,6.22553475e-26,-9.0,3.15419632e-17,3.15419633e-17,-9.08869965e-17,3.15419772e-17,3.1541963e-17,3.15419629e-17
3.928e-05,4.49093834e-26,-9.0,3.15422489e-17,3.15422489e-17,-9.08867109e-17,3.15422628e-17,3.15422486e-17,3.15422485e-17
4.028e-05,-1.03082008e-25,-9.0,3.1542106e-17,3.1542106e-17,-9.08868538e-17,3.15421199e-17,3.15421057e-17,3.15421056e-17
4.128e-05,4.88013686e-26,-9.0,3.15419632e-17,3.15419632e-17,-9.08869965e-17,3.15419772e-17,3.15419629e-17,3.15419628e-17
4.228e-05,5.87171673e-26,-9.0,3.1542106e-17,3.1542106e-17,-9.08868537e-17,3.154212e-17,3.15421057e-17,3.15421056e-17
4.328e-05,-1.02180467e-25,-9.0,3.15422488e-17,3.15422488e-17,-9.08867109e-17,3.15422627e-17,3.15422485e-17,3.15422484e-17
4.428e-05,3.41740546e-26,-9.0,3.15419632e-17,3.15419632e-17,-9.08869965e-17,3.15419771e-17,3.15419629e-17,3.15419628e-17
4.528e-05,7.11130931e-26,-9.0,3.1542106e-17,3.1542106e-17,-9.08868537e-17,3.154212e-17,3.15421057e-17,3.15421056e-17
4.628e-05,-9.88222289e-26,-9.0,3.1542106e-17,3.1542106e-17,-9.08868537e-17,3.15421199e-17,3.15421057e-17,3.15421056e-17
4.728e-05,1.87252047e-26,-9.0,3.15419632e-17,3.15419632e-17,-9.08869965e-17,3.15419771e-17,3.15419629e-17,3.15419628e-17
4.828e-05,8.17994075e-26,-9.0,3.15422488e-17,3.15422488e-17,-9.08867109e-17,3.15422627e-17,3.15422485e-17,3.15422484e-17
4.928e-05,-9.30883225e-26,-9.0,3.15419631e-17,3.15419631e-17,-9.08869966e-17,3.15419771e-17,3.15419629e-17,3.15419627e-17
5.028e-05,2.82619621e-27,-9.0,3.15419632e-17,3.15419632e-17,-9.08869965e-17,3.15419771e-17,3.15419629e-17,3.15419627e-17
5.128e-05,9.05191653e-26,-9.0,3.1542106e-17,3.1542106e-17,-9.08868537e-17,3.15421199e-17,3.15421057e-17,3.15421056e-17
5.228e-05,-8.51162945e-26,-9.0,3.15421059e-17,3.15421059e-17,-9.08868537e-17,3.15421199e-17,3.15421057e-17,3.15421055e-17
5.328e-05,-1.31408078e-26,-9.0,3.15419631e-17,3.15419631e-17,-9.08869965e-17,3.15419771e-17,3.15419629e-17,3.15419627e-17
5.428e-05,9.70625034e-26,-9.0,3.1542106e-17,3.1542106e-17,-9.08868537e-17,3.15421199e-17,3.15421057e-17,3.15421055e-17
5.528e-05,-7.50977596e-26,-9.0,3.15421059e-17,3.15421059e-17,-9.08868537e-17,3.15421199e-17,3.15421056e-17,3.15421055e-17
5.628e-05,-2.87919049e-26,-9.0,3.15419631e-17,3.15419631e-17,-9.08869965e-17,3.15419771e-17,3.15419628e-17,3.15419627e-17
5.728e-05,1.01272239e-25,-9.0,3.1542106e-17,3.1542106e-17,-9.08868537e-17,3.15421199e-17,3.15421057e-17,3.15421055e-17
5.828e-05,-6.32736945e-26,-9.0,3.15421059e-17,3.15421059e-17,-9.08868537e-17,3.15421198e-17,3.15421056e-17,3.15421055e-17
5.928e-05,-4.37507902e-26,-9.0,3.15419631e-17,3.15419631e-17,-9.08869965e-17,3.1541977e-17,3.15419628e-17,3.15419626e-17
6.028e-05,1.0304716e-25,-9.0,3.15421059e-17,3.15421059e-17,-9.08868537e-17,3.15421199e-17,3.15421057e-17,3.15421055e-17
6.128e-05,-4.99284463e-26,-9.0,3.15419631e-17,3.15419631e-17,-9.08869965e-17,3.1541977e-17,3.15419628e-17,3.15419626e-17
6.228e-05,-5.76578075e-26,-9.0,3.15418203e-17,3.15418203e-17,-9.08871394e-17,3.15418342e-17,3.154182e-17,3.15418198e-17
6.328e-05,1.02344747e-25,-9.0,3.15421059e-17,3.15421059e-17,-9.08868537e-17,3.15421199e-17,3.15421056e-17,3.15421055e-17
6.428e-05,-3.53828197e-26,-9.0,3.15419631e-17,3.15419631e-17,-9.08869965e-17,3.1541977e-17,3.15419628e-17,3.15419626e-17
6.528e-05,-7.01786393e-26,-9.0,3.15419631e-17,3.15419631e-17,-9.08869966e-17,3.1541977e-17,3.15419628e-17,3.15419626e-17
6.628e-05,9.91816747e-26,-9.0,3.15421059e-17,3.15421059e-17,-9.08868537e-17,3.15421198e-17,3.15421056e-17,3.15421054e-17
6.728e-05,-1.99865396e-26,-9.0,3.15419631e-17,3.15419631e-17,-9.08869965e-17,3.1541977e-17,3.15419628e-17,3.15419626e-17
6.828e-05,-8.10121652e-26,-9.0,3.1541963e-17,3.1541963e-17,-9.08869966e-17,3.1541977e-17,3.15419628e-17,3.15419626e-17
6.928e-05,9.36340545e-26,-9.0,3.15421059e-17,3.15421059e-17,-9.08868537e-17,3.15421198e-17,3.15421056e-17,3.15421054e-17
7.028e-05,-4.10965064e-27,-9.0,3.15421059e-17,3.15421059e-17,-9.08868537e-17,3.15421198e-17,3.15421056e-17,3.15421054e-17
7.128e-05,-8.98981005e-26,-9.0,3.1541963e-17,3.1541963e-17,-9.08869966e-17,3.1541977e-17,3.15419627e-17,3.15419625e-17
7.228e-05,8.58352166e-26,-9.0,3.15421059e-17,3.15421059e-17,-9.08868537e-17,3.15421198e-17,3.15421056e-17,3.15421054e-17
7.328e-05,1.18660854e-26,-9.0,3.1541963e-17,3.1541963e-17,-9.08869965e-17,3.1541977e-17,3.15419627e-17,3.15419625e-17
7.428e-05,-9.66225669e-26,-9.0,3.15421058e-17,3.15421058e-17,-9.08868537e-17,3.15421197e-17,3.15421055e-17,3.15421053e-17
7.528e-05,7.59726837e-26,-9.0,3.15421058e-17,3.15421058e-17,-9.08868537e-17,3.15421198e-17,3.15421056e-17,3.15421054e-17
7.628e-05,2.75563986e-26,-9.0,3.1541963e-17,3.1541963e-17,-9.08869965e-17,3.1541977e-17,3.15419627e-17,3.15419625e-17
7.728e-05,-1.01024007e-25,-9.0,3.1541963e-17,3.1541963e-17,-9.08869966e-17,3.15419769e-17,3.15419627e-17,3.15419625e-17
7.828e-05,6.42836998e-26,-9.0,3.15421058e-17,3.15421058e-17,-9.08868537e-17,3.15421198e-17,3.15421055e-17,3.15421053e-17
7.928e-05,4.25841878e-26,-9.0,3.15418202e-17,3.15418202e-17,-9.08871393e-17,3.15418341e-17,3.15418199e-17,3.15418197e-17
8.028e-05,-1.0299665e-25,-9.0,3.1541963e-17,3.1541963e-17,-9.08869966e-17,3.15419769e-17,3.15419627e-17,3.15419625e-17
8.128e-05,5.10492942e-26,-9.0,3.15421058e-17,3.15421058e-17,-9.08868537e-17,3.15421197e-17,3.15421055e-17,3.15421053e-17
8.228e-05,5.65881602e-26,-9.0,3.1541963e-17,3.1541963e-17,-9.08869965e-17,3.15419769e-17,3.15419627e-17,3.15419625e-17
8.328e-05,-1.02493076e-25,-9.0,3.15421058e-17,3.15421058e-17,-9.08868538e-17,3.15421197e-17,3.15421055e-17,3.15421052e-17
8.428e-05,3.65874355e-26,-9.0,3.15421058e-17,3.15421058e-17,-9.08868537e-17,3.15421197e-17,3.15421055e-17,3.15421053e-17
8.528e-05,6.92316789e-26,-9.0,3.1541963e-17,3.1541963e-17,-9.08869965e-17,3.15419769e-17,3.15419627e-17,3.15419625e-17
8.628e-05,-9.95253773e-26,-9.0,3.15419629e-17,3.15419629e-17,-9.08869966e-17,3.15419769e-17,3.15419626e-17,3.15419624e-17
8.728e-05,2.12460289e-26,-9.0,3.15421058e-17,3.15421058e-17,-9.08868537e-17,3.15421197e-17,3.15421055e-17,3.15421052e-17
8.828e-05,8.02107854e-26,-9.0,3.1541963e-17,3.1541963e-17,-9.08869965e-17,3.15419769e-17,3.15419627e-17,3.15419624e-17
8.928e-05,-9.41649967e-26,-9.0,3.15419629e-17,3.15419629e-17,-9.08869966e-17,3.15419768e-17,3.15419626e-17,3.15419624e-17
9.028e-05,5.39377709e-27,-9.0,3.15419629e-17,3.15419629e-17,-9.08869965e-17,3.15419769e-17,3.15419627e-17,3.15419624e-17
9.128e-05,8.92615629e-26,-9.0,3.1541963e-17,3.1541963e-17,-9.08869965e-17,3.15419769e-17,3.15419627e-17,3.15419624e-17
9.228e-05,-8.65406524e-26,-
```

> Artifact truncated in this preview. The original file remains available through the manifest path.
