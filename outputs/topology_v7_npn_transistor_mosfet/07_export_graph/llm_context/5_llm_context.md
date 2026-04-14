# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `5` (`5.jpg`) from pipeline variant `topology_v7_npn_transistor_mosfet` was exported from `06_match_terminals_to_nets`.
The topology contains 13 components, 25 terminals, 6 nets, and 25 terminal-to-net connections.
Explicit power sources: Current_Source 6.1.
Explicit ground references: GND 9.1.
Possible external outputs or bridge interfaces: Terminal 26.1, Terminal 26.3.

# Main Branches
- `N2` (source_connected_branch, importance=high): Net N2 forms a source connected branch connecting NPN_Transistor 18.3, NPN_Transistor 18.4, Resistor 22.1, Resistor 22.2, Terminal 26.2, Terminal 26.4, Current_Source 6.1.
- `N6` (source_connected_branch, importance=high): Net N6 forms a source connected branch connecting NPN_Transistor 18.3, Current_Source 6.1.
- `N1` (shared_internal_branch, importance=medium): Net N1 forms a shared internal branch connecting NPN_Transistor 18.1, NPN_Transistor 18.2, Resistor 22.1.
- `N5` (shared_internal_branch, importance=medium): Net N5 forms a shared internal branch connecting NPN_Transistor 18.2, NPN_Transistor 18.4, Resistor 22.2.

# Component Descriptions
- `18.1` (NPN_Transistor): active component [specificity=low, confidence=0.72] NPN_Transistor 18.1 is described as active component. It is connected to nets N1, N3 and to NPN_Transistor 18.2 via N1; NPN_Transistor 18.4 via N3; Resistor 22.1 via N1; Resistor 22.3 via N3; Terminal 26.1 via N3; Terminal 26.3 via N3; GND 9.1 via N3.
- `18.2` (NPN_Transistor): active component [specificity=low, confidence=0.72] NPN_Transistor 18.2 is described as active component. It is connected to nets N1, N4, N5 and to NPN_Transistor 18.1 via N1; NPN_Transistor 18.4 via N5; Resistor 22.1 via N1; Resistor 22.2 via N5; Resistor 22.3 via N4.
- `18.3` (NPN_Transistor): active component [specificity=low, confidence=0.72] NPN_Transistor 18.3 is described as active component. It is connected to nets N2, N6 and to NPN_Transistor 18.4 via N2; Resistor 22.1 via N2; Resistor 22.2 via N2; Terminal 26.2 via N2; Terminal 26.4 via N2; Current_Source 6.1 via N2, N6.
- `18.4` (NPN_Transistor): active component [specificity=low, confidence=0.72] NPN_Transistor 18.4 is described as active component. It is connected to nets N2, N3, N5 and to NPN_Transistor 18.1 via N3; NPN_Transistor 18.2 via N5; NPN_Transistor 18.3 via N2; Resistor 22.1 via N2; Resistor 22.2 via N2, N5; Resistor 22.3 via N3; Terminal 26.1 via N3; Terminal 26.2 via N2; Terminal 26.3 via N3; Terminal 26.4 via N2; Current_Source 6.1 via N2; GND 9.1 via N3.
- `22.1` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.1 is described as passive component. It is connected to nets N1, N2 and to NPN_Transistor 18.1 via N1; NPN_Transistor 18.2 via N1; NPN_Transistor 18.3 via N2; NPN_Transistor 18.4 via N2; Resistor 22.2 via N2; Terminal 26.2 via N2; Terminal 26.4 via N2; Current_Source 6.1 via N2.
- `22.2` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.2 is described as passive component. It is connected to nets N2, N5 and to NPN_Transistor 18.2 via N5; NPN_Transistor 18.3 via N2; NPN_Transistor 18.4 via N2, N5; Resistor 22.1 via N2; Terminal 26.2 via N2; Terminal 26.4 via N2; Current_Source 6.1 via N2.
- `22.3` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.3 is described as passive component. It is connected to nets N3, N4 and to NPN_Transistor 18.1 via N3; NPN_Transistor 18.2 via N4; NPN_Transistor 18.4 via N3; Terminal 26.1 via N3; Terminal 26.3 via N3; GND 9.1 via N3.
- `26.1` (Terminal): external interface [specificity=low, confidence=0.74] Terminal 26.1 is described as external interface. It is connected to nets N3 and to NPN_Transistor 18.1 via N3; NPN_Transistor 18.4 via N3; Resistor 22.3 via N3; Terminal 26.3 via N3; GND 9.1 via N3.
- `26.2` (Terminal): external interface [specificity=low, confidence=0.64] Terminal 26.2 is described as external interface. It is connected to nets N2 and to NPN_Transistor 18.3 via N2; NPN_Transistor 18.4 via N2; Resistor 22.1 via N2; Resistor 22.2 via N2; Terminal 26.4 via N2; Current_Source 6.1 via N2.
- `26.3` (Terminal): external interface [specificity=low, confidence=0.74] Terminal 26.3 is described as external interface. It is connected to nets N3 and to NPN_Transistor 18.1 via N3; NPN_Transistor 18.4 via N3; Resistor 22.3 via N3; Terminal 26.1 via N3; GND 9.1 via N3.
- `26.4` (Terminal): external interface [specificity=low, confidence=0.64] Terminal 26.4 is described as external interface. It is connected to nets N2 and to NPN_Transistor 18.3 via N2; NPN_Transistor 18.4 via N2; Resistor 22.1 via N2; Resistor 22.2 via N2; Terminal 26.2 via N2; Current_Source 6.1 via N2.
- `6.1` (Current_Source): power source [specificity=high, confidence=0.98] Current_Source 6.1 is described as power source. It is connected to nets N2, N6 and to NPN_Transistor 18.3 via N2, N6; NPN_Transistor 18.4 via N2; Resistor 22.1 via N2; Resistor 22.2 via N2; Terminal 26.2 via N2; Terminal 26.4 via N2.
- `9.1` (GND): ground reference [specificity=high, confidence=1.00] GND 9.1 is described as ground reference. It is connected to nets N3 and to NPN_Transistor 18.1 via N3; NPN_Transistor 18.4 via N3; Resistor 22.3 via N3; Terminal 26.1 via N3; Terminal 26.3 via N3.

