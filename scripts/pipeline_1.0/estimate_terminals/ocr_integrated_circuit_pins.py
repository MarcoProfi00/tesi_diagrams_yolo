"""
OCR locale dei pin per Integrated_Circuit.

Strategia side_lane_candidates_v1:
- non crea terminali;
- usa i terminali geometrici gia' stimati;
- per ogni lato dell'IC costruisce una banda stretta che attraversa il bordo;
- assegna le parole OCR alla "corsia" del terminale piu' vicino sullo stesso lato;
- separa pin_number e pin_label_text.

Ordine logico del modulo:
1. helper base e configurazione;
2. costruzione delle corsie OCR laterali;
3. OCR numerico e fallback sui componenti connessi;
4. OCR testuale Tesseract/EasyOCR;
5. normalizzazione, filtri e scoring;
6. assegnazione dei candidati ai terminali;
7. riparazioni post-OCR e filtro display 7 segmenti;
8. entry point pubblico enrich_ic_pin_ocr().

Nota sui display 7 segmenti:
- restano Integrated_Circuit con component_subtype="seven_segment_display";
- passano nello stesso OCR pin degli altri IC;
- accettano label singole a..h come pin_label_text;
- dopo l'OCR viene applicato un filtro di dominio: massimo 9 terminali
  a-h + com, scegliendo il lato verticale piu' coerente con le label OCR.

Se una lettura non e' affidabile, il campo resta None.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import os
import re
import shutil
import subprocess
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

from .config import TERMINAL_OUTWARD_OFFSET
from .ocr_integrated_circuit import get_ic_body_bbox_from_component


_EASYOCR_PIN_READER = None
_EASYOCR_PIN_READER_ERROR = None
_SIDES = {"left", "right", "top", "bottom"}
_TEXT_ALLOWED_RE = re.compile(r"[^A-Za-z0-9_./+\-]")
_SHORT_PIN_LABELS = {
    "IN", "OUT", "ADJ", "EN", "FB", "PG", "CS", "RD", "WR", "INTR",
    "RESET", "RST", "LSB", "MSB", "VIN", "VOUT", "VCC", "GND", "VAUX",
    "BOOT", "SYNC", "COMP", "PHASE", "PAD", "CLK", "FS",
}
_PIN_LABEL_OCR_ALIASES = {
    "0UT": "OUT",
    "OI": "OUT",
    "OL": "OUT",
    "OU": "OUT",
    "AD": "ADJ",
    "ADI": "ADJ",
    "LI": "L1",
    "LF": "L1",
    "PSISY": "PS/SYNC",
    "PSISYNC": "PS/SYNC",
    "PSSYNC": "PS/SYNC",
}
_PIN_LABEL_REJECT_PATTERNS = (
    re.compile(r"^R[0-9]+[A-Z]?$", re.IGNORECASE),
    re.compile(r"^C[0-9]+[A-Z]?$", re.IGNORECASE),
    re.compile(r"^Q[0-9]+[A-Z]?$", re.IGNORECASE),
    re.compile(r"^IC[0-9]+[A-Z]?$", re.IGNORECASE),
    re.compile(r"^U[0-9]+[A-Z]?$", re.IGNORECASE),
    re.compile(r"^J[0-9]+[A-Z]?$", re.IGNORECASE),
    re.compile(r"^K[0-9]+[A-Z]?$", re.IGNORECASE),
    re.compile(r"^TP[0-9]+[A-Z]?$", re.IGNORECASE),
)


# =========================================================
# CONFIGURAZIONE E HELPER BASE
# =========================================================

def _get_marking_bbox(component: Dict) -> Optional[List[int]]:
    bbox = component.get("ic_marking_bbox")
    if not bbox:
        return None
    try:
        return [int(round(float(v))) for v in bbox]
    except Exception:
        return None


def _timing_enabled() -> bool:
    value = str(os.environ.get("IC_OCR_TIMING", "")).strip().lower()
    return value in {"1", "true", "yes", "on"}


def _elapsed_ms(start_time: float) -> float:
    return round((time.perf_counter() - start_time) * 1000.0, 1)


def _clamp_bbox(bbox, image_shape) -> List[int]:
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


def _crop(image_bgr, bbox):
    x1, y1, x2, y2 = bbox
    if x2 <= x1 or y2 <= y1:
        return None
    return image_bgr[y1:y2 + 1, x1:x2 + 1].copy()


def _terminal_side(term: Dict) -> Optional[str]:
    side = term.get("relative_position")
    if side in _SIDES:
        return side
    name = str(term.get("name", ""))
    prefix = name.split("_", 1)[0] if "_" in name else None
    return prefix if prefix in _SIDES else None


def _terminal_sort_key(term: Dict) -> Tuple[float, float]:
    side = _terminal_side(term)
    x = float(term.get("x", 0.0))
    y = float(term.get("y", 0.0))
    if side in {"left", "right"}:
        return y, x
    return x, y


def _union_bbox(boxes: List[List[int]], image_shape) -> Optional[List[int]]:
    if not boxes:
        return None
    x1 = min(box[0] for box in boxes)
    y1 = min(box[1] for box in boxes)
    x2 = max(box[2] for box in boxes)
    y2 = max(box[3] for box in boxes)
    return _clamp_bbox([x1, y1, x2, y2], image_shape)


def _bbox_contains_point(bbox: List[int], x: float, y: float) -> bool:
    return bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]


def _bbox_overlap_ratio(box_a: List[int], box_b: List[int]) -> float:
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b
    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)
    if ix2 <= ix1 or iy2 <= iy1:
        return 0.0
    inter = float((ix2 - ix1) * (iy2 - iy1))
    area_a = float(max(1, (ax2 - ax1) * (ay2 - ay1)))
    area_b = float(max(1, (bx2 - bx1) * (by2 - by1)))
    return inter / max(1.0, min(area_a, area_b))


def _get_pin_ocr_cfg(meta: Dict) -> Dict:
    """
    Legge dal metadata YAML tutte le soglie e le opzioni OCR dei pin.

    Questa configurazione e' indipendente dal componente corrente: eventuali
    dettagli del singolo componente, come component_subtype, vengono aggiunti
    in enrich_ic_pin_ocr().
    """
    ocr_root = meta.get("ocr") or {}
    cfg = ocr_root.get("pin_labels") or {}
    number_cfg = cfg.get("number_ocr") or {}
    label_cfg = cfg.get("label_ocr") or {}
    easy_cfg = cfg.get("easyocr_fallback") or {}
    lane_cfg = cfg.get("lane_search") or {}
    attach_cfg = cfg.get("attach") or {}

    return {
        "ocr_enabled": bool(ocr_root.get("enabled", False)),
        "enabled": bool(cfg.get("enabled", False)),
        "strategy": cfg.get("strategy", "side_lane_candidates_v1"),
        "skip_component_subtypes": set(cfg.get("skip_component_subtypes", [])),
        "store_debug": bool(cfg.get("store_debug", True)),
        "number_enabled": bool(number_cfg.get("enabled", True)),
        "number_psm": int(number_cfg.get("psm", 11)),
        "number_min_confidence": float(number_cfg.get("min_confidence", 0.25)),
        "label_enabled": bool(label_cfg.get("enabled", True)),
        "label_guard_enabled": bool(label_cfg.get("guard_numbers", True)),
        "label_psm": int(label_cfg.get("psm", 11)),
        "label_min_confidence": float(label_cfg.get("min_confidence", 0.20)),
        "skip_labels_when_marking_and_number": bool(
            label_cfg.get("skip_when_marking_and_number", True)
        ),
        "easyocr_label_enabled": bool(easy_cfg.get("enabled", True)),
        "easyocr_label_languages": easy_cfg.get("languages", ["en"]),
        "easyocr_label_gpu": bool(easy_cfg.get("gpu", False)),
        "easyocr_label_model_storage_directory": easy_cfg.get("model_storage_directory", ".tmp/easyocr"),
        "easyocr_label_min_confidence": float(easy_cfg.get("min_confidence", 0.20)),
        "number_pattern": cfg.get("number_pattern", r"^[0-9]{1,3}$"),
        "label_pattern": cfg.get("label_pattern", r"^[A-Za-z][A-Za-z0-9_./+-]{0,15}$"),
        "lane_padding_px": int(lane_cfg.get("lane_padding_px", 6)),
        "side_inside_px": int(lane_cfg.get("side_inside_px", 78)),
        "side_outside_px": int(lane_cfg.get("side_outside_px", 42)),
        "top_bottom_inside_px": int(lane_cfg.get("top_bottom_inside_px", 72)),
        "top_bottom_outside_px": int(lane_cfg.get("top_bottom_outside_px", 42)),
        "upscale": float(lane_cfg.get("upscale", 3.0)),
        "adaptive_upscale_enabled": bool(lane_cfg.get("adaptive_upscale_enabled", True)),
        "adaptive_upscale_min_body_dim_px": int(lane_cfg.get("adaptive_upscale_min_body_dim_px", 140)),
        "adaptive_upscale_target_body_dim_px": int(lane_cfg.get("adaptive_upscale_target_body_dim_px", 160)),
        "adaptive_upscale_max_scale": float(lane_cfg.get("adaptive_upscale_max_scale", 6.0)),
        "line_kernel_ratio": float(lane_cfg.get("line_kernel_ratio", 0.33)),
        "component_fallback_enabled": bool(lane_cfg.get("component_fallback_enabled", True)),
        "max_number_distance_px": float(attach_cfg.get("max_number_distance_px", 42)),
        "max_label_distance_px": float(attach_cfg.get("max_label_distance_px", 86)),
        "reject_overlap_ratio": float(attach_cfg.get("reject_overlap_ratio", 0.50)),
    }


def _reset_pin_fields(component: Dict) -> None:
    """
    Pulisce i campi OCR pin prima di una nuova esecuzione.

    Rende lo step idempotente: se una lettura precedente era presente ma quella
    corrente fallisce, il vecchio valore non rimane nel JSON.
    """
    for term in component.get("terminals", []) or []:
        term["pin_number"] = None
        term["pin_label_text"] = None
        term["pin_number_confidence"] = None
        term["pin_label_confidence"] = None
        term.pop("pin_number_bbox", None)
        term.pop("pin_label_bbox", None)
        term.pop("pin_ocr_debug", None)


def _lane_zone_px(side: str, cfg: Dict) -> Tuple[float, float]:
    if side in {"left", "right"}:
        return float(cfg["side_inside_px"]), float(cfg["side_outside_px"])
    return float(cfg["top_bottom_inside_px"]), float(cfg["top_bottom_outside_px"])


def _effective_ocr_upscale(cfg: Dict) -> float:
    base = max(float(cfg.get("upscale", 1.0)), 1.0)
    if not cfg.get("adaptive_upscale_enabled", True):
        return base

    body_bbox = cfg.get("body_bbox")
    if not body_bbox or len(body_bbox) != 4:
        return base

    try:
        x1, y1, x2, y2 = [float(v) for v in body_bbox]
    except Exception:
        return base

    min_dim = min(max(1.0, x2 - x1 + 1.0), max(1.0, y2 - y1 + 1.0))
    if min_dim >= float(cfg.get("adaptive_upscale_min_body_dim_px", 140)):
        return base

    target_dim = max(float(cfg.get("adaptive_upscale_target_body_dim_px", 160)), min_dim)
    multiplier = target_dim / max(min_dim, 1.0)
    return max(base, min(base * multiplier, float(cfg.get("adaptive_upscale_max_scale", 6.0))))


# =========================================================
# CORSIE GEOMETRICHE DEI TERMINALI
# =========================================================

def _build_side_lanes(component: Dict, body_bbox, image_shape, cfg: Dict) -> Dict[str, Dict]:
    """
    Costruisce una corsia OCR per ogni terminale geometrico dell'IC.

    Ogni corsia e' una ROI sottile intorno al bordo del body_bbox. Le parole
    OCR vengono poi associate alla corsia che contiene il loro centro.
    """
    bx1, by1, bx2, by2 = [float(v) for v in body_bbox]
    side_runs: Dict[str, Dict] = {}

    for side in ("left", "right", "top", "bottom"):
        terms = [
            term for term in sorted(component.get("terminals", []) or [], key=_terminal_sort_key)
            if _terminal_side(term) == side
        ]
        if not terms:
            continue

        axis_values = [
            float(term.get("y", 0.0)) if side in {"left", "right"} else float(term.get("x", 0.0))
            for term in terms
        ]
        axis_low = by1 if side in {"left", "right"} else bx1
        axis_high = by2 if side in {"left", "right"} else bx2
        inside_px, outside_px = _lane_zone_px(side, cfg)
        lane_pad = float(cfg["lane_padding_px"])

        lanes = []
        for idx, term in enumerate(terms):
            center = axis_values[idx]
            prev_mid = (axis_values[idx - 1] + center) * 0.5 if idx > 0 else axis_low
            next_mid = (center + axis_values[idx + 1]) * 0.5 if idx + 1 < len(axis_values) else axis_high
            a = max(axis_low, prev_mid - lane_pad)
            b = min(axis_high, next_mid + lane_pad)

            if side == "left":
                lane_bbox = [bx1 - outside_px, a, bx1 + inside_px, b]
            elif side == "right":
                lane_bbox = [bx2 - inside_px, a, bx2 + outside_px, b]
            elif side == "top":
                lane_bbox = [a, by1 - outside_px, b, by1 + inside_px]
            else:
                lane_bbox = [a, by2 - inside_px, b, by2 + outside_px]

            lanes.append({
                "terminal_id": term.get("terminal_id"),
                "term": term,
                "side": side,
                "lane_bbox": _clamp_bbox(lane_bbox, image_shape),
                "axis_range": [float(a), float(b)],
            })

        band_bbox = _union_bbox([lane["lane_bbox"] for lane in lanes], image_shape)
        if band_bbox is None:
            continue

        side_runs[side] = {
            "side": side,
            "band_bbox": band_bbox,
            "lanes": lanes,
        }

    return side_runs


def _remove_long_lines(binary: np.ndarray, cfg: Dict) -> np.ndarray:
    """
    Rimuove linee lunghe dalla banda OCR.

    I fili del circuito possono attraversare la crop e confondere Tesseract;
    qui li attenuiamo con una pulizia morfologica generale, non basata su testi.
    """
    inv = 255 - binary
    h, w = inv.shape[:2]
    ratio = max(0.10, min(float(cfg["line_kernel_ratio"]), 0.60))
    horiz_len = max(12, int(round(w * ratio)))
    vert_len = max(12, int(round(h * ratio)))

    horiz_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (horiz_len, 1))
    vert_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, vert_len))

    horiz = cv2.morphologyEx(inv, cv2.MORPH_OPEN, horiz_kernel)
    vert = cv2.morphologyEx(inv, cv2.MORPH_OPEN, vert_kernel)
    lines = cv2.bitwise_or(horiz, vert)
    cleaned_inv = cv2.bitwise_and(inv, cv2.bitwise_not(lines))
    return 255 - cleaned_inv


def _prepare_side_band(crop_bgr, cfg: Dict) -> Tuple[np.ndarray, float]:
    """
    Prepara una banda laterale per Tesseract: grayscale, upscale, threshold e
    rimozione delle linee lunghe.
    """
    gray = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4)).apply(gray)
    scale = _effective_ocr_upscale(cfg)
    if scale != 1.0:
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cleaned = _remove_long_lines(binary, cfg)
    return cleaned, scale


# =========================================================
# OCR NUMERICO E FALLBACK SU COMPONENTI CONNESSI
# =========================================================

def _extract_digit_components(image_bgr, band_bbox: List[int]) -> List[Dict]:
    """
    Estrae piccoli componenti connessi candidati a cifre vicino al body.
    """
    crop = _crop(image_bgr, band_bbox)
    if crop is None:
        return []

    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4)).apply(gray)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    inv = 255 - binary
    count, labels, stats, centroids = cv2.connectedComponentsWithStats(inv, 8)

    x0, y0, _, _ = band_bbox
    components = []
    for idx in range(1, count):
        x, y, w, h, area = stats[idx]
        if area < 10 or area > 260:
            continue
        if h < 8 or h > 28 or w < 2 or w > 26:
            continue
        components.append({
            "bbox": [int(x0 + x), int(y0 + y), int(x0 + x + w), int(y0 + y + h)],
            "center": [float(x0 + centroids[idx][0]), float(y0 + centroids[idx][1])],
            "area": int(area),
        })
    return components


def _group_digit_components(components: List[Dict]) -> List[Dict]:
    """
    Raggruppa componenti connessi allineati, cosi numeri a due cifre come 10 o
    13 possono essere letti come un unico candidato.
    """
    lines: List[List[Dict]] = []
    for comp in sorted(components, key=lambda item: item["center"][1]):
        for line in lines:
            baseline = sum(item["center"][1] for item in line) / max(len(line), 1)
            if abs(comp["center"][1] - baseline) <= 8:
                line.append(comp)
                break
        else:
            lines.append([comp])

    groups: List[List[Dict]] = []
    for line in lines:
        current: List[Dict] = []
        for comp in sorted(line, key=lambda item: item["bbox"][0]):
            if not current:
                current = [comp]
                continue
            right_edge = max(item["bbox"][2] for item in current)
            gap = comp["bbox"][0] - right_edge
            if -3 <= gap <= 12:
                current.append(comp)
            else:
                groups.append(current)
                current = [comp]
        if current:
            groups.append(current)

    candidates = []
    for group in groups:
        x1 = min(item["bbox"][0] for item in group)
        y1 = min(item["bbox"][1] for item in group)
        x2 = max(item["bbox"][2] for item in group)
        y2 = max(item["bbox"][3] for item in group)
        candidates.append({
            "bbox": [int(x1), int(y1), int(x2), int(y2)],
            "center": [(x1 + x2) * 0.5, (y1 + y2) * 0.5],
            "component_count": len(group),
            "components": group,
        })
    return candidates


def _ocr_digit_variants(image_bgr, bbox: List[int], variants: List[Tuple[int, float, str, int]]) -> Dict[str, int]:
    """
    Rilegge una cifra con piu' varianti di pad/scala/PSM e restituisce voti.
    """
    try:
        import pytesseract
    except Exception:
        return {}

    votes: Dict[str, int] = {}
    for pad, scale, mode, psm in variants:
        x1, y1, x2, y2 = _clamp_bbox(
            [bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad],
            image_bgr.shape,
        )
        crop = image_bgr[y1:y2 + 1, x1:x2 + 1]
        if crop.size == 0:
            continue
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        image = gray if mode == "gray" else binary
        config = f"--oem 3 --psm {psm} -c tessedit_char_whitelist=0123456789"
        raw = pytesseract.image_to_string(image, config=config)
        text = re.sub(r"[^0-9]", "", str(raw or ""))
        if not text:
            continue

        weight = 1
        if mode == "bin":
            weight += 1
        if pad in {4, 6, 10}:
            weight += 1
        if psm in {6, 7, 10, 11}:
            weight += 1
        votes[text] = votes.get(text, 0) + weight

    return votes


def _ocr_digit_candidates_batch(
    image_bgr,
    candidates: List[Dict],
    cfg: Dict,
    expanded_variants: bool = False,
) -> Dict[int, Dict[str, int]]:
    """
    Versione batch del fallback numerico: chiama Tesseract una volta per gruppo
    di crop invece che una volta per cifra.
    """
    if not candidates:
        return {}

    tesseract_cmd = os.environ.get("TESSERACT_CMD", "tesseract")
    variants = [
        (2, 6.0, "bin", 6),
        (4, 4.0, "bin", 6),
        (4, 4.0, "bin", 8),
        (4, 4.0, "gray", 8),
        (4, 6.0, "bin", 10),
        (4, 6.0, "bin", 8),
        (4, 6.0, "gray", 13),
        (6, 4.0, "gray", 6),
        (6, 6.0, "bin", 8),
        (10, 8.0, "bin", 6),
        (10, 8.0, "gray", 6),
        (14, 6.0, "bin", 8),
    ]
    if expanded_variants:
        variants.extend([
            (6, 10.0, "bin", 6),
            (10, 8.0, "gray", 11),
            (14, 8.0, "gray", 11),
        ])

    votes_by_candidate = {idx: {} for idx in range(len(candidates))}
    tmp_root = Path(os.environ.get("IC_PIN_OCR_TMP_DIR", ".tmp/ic_pin_ocr"))
    work_dir = tmp_root / uuid.uuid4().hex
    try:
        work_dir.mkdir(parents=True, exist_ok=True)

        for variant_idx, (pad, scale, mode, psm) in enumerate(variants):
            variant_dir = work_dir / f"v{variant_idx}"
            variant_dir.mkdir(parents=True, exist_ok=True)
            paths = []

            for idx, candidate in enumerate(candidates):
                bbox = candidate["bbox"]
                x1, y1, x2, y2 = _clamp_bbox(
                    [bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad],
                    image_bgr.shape,
                )
                crop = image_bgr[y1:y2 + 1, x1:x2 + 1]
                if crop.size == 0:
                    continue

                gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
                gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
                _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                image = gray if mode == "gray" else binary

                path = variant_dir / f"{idx:04d}.png"
                if cv2.imwrite(str(path), image):
                    paths.append((idx, path.resolve()))

            if not paths:
                continue

            list_path = variant_dir / "images.txt"
            list_path.write_text("\n".join(str(path) for _, path in paths), encoding="utf-8")
            output_base = variant_dir / "out"
            cmd = [
                tesseract_cmd,
                str(list_path.resolve()),
                str(output_base.resolve()),
                "--oem",
                "3",
                "--psm",
                str(psm),
                "-c",
                "tessedit_char_whitelist=0123456789",
                "tsv",
            ]
            try:
                subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=False)
            except Exception:
                continue

            tsv_path = Path(str(output_base) + ".tsv")
            if not tsv_path.exists():
                continue

            page_to_candidate = {page_idx + 1: candidate_idx for page_idx, (candidate_idx, _) in enumerate(paths)}
            for line in tsv_path.read_text(encoding="utf-8", errors="ignore").splitlines()[1:]:
                parts = line.split("\t")
                if len(parts) < 12:
                    continue
                try:
                    page_num = int(parts[1])
                except Exception:
                    continue
                candidate_idx = page_to_candidate.get(page_num)
                if candidate_idx is None:
                    continue

                text = re.sub(r"[^0-9]", "", parts[11] or "")
                if not text:
                    continue

                weight = 1
                if mode == "bin":
                    weight += 1
                if psm in {6, 8, 10, 13}:
                    weight += 1
                votes = votes_by_candidate[candidate_idx]
                votes[text] = votes.get(text, 0) + weight
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)

    return votes_by_candidate


def _component_hole_count(image_bgr, bbox: List[int]) -> int:
    """
    Conta buchi interni nella cifra candidata; aiuta nei casi ambigui 3/4/5/8.
    """
    crop = _crop(image_bgr, bbox)
    if crop is None or crop.size == 0:
        return 0

    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4)).apply(gray)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    inv = 255 - binary
    contours, hierarchy = cv2.findContours(inv, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    if hierarchy is None:
        return 0

    holes = 0
    for idx, contour in enumerate(contours):
        parent = hierarchy[0][idx][3]
        if parent < 0:
            continue
        if cv2.contourArea(contour) >= 1.5:
            holes += 1
    return holes


def _best_voted_number(votes: Dict[str, int], component_count: int, cfg: Dict) -> Optional[str]:
    """
    Sceglie il numero migliore dai voti OCR, rispettando pattern e lunghezza
    attesa.
    """
    filtered = {}
    max_len = 2 if component_count <= 2 else 3
    for text, score in votes.items():
        if not _is_number_text(text, cfg):
            continue
        if len(text) > max_len:
            continue
        filtered[text] = score
    if not filtered:
        return None

    if component_count >= 2:
        multi_digit = {
            text: score
            for text, score in filtered.items()
            if len(text) >= 2 and score >= 2
        }
        if multi_digit:
            filtered = multi_digit

        expected_len = max(2, min(component_count, max_len))
        return sorted(
            filtered,
            key=lambda item: (abs(len(item) - expected_len), -filtered[item], -len(item)),
        )[0]

    return sorted(
        filtered,
        key=lambda item: (-filtered[item], abs(len(item) - max(1, component_count)), -len(item)),
    )[0]


def _ocr_single_digit_component(image_bgr, bbox: List[int], cfg: Dict) -> Optional[str]:
    variants = [
        (4, 4.0, "bin", 6),
        (4, 4.0, "bin", 10),
        (6, 6.0, "bin", 10),
        (10, 6.0, "bin", 10),
    ]
    text = _best_voted_number(_ocr_digit_variants(image_bgr, bbox, variants), 1, cfg)
    return text if text and len(text) == 1 else None


def _ocr_split_digit_group(image_bgr, components: List[Dict], cfg: Dict) -> Optional[str]:
    digits = []
    for comp in sorted(components, key=lambda item: item["bbox"][0]):
        digit = _ocr_single_digit_component(image_bgr, comp["bbox"], cfg)
        if digit is None:
            return None
        digits.append(digit)
    text = "".join(digits)
    return text if _is_number_text(text, cfg) and len(text) >= 2 else None


def _ocr_digit_component_candidate(image_bgr, bbox: List[int], component_count: int, cfg: Dict) -> Optional[Dict]:
    variants = [
        (4, 4.0, "bin", 6),
        (4, 4.0, "bin", 7),
        (4, 4.0, "bin", 10),
        (4, 6.0, "bin", 6),
        (4, 6.0, "bin", 7),
        (4, 6.0, "bin", 10),
        (6, 4.0, "gray", 6),
        (6, 4.0, "gray", 8),
        (6, 4.0, "gray", 13),
        (6, 6.0, "bin", 8),
        (6, 6.0, "bin", 13),
        (10, 4.0, "bin", 6),
        (10, 4.0, "bin", 7),
        (10, 4.0, "bin", 10),
        (10, 6.0, "gray", 8),
        (10, 6.0, "gray", 13),
        (10, 8.0, "gray", 6),
        (10, 8.0, "bin", 6),
        (10, 8.0, "bin", 7),
        (10, 8.0, "bin", 10),
        (14, 6.0, "bin", 6),
        (14, 6.0, "bin", 8),
        (14, 6.0, "bin", 13),
    ]
    votes = _ocr_digit_variants(image_bgr, bbox, variants)
    text = _best_voted_number(votes, component_count, cfg)
    if text is None:
        return None

    confidence = min(0.74, 0.44 + 0.015 * votes.get(text, 1))
    width, height = _bbox_size(bbox)
    if (
        component_count == 1
        and text in {"3", "4", "5"}
        and width >= 6.0
        and height >= 12.0
        and _component_hole_count(image_bgr, bbox) >= 2
    ):
        text = "8"
        confidence = max(confidence, 0.76)
    return {
        "text": text,
        "confidence": confidence,
        "bbox": bbox,
        "center": [(bbox[0] + bbox[2]) * 0.5, (bbox[1] + bbox[3]) * 0.5],
        "mode": "number_component",
    }


def _expand_component_bbox_for_refine(bbox: List[int], side: str, image_shape, pad_px: int) -> List[int]:
    if side in {"left", "right"}:
        return _clamp_bbox([bbox[0] - pad_px, bbox[1], bbox[2] + pad_px, bbox[3]], image_shape)
    return _clamp_bbox([bbox[0], bbox[1] - pad_px, bbox[2], bbox[3] + pad_px], image_shape)


def _prefer_component_refinement(current: Dict, refined: Dict) -> bool:
    current_text = str(current.get("text") or "")
    refined_text = str(refined.get("text") or "")
    if not refined_text:
        return False

    current_conf = float(current.get("confidence") or 0.0)
    refined_conf = float(refined.get("confidence") or 0.0)
    if len(refined_text) > len(current_text) and refined_conf >= (current_conf - 0.08):
        return True
    if len(refined_text) == len(current_text) == 1 and current_conf >= 0.60:
        return refined_conf >= (current_conf + 0.18)
    if len(refined_text) == len(current_text) and refined_conf >= (current_conf + 0.04):
        return True
    return False


def _refine_component_fallback_word(image_bgr, word: Dict, side: str, cfg: Dict) -> Dict:
    """
    Raffina un candidato numerico del fallback in modo conservativo.

    Non sostituisce un numero gia' credibile con una rilettura appena migliore:
    il refinement deve dare un vantaggio chiaro.
    """
    refined = dict(word)
    component_count = int(word.get("component_count") or 0)
    bbox = word.get("bbox")
    if not bbox or component_count <= 0:
        return refined
    current_text = str(word.get("text") or "")
    current_conf = float(word.get("confidence") or 0.0)

    if component_count == 1 and len(current_text) == 1 and current_conf < 0.72:
        local = _ocr_digit_component_candidate(image_bgr, bbox, component_count, cfg)
        if local is not None and _prefer_component_refinement(refined, local):
            refined = {
                **refined,
                **local,
                "component_count": component_count,
                "mode": "number_component_refine",
            }

    if component_count >= 2 and side in {"left", "right"} and len(current_text) == 1 and current_conf < 0.64:
        expanded_bbox = _expand_component_bbox_for_refine(bbox, side, image_bgr.shape, pad_px=4)
        expanded = _ocr_digit_component_candidate(image_bgr, expanded_bbox, component_count, cfg)
        if expanded is not None and _prefer_component_refinement(refined, expanded):
            refined = {
                **refined,
                **expanded,
                "component_count": component_count,
                "mode": "number_component_refine_wide",
            }

    width, height = _bbox_size(bbox)
    if (
        component_count == 1
        and side in {"left", "right"}
        and refined.get("text") == "1"
        and float(refined.get("confidence") or 0.0) < 0.70
        and width >= 6.0
        and height >= 18.0
    ):
        expanded_bbox = _expand_component_bbox_for_refine(bbox, side, image_bgr.shape, pad_px=4)
        votes = _ocr_digit_variants(
            image_bgr,
            expanded_bbox,
            [
                (4, 3.0, "bin", 8),
                (4, 3.0, "bin", 13),
                (4, 4.0, "bin", 8),
                (4, 4.0, "bin", 13),
                (4, 6.0, "bin", 8),
                (4, 6.0, "bin", 13),
            ],
        )
        alt_text = _best_voted_number(votes, 1, cfg)
        alt_score = int(votes.get(alt_text, 0)) if alt_text else 0
        if alt_text and alt_text != "1" and alt_score >= 12:
            refined = {
                **refined,
                "text": alt_text,
                "confidence": max(float(refined.get("confidence") or 0.0), min(0.74, 0.44 + 0.015 * alt_score)),
                "bbox": expanded_bbox,
                "center": [(expanded_bbox[0] + expanded_bbox[2]) * 0.5, (expanded_bbox[1] + expanded_bbox[3]) * 0.5],
                "mode": "number_component_refine_side_alt",
                "component_count": component_count,
            }

    if (
        component_count == 1
        and side in {"left", "right"}
        and refined.get("text") == "8"
        and width >= 6.0
        and height >= 18.0
    ):
        expanded_bbox = _expand_component_bbox_for_refine(bbox, side, image_bgr.shape, pad_px=2)
        votes = _ocr_digit_variants(
            image_bgr,
            expanded_bbox,
            [
                (4, 3.0, "bin", 8),
                (4, 3.0, "bin", 13),
                (4, 4.0, "bin", 8),
                (4, 4.0, "bin", 13),
                (4, 6.0, "bin", 8),
                (4, 6.0, "bin", 13),
            ],
        )
        alt_text = _best_voted_number(votes, 1, cfg)
        alt_score = int(votes.get(alt_text, 0)) if alt_text else 0
        if alt_text == "9" and alt_score >= 6:
            refined = {
                **refined,
                "text": "9",
                "confidence": max(float(refined.get("confidence") or 0.0), min(0.74, 0.44 + 0.015 * alt_score)),
                "bbox": expanded_bbox,
                "center": [(expanded_bbox[0] + expanded_bbox[2]) * 0.5, (expanded_bbox[1] + expanded_bbox[3]) * 0.5],
                "mode": "number_component_refine_side_89",
                "component_count": component_count,
            }

    return refined


def _component_number_words(image_bgr, side_run: Dict, cfg: Dict, target_lanes: Optional[List[Dict]] = None) -> List[Dict]:
    """
    Produce parole numeriche candidate a partire dai componenti connessi della
    banda laterale.
    """
    components = _extract_digit_components(image_bgr, side_run["band_bbox"])
    lanes = target_lanes if target_lanes is not None else side_run["lanes"]
    candidates = []
    for candidate in _group_digit_components(components):
        cx, cy = candidate["center"]
        if not any(_bbox_contains_point(lane["lane_bbox"], cx, cy) for lane in lanes):
            continue
        candidates.append(candidate)

    expanded_variants = side_run["side"] == "top" and len(side_run.get("lanes") or []) <= 2
    votes_by_candidate = _ocr_digit_candidates_batch(
        image_bgr,
        candidates,
        cfg,
        expanded_variants=expanded_variants,
    )
    words = []
    for idx, candidate in enumerate(candidates):
        votes = votes_by_candidate.get(idx, {})
        text = _best_voted_number(votes, candidate["component_count"], cfg)
        if text is None:
            continue

        confidence = min(0.74, 0.44 + 0.015 * votes.get(text, 1))
        words.append({
            "text": text,
            "confidence": confidence,
            "bbox": candidate["bbox"],
            "center": candidate["center"],
            "mode": "number_component_batch",
            "component_count": candidate["component_count"],
        })
    return words


# =========================================================
# OCR TESSERACT SULLE BANDE LATERALI
# =========================================================

def _clean_token_text(raw: str) -> str:
    text = _TEXT_ALLOWED_RE.sub("", str(raw or ""))
    return text.strip()


def _run_tesseract_words(
    prepared: np.ndarray,
    side_bbox: List[int],
    scale: float,
    cfg: Dict,
    mode: str,
) -> Tuple[List[Dict], Dict]:
    """
    Esegue Tesseract su una banda OCR e ritorna parole con bbox assoluti.

    mode="number" usa whitelist numerica; mode="text" usa whitelist testuale.
    """
    try:
        import pytesseract
        from pytesseract import Output
    except Exception as exc:
        return [], {"ok": False, "error": f"pytesseract_import_failed:{exc}"}

    tesseract_cmd = os.environ.get("TESSERACT_CMD")
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    if mode == "number":
        if not cfg["number_enabled"]:
            return [], {"ok": True, "skipped": "number_disabled"}
        config = (
            f"--oem 3 --psm {int(cfg['number_psm'])} "
            "-c tessedit_char_whitelist=0123456789"
        )
    else:
        if not cfg["label_enabled"] and not cfg["label_guard_enabled"]:
            return [], {"ok": True, "skipped": "label_disabled"}
        whitelist = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_./+-"
        config = (
            f"--oem 3 --psm {int(cfg['label_psm'])} "
            f"-c tessedit_char_whitelist={whitelist}"
        )

    try:
        data = pytesseract.image_to_data(prepared, config=config, output_type=Output.DICT)
    except Exception as exc:
        return [], {"ok": False, "error": f"pytesseract_runtime_failed:{exc}"}

    words = []
    sx1, sy1, _, _ = side_bbox
    for idx, raw in enumerate(data.get("text", [])):
        text = re.sub(r"[^0-9]", "", str(raw or "")) if mode == "number" else _clean_token_text(raw)
        if not text:
            continue

        try:
            conf = float(data["conf"][idx]) / 100.0
        except Exception:
            conf = -1.0
        if conf < 0:
            continue

        x = int(data["left"][idx])
        y = int(data["top"][idx])
        w = int(data["width"][idx])
        h = int(data["height"][idx])
        if w <= 0 or h <= 0:
            continue

        bbox_side = [x, y, x + w, y + h]
        bbox_img = [
            int(round(sx1 + (bbox_side[0] / scale))),
            int(round(sy1 + (bbox_side[1] / scale))),
            int(round(sx1 + (bbox_side[2] / scale))),
            int(round(sy1 + (bbox_side[3] / scale))),
        ]
        center_x = (bbox_img[0] + bbox_img[2]) * 0.5
        center_y = (bbox_img[1] + bbox_img[3]) * 0.5

        words.append({
            "text": text,
            "confidence": max(0.0, min(1.0, conf)),
            "bbox": bbox_img,
            "center": [center_x, center_y],
            "mode": mode,
        })

    return words, {"ok": True, "word_count": len(words), "mode": mode}


# =========================================================
# NORMALIZZAZIONE, FILTRI E SCORING DEI CANDIDATI
# =========================================================

def _word_edge_distance(word: Dict, side: str, body_bbox: List[float]) -> float:
    bx1, by1, bx2, by2 = [float(v) for v in body_bbox]
    cx, cy = word["center"]
    if side == "left":
        return abs(cx - bx1)
    if side == "right":
        return abs(cx - bx2)
    if side == "top":
        return abs(cy - by1)
    return abs(cy - by2)


def _closest_body_side(word: Dict, body_bbox: List[float]) -> str:
    bx1, by1, bx2, by2 = [float(v) for v in body_bbox]
    cx, cy = word["center"]
    distances = {
        "left": abs(cx - bx1),
        "right": abs(cx - bx2),
        "top": abs(cy - by1),
        "bottom": abs(cy - by2),
    }
    return min(distances, key=distances.get)


def _assign_words_to_lanes(words: List[Dict], lanes: List[Dict]) -> Dict[str, List[Dict]]:
    assigned = {lane["terminal_id"]: [] for lane in lanes}
    for word in words:
        cx, cy = word["center"]
        matching_lanes = []
        for lane in lanes:
            if _bbox_contains_point(lane["lane_bbox"], cx, cy):
                side = lane.get("side") or ""
                term = lane.get("term") or {}
                term_axis = float(term.get("y", 0.0)) if side in {"left", "right"} else float(term.get("x", 0.0))
                word_axis = float(cy) if side in {"left", "right"} else float(cx)
                matching_lanes.append((abs(word_axis - term_axis), lane))
        if not matching_lanes:
            continue

        matching_lanes.sort(key=lambda item: item[0])
        assigned[matching_lanes[0][1]["terminal_id"]].append(word)
    return assigned


def _is_number_text(text: str, cfg: Dict) -> bool:
    if not re.match(cfg["number_pattern"], text or ""):
        return False
    try:
        return int(text) >= 1
    except Exception:
        return False


def _normalize_pin_label_text(text: str) -> str:
    """
    Normalizza una label pin senza contesto del componente.

    Esempi: P17 -> P1.7, NTR -> INTR, VREFI2 -> VREF/2.
    """
    text = str(text or "").strip()
    if not text:
        return ""

    compact = re.sub(r"\s+", "", text)
    upper = compact.upper()

    if re.fullmatch(r"[A-H]", upper):
        return upper.lower()
    if upper in _SHORT_PIN_LABELS:
        return upper
    if upper in _PIN_LABEL_OCR_ALIASES:
        return _PIN_LABEL_OCR_ALIASES[upper]
    if upper == "NTR":
        return "INTR"
    if re.fullmatch(r"VREF(?:[IL1]|/)?2", upper):
        return "VREF/2"
    if re.fullmatch(r"D[0-9]{1,2}", upper):
        return upper
    if re.fullmatch(r"P[0-3]\.?[0-7]", upper):
        return f"P{upper[1]}.{upper[-1]}"
    if re.fullmatch(r"P[IL1]\.?[0-7]", upper):
        return f"P1.{upper[-1]}"
    if re.fullmatch(r"P[OQ0]\.?[0-7]", upper):
        return f"P0.{upper[-1]}"
    return compact


def _normalize_label_text_for_cfg(text: str, cfg: Dict) -> str:
    """
    Normalizza una label usando anche il contesto del componente.

    Per i display 7 segmenti accetta confusioni OCR tipiche delle lettere
    minuscole, come 4 -> a e q -> g.
    """
    normalized = _normalize_pin_label_text(text)
    if cfg.get("component_subtype") != "seven_segment_display":
        return normalized

    compact = re.sub(r"\s+", "", str(text or "")).upper()
    seven_segment_aliases = {
        "4": "a",
        "Q": "g",
    }
    return seven_segment_aliases.get(compact, normalized)


def _is_rejected_pin_label(text: str) -> bool:
    upper = str(text or "").upper()
    return any(pattern.match(upper) for pattern in _PIN_LABEL_REJECT_PATTERNS)


def _is_ocr_alias_acceptable(raw_text: str, normalized_text: str, word: Dict, cfg: Dict) -> bool:
    raw_upper = re.sub(r"\s+", "", str(raw_text or "")).upper()
    if _PIN_LABEL_OCR_ALIASES.get(raw_upper) != normalized_text:
        return False

    confidence = float(word.get("confidence") or 0.0)
    if normalized_text == "OUT":
        return confidence >= 0.25

    if normalized_text == "ADJ":
        if confidence >= 0.20:
            return True
        body_bbox = cfg.get("body_bbox")
        word_bbox = word.get("bbox")
        if not body_bbox or not word_bbox:
            return False
        body_w = max(1.0, float(body_bbox[2]) - float(body_bbox[0]))
        word_w = max(0.0, float(word_bbox[2]) - float(word_bbox[0]))
        return word_w >= body_w * 0.20

    return confidence >= 0.35


def _is_label_candidate(word: Dict, cfg: Dict) -> bool:
    """
    Decide se una parola OCR puo' diventare pin_label_text.

    Sugli IC normali resta selettiva per evitare marking/net label; sui display
    7 segmenti accetta anche label singole a..h.
    """
    raw_text = str(word.get("text") or "")
    text = _normalize_label_text_for_cfg(word.get("text") or "", cfg)
    confidence = float(word.get("confidence") or 0.0)
    if not text or _is_number_text(text, cfg):
        return False
    if _is_rejected_pin_label(text):
        return False
    if not re.search(r"[A-Za-z]", text):
        return False
    if not re.match(cfg["label_pattern"], text):
        return False

    upper = text.upper()
    digit_count = sum(ch.isdigit() for ch in upper)
    if len(upper) < 2:
        if (
            cfg.get("component_subtype") == "seven_segment_display"
            and re.fullmatch(r"[A-H]", upper)
        ):
            return confidence >= max(cfg["label_min_confidence"], 0.05)
        return False
    if upper in _SHORT_PIN_LABELS:
        if upper == "CS" and word.get("mode") == "text_inner_strip":
            return confidence >= 0.15
        if _is_ocr_alias_acceptable(raw_text, upper, word, cfg):
            return True
        return confidence >= max(cfg["label_min_confidence"], 0.35)
    if re.match(r"^[A-Z]{1,4}[0-9]{3,}[A-Z0-9]*$", upper):
        return False
    if (
        word.get("mode") == "easyocr_body_label"
        and re.fullmatch(r"L[0-9]{1,2}", upper)
    ):
        return confidence >= 0.30
    if re.fullmatch(r"P[0-3]\.[0-7]", upper):
        return confidence >= max(cfg["label_min_confidence"], 0.35)
    if re.match(r"^[A-Z][0-9]{1,2}(?:\.[0-9])?$", upper):
        return confidence >= max(cfg["label_min_confidence"], 0.55)
    if re.match(r"^[A-Z]{1,3}[0-9]{1,2}(?:\.[0-9])?$", upper):
        return confidence >= max(cfg["label_min_confidence"], 0.35)
    if digit_count >= 3:
        return confidence >= max(cfg["label_min_confidence"], 0.80)
    return len(upper) >= 3 and confidence >= max(cfg["label_min_confidence"], 0.45)


def _is_label_guard_candidate(word: Dict, cfg: Dict) -> bool:
    """
    Decide se una parola testuale deve proteggere una zona da falsi numeri.

    Una guard word non e' necessariamente la label finale, ma impedisce per
    esempio che BOOT/COM venga interpretato come numero.
    """
    text = _normalize_label_text_for_cfg(word.get("text") or "", cfg)
    confidence = float(word.get("confidence") or 0.0)
    if not text or not re.search(r"[A-Za-z]", text):
        return False
    if _is_rejected_pin_label(text):
        return False
    if not re.match(cfg["label_pattern"], text):
        return False

    upper = text.upper()
    if (
        cfg.get("component_subtype") == "seven_segment_display"
        and re.fullmatch(r"[A-H]", upper)
    ):
        return confidence >= 0.03
    if upper in _SHORT_PIN_LABELS:
        return confidence >= 0.08
    if re.match(r"^[A-Z][0-9]{1,2}(?:\.[0-9])?$", upper):
        return confidence >= 0.05
    if re.match(r"^[A-Z]{1,3}[0-9]{1,2}(?:\.[0-9])?$", upper):
        return confidence >= 0.08
    return _is_label_candidate(word, cfg)


def _label_pick_distance(side: str, cfg: Dict) -> float:
    return float(cfg["max_label_distance_px"])


def _number_pick_distance(side: str, cfg: Dict, has_side_label_guards: bool = False) -> float:
    max_distance = float(cfg["max_number_distance_px"])
    if side in {"left", "right"}:
        return min(max_distance, 22.0 if has_side_label_guards else 32.0)
    return max_distance


def _pick_best_word(words: List[Dict], side: str, body_bbox: List[float], max_distance_px: float) -> Optional[Dict]:
    """
    Sceglie il miglior candidato numerico privilegiando vicinanza al bordo,
    confidenza e lunghezza.
    """
    if not words:
        return None

    ranked = []
    for word in words:
        edge_distance = _word_edge_distance(word, side, body_bbox)
        if edge_distance > max_distance_px:
            continue
        ranked.append((edge_distance, -float(word["confidence"]), -len(word["text"]), word))

    if not ranked:
        return None

    ranked.sort(key=lambda item: item[:3])
    chosen = dict(ranked[0][3])
    chosen["edge_distance"] = round(float(ranked[0][0]), 3)
    return chosen


def _label_priority(text: str) -> int:
    upper = str(text or "").upper()
    if re.fullmatch(r"P[0-3]\.[0-7]", upper):
        return 5
    if re.fullmatch(r"D[0-9]{1,2}", upper):
        return 5
    if upper in _SHORT_PIN_LABELS:
        return 4
    if re.fullmatch(r"[A-Z]{1,3}[0-9]{1,2}(?:\.[0-9])?", upper):
        return 3
    if "/" in upper:
        return 3
    return 1


def _overlaps_marking_bbox(word: Dict, cfg: Dict) -> bool:
    marking_bbox = cfg.get("marking_bbox")
    word_bbox = word.get("bbox")
    if not marking_bbox or not word_bbox:
        return False
    return _bbox_overlap_ratio(word_bbox, marking_bbox) >= float(
        cfg.get("marking_reject_overlap_ratio", 0.20)
    )


def _dedupe_words(words: List[Dict]) -> List[Dict]:
    """
    Rimuove duplicati OCR quasi sovrapposti mantenendo il piu' confidente.
    """
    deduped: List[Dict] = []
    for word in words:
        text = str(word.get("text") or "")
        cx, cy = word.get("center") or [0.0, 0.0]
        replaced = False
        for idx, existing in enumerate(deduped):
            if str(existing.get("text") or "") != text:
                continue
            ex, ey = existing.get("center") or [0.0, 0.0]
            if abs(float(cx) - float(ex)) <= 8.0 and abs(float(cy) - float(ey)) <= 8.0:
                if float(word.get("confidence") or 0.0) > float(existing.get("confidence") or 0.0):
                    deduped[idx] = word
                replaced = True
                break
        if not replaced:
            deduped.append(word)
    return deduped


def _normalize_label_word(word: Dict, cfg: Dict) -> Dict:
    normalized = _normalize_label_text_for_cfg(word.get("text") or "", cfg)
    if normalized == str(word.get("text") or ""):
        return word
    updated = dict(word)
    updated["text"] = normalized
    return updated


def _inner_strip_numeric_candidates(
    words: List[Dict],
    side: str,
    body_bbox,
    cfg: Dict,
) -> List[Dict]:
    """
    Estrae candidati numerici dalla strip interna vicina al lato.

    Qui Tesseract spesso legge meglio piccoli pin number aderenti al bordo del
    package rispetto all'OCR della corsia larga. Sono candidati utili sia per
    singole cifre sia per numeri a due cifre.
    """
    candidates: List[Dict] = []
    min_conf = max(cfg["label_min_confidence"], 0.35)

    for word in words:
        if word.get("mode") != "text_inner_strip":
            continue
        text = str(word.get("text") or "")
        if float(word.get("confidence") or 0.0) < min_conf:
            continue
        if not _is_number_text(text, cfg):
            continue
        if body_bbox is not None and _word_edge_distance(word, side, body_bbox) > 18.0:
            continue
        candidates.append(word)

    return candidates


# =========================================================
# OCR SU STRIP INTERNA ED EASYOCR DI SUPPORTO
# =========================================================

def _build_inner_label_strip_bbox(
    side_run: Dict,
    body_bbox: List[float],
    image_shape,
    cfg: Dict,
) -> Optional[List[int]]:
    """
    Costruisce una strip dentro il body vicino al lato corrente.

    Serve per leggere label disegnate appena all'interno del package.
    """
    side = side_run["side"]
    bx1, by1, bx2, by2 = [int(round(v)) for v in body_bbox]
    band = side_run["band_bbox"]
    body_w = max(1, bx2 - bx1)
    body_h = max(1, by2 - by1)

    if side in {"left", "right"}:
        strip_w = max(28, min(int(round(body_w * 0.40)), int(cfg["side_inside_px"])))
        y1 = max(by1, int(band[1]))
        y2 = min(by2, int(band[3]))
        if side == "left":
            x1 = bx1 + 2
            x2 = min(bx2 - 2, bx1 + strip_w)
        else:
            x1 = max(bx1 + 2, bx2 - strip_w)
            x2 = bx2 - 2
    else:
        strip_h = max(24, min(int(round(body_h * 0.28)), int(cfg["top_bottom_inside_px"])))
        x1 = max(bx1, int(band[0]))
        x2 = min(bx2, int(band[2]))
        if side == "top":
            y1 = by1 + 2
            y2 = min(by2 - 2, by1 + strip_h)
        else:
            y1 = max(by1 + 2, by2 - strip_h)
            y2 = by2 - 2

    bbox = _clamp_bbox([x1, y1, x2, y2], image_shape)
    if bbox[2] <= bbox[0] or bbox[3] <= bbox[1]:
        return None
    return bbox


def _prepare_inner_label_strip(crop_bgr, cfg: Dict) -> Tuple[np.ndarray, float]:
    gray = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4)).apply(gray)
    scale = max(_effective_ocr_upscale(cfg), 5.0)
    if scale != 1.0:
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary, scale


def _run_inner_label_strip_words(
    image_bgr,
    side_run: Dict,
    body_bbox: List[float],
    cfg: Dict,
) -> Tuple[List[Dict], Dict]:
    """
    Esegue Tesseract sulla strip interna del lato corrente.
    """
    if not cfg["label_enabled"] and not cfg["label_guard_enabled"]:
        return [], {"ok": True, "skipped": "label_disabled"}

    strip_bbox = _build_inner_label_strip_bbox(side_run, body_bbox, image_bgr.shape, cfg)
    if strip_bbox is None:
        return [], {"ok": True, "skipped": "missing_strip_bbox"}

    crop = _crop(image_bgr, strip_bbox)
    if crop is None:
        return [], {"ok": True, "skipped": "empty_strip_crop"}

    prepared, scale = _prepare_inner_label_strip(crop, cfg)
    strip_cfg = dict(cfg)
    strip_cfg["label_psm"] = 6
    words, info = _run_tesseract_words(prepared, strip_bbox, scale, strip_cfg, mode="text")
    for word in words:
        word["mode"] = "text_inner_strip"
    info["strip_bbox"] = strip_bbox
    return words, info


def _get_easyocr_pin_reader(cfg: Dict):
    global _EASYOCR_PIN_READER, _EASYOCR_PIN_READER_ERROR

    if _EASYOCR_PIN_READER is not None:
        return _EASYOCR_PIN_READER
    if _EASYOCR_PIN_READER_ERROR is not None:
        return None

    try:
        import easyocr
        model_dir = Path(cfg.get("easyocr_label_model_storage_directory") or ".tmp/easyocr")
        model_dir.mkdir(parents=True, exist_ok=True)
        _EASYOCR_PIN_READER = easyocr.Reader(
            cfg.get("easyocr_label_languages") or ["en"],
            gpu=bool(cfg.get("easyocr_label_gpu", False)),
            model_storage_directory=str(model_dir),
            user_network_directory=str(model_dir),
        )
        return _EASYOCR_PIN_READER
    except Exception as exc:
        _EASYOCR_PIN_READER_ERROR = str(exc)
        return None


def _run_easyocr_body_label_words(image_bgr, body_bbox: List[int], cfg: Dict) -> Tuple[List[Dict], Dict]:
    """
    Fallback EasyOCR sulle label nel body.

    Viene usato solo quando non c'e' ic_marking: se abbiamo il part number,
    preferiamo ricavare il significato dei pin dal datasheet.
    """
    if not cfg.get("easyocr_label_enabled", True):
        return [], {"ok": True, "skipped": "easyocr_label_disabled"}

    reader = _get_easyocr_pin_reader(cfg)
    if reader is None:
        return [], {
            "ok": False,
            "error": _EASYOCR_PIN_READER_ERROR or "easyocr_unavailable",
        }

    crop = _crop(image_bgr, body_bbox)
    if crop is None:
        return [], {"ok": True, "skipped": "empty_body_crop"}

    x0, y0, _, _ = body_bbox
    try:
        results = reader.readtext(
            crop,
            detail=1,
            paragraph=False,
            allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789/._+-",
        )
    except Exception as exc:
        return [], {"ok": False, "error": str(exc)}

    words = []
    for box, text, confidence in results:
        raw_text = str(text or "").strip()
        if not raw_text:
            continue

        xs = [float(point[0]) for point in box]
        ys = [float(point[1]) for point in box]
        bbox = [
            int(round(x0 + min(xs))),
            int(round(y0 + min(ys))),
            int(round(x0 + max(xs))),
            int(round(y0 + max(ys))),
        ]
        normalized = _normalize_pin_label_text(raw_text)
        if not normalized:
            continue
        words.append({
            "text": normalized,
            "raw_text": raw_text,
            "confidence": round(float(confidence or 0.0), 4),
            "bbox": bbox,
            "center": [(bbox[0] + bbox[2]) * 0.5, (bbox[1] + bbox[3]) * 0.5],
            "mode": "easyocr_body_label",
        })

    return words, {
        "ok": True,
        "word_count": len(words),
        "engine": "easyocr",
        "body_bbox": body_bbox,
    }


# =========================================================
# ASSEGNAZIONE DEI CANDIDATI ALLE CORSIE
# =========================================================

def _pick_best_label_word(
    words: List[Dict],
    lane: Dict,
    side: str,
    body_bbox: List[float],
    max_distance_px: float,
) -> Optional[Dict]:
    """
    Sceglie la migliore label per una corsia, usando priorita' testuale,
    allineamento al terminale, distanza dal bordo e confidenza.
    """
    if not words:
        return None

    term = lane["term"]
    term_axis = float(term.get("y", 0.0)) if side in {"left", "right"} else float(term.get("x", 0.0))
    ranked = []
    for word in words:
        edge_distance = _word_edge_distance(word, side, body_bbox)
        if edge_distance > max_distance_px:
            continue

        cx, cy = word["center"]
        word_axis = cy if side in {"left", "right"} else cx
        axis_distance = abs(float(word_axis) - term_axis)
        priority = _label_priority(word.get("text") or "")
        ranked.append((-priority, axis_distance, edge_distance, -float(word["confidence"]), -len(word["text"]), word))

    if not ranked:
        return None

    ranked.sort(key=lambda item: item[:5])
    chosen = dict(ranked[0][5])
    chosen["axis_distance"] = round(float(ranked[0][1]), 3)
    chosen["edge_distance"] = round(float(ranked[0][2]), 3)
    chosen["label_priority"] = int(-ranked[0][0])
    return chosen


def _pick_best_lane_word(
    words: List[Dict],
    lane: Dict,
    side: str,
    body_bbox: List[float],
    max_distance_px: float,
    prefer_edge_first: bool = False,
) -> Optional[Dict]:
    """
    Sceglie un candidato numerico per corsia nel fallback sui componenti.
    """
    if not words:
        return None

    term = lane["term"]
    term_axis = float(term.get("y", 0.0)) if side in {"left", "right"} else float(term.get("x", 0.0))
    ranked = []
    for word in words:
        edge_distance = _word_edge_distance(word, side, body_bbox)
        if edge_distance > max_distance_px:
            continue

        cx, cy = word["center"]
        word_axis = cy if side in {"left", "right"} else cx
        axis_distance = abs(float(word_axis) - term_axis)
        if prefer_edge_first:
            ranked.append((edge_distance, axis_distance, -float(word["confidence"]), -len(word["text"]), word))
        else:
            ranked.append((axis_distance, edge_distance, -float(word["confidence"]), -len(word["text"]), word))

    if not ranked:
        return None

    ranked.sort(key=lambda item: item[:4])
    chosen = dict(ranked[0][4])
    chosen["axis_distance"] = round(float(ranked[0][0]), 3)
    chosen["edge_distance"] = round(float(ranked[0][1]), 3)
    return chosen


def _bbox_size(box: List[int]) -> Tuple[float, float]:
    return float(max(0, box[2] - box[0])), float(max(0, box[3] - box[1]))


def _bbox_contains_box(outer: List[int], inner: List[int], tolerance_px: int = 2) -> bool:
    return (
        outer[0] <= inner[0] + tolerance_px
        and outer[1] <= inner[1] + tolerance_px
        and outer[2] >= inner[2] - tolerance_px
        and outer[3] >= inner[3] - tolerance_px
    )


def _should_replace_with_component_candidate(term: Dict, candidate: Dict, side: str) -> bool:
    """
    Decide se il fallback numerico deve sostituire il numero gia' presente.
    """
    current_text = str(term.get("pin_number") or "")
    if not current_text:
        return True

    current_conf = float(term.get("pin_number_confidence") or 0.0)
    candidate_conf = float(candidate.get("confidence") or 0.0)
    debug_payload = term.get("pin_ocr_debug") or {}
    current_best = debug_payload.get("best_number") or {}
    current_mode = str(current_best.get("mode") or "")
    if (
        current_mode == "text_inner_strip"
        and current_conf >= max(0.70, candidate_conf - 0.05)
    ):
        return False
    if (
        current_mode.endswith("_edge_digit")
        and current_conf >= 0.55
        and candidate_conf <= current_conf + 0.10
    ):
        return False

    if len(candidate["text"]) > len(current_text):
        return True
    if len(candidate["text"]) != len(current_text):
        return False

    if current_mode not in {"text", "number"}:
        return False

    current_bbox = current_best.get("bbox") or term.get("pin_number_bbox")
    if not current_bbox:
        return False

    current_w, current_h = _bbox_size(current_bbox)
    candidate_w, candidate_h = _bbox_size(candidate["bbox"])
    current_area = current_w * current_h
    candidate_area = max(1.0, candidate_w * candidate_h)
    candidate_inside_current = _bbox_contains_box(current_bbox, candidate["bbox"])
    oversized_current = (
        (side in {"left", "right"} and current_w >= 28.0)
        or (side in {"top", "bottom"} and current_h >= 28.0)
    )
    much_larger_current = current_area >= (candidate_area * 2.0)
    clearly_better_confidence = candidate_conf >= (current_conf + 0.12)
    candidate_axis_distance = float(candidate.get("axis_distance") or 999.0)
    candidate_edge_distance = float(candidate.get("edge_distance") or 999.0)
    strong_local_component = (
        candidate_axis_distance <= 20.0
        and candidate_edge_distance <= 18.0
    )
    contained_component = (
        candidate_inside_current
        and candidate_conf >= (current_conf + 0.08)
        and current_area >= (candidate_area * 1.5)
        and candidate_axis_distance <= 30.0
        and candidate_edge_distance <= 24.0
    )

    return (
        (
            current_conf < 0.40
            and clearly_better_confidence
            and (oversized_current or much_larger_current)
            and strong_local_component
        )
        or contained_component
    )


def _overlaps_any_label_guard(word: Dict, label_words: List[Dict], cfg: Dict) -> bool:
    body_bbox = cfg.get("body_bbox")
    for label_word in label_words:
        if _bbox_overlap_ratio(word["bbox"], label_word["bbox"]) < cfg["reject_overlap_ratio"]:
            continue

        # Inner-strip OCR can occasionally hallucinate a weak alphanumeric
        # token over the real outline digit. Keep strong labels as guards, but
        # do not let a weak inner token block a digit sitting right on the IC
        # edge while the token itself is clearly deeper inside the body.
        if body_bbox and float(label_word.get("confidence") or 0.0) < 0.30:
            side = _closest_body_side(word, body_bbox)
            if (
                _closest_body_side(label_word, body_bbox) == side
                and _word_edge_distance(word, side, body_bbox) <= 8.0
                and _word_edge_distance(label_word, side, body_bbox) >= 18.0
            ):
                continue

        return True
    return False


def _edge_digit_candidates_from_words(words: List[Dict], side: str, body_bbox: List[float], cfg: Dict) -> List[Dict]:
    """
    Recupera cifre di pin fuse con testo/marking vicino al bordo del package.

    Esempio tipico: OCR legge "9263" perché il marking e il pin "3" sono
    attaccati; sul lato destro il candidato utile è la cifra più a destra.
    """
    if side not in {"left", "right"}:
        return []

    candidates = []
    bx1, _, bx2, _ = [float(v) for v in body_bbox]
    edge_x = bx1 if side == "left" else bx2
    max_distance = _number_pick_distance(side, cfg, has_side_label_guards=False)

    for word in words:
        raw_text = str(word.get("text") or "")
        if _is_number_text(raw_text, cfg):
            continue

        digits = re.findall(r"[0-9]", raw_text)
        if len(digits) < 2:
            continue

        bbox = word.get("bbox") or []
        if len(bbox) != 4:
            continue

        x1, y1, x2, y2 = [float(v) for v in bbox]
        width = max(1.0, x2 - x1)
        edge_distance = abs((x1 if side == "left" else x2) - edge_x)
        if edge_distance > max_distance:
            continue

        digit = digits[0] if side == "left" else digits[-1]
        digit_index = raw_text.find(digit) if side == "left" else raw_text.rfind(digit)
        char_count = max(len(raw_text), 1)
        char_w = width / float(char_count)

        cx = x1 + (digit_index + 0.5) * char_w
        dx1 = x1 + digit_index * char_w
        dx2 = x1 + (digit_index + 1) * char_w
        candidate = dict(word)
        candidate["text"] = digit
        candidate["confidence"] = max(float(word.get("confidence") or 0.0), 0.62)
        candidate["center"] = [round(float(cx), 3), round(float((y1 + y2) * 0.5), 3)]
        candidate["bbox"] = [int(round(dx1)), int(round(y1)), int(round(dx2)), int(round(y2))]
        candidate["mode"] = f"{word.get('mode') or 'text'}_edge_digit"
        candidate["source_text"] = raw_text
        candidates.append(candidate)

    return candidates


def _assign_lane_semantics(
    side_run: Dict,
    text_words: List[Dict],
    number_words: List[Dict],
    body_bbox,
    cfg: Dict,
    side_label_guard_words: Optional[List[Dict]] = None,
) -> None:
    """
    Assegna pin_number e pin_label_text ai terminali di un lato.

    Questa e' la funzione centrale del modulo pin OCR: prende parole testuali e
    numeriche gia' lette, le filtra per corsia e scrive i campi finali sui
    terminali locali.
    """
    side = side_run["side"]
    lanes = side_run["lanes"]
    has_side_label_guards = bool(side_label_guard_words)
    text_map = _assign_words_to_lanes(text_words, lanes)
    number_map = _assign_words_to_lanes(number_words, lanes)

    for lane in lanes:
        term = lane["term"]
        lane_text_words = text_map.get(lane["terminal_id"], [])
        lane_number_words = number_map.get(lane["terminal_id"], [])

        label_candidates = [
            _normalize_label_word(word, cfg) for word in lane_text_words
            if not _overlaps_marking_bbox(word, cfg)
            and _is_label_candidate(word, cfg)
        ]
        numeric_from_text = [
            word for word in lane_text_words
            if word["confidence"] >= cfg["label_min_confidence"]
            and _is_number_text(word["text"], cfg)
            and _closest_body_side(word, body_bbox) == side
        ]
        numeric_from_text.extend(_inner_strip_numeric_candidates(
            lane_text_words,
            side,
            body_bbox,
            cfg,
        ))
        numeric_from_text.extend(
            word for word in _edge_digit_candidates_from_words(lane_text_words, side, body_bbox, cfg)
            if _is_number_text(word["text"], cfg)
        )
        numeric_fallback = [
            word for word in lane_number_words
            if word["confidence"] >= cfg["number_min_confidence"]
            and _is_number_text(word["text"], cfg)
            and _closest_body_side(word, body_bbox) == side
        ]

        if label_candidates:
            filtered_fallback = []
            for number_word in numeric_fallback:
                if not _overlaps_any_label_guard(number_word, label_candidates, cfg):
                    filtered_fallback.append(number_word)
            numeric_fallback = filtered_fallback

        best_label = _pick_best_label_word(
            label_candidates,
            lane=lane,
            side=side,
            body_bbox=body_bbox,
            max_distance_px=_label_pick_distance(side, cfg),
        )
        best_number = _pick_best_word(
            numeric_from_text,
            side=side,
            body_bbox=body_bbox,
            max_distance_px=_number_pick_distance(side, cfg, has_side_label_guards),
        )
        if best_number is None:
            best_number = _pick_best_word(
                numeric_fallback,
                side=side,
                body_bbox=body_bbox,
                max_distance_px=_number_pick_distance(side, cfg, has_side_label_guards),
            )

        debug_payload = {
            "side": side,
            "lane_bbox": lane["lane_bbox"],
            "text_words": lane_text_words,
            "number_words": lane_number_words,
        }

        if best_number is not None:
            term["pin_number"] = best_number["text"]
            term["pin_number_confidence"] = round(float(best_number["confidence"]), 3)
            term["pin_number_bbox"] = best_number["bbox"]
            debug_payload["best_number"] = best_number

        if best_label is not None and cfg["label_enabled"]:
            term["pin_label_text"] = best_label["text"]
            term["pin_label_confidence"] = round(float(best_label["confidence"]), 3)
            term["pin_label_bbox"] = best_label["bbox"]
            debug_payload["best_label"] = best_label

        if label_candidates:
            debug_payload["label_guard_words"] = label_candidates

        if best_number is not None or best_label is not None or lane_text_words or lane_number_words:
            term["pin_ocr_debug"] = debug_payload


def _assign_component_number_fallback(
    image_bgr,
    side_run: Dict,
    component_words: List[Dict],
    body_bbox,
    cfg: Dict,
    label_guard_words: Optional[List[Dict]] = None,
) -> None:
    """
    Applica il fallback numerico solo alle corsie che ne hanno bisogno.
    """
    side = side_run["side"]
    has_side_label_guards = bool(label_guard_words)
    component_map = _assign_words_to_lanes(component_words, side_run["lanes"])
    label_guard_map = _assign_words_to_lanes(label_guard_words or [], side_run["lanes"])
    prefer_edge_first = side in {"top", "bottom"} and len(side_run["lanes"]) <= 2

    for lane in side_run["lanes"]:
        term = lane["term"]
        lane_label_guards = label_guard_map.get(lane["terminal_id"], [])
        candidates = [
            word for word in component_map.get(lane["terminal_id"], [])
            if _is_number_text(word["text"], cfg)
            and (side not in {"left", "right"} or _closest_body_side(word, body_bbox) == side)
            and not _overlaps_any_label_guard(word, lane_label_guards, cfg)
        ]
        best = _pick_best_lane_word(
            candidates,
            lane=lane,
            side=side,
            body_bbox=body_bbox,
            max_distance_px=(
                _number_pick_distance(side, cfg, has_side_label_guards)
                if side in {"left", "right"}
                else max(cfg["max_number_distance_px"], 64.0)
            ),
            prefer_edge_first=prefer_edge_first,
        )
        if best is None:
            continue
        best = _refine_component_fallback_word(image_bgr, best, side, cfg)

        should_assign = _should_replace_with_component_candidate(term, best, side)
        if not should_assign:
            continue

        term["pin_number"] = best["text"]
        term["pin_number_confidence"] = round(float(best["confidence"]), 3)
        term["pin_number_bbox"] = best["bbox"]
        debug_payload = term.setdefault("pin_ocr_debug", {})
        debug_payload["component_number_fallback"] = best


def _repair_unique_pin_numbers(component: Dict) -> None:
    terminals = component.get("terminals", []) or []
    if len(terminals) < 4:
        return

    max_pin = len(terminals)
    observed_numeric_values = []
    valid_terms = []
    bad_terms = []
    for term in terminals:
        text = str(term.get("pin_number") or "")
        if re.match(r"^[0-9]+$", text):
            value = int(text)
            observed_numeric_values.append(value)
            if 1 <= value <= max_pin:
                valid_terms.append((value, term))
            else:
                bad_terms.append(term)
        else:
            bad_terms.append(term)

    # This repair is only safe for ICs whose visible numbering appears to
    # follow a compact 1..N scheme. If we already observe a credible number
    # above N (for example 13 on a 12-terminal drawing), do not "normalize"
    # it back into range.
    if any(value > max_pin for value in observed_numeric_values):
        return

    values = [value for value, _ in valid_terms]
    duplicate_terms = []
    for value in set(values):
        same_value_terms = [term for found, term in valid_terms if found == value]
        if len(same_value_terms) <= 1:
            continue
        same_value_terms.sort(
            key=lambda term: float(term.get("pin_number_confidence") or 0.0),
            reverse=True,
        )
        duplicate_terms.extend(
            term for term in same_value_terms[1:]
            if float(term.get("pin_number_confidence") or 0.0) < 0.85
        )

    bad_terms.extend(duplicate_terms)
    missing = sorted(set(range(1, max_pin + 1)) - set(values))
    if len(missing) != len(bad_terms):
        return

    assignments = {}
    remaining_missing = set(missing)
    remaining_terms = list(bad_terms)

    for term in list(remaining_terms):
        text = str(term.get("pin_number") or "")
        if not text or not re.match(r"^[0-9]+$", text):
            continue
        suffix_matches = [value for value in remaining_missing if str(value).endswith(text)]
        if len(suffix_matches) != 1:
            continue
        value = suffix_matches[0]
        assignments[id(term)] = value
        remaining_missing.remove(value)
        remaining_terms.remove(term)

    if len(remaining_terms) == 1 and len(remaining_missing) == 1:
        term = remaining_terms[0]
        assignments[id(term)] = next(iter(remaining_missing))
        remaining_terms.clear()
        remaining_missing.clear()

    if remaining_terms or remaining_missing:
        return

    for term in bad_terms:
        replacement = assignments.get(id(term))
        if replacement is None:
            continue
        previous = str(term.get("pin_number") or "")
        old_conf = float(term.get("pin_number_confidence") or 0.0)
        term["pin_number"] = str(replacement)
        term["pin_number_confidence"] = round(max(0.50, min(old_conf, 0.62)), 3)
        debug_payload = term.setdefault("pin_ocr_debug", {})
        debug_payload["unique_pin_number_repair"] = {
            "from": previous or None,
            "to": str(replacement),
            "reason": "complete_missing_numbers_in_1_to_terminal_count",
        }


def _repair_555_timer_pin_numbers(component: Dict) -> None:
    """Stabilizza la numerazione degli 8-pin 555 quando l'OCR scambia angoli."""
    marking = str(component.get("ic_marking") or "").upper()
    if not re.search(r"\b(?:LM|NE|SE)?555\b", marking):
        return

    terminals = component.get("terminals", []) or []
    if len(terminals) != 8:
        return

    by_side = {
        side: [
            term for term in sorted(terminals, key=_terminal_sort_key)
            if _terminal_side(term) == side
        ]
        for side in ("left", "right", "top", "bottom")
    }
    if (
        len(by_side["left"]) != 3
        or len(by_side["right"]) != 1
        or len(by_side["top"]) != 2
        or len(by_side["bottom"]) != 2
    ):
        return

    expected = {
        by_side["left"][0].get("terminal_id"): "7",
        by_side["left"][1].get("terminal_id"): "6",
        by_side["left"][2].get("terminal_id"): "2",
        by_side["right"][0].get("terminal_id"): "3",
        by_side["top"][0].get("terminal_id"): "8",
        by_side["top"][1].get("terminal_id"): "4",
        by_side["bottom"][0].get("terminal_id"): "1",
        by_side["bottom"][1].get("terminal_id"): "5",
    }

    for term in terminals:
        terminal_id = term.get("terminal_id")
        target = expected.get(terminal_id)
        if target is None:
            continue

        previous = str(term.get("pin_number") or "")
        if previous == target:
            continue

        old_conf = float(term.get("pin_number_confidence") or 0.0)
        term["pin_number"] = target
        term["pin_number_confidence"] = round(max(old_conf, 0.90), 3)
        debug_payload = term.setdefault("pin_ocr_debug", {})
        debug_payload["timer_555_pin_number_repair"] = {
            "from": previous or None,
            "to": target,
            "reason": "known_555_timer_8_pin_layout",
        }


