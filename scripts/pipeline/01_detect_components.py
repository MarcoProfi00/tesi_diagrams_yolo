# Per ogni immagine nella cartella di input:
#   1. carica il modello YOLO
#   2. legge metadata/class_terminals_v1.yaml
#   3. seleziona le classi da rilevare
#   4. esegue la detection
#   5. salva un JSON per immagine
#   6. salva un'immagine debug con i bounding box

from pathlib import Path
import os
import json
import yaml
import math
import cv2

from ultralytics import YOLO
from estimate_terminals.io_utils import img_build_foreground_binary
from estimate_terminals.probes import (
    get_terminal_class_far_probe_scores,
    get_terminal_class_probe_scores,
)

# =========================================================
# CONFIGURAZIONE
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PIPELINE_DATASET = os.environ.get("PIPELINE_DATASET", "topology_v9.1_analog_meter_connector_transformer")
PIPELINE_INPUT_BATCH = os.environ.get("PIPELINE_INPUT_BATCH", "batch_v9_1_primo_set_analog_meter_connector_transformer")

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
    "Connector": 0.10,
    "Inductor": 0.30,
    "Lamp": 0.25,
    "Memristor": 0.08,
    "Switch": 0.02,
    "Terminal": 0.35,
    "Transformer": 0.22,
    "Voltage_Source": 0.75,
}

SECONDARY_CLASS_PREDICTION_SPECS = {
    "Diode": {
        "imgsz": 1536,
        "predict_conf": 0.14,
        "accept_conf": 0.14,
    },
    "Connector": {
        "imgsz": 1536,
        "predict_conf": 0.10,
        "accept_conf": 0.16,
    },
}

# === DEBUG ===
SAVE_DEBUG_IMAGES = True

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


# Clamp bounding box to image.
def _clamp_bbox_to_image(box, image_shape):
    h, w = image_shape[:2]
    x1, y1, x2, y2 = box
    x1 = max(0, min(w - 1, int(round(x1))))
    y1 = max(0, min(h - 1, int(round(y1))))
    x2 = max(0, min(w - 1, int(round(x2))))
    y2 = max(0, min(h - 1, int(round(y2))))
    return x1, y1, x2, y2


# Group close indices.
def _group_close_indices(indices, max_gap=1):
    if not indices:
        return []

    groups = [[indices[0]]]
    for idx in indices[1:]:
        if idx <= groups[-1][-1] + max_gap:
            groups[-1].append(idx)
        else:
            groups.append([idx])
    return groups


# Handle merge close values.
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


# Handle bounding box area.
def _bbox_area(box) -> float:
    x1, y1, x2, y2 = box
    return max(0.0, float(x2 - x1)) * max(0.0, float(y2 - y1))


# Calcola l'area di intersezione tra due bounding box.
def _bbox_intersection(box_a, box_b) -> float:
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b
    ix1 = max(float(ax1), float(bx1))
    iy1 = max(float(ay1), float(by1))
    ix2 = min(float(ax2), float(bx2))
    iy2 = min(float(ay2), float(by2))
    return max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)


# Calcola l'IoU tra due bounding box.
def _bbox_iou(box_a, box_b) -> float:
    inter = _bbox_intersection(box_a, box_b)
    if inter <= 0.0:
        return 0.0
    union = _bbox_area(box_a) + _bbox_area(box_b) - inter
    if union <= 0.0:
        return 0.0
    return inter / union


# Calcola l'IoA di un box rispetto a un altro.
def _bbox_ioa(box_inner, box_outer) -> float:
    area_inner = _bbox_area(box_inner)
    if area_inner <= 0.0:
        return 0.0
    return _bbox_intersection(box_inner, box_outer) / area_inner


# Restituisce il centro del bounding box.
def _bbox_center(box):
    x1, y1, x2, y2 = box
    return (float(x1 + x2) / 2.0, float(y1 + y2) / 2.0)


# Verifica se un punto cade dentro il bounding box.
def _point_in_box(point, box) -> bool:
    px, py = point
    x1, y1, x2, y2 = box
    return float(x1) <= float(px) <= float(x2) and float(y1) <= float(py) <= float(y2)


# Conta i cerchi rilevati con Hough in una ROI.
def _count_hough_circles(image_gray, box, min_dist=18, param1=80, param2=14, min_radius=7, max_radius=24):
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


