"""
03_estimate_terminals.py

Scopo:
    Stimare i terminali dei componenti rilevati nel passo 02.

Strategie principali:
    - fixed
    - auto_by_aspect_ratio
    - one_terminal_by_orientation
    - two_terminal_by_connection_axis
    - terminal_auto_one_or_two

Casi speciali:
    - Capacitor / Polarized_Capacitor
    - Switch
    - Terminal

    Per i componenti a 3 terminali non basta dire su quale lato cade il terminale
    ma serve anche capire dove si trova realmente lungo quel lato.
    Si usa una localizzazione "side peak": 
    prima stimiamo i lati attivi, poi cerchiamo il picco di connessione lungo il lato.
"""

from pathlib import Path
import json
import yaml
import cv2

#PATH / INPUT-OUTPUT
PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_DIR = PROJECT_ROOT / "outputs" / "topology_v3_three_terminals" / "02_assign_instances"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "topology_v3_three_terminals" / "03_estimate_terminals"
DEBUG_IMAGES_DIR = OUTPUT_DIR / "debug_images"

CLASS_TERMINALS_PATH = PROJECT_ROOT / "metadata" / "class_terminals_v1.yaml"

#DEBUG / VISUALIZATION
SAVE_DEBUG_IMAGES = True
TERMINAL_RADIUS = 6

# COARSE SIDE SAMPLING
SIDE_SAMPLE_THICKNESS = 10
SIDE_CENTER_RATIO = 0.35
SIDE_SCORE_MIN_PIXELS = 5
AXIS_SCORE_MARGIN = 1.15


# GENERIC TERMINAL GEOMETRY
TERMINAL_OUTWARD_OFFSET = 4
ASPECT_RATIO_THRESHOLD = 1.10

# LOCAL PROBES FOR GENERIC TWO-TERMINAL COMPONENTS
TERMINAL_PROBE_OUT_LEN = 12
TERMINAL_PROBE_INSET = 2
TERMINAL_PROBE_HALFSPAN_RATIO = 0.22
TERMINAL_PROBE_HALFSPAN_MIN = 3
TERMINAL_PROBE_HALFSPAN_MAX = 8
TERMINAL_PROBE_AXIS_MARGIN = 1.12
TERMINAL_PROBE_MIN_SIDE_SCORE = 3

SWITCH_ANCHOR_RATIOS = (0.30, 0.50, 0.70)

# SPECIAL HEURISTICS FOR CLASS "Terminal"
# Probe locali vicini al bbox
TERMINAL_CLASS_PROBE_OUT_LEN = 10
TERMINAL_CLASS_PROBE_HALFSPAN_RATIO = 0.16
TERMINAL_CLASS_PROBE_HALFSPAN_MIN = 2
TERMINAL_CLASS_PROBE_HALFSPAN_MAX = 4

# Decisione 1-vs-2 terminali
TERMINAL_CLASS_TWO_SIDE_MIN = 5
TERMINAL_CLASS_ONE_SIDE_MIN = 3
TERMINAL_CLASS_TWO_AXIS_MARGIN = 1.35
TERMINAL_CLASS_TWO_BALANCE_RATIO = 0.60

# Bias per porte esterne / terminali vicino al bordo immagine
TERMINAL_CLASS_BORDER_MARGIN = 14
TERMINAL_BORDER_MARGIN_RATIO = 0.04
TERMINAL_BORDER_MARGIN_MIN = 28

# Probe più lontani dal bbox per confermare continuità reale del wire
TERMINAL_CLASS_FAR_GAP = 3
TERMINAL_CLASS_FAR_LEN = 10
TERMINAL_CLASS_FAR_MIN = 2

# 3 TERMINALI - STIMA DEL PATTERN DEI LATI
THREE_TERMINAL_ANCHOR_RATIOS = (0.22, 0.50, 0.78)
THREE_TERMINAL_MIN_SIDE_SCORE = 3

THREE_TERMINAL_TEMPLATES = {
    "left": ("left", "top", "bottom"),
    "right": ("right", "top", "bottom"),
    "top": ("top", "left", "right"),
    "bottom": ("bottom", "left", "right"),
}

# Per i 3-terminali il lato "singolo" (base/gate) di solito entra circa a metà lato,
# mentre gli altri due terminali stanno sull'asse ortogonale e molto spesso verso
# il lato opposto del simbolo.
#
# Per questo facciamo due cose distinte:
#   1. stimiamo PRIMA il lato singolo usando probe centrati
#   2. stimiamo POI i punti finali con una ricerca "biased" coerente con quel lato
THREE_TERMINAL_SINGLE_SIDE_MIN_SCORE = 3
THREE_TERMINAL_SINGLE_SIDE_MARGIN = 1.08

# 3 TERMINALI - LOCALIZZAZIONE FINE DEL PUNTO SUL LATO
THREE_TERMINAL_POINT_MODE = "three_terminal_structured"

