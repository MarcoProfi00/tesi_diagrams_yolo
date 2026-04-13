# LLM Context - Diagram 5

## Purpose
Use this context to reason about the circuit topology and identify possible faults, broken components, abnormal connections, or inconsistent supply paths.

## Overview
- Diagram ID: 5
- Image: 5.jpg
- Pipeline variant: topology_v6_opamp
- Components: 20
- Terminals: 35
- Nets: 13
- Connections: 35
- Suspicious terminal matches: 0
- Unmatched terminals: 0
- Implicit supply nets: 0

## Diagnostic Notes
- No implicit supply nets, suspicious terminal matches, or unmatched terminals were detected.

## Component-Centric Topology

### 26.1 (Terminal)
- Connected nets: N2
- Connected components: 22.1 (Resistor) via N2
- 26.1:t1: 26.1 (Terminal) terminal t1 is connected on net N2 to 22.1 (Resistor) terminal t1.

### 26.2 (Terminal)
- Connected nets: N1
- Connected components: 22.2 (Resistor) via N1
- 26.2:t1: 26.2 (Terminal) terminal t1 is connected on net N1 to 22.2 (Resistor) terminal t1.

### 22.1 (Resistor)
- Connected nets: N2, N3
- Connected components: 19.1 (Operational_Amplifier) via N3; 22.2 (Resistor) via N3; 22.3 (Resistor) via N3; 26.1 (Terminal) via N2
- 22.1:t1: 22.1 (Resistor) terminal t1 is connected on net N2 to 26.1 (Terminal) terminal t1.
- 22.1:t2: 22.1 (Resistor) terminal t2 is connected on net N3 together with 19.1 (Operational_Amplifier) terminal in1, 22.2 (Resistor) terminal t2, 22.3 (Resistor) terminal t1.

### 22.2 (Resistor)
- Connected nets: N1, N3
- Connected components: 19.1 (Operational_Amplifier) via N3; 22.1 (Resistor) via N3; 22.3 (Resistor) via N3; 26.2 (Terminal) via N1
- 22.2:t1: 22.2 (Resistor) terminal t1 is connected on net N1 to 26.2 (Terminal) terminal t1.
- 22.2:t2: 22.2 (Resistor) terminal t2 is connected on net N3 together with 19.1 (Operational_Amplifier) terminal in1, 22.1 (Resistor) terminal t2, 22.3 (Resistor) terminal t1.

### 9.1 (GND)
- Connected nets: N4
- Connected components: 19.1 (Operational_Amplifier) via N4
- 9.1:t1: 9.1 (GND) terminal t1 is connected on net N4 to 19.1 (Operational_Amplifier) terminal in2.

### 22.3 (Resistor)
- Connected nets: N3, N7
- Connected components: 19.1 (Operational_Amplifier) via N3, N7; 22.1 (Resistor) via N3; 22.2 (Resistor) via N3; 22.5 (Resistor) via N7
- 22.3:t1: 22.3 (Resistor) terminal t1 is connected on net N3 together with 19.1 (Operational_Amplifier) terminal in1, 22.1 (Resistor) terminal t2, 22.2 (Resistor) terminal t2.
- 22.3:t2: 22.3 (Resistor) terminal t2 is connected on net N7 together with 19.1 (Operational_Amplifier) terminal out, 22.5 (Resistor) terminal t1.

### 19.1 (Operational_Amplifier)
- Connected nets: N3, N4, N5, N6, N7
- Connected components: 22.1 (Resistor) via N3; 22.2 (Resistor) via N3; 22.3 (Resistor) via N3, N7; 22.5 (Resistor) via N7; 26.3 (Terminal) via N5; 26.4 (Terminal) via N6; 9.1 (GND) via N4
- 19.1:aux1: 19.1 (Operational_Amplifier) terminal aux1 is connected on net N6 to 26.4 (Terminal) terminal t1.
- 19.1:aux2: 19.1 (Operational_Amplifier) terminal aux2 is connected on net N5 to 26.3 (Terminal) terminal t1.
- 19.1:in1: 19.1 (Operational_Amplifier) terminal in1 is connected on net N3 together with 22.1 (Resistor) terminal t2, 22.2 (Resistor) terminal t2, 22.3 (Resistor) terminal t1.
- 19.1:in2: 19.1 (Operational_Amplifier) terminal in2 is connected on net N4 to 9.1 (GND) terminal t1.
- 19.1:out: 19.1 (Operational_Amplifier) terminal out is connected on net N7 together with 22.3 (Resistor) terminal t2, 22.5 (Resistor) terminal t1.

### 26.3 (Terminal)
- Connected nets: N5
- Connected components: 19.1 (Operational_Amplifier) via N5
- 26.3:t1: 26.3 (Terminal) terminal t1 is connected on net N5 to 19.1 (Operational_Amplifier) terminal aux2.

