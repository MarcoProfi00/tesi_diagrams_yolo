"""
OCR per Integrated_Circuit.

Versione attuale:
- legge SOLO il nome/marking del circuito integrato;
- NON legge ancora i pin;
- NON modifica terminal_id;
- NON cambia la geometria dei terminali;
- aggiunge campi semantici al componente:
    ic_marking
    ic_marking_confidence
    ic_marking_bbox
    ic_marking_source_region
    ic_ocr_debug

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

def build_ic_marking_regions(component: Dict, image_bgr, meta: Dict) -> List[Dict]:
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
# OCR ENGINE
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
# TEXT NORMALIZATION / FILTERING
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

    if _matches_any_pattern(text, reject_patterns) and not _looks_like_ic_family_marking(text):
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

    # Peso della regione.
    # expanded_bbox è utile ma pericolosa, quindi nessun bonus.
    region_bonus = {
        "body_inner": 0.18,
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
            c.get("confidence", 0.0),
        ),
        reverse=True,
    )


def _best_candidate(candidates: List[Dict], meta: Optional[Dict] = None) -> Optional[Dict]:
    """
    Ritorna il candidato migliore secondo score OCR + consenso.
    """
    ranked = _candidates_with_consensus(candidates, meta)
    if not ranked:
        return None
    return ranked[0]


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
    min_score = float(easy_cfg.get("run_when_best_score_below", 1.20))
    return (
        float(best.get("confidence", 0.0)) < min_conf
        or float(best.get("score", 0.0)) < min_score
    )


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

    regions = build_ic_marking_regions(component, image_bgr, meta)

    # Whitelist per marking IC.
    # Include slash perché alcuni OCR leggono LM317T come LM31/T.
    whitelist = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_/-+."

    all_candidates = []
    region_debug = []

    for region in regions:
        words, engine_debug = _run_tesseract_words(
            region["image"],
            whitelist=whitelist,
            psm=int(region.get("psm", 6)),
        )

        region_info = {
            "region": region["name"],
            "bbox": region["bbox"],
            "engine_debug": {
                "tesseract": engine_debug,
            },
            "raw_words": words,
            "candidate_debug": [],
        }

        _add_ocr_words_as_candidates(
            words=words,
            region=region,
            engine_name="tesseract",
            meta=meta,
            body_bbox=body_bbox,
            all_candidates=all_candidates,
            region_info=region_info,
        )

        region_debug.append(region_info)
        continue

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

            # Converte bbox locale ROI in bbox assoluto immagine.
            lx1, ly1, lx2, ly2 = word["bbox_local"]
            abs_bbox = [rx1 + lx1, ry1 + ly1, rx1 + lx2, ry1 + ly2]
            cand_debug["bbox"] = abs_bbox

            # ---------------------------------------------------------
            # Filtro speciale per expanded_bbox.
            #
            # expanded_bbox può leggere testi lontani:
            # watermark, valori, altri componenti, label di rete.
            #
            # Accettiamo un candidato da expanded_bbox solo se il centro
            # del testo cade dentro il body_bbox leggermente espanso.
            # ---------------------------------------------------------
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
                "engine": "tesseract",
            })

        region_debug.append(region_info)

    if _should_run_easyocr_fallback(all_candidates, meta):
        for region, region_info in zip(regions, region_debug):
            easy_words, easy_debug = _run_easyocr_words(region["image"], meta)
            region_info["engine_debug"]["easyocr"] = easy_debug
            region_info["raw_words_easyocr"] = easy_words

            _add_ocr_words_as_candidates(
                words=easy_words,
                region=region,
                engine_name="easyocr",
                meta=meta,
                body_bbox=body_bbox,
                all_candidates=all_candidates,
                region_info=region_info,
            )

    if not all_candidates:
        component["ic_marking"] = None
        component["ic_marking_confidence"] = 0.0
        component["ic_marking_bbox"] = None
        component["ic_marking_source_region"] = None

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

    ranked_candidates = _candidates_with_consensus(all_candidates, meta)

    component["ic_ocr_debug"] = {
        "enabled": True,
        "body_bbox": body_bbox,
        "selected": best,
        "marking_normalization": marking_normalization,
        "candidate_count": len(all_candidates),
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
