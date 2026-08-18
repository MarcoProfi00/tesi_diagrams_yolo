# Agent input preview

This file is a local preview of the evidence that will be provided to the read-only diagnostic agent.
The agent remains read-only: it can inspect base outputs and existing scenario artifacts, but it does not modify files.

## User problem

Puoi concludere l’esperimento riassumendo la causa più probabile e la correzione verificata?

## Circuit

- Batch: `batchICChatAgentEvaluation`
- Circuit: `ic03`
- Agent mode: `graph_grounded_readonly`

## Technical summary

```json
{
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_message": "ngspice completed successfully.",
  "emitted_elements": 11,
  "skipped_elements": 3,
  "emit_warnings_count": 0,
  "skipped_components_count": 3,
  "node_count": 7,
  "ground_groups_count": 1,
  "singleton_nodes_count": 0,
  "bound_components": 9,
  "missing_components": 0,
  "unsupported_components": 1,
  "spice_ready_components": 10,
  "rules_missing_components": 0,
  "has_tran_csv": true,
  "has_tran_plot": true,
  "led_profiles": {},
  "load_profiles": {
    "Rlamp13_1": {
      "source_component_id": "lamp13.1",
      "state": "blinking",
      "regular_period": true,
      "period_s": 0.3552648299999994,
      "frequency_hz": 2.8148015664821133,
      "duty_cycle": 0.11259206265928588,
      "on_fraction": 0.10587539432176656,
      "pulse_count": 50,
      "voltage_min": 0.0401859746,
      "voltage_max": 11.4997328,
      "positive_node": "N003",
      "negative_node": "0"
    }
  },
  "temporal_profiles": {
    "Rlamp13_1": {
      "source_component_id": "lamp13.1",
      "state": "blinking",
      "regular_period": true,
      "period_s": 0.3552648299999994,
      "frequency_hz": 2.8148015664821133,
      "duty_cycle": 0.11259206265928588,
      "on_fraction": 0.10587539432176656,
      "pulse_count": 50,
      "voltage_min": 0.0401859746,
      "voltage_max": 11.4997328,
      "positive_node": "N003",
      "negative_node": "0"
    }
  }
}
```

## Image policy

- Included by default: `False`
- Can be requested: `True`
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\input\images\ic03.jpg`
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
      "scenario_id": "scenario_3",
      "title": "Aumentare R1 per testare la costante di tempo resistiva",
      "status": "spice_success",
      "spice_status": "success",
      "outcome_status": "partially_resolved",
      "outcome_label": "Criteri temporali non soddisfatti",
      "outcome_technical_label": "Temporal criteria not satisfied",
      "outcome_reason": "Almeno un criterio temporale non e soddisfatto.",
      "stop_automation": false,
      "comparison_summary": {
        "requested_count": 3,
        "changed_count": 3,
        "activated_count": 0,
        "missing_count": 0,
        "expected_count": 3,
        "expectations_met_count": 3,
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
        "min_gain_ratio": null,
        "temporal_required": true,
        "temporal_available": true,
        "temporal_met": false
      },
      "quantity_summary": {
        "changed": [
          "v(N001)",
          "v(N004)",
          "v(N003)"
        ],
        "unchanged": [],
        "missing": []
      },
      "led_profiles": {},
      "ranking_verified": true,
      "score": 35,
      "load_profiles": {
        "Rlamp13_1": {
          "source_component_id": "lamp13.1",
          "state": "blinking",
          "regular_period": true,
          "period_s": 0.4815494299999994,
          "frequency_hz": 2.076630014908337,
          "duty_cycle": 0.11571730029874687,
          "on_fraction": 0.10092106566306824,
          "pulse_count": 36,
          "voltage_min": 0.0386900095,
          "voltage_max": 11.4994736,
          "positive_node": "N003",
          "negative_node": "0"
        }
      },
      "temporal_profiles": {
        "Rlamp13_1": {
          "source_component_id": "lamp13.1",
          "state": "blinking",
          "regular_period": true,
          "period_s": 0.4815494299999994,
          "frequency_hz": 2.076630014908337,
          "duty_cycle": 0.11571730029874687,
          "on_fraction": 0.10092106566306824,
          "pulse_count": 36,
          "voltage_min": 0.0386900095,
          "voltage_max": 11.4994736,
          "positive_node": "N003",
          "negative_node": "0"
        }
      }
    },
    {
      "scenario_id": "scenario_4",
      "title": "Aumentare ancora R1",
      "status": "spice_success",
      "spice_status": "success",
      "outcome_status": "resolved_candidate",
      "outcome_label": "Criteri elettrici e temporali soddisfatti",
      "outcome_technical_label": "Transient correction verified",
      "outcome_reason": "Le aspettative elettriche e il profilo transitorio richiesto sono verificati.",
      "stop_automation": true,
      "comparison_summary": {
        "requested_count": 3,
        "changed_count": 3,
        "activated_count": 0,
        "missing_count": 0,
        "expected_count": 3,
        "expectations_met_count": 3,
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
        "min_gain_ratio": null,
        "temporal_required": true,
        "temporal_available": true,
        "temporal_met": true
      },
      "quantity_summary": {
        "changed": [
          "v(N001)",
          "v(N004)",
          "v(N003)"
        ],
        "unchanged": [],
        "missing": []
      },
      "led_profiles": {},
      "ranking_verified": true,
      "score": 195,
      "load_profiles": {
        "Rlamp13_1": {
          "source_component_id": "lamp13.1",
          "state": "blinking",
          "regular_period": true,
          "period_s": 0.5552144200000004,
          "frequency_hz": 1.8011059583070612,
          "duty_cycle": 0.11530494831168063,
          "on_fraction": 0.09711338160896736,
          "pulse_count": 30,
          "voltage_min": 0.0401190388,
          "voltage_max": 11.4993474,
          "positive_node": "N003",
          "negative_node": "0"
        }
      },
      "temporal_profiles": {
        "Rlamp13_1": {
          "source_component_id": "lamp13.1",
          "state": "blinking",
          "regular_period": true,
          "period_s": 0.5552144200000004,
          "frequency_hz": 1.8011059583070612,
          "duty_cycle": 0.11530494831168063,
          "on_fraction": 0.09711338160896736,
          "pulse_count": 30,
          "voltage_min": 0.0401190388,
          "voltage_max": 11.4993474,
          "positive_node": "N003",
          "negative_node": "0"
        }
      }
    }
  ]
}
```


## Executed scenarios

### scenario_3

- Title: `Aumentare R1 per testare la costante di tempo resistiva`
- Status: `spice_success`
- SPICE status: `success`
- Outcome: `partially_resolved`
- Stop automation: `False`
- Comparison: `3/3` changed
- LED profiles: `{}`
- Temporal profiles: `{"Rlamp13_1": {"source_component_id": "lamp13.1", "state": "blinking", "regular_period": true, "period_s": 0.4815494299999994, "frequency_hz": 2.076630014908337, "duty_cycle": 0.11571730029874687, "on_fraction": 0.10092106566306824, "pulse_count": 36, "voltage_min": 0.0386900095, "voltage_max": 11.4994736, "positive_node": "N003", "negative_node": "0"}}`

#### scenario_definition

- Role: Scenario selected by the user and saved before execution.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic03\scenarios\scenario_3\scenario.json`

```json
{
  "scenario_id": "scenario_3",
  "title": "Aumentare R1 per testare la costante di tempo resistiva",
  "hypothesis": "Rresistor22_3 è una delle resistenze che fissano il periodo e un suo valore troppo basso accelera il lampeggio.",
  "intent": "correction",
  "actions": [
    {
      "type": "change_component_value",
      "target": "Rresistor22_3",
      "value": "22k"
    }
  ],
  "rerun_from": "07",
  "analysis": "tran",
  "compare": [
    "v(N001)",
    "v(N004)",
    "v(N003)"
  ],
  "expect": {
    "v(N001)": "changed",
    "v(N004)": "changed",
    "v(N003)": "changed"
  },
  "temporal_expect": {
    "target": "Rlamp13_1",
    "required_state": "blinking",
    "require_regular_period": true,
    "max_frequency_hz": 2.0
  }
}
```

#### scenario_status

- Role: Current scenario status, SPICE status and diagnostic outcome.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic03\scenarios\scenario_3\scenario_status.json`

```json
{
  "status": "spice_success",
  "stage": "scenario_spice_executed",
  "scenario_id": "scenario_3",
  "source": "guided_chat",
  "spice_executed": true,
  "created_or_updated_at": "2026-08-03T15:21:23",
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic03\\scenarios\\scenario_3\\run\\08_spice_run.json",
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic03\\scenarios\\scenario_3\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 3,
    "changed_count": 3,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 3,
    "expectations_met_count": 3,
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
    "min_gain_ratio": null,
    "temporal_required": true,
    "temporal_available": true,
    "temporal_met": false
  },
  "diagnostic_outcome": {
    "status": "partially_resolved",
    "technical_label": "Temporal criteria not satisfied",
    "label": "Criteri temporali non soddisfatti",
    "reason": "Almeno un criterio temporale non e soddisfatto.",
    "user_message": "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato.",
    "stop_automation": false,
    "confidence": "low",
    "next_step": "Il comportamento temporale non soddisfa ancora l'obiettivo: prova un'altra correzione."
  },
  "controlled_scenario_report": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic03\\scenarios\\scenario_3\\12_controlled_scenarios.json",
  "executed_scenarios_count": 1,
  "scenario_budget_exhausted": false,
  "next_step": "Il comportamento temporale non soddisfa ancora l'obiettivo: prova un'altra correzione."
}
```

#### controlled_scenario_report

