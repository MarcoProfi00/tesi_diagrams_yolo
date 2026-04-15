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
    "Connector": 0.18,
    "Lamp": 0.25,
    "Switch": 0.02,
    "Terminal": 0.35,
    "Transformer": 0.22,
}

# === DEBUG ===
SAVE_DEBUG_IMAGES = True

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


def _clamp_bbox_to_image(box, image_shape):
    """Riporta un bbox ai limiti immagine per le euristiche locali di post-detection."""
    h, w = image_shape[:2]
    x1, y1, x2, y2 = box
    x1 = max(0, min(w - 1, int(round(x1))))
    y1 = max(0, min(h - 1, int(round(y1))))
    x2 = max(0, min(w - 1, int(round(x2))))
    y2 = max(0, min(h - 1, int(round(y2))))
    return x1, y1, x2, y2


def _group_close_indices(indices, max_gap=1):
    """Raggruppa indici vicini per stabilizzare le euristiche basate su proiezione."""
    if not indices:
        return []

    groups = [[indices[0]]]
    for idx in indices[1:]:
        if idx <= groups[-1][-1] + max_gap:
            groups[-1].append(idx)
        else:
            groups.append([idx])
    return groups


def _merge_close_values(values, min_gap):
    """Fonde coordinate troppo vicine per evitare doppi conteggi dello stesso pin/feature."""
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


def _count_connector_pin_rows(image_binary, box):
    """Stima il numero di pin di un connettore verticale usando la proiezione interna."""
    x1, y1, x2, y2 = _clamp_bbox_to_image(box, image_binary.shape)
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)
    xc = int(round((x1 + x2) / 2))
    band_half = max(3, int(round(width * 0.22)))
    bx1 = max(x1, xc - band_half)
    bx2 = min(x2, xc + band_half)

    projection = [
        int(cv2.countNonZero(image_binary[y:y + 1, bx1:bx2 + 1]))
        for y in range(y1, y2 + 1)
    ]
    if not projection:
        return 0

    threshold = max(2, int(round(max(projection) * 0.32)))
    groups = _group_close_indices(
        [i for i, score in enumerate(projection) if score >= threshold],
        max_gap=6,
    )
    centers = [
        y1 + int(round((group[0] + group[-1]) / 2.0))
        for group in groups
    ]
    centers = _merge_close_values(
        sorted(centers),
        min_gap=max(18, int(round(height * 0.10))),
    )
    return len(centers)


def is_connector_like_bbox(image_binary, box) -> bool:
    """Verifica se un bbox assomiglia a un connettore multipin verticale del batch v9.1."""
    x1, y1, x2, y2 = _clamp_bbox_to_image(box, image_binary.shape)
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)

    if height < width * 1.8 or width < 30 or height < 110:
        return False

    xc = int(round((x1 + x2) / 2))
    band_half = max(3, int(round(width * 0.22)))
    bx1 = max(x1, xc - band_half)
    bx2 = min(x2, xc + band_half)

    projection = [
        int(cv2.countNonZero(image_binary[y:y + 1, bx1:bx2 + 1]))
        for y in range(y1, y2 + 1)
    ]
    if not projection:
        return False

    threshold = max(2, int(round(max(projection) * 0.32)))
    groups = _group_close_indices(
        [i for i, score in enumerate(projection) if score >= threshold],
        max_gap=6,
    )
    centers = [
        y1 + int(round((group[0] + group[-1]) / 2.0))
        for group in groups
    ]
    centers = _merge_close_values(
        sorted(centers),
        min_gap=max(18, int(round(height * 0.10))),
    )
    return 3 <= len(centers) <= 6


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


