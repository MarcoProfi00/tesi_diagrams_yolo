from pathlib import Path
import os
import json
import cv2
import numpy as np

"""
05_build_terminal_graph.py

Scopo:
    Costruire il JSON canonico del circuito a partire dallo skeleton dei fili.

Idea:
    - il passo 03 stima i terminali dei componenti
    - il passo 04 estrae i fili e salva lo skeleton
    - questo passo 05 aggancia ogni terminale al filo più vicino
      e poi collega tra loro i terminali che cadono sullo stesso filo

Output principale:
    Un solo JSON per immagine, pensato per essere letto da un'AI.
    Il JSON contiene solo le informazioni utili alla comprensione del circuito:

    - image_id
    - image_name
    - components -> lista dei componenti con terminali semantici minimali
    - graph      -> collegamenti terminale -> terminali collegati
    - warnings   -> piccole segnalazioni utili (terminali isolati / unmatched / suspicious)

Nota importante:
    Internamente usiamo ancora le connected components dello skeleton,
    ma NON salviamo net / net_id / net_index come output finale.
    Le connected components servono solo come mezzo tecnico per costruire
    il grafo finale tra terminali.

Nota sul debug:
    Le immagini di debug vengono comunque salvate su disco, ma i loro path
    NON vengono scritti nel JSON finale.
"""

# =========================================================
# PATHS / INPUT-OUTPUT
# =========================================================
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PIPELINE_DATASET = os.environ.get("PIPELINE_DATASET", "pipeline2.0/batch_v9_2_set_successivo_analog_meter_connector_transformer")

INPUT_DIR = PROJECT_ROOT / "outputs" / PIPELINE_DATASET / "04_extract_wires"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / PIPELINE_DATASET / "05_build_terminal_graph"

# Cartelle per le immagini di debug.
DEBUG_TERMINAL_OVERLAY_DIR = OUTPUT_DIR / "debug_terminal_overlay"
DEBUG_SKELETON_OVERLAY_DIR = OUTPUT_DIR / "debug_skeleton_overlay"

# =========================================================
# MATCH TERMINALE -> FILO
# =========================================================
# Finestra di ricerca principale, coerente con il lato del terminale.
TERMINAL_SEARCH_OUTWARD = 16
TERMINAL_SEARCH_INWARD = 4
TERMINAL_DIRECTIONAL_HALFSPAN = 5

# Fallback semplice: se la finestra direzionale non trova nulla,
# cerchiamo in un piccolo quadrato attorno al terminale.
TERMINAL_SQUARE_FALLBACK_RADIUS = 12

# Se il pixel etichettato trovato è troppo lontano dal terminale,
# lo marchiamo come sospetto nel debug.
MAX_REASONABLE_SNAP_DISTANCE = 24.0
ANALOG_METER_FALLBACK_RADIUS = 140
ANALOG_METER_MAX_SNAP_DISTANCE = 160.0
NON_SHORTING_MULTI_TERMINAL_CLASSES = {
    "connector",
    "transformer",
}

# =========================================================
# HEURISTICHE SPECIALI
# =========================================================
BJT_BASE_ALIGN_Y_TOL = 10
BJT_BASE_MAX_DX = 180
BJT_BASE_LABEL_MAX_GAP = 180

MOSFET_GATE_ALIGN_Y_TOL = 10
MOSFET_GATE_MAX_DX = 260
MOSFET_GATE_LABEL_MAX_GAP = 120
MOSFET_GATE_SUPPLY_ALIGN_Y_TOL = 85

OPAMP_AUX_EXTERNAL_MAX_DX = 12
OPAMP_AUX_EXTERNAL_MAX_DY = 180
HORIZONTAL_STUB_LABEL_MAX_GAP = 70
HORIZONTAL_STUB_LABEL_Y_TOL = 24
HORIZONTAL_STUB_SOURCE_CLASSES = {
    "diode",
    "led",
}
INDUCTOR_PARALLEL_BRANCH_MAX_LABEL_DISTANCE = 34.0
INDUCTOR_PARALLEL_BRANCH_MAX_TERMINAL_DISTANCE = 220.0

SUPPLY_ARROW_SOURCE_CLASSES = {
    "battery",
    "current_source",
    "voltage_source",
}
SUPPLY_ARROW_EXCLUDED_CLASSES = {
    "breaker",
    "terminal",
    "gnd",
    "ground",
}
SUPPLY_ARROW_MIN_STUB_HEIGHT = 20
SUPPLY_ARROW_MAX_STUB_WIDTH = 34
SUPPLY_ARROW_X_TOL = 10
SUPPLY_ARROW_Y_GAP = 12
SUPPLY_ARROW_TOP_BORDER_RATIO = 0.22
SUPPLY_ARROW_BOTTOM_BORDER_RATIO = 0.78

COMPONENT_BODY_ERASE_PADDING = 3
COMPONENT_BODY_ERASE_EXCLUDED_CLASSES = {
    "terminal",
    "gnd",
    "ground",
}

BRIDGE_MIN_RUN = 25
BRIDGE_MIN_PIXELS_PER_DIRECTION = 6
BRIDGE_HUMP_Y_MIN = 2
BRIDGE_HUMP_Y_MAX = 8
BRIDGE_HUMP_X_MIN = 3
BRIDGE_HUMP_X_MAX = 14
BRIDGE_CUT_HALF_WIDTH = 6
BRIDGE_CUT_HALF_HEIGHT = 8
BRIDGE_PROBE_DISTANCE = 18

PLAIN_CROSSING_MIN_RUN = 25
PLAIN_CROSSING_MIN_PIXELS_PER_DIRECTION = 6
PLAIN_CROSSING_DOT_RADIUS = 8
PLAIN_CROSSING_DOT_AREA_MIN = 210
PLAIN_CROSSING_CUT_HALF_WIDTH = 4
PLAIN_CROSSING_CUT_HALF_HEIGHT = 4
PLAIN_CROSSING_PROBE_DISTANCE = 18

# =========================================================
# DEBUG VISIVO
# =========================================================
SAVE_DEBUG_IMAGES = True
TEXT_FONT_SCALE = 0.42
TEXT_THICKNESS = 1
TEXT_OUTLINE_THICKNESS = 3
TERMINAL_RADIUS = 4
SNAP_RADIUS = 3

