"""
OCR locale dei pin per Integrated_Circuit.

Strategia side_lane_candidates_v1:
- non crea terminali;
- usa i terminali geometrici gia' stimati;
- per ogni lato dell'IC costruisce una banda stretta che attraversa il bordo;
- assegna le parole OCR alla "corsia" del terminale piu' vicino sullo stesso lato;
- separa pin_number e pin_label_text.

Se una lettura non e' affidabile, il campo resta None.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

from .ocr_integrated_circuit import get_ic_body_bbox_from_component


_SIDES = {"left", "right", "top", "bottom"}
_TEXT_ALLOWED_RE = re.compile(r"[^A-Za-z0-9_./+\-]")
_SHORT_PIN_LABELS = {
    "IN", "OUT", "ADJ", "EN", "FB", "PG", "CS", "RD", "WR", "INTR",
    "RESET", "RST", "LSB", "MSB", "VIN", "VOUT", "VCC", "GND", "VAUX",
    "BOOT", "SYNC", "COMP", "PHASE", "PAD", "CLK", "FS",
}


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
    ocr_root = meta.get("ocr") or {}
    cfg = ocr_root.get("pin_labels") or {}
    number_cfg = cfg.get("number_ocr") or {}
    label_cfg = cfg.get("label_ocr") or {}
    lane_cfg = cfg.get("lane_search") or {}
    attach_cfg = cfg.get("attach") or {}

    return {
        "ocr_enabled": bool(ocr_root.get("enabled", False)),
        "enabled": bool(cfg.get("enabled", False)),
        "strategy": cfg.get("strategy", "side_lane_candidates_v1"),
        "skip_component_subtypes": set(cfg.get("skip_component_subtypes", ["seven_segment_display"])),
        "store_debug": bool(cfg.get("store_debug", True)),
        "number_enabled": bool(number_cfg.get("enabled", True)),
        "number_psm": int(number_cfg.get("psm", 11)),
        "number_min_confidence": float(number_cfg.get("min_confidence", 0.25)),
        "label_enabled": bool(label_cfg.get("enabled", True)),
        "label_psm": int(label_cfg.get("psm", 11)),
        "label_min_confidence": float(label_cfg.get("min_confidence", 0.20)),
        "number_pattern": cfg.get("number_pattern", r"^[0-9]{1,3}$"),
        "label_pattern": cfg.get("label_pattern", r"^[A-Za-z][A-Za-z0-9_./+-]{0,15}$"),
        "lane_padding_px": int(lane_cfg.get("lane_padding_px", 6)),
        "side_inside_px": int(lane_cfg.get("side_inside_px", 78)),
        "side_outside_px": int(lane_cfg.get("side_outside_px", 42)),
        "top_bottom_inside_px": int(lane_cfg.get("top_bottom_inside_px", 72)),
        "top_bottom_outside_px": int(lane_cfg.get("top_bottom_outside_px", 42)),
        "upscale": float(lane_cfg.get("upscale", 3.0)),
        "line_kernel_ratio": float(lane_cfg.get("line_kernel_ratio", 0.33)),
        "component_fallback_enabled": bool(lane_cfg.get("component_fallback_enabled", True)),
        "max_number_distance_px": float(attach_cfg.get("max_number_distance_px", 42)),
        "max_label_distance_px": float(attach_cfg.get("max_label_distance_px", 86)),
        "reject_overlap_ratio": float(attach_cfg.get("reject_overlap_ratio", 0.50)),
    }


def _reset_pin_fields(component: Dict) -> None:
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


def _build_side_lanes(component: Dict, body_bbox, image_shape, cfg: Dict) -> Dict[str, Dict]:
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
    gray = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4)).apply(gray)
    scale = max(float(cfg["upscale"]), 1.0)
    if scale != 1.0:
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cleaned = _remove_long_lines(binary, cfg)
    return cleaned, scale


def _extract_digit_components(image_bgr, band_bbox: List[int]) -> List[Dict]:
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


def _ocr_digit_candidates_batch(image_bgr, candidates: List[Dict], cfg: Dict) -> Dict[int, Dict[str, int]]:
    if not candidates:
        return {}

    tesseract_cmd = os.environ.get("TESSERACT_CMD", "tesseract")
    variants = [
        (4, 4.0, "bin", 6),
        (4, 4.0, "gray", 8),
        (4, 6.0, "bin", 10),
        (4, 6.0, "gray", 13),
        (6, 4.0, "gray", 6),
        (10, 8.0, "bin", 6),
        (10, 8.0, "gray", 6),
        (14, 6.0, "bin", 8),
    ]

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


def _best_voted_number(votes: Dict[str, int], component_count: int, cfg: Dict) -> Optional[str]:
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
    return {
        "text": text,
        "confidence": confidence,
        "bbox": bbox,
        "center": [(bbox[0] + bbox[2]) * 0.5, (bbox[1] + bbox[3]) * 0.5],
        "mode": "number_component",
    }


def _component_number_words(image_bgr, side_run: Dict, cfg: Dict, target_lanes: Optional[List[Dict]] = None) -> List[Dict]:
    components = _extract_digit_components(image_bgr, side_run["band_bbox"])
    lanes = target_lanes if target_lanes is not None else side_run["lanes"]
    candidates = []
    for candidate in _group_digit_components(components):
        cx, cy = candidate["center"]
        if not any(_bbox_contains_point(lane["lane_bbox"], cx, cy) for lane in lanes):
            continue
        candidates.append(candidate)

    votes_by_candidate = _ocr_digit_candidates_batch(image_bgr, candidates, cfg)
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
        if not cfg["label_enabled"]:
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
        for lane in lanes:
            if _bbox_contains_point(lane["lane_bbox"], cx, cy):
                assigned[lane["terminal_id"]].append(word)
                break
    return assigned


def _is_number_text(text: str, cfg: Dict) -> bool:
    return bool(re.match(cfg["number_pattern"], text or ""))


def _is_label_candidate(word: Dict, cfg: Dict) -> bool:
    text = str(word.get("text") or "")
    confidence = float(word.get("confidence") or 0.0)
    if not text or _is_number_text(text, cfg):
        return False
    if not re.search(r"[A-Za-z]", text):
        return False
    if not re.match(cfg["label_pattern"], text):
        return False

    upper = text.upper()
    if len(upper) < 2:
        return False
    if upper in _SHORT_PIN_LABELS:
        return confidence >= max(cfg["label_min_confidence"], 0.35)
    if re.match(r"^[A-Z][0-9]{1,2}(?:\.[0-9])?$", upper):
        return confidence >= max(cfg["label_min_confidence"], 0.25)
    if re.match(r"^[A-Z]{1,3}[0-9]{1,2}(?:\.[0-9])?$", upper):
        return confidence >= max(cfg["label_min_confidence"], 0.35)
    return len(upper) >= 3 and confidence >= max(cfg["label_min_confidence"], 0.45)


def _pick_best_word(words: List[Dict], side: str, body_bbox: List[float], max_distance_px: float) -> Optional[Dict]:
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


def _assign_lane_semantics(side_run: Dict, text_words: List[Dict], number_words: List[Dict], body_bbox, cfg: Dict) -> None:
    side = side_run["side"]
    lanes = side_run["lanes"]
    text_map = _assign_words_to_lanes(text_words, lanes)
    number_map = _assign_words_to_lanes(number_words, lanes)

    for lane in lanes:
        term = lane["term"]
        lane_text_words = text_map.get(lane["terminal_id"], [])
        lane_number_words = number_map.get(lane["terminal_id"], [])

        label_candidates = [
            word for word in lane_text_words
            if _is_label_candidate(word, cfg)
        ]
        numeric_from_text = [
            word for word in lane_text_words
            if word["confidence"] >= cfg["label_min_confidence"] and _is_number_text(word["text"], cfg)
        ]
        numeric_fallback = [
            word for word in lane_number_words
            if word["confidence"] >= cfg["number_min_confidence"] and _is_number_text(word["text"], cfg)
        ]

        if label_candidates:
            filtered_fallback = []
            for number_word in numeric_fallback:
                overlaps_label = any(
                    _bbox_overlap_ratio(number_word["bbox"], label_word["bbox"]) >= cfg["reject_overlap_ratio"]
                    for label_word in label_candidates
                )
                if not overlaps_label:
                    filtered_fallback.append(number_word)
            numeric_fallback = filtered_fallback

        best_label = _pick_best_word(
            label_candidates,
            side=side,
            body_bbox=body_bbox,
            max_distance_px=cfg["max_label_distance_px"],
        )
        best_number = _pick_best_word(
            numeric_from_text,
            side=side,
            body_bbox=body_bbox,
            max_distance_px=cfg["max_number_distance_px"],
        )
        if best_number is None:
            best_number = _pick_best_word(
                numeric_fallback,
                side=side,
                body_bbox=body_bbox,
                max_distance_px=cfg["max_number_distance_px"],
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

        if best_label is not None:
            term["pin_label_text"] = best_label["text"]
            term["pin_label_confidence"] = round(float(best_label["confidence"]), 3)
            term["pin_label_bbox"] = best_label["bbox"]
            debug_payload["best_label"] = best_label

        if best_number is not None or best_label is not None or lane_text_words or lane_number_words:
            term["pin_ocr_debug"] = debug_payload


def _assign_component_number_fallback(side_run: Dict, component_words: List[Dict], body_bbox, cfg: Dict) -> None:
    side = side_run["side"]
    component_map = _assign_words_to_lanes(component_words, side_run["lanes"])

    for lane in side_run["lanes"]:
        term = lane["term"]
        candidates = [
            word for word in component_map.get(lane["terminal_id"], [])
            if _is_number_text(word["text"], cfg)
            and _closest_body_side(word, body_bbox) == side
        ]
        best = _pick_best_word(
            candidates,
            side=side,
            body_bbox=body_bbox,
            max_distance_px=max(cfg["max_number_distance_px"], 64.0),
        )
        if best is None:
            continue

        current = str(term.get("pin_number") or "")
        should_assign = not current or len(best["text"]) > len(current)
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
    valid_terms = []
    bad_terms = []
    for term in terminals:
        text = str(term.get("pin_number") or "")
        if re.match(r"^[0-9]+$", text):
            value = int(text)
            if 1 <= value <= max_pin:
                valid_terms.append((value, term))
            else:
                bad_terms.append(term)
        else:
            bad_terms.append(term)

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
        duplicate_terms.extend(same_value_terms[1:])

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


def _lanes_needing_component_fallback(side_run: Dict, component_terminal_count: int) -> List[Dict]:
    lanes = []
    for lane in side_run["lanes"]:
        term = lane["term"]
        number = str(term.get("pin_number") or "")
        confidence = float(term.get("pin_number_confidence") or 0.0)
        if not number:
            lanes.append(lane)
        elif component_terminal_count > 9 and len(number) == 1:
            lanes.append(lane)
        elif confidence < 0.62:
            lanes.append(lane)
    return lanes


def enrich_ic_pin_ocr(component: Dict, image_bgr, meta: Dict) -> Dict:
    cfg = _get_pin_ocr_cfg(meta)
    _reset_pin_fields(component)

    debug = {
        "enabled": bool(cfg["ocr_enabled"] and cfg["enabled"]),
        "strategy": cfg["strategy"],
        "engine": "tesseract",
        "skipped": False,
        "reasons": [],
        "side_runs": [],
        "assigned_count": 0,
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
    side_runs = _build_side_lanes(component, body_bbox, image_bgr.shape, cfg)
    if not side_runs:
        debug["skipped"] = True
        debug["reasons"].append("no_side_lanes")
        component["ic_pin_ocr_debug"] = debug
        return component

    for side in ("left", "right", "top", "bottom"):
        side_run = side_runs.get(side)
        if side_run is None:
            continue

        crop = _crop(image_bgr, side_run["band_bbox"])
        if crop is None:
            continue

        prepared, scale = _prepare_side_band(crop, cfg)
        text_words, text_info = _run_tesseract_words(prepared, side_run["band_bbox"], scale, cfg, mode="text")
        number_words, number_info = _run_tesseract_words(prepared, side_run["band_bbox"], scale, cfg, mode="number")
        _assign_lane_semantics(side_run, text_words, number_words, body_bbox, cfg)
        component_words = []
        if cfg["component_fallback_enabled"] and cfg["number_enabled"]:
            fallback_lanes = _lanes_needing_component_fallback(
                side_run,
                component_terminal_count=len(component.get("terminals", []) or []),
            )
            if fallback_lanes:
                component_words = _component_number_words(image_bgr, side_run, cfg, target_lanes=fallback_lanes)
                _assign_component_number_fallback(side_run, component_words, body_bbox, cfg)

        debug["side_runs"].append({
            "side": side,
            "band_bbox": side_run["band_bbox"],
            "lane_count": len(side_run["lanes"]),
            "ocr_text": text_info,
            "ocr_number": number_info,
            "lanes": [
                {
                    "terminal_id": lane["terminal_id"],
                    "lane_bbox": lane["lane_bbox"],
                    "axis_range": lane["axis_range"],
                }
                for lane in side_run["lanes"]
            ] if cfg["store_debug"] else [],
            "text_words": text_words if cfg["store_debug"] else [],
            "number_words": number_words if cfg["store_debug"] else [],
            "component_words": component_words if cfg["store_debug"] else [],
        })

    _repair_unique_pin_numbers(component)

    assigned_count = sum(
        1
        for term in component.get("terminals", []) or []
        if term.get("pin_number") not in (None, "") or term.get("pin_label_text") not in (None, "")
    )
    debug["assigned_count"] = assigned_count
    component["ic_pin_ocr_debug"] = debug
    return component
