# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `20` (`20.png`) from pipeline variant `topology_v9.1_analog_meter_connector_transformer` was exported from `06_match_terminals_to_nets`.
The topology contains 10 components, 18 terminals, 8 nets, and 18 terminal-to-net connections.
Explicit ground references: GND 9.1, GND 9.2, GND 9.3, GND 9.4.

# Main Branches
- `N2` (single_terminal_stub, importance=low): Net N2 forms a single terminal stub connecting Switch 25.1, Connector 5.1.
- `N6` (single_terminal_stub, importance=low): Net N6 forms a single terminal stub connecting Analog_Meter 0.1, Transformer 28.1.

# Component Descriptions
- `0.1` (Analog_Meter): generic circuit element [specificity=low, confidence=0.55] Analog_Meter 0.1 is described as generic circuit element. It is connected to nets N6, N7 and to LED 12.1 via N7; Resistor 22.1 via N7; Transformer 28.1 via N6; GND 9.3 via N7.
- `12.1` (LED): generic circuit element [specificity=low, confidence=0.55] LED 12.1 is described as generic circuit element. It is connected to nets N7, N8 and to Analog_Meter 0.1 via N7; Resistor 22.1 via N7; GND 9.3 via N7; GND 9.4 via N8.
- `22.1` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.1 is described as passive component. It is connected to nets N5, N7 and to Analog_Meter 0.1 via N7; LED 12.1 via N7; Connector 5.1 via N5; GND 9.3 via N7.
- `25.1` (Switch): active component [specificity=low, confidence=0.72] Switch 25.1 is described as active component. It is connected to nets N1, N2 and to Connector 5.1 via N2; GND 9.1 via N1.
- `28.1` (Transformer): generic circuit element [specificity=low, confidence=0.55] Transformer 28.1 is described as generic circuit element. It is connected to nets N4, N6 and to Analog_Meter 0.1 via N6; Connector 5.1 via N4.
- `5.1` (Connector): generic circuit element [specificity=low, confidence=0.55] Connector 5.1 is described as generic circuit element. It is connected to nets N2, N3, N4, N5 and to Resistor 22.1 via N5; Switch 25.1 via N2; Transformer 28.1 via N4; GND 9.2 via N3.
- `9.1` (GND): ground reference [specificity=high, confidence=1.00] GND 9.1 is described as ground reference. It is connected to nets N1 and to Switch 25.1 via N1.
- `9.2` (GND): ground reference [specificity=high, confidence=1.00] GND 9.2 is described as ground reference. It is connected to nets N3 and to Connector 5.1 via N3.
- `9.3` (GND): ground reference [specificity=high, confidence=1.00] GND 9.3 is described as ground reference. It is connected to nets N7 and to Analog_Meter 0.1 via N7; LED 12.1 via N7; Resistor 22.1 via N7.
- `9.4` (GND): ground reference [specificity=high, confidence=1.00] GND 9.4 is described as ground reference. It is connected to nets N8 and to LED 12.1 via N8.

# Net Descriptions
- `N1`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N2`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N3`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N4`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N5`: local interconnect [specificity=low, confidence=0.60] Basis: The net connects a small local group without stronger semantic evidence.
- `N6`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N7`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N8`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.

# Aggregated Relations
- `N7`: N7 is a ground return connecting Analog_Meter 0.1 terminal t2, LED 12.1 anode, Resistor 22.1 terminal t2, GND 9.3 terminal t1.
- `N1`: N1 is a ground return connecting Switch 25.1 terminal t1, GND 9.1 terminal t1.
- `N2`: N2 is a single terminal stub connecting Switch 25.1 terminal t2, Connector 5.1 pin3.
- `N3`: N3 is a ground return connecting Connector 5.1 pin4, GND 9.2 terminal t1.
- `N4`: N4 is a local interconnect connecting Transformer 28.1 terminal t1, Connector 5.1 pin1.
- `N5`: N5 is a local interconnect connecting Resistor 22.1 terminal t1, Connector 5.1 pin2.
- `N6`: N6 is a single terminal stub connecting Analog_Meter 0.1 terminal t1, Transformer 28.1 terminal t2.
- `N8`: N8 is a ground return connecting LED 12.1 cathode, GND 9.4 terminal t1.

# Functional Paths
- `P1` `ground_to_device_path`: Ground to device path: GND 9.1 -> N1 (ground return) -> Switch 25.1. Confidence: 0.68 (heuristic_inference).
- `P2` `ground_to_device_path`: Ground to device path: GND 9.2 -> N3 (ground return) -> Connector 5.1 -> N2 (single terminal stub) -> Switch 25.1. Confidence: 0.68 (heuristic_inference).
- `P3` `ground_to_device_path`: Ground to device path: GND 9.3 -> N7 (ground return) -> Resistor 22.1 -> N5 (local interconnect) -> Connector 5.1 -> N2 (single terminal stub) -> Switch 25.1. Confidence: 0.68 (heuristic_inference).
- `P4` `ground_to_device_path`: Ground to device path: GND 9.4 -> N8 (ground return) -> LED 12.1 -> N7 (ground return) -> Resistor 22.1 -> N5 (local interconnect) -> Connector 5.1 -> N2 (single terminal stub) -> Switch 25.1. Confidence: 0.68 (heuristic_inference).

# Structural Patterns
- `single_terminal_stub` on `N2`: Net N2 currently touches only Switch 25.1 terminal t2.
- `single_terminal_stub` on `N6`: Net N6 currently touches only Transformer 28.1 terminal t2.

# Terminal Facts
- `0.1:t1`: Analog_Meter 0.1 terminal t1 is connected on net N6 with Transformer 28.1.
- `0.1:t2`: Analog_Meter 0.1 terminal t2 is connected on net N7 with GND 9.3, LED 12.1, Resistor 22.1.
- `12.1:anode`: LED 12.1 terminal anode is connected on net N7 with Analog_Meter 0.1, GND 9.3, Resistor 22.1.
- `12.1:cathode`: LED 12.1 terminal cathode is connected on net N8 with GND 9.4.
- `22.1:t1`: Resistor 22.1 terminal t1 is connected on net N5 with Connector 5.1.
- `22.1:t2`: Resistor 22.1 terminal t2 is connected on net N7 with Analog_Meter 0.1, GND 9.3, LED 12.1.
- `25.1:t1`: Switch 25.1 terminal t1 is connected on net N1 with GND 9.1.
- `25.1:t2`: Switch 25.1 terminal t2 is connected on net N2 with Connector 5.1.
- `28.1:t1`: Transformer 28.1 terminal t1 is connected on net N4 with Connector 5.1.
- `28.1:t2`: Transformer 28.1 terminal t2 is connected on net N6 with Analog_Meter 0.1.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
