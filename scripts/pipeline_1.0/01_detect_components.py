"""
Passo 01: rilevamento componenti.

Per ogni immagine nella cartella di input:
    1. carica il modello YOLO;
    2. legge metadata/class_terminals_v1.yaml;
    3. seleziona le classi da rilevare;
    4. esegue la detection;
    5. applica le rifiniture geometriche specifiche per simboli ambigui;
    6. salva un JSON per immagine;
    7. salva un'immagine debug con i bounding box.
"""

from pathlib import Path
import os
import json
import math
import cv2

from ultralytics import YOLO
from estimate_terminals._shared_utils import (
    group_close_indices as _group_close_indices,
)
from estimate_terminals.io_utils import (
    img_build_foreground_binary,
    io_load_yaml as load_yaml,
)
from estimate_terminals.probes import (
    get_terminal_class_far_probe_scores,
    get_terminal_class_probe_scores,
)

# =========================================================
# CONFIGURAZIONE
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PIPELINE_DATASET = os.environ.get(
    "PIPELINE_DATASET",
    "pipeline1.0/batchA_07_09"
)
PIPELINE_INPUT_BATCH = os.environ.get("PIPELINE_INPUT_BATCH", "batchA_07_09")
PIPELINE_INPUT_DIR = str(os.environ.get("PIPELINE_INPUT_DIR", "")).strip()
PIPELINE_IMAGE_IDS = {
    image_id.strip()
    for image_id in os.environ.get("PIPELINE_IMAGE_IDS", "").split(",")
    if image_id.strip()
}

# === MODELLO ===
MODEL_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "yolo11"
    / "exp11b1_yolo11_rgb_aug_strong_v3"
    / "weights"
    / "best.pt"
)

# === METADATI CLASSI ===
CLASS_TERMINALS_PATH = PROJECT_ROOT / "metadata" / "class_terminals_v1.yaml"

# === INPUT ===
if PIPELINE_INPUT_DIR:
    _configured_input_dir = Path(PIPELINE_INPUT_DIR).expanduser()
    INPUT_IMAGES_DIR = (
        _configured_input_dir
        if _configured_input_dir.is_absolute()
        else PROJECT_ROOT / _configured_input_dir
    )
else:
    INPUT_IMAGES_DIR = PROJECT_ROOT / "data" / PIPELINE_INPUT_BATCH

# === OUTPUT ===
OUTPUT_DIR = PROJECT_ROOT / "outputs" / PIPELINE_DATASET / "01_detect_components"
DEBUG_IMAGES_DIR = OUTPUT_DIR / "debug_images"

# === PARAMETRI INFERENZA ===
IMG_SIZE = 1024
CONF_THRES = 0.40
IOU_THRES = 0.45
CLASS_CONF_THRES = {
    "Analog_Meter": 0.03,
    "Battery": 0.18,
    "Connector": 0.18,
    "Diode": 0.20,
    "Inductor": 0.30,
    "Lamp": 0.25,
    "Memristor": 0.08,
    "Meter": 0.18,
    "Mosfet": 0.22,
    "Push_Button": 0.22,
    "Resistor": 0.30,
    "Switch": 0.02,
    "Terminal": 0.25,
    "Transformer": 0.22,
}

# === DEBUG ===
SAVE_DEBUG_IMAGES = True

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}

# =========================================================
# UTILITY GEOMETRICHE DI BASE
# =========================================================
#Riporta un bbox ai limiti immagine per le euristiche locali di post-detection
def _clamp_bbox_to_image(box, image_shape):
    h, w = image_shape[:2]
    x1, y1, x2, y2 = box
    x1 = max(0, min(w - 1, int(round(x1))))
    y1 = max(0, min(h - 1, int(round(y1))))
    x2 = max(0, min(w - 1, int(round(x2))))
    y2 = max(0, min(h - 1, int(round(y2))))
    return x1, y1, x2, y2

#Fonde coordinate troppo vicine per evitare doppi conteggi dello stesso pin/feature
def _merge_close_values(values, min_gap):
    if not values:
        return []

    merged = [float(values[0])]
    for value in values[1:]:
        if float(value) - merged[-1] < float(min_gap):
            merged[-1] = (merged[-1] + float(value)) / 2.0
        else:
            merged.append(float(value))
    return [int(round(v)) for v in merged]


def _bbox_area(box) -> float:
    x1, y1, x2, y2 = box
    return max(0.0, float(x2 - x1)) * max(0.0, float(y2 - y1))


def _bbox_intersection(box_a, box_b) -> float:
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b
    ix1 = max(float(ax1), float(bx1))
    iy1 = max(float(ay1), float(by1))
    ix2 = min(float(ax2), float(bx2))
    iy2 = min(float(ay2), float(by2))
    return max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)


def _bbox_iou(box_a, box_b) -> float:
    inter = _bbox_intersection(box_a, box_b)
    if inter <= 0.0:
        return 0.0
    union = _bbox_area(box_a) + _bbox_area(box_b) - inter
    if union <= 0.0:
        return 0.0
    return inter / union


def _axis_overlap_ratio(a1, a2, b1, b2) -> float:
    """Misura quanto due intervalli si sovrappongono rispetto al piu' corto."""
    inter = max(0.0, min(float(a2), float(b2)) - max(float(a1), float(b1)))
    base = max(1.0, min(abs(float(a2) - float(a1)), abs(float(b2) - float(b1))))
    return inter / base


def _bbox_ioa(box_inner, box_outer) -> float:
    area_inner = _bbox_area(box_inner)
    if area_inner <= 0.0:
        return 0.0
    return _bbox_intersection(box_inner, box_outer) / area_inner


def _bbox_center(box):
    x1, y1, x2, y2 = box
    return (float(x1 + x2) / 2.0, float(y1 + y2) / 2.0)


def _point_in_box(point, box) -> bool:
    px, py = point
    x1, y1, x2, y2 = box
    return float(x1) <= float(px) <= float(x2) and float(y1) <= float(py) <= float(y2)

# =========================================================
# UTILITY DI ANALISI IMMAGINE / BINARIO
# =========================================================
def _count_hough_circles(image_gray, box, min_dist=18, param1=80, param2=14, min_radius=7, max_radius=24):
    """Conta i cerchi rilevati in una ROI: utile per connettori e meter analogici."""
    x1, y1, x2, y2 = _clamp_bbox_to_image(box, image_gray.shape)
    if x2 <= x1 or y2 <= y1:
        return 0

    roi = image_gray[y1:y2 + 1, x1:x2 + 1]
    circles = cv2.HoughCircles(
        roi,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=min_dist,
        param1=param1,
        param2=param2,
        minRadius=min_radius,
        maxRadius=max_radius,
    )
    if circles is None:
        return 0
    return int(circles.shape[1])


def expand_led_bbox(box, image_shape):
    """Allarga leggermente il bbox del LED verso l'area delle frecce luminose."""
    x1, y1, x2, y2 = box
    expanded = [
        float(x1) - 6.0,
        float(y1) - 18.0,
        float(x2) + 30.0,
        float(y2) + 6.0,
    ]
    return _clamp_bbox_to_image(expanded, image_shape)


def _component_areas_in_box(image_binary, box):
    """Restituisce le aree delle connected components in una ROI binaria."""
    x1, y1, x2, y2 = _clamp_bbox_to_image(box, image_binary.shape)
    if x2 <= x1 or y2 <= y1:
        return []

    roi = image_binary[y1:y2 + 1, x1:x2 + 1]
    num_labels, _, stats, _ = cv2.connectedComponentsWithStats(roi, connectivity=8)
    return sorted(
        [int(stats[i, cv2.CC_STAT_AREA]) for i in range(1, num_labels)],
        reverse=True,
    )


# =========================================================
# VALIDATOR PER CLASSI SPECIFICHE
# =========================================================

# Verifica se un simbolo circolare con grafica interna e una signal source.
def is_signal_source_like_bbox(image_gray, image_binary, box) -> bool:
    x1, y1, x2, y2 = _clamp_bbox_to_image(box, image_gray.shape)
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)
    ratio = width / float(height)

    # Il simbolo e quasi circolare/quadrato.
    if min(width, height) < 70 or not (0.78 <= ratio <= 1.28):
        return False

    # Deve esserci il cerchio esterno.
    circle_count = _count_hough_circles(
        image_gray,
        box,
        min_dist=max(20, int(round(min(width, height) * 0.30))),
        param1=80,
        param2=13,
        min_radius=max(18, int(round(min(width, height) * 0.22))),
        max_radius=max(60, int(round(min(width, height) * 0.48))),
    )
    if circle_count < 1:
        return False

    roi_gray = image_gray[y1:y2 + 1, x1:x2 + 1]
    roi_bin = image_binary[y1:y2 + 1, x1:x2 + 1]

    # Guarda solo la parte interna, escludendo il bordo del cerchio.
    cx1 = int(round(width * 0.22))
    cx2 = int(round(width * 0.78))
    cy1 = int(round(height * 0.22))
    cy2 = int(round(height * 0.78))
    inner_gray = roi_gray[cy1:cy2, cx1:cx2]
    inner_bin = roi_bin[cy1:cy2, cx1:cx2]

    if inner_gray.size == 0 or inner_bin.size == 0:
        return False

    inner_density = cv2.countNonZero(inner_bin) / float(max(inner_bin.size, 1))

    # Una sorgente sinusoidale ha contenuto centrale moderato.
    if not (0.05 <= inner_density <= 0.28):
        return False

    # Evita i meter con lancetta/segmenti forti.
    edges = cv2.Canny(inner_gray, 50, 150)
    lines = cv2.HoughLinesP(
        edges,
        1,
        math.pi / 180.0,
        threshold=10,
        minLineLength=max(16, int(round(min(inner_gray.shape[:2]) * 0.28))),
        maxLineGap=5,
    )

    strong_straight_lines = 0
    if lines is not None:
        for line in lines[:, 0, :]:
            lx1, ly1, lx2, ly2 = map(int, line)
            dx = lx2 - lx1
            dy = ly2 - ly1
            length = math.hypot(dx, dy)
            if length < max(16, min(width, height) * 0.22):
                continue

            angle = abs(math.degrees(math.atan2(dy, dx)))
            angle = min(angle, 180.0 - angle)

            # linee molto dritte orizzontali/verticali/diagonali lunghe
            if angle <= 18.0 or 72.0 <= angle <= 108.0 or angle >= 150.0:
                strong_straight_lines += 1

    if strong_straight_lines >= 2:
        return False

    component_areas = _component_areas_in_box(
        image_binary,
        [x1 + cx1, y1 + cy1, x1 + cx2, y1 + cy2],
    )
    medium_components = [
        a for a in component_areas
        if a >= max(20, int(round(inner_bin.shape[0] * inner_bin.shape[1] * 0.015)))
    ]

    # Dentro ci aspettiamo pochi tratti, non tanti pezzi sparsi.
    return 1 <= len(medium_components) <= 3

