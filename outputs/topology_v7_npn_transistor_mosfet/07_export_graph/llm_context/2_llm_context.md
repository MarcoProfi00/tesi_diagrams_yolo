# LLM Context - Diagram 2

## Purpose
Use this context to reason about the circuit topology and identify possible faults, broken components, abnormal connections, or inconsistent supply paths.

## Overview
- Diagram ID: 2
- Image: 2.jpg
- Pipeline variant: topology_v7_npn_transistor_mosfet
- Components: 14
- Terminals: 29
- Nets: 11
- Connections: 27
- Suspicious terminal matches: 2
- Unmatched terminals: 2
- Implicit supply nets: 0

## Diagnostic Notes
- 2 suspicious terminal match(es) detected.
- 2 terminal(s) are unmatched.

### Suspicious Terminal Matches
- 26.3:t2 on 26.3 (Terminal): status=unmatched, confidence=unmatched, warnings=unmatched_terminal
- 2.1:t1 on 2.1 (Battery): status=unmatched, confidence=unmatched, warnings=unmatched_terminal

### Unmatched Terminals
- 26.3:t2 on 26.3 (Terminal)
- 2.1:t1 on 2.1 (Battery)

## Component-Centric Topology

### 26.1 (Terminal)
- Connected nets: N1
- Connected components: 16.2 (Mosfet) via N1
- 26.1:t1: 26.1 (Terminal) terminal t1 is connected on net N1 to 16.2 (Mosfet) terminal G.

### 26.2 (Terminal)
- Connected nets: N6
- Connected components: 16.1 (Mosfet) via N6; 16.2 (Mosfet) via N6; 16.4 (Mosfet) via N6; 16.6 (Mosfet) via N6; 22.1 (Resistor) via N6
- 26.2:t1: 26.2 (Terminal) terminal t1 is connected on net N6 together with 16.1 (Mosfet) terminal D, 16.2 (Mosfet) terminal S, 16.4 (Mosfet) terminal D, 16.6 (Mosfet) terminal G, 16.6 (Mosfet) terminal S, 22.1 (Resistor) terminal t1, 22.1 (Resistor) terminal t2.

### 16.1 (Mosfet)
- Connected nets: N2, N3, N6
- Connected components: 16.2 (Mosfet) via N6; 16.4 (Mosfet) via N6; 16.6 (Mosfet) via N6; 22.1 (Resistor) via N6; 26.2 (Terminal) via N6; 9.1 (GND) via N3
- 16.1:G: 16.1 (Mosfet) terminal G is the only modeled terminal on net N2.
- 16.1:D: 16.1 (Mosfet) terminal D is connected on net N6 together with 16.2 (Mosfet) terminal S, 16.4 (Mosfet) terminal D, 16.6 (Mosfet) terminal G, 16.6 (Mosfet) terminal S, 22.1 (Resistor) terminal t1, 22.1 (Resistor) terminal t2, 26.2 (Terminal) terminal t1.
- 16.1:S: 16.1 (Mosfet) terminal S is connected on net N3 to 9.1 (GND) terminal t1.

### 16.2 (Mosfet)
- Connected nets: N1, N4, N6
- Connected components: 16.1 (Mosfet) via N6; 16.3 (Mosfet) via N4; 16.4 (Mosfet) via N6; 16.5 (Mosfet) via N4; 16.6 (Mosfet) via N6; 22.1 (Resistor) via N6; 26.1 (Terminal) via N1; 26.2 (Terminal) via N6
- 16.2:G: 16.2 (Mosfet) terminal G is connected on net N1 to 26.1 (Terminal) terminal t1.
- 16.2:D: 16.2 (Mosfet) terminal D is connected on net N4 together with 16.3 (Mosfet) terminal G, 16.3 (Mosfet) terminal D, 16.5 (Mosfet) terminal G.
- 16.2:S: 16.2 (Mosfet) terminal S is connected on net N6 together with 16.1 (Mosfet) terminal D, 16.4 (Mosfet) terminal D, 16.6 (Mosfet) terminal G, 16.6 (Mosfet) terminal S, 22.1 (Resistor) terminal t1, 22.1 (Resistor) terminal t2, 26.2 (Terminal) terminal t1.