# Net Descriptions
- `N1`: shared internal branch [specificity=medium, confidence=0.70] Basis: The net behaves like a multi-device internal junction and its terminal semantics are mixed or widely shared.
- `N2`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N3`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N4`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N5`: shared internal branch [specificity=medium, confidence=0.70] Basis: The net behaves like a multi-device internal junction and its terminal semantics are mixed or widely shared.
- `N6`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.

# Aggregated Relations
- `N2`: N2 is a source connected branch connecting NPN_Transistor 18.3 base, NPN_Transistor 18.4 collector, Resistor 22.1 terminal t1, Resistor 22.2 terminal t1, Terminal 26.2 terminal t1, Terminal 26.4 terminal t1, Current_Source 6.1 terminal t2.
- `N6`: N6 is a source connected branch connecting NPN_Transistor 18.3 collector, Current_Source 6.1 terminal t1.
- `N1`: N1 is a shared internal branch connecting NPN_Transistor 18.1 base, NPN_Transistor 18.2 base, Resistor 22.1 terminal t2.
- `N3`: N3 is a ground return connecting NPN_Transistor 18.1 emitter, NPN_Transistor 18.4 emitter, Resistor 22.3 terminal t2, Terminal 26.1 terminal t1, Terminal 26.3 terminal t1, GND 9.1 terminal t1.
- `N5`: N5 is a shared internal branch connecting NPN_Transistor 18.2 collector, NPN_Transistor 18.4 base, Resistor 22.2 terminal t2.
- `N4`: N4 is a local interconnect connecting NPN_Transistor 18.2 emitter, Resistor 22.3 terminal t1.

# Functional Paths
- `P1` `source_to_interface_path`: Source to interface path: Current_Source 6.1 -> N2 (source connected branch) -> NPN_Transistor 18.4 -> N3 (ground return) -> Terminal 26.1. Confidence: 0.78 (heuristic_inference).
- `P2` `device_to_interface_path`: Device to interface path: NPN_Transistor 18.1 -> N3 (ground return) -> Terminal 26.1. Confidence: 0.74 (heuristic_inference).
- `P3` `device_to_interface_path`: Device to interface path: NPN_Transistor 18.1 -> N3 (ground return) -> Terminal 26.3. Confidence: 0.74 (heuristic_inference).
- `P4` `ground_to_device_path`: Ground to device path: GND 9.1 -> N3 (ground return) -> NPN_Transistor 18.1. Confidence: 0.68 (heuristic_inference).

# Structural Patterns
- `multiple_terminals_same_net` on `18.1`: NPN_Transistor 18.1 has terminals 18.1:B, 18.1:C on the same net N1.
- `multiple_terminals_same_net` on `18.3`: NPN_Transistor 18.3 has terminals 18.3:B, 18.3:E on the same net N2.

# Terminal Facts
- `18.1:B`: NPN_Transistor 18.1 terminal B is connected on net N1 with NPN_Transistor 18.1, NPN_Transistor 18.2, Resistor 22.1.
- `18.1:C`: NPN_Transistor 18.1 terminal C is connected on net N1 with NPN_Transistor 18.1, NPN_Transistor 18.2, Resistor 22.1.
- `18.1:E`: NPN_Transistor 18.1 terminal E is connected on net N3 with GND 9.1, NPN_Transistor 18.4, Resistor 22.3, Terminal 26.1, Terminal 26.3.
- `18.2:B`: NPN_Transistor 18.2 terminal B is connected on net N1 with NPN_Transistor 18.1, Resistor 22.1.
- `18.2:C`: NPN_Transistor 18.2 terminal C is connected on net N5 with NPN_Transistor 18.4, Resistor 22.2.
- `18.2:E`: NPN_Transistor 18.2 terminal E is connected on net N4 with Resistor 22.3.
- `18.3:B`: NPN_Transistor 18.3 terminal B is connected on net N2 with Current_Source 6.1, NPN_Transistor 18.3, NPN_Transistor 18.4, Resistor 22.1, Resistor 22.2, Terminal 26.2, Terminal 26.4.
- `18.3:C`: NPN_Transistor 18.3 terminal C is connected on net N6 with Current_Source 6.1.
- `18.3:E`: NPN_Transistor 18.3 terminal E is connected on net N2 with Current_Source 6.1, NPN_Transistor 18.3, NPN_Transistor 18.4, Resistor 22.1, Resistor 22.2, Terminal 26.2, Terminal 26.4.
- `18.4:B`: NPN_Transistor 18.4 terminal B is connected on net N5 with NPN_Transistor 18.2, Resistor 22.2.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
