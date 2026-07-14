from .config import *
from .image_ops import img_count_foreground_pixels
from .geometry import geom_clamp_bbox_to_image

# =========================================================
# PROBE HELPERS - GENERIC
# =========================================================
# Calcola gli score dei lati con probe locali.
def probe_get_side_scores(binary, bbox):
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)
    xc = int(round((x1 + x2) / 2))
    yc = int(round((y1 + y2) / 2))
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)
    half_band_x = max(4, int(width * SIDE_CENTER_RATIO / 2))
    half_band_y = max(4, int(height * SIDE_CENTER_RATIO / 2))
    return {
        "top": img_count_foreground_pixels(binary, xc - half_band_x, y1 - SIDE_SAMPLE_THICKNESS, xc + half_band_x + 1, y1),
        "bottom": img_count_foreground_pixels(binary, xc - half_band_x, y2 + 1, xc + half_band_x + 1, y2 + 1 + SIDE_SAMPLE_THICKNESS),
        "left": img_count_foreground_pixels(binary, x1 - SIDE_SAMPLE_THICKNESS, yc - half_band_y, x1, yc + half_band_y + 1),
        "right": img_count_foreground_pixels(binary, x2 + 1, yc - half_band_y, x2 + 1 + SIDE_SAMPLE_THICKNESS, yc + half_band_y + 1),
    }


# Calcola l'halfspan dei probe.
def _probe_halfspan(width, height):
    min_dim = max(1, min(width, height))
    halfspan = int(round(min_dim * TERMINAL_PROBE_HALFSPAN_RATIO))
    halfspan = max(TERMINAL_PROBE_HALFSPAN_MIN, halfspan)
    halfspan = min(TERMINAL_PROBE_HALFSPAN_MAX, halfspan)
    return halfspan


# Calcola gli score locali centrati dei terminali.
def get_local_terminal_probe_scores_center(binary, bbox):
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)
    xc = int(round((x1 + x2) / 2))
    yc = int(round((y1 + y2) / 2))
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)
    halfspan = _probe_halfspan(width, height)

    return {
        "top": img_count_foreground_pixels(binary, xc - halfspan, y1 - TERMINAL_PROBE_OUT_LEN, xc + halfspan + 1, y1 + TERMINAL_PROBE_INSET + 1),
        "bottom": img_count_foreground_pixels(binary, xc - halfspan, y2 - TERMINAL_PROBE_INSET, xc + halfspan + 1, y2 + TERMINAL_PROBE_OUT_LEN + 1),
        "left": img_count_foreground_pixels(binary, x1 - TERMINAL_PROBE_OUT_LEN, yc - halfspan, x1 + TERMINAL_PROBE_INSET + 1, yc + halfspan + 1),
        "right": img_count_foreground_pixels(binary, x2 - TERMINAL_PROBE_INSET, yc - halfspan, x2 + TERMINAL_PROBE_OUT_LEN + 1, yc + halfspan + 1),
        "probe_halfspan": halfspan,
        "probe_out_len": TERMINAL_PROBE_OUT_LEN,
        "probe_inset": TERMINAL_PROBE_INSET,
        "probe_mode": "center",
    }


# Calcola gli score locali usando più ancore.
def get_local_terminal_probe_scores_multi_anchor(binary, bbox, anchor_ratios=SWITCH_ANCHOR_RATIOS):
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)
    halfspan = _probe_halfspan(width, height)

    x_anchors = [int(round(x1 + width * r)) for r in anchor_ratios]
    y_anchors = [int(round(y1 + height * r)) for r in anchor_ratios]

    top_candidates = [
        img_count_foreground_pixels(binary, xa - halfspan, y1 - TERMINAL_PROBE_OUT_LEN, xa + halfspan + 1, y1 + TERMINAL_PROBE_INSET + 1)
        for xa in x_anchors
    ]
    bottom_candidates = [
        img_count_foreground_pixels(binary, xa - halfspan, y2 - TERMINAL_PROBE_INSET, xa + halfspan + 1, y2 + TERMINAL_PROBE_OUT_LEN + 1)
        for xa in x_anchors
    ]
    left_candidates = [
        img_count_foreground_pixels(binary, x1 - TERMINAL_PROBE_OUT_LEN, ya - halfspan, x1 + TERMINAL_PROBE_INSET + 1, ya + halfspan + 1)
        for ya in y_anchors
    ]
    right_candidates = [
        img_count_foreground_pixels(binary, x2 - TERMINAL_PROBE_INSET, ya - halfspan, x2 + TERMINAL_PROBE_OUT_LEN + 1, ya + halfspan + 1)
        for ya in y_anchors
    ]

    return {
        "top": max(top_candidates) if top_candidates else 0,
        "bottom": max(bottom_candidates) if bottom_candidates else 0,
        "left": max(left_candidates) if left_candidates else 0,
        "right": max(right_candidates) if right_candidates else 0,
        "probe_halfspan": halfspan,
        "probe_out_len": TERMINAL_PROBE_OUT_LEN,
        "probe_inset": TERMINAL_PROBE_INSET,
        "probe_mode": "multi_anchor",
        "x_anchors": x_anchors,
        "y_anchors": y_anchors,
    }