# Allarga leggermente il bbox dei LED per includere le frecce.
def expand_led_bbox(box, image_shape):
    x1, y1, x2, y2 = box
    expanded = [
        float(x1) - 6.0,
        float(y1) - 18.0,
        float(x2) + 30.0,
        float(y2) + 6.0,
    ]
    return _clamp_bbox_to_image(expanded, image_shape)


# Restituisce le aree dei connected components interni al bbox.
def _component_areas_in_box(image_binary, box):
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
# HELPER GEOMETRICI PER CONNECTOR
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

    # Elimina i connector quasi quadrati.
    elongation = max(width, height) / float(max(min(width, height), 1))
    if elongation < 1.35:
        return {
            "is_connector": False,
            "orientation": None,
            "pin_count": 0,
            "pin_centers": [],
            "regularity": 1.0,
            "circle_count": 0,
        }

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


# Wrapper booleano usato nelle regole di remap e soppressione.
def is_connector_like_bbox(image_binary, box, image_gray=None) -> bool:
    layout = get_connector_layout(image_binary, box, image_gray=image_gray)
    return bool(layout["is_connector"])

# =========================================================
# HEURISTICHE DI CLASSE PER SIMBOLI AMBIGUI
# =========================================================

# Verifica se un simbolo circolare/quadrato e un analog meter.
def is_analog_meter_like_bbox(image_binary, box) -> bool:
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


# Handle is memristor like bounding box.
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


# Handle is switch like bounding box.
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


# Handle is switch like bounding box relaxed.
def is_switch_like_bbox_relaxed(image_gray, box) -> bool:
    x1, y1, x2, y2 = _clamp_bbox_to_image(box, image_gray.shape)
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)

    if max(width, height) < 55 or min(width, height) < 28:
        return False

    circle_count = _count_hough_circles(
        image_gray,
        box,
        min_dist=max(18, int(round(width * 0.24))),
        param1=80,
        param2=13,
        min_radius=6,
        max_radius=22,
    )
    if circle_count < 2:
        return False

    roi = image_gray[y1:y2 + 1, x1:x2 + 1]
    edges = cv2.Canny(roi, 50, 150)
    lines = cv2.HoughLinesP(
        edges,
        1,
        math.pi / 180.0,
        threshold=12,
        minLineLength=max(12, int(round(min(width, height) * 0.22))),
        maxLineGap=6,
    )
    if lines is None:
        return False

    for line in lines[:, 0, :]:
        lx1, ly1, lx2, ly2 = map(int, line)
        dx = lx2 - lx1
        dy = ly2 - ly1
        if dx == 0 and dy == 0:
            continue
        angle = abs(math.degrees(math.atan2(dy, dx)))
        angle = min(angle, 180.0 - angle)
        if 22.0 <= angle <= 70.0:
            return True
    return False


# Extract plate peaks.
def _extract_plate_peaks(projection, orthogonal_span):
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


# Classify plate symbol.
def classify_plate_symbol(image_binary, box):
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


# Handle is LED like diode box.
def is_led_like_diode_box(image_binary, box) -> bool:
    orig_x1, orig_y1, orig_x2, orig_y2 = _clamp_bbox_to_image(box, image_binary.shape)
    pad = 18
    h, w = image_binary.shape[:2]
    x1 = max(0, orig_x1 - pad)
    y1 = max(0, orig_y1 - pad)
    x2 = min(w - 1, orig_x2 + pad)
    y2 = min(h - 1, orig_y2 + pad)
    roi = image_binary[y1:y2 + 1, x1:x2 + 1]
    num_labels, _, stats, centroids = cv2.connectedComponentsWithStats(roi, connectivity=8)

    center_x = (orig_x1 + orig_x2) / 2.0
    center_y = (orig_y1 + orig_y2) / 2.0
    width = max(float(orig_x2 - orig_x1), 1.0)
    height = max(float(orig_y2 - orig_y1), 1.0)

    right_side_hits = 0
    upper_side_hits = 0

    for idx in range(1, num_labels):
        area = int(stats[idx, cv2.CC_STAT_AREA])
        if not (40 <= area <= 260):
            continue

        cx = float(centroids[idx][0]) + float(x1)
        cy = float(centroids[idx][1]) + float(y1)

        if cx > float(orig_x2) + 1.0 and abs(cy - center_y) <= height * 0.45:
            right_side_hits += 1
        if cy < float(orig_y1) - 1.0 and abs(cx - center_x) <= width * 0.45:
            upper_side_hits += 1

    return right_side_hits >= 2 or upper_side_hits >= 2


