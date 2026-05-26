"""Orchestrazione del passo 05: match, correzioni euristiche ed export finale."""

from pathlib import Path

import cv2

from .canonical_export import build_canonical_components, build_terminal_metadata
from .crossings import is_blue_wire_style, split_bridge_labels
from .graph_utils import build_terminal_graph
from .grouping import (
    build_label_to_terminal_ids,
    remove_non_shorting_component_self_matches,
    split_polarized_capacitor_self_short_groups,
)
from .heuristics_connector import build_connector_aligned_gnd_edges, fix_stacked_connector_gnd_crossing_edges
from .heuristics_bjt import merge_bjt_base_aligned_labels
from .heuristics_inductor import merge_near_horizontal_stub_labels
from .heuristics_mosfet import merge_mosfet_gate_aligned_labels, merge_mosfet_gate_rail_groups
from .heuristics_oblique import merge_short_oblique_branch_labels
from .heuristics_opamp import merge_opamp_aux_external_terminal_labels
from .heuristics_seven_segment import (
    build_seven_segment_shared_segment_edges,
    split_seven_segment_segment_label_groups,
)
from .heuristics_supply import build_supply_graph_links, merge_battery_gate_rail_groups
from .ids import build_simple_id_map, build_simple_list, build_simple_terminal_graph
from .io_utils import load_binary_image
from .matching import (
    attach_unmatched_analog_meter_terminals,
    attach_unmatched_opamp_aux_to_external_terminals,
    match_terminal_to_skeleton_label,
    remap_monoterminal_outward_stub_matches,
)
from .skeleton_ops import erase_component_bodies_from_skeleton, load_junction_support_binary


