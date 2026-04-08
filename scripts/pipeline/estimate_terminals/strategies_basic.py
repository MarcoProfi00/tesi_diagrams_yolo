from .config import *
from .geometry import geom_clamp_bbox_to_image, geom_infer_orientation_from_bbox
from .probes import (
    get_local_terminal_probe_scores_center,
    get_local_terminal_probe_scores_multi_anchor,
    get_round_source_probe_scores,
    get_round_source_far_probe_scores,
    img_count_foreground_pixels,
    probe_get_side_scores,
)
# =========================================================
# STRATEGY: ONE-TERMINAL COMPONENTS
# =========================================================
def strategy_detect_connected_side(binary, bbox):
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)
    xc = int(round((x1 + x2) / 2))
    yc = int(round((y1 + y2) / 2))
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)
    half_band_x = max(4, int(width * SIDE_CENTER_RATIO / 2))
    half_band_y = max(4, int(height * SIDE_CENTER_RATIO / 2))

    side_scores = {
        "top": img_count_foreground_pixels(binary, xc - half_band_x, y1 - SIDE_SAMPLE_THICKNESS, xc + half_band_x + 1, y1),
        "bottom": img_count_foreground_pixels(binary, xc - half_band_x, y2 + 1, xc + half_band_x + 1, y2 + 1 + SIDE_SAMPLE_THICKNESS),
        "left": img_count_foreground_pixels(binary, x1 - SIDE_SAMPLE_THICKNESS, yc - half_band_y, x1, yc + half_band_y + 1),
        "right": img_count_foreground_pixels(binary, x2 + 1, yc - half_band_y, x2 + 1 + SIDE_SAMPLE_THICKNESS, yc + half_band_y + 1),
    }
    best_side = max(side_scores, key=side_scores.get)
    if side_scores[best_side] < SIDE_SCORE_MIN_PIXELS:
        return None, side_scores
    return best_side, side_scores

def resolve_one_terminal_orientation(meta: dict, connected_side: str):
    orientations = meta.get("orientations", {})
    for orientation_name, terminals_def in orientations.items():
        for term_def in terminals_def:
            if term_def.get("relative_position") == connected_side:
                return terminals_def, orientation_name

    default_orientation = meta.get("default_orientation")
    if default_orientation is None:
        raise ValueError("Impossibile risolvere one_terminal_by_orientation e manca default_orientation.")
    terminals_def = orientations.get(default_orientation)
    if terminals_def is None:
        raise ValueError(f"Nessuna definizione terminali per default_orientation '{default_orientation}'")
    return terminals_def, default_orientation

# =========================================================
# STRATEGY: TWO-TERMINAL COMPONENTS
# =========================================================
def _decide_axis_from_scores(side_scores):
    lr_pair = min(side_scores["left"], side_scores["right"])
    tb_pair = min(side_scores["top"], side_scores["bottom"])
    lr_score = side_scores["left"] + side_scores["right"]
    tb_score = side_scores["top"] + side_scores["bottom"]

    if lr_pair >= TERMINAL_PROBE_MIN_SIDE_SCORE and lr_score > tb_score * TERMINAL_PROBE_AXIS_MARGIN:
        return "horizontal"
    if tb_pair >= TERMINAL_PROBE_MIN_SIDE_SCORE and tb_score > lr_score * TERMINAL_PROBE_AXIS_MARGIN:
        return "vertical"
    return None

def strategy_detect_two_terminal_orientation_generic(binary, bbox, default_orientation="horizontal"):
    side_scores = get_local_terminal_probe_scores_center(binary, bbox)
    orientation = _decide_axis_from_scores(side_scores)
    if orientation is not None:
        side_scores["decision_mode"] = "local_terminal_probes_center"
        return orientation, side_scores

    coarse_scores = probe_get_side_scores(binary, bbox)
    coarse_orientation = None
    lr_score = coarse_scores["left"] + coarse_scores["right"]
    tb_score = coarse_scores["top"] + coarse_scores["bottom"]
    if coarse_scores["left"] >= SIDE_SCORE_MIN_PIXELS and coarse_scores["right"] >= SIDE_SCORE_MIN_PIXELS and lr_score > tb_score * AXIS_SCORE_MARGIN:
        coarse_orientation = "horizontal"
    elif coarse_scores["top"] >= SIDE_SCORE_MIN_PIXELS and coarse_scores["bottom"] >= SIDE_SCORE_MIN_PIXELS and tb_score > lr_score * AXIS_SCORE_MARGIN:
        coarse_orientation = "vertical"

    if coarse_orientation is not None:
        merged = dict(side_scores)
        merged["coarse_scores"] = coarse_scores
        merged["decision_mode"] = "coarse_side_bands_after_local"
        return coarse_orientation, merged

    side_scores["decision_mode"] = "bbox_fallback_after_local_probes"
    return geom_infer_orientation_from_bbox(bbox, default_orientation=default_orientation), side_scores


