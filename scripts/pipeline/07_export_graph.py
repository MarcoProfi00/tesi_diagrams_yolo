"""
07_export_graph.py

Scopo:
    Esportare il risultato topologico del passo 06 come grafo strutturato.

Output:
    - graph_json per diagramma
    - nodes.csv per diagramma
    - edges.csv per diagramma
    - CSV batch combinati

Modello del grafo:
    Diagram -> HAS_COMPONENT -> Component
    Diagram -> HAS_NET -> Net
    Component -> HAS_TERMINAL -> Terminal
    Terminal -> CONNECTED_TO -> Net
"""
from pathlib import Path
import json
import csv
from typing import Any

# =========================================================
# PATHS / INPUT-OUTPUT
# =========================================================
PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_DIR = PROJECT_ROOT / "outputs" / "topology_v4_source_mosfet_transistor" / "06_match_terminals_to_nets"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "topology_v4_source_mosfet_transistor" / "07_export_graph"

# =========================================================
# OUTPUT SUBDIRECTORIES
# =========================================================
GRAPH_JSON_DIR = OUTPUT_DIR / "graph_json"
NODES_CSV_DIR = OUTPUT_DIR / "nodes_csv"
EDGES_CSV_DIR = OUTPUT_DIR / "edges_csv"
COMBINED_DIR = OUTPUT_DIR / "combined_csv"

# =========================================================
# FLAGS
# =========================================================
SAVE_COMBINED_CSV = True


# =========================================================
# UTILITY
# =========================================================
def infer_source_stage(data: dict) -> str:
    if "terminal_net_matching" in data:
        matching = data.get("terminal_net_matching", {})
        if "confidence_counts" in matching:
            return "06_match_terminals_to_nets_v3_confidence"
        return "06_match_terminals_to_nets_v3"
    return "unknown"

def jsonable(value: Any):
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return value

def save_csv(rows: list[dict], out_path: Path):
    if not rows:
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            pass
        return

    fieldnames = sorted({key for row in rows for key in row.keys()})

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: jsonable(v) for k, v in row.items()})


# =========================================================
# COSTRUZIONE ID UNIVOCI NEL BATCH
# =========================================================
def diagram_node_id(diagram_id: str) -> str:
    return f"diagram:{diagram_id}"

def component_node_id(diagram_id: str, instance_id: str) -> str:
    return f"component:{diagram_id}:{instance_id}"

def terminal_node_id(diagram_id: str, terminal_id: str) -> str:
    return f"terminal:{diagram_id}:{terminal_id}"

def net_node_id(diagram_id: str, net_id: str) -> str:
    return f"net:{diagram_id}:{net_id}"


# =========================================================
# NODE BUILDER
# =========================================================
def make_diagram_node(data: dict) -> dict:
    diagram_id = data["image_id"]
    return {
        "node_id": diagram_node_id(diagram_id),
        "node_type": "Diagram",
        "label": diagram_id,
        "diagram_id": diagram_id,
        "image_name": data.get("image_name"),
        "image_path": data.get("image_path"),
        "image_width": data.get("image_width"),
        "image_height": data.get("image_height"),
        "n_components": data.get("n_components"),
        "n_terminals_estimated": data.get("n_terminals_estimated"),
        "n_nets": data.get("n_nets"),
        "n_connections": data.get("n_connections"),
        "source_json_stage": infer_source_stage(data),
    }


def make_component_node(component: dict, diagram_id: str) -> dict:
    bbox = component.get("bbox", [None, None, None, None])
    return {
        "node_id": component_node_id(diagram_id, component["instance_id"]),
        "node_type": "Component",
        "label": component["instance_id"],
        "diagram_id": diagram_id,
        "instance_id": component["instance_id"],
        "class_id": component.get("class_id"),
        "class_name": component.get("class_name"),
        "symbol_type": component.get("symbol_type"),
        "confidence": component.get("conf"),
        "bbox_x1": bbox[0],
        "bbox_y1": bbox[1],
        "bbox_x2": bbox[2],
        "bbox_y2": bbox[3],
        "estimated_orientation": component.get("estimated_orientation"),
        "estimated_connection_side": component.get("estimated_connection_side"),
        "use_for_terminals": component.get("use_for_terminals"),
        "use_for_masking": component.get("use_for_masking"),
        "n_terminals": len(component.get("terminals", [])),
    }