MATCHED_TERMINAL_COLOR = (0, 180, 0)      # verde
UNMATCHED_TERMINAL_COLOR = (0, 0, 255)    # rosso
SUSPICIOUS_TERMINAL_COLOR = (0, 165, 255) # arancione
SNAP_POINT_COLOR = (255, 0, 0)            # blu
LINK_COLOR = (255, 0, 255)                # magenta
TEXT_COLOR = (255, 255, 0)                # giallo
TEXT_OUTLINE_COLOR = (0, 0, 0)            # nero



# =========================================================
# UTILITY BASE
# =========================================================
# Carica una immagine binaria da disco.
def load_binary_image(path: Path) -> np.ndarray:
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Immagine non trovata o non leggibile: {path}")

    # Normalizziamo a 0/255 per evitare ambiguità.
    return np.where(img > 0, 255, 0).astype(np.uint8)


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

def should_erase_component_body_from_skeleton(component: dict):
    class_name = normalize_class_name(component.get("class_name"))
    terminals = component.get("terminals", [])

    if class_name in COMPONENT_BODY_ERASE_EXCLUDED_CLASSES:
        return False

    return len(terminals) == 2


def erase_component_bodies_from_skeleton(
    skeleton_binary: np.ndarray,
    components: list[dict],
):
    cleaned = skeleton_binary.copy()
    h, w = cleaned.shape[:2]

    for component in components:
        if not should_erase_component_body_from_skeleton(component):
            continue

        bbox = component.get("bbox")
        if not bbox or len(bbox) != 4:
            continue

        x1, y1, x2, y2 = map(float, bbox)
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

    return cleaned


# Clamp di una finestra dentro i limiti immagine.
def clamp_window(x1, y1, x2, y2, w, h):
    return (
        max(0, min(w, int(round(x1)))),
        max(0, min(h, int(round(y1)))),
        max(0, min(w, int(round(x2)))),
        max(0, min(h, int(round(y2)))),
    )


# Disegna testo con contorno, utile per rendere leggibili le etichette.
def draw_outlined_text(
    image,
    text,
    origin,
    color=TEXT_COLOR,
    outline_color=TEXT_OUTLINE_COLOR,
    font_scale=TEXT_FONT_SCALE,
    thickness=TEXT_THICKNESS,
    outline_thickness=TEXT_OUTLINE_THICKNESS,
):
    cv2.putText(
        image,
        text,
        origin,
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        outline_color,
        outline_thickness,
        cv2.LINE_AA,
    )
    cv2.putText(
        image,
        text,
        origin,
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        color,
        thickness,
        cv2.LINE_AA,
    )


# Normalizza il nome classe per usarlo in una chiave semplice.
def normalize_class_name(class_name: str) -> str:
    class_name = str(class_name or "component").strip().lower()
    class_name = class_name.replace(" ", "_")
    return class_name


# Costruisce un id di componente leggibile, ad esempio:
#   Mosfet + 16.2 -> mosfet16.2
def make_simple_component_id(instance_id: str, class_name: str) -> str:
    return f"{normalize_class_name(class_name)}{instance_id}"


# Normalizza un id pubblico per usarlo come chiave semplice.
# Esempio:
#   16.2:G -> 16.2_G
# Manteniamo le MAIUSCOLE del terminale per non perdere G/S/D, B/C/E.
def normalize_public_terminal_id(value: str) -> str:
    value = str(value or "").strip()
    value = value.replace(":", "_")
    value = value.replace(" ", "")
    return value


# Restituisce l'id pubblico migliore del terminale, riusando quanto creato nel 03.
def get_preferred_terminal_public_id(term: dict) -> str:
    return (
        term.get("display_terminal_id")
        or term.get("semantic_terminal_id")
        or term.get("terminal_id")
        or f"{term.get('instance_id', 'unknown')}:{term.get('name', 't')}"
    )


# Restituisce il nome corto migliore del terminale, riusando quanto creato nel 03.
def get_preferred_terminal_public_name(term: dict) -> str:
    return (
        term.get("display_name")
        or term.get("semantic_terminal_name")
        or term.get("name")
        or "t"
    )


# Costruisce la chiave umana semplice del terminale.
# Esempi:
#   display_terminal_id = 16.2:G        -> mosfet16.2_G
#   display_terminal_id = 2.1:positive -> battery2.1_positive
#   display_terminal_id assente         -> resistor22.1_t1
def make_simple_terminal_key(term: dict) -> str:
    class_name = normalize_class_name(term.get("component_class_name"))
    public_terminal_id = normalize_public_terminal_id(
        get_preferred_terminal_public_id(term)
    )
    return f"{class_name}{public_terminal_id}"


# =========================================================
# GEOMETRIA DI RICERCA ATTORNO AL TERMINALE
# =========================================================
# Costruisce una finestra direzionale coerente con il lato del terminale.
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


# Finestra quadrata di fallback.
def get_square_window(term: dict, labels_shape, radius=12):
    h, w = labels_shape[:2]
    x = int(round(term["x"]))
    y = int(round(term["y"]))
    return clamp_window(x - radius, y - radius, x + radius + 1, y + radius + 1, w, h)


# =========================================================
# LETTURA DELLE LABEL NELLA FINESTRA
# =========================================================
# Restituisce tutte le label positive (quindi esclude lo sfondo = 0)
# trovate dentro una finestra.
def collect_labels_in_window(labels: np.ndarray, window):
    x1, y1, x2, y2 = window
    roi = labels[y1:y2, x1:x2]
    unique_labels = np.unique(roi)
    return [int(v) for v in unique_labels if int(v) > 0]


# Trova il pixel etichettato più vicino al terminale dentro una finestra.
def find_nearest_labeled_pixel(labels: np.ndarray, term: dict, window):
    x1, y1, x2, y2 = window
    roi = labels[y1:y2, x1:x2]

    ys, xs = np.where(roi > 0)
    if len(xs) == 0:
        return None

    abs_xs = xs + x1
    abs_ys = ys + y1

    tx = float(term["x"])
    ty = float(term["y"])

    d2 = (abs_xs - tx) ** 2 + (abs_ys - ty) ** 2
    best_idx = int(np.argmin(d2))

    px = int(abs_xs[best_idx])
    py = int(abs_ys[best_idx])
    lbl = int(labels[py, px])
    dist = float(np.sqrt(d2[best_idx]))

    return {
        "label": lbl,
        "snap_point": [px, py],
        "snap_distance": round(dist, 3),
    }


