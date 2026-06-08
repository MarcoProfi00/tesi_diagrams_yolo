"""
04_extract_wires.py

Scopo:
    Estrarre i fili dal diagramma dopo lo step 03.

    Lo step 03 fornisce:
      - componenti con bbox/body_bbox;
      - terminali con coordinate e lato stimato.

    Lo step 04 usa queste informazioni per:
      - mascherare il corpo dei componenti, evitando che simboli e testi
        vengano interpretati come fili;
      - riaprire piccole zone attorno ai terminali, cosi' il contatto tra
        terminale e filo non viene cancellato dalla maschera;
      - binarizzare, chiudere piccoli gap, filtrare rumore e produrre lo
        skeleton dei fili usato dallo step 05.

Output principali:
    - component_mask: maschera dei componenti da rimuovere;
    - terminal_keep_debug: zone terminali preservate;
    - masked_gray: immagine grayscale con componenti cancellati;
    - binary: binarizzazione dei fili;
    - closed: binario dopo closing morfologico;
    - bridged: binario dopo ricucitura di segmenti frammentati;
    - filtered: binario dopo rimozione componenti piccoli;
    - skeleton: skeleton monolinea dei fili.
"""

from pathlib import Path
import os
import json
import cv2
import numpy as np
from skimage.morphology import skeletonize

# =========================================================
# PERCORSI / INPUT-OUTPUT
# =========================================================
# PIPELINE_DATASET e PIPELINE_IMAGE_IDS permettono di usare lo stesso script
# su batch diversi o su un sottoinsieme di immagini, senza modificare il codice.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PIPELINE_DATASET = os.environ.get("PIPELINE_DATASET", "pipeline1.0/batchC/batchC1")
PIPELINE_IMAGE_IDS = [
    image_id.strip()
    for image_id in os.environ.get("PIPELINE_IMAGE_IDS", "").split(",")
    if image_id.strip()
]

INPUT_DIR = PROJECT_ROOT / "outputs" / PIPELINE_DATASET / "03_estimate_terminals"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / PIPELINE_DATASET / "04_extract_wires"

# =========================================================
# MASCHERAMENTO COMPONENTI
# =========================================================
# Ogni sottocartella salva una vista intermedia. Questo rende lo step 04
# ispezionabile: quando il grafo finale e' sbagliato si puo' capire se il
# problema nasce dalla maschera, dalla binarizzazione o dallo skeleton.
MASK_DEBUG_DIR = OUTPUT_DIR / "mask_debug"
COMPONENT_MASK_DIR = OUTPUT_DIR / "component_mask"
TERMINAL_KEEP_DEBUG_DIR = OUTPUT_DIR / "terminal_keep_debug"
MASKED_DIR = OUTPUT_DIR / "masked_gray"
BINARY_DIR = OUTPUT_DIR / "binary"
CLOSED_DIR = OUTPUT_DIR / "closed"
BRIDGED_DIR = OUTPUT_DIR / "bridged"
FILTERED_DIR = OUTPUT_DIR / "filtered"
SKELETON_DIR = OUTPUT_DIR / "skeleton"


MASK_SHRINK_FACTOR = 1.0

# Padding aggiuntivo per classi in cui il bbox YOLO tende a lasciare fuori
# porzioni del simbolo. Aumentare troppo questi valori puo' cancellare fili
# vicini, quindi sono mantenuti specifici per classe.
CLASS_MASK_PADDING = {
    "Analog_Meter": 8,
    "Antenna": 10,
    "Connector": 6,
    "Polarized_Capacitor": 8,
    "Switch": 4,
    "Transformer": 4,
}

# =========================================================
# ZONE TERMINALI DA PRESERVARE
# =========================================================
# Dopo aver mascherato i componenti, apriamo piccole zone attorno ai terminali:
# senza questo passaggio il filo che tocca il componente verrebbe cancellato
# insieme al corpo del simbolo e lo step 05 non riuscirebbe ad agganciare il
# terminale allo skeleton.
TERMINAL_KEEP_RADIUS = 10
TERMINAL_KEEP_LINE_THICKNESS = 7
TERMINAL_KEEP_INWARD_LEN = 14
TERMINAL_KEEP_OUTWARD_LEN = 12
FACING_KEEP_MAX_AXIS_GAP = 52
FACING_KEEP_MAX_LATERAL_DELTA = 14
FACING_KEEP_MAX_BBOX_GAP = 28
FACING_KEEP_MAX_BBOX_OVERLAP = 36
FACING_KEEP_MIN_PROJECTION_OVERLAP_RATIO = 0.45
FACING_KEEP_MIN_THICKNESS = 4

