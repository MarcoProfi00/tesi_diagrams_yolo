"""
OCR per Integrated_Circuit.

Versione attuale:
- legge il nome/marking del circuito integrato;
- riconosce il sottotipo seven_segment_display quando un falso IC e' in realta'
  un display a 7 segmenti;
- NON legge i pin: quelli sono gestiti da ocr_integrated_circuit_pins.py;
- NON modifica terminal_id;
- NON cambia la geometria dei terminali;
- aggiunge campi semantici al componente:
    ic_marking
    ic_marking_confidence
    ic_marking_bbox
    ic_marking_source_region
    ic_ocr_debug

Ordine logico del modulo:
1. helper geometrici e recupero body_bbox;
2. costruzione delle regioni OCR candidate;
3. preprocessing e varianti immagine;
4. motori OCR Tesseract/EasyOCR;
5. normalizzazione, scoring e consenso dei candidati;
6. riconoscimento display 7 segmenti;
7. entry point pubblico enrich_ic_marking_ocr().

La logica resta:
1. i terminali vengono trovati geometricamente dai fili;
2. l'OCR arricchisce il componente con informazioni testuali.
"""

import os
import re
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

_EASYOCR_READER = None
_EASYOCR_READER_ERROR = None

IC_MARKING_PREFIXES = (
    "NE", "LM", "TDA", "TPS", "ISL", "ADC", "AT",
    "HT", "TC", "CD", "L", "TL", "UA", "MC", "MAX",
)


# =========================================================
# BASIC GEOMETRY HELPERS
# =========================================================

def _clamp_bbox(bbox, image_shape):
    """
    Limita un bbox ai bordi dell'immagine.

    bbox:
        [x1, y1, x2, y2]

    image_shape:
        shape OpenCV, quindi:
        - (h, w, c) per immagini BGR;
        - (h, w) per immagini grayscale/binarie.
    """
    h, w = image_shape[:2]

    x1, y1, x2, y2 = bbox

    x1 = int(max(0, min(w - 1, round(x1))))
    y1 = int(max(0, min(h - 1, round(y1))))
    x2 = int(max(0, min(w - 1, round(x2))))
    y2 = int(max(0, min(h - 1, round(y2))))

    # Garantisce ordine corretto anche se arriva un bbox invertito.
    if x2 < x1:
        x1, x2 = x2, x1
    if y2 < y1:
        y1, y2 = y2, y1

    return [x1, y1, x2, y2]


def _expand_bbox(bbox, image_shape, pad_x, pad_y):
    """
    Espande un bbox di pad_x/pad_y pixel e poi lo limita all'immagine.
    """
    x1, y1, x2, y2 = bbox

    return _clamp_bbox(
        [x1 - pad_x, y1 - pad_y, x2 + pad_x, y2 + pad_y],
        image_shape,
    )


def _crop(image_bgr, bbox):
    """
    Estrae una ROI dall'immagine BGR.

    Ritorna None se il bbox è vuoto.
    """
    x1, y1, x2, y2 = bbox

    if x2 <= x1 or y2 <= y1:
        return None

    return image_bgr[y1:y2 + 1, x1:x2 + 1].copy()


def _bbox_center(bbox):
    """
    Centro di un bbox [x1, y1, x2, y2].
    """
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)


def _center_inside_bbox(candidate_bbox, reference_bbox, pad_px=0):
    """
    True se il centro del bbox candidato cade dentro reference_bbox,
    eventualmente espanso di pad_px.

    Serve soprattutto per expanded_bbox:
    expanded_bbox può leggere testi lontani dal corpo IC.
    """
    cx, cy = _bbox_center(candidate_bbox)
    x1, y1, x2, y2 = reference_bbox

    return (
        (x1 - pad_px) <= cx <= (x2 + pad_px)
        and (y1 - pad_px) <= cy <= (y2 + pad_px)
    )


# =========================================================
# BODY BBOX EXTRACTION
# =========================================================

def get_ic_body_bbox_from_component(component: Dict, image_shape) -> List[int]:
    """
    Recupera il body_bbox dell'IC.

    Priorità:
    1. component["body_bbox"], se già salvato;
    2. component["connection_side_scores"]["body_bbox"], prodotto dalla strategia IC;
    3. body_bbox dentro il debug del primo terminale;
    4. fallback: component["bbox"] YOLO.

    Questo rende il modulo OCR robusto rispetto a piccole modifiche future
    nel formato JSON.
    """
    if component.get("body_bbox") is not None:
        return _clamp_bbox(component["body_bbox"], image_shape)

    side_scores = component.get("connection_side_scores") or {}
    if side_scores.get("body_bbox") is not None:
        return _clamp_bbox(side_scores["body_bbox"], image_shape)

    for term in component.get("terminals", []):
        dbg = term.get("terminal_point_debug") or {}
        if dbg.get("body_bbox") is not None:
            return _clamp_bbox(dbg["body_bbox"], image_shape)

    return _clamp_bbox(component["bbox"], image_shape)


# =========================================================
# OCR REGIONS
# =========================================================

def _build_dynamic_top_text_region(image_bgr, body_bbox: List[int], meta: Dict) -> Optional[Dict]:
    """
    Isola automaticamente una riga di testo nella parte alta del package IC.

    E' una ROI generale: non conosce il nome del componente, cerca solo una
    banda orizzontale con abbastanza pixel scuri dentro il corpo dell'IC.
    """
    ocr_cfg = ((meta.get("ocr") or {}).get("ic_marking") or {})
    image_shape = image_bgr.shape
    x1, y1, x2, y2 = body_bbox
    bw = max(1, x2 - x1)
    bh = max(1, y2 - y1)

    margin_x = int(round(bw * float(ocr_cfg.get("dynamic_text_margin_x_ratio", 0.06))))
    search_h = max(18, int(round(bh * float(ocr_cfg.get("dynamic_top_text_height_ratio", 0.16)))))

    sx1 = x1 + margin_x
    sx2 = x2 - margin_x
    sy1 = y1 + 1
    sy2 = min(y2, y1 + search_h)
    search_bbox = _clamp_bbox([sx1, sy1, sx2, sy2], image_shape)
    search_crop = _crop(image_bgr, search_bbox)
    if search_crop is None:
        return None

    gray = cv2.cvtColor(search_crop, cv2.COLOR_BGR2GRAY)
    if gray.shape[0] < 8 or gray.shape[1] < 20:
        return None

    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    _, binary = cv2.threshold(
        blurred,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
    )

    # Rimuove bordi sottili: ci interessa la riga di testo, non il rettangolo IC.
    edge_y = max(1, int(round(binary.shape[0] * 0.08)))
    edge_x = max(1, int(round(binary.shape[1] * 0.03)))
    binary[:edge_y, :] = 0
    binary[:, :edge_x] = 0
    binary[:, binary.shape[1] - edge_x:] = 0

    row_counts = np.count_nonzero(binary, axis=1).astype(np.float32)
    if row_counts.size < 3 or float(row_counts.max(initial=0.0)) <= 0.0:
        return None

    kernel = np.ones(5, dtype=np.float32) / 5.0
    smooth = np.convolve(row_counts, kernel, mode="same")
    min_row_pixels = max(4, int(round(binary.shape[1] * 0.035)))
    active = smooth >= min_row_pixels

    bands = []
    start = None
    for idx, is_active in enumerate(active):
        if is_active and start is None:
            start = idx
        elif not is_active and start is not None:
            bands.append((start, idx - 1))
            start = None
    if start is not None:
        bands.append((start, len(active) - 1))

    if not bands:
        return None

    best_band = max(
        bands,
        key=lambda band: (
            float(smooth[band[0]:band[1] + 1].sum()),
            -(band[0]),
        ),
    )

    y_start, y_end = best_band
    band_mask = binary[y_start:y_end + 1, :]
    col_counts = np.count_nonzero(band_mask, axis=0)
    active_cols = np.where(col_counts > 0)[0]
    if active_cols.size < 8:
        return None

    x_start = int(active_cols.min())
    x_end = int(active_cols.max())

    pad_x = max(4, int(round(bw * 0.025)))
    pad_y = max(3, int(round(bh * 0.012)))
    rx1, ry1, _, _ = search_bbox
    bbox = _clamp_bbox(
        [
            rx1 + x_start - pad_x,
            ry1 + y_start - pad_y,
            rx1 + x_end + pad_x,
            ry1 + y_end + pad_y,
        ],
        image_shape,
    )
    crop = _crop(image_bgr, bbox)
    if crop is None:
        return None

    return {
        "name": "body_top_text_line",
        "bbox": bbox,
        "image": crop,
        "psm": int(ocr_cfg.get("body_top_marking_psm", 7)),
    }


