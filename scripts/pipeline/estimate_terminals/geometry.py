from .config import *
from .image_ops import img_count_foreground_pixels

# =========================================================
# GENERIC GEOMETRY
# =========================================================
def geom_clamp_bbox_to_image(bbox, image_shape):
    h, w = image_shape[:2]
    x1, y1, x2, y2 = bbox
    x1 = int(max(0, min(w - 1, round(x1))))
    y1 = int(max(0, min(h - 1, round(y1))))
    x2 = int(max(0, min(w - 1, round(x2))))
    y2 = int(max(0, min(h - 1, round(y2))))
    return x1, y1, x2, y2

def geom_terminal_point_from_bbox(bbox, relative_position: str):
    """
    Modalità base:
    mette il terminale al centro geometrico del lato del bbox.

    Va bene per molti componenti semplici.
    Per Mosfet / NPN invece usiamo una stima più precisa lungo il lato.
    """
    x1, y1, x2, y2 = bbox
    xc = (x1 + x2) / 2.0
    yc = (y1 + y2) / 2.0

    if relative_position == "left":
        return [round(x1 - TERMINAL_OUTWARD_OFFSET, 2), round(yc, 2)]
    if relative_position == "right":
        return [round(x2 + TERMINAL_OUTWARD_OFFSET, 2), round(yc, 2)]
    if relative_position == "top":
        return [round(xc, 2), round(y1 - TERMINAL_OUTWARD_OFFSET, 2)]
    if relative_position == "bottom":
        return [round(xc, 2), round(y2 + TERMINAL_OUTWARD_OFFSET, 2)]
    raise ValueError(f"relative_position non supportata: {relative_position}")

def geom_infer_orientation_from_bbox(bbox, default_orientation="horizontal"):
    x1, y1, x2, y2 = bbox
    width = max(x2 - x1, 1e-6)
    height = max(y2 - y1, 1e-6)

    if height / width >= ASPECT_RATIO_THRESHOLD:
        return "vertical"
    if width / height >= ASPECT_RATIO_THRESHOLD:
        return "horizontal"
    return default_orientation

# =========================================================
# GENERIC SIDE-PEAK LOCALIZATION
# =========================================================
def _side_peak_halfspan(width, height):
    """
    Semi-larghezza della probe usata durante la scansione lungo il lato.

    La teniamo piccola per campionare bene il wire vicino al terminale,
    senza farci influenzare troppo dalla grafica interna del simbolo.
    """
    min_dim = max(1, min(width, height))
    halfspan = int(round(min_dim * SIDE_PEAK_HALFSPAN_RATIO))
    halfspan = max(SIDE_PEAK_HALFSPAN_MIN, halfspan)
    halfspan = min(SIDE_PEAK_HALFSPAN_MAX, halfspan)
    return halfspan


def _side_peak_scan_margin(length):
    """
    Evita di campionare esattamente sugli angoli del bbox,
    che spesso non corrispondono a terminali reali.
    """
    margin = int(round(length * SIDE_PEAK_SCAN_MARGIN_RATIO))
    return max(SIDE_PEAK_SCAN_MARGIN_MIN, margin)

def _group_consecutive_indices(indices):
    if not indices:
        return []

    groups = [[indices[0]]]
    for idx in indices[1:]:
        if idx == groups[-1][-1] + 1:
            groups[-1].append(idx)
        else:
            groups.append([idx])
    return groups


def _select_peak_index_from_scores(scores, center_index):
    """
    Dato un profilo 1D di score lungo un lato, sceglie il picco più affidabile.

    Non scegliamo direttamente il singolo massimo pixel, perché sarebbe troppo rumoroso.
    Invece:
    - teniamo i punti vicini al massimo
    - li raggruppiamo in run consecutive
    - scegliamo la run migliore
    - prendiamo il centro della run
    """
    if not scores:
        return None, {
            "max_score": 0,
            "keep_threshold": 0,
            "selected_run_start": None,
            "selected_run_end": None,
            "selected_run_length": 0,
            "selected_run_score": 0,
        }

    max_score = max(scores)

    if max_score < SIDE_PEAK_MIN_SCORE:
        # Se il segnale è troppo debole, fallback sul centro del lato.
        return center_index, {
            "max_score": max_score,
            "keep_threshold": SIDE_PEAK_MIN_SCORE,
            "selected_run_start": center_index,
            "selected_run_end": center_index,
            "selected_run_length": 1,
            "selected_run_score": scores[center_index],
        }

    keep_threshold = max(SIDE_PEAK_MIN_SCORE, int(round(max_score * SIDE_PEAK_KEEP_RATIO)))
    kept = [i for i, score in enumerate(scores) if score >= keep_threshold]

    if not kept:
        best_idx = max(
            range(len(scores)),
            key=lambda i: (scores[i], -abs(i - center_index))
        )
        return best_idx, {
            "max_score": max_score,
            "keep_threshold": keep_threshold,
            "selected_run_start": best_idx,
            "selected_run_end": best_idx,
            "selected_run_length": 1,
            "selected_run_score": scores[best_idx],
        }

    groups = _group_consecutive_indices(kept)

    def group_key(group):
        group_scores = [scores[i] for i in group]
        group_center = (group[0] + group[-1]) / 2.0
        return (
            max(group_scores),                 # run con picco più alto
            sum(group_scores),                 # run con più supporto complessivo
            len(group),                        # run più larga
            -abs(group_center - center_index)  # in caso di parità, più vicina al centro
        )

    best_group = max(groups, key=group_key)
    best_idx = int(round((best_group[0] + best_group[-1]) / 2.0))

    return best_idx, {
        "max_score": max_score,
        "keep_threshold": keep_threshold,
        "selected_run_start": best_group[0],
        "selected_run_end": best_group[-1],
        "selected_run_length": len(best_group),
        "selected_run_score": scores[best_idx],
    }

