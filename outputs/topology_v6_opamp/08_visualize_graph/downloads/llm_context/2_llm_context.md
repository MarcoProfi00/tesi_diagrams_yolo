# LLM Context - Diagram 2

## Purpose
Use this context to reason about the circuit topology and identify possible faults, broken components, abnormal connections, or inconsistent supply paths.

## Overview
- Diagram ID: 2
- Image: 2.jpg
- Pipeline variant: topology_v6_opamp
- Components: 10
- Terminals: 22
- Nets: 7
- Connections: 22
- Suspicious terminal matches: 0
- Unmatched terminals: 0
- Implicit supply nets: 1

## Diagnostic Notes
- 1 implicit supply net(s) detected.

### Implicit Supply Matches
- 19.1:aux1 on 19.1 (Operational_Amplifier) uses N7 with reason `missing_terminal_symbol`.

## Component-Centric Topology

### 18.1 (NPN_Transistor)
- Connected nets: N3, N4
- Connected components: 18.2 (NPN_Transistor) via N4; 19.1 (Operational_Amplifier) via N3, N4; 22.1 (Resistor) via N3; 22.2 (Resistor) via N3; 22.3 (Resistor) via N3; 26.2 (Terminal) via N4; 31.1 (Voltage_Source) via N3; 9.1 (GND) via N4
- 18.1:t1: 18.1 (NPN_Transistor) terminal t1 is connected on net N4 together with 18.1 (NPN_Transistor) terminal t3, 18.2 (NPN_Transistor) terminal t3, 19.1 (Operational_Amplifier) terminal aux2, 26.2 (Terminal) terminal t1, 9.1 (GND) terminal t1.
- 18.1:t2: 18.1 (NPN_Transistor) terminal t2 is connected on net N3 together with 19.1 (Operational_Amplifier) terminal in2, 22.1 (Resistor) terminal t2, 22.2 (Resistor) terminal t2, 22.3 (Resistor) terminal t1, 31.1 (Voltage_Source) terminal t1.
- 18.1:t3: 18.1 (NPN_Transistor) terminal t3 is connected on net N4 together with 18.1 (NPN_Transistor) terminal t1, 18.2 (NPN_Transistor) terminal t3, 19.1 (Operational_Amplifier) terminal aux2, 26.2 (Terminal) terminal t1, 9.1 (GND) terminal t1.

### 22.1 (Resistor)
- Connected nets: N3, N5
- Connected components: 18.1 (NPN_Transistor) via N3; 19.1 (Operational_Amplifier) via N3, N5; 22.2 (Resistor) via N3, N5; 22.3 (Resistor) via N3; 26.1 (Terminal) via N5; 31.1 (Voltage_Source) via N3
- 22.1:t1: 22.1 (Resistor) terminal t1 is connected on net N5 together with 19.1 (Operational_Amplifier) terminal out, 22.2 (Resistor) terminal t1, 26.1 (Terminal) terminal t1.
- 22.1:t2: 22.1 (Resistor) terminal t2 is connected on net N3 together with 18.1 (NPN_Transistor) terminal t2, 19.1 (Operational_Amplifier) terminal in2, 22.2 (Resistor) terminal t2, 22.3 (Resistor) terminal t1, 31.1 (Voltage_Source) terminal t1.

### 18.2 (NPN_Transistor)
- Connected nets: N1, N2, N4
- Connected components: 18.1 (NPN_Transistor) via N4; 19.1 (Operational_Amplifier) via N4; 22.3 (Resistor) via N2; 26.2 (Terminal) via N4; 9.1 (GND) via N4
- 18.2:t1: 18.2 (NPN_Transistor) terminal t1 is the only modeled terminal on net N1.
- 18.2:t2: 18.2 (NPN_Transistor) terminal t2 is connected on net N2 to 22.3 (Resistor) terminal t2.
- 18.2:t3: 18.2 (NPN_Transistor) terminal t3 is connected on net N4 together with 18.1 (NPN_Transistor) terminal t1, 18.1 (NPN_Transistor) terminal t3, 19.1 (Operational_Amplifier) terminal aux2, 26.2 (Terminal) terminal t1, 9.1 (GND) terminal t1.

