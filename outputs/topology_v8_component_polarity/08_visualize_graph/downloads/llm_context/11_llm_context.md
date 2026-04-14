# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `11` (`11.jpg`) from pipeline variant `topology_v8_component_polarity` was exported from `06_match_terminals_to_nets`.
The topology contains 10 components, 18 terminals, 8 nets, and 18 terminal-to-net connections.
Explicit power sources: Battery 2.1, Battery 2.2.
Explicit ground references: GND 9.1, GND 9.2.
Possible external outputs or bridge interfaces: Terminal 26.2.

# Main Branches
- `N1` (source_connected_branch, importance=high): Net N1 forms a source connected branch connecting Battery 2.1, Battery 2.2, Terminal 26.1.
- `N2` (source_connected_branch, importance=high): Net N2 forms a source connected branch connecting Mosfet 16.1, Battery 2.2.
- `N3` (source_connected_branch, importance=high): Net N3 forms a source connected branch connecting Mosfet 16.2, Battery 2.1.
- `N7` (shared_internal_branch, importance=medium): Net N7 forms a shared internal branch connecting Mosfet 16.1, Mosfet 16.2, Polarized_Capacitor 20.1, Resistor 22.1, Terminal 26.2.
- `N4` (single_terminal_stub, importance=low): Net N4 forms a single terminal stub connecting Mosfet 16.2.
- `N5` (single_terminal_stub, importance=low): Net N5 forms a single terminal stub connecting Mosfet 16.1.

# Component Descriptions
- `16.1` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.1 is described as active component. It is connected to nets N2, N5, N7 and to Mosfet 16.2 via N7; Battery 2.2 via N2; Polarized_Capacitor 20.1 via N7; Resistor 22.1 via N7; Terminal 26.2 via N7.
- `16.2` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.2 is described as active component. It is connected to nets N3, N4, N7 and to Mosfet 16.1 via N7; Battery 2.1 via N3; Polarized_Capacitor 20.1 via N7; Resistor 22.1 via N7; Terminal 26.2 via N7.
- `2.1` (Battery): power source [specificity=high, confidence=0.98] Battery 2.1 is described as power source. It is connected to nets N1, N3 and to Mosfet 16.2 via N3; Battery 2.2 via N1; Terminal 26.1 via N1.
- `2.2` (Battery): power source [specificity=high, confidence=0.98] Battery 2.2 is described as power source. It is connected to nets N1, N2 and to Mosfet 16.1 via N2; Battery 2.1 via N1; Terminal 26.1 via N1.
- `20.1` (Polarized_Capacitor): generic circuit element [specificity=low, confidence=0.55] Polarized_Capacitor 20.1 is described as generic circuit element. It is connected to nets N6, N7 and to Mosfet 16.1 via N7; Mosfet 16.2 via N7; Resistor 22.1 via N7; Terminal 26.2 via N7; GND 9.1 via N6.
- `22.1` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.1 is described as passive component. It is connected to nets N7, N8 and to Mosfet 16.1 via N7; Mosfet 16.2 via N7; Polarized_Capacitor 20.1 via N7; Terminal 26.2 via N7; GND 9.2 via N8.
- `26.1` (Terminal): external interface [specificity=low, confidence=0.68] Terminal 26.1 is described as external interface. It is connected to nets N1 and to Battery 2.1 via N1; Battery 2.2 via N1.
- `26.2` (Terminal): external interface [specificity=low, confidence=0.74] Terminal 26.2 is described as external interface. It is connected to nets N7 and to Mosfet 16.1 via N7; Mosfet 16.2 via N7; Polarized_Capacitor 20.1 via N7; Resistor 22.1 via N7.
- `9.1` (GND): ground reference [specificity=high, confidence=1.00] GND 9.1 is described as ground reference. It is connected to nets N6 and to Polarized_Capacitor 20.1 via N6.
- `9.2` (GND): ground reference [specificity=high, confidence=1.00] GND 9.2 is described as ground reference. It is connected to nets N8 and to Resistor 22.1 via N8.