def detect_two_terminal_orientation_capacitor(binary, bbox, default_orientation="horizontal"):
    side_scores = get_local_terminal_probe_scores_center(binary, bbox)
    orientation = _decide_axis_from_scores(side_scores)
    if orientation is not None:
        side_scores["decision_mode"] = "capacitor_center_probes"
        return orientation, side_scores

    coarse_scores = probe_get_side_scores(binary, bbox)
    lr_score = coarse_scores["left"] + coarse_scores["right"]
    tb_score = coarse_scores["top"] + coarse_scores["bottom"]
    if coarse_scores["left"] >= SIDE_SCORE_MIN_PIXELS and coarse_scores["right"] >= SIDE_SCORE_MIN_PIXELS and lr_score > tb_score * AXIS_SCORE_MARGIN:
        merged = dict(side_scores)
        merged["coarse_scores"] = coarse_scores
        merged["decision_mode"] = "capacitor_coarse_center_bands"
        return "horizontal", merged
    if coarse_scores["top"] >= SIDE_SCORE_MIN_PIXELS and coarse_scores["bottom"] >= SIDE_SCORE_MIN_PIXELS and tb_score > lr_score * AXIS_SCORE_MARGIN:
        merged = dict(side_scores)
        merged["coarse_scores"] = coarse_scores
        merged["decision_mode"] = "capacitor_coarse_center_bands"
        return "vertical", merged

    side_scores["decision_mode"] = "capacitor_bbox_fallback"
    return geom_infer_orientation_from_bbox(bbox, default_orientation=default_orientation), side_scores


def strategy_detect_two_terminal_orientation_switch(binary, bbox, default_orientation="horizontal"):
    side_scores = get_local_terminal_probe_scores_multi_anchor(binary, bbox)
    orientation = _decide_axis_from_scores(side_scores)
    if orientation is not None:
        side_scores["decision_mode"] = "switch_multi_anchor_probes"
        return orientation, side_scores

    coarse_scores = probe_get_side_scores(binary, bbox)
    lr_score = coarse_scores["left"] + coarse_scores["right"]
    tb_score = coarse_scores["top"] + coarse_scores["bottom"]
    if coarse_scores["left"] >= SIDE_SCORE_MIN_PIXELS and coarse_scores["right"] >= SIDE_SCORE_MIN_PIXELS and lr_score > tb_score * AXIS_SCORE_MARGIN:
        merged = dict(side_scores)
        merged["coarse_scores"] = coarse_scores
        merged["decision_mode"] = "switch_coarse_side_bands"
        return "horizontal", merged
    if coarse_scores["top"] >= SIDE_SCORE_MIN_PIXELS and coarse_scores["bottom"] >= SIDE_SCORE_MIN_PIXELS and tb_score > lr_score * AXIS_SCORE_MARGIN:
        merged = dict(side_scores)
        merged["coarse_scores"] = coarse_scores
        merged["decision_mode"] = "switch_coarse_side_bands"
        return "vertical", merged

    # Per switch aperti il bbox è fuorviante: meglio default_orientation che aspect ratio.
    side_scores["decision_mode"] = "switch_default_orientation_fallback"
    return default_orientation, side_scores

