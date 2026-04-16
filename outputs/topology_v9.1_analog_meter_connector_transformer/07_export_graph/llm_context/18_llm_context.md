# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `18` (`18.png`) from pipeline variant `topology_v9.1_analog_meter_connector_transformer` was exported from `06_match_terminals_to_nets`.
The topology contains 7 components, 9 terminals, 5 nets, and 8 terminal-to-net connections.
Explicit power sources: Battery 2.1.
Explicit ground references: GND 9.1, GND 9.2, GND 9.3.

# Main Branches
- `N2` (source_connected_branch, importance=high): Net N2 forms a source connected branch connecting Battery 2.1, Resistor 22.1.
- `N3` (single_terminal_stub, importance=low): Net N3 forms a single terminal stub connecting Resistor 22.1.
- `N4` (single_terminal_stub, importance=low): Net N4 forms a single terminal stub connecting GND 9.2.
- `N5` (single_terminal_stub, importance=low): Net N5 forms a single terminal stub connecting Analog_Meter 0.1, GND 9.3.

# Component Descriptions
- `0.1` (Analog_Meter): generic circuit element [specificity=low, confidence=0.55] Analog_Meter 0.1 is described as generic circuit element. It is connected to nets N5 and to GND 9.3 via N5.
- `11.1` (Integrated_Circuit): generic circuit element [specificity=low, confidence=0.55] Integrated_Circuit 11.1 is described as generic circuit element. It is connected to nets none and to no other modeled components.
- `2.1` (Battery): power source [specificity=high, confidence=0.98] Battery 2.1 is described as power source. It is connected to nets N1, N2 and to Resistor 22.1 via N2; GND 9.1 via N1.
- `22.1` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.1 is described as passive component. It is connected to nets N2, N3 and to Battery 2.1 via N2.
- `9.1` (GND): ground reference [specificity=high, confidence=1.00] GND 9.1 is described as ground reference. It is connected to nets N1 and to Battery 2.1 via N1.
- `9.2` (GND): ground reference [specificity=high, confidence=1.00] GND 9.2 is described as ground reference. It is connected to nets N4 and to no other modeled components.
- `9.3` (GND): ground reference [specificity=high, confidence=1.00] GND 9.3 is described as ground reference. It is connected to nets N5 and to Analog_Meter 0.1 via N5.

# Net Descriptions
- `N1`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N2`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N3`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N4`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N5`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.

# Aggregated Relations
- `N2`: N2 is a source connected branch connecting Battery 2.1 positive, Resistor 22.1 terminal t1.
- `N1`: N1 is a ground return connecting Battery 2.1 negative, GND 9.1 terminal t1.
- `N5`: N5 is a single terminal stub connecting Analog_Meter 0.1 terminal t2, GND 9.3 terminal t1.

# Functional Paths
- No functional path summary was produced from the current topology.

# Structural Patterns
- `single_terminal_stub` on `N3`: Net N3 currently touches only Resistor 22.1 terminal t2.
- `single_terminal_stub` on `N4`: Net N4 currently touches only GND 9.2 terminal t1.
- `single_terminal_stub` on `N5`: Net N5 currently touches only Analog_Meter 0.1 terminal t2.
- `suspicious_terminal_match` on `0.1:t1`: Analog_Meter 0.1 terminal t1 was flagged as a suspicious terminal-to-net match.
- `unmatched_terminal` on `0.1:t1`: Analog_Meter 0.1 terminal t1 is unmatched.

# Terminal Facts
- `0.1:t1`: Analog_Meter 0.1 terminal t1 is currently unmatched to any net.
- `0.1:t2`: Analog_Meter 0.1 terminal t2 is connected on net N5 with GND 9.3.
- `2.1:positive`: Battery 2.1 terminal positive is connected on net N2 with Resistor 22.1.
- `2.1:negative`: Battery 2.1 terminal negative is connected on net N1 with GND 9.1.
- `22.1:t1`: Resistor 22.1 terminal t1 is connected on net N2 with Battery 2.1.
- `22.1:t2`: Resistor 22.1 terminal t2 is the only modeled terminal on net N3.
- `9.1:t1`: GND 9.1 terminal t1 is connected on net N1 with Battery 2.1.
- `9.2:t1`: GND 9.2 terminal t1 is the only modeled terminal on net N4.
- `9.3:t1`: GND 9.3 terminal t1 is connected on net N5 with Analog_Meter 0.1.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
