# LLM Context - Diagram 4

## Purpose
Use this context to reason about the circuit topology and identify possible faults, broken components, abnormal connections, or inconsistent supply paths.

## Overview
- Diagram ID: 4
- Image: 4.jpg
- Pipeline variant: topology_v7_npn_transistor_mosfet
- Components: 8
- Terminals: 21
- Nets: 7
- Connections: 21
- Suspicious terminal matches: 0
- Unmatched terminals: 0
- Implicit supply nets: 0

## Diagnostic Notes
- No implicit supply nets, suspicious terminal matches, or unmatched terminals were detected.

## Component-Centric Topology

### 16.1 (Mosfet)
- Connected nets: N1, N3, N4
- Connected components: 16.2 (Mosfet) via N1; 16.3 (Mosfet) via N1, N4; 16.5 (Mosfet) via N3, N4; 22.1 (Resistor) via N3, N4; 9.1 (GND) via N3
- 16.1:G: 16.1 (Mosfet) terminal G is connected on net N4 together with 16.3 (Mosfet) terminal S, 16.5 (Mosfet) terminal G, 22.1 (Resistor) terminal t1.
- 16.1:D: 16.1 (Mosfet) terminal D is connected on net N1 together with 16.2 (Mosfet) terminal D, 16.3 (Mosfet) terminal G.
- 16.1:S: 16.1 (Mosfet) terminal S is connected on net N3 together with 16.5 (Mosfet) terminal S, 22.1 (Resistor) terminal t2, 9.1 (GND) terminal t1.

### 16.2 (Mosfet)
- Connected nets: N1, N2, N5
- Connected components: 16.1 (Mosfet) via N1; 16.3 (Mosfet) via N1, N5; 16.4 (Mosfet) via N2, N5; 16.6 (Mosfet) via N2, N5
- 16.2:G: 16.2 (Mosfet) terminal G is connected on net N5 together with 16.3 (Mosfet) terminal D, 16.4 (Mosfet) terminal G, 16.4 (Mosfet) terminal D, 16.6 (Mosfet) terminal G.
- 16.2:S: 16.2 (Mosfet) terminal S is connected on net N2 together with 16.4 (Mosfet) terminal S, 16.6 (Mosfet) terminal S.
- 16.2:D: 16.2 (Mosfet) terminal D is connected on net N1 together with 16.1 (Mosfet) terminal D, 16.3 (Mosfet) terminal G.

### 16.3 (Mosfet)
- Connected nets: N1, N4, N5
- Connected components: 16.1 (Mosfet) via N1, N4; 16.2 (Mosfet) via N1, N5; 16.4 (Mosfet) via N5; 16.5 (Mosfet) via N4; 16.6 (Mosfet) via N5; 22.1 (Resistor) via N4
- 16.3:G: 16.3 (Mosfet) terminal G is connected on net N1 together with 16.1 (Mosfet) terminal D, 16.2 (Mosfet) terminal D.
- 16.3:D: 16.3 (Mosfet) terminal D is connected on net N5 together with 16.2 (Mosfet) terminal G, 16.4 (Mosfet) terminal G, 16.4 (Mosfet) terminal D, 16.6 (Mosfet) terminal G.
- 16.3:S: 16.3 (Mosfet) terminal S is connected on net N4 together with 16.1 (Mosfet) terminal G, 16.5 (Mosfet) terminal G, 22.1 (Resistor) terminal t1.

### 16.4 (Mosfet)
- Connected nets: N2, N5
- Connected components: 16.2 (Mosfet) via N2, N5; 16.3 (Mosfet) via N5; 16.6 (Mosfet) via N2, N5
- 16.4:G: 16.4 (Mosfet) terminal G is connected on net N5 together with 16.2 (Mosfet) terminal G, 16.3 (Mosfet) terminal D, 16.4 (Mosfet) terminal D, 16.6 (Mosfet) terminal G.
- 16.4:S: 16.4 (Mosfet) terminal S is connected on net N2 together with 16.2 (Mosfet) terminal S, 16.6 (Mosfet) terminal S.
- 16.4:D: 16.4 (Mosfet) terminal D is connected on net N5 together with 16.2 (Mosfet) terminal G, 16.3 (Mosfet) terminal D, 16.4 (Mosfet) terminal G, 16.6 (Mosfet) terminal G.

