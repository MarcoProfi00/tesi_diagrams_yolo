# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `8` (`8.jpg`) from pipeline variant `topology_v9.2_set_successivo` was exported from `06_match_terminals_to_nets`.
The topology contains 9 components, 15 terminals, 6 nets, and 15 terminal-to-net connections.
Explicit ground references: GND 9.1.

# Main Branches
- `N1` (external_interface_branch, importance=high): Net N1 forms an external interface branch connecting Polarized_Capacitor 20.1, Terminal 26.2.
- `N5` (external_interface_branch, importance=high): Net N5 forms an external interface branch connecting Terminal 26.4, Transformer 28.1.
- `N6` (external_interface_branch, importance=high): Net N6 forms an external interface branch connecting Terminal 26.3, Transformer 28.1.

# Component Descriptions
- `10.1` (Inductor): passive component [specificity=medium, confidence=0.76] Inductor 10.1 is described as passive component. It is connected to nets N2, N4 and to Polarized_Capacitor 20.1 via N2; Polarized_Capacitor 20.2 via N2; Transformer 28.1 via N4.
- `20.1` (Polarized_Capacitor): generic circuit element [specificity=low, confidence=0.55] Polarized_Capacitor 20.1 is described as generic circuit element. It is connected to nets N1, N2 and to Inductor 10.1 via N2; Polarized_Capacitor 20.2 via N2; Terminal 26.2 via N1.
- `20.2` (Polarized_Capacitor): generic circuit element [specificity=low, confidence=0.55] Polarized_Capacitor 20.2 is described as generic circuit element. It is connected to nets N2, N3 and to Inductor 10.1 via N2; Polarized_Capacitor 20.1 via N2; Terminal 26.1 via N3; Transformer 28.1 via N3; GND 9.1 via N3.
- `26.1` (Terminal): external interface [specificity=low, confidence=0.68] Terminal 26.1 is described as external interface. It is connected to nets N3 and to Polarized_Capacitor 20.2 via N3; Transformer 28.1 via N3; GND 9.1 via N3.
- `26.2` (Terminal): external interface [specificity=low, confidence=0.68] Terminal 26.2 is described as external interface. It is connected to nets N1 and to Polarized_Capacitor 20.1 via N1.
- `26.3` (Terminal): external interface [specificity=low, confidence=0.68] Terminal 26.3 is described as external interface. It is connected to nets N6 and to Transformer 28.1 via N6.
- `26.4` (Terminal): external interface [specificity=low, confidence=0.68] Terminal 26.4 is described as external interface. It is connected to nets N5 and to Transformer 28.1 via N5.
- `28.1` (Transformer): generic circuit element [specificity=low, confidence=0.55] Transformer 28.1 is described as generic circuit element. It is connected to nets N3, N4, N5, N6 and to Inductor 10.1 via N4; Polarized_Capacitor 20.2 via N3; Terminal 26.1 via N3; Terminal 26.3 via N6; Terminal 26.4 via N5; GND 9.1 via N3.
- `9.1` (GND): ground reference [specificity=high, confidence=1.00] GND 9.1 is described as ground reference. It is connected to nets N3 and to Polarized_Capacitor 20.2 via N3; Terminal 26.1 via N3; Transformer 28.1 via N3.

# Net Descriptions
- `N1`: external interface branch [specificity=low, confidence=0.68] Basis: The net reaches at least one explicit external interface.
- `N2`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N3`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N4`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N5`: external interface branch [specificity=low, confidence=0.68] Basis: The net reaches at least one explicit external interface.
- `N6`: external interface branch [specificity=low, confidence=0.68] Basis: The net reaches at least one explicit external interface.

# Aggregated Relations
- `N1`: N1 is a external interface branch connecting Polarized_Capacitor 20.1 positive, Terminal 26.2 terminal t1.
- `N5`: N5 is a external interface branch connecting Terminal 26.4 terminal t1, Transformer 28.1 terminal t4.
- `N6`: N6 is a external interface branch connecting Terminal 26.3 terminal t1, Transformer 28.1 terminal t2.
- `N3`: N3 is a ground return connecting Polarized_Capacitor 20.2 negative, Terminal 26.1 terminal t1, Transformer 28.1 terminal t3, GND 9.1 terminal t1.
- `N2`: N2 is a local interconnect connecting Inductor 10.1 terminal t1, Polarized_Capacitor 20.1 negative, Polarized_Capacitor 20.2 positive.
- `N4`: N4 is a local interconnect connecting Inductor 10.1 terminal t2, Transformer 28.1 terminal t1.

# Functional Paths
- No functional path summary was produced from the current topology.

# Structural Patterns
- No structural pattern was recorded from the current topology.

# Terminal Facts
- `10.1:t1`: Inductor 10.1 terminal t1 is connected on net N2 with Polarized_Capacitor 20.1, Polarized_Capacitor 20.2.
- `10.1:t2`: Inductor 10.1 terminal t2 is connected on net N4 with Transformer 28.1.
- `20.1:positive`: Polarized_Capacitor 20.1 terminal positive is connected on net N1 with Terminal 26.2.
- `20.1:negative`: Polarized_Capacitor 20.1 terminal negative is connected on net N2 with Inductor 10.1, Polarized_Capacitor 20.2.
- `20.2:positive`: Polarized_Capacitor 20.2 terminal positive is connected on net N2 with Inductor 10.1, Polarized_Capacitor 20.1.
- `20.2:negative`: Polarized_Capacitor 20.2 terminal negative is connected on net N3 with GND 9.1, Terminal 26.1, Transformer 28.1.
- `26.1:t1`: Terminal 26.1 terminal t1 is connected on net N3 with GND 9.1, Polarized_Capacitor 20.2, Transformer 28.1.
- `26.2:t1`: Terminal 26.2 terminal t1 is connected on net N1 with Polarized_Capacitor 20.1.
- `26.3:t1`: Terminal 26.3 terminal t1 is connected on net N6 with Transformer 28.1.
- `26.4:t1`: Terminal 26.4 terminal t1 is connected on net N5 with Transformer 28.1.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
