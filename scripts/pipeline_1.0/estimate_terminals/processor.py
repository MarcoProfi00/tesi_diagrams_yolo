"""
Prende un singolo componente e lo trasforma in una lista di terminali.

Questo modulo e' il cuore dello step 03:
  - riceve il componente rilevato/istanziato;
  - chiede al dispatcher quali terminali aspettarsi;
  - calcola le coordinate reali dei terminali sull'immagine;
  - aggiunge metadati geometrici e semantici usati dagli step successivi.
"""
from .config import LED_SIDE_PEAK_AXIS_SCAN_RATIO, OPAMP_POINT_MODE
from .dispatcher import get_terminals_definition, resolve_terminal_point_mode
from .geometry import (
    geom_terminal_point_from_bbox,
    geom_terminal_point_from_bbox_with_anchor,
    geom_terminal_point_three_terminal,
    geom_terminal_point_by_side_peak,
    geom_terminal_point_opamp,
)
from .image_ops import img_count_foreground_pixels
from .strategies_three_terminal import (
    get_three_terminal_working_binary,
    resolve_three_terminal_semantics,
    snap_bjt_pair_terminal_to_lateral_wire,
)
from .strategies_basic import get_one_terminal_working_binary, get_two_terminal_working_binary
from .semantic_two_terminal import resolve_two_terminal_semantics


def _get_led_side_peak_scan_window(bbox, estimated_orientation, relative_position):
    """
    Limita la scansione side-peak dei LED all'asse centrale.

    Il LED puo' avere frecce/simboli interni che sporcano il bbox. Restringere
    la finestra di ricerca aiuta a prendere il filo esterno invece del disegno
    interno del simbolo.
    """
    x1, y1, x2, y2 = bbox
    width = max(float(x2) - float(x1), 1.0)
    height = max(float(y2) - float(y1), 1.0)

    if estimated_orientation == "vertical" and relative_position in {"top", "bottom"}:
        half_window = max(10.0, width * LED_SIDE_PEAK_AXIS_SCAN_RATIO / 2.0)
        center_x = (float(x1) + float(x2)) / 2.0
        return (
            center_x - half_window,
            center_x + half_window,
            center_x,
        )

    if estimated_orientation == "horizontal" and relative_position in {"left", "right"}:
        half_window = max(10.0, height * LED_SIDE_PEAK_AXIS_SCAN_RATIO / 2.0)
        center_y = (float(y1) + float(y2)) / 2.0
        return (
            center_y - half_window,
            center_y + half_window,
            center_y,
        )

    return None


