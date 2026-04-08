from typing import Any


def derive_component_net_graph(graph_data: dict[str, Any]) -> dict[str, Any]:
    component_nodes = [n for n in graph_data["nodes"] if n.get("node_type") == "Component"]
    net_nodes = [n for n in graph_data["nodes"] if n.get("node_type") == "Net"]
    component_lookup = {str(n.get("instance_id")): n for n in component_nodes}
    net_lookup = {str(n.get("net_id")): n for n in net_nodes}

    edge_groups: dict[tuple[str, str], dict[str, Any]] = {}
    for edge in graph_data["edges"]:
        if edge.get("relation_type") != "CONNECTED_TO":
            continue
        source = str(edge.get("source", ""))
        if ":" not in source:
            continue
        # source is terminal:<diagram_id>:<instance_id>:tX
        parts = source.split(":")
        if len(parts) < 4:
            continue
        instance_id = parts[-2]
        net_id = str(edge.get("net_id", ""))
        key = (instance_id, net_id)
        payload = edge_groups.setdefault(
            key,
            {
                "instance_id": instance_id,
                "net_id": net_id,
                "terminal_ids": [],
                "has_suspicious": False,
                "confidences": [],
            },
        )
        term_id = edge.get("terminal_id")
        if term_id:
            payload["terminal_ids"].append(term_id)
        if edge.get("is_suspicious_match", False):
            payload["has_suspicious"] = True
        conf = edge.get("match_confidence")
        if conf:
            payload["confidences"].append(conf)

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    for comp in component_nodes:
        comp_copy = dict(comp)
        comp_copy["viz_node_type"] = "Component"
        nodes.append(comp_copy)
    for net in net_nodes:
        net_copy = dict(net)
        net_copy["viz_node_type"] = "Net"
        nodes.append(net_copy)

    for i, ((instance_id, net_id), payload) in enumerate(sorted(edge_groups.items()), start=1):
        comp = component_lookup.get(instance_id)
        net = net_lookup.get(net_id)
        if comp is None or net is None:
            continue
        edges.append(
            {
                "edge_id": f"component_net:{i}",
                "source": comp["node_id"],
                "target": net["node_id"],
                "relation_type": "COMPONENT_TO_NET",
                "instance_id": instance_id,
                "net_id": net_id,
                "n_terminals": len(payload["terminal_ids"]),
                "terminal_ids": sorted(payload["terminal_ids"]),
                "is_suspicious_match": payload["has_suspicious"],
                "match_confidences": sorted(set(payload["confidences"])),
            }
        )

    return {
        "graph_metadata": graph_data.get("graph_metadata", {}),
        "graph_summary": graph_data.get("graph_summary", {}),
        "nodes": nodes,
        "edges": edges,
    }
