# LLM Context - Diagram 5

## Purpose
Use this context to reason about the circuit topology and identify possible faults, broken components, abnormal connections, or inconsistent supply paths.

## Overview
- Diagram ID: 5
- Image: 5.jpg
- Pipeline variant: topology_v7_npn_transistor_mosfet
- Components: 13
- Terminals: 25
- Nets: 6
- Connections: 25
- Suspicious terminal matches: 0
- Unmatched terminals: 0
- Implicit supply nets: 0

## Diagnostic Notes
- No implicit supply nets, suspicious terminal matches, or unmatched terminals were detected.

## Component-Centric Topology

### 26.1 (Terminal)
- Connected nets: N3
- Connected components: 18.1 (NPN_Transistor) via N3; 18.4 (NPN_Transistor) via N3; 22.3 (Resistor) via N3; 26.3 (Terminal) via N3; 9.1 (GND) via N3
- 26.1:t1: 26.1 (Terminal) terminal t1 is connected on net N3 together with 18.1 (NPN_Transistor) terminal E, 18.4 (NPN_Transistor) terminal E, 22.3 (Resistor) terminal t2, 26.3 (Terminal) terminal t1, 9.1 (GND) terminal t1.

### 26.2 (Terminal)
- Connected nets: N2
- Connected components: 18.3 (NPN_Transistor) via N2; 18.4 (NPN_Transistor) via N2; 22.1 (Resistor) via N2; 22.2 (Resistor) via N2; 26.4 (Terminal) via N2; 6.1 (Current_Source) via N2
- 26.2:t1: 26.2 (Terminal) terminal t1 is connected on net N2 together with 18.3 (NPN_Transistor) terminal B, 18.3 (NPN_Transistor) terminal E, 18.4 (NPN_Transistor) terminal C, 22.1 (Resistor) terminal t1, 22.2 (Resistor) terminal t1, 26.4 (Terminal) terminal t1, 6.1 (Current_Source) terminal t2.

### 22.1 (Resistor)
- Connected nets: N1, N2
- Connected components: 18.1 (NPN_Transistor) via N1; 18.2 (NPN_Transistor) via N1; 18.3 (NPN_Transistor) via N2; 18.4 (NPN_Transistor) via N2; 22.2 (Resistor) via N2; 26.2 (Terminal) via N2; 26.4 (Terminal) via N2; 6.1 (Current_Source) via N2
- 22.1:t1: 22.1 (Resistor) terminal t1 is connected on net N2 together with 18.3 (NPN_Transistor) terminal B, 18.3 (NPN_Transistor) terminal E, 18.4 (NPN_Transistor) terminal C, 22.2 (Resistor) terminal t1, 26.2 (Terminal) terminal t1, 26.4 (Terminal) terminal t1, 6.1 (Current_Source) terminal t2.
- 22.1:t2: 22.1 (Resistor) terminal t2 is connected on net N1 together with 18.1 (NPN_Transistor) terminal B, 18.1 (NPN_Transistor) terminal C, 18.2 (NPN_Transistor) terminal B.

### 18.1 (NPN_Transistor)
- Connected nets: N1, N3
- Connected components: 18.2 (NPN_Transistor) via N1; 18.4 (NPN_Transistor) via N3; 22.1 (Resistor) via N1; 22.3 (Resistor) via N3; 26.1 (Terminal) via N3; 26.3 (Terminal) via N3; 9.1 (GND) via N3
- 18.1:B: 18.1 (NPN_Transistor) terminal B is connected on net N1 together with 18.1 (NPN_Transistor) terminal C, 18.2 (NPN_Transistor) terminal B, 22.1 (Resistor) terminal t2.
- 18.1:C: 18.1 (NPN_Transistor) terminal C is connected on net N1 together with 18.1 (NPN_Transistor) terminal B, 18.2 (NPN_Transistor) terminal B, 22.1 (Resistor) terminal t2.
- 18.1:E: 18.1 (NPN_Transistor) terminal E is connected on net N3 together with 18.4 (NPN_Transistor) terminal E, 22.3 (Resistor) terminal t2, 26.1 (Terminal) terminal t1, 26.3 (Terminal) terminal t1, 9.1 (GND) terminal t1.

### 18.2 (NPN_Transistor)
- Connected nets: N1, N4, N5
- Connected components: 18.1 (NPN_Transistor) via N1; 18.4 (NPN_Transistor) via N5; 22.1 (Resistor) via N1; 22.2 (Resistor) via N5; 22.3 (Resistor) via N4
- 18.2:B: 18.2 (NPN_Transistor) terminal B is connected on net N1 together with 18.1 (NPN_Transistor) terminal B, 18.1 (NPN_Transistor) terminal C, 22.1 (Resistor) terminal t2.
- 18.2:C: 18.2 (NPN_Transistor) terminal C is connected on net N5 together with 18.4 (NPN_Transistor) terminal B, 22.2 (Resistor) terminal t2.
- 18.2:E: 18.2 (NPN_Transistor) terminal E is connected on net N4 to 22.3 (Resistor) terminal t1.

