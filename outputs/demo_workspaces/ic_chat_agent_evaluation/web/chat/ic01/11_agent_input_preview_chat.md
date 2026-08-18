# Agent input preview

This file is a local preview of the evidence that will be provided to the read-only diagnostic agent.
The agent remains read-only: it can inspect base outputs and existing scenario artifacts, but it does not modify files.

## User problem

Interpreta il risultato dello scenario 2 e dammi la conclusione finale, senza proporre altri scenari.

## Circuit

- Batch: `batchICChatAgentEvaluation`
- Circuit: `ic01`
- Agent mode: `graph_grounded_readonly`

## Technical summary

```json
{
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_message": "ngspice completed successfully.",
  "emitted_elements": 9,
  "skipped_elements": 2,
  "emit_warnings_count": 0,
  "skipped_components_count": 2,
  "node_count": 7,
  "ground_groups_count": 1,
  "singleton_nodes_count": 0,
  "bound_components": 7,
  "missing_components": 0,
  "unsupported_components": 1,
  "spice_ready_components": 8,
  "rules_missing_components": 0,
  "has_tran_csv": true,
  "has_tran_plot": true,
  "led_profiles": {
    "Dled12_1": {
      "state": "transient_pulse",
      "regular_period": false,
      "frequency_hz": null,
      "duty_cycle": 0.5147793334970933,
      "on_fraction": 0.5147793334970933,
      "pulse_count": 63,
      "voltage_min": -0.0342456757,
      "voltage_max": 0.708918299,
      "anode_node": "N006",
      "cathode_node": "0"
    }
  }
}
```

## Image policy

- Included by default: `False`
- Can be requested: `True`
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\input\images\ic01.jpg`
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
  "best_outcome_status": "resolved_candidate",
  "best_stop_automation": true,
  "ranking_status": "verified_best",
  "interpretation_rule": "If a user asks which scenario resolves the problem, prefer the scenario with outcome_status='resolved_candidate' and stop_automation=true. Partially resolved scenarios without verified expectations are supporting diagnostics and must not be ranked only by changed_count.",
  "scenarios": [
    {
      "scenario_id": "scenario_2",
      "title": "Ridurre l'influenza del ramo di controllo sul pin CONT",
      "status": "spice_success",
      "spice_status": "success",
      "outcome_status": "resolved_candidate",
      "outcome_label": "Criteri elettrici e temporali soddisfatti",
      "outcome_technical_label": "Transient correction verified",
      "outcome_reason": "Le aspettative elettriche e il profilo transitorio richiesto sono verificati.",
      "stop_automation": true,
      "comparison_summary": {
        "requested_count": 4,
        "changed_count": 4,
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
          "v(N002)",
          "v(N005)",
          "v(N006)",
          "@dled12_1[id]"
        ],
        "unchanged": [],
        "missing": []
      },
      "led_profiles": {
        "Dled12_1": {
          "state": "blinking",
          "regular_period": true,
          "frequency_hz": 478.1151286408193,
          "duty_cycle": 0.662196720517488,
          "on_fraction": 0.6004169272461956,
          "pulse_count": 51,
          "voltage_min": -0.0245919331,
          "voltage_max": 0.708935271,
          "anode_node": "N006",
          "cathode_node": "0"
        }
      },
      "ranking_verified": true,
      "score": 195
    }
  ]
}
```


## Executed scenarios

### scenario_2

- Title: `Ridurre l'influenza del ramo di controllo sul pin CONT`
- Status: `spice_success`
- SPICE status: `success`
- Outcome: `resolved_candidate`
- Stop automation: `True`
- Comparison: `4/4` changed
- LED profiles: `{"Dled12_1": {"state": "blinking", "regular_period": true, "frequency_hz": 478.1151286408193, "duty_cycle": 0.662196720517488, "on_fraction": 0.6004169272461956, "pulse_count": 51, "voltage_min": -0.0245919331, "voltage_max": 0.708935271, "anode_node": "N006", "cathode_node": "0"}}`

#### scenario_definition

- Role: Scenario selected by the user and saved before execution.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic01\scenarios\scenario_2\scenario.json`

```json
{
  "scenario_id": "scenario_2",
  "title": "Ridurre l'influenza del ramo di controllo sul pin CONT",
  "hypothesis": "Il condensatore Ccapacitor4_2 sul nodo N002 (CONT) contribuisce all'irregolarita di startup del 555.",
  "intent": "correction",
  "actions": [
    {
      "type": "change_component_value",
      "target": "Ccapacitor4_2",
      "value": "100n"
    }
  ],
  "rerun_from": "07",
  "analysis": "tran",
  "compare": [
    "v(N002)",
    "v(N005)",
    "v(N006)",
    "@dled12_1[id]"
  ],
  "expect": {
    "v(N002)": "changed",
    "v(N006)": "changed",
    "@dled12_1[id]": "changed"
  },
  "measure": {
    "@dled12_1[id]": "tran_abs_peak"
  },
  "temporal_expect": {
    "target": "Dled12_1",
    "required_state": "blinking",
    "require_regular_period": true
  }
}
```

#### scenario_status

- Role: Current scenario status, SPICE status and diagnostic outcome.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic01\scenarios\scenario_2\scenario_status.json`

```json
{
  "status": "spice_success",
  "stage": "scenario_spice_executed",
  "scenario_id": "scenario_2",
  "source": "guided_chat",
  "spice_executed": true,
  "created_or_updated_at": "2026-07-30T11:54:45",
  "message": "Scenario actions were applied and ngspice was executed on the scenario run.",
  "spice_status": "success",
  "spice_exit_code": 0,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic01\\scenarios\\scenario_2\\run\\08_spice_run.json",
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic01\\scenarios\\scenario_2\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 4,
    "changed_count": 4,
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
  "controlled_scenario_report": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic01\\scenarios\\scenario_2\\12_controlled_scenarios.json",
  "executed_scenarios_count": 1,
  "scenario_budget_exhausted": false,
  "next_step": "La correzione e verificata: puoi passare alla conclusione diagnostica."
}
```

#### controlled_scenario_report

