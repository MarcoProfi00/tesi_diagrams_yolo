# =========================================================
# PULIZIA SKELETON DENTRO I COMPONENTI A DUE TERMINALI
# =========================================================
# Il passo 04 puo' lasciare nello skeleton tratti del corpo del componente
# (ad esempio la zig-zag del resistore). Se quei pixel restano collegati ai
# fili esterni, i due capi del componente finiscono nella stessa connected
# component e il grafo crea un "mega nodo" non reale.
#
# Per il passo 05 il corpo di un componente a due terminali non e' un filo:
# deve separare i due morsetti. Per questo cancelliamo solo l'interno del
# bbox dei componenti a due terminali, lasciando vivi i piccoli stub esterni
# vicino ai terminali.

from __future__ import annotations

FACING_RESTORE_MAX_AXIS_GAP = 52
FACING_RESTORE_MAX_LATERAL_DELTA = 14
FACING_RESTORE_MAX_BBOX_GAP = 28
FACING_RESTORE_MAX_BBOX_OVERLAP = 36
FACING_RESTORE_MIN_PROJECTION_OVERLAP_RATIO = 0.45
FACING_RESTORE_THICKNESS = 4
FACING_RESTORE_LABEL_RADIUS = 5

# Decide se cancellare il corpo del componente dallo skeleton
# Cancella i componenti con 2 terminali perchè i terminali non devono risultare cortocircuitati dal corpo del simbolo
def should_erase_component_body_from_skeleton(component: dict):
    class_name = normalize_class_name(component.get("class_name"))
    terminals = component.get("terminals", [])

    if class_name in {"connector", "integrated_circuit", "npn_transistor", "pnp_transistor", "operational_amplifier"}:
        return True

    if class_name in COMPONENT_BODY_ERASE_EXCLUDED_CLASSES:
        return False

    return len(terminals) == 2


def _component_bbox(component: dict):
    return component.get("body_bbox") or component.get("bbox")


def _bbox_projection_overlap_ratio(a0, a1, b0, b1):
    inter = max(0.0, min(float(a1), float(b1)) - max(float(a0), float(b0)))
    len_a = max(1.0, float(a1) - float(a0))
    len_b = max(1.0, float(b1) - float(b0))
    return inter / max(1.0, min(len_a, len_b))


def _flatten_component_terminals(components: list[dict]):
    flat = []
    for component in components:
        bbox = _component_bbox(component)
        instance_id = component.get("instance_id")
        if bbox is None or instance_id is None:
            continue
        for term in component.get("terminals", []) or []:
            flat.append({
                "instance_id": str(instance_id),
                "component_bbox": bbox,
                "term": term,
            })
    return flat


def _find_facing_restore_pairs(components: list[dict]):
    terminals = _flatten_component_terminals(components)
    pairs = []

    for idx, item_a in enumerate(terminals):
        term_a = item_a["term"]
        side_a = str(term_a.get("relative_position") or "").lower()
        bbox_a = item_a["component_bbox"]

        for item_b in terminals[idx + 1:]:
            if item_a["instance_id"] == item_b["instance_id"]:
                continue

            term_b = item_b["term"]
            side_b = str(term_b.get("relative_position") or "").lower()
            bbox_b = item_b["component_bbox"]
            x_a = float(term_a["x"])
            y_a = float(term_a["y"])
            x_b = float(term_b["x"])
            y_b = float(term_b["y"])

            if {side_a, side_b} == {"top", "bottom"}:
                lateral_delta = abs(x_a - x_b)
                axis_gap = abs(y_a - y_b)
                bbox_gap = min(
                    abs(float(bbox_a[1]) - float(bbox_b[3])),
                    abs(float(bbox_b[1]) - float(bbox_a[3])),
                )
                bbox_overlap = max(
                    0.0,
                    min(float(bbox_a[3]), float(bbox_b[3])) - max(float(bbox_a[1]), float(bbox_b[1])),
                )
                projection_overlap = _bbox_projection_overlap_ratio(
                    float(bbox_a[0]), float(bbox_a[2]),
                    float(bbox_b[0]), float(bbox_b[2]),
                )
            elif {side_a, side_b} == {"left", "right"}:
                lateral_delta = abs(y_a - y_b)
                axis_gap = abs(x_a - x_b)
                bbox_gap = min(
                    abs(float(bbox_a[0]) - float(bbox_b[2])),
                    abs(float(bbox_b[0]) - float(bbox_a[2])),
                )
                bbox_overlap = max(
                    0.0,
                    min(float(bbox_a[2]), float(bbox_b[2])) - max(float(bbox_a[0]), float(bbox_b[0])),
                )
                projection_overlap = _bbox_projection_overlap_ratio(
                    float(bbox_a[1]), float(bbox_a[3]),
                    float(bbox_b[1]), float(bbox_b[3]),
                )
            else:
                continue

            if lateral_delta > FACING_RESTORE_MAX_LATERAL_DELTA:
                continue
            if axis_gap > FACING_RESTORE_MAX_AXIS_GAP:
                continue
            if projection_overlap < FACING_RESTORE_MIN_PROJECTION_OVERLAP_RATIO:
                continue
            if bbox_gap > FACING_RESTORE_MAX_BBOX_GAP and bbox_overlap <= 0.0:
                continue
            if bbox_overlap > FACING_RESTORE_MAX_BBOX_OVERLAP:
                continue

            pairs.append((term_a, term_b))

    return pairs


