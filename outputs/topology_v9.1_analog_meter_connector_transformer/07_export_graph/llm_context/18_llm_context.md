# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `18` (`18.png`) from pipeline variant `topology_v9.1_analog_meter_connector_transformer` was exported from `06_match_terminals_to_nets`.
The topology contains 7 components, 12 terminals, 6 nets, and 11 terminal-to-net connections.
Explicit power sources: Battery 2.1.
Explicit ground references: GND 9.1, GND 9.2, GND 9.3.

# Main Branches
- `N2` (source_connected_branch, importance=high): Net N2 forms a source connected branch connecting Battery 2.1, Resistor 22.1.
- `N5` (single_terminal_stub, importance=low): Net N5 forms a single terminal stub connecting Connector 5.1.
- `N6` (single_terminal_stub, importance=low): Net N6 forms a single terminal stub connecting Analog_Meter 0.1, GND 9.3.

# Component Descriptions
- `0.1` (Analog_Meter): generic circuit element [specificity=low, confidence=0.55] Analog_Meter 0.1 is described as generic circuit element. It is connected to nets N6 and to GND 9.3 via N6.
- `2.1` (Battery): power source [specificity=high, confidence=0.98] Battery 2.1 is described as power source. It is connected to nets N1, N2 and to Resistor 22.1 via N2; GND 9.1 via N1.
- `22.1` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.1 is described as passive component. It is connected to nets N2, N3 and to Battery 2.1 via N2; Connector 5.1 via N3.
- `5.1` (Connector): generic circuit element [specificity=low, confidence=0.55] Connector 5.1 is described as generic circuit element. It is connected to nets N3, N4, N5 and to Resistor 22.1 via N3; GND 9.2 via N4.
- `9.1` (GND): ground reference [specificity=high, confidence=1.00] GND 9.1 is described as ground reference. It is connected to nets N1 and to Battery 2.1 via N1.
- `9.2` (GND): ground reference [specificity=high, confidence=1.00] GND 9.2 is described as ground reference. It is connected to nets N4 and to Connector 5.1 via N4.
- `9.3` (GND): ground reference [specificity=high, confidence=1.00] GND 9.3 is described as ground reference. It is connected to nets N6 and to Analog_Meter 0.1 via N6.

# Net Descriptions
- `N1`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N2`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N3`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N4`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N5`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N6`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.

# Aggregated Relations
- `N2`: N2 is a source connected branch connecting Battery 2.1 positive, Resistor 22.1 terminal t1.
- `N1`: N1 is a ground return connecting Battery 2.1 negative, GND 9.1 terminal t1.
- `N3`: N3 is a local interconnect connecting Resistor 22.1 terminal t2, Connector 5.1 pin2.
- `N4`: N4 is a ground return connecting Connector 5.1 pin3, GND 9.2 terminal t1.
- `N6`: N6 is a single terminal stub connecting Analog_Meter 0.1 terminal t2, GND 9.3 terminal t1.

# Functional Paths
- No functional path summary was produced from the current topology.

# Structural Patterns
- `single_terminal_stub` on `N5`: Net N5 currently touches only Connector 5.1 pin1.
- `single_terminal_stub` on `N6`: Net N6 currently touches only Analog_Meter 0.1 terminal t2.
- `suspicious_terminal_match` on `0.1:t1`: Analog_Meter 0.1 terminal t1 was flagged as a suspicious terminal-to-net match.
- `unmatched_terminal` on `0.1:t1`: Analog_Meter 0.1 terminal t1 is unmatched.

# Terminal Facts
- `0.1:t1`: Analog_Meter 0.1 terminal t1 is currently unmatched to any net.
- `0.1:t2`: Analog_Meter 0.1 terminal t2 is connected on net N6 with GND 9.3.
- `2.1:positive`: Battery 2.1 terminal positive is connected on net N2 with Resistor 22.1.
- `2.1:negative`: Battery 2.1 terminal negative is connected on net N1 with GND 9.1.
- `22.1:t1`: Resistor 22.1 terminal t1 is connected on net N2 with Battery 2.1.
- `22.1:t2`: Resistor 22.1 terminal t2 is connected on net N3 with Connector 5.1.
- `5.1:pin1`: Connector 5.1 terminal pin1 is the only modeled terminal on net N5.
- `5.1:pin2`: Connector 5.1 terminal pin2 is connected on net N3 with Resistor 22.1.
- `5.1:pin3`: Connector 5.1 terminal pin3 is connected on net N4 with GND 9.2.
- `9.1:t1`: GND 9.1 terminal t1 is connected on net N1 with Battery 2.1.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