### 26.4 (Terminal)
- Connected nets: N6
- Connected components: 19.1 (Operational_Amplifier) via N6
- 26.4:t1: 26.4 (Terminal) terminal t1 is connected on net N6 to 19.1 (Operational_Amplifier) terminal aux1.

### 26.5 (Terminal)
- Connected nets: N9
- Connected components: 22.4 (Resistor) via N9
- 26.5:t1: 26.5 (Terminal) terminal t1 is connected on net N9 to 22.4 (Resistor) terminal t1.

### 26.6 (Terminal)
- Connected nets: N8
- Connected components: 22.6 (Resistor) via N8
- 26.6:t1: 26.6 (Terminal) terminal t1 is connected on net N8 to 22.6 (Resistor) terminal t1.

### 22.4 (Resistor)
- Connected nets: N10, N9
- Connected components: 19.2 (Operational_Amplifier) via N10; 22.5 (Resistor) via N10; 22.6 (Resistor) via N10; 22.7 (Resistor) via N10; 26.5 (Terminal) via N9; 9.2 (GND) via N10
- 22.4:t1: 22.4 (Resistor) terminal t1 is connected on net N9 to 26.5 (Terminal) terminal t1.
- 22.4:t2: 22.4 (Resistor) terminal t2 is connected on net N10 together with 19.2 (Operational_Amplifier) terminal in1, 19.2 (Operational_Amplifier) terminal in2, 22.5 (Resistor) terminal t2, 22.6 (Resistor) terminal t2, 22.7 (Resistor) terminal t1, 9.2 (GND) terminal t1.

### 22.5 (Resistor)
- Connected nets: N10, N7
- Connected components: 19.1 (Operational_Amplifier) via N7; 19.2 (Operational_Amplifier) via N10; 22.3 (Resistor) via N7; 22.4 (Resistor) via N10; 22.6 (Resistor) via N10; 22.7 (Resistor) via N10; 9.2 (GND) via N10
- 22.5:t1: 22.5 (Resistor) terminal t1 is connected on net N7 together with 19.1 (Operational_Amplifier) terminal out, 22.3 (Resistor) terminal t2.
- 22.5:t2: 22.5 (Resistor) terminal t2 is connected on net N10 together with 19.2 (Operational_Amplifier) terminal in1, 19.2 (Operational_Amplifier) terminal in2, 22.4 (Resistor) terminal t2, 22.6 (Resistor) terminal t2, 22.7 (Resistor) terminal t1, 9.2 (GND) terminal t1.

### 22.6 (Resistor)
- Connected nets: N10, N8
- Connected components: 19.2 (Operational_Amplifier) via N10; 22.4 (Resistor) via N10; 22.5 (Resistor) via N10; 22.7 (Resistor) via N10; 26.6 (Terminal) via N8; 9.2 (GND) via N10
- 22.6:t1: 22.6 (Resistor) terminal t1 is connected on net N8 to 26.6 (Terminal) terminal t1.
- 22.6:t2: 22.6 (Resistor) terminal t2 is connected on net N10 together with 19.2 (Operational_Amplifier) terminal in1, 19.2 (Operational_Amplifier) terminal in2, 22.4 (Resistor) terminal t2, 22.5 (Resistor) terminal t2, 22.7 (Resistor) terminal t1, 9.2 (GND) terminal t1.

### 9.2 (GND)
- Connected nets: N10
- Connected components: 19.2 (Operational_Amplifier) via N10; 22.4 (Resistor) via N10; 22.5 (Resistor) via N10; 22.6 (Resistor) via N10; 22.7 (Resistor) via N10
- 9.2:t1: 9.2 (GND) terminal t1 is connected on net N10 together with 19.2 (Operational_Amplifier) terminal in1, 19.2 (Operational_Amplifier) terminal in2, 22.4 (Resistor) terminal t2, 22.5 (Resistor) terminal t2, 22.6 (Resistor) terminal t2, 22.7 (Resistor) terminal t1.

### 22.7 (Resistor)
- Connected nets: N10, N13
- Connected components: 19.2 (Operational_Amplifier) via N10, N13; 22.4 (Resistor) via N10; 22.5 (Resistor) via N10; 22.6 (Resistor) via N10; 26.9 (Terminal) via N13; 9.2 (GND) via N10
- 22.7:t1: 22.7 (Resistor) terminal t1 is connected on net N10 together with 19.2 (Operational_Amplifier) terminal in1, 19.2 (Operational_Amplifier) terminal in2, 22.4 (Resistor) terminal t2, 22.5 (Resistor) terminal t2, 22.6 (Resistor) terminal t2, 9.2 (GND) terminal t1.
- 22.7:t2: 22.7 (Resistor) terminal t2 is connected on net N13 together with 19.2 (Operational_Amplifier) terminal out, 26.9 (Terminal) terminal t1.