def build_ic_marking_regions(component: Dict, image_bgr, meta: Dict, mode: str = "fast") -> List[Dict]:
    """
    Costruisce le ROI dove cercare il marking dell'integrato.

    Le regioni sono configurabili nel YAML:

        ocr:
          ic_marking:
            search_regions:
              - body_inner
              - above_body
              - expanded_bbox

    Le regioni più importanti sono:
    - body_inner: nome dentro al rettangolo IC;
    - above_body: nome sopra il corpo, es. TPS63061 / ISL85410;
    - expanded_bbox: fallback più largo, ma viene filtrato dopo.
    """
    image_shape = image_bgr.shape
    body_bbox = get_ic_body_bbox_from_component(component, image_shape)

    x1, y1, x2, y2 = body_bbox
    bw = max(1, x2 - x1)
    bh = max(1, y2 - y1)

    ocr_cfg = ((meta.get("ocr") or {}).get("ic_marking") or {})

    search_regions = ocr_cfg.get(
        "search_regions",
        ["body_inner", "above_body", "expanded_bbox"],
    )

    pad_ratio = float(ocr_cfg.get("expanded_bbox_pad_ratio", 0.35))
    pad_x = int(round(bw * pad_ratio))
    pad_y = int(round(bh * pad_ratio))

    # Padding per regioni laterali/sopra/sotto.
    side_pad_x = max(8, int(round(bw * 0.12)))
    side_pad_y = max(8, int(round(bh * 0.20)))

    regions = []

    for region_name in search_regions:
        if region_name == "body_inner":
            # ---------------------------------------------------------
            # Per il marking dell'IC non conviene usare tutto il corpo.
            # Ai bordi ci sono spesso:
            # - numeri dei pin;
            # - label dei pin;
            # - fili;
            # - scritte tipo IC1.
            #
            # Usiamo quindi una ROI più centrale.
            # ---------------------------------------------------------
            inner_margin_x_ratio = float(
                ocr_cfg.get("body_inner_margin_x_ratio", 0.12)
            )
            inner_margin_y_ratio = float(
                ocr_cfg.get("body_inner_margin_y_ratio", 0.12)
            )

            mx = int(round(bw * inner_margin_x_ratio))
            my = int(round(bh * inner_margin_y_ratio))

            if (x2 - x1) > 2 * mx + 10 and (y2 - y1) > 2 * my + 10:
                bbox = _clamp_bbox(
                    [x1 + mx, y1 + my, x2 - mx, y2 - my],
                    image_shape,
                )
            else:
                bbox = _clamp_bbox([x1, y1, x2, y2], image_shape)

        elif region_name == "above_body":
            bbox = _clamp_bbox(
                [x1 - side_pad_x, y1 - side_pad_y, x2 + side_pad_x, y1],
                image_shape,
            )

        elif region_name == "below_body":
            bbox = _clamp_bbox(
                [x1 - side_pad_x, y2, x2 + side_pad_x, y2 + side_pad_y],
                image_shape,
            )

        elif region_name == "left_of_body":
            bbox = _clamp_bbox(
                [x1 - side_pad_x, y1, x1, y2],
                image_shape,
            )

        elif region_name == "right_of_body":
            bbox = _clamp_bbox(
                [x2, y1, x2 + side_pad_x, y2],
                image_shape,
            )

        elif region_name == "expanded_bbox":
            bbox = _expand_bbox(body_bbox, image_shape, pad_x, pad_y)

        else:
            # Regione sconosciuta nel YAML: la ignoriamo.
            continue

        crop = _crop(image_bgr, bbox)
        if crop is None:
            continue

        regions.append({
            "name": region_name,
            "bbox": bbox,
            "image": crop,
        })

    if ocr_cfg.get("body_top_marking_region_enabled", True):
        top_margin_x_ratio = float(ocr_cfg.get("body_top_marking_margin_x_ratio", 0.08))
        top_height_ratio = float(ocr_cfg.get("body_top_marking_height_ratio", 0.07))

        tx1 = x1 + int(round(bw * top_margin_x_ratio))
        tx2 = x2 - int(round(bw * top_margin_x_ratio))
        ty2 = y1 + max(12, int(round(bh * top_height_ratio)))
        bbox = _clamp_bbox([tx1, y1, tx2, ty2], image_shape)
        crop = _crop(image_bgr, bbox)
        if crop is not None:
            regions.append({
                "name": "body_top_marking",
                "bbox": bbox,
                "image": crop,
                "psm": int(ocr_cfg.get("body_top_marking_psm", 7)),
            })

        if mode == "deep":
            dynamic_region = _build_dynamic_top_text_region(image_bgr, body_bbox, meta)
            if dynamic_region is not None:
                regions.append(dynamic_region)

            tight_offset_ratio = float(ocr_cfg.get("body_top_marking_tight_offset_ratio", 0.017))
            tight_height_ratio = float(ocr_cfg.get("body_top_marking_tight_height_ratio", 0.068))
            ty1 = y1 + int(round(bh * tight_offset_ratio))
            ty2 = ty1 + max(12, int(round(bh * tight_height_ratio)))
            bbox = _clamp_bbox([tx1, ty1, tx2, ty2], image_shape)
            crop = _crop(image_bgr, bbox)
            if crop is not None:
                regions.append({
                    "name": "body_top_marking_tight",
                    "bbox": bbox,
                    "image": crop,
                    "psm": int(ocr_cfg.get("body_top_marking_psm", 7)),
                })

            for idx, (offset_ratio, height_ratio) in enumerate(
                ocr_cfg.get("body_top_marking_extra_bands", [
                    [0.012, 0.075],
                    [0.032, 0.060],
                ]),
                start=1,
            ):
                ty1 = y1 + int(round(bh * float(offset_ratio)))
                ty2 = ty1 + max(12, int(round(bh * float(height_ratio))))
                bbox = _clamp_bbox([tx1, ty1, tx2, ty2], image_shape)
                crop = _crop(image_bgr, bbox)
                if crop is None:
                    continue

                regions.append({
                    "name": f"body_top_marking_{idx}",
                    "bbox": bbox,
                    "image": crop,
                    "psm": int(ocr_cfg.get("body_top_marking_psm", 7)),
                })

    # ---------------------------------------------------------
    # ROI di riga interne al body.
    #
    # Tesseract spesso sbaglia quando vede insieme:
    # - marking centrale;
    # - numeri dei pin;
    # - bordi del rettangolo;
    # - fili verticali/orizzontali.
    #
    # Aggiungiamo quindi poche bande orizzontali centrali, molto piu'
    # strette, da leggere come singola riga. E' una strategia generale:
    # non conosce il nome dell'IC, prova solo a isolare meglio il testo.
    # ---------------------------------------------------------
    if ocr_cfg.get("body_line_regions_enabled", True):
        line_margin_x_ratio = float(ocr_cfg.get("body_line_margin_x_ratio", 0.18))
        line_height_ratio = float(ocr_cfg.get("body_line_height_ratio", 0.20))
        line_centers = ocr_cfg.get("body_line_center_y_ratios", [0.38, 0.50, 0.62])

        lx1 = x1 + int(round(bw * line_margin_x_ratio))
        lx2 = x2 - int(round(bw * line_margin_x_ratio))
        half_h = max(8, int(round(bh * line_height_ratio / 2.0)))

        for idx, center_ratio in enumerate(line_centers, start=1):
            cy = y1 + int(round(bh * float(center_ratio)))
            bbox = _clamp_bbox([lx1, cy - half_h, lx2, cy + half_h], image_shape)
            crop = _crop(image_bgr, bbox)
            if crop is None:
                continue

            regions.append({
                "name": f"body_line_{idx}",
                "bbox": bbox,
                "image": crop,
                "psm": int(ocr_cfg.get("body_line_psm", 7)),
            })

    return regions


