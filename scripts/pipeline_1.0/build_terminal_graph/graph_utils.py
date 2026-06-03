"""Utility per trasformare gruppi di label in archi espliciti tra terminali."""

from .config import NON_SHORTING_MULTI_TERMINAL_CLASSES
from .ids import normalize_class_name


def _is_same_non_shorting_component(source: dict, target: dict) -> bool:
    if str(source.get("instance_id")) != str(target.get("instance_id")):
        return False

    source_class = normalize_class_name(source.get("component_class_name"))
    target_class = normalize_class_name(target.get("component_class_name"))
    if source_class != target_class:
        return False

    if source_class == "integrated_circuit" and _is_valid_same_ic_external_edge(source, target):
        return False

    return source_class in NON_SHORTING_MULTI_TERMINAL_CLASSES


def _is_valid_same_ic_external_edge(source: dict, target: dict) -> bool:
    source_side = str(source.get("relative_position"))
    target_side = str(target.get("relative_position"))
    sides = {source_side, target_side}
    dx = float(source.get("x", 0.0)) - float(target.get("x", 0.0))
    dy = float(source.get("y", 0.0)) - float(target.get("y", 0.0))
    distance = (dx * dx + dy * dy) ** 0.5

    if len(sides) == 1:
        return distance <= 100.0

    if len(sides) != 2:
        return False
    if not sides.intersection({"top", "bottom"}) or not sides.intersection({"left", "right"}):
        return False

    return distance <= 230.0

# =========================================================
# COSTRUZIONE DEL GRAFO FINALE TRA TERMINALI
# =========================================================
# Per ogni label
#   prende i terminali di quel gruppo
#   crea una clique completa tra loro trasformando i nodi impliciti in archi espliciti
# Es:   A -> [B, C]
#       B -> [A, C]
#       C -> [A, B]
def build_terminal_graph(terminals, label_to_terminal_ids: dict):
    graph = {term["terminal_id"]: [] for term in terminals}
    terminal_by_id = {term["terminal_id"]: term for term in terminals}

    for _, terminal_ids in label_to_terminal_ids.items():
        unique_ids = sorted(set(terminal_ids))
        if len(unique_ids) < 2:
            continue

        for source_id in unique_ids:
            source = terminal_by_id.get(source_id)
            others = []
            for target_id in unique_ids:
                if target_id == source_id:
                    continue
                target = terminal_by_id.get(target_id)
                if source is not None and target is not None and _is_same_non_shorting_component(source, target):
                    continue
                others.append(target_id)
            graph[source_id].extend(others)

    for terminal_id in graph:
        graph[terminal_id] = sorted(set(graph[terminal_id]))

    return graph
