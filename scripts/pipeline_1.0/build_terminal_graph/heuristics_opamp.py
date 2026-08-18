"""Euristiche per collegare i terminali ausiliari degli op-amp."""

from .config import OPAMP_AUX_EXTERNAL_MAX_DX, OPAMP_AUX_EXTERNAL_MAX_DY
from .ids import get_preferred_terminal_public_name, normalize_class_name
from .label_union import LabelUnionFind, merge_label_groups


# =========================================================
# MATCH VIRTUALE AUX OPAMP -> TERMINALE ESTERNO
# =========================================================
# Gli ingressi ausiliari degli opamp (aux1 / aux2) possono cadere dentro o
# vicino al triangolo del simbolo. In quel caso il passo 04 maschera il
# componente e lo skeleton puo' perdere il tratto fino al terminale esterno
# VCC/VEE. Se un aux e un componente Terminal sono quasi verticalmente
# allineati, li trattiamo come la stessa connessione elettrica.

# Riconosce aux1 / aux2.
def is_opamp_aux_terminal(term: dict) -> bool:
    """Riconosce aux1/aux2 di un Operational_Amplifier."""
    class_name = normalize_class_name(term.get("component_class_name"))
    terminal_name = str(get_preferred_terminal_public_name(term) or "").strip().lower()
    return class_name == "operational_amplifier" and terminal_name.startswith("aux")

# Riconosce i componenti di Terminal.
def is_external_terminal_component(term: dict) -> bool:
    """Riconosce componenti Terminal esterni usati come VCC/VEE o riferimenti."""
    class_name = normalize_class_name(term.get("component_class_name"))
    return class_name == "terminal"

# Verifica se un terminale esterno sta nella direzione giusta rispetto a un aux.
# Es. Se aux è top il terminale deve stare sopra
def is_terminal_in_aux_direction(aux_term: dict, candidate_term: dict):
    """
    Verifica se un terminale esterno e' nella direzione corretta dell'aux.

    Se aux e' top il terminale deve stare sopra; se e' bottom deve stare sotto.
    """
    aux_y = float(aux_term["y"])
    candidate_y = float(candidate_term["y"])
    relative_position = aux_term.get("relative_position")

    if relative_position == "top":
        return candidate_y < aux_y
    if relative_position == "bottom":
        return candidate_y > aux_y

    return False


# Raccoglie le coppie plausibili
def collect_opamp_aux_external_terminal_pairs(
    terminals: list[dict],
    terminal_match_debug: dict,
):
    """Raccoglie coppie plausibili aux opamp -> terminale esterno allineato."""
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

# Unisce le label degli aux con quelle dei terminali esterni anche quando il filo viene mascherato.
def merge_opamp_aux_external_terminal_labels(
    label_to_terminal_ids: dict,
    terminals: list[dict],
    terminal_match_debug: dict,
):
    """Unisce le label degli aux con quelle dei terminali esterni allineati."""
    pairs = collect_opamp_aux_external_terminal_pairs(terminals, terminal_match_debug)
    if not pairs:
        return label_to_terminal_ids

    union_find = LabelUnionFind(label_to_terminal_ids)

    for pair in pairs:
        aux_id = pair["aux_term"]["terminal_id"]
        external_id = pair["external_term"]["terminal_id"]
        aux_label = terminal_match_debug.get(aux_id, {}).get("matched_label")
        external_label = terminal_match_debug.get(external_id, {}).get("matched_label")

        if aux_label is None or external_label is None:
            continue

        union_find.union(int(aux_label), int(external_label))

    return merge_label_groups(label_to_terminal_ids, union_find)