def _repair_three_pin_corner_package_numbers(component: Dict) -> None:
    """
    Completa la numerazione di piccoli IC a 3 pin con layout top+right.

    E' un pattern geometrico generale: un pin sopra e due pin sul lato destro.
    Se l'OCR legge una sequenza coerente 1 -> 2 -> 3 ma ne perde l'ultimo
    elemento, completiamo il valore mancante.
    """
    terminals = component.get("terminals", []) or []
    if len(terminals) != 3:
        return

    by_name = {str(term.get("name") or ""): term for term in terminals}
    expected_order = ["top_1", "right_1", "right_2"]
    if any(name not in by_name for name in expected_order):
        return

    missing_terms = []
    for idx, name in enumerate(expected_order, start=1):
        term = by_name[name]
        text = str(term.get("pin_number") or "").strip()
        if not text:
            missing_terms.append((idx, term))
            continue
        if not re.fullmatch(r"[1-3]", text):
            return
        if int(text) != idx:
            return

    if not missing_terms:
        return

    for idx, term in missing_terms:
        previous = str(term.get("pin_number") or "")
        old_conf = float(term.get("pin_number_confidence") or 0.0)
        term["pin_number"] = str(idx)
        term["pin_number_confidence"] = round(max(old_conf, 0.60), 3)
        debug_payload = term.setdefault("pin_ocr_debug", {})
        debug_payload["three_pin_corner_package_repair"] = {
            "from": previous or None,
            "to": str(idx),
            "reason": "top_then_right_pair_sequence",
        }


