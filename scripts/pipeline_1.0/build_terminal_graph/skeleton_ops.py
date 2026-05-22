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

# Decide se cancellare il corpo del componente dallo skeleton
# Cancella i componenti con 2 terminali perchè i terminali non devono risultare cortocircuitati dal corpo del simbolo
def should_erase_component_body_from_skeleton(component: dict):
    class_name = normalize_class_name(component.get("class_name"))
    terminals = component.get("terminals", [])

    if class_name in {"connector", "integrated_circuit", "npn_transistor", "pnp_transistor"}:
        return True

    if class_name in COMPONENT_BODY_ERASE_EXCLUDED_CLASSES:
        return False

    return len(terminals) == 2

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

import numpy as np

from .config import COMPONENT_BODY_ERASE_EXCLUDED_CLASSES, COMPONENT_BODY_ERASE_PADDING
from .geometry import clamp_window
from .ids import normalize_class_name
from .io_utils import load_binary_image
