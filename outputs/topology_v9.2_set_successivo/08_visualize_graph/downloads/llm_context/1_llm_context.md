# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `1` (`1.jpg`) from pipeline variant `topology_v9.2_set_successivo` was exported from `06_match_terminals_to_nets`.
The topology contains 13 components, 24 terminals, 10 nets, and 24 terminal-to-net connections.
Explicit power sources: Battery 2.1.
Explicit ground references: GND 9.1, GND 9.2.

# Main Branches
- `N1` (source_connected_branch, importance=high): Net N1 forms a source connected branch connecting Battery 2.1, Fuse 8.1.
- `N2` (source_connected_branch, importance=high): Net N2 forms a source connected branch connecting Battery 2.1, Variable_Resistor 30.1.
- `N6` (shared_internal_branch, importance=medium): Net N6 forms a shared internal branch connecting Inductor 10.1, Lamp 13.1, Switch 25.1, Capacitor 4.1.
- `N10` (single_terminal_stub, importance=low): Net N10 forms a single terminal stub connecting Analog_Meter 0.1, Lamp 13.1.
- `N9` (single_terminal_stub, importance=low): Net N9 forms a single terminal stub connecting Analog_Meter 0.1, Resistor 22.1.

# Component Descriptions
- `0.1` (Analog_Meter): generic circuit element [specificity=low, confidence=0.55] Analog_Meter 0.1 is described as generic circuit element. It is connected to nets N10, N9 and to Lamp 13.1 via N10; Resistor 22.1 via N9.
- `10.1` (Inductor): passive component [specificity=medium, confidence=0.76] Inductor 10.1 is described as passive component. It is connected to nets N6, N8 and to Lamp 13.1 via N6; Switch 25.1 via N6; Capacitor 4.1 via N6; Diode 7.1 via N8.
- `12.1` (LED): generic circuit element [specificity=low, confidence=0.55] LED 12.1 is described as generic circuit element. It is connected to nets N4, N5 and to Resistor 22.1 via N5; Variable_Resistor 30.1 via N5; Capacitor 4.1 via N4; GND 9.1 via N5.
- `13.1` (Lamp): generic circuit element [specificity=low, confidence=0.55] Lamp 13.1 is described as generic circuit element. It is connected to nets N10, N6 and to Analog_Meter 0.1 via N10; Inductor 10.1 via N6; Switch 25.1 via N6; Capacitor 4.1 via N6.
- `2.1` (Battery): power source [specificity=high, confidence=0.98] Battery 2.1 is described as power source. It is connected to nets N1, N2 and to Variable_Resistor 30.1 via N2; Fuse 8.1 via N1.
- `22.1` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.1 is described as passive component. It is connected to nets N5, N9 and to Analog_Meter 0.1 via N9; LED 12.1 via N5; Variable_Resistor 30.1 via N5; GND 9.1 via N5.
- `25.1` (Switch): active component [specificity=low, confidence=0.72] Switch 25.1 is described as active component. It is connected to nets N3, N6 and to Inductor 10.1 via N6; Lamp 13.1 via N6; Capacitor 4.1 via N6; Fuse 8.1 via N3.
- `30.1` (Variable_Resistor): generic circuit element [specificity=low, confidence=0.55] Variable_Resistor 30.1 is described as generic circuit element. It is connected to nets N2, N5 and to LED 12.1 via N5; Battery 2.1 via N2; Resistor 22.1 via N5; GND 9.1 via N5.
- `4.1` (Capacitor): passive component [specificity=medium, confidence=0.76] Capacitor 4.1 is described as passive component. It is connected to nets N4, N6 and to Inductor 10.1 via N6; LED 12.1 via N4; Lamp 13.1 via N6; Switch 25.1 via N6.
- `7.1` (Diode): passive component [specificity=medium, confidence=0.76] Diode 7.1 is described as passive component. It is connected to nets N7, N8 and to Inductor 10.1 via N8; GND 9.2 via N7.
- `8.1` (Fuse): generic circuit element [specificity=low, confidence=0.55] Fuse 8.1 is described as generic circuit element. It is connected to nets N1, N3 and to Battery 2.1 via N1; Switch 25.1 via N3.
- `9.1` (GND): ground reference [specificity=high, confidence=1.00] GND 9.1 is described as ground reference. It is connected to nets N5 and to LED 12.1 via N5; Resistor 22.1 via N5; Variable_Resistor 30.1 via N5.
- `9.2` (GND): ground reference [specificity=high, confidence=1.00] GND 9.2 is described as ground reference. It is connected to nets N7 and to Diode 7.1 via N7.