- Role: Report produced by the controlled scenario runner.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic03\scenarios\scenario_3\12_controlled_scenarios.json`

```json
{
  "source_format": "pipeline2.0_controlled_scenario_report",
  "status": "spice_success",
  "scenario_id": "scenario_3",
  "scenario_title": "Aumentare R1 per testare la costante di tempo resistiva",
  "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic03\\scenarios\\scenario_3",
  "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic03\\scenarios\\scenario_3\\run",
  "netlist": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic03\\scenarios\\scenario_3\\run\\07_netlist.cir",
  "applied_actions": [
    {
      "status": "applied",
      "type": "change_component_value",
      "target": "Rresistor22_3",
      "resolved_component_name": "Rresistor22_3",
      "tried_component_names": [
        "Rresistor22_3"
      ],
      "value": "22k",
      "normalized_component_value": "22k",
      "old_value": "10k",
      "new_value": "22k",
      "old_line": "Rresistor22_3 N001 N004 10k",
      "new_line": "Rresistor22_3 N001 N004 22k",
      "operation": "updated",
      "spice_executed": false,
      "index": 1
    }
  ],
  "unsupported_actions": [],
  "failed_actions": [],
  "spice_executed": true,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic03\\scenarios\\scenario_3\\run\\08_spice_run.json",
  "spice_status": "success",
  "spice_exit_code": 0,
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic03\\scenarios\\scenario_3\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 3,
    "changed_count": 3,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 3,
    "expectations_met_count": 3,
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
    "min_gain_ratio": null,
    "temporal_required": true,
    "temporal_available": true,
    "temporal_met": false
  },
  "diagnostic_outcome": {
    "status": "partially_resolved",
    "technical_label": "Temporal criteria not satisfied",
    "label": "Criteri temporali non soddisfatti",
    "reason": "Almeno un criterio temporale non e soddisfatto.",
    "user_message": "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato.",
    "stop_automation": false,
    "confidence": "low",
    "next_step": "Il comportamento temporale non soddisfa ancora l'obiettivo: prova un'altra correzione."
  },
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "created_or_updated_at": "2026-08-03T15:21:23"
}
```

#### scenario_comparison

- Role: Base-vs-scenario comparison used to evaluate the scenario.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic03\scenarios\scenario_3\scenario_comparison.json`

```json
{
  "source_format": "pipeline2.0_scenario_comparison",
  "scenario_id": "scenario_3",
  "scenario_title": "Aumentare R1 per testare la costante di tempo resistiva",
  "scenario_intent": "correction",
  "base_output_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic03",
  "scenario_run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic03\\scenarios\\scenario_3\\run",
  "base_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic03\\08_ngspice_stdout.txt",
  "scenario_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic03\\scenarios\\scenario_3\\run\\08_ngspice_stdout.txt",
  "base_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic03\\08_ngspice_stderr.txt",
  "scenario_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic03\\scenarios\\scenario_3\\run\\08_ngspice_stderr.txt",
  "quantities": [
    {
      "quantity": "v(N001)",
      "base_value": 11.83920076,
      "scenario_value": 11.87623682,
      "delta": 0.03703606000000015,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 0.003128256776008936,
      "meaningful_improvement": false,
      "metric": "v(n001).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": -1.56278436,
        "max": 10.2764164,
        "mean": 0.08648327066114969,
        "vpp": 11.83920076,
        "final": -1.4960299,
        "abs_peak": 10.2764164
      },
      "scenario_details": {
        "min": -1.59540782,
        "max": 10.280829,
        "mean": 0.04517445497783586,
        "vpp": 11.87623682,
        "final": -0.840324794,
        "abs_peak": 10.280829
      }
    },
    {
      "quantity": "v(N004)",
      "base_value": 12.27032565,
      "scenario_value": 12.803650509999999,
      "delta": 0.5333248599999987,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 0.04346460519570633,
      "meaningful_improvement": false,
      "metric": "v(n004).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": -1.81453185,
        "max": 10.4557938,
        "mean": 0.08590050285344784,
        "vpp": 12.27032565,
        "final": -1.34353832,
        "abs_peak": 10.4557938
      },
      "scenario_details": {
        "min": -2.17297571,
        "max": 10.6306748,
        "mean": 0.04511666251853314,
        "vpp": 12.803650509999999,
        "final": -0.444658428,
        "abs_peak": 10.6306748
      }
    },
    {
      "quantity": "v(N003)",
      "base_value": 11.4595468254,
      "scenario_value": 11.4607835905,
      "delta": 0.0012367650999998148,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 0.0001079244335612412,
      "meaningful_improvement": false,
      "metric": "v(n003).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": 0.0401859746,
        "max": 11.4997328,
        "mean": 1.4967378960588031,
        "vpp": 11.4595468254,
        "final": 0.0493115416,
        "abs_peak": 11.4997328
      },
      "scenario_details": {
        "min": 0.0386900095,
        "max": 11.4994736,
        "mean": 1.4637314481571655,
        "vpp": 11.4607835905,
        "final": 0.43655173,
        "abs_peak": 11.4994736
      }
    }
  ],
  "summary": {
    "requested_count": 3,
    "changed_count": 3,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 3,
    "expectations_met_count": 3,
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
    "min_gain_ratio": null,
    "temporal_required": true,
    "temporal_available": true,
    "temporal_met": false
  },
  "gain_comparison": null,
  "quality_comparison": null,
  "diagnostic_outcome": {
    "status": "partially_resolved",
    "technical_label": "Temporal criteria not satisfied",
    "label": "Criteri temporali non soddisfatti",
    "reason": "Almeno un criterio temporale non e soddisfatto.",
    "user_message": "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato.",
    "stop_automation": false,
    "confidence": "low",
    "next_step": "Il comportamento temporale non soddisfa ancora l'obiettivo: prova un'altra correzione."
  },
  "created_or_updated_at": "2026-08-03T15:21:23",
  "temporal_expectation": {
    "target": "Rlamp13_1",
    "available": true,
    "met": false,
    "reason": "Almeno un criterio temporale non e soddisfatto.",
    "base_profile": {
      "status": "measured",
      "source_component_id": "lamp13.1",
      "state": "blinking",
      "profile_method": "differential_voltage_relative_threshold",
      "positive_node": "N003",
      "negative_node": "0",
      "threshold_v": 5.7699593873,
      "on_fraction": 0.10587539432176656,
      "duty_cycle": 0.11259206265928588,
      "regular_period": true,
      "period_s": 0.3552648299999994,
      "frequency_hz": 2.8148015664821133,
      "pulse_count": 50,
      "timeline_key_times": [
        0.0,
        0.12232799999999999,
        0.123582876,
        0.1366761675,
        0.13857616749999999,
        0.1540761675,
        0.1560761675,
        0.171769711,
        0.17386971099999998,
        0.1898074185,
        0.1917795785,
        0.2075309035,
        0.20949454099999998,
        0.225121716,
        0.227130331,
        0.242823618,
        0.244923618,
        0.260561118,
        0.2625693275,
        0.2783693275,
        0.280362139,
        0.2962582995,
        0.2982582995,
        0.3141531405,
        0.3161531405,
        0.3319777985,
        0.3339884105,
        0.3497884105,
        0.3517884105,
        0.3676884105,
        0.3696884105,
        0.3854783705,
        0.3875741285,
        0.4032890285,
        0.40528832049999997,
        0.42095374249999995,
        0.422910567,
        0.4385400945,
        0.44062581549999996,
        0.45645634900000004,
        0.45849099649999997,
        0.4742195905,
        0.47630724100000005,
        0.4921376095,
        0.49414432350000004,
        0.50979636,
        0.511859735,
        0.527644895,
        0.5296948699999999,
        0.545580105,
        0.547601485,
        0.56339785,
        0.565446715,
        0.58113953,
        0.58311484,
        0.598756065,
        0.60082334,
        0.616514215,
        0.6185056099999999,
        0.63420181,
        0.636236985,
        0.652132385,
        0.654132385,
        0.66994829,
        0.672019785,
        0.68781295,
        0.689842025,
        0.705542025,
        0.707542025,
        0.723242025,
        0.72521463,
        0.74086505,
        0.742835695,
        0.758472515,
        0.7604986499999999,
        0.77623088,
        0.77822929,
        0.793886805,
        0.795841875,
        0.8114758,
        0.81352632,
        0.829398945,
        0.831356775,
        0.84706268,
        0.849051365,
        0.864751365,
        0.866751365,
        0.8824926100000001,
        0.88452965,
        0.9004266700000001,
        0.90242667,
        0.918320965,
        0.92031979,
        0.93610726,
        0.93817207,
        0.953900695,
        0.95594681,
        0.97168342,
        0.9737127400000001,
        0.9895077999999999,
        0.99147414,
        1.0
      ],
      "timeline_states": [
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        false
      ],
      "voltage_min": 0.0401859746,
      "voltage_max": 11.4997328,
      "voltage_magnitude_min": 0.0401859746,
      "voltage_magnitude_max": 11.4997328,
      "time_window_s": 20.0
    },
    "scenario_profile": {
      "status": "measured",
      "source_component_id": "lamp13.1",
      "state": "blinking",
      "profile_method": "differential_voltage_relative_threshold",
      "positive_node": "N003",
      "negative_node": "0",
      "threshold_v": 5.76908180475,
      "on_fraction": 0.10092106566306824,
      "duty_cycle": 0.11571730029874687,
      "regular_period": true,
      "period_s": 0.4815494299999994,
      "frequency_hz": 2.076630014908337,
      "pulse_count": 36,
      "timeline_key_times": [
        0.0,
        0.149928,
        0.150228,
        0.161328,
        0.1632748235,
        0.1817540685,
        0.1843842265,
        0.2052932245,
        0.208084305,
        0.22932180500000002,
        0.2321992765,
        0.2533992765,
        0.25619927649999996,
        0.27748442149999997,
        0.28024637,
        0.301547872,
        0.3043207715,
        0.3256758515,
        0.3285304575,
        0.349983328,
        0.352783328,
        0.374167878,
        0.376930567,
        0.398170052,
        0.400954658,
        0.4222919815,
        0.4250128215,
        0.44628301800000003,
        0.44916270799999997,
        0.47060092400000003,
        0.473400924,
        0.4947094545,
        0.49747055749999997,
        0.51875829,
        0.5215180349999999,
        0.54280621,
        0.545564905,
        0.566854255,
        0.569611985,
        0.590904975,
        0.59366291,
        0.61494602,
        0.61769974,
        0.638917655,
        0.641717655,
        0.663017655,
        0.665817655,
        0.68707841,
        0.68986459,
        0.7111359150000001,
        0.7139601,
        0.7352601,
        0.7381601,
        0.7593976,
        0.7622482500000001,
        0.783600085,
        0.786500085,
        0.807800085,
        0.8105420999999999,
        0.831801735,
        0.834619455,
        0.855988355,
        0.85885351,
        0.8801535100000001,
        0.8828723650000001,
        0.904172365,
        0.906972365,
        0.928321865,
        0.931108045,
        0.952521545,
        0.9553606200000001,
        0.9766908150000001,
        0.9794658399999999,
        1.0
      ],
      "timeline_states": [
        false,
        true,
        false,
        true,
```

> Scenario artifact truncated in this preview.

### scenario_4

