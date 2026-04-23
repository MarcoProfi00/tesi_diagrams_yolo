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

    for _, terminal_ids in label_to_terminal_ids.items():
        unique_ids = sorted(set(terminal_ids))
        if len(unique_ids) < 2:
            continue

        for source_id in unique_ids:
            others = [target_id for target_id in unique_ids if target_id != source_id]
            graph[source_id].extend(others)

    for terminal_id in graph:
        graph[terminal_id] = sorted(set(graph[terminal_id]))

    return graph
