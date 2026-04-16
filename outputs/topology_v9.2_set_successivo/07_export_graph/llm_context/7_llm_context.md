# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `7` (`7.jpg`) from pipeline variant `topology_v9.2_set_successivo` was exported from `06_match_terminals_to_nets`.
The topology contains 15 components, 33 terminals, 13 nets, and 30 terminal-to-net connections.
Explicit power sources: Battery 2.1.
Explicit ground references: GND 9.1, GND 9.2, GND 9.3.

# Main Branches
- `N1` (source_connected_branch, importance=high): Net N1 forms a source connected branch connecting Battery 2.1, Fuse 8.1.
- `N3` (source_connected_branch, importance=high): Net N3 forms a source connected branch connecting Operational_Amplifier 19.1, Battery 2.1.
- `N8` (shared_internal_branch, importance=medium): Net N8 forms a shared internal branch connecting Resistor 22.1, Switch 25.1, Transformer 28.1, Capacitor 4.1, Connector 5.1.

# Component Descriptions
- `12.1` (LED): generic circuit element [specificity=low, confidence=0.55] LED 12.1 is described as generic circuit element. It is connected to nets N4, N5 and to Resistor 22.1 via N4; GND 9.1 via N5.
- `18.1` (NPN_Transistor): active component [specificity=low, confidence=0.72] NPN_Transistor 18.1 is described as active component. It is connected to nets N11, N13 and to Resistor 22.2 via N11; GND 9.3 via N13.
- `19.1` (Operational_Amplifier): generic circuit element [specificity=low, confidence=0.55] Operational_Amplifier 19.1 is described as generic circuit element. It is connected to nets N10, N3 and to Battery 2.1 via N3; Resistor 22.2 via N10.
- `2.1` (Battery): power source [specificity=high, confidence=0.98] Battery 2.1 is described as power source. It is connected to nets N1, N3 and to Operational_Amplifier 19.1 via N3; Fuse 8.1 via N1.
- `22.1` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.1 is described as passive component. It is connected to nets N4, N8 and to LED 12.1 via N4; Switch 25.1 via N8; Transformer 28.1 via N8; Capacitor 4.1 via N8; Connector 5.1 via N8.
- `22.2` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.2 is described as passive component. It is connected to nets N10, N11 and to NPN_Transistor 18.1 via N11; Operational_Amplifier 19.1 via N10.
- `25.1` (Switch): active component [specificity=low, confidence=0.72] Switch 25.1 is described as active component. It is connected to nets N2, N8 and to Resistor 22.1 via N8; Transformer 28.1 via N8; Capacitor 4.1 via N8; Connector 5.1 via N8; Fuse 8.1 via N2.
- `28.1` (Transformer): generic circuit element [specificity=low, confidence=0.55] Transformer 28.1 is described as generic circuit element. It is connected to nets N8, N9 and to Resistor 22.1 via N8; Switch 25.1 via N8; Capacitor 4.1 via N8; Connector 5.1 via N8.
- `4.1` (Capacitor): passive component [specificity=medium, confidence=0.76] Capacitor 4.1 is described as passive component. It is connected to nets N6, N8 and to Resistor 22.1 via N8; Switch 25.1 via N8; Transformer 28.1 via N8; Connector 5.1 via N8; Diode 7.1 via N6.
- `5.1` (Connector): generic circuit element [specificity=low, confidence=0.55] Connector 5.1 is described as generic circuit element. It is connected to nets N12, N8 and to Resistor 22.1 via N8; Switch 25.1 via N8; Transformer 28.1 via N8; Capacitor 4.1 via N8.
- `7.1` (Diode): passive component [specificity=medium, confidence=0.76] Diode 7.1 is described as passive component. It is connected to nets N6, N7 and to Capacitor 4.1 via N6; GND 9.2 via N7.
- `8.1` (Fuse): generic circuit element [specificity=low, confidence=0.55] Fuse 8.1 is described as generic circuit element. It is connected to nets N1, N2 and to Battery 2.1 via N1; Switch 25.1 via N2.
- `9.1` (GND): ground reference [specificity=high, confidence=1.00] GND 9.1 is described as ground reference. It is connected to nets N5 and to LED 12.1 via N5.
- `9.2` (GND): ground reference [specificity=high, confidence=1.00] GND 9.2 is described as ground reference. It is connected to nets N7 and to Diode 7.1 via N7.
- `9.3` (GND): ground reference [specificity=high, confidence=1.00] GND 9.3 is described as ground reference. It is connected to nets N13 and to NPN_Transistor 18.1 via N13.

