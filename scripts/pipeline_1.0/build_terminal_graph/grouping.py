from .config import NON_SHORTING_MULTI_TERMINAL_CLASSES
from .ids import normalize_class_name


# =========================================================
# COSTRUZIONE DEI GRUPPI INTERNI DI FILO
# =========================================================
# Costruisce la mappa interna label -> [terminal_id, terminal_id, ...]
# Legge matched_label di ogni terminale
# raggruppa i terminali per label
# deduplica e ordina 
def build_label_to_terminal_ids(match_debug_by_terminal_id: dict):
    label_to_terminal_ids = {}

    for terminal_id, match_info in match_debug_by_terminal_id.items():
        matched_label = match_info.get("matched_label")
        if matched_label is None:
            continue
        label_to_terminal_ids.setdefault(int(matched_label), []).append(terminal_id)

    cleaned = {}
    for label, terminal_ids in label_to_terminal_ids.items():
        cleaned[int(label)] = sorted(set(terminal_ids))

    return cleaned

# Elimina gruppi in cui più terminali dello stesso connector o transformer sono finiti sulla stessa label
# Connector e Transformer non devono essere cortocircuitati internamente
def remove_non_shorting_component_self_matches(
    label_to_terminal_ids: dict,
    terminals: list[dict],
    terminal_match_debug: dict,
):
    terminal_by_id = {term["terminal_id"]: term for term in terminals}
    cleaned = {}

    for label, terminal_ids in label_to_terminal_ids.items():
        unique_ids = sorted(set(terminal_ids))
        if len(unique_ids) < 2:
            cleaned[int(label)] = unique_ids
            continue

        terms = [terminal_by_id.get(terminal_id) for terminal_id in unique_ids]
        if any(term is None for term in terms):
            cleaned[int(label)] = unique_ids
            continue

        instance_ids = {str(term.get("instance_id")) for term in terms}
        class_names = {normalize_class_name(term.get("component_class_name")) for term in terms}
        if (
            len(instance_ids) != 1
            or len(class_names) != 1
            or next(iter(class_names)) not in NON_SHORTING_MULTI_TERMINAL_CLASSES
        ):
            cleaned[int(label)] = unique_ids
            continue

        for terminal_id in unique_ids:
            terminal_match_debug[terminal_id] = {
                "terminal_id": terminal_id,
                "candidate_labels": terminal_match_debug.get(terminal_id, {}).get("candidate_labels", []),
                "matched_label": None,
                "match_mode": "unmatched_same_component_artifact",
                "search_window": terminal_match_debug.get(terminal_id, {}).get("search_window"),
                "snap_point": None,
                "snap_distance": None,
                "is_suspicious": False,
            }

    return cleaned

# Costruisce una mappa instance_id -> bbox
# è usato in molte heuristics che confrontano distanze tra componenti
def build_component_bbox_by_instance(components: list[dict]):
    bbox_by_instance = {}
    for comp in components:
        instance_id = comp.get("instance_id")
        bbox = comp.get("bbox")
        if instance_id is None or not bbox or len(bbox) != 4:
            continue
        bbox_by_instance[str(instance_id)] = [float(v) for v in bbox]
    return bbox_by_instance
