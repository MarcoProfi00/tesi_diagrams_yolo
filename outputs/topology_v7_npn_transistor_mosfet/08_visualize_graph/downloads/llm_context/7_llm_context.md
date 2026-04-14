# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `7` (`7.jpg`) from pipeline variant `topology_v7_npn_transistor_mosfet` was exported from `06_match_terminals_to_nets`.
The topology contains 10 components, 26 terminals, 7 nets, and 26 terminal-to-net connections.
Explicit ground references: GND 9.1.

# Main Branches
- `N1` (shared_internal_branch, importance=medium): Net N1 forms a shared internal branch connecting Mosfet 16.1, NPN_Transistor 18.1, Operational_Amplifier 19.1.
- `N2` (shared_internal_branch, importance=medium): Net N2 forms a shared internal branch connecting Mosfet 16.2, Operational_Amplifier 19.1, Resistor 22.1.
- `N3` (shared_internal_branch, importance=medium): Net N3 forms a shared internal branch connecting Mosfet 16.1, Mosfet 16.2, Mosfet 16.3, Operational_Amplifier 19.1.

# Component Descriptions
- `16.1` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.1 is described as active component. It is connected to nets N1, N3 and to Mosfet 16.2 via N3; Mosfet 16.3 via N3; NPN_Transistor 18.1 via N1; Operational_Amplifier 19.1 via N1, N3.
- `16.2` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.2 is described as active component. It is connected to nets N2, N3 and to Mosfet 16.1 via N3; Mosfet 16.3 via N3; Operational_Amplifier 19.1 via N2, N3; Resistor 22.1 via N2.
- `16.3` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.3 is described as active component. It is connected to nets N3, N7 and to Mosfet 16.1 via N3; Mosfet 16.2 via N3; Operational_Amplifier 19.1 via N3; Resistor 22.2 via N7.
- `18.1` (NPN_Transistor): active component [specificity=low, confidence=0.72] NPN_Transistor 18.1 is described as active component. It is connected to nets N1, N4 and to Mosfet 16.1 via N1; NPN_Transistor 18.2 via N4; NPN_Transistor 18.3 via N4; Operational_Amplifier 19.1 via N1; GND 9.1 via N4.
- `18.2` (NPN_Transistor): active component [specificity=low, confidence=0.72] NPN_Transistor 18.2 is described as active component. It is connected to nets N4, N5 and to NPN_Transistor 18.1 via N4; NPN_Transistor 18.3 via N4; Resistor 22.1 via N5; GND 9.1 via N4.
- `18.3` (NPN_Transistor): active component [specificity=low, confidence=0.72] NPN_Transistor 18.3 is described as active component. It is connected to nets N4, N6 and to NPN_Transistor 18.1 via N4; NPN_Transistor 18.2 via N4; Resistor 22.2 via N6; GND 9.1 via N4.
- `19.1` (Operational_Amplifier): generic circuit element [specificity=low, confidence=0.55] Operational_Amplifier 19.1 is described as generic circuit element. It is connected to nets N1, N2, N3 and to Mosfet 16.1 via N1, N3; Mosfet 16.2 via N2, N3; Mosfet 16.3 via N3; NPN_Transistor 18.1 via N1; Resistor 22.1 via N2.
- `22.1` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.1 is described as passive component. It is connected to nets N2, N5 and to Mosfet 16.2 via N2; NPN_Transistor 18.2 via N5; Operational_Amplifier 19.1 via N2.
- `22.2` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.2 is described as passive component. It is connected to nets N6, N7 and to Mosfet 16.3 via N7; NPN_Transistor 18.3 via N6.
- `9.1` (GND): ground reference [specificity=high, confidence=1.00] GND 9.1 is described as ground reference. It is connected to nets N4 and to NPN_Transistor 18.1 via N4; NPN_Transistor 18.2 via N4; NPN_Transistor 18.3 via N4.

