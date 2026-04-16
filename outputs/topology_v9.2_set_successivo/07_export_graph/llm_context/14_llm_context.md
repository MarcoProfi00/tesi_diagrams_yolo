# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `14` (`14.jpg`) from pipeline variant `topology_v9.2_set_successivo` was exported from `06_match_terminals_to_nets`.
The topology contains 16 components, 32 terminals, 9 nets, and 32 terminal-to-net connections.
Explicit power sources: Battery 2.1.
Explicit ground references: GND 9.1.

# Main Branches
- `N5` (source_connected_branch, importance=high): Net N5 forms a source connected branch connecting NPN_Transistor 18.1, NPN_Transistor 18.2, Battery 2.1, Polarized_Capacitor 20.1, Polarized_Capacitor 20.4, Resistor 22.1, Resistor 22.2, Resistor 22.3, Switch 25.1.
- `N4` (shared_internal_branch, importance=medium): Net N4 forms a shared internal branch connecting NPN_Transistor 18.1, Polarized_Capacitor 20.1, Polarized_Capacitor 20.2, Resistor 22.1, Diode 7.1.
- `N6` (shared_internal_branch, importance=medium): Net N6 forms a shared internal branch connecting NPN_Transistor 18.1, NPN_Transistor 18.2, Polarized_Capacitor 20.3, Resistor 22.2, Resistor 22.3.
- `N1` (single_terminal_stub, importance=low): Net N1 forms a single terminal stub connecting Inductor 10.1.
- `N3` (single_terminal_stub, importance=low): Net N3 forms a single terminal stub connecting Antenna 1.1.
- `N7` (single_terminal_stub, importance=low): Net N7 forms a single terminal stub connecting NPN_Transistor 18.2.

