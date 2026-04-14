# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `3` (`3.jpg`) from pipeline variant `topology_v7_npn_transistor_mosfet` was exported from `06_match_terminals_to_nets`.
The topology contains 8 components, 16 terminals, 8 nets, and 16 terminal-to-net connections.
Possible external inputs: Terminal 26.1, Terminal 26.2, Terminal 26.3.

# Main Branches
- `N1` (external_control_branch, importance=high): Net N1 forms an external control branch connecting NPN_Transistor 18.1, Terminal 26.1.
- `N6` (external_control_branch, importance=high): Net N6 forms an external control branch connecting NPN_Transistor 18.2, Terminal 26.2.
- `N8` (external_control_branch, importance=high): Net N8 forms an external control branch connecting NPN_Transistor 18.3, Terminal 26.3.
- `N4` (shared_internal_branch, importance=medium): Net N4 forms a shared internal branch connecting NPN_Transistor 18.1, NPN_Transistor 18.2, NPN_Transistor 18.3.
- `N3` (single_terminal_stub, importance=low): Net N3 forms a single terminal stub connecting NPN_Transistor 18.2.

# Component Descriptions
- `18.1` (NPN_Transistor): active component [specificity=low, confidence=0.72] NPN_Transistor 18.1 is described as active component. It is connected to nets N1, N2, N4 and to NPN_Transistor 18.2 via N4; NPN_Transistor 18.3 via N4; Resistor 22.1 via N2; Terminal 26.1 via N1.
- `18.2` (NPN_Transistor): active component [specificity=low, confidence=0.72] NPN_Transistor 18.2 is described as active component. It is connected to nets N3, N4, N6 and to NPN_Transistor 18.1 via N4; NPN_Transistor 18.3 via N4; Terminal 26.2 via N6.
- `18.3` (NPN_Transistor): active component [specificity=low, confidence=0.72] NPN_Transistor 18.3 is described as active component. It is connected to nets N4, N7, N8 and to NPN_Transistor 18.1 via N4; NPN_Transistor 18.2 via N4; Resistor 22.2 via N7; Terminal 26.3 via N8.
- `22.1` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.1 is described as passive component. It is connected to nets N2, N5 and to NPN_Transistor 18.1 via N2; Resistor 22.2 via N5.
- `22.2` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.2 is described as passive component. It is connected to nets N5, N7 and to NPN_Transistor 18.3 via N7; Resistor 22.1 via N5.
- `26.1` (Terminal): external interface [specificity=medium, confidence=0.76] Terminal 26.1 is described as external interface. It is connected to nets N1 and to NPN_Transistor 18.1 via N1.
- `26.2` (Terminal): external interface [specificity=medium, confidence=0.76] Terminal 26.2 is described as external interface. It is connected to nets N6 and to NPN_Transistor 18.2 via N6.
- `26.3` (Terminal): external interface [specificity=medium, confidence=0.76] Terminal 26.3 is described as external interface. It is connected to nets N8 and to NPN_Transistor 18.3 via N8.

# Net Descriptions
- `N1`: external control branch [specificity=medium, confidence=0.74] Basis: The net reaches an external interface and at least one control-like terminal.
- `N2`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N3`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N4`: shared internal branch [specificity=medium, confidence=0.72] Basis: The net behaves like a shared internal junction between multiple components.
- `N5`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N6`: external control branch [specificity=medium, confidence=0.74] Basis: The net reaches an external interface and at least one control-like terminal.
- `N7`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N8`: external control branch [specificity=medium, confidence=0.74] Basis: The net reaches an external interface and at least one control-like terminal.

# Aggregated Relations
- `N1`: N1 is a external control branch connecting NPN_Transistor 18.1 base, Terminal 26.1 terminal t1.
- `N6`: N6 is a external control branch connecting NPN_Transistor 18.2 base, Terminal 26.2 terminal t1.
- `N8`: N8 is a external control branch connecting NPN_Transistor 18.3 base, Terminal 26.3 terminal t1.
- `N4`: N4 is a shared internal branch connecting NPN_Transistor 18.1 emitter, NPN_Transistor 18.2 collector, NPN_Transistor 18.3 emitter.
- `N2`: N2 is a local interconnect connecting NPN_Transistor 18.1 collector, Resistor 22.1 terminal t1.
- `N5`: N5 is a local interconnect connecting Resistor 22.1 terminal t2, Resistor 22.2 terminal t2.
- `N7`: N7 is a local interconnect connecting NPN_Transistor 18.3 collector, Resistor 22.2 terminal t1.

# Functional Paths
- `P1` `external_interface_to_device_path`: External interface to device path: Terminal 26.1 -> N1 (external control branch) -> NPN_Transistor 18.1. Confidence: 0.72 (heuristic_inference).
- `P2` `external_interface_to_device_path`: External interface to device path: Terminal 26.2 -> N6 (external control branch) -> NPN_Transistor 18.2. Confidence: 0.72 (heuristic_inference).
- `P3` `external_interface_to_device_path`: External interface to device path: Terminal 26.3 -> N8 (external control branch) -> NPN_Transistor 18.3. Confidence: 0.72 (heuristic_inference).

# Structural Patterns
- `single_terminal_stub` on `N3`: Net N3 currently touches only NPN_Transistor 18.2 emitter.

# Terminal Facts
- `18.1:B`: NPN_Transistor 18.1 terminal B is connected on net N1 with Terminal 26.1.
- `18.1:E`: NPN_Transistor 18.1 terminal E is connected on net N4 with NPN_Transistor 18.2, NPN_Transistor 18.3.
- `18.1:C`: NPN_Transistor 18.1 terminal C is connected on net N2 with Resistor 22.1.
- `18.2:B`: NPN_Transistor 18.2 terminal B is connected on net N6 with Terminal 26.2.
- `18.2:E`: NPN_Transistor 18.2 terminal E is the only modeled terminal on net N3.
- `18.2:C`: NPN_Transistor 18.2 terminal C is connected on net N4 with NPN_Transistor 18.1, NPN_Transistor 18.3.
- `18.3:B`: NPN_Transistor 18.3 terminal B is connected on net N8 with Terminal 26.3.
- `18.3:E`: NPN_Transistor 18.3 terminal E is connected on net N4 with NPN_Transistor 18.1, NPN_Transistor 18.2.
- `18.3:C`: NPN_Transistor 18.3 terminal C is connected on net N7 with Resistor 22.2.
- `22.1:t1`: Resistor 22.1 terminal t1 is connected on net N2 with NPN_Transistor 18.1.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
