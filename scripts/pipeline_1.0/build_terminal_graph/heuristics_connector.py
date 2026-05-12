from .ids import normalize_class_name


CONNECTOR_GND_ALIGN_TOL = 8.0
CONNECTOR_GND_MAX_GAP = 140.0


def _is_aligned_in_direction(source: dict, target: dict):
    side = source.get("relative_position")
    sx = float(source.get("x", 0.0))
    sy = float(source.get("y", 0.0))
    tx = float(target.get("x", 0.0))
    ty = float(target.get("y", 0.0))

    if side == "bottom":
        return abs(tx - sx) <= CONNECTOR_GND_ALIGN_TOL and 0 < ty - sy <= CONNECTOR_GND_MAX_GAP
    if side == "top":
        return abs(tx - sx) <= CONNECTOR_GND_ALIGN_TOL and 0 < sy - ty <= CONNECTOR_GND_MAX_GAP
    if side == "right":
        return abs(ty - sy) <= CONNECTOR_GND_ALIGN_TOL and 0 < tx - sx <= CONNECTOR_GND_MAX_GAP
    if side == "left":
        return abs(ty - sy) <= CONNECTOR_GND_ALIGN_TOL and 0 < sx - tx <= CONNECTOR_GND_MAX_GAP

    return False


def _direction_gap(source: dict, target: dict):
    side = source.get("relative_position")
    sx = float(source.get("x", 0.0))
    sy = float(source.get("y", 0.0))
    tx = float(target.get("x", 0.0))
    ty = float(target.get("y", 0.0))

    if side in {"top", "bottom"}:
        return abs(tx - sx), abs(ty - sy)
    return abs(ty - sy), abs(tx - sx)


def build_connector_aligned_gnd_edges(terminals: list[dict], terminal_graph: dict):
    connector_terms = [
        term
        for term in terminals
        if normalize_class_name(term.get("component_class_name")) == "connector"
    ]
    gnd_terms = [
        term
        for term in terminals
        if normalize_class_name(term.get("component_class_name")) in {"gnd", "ground"}
    ]

    edges = []
    for connector_term in connector_terms:
        connector_id = connector_term.get("terminal_id")
        if connector_id is None:
            continue
        if terminal_graph.get(connector_id):
            continue

        candidates = [
            gnd_term
            for gnd_term in gnd_terms
            if _is_aligned_in_direction(connector_term, gnd_term)
        ]
        if not candidates:
            continue

        best_gnd = min(candidates, key=lambda term: _direction_gap(connector_term, term))
        gnd_id = best_gnd.get("terminal_id")
        if gnd_id is None:
            continue
        edges.append((connector_id, gnd_id))

    return edges


def fix_stacked_connector_gnd_crossing_edges(terminals: list[dict], terminal_graph: dict):
    terminal_by_id = {term.get("terminal_id"): term for term in terminals}
    gnd_ids = {
        term.get("terminal_id")
        for term in terminals
        if normalize_class_name(term.get("component_class_name")) in {"gnd", "ground"}
    }

    connector_groups = {}
    for term in terminals:
        if normalize_class_name(term.get("component_class_name")) != "connector":
            continue
        if term.get("relative_position") not in {"left", "right"}:
            continue
        connector_groups.setdefault(str(term.get("instance_id")), []).append(term)

    for connector_terms in connector_groups.values():
        if len(connector_terms) < 2:
            continue

        sorted_terms = sorted(connector_terms, key=lambda term: float(term.get("y", 0.0)))
        bottom_term = sorted_terms[-1]
        previous_term = sorted_terms[-2]

        bottom_id = bottom_term.get("terminal_id")
        previous_id = previous_term.get("terminal_id")
        if bottom_id is None or previous_id is None:
            continue

        bottom_gnds = [neighbor for neighbor in terminal_graph.get(bottom_id, []) if neighbor in gnd_ids]
        for gnd_id in bottom_gnds:
            gnd_term = terminal_by_id.get(gnd_id)
            if gnd_term is None:
                continue

            gnd_y = float(gnd_term.get("y", 0.0))
            gnd_x = float(gnd_term.get("x", 0.0))
            bottom_y = float(bottom_term.get("y", 0.0))
            bottom_x = float(bottom_term.get("x", 0.0))
            previous_y = float(previous_term.get("y", 0.0))

            if not (gnd_y > bottom_y and abs(gnd_x - bottom_x) <= CONNECTOR_GND_MAX_GAP):
                continue
            if bottom_y - previous_y > 70.0:
                continue

            terminal_graph[bottom_id] = [
                neighbor for neighbor in terminal_graph.get(bottom_id, []) if neighbor != gnd_id
            ]
            terminal_graph[gnd_id] = [
                neighbor for neighbor in terminal_graph.get(gnd_id, []) if neighbor != bottom_id
            ]
            terminal_graph.setdefault(previous_id, []).append(gnd_id)
            terminal_graph.setdefault(gnd_id, []).append(previous_id)
