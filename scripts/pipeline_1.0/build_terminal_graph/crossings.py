from __future__ import annotations

# Verifica la presenza del ponte
# Se c'è la gobba allora è un ponte
def has_bridge_hump(binary: np.ndarray, x: int, y: int):
    h, w = binary.shape[:2]
    left_count = 0
    right_count = 0

    for dy in range(BRIDGE_HUMP_Y_MIN, BRIDGE_HUMP_Y_MAX + 1):
        yy = int(y) - dy
        if yy < 0:
            continue

        for dx in range(BRIDGE_HUMP_X_MIN, BRIDGE_HUMP_X_MAX + 1):
            lx = int(x) - dx
            rx = int(x) + dx
            if 0 <= lx < w and binary[yy, lx] > 0:
                left_count += 1
            if 0 <= rx < w and binary[yy, rx] > 0:
                right_count += 1

    return left_count >= 1 and right_count >= 1

# Rileva ponte sullo skeleton
# Cerca punti con:
#   continuita nelle 4 dir
#   hump
#   label valida
def detect_wire_bridges(skeleton_binary: np.ndarray, labels: np.ndarray):
    binary = np.where(skeleton_binary > 0, 1, 0).astype(np.uint8)
    h, w = binary.shape[:2]
    candidates = []

    for y in range(BRIDGE_HUMP_Y_MAX + 1, h - BRIDGE_PROBE_DISTANCE):
        for x in range(BRIDGE_PROBE_DISTANCE, w - BRIDGE_PROBE_DISTANCE):
            if binary[y, x] == 0:
                continue

            if labels[y, x] <= 0:
                continue

            left = int(np.sum(binary[y, x - BRIDGE_MIN_RUN:x]))
            right = int(np.sum(binary[y, x + 1:x + BRIDGE_MIN_RUN + 1]))
            up = int(np.sum(binary[y - BRIDGE_MIN_RUN:y, x]))
            down = int(np.sum(binary[y + 1:y + BRIDGE_MIN_RUN + 1, x]))

            if min(left, right, up, down) < BRIDGE_MIN_PIXELS_PER_DIRECTION:
                continue

            if not has_bridge_hump(binary, x, y):
                continue

            candidates.append({
                "x": int(x),
                "y": int(y),
                "label": int(labels[y, x]),
            })

    # Collassiamo piu' pixel dello stesso ponte in un solo candidato.
    collapsed = []
    for cand in candidates:
        if any(abs(cand["x"] - prev["x"]) <= 4 and abs(cand["y"] - prev["y"]) <= 4 for prev in collapsed):
            continue
        collapsed.append(cand)

    return collapsed

# Verifica se esiste il pallino pieno, se c'è allora il crossing è un nodod reale e non va spezzato
def has_filled_junction_dot(junction_binary: np.ndarray | None, x: int, y: int):
    if junction_binary is None:
        return False

    h, w = junction_binary.shape[:2]
    radius = PLAIN_CROSSING_DOT_RADIUS
    best_area = 0

    # Il candidato puo' cadere sul bordo del pallino per via dello spessore
    # della maschera. Cerchiamo quindi anche in una piccola griglia vicina.
    for dy in (-4, 0, 4):
        for dx in (-4, 0, 4):
            cx = int(x) + dx
            cy = int(y) + dy
            x1, y1, x2, y2 = clamp_window(
                cx - radius,
                cy - radius,
                cx + radius + 1,
                cy + radius + 1,
                w,
                h,
            )

            dot_area = int(np.count_nonzero(junction_binary[y1:y2, x1:x2] > 0))
            best_area = max(best_area, dot_area)

    return best_area >= PLAIN_CROSSING_DOT_AREA_MIN


