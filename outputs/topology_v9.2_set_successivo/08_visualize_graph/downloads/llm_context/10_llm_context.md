# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `10` (`10.jpg`) from pipeline variant `topology_v9.2_set_successivo` was exported from `06_match_terminals_to_nets`.
The topology contains 15 components, 36 terminals, 11 nets, and 36 terminal-to-net connections.
Explicit power sources: Voltage_Source 31.1.

# Main Branches
- `N3` (source_connected_branch, importance=high): Net N3 forms a source connected branch connecting LED 12.2, NPN_Transistor 18.2, NPN_Transistor 18.4, Voltage_Source 31.1, Diode 7.2.
- `N4` (source_connected_branch, importance=high): Net N4 forms a source connected branch connecting LED 12.1, NPN_Transistor 18.1, NPN_Transistor 18.3, Voltage_Source 31.1, Diode 7.1.
- `N7` (shared_internal_branch, importance=medium): Net N7 forms a shared internal branch connecting Inductor 10.1, LED 12.1, LED 12.2, NPN_Transistor 18.1, NPN_Transistor 18.2, NPN_Transistor 18.3, NPN_Transistor 18.4, Transformer 28.1, Capacitor 4.1, Diode 7.1, Diode 7.2.
- `N9` (shared_internal_branch, importance=medium): Net N9 forms a shared internal branch connecting Resistor 22.1, Switch 25.1, Transformer 28.1.
- `N1` (single_terminal_stub, importance=low): Net N1 forms a single terminal stub connecting NPN_Transistor 18.1.
- `N2` (single_terminal_stub, importance=low): Net N2 forms a single terminal stub connecting NPN_Transistor 18.2.

