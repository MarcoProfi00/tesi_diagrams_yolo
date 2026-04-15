# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `24` (`24.png`) from pipeline variant `topology_v9.1_analog_meter_connector_transformer` was exported from `06_match_terminals_to_nets`.
The topology contains 13 components, 24 terminals, 11 nets, and 24 terminal-to-net connections.
Explicit power sources: Battery 2.1.
Explicit ground references: GND 9.1, GND 9.2, GND 9.3, GND 9.4, GND 9.5.

# Main Branches
- `N2` (source_connected_branch, importance=high): Net N2 forms a source connected branch connecting Battery 2.1, Fuse 8.1.
- `N5` (shared_internal_branch, importance=medium): Net N5 forms a shared internal branch connecting Switch 25.1, Capacitor 4.1, Connector 5.1.
- `N10` (single_terminal_stub, importance=low): Net N10 forms a single terminal stub connecting Lamp 13.1.
- `N11` (single_terminal_stub, importance=low): Net N11 forms a single terminal stub connecting GND 9.5.
- `N9` (single_terminal_stub, importance=low): Net N9 forms a single terminal stub connecting Lamp 13.1, Switch 25.1.

# Component Descriptions
- `12.1` (LED): generic circuit element [specificity=low, confidence=0.55] LED 12.1 is described as generic circuit element. It is connected to nets N7, N8 and to Resistor 22.1 via N7; GND 9.4 via N8.
- `13.1` (Lamp): generic circuit element [specificity=low, confidence=0.55] Lamp 13.1 is described as generic circuit element. It is connected to nets N10, N9 and to Switch 25.1 via N9.
- `2.1` (Battery): power source [specificity=high, confidence=0.98] Battery 2.1 is described as power source. It is connected to nets N1, N2 and to Fuse 8.1 via N2; GND 9.1 via N1.
- `22.1` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.1 is described as passive component. It is connected to nets N6, N7 and to LED 12.1 via N7; Capacitor 4.1 via N6; Connector 5.1 via N6; GND 9.3 via N6.
- `25.1` (Switch): active component [specificity=low, confidence=0.72] Switch 25.1 is described as active component. It is connected to nets N5, N9 and to Lamp 13.1 via N9; Capacitor 4.1 via N5; Connector 5.1 via N5.
- `4.1` (Capacitor): passive component [specificity=medium, confidence=0.76] Capacitor 4.1 is described as passive component. It is connected to nets N5, N6 and to Resistor 22.1 via N6; Switch 25.1 via N5; Connector 5.1 via N5, N6; GND 9.3 via N6.
- `5.1` (Connector): generic circuit element [specificity=low, confidence=0.55] Connector 5.1 is described as generic circuit element. It is connected to nets N3, N4, N5, N6 and to Resistor 22.1 via N6; Switch 25.1 via N5; Capacitor 4.1 via N5, N6; Fuse 8.1 via N3; GND 9.2 via N4; GND 9.3 via N6.
- `8.1` (Fuse): generic circuit element [specificity=low, confidence=0.55] Fuse 8.1 is described as generic circuit element. It is connected to nets N2, N3 and to Battery 2.1 via N2; Connector 5.1 via N3.
- `9.1` (GND): ground reference [specificity=high, confidence=1.00] GND 9.1 is described as ground reference. It is connected to nets N1 and to Battery 2.1 via N1.
- `9.2` (GND): ground reference [specificity=high, confidence=1.00] GND 9.2 is described as ground reference. It is connected to nets N4 and to Connector 5.1 via N4.
- `9.3` (GND): ground reference [specificity=high, confidence=1.00] GND 9.3 is described as ground reference. It is connected to nets N6 and to Resistor 22.1 via N6; Capacitor 4.1 via N6; Connector 5.1 via N6.
- `9.4` (GND): ground reference [specificity=high, confidence=1.00] GND 9.4 is described as ground reference. It is connected to nets N8 and to LED 12.1 via N8.
- `9.5` (GND): ground reference [specificity=high, confidence=1.00] GND 9.5 is described as ground reference. It is connected to nets N11 and to no other modeled components.