# Calcola l'halfspan dei probe LED.
def _led_probe_halfspan(width, height):
    min_dim = max(1, min(width, height))
    halfspan = int(round(min_dim * LED_PROBE_HALFSPAN_RATIO))
    halfspan = max(LED_PROBE_HALFSPAN_MIN, halfspan)
    halfspan = min(LED_PROBE_HALFSPAN_MAX, halfspan)
    return halfspan


# Calcola gli score dei probe LED.
def get_led_probe_scores(binary, bbox):
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)
    xc = int(round((x1 + x2) / 2))
    yc = int(round((y1 + y2) / 2))

    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)

    halfspan = _led_probe_halfspan(width, height)

    x_halfband = max(2, int(round(width * LED_CENTER_BAND_RATIO / 2)))
    y_halfband = max(2, int(round(height * LED_CENTER_BAND_RATIO / 2)))

    return {
        "top": img_count_foreground_pixels(
            binary,
            xc - x_halfband,
            y1 - LED_PROBE_OUT_LEN,
            xc + x_halfband + 1,
            y1 + LED_PROBE_INSET + 1
        ),
        "bottom": img_count_foreground_pixels(
            binary,
            xc - x_halfband,
            y2 - LED_PROBE_INSET,
            xc + x_halfband + 1,
            y2 + LED_PROBE_OUT_LEN + 1
        ),
        "left": img_count_foreground_pixels(
            binary,
            x1 - LED_PROBE_OUT_LEN,
            yc - y_halfband,
            x1 + LED_PROBE_INSET + 1,
            yc + y_halfband + 1
        ),
        "right": img_count_foreground_pixels(
            binary,
            x2 - LED_PROBE_INSET,
            yc - y_halfband,
            x2 + LED_PROBE_OUT_LEN + 1,
            yc + y_halfband + 1
        ),
        "probe_halfspan": halfspan,
        "probe_out_len": LED_PROBE_OUT_LEN,
        "probe_inset": LED_PROBE_INSET,
        "probe_mode": "led_narrow_center_probes",
    }

# Calcola gli score dei probe LED lontani.
def get_led_far_probe_scores(binary, bbox):
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)
    xc = int(round((x1 + x2) / 2))
    yc = int(round((y1 + y2) / 2))

    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)

    x_halfband = max(2, int(round(width * LED_CENTER_BAND_RATIO / 2)))
    y_halfband = max(2, int(round(height * LED_CENTER_BAND_RATIO / 2)))

    gap = LED_FAR_GAP
    far_len = LED_FAR_LEN

    return {
        "top": img_count_foreground_pixels(
            binary,
            xc - x_halfband,
            y1 - gap - far_len,
            xc + x_halfband + 1,
            y1 - gap
        ),
        "bottom": img_count_foreground_pixels(
            binary,
            xc - x_halfband,
            y2 + 1 + gap,
            xc + x_halfband + 1,
            y2 + 1 + gap + far_len
        ),
        "left": img_count_foreground_pixels(
            binary,
            x1 - gap - far_len,
            yc - y_halfband,
            x1 - gap,
            yc + y_halfband + 1
        ),
        "right": img_count_foreground_pixels(
            binary,
            x2 + 1 + gap,
            yc - y_halfband,
            x2 + 1 + gap + far_len,
            yc + y_halfband + 1
        ),
    }

# Calcola l'halfspan per il lato singolo del MOSFET.
def _mosfet_single_side_halfspan(width, height):
    min_dim = max(1, min(width, height))
    halfspan = int(round(min_dim * MOSFET_SINGLE_SIDE_HALFSPAN_RATIO))
    halfspan = max(MOSFET_SINGLE_SIDE_HALFSPAN_MIN, halfspan)
    halfspan = min(MOSFET_SINGLE_SIDE_HALFSPAN_MAX, halfspan)
    return halfspan