def is_switch_like_bbox(image_gray, box) -> bool:
    """Filtra false positive di Switch mantenendo solo simboli con due contatti circolari reali."""
    x1, y1, x2, y2 = _clamp_bbox_to_image(box, image_gray.shape)
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)

    if width < 90 or height < 55 or width < height * 0.95:
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
    return circle_count >= 2


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
    """Capisce se un bbox predetto come Diode contiene in realta un LED con frecce luminose."""
    x1, y1, x2, y2 = _clamp_bbox_to_image(box, image_binary.shape)
    pad = 18
    h, w = image_binary.shape[:2]
    x1 = max(0, x1 - pad)
    y1 = max(0, y1 - pad)
    x2 = min(w - 1, x2 + pad)
    y2 = min(h - 1, y2 + pad)
    roi = image_binary[y1:y2 + 1, x1:x2 + 1]
    num_labels, _, stats, _ = cv2.connectedComponentsWithStats(roi, connectivity=8)
    areas = sorted(
        [int(stats[i, cv2.CC_STAT_AREA]) for i in range(1, num_labels)],
        reverse=True,
    )
    medium = [area for area in areas[1:] if 40 <= area <= 900]
    return len(medium) >= 2


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


def find_structured_symbol_candidates(image_gray, image_binary):
    """Trova candidati strutturali per Connector e Analog_Meter direttamente dal binario."""
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
        circle_count = 0

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

        if (
            h >= w * 3.2
            and 55 <= w <= 130
            and h >= 250
            and extent >= 0.78
        ):
            circle_count = _count_hough_circles(
                image_gray,
                box,
                min_dist=18,
                param2=14,
                min_radius=7,
                max_radius=20,
            )
            row_count = _count_connector_pin_rows(image_binary, box)
            if circle_count >= 4 and 3 <= row_count <= 6:
                connector_candidates.append({
                    "bbox": box,
                    "score": 10.0 * extent + float(circle_count) + 0.5 * float(row_count),
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


def remap_special_component(image_gray, image_binary, box, predicted_class_name: str, structured_candidates):
    """Rimappa alcune classi YOLO verso Connector/Analog_Meter quando la forma locale lo suggerisce chiaramente."""
    connector_candidates = structured_candidates.get("Connector", [])
    analog_candidates = structured_candidates.get("Analog_Meter", [])

    if predicted_class_name == "Integrated_Circuit":
        if any(_box_matches_candidate(box, candidate["bbox"]) for candidate in connector_candidates):
            return "Connector"
        if is_connector_like_bbox(image_binary, box):
            return "Connector"

    if predicted_class_name in {"Meter", "Integrated_Circuit", "Inductor"}:
        if any(_box_matches_candidate(box, candidate["bbox"]) for candidate in analog_candidates):
            return "Analog_Meter"
        if is_analog_meter_like_bbox(image_binary, box):
            return "Analog_Meter"

    plate_symbol = classify_plate_symbol(image_binary, box)
    if predicted_class_name == "Capacitor" and plate_symbol == "Battery":
        return "Battery"
    if predicted_class_name == "Battery" and plate_symbol == "Capacitor":
        return "Capacitor"

    if predicted_class_name == "Diode" and is_led_like_diode_box(image_binary, box):
        return "LED"

    return predicted_class_name


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
    """Aggiunge componenti euristici quando il modello non li ha proprio rilevati."""
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


def load_yaml(path: Path):
    """Legge un file YAML e ne restituisce il contenuto gia convertito in strutture Python."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


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

    if not images:
        raise FileNotFoundError(f"Nessuna immagine trovata in: {INPUT_IMAGES_DIR}")

    return images


def draw_components(image_bgr, components):
    """Disegna bounding box e label dei componenti rilevati sull'immagine di debug."""
    out = image_bgr.copy()

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

        cv2.rectangle(out, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            out,
            label,
            (x1, max(y1 - 8, 0)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.50,
            (0, 255, 0),
            2,
            cv2.LINE_AA
        )

    return out


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
                continue

            # La classe Terminal e particolarmente rumorosa: oltre alla confidence
            # richiediamo anche un minimo di struttura grafica coerente.
            if yaml_class_name == "Terminal" and not is_terminal_detection_valid(image_binary, box):
                continue
            if yaml_class_name == "Switch" and not is_switch_like_bbox(image_gray, box):
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
