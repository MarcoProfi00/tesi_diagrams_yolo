from .config import OPAMP_AUX_EXTERNAL_MAX_DX, OPAMP_AUX_EXTERNAL_MAX_DY
from .ids import get_preferred_terminal_public_name, normalize_class_name


# =========================================================
# MATCH VIRTUALE AUX OPAMP -> TERMINALE ESTERNO
# =========================================================
# Gli ingressi ausiliari degli opamp (aux1 / aux2) possono cadere dentro o
# vicino al triangolo del simbolo. In quel caso il passo 04 maschera il
# componente e lo skeleton puo' perdere il tratto fino al terminale esterno
# VCC/VEE. Se un aux e un componente Terminal sono quasi verticalmente
# allineati, li trattiamo come la stessa connessione elettrica.

def is_opamp_aux_terminal(term: dict) -> bool:
    class_name = normalize_class_name(term.get("component_class_name"))
    terminal_name = str(get_preferred_terminal_public_name(term) or "").strip().lower()
    return class_name == "operational_amplifier" and terminal_name.startswith("aux")


def is_external_terminal_component(term: dict) -> bool:
    class_name = normalize_class_name(term.get("component_class_name"))
    return class_name == "terminal"


def is_terminal_in_aux_direction(aux_term: dict, candidate_term: dict):
    aux_y = float(aux_term["y"])
    candidate_y = float(candidate_term["y"])
    relative_position = aux_term.get("relative_position")

    if relative_position == "top":
        return candidate_y < aux_y
    if relative_position == "bottom":
        return candidate_y > aux_y

    return False


def collect_opamp_aux_external_terminal_pairs(
    terminals: list[dict],
    terminal_match_debug: dict,
):
    pairs = []
    terminal_candidates = [
        term
        for term in terminals
        if is_external_terminal_component(term)
        and terminal_match_debug.get(term["terminal_id"], {}).get("matched_label") is not None
    ]

    for aux_term in terminals:
        if not is_opamp_aux_terminal(aux_term):
            continue

        aux_match = terminal_match_debug.get(aux_term["terminal_id"], {})
        if aux_match.get("matched_label") is None:
            continue

        candidates = []
        for candidate in terminal_candidates:
            if not is_terminal_in_aux_direction(aux_term, candidate):
                continue

            dx = abs(float(candidate["x"]) - float(aux_term["x"]))
            dy = abs(float(candidate["y"]) - float(aux_term["y"]))

            if dx > OPAMP_AUX_EXTERNAL_MAX_DX:
                continue
            if dy > OPAMP_AUX_EXTERNAL_MAX_DY:
                continue

            candidates.append({
                "aux_term": aux_term,
                "external_term": candidate,
                "dx": dx,
                "dy": dy,
            })

        if not candidates:
            continue

        best = min(candidates, key=lambda item: (item["dx"], item["dy"]))
        pairs.append(best)

    return pairs


def merge_opamp_aux_external_terminal_labels(
    label_to_terminal_ids: dict,
    terminals: list[dict],
    terminal_match_debug: dict,
):
    pairs = collect_opamp_aux_external_terminal_pairs(terminals, terminal_match_debug)
    if not pairs:
        return label_to_terminal_ids

    parent = {int(label): int(label) for label in label_to_terminal_ids.keys()}

    def find(label):
        label = int(label)
        parent.setdefault(label, label)
        while parent[label] != label:
            parent[label] = parent[parent[label]]
            label = parent[label]
        return label

    def union(label_a, label_b):
        root_a = find(label_a)
        root_b = find(label_b)
        if root_a != root_b:
            parent[max(root_a, root_b)] = min(root_a, root_b)

    for pair in pairs:
        aux_id = pair["aux_term"]["terminal_id"]
        external_id = pair["external_term"]["terminal_id"]
        aux_label = terminal_match_debug.get(aux_id, {}).get("matched_label")
        external_label = terminal_match_debug.get(external_id, {}).get("matched_label")

        if aux_label is None or external_label is None:
            continue

        union(int(aux_label), int(external_label))

    merged = {}
    for label, terminal_ids in label_to_terminal_ids.items():
        root = find(int(label))
        merged.setdefault(root, []).extend(terminal_ids)

    return {
        int(label): sorted(set(terminal_ids))
        for label, terminal_ids in merged.items()
    }
