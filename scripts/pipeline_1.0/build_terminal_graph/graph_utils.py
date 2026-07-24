"""Utility per trasformare gruppi di label in archi espliciti tra terminali."""

from .config import NON_SHORTING_MULTI_TERMINAL_CLASSES
from .ids import normalize_class_name


def _is_same_non_shorting_component(source: dict, target: dict) -> bool:
    """
    Riconosce terminali dello stesso componente multi-terminale non cortocircuitante.

    Connector, transistor, opamp, transformer ecc. possono avere piu' pin sulla
    stessa area di skeleton per artefatti grafici, ma i loro pin non devono
    diventare automaticamente tutti collegati tra loro.
    """
    if str(source.get("instance_id")) != str(target.get("instance_id")):
        return False

    source_class = normalize_class_name(source.get("component_class_name"))
    target_class = normalize_class_name(target.get("component_class_name"))
    if source_class != target_class:
        return False

    if source_class == "integrated_circuit":
        return False

    return source_class in NON_SHORTING_MULTI_TERMINAL_CLASSES

# =========================================================
# COSTRUZIONE DEL GRAFO FINALE TRA TERMINALI
# =========================================================
def build_terminal_graph(terminals, label_to_terminal_ids: dict):
    """
    Converte gruppi label -> terminali in un grafo terminale esplicito.

    Ogni connected component dello skeleton rappresenta un nodo elettrico
    implicito. Se su quella label cadono A, B e C, il grafo finale esplicita una
    clique: A-B, A-C, B-C. Durante la creazione evitiamo self-short interni di
    componenti che non devono condurre tra i propri pin.
    """
    graph = {term["terminal_id"]: [] for term in terminals}
    terminal_by_id = {term["terminal_id"]: term for term in terminals}

    for terminal_ids in label_to_terminal_ids.values():
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