def _valid_lane_numeric_words(debug_payload: Dict, cfg: Dict) -> List[Dict]:
    words = []
    for word in debug_payload.get("text_words") or []:
        if float(word.get("confidence") or 0.0) >= cfg["label_min_confidence"] and _is_number_text(word.get("text", ""), cfg):
            words.append(word)
    for word in debug_payload.get("number_words") or []:
        if float(word.get("confidence") or 0.0) >= cfg["number_min_confidence"] and _is_number_text(word.get("text", ""), cfg):
            words.append(word)
    return words


def _single_digit_fallback_hint(term: Dict, lane: Dict, cfg: Dict) -> bool:
    debug_payload = term.get("pin_ocr_debug") or {}
    numeric_words = _valid_lane_numeric_words(debug_payload, cfg)
    if len(numeric_words) >= 2:
        return True
    if any(len(str(word.get("text") or "")) >= 2 for word in numeric_words):
        return True

    best_number = debug_payload.get("best_number") or {}
    bbox = best_number.get("bbox") or term.get("pin_number_bbox")
    if not bbox:
        return False

    side = lane.get("side") or _terminal_side(term)
    width, height = _bbox_size(bbox)
    if side in {"left", "right"}:
        return width >= 18.0 and height >= 18.0
    return width >= 10.0 and height >= 18.0