# =========================================================
# MATCH DI UN SINGOLO TERMINALE
# =========================================================
# Versione volutamente semplice:
# 1. prova finestra direzionale
# 2. se non trova nulla, prova finestra quadrata
# 3. se ancora nulla, terminale unmatched

def match_terminal_to_skeleton_label(labels: np.ndarray, term: dict):
    # Primo tentativo: finestra direzionale
    dir_window = get_directional_window(
        term,
        labels.shape,
        outward=TERMINAL_SEARCH_OUTWARD,
        inward=TERMINAL_SEARCH_INWARD,
        halfspan=TERMINAL_DIRECTIONAL_HALFSPAN,
    )
    dir_labels = collect_labels_in_window(labels, dir_window)
    nearest = find_nearest_labeled_pixel(labels, term, dir_window)

    if nearest is not None:
        return {
            "terminal_id": term["terminal_id"],
            "candidate_labels": dir_labels,
            "matched_label": int(nearest["label"]),
            "match_mode": "directional",
            "search_window": [int(v) for v in dir_window],
            "snap_point": nearest["snap_point"],
            "snap_distance": nearest["snap_distance"],
            "is_suspicious": float(nearest["snap_distance"]) > float(MAX_REASONABLE_SNAP_DISTANCE),
        }

    # Secondo tentativo: piccolo quadrato attorno al terminale
    sq_window = get_square_window(term, labels.shape, radius=TERMINAL_SQUARE_FALLBACK_RADIUS)
    sq_labels = collect_labels_in_window(labels, sq_window)
    nearest = find_nearest_labeled_pixel(labels, term, sq_window)

    if nearest is not None:
        return {
            "terminal_id": term["terminal_id"],
            "candidate_labels": sq_labels,
            "matched_label": int(nearest["label"]),
            "match_mode": "square_fallback",
            "search_window": [int(v) for v in sq_window],
            "snap_point": nearest["snap_point"],
            "snap_distance": nearest["snap_distance"],
            "is_suspicious": float(nearest["snap_distance"]) > float(MAX_REASONABLE_SNAP_DISTANCE),
        }

    # Nessun match trovato.
    return {
        "terminal_id": term["terminal_id"],
        "candidate_labels": [],
        "matched_label": None,
        "match_mode": "unmatched",
        "search_window": None,
        "snap_point": None,
        "snap_distance": None,
        "is_suspicious": True,
    }


def attach_unmatched_analog_meter_terminals(
    components: list[dict],
    terminal_match_debug: dict,
    labels: np.ndarray,
):
    """Fallback mirato per i post dell'analog meter, che spesso sono dentro il simbolo."""
    for component in components:
        if normalize_class_name(component.get("class_name")) != "analog_meter":
            continue

        for term in component.get("terminals", []):
            terminal_id = term.get("terminal_id")
            if terminal_id is None:
                continue

            current_match = terminal_match_debug.get(terminal_id, {})
            if current_match.get("matched_label") is not None:
                continue

            sq_window = get_square_window(
                term,
                labels.shape,
                radius=ANALOG_METER_FALLBACK_RADIUS,
            )
            sq_labels = collect_labels_in_window(labels, sq_window)
            nearest = find_nearest_labeled_pixel(labels, term, sq_window)

            if nearest is None:
                continue
            if float(nearest["snap_distance"]) > ANALOG_METER_MAX_SNAP_DISTANCE:
                continue

            terminal_match_debug[terminal_id] = {
                "terminal_id": terminal_id,
                "candidate_labels": sq_labels,
                "matched_label": int(nearest["label"]),
                "match_mode": "analog_meter_wide_fallback",
                "search_window": [int(v) for v in sq_window],
                "snap_point": nearest["snap_point"],
                "snap_distance": nearest["snap_distance"],
                "is_suspicious": False,
            }


# =========================================================
# COSTRUZIONE DEI GRUPPI INTERNI DI FILO
# =========================================================
# Trasforma il debug terminale -> label in una struttura:
#   label -> [terminal_id, terminal_id, ...]
# Questa struttura serve solo internamente.
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


# =========================================================
# FUSIONE LABEL SPEZZATE DA SIMBOLI BJT
# =========================================================
# In alcuni schemi il filo della base passa visivamente attraverso/accanto
# al simbolo del transistor, ma il passo 04 spezza lo skeleton perche'
# maschera il componente. Qui fondiamo solo casi molto conservativi:
# terminali B di BJT, quasi alla stessa y, con bbox vicine e label vicine.

def is_bjt_base_terminal(term: dict) -> bool:
    class_name = normalize_class_name(term.get("component_class_name"))
    terminal_name = str(get_preferred_terminal_public_name(term) or "").strip().upper()
    return "transistor" in class_name and terminal_name == "B"


def build_component_bbox_by_instance(components: list[dict]):
    bbox_by_instance = {}
    for comp in components:
        instance_id = comp.get("instance_id")
        bbox = comp.get("bbox")
        if instance_id is None or not bbox or len(bbox) != 4:
            continue
        bbox_by_instance[str(instance_id)] = [float(v) for v in bbox]
    return bbox_by_instance


def horizontal_bbox_gap(bbox_a, bbox_b):
    ax1, _, ax2, _ = bbox_a
    bx1, _, bx2, _ = bbox_b

    if ax2 < bx1:
        return float(bx1 - ax2)
    if bx2 < ax1:
        return float(ax1 - bx2)
    return 0.0


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


def merge_bjt_base_aligned_labels(
    label_to_terminal_ids: dict,
    terminals: list[dict],
    components: list[dict],
    terminal_match_debug: dict,
    labels: np.ndarray,
):
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
    base_terms = [term for term in terminals if is_bjt_base_terminal(term)]

    for i, term_a in enumerate(base_terms):
        info_a = terminal_match_debug.get(term_a["terminal_id"], {})
        label_a = info_a.get("matched_label")
        if label_a is None:
            continue

        bbox_a = bbox_by_instance.get(str(term_a.get("instance_id")))
        if bbox_a is None:
            continue

        for term_b in base_terms[i + 1:]:
            info_b = terminal_match_debug.get(term_b["terminal_id"], {})
            label_b = info_b.get("matched_label")
            if label_b is None or int(label_a) == int(label_b):
                continue

            bbox_b = bbox_by_instance.get(str(term_b.get("instance_id")))
            if bbox_b is None:
                continue

            if abs(float(term_a["y"]) - float(term_b["y"])) > BJT_BASE_ALIGN_Y_TOL:
                continue

            if horizontal_bbox_gap(bbox_a, bbox_b) > BJT_BASE_MAX_DX:
                continue

            label_gap = min_label_distance(labels, int(label_a), int(label_b))
            if label_gap is None or label_gap > BJT_BASE_LABEL_MAX_GAP:
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