def geom_terminal_point_by_side_peak(binary, bbox, relative_position: str, scan_start=None, scan_end=None, center_coord=None):
    """
    Localizzazione fine del terminale lungo il lato del bbox.

    Invece di usare sempre il centro del lato:
    - per top/bottom scorriamo lungo X
    - per left/right scorriamo lungo Y

    Possiamo anche passare una finestra di scansione custom (scan_start / scan_end):
    questo serve molto per i componenti a 3 terminali, dove sappiamo già in quale
    zona del lato è più probabile trovare il terminale vero.

    Restituisce:
    - point      : [x, y]
    - debug_info : dizionario con score e dettagli della scansione
    """
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)
    halfspan = _side_peak_halfspan(width, height)

    if relative_position in {"top", "bottom"}:
        margin = _side_peak_scan_margin(width)
        default_start = x1 + margin
        default_end = x2 - margin

        start = default_start if scan_start is None else int(round(scan_start))
        end = default_end if scan_end is None else int(round(scan_end))

        start = max(x1, min(x2, start))
        end = max(x1, min(x2, end))

        if end < start:
            start, end = x1, x2

        coords = list(range(start, end + 1))
        if not coords:
            coords = [int(round((x1 + x2) / 2))]

        scores = []
        for x in coords:
            if relative_position == "top":
                score = img_count_foreground_pixels(
                    binary,
                    x - halfspan,
                    y1 - SIDE_PEAK_OUT_LEN,
                    x + halfspan + 1,
                    y1 + SIDE_PEAK_INSET + 1
                )
            else:
                score = img_count_foreground_pixels(
                    binary,
                    x - halfspan,
                    y2 - SIDE_PEAK_INSET,
                    x + halfspan + 1,
                    y2 + SIDE_PEAK_OUT_LEN + 1
                )
            scores.append(score)

        if center_coord is None:
            center_coord = int(round((start + end) / 2))
        center_index = min(range(len(coords)), key=lambda i: abs(coords[i] - center_coord))
        best_index, peak_info = _select_peak_index_from_scores(scores, center_index)
        best_x = coords[best_index]

        point = [
            round(float(best_x), 2),
            round(float(y1 - TERMINAL_OUTWARD_OFFSET if relative_position == "top" else y2 + TERMINAL_OUTWARD_OFFSET), 2)
        ]

        debug_info = {
            "point_mode": "side_peak_outside",
            "scan_axis": "x",
            "relative_position": relative_position,
            "scan_start": start,
            "scan_end": end,
            "scan_margin": margin,
            "probe_halfspan": halfspan,
            "probe_out_len": SIDE_PEAK_OUT_LEN,
            "probe_inset": SIDE_PEAK_INSET,
            "peak_coord": best_x,
            "anchor_offset_ratio": round((best_x - x1) / max(width, 1), 4),
            **peak_info,
        }
        return point, debug_info

    if relative_position in {"left", "right"}:
        margin = _side_peak_scan_margin(height)
        default_start = y1 + margin
        default_end = y2 - margin

        start = default_start if scan_start is None else int(round(scan_start))
        end = default_end if scan_end is None else int(round(scan_end))

        start = max(y1, min(y2, start))
        end = max(y1, min(y2, end))

        if end < start:
            start, end = y1, y2

        coords = list(range(start, end + 1))
        if not coords:
            coords = [int(round((y1 + y2) / 2))]

        scores = []
        for y in coords:
            if relative_position == "left":
                score = img_count_foreground_pixels(
                    binary,
                    x1 - SIDE_PEAK_OUT_LEN,
                    y - halfspan,
                    x1 + SIDE_PEAK_INSET + 1,
                    y + halfspan + 1
                )
            else:
                score = img_count_foreground_pixels(
                    binary,
                    x2 - SIDE_PEAK_INSET,
                    y - halfspan,
                    x2 + SIDE_PEAK_OUT_LEN + 1,
                    y + halfspan + 1
                )
            scores.append(score)

        if center_coord is None:
            center_coord = int(round((start + end) / 2))
        center_index = min(range(len(coords)), key=lambda i: abs(coords[i] - center_coord))
        best_index, peak_info = _select_peak_index_from_scores(scores, center_index)
        best_y = coords[best_index]

        point = [
            round(float(x1 - TERMINAL_OUTWARD_OFFSET if relative_position == "left" else x2 + TERMINAL_OUTWARD_OFFSET), 2),
            round(float(best_y), 2)
        ]

        debug_info = {
            "point_mode": "side_peak_outside",
            "scan_axis": "y",
            "relative_position": relative_position,
            "scan_start": start,
            "scan_end": end,
            "scan_margin": margin,
            "probe_halfspan": halfspan,
            "probe_out_len": SIDE_PEAK_OUT_LEN,
            "probe_inset": SIDE_PEAK_INSET,
            "peak_coord": best_y,
            "anchor_offset_ratio": round((best_y - y1) / max(height, 1), 4),
            **peak_info,
        }
        return point, debug_info

    raise ValueError(f"relative_position non supportata: {relative_position}")

