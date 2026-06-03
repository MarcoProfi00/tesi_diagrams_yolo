"""Raggruppamento dei terminali agganciati alle stesse label dello skeleton."""

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

# Elimina gruppi in cui più terminali dello stesso connector o transformer
# sono finiti sulla stessa label. Connector e Transformer non devono essere
# cortocircuitati internamente.
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

        if _is_valid_same_ic_external_branch(unique_ids, terms, label, terminal_match_debug, terminal_by_id):
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


def _is_valid_same_ic_external_branch(
    terminal_ids: list[str],
    terms: list[dict],
    label: int,
    terminal_match_debug: dict,
    terminal_by_id: dict,
):
    if len(terms) != 2:
        return False
    if {
        normalize_class_name(term.get("component_class_name"))
        for term in terms
    } != {"integrated_circuit"}:
        return False

    sides = {str(term.get("relative_position")) for term in terms}
    if len(sides) == 1:
        return _min_terminal_distance(terms[:1], terms[1:]) <= 100.0

    if len(sides) != 2:
        return False
    if not sides.intersection({"top", "bottom"}) or not sides.intersection({"left", "right"}):
        return False

    if _min_terminal_distance(terms[:1], terms[1:]) > 230.0:
        return False

    return True


def split_polarized_capacitor_self_short_groups(
    label_to_terminal_ids: dict,
    terminals: list[dict],
):
    terminal_by_id = {term["terminal_id"]: term for term in terminals}
    relabeled_groups = []

    for _, terminal_ids in label_to_terminal_ids.items():
        unique_ids = sorted(set(terminal_ids))
        split_groups = _split_group_on_polarized_capacitor_axis(unique_ids, terminal_by_id)
        relabeled_groups.extend(split_groups)

    relabeled = {}
    for index, terminal_ids in enumerate(relabeled_groups, start=1):
        relabeled[index] = sorted(set(terminal_ids))

    return relabeled


def _split_group_on_polarized_capacitor_axis(
    terminal_ids: list[str],
    terminal_by_id: dict,
):
    terms = [terminal_by_id.get(terminal_id) for terminal_id in terminal_ids]
    terms = [term for term in terms if term is not None]

    by_instance = {}
    for term in terms:
        if normalize_class_name(term.get("component_class_name")) != "polarized_capacitor":
            continue
        by_instance.setdefault(str(term.get("instance_id")), []).append(term)

    for cap_terms in by_instance.values():
        if len(cap_terms) != 2:
            continue

        term_a, term_b = cap_terms
        try:
            ax = float(term_a["x"])
            ay = float(term_a["y"])
            bx = float(term_b["x"])
            by = float(term_b["y"])
        except (KeyError, TypeError, ValueError):
            continue

        if abs(ax - bx) >= abs(ay - by):
            midpoint = (ax + bx) / 2.0
            first_side = [
                term["terminal_id"]
                for term in terms
                if float(term.get("x", midpoint)) <= midpoint
            ]
            second_side = [
                term["terminal_id"]
                for term in terms
                if float(term.get("x", midpoint)) > midpoint
            ]
        else:
            midpoint = (ay + by) / 2.0
            first_side = [
                term["terminal_id"]
                for term in terms
                if float(term.get("y", midpoint)) <= midpoint
            ]
            second_side = [
                term["terminal_id"]
                for term in terms
                if float(term.get("y", midpoint)) > midpoint
            ]

        # Non accettiamo split che lasciano un polo isolato: in quei casi il
        # gruppo e' ambiguo e il grafo validato e' piu' affidabile dello split.
        if len(set(first_side)) >= 2 and len(set(second_side)) >= 2:
            return [first_side, second_side]

    return [terminal_ids]

# Costruisce una mappa instance_id -> bbox
# è usato in molte euristiche che confrontano distanze tra componenti
def merge_split_grounded_ic_side_branches(
    label_to_terminal_ids: dict,
    terminals: list[dict],
    terminal_match_debug: dict,
):
    terminal_by_id = {term["terminal_id"]: term for term in terminals}
    groups = [sorted(set(ids)) for ids in label_to_terminal_ids.values()]
    merged = [False] * len(groups)
    output_groups = []

    for idx, terminal_ids in enumerate(groups):
        if merged[idx]:
            continue

        current = set(terminal_ids)
        current_original_labels = _original_matched_labels(current, terminal_match_debug)

        changed = True
        while changed:
            changed = False
            for other_idx, other_ids in enumerate(groups):
                if other_idx == idx or merged[other_idx]:
                    continue

                other = set(other_ids)
                other_original_labels = _original_matched_labels(other, terminal_match_debug)
                if not current_original_labels.intersection(other_original_labels):
                    continue

                if _should_merge_grounded_ic_side_branch(current, other, terminal_by_id):
                    current.update(other)
                    current_original_labels.update(other_original_labels)
                    merged[other_idx] = True
                    changed = True
                elif _should_merge_grounded_ic_side_branch(other, current, terminal_by_id):
                    current.update(other)
                    current_original_labels.update(other_original_labels)
                    merged[other_idx] = True
                    changed = True

        merged[idx] = True
        output_groups.append(sorted(current))

    return {
        index: terminal_ids
        for index, terminal_ids in enumerate(output_groups, start=1)
    }


