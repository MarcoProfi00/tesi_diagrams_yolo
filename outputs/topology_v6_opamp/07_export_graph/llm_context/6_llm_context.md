# LLM Context - Diagram 6

## Purpose
Use this context to reason about the circuit topology and identify possible faults, broken components, abnormal connections, or inconsistent supply paths.

## Overview
- Diagram ID: 6
- Image: 6.jpg
- Pipeline variant: topology_v6_opamp
- Components: 9
- Terminals: 16
- Nets: 7
- Connections: 16
- Suspicious terminal matches: 0
- Unmatched terminals: 0
- Implicit supply nets: 0

## Diagnostic Notes
- No implicit supply nets, suspicious terminal matches, or unmatched terminals were detected.

## Component-Centric Topology

### 31.1 (Voltage_Source)
- Connected nets: N1, N2
- Connected components: 22.1 (Resistor) via N2; 9.1 (GND) via N1
- 31.1:t1: 31.1 (Voltage_Source) terminal t1 is connected on net N2 to 22.1 (Resistor) terminal t1.
- 31.1:t2: 31.1 (Voltage_Source) terminal t2 is connected on net N1 to 9.1 (GND) terminal t1.

### 9.1 (GND)
- Connected nets: N1
- Connected components: 31.1 (Voltage_Source) via N1
- 9.1:t1: 9.1 (GND) terminal t1 is connected on net N1 to 31.1 (Voltage_Source) terminal t2.

### 22.1 (Resistor)
- Connected nets: N2, N4
- Connected components: 19.1 (Operational_Amplifier) via N4; 22.2 (Resistor) via N4; 31.1 (Voltage_Source) via N2
- 22.1:t1: 22.1 (Resistor) terminal t1 is connected on net N2 to 31.1 (Voltage_Source) terminal t1.
- 22.1:t2: 22.1 (Resistor) terminal t2 is connected on net N4 together with 19.1 (Operational_Amplifier) terminal in1, 22.2 (Resistor) terminal t1.

### 9.2 (GND)
- Connected nets: N3
- Connected components: 19.1 (Operational_Amplifier) via N3
- 9.2:t1: 9.2 (GND) terminal t1 is connected on net N3 to 19.1 (Operational_Amplifier) terminal in2.

### 22.2 (Resistor)
- Connected nets: N4, N7
- Connected components: 19.1 (Operational_Amplifier) via N4, N7; 22.1 (Resistor) via N4; 26.3 (Terminal) via N7
- 22.2:t1: 22.2 (Resistor) terminal t1 is connected on net N4 together with 19.1 (Operational_Amplifier) terminal in1, 22.1 (Resistor) terminal t2.
- 22.2:t2: 22.2 (Resistor) terminal t2 is connected on net N7 together with 19.1 (Operational_Amplifier) terminal out, 26.3 (Terminal) terminal t1.

### 19.1 (Operational_Amplifier)
- Connected nets: N3, N4, N5, N6, N7
- Connected components: 22.1 (Resistor) via N4; 22.2 (Resistor) via N4, N7; 26.1 (Terminal) via N5; 26.2 (Terminal) via N6; 26.3 (Terminal) via N7; 9.2 (GND) via N3
- 19.1:aux1: 19.1 (Operational_Amplifier) terminal aux1 is connected on net N6 to 26.2 (Terminal) terminal t1.
- 19.1:aux2: 19.1 (Operational_Amplifier) terminal aux2 is connected on net N5 to 26.1 (Terminal) terminal t1.
- 19.1:in1: 19.1 (Operational_Amplifier) terminal in1 is connected on net N4 together with 22.1 (Resistor) terminal t2, 22.2 (Resistor) terminal t1.
- 19.1:in2: 19.1 (Operational_Amplifier) terminal in2 is connected on net N3 to 9.2 (GND) terminal t1.
- 19.1:out: 19.1 (Operational_Amplifier) terminal out is connected on net N7 together with 22.2 (Resistor) terminal t2, 26.3 (Terminal) terminal t1.

### 26.1 (Terminal)
- Connected nets: N5
- Connected components: 19.1 (Operational_Amplifier) via N5
- 26.1:t1: 26.1 (Terminal) terminal t1 is connected on net N5 to 19.1 (Operational_Amplifier) terminal aux2.

### 26.2 (Terminal)
- Connected nets: N6
- Connected components: 19.1 (Operational_Amplifier) via N6
- 26.2:t1: 26.2 (Terminal) terminal t1 is connected on net N6 to 19.1 (Operational_Amplifier) terminal aux1.

### 26.3 (Terminal)
- Connected nets: N7
- Connected components: 19.1 (Operational_Amplifier) via N7; 22.2 (Resistor) via N7
- 26.3:t1: 26.3 (Terminal) terminal t1 is connected on net N7 together with 19.1 (Operational_Amplifier) terminal out, 22.2 (Resistor) terminal t2.

## Net-Centric Topology
- N1: Net N1 connects 31.1 (Voltage_Source) terminal t2, 9.1 (GND) terminal t1.
- N2: Net N2 connects 22.1 (Resistor) terminal t1, 31.1 (Voltage_Source) terminal t1.
- N3: Net N3 connects 19.1 (Operational_Amplifier) terminal in2, 9.2 (GND) terminal t1.
- N4: Net N4 connects 19.1 (Operational_Amplifier) terminal in1, 22.1 (Resistor) terminal t2, 22.2 (Resistor) terminal t1.
- N5: Net N5 connects 19.1 (Operational_Amplifier) terminal aux2, 26.1 (Terminal) terminal t1.
- N6: Net N6 connects 19.1 (Operational_Amplifier) terminal aux1, 26.2 (Terminal) terminal t1.
- N7: Net N7 connects 19.1 (Operational_Amplifier) terminal out, 22.2 (Resistor) terminal t2, 26.3 (Terminal) terminal t1.

## Reasoning Hints
- Check whether supply nets, especially implicit ones, are plausible for the connected components.
- Look for components whose terminals connect to unexpected peers or to only one modeled net when that seems electrically unusual.
- Use the component-centric section to follow signal flow and the net-centric section to verify shared connectivity.

## Companion Files
- `*_simplified.json`: same information in structured JSON form.
- `*_graph.json`: full graph export with nodes and edges.
