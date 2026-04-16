# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `4` (`4.jpg`) from pipeline variant `topology_v9.2_set_successivo` was exported from `06_match_terminals_to_nets`.
The topology contains 13 components, 25 terminals, 10 nets, and 25 terminal-to-net connections.
Explicit power sources: Battery 2.1.
Explicit ground references: GND 9.1.
Possible external outputs or bridge interfaces: Terminal 26.1.

# Main Branches
- `N1` (source_connected_branch, importance=high): Net N1 forms a source connected branch connecting Battery 2.1, Fuse 8.1.
- `N4` (source_connected_branch, importance=high): Net N4 forms a source connected branch connecting Analog_Meter 0.1, LED 12.1, Battery 2.1, Variable_Resistor 30.2, Diode 7.1.
- `N7` (external_interface_branch, importance=high): Net N7 forms an external interface branch connecting Switch 25.1, Terminal 26.1.
- `N9` (external_interface_branch, importance=high): Net N9 forms an external interface branch connecting Lamp 13.1, Terminal 26.1.
- `N5` (shared_internal_branch, importance=medium): Net N5 forms a shared internal branch connecting Signal_Source 23.1, Switch 25.1, Variable_Resistor 30.1.
- `N8` (single_terminal_stub, importance=low): Net N8 forms a single terminal stub connecting Analog_Meter 0.1, Lamp 13.1.

# Component Descriptions
- `0.1` (Analog_Meter): generic circuit element [specificity=low, confidence=0.55] Analog_Meter 0.1 is described as generic circuit element. It is connected to nets N4, N8 and to LED 12.1 via N4; Lamp 13.1 via N8; Battery 2.1 via N4; Variable_Resistor 30.2 via N4; Diode 7.1 via N4.
- `12.1` (LED): generic circuit element [specificity=low, confidence=0.55] LED 12.1 is described as generic circuit element. It is connected to nets N3, N4 and to Analog_Meter 0.1 via N4; Battery 2.1 via N4; Trim_Capacitor 29.1 via N3; Variable_Resistor 30.2 via N4; Diode 7.1 via N4.
- `13.1` (Lamp): generic circuit element [specificity=low, confidence=0.55] Lamp 13.1 is described as generic circuit element. It is connected to nets N8, N9 and to Analog_Meter 0.1 via N8; Terminal 26.1 via N9.
- `2.1` (Battery): power source [specificity=high, confidence=0.98] Battery 2.1 is described as power source. It is connected to nets N1, N4 and to Analog_Meter 0.1 via N4; LED 12.1 via N4; Variable_Resistor 30.2 via N4; Diode 7.1 via N4; Fuse 8.1 via N1.
- `23.1` (Signal_Source): generic circuit element [specificity=low, confidence=0.55] Signal_Source 23.1 is described as generic circuit element. It is connected to nets N2, N5 and to Switch 25.1 via N5; Trim_Capacitor 29.1 via N2; Variable_Resistor 30.1 via N5; Fuse 8.1 via N2.
- `25.1` (Switch): active component [specificity=low, confidence=0.72] Switch 25.1 is described as active component. It is connected to nets N5, N7 and to Signal_Source 23.1 via N5; Terminal 26.1 via N7; Variable_Resistor 30.1 via N5.
- `26.1` (Terminal): external interface [specificity=medium, confidence=0.82] Terminal 26.1 is described as external interface. It is connected to nets N7, N9 and to Lamp 13.1 via N9; Switch 25.1 via N7.
- `29.1` (Trim_Capacitor): generic circuit element [specificity=low, confidence=0.55] Trim_Capacitor 29.1 is described as generic circuit element. It is connected to nets N2, N3 and to LED 12.1 via N3; Signal_Source 23.1 via N2; Fuse 8.1 via N2.
- `30.1` (Variable_Resistor): generic circuit element [specificity=low, confidence=0.55] Variable_Resistor 30.1 is described as generic circuit element. It is connected to nets N5, N6 and to Signal_Source 23.1 via N5; Switch 25.1 via N5; Variable_Resistor 30.2 via N6.
- `30.2` (Variable_Resistor): generic circuit element [specificity=low, confidence=0.55] Variable_Resistor 30.2 is described as generic circuit element. It is connected to nets N4, N6 and to Analog_Meter 0.1 via N4; LED 12.1 via N4; Battery 2.1 via N4; Variable_Resistor 30.1 via N6; Diode 7.1 via N4.
- `7.1` (Diode): passive component [specificity=medium, confidence=0.76] Diode 7.1 is described as passive component. It is connected to nets N10, N4 and to Analog_Meter 0.1 via N4; LED 12.1 via N4; Battery 2.1 via N4; Variable_Resistor 30.2 via N4; GND 9.1 via N10.
- `8.1` (Fuse): generic circuit element [specificity=low, confidence=0.55] Fuse 8.1 is described as generic circuit element. It is connected to nets N1, N2 and to Battery 2.1 via N1; Signal_Source 23.1 via N2; Trim_Capacitor 29.1 via N2.
- `9.1` (GND): ground reference [specificity=high, confidence=1.00] GND 9.1 is described as ground reference. It is connected to nets N10 and to Diode 7.1 via N10.

