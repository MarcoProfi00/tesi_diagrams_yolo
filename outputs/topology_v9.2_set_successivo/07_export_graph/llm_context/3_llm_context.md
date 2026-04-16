# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `3` (`3.jpg`) from pipeline variant `topology_v9.2_set_successivo` was exported from `06_match_terminals_to_nets`.
The topology contains 12 components, 23 terminals, 11 nets, and 23 terminal-to-net connections.
Explicit power sources: Battery 2.1.
Explicit ground references: GND 9.1.

# Main Branches
- `N1` (source_connected_branch, importance=high): Net N1 forms a source connected branch connecting Battery 2.1, Fuse 8.1.
- `N2` (shared_internal_branch, importance=medium): Net N2 forms a shared internal branch connecting Switch 25.1, Variable_Resistor 30.1, Fuse 8.1.
- `N6` (shared_internal_branch, importance=medium): Net N6 forms a shared internal branch connecting Signal_Source 23.1, Switch 25.1, Trim_Capacitor 29.1.
- `N3` (single_terminal_stub, importance=low): Net N3 forms a single terminal stub connecting Analog_Meter 0.1, Battery 2.1.
- `N4` (single_terminal_stub, importance=low): Net N4 forms a single terminal stub connecting LED 12.1.
- `N7` (single_terminal_stub, importance=low): Net N7 forms a single terminal stub connecting Diode 7.1.

# Component Descriptions
- `0.1` (Analog_Meter): generic circuit element [specificity=low, confidence=0.55] Analog_Meter 0.1 is described as generic circuit element. It is connected to nets N3, N9 and to Battery 2.1 via N3.
- `12.1` (LED): generic circuit element [specificity=low, confidence=0.55] LED 12.1 is described as generic circuit element. It is connected to nets N4, N5 and to Variable_Resistor 30.1 via N5.
- `13.1` (Lamp): generic circuit element [specificity=low, confidence=0.55] Lamp 13.1 is described as generic circuit element. It is connected to nets N10, N11 and to Signal_Source 23.1 via N10; Variable_Resistor 30.2 via N10, N11; GND 9.1 via N11.
- `2.1` (Battery): power source [specificity=high, confidence=0.98] Battery 2.1 is described as power source. It is connected to nets N1, N3 and to Analog_Meter 0.1 via N3; Fuse 8.1 via N1.
- `23.1` (Signal_Source): generic circuit element [specificity=low, confidence=0.55] Signal_Source 23.1 is described as generic circuit element. It is connected to nets N10, N6 and to Lamp 13.1 via N10; Switch 25.1 via N6; Trim_Capacitor 29.1 via N6; Variable_Resistor 30.2 via N10.
- `25.1` (Switch): active component [specificity=low, confidence=0.72] Switch 25.1 is described as active component. It is connected to nets N2, N6 and to Signal_Source 23.1 via N6; Trim_Capacitor 29.1 via N6; Variable_Resistor 30.1 via N2; Fuse 8.1 via N2.
- `29.1` (Trim_Capacitor): generic circuit element [specificity=low, confidence=0.55] Trim_Capacitor 29.1 is described as generic circuit element. It is connected to nets N6, N8 and to Signal_Source 23.1 via N6; Switch 25.1 via N6; Diode 7.1 via N8.
- `30.1` (Variable_Resistor): generic circuit element [specificity=low, confidence=0.55] Variable_Resistor 30.1 is described as generic circuit element. It is connected to nets N2, N5 and to LED 12.1 via N5; Switch 25.1 via N2; Fuse 8.1 via N2.
- `30.2` (Variable_Resistor): generic circuit element [specificity=low, confidence=0.55] Variable_Resistor 30.2 is described as generic circuit element. It is connected to nets N10, N11 and to Lamp 13.1 via N10, N11; Signal_Source 23.1 via N10; GND 9.1 via N11.
- `7.1` (Diode): passive component [specificity=medium, confidence=0.76] Diode 7.1 is described as passive component. It is connected to nets N7, N8 and to Trim_Capacitor 29.1 via N8.
- `8.1` (Fuse): generic circuit element [specificity=low, confidence=0.55] Fuse 8.1 is described as generic circuit element. It is connected to nets N1, N2 and to Battery 2.1 via N1; Switch 25.1 via N2; Variable_Resistor 30.1 via N2.
- `9.1` (GND): ground reference [specificity=high, confidence=1.00] GND 9.1 is described as ground reference. It is connected to nets N11 and to Lamp 13.1 via N11; Variable_Resistor 30.2 via N11.

