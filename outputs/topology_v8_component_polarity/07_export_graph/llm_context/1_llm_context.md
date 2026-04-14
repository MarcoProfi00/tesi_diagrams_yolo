# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `1` (`1.jpg`) from pipeline variant `topology_v8_component_polarity` was exported from `06_match_terminals_to_nets`.
The topology contains 17 components, 29 terminals, 6 nets, and 29 terminal-to-net connections.
Explicit power sources: Voltage_Source 31.1, Current_Source 6.1, Current_Source 6.2, Current_Source 6.3.
Explicit ground references: GND 9.1.

# Main Branches
- `N1` (source_connected_branch, importance=high): Net N1 forms a source connected branch connecting Polarized_Capacitor 20.1, Polarized_Capacitor 20.2, Polarized_Capacitor 20.3, Resistor 22.1, Resistor 22.2, Terminal 26.1, Current_Source 6.1, Current_Source 6.2.
- `N4` (external_interface_branch, importance=high): Net N4 forms an external interface branch connecting Polarized_Capacitor 20.2, Polarized_Capacitor 20.4, Terminal 26.3.
- `N6` (source_connected_branch, importance=high): Net N6 forms a source connected branch connecting Polarized_Capacitor 20.3, Polarized_Capacitor 20.4, Polarized_Capacitor 20.5, Resistor 22.2, Terminal 26.4, Voltage_Source 31.1, Current_Source 6.2, Current_Source 6.3.
- `N2` (single_terminal_stub, importance=low): Net N2 forms a single terminal stub connecting Resistor 22.1, Switch 25.1.
- `N5` (single_terminal_stub, importance=low): Net N5 forms a single terminal stub connecting Switch 25.1, Voltage_Source 31.1.