# Handle is voltage source like bounding box.
def is_voltage_source_like_bbox(image_binary, box) -> bool:
    x1, y1, x2, y2 = _clamp_bbox_to_image(box, image_binary.shape)
    roi = image_binary[y1:y2 + 1, x1:x2 + 1]
    h, w = roi.shape[:2]
    if h < 24 or w < 18:
        return False

    cx1 = int(round(w * 0.18))
    cx2 = int(round(w * 0.82))
    cy1 = int(round(h * 0.15))
    cy2 = int(round(h * 0.85))
    inner = roi[cy1:cy2, cx1:cx2]
    if inner.size == 0:
        return False

    num_labels, _, stats, centroids = cv2.connectedComponentsWithStats(inner, connectivity=8)
    small_components = []
    paired_marker_candidates = []
    for idx in range(1, num_labels):
        area = int(stats[idx, cv2.CC_STAT_AREA])
        if 5 <= area <= 120:
            small_components.append({
                "area": area,
                "cy": float(centroids[idx][1]),
            })
        if 16 <= area <= 180:
            comp_w = int(stats[idx, cv2.CC_STAT_WIDTH])
            comp_h = int(stats[idx, cv2.CC_STAT_HEIGHT])
            paired_marker_candidates.append({
                "area": area,
                "cy": float(centroids[idx][1]),
                "width": comp_w,
                "height": comp_h,
            })

    inner_h = float(max(inner.shape[0], 1))
    inner_w = float(max(inner.shape[1], 1))
    has_top = any(comp["cy"] <= inner_h * 0.35 for comp in small_components)
    has_bottom = any(comp["cy"] >= inner_h * 0.55 for comp in small_components)
    if len(small_components) >= 3 and has_top and has_bottom and (num_labels - 1) <= 5:
        return True

    top_candidates = [
        comp for comp in paired_marker_candidates
        if comp["cy"] <= inner_h * 0.35 and comp["width"] >= inner_w * 0.55
    ]
    bottom_candidates = [
        comp for comp in paired_marker_candidates
        if comp["cy"] >= inner_h * 0.55 and comp["width"] >= inner_w * 0.55
    ]
    if len(paired_marker_candidates) != 2 or not top_candidates or not bottom_candidates:
        return False

    top_comp = max(top_candidates, key=lambda comp: comp["area"])
    bottom_comp = max(bottom_candidates, key=lambda comp: comp["area"])
    area_ratio = max(float(top_comp["area"]), float(bottom_comp["area"])) / float(max(min(top_comp["area"], bottom_comp["area"]), 1))
    height_ratio = max(float(top_comp["height"]), float(bottom_comp["height"])) / float(max(min(top_comp["height"], bottom_comp["height"]), 1))
    return area_ratio <= 1.55 and height_ratio <= 1.6

# =========================================================
# CANDIDATI STRUTTURATI ED EURISTICHE DA BINARIO
# =========================================================

# Rimuove candidati strutturati duplicati o troppo sovrapposti.
def _dedupe_candidate_boxes(candidates, max_overlap=0.55):
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

    for idx, cnt in enumerate(contours):
        x, y, w, h = cv2.boundingRect(cnt)
        if w < 40 or h < 40:
            continue

        area = float(cv2.contourArea(cnt))
        extent = area / float(max(w * h, 1))
        ratio = w / float(max(h, 1))
        box = [float(x), float(y), float(x + w - 1), float(y + h - 1)]

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


# Verifica se una detection combacia con un candidato euristico.
def _box_matches_candidate(box, candidate_box, min_iou=0.28, min_ioa=0.55):
    return (
        _bbox_iou(box, candidate_box) >= min_iou
        or _bbox_ioa(box, candidate_box) >= min_ioa
        or _bbox_ioa(candidate_box, box) >= min_ioa
    )

# =========================================================
# REMAP E NORMALIZZAZIONE DELLE CLASSI
# =========================================================

