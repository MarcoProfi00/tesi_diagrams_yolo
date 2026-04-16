# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `17` (`17.png`) from pipeline variant `topology_v9.1_analog_meter_connector_transformer` was exported from `06_match_terminals_to_nets`.
The topology contains 8 components, 11 terminals, 8 nets, and 11 terminal-to-net connections.
Explicit power sources: Battery 2.1.
Explicit ground references: GND 9.1, GND 9.2, GND 9.3.

# Main Branches
- `N1` (single_terminal_stub, importance=low): Net N1 forms a single terminal stub connecting Battery 2.1.
- `N2` (single_terminal_stub, importance=low): Net N2 forms a single terminal stub connecting Battery 2.1.
- `N3` (single_terminal_stub, importance=low): Net N3 forms a single terminal stub connecting GND 9.1.
- `N5` (single_terminal_stub, importance=low): Net N5 forms a single terminal stub connecting Resistor 22.1.
- `N6` (single_terminal_stub, importance=low): Net N6 forms a single terminal stub connecting Capacitor 4.1.

# Component Descriptions
- `11.1` (Integrated_Circuit): generic circuit element [specificity=low, confidence=0.55] Integrated_Circuit 11.1 is described as generic circuit element. It is connected to nets none and to no other modeled components.
- `2.1` (Battery): power source [specificity=high, confidence=0.98] Battery 2.1 is described as power source. It is connected to nets N1, N2 and to no other modeled components.
- `22.1` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.1 is described as passive component. It is connected to nets N4, N5 and to Switch 25.1 via N4.
- `25.1` (Switch): active component [specificity=low, confidence=0.72] Switch 25.1 is described as active component. It is connected to nets N4, N8 and to Resistor 22.1 via N4; GND 9.3 via N8.
- `4.1` (Capacitor): passive component [specificity=medium, confidence=0.76] Capacitor 4.1 is described as passive component. It is connected to nets N6, N7 and to GND 9.2 via N7.
- `9.1` (GND): ground reference [specificity=high, confidence=1.00] GND 9.1 is described as ground reference. It is connected to nets N3 and to no other modeled components.
- `9.2` (GND): ground reference [specificity=high, confidence=1.00] GND 9.2 is described as ground reference. It is connected to nets N7 and to Capacitor 4.1 via N7.
- `9.3` (GND): ground reference [specificity=high, confidence=1.00] GND 9.3 is described as ground reference. It is connected to nets N8 and to Switch 25.1 via N8.

# Net Descriptions
- `N1`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N2`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N3`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N4`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N5`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N6`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N7`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N8`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.

# Aggregated Relations
- `N4`: N4 is a local interconnect connecting Resistor 22.1 terminal t1, Switch 25.1 terminal t1.
- `N7`: N7 is a ground return connecting Capacitor 4.1 terminal t2, GND 9.2 terminal t1.
- `N8`: N8 is a ground return connecting Switch 25.1 terminal t2, GND 9.3 terminal t1.

# Functional Paths
- `P1` `ground_to_device_path`: Ground to device path: GND 9.3 -> N8 (ground return) -> Switch 25.1. Confidence: 0.68 (heuristic_inference).

# Structural Patterns
- `single_terminal_stub` on `N1`: Net N1 currently touches only Battery 2.1 negative.
- `single_terminal_stub` on `N2`: Net N2 currently touches only Battery 2.1 positive.
- `single_terminal_stub` on `N3`: Net N3 currently touches only GND 9.1 terminal t1.
- `single_terminal_stub` on `N5`: Net N5 currently touches only Resistor 22.1 terminal t2.
- `single_terminal_stub` on `N6`: Net N6 currently touches only Capacitor 4.1 terminal t1.

# Terminal Facts
- `2.1:negative`: Battery 2.1 terminal negative is the only modeled terminal on net N1.
- `2.1:positive`: Battery 2.1 terminal positive is the only modeled terminal on net N2.
- `22.1:t1`: Resistor 22.1 terminal t1 is connected on net N4 with Switch 25.1.
- `22.1:t2`: Resistor 22.1 terminal t2 is the only modeled terminal on net N5.
- `25.1:t1`: Switch 25.1 terminal t1 is connected on net N4 with Resistor 22.1.
- `25.1:t2`: Switch 25.1 terminal t2 is connected on net N8 with GND 9.3.
- `4.1:t1`: Capacitor 4.1 terminal t1 is the only modeled terminal on net N6.
- `4.1:t2`: Capacitor 4.1 terminal t2 is connected on net N7 with GND 9.2.
- `9.1:t1`: GND 9.1 terminal t1 is the only modeled terminal on net N3.
- `9.2:t1`: GND 9.2 terminal t1 is connected on net N7 with Capacitor 4.1.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
