# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `22` (`22.png`) from pipeline variant `topology_v9.1_analog_meter_connector_transformer` was exported from `06_match_terminals_to_nets`.
The topology contains 9 components, 15 terminals, 10 nets, and 14 terminal-to-net connections.
Explicit power sources: Battery 2.1.
Explicit ground references: GND 9.1, GND 9.2, GND 9.3.

# Main Branches
- `N1` (single_terminal_stub, importance=low): Net N1 forms a single terminal stub connecting Battery 2.1.
- `N10` (single_terminal_stub, importance=low): Net N10 forms a single terminal stub connecting Analog_Meter 0.1, GND 9.3.
- `N2` (single_terminal_stub, importance=low): Net N2 forms a single terminal stub connecting Battery 2.1.
- `N3` (single_terminal_stub, importance=low): Net N3 forms a single terminal stub connecting GND 9.1.
- `N4` (single_terminal_stub, importance=low): Net N4 forms a single terminal stub connecting Transformer 28.1.
- `N5` (single_terminal_stub, importance=low): Net N5 forms a single terminal stub connecting Capacitor 4.1.

# Component Descriptions
- `0.1` (Analog_Meter): generic circuit element [specificity=low, confidence=0.55] Analog_Meter 0.1 is described as generic circuit element. It is connected to nets N10 and to GND 9.3 via N10.
- `11.1` (Integrated_Circuit): generic circuit element [specificity=low, confidence=0.55] Integrated_Circuit 11.1 is described as generic circuit element. It is connected to nets none and to no other modeled components.
- `2.1` (Battery): power source [specificity=high, confidence=0.98] Battery 2.1 is described as power source. It is connected to nets N1, N2 and to no other modeled components.
- `22.1` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.1 is described as passive component. It is connected to nets N8, N9 and to Capacitor 4.1 via N8; GND 9.2 via N9.
- `28.1` (Transformer): generic circuit element [specificity=low, confidence=0.55] Transformer 28.1 is described as generic circuit element. It is connected to nets N4, N6, N7 and to no other modeled components.
- `4.1` (Capacitor): passive component [specificity=medium, confidence=0.76] Capacitor 4.1 is described as passive component. It is connected to nets N5, N8 and to Resistor 22.1 via N8.
- `9.1` (GND): ground reference [specificity=high, confidence=1.00] GND 9.1 is described as ground reference. It is connected to nets N3 and to no other modeled components.
- `9.2` (GND): ground reference [specificity=high, confidence=1.00] GND 9.2 is described as ground reference. It is connected to nets N9 and to Resistor 22.1 via N9.
- `9.3` (GND): ground reference [specificity=high, confidence=1.00] GND 9.3 is described as ground reference. It is connected to nets N10 and to Analog_Meter 0.1 via N10.

# Net Descriptions
- `N1`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N2`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N3`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N4`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N5`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N6`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N7`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N8`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N9`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N10`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.

# Aggregated Relations
- `N10`: N10 is a single terminal stub connecting Analog_Meter 0.1 terminal t2, GND 9.3 terminal t1.
- `N8`: N8 is a local interconnect connecting Resistor 22.1 terminal t1, Capacitor 4.1 terminal t2.
- `N9`: N9 is a ground return connecting Resistor 22.1 terminal t2, GND 9.2 terminal t1.

# Functional Paths
- No functional path summary was produced from the current topology.

# Structural Patterns
- `multiple_terminals_same_net` on `28.1`: Transformer 28.1 has terminals 28.1:t1, 28.1:t2 on the same net N6.
- `single_terminal_stub` on `N1`: Net N1 currently touches only Battery 2.1 negative.
- `single_terminal_stub` on `N10`: Net N10 currently touches only Analog_Meter 0.1 terminal t2.
- `single_terminal_stub` on `N2`: Net N2 currently touches only Battery 2.1 positive.
- `single_terminal_stub` on `N3`: Net N3 currently touches only GND 9.1 terminal t1.
- `single_terminal_stub` on `N4`: Net N4 currently touches only Transformer 28.1 terminal t3.
- `single_terminal_stub` on `N5`: Net N5 currently touches only Capacitor 4.1 terminal t1.
- `single_terminal_stub` on `N7`: Net N7 currently touches only Transformer 28.1 terminal t4.
- `suspicious_terminal_match` on `0.1:t1`: Analog_Meter 0.1 terminal t1 was flagged as a suspicious terminal-to-net match.
- `unmatched_terminal` on `0.1:t1`: Analog_Meter 0.1 terminal t1 is unmatched.

# Terminal Facts
- `0.1:t1`: Analog_Meter 0.1 terminal t1 is currently unmatched to any net.
- `0.1:t2`: Analog_Meter 0.1 terminal t2 is connected on net N10 with GND 9.3.
- `2.1:negative`: Battery 2.1 terminal negative is the only modeled terminal on net N1.
- `2.1:positive`: Battery 2.1 terminal positive is the only modeled terminal on net N2.
- `22.1:t1`: Resistor 22.1 terminal t1 is connected on net N8 with Capacitor 4.1.
- `22.1:t2`: Resistor 22.1 terminal t2 is connected on net N9 with GND 9.2.
- `28.1:t1`: Transformer 28.1 terminal t1 is connected on net N6 with Transformer 28.1.
- `28.1:t2`: Transformer 28.1 terminal t2 is connected on net N6 with Transformer 28.1.
- `28.1:t3`: Transformer 28.1 terminal t3 is the only modeled terminal on net N4.
- `28.1:t4`: Transformer 28.1 terminal t4 is the only modeled terminal on net N7.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