# =========================================================
# FUSIONE LABEL SPEZZATE TRA GATE MOSFET
# =========================================================
# Nei mirror e negli stadi differenziali le gate dei MOSFET possono essere
# unite da un filo orizzontale che passa vicino ai simboli. Se il passo 04
# spezza quel filo in due tronconi, fondiamo solo coppie di gate MOSFET
# quasi allineate, con componenti vicini e spezzoni di skeleton vicini.

def is_mosfet_gate_terminal(term: dict) -> bool:
    class_name = normalize_class_name(term.get("component_class_name"))
    terminal_name = str(get_preferred_terminal_public_name(term) or "").strip().upper()
    return "mosfet" in class_name and terminal_name == "G"


def is_mosfet_terminal(term: dict) -> bool:
    class_name = normalize_class_name(term.get("component_class_name"))
    return "mosfet" in class_name


def is_battery_terminal(term: dict) -> bool:
    class_name = normalize_class_name(term.get("component_class_name"))
    return class_name == "battery"


def merge_mosfet_gate_aligned_labels(
    label_to_terminal_ids: dict,
    terminals: list[dict],
    components: list[dict],
    terminal_match_debug: dict,
    labels: np.ndarray,
):
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


def attach_unmatched_opamp_aux_to_external_terminals(
    terminals: list[dict],
    terminal_match_debug: dict,
):
    terminal_candidates = [
        term
        for term in terminals
        if is_external_terminal_component(term)
        and terminal_match_debug.get(term["terminal_id"], {}).get("matched_label") is not None
    ]

    for aux_term in terminals:
        aux_id = aux_term["terminal_id"]
        aux_match = terminal_match_debug.get(aux_id, {})

        if aux_match.get("matched_label") is not None:
            continue

        if not is_opamp_aux_terminal(aux_term):
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

            candidate_match = terminal_match_debug.get(candidate["terminal_id"], {})
            candidates.append({
                "term": candidate,
                "match": candidate_match,
                "dx": dx,
                "dy": dy,
            })

        if not candidates:
            continue

        best = min(candidates, key=lambda item: (item["dx"], item["dy"]))
        best_term = best["term"]
        best_match = best["match"]
        snap_point = best_match.get("snap_point")

        terminal_match_debug[aux_id] = {
            "terminal_id": aux_id,
            "candidate_labels": [int(best_match["matched_label"])],
            "matched_label": int(best_match["matched_label"]),
            "match_mode": "opamp_aux_external_terminal_virtual",
            "search_window": None,
            "snap_point": snap_point,
            "snap_distance": round(float(best["dy"]), 3),
            "is_suspicious": False,
            "virtual_match": True,
            "virtual_match_reason": "unmatched_opamp_aux_aligned_to_external_terminal",
            "external_terminal_id": best_term["terminal_id"],
            "external_terminal_point": [
                round(float(best_term["x"]), 3),
                round(float(best_term["y"]), 3),
            ],
            "axis_delta": [
                round(float(best["dx"]), 3),
                round(float(best["dy"]), 3),
            ],
        }


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


def merge_near_horizontal_stub_labels(
    label_to_terminal_ids: dict,
    terminals: list[dict],
    terminal_match_debug: dict,
    labels: np.ndarray,
):
    terminal_by_id = {term["terminal_id"]: term for term in terminals}
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

    boxes = {
        int(label): label_bbox(labels, int(label))
        for label in label_to_terminal_ids.keys()
    }

    for source_label, terminal_ids in label_to_terminal_ids.items():
        source_label = int(source_label)
        unique_ids = sorted(set(terminal_ids))
        if len(unique_ids) != 1:
            continue

        terminal_id = unique_ids[0]
        term = terminal_by_id.get(terminal_id)
        if term is None:
            continue

        class_name = normalize_class_name(term.get("component_class_name"))
        if class_name not in HORIZONTAL_STUB_SOURCE_CLASSES:
            continue

        relative_position = str(term.get("relative_position") or "").lower()
        if relative_position not in {"left", "right"}:
            continue

        source_box = boxes.get(source_label)
        if source_box is None:
            continue

        tx = float(term.get("x"))
        ty = float(term.get("y"))
        best = None

        for target_label, target_ids in label_to_terminal_ids.items():
            target_label = int(target_label)
            if target_label == source_label:
                continue

            target_box = boxes.get(target_label)
            if target_box is None:
                continue

            sx1, sy1, sx2, sy2 = source_box
            tx1, ty1, tx2, ty2 = target_box
            if relative_position == "right":
                gap = float(tx1 - sx2)
                direction_ok = tx1 >= sx2
            else:
                gap = float(sx1 - tx2)
                direction_ok = tx2 <= sx1

            if not direction_ok or gap < 0 or gap > HORIZONTAL_STUB_LABEL_MAX_GAP:
                continue

            if ty < ty1:
                y_gap = float(ty1) - ty
            elif ty > ty2:
                y_gap = ty - float(ty2)
            else:
                y_gap = 0.0

            if y_gap > HORIZONTAL_STUB_LABEL_Y_TOL:
                continue

            score = (gap, y_gap, len(set(target_ids)))
            if best is None or score < best[0]:
                best = (score, target_label)

        if best is not None:
            union(source_label, best[1])

    merged = {}
    for label, terminal_ids in label_to_terminal_ids.items():
        root = find(int(label))
        merged.setdefault(root, []).extend(terminal_ids)

    return {
        int(label): sorted(set(terminal_ids))
        for label, terminal_ids in merged.items()
    }


