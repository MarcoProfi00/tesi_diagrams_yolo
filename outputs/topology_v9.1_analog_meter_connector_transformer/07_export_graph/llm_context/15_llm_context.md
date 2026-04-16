# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `15` (`15.png`) from pipeline variant `topology_v9.1_analog_meter_connector_transformer` was exported from `06_match_terminals_to_nets`.
The topology contains 10 components, 14 terminals, 9 nets, and 14 terminal-to-net connections.
Explicit power sources: Battery 2.1.
Explicit ground references: GND 9.1, GND 9.2, GND 9.3, GND 9.4.

# Main Branches
- `N2` (source_connected_branch, importance=high): Net N2 forms a source connected branch connecting Battery 2.1, Switch 25.1.
- `N3` (single_terminal_stub, importance=low): Net N3 forms a single terminal stub connecting Switch 25.1.
- `N4` (single_terminal_stub, importance=low): Net N4 forms a single terminal stub connecting GND 9.2.
- `N5` (single_terminal_stub, importance=low): Net N5 forms a single terminal stub connecting Lamp 13.1.
- `N6` (single_terminal_stub, importance=low): Net N6 forms a single terminal stub connecting Resistor 22.1.

# Component Descriptions
- `11.1` (Integrated_Circuit): generic circuit element [specificity=low, confidence=0.55] Integrated_Circuit 11.1 is described as generic circuit element. It is connected to nets none and to no other modeled components.
- `12.1` (LED): generic circuit element [specificity=low, confidence=0.55] LED 12.1 is described as generic circuit element. It is connected to nets N8, N9 and to Resistor 22.1 via N8; GND 9.4 via N9.
- `13.1` (Lamp): generic circuit element [specificity=low, confidence=0.55] Lamp 13.1 is described as generic circuit element. It is connected to nets N5, N7 and to GND 9.3 via N7.
- `2.1` (Battery): power source [specificity=high, confidence=0.98] Battery 2.1 is described as power source. It is connected to nets N1, N2 and to Switch 25.1 via N2; GND 9.1 via N1.
- `22.1` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.1 is described as passive component. It is connected to nets N6, N8 and to LED 12.1 via N8.
- `25.1` (Switch): active component [specificity=low, confidence=0.72] Switch 25.1 is described as active component. It is connected to nets N2, N3 and to Battery 2.1 via N2.
- `9.1` (GND): ground reference [specificity=high, confidence=1.00] GND 9.1 is described as ground reference. It is connected to nets N1 and to Battery 2.1 via N1.
- `9.2` (GND): ground reference [specificity=high, confidence=1.00] GND 9.2 is described as ground reference. It is connected to nets N4 and to no other modeled components.
- `9.3` (GND): ground reference [specificity=high, confidence=1.00] GND 9.3 is described as ground reference. It is connected to nets N7 and to Lamp 13.1 via N7.
- `9.4` (GND): ground reference [specificity=high, confidence=1.00] GND 9.4 is described as ground reference. It is connected to nets N9 and to LED 12.1 via N9.

# Net Descriptions
- `N1`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N2`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N3`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N4`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N5`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N6`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N7`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N8`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N9`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.

# Aggregated Relations
- `N2`: N2 is a source connected branch connecting Battery 2.1 positive, Switch 25.1 terminal t1.
- `N1`: N1 is a ground return connecting Battery 2.1 negative, GND 9.1 terminal t1.
- `N7`: N7 is a ground return connecting Lamp 13.1 terminal t2, GND 9.3 terminal t1.
- `N8`: N8 is a local interconnect connecting LED 12.1 anode, Resistor 22.1 terminal t2.
- `N9`: N9 is a ground return connecting LED 12.1 cathode, GND 9.4 terminal t1.

# Functional Paths
- `P1` `ground_to_device_path`: Ground to device path: GND 9.1 -> N1 (ground return) -> Battery 2.1 -> N2 (source connected branch) -> Switch 25.1. Confidence: 0.68 (heuristic_inference).

# Structural Patterns
- `single_terminal_stub` on `N3`: Net N3 currently touches only Switch 25.1 terminal t2.
- `single_terminal_stub` on `N4`: Net N4 currently touches only GND 9.2 terminal t1.
- `single_terminal_stub` on `N5`: Net N5 currently touches only Lamp 13.1 terminal t1.
- `single_terminal_stub` on `N6`: Net N6 currently touches only Resistor 22.1 terminal t1.

# Terminal Facts
- `12.1:anode`: LED 12.1 terminal anode is connected on net N8 with Resistor 22.1.
- `12.1:cathode`: LED 12.1 terminal cathode is connected on net N9 with GND 9.4.
- `13.1:t1`: Lamp 13.1 terminal t1 is the only modeled terminal on net N5.
- `13.1:t2`: Lamp 13.1 terminal t2 is connected on net N7 with GND 9.3.
- `2.1:positive`: Battery 2.1 terminal positive is connected on net N2 with Switch 25.1.
- `2.1:negative`: Battery 2.1 terminal negative is connected on net N1 with GND 9.1.
- `22.1:t1`: Resistor 22.1 terminal t1 is the only modeled terminal on net N6.
- `22.1:t2`: Resistor 22.1 terminal t2 is connected on net N8 with LED 12.1.
- `25.1:t1`: Switch 25.1 terminal t1 is connected on net N2 with Battery 2.1.
- `25.1:t2`: Switch 25.1 terminal t2 is the only modeled terminal on net N3.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
