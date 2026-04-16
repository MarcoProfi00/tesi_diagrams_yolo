# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `13` (`13.jpg`) from pipeline variant `topology_v9.2_set_successivo` was exported from `06_match_terminals_to_nets`.
The topology contains 18 components, 35 terminals, 14 nets, and 35 terminal-to-net connections.
Possible external outputs or bridge interfaces: Terminal 26.4.

# Main Branches
- `N1` (external_interface_branch, importance=high): Net N1 forms an external interface branch connecting Terminal 26.2, Transformer 28.1.
- `N14` (external_interface_branch, importance=high): Net N14 forms an external interface branch connecting Terminal 26.3, Fuse 8.1.
- `N2` (external_interface_branch, importance=high): Net N2 forms an external interface branch connecting Terminal 26.1, Transformer 28.1.
- `N3` (shared_internal_branch, importance=medium): Net N3 forms a shared internal branch connecting Resistor 22.1, Resistor 22.2, Transformer 28.1, Diode 7.2.
- `N8` (shared_internal_branch, importance=medium): Net N8 forms a shared internal branch connecting Resistor 22.3, Resistor 22.6, Diode 7.2, Diode 7.3, Diode 7.4.
- `N9` (shared_internal_branch, importance=medium): Net N9 forms a shared internal branch connecting NPN_Transistor 18.1, Resistor 22.4, Terminal 26.4, Transformer 28.1.

# Component Descriptions
- `12.1` (LED): generic circuit element [specificity=low, confidence=0.55] LED 12.1 is described as generic circuit element. It is connected to nets N10, N7 and to NPN_Transistor 18.1 via N7.
- `18.1` (NPN_Transistor): active component [specificity=low, confidence=0.72] NPN_Transistor 18.1 is described as active component. It is connected to nets N5, N7, N9 and to LED 12.1 via N7; Resistor 22.4 via N9; Terminal 26.4 via N9; Transformer 28.1 via N9; Diode 7.1 via N5.
- `22.1` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.1 is described as passive component. It is connected to nets N3, N6 and to Resistor 22.2 via N3; Transformer 28.1 via N3; Diode 7.2 via N3; Diode 7.4 via N6.
- `22.2` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.2 is described as passive component. It is connected to nets N3, N4 and to Resistor 22.1 via N3; Transformer 28.1 via N3; Diode 7.1 via N4; Diode 7.2 via N3; Diode 7.3 via N4.
- `22.3` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.3 is described as passive component. It is connected to nets N11, N8 and to Resistor 22.5 via N11; Resistor 22.6 via N8; Diode 7.2 via N8; Diode 7.3 via N8; Diode 7.4 via N8.
- `22.4` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.4 is described as passive component. It is connected to nets N12, N9 and to NPN_Transistor 18.1 via N9; Resistor 22.5 via N12; Terminal 26.4 via N9; Transformer 28.1 via N9.
- `22.5` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.5 is described as passive component. It is connected to nets N11, N12 and to Resistor 22.3 via N11; Resistor 22.4 via N12.
- `22.6` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.6 is described as passive component. It is connected to nets N13, N8 and to Resistor 22.3 via N8; Diode 7.2 via N8; Diode 7.3 via N8; Diode 7.4 via N8; Fuse 8.1 via N13.
- `26.1` (Terminal): external interface [specificity=low, confidence=0.68] Terminal 26.1 is described as external interface. It is connected to nets N2 and to Transformer 28.1 via N2.
- `26.2` (Terminal): external interface [specificity=low, confidence=0.68] Terminal 26.2 is described as external interface. It is connected to nets N1 and to Transformer 28.1 via N1.
- `26.3` (Terminal): external interface [specificity=low, confidence=0.68] Terminal 26.3 is described as external interface. It is connected to nets N14 and to Fuse 8.1 via N14.
- `26.4` (Terminal): external interface [specificity=low, confidence=0.74] Terminal 26.4 is described as external interface. It is connected to nets N9 and to NPN_Transistor 18.1 via N9; Resistor 22.4 via N9; Transformer 28.1 via N9.
- `28.1` (Transformer): generic circuit element [specificity=low, confidence=0.55] Transformer 28.1 is described as generic circuit element. It is connected to nets N1, N2, N3, N9 and to NPN_Transistor 18.1 via N9; Resistor 22.1 via N3; Resistor 22.2 via N3; Resistor 22.4 via N9; Terminal 26.1 via N2; Terminal 26.2 via N1; Terminal 26.4 via N9; Diode 7.2 via N3.
- `7.1` (Diode): passive component [specificity=medium, confidence=0.76] Diode 7.1 is described as passive component. It is connected to nets N4, N5 and to NPN_Transistor 18.1 via N5; Resistor 22.2 via N4; Diode 7.3 via N4.
- `7.2` (Diode): passive component [specificity=medium, confidence=0.76] Diode 7.2 is described as passive component. It is connected to nets N3, N8 and to Resistor 22.1 via N3; Resistor 22.2 via N3; Resistor 22.3 via N8; Resistor 22.6 via N8; Transformer 28.1 via N3; Diode 7.3 via N8; Diode 7.4 via N8.
- `7.3` (Diode): passive component [specificity=medium, confidence=0.76] Diode 7.3 is described as passive component. It is connected to nets N4, N8 and to Resistor 22.2 via N4; Resistor 22.3 via N8; Resistor 22.6 via N8; Diode 7.1 via N4; Diode 7.2 via N8; Diode 7.4 via N8.
- `7.4` (Diode): passive component [specificity=medium, confidence=0.76] Diode 7.4 is described as passive component. It is connected to nets N6, N8 and to Resistor 22.1 via N6; Resistor 22.3 via N8; Resistor 22.6 via N8; Diode 7.2 via N8; Diode 7.3 via N8.
- `8.1` (Fuse): generic circuit element [specificity=low, confidence=0.55] Fuse 8.1 is described as generic circuit element. It is connected to nets N13, N14 and to Resistor 22.6 via N13; Terminal 26.3 via N14.