# Rileva incroci ortogonali senza pallino di giunzione.
# Convenzione grafica: un incrocio con pallino e' un nodo reale, mentre una
# croce sottile senza pallino rappresenta due fili che si attraversano senza
# connessione. Lo skeleton da solo li fonderebbe in una stessa label.
def detect_plain_wire_crossings(
    skeleton_binary: np.ndarray,
    labels: np.ndarray,
    junction_binary: np.ndarray | None,
):
    # Use the one-pixel skeleton to test the actual crossing geometry.  The
    # thicker junction mask is useful only to decide whether a filled dot is
    # present; using it for directional runs can turn tight bends or stubs into
    # false four-way crossings.
    binary = np.where(skeleton_binary > 0, 1, 0).astype(np.uint8)
    h, w = binary.shape[:2]
    candidates = []

    run = PLAIN_CROSSING_MIN_RUN
    min_pixels = PLAIN_CROSSING_MIN_PIXELS_PER_DIRECTION

    for y in range(run, h - run):
        for x in range(run, w - run):
            if binary[y, x] == 0:
                continue

            source_label = nearest_split_label(labels, x, y, radius=3)
            if source_label is None:
                continue

            left = count_run(binary, x, y, -1, 0, run)
            right = count_run(binary, x, y, 1, 0, run)
            up = count_run(binary, x, y, 0, -1, run)
            down = count_run(binary, x, y, 0, 1, run)

            if min(left, right, up, down) < min_pixels:
                continue

            if has_filled_junction_dot(junction_binary, x, y):
                continue

            candidates.append({
                "x": int(x),
                "y": int(y),
                "label": int(source_label),
            })

    collapsed = []
    for cand in candidates:
        if any(abs(cand["x"] - prev["x"]) <= 5 and abs(cand["y"] - prev["y"]) <= 5 for prev in collapsed):
            continue
        collapsed.append(cand)

    return collapsed

# Trova label che contengono due o più terminali dello stesso componente
def labels_with_multi_terminal_self_short(
    terminals: list[dict],
    terminal_match_debug: dict,
):
    by_component_and_label = {}

    for term in terminals:
        matched_label = terminal_match_debug.get(term["terminal_id"], {}).get("matched_label")
        if matched_label is None:
            continue

        class_name = normalize_class_name(term.get("component_class_name"))
        if class_name in COMPONENT_BODY_ERASE_EXCLUDED_CLASSES:
            continue

        instance_id = term.get("instance_id")
        if instance_id is None:
            continue

        key = (str(instance_id), int(matched_label))
        by_component_and_label.setdefault(key, set()).add(term["terminal_id"])

    return {
        int(label)
        for (_, label), terminal_ids in by_component_and_label.items()
        if len(terminal_ids) >= 2
    }

# Dopo uno split, trova una nuova label più vicina a un certo punto
# Riassocia i terminali alle nuove connected components dopo il taglio
def nearest_split_label(split_labels: np.ndarray, x: int, y: int, radius: int = 6):
    h, w = split_labels.shape[:2]
    window = clamp_window(x - radius, y - radius, x + radius + 1, y + radius + 1, w, h)
    x1, y1, x2, y2 = window
    roi = split_labels[y1:y2, x1:x2]
    ys, xs = np.where(roi > 0)

    if len(xs) == 0:
        return None

    abs_xs = xs + x1
    abs_ys = ys + y1
    d2 = (abs_xs - float(x)) ** 2 + (abs_ys - float(y)) ** 2
    best_idx = int(np.argmin(d2))
    return int(split_labels[int(abs_ys[best_idx]), int(abs_xs[best_idx])])

