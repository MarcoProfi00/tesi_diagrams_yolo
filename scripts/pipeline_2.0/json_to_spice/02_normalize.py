"""
Normalizzazione del Graph JSON.

Questo modulo trasforma il JSON canonico prodotto dalla pipeline_1.0 (script 05) in una
struttura interna piu comoda per i passaggi successivi.

Il JSON di partenza contiene principalmente:

- components;
- terminal_metadata;
- graph;
- warnings.

La normalizzazione dovra costruire una vista coerente del circuito, con lookup
rapidi per componenti, terminali, classi, appartenenza terminale-componente e
adiacenze del grafo. Non deve ancora generare nodi SPICE ne netlist.
"""

from __future__ import annotations

from collections import Counter
from typing import Any


def _as_list(value: Any) -> list[Any]:
    """Converte None in lista vuota e preserva le liste."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _sorted_unique(values: list[str]) -> list[str]:
    """Restituisce valori stringa unici in ordine alfabetico."""
    return sorted({str(value) for value in values if value not in (None, "")})


def build_terminal_rows(components: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, str]]:
    """
      Restituisce:
    - lista terminali normalizzati;
    - mappa terminal_id -> component_id.
    """
    terminals: list[dict[str, Any]] = []
    terminal_to_component: dict[str, str] = {}

    for component in components:
        component_id = str(component.get("component_id", ""))
        class_name = str(component.get("class_name", ""))
        instance_id = component.get("instance_id")

        if not component_id:
            continue

        for terminal in _as_list(component.get("terminals")):
            if not isinstance(terminal, dict):
                continue

            terminal_id = str(terminal.get("terminal_id", ""))
            if not terminal_id:
                continue

            row = {
                "terminal_id": terminal_id,
                "component_id": component_id,
                "instance_id": instance_id,
                "class_name": class_name,
                "name": terminal.get("name"),
                "relative_position": terminal.get("relative_position"),
            }

            for optional_key in ("display_name", "pin_number", "pin_label"):
                if optional_key in terminal:
                    row[optional_key] = terminal.get(optional_key)

            terminals.append(row)
            terminal_to_component[terminal_id] = component_id

    terminals.sort(key=lambda item: item["terminal_id"])
    return terminals, terminal_to_component


def normalize_graph(
    graph: dict[str, Any],
    terminal_ids: set[str],
) -> tuple[dict[str, list[str]], list[dict[str, Any]]]:
    """
    Normalizza il grafo terminale-terminale.

    La pipeline 1.0 esporta gia un grafo simmetrico, ma qui lo rendiamo
    esplicitamente tale per proteggere i passaggi successivi da edge mancanti
    in una sola direzione.
    """
    normalized: dict[str, set[str]] = {terminal_id: set() for terminal_id in terminal_ids}
    graph_issues: list[dict[str, Any]] = []

    for raw_source, raw_neighbors in (graph or {}).items():
        source = str(raw_source)
        if source not in normalized:
            normalized[source] = set()
            graph_issues.append({
                "type": "graph_source_not_declared_as_terminal",
                "terminal_id": source,
            })

        for raw_target in _as_list(raw_neighbors):
            target = str(raw_target)
            if target == "":
                continue
            if target not in normalized:
                normalized[target] = set()
                graph_issues.append({
                    "type": "graph_target_not_declared_as_terminal",
                    "terminal_id": target,
                    "source_terminal_id": source,
                })
            if target == source:
                graph_issues.append({
                    "type": "self_edge",
                    "terminal_id": source,
                })
                continue
            normalized[source].add(target)
            normalized[target].add(source)

    return (
        {terminal_id: sorted(neighbors) for terminal_id, neighbors in sorted(normalized.items())},
        graph_issues,
    )


def build_component_lookup(components: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Costruisce component_id -> componente."""
    lookup: dict[str, dict[str, Any]] = {}
    for component in components:
        component_id = str(component.get("component_id", ""))
        if component_id:
            lookup[component_id] = component
    return dict(sorted(lookup.items()))


def build_stats(
    components: list[dict[str, Any]],
    terminals: list[dict[str, Any]],
    graph: dict[str, list[str]],
    graph_issues: list[dict[str, Any]],
) -> dict[str, Any]:
    """Calcola statistiche sintetiche utili per report e debug."""
    class_counts = Counter(str(component.get("class_name", "")) for component in components)
    edge_refs = sum(len(neighbors) for neighbors in graph.values())
    isolated_terminals = [
        terminal_id
        for terminal_id, neighbors in graph.items()
        if len(neighbors) == 0
    ]

    return {
        "components_count": len(components),
        "terminals_count": len(terminals),
        "graph_terminals_count": len(graph),
        "edge_references_count": edge_refs,
        "undirected_edges_count": edge_refs // 2,
        "isolated_terminals_count": len(isolated_terminals),
        "isolated_terminals": isolated_terminals,
        "class_counts": dict(sorted(class_counts.items())),
        "graph_issues_count": len(graph_issues),
    }


def normalize_circuit_graph(raw_graph_json: dict[str, Any]) -> dict[str, Any]:
    """
    Normalizza un Graph JSON della pipeline 1.0.

    Questa funzione non interpreta ancora elettricamente il circuito: prepara
    solo una rappresentazione coerente per node map, YAML e SPICE emitter.
    """
    components = _as_list(raw_graph_json.get("components"))
    components = [component for component in components if isinstance(component, dict)]
    components.sort(key=lambda item: str(item.get("component_id", "")))

    terminals, terminal_to_component = build_terminal_rows(components)
    terminal_ids = {terminal["terminal_id"] for terminal in terminals}
    normalized_graph, graph_issues = normalize_graph(
        raw_graph_json.get("graph") or {},
        terminal_ids,
    )

    component_by_id = build_component_lookup(components)
    terminal_metadata = raw_graph_json.get("terminal_metadata") or {}
    warnings = raw_graph_json.get("warnings") or {}

    normalized = {
        "circuit_id": raw_graph_json.get("image_id"),
        "image_name": raw_graph_json.get("image_name"),
        "source_format": "pipeline1.0_graph_json",
        "components": components,
        "component_by_id": component_by_id,
        "terminals": terminals,
        "terminal_to_component": dict(sorted(terminal_to_component.items())),
        "terminal_metadata": terminal_metadata,
        "graph": normalized_graph,
        "warnings": warnings,
        "normalization_warnings": graph_issues,
        "stats": build_stats(components, terminals, normalized_graph, graph_issues),
    }

    return normalized