def _nearest_label_in_radius(labels: np.ndarray, x: float, y: float, radius: int):
    h, w = labels.shape[:2]
    tx = int(round(float(x)))
    ty = int(round(float(y)))
    x1 = max(0, tx - int(radius))
    x2 = min(w, tx + int(radius) + 1)
    y1 = max(0, ty - int(radius))
    y2 = min(h, ty + int(radius) + 1)
    roi = labels[y1:y2, x1:x2]
    ys, xs = np.where(roi > 0)
    if len(xs) == 0:
        return None

    abs_xs = xs + x1
    abs_ys = ys + y1
    d2 = (abs_xs - float(x)) ** 2 + (abs_ys - float(y)) ** 2
    best_idx = int(np.argmin(d2))
    px = int(abs_xs[best_idx])
    py = int(abs_ys[best_idx])
    return int(labels[py, px])

# Cancella i body dei componenti a due terminali dallo skeleton
# Per ogni componente
#   prende il bbox
#   applica un padding interno
#   azzera i pixel interni
# Rompe i nodi FP generati dal simbolo del componente
def erase_component_bodies_from_skeleton(
    skeleton_binary: np.ndarray,
    components: list[dict],
):
    cleaned = skeleton_binary.copy()
    h, w = cleaned.shape[:2]
    original_binary = (skeleton_binary > 0).astype(np.uint8)
    _, original_labels, _, _ = cv2.connectedComponentsWithStats(original_binary, connectivity=8)

    for component in components:
        if not should_erase_component_body_from_skeleton(component):
            continue

        bbox = component.get("body_bbox") or component.get("bbox")
        if not bbox or len(bbox) != 4:
            continue

        x1, y1, x2, y2 = map(float, bbox)
        class_name = normalize_class_name(component.get("class_name"))
        if class_name == "connector":
            pad = -10.0
        elif class_name == "integrated_circuit":
            pad = -2.0
        else:
            pad = float(COMPONENT_BODY_ERASE_PADDING)

        erase_window = clamp_window(
            x1 + pad,
            y1 + pad,
            x2 - pad,
            y2 - pad,
            w,
            h,
        )
        ex1, ey1, ex2, ey2 = erase_window

        if ex2 <= ex1 or ey2 <= ey1:
            continue

        cleaned[ey1:ey2, ex1:ex2] = 0
        if class_name == "connector":
            cut_connector_pin_separators(cleaned, component)

    for term_a, term_b in _find_facing_restore_pairs(components):
        label_a = _nearest_label_in_radius(
            original_labels,
            term_a.get("x", 0.0),
            term_a.get("y", 0.0),
            radius=FACING_RESTORE_LABEL_RADIUS,
        )
        label_b = _nearest_label_in_radius(
            original_labels,
            term_b.get("x", 0.0),
            term_b.get("y", 0.0),
            radius=FACING_RESTORE_LABEL_RADIUS,
        )
        if label_a is None or label_b is None or int(label_a) <= 0 or int(label_a) != int(label_b):
            continue

        restore_mask = np.zeros_like(cleaned)
        p1 = (
            int(round(float(term_a.get("x", 0.0)))),
            int(round(float(term_a.get("y", 0.0)))),
        )
        p2 = (
            int(round(float(term_b.get("x", 0.0)))),
            int(round(float(term_b.get("y", 0.0)))),
        )
        cv2.line(restore_mask, p1, p2, 255, thickness=FACING_RESTORE_THICKNESS)
        cv2.circle(restore_mask, p1, FACING_RESTORE_THICKNESS // 2 + 1, 255, thickness=-1)
        cv2.circle(restore_mask, p2, FACING_RESTORE_THICKNESS // 2 + 1, 255, thickness=-1)
        restore_pixels = (restore_mask > 0) & (skeleton_binary > 0)
        cleaned[restore_pixels] = skeleton_binary[restore_pixels]

    return cleaned


def cut_connector_pin_separators(cleaned: np.ndarray, component: dict):
    terminals = component.get("terminals", [])
    h, w = cleaned.shape[:2]

    for side in ("top", "bottom"):
        side_terms = sorted(
            [term for term in terminals if term.get("relative_position") == side],
            key=lambda term: float(term.get("x", 0.0)),
        )
        for left_term, right_term in zip(side_terms, side_terms[1:]):
            x_mid = int(round((float(left_term["x"]) + float(right_term["x"])) / 2.0))
            y_anchor = int(round((float(left_term["y"]) + float(right_term["y"])) / 2.0))
            if side == "bottom":
                window = clamp_window(x_mid - 2, y_anchor - 4, x_mid + 3, y_anchor + 90, w, h)
            else:
                window = clamp_window(x_mid - 2, y_anchor - 90, x_mid + 3, y_anchor + 4, w, h)
            x1, y1, x2, y2 = window
            cleaned[y1:y2, x1:x2] = 0

    for side in ("left", "right"):
        side_terms = sorted(
            [term for term in terminals if term.get("relative_position") == side],
            key=lambda term: float(term.get("y", 0.0)),
        )
        for top_term, bottom_term in zip(side_terms, side_terms[1:]):
            y_mid = int(round((float(top_term["y"]) + float(bottom_term["y"])) / 2.0))
            x_anchor = int(round((float(top_term["x"]) + float(bottom_term["x"])) / 2.0))
            if side == "right":
                window = clamp_window(x_anchor - 4, y_mid - 2, x_anchor + 90, y_mid + 3, w, h)
            else:
                window = clamp_window(x_anchor - 90, y_mid - 2, x_anchor + 4, y_mid + 3, w, h)
            x1, y1, x2, y2 = window
            cleaned[y1:y2, x1:x2] = 0

# =========================================================
# LETTURA DELLE LABEL NELLA FINESTRA
# =========================================================
# Restituisce tutte le label positive (quindi esclude lo sfondo = 0) trovate dentro una finestra.
# Aiuta a sapere quali candidati di filo esistono vicino al terminale
def collect_labels_in_window(labels: np.ndarray, window):
    x1, y1, x2, y2 = window
    roi = labels[y1:y2, x1:x2]
    unique_labels = np.unique(roi)
    return [int(v) for v in unique_labels if int(v) > 0]

# Carica, quando disponibile, una maschera piu' spessa dello skeleton.
# Serve per distinguere un vero nodo con pallino da un semplice incrocio
# geometrico: nello skeleton entrambi sembrano croci, ma nella maschera piena
# il nodo con pallino ha molta piu' area nera locale.
def load_junction_support_binary(wire_extraction: dict):
    for key in ("filtered_path", "bridged_path", "closed_path", "binary_path"):
        path = wire_extraction.get(key)
        if not path:
            continue

        try:
            return load_binary_image(Path(path))
        except FileNotFoundError:
            continue

    return None
"""Caricamento e analisi connected-components dello skeleton dei fili."""

from pathlib import Path

import cv2
import numpy as np

from .config import COMPONENT_BODY_ERASE_EXCLUDED_CLASSES, COMPONENT_BODY_ERASE_PADDING
from .geometry import clamp_window
from .ids import normalize_class_name
from .io_utils import load_binary_image