### 9.1 (GND)
- Connected nets: N3
- Connected components: 16.1 (Mosfet) via N3
- 9.1:t1: 9.1 (GND) terminal t1 is connected on net N3 to 16.1 (Mosfet) terminal S.

### 16.3 (Mosfet)
- Connected nets: N4, N7
- Connected components: 16.2 (Mosfet) via N4; 16.5 (Mosfet) via N4, N7
- 16.3:G: 16.3 (Mosfet) terminal G is connected on net N4 together with 16.2 (Mosfet) terminal D, 16.3 (Mosfet) terminal D, 16.5 (Mosfet) terminal G.
- 16.3:S: 16.3 (Mosfet) terminal S is connected on net N7 to 16.5 (Mosfet) terminal S.
- 16.3:D: 16.3 (Mosfet) terminal D is connected on net N4 together with 16.2 (Mosfet) terminal D, 16.3 (Mosfet) terminal G, 16.5 (Mosfet) terminal G.

### 22.1 (Resistor)
- Connected nets: N6
- Connected components: 16.1 (Mosfet) via N6; 16.2 (Mosfet) via N6; 16.4 (Mosfet) via N6; 16.6 (Mosfet) via N6; 26.2 (Terminal) via N6
- 22.1:t1: 22.1 (Resistor) terminal t1 is connected on net N6 together with 16.1 (Mosfet) terminal D, 16.2 (Mosfet) terminal S, 16.4 (Mosfet) terminal D, 16.6 (Mosfet) terminal G, 16.6 (Mosfet) terminal S, 22.1 (Resistor) terminal t2, 26.2 (Terminal) terminal t1.
- 22.1:t2: 22.1 (Resistor) terminal t2 is connected on net N6 together with 16.1 (Mosfet) terminal D, 16.2 (Mosfet) terminal S, 16.4 (Mosfet) terminal D, 16.6 (Mosfet) terminal G, 16.6 (Mosfet) terminal S, 22.1 (Resistor) terminal t1, 26.2 (Terminal) terminal t1.

### 16.4 (Mosfet)
- Connected nets: N5, N6, N8
- Connected components: 16.1 (Mosfet) via N6; 16.2 (Mosfet) via N6; 16.6 (Mosfet) via N6; 22.1 (Resistor) via N6; 26.2 (Terminal) via N6; 9.2 (GND) via N8
- 16.4:G: 16.4 (Mosfet) terminal G is the only modeled terminal on net N5.
- 16.4:D: 16.4 (Mosfet) terminal D is connected on net N6 together with 16.1 (Mosfet) terminal D, 16.2 (Mosfet) terminal S, 16.6 (Mosfet) terminal G, 16.6 (Mosfet) terminal S, 22.1 (Resistor) terminal t1, 22.1 (Resistor) terminal t2, 26.2 (Terminal) terminal t1.
- 16.4:S: 16.4 (Mosfet) terminal S is connected on net N8 to 9.2 (GND) terminal t1.

### 16.5 (Mosfet)
- Connected nets: N4, N7, N9
- Connected components: 16.2 (Mosfet) via N4; 16.3 (Mosfet) via N4, N7; 16.6 (Mosfet) via N9; 26.3 (Terminal) via N9
- 16.5:G: 16.5 (Mosfet) terminal G is connected on net N4 together with 16.2 (Mosfet) terminal D, 16.3 (Mosfet) terminal G, 16.3 (Mosfet) terminal D.
- 16.5:S: 16.5 (Mosfet) terminal S is connected on net N7 to 16.3 (Mosfet) terminal S.
- 16.5:D: 16.5 (Mosfet) terminal D is connected on net N9 together with 16.6 (Mosfet) terminal D, 26.3 (Terminal) terminal t1.

### 9.2 (GND)
- Connected nets: N8
- Connected components: 16.4 (Mosfet) via N8
- 9.2:t1: 9.2 (GND) terminal t1 is connected on net N8 to 16.4 (Mosfet) terminal S.

