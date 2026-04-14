# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `4` (`4.jpg`) from pipeline variant `topology_v7_npn_transistor_mosfet` was exported from `06_match_terminals_to_nets`.
The topology contains 8 components, 21 terminals, 7 nets, and 21 terminal-to-net connections.
Explicit ground references: GND 9.1.

# Main Branches
- `N1` (shared_internal_branch, importance=medium): Net N1 forms a shared internal branch connecting Mosfet 16.1, Mosfet 16.2, Mosfet 16.3.
- `N2` (shared_internal_branch, importance=medium): Net N2 forms a shared internal branch connecting Mosfet 16.2, Mosfet 16.4, Mosfet 16.6.
- `N4` (shared_internal_branch, importance=medium): Net N4 forms a shared internal branch connecting Mosfet 16.1, Mosfet 16.3, Mosfet 16.5, Resistor 22.1.
- `N5` (shared_internal_branch, importance=medium): Net N5 forms a shared internal branch connecting Mosfet 16.2, Mosfet 16.3, Mosfet 16.4, Mosfet 16.6.
- `N6` (single_terminal_stub, importance=low): Net N6 forms a single terminal stub connecting Mosfet 16.5.
- `N7` (single_terminal_stub, importance=low): Net N7 forms a single terminal stub connecting Mosfet 16.6.

# Component Descriptions
- `16.1` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.1 is described as active component. It is connected to nets N1, N3, N4 and to Mosfet 16.2 via N1; Mosfet 16.3 via N1, N4; Mosfet 16.5 via N3, N4; Resistor 22.1 via N3, N4; GND 9.1 via N3.
- `16.2` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.2 is described as active component. It is connected to nets N1, N2, N5 and to Mosfet 16.1 via N1; Mosfet 16.3 via N1, N5; Mosfet 16.4 via N2, N5; Mosfet 16.6 via N2, N5.
- `16.3` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.3 is described as active component. It is connected to nets N1, N4, N5 and to Mosfet 16.1 via N1, N4; Mosfet 16.2 via N1, N5; Mosfet 16.4 via N5; Mosfet 16.5 via N4; Mosfet 16.6 via N5; Resistor 22.1 via N4.
- `16.4` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.4 is described as active component. It is connected to nets N2, N5 and to Mosfet 16.2 via N2, N5; Mosfet 16.3 via N5; Mosfet 16.6 via N2, N5.
- `16.5` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.5 is described as active component. It is connected to nets N3, N4, N6 and to Mosfet 16.1 via N3, N4; Mosfet 16.3 via N4; Resistor 22.1 via N3, N4; GND 9.1 via N3.
- `16.6` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.6 is described as active component. It is connected to nets N2, N5, N7 and to Mosfet 16.2 via N2, N5; Mosfet 16.3 via N5; Mosfet 16.4 via N2, N5.
- `22.1` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.1 is described as passive component. It is connected to nets N3, N4 and to Mosfet 16.1 via N3, N4; Mosfet 16.3 via N4; Mosfet 16.5 via N3, N4; GND 9.1 via N3.
- `9.1` (GND): ground reference [specificity=high, confidence=1.00] GND 9.1 is described as ground reference. It is connected to nets N3 and to Mosfet 16.1 via N3; Mosfet 16.5 via N3; Resistor 22.1 via N3.

# Net Descriptions
- `N1`: shared internal branch [specificity=medium, confidence=0.70] Basis: The net behaves like a multi-device internal junction and its terminal semantics are mixed or widely shared.
- `N2`: shared internal branch [specificity=medium, confidence=0.72] Basis: The net behaves like a shared internal junction between multiple components.
- `N3`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N4`: shared internal branch [specificity=medium, confidence=0.70] Basis: The net behaves like a multi-device internal junction and its terminal semantics are mixed or widely shared.
- `N5`: shared internal branch [specificity=medium, confidence=0.70] Basis: The net behaves like a multi-device internal junction and its terminal semantics are mixed or widely shared.
- `N6`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N7`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.

# Aggregated Relations
- `N1`: N1 is a shared internal branch connecting Mosfet 16.1 drain, Mosfet 16.2 drain, Mosfet 16.3 gate.
- `N2`: N2 is a shared internal branch connecting Mosfet 16.2 source, Mosfet 16.4 source, Mosfet 16.6 source.
- `N3`: N3 is a ground return connecting Mosfet 16.1 source, Mosfet 16.5 source, Resistor 22.1 terminal t2, GND 9.1 terminal t1.
- `N4`: N4 is a shared internal branch connecting Mosfet 16.1 gate, Mosfet 16.3 source, Mosfet 16.5 gate, Resistor 22.1 terminal t1.
- `N5`: N5 is a shared internal branch connecting Mosfet 16.2 gate, Mosfet 16.3 drain, Mosfet 16.4 drain, Mosfet 16.6 gate.

# Functional Paths
- `P1` `ground_to_device_path`: Ground to device path: GND 9.1 -> N3 (ground return) -> Mosfet 16.1. Confidence: 0.68 (heuristic_inference).

# Structural Patterns
- `multiple_terminals_same_net` on `16.4`: Mosfet 16.4 has terminals 16.4:G, 16.4:D on the same net N5.
- `single_terminal_stub` on `N6`: Net N6 currently touches only Mosfet 16.5 drain.
- `single_terminal_stub` on `N7`: Net N7 currently touches only Mosfet 16.6 drain.

# Terminal Facts
- `16.1:G`: Mosfet 16.1 terminal G is connected on net N4 with Mosfet 16.3, Mosfet 16.5, Resistor 22.1.
- `16.1:D`: Mosfet 16.1 terminal D is connected on net N1 with Mosfet 16.2, Mosfet 16.3.
- `16.1:S`: Mosfet 16.1 terminal S is connected on net N3 with GND 9.1, Mosfet 16.5, Resistor 22.1.
- `16.2:G`: Mosfet 16.2 terminal G is connected on net N5 with Mosfet 16.3, Mosfet 16.4, Mosfet 16.6.
- `16.2:S`: Mosfet 16.2 terminal S is connected on net N2 with Mosfet 16.4, Mosfet 16.6.
- `16.2:D`: Mosfet 16.2 terminal D is connected on net N1 with Mosfet 16.1, Mosfet 16.3.
- `16.3:G`: Mosfet 16.3 terminal G is connected on net N1 with Mosfet 16.1, Mosfet 16.2.
- `16.3:D`: Mosfet 16.3 terminal D is connected on net N5 with Mosfet 16.2, Mosfet 16.4, Mosfet 16.6.
- `16.3:S`: Mosfet 16.3 terminal S is connected on net N4 with Mosfet 16.1, Mosfet 16.5, Resistor 22.1.
- `16.4:G`: Mosfet 16.4 terminal G is connected on net N5 with Mosfet 16.2, Mosfet 16.3, Mosfet 16.4, Mosfet 16.6.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
