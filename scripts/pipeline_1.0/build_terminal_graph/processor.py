"""
Orchestrazione del passo 05: match, correzioni euristiche ed export finale.

Questo modulo e' il punto centrale della costruzione del grafo:
  - legge terminali/componenti e i path prodotti dallo step 04;
  - aggancia ogni terminale a una connected component dello skeleton;
  - applica euristiche per correggere casi noti di skeleton spezzato o falso
    corto;
  - converte i gruppi di label in archi terminale-terminale;
  - prepara il JSON canonico e i dati di debug per l'entrypoint.
"""

from pathlib import Path

import cv2

from .canonical_export import build_canonical_components, build_terminal_metadata
from .crossings import (
    is_blue_wire_style,
    split_bridge_labels,
    split_looped_orthogonal_crossing_groups,
)
from .graph_utils import build_terminal_graph
from .grouping import (
    build_label_to_terminal_ids,
    merge_split_grounded_ic_side_branches,
    remove_non_shorting_component_self_matches,
    split_same_side_ic_fanout_groups,
    split_polarized_capacitor_self_short_groups,
)
from .heuristics_connector import build_connector_aligned_gnd_edges, fix_stacked_connector_gnd_crossing_edges
from .heuristics_bjt import merge_bjt_base_aligned_labels
from .heuristics_inductor import merge_near_horizontal_stub_labels, merge_near_vertical_stub_labels
from .heuristics_mosfet import merge_mosfet_gate_aligned_labels, merge_mosfet_gate_rail_groups
from .heuristics_oblique import merge_short_oblique_branch_labels
from .heuristics_opamp import merge_opamp_aux_external_terminal_labels
from .heuristics_seven_segment import (
    build_seven_segment_shared_segment_edges,
    split_seven_segment_segment_label_groups,
)
from .heuristics_supply import merge_battery_gate_rail_groups
from .ids import build_simple_id_map, build_simple_list, build_simple_terminal_graph
from .io_utils import load_binary_image
from .matching import (
    attach_unmatched_analog_meter_terminals,
    attach_unmatched_lateral_terminal_labels,
    attach_unmatched_opamp_aux_to_external_terminals,
    match_terminal_to_skeleton_label,
    remap_opamp_aux_to_aligned_label,
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
# costruisce warning;
# costruisce componenti canonici;
# restituisce tutto il necessario per export e debug.
def build_terminal_graph_for_image(data: dict):
    """Costruisce grafo, componenti canonici, warning e debug per una immagine."""
    terminals = data.get("terminals", [])
    components = data.get("components", [])

    # wire_extraction contiene i path dello step 04. Aggiungiamo image_path
    # per permettere ad alcune euristiche di riconoscere lo stile grafico.
    wire_extraction = dict(data.get("wire_extraction", {}))
    wire_extraction["image_path"] = data.get("image_path")
    skeleton_path = wire_extraction.get("skeleton_path")

    if not skeleton_path:
        raise ValueError("skeleton_path mancante nel JSON del passo 04.")

    # Lo skeleton e' la rappresentazione monolinea dei fili. filtered_binary
    # resta piu' spesso e viene usato solo da alcune euristiche geometriche.
    skeleton = load_binary_image(Path(skeleton_path))
    filtered_binary = None
    filtered_path = wire_extraction.get("filtered_path")
    if filtered_path:
        filtered_binary = load_binary_image(Path(filtered_path))
    # Lo step 04 puo' lasciare tratti di corpo componente nello skeleton; prima
    # di creare le label cancelliamo i corpi che non sono veri fili elettrici.
    skeleton_for_graph = erase_component_bodies_from_skeleton(skeleton, components)

    # Connected components dello skeleton.
    # Ogni label > 0 rappresenta un tratto di filo connesso.
    _, labels, _, _ = cv2.connectedComponentsWithStats(skeleton_for_graph, connectivity=8)

    # Abbinamento semplice: ogni terminale viene agganciato alla label dello skeleton
    # trovata nella sua zona locale.
    terminal_match_debug = {}
    for term in terminals:
        terminal_match_debug[term["terminal_id"]] = match_terminal_to_skeleton_label(labels, term)

    # Fallback/remap locali sui singoli terminali. Queste funzioni non creano
    # ancora il grafo: migliorano solo matched_label quando il match base fallisce.
    attach_unmatched_analog_meter_terminals(components, terminal_match_debug, labels)
    attach_unmatched_opamp_aux_to_external_terminals(terminals, terminal_match_debug)
    attach_unmatched_lateral_terminal_labels(terminals, terminal_match_debug, labels)
    remap_opamp_aux_to_aligned_label(terminals, terminal_match_debug, labels)
    remap_monoterminal_outward_stub_matches(terminals, terminal_match_debug, labels)

    # Mappa terminal_id interno -> id leggibile/esportabile.
    original_to_simple = build_simple_id_map(terminals)

    # Gruppi di terminali che insistono sullo stesso tratto di filo.
    label_to_terminal_ids = build_label_to_terminal_ids(terminal_match_debug)
    # Fusioni euristiche: uniscono label separate quando lo skeleton e' spezzato
    # ma la geometria del componente suggerisce che il collegamento e' unico.
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
        labels,
    )
    label_to_terminal_ids = merge_near_vertical_stub_labels(
        label_to_terminal_ids,
        terminals,
        labels,
        filtered_binary,
    )
    # Alcune immagini hanno fili blu/spessi: in quel caso la maschera piena e'
    # piu' informativa dello skeleton per recuperare ramificazioni oblique.
    if is_blue_wire_style(wire_extraction, load_junction_support_binary(wire_extraction)):
        label_to_terminal_ids = merge_short_oblique_branch_labels(
            label_to_terminal_ids,
            terminals,
            terminal_match_debug,
            labels,
            filtered_binary,
        )
    # Divisioni euristiche: separano label che lo skeleton ha unito ma che
    # elettricamente non devono essere cortocircuitate.
    label_to_terminal_ids = split_bridge_labels(
        label_to_terminal_ids,
        terminals,
        terminal_match_debug,
        skeleton_for_graph,
        labels,
        wire_extraction,
    )
    label_to_terminal_ids = split_looped_orthogonal_crossing_groups(
        label_to_terminal_ids,
        terminals,
        skeleton_for_graph,
    )
    label_to_terminal_ids = merge_split_grounded_ic_side_branches(
        label_to_terminal_ids,
        terminals,
        terminal_match_debug,
    )
    label_to_terminal_ids = split_same_side_ic_fanout_groups(
        label_to_terminal_ids,
        terminals,
    )
    label_to_terminal_ids = split_polarized_capacitor_self_short_groups(
        label_to_terminal_ids,
        terminals,
        components,
        skeleton_for_graph,
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
    # Trasformiamo ogni gruppo di terminali sulla stessa label in archi espliciti
    # del grafo interno, ancora basato sui terminal_id originali.
    terminal_graph = build_terminal_graph(terminals, label_to_terminal_ids)

    # Archi aggiunti a valle dei gruppi skeleton: sono connessioni di dominio
    # che possono mancare nel matching pixel-based ma sono molto plausibili.
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
    # Deduplica finale degli archi interni prima della conversione a id semplici.
    for terminal_id in terminal_graph:
        terminal_graph[terminal_id] = sorted(set(terminal_graph[terminal_id]))
    simple_terminal_graph = build_simple_terminal_graph(terminal_graph, original_to_simple)

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

    # L'export canonico rimuove dettagli geometrici/debug e conserva solo cio'
    # che serve a lettura AI, report e passi successivi.
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