# =========================================================
# OCR PREPROCESSING E MOTORI OCR
# =========================================================

def _preprocess_for_ocr(crop_bgr):
    """
    Preprocess semplice per Tesseract.

    Passi:
    1. grayscale;
    2. resize x3;
    3. blur leggero;
    4. soglia Otsu;
    5. testo nero su sfondo bianco.

    È volutamente semplice: prima rendiamo stabile la pipeline,
    poi eventualmente ottimizziamo per casi difficili.
    """
    gray = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2GRAY)

    scale = 3
    gray = cv2.resize(
        gray,
        None,
        fx=scale,
        fy=scale,
        interpolation=cv2.INTER_CUBIC,
    )

    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    _, th = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU,
    )

    # Tesseract preferisce testo nero su fondo bianco.
    if np.mean(th) < 127:
        th = cv2.bitwise_not(th)

    return th, scale


def _make_ocr_image_variants(crop_bgr, region_name: str, meta: Dict, mode: str = "fast") -> List[Dict]:
    """
    Crea poche varianti visive della ROI senza cambiare il testo OCR.

    Per semplicità le varianti extra sono usate solo sulla fascia alta del
    package, dove i marking piccoli soffrono di piu'.
    """
    ocr_cfg = ((meta.get("ocr") or {}).get("ic_marking") or {})
    if (
        mode != "deep"
        or not str(region_name).startswith("body_top_marking")
        or not ocr_cfg.get("ocr_variants_enabled", True)
    ):
        return [{
            "name": "raw",
            "image": crop_bgr,
            "scale_x": 1.0,
            "scale_y": 1.0,
        }]

    variants = [{
        "name": "raw",
        "image": crop_bgr,
        "scale_x": 1.0,
        "scale_y": 1.0,
    }]

    gray = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2GRAY)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
    clahe_bgr = cv2.cvtColor(clahe, cv2.COLOR_GRAY2BGR)
    variants.append({
        "name": "clahe",
        "image": clahe_bgr,
        "scale_x": 1.0,
        "scale_y": 1.0,
    })

    adaptive = cv2.adaptiveThreshold(
        clahe,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        21,
        9,
    )
    if np.mean(adaptive) < 127:
        adaptive = cv2.bitwise_not(adaptive)
    variants.append({
        "name": "adaptive",
        "image": cv2.cvtColor(adaptive, cv2.COLOR_GRAY2BGR),
        "scale_x": 1.0,
        "scale_y": 1.0,
    })

    scale = float(ocr_cfg.get("ocr_variant_upscale", 2.0))
    if scale > 1.0:
        upscaled = cv2.resize(
            clahe_bgr,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_CUBIC,
        )
        variants.append({
            "name": "upscaled_clahe",
            "image": upscaled,
            "scale_x": scale,
            "scale_y": scale,
        })

    return variants


def _easyocr_variants_for_region(region_name: str, variants: List[Dict]) -> List[Dict]:
    """
    Limita EasyOCR alle prove che valgono davvero il costo.

    Tesseract resta il motore economico che esplora piu' varianti; EasyOCR e'
    usato solo sulle regioni interne al package e con poche immagini.
    """
    if _region_priority(region_name) < 2:
        return []

    if str(region_name).startswith("body_top_marking"):
        return [
            variant for variant in variants
            if variant.get("name", "raw") in {"raw", "clahe"}
        ]

    return [
        variant for variant in variants
        if variant.get("name", "raw") == "raw"
    ]


def _select_easyocr_regions(regions: List[Dict], candidates: List[Dict], meta: Dict) -> set:
    """
    Sceglie poche ROI interne su cui vale la pena provare EasyOCR.
    """
    available = {region["name"] for region in regions}
    selected = []

    for candidate in _candidates_with_consensus(candidates, meta):
        region_name = candidate.get("source_region")
        if region_name in available and _region_priority(region_name) >= 2:
            if region_name not in selected:
                selected.append(region_name)
        if len(selected) >= 2:
            break

    if "body_inner" in available and "body_inner" not in selected:
        selected.append("body_inner")

    if not selected:
        for region_name in ("body_inner", "body_top_marking", "body_line_2"):
            if region_name in available:
                selected.append(region_name)

    return set(selected[:3])


def _words_to_original_variant_scale(words: List[Dict], variant: Dict) -> List[Dict]:
    """
    Riporta le bbox di una variante scalata alle coordinate della ROI originale.
    """
    scale_x = max(float(variant.get("scale_x", 1.0)), 1e-6)
    scale_y = max(float(variant.get("scale_y", 1.0)), 1e-6)

    normalized_words = []
    for word in words:
        lx1, ly1, lx2, ly2 = word["bbox_local"]
        normalized = dict(word)
        normalized["bbox_local"] = [
            int(round(lx1 / scale_x)),
            int(round(ly1 / scale_y)),
            int(round(lx2 / scale_x)),
            int(round(ly2 / scale_y)),
        ]
        normalized["variant"] = variant.get("name", "raw")
        normalized_words.append(normalized)

    return normalized_words


def _run_tesseract_words(crop_bgr, whitelist: Optional[str] = None, psm: int = 6) -> Tuple[List[Dict], Dict]:
    """
    Esegue pytesseract sulla ROI e ritorna una lista di parole.

    Ogni parola ha:
    - text;
    - confidence;
    - bbox_local.

    Se pytesseract o tesseract.exe non sono disponibili,
    non blocchiamo la pipeline: ritorniamo lista vuota e debug.
    """
    try:
        import pytesseract
        from pytesseract import Output

        # Permette di specificare manualmente il path di tesseract.exe.
        #
        # Esempio Windows:
        #   set TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe
        tesseract_cmd = os.environ.get("TESSERACT_CMD")
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    except Exception as exc:
        return [], {
            "available": False,
            "engine": "pytesseract",
            "error": f"pytesseract_import_failed: {exc}",
        }

    prep, scale = _preprocess_for_ocr(crop_bgr)

    config_parts = [
        f"--psm {psm}",
        "--oem 3",
    ]

    if whitelist:
        config_parts.append(f"-c tessedit_char_whitelist={whitelist}")

    config = " ".join(config_parts)

    try:
        data = pytesseract.image_to_data(
            prep,
            output_type=Output.DICT,
            config=config,
        )
    except Exception as exc:
        return [], {
            "available": False,
            "engine": "pytesseract",
            "error": f"pytesseract_runtime_failed: {exc}",
        }

    words = []

    for i, raw_text in enumerate(data.get("text", [])):
        text = str(raw_text).strip()
        if not text:
            continue

        try:
            conf = float(data["conf"][i])
        except Exception:
            conf = -1.0

        # Tesseract usa -1 per box non validi.
        if conf < 0:
            continue

        x = int(round(data["left"][i] / scale))
        y = int(round(data["top"][i] / scale))
        w = int(round(data["width"][i] / scale))
        h = int(round(data["height"][i] / scale))

        words.append({
            "text": text,
            "confidence": conf / 100.0,
            "bbox_local": [x, y, x + w, y + h],
        })

    return words, {
        "available": True,
        "engine": "pytesseract",
        "psm": psm,
        "word_count": len(words),
    }


