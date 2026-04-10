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


def _opamp_diagonal_support(binary, x, y, diag_kind, radius=4):
    """
    Supporto locale della diagonale del triangolo vicino al punto candidato.

    diag_kind:
      - "down_right"  -> linea tipo "\"
      - "up_right"    -> linea tipo "/"
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


def _opamp_connected_vertical_run_from_side(binary, x, y1, y2, side, halfspan=1, min_fg=1):
    """
    Cerca una run verticale CONTIGUA connessa al lato alto o basso del bbox.

    È la strategia unica per gli aux:
    - il ramo deve partire davvero dal lato esterno del simbolo
    - la giunzione è la fine di quella run, dove incontra il lato obliquo
    """
    h = binary.shape[0]
    side_band = max(2, int(round(0.04 * max(y2 - y1, 1))))

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
            y for y in range(y1, min(y2, y1 + side_band) + 1)
            if row_fg(y) >= min_fg
        ]
        if not start_candidates:
            return None

        run_start = start_candidates[0]
        run_end = run_start

        max_y = min(y2, y1 + int(round(0.75 * max(y2 - y1, 1))))
        for y in range(run_start + 1, max_y + 1):
            if row_fg(y) >= min_fg:
                run_end = y
            else:
                break

        return {
            "run_start": run_start,
            "run_end": run_end,
            "run_len": int(run_end - run_start + 1),
            "side_band": side_band,
        }

    if side == "bottom":
        start_candidates = [
            y for y in range(y2, max(y1, y2 - side_band) - 1, -1)
            if row_fg(y) >= min_fg
        ]
        if not start_candidates:
            return None

        run_start = start_candidates[0]
        run_end = run_start

        min_y = max(y1, y2 - int(round(0.75 * max(y2 - y1, 1))))
        for y in range(run_start - 1, min_y - 1, -1):
            if row_fg(y) >= min_fg:
                run_end = y
            else:
                break

        return {
            "run_start": run_start,
            "run_end": run_end,
            "run_len": int(run_start - run_end + 1),
            "side_band": side_band,
        }

    return None




def _geom_opamp_refine_aux_junction(binary, bbox, orientation, relative_position, base_point, diag_kind):
    """
    Rifinisce il punto dell'aux DOPO l'attivazione geometrica.

    La prima fase decide se l'aux esiste davvero partendo dal lato esterno.
    Però, quando sopra/sotto all'opamp c'è anche un simbolo piccolo (es. terminal,
    bubble, source), il punto trovato può fermarsi troppo presto: al bordo del
    simbolo esterno, non al vero giunto tra branch verticale e diagonale del triangolo.

    Qui facciamo una seconda fase locale:
    - partiamo dal punto candidato già trovato
    - proviamo una piccola finestra di x attorno al candidato
    - per ogni x cerchiamo la fine del branch verticale interno
    - scegliamo il candidato con miglior supporto della diagonale corretta

    Così l'aux resta attivato solo quando esiste davvero, ma il punto finale
    viene riportato sul corpo dell'opamp.
    """
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)

    base_x = int(round(base_point[0]))
    base_y = int(round(base_point[1]))

    x_radius = OPAMP_AUX_JUNCTION_REFINE_X_RADIUS

    best = None
    for x in range(max(x1, base_x - x_radius), min(x2, base_x + x_radius) + 1):
        refined_point = _geom_opamp_internal_wire_triangle_junction(
            binary,
            bbox,
            (float(x), float(base_y)),
            relative_position,
        )
        if refined_point is None:
            continue

        rx = int(round(refined_point[0]))
        ry = int(round(refined_point[1]))
        diag_support = _opamp_diagonal_support(
            binary,
            rx,
            ry,
            diag_kind=diag_kind,
            radius=OPAMP_AUX_JUNCTION_DIAG_RADIUS,
        )

        travel = abs(ry - base_y) if relative_position in {"top", "bottom"} else abs(rx - base_x)

        key = (
            diag_support >= OPAMP_AUX_MIN_DIAG_SUPPORT,
            diag_support,
            travel,
            -abs(x - base_x),
        )

        if best is None or key > best["key"]:
            best = {
                "key": key,
                "point": (float(rx), float(ry)),
                "diag_support": diag_support,
                "travel": travel,
                "source_x": x,
            }

    if best is None:
        return base_point, {
            "refined": False,
            "refine_source_x": base_x,
            "refine_travel": 0,
            "refined_diag_support": 0,
        }

    return best["point"], {
        "refined": best["point"] != base_point,
        "refine_source_x": best["source_x"],
        "refine_travel": best["travel"],
        "refined_diag_support": best["diag_support"],
    }


def _geom_opamp_aux_internal_junction(binary, bbox, orientation, relative_position, scan_start, scan_end, center_coord):
    """
    Strategia unica per gli auxiliary pin dell'opamp.

    Cerchiamo SOLO una run verticale connessa al lato alto/basso del bbox
    nella banda centrale dell'opamp. Il terminale viene posto alla fine della
    run, ma solo se in quel punto troviamo anche supporto della diagonale
    corretta del triangolo.

    Questo evita di agganciarsi ai numeri interni (4, 5, ecc.), che possono
    avere tratti verticali ma non sono connessi al lato esterno del simbolo.
    """
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)

    scan_start = int(round(scan_start))
    scan_end = int(round(scan_end))
    center_coord = int(round(center_coord))

    # Questa versione gestisce in modo robusto gli opamp orizzontali.
    # Per gli altri casi facciamo fallback pulito senza falsi positivi.
    if orientation not in {"right", "left"} or relative_position not in {"top", "bottom"}:
        fallback_point = (
            float(center_coord),
            float(y1 if relative_position == "top" else y2),
        )
        return fallback_point, {
            "point_mode": "opamp_aux_side_connected_branch",
            "relative_position": relative_position,
            "scan_axis": "x",
            "scan_start": scan_start,
            "scan_end": scan_end,
            "aux_detected": False,
            "aux_stem_length": 0,
            "diag_support": 0,
            "junction_point": fallback_point,
            "center_coord": center_coord,
            "orientation_supported": False,
        }

    xs = list(range(max(x1, scan_start), min(x2, scan_end) + 1))
    if not xs:
        xs = [int(round((x1 + x2) / 2))]

    if orientation == "right":
        diag_kind = "down_right" if relative_position == "top" else "up_right"
    else:
        diag_kind = "up_right" if relative_position == "top" else "down_right"

    best = None

    for x in xs:
        run = _opamp_connected_vertical_run_from_side(
            binary,
            x,
            y1,
            y2,
            side=relative_position,
            halfspan=1,
            min_fg=1,
        )
        if run is None:
            continue

        junction_y = run["run_end"]
        diag_support = _opamp_diagonal_support(
            binary,
            x,
            junction_y,
            diag_kind=diag_kind,
            radius=4,
        )

        key = (
            run["run_len"] >= OPAMP_AUX_MIN_STEM_LENGTH,
            diag_support >= OPAMP_AUX_MIN_DIAG_SUPPORT,
            run["run_len"],
            diag_support,
            -abs(x - center_coord),
        )

        if best is None or key > best["key"]:
            best = {
                "key": key,
                "x": x,
                "junction_y": junction_y,
                "run_len": run["run_len"],
                "run_start": run["run_start"],
                "run_end": run["run_end"],
                "diag_support": diag_support,
                "diag_kind": diag_kind,
                "side_band": run["side_band"],
            }

    if best is None:
        fallback_point = (
            float(center_coord),
            float(y1 if relative_position == "top" else y2),
        )
        return fallback_point, {
            "point_mode": "opamp_aux_side_connected_branch",
            "relative_position": relative_position,
            "scan_axis": "x",
            "scan_start": scan_start,
            "scan_end": scan_end,
            "aux_detected": False,
            "aux_stem_length": 0,
            "diag_support": 0,
            "junction_point": fallback_point,
            "center_coord": center_coord,
            "orientation_supported": True,
        }

    base_point = (float(best["x"]), float(best["junction_y"]))
    refined_point, refine_debug = _geom_opamp_refine_aux_junction(
        binary,
        bbox,
        orientation,
        relative_position,
        base_point,
        diag_kind=best["diag_kind"],
    )

    point = refined_point
    effective_diag_support = max(
        int(best["diag_support"]),
        int(refine_debug.get("refined_diag_support", 0)),
    )

    aux_detected = (
        best["run_len"] >= OPAMP_AUX_MIN_STEM_LENGTH
        and effective_diag_support >= OPAMP_AUX_MIN_DIAG_SUPPORT
    )

    return point, {
        "point_mode": "opamp_aux_side_connected_branch",
        "relative_position": relative_position,
        "scan_axis": "x",
        "scan_start": scan_start,
        "scan_end": scan_end,
        "candidate_coord": best["x"],
        "stem_run_start": best["run_start"],
        "stem_run_end": best["run_end"],
        "aux_stem_length": best["run_len"],
        "diag_support": effective_diag_support,
        "base_diag_support": best["diag_support"],
        "diag_kind": best["diag_kind"],
        "side_band": best["side_band"],
        "base_point": base_point,
        "junction_point": point,
        "aux_detected": aux_detected,
        "center_coord": center_coord,
        "orientation_supported": True,
        **refine_debug,
    }


def geom_terminal_point_opamp(binary, bbox, orientation: str, term_def: dict):
    """
    Localizzazione dei terminali di un opamp.

    - terminali obbligatori: lato bbox + slot
    - terminali ausiliari: giunto tra ramo esterno e lato obliquo
    """
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)

    relative_position = term_def["relative_position"]
    slot = term_def.get("slot", "center")

    scan_start, scan_end, center_coord = _opamp_slot_scan_range(
        x1, y1, x2, y2, relative_position, slot
    )

    if term_def.get("terminal_role") == "auxiliary" and slot == "center":
        width = max(x2 - x1, 1)
        height = max(y2 - y1, 1)

        if relative_position in {"top", "bottom"}:
            scan_start = x1 + OPAMP_AUX_CENTER_START_RATIO * width
            scan_end = x1 + OPAMP_AUX_CENTER_END_RATIO * width
        else:
            scan_start = y1 + OPAMP_AUX_CENTER_START_RATIO * height
            scan_end = y1 + OPAMP_AUX_CENTER_END_RATIO * height

        center_coord = int(round((scan_start + scan_end) / 2))

    if term_def.get("terminal_role") == "auxiliary":
        point, aux_debug = _geom_opamp_aux_internal_junction(
            binary,
            bbox,
            orientation,
            relative_position,
            scan_start,
            scan_end,
            center_coord,
        )

        aux_debug["opamp_orientation"] = orientation
        aux_debug["opamp_terminal_name"] = term_def.get("name")
        aux_debug["opamp_terminal_role"] = term_def.get("terminal_role")
        aux_debug["opamp_slot"] = slot
        return point, aux_debug

    point, peak_debug = geom_terminal_point_by_side_peak(
        binary,
        bbox,
        relative_position,
        scan_start=scan_start,
        scan_end=scan_end,
        center_coord=center_coord,
    )

    peak_debug["point_mode"] = OPAMP_POINT_MODE
    peak_debug["opamp_orientation"] = orientation
    peak_debug["opamp_terminal_name"] = term_def.get("name")
    peak_debug["opamp_terminal_role"] = term_def.get("terminal_role")
    peak_debug["opamp_slot"] = slot

    return point, peak_debug

def geom_infer_orientation_from_bbox(bbox, default_orientation="horizontal"):
    x1, y1, x2, y2 = bbox
    width = max(x2 - x1, 1e-6)
    height = max(y2 - y1, 1e-6)

    if height / width >= ASPECT_RATIO_THRESHOLD:
        return "vertical"
    if width / height >= ASPECT_RATIO_THRESHOLD:
        return "horizontal"
    return default_orientation

def _geom_opamp_internal_wire_triangle_junction(binary, bbox, base_point, relative_position):
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)

    xi = int(round(base_point[0]))
    yi = int(round(base_point[1]))

    halfspan = 2
    min_fg = 3

    def row_fg(y):
        return img_count_foreground_pixels(
            binary,
            xi - halfspan,
            y,
            xi + halfspan + 1,
            y + 1,
        )

    def col_fg(x):
        return img_count_foreground_pixels(
            binary,
            x,
            yi - halfspan,
            x + 1,
            yi + halfspan + 1,
        )

    if relative_position == "top":
        y_start = max(y1, yi)
        y_stop = min(y2, y1 + int(0.70 * (y2 - y1)))
        run_start = None
        run_end = None

        for y in range(y_start, y_stop + 1):
            if row_fg(y) >= min_fg:
                if run_start is None:
                    run_start = y
                run_end = y
            elif run_start is not None:
                break

        if run_start is not None:
            return (float(xi), float(run_end))

    elif relative_position == "bottom":
        y_start = min(y2, yi)
        y_stop = max(y1, y2 - int(0.70 * (y2 - y1)))
        run_start = None
        run_end = None

        for y in range(y_start, y_stop - 1, -1):
            if row_fg(y) >= min_fg:
                if run_start is None:
                    run_start = y
                run_end = y
            elif run_start is not None:
                break

        if run_start is not None:
            return (float(xi), float(run_end))

    elif relative_position == "left":
        x_start = max(x1, xi)
        x_stop = min(x2, x1 + int(0.70 * (x2 - x1)))
        run_start = None
        run_end = None

        for x in range(x_start, x_stop + 1):
            if col_fg(x) >= min_fg:
                if run_start is None:
                    run_start = x
                run_end = x
            elif run_start is not None:
                break

        if run_start is not None:
            return (float(run_end), float(yi))

    elif relative_position == "right":
        x_start = min(x2, xi)
        x_stop = max(x1, x2 - int(0.70 * (x2 - x1)))
        run_start = None
        run_end = None

        for x in range(x_start, x_stop - 1, -1):
            if col_fg(x) >= min_fg:
                if run_start is None:
                    run_start = x
                run_end = x
            elif run_start is not None:
                break

        if run_start is not None:
            return (float(run_end), float(yi))

    return base_point