# Component Descriptions
- `10.1` (Inductor): passive component [specificity=medium, confidence=0.76] Inductor 10.1 is described as passive component. It is connected to nets N7 and to LED 12.1 via N7; LED 12.2 via N7; NPN_Transistor 18.1 via N7; NPN_Transistor 18.2 via N7; NPN_Transistor 18.3 via N7; NPN_Transistor 18.4 via N7; Transformer 28.1 via N7; Capacitor 4.1 via N7; Diode 7.1 via N7; Diode 7.2 via N7.
- `12.1` (LED): generic circuit element [specificity=low, confidence=0.55] LED 12.1 is described as generic circuit element. It is connected to nets N4, N7 and to Inductor 10.1 via N7; LED 12.2 via N7; NPN_Transistor 18.1 via N4, N7; NPN_Transistor 18.2 via N7; NPN_Transistor 18.3 via N4, N7; NPN_Transistor 18.4 via N7; Transformer 28.1 via N7; Voltage_Source 31.1 via N4; Capacitor 4.1 via N7; Diode 7.1 via N4, N7; Diode 7.2 via N7.
- `12.2` (LED): generic circuit element [specificity=low, confidence=0.55] LED 12.2 is described as generic circuit element. It is connected to nets N3, N7 and to Inductor 10.1 via N7; LED 12.1 via N7; NPN_Transistor 18.1 via N7; NPN_Transistor 18.2 via N3, N7; NPN_Transistor 18.3 via N7; NPN_Transistor 18.4 via N3, N7; Transformer 28.1 via N7; Voltage_Source 31.1 via N3; Capacitor 4.1 via N7; Diode 7.1 via N7; Diode 7.2 via N3, N7.
- `18.1` (NPN_Transistor): active component [specificity=low, confidence=0.72] NPN_Transistor 18.1 is described as active component. It is connected to nets N1, N4, N7 and to Inductor 10.1 via N7; LED 12.1 via N4, N7; LED 12.2 via N7; NPN_Transistor 18.2 via N7; NPN_Transistor 18.3 via N4, N7; NPN_Transistor 18.4 via N7; Transformer 28.1 via N7; Voltage_Source 31.1 via N4; Capacitor 4.1 via N7; Diode 7.1 via N4, N7; Diode 7.2 via N7.
- `18.2` (NPN_Transistor): active component [specificity=low, confidence=0.72] NPN_Transistor 18.2 is described as active component. It is connected to nets N2, N3, N7 and to Inductor 10.1 via N7; LED 12.1 via N7; LED 12.2 via N3, N7; NPN_Transistor 18.1 via N7; NPN_Transistor 18.3 via N7; NPN_Transistor 18.4 via N3, N7; Transformer 28.1 via N7; Voltage_Source 31.1 via N3; Capacitor 4.1 via N7; Diode 7.1 via N7; Diode 7.2 via N3, N7.
- `18.3` (NPN_Transistor): active component [specificity=low, confidence=0.72] NPN_Transistor 18.3 is described as active component. It is connected to nets N4, N5, N7 and to Inductor 10.1 via N7; LED 12.1 via N4, N7; LED 12.2 via N7; NPN_Transistor 18.1 via N4, N7; NPN_Transistor 18.2 via N7; NPN_Transistor 18.4 via N7; Transformer 28.1 via N7; Voltage_Source 31.1 via N4; Capacitor 4.1 via N7; Diode 7.1 via N4, N7; Diode 7.2 via N7.
- `18.4` (NPN_Transistor): active component [specificity=low, confidence=0.72] NPN_Transistor 18.4 is described as active component. It is connected to nets N3, N6, N7 and to Inductor 10.1 via N7; LED 12.1 via N7; LED 12.2 via N3, N7; NPN_Transistor 18.1 via N7; NPN_Transistor 18.2 via N3, N7; NPN_Transistor 18.3 via N7; Transformer 28.1 via N7; Voltage_Source 31.1 via N3; Capacitor 4.1 via N7; Diode 7.1 via N7; Diode 7.2 via N3, N7.
- `22.1` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.1 is described as passive component. It is connected to nets N10, N9 and to Signal_Source 23.1 via N10; Switch 25.1 via N9; Transformer 28.1 via N10, N9.
- `23.1` (Signal_Source): generic circuit element [specificity=low, confidence=0.55] Signal_Source 23.1 is described as generic circuit element. It is connected to nets N10, N11 and to Resistor 22.1 via N10; Switch 25.1 via N11; Transformer 28.1 via N10.
- `25.1` (Switch): active component [specificity=low, confidence=0.72] Switch 25.1 is described as active component. It is connected to nets N11, N9 and to Resistor 22.1 via N9; Signal_Source 23.1 via N11; Transformer 28.1 via N9.
- `28.1` (Transformer): generic circuit element [specificity=low, confidence=0.55] Transformer 28.1 is described as generic circuit element. It is connected to nets N10, N7, N8, N9 and to Inductor 10.1 via N7; LED 12.1 via N7; LED 12.2 via N7; NPN_Transistor 18.1 via N7; NPN_Transistor 18.2 via N7; NPN_Transistor 18.3 via N7; NPN_Transistor 18.4 via N7; Resistor 22.1 via N10, N9; Signal_Source 23.1 via N10; Switch 25.1 via N9; Capacitor 4.1 via N7; Diode 7.1 via N7; Diode 7.2 via N7.
- `31.1` (Voltage_Source): power source [specificity=high, confidence=0.98] Voltage_Source 31.1 is described as power source. It is connected to nets N3, N4 and to LED 12.1 via N4; LED 12.2 via N3; NPN_Transistor 18.1 via N4; NPN_Transistor 18.2 via N3; NPN_Transistor 18.3 via N4; NPN_Transistor 18.4 via N3; Diode 7.1 via N4; Diode 7.2 via N3.
- `4.1` (Capacitor): passive component [specificity=medium, confidence=0.76] Capacitor 4.1 is described as passive component. It is connected to nets N7 and to Inductor 10.1 via N7; LED 12.1 via N7; LED 12.2 via N7; NPN_Transistor 18.1 via N7; NPN_Transistor 18.2 via N7; NPN_Transistor 18.3 via N7; NPN_Transistor 18.4 via N7; Transformer 28.1 via N7; Diode 7.1 via N7; Diode 7.2 via N7.
- `7.1` (Diode): passive component [specificity=medium, confidence=0.76] Diode 7.1 is described as passive component. It is connected to nets N4, N7 and to Inductor 10.1 via N7; LED 12.1 via N4, N7; LED 12.2 via N7; NPN_Transistor 18.1 via N4, N7; NPN_Transistor 18.2 via N7; NPN_Transistor 18.3 via N4, N7; NPN_Transistor 18.4 via N7; Transformer 28.1 via N7; Voltage_Source 31.1 via N4; Capacitor 4.1 via N7; Diode 7.2 via N7.
- `7.2` (Diode): passive component [specificity=medium, confidence=0.76] Diode 7.2 is described as passive component. It is connected to nets N3, N7 and to Inductor 10.1 via N7; LED 12.1 via N7; LED 12.2 via N3, N7; NPN_Transistor 18.1 via N7; NPN_Transistor 18.2 via N3, N7; NPN_Transistor 18.3 via N7; NPN_Transistor 18.4 via N3, N7; Transformer 28.1 via N7; Voltage_Source 31.1 via N3; Capacitor 4.1 via N7; Diode 7.1 via N7.

# Net Descriptions
- `N1`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N2`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N3`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N4`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N5`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N6`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N7`: shared internal branch [specificity=medium, confidence=0.70] Basis: The net behaves like a multi-device internal junction and its terminal semantics are mixed or widely shared.
- `N8`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N9`: shared internal branch [specificity=medium, confidence=0.72] Basis: The net behaves like a shared internal junction between multiple components.
- `N10`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N11`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.

