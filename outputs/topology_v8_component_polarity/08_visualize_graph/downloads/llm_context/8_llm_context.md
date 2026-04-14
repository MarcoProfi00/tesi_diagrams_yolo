# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `8` (`8.jpg`) from pipeline variant `topology_v8_component_polarity` was exported from `06_match_terminals_to_nets`.
The topology contains 20 components, 42 terminals, 18 nets, and 42 terminal-to-net connections.
Explicit power sources: Battery 2.1.
Explicit ground references: GND 9.1, GND 9.2, GND 9.3, GND 9.4.
Possible external outputs or bridge interfaces: Terminal 26.1.

# Main Branches
- `N17` (external_interface_branch, importance=high): Net N17 forms an external interface branch connecting Mosfet 16.7, Resistor 22.2, Terminal 26.1.
- `N6` (source_connected_branch, importance=high): Net N6 forms a source connected branch connecting Mosfet 16.2, Mosfet 16.6, Mosfet 16.8, Battery 2.1.
- `N5` (shared_internal_branch, importance=medium): Net N5 forms a shared internal branch connecting Mosfet 16.1, Mosfet 16.3, Mosfet 16.4.
- `N7` (shared_internal_branch, importance=medium): Net N7 forms a shared internal branch connecting Mosfet 16.1, Mosfet 16.2, Mosfet 16.4, Mosfet 16.5, Mosfet 16.6.
- `N1` (single_terminal_stub, importance=low): Net N1 forms a single terminal stub connecting Battery 2.1.
- `N12` (single_terminal_stub, importance=low): Net N12 forms a single terminal stub connecting Mosfet 16.7.

# Component Descriptions
- `16.1` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.1 is described as active component. It is connected to nets N2, N5, N7 and to Mosfet 16.2 via N2, N7; Mosfet 16.3 via N5; Mosfet 16.4 via N5, N7; Mosfet 16.5 via N7; Mosfet 16.6 via N7.
- `16.2` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.2 is described as active component. It is connected to nets N2, N6, N7 and to Mosfet 16.1 via N2, N7; Mosfet 16.4 via N7; Mosfet 16.5 via N7; Mosfet 16.6 via N6, N7; Mosfet 16.8 via N6; Battery 2.1 via N6.
- `16.3` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.3 is described as active component. It is connected to nets N3, N5 and to Mosfet 16.1 via N5; Mosfet 16.4 via N5; Diode 7.1 via N3.
- `16.4` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.4 is described as active component. It is connected to nets N5, N7, N9 and to Mosfet 16.1 via N5, N7; Mosfet 16.2 via N7; Mosfet 16.3 via N5; Mosfet 16.5 via N7; Mosfet 16.6 via N7; Resistor 22.1 via N9.
- `16.5` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.5 is described as active component. It is connected to nets N7, N8 and to Mosfet 16.1 via N7; Mosfet 16.2 via N7; Mosfet 16.4 via N7; Mosfet 16.6 via N7, N8.
- `16.6` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.6 is described as active component. It is connected to nets N6, N7, N8 and to Mosfet 16.1 via N7; Mosfet 16.2 via N6, N7; Mosfet 16.4 via N7; Mosfet 16.5 via N7, N8; Mosfet 16.8 via N6; Battery 2.1 via N6.
- `16.7` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.7 is described as active component. It is connected to nets N12, N14, N17 and to Mosfet 16.8 via N14; Resistor 22.2 via N17; Terminal 26.1 via N17.
- `16.8` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.8 is described as active component. It is connected to nets N13, N14, N6 and to Mosfet 16.2 via N6; Mosfet 16.6 via N6; Mosfet 16.7 via N14; Battery 2.1 via N6.
- `2.1` (Battery): power source [specificity=high, confidence=0.98] Battery 2.1 is described as power source. It is connected to nets N1, N6 and to Mosfet 16.2 via N6; Mosfet 16.6 via N6; Mosfet 16.8 via N6.
- `22.1` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.1 is described as passive component. It is connected to nets N10, N9 and to Mosfet 16.4 via N9; Diode 7.2 via N10.
- `22.2` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.2 is described as passive component. It is connected to nets N16, N17 and to Mosfet 16.7 via N17; Terminal 26.1 via N17; Diode 7.3 via N16.
- `26.1` (Terminal): external interface [specificity=low, confidence=0.74] Terminal 26.1 is described as external interface. It is connected to nets N17 and to Mosfet 16.7 via N17; Resistor 22.2 via N17.
- `26.2` (Terminal): external interface [specificity=low, confidence=0.68] Terminal 26.2 is described as external interface. It is connected to nets N18 and to GND 9.4 via N18.
- `7.1` (Diode): passive component [specificity=medium, confidence=0.76] Diode 7.1 is described as passive component. It is connected to nets N3, N4 and to Mosfet 16.3 via N3; GND 9.1 via N4.
- `7.2` (Diode): passive component [specificity=medium, confidence=0.76] Diode 7.2 is described as passive component. It is connected to nets N10, N11 and to Resistor 22.1 via N10; GND 9.2 via N11.
- `7.3` (Diode): passive component [specificity=medium, confidence=0.76] Diode 7.3 is described as passive component. It is connected to nets N15, N16 and to Resistor 22.2 via N16; GND 9.3 via N15.
- `9.1` (GND): ground reference [specificity=high, confidence=1.00] GND 9.1 is described as ground reference. It is connected to nets N4 and to Diode 7.1 via N4.
- `9.2` (GND): ground reference [specificity=high, confidence=1.00] GND 9.2 is described as ground reference. It is connected to nets N11 and to Diode 7.2 via N11.
- `9.3` (GND): ground reference [specificity=high, confidence=1.00] GND 9.3 is described as ground reference. It is connected to nets N15 and to Diode 7.3 via N15.
- `9.4` (GND): ground reference [specificity=high, confidence=1.00] GND 9.4 is described as ground reference. It is connected to nets N18 and to Terminal 26.2 via N18.