# CLASSI LINEARI - TRANSISTOR - SWITCH
def is_mosfet_like_bbox(image_gray, box) -> bool:
    """Valida Mosfet in modo piu semplice:
    richiede almeno due barre verticali interne ben separate.
    Evita la T di alimentazione, che di solito ha una sola barra verticale.
    """
    x1, y1, x2, y2 = _clamp_bbox_to_image(box, image_gray.shape)
    width = max(x2 - x1 + 1, 1)
    height = max(y2 - y1 + 1, 1)

    if width < 48 or height < 48:
        return False

    roi = image_gray[y1:y2 + 1, x1:x2 + 1]
    if roi.size == 0:
        return False

    # binarizzazione semplice del simbolo
    _, roi_bin = cv2.threshold(roi, 210, 255, cv2.THRESH_BINARY_INV)

    # togli un po' di bordo per non farti influenzare troppo dai fili esterni
    margin_x = max(2, int(round(width * 0.06)))
    margin_y = max(2, int(round(height * 0.12)))
    core = roi_bin[margin_y:height - margin_y, margin_x:width - margin_x]
    if core.size == 0:
        return False

    # proiezione per colonne: le barre verticali del mosfet devono emergere bene
    col_proj = (core > 0).sum(axis=0).tolist()
    if not col_proj:
        return False

    min_col = max(8, int(round(core.shape[0] * 0.28)))
    groups = _group_close_indices(
        [i for i, v in enumerate(col_proj) if int(v) >= min_col],
        max_gap=max(2, int(round(core.shape[1] * 0.03))),
    )

    centers = []
    max_group_width = max(2, int(round(core.shape[1] * 0.16)))
    for g in groups:
        gwidth = g[-1] - g[0] + 1
        if gwidth > max_group_width:
            continue
        centers.append(int(round((g[0] + g[-1]) / 2.0)))

    centers = _merge_close_values(
        sorted(centers),
        min_gap=max(6, int(round(core.shape[1] * 0.08))),
    )

    # il mosfet deve avere almeno 2 barre verticali interne
    if len(centers) < 2:
        return False

    span = centers[-1] - centers[0]
    if span < max(10, int(round(core.shape[1] * 0.14))):
        return False

    return True


# Riconosce bbox compatibili con simboli switch-like.
def is_switch_like_bbox(image_gray, box) -> bool:
    x1, y1, x2, y2 = _clamp_bbox_to_image(box, image_gray.shape)
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)

    # Alcuni switch del batch v9.2 hanno bbox quasi quadrati o perfino piu alti
    # che larghi: il segnale decisivo resta la presenza dei due contatti circolari.
    if max(width, height) < 75 or min(width, height) < 35:
        return False

    circle_count = _count_hough_circles(
        image_gray,
        box,
        min_dist=max(22, int(round(width * 0.28))),
        param1=80,
        param2=13,
        min_radius=7,
        max_radius=22,
    )
    if circle_count < 2:
        return False

    roi = image_gray[y1:y2 + 1, x1:x2 + 1]
    _, roi_binary = cv2.threshold(roi, 200, 255, cv2.THRESH_BINARY_INV)
    num_labels, _, stats, _ = cv2.connectedComponentsWithStats(roi_binary, connectivity=8)
    min_component_area = max(80, int(round(width * height * 0.018)))
    large_components = [
        int(stats[idx, cv2.CC_STAT_AREA])
        for idx in range(1, num_labels)
        if int(stats[idx, cv2.CC_STAT_AREA]) >= min_component_area
    ]
    return len(large_components) >= 2


def is_push_button_like_bbox(image_binary, box) -> bool:
    """Riconosce push button compatti come lama/attuatore + due contatti separati."""
    x1, y1, x2, y2 = _clamp_bbox_to_image(box, image_binary.shape)
    width = max(x2 - x1 + 1, 1)
    height = max(y2 - y1 + 1, 1)

    if max(width, height) < 55 or min(width, height) < 18:
        return False

    roi = image_binary[y1:y2 + 1, x1:x2 + 1]
    if roi.size == 0:
        return False

    num_labels, _, stats, centroids = cv2.connectedComponentsWithStats(roi, connectivity=8)
    min_component_area = max(70, int(round(width * height * 0.035)))

    components = []
    for idx in range(1, num_labels):
        area = int(stats[idx, cv2.CC_STAT_AREA])
        if area < min_component_area:
            continue
        comp_w = int(stats[idx, cv2.CC_STAT_WIDTH])
        comp_h = int(stats[idx, cv2.CC_STAT_HEIGHT])
        components.append(
            {
                "area": area,
                "x": int(stats[idx, cv2.CC_STAT_LEFT]),
                "y": int(stats[idx, cv2.CC_STAT_TOP]),
                "w": comp_w,
                "h": comp_h,
                "cx": float(centroids[idx][0]),
                "cy": float(centroids[idx][1]),
                "aspect": max(comp_w, comp_h) / float(max(min(comp_w, comp_h), 1)),
            }
        )

    if len(components) < 3 or len(components) > 4:
        return False

    vertical_candidates = [
        comp
        for comp in components
        if comp["h"] >= max(34, int(round(height * 0.48)))
        and comp["h"] / float(max(comp["w"], 1)) >= 2.2
    ]
    horizontal_candidates = [
        comp
        for comp in components
        if comp["w"] >= max(34, int(round(width * 0.48)))
        and comp["w"] / float(max(comp["h"], 1)) >= 2.2
    ]

    def _compact_contacts_ok(actuator, contacts, orientation):
        compact = [
            comp
            for comp in contacts
            if comp["aspect"] <= 2.6
            and comp["area"] >= max(55, int(round(width * height * 0.025)))
        ]
        if len(compact) != 2:
            return False

        if orientation == "vertical":
            same_side_right = all(comp["cx"] >= actuator["cx"] + width * 0.12 for comp in compact)
            same_side_left = all(comp["cx"] <= actuator["cx"] - width * 0.12 for comp in compact)
            if not (same_side_right or same_side_left):
                return False
            if abs(compact[0]["cx"] - compact[1]["cx"]) > max(12, int(round(width * 0.20))):
                return False
            top = min(compact, key=lambda item: item["cy"])
            bottom = max(compact, key=lambda item: item["cy"])
            if bottom["cy"] - top["cy"] < max(20, height * 0.28):
                return False
            return (
                top["cy"] <= actuator["cy"] - height * 0.12
                and bottom["cy"] >= actuator["cy"] + height * 0.12
            )

        same_side_bottom = all(comp["cy"] >= actuator["cy"] + height * 0.12 for comp in compact)
        same_side_top = all(comp["cy"] <= actuator["cy"] - height * 0.12 for comp in compact)
        if not (same_side_bottom or same_side_top):
            return False
        if abs(compact[0]["cy"] - compact[1]["cy"]) > max(12, int(round(height * 0.20))):
            return False
        left = min(compact, key=lambda item: item["cx"])
        right = max(compact, key=lambda item: item["cx"])
        if right["cx"] - left["cx"] < max(20, width * 0.28):
            return False
        return (
            left["cx"] <= actuator["cx"] - width * 0.12
            and right["cx"] >= actuator["cx"] + width * 0.12
        )

    for actuator in vertical_candidates:
        contacts = [comp for comp in components if comp is not actuator]
        if _compact_contacts_ok(actuator, contacts, "vertical"):
            return True

    for actuator in horizontal_candidates:
        contacts = [comp for comp in components if comp is not actuator]
        if _compact_contacts_ok(actuator, contacts, "horizontal"):
            return True

    return False