def make_terminal_node(terminal: dict, diagram_id: str) -> dict:
    snap_point = terminal.get("snap_point") or [None, None]
    return {
        "node_id": terminal_node_id(diagram_id, terminal["terminal_id"]),
        "node_type": "Terminal",
        "label": terminal["terminal_id"],
        "diagram_id": diagram_id,
        "terminal_id": terminal["terminal_id"],
        "instance_id": terminal.get("instance_id"),
        "component_node_id": component_node_id(diagram_id, terminal.get("instance_id")),
        "component_class_id": terminal.get("component_class_id"),
        "component_class_name": terminal.get("component_class_name"),
        "terminal_name": terminal.get("name"),
        "relative_position": terminal.get("relative_position"),
        "estimated_orientation": terminal.get("estimated_orientation"),
        "estimated_connection_side": terminal.get("estimated_connection_side"),
        "x": terminal.get("x"),
        "y": terminal.get("y"),
        "terminal_point_mode": terminal.get("terminal_point_mode"),
        "terminal_point_debug": terminal.get("terminal_point_debug"),
        "matched_net_id": terminal.get("matched_net_id"),
        "matched_net_index": terminal.get("matched_net_index"),
        "preferred_net_id_from_05": terminal.get("preferred_net_id_from_05"),
        "preferred_net_index_from_05": terminal.get("preferred_net_index_from_05"),
        "match_status": terminal.get("match_status"),
        "match_distance_px": terminal.get("match_distance_px"),
        "match_confidence": terminal.get("match_confidence"),
        "match_warnings": terminal.get("match_warnings", []),
        "is_suspicious_match": terminal.get("is_suspicious_match", False),
        "search_stage": terminal.get("search_stage"),
        "search_kind": terminal.get("search_kind"),
        "search_window": terminal.get("search_window"),
        "snap_x": snap_point[0],
        "snap_y": snap_point[1],
    }

def make_net_node(net: dict, diagram_id: str) -> dict:
    bbox = net.get("bbox", [None, None, None, None])
    return {
        "node_id": net_node_id(diagram_id, net["net_id"]),
        "node_type": "Net",
        "label": net["net_id"],
        "diagram_id": diagram_id,
        "net_id": net["net_id"],
        "net_index": net.get("net_index"),
        "source_label": net.get("source_label"),
        "pixel_count": net.get("pixel_count"),
        "n_connected_terminals": net.get("n_connected_terminals"),
        "bbox_x1": bbox[0],
        "bbox_y1": bbox[1],
        "bbox_x2": bbox[2],
        "bbox_y2": bbox[3],
        "connected_terminal_ids": net.get("connected_terminal_ids", []),
    }


# =========================================================
# EDGE BUILDERS
# =========================================================
def make_edge(edge_id: str, source: str, target: str, relation_type: str, diagram_id: str, **attrs) -> dict:
    edge = {
        "edge_id": edge_id,
        "source": source,
        "target": target,
        "relation_type": relation_type,
        "diagram_id": diagram_id,
    }
    edge.update(attrs)
    return edge

# =========================================================
# BUILD GRAPH
# =========================================================
def build_graph(data: dict):
    diagram_id = data["image_id"]

    nodes: list[dict] = []
    edges: list[dict] = []

    components = data.get("components", [])
    terminals = data.get("terminals", [])
    nets = data.get("nets", [])
    connections = data.get("connections", [])

    # Nodo diagram
    nodes.append(make_diagram_node(data))

    # Nodi componenti / terminali / net
    for comp in components:
        nodes.append(make_component_node(comp, diagram_id))
    for term in terminals:
        nodes.append(make_terminal_node(term, diagram_id))
    for net in nets:
        nodes.append(make_net_node(net, diagram_id))

    # Archi diagram -> component
    for comp in components:
        comp_node = component_node_id(diagram_id, comp["instance_id"])
        edges.append(
            make_edge(
                edge_id=f"edge:{diagram_id}:diagram_to_component:{comp['instance_id']}",
                source=diagram_node_id(diagram_id),
                target=comp_node,
                relation_type="HAS_COMPONENT",
                diagram_id=diagram_id,
                instance_id=comp["instance_id"],
                class_name=comp.get("class_name"),
            )
        )

    # Archi diagram -> net
    for net in nets:
        edges.append(
            make_edge(
                edge_id=f"edge:{diagram_id}:diagram_to_net:{net['net_id']}",
                source=diagram_node_id(diagram_id),
                target=net_node_id(diagram_id, net["net_id"]),
                relation_type="HAS_NET",
                diagram_id=diagram_id,
                net_id=net["net_id"],
                net_index=net.get("net_index"),
            )
        )

    # Archi component -> terminal
    for comp in components:
        comp_node = component_node_id(diagram_id, comp["instance_id"])
        for term in comp.get("terminals", []):
            edges.append(
                make_edge(
                    edge_id=f"edge:{diagram_id}:component:{comp['instance_id']}:terminal:{term['terminal_id']}",
                    source=comp_node,
                    target=terminal_node_id(diagram_id, term["terminal_id"]),
                    relation_type="HAS_TERMINAL",
                    diagram_id=diagram_id,
                    instance_id=comp["instance_id"],
                    terminal_id=term["terminal_id"],
                    terminal_name=term.get("name"),
                    relative_position=term.get("relative_position"),
                )
            )

    # Archi terminal -> net
    for conn in connections:
        terminal_id = conn["terminal_id"]
        net_id = conn["net_id"]
        edges.append(
            make_edge(
                edge_id=f"edge:{diagram_id}:terminal:{terminal_id}:net:{net_id}",
                source=terminal_node_id(diagram_id, terminal_id),
                target=net_node_id(diagram_id, net_id),
                relation_type="CONNECTED_TO",
                diagram_id=diagram_id,
                terminal_id=terminal_id,
                net_id=net_id,
                net_index=conn.get("net_index"),
                component_class_name=conn.get("component_class_name"),
                match_status=conn.get("match_status"),
                match_distance_px=conn.get("match_distance_px"),
                match_confidence=conn.get("match_confidence"),
                match_warnings=conn.get("match_warnings", []),
                is_suspicious_match=conn.get("is_suspicious_match", False),
                snap_point=conn.get("snap_point"),
            )
        )

    confidence_counts = {
        "high": sum(1 for t in terminals if t.get("match_confidence") == "high"),
        "medium": sum(1 for t in terminals if t.get("match_confidence") == "medium"),
        "low": sum(1 for t in terminals if t.get("match_confidence") == "low"),
        "none": sum(1 for t in terminals if t.get("match_confidence") == "none"),
    }

    graph_summary = {
        "diagram_id": diagram_id,
        "n_nodes_total": len(nodes),
        "n_edges_total": len(edges),
        "n_diagram_nodes": 1,
        "n_component_nodes": len(components),
        "n_terminal_nodes": len(terminals),
        "n_net_nodes": len(nets),
        "n_has_component_edges": len(components),
        "n_has_net_edges": len(nets),
        "n_has_terminal_edges": sum(len(comp.get("terminals", [])) for comp in components),
        "n_connected_to_edges": len(connections),
        "n_suspicious_terminal_matches": sum(1 for t in terminals if t.get("is_suspicious_match", False)),
        "terminal_match_confidence_counts": confidence_counts,
        "n_terminals_matched": sum(1 for t in terminals if t.get("matched_net_id") is not None),
        "n_terminals_unmatched": sum(1 for t in terminals if t.get("matched_net_id") is None),
    }

    graph_data = {
        "graph_metadata": {
            "diagram_id": diagram_id,
            "image_name": data.get("image_name"),
            "image_path": data.get("image_path"),
            "source_json_stage": infer_source_stage(data),
            "topology_stage_input": "06_match_terminals_to_nets_v3",
            "pipeline_variant": "topology_v3_three_terminals",
        },
        "graph_summary": graph_summary,
        "nodes": nodes,
        "edges": edges,
    }

    return graph_data