SIDE_PEAK_SCAN_MARGIN_RATIO = 0.08
SIDE_PEAK_SCAN_MARGIN_MIN = 2

SIDE_PEAK_HALFSPAN_RATIO = 0.12
SIDE_PEAK_HALFSPAN_MIN = 2
SIDE_PEAK_HALFSPAN_MAX = 6

SIDE_PEAK_OUT_LEN = 12
SIDE_PEAK_INSET = 1

SIDE_PEAK_MIN_SCORE = 2
SIDE_PEAK_KEEP_RATIO = 0.85

# Nei 3-terminali:
# - il terminale "singolo" viene cercato in una banda centrale del suo lato
# - i due terminali opposti vengono cercati verso il lato opposto al terminale singolo
THREE_TERMINAL_SINGLE_SCAN_START_RATIO = 0.25
THREE_TERMINAL_SINGLE_SCAN_END_RATIO = 0.75

THREE_TERMINAL_OPPOSITE_NEAR_RATIO = 0.52
THREE_TERMINAL_OPPOSITE_FAR_RATIO = 0.96

# =========================================================
# MOSFET - STIMA DEL LATO SINGOLO
# =========================================================
# Per i Mosfet il lato singolo (gate) conviene stimarlo con probe
# molto stretti e quasi solo esterni al bbox, altrimenti il canale
# interno del simbolo falsifica facilmente i punteggi.
MOSFET_SINGLE_SIDE_OUT_LEN = 14
MOSFET_SINGLE_SIDE_INSET = 0

MOSFET_SINGLE_SIDE_HALFSPAN_RATIO = 0.10
MOSFET_SINGLE_SIDE_HALFSPAN_MIN = 2
MOSFET_SINGLE_SIDE_HALFSPAN_MAX = 5

MOSFET_SINGLE_SIDE_MIN_SCORE = 3
MOSFET_SINGLE_SIDE_MARGIN = 1.12

# Probe "far" per confermare che il lato singolo del Mosfet
# continua davvero come wire e non è solo testo / grafica vicina.
MOSFET_SINGLE_SIDE_FAR_GAP = 2
MOSFET_SINGLE_SIDE_FAR_LEN = 10
MOSFET_SINGLE_SIDE_FAR_WEIGHT = 1.0

# Nei Mosfet verticali del dataset il gate è quasi sempre laterale.
# Per distinguere left vs right usiamo anche una striscia INTERNA
# al bbox nella zona centrale del simbolo.
MOSFET_GATE_INSIDE_X_RATIO = 0.12
MOSFET_GATE_INSIDE_X_MIN = 3
MOSFET_GATE_CENTER_Y1_RATIO = 0.30
MOSFET_GATE_CENTER_Y2_RATIO = 0.70
MOSFET_GATE_INSIDE_WEIGHT = 0.35
MOSFET_FORCE_LATERAL_GATE = True

# Validazione finale dell'orientazione del Mosfet tramite supporto locale
# attorno ai 3 terminali stimati.
MOSFET_POINT_SUPPORT_RADIUS = 5
MOSFET_ORIENTATION_VALIDATION_MARGIN = 1.03
MOSFET_SINGLE_TERMINAL_WEIGHT = 1.25

