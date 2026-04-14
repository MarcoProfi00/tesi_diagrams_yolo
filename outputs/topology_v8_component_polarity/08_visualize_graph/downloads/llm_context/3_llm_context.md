# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `3` (`3.jpg`) from pipeline variant `topology_v8_component_polarity` was exported from `06_match_terminals_to_nets`.
The topology contains 9 components, 18 terminals, 6 nets, and 18 terminal-to-net connections.
Explicit power sources: Voltage_Source 31.1, Voltage_Source 31.2, Voltage_Source 31.3, Voltage_Source 31.4, Current_Source 6.1, Current_Source 6.2.

# Main Branches
- `N1` (source_connected_branch, importance=high): Net N1 forms a source connected branch connecting Inductor 10.2, Voltage_Source 31.1, Current_Source 6.2.
- `N2` (source_connected_branch, importance=high): Net N2 forms a source connected branch connecting Inductor 10.1, Voltage_Source 31.2, Current_Source 6.1.
- `N3` (source_connected_branch, importance=high): Net N3 forms a source connected branch connecting Voltage_Source 31.1, Voltage_Source 31.2, Voltage_Source 31.3.
- `N4` (source_connected_branch, importance=high): Net N4 forms a source connected branch connecting Inductor 10.2, Capacitor 4.1, Current_Source 6.2.
- `N5` (source_connected_branch, importance=high): Net N5 forms a source connected branch connecting Inductor 10.1, Voltage_Source 31.3, Voltage_Source 31.4, Current_Source 6.1.
- `N6` (source_connected_branch, importance=high): Net N6 forms a source connected branch connecting Voltage_Source 31.4, Capacitor 4.1.

# Component Descriptions
- `10.1` (Inductor): passive component [specificity=medium, confidence=0.76] Inductor 10.1 is described as passive component. It is connected to nets N2, N5 and to Voltage_Source 31.2 via N2; Voltage_Source 31.3 via N5; Voltage_Source 31.4 via N5; Current_Source 6.1 via N2, N5.
- `10.2` (Inductor): passive component [specificity=medium, confidence=0.76] Inductor 10.2 is described as passive component. It is connected to nets N1, N4 and to Voltage_Source 31.1 via N1; Capacitor 4.1 via N4; Current_Source 6.2 via N1, N4.
- `31.1` (Voltage_Source): power source [specificity=high, confidence=0.98] Voltage_Source 31.1 is described as power source. It is connected to nets N1, N3 and to Inductor 10.2 via N1; Voltage_Source 31.2 via N3; Voltage_Source 31.3 via N3; Current_Source 6.2 via N1.
- `31.2` (Voltage_Source): power source [specificity=high, confidence=0.98] Voltage_Source 31.2 is described as power source. It is connected to nets N2, N3 and to Inductor 10.1 via N2; Voltage_Source 31.1 via N3; Voltage_Source 31.3 via N3; Current_Source 6.1 via N2.
- `31.3` (Voltage_Source): power source [specificity=high, confidence=0.98] Voltage_Source 31.3 is described as power source. It is connected to nets N3, N5 and to Inductor 10.1 via N5; Voltage_Source 31.1 via N3; Voltage_Source 31.2 via N3; Voltage_Source 31.4 via N5; Current_Source 6.1 via N5.
- `31.4` (Voltage_Source): power source [specificity=high, confidence=0.98] Voltage_Source 31.4 is described as power source. It is connected to nets N5, N6 and to Inductor 10.1 via N5; Voltage_Source 31.3 via N5; Capacitor 4.1 via N6; Current_Source 6.1 via N5.
- `4.1` (Capacitor): passive component [specificity=medium, confidence=0.76] Capacitor 4.1 is described as passive component. It is connected to nets N4, N6 and to Inductor 10.2 via N4; Voltage_Source 31.4 via N6; Current_Source 6.2 via N4.
- `6.1` (Current_Source): power source [specificity=high, confidence=0.98] Current_Source 6.1 is described as power source. It is connected to nets N2, N5 and to Inductor 10.1 via N2, N5; Voltage_Source 31.2 via N2; Voltage_Source 31.3 via N5; Voltage_Source 31.4 via N5.
- `6.2` (Current_Source): power source [specificity=high, confidence=0.98] Current_Source 6.2 is described as power source. It is connected to nets N1, N4 and to Inductor 10.2 via N1, N4; Voltage_Source 31.1 via N1; Capacitor 4.1 via N4.

# Net Descriptions
- `N1`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N2`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N3`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N4`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N5`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N6`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.

# Aggregated Relations
- `N1`: N1 is a source connected branch connecting Inductor 10.2 terminal t1, Voltage_Source 31.1 positive, Current_Source 6.2 current_from.
- `N2`: N2 is a source connected branch connecting Inductor 10.1 terminal t1, Voltage_Source 31.2 positive, Current_Source 6.1 current_from.
- `N3`: N3 is a source connected branch connecting Voltage_Source 31.1 negative, Voltage_Source 31.2 negative, Voltage_Source 31.3 negative.
- `N4`: N4 is a source connected branch connecting Inductor 10.2 terminal t2, Capacitor 4.1 terminal t1, Current_Source 6.2 current_to.
- `N5`: N5 is a source connected branch connecting Inductor 10.1 terminal t2, Voltage_Source 31.3 positive, Voltage_Source 31.4 negative, Current_Source 6.1 current_to.
- `N6`: N6 is a source connected branch connecting Voltage_Source 31.4 positive, Capacitor 4.1 terminal t2.

# Functional Paths
- No functional path summary was produced from the current topology.

# Structural Patterns
- No structural pattern was recorded from the current topology.

# Terminal Facts
- `10.1:t1`: Inductor 10.1 terminal t1 is connected on net N2 with Current_Source 6.1, Voltage_Source 31.2.
- `10.1:t2`: Inductor 10.1 terminal t2 is connected on net N5 with Current_Source 6.1, Voltage_Source 31.3, Voltage_Source 31.4.
- `10.2:t1`: Inductor 10.2 terminal t1 is connected on net N1 with Current_Source 6.2, Voltage_Source 31.1.
- `10.2:t2`: Inductor 10.2 terminal t2 is connected on net N4 with Capacitor 4.1, Current_Source 6.2.
- `31.1:positive`: Voltage_Source 31.1 terminal positive is connected on net N1 with Current_Source 6.2, Inductor 10.2.
- `31.1:negative`: Voltage_Source 31.1 terminal negative is connected on net N3 with Voltage_Source 31.2, Voltage_Source 31.3.
- `31.2:positive`: Voltage_Source 31.2 terminal positive is connected on net N2 with Current_Source 6.1, Inductor 10.1.
- `31.2:negative`: Voltage_Source 31.2 terminal negative is connected on net N3 with Voltage_Source 31.1, Voltage_Source 31.3.
- `31.3:positive`: Voltage_Source 31.3 terminal positive is connected on net N5 with Current_Source 6.1, Inductor 10.1, Voltage_Source 31.4.
- `31.3:negative`: Voltage_Source 31.3 terminal negative is connected on net N3 with Voltage_Source 31.1, Voltage_Source 31.2.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