# Calcola gli score del lato singolo del MOSFET.
def get_mosfet_single_side_scores(binary, bbox):
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)
    xc = int(round((x1 + x2) / 2))
    yc = int(round((y1 + y2) / 2))
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)
    halfspan = _mosfet_single_side_halfspan(width, height)

    # ---------------------------
    # Probe near: SOLO esterni
    # ---------------------------
    near_scores = {
        "top": img_count_foreground_pixels(
            binary,
            xc - halfspan,
            y1 - MOSFET_SINGLE_SIDE_OUT_LEN,
            xc + halfspan + 1,
            y1
        ),
        "bottom": img_count_foreground_pixels(
            binary,
            xc - halfspan,
            y2 + 1,
            xc + halfspan + 1,
            y2 + 1 + MOSFET_SINGLE_SIDE_OUT_LEN
        ),
        "left": img_count_foreground_pixels(
            binary,
            x1 - MOSFET_SINGLE_SIDE_OUT_LEN,
            yc - halfspan,
            x1,
            yc + halfspan + 1
        ),
        "right": img_count_foreground_pixels(
            binary,
            x2 + 1,
            yc - halfspan,
            x2 + 1 + MOSFET_SINGLE_SIDE_OUT_LEN,
            yc + halfspan + 1
        ),
    }

    # ---------------------------
    # Probe far: continuità wire
    # ---------------------------
    gap = MOSFET_SINGLE_SIDE_FAR_GAP
    far_len = MOSFET_SINGLE_SIDE_FAR_LEN

    far_scores = {
        "top": img_count_foreground_pixels(
            binary,
            xc - halfspan,
            y1 - gap - far_len,
            xc + halfspan + 1,
            y1 - gap
        ),
        "bottom": img_count_foreground_pixels(
            binary,
            xc - halfspan,
            y2 + 1 + gap,
            xc + halfspan + 1,
            y2 + 1 + gap + far_len
        ),
        "left": img_count_foreground_pixels(
            binary,
            x1 - gap - far_len,
            yc - halfspan,
            x1 - gap,
            yc + halfspan + 1
        ),
        "right": img_count_foreground_pixels(
            binary,
            x2 + 1 + gap,
            yc - halfspan,
            x2 + 1 + gap + far_len,
            yc + halfspan + 1
        ),
    }

    combined_scores = {
        side: near_scores[side] + MOSFET_SINGLE_SIDE_FAR_WEIGHT * far_scores[side]
        for side in ("top", "bottom", "left", "right")
    }

    combined_scores["near_scores"] = near_scores
    combined_scores["far_scores"] = far_scores
    combined_scores["probe_halfspan"] = halfspan
    combined_scores["probe_out_len"] = MOSFET_SINGLE_SIDE_OUT_LEN
    combined_scores["probe_mode"] = "mosfet_single_side_near_far"
    return combined_scores