# =========================================================
# THREE-TERMINAL GEOMETRY
# =========================================================
def _three_terminal_pair_scan_window(x1, y1, x2, y2, orientation, same_side=False):
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)

    def xr(r):
        return x1 + r * width

    def yr(r):
        return y1 + r * height

    # same_side=False  -> comportamento attuale
    # same_side=True   -> versione specchiata

    if orientation == "left":
        if not same_side:
            return xr(THREE_TERMINAL_OPPOSITE_NEAR_RATIO), xr(THREE_TERMINAL_OPPOSITE_FAR_RATIO)
        return xr(1.0 - THREE_TERMINAL_OPPOSITE_FAR_RATIO), xr(1.0 - THREE_TERMINAL_OPPOSITE_NEAR_RATIO)

    if orientation == "right":
        if not same_side:
            return xr(1.0 - THREE_TERMINAL_OPPOSITE_FAR_RATIO), xr(1.0 - THREE_TERMINAL_OPPOSITE_NEAR_RATIO)
        return xr(THREE_TERMINAL_OPPOSITE_NEAR_RATIO), xr(THREE_TERMINAL_OPPOSITE_FAR_RATIO)

    if orientation == "top":
        if not same_side:
            return yr(THREE_TERMINAL_OPPOSITE_NEAR_RATIO), yr(THREE_TERMINAL_OPPOSITE_FAR_RATIO)
        return yr(1.0 - THREE_TERMINAL_OPPOSITE_FAR_RATIO), yr(1.0 - THREE_TERMINAL_OPPOSITE_NEAR_RATIO)

    if orientation == "bottom":
        if not same_side:
            return yr(1.0 - THREE_TERMINAL_OPPOSITE_FAR_RATIO), yr(1.0 - THREE_TERMINAL_OPPOSITE_NEAR_RATIO)
        return yr(THREE_TERMINAL_OPPOSITE_NEAR_RATIO), yr(THREE_TERMINAL_OPPOSITE_FAR_RATIO)

    raise ValueError(f"orientation non supportata: {orientation}")

def _resolve_three_terminal_pair_bias(binary, bbox, orientation):
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)

    pair_positions = ("top", "bottom") if orientation in {"left", "right"} else ("left", "right")

    def score_candidate(same_side):
        total = 0.0
        debug = {}

        for rel_pos in pair_positions:
            scan_start, scan_end = _three_terminal_pair_scan_window(
                x1, y1, x2, y2,
                orientation=orientation,
                same_side=same_side,
            )
            center_coord = int(round((scan_start + scan_end) / 2))

            _, term_debug = geom_terminal_point_by_side_peak(
                binary,
                (x1, y1, x2, y2),
                rel_pos,
                scan_start=scan_start,
                scan_end=scan_end,
                center_coord=center_coord,
            )

            local_score = (
                float(term_debug.get("selected_run_score", 0.0)) +
                0.25 * float(term_debug.get("max_score", 0.0))
            )
            total += local_score
            debug[rel_pos] = {
                "local_score": local_score,
                **term_debug,
            }

        return total, debug

    opposite_score, opposite_debug = score_candidate(same_side=False)
    same_score, same_debug = score_candidate(same_side=True)

    if same_score > opposite_score * 1.05:
        return "same_side", same_debug

    return "opposite_side", opposite_debug

def geom_terminal_point_three_terminal(binary, bbox, orientation: str, relative_position: str):
    """
    Localizzazione specifica per Mosfet / NPN.

    Idea chiave:
    - orientation rappresenta il lato "singolo" del componente (gate/base)
    - gli altri due terminali stanno sull'asse ortogonale
    - questi due terminali sono di solito verso il lato opposto al terminale singolo

    Esempi:
    - orientation = "left"  -> terminale singolo a sinistra, gli altri su top/bottom ma
                               cercati verso destra
    - orientation = "right" -> terminale singolo a destra, gli altri su top/bottom ma
                               cercati verso sinistra
    - orientation = "top"   -> terminale singolo in alto, gli altri su left/right ma
                               cercati verso il basso
    - orientation = "bottom"-> terminale singolo in basso, gli altri su left/right ma
                               cercati verso l'alto
    """
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)

    def x_from_ratio(r):
        return x1 + r * width

    def y_from_ratio(r):
        return y1 + r * height

    # -------------------------------------------------
    # 1) Terminale singolo: cerca in banda centrale
    # -------------------------------------------------
    if relative_position == orientation:
        if relative_position in {"top", "bottom"}:
            scan_start = x_from_ratio(THREE_TERMINAL_SINGLE_SCAN_START_RATIO)
            scan_end = x_from_ratio(THREE_TERMINAL_SINGLE_SCAN_END_RATIO)
            center_coord = int(round((scan_start + scan_end) / 2))
        else:
            scan_start = y_from_ratio(THREE_TERMINAL_SINGLE_SCAN_START_RATIO)
            scan_end = y_from_ratio(THREE_TERMINAL_SINGLE_SCAN_END_RATIO)
            center_coord = int(round((scan_start + scan_end) / 2))

        point, debug = geom_terminal_point_by_side_peak(
            binary,
            bbox,
            relative_position,
            scan_start=scan_start,
            scan_end=scan_end,
            center_coord=center_coord
        )
        debug["point_mode"] = "three_terminal_structured"
        debug["three_terminal_role"] = "single_side_terminal"
        debug["three_terminal_orientation"] = orientation
        return point, debug
    
    pair_bias, pair_bias_debug = _resolve_three_terminal_pair_bias(
        binary,
        (x1, y1, x2, y2),
        orientation,
    )
    same_side = (pair_bias == "same_side")

    if orientation in {"left", "right"} and relative_position in {"top", "bottom"}:
        scan_start, scan_end = _three_terminal_pair_scan_window(
            x1, y1, x2, y2,
            orientation=orientation,
            same_side=same_side,
        )
        center_coord = int(round((scan_start + scan_end) / 2))

    elif orientation in {"top", "bottom"} and relative_position in {"left", "right"}:
        scan_start, scan_end = _three_terminal_pair_scan_window(
            x1, y1, x2, y2,
            orientation=orientation,
            same_side=same_side,
        )
        center_coord = int(round((scan_start + scan_end) / 2))

    else:
        point, debug = geom_terminal_point_by_side_peak(binary, bbox, relative_position)
        debug["point_mode"] = "three_terminal_structured_fallback"
        debug["three_terminal_role"] = "fallback"
        debug["three_terminal_orientation"] = orientation
        return point, debug

    point, debug = geom_terminal_point_by_side_peak(
        binary,
        bbox,
        relative_position,
        scan_start=scan_start,
        scan_end=scan_end,
        center_coord=center_coord
    )
    debug["point_mode"] = "three_terminal_structured"
    debug["three_terminal_role"] = "orthogonal_pair_terminal"
    debug["three_terminal_orientation"] = orientation
    debug["three_terminal_pair_bias"] = pair_bias
    debug["three_terminal_pair_bias_debug"] = pair_bias_debug
    return point, debug