# I pin ausiliari degli opamp possono essere molto vicini al corpo del simbolo:
# usiamo una keep zone piu' piccola per non riaprire troppo il triangolo.
OPAMP_AUX_KEEP_RADIUS = 5
OPAMP_AUX_KEEP_LINE_THICKNESS = 5
OPAMP_AUX_KEEP_INWARD_LEN = 0
OPAMP_AUX_KEEP_OUTWARD_LEN = 12

CLASS_TERMINAL_KEEP_OVERRIDES = {
    # Questi simboli hanno molto "corpo" interno e, se preserviamo troppo
    # dentro al bbox, rischiamo di riaprire il simbolo nello skeleton.
    "Analog_Meter": {
        "radius": 8,
        "thickness": 6,
        "inward_len": 4,
        "outward_len": 14,
    },
    # L'antenna e' monoterminale ma il simbolo puo' contenere frecce o
    # tratti decorativi che, se preservati troppo, vengono letti come fili.
    # Lasciamo aperto solo un piccolo corridoio attorno al vero pin.
    "Antenna": {
        "radius": 4,
        "thickness": 5,
        "inward_len": 0,
        "outward_len": 24,
    },
    "Connector": {
        "radius": 3,
        "thickness": 3,
        "inward_len": 1,
        "outward_len": 14,
    },
    "Switch": {
        "radius": 8,
        "thickness": 6,
        "inward_len": 2,
        "outward_len": 16,
    },
    "Transformer": {
        "radius": 8,
        "thickness": 6,
        "inward_len": 4,
        "outward_len": 14,
    },
    "Integrated_Circuit": {
        "radius": 6,
        "thickness": 5,
        "inward_len": 2,
        "outward_len": 16,
    },
    # Il simbolo GND e' monoterminale: se riapriamo troppo il bbox, le barre
    # del simbolo possono diventare ponti laterali verso fili vicini.
    "GND": {
        "radius": 3,
        "thickness": 3,
        "inward_len": 0,
        "outward_len": 18,
    },
    # Nei polarizzati il body e i marker grafici (+ / piastra curva) possono
    # riaprire il simbolo come fosse un filo continuo. Manteniamo solo stub
    # corti vicino ai terminali.
    "Polarized_Capacitor": {
        "radius": 5,
        "thickness": 4,
        "inward_len": 0,
        "outward_len": 9,
    },
}

# =========================================================
# MORFOLOGIA
# =========================================================
# Parametri della pipeline morfologica:
# - closing: ricuce piccoli gap locali;
# - ricucitura fili frammentati: ricuce spezzoni, soprattutto dopo maschera;
# - soppressione IC: evita che la ricucitura verticale crei falsi collegamenti
#   paralleli lungo i lati degli integrati.
CLOSING_KERNEL_SIZE = 3
CLOSING_ITERATIONS = 1
ENABLE_FRAGMENTED_WIRE_BRIDGE = True
FRAGMENTED_WIRE_BRIDGE_KERNEL_LENGTH = 15
FRAGMENTED_WIRE_BRIDGE_KERNEL_THICKNESS = 3
FRAGMENTED_WIRE_BRIDGE_ITERATIONS = 1
FRAGMENTED_WIRE_BRIDGE_DETECT_LENGTH = 7
IC_VERTICAL_BRIDGE_SUPPRESS_OUTWARD = 80
IC_VERTICAL_BRIDGE_SUPPRESS_INWARD = 14
IC_VERTICAL_BRIDGE_SUPPRESS_Y_PAD = 30

# =========================================================
# FILTRO COMPONENTI CONNESSE PICCOLE
# =========================================================
# Rimuove piccole componenti connesse residue dopo binarizzazione/closing:
# tipicamente pixel isolati, testo rimasto o frammenti non elettrici.
ENABLE_SMALL_COMPONENT_FILTER = True
MIN_COMPONENT_AREA = 40

# =========================================================
# UTILITY GEOMETRICHE
# =========================================================
def clamp_point(x, y, w, h):
    """Porta un punto dentro i limiti dell'immagine."""
    x = max(0, min(w - 1, int(round(x))))
    y = max(0, min(h - 1, int(round(y))))
    return x, y


def shrink_bbox(bbox, shrink_factor=0.88):
    """Riduce un bbox mantenendone il centro."""
    x1, y1, x2, y2 = bbox
    xc = (x1 + x2) / 2.0
    yc = (y1 + y2) / 2.0
    w = (x2 - x1) * shrink_factor
    h = (y2 - y1) * shrink_factor

    new_x1 = xc - w / 2.0
    new_y1 = yc - h / 2.0
    new_x2 = xc + w / 2.0
    new_y2 = yc + h / 2.0

    return [new_x1, new_y1, new_x2, new_y2]


