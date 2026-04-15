"""
07_export_graph.py

Scopo:
    Esportare il risultato topologico del passo 06 come grafo strutturato.

Output:
    - graph_json per diagramma
    - semantic_explanation.json per diagramma
    - llm_context.md per diagramma
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
import os
import json
import csv
import shutil
from collections import defaultdict, deque
from itertools import combinations
from typing import Any

from semantic_export.export_semantic_explanation import (
    build_semantic_explanation,
    build_semantic_llm_context,
)

# =========================================================
# PATHS / INPUT-OUTPUT
# =========================================================
PROJECT_ROOT = Path(__file__).resolve().parents[2]

PIPELINE_DATASET = os.environ.get("PIPELINE_DATASET", "topology_v6_opamp")

INPUT_DIR = PROJECT_ROOT / "outputs" / PIPELINE_DATASET / "06_match_terminals_to_nets"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / PIPELINE_DATASET / "07_export_graph"

# =========================================================
# OUTPUT SUBDIRECTORIES
# =========================================================
GRAPH_JSON_DIR = OUTPUT_DIR / "graph_json"
SEMANTIC_JSON_DIR = OUTPUT_DIR / "semantic_explanation"
LLM_CONTEXT_DIR = OUTPUT_DIR / "llm_context"
NODES_CSV_DIR = OUTPUT_DIR / "nodes_csv"
EDGES_CSV_DIR = OUTPUT_DIR / "edges_csv"
COMBINED_DIR = OUTPUT_DIR / "combined_csv"
LEGACY_SIMPLIFIED_JSON_DIR = OUTPUT_DIR / "simplified_json"

# =========================================================
# FLAGS
# =========================================================
SAVE_COMBINED_CSV = True

GROUND_COMPONENT_CLASSES = {"gnd"}
SUPPLY_COMPONENT_CLASSES = {"battery", "voltage_source", "current_source"}
EXTERNAL_INTERFACE_CLASSES = {"terminal"}
PASSIVE_COMPONENT_CLASSES = {"resistor", "capacitor", "inductor"}
CONTROL_TERMINAL_NAMES = {
    "g",
    "gate",
    "b",
    "base",
    "ctrl",
    "control",
    "in",
    "in+",
    "in-",
    "input",
    "non_inverting_input",
    "inverting_input",
}
OUTPUT_TERMINAL_NAMES = {
    "d",
    "drain",
    "c",
    "collector",
    "out",
    "output",
    "s",
    "source",
    "e",
    "emitter",
}
TERMINAL_NAME_EXPANSIONS = {
    "g": "gate",
    "d": "drain",
    "s": "source",
    "b": "base",
    "c": "collector",
    "e": "emitter",
}
MAX_FUNCTIONAL_PATHS = 8


# =========================================================
# UTILITY
# =========================================================
def infer_source_stage(data: dict) -> str:
    """Inferisce source stage dalle evidenze disponibili."""
    if "terminal_net_matching" in data:
        matching = data.get("terminal_net_matching", {})
        if "n_ok_matches" in matching or "n_unmatched_matches" in matching:
            return "06_match_terminals_to_nets"
        return "06_match_terminals_to_nets"
    return "unknown"

def jsonable(value: Any):
    """Converte liste e dizionari in stringhe JSON per poterli scrivere comodamente nei CSV."""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return value

def save_csv(rows: list[dict], out_path: Path):
    """Salva una tabella CSV costruendo automaticamente l'unione di tutte le colonne presenti nelle righe."""
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
    """Genera l'identificatore univoco del nodo Diagram nel grafo esportato."""
    return f"diagram:{diagram_id}"

def component_node_id(diagram_id: str, instance_id: str) -> str:
    """Genera l'identificatore univoco di un nodo Component nel grafo esportato."""
    return f"component:{diagram_id}:{instance_id}"

def terminal_node_id(diagram_id: str, terminal_id: str) -> str:
    """Genera l'identificatore univoco di un nodo Terminal nel grafo esportato."""
    return f"terminal:{diagram_id}:{terminal_id}"

def net_node_id(diagram_id: str, net_id: str) -> str:
    """Genera l'identificatore univoco di un nodo Net nel grafo esportato."""
    return f"net:{diagram_id}:{net_id}"


def component_ref(instance_id: str | None, class_name: str | None) -> str:
    """Costruisce una stringa leggibile per riferirsi a un componente nei testi descrittivi."""
    if instance_id and class_name:
        return f"{instance_id} ({class_name})"
    return instance_id or class_name or "unknown_component"