# =========================================================
# I/O HELPERS
# =========================================================
def io_load_yaml(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def io_load_class_metadata(class_terminals_path: Path):
    data = io_load_yaml(class_terminals_path)
    return {int(k): v for k, v in data.items()}

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

def img_count_foreground_pixels(binary, x1, y1, x2, y2):
    h, w = binary.shape[:2]
    x1 = max(0, min(w, x1))
    y1 = max(0, min(h, y1))
    x2 = max(0, min(w, x2))
    y2 = max(0, min(h, y2))
    if x2 <= x1 or y2 <= y1:
        return 0
    return int(cv2.countNonZero(binary[y1:y2, x1:x2]))

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


def candidate_mosfet_orientations_from_bbox(bbox):
    """
    Riduce le orientazioni candidate in base all'aspect ratio del bbox.
    - simbolo verticale -> gate laterale -> left/right
    - simbolo orizzontale -> gate sopra/sotto -> top/bottom
    - bbox quasi quadrato -> tutte
    """
    x1, y1, x2, y2 = bbox
    width = max(x2 - x1, 1e-6)
    height = max(y2 - y1, 1e-6)

    if height / width >= ASPECT_RATIO_THRESHOLD:
        return ("left", "right")
    if width / height >= ASPECT_RATIO_THRESHOLD:
        return ("top", "bottom")
    return ("left", "right", "top", "bottom")


def score_mosfet_orientation_by_terminal_points(binary, bbox, orientation):
    """
    Valuta un'orientazione candidata del Mosfet usando i 3 terminali stimati.

    Per ogni terminale:
    - stima il punto con geom_terminal_point_three_terminal(...)
    - misura il supporto locale attorno al punto
    - somma i punteggi

    Il terminale singolo (gate) pesa un po' di più, perché è quello che
    ci interessa davvero distinguere tra left/right o top/bottom.
    """
    total_score = 0.0
    debug = {}

    for rel_pos in THREE_TERMINAL_TEMPLATES[orientation]:
        point, point_debug = geom_terminal_point_three_terminal(
            binary,
            bbox,
            orientation,
            rel_pos
        )
        x, y = point
        local_support = score_point_local_support(binary, x, y)

        weight = MOSFET_SINGLE_TERMINAL_WEIGHT if rel_pos == orientation else 1.0
        weighted_score = weight * local_support
        total_score += weighted_score

        debug[rel_pos] = {
            "point": point,
            "local_support": local_support,
            "weight": weight,
            "weighted_score": weighted_score,
            "point_debug": point_debug,
        }

    return total_score, debug


def geom_infer_orientation_from_bbox(bbox, default_orientation="horizontal"):
    x1, y1, x2, y2 = bbox
    width = max(x2 - x1, 1e-6)
    height = max(y2 - y1, 1e-6)

    if height / width >= ASPECT_RATIO_THRESHOLD:
        return "vertical"
    if width / height >= ASPECT_RATIO_THRESHOLD:
        return "horizontal"
    return default_orientation


def img_build_foreground_binary(image_bgr):
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return binary

# =========================================================
# PROBE HELPERS - GENERIC
# =========================================================
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


def _probe_halfspan(width, height):
    min_dim = max(1, min(width, height))
    halfspan = int(round(min_dim * TERMINAL_PROBE_HALFSPAN_RATIO))
    halfspan = max(TERMINAL_PROBE_HALFSPAN_MIN, halfspan)
    halfspan = min(TERMINAL_PROBE_HALFSPAN_MAX, halfspan)
    return halfspan


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

def _mosfet_single_side_halfspan(width, height):
    """
    Halfspan piccolo: vogliamo leggere soprattutto il wire che entra nel gate,
    non la struttura interna del Mosfet.
    """
    min_dim = max(1, min(width, height))
    halfspan = int(round(min_dim * MOSFET_SINGLE_SIDE_HALFSPAN_RATIO))
    halfspan = max(MOSFET_SINGLE_SIDE_HALFSPAN_MIN, halfspan)
    halfspan = min(MOSFET_SINGLE_SIDE_HALFSPAN_MAX, halfspan)
    return halfspan


def get_mosfet_single_side_scores(binary, bbox):
    """
    Score specifici per capire il lato singolo del Mosfet.

    Usiamo:
    - probe near: subito fuori dal bbox
    - probe far : poco più lontano, per confermare continuità reale del wire

    Questo riduce gli errori dovuti a:
    - testo vicino al simbolo
    - bordo del simbolo
    - grafica interna del canale
    """
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

def get_mosfet_lateral_gate_scores(binary, bbox):
    """
    Score specifico per decidere se il gate del Mosfet è a sinistra o a destra.

    Combiniamo:
    - score esterno (wire che arriva da fuori)
    - score interno nella fascia centrale del simbolo

    Questo aiuta nei casi in cui il lato drain/source ha un wire più forte
    all'esterno ma il gate vero è riconoscibile meglio all'interno del simbolo.
    """
    x1, y1, x2, y2 = geom_clamp_bbox_to_image(bbox, binary.shape)
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)

    outside_scores = get_mosfet_single_side_scores(binary, bbox)

    inside_w = max(MOSFET_GATE_INSIDE_X_MIN, int(round(width * MOSFET_GATE_INSIDE_X_RATIO)))
    cy1 = int(round(y1 + height * MOSFET_GATE_CENTER_Y1_RATIO))
    cy2 = int(round(y1 + height * MOSFET_GATE_CENTER_Y2_RATIO))

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

    combined_left = outside_scores["left"] + MOSFET_GATE_INSIDE_WEIGHT * inside_left
    combined_right = outside_scores["right"] + MOSFET_GATE_INSIDE_WEIGHT * inside_right

    return {
        "left": combined_left,
        "right": combined_right,
        "outside_left": outside_scores["left"],
        "outside_right": outside_scores["right"],
        "inside_left": inside_left,
        "inside_right": inside_right,
        "probe_mode": "mosfet_lateral_gate_combined",
    }

# =========================================================
# PROBE HELPERS - CLASS "Terminal"
# =========================================================
def _terminal_class_probe_halfspan(width, height):
    min_dim = max(1, min(width, height))
    halfspan = int(round(min_dim * TERMINAL_CLASS_PROBE_HALFSPAN_RATIO))
    halfspan = max(TERMINAL_CLASS_PROBE_HALFSPAN_MIN, halfspan)
    halfspan = min(TERMINAL_CLASS_PROBE_HALFSPAN_MAX, halfspan)
    return halfspan


def get_terminal_class_probe_scores(binary, bbox):
    """
    Probe stretti SOLO esterni al bbox, pensati per la classe Terminal.
    Questo evita di far contaminare i punteggi dalla grafica interna del cerchietto.
    """
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