# Component Descriptions
- `1.1` (Antenna): generic circuit element [specificity=low, confidence=0.55] Antenna 1.1 is described as generic circuit element. It is connected to nets N3 and to no other modeled components.
- `10.1` (Inductor): passive component [specificity=medium, confidence=0.76] Inductor 10.1 is described as passive component. It is connected to nets N1, N2 and to GND 9.1 via N2.
- `18.1` (NPN_Transistor): active component [specificity=low, confidence=0.72] NPN_Transistor 18.1 is described as active component. It is connected to nets N4, N5, N6 and to NPN_Transistor 18.2 via N5, N6; Battery 2.1 via N5; Polarized_Capacitor 20.1 via N4, N5; Polarized_Capacitor 20.2 via N4; Polarized_Capacitor 20.3 via N6; Polarized_Capacitor 20.4 via N5; Resistor 22.1 via N4, N5; Resistor 22.2 via N5, N6; Resistor 22.3 via N5, N6; Switch 25.1 via N5; Diode 7.1 via N4.
- `18.2` (NPN_Transistor): active component [specificity=low, confidence=0.72] NPN_Transistor 18.2 is described as active component. It is connected to nets N5, N6, N7 and to NPN_Transistor 18.1 via N5, N6; Battery 2.1 via N5; Polarized_Capacitor 20.1 via N5; Polarized_Capacitor 20.3 via N6; Polarized_Capacitor 20.4 via N5; Resistor 22.1 via N5; Resistor 22.2 via N5, N6; Resistor 22.3 via N5, N6; Switch 25.1 via N5.
- `2.1` (Battery): power source [specificity=high, confidence=0.98] Battery 2.1 is described as power source. It is connected to nets N5 and to NPN_Transistor 18.1 via N5; NPN_Transistor 18.2 via N5; Polarized_Capacitor 20.1 via N5; Polarized_Capacitor 20.4 via N5; Resistor 22.1 via N5; Resistor 22.2 via N5; Resistor 22.3 via N5; Switch 25.1 via N5.
- `20.1` (Polarized_Capacitor): generic circuit element [specificity=low, confidence=0.55] Polarized_Capacitor 20.1 is described as generic circuit element. It is connected to nets N4, N5 and to NPN_Transistor 18.1 via N4, N5; NPN_Transistor 18.2 via N5; Battery 2.1 via N5; Polarized_Capacitor 20.2 via N4; Polarized_Capacitor 20.4 via N5; Resistor 22.1 via N4, N5; Resistor 22.2 via N5; Resistor 22.3 via N5; Switch 25.1 via N5; Diode 7.1 via N4.
- `20.2` (Polarized_Capacitor): generic circuit element [specificity=low, confidence=0.55] Polarized_Capacitor 20.2 is described as generic circuit element. It is connected to nets N4 and to NPN_Transistor 18.1 via N4; Polarized_Capacitor 20.1 via N4; Resistor 22.1 via N4; Diode 7.1 via N4.
- `20.3` (Polarized_Capacitor): generic circuit element [specificity=low, confidence=0.55] Polarized_Capacitor 20.3 is described as generic circuit element. It is connected to nets N6 and to NPN_Transistor 18.1 via N6; NPN_Transistor 18.2 via N6; Resistor 22.2 via N6; Resistor 22.3 via N6.
- `20.4` (Polarized_Capacitor): generic circuit element [specificity=low, confidence=0.55] Polarized_Capacitor 20.4 is described as generic circuit element. It is connected to nets N5, N8 and to NPN_Transistor 18.1 via N5; NPN_Transistor 18.2 via N5; Battery 2.1 via N5; Polarized_Capacitor 20.1 via N5; Resistor 22.1 via N5; Resistor 22.2 via N5; Resistor 22.3 via N5; Switch 25.1 via N5; Breaker 3.1 via N8.
- `22.1` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.1 is described as passive component. It is connected to nets N4, N5 and to NPN_Transistor 18.1 via N4, N5; NPN_Transistor 18.2 via N5; Battery 2.1 via N5; Polarized_Capacitor 20.1 via N4, N5; Polarized_Capacitor 20.2 via N4; Polarized_Capacitor 20.4 via N5; Resistor 22.2 via N5; Resistor 22.3 via N5; Switch 25.1 via N5; Diode 7.1 via N4.
- `22.2` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.2 is described as passive component. It is connected to nets N5, N6 and to NPN_Transistor 18.1 via N5, N6; NPN_Transistor 18.2 via N5, N6; Battery 2.1 via N5; Polarized_Capacitor 20.1 via N5; Polarized_Capacitor 20.3 via N6; Polarized_Capacitor 20.4 via N5; Resistor 22.1 via N5; Resistor 22.3 via N5, N6; Switch 25.1 via N5.
- `22.3` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.3 is described as passive component. It is connected to nets N5, N6 and to NPN_Transistor 18.1 via N5, N6; NPN_Transistor 18.2 via N5, N6; Battery 2.1 via N5; Polarized_Capacitor 20.1 via N5; Polarized_Capacitor 20.3 via N6; Polarized_Capacitor 20.4 via N5; Resistor 22.1 via N5; Resistor 22.2 via N5, N6; Switch 25.1 via N5.
- `25.1` (Switch): active component [specificity=low, confidence=0.72] Switch 25.1 is described as active component. It is connected to nets N5 and to NPN_Transistor 18.1 via N5; NPN_Transistor 18.2 via N5; Battery 2.1 via N5; Polarized_Capacitor 20.1 via N5; Polarized_Capacitor 20.4 via N5; Resistor 22.1 via N5; Resistor 22.2 via N5; Resistor 22.3 via N5.
- `3.1` (Breaker): generic circuit element [specificity=low, confidence=0.55] Breaker 3.1 is described as generic circuit element. It is connected to nets N8, N9 and to Polarized_Capacitor 20.4 via N8.
- `7.1` (Diode): passive component [specificity=medium, confidence=0.76] Diode 7.1 is described as passive component. It is connected to nets N4 and to NPN_Transistor 18.1 via N4; Polarized_Capacitor 20.1 via N4; Polarized_Capacitor 20.2 via N4; Resistor 22.1 via N4.
- `9.1` (GND): ground reference [specificity=high, confidence=1.00] GND 9.1 is described as ground reference. It is connected to nets N2 and to Inductor 10.1 via N2.

# Net Descriptions
- `N1`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N2`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N3`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N4`: shared internal branch [specificity=medium, confidence=0.70] Basis: The net behaves like a multi-device internal junction and its terminal semantics are mixed or widely shared.
- `N5`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N6`: shared internal branch [specificity=medium, confidence=0.70] Basis: The net behaves like a multi-device internal junction and its terminal semantics are mixed or widely shared.
- `N7`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N8`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N9`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.