### 22.2 (Resistor)
- Connected nets: N2, N5
- Connected components: 18.2 (NPN_Transistor) via N5; 18.3 (NPN_Transistor) via N2; 18.4 (NPN_Transistor) via N2, N5; 22.1 (Resistor) via N2; 26.2 (Terminal) via N2; 26.4 (Terminal) via N2; 6.1 (Current_Source) via N2
- 22.2:t1: 22.2 (Resistor) terminal t1 is connected on net N2 together with 18.3 (NPN_Transistor) terminal B, 18.3 (NPN_Transistor) terminal E, 18.4 (NPN_Transistor) terminal C, 22.1 (Resistor) terminal t1, 26.2 (Terminal) terminal t1, 26.4 (Terminal) terminal t1, 6.1 (Current_Source) terminal t2.
- 22.2:t2: 22.2 (Resistor) terminal t2 is connected on net N5 together with 18.2 (NPN_Transistor) terminal C, 18.4 (NPN_Transistor) terminal B.

### 22.3 (Resistor)
- Connected nets: N3, N4
- Connected components: 18.1 (NPN_Transistor) via N3; 18.2 (NPN_Transistor) via N4; 18.4 (NPN_Transistor) via N3; 26.1 (Terminal) via N3; 26.3 (Terminal) via N3; 9.1 (GND) via N3
- 22.3:t1: 22.3 (Resistor) terminal t1 is connected on net N4 to 18.2 (NPN_Transistor) terminal E.
- 22.3:t2: 22.3 (Resistor) terminal t2 is connected on net N3 together with 18.1 (NPN_Transistor) terminal E, 18.4 (NPN_Transistor) terminal E, 26.1 (Terminal) terminal t1, 26.3 (Terminal) terminal t1, 9.1 (GND) terminal t1.

### 18.3 (NPN_Transistor)
- Connected nets: N2, N6
- Connected components: 18.4 (NPN_Transistor) via N2; 22.1 (Resistor) via N2; 22.2 (Resistor) via N2; 26.2 (Terminal) via N2; 26.4 (Terminal) via N2; 6.1 (Current_Source) via N2, N6
- 18.3:B: 18.3 (NPN_Transistor) terminal B is connected on net N2 together with 18.3 (NPN_Transistor) terminal E, 18.4 (NPN_Transistor) terminal C, 22.1 (Resistor) terminal t1, 22.2 (Resistor) terminal t1, 26.2 (Terminal) terminal t1, 26.4 (Terminal) terminal t1, 6.1 (Current_Source) terminal t2.
- 18.3:C: 18.3 (NPN_Transistor) terminal C is connected on net N6 to 6.1 (Current_Source) terminal t1.
- 18.3:E: 18.3 (NPN_Transistor) terminal E is connected on net N2 together with 18.3 (NPN_Transistor) terminal B, 18.4 (NPN_Transistor) terminal C, 22.1 (Resistor) terminal t1, 22.2 (Resistor) terminal t1, 26.2 (Terminal) terminal t1, 26.4 (Terminal) terminal t1, 6.1 (Current_Source) terminal t2.

### 9.1 (GND)
- Connected nets: N3
- Connected components: 18.1 (NPN_Transistor) via N3; 18.4 (NPN_Transistor) via N3; 22.3 (Resistor) via N3; 26.1 (Terminal) via N3; 26.3 (Terminal) via N3
- 9.1:t1: 9.1 (GND) terminal t1 is connected on net N3 together with 18.1 (NPN_Transistor) terminal E, 18.4 (NPN_Transistor) terminal E, 22.3 (Resistor) terminal t2, 26.1 (Terminal) terminal t1, 26.3 (Terminal) terminal t1.

### 18.4 (NPN_Transistor)
- Connected nets: N2, N3, N5
- Connected components: 18.1 (NPN_Transistor) via N3; 18.2 (NPN_Transistor) via N5; 18.3 (NPN_Transistor) via N2; 22.1 (Resistor) via N2; 22.2 (Resistor) via N2, N5; 22.3 (Resistor) via N3; 26.1 (Terminal) via N3; 26.2 (Terminal) via N2; 26.3 (Terminal) via N3; 26.4 (Terminal) via N2; 6.1 (Current_Source) via N2; 9.1 (GND) via N3
- 18.4:B: 18.4 (NPN_Transistor) terminal B is connected on net N5 together with 18.2 (NPN_Transistor) terminal C, 22.2 (Resistor) terminal t2.
- 18.4:C: 18.4 (NPN_Transistor) terminal C is connected on net N2 together with 18.3 (NPN_Transistor) terminal B, 18.3 (NPN_Transistor) terminal E, 22.1 (Resistor) terminal t1, 22.2 (Resistor) terminal t1, 26.2 (Terminal) terminal t1, 26.4 (Terminal) terminal t1, 6.1 (Current_Source) terminal t2.
- 18.4:E: 18.4 (NPN_Transistor) terminal E is connected on net N3 together with 18.1 (NPN_Transistor) terminal E, 22.3 (Resistor) terminal t2, 26.1 (Terminal) terminal t1, 26.3 (Terminal) terminal t1, 9.1 (GND) terminal t1.