- Role: Report produced by the controlled scenario runner.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic01\scenarios\scenario_2\12_controlled_scenarios.json`

```json
{
  "source_format": "pipeline2.0_controlled_scenario_report",
  "status": "spice_success",
  "scenario_id": "scenario_2",
  "scenario_title": "Ridurre l'influenza del ramo di controllo sul pin CONT",
  "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic01\\scenarios\\scenario_2",
  "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic01\\scenarios\\scenario_2\\run",
  "netlist": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic01\\scenarios\\scenario_2\\run\\07_netlist.cir",
  "applied_actions": [
    {
      "status": "applied",
      "type": "change_component_value",
      "target": "Ccapacitor4_2",
      "resolved_component_name": "Ccapacitor4_2",
      "tried_component_names": [
        "Ccapacitor4_2"
      ],
      "value": "100n",
      "normalized_component_value": "100n",
      "old_value": "1u",
      "new_value": "100n",
      "old_line": "Ccapacitor4_2 N002 0 1u",
      "new_line": "Ccapacitor4_2 N002 0 100n",
      "operation": "updated",
      "spice_executed": false,
      "index": 1
    }
  ],
  "unsupported_actions": [],
  "failed_actions": [],
  "spice_executed": true,
  "spice_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic01\\scenarios\\scenario_2\\run\\08_spice_run.json",
  "spice_status": "success",
  "spice_exit_code": 0,
  "comparison_report_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic01\\scenarios\\scenario_2\\scenario_comparison.json",
  "comparison_summary": {
    "requested_count": 4,
    "changed_count": 4,
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
  "created_or_updated_at": "2026-07-30T11:54:45"
}
```

#### scenario_comparison

- Role: Base-vs-scenario comparison used to evaluate the scenario.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic01\scenarios\scenario_2\scenario_comparison.json`

```json
{
  "source_format": "pipeline2.0_scenario_comparison",
  "scenario_id": "scenario_2",
  "scenario_title": "Ridurre l'influenza del ramo di controllo sul pin CONT",
  "scenario_intent": "correction",
  "base_output_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic01",
  "scenario_run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic01\\scenarios\\scenario_2\\run",
  "base_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic01\\08_ngspice_stdout.txt",
  "scenario_stdout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic01\\scenarios\\scenario_2\\run\\08_ngspice_stdout.txt",
  "base_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic01\\08_ngspice_stderr.txt",
  "scenario_stderr": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\chat\\ic01\\scenarios\\scenario_2\\run\\08_ngspice_stderr.txt",
  "quantities": [
    {
      "quantity": "v(N002)",
      "base_value": 5.8789549012,
      "scenario_value": 5.9086817436,
      "delta": 0.029726842399999676,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 0.005056484171010037,
      "meaningful_improvement": false,
      "metric": "v(n002).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": 0.0581162788,
        "max": 5.93707118,
        "mean": 4.721224077740826,
        "vpp": 5.8789549012,
        "final": 5.93707118,
        "abs_peak": 5.93707118
      },
      "scenario_details": {
        "min": 0.0913174464,
        "max": 5.99999919,
        "mean": 5.854647357946375,
        "vpp": 5.9086817436,
        "final": 5.99999898,
        "abs_peak": 5.99999919
      }
    },
    {
      "quantity": "v(N005)",
      "base_value": 8.6686471958,
      "scenario_value": 8.5716687132,
      "delta": -0.09697848260000086,
      "change": "changed",
      "expectation": null,
      "expectation_met": null,
      "relative_change": 0.011187268371815546,
      "meaningful_improvement": false,
      "metric": "v(n005).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": -0.0342456758,
        "max": 8.63440152,
        "mean": 4.386056878329287,
        "vpp": 8.6686471958,
        "final": -4.72069682e-05,
        "abs_peak": 8.63440152
      },
      "scenario_details": {
        "min": -0.0245919332,
        "max": 8.54707678,
        "mean": 5.115709029643018,
        "vpp": 8.5716687132,
        "final": 8.50562731,
        "abs_peak": 8.54707678
      }
    },
    {
      "quantity": "v(N006)",
      "base_value": 0.7431639747000001,
      "scenario_value": 0.7335272040999999,
      "delta": -0.009636770600000122,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 0.012967219790074307,
      "meaningful_improvement": false,
      "metric": "v(n006).vpp",
      "measurement": "tran_vpp",
      "base_details": {
        "min": -0.0342456757,
        "max": 0.708918299,
        "mean": 0.36462646308218305,
        "vpp": 0.7431639747000001,
        "final": -4.72069681e-05,
        "abs_peak": 0.708918299
      },
      "scenario_details": {
        "min": -0.0245919331,
        "max": 0.708935271,
        "mean": 0.42527575157176445,
        "vpp": 0.7335272040999999,
        "final": 0.708239156,
        "abs_peak": 0.708935271
      }
    },
    {
      "quantity": "@dled12_1[id]",
      "base_value": 0.00800489478,
      "scenario_value": 0.00801014912,
      "delta": 5.254340000000052e-06,
      "change": "changed",
      "expectation": "changed",
      "expectation_met": true,
      "relative_change": 0.0006563908888756251,
      "meaningful_improvement": false,
      "metric": "@dled12_1[id].abs_peak",
      "measurement": "tran_abs_peak",
      "base_details": {
        "min": -4.15850409e-14,
        "max": 0.00800489478,
        "mean": 0.004021560821778468,
        "vpp": 0.008004894780041585,
        "final": -6.54416737e-17,
        "abs_peak": 0.00800489478
      },
      "scenario_details": {
        "min": -3.07275513e-14,
        "max": 0.00801014912,
        "mean": 0.004690545857420072,
        "vpp": 0.008010149120030728,
        "final": 0.0077974433,
        "abs_peak": 0.00801014912
      }
    }
  ],
  "summary": {
    "requested_count": 4,
    "changed_count": 4,
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
  "created_or_updated_at": "2026-07-30T11:54:45",
  "temporal_expectation": {
    "target": "Dled12_1",
    "available": true,
    "met": true,
    "reason": "Criteri temporali verificati.",
    "base_profile": {
      "status": "measured",
      "state": "transient_pulse",
      "threshold_v": null,
      "profile_method": "device_current_hysteresis",
      "anode_node": "N006",
      "cathode_node": "0",
      "on_fraction": 0.5147793334970933,
      "duty_cycle": 0.5147793334970933,
      "display_duty_cycle": 0.6539849940879463,
      "regular_period": false,
      "period_s": null,
      "frequency_hz": null,
      "playback_duration_s": 1.0,
      "playback_slowdown": 10.0,
      "pulse_count": 63,
      "timeline_key_times": [
        0.0,
        0.00039397911999999993,
        0.00786258441,
        0.00863637495,
        0.0140113185,
        0.0150425487,
        0.020787700699999998,
        0.022105897499999996,
        0.028107436199999995,
        0.029726991699999997,
        0.0359371264,
        0.0378417307,
        0.0440808994,
        0.04630735169999999,
        0.05270325349999999,
        0.05524877549999999,
        0.06173068179999999,
        0.064653675,
        0.0713237682,
        0.0745927545,
        0.08124389109999999,
        0.0848377995,
        0.0915312895,
        0.095478682,
        0.10222524300000001,
        0.10657455399999999,
        0.113394327,
        0.118084902,
        0.124950249,
        0.13001786899999998,
        0.13687027999999998,
        0.14227582,
        0.14914504199999998,
        0.154900492,
        0.161794196,
        0.16791408599999996,
        0.17486712899999998,
        0.18139250299999998,
        0.18834418499999997,
        0.19519181900000002,
        0.20216399999999998,
        0.209319326,
        0.216268898,
        0.223795855,
        0.23078479999999998,
        0.23864561299999998,
        0.245640018,
        0.25381525299999996,
        0.26083270499999994,
        0.269300329,
        0.27629821299999996,
        0.285089796,
        0.292123888,
        0.301216463,
        0.30824783699999997,
        0.317594815,
        0.32460122299999994,
        0.33420199999999994,
        0.34122775199999994,
        0.351127225,
        0.35816925099999997,
        0.36831996699999997,
        0.375364621,
        0.385704293,
        0.392732312,
        0.40333157199999997,
        0.41036267199999993,
        0.421198954,
        0.42825728299999993,
        0.439262745,
        0.44630028099999997,
        0.457519279,
        0.46456008299999996,
        0.475953042,
        0.482997664,
        0.494583767,
        0.501650698,
        0.5133993299999999,
        0.520466287,
        0.532334568,
        0.5393913349999999,
        0.5514420489999999,
        0.558506055,
        0.570682862,
        0.577753344,
        0.590056743,
        0.597127984,
        0.609511396,
        0.616562577,
        0.6290603229999999,
        0.636113505,
        0.6487424589999999,
        0.655818862,
        0.668546618,
        0.675618991,
        0.6884051809999999,
        0.6954674019999999,
        0.708368307,
        0.715444878,
        0.728418162,
        0.7354851029999999,
        0.748486798,
        0.7555425709999999,
        0.7686528909999999,
        0.7757314179999999,
        0.7888723929999999,
        0.7959337019999999,
        0.8091339989999999,
        0.8161958599999999,
        0.829435847,
        0.836496223,
        0.849796292,
        0.856867572,
        0.870205123,
        0.8772674599999999,
        0.890669476,
        0.897735612,
        0.911135106,
        0.918198938,
        0.931638812,
        0.938707141,
        0.9522138889999999,
        0.959290049,
        0.9727997559999999,
        0.979849816,
        0.993402696,
        1.0
      ],
      "timeline_states": [
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
      "voltage_min": -0.0342456757,
      "voltage_max": 0.708918299,
      "threshold_current_a": 0.0001,
      "current_min_a": -4.15850409e-14,
      "current_max_a": 0.00800489478,
      "turn_on_current_a": 0.003201957911975049,
      "turn_off_current_a": 0.0012007342169646528
    },
    "scenario_profile": {
      "status"
```

> Scenario artifact truncated in this preview.


## Loaded artifacts

### graph

- Step: `01`
- Role: Graph JSON copied from Pipeline 1.0.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic01\01_graph.json`

```json
{
  "image_id": "ic01",
  "image_name": "ic01.jpg",
  "components": [
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
      "component_id": "capacitor4.1",
      "instance_id": "4.1",
      "class_name": "Capacitor",
      "terminals": [
        {
          "terminal_id": "capacitor4.1_t1",
          "name": "t1",
          "relative_position": "top"
        },
        {
          "terminal_id": "capacitor4.1_t2",
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
          "display_name": "555TIMER left_1 pin7",
          "pin_number": "7"
        },
        {
          "terminal_id": "integrated_circuit11.1_left_2",
          "name": "left_2",
          "relative_position": "left",
          "display_name": "555TIMER left_2 pin6",
          "pin_number": "6"
        },
        {
          "terminal_id": "integrated_circuit11.1_right_1",
          "name": "right_1",
          "relative_position": "right",
          "display_name": "555TIMER right_1 pin3",
          "pin_number": "3"
        },
        {
          "terminal_id": "integrated_circuit11.1_right_2",
          "name": "right_2",
          "relative_position": "right",
          "display_name": "555TIMER right_2 pin5",
          "pin_number": "5"
        },
        {
          "terminal_id": "integrated_circuit11.1_top_1",
          "name": "top_1",
          "relative_position": "top",
          "display_name": "555TIMER top_1 pin4",
          "pin_number": "4"
        },
        {
          "terminal_id": "integrated_circuit11.1_top_2",
          "name": "top_2",
          "relative_position": "top",
          "display_name": "555TIMER top_2 pin8",
          "pin_number": "8"
        },
        {
          "terminal_id": "integrated_circuit11.1_bottom_1",
          "name": "bottom_1",
          "relative_position": "bottom",
          "display_name": "555TIMER bottom_1 pin2",
          "pin_number": "2"
        },
        {
          "terminal_id": "integrated_circuit11.1_bottom_2",
          "name": "bottom_2",
          "relative_position": "bottom",
          "display_name": "555TIMER bottom_2 pin1",
          "pin_number": "1"
        }
      ],
      "display_name": "555TIMER",
      "ic_marking": "555TIMER"
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
      "component_id": "resistor22.3",
      "instance_id": "22.3",
      "class_name": "Resistor",
      "terminals": [
        {
          "terminal_id": "resistor22.3_t1",
          "name": "t1",
          "relative_position": "left"
        },
        {
          "terminal_id": "resistor22.3_t2",
          "name": "t2",
          "relative_position": "right"
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
      "component_id": "capacitor4.3",
      "instance_id": "4.3",
      "class_name": "Capacitor",
      "terminals": [
        {
          "terminal_id": "capacitor4.3_t1",
          "name": "t1",
          "relative_position": "top"
        },
        {
          "terminal_id": "capacitor4.3_t2",
          "name": "t2",
          "relative_position": "bottom"
        }
      ]
    }
  ],
  "terminal_metadata": {
    "integrated_circuit11.1_bottom_1": {
      "display_name": "555TIMER bottom_1 pin2",
      "pin_number": "2",
      "component_display_name": "555TIMER",
      "ic_marking": "555TIMER",
      "component_id": "integrated_circuit11.1",
      "class_name": "Integrated_Circuit"
    },
    "integrated_circuit11.1_bottom_2": {
      "display_name": "555TIMER bottom_2 pin1",
      "pin_number": "1",
      "component_display_name": "555TIMER",
      "ic_marking": "555TIMER",
      "component_id": "integrated_circuit11.1",
      "class_name": "Integrated_Circuit"
    },
    "integrated_circuit11.1_left_1": {
      "display_name": "555TIMER left_1 pin7",
      "pin_number": "7",
      "component_display_name": "555TIMER",
      "ic_marking": "555TIMER",
      "component_id": "integrated_circuit11.1",
      "class_name": "Integrated_Circuit"
    },
    "integrated_circuit11.1_left_2": {
      "display_name": "555TIMER left_2 pin6",
      "pin_number": "6",
      "component_display_name": "555TIMER",
      "ic_marking": "555TIMER",
      "component_id": "integrated_circuit11.1",
      "class_name": "Integrated_Circuit"
    },
    "integrated_circuit11.1_right_1": {
      "display_name": "555TIMER right_1 pin3",
      "pin_number": "3",
      "component_display_name": "555TIMER",
      "ic_marking": "555TIMER",
      "component_id": "integrated_circuit11.1",
      "class_name": "Integrated_Circuit"
    },
    "integrated_circuit11.1_right_2": {
      "display_name": "555TIMER right_2 pin5",
      "pin_number": "5",
      "component_display_name": "555TIMER",
      "ic_marking": "555TIMER",
      "component_id": "integrated_circuit11.1",
      "class_name": "Integrated_Circuit"
    },
    "integrated_circuit11.1_top_1": {
      "display_name": "555TIMER top_1 pin4",
      "pin_number": "4",
      "component_display_name": "555TIMER",
      "ic_marking": "555TIMER",
      "component_id": "integrated_circuit11.1",
      "class_name": "Integrated_Circuit"
    },
    "integrated_circuit11.1_top_2": {
      "display_name": "555TIMER top_2 pin8",
      "pin_number": "8",
      "component_display_name": "555TIMER",
      "ic_marking": "555TIMER",
      "component_id": "integrated_circuit11.1",
      "class_name": "Integrated_Circuit"
    }
  },
  "graph": {
    "capacitor4.1_t1": [
      "integrated_circuit11.1_bottom_1",
      "integrated_circuit11.1_left_2",
      "resistor22.1_t2"
    ],
    "capacitor4.1_t2": [
      "capacitor4.2_t2",
      "capacitor4.3_t2",
      "gnd9.1_t1",
      "integrated_circuit11.1_bottom_2",
      "led12.1_cathode"
    ],
    "capacitor4.2_t1": [
      "integrated_circuit11.1_right_2"
    ],
    "capacitor4.2_t2": [
      "capacitor4.1_t2",
      "capacitor4.3_t2",
      "gnd9.1_t1",
      "integrated_circuit11.1_bottom_2",
      "led12.1_cathode"
    ],
    "capacitor4.3_t1": [
      "integrated_circuit11.1_top_1",
      "integrated_circuit11.1_top_2",
      "resistor22.2_t1",
      "terminal26.1_t1"
    ],
    "capacitor4.3_t2": [
      "capacitor4.1_t2",
      "capacitor4.2_t2",
      "gnd9.1_t1",
      "integrated_circuit11.1_bottom_2",
      "led12.1_cathode"
    ],
    "gnd9.1_t1": [
      "capacitor4.1_t2",
      "capacitor4.2_t2",
      "capacitor4.3_t2",
      "integrated_circuit11.1_bottom_2",
      "led12.1_cathode"
    ],
    "integrated_circuit11.1_bottom_1": [
      "capacitor4.1_t1",
      "integrated_circuit11.1_left_2",
      "resistor22.1_t2"
    ],
    "integrated_circuit11.1_bottom_2": [
      "capacitor4.1_t2",
      "capacitor4.2_t2",
      "capacitor4.3_t2",
      "gnd9.1_t1",
      "led12.1_cathode"
    ],
    "integrated_circuit11.1_left_1": [
      "resistor22.1_t1",
      "resistor22.2_t2"
    ],
    "integrated_circuit11.1_left_2": [
      "capacitor4.1_t1",
      "integrated_circuit11.1_bottom_1",
      "resistor22.1_t2"
    ],
    "integrated_circuit11.1_right_1": [
      "resistor22.3_t1"
    ],
    "integrated_circuit11.1_right_2": [
      "capacitor4.2_t1"
    ],
    "integrated_circuit11.1_top_1": [
      "capacitor4.3_t1",
      "integrated_circuit11.1_top_2",
      "resistor22.2_t1",
      "terminal26.1_t1"
    ],
    "integrated_circuit11.1_top_2": [
      "capacitor4.3_t1",
      "integrated_circuit11.1_top_1",
      "resistor22.2_t1",
      "terminal26.1_t1"
    ],
    "led12.1_anode": [
      "resistor22.3_t2"
    ],
    "led12.1_cathode": [
      "capacitor4.1_t2",
      "capacitor4.2_t2",
      "capacitor4.3_t2",
      "gnd9.1_t1",
      "integrated_circuit11.1_bottom_2"
    ],
    "resistor22.1_t1": [
      "integrated_circuit11.1_left_1",
      "resistor22.2_t2"
    ],
    "resistor22.1_t2": [
      "capacitor4.1_t1",
      "integrated_circuit11.1_bottom_1",
      "integrated_circuit11.1_left_2"
    ],
    "resistor22.2_t1": [
      "capacitor4.3_t1",
      "integrated_circuit11.1_top_1",
      "integrated_circuit11.1_top_2",
      "terminal26.1_t1"
    ],
    "resistor22.2_t2": [
      "integrated_circuit11.1_left_1",
      "resistor22.1_t1"
    ],
    "resistor22.3_t1": [
      "integrated_circuit11.1_right_1"
    ],
    "resistor22.3_t2": [
      "led12.1_anode"
    ],
    "terminal26.1_t1": [
      "capacitor4.3_t1",
      "integrated_circuit11.1_top_1",
      "integrated_circuit11.1_top_2",
      "resistor22.2_t1"
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
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic01\03_node_map.json`

```json
{
  "circuit_id": "ic01",
  "source_format": "pipeline2.0_node_map",
  "nodes": [
    {
      "node_id": "0",
      "kind": "ground",
      "terminals": [
        "capacitor4.1_t2",
        "capacitor4.2_t2",
        "capacitor4.3_t2",
        "gnd9.1_t1",
        "integrated_circuit11.1_bottom_2",
        "led12.1_cathode"
      ],
      "terminal_count": 6,
      "source_groups": [
        [
          "capacitor4.1_t2",
          "capacitor4.2_t2",
          "capacitor4.3_t2",
          "gnd9.1_t1",
          "integrated_circuit11.1_bottom_2",
          "led12.1_cathode"
        ]
      ]
    },
    {
      "node_id": "N001",
      "kind": "normal",
      "terminals": [
        "capacitor4.1_t1",
        "integrated_circuit11.1_bottom_1",
        "integrated_circuit11.1_left_2",
        "resistor22.1_t2"
      ],
      "terminal_count": 4
    },
    {
      "node_id": "N002",
      "kind": "normal",
      "terminals": [
        "capacitor4.2_t1",
        "integrated_circuit11.1_right_2"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N003",
      "kind": "normal",
      "terminals": [
        "capacitor4.3_t1",
        "integrated_circuit11.1_top_1",
        "integrated_circuit11.1_top_2",
        "resistor22.2_t1",
        "terminal26.1_t1"
      ],
      "terminal_count": 5
    },
    {
      "node_id": "N004",
      "kind": "normal",
      "terminals": [
        "integrated_circuit11.1_left_1",
        "resistor22.1_t1",
        "resistor22.2_t2"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N005",
      "kind": "normal",
      "terminals": [
        "integrated_circuit11.1_right_1",
        "resistor22.3_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N006",
      "kind": "normal",
      "terminals": [
        "led12.1_anode",
        "resistor22.3_t2"
      ],
      "terminal_count": 2
    }
  ],
  "terminal_to_node": {
    "capacitor4.1_t1": "N001",
    "capacitor4.1_t2": "0",
    "capacitor4.2_t1": "N002",
    "capacitor4.2_t2": "0",
    "capacitor4.3_t1": "N003",
    "capacitor4.3_t2": "0",
    "gnd9.1_t1": "0",
    "integrated_circuit11.1_bottom_1": "N001",
    "integrated_circuit11.1_bottom_2": "0",
    "integrated_circuit11.1_left_1": "N004",
    "integrated_circuit11.1_left_2": "N001",
    "integrated_circuit11.1_right_1": "N005",
    "integrated_circuit11.1_right_2": "N002",
    "integrated_circuit11.1_top_1": "N003",
    "integrated_circuit11.1_top_2": "N003",
    "led12.1_anode": "N006",
    "led12.1_cathode": "0",
    "resistor22.1_t1": "N004",
    "resistor22.1_t2": "N001",
    "resistor22.2_t1": "N003",
    "resistor22.2_t2": "N004",
    "resistor22.3_t1": "N005",
    "resistor22.3_t2": "N006",
    "terminal26.1_t1": "N003"
  },
  "component_terminal_nodes": {
    "capacitor4.1": {
      "t1": "N001",
      "t2": "0"
    },
    "capacitor4.2": {
      "t1": "N002",
      "t2": "0"
    },
    "capacitor4.3": {
      "t1": "N003",
      "t2": "0"
    },
    "gnd9.1": {
      "t1": "0"
    },
    "integrated_circuit11.1": {
      "left_1": "N004",
      "left_2": "N001",
      "right_1": "N005",
      "right_2": "N002",
      "top_1": "N003",
      "top_2": "N003",
      "bottom_1": "N001",
      "bottom_2": "0"
    },
    "led12.1": {
      "anode": "N006",
      "cathode": "0"
    },
    "resistor22.1": {
      "t1": "N004",
      "t2": "N001"
    },
    "resistor22.2": {
      "t1": "N003",
      "t2": "N004"
    },
    "resistor22.3": {
      "t1": "N005",
      "t2": "N006"
    },
    "terminal26.1": {
      "t1": "N003"
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
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic01\04_values_bound.json`

```json
{
  "circuit_id": "ic01",
  "source_format": "pipeline2.0_values_bound",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\data\\batchPipeline2.0\\batchICChatAgentEvaluation\\values\\ic01_values.yaml",
  "supplies": {
    "VCC_9": {
      "terminal": "terminal26.1_t1",
      "type": "dc",
      "value": 9,
      "unit": "V",
      "reference": 0,
      "source": "manual_from_image_label",
      "label_text": "+9 V DC",
      "viewer_override": {
        "visual_class": "voltage_source",
        "label": "+9 V",
        "display_value": "9 V DC"
      },
      "node": "N003"
    }
  },
  "components": {
    "capacitor4.1": {
      "class_name": "Capacitor",
      "terminal_nodes": {
        "t1": "N001",
        "t2": "0"
      },
      "value_data": {
        "value": 1,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C1 1 uF",
        "viewer_override": {
          "label": "C1",
          "display_value": "1 uF"
        }
      },
      "status": "bound"
    },
    "capacitor4.2": {
      "class_name": "Capacitor",
      "terminal_nodes": {
        "t1": "N002",
        "t2": "0"
      },
      "value_data": {
        "value": 1,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C2 1 uF",
        "viewer_override": {
          "label": "C2",
          "display_value": "1 uF"
        }
      },
      "status": "bound"
    },
    "capacitor4.3": {
      "class_name": "Capacitor",
      "terminal_nodes": {
        "t1": "N003",
        "t2": "0"
      },
      "value_data": {
        "value": 1,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C3 1 uF",
        "viewer_override": {
          "label": "C3",
          "display_value": "1 uF"
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
    "integrated_circuit11.1": {
      "class_name": "Integrated_Circuit",
      "terminal_nodes": {
        "left_1": "N004",
        "left_2": "N001",
        "right_1": "N005",
        "right_2": "N002",
        "top_1": "N003",
        "top_2": "N003",
        "bottom_1": "N001",
        "bottom_2": "0"
      },
      "value_data": {
        "model": "TLC555_6",
        "source": "ti_official_slfj002e_pspice_model",
        "label_text": "IC1 555 Timer; modello ufficiale TI TLC555_6 Rev. E",
        "viewer_override": {
          "label": "IC1",
          "display_value": "TLC555",
          "tooltip": "IC1 TLC555; modello ufficiale TI PSpice Rev. E SLFJ002E"
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
            "CONT": "integrated_circuit11.1_right_2",
            "TRIG": "integrated_circuit11.1_bottom_1",
            "RESET": "integrated_circuit11.1_top_1",
            "OUT": "integrated_circuit11.1_right_1",
            "DISC": "integrated_circuit11.1_left_1",
            "VCC": "integrated_circuit11.1_top_2",
            "GND": "integrated_circuit11.1_bottom_2"
          },
          "resolved_node_refs": {
            "THRES": "N001",
            "CONT": "N002",
            "TRIG": "N001",
            "RESET": "N003",
            "OUT": "N005",
            "DISC": "N004",
            "VCC": "N003",
            "GND": "0"
          }
        }
      },
      "status": "unsupported_for_now"
    },
    "led12.1": {
      "class_name": "LED",
      "terminal_nodes": {
        "anode": "N006",
        "cathode": "0"
      },
      "value_data": {
        "model": "LED_RED",
        "source": "manual_assumption_standard_red_led",
        "label_text": "LED rosso standard; part number non specificato",
        "viewer_override": {
          "label": "LED",
          "display_value": "red",
          "tooltip": "LED rosso standard assunto; part number non indicato nello schema"
        }
      },
      "status": "bound"
    },
    "resistor22.1": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N004",
        "t2": "N001"
      },
      "value_data": {
        "value": 1,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R2 1 kohm",
        "viewer_override": {
          "label": "R2",
          "display_value": "1 kohm"
        }
      },
      "status": "bound"
    },
    "resistor22.2": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N003",
        "t2": "N004"
      },
      "value_data": {
        "value": 1,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R1 1 kohm",
        "viewer_override": {
          "label": "R1",
          "display_value": "1 kohm"
        }
      },
      "status": "bound"
    },
    "resistor22.3": {
      "class_name": "Resistor",
      "terminal_nodes": {
        "t1": "N005",
        "t2": "N006"
      },
      "value_data": {
        "value": 1,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R3 1 kohm",
        "viewer_override": {
          "label": "R3",
          "display_value": "1 kohm"
        }
      },
      "status": "bound"
    },
    "terminal26.1": {
      "class_name": "Terminal",
      "terminal_nodes": {
        "t1": "N003"
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
      "label": "TIMER_TRIGGER",
      "source": "manual_from_validated_graph_pin2",
      "node": "N001"
    },
    "integrated_circuit11.1_left_1": {
      "label": "TIMER_DISCHARGE",
      "source": "manual_from_validated_graph_pin7",
      "node": "N004"
    },
    "integrated_circuit11.1_left_2": {
      "label": "TIMER_THRESHOLD",
      "source": "manual_from_validated_graph_pin6",
      "node": "N001"
    },
    "integrated_circuit11.1_right_1": {
      "label": "TIMER_OUT",
      "source": "manual_from_validated_graph_pin3",
      "node": "N005"
    },
    "integrated_circuit11.1_right_2": {
      "label": "TIMER_CONTROL",
      "source": "manual_from_validated_graph_pin5",
      "node": "N002"
    },
    "terminal26.1_t1": {
      "label": "VCC_9",
      "source": "manual_from_image_label",
      "label_text": "+9 V",
      "node": "N003"
    }
  },
  "spice_topology_overlay": [],
  "simulation": {
    "analyses": [
      "tran"
    ],
    "tran": {
      "step": "5us",
      "stop": "100ms"
    }
  },
  "missing": [],
  "stats": {
    "components_total": 10,
    "bound_components": 7,
    "missing_components": 0,
    "not_required_components": 2,
    "unsupported_components": 1,
    "supplies_count": 1,
    "manual_nodes_count": 7
  }
}
```

### component_rules

- Step: `06`
- Role: SPICE conversion rules for each component.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic01\06_component_rules.json`

```json
{
  "circuit_id": "ic01",
  "source_format": "pipeline2.0_component_rules",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\data\\batchPipeline2.0\\batchICChatAgentEvaluation\\values\\ic01_values.yaml",
  "spice_classes_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_spice_classes.yaml",
  "supplies": {
    "VCC_9": {
      "status": "spice_ready",
      "spice_prefix": "V",
      "emit_as": "independent_voltage_source",
      "nodes": [
        "N003",
        "0"
      ],
      "parameters": {
        "terminal": "terminal26.1_t1",
        "type": "dc",
        "value": 9,
        "unit": "V",
        "reference": 0,
        "source": "manual_from_image_label",
        "label_text": "+9 V DC",
        "viewer_override": {
          "visual_class": "voltage_source",
          "label": "+9 V",
          "display_value": "9 V DC"
        },
        "node": "N003"
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
        "0"
      ],
      "parameters": {
        "value": 1,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C1 1 uF",
        "viewer_override": {
          "label": "C1",
          "display_value": "1 uF"
        }
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
        "N002",
        "0"
      ],
      "parameters": {
        "value": 1,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C2 1 uF",
        "viewer_override": {
          "label": "C2",
          "display_value": "1 uF"
        }
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
        "N003",
        "0"
      ],
      "parameters": {
        "value": 1,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C3 1 uF",
        "viewer_override": {
          "label": "C3",
          "display_value": "1 uF"
        }
      }
    },
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
        "N001",
        "N002",
        "N001",
        "N003",
        "N005",
        "N004",
        "N003",
        "0"
      ],
      "parameters": {
        "model": "TLC555_6",
        "source": "ti_official_slfj002e_pspice_model",
        "label_text": "IC1 555 Timer; modello ufficiale TI TLC555_6 Rev. E",
        "viewer_override": {
          "label": "IC1",
          "display_value": "TLC555",
          "tooltip": "IC1 TLC555; modello ufficiale TI PSpice Rev. E SLFJ002E"
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
            "CONT": "integrated_circuit11.1_right_2",
            "TRIG": "integrated_circuit11.1_bottom_1",
            "RESET": "integrated_circuit11.1_top_1",
            "OUT": "integrated_circuit11.1_right_1",
            "DISC": "integrated_circuit11.1_left_1",
            "VCC": "integrated_circuit11.1_top_2",
            "GND": "integrated_circuit11.1_bottom_2"
          },
          "resolved_node_refs": {
            "THRES": "N001",
            "CONT": "N002",
            "TRIG": "N001",
            "RESET": "N003",
            "OUT": "N005",
            "DISC": "N004",
            "VCC": "N003",
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
        "N006",
        "0"
      ],
      "parameters": {
        "model": "LED_RED",
        "source": "manual_assumption_standard_red_led",
        "label_text": "LED rosso standard; part number non specificato",
        "viewer_override": {
          "label": "LED",
          "display_value": "red",
          "tooltip": "LED rosso standard assunto; part number non indicato nello schema"
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
        "N001"
      ],
      "parameters": {
        "value": 1,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R2 1 kohm",
        "viewer_override": {
          "label": "R2",
          "display_value": "1 kohm"
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
        "N003",
        "N004"
      ],
      "parameters": {
        "value": 1,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R1 1 kohm",
        "viewer_override": {
          "label": "R1",
          "display_value": "1 kohm"
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
        "N005",
        "N006"
      ],
      "parameters": {
        "value": 1,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R3 1 kohm",
        "viewer_override": {
          "label": "R3",
          "display_value": "1 kohm"
        }
      }
    },
    "terminal26.1": {
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
      "step": "5us",
      "stop": "100ms"
    }
  },
  "stats": {
    "components_total": 10,
    "spice_ready_components": 8,
    "not_emitted_components": 2,
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
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic01\07_netlist.cir`

```spice
* pipeline2.0 netlist
* circuit: ic01

VVCC_9 N003 0 DC 9
Ccapacitor4_1 N001 0 1u
Ccapacitor4_2 N002 0 1u
Ccapacitor4_3 N003 0 1u
Xintegrated_circuit11_1 N001 N002 N001 N003 N005 N004 N003 0 TLC555_6
Dled12_1 N006 0 LED_RED
Rresistor22_1 N004 N001 1k
Rresistor22_2 N003 N004 1k
Rresistor22_3 N005 N006 1k

.model LED_RED D
.include "07_external_models.lib"

.save all
.tran 5us 100ms

.control
set wr_singlescale
set wr_vecnames
save all @dled12_1[id]
run
wrdata 08_tran.csv time v(N001) v(N002) v(N003) v(N004) v(N005) v(N006) @dled12_1[id]
.endc
.end

```

### spice_emit_report

- Step: `07`
- Role: Report of emitted, skipped and warning components.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic01\07_spice_emit_report.json`

```json
{
  "circuit_id": "ic01",
  "source_format": "pipeline2.0_spice_emit_report",
  "emitted_elements": 9,
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
      "N006"
    ],
    "device_currents": [
      "@dled12_1[id]"
    ]
  },
  "models": [
    "LED_RED",
    "TLC555_6"
  ],
  "warnings": [],
  "external_model_sources": [
    {
      "model": "TLC555_6",
      "kind": "file",
      "file": "spice_models/ti/tlc555/slfj002e/TLC555_6.LIB",
      "sha256": "7C091782CC4931DDA4FEBF25605083F47161C5E1592C076689B04B70DD749034"
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
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic01\08_spice_run.json`

```json
{
  "source_format": "pipeline2.0_spice_run",
  "status": "success",
  "netlist_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\pipeline2.0\\ic01\\07_netlist.cir",
  "command": [
    "C:\\Users\\m.profilo\\Spice64\\bin\\ngspice_con.EXE",
    "-D",
    "ngbehavior=ps",
    "-b",
    "07_netlist.cir"
  ],
  "exit_code": 0,
  "stdout_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\pipeline2.0\\ic01\\08_ngspice_stdout.txt",
  "stderr_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\pipeline2.0\\ic01\\08_ngspice_stderr.txt",
  "tran_raw_csv_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\pipeline2.0\\ic01\\08_tran_raw.csv",
  "tran_csv_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\pipeline2.0\\ic01\\08_tran.csv",
  "tran_plot_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\pipeline2.0\\ic01\\08_tran_plot.png",
  "tran_plot_png_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\pipeline2.0\\ic01\\08_tran_plot.png",
  "tran_plot_svg_path": null,
  "message": "ngspice completed successfully."
}
```

### ngspice_stdout

- Step: `08`
- Role: Raw ngspice stdout log.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic01\08_ngspice_stdout.txt`

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
n003                                         9
n001                                   0.37893
n002                                 0.0581163
xintegrated_circuit11_1.resi                 9
xintegrated_circuit11_1.trgi          0.378927
xintegrated_circuit11_1.thri          0.378927
xintegrated_circuit11_1.conti         0.326105
xintegrated_circuit11_1.qff                  1
xintegrated_circuit11_1.gout       5.31855e-07
xintegrated_circuit11_1.trgo        0.00247082
xintegrated_circuit11_1.xmn3.10            0.14
xintegrated_circuit11_1.23            0.186463
xintegrated_circuit11_1.thrs        -0.0039892
xintegrated_circuit11_1.xmn5.10            0.14
xintegrated_circuit11_1.25            0.150433
xintegrated_circuit11_1.reso        0.00031436
xintegrated_circuit11_1.15           0.0377662
xintegrated_circuit11_1.xmp9.10            8.15
xintegrated_circuit11_1.xmp6.10            8.15
xintegrated_circuit11_1.trgs          0.754236
xintegrated_circuit11_1.xmp5.10            8.15
xintegrated_circuit11_1.thro           8.46572
xintegrated_circuit11_1.xmp1.10            8.86
xintegrated_circuit11_1.29                8.86
xintegrated_circuit11_1.xib.gb_int1     3.77573e-08
xintegrated_circuit11_1.xrsff.xu1.out_vmeas_0    -1.13852e-15
xintegrated_circuit11_1.xrsff.xu1.eout_int1    -1.13852e-15
xintegrated_circuit11_1.30        -1.13852e-15
xintegrated_circuit11_1.xrsff.xu2.out_vmeas_2               1
xintegrated_circuit11_1.xrsff.xu2.eout_int1               1
xintegrated_circuit11_1.xrsff.xu2.1        0.122699
xintegrated_circuit11_1.xrsff.xu2.e1_int1        0.122699
n004                                   4.68946
n005                                   8.52024
xintegrated_circuit11_1.trgc         0.0870928
xintegrated_circuit11_1.32          -0.0249399
xintegrated_circuit11_1.33             0.18685
xintegrated_circuit11_1.34             4.66305
n006                                  0.708287
b.xintegrated_circuit11_1.xrsff.xu2.be1#branch               0
b.xintegrated_circuit11_1.xrsff.xu2.beout#branch               0
v.xintegrated_circuit11_1.xrsff.xu2.v_eout#branch    -2.00594e-12
b.xintegrated_circuit11_1.xrsff.xu1.beout#branch               0
v.xintegrated_circuit11_1.xrsff.xu1.v_eout#branch    -1.13852e-16
b.xintegrated_circuit11_1.xib.bgb#branch               0
v.xintegrated_circuit11_1.xmp1.v1#branch     1.78919e-11
v.xintegrated_circuit11_1.xmn5.v1#branch     4.41926e-09
v.xintegrated_circuit11_1.xmn3.v1#branch      7.8362e-07
e.xintegrated_circuit11_1.xrsff.xu2.e1#branch               0
e.xintegrated_circuit11_1.xrsff.xu2.eout#branch    -2.00594e-12
e.xintegrated_circuit11_1.xrsff.xu1.eout#branch    -1.13852e-16
v.xintegrated_circuit11_1.xmp5.v1#branch     8.39576e-12
v.xintegrated_circuit11_1.xmp6.v1#branch     8.99957e-12
v.xintegrated_circuit11_1.xmp9.v1#branch     9.14969e-12
vvcc_9#branch                       -0.0171681

 Reference value :  2.30777e-02
 Reference value :  6.71178e-02

No. of Data Rows : 24426
Note: Simulation executed from .control section 

```

### ngspice_stderr

- Step: `08`
- Role: Raw ngspice stderr log.
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic01\08_ngspice_stderr.txt`

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
- Path: `outputs\demo_workspaces\ic_chat_agent_evaluation\web\chat\ic01\08_tran.csv`

```csv
time,v(N001),v(N002),v(N003),v(N004),v(N005),v(N006),@dled12_1[id]
0.0,0.378930123,0.0581162788,9.0,4.68946142,8.52024254,0.708287249,0.00781195529
5e-08,0.379145644,0.0581347861,9.0,4.68956916,8.52024994,0.708287274,0.00781196266
1e-07,0.379361159,0.0581532934,9.0,4.68967691,8.52024994,0.708287274,0.00781196266
2e-07,0.379792179,0.0581903078,9.0,4.68989242,8.52024994,0.708287274,0.00781196266
4e-07,0.380654154,0.0582643357,9.0,4.69032341,8.52024994,0.708287274,0.00781196266
8e-07,0.382377846,0.0584123878,9.0,4.69118526,8.52024994,0.708287274,0.00781196266
1.6e-06,0.385824195,0.0587084772,9.0,4.69290844,8.52024994,0.708287274,0.00781196266
3.2e-06,0.392712759,0.0593005968,9.0,4.69635272,8.52024994,0.708287274,0.00781196266
6.4e-06,0.406473369,0.0604845996,9.0,4.70323303,8.52024994,0.708287274,0.00781196266
1.14e-05,0.427930299,0.062333973,9.0,4.71396151,8.52024994,0.708287274,0.00781196266
1.64e-05,0.449333654,0.0641825774,9.0,4.7246632,8.52024994,0.708287274,0.00781196266
2.14e-05,0.470683567,0.0660304131,9.0,4.73533817,8.52024994,0.708287274,0.00781196266
2.64e-05,0.491980171,0.0678774807,9.0,4.74598648,8.52024994,0.708287274,0.00781196266
3.14e-05,0.513223598,0.0697237807,9.0,4.75660821,8.52024994,0.708287274,0.00781196266
3.64e-05,0.534413981,0.0715693134,9.0,4.76720341,8.52024994,0.708287274,0.00781196266
3.86242458e-05,0.543823489,0.0723900507,9.0,4.77190817,8.52024994,0.708287274,0.00781196266
3.9397912e-05,0.545274803,0.0726754946,9.0,0.0689842686,0.00420807525,0.00420807524,5.97484479e-15
3.96483763e-05,0.545155037,0.0727678995,9.0,0.0650854623,-0.00415380646,-0.00415380645,-5.63744722e-15
3.97293962e-05,0.545116295,0.07279779,9.0,0.0688317585,0.00403298187,0.00403298186,5.7203649e-15
3.973497e-05,0.545113633,0.0727998464,9.0,0.0663874395,-0.00259695676,-0.00259695675,-3.55224284e-15
3.97377872e-05,0.545112285,0.0728008857,9.0,0.0667483725,0.001323377,0.001323377,1.8483418e-15
3.97381392e-05,0.545112117,0.0728010156,9.0,0.067266203,0.000113424766,0.000113424766,1.57373807e-16
3.97384225e-05,0.545111982,0.0728011201,9.0,0.0671332664,0.000123322888,0.000123322887,1.71116335e-16
3.97387772e-05,0.545111812,0.072801251,9.0,0.0671028575,9.06523845e-05,9.06523843e-05,1.25762271e-16
3.97391986e-05,0.545111611,0.0728014064,9.0,0.0670668147,5.56323902e-05,5.56323901e-05,7.71643603e-17
3.97397294e-05,0.545111357,0.0728016023,9.0,0.0670437855,3.13472916e-05,3.13472915e-05,4.34742568e-17
3.97403766e-05,0.545111047,0.072801841,9.0,0.0670270835,1.50175359e-05,1.50175359e-05,2.08253629e-17
3.97412247e-05,0.545110642,0.0728021539,9.0,0.0670183344,5.62210439e-06,5.62210437e-06,7.79598161e-18
3.9742185e-05,0.545110183,0.0728025082,9.0,0.0670141371,1.82008686e-06,1.82008685e-06,2.52380104e-18
3.97435689e-05,0.545109521,0.0728030187,9.0,0.0670129765,2.19377325e-07,2.19377324e-07,3.04194242e-19
3.97456611e-05,0.545108521,0.0728037906,9.0,0.0670123818,3.42912479e-08,3.42912478e-08,4.7549079e-20
3.97498456e-05,0.54510652,0.0728053344,9.0,0.0670126861,-4.66248486e-08,-4.66248485e-08,-6.46511218e-20
3.97582146e-05,0.545102519,0.0728084219,9.0,0.0670123586,5.04678467e-08,5.04678466e-08,6.99799509e-20
3.97730007e-05,0.54509545,0.0728138769,9.0,0.0670126014,-5.18306994e-08,-5.18306993e-08,-7.18696761e-20
3.97887916e-05,0.545087901,0.0728197026,9.0,0.0670122596,5.34131027e-08,5.34131026e-08,7.40639161e-20
3.98037796e-05,0.545080736,0.072825232,9.0,0.0670124941,-5.43919366e-08,-5.43919365e-08,-7.54211473e-20
3.98178492e-05,0.545074009,0.0728304227,9.0,0.0670121651,5.58211028e-08,5.58211026e-08,7.74029089e-20
3.98321379e-05,0.545067179,0.0728356941,9.0,0.0670123953,-5.6600363e-08,-5.66003628e-08,-7.84834027e-20
3.98464355e-05,0.545060344,0.0728409689,9.0,0.0670120717,5.7800016e-08,5.78000158e-08,8.01469193e-20
3.98609241e-05,0.545053417,0.0728463141,9.0,0.0670122955,-5.83981475e-08,-5.83981474e-08,-8.09762525e-20
3.98752725e-05,0.545046558,0.0728516075,9.0,0.0670119772,5.94574958e-08,5.94574957e-08,8.24452222e-20
3.98896987e-05,0.545039662,0.0728569297,9.0,0.0670121961,-5.99467915e-08,-5.99467913e-08,-8.31236381e-20
3.99040405e-05,0.545032807,0.0728622207,9.0,0.0670118826,6.0911753e-08,6.09117529e-08,8.44617317e-20
3.99184567e-05,0.545025915,0.0728675392,9.0,0.0670120969,-6.13217702e-08,-6.132177e-08,-8.50302155e-20
3.99328157e-05,0.545019052,0.0728728365,9.0,0.0670117878,6.22171888e-08,6.22171887e-08,8.62718815e-20
3.99472241e-05,0.545012164,0.0728781521,9.0,0.0670119979,-6.25680856e-08,-6.25680854e-08,-8.67583853e-20
3.99626602e-05,0.545004786,0.0728838468,9.0,0.0670116892,6.33707885e-08,6.33707884e-08,8.78714918e-20
3.99807844e-05,0.544996123,0.0728905332,9.0,0.0670118831,-6.35626693e-08,-6.35626691e-08,-8.8137498e-20
4.00014388e-05,0.544986251,0.072898153,9.0,0.0670115599,6.42033498e-08,6.42033497e-08,8.90259421e-20
4.0025964e-05,0.544974528,0.0729072008,9.0,0.0670117297,-6.42616385e-08,-6.42616384e-08,-8.9106705e-20
4.00548675e-05,0.544960714,0.0729178638,9.0,0.0670113809,6.47816979e-08,6.47816978e-08,8.98278941e-20
4.00909588e-05,0.544943464,0.0729311785,9.0,0.06701151,-6.47316825e-08,-6.47316824e-08,-8.97584789e-20
4.01368225e-05,0.544921545,0.0729480984,9.0,0.0670111054,6.51501381e-08,6.51501379e-08,9.03387824e-20
4.01998474e-05,0.544891426,0.0729713491,9.0,0.0670111427,-6.50091006e-08,-6.50091004e-08,-9.01431532e-20
4.02921442e-05,0.544847321,0.0730053985,9.0,0.0670105825,6.53452616e-08,6.53452614e-08,9.06093456e-20
4.04496915e-05,0.544772045,0.073063519,9.0,0.0670103009,-6.51340054e-08,-6.51340052e-08,-9.0316349e-20
4.07647862e-05,0.544621529,0.0731797577,9.0,0.067008991,6.54142482e-08,6.5414248e-08,9.07050041e-20
4.13949755e-05,0.544320638,0.073412226,9.0,0.0670071188,-6.51684349e-08,-6.51684347e-08,-9.03640898e-20
4.26553541e-05,0.543719419,0.0738771259,9.0,0.067002632,6.54314471e-08,6.54314469e-08,9.07288526e-20
4.51761114e-05,0.542519237,0.0748067799,9.0,0.0669944206,-6.51770304e-08,-6.51770302e-08,-9.03760085e-20
5.01761114e-05,0.540147506,0.0766502012,9.0,0.0669774532,6.54357557e-08,6.54357556e-08,9.0734827e-20
5.51761114e-05,0.537787521,0.0784928571,9.0,0.0669610663,-6.51799183e-08,-6.51799181e-08,-9.03800129e-20
6.01761114e-05,0.535439223,0.0803347481,9.0,0.0669442642,6.54386433e-08,6.54386432e-08,9.07388311e-20
6.51761114e-05,0.533102555,0.0821758745,9.0,0.0669280417,-6.51828056e-08,-6.51828054e-08,-9.03840165e-20
7.01761114e-05,0.530777459,0.084016237,9.0,0.0669114032,6.54415304e-08,6.54415303e-08,9.07428344e-20
7.51761114e-05,0.528463878,0.0858558358,9.0,0.0668953435,-6.51856924e-08,-6.51856923e-08,-9.03880194e-20
8.01761114e-05,0.526161755,0.0876946716,9.0,0.0668788671,6.5444417e-08,6.54444168e-08,9.07468369e-20
8.51761114e-05,0.523871033,0.0895327448,9.0,0.0668629685,-6.51885787e-08,-6.51885785e-08,-9.03920216e-20
9.01761114e-05,0.521591656,0.0913700558,9.0,0.0668466525,6.5447303e-08,6.54473028e-08,9.07508387e-20
9.51761114e-05,0.519323567,0.0932066051,9.0,0.0668309136,-6.51914644e-08,-6.51914643e-08,-9.03960231e-20
0.000100176111,0.517066711,0.0950423932,9.0,0.0668147563,6.54501884e-08,6.54501883e-08,9.07548398e-20
0.000105176111,0.514821032,0.0968774205,9.0,0.0667991754,-6.51943496e-08,-6.51943495e-08,-9.04000237e-20
0.000110176111,0.512586474,0.0987116876,9.0,0.0667831755,6.54530734e-08,6.54530732e-08,9.07588401e-20
0.000115176111,0.510362983,0.100545195,9.0,0.066767751,-6.51972343e-08,-6.51972341e-08,-9.04040237e-20
0.000120176111,0.508150504,0.102377943,9.0,0.0667519067,6.54559578e-08,6.54559576e-08,9.07628397e-20
0.000125176111,0.505948981,0.104209932,9.0,0.0667366372,-6.52001184e-08,-6.52001183e-08,-9.04080229e-20
0.000130176111,0.503758362,0.106041162,9.0,0.066720947,6.54588416e-08,6.54588415e-08,9.07668385e-20
0.000135176111,0.501578591,0.107871635,9.0,0.0667058309,-6.5203002e-08,-6.52030019e-08,-9.04120213e-20
0.000140176111,0.499409616,0.109701349,9.0,0.0666902934,6.5461725e-08,6.54617248e-08,9.07708366e-20
0.000145176111,0.497251382,0.111530307,9.0,0.0666753291,-6.52058851e-08,-6.52058849e-08,-9.04160191e-20
0.000150176111,0.495103837,0.113358509,9.0,0.0666599427,6.54646078e-08,6.54646076e-08,9.0774834e-20
0.000155176111,0.492966928,0.115185954,9.0,0.0666451287,-6.52087676e-08,-6.52087675e-08,-9.0420016e-20
0.000160176111,0.490840601,0.117012644,9.0,0.066629892,6.546749e-08,6.54674899e-08,9.07788306e-20
0.000165176111,0.488724805,0.118838578,9.0,0.0666152269,-6.52116496e-08,-6.52116494e-08,-9.04240123e-20
0.000170176111,0.486619488,0.120663757,9.0,0.0666001383,6.54703717e-08,6.54703716e-08,9.07828264e-20
0.000175176111,0.484524596,0.122488183,9.0,0.0665856206,-6.52145311e-08,-6.52145309e-08,-9.04280078e-20
0.000180176111,0.48244008,0.124311854,9.0,0.0665706787,6.54732529e-08,6.54732528e-08,9.07868216e-20
0.000185176111,0.480365887,0.126134772,9.0,0.066556307,-6.5217412e-08,-6.52174118e-08,-9.04320025e-20
0.000190176111,0.478301966,0.127956937,9.0,0.0665415103,6.54761336e-08,6.54761334e-08,9.0790816e-20
0.000195176111,0.476248267,0.12977835,9.0,0.066527283,-6.52202924e-08,-6.52202922e-08,-9.04359965e-20
0.000200176111,0.474204739,0.131599011,9.0,0.0665126302,6.54790137e-08,6.54790135e-08,9.07948096e-20
0.000205176111,0.472171331,0.13341892,9.0,0.066498546,-6.52231722e-08,-6.52231721e-08,-9.04399898e-20
0.000210176111,0.470147994,0.135238078,9.0,0.0664840355,6.54818933e-08,6.54818931e-08,9.07988025e-20
0.000215176111,0.468134677,0.137056486,9.0,0.066470093,-6.52260515e-08,-6.52260514e-08,-9.04439823e-20
0.000220176111,0.466131331,0.138874143,9.0,0.0664557234,6.54847723e-08,6.54847722e-08,9.08027947e-20
0.000225176111,0.464137906,0.14069105,9.0,0.0664419212,-6.52289303e-08,-6.52289302e-08,-9.04479741e-20
0.000230176111,0.462154354,0.142507209,9.0,0.0664276912,6.54876509e-08,6.54876507e-08,9.08067861e-20
0.000235176111,0.460180625,0.144322618,9.0,0.0664140278,-6.52318086e-08,-6.52318084e-08,-9.04519652e-20
0.000240176111,0.458216671,0.146137279,9.0,0.0663999361,6.54905288e-08,6.54905287e-08,9.08107768e-20
0.000245176111,0.456262444,0.147951193,9.0,0.0663864101,-6.52346863e-08,-6.52346862e-08,-9.04559555e-20
0.000250176111,0.454317895,0.149764359,9.0,0.0663724552,6.54934063e-08,6.54934061e-08,9.08147667e-20
0.000255176111,0.452382976,0.151576777,9.0,0.0663590654,-6.52375635e-08,-6.52375633e-08,-9.04599451e-20
0.000260176111,0.450457639,0.15338845,9.0,0.066345246,6.54962832e-08,6.54962831e-08,9.0818756e-20
0.000265176111,0.448541838,0.155199376,9.0,0.066331991,-6.52404406e-08,-6.52404404e-08,-9.04639345e-20
0.000270176111,0.446635525,0.157009557,9.0,0.0663183057,6.5499159e-08,6.54991588e-08,9.08227435e-20
0.000275176111,0.444738652,0.158818992,9.0,0.0663051841,-6.52433163e-08,-6.52433161e-08,-9.0467922e-20
0.000280176111,0.442851174,0.160627683,9.0,0.0662916317,6.55020355e-08,6.55020353e-08,9.08267322e-20
0.000285176111,0.440973044,0.162435629,9.0,0.0662786422,-6.52461919e-08,-6.52461917e-08,-9.04719094e-20
0.000290176111,0.439104215,0.164242832,9.0,0.0662652213,6.55049108e-08,6.55049106e-08,9.08307192e-20
0.000295176111,0.437244641,0.166049291,9.0,0.0662523627,-6.52490669e-08,-6.52490668e-08,-9.0475896e-20
0.000300176111,0.435394277,0.167855007,9.0,0.0662390719,6.55077856e-08,6.55077854e-08,9.08347054e-20
0.000305176111,0.433553077,0.169659981,9.0,0.0662263429,-6.52519414e-08,-6.52519413e-08,-9.04798819e-20
0.000310176111,0.431720995,0.171464213,9.0,0.066213181,6.55106598e-08,6.55106597e-08,9.08386909e-20
0.000315176111,0.429897986,0.173267703,9.0,0.0662005802,-6.52548154e-08,-6.52548153e-08,-9.0483867e-20
0.000320176111,0.428084006,0.175070452,9.0,0.066187546,6.55135336e-08,6.55135334e-08,9.08426757e-20
0.000325176111,0.42627901,0.176872461,9.0,0.0661750722,-6.52576889e-08,-6.52576887e-08,-9.04878514e-20
0.000330176111,0.424482953,0.178673729,9.0,0.0661621643,6.55164068e-08,6.55164066e-08,9.08466598e-20
0.000335176111,0.42269579,0.180474257,9.0,0.0661498162,-6.52605618e-08,-6.52605617e-08,-9.04918351e-20
0.000340176111,0.420917479,0.182274046,9.0,0.0661370335,6.55192794e-08,6.55192793e-08,9.08506431e-20
0.000345176111,0.419147974,0.184073097,9.0,0.0661248099,-6.
```

> Artifact truncated in this preview. The original file remains available through the manifest path.
