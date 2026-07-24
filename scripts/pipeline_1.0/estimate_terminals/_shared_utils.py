"""Piccoli helper puri condivisi dai moduli di stima dei terminali."""

import time


def clamp_bbox(bbox, image_shape):
    """Limita e ordina una bbox inclusiva rispetto ai bordi dell'immagine."""
    h, w = image_shape[:2]
    x1, y1, x2, y2 = bbox
    x1 = int(max(0, min(w - 1, round(x1))))
    y1 = int(max(0, min(h - 1, round(y1))))
    x2 = int(max(0, min(w - 1, round(x2))))
    y2 = int(max(0, min(h - 1, round(y2))))
    if x2 < x1:
        x1, x2 = x2, x1
    if y2 < y1:
        y1, y2 = y2, y1
    return [x1, y1, x2, y2]


def crop_image_bbox(image_bgr, bbox):
    """Estrae una copia della bbox inclusiva, oppure ``None`` se è vuota."""
    x1, y1, x2, y2 = bbox
    if x2 <= x1 or y2 <= y1:
        return None
    return image_bgr[y1:y2 + 1, x1:x2 + 1].copy()


def group_consecutive_indices(indices):
    """Raggruppa indici adiacenti preservando valori e ordine di input."""
    if not indices:
        return []

    groups = [[indices[0]]]
    for idx in indices[1:]:
        if idx == groups[-1][-1] + 1:
            groups[-1].append(idx)
        else:
            groups.append([idx])
    return groups


def group_close_indices(indices, max_gap=1):
    """Raggruppa indici la cui distanza non supera ``max_gap``."""
    if not indices:
        return []

    groups = [[indices[0]]]
    for idx in indices[1:]:
        if idx <= groups[-1][-1] + max_gap:
            groups[-1].append(idx)
        else:
            groups.append([idx])
    return groups


def elapsed_ms(start_time: float) -> float:
    """Converte un timestamp ``perf_counter`` in millisecondi arrotondati."""
    return round((time.perf_counter() - start_time) * 1000.0, 1)


def opposite_side(side):
    """Restituisce il lato opposto, sollevando ``KeyError`` per lati ignoti."""
    return {
        "top": "bottom",
        "bottom": "top",
        "left": "right",
        "right": "left",
    }[side]


def range_overlap_ratio(a1, a2, b1, b2):
    """Calcola l'overlap inclusivo rispetto al più corto dei due intervalli."""
    inter = max(0, min(a2, b2) - max(a1, b1) + 1)
    base = max(1, min(a2 - a1 + 1, b2 - b1 + 1))
    return float(inter) / float(base)