# =========================================================
# MAIN
# =========================================================
def main() -> None:
    # 1. load input json
    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"Cartella input non trovata: {INPUT_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    GRAPH_JSON_DIR.mkdir(parents=True, exist_ok=True)
    NODES_CSV_DIR.mkdir(parents=True, exist_ok=True)
    EDGES_CSV_DIR.mkdir(parents=True, exist_ok=True)
    if SAVE_COMBINED_CSV:
        COMBINED_DIR.mkdir(parents=True, exist_ok=True)

    json_files = sorted(INPUT_DIR.glob("*.json"))
    if not json_files:
        raise FileNotFoundError(f"Nessun file JSON trovato in: {INPUT_DIR}")

    print(f"Input directory : {INPUT_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"File trovati    : {len(json_files)}\\n")

    # 2. build graph
    all_nodes: list[dict] = []
    all_edges: list[dict] = []
    graph_summaries: list[dict] = []

    # 3. save per-diagram outputs
    for i, json_path in enumerate(json_files, start=1):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        graph_data = build_graph(data)
        stem = json_path.stem

        graph_json_path = GRAPH_JSON_DIR / f"{stem}_graph.json"
        nodes_csv_path = NODES_CSV_DIR / f"{stem}_nodes.csv"
        edges_csv_path = EDGES_CSV_DIR / f"{stem}_edges.csv"

        with open(graph_json_path, "w", encoding="utf-8") as f:
            json.dump(graph_data, f, indent=2, ensure_ascii=False)

        save_csv(graph_data["nodes"], nodes_csv_path)
        save_csv(graph_data["edges"], edges_csv_path)

        all_nodes.extend(graph_data["nodes"])
        all_edges.extend(graph_data["edges"])
        graph_summaries.append(graph_data["graph_summary"])

        summary = graph_data["graph_summary"]
        print(
            f"[{i}/{len(json_files)}] {json_path.name} -> "
            f"nodes={summary['n_nodes_total']}, edges={summary['n_edges_total']}, "
            f"suspicious={summary['n_suspicious_terminal_matches']}"
        )
        print(
            f"    diagram={summary['n_diagram_nodes']}, "
            f"components={summary['n_component_nodes']}, "
            f"terminals={summary['n_terminal_nodes']}, "
            f"nets={summary['n_net_nodes']}"
        )

    if SAVE_COMBINED_CSV:
        save_csv(all_nodes, COMBINED_DIR / "all_nodes.csv")
        save_csv(all_edges, COMBINED_DIR / "all_edges.csv")
        save_csv(graph_summaries, COMBINED_DIR / "graph_summaries.csv")

    print("\nCompletato.")
    print(f"Graph JSON salvati in: {GRAPH_JSON_DIR}")
    print(f"Nodes CSV salvati in : {NODES_CSV_DIR}")
    print(f"Edges CSV salvati in : {EDGES_CSV_DIR}")
    if SAVE_COMBINED_CSV:
        print(f"CSV batch salvati in : {COMBINED_DIR}")


if __name__ == "__main__":
    main()