### 6.1 (Current_Source)
- Connected nets: N2, N6
- Connected components: 18.3 (NPN_Transistor) via N2, N6; 18.4 (NPN_Transistor) via N2; 22.1 (Resistor) via N2; 22.2 (Resistor) via N2; 26.2 (Terminal) via N2; 26.4 (Terminal) via N2
- 6.1:t1: 6.1 (Current_Source) terminal t1 is connected on net N6 to 18.3 (NPN_Transistor) terminal C.
- 6.1:t2: 6.1 (Current_Source) terminal t2 is connected on net N2 together with 18.3 (NPN_Transistor) terminal B, 18.3 (NPN_Transistor) terminal E, 18.4 (NPN_Transistor) terminal C, 22.1 (Resistor) terminal t1, 22.2 (Resistor) terminal t1, 26.2 (Terminal) terminal t1, 26.4 (Terminal) terminal t1.

### 26.3 (Terminal)
- Connected nets: N3
- Connected components: 18.1 (NPN_Transistor) via N3; 18.4 (NPN_Transistor) via N3; 22.3 (Resistor) via N3; 26.1 (Terminal) via N3; 9.1 (GND) via N3
- 26.3:t1: 26.3 (Terminal) terminal t1 is connected on net N3 together with 18.1 (NPN_Transistor) terminal E, 18.4 (NPN_Transistor) terminal E, 22.3 (Resistor) terminal t2, 26.1 (Terminal) terminal t1, 9.1 (GND) terminal t1.

### 26.4 (Terminal)
- Connected nets: N2
- Connected components: 18.3 (NPN_Transistor) via N2; 18.4 (NPN_Transistor) via N2; 22.1 (Resistor) via N2; 22.2 (Resistor) via N2; 26.2 (Terminal) via N2; 6.1 (Current_Source) via N2
- 26.4:t1: 26.4 (Terminal) terminal t1 is connected on net N2 together with 18.3 (NPN_Transistor) terminal B, 18.3 (NPN_Transistor) terminal E, 18.4 (NPN_Transistor) terminal C, 22.1 (Resistor) terminal t1, 22.2 (Resistor) terminal t1, 26.2 (Terminal) terminal t1, 6.1 (Current_Source) terminal t2.

## Net-Centric Topology
- N1: Net N1 connects 18.1 (NPN_Transistor) terminal B, 18.1 (NPN_Transistor) terminal C, 18.2 (NPN_Transistor) terminal B, 22.1 (Resistor) terminal t2.
- N2: Net N2 connects 18.3 (NPN_Transistor) terminal B, 18.3 (NPN_Transistor) terminal E, 18.4 (NPN_Transistor) terminal C, 22.1 (Resistor) terminal t1, 22.2 (Resistor) terminal t1, 26.2 (Terminal) terminal t1, 26.4 (Terminal) terminal t1, 6.1 (Current_Source) terminal t2.
- N3: Net N3 connects 18.1 (NPN_Transistor) terminal E, 18.4 (NPN_Transistor) terminal E, 22.3 (Resistor) terminal t2, 26.1 (Terminal) terminal t1, 26.3 (Terminal) terminal t1, 9.1 (GND) terminal t1.
- N4: Net N4 connects 18.2 (NPN_Transistor) terminal E, 22.3 (Resistor) terminal t1.
- N5: Net N5 connects 18.2 (NPN_Transistor) terminal C, 18.4 (NPN_Transistor) terminal B, 22.2 (Resistor) terminal t2.
- N6: Net N6 connects 18.3 (NPN_Transistor) terminal C, 6.1 (Current_Source) terminal t1.

## Reasoning Hints
- Check whether supply nets, especially implicit ones, are plausible for the connected components.
- Look for components whose terminals connect to unexpected peers or to only one modeled net when that seems electrically unusual.
- Use the component-centric section to follow signal flow and the net-centric section to verify shared connectivity.

## Companion Files
- `*_simplified.json`: same information in structured JSON form.
- `*_graph.json`: full graph export with nodes and edges.
