# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `2` (`2.jpg`) from pipeline variant `topology_v9.2_set_successivo` was exported from `06_match_terminals_to_nets`.
The topology contains 20 components, 34 terminals, 13 nets, and 34 terminal-to-net connections.
Explicit ground references: GND 9.1, GND 9.2, GND 9.3, GND 9.4, GND 9.5, GND 9.6, GND 9.7, GND 9.8.

# Main Branches
- `N8` (shared_internal_branch, importance=medium): Net N8 forms a shared internal branch connecting Lamp 13.1, Meter 15.2, Resistor 22.1, Transformer 28.1, Capacitor 4.1, Diode 7.1, Diode 7.2.

# Component Descriptions
- `12.1` (LED): generic circuit element [specificity=low, confidence=0.55] LED 12.1 is described as generic circuit element. It is connected to nets N10, N11 and to Resistor 22.1 via N10; GND 9.7 via N11.
- `13.1` (Lamp): generic circuit element [specificity=low, confidence=0.55] Lamp 13.1 is described as generic circuit element. It is connected to nets N13, N8 and to Meter 15.2 via N8; Meter 15.3 via N13; Resistor 22.1 via N8; Transformer 28.1 via N8; Capacitor 4.1 via N8; Diode 7.1 via N8; Diode 7.2 via N8.
- `15.1` (Meter): measurement or observation point [specificity=medium, confidence=0.78] Meter 15.1 is described as measurement or observation point. It is connected to nets N1, N2 and to Signal_Source 23.1 via N1, N2; Fuse 8.1 via N2; GND 9.1 via N1.
- `15.2` (Meter): measurement or observation point [specificity=medium, confidence=0.78] Meter 15.2 is described as measurement or observation point. It is connected to nets N6, N8 and to Lamp 13.1 via N8; Resistor 22.1 via N8; Transformer 28.1 via N8; Capacitor 4.1 via N8; Diode 7.1 via N8; Diode 7.2 via N8; GND 9.4 via N6.
- `15.3` (Meter): measurement or observation point [specificity=medium, confidence=0.78] Meter 15.3 is described as measurement or observation point. It is connected to nets N12, N13 and to Lamp 13.1 via N13; GND 9.8 via N12.
- `22.1` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.1 is described as passive component. It is connected to nets N10, N8 and to LED 12.1 via N10; Lamp 13.1 via N8; Meter 15.2 via N8; Transformer 28.1 via N8; Capacitor 4.1 via N8; Diode 7.1 via N8; Diode 7.2 via N8.
- `23.1` (Signal_Source): generic circuit element [specificity=low, confidence=0.55] Signal_Source 23.1 is described as generic circuit element. It is connected to nets N1, N2 and to Meter 15.1 via N1, N2; Fuse 8.1 via N2; GND 9.1 via N1.
- `28.1` (Transformer): generic circuit element [specificity=low, confidence=0.55] Transformer 28.1 is described as generic circuit element. It is connected to nets N3, N4, N5, N8 and to Lamp 13.1 via N8; Meter 15.2 via N8; Resistor 22.1 via N8; Capacitor 4.1 via N8; Diode 7.1 via N8; Diode 7.2 via N8; Fuse 8.1 via N3; GND 9.2 via N4; GND 9.3 via N5.
- `4.1` (Capacitor): passive component [specificity=medium, confidence=0.76] Capacitor 4.1 is described as passive component. It is connected to nets N7, N8 and to Lamp 13.1 via N8; Meter 15.2 via N8; Resistor 22.1 via N8; Transformer 28.1 via N8; Diode 7.1 via N8; Diode 7.2 via N8; GND 9.5 via N7.
- `7.1` (Diode): passive component [specificity=medium, confidence=0.76] Diode 7.1 is described as passive component. It is connected to nets N8 and to Lamp 13.1 via N8; Meter 15.2 via N8; Resistor 22.1 via N8; Transformer 28.1 via N8; Capacitor 4.1 via N8; Diode 7.2 via N8.
- `7.2` (Diode): passive component [specificity=medium, confidence=0.76] Diode 7.2 is described as passive component. It is connected to nets N8, N9 and to Lamp 13.1 via N8; Meter 15.2 via N8; Resistor 22.1 via N8; Transformer 28.1 via N8; Capacitor 4.1 via N8; Diode 7.1 via N8; GND 9.6 via N9.
- `8.1` (Fuse): generic circuit element [specificity=low, confidence=0.55] Fuse 8.1 is described as generic circuit element. It is connected to nets N2, N3 and to Meter 15.1 via N2; Signal_Source 23.1 via N2; Transformer 28.1 via N3.
- `9.1` (GND): ground reference [specificity=high, confidence=1.00] GND 9.1 is described as ground reference. It is connected to nets N1 and to Meter 15.1 via N1; Signal_Source 23.1 via N1.
- `9.2` (GND): ground reference [specificity=high, confidence=1.00] GND 9.2 is described as ground reference. It is connected to nets N4 and to Transformer 28.1 via N4.
- `9.3` (GND): ground reference [specificity=high, confidence=1.00] GND 9.3 is described as ground reference. It is connected to nets N5 and to Transformer 28.1 via N5.
- `9.4` (GND): ground reference [specificity=high, confidence=1.00] GND 9.4 is described as ground reference. It is connected to nets N6 and to Meter 15.2 via N6.
- `9.5` (GND): ground reference [specificity=high, confidence=1.00] GND 9.5 is described as ground reference. It is connected to nets N7 and to Capacitor 4.1 via N7.
- `9.6` (GND): ground reference [specificity=high, confidence=1.00] GND 9.6 is described as ground reference. It is connected to nets N9 and to Diode 7.2 via N9.
- `9.7` (GND): ground reference [specificity=high, confidence=1.00] GND 9.7 is described as ground reference. It is connected to nets N11 and to LED 12.1 via N11.
- `9.8` (GND): ground reference [specificity=high, confidence=1.00] GND 9.8 is described as ground reference. It is connected to nets N12 and to Meter 15.3 via N12.

