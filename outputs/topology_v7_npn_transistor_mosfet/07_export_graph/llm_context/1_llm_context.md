# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `1` (`1.jpg`) from pipeline variant `topology_v7_npn_transistor_mosfet` was exported from `06_match_terminals_to_nets`.
The topology contains 4 components, 10 terminals, 4 nets, and 10 terminal-to-net connections.
Explicit ground references: GND 9.1.

# Main Branches
- `N3` (shared_internal_branch, importance=medium): Net N3 forms a shared internal branch connecting Mosfet 16.1, Mosfet 16.2, Mosfet 16.3.
- `N4` (single_terminal_stub, importance=low): Net N4 forms a single terminal stub connecting Mosfet 16.2.

# Component Descriptions
- `16.1` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.1 is described as active component. It is connected to nets N1, N2, N3 and to Mosfet 16.2 via N1, N3; Mosfet 16.3 via N2, N3; GND 9.1 via N2.
- `16.2` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.2 is described as active component. It is connected to nets N1, N3, N4 and to Mosfet 16.1 via N1, N3; Mosfet 16.3 via N3.
- `16.3` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.3 is described as active component. It is connected to nets N2, N3 and to Mosfet 16.1 via N2, N3; Mosfet 16.2 via N3; GND 9.1 via N2.
- `9.1` (GND): ground reference [specificity=high, confidence=1.00] GND 9.1 is described as ground reference. It is connected to nets N2 and to Mosfet 16.1 via N2; Mosfet 16.3 via N2.

# Net Descriptions
- `N1`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N2`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N3`: shared internal branch [specificity=medium, confidence=0.70] Basis: The net behaves like a multi-device internal junction and its terminal semantics are mixed or widely shared.
- `N4`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.

# Aggregated Relations
- `N3`: N3 is a shared internal branch connecting Mosfet 16.1 gate, Mosfet 16.2 source, Mosfet 16.3 drain.
- `N1`: N1 is a local interconnect connecting Mosfet 16.1 drain, Mosfet 16.2 gate.
- `N2`: N2 is a ground return connecting Mosfet 16.1 source, Mosfet 16.3 source, GND 9.1 terminal t1.

# Functional Paths
- `P1` `ground_to_device_path`: Ground to device path: GND 9.1 -> N2 (ground return) -> Mosfet 16.1. Confidence: 0.68 (heuristic_inference).

# Structural Patterns
- `multiple_terminals_same_net` on `16.3`: Mosfet 16.3 has terminals 16.3:G, 16.3:D on the same net N3.
- `single_terminal_stub` on `N4`: Net N4 currently touches only Mosfet 16.2 drain.

# Terminal Facts
- `16.1:G`: Mosfet 16.1 terminal G is connected on net N3 with Mosfet 16.2, Mosfet 16.3.
- `16.1:D`: Mosfet 16.1 terminal D is connected on net N1 with Mosfet 16.2.
- `16.1:S`: Mosfet 16.1 terminal S is connected on net N2 with GND 9.1, Mosfet 16.3.
- `16.2:G`: Mosfet 16.2 terminal G is connected on net N1 with Mosfet 16.1.
- `16.2:D`: Mosfet 16.2 terminal D is the only modeled terminal on net N4.
- `16.2:S`: Mosfet 16.2 terminal S is connected on net N3 with Mosfet 16.1, Mosfet 16.3.
- `16.3:G`: Mosfet 16.3 terminal G is connected on net N3 with Mosfet 16.1, Mosfet 16.2, Mosfet 16.3.
- `16.3:D`: Mosfet 16.3 terminal D is connected on net N3 with Mosfet 16.1, Mosfet 16.2, Mosfet 16.3.
- `16.3:S`: Mosfet 16.3 terminal S is connected on net N2 with GND 9.1, Mosfet 16.1.
- `9.1:t1`: GND 9.1 terminal t1 is connected on net N2 with Mosfet 16.1, Mosfet 16.3.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
