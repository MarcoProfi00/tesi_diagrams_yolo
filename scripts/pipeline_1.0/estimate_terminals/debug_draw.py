import cv2

from .config import *
# =========================================================
# DEBUG DRAWING
# =========================================================
# Draw terminals.
def draw_terminals(image_bgr, components, terminals):
    out = image_bgr.copy()
    comp_box_color = (220, 170, 40)
    term_box_color = (58, 92, 190)
    state_box_colors = {
        "open": (30, 120, 230),
        "closed": (55, 150, 65),
        "unknown": (120, 120, 120),
    }
    text_color = (35, 35, 35)
    label_bg_color = (245, 245, 245)
    font = cv2.FONT_HERSHEY_SIMPLEX
    comp_font_scale = 0.46
    term_font_scale = 0.43
    state_font_scale = 0.43
    font_thickness = 1
    box_thickness = 2
    padding_x = 5
    padding_y = 4

    # Draw label.
    def draw_label(text, anchor_x, anchor_y, border_color, font_scale):
        (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, font_thickness)
        label_x1 = max(0, int(anchor_x))
        label_y2 = max(text_h + 2 * padding_y + baseline, int(anchor_y))
        label_y1 = max(0, label_y2 - (text_h + 2 * padding_y + baseline))
        label_x2 = min(out.shape[1] - 1, label_x1 + text_w + 2 * padding_x)

        overlay = out.copy()
        cv2.rectangle(overlay, (label_x1, label_y1), (label_x2, label_y2), label_bg_color, -1)
        cv2.addWeighted(overlay, 0.88, out, 0.12, 0, out)
        cv2.rectangle(out, (label_x1, label_y1), (label_x2, label_y2), border_color, 1)
        cv2.putText(
            out,
            text,
            (label_x1 + padding_x, label_y2 - baseline - padding_y),
            font,
            font_scale,
            text_color,
            font_thickness,
            cv2.LINE_AA,
        )

    # Draw semantic state labels, when the component estimator produced one.
    # This keeps the 03 debug image aligned with the JSON output without
    # hardcoding any specific class: ogni componente con "state" viene annotato.
    def draw_component_state(comp, x1, y2):
        state = comp.get("state")
        if not state:
            return

        confidence = comp.get("state_confidence")
        if isinstance(confidence, (int, float)):
            label = f"state: {state} ({confidence:.2f})"
        else:
            label = f"state: {state}"

        state_color = state_box_colors.get(state, state_box_colors["unknown"])
        draw_label(label, x1, y2 + 18, state_color, state_font_scale)

    for comp in components:
        x1, y1, x2, y2 = map(int, comp["bbox"])
        label = comp.get("instance_id", "N/A")
        if comp.get("estimated_orientation"):
            label = f"{label} ({comp['estimated_orientation'][0]})"
        cv2.rectangle(out, (x1, y1), (x2, y2), comp_box_color, box_thickness)
        draw_label(label, x1, y1, comp_box_color, comp_font_scale)
        draw_component_state(comp, x1, y2)

    for term in terminals:
        x = int(round(term["x"]))
        y = int(round(term["y"]))
        label = term.get("display_terminal_id", term["terminal_id"])
        cv2.circle(out, (x, y), TERMINAL_RADIUS, (0, 0, 255), -1)
        draw_label(label, x + 8, max(y - 8, 0), term_box_color, term_font_scale)
    return out


