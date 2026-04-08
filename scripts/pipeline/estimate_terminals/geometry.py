from .config import *
from .image_ops import img_count_foreground_pixels
# =========================================================
# GEOMETRY / IMAGE HELPERS
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

    # -------------------------------------------------
    # 2) Terminali della coppia opposta: cerca verso il lato opposto
    # -------------------------------------------------
    if orientation == "left" and relative_position in {"top", "bottom"}:
        scan_start = x_from_ratio(THREE_TERMINAL_OPPOSITE_NEAR_RATIO)
        scan_end = x_from_ratio(THREE_TERMINAL_OPPOSITE_FAR_RATIO)
        center_coord = int(round((scan_start + scan_end) / 2))
    elif orientation == "right" and relative_position in {"top", "bottom"}:
        scan_start = x_from_ratio(1.0 - THREE_TERMINAL_OPPOSITE_FAR_RATIO)
        scan_end = x_from_ratio(1.0 - THREE_TERMINAL_OPPOSITE_NEAR_RATIO)
        center_coord = int(round((scan_start + scan_end) / 2))
    elif orientation == "top" and relative_position in {"left", "right"}:
        scan_start = y_from_ratio(THREE_TERMINAL_OPPOSITE_NEAR_RATIO)
        scan_end = y_from_ratio(THREE_TERMINAL_OPPOSITE_FAR_RATIO)
        center_coord = int(round((scan_start + scan_end) / 2))
    elif orientation == "bottom" and relative_position in {"left", "right"}:
        scan_start = y_from_ratio(1.0 - THREE_TERMINAL_OPPOSITE_FAR_RATIO)
        scan_end = y_from_ratio(1.0 - THREE_TERMINAL_OPPOSITE_NEAR_RATIO)
        center_coord = int(round((scan_start + scan_end) / 2))
    else:
        # Caso incoerente o inatteso: fallback alla side_peak standard.
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
    return point, debug

def score_point_local_support(binary, x, y, radius=MOSFET_POINT_SUPPORT_RADIUS):
    """
    Misura quanta evidenza di foreground/wire c'è attorno a un punto terminale stimato.
    """
    xi = int(round(x))
    yi = int(round(y))
    return img_count_foreground_pixels(
        binary,
        xi - radius,
        yi - radius,
        xi + radius + 1,
        yi + radius + 1
    )

def score_point_directional_support(
    binary,
    x,
    y,
    relative_position,
    outward=10,
    inward=2,
    halfspan=3,
):
    xi = int(round(x))
    yi = int(round(y))

    if relative_position == "left":
        return img_count_foreground_pixels(
            binary,
            xi - outward,
            yi - halfspan,
            xi + inward + 1,
            yi + halfspan + 1
        )

    if relative_position == "right":
        return img_count_foreground_pixels(
            binary,
            xi - inward,
            yi - halfspan,
            xi + outward + 1,
            yi + halfspan + 1
        )

    if relative_position == "top":
        return img_count_foreground_pixels(
            binary,
            xi - halfspan,
            yi - outward,
            xi + halfspan + 1,
            yi + inward + 1
        )

    if relative_position == "bottom":
        return img_count_foreground_pixels(
            binary,
            xi - halfspan,
            yi - inward,
            xi + halfspan + 1,
            yi + outward + 1
        )

    return 0

def geom_infer_orientation_from_bbox(bbox, default_orientation="horizontal"):
    x1, y1, x2, y2 = bbox
    width = max(x2 - x1, 1e-6)
    height = max(y2 - y1, 1e-6)

    if height / width >= ASPECT_RATIO_THRESHOLD:
        return "vertical"
    if width / height >= ASPECT_RATIO_THRESHOLD:
        return "horizontal"
    return default_orientation