def get_terminal_border_preference(binary_shape, bbox, margin=TERMINAL_CLASS_BORDER_MARGIN):
    """
    Se il Terminal è vicino al bordo dell'immagine, favorisce il lato interno al diagramma.
    Esempio:
    - vicino al bordo sinistro -> preferisci 'right'
    - vicino al bordo destro  -> preferisci 'left'
    """
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

# =========================================================
# STRATEGY: VARIABLE TERMINAL CLASS ("Terminal")
# =========================================================
def classify_terminal_cardinality(binary, bbox, default_side="right"):
    local_scores = get_terminal_class_probe_scores(binary, bbox)
    far_scores = get_terminal_class_far_probe_scores(binary, bbox)
    border_pref = get_terminal_border_preference(binary.shape, bbox)

    # -------------------------------------------------
    # 1) Porta esterna: vicino al bordo -> forza 1 lato
    # -------------------------------------------------
    if is_terminal_near_border(binary.shape, bbox):
        local_scores["far_scores"] = far_scores
        local_scores["decision_mode"] = "terminal_cardinality_border_forced_one"
        local_scores["border_preference"] = border_pref
        return 1, border_pref if border_pref is not None else default_side, local_scores

    # Lato attivo solo se confermato anche dal probe far
    active = {}
    for side in ("top", "bottom", "left", "right"):
        active[side] = (
            local_scores[side] >= TERMINAL_CLASS_ONE_SIDE_MIN and
            far_scores[side] >= TERMINAL_CLASS_FAR_MIN
        )

    left_val = local_scores["left"]
    right_val = local_scores["right"]
    top_val = local_scores["top"]
    bottom_val = local_scores["bottom"]

    lr_pair = min(left_val, right_val)
    tb_pair = min(top_val, bottom_val)
    lr_score = left_val + right_val
    tb_score = top_val + bottom_val

    # -------------------------------------------------
    # 2) Due terminali solo se davvero molto chiaro
    # -------------------------------------------------
    if (
        active["left"] and active["right"] and
        lr_pair >= TERMINAL_CLASS_TWO_SIDE_MIN and
        lr_score > tb_score * TERMINAL_CLASS_TWO_AXIS_MARGIN and
        min(left_val, right_val) >= TERMINAL_CLASS_TWO_BALANCE_RATIO * max(left_val, right_val) and
        not active["top"] and not active["bottom"]
    ):
        local_scores["far_scores"] = far_scores
        local_scores["decision_mode"] = "terminal_cardinality_two_horizontal"
        return 2, "horizontal", local_scores

    if (
        active["top"] and active["bottom"] and
        tb_pair >= TERMINAL_CLASS_TWO_SIDE_MIN and
        tb_score > lr_score * TERMINAL_CLASS_TWO_AXIS_MARGIN and
        min(top_val, bottom_val) >= TERMINAL_CLASS_TWO_BALANCE_RATIO * max(top_val, bottom_val) and
        not active["left"] and not active["right"]
    ):
        local_scores["far_scores"] = far_scores
        local_scores["decision_mode"] = "terminal_cardinality_two_vertical"
        return 2, "vertical", local_scores

    # -------------------------------------------------
    # 3) Altrimenti uno
    # -------------------------------------------------
    candidate_sides = [s for s in ("top", "bottom", "left", "right") if active[s]]
    if candidate_sides:
        best_side = max(candidate_sides, key=lambda s: local_scores[s])
    else:
        best_side = max(("top", "bottom", "left", "right"), key=lambda s: local_scores[s])

    local_scores["far_scores"] = far_scores
    local_scores["decision_mode"] = "terminal_cardinality_default_one"
    return 1, best_side, local_scores

def detect_terminal_one_side(binary, bbox, default_side="right", precomputed_scores=None):
    scores = precomputed_scores if precomputed_scores is not None else get_terminal_class_probe_scores(binary, bbox)

    border_pref = get_terminal_border_preference(binary.shape, bbox)
    if border_pref is not None:
        return [{"name": "t1", "relative_position": border_pref}], border_pref

    best_side = max(("top", "bottom", "left", "right"), key=lambda s: scores[s])
    if scores[best_side] >= TERMINAL_CLASS_ONE_SIDE_MIN:
        return [{"name": "t1", "relative_position": best_side}], best_side

    return [{"name": "t1", "relative_position": default_side}], default_side

def detect_terminal_two_sides(binary, bbox, precomputed_scores=None):
    scores = precomputed_scores if precomputed_scores is not None else get_terminal_class_probe_scores(binary, bbox)

    lr_score = scores["left"] + scores["right"]
    tb_score = scores["top"] + scores["bottom"]

    if lr_score >= tb_score:
        return [
            {"name": "t1", "relative_position": "left"},
            {"name": "t2", "relative_position": "right"},
        ], "horizontal"

    return [
        {"name": "t1", "relative_position": "top"},
        {"name": "t2", "relative_position": "bottom"},
    ], "vertical"


