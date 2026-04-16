# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `12` (`12.jpg`) from pipeline variant `topology_v9.2_set_successivo` was exported from `06_match_terminals_to_nets`.
The topology contains 9 components, 16 terminals, 8 nets, and 16 terminal-to-net connections.
Explicit ground references: GND 9.1, GND 9.2.

# Main Branches
- `N7` (shared_internal_branch, importance=medium): Net N7 forms a shared internal branch connecting Resistor 22.1, Terminal 26.1, Capacitor 4.1, Diode 7.1, Diode 7.2.
- `N1` (single_terminal_stub, importance=low): Net N1 forms a single terminal stub connecting Transformer 28.1.
- `N2` (single_terminal_stub, importance=low): Net N2 forms a single terminal stub connecting Transformer 28.1.
- `N3` (single_terminal_stub, importance=low): Net N3 forms a single terminal stub connecting Transformer 28.1.
- `N4` (single_terminal_stub, importance=low): Net N4 forms a single terminal stub connecting GND 9.1.
- `N6` (single_terminal_stub, importance=low): Net N6 forms a single terminal stub connecting Diode 7.2.

# Component Descriptions
- `22.1` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.1 is described as passive component. It is connected to nets N7, N8 and to Terminal 26.1 via N7; Terminal 26.2 via N8; Capacitor 4.1 via N7, N8; Diode 7.1 via N7; Diode 7.2 via N7; GND 9.2 via N8.
- `26.1` (Terminal): external interface [specificity=low, confidence=0.68] Terminal 26.1 is described as external interface. It is connected to nets N7 and to Resistor 22.1 via N7; Capacitor 4.1 via N7; Diode 7.1 via N7; Diode 7.2 via N7.
- `26.2` (Terminal): external interface [specificity=low, confidence=0.68] Terminal 26.2 is described as external interface. It is connected to nets N8 and to Resistor 22.1 via N8; Capacitor 4.1 via N8; GND 9.2 via N8.
- `28.1` (Transformer): generic circuit element [specificity=low, confidence=0.55] Transformer 28.1 is described as generic circuit element. It is connected to nets N1, N2, N3, N5 and to Diode 7.1 via N5.
- `4.1` (Capacitor): passive component [specificity=medium, confidence=0.76] Capacitor 4.1 is described as passive component. It is connected to nets N7, N8 and to Resistor 22.1 via N7, N8; Terminal 26.1 via N7; Terminal 26.2 via N8; Diode 7.1 via N7; Diode 7.2 via N7; GND 9.2 via N8.
- `7.1` (Diode): passive component [specificity=medium, confidence=0.76] Diode 7.1 is described as passive component. It is connected to nets N5, N7 and to Resistor 22.1 via N7; Terminal 26.1 via N7; Transformer 28.1 via N5; Capacitor 4.1 via N7; Diode 7.2 via N7.
- `7.2` (Diode): passive component [specificity=medium, confidence=0.76] Diode 7.2 is described as passive component. It is connected to nets N6, N7 and to Resistor 22.1 via N7; Terminal 26.1 via N7; Capacitor 4.1 via N7; Diode 7.1 via N7.
- `9.1` (GND): ground reference [specificity=high, confidence=1.00] GND 9.1 is described as ground reference. It is connected to nets N4 and to no other modeled components.
- `9.2` (GND): ground reference [specificity=high, confidence=1.00] GND 9.2 is described as ground reference. It is connected to nets N8 and to Resistor 22.1 via N8; Terminal 26.2 via N8; Capacitor 4.1 via N8.

# Net Descriptions
- `N1`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N2`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N3`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N4`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N5`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N6`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N7`: shared internal branch [specificity=medium, confidence=0.70] Basis: The net behaves like a multi-device internal junction and its terminal semantics are mixed or widely shared.
- `N8`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.

# Aggregated Relations
- `N7`: N7 is a shared internal branch connecting Resistor 22.1 terminal t1, Terminal 26.1 terminal t1, Capacitor 4.1 terminal t1, Diode 7.1 cathode, Diode 7.2 cathode.
- `N8`: N8 is a ground return connecting Resistor 22.1 terminal t2, Terminal 26.2 terminal t1, Capacitor 4.1 terminal t2, GND 9.2 terminal t1.
- `N5`: N5 is a local interconnect connecting Transformer 28.1 terminal t4, Diode 7.1 anode.

# Functional Paths
- No functional path summary was produced from the current topology.

# Structural Patterns
- `high_degree_shared_branch` on `N7`: Net N7 is a shared internal branch touching 5 modeled components.
- `single_terminal_stub` on `N1`: Net N1 currently touches only Transformer 28.1 terminal t3.
- `single_terminal_stub` on `N2`: Net N2 currently touches only Transformer 28.1 terminal t1.
- `single_terminal_stub` on `N3`: Net N3 currently touches only Transformer 28.1 terminal t2.
- `single_terminal_stub` on `N4`: Net N4 currently touches only GND 9.1 terminal t1.
- `single_terminal_stub` on `N6`: Net N6 currently touches only Diode 7.2 anode.

# Terminal Facts
- `22.1:t1`: Resistor 22.1 terminal t1 is connected on net N7 with Capacitor 4.1, Diode 7.1, Diode 7.2, Terminal 26.1.
- `22.1:t2`: Resistor 22.1 terminal t2 is connected on net N8 with Capacitor 4.1, GND 9.2, Terminal 26.2.
- `26.1:t1`: Terminal 26.1 terminal t1 is connected on net N7 with Capacitor 4.1, Diode 7.1, Diode 7.2, Resistor 22.1.
- `26.2:t1`: Terminal 26.2 terminal t1 is connected on net N8 with Capacitor 4.1, GND 9.2, Resistor 22.1.
- `28.1:t1`: Transformer 28.1 terminal t1 is the only modeled terminal on net N2.
- `28.1:t2`: Transformer 28.1 terminal t2 is the only modeled terminal on net N3.
- `28.1:t3`: Transformer 28.1 terminal t3 is the only modeled terminal on net N1.
- `28.1:t4`: Transformer 28.1 terminal t4 is connected on net N5 with Diode 7.1.
- `4.1:t1`: Capacitor 4.1 terminal t1 is connected on net N7 with Diode 7.1, Diode 7.2, Resistor 22.1, Terminal 26.1.
- `4.1:t2`: Capacitor 4.1 terminal t2 is connected on net N8 with GND 9.2, Resistor 22.1, Terminal 26.2.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