- Title: `Aumentare ancora R1`
- Status: `spice_success`
- SPICE status: `success`
- Outcome: `resolved_candidate`
- Stop automation: `True`
- Comparison: `3/3` changed
- LED profiles: `{}`
- Temporal profiles: `{"Rlamp13_1": {"source_component_id": "lamp13.1", "state": "blinking", "regular_period": true, "period_s": 0.5552144200000004, "frequency_hz": 1.8011059583070612, "duty_cycle": 0.11530494831168063, "on_fraction": 0.09711338160896736, "pulse_count": 30, "voltage_min": 0.0401190388, "voltage_max": 11.4993474, "positive_node": "N003", "negative_node": "0"}}`

#### scenario_definition

- Role: Scenario selected by the user and saved before execution.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic03\scenarios\scenario_4\scenario.json`

```json
{
  "scenario_id": "scenario_4",
  "title": "Aumentare ancora R1",
  "hypothesis": "Poiche l'aumento di Rresistor22_3 da 10k a 22k ha gia rallentato il lampeggio senza raggiungere il target, un ulteriore aumento della stessa resistenza puo ridurre ancora la frequenza di Rlamp13_1.",
  "intent": "correction",
  "actions": [
    {
      "type": "change_component_value",
      "target": "Rresistor22_3",
      "value": "33k"
    }
  ],
  "rerun_from": "07",
  "analysis": "tran",
  "compare": [
    "v(N001)",
    "v(N004)",
    "v(N003)"
  ],
  "expect": {
    "v(N001)": "changed",
    "v(N004)": "changed",
    "v(N003)": "changed"
  },
  "temporal_expect": {
    "target": "Rlamp13_1",
    "required_state": "blinking",
    "require_regular_period": true,
    "max_frequency_hz": 2.0
  }
}
```

#### scenario_status

- Role: Current scenario status, SPICE status and diagnostic outcome.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic03\scenarios\scenario_4\scenario_status.json`

```json
{
  "status": "spice_success",
  "stage": "scenario_spice_executed",
  "scenario_id": "scenario_4",
  "source": "guided_chat",
  "spice_executed": true,
  "created_or_updated_at": "2026-08-03T15:25:12",
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic03\\scenarios\\scenario_4\\run\\08_spice_run.json",
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic03\\scenarios\\scenario_4\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 3,
    "changed_count": 3,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 3,
    "expectations_met_count": 3,
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
    "min_gain_ratio": null,
    "temporal_required": true,
    "temporal_available": true,
    "temporal_met": true
  },
  "diagnostic_outcome": {
    "status": "resolved_candidate",
    "technical_label": "Transient correction verified",
    "label": "Criteri elettrici e temporali soddisfatti",
    "reason": "Le aspettative elettriche e il profilo transitorio richiesto sono verificati.",
    "user_message": "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato.",
    "stop_automation": true,
    "confidence": "medium",
    "next_step": "La correzione e verificata: puoi passare alla conclusione diagnostica."
  },
  "controlled_scenario_report": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic03\\scenarios\\scenario_4\\12_controlled_scenarios.json",
  "executed_scenarios_count": 2,
  "scenario_budget_exhausted": false,
  "next_step": "La correzione e verificata: puoi passare alla conclusione diagnostica."
}
```

#### controlled_scenario_report

- Role: Report produced by the controlled scenario runner.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic03\scenarios\scenario_4\12_controlled_scenarios.json`

```json
{
  "source_format": "pipeline2.0_controlled_scenario_report",
  "status": "spice_success",
  "scenario_id": "scenario_4",
  "scenario_title": "Aumentare ancora R1",
  "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic03\\scenarios\\scenario_4",
  "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic03\\scenarios\\scenario_4\\run",
  "netlist": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic03\\scenarios\\scenario_4\\run\\07_netlist.cir",
  "applied_actions": [
    {
      "status": "applied",
      "type": "change_component_value",
      "target": "Rresistor22_3",
      "resolved_component_name": "Rresistor22_3",
      "tried_component_names": [
        "Rresistor22_3"
      ],
      "value": "33k",
      "normalized_component_value": "33k",
      "old_value": "10k",
      "new_value": "33k",
      "old_line": "Rresistor22_3 N001 N004 10k",
      "new_line": "Rresistor22_3 N001 N004 33k",
      "operation": "updated",
      "spice_executed": false,
      "index": 1
    }
  ],
  "unsupported_actions": [],
  "failed_actions": [],
  "spice_executed": true,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic03\\scenarios\\scenario_4\\run\\08_spice_run.json",
  "spice_status": "success",
  "spice_exit_code": 0,
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic03\\scenarios\\scenario_4\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 3,
    "changed_count": 3,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 3,
    "expectations_met_count": 3,
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
    "min_gain_ratio": null,
    "temporal_required": true,
    "temporal_available": true,
    "temporal_met": true
  },
  "diagnostic_outcome": {
    "status": "resolved_candidate",
    "technical_label": "Transient correction verified",
    "label": "Criteri elettrici e temporali soddisfatti",
    "reason": "Le aspettative elettriche e il profilo transitorio richiesto sono verificati.",
    "user_message": "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato.",
    "stop_automation": true,
    "confidence": "medium",
    "next_step": "La correzione e verificata: puoi passare alla conclusione diagnostica."
  },
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "created_or_updated_at": "2026-08-03T15:25:12"
}
```

#### scenario_comparison

- Role: Base-vs-scenario comparison used to evaluate the scenario.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic03\scenarios\scenario_4\scenario_comparison.json`

```json
{
  "source_format": "pipeline2.0_scenario_comparison",
  "scenario_id": "scenario_4",
  "scenario_title": "Aumentare ancora R1",
  "scenario_intent": "correction",
  "base_output_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic03",
  "scenario_run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic03\\scenarios\\scenario_4\\run",
  "base_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic03\\08_ngspice_stdout.txt",
  "scenario_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic03\\scenarios\\scenario_4\\run\\08_ngspice_stdout.txt",
  "base_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic03\\08_ngspice_stderr.txt",
  "scenario_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic03\\scenarios\\scenario_4\\run\\08_ngspice_stderr.txt",
  "quantities": [
    {
      "quantity": "v(N001)",
      "base_value": 11.83920076,
      "scenario_value": 11.85463743,
      "delta": 0.015436669999999708,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 0.0013038608190642513,
      "meaningful_improvement": false,
      "metric": "v(n001).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": -1.56278436,
        "max": 10.2764164,
        "mean": 0.08648327066114969,
        "vpp": 11.83920076,
        "final": -1.4960299,
        "abs_peak": 10.2764164
      },
      "scenario_details": {
        "min": -1.57491183,
        "max": 10.2797256,
        "mean": 0.04501653177877264,
        "vpp": 11.85463743,
        "final": -1.21433847,
        "abs_peak": 10.2797256
      }
    },
    {
      "quantity": "v(N004)",
      "base_value": 12.27032565,
      "scenario_value": 13.093204669999999,
      "delta": 0.8228790199999985,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 0.06706252494610837,
      "meaningful_improvement": false,
      "metric": "v(n004).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": -1.81453185,
        "max": 10.4557938,
        "mean": 0.08590050285344784,
        "vpp": 12.27032565,
        "final": -1.34353832,
        "abs_peak": 10.4557938
      },
      "scenario_details": {
        "min": -2.35776477,
        "max": 10.7354399,
        "mean": 0.04454650925762005,
        "vpp": 13.093204669999999,
        "final": -0.704677362,
        "abs_peak": 10.7354399
      }
    },
    {
      "quantity": "v(N003)",
      "base_value": 11.4595468254,
      "scenario_value": 11.4592283612,
      "delta": -0.00031846420000114506,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 2.7790296148122674e-05,
      "meaningful_improvement": false,
      "metric": "v(n003).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": 0.0401859746,
        "max": 11.4997328,
        "mean": 1.4967378960588031,
        "vpp": 11.4595468254,
        "final": 0.0493115416,
        "abs_peak": 11.4997328
      },
      "scenario_details": {
        "min": 0.0401190388,
        "max": 11.4993474,
        "mean": 1.4513731113520385,
        "vpp": 11.4592283612,
        "final": 0.131947656,
        "abs_peak": 11.4993474
      }
    }
  ],
  "summary": {
    "requested_count": 3,
    "changed_count": 3,
    "activated_count": 0,
    "missing_count": 0,
    "expected_count": 3,
    "expectations_met_count": 3,
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
    "min_gain_ratio": null,
    "temporal_required": true,
    "temporal_available": true,
    "temporal_met": true
  },
  "gain_comparison": null,
  "quality_comparison": null,
  "diagnostic_outcome": {
    "status": "resolved_candidate",
    "technical_label": "Transient correction verified",
    "label": "Criteri elettrici e temporali soddisfatti",
    "reason": "Le aspettative elettriche e il profilo transitorio richiesto sono verificati.",
    "user_message": "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato.",
    "stop_automation": true,
    "confidence": "medium",
    "next_step": "La correzione e verificata: puoi passare alla conclusione diagnostica."
  },
  "created_or_updated_at": "2026-08-03T15:25:12",
  "temporal_expectation": {
    "target": "Rlamp13_1",
    "available": true,
    "met": true,
    "reason": "Criteri temporali verificati.",
    "base_profile": {
      "status": "measured",
      "source_component_id": "lamp13.1",
      "state": "blinking",
      "profile_method": "differential_voltage_relative_threshold",
      "positive_node": "N003",
      "negative_node": "0",
      "threshold_v": 5.7699593873,
      "on_fraction": 0.10587539432176656,
      "duty_cycle": 0.11259206265928588,
      "regular_period": true,
      "period_s": 0.3552648299999994,
      "frequency_hz": 2.8148015664821133,
      "pulse_count": 50,
      "timeline_key_times": [
        0.0,
        0.12232799999999999,
        0.123582876,
        0.1366761675,
        0.13857616749999999,
        0.1540761675,
        0.1560761675,
        0.171769711,
        0.17386971099999998,
        0.1898074185,
        0.1917795785,
        0.2075309035,
        0.20949454099999998,
        0.225121716,
        0.227130331,
        0.242823618,
        0.244923618,
        0.260561118,
        0.2625693275,
        0.2783693275,
        0.280362139,
        0.2962582995,
        0.2982582995,
        0.3141531405,
        0.3161531405,
        0.3319777985,
        0.3339884105,
        0.3497884105,
        0.3517884105,
        0.3676884105,
        0.3696884105,
        0.3854783705,
        0.3875741285,
        0.4032890285,
        0.40528832049999997,
        0.42095374249999995,
        0.422910567,
        0.4385400945,
        0.44062581549999996,
        0.45645634900000004,
        0.45849099649999997,
        0.4742195905,
        0.47630724100000005,
        0.4921376095,
        0.49414432350000004,
        0.50979636,
        0.511859735,
        0.527644895,
        0.5296948699999999,
        0.545580105,
        0.547601485,
        0.56339785,
        0.565446715,
        0.58113953,
        0.58311484,
        0.598756065,
        0.60082334,
        0.616514215,
        0.6185056099999999,
        0.63420181,
        0.636236985,
        0.652132385,
        0.654132385,
        0.66994829,
        0.672019785,
        0.68781295,
        0.689842025,
        0.705542025,
        0.707542025,
        0.723242025,
        0.72521463,
        0.74086505,
        0.742835695,
        0.758472515,
        0.7604986499999999,
        0.77623088,
        0.77822929,
        0.793886805,
        0.795841875,
        0.8114758,
        0.81352632,
        0.829398945,
        0.831356775,
        0.84706268,
        0.849051365,
        0.864751365,
        0.866751365,
        0.8824926100000001,
        0.88452965,
        0.9004266700000001,
        0.90242667,
        0.918320965,
        0.92031979,
        0.93610726,
        0.93817207,
        0.953900695,
        0.95594681,
        0.97168342,
        0.9737127400000001,
        0.9895077999999999,
        0.99147414,
        1.0
      ],
      "timeline_states": [
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        false
      ],
      "voltage_min": 0.0401859746,
      "voltage_max": 11.4997328,
      "voltage_magnitude_min": 0.0401859746,
      "voltage_magnitude_max": 11.4997328,
      "time_window_s": 20.0
    },
    "scenario_profile": {
      "status": "measured",
      "source_component_id": "lamp13.1",
      "state": "blinking",
      "profile_method": "differential_voltage_relative_threshold",
      "positive_node": "N003",
      "negative_node": "0",
      "threshold_v": 5.7697332194,
      "on_fraction": 0.09711338160896736,
      "duty_cycle": 0.11530494831168063,
      "regular_period": true,
      "period_s": 0.5552144200000004,
      "frequency_hz": 1.8011059583070612,
      "pulse_count": 30,
      "timeline_key_times": [
        0.0,
        0.184028,
        0.18501880850000002,
        0.2003188085,
        0.20285545749999997,
        0.225398537,
        0.2284532395,
        0.2527891125,
        0.255998358,
        0.28065208799999997,
        0.28387932400000004,
        0.308372588,
        0.3115348575,
        0.33613093850000003,
        0.3393328355,
        0.364029114,
        0.36724538949999996,
        0.3918453895,
        0.3950453895,
        0.4196453895,
        0.42284538950000006,
        0.4474453895,
        0.45066366999999996,
        0.4752061105,
        0.478327539,
        0.5029190299999999,
        0.506154335,
        0.53064498,
        0.5338291749999999,
        0.558409155,
        0.561591475,
        0.5861551150000001,
        0.589432515,
        0.614089315,
        0.61737952,
        0.64197511,
        0.645167885,
        0.669797325,
        0.672963395,
        0.69755861,
        0.700699995,
        0.72527333,
        0.728491275,
        0.753022285,
        0.756166165,
        0.780691525,
        0.78387637,
        0.8084346050000001,
        0.8116881899999999,
        0.8363408099999999,
        0.839610485,
        0.8643009749999999,
        0.8676001400000001,
        0.8922001399999999,
        0.89533977,
        0.919892065,
        0.9231048100000001,
        0.94770481,
        0.9509498949999999,
        0.975449895,
        0.9786781449999999,
        1.0
      ],
      "timeline_states": [
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        fals
```