def merge_vertical_inductor_parallel_branch_labels(
    label_to_terminal_ids: dict,
    terminals: list[dict],
    terminal_match_debug: dict,
    labels: np.ndarray,
):
    terminal_by_id = {term["terminal_id"]: term for term in terminals}
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

    def terms_for_label(label):
        return [
            terminal_by_id[terminal_id]
            for terminal_id in label_to_terminal_ids.get(int(label), [])
            if terminal_id in terminal_by_id
        ]

    def is_inductor_vertical_terminal(term):
        class_name = normalize_class_name(term.get("component_class_name"))
        relative_position = str(term.get("relative_position") or "").lower()
        return class_name == "inductor" and relative_position in {"top", "bottom"}

    def is_matching_parallel_target(inductor_term, target_terms):
        relative_position = str(inductor_term.get("relative_position") or "").lower()
        for target_term in target_terms:
            class_name = normalize_class_name(target_term.get("component_class_name"))
            public_name = str(get_preferred_terminal_public_name(target_term) or "").lower()
            polarity = str(target_term.get("semantic_polarity") or "").lower()

            if relative_position == "top":
                if class_name == "antenna":
                    return True
                if "capacitor" in class_name and (public_name == "positive" or polarity == "positive"):
                    return True

            if relative_position == "bottom":
                if class_name in {"gnd", "ground"}:
                    return True
                if "capacitor" in class_name and (public_name == "negative" or polarity == "negative"):
                    return True

        return False

    inductor_items = []
    for terminal_id, info in terminal_match_debug.items():
        label = info.get("matched_label")
        if label is None:
            continue
        term = terminal_by_id.get(terminal_id)
        if term is None or not is_inductor_vertical_terminal(term):
            continue
        inductor_items.append((term, int(label)))

    for inductor_term, inductor_label in inductor_items:
        for target_label in label_to_terminal_ids:
            target_label = int(target_label)
            if target_label == inductor_label:
                continue

            target_terms = terms_for_label(target_label)
            if not target_terms:
                continue
            if not is_matching_parallel_target(inductor_term, target_terms):
                continue

            distance = min_label_distance(labels, inductor_label, target_label)
            if distance is None or distance > INDUCTOR_PARALLEL_BRANCH_MAX_LABEL_DISTANCE:
                continue

            union(inductor_label, target_label)

    merged = {}
    for label, terminal_ids in label_to_terminal_ids.items():
        root = find(int(label))
        merged.setdefault(root, []).extend(terminal_ids)

    return {
        int(label): sorted(set(terminal_ids))
        for label, terminal_ids in merged.items()
    }


def build_vertical_inductor_parallel_direct_edges(
    terminals: list[dict],
    terminal_match_debug: dict,
    labels: np.ndarray,
):
    edges = []

    def is_vertical_inductor_terminal(term):
        class_name = normalize_class_name(term.get("component_class_name"))
        relative_position = str(term.get("relative_position") or "").lower()
        return class_name == "inductor" and relative_position in {"top", "bottom"}

    def is_target_for_inductor_side(inductor_term, target_term):
        relative_position = str(inductor_term.get("relative_position") or "").lower()
        class_name = normalize_class_name(target_term.get("component_class_name"))
        public_name = str(get_preferred_terminal_public_name(target_term) or "").lower()
        polarity = str(target_term.get("semantic_polarity") or "").lower()

        if relative_position == "top":
            if class_name == "antenna":
                return True
            return "capacitor" in class_name and (public_name == "positive" or polarity == "positive")

        if relative_position == "bottom":
            if class_name in {"gnd", "ground"}:
                return True
            return "capacitor" in class_name and (public_name == "negative" or polarity == "negative")

        return False

    def terminal_distance(term_a, term_b):
        ax = float(term_a.get("x", 0.0))
        ay = float(term_a.get("y", 0.0))
        bx = float(term_b.get("x", 0.0))
        by = float(term_b.get("y", 0.0))
        return float(np.hypot(ax - bx, ay - by))

    inductor_terms = [term for term in terminals if is_vertical_inductor_terminal(term)]

    for inductor_term in inductor_terms:
        inductor_id = inductor_term["terminal_id"]
        inductor_label = terminal_match_debug.get(inductor_id, {}).get("matched_label")
        if inductor_label is None:
            continue

        for target_term in terminals:
            target_id = target_term["terminal_id"]
            if target_id == inductor_id:
                continue
            if not is_target_for_inductor_side(inductor_term, target_term):
                continue

            target_label = terminal_match_debug.get(target_id, {}).get("matched_label")
            if target_label is None:
                continue

            distance = min_label_distance(labels, int(inductor_label), int(target_label))
            if distance is None or distance > INDUCTOR_PARALLEL_BRANCH_MAX_LABEL_DISTANCE:
                continue
            target_class = normalize_class_name(target_term.get("component_class_name"))
            if (
                target_class != "antenna"
                and terminal_distance(inductor_term, target_term) > INDUCTOR_PARALLEL_BRANCH_MAX_TERMINAL_DISTANCE
            ):
                continue

            edges.append(tuple(sorted((inductor_id, target_id))))

    return sorted(set(edges))


def merge_battery_gate_rail_groups(
    label_to_terminal_ids: dict,
    terminals: list[dict],
):
    terminal_by_id = {term["terminal_id"]: term for term in terminals}

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

    def is_battery_only_group(label):
        known_terms = known_terms_for_label(label)
        return bool(known_terms) and all(is_battery_terminal(term) for term in known_terms)

    def is_gate_only_group(label):
        known_terms = known_terms_for_label(label)
        return bool(known_terms) and all(is_mosfet_gate_terminal(term) for term in known_terms)

    battery_groups = [
        (label, known_terms_for_label(label))
        for label in label_to_terminal_ids
        if is_battery_only_group(label)
    ]
    gate_groups = [
        (label, known_terms_for_label(label))
        for label in label_to_terminal_ids
        if is_gate_only_group(label)
    ]

    for battery_label, battery_terms in battery_groups:
        for battery_term in battery_terms:
            battery_y = float(battery_term["y"])

            for gate_label, gate_terms in gate_groups:
                gate_y_values = [float(term["y"]) for term in gate_terms]
                if not gate_y_values:
                    continue

                nearest_gate_dy = min(abs(gate_y - battery_y) for gate_y in gate_y_values)
                if nearest_gate_dy > MOSFET_GATE_SUPPLY_ALIGN_Y_TOL:
                    continue

                union(int(battery_label), int(gate_label))

    merged = {}
    for label, terminal_ids in label_to_terminal_ids.items():
        root = find(int(label))
        merged.setdefault(root, []).extend(terminal_ids)

    return {
        int(label): sorted(set(terminal_ids))
        for label, terminal_ids in merged.items()
    }


def merge_mosfet_gate_rail_groups(
    label_to_terminal_ids: dict,
    terminals: list[dict],
    components: list[dict],
):
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


