# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `7` (`7.jpg`) from pipeline variant `topology_v8_component_polarity` was exported from `06_match_terminals_to_nets`.
The topology contains 7 components, 12 terminals, 3 nets, and 12 terminal-to-net connections.
Explicit power sources: Current_Source 6.1, Current_Source 6.2, Current_Source 6.3.

# Main Branches
- `N1` (source_connected_branch, importance=high): Net N1 forms a source connected branch connecting Resistor 22.1, Resistor 22.2, Current_Source 6.1, Current_Source 6.2, Current_Source 6.3.
- `N2` (source_connected_branch, importance=high): Net N2 forms a source connected branch connecting Resistor 22.2, Terminal 26.2, Current_Source 6.1, Current_Source 6.3.
- `N3` (source_connected_branch, importance=high): Net N3 forms a source connected branch connecting Resistor 22.1, Terminal 26.1, Current_Source 6.2.

# Component Descriptions
- `22.1` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.1 is described as passive component. It is connected to nets N1, N3 and to Resistor 22.2 via N1; Terminal 26.1 via N3; Current_Source 6.1 via N1; Current_Source 6.2 via N1, N3; Current_Source 6.3 via N1.
- `22.2` (Resistor): passive component [specificity=medium, confidence=0.76] Resistor 22.2 is described as passive component. It is connected to nets N1, N2 and to Resistor 22.1 via N1; Terminal 26.2 via N2; Current_Source 6.1 via N1, N2; Current_Source 6.2 via N1; Current_Source 6.3 via N1, N2.
- `26.1` (Terminal): external interface [specificity=low, confidence=0.68] Terminal 26.1 is described as external interface. It is connected to nets N3 and to Resistor 22.1 via N3; Current_Source 6.2 via N3.
- `26.2` (Terminal): external interface [specificity=low, confidence=0.68] Terminal 26.2 is described as external interface. It is connected to nets N2 and to Resistor 22.2 via N2; Current_Source 6.1 via N2; Current_Source 6.3 via N2.
- `6.1` (Current_Source): power source [specificity=high, confidence=0.98] Current_Source 6.1 is described as power source. It is connected to nets N1, N2 and to Resistor 22.1 via N1; Resistor 22.2 via N1, N2; Terminal 26.2 via N2; Current_Source 6.2 via N1; Current_Source 6.3 via N1, N2.
- `6.2` (Current_Source): power source [specificity=high, confidence=0.98] Current_Source 6.2 is described as power source. It is connected to nets N1, N3 and to Resistor 22.1 via N1, N3; Resistor 22.2 via N1; Terminal 26.1 via N3; Current_Source 6.1 via N1; Current_Source 6.3 via N1.
- `6.3` (Current_Source): power source [specificity=high, confidence=0.98] Current_Source 6.3 is described as power source. It is connected to nets N1, N2 and to Resistor 22.1 via N1; Resistor 22.2 via N1, N2; Terminal 26.2 via N2; Current_Source 6.1 via N1, N2; Current_Source 6.2 via N1.

# Net Descriptions
- `N1`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N2`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N3`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.

# Aggregated Relations
- `N1`: N1 is a source connected branch connecting Resistor 22.1 terminal t1, Resistor 22.2 terminal t2, Current_Source 6.1 current_to, Current_Source 6.2 current_from, Current_Source 6.3 current_to.
- `N2`: N2 is a source connected branch connecting Resistor 22.2 terminal t1, Terminal 26.2 terminal t1, Current_Source 6.1 current_from, Current_Source 6.3 current_from.
- `N3`: N3 is a source connected branch connecting Resistor 22.1 terminal t2, Terminal 26.1 terminal t1, Current_Source 6.2 current_to.

# Functional Paths
- No functional path summary was produced from the current topology.

# Structural Patterns
- No structural pattern was recorded from the current topology.

# Terminal Facts
- `22.1:t1`: Resistor 22.1 terminal t1 is connected on net N1 with Current_Source 6.1, Current_Source 6.2, Current_Source 6.3, Resistor 22.2.
- `22.1:t2`: Resistor 22.1 terminal t2 is connected on net N3 with Current_Source 6.2, Terminal 26.1.
- `22.2:t1`: Resistor 22.2 terminal t1 is connected on net N2 with Current_Source 6.1, Current_Source 6.3, Terminal 26.2.
- `22.2:t2`: Resistor 22.2 terminal t2 is connected on net N1 with Current_Source 6.1, Current_Source 6.2, Current_Source 6.3, Resistor 22.1.
- `26.1:t1`: Terminal 26.1 terminal t1 is connected on net N3 with Current_Source 6.2, Resistor 22.1.
- `26.2:t1`: Terminal 26.2 terminal t1 is connected on net N2 with Current_Source 6.1, Current_Source 6.3, Resistor 22.2.
- `6.1:current_from`: Current_Source 6.1 terminal current_from is connected on net N2 with Current_Source 6.3, Resistor 22.2, Terminal 26.2.
- `6.1:current_to`: Current_Source 6.1 terminal current_to is connected on net N1 with Current_Source 6.2, Current_Source 6.3, Resistor 22.1, Resistor 22.2.
- `6.2:current_from`: Current_Source 6.2 terminal current_from is connected on net N1 with Current_Source 6.1, Current_Source 6.3, Resistor 22.1, Resistor 22.2.
- `6.2:current_to`: Current_Source 6.2 terminal current_to is connected on net N3 with Resistor 22.1, Terminal 26.1.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