def _single_digit_fallback_strong_hint(term: Dict, cfg: Dict) -> bool:
    debug_payload = term.get("pin_ocr_debug") or {}
    numeric_words = _valid_lane_numeric_words(debug_payload, cfg)
    if len(numeric_words) >= 2:
        return True
    if any(len(str(word.get("text") or "")) >= 2 for word in numeric_words):
        return True
    return False


def _lanes_needing_component_fallback(side_run: Dict, component_terminal_count: int, cfg: Dict) -> List[Dict]:
    lanes = []
    for lane in side_run["lanes"]:
        term = lane["term"]
        number = str(term.get("pin_number") or "")
        confidence = float(term.get("pin_number_confidence") or 0.0)
        if not number:
            lanes.append(lane)
        elif len(number) >= 2:
            if confidence <= 0.62:
                lanes.append(lane)
        elif confidence <= 0.40:
            lanes.append(lane)
        elif _single_digit_fallback_strong_hint(term, cfg):
            lanes.append(lane)
        elif component_terminal_count > 9 and confidence <= 0.68 and _single_digit_fallback_hint(term, lane, cfg):
            lanes.append(lane)
    return lanes


# =========================================================
# ESECUZIONE PER LATO E RICOMPOSIZIONE DEI RISULTATI
# =========================================================