# Component Descriptions
- `20.1` (Polarized_Capacitor): generic circuit element [specificity=low, confidence=0.55] Polarized_Capacitor 20.1 is described as generic circuit element. It is connected to nets N1, N3 and to Polarized_Capacitor 20.2 via N1; Polarized_Capacitor 20.3 via N1; Polarized_Capacitor 20.5 via N3; Resistor 22.1 via N1; Resistor 22.2 via N1; Terminal 26.1 via N1; Terminal 26.2 via N3; Current_Source 6.1 via N1, N3; Current_Source 6.2 via N1; Current_Source 6.3 via N3; GND 9.1 via N3.
- `20.2` (Polarized_Capacitor): generic circuit element [specificity=low, confidence=0.55] Polarized_Capacitor 20.2 is described as generic circuit element. It is connected to nets N1, N4 and to Polarized_Capacitor 20.1 via N1; Polarized_Capacitor 20.3 via N1; Polarized_Capacitor 20.4 via N4; Resistor 22.1 via N1; Resistor 22.2 via N1; Terminal 26.1 via N1; Terminal 26.3 via N4; Current_Source 6.1 via N1; Current_Source 6.2 via N1.
- `20.3` (Polarized_Capacitor): generic circuit element [specificity=low, confidence=0.55] Polarized_Capacitor 20.3 is described as generic circuit element. It is connected to nets N1, N6 and to Polarized_Capacitor 20.1 via N1; Polarized_Capacitor 20.2 via N1; Polarized_Capacitor 20.4 via N6; Polarized_Capacitor 20.5 via N6; Resistor 22.1 via N1; Resistor 22.2 via N1, N6; Terminal 26.1 via N1; Terminal 26.4 via N6; Voltage_Source 31.1 via N6; Current_Source 6.1 via N1; Current_Source 6.2 via N1, N6; Current_Source 6.3 via N6.
- `20.4` (Polarized_Capacitor): generic circuit element [specificity=low, confidence=0.55] Polarized_Capacitor 20.4 is described as generic circuit element. It is connected to nets N4, N6 and to Polarized_Capacitor 20.2 via N4; Polarized_Capacitor 20.3 via N6; Polarized_Capacitor 20.5 via N6; Resistor 22.2 via N6; Terminal 26.3 via N4; Terminal 26.4 via N6; Voltage_Source 31.1 via N6; Current_Source 6.2 via N6; Current_Source 6.3 via N6.
- `20.5` (Polarized_Capacitor): generic circuit element [specificity=low, confidence=0.55] Polarized_Capacitor 20.5 is described as generic circuit element. It is connected to nets N3, N6 and to Polarized_Capacitor 20.1 via N3; Polarized_Capacitor 20.3 via N6; Polarized_Capacitor 20.4 via N6; Resistor 22.2 via N6; Terminal 26.2 via N3; Terminal 26.4 via N6; Voltage_Source 31.1 via N6; Current_Source 6.1 via N3; Current_Source 6.2 via N6; Current_Source 6.3 via N3, N6; GND 9.1 via N3.
- `22.1` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.1 is described as passive component. It is connected to nets N1, N2 and to Polarized_Capacitor 20.1 via N1; Polarized_Capacitor 20.2 via N1; Polarized_Capacitor 20.3 via N1; Resistor 22.2 via N1; Switch 25.1 via N2; Terminal 26.1 via N1; Current_Source 6.1 via N1; Current_Source 6.2 via N1.
- `22.2` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.2 is described as passive component. It is connected to nets N1, N6 and to Polarized_Capacitor 20.1 via N1; Polarized_Capacitor 20.2 via N1; Polarized_Capacitor 20.3 via N1, N6; Polarized_Capacitor 20.4 via N6; Polarized_Capacitor 20.5 via N6; Resistor 22.1 via N1; Terminal 26.1 via N1; Terminal 26.4 via N6; Voltage_Source 31.1 via N6; Current_Source 6.1 via N1; Current_Source 6.2 via N1, N6; Current_Source 6.3 via N6.
- `25.1` (Switch): active component [specificity=low, confidence=0.72] Switch 25.1 is described as active component. It is connected to nets N2, N5 and to Resistor 22.1 via N2; Voltage_Source 31.1 via N5.
- `26.1` (Terminal): external interface [specificity=low, confidence=0.68] Terminal 26.1 is described as external interface. It is connected to nets N1 and to Polarized_Capacitor 20.1 via N1; Polarized_Capacitor 20.2 via N1; Polarized_Capacitor 20.3 via N1; Resistor 22.1 via N1; Resistor 22.2 via N1; Current_Source 6.1 via N1; Current_Source 6.2 via N1.
- `26.2` (Terminal): external interface [specificity=low, confidence=0.68] Terminal 26.2 is described as external interface. It is connected to nets N3 and to Polarized_Capacitor 20.1 via N3; Polarized_Capacitor 20.5 via N3; Current_Source 6.1 via N3; Current_Source 6.3 via N3; GND 9.1 via N3.
- `26.3` (Terminal): external interface [specificity=low, confidence=0.68] Terminal 26.3 is described as external interface. It is connected to nets N4 and to Polarized_Capacitor 20.2 via N4; Polarized_Capacitor 20.4 via N4.
- `26.4` (Terminal): external interface [specificity=low, confidence=0.68] Terminal 26.4 is described as external interface. It is connected to nets N6 and to Polarized_Capacitor 20.3 via N6; Polarized_Capacitor 20.4 via N6; Polarized_Capacitor 20.5 via N6; Resistor 22.2 via N6; Voltage_Source 31.1 via N6; Current_Source 6.2 via N6; Current_Source 6.3 via N6.
- `31.1` (Voltage_Source): power source [specificity=high, confidence=0.98] Voltage_Source 31.1 is described as power source. It is connected to nets N5, N6 and to Polarized_Capacitor 20.3 via N6; Polarized_Capacitor 20.4 via N6; Polarized_Capacitor 20.5 via N6; Resistor 22.2 via N6; Switch 25.1 via N5; Terminal 26.4 via N6; Current_Source 6.2 via N6; Current_Source 6.3 via N6.
- `6.1` (Current_Source): power source [specificity=high, confidence=0.98] Current_Source 6.1 is described as power source. It is connected to nets N1, N3 and to Polarized_Capacitor 20.1 via N1, N3; Polarized_Capacitor 20.2 via N1; Polarized_Capacitor 20.3 via N1; Polarized_Capacitor 20.5 via N3; Resistor 22.1 via N1; Resistor 22.2 via N1; Terminal 26.1 via N1; Terminal 26.2 via N3; Current_Source 6.2 via N1; Current_Source 6.3 via N3; GND 9.1 via N3.
- `6.2` (Current_Source): power source [specificity=high, confidence=0.98] Current_Source 6.2 is described as power source. It is connected to nets N1, N6 and to Polarized_Capacitor 20.1 via N1; Polarized_Capacitor 20.2 via N1; Polarized_Capacitor 20.3 via N1, N6; Polarized_Capacitor 20.4 via N6; Polarized_Capacitor 20.5 via N6; Resistor 22.1 via N1; Resistor 22.2 via N1, N6; Terminal 26.1 via N1; Terminal 26.4 via N6; Voltage_Source 31.1 via N6; Current_Source 6.1 via N1; Current_Source 6.3 via N6.
- `6.3` (Current_Source): power source [specificity=high, confidence=0.98] Current_Source 6.3 is described as power source. It is connected to nets N3, N6 and to Polarized_Capacitor 20.1 via N3; Polarized_Capacitor 20.3 via N6; Polarized_Capacitor 20.4 via N6; Polarized_Capacitor 20.5 via N3, N6; Resistor 22.2 via N6; Terminal 26.2 via N3; Terminal 26.4 via N6; Voltage_Source 31.1 via N6; Current_Source 6.1 via N3; Current_Source 6.2 via N6; GND 9.1 via N3.
- `9.1` (GND): ground reference [specificity=high, confidence=1.00] GND 9.1 is described as ground reference. It is connected to nets N3 and to Polarized_Capacitor 20.1 via N3; Polarized_Capacitor 20.5 via N3; Terminal 26.2 via N3; Current_Source 6.1 via N3; Current_Source 6.3 via N3.