# Riconosce bbox compatibili con simboli memristor-like.
def is_memristor_like_bbox(image_binary, box) -> bool:
    x1, y1, x2, y2 = _clamp_bbox_to_image(box, image_binary.shape)
    width = max(x2 - x1 + 1, 1)
    height = max(y2 - y1 + 1, 1)
    ratio = height / float(width)

    if not (28 <= width <= 70 and height >= 140 and ratio >= 2.8):
        return False

    roi = image_binary[y1:y2 + 1, x1:x2 + 1]
    side_band = max(2, int(round(width * 0.18)))
    top_band = max(2, int(round(height * 0.10)))

    left_density = cv2.countNonZero(roi[:, :side_band]) / float(max(roi[:, :side_band].size, 1))
    right_density = cv2.countNonZero(roi[:, -side_band:]) / float(max(roi[:, -side_band:].size, 1))
    top_density = cv2.countNonZero(roi[:top_band, :]) / float(max(roi[:top_band, :].size, 1))

    cy1 = int(round(height * 0.20))
    cy2 = int(round(height * 0.80))
    cx1 = int(round(width * 0.25))
    cx2 = int(round(width * 0.75))
    center_roi = roi[cy1:cy2, cx1:cx2]
    center_density = cv2.countNonZero(center_roi) / float(max(center_roi.size, 1))

    component_areas = _component_areas_in_box(image_binary, box)
    dominant_area = component_areas[0] if component_areas else 0

    return (
        left_density >= 0.16
        and right_density >= 0.10
        and top_density >= 0.18
        and center_density >= 0.22
        and len(component_areas) <= 2
        and dominant_area >= int(round(width * height * 0.22))
    )

#DIODI
def _extract_plate_peaks(projection, orthogonal_span):
    """Estrae i due picchi principali associati alle piastre di battery/capacitor."""
    if projection is None or len(projection) == 0:
        return []

    max_value = int(max(int(v) for v in projection))
    if max_value <= 0:
        return []

    threshold = max(3, int(round(float(max_value) * 0.35)))
    groups = _group_close_indices(
        [idx for idx, score in enumerate(projection) if int(score) >= threshold],
        max_gap=3,
    )

    max_thickness = max(10, int(round(len(projection) * 0.18)))
    min_score = max(6, int(round(float(orthogonal_span) * 0.10)))

    peaks = []
    for group in groups:
        thickness = group[-1] - group[0] + 1
        if thickness > max_thickness:
            continue

        avg_score = sum(int(projection[idx]) for idx in group) / float(len(group))
        if avg_score < min_score:
            continue

        peaks.append({
            "center": int(round((group[0] + group[-1]) / 2.0)),
            "score": float(avg_score),
            "thickness": int(thickness),
        })

    return sorted(peaks, key=lambda item: item["score"], reverse=True)


def classify_plate_symbol(image_binary, box):
    """Distingue Battery da Capacitor misurando la differenza tra le due piastre principali."""
    x1, y1, x2, y2 = _clamp_bbox_to_image(box, image_binary.shape)
    width = max(x2 - x1 + 1, 1)
    height = max(y2 - y1 + 1, 1)
    roi = image_binary[y1:y2 + 1, x1:x2 + 1]

    row_projection = (roi > 0).sum(axis=1).tolist()
    col_projection = (roi > 0).sum(axis=0).tolist()

    row_peaks = _extract_plate_peaks(row_projection, width)
    col_peaks = _extract_plate_peaks(col_projection, height)

    candidates = []
    if len(row_peaks) >= 2:
        candidates.append(("rows", row_peaks))
    if len(col_peaks) >= 2:
        candidates.append(("cols", col_peaks))
    if not candidates:
        return None

    _, selected_peaks = max(
        candidates,
        key=lambda item: float(item[1][0]["score"]) + float(item[1][1]["score"]),
    )

    peak_scores = [float(peak["score"]) for peak in selected_peaks]
    top_score = float(peak_scores[0])
    second_score = float(peak_scores[1])

    # Le batterie multisezione hanno piu picchi paralleli con due famiglie di lunghezze
    # (piastre lunghe e piastre corte), a differenza dei capacitor con due piastre uguali.
    if len(peak_scores) >= 4:
        strong_count = sum(1 for score in peak_scores if score >= top_score * 0.85)
        weak_count = sum(1 for score in peak_scores if score <= top_score * 0.70)
        if strong_count >= 2 and weak_count >= 2:
            return "Battery"

    ratio = max(top_score, second_score) / float(
        max(min(top_score, second_score), 1e-6)
    )
    if ratio >= 1.22:
        return "Battery"
    if ratio <= 1.10:
        return "Capacitor"
    return None


def is_led_like_diode_box(image_binary, box) -> bool:
    """Riconosce due marker luminosi staccati e coerenti con un LED.

    Le sole componenti connesse vicine non bastano: lettere, valori e tratti
    dei rami possono produrre lo stesso conteggio. I due marker devono quindi
    essere compatti, sufficientemente pieni, simili tra loro e collocati
    dalla stessa parte del corpo del diodo.
    """
    x1, y1, x2, y2 = _clamp_bbox_to_image(box, image_binary.shape)
    h, w = image_binary.shape[:2]

    pad = 22
    ex1 = max(0, x1 - pad)
    ey1 = max(0, y1 - pad)
    ex2 = min(w - 1, x2 + pad)
    ey2 = min(h - 1, y2 + pad)

    roi = image_binary[ey1:ey2 + 1, ex1:ex2 + 1]
    if roi.size == 0:
        return False

    # bbox originale dentro la ROI allargata
    ox1 = x1 - ex1
    oy1 = y1 - ey1
    ox2 = x2 - ex1
    oy2 = y2 - ey1

    # un piccolo margine per considerare "corpo del diodo"
    core_margin = 4
    cx1 = max(0, ox1 - core_margin)
    cy1 = max(0, oy1 - core_margin)
    cx2 = min(roi.shape[1] - 1, ox2 + core_margin)
    cy2 = min(roi.shape[0] - 1, oy2 + core_margin)

    num_labels, _, stats, _ = cv2.connectedComponentsWithStats(roi, connectivity=8)
    if num_labels <= 1:
        return False

    core_cx = (ox1 + ox2) / 2.0
    core_cy = (oy1 + oy2) / 2.0
    core_w = max(ox2 - ox1 + 1, 1)
    core_h = max(oy2 - oy1 + 1, 1)

    detached_markers = []

    for idx in range(1, num_labels):
        sx = int(stats[idx, cv2.CC_STAT_LEFT])
        sy = int(stats[idx, cv2.CC_STAT_TOP])
        sw = int(stats[idx, cv2.CC_STAT_WIDTH])
        sh = int(stats[idx, cv2.CC_STAT_HEIGHT])
        area = int(stats[idx, cv2.CC_STAT_AREA])

        # Componenti piccole/medie, non il simbolo principale.
        if not (12 <= area <= 260):
            continue

        sx2 = sx + sw - 1
        sy2 = sy + sh - 1

        # deve essere staccata dal corpo del diodo
        intersects_core = not (sx2 < cx1 or sx > cx2 or sy2 < cy1 or sy > cy2)
        if intersects_core:
            continue

        comp_cx = (sx + sx2) / 2.0
        comp_cy = (sy + sy2) / 2.0
        dx = comp_cx - core_cx
        dy = comp_cy - core_cy

        aspect = max(sw, sh) / float(max(1, min(sw, sh)))
        fill_ratio = area / float(max(1, sw * sh))

        # Le punte piene delle frecce occupano una parte consistente del bbox.
        # Conserviamo anche il formato storico con due tratti molto sottili e
        # allungati, ma le due forme non possono essere mescolate nella coppia.
        compact_marker = min(sw, sh) >= 5 and fill_ratio >= 0.45
        thin_marker = min(sw, sh) >= 2 and aspect >= 4.0 and area >= 20
        if not compact_marker and not thin_marker:
            continue

        # Due modalita' valide:
        # 1) tratti obliqui/laterali ben allungati;
        # 2) due piccole componenti staccate sopra il diodo, tipiche
        #    delle frecce LED rasterizzate quasi quadrate.
        lateral_arrow = abs(dx) >= core_w * 0.35 and abs(dy) >= core_h * 0.08 and aspect >= 1.2
        upper_led_marker = abs(dx) >= core_w * 0.10 and dy <= -core_h * 0.35 and aspect >= 0.9

        if not (lateral_arrow or upper_led_marker):
            continue

        detached_markers.append(
            {
                "dx": float(dx),
                "dy": float(dy),
                "area": int(area),
                "compact": bool(compact_marker),
                "thin": bool(thin_marker),
            }
        )

    # Una coppia valida deve puntare nella stessa direzione rispetto al diodo
    # e avere dimensioni confrontabili. La similarita' angolare evita di
    # scambiare per frecce due frammenti posti ai lati opposti del simbolo.
    for marker_index, first in enumerate(detached_markers):
        for second in detached_markers[marker_index + 1:]:
            direction_dot = first["dx"] * second["dx"] + first["dy"] * second["dy"]
            first_distance = math.hypot(first["dx"], first["dy"])
            second_distance = math.hypot(second["dx"], second["dy"])
            direction_similarity = direction_dot / float(
                max(first_distance * second_distance, 1e-6)
            )
            area_ratio = min(first["area"], second["area"]) / float(
                max(first["area"], second["area"])
            )
            same_marker_family = (
                (first["compact"] and second["compact"])
                or (first["thin"] and second["thin"])
            )
            if (
                same_marker_family
                and direction_similarity >= 0.65
                and area_ratio >= 0.55
            ):
                return True

    return False

# =========================================================
# CONNECTOR E ANALOG METER STRUTTURATI
# =========================================================
# Estrae i centri dei pin da una proiezione monodimensionale.
def _extract_connector_pin_centers(projection, axis_offset, axis_span, max_gap=6):
    if not projection:
        return []

    threshold = max(2, int(round(max(projection) * 0.32)))
    groups = _group_close_indices(
        [i for i, score in enumerate(projection) if score >= threshold],
        max_gap=max_gap,
    )
    centers = [
        axis_offset + int(round((group[0] + group[-1]) / 2.0))
        for group in groups
    ]
    return _merge_close_values(
        sorted(centers),
        min_gap=max(16, int(round(axis_span * 0.10))),
    )