# Net Descriptions
- `N1`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N2`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N3`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N4`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N5`: shared internal branch [specificity=medium, confidence=0.72] Basis: The net behaves like a shared internal junction between multiple components.
- `N6`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N7`: external interface branch [specificity=low, confidence=0.68] Basis: The net reaches at least one explicit external interface.
- `N8`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N9`: external interface branch [specificity=low, confidence=0.68] Basis: The net reaches at least one explicit external interface.
- `N10`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.

# Aggregated Relations
- `N1`: N1 is a source connected branch connecting Battery 2.1 positive, Fuse 8.1 terminal t1.
- `N4`: N4 is a source connected branch connecting Analog_Meter 0.1 terminal t2, LED 12.1 cathode, Battery 2.1 negative, Variable_Resistor 30.2 terminal t2, Diode 7.1 cathode.
- `N7`: N7 is a external interface branch connecting Switch 25.1 terminal t2, Terminal 26.1 terminal t1.
- `N9`: N9 is a external interface branch connecting Lamp 13.1 terminal t1, Terminal 26.1 terminal t2.
- `N5`: N5 is a shared internal branch connecting Signal_Source 23.1 terminal t2, Switch 25.1 terminal t1, Variable_Resistor 30.1 terminal t1.
- `N10`: N10 is a ground return connecting Diode 7.1 anode, GND 9.1 terminal t1.
- `N2`: N2 is a local interconnect connecting Signal_Source 23.1 terminal t1, Trim_Capacitor 29.1 terminal t1, Fuse 8.1 terminal t2.
- `N3`: N3 is a local interconnect connecting LED 12.1 anode, Trim_Capacitor 29.1 terminal t2.

# Functional Paths
- `P1` `source_to_interface_path`: Source to interface path: Battery 2.1 -> N4 (source connected branch) -> Analog_Meter 0.1 -> N8 (single terminal stub) -> Lamp 13.1 -> N9 (external interface branch) -> Terminal 26.1. Confidence: 0.78 (heuristic_inference).
- `P2` `device_to_interface_path`: Device to interface path: Switch 25.1 -> N7 (external interface branch) -> Terminal 26.1. Confidence: 0.74 (heuristic_inference).
- `P3` `ground_to_device_path`: Ground to device path: GND 9.1 -> N10 (ground return) -> Diode 7.1 -> N4 (source connected branch) -> Variable_Resistor 30.2 -> N6 (local interconnect) -> Variable_Resistor 30.1 -> N5 (shared internal branch) -> Switch 25.1. Confidence: 0.68 (heuristic_inference).
- `P4` `interface_bridge_path`: Interface bridge path: N7 (external interface branch) -> Terminal 26.1 -> N9 (external interface branch). Confidence: 0.84 (topological_fact).

# Structural Patterns
- `single_terminal_stub` on `N8`: Net N8 currently touches only Lamp 13.1 terminal t2.

# Terminal Facts
- `0.1:t1`: Analog_Meter 0.1 terminal t1 is connected on net N8 with Lamp 13.1.
- `0.1:t2`: Analog_Meter 0.1 terminal t2 is connected on net N4 with Battery 2.1, Diode 7.1, LED 12.1, Variable_Resistor 30.2.
- `12.1:anode`: LED 12.1 terminal anode is connected on net N3 with Trim_Capacitor 29.1.
- `12.1:cathode`: LED 12.1 terminal cathode is connected on net N4 with Analog_Meter 0.1, Battery 2.1, Diode 7.1, Variable_Resistor 30.2.
- `13.1:t1`: Lamp 13.1 terminal t1 is connected on net N9 with Terminal 26.1.
- `13.1:t2`: Lamp 13.1 terminal t2 is connected on net N8 with Analog_Meter 0.1.
- `2.1:positive`: Battery 2.1 terminal positive is connected on net N1 with Fuse 8.1.
- `2.1:negative`: Battery 2.1 terminal negative is connected on net N4 with Analog_Meter 0.1, Diode 7.1, LED 12.1, Variable_Resistor 30.2.
- `23.1:t1`: Signal_Source 23.1 terminal t1 is connected on net N2 with Fuse 8.1, Trim_Capacitor 29.1.
- `23.1:t2`: Signal_Source 23.1 terminal t2 is connected on net N5 with Switch 25.1, Variable_Resistor 30.1.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
