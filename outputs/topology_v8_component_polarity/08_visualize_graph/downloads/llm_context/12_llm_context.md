# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `12` (`12.jpg`) from pipeline variant `topology_v8_component_polarity` was exported from `06_match_terminals_to_nets`.
The topology contains 18 components, 34 terminals, 11 nets, and 34 terminal-to-net connections.
Explicit power sources: Current_Source 6.1, Current_Source 6.2, Current_Source 6.3.
Explicit ground references: GND 9.1.
Possible external inputs: Terminal 26.2, Terminal 26.3.
Possible external outputs or bridge interfaces: Terminal 26.4.

# Main Branches
- `N1` (external_control_branch, importance=high): Net N1 forms an external control branch connecting Mosfet 16.1, Terminal 26.2.
- `N2` (external_interface_branch, importance=high): Net N2 forms an external interface branch connecting Terminal 26.1, Diode 7.1, Diode 7.2.
- `N4` (source_connected_branch, importance=high): Net N4 forms a source connected branch connecting Mosfet 16.1, Mosfet 16.2, Current_Source 6.2.
- `N7` (source_connected_branch, importance=high): Net N7 forms a source connected branch connecting Mosfet 16.1, Mosfet 16.2, Current_Source 6.1, Current_Source 6.3, Diode 7.1, Diode 7.2, Diode 7.3, Diode 7.4, Diode 7.5, Diode 7.6.
- `N8` (external_control_branch, importance=high): Net N8 forms an external control branch connecting Mosfet 16.2, Terminal 26.3.
- `N11` (shared_internal_branch, importance=medium): Net N11 forms a shared internal branch connecting Operational_Amplifier 19.1, Terminal 26.4, Diode 7.5, Diode 7.6.