# Esegue gli split dovuti ai ponti e a incroci senza il nodo (dot)
# Rileva i ponti
# Rileva incroci da spezzare
# Taglia localmente lo skeleton
# Ricalcola le connected components
# Riaggancia i terminali alle nuove lable
# Ricrea i gruppi finali
# Evita fusioni topologiche sbagliate
def split_bridge_labels(
    label_to_terminal_ids: dict,
    terminals: list[dict],
    terminal_match_debug: dict,
    skeleton_binary: np.ndarray,
    labels: np.ndarray,
    wire_extraction: dict | None = None,
):
    bridges = detect_wire_bridges(skeleton_binary, labels)
    bridge_labels = {int(bridge["label"]) for bridge in bridges}
    junction_binary = load_junction_support_binary(wire_extraction or {})
    self_short_labels = labels_with_multi_terminal_self_short(
        terminals,
        terminal_match_debug,
    )

    # I ponticelli a gobba sono un segnale grafico esplicito di "non giunzione".
    # Se una label contiene gia' un ponte, lasciamo che sia quel detector a
    # guidare lo split ed evitiamo tagli plain aggiuntivi sulla stessa label.
    plain_crossings = [
        crossing
        for crossing in detect_plain_wire_crossings(skeleton_binary, labels, junction_binary)
        if int(crossing["label"]) in self_short_labels
        and int(crossing["label"]) not in bridge_labels
    ]

    split_points = []
    for bridge in bridges:
        split_points.append({
            **bridge,
            "split_kind": "bridge_hump",
            "cut_half_width": BRIDGE_CUT_HALF_WIDTH,
            "cut_half_height": BRIDGE_CUT_HALF_HEIGHT,
            "probe_distance": BRIDGE_PROBE_DISTANCE,
        })

    for crossing in plain_crossings:
        split_points.append({
            **crossing,
            "split_kind": "plain_crossing_without_dot",
            "cut_half_width": PLAIN_CROSSING_CUT_HALF_WIDTH,
            "cut_half_height": PLAIN_CROSSING_CUT_HALF_HEIGHT,
            "probe_distance": PLAIN_CROSSING_PROBE_DISTANCE,
        })

    if not split_points:
        return label_to_terminal_ids

    split_labels_to_rebuild = {int(point["label"]) for point in split_points}
    if not split_labels_to_rebuild:
        return label_to_terminal_ids

    cut_skeleton = skeleton_binary.copy()
    h, w = cut_skeleton.shape[:2]
    for split_point in split_points:
        x = int(split_point["x"])
        y = int(split_point["y"])
        cut_half_width = int(split_point["cut_half_width"])
        cut_half_height = int(split_point["cut_half_height"])
        x1, y1, x2, y2 = clamp_window(
            x - cut_half_width,
            y - cut_half_height,
            x + cut_half_width + 1,
            y + cut_half_height + 1,
            w,
            h,
        )
        cut_skeleton[y1:y2, x1:x2] = 0

    _, split_labels, _, _ = cv2.connectedComponentsWithStats(cut_skeleton, connectivity=8)

    parent = {}

    def find(label):
        label = int(label)
        parent.setdefault(label, label)
        while parent[label] != label:
            parent[label] = parent[parent[label]]
            label = parent[label]
        return label

    def union(label_a, label_b):
        if label_a is None or label_b is None:
            return
        root_a = find(label_a)
        root_b = find(label_b)
        if root_a != root_b:
            parent[max(root_a, root_b)] = min(root_a, root_b)

    for split_point in split_points:
        x = int(split_point["x"])
        y = int(split_point["y"])
        probe_distance = int(split_point["probe_distance"])
        top_label = nearest_split_label(split_labels, x, y - probe_distance)
        bottom_label = nearest_split_label(split_labels, x, y + probe_distance)
        left_label = nearest_split_label(split_labels, x - probe_distance, y)
        right_label = nearest_split_label(split_labels, x + probe_distance, y)

        union(top_label, bottom_label)
        union(left_label, right_label)

    terminal_by_id = {term["terminal_id"]: term for term in terminals}
    split_groups = {}

    for original_label, terminal_ids in label_to_terminal_ids.items():
        if int(original_label) not in split_labels_to_rebuild:
            split_groups[(int(original_label), 0)] = list(terminal_ids)
            continue

        for terminal_id in terminal_ids:
            term = terminal_by_id.get(terminal_id)
            if term is None:
                continue

            split_label = nearest_split_label(
                split_labels,
                int(round(term["x"])),
                int(round(term["y"])),
                radius=max(
                    TERMINAL_SQUARE_FALLBACK_RADIUS,
                    BRIDGE_PROBE_DISTANCE,
                    PLAIN_CROSSING_PROBE_DISTANCE,
                ),
            )

            if split_label is None:
                matched_label = terminal_match_debug.get(terminal_id, {}).get("matched_label")
                split_key = ("unresolved", int(original_label), int(matched_label or original_label))
            else:
                split_key = ("split", int(original_label), find(split_label))

            split_groups.setdefault(split_key, []).append(terminal_id)

    final_groups = []
    handled_original_labels = set()

    for original_label, terminal_ids in label_to_terminal_ids.items():
        original_label = int(original_label)
        if original_label not in split_labels_to_rebuild:
            continue

        related_groups = [
            group_terminal_ids
            for key, group_terminal_ids in split_groups.items()
            if isinstance(key, tuple)
            and len(key) >= 2
            and key[0] in {"split", "unresolved"}
            and int(key[1]) == original_label
        ]

        if not related_groups:
            final_groups.append(list(terminal_ids))
            handled_original_labels.add(original_label)
            continue

        creates_singleton = any(len(set(group)) < 2 for group in related_groups)

        if creates_singleton:
            final_groups.append(list(terminal_ids))
        else:
            final_groups.extend(related_groups)

        handled_original_labels.add(original_label)

    for key, terminal_ids in split_groups.items():
        if (
            isinstance(key, tuple)
            and len(key) >= 2
            and key[0] in {"split", "unresolved"}
            and int(key[1]) in handled_original_labels
        ):
            continue

        final_groups.append(terminal_ids)

    relabeled = {}
    next_label = 1
    for terminal_ids in final_groups:
        while next_label in relabeled:
            next_label += 1
        relabeled[next_label] = sorted(set(terminal_ids))
        next_label += 1

    return relabeled