# Net Descriptions
- `N1`: external interface branch [specificity=low, confidence=0.68] Basis: The net reaches at least one explicit external interface.
- `N2`: external interface branch [specificity=low, confidence=0.68] Basis: The net reaches at least one explicit external interface.
- `N3`: shared internal branch [specificity=medium, confidence=0.70] Basis: The net behaves like a multi-device internal junction and its terminal semantics are mixed or widely shared.
- `N4`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N5`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N6`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N7`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N8`: shared internal branch [specificity=medium, confidence=0.70] Basis: The net behaves like a multi-device internal junction and its terminal semantics are mixed or widely shared.
- `N9`: shared internal branch [specificity=medium, confidence=0.70] Basis: The net behaves like a multi-device internal junction and its terminal semantics are mixed or widely shared.
- `N10`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N11`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N12`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N13`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N14`: external interface branch [specificity=low, confidence=0.68] Basis: The net reaches at least one explicit external interface.

# Aggregated Relations
- `N1`: N1 is a external interface branch connecting Terminal 26.2 terminal t1, Transformer 28.1 terminal t3.
- `N14`: N14 is a external interface branch connecting Terminal 26.3 terminal t1, Fuse 8.1 terminal t2.
- `N2`: N2 is a external interface branch connecting Terminal 26.1 terminal t1, Transformer 28.1 terminal t1.
- `N3`: N3 is a shared internal branch connecting Resistor 22.1 terminal t1, Resistor 22.2 terminal t1, Transformer 28.1 terminal t2, Diode 7.2 anode.
- `N8`: N8 is a shared internal branch connecting Resistor 22.3 terminal t1, Resistor 22.6 terminal t1, Diode 7.2 cathode, Diode 7.3 cathode, Diode 7.4 cathode.
- `N9`: N9 is a shared internal branch connecting NPN_Transistor 18.1 emitter, Resistor 22.4 terminal t2, Terminal 26.4 terminal t1, Transformer 28.1 terminal t4.
- `N11`: N11 is a local interconnect connecting Resistor 22.3 terminal t2, Resistor 22.5 terminal t1.
- `N12`: N12 is a local interconnect connecting Resistor 22.4 terminal t1, Resistor 22.5 terminal t2.

# Functional Paths
- `P1` `device_to_interface_path`: Device to interface path: NPN_Transistor 18.1 -> N9 (shared internal branch) -> Terminal 26.4. Confidence: 0.74 (heuristic_inference).

# Structural Patterns
- `high_degree_shared_branch` on `N8`: Net N8 is a shared internal branch touching 5 modeled components.
- `single_terminal_stub` on `N10`: Net N10 currently touches only LED 12.1 anode.
- `single_terminal_stub` on `N5`: Net N5 currently touches only Diode 7.1 cathode.

# Terminal Facts
- `12.1:cathode`: LED 12.1 terminal cathode is connected on net N7 with NPN_Transistor 18.1.
- `12.1:anode`: LED 12.1 terminal anode is the only modeled terminal on net N10.
- `18.1:B`: NPN_Transistor 18.1 terminal B is connected on net N7 with LED 12.1.
- `18.1:C`: NPN_Transistor 18.1 terminal C is connected on net N5 with Diode 7.1.
- `18.1:E`: NPN_Transistor 18.1 terminal E is connected on net N9 with Resistor 22.4, Terminal 26.4, Transformer 28.1.
- `22.1:t1`: Resistor 22.1 terminal t1 is connected on net N3 with Diode 7.2, Resistor 22.2, Transformer 28.1.
- `22.1:t2`: Resistor 22.1 terminal t2 is connected on net N6 with Diode 7.4.
- `22.2:t1`: Resistor 22.2 terminal t1 is connected on net N3 with Diode 7.2, Resistor 22.1, Transformer 28.1.
- `22.2:t2`: Resistor 22.2 terminal t2 is connected on net N4 with Diode 7.1, Diode 7.3.
- `22.3:t1`: Resistor 22.3 terminal t1 is connected on net N8 with Diode 7.2, Diode 7.3, Diode 7.4, Resistor 22.6.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
