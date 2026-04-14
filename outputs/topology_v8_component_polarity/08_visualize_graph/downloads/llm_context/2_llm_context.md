# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `2` (`2.jpg`) from pipeline variant `topology_v8_component_polarity` was exported from `06_match_terminals_to_nets`.
The topology contains 16 components, 27 terminals, 7 nets, and 27 terminal-to-net connections.
Explicit ground references: GND 9.1, GND 9.2, GND 9.3, GND 9.4.
Possible external outputs or bridge interfaces: Terminal 26.3.

# Main Branches
- `N1` (external_interface_branch, importance=high): Net N1 forms an external interface branch connecting Polarized_Capacitor 20.1, Terminal 26.1.
- `N4` (external_interface_branch, importance=high): Net N4 forms an external interface branch connecting Resistor 22.2, Resistor 22.3, Terminal 26.2.
- `N6` (shared_internal_branch, importance=medium): Net N6 forms a shared internal branch connecting NPN_Transistor 18.1, Polarized_Capacitor 20.3, Resistor 22.3, Resistor 22.5, Terminal 26.3.

# Component Descriptions
- `18.1` (NPN_Transistor): active component [specificity=low, confidence=0.72] NPN_Transistor 18.1 is described as active component. It is connected to nets N2, N6 and to Polarized_Capacitor 20.1 via N2; Polarized_Capacitor 20.2 via N2; Polarized_Capacitor 20.3 via N6; Resistor 22.1 via N2; Resistor 22.2 via N2; Resistor 22.3 via N6; Resistor 22.4 via N2; Resistor 22.5 via N6; Terminal 26.3 via N6; GND 9.1 via N2.
- `20.1` (Polarized_Capacitor): generic circuit element [specificity=low, confidence=0.55] Polarized_Capacitor 20.1 is described as generic circuit element. It is connected to nets N1, N2 and to NPN_Transistor 18.1 via N2; Polarized_Capacitor 20.2 via N2; Resistor 22.1 via N2; Resistor 22.2 via N2; Resistor 22.4 via N2; Terminal 26.1 via N1; GND 9.1 via N2.
- `20.2` (Polarized_Capacitor): generic circuit element [specificity=low, confidence=0.55] Polarized_Capacitor 20.2 is described as generic circuit element. It is connected to nets N2 and to NPN_Transistor 18.1 via N2; Polarized_Capacitor 20.1 via N2; Resistor 22.1 via N2; Resistor 22.2 via N2; Resistor 22.4 via N2; GND 9.1 via N2.
- `20.3` (Polarized_Capacitor): generic circuit element [specificity=low, confidence=0.55] Polarized_Capacitor 20.3 is described as generic circuit element. It is connected to nets N6 and to NPN_Transistor 18.1 via N6; Resistor 22.3 via N6; Resistor 22.5 via N6; Terminal 26.3 via N6.
- `22.1` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.1 is described as passive component. It is connected to nets N2, N3 and to NPN_Transistor 18.1 via N2; Polarized_Capacitor 20.1 via N2; Polarized_Capacitor 20.2 via N2; Resistor 22.2 via N2; Resistor 22.4 via N2; GND 9.1 via N2; GND 9.2 via N3.
- `22.2` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.2 is described as passive component. It is connected to nets N2, N4 and to NPN_Transistor 18.1 via N2; Polarized_Capacitor 20.1 via N2; Polarized_Capacitor 20.2 via N2; Resistor 22.1 via N2; Resistor 22.3 via N4; Resistor 22.4 via N2; Terminal 26.2 via N4; GND 9.1 via N2.
- `22.3` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.3 is described as passive component. It is connected to nets N4, N6 and to NPN_Transistor 18.1 via N6; Polarized_Capacitor 20.3 via N6; Resistor 22.2 via N4; Resistor 22.5 via N6; Terminal 26.2 via N4; Terminal 26.3 via N6.
- `22.4` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.4 is described as passive component. It is connected to nets N2, N5 and to NPN_Transistor 18.1 via N2; Polarized_Capacitor 20.1 via N2; Polarized_Capacitor 20.2 via N2; Resistor 22.1 via N2; Resistor 22.2 via N2; GND 9.1 via N2; GND 9.3 via N5.
- `22.5` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.5 is described as passive component. It is connected to nets N6, N7 and to NPN_Transistor 18.1 via N6; Polarized_Capacitor 20.3 via N6; Resistor 22.3 via N6; Terminal 26.3 via N6; GND 9.4 via N7.
- `26.1` (Terminal): external interface [specificity=low, confidence=0.68] Terminal 26.1 is described as external interface. It is connected to nets N1 and to Polarized_Capacitor 20.1 via N1.
- `26.2` (Terminal): external interface [specificity=low, confidence=0.68] Terminal 26.2 is described as external interface. It is connected to nets N4 and to Resistor 22.2 via N4; Resistor 22.3 via N4.
- `26.3` (Terminal): external interface [specificity=low, confidence=0.74] Terminal 26.3 is described as external interface. It is connected to nets N6 and to NPN_Transistor 18.1 via N6; Polarized_Capacitor 20.3 via N6; Resistor 22.3 via N6; Resistor 22.5 via N6.
- `9.1` (GND): ground reference [specificity=high, confidence=1.00] GND 9.1 is described as ground reference. It is connected to nets N2 and to NPN_Transistor 18.1 via N2; Polarized_Capacitor 20.1 via N2; Polarized_Capacitor 20.2 via N2; Resistor 22.1 via N2; Resistor 22.2 via N2; Resistor 22.4 via N2.
- `9.2` (GND): ground reference [specificity=high, confidence=1.00] GND 9.2 is described as ground reference. It is connected to nets N3 and to Resistor 22.1 via N3.
- `9.3` (GND): ground reference [specificity=high, confidence=1.00] GND 9.3 is described as ground reference. It is connected to nets N5 and to Resistor 22.4 via N5.
- `9.4` (GND): ground reference [specificity=high, confidence=1.00] GND 9.4 is described as ground reference. It is connected to nets N7 and to Resistor 22.5 via N7.

