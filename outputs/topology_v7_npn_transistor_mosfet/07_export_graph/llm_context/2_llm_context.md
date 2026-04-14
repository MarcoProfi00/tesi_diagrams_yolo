# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `2` (`2.jpg`) from pipeline variant `topology_v7_npn_transistor_mosfet` was exported from `06_match_terminals_to_nets`.
The topology contains 14 components, 29 terminals, 11 nets, and 29 terminal-to-net connections.
Explicit power sources: Battery 2.1.
Explicit ground references: GND 9.1, GND 9.2, GND 9.3.
Possible external inputs: Terminal 26.1.
Possible external outputs or bridge interfaces: Terminal 26.3.

# Main Branches
- `N10` (source_connected_branch, importance=high): Net N10 forms a source connected branch connecting Battery 2.1, Terminal 26.3.
- `N2` (external_control_branch, importance=high): Net N2 forms an external control branch connecting Mosfet 16.2, Terminal 26.1.
- `N9` (external_interface_branch, importance=high): Net N9 forms an external interface branch connecting Mosfet 16.5, Mosfet 16.6, Terminal 26.3.
- `N4` (shared_internal_branch, importance=medium): Net N4 forms a shared internal branch connecting Mosfet 16.2, Mosfet 16.3, Mosfet 16.5.
- `N6` (shared_internal_branch, importance=medium): Net N6 forms a shared internal branch connecting Mosfet 16.1, Mosfet 16.2, Mosfet 16.4, Mosfet 16.6, Resistor 22.1, Terminal 26.2.
- `N1` (single_terminal_stub, importance=low): Net N1 forms a single terminal stub connecting Mosfet 16.1.

# Component Descriptions
- `16.1` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.1 is described as active component. It is connected to nets N1, N3, N6 and to Mosfet 16.2 via N6; Mosfet 16.4 via N6; Mosfet 16.6 via N6; Resistor 22.1 via N6; Terminal 26.2 via N6; GND 9.1 via N3.
- `16.2` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.2 is described as active component. It is connected to nets N2, N4, N6 and to Mosfet 16.1 via N6; Mosfet 16.3 via N4; Mosfet 16.4 via N6; Mosfet 16.5 via N4; Mosfet 16.6 via N6; Resistor 22.1 via N6; Terminal 26.1 via N2; Terminal 26.2 via N6.
- `16.3` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.3 is described as active component. It is connected to nets N4, N7 and to Mosfet 16.2 via N4; Mosfet 16.5 via N4, N7.
- `16.4` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.4 is described as active component. It is connected to nets N5, N6, N8 and to Mosfet 16.1 via N6; Mosfet 16.2 via N6; Mosfet 16.6 via N6; Resistor 22.1 via N6; Terminal 26.2 via N6; GND 9.2 via N8.
- `16.5` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.5 is described as active component. It is connected to nets N4, N7, N9 and to Mosfet 16.2 via N4; Mosfet 16.3 via N4, N7; Mosfet 16.6 via N9; Terminal 26.3 via N9.
- `16.6` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.6 is described as active component. It is connected to nets N6, N9 and to Mosfet 16.1 via N6; Mosfet 16.2 via N6; Mosfet 16.4 via N6; Mosfet 16.5 via N9; Resistor 22.1 via N6; Terminal 26.2 via N6; Terminal 26.3 via N9.
- `2.1` (Battery): power source [specificity=high, confidence=0.98] Battery 2.1 is described as power source. It is connected to nets N10, N11 and to Terminal 26.3 via N10; GND 9.3 via N11.
- `22.1` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.1 is described as passive component. It is connected to nets N6 and to Mosfet 16.1 via N6; Mosfet 16.2 via N6; Mosfet 16.4 via N6; Mosfet 16.6 via N6; Terminal 26.2 via N6.
- `26.1` (Terminal): external interface [specificity=medium, confidence=0.76] Terminal 26.1 is described as external interface. It is connected to nets N2 and to Mosfet 16.2 via N2.
- `26.2` (Terminal): external interface [specificity=low, confidence=0.64] Terminal 26.2 is described as external interface. It is connected to nets N6 and to Mosfet 16.1 via N6; Mosfet 16.2 via N6; Mosfet 16.4 via N6; Mosfet 16.6 via N6; Resistor 22.1 via N6.
- `26.3` (Terminal): external interface [specificity=medium, confidence=0.82] Terminal 26.3 is described as external interface. It is connected to nets N10, N9 and to Mosfet 16.5 via N9; Mosfet 16.6 via N9; Battery 2.1 via N10.
- `9.1` (GND): ground reference [specificity=high, confidence=1.00] GND 9.1 is described as ground reference. It is connected to nets N3 and to Mosfet 16.1 via N3.
- `9.2` (GND): ground reference [specificity=high, confidence=1.00] GND 9.2 is described as ground reference. It is connected to nets N8 and to Mosfet 16.4 via N8.
- `9.3` (GND): ground reference [specificity=high, confidence=1.00] GND 9.3 is described as ground reference. It is connected to nets N11 and to Battery 2.1 via N11.