# =========================================================
# OPAMP - LOW LEVEL HELPERS
# =========================================================
def _opamp_count_horizontal_line(binary, x_start, x_end, y):
    h, w = binary.shape[:2]
    y = max(0, min(h - 1, int(round(y))))

    xa = int(round(min(x_start, x_end)))
    xb = int(round(max(x_start, x_end)))

    xa = max(0, min(w, xa))
    xb = max(0, min(w, xb))

    if xb <= xa:
        return 0

    return img_count_foreground_pixels(binary, xa, y, xb, y + 1)


def _opamp_count_vertical_line(binary, x, y_start, y_end):
    h, w = binary.shape[:2]
    x = max(0, min(w - 1, int(round(x))))

    ya = int(round(min(y_start, y_end)))
    yb = int(round(max(y_start, y_end)))

    ya = max(0, min(h, ya))
    yb = max(0, min(h, yb))

    if yb <= ya:
        return 0

    return img_count_foreground_pixels(binary, x, ya, x + 1, yb)


def _select_opamp_mandatory_best_index(scores, coords, center_coord):
    if not scores:
        return 0, {
            "max_score": 0,
            "keep_threshold": 0,
            "selected_coord": None,
            "selected_distance_to_center": None,
            "kept_candidates": 0,
        }

    max_score = max(scores)
    keep_threshold = max_score * OPAMP_MANDATORY_KEEP_RATIO
    kept = [i for i, s in enumerate(scores) if s >= keep_threshold]

    if not kept:
        best_idx = max(range(len(scores)), key=lambda i: scores[i])
    else:
        best_idx = min(
            kept,
            key=lambda i: (abs(coords[i] - center_coord), -scores[i])
        )

    return best_idx, {
        "max_score": round(float(max_score), 4),
        "keep_threshold": round(float(keep_threshold), 4),
        "selected_coord": coords[best_idx],
        "selected_distance_to_center": int(abs(coords[best_idx] - center_coord)),
        "kept_candidates": len(kept),
    }

def _opamp_slot_scan_range(x1, y1, x2, y2, relative_position: str, slot: str):
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)

    if relative_position in {"left", "right"}:
        if slot == "upper":
            start = y1 + OPAMP_SLOT_UPPER_START_RATIO * height
            end = y1 + OPAMP_SLOT_UPPER_END_RATIO * height
        elif slot == "lower":
            start = y1 + OPAMP_SLOT_LOWER_START_RATIO * height
            end = y1 + OPAMP_SLOT_LOWER_END_RATIO * height
        else:
            start = y1 + OPAMP_SLOT_CENTER_START_RATIO * height
            end = y1 + OPAMP_SLOT_CENTER_END_RATIO * height

        center_coord = int(round((start + end) / 2))
        return start, end, center_coord

    if relative_position in {"top", "bottom"}:
        if slot == "left":
            start = x1 + OPAMP_SLOT_LEFT_START_RATIO * width
            end = x1 + OPAMP_SLOT_LEFT_END_RATIO * width
        elif slot == "right":
            start = x1 + OPAMP_SLOT_RIGHT_START_RATIO * width
            end = x1 + OPAMP_SLOT_RIGHT_END_RATIO * width
        else:
            start = x1 + OPAMP_SLOT_CENTER_START_RATIO * width
            end = x1 + OPAMP_SLOT_CENTER_END_RATIO * width

        center_coord = int(round((start + end) / 2))
        return start, end, center_coord

    raise ValueError(f"relative_position non supportata per opamp: {relative_position}")

