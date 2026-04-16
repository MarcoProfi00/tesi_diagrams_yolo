# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `9` (`9.jpg`) from pipeline variant `topology_v9.2_set_successivo` was exported from `06_match_terminals_to_nets`.
The topology contains 9 components, 20 terminals, 9 nets, and 20 terminal-to-net connections.

# Main Branches
- `N5` (shared_internal_branch, importance=medium): Net N5 forms a shared internal branch connecting Inductor 10.2, Resistor 22.2, Resistor 22.3, Transformer 28.1.
- `N6` (shared_internal_branch, importance=medium): Net N6 forms a shared internal branch connecting Inductor 10.2, Inductor 10.4, Resistor 22.2, Transformer 28.1.
- `N1` (single_terminal_stub, importance=low): Net N1 forms a single terminal stub connecting Resistor 22.1.
- `N3` (single_terminal_stub, importance=low): Net N3 forms a single terminal stub connecting Transformer 28.1.

# Component Descriptions
- `10.1` (Inductor): passive component [specificity=medium, confidence=0.76] Inductor 10.1 is described as passive component. It is connected to nets N2, N4 and to Resistor 22.1 via N2; Transformer 28.1 via N4.
- `10.2` (Inductor): passive component [specificity=medium, confidence=0.76] Inductor 10.2 is described as passive component. It is connected to nets N5, N6 and to Inductor 10.4 via N6; Resistor 22.2 via N5, N6; Resistor 22.3 via N5; Transformer 28.1 via N5, N6.
- `10.3` (Inductor): passive component [specificity=medium, confidence=0.76] Inductor 10.3 is described as passive component. It is connected to nets N7, N8 and to Resistor 22.3 via N7; Resistor 22.4 via N8.
- `10.4` (Inductor): passive component [specificity=medium, confidence=0.76] Inductor 10.4 is described as passive component. It is connected to nets N6, N9 and to Inductor 10.2 via N6; Resistor 22.2 via N6; Resistor 22.4 via N9; Transformer 28.1 via N6.
- `22.1` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.1 is described as passive component. It is connected to nets N1, N2 and to Inductor 10.1 via N2.
- `22.2` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.2 is described as passive component. It is connected to nets N5, N6 and to Inductor 10.2 via N5, N6; Inductor 10.4 via N6; Resistor 22.3 via N5; Transformer 28.1 via N5, N6.
- `22.3` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.3 is described as passive component. It is connected to nets N5, N7 and to Inductor 10.2 via N5; Inductor 10.3 via N7; Resistor 22.2 via N5; Transformer 28.1 via N5.
- `22.4` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.4 is described as passive component. It is connected to nets N8, N9 and to Inductor 10.3 via N8; Inductor 10.4 via N9.
- `28.1` (Transformer): generic circuit element [specificity=low, confidence=0.55] Transformer 28.1 is described as generic circuit element. It is connected to nets N3, N4, N5, N6 and to Inductor 10.1 via N4; Inductor 10.2 via N5, N6; Inductor 10.4 via N6; Resistor 22.2 via N5, N6; Resistor 22.3 via N5.

# Net Descriptions
- `N1`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N2`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N3`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N4`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N5`: shared internal branch [specificity=medium, confidence=0.70] Basis: The net behaves like a multi-device internal junction and its terminal semantics are mixed or widely shared.
- `N6`: shared internal branch [specificity=medium, confidence=0.70] Basis: The net behaves like a multi-device internal junction and its terminal semantics are mixed or widely shared.
- `N7`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N8`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N9`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.

# Aggregated Relations
- `N5`: N5 is a shared internal branch connecting Inductor 10.2 terminal t1, Resistor 22.2 terminal t1, Resistor 22.3 terminal t1, Transformer 28.1 terminal t2.
- `N6`: N6 is a shared internal branch connecting Inductor 10.2 terminal t2, Inductor 10.4 terminal t2, Resistor 22.2 terminal t2, Transformer 28.1 terminal t4.
- `N2`: N2 is a local interconnect connecting Inductor 10.1 terminal t1, Resistor 22.1 terminal t2.
- `N4`: N4 is a local interconnect connecting Inductor 10.1 terminal t2, Transformer 28.1 terminal t1.
- `N7`: N7 is a local interconnect connecting Inductor 10.3 terminal t1, Resistor 22.3 terminal t2.
- `N8`: N8 is a local interconnect connecting Inductor 10.3 terminal t2, Resistor 22.4 terminal t1.
- `N9`: N9 is a local interconnect connecting Inductor 10.4 terminal t1, Resistor 22.4 terminal t2.

# Functional Paths
- No functional path summary was produced from the current topology.

# Structural Patterns
- `single_terminal_stub` on `N1`: Net N1 currently touches only Resistor 22.1 terminal t1.
- `single_terminal_stub` on `N3`: Net N3 currently touches only Transformer 28.1 terminal t3.

# Terminal Facts
- `10.1:t1`: Inductor 10.1 terminal t1 is connected on net N2 with Resistor 22.1.
- `10.1:t2`: Inductor 10.1 terminal t2 is connected on net N4 with Transformer 28.1.
- `10.2:t1`: Inductor 10.2 terminal t1 is connected on net N5 with Resistor 22.2, Resistor 22.3, Transformer 28.1.
- `10.2:t2`: Inductor 10.2 terminal t2 is connected on net N6 with Inductor 10.4, Resistor 22.2, Transformer 28.1.
- `10.3:t1`: Inductor 10.3 terminal t1 is connected on net N7 with Resistor 22.3.
- `10.3:t2`: Inductor 10.3 terminal t2 is connected on net N8 with Resistor 22.4.
- `10.4:t1`: Inductor 10.4 terminal t1 is connected on net N9 with Resistor 22.4.
- `10.4:t2`: Inductor 10.4 terminal t2 is connected on net N6 with Inductor 10.2, Resistor 22.2, Transformer 28.1.
- `22.1:t1`: Resistor 22.1 terminal t1 is the only modeled terminal on net N1.
- `22.1:t2`: Resistor 22.1 terminal t2 is connected on net N2 with Inductor 10.1.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