def _easyocr_bbox_to_xyxy(points) -> List[int]:
    """
    Converte il quadrilatero EasyOCR in bbox [x1, y1, x2, y2].
    """
    xs = [float(p[0]) for p in points]
    ys = [float(p[1]) for p in points]
    return [
        int(round(min(xs))),
        int(round(min(ys))),
        int(round(max(xs))),
        int(round(max(ys))),
    ]


def _get_easyocr_reader(
    languages: Optional[List[str]] = None,
    gpu: bool = False,
    model_storage_directory: Optional[str] = None,
):
    """
    Lazy singleton per EasyOCR.

    Caricare il reader per ogni crop sarebbe lentissimo; lo creiamo una volta
    e poi lo riusiamo per tutti gli IC.
    """
    global _EASYOCR_READER, _EASYOCR_READER_ERROR

    if _EASYOCR_READER is not None:
        return _EASYOCR_READER, None
    if _EASYOCR_READER_ERROR is not None:
        return None, _EASYOCR_READER_ERROR

    try:
        import easyocr
    except Exception as exc:
        _EASYOCR_READER_ERROR = f"easyocr_import_failed: {exc}"
        return None, _EASYOCR_READER_ERROR

    try:
        if model_storage_directory:
            model_storage_directory = os.path.abspath(model_storage_directory)
            user_network_directory = os.path.join(model_storage_directory, "user_network")
            os.makedirs(model_storage_directory, exist_ok=True)
            os.makedirs(user_network_directory, exist_ok=True)
        else:
            user_network_directory = None

        _EASYOCR_READER = easyocr.Reader(
            languages or ["en"],
            gpu=bool(gpu),
            model_storage_directory=model_storage_directory,
            user_network_directory=user_network_directory,
        )
    except Exception as exc:
        _EASYOCR_READER_ERROR = f"easyocr_reader_init_failed: {exc}"
        return None, _EASYOCR_READER_ERROR

    return _EASYOCR_READER, None


def _run_easyocr_words(crop_bgr, meta: Dict) -> Tuple[List[Dict], Dict]:
    """
    Esegue EasyOCR sulla ROI e ritorna parole compatibili col formato Tesseract.

    Se EasyOCR non e' installato o non riesce a inizializzarsi, non blocchiamo
    la pipeline: ritorniamo lista vuota e debug con errore.
    """
    ocr_cfg = ((meta.get("ocr") or {}).get("ic_marking") or {})
    easy_cfg = ocr_cfg.get("easyocr_fallback") or {}

    languages = list(easy_cfg.get("languages", ["en"]))
    gpu = bool(easy_cfg.get("gpu", False))
    min_confidence = float(easy_cfg.get("min_confidence", 0.0))
    model_storage_directory = os.environ.get(
        "EASYOCR_MODEL_DIR",
        str(easy_cfg.get("model_storage_directory", ".tmp/easyocr")),
    )

    reader, error = _get_easyocr_reader(
        languages=languages,
        gpu=gpu,
        model_storage_directory=model_storage_directory,
    )
    if reader is None:
        return [], {
            "available": False,
            "engine": "easyocr",
            "error": error,
        }

    try:
        results = reader.readtext(
            crop_bgr,
            detail=1,
            paragraph=False,
            allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789/-+.",
        )
    except Exception as exc:
        return [], {
            "available": False,
            "engine": "easyocr",
            "error": f"easyocr_runtime_failed: {exc}",
        }

    words = []
    for bbox_points, text, confidence in results:
        confidence = float(confidence)
        if confidence < min_confidence:
            continue

        text = str(text).strip()
        if not text:
            continue

        words.append({
            "text": text,
            "confidence": confidence,
            "bbox_local": _easyocr_bbox_to_xyxy(bbox_points),
        })

    return words, {
        "available": True,
        "engine": "easyocr",
        "word_count": len(words),
        "languages": languages,
        "gpu": gpu,
    }


# =========================================================
# NORMALIZZAZIONE, FILTRI E SCORING DEI CANDIDATI
# =========================================================

def _normalize_text(text: str) -> str:
    """
    Normalizza testo OCR.

    Manteniamo una normalizzazione prudente:
    - maiuscolo;
    - rimozione spazi;
    - pulizia caratteri ai bordi;
    - piccola correzione LM31/T -> LM317T.

    Non correggiamo aggressivamente codici tipo TDA7ON -> TDA7000,
    perché quello richiederà un passaggio successivo con fuzzy matching
    o datasheet lookup.
    """
    text = text.strip().upper()
    text = text.replace(" ", "")
    text = text.replace("\n", "")
    text = text.strip(".,:;|[]{}()")

    # Caso generale: Tesseract puo' leggere il tratto obliquo del 7 come slash.
    # Esempi:
    # - LM18/5 -> LM1875
    # - codici numerici simili con "/" tra due cifre
    text = re.sub(r"(?<=\d)/(?=\d)", "7", text)

    # Caso frequente: LM31/T letto al posto di LM317T.
    if re.match(r"^LM[0-9]+/T$", text):
        text = text.replace("/", "7")

    # Dopo la normalizzazione dello slash, un OCR tipo LM31/7T puo'
    # diventare LM3177T. Collassiamo il doppio 7 solo davanti a un suffisso.
    text = re.sub(r"(?<=7)7(?=[A-Z]$)", "", text)

    return text


def _matches_any_pattern(text: str, patterns: List[str]) -> bool:
    """
    True se text matcha almeno una regex della lista.
    """
    for pattern in patterns:
        try:
            if re.match(pattern, text):
                return True
        except re.error:
            # Regex non valida nel YAML: la ignoriamo.
            continue

    return False


def _is_probable_unit_or_value(text: str) -> bool:
    """
    Scarta valori elettrici o unità che non sono marking IC.

    Esempi:
    - 10UF
    - 100NF
    - 4.7K
    - 12V
    - 500MW
    - 22UH
    """
    unit_pattern = (
        r"^[0-9]+(\.[0-9]+)?"
        r"(UF|NF|PF|MF|V|DC|K|KOHM|OHM|R|W|MW|A|MA|UH|MH|H)$"
    )

    return re.match(unit_pattern, text) is not None