def detect_terminal_auto_one_or_two(binary, bbox, default_side="right"):
    cardinality, mode, scores = classify_terminal_cardinality(binary, bbox, default_side=default_side)

    if cardinality == 1:
        terminals_def, orientation = detect_terminal_one_side(
            binary, bbox, default_side=default_side, precomputed_scores=scores
        )
        scores["final_mode"] = "one_terminal"
        return terminals_def, orientation, scores

    terminals_def, orientation = detect_terminal_two_sides(
        binary, bbox, precomputed_scores=scores
    )
    scores["final_mode"] = "two_terminal"
    return terminals_def, orientation, scores

# =========================================================
# STRATEGY: THREE-TERMINAL COMPONENTS
# =========================================================
def strategy_detect_three_terminal_orientation(binary, bbox, class_name="", default_orientation="right"):
    """
    Strategia per i 3-terminali.

    Idea generale:
    - NPN: la scelta del lato singolo funziona bene con i probe classici
    - Mosfet: oltre ai probe per il lato singolo, facciamo una validazione
      finale dell'orientazione usando i 3 punti terminali stimati

    Flusso:
    1. calcolo score del lato singolo
    2. calcolo fallback multi-anchor
    3. se classe Mosfet:
       - valuto direttamente le orientazioni candidate (left/right oppure top/bottom)
         usando il supporto locale attorno ai 3 terminali stimati
       - se una orientazione è chiaramente migliore, la uso
    4. altrimenti uso il lato singolo se è chiaro
    5. se non basta, fallback multi-anchor
    6. ultimo fallback: default_orientation YAML
    """
    # -------------------------------------------------
    # 1) Score per il lato singolo
    # -------------------------------------------------
    if class_name == "Mosfet":
        single_side_scores = get_mosfet_single_side_scores(binary, bbox)
        single_side_source = "mosfet_near_far"
        single_side_min_score = MOSFET_SINGLE_SIDE_MIN_SCORE
        single_side_margin = MOSFET_SINGLE_SIDE_MARGIN
        lateral_scores = get_mosfet_lateral_gate_scores(binary, bbox)
    else:
        single_side_scores = get_local_terminal_probe_scores_center(binary, bbox)
        single_side_source = "generic_center"
        single_side_min_score = THREE_TERMINAL_SINGLE_SIDE_MIN_SCORE
        single_side_margin = THREE_TERMINAL_SINGLE_SIDE_MARGIN
        lateral_scores = None

    # Score multi-anchor usati per il fallback template
    multi_scores = get_local_terminal_probe_scores_multi_anchor(
        binary,
        bbox,
        anchor_ratios=THREE_TERMINAL_ANCHOR_RATIOS
    )

    ordered_single = sorted(
        ("top", "bottom", "left", "right"),
        key=lambda side: single_side_scores[side],
        reverse=True
    )
    best_side = ordered_single[0]
    second_side = ordered_single[1]
    best_score = single_side_scores[best_side]
    second_score = single_side_scores[second_side]

    # -------------------------------------------------
    # 2) Validazione finale specifica per Mosfet
    # -------------------------------------------------
    mosfet_orientation_scores = None
    mosfet_orientation_point_debug = None

    if class_name == "Mosfet":
        candidate_orientations = candidate_mosfet_orientations_from_bbox(bbox)

        mosfet_orientation_scores = {}
        mosfet_orientation_point_debug = {}

        for cand in candidate_orientations:
            cand_score, cand_debug = score_mosfet_orientation_by_terminal_points(
                binary,
                bbox,
                cand
            )
            mosfet_orientation_scores[cand] = cand_score
            mosfet_orientation_point_debug[cand] = cand_debug

        ordered_candidates = sorted(
            candidate_orientations,
            key=lambda o: mosfet_orientation_scores[o],
            reverse=True
        )

        cand_best = ordered_candidates[0]
        cand_second = ordered_candidates[1] if len(ordered_candidates) > 1 else None

        cand_best_score = mosfet_orientation_scores[cand_best]
        cand_second_score = (
            mosfet_orientation_scores[cand_second]
            if cand_second is not None else 0.0
        )

        # Se una orientazione candidata è chiaramente migliore,
        # la usiamo direttamente.
        if (
            cand_second is None or
            cand_best_score > cand_second_score * MOSFET_ORIENTATION_VALIDATION_MARGIN
        ):
            required_sides = THREE_TERMINAL_TEMPLATES[cand_best]

            debug_scores = dict(multi_scores)
            debug_scores["single_side_scores"] = {
                "top": single_side_scores["top"],
                "bottom": single_side_scores["bottom"],
                "left": single_side_scores["left"],
                "right": single_side_scores["right"],
            }
            debug_scores["single_side_source"] = single_side_source
            debug_scores["decision_mode"] = "three_terminal_mosfet_point_validation"
            debug_scores["single_side"] = cand_best
            debug_scores["single_side_score"] = cand_best_score
            debug_scores["second_side"] = cand_second
            debug_scores["second_side_score"] = cand_second_score
            debug_scores["required_sides"] = list(required_sides)
            debug_scores["missing_side"] = next(
                side for side in ("top", "bottom", "left", "right")
                if side not in required_sides
            )

            if lateral_scores is not None:
                debug_scores["mosfet_lateral_scores"] = lateral_scores
            debug_scores["mosfet_orientation_scores"] = mosfet_orientation_scores
            debug_scores["mosfet_orientation_point_debug"] = mosfet_orientation_point_debug

            return cand_best, debug_scores

    # -------------------------------------------------
    # 3) Se il lato singolo è abbastanza chiaro, usiamo quello
    # -------------------------------------------------
    if (
        best_score >= single_side_min_score and
        best_score > second_score * single_side_margin
    ):
        required_sides = THREE_TERMINAL_TEMPLATES[best_side]

        debug_scores = dict(multi_scores)
        debug_scores["single_side_scores"] = {
            "top": single_side_scores["top"],
            "bottom": single_side_scores["bottom"],
            "left": single_side_scores["left"],
            "right": single_side_scores["right"],
        }
        debug_scores["single_side_source"] = single_side_source
        debug_scores["decision_mode"] = "three_terminal_single_side"
        debug_scores["single_side"] = best_side
        debug_scores["single_side_score"] = best_score
        debug_scores["second_side"] = second_side
        debug_scores["second_side_score"] = second_score
        debug_scores["required_sides"] = list(required_sides)
        debug_scores["missing_side"] = next(
            side for side in ("top", "bottom", "left", "right")
            if side not in required_sides
        )

        if lateral_scores is not None:
            debug_scores["mosfet_lateral_scores"] = lateral_scores
        if mosfet_orientation_scores is not None:
            debug_scores["mosfet_orientation_scores"] = mosfet_orientation_scores
        if mosfet_orientation_point_debug is not None:
            debug_scores["mosfet_orientation_point_debug"] = mosfet_orientation_point_debug

        return best_side, debug_scores

    # -------------------------------------------------
    # 4) Fallback: template scoring multi-anchor
    # -------------------------------------------------
    candidate_scores = {}
    for orientation, required_sides in THREE_TERMINAL_TEMPLATES.items():
        missing_side = next(
            side for side in ("top", "bottom", "left", "right")
            if side not in required_sides
        )

        req_vals = [multi_scores[s] for s in required_sides]
        missing_val = multi_scores[missing_side]

        candidate_scores[orientation] = sum(req_vals) + min(req_vals) - missing_val

    best_orientation = max(candidate_scores, key=candidate_scores.get)
    required_sides = THREE_TERMINAL_TEMPLATES[best_orientation]
    missing_side = next(
        side for side in ("top", "bottom", "left", "right")
        if side not in required_sides
    )

    if min(multi_scores[s] for s in required_sides) >= THREE_TERMINAL_MIN_SIDE_SCORE:
        multi_scores["single_side_scores"] = {
            "top": single_side_scores["top"],
            "bottom": single_side_scores["bottom"],
            "left": single_side_scores["left"],
            "right": single_side_scores["right"],
        }
        multi_scores["single_side_source"] = single_side_source
        multi_scores["candidate_scores"] = candidate_scores
        multi_scores["decision_mode"] = "three_terminal_multi_anchor_fallback"
        multi_scores["required_sides"] = list(required_sides)
        multi_scores["missing_side"] = missing_side

        if lateral_scores is not None:
            multi_scores["mosfet_lateral_scores"] = lateral_scores
        if mosfet_orientation_scores is not None:
            multi_scores["mosfet_orientation_scores"] = mosfet_orientation_scores
        if mosfet_orientation_point_debug is not None:
            multi_scores["mosfet_orientation_point_debug"] = mosfet_orientation_point_debug

        return best_orientation, multi_scores

    # -------------------------------------------------
    # 5) Ultimo fallback: default_orientation YAML
    # -------------------------------------------------
    multi_scores["single_side_scores"] = {
        "top": single_side_scores["top"],
        "bottom": single_side_scores["bottom"],
        "left": single_side_scores["left"],
        "right": single_side_scores["right"],
    }
    multi_scores["single_side_source"] = single_side_source
    multi_scores["candidate_scores"] = candidate_scores
    multi_scores["decision_mode"] = "three_terminal_default_fallback"

    if lateral_scores is not None:
        multi_scores["mosfet_lateral_scores"] = lateral_scores
    if mosfet_orientation_scores is not None:
        multi_scores["mosfet_orientation_scores"] = mosfet_orientation_scores
    if mosfet_orientation_point_debug is not None:
        multi_scores["mosfet_orientation_point_debug"] = mosfet_orientation_point_debug

    return default_orientation, multi_scores