# Net Descriptions
- `N1`: shared internal branch [specificity=medium, confidence=0.72] Basis: The net behaves like a shared internal junction between multiple components.
- `N2`: shared internal branch [specificity=medium, confidence=0.72] Basis: The net behaves like a shared internal junction between multiple components.
- `N3`: shared internal branch [specificity=medium, confidence=0.70] Basis: The net behaves like a multi-device internal junction and its terminal semantics are mixed or widely shared.
- `N4`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N5`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N6`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N7`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.

# Aggregated Relations
- `N1`: N1 is a shared internal branch connecting Mosfet 16.1 terminal t3, NPN_Transistor 18.1 emitter, Operational_Amplifier 19.1 in1.
- `N2`: N2 is a shared internal branch connecting Mosfet 16.2 terminal t3, Operational_Amplifier 19.1 in2, Resistor 22.1 terminal t1.
- `N3`: N3 is a shared internal branch connecting Mosfet 16.1 terminal t2, Mosfet 16.2 terminal t2, Mosfet 16.3 terminal t2, Operational_Amplifier 19.1 out.
- `N4`: N4 is a ground return connecting NPN_Transistor 18.1 base, NPN_Transistor 18.2 base, NPN_Transistor 18.3 base, GND 9.1 terminal t1.
- `N5`: N5 is a local interconnect connecting NPN_Transistor 18.2 emitter, Resistor 22.1 terminal t2.
- `N6`: N6 is a local interconnect connecting NPN_Transistor 18.3 emitter, Resistor 22.2 terminal t2.
- `N7`: N7 is a local interconnect connecting Mosfet 16.3 terminal t3, Resistor 22.2 terminal t1.

# Functional Paths
- `P1` `ground_to_device_path`: Ground to device path: GND 9.1 -> N4 (ground return) -> NPN_Transistor 18.1. Confidence: 0.68 (heuristic_inference).

# Structural Patterns
- `multiple_terminals_same_net` on `16.1`: Mosfet 16.1 has terminals 16.1:G, 16.1:t2 on the same net N3.
- `multiple_terminals_same_net` on `16.2`: Mosfet 16.2 has terminals 16.2:G, 16.2:t2 on the same net N3.
- `multiple_terminals_same_net` on `16.3`: Mosfet 16.3 has terminals 16.3:G, 16.3:t2 on the same net N3.
- `multiple_terminals_same_net` on `18.1`: NPN_Transistor 18.1 has terminals 18.1:B, 18.1:C on the same net N4.
- `multiple_terminals_same_net` on `18.2`: NPN_Transistor 18.2 has terminals 18.2:B, 18.2:C on the same net N4.
- `multiple_terminals_same_net` on `18.3`: NPN_Transistor 18.3 has terminals 18.3:B, 18.3:C on the same net N4.

# Terminal Facts
- `16.1:G`: Mosfet 16.1 terminal G is connected on net N3 with Mosfet 16.1, Mosfet 16.2, Mosfet 16.3, Operational_Amplifier 19.1.
- `16.1:t2`: Mosfet 16.1 terminal t2 is connected on net N3 with Mosfet 16.1, Mosfet 16.2, Mosfet 16.3, Operational_Amplifier 19.1.
- `16.1:t3`: Mosfet 16.1 terminal t3 is connected on net N1 with NPN_Transistor 18.1, Operational_Amplifier 19.1.
- `16.2:G`: Mosfet 16.2 terminal G is connected on net N3 with Mosfet 16.1, Mosfet 16.2, Mosfet 16.3, Operational_Amplifier 19.1.
- `16.2:t2`: Mosfet 16.2 terminal t2 is connected on net N3 with Mosfet 16.1, Mosfet 16.2, Mosfet 16.3, Operational_Amplifier 19.1.
- `16.2:t3`: Mosfet 16.2 terminal t3 is connected on net N2 with Operational_Amplifier 19.1, Resistor 22.1.
- `16.3:G`: Mosfet 16.3 terminal G is connected on net N3 with Mosfet 16.1, Mosfet 16.2, Mosfet 16.3, Operational_Amplifier 19.1.
- `16.3:t2`: Mosfet 16.3 terminal t2 is connected on net N3 with Mosfet 16.1, Mosfet 16.2, Mosfet 16.3, Operational_Amplifier 19.1.
- `16.3:t3`: Mosfet 16.3 terminal t3 is connected on net N7 with Resistor 22.2.
- `18.1:B`: NPN_Transistor 18.1 terminal B is connected on net N4 with GND 9.1, NPN_Transistor 18.1, NPN_Transistor 18.2, NPN_Transistor 18.3.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