# =========================================================
# IC OCR SUMMARY DEBUG DRAWING
# =========================================================
# Draw a clean OCR summary image for Integrated_Circuit components.
def draw_ic_ocr_summary(image_bgr, components):
    """
    Disegna una seconda immagine debug, dedicata SOLO all'OCR del nome IC.

    Versione semplificata e piu' leggibile:
      - bbox YOLO del componente in grigio;
      - body_bbox raffinato in cyan;
      - bbox del testo OCR selezionato con colore in base alla confidenza;
      - label corta del tipo:
            11.1: NE555 (0.91) [inner/tess]

    Non disegna:
      - tutte le ROI OCR;
      - tutti i candidati;
      - parole scartate;
      - pin number / pin label.

    Obiettivo pratico:
      aprire *_ic_ocr.jpg e capire in pochi secondi:
        1. qual e' il body_bbox usato;
        2. quale testo e' stato scelto;
        3. quanto e' affidabile;
        4. se un falso IC e' stato riconosciuto come display 7 segmenti.
    """
    out = image_bgr.copy()

    # ---------------------------------------------------------
    # Colori BGR OpenCV.
    # Nota: OpenCV usa BGR, non RGB.
    # ---------------------------------------------------------
    yolo_bbox_color = (170, 170, 170)       # grigio: bbox YOLO grezzo
    body_bbox_color = (255, 220, 0)         # cyan/azzurro: body_bbox raffinato
    strong_ocr_color = (60, 180, 75)        # verde: OCR forte
    medium_ocr_color = (0, 220, 255)        # giallo: OCR medio
    weak_ocr_color = (0, 165, 255)          # arancione: OCR debole/incerto
    very_weak_ocr_color = (0, 0, 255)       # rosso: OCR molto debole o assente
    display_color = (180, 60, 180)          # viola: display 7 segmenti / non-IC marking
    pin_number_color = (40, 190, 40)        # verde: numero pin OCR
    pin_label_color = (210, 80, 210)        # magenta: label pin OCR

    text_color = (35, 35, 35)
    label_bg_color = (245, 245, 245)

    font = cv2.FONT_HERSHEY_SIMPLEX
    label_font_scale = 0.45
    small_font_scale = 0.38
    font_thickness = 1
    padding_x = 5
    padding_y = 4

    # ---------------------------------------------------------
    # Helper: clamp bbox dentro l'immagine.
    # Serve per evitare errori se qualche bbox OCR esce leggermente dai limiti.
    # ---------------------------------------------------------
    def clamp_bbox(bbox):
        if not bbox:
            return None

        h, w = out.shape[:2]
        x1, y1, x2, y2 = bbox
        x1 = int(max(0, min(w - 1, round(float(x1)))))
        y1 = int(max(0, min(h - 1, round(float(y1)))))
        x2 = int(max(0, min(w - 1, round(float(x2)))))
        y2 = int(max(0, min(h - 1, round(float(y2)))))

        if x2 < x1:
            x1, x2 = x2, x1
        if y2 < y1:
            y1, y2 = y2, y1

        return x1, y1, x2, y2

    # ---------------------------------------------------------
    # Helper: recupera il body_bbox dell'IC.
    # Lo cerchiamo in piu' posti per essere robusti rispetto al formato JSON:
    #   1. comp["body_bbox"]
    #   2. comp["connection_side_scores"]["body_bbox"]
    #   3. terminal_point_debug["body_bbox"]
    #   4. fallback: bbox YOLO
    # ---------------------------------------------------------
    def get_body_bbox(comp):
        body_bbox = comp.get("body_bbox")
        if body_bbox:
            return clamp_bbox(body_bbox)

        side_scores = comp.get("connection_side_scores") or {}
        body_bbox = side_scores.get("body_bbox")
        if body_bbox:
            return clamp_bbox(body_bbox)

        for term in comp.get("terminals", []):
            point_debug = term.get("terminal_point_debug") or {}
            body_bbox = point_debug.get("body_bbox")
            if body_bbox:
                return clamp_bbox(body_bbox)

        return clamp_bbox(comp.get("bbox"))

    # ---------------------------------------------------------
    # Helper: label con sfondo semi-trasparente.
    # Rispetto alla versione precedente, qui proviamo anche a tenere
    # la label dentro l'immagine in orizzontale, cosi non viene tagliata.
    # ---------------------------------------------------------
    def draw_label(text, anchor_x, anchor_y, border_color, font_scale=label_font_scale):
        if not text:
            return

        (text_w, text_h), baseline = cv2.getTextSize(
            text,
            font,
            font_scale,
            font_thickness,
        )

        h, w = out.shape[:2]
        label_w = text_w + 2 * padding_x
        label_h = text_h + 2 * padding_y + baseline

        # Tieni la label dentro l'immagine, soprattutto a destra.
        label_x1 = int(round(anchor_x))
        label_x1 = max(0, min(w - 1, label_x1))
        if label_x1 + label_w >= w:
            label_x1 = max(0, w - label_w - 1)

        label_y2 = max(label_h, int(round(anchor_y)))
        label_y2 = min(h - 1, label_y2)
        label_y1 = max(0, label_y2 - label_h)
        label_x2 = min(w - 1, label_x1 + label_w)

        overlay = out.copy()
        cv2.rectangle(
            overlay,
            (label_x1, label_y1),
            (label_x2, label_y2),
            label_bg_color,
            -1,
        )
        cv2.addWeighted(overlay, 0.88, out, 0.12, 0, out)
        cv2.rectangle(out, (label_x1, label_y1), (label_x2, label_y2), border_color, 1)
        cv2.putText(
            out,
            text,
            (label_x1 + padding_x, label_y2 - baseline - padding_y),
            font,
            font_scale,
            text_color,
            font_thickness,
            cv2.LINE_AA,
        )

    def format_conf(value):
        """Formatta la confidenza OCR in modo compatto."""
        if isinstance(value, (int, float)):
            return f"{float(value):.2f}"
        return "n/a"

    def confidence_value(value):
        """Ritorna la confidenza come float oppure None."""
        if isinstance(value, (int, float)):
            return float(value)
        return None

    def ocr_color_for_conf(confidence):
        """
        Colore del risultato OCR in base alla confidenza.

        Soglie volutamente semplici:
          >= 0.70  verde   = buono
          >= 0.40  giallo  = medio
          >= 0.25  arancio = debole/incerto
          <  0.25  rosso   = molto debole
        """
        conf = confidence_value(confidence)
        if conf is None:
            return weak_ocr_color
        if conf >= 0.70:
            return strong_ocr_color
        if conf >= 0.40:
            return medium_ocr_color
        if conf >= 0.25:
            return weak_ocr_color
        return very_weak_ocr_color

    def source_short(source_region):
        """Abbrevia il nome della regione OCR per tenere la label corta."""
        if not source_region:
            return "src?"

        source_region = str(source_region)
        mapping = {
            "body_inner": "inner",
            "above_body": "top",
            "below_body": "bottom",
            "left_of_body": "left",
            "right_of_body": "right",
            "expanded_bbox": "exp",
            "body_top_marking": "top",
            "body_top_marking_tight": "top",
            "body_line_1": "line1",
            "body_line_2": "line2",
            "body_line_3": "line3",
        }

        if source_region in mapping:
            return mapping[source_region]

        # Fallback compatto: togli prefissi lunghi e limita la lunghezza.
        short = source_region.replace("body_", "")
        short = short.replace("marking_", "")
        return short[:10]

    def engine_short(engine):
        """Abbrevia il nome del motore OCR."""
        if not engine:
            return "ocr?"
        engine = str(engine).lower()
        if "tesseract" in engine:
            return "tess"
        if "easy" in engine:
            return "easy"
        return engine[:6]

    def mode_short(mode):
        """Abbrevia la modalita' OCR, se presente."""
        if not mode:
            return None
        mode = str(mode).lower()
        if mode.startswith("fast"):
            return "fast"
        if mode.startswith("deep"):
            return "deep"
        return mode[:6]

    def compact_ocr_label(instance_id, marking, confidence, source_region, engine, ocr_mode):
        """
        Costruisce una label breve.

        Esempi:
          11.1: TDA7000 (0.75) [inner/tess]
          11.1: TPS63061 (0.36) [top/tess] ?
        """
        conf = confidence_value(confidence)
        conf_text = format_conf(confidence)
        src = source_short(source_region)
        eng = engine_short(engine)
        mode = mode_short(ocr_mode)

        parts = [src, eng]
        if mode:
            parts.append(mode)

        suffix = "?" if conf is not None and conf < 0.40 else ""
        return f"{instance_id}: {marking} ({conf_text}) [{'/' .join(parts)}] {suffix}".strip()

    def draw_pin_ocr_boxes(comp):
        """
        Disegna i valori finali selezionati per pin_number e pin_label_text.

        Non usiamo il bbox OCR come riferimento principale: alcune label possono
        essere normalizzate o ricostruite, quindi il bbox grezzo potrebbe
        circondare una parola diversa dal valore finale salvato nel JSON.
        """
        def pin_label_anchor(term, line_index):
            x = int(round(float(term.get("x", 0.0))))
            y = int(round(float(term.get("y", 0.0))))
            side = term.get("relative_position")
            line_gap = 17

            if side == "left":
                return max(0, x - 74), max(18, y - 8 + line_index * line_gap)
            if side == "right":
                return x + 10, max(18, y - 8 + line_index * line_gap)
            if side == "top":
                return max(0, x - 28), max(18, y - 24 - line_index * line_gap)
            if side == "bottom":
                return max(0, x - 28), y + 22 + line_index * line_gap
            return x + 10, y + 10 + line_index * line_gap

        for term in comp.get("terminals", []):
            pin_number = term.get("pin_number")
            pin_label = term.get("pin_label_text")
            line_index = 0

            if pin_number not in (None, ""):
                ax, ay = pin_label_anchor(term, line_index)
                draw_label(
                    f"pin {pin_number}",
                    ax,
                    ay,
                    pin_number_color,
                    small_font_scale,
                )
                line_index += 1

            if pin_label not in (None, ""):
                ax, ay = pin_label_anchor(term, line_index)
                draw_label(
                    str(pin_label),
                    ax,
                    ay,
                    pin_label_color,
                    small_font_scale,
                )

    # ---------------------------------------------------------
    # Disegno di ogni Integrated_Circuit.
    # ---------------------------------------------------------
    for comp in components:
        if comp.get("class_name") != "Integrated_Circuit":
            continue

        instance_id = comp.get("instance_id", "IC")
        yolo_bbox = clamp_bbox(comp.get("bbox"))
        body_bbox = get_body_bbox(comp)

        if yolo_bbox:
            x1, y1, x2, y2 = yolo_bbox
            cv2.rectangle(out, (x1, y1), (x2, y2), yolo_bbox_color, 1)
        else:
            # Se manca anche il bbox YOLO, non abbiamo un punto affidabile dove disegnare.
            continue

        if body_bbox:
            bx1, by1, bx2, by2 = body_bbox
            cv2.rectangle(out, (bx1, by1), (bx2, by2), body_bbox_color, 2)
        else:
            bx1, by1, bx2, by2 = x1, y1, x2, y2

        marking = comp.get("ic_marking")
        confidence = comp.get("ic_marking_confidence")
        source_region = comp.get("ic_marking_source_region")
        engine = comp.get("ic_marking_engine")
        ocr_mode = comp.get("ic_ocr_mode")
        candidate_count = (comp.get("ic_ocr_debug") or {}).get("candidate_count")
        component_subtype = comp.get("component_subtype")
        display_type = comp.get("display_type")

        is_display = (
            component_subtype == "seven_segment_display"
            or display_type == "seven_segment"
        )

        # -----------------------------------------------------
        # Caso 1: display a 7 segmenti riconosciuto come falso IC.
        # -----------------------------------------------------
        if is_display:
            label = f"{instance_id}: DISPLAY_7SEG"
            draw_label(label, bx1, max(by1 - 6, 0), display_color, label_font_scale)
            cv2.rectangle(out, (bx1, by1), (bx2, by2), display_color, 2)
            draw_pin_ocr_boxes(comp)
            continue

        # -----------------------------------------------------
        # Caso 2: marking IC trovato.
        # Colore e label dipendono dalla confidenza OCR.
        # -----------------------------------------------------
        if marking:
            result_color = ocr_color_for_conf(confidence)

            selected_bbox = clamp_bbox(comp.get("ic_marking_bbox"))
            if selected_bbox:
                tx1, ty1, tx2, ty2 = selected_bbox
                cv2.rectangle(out, (tx1, ty1), (tx2, ty2), result_color, 2)

            label = compact_ocr_label(
                instance_id=instance_id,
                marking=marking,
                confidence=confidence,
                source_region=source_region,
                engine=engine,
                ocr_mode=ocr_mode,
            )
            draw_label(label, bx1, max(by1 - 6, 0), result_color, label_font_scale)
            draw_pin_ocr_boxes(comp)
            continue

        # -----------------------------------------------------
        # Caso 3: nessun marking trovato.
        # Label corta: non serve riportare tutti i dettagli OCR nell'immagine.
        # Quelli restano nel JSON.
        # -----------------------------------------------------
        if candidate_count is not None:
            label = f"{instance_id}: OCR NONE (cand={candidate_count})"
        else:
            label = f"{instance_id}: OCR NONE"

        draw_label(label, bx1, max(by1 - 6, 0), very_weak_ocr_color, label_font_scale)
        cv2.rectangle(out, (bx1, by1), (bx2, by2), very_weak_ocr_color, 1)
        draw_pin_ocr_boxes(comp)

    # Piccola legenda compatta in alto a sinistra.
    draw_label(
        "IC OCR: cyan=body, gray=YOLO, OCR box=marking | green pin number, magenta pin label",
        8,
        24,
        body_bbox_color,
        small_font_scale,
    )

    return out