def _original_matched_labels(terminal_ids: set[str], terminal_match_debug: dict):
    labels = set()
    for terminal_id in terminal_ids:
        label = terminal_match_debug.get(terminal_id, {}).get("matched_label")
        if label is not None:
            labels.add(int(label))
    return labels


def _should_merge_grounded_ic_side_branch(
    switch_branch_ids: set[str],
    grounded_ic_ids: set[str],
    terminal_by_id: dict,
):
    switch_branch_terms = [terminal_by_id.get(terminal_id) for terminal_id in switch_branch_ids]
    grounded_terms = [terminal_by_id.get(terminal_id) for terminal_id in grounded_ic_ids]
    if any(term is None for term in switch_branch_terms + grounded_terms):
        return False

    switch_classes = {
        normalize_class_name(term.get("component_class_name"))
        for term in switch_branch_terms
    }
    has_switch_or_button = bool(switch_classes.intersection({"push_button", "switch"}))
    has_series_resistor = "resistor" in switch_classes
    if not (has_switch_or_button and has_series_resistor):
        return False

    grounded_classes = {
        normalize_class_name(term.get("component_class_name"))
        for term in grounded_terms
    }
    if not grounded_classes.intersection({"gnd", "ground"}):
        return False

    ic_terms = [
        term
        for term in grounded_terms
        if normalize_class_name(term.get("component_class_name")) == "integrated_circuit"
    ]
    if len(ic_terms) < 2:
        return False

    ic_instances = {str(term.get("instance_id")) for term in ic_terms}
    ic_sides = {str(term.get("relative_position")) for term in ic_terms}
    if len(ic_instances) != 1 or len(ic_sides) != 1:
        return False

    return _min_terminal_distance(switch_branch_terms, grounded_terms) <= 130.0


def _min_terminal_distance(first_terms: list[dict], second_terms: list[dict]):
    best = None
    for term_a in first_terms:
        ax = float(term_a.get("x", 0.0))
        ay = float(term_a.get("y", 0.0))
        for term_b in second_terms:
            bx = float(term_b.get("x", 0.0))
            by = float(term_b.get("y", 0.0))
            dist = ((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5
            if best is None or dist < best:
                best = dist
    return float(best or 0.0)


def split_same_side_ic_fanout_groups(
    label_to_terminal_ids: dict,
    terminals: list[dict],
):
    terminal_by_id = {term["terminal_id"]: term for term in terminals}
    output_groups = []

    for terminal_ids in label_to_terminal_ids.values():
        unique_ids = sorted(set(terminal_ids))
        split_groups = _split_same_side_ic_fanout_group(unique_ids, terminal_by_id)
        output_groups.extend(split_groups)

    return {
        index: terminal_ids
        for index, terminal_ids in enumerate(output_groups, start=1)
    }


def _split_same_side_ic_fanout_group(
    terminal_ids: list[str],
    terminal_by_id: dict,
):
    terms = [terminal_by_id.get(terminal_id) for terminal_id in terminal_ids]
    terms = [term for term in terms if term is not None]
    if len(terms) != len(terminal_ids):
        return [terminal_ids]

    ic_terms = [
        term
        for term in terms
        if normalize_class_name(term.get("component_class_name")) == "integrated_circuit"
    ]
    external_terms = [
        term
        for term in terms
        if normalize_class_name(term.get("component_class_name")) != "integrated_circuit"
    ]
    if len(ic_terms) < 2 or len(ic_terms) != len(external_terms):
        return [terminal_ids]

    ic_instances = {str(term.get("instance_id")) for term in ic_terms}
    ic_sides = {str(term.get("relative_position")) for term in ic_terms}
    external_classes = {
        normalize_class_name(term.get("component_class_name"))
        for term in external_terms
    }
    if len(ic_instances) != 1 or len(ic_sides) != 1 or len(external_classes) != 1:
        return [terminal_ids]
    if external_classes.intersection({"gnd", "ground", "terminal"}):
        return [terminal_ids]

    side = next(iter(ic_sides))
    if side not in {"left", "right", "top", "bottom"}:
        return [terminal_ids]

    sorted_ic_terms = sorted(ic_terms, key=lambda term: float(term.get("y", 0.0)))
    if side == "right":
        sorted_external_terms = sorted(external_terms, key=lambda term: float(term.get("x", 0.0)))
    elif side == "left":
        sorted_external_terms = sorted(external_terms, key=lambda term: -float(term.get("x", 0.0)))
    elif side == "bottom":
        sorted_ic_terms = sorted(ic_terms, key=lambda term: float(term.get("x", 0.0)))
        sorted_external_terms = sorted(external_terms, key=lambda term: float(term.get("y", 0.0)))
    else:
        sorted_ic_terms = sorted(ic_terms, key=lambda term: float(term.get("x", 0.0)))
        sorted_external_terms = sorted(external_terms, key=lambda term: -float(term.get("y", 0.0)))

    return [
        [ic_term["terminal_id"], external_term["terminal_id"]]
        for ic_term, external_term in zip(sorted_ic_terms, sorted_external_terms)
    ]


def build_component_bbox_by_instance(components: list[dict]):
    bbox_by_instance = {}
    for comp in components:
        instance_id = comp.get("instance_id")
        bbox = comp.get("bbox")
        if instance_id is None or not bbox or len(bbox) != 4:
            continue
        bbox_by_instance[str(instance_id)] = [float(v) for v in bbox]
    return bbox_by_instance