### 22.2 (Resistor)
- Connected nets: N3, N5
- Connected components: 18.1 (NPN_Transistor) via N3; 19.1 (Operational_Amplifier) via N3, N5; 22.1 (Resistor) via N3, N5; 22.3 (Resistor) via N3; 26.1 (Terminal) via N5; 31.1 (Voltage_Source) via N3
- 22.2:t1: 22.2 (Resistor) terminal t1 is connected on net N5 together with 19.1 (Operational_Amplifier) terminal out, 22.1 (Resistor) terminal t1, 26.1 (Terminal) terminal t1.
- 22.2:t2: 22.2 (Resistor) terminal t2 is connected on net N3 together with 18.1 (NPN_Transistor) terminal t2, 19.1 (Operational_Amplifier) terminal in2, 22.1 (Resistor) terminal t2, 22.3 (Resistor) terminal t1, 31.1 (Voltage_Source) terminal t1.

### 9.1 (GND)
- Connected nets: N4
- Connected components: 18.1 (NPN_Transistor) via N4; 18.2 (NPN_Transistor) via N4; 19.1 (Operational_Amplifier) via N4; 26.2 (Terminal) via N4
- 9.1:t1: 9.1 (GND) terminal t1 is connected on net N4 together with 18.1 (NPN_Transistor) terminal t1, 18.1 (NPN_Transistor) terminal t3, 18.2 (NPN_Transistor) terminal t3, 19.1 (Operational_Amplifier) terminal aux2, 26.2 (Terminal) terminal t1.

### 22.3 (Resistor)
- Connected nets: N2, N3
- Connected components: 18.1 (NPN_Transistor) via N3; 18.2 (NPN_Transistor) via N2; 19.1 (Operational_Amplifier) via N3; 22.1 (Resistor) via N3; 22.2 (Resistor) via N3; 31.1 (Voltage_Source) via N3
- 22.3:t1: 22.3 (Resistor) terminal t1 is connected on net N3 together with 18.1 (NPN_Transistor) terminal t2, 19.1 (Operational_Amplifier) terminal in2, 22.1 (Resistor) terminal t2, 22.2 (Resistor) terminal t2, 31.1 (Voltage_Source) terminal t1.
- 22.3:t2: 22.3 (Resistor) terminal t2 is connected on net N2 to 18.2 (NPN_Transistor) terminal t2.

### 31.1 (Voltage_Source)
- Connected nets: N3, N6
- Connected components: 18.1 (NPN_Transistor) via N3; 19.1 (Operational_Amplifier) via N3, N6; 22.1 (Resistor) via N3; 22.2 (Resistor) via N3; 22.3 (Resistor) via N3
- 31.1:t1: 31.1 (Voltage_Source) terminal t1 is connected on net N3 together with 18.1 (NPN_Transistor) terminal t2, 19.1 (Operational_Amplifier) terminal in2, 22.1 (Resistor) terminal t2, 22.2 (Resistor) terminal t2, 22.3 (Resistor) terminal t1.
- 31.1:t2: 31.1 (Voltage_Source) terminal t2 is connected on net N6 to 19.1 (Operational_Amplifier) terminal in1.

