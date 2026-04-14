# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `9` (`9.jpg`) from pipeline variant `topology_v8_component_polarity` was exported from `06_match_terminals_to_nets`.
The topology contains 9 components, 19 terminals, 9 nets, and 19 terminal-to-net connections.
Explicit power sources: Battery 2.1, Current_Source 6.1.
Explicit ground references: GND 9.1, GND 9.2, GND 9.3.

# Main Branches
- `N6` (source_connected_branch, importance=high): Net N6 forms a source connected branch connecting Mosfet 16.1, Mosfet 16.2, Mosfet 16.3, Mosfet 16.4, Current_Source 6.1.
- `N2` (single_terminal_stub, importance=low): Net N2 forms a single terminal stub connecting Battery 2.1.
- `N5` (single_terminal_stub, importance=low): Net N5 forms a single terminal stub connecting Current_Source 6.1.
- `N7` (single_terminal_stub, importance=low): Net N7 forms a single terminal stub connecting Mosfet 16.3.

# Component Descriptions
- `16.1` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.1 is described as active component. It is connected to nets N3, N4, N6 and to Mosfet 16.2 via N3, N6; Mosfet 16.3 via N6; Mosfet 16.4 via N6; Current_Source 6.1 via N6; GND 9.2 via N4.
- `16.2` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.2 is described as active component. It is connected to nets N3, N6 and to Mosfet 16.1 via N3, N6; Mosfet 16.3 via N6; Mosfet 16.4 via N6; Current_Source 6.1 via N6.
- `16.3` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.3 is described as active component. It is connected to nets N6, N7, N8 and to Mosfet 16.1 via N6; Mosfet 16.2 via N6; Mosfet 16.4 via N6, N8; Current_Source 6.1 via N6.
- `16.4` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.4 is described as active component. It is connected to nets N6, N8, N9 and to Mosfet 16.1 via N6; Mosfet 16.2 via N6; Mosfet 16.3 via N6, N8; Current_Source 6.1 via N6; GND 9.3 via N9.
- `2.1` (Battery): power source [specificity=high, confidence=0.98] Battery 2.1 is described as power source. It is connected to nets N1, N2 and to GND 9.1 via N1.
- `6.1` (Current_Source): power source [specificity=high, confidence=0.98] Current_Source 6.1 is described as power source. It is connected to nets N5, N6 and to Mosfet 16.1 via N6; Mosfet 16.2 via N6; Mosfet 16.3 via N6; Mosfet 16.4 via N6.
- `9.1` (GND): ground reference [specificity=high, confidence=1.00] GND 9.1 is described as ground reference. It is connected to nets N1 and to Battery 2.1 via N1.
- `9.2` (GND): ground reference [specificity=high, confidence=1.00] GND 9.2 is described as ground reference. It is connected to nets N4 and to Mosfet 16.1 via N4.
- `9.3` (GND): ground reference [specificity=high, confidence=1.00] GND 9.3 is described as ground reference. It is connected to nets N9 and to Mosfet 16.4 via N9.

# Net Descriptions
- `N1`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N2`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N3`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N4`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N5`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N6`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N7`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N8`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N9`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.

# Aggregated Relations
- `N6`: N6 is a source connected branch connecting Mosfet 16.1 gate, Mosfet 16.2 drain, Mosfet 16.3 gate, Mosfet 16.4 gate, Current_Source 6.1 current_to.
- `N1`: N1 is a ground return connecting Battery 2.1 negative, GND 9.1 terminal t1.
- `N3`: N3 is a local interconnect connecting Mosfet 16.1 drain, Mosfet 16.2 source.
- `N4`: N4 is a ground return connecting Mosfet 16.1 source, GND 9.2 terminal t1.
- `N8`: N8 is a local interconnect connecting Mosfet 16.3 source, Mosfet 16.4 drain.
- `N9`: N9 is a ground return connecting Mosfet 16.4 source, GND 9.3 terminal t1.

# Functional Paths
- `P1` `ground_to_device_path`: Ground to device path: GND 9.2 -> N4 (ground return) -> Mosfet 16.1. Confidence: 0.68 (heuristic_inference).
- `P2` `ground_to_device_path`: Ground to device path: GND 9.3 -> N9 (ground return) -> Mosfet 16.4. Confidence: 0.68 (heuristic_inference).

# Structural Patterns
- `multiple_terminals_same_net` on `16.2`: Mosfet 16.2 has terminals 16.2:G, 16.2:D on the same net N6.
- `single_terminal_stub` on `N2`: Net N2 currently touches only Battery 2.1 positive.
- `single_terminal_stub` on `N5`: Net N5 currently touches only Current_Source 6.1 current_from.
- `single_terminal_stub` on `N7`: Net N7 currently touches only Mosfet 16.3 drain.

# Terminal Facts
- `16.1:G`: Mosfet 16.1 terminal G is connected on net N6 with Current_Source 6.1, Mosfet 16.2, Mosfet 16.3, Mosfet 16.4.
- `16.1:D`: Mosfet 16.1 terminal D is connected on net N3 with Mosfet 16.2.
- `16.1:S`: Mosfet 16.1 terminal S is connected on net N4 with GND 9.2.
- `16.2:G`: Mosfet 16.2 terminal G is connected on net N6 with Current_Source 6.1, Mosfet 16.1, Mosfet 16.2, Mosfet 16.3, Mosfet 16.4.
- `16.2:D`: Mosfet 16.2 terminal D is connected on net N6 with Current_Source 6.1, Mosfet 16.1, Mosfet 16.2, Mosfet 16.3, Mosfet 16.4.
- `16.2:S`: Mosfet 16.2 terminal S is connected on net N3 with Mosfet 16.1.
- `16.3:G`: Mosfet 16.3 terminal G is connected on net N6 with Current_Source 6.1, Mosfet 16.1, Mosfet 16.2, Mosfet 16.4.
- `16.3:D`: Mosfet 16.3 terminal D is the only modeled terminal on net N7.
- `16.3:S`: Mosfet 16.3 terminal S is connected on net N8 with Mosfet 16.4.
- `16.4:G`: Mosfet 16.4 terminal G is connected on net N6 with Current_Source 6.1, Mosfet 16.1, Mosfet 16.2, Mosfet 16.3.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