def expand_bbox(bbox, pad=0):
    """Espande un bbox dello stesso padding su tutti i lati."""
    x1, y1, x2, y2 = bbox
    return [x1 - pad, y1 - pad, x2 + pad, y2 + pad]


def component_mask_bbox(comp):
    """
    Sceglie il bbox da usare per mascherare un componente.

    Per gli Integrated_Circuit preferiamo body_bbox quando disponibile: il bbox
    YOLO puo' includere pin/testo esterno, mentre body_bbox rappresenta meglio
    il corpo da cancellare.
    """
    if comp.get("class_name") == "Integrated_Circuit" and comp.get("body_bbox"):
        return comp["body_bbox"]
    return comp["bbox"]


# =========================================================
# COSTRUZIONE MASCHERE
# =========================================================
def build_base_component_mask(image_shape, components):
    """
    Costruisce la maschera base dei componenti.

    I pixel a 255 rappresentano zone da cancellare dall'immagine dei fili.
    Le zone dei terminali vengono riaperte in un secondo momento.
    """
    h, w = image_shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)

    for comp in components:
        if not comp.get("use_for_masking", False):
            continue

        bbox = shrink_bbox(component_mask_bbox(comp), shrink_factor=MASK_SHRINK_FACTOR)
        bbox = expand_bbox(
            bbox,
            pad=int(CLASS_MASK_PADDING.get(str(comp.get("class_name", "")).strip(), 0)),
        )
        x1, y1, x2, y2 = map(int, bbox)

        x1 = max(0, min(w - 1, x1))
        y1 = max(0, min(h - 1, y1))
        x2 = max(0, min(w - 1, x2))
        y2 = max(0, min(h - 1, y2))

        cv2.rectangle(mask, (x1, y1), (x2, y2), 255, thickness=-1)

    return mask

def terminal_keep_params(term):
    """Restituisce i parametri di keep zone per un singolo terminale."""
    name = str(term.get("name", "")).lower()
    class_name = str(term.get("component_class_name", "")).strip()

    if name in {"aux1", "aux2"}:
        return {
            "radius": OPAMP_AUX_KEEP_RADIUS,
            "thickness": OPAMP_AUX_KEEP_LINE_THICKNESS,
            "inward_len": OPAMP_AUX_KEEP_INWARD_LEN,
            "outward_len": OPAMP_AUX_KEEP_OUTWARD_LEN,
        }

    if class_name in CLASS_TERMINAL_KEEP_OVERRIDES:
        return dict(CLASS_TERMINAL_KEEP_OVERRIDES[class_name])

    return {
        "radius": TERMINAL_KEEP_RADIUS,
        "thickness": TERMINAL_KEEP_LINE_THICKNESS,
        "inward_len": TERMINAL_KEEP_INWARD_LEN,
        "outward_len": TERMINAL_KEEP_OUTWARD_LEN,
    }


def adapt_terminal_keep_for_component(term, params, components_by_instance):
    """
    Adatta i parametri di keep zone usando informazioni del componente padre.

    Caso principale: i display seven-segment hanno molti terminali vicini e
    segmenti interni; sulle colonne laterali usiamo corridoi piu' stretti per
    non trasformare il display in un falso nodo elettrico.
    """
    instance_id = term.get("instance_id")
    if instance_id is None:
        return params

    component = components_by_instance.get(str(instance_id))
    if not component:
        return params

    if component.get("component_subtype") != "seven_segment_display":
        return params

    side = str(term.get("relative_position") or "").lower()
    if side not in {"left", "right"}:
        return params

    adapted = dict(params)
    adapted["radius"] = min(int(adapted["radius"]), 3)
    adapted["thickness"] = min(int(adapted["thickness"]), 2)
    adapted["inward_len"] = min(int(adapted["inward_len"]), 0)
    adapted["outward_len"] = min(int(adapted["outward_len"]), 12)
    return adapted


