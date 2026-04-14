# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `4` (`4.jpg`) from pipeline variant `topology_v8_component_polarity` was exported from `06_match_terminals_to_nets`.
The topology contains 10 components, 18 terminals, 8 nets, and 18 terminal-to-net connections.
Explicit power sources: Current_Source 6.1.
Explicit ground references: GND 9.1, GND 9.2.
Possible external inputs: Terminal 26.2.

# Main Branches
- `N2` (external_control_branch, importance=high): Net N2 forms an external control branch connecting NPN_Transistor 18.1, Terminal 26.2, Diode 7.2.
- `N4` (source_connected_branch, importance=high): Net N4 forms a source connected branch connecting NPN_Transistor 18.2, Current_Source 6.1, Diode 7.1.
- `N6` (source_connected_branch, importance=high): Net N6 forms a source connected branch connecting NPN_Transistor 18.2, Current_Source 6.1.
- `N7` (shared_internal_branch, importance=medium): Net N7 forms a shared internal branch connecting NPN_Transistor 18.1, NPN_Transistor 18.2, Resistor 22.1.
- `N5` (single_terminal_stub, importance=low): Net N5 forms a single terminal stub connecting NPN_Transistor 18.1.

# Component Descriptions
- `18.1` (NPN_Transistor): active component [specificity=low, confidence=0.72] NPN_Transistor 18.1 is described as active component. It is connected to nets N2, N5, N7 and to NPN_Transistor 18.2 via N7; Resistor 22.1 via N7; Terminal 26.2 via N2; Diode 7.2 via N2.
- `18.2` (NPN_Transistor): active component [specificity=low, confidence=0.72] NPN_Transistor 18.2 is described as active component. It is connected to nets N4, N6, N7 and to NPN_Transistor 18.1 via N7; Resistor 22.1 via N7; Current_Source 6.1 via N4, N6; Diode 7.1 via N4.
- `22.1` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.1 is described as passive component. It is connected to nets N7, N8 and to NPN_Transistor 18.1 via N7; NPN_Transistor 18.2 via N7; GND 9.2 via N8.
- `26.1` (Terminal): external interface [specificity=low, confidence=0.68] Terminal 26.1 is described as external interface. It is connected to nets N1 and to GND 9.1 via N1.
- `26.2` (Terminal): external interface [specificity=medium, confidence=0.76] Terminal 26.2 is described as external interface. It is connected to nets N2 and to NPN_Transistor 18.1 via N2; Diode 7.2 via N2.
- `6.1` (Current_Source): power source [specificity=high, confidence=0.98] Current_Source 6.1 is described as power source. It is connected to nets N4, N6 and to NPN_Transistor 18.2 via N4, N6; Diode 7.1 via N4.
- `7.1` (Diode): passive component [specificity=medium, confidence=0.76] Diode 7.1 is described as passive component. It is connected to nets N3, N4 and to NPN_Transistor 18.2 via N4; Current_Source 6.1 via N4; Diode 7.2 via N3.
- `7.2` (Diode): passive component [specificity=medium, confidence=0.76] Diode 7.2 is described as passive component. It is connected to nets N2, N3 and to NPN_Transistor 18.1 via N2; Terminal 26.2 via N2; Diode 7.1 via N3.
- `9.1` (GND): ground reference [specificity=high, confidence=1.00] GND 9.1 is described as ground reference. It is connected to nets N1 and to Terminal 26.1 via N1.
- `9.2` (GND): ground reference [specificity=high, confidence=1.00] GND 9.2 is described as ground reference. It is connected to nets N8 and to Resistor 22.1 via N8.

# Net Descriptions
- `N1`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N2`: external control branch [specificity=medium, confidence=0.74] Basis: The net reaches an external interface and at least one control-like terminal.
- `N3`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N4`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N5`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N6`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N7`: shared internal branch [specificity=medium, confidence=0.72] Basis: The net behaves like a shared internal junction between multiple components.
- `N8`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.

# Aggregated Relations
- `N2`: N2 is a external control branch connecting NPN_Transistor 18.1 base, Terminal 26.2 terminal t1, Diode 7.2 cathode.
- `N4`: N4 is a source connected branch connecting NPN_Transistor 18.2 base, Current_Source 6.1 current_to, Diode 7.1 anode.
- `N6`: N6 is a source connected branch connecting NPN_Transistor 18.2 collector, Current_Source 6.1 current_from.
- `N7`: N7 is a shared internal branch connecting NPN_Transistor 18.1 emitter, NPN_Transistor 18.2 emitter, Resistor 22.1 terminal t1.
- `N1`: N1 is a ground return connecting Terminal 26.1 terminal t1, GND 9.1 terminal t1.
- `N3`: N3 is a local interconnect connecting Diode 7.1 cathode, Diode 7.2 anode.
- `N8`: N8 is a ground return connecting Resistor 22.1 terminal t2, GND 9.2 terminal t1.

# Functional Paths
- `P1` `external_interface_to_device_path`: External interface to device path: Terminal 26.2 -> N2 (external control branch) -> NPN_Transistor 18.1. Confidence: 0.72 (heuristic_inference).
- `P2` `ground_to_device_path`: Ground to device path: GND 9.2 -> N8 (ground return) -> Resistor 22.1 -> N7 (shared internal branch) -> NPN_Transistor 18.1. Confidence: 0.68 (heuristic_inference).

# Structural Patterns
- `single_terminal_stub` on `N5`: Net N5 currently touches only NPN_Transistor 18.1 collector.

# Terminal Facts
- `18.1:B`: NPN_Transistor 18.1 terminal B is connected on net N2 with Diode 7.2, Terminal 26.2.
- `18.1:E`: NPN_Transistor 18.1 terminal E is connected on net N7 with NPN_Transistor 18.2, Resistor 22.1.
- `18.1:C`: NPN_Transistor 18.1 terminal C is the only modeled terminal on net N5.
- `18.2:B`: NPN_Transistor 18.2 terminal B is connected on net N4 with Current_Source 6.1, Diode 7.1.
- `18.2:C`: NPN_Transistor 18.2 terminal C is connected on net N6 with Current_Source 6.1.
- `18.2:E`: NPN_Transistor 18.2 terminal E is connected on net N7 with NPN_Transistor 18.1, Resistor 22.1.
- `22.1:t1`: Resistor 22.1 terminal t1 is connected on net N7 with NPN_Transistor 18.1, NPN_Transistor 18.2.
- `22.1:t2`: Resistor 22.1 terminal t2 is connected on net N8 with GND 9.2.
- `26.1:t1`: Terminal 26.1 terminal t1 is connected on net N1 with GND 9.1.
- `26.2:t1`: Terminal 26.2 terminal t1 is connected on net N2 with Diode 7.2, NPN_Transistor 18.1.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