def _score_ic_marking_candidate(text: str, confidence: float, region_name: str, meta: Dict) -> Tuple[float, Dict]:
    """
    Calcola uno score per decidere se una parola OCR può essere il marking IC.

    Versione severa:
    - deve contenere almeno una lettera;
    - deve contenere almeno un numero;
    - scarta COM, OUT, ADJ, VIN, GND, ecc.;
    - scarta designator come IC1, U1, R1, C2;
    - scarta transistor comuni come 2N2222, BC547;
    - scarta valori come 10UF, 100NF, 12V.
    """
    ocr_cfg = ((meta.get("ocr") or {}).get("ic_marking") or {})

    min_chars = int(ocr_cfg.get("min_chars", 3))
    reject_patterns = list(ocr_cfg.get("reject_designator_patterns", []))

    # Protezioni extra anche se il YAML non è aggiornato.
    reject_patterns.extend([
        r"^IC[0-9]+[A-Z]?$",
        r"^U[0-9]+[A-Z]?$",
        r"^R[0-9]+[A-Z]?$",
        r"^C[0-9]+[A-Z]?$",
        r"^L[0-9]+[A-Z]?$",
        r"^D[0-9]+[A-Z]?$",
        r"^Q[0-9]+[A-Z]?$",
        r"^K[0-9]+[A-Z]?$",
        r"^S[0-9]+[A-Z]?$",
        r"^J[0-9]+[A-Z]?$",
        r"^TP[0-9]+[A-Z]?$",

        # Porte/pin digitali: P0.1, P1.7, P3.2...
        r"^P[0-9]+(\.[0-9]+)?$",

        # Transistor comuni: non sono IC marking.
        r"^2N[0-9]+[A-Z]?$",
        r"^BC[0-9]+[A-Z]?$",
    ])

    # Parole che possono essere pin label o net label,
    # ma non devono diventare nome IC.
    hard_reject_words = {
        "IN", "OUT", "ADJ", "COM", "NC", "N/C",
        "VIN", "VOUT", "VCC", "VDD", "VSS",
        "GND", "PGND", "PAD",
        "EN", "FB", "PG", "COMP", "SYNC", "BOOT",
        "PHASE", "SS", "FS", "SHDN", "RESET",
        "MODE", "SWITCH", "AUDIO", "POWER", "DIRECTION",
        "ANTENNA", "NO", "CONNECTION",
        "WWW", "CIRCUITSTODAY", "WWW.CIRCUITSTODAY",
    }

    deprioritize_net_labels = set(
        str(v).upper()
        for v in ocr_cfg.get("deprioritize_net_labels", [])
    )

    debug = {
        "text": text,
        "confidence": round(float(confidence), 4),
        "region": region_name,
        "accepted": False,
        "reject_reason": None,
        "score": 0.0,
    }

    if len(text) < min_chars:
        debug["reject_reason"] = "too_short"
        return -999.0, debug

    if text in hard_reject_words:
        debug["reject_reason"] = "hard_reject_word"
        return -999.0, debug

    if text in deprioritize_net_labels:
        debug["reject_reason"] = "net_or_pin_label"
        return -999.0, debug

    if "CIRCUIT" in text or "WWW" in text:
        debug["reject_reason"] = "watermark_or_website"
        return -999.0, debug

    designator_check_text = re.sub(r"^[^A-Z0-9]+", "", text)

    if (
        _matches_any_pattern(text, reject_patterns)
        or _matches_any_pattern(designator_check_text, reject_patterns)
    ) and not _looks_like_ic_family_marking(text):
        debug["reject_reason"] = "component_designator_or_non_ic"
        return -999.0, debug

    if _is_probable_unit_or_value(text):
        debug["reject_reason"] = "unit_or_value"
        return -999.0, debug

    has_alpha = any(ch.isalpha() for ch in text)
    has_digit = any(ch.isdigit() for ch in text)
    digit_count = sum(ch.isdigit() for ch in text)
    digit_runs = re.findall(r"[0-9]+", text)
    longest_digit_run = max((len(run) for run in digit_runs), default=0)

    if not has_alpha:
        debug["reject_reason"] = "no_alpha"
        return -999.0, debug

    # Regola chiave:
    # i marking utili per datasheet di solito contengono lettere e numeri:
    # NE555, LM317T, TDA7000, TPS63061, ISL85410, ADC0804, AT89S51, L298...
    if not has_digit:
        debug["reject_reason"] = "no_digit_for_ic_marking"
        return -999.0, debug

    allowed_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/-+_.")
    strange_chars = [ch for ch in text if ch not in allowed_chars]
    if strange_chars:
        debug["reject_reason"] = "strange_chars"
        return -999.0, debug

    score = float(confidence)

    # Bonus perché contiene lettere e numeri.
    score += 0.35

    # Bonus per lunghezza realistica.
    if 4 <= len(text) <= 16:
        score += 0.20

    # Bonus per prefissi frequenti nei tuoi esempi.
    if text.startswith(IC_MARKING_PREFIXES):
        score += 0.25

    # I codici IC reali spesso hanno una parte numerica forte:
    # ADC0804, AT89S51, TDA1553, NE555, LM317T. Questo aiuta a preferire
    # letture numeriche plausibili rispetto a OCR piu' "letterosi".
    if digit_count >= 3:
        score += 0.12
    if digit_count >= 4:
        score += 0.08
    if longest_digit_run >= 3:
        score += 0.18
    elif longest_digit_run == 2:
        score += 0.08

    if _looks_like_structured_alternative_marking(text):
        score += 0.55

    # Peso della regione.
    # expanded_bbox è utile ma pericolosa, quindi nessun bonus.
    region_bonus = {
        "body_inner": 0.18,
        "body_top_marking": 0.28,
        "body_top_marking_tight": 0.33,
        "body_top_text_line": 0.30,
        "body_top_marking_1": 0.28,
        "body_top_marking_2": 0.28,
        "body_line_1": 0.24,
        "body_line_2": 0.24,
        "body_line_3": 0.24,
        "above_body": 0.15,
        "expanded_bbox": 0.10,
        "below_body": -0.05,
        "left_of_body": -0.10,
        "right_of_body": -0.10,
    }
    score += region_bonus.get(region_name, 0.0)

    debug["digit_count"] = digit_count
    debug["longest_digit_run"] = longest_digit_run

    debug["accepted"] = True
    debug["score"] = round(float(score), 4)

    return score, debug


def _add_ocr_words_as_candidates(
    words: List[Dict],
    region: Dict,
    engine_name: str,
    meta: Dict,
    body_bbox: List[int],
    all_candidates: List[Dict],
    region_info: Dict,
) -> None:
    """
    Converte parole OCR in candidate marking usando scoring e filtri comuni.
    """
    rx1, ry1, _, _ = region["bbox"]

    for word in words:
        normalized = _normalize_text(word["text"])

        score, cand_debug = _score_ic_marking_candidate(
            normalized,
            word.get("confidence", 0.0),
            region["name"],
            meta,
        )

        cand_debug["raw_text"] = word["text"]
        cand_debug["engine"] = engine_name
        cand_debug["variant"] = word.get("variant", "raw")

        lx1, ly1, lx2, ly2 = word["bbox_local"]
        abs_bbox = [rx1 + lx1, ry1 + ly1, rx1 + lx2, ry1 + ly2]
        cand_debug["bbox"] = abs_bbox

        if region["name"] == "expanded_bbox":
            bw = max(1, body_bbox[2] - body_bbox[0])
            bh = max(1, body_bbox[3] - body_bbox[1])
            pad_px = int(round(max(bw, bh) * 0.08))

            if not _center_inside_bbox(abs_bbox, body_bbox, pad_px=pad_px):
                cand_debug["accepted"] = False
                cand_debug["reject_reason"] = "expanded_bbox_candidate_outside_body"
                cand_debug["score"] = 0.0
                region_info["candidate_debug"].append(cand_debug)
                continue

        region_info["candidate_debug"].append(cand_debug)

        if score <= -900:
            continue

        all_candidates.append({
            "text": normalized,
            "score": round(float(score), 4),
            "confidence": round(float(word.get("confidence", 0.0)), 4),
            "bbox": abs_bbox,
            "source_region": region["name"],
            "raw_text": word["text"],
            "engine": engine_name,
            "variant": word.get("variant", "raw"),
        })


def _candidates_with_consensus(candidates: List[Dict], meta: Optional[Dict] = None) -> List[Dict]:
    """
    Arricchisce i candidati con un punteggio di consenso.

    Oltre allo score della singola lettura, premiamo leggermente il consenso:
    se lo stesso testo viene letto in piu' regioni/engine e' piu' affidabile
    di una lettura isolata con score appena superiore.
    """
    if not candidates:
        return []

    ocr_cfg = (((meta or {}).get("ocr") or {}).get("ic_marking") or {})
    region_bonus = float(ocr_cfg.get("consensus_region_bonus", 0.18))
    engine_bonus = float(ocr_cfg.get("consensus_engine_bonus", 0.08))

    support_by_text = {}
    for candidate in candidates:
        text = candidate.get("text")
        if not text:
            continue

        support = support_by_text.setdefault(text, {
            "regions": set(),
            "engines": set(),
        })
        if candidate.get("source_region"):
            support["regions"].add(candidate["source_region"])
        if candidate.get("engine"):
            support["engines"].add(candidate["engine"])

    ranked = []
    for candidate in candidates:
        support = support_by_text.get(candidate.get("text"), {})
        regions = sorted(support.get("regions", set()))
        engines = sorted(support.get("engines", set()))

        consensus_score = float(candidate.get("score", 0.0))
        consensus_score += max(0, len(regions) - 1) * region_bonus
        consensus_score += max(0, len(engines) - 1) * engine_bonus

        enriched = dict(candidate)
        enriched["consensus_score"] = round(float(consensus_score), 4)
        enriched["consensus_support_count"] = len(regions)
        enriched["consensus_support_regions"] = regions
        enriched["consensus_support_engines"] = engines
        ranked.append(enriched)

    return sorted(
        ranked,
        key=lambda c: (
            c["consensus_score"],
            c.get("score", 0.0),
            _region_priority(c.get("source_region")),
            c.get("confidence", 0.0),
        ),
        reverse=True,
    )