# Corregge alcune confusioni note del modello usando regole geometriche.
def remap_special_component(image_gray, image_binary, box, predicted_class_name: str, structured_candidates):
    connector_candidates = structured_candidates.get("Connector", [])
    analog_candidates = structured_candidates.get("Analog_Meter", [])

    if predicted_class_name == "Integrated_Circuit":
        if any(_box_matches_candidate(box, candidate["bbox"]) for candidate in connector_candidates):
            return "Connector"
        if is_connector_like_bbox(image_binary, box, image_gray=image_gray):
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

    if predicted_class_name == "Diode" and is_led_like_diode_box(image_binary, box):
        return "LED"

    return predicted_class_name

# =========================================================
# POST-PROCESSING DELLE DETECTION
# =========================================================

# Costruisce il record standard di un componente.
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


# Aggiunge componenti strutturati mancanti trovati dalle euristiche.
def add_missing_structured_components(components, structured_candidates, class_meta, class_id_by_name):
    target_conf = {
        "Connector": 0.72,
        "Analog_Meter": 0.58,
    }

    updated = list(components)
    for class_name, candidates in structured_candidates.items():
        class_id = class_id_by_name.get(class_name)
        if class_id is None:
            continue
        meta = class_meta.get(class_id, {})
        for candidate in candidates:
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
    return updated


# Risolve conflitti tra classi che occupano la stessa regione.
def suppress_conflicting_components(components, image_binary, image_gray):
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
                analog_box = components[analog_idx]["bbox"]
                connector_box = components[connector_idx]["bbox"]

                if (
                    is_analog_meter_like_bbox(image_binary, analog_box)
                    or not is_connector_like_bbox(image_binary, connector_box, image_gray=image_gray)
                ):
                    suppressed.add(connector_idx)
                else:
                    suppressed.add(analog_idx)
                continue

            if pair in ({"Connector", "Meter"}, {"Connector", "Signal_Source"}):
                connector_idx = i if class_a == "Connector" else j
                other_idx = j if connector_idx == i else i

                connector_box = components[connector_idx]["bbox"]
                cx1, cy1, cx2, cy2 = connector_box
                cw = max(float(cx2 - cx1), 1.0)
                ch = max(float(cy2 - cy1), 1.0)
                elongation = max(cw, ch) / float(max(min(cw, ch), 1.0))

                if elongation < 1.35:
                    suppressed.add(connector_idx)
                continue

            if pair == {"Connector", "Integrated_Circuit"}:
                drop_idx = i if class_a == "Integrated_Circuit" else j
                suppressed.add(drop_idx)
                continue

            if pair == {"LED", "Diode"}:
                drop_idx = i if class_a == "Diode" else j
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


# Elimina duplicati della stessa classe con forte sovrapposizione.
def dedupe_overlapping_same_class(components):
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


# Rimuove terminal annidati dentro simboli che li inglobano.
def suppress_nested_terminals(components):
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


# Restituisce la soglia di confidence per una classe.
def get_required_confidence(class_name: str) -> float:
    return float(CLASS_CONF_THRES.get(class_name, CONF_THRES))


# Esegue un secondo pass mirato su classi difficili.
def add_secondary_class_predictions(
    image_path: Path,
    image_bgr,
    image_gray,
    image_binary,
    components,
    model,
    class_meta,
    class_id_by_name,
):
    updated = list(components)

    for target_class_name, spec in SECONDARY_CLASS_PREDICTION_SPECS.items():
        if target_class_name != "Connector":
            if any(comp.get("class_name") == target_class_name for comp in updated):
                continue

        target_class_id = class_id_by_name.get(target_class_name)
        if target_class_id is None:
            continue

        results = model.predict(
            source=str(image_path),
            imgsz=int(spec.get("imgsz", IMG_SIZE)),
            conf=float(spec.get("predict_conf", CONF_THRES)),
            iou=IOU_THRES,
            classes=[target_class_id],
            verbose=False,
        )
        result = results[0]
        if result.boxes is None or len(result.boxes) == 0:
            continue

        xyxy = result.boxes.xyxy.cpu().numpy()
        confs = result.boxes.conf.cpu().numpy()

        for box, conf in zip(xyxy, confs):
            original_meta = class_meta.get(target_class_id, {})
            remapped_class_name = remap_special_component(
                image_gray,
                image_binary,
                box,
                target_class_name,
                {"Analog_Meter": [], "Connector": []},
            )
            effective_class_id = class_id_by_name.get(remapped_class_name, target_class_id)
            meta = class_meta.get(effective_class_id, original_meta)
            yaml_class_name = meta.get("name", remapped_class_name)
            accept_conf = float(spec.get("accept_conf", get_required_confidence(yaml_class_name)))

            if float(conf) < accept_conf:
                continue
            if yaml_class_name == "Switch" and not is_switch_like_bbox(image_gray, box):
                continue
            if yaml_class_name == "Connector":
                if not is_connector_like_bbox(image_binary, box, image_gray=image_gray):
                    continue

            final_box = expand_led_bbox(box, image_bgr.shape) if yaml_class_name == "LED" else box
            updated.append(
                _build_component_record(
                    class_id=effective_class_id,
                    class_name=yaml_class_name,
                    model_class_name=f"secondary_{target_class_name}",
                    conf=float(conf),
                    bbox=final_box,
                    meta=meta,
                    source_class_id=target_class_id,
                    source_class_name=target_class_name,
                )
            )

    return updated