def terminal_ref(terminal_id: str | None, terminal_name: str | None) -> str:
    """Costruisce una stringa leggibile per riferirsi a un terminale nei testi descrittivi."""
    if terminal_name:
        return f"{terminal_id} [{terminal_name}]"
    return terminal_id or "unknown_terminal"


def terminal_display_id(term: dict) -> str | None:
    """Restituisce l'identificatore piu leggibile da mostrare per un terminale."""
    return term.get("display_terminal_id") or term.get("terminal_id")


def terminal_human_name(term: dict) -> str | None:
    """Restituisce il nome piu parlante disponibile per un terminale."""
    return (
        term.get("display_name")
        or term.get("semantic_terminal_name")
        or term.get("name")
        or term.get("display_terminal_id")
        or term.get("terminal_id")
    )


def build_match_status_counts(terminals: list[dict]) -> dict[str, int]:
    """Conta quanti terminali ricadono in ciascuno stato di matching."""
    counts: dict[str, int] = {}
    for terminal in terminals:
        status = str(terminal.get("match_status") or "unknown")
        counts[status] = counts.get(status, 0) + 1
    return counts


def build_terminal_and_net_indexes(data: dict):
    """Prepara indici rapidi di componenti, terminali e net insieme alla mappa net -> terminali."""
    components = data.get("components", [])
    terminals = data.get("terminals", [])
    nets = data.get("nets", [])

    component_index = {
        comp["instance_id"]: comp
        for comp in components
        if comp.get("instance_id") is not None
    }
    terminal_index = {
        term["terminal_id"]: term
        for term in terminals
        if term.get("terminal_id") is not None
    }
    net_index = {
        net["net_id"]: net
        for net in nets
        if net.get("net_id") is not None
    }

    net_to_terminal_ids: dict[str, list[str]] = {}
    for term in terminals:
        terminal_id = term.get("terminal_id")
        matched_net_id = term.get("matched_net_id")
        if terminal_id is None or matched_net_id is None:
            continue
        net_to_terminal_ids.setdefault(str(matched_net_id), []).append(str(terminal_id))

    for net_id in list(net_to_terminal_ids.keys()):
        net_to_terminal_ids[net_id] = sorted(set(net_to_terminal_ids[net_id]))

    return component_index, terminal_index, net_index, net_to_terminal_ids


def build_terminal_statement(term: dict, peer_terminals: list[dict]) -> str:
    """Genera una frase breve che descrive come un terminale e collegato nel diagramma."""
    comp_text = component_ref(term.get("instance_id"), term.get("component_class_name"))
    terminal_name = terminal_human_name(term)
    net_id = term.get("matched_net_id")
    is_implicit_supply = bool(term.get("matched_net_is_implicit_supply", False))
    implicit_reason = term.get("matched_net_implicit_reason")

    if net_id is None:
        return f"{comp_text} terminal {terminal_name} is currently unmatched to any net."

    if not peer_terminals:
        if is_implicit_supply:
            reason_text = f" ({implicit_reason})" if implicit_reason else ""
            return (
                f"{comp_text} terminal {terminal_name} is connected to implicit supply net "
                f"{net_id}{reason_text}; no explicit peer terminal is modeled."
            )
        return f"{comp_text} terminal {terminal_name} is the only modeled terminal on net {net_id}."

    if len(peer_terminals) == 1:
        peer = peer_terminals[0]
        peer_text = component_ref(peer.get("instance_id"), peer.get("component_class_name"))
        peer_terminal_name = peer.get("terminal_name") or peer.get("display_terminal_id") or peer.get("terminal_id")
        return (
            f"{comp_text} terminal {terminal_name} is connected on net {net_id} to "
            f"{peer_text} terminal {peer_terminal_name}."
        )

    peers_text = ", ".join(
        f"{component_ref(peer.get('instance_id'), peer.get('component_class_name'))} terminal "
        f"{peer.get('terminal_name') or peer.get('display_terminal_id') or peer.get('terminal_id')}"
        for peer in peer_terminals
    )
    return (
        f"{comp_text} terminal {terminal_name} is connected on net {net_id} together with "
        f"{peers_text}."
    )


