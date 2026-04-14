# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `6` (`6.jpg`) from pipeline variant `topology_v7_npn_transistor_mosfet` was exported from `06_match_terminals_to_nets`.
The topology contains 18 components, 32 terminals, 14 nets, and 32 terminal-to-net connections.
Explicit ground references: GND 9.1, GND 9.2, GND 9.3, GND 9.4, GND 9.5.
Possible external inputs: Terminal 26.1.

# Main Branches
- `N1` (external_control_branch, importance=high): Net N1 forms an external control branch connecting Mosfet 16.1, Terminal 26.1.
- `N14` (external_interface_branch, importance=high): Net N14 forms an external interface branch connecting Inductor 10.6, Terminal 26.2.
- `N11` (shared_internal_branch, importance=medium): Net N11 forms a shared internal branch connecting Inductor 10.4, Inductor 10.6, Mosfet 16.3.
- `N6` (shared_internal_branch, importance=medium): Net N6 forms a shared internal branch connecting Inductor 10.1, Inductor 10.3, Mosfet 16.2.
- `N7` (shared_internal_branch, importance=medium): Net N7 forms a shared internal branch connecting Inductor 10.2, Inductor 10.4, Mosfet 16.2.
- `N9` (shared_internal_branch, importance=medium): Net N9 forms a shared internal branch connecting Inductor 10.3, Inductor 10.5, Mosfet 16.3.

# Component Descriptions
- `10.1` (Inductor): passive component [specificity=medium, confidence=0.76] Inductor 10.1 is described as passive component. It is connected to nets N3, N6 and to Inductor 10.3 via N6; Mosfet 16.1 via N3; Mosfet 16.2 via N6.
- `10.2` (Inductor): passive component [specificity=medium, confidence=0.76] Inductor 10.2 is described as passive component. It is connected to nets N5, N7 and to Inductor 10.4 via N7; Mosfet 16.2 via N7; Resistor 22.1 via N5.
- `10.3` (Inductor): passive component [specificity=medium, confidence=0.76] Inductor 10.3 is described as passive component. It is connected to nets N6, N9 and to Inductor 10.1 via N6; Inductor 10.5 via N9; Mosfet 16.2 via N6; Mosfet 16.3 via N9.
- `10.4` (Inductor): passive component [specificity=medium, confidence=0.76] Inductor 10.4 is described as passive component. It is connected to nets N11, N7 and to Inductor 10.2 via N7; Inductor 10.6 via N11; Mosfet 16.2 via N7; Mosfet 16.3 via N11.
- `10.5` (Inductor): passive component [specificity=medium, confidence=0.76] Inductor 10.5 is described as passive component. It is connected to nets N12, N9 and to Inductor 10.3 via N9; Mosfet 16.3 via N9; Resistor 22.2 via N12.
- `10.6` (Inductor): passive component [specificity=medium, confidence=0.76] Inductor 10.6 is described as passive component. It is connected to nets N11, N14 and to Inductor 10.4 via N11; Mosfet 16.3 via N11; Terminal 26.2 via N14.
- `16.1` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.1 is described as active component. It is connected to nets N1, N2, N3 and to Inductor 10.1 via N3; Terminal 26.1 via N1; GND 9.1 via N2.
- `16.2` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.2 is described as active component. It is connected to nets N6, N7, N8 and to Inductor 10.1 via N6; Inductor 10.2 via N7; Inductor 10.3 via N6; Inductor 10.4 via N7; GND 9.3 via N8.
- `16.3` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.3 is described as active component. It is connected to nets N10, N11, N9 and to Inductor 10.3 via N9; Inductor 10.4 via N11; Inductor 10.5 via N9; Inductor 10.6 via N11; GND 9.4 via N10.
- `22.1` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.1 is described as passive component. It is connected to nets N4, N5 and to Inductor 10.2 via N5; GND 9.2 via N4.
- `22.2` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.2 is described as passive component. It is connected to nets N12, N13 and to Inductor 10.5 via N12; GND 9.5 via N13.
- `26.1` (Terminal): external interface [specificity=medium, confidence=0.76] Terminal 26.1 is described as external interface. It is connected to nets N1 and to Mosfet 16.1 via N1.
- `26.2` (Terminal): external interface [specificity=low, confidence=0.68] Terminal 26.2 is described as external interface. It is connected to nets N14 and to Inductor 10.6 via N14.
- `9.1` (GND): ground reference [specificity=high, confidence=1.00] GND 9.1 is described as ground reference. It is connected to nets N2 and to Mosfet 16.1 via N2.
- `9.2` (GND): ground reference [specificity=high, confidence=1.00] GND 9.2 is described as ground reference. It is connected to nets N4 and to Resistor 22.1 via N4.
- `9.3` (GND): ground reference [specificity=high, confidence=1.00] GND 9.3 is described as ground reference. It is connected to nets N8 and to Mosfet 16.2 via N8.
- `9.4` (GND): ground reference [specificity=high, confidence=1.00] GND 9.4 is described as ground reference. It is connected to nets N10 and to Mosfet 16.3 via N10.
- `9.5` (GND): ground reference [specificity=high, confidence=1.00] GND 9.5 is described as ground reference. It is connected to nets N13 and to Resistor 22.2 via N13.

