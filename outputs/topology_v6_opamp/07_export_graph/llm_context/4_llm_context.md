# LLM Context - Diagram 4

## Purpose
Use this context to reason about the circuit topology and identify possible faults, broken components, abnormal connections, or inconsistent supply paths.

## Overview
- Diagram ID: 4
- Image: 4.jpg
- Pipeline variant: topology_v6_opamp
- Components: 8
- Terminals: 14
- Nets: 5
- Connections: 14
- Suspicious terminal matches: 0
- Unmatched terminals: 0
- Implicit supply nets: 0

## Diagnostic Notes
- No implicit supply nets, suspicious terminal matches, or unmatched terminals were detected.

## Component-Centric Topology

### 9.1 (GND)
- Connected nets: N1
- Connected components: 4.1 (Capacitor) via N1
- 9.1:t1: 9.1 (GND) terminal t1 is connected on net N1 to 4.1 (Capacitor) terminal t1.

### 4.1 (Capacitor)
- Connected nets: N1, N2
- Connected components: 19.1 (Operational_Amplifier) via N2; 4.2 (Capacitor) via N2; 4.3 (Capacitor) via N2; 9.1 (GND) via N1
- 4.1:t1: 4.1 (Capacitor) terminal t1 is connected on net N1 to 9.1 (GND) terminal t1.
- 4.1:t2: 4.1 (Capacitor) terminal t2 is connected on net N2 together with 19.1 (Operational_Amplifier) terminal in1, 4.2 (Capacitor) terminal t1, 4.3 (Capacitor) terminal t1.

### 4.2 (Capacitor)
- Connected nets: N2, N3
- Connected components: 19.1 (Operational_Amplifier) via N2, N3; 4.1 (Capacitor) via N2; 4.3 (Capacitor) via N2; 9.2 (GND) via N3
- 4.2:t1: 4.2 (Capacitor) terminal t1 is connected on net N2 together with 19.1 (Operational_Amplifier) terminal in1, 4.1 (Capacitor) terminal t2, 4.3 (Capacitor) terminal t1.
- 4.2:t2: 4.2 (Capacitor) terminal t2 is connected on net N3 together with 19.1 (Operational_Amplifier) terminal in2, 9.2 (GND) terminal t1.

### 9.2 (GND)
- Connected nets: N3
- Connected components: 19.1 (Operational_Amplifier) via N3; 4.2 (Capacitor) via N3
- 9.2:t1: 9.2 (GND) terminal t1 is connected on net N3 together with 19.1 (Operational_Amplifier) terminal in2, 4.2 (Capacitor) terminal t2.

### 19.1 (Operational_Amplifier)
- Connected nets: N2, N3, N4
- Connected components: 4.1 (Capacitor) via N2; 4.2 (Capacitor) via N2, N3; 4.3 (Capacitor) via N2, N4; 4.4 (Capacitor) via N4; 9.2 (GND) via N3
- 19.1:in1: 19.1 (Operational_Amplifier) terminal in1 is connected on net N2 together with 4.1 (Capacitor) terminal t2, 4.2 (Capacitor) terminal t1, 4.3 (Capacitor) terminal t1.
- 19.1:in2: 19.1 (Operational_Amplifier) terminal in2 is connected on net N3 together with 4.2 (Capacitor) terminal t2, 9.2 (GND) terminal t1.
- 19.1:out: 19.1 (Operational_Amplifier) terminal out is connected on net N4 together with 4.3 (Capacitor) terminal t2, 4.4 (Capacitor) terminal t1.

### 4.3 (Capacitor)
- Connected nets: N2, N4
- Connected components: 19.1 (Operational_Amplifier) via N2, N4; 4.1 (Capacitor) via N2; 4.2 (Capacitor) via N2; 4.4 (Capacitor) via N4
- 4.3:t1: 4.3 (Capacitor) terminal t1 is connected on net N2 together with 19.1 (Operational_Amplifier) terminal in1, 4.1 (Capacitor) terminal t2, 4.2 (Capacitor) terminal t1.
- 4.3:t2: 4.3 (Capacitor) terminal t2 is connected on net N4 together with 19.1 (Operational_Amplifier) terminal out, 4.4 (Capacitor) terminal t1.

### 4.4 (Capacitor)
- Connected nets: N4, N5
- Connected components: 19.1 (Operational_Amplifier) via N4; 4.3 (Capacitor) via N4; 9.3 (GND) via N5
- 4.4:t1: 4.4 (Capacitor) terminal t1 is connected on net N4 together with 19.1 (Operational_Amplifier) terminal out, 4.3 (Capacitor) terminal t2.
- 4.4:t2: 4.4 (Capacitor) terminal t2 is connected on net N5 to 9.3 (GND) terminal t1.

### 9.3 (GND)
- Connected nets: N5
- Connected components: 4.4 (Capacitor) via N5
- 9.3:t1: 9.3 (GND) terminal t1 is connected on net N5 to 4.4 (Capacitor) terminal t2.

## Net-Centric Topology
- N1: Net N1 connects 4.1 (Capacitor) terminal t1, 9.1 (GND) terminal t1.
- N2: Net N2 connects 19.1 (Operational_Amplifier) terminal in1, 4.1 (Capacitor) terminal t2, 4.2 (Capacitor) terminal t1, 4.3 (Capacitor) terminal t1.
- N3: Net N3 connects 19.1 (Operational_Amplifier) terminal in2, 4.2 (Capacitor) terminal t2, 9.2 (GND) terminal t1.
- N4: Net N4 connects 19.1 (Operational_Amplifier) terminal out, 4.3 (Capacitor) terminal t2, 4.4 (Capacitor) terminal t1.
- N5: Net N5 connects 4.4 (Capacitor) terminal t2, 9.3 (GND) terminal t1.

## Reasoning Hints
- Check whether supply nets, especially implicit ones, are plausible for the connected components.
- Look for components whose terminals connect to unexpected peers or to only one modeled net when that seems electrically unusual.
- Use the component-centric section to follow signal flow and the net-centric section to verify shared connectivity.

## Companion Files
- `*_simplified.json`: same information in structured JSON form.
- `*_graph.json`: full graph export with nodes and edges.