### 19.1 (Operational_Amplifier)
- Connected nets: N3, N4, N5, N6, N7
- Connected components: 18.1 (NPN_Transistor) via N3, N4; 18.2 (NPN_Transistor) via N4; 22.1 (Resistor) via N3, N5; 22.2 (Resistor) via N3, N5; 22.3 (Resistor) via N3; 26.1 (Terminal) via N5; 26.2 (Terminal) via N4; 31.1 (Voltage_Source) via N3, N6; 9.1 (GND) via N4
- 19.1:aux1: 19.1 (Operational_Amplifier) terminal aux1 is connected to implicit supply net N7 (missing_terminal_symbol); no explicit peer terminal is modeled.
- 19.1:aux2: 19.1 (Operational_Amplifier) terminal aux2 is connected on net N4 together with 18.1 (NPN_Transistor) terminal t1, 18.1 (NPN_Transistor) terminal t3, 18.2 (NPN_Transistor) terminal t3, 26.2 (Terminal) terminal t1, 9.1 (GND) terminal t1.
- 19.1:in1: 19.1 (Operational_Amplifier) terminal in1 is connected on net N6 to 31.1 (Voltage_Source) terminal t2.
- 19.1:in2: 19.1 (Operational_Amplifier) terminal in2 is connected on net N3 together with 18.1 (NPN_Transistor) terminal t2, 22.1 (Resistor) terminal t2, 22.2 (Resistor) terminal t2, 22.3 (Resistor) terminal t1, 31.1 (Voltage_Source) terminal t1.
- 19.1:out: 19.1 (Operational_Amplifier) terminal out is connected on net N5 together with 22.1 (Resistor) terminal t1, 22.2 (Resistor) terminal t1, 26.1 (Terminal) terminal t1.

### 26.1 (Terminal)
- Connected nets: N5
- Connected components: 19.1 (Operational_Amplifier) via N5; 22.1 (Resistor) via N5; 22.2 (Resistor) via N5
- 26.1:t1: 26.1 (Terminal) terminal t1 is connected on net N5 together with 19.1 (Operational_Amplifier) terminal out, 22.1 (Resistor) terminal t1, 22.2 (Resistor) terminal t1.

### 26.2 (Terminal)
- Connected nets: N4
- Connected components: 18.1 (NPN_Transistor) via N4; 18.2 (NPN_Transistor) via N4; 19.1 (Operational_Amplifier) via N4; 9.1 (GND) via N4
- 26.2:t1: 26.2 (Terminal) terminal t1 is connected on net N4 together with 18.1 (NPN_Transistor) terminal t1, 18.1 (NPN_Transistor) terminal t3, 18.2 (NPN_Transistor) terminal t3, 19.1 (Operational_Amplifier) terminal aux2, 9.1 (GND) terminal t1.

## Net-Centric Topology
- N1: Net N1 currently touches only 18.2 (NPN_Transistor) terminal t1.
- N2: Net N2 connects 18.2 (NPN_Transistor) terminal t2, 22.3 (Resistor) terminal t2.
- N3: Net N3 connects 18.1 (NPN_Transistor) terminal t2, 19.1 (Operational_Amplifier) terminal in2, 22.1 (Resistor) terminal t2, 22.2 (Resistor) terminal t2, 22.3 (Resistor) terminal t1, 31.1 (Voltage_Source) terminal t1.
- N4: Net N4 connects 18.1 (NPN_Transistor) terminal t1, 18.1 (NPN_Transistor) terminal t3, 18.2 (NPN_Transistor) terminal t3, 19.1 (Operational_Amplifier) terminal aux2, 26.2 (Terminal) terminal t1, 9.1 (GND) terminal t1.
- N5: Net N5 connects 19.1 (Operational_Amplifier) terminal out, 22.1 (Resistor) terminal t1, 22.2 (Resistor) terminal t1, 26.1 (Terminal) terminal t1.
- N6: Net N6 connects 19.1 (Operational_Amplifier) terminal in1, 31.1 (Voltage_Source) terminal t2.
- N7: Net N7 is an implicit supply connection (missing_terminal_symbol) attached to 19.1 (Operational_Amplifier) terminal aux1. Implicit reason: `missing_terminal_symbol`.

## Reasoning Hints
- Check whether supply nets, especially implicit ones, are plausible for the connected components.
- Look for components whose terminals connect to unexpected peers or to only one modeled net when that seems electrically unusual.
- Use the component-centric section to follow signal flow and the net-centric section to verify shared connectivity.

## Companion Files
- `*_simplified.json`: same information in structured JSON form.
- `*_graph.json`: full graph export with nodes and edges.