# Net Descriptions
- `N1`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N2`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N3`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N4`: external interface branch [specificity=low, confidence=0.68] Basis: The net reaches at least one explicit external interface.
- `N5`: single terminal stub [specificity=high, confidence=0.96] Basis: Only one modeled terminal reaches this net.
- `N6`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.

# Aggregated Relations
- `N1`: N1 is a source connected branch connecting Polarized_Capacitor 20.1 positive, Polarized_Capacitor 20.2 positive, Polarized_Capacitor 20.3 positive, Resistor 22.1 terminal t1, Resistor 22.2 terminal t1, Terminal 26.1 terminal t1, Current_Source 6.1 current_from, Current_Source 6.2 current_from.
- `N4`: N4 is a external interface branch connecting Polarized_Capacitor 20.2 negative, Polarized_Capacitor 20.4 positive, Terminal 26.3 terminal t1.
- `N6`: N6 is a source connected branch connecting Polarized_Capacitor 20.3 negative, Polarized_Capacitor 20.4 negative, Polarized_Capacitor 20.5 positive, Resistor 22.2 terminal t2, Terminal 26.4 terminal t1, Voltage_Source 31.1 negative, Current_Source 6.2 current_to, Current_Source 6.3 current_from.
- `N3`: N3 is a ground return connecting Polarized_Capacitor 20.1 negative, Polarized_Capacitor 20.5 negative, Terminal 26.2 terminal t1, Current_Source 6.1 current_to, Current_Source 6.3 current_to, GND 9.1 terminal t1.
- `N2`: N2 is a single terminal stub connecting Resistor 22.1 terminal t2, Switch 25.1 terminal t1.
- `N5`: N5 is a single terminal stub connecting Switch 25.1 terminal t2, Voltage_Source 31.1 positive.

# Functional Paths
- `P1` `ground_to_device_path`: Ground to device path: GND 9.1 -> N3 (ground return) -> Polarized_Capacitor 20.1 -> N1 (source connected branch) -> Resistor 22.1 -> N2 (single terminal stub) -> Switch 25.1. Confidence: 0.68 (heuristic_inference).

# Structural Patterns
- `single_terminal_stub` on `N2`: Net N2 currently touches only Resistor 22.1 terminal t2.
- `single_terminal_stub` on `N5`: Net N5 currently touches only Switch 25.1 terminal t2.

# Terminal Facts
- `20.1:positive`: Polarized_Capacitor 20.1 terminal positive is connected on net N1 with Current_Source 6.1, Current_Source 6.2, Polarized_Capacitor 20.2, Polarized_Capacitor 20.3, Resistor 22.1, Resistor 22.2, Terminal 26.1.
- `20.1:negative`: Polarized_Capacitor 20.1 terminal negative is connected on net N3 with Current_Source 6.1, Current_Source 6.3, GND 9.1, Polarized_Capacitor 20.5, Terminal 26.2.
- `20.2:positive`: Polarized_Capacitor 20.2 terminal positive is connected on net N1 with Current_Source 6.1, Current_Source 6.2, Polarized_Capacitor 20.1, Polarized_Capacitor 20.3, Resistor 22.1, Resistor 22.2, Terminal 26.1.
- `20.2:negative`: Polarized_Capacitor 20.2 terminal negative is connected on net N4 with Polarized_Capacitor 20.4, Terminal 26.3.
- `20.3:positive`: Polarized_Capacitor 20.3 terminal positive is connected on net N1 with Current_Source 6.1, Current_Source 6.2, Polarized_Capacitor 20.1, Polarized_Capacitor 20.2, Resistor 22.1, Resistor 22.2, Terminal 26.1.
- `20.3:negative`: Polarized_Capacitor 20.3 terminal negative is connected on net N6 with Current_Source 6.2, Current_Source 6.3, Polarized_Capacitor 20.4, Polarized_Capacitor 20.5, Resistor 22.2, Terminal 26.4, Voltage_Source 31.1.
- `20.4:positive`: Polarized_Capacitor 20.4 terminal positive is connected on net N4 with Polarized_Capacitor 20.2, Terminal 26.3.
- `20.4:negative`: Polarized_Capacitor 20.4 terminal negative is connected on net N6 with Current_Source 6.2, Current_Source 6.3, Polarized_Capacitor 20.3, Polarized_Capacitor 20.5, Resistor 22.2, Terminal 26.4, Voltage_Source 31.1.
- `20.5:positive`: Polarized_Capacitor 20.5 terminal positive is connected on net N6 with Current_Source 6.2, Current_Source 6.3, Polarized_Capacitor 20.3, Polarized_Capacitor 20.4, Resistor 22.2, Terminal 26.4, Voltage_Source 31.1.
- `20.5:negative`: Polarized_Capacitor 20.5 terminal negative is connected on net N3 with Current_Source 6.1, Current_Source 6.3, GND 9.1, Polarized_Capacitor 20.1, Terminal 26.2.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