### 26.7 (Terminal)
- Connected nets: N11
- Connected components: 19.2 (Operational_Amplifier) via N11
- 26.7:t1: 26.7 (Terminal) terminal t1 is connected on net N11 to 19.2 (Operational_Amplifier) terminal aux2.

### 19.2 (Operational_Amplifier)
- Connected nets: N10, N11, N12, N13
- Connected components: 22.4 (Resistor) via N10; 22.5 (Resistor) via N10; 22.6 (Resistor) via N10; 22.7 (Resistor) via N10, N13; 26.7 (Terminal) via N11; 26.8 (Terminal) via N12; 26.9 (Terminal) via N13; 9.2 (GND) via N10
- 19.2:aux1: 19.2 (Operational_Amplifier) terminal aux1 is connected on net N12 to 26.8 (Terminal) terminal t1.
- 19.2:aux2: 19.2 (Operational_Amplifier) terminal aux2 is connected on net N11 to 26.7 (Terminal) terminal t1.
- 19.2:in1: 19.2 (Operational_Amplifier) terminal in1 is connected on net N10 together with 19.2 (Operational_Amplifier) terminal in2, 22.4 (Resistor) terminal t2, 22.5 (Resistor) terminal t2, 22.6 (Resistor) terminal t2, 22.7 (Resistor) terminal t1, 9.2 (GND) terminal t1.
- 19.2:in2: 19.2 (Operational_Amplifier) terminal in2 is connected on net N10 together with 19.2 (Operational_Amplifier) terminal in1, 22.4 (Resistor) terminal t2, 22.5 (Resistor) terminal t2, 22.6 (Resistor) terminal t2, 22.7 (Resistor) terminal t1, 9.2 (GND) terminal t1.
- 19.2:out: 19.2 (Operational_Amplifier) terminal out is connected on net N13 together with 22.7 (Resistor) terminal t2, 26.9 (Terminal) terminal t1.

### 26.8 (Terminal)
- Connected nets: N12
- Connected components: 19.2 (Operational_Amplifier) via N12
- 26.8:t1: 26.8 (Terminal) terminal t1 is connected on net N12 to 19.2 (Operational_Amplifier) terminal aux1.

### 26.9 (Terminal)
- Connected nets: N13
- Connected components: 19.2 (Operational_Amplifier) via N13; 22.7 (Resistor) via N13
- 26.9:t1: 26.9 (Terminal) terminal t1 is connected on net N13 together with 19.2 (Operational_Amplifier) terminal out, 22.7 (Resistor) terminal t2.

## Net-Centric Topology
- N1: Net N1 connects 22.2 (Resistor) terminal t1, 26.2 (Terminal) terminal t1.
- N2: Net N2 connects 22.1 (Resistor) terminal t1, 26.1 (Terminal) terminal t1.
- N3: Net N3 connects 19.1 (Operational_Amplifier) terminal in1, 22.1 (Resistor) terminal t2, 22.2 (Resistor) terminal t2, 22.3 (Resistor) terminal t1.
- N4: Net N4 connects 19.1 (Operational_Amplifier) terminal in2, 9.1 (GND) terminal t1.
- N5: Net N5 connects 19.1 (Operational_Amplifier) terminal aux2, 26.3 (Terminal) terminal t1.
- N6: Net N6 connects 19.1 (Operational_Amplifier) terminal aux1, 26.4 (Terminal) terminal t1.
- N7: Net N7 connects 19.1 (Operational_Amplifier) terminal out, 22.3 (Resistor) terminal t2, 22.5 (Resistor) terminal t1.
- N8: Net N8 connects 22.6 (Resistor) terminal t1, 26.6 (Terminal) terminal t1.
- N9: Net N9 connects 22.4 (Resistor) terminal t1, 26.5 (Terminal) terminal t1.
- N10: Net N10 connects 19.2 (Operational_Amplifier) terminal in1, 19.2 (Operational_Amplifier) terminal in2, 22.4 (Resistor) terminal t2, 22.5 (Resistor) terminal t2, 22.6 (Resistor) terminal t2, 22.7 (Resistor) terminal t1, 9.2 (GND) terminal t1.
- N11: Net N11 connects 19.2 (Operational_Amplifier) terminal aux2, 26.7 (Terminal) terminal t1.
- N12: Net N12 connects 19.2 (Operational_Amplifier) terminal aux1, 26.8 (Terminal) terminal t1.
- N13: Net N13 connects 19.2 (Operational_Amplifier) terminal out, 22.7 (Resistor) terminal t2, 26.9 (Terminal) terminal t1.

## Reasoning Hints
- Check whether supply nets, especially implicit ones, are plausible for the connected components.
- Look for components whose terminals connect to unexpected peers or to only one modeled net when that seems electrically unusual.
- Use the component-centric section to follow signal flow and the net-centric section to verify shared connectivity.

## Companion Files
- `*_simplified.json`: same information in structured JSON form.
- `*_graph.json`: full graph export with nodes and edges.