# Fallback: recupera i centri dei pin verticali usando i cerchi interni.
def _find_connector_pin_circle_centers_vertical(image_gray, box):
    x1, y1, x2, y2 = _clamp_bbox_to_image(box, image_gray.shape)
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)

    inset = max(3, int(round(width * 0.08)))
    band_w = max(8, int(round(width * 0.28)))

    candidate_bands = [
        (
            min(x2, x1 + inset),
            min(x2, x1 + inset + band_w),
        ),
        (
            max(x1, x2 - inset - band_w),
            max(x1, x2 - inset),
        ),
    ]

    best_centers = []

    for bx1, bx2 in candidate_bands:
        roi = image_gray[y1:y2 + 1, bx1:bx2 + 1]
        circles = cv2.HoughCircles(
            roi,
            cv2.HOUGH_GRADIENT,
            dp=1.2,
            minDist=max(18, int(round(height * 0.10))),
            param1=80,
            param2=12,
            minRadius=max(6, int(round(width * 0.08))),
            maxRadius=max(18, int(round(width * 0.22))),
        )

        if circles is None:
            continue

        ys = []
        for c in circles[0]:
            cy = float(c[1]) + float(y1)
            ys.append(cy)

        centers = _merge_close_values(
            sorted(ys),
            min_gap=max(18, int(round(height * 0.10))),
        )

        if len(centers) > len(best_centers):
            best_centers = centers

    return best_centers

# Cerca i pin di un connector verticale usando due bande laterali strette.
def _find_connector_pin_centers_vertical(image_binary, box):
    x1, y1, x2, y2 = _clamp_bbox_to_image(box, image_binary.shape)
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)

    inset = max(3, int(round(width * 0.08)))
    band_w = max(4, int(round(width * 0.20)))

    candidate_bands = [
        (
            min(x2, x1 + inset),
            min(x2, x1 + inset + band_w),
        ),
        (
            max(x1, x2 - inset - band_w),
            max(x1, x2 - inset),
        ),
    ]

    best_centers = []
    for bx1, bx2 in candidate_bands:
        projection = [
            int(cv2.countNonZero(image_binary[y:y + 1, bx1:bx2 + 1]))
            for y in range(y1, y2 + 1)
        ]
        centers = _extract_connector_pin_centers(projection, y1, height, max_gap=6)
        if len(centers) > len(best_centers):
            best_centers = centers

    return best_centers

# Se vengono trovati piu di 3 centri, sceglie la tripletta piu plausibile.
def _pick_best_three_centers(centers):
    values = sorted(int(v) for v in centers)
    if len(values) <= 3:
        return values

    best_triplet = values[:3]
    best_score = None

    for i in range(len(values) - 2):
        triplet = values[i:i + 3]
        reg = _connector_spacing_regularity(triplet)
        span = float(triplet[-1] - triplet[0])

        # meglio regolarità bassa, meglio span grande
        score = (reg, -span)

        if best_score is None or score < best_score:
            best_score = score
            best_triplet = triplet

    return best_triplet


# Cerca i pin di un connector orizzontale usando due bande superiore/inferiore.
def _find_connector_pin_centers_horizontal(image_binary, box):
    x1, y1, x2, y2 = _clamp_bbox_to_image(box, image_binary.shape)
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)

    side_band = max(6, int(round(height * 0.36)))

    candidate_bands = [
        (y1, min(y2, y1 + side_band)),                  # lato alto
        (max(y1, y2 - side_band), y2),                  # lato basso
    ]

    best_centers = []
    for by1, by2 in candidate_bands:
        projection = [
            int(cv2.countNonZero(image_binary[by1:by2 + 1, x:x + 1]))
            for x in range(x1, x2 + 1)
        ]
        centers = _extract_connector_pin_centers(projection, x1, width, max_gap=6)
        if len(centers) > len(best_centers):
            best_centers = centers

    return best_centers


# Misura quanto la spaziatura dei pin e regolare.
def _connector_spacing_regularity(centers):
    if len(centers) <= 2:
        return 0.0

    diffs = [
        float(centers[i + 1] - centers[i])
        for i in range(len(centers) - 1)
        if float(centers[i + 1] - centers[i]) > 0.0
    ]
    if not diffs:
        return 1.0

    mean_diff = sum(diffs) / float(len(diffs))
    variance = sum((d - mean_diff) ** 2 for d in diffs) / float(len(diffs))
    std_diff = math.sqrt(max(variance, 0.0))
    return std_diff / float(max(mean_diff, 1e-6))


# Conta i cerchi interni al connector con parametri adattivi.
def _count_connector_circles(image_gray, box):
    x1, y1, x2, y2 = _clamp_bbox_to_image(box, image_gray.shape)
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)
    min_side = max(12, min(width, height))

    return _count_hough_circles(
        image_gray,
        box,
        min_dist=max(16, int(round(min_side * 0.22))),
        param1=80,
        param2=13,
        min_radius=max(5, int(round(min_side * 0.08))),
        max_radius=max(14, int(round(min_side * 0.24))),
    )


# Descrive il layout del connector e decide se il bbox e plausibile.
def get_connector_layout(image_binary, box, image_gray=None):
    x1, y1, x2, y2 = _clamp_bbox_to_image(box, image_binary.shape)
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)
    short_side = min(width, height)
    long_side = max(width, height)

    # Supporta sia connector molto allungati sia alcuni connector compatti
    # che hanno pin interni regolari in un box piccolo quasi quadrato.
    elongation = long_side / float(max(short_side, 1))

    vertical_centers = _find_connector_pin_centers_vertical(image_binary, box)
    horizontal_centers = _find_connector_pin_centers_horizontal(image_binary, box)

    vertical_circle_centers = []
    if image_gray is not None and len(vertical_centers) < 3:
        vertical_circle_centers = _find_connector_pin_circle_centers_vertical(image_gray, box)
        if len(vertical_circle_centers) > len(vertical_centers):
            vertical_centers = vertical_circle_centers

    vertical_reg = _connector_spacing_regularity(vertical_centers)
    horizontal_reg = _connector_spacing_regularity(horizontal_centers)

    circle_count = 0
    if image_gray is not None:
        circle_count = _count_connector_circles(image_gray, box)

    compact_vertical_ok = (
        elongation < 1.35
        and short_side <= 95
        and long_side <= 130
        and 4 <= len(vertical_centers) <= 6
        and vertical_reg <= 0.18
        and circle_count >= max(6, len(vertical_centers) + 2)
    )

    compact_horizontal_ok = (
        elongation < 1.35
        and short_side <= 95
        and long_side <= 130
        and 4 <= len(horizontal_centers) <= 6
        and horizontal_reg <= 0.18
        and circle_count >= max(6, len(horizontal_centers) + 2)
    )

    if compact_vertical_ok and (not compact_horizontal_ok or len(vertical_centers) >= len(horizontal_centers)):
        return {
            "is_connector": True,
            "orientation": "vertical",
            "pin_count": len(vertical_centers),
            "pin_centers": vertical_centers,
            "regularity": vertical_reg,
            "circle_count": circle_count,
        }

    if compact_horizontal_ok:
        return {
            "is_connector": True,
            "orientation": "horizontal",
            "pin_count": len(horizontal_centers),
            "pin_centers": horizontal_centers,
            "regularity": horizontal_reg,
            "circle_count": circle_count,
        }

    if elongation < 1.35:
        return {
            "is_connector": False,
            "orientation": None,
            "pin_count": 0,
            "pin_centers": [],
            "regularity": 1.0,
            "circle_count": circle_count,
        }

    vertical_ok = (
        3 <= len(vertical_centers) <= 6
        and vertical_reg <= 0.34
        and (
            height >= width * 1.20
            or (
                height >= width * 0.90
                and circle_count >= max(3, len(vertical_centers) - 1)
            )
        )
    )

    horizontal_ok = (
        3 <= len(horizontal_centers) <= 6
        and horizontal_reg <= 0.34
        and (
            width >= height * 1.20
            or (
                width >= height * 0.90
                and circle_count >= max(3, len(horizontal_centers) - 1)
            )
        )
    )

    # -------------------------------------------------
    # Fallback rilassato: connector verticale stretto con 3 pin
    # -------------------------------------------------
    if not vertical_ok:
        relaxed_three_pin_centers = []

        if len(vertical_centers) >= 3:
            relaxed_three_pin_centers = _pick_best_three_centers(vertical_centers)
        elif len(vertical_circle_centers) >= 3:
            relaxed_three_pin_centers = _pick_best_three_centers(vertical_circle_centers)

        if relaxed_three_pin_centers:
            relaxed_reg = _connector_spacing_regularity(relaxed_three_pin_centers)

            vertical_three_pin_relaxed = (
                height >= width * 2.4
                and width <= 130
                and circle_count >= 8
                and len(relaxed_three_pin_centers) == 3
                and relaxed_reg <= 0.65
            )

            if vertical_three_pin_relaxed:
                return {
                    "is_connector": True,
                    "orientation": "vertical",
                    "pin_count": len(relaxed_three_pin_centers),
                    "pin_centers": relaxed_three_pin_centers,
                    "regularity": relaxed_reg,
                    "circle_count": circle_count,
                }

    if vertical_ok and (not horizontal_ok or len(vertical_centers) >= len(horizontal_centers)):
        return {
            "is_connector": True,
            "orientation": "vertical",
            "pin_count": len(vertical_centers),
            "pin_centers": vertical_centers,
            "regularity": vertical_reg,
            "circle_count": circle_count,
        }

    if horizontal_ok:
        return {
            "is_connector": True,
            "orientation": "horizontal",
            "pin_count": len(horizontal_centers),
            "pin_centers": horizontal_centers,
            "regularity": horizontal_reg,
            "circle_count": circle_count,
        }

    return {
        "is_connector": False,
        "orientation": None,
        "pin_count": 0,
        "pin_centers": [],
        "regularity": 1.0,
        "circle_count": circle_count,
    }