# Component Descriptions
- `16.1` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.1 is described as active component. It is connected to nets N1, N4, N7 and to Mosfet 16.2 via N4, N7; Terminal 26.2 via N1; Current_Source 6.1 via N7; Current_Source 6.2 via N4; Current_Source 6.3 via N7; Diode 7.1 via N7; Diode 7.2 via N7; Diode 7.3 via N7; Diode 7.4 via N7; Diode 7.5 via N7; Diode 7.6 via N7.
- `16.2` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.2 is described as active component. It is connected to nets N4, N7, N8 and to Mosfet 16.1 via N4, N7; Terminal 26.3 via N8; Current_Source 6.1 via N7; Current_Source 6.2 via N4; Current_Source 6.3 via N7; Diode 7.1 via N7; Diode 7.2 via N7; Diode 7.3 via N7; Diode 7.4 via N7; Diode 7.5 via N7; Diode 7.6 via N7.
- `19.1` (Operational_Amplifier): generic circuit element [specificity=low, confidence=0.55] Operational_Amplifier 19.1 is described as generic circuit element. It is connected to nets N11, N9 and to Polarized_Capacitor 20.1 via N9; Terminal 26.4 via N11; Diode 7.3 via N9; Diode 7.4 via N9; Diode 7.5 via N11; Diode 7.6 via N11.
- `20.1` (Polarized_Capacitor): generic circuit element [specificity=low, confidence=0.55] Polarized_Capacitor 20.1 is described as generic circuit element. It is connected to nets N10, N9 and to Operational_Amplifier 19.1 via N9; Diode 7.3 via N9; Diode 7.4 via N9; GND 9.1 via N10.
- `26.1` (Terminal): external interface [specificity=low, confidence=0.68] Terminal 26.1 is described as external interface. It is connected to nets N2 and to Diode 7.1 via N2; Diode 7.2 via N2.
- `26.2` (Terminal): external interface [specificity=medium, confidence=0.76] Terminal 26.2 is described as external interface. It is connected to nets N1 and to Mosfet 16.1 via N1.
- `26.3` (Terminal): external interface [specificity=medium, confidence=0.76] Terminal 26.3 is described as external interface. It is connected to nets N8 and to Mosfet 16.2 via N8.
- `26.4` (Terminal): external interface [specificity=low, confidence=0.74] Terminal 26.4 is described as external interface. It is connected to nets N11 and to Operational_Amplifier 19.1 via N11; Diode 7.5 via N11; Diode 7.6 via N11.
- `6.1` (Current_Source): power source [specificity=high, confidence=0.98] Current_Source 6.1 is described as power source. It is connected to nets N3, N7 and to Mosfet 16.1 via N7; Mosfet 16.2 via N7; Current_Source 6.3 via N7; Diode 7.1 via N7; Diode 7.2 via N7; Diode 7.3 via N7; Diode 7.4 via N7; Diode 7.5 via N7; Diode 7.6 via N7.
- `6.2` (Current_Source): power source [specificity=high, confidence=0.98] Current_Source 6.2 is described as power source. It is connected to nets N4, N5 and to Mosfet 16.1 via N4; Mosfet 16.2 via N4.
- `6.3` (Current_Source): power source [specificity=high, confidence=0.98] Current_Source 6.3 is described as power source. It is connected to nets N6, N7 and to Mosfet 16.1 via N7; Mosfet 16.2 via N7; Current_Source 6.1 via N7; Diode 7.1 via N7; Diode 7.2 via N7; Diode 7.3 via N7; Diode 7.4 via N7; Diode 7.5 via N7; Diode 7.6 via N7.
- `7.1` (Diode): passive component [specificity=medium, confidence=0.76] Diode 7.1 is described as passive component. It is connected to nets N2, N7 and to Mosfet 16.1 via N7; Mosfet 16.2 via N7; Terminal 26.1 via N2; Current_Source 6.1 via N7; Current_Source 6.3 via N7; Diode 7.2 via N2, N7; Diode 7.3 via N7; Diode 7.4 via N7; Diode 7.5 via N7; Diode 7.6 via N7.
- `7.2` (Diode): passive component [specificity=medium, confidence=0.76] Diode 7.2 is described as passive component. It is connected to nets N2, N7 and to Mosfet 16.1 via N7; Mosfet 16.2 via N7; Terminal 26.1 via N2; Current_Source 6.1 via N7; Current_Source 6.3 via N7; Diode 7.1 via N2, N7; Diode 7.3 via N7; Diode 7.4 via N7; Diode 7.5 via N7; Diode 7.6 via N7.
- `7.3` (Diode): passive component [specificity=medium, confidence=0.76] Diode 7.3 is described as passive component. It is connected to nets N7, N9 and to Mosfet 16.1 via N7; Mosfet 16.2 via N7; Operational_Amplifier 19.1 via N9; Polarized_Capacitor 20.1 via N9; Current_Source 6.1 via N7; Current_Source 6.3 via N7; Diode 7.1 via N7; Diode 7.2 via N7; Diode 7.4 via N7, N9; Diode 7.5 via N7; Diode 7.6 via N7.
- `7.4` (Diode): passive component [specificity=medium, confidence=0.76] Diode 7.4 is described as passive component. It is connected to nets N7, N9 and to Mosfet 16.1 via N7; Mosfet 16.2 via N7; Operational_Amplifier 19.1 via N9; Polarized_Capacitor 20.1 via N9; Current_Source 6.1 via N7; Current_Source 6.3 via N7; Diode 7.1 via N7; Diode 7.2 via N7; Diode 7.3 via N7, N9; Diode 7.5 via N7; Diode 7.6 via N7.
- `7.5` (Diode): passive component [specificity=medium, confidence=0.76] Diode 7.5 is described as passive component. It is connected to nets N11, N7 and to Mosfet 16.1 via N7; Mosfet 16.2 via N7; Operational_Amplifier 19.1 via N11; Terminal 26.4 via N11; Current_Source 6.1 via N7; Current_Source 6.3 via N7; Diode 7.1 via N7; Diode 7.2 via N7; Diode 7.3 via N7; Diode 7.4 via N7; Diode 7.6 via N11, N7.
- `7.6` (Diode): passive component [specificity=medium, confidence=0.76] Diode 7.6 is described as passive component. It is connected to nets N11, N7 and to Mosfet 16.1 via N7; Mosfet 16.2 via N7; Operational_Amplifier 19.1 via N11; Terminal 26.4 via N11; Current_Source 6.1 via N7; Current_Source 6.3 via N7; Diode 7.1 via N7; Diode 7.2 via N7; Diode 7.3 via N7; Diode 7.4 via N7; Diode 7.5 via N11, N7.
- `9.1` (GND): ground reference [specificity=high, confidence=1.00] GND 9.1 is described as ground reference. It is connected to nets N10 and to Polarized_Capacitor 20.1 via N10.

# Net Descriptions
- `N1`: external control branch [specificity=medium, confidence=0.74] Basis: The net reaches an external interface and at least one control-like terminal.
- `N2`: external interface branch [specificity=low, confidence=0.68] Basis: The net reaches at least one explicit external interface.
- `N3`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N4`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N5`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N6`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N7`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N8`: external control branch [specificity=medium, confidence=0.74] Basis: The net reaches an external interface and at least one control-like terminal.
- `N9`: shared internal branch [specificity=medium, confidence=0.70] Basis: The net behaves like a multi-device internal junction and its terminal semantics are mixed or widely shared.
- `N10`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N11`: shared internal branch [specificity=medium, confidence=0.70] Basis: The net behaves like a multi-device internal junction and its terminal semantics are mixed or widely shared.

