# Legge il json di 06 e costruisce un graph formato da:
#   nodi
#       Diagram
#       Component
#       Terminal
#       Net
#   archi
#       Diagram -> HAS_COMPONENT -> Component
#       Diagram -> HAS_NET -> Net
#       Component -> HAS_TERMINAL -> Terminal
#       Terminal -> CONNECTED_TO -> Net

from pathlib import Path
import json
import csv

# =========================================================
# CONFIGURAZIONE
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_DIR = PROJECT_ROOT / "outputs" / "topology" / "06_match_terminals_to_nets"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "topology" / "07_export_graph"

GRAPH_JSON_DIR = OUTPUT_DIR / "graph_json"
NODES_CSV_DIR = OUTPUT_DIR / "nodes_csv"
EDGES_CSV_DIR = OUTPUT_DIR / "edges_csv"


def make_diagram_node(data: dict) -> dict:
    diagram_id = data["image_id"]

    return {
        "node_id": f"diagram:{diagram_id}",
        "node_type": "Diagram",
        "label": diagram_id,
        "diagram_id": diagram_id,
        "image_name": data.get("image_name"),
        "image_path": data.get("image_path"),
        "image_width": data.get("image_width"),
        "image_height": data.get("image_height"),
    }


def make_component_node(component: dict, diagram_id: str) -> dict:
    return {
        "node_id": f"component:{component['instance_id']}",
        "node_type": "Component",
        "label": component["instance_id"],
        "diagram_id": diagram_id,
        "instance_id": component["instance_id"],
        "class_id": component.get("class_id"),
        "class_name": component.get("class_name"),
        "symbol_type": component.get("symbol_type"),
        "confidence": component.get("conf"),
        "bbox_x1": component["bbox"][0],
        "bbox_y1": component["bbox"][1],
        "bbox_x2": component["bbox"][2],
        "bbox_y2": component["bbox"][3],
        "estimated_orientation": component.get("estimated_orientation"),
        "use_for_terminals": component.get("use_for_terminals"),
        "use_for_masking": component.get("use_for_masking"),
    }


def make_terminal_node(terminal: dict, diagram_id: str) -> dict:
    return {
        "node_id": f"terminal:{terminal['terminal_id']}",
        "node_type": "Terminal",
        "label": terminal["terminal_id"],
        "diagram_id": diagram_id,
        "terminal_id": terminal["terminal_id"],
        "instance_id": terminal.get("instance_id"),
        "component_class_id": terminal.get("component_class_id"),
        "component_class_name": terminal.get("component_class_name"),
        "terminal_name": terminal.get("name"),
        "relative_position": terminal.get("relative_position"),
        "estimated_orientation": terminal.get("estimated_orientation"),
        "x": terminal.get("x"),
        "y": terminal.get("y"),
        "matched_net_id": terminal.get("matched_net_id"),
        "matched_net_index": terminal.get("matched_net_index"),
        "match_status": terminal.get("match_status"),
        "match_distance_px": terminal.get("match_distance_px"),
    }


def make_net_node(net: dict, diagram_id: str) -> dict:
    return {
        "node_id": f"net:{net['net_id']}",
        "node_type": "Net",
        "label": net["net_id"],
        "diagram_id": diagram_id,
        "net_id": net["net_id"],
        "net_index": net.get("net_index"),
        "pixel_count": net.get("pixel_count"),
        "n_connected_terminals": net.get("n_connected_terminals"),
        "bbox_x1": net["bbox"][0],
        "bbox_y1": net["bbox"][1],
        "bbox_x2": net["bbox"][2],
        "bbox_y2": net["bbox"][3],
    }


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


