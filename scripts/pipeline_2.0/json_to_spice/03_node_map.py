"""
Costruzione della mappa dei nodi elettrici.

Cuore iniziale della pipeline 2.0. A partire dal campo
graph del JSON, calcola le componenti connesse dei terminali e assegna a
ogni gruppo un nodo elettrico.

Responsabilita previste:

- raggruppare terminali connessi nello stesso nodo;
- mappare i terminali collegati a GND sul nodo SPICE 0;
- applicare eventuali nodi manuali dichiarati nel values.yaml;
- preservare warning e informazioni di provenienza;
- produrre node_map.json.

La node map deve diventare il contratto elettrico principale da cui derivare
netlist, report e diagnosi.
"""

from __future__ import annotations

from typing import Any


GROUND_CLASS_NAMES = {"GND", "Ground"}


def find_connected_components(graph: dict[str, list[str]]) -> list[list[str]]:
    """
    Trova le componenti connesse del grafo terminale-terminale.

    Ogni componente connessa corrisponde a un nodo elettrico candidato.
    """
    visited: set[str] = set()
    components: list[list[str]] = []

    for start in sorted(graph.keys()):
        if start in visited:
            continue

        stack = [start]
        group: list[str] = []
        visited.add(start)

        while stack:
            current = stack.pop()
            group.append(current)

            for neighbor in graph.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append(neighbor)

        components.append(sorted(group))

    return components


def is_ground_terminal(
    terminal_id: str,
    terminal_to_component: dict[str, str],
    component_by_id: dict[str, dict[str, Any]],
) -> bool:
    """Restituisce True se il terminale appartiene a un componente GND."""
    component_id = terminal_to_component.get(terminal_id)
    if component_id is None:
        return False

    component = component_by_id.get(component_id, {})
    return component.get("class_name") in GROUND_CLASS_NAMES


def build_component_terminal_nodes(
    components: list[dict[str, Any]],
    terminal_to_node: dict[str, str],
) -> dict[str, dict[str, str]]:
    """
    Costruisce una vista comoda: component_id -> nome terminale -> node_id.

    Esempio:
    resistor22.1 -> {"t1": "N001", "t2": "N002"}
    """
    result: dict[str, dict[str, str]] = {}

    for component in components:
        component_id = str(component.get("component_id", ""))
        if not component_id:
            continue

        terminal_nodes: dict[str, str] = {}
        for terminal in component.get("terminals", []) or []:
            terminal_id = terminal.get("terminal_id")
            terminal_name = terminal.get("name") or terminal_id
            if terminal_id in terminal_to_node:
                terminal_nodes[str(terminal_name)] = terminal_to_node[str(terminal_id)]

        result[component_id] = terminal_nodes

    return dict(sorted(result.items()))


def build_node_map(normalized_circuit: dict[str, Any]) -> dict[str, Any]:
    """
    Costruisce node_map.json a partire dal circuito normalizzato.

    Regola principale:
    - se un gruppo contiene un terminale GND, il node_id e "0";
    - altrimenti i nodi sono N001, N002, ...
    """
    graph = normalized_circuit.get("graph") or {}
    terminal_to_component = normalized_circuit.get("terminal_to_component") or {}
    component_by_id = normalized_circuit.get("component_by_id") or {}
    components = normalized_circuit.get("components") or []

    connected_components = find_connected_components(graph)

    nodes: list[dict[str, Any]] = []
    ground_terminals: list[str] = []
    ground_groups: list[list[str]] = []
    terminal_to_node: dict[str, str] = {}
    normal_node_index = 1
    ground_groups_count = 0

    for group in connected_components:
        has_ground = any(
            is_ground_terminal(terminal_id, terminal_to_component, component_by_id)
            for terminal_id in group
        )

        if has_ground:
            node_id = "0"
            node_kind = "ground"
            ground_groups_count += 1
            ground_groups.append(group)
            ground_terminals.extend(group)
        else:
            node_id = f"N{normal_node_index:03d}"
            node_kind = "normal"
            normal_node_index += 1

        for terminal_id in group:
            terminal_to_node[terminal_id] = node_id

        if node_kind == "normal":
            nodes.append({
                "node_id": node_id,
                "kind": node_kind,
                "terminals": group,
                "terminal_count": len(group),
            })

    if ground_terminals:
        nodes.append({
            "node_id": "0",
            "kind": "ground",
            "terminals": sorted(set(ground_terminals)),
            "terminal_count": len(set(ground_terminals)),
            "source_groups": ground_groups,
        })

    nodes.sort(key=lambda node: (node["node_id"] != "0", node["node_id"], node["terminals"]))
    terminal_to_node = dict(sorted(terminal_to_node.items()))

    singleton_nodes = [
        node["node_id"]
        for node in nodes
        if node["terminal_count"] == 1
    ]

    component_terminal_nodes = build_component_terminal_nodes(components, terminal_to_node)

    return {
        "circuit_id": normalized_circuit.get("circuit_id"),
        "source_format": "pipeline2.0_node_map",
        "nodes": nodes,
        "terminal_to_node": terminal_to_node,
        "component_terminal_nodes": component_terminal_nodes,
        "warnings": {
            "ground_groups_count": ground_groups_count,
            "multiple_ground_groups_merged_as_node_0": ground_groups_count > 1,
            "singleton_nodes": singleton_nodes,
            "original_warnings": normalized_circuit.get("warnings") or {},
            "normalization_warnings": normalized_circuit.get("normalization_warnings") or [],
        },
        "stats": {
            "nodes_count": len(nodes),
            "normal_nodes_count": len([node for node in nodes if node["kind"] == "normal"]),
            "ground_nodes_count": len([node for node in nodes if node["kind"] == "ground"]),
            "ground_groups_count": ground_groups_count,
            "terminal_to_node_count": len(terminal_to_node),
            "singleton_nodes_count": len(singleton_nodes),
        },
    }