def _region_priority(region_name: Optional[str]) -> int:
    """
    Preferisce letture dentro il package rispetto a testo esterno vicino.
    """
    if region_name in {"body_top_marking", "body_top_text_line", "body_inner"}:
        return 2
    if str(region_name or "").startswith("body_top_marking_"):
        return 2
    if str(region_name or "").startswith("body_line_"):
        return 2
    if region_name == "expanded_bbox":
        return 1
    return 0


def _best_candidate(candidates: List[Dict], meta: Optional[Dict] = None) -> Optional[Dict]:
    """
    Ritorna il candidato migliore secondo score OCR + consenso.
    """
    ranked = _candidates_with_consensus(candidates, meta)
    if not ranked:
        return None
    return ranked[0]


def _ocr_engines_used(region_debug: List[Dict]) -> List[str]:
    """
    Elenca i motori OCR realmente disponibili/provati durante la lettura.
    """
    engines = set()

    for region in region_debug:
        engine_debug = region.get("engine_debug") or {}
        for engine_name, debug_info in engine_debug.items():
            if isinstance(debug_info, dict) and debug_info.get("available") is not None:
                if debug_info.get("available"):
                    engines.add(engine_name)
                continue

            if isinstance(debug_info, dict):
                for variant_debug in debug_info.values():
                    if isinstance(variant_debug, dict) and variant_debug.get("available"):
                        engines.add(engine_name)
                        break

    return sorted(engines)


def _should_run_easyocr_fallback(candidates: List[Dict], meta: Dict) -> bool:
    """
    Decide se EasyOCR va usato come fallback.
    """
    ocr_cfg = ((meta.get("ocr") or {}).get("ic_marking") or {})
    easy_cfg = ocr_cfg.get("easyocr_fallback") or {}

    if not easy_cfg.get("enabled", False):
        return False

    best = _best_candidate(candidates, meta)
    if best is None:
        return bool(easy_cfg.get("run_when_no_candidates", True))

    min_conf = float(easy_cfg.get("run_when_best_confidence_below", 0.30))
    return float(best.get("confidence", 0.0)) < min_conf


def _has_pin_label_family_evidence(region_debug: List[Dict], suffix: str) -> bool:
    """
    True se l'OCR dello stesso IC ha visto pin label della famiglia indicata.

    Per esempio, se il part number candidato finisce con "D" e nelle raw words
    compaiono D0/D1/D6, il suffisso finale e' probabilmente una pin label fusa.
    """
    if not suffix:
        return False

    pattern = re.compile(rf"^{re.escape(suffix)}[0-9]+$", re.IGNORECASE)
    for region in region_debug:
        for word in region.get("raw_words", []):
            raw_text = str(word.get("text", "")).strip()
            normalized = _normalize_text(raw_text)
            if pattern.match(normalized):
                return True

    return False


def _looks_like_ic_family_marking(text: str) -> bool:
    """
    True se il token sembra un marking IC plausibile di una famiglia nota.

    Serve per non scartare testi come L298 solo perche' somigliano anche
    a designatori schematici.
    """
    if not text:
        return False

    if re.fullmatch(r"(?:74|54)[A-Z]{1,5}[0-9]{2,4}[A-Z]?", text):
        return True

    if not text.startswith(IC_MARKING_PREFIXES):
        return False

    digit_count = sum(ch.isdigit() for ch in text)
    digit_runs = re.findall(r"[0-9]+", text)
    longest_digit_run = max((len(run) for run in digit_runs), default=0)

    if len(text) < 4:
        return False

    # Il prefisso singolo "L" e' ambiguo con designatori tipo L1/L2.
    # Lo sblocchiamo solo quando c'e' una parte numerica abbastanza forte.
    if text.startswith("L") and not text.startswith(("LM", "LF")):
        return digit_count >= 3 and longest_digit_run >= 3

    return digit_count >= 2


def _looks_like_structured_alternative_marking(text: str) -> bool:
    """
    True per marking del tipo CODICE/CODICE.

    Alcuni datasheet o simboli indicano varianti compatibili separate da slash.
    Questo non corregge il testo: aiuta solo il ranking a preferire una lettura
    strutturata rispetto a una stringa lunga fusa.
    """
    if "/" not in text:
        return False

    parts = [part for part in text.split("/") if part]
    if len(parts) != 2:
        return False

    for part in parts:
        if len(part) < 4 or len(part) > 14:
            return False
        if not any(ch.isalpha() for ch in part):
            return False
        if sum(ch.isdigit() for ch in part) < 3:
            return False
        if not re.match(r"^[A-Z0-9+_.-]+$", part):
            return False

    return True


def _split_possible_pin_suffix_from_part_number(text: str, region_debug: List[Dict]) -> Tuple[str, Dict]:
    """
    Separa un possibile frammento di pin label agganciato al part number.

    Esempio reale: OCR legge "ADC0804D" perche' la D del pin "D6" viene
    fusa con il marking "ADC0804". Non vogliamo perdere il raw text, quindi
    questa funzione restituisce sia il nome base sia un debug esplicito.

    Regola volutamente stretta e generale:
    - prefisso alfabetico iniziale;
    - almeno tre cifre consecutive nel part number base;
    - un solo suffisso finale che assomiglia a una famiglia di pin label.
    """
    debug = {
        "raw_text": text,
        "normalized_part_number": text,
        "changed": False,
        "reason": None,
        "removed_suffix": None,
    }

    if not text:
        return text, debug

    match = re.match(r"^([A-Z]{2,6}[0-9][A-Z0-9]*[0-9])([ADPQ])$", text)
    if not match:
        return text, debug

    base, suffix = match.groups()
    if not _has_pin_label_family_evidence(region_debug, suffix):
        debug["reason"] = "no_same_family_pin_label_evidence"
        return text, debug

    longest_digit_run = max((len(run) for run in re.findall(r"[0-9]+", base)), default=0)
    if longest_digit_run < 3:
        return text, debug

    debug.update({
        "normalized_part_number": base,
        "changed": True,
        "reason": "possible_trailing_pin_label_suffix",
        "removed_suffix": suffix,
    })
    return base, debug


# =========================================================
# RICONOSCIMENTO DISPLAY 7 SEGMENTI
# =========================================================

def _abs_word_bbox(region: Dict, word: Dict) -> List[int]:
    """
    Converte il bbox locale di una raw word OCR in coordinate immagine.
    """
    rx1, ry1, _, _ = region["bbox"]
    lx1, ly1, lx2, ly2 = word["bbox_local"]
    return [rx1 + lx1, ry1 + ly1, rx1 + lx2, ry1 + ly2]


def _collect_ocr_raw_words(region_debug: List[Dict]) -> List[Dict]:
    """
    Raccoglie le raw words OCR con bbox assoluto e testo normalizzato.
    """
    words = []
    for region in region_debug:
        for word in region.get("raw_words", []):
            raw_text = str(word.get("text", "")).strip()
            if not raw_text:
                continue
            words.append({
                "raw_text": raw_text,
                "text": _normalize_text(raw_text),
                "confidence": round(float(word.get("confidence", 0.0)), 4),
                "bbox": _abs_word_bbox(region, word),
                "source_region": region.get("region"),
            })
    return words