def build_graph(data: dict):
    diagram_id = data["image_id"]

    nodes = []
    edges = []

    # =========================================================
    # NODO DIAGRAM
    # =========================================================
    diagram_node = make_diagram_node(data)
    nodes.append(diagram_node)

    # =========================================================
    # NODI COMPONENT
    # =========================================================
    components = data.get("components", [])
    for comp in components:
        nodes.append(make_component_node(comp, diagram_id))

    # =========================================================
    # NODI TERMINAL
    # =========================================================
    terminals = data.get("terminals", [])
    for term in terminals:
        nodes.append(make_terminal_node(term, diagram_id))

    # =========================================================
    # NODI NET
    # =========================================================
    nets = data.get("nets", [])
    for net in nets:
        nodes.append(make_net_node(net, diagram_id))

    # =========================================================
    # ARCHI Diagram -> Component
    # =========================================================
    for comp in components:
        edges.append(
            make_edge(
                edge_id=f"edge:diagram:{diagram_id}:component:{comp['instance_id']}",
                source=f"diagram:{diagram_id}",
                target=f"component:{comp['instance_id']}",
                relation_type="HAS_COMPONENT",
                diagram_id=diagram_id,
                instance_id=comp["instance_id"],
            )
        )

    # =========================================================
    # ARCHI Diagram -> Net
    # =========================================================
    for net in nets:
        edges.append(
            make_edge(
                edge_id=f"edge:diagram:{diagram_id}:net:{net['net_id']}",
                source=f"diagram:{diagram_id}",
                target=f"net:{net['net_id']}",
                relation_type="HAS_NET",
                diagram_id=diagram_id,
                net_id=net["net_id"],
            )
        )

    # =========================================================
    # ARCHI Component -> Terminal
    # =========================================================
    for comp in components:
        for term in comp.get("terminals", []):
            edges.append(
                make_edge(
                    edge_id=f"edge:component:{comp['instance_id']}:terminal:{term['terminal_id']}",
                    source=f"component:{comp['instance_id']}",
                    target=f"terminal:{term['terminal_id']}",
                    relation_type="HAS_TERMINAL",
                    diagram_id=diagram_id,
                    instance_id=comp["instance_id"],
                    terminal_id=term["terminal_id"],
                )
            )

    # =========================================================
    # ARCHI Terminal -> Net
    # =========================================================
    connections = data.get("connections", [])
    for conn in connections:
        terminal_id = conn["terminal_id"]
        net_id = conn["net_id"]

        edges.append(
            make_edge(
                edge_id=f"edge:terminal:{terminal_id}:net:{net_id}",
                source=f"terminal:{terminal_id}",
                target=f"net:{net_id}",
                relation_type="CONNECTED_TO",
                diagram_id=diagram_id,
                terminal_id=terminal_id,
                net_id=net_id,
                match_status=conn.get("match_status"),
                match_distance_px=conn.get("match_distance_px"),
            )
        )

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
    }

    graph_data = {
        "graph_metadata": {
            "diagram_id": diagram_id,
            "image_name": data.get("image_name"),
            "image_path": data.get("image_path"),
            "source_json_stage": "06_match_terminals_to_nets",
        },
        "graph_summary": graph_summary,
        "nodes": nodes,
        "edges": edges,
    }

    return graph_data


def save_csv(rows: list[dict], out_path: Path):
    if not rows:
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            pass
        return

    fieldnames = sorted({key for row in rows for key in row.keys()})

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"Cartella input non trovata: {INPUT_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    GRAPH_JSON_DIR.mkdir(parents=True, exist_ok=True)
    NODES_CSV_DIR.mkdir(parents=True, exist_ok=True)
    EDGES_CSV_DIR.mkdir(parents=True, exist_ok=True)

    json_files = sorted(INPUT_DIR.glob("*.json"))

    if not json_files:
        raise FileNotFoundError(f"Nessun file JSON trovato in: {INPUT_DIR}")

    print(f"Input directory : {INPUT_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"File trovati    : {len(json_files)}\n")

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

        summary = graph_data["graph_summary"]
        print(
            f"[{i}/{len(json_files)}] {json_path.name} -> "
            f"nodes={summary['n_nodes_total']}, edges={summary['n_edges_total']}"
        )
        print(
            f"    diagram={summary['n_diagram_nodes']}, "
            f"components={summary['n_component_nodes']}, "
            f"terminals={summary['n_terminal_nodes']}, "
            f"nets={summary['n_net_nodes']}"
        )

    print("\nCompletato.")
    print(f"Graph JSON salvati in: {GRAPH_JSON_DIR}")
    print(f"Nodes CSV salvati in : {NODES_CSV_DIR}")
    print(f"Edges CSV salvati in : {EDGES_CSV_DIR}")


if __name__ == "__main__":
    main()