# Net Descriptions
- `N1`: external interface branch [specificity=low, confidence=0.68] Basis: The net reaches at least one explicit external interface.
- `N2`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N3`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N4`: external interface branch [specificity=low, confidence=0.68] Basis: The net reaches at least one explicit external interface.
- `N5`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N6`: shared internal branch [specificity=medium, confidence=0.70] Basis: The net behaves like a multi-device internal junction and its terminal semantics are mixed or widely shared.
- `N7`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.

# Aggregated Relations
- `N1`: N1 is a external interface branch connecting Polarized_Capacitor 20.1 negative, Terminal 26.1 terminal t1.
- `N4`: N4 is a external interface branch connecting Resistor 22.2 terminal t1, Resistor 22.3 terminal t1, Terminal 26.2 terminal t1.
- `N2`: N2 is a ground return connecting NPN_Transistor 18.1 base, Polarized_Capacitor 20.1 positive, Polarized_Capacitor 20.2 negative, Resistor 22.1 terminal t1, Resistor 22.2 terminal t2, Resistor 22.4 terminal t1, GND 9.1 terminal t1.
- `N6`: N6 is a shared internal branch connecting NPN_Transistor 18.1 collector, Polarized_Capacitor 20.3 negative, Resistor 22.3 terminal t2, Resistor 22.5 terminal t1, Terminal 26.3 terminal t1.
- `N3`: N3 is a ground return connecting Resistor 22.1 terminal t2, GND 9.2 terminal t1.
- `N5`: N5 is a ground return connecting Resistor 22.4 terminal t2, GND 9.3 terminal t1.
- `N7`: N7 is a ground return connecting Resistor 22.5 terminal t2, GND 9.4 terminal t1.

# Functional Paths
- `P1` `device_to_interface_path`: Device to interface path: NPN_Transistor 18.1 -> N6 (shared internal branch) -> Terminal 26.3. Confidence: 0.74 (heuristic_inference).
- `P2` `ground_to_device_path`: Ground to device path: GND 9.1 -> N2 (ground return) -> NPN_Transistor 18.1. Confidence: 0.68 (heuristic_inference).
- `P3` `ground_to_device_path`: Ground to device path: GND 9.2 -> N3 (ground return) -> Resistor 22.1 -> N2 (ground return) -> NPN_Transistor 18.1. Confidence: 0.68 (heuristic_inference).
- `P4` `ground_to_device_path`: Ground to device path: GND 9.3 -> N5 (ground return) -> Resistor 22.4 -> N2 (ground return) -> NPN_Transistor 18.1. Confidence: 0.68 (heuristic_inference).
- `P5` `ground_to_device_path`: Ground to device path: GND 9.4 -> N7 (ground return) -> Resistor 22.5 -> N6 (shared internal branch) -> NPN_Transistor 18.1. Confidence: 0.68 (heuristic_inference).

# Structural Patterns
- `high_degree_shared_branch` on `N6`: Net N6 is a shared internal branch touching 5 modeled components.
- `multiple_terminals_same_net` on `18.1`: NPN_Transistor 18.1 has terminals 18.1:B, 18.1:E on the same net N2.
- `multiple_terminals_same_net` on `20.2`: Polarized_Capacitor 20.2 has terminals 20.2:negative, 20.2:positive on the same net N2.
- `multiple_terminals_same_net` on `20.3`: Polarized_Capacitor 20.3 has terminals 20.3:positive, 20.3:negative on the same net N6.
- `multiple_terminals_same_net` on `26.3`: Terminal 26.3 has terminals 26.3:t1, 26.3:t2 on the same net N6.

# Terminal Facts
- `18.1:B`: NPN_Transistor 18.1 terminal B is connected on net N2 with GND 9.1, NPN_Transistor 18.1, Polarized_Capacitor 20.1, Polarized_Capacitor 20.2, Resistor 22.1, Resistor 22.2, Resistor 22.4.
- `18.1:C`: NPN_Transistor 18.1 terminal C is connected on net N6 with Polarized_Capacitor 20.3, Resistor 22.3, Resistor 22.5, Terminal 26.3.
- `18.1:E`: NPN_Transistor 18.1 terminal E is connected on net N2 with GND 9.1, NPN_Transistor 18.1, Polarized_Capacitor 20.1, Polarized_Capacitor 20.2, Resistor 22.1, Resistor 22.2, Resistor 22.4.
- `20.1:negative`: Polarized_Capacitor 20.1 terminal negative is connected on net N1 with Terminal 26.1.
- `20.1:positive`: Polarized_Capacitor 20.1 terminal positive is connected on net N2 with GND 9.1, NPN_Transistor 18.1, Polarized_Capacitor 20.2, Resistor 22.1, Resistor 22.2, Resistor 22.4.
- `20.2:negative`: Polarized_Capacitor 20.2 terminal negative is connected on net N2 with GND 9.1, NPN_Transistor 18.1, Polarized_Capacitor 20.1, Polarized_Capacitor 20.2, Resistor 22.1, Resistor 22.2, Resistor 22.4.
- `20.2:positive`: Polarized_Capacitor 20.2 terminal positive is connected on net N2 with GND 9.1, NPN_Transistor 18.1, Polarized_Capacitor 20.1, Polarized_Capacitor 20.2, Resistor 22.1, Resistor 22.2, Resistor 22.4.
- `20.3:positive`: Polarized_Capacitor 20.3 terminal positive is connected on net N6 with NPN_Transistor 18.1, Polarized_Capacitor 20.3, Resistor 22.3, Resistor 22.5, Terminal 26.3.
- `20.3:negative`: Polarized_Capacitor 20.3 terminal negative is connected on net N6 with NPN_Transistor 18.1, Polarized_Capacitor 20.3, Resistor 22.3, Resistor 22.5, Terminal 26.3.
- `22.1:t1`: Resistor 22.1 terminal t1 is connected on net N2 with GND 9.1, NPN_Transistor 18.1, Polarized_Capacitor 20.1, Polarized_Capacitor 20.2, Resistor 22.2, Resistor 22.4.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