# Net Descriptions
- `N1`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N2`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N3`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N4`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N5`: shared internal branch [specificity=medium, confidence=0.70] Basis: The net behaves like a multi-device internal junction and its terminal semantics are mixed or widely shared.
- `N6`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N7`: shared internal branch [specificity=medium, confidence=0.70] Basis: The net behaves like a multi-device internal junction and its terminal semantics are mixed or widely shared.
- `N8`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N9`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N10`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N11`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N12`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N13`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N14`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N15`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N16`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N17`: external interface branch [specificity=medium, confidence=0.74] Basis: The net reaches an external interface and output-like active-device terminals.
- `N18`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.

# Aggregated Relations
- `N17`: N17 is a external interface branch connecting Mosfet 16.7 drain, Resistor 22.2 terminal t1, Terminal 26.1 terminal t1.
- `N6`: N6 is a source connected branch connecting Mosfet 16.2 source, Mosfet 16.6 source, Mosfet 16.8 source, Battery 2.1 positive.
- `N5`: N5 is a shared internal branch connecting Mosfet 16.1 drain, Mosfet 16.3 drain, Mosfet 16.4 gate.
- `N7`: N7 is a shared internal branch connecting Mosfet 16.1 gate, Mosfet 16.2 gate, Mosfet 16.4 drain, Mosfet 16.5 drain, Mosfet 16.6 gate.
- `N10`: N10 is a local interconnect connecting Resistor 22.1 terminal t2, Diode 7.2 anode.
- `N11`: N11 is a ground return connecting Diode 7.2 cathode, GND 9.2 terminal t1.
- `N14`: N14 is a local interconnect connecting Mosfet 16.7 source, Mosfet 16.8 drain.
- `N15`: N15 is a ground return connecting Diode 7.3 cathode, GND 9.3 terminal t1.

# Functional Paths
- `P1` `source_to_interface_path`: Source to interface path: Battery 2.1 -> N6 (source connected branch) -> Mosfet 16.8 -> N14 (local interconnect) -> Mosfet 16.7 -> N17 (external interface branch) -> Terminal 26.1. Confidence: 0.78 (heuristic_inference).
- `P2` `device_to_interface_path`: Device to interface path: Mosfet 16.7 -> N17 (external interface branch) -> Terminal 26.1. Confidence: 0.74 (heuristic_inference).
- `P3` `ground_to_device_path`: Ground to device path: GND 9.1 -> N4 (ground return) -> Diode 7.1 -> N3 (local interconnect) -> Mosfet 16.3. Confidence: 0.68 (heuristic_inference).
- `P4` `ground_to_device_path`: Ground to device path: GND 9.2 -> N11 (ground return) -> Diode 7.2 -> N10 (local interconnect) -> Resistor 22.1 -> N9 (local interconnect) -> Mosfet 16.4. Confidence: 0.68 (heuristic_inference).
- `P5` `ground_to_device_path`: Ground to device path: GND 9.3 -> N15 (ground return) -> Diode 7.3 -> N16 (local interconnect) -> Resistor 22.2 -> N17 (external interface branch) -> Mosfet 16.7. Confidence: 0.68 (heuristic_inference).

# Structural Patterns
- `high_degree_shared_branch` on `N7`: Net N7 is a shared internal branch touching 5 modeled components.
- `multiple_terminals_same_net` on `16.3`: Mosfet 16.3 has terminals 16.3:G, 16.3:D on the same net N5.
- `multiple_terminals_same_net` on `16.5`: Mosfet 16.5 has terminals 16.5:G, 16.5:D on the same net N7.
- `single_terminal_stub` on `N1`: Net N1 currently touches only Battery 2.1 negative.
- `single_terminal_stub` on `N12`: Net N12 currently touches only Mosfet 16.7 gate.
- `single_terminal_stub` on `N13`: Net N13 currently touches only Mosfet 16.8 gate.

# Terminal Facts
- `16.1:G`: Mosfet 16.1 terminal G is connected on net N7 with Mosfet 16.2, Mosfet 16.4, Mosfet 16.5, Mosfet 16.6.
- `16.1:S`: Mosfet 16.1 terminal S is connected on net N2 with Mosfet 16.2.
- `16.1:D`: Mosfet 16.1 terminal D is connected on net N5 with Mosfet 16.3, Mosfet 16.4.
- `16.2:G`: Mosfet 16.2 terminal G is connected on net N7 with Mosfet 16.1, Mosfet 16.4, Mosfet 16.5, Mosfet 16.6.
- `16.2:S`: Mosfet 16.2 terminal S is connected on net N6 with Battery 2.1, Mosfet 16.6, Mosfet 16.8.
- `16.2:D`: Mosfet 16.2 terminal D is connected on net N2 with Mosfet 16.1.
- `16.3:G`: Mosfet 16.3 terminal G is connected on net N5 with Mosfet 16.1, Mosfet 16.3, Mosfet 16.4.
- `16.3:D`: Mosfet 16.3 terminal D is connected on net N5 with Mosfet 16.1, Mosfet 16.3, Mosfet 16.4.
- `16.3:S`: Mosfet 16.3 terminal S is connected on net N3 with Diode 7.1.
- `16.4:G`: Mosfet 16.4 terminal G is connected on net N5 with Mosfet 16.1, Mosfet 16.3.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