# =========================================================
# OPAMP - MANDATORY TERMINALS
# =========================================================
def _opamp_mandatory_probe_score(binary, bbox, relative_position: str, coord: int):
    """
    Score 1D per i 3 terminali obbligatori dell'opamp.

    Obiettivo:
    - leggere soprattutto il filo ESTERNO al bbox
    - usare il bordo come conferma leggera
    - non leggere quasi per niente la grafica interna dell'opamp

    Così numeri e simboli interni (+, -, 1, 2, 3, 4, 5) disturbano molto meno.
    """
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)

    if relative_position == "left":
        ys = range(coord - OPAMP_MANDATORY_ROW_TOL, coord + OPAMP_MANDATORY_ROW_TOL + 1)

        near = max(
            _opamp_count_horizontal_line(binary, x1 - OPAMP_MANDATORY_OUTWARD_LEN, x1, y)
            for y in ys
        )
        far = max(
            _opamp_count_horizontal_line(
                binary,
                x1 - OPAMP_MANDATORY_OUTWARD_LEN - OPAMP_MANDATORY_FAR_GAP - OPAMP_MANDATORY_FAR_LEN,
                x1 - OPAMP_MANDATORY_OUTWARD_LEN - OPAMP_MANDATORY_FAR_GAP,
                y,
            )
            for y in ys
        )
        border = max(
            _opamp_count_horizontal_line(binary, x1 - 1, x1 + 2, y)
            for y in ys
        )

        return near + OPAMP_MANDATORY_FAR_WEIGHT * far + OPAMP_MANDATORY_BORDER_WEIGHT * border

    if relative_position == "right":
        ys = range(coord - OPAMP_MANDATORY_ROW_TOL, coord + OPAMP_MANDATORY_ROW_TOL + 1)

        near = max(
            _opamp_count_horizontal_line(binary, x2 + 1, x2 + OPAMP_MANDATORY_OUTWARD_LEN + 1, y)
            for y in ys
        )
        far = max(
            _opamp_count_horizontal_line(
                binary,
                x2 + OPAMP_MANDATORY_OUTWARD_LEN + OPAMP_MANDATORY_FAR_GAP,
                x2 + OPAMP_MANDATORY_OUTWARD_LEN + OPAMP_MANDATORY_FAR_GAP + OPAMP_MANDATORY_FAR_LEN + 1,
                y,
            )
            for y in ys
        )
        border = max(
            _opamp_count_horizontal_line(binary, x2 - 1, x2 + 2, y)
            for y in ys
        )

        return near + OPAMP_MANDATORY_FAR_WEIGHT * far + OPAMP_MANDATORY_BORDER_WEIGHT * border

    if relative_position == "top":
        xs = range(coord - OPAMP_MANDATORY_ROW_TOL, coord + OPAMP_MANDATORY_ROW_TOL + 1)

        near = max(
            _opamp_count_vertical_line(binary, x, y1 - OPAMP_MANDATORY_OUTWARD_LEN, y1)
            for x in xs
        )
        far = max(
            _opamp_count_vertical_line(
                binary,
                x,
                y1 - OPAMP_MANDATORY_OUTWARD_LEN - OPAMP_MANDATORY_FAR_GAP - OPAMP_MANDATORY_FAR_LEN,
                y1 - OPAMP_MANDATORY_OUTWARD_LEN - OPAMP_MANDATORY_FAR_GAP,
            )
            for x in xs
        )
        border = max(
            _opamp_count_vertical_line(binary, x, y1 - 1, y1 + 2)
            for x in xs
        )

        return near + OPAMP_MANDATORY_FAR_WEIGHT * far + OPAMP_MANDATORY_BORDER_WEIGHT * border

    if relative_position == "bottom":
        xs = range(coord - OPAMP_MANDATORY_ROW_TOL, coord + OPAMP_MANDATORY_ROW_TOL + 1)

        near = max(
            _opamp_count_vertical_line(binary, x, y2 + 1, y2 + OPAMP_MANDATORY_OUTWARD_LEN + 1)
            for x in xs
        )
        far = max(
            _opamp_count_vertical_line(
                binary,
                x,
                y2 + OPAMP_MANDATORY_OUTWARD_LEN + OPAMP_MANDATORY_FAR_GAP,
                y2 + OPAMP_MANDATORY_OUTWARD_LEN + OPAMP_MANDATORY_FAR_GAP + OPAMP_MANDATORY_FAR_LEN + 1,
            )
            for x in xs
        )
        border = max(
            _opamp_count_vertical_line(binary, x, y2 - 1, y2 + 2)
            for x in xs
        )

        return near + OPAMP_MANDATORY_FAR_WEIGHT * far + OPAMP_MANDATORY_BORDER_WEIGHT * border

    raise ValueError(f"relative_position non supportata per opamp mandatory: {relative_position}")


def _geom_opamp_mandatory_terminal(binary, bbox, relative_position: str, slot: str):
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)
    scan_start, scan_end, center_coord = _opamp_slot_scan_range(x1, y1, x2, y2, relative_position, slot)
    halfspan = OPAMP_MANDATORY_SCAN_HALFSPAN

    if relative_position in {"left", "right"}:
        start = max(y1, min(y2, int(round(scan_start))))
        end = max(y1, min(y2, int(round(scan_end))))
        if end < start:
            start, end = y1, y2
        coords = list(range(start, end + 1)) or [int(round((y1 + y2) / 2))]

        scores = [
            _opamp_mandatory_probe_score(binary, bbox, relative_position, y)
            for y in coords
        ]
        best_index, peak_info = _select_opamp_mandatory_best_index(scores, coords, center_coord)
        best_coord = coords[best_index]

        x = float(x1 - OPAMP_MANDATORY_OUTWARD_OFFSET if relative_position == "left" else x2 + OPAMP_MANDATORY_OUTWARD_OFFSET)
        y = float(best_coord)
        point = (x, y)
        debug = {
            "point_mode": "opamp_mandatory_wire_probe",
            "relative_position": relative_position,
            "scan_axis": "y",
            "scan_start": start,
            "scan_end": end,
            "probe_halfspan": halfspan,
            "probe_outward_len": OPAMP_MANDATORY_OUTWARD_LEN,
            "probe_inward_len": OPAMP_MANDATORY_INWARD_LEN,
            "probe_far_gap": OPAMP_MANDATORY_FAR_GAP,
            "probe_far_len": OPAMP_MANDATORY_FAR_LEN,
            "peak_coord": best_coord,
            "raw_scores_max": round(float(max(scores) if scores else 0.0), 4),
            **peak_info,
        }
        return point, debug

    if relative_position in {"top", "bottom"}:
        start = max(x1, min(x2, int(round(scan_start))))
        end = max(x1, min(x2, int(round(scan_end))))
        if end < start:
            start, end = x1, x2
        coords = list(range(start, end + 1)) or [int(round((x1 + x2) / 2))]

        scores = [
            _opamp_mandatory_probe_score(binary, bbox, relative_position, x)
            for x in coords
        ]
        best_index, peak_info = _select_opamp_mandatory_best_index(scores, coords, center_coord)
        best_coord = coords[best_index]

        x = float(best_coord)
        y = float(y1 - OPAMP_MANDATORY_OUTWARD_OFFSET if relative_position == "top" else y2 + OPAMP_MANDATORY_OUTWARD_OFFSET)
        point = (x, y)
        debug = {
            "point_mode": "opamp_mandatory_wire_probe",
            "relative_position": relative_position,
            "scan_axis": "x",
            "scan_start": start,
            "scan_end": end,
            "probe_halfspan": halfspan,
            "probe_outward_len": OPAMP_MANDATORY_OUTWARD_LEN,
            "probe_inward_len": OPAMP_MANDATORY_INWARD_LEN,
            "probe_far_gap": OPAMP_MANDATORY_FAR_GAP,
            "probe_far_len": OPAMP_MANDATORY_FAR_LEN,
            "peak_coord": best_coord,
            "raw_scores_max": round(float(max(scores) if scores else 0.0), 4),
            **peak_info,
        }
        return point, debug

    raise ValueError(f"relative_position non supportata per opamp mandatory: {relative_position}")