# Net Descriptions
- `N1`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N2`: external control branch [specificity=medium, confidence=0.74] Basis: The net reaches an external interface and at least one control-like terminal.
- `N3`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N4`: shared internal branch [specificity=medium, confidence=0.70] Basis: The net behaves like a multi-device internal junction and its terminal semantics are mixed or widely shared.
- `N5`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N6`: shared internal branch [specificity=medium, confidence=0.70] Basis: The net behaves like a multi-device internal junction and its terminal semantics are mixed or widely shared.
- `N7`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N8`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N9`: external interface branch [specificity=medium, confidence=0.74] Basis: The net reaches an external interface and output-like active-device terminals.
- `N10`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N11`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.

# Aggregated Relations
- `N10`: N10 is a source connected branch connecting Battery 2.1 terminal t1, Terminal 26.3 terminal t2.
- `N2`: N2 is a external control branch connecting Mosfet 16.2 gate, Terminal 26.1 terminal t1.
- `N9`: N9 is a external interface branch connecting Mosfet 16.5 drain, Mosfet 16.6 drain, Terminal 26.3 terminal t1.
- `N4`: N4 is a shared internal branch connecting Mosfet 16.2 drain, Mosfet 16.3 drain, Mosfet 16.5 gate.
- `N6`: N6 is a shared internal branch connecting Mosfet 16.1 drain, Mosfet 16.2 source, Mosfet 16.4 drain, Mosfet 16.6 gate, Resistor 22.1 terminal t1, Terminal 26.2 terminal t1.
- `N11`: N11 is a ground return connecting Battery 2.1 terminal t2, GND 9.3 terminal t1.
- `N3`: N3 is a ground return connecting Mosfet 16.1 source, GND 9.1 terminal t1.
- `N7`: N7 is a local interconnect connecting Mosfet 16.3 source, Mosfet 16.5 source.

# Functional Paths
- `P1` `source_to_interface_path`: Source to interface path: Battery 2.1 -> N10 (source connected branch) -> Terminal 26.3. Confidence: 0.78 (heuristic_inference).
- `P2` `device_to_interface_path`: Device to interface path: Mosfet 16.5 -> N9 (external interface branch) -> Terminal 26.3. Confidence: 0.74 (heuristic_inference).
- `P3` `external_interface_to_device_path`: External interface to device path: Terminal 26.1 -> N2 (external control branch) -> Mosfet 16.2. Confidence: 0.72 (heuristic_inference).
- `P4` `ground_to_device_path`: Ground to device path: GND 9.1 -> N3 (ground return) -> Mosfet 16.1. Confidence: 0.68 (heuristic_inference).
- `P5` `ground_to_device_path`: Ground to device path: GND 9.2 -> N8 (ground return) -> Mosfet 16.4. Confidence: 0.68 (heuristic_inference).

# Structural Patterns
- `collapsed_passive_component` on `22.1`: Resistor 22.1 has terminals 22.1:t1, 22.1:t2 on the same net N6.
- `high_degree_shared_branch` on `N6`: Net N6 is a shared internal branch touching 6 modeled components.
- `multiple_terminals_same_net` on `16.3`: Mosfet 16.3 has terminals 16.3:G, 16.3:D on the same net N4.
- `multiple_terminals_same_net` on `16.6`: Mosfet 16.6 has terminals 16.6:G, 16.6:S on the same net N6.
- `single_terminal_stub` on `N1`: Net N1 currently touches only Mosfet 16.1 gate.
- `single_terminal_stub` on `N5`: Net N5 currently touches only Mosfet 16.4 gate.

# Terminal Facts
- `16.1:G`: Mosfet 16.1 terminal G is the only modeled terminal on net N1.
- `16.1:D`: Mosfet 16.1 terminal D is connected on net N6 with Mosfet 16.2, Mosfet 16.4, Mosfet 16.6, Resistor 22.1, Terminal 26.2.
- `16.1:S`: Mosfet 16.1 terminal S is connected on net N3 with GND 9.1.
- `16.2:G`: Mosfet 16.2 terminal G is connected on net N2 with Terminal 26.1.
- `16.2:D`: Mosfet 16.2 terminal D is connected on net N4 with Mosfet 16.3, Mosfet 16.5.
- `16.2:S`: Mosfet 16.2 terminal S is connected on net N6 with Mosfet 16.1, Mosfet 16.4, Mosfet 16.6, Resistor 22.1, Terminal 26.2.
- `16.3:G`: Mosfet 16.3 terminal G is connected on net N4 with Mosfet 16.2, Mosfet 16.3, Mosfet 16.5.
- `16.3:S`: Mosfet 16.3 terminal S is connected on net N7 with Mosfet 16.5.
- `16.3:D`: Mosfet 16.3 terminal D is connected on net N4 with Mosfet 16.2, Mosfet 16.3, Mosfet 16.5.
- `16.4:G`: Mosfet 16.4 terminal G is the only modeled terminal on net N5.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