def terminal_keep_segment(term, params=None):
    """
    Calcola il segmento direzionato da preservare attorno a un terminale.

    Il segmento si estende:
      - verso l'esterno del componente, per mantenere il filo;
      - leggermente verso l'interno, per tollerare terminali stimati non
        perfettamente sul bordo.
    """
    x = float(term["x"])
    y = float(term["y"])
    rel = term.get("relative_position")
    if params is None:
        params = terminal_keep_params(term)

    inward_len = params["inward_len"]
    outward_len = params["outward_len"]

    if rel == "left":
        p1 = (x - outward_len, y)
        p2 = (x + inward_len, y)
    elif rel == "right":
        p1 = (x - inward_len, y)
        p2 = (x + outward_len, y)
    elif rel == "top":
        p1 = (x, y - outward_len)
        p2 = (x, y + inward_len)
    elif rel == "bottom":
        p1 = (x, y - inward_len)
        p2 = (x, y + outward_len)
    else:
        p1 = (x, y)
        p2 = (x, y)

    return p1, p2


def _bbox_projection_overlap_ratio(a0, a1, b0, b1):
    """Calcola quanto due intervalli si sovrappongono lungo un asse."""
    inter = max(0.0, min(float(a1), float(b1)) - max(float(a0), float(b0)))
    len_a = max(1.0, float(a1) - float(a0))
    len_b = max(1.0, float(b1) - float(b0))
    return inter / max(1.0, min(len_a, len_b))


def _component_bbox_by_instance(components):
    """Crea un lookup instance_id -> bbox usato per la maschera."""
    mapping = {}
    for comp in components:
        instance_id = comp.get("instance_id")
        if instance_id is None:
            continue
        mapping[str(instance_id)] = component_mask_bbox(comp)
    return mapping


def _facing_terminal_keep_pairs(terminals, components):
    """
    Trova terminali di componenti diversi che si fronteggiano a distanza breve.

    Serve per preservare piccoli tratti di filo tra componenti molto vicini:
    senza questa eccezione la maschera di entrambi i componenti potrebbe
    cancellare completamente il collegamento intermedio.
    """
    component_boxes = _component_bbox_by_instance(components)
    pairs = []

    for idx, term_a in enumerate(terminals):
        side_a = str(term_a.get("relative_position") or "").lower()
        inst_a = str(term_a.get("instance_id") or "")
        bbox_a = component_boxes.get(inst_a)
        if bbox_a is None:
            continue

        for term_b in terminals[idx + 1:]:
            side_b = str(term_b.get("relative_position") or "").lower()
            inst_b = str(term_b.get("instance_id") or "")
            if not inst_b or inst_a == inst_b:
                continue
            bbox_b = component_boxes.get(inst_b)
            if bbox_b is None:
                continue

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

            if lateral_delta > FACING_KEEP_MAX_LATERAL_DELTA:
                continue
            if axis_gap > FACING_KEEP_MAX_AXIS_GAP:
                continue
            if projection_overlap < FACING_KEEP_MIN_PROJECTION_OVERLAP_RATIO:
                continue
            if bbox_gap > FACING_KEEP_MAX_BBOX_GAP and bbox_overlap <= 0.0:
                continue
            if bbox_overlap > FACING_KEEP_MAX_BBOX_OVERLAP:
                continue

            pairs.append((term_a, term_b))

    return pairs


def carve_terminal_keep_zones(mask, terminals, components):
    """
    Riapre nella maschera le zone che devono rimanere visibili come filo.

    La maschera parte con i componenti pieni a 255. Qui disegniamo a 0:
      - un cerchio centrato sul terminale;
      - una capsula direzionata lungo il lato stimato;
      - eventuali segmenti tra terminali frontali molto vicini.

    keep_debug salva le stesse zone in bianco, cosi' e' possibile verificare
    visivamente quali parti sono state preservate.
    """
    h, w = mask.shape[:2]
    keep_debug = np.zeros_like(mask)

    # Lookup dei componenti per instance_id: serve per adattare le keep zone in
    # base al componente padre, ad esempio per display seven-segment.
    components_by_instance = {}
    for comp in components:
        instance_id = comp.get("instance_id")
        if instance_id is None:
            continue
        components_by_instance[str(instance_id)] = comp

    for term in terminals:
        # Parametri finali del terminale: default per classe piu' eventuale
        # adattamento specifico del componente.
        params = adapt_terminal_keep_for_component(
            term,
            terminal_keep_params(term),
            components_by_instance,
        )

        x = int(round(term["x"]))
        y = int(round(term["y"]))
        x, y = clamp_point(x, y, w, h)

        # Cerchio locale: protegge il punto stimato anche se la coordinata non
        # cade esattamente sul pixel del filo.
        cv2.circle(mask, (x, y), params["radius"], 0, thickness=-1)
        cv2.circle(keep_debug, (x, y), params["radius"], 255, thickness=-1)

        # Segmento direzionato: preserva il tratto di filo che esce dal lato del
        # componente e un piccolo tratto interno di tolleranza.
        p1f, p2f = terminal_keep_segment(term, params=params)
        p1 = clamp_point(p1f[0], p1f[1], w, h)
        p2 = clamp_point(p2f[0], p2f[1], w, h)

        cv2.line(mask, p1, p2, 0, thickness=params["thickness"])
        cv2.line(keep_debug, p1, p2, 255, thickness=params["thickness"])

    for term_a, term_b in _facing_terminal_keep_pairs(terminals, components):
        # Quando due terminali di componenti diversi si fronteggiano molto da
        # vicino, preserviamo anche il segmento tra i due punti: e' una difesa
        # contro collegamenti corti cancellati da due maschere adiacenti.
        x1, y1 = clamp_point(term_a["x"], term_a["y"], w, h)
        x2, y2 = clamp_point(term_b["x"], term_b["y"], w, h)

        params_a = adapt_terminal_keep_for_component(
            term_a,
            terminal_keep_params(term_a),
            components_by_instance,
        )
        params_b = adapt_terminal_keep_for_component(
            term_b,
            terminal_keep_params(term_b),
            components_by_instance,
        )
        thickness = max(
            FACING_KEEP_MIN_THICKNESS,
            min(int(params_a["thickness"]), int(params_b["thickness"])),
        )

        cv2.line(mask, (x1, y1), (x2, y2), 0, thickness=thickness)
        cv2.line(keep_debug, (x1, y1), (x2, y2), 255, thickness=thickness)

    return mask, keep_debug