# =========================================================
# SPLIT LABEL IN CORRISPONDENZA DEI PONTI
# =========================================================
# Nei disegni circuitali un ponticello indica un incrocio senza giunzione.
# Lo skeleton, pero', puo' trasformarlo in una croce connessa. Rileviamo
# la gobba sopra l'incrocio e separiamo la label in due reti: verticale e
# orizzontale.

# Conta quanti pixel ci sono lungo una direzione per capire se ci sono davvero segmenti di filo sufficientemente lunghi nelle 4 direzioni
def count_run(binary: np.ndarray, x: int, y: int, dx: int, dy: int, limit: int):
    h, w = binary.shape[:2]
    count = 0
    cx = int(x) + int(dx)
    cy = int(y) + int(dy)

    while 0 <= cx < w and 0 <= cy < h and count < limit:
        if binary[cy, cx] == 0:
            break
        count += 1
        cx += int(dx)
        cy += int(dy)

    return count
import cv2
import numpy as np

from .config import (
    BRIDGE_CUT_HALF_HEIGHT,
    BRIDGE_CUT_HALF_WIDTH,
    BRIDGE_HUMP_X_MAX,
    BRIDGE_HUMP_X_MIN,
    BRIDGE_HUMP_Y_MAX,
    BRIDGE_HUMP_Y_MIN,
    BRIDGE_MIN_PIXELS_PER_DIRECTION,
    BRIDGE_MIN_RUN,
    BRIDGE_PROBE_DISTANCE,
    COMPONENT_BODY_ERASE_EXCLUDED_CLASSES,
    PLAIN_CROSSING_CUT_HALF_HEIGHT,
    PLAIN_CROSSING_CUT_HALF_WIDTH,
    PLAIN_CROSSING_DOT_AREA_MIN,
    PLAIN_CROSSING_DOT_RADIUS,
    PLAIN_CROSSING_MIN_PIXELS_PER_DIRECTION,
    PLAIN_CROSSING_MIN_RUN,
    PLAIN_CROSSING_PROBE_DISTANCE,
    TERMINAL_SQUARE_FALLBACK_RADIUS,
)
from .geometry import clamp_window
from .ids import normalize_class_name
from .skeleton_ops import load_junction_support_binary
