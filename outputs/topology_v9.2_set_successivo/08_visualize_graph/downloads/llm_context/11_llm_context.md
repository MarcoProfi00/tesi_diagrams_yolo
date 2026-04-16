# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `11` (`11.jpg`) from pipeline variant `topology_v9.2_set_successivo` was exported from `06_match_terminals_to_nets`.
The topology contains 14 components, 25 terminals, 10 nets, and 25 terminal-to-net connections.
Explicit ground references: GND 9.1, GND 9.2, GND 9.3, GND 9.4, GND 9.5.

# Main Branches
- `N5` (shared_internal_branch, importance=medium): Net N5 forms a shared internal branch connecting Inductor 10.1, Inductor 10.2, Resistor 22.1, Capacitor 4.1, Diode 7.1.
- `N1` (single_terminal_stub, importance=low): Net N1 forms a single terminal stub connecting Transformer 28.1.
- `N2` (single_terminal_stub, importance=low): Net N2 forms a single terminal stub connecting Transformer 28.1.
- `N7` (single_terminal_stub, importance=low): Net N7 forms a single terminal stub connecting Inductor 10.1, Inductor 10.3.

# Component Descriptions
- `10.1` (Inductor): passive component [specificity=medium, confidence=0.76] Inductor 10.1 is described as passive component. It is connected to nets N5, N7 and to Inductor 10.2 via N5; Inductor 10.3 via N7; Resistor 22.1 via N5; Capacitor 4.1 via N5; Diode 7.1 via N5.
- `10.2` (Inductor): passive component [specificity=medium, confidence=0.76] Inductor 10.2 is described as passive component. It is connected to nets N5, N9 and to Inductor 10.1 via N5; Inductor 10.3 via N9; Resistor 22.1 via N5; Capacitor 4.1 via N5; Capacitor 4.2 via N9; Capacitor 4.3 via N9; Diode 7.1 via N5; GND 9.4 via N9.
- `10.3` (Inductor): passive component [specificity=medium, confidence=0.76] Inductor 10.3 is described as passive component. It is connected to nets N7, N9 and to Inductor 10.1 via N7; Inductor 10.2 via N9; Capacitor 4.2 via N9; Capacitor 4.3 via N9; GND 9.4 via N9.
- `22.1` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.1 is described as passive component. It is connected to nets N4, N5 and to Inductor 10.1 via N5; Inductor 10.2 via N5; Transformer 28.1 via N4; Capacitor 4.1 via N4, N5; Diode 7.1 via N5.
- `28.1` (Transformer): generic circuit element [specificity=low, confidence=0.55] Transformer 28.1 is described as generic circuit element. It is connected to nets N1, N2, N3, N4 and to Resistor 22.1 via N4; Capacitor 4.1 via N4; GND 9.1 via N3.
- `4.1` (Capacitor): passive component [specificity=medium, confidence=0.76] Capacitor 4.1 is described as passive component. It is connected to nets N4, N5 and to Inductor 10.1 via N5; Inductor 10.2 via N5; Resistor 22.1 via N4, N5; Transformer 28.1 via N4; Diode 7.1 via N5.
- `4.2` (Capacitor): passive component [specificity=medium, confidence=0.76] Capacitor 4.2 is described as passive component. It is connected to nets N8, N9 and to Inductor 10.2 via N9; Inductor 10.3 via N9; Capacitor 4.3 via N9; GND 9.3 via N8; GND 9.4 via N9.
- `4.3` (Capacitor): passive component [specificity=medium, confidence=0.76] Capacitor 4.3 is described as passive component. It is connected to nets N10, N9 and to Inductor 10.2 via N9; Inductor 10.3 via N9; Capacitor 4.2 via N9; GND 9.4 via N9; GND 9.5 via N10.
- `7.1` (Diode): passive component [specificity=medium, confidence=0.76] Diode 7.1 is described as passive component. It is connected to nets N5, N6 and to Inductor 10.1 via N5; Inductor 10.2 via N5; Resistor 22.1 via N5; Capacitor 4.1 via N5; GND 9.2 via N6.
- `9.1` (GND): ground reference [specificity=high, confidence=1.00] GND 9.1 is described as ground reference. It is connected to nets N3 and to Transformer 28.1 via N3.
- `9.2` (GND): ground reference [specificity=high, confidence=1.00] GND 9.2 is described as ground reference. It is connected to nets N6 and to Diode 7.1 via N6.
- `9.3` (GND): ground reference [specificity=high, confidence=1.00] GND 9.3 is described as ground reference. It is connected to nets N8 and to Capacitor 4.2 via N8.
- `9.4` (GND): ground reference [specificity=high, confidence=1.00] GND 9.4 is described as ground reference. It is connected to nets N9 and to Inductor 10.2 via N9; Inductor 10.3 via N9; Capacitor 4.2 via N9; Capacitor 4.3 via N9.
- `9.5` (GND): ground reference [specificity=high, confidence=1.00] GND 9.5 is described as ground reference. It is connected to nets N10 and to Capacitor 4.3 via N10.