# =========================================================
# OPAMP - AUXILIARY TERMINALS
# =========================================================
def _opamp_aux_scan_x_range(bbox):
    x1, y1, x2, y2 = bbox
    width = max(x2 - x1, 1)
    start = x1 + int(round(OPAMP_AUX_SCAN_X_START_RATIO * width))
    end = x1 + int(round(OPAMP_AUX_SCAN_X_END_RATIO * width))
    if end < start:
        start, end = start, start
    return start, end


def _opamp_vertical_run_from_edge(binary, bbox, x, side):
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)
    height = max(y2 - y1, 1)

    halfspan = OPAMP_AUX_RUN_HALFSPAN
    min_fg = OPAMP_AUX_RUN_MIN_FG
    max_gap = OPAMP_AUX_RUN_MAX_GAP
    max_depth = int(round(OPAMP_AUX_RUN_MAX_DEPTH_RATIO * height))
    edge_band = max(2, int(round(OPAMP_AUX_EDGE_BAND_RATIO * height)))

    def row_fg(y):
        return img_count_foreground_pixels(
            binary,
            x - halfspan,
            y,
            x + halfspan + 1,
            y + 1,
        )

    if side == "top":
        start_candidates = [
            y for y in range(y1, min(y2, y1 + edge_band) + 1)
            if row_fg(y) >= min_fg
        ]
        if not start_candidates:
            return None

        run_start = start_candidates[0]
        run_end = run_start
        gaps = 0

        stop_y = min(y2, y1 + max_depth)
        for y in range(run_start + 1, stop_y + 1):
            if row_fg(y) >= min_fg:
                run_end = y
                gaps = 0
            else:
                gaps += 1
                if gaps > max_gap:
                    break

        return {
            "run_start": run_start,
            "run_end": run_end,
            "run_len": int(run_end - run_start + 1),
            "side": side,
        }

    if side == "bottom":
        start_candidates = [
            y for y in range(y2, max(y1, y2 - edge_band) - 1, -1)
            if row_fg(y) >= min_fg
        ]
        if not start_candidates:
            return None

        run_start = start_candidates[0]
        run_end = run_start
        gaps = 0

        stop_y = max(y1, y2 - max_depth)
        for y in range(run_start - 1, stop_y - 1, -1):
            if row_fg(y) >= min_fg:
                run_end = y
                gaps = 0
            else:
                gaps += 1
                if gaps > max_gap:
                    break

        return {
            "run_start": run_start,
            "run_end": run_end,
            "run_len": int(run_start - run_end + 1),
            "side": side,
        }

    return None

def _opamp_diagonal_support(binary, x, y, diag_kind, radius=4):
    """
    Conta quanto supporto c'è attorno al punto (x, y) lungo la diagonale corretta
    del triangolo dell'opamp.
    """
    h, w = binary.shape[:2]

    def sample(offset):
        cnt = 0
        for k in range(-radius, radius + 1):
            xx = x + k
            if diag_kind == "down_right":
                yy = y + k + offset
            else:
                yy = y - k + offset

            if 0 <= xx < w and 0 <= yy < h and binary[yy, xx] > 0:
                cnt += 1
        return cnt

    return max(sample(-1), sample(0), sample(1))


def _opamp_aux_segment_density(binary, x, y1, y2, side, y, halfspan=1):
    """
    Densità del ramo verticale tra il bordo esterno dell'opamp e il punto candidato.
    Serve per evitare di scegliere punti sulla diagonale dove però non c'è davvero
    continuità del ramo verticale.
    """
    h, w = binary.shape[:2]
    xa = max(0, x - halfspan)
    xb = min(w, x + halfspan + 1)

    if side == "top":
        ya = max(0, min(h - 1, y1))
        yb = max(0, min(h - 1, y))
    else:
        ya = max(0, min(h - 1, y))
        yb = max(0, min(h - 1, y2))

    if yb < ya:
        ya, yb = yb, ya

    pixel_count = img_count_foreground_pixels(binary, xa, ya, xb, yb + 1)
    area = max(1, (xb - xa) * (yb - ya + 1))
    return float(pixel_count) / float(area)