def resolve_terminal_point_mode(meta: dict):
    """
    Decide come calcolare le coordinate finali del terminale.

    Modalità disponibili:
    - bbox_side_center: centro del lato del bbox
    - three_terminal_structured: localizzazione guidata dal lato singolo
    """
    explicit_mode = meta.get("terminal_point_mode")
    if explicit_mode is not None:
        return explicit_mode

    strategy = meta.get("terminal_strategy", "")
    if strategy == "three_terminal_by_side_pattern":
        return THREE_TERMINAL_POINT_MODE

    return "bbox_side_center"


# =========================================================
# STRATEGY DISPATCHER
# =========================================================
def get_terminals_definition(meta: dict, bbox, image_binary=None):
    strategy = meta.get("terminal_strategy", "fixed")

    if strategy == "fixed":
        return meta.get("terminals", []), None, None, None

    if strategy == "auto_by_aspect_ratio":
        default_orientation = meta.get("default_orientation", "horizontal")
        orientation = geom_infer_orientation_from_bbox(bbox, default_orientation=default_orientation)
        terminals_def = meta.get("orientations", {}).get(orientation)
        if terminals_def is None:
            raise ValueError(f"Nessuna definizione terminali per orientazione '{orientation}'")
        return terminals_def, orientation, None, None

    if strategy == "one_terminal_by_orientation":
        if image_binary is None:
            raise ValueError("one_terminal_by_orientation richiede image_binary.")
        connected_side, side_scores = strategy_detect_connected_side(image_binary, bbox)
        if connected_side is not None:
            terminals_def, orientation = resolve_one_terminal_orientation(meta, connected_side)
            return terminals_def, orientation, connected_side, side_scores
        default_orientation = meta.get("default_orientation")
        terminals_def = meta.get("orientations", {}).get(default_orientation)
        if terminals_def is None:
            raise ValueError(f"Nessuna definizione terminali per default_orientation '{default_orientation}'")
        return terminals_def, default_orientation, None, side_scores

    if strategy in {"two_terminal_by_connection_axis", "two_terminal_capacitor", "two_terminal_switch"}:
        if image_binary is None:
            raise ValueError(f"{strategy} richiede image_binary.")
        default_orientation = meta.get("default_orientation", "horizontal")
        class_name = meta.get("name", "")
        if strategy == "two_terminal_capacitor" or class_name in {"Capacitor", "Polarized_Capacitor"}:
            orientation, side_scores = detect_two_terminal_orientation_capacitor(image_binary, bbox, default_orientation=default_orientation)
        elif strategy == "two_terminal_switch" or class_name == "Switch":
            orientation, side_scores = strategy_detect_two_terminal_orientation_switch(image_binary, bbox, default_orientation=default_orientation)
        else:
            orientation, side_scores = strategy_detect_two_terminal_orientation_generic(image_binary, bbox, default_orientation=default_orientation)
        terminals_def = meta.get("orientations", {}).get(orientation)
        if terminals_def is None:
            raise ValueError(f"Nessuna definizione terminali per orientazione '{orientation}'")
        return terminals_def, orientation, None, side_scores
    
    if strategy == "terminal_auto_one_or_two":
        if image_binary is None:
            raise ValueError("terminal_auto_one_or_two richiede image_binary.")
        default_side = meta.get("default_orientation", "right")
        terminals_def, orientation, side_scores = detect_terminal_auto_one_or_two(image_binary, bbox, default_side=default_side)
        return terminals_def, orientation, None, side_scores

    # 3 terminali
    if strategy == "three_terminal_by_side_pattern":
        if image_binary is None:
            raise ValueError("three_terminal_by_side_pattern richiede image_binary.")

        default_orientation = meta.get("default_orientation", "right")
        class_name = meta.get("name", "")

        orientation, side_scores = strategy_detect_three_terminal_orientation(
            image_binary,
            bbox,
            class_name=class_name,
            default_orientation=default_orientation
        )

        terminals_def = meta.get("orientations", {}).get(orientation)
        if terminals_def is None:
            raise ValueError(f"Nessuna definizione terminali per orientazione '{orientation}'")

        return terminals_def, orientation, None, side_scores


    raise ValueError(f"Strategia terminali non supportata: {strategy}")