def _estimate_seven_segment_shape_evidence(image_bgr, body_bbox: List[int]) -> Dict:
    """
    Cerca evidenza grafica di segmenti spessi dentro il body.

    Non prova a riconoscere il numero visualizzato; misura solo se dentro il
    rettangolo ci sono componenti scure grandi e compatte, piu' simili a
    segmenti LED/LCD che a testo sottile di un part number.
    """
    crop = _crop(image_bgr, body_bbox)
    if crop is None:
        return {
            "has_segment_shape": False,
            "reason": "empty_body_crop",
        }

    h, w = crop.shape[:2]
    if h < 40 or w < 40:
        return {
            "has_segment_shape": False,
            "reason": "body_too_small",
            "width": w,
            "height": h,
        }

    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

    # Evita bordo e pin label vicino al bordo: guardiamo soprattutto l'interno.
    mx = max(4, int(round(w * 0.12)))
    my = max(4, int(round(h * 0.08)))
    inner = gray[my:h - my, mx:w - mx]
    if inner.size == 0:
        inner = gray

    dark = inner < 120
    dark_ratio = float(np.count_nonzero(dark)) / float(dark.size)

    mask = dark.astype(np.uint8) * 255
    n_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)

    min_area = max(20, int(round(inner.size * 0.004)))
    large_components = []
    largest_area = 0
    elongated_components = 0

    for label_idx in range(1, n_labels):
        area = int(stats[label_idx, cv2.CC_STAT_AREA])
        if area < min_area:
            continue

        cw = int(stats[label_idx, cv2.CC_STAT_WIDTH])
        ch = int(stats[label_idx, cv2.CC_STAT_HEIGHT])
        largest_area = max(largest_area, area)
        aspect = max(cw, ch) / max(1, min(cw, ch))
        if aspect >= 2.0:
            elongated_components += 1

        large_components.append({
            "area": area,
            "width": cw,
            "height": ch,
            "aspect": round(float(aspect), 3),
        })

    largest_area_ratio = float(largest_area) / float(inner.size)
    has_segment_shape = (
        dark_ratio >= 0.035
        and largest_area_ratio >= 0.012
        and (len(large_components) >= 2 or elongated_components >= 1)
    )

    return {
        "has_segment_shape": bool(has_segment_shape),
        "dark_ratio": round(float(dark_ratio), 4),
        "largest_area_ratio": round(float(largest_area_ratio), 4),
        "large_component_count": len(large_components),
        "elongated_component_count": elongated_components,
        "large_components_sample": large_components[:8],
    }


def _detect_seven_segment_display(component: Dict, image_bgr, body_bbox: List[int], region_debug: List[Dict]) -> Optional[Dict]:
    """
    Classifica un Integrated_Circuit senza part number come display a 7 segmenti.

    La decisione combina:
    - OCR di pin/segment labels: a-g e com;
    - eventuale reference designator D1/D2, salvato ma non usato come marking;
    - evidenza grafica di segmenti scuri nel body.
    """
    raw_words = _collect_ocr_raw_words(region_debug)

    segment_labels = set()
    com_labels = []
    reference_designators = []

    for word in raw_words:
        text = word["text"]
        if text in {"A", "B", "C", "D", "E", "F", "G"}:
            segment_labels.add(text.lower())
        elif text == "COM":
            com_labels.append(word)
        elif re.match(r"^D[0-9]+$", text):
            reference_designators.append(word)

    shape_evidence = _estimate_seven_segment_shape_evidence(image_bgr, body_bbox)

    label_score = len(segment_labels) + (2 if com_labels else 0)
    has_label_evidence = label_score >= 4
    has_mixed_evidence = label_score >= 3 and shape_evidence.get("has_segment_shape", False)

    if not has_label_evidence and not has_mixed_evidence:
        return None

    reference_designator = None
    if reference_designators:
        reference_designator = sorted(
            reference_designators,
            key=lambda item: item.get("confidence", 0.0),
            reverse=True,
        )[0]["text"]

    return {
        "component_subtype": "seven_segment_display",
        "display_type": "seven_segment",
        "reference_designator_ocr": reference_designator,
        "debug": {
            "segment_labels_detected": sorted(segment_labels),
            "has_com_label": bool(com_labels),
            "label_score": label_score,
            "reference_designator_candidates": reference_designators[:5],
            "shape_evidence": shape_evidence,
        },
    }


def _subtype_from_marking_text(marking: str) -> Optional[Dict]:
    upper = re.sub(r"\s+", "", str(marking or "")).upper()
    if not re.fullmatch(r"DIS[0-9]+", upper):
        return None

    return {
        "component_subtype": "seven_segment_display",
        "display_type": "seven_segment",
        "reference_designator_ocr": upper,
        "debug": {
            "reason": "marking_matches_display_designator",
            "marking": upper,
        },
    }


# =========================================================
# RACCOLTA CANDIDATI E MODALITA' FAST/DEEP
# =========================================================

def _collect_ocr_candidates(
    regions: List[Dict],
    meta: Dict,
    body_bbox: List[int],
    whitelist: str,
    mode: str = "fast",
    run_easyocr: bool = False,
    easyocr_region_names: Optional[set] = None,
) -> Tuple[List[Dict], List[Dict]]:
    """
    Esegue un pass OCR e raccoglie candidati/debug.

    mode="fast":
      - solo immagini raw;
      - niente bande extra;
      - normalmente solo Tesseract.

    mode="deep":
      - abilita varianti immagine sulle fasce alte;
      - puo' usare EasyOCR come secondo motore.
    """
    all_candidates = []
    region_debug = []

    for region in regions:
        region_info = {
            "region": region["name"],
            "bbox": region["bbox"],
            "ocr_mode": mode,
            "engine_debug": {
                "tesseract": {},
            },
            "raw_words": [],
            "candidate_debug": [],
        }

        variants = _make_ocr_image_variants(
            region["image"],
            region["name"],
            meta,
            mode=mode,
        )

        for variant in variants:
            words, engine_debug = _run_tesseract_words(
                variant["image"],
                whitelist=whitelist,
                psm=int(region.get("psm", 6)),
            )
            words = _words_to_original_variant_scale(words, variant)

            variant_name = variant.get("name", "raw")
            region_info["engine_debug"]["tesseract"][variant_name] = engine_debug
            region_info["raw_words"].extend(words)

            _add_ocr_words_as_candidates(
                words=words,
                region=region,
                engine_name="tesseract",
                meta=meta,
                body_bbox=body_bbox,
                all_candidates=all_candidates,
                region_info=region_info,
            )

        if run_easyocr and (
            easyocr_region_names is None
            or region["name"] in easyocr_region_names
        ):
            region_info["engine_debug"]["easyocr"] = {}
            region_info["raw_words_easyocr"] = []

            for variant in _easyocr_variants_for_region(region["name"], variants):
                easy_words, easy_debug = _run_easyocr_words(variant["image"], meta)
                easy_words = _words_to_original_variant_scale(easy_words, variant)

                variant_name = variant.get("name", "raw")
                region_info["engine_debug"]["easyocr"][variant_name] = easy_debug
                region_info["raw_words_easyocr"].extend(easy_words)

                _add_ocr_words_as_candidates(
                    words=easy_words,
                    region=region,
                    engine_name="easyocr",
                    meta=meta,
                    body_bbox=body_bbox,
                    all_candidates=all_candidates,
                    region_info=region_info,
                )

        region_debug.append(region_info)

    return all_candidates, region_debug


