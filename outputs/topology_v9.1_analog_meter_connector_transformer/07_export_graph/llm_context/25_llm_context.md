# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `25` (`25.png`) from pipeline variant `topology_v9.1_analog_meter_connector_transformer` was exported from `06_match_terminals_to_nets`.
The topology contains 7 components, 12 terminals, 6 nets, and 12 terminal-to-net connections.
Explicit ground references: GND 9.1, GND 9.2.

# Main Branches
- `N1` (single_terminal_stub, importance=low): Net N1 forms a single terminal stub connecting Meter 15.1.

# Component Descriptions
- `13.1` (Lamp): generic circuit element [specificity=low, confidence=0.55] Lamp 13.1 is described as generic circuit element. It is connected to nets N5, N6 and to Resistor 22.1 via N5; Capacitor 4.1 via N5; GND 9.2 via N6.
- `15.1` (Meter): measurement or observation point [specificity=medium, confidence=0.78] Meter 15.1 is described as measurement or observation point. It is connected to nets N1, N2 and to Transformer 28.1 via N2.
- `22.1` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.1 is described as passive component. It is connected to nets N4, N5 and to Lamp 13.1 via N5; Transformer 28.1 via N4; Capacitor 4.1 via N5.
- `28.1` (Transformer): generic circuit element [specificity=low, confidence=0.55] Transformer 28.1 is described as generic circuit element. It is connected to nets N2, N4 and to Meter 15.1 via N2; Resistor 22.1 via N4.
- `4.1` (Capacitor): passive component [specificity=medium, confidence=0.76] Capacitor 4.1 is described as passive component. It is connected to nets N3, N5 and to Lamp 13.1 via N5; Resistor 22.1 via N5; GND 9.1 via N3.
- `9.1` (GND): ground reference [specificity=high, confidence=1.00] GND 9.1 is described as ground reference. It is connected to nets N3 and to Capacitor 4.1 via N3.
- `9.2` (GND): ground reference [specificity=high, confidence=1.00] GND 9.2 is described as ground reference. It is connected to nets N6 and to Lamp 13.1 via N6.

# Net Descriptions
- `N1`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N2`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N3`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N4`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N5`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N6`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.

# Aggregated Relations
- `N2`: N2 is a local interconnect connecting Meter 15.1 terminal t2, Transformer 28.1 terminal t1.
- `N3`: N3 is a ground return connecting Capacitor 4.1 terminal t1, GND 9.1 terminal t1.
- `N4`: N4 is a local interconnect connecting Resistor 22.1 terminal t1, Transformer 28.1 terminal t2.
- `N5`: N5 is a local interconnect connecting Lamp 13.1 terminal t1, Resistor 22.1 terminal t2, Capacitor 4.1 terminal t2.
- `N6`: N6 is a ground return connecting Lamp 13.1 terminal t2, GND 9.2 terminal t1.

# Functional Paths
- No functional path summary was produced from the current topology.

# Structural Patterns
- `single_terminal_stub` on `N1`: Net N1 currently touches only Meter 15.1 terminal t1.

# Terminal Facts
- `13.1:t1`: Lamp 13.1 terminal t1 is connected on net N5 with Capacitor 4.1, Resistor 22.1.
- `13.1:t2`: Lamp 13.1 terminal t2 is connected on net N6 with GND 9.2.
- `15.1:t1`: Meter 15.1 terminal t1 is the only modeled terminal on net N1.
- `15.1:t2`: Meter 15.1 terminal t2 is connected on net N2 with Transformer 28.1.
- `22.1:t1`: Resistor 22.1 terminal t1 is connected on net N4 with Transformer 28.1.
- `22.1:t2`: Resistor 22.1 terminal t2 is connected on net N5 with Capacitor 4.1, Lamp 13.1.
- `28.1:t1`: Transformer 28.1 terminal t1 is connected on net N2 with Meter 15.1.
- `28.1:t2`: Transformer 28.1 terminal t2 is connected on net N4 with Resistor 22.1.
- `4.1:t1`: Capacitor 4.1 terminal t1 is connected on net N3 with GND 9.1.
- `4.1:t2`: Capacitor 4.1 terminal t2 is connected on net N5 with Lamp 13.1, Resistor 22.1.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