# =========================================================
# SPLIT LABEL IN CORRISPONDENZA DEI PONTI
# =========================================================
# Nei disegni circuitali un ponticello indica un incrocio senza giunzione.
# Lo skeleton, pero', puo' trasformarlo in una croce connessa. Rileviamo
# la gobba sopra l'incrocio e separiamo la label in due reti: verticale e
# orizzontale.

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
    crossing_source = junction_binary if junction_binary is not None else skeleton_binary
    binary = np.where(crossing_source > 0, 1, 0).astype(np.uint8)
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

            left = int(np.sum(binary[y, x - run:x]))
            right = int(np.sum(binary[y, x + 1:x + run + 1]))
            up = int(np.sum(binary[y - run:y, x]))
            down = int(np.sum(binary[y + 1:y + run + 1, x]))

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

    plain_crossing_labels = {int(crossing["label"]) for crossing in plain_crossings}
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

        plain_touched_split = original_label in plain_crossing_labels
        creates_singleton = any(len(set(group)) < 2 for group in related_groups)

        if plain_touched_split and creates_singleton:
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
# COSTRUZIONE DEL GRAFO FINALE TRA TERMINALI
# =========================================================
# Per ogni gruppo di filo:
# - se il gruppo contiene almeno 2 terminali
# - allora ogni terminale è collegato a tutti gli altri terminali del gruppo

def build_terminal_graph(terminals, label_to_terminal_ids: dict):
    graph = {term["terminal_id"]: [] for term in terminals}

    for _, terminal_ids in label_to_terminal_ids.items():
        unique_ids = sorted(set(terminal_ids))
        if len(unique_ids) < 2:
            continue

        for source_id in unique_ids:
            others = [target_id for target_id in unique_ids if target_id != source_id]
            graph[source_id].extend(others)

    for terminal_id in graph:
        graph[terminal_id] = sorted(set(graph[terminal_id]))

    return graph


def label_bbox(labels: np.ndarray, label: int):
    ys, xs = np.where(labels == int(label))
    if len(xs) == 0:
        return None
    return [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]


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


# Costruisce la mappa original_id -> simple_id.
def build_simple_id_map(terminals: list[dict]):
    original_to_simple = {}
    for term in terminals:
        original_to_simple[term["terminal_id"]] = make_simple_terminal_key(term)
    return original_to_simple


# Converte il grafo interno in un dizionario semplice e leggibile.
def build_simple_terminal_graph(terminal_graph: dict, original_to_simple: dict):
    public_graph = {}

    for original_source_id, original_target_ids in terminal_graph.items():
        public_source_id = original_to_simple.get(original_source_id, original_source_id)
        public_target_ids = [original_to_simple.get(target_id, target_id) for target_id in original_target_ids]
        public_graph[public_source_id] = sorted(set(public_target_ids))

    public_graph = {key: public_graph[key] for key in sorted(public_graph.keys())}
    return public_graph


# Converte una lista di id interni in una lista di id semplici.
def build_simple_list(values: list[str], original_to_simple: dict):
    return sorted([original_to_simple.get(v, v) for v in values])


def infer_supply_arrow_connection_for_terminal(
    term: dict,
    label_box: list[int],
    image_height: int | None,
):
    class_name = normalize_class_name(term.get("component_class_name"))
    if class_name in SUPPLY_ARROW_EXCLUDED_CLASSES:
        return None

    x1, y1, x2, y2 = map(float, label_box)
    tx = float(term.get("x"))
    ty = float(term.get("y"))
    width = max(0.0, x2 - x1)
    height = max(0.0, y2 - y1)

    if height < SUPPLY_ARROW_MIN_STUB_HEIGHT:
        return None
    if width > max(float(SUPPLY_ARROW_MAX_STUB_WIDTH), height * 0.75):
        return None
    if tx < x1 - SUPPLY_ARROW_X_TOL or tx > x2 + SUPPLY_ARROW_X_TOL:
        return None

    relative_position = str(term.get("relative_position") or "").strip().lower()
    needs_border_evidence = class_name not in SUPPLY_ARROW_SOURCE_CLASSES
    top_border_limit = image_height * SUPPLY_ARROW_TOP_BORDER_RATIO if image_height else None
    bottom_border_limit = image_height * SUPPLY_ARROW_BOTTOM_BORDER_RATIO if image_height else None
    confidence = 0.86 if class_name in SUPPLY_ARROW_SOURCE_CLASSES else 0.78

    if relative_position == "top" and y1 < ty - SUPPLY_ARROW_Y_GAP:
        if needs_border_evidence and top_border_limit is not None and y1 > top_border_limit:
            return None
        return {
            "type": "supply_arrow",
            "label": "VDD",
            "direction": "up",
            "polarity": "positive_supply",
            "confidence": confidence,
            "evidence_type": "geometry_heuristic",
            "reason": "single_terminal_vertical_stub_to_up_supply_arrow",
        }

    if relative_position == "bottom" and y2 > ty + SUPPLY_ARROW_Y_GAP:
        if needs_border_evidence and bottom_border_limit is not None and y2 < bottom_border_limit:
            return None
        return {
            "type": "supply_arrow",
            "label": "VSS",
            "direction": "down",
            "polarity": "negative_supply",
            "confidence": confidence,
            "evidence_type": "geometry_heuristic",
            "reason": "single_terminal_vertical_stub_to_down_supply_arrow",
        }

    return None


def build_supply_graph_links(
    terminals: list[dict],
    label_to_terminal_ids: dict,
    terminal_match_debug: dict,
    labels: np.ndarray,
    image_height: int | None,
    original_to_simple: dict,
):
    terminal_by_id = {term["terminal_id"]: term for term in terminals}
    supply_links = {}

    for terminal_ids in label_to_terminal_ids.values():
        unique_terminal_ids = sorted(set(terminal_ids))
        if len(unique_terminal_ids) != 1:
            continue

        terminal_id = unique_terminal_ids[0]
        term = terminal_by_id.get(terminal_id)
        if term is None:
            continue

        matched_label = terminal_match_debug.get(terminal_id, {}).get("matched_label")
        if matched_label is None:
            continue

        bbox = label_bbox(labels, int(matched_label))
        if bbox is None:
            continue

        connection = infer_supply_arrow_connection_for_terminal(term, bbox, image_height)
        if connection is None:
            continue

        simple_terminal_id = original_to_simple.get(terminal_id, terminal_id)
        supply_links.setdefault(simple_terminal_id, set()).add(connection["label"])

    return {
        terminal_id: sorted(labels)
        for terminal_id, labels in supply_links.items()
    }