# Net Descriptions
- `N1`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N2`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N3`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N4`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N5`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N6`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N7`: shared internal branch [specificity=medium, confidence=0.70] Basis: The net behaves like a multi-device internal junction and its terminal semantics are mixed or widely shared.
- `N8`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.

# Aggregated Relations
- `N1`: N1 is a source connected branch connecting Battery 2.1 negative, Battery 2.2 positive, Terminal 26.1 terminal t1.
- `N2`: N2 is a source connected branch connecting Mosfet 16.1 gate, Battery 2.2 negative.
- `N3`: N3 is a source connected branch connecting Mosfet 16.2 gate, Battery 2.1 positive.
- `N7`: N7 is a shared internal branch connecting Mosfet 16.1 drain, Mosfet 16.2 drain, Polarized_Capacitor 20.1 positive, Resistor 22.1 terminal t1, Terminal 26.2 terminal t1.
- `N6`: N6 is a ground return connecting Polarized_Capacitor 20.1 negative, GND 9.1 terminal t1.
- `N8`: N8 is a ground return connecting Resistor 22.1 terminal t2, GND 9.2 terminal t1.

# Functional Paths
- `P1` `source_to_interface_path`: Source to interface path: Battery 2.1 -> N3 (source connected branch) -> Mosfet 16.2 -> N7 (shared internal branch) -> Terminal 26.2. Confidence: 0.78 (heuristic_inference).
- `P2` `source_to_interface_path`: Source to interface path: Battery 2.2 -> N2 (source connected branch) -> Mosfet 16.1 -> N7 (shared internal branch) -> Terminal 26.2. Confidence: 0.78 (heuristic_inference).
- `P3` `device_to_interface_path`: Device to interface path: Mosfet 16.1 -> N7 (shared internal branch) -> Terminal 26.2. Confidence: 0.74 (heuristic_inference).
- `P4` `ground_to_device_path`: Ground to device path: GND 9.1 -> N6 (ground return) -> Polarized_Capacitor 20.1 -> N7 (shared internal branch) -> Mosfet 16.1. Confidence: 0.68 (heuristic_inference).
- `P5` `ground_to_device_path`: Ground to device path: GND 9.2 -> N8 (ground return) -> Resistor 22.1 -> N7 (shared internal branch) -> Mosfet 16.1. Confidence: 0.68 (heuristic_inference).

# Structural Patterns
- `high_degree_shared_branch` on `N7`: Net N7 is a shared internal branch touching 5 modeled components.
- `single_terminal_stub` on `N4`: Net N4 currently touches only Mosfet 16.2 source.
- `single_terminal_stub` on `N5`: Net N5 currently touches only Mosfet 16.1 source.

# Terminal Facts
- `16.1:G`: Mosfet 16.1 terminal G is connected on net N2 with Battery 2.2.
- `16.1:D`: Mosfet 16.1 terminal D is connected on net N7 with Mosfet 16.2, Polarized_Capacitor 20.1, Resistor 22.1, Terminal 26.2.
- `16.1:S`: Mosfet 16.1 terminal S is the only modeled terminal on net N5.
- `16.2:G`: Mosfet 16.2 terminal G is connected on net N3 with Battery 2.1.
- `16.2:S`: Mosfet 16.2 terminal S is the only modeled terminal on net N4.
- `16.2:D`: Mosfet 16.2 terminal D is connected on net N7 with Mosfet 16.1, Polarized_Capacitor 20.1, Resistor 22.1, Terminal 26.2.
- `2.1:positive`: Battery 2.1 terminal positive is connected on net N3 with Mosfet 16.2.
- `2.1:negative`: Battery 2.1 terminal negative is connected on net N1 with Battery 2.2, Terminal 26.1.
- `2.2:positive`: Battery 2.2 terminal positive is connected on net N1 with Battery 2.1, Terminal 26.1.
- `2.2:negative`: Battery 2.2 terminal negative is connected on net N2 with Mosfet 16.1.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