> Scenario artifact truncated in this preview.


## Loaded artifacts

### graph

- Step: `01`
- Role: Graph JSON copied from Pipeline 1.0.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic03\01_graph.json`

```json
{
  "image_id": "ic03",
  "image_name": "ic03.jpg",
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
      "state": "closed",
      "state_confidence": 0.75
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
      "component_id": "integrated_circuit11.1",
      "instance_id": "11.1",
      "class_name": "Integrated_Circuit",
      "terminals": [
        {
          "terminal_id": "integrated_circuit11.1_left_1",
          "name": "left_1",
          "relative_position": "left",
          "display_name": "LM317T left_1 IN",
          "pin_label": "IN"
        },
        {
          "terminal_id": "integrated_circuit11.1_right_1",
          "name": "right_1",
          "relative_position": "right",
          "display_name": "LM317T right_1 OUT",
          "pin_label": "OUT"
        },
        {
          "terminal_id": "integrated_circuit11.1_bottom_1",
          "name": "bottom_1",
          "relative_position": "bottom",
          "display_name": "LM317T bottom_1 ADJ",
          "pin_label": "ADJ"
        }
      ],
      "display_name": "LM317T",
      "ic_marking": "LM317T"
    },
    {
      "component_id": "polarized_capacitor20.2",
      "instance_id": "20.2",
      "class_name": "Polarized_Capacitor",
      "terminals": [
        {
          "terminal_id": "polarized_capacitor20.2_negative",
          "name": "negative",
          "relative_position": "left"
        },
        {
          "terminal_id": "polarized_capacitor20.2_positive",
          "name": "positive",
          "relative_position": "right"
        }
      ]
    },
    {
      "component_id": "polarized_capacitor20.3",
      "instance_id": "20.3",
      "class_name": "Polarized_Capacitor",
      "terminals": [
        {
          "terminal_id": "polarized_capacitor20.3_negative",
          "name": "negative",
          "relative_position": "left"
        },
        {
          "terminal_id": "polarized_capacitor20.3_positive",
          "name": "positive",
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
          "terminal_id": "polarized_capacitor20.4_negative",
          "name": "negative",
          "relative_position": "left"
        },
        {
          "terminal_id": "polarized_capacitor20.4_positive",
          "name": "positive",
          "relative_position": "right"
        }
      ]
    },
    {
      "component_id": "lamp13.1",
      "instance_id": "13.1",
      "class_name": "Lamp",
      "terminals": [
        {
          "terminal_id": "lamp13.1_t1",
          "name": "t1",
          "relative_position": "top"
        },
        {
          "terminal_id": "lamp13.1_t2",
          "name": "t2",
          "relative_position": "bottom"
        }
      ]
    }
  ],
  "terminal_metadata": {
    "integrated_circuit11.1_bottom_1": {
      "display_name": "LM317T bottom_1 ADJ",
      "pin_label": "ADJ",
      "component_display_name": "LM317T",
      "ic_marking": "LM317T",
      "component_id": "integrated_circuit11.1",
      "class_name": "Integrated_Circuit"
    },
    "integrated_circuit11.1_left_1": {
      "display_name": "LM317T left_1 IN",
      "pin_label": "IN",
      "component_display_name": "LM317T",
      "ic_marking": "LM317T",
      "component_id": "integrated_circuit11.1",
      "class_name": "Integrated_Circuit"
    },
    "integrated_circuit11.1_right_1": {
      "display_name": "LM317T right_1 OUT",
      "pin_label": "OUT",
      "component_display_name": "LM317T",
      "ic_marking": "LM317T",
      "component_id": "integrated_circuit11.1",
      "class_name": "Integrated_Circuit"
    }
  },
  "graph": {
    "gnd9.1_t1": [
      "lamp13.1_t2",
      "polarized_capacitor20.1_negative",
      "resistor22.2_t2",
      "terminal26.2_t1"
    ],
    "integrated_circuit11.1_bottom_1": [
      "polarized_capacitor20.3_negative",
      "resistor22.3_t1"
    ],
    "integrated_circuit11.1_left_1": [
      "polarized_capacitor20.1_positive",
      "switch25.1_t2"
    ],
    "integrated_circuit11.1_right_1": [
      "lamp13.1_t1",
      "polarized_capacitor20.2_positive",
      "polarized_capacitor20.3_positive",
      "polarized_capacitor20.4_positive"
    ],
    "lamp13.1_t1": [
      "integrated_circuit11.1_right_1",
      "polarized_capacitor20.2_positive",
      "polarized_capacitor20.3_positive",
      "polarized_capacitor20.4_positive"
    ],
    "lamp13.1_t2": [
      "gnd9.1_t1",
      "polarized_capacitor20.1_negative",
      "resistor22.2_t2",
      "terminal26.2_t1"
    ],
    "polarized_capacitor20.1_negative": [
      "gnd9.1_t1",
      "lamp13.1_t2",
      "resistor22.2_t2",
      "terminal26.2_t1"
    ],
    "polarized_capacitor20.1_positive": [
      "integrated_circuit11.1_left_1",
      "switch25.1_t2"
    ],
    "polarized_capacitor20.2_negative": [
      "resistor22.1_t1",
      "resistor22.3_t2"
    ],
    "polarized_capacitor20.2_positive": [
      "integrated_circuit11.1_right_1",
      "lamp13.1_t1",
      "polarized_capacitor20.3_positive",
      "polarized_capacitor20.4_positive"
    ],
    "polarized_capacitor20.3_negative": [
      "integrated_circuit11.1_bottom_1",
      "resistor22.3_t1"
    ],
    "polarized_capacitor20.3_positive": [
      "integrated_circuit11.1_right_1",
      "lamp13.1_t1",
      "polarized_capacitor20.2_positive",
      "polarized_capacitor20.4_positive"
    ],
    "polarized_capacitor20.4_negative": [
      "resistor22.1_t2",
      "resistor22.2_t1"
    ],
    "polarized_capacitor20.4_positive": [
      "integrated_circuit11.1_right_1",
      "lamp13.1_t1",
      "polarized_capacitor20.2_positive",
      "polarized_capacitor20.3_positive"
    ],
    "resistor22.1_t1": [
      "polarized_capacitor20.2_negative",
      "resistor22.3_t2"
    ],
    "resistor22.1_t2": [
      "polarized_capacitor20.4_negative",
      "resistor22.2_t1"
    ],
    "resistor22.2_t1": [
      "polarized_capacitor20.4_negative",
      "resistor22.1_t2"
    ],
    "resistor22.2_t2": [
      "gnd9.1_t1",
      "lamp13.1_t2",
      "polarized_capacitor20.1_negative",
      "terminal26.2_t1"
    ],
    "resistor22.3_t1": [
      "integrated_circuit11.1_bottom_1",
      "polarized_capacitor20.3_negative"
    ],
    "resistor22.3_t2": [
      "polarized_capacitor20.2_negative",
      "resistor22.1_t1"
    ],
    "switch25.1_t1": [
      "terminal26.1_t1"
    ],
    "switch25.1_t2": [
      "integrated_circuit11.1_left_1",
      "polarized_capacitor20.1_positive"
    ],
    "terminal26.1_t1": [
      "switch25.1_t1"
    ],
    "terminal26.2_t1": [
      "gnd9.1_t1",
      "lamp13.1_t2",
      "polarized_capacitor20.1_negative",
      "resistor22.2_t2"
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
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic03\03_node_map.json`

```json
{
  "circuit_id": "ic03",
  "source_format": "pipeline2.0_node_map",
  "nodes": [
    {
      "node_id": "0",
      "kind": "ground",
      "terminals": [
        "gnd9.1_t1",
        "lamp13.1_t2",
        "polarized_capacitor20.1_negative",
        "resistor22.2_t2",
        "terminal26.2_t1"
      ],
      "terminal_count": 5,
      "source_groups": [
        [
          "gnd9.1_t1",
          "lamp13.1_t2",
          "polarized_capacitor20.1_negative",
          "resistor22.2_t2",
          "terminal26.2_t1"
        ]
      ]
    },
    {
      "node_id": "N001",
      "kind": "normal",
      "terminals": [
        "integrated_circuit11.1_bottom_1",
        "polarized_capacitor20.3_negative",
        "resistor22.3_t1"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N002",
      "kind": "normal",
      "terminals": [
        "integrated_circuit11.1_left_1",
        "polarized_capacitor20.1_positive",
        "switch25.1_t2"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N003",
      "kind": "normal",
      "terminals": [
        "integrated_circuit11.1_right_1",
        "lamp13.1_t1",
        "polarized_capacitor20.2_positive",
        "polarized_capacitor20.3_positive",
        "polarized_capacitor20.4_positive"
      ],
      "terminal_count": 5
    },
    {
      "node_id": "N004",
      "kind": "normal",
      "terminals": [
        "polarized_capacitor20.2_negative",
        "resistor22.1_t1",
        "resistor22.3_t2"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N005",
      "kind": "normal",
      "terminals": [
        "polarized_capacitor20.4_negative",
        "resistor22.1_t2",
        "resistor22.2_t1"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N006",
      "kind": "normal",
      "terminals": [
        "switch25.1_t1",
        "terminal26.1_t1"
      ],
      "terminal_count": 2
    }
  ],
  "terminal_to_node": {
    "gnd9.1_t1": "0",
    "integrated_circuit11.1_bottom_1": "N001",
    "integrated_circuit11.1_left_1": "N002",
    "integrated_circuit11.1_right_1": "N003",
    "lamp13.1_t1": "N003",
    "lamp13.1_t2": "0",
    "polarized_capacitor20.1_negative": "0",
    "polarized_capacitor20.1_positive": "N002",
    "polarized_capacitor20.2_negative": "N004",
    "polarized_capacitor20.2_positive": "N003",
    "polarized_capacitor20.3_negative": "N001",
    "polarized_capacitor20.3_positive": "N003",
    "polarized_capacitor20.4_negative": "N005",
    "polarized_capacitor20.4_positive": "N003",
    "resistor22.1_t1": "N004",
    "resistor22.1_t2": "N005",
    "resistor22.2_t1": "N005",
    "resistor22.2_t2": "0",
    "resistor22.3_t1": "N001",
    "resistor22.3_t2": "N004",
    "switch25.1_t1": "N006",
    "switch25.1_t2": "N002",
    "terminal26.1_t1": "N006",
    "terminal26.2_t1": "0"
  },
  "component_terminal_nodes": {
    "gnd9.1": {
      "t1": "0"
    },
    "integrated_circuit11.1": {
      "left_1": "N002",
      "right_1": "N003",
      "bottom_1": "N001"
    },
    "lamp13.1": {
      "t1": "N003",
      "t2": "0"
    },
    "polarized_capacitor20.1": {
      "positive": "N002",
      "negative": "0"
    },
    "polarized_capacitor20.2": {
      "negative": "N004",
      "positive": "N003"
    },
    "polarized_capacitor20.3": {
      "negative": "N001",
      "positive": "N003"
    },
    "polarized_capacitor20.4": {
      "negative": "N005",
      "positive": "N003"
    },
    "resistor22.1": {
      "t1": "N004",
      "t2": "N005"
    },
    "resistor22.2": {
      "t1": "N005",
      "t2": "0"
    },
    "resistor22.3": {
      "t1": "N001",
      "t2": "N004"
    },
    "switch25.1": {
      "t1": "N006",
      "t2": "N002"
    },
    "terminal26.1": {
      "t1": "N006"
    },
    "terminal26.2": {
      "t1": "0"
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
    "nodes_count": 7,
    "normal_nodes_count": 6,
    "ground_nodes_count": 1,
    "ground_groups_count": 1,
    "terminal_to_node_count": 24,
    "singleton_nodes_count": 0
  }
}
```

### values_bound

- Step: `04`
- Role: Values and labels bound to graph components.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic03\04_values_bound.json`

```json
{
  "circuit_id": "ic03",
  "source_format": "pipeline2.0_values_bound",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\data\\batchPipeline2.0\\batchICChatAgentEvaluation\\values\\ic03_values.yaml",
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
      "node": "N006"
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
        "right_1": "N003",
        "bottom_1": "N001"
      },
      "value_data": {
        "model": "LM317_TRANS",
        "source": "ti_official_slvmc40_unencrypted_pspice_transient_model",
        "label_text": "IC1 LM317T; modello transitorio ufficiale TI Final 1.00",
        "viewer_override": {
          "label": "IC1",
          "display_value": "LM317T",
          "tooltip": "IC1 LM317T; modello transitorio ufficiale TI SLVMC40 Final 1.00"
        },
        "spice_override": {
          "emit_as": "subcircuit",
          "pin_order": [
            "IN",
            "ADJ",
            "OUT_0",
            "OUT_1"
          ],
          "node_refs": {
            "IN": "integrated_circuit11.1_left_1",
            "ADJ": "integrated_circuit11.1_bottom_1",
            "OUT_0": "integrated_circuit11.1_right_1",
            "OUT_1": "integrated_circuit11.1_right_1"
          },
          "resolved_node_refs": {
            "IN": "N002",
            "ADJ": "N001",
            "OUT_0": "N003",
            "OUT_1": "N003"
          }
        }
      },
      "status": "unsupported_for_now"
    },
    "lamp13.1": {
      "class_name": "Lamp",
      "terminal_nodes": {
        "t1": "N003",
        "t2": "0"
      },
      "value_data": {
        "nominal_voltage": 12,
        "nominal_voltage_unit": "V",
        "assumed_nominal_power": 12,
        "power_unit": "W",
        "source": "manual_testbench_assumption_using_documented_12w_limit",
        "label_text": "L1 lampada 12 V; equivalente assunto 12 ohm (12 W)",
        "spice_override": {
          "emit_as": "resistive_load",
          "equivalent_resistance": 12,
          "resistance_unit": "ohm",
          "node_order": [
            "t1",
            "t2"
          ],
          "semantic_role": "lamp_equivalent"
        },
        "viewer_override": {
          "visual_class": "lamp",
          "label": "L1",
          "display_value": "12 V Lamp",
          "tooltip": "Lampada 12 V; testbench SPICE resistivo 12 ohm, potenza assunta 12 W"
        }
      },
      "status": "bound"
    },
    "polarized_capacitor20.1": {
      "class_name": "Polarized_Capacitor",
      "terminal_nodes": {
        "positive": "N002",
        "negative": "0"
      },
      "value_data": {
        "value": 2.2,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C1 2.2 uF",
        "viewer_override": {
          "label": "C1",
          "display_value": "2.2 uF"
        }
      },
      "status": "bound"
    },
    "polarized_capacitor20.2": {
      "class_name": "Polarized_Capacitor",
      "terminal_nodes": {
        "negative": "N004",
        "positive": "N003"
      },
      "value_data": {
        "value": 10,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C3 10 uF",
        "viewer_override": {
          "label": "C3",
          "display_value": "10 uF"
        }
      },
      "status": "bound"
    },
    "polarized_capacitor20.3": {
      "class_name": "Polarized_Capacitor",
      "terminal_nodes": {
        "negative": "N001",
        "positive": "N003"
      },
      "value_data": {
        "value": 10,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C2 10 uF",
        "viewer_override": {
          "label": "C2",
          "display_value": "10 uF"
        }
      },
      "status": "bound"
    },
    "polarized_capacitor20.4": {
      "class_name": "Polarized_Capacitor",
      "terminal_nodes": {
        "negative": "N005",
        "positive": "N003"
      },
      "value_data": {
        "value": 10,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C4 10 uF",
        "viewer_override": {
          "label": "C4",
          "display_value": "10 uF"
        }
      },
      "status": "bound"
    },
    "resistor22.1": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N004",
        "t2": "N005"
      },
      "value_data": {
        "value": 10,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R2 10 kohm",
        "viewer_override": {
          "label": "R2",
          "display_value": "10 kohm"
        }
      },
      "status": "bound"
    },
    "resistor22.2": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N005",
        "t2": "0"
      },
      "value_data": {
        "value": 10,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R3 10 kohm",
        "viewer_override": {
          "label": "R3",
          "display_value": "10 kohm"
        }
      },
      "status": "bound"
    },
    "resistor22.3": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N001",
        "t2": "N004"
      },
      "value_data": {
        "value": 10,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R1 10 kohm",
        "viewer_override": {
          "label": "R1",
          "display_value": "10 kohm"
        }
      },
      "status": "bound"
    },
    "switch25.1": {
      "class_name": "Switch",
      "terminal_nodes": {
        "t1": "N006",
        "t2": "N002"
      },
      "value_data": {
        "state": "closed",
        "state_source": "graph_json_state",
        "state_confidence": 0.75,
        "source": "graph_json_state_validated_from_image",
        "label_text": "S1 chiuso",
        "viewer_override": {
          "label": "S1",
          "display_value": "closed"
        }
      },
      "status": "bound"
    },
    "terminal26.1": {
      "class_name": "Terminal",
      "terminal_nodes": {
        "t1": "N006"
      },
      "value_data": null,
      "status": "not_required"
    },
    "terminal26.2": {
      "class_name": "Terminal",
      "terminal_nodes": {
        "t1": "0"
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
    "integrated_circuit11.1_bottom_1": {
      "label": "REGULATOR_ADJ",
      "source": "manual_from_validated_graph_pin_adj",
      "node": "N001"
    },
    "integrated_circuit11.1_left_1": {
      "label": "REGULATOR_IN",
      "source": "manual_from_validated_graph_pin_in",
      "node": "N002"
    },
    "integrated_circuit11.1_right_1": {
      "label": "FLASH_OUTPUT",
      "source": "manual_from_validated_graph_pin_out",
      "node": "N003"
    },
    "polarized_capacitor20.2_negative": {
      "label": "TIMING_R1_R2",
      "source": "manual_from_validated_graph",
      "node": "N004"
    },
    "polarized_capacitor20.4_negative": {
      "label": "TIMING_R2_R3",
      "source": "manual_from_validated_graph",
      "node": "N005"
    },
    "terminal26.1_t1": {
      "label": "VCC_12",
      "source": "manual_from_image_label",
      "label_text": "+12 V DC",
      "node": "N006"
    },
    "terminal26.2_t1": {
      "label": "SUPPLY_RETURN",
      "source": "manual_from_image_ground_connection",
      "label_text": "Ritorno alimentazione a massa",
      "node": "0"
    }
  },
  "spice_topology_overlay": [],
  "simulation": {
    "analyses": [
      "tran"
    ],
    "tran": {
      "step": "2ms",
      "stop": "20s"
    }
  },
  "missing": [],
  "stats": {
    "components_total": 13,
    "bound_components": 9,
    "missing_components": 0,
    "not_required_components": 3,
    "unsupported_components": 1,
    "supplies_count": 1,
    "manual_nodes_count": 8
  }
}
```

### component_rules

- Step: `06`
- Role: SPICE conversion rules for each component.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic03\06_component_rules.json`

```json
{
  "circuit_id": "ic03",
  "source_format": "pipeline2.0_component_rules",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\data\\batchPipeline2.0\\batchICChatAgentEvaluation\\values\\ic03_values.yaml",
  "spice_classes_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_spice_classes.yaml",
  "supplies": {
    "VCC_12": {
      "status": "spice_ready",
      "spice_prefix": "V",
      "emit_as": "independent_voltage_source",
      "nodes": [
        "N006",
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
        "node": "N006"
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
        "IN",
        "ADJ",
        "OUT_0",
        "OUT_1"
      ],
      "nodes": [
        "N002",
        "N001",
        "N003",
        "N003"
      ],
      "parameters": {
        "model": "LM317_TRANS",
        "source": "ti_official_slvmc40_unencrypted_pspice_transient_model",
        "label_text": "IC1 LM317T; modello transitorio ufficiale TI Final 1.00",
        "viewer_override": {
          "label": "IC1",
          "display_value": "LM317T",
          "tooltip": "IC1 LM317T; modello transitorio ufficiale TI SLVMC40 Final 1.00"
        },
        "spice_override": {
          "emit_as": "subcircuit",
          "pin_order": [
            "IN",
            "ADJ",
            "OUT_0",
            "OUT_1"
          ],
          "node_refs": {
            "IN": "integrated_circuit11.1_left_1",
            "ADJ": "integrated_circuit11.1_bottom_1",
            "OUT_0": "integrated_circuit11.1_right_1",
            "OUT_1": "integrated_circuit11.1_right_1"
          },
          "resolved_node_refs": {
            "IN": "N002",
            "ADJ": "N001",
            "OUT_0": "N003",
            "OUT_1": "N003"
          }
        }
      },
      "reason": "Explicit YAML override emitted as a SPICE subcircuit."
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
        "N003",
        "0"
      ],
      "parameters": {
        "nominal_voltage": 12,
        "nominal_voltage_unit": "V",
        "assumed_nominal_power": 12,
        "power_unit": "W",
        "source": "manual_testbench_assumption_using_documented_12w_limit",
        "label_text": "L1 lampada 12 V; equivalente assunto 12 ohm (12 W)",
        "spice_override": {
          "emit_as": "resistive_load",
          "equivalent_resistance": 12,
          "resistance_unit": "ohm",
          "node_order": [
            "t1",
            "t2"
          ],
          "semantic_role": "lamp_equivalent"
        },
        "viewer_override": {
          "visual_class": "lamp",
          "label": "L1",
          "display_value": "12 V Lamp",
          "tooltip": "Lampada 12 V; testbench SPICE resistivo 12 ohm, potenza assunta 12 W"
        },
        "equivalent_resistance": 12,
        "resistance_unit": "ohm"
      },
      "reason": "Explicit YAML override emitted as an equivalent resistive load."
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
        "N002",
        "0"
      ],
      "parameters": {
        "value": 2.2,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C1 2.2 uF",
        "viewer_override": {
          "label": "C1",
          "display_value": "2.2 uF"
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
        "N003",
        "N004"
      ],
      "parameters": {
        "value": 10,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C3 10 uF",
        "viewer_override": {
          "label": "C3",
          "display_value": "10 uF"
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
        "N003",
        "N001"
      ],
      "parameters": {
        "value": 10,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C2 10 uF",
        "viewer_override": {
          "label": "C2",
          "display_value": "10 uF"
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
        "N003",
        "N005"
      ],
      "parameters": {
        "value": 10,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C4 10 uF",
        "viewer_override": {
          "label": "C4",
          "display_value": "10 uF"
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
        "N004",
        "N005"
      ],
      "parameters": {
        "value": 10,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R2 10 kohm",
        "viewer_override": {
          "label": "R2",
          "display_value": "10 kohm"
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
        "0"
      ],
      "parameters": {
        "value": 10,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R3 10 kohm",
        "viewer_override": {
          "label": "R3",
          "display_value": "10 kohm"
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
        "N001",
        "N004"
      ],
      "parameters": {
        "value": 10,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R1 10 kohm",
        "viewer_override": {
          "label": "R1",
          "display_value": "10 kohm"
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
        "N006",
        "N002"
      ],
      "parameters": {
        "state": "closed",
        "state_source": "graph_json_state",
        "state_confidence": 0.75,
        "source": "graph_json_state_validated_from_image",
        "label_text": "S1 chiuso",
        "viewer_override": {
          "label": "S1",
          "display_value": "closed"
        }
      },
      "strategy": "short_circuit"
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
    }
  },
  "simulation": {
    "analyses": [
      "tran"
    ],
    "tran": {
      "step": "2ms",
      "stop": "20s"
    }
  },
  "stats": {
    "components_total": 13,
    "spice_ready_components": 10,
    "not_emitted_components": 3,
    "measurement_components": 0,
    "missing_components": 0,
    "unsupported_components": 0,
    "pin_aware_components": 0,
    "invalid_components": 0,
    "supplies_ready_count": 1
  }
}
```

### netlist

- Step: `07`
- Role: Generated SPICE netlist.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic03\07_netlist.cir`

```spice
* pipeline2.0 netlist
* circuit: ic03

VVCC_12 N006 0 DC 12
Xintegrated_circuit11_1 N002 N001 N003 N003 LM317_TRANS
Rlamp13_1 N003 0 12
Cpolarized_capacitor20_1 N002 0 2.2u
Cpolarized_capacitor20_2 N003 N004 10u
Cpolarized_capacitor20_3 N003 N001 10u
Cpolarized_capacitor20_4 N003 N005 10u
Rresistor22_1 N004 N005 10k
Rresistor22_2 N005 0 10k
Rresistor22_3 N001 N004 10k
Rswitch25_1 N006 N002 1m

.include "07_external_models.lib"

.save all
.tran 2ms 20s

.control
set wr_singlescale
set wr_vecnames
run
wrdata 08_tran.csv time v(N001) v(N002) v(N003) v(N004) v(N005) v(N006)
.endc
.end

```

### spice_emit_report

- Step: `07`
- Role: Report of emitted, skipped and warning components.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic03\07_spice_emit_report.json`

```json
{
  "circuit_id": "ic03",
  "source_format": "pipeline2.0_spice_emit_report",
  "emitted_elements": 11,
  "skipped_elements": 3,
  "skipped_components": [
    "gnd9.1",
    "terminal26.1",
    "terminal26.2"
  ],
  "informational_skips": [
    "gnd9.1: structural component not emitted",
    "terminal26.1: structural component not emitted",
    "terminal26.2: structural component not emitted"
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
      "N006"
    ],
    "device_currents": []
  },
  "models": [
    "LM317_TRANS"
  ],
  "warnings": [],
  "external_model_sources": [
    {
      "model": "LM317_TRANS",
      "kind": "file",
      "file": "spice_models/ti/lm317/slvmc40/LM317_TRANS.LIB",
      "sha256": "9B56D7C68B75D3C0FD1E0B55F5DDC448F89F82984F026FF31ACDF89BDE4BD7E1",
      "encoding": "cp1252"
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
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic03\08_spice_run.json`

```json
{
  "source_format": "pipeline2.0_spice_run",
  "status": "success",
  "netlist_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\pipeline2.0\\ic03\\07_netlist.cir",
  "command": [
    "C:\\Users\\m.profilo\\Spice64\\bin\\ngspice_con.exe",
    "-D",
    "ngbehavior=ps",
    "-b",
    "07_netlist.cir"
  ],
  "exit_code": 0,
  "stdout_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\pipeline2.0\\ic03\\08_ngspice_stdout.txt",
  "stderr_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\pipeline2.0\\ic03\\08_ngspice_stderr.txt",
  "tran_raw_csv_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\pipeline2.0\\ic03\\08_tran_raw.csv",
  "tran_csv_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\pipeline2.0\\ic03\\08_tran.csv",
  "tran_plot_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\pipeline2.0\\ic03\\08_tran_plot.png",
  "tran_plot_png_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\pipeline2.0\\ic03\\08_tran_plot.png",
  "tran_plot_svg_path": null,
  "message": "ngspice completed successfully."
}
```

### ngspice_stdout

- Step: `08`
- Role: Raw ngspice stdout log.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic03\08_ngspice_stdout.txt`

```text
Note: gnd in a subcircuit is not set to 0 automatically

Note: Compatibility modes selected: ps


Circuit: * pipeline2.0 netlist

Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

Initial Transient Solution
--------------------------

Node                                   Voltage
----                                   -------
n006                                        12
xintegrated_circuit11_1.vxx            1.25854
n002                                   11.9999
xintegrated_circuit11_1.n242982         1.25854
xintegrated_circuit11_1.vyy            1.25854
xintegrated_circuit11_1.vzz             1.2585
xintegrated_circuit11_1.e_abm1_int1         1.25854
xintegrated_circuit11_1.n222524         1.25001
xintegrated_circuit11_1.u1_n26728            1.25
xintegrated_circuit11_1.u1_n31197            1.25
xintegrated_circuit11_1.e_u1_abm5_int1            1.25
xintegrated_circuit11_1.u1_n08257            1.25
xintegrated_circuit11_1.u1_n28933            1.25
xintegrated_circuit11_1.x_u1_u2.inp1               0
xintegrated_circuit11_1.x_u1_u2.inm1        -11.9999
xintegrated_circuit11_1.u1_n12783               0
xintegrated_circuit11_1.x_u1_u2.inp2               0
xintegrated_circuit11_1.x_u1_u2.ehys_int1               0
xintegrated_circuit11_1.x_u1_u2.1               1
xintegrated_circuit11_1.u1_n12664               0
xintegrated_circuit11_1.u1_uvlo_ok               1
xintegrated_circuit11_1.x_u1_u2.eout_int1               1
xintegrated_circuit11_1.u1_en_out            1.25
xintegrated_circuit11_1.e_u1_abm6_int1            1.25
xintegrated_circuit11_1.e_u1_abm4_int1            1.25
n003                                    1.2585
n001                                         0
n004                                         0
n005                                         0
b.xintegrated_circuit11_1.be_u1_abm4#branch               0
b.xintegrated_circuit11_1.be_u1_abm6#branch               0
b.xintegrated_circuit11_1.x_u1_u2.beout#branch               0
b.xintegrated_circuit11_1.x_u1_u2.behys#branch               0
b.xintegrated_circuit11_1.be_u1_abm5#branch               0
b.xintegrated_circuit11_1.be_abm1#branch               0
v.xintegrated_circuit11_1.x_f1.vf_f1#branch        0.104875
e.xintegrated_circuit11_1.e_u1_abm4#branch       -1.25e-09
e.xintegrated_circuit11_1.e_u1_abm6#branch       -1.25e-09
e.xintegrated_circuit11_1.x_u1_u2.eout#branch               0
e.xintegrated_circuit11_1.x_u1_u2.ehys#branch               0
e.xintegrated_circuit11_1.x_u1_u2.ein#branch               0
e.xintegrated_circuit11_1.e_u1_abm5#branch     1.07414e-06
e.xintegrated_circuit11_1.e_abm1#branch     5.76622e-13
v.xintegrated_circuit11_1.v_u1_v3#branch               0
v.xintegrated_circuit11_1.v_u1_v4#branch               0
vvcc_12#branch                       -0.104876


No. of Data Rows : 10144
Note: Simulation executed from .control section 

```

### ngspice_stderr

- Step: `08`
- Role: Raw ngspice stderr log.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic03\08_ngspice_stderr.txt`

```text

```

### tran_csv

- Step: `08`
- Role: Clean transient CSV, when .tran data is available.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic03\08_tran.csv`

```csv
time,v(N001),v(N002),v(N003),v(N004),v(N005),v(N006)
0.0,0.0,11.9998951,1.25849669,0.0,0.0,12.0
2e-05,-5.95010485e-10,11.9998951,1.25849669,-5.95010929e-10,-5.94891691e-10,12.0
4e-05,-7.14707404e-10,11.9998951,1.25849669,-7.14707848e-10,-7.14445614e-10,12.0
8e-05,-7.63042962e-10,11.9998951,1.25849669,-7.63043184e-10,-7.62485408e-10,12.0
0.00016,-7.02170544e-10,11.9998951,1.25849669,-7.021701e-10,-7.01028124e-10,12.0
0.00032,-9.99447192e-10,11.9998951,1.25849669,-9.99443861e-10,-9.96948746e-10,12.0
0.00064,-1.35914169e-10,11.9998951,1.25849669,-1.35899514e-10,-1.31620714e-10,12.0
0.00128,-7.53566098e-10,11.9998951,1.25849669,-7.53515472e-10,-7.46499085e-10,12.0
0.00256,-8.19991852e-10,11.9998951,1.25849669,-8.19793122e-10,-8.03160649e-10,12.0
0.00456,-4.5157833e-10,11.9998951,1.25849669,-4.509495e-10,-4.22941016e-10,12.0
0.00656,-5.3464011e-10,11.9998951,1.25849669,-5.33408651e-10,-4.97457409e-10,12.0
0.00856,-4.45826487e-10,11.9998951,1.25849669,-4.43865389e-10,-4.00489419e-10,12.0
0.01056,-5.23375343e-10,11.9998951,1.25849669,-5.20572918e-10,-4.7031401e-10,12.0
0.01256,-4.3191406e-10,11.9998951,1.25849669,-4.28173941e-10,-3.7156811e-10,12.0
0.01456,-5.02794029e-10,11.9998951,1.25849669,-4.98033836e-10,-4.35650627e-10,12.0
0.01656,-4.07598177e-10,11.9998951,1.25849669,-4.01750411e-10,-3.34162475e-10,12.0
0.01856,-4.71111816e-10,11.9998951,1.25849669,-4.64123406e-10,-3.91940924e-10,12.0
0.02056,-3.71554343e-10,11.9998951,1.25849669,-3.63385544e-10,-2.87226021e-10,12.0
0.02256,-4.27206936e-10,11.9998951,1.25849669,-4.17832879e-10,-3.383549e-10,12.0
0.02456,-3.22883942e-10,11.9998951,1.25849669,-3.12293746e-10,-2.30163e-10,12.0
0.02656,-3.70651732e-10,11.9998951,1.25849669,-3.5884784e-10,-2.7476732e-10,12.0
0.02856,-2.61412003e-10,11.9998951,1.25849669,-2.48410847e-10,-1.63090874e-10,12.0
0.03056,-3.01344949e-10,11.9998951,1.25849669,-2.87176061e-10,-2.0136226e-10,12.0
0.03256,-1.87551086e-10,11.9998951,1.25849669,-1.72257986e-10,-8.66959837e-11,12.0
0.03456,-2.19916751e-10,11.9998951,1.25849669,-2.03556061e-10,-1.19021681e-10,12.0
0.03656,-1.02020614e-10,11.9998951,1.25849669,-8.46616111e-11,-1.92579286e-12,12.0
0.03856,-1.27800215e-10,11.9998951,1.25849669,-1.09524834e-10,-2.93776115e-11,12.0
0.04056,-6.52589094e-12,11.9998951,1.25849669,1.25712774e-11,8.93536356e-11,12.0
0.04256,-2.64230859e-11,11.9998951,1.25849669,-6.61004584e-12,6.60194122e-11,12.0
0.04456,9.70901137e-11,11.9998951,1.25849669,1.17502008e-10,1.85214732e-10,12.0
0.04656,8.17605983e-11,11.9998951,1.25849669,1.02643449e-10,1.64675829e-10,12.0
0.04856,2.06355821e-10,11.9998951,1.25849669,2.27572849e-10,2.83194801e-10,12.0
0.05056,1.94265937e-10,11.9998951,1.25849669,2.15671259e-10,2.64164024e-10,12.0
0.05256,3.18408411e-10,11.9998951,1.25849669,3.39849038e-10,3.80539156e-10,12.0
0.05456,3.07730952e-10,11.9998951,1.25849669,3.29046346e-10,3.61286334e-10,12.0
0.05656,4.29896119e-10,11.9998951,1.25849669,4.50919302e-10,4.74119188e-10,12.0
0.05856,4.19112745e-10,11.9998951,1.25849669,4.39672521e-10,4.5327786e-10,12.0
0.06056,5.37492273e-10,11.9998951,1.25849669,5.57413893e-10,5.60939073e-10,12.0
0.06256,5.24623678e-10,11.9998951,1.25849669,5.43729506e-10,5.36737543e-10,12.0
0.06456,6.37492947e-10,11.9998951,1.25849669,6.55605348e-10,6.37737863e-10,12.0
0.06656,6.20650864e-10,11.9998951,1.25849669,6.37592645e-10,6.08550987e-10,12.0
0.06856,7.26013027e-10,11.9998951,1.25849669,7.41609663e-10,7.0118511e-10,12.0
0.07056,7.03380687e-10,11.9998951,1.25849669,7.17459647e-10,6.65512978e-10,12.0
0.07256,7.99467825e-10,11.9998951,1.25849669,8.11862577e-10,7.48351603e-10,12.0
0.07456,7.69120989e-10,11.9998951,1.25849669,7.79670994e-10,7.0463102e-10,12.0
0.07656,8.54386561e-10,11.9998951,1.25849669,8.62939498e-10,7.76509079e-10,12.0
0.07856,8.14682544e-10,11.9998951,1.25849669,8.2109608e-10,7.2349593e-10,12.0
0.08056,8.87330431e-10,11.9998951,1.25849669,8.91472451e-10,7.83033416e-10,12.0
0.08256,8.36917202e-10,11.9998951,1.25849669,8.38668468e-10,7.19806215e-10,12.0
0.08456,8.95810315e-10,11.9998951,1.25849669,8.95065133e-10,7.66304353e-10,12.0
0.08656,8.33318081e-10,11.9998951,1.25849669,8.29986746e-10,6.91938951e-10,12.0
0.08856,8.77504958e-10,11.9998951,1.25849669,8.71513306e-10,7.24897475e-10,12.0
0.09056,8.02185873e-10,11.9998951,1.25849669,7.93477728e-10,6.39095665e-10,12.0
0.09256,8.30832958e-10,11.9998951,1.25849669,8.19371904e-10,6.58128663e-10,12.0
0.09456,7.4211326e-10,11.9998951,1.25849669,7.27882421e-10,5.60760771e-10,12.0
0.09656,7.55221219e-10,11.9998951,1.25849669,7.38224148e-10,5.66300784e-10,12.0
0.09856,6.5307848e-10,11.9998951,1.25849669,6.33340713e-10,4.5775983e-10,12.0
0.10056,6.50511645e-10,11.9998951,1.25849669,6.28081365e-10,4.50072202e-10,12.0
0.10256,5.35262057e-10,11.9998951,1.25849669,5.10209652e-10,3.31057626e-10,12.0
0.10456,5.1788307e-10,11.9998951,1.25849669,4.90302021e-10,3.11361603e-10,12.0
0.10656,3.90345312e-10,11.9998951,1.25849669,3.60352859e-10,1.83018711e-10,12.0
0.10856,3.59221097e-10,11.9998951,1.25849669,3.2695735e-10,1.52676316e-10,12.0
0.11056,2.20703678e-10,11.9998951,1.25849669,1.86332061e-10,1.65731873e-11,12.0
0.11256,1.77390103e-10,11.9998951,1.25849669,1.4109669e-10,-2.26376695e-11,12.0
0.11456,2.98441272e-11,11.9998951,1.25849669,-8.16302581e-12,-1.64370961e-10,12.0
0.11656,-2.33240094e-11,11.9998951,1.25849669,-6.28155306e-11,-2.09986917e-10,12.0
0.11856,-1.77690751e-10,11.9998951,1.25849669,-2.1841684e-10,-3.55063534e-10,12.0
0.12056,-2.38394637e-10,11.9998951,1.25849669,-2.80085954e-10,-4.04733136e-10,12.0
0.12256,-3.96910282e-10,11.9998951,1.25849669,-4.3927928e-10,-5.50497203e-10,12.0
0.12456,-4.62203165e-10,11.9998951,1.25849669,-5.04946529e-10,-6.01344308e-10,12.0
0.12656,-6.21679375e-10,11.9998951,1.25849669,-6.64478472e-10,-7.44738049e-10,12.0
0.12856,-6.88203494e-10,11.9998951,1.25849669,-7.30727701e-10,-7.93594523e-10,12.0
0.13056,-8.45348014e-10,11.9998951,1.25849669,-8.87255158e-10,-9.3157082e-10,12.0
0.13256,-9.09544662e-10,11.9998951,1.25849669,-9.50484802e-10,-9.75181491e-10,12.0
0.13456,-1.06063713e-09,11.9998951,1.25849669,-1.10025455e-09,-1.10438436e-09,12.0
0.13656,-1.11872422e-09,11.9998951,1.25849669,-1.15665966e-09,-1.13938925e-09,12.0
0.13856,-1.25999811e-09,11.9998951,1.25849669,-1.29589139e-09,-1.25653177e-09,12.0
0.14056,-1.30818711e-09,11.9998951,1.25849669,-1.34167943e-09,-1.27967836e-09,12.0
0.14256,-1.43594781e-09,11.9998951,1.25849669,-1.46668544e-09,-1.38165346e-09,12.0
0.14456,-1.47056256e-09,11.9998951,1.25849669,-1.49819956e-09,-1.38990197e-09,12.0
0.14656,-1.58111657e-09,11.9998951,1.25849669,-1.60531788e-09,-1.47370094e-09,12.0
0.14856,-1.59840452e-09,11.9998951,1.25849669,-1.61884883e-09,-1.46402979e-09,12.0
0.15056,-1.68830638e-09,11.9998951,1.25849669,-1.70468928e-09,-1.52697854e-09,12.0
0.15256,-1.68503811e-09,11.9998951,1.25849669,-1.6970747e-09,-1.49696477e-09,12.0
0.15456,-1.75126691e-09,11.9998951,1.25849669,-1.75869519e-09,-1.53687973e-09,12.0
0.15656,-1.72454762e-09,11.9998951,1.25849669,-1.72713088e-09,-1.48449075e-09,12.0
0.15856,-1.76444215e-09,11.9998951,1.25849669,-1.76197301e-09,-1.49959312e-09,12.0
0.16056,-1.71186154e-09,11.9998951,1.25849669,-1.7041637e-09,-1.42331746e-09,12.0
0.16256,-1.72334769e-09,11.9998951,1.25849669,-1.71027814e-09,-1.41244083e-09,12.0
0.16456,-1.64329483e-09,11.9998951,1.25849669,-1.62474745e-09,-1.31157418e-09,12.0
0.16656,-1.62507452e-09,11.9998951,1.25849669,-1.60098179e-09,-1.27431998e-09,12.0
0.16856,-1.51652468e-09,11.9998951,1.25849669,-1.4868593e-09,-1.14872534e-09,12.0
0.17056,-1.46825974e-09,11.9998951,1.25849669,-1.43303636e-09,-1.08562137e-09,12.0
0.17256,-1.33119871e-09,11.9998951,1.25849669,-1.29047617e-09,-9.3612007e-10,12.0
0.17456,-1.25317023e-09,11.9998951,1.25849669,-1.20705312e-09,-8.48248138e-10,12.0
0.17656,-1.08842335e-09,11.9998951,1.25849669,-1.03706155e-09,-6.76423584e-10,12.0
0.17856,-9.82068205e-10,11.9998951,1.25849669,-9.25658439e-10,-5.65926195e-10,12.0
0.18056,-7.91409382e-10,11.9998951,1.25849669,-7.30194794e-10,-3.74199782e-10,12.0
0.18256,-6.59025501e-10,11.9998951,1.25849669,-5.93296301e-10,-2.43957299e-10,12.0
0.18456,-4.45320447e-10,11.9998951,1.25849669,-3.75413922e-10,-3.57027741e-11,12.0
0.18656,-2.90254043e-10,11.9998951,1.25849669,-2.1655211e-10,1.105116e-10,12.0
0.18856,-5.7337024e-11,11.9998951,1.25849669,1.97337702e-11,3.3112002e-10,12.0
0.19056,1.16209264e-10,11.9998951,1.25849669,1.96180183e-10,4.88855623e-10,12.0
0.19256,3.63768793e-10,11.9998951,1.25849669,4.46129356e-10,7.17095938e-10,12.0
0.19456,5.50588686e-10,11.9998951,1.25849669,6.34789998e-10,8.81095641e-10,12.0
0.19656,8.07039768e-10,11.9998951,1.25849669,8.92498742e-10,1.11127596e-09,12.0
0.19856,1.0010146e-09,11.9998951,1.25849669,1.08711506e-09,1.27559407e-09,12.0
0.20056,1.26039046e-09,11.9998951,1.25849669,1.34648737e-09,1.50203139e-09,12.0
0.20256,1.45489176e-09,11.9998951,1.25849669,1.54031543e-09,1.66043579e-09,12.0
0.20456,1.70994818e-09,11.9998951,1.25849669,1.79400717e-09,1.8764037e-09,12.0
0.20656,1.89812543e-09,11.9998951,1.25849669,1.9801123e-09,2.02267958e-09,12.0
0.20856,2.14164131e-09,11.9998951,1.25849669,2.22083862e-09,2.22170549e-09,12.0
0.21056,2.3155251e-09,11.9998951,1.25849669,2.39120901e-09,2.34875253e-09,12.0
0.21256,2.53980459e-09,11.9998951,1.25849669,2.61124988e-09,2.5241278e-09,12.0
0.21456,2.69197731e-09,11.9998951,1.25849669,2.75846412e-09,2.62562327e-09,12.0
0.21656,2.88956858e-09,11.9998951,1.25849669,2.95038749e-09,2.77109513e-09,12.0
0.21856,3.01249403e-09,11.9998951,1.25849669,3.06695291e-09,2.84080315e-09,12.0
0.22056,3.17591575e-09,11.9998951,1.25849669,3.22334492e-09,2.95028735e-09,12.0
0.22256,3.26234262e-09,11.9998951,1.25849669,3.30210082e-09,2.98244252e-09,12.0
0.22456,3.38473694e-09,11.9998951,1.25849669,3.41621798e-09,3.0506464e-09,12.0
0.22656,3.42806716e-09,11.9998951,1.25849669,3.45070572e-09,3.04028624e-09,12.0
0.22856,3.50329343e-09,11.9998951,1.25849669,3.51657103e-09,3.06276515e-09,12.0
0.23056,3.49793239e-09,11.9998951,1.25849669,3.50138363e-09,3.00604031e-09,12.0
0.23256,3.52081186e-09,11.9998951,1.25849669,3.51402973e-09,2.97939851e-09,12.0
0.23456,3.46203355e-09,11.9998951,1.25849669,3.44467477e-09,2.87339308e-09,12.0
0.23656,3.42865647e-09,11.9998951,1.25849669,3.40044726e-09,2.79554446e-09,12.0
0.23856,3.31319439e-09,11.9998951,1.25849669,3.27393401e-09,2.63881361e-09,12.0
0.24056,3.22110827e-09,11.9998951,1.25849669,3.17067417e-09,2.50911203e-09,12.0
0.24256,3.04735814e-09,11.9998951,1.25849669,2.98571057e-09,2.30182806e-09,12.0
0.24456,2.89564106e-09,11.9998951,1.25849669,2.82282597e-09,2.12108264e-09,12.0
0.24656,2.66357225e-09,11.9998951,1.25849669,2.57972377e-09,1.8648858e-09,12.0
0.24856,2.45329601e-09,11.9998951,1.25849669,2.35863995e-09,1.63576441e-09,12.0
0.25056,2.16470264e-09,11.9998951,1.25849669,2.05955764e-09,1.3339565e-09,12.0
0.25256,1.89848626e-09,11.9998951,1.25849669,1.78326487e-09,1.06048303e-09,12.0
0.25456,1.55755453e-09,11.9998951,1.25849669,1.43276324e-09,7.18531679e-10,12.0
0.25656,1.24044197e-09,11.9998951,1.25849669,1.10668141e-09,4.06890521e-10,12.0
0.25856,8.5259777e-10,11.9998951,1.25849669,7.1056161e-10,3.12139203e-11,12.0
0.26056,4.91462648e-10,11.9998951,1.25849669,3.41936257e-10,-3.10887316e-10,12.0
0.26256,6.47861764e-11,11.9998951,1.25849669,-9.1356922e-11,-7.11553039e-10,12.0
0.26456,-3.31620509e-10,11.9998951,1.25849669,-4.93421304e-10,-1.07489928e-09,12.0
0.26656,-7.87805599e-10,11.9998951,1.25849669,-9.54224255e-10,-1.49096135e-09,12.0
0.26856,-1.20897514e-09,11.9998951,1.25849669,-1.37889478e-09,-1.8649795e-09,12.0
0.27056,-1.6830235e-09,11.9998951,1.25849669,-1.85525795e-09,-2.28494912e-09,12.0
0.27256,-2.11683471e-09,11.9998951,1.25849668,-2.29013319e-09,-2.65790145e-09,12.0
0.27456,-2.59599831e-09,11.9998951,1.25849668,-2.76905299e-09,-3.06964232e-09,12.0
0.27656,-3.02893022e-09,11.9998951,1.25849668,-3.20038551e-09,-3.42885342e-09,12.0
0.27856,-3.49909635e-09,11.9998951,1.25849668,-3.66755604e-09,-3.81933551e-09,12.0
0.28056,-3.91658594e-09,11.9998951,1.25849668,-4.08062295e-09,-4
```

> Artifact truncated in this preview. The original file remains available through the manifest path.
