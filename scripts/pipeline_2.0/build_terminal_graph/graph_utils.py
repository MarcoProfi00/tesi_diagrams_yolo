# =========================================================
# COSTRUZIONE DEL GRAFO FINALE TRA TERMINALI
# =========================================================
# Per ogni gruppo di filo:
# - se il gruppo contiene almeno 2 terminali
# - allora ogni terminale è collegato a tutti gli altri terminali del gruppo

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