# Aggregated Relations
- `N3`: N3 is a source connected branch connecting LED 12.2 cathode, NPN_Transistor 18.2 collector, NPN_Transistor 18.4 collector, Voltage_Source 31.1 positive, Diode 7.2 cathode.
- `N4`: N4 is a source connected branch connecting LED 12.1 anode, NPN_Transistor 18.1 emitter, NPN_Transistor 18.3 emitter, Voltage_Source 31.1 negative, Diode 7.1 anode.
- `N7`: N7 is a shared internal branch connecting Inductor 10.1 terminal t1, LED 12.1 cathode, LED 12.2 anode, NPN_Transistor 18.1 collector, NPN_Transistor 18.2 emitter, NPN_Transistor 18.3 collector, NPN_Transistor 18.4 emitter, Transformer 28.1 terminal t1, Capacitor 4.1 terminal t1, Diode 7.1 cathode, Diode 7.2 anode.
- `N9`: N9 is a shared internal branch connecting Resistor 22.1 terminal t1, Switch 25.1 terminal t1, Transformer 28.1 terminal t2.
- `N10`: N10 is a local interconnect connecting Resistor 22.1 terminal t2, Signal_Source 23.1 terminal t2, Transformer 28.1 terminal t4.
- `N11`: N11 is a local interconnect connecting Signal_Source 23.1 terminal t1, Switch 25.1 terminal t2.

# Functional Paths
- No functional path summary was produced from the current topology.

# Structural Patterns
- `high_degree_shared_branch` on `N7`: Net N7 is a shared internal branch touching 11 modeled components.
- `multiple_terminals_same_net` on `10.1`: Inductor 10.1 has terminals 10.1:t1, 10.1:t2 on the same net N7.
- `multiple_terminals_same_net` on `4.1`: Capacitor 4.1 has terminals 4.1:t1, 4.1:t2 on the same net N7.
- `single_terminal_stub` on `N1`: Net N1 currently touches only NPN_Transistor 18.1 base.
- `single_terminal_stub` on `N2`: Net N2 currently touches only NPN_Transistor 18.2 base.
- `single_terminal_stub` on `N5`: Net N5 currently touches only NPN_Transistor 18.3 base.
- `single_terminal_stub` on `N6`: Net N6 currently touches only NPN_Transistor 18.4 base.
- `single_terminal_stub` on `N8`: Net N8 currently touches only Transformer 28.1 terminal t3.

# Terminal Facts
- `10.1:t1`: Inductor 10.1 terminal t1 is connected on net N7 with Capacitor 4.1, Diode 7.1, Diode 7.2, Inductor 10.1, LED 12.1, LED 12.2, NPN_Transistor 18.1, NPN_Transistor 18.2, NPN_Transistor 18.3, NPN_Transistor 18.4, Transformer 28.1.
- `10.1:t2`: Inductor 10.1 terminal t2 is connected on net N7 with Capacitor 4.1, Diode 7.1, Diode 7.2, Inductor 10.1, LED 12.1, LED 12.2, NPN_Transistor 18.1, NPN_Transistor 18.2, NPN_Transistor 18.3, NPN_Transistor 18.4, Transformer 28.1.
- `12.1:cathode`: LED 12.1 terminal cathode is connected on net N7 with Capacitor 4.1, Diode 7.1, Diode 7.2, Inductor 10.1, LED 12.2, NPN_Transistor 18.1, NPN_Transistor 18.2, NPN_Transistor 18.3, NPN_Transistor 18.4, Transformer 28.1.
- `12.1:anode`: LED 12.1 terminal anode is connected on net N4 with Diode 7.1, NPN_Transistor 18.1, NPN_Transistor 18.3, Voltage_Source 31.1.
- `12.2:cathode`: LED 12.2 terminal cathode is connected on net N3 with Diode 7.2, NPN_Transistor 18.2, NPN_Transistor 18.4, Voltage_Source 31.1.
- `12.2:anode`: LED 12.2 terminal anode is connected on net N7 with Capacitor 4.1, Diode 7.1, Diode 7.2, Inductor 10.1, LED 12.1, NPN_Transistor 18.1, NPN_Transistor 18.2, NPN_Transistor 18.3, NPN_Transistor 18.4, Transformer 28.1.
- `18.1:B`: NPN_Transistor 18.1 terminal B is the only modeled terminal on net N1.
- `18.1:C`: NPN_Transistor 18.1 terminal C is connected on net N7 with Capacitor 4.1, Diode 7.1, Diode 7.2, Inductor 10.1, LED 12.1, LED 12.2, NPN_Transistor 18.2, NPN_Transistor 18.3, NPN_Transistor 18.4, Transformer 28.1.
- `18.1:E`: NPN_Transistor 18.1 terminal E is connected on net N4 with Diode 7.1, LED 12.1, NPN_Transistor 18.3, Voltage_Source 31.1.
- `18.2:B`: NPN_Transistor 18.2 terminal B is the only modeled terminal on net N2.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