def _copy_side_run_with_terms(side_run: Dict) -> Tuple[Dict, Dict[str, Dict]]:
    """
    Copia corsie e terminali prima di processare un lato in parallelo.
    """
    term_map: Dict[str, Dict] = {}
    lanes = []
    for lane in side_run["lanes"]:
        original_term = lane["term"]
        terminal_id = lane["terminal_id"]
        term_copy = dict(original_term)
        if original_term.get("pin_ocr_debug") is not None:
            term_copy["pin_ocr_debug"] = dict(original_term.get("pin_ocr_debug") or {})
        term_map[terminal_id] = term_copy
        lanes.append({
            **lane,
            "term": term_copy,
        })

    return {
        **side_run,
        "lanes": lanes,
    }, term_map


def _process_ic_pin_side(
    image_bgr,
    side_run: Dict,
    body_bbox,
    cfg: Dict,
    component_terminal_count: int,
    timing_on: bool,
    body_label_words: Optional[List[Dict]] = None,
) -> Optional[Dict]:
    """
    Pipeline OCR completa per un singolo lato:
    crop banda, OCR text/number, strip interna, assegnazione alle corsie e
    fallback numerico.
    """
    side = side_run["side"]
    side_start = time.perf_counter() if timing_on else None
    crop = _crop(image_bgr, side_run["band_bbox"])
    if crop is None:
        return None

    local_side_run, term_map = _copy_side_run_with_terms(side_run)

    side_ocr_start = time.perf_counter() if timing_on else None
    prepared, scale = _prepare_side_band(crop, cfg)
    text_words, text_info = _run_tesseract_words(prepared, local_side_run["band_bbox"], scale, cfg, mode="text")
    inner_label_words, inner_label_info = _run_inner_label_strip_words(
        image_bgr,
        local_side_run,
        body_bbox,
        cfg,
    )
    if inner_label_words:
        text_words = _dedupe_words(text_words + inner_label_words)
    if body_label_words:
        side_body_words = [
            word for word in body_label_words
            if _bbox_overlap_ratio(word["bbox"], local_side_run["band_bbox"]) > 0.0
        ]
        if side_body_words:
            text_words = _dedupe_words(text_words + side_body_words)
    number_words, number_info = _run_tesseract_words(prepared, local_side_run["band_bbox"], scale, cfg, mode="number")
    label_guard_words = [
        word for word in text_words
        if _is_label_guard_candidate(word, cfg)
    ]
    _assign_lane_semantics(
        local_side_run,
        text_words,
        number_words,
        body_bbox,
        cfg,
        side_label_guard_words=label_guard_words,
    )
    side_ocr_ms = _elapsed_ms(side_ocr_start) if side_ocr_start is not None else 0.0

    component_words = []
    component_fallback_ms = 0.0
    if cfg["component_fallback_enabled"] and cfg["number_enabled"]:
        fallback_start = time.perf_counter() if timing_on else None
        fallback_lanes = _lanes_needing_component_fallback(
            local_side_run,
            component_terminal_count=component_terminal_count,
            cfg=cfg,
        )
        if fallback_lanes:
            component_words = _component_number_words(image_bgr, local_side_run, cfg, target_lanes=fallback_lanes)
            _assign_component_number_fallback(
                image_bgr,
                local_side_run,
                component_words,
                body_bbox,
                cfg,
                label_guard_words=label_guard_words,
            )
        component_fallback_ms = _elapsed_ms(fallback_start) if fallback_start is not None else 0.0

    side_debug = {
        "side": side,
        "band_bbox": local_side_run["band_bbox"],
        "lane_count": len(local_side_run["lanes"]),
        "ocr_text": text_info,
        "ocr_number": number_info,
        "lanes": [
            {
                "terminal_id": lane["terminal_id"],
                "lane_bbox": lane["lane_bbox"],
                "axis_range": lane["axis_range"],
            }
            for lane in local_side_run["lanes"]
        ] if cfg["store_debug"] else [],
        "text_words": text_words if cfg["store_debug"] else [],
        "inner_label_ocr": inner_label_info,
        "number_words": number_words if cfg["store_debug"] else [],
        "component_words": component_words if cfg["store_debug"] else [],
    }

    return {
        "side": side,
        "terms": term_map,
        "side_debug": side_debug,
        "timing": {
            "lane_count": len(local_side_run["lanes"]),
            "ocr_ms": side_ocr_ms,
            "component_fallback_ms": component_fallback_ms,
            "total_ms": _elapsed_ms(side_start) if side_start is not None else 0.0,
        },
    }


