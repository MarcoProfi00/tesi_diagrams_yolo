# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `5` (`5.jpg`) from pipeline variant `topology_v8_component_polarity` was exported from `06_match_terminals_to_nets`.
The topology contains 11 components, 23 terminals, 6 nets, and 23 terminal-to-net connections.
Explicit ground references: GND 9.1.

# Main Branches
- `N2` (shared_internal_branch, importance=medium): Net N2 forms a shared internal branch connecting NPN_Transistor 18.1, Polarized_Capacitor 20.1, Polarized_Capacitor 20.2, Resistor 22.1, Resistor 22.2.
- `N3` (shared_internal_branch, importance=medium): Net N3 forms a shared internal branch connecting LED 12.1, LED 12.2, Resistor 22.2, Resistor 22.3.
- `N5` (shared_internal_branch, importance=medium): Net N5 forms a shared internal branch connecting NPN_Transistor 18.2, Polarized_Capacitor 20.1, Polarized_Capacitor 20.2, Resistor 22.3, Resistor 22.4.

# Component Descriptions
- `12.1` (LED): generic circuit element [specificity=low, confidence=0.55] LED 12.1 is described as generic circuit element. It is connected to nets N1, N3 and to LED 12.2 via N3; Resistor 22.1 via N1; Resistor 22.2 via N3; Resistor 22.3 via N3.
- `12.2` (LED): generic circuit element [specificity=low, confidence=0.55] LED 12.2 is described as generic circuit element. It is connected to nets N3, N6 and to LED 12.1 via N3; Resistor 22.2 via N3; Resistor 22.3 via N3; Resistor 22.4 via N6.
- `18.1` (NPN_Transistor): active component [specificity=low, confidence=0.72] NPN_Transistor 18.1 is described as active component. It is connected to nets N2, N4 and to NPN_Transistor 18.2 via N4; Polarized_Capacitor 20.1 via N2; Polarized_Capacitor 20.2 via N2; Resistor 22.1 via N2; Resistor 22.2 via N2; GND 9.1 via N4.
- `18.2` (NPN_Transistor): active component [specificity=low, confidence=0.72] NPN_Transistor 18.2 is described as active component. It is connected to nets N4, N5 and to NPN_Transistor 18.1 via N4; Polarized_Capacitor 20.1 via N5; Polarized_Capacitor 20.2 via N5; Resistor 22.3 via N5; Resistor 22.4 via N5; GND 9.1 via N4.
- `20.1` (Polarized_Capacitor): generic circuit element [specificity=low, confidence=0.55] Polarized_Capacitor 20.1 is described as generic circuit element. It is connected to nets N2, N5 and to NPN_Transistor 18.1 via N2; NPN_Transistor 18.2 via N5; Polarized_Capacitor 20.2 via N2, N5; Resistor 22.1 via N2; Resistor 22.2 via N2; Resistor 22.3 via N5; Resistor 22.4 via N5.
- `20.2` (Polarized_Capacitor): generic circuit element [specificity=low, confidence=0.55] Polarized_Capacitor 20.2 is described as generic circuit element. It is connected to nets N2, N5 and to NPN_Transistor 18.1 via N2; NPN_Transistor 18.2 via N5; Polarized_Capacitor 20.1 via N2, N5; Resistor 22.1 via N2; Resistor 22.2 via N2; Resistor 22.3 via N5; Resistor 22.4 via N5.
- `22.1` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.1 is described as passive component. It is connected to nets N1, N2 and to LED 12.1 via N1; NPN_Transistor 18.1 via N2; Polarized_Capacitor 20.1 via N2; Polarized_Capacitor 20.2 via N2; Resistor 22.2 via N2.
- `22.2` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.2 is described as passive component. It is connected to nets N2, N3 and to LED 12.1 via N3; LED 12.2 via N3; NPN_Transistor 18.1 via N2; Polarized_Capacitor 20.1 via N2; Polarized_Capacitor 20.2 via N2; Resistor 22.1 via N2; Resistor 22.3 via N3.
- `22.3` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.3 is described as passive component. It is connected to nets N3, N5 and to LED 12.1 via N3; LED 12.2 via N3; NPN_Transistor 18.2 via N5; Polarized_Capacitor 20.1 via N5; Polarized_Capacitor 20.2 via N5; Resistor 22.2 via N3; Resistor 22.4 via N5.
- `22.4` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.4 is described as passive component. It is connected to nets N5, N6 and to LED 12.2 via N6; NPN_Transistor 18.2 via N5; Polarized_Capacitor 20.1 via N5; Polarized_Capacitor 20.2 via N5; Resistor 22.3 via N5.
- `9.1` (GND): ground reference [specificity=high, confidence=1.00] GND 9.1 is described as ground reference. It is connected to nets N4 and to NPN_Transistor 18.1 via N4; NPN_Transistor 18.2 via N4.