# Net Descriptions
- `N1`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N2`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N3`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N4`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N5`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N6`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N7`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N8`: shared internal branch [specificity=medium, confidence=0.70] Basis: The net behaves like a multi-device internal junction and its terminal semantics are mixed or widely shared.
- `N9`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N10`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N11`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N12`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N13`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.

# Aggregated Relations
- `N1`: N1 is a source connected branch connecting Battery 2.1 positive, Fuse 8.1 terminal t1.
- `N3`: N3 is a source connected branch connecting Operational_Amplifier 19.1 in1, Battery 2.1 negative.
- `N8`: N8 is a shared internal branch connecting Resistor 22.1 terminal t1, Switch 25.1 terminal t2, Transformer 28.1 terminal t1, Capacitor 4.1 terminal t1, Connector 5.1 pin1.
- `N10`: N10 is a local interconnect connecting Operational_Amplifier 19.1 out, Resistor 22.2 terminal t1.
- `N11`: N11 is a local interconnect connecting NPN_Transistor 18.1 base, Resistor 22.2 terminal t2.
- `N13`: N13 is a ground return connecting NPN_Transistor 18.1 emitter, GND 9.3 terminal t1.
- `N2`: N2 is a local interconnect connecting Switch 25.1 terminal t1, Fuse 8.1 terminal t2.
- `N4`: N4 is a local interconnect connecting LED 12.1 anode, Resistor 22.1 terminal t2.

# Functional Paths
- `P1` `ground_to_device_path`: Ground to device path: GND 9.1 -> N5 (ground return) -> LED 12.1 -> N4 (local interconnect) -> Resistor 22.1 -> N8 (shared internal branch) -> Switch 25.1. Confidence: 0.68 (heuristic_inference).
- `P2` `ground_to_device_path`: Ground to device path: GND 9.2 -> N7 (ground return) -> Diode 7.1 -> N6 (local interconnect) -> Capacitor 4.1 -> N8 (shared internal branch) -> Switch 25.1. Confidence: 0.68 (heuristic_inference).
- `P3` `ground_to_device_path`: Ground to device path: GND 9.3 -> N13 (ground return) -> NPN_Transistor 18.1. Confidence: 0.68 (heuristic_inference).

# Structural Patterns
- `high_degree_shared_branch` on `N8`: Net N8 is a shared internal branch touching 5 modeled components.
- `multiple_terminals_same_net` on `28.1`: Transformer 28.1 has terminals 28.1:t1, 28.1:t2 on the same net N8.
- `multiple_terminals_same_net` on `28.1`: Transformer 28.1 has terminals 28.1:t3, 28.1:t4 on the same net N9.
- `multiple_terminals_same_net` on `5.1`: Connector 5.1 has terminals 5.1:pin2, 5.1:pin3 on the same net N12.
- `suspicious_terminal_match` on `18.1:C`: NPN_Transistor 18.1 collector was flagged as a suspicious terminal-to-net match.
- `suspicious_terminal_match` on `19.1:in2`: Operational_Amplifier 19.1 in2 was flagged as a suspicious terminal-to-net match.
- `suspicious_terminal_match` on `5.1:pin4`: Connector 5.1 pin4 was flagged as a suspicious terminal-to-net match.
- `unmatched_terminal` on `18.1:C`: NPN_Transistor 18.1 collector is unmatched.
- `unmatched_terminal` on `19.1:in2`: Operational_Amplifier 19.1 in2 is unmatched.
- `unmatched_terminal` on `5.1:pin4`: Connector 5.1 pin4 is unmatched.

# Terminal Facts
- `12.1:anode`: LED 12.1 terminal anode is connected on net N4 with Resistor 22.1.
- `12.1:cathode`: LED 12.1 terminal cathode is connected on net N5 with GND 9.1.
- `18.1:B`: NPN_Transistor 18.1 terminal B is connected on net N11 with Resistor 22.2.
- `18.1:C`: NPN_Transistor 18.1 terminal C is currently unmatched to any net.
- `18.1:E`: NPN_Transistor 18.1 terminal E is connected on net N13 with GND 9.3.
- `19.1:in1`: Operational_Amplifier 19.1 terminal in1 is connected on net N3 with Battery 2.1.
- `19.1:in2`: Operational_Amplifier 19.1 terminal in2 is currently unmatched to any net.
- `19.1:out`: Operational_Amplifier 19.1 terminal out is connected on net N10 with Resistor 22.2.
- `2.1:positive`: Battery 2.1 terminal positive is connected on net N1 with Fuse 8.1.
- `2.1:negative`: Battery 2.1 terminal negative is connected on net N3 with Operational_Amplifier 19.1.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