# Calcola gli score laterali del gate MOSFET.
def get_mosfet_lateral_gate_scores(binary, bbox):
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)

    outside_scores = get_mosfet_single_side_scores(binary, bbox)

    inside_w = max(MOSFET_GATE_INSIDE_X_MIN, int(round(width * MOSFET_GATE_INSIDE_X_RATIO)))
    cy1 = int(round(y1 + height * MOSFET_GATE_CENTER_Y1_RATIO))
    cy2 = int(round(y1 + height * MOSFET_GATE_CENTER_Y2_RATIO))
    outside_strip_w = max(2, int(round(width * 0.10)))
    outer_y1 = y1 + max(1, int(round(0.06 * height)))
    outer_y2 = y2 - max(1, int(round(0.06 * height)))
    corner_w = max(3, int(round(width * 0.20)))
    corner_h = max(3, int(round(height * 0.22)))

    outer_mass_left = img_count_foreground_pixels(
        binary,
        x1 - outside_strip_w,
        outer_y1,
        x1,
        outer_y2 + 1,
    )

    outer_mass_right = img_count_foreground_pixels(
        binary,
        x2 + 1,
        outer_y1,
        x2 + 1 + outside_strip_w,
        outer_y2 + 1,
    )

    inside_left = img_count_foreground_pixels(
        binary,
        x1 + 1,
        cy1,
        x1 + 1 + inside_w,
        cy2
    )

    inside_right = img_count_foreground_pixels(
        binary,
        x2 - inside_w,
        cy1,
        x2,
        cy2
    )

    corner_mass_left = (
        img_count_foreground_pixels(
            binary,
            x1 + 1,
            y1 + 1,
            x1 + 1 + corner_w,
            y1 + 1 + corner_h,
        )
        + img_count_foreground_pixels(
            binary,
            x1 + 1,
            y2 - corner_h,
            x1 + 1 + corner_w,
            y2,
        )
    )

    corner_mass_right = (
        img_count_foreground_pixels(
            binary,
            x2 - corner_w,
            y1 + 1,
            x2,
            y1 + 1 + corner_h,
        )
        + img_count_foreground_pixels(
            binary,
            x2 - corner_w,
            y2 - corner_h,
            x2,
            y2,
        )
    )

    # Il gate laterale tende ad avere una connessione compatta e concentrata
    # nella banda centrale, mentre il lato drain/source spesso genera una massa
    # esterna piu' diffusa lungo tutto il lato. Il rapporto centro/massa aiuta
    # a risolvere i casi speculari come M3/M7 del batch v8.
    left_focus_ratio = float(outside_scores["left"]) / float(max(outer_mass_left, 1))
    right_focus_ratio = float(outside_scores["right"]) / float(max(outer_mass_right, 1))
    focus_bonus_scale = 45.0
    corner_penalty_scale = 0.45

    combined_left = (
        outside_scores["left"]
        + MOSFET_GATE_INSIDE_WEIGHT * inside_left
        + focus_bonus_scale * left_focus_ratio
        - corner_penalty_scale * corner_mass_left
    )
    combined_right = (
        outside_scores["right"]
        + MOSFET_GATE_INSIDE_WEIGHT * inside_right
        + focus_bonus_scale * right_focus_ratio
        - corner_penalty_scale * corner_mass_right
    )

    return {
        "left": combined_left,
        "right": combined_right,
        "outside_left": outside_scores["left"],
        "outside_right": outside_scores["right"],
        "inside_left": inside_left,
        "inside_right": inside_right,
        "outer_mass_left": outer_mass_left,
        "outer_mass_right": outer_mass_right,
        "focus_ratio_left": round(left_focus_ratio, 4),
        "focus_ratio_right": round(right_focus_ratio, 4),
        "focus_bonus_scale": focus_bonus_scale,
        "corner_mass_left": corner_mass_left,
        "corner_mass_right": corner_mass_right,
        "corner_penalty_scale": corner_penalty_scale,
        "probe_mode": "mosfet_lateral_gate_combined",
    }

# =========================================================
# PROBE HELPERS - CLASS "Terminal"
# =========================================================
# Terminal class probe halfspan.
def _terminal_class_probe_halfspan(width, height):
    min_dim = max(1, min(width, height))
    halfspan = int(round(min_dim * TERMINAL_CLASS_PROBE_HALFSPAN_RATIO))
    halfspan = max(TERMINAL_CLASS_PROBE_HALFSPAN_MIN, halfspan)
    halfspan = min(TERMINAL_CLASS_PROBE_HALFSPAN_MAX, halfspan)
    return halfspan


# Calcola gli score probe per la classe Terminal.
def get_terminal_class_probe_scores(binary, bbox):
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)
    xc = int(round((x1 + x2) / 2))
    yc = int(round((y1 + y2) / 2))
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)
    halfspan = _terminal_class_probe_halfspan(width, height)

    scores = {
        "top": img_count_foreground_pixels(
            binary,
            xc - halfspan,
            y1 - TERMINAL_CLASS_PROBE_OUT_LEN,
            xc + halfspan + 1,
            y1
        ),
        "bottom": img_count_foreground_pixels(
            binary,
            xc - halfspan,
            y2 + 1,
            xc + halfspan + 1,
            y2 + 1 + TERMINAL_CLASS_PROBE_OUT_LEN
        ),
        "left": img_count_foreground_pixels(
            binary,
            x1 - TERMINAL_CLASS_PROBE_OUT_LEN,
            yc - halfspan,
            x1,
            yc + halfspan + 1
        ),
        "right": img_count_foreground_pixels(
            binary,
            x2 + 1,
            yc - halfspan,
            x2 + 1 + TERMINAL_CLASS_PROBE_OUT_LEN,
            yc + halfspan + 1
        ),
    }

    scores["probe_halfspan"] = halfspan
    scores["probe_out_len"] = TERMINAL_CLASS_PROBE_OUT_LEN
    scores["probe_mode"] = "terminal_outside_only"
    return scores