# Aggregated Relations
- `N1`: N1 is a external control branch connecting Mosfet 16.1 gate, Terminal 26.2 terminal t1.
- `N2`: N2 is a external interface branch connecting Terminal 26.1 terminal t1, Diode 7.1 cathode, Diode 7.2 anode.
- `N4`: N4 is a source connected branch connecting Mosfet 16.1 source, Mosfet 16.2 source, Current_Source 6.2 current_from.
- `N7`: N7 is a source connected branch connecting Mosfet 16.1 drain, Mosfet 16.2 drain, Current_Source 6.1 current_to, Current_Source 6.3 current_to, Diode 7.1 anode, Diode 7.2 cathode, Diode 7.3 cathode, Diode 7.4 anode, Diode 7.5 anode, Diode 7.6 cathode.
- `N8`: N8 is a external control branch connecting Mosfet 16.2 gate, Terminal 26.3 terminal t1.
- `N11`: N11 is a shared internal branch connecting Operational_Amplifier 19.1 in2, Terminal 26.4 terminal t1, Diode 7.5 cathode, Diode 7.6 anode.
- `N9`: N9 is a shared internal branch connecting Operational_Amplifier 19.1 in1, Polarized_Capacitor 20.1 positive, Diode 7.3 anode, Diode 7.4 cathode.
- `N10`: N10 is a ground return connecting Polarized_Capacitor 20.1 negative, GND 9.1 terminal t1.

# Functional Paths
- `P1` `source_to_interface_path`: Source to interface path: Current_Source 6.1 -> N7 (source connected branch) -> Diode 7.5 -> N11 (shared internal branch) -> Terminal 26.4. Confidence: 0.78 (heuristic_inference).
- `P2` `source_to_interface_path`: Source to interface path: Current_Source 6.2 -> N4 (source connected branch) -> Mosfet 16.1 -> N7 (source connected branch) -> Diode 7.5 -> N11 (shared internal branch) -> Terminal 26.4. Confidence: 0.78 (heuristic_inference).
- `P3` `source_to_interface_path`: Source to interface path: Current_Source 6.3 -> N7 (source connected branch) -> Diode 7.5 -> N11 (shared internal branch) -> Terminal 26.4. Confidence: 0.78 (heuristic_inference).
- `P4` `device_to_interface_path`: Device to interface path: Mosfet 16.1 -> N7 (source connected branch) -> Diode 7.5 -> N11 (shared internal branch) -> Terminal 26.4. Confidence: 0.74 (heuristic_inference).
- `P5` `external_interface_to_device_path`: External interface to device path: Terminal 26.2 -> N1 (external control branch) -> Mosfet 16.1. Confidence: 0.72 (heuristic_inference).

# Structural Patterns
- `multiple_terminals_same_net` on `19.1`: Operational_Amplifier 19.1 has terminals 19.1:in2, 19.1:out on the same net N11.
- `single_terminal_stub` on `N3`: Net N3 currently touches only Current_Source 6.1 current_from.
- `single_terminal_stub` on `N5`: Net N5 currently touches only Current_Source 6.2 current_to.
- `single_terminal_stub` on `N6`: Net N6 currently touches only Current_Source 6.3 current_from.

# Terminal Facts
- `16.1:G`: Mosfet 16.1 terminal G is connected on net N1 with Terminal 26.2.
- `16.1:D`: Mosfet 16.1 terminal D is connected on net N7 with Current_Source 6.1, Current_Source 6.3, Diode 7.1, Diode 7.2, Diode 7.3, Diode 7.4, Diode 7.5, Diode 7.6, Mosfet 16.2.
- `16.1:S`: Mosfet 16.1 terminal S is connected on net N4 with Current_Source 6.2, Mosfet 16.2.
- `16.2:G`: Mosfet 16.2 terminal G is connected on net N8 with Terminal 26.3.
- `16.2:D`: Mosfet 16.2 terminal D is connected on net N7 with Current_Source 6.1, Current_Source 6.3, Diode 7.1, Diode 7.2, Diode 7.3, Diode 7.4, Diode 7.5, Diode 7.6, Mosfet 16.1.
- `16.2:S`: Mosfet 16.2 terminal S is connected on net N4 with Current_Source 6.2, Mosfet 16.1.
- `19.1:in1`: Operational_Amplifier 19.1 terminal in1 is connected on net N9 with Diode 7.3, Diode 7.4, Polarized_Capacitor 20.1.
- `19.1:in2`: Operational_Amplifier 19.1 terminal in2 is connected on net N11 with Diode 7.5, Diode 7.6, Operational_Amplifier 19.1, Terminal 26.4.
- `19.1:out`: Operational_Amplifier 19.1 terminal out is connected on net N11 with Diode 7.5, Diode 7.6, Operational_Amplifier 19.1, Terminal 26.4.
- `20.1:positive`: Polarized_Capacitor 20.1 terminal positive is connected on net N9 with Diode 7.3, Diode 7.4, Operational_Amplifier 19.1.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