# Costruisce la maschera finale dei componenti e le zone terminali da preservare.
def build_component_mask(image_shape, components, terminals):
    """Costruisce maschera componenti finale e immagine debug delle keep zone."""
    mask = build_base_component_mask(image_shape, components)
    mask, keep_debug = carve_terminal_keep_zones(mask, terminals, components)
    return mask, keep_debug

# =========================================================
# OUTPUT DI DEBUG
# =========================================================
def save_mask_debug(image_bgr, mask, out_path: Path):
    """Salva un overlay rosso delle zone componenti mascherate."""
    overlay = image_bgr.copy()
    red_layer = np.zeros_like(image_bgr)
    red_layer[:, :, 2] = 255

    alpha = 0.35
    mask_bool = mask > 0
    overlay[mask_bool] = cv2.addWeighted(
        image_bgr[mask_bool], 1 - alpha, red_layer[mask_bool], alpha, 0
    )

    cv2.imwrite(str(out_path), overlay)


def save_terminal_keep_debug(image_bgr, keep_debug, out_path: Path):
    """Salva un overlay verde delle zone terminali preservate."""
    overlay = image_bgr.copy()
    green_layer = np.zeros_like(image_bgr)
    green_layer[:, :, 1] = 255

    alpha = 0.35
    keep_bool = keep_debug > 0
    overlay[keep_bool] = cv2.addWeighted(
        image_bgr[keep_bool], 1 - alpha, green_layer[keep_bool], alpha, 0
    )

    cv2.imwrite(str(out_path), overlay)

# =========================================================
# POST-PROCESSING FILI
# =========================================================
def remove_small_connected_components(binary_img, min_area=40):
    """Rimuove componenti connesse troppo piccole per essere fili affidabili."""
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary_img, connectivity=8)

    filtered = np.zeros_like(binary_img)
    kept_components = 0
    removed_components = 0

    for label_idx in range(1, num_labels):
        area = stats[label_idx, cv2.CC_STAT_AREA]

        if area >= min_area:
            filtered[labels == label_idx] = 255
            kept_components += 1
        else:
            removed_components += 1

    return filtered, kept_components, removed_components