### 16.6 (Mosfet)
- Connected nets: N6, N9
- Connected components: 16.1 (Mosfet) via N6; 16.2 (Mosfet) via N6; 16.4 (Mosfet) via N6; 16.5 (Mosfet) via N9; 22.1 (Resistor) via N6; 26.2 (Terminal) via N6; 26.3 (Terminal) via N9
- 16.6:G: 16.6 (Mosfet) terminal G is connected on net N6 together with 16.1 (Mosfet) terminal D, 16.2 (Mosfet) terminal S, 16.4 (Mosfet) terminal D, 16.6 (Mosfet) terminal S, 22.1 (Resistor) terminal t1, 22.1 (Resistor) terminal t2, 26.2 (Terminal) terminal t1.
- 16.6:D: 16.6 (Mosfet) terminal D is connected on net N9 together with 16.5 (Mosfet) terminal D, 26.3 (Terminal) terminal t1.
- 16.6:S: 16.6 (Mosfet) terminal S is connected on net N6 together with 16.1 (Mosfet) terminal D, 16.2 (Mosfet) terminal S, 16.4 (Mosfet) terminal D, 16.6 (Mosfet) terminal G, 22.1 (Resistor) terminal t1, 22.1 (Resistor) terminal t2, 26.2 (Terminal) terminal t1.

### 26.3 (Terminal)
- Connected nets: N9
- Connected components: 16.5 (Mosfet) via N9; 16.6 (Mosfet) via N9
- 26.3:t1: 26.3 (Terminal) terminal t1 is connected on net N9 together with 16.5 (Mosfet) terminal D, 16.6 (Mosfet) terminal D.
- 26.3:t2: 26.3 (Terminal) terminal t2 is currently unmatched to any net.

### 2.1 (Battery)
- Connected nets: N10
- Connected components: none
- 2.1:t1: 2.1 (Battery) terminal t1 is currently unmatched to any net.
- 2.1:t2: 2.1 (Battery) terminal t2 is the only modeled terminal on net N10.

### 9.3 (GND)
- Connected nets: N11
- Connected components: none
- 9.3:t1: 9.3 (GND) terminal t1 is the only modeled terminal on net N11.

## Net-Centric Topology
- N1: Net N1 connects 16.2 (Mosfet) terminal G, 26.1 (Terminal) terminal t1.
- N2: Net N2 currently touches only 16.1 (Mosfet) terminal G.
- N3: Net N3 connects 16.1 (Mosfet) terminal S, 9.1 (GND) terminal t1.
- N4: Net N4 connects 16.2 (Mosfet) terminal D, 16.3 (Mosfet) terminal G, 16.3 (Mosfet) terminal D, 16.5 (Mosfet) terminal G.
- N5: Net N5 currently touches only 16.4 (Mosfet) terminal G.
- N6: Net N6 connects 16.1 (Mosfet) terminal D, 16.2 (Mosfet) terminal S, 16.4 (Mosfet) terminal D, 16.6 (Mosfet) terminal G, 16.6 (Mosfet) terminal S, 22.1 (Resistor) terminal t1, 22.1 (Resistor) terminal t2, 26.2 (Terminal) terminal t1.
- N7: Net N7 connects 16.3 (Mosfet) terminal S, 16.5 (Mosfet) terminal S.
- N8: Net N8 connects 16.4 (Mosfet) terminal S, 9.2 (GND) terminal t1.
- N9: Net N9 connects 16.5 (Mosfet) terminal D, 16.6 (Mosfet) terminal D, 26.3 (Terminal) terminal t1.
- N10: Net N10 currently touches only 2.1 (Battery) terminal t2.
- N11: Net N11 currently touches only 9.3 (GND) terminal t1.

## Reasoning Hints
- Check whether supply nets, especially implicit ones, are plausible for the connected components.
- Look for components whose terminals connect to unexpected peers or to only one modeled net when that seems electrically unusual.
- Use the component-centric section to follow signal flow and the net-centric section to verify shared connectivity.

## Companion Files
- `*_simplified.json`: same information in structured JSON form.
- `*_graph.json`: full graph export with nodes and edges.
