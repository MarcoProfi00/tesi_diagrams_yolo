# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `10` (`10.jpg`) from pipeline variant `topology_v8_component_polarity` was exported from `06_match_terminals_to_nets`.
The topology contains 9 components, 16 terminals, 3 nets, and 16 terminal-to-net connections.
Explicit power sources: Current_Source 6.1, Current_Source 6.2.

# Main Branches
- `N1` (source_connected_branch, importance=high): Net N1 forms a source connected branch connecting Polarized_Capacitor 20.1, Polarized_Capacitor 20.2, Resistor 22.1, Current_Source 6.1.
- `N2` (source_connected_branch, importance=high): Net N2 forms a source connected branch connecting Polarized_Capacitor 20.1, Polarized_Capacitor 20.3, Resistor 22.1, Resistor 22.2, Terminal 26.1, Current_Source 6.1, Current_Source 6.2.
- `N3` (source_connected_branch, importance=high): Net N3 forms a source connected branch connecting Polarized_Capacitor 20.2, Polarized_Capacitor 20.3, Resistor 22.2, Terminal 26.2, Current_Source 6.2.

# Component Descriptions
- `20.1` (Polarized_Capacitor): generic circuit element [specificity=low, confidence=0.55] Polarized_Capacitor 20.1 is described as generic circuit element. It is connected to nets N1, N2 and to Polarized_Capacitor 20.2 via N1; Polarized_Capacitor 20.3 via N2; Resistor 22.1 via N1, N2; Resistor 22.2 via N2; Terminal 26.1 via N2; Current_Source 6.1 via N1, N2; Current_Source 6.2 via N2.
- `20.2` (Polarized_Capacitor): generic circuit element [specificity=low, confidence=0.55] Polarized_Capacitor 20.2 is described as generic circuit element. It is connected to nets N1, N3 and to Polarized_Capacitor 20.1 via N1; Polarized_Capacitor 20.3 via N3; Resistor 22.1 via N1; Resistor 22.2 via N3; Terminal 26.2 via N3; Current_Source 6.1 via N1; Current_Source 6.2 via N3.
- `20.3` (Polarized_Capacitor): generic circuit element [specificity=low, confidence=0.55] Polarized_Capacitor 20.3 is described as generic circuit element. It is connected to nets N2, N3 and to Polarized_Capacitor 20.1 via N2; Polarized_Capacitor 20.2 via N3; Resistor 22.1 via N2; Resistor 22.2 via N2, N3; Terminal 26.1 via N2; Terminal 26.2 via N3; Current_Source 6.1 via N2; Current_Source 6.2 via N2, N3.
- `22.1` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.1 is described as passive component. It is connected to nets N1, N2 and to Polarized_Capacitor 20.1 via N1, N2; Polarized_Capacitor 20.2 via N1; Polarized_Capacitor 20.3 via N2; Resistor 22.2 via N2; Terminal 26.1 via N2; Current_Source 6.1 via N1, N2; Current_Source 6.2 via N2.
- `22.2` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.2 is described as passive component. It is connected to nets N2, N3 and to Polarized_Capacitor 20.1 via N2; Polarized_Capacitor 20.2 via N3; Polarized_Capacitor 20.3 via N2, N3; Resistor 22.1 via N2; Terminal 26.1 via N2; Terminal 26.2 via N3; Current_Source 6.1 via N2; Current_Source 6.2 via N2, N3.
- `26.1` (Terminal): external interface [specificity=low, confidence=0.68] Terminal 26.1 is described as external interface. It is connected to nets N2 and to Polarized_Capacitor 20.1 via N2; Polarized_Capacitor 20.3 via N2; Resistor 22.1 via N2; Resistor 22.2 via N2; Current_Source 6.1 via N2; Current_Source 6.2 via N2.
- `26.2` (Terminal): external interface [specificity=low, confidence=0.68] Terminal 26.2 is described as external interface. It is connected to nets N3 and to Polarized_Capacitor 20.2 via N3; Polarized_Capacitor 20.3 via N3; Resistor 22.2 via N3; Current_Source 6.2 via N3.
- `6.1` (Current_Source): power source [specificity=high, confidence=0.98] Current_Source 6.1 is described as power source. It is connected to nets N1, N2 and to Polarized_Capacitor 20.1 via N1, N2; Polarized_Capacitor 20.2 via N1; Polarized_Capacitor 20.3 via N2; Resistor 22.1 via N1, N2; Resistor 22.2 via N2; Terminal 26.1 via N2; Current_Source 6.2 via N2.
- `6.2` (Current_Source): power source [specificity=high, confidence=0.98] Current_Source 6.2 is described as power source. It is connected to nets N2, N3 and to Polarized_Capacitor 20.1 via N2; Polarized_Capacitor 20.2 via N3; Polarized_Capacitor 20.3 via N2, N3; Resistor 22.1 via N2; Resistor 22.2 via N2, N3; Terminal 26.1 via N2; Terminal 26.2 via N3; Current_Source 6.1 via N2.