def build_net_statement(net: dict, connected_terminals: list[dict]) -> str:
    """Genera una frase breve che descrive quali terminali risultano collegati alla net."""
    net_id = net.get("net_id")
    if not connected_terminals:
        return f"Net {net_id} has no modeled connected terminals."

    is_implicit_supply = bool(net.get("is_implicit_supply", False))
    implicit_reason = net.get("implicit_reason")

    if len(connected_terminals) == 1:
        term = connected_terminals[0]
        comp_text = component_ref(term.get("instance_id"), term.get("component_class_name"))
        terminal_name = terminal_human_name(term)
        if is_implicit_supply:
            reason_text = f" ({implicit_reason})" if implicit_reason else ""
            return (
                f"Net {net_id} is an implicit supply connection{reason_text} attached to "
                f"{comp_text} terminal {terminal_name}."
            )
        return f"Net {net_id} currently touches only {comp_text} terminal {terminal_name}."

    endpoints_text = ", ".join(
        f"{component_ref(term.get('instance_id'), term.get('component_class_name'))} terminal "
        f"{terminal_human_name(term)}"
        for term in connected_terminals
    )
    return f"Net {net_id} connects {endpoints_text}."


def build_diagnostic_context(terminals: list[dict], nets: list[dict]) -> dict:
    """Raccoglie il contesto diagnostico utile per terminali sospetti, unmatched e net implicite."""
    suspicious_terminals = [
        {
            "terminal_id": term.get("terminal_id"),
            "display_terminal_id": terminal_display_id(term),
            "instance_id": term.get("instance_id"),
            "component_class_name": term.get("component_class_name"),
            "match_status": term.get("match_status"),
            "match_confidence": term.get("match_confidence"),
            "match_warnings": term.get("match_warnings", []),
        }
        for term in terminals
        if term.get("is_suspicious_match", False)
    ]

    unmatched_terminals = [
        {
            "terminal_id": term.get("terminal_id"),
            "display_terminal_id": terminal_display_id(term),
            "instance_id": term.get("instance_id"),
            "component_class_name": term.get("component_class_name"),
        }
        for term in terminals
        if term.get("matched_net_id") is None
    ]

    implicit_supply_nets = [
        {
            "net_id": net.get("net_id"),
            "implicit_reason": net.get("implicit_reason"),
            "connected_terminal_ids": net.get("connected_terminal_ids", []),
        }
        for net in nets
        if net.get("is_implicit_supply", False)
    ]

    implicit_supply_terminal_matches = [
        {
            "terminal_id": term.get("terminal_id"),
            "display_terminal_id": terminal_display_id(term),
            "instance_id": term.get("instance_id"),
            "component_class_name": term.get("component_class_name"),
            "matched_net_id": term.get("matched_net_id"),
            "match_status": term.get("match_status"),
            "implicit_reason": term.get("matched_net_implicit_reason"),
        }
        for term in terminals
        if term.get("matched_net_is_implicit_supply", False)
    ]

    # Questo blocco produce un riassunto umano molto compatto che poi viene
    # riutilizzato sia nell'export semantico sia nelle viste di debug.
    notes = []
    if implicit_supply_nets:
        notes.append(
            f"{len(implicit_supply_nets)} implicit supply net(s) detected."
        )
    if suspicious_terminals:
        notes.append(
            f"{len(suspicious_terminals)} suspicious terminal match(es) detected."
        )
    if unmatched_terminals:
        notes.append(
            f"{len(unmatched_terminals)} terminal(s) are unmatched."
        )
    if not notes:
        notes.append("No implicit supply nets, suspicious terminal matches, or unmatched terminals were detected.")

    return {
        "suspicious_terminals": suspicious_terminals,
        "unmatched_terminals": unmatched_terminals,
        "implicit_supply_nets": implicit_supply_nets,
        "implicit_supply_terminal_matches": implicit_supply_terminal_matches,
        "notes": notes,
    }