def suppress_ic_side_vertical_bridge_pixels(vertical_bridged, base_img, components):
    """
    Elimina ricuciture verticali artificiali vicino ai lati degli IC.

    Il bridge verticale puo' unire tra loro pin consecutivi dello stesso lato,
    creando un falso filo parallelo al corpo dell'integrato. Per evitarlo
    cancelliamo solo i pixel aggiunti dal bridge nelle fasce laterali degli IC.
    """
    cleaned = vertical_bridged.copy()
    added_by_vertical_bridge = (vertical_bridged > 0) & (base_img == 0)
    h, w = cleaned.shape[:2]

    for comp in components:
        if comp.get("class_name") != "Integrated_Circuit":
            continue

        for side in ("left", "right"):
            side_terms = [
                term
                for term in comp.get("terminals", [])
                if term.get("relative_position") == side
            ]
            if len(side_terms) < 2:
                continue

            side_terms = sorted(side_terms, key=lambda term: float(term["y"]))
            x_anchor = int(round(sum(float(term["x"]) for term in side_terms) / len(side_terms)))
            y_values = [float(term["y"]) for term in side_terms]
            y1 = max(0, int(round(min(y_values) - IC_VERTICAL_BRIDGE_SUPPRESS_Y_PAD)))
            y2 = min(h, int(round(max(y_values) + IC_VERTICAL_BRIDGE_SUPPRESS_Y_PAD)))

            if side == "left":
                x1 = max(0, x_anchor - IC_VERTICAL_BRIDGE_SUPPRESS_OUTWARD)
                x2 = min(w, x_anchor + IC_VERTICAL_BRIDGE_SUPPRESS_INWARD)
            else:
                x1 = max(0, x_anchor - IC_VERTICAL_BRIDGE_SUPPRESS_INWARD)
                x2 = min(w, x_anchor + IC_VERTICAL_BRIDGE_SUPPRESS_OUTWARD)

            if y2 <= y1:
                continue

            bridge_mask = added_by_vertical_bridge[y1:y2, x1:x2]
            cleaned[y1:y2, x1:x2][bridge_mask] = 0

    return cleaned


def bridge_fragmented_wires(binary_img, components=None):
    """
    Ricuce piccoli gap nei fili frammentati.

    Usa due direzioni:
      - closing orizzontale sul binario completo;
      - closing verticale partendo da un seed verticale, per evitare che tratti
        orizzontali o simboli diventino falsi fili verticali.
    """
    if not ENABLE_FRAGMENTED_WIRE_BRIDGE:
        return binary_img.copy(), {
            "enabled": False,
            "kernel_length": None,
            "kernel_thickness": None,
            "iterations": None,
            "detect_length": None,
        }

    # Kernel orientati: uno per gap orizzontali e uno per gap verticali.
    h_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (
            FRAGMENTED_WIRE_BRIDGE_KERNEL_LENGTH,
            FRAGMENTED_WIRE_BRIDGE_KERNEL_THICKNESS,
        ),
    )
    v_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (
            FRAGMENTED_WIRE_BRIDGE_KERNEL_THICKNESS,
            FRAGMENTED_WIRE_BRIDGE_KERNEL_LENGTH,
        ),
    )
    h_detect_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (FRAGMENTED_WIRE_BRIDGE_DETECT_LENGTH, 1),
    )
    v_detect_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (1, FRAGMENTED_WIRE_BRIDGE_DETECT_LENGTH),
    )

    # Seed verticale: conserva solo evidenze gia' verticali prima di chiuderle,
    # riducendo il rischio di creare colonne artificiali.
    vertical_seed = cv2.morphologyEx(binary_img, cv2.MORPH_OPEN, v_detect_kernel)

    horizontal_bridged = cv2.morphologyEx(
        binary_img,
        cv2.MORPH_CLOSE,
        h_kernel,
        iterations=FRAGMENTED_WIRE_BRIDGE_ITERATIONS,
    )
    vertical_bridged = cv2.morphologyEx(
        vertical_seed,
        cv2.MORPH_CLOSE,
        v_kernel,
        iterations=FRAGMENTED_WIRE_BRIDGE_ITERATIONS,
    )
    # Pulizia specifica IC: rimuove le sole colonne introdotte dal bridge vicino
    # ai pin laterali degli integrati.
    vertical_bridged = suppress_ic_side_vertical_bridge_pixels(
        vertical_bridged,
        binary_img,
        components or [],
    )

    bridged = cv2.bitwise_or(
        binary_img,
        cv2.bitwise_or(horizontal_bridged, vertical_bridged),
    )

    return bridged, {
        "enabled": True,
        "kernel_length": FRAGMENTED_WIRE_BRIDGE_KERNEL_LENGTH,
        "kernel_thickness": FRAGMENTED_WIRE_BRIDGE_KERNEL_THICKNESS,
        "iterations": FRAGMENTED_WIRE_BRIDGE_ITERATIONS,
        "detect_length": FRAGMENTED_WIRE_BRIDGE_DETECT_LENGTH,
        "ic_vertical_bridge_suppress_outward": IC_VERTICAL_BRIDGE_SUPPRESS_OUTWARD,
        "ic_vertical_bridge_suppress_inward": IC_VERTICAL_BRIDGE_SUPPRESS_INWARD,
        "ic_vertical_bridge_suppress_y_pad": IC_VERTICAL_BRIDGE_SUPPRESS_Y_PAD,
        "notes": "Bridge orientato: ricuce segmenti orizzontali e verticali dai rispettivi seed, ma evita ricuciture verticali artificiali nei corridoi laterali degli IC.",
    }