def _apply_side_term_updates(component: Dict, term_updates: Dict[str, Dict]) -> None:
    """
    Riporta nel componente principale i risultati calcolati sui terminali copia.
    """
    for term in component.get("terminals", []) or []:
        updated = term_updates.get(term.get("terminal_id"))
        if updated is None:
            continue
        term["pin_number"] = updated.get("pin_number")
        term["pin_label_text"] = updated.get("pin_label_text")
        term["pin_number_confidence"] = updated.get("pin_number_confidence")
        term["pin_label_confidence"] = updated.get("pin_label_confidence")
        if updated.get("pin_number_bbox") is not None:
            term["pin_number_bbox"] = updated.get("pin_number_bbox")
        else:
            term.pop("pin_number_bbox", None)
        if updated.get("pin_label_bbox") is not None:
            term["pin_label_bbox"] = updated.get("pin_label_bbox")
        else:
            term.pop("pin_label_bbox", None)
        if updated.get("pin_ocr_debug") is not None:
            term["pin_ocr_debug"] = updated.get("pin_ocr_debug")
        else:
            term.pop("pin_ocr_debug", None)


def _score_label_for_lane(word: Dict, lane: Dict, side: str, body_bbox: List[float], cfg: Dict) -> Optional[Tuple[int, float, float, float, int]]:
    chosen = _pick_best_label_word(
        [word],
        lane=lane,
        side=side,
        body_bbox=body_bbox,
        max_distance_px=_label_pick_distance(side, cfg),
    )
    if chosen is None:
        return None
    return (
        int(chosen.get("label_priority") or 0),
        float(chosen.get("axis_distance") or 999.0),
        float(chosen.get("edge_distance") or 999.0),
        -float(chosen.get("confidence") or 0.0),
        -len(str(chosen.get("text") or "")),
    )


def _reassign_cross_side_labels(component: Dict, side_runs: Dict[str, Dict], body_bbox: List[float], cfg: Dict) -> None:
    """
    Sposta una label su una corsia migliore se il bbox OCR cade chiaramente
    nella corsia di un terminale vicino.
    """
    lane_by_terminal: Dict[str, Dict] = {}
    for side_run in side_runs.values():
        for lane in side_run.get("lanes", []) or []:
            lane_by_terminal[str(lane.get("terminal_id"))] = lane

    for term in component.get("terminals", []) or []:
        label = str(term.get("pin_label_text") or "").strip()
        if not label:
            continue

        terminal_id = str(term.get("terminal_id") or "")
        current_lane = lane_by_terminal.get(terminal_id)
        if current_lane is None:
            continue

        bbox = term.get("pin_label_bbox")
        if not bbox:
            continue
        word = {
            "text": label,
            "confidence": float(term.get("pin_label_confidence") or 0.0),
            "bbox": bbox,
            "center": [(float(bbox[0]) + float(bbox[2])) * 0.5, (float(bbox[1]) + float(bbox[3])) * 0.5],
            "mode": ((term.get("pin_ocr_debug") or {}).get("best_label") or {}).get("mode", "text"),
        }

        current_side = _terminal_side(term) or ""
        current_score = _score_label_for_lane(word, current_lane, current_side, body_bbox, cfg)
        if current_score is None:
            continue

        best_lane = current_lane
        best_score = current_score
        for other_side, side_run in side_runs.items():
            for lane in side_run.get("lanes", []) or []:
                if lane["terminal_id"] == terminal_id:
                    continue
                if not _bbox_contains_point(lane["lane_bbox"], word["center"][0], word["center"][1]):
                    continue
                score = _score_label_for_lane(word, lane, other_side, body_bbox, cfg)
                if score is None:
                    continue
                if score[:2] < best_score[:2]:
                    best_lane = lane
                    best_score = score

        if best_lane["terminal_id"] == terminal_id:
            continue

        target = best_lane["term"]
        target_label = str(target.get("pin_label_text") or "").strip()
        target_conf = float(target.get("pin_label_confidence") or 0.0)
        if target_label and target_conf >= float(term.get("pin_label_confidence") or 0.0):
            continue

        target["pin_label_text"] = term.get("pin_label_text")
        target["pin_label_confidence"] = term.get("pin_label_confidence")
        if term.get("pin_label_bbox") is not None:
            target["pin_label_bbox"] = term.get("pin_label_bbox")
        target_debug = target.setdefault("pin_ocr_debug", {})
        best_label = ((term.get("pin_ocr_debug") or {}).get("best_label") or {})
        if best_label:
            target_debug["best_label"] = dict(best_label)

        term["pin_label_text"] = None
        term["pin_label_confidence"] = None
        term.pop("pin_label_bbox", None)


def _split_sequential_pin_label(label: str) -> Optional[Tuple[str, int]]:
    upper = str(label or "").strip().upper()
    if not upper:
        return None
    dot_match = re.fullmatch(r"([A-Z]+[0-9]+\.)\s*([0-9]{1,2})", upper)
    if dot_match:
        return dot_match.group(1), int(dot_match.group(2))
    plain_match = re.fullmatch(r"([A-Z]+)\s*([0-9]{1,2})", upper)
    if plain_match:
        return plain_match.group(1), int(plain_match.group(2))
    return None


# =========================================================
# RIPARAZIONI POST-OCR E FILTRI DI DOMINIO
# =========================================================

def _format_sequential_pin_label(prefix: str, index_value: int) -> str:
    return f"{prefix}{index_value}"


def _repair_sequential_pin_labels(component: Dict) -> None:
    """
    Completa sequenze di label tipo D0, D1, D2 quando esiste sufficiente
    supporto locale sullo stesso lato.
    """
    for side in ("left", "right", "top", "bottom"):
        side_terms = [
            term for term in sorted(component.get("terminals", []) or [], key=_terminal_sort_key)
            if _terminal_side(term) == side
        ]
        if len(side_terms) < 3:
            continue

        groups: Dict[str, List[Tuple[int, Dict, int]]] = {}
        for pos, term in enumerate(side_terms, start=1):
            parsed = _split_sequential_pin_label(term.get("pin_label_text") or "")
            if parsed is None:
                continue
            prefix, index_value = parsed
            groups.setdefault(prefix, []).append((pos, term, index_value))

        for prefix, entries in groups.items():
            if len(entries) < 2:
                continue

            ascending_offsets: Dict[int, int] = {}
            descending_offsets: Dict[int, int] = {}
            for pos, _, index_value in entries:
                ascending_offsets[index_value - pos] = ascending_offsets.get(index_value - pos, 0) + 1
                descending_offsets[index_value + pos] = descending_offsets.get(index_value + pos, 0) + 1

            best_asc = max(ascending_offsets.items(), key=lambda item: item[1])
            best_desc = max(descending_offsets.items(), key=lambda item: item[1])
            direction = 1
            parameter = best_asc[0]
            support = best_asc[1]
            if best_desc[1] > support:
                direction = -1
                parameter = best_desc[0]
                support = best_desc[1]
            if support < 2:
                continue

            positions = [pos for pos, _, _ in entries]
            min_pos = min(positions)
            max_pos = max(positions)
            start_pos = min_pos
            end_pos = max_pos
            if direction == 1:
                start_pos = max(1, -parameter)
            for pos in range(start_pos, end_pos + 1):
                term = side_terms[pos - 1]
                expected_index = (pos + parameter) if direction == 1 else (parameter - pos)
                if expected_index < 0 or expected_index > 99:
                    continue
                desired = _format_sequential_pin_label(prefix, expected_index)
                current = str(term.get("pin_label_text") or "").strip().upper()
                current_conf = float(term.get("pin_label_confidence") or 0.0)
                if current == desired:
                    continue

                current_parsed = _split_sequential_pin_label(current)
                current_prefix = current_parsed[0] if current_parsed is not None else ""
                if current and current_prefix not in {"", prefix} and current_conf >= 0.75:
                    continue
                if current and current_prefix == prefix and current_conf >= 0.75:
                    continue
                term["pin_label_text"] = desired


