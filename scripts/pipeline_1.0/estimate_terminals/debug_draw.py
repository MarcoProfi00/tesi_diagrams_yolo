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
    default_terminal_color = (0, 0, 255)      # rosso per terminali standard
    ic_terminal_color = (0, 165, 255)         # arancione per terminali Integrated_Circuit (BGR OpenCV)
    ic_label_border_color = (0, 140, 255)     # arancione leggermente più scuro per label IC
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

    def draw_ic_marking(comp, x1, y1):
        if comp.get("class_name") != "Integrated_Circuit":
            return

        marking = comp.get("ic_marking")
        if not marking:
            return

        confidence = comp.get("ic_marking_confidence")
        if isinstance(confidence, (int, float)):
            label = f"OCR: {marking} ({confidence:.2f})"
        else:
            label = f"OCR: {marking}"

        draw_label(label, x1, y1 + 36, ic_label_border_color, state_font_scale)

    for comp in components:
        x1, y1, x2, y2 = map(int, comp["bbox"])
        label = comp.get("instance_id", "N/A")
        if comp.get("estimated_orientation"):
            label = f"{label} ({comp['estimated_orientation'][0]})"
        cv2.rectangle(out, (x1, y1), (x2, y2), comp_box_color, box_thickness)
        draw_label(label, x1, y1, comp_box_color, comp_font_scale)
        draw_ic_marking(comp, x1, y1)
        draw_component_state(comp, x1, y2)

    for term in terminals:
        x = int(round(term["x"]))
        y = int(round(term["y"]))
        label = term.get("display_terminal_id", term["terminal_id"])

        is_ic_terminal = term.get("component_class_name") == "Integrated_Circuit"
        circle_color = ic_terminal_color if is_ic_terminal else default_terminal_color
        label_border_color = ic_label_border_color if is_ic_terminal else term_box_color
        radius = TERMINAL_RADIUS + 1 if is_ic_terminal else TERMINAL_RADIUS

        cv2.circle(out, (x, y), radius, circle_color, -1)
        cv2.circle(out, (x, y), radius, (0, 0, 0), 1)
        draw_label(label, x + 8, max(y - 8, 0), label_border_color, term_font_scale)
    return out