# Net Descriptions
- `N1`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N2`: shared internal branch [specificity=medium, confidence=0.70] Basis: The net behaves like a multi-device internal junction and its terminal semantics are mixed or widely shared.
- `N3`: shared internal branch [specificity=medium, confidence=0.70] Basis: The net behaves like a multi-device internal junction and its terminal semantics are mixed or widely shared.
- `N4`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N5`: shared internal branch [specificity=medium, confidence=0.70] Basis: The net behaves like a multi-device internal junction and its terminal semantics are mixed or widely shared.
- `N6`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.

# Aggregated Relations
- `N2`: N2 is a shared internal branch connecting NPN_Transistor 18.1 base, Polarized_Capacitor 20.1 positive, Polarized_Capacitor 20.2 negative, Resistor 22.1 terminal t2, Resistor 22.2 terminal t2.
- `N3`: N3 is a shared internal branch connecting LED 12.1 anode, LED 12.2 anode, Resistor 22.2 terminal t1, Resistor 22.3 terminal t1.
- `N5`: N5 is a shared internal branch connecting NPN_Transistor 18.2 base, Polarized_Capacitor 20.1 negative, Polarized_Capacitor 20.2 positive, Resistor 22.3 terminal t2, Resistor 22.4 terminal t2.
- `N1`: N1 is a local interconnect connecting LED 12.1 cathode, Resistor 22.1 terminal t1.
- `N4`: N4 is a ground return connecting NPN_Transistor 18.1 emitter, NPN_Transistor 18.2 emitter, GND 9.1 terminal t1.
- `N6`: N6 is a local interconnect connecting LED 12.2 cathode, Resistor 22.4 terminal t1.

# Functional Paths
- `P1` `ground_to_device_path`: Ground to device path: GND 9.1 -> N4 (ground return) -> NPN_Transistor 18.1. Confidence: 0.68 (heuristic_inference).

# Structural Patterns
- `high_degree_shared_branch` on `N2`: Net N2 is a shared internal branch touching 5 modeled components.
- `high_degree_shared_branch` on `N5`: Net N5 is a shared internal branch touching 5 modeled components.
- `multiple_terminals_same_net` on `18.1`: NPN_Transistor 18.1 has terminals 18.1:B, 18.1:C on the same net N2.
- `multiple_terminals_same_net` on `18.2`: NPN_Transistor 18.2 has terminals 18.2:B, 18.2:C on the same net N5.

# Terminal Facts
- `12.1:anode`: LED 12.1 terminal anode is connected on net N3 with LED 12.2, Resistor 22.2, Resistor 22.3.
- `12.1:cathode`: LED 12.1 terminal cathode is connected on net N1 with Resistor 22.1.
- `12.2:anode`: LED 12.2 terminal anode is connected on net N3 with LED 12.1, Resistor 22.2, Resistor 22.3.
- `12.2:cathode`: LED 12.2 terminal cathode is connected on net N6 with Resistor 22.4.
- `18.1:B`: NPN_Transistor 18.1 terminal B is connected on net N2 with NPN_Transistor 18.1, Polarized_Capacitor 20.1, Polarized_Capacitor 20.2, Resistor 22.1, Resistor 22.2.
- `18.1:C`: NPN_Transistor 18.1 terminal C is connected on net N2 with NPN_Transistor 18.1, Polarized_Capacitor 20.1, Polarized_Capacitor 20.2, Resistor 22.1, Resistor 22.2.
- `18.1:E`: NPN_Transistor 18.1 terminal E is connected on net N4 with GND 9.1, NPN_Transistor 18.2.
- `18.2:B`: NPN_Transistor 18.2 terminal B is connected on net N5 with NPN_Transistor 18.2, Polarized_Capacitor 20.1, Polarized_Capacitor 20.2, Resistor 22.3, Resistor 22.4.
- `18.2:C`: NPN_Transistor 18.2 terminal C is connected on net N5 with NPN_Transistor 18.2, Polarized_Capacitor 20.1, Polarized_Capacitor 20.2, Resistor 22.3, Resistor 22.4.
- `18.2:E`: NPN_Transistor 18.2 terminal E is connected on net N4 with GND 9.1, NPN_Transistor 18.1.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