# Calcola gli score probe lontani per la classe Terminal.
def get_terminal_class_far_probe_scores(binary, bbox):
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)
    xc = int(round((x1 + x2) / 2))
    yc = int(round((y1 + y2) / 2))
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)
    halfspan = _terminal_class_probe_halfspan(width, height)

    gap = TERMINAL_CLASS_FAR_GAP
    far_len = TERMINAL_CLASS_FAR_LEN

    return {
        "top": img_count_foreground_pixels(
            binary,
            xc - halfspan,
            y1 - gap - far_len,
            xc + halfspan + 1,
            y1 - gap
        ),
        "bottom": img_count_foreground_pixels(
            binary,
            xc - halfspan,
            y2 + 1 + gap,
            xc + halfspan + 1,
            y2 + 1 + gap + far_len
        ),
        "left": img_count_foreground_pixels(
            binary,
            x1 - gap - far_len,
            yc - halfspan,
            x1 - gap,
            yc + halfspan + 1
        ),
        "right": img_count_foreground_pixels(
            binary,
            x2 + 1 + gap,
            yc - halfspan,
            x2 + 1 + gap + far_len,
            yc + halfspan + 1
        ),
    }

# Calcola la preferenza del bordo per il terminale.
def get_terminal_border_preference(binary_shape, bbox, margin=TERMINAL_CLASS_BORDER_MARGIN):
    h, w = binary_shape[:2]
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, (h, w))

    distances = {
        "left": x1,
        "right": (w - 1 - x2),
        "top": y1,
        "bottom": (h - 1 - y2),
    }

    nearest_side = min(distances, key=distances.get)
    if distances[nearest_side] > margin:
        return None

    opposite = {
        "left": "right",
        "right": "left",
        "top": "bottom",
        "bottom": "top",
    }
    return opposite[nearest_side]


# Verifica se il terminale è vicino al bordo immagine.
def is_terminal_near_border(binary_shape, bbox):
    h, w = binary_shape[:2]
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, (h, w))
    margin = max(TERMINAL_BORDER_MARGIN_MIN, int(TERMINAL_BORDER_MARGIN_RATIO * min(h, w)))

    return (
        x1 <= margin or
        y1 <= margin or
        (w - 1 - x2) <= margin or
        (h - 1 - y2) <= margin
    )

# Valuta il supporto locale di un punto.
def score_point_local_support(binary, x, y, radius=MOSFET_POINT_SUPPORT_RADIUS):
    xi = int(round(x))
    yi = int(round(y))
    return img_count_foreground_pixels(
        binary,
        xi - radius,
        yi - radius,
        xi + radius + 1,
        yi + radius + 1
    )

# Valuta il supporto direzionale di un punto.
def score_point_directional_support(
    binary,
    x,
    y,
    relative_position,
    outward=10,
    inward=3,
    halfspan=4,
):
    h, w = binary.shape[:2]
    xi = int(round(x))
    yi = int(round(y))

    if relative_position == "left":
        x1, y1, x2, y2 = (
            xi - outward,
            yi - halfspan,
            xi + inward + 1,
            yi + halfspan + 1,
        )
    elif relative_position == "right":
        x1, y1, x2, y2 = (
            xi - inward,
            yi - halfspan,
            xi + outward + 1,
            yi + halfspan + 1,
        )
    elif relative_position == "top":
        x1, y1, x2, y2 = (
            xi - halfspan,
            yi - outward,
            xi + halfspan + 1,
            yi + inward + 1,
        )
    elif relative_position == "bottom":
        x1, y1, x2, y2 = (
            xi - halfspan,
            yi - inward,
            xi + halfspan + 1,
            yi + outward + 1,
        )
    else:
        x1, y1, x2, y2 = (
            xi - outward,
            yi - outward,
            xi + outward + 1,
            yi + outward + 1,
        )

    x1 = max(0, min(w, x1))
    y1 = max(0, min(h, y1))
    x2 = max(0, min(w, x2))
    y2 = max(0, min(h, y2))

    if x2 <= x1 or y2 <= y1:
        return 0

    return img_count_foreground_pixels(binary, x1, y1, x2, y2)


# Valuta il supporto ortogonale di un punto.
def score_point_orthogonal_support(binary, x, y, relative_position):
    if relative_position in {"left", "right"}:
        return (
            score_point_directional_support(binary, x, y, "top")
            + score_point_directional_support(binary, x, y, "bottom")
        )

    if relative_position in {"top", "bottom"}:
        return (
            score_point_directional_support(binary, x, y, "left")
            + score_point_directional_support(binary, x, y, "right")
        )

    return 0