# Net Descriptions
- `N1`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N2`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N3`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N4`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N5`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N6`: shared internal branch [specificity=medium, confidence=0.70] Basis: The net behaves like a multi-device internal junction and its terminal semantics are mixed or widely shared.
- `N7`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N8`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N9`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N10`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.

# Aggregated Relations
- `N1`: N1 is a source connected branch connecting Battery 2.1 positive, Fuse 8.1 terminal t1.
- `N2`: N2 is a source connected branch connecting Battery 2.1 negative, Variable_Resistor 30.1 terminal t1.
- `N5`: N5 is a ground return connecting LED 12.1 cathode, Resistor 22.1 terminal t1, Variable_Resistor 30.1 terminal t2, GND 9.1 terminal t1.
- `N6`: N6 is a shared internal branch connecting Inductor 10.1 terminal t1, Lamp 13.1 terminal t1, Switch 25.1 terminal t2, Capacitor 4.1 terminal t1.
- `N10`: N10 is a single terminal stub connecting Analog_Meter 0.1 terminal t1, Lamp 13.1 terminal t2.
- `N3`: N3 is a local interconnect connecting Switch 25.1 terminal t1, Fuse 8.1 terminal t2.
- `N4`: N4 is a local interconnect connecting LED 12.1 anode, Capacitor 4.1 terminal t2.
- `N7`: N7 is a ground return connecting Diode 7.1 cathode, GND 9.2 terminal t1.

# Functional Paths
- `P1` `ground_to_device_path`: Ground to device path: GND 9.1 -> N5 (ground return) -> LED 12.1 -> N4 (local interconnect) -> Capacitor 4.1 -> N6 (shared internal branch) -> Switch 25.1. Confidence: 0.68 (heuristic_inference).
- `P2` `ground_to_device_path`: Ground to device path: GND 9.2 -> N7 (ground return) -> Diode 7.1 -> N8 (local interconnect) -> Inductor 10.1 -> N6 (shared internal branch) -> Switch 25.1. Confidence: 0.68 (heuristic_inference).

# Structural Patterns
- `single_terminal_stub` on `N10`: Net N10 currently touches only Lamp 13.1 terminal t2.
- `single_terminal_stub` on `N9`: Net N9 currently touches only Resistor 22.1 terminal t2.

# Terminal Facts
- `0.1:t1`: Analog_Meter 0.1 terminal t1 is connected on net N10 with Lamp 13.1.
- `0.1:t2`: Analog_Meter 0.1 terminal t2 is connected on net N9 with Resistor 22.1.
- `10.1:t1`: Inductor 10.1 terminal t1 is connected on net N6 with Capacitor 4.1, Lamp 13.1, Switch 25.1.
- `10.1:t2`: Inductor 10.1 terminal t2 is connected on net N8 with Diode 7.1.
- `12.1:anode`: LED 12.1 terminal anode is connected on net N4 with Capacitor 4.1.
- `12.1:cathode`: LED 12.1 terminal cathode is connected on net N5 with GND 9.1, Resistor 22.1, Variable_Resistor 30.1.
- `13.1:t1`: Lamp 13.1 terminal t1 is connected on net N6 with Capacitor 4.1, Inductor 10.1, Switch 25.1.
- `13.1:t2`: Lamp 13.1 terminal t2 is connected on net N10 with Analog_Meter 0.1.
- `2.1:positive`: Battery 2.1 terminal positive is connected on net N1 with Fuse 8.1.
- `2.1:negative`: Battery 2.1 terminal negative is connected on net N2 with Variable_Resistor 30.1.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