# =========================================================
# MAIN LOGIC PER UNA SINGOLA IMMAGINE
# =========================================================
# prende terminali, componenti e wire extraction dal JSON;
# carica lo skeleton;
# cancella i corpi dei componenti a due terminali;
# calcola le connected components;
# fa il match di tutti i terminali;
# applica fallback analog meter;
# applica fallback opamp aux;
# costruisce label_to_terminal_ids;
# applica tutte le fusioni euristiche;
# applica gli split per ponti/crossing;
# fonde rail MOSFET/battery dove serve;
# rimuove self-short non validi;
# costruisce il grafo finale;
# aggiunge VDD / VSS;
# costruisce warning;
# costruisce componenti canonici;
# restituisce tutto il necessario per export e debug.
def build_terminal_graph_for_image(data: dict):
    terminals = data.get("terminals", [])
    components = data.get("components", [])
    wire_extraction = dict(data.get("wire_extraction", {}))
    wire_extraction["image_path"] = data.get("image_path")
    skeleton_path = wire_extraction.get("skeleton_path")

    if not skeleton_path:
        raise ValueError("skeleton_path mancante nel JSON del passo 04.")

    skeleton = load_binary_image(Path(skeleton_path))
    filtered_binary = None
    filtered_path = wire_extraction.get("filtered_path")
    if filtered_path:
        filtered_binary = load_binary_image(Path(filtered_path))
    skeleton_for_graph = erase_component_bodies_from_skeleton(skeleton, components)

    # Connected components dello skeleton.
    # Ogni label > 0 rappresenta un tratto di filo connesso.
    _, labels, _, _ = cv2.connectedComponentsWithStats(skeleton_for_graph, connectivity=8)

    # Match semplice: ogni terminale viene agganciato alla label dello skeleton
    # trovata nella sua zona locale.
    terminal_match_debug = {}
    for term in terminals:
        terminal_match_debug[term["terminal_id"]] = match_terminal_to_skeleton_label(labels, term)

    attach_unmatched_analog_meter_terminals(components, terminal_match_debug, labels)
    attach_unmatched_opamp_aux_to_external_terminals(terminals, terminal_match_debug)
    remap_monoterminal_outward_stub_matches(terminals, terminal_match_debug, labels)

    original_to_simple = build_simple_id_map(terminals)

    # Gruppi di terminali che insistono sullo stesso tratto di filo.
    label_to_terminal_ids = build_label_to_terminal_ids(terminal_match_debug)
    label_to_terminal_ids = merge_mosfet_gate_aligned_labels(
        label_to_terminal_ids,
        terminals,
        components,
        terminal_match_debug,
        labels,
    )
    label_to_terminal_ids = merge_opamp_aux_external_terminal_labels(
        label_to_terminal_ids,
        terminals,
        terminal_match_debug,
    )
    label_to_terminal_ids = merge_bjt_base_aligned_labels(
        label_to_terminal_ids,
        terminals,
        components,
        terminal_match_debug,
        labels,
    )
    label_to_terminal_ids = merge_near_horizontal_stub_labels(
        label_to_terminal_ids,
        terminals,
        terminal_match_debug,
        labels,
    )
    if is_blue_wire_style(wire_extraction, load_junction_support_binary(wire_extraction)):
        label_to_terminal_ids = merge_short_oblique_branch_labels(
            label_to_terminal_ids,
            terminals,
            terminal_match_debug,
            labels,
            filtered_binary,
        )
    label_to_terminal_ids = split_bridge_labels(
        label_to_terminal_ids,
        terminals,
        terminal_match_debug,
        skeleton_for_graph,
        labels,
        wire_extraction,
    )
    label_to_terminal_ids = split_polarized_capacitor_self_short_groups(
        label_to_terminal_ids,
        terminals,
    )
    label_to_terminal_ids = merge_mosfet_gate_rail_groups(
        label_to_terminal_ids,
        terminals,
        components,
    )
    label_to_terminal_ids = merge_battery_gate_rail_groups(
        label_to_terminal_ids,
        terminals,
    )
    label_to_terminal_ids = remove_non_shorting_component_self_matches(
        label_to_terminal_ids,
        terminals,
        terminal_match_debug,
    )
    label_to_terminal_ids = split_seven_segment_segment_label_groups(
        label_to_terminal_ids,
        terminals,
        components,
    )

    # Grafo finale interno e sua vista canonica leggibile.
    terminal_graph = build_terminal_graph(terminals, label_to_terminal_ids)
    for source_id, target_id in build_connector_aligned_gnd_edges(terminals, terminal_graph):
        terminal_graph.setdefault(source_id, [])
        terminal_graph.setdefault(target_id, [])
        terminal_graph[source_id].append(target_id)
        terminal_graph[target_id].append(source_id)
    fix_stacked_connector_gnd_crossing_edges(terminals, terminal_graph)
    for source_id, target_id in build_seven_segment_shared_segment_edges(components):
        terminal_graph.setdefault(source_id, [])
        terminal_graph.setdefault(target_id, [])
        terminal_graph[source_id].append(target_id)
        terminal_graph[target_id].append(source_id)
    for terminal_id in terminal_graph:
        terminal_graph[terminal_id] = sorted(set(terminal_graph[terminal_id]))
    simple_terminal_graph = build_simple_terminal_graph(terminal_graph, original_to_simple)
    supply_graph_links = build_supply_graph_links(
        terminals,
        label_to_terminal_ids,
        terminal_match_debug,
        labels,
        data.get("image_height"),
        original_to_simple,
    )
    for terminal_id, supply_labels in supply_graph_links.items():
        simple_terminal_graph.setdefault(terminal_id, [])
        simple_terminal_graph[terminal_id] = sorted(set(simple_terminal_graph[terminal_id]) | set(supply_labels))
        for supply_label in supply_labels:
            simple_terminal_graph.setdefault(supply_label, [])
            simple_terminal_graph[supply_label] = sorted(set(simple_terminal_graph[supply_label]) | {terminal_id})
    simple_terminal_graph = {key: simple_terminal_graph[key] for key in sorted(simple_terminal_graph.keys())}

    # Terminali isolati nel grafo finale.
    unconnected_terminals = sorted([
        terminal_id
        for terminal_id, neighbors in simple_terminal_graph.items()
        if len(neighbors) == 0
    ])
    unmatched_terminals = sorted([
        terminal_id
        for terminal_id, info in terminal_match_debug.items()
        if info.get("matched_label") is None
    ])
    suspicious_matches = sorted([
        terminal_id
        for terminal_id, info in terminal_match_debug.items()
        if info.get("is_suspicious", False) and info.get("matched_label") is not None
    ])

    canonical_components = build_canonical_components(components)
    terminal_metadata = build_terminal_metadata(canonical_components)

    warnings = {
        "unconnected_terminals": unconnected_terminals,
        "unmatched_terminals": build_simple_list(unmatched_terminals, original_to_simple),
        "suspicious_matches": build_simple_list(suspicious_matches, original_to_simple),
    }

    return {
        "components": canonical_components,
        "terminal_metadata": terminal_metadata,
        "graph": simple_terminal_graph,
        "warnings": warnings,
        "skeleton_binary": skeleton_for_graph,
        "terminal_match_debug": terminal_match_debug,
        "simple_id_map": original_to_simple,
    }
