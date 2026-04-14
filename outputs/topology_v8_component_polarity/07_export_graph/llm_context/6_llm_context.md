# Purpose
This document summarizes the extracted circuit topology in a descriptive form. Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology.

# Overview
Diagram `6` (`6.jpg`) from pipeline variant `topology_v8_component_polarity` was exported from `06_match_terminals_to_nets`.
The topology contains 7 components, 12 terminals, 4 nets, and 12 terminal-to-net connections.
Explicit power sources: Voltage_Source 31.1.
Explicit ground references: GND 9.1.
Possible external inputs: Terminal 26.1.
Possible external outputs or bridge interfaces: Terminal 26.3.

# Main Branches
- `N1` (source_connected_branch, importance=high): Net N1 forms a source connected branch connecting Mosfet 16.1, Voltage_Source 31.1.
- `N2` (external_control_branch, importance=high): Net N2 forms an external control branch connecting Mosfet 16.1, Terminal 26.1.
- `N4` (shared_internal_branch, importance=medium): Net N4 forms a shared internal branch connecting Mosfet 16.1, Mosfet 16.2, Terminal 26.2.

# Component Descriptions
- `16.1` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.1 is described as active component. It is connected to nets N1, N2, N4 and to Mosfet 16.2 via N4; Terminal 26.1 via N2; Terminal 26.2 via N4; Voltage_Source 31.1 via N1.
- `16.2` (Mosfet): active component [specificity=low, confidence=0.72] Mosfet 16.2 is described as active component. It is connected to nets N3, N4 and to Mosfet 16.1 via N4; Terminal 26.2 via N4; Terminal 26.3 via N3; Voltage_Source 31.1 via N3; GND 9.1 via N3.
- `26.1` (Terminal): external interface [specificity=medium, confidence=0.76] Terminal 26.1 is described as external interface. It is connected to nets N2 and to Mosfet 16.1 via N2.
- `26.2` (Terminal): external interface [specificity=low, confidence=0.64] Terminal 26.2 is described as external interface. It is connected to nets N4 and to Mosfet 16.1 via N4; Mosfet 16.2 via N4.
- `26.3` (Terminal): external interface [specificity=low, confidence=0.74] Terminal 26.3 is described as external interface. It is connected to nets N3 and to Mosfet 16.2 via N3; Voltage_Source 31.1 via N3; GND 9.1 via N3.
- `31.1` (Voltage_Source): power source [specificity=high, confidence=0.98] Voltage_Source 31.1 is described as power source. It is connected to nets N1, N3 and to Mosfet 16.1 via N1; Mosfet 16.2 via N3; Terminal 26.3 via N3; GND 9.1 via N3.
- `9.1` (GND): ground reference [specificity=high, confidence=1.00] GND 9.1 is described as ground reference. It is connected to nets N3 and to Mosfet 16.2 via N3; Terminal 26.3 via N3; Voltage_Source 31.1 via N3.

# Net Descriptions
- `N1`: source connected branch [specificity=medium, confidence=0.88] Basis: An explicit source component is attached to this net.
- `N2`: external control branch [specificity=medium, confidence=0.74] Basis: The net reaches an external interface and at least one control-like terminal.
- `N3`: ground return [specificity=high, confidence=1.00] Basis: An explicit ground symbol is attached to this net.
- `N4`: shared internal branch [specificity=medium, confidence=0.70] Basis: The net behaves like a multi-device internal junction and its terminal semantics are mixed or widely shared.

# Aggregated Relations
- `N1`: N1 is a source connected branch connecting Mosfet 16.1 source, Voltage_Source 31.1 positive.
- `N2`: N2 is a external control branch connecting Mosfet 16.1 gate, Terminal 26.1 terminal t1.
- `N3`: N3 is a ground return connecting Mosfet 16.2 drain, Terminal 26.3 terminal t1, Voltage_Source 31.1 negative, GND 9.1 terminal t1.
- `N4`: N4 is a shared internal branch connecting Mosfet 16.1 drain, Mosfet 16.2 gate, Terminal 26.2 terminal t1.

# Functional Paths
- `P1` `source_to_interface_path`: Source to interface path: Voltage_Source 31.1 -> N3 (ground return) -> Terminal 26.3. Confidence: 0.78 (heuristic_inference).
- `P2` `device_to_interface_path`: Device to interface path: Mosfet 16.2 -> N3 (ground return) -> Terminal 26.3. Confidence: 0.74 (heuristic_inference).
- `P3` `external_interface_to_device_path`: External interface to device path: Terminal 26.1 -> N2 (external control branch) -> Mosfet 16.1. Confidence: 0.72 (heuristic_inference).
- `P4` `ground_to_device_path`: Ground to device path: GND 9.1 -> N3 (ground return) -> Mosfet 16.2. Confidence: 0.68 (heuristic_inference).

# Structural Patterns
- `multiple_terminals_same_net` on `16.2`: Mosfet 16.2 has terminals 16.2:S, 16.2:D on the same net N3.

# Terminal Facts
- `16.1:G`: Mosfet 16.1 terminal G is connected on net N2 with Terminal 26.1.
- `16.1:S`: Mosfet 16.1 terminal S is connected on net N1 with Voltage_Source 31.1.
- `16.1:D`: Mosfet 16.1 terminal D is connected on net N4 with Mosfet 16.2, Terminal 26.2.
- `16.2:G`: Mosfet 16.2 terminal G is connected on net N4 with Mosfet 16.1, Terminal 26.2.
- `16.2:S`: Mosfet 16.2 terminal S is connected on net N3 with GND 9.1, Mosfet 16.2, Terminal 26.3, Voltage_Source 31.1.
- `16.2:D`: Mosfet 16.2 terminal D is connected on net N3 with GND 9.1, Mosfet 16.2, Terminal 26.3, Voltage_Source 31.1.
- `26.1:t1`: Terminal 26.1 terminal t1 is connected on net N2 with Mosfet 16.1.
- `26.2:t1`: Terminal 26.2 terminal t1 is connected on net N4 with Mosfet 16.1, Mosfet 16.2.
- `26.3:t1`: Terminal 26.3 terminal t1 is connected on net N3 with GND 9.1, Mosfet 16.2, Voltage_Source 31.1.
- `31.1:positive`: Voltage_Source 31.1 terminal positive is connected on net N1 with Mosfet 16.1.

# Companion Files
- `*_graph.json` remains the technical source of truth.
- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.