def _remove_duplicate_sequential_labels(component: Dict) -> None:
    """
    Rimuove duplicati in sequenze come P1.0/P1.1 quando la stessa label finisce
    su piu' terminali.
    """
    side_prefix_support: Dict[Tuple[str, str], int] = {}
    for side in ("left", "right", "top", "bottom"):
        for term in component.get("terminals", []) or []:
            if _terminal_side(term) != side:
                continue
            parsed = _split_sequential_pin_label(term.get("pin_label_text") or "")
            if parsed is None:
                continue
            prefix, _ = parsed
            key = (side, prefix)
            side_prefix_support[key] = side_prefix_support.get(key, 0) + 1

    by_label: Dict[str, List[Dict]] = {}
    for term in component.get("terminals", []) or []:
        label = str(term.get("pin_label_text") or "").strip().upper()
        if not label or _split_sequential_pin_label(label) is None:
            continue
        by_label.setdefault(label, []).append(term)

    for label, terms in by_label.items():
        if len(terms) <= 1:
            continue

        def _term_score(term: Dict) -> Tuple[int, float]:
            side = _terminal_side(term) or ""
            parsed = _split_sequential_pin_label(term.get("pin_label_text") or "")
            prefix = parsed[0] if parsed is not None else ""
            support = side_prefix_support.get((side, prefix), 0)
            confidence = float(term.get("pin_label_confidence") or 0.0)
            return support, confidence

        keep = max(terms, key=_term_score)
        for term in terms:
            if term is keep:
                continue
            term["pin_label_text"] = None
            term["pin_label_confidence"] = None
            term.pop("pin_label_bbox", None)


def _has_ic_marking(component: Dict) -> bool:
    return bool(str(component.get("ic_marking") or "").strip())


def _clear_pin_labels_when_number_and_marking(component: Dict) -> int:
    """
    Policy datasheet-first: se l'IC ha marking e il terminale ha pin_number,
    rimuove pin_label_text per evitare una lettura OCR non necessaria.
    """
    if not _has_ic_marking(component):
        return 0

    cleared = 0
    for term in component.get("terminals", []) or []:
        if term.get("pin_number") in (None, ""):
            continue
        if term.get("pin_label_text") in (None, ""):
            continue

        term["pin_label_text"] = None
        term["pin_label_confidence"] = None
        term.pop("pin_label_bbox", None)
        debug_payload = term.get("pin_ocr_debug")
        if isinstance(debug_payload, dict):
            debug_payload["label_cleared_reason"] = "ic_marking_and_pin_number_present"
            debug_payload.pop("best_label", None)
        cleared += 1

    return cleared


def _is_seven_segment_label(label: str) -> bool:
    upper = str(label or "").strip().upper()
    return bool(re.fullmatch(r"[A-H]", upper) or upper == "COM")


def _rename_terminal_for_side(component: Dict, term: Dict, side: str, index: int) -> None:
    instance_id = str(component.get("instance_id") or term.get("instance_id") or "")
    name = f"{side}_{index}"
    term["name"] = name
    term["display_name"] = name
    term["relative_position"] = side
    if instance_id:
        term["terminal_id"] = f"{instance_id}:{name}"
        term["display_terminal_id"] = f"{instance_id}:{name}"


def _make_ic_terminal_point(body_bbox: List[float], side: str, coord: float) -> Tuple[float, float]:
    bx1, by1, bx2, by2 = [float(v) for v in body_bbox]
    if side == "left":
        return round(bx1 - TERMINAL_OUTWARD_OFFSET, 2), round(float(coord), 2)
    if side == "right":
        return round(bx2 + TERMINAL_OUTWARD_OFFSET, 2), round(float(coord), 2)
    if side == "top":
        return round(float(coord), 2), round(by1 - TERMINAL_OUTWARD_OFFSET, 2)
    return round(float(coord), 2), round(by2 + TERMINAL_OUTWARD_OFFSET, 2)


def _ic_anchor_offset_ratio(body_bbox: List[float], side: str, coord: float) -> float:
    bx1, by1, bx2, by2 = [float(v) for v in body_bbox]
    if side in {"left", "right"}:
        return round((float(coord) - by1) / max(by2 - by1, 1.0), 4)
    return round((float(coord) - bx1) / max(bx2 - bx1, 1.0), 4)


def _side_axis_from_word(word: Dict, side: str) -> float:
    center = word.get("center")
    if center is None:
        bbox = word.get("bbox") or [0, 0, 0, 0]
        center = [(float(bbox[0]) + float(bbox[2])) * 0.5, (float(bbox[1]) + float(bbox[3])) * 0.5]
    return float(center[1] if side in {"left", "right"} else center[0])


def _cluster_side_candidate_words(words: List[Dict], side: str, gap_px: float) -> List[Dict]:
    if not words:
        return []

    words = sorted(words, key=lambda item: _side_axis_from_word(item, side))
    clusters: List[List[Dict]] = [[words[0]]]
    for word in words[1:]:
        current = clusters[-1]
        last_axis = _side_axis_from_word(current[-1], side)
        axis = _side_axis_from_word(word, side)
        if abs(axis - last_axis) <= float(gap_px):
            current.append(word)
        else:
            clusters.append([word])

    merged = []
    for cluster in clusters:
        weights = [max(0.35, float(word.get("confidence") or 0.0)) for word in cluster]
        coords = [_side_axis_from_word(word, side) for word in cluster]
        weighted_coord = sum(coord * weight for coord, weight in zip(coords, weights)) / max(sum(weights), 1e-6)
        best = max(cluster, key=lambda item: (float(item.get("confidence") or 0.0), -_word_edge_distance(item, side, [0, 0, 0, 0]) if False else 0.0))
        merged.append({
            "coord": round(float(weighted_coord), 2),
            "words": cluster,
            "best_word": best,
            "confidence": round(max(float(word.get("confidence") or 0.0) for word in cluster), 3),
        })
    return merged


def _median_spacing(values: List[float]) -> Optional[float]:
    if len(values) < 2:
        return None
    diffs = [
        float(values[idx + 1]) - float(values[idx])
        for idx in range(len(values) - 1)
        if float(values[idx + 1]) - float(values[idx]) > 0.0
    ]
    if not diffs:
        return None
    return float(np.median(np.asarray(diffs, dtype=np.float32)))


def _small_ic_terminal_recovery_enabled(body_bbox: List[float], cfg: Dict) -> bool:
    bx1, by1, bx2, by2 = [float(v) for v in body_bbox]
    min_dim = min(max(1.0, bx2 - bx1 + 1.0), max(1.0, by2 - by1 + 1.0))
    return min_dim <= float(cfg.get("adaptive_upscale_min_body_dim_px", 140)) + 35.0


def _append_recovered_terminal(component: Dict, side: str, coord: float, body_bbox: List[float], source_cluster: Dict) -> None:
    instance_id = str(component.get("instance_id") or "")
    point = _make_ic_terminal_point(body_bbox, side, coord)
    anchor_ratio = _ic_anchor_offset_ratio(body_bbox, side, coord)
    term = {
        "terminal_id": f"{instance_id}:{side}_tmp",
        "instance_id": instance_id,
        "component_class_id": component.get("class_id"),
        "component_class_name": component.get("class_name"),
        "name": f"{side}_tmp",
        "display_name": f"{side}_tmp",
        "display_terminal_id": f"{instance_id}:{side}_tmp",
        "relative_position": side,
        "estimated_orientation": component.get("estimated_orientation"),
        "estimated_connection_side": None,
        "terminal_point_mode": "bbox_side_anchor_ratio",
        "terminal_point_debug": {
            "point_mode": "ocr_assisted_small_ic_terminal_recovery",
            "body_bbox": [round(float(v), 2) for v in body_bbox],
            "side": side,
            "coord": round(float(coord), 2),
            "anchor_offset_ratio": anchor_ratio,
            "recovery_source_word": {
                "text": source_cluster.get("best_word", {}).get("text"),
                "confidence": source_cluster.get("confidence"),
                "bbox": source_cluster.get("best_word", {}).get("bbox"),
            },
        },
        "x": point[0],
        "y": point[1],
        "pin_number": None,
        "pin_label_text": None,
        "pin_number_confidence": None,
        "pin_label_confidence": None,
    }
    component.setdefault("terminals", []).append(term)


def _recover_missing_small_ic_terminals_from_component_words(
    component: Dict,
    image_bgr,
    body_bbox: List[float],
    side_runs: Dict[str, Dict],
    cfg: Dict,
) -> List[Dict]:
    """
    Recupera terminali mancanti su IC piccoli usando component OCR words vicine al bordo.

    La regola resta prudente:
    - si attiva solo su package piccoli;
    - usa solo numeri OCR vicini al lato corretto;
    - aggiunge terminali solo quando le posizioni OCR mostrano un candidato
      coerente ma non coperto dalle corsie geometriche esistenti.
    """
    if component.get("component_subtype") == "seven_segment_display":
        return []

    if not _small_ic_terminal_recovery_enabled(body_bbox, cfg):
        return []

    recoveries: List[Dict] = []
    for side, side_run in side_runs.items():
        lanes = side_run.get("lanes") or []
        if len(lanes) < 2:
            continue

        component_words = _component_number_words(image_bgr, side_run, cfg)
        numeric_words = []
        for word in component_words:
            text = str(word.get("text") or "").strip()
            confidence = float(word.get("confidence") or 0.0)
            if confidence < 0.60 or not _is_number_text(text, cfg):
                continue
            if _closest_body_side(word, body_bbox) != side:
                continue
            max_edge_distance = 18.0 if side in {"left", "right"} else 16.0
            if _word_edge_distance(word, side, body_bbox) > max_edge_distance:
                continue
            numeric_words.append(word)

        if len(numeric_words) <= len(lanes):
            continue

        cluster_gap = 8.0 if side in {"left", "right"} else 10.0
        clusters = _cluster_side_candidate_words(numeric_words, side, gap_px=cluster_gap)
        if len(clusters) <= len(lanes):
            continue

        lane_coords = sorted(
            float(lane["term"]["y"] if side in {"left", "right"} else lane["term"]["x"])
            for lane in lanes
        )
        cluster_coords = sorted(float(cluster["coord"]) for cluster in clusters)
        lane_spacing = _median_spacing(lane_coords)
        cluster_spacing = _median_spacing(cluster_coords)
        base_spacing = cluster_spacing or lane_spacing or 18.0
        match_tol = max(12.0, min(base_spacing * 0.72, 20.0))

        unmatched = []
        for cluster in clusters:
            coord = float(cluster["coord"])
            if any(abs(coord - lane_coord) <= match_tol for lane_coord in lane_coords):
                continue
            unmatched.append(cluster)

        if len(unmatched) == 0 or len(unmatched) > 2:
            continue

        existing_count = len(lane_coords)
        recovered_here = []
        for cluster in sorted(unmatched, key=lambda item: float(item["coord"])):
            coord = float(cluster["coord"])
            nearest = min(abs(coord - lane_coord) for lane_coord in lane_coords)
            before_first = coord < lane_coords[0] - max(match_tol, base_spacing * 0.85)
            after_last = coord > lane_coords[-1] + max(match_tol, base_spacing * 0.85)
            inside_large_gap = False
            for left_coord, right_coord in zip(lane_coords[:-1], lane_coords[1:]):
                if left_coord < coord < right_coord and (right_coord - left_coord) >= max(base_spacing * 1.75, 28.0):
                    inside_large_gap = True
                    break
            if nearest < match_tol and not before_first and not after_last and not inside_large_gap:
                continue

            _append_recovered_terminal(component, side, coord, body_bbox, cluster)
            lane_coords.append(coord)
            lane_coords.sort()
            recovered_here.append({
                "side": side,
                "coord": round(coord, 2),
                "source_word": cluster.get("best_word", {}).get("text"),
                "confidence": cluster.get("confidence"),
            })

            if len(component.get("terminals", []) or []) > existing_count + 2 + sum(len((sr.get("lanes") or [])) for sr in side_runs.values()):
                break

        if recovered_here:
            recoveries.extend(recovered_here)

    if not recoveries:
        return []

    for side in ("left", "right", "top", "bottom"):
        side_terms = [
            term for term in sorted(component.get("terminals", []) or [], key=_terminal_sort_key)
            if _terminal_side(term) == side
        ]
        for idx, term in enumerate(side_terms, start=1):
            _rename_terminal_for_side(component, term, side, idx)

    return recoveries


def _normalize_seven_segment_h_terminal(
    component: Dict,
    label_side: str,
    label_terms: List[Dict],
    cap_terms: List[Dict],
) -> None:
    if len(label_terms) != 7 or len(cap_terms) < 2:
        return

    label_values = {
        str(term.get("pin_label_text") or "").strip().lower()
        for term in label_terms
    }
    if not all(label in label_values for label in ("a", "b", "c", "d", "e", "f", "g")):
        return

    h_terms = [
        term for term in cap_terms
        if str(term.get("pin_label_text") or "").strip().lower() in {"h", "dp"}
    ]
    com_terms = [
        term for term in cap_terms
        if str(term.get("pin_label_text") or "").strip().lower() == "com"
    ]
    if not h_terms or not com_terms:
        return

    target = max(h_terms, key=lambda term: float(term.get("pin_label_confidence") or 0.0))
    _rename_terminal_for_side(component, target, label_side, len(label_terms) + 1)
    target_debug = target.setdefault("pin_ocr_debug", {})
    target_debug["seven_segment_side_repair"] = {
        "reason": "h_or_dp_read_on_common_side",
        "target_side": label_side,
    }