def is_analog_meter_like_bbox(image_binary, box) -> bool:
    """Verifica se un bbox assomiglia a un meter analogico quadrato del batch v9.1."""
    x1, y1, x2, y2 = _clamp_bbox_to_image(box, image_binary.shape)
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)
    ratio = width / float(height)

    if min(width, height) < 90 or not (0.68 <= ratio <= 1.42):
        return False

    band = max(2, int(round(min(width, height) * 0.06)))

    top = cv2.countNonZero(image_binary[y1:y1 + band, x1:x2 + 1])
    bottom = cv2.countNonZero(image_binary[y2 - band + 1:y2 + 1, x1:x2 + 1])
    left = cv2.countNonZero(image_binary[y1:y2 + 1, x1:x1 + band])
    right = cv2.countNonZero(image_binary[y1:y2 + 1, x2 - band + 1:x2 + 1])

    top_density = top / float(max((x2 - x1 + 1) * band, 1))
    bottom_density = bottom / float(max((x2 - x1 + 1) * band, 1))
    left_density = left / float(max((y2 - y1 + 1) * band, 1))
    right_density = right / float(max((y2 - y1 + 1) * band, 1))

    cx1 = x1 + int(round(width * 0.20))
    cx2 = x1 + int(round(width * 0.80))
    cy1 = y1 + int(round(height * 0.18))
    cy2 = y1 + int(round(height * 0.72))
    center_density = cv2.countNonZero(image_binary[cy1:cy2 + 1, cx1:cx2 + 1]) / float(
        max((cx2 - cx1 + 1) * (cy2 - cy1 + 1), 1)
    )

    component_areas = _component_areas_in_box(image_binary, box)

    return (
        min(top_density, bottom_density, left_density, right_density) >= 0.16
        and center_density <= 0.38
        and len(component_areas) <= 6
    )


# =========================================================
# CANDIDATI STRUTTURATI E REMAP CLASSI
# =========================================================
def _dedupe_candidate_boxes(candidates, max_overlap=0.55):
    """Rimuove candidati duplicati tenendo quelli piu plausibili."""
    ordered = sorted(
        candidates,
        key=lambda c: (float(c["score"]), -_bbox_area(c["bbox"])),
        reverse=True,
    )
    kept = []
    for candidate in ordered:
        if any(_bbox_iou(candidate["bbox"], existing["bbox"]) >= max_overlap for existing in kept):
            continue
        kept.append(candidate)
    return kept


# Cerca candidati strutturati aggiuntivi direttamente dal binario.
def find_structured_symbol_candidates(image_gray, image_binary):
    contours, hierarchy = cv2.findContours(
        image_binary,
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE,
    )
    if hierarchy is None:
        return {"Analog_Meter": [], "Connector": []}

    analog_candidates = []
    connector_candidates = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = float(cv2.contourArea(cnt))
        extent = area / float(max(w * h, 1))
        ratio = w / float(max(h, 1))
        box = [float(x), float(y), float(x + w - 1), float(y + h - 1)]

        if w < 40 or h < 40:
            continue

        # -------------------------------------------------
        # Analog meter candidates
        # -------------------------------------------------
        if (
            0.82 <= ratio <= 1.15
            and 145 <= w <= 240
            and 145 <= h <= 240
            and extent >= 0.88
        ):
            circle_count = _count_hough_circles(
                image_gray,
                box,
                min_dist=18,
                param2=14,
                min_radius=7,
                max_radius=22,
            )
            component_areas = _component_areas_in_box(image_binary, box)
            medium_components = [a for a in component_areas[1:] if a >= 80]

            if circle_count >= 5 and len(component_areas) <= 6 and len(medium_components) >= 2:
                analog_candidates.append({
                    "bbox": box,
                    "score": 10.0 * extent + float(circle_count),
                })

        # -------------------------------------------------
        # Connector candidates
        # Supporta sia verticali sia orizzontali
        # -------------------------------------------------
        if (
            min(w, h) >= 45
            and max(w, h) >= 120
            and extent >= 0.72
        ):
            connector_layout = get_connector_layout(
                image_binary,
                box,
                image_gray=image_gray,
            )

            if connector_layout["is_connector"]:
                orientation_bonus = 0.0
                if connector_layout["orientation"] in {"vertical", "horizontal"}:
                    orientation_bonus = 0.4

                regularity_bonus = max(
                    0.0,
                    0.35 - float(connector_layout["regularity"])
                )

                connector_candidates.append({
                    "bbox": box,
                    "score": (
                        10.0 * extent
                        + 0.8 * float(connector_layout["pin_count"])
                        + 0.5 * float(connector_layout["circle_count"])
                        + orientation_bonus
                        + regularity_bonus
                    ),
                })

    return {
        "Analog_Meter": _dedupe_candidate_boxes(analog_candidates),
        "Connector": _dedupe_candidate_boxes(connector_candidates),
    }


def _box_matches_candidate(box, candidate_box, min_iou=0.28, min_ioa=0.55):
    return (
        _bbox_iou(box, candidate_box) >= min_iou
        or _bbox_ioa(box, candidate_box) >= min_ioa
        or _bbox_ioa(candidate_box, box) >= min_ioa
    )


def _ic_can_remap_to_connector(box, connector_layout):
    """Keep IC->Connector remap only for narrow, strongly elongated multipin connectors."""
    if not connector_layout.get("is_connector", False):
        return False

    orientation = connector_layout.get("orientation")
    if orientation not in {"vertical", "horizontal"}:
        return False

    x1, y1, x2, y2 = box
    width = max(float(x2 - x1), 1.0)
    height = max(float(y2 - y1), 1.0)
    short_side = min(width, height)
    long_side = max(width, height)
    elongation = long_side / short_side
    pin_count = int(connector_layout.get("pin_count", 0))
    regularity = float(connector_layout.get("regularity", 1.0))
    circle_count = int(connector_layout.get("circle_count", 0))

    compact_connector_ok = (
        short_side <= 95.0
        and long_side <= 130.0
        and 4 <= pin_count <= 6
        and regularity <= 0.18
        and circle_count >= max(6, pin_count + 2)
    )

    return (
        compact_connector_ok
        or (
            elongation >= 4.0
            and short_side <= 130.0
            and 3 <= pin_count <= 6
        )
    )


def remap_special_component(image_gray, image_binary, box, predicted_class_name: str, structured_candidates):
    """Rimappa alcune classi YOLO verso Connector/Analog_Meter quando la forma locale lo suggerisce chiaramente."""
    connector_candidates = structured_candidates.get("Connector", [])
    analog_candidates = structured_candidates.get("Analog_Meter", [])

    if predicted_class_name == "Integrated_Circuit":
        if any(_box_matches_candidate(box, candidate["bbox"]) for candidate in analog_candidates):
            return "Analog_Meter"
        if is_analog_meter_like_bbox(image_binary, box):
            return "Analog_Meter"
        connector_layout = get_connector_layout(image_binary, box, image_gray=image_gray)
        if (
            any(_box_matches_candidate(box, candidate["bbox"]) for candidate in connector_candidates)
            and _ic_can_remap_to_connector(box, connector_layout)
        ):
            return "Connector"
        if _ic_can_remap_to_connector(box, connector_layout):
            return "Connector"

    if predicted_class_name == "Meter":
        if is_signal_source_like_bbox(image_gray, image_binary, box):
            return "Signal_Source"

    if predicted_class_name in {"Meter", "Integrated_Circuit", "Inductor"}:
        if any(_box_matches_candidate(box, candidate["bbox"]) for candidate in analog_candidates):
            return "Analog_Meter"
        if is_analog_meter_like_bbox(image_binary, box):
            return "Analog_Meter"

    if predicted_class_name in {"Mosfet", "Integrated_Circuit"}:
        if is_memristor_like_bbox(image_binary, box):
            return "Memristor"

    plate_symbol = classify_plate_symbol(image_binary, box)
    if predicted_class_name == "Capacitor" and plate_symbol == "Battery":
        return "Battery"
    if predicted_class_name == "Battery" and plate_symbol == "Capacitor":
        return "Capacitor"
    if predicted_class_name == "Switch" and is_push_button_like_bbox(image_binary, box):
        return "Push_Button"

    if predicted_class_name == "Diode" and is_led_like_diode_box(image_binary, box):
        return "LED"

    return predicted_class_name

# =========================================================
# POST-PROCESSING COMPONENTI
# =========================================================
def _build_component_record(
    class_id,
    class_name,
    model_class_name,
    conf,
    bbox,
    meta,
    source_class_id=None,
    source_class_name=None,
):
    return {
        "class_id": int(class_id),
        "class_name": class_name,
        "model_class_name": model_class_name,
        "source_class_id": source_class_id,
        "source_class_name": source_class_name,
        "conf": round(float(conf), 4),
        "bbox": [
            round(float(bbox[0]), 2),
            round(float(bbox[1]), 2),
            round(float(bbox[2]), 2),
            round(float(bbox[3]), 2),
        ],
        "symbol_type": meta.get("symbol_type"),
        "use_for_terminals": meta.get("use_for_terminals", False),
        "use_for_masking": meta.get("use_for_masking", False),
    }