def _opamp_refine_aux_y_to_diagonal(binary, bbox, orientation, relative_position, x, base_y):
    """
    Raffina SOLO la y del punto aux.

    Strategia nuova:
    - scorriamo dal bordo esterno verso l'interno
    - prendiamo il PRIMO punto valido che sembra davvero il giunto
    - solo se non troviamo nulla facciamo fallback al best globale

    Questo evita che i numeri interni (4, 5) vincano sul vero incrocio.
    """
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)
    height = max(y2 - y1, 1)

    if orientation == "right":
        diag_kind = "down_right" if relative_position == "top" else "up_right"
    else:
        diag_kind = "up_right" if relative_position == "top" else "down_right"

    if relative_position == "top":
        search_start = max(
            int(round(base_y)),
            y1 + int(round(OPAMP_AUX_REFINE_TOP_START_RATIO * height)),
        )
        search_end = min(
            y2,
            y1 + int(round(OPAMP_AUX_REFINE_TOP_END_RATIO * height)),
        )
        ys = list(range(search_start, search_end + 1))   # dall'alto verso il basso
    else:
        search_start = max(
            y1,
            y1 + int(round(OPAMP_AUX_REFINE_BOTTOM_START_RATIO * height)),
        )
        search_end = min(
            int(round(base_y)),
            y1 + int(round(OPAMP_AUX_REFINE_BOTTOM_END_RATIO * height)),
        )
        ys = list(range(search_end, search_start - 1, -1))  # dal basso verso l'alto

    if not ys:
        return float(base_y), {
            "refined": False,
            "refined_y": float(base_y),
            "refined_diag_support": 0,
            "segment_density": 0.0,
            "refine_mode": "empty_search",
        }

    # ---------------------------------------------------------
    # 1) FIRST-HIT: primo giunto plausibile dal bordo verso dentro
    # ---------------------------------------------------------
    first_valid = None

    for y in ys:
        diag_support = _opamp_diagonal_support(
            binary,
            int(round(x)),
            int(round(y)),
            diag_kind=diag_kind,
            radius=OPAMP_AUX_DIAG_RADIUS,
        )
        segment_density = _opamp_aux_segment_density(
            binary,
            int(round(x)),
            y1,
            y2,
            relative_position,
            int(round(y)),
            halfspan=1,
        )

        if (
            diag_support >= OPAMP_AUX_REFINE_MIN_DIAG_SUPPORT
            and segment_density >= OPAMP_AUX_REFINE_MIN_SEGMENT_DENSITY
        ):
            first_valid = {
                "y": float(y),
                "diag_support": int(diag_support),
                "segment_density": float(segment_density),
            }
            break

    if first_valid is not None:
        return first_valid["y"], {
            "refined": first_valid["y"] != float(base_y),
            "refined_y": first_valid["y"],
            "refined_diag_support": first_valid["diag_support"],
            "segment_density": round(first_valid["segment_density"], 4),
            "refine_mode": "first_valid_from_edge",
        }

    # ---------------------------------------------------------
    # 2) FALLBACK: se non troviamo nessun primo giunto valido,
    #    usiamo il best globale come prima
    # ---------------------------------------------------------
    best = None
    for y in ys:
        diag_support = _opamp_diagonal_support(
            binary,
            int(round(x)),
            int(round(y)),
            diag_kind=diag_kind,
            radius=OPAMP_AUX_DIAG_RADIUS,
        )
        segment_density = _opamp_aux_segment_density(
            binary,
            int(round(x)),
            y1,
            y2,
            relative_position,
            int(round(y)),
            halfspan=1,
        )

        if relative_position == "top":
            tie_break = y
        else:
            tie_break = -y

        key = (
            diag_support >= OPAMP_AUX_REFINE_MIN_DIAG_SUPPORT,
            segment_density >= OPAMP_AUX_REFINE_MIN_SEGMENT_DENSITY,
            diag_support,
            segment_density,
            tie_break,
        )

        if best is None or key > best["key"]:
            best = {
                "key": key,
                "y": float(y),
                "diag_support": int(diag_support),
                "segment_density": float(segment_density),
            }

    return best["y"], {
        "refined": best["y"] != float(base_y),
        "refined_y": best["y"],
        "refined_diag_support": best["diag_support"],
        "segment_density": round(best["segment_density"], 4),
        "refine_mode": "best_global_fallback",
    }

def _opamp_vertical_band_density(binary, x, y_start, y_end, halfspan=1):
    h, w = binary.shape[:2]
    xa = max(0, int(round(x)) - halfspan)
    xb = min(w, int(round(x)) + halfspan + 1)

    ya = max(0, min(h - 1, int(round(min(y_start, y_end)))))
    yb = max(0, min(h - 1, int(round(max(y_start, y_end)))))

    if yb < ya:
        ya, yb = yb, ya

    pixel_count = img_count_foreground_pixels(binary, xa, ya, xb, yb + 1)
    area = max(1, (xb - xa) * (yb - ya + 1))
    return float(pixel_count) / float(area)


def _opamp_aux_make_refine_binary(binary, bbox, orientation):
    """
    Restituisce una copia locale del binary in cui i numeri interni
    dell'opamp (tipicamente 4 e 5) sono mascherati.

    La maschera viene usata SOLO per la refine degli auxiliary.
    """
    if not OPAMP_AUX_MASK_INTERNAL_LABELS:
        return binary, {
            "internal_label_masked": False,
        }

    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)

    # Per ora la usiamo solo sugli opamp orizzontali
    if orientation not in {"right", "left"}:
        return binary, {
            "internal_label_masked": False,
            "mask_orientation_supported": False,
        }

    masked = binary.copy()

    def xr(r):
        return x1 + int(round(r * width))

    def yr(r):
        return y1 + int(round(r * height))

    def mirrored_x_interval(r1, r2):
        if orientation == "right":
            xa = xr(r1)
            xb = xr(r2)
        else:
            # mirror orizzontale per opamp "left"
            xa = xr(1.0 - r2)
            xb = xr(1.0 - r1)

        if xb < xa:
            xa, xb = xb, xa
        return xa, xb

    mask_x1, mask_x2 = mirrored_x_interval(
        OPAMP_AUX_MASK_X1_RATIO,
        OPAMP_AUX_MASK_X2_RATIO,
    )

    top_y1 = yr(OPAMP_AUX_MASK_TOP_Y1_RATIO)
    top_y2 = yr(OPAMP_AUX_MASK_TOP_Y2_RATIO)

    bottom_y1 = yr(OPAMP_AUX_MASK_BOTTOM_Y1_RATIO)
    bottom_y2 = yr(OPAMP_AUX_MASK_BOTTOM_Y2_RATIO)

    # clamp
    mask_x1 = max(0, min(binary.shape[1] - 1, mask_x1))
    mask_x2 = max(0, min(binary.shape[1] - 1, mask_x2))
    top_y1 = max(0, min(binary.shape[0] - 1, top_y1))
    top_y2 = max(0, min(binary.shape[0] - 1, top_y2))
    bottom_y1 = max(0, min(binary.shape[0] - 1, bottom_y1))
    bottom_y2 = max(0, min(binary.shape[0] - 1, bottom_y2))

    if mask_x2 >= mask_x1 and top_y2 >= top_y1:
        masked[top_y1:top_y2 + 1, mask_x1:mask_x2 + 1] = 0

    if mask_x2 >= mask_x1 and bottom_y2 >= bottom_y1:
        masked[bottom_y1:bottom_y2 + 1, mask_x1:mask_x2 + 1] = 0

    return masked, {
        "internal_label_masked": True,
        "mask_x1": int(mask_x1),
        "mask_x2": int(mask_x2),
        "mask_top_y1": int(top_y1),
        "mask_top_y2": int(top_y2),
        "mask_bottom_y1": int(bottom_y1),
        "mask_bottom_y2": int(bottom_y2),
        "mask_orientation_supported": True,
    }

