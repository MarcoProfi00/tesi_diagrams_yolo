# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `26` (`26.png`) from pipeline variant `topology_v9.1_analog_meter_connector_transformer` was exported from `06_match_terminals_to_nets`.
The topology contains 6 components, 12 terminals, 6 nets, and 11 terminal-to-net connections.
Explicit ground references: GND 9.1, GND 9.2.

# Main Branches
- `N1` (single_terminal_stub, importance=low): Net N1 forms a single terminal stub connecting Signal_Source 23.1.
- `N5` (single_terminal_stub, importance=low): Net N5 forms a single terminal stub connecting Transformer 28.1.

# Component Descriptions
- `0.1` (Analog_Meter): generic circuit element [specificity=low, confidence=0.55] Analog_Meter 0.1 is described as generic circuit element. It is connected to nets N6 and to Resistor 22.1 via N6; GND 9.2 via N6.
- `22.1` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.1 is described as passive component. It is connected to nets N3, N6 and to Analog_Meter 0.1 via N6; GND 9.1 via N3; GND 9.2 via N6.
- `23.1` (Signal_Source): generic circuit element [specificity=low, confidence=0.55] Signal_Source 23.1 is described as generic circuit element. It is connected to nets N1, N2 and to Transformer 28.1 via N2.
- `28.1` (Transformer): generic circuit element [specificity=low, confidence=0.55] Transformer 28.1 is described as generic circuit element. It is connected to nets N2, N4, N5 and to Signal_Source 23.1 via N2.
- `9.1` (GND): ground reference [specificity=high, confidence=1.00] GND 9.1 is described as ground reference. It is connected to nets N3 and to Resistor 22.1 via N3.
- `9.2` (GND): ground reference [specificity=high, confidence=1.00] GND 9.2 is described as ground reference. It is connected to nets N6 and to Analog_Meter 0.1 via N6; Resistor 22.1 via N6.

# Net Descriptions
- `N1`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N2`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N3`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N4`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N5`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N6`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.

# Aggregated Relations
- `N2`: N2 is a local interconnect connecting Signal_Source 23.1 terminal t2, Transformer 28.1 terminal t3.
- `N3`: N3 is a ground return connecting Resistor 22.1 terminal t1, GND 9.1 terminal t1.
- `N6`: N6 is a ground return connecting Analog_Meter 0.1 terminal t2, Resistor 22.1 terminal t2, GND 9.2 terminal t1.

# Functional Paths
- No functional path summary was produced from the current topology.

# Structural Patterns
- `multiple_terminals_same_net` on `28.1`: Transformer 28.1 has terminals 28.1:t1, 28.1:t2 on the same net N4.
- `single_terminal_stub` on `N1`: Net N1 currently touches only Signal_Source 23.1 terminal t1.
- `single_terminal_stub` on `N5`: Net N5 currently touches only Transformer 28.1 terminal t4.
- `suspicious_terminal_match` on `0.1:t1`: Analog_Meter 0.1 terminal t1 was flagged as a suspicious terminal-to-net match.
- `unmatched_terminal` on `0.1:t1`: Analog_Meter 0.1 terminal t1 is unmatched.

# Terminal Facts
- `0.1:t1`: Analog_Meter 0.1 terminal t1 is currently unmatched to any net.
- `0.1:t2`: Analog_Meter 0.1 terminal t2 is connected on net N6 with GND 9.2, Resistor 22.1.
- `22.1:t1`: Resistor 22.1 terminal t1 is connected on net N3 with GND 9.1.
- `22.1:t2`: Resistor 22.1 terminal t2 is connected on net N6 with Analog_Meter 0.1, GND 9.2.
- `23.1:t1`: Signal_Source 23.1 terminal t1 is the only modeled terminal on net N1.
- `23.1:t2`: Signal_Source 23.1 terminal t2 is connected on net N2 with Transformer 28.1.
- `28.1:t1`: Transformer 28.1 terminal t1 is connected on net N4 with Transformer 28.1.
- `28.1:t2`: Transformer 28.1 terminal t2 is connected on net N4 with Transformer 28.1.
- `28.1:t3`: Transformer 28.1 terminal t3 is connected on net N2 with Signal_Source 23.1.
- `28.1:t4`: Transformer 28.1 terminal t4 is the only modeled terminal on net N5.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