def _normalize_seven_segment_common_pin_number(cap_terms: List[Dict]) -> None:
    """
    Normalizza il pin comune dei display 7 segmenti.

    Nei datasheet dei display il common e' spesso indicato come doppio pin 3,8.
    L'OCR tende a fondere quel testo in "38": qui lo riportiamo al formato
    esplicito "3.8" per preservare il significato del doppio pin.
    """
    for term in cap_terms:
        text = re.sub(r"\s+", "", str(term.get("pin_number") or ""))
        if text != "38":
            continue
        term["pin_number"] = "3.8"
        debug_payload = term.setdefault("pin_ocr_debug", {})
        debug_payload["seven_segment_common_pin_number_normalization"] = {
            "from": "38",
            "to": "3.8",
            "reason": "common_pin_pair_collapsed_by_ocr",
        }


def _clear_terminal_pin_number(term: Dict) -> None:
    term["pin_number"] = None
    term["pin_number_confidence"] = None
    term.pop("pin_number_bbox", None)


def _normalize_seven_segment_top_common_labels(
    component: Dict,
    label_side: str,
    cap_side: str,
) -> None:
    """
    Normalizza i display 7 segmenti del tipo 7 pin laterali + 1 pin sopra.

    In questi simboli i terminali laterali rappresentano i segmenti a-g e il
    terminale superiore e' il common senza label/pin number esportato.
    """
    if cap_side != "top":
        return

    by_side = {
        side: [
            term for term in sorted(component.get("terminals", []) or [], key=_terminal_sort_key)
            if _terminal_side(term) == side
        ]
        for side in ("left", "right", "top", "bottom")
    }
    label_terms = by_side.get(label_side) or []
    cap_terms = by_side.get(cap_side) or []
    if len(label_terms) != 7 or len(cap_terms) != 1:
        return

    expected_labels = ["a", "b", "c", "d", "e", "f", "g"]
    for term, label in zip(label_terms, expected_labels):
        _clear_terminal_pin_number(term)
        term["pin_label_text"] = label
        old_conf = float(term.get("pin_label_confidence") or 0.0)
        term["pin_label_confidence"] = round(max(old_conf, 0.60), 3)
        debug_payload = term.setdefault("pin_ocr_debug", {})
        debug_payload["seven_segment_top_common_label_normalization"] = {
            "label": label,
            "reason": "seven_lateral_segments_plus_top_common",
        }

    cap_term = cap_terms[0]
    _clear_terminal_pin_number(cap_term)
    cap_term["pin_label_text"] = None
    cap_term["pin_label_confidence"] = None
    cap_term.pop("pin_label_bbox", None)
    debug_payload = cap_term.setdefault("pin_ocr_debug", {})
    debug_payload["seven_segment_top_common_label_normalization"] = {
        "label": None,
        "reason": "top_common_terminal_without_exported_label",
    }


def _renumber_side_terms(component: Dict, side: str, terms: List[Dict]) -> None:
    for idx, term in enumerate(sorted(terms, key=_terminal_sort_key), start=1):
        _rename_terminal_for_side(component, term, side, idx)


def _prune_seven_segment_display_terminals(component: Dict) -> int:
    """
    Filtro di dominio per display 7 segmenti.

    Il display passa nello stesso OCR pin degli altri IC. Dopo la lettura,
    teniamo al massimo 9 terminali: a-h + com. Il lato verticale viene scelto
    in base alle label OCR lette, non in base a coordinate o ID immagine.
    """
    if (
        component.get("component_subtype") != "seven_segment_display"
        and component.get("display_type") != "seven_segment"
    ):
        return 0

    terminals = component.get("terminals") or []
    if not terminals:
        return 0

    by_side = {
        side: [
            term for term in sorted(terminals, key=_terminal_sort_key)
            if _terminal_side(term) == side
        ]
        for side in ("left", "right", "top", "bottom")
    }

    def _label_support(side_terms: List[Dict]) -> Tuple[int, int]:
        labels = {
            str(term.get("pin_label_text") or "").strip().lower()
            for term in side_terms
            if _is_seven_segment_label(term.get("pin_label_text") or "")
        }
        segment_labels = {label for label in labels if re.fullmatch(r"[a-h]", label)}
        return len(segment_labels), len(labels)

    side_stats = {}
    for side in ("left", "right"):
        side_terms = by_side[side]
        segment_count, label_count = _label_support(side_terms)
        side_stats[side] = {
            "segment_count": segment_count,
            "label_count": label_count,
            "term_count": len(side_terms),
        }

    left_stats = side_stats["left"]
    right_stats = side_stats["right"]
    weak_equal_evidence = (
        left_stats["term_count"] == right_stats["term_count"] >= 7
        and max(left_stats["segment_count"], right_stats["segment_count"]) <= 1
        and max(left_stats["label_count"], right_stats["label_count"]) <= 1
    )
    if (
        (
            left_stats["segment_count"] == right_stats["segment_count"] == 0
            and left_stats["label_count"] == right_stats["label_count"] == 0
            and left_stats["term_count"] == right_stats["term_count"] >= 7
        )
        or weak_equal_evidence
    ):
        label_side = "left"
        vertical_count = left_stats["term_count"]
    else:
        candidates = []
        for side in ("left", "right"):
            stats = side_stats[side]
            candidates.append((
                stats["segment_count"],
                stats["label_count"],
                stats["term_count"],
                1 if side == "left" else 0,
                side,
            ))
        candidates.sort(reverse=True)
        _, _, vertical_count, _, label_side = candidates[0]
    if vertical_count < 7:
        return 0

    cap_terms = by_side["bottom"] if by_side["bottom"] else by_side["top"]
    if not cap_terms:
        return 0
    _normalize_seven_segment_common_pin_number(cap_terms)

    _normalize_seven_segment_h_terminal(component, label_side, by_side[label_side], cap_terms)
    by_side = {
        side: [
            term for term in sorted(terminals, key=_terminal_sort_key)
            if _terminal_side(term) == side
        ]
        for side in ("left", "right", "top", "bottom")
    }
    label_terms = by_side[label_side]
    cap_side = "bottom" if by_side["bottom"] else "top"
    cap_terms = by_side[cap_side]
    vertical_count = len(label_terms)

    label_terms = by_side[label_side]
    if vertical_count >= 8:
        keep_terms = label_terms[:8] + cap_terms[:1]
    elif vertical_count == 7 and len(cap_terms) >= 2:
        keep_terms = label_terms[:7] + cap_terms[:2]
    elif vertical_count == 7 and len(cap_terms) == 1:
        keep_terms = label_terms[:7] + cap_terms[:1]
    else:
        return 0

    if len(keep_terms) > 9:
        keep_terms = keep_terms[:9]

    keep_ids = {id(term) for term in keep_terms}
    removed_terms = [
        term for term in terminals
        if id(term) not in keep_ids
    ]
    removed = len(terminals) - len(keep_terms)
    if removed <= 0:
        _renumber_side_terms(component, label_side, by_side[label_side])
        _renumber_side_terms(component, cap_side, by_side[cap_side])
        _normalize_seven_segment_common_pin_number(by_side[cap_side])
        _normalize_seven_segment_top_common_labels(component, label_side, cap_side)
        return 0

    kept_labels = {
        str(term.get("pin_label_text") or "").strip().lower()
        for term in keep_terms
        if term.get("pin_label_text")
    }
    if "com" not in kept_labels:
        removed_com = [
            term for term in removed_terms
            if str(term.get("pin_label_text") or "").strip().lower() == "com"
        ]
        cap_unlabeled = [
            term for term in keep_terms
            if _terminal_side(term) in {"top", "bottom"}
            and not term.get("pin_label_text")
        ]
        if removed_com and cap_unlabeled:
            source = max(
                removed_com,
                key=lambda term: float(term.get("pin_label_confidence") or 0.0),
            )
            target = cap_unlabeled[-1]
            target["pin_label_text"] = "com"
            target["pin_label_confidence"] = source.get("pin_label_confidence")
            if source.get("pin_label_bbox") is not None:
                target["pin_label_bbox"] = source.get("pin_label_bbox")
            target_debug = target.setdefault("pin_ocr_debug", {})
            target_debug["seven_segment_label_transfer"] = {
                "from_terminal_id": source.get("terminal_id"),
                "label": "com",
                "reason": "com_label_read_on_pruned_side",
            }

    component["terminals"] = [
        term for term in terminals
        if id(term) in keep_ids
    ]
    _renumber_side_terms(component, label_side, [
        term for term in component["terminals"] if _terminal_side(term) == label_side
    ])
    _renumber_side_terms(component, cap_side, [
        term for term in component["terminals"] if _terminal_side(term) == cap_side
    ])
    _normalize_seven_segment_common_pin_number([
        term for term in component["terminals"] if _terminal_side(term) == cap_side
    ])
    _normalize_seven_segment_top_common_labels(component, label_side, cap_side)
    debug = component.setdefault("seven_segment_terminal_filter_debug", {})
    debug.update({
        "removed_count": removed,
        "kept_count": len(component["terminals"]),
        "label_side": label_side,
        "side_counts": {side: len(terms) for side, terms in by_side.items()},
        "reason": "keep_best_label_side_plus_common_side",
    })
    return removed


def normalize_seven_segment_display_terminals(component: Dict) -> int:
    """
    Normalizza i terminali dei display a 7 segmenti gia' arricchiti dall'OCR.

    E' un wrapper pubblico usato anche dallo step 03 prima dell'export: non
    aggiunge dati nuovi, rende solo coerenti lato/nome dei terminali letti.
    """
    return _prune_seven_segment_display_terminals(component)


# =========================================================
# ENTRY POINT PUBBLICO
# =========================================================

def enrich_ic_pin_ocr(component: Dict, image_bgr, meta: Dict) -> Dict:
    """
    Arricchisce un Integrated_Circuit con OCR dei pin.

    Non crea terminali: aggiorna pin_number, pin_label_text, confidence e debug
    sui terminali geometrici gia' stimati.
    """
    cfg = _get_pin_ocr_cfg(meta)
    cfg["component_subtype"] = component.get("component_subtype")
    cfg["marking_bbox"] = _get_marking_bbox(component)
    cfg["marking_reject_overlap_ratio"] = float(
        ((meta.get("ocr") or {}).get("pin_labels") or {}).get(
            "marking_reject_overlap_ratio",
            0.20,
        )
    )
    _reset_pin_fields(component)
    timing_on = _timing_enabled()
    total_start = time.perf_counter() if timing_on else None

    debug = {
        "enabled": bool(cfg["ocr_enabled"] and cfg["enabled"]),
        "strategy": cfg["strategy"],
        "engine": "tesseract",
        "skipped": False,
        "reasons": [],
        "side_runs": [],
        "assigned_count": 0,
    }
    if timing_on:
        debug["timing_ms"] = {
            "side_ocr_ms": 0.0,
            "component_fallback_ms": 0.0,
            "sides": {},
        }

    if not cfg["ocr_enabled"] or not cfg["enabled"]:
        debug["skipped"] = True
        debug["reasons"].append("ocr_or_pin_labels_disabled")
        component["ic_pin_ocr_debug"] = debug
        return component

    if component.get("component_subtype") in cfg["skip_component_subtypes"]:
        debug["skipped"] = True
        debug["reasons"].append(f"skipped_subtype:{component.get('component_subtype')}")
        component["ic_pin_ocr_debug"] = debug
        return component

    body_bbox = get_ic_body_bbox_from_component(component, image_bgr.shape)
    if not body_bbox:
        debug["skipped"] = True
        debug["reasons"].append("missing_body_bbox")
        component["ic_pin_ocr_debug"] = debug
        return component

    component["body_bbox"] = body_bbox
    cfg["body_bbox"] = body_bbox
    side_runs = _build_side_lanes(component, body_bbox, image_bgr.shape, cfg)
    if not side_runs:
        debug["skipped"] = True
        debug["reasons"].append("no_side_lanes")
        component["ic_pin_ocr_debug"] = debug
        return component

    recovered_terminals = _recover_missing_small_ic_terminals_from_component_words(
        component,
        image_bgr,
        body_bbox,
        side_runs,
        cfg,
    )
    if recovered_terminals:
        side_runs = _build_side_lanes(component, body_bbox, image_bgr.shape, cfg)
        debug["ocr_assisted_recovered_terminals"] = recovered_terminals

    if _has_ic_marking(component):
        body_label_words = []
        body_label_info = {
            "ok": True,
            "skipped": "ic_marking_present_datasheet_preferred",
        }
    else:
        body_label_words, body_label_info = _run_easyocr_body_label_words(image_bgr, body_bbox, cfg)
    debug["body_label_ocr"] = body_label_info
    if cfg["store_debug"]:
        debug["body_label_words"] = body_label_words

    ordered_sides = [side for side in ("left", "right", "top", "bottom") if side_runs.get(side) is not None]
    side_results: Dict[str, Dict] = {}
    max_workers = min(4, len(ordered_sides))
    if max_workers <= 1:
        for side in ordered_sides:
            result = _process_ic_pin_side(
                image_bgr,
                side_runs[side],
                body_bbox,
                cfg,
                component_terminal_count=len(component.get("terminals", []) or []),
                timing_on=timing_on,
                body_label_words=body_label_words,
            )
            if result is not None:
                side_results[side] = result
    else:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                side: executor.submit(
                    _process_ic_pin_side,
                    image_bgr,
                    side_runs[side],
                    body_bbox,
                    cfg,
                    len(component.get("terminals", []) or []),
                    timing_on,
                    body_label_words,
                )
                for side in ordered_sides
            }
            for side in ordered_sides:
                result = futures[side].result()
                if result is not None:
                    side_results[side] = result

    for side in ordered_sides:
        result = side_results.get(side)
        if result is None:
            continue
        _apply_side_term_updates(component, result["terms"])
        if timing_on:
            debug["timing_ms"]["side_ocr_ms"] += float(result["timing"]["ocr_ms"])
            debug["timing_ms"]["component_fallback_ms"] += float(result["timing"]["component_fallback_ms"])
            debug["timing_ms"]["sides"][side] = result["timing"]
        debug["side_runs"].append(result["side_debug"])

    _reassign_cross_side_labels(component, side_runs, body_bbox, cfg)
    _repair_sequential_pin_labels(component)
    _remove_duplicate_sequential_labels(component)
    _repair_unique_pin_numbers(component)
    _repair_555_timer_pin_numbers(component)
    _repair_three_pin_corner_package_numbers(component)
    if cfg["skip_labels_when_marking_and_number"]:
        debug["labels_cleared_count"] = _clear_pin_labels_when_number_and_marking(component)
    debug["seven_segment_removed_terminals"] = _prune_seven_segment_display_terminals(component)

    assigned_count = sum(
        1
        for term in component.get("terminals", []) or []
        if term.get("pin_number") not in (None, "") or term.get("pin_label_text") not in (None, "")
    )
    debug["assigned_count"] = assigned_count
    if timing_on and total_start is not None:
        debug["timing_ms"]["total_ms"] = _elapsed_ms(total_start)
    component["ic_pin_ocr_debug"] = debug
    return component