### 22.1 (Resistor)
- Connected nets: N3, N4
- Connected components: 16.1 (Mosfet) via N3, N4; 16.3 (Mosfet) via N4; 16.5 (Mosfet) via N3, N4; 9.1 (GND) via N3
- 22.1:t1: 22.1 (Resistor) terminal t1 is connected on net N4 together with 16.1 (Mosfet) terminal G, 16.3 (Mosfet) terminal S, 16.5 (Mosfet) terminal G.
- 22.1:t2: 22.1 (Resistor) terminal t2 is connected on net N3 together with 16.1 (Mosfet) terminal S, 16.5 (Mosfet) terminal S, 9.1 (GND) terminal t1.

### 9.1 (GND)
- Connected nets: N3
- Connected components: 16.1 (Mosfet) via N3; 16.5 (Mosfet) via N3; 22.1 (Resistor) via N3
- 9.1:t1: 9.1 (GND) terminal t1 is connected on net N3 together with 16.1 (Mosfet) terminal S, 16.5 (Mosfet) terminal S, 22.1 (Resistor) terminal t2.

### 16.5 (Mosfet)
- Connected nets: N3, N4, N7
- Connected components: 16.1 (Mosfet) via N3, N4; 16.3 (Mosfet) via N4; 22.1 (Resistor) via N3, N4; 9.1 (GND) via N3
- 16.5:G: 16.5 (Mosfet) terminal G is connected on net N4 together with 16.1 (Mosfet) terminal G, 16.3 (Mosfet) terminal S, 22.1 (Resistor) terminal t1.
- 16.5:D: 16.5 (Mosfet) terminal D is the only modeled terminal on net N7.
- 16.5:S: 16.5 (Mosfet) terminal S is connected on net N3 together with 16.1 (Mosfet) terminal S, 22.1 (Resistor) terminal t2, 9.1 (GND) terminal t1.

### 16.6 (Mosfet)
- Connected nets: N2, N5, N6
- Connected components: 16.2 (Mosfet) via N2, N5; 16.3 (Mosfet) via N5; 16.4 (Mosfet) via N2, N5
- 16.6:G: 16.6 (Mosfet) terminal G is connected on net N5 together with 16.2 (Mosfet) terminal G, 16.3 (Mosfet) terminal D, 16.4 (Mosfet) terminal G, 16.4 (Mosfet) terminal D.
- 16.6:S: 16.6 (Mosfet) terminal S is connected on net N2 together with 16.2 (Mosfet) terminal S, 16.4 (Mosfet) terminal S.
- 16.6:D: 16.6 (Mosfet) terminal D is the only modeled terminal on net N6.

## Net-Centric Topology
- N1: Net N1 connects 16.1 (Mosfet) terminal D, 16.2 (Mosfet) terminal D, 16.3 (Mosfet) terminal G.
- N2: Net N2 connects 16.2 (Mosfet) terminal S, 16.4 (Mosfet) terminal S, 16.6 (Mosfet) terminal S.
- N3: Net N3 connects 16.1 (Mosfet) terminal S, 16.5 (Mosfet) terminal S, 22.1 (Resistor) terminal t2, 9.1 (GND) terminal t1.
- N4: Net N4 connects 16.1 (Mosfet) terminal G, 16.3 (Mosfet) terminal S, 16.5 (Mosfet) terminal G, 22.1 (Resistor) terminal t1.
- N5: Net N5 connects 16.2 (Mosfet) terminal G, 16.3 (Mosfet) terminal D, 16.4 (Mosfet) terminal G, 16.4 (Mosfet) terminal D, 16.6 (Mosfet) terminal G.
- N6: Net N6 currently touches only 16.6 (Mosfet) terminal D.
- N7: Net N7 currently touches only 16.5 (Mosfet) terminal D.

## Reasoning Hints
- Check whether supply nets, especially implicit ones, are plausible for the connected components.
- Look for components whose terminals connect to unexpected peers or to only one modeled net when that seems electrically unusual.
- Use the component-centric section to follow signal flow and the net-centric section to verify shared connectivity.

## Companion Files
- `*_simplified.json`: same information in structured JSON form.
- `*_graph.json`: full graph export with nodes and edges.