def add_missing_structured_components(components, structured_candidates, class_meta, class_id_by_name):
    """Aggiunge solo componenti euristici ancora utili: per ora Analog_Meter."""
    target_conf = {
        "Analog_Meter": 0.58,
    }

    updated = list(components)
    analog_candidates = structured_candidates.get("Analog_Meter", [])
    class_name = "Analog_Meter"
    class_id = class_id_by_name.get(class_name)
    if class_id is None:
        return updated

    meta = class_meta.get(class_id, {})
    for candidate in analog_candidates:
        candidate_box = candidate["bbox"]
        already_present = any(
            comp.get("class_name") == class_name
            and _box_matches_candidate(comp.get("bbox", []), candidate_box, min_iou=0.22, min_ioa=0.50)
            for comp in updated
        )
        if already_present:
            continue

        updated.append(
            _build_component_record(
                class_id=class_id,
                class_name=class_name,
                model_class_name=f"heuristic_{class_name}",
                conf=target_conf.get(class_name, 0.5),
                bbox=candidate_box,
                meta=meta,
                source_class_id=None,
                source_class_name="heuristic",
            )
        )
    updated = repair_spst_switch_bank(updated, class_meta, class_id_by_name)
    return updated


def repair_spst_switch_bank(components, class_meta, class_id_by_name):
    """Corregge banchi molto regolari di 4 SPST quando YOLO fonde 3 switch in box larghi.

    L'euristica e' volutamente stretta:
    - 4 resistori verticali piccoli, quasi allineati e quasi equispaziati
    - 3 detection Switch sopra al banco, con box larghi/fusi
    In quel caso sostituiamo i 3 box switch locali con 4 box coerenti centrati
    sulle 4 colonne del banco.
    """
    switch_class_id = class_id_by_name.get("Switch")
    if switch_class_id is None:
        return components

    switch_meta = class_meta.get(switch_class_id, {})
    resistors = [
        comp for comp in components
        if comp.get("class_name") == "Resistor"
    ]
    switches = [
        comp for comp in components
        if comp.get("class_name") == "Switch"
    ]
    if len(resistors) < 4 or len(switches) < 2:
        return components

    vertical_resistors = []
    for comp in resistors:
        box = comp.get("bbox", [])
        if len(box) != 4:
            continue
        x1, y1, x2, y2 = map(float, box)
        w = max(x2 - x1, 1.0)
        h = max(y2 - y1, 1.0)
        if h >= w * 1.7 and 10.0 <= w <= 30.0 and 22.0 <= h <= 60.0:
            vertical_resistors.append(comp)

    if len(vertical_resistors) < 4:
        return components

    sorted_resistors = sorted(vertical_resistors, key=lambda comp: _bbox_center(comp["bbox"])[0])

    for start in range(len(sorted_resistors) - 3):
        bank = sorted_resistors[start:start + 4]
        centers = [_bbox_center(comp["bbox"])[0] for comp in bank]
        gaps = [centers[i + 1] - centers[i] for i in range(3)]
        if min(gaps) <= 0.0:
            continue

        mean_gap = sum(gaps) / 3.0
        if not (18.0 <= mean_gap <= 42.0):
            continue
        if any(abs(gap - mean_gap) > max(4.0, mean_gap * 0.18) for gap in gaps):
            continue

        ys_top = [float(comp["bbox"][1]) for comp in bank]
        ys_bottom = [float(comp["bbox"][3]) for comp in bank]
        if max(ys_top) - min(ys_top) > 6.0 or max(ys_bottom) - min(ys_bottom) > 6.0:
            continue

        bank_x1 = min(float(comp["bbox"][0]) for comp in bank)
        bank_x2 = max(float(comp["bbox"][2]) for comp in bank)
        bank_y1 = min(ys_top)

        local_switches = []
        for comp in switches:
            box = comp.get("bbox", [])
            if len(box) != 4:
                continue
            sx1, _, sx2, sy2 = map(float, box)
            scx, _ = _bbox_center(box)
            if sy2 >= bank_y1 - 40.0:
                continue
            if scx < bank_x1 - mean_gap or scx > bank_x2 + mean_gap:
                continue
            if sx2 - sx1 < 10.0:
                continue
            local_switches.append(comp)

        if len(local_switches) != 3:
            continue

        switch_widths = [float(comp["bbox"][2]) - float(comp["bbox"][0]) for comp in local_switches]
        if max(switch_widths) < mean_gap * 1.25:
            continue

        local_switches_sorted = sorted(local_switches, key=lambda comp: _bbox_center(comp["bbox"])[0])
        switch_y1 = min(float(comp["bbox"][1]) for comp in local_switches_sorted)
        switch_y2 = max(float(comp["bbox"][3]) for comp in local_switches_sorted)
        switch_h = max(switch_y2 - switch_y1, 20.0)
        narrow_w = max(12.0, min(mean_gap * 0.52, switch_h * 0.55))

        bank_set = {id(comp) for comp in local_switches}
        updated = [comp for comp in components if id(comp) not in bank_set]

        for center_x in centers:
            bbox = [
                center_x - narrow_w / 2.0,
                switch_y1,
                center_x + narrow_w / 2.0,
                switch_y2,
            ]
            updated.append(
                _build_component_record(
                    class_id=switch_class_id,
                    class_name="Switch",
                    model_class_name="heuristic_Switch",
                    conf=0.58,
                    bbox=bbox,
                    meta=switch_meta,
                    source_class_id=None,
                    source_class_name="heuristic",
                )
            )
        return updated

    return components


def suppress_conflicting_components(components, image_binary):
    """Sopprime detection in conflitto scegliendo la classe piu plausibile per alcuni casi noti."""
    suppressed = set()

    for i in range(len(components)):
        if i in suppressed:
            continue
        for j in range(i + 1, len(components)):
            if j in suppressed:
                continue

            comp_a = components[i]
            comp_b = components[j]
            box_a = comp_a["bbox"]
            box_b = comp_b["bbox"]
            overlap = max(
                _bbox_iou(box_a, box_b),
                _bbox_ioa(box_a, box_b),
                _bbox_ioa(box_b, box_a),
            )
            if overlap < 0.42:
                continue

            class_a = comp_a["class_name"]
            class_b = comp_b["class_name"]
            pair = {class_a, class_b}

            if "Analog_Meter" in pair and pair.intersection({"Integrated_Circuit", "Meter", "Inductor"}):
                drop_idx = i if class_a in {"Integrated_Circuit", "Meter", "Inductor"} else j
                suppressed.add(drop_idx)
                continue

            if pair == {"Analog_Meter", "Connector"}:
                analog_idx = i if class_a == "Analog_Meter" else j
                connector_idx = j if analog_idx == i else i
                suppressed.add(connector_idx)
                continue

            if pair == {"Connector", "Integrated_Circuit"}:
                drop_idx = i if class_a == "Integrated_Circuit" else j
                suppressed.add(drop_idx)
                continue

            if pair == {"Transformer", "Inductor"}:
                transformer_idx = i if class_a == "Transformer" else j
                inductor_idx = j if transformer_idx == i else i
                transformer = components[transformer_idx]
                inductor = components[inductor_idx]
                if (
                    float(transformer.get("conf", 0.0)) <= float(inductor.get("conf", 0.0))
                    or overlap >= 0.68
                ):
                    suppressed.add(transformer_idx)
                    continue

            if pair == {"LED", "Diode"}:
                drop_idx = i if class_a == "Diode" else j
                suppressed.add(drop_idx)
                continue

            if pair == {"Fuse", "Switch"}:
                # Il simbolo del fuse puo' essere occasionalmente duplicato come Switch
                # sullo stesso box; in quel caso teniamo il fuse e scartiamo il doppione.
                drop_idx = i if class_a == "Switch" else j
                suppressed.add(drop_idx)
                continue

            if pair == {"Lamp", "Signal_Source"}:
                drop_idx = i if class_a == "Lamp" else j
                suppressed.add(drop_idx)
                continue

            if pair == {"Meter", "Current_Source"}:
                meter_idx = i if class_a == "Meter" else j
                other_idx = j if meter_idx == i else i
                suppressed.add(other_idx)
                continue

            if pair == {"Meter", "Signal_Source"}:
                drop_idx = i if class_a == "Meter" else j
                suppressed.add(drop_idx)
                continue

            if pair == {"Battery", "Capacitor"}:
                plate_class = classify_plate_symbol(
                    image_binary,
                    box_a if comp_a["conf"] >= comp_b["conf"] else box_b,
                )
                if plate_class == "Battery":
                    drop_idx = i if class_a == "Capacitor" else j
                elif plate_class == "Capacitor":
                    drop_idx = i if class_a == "Battery" else j
                else:
                    drop_idx = i if comp_a["conf"] < comp_b["conf"] else j
                suppressed.add(drop_idx)
                continue

            if pair == {"Battery", "Polarized_Capacitor"}:
                drop_idx = i if class_a == "Battery" else j
                suppressed.add(drop_idx)
                continue

            if pair in ({"Battery", "GND"}, {"Capacitor", "GND"}):
                gnd_idx = i if class_a == "GND" else j
                other_idx = j if gnd_idx == i else i
                gnd_box = components[gnd_idx]["bbox"]
                other_box = components[other_idx]["bbox"]
                if _bbox_ioa(gnd_box, other_box) >= 0.72:
                    suppressed.add(gnd_idx)

    return [
        comp for idx, comp in enumerate(components)
        if idx not in suppressed
    ]