def _select_led_vertical_lead_x(binary, bbox):
    """
    Cerca la colonna verticale piu' probabile per i terminali top/bottom del LED.

    Per un LED verticale il centro del bbox non sempre coincide con i reofori:
    questa funzione misura il foreground sopra e sotto il componente e sceglie
    la colonna che ha supporto grafico su entrambi i lati.
    """
    x1, y1, x2, y2 = [int(round(float(v))) for v in bbox]
    if x2 <= x1 or y2 <= y1:
        return None, {"point_mode": "led_vertical_lead_column", "reason": "invalid_bbox"}

    # Scansione colonna per colonna: un buon terminale verticale deve avere
    # pixel foreground sia sopra sia sotto il simbolo.
    scores = []
    for x in range(x1, x2 + 1):
        top_score = img_count_foreground_pixels(binary, x - 2, y1 - 30, x + 3, y1 + 35)
        bottom_score = img_count_foreground_pixels(binary, x - 2, y2 - 35, x + 3, y2 + 30)
        full_score = img_count_foreground_pixels(binary, x - 2, y1 - 30, x + 3, y2 + 30)
        score = min(top_score, bottom_score) * 4.0 + top_score + bottom_score + full_score * 0.1
        scores.append((x, score, top_score, bottom_score, full_score))

    if not scores:
        return None, {"point_mode": "led_vertical_lead_column", "reason": "empty_scan"}

    max_score = max(score for _, score, _, _, _ in scores)
    center_x = (float(x1) + float(x2)) / 2.0
    keep_threshold = max_score * 0.90
    kept = [entry for entry in scores if entry[1] >= keep_threshold]

    # Raggruppiamo colonne adiacenti con score alto: il filo puo' occupare piu'
    # pixel, quindi scegliamo il gruppo migliore invece della singola colonna.
    groups = []
    current = []
    previous_x = None
    for entry in kept:
        x = entry[0]
        if previous_x is None or x <= previous_x + 1:
            current.append(entry)
        else:
            if current:
                groups.append(current)
            current = [entry]
        previous_x = x
    if current:
        groups.append(current)

    def group_key(group):
        best_group_score = max(entry[1] for entry in group)
        group_center = sum(entry[0] for entry in group) / float(len(group))
        return (best_group_score, -abs(group_center - center_x), len(group))

    best_group = max(groups, key=group_key) if groups else kept
    best_x = int(round(sum(entry[0] for entry in best_group) / float(len(best_group))))
    best_entry = max(best_group, key=lambda entry: entry[1])

    if min(best_entry[2], best_entry[3]) < 20:
        return None, {
            "point_mode": "led_vertical_lead_column",
            "reason": "weak_top_bottom_support",
            "best_x": best_x,
            "max_score": round(float(max_score), 3),
            "best_top_score": int(best_entry[2]),
            "best_bottom_score": int(best_entry[3]),
        }

    return float(best_x), {
        "point_mode": "led_vertical_lead_column",
        "scan_start": int(x1),
        "scan_end": int(x2),
        "selected_x": int(best_x),
        "center_x": round(float(center_x), 2),
        "max_score": round(float(max_score), 3),
        "keep_threshold": round(float(keep_threshold), 3),
        "selected_run_start": int(best_group[0][0]),
        "selected_run_end": int(best_group[-1][0]),
        "selected_run_length": int(len(best_group)),
        "best_top_score": int(best_entry[2]),
        "best_bottom_score": int(best_entry[3]),
        "best_full_score": int(best_entry[4]),
        "anchor_offset_ratio": round((float(best_x) - float(x1)) / max(float(x2 - x1), 1.0), 4),
    }