def extract_wires_from_image(image_bgr, components, terminals):
    """
    Esegue l'intera estrazione fili per una singola immagine.

    Restituisce tutte le immagini intermedie per debug e i metadati tecnici da
    salvare nel JSON dello step 04.
    """
    # 1. Conversione in grayscale: la pipeline lavora su intensita', non colore.
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

    # 2. Maschera componenti + riapertura locale dei terminali.
    component_mask, terminal_keep_debug = build_component_mask(
        image_bgr.shape, components, terminals
    )

    # 3. Applicazione maschera: le zone a 255 della maschera diventano bianche,
    # quindi spariscono nella successiva threshold invertita.
    masked_gray = gray.copy()
    masked_gray[component_mask > 0] = 255

    # 4. Threshold Otsu invertita: i fili scuri diventano foreground bianco.
    _, binary = cv2.threshold(
        masked_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    # 5. Closing leggero per chiudere micro-gap prodotti da scansione/maschera.
    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (CLOSING_KERNEL_SIZE, CLOSING_KERNEL_SIZE)
    )
    closed = cv2.morphologyEx(
        binary,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=CLOSING_ITERATIONS,
    )

    # 6. Ricucitura orientata di fili frammentati.
    bridged, bridge_info = bridge_fragmented_wires(closed, components)

    # 7. Rimozione di piccole componenti residue non affidabili.
    if ENABLE_SMALL_COMPONENT_FILTER:
        filtered, kept_components, removed_components = remove_small_connected_components(
            bridged,
            min_area=MIN_COMPONENT_AREA,
        )
    else:
        filtered = bridged.copy()
        kept_components = None
        removed_components = None

    # 8. Skeletonizzazione: riduce i fili a un solo pixel di spessore, forma
    # richiesta dallo step 05 per connected components e matching terminali.
    skeleton_bool = skeletonize(filtered > 0)
    skeleton = (skeleton_bool.astype(np.uint8)) * 255

    filter_info = {
        "enabled": ENABLE_SMALL_COMPONENT_FILTER,
        "min_component_area": MIN_COMPONENT_AREA,
        "kept_components": kept_components,
        "removed_components": removed_components,
    }

    keep_info = {
        "terminal_keep_radius": TERMINAL_KEEP_RADIUS,
        "terminal_keep_line_thickness": TERMINAL_KEEP_LINE_THICKNESS,
        "terminal_keep_inward_len": TERMINAL_KEEP_INWARD_LEN,
        "terminal_keep_outward_len": TERMINAL_KEEP_OUTWARD_LEN,
        "facing_keep_max_axis_gap": FACING_KEEP_MAX_AXIS_GAP,
        "facing_keep_max_lateral_delta": FACING_KEEP_MAX_LATERAL_DELTA,
        "facing_keep_max_bbox_gap": FACING_KEEP_MAX_BBOX_GAP,
        "facing_keep_max_bbox_overlap": FACING_KEEP_MAX_BBOX_OVERLAP,
        "facing_keep_min_projection_overlap_ratio": FACING_KEEP_MIN_PROJECTION_OVERLAP_RATIO,
        "notes": "Ogni terminale preserva un cerchio locale e una piccola capsula direzionata lungo il lato stimato, per tollerare terminali non perfettamente sul cavo.",
    }

    return (
        component_mask,
        terminal_keep_debug,
        masked_gray,
        binary,
        closed,
        bridged,
        filtered,
        skeleton,
        filter_info,
        keep_info,
        bridge_info,
    )

