import numpy as np


# Limita una finestra che si trova ai bordi dell'img
# Taglia le coordinate in modo che restano sempre dentro w e h
def clamp_window(x1, y1, x2, y2, w, h):
    return (
        max(0, min(w, int(round(x1)))),
        max(0, min(h, int(round(y1)))),
        max(0, min(w, int(round(x2)))),
        max(0, min(h, int(round(y2)))),
    )

# Costruisce una finestra direzionale coerente con il lato del terminale.
# Usa relative_position dello yaml: left, right, top e bottom. Il terminali dovrebbe cercare il filo soprattuto dal suo lato di uscita
def get_directional_window(term: dict, labels_shape, outward=16, inward=4, halfspan=5):
    h, w = labels_shape[:2]
    x = int(round(term["x"]))
    y = int(round(term["y"]))
    rel = term.get("relative_position")

    if rel == "left":
        return clamp_window(x - outward, y - halfspan, x + inward + 1, y + halfspan + 1, w, h)
    if rel == "right":
        return clamp_window(x - inward, y - halfspan, x + outward + 1, y + halfspan + 1, w, h)
    if rel == "top":
        return clamp_window(x - halfspan, y - outward, x + halfspan + 1, y + inward + 1, w, h)
    if rel == "bottom":
        return clamp_window(x - halfspan, y - inward, x + halfspan + 1, y + outward + 1, w, h)

    # Fallback molto semplice: se manca relative_position,
    # usiamo una finestra quadrata centrata sul terminale.
    return clamp_window(x - outward, y - outward, x + outward + 1, y + outward + 1, w, h)


# Costruisce una finestra quadrata centrata sul terminale
# Lo si usa se la ricerca dei terminali non trova nulla
def get_square_window(term: dict, labels_shape, radius=12):
    h, w = labels_shape[:2]
    x = int(round(term["x"]))
    y = int(round(term["y"]))
    return clamp_window(x - radius, y - radius, x + radius + 1, y + radius + 1, w, h)

# Calcola il gap orizzontale tra due bbox
# Serve per capire se due componenti sono abbastanza vicini da essere probabilmente sullo stesso filo
def horizontal_bbox_gap(bbox_a, bbox_b):
    ax1, _, ax2, _ = bbox_a
    bx1, _, bx2, _ = bbox_b

    if ax2 < bx1:
        return float(bx1 - ax2)
    if bx2 < ax1:
        return float(ax1 - bx2)
    return 0.0

#Calcola il bbox di una lable di skeleton, viene usata nelle heuristics
def label_bbox(labels: np.ndarray, label: int):
    ys, xs = np.where(labels == int(label))
    if len(xs) == 0:
        return None
    return [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]

# Calcola la distanza minima reale tra due label di skeleton
# Evita di unire pezzi di filo troppo lontani
def min_label_distance(labels: np.ndarray, label_a: int, label_b: int):
    ys_a, xs_a = np.where(labels == int(label_a))
    ys_b, xs_b = np.where(labels == int(label_b))

    if len(xs_a) == 0 or len(xs_b) == 0:
        return None

    # Le label dei fili sono piccole; questo calcolo esplicito resta semplice
    # e ci restituisce la vera distanza minima tra i due spezzoni.
    best = None
    points_a = np.column_stack((xs_a, ys_a)).astype(np.float32)
    for xb, yb in zip(xs_b, ys_b):
        d2 = (points_a[:, 0] - float(xb)) ** 2 + (points_a[:, 1] - float(yb)) ** 2
        dist = float(np.sqrt(np.min(d2)))
        if best is None or dist < best:
            best = dist

    return best