def dedupe_overlapping_same_class(components):
    """Elimina duplicati della stessa classe nati da remap o detection molto sovrapposte."""
    suppressed = set()
    ordered = sorted(
        range(len(components)),
        key=lambda idx: float(components[idx].get("conf", 0.0)),
        reverse=True,
    )

    for pos, idx_a in enumerate(ordered):
        if idx_a in suppressed:
            continue

        comp_a = components[idx_a]
        box_a = comp_a.get("bbox", [])
        class_a = comp_a.get("class_name")

        for idx_b in ordered[pos + 1:]:
            if idx_b in suppressed:
                continue

            comp_b = components[idx_b]
            if comp_b.get("class_name") != class_a:
                continue

            box_b = comp_b.get("bbox", [])
            overlap = max(
                _bbox_iou(box_a, box_b),
                _bbox_ioa(box_a, box_b),
                _bbox_ioa(box_b, box_a),
            )
            if overlap >= 0.72:
                suppressed.add(idx_b)

    return [
        comp for idx, comp in enumerate(components)
        if idx not in suppressed
    ]


def suppress_partial_low_conf_mosfet_duplicates(components):
    """Rimuove crop parziali Mosfet prodotti attorno a simboli gia' rilevati.

    Alcune frecce o scritte vicine a un MOSFET possono generare un bbox Mosfet
    largo e poco affidabile che include solo una parte del simbolo reale. Non e'
    abbastanza sovrapposto per la NMS classica, ma ha quasi lo stesso asse X,
    una piccola sovrapposizione verticale e confidenza molto piu' bassa.
    """
    suppressed = set()
    mosfet_indices = [
        idx
        for idx, comp in enumerate(components)
        if comp.get("class_name") == "Mosfet"
    ]

    for idx_low in mosfet_indices:
        low = components[idx_low]
        low_conf = float(low.get("conf", 0.0))
        if low_conf >= 0.50:
            continue

        low_box = low.get("bbox", [])
        if len(low_box) != 4:
            continue

        lx1, ly1, lx2, ly2 = map(float, low_box)
        low_w = max(lx2 - lx1, 1.0)
        low_h = max(ly2 - ly1, 1.0)
        low_cx, low_cy = _bbox_center(low_box)

        for idx_high in mosfet_indices:
            if idx_high == idx_low:
                continue

            high = components[idx_high]
            high_conf = float(high.get("conf", 0.0))
            if high_conf < 0.75 or high_conf <= low_conf:
                continue

            high_box = high.get("bbox", [])
            if len(high_box) != 4:
                continue

            hx1, hy1, hx2, hy2 = map(float, high_box)
            high_w = max(hx2 - hx1, 1.0)
            high_h = max(hy2 - hy1, 1.0)
            high_cx, high_cy = _bbox_center(high_box)

            x_overlap = _axis_overlap_ratio(lx1, lx2, hx1, hx2)
            y_overlap = _axis_overlap_ratio(ly1, ly2, hy1, hy2)
            center_dx = abs(low_cx - high_cx)
            center_dy = abs(low_cy - high_cy)

            partial_same_column = (
                x_overlap >= 0.82
                and 0.06 <= y_overlap <= 0.35
                and center_dx <= 0.18 * max(low_w, high_w)
                and center_dy <= 1.05 * max(low_h, high_h)
            )

            if partial_same_column:
                suppressed.add(idx_low)
                break

    return [
        comp for idx, comp in enumerate(components)
        if idx not in suppressed
    ]


def suppress_nested_terminals(components):
    """Rimuove Terminal rilevati dentro simboli strutturati dove i pallini fanno parte del simbolo."""
    blocking_classes = {"Connector", "Switch", "Analog_Meter", "Meter", "Integrated_Circuit"}
    filtered = []
    for comp in components:
        if comp.get("class_name") != "Terminal":
            filtered.append(comp)
            continue

        term_box = comp.get("bbox", [])
        term_center = _bbox_center(term_box)
        drop = False
        for other in components:
            if other is comp or other.get("class_name") not in blocking_classes:
                continue
            other_box = other.get("bbox", [])
            if _bbox_ioa(term_box, other_box) >= 0.65 or _point_in_box(term_center, other_box):
                drop = True
                break

        if not drop:
            filtered.append(comp)
    return filtered

# =========================================================
# IO, METADATI E HELPERS PIPELINE
# =========================================================
def get_required_confidence(class_name: str) -> float:
    """Restituisce la soglia minima di confidenza da usare per una specifica classe rilevata."""
    return float(CLASS_CONF_THRES.get(class_name, CONF_THRES))


def get_model_inference_confidence(class_meta) -> float:
    """Calcola la confidenza globale di inferenza del modello scegliendo la soglia piu permissiva necessaria tra le classi abilitate."""
    class_names = [meta.get("name", "") for meta in class_meta.values()]
    per_class_thresholds = [get_required_confidence(name) for name in class_names if name]
    if not per_class_thresholds:
        return CONF_THRES
    # Usiamo la soglia minima per non tagliare via in partenza classi che
    # richiedono un threshold piu basso; il filtraggio fine avviene dopo.
    return min([CONF_THRES, *per_class_thresholds])


def is_terminal_detection_valid(image_binary, bbox) -> bool:
    """Verifica se una detection della classe Terminal ha abbastanza evidenza grafica sui lati per essere considerata plausibile."""
    near_scores = get_terminal_class_probe_scores(image_binary, bbox)
    far_scores = get_terminal_class_far_probe_scores(image_binary, bbox)

    # Il contributo lontano pesa meno: serve come conferma, non come segnale principale.
    combined = {
        side: float(near_scores.get(side, 0)) + 0.8 * float(far_scores.get(side, 0))
        for side in ("top", "bottom", "left", "right")
    }
    ordered = sorted(combined.items(), key=lambda kv: kv[1], reverse=True)
    best_score = ordered[0][1]
    second_score = ordered[1][1]

    return (
        best_score >= 18.0
        or (best_score >= 10.0 and second_score >= 5.0)
    )


def is_border_supply_terminal_candidate(image_binary, bbox, image_shape) -> bool:
    """Accetta Terminal esterni deboli, inclusi piccoli jack a due contatti."""
    x1, y1, x2, y2 = _clamp_bbox_to_image(bbox, image_shape)
    h, w = image_shape[:2]
    border_margin = 28

    touches_border = (
        y1 <= border_margin
        or y2 >= h - 1 - border_margin
        or x1 <= border_margin
        or x2 >= w - 1 - border_margin
    )
    if not touches_border:
        return False

    if not is_terminal_detection_valid(image_binary, bbox):
        return False

    width = max(1, x2 - x1 + 1)
    height = max(1, y2 - y1 + 1)
    area = width * height
    if area > 1600:
        # Il vecchio limite compatto resta valido per i morsetti a un solo
        # contatto. Un jack sul bordo puo' essere un po' piu' grande, ma deve
        # mostrare due lati connessi in modo netto per non recuperare simboli
        # interni rumorosi classificati come Terminal a bassa confidenza.
        near_scores = get_terminal_class_probe_scores(image_binary, bbox)
        far_scores = get_terminal_class_far_probe_scores(image_binary, bbox)
        combined_scores = {
            side: float(near_scores.get(side, 0))
            + 0.8 * float(far_scores.get(side, 0))
            for side in ("top", "bottom", "left", "right")
        }
        strong_sides = sum(score >= 18.0 for score in combined_scores.values())
        if area > 2800 or strong_sides < 2:
            return False

    return True


def load_class_metadata(class_terminals_path: Path):
    """Carica i metadati delle classi e prepara gli insiemi di classi usate per detection, terminali e masking."""
    data = load_yaml(class_terminals_path)

    class_meta = {}
    for k, v in data.items():
        class_id = int(k)
        class_meta[class_id] = v

    detect_class_ids = sorted(class_meta.keys())
    terminal_class_ids = sorted([
        cid for cid, meta in class_meta.items()
        if meta.get("use_for_terminals", False)
    ])
    masking_class_ids = sorted([
        cid for cid, meta in class_meta.items()
        if meta.get("use_for_masking", False)
    ])

    return class_meta, detect_class_ids, terminal_class_ids, masking_class_ids


def normalize_model_names(model_names):
    """Normalizza il mapping dei nomi classe del modello in un dizionario indicizzato per class_id."""
    if isinstance(model_names, list):
        return {i: name for i, name in enumerate(model_names)}

    if isinstance(model_names, dict):
        return {int(k): v for k, v in model_names.items()}

    raise TypeError("Formato model.names non riconosciuto.")


def get_input_images():
    """Raccoglie e ordina le immagini di input che verranno processate in questo step."""
    if not INPUT_IMAGES_DIR.exists():
        raise FileNotFoundError(f"Cartella immagini non trovata: {INPUT_IMAGES_DIR}")

    images = sorted([
        p for p in INPUT_IMAGES_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS
    ])

    # Lo stesso filtro e' condiviso con gli step 03-05. Se non viene
    # configurato, il comportamento storico sul batch completo non cambia.
    if PIPELINE_IMAGE_IDS:
        images = [path for path in images if path.stem in PIPELINE_IMAGE_IDS]

    if not images:
        requested = ", ".join(sorted(PIPELINE_IMAGE_IDS))
        filter_detail = f" per PIPELINE_IMAGE_IDS={requested}" if requested else ""
        raise FileNotFoundError(
            f"Nessuna immagine trovata in: {INPUT_IMAGES_DIR}{filter_detail}"
        )

    return images


