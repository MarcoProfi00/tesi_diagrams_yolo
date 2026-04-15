# =========================================================
# graph preparation
# =========================================================
from typing import Any
import networkx as nx
from .config import LAYER_X
from .labels import sort_components_spatial, sort_nets, sort_terminals


def build_nx_graph(graph_data: dict[str, Any]) -> nx.DiGraph:
    """Costruisce nx graph a partire dagli input correnti della pipeline."""
    G = nx.DiGraph()
    for node in graph_data["nodes"]:
        G.add_node(node["node_id"], **node)
    for edge in graph_data["edges"]:
        G.add_edge(edge["source"], edge["target"], **edge)
    return G

def compute_layered_positions(graph_data: dict[str, Any]) -> dict[str, tuple[float, float]]:
    """Calcola layered positions a partire dagli input forniti."""
    by_type: dict[str, list[dict[str, Any]]] = {
        "Diagram": [],
        "Component": [],
        "Terminal": [],
        "Net": [],
    }
    for node in graph_data["nodes"]:
        by_type.setdefault(node.get("node_type", "Other"), []).append(node)

    component_nodes = sort_components_spatial(by_type.get("Component", []))
    component_order = {str(n.get("instance_id", "")): i for i, n in enumerate(component_nodes)}
    terminal_nodes = sort_terminals(by_type.get("Terminal", []), component_order)
    net_nodes = sort_nets(by_type.get("Net", []))
    diagram_nodes = by_type.get("Diagram", [])

    ordered = {
        "Diagram": diagram_nodes,
        "Component": component_nodes,
        "Terminal": terminal_nodes,
        "Net": net_nodes,
    }

    positions: dict[str, tuple[float, float]] = {}
    for node_type, nodes in ordered.items():
        if not nodes:
            continue
        x = LAYER_X.get(node_type, 8.0)
        n = len(nodes)
        if n == 1:
            ys = [0.0]
        else:
            spacing = 1.18 if node_type == "Terminal" else 1.35
            start = (n - 1) * spacing / 2.0
            ys = [start - i * spacing for i in range(n)]
        for node, y in zip(nodes, ys):
            positions[node["node_id"]] = (x, y)
    return positions

def compute_component_net_positions(graph_data: dict[str, Any]) -> dict[str, tuple[float, float]]:
    """Calcola component net positions a partire dagli input forniti."""
    components = sort_components_spatial([n for n in graph_data["nodes"] if n.get("viz_node_type") == "Component"])
    nets = sort_nets([n for n in graph_data["nodes"] if n.get("viz_node_type") == "Net"])

    positions: dict[str, tuple[float, float]] = {}
    for x, nodes in [(0.0, components), (3.2, nets)]:
        if not nodes:
            continue
        n = len(nodes)
        if n == 1:
            ys = [0.0]
        else:
            spacing = 1.45
            start = (n - 1) * spacing / 2.0
            ys = [start - i * spacing for i in range(n)]
        for node, y in zip(nodes, ys):
            positions[node["node_id"]] = (x, y)
    return positions