# =========================================================
# NODE BUILDER
# =========================================================
def make_diagram_node(data: dict) -> dict:
    """Crea diagram node per la struttura del grafo esportato."""
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
    """Crea component node per la struttura del grafo esportato."""
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
    """Crea terminal node per la struttura del grafo esportato."""
    snap_point = terminal.get("snap_point") or [None, None]
    display_terminal_id = terminal_display_id(terminal)
    display_name = terminal_human_name(terminal)
    return {
        "node_id": terminal_node_id(diagram_id, terminal["terminal_id"]),
        "node_type": "Terminal",
        "label": display_terminal_id,
        "diagram_id": diagram_id,
        "terminal_id": terminal["terminal_id"],
        "display_terminal_id": display_terminal_id,
        "instance_id": terminal.get("instance_id"),
        "component_node_id": component_node_id(diagram_id, terminal.get("instance_id")),
        "component_class_id": terminal.get("component_class_id"),
        "component_class_name": terminal.get("component_class_name"),
        "terminal_name": terminal.get("name"),
        "display_name": display_name,
        "semantic_terminal_name": terminal.get("semantic_terminal_name"),
        "semantic_terminal_id": terminal.get("semantic_terminal_id"),
        "semantic_slot": terminal.get("semantic_slot"),
        "semantic_confidence": terminal.get("semantic_confidence"),
        "semantic_evidence_type": terminal.get("semantic_evidence_type"),
        "semantic_resolution_mode": terminal.get("semantic_resolution_mode"),
        "semantic_role_family": terminal.get("semantic_role_family"),
        "semantic_polarity": terminal.get("semantic_polarity"),
        "semantic_direction": terminal.get("semantic_direction"),
        "relative_position": terminal.get("relative_position"),
        "estimated_orientation": terminal.get("estimated_orientation"),
        "estimated_connection_side": terminal.get("estimated_connection_side"),
        "x": terminal.get("x"),
        "y": terminal.get("y"),
        "terminal_point_mode": terminal.get("terminal_point_mode"),
        "terminal_point_debug": terminal.get("terminal_point_debug"),
        "matched_net_id": terminal.get("matched_net_id"),
        "matched_net_index": terminal.get("matched_net_index"),
        "matched_net_is_implicit_supply": terminal.get("matched_net_is_implicit_supply", False),
        "matched_net_implicit_reason": terminal.get("matched_net_implicit_reason"),
        "preferred_net_id_from_05": terminal.get("preferred_net_id_from_05"),
        "preferred_net_index_from_05": terminal.get("preferred_net_index_from_05"),
        "preferred_from_05_is_implicit_supply": terminal.get("preferred_from_05_is_implicit_supply", False),
        "preferred_from_05_implicit_reason": terminal.get("preferred_from_05_implicit_reason"),
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
    """Crea net node per la struttura del grafo esportato."""
    bbox = net.get("bbox", [None, None, None, None])
    return {
        "node_id": net_node_id(diagram_id, net["net_id"]),
        "node_type": "Net",
        "label": net["net_id"],
        "diagram_id": diagram_id,
        "net_id": net["net_id"],
        "net_index": net.get("net_index"),
        "source_label": net.get("source_label"),
        "merged_source_labels": net.get("merged_source_labels", [net.get("source_label")]),
        "pixel_count": net.get("pixel_count"),
        "n_connected_terminals": net.get("n_connected_terminals"),
        "is_implicit_supply": net.get("is_implicit_supply", False),
        "implicit_reason": net.get("implicit_reason"),
        "implicit_anchor_terminal_id": net.get("implicit_anchor_terminal_id"),
        "bbox_x1": bbox[0],
        "bbox_y1": bbox[1],
        "bbox_x2": bbox[2],
        "bbox_y2": bbox[3],
        "connected_terminal_ids": net.get("connected_terminal_ids", []),
        "connected_terminal_display_ids": net.get("connected_terminal_display_ids", []),
        "connected_semantic_terminal_names": net.get("connected_semantic_terminal_names", []),
    }


# =========================================================
# EDGE BUILDERS
# =========================================================
def make_edge(edge_id: str, source: str, target: str, relation_type: str, diagram_id: str, **attrs) -> dict:
    """Crea edge per la struttura del grafo esportato."""
    edge = {
        "edge_id": edge_id,
        "source": source,
        "target": target,
        "relation_type": relation_type,
        "diagram_id": diagram_id,
    }
    edge.update(attrs)
    return edge


def build_simplified_diagram_json(data: dict) -> dict:
    # Legacy compatibility wrapper: the active export now writes semantic_explanation.json.
    """Mantiene la compatibilita legacy costruendo il JSON semantico semplificato."""
    return build_semantic_explanation(
        data,
        pipeline_variant=PIPELINE_DATASET,
        source_stage=infer_source_stage(data),
    )


def join_or_none(values: list[str]) -> str:
    """Unisce or none in una rappresentazione testuale compatta."""
    cleaned = [str(value) for value in values if value]
    if not cleaned:
        return "none"
    return ", ".join(cleaned)


def build_llm_context_markdown(simplified_data: dict) -> str:
    # Legacy compatibility wrapper: the active markdown now derives from semantic_explanation.json.
    """Genera il contesto testuale in Markdown da allegare all'export semantico."""
    return build_semantic_llm_context(simplified_data)

# =========================================================
# BUILD GRAPH
# =========================================================
def build_graph(data: dict):
    """Costruisce nodi, archi e statistiche del grafo finale a partire dai risultati topologici."""
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
                is_implicit_supply=net.get("is_implicit_supply", False),
                implicit_reason=net.get("implicit_reason"),
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
                display_terminal_id=term.get("display_terminal_id"),
                terminal_name=term.get("name"),
                display_name=term.get("display_name"),
                semantic_terminal_name=term.get("semantic_terminal_name"),
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
                display_terminal_id=conn.get("display_terminal_id"),
                semantic_terminal_name=conn.get("semantic_terminal_name"),
                net_id=net_id,
                net_index=conn.get("net_index"),
                component_class_name=conn.get("component_class_name"),
                match_status=conn.get("match_status"),
                net_is_implicit_supply=conn.get("net_is_implicit_supply", False),
                net_implicit_reason=conn.get("net_implicit_reason"),
                match_distance_px=conn.get("match_distance_px"),
                match_confidence=conn.get("match_confidence"),
                match_warnings=conn.get("match_warnings", []),
                is_suspicious_match=conn.get("is_suspicious_match", False),
                snap_point=conn.get("snap_point"),
            )
        )

    # Le statistiche finali non servono solo per reportistica: vengono lette anche
    # dalla dashboard HTML per mostrare rapidamente problemi e copertura del matching.
    confidence_counts = {
        "ok": sum(1 for t in terminals if t.get("match_confidence") == "ok"),
        "unmatched": sum(1 for t in terminals if t.get("match_confidence") == "unmatched"),
        "none": sum(1 for t in terminals if t.get("match_confidence") == "none"),
    }
    match_status_counts = build_match_status_counts(terminals)

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
        "terminal_match_status_counts": match_status_counts,
        "terminal_connection_status_counts": match_status_counts,
        "n_terminals_matched": sum(1 for t in terminals if t.get("matched_net_id") is not None),
        "n_terminals_unmatched": sum(1 for t in terminals if t.get("matched_net_id") is None),
        "n_implicit_supply_nets": sum(1 for net in nets if net.get("is_implicit_supply", False)),
        "n_implicit_supply_terminal_matches": sum(
            1 for t in terminals if t.get("matched_net_is_implicit_supply", False)
        ),
    }

    graph_data = {
        "graph_metadata": {
            "diagram_id": diagram_id,
            "image_name": data.get("image_name"),
            "image_path": data.get("image_path"),
            "source_json_stage": infer_source_stage(data),
            "topology_stage_input": "06_match_terminals_to_nets",
            "pipeline_variant": PIPELINE_DATASET,
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
    """Esegue il punto di ingresso dello step corrente della pipeline."""
    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"Cartella input non trovata: {INPUT_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    GRAPH_JSON_DIR.mkdir(parents=True, exist_ok=True)
    if LEGACY_SIMPLIFIED_JSON_DIR.exists():
        shutil.rmtree(LEGACY_SIMPLIFIED_JSON_DIR)
    SEMANTIC_JSON_DIR.mkdir(parents=True, exist_ok=True)
    LLM_CONTEXT_DIR.mkdir(parents=True, exist_ok=True)
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
        semantic_data = build_semantic_explanation(
            data,
            pipeline_variant=PIPELINE_DATASET,
            source_stage=infer_source_stage(data),
        )
        llm_context_md = build_semantic_llm_context(semantic_data)
        stem = json_path.stem

        graph_json_path = GRAPH_JSON_DIR / f"{stem}_graph.json"
        semantic_json_path = SEMANTIC_JSON_DIR / f"{stem}_semantic_explanation.json"
        llm_context_path = LLM_CONTEXT_DIR / f"{stem}_llm_context.md"
        nodes_csv_path = NODES_CSV_DIR / f"{stem}_nodes.csv"
        edges_csv_path = EDGES_CSV_DIR / f"{stem}_edges.csv"

        with open(graph_json_path, "w", encoding="utf-8") as f:
            json.dump(graph_data, f, indent=2, ensure_ascii=False)
        with open(semantic_json_path, "w", encoding="utf-8") as f:
            json.dump(semantic_data, f, indent=2, ensure_ascii=False)
        with open(llm_context_path, "w", encoding="utf-8") as f:
            f.write(llm_context_md)

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
    print(f"Semantic explanation JSON salvati in: {SEMANTIC_JSON_DIR}")
    print(f"LLM context salvati in: {LLM_CONTEXT_DIR}")
    print(f"Nodes CSV salvati in : {NODES_CSV_DIR}")
    print(f"Edges CSV salvati in : {EDGES_CSV_DIR}")
    if SAVE_COMBINED_CSV:
        print(f"CSV batch salvati in : {COMBINED_DIR}")


if __name__ == "__main__":
    main()