# Net Descriptions
- `N1`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N2`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N3`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N4`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N5`: shared internal branch [specificity=medium, confidence=0.70] Basis: The net behaves like a multi-device internal junction and its terminal semantics are mixed or widely shared.
- `N6`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N7`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N8`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N9`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N10`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.

# Aggregated Relations
- `N5`: N5 is a shared internal branch connecting Inductor 10.1 terminal t2, Inductor 10.2 terminal t1, Resistor 22.1 terminal t2, Capacitor 4.1 terminal t2, Diode 7.1 anode.
- `N9`: N9 is a ground return connecting Inductor 10.2 terminal t2, Inductor 10.3 terminal t2, Capacitor 4.2 terminal t1, Capacitor 4.3 terminal t1, GND 9.4 terminal t1.
- `N10`: N10 is a ground return connecting Capacitor 4.3 terminal t2, GND 9.5 terminal t1.
- `N3`: N3 is a ground return connecting Transformer 28.1 terminal t4, GND 9.1 terminal t1.
- `N4`: N4 is a local interconnect connecting Resistor 22.1 terminal t1, Transformer 28.1 terminal t2, Capacitor 4.1 terminal t1.
- `N6`: N6 is a ground return connecting Diode 7.1 cathode, GND 9.2 terminal t1.
- `N7`: N7 is a single terminal stub connecting Inductor 10.1 terminal t1, Inductor 10.3 terminal t1.
- `N8`: N8 is a ground return connecting Capacitor 4.2 terminal t2, GND 9.3 terminal t1.

# Functional Paths
- No functional path summary was produced from the current topology.

# Structural Patterns
- `high_degree_shared_branch` on `N5`: Net N5 is a shared internal branch touching 5 modeled components.
- `single_terminal_stub` on `N1`: Net N1 currently touches only Transformer 28.1 terminal t3.
- `single_terminal_stub` on `N2`: Net N2 currently touches only Transformer 28.1 terminal t1.
- `single_terminal_stub` on `N7`: Net N7 currently touches only Inductor 10.1 terminal t1.

# Terminal Facts
- `10.1:t1`: Inductor 10.1 terminal t1 is connected on net N7 with Inductor 10.3.
- `10.1:t2`: Inductor 10.1 terminal t2 is connected on net N5 with Capacitor 4.1, Diode 7.1, Inductor 10.2, Resistor 22.1.
- `10.2:t1`: Inductor 10.2 terminal t1 is connected on net N5 with Capacitor 4.1, Diode 7.1, Inductor 10.1, Resistor 22.1.
- `10.2:t2`: Inductor 10.2 terminal t2 is connected on net N9 with Capacitor 4.2, Capacitor 4.3, GND 9.4, Inductor 10.3.
- `10.3:t1`: Inductor 10.3 terminal t1 is connected on net N7 with Inductor 10.1.
- `10.3:t2`: Inductor 10.3 terminal t2 is connected on net N9 with Capacitor 4.2, Capacitor 4.3, GND 9.4, Inductor 10.2.
- `22.1:t1`: Resistor 22.1 terminal t1 is connected on net N4 with Capacitor 4.1, Transformer 28.1.
- `22.1:t2`: Resistor 22.1 terminal t2 is connected on net N5 with Capacitor 4.1, Diode 7.1, Inductor 10.1, Inductor 10.2.
- `28.1:t1`: Transformer 28.1 terminal t1 is the only modeled terminal on net N2.
- `28.1:t2`: Transformer 28.1 terminal t2 is connected on net N4 with Capacitor 4.1, Resistor 22.1.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
