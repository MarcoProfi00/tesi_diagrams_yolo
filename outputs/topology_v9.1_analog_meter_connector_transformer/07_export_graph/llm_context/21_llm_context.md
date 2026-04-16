# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `21` (`21.png`) from pipeline variant `topology_v9.1_analog_meter_connector_transformer` was exported from `06_match_terminals_to_nets`.
The topology contains 9 components, 19 terminals, 10 nets, and 19 terminal-to-net connections.
Explicit power sources: Battery 2.1.
Explicit ground references: GND 9.1, GND 9.2, GND 9.3.

# Main Branches
- `N2` (source_connected_branch, importance=high): Net N2 forms a source connected branch connecting Battery 2.1, Connector 5.1.
- `N1` (single_terminal_stub, importance=low): Net N1 forms a single terminal stub connecting Battery 2.1.
- `N10` (single_terminal_stub, importance=low): Net N10 forms a single terminal stub connecting Analog_Meter 0.1, GND 9.3.
- `N9` (single_terminal_stub, importance=low): Net N9 forms a single terminal stub connecting Analog_Meter 0.1, Resistor 22.1.

# Component Descriptions
- `0.1` (Analog_Meter): generic circuit element [specificity=low, confidence=0.55] Analog_Meter 0.1 is described as generic circuit element. It is connected to nets N10, N9 and to Resistor 22.1 via N9; GND 9.3 via N10.
- `2.1` (Battery): power source [specificity=high, confidence=0.98] Battery 2.1 is described as power source. It is connected to nets N1, N2 and to Connector 5.1 via N2.
- `22.1` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.1 is described as passive component. It is connected to nets N8, N9 and to Analog_Meter 0.1 via N9; Transformer 28.1 via N8.
- `28.1` (Transformer): generic circuit element [specificity=low, confidence=0.55] Transformer 28.1 is described as generic circuit element. It is connected to nets N4, N7, N8 and to Resistor 22.1 via N8; Connector 5.1 via N4.
- `4.1` (Capacitor): passive component [specificity=medium, confidence=0.76] Capacitor 4.1 is described as passive component. It is connected to nets N5, N6 and to Connector 5.1 via N5; GND 9.2 via N6.
- `5.1` (Connector): generic circuit element [specificity=low, confidence=0.55] Connector 5.1 is described as generic circuit element. It is connected to nets N2, N3, N4, N5 and to Battery 2.1 via N2; Transformer 28.1 via N4; Capacitor 4.1 via N5; GND 9.1 via N3.
- `9.1` (GND): ground reference [specificity=high, confidence=1.00] GND 9.1 is described as ground reference. It is connected to nets N3 and to Connector 5.1 via N3.
- `9.2` (GND): ground reference [specificity=high, confidence=1.00] GND 9.2 is described as ground reference. It is connected to nets N6 and to Capacitor 4.1 via N6.
- `9.3` (GND): ground reference [specificity=high, confidence=1.00] GND 9.3 is described as ground reference. It is connected to nets N10 and to Analog_Meter 0.1 via N10.

# Net Descriptions
- `N1`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N2`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N3`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N4`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N5`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N6`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N7`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N8`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N9`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N10`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.

# Aggregated Relations
- `N2`: N2 is a source connected branch connecting Battery 2.1 positive, Connector 5.1 pin1.
- `N10`: N10 is a single terminal stub connecting Analog_Meter 0.1 terminal t2, GND 9.3 terminal t1.
- `N3`: N3 is a ground return connecting Connector 5.1 pin4, GND 9.1 terminal t1.
- `N4`: N4 is a local interconnect connecting Transformer 28.1 terminal t3, Connector 5.1 pin2.
- `N5`: N5 is a local interconnect connecting Capacitor 4.1 terminal t1, Connector 5.1 pin3.
- `N6`: N6 is a ground return connecting Capacitor 4.1 terminal t2, GND 9.2 terminal t1.
- `N8`: N8 is a local interconnect connecting Resistor 22.1 terminal t1, Transformer 28.1 terminal t4.
- `N9`: N9 is a single terminal stub connecting Analog_Meter 0.1 terminal t1, Resistor 22.1 terminal t2.

# Functional Paths
- No functional path summary was produced from the current topology.

# Structural Patterns
- `multiple_terminals_same_net` on `28.1`: Transformer 28.1 has terminals 28.1:t1, 28.1:t2 on the same net N7.
- `single_terminal_stub` on `N1`: Net N1 currently touches only Battery 2.1 negative.
- `single_terminal_stub` on `N10`: Net N10 currently touches only GND 9.3 terminal t1.
- `single_terminal_stub` on `N9`: Net N9 currently touches only Resistor 22.1 terminal t2.

# Terminal Facts
- `0.1:t1`: Analog_Meter 0.1 terminal t1 is connected on net N9 with Resistor 22.1.
- `0.1:t2`: Analog_Meter 0.1 terminal t2 is connected on net N10 with GND 9.3.
- `2.1:negative`: Battery 2.1 terminal negative is the only modeled terminal on net N1.
- `2.1:positive`: Battery 2.1 terminal positive is connected on net N2 with Connector 5.1.
- `22.1:t1`: Resistor 22.1 terminal t1 is connected on net N8 with Transformer 28.1.
- `22.1:t2`: Resistor 22.1 terminal t2 is connected on net N9 with Analog_Meter 0.1.
- `28.1:t1`: Transformer 28.1 terminal t1 is connected on net N7 with Transformer 28.1.
- `28.1:t2`: Transformer 28.1 terminal t2 is connected on net N7 with Transformer 28.1.
- `28.1:t3`: Transformer 28.1 terminal t3 is connected on net N4 with Connector 5.1.
- `28.1:t4`: Transformer 28.1 terminal t4 is connected on net N8 with Resistor 22.1.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