# Aggregated Relations
- `N5`: N5 is a source connected branch connecting NPN_Transistor 18.1 emitter, NPN_Transistor 18.2 emitter, Battery 2.1 negative, Polarized_Capacitor 20.1 negative, Polarized_Capacitor 20.4 negative, Resistor 22.1 terminal t2, Resistor 22.2 terminal t2, Resistor 22.3 terminal t2, Switch 25.1 terminal t1.
- `N4`: N4 is a shared internal branch connecting NPN_Transistor 18.1 base, Polarized_Capacitor 20.1 positive, Polarized_Capacitor 20.2 negative, Resistor 22.1 terminal t1, Diode 7.1 anode.
- `N6`: N6 is a shared internal branch connecting NPN_Transistor 18.1 collector, NPN_Transistor 18.2 base, Polarized_Capacitor 20.3 negative, Resistor 22.2 terminal t1, Resistor 22.3 terminal t1.
- `N2`: N2 is a ground return connecting Inductor 10.1 terminal t2, GND 9.1 terminal t1.
- `N8`: N8 is a single terminal stub connecting Polarized_Capacitor 20.4 positive, Breaker 3.1 terminal t1.

# Functional Paths
- No functional path summary was produced from the current topology.

# Structural Patterns
- `high_degree_shared_branch` on `N4`: Net N4 is a shared internal branch touching 5 modeled components.
- `high_degree_shared_branch` on `N6`: Net N6 is a shared internal branch touching 5 modeled components.
- `multiple_terminals_same_net` on `2.1`: Battery 2.1 has terminals 2.1:positive, 2.1:negative on the same net N5.
- `multiple_terminals_same_net` on `20.2`: Polarized_Capacitor 20.2 has terminals 20.2:positive, 20.2:negative on the same net N4.
- `multiple_terminals_same_net` on `20.3`: Polarized_Capacitor 20.3 has terminals 20.3:positive, 20.3:negative on the same net N6.
- `multiple_terminals_same_net` on `25.1`: Switch 25.1 has terminals 25.1:t1, 25.1:t2 on the same net N5.
- `multiple_terminals_same_net` on `7.1`: Diode 7.1 has terminals 7.1:anode, 7.1:cathode on the same net N4.
- `single_terminal_stub` on `N1`: Net N1 currently touches only Inductor 10.1 terminal t1.
- `single_terminal_stub` on `N3`: Net N3 currently touches only Antenna 1.1 terminal t1.
- `single_terminal_stub` on `N7`: Net N7 currently touches only NPN_Transistor 18.2 collector.

# Terminal Facts
- `1.1:t1`: Antenna 1.1 terminal t1 is the only modeled terminal on net N3.
- `10.1:t1`: Inductor 10.1 terminal t1 is the only modeled terminal on net N1.
- `10.1:t2`: Inductor 10.1 terminal t2 is connected on net N2 with GND 9.1.
- `18.1:B`: NPN_Transistor 18.1 terminal B is connected on net N4 with Diode 7.1, Polarized_Capacitor 20.1, Polarized_Capacitor 20.2, Resistor 22.1.
- `18.1:C`: NPN_Transistor 18.1 terminal C is connected on net N6 with NPN_Transistor 18.2, Polarized_Capacitor 20.3, Resistor 22.2, Resistor 22.3.
- `18.1:E`: NPN_Transistor 18.1 terminal E is connected on net N5 with Battery 2.1, NPN_Transistor 18.2, Polarized_Capacitor 20.1, Polarized_Capacitor 20.4, Resistor 22.1, Resistor 22.2, Resistor 22.3, Switch 25.1.
- `18.2:B`: NPN_Transistor 18.2 terminal B is connected on net N6 with NPN_Transistor 18.1, Polarized_Capacitor 20.3, Resistor 22.2, Resistor 22.3.
- `18.2:C`: NPN_Transistor 18.2 terminal C is the only modeled terminal on net N7.
- `18.2:E`: NPN_Transistor 18.2 terminal E is connected on net N5 with Battery 2.1, NPN_Transistor 18.1, Polarized_Capacitor 20.1, Polarized_Capacitor 20.4, Resistor 22.1, Resistor 22.2, Resistor 22.3, Switch 25.1.
- `2.1:positive`: Battery 2.1 terminal positive is connected on net N5 with Battery 2.1, NPN_Transistor 18.1, NPN_Transistor 18.2, Polarized_Capacitor 20.1, Polarized_Capacitor 20.4, Resistor 22.1, Resistor 22.2, Resistor 22.3, Switch 25.1.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
