"""Euristiche per reti di gate MOSFET e rail spezzati."""

import numpy as np

from .config import (
    MOSFET_GATE_ALIGN_Y_TOL,
    MOSFET_GATE_LABEL_MAX_GAP,
    MOSFET_GATE_MAX_DX,
)
from .geometry import horizontal_bbox_gap, min_label_distance
from .grouping import build_component_bbox_by_instance
from .ids import get_preferred_terminal_public_name, normalize_class_name


# =========================================================
# FUSIONE LABEL SPEZZATE TRA GATE MOSFET
# =========================================================
# Nei mirror e negli stadi differenziali le gate dei MOSFET possono essere
# unite da un filo orizzontale che passa vicino ai simboli. Se il passo 04
# spezza quel filo in due tronconi, fondiamo solo coppie di gate MOSFET
# quasi allineate, con componenti vicini e spezzoni di skeleton vicini.

# Dice se un terminale è un gate (G) del MOSFET.
def is_mosfet_gate_terminal(term: dict) -> bool:
    """Riconosce il terminale gate G di un MOSFET."""
    class_name = normalize_class_name(term.get("component_class_name"))
    terminal_name = str(get_preferred_terminal_public_name(term) or "").strip().upper()
    return "mosfet" in class_name and terminal_name == "G"


def is_mosfet_terminal(term: dict) -> bool:
    """Riconosce qualunque terminale appartenente a un MOSFET."""
    class_name = normalize_class_name(term.get("component_class_name"))
    return "mosfet" in class_name

# Unisce label spezzate che rappresentano la stessa rete di gate (G) del MOSFET:
# il filo passa spesso vicino ai simboli e può spezzarsi.
def merge_mosfet_gate_aligned_labels(
    label_to_terminal_ids: dict,
    terminals: list[dict],
    components: list[dict],
    terminal_match_debug: dict,
    labels: np.ndarray,
):
    """
    Unisce label spezzate che rappresentano la stessa rete di gate.

    La fusione e' volutamente conservativa: accetta solo gruppi composti da gate
    MOSFET, allineati e vicini, evitando di unire reti gia' complete.
    """
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

    bbox_by_instance = build_component_bbox_by_instance(components)
    gate_terms = [term for term in terminals if is_mosfet_gate_terminal(term)]
    terminal_by_id = {term["terminal_id"]: term for term in terminals}

    def label_group_is_only_mosfet_gates(label):
        terminal_ids = label_to_terminal_ids.get(int(label), [])
        if not terminal_ids:
            return False

        return all(
            is_mosfet_gate_terminal(terminal_by_id[terminal_id])
            for terminal_id in terminal_ids
            if terminal_id in terminal_by_id
        )

    for i, term_a in enumerate(gate_terms):
        info_a = terminal_match_debug.get(term_a["terminal_id"], {})
        label_a = info_a.get("matched_label")
        if label_a is None:
            continue

        bbox_a = bbox_by_instance.get(str(term_a.get("instance_id")))
        if bbox_a is None:
            continue

        for term_b in gate_terms[i + 1:]:
            info_b = terminal_match_debug.get(term_b["terminal_id"], {})
            label_b = info_b.get("matched_label")
            if label_b is None or int(label_a) == int(label_b):
                continue

            bbox_b = bbox_by_instance.get(str(term_b.get("instance_id")))
            if bbox_b is None:
                continue

            # Questa fusione serve a ricucire fili di gate spezzati dal passo 04.
            # Se una delle due label contiene gia' induttori, resistori, terminali
            # o altri componenti, allora non e' uno spezzone isolato di gate ma un
            # nodo elettrico gia' formato: fonderlo rischia di unire reti distinte.
            if not label_group_is_only_mosfet_gates(label_a):
                continue
            if not label_group_is_only_mosfet_gates(label_b):
                continue

            if abs(float(term_a["y"]) - float(term_b["y"])) > MOSFET_GATE_ALIGN_Y_TOL:
                continue

            if horizontal_bbox_gap(bbox_a, bbox_b) > MOSFET_GATE_MAX_DX:
                continue

            label_gap = min_label_distance(labels, int(label_a), int(label_b))
            if label_gap is None or label_gap > MOSFET_GATE_LABEL_MAX_GAP:
                continue

            union(int(label_a), int(label_b))

    merged = {}
    for label, terminal_ids in label_to_terminal_ids.items():
        root = find(int(label))
        merged.setdefault(root, []).extend(terminal_ids)

    return {
        int(label): sorted(set(terminal_ids))
        for label, terminal_ids in merged.items()
    }

# Unisce gruppi composti solo da terminali MOSFET, se rappresentano la stessa rail di gate.
def merge_mosfet_gate_rail_groups(
    label_to_terminal_ids: dict,
    terminals: list[dict],
    components: list[dict],
):
    """
    Unisce gruppi di soli MOSFET quando formano una rail di gate.

    Dopo gli split per crossing possono restare piccole reti MOSFET separate ma
    allineate; questa euristica le ricompone se non includono componenti esterni.
    """
    terminal_by_id = {term["terminal_id"]: term for term in terminals}
    bbox_by_instance = build_component_bbox_by_instance(components)

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

    def known_terms_for_label(label):
        return [
            terminal_by_id[terminal_id]
            for terminal_id in label_to_terminal_ids.get(int(label), [])
            if terminal_id in terminal_by_id
        ]

    def gate_terms_for_mosfet_only_group(label):
        known_terms = known_terms_for_label(label)
        if not known_terms:
            return []

        # Dopo gli split una net di soli MOSFET puo' contenere gate e piccoli
        # residui di source/drain dello stesso rail. La consideriamo ricucibile
        # solo se non contiene passivi, ground, batteria o terminali esterni.
        if not all(is_mosfet_terminal(term) for term in known_terms):
            return []

        return [term for term in known_terms if is_mosfet_gate_terminal(term)]

    gate_groups = [
        (label, gate_terms_for_mosfet_only_group(label))
        for label in label_to_terminal_ids
    ]
    gate_groups = [
        (label, gate_terms)
        for label, gate_terms in gate_groups
        if gate_terms
    ]

    for i, (label_a, gate_terms_a) in enumerate(gate_groups):
        for label_b, gate_terms_b in gate_groups[i + 1:]:
            best_pair = None

            for gate_a in gate_terms_a:
                bbox_a = bbox_by_instance.get(str(gate_a.get("instance_id")))
                if bbox_a is None:
                    continue

                for gate_b in gate_terms_b:
                    bbox_b = bbox_by_instance.get(str(gate_b.get("instance_id")))
                    if bbox_b is None:
                        continue

                    dy = abs(float(gate_a["y"]) - float(gate_b["y"]))
                    if dy > MOSFET_GATE_ALIGN_Y_TOL:
                        continue

                    gap = horizontal_bbox_gap(bbox_a, bbox_b)
                    if gap > MOSFET_GATE_MAX_DX:
                        continue

                    candidate = (dy, gap)
                    if best_pair is None or candidate < best_pair:
                        best_pair = candidate

            if best_pair is None:
                continue

            union(int(label_a), int(label_b))

    merged = {}
    for label, terminal_ids in label_to_terminal_ids.items():
        root = find(int(label))
        merged.setdefault(root, []).extend(terminal_ids)

    return {
        int(label): sorted(set(terminal_ids))
        for label, terminal_ids in merged.items()
    }