# Net Descriptions
- `N1`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N2`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N3`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.

# Aggregated Relations
- `N1`: N1 is a source connected branch connecting Polarized_Capacitor 20.1 positive, Polarized_Capacitor 20.2 positive, Resistor 22.1 terminal t1, Current_Source 6.1 current_to.
- `N2`: N2 is a source connected branch connecting Polarized_Capacitor 20.1 negative, Polarized_Capacitor 20.3 negative, Resistor 22.1 terminal t2, Resistor 22.2 terminal t2, Terminal 26.1 terminal t1, Current_Source 6.1 current_from, Current_Source 6.2 current_to.
- `N3`: N3 is a source connected branch connecting Polarized_Capacitor 20.2 negative, Polarized_Capacitor 20.3 positive, Resistor 22.2 terminal t1, Terminal 26.2 terminal t1, Current_Source 6.2 current_from.

# Functional Paths
- No functional path summary was produced from the current topology.

# Structural Patterns
- No structural pattern was recorded from the current topology.

# Terminal Facts
- `20.1:positive`: Polarized_Capacitor 20.1 terminal positive is connected on net N1 with Current_Source 6.1, Polarized_Capacitor 20.2, Resistor 22.1.
- `20.1:negative`: Polarized_Capacitor 20.1 terminal negative is connected on net N2 with Current_Source 6.1, Current_Source 6.2, Polarized_Capacitor 20.3, Resistor 22.1, Resistor 22.2, Terminal 26.1.
- `20.2:positive`: Polarized_Capacitor 20.2 terminal positive is connected on net N1 with Current_Source 6.1, Polarized_Capacitor 20.1, Resistor 22.1.
- `20.2:negative`: Polarized_Capacitor 20.2 terminal negative is connected on net N3 with Current_Source 6.2, Polarized_Capacitor 20.3, Resistor 22.2, Terminal 26.2.
- `20.3:positive`: Polarized_Capacitor 20.3 terminal positive is connected on net N3 with Current_Source 6.2, Polarized_Capacitor 20.2, Resistor 22.2, Terminal 26.2.
- `20.3:negative`: Polarized_Capacitor 20.3 terminal negative is connected on net N2 with Current_Source 6.1, Current_Source 6.2, Polarized_Capacitor 20.1, Resistor 22.1, Resistor 22.2, Terminal 26.1.
- `22.1:t1`: Resistor 22.1 terminal t1 is connected on net N1 with Current_Source 6.1, Polarized_Capacitor 20.1, Polarized_Capacitor 20.2.
- `22.1:t2`: Resistor 22.1 terminal t2 is connected on net N2 with Current_Source 6.1, Current_Source 6.2, Polarized_Capacitor 20.1, Polarized_Capacitor 20.3, Resistor 22.2, Terminal 26.1.
- `22.2:t1`: Resistor 22.2 terminal t1 is connected on net N3 with Current_Source 6.2, Polarized_Capacitor 20.2, Polarized_Capacitor 20.3, Terminal 26.2.
- `22.2:t2`: Resistor 22.2 terminal t2 is connected on net N2 with Current_Source 6.1, Current_Source 6.2, Polarized_Capacitor 20.1, Polarized_Capacitor 20.3, Resistor 22.1, Terminal 26.1.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