# Net Descriptions
- `N1`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N2`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N3`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N4`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N5`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N6`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N7`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N8`: shared internal branch [specificity=medium, confidence=0.70] Basis: The net behaves like a multi-device internal junction and its terminal semantics are mixed or widely shared.
- `N9`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N10`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N11`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N12`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N13`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.

# Aggregated Relations
- `N8`: N8 is a shared internal branch connecting Lamp 13.1 terminal t1, Meter 15.2 terminal t1, Resistor 22.1 terminal t1, Transformer 28.1 terminal t2, Capacitor 4.1 terminal t1, Diode 7.1 anode, Diode 7.2 anode.
- `N1`: N1 is a ground return connecting Meter 15.1 terminal t2, Signal_Source 23.1 terminal t2, GND 9.1 terminal t1.
- `N10`: N10 is a local interconnect connecting LED 12.1 anode, Resistor 22.1 terminal t2.
- `N11`: N11 is a ground return connecting LED 12.1 cathode, GND 9.7 terminal t1.
- `N12`: N12 is a ground return connecting Meter 15.3 terminal t2, GND 9.8 terminal t1.
- `N13`: N13 is a local interconnect connecting Lamp 13.1 terminal t2, Meter 15.3 terminal t1.
- `N2`: N2 is a local interconnect connecting Meter 15.1 terminal t1, Signal_Source 23.1 terminal t1, Fuse 8.1 terminal t1.
- `N3`: N3 is a local interconnect connecting Transformer 28.1 terminal t1, Fuse 8.1 terminal t2.

# Functional Paths
- No functional path summary was produced from the current topology.

# Structural Patterns
- `high_degree_shared_branch` on `N8`: Net N8 is a shared internal branch touching 7 modeled components.
- `multiple_terminals_same_net` on `7.1`: Diode 7.1 has terminals 7.1:anode, 7.1:cathode on the same net N8.

# Terminal Facts
- `12.1:anode`: LED 12.1 terminal anode is connected on net N10 with Resistor 22.1.
- `12.1:cathode`: LED 12.1 terminal cathode is connected on net N11 with GND 9.7.
- `13.1:t1`: Lamp 13.1 terminal t1 is connected on net N8 with Capacitor 4.1, Diode 7.1, Diode 7.2, Meter 15.2, Resistor 22.1, Transformer 28.1.
- `13.1:t2`: Lamp 13.1 terminal t2 is connected on net N13 with Meter 15.3.
- `15.1:t1`: Meter 15.1 terminal t1 is connected on net N2 with Fuse 8.1, Signal_Source 23.1.
- `15.1:t2`: Meter 15.1 terminal t2 is connected on net N1 with GND 9.1, Signal_Source 23.1.
- `15.2:t1`: Meter 15.2 terminal t1 is connected on net N8 with Capacitor 4.1, Diode 7.1, Diode 7.2, Lamp 13.1, Resistor 22.1, Transformer 28.1.
- `15.2:t2`: Meter 15.2 terminal t2 is connected on net N6 with GND 9.4.
- `15.3:t1`: Meter 15.3 terminal t1 is connected on net N13 with Lamp 13.1.
- `15.3:t2`: Meter 15.3 terminal t2 is connected on net N12 with GND 9.8.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
