# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `6` (`6.jpg`) from pipeline variant `topology_v9.2_set_successivo` was exported from `06_match_terminals_to_nets`.
The topology contains 12 components, 24 terminals, 11 nets, and 24 terminal-to-net connections.
Explicit power sources: Battery 2.1.
Possible external outputs or bridge interfaces: Terminal 26.1.

# Main Branches
- `N1` (source_connected_branch, importance=high): Net N1 forms a source connected branch connecting Battery 2.1, Breaker 3.1.
- `N11` (external_interface_branch, importance=high): Net N11 forms an external interface branch connecting Meter 15.2, Terminal 26.1.
- `N2` (source_connected_branch, importance=high): Net N2 forms a source connected branch connecting Meter 15.1, Battery 2.1.
- `N8` (shared_internal_branch, importance=medium): Net N8 forms a shared internal branch connecting Inductor 10.1, Signal_Source 23.1, Terminal 26.1, Variable_Resistor 30.1.
- `N4` (single_terminal_stub, importance=low): Net N4 forms a single terminal stub connecting Analog_Meter 0.1.
- `N5` (single_terminal_stub, importance=low): Net N5 forms a single terminal stub connecting Analog_Meter 0.1.

# Component Descriptions
- `0.1` (Analog_Meter): generic circuit element [specificity=low, confidence=0.55] Analog_Meter 0.1 is described as generic circuit element. It is connected to nets N4, N5 and to no other modeled components.
- `10.1` (Inductor): passive component [specificity=medium, confidence=0.76] Inductor 10.1 is described as passive component. It is connected to nets N8, N9 and to Signal_Source 23.1 via N8; Terminal 26.1 via N8; Variable_Resistor 30.1 via N8; Diode 7.1 via N9.
- `15.1` (Meter): measurement or observation point [specificity=medium, confidence=0.78] Meter 15.1 is described as measurement or observation point. It is connected to nets N2, N7 and to Battery 2.1 via N2; Trim_Capacitor 29.1 via N7; Variable_Resistor 30.2 via N7.
- `15.2` (Meter): measurement or observation point [specificity=medium, confidence=0.78] Meter 15.2 is described as measurement or observation point. It is connected to nets N10, N11 and to Terminal 26.1 via N11; Variable_Resistor 30.2 via N10; Diode 7.1 via N10.
- `2.1` (Battery): power source [specificity=high, confidence=0.98] Battery 2.1 is described as power source. It is connected to nets N1, N2 and to Meter 15.1 via N2; Breaker 3.1 via N1.
- `23.1` (Signal_Source): generic circuit element [specificity=low, confidence=0.55] Signal_Source 23.1 is described as generic circuit element. It is connected to nets N3, N8 and to Inductor 10.1 via N8; Terminal 26.1 via N8; Breaker 3.1 via N3; Variable_Resistor 30.1 via N8.
- `26.1` (Terminal): external interface [specificity=medium, confidence=0.82] Terminal 26.1 is described as external interface. It is connected to nets N11, N8 and to Inductor 10.1 via N8; Meter 15.2 via N11; Signal_Source 23.1 via N8; Variable_Resistor 30.1 via N8.
- `29.1` (Trim_Capacitor): generic circuit element [specificity=low, confidence=0.55] Trim_Capacitor 29.1 is described as generic circuit element. It is connected to nets N6, N7 and to Meter 15.1 via N7; Variable_Resistor 30.1 via N6; Variable_Resistor 30.2 via N7.
- `3.1` (Breaker): generic circuit element [specificity=low, confidence=0.55] Breaker 3.1 is described as generic circuit element. It is connected to nets N1, N3 and to Battery 2.1 via N1; Signal_Source 23.1 via N3.
- `30.1` (Variable_Resistor): generic circuit element [specificity=low, confidence=0.55] Variable_Resistor 30.1 is described as generic circuit element. It is connected to nets N6, N8 and to Inductor 10.1 via N8; Signal_Source 23.1 via N8; Terminal 26.1 via N8; Trim_Capacitor 29.1 via N6.
- `30.2` (Variable_Resistor): generic circuit element [specificity=low, confidence=0.55] Variable_Resistor 30.2 is described as generic circuit element. It is connected to nets N10, N7 and to Meter 15.1 via N7; Meter 15.2 via N10; Trim_Capacitor 29.1 via N7; Diode 7.1 via N10.
- `7.1` (Diode): passive component [specificity=medium, confidence=0.76] Diode 7.1 is described as passive component. It is connected to nets N10, N9 and to Inductor 10.1 via N9; Meter 15.2 via N10; Variable_Resistor 30.2 via N10.