# =========================================================
# PROCESSAMENTO COMPONENTI
# =========================================================
# Stima i terminali di un singolo componente partendo da:
# dizionario del componente
# metadati della classe
# immagine binaria del diagramma
# Ritorna: lista terminali, orientazione stimata, lato connesso e stato.
def estimate_terminals_for_component(component: dict, class_meta: dict, image_binary):
    class_id = component["class_id"]
    meta = class_meta.get(class_id, {})

    # Alcune classi YOLO possono essere utili per detection/masking ma non
    # diventano nodi elettrici: in quel caso non produciamo terminali.
    if not component.get("use_for_terminals", False):
        return [], None, None, None

    bbox = component["bbox"]
    instance_id = component["instance_id"]

    # Il dispatcher restituisce una definizione astratta dei terminali:
    # nomi, lati relativi, orientazione stimata ed eventuali score di debug.
    terminals_def, estimated_orientation, connected_side, side_scores = get_terminals_definition(
        meta,
        bbox,
        image_binary=image_binary
    )

    # Scelta dell'immagine binaria da usare per localizzare i punti.
    # Alcune strategie puliscono o restringono il bbox prima di cercare i picchi:
    # per esempio transistor, terminali singoli e componenti a due terminali.
    point_mode = resolve_terminal_point_mode(meta)
    point_binary = image_binary
    if point_mode == "three_terminal_structured":
        point_binary = get_three_terminal_working_binary(image_binary, bbox)
    elif meta.get("terminal_strategy") == "one_terminal_by_orientation":
        point_binary = get_one_terminal_working_binary(image_binary, bbox)
    elif point_mode == "two_terminal_side_peak":
        point_binary = get_two_terminal_working_binary(
            image_binary,
            bbox,
            estimated_orientation,
        )

    terminals = []
    for term_def in terminals_def:
        term_name = term_def["name"]
        rel_pos = term_def["relative_position"]

        point_debug = {
            "point_mode": point_mode
        }

        # Se term_def["point"] esiste, la strategia ha gia' prodotto un punto
        # assoluto sull'immagine: non serve applicare un'altra geometria.
        if term_def.get("point") is not None:
            x, y = [round(float(v), 2) for v in term_def["point"]]
            point_debug["point_mode"] = "strategy_absolute_point"
            point_debug["point_source"] = "term_def.point"

            if term_def.get("point_debug") is not None:
                point_debug.update(term_def["point_debug"])

        elif point_mode == "three_terminal_structured":
            # Componenti a 3 terminali: localizza terminale singolo e coppia
            # ortogonale coerente con orientazione/lati rilevati.
            point, structured_debug = geom_terminal_point_three_terminal(
                point_binary,
                bbox,
                estimated_orientation,
                rel_pos
            )
            if component.get("class_name") == "NPN_Transistor":
                point, snap_debug = snap_bjt_pair_terminal_to_lateral_wire(
                    point_binary,
                    bbox,
                    estimated_orientation,
                    rel_pos,
                    point,
                )
                if snap_debug is not None:
                    structured_debug.update(snap_debug)
            x, y = point
            point_debug.update(structured_debug)

        elif point_mode == OPAMP_POINT_MODE:
            # Opamp: gestisce terminali obbligatori (in1, in2, out) e pin
            # ausiliari opzionali (aux1, aux2) quando sono presenti nel disegno.
            point, opamp_debug = geom_terminal_point_opamp(
                image_binary,
                bbox,
                estimated_orientation,
                term_def,
            )
            x, y = point
            point_debug.update(opamp_debug)

        elif point_mode == "two_terminal_side_peak":
            # Componenti a due terminali con side-peak: il lato e' noto, ma il
            # punto preciso lungo quel lato viene cercato sui pixel foreground.
            # Alcuni simboli hanno pero' eccezioni dedicate.
            if component.get("class_name") == "Diode":
                # Diode: il centro del lato e' piu' stabile del picco, perche'
                # il simbolo interno puo' creare falsi massimi.
                x, y = geom_terminal_point_from_bbox(bbox, rel_pos)
                point_debug["point_mode"] = "two_terminal_axis_center"
                point_debug["anchor_offset_ratio"] = 0.5
            elif component.get("class_name") == "GND":
                # GND usa il centro del lato superiore per non farsi influenzare
                # da testo o linee vicine.
                x, y = geom_terminal_point_from_bbox(bbox, rel_pos)
                point_debug["point_mode"] = "one_terminal_axis_center"
                point_debug["anchor_offset_ratio"] = 0.5
            elif component.get("class_name") == "LED":
                # LED: usa regole piu' restrittive per evitare che frecce e
                # simboli interni vengano scambiati per terminali.
                if estimated_orientation == "vertical" and rel_pos in {"top", "bottom"}:
                    lead_x, peak_debug = _select_led_vertical_lead_x(image_binary, bbox)
                    if lead_x is None:
                        x, y = geom_terminal_point_from_bbox(bbox, rel_pos)
                        peak_debug["fallback_point_mode"] = "led_vertical_axis_center"
                        peak_debug["anchor_offset_ratio"] = 0.5
                    else:
                        _, y = geom_terminal_point_from_bbox(bbox, rel_pos)
                        x = round(float(lead_x), 2)
                else:
                    scan_window = _get_led_side_peak_scan_window(
                        bbox,
                        estimated_orientation,
                        rel_pos,
                    )
                    if scan_window is not None:
                        scan_start, scan_end, center_coord = scan_window
                        point, peak_debug = geom_terminal_point_by_side_peak(
                            point_binary,
                            bbox,
                            rel_pos,
                            scan_start=scan_start,
                            scan_end=scan_end,
                            center_coord=center_coord,
                        )
                        peak_debug["scan_window_mode"] = "led_center_axis_window"
                        peak_debug["scan_window_ratio"] = float(LED_SIDE_PEAK_AXIS_SCAN_RATIO)
                    else:
                        point, peak_debug = geom_terminal_point_by_side_peak(
                            point_binary,
                            bbox,
                            rel_pos
                        )
                    x, y = point
                point_debug.update(peak_debug)
            else:
                # Caso generale: cerca il massimo foreground lungo il lato.
                point, peak_debug = geom_terminal_point_by_side_peak(
                    point_binary,
                    bbox,
                    rel_pos
                )
                x, y = point
                point_debug.update(peak_debug)

        else:
            # Fallback comune: prende il centro del lato del bbox oppure, se il
            # metadata fornisce anchor_offset_ratio, un punto ancorato lungo il
            # lato con posizione relativa fissata.
            anchor_offset_ratio = term_def.get("anchor_offset_ratio")
            if anchor_offset_ratio is not None:
                x, y = geom_terminal_point_from_bbox_with_anchor(
                    bbox,
                    rel_pos,
                    anchor_offset_ratio,
                )
                point_debug["point_mode"] = "bbox_side_anchor_ratio"
                point_debug["anchor_offset_ratio"] = round(float(anchor_offset_ratio), 4)
            else:
                x, y = geom_terminal_point_from_bbox(bbox, rel_pos)

                x1, y1, x2, y2 = bbox
                width = max(x2 - x1, 1e-6)
                height = max(y2 - y1, 1e-6)

                if rel_pos in {"top", "bottom"}:
                    point_debug["anchor_offset_ratio"] = round((x - x1) / width, 4)
                else:
                    point_debug["anchor_offset_ratio"] = round((y - y1) / height, 4)

        if (
            component.get("class_name") == "Motor"
            and estimated_orientation == "vertical"
            and rel_pos == "bottom"
        ):
            # Motor verticale: il contatto inferiore puo' essere piu' affidabile
            # cercandolo come side-peak sul lato bottom.
            motor_point, motor_debug = geom_terminal_point_by_side_peak(
                point_binary,
                bbox,
                "bottom",
            )
            x, y = motor_point
            rel_pos = "bottom"
            point_debug.update(motor_debug)
            point_debug["point_mode"] = "motor_vertical_lower_bottom_contact"

        # Creazione del terminale interno.
        # Qui salviamo sia identificativi stabili sia debug geometrico; piu'
        # avanti lo step 03 filtrera' i campi debug nel JSON pubblico.
        terminals.append({
            "terminal_id": f"{instance_id}:{term_name}",
            "instance_id": instance_id,
            "component_class_id": class_id,
            "component_class_name": component.get("class_name"),
            "name": term_name,
            "display_name": term_name,
            "display_terminal_id": f"{instance_id}:{term_name}",
            "relative_position": rel_pos,
            "estimated_orientation": estimated_orientation,
            "estimated_connection_side": connected_side,
            "terminal_point_mode": point_mode,
            "terminal_point_debug": point_debug,
            "x": x,
            "y": y,
        })

    if meta.get("terminal_strategy") == "integrated_circuit_wire_contacts":
        # Gli IC hanno terminali gia' legati ai contatti fisici/pin: la semantica
        # dei pin viene arricchita dopo con OCR, non con le regole generiche
        # dei componenti a due terminali.
        return terminals, estimated_orientation, connected_side, side_scores

    if point_mode == "three_terminal_structured":
        # Transistor/MOSFET: assegna ruoli semantici coerenti con geometria e
        # metadata, per esempio base/collector/emitter o gate/source/drain.
        terminals = resolve_three_terminal_semantics(
            point_binary,
            bbox,
            estimated_orientation,
            terminals,
            meta,
        )
    else:
        # Tutti gli altri componenti passano dal resolver semantico generico:
        # polarita', positivo/negativo, anodo/catodo, lato superiore/inferiore.
        terminals = resolve_two_terminal_semantics(
            image_binary,
            bbox,
            estimated_orientation,
            terminals,
            meta,
        )
    return terminals, estimated_orientation, connected_side, side_scores