def _geom_opamp_aux_terminal_v1(binary, bbox, orientation, relative_position):
    """
    V1:
    - solo opamp orizzontali
    - cerca un ramo verticale connesso al bordo top/bottom
    - il punto finale è la fine della run
    """
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)

    if orientation not in {"right", "left"} or relative_position not in {"top", "bottom"}:
        point = geom_terminal_point_from_bbox(bbox, relative_position)
        return point, {
            "point_mode": "opamp_aux_v1",
            "aux_detected": False,
            "orientation_supported": False,
            "relative_position": relative_position,
        }

    scan_start, scan_end = _opamp_aux_scan_x_range((x1, y1, x2, y2))
    xs = list(range(max(x1, scan_start), min(x2, scan_end) + 1))
    if not xs:
        xs = [int(round((x1 + x2) / 2))]

    candidates = []

    for x in xs:
        run = _opamp_vertical_run_from_edge(
            binary,
            (x1, y1, x2, y2),
            x,
            relative_position,
        )
        if run is None:
            continue

        candidates.append({
            "x": float(x),
            **run,
        })

    if not candidates:
        point = geom_terminal_point_from_bbox(bbox, relative_position)
        return point, {
            "point_mode": "opamp_aux_v1",
            "aux_detected": False,
            "orientation_supported": True,
            "relative_position": relative_position,
            "scan_start": scan_start,
            "scan_end": scan_end,
            "min_run_length": OPAMP_AUX_MIN_RUN_LENGTH,
            "aux_reason": "no_vertical_run_candidates",
        }

    max_run_len = max(c["run_len"] for c in candidates)
    keep_threshold = max(
        OPAMP_AUX_MIN_RUN_LENGTH,
        int(round(max_run_len * OPAMP_AUX_RUN_KEEP_RATIO)),
    )

    kept = [c for c in candidates if c["run_len"] >= keep_threshold]

    if not kept:
        kept = candidates

    if orientation == "right":
        # scegli il ramo più interno: più a sinistra
        best = min(kept, key=lambda c: c["x"])
    else:
        # opamp left: simmetrico, più a destra
        best = max(kept, key=lambda c: c["x"])

    if best is None or best["run_len"] < OPAMP_AUX_MIN_RUN_LENGTH:
        point = geom_terminal_point_from_bbox(bbox, relative_position)
        return point, {
            "point_mode": "opamp_aux_v1",
            "aux_detected": False,
            "orientation_supported": True,
            "relative_position": relative_position,
            "scan_start": scan_start,
            "scan_end": scan_end,
            "min_run_length": OPAMP_AUX_MIN_RUN_LENGTH,
        }

    base_x = float(best["x"])
    base_y = float(best["run_end"])

    refine_binary, mask_debug = _opamp_aux_make_refine_binary(
        binary,
        (x1, y1, x2, y2),
        orientation,
    )

    # Per gli aux teniamo la x dello stelo trovata dalla run verticale.
    # La refine della x stava spostando il punto fuori dallo stelo.
    refined_x = float(base_x)
    x_refine_debug = {
        "x_refined": False,
        "refined_x": float(base_x),
        "x_refine_mode": "disabled_trust_run_axis",
    }

    refined_y, y_refine_debug = _opamp_refine_aux_y_to_diagonal(
        refine_binary,
        (x1, y1, x2, y2),
        orientation,
        relative_position,
        refined_x,
        base_y,
    )

    point = (float(refined_x), float(refined_y))

    return point, {
        "point_mode": "opamp_aux_v1",
        "aux_detected": True,
        "orientation_supported": True,
        "relative_position": relative_position,
        "scan_start": scan_start,
        "scan_end": scan_end,
        "candidate_x": best["x"],
        "run_start": best["run_start"],
        "run_end": best["run_end"],
        "run_len": best["run_len"],
        "min_run_length": OPAMP_AUX_MIN_RUN_LENGTH,
        "base_x": base_x,
        "base_y": base_y,
        **mask_debug,
        **x_refine_debug,
        **y_refine_debug,
    }

# =========================================================
# OPAMP - PUBLIC API
# =========================================================
def geom_terminal_point_opamp(binary, bbox, orientation: str, term_def: dict):
    """
    Nuova strategia semplificata per l'opamp.

    In questa fase gestiamo BENE solo i 3 terminali obbligatori:
    - in1
    - in2
    - out

    Gli auxiliary vengono volutamente ignorati a livello di strategia e potranno
    essere reintrodotti in una seconda fase separata.
    """
    relative_position = term_def["relative_position"]
    slot = term_def.get("slot", "center")
    terminal_role = term_def.get("terminal_role")

    if terminal_role == "auxiliary":
        point, debug = _geom_opamp_aux_terminal_v1(
            binary,
            bbox,
            orientation,
            relative_position,
        )
        debug["opamp_orientation"] = orientation
        debug["opamp_terminal_name"] = term_def.get("name")
        debug["opamp_terminal_role"] = terminal_role
        debug["opamp_slot"] = slot
        return point, debug

    point, debug = _geom_opamp_mandatory_terminal(
        binary,
        bbox,
        relative_position,
        slot,
    )
    debug["opamp_orientation"] = orientation
    debug["opamp_terminal_name"] = term_def.get("name")
    debug["opamp_terminal_role"] = terminal_role
    debug["opamp_slot"] = slot
    return point, debug