def _append_easyocr_candidates(
    regions: List[Dict],
    region_debug: List[Dict],
    meta: Dict,
    body_bbox: List[int],
    mode: str,
    easyocr_region_names: set,
) -> List[Dict]:
    """
    Aggiunge solo EasyOCR ai debug/candidati gia' raccolti con Tesseract.
    """
    all_candidates = []

    for region, region_info in zip(regions, region_debug):
        if region["name"] not in easyocr_region_names:
            continue

        variants = _make_ocr_image_variants(
            region["image"],
            region["name"],
            meta,
            mode=mode,
        )

        region_info.setdefault("engine_debug", {}).setdefault("easyocr", {})
        region_info.setdefault("raw_words_easyocr", [])

        for variant in _easyocr_variants_for_region(region["name"], variants):
            easy_words, easy_debug = _run_easyocr_words(variant["image"], meta)
            easy_words = _words_to_original_variant_scale(easy_words, variant)

            variant_name = variant.get("name", "raw")
            region_info["engine_debug"]["easyocr"][variant_name] = easy_debug
            region_info["raw_words_easyocr"].extend(easy_words)

            _add_ocr_words_as_candidates(
                words=easy_words,
                region=region,
                engine_name="easyocr",
                meta=meta,
                body_bbox=body_bbox,
                all_candidates=all_candidates,
                region_info=region_info,
            )

    return all_candidates


def _should_run_deep_ocr(candidates: List[Dict], meta: Dict) -> bool:
    """
    Decide se passare dalla lettura veloce a quella profonda.

    Non corregge il testo: controlla solo se vale la pena spendere tempo con
    ROI/varianti piu' robuste.
    """
    if not candidates:
        return True

    best = _best_candidate(candidates, meta)
    if best is None:
        return True

    if _should_run_easyocr_fallback(candidates, meta):
        return True

    source_region = best.get("source_region")
    if source_region == "above_body":
        return True

    if source_region == "expanded_bbox" and float(best.get("confidence", 0.0)) < 0.75:
        return True

    return False


# =========================================================
# PUBLIC API
# =========================================================

def enrich_ic_marking_ocr(component: Dict, image_bgr, meta: Dict) -> Dict:
    """
    Arricchisce un componente Integrated_Circuit con il marking OCR.

    Modifica e ritorna component.

    Campi aggiunti:
    - body_bbox;
    - ic_marking;
    - ic_marking_confidence;
    - ic_marking_bbox;
    - ic_marking_source_region;
    - ic_ocr_debug.

    Non modifica i terminali.
    """
    ocr_root = meta.get("ocr") or {}
    ic_marking_cfg = ocr_root.get("ic_marking") or {}

    if not ocr_root.get("enabled", False) or not ic_marking_cfg.get("enabled", False):
        component["ic_ocr_debug"] = {
            "enabled": False,
            "reason": "ocr_disabled_in_yaml",
        }
        return component

    body_bbox = get_ic_body_bbox_from_component(component, image_bgr.shape)

    # Salviamo il body_bbox anche a livello componente.
    # Sarà utile per debug, script 04 e OCR pin.
    component["body_bbox"] = body_bbox

    regions = build_ic_marking_regions(component, image_bgr, meta, mode="fast")

    # Whitelist per marking IC.
    # Include slash perché alcuni OCR leggono LM317T come LM31/T.
    whitelist = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_/-+."

    all_candidates, region_debug = _collect_ocr_candidates(
        regions=regions,
        meta=meta,
        body_bbox=body_bbox,
        whitelist=whitelist,
        mode="fast",
        run_easyocr=False,
    )

    subtype_info = None
    if not all_candidates:
        subtype_info = _detect_seven_segment_display(
            component,
            image_bgr,
            body_bbox,
            region_debug,
        )

    ocr_mode = "fast"
    if subtype_info is None and _should_run_deep_ocr(all_candidates, meta):
        regions = build_ic_marking_regions(component, image_bgr, meta, mode="deep")
        easy_cfg = ic_marking_cfg.get("easyocr_fallback") or {}
        all_candidates, region_debug = _collect_ocr_candidates(
            regions=regions,
            meta=meta,
            body_bbox=body_bbox,
            whitelist=whitelist,
            mode="deep",
            run_easyocr=False,
        )

        if bool(easy_cfg.get("enabled", False)) and _should_run_easyocr_fallback(all_candidates, meta):
            easyocr_region_names = _select_easyocr_regions(regions, all_candidates, meta)
            easy_candidates = _append_easyocr_candidates(
                regions=regions,
                region_debug=region_debug,
                meta=meta,
                body_bbox=body_bbox,
                mode="deep",
                easyocr_region_names=easyocr_region_names,
            )
            all_candidates.extend(easy_candidates)

        ocr_mode = "deep"

    if not all_candidates:
        component["ic_marking"] = None
        component["ic_marking_confidence"] = 0.0
        component["ic_marking_bbox"] = None
        component["ic_marking_source_region"] = None
        component["ic_marking_engine"] = None
        component["ic_marking_variant"] = None
        component["ic_ocr_mode"] = ocr_mode
        component["ic_ocr_engines_used"] = _ocr_engines_used(region_debug)

        if subtype_info is None:
            subtype_info = _detect_seven_segment_display(
                component,
                image_bgr,
                body_bbox,
                region_debug,
            )
        if subtype_info:
            component["component_subtype"] = subtype_info["component_subtype"]
            component["display_type"] = subtype_info["display_type"]
            component["reference_designator_ocr"] = subtype_info["reference_designator_ocr"]

        component["ic_ocr_debug"] = {
            "enabled": True,
            "ocr_mode": ocr_mode,
            "body_bbox": body_bbox,
            "selected": None,
            "candidate_count": 0,
            "subtype_detection": subtype_info["debug"] if subtype_info else None,
            "regions": region_debug,
        }
        return component

    best = _best_candidate(all_candidates, meta)

    marking, marking_normalization = _split_possible_pin_suffix_from_part_number(
        best["text"],
        region_debug,
    )

    component["ic_marking"] = marking
    component["ic_marking_confidence"] = best["confidence"]
    component["ic_marking_bbox"] = best["bbox"]
    component["ic_marking_source_region"] = best["source_region"]
    component["ic_marking_engine"] = best.get("engine")
    component["ic_marking_variant"] = best.get("variant", "raw")
    component["ic_ocr_mode"] = ocr_mode
    component["ic_ocr_engines_used"] = _ocr_engines_used(region_debug)

    if subtype_info is None:
        subtype_info = _subtype_from_marking_text(marking)
    if subtype_info is None and not _looks_like_ic_family_marking(marking):
        subtype_info = _detect_seven_segment_display(
            component,
            image_bgr,
            body_bbox,
            region_debug,
        )
    if subtype_info:
        component["component_subtype"] = subtype_info["component_subtype"]
        component["display_type"] = subtype_info["display_type"]
        component["reference_designator_ocr"] = subtype_info["reference_designator_ocr"]

    ranked_candidates = _candidates_with_consensus(all_candidates, meta)

    component["ic_ocr_debug"] = {
        "enabled": True,
        "ocr_mode": ocr_mode,
        "body_bbox": body_bbox,
        "selected": best,
        "marking_normalization": marking_normalization,
        "candidate_count": len(all_candidates),
        "subtype_detection": subtype_info["debug"] if subtype_info else None,
        "candidates": ranked_candidates[:10],
        "regions": region_debug,
    }

    return component


def enrich_integrated_circuit_with_ocr(component: Dict, image_bgr, meta: Dict) -> Dict:
    """
    Alias comodo per uso futuro.

    Per ora chiama solo enrich_ic_marking_ocr.
    Quando aggiungeremo OCR dei pin, questa funzione potrà diventare:
        1. enrich_ic_marking_ocr(...)
        2. enrich_ic_pin_ocr(...)
    """
    return enrich_ic_marking_ocr(component, image_bgr, meta)