# =========================================================
# DEBUG VISIVO
# =========================================================
def draw_components(image_bgr, components):
    out = image_bgr.copy()
    box_color = (220, 170, 40)
    text_color = (35, 35, 35)
    label_bg_color = (245, 245, 245)
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.46
    font_thickness = 1
    box_thickness = 2
    padding_x = 5
    padding_y = 4

    for comp in components:
        x1, y1, x2, y2 = comp["bbox"]
        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])

        class_id = comp["class_id"]
        class_name = comp["class_name"]
        conf = comp["conf"]

        if comp.get("use_for_terminals", False):
            suffix = "T"
        elif comp.get("use_for_masking", False):
            suffix = "M"
        else:
            suffix = "-"

        label = f"{class_id} | {class_name} | {conf:.2f} | {suffix}"

        cv2.rectangle(out, (x1, y1), (x2, y2), box_color, box_thickness)

        (text_w, text_h), baseline = cv2.getTextSize(label, font, font_scale, font_thickness)
        label_x1 = max(0, x1)
        label_y2 = max(text_h + 2 * padding_y + baseline, y1)
        label_y1 = max(0, label_y2 - (text_h + 2 * padding_y + baseline))
        label_x2 = min(out.shape[1] - 1, label_x1 + text_w + 2 * padding_x)

        overlay = out.copy()
        cv2.rectangle(overlay, (label_x1, label_y1), (label_x2, label_y2), label_bg_color, -1)
        cv2.addWeighted(overlay, 0.88, out, 0.12, 0, out)
        cv2.rectangle(out, (label_x1, label_y1), (label_x2, label_y2), box_color, 1)
        cv2.putText(
            out,
            label,
            (label_x1 + padding_x, label_y2 - baseline - padding_y),
            font,
            font_scale,
            text_color,
            font_thickness,
            cv2.LINE_AA,
        )

    return out

# =========================================================
# CORE PIPELINE
# =========================================================
def predict_components_on_image(
    image_path: Path,
    model,
    detect_class_ids,
    model_names,
    class_meta
):
    """Esegue la detection su una singola immagine e costruisce il JSON con i componenti filtrati."""
    image_bgr = cv2.imread(str(image_path))
    if image_bgr is None:
        raise ValueError(f"Impossibile leggere l'immagine: {image_path}")

    image_h, image_w = image_bgr.shape[:2]
    image_gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    image_binary = img_build_foreground_binary(image_bgr)
    structured_candidates = find_structured_symbol_candidates(image_gray, image_binary)

    results = model.predict(
        source=str(image_path),
        imgsz=IMG_SIZE,
        conf=get_model_inference_confidence(class_meta),
        iou=IOU_THRES,
        classes=detect_class_ids,
        verbose=False
    )

    result = results[0]
    components = []
    class_id_by_name = {
        meta.get("name"): cid
        for cid, meta in class_meta.items()
        if meta.get("name")
    }

    if result.boxes is not None and len(result.boxes) > 0:
        xyxy = result.boxes.xyxy.cpu().numpy()
        cls = result.boxes.cls.cpu().numpy()
        confs = result.boxes.conf.cpu().numpy()

        for box, class_id, conf in zip(xyxy, cls, confs):
            x1, y1, x2, y2 = box
            class_id = int(class_id)

            original_meta = class_meta.get(class_id, {})
            original_yaml_class_name = original_meta.get("name", f"class_{class_id}")
            model_class_name = model_names.get(class_id, f"class_{class_id}")

            remapped_class_name = remap_special_component(
                image_gray,
                image_binary,
                box,
                original_yaml_class_name,
                structured_candidates,
            )
            effective_class_id = class_id_by_name.get(remapped_class_name, class_id)
            meta = class_meta.get(effective_class_id, original_meta)
            yaml_class_name = meta.get("name", remapped_class_name)
            required_conf = get_required_confidence(yaml_class_name)

            if float(conf) < required_conf:
                if not (
                    yaml_class_name == "Terminal"
                    and float(conf) >= 0.05
                    and is_border_supply_terminal_candidate(image_binary, box, image_bgr.shape)
                ):
                    continue

            # La classe Terminal e particolarmente rumorosa: oltre alla confidence
            # richiediamo anche un minimo di struttura grafica coerente.
            if yaml_class_name == "Terminal" and not is_terminal_detection_valid(image_binary, box):
                continue

            if yaml_class_name == "Switch":
                switch_shape_ok = is_switch_like_bbox(image_gray, box)
                push_button_shape_ok = is_push_button_like_bbox(image_binary, box)
                if not switch_shape_ok and not push_button_shape_ok:
                    # Manteniamo un fallback per switch atipici ma comunque plausibili,
                    # come alcuni rotary/push switch che il filtro morfologico classico penalizza.
                    if float(conf) < 0.20:
                        continue

            if yaml_class_name == "Battery":
                # I marker di alimentazione sul bordo possono sembrare piccole battery
                # al detector, ma senza una vera struttura a piastre non li teniamo.
                if classify_plate_symbol(image_binary, box) != "Battery":
                    continue

            if yaml_class_name == "Mosfet":
                mosfet_shape_ok = is_mosfet_like_bbox(image_gray, box)
                keep_mosfet = mosfet_shape_ok or float(conf) >= 0.78

                if not keep_mosfet:
                    continue

            if yaml_class_name == "LED":
                x1, y1, x2, y2 = expand_led_bbox(box, image_bgr.shape)
            else:
                x1, y1, x2, y2 = box

            components.append({
                "class_id": effective_class_id,
                "class_name": yaml_class_name,
                "model_class_name": model_class_name,
                "source_class_id": class_id,
                "source_class_name": original_yaml_class_name,
                "conf": round(float(conf), 4),
                "bbox": [
                    round(float(x1), 2),
                    round(float(y1), 2),
                    round(float(x2), 2),
                    round(float(y2), 2),
                ],
                "symbol_type": meta.get("symbol_type"),
                "use_for_terminals": meta.get("use_for_terminals", False),
                "use_for_masking": meta.get("use_for_masking", False),
            })

    components = add_missing_structured_components(
        components=components,
        structured_candidates=structured_candidates,
        class_meta=class_meta,
        class_id_by_name=class_id_by_name,
    )
    components = suppress_conflicting_components(components, image_binary)
    components = dedupe_overlapping_same_class(components)
    components = suppress_partial_low_conf_mosfet_duplicates(components)
    components = suppress_nested_terminals(components)

    output_data = {
        "image_id": image_path.stem,
        "image_name": image_path.name,
        "image_path": str(image_path),
        "image_width": image_w,
        "image_height": image_h,
        "detect_class_ids": detect_class_ids,
        "terminal_class_ids": sorted([
            cid for cid, meta in class_meta.items()
            if meta.get("use_for_terminals", False)
        ]),
        "masking_class_ids": sorted([
            cid for cid, meta in class_meta.items()
            if meta.get("use_for_masking", False)
        ]),
        "components": components
    }

    return image_bgr, output_data


def main() -> None:
    """Esegue il punto di ingresso dello step corrente della pipeline."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Modello non trovato: {MODEL_PATH}")

    if not CLASS_TERMINALS_PATH.exists():
        raise FileNotFoundError(f"class_terminals_v1.yaml non trovato: {CLASS_TERMINALS_PATH}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DEBUG_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    class_meta, detect_class_ids, terminal_class_ids, masking_class_ids = load_class_metadata(
        CLASS_TERMINALS_PATH
    )

    print(f"PROJECT_ROOT         : {PROJECT_ROOT}")
    print(f"MODEL_PATH           : {MODEL_PATH}")
    print(f"CLASS_TERMINALS_PATH : {CLASS_TERMINALS_PATH}")
    print(f"INPUT_IMAGES_DIR     : {INPUT_IMAGES_DIR}")
    print(f"OUTPUT_DIR           : {OUTPUT_DIR}")
    if PIPELINE_IMAGE_IDS:
        print(f"PIPELINE_IMAGE_IDS   : {sorted(PIPELINE_IMAGE_IDS)}")
    print(f"DETECT_CLASS_IDS     : {detect_class_ids}")
    print(f"TERMINAL_CLASS_IDS   : {terminal_class_ids}")
    print(f"MASKING_CLASS_IDS    : {masking_class_ids}\n")
    print(f"CONF_THRES           : {CONF_THRES}")
    print(f"CLASS_CONF_THRES     : {CLASS_CONF_THRES}\n")

    model = YOLO(str(MODEL_PATH))
    model_names = normalize_model_names(model.names)

    print("Mapping classi selezionate:")
    for class_id in detect_class_ids:
        yaml_name = class_meta[class_id].get("name", "")
        model_name = model_names.get(class_id, "")
        print(
            f"  {class_id}: yaml='{yaml_name}' | model='{model_name}' | "
            f"terminals={class_meta[class_id].get('use_for_terminals', False)} | "
            f"masking={class_meta[class_id].get('use_for_masking', False)}"
        )
    print()

    input_images = get_input_images()
    print(f"Numero immagini da processare: {len(input_images)}\n")

    for idx, image_path in enumerate(input_images, start=1):
        image_bgr, output_data = predict_components_on_image(
            image_path=image_path,
            model=model,
            detect_class_ids=detect_class_ids,
            model_names=model_names,
            class_meta=class_meta
        )

        out_json_path = OUTPUT_DIR / f"{image_path.stem}.json"
        with open(out_json_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        if SAVE_DEBUG_IMAGES:
            debug_img = draw_components(image_bgr, output_data["components"])
            debug_img_path = DEBUG_IMAGES_DIR / f"{image_path.stem}_detect.jpg"
            cv2.imwrite(str(debug_img_path), debug_img)

        print(
            f"[{idx}/{len(input_images)}] "
            f"{image_path.name} -> {len(output_data['components'])} componenti"
        )

    print("\nCompletato.")
    print(f"JSON salvati in: {OUTPUT_DIR}")
    if SAVE_DEBUG_IMAGES:
        print(f"Immagini debug salvate in: {DEBUG_IMAGES_DIR}")


if __name__ == "__main__":
    main()