# Net Descriptions
- `N1`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N2`: shared internal branch [specificity=medium, confidence=0.72] Basis: The net behaves like a shared internal junction between multiple components.
- `N3`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N4`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N5`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N6`: shared internal branch [specificity=medium, confidence=0.72] Basis: The net behaves like a shared internal junction between multiple components.
- `N7`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N8`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N9`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N10`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N11`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.

# Aggregated Relations
- `N1`: N1 is a source connected branch connecting Battery 2.1 positive, Fuse 8.1 terminal t1.
- `N2`: N2 is a shared internal branch connecting Switch 25.1 terminal t1, Variable_Resistor 30.1 terminal t1, Fuse 8.1 terminal t2.
- `N6`: N6 is a shared internal branch connecting Signal_Source 23.1 terminal t1, Switch 25.1 terminal t2, Trim_Capacitor 29.1 terminal t1.
- `N10`: N10 is a local interconnect connecting Lamp 13.1 terminal t1, Signal_Source 23.1 terminal t2, Variable_Resistor 30.2 terminal t1.
- `N11`: N11 is a ground return connecting Lamp 13.1 terminal t2, Variable_Resistor 30.2 terminal t2, GND 9.1 terminal t1.
- `N3`: N3 is a single terminal stub connecting Analog_Meter 0.1 terminal t1, Battery 2.1 negative.
- `N5`: N5 is a local interconnect connecting LED 12.1 anode, Variable_Resistor 30.1 terminal t2.
- `N8`: N8 is a local interconnect connecting Trim_Capacitor 29.1 terminal t2, Diode 7.1 anode.

# Functional Paths
- `P1` `ground_to_device_path`: Ground to device path: GND 9.1 -> N11 (ground return) -> Lamp 13.1 -> N10 (local interconnect) -> Signal_Source 23.1 -> N6 (shared internal branch) -> Switch 25.1. Confidence: 0.68 (heuristic_inference).

# Structural Patterns
- `single_terminal_stub` on `N3`: Net N3 currently touches only Battery 2.1 negative.
- `single_terminal_stub` on `N4`: Net N4 currently touches only LED 12.1 cathode.
- `single_terminal_stub` on `N7`: Net N7 currently touches only Diode 7.1 cathode.
- `single_terminal_stub` on `N9`: Net N9 currently touches only Analog_Meter 0.1 terminal t2.

# Terminal Facts
- `0.1:t1`: Analog_Meter 0.1 terminal t1 is connected on net N3 with Battery 2.1.
- `0.1:t2`: Analog_Meter 0.1 terminal t2 is the only modeled terminal on net N9.
- `12.1:anode`: LED 12.1 terminal anode is connected on net N5 with Variable_Resistor 30.1.
- `12.1:cathode`: LED 12.1 terminal cathode is the only modeled terminal on net N4.
- `13.1:t1`: Lamp 13.1 terminal t1 is connected on net N10 with Signal_Source 23.1, Variable_Resistor 30.2.
- `13.1:t2`: Lamp 13.1 terminal t2 is connected on net N11 with GND 9.1, Variable_Resistor 30.2.
- `2.1:positive`: Battery 2.1 terminal positive is connected on net N1 with Fuse 8.1.
- `2.1:negative`: Battery 2.1 terminal negative is connected on net N3 with Analog_Meter 0.1.
- `23.1:t1`: Signal_Source 23.1 terminal t1 is connected on net N6 with Switch 25.1, Trim_Capacitor 29.1.
- `23.1:t2`: Signal_Source 23.1 terminal t2 is connected on net N10 with Lamp 13.1, Variable_Resistor 30.2.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
