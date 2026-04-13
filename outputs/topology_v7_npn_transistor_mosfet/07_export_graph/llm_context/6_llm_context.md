# LLM Context - Diagram 6

## Purpose
Use this context to reason about the circuit topology and identify possible faults, broken components, abnormal connections, or inconsistent supply paths.

## Overview
- Diagram ID: 6
- Image: 6.jpg
- Pipeline variant: topology_v7_npn_transistor_mosfet
- Components: 18
- Terminals: 32
- Nets: 14
- Connections: 32
- Suspicious terminal matches: 0
- Unmatched terminals: 0
- Implicit supply nets: 0

## Diagnostic Notes
- No implicit supply nets, suspicious terminal matches, or unmatched terminals were detected.

## Component-Centric Topology

### 26.1 (Terminal)
- Connected nets: N1
- Connected components: 16.1 (Mosfet) via N1
- 26.1:t1: 26.1 (Terminal) terminal t1 is connected on net N1 to 16.1 (Mosfet) terminal G.

### 16.1 (Mosfet)
- Connected nets: N1, N2, N3
- Connected components: 10.1 (Inductor) via N3; 26.1 (Terminal) via N1; 9.1 (GND) via N2
- 16.1:G: 16.1 (Mosfet) terminal G is connected on net N1 to 26.1 (Terminal) terminal t1.
- 16.1:D: 16.1 (Mosfet) terminal D is connected on net N3 to 10.1 (Inductor) terminal t1.
- 16.1:S: 16.1 (Mosfet) terminal S is connected on net N2 to 9.1 (GND) terminal t1.

### 9.1 (GND)
- Connected nets: N2
- Connected components: 16.1 (Mosfet) via N2
- 9.1:t1: 9.1 (GND) terminal t1 is connected on net N2 to 16.1 (Mosfet) terminal S.

### 9.2 (GND)
- Connected nets: N4
- Connected components: 22.1 (Resistor) via N4
- 9.2:t1: 9.2 (GND) terminal t1 is connected on net N4 to 22.1 (Resistor) terminal t2.

### 10.1 (Inductor)
- Connected nets: N3, N6
- Connected components: 10.3 (Inductor) via N6; 16.1 (Mosfet) via N3; 16.2 (Mosfet) via N6
- 10.1:t1: 10.1 (Inductor) terminal t1 is connected on net N3 to 16.1 (Mosfet) terminal D.
- 10.1:t2: 10.1 (Inductor) terminal t2 is connected on net N6 together with 10.3 (Inductor) terminal t1, 16.2 (Mosfet) terminal G.

### 22.1 (Resistor)
- Connected nets: N4, N5
- Connected components: 10.2 (Inductor) via N5; 9.2 (GND) via N4
- 22.1:t1: 22.1 (Resistor) terminal t1 is connected on net N5 to 10.2 (Inductor) terminal t1.
- 22.1:t2: 22.1 (Resistor) terminal t2 is connected on net N4 to 9.2 (GND) terminal t1.

### 10.2 (Inductor)
- Connected nets: N5, N7
- Connected components: 10.4 (Inductor) via N7; 16.2 (Mosfet) via N7; 22.1 (Resistor) via N5
- 10.2:t1: 10.2 (Inductor) terminal t1 is connected on net N5 to 22.1 (Resistor) terminal t1.
- 10.2:t2: 10.2 (Inductor) terminal t2 is connected on net N7 together with 10.4 (Inductor) terminal t1, 16.2 (Mosfet) terminal D.

### 16.2 (Mosfet)
- Connected nets: N6, N7, N8
- Connected components: 10.1 (Inductor) via N6; 10.2 (Inductor) via N7; 10.3 (Inductor) via N6; 10.4 (Inductor) via N7; 9.3 (GND) via N8
- 16.2:G: 16.2 (Mosfet) terminal G is connected on net N6 together with 10.1 (Inductor) terminal t2, 10.3 (Inductor) terminal t1.
- 16.2:D: 16.2 (Mosfet) terminal D is connected on net N7 together with 10.2 (Inductor) terminal t2, 10.4 (Inductor) terminal t1.
- 16.2:S: 16.2 (Mosfet) terminal S is connected on net N8 to 9.3 (GND) terminal t1.

### 10.3 (Inductor)
- Connected nets: N6, N9
- Connected components: 10.1 (Inductor) via N6; 10.5 (Inductor) via N9; 16.2 (Mosfet) via N6; 16.3 (Mosfet) via N9
- 10.3:t1: 10.3 (Inductor) terminal t1 is connected on net N6 together with 10.1 (Inductor) terminal t2, 16.2 (Mosfet) terminal G.
- 10.3:t2: 10.3 (Inductor) terminal t2 is connected on net N9 together with 10.5 (Inductor) terminal t1, 16.3 (Mosfet) terminal G.

### 9.3 (GND)
- Connected nets: N8
- Connected components: 16.2 (Mosfet) via N8
- 9.3:t1: 9.3 (GND) terminal t1 is connected on net N8 to 16.2 (Mosfet) terminal S.

### 10.4 (Inductor)
- Connected nets: N11, N7
- Connected components: 10.2 (Inductor) via N7; 10.6 (Inductor) via N11; 16.2 (Mosfet) via N7; 16.3 (Mosfet) via N11
- 10.4:t1: 10.4 (Inductor) terminal t1 is connected on net N7 together with 10.2 (Inductor) terminal t2, 16.2 (Mosfet) terminal D.
- 10.4:t2: 10.4 (Inductor) terminal t2 is connected on net N11 together with 10.6 (Inductor) terminal t1, 16.3 (Mosfet) terminal D.