# Net Descriptions
- `N1`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N2`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N3`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N4`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N5`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N6`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N7`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N8`: shared internal branch [specificity=medium, confidence=0.70] Basis: The net behaves like a multi-device internal junction and its terminal semantics are mixed or widely shared.
- `N9`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N10`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N11`: external interface branch [specificity=low, confidence=0.68] Basis: The net reaches at least one explicit external interface.

# Aggregated Relations
- `N1`: N1 is a source connected branch connecting Battery 2.1 positive, Breaker 3.1 terminal t1.
- `N11`: N11 is a external interface branch connecting Meter 15.2 terminal t1, Terminal 26.1 terminal t2.
- `N2`: N2 is a source connected branch connecting Meter 15.1 terminal t1, Battery 2.1 negative.
- `N8`: N8 is a shared internal branch connecting Inductor 10.1 terminal t1, Signal_Source 23.1 terminal t2, Terminal 26.1 terminal t1, Variable_Resistor 30.1 terminal t1.
- `N10`: N10 is a local interconnect connecting Meter 15.2 terminal t2, Variable_Resistor 30.2 terminal t2, Diode 7.1 anode.
- `N3`: N3 is a local interconnect connecting Signal_Source 23.1 terminal t1, Breaker 3.1 terminal t2.
- `N6`: N6 is a local interconnect connecting Trim_Capacitor 29.1 terminal t1, Variable_Resistor 30.1 terminal t2.
- `N7`: N7 is a local interconnect connecting Meter 15.1 terminal t2, Trim_Capacitor 29.1 terminal t2, Variable_Resistor 30.2 terminal t1.

# Functional Paths
- `P1` `source_to_interface_path`: Source to interface path: Battery 2.1 -> N1 (source connected branch) -> Breaker 3.1 -> N3 (local interconnect) -> Signal_Source 23.1 -> N8 (shared internal branch) -> Terminal 26.1. Confidence: 0.78 (heuristic_inference).
- `P2` `interface_bridge_path`: Interface bridge path: N11 (external interface branch) -> Terminal 26.1 -> N8 (shared internal branch). Confidence: 0.84 (topological_fact).

# Structural Patterns
- `single_terminal_stub` on `N4`: Net N4 currently touches only Analog_Meter 0.1 terminal t1.
- `single_terminal_stub` on `N5`: Net N5 currently touches only Analog_Meter 0.1 terminal t2.

# Terminal Facts
- `0.1:t1`: Analog_Meter 0.1 terminal t1 is the only modeled terminal on net N4.
- `0.1:t2`: Analog_Meter 0.1 terminal t2 is the only modeled terminal on net N5.
- `10.1:t1`: Inductor 10.1 terminal t1 is connected on net N8 with Signal_Source 23.1, Terminal 26.1, Variable_Resistor 30.1.
- `10.1:t2`: Inductor 10.1 terminal t2 is connected on net N9 with Diode 7.1.
- `15.1:t1`: Meter 15.1 terminal t1 is connected on net N2 with Battery 2.1.
- `15.1:t2`: Meter 15.1 terminal t2 is connected on net N7 with Trim_Capacitor 29.1, Variable_Resistor 30.2.
- `15.2:t1`: Meter 15.2 terminal t1 is connected on net N11 with Terminal 26.1.
- `15.2:t2`: Meter 15.2 terminal t2 is connected on net N10 with Diode 7.1, Variable_Resistor 30.2.
- `2.1:positive`: Battery 2.1 terminal positive is connected on net N1 with Breaker 3.1.
- `2.1:negative`: Battery 2.1 terminal negative is connected on net N2 with Meter 15.1.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