# Net Descriptions
- `N1`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N2`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N3`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N4`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N5`: shared internal branch [specificity=medium, confidence=0.72] Basis: The net behaves like a shared internal junction between multiple components.
- `N6`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N7`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N8`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N9`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N10`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N11`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.

# Aggregated Relations
- `N2`: N2 is a source connected branch connecting Battery 2.1 positive, Fuse 8.1 terminal t1.
- `N5`: N5 is a shared internal branch connecting Switch 25.1 terminal t1, Capacitor 4.1 terminal t1, Connector 5.1 pin2.
- `N6`: N6 is a ground return connecting Resistor 22.1 terminal t1, Capacitor 4.1 terminal t2, Connector 5.1 pin4, GND 9.3 terminal t1.
- `N1`: N1 is a ground return connecting Battery 2.1 negative, GND 9.1 terminal t1.
- `N3`: N3 is a local interconnect connecting Connector 5.1 pin1, Fuse 8.1 terminal t2.
- `N4`: N4 is a ground return connecting Connector 5.1 pin5, GND 9.2 terminal t1.
- `N7`: N7 is a local interconnect connecting LED 12.1 anode, Resistor 22.1 terminal t2.
- `N8`: N8 is a ground return connecting LED 12.1 cathode, GND 9.4 terminal t1.

# Functional Paths
- `P1` `ground_to_device_path`: Ground to device path: GND 9.1 -> N1 (ground return) -> Battery 2.1 -> N2 (source connected branch) -> Fuse 8.1 -> N3 (local interconnect) -> Connector 5.1 -> N5 (shared internal branch) -> Switch 25.1. Confidence: 0.68 (heuristic_inference).
- `P2` `ground_to_device_path`: Ground to device path: GND 9.2 -> N4 (ground return) -> Connector 5.1 -> N5 (shared internal branch) -> Switch 25.1. Confidence: 0.68 (heuristic_inference).
- `P3` `ground_to_device_path`: Ground to device path: GND 9.3 -> N6 (ground return) -> Capacitor 4.1 -> N5 (shared internal branch) -> Switch 25.1. Confidence: 0.68 (heuristic_inference).
- `P4` `ground_to_device_path`: Ground to device path: GND 9.4 -> N8 (ground return) -> LED 12.1 -> N7 (local interconnect) -> Resistor 22.1 -> N6 (ground return) -> Capacitor 4.1 -> N5 (shared internal branch) -> Switch 25.1. Confidence: 0.68 (heuristic_inference).

# Structural Patterns
- `multiple_terminals_same_net` on `5.1`: Connector 5.1 has terminals 5.1:pin2, 5.1:pin3 on the same net N5.
- `single_terminal_stub` on `N10`: Net N10 currently touches only Lamp 13.1 terminal t2.
- `single_terminal_stub` on `N11`: Net N11 currently touches only GND 9.5 terminal t1.
- `single_terminal_stub` on `N9`: Net N9 currently touches only Switch 25.1 terminal t2.

# Terminal Facts
- `12.1:anode`: LED 12.1 terminal anode is connected on net N7 with Resistor 22.1.
- `12.1:cathode`: LED 12.1 terminal cathode is connected on net N8 with GND 9.4.
- `13.1:t1`: Lamp 13.1 terminal t1 is connected on net N9 with Switch 25.1.
- `13.1:t2`: Lamp 13.1 terminal t2 is the only modeled terminal on net N10.
- `2.1:positive`: Battery 2.1 terminal positive is connected on net N2 with Fuse 8.1.
- `2.1:negative`: Battery 2.1 terminal negative is connected on net N1 with GND 9.1.
- `22.1:t1`: Resistor 22.1 terminal t1 is connected on net N6 with Capacitor 4.1, Connector 5.1, GND 9.3.
- `22.1:t2`: Resistor 22.1 terminal t2 is connected on net N7 with LED 12.1.
- `25.1:t1`: Switch 25.1 terminal t1 is connected on net N5 with Capacitor 4.1, Connector 5.1.
- `25.1:t2`: Switch 25.1 terminal t2 is connected on net N9 with Lamp 13.1.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