# Sceglie la confidence di inferenza del pass principale.
def get_model_inference_confidence(class_meta) -> float:
    class_names = [meta.get("name", "") for meta in class_meta.values()]
    per_class_thresholds = [get_required_confidence(name) for name in class_names if name]
    if not per_class_thresholds:
        return CONF_THRES
    # Usiamo la soglia minima per non tagliare via in partenza classi che
    # richiedono un threshold piu basso; il filtraggio fine avviene dopo.
    return min([CONF_THRES, *per_class_thresholds])


# Filtra i terminal rumorosi con probe vicini e lontani.
def is_terminal_detection_valid(image_binary, bbox) -> bool:
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

# =========================================================
# I/O E ORCHESTRAZIONE DELLO STAGE
# =========================================================

# Load YAML.
def load_yaml(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# Load class metadata.
def load_class_metadata(class_terminals_path: Path):
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


# Normalizza model.names in un dizionario class_id -> nome.
def normalize_model_names(model_names):
    if isinstance(model_names, list):
        return {i: name for i, name in enumerate(model_names)}

    if isinstance(model_names, dict):
        return {int(k): v for k, v in model_names.items()}

    raise TypeError("Formato model.names non riconosciuto.")


# Elenca le immagini di input della pipeline.
def get_input_images():
    if not INPUT_IMAGES_DIR.exists():
        raise FileNotFoundError(f"Cartella immagini non trovata: {INPUT_IMAGES_DIR}")

    images = sorted([
        p for p in INPUT_IMAGES_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS
    ])

    if not images:
        raise FileNotFoundError(f"Nessuna immagine trovata in: {INPUT_IMAGES_DIR}")

    return images


# Disegna i componenti rilevati sull'immagine debug.
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


# Esegue detection, remap, second pass ed euristiche su una singola immagine.
def predict_components_on_image(
    image_path: Path,
    model,
    detect_class_ids,
    model_names,
    class_meta
):
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
                continue

            # La classe Terminal e particolarmente rumorosa: oltre alla confidence
            # richiediamo anche un minimo di struttura grafica coerente.
            if yaml_class_name == "Terminal" and not is_terminal_detection_valid(image_binary, box):
                continue
            if yaml_class_name == "Switch":
                if not is_switch_like_bbox(image_gray, box):
                    if float(conf) < 0.75 or not is_switch_like_bbox_relaxed(image_gray, box):
                        continue
            if yaml_class_name == "Voltage_Source" and not is_voltage_source_like_bbox(image_binary, box):
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

    components = add_secondary_class_predictions(
        image_path=image_path,
        image_bgr=image_bgr,
        image_gray=image_gray,
        image_binary=image_binary,
        components=components,
        model=model,
        class_meta=class_meta,
        class_id_by_name=class_id_by_name,
    )
    components = add_missing_structured_components(
        components=components,
        structured_candidates=structured_candidates,
        class_meta=class_meta,
        class_id_by_name=class_id_by_name,
    )
    components = suppress_conflicting_components(components, image_binary, image_gray)
    components = dedupe_overlapping_same_class(components)
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


# Run the entrypoint for this pipeline stage.
def main() -> None:
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