# =========================================================
# MAIN
# =========================================================
def main() -> None:
    """Entry point dello step 04."""
    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"Cartella input non trovata: {INPUT_DIR}")

    # Creiamo sempre tutte le cartelle di output per mantenere ispezionabili le
    # immagini intermedie prodotte dalla pipeline.
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MASK_DEBUG_DIR.mkdir(parents=True, exist_ok=True)
    COMPONENT_MASK_DIR.mkdir(parents=True, exist_ok=True)
    TERMINAL_KEEP_DEBUG_DIR.mkdir(parents=True, exist_ok=True)
    MASKED_DIR.mkdir(parents=True, exist_ok=True)
    BINARY_DIR.mkdir(parents=True, exist_ok=True)
    CLOSED_DIR.mkdir(parents=True, exist_ok=True)
    BRIDGED_DIR.mkdir(parents=True, exist_ok=True)
    FILTERED_DIR.mkdir(parents=True, exist_ok=True)
    SKELETON_DIR.mkdir(parents=True, exist_ok=True)

    # Ogni JSON di input e' l'output dello step 03 per una singola immagine.
    json_files = sorted(INPUT_DIR.glob("*.json"))
    if PIPELINE_IMAGE_IDS:
        # Filtro opzionale per rilanciare lo step su immagini specifiche.
        wanted = set(PIPELINE_IMAGE_IDS)
        json_files = [json_path for json_path in json_files if json_path.stem in wanted]

    if not json_files:
        raise FileNotFoundError(f"Nessun file JSON trovato in: {INPUT_DIR}")

    print(f"Input directory : {INPUT_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"File trovati    : {len(json_files)}")
    if PIPELINE_IMAGE_IDS:
        print(f"\nFiltro immagini : {PIPELINE_IMAGE_IDS}\n")
    else:
        print()

    for i, json_path in enumerate(json_files, start=1):
        # Caricamento dati step 03: componenti, terminali e path immagine.
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        image_path = Path(data["image_path"])
        image_bgr = cv2.imread(str(image_path))
        if image_bgr is None:
            print(f"Attenzione: immagine non leggibile -> {image_path}")
            continue

        components = data.get("components", [])
        terminals = data.get("terminals", [])

        # Estrazione fili vera e propria.
        (
            component_mask,
            terminal_keep_debug,
            masked_gray,
            binary,
            closed,
            bridged,
            filtered,
            skeleton,
            filter_info,
            keep_info,
            bridge_info,
        ) = extract_wires_from_image(image_bgr, components, terminals)

        # Path delle immagini intermedie associate al JSON corrente.
        stem = json_path.stem

        mask_debug_path = MASK_DEBUG_DIR / f"{stem}_mask_debug.jpg"
        component_mask_path = COMPONENT_MASK_DIR / f"{stem}_component_mask.png"
        terminal_keep_debug_path = TERMINAL_KEEP_DEBUG_DIR / f"{stem}_terminal_keep_debug.jpg"
        masked_path = MASKED_DIR / f"{stem}_masked_gray.png"
        binary_path = BINARY_DIR / f"{stem}_binary.png"
        closed_path = CLOSED_DIR / f"{stem}_closed.png"
        bridged_path = BRIDGED_DIR / f"{stem}_bridged.png"
        filtered_path = FILTERED_DIR / f"{stem}_filtered.png"
        skeleton_path = SKELETON_DIR / f"{stem}_skeleton.png"

        # Salvataggio viste intermedie: sono fondamentali per capire eventuali
        # errori dello step 05 guardando cosa e' successo allo skeleton.
        save_mask_debug(image_bgr, component_mask, mask_debug_path)
        save_terminal_keep_debug(image_bgr, terminal_keep_debug, terminal_keep_debug_path)
        cv2.imwrite(str(component_mask_path), component_mask)
        cv2.imwrite(str(masked_path), masked_gray)
        cv2.imwrite(str(binary_path), binary)
        cv2.imwrite(str(closed_path), closed)
        cv2.imwrite(str(bridged_path), bridged)
        cv2.imwrite(str(filtered_path), filtered)
        cv2.imwrite(str(skeleton_path), skeleton)

        # Il JSON di output conserva i dati precedenti e aggiunge solo il blocco
        # wire_extraction, che contiene parametri tecnici e path usati da 05.
        output_data = dict(data)
        output_data["wire_extraction"] = {
            "mask_shrink_factor": MASK_SHRINK_FACTOR,
            "terminal_keep": keep_info,
            "closing_kernel_size": CLOSING_KERNEL_SIZE,
            "closing_iterations": CLOSING_ITERATIONS,
            "fragmented_wire_bridge": bridge_info,
            "small_component_filter": filter_info,
            "mask_debug_path": str(mask_debug_path),
            "component_mask_path": str(component_mask_path),
            "terminal_keep_debug_path": str(terminal_keep_debug_path),
            "masked_gray_path": str(masked_path),
            "binary_path": str(binary_path),
            "closed_path": str(closed_path),
            "bridged_path": str(bridged_path),
            "filtered_path": str(filtered_path),
            "skeleton_path": str(skeleton_path),
        }

        out_json_path = OUTPUT_DIR / json_path.name
        with open(out_json_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"[{i}/{len(json_files)}] {json_path.name} -> estrazione fili completata")
        if ENABLE_SMALL_COMPONENT_FILTER:
            print(
                f"    filtro componenti piccoli -> kept={filter_info['kept_components']}, "
                f"removed={filter_info['removed_components']}"
            )

    print("\nCompletato.")
    print(f"Risultati salvati in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