def detect_two_terminal_orientation_led(binary, bbox, default_orientation="vertical"):
    """
    Orientazione dedicata per il LED.

    Heuristica semplice:
    - nei LED verticali le frecce laterali allargano il bbox
      -> bbox più largo => LED verticale
    - nei LED orizzontali succede il contrario
      -> bbox più alto => LED orizzontale

    Se il bbox è quasi quadrato, fallback ai probe.
    """
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)
    width = max(x2 - x1, 1e-6)
    height = max(y2 - y1, 1e-6)

    ratio_wh = width / height
    ratio_hw = height / width

    LED_BBOX_RATIO_MARGIN = 1.08

    # euristica invertita specifica per LED
    if ratio_wh >= LED_BBOX_RATIO_MARGIN:
        return "vertical", {
            "decision_mode": "led_reversed_bbox_vertical",
            "bbox_width": round(width, 2),
            "bbox_height": round(height, 2),
            "bbox_ratio_wh": round(ratio_wh, 4),
        }

    if ratio_hw >= LED_BBOX_RATIO_MARGIN:
        return "horizontal", {
            "decision_mode": "led_reversed_bbox_horizontal",
            "bbox_width": round(width, 2),
            "bbox_height": round(height, 2),
            "bbox_ratio_hw": round(ratio_hw, 4),
        }

    # fallback: probe multi-anchor, meglio dei probe centrati
    side_scores = get_local_terminal_probe_scores_multi_anchor(
        binary,
        bbox,
        anchor_ratios=(0.25, 0.50, 0.75)
    )

    orientation = _decide_axis_from_scores(side_scores)
    if orientation is not None:
        side_scores["decision_mode"] = "led_multi_anchor_fallback"
        side_scores["bbox_width"] = round(width, 2)
        side_scores["bbox_height"] = round(height, 2)
        return orientation, side_scores

    # ultimo fallback
    side_scores["decision_mode"] = "led_default_fallback"
    side_scores["bbox_width"] = round(width, 2)
    side_scores["bbox_height"] = round(height, 2)
    return default_orientation, side_scores

def detect_two_terminal_orientation_round_source(binary, bbox, default_orientation="vertical"):
    """
    Strategia dedicata per simboli rotondi a 2 terminali.

    Obiettivo:
    - evitare che il cerchio interno falsi left/right oppure top/bottom
    - evitare che il bordo immagine o testo vicino pesino troppo

    Flusso:
    1. probe near stretti e SOLO esterni
    2. probe far per conferma continuità wire
    3. decisione asse
    4. fallback su aspect ratio se il bbox è abbastanza non quadrato
    5. ultimo fallback: default_orientation YAML
    """
    near_scores = get_round_source_probe_scores(binary, bbox)
    far_scores = get_round_source_far_probe_scores(binary, bbox)

    combined_scores = {
        "top": near_scores["top"] + ROUND_SOURCE_FAR_WEIGHT * far_scores["top"],
        "bottom": near_scores["bottom"] + ROUND_SOURCE_FAR_WEIGHT * far_scores["bottom"],
        "left": near_scores["left"] + ROUND_SOURCE_FAR_WEIGHT * far_scores["left"],
        "right": near_scores["right"] + ROUND_SOURCE_FAR_WEIGHT * far_scores["right"],
        "near_scores": near_scores,
        "far_scores": far_scores,
        "probe_mode": "round_source_near_far",
    }

    lr_pair = min(combined_scores["left"], combined_scores["right"])
    tb_pair = min(combined_scores["top"], combined_scores["bottom"])
    lr_score = combined_scores["left"] + combined_scores["right"]
    tb_score = combined_scores["top"] + combined_scores["bottom"]

    if (
        lr_pair >= ROUND_SOURCE_MIN_SIDE_SCORE and
        lr_score > tb_score * ROUND_SOURCE_AXIS_MARGIN
    ):
        combined_scores["decision_mode"] = "round_source_near_far_horizontal"
        return "horizontal", combined_scores

    if (
        tb_pair >= ROUND_SOURCE_MIN_SIDE_SCORE and
        tb_score > lr_score * ROUND_SOURCE_AXIS_MARGIN
    ):
        combined_scores["decision_mode"] = "round_source_near_far_vertical"
        return "vertical", combined_scores

    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)
    width = max(x2 - x1, 1e-6)
    height = max(y2 - y1, 1e-6)

    ratio_wh = width / height
    ratio_hw = height / width

    combined_scores["bbox_width"] = round(width, 2)
    combined_scores["bbox_height"] = round(height, 2)

    if ratio_wh >= ROUND_SOURCE_BBOX_RATIO_MARGIN:
        combined_scores["decision_mode"] = "round_source_bbox_fallback_horizontal"
        combined_scores["bbox_ratio_wh"] = round(ratio_wh, 4)
        return "horizontal", combined_scores

    if ratio_hw >= ROUND_SOURCE_BBOX_RATIO_MARGIN:
        combined_scores["decision_mode"] = "round_source_bbox_fallback_vertical"
        combined_scores["bbox_ratio_hw"] = round(ratio_hw, 4)
        return "vertical", combined_scores

    combined_scores["decision_mode"] = "round_source_default_fallback"
    return default_orientation, combined_scores