# =========================================================
# COSTRUZIONE DEI COMPONENTI CANONICI
# =========================================================
# Produce una vista semplificata dei componenti.
# Nel JSON finale teniamo solo:
# - component_id
# - instance_id
# - class_name
# - terminals con terminal_id, name e relative_position
# NIENTE bbox, coordinate o altri dettagli geometrici.
def build_canonical_components(components: list[dict]):
    canonical_components = []

    for comp in components:
        class_name = comp.get("class_name")
        instance_id = comp.get("instance_id")

        canonical_terminals = []
        for term in comp.get("terminals", []):
            canonical_terminals.append({
                "terminal_id": make_simple_terminal_key(term),
                "name": get_preferred_terminal_public_name(term),
                "relative_position": term.get("relative_position"),
            })

        canonical_component = {
            "component_id": make_simple_component_id(instance_id, class_name),
            "instance_id": instance_id,
            "class_name": class_name,
            "terminals": canonical_terminals,
        }

        if comp.get("state") is not None:
            canonical_component["state"] = comp.get("state")
            canonical_component["state_confidence"] = comp.get("state_confidence")

        canonical_components.append(canonical_component)

    return canonical_components



# =========================================================
# DEBUG VISIVO
# =========================================================
# Sceglie il colore del terminale in base allo stato del match.
def get_terminal_debug_color(match_info: dict):
    if match_info.get("matched_label") is None:
        return UNMATCHED_TERMINAL_COLOR
    if match_info.get("is_suspicious", False):
        return SUSPICIOUS_TERMINAL_COLOR
    return MATCHED_TERMINAL_COLOR


# Disegna overlay sul diagramma originale.
def draw_terminal_overlay(image_bgr, terminals, terminal_match_debug, original_to_simple):
    out = image_bgr.copy()

    for term in terminals:
        terminal_id = term["terminal_id"]
        simple_id = original_to_simple.get(terminal_id, terminal_id)
        info = terminal_match_debug.get(terminal_id, {})

        tx = int(round(term["x"]))
        ty = int(round(term["y"]))
        color = get_terminal_debug_color(info)

        cv2.circle(out, (tx, ty), TERMINAL_RADIUS, color, -1)
        cv2.circle(out, (tx, ty), TERMINAL_RADIUS + 1, (0, 0, 0), 1)

        snap_point = info.get("snap_point")
        if snap_point is not None:
            sx, sy = map(int, snap_point)
            cv2.circle(out, (sx, sy), SNAP_RADIUS, SNAP_POINT_COLOR, -1)
            cv2.circle(out, (sx, sy), SNAP_RADIUS + 1, (255, 255, 255), 1)
            cv2.line(out, (tx, ty), (sx, sy), LINK_COLOR, 1)

        label_text = simple_id
        if info.get("matched_label") is None:
            label_text += " [none]"
        elif info.get("is_suspicious", False):
            label_text += f" [d={info.get('snap_distance')}]"

        draw_outlined_text(out, label_text, (tx + 8, max(16, ty - 6)))

    return out


# Disegna overlay sullo skeleton, utile per capire se il match cade davvero sul filo.
def draw_skeleton_overlay(skeleton_binary, terminals, terminal_match_debug, original_to_simple):
    out = cv2.cvtColor(skeleton_binary, cv2.COLOR_GRAY2BGR)

    for term in terminals:
        terminal_id = term["terminal_id"]
        simple_id = original_to_simple.get(terminal_id, terminal_id)
        info = terminal_match_debug.get(terminal_id, {})

        tx = int(round(term["x"]))
        ty = int(round(term["y"]))
        color = get_terminal_debug_color(info)

        cv2.circle(out, (tx, ty), TERMINAL_RADIUS, color, -1)
        cv2.circle(out, (tx, ty), TERMINAL_RADIUS + 1, (255, 255, 255), 1)

        snap_point = info.get("snap_point")
        if snap_point is not None:
            sx, sy = map(int, snap_point)
            cv2.circle(out, (sx, sy), SNAP_RADIUS, SNAP_POINT_COLOR, -1)
            cv2.circle(out, (sx, sy), SNAP_RADIUS + 1, (255, 255, 255), 1)
            cv2.line(out, (tx, ty), (sx, sy), LINK_COLOR, 1)

        draw_outlined_text(out, simple_id, (tx + 8, max(16, ty - 6)))

    return out


# =========================================================
# MAIN LOGIC PER UNA SINGOLA IMMAGINE
# =========================================================
# Costruisce il grafo dei terminali a partire da:
# - terminals del passo 03
# - skeleton del passo 04

def build_terminal_graph_for_image(data: dict):
    terminals = data.get("terminals", [])
    components = data.get("components", [])
    wire_extraction = data.get("wire_extraction", {})
    skeleton_path = wire_extraction.get("skeleton_path")

    if not skeleton_path:
        raise ValueError("skeleton_path mancante nel JSON del passo 04.")

    skeleton = load_binary_image(Path(skeleton_path))
    skeleton_for_graph = erase_component_bodies_from_skeleton(skeleton, components)

    # Connected components dello skeleton.
    # Ogni label > 0 rappresenta un tratto di filo connesso.
    _, labels, _, _ = cv2.connectedComponentsWithStats(skeleton_for_graph, connectivity=8)

    # Match semplice: ogni terminale viene agganciato alla label dello skeleton
    # trovata nella sua zona locale.
    terminal_match_debug = {}
    for term in terminals:
        terminal_match_debug[term["terminal_id"]] = match_terminal_to_skeleton_label(labels, term)

    attach_unmatched_analog_meter_terminals(components, terminal_match_debug, labels)
    attach_unmatched_opamp_aux_to_external_terminals(terminals, terminal_match_debug)

    original_to_simple = build_simple_id_map(terminals)

    # Gruppi di terminali che insistono sullo stesso tratto di filo.
    label_to_terminal_ids = build_label_to_terminal_ids(terminal_match_debug)
    label_to_terminal_ids = merge_bjt_base_aligned_labels(
        label_to_terminal_ids,
        terminals,
        components,
        terminal_match_debug,
        labels,
    )
    label_to_terminal_ids = merge_mosfet_gate_aligned_labels(
        label_to_terminal_ids,
        terminals,
        components,
        terminal_match_debug,
        labels,
    )
    label_to_terminal_ids = merge_opamp_aux_external_terminal_labels(
        label_to_terminal_ids,
        terminals,
        terminal_match_debug,
    )
    label_to_terminal_ids = merge_near_horizontal_stub_labels(
        label_to_terminal_ids,
        terminals,
        terminal_match_debug,
        labels,
    )
    label_to_terminal_ids = split_bridge_labels(
        label_to_terminal_ids,
        terminals,
        terminal_match_debug,
        skeleton_for_graph,
        labels,
        wire_extraction,
    )
    label_to_terminal_ids = merge_mosfet_gate_rail_groups(
        label_to_terminal_ids,
        terminals,
        components,
    )
    label_to_terminal_ids = merge_battery_gate_rail_groups(
        label_to_terminal_ids,
        terminals,
    )
    label_to_terminal_ids = remove_non_shorting_component_self_matches(
        label_to_terminal_ids,
        terminals,
        terminal_match_debug,
    )

    # Grafo finale interno e sua vista canonica leggibile.
    terminal_graph = build_terminal_graph(terminals, label_to_terminal_ids)
    for source_id, target_id in build_vertical_inductor_parallel_direct_edges(
        terminals,
        terminal_match_debug,
        labels,
    ):
        terminal_graph.setdefault(source_id, [])
        terminal_graph.setdefault(target_id, [])
        terminal_graph[source_id].append(target_id)
        terminal_graph[target_id].append(source_id)
    for terminal_id in terminal_graph:
        terminal_graph[terminal_id] = sorted(set(terminal_graph[terminal_id]))
    simple_terminal_graph = build_simple_terminal_graph(terminal_graph, original_to_simple)
    supply_graph_links = build_supply_graph_links(
        terminals,
        label_to_terminal_ids,
        terminal_match_debug,
        labels,
        data.get("image_height"),
        original_to_simple,
    )
    for terminal_id, supply_labels in supply_graph_links.items():
        simple_terminal_graph.setdefault(terminal_id, [])
        simple_terminal_graph[terminal_id] = sorted(set(simple_terminal_graph[terminal_id]) | set(supply_labels))
        for supply_label in supply_labels:
            simple_terminal_graph.setdefault(supply_label, [])
            simple_terminal_graph[supply_label] = sorted(set(simple_terminal_graph[supply_label]) | {terminal_id})
    simple_terminal_graph = {key: simple_terminal_graph[key] for key in sorted(simple_terminal_graph.keys())}

    # Terminali isolati nel grafo finale.
    unconnected_terminals = sorted([
        terminal_id
        for terminal_id, neighbors in simple_terminal_graph.items()
        if len(neighbors) == 0
    ])
    unmatched_terminals = sorted([
        terminal_id
        for terminal_id, info in terminal_match_debug.items()
        if info.get("matched_label") is None
    ])
    suspicious_matches = sorted([
        terminal_id
        for terminal_id, info in terminal_match_debug.items()
        if info.get("is_suspicious", False) and info.get("matched_label") is not None
    ])

    canonical_components = build_canonical_components(components)

    warnings = {
        "unconnected_terminals": unconnected_terminals,
        "unmatched_terminals": build_simple_list(unmatched_terminals, original_to_simple),
        "suspicious_matches": build_simple_list(suspicious_matches, original_to_simple),
    }

    return {
        "components": canonical_components,
        "graph": simple_terminal_graph,
        "warnings": warnings,
        "skeleton_binary": skeleton_for_graph,
        "terminal_match_debug": terminal_match_debug,
        "simple_id_map": original_to_simple,
    }


# =========================================================
# MAIN
# =========================================================
# Run dell'entrypoint del nuovo passo 05.
def main() -> None:
    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"Cartella input non trovata: {INPUT_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if SAVE_DEBUG_IMAGES:
        DEBUG_TERMINAL_OVERLAY_DIR.mkdir(parents=True, exist_ok=True)
        DEBUG_SKELETON_OVERLAY_DIR.mkdir(parents=True, exist_ok=True)

    json_files = sorted(INPUT_DIR.glob("*.json"))
    if not json_files:
        raise FileNotFoundError(f"Nessun file JSON trovato in: {INPUT_DIR}")

    print(f"Input directory : {INPUT_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"File trovati    : {len(json_files)}\n")

    for i, json_path in enumerate(json_files, start=1):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        graph_info = build_terminal_graph_for_image(data)

        # -------------------------------------------------
        # 1) Eventuali immagini di debug
        # -------------------------------------------------
        if SAVE_DEBUG_IMAGES:
            image_path = Path(data["image_path"])
            image_bgr = cv2.imread(str(image_path))
            if image_bgr is not None:
                terminal_overlay = draw_terminal_overlay(
                    image_bgr,
                    data.get("terminals", []),
                    graph_info["terminal_match_debug"],
                    graph_info["simple_id_map"],
                )
                terminal_overlay_path = DEBUG_TERMINAL_OVERLAY_DIR / f"{json_path.stem}_terminal_overlay.jpg"
                cv2.imwrite(str(terminal_overlay_path), terminal_overlay)

            skeleton_overlay = draw_skeleton_overlay(
                graph_info["skeleton_binary"],
                data.get("terminals", []),
                graph_info["terminal_match_debug"],
                graph_info["simple_id_map"],
            )
            skeleton_overlay_path = DEBUG_SKELETON_OVERLAY_DIR / f"{json_path.stem}_skeleton_overlay.jpg"
            cv2.imwrite(str(skeleton_overlay_path), skeleton_overlay)

        # -------------------------------------------------
        # 2) Salvataggio JSON canonico del passo 05
        # -------------------------------------------------
        output_data = {
            "image_id": data.get("image_id"),
            "image_name": data.get("image_name"),
            "components": graph_info["components"],
            "graph": graph_info["graph"],
            "warnings": graph_info["warnings"],
        }

        out_json_path = OUTPUT_DIR / json_path.name
        with open(out_json_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(
            f"[{i}/{len(json_files)}] {json_path.name} -> "
            f"componenti={len(output_data['components'])}, "
            f"nodi_grafo={len(output_data['graph'])}, "
            f"isolati={len(output_data['warnings']['unconnected_terminals'])}, "
            f"unmatched={len(output_data['warnings']['unmatched_terminals'])}"
        )

    print("\nCompletato.")
    print(f"JSON salvati in: {OUTPUT_DIR}")
    if SAVE_DEBUG_IMAGES:
        print(f"Debug overlay diagramma in: {DEBUG_TERMINAL_OVERLAY_DIR}")
        print(f"Debug overlay skeleton in: {DEBUG_SKELETON_OVERLAY_DIR}")


if __name__ == "__main__":
    main()