# Valuta i terminali candidati del MOSFET.
def score_mosfet_candidate_terminals(binary, terminals, single_side, single_weight=1.35):
    total = 0.0
    details = []

    for term in terminals:
        rel = term["relative_position"]
        x = term["x"]
        y = term["y"]

        local_score = score_point_local_support(binary, x, y)
        directional_score = score_point_directional_support(binary, x, y, rel)
        orthogonal_support = score_point_orthogonal_support(binary, x, y, rel)

        point_score = local_score + 1.15 * directional_score

        penalty = 0.0
        if rel == single_side:
            penalty = MOSFET_SINGLE_TERMINAL_ORTHOGONAL_PENALTY * orthogonal_support
            point_score = max(0.0, point_score - penalty)

        weight = single_weight if rel == single_side else 1.0
        weighted_score = weight * point_score
        total += weighted_score

        details.append({
            "relative_position": rel,
            "x": round(float(x), 2),
            "y": round(float(y), 2),
            "local_score": round(float(local_score), 3),
            "directional_score": round(float(directional_score), 3),
            "orthogonal_support": round(float(orthogonal_support), 3),
            "orthogonal_penalty": round(float(penalty), 3),
            "weight": round(float(weight), 3),
            "weighted_score": round(float(weighted_score), 3),
        })

    return total, details

# Calcola gli score probe per sorgenti circolari.
def get_round_source_probe_scores(binary, bbox):
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)
    xc = int(round((x1 + x2) / 2))
    yc = int(round((y1 + y2) / 2))

    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)

    x_halfband = max(2, int(round(width * ROUND_SOURCE_CENTER_BAND_RATIO / 2)))
    y_halfband = max(2, int(round(height * ROUND_SOURCE_CENTER_BAND_RATIO / 2)))

    return {
        "top": img_count_foreground_pixels(
            binary,
            xc - x_halfband,
            y1 - ROUND_SOURCE_PROBE_OUT_LEN,
            xc + x_halfband + 1,
            y1
        ),
        "bottom": img_count_foreground_pixels(
            binary,
            xc - x_halfband,
            y2 + 1,
            xc + x_halfband + 1,
            y2 + 1 + ROUND_SOURCE_PROBE_OUT_LEN
        ),
        "left": img_count_foreground_pixels(
            binary,
            x1 - ROUND_SOURCE_PROBE_OUT_LEN,
            yc - y_halfband,
            x1,
            yc + y_halfband + 1
        ),
        "right": img_count_foreground_pixels(
            binary,
            x2 + 1,
            yc - y_halfband,
            x2 + 1 + ROUND_SOURCE_PROBE_OUT_LEN,
            yc + y_halfband + 1
        ),
        "probe_out_len": ROUND_SOURCE_PROBE_OUT_LEN,
        "center_band_ratio": ROUND_SOURCE_CENTER_BAND_RATIO,
        "probe_mode": "round_source_near",
    }


# Calcola gli score probe lontani per sorgenti circolari.
def get_round_source_far_probe_scores(binary, bbox):
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)
    xc = int(round((x1 + x2) / 2))
    yc = int(round((y1 + y2) / 2))

    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)

    x_halfband = max(2, int(round(width * ROUND_SOURCE_CENTER_BAND_RATIO / 2)))
    y_halfband = max(2, int(round(height * ROUND_SOURCE_CENTER_BAND_RATIO / 2)))

    gap = ROUND_SOURCE_FAR_GAP
    far_len = ROUND_SOURCE_FAR_LEN

    return {
        "top": img_count_foreground_pixels(
            binary,
            xc - x_halfband,
            y1 - gap - far_len,
            xc + x_halfband + 1,
            y1 - gap
        ),
        "bottom": img_count_foreground_pixels(
            binary,
            xc - x_halfband,
            y2 + 1 + gap,
            xc + x_halfband + 1,
            y2 + 1 + gap + far_len
        ),
        "left": img_count_foreground_pixels(
            binary,
            x1 - gap - far_len,
            yc - y_halfband,
            x1 - gap,
            yc + y_halfband + 1
        ),
        "right": img_count_foreground_pixels(
            binary,
            x2 + 1 + gap,
            yc - y_halfband,
            x2 + 1 + gap + far_len,
            yc + y_halfband + 1
        ),
    }