### 16.3 (Mosfet)
- Connected nets: N10, N11, N9
- Connected components: 10.3 (Inductor) via N9; 10.4 (Inductor) via N11; 10.5 (Inductor) via N9; 10.6 (Inductor) via N11; 9.4 (GND) via N10
- 16.3:G: 16.3 (Mosfet) terminal G is connected on net N9 together with 10.3 (Inductor) terminal t2, 10.5 (Inductor) terminal t1.
- 16.3:D: 16.3 (Mosfet) terminal D is connected on net N11 together with 10.4 (Inductor) terminal t2, 10.6 (Inductor) terminal t1.
- 16.3:S: 16.3 (Mosfet) terminal S is connected on net N10 to 9.4 (GND) terminal t1.

### 9.4 (GND)
- Connected nets: N10
- Connected components: 16.3 (Mosfet) via N10
- 9.4:t1: 9.4 (GND) terminal t1 is connected on net N10 to 16.3 (Mosfet) terminal S.

### 10.5 (Inductor)
- Connected nets: N12, N9
- Connected components: 10.3 (Inductor) via N9; 16.3 (Mosfet) via N9; 22.2 (Resistor) via N12
- 10.5:t1: 10.5 (Inductor) terminal t1 is connected on net N9 together with 10.3 (Inductor) terminal t2, 16.3 (Mosfet) terminal G.
- 10.5:t2: 10.5 (Inductor) terminal t2 is connected on net N12 to 22.2 (Resistor) terminal t1.

### 22.2 (Resistor)
- Connected nets: N12, N13
- Connected components: 10.5 (Inductor) via N12; 9.5 (GND) via N13
- 22.2:t1: 22.2 (Resistor) terminal t1 is connected on net N12 to 10.5 (Inductor) terminal t2.
- 22.2:t2: 22.2 (Resistor) terminal t2 is connected on net N13 to 9.5 (GND) terminal t1.

### 9.5 (GND)
- Connected nets: N13
- Connected components: 22.2 (Resistor) via N13
- 9.5:t1: 9.5 (GND) terminal t1 is connected on net N13 to 22.2 (Resistor) terminal t2.

### 10.6 (Inductor)
- Connected nets: N11, N14
- Connected components: 10.4 (Inductor) via N11; 16.3 (Mosfet) via N11; 26.2 (Terminal) via N14
- 10.6:t1: 10.6 (Inductor) terminal t1 is connected on net N11 together with 10.4 (Inductor) terminal t2, 16.3 (Mosfet) terminal D.
- 10.6:t2: 10.6 (Inductor) terminal t2 is connected on net N14 to 26.2 (Terminal) terminal t1.

### 26.2 (Terminal)
- Connected nets: N14
- Connected components: 10.6 (Inductor) via N14
- 26.2:t1: 26.2 (Terminal) terminal t1 is connected on net N14 to 10.6 (Inductor) terminal t2.

## Net-Centric Topology
- N1: Net N1 connects 16.1 (Mosfet) terminal G, 26.1 (Terminal) terminal t1.
- N2: Net N2 connects 16.1 (Mosfet) terminal S, 9.1 (GND) terminal t1.
- N3: Net N3 connects 10.1 (Inductor) terminal t1, 16.1 (Mosfet) terminal D.
- N4: Net N4 connects 22.1 (Resistor) terminal t2, 9.2 (GND) terminal t1.
- N5: Net N5 connects 10.2 (Inductor) terminal t1, 22.1 (Resistor) terminal t1.
- N6: Net N6 connects 10.1 (Inductor) terminal t2, 10.3 (Inductor) terminal t1, 16.2 (Mosfet) terminal G.
- N7: Net N7 connects 10.2 (Inductor) terminal t2, 10.4 (Inductor) terminal t1, 16.2 (Mosfet) terminal D.
- N8: Net N8 connects 16.2 (Mosfet) terminal S, 9.3 (GND) terminal t1.
- N9: Net N9 connects 10.3 (Inductor) terminal t2, 10.5 (Inductor) terminal t1, 16.3 (Mosfet) terminal G.
- N10: Net N10 connects 16.3 (Mosfet) terminal S, 9.4 (GND) terminal t1.
- N11: Net N11 connects 10.4 (Inductor) terminal t2, 10.6 (Inductor) terminal t1, 16.3 (Mosfet) terminal D.
- N12: Net N12 connects 10.5 (Inductor) terminal t2, 22.2 (Resistor) terminal t1.
- N13: Net N13 connects 22.2 (Resistor) terminal t2, 9.5 (GND) terminal t1.
- N14: Net N14 connects 10.6 (Inductor) terminal t2, 26.2 (Terminal) terminal t1.

## Reasoning Hints
- Check whether supply nets, especially implicit ones, are plausible for the connected components.
- Look for components whose terminals connect to unexpected peers or to only one modeled net when that seems electrically unusual.
- Use the component-centric section to follow signal flow and the net-centric section to verify shared connectivity.

## Companion Files
- `*_simplified.json`: same information in structured JSON form.
- `*_graph.json`: full graph export with nodes and edges.