# Net Descriptions
- `N1`: external control branch [specificity=medium, confidence=0.74] Basis: The net reaches an external interface and at least one control-like terminal.
- `N2`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N3`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N4`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N5`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N6`: shared internal branch [specificity=medium, confidence=0.72] Basis: The net behaves like a shared internal junction between multiple components.
- `N7`: shared internal branch [specificity=medium, confidence=0.72] Basis: The net behaves like a shared internal junction between multiple components.
- `N8`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N9`: shared internal branch [specificity=medium, confidence=0.72] Basis: The net behaves like a shared internal junction between multiple components.
- `N10`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N11`: shared internal branch [specificity=medium, confidence=0.72] Basis: The net behaves like a shared internal junction between multiple components.
- `N12`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N13`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N14`: external interface branch [specificity=low, confidence=0.68] Basis: The net reaches at least one explicit external interface.

# Aggregated Relations
- `N1`: N1 is a external control branch connecting Mosfet 16.1 gate, Terminal 26.1 terminal t1.
- `N14`: N14 is a external interface branch connecting Inductor 10.6 terminal t2, Terminal 26.2 terminal t1.
- `N11`: N11 is a shared internal branch connecting Inductor 10.4 terminal t2, Inductor 10.6 terminal t1, Mosfet 16.3 drain.
- `N6`: N6 is a shared internal branch connecting Inductor 10.1 terminal t2, Inductor 10.3 terminal t1, Mosfet 16.2 gate.
- `N7`: N7 is a shared internal branch connecting Inductor 10.2 terminal t2, Inductor 10.4 terminal t1, Mosfet 16.2 drain.
- `N9`: N9 is a shared internal branch connecting Inductor 10.3 terminal t2, Inductor 10.5 terminal t1, Mosfet 16.3 gate.
- `N10`: N10 is a ground return connecting Mosfet 16.3 source, GND 9.4 terminal t1.
- `N12`: N12 is a local interconnect connecting Inductor 10.5 terminal t2, Resistor 22.2 terminal t1.

# Functional Paths
- `P1` `external_interface_to_device_path`: External interface to device path: Terminal 26.1 -> N1 (external control branch) -> Mosfet 16.1. Confidence: 0.72 (heuristic_inference).
- `P2` `ground_to_device_path`: Ground to device path: GND 9.1 -> N2 (ground return) -> Mosfet 16.1. Confidence: 0.68 (heuristic_inference).
- `P3` `ground_to_device_path`: Ground to device path: GND 9.2 -> N4 (ground return) -> Resistor 22.1 -> N5 (local interconnect) -> Inductor 10.2 -> N7 (shared internal branch) -> Mosfet 16.2. Confidence: 0.68 (heuristic_inference).
- `P4` `ground_to_device_path`: Ground to device path: GND 9.3 -> N8 (ground return) -> Mosfet 16.2. Confidence: 0.68 (heuristic_inference).
- `P5` `ground_to_device_path`: Ground to device path: GND 9.4 -> N10 (ground return) -> Mosfet 16.3. Confidence: 0.68 (heuristic_inference).

# Structural Patterns
- No structural pattern was recorded from the current topology.

# Terminal Facts
- `10.1:t1`: Inductor 10.1 terminal t1 is connected on net N3 with Mosfet 16.1.
- `10.1:t2`: Inductor 10.1 terminal t2 is connected on net N6 with Inductor 10.3, Mosfet 16.2.
- `10.2:t1`: Inductor 10.2 terminal t1 is connected on net N5 with Resistor 22.1.
- `10.2:t2`: Inductor 10.2 terminal t2 is connected on net N7 with Inductor 10.4, Mosfet 16.2.
- `10.3:t1`: Inductor 10.3 terminal t1 is connected on net N6 with Inductor 10.1, Mosfet 16.2.
- `10.3:t2`: Inductor 10.3 terminal t2 is connected on net N9 with Inductor 10.5, Mosfet 16.3.
- `10.4:t1`: Inductor 10.4 terminal t1 is connected on net N7 with Inductor 10.2, Mosfet 16.2.
- `10.4:t2`: Inductor 10.4 terminal t2 is connected on net N11 with Inductor 10.6, Mosfet 16.3.
- `10.5:t1`: Inductor 10.5 terminal t1 is connected on net N9 with Inductor 10.3, Mosfet 16.3.
- `10.5:t2`: Inductor 10.5 terminal t2 is connected on net N12 with Resistor 22.2.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