# =========================================================
# COMPONENT PROCESSING
# =========================================================
def estimate_terminals_for_component(component: dict, class_meta: dict, image_binary):
    class_id = component["class_id"]
    meta = class_meta.get(class_id, {})
    if not component.get("use_for_terminals", False):
        return [], None, None, None

    bbox = component["bbox"]
    instance_id = component["instance_id"]

    terminals_def, estimated_orientation, connected_side, side_scores = get_terminals_definition(
        meta,
        bbox,
        image_binary=image_binary
    )

    # Per quasi tutti i componenti useremo il centro del lato.
    # Per i 3-terminal invece usiamo una localizzazione più strutturata:
    # prima il lato singolo, poi la coppia ortogonale coerente con quel lato.
    point_mode = resolve_terminal_point_mode(meta)

    terminals = []
    for term_def in terminals_def:
        term_name = term_def["name"]
        rel_pos = term_def["relative_position"]

        point_debug = {
            "point_mode": point_mode
        }

        if point_mode == "three_terminal_structured":
            point, structured_debug = geom_terminal_point_three_terminal(
                image_binary,
                bbox,
                estimated_orientation,
                rel_pos
            )
            x, y = point
            point_debug.update(structured_debug)

        else:
            x, y = geom_terminal_point_from_bbox(bbox, rel_pos)

            # Anche in modalità semplice salviamo un offset relativo sul lato.
            x1, y1, x2, y2 = bbox
            width = max(x2 - x1, 1e-6)
            height = max(y2 - y1, 1e-6)

            if rel_pos in {"top", "bottom"}:
                point_debug["anchor_offset_ratio"] = round((x - x1) / width, 4)
            else:
                point_debug["anchor_offset_ratio"] = round((y - y1) / height, 4)

        terminals.append({
            "terminal_id": f"{instance_id}:{term_name}",
            "instance_id": instance_id,
            "component_class_id": class_id,
            "component_class_name": component.get("class_name"),
            "name": term_name,
            "relative_position": rel_pos,
            "estimated_orientation": estimated_orientation,
            "estimated_connection_side": connected_side,
            "terminal_point_mode": point_mode,
            "terminal_point_debug": point_debug,
            "x": x,
            "y": y,
        })
    return terminals, estimated_orientation, connected_side, side_scores


# =========================================================
# DEBUG DRAWING
# =========================================================
def draw_terminals(image_bgr, components, terminals):
    out = image_bgr.copy()
    for comp in components:
        x1, y1, x2, y2 = map(int, comp["bbox"])
        label = comp.get("instance_id", "N/A")
        if comp.get("estimated_orientation"):
            label = f"{label} ({comp['estimated_orientation'][0]})"
        cv2.rectangle(out, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(out, label, (x1, max(y1 - 8, 0)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA)

    for term in terminals:
        x = int(round(term["x"]))
        y = int(round(term["y"]))
        cv2.circle(out, (x, y), TERMINAL_RADIUS, (0, 0, 255), -1)
        cv2.putText(out, term["terminal_id"], (x + 8, max(y - 8, 0)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 1, cv2.LINE_AA)
    return out

# =========================================================
# MAIN
# =========================================================
def main() -> None:
    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"Cartella input non trovata: {INPUT_DIR}")
    if not CLASS_TERMINALS_PATH.exists():
        raise FileNotFoundError(f"class_terminals_v1.yaml non trovato: {CLASS_TERMINALS_PATH}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DEBUG_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    class_meta = io_load_class_metadata(CLASS_TERMINALS_PATH)
    json_files = sorted(INPUT_DIR.glob("*.json"))
    if not json_files:
        raise FileNotFoundError(f"Nessun file JSON trovato in: {INPUT_DIR}")

    print(f"Input directory : {INPUT_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Class yaml      : {CLASS_TERMINALS_PATH}")
    print(f"File trovati    : {len(json_files)}\n")

    for i, json_path in enumerate(json_files, start=1):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        image_path = Path(data["image_path"])
        image_bgr = cv2.imread(str(image_path))
        if image_bgr is None:
            print(f"Attenzione: immagine non leggibile -> {image_path}")
            continue

        image_binary = img_build_foreground_binary(image_bgr)
        components = data.get("components", [])
        all_terminals = []
        updated_components = []

        for comp in components:
            comp_copy = dict(comp)
            terminals, estimated_orientation, connected_side, side_scores = estimate_terminals_for_component(comp_copy, class_meta, image_binary)
            comp_copy["terminals"] = terminals
            if estimated_orientation is not None:
                comp_copy["estimated_orientation"] = estimated_orientation
            if connected_side is not None:
                comp_copy["estimated_connection_side"] = connected_side
            if side_scores is not None:
                comp_copy["connection_side_scores"] = side_scores
            updated_components.append(comp_copy)
            all_terminals.extend(terminals)

        output_data = dict(data)
        output_data["components"] = updated_components
        output_data["terminals"] = all_terminals
        output_data["n_terminals_estimated"] = len(all_terminals)

        out_json_path = OUTPUT_DIR / json_path.name
        with open(out_json_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        if SAVE_DEBUG_IMAGES:
            debug_img = draw_terminals(image_bgr, updated_components, all_terminals)
            out_img_path = DEBUG_IMAGES_DIR / f"{json_path.stem}_terminals.jpg"
            cv2.imwrite(str(out_img_path), debug_img)

        print(f"[{i}/{len(json_files)}] {json_path.name} -> {len(updated_components)} componenti, {len(all_terminals)} terminali")

    print("\nCompletato.")
    print(f"JSON salvati in: {OUTPUT_DIR}")
    if SAVE_DEBUG_IMAGES:
        print(f"Immagini debug salvate in: {DEBUG_IMAGES_DIR}")


if __name__ == "__main__":
    main()
