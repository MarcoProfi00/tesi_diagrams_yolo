import cv2

from .config import (
    LINK_COLOR,
    MATCHED_TERMINAL_COLOR,
    PROBLEM_TERMINAL_COLOR,
    SNAP_POINT_COLOR,
    SNAP_RADIUS,
    SUSPICIOUS_TERMINAL_COLOR,
    TERMINAL_RADIUS,
    TEXT_COLOR,
    TEXT_FONT_SCALE,
    TEXT_OUTLINE_COLOR,
    TEXT_OUTLINE_THICKNESS,
    TEXT_THICKNESS,
    UNMATCHED_TERMINAL_COLOR,
)


# =========================================================
# DEBUG VISIVO
# =========================================================

# Disegna testo con contorno, utile per rendere leggibili le etichette.
def draw_outlined_text(
    image,
    text,
    origin,
    color=TEXT_COLOR,
    outline_color=TEXT_OUTLINE_COLOR,
    font_scale=TEXT_FONT_SCALE,
    thickness=TEXT_THICKNESS,
    outline_thickness=TEXT_OUTLINE_THICKNESS,
):
    cv2.putText(
        image,
        text,
        origin,
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        outline_color,
        outline_thickness,
        cv2.LINE_AA,
    )
    cv2.putText(
        image,
        text,
        origin,
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        color,
        thickness,
        cv2.LINE_AA,
    )

# Sceglie il colore del terminale in base allo stato del match/grafo.
# verde = matched
# giallo-arancio acceso = unmatched o unconnected
# arancione = suspicious
def get_terminal_debug_color(match_info: dict, is_problem_terminal=False):
    if is_problem_terminal:
        return PROBLEM_TERMINAL_COLOR
    if match_info.get("matched_label") is None:
        return UNMATCHED_TERMINAL_COLOR
    if match_info.get("is_suspicious", False):
        return SUSPICIOUS_TERMINAL_COLOR
    return MATCHED_TERMINAL_COLOR


def is_problem_terminal(terminal_id, simple_id, problem_terminal_ids):
    if not problem_terminal_ids:
        return False
    return terminal_id in problem_terminal_ids or simple_id in problem_terminal_ids


# Disegna overlay sul diagramma originale.
def draw_terminal_overlay(
    image_bgr,
    terminals,
    terminal_match_debug,
    original_to_simple,
    problem_terminal_ids=None,
):
    out = image_bgr.copy()
    problem_terminal_ids = set(problem_terminal_ids or [])

    for term in terminals:
        terminal_id = term["terminal_id"]
        simple_id = original_to_simple.get(terminal_id, terminal_id)
        info = terminal_match_debug.get(terminal_id, {})

        tx = int(round(term["x"]))
        ty = int(round(term["y"]))
        problem = is_problem_terminal(terminal_id, simple_id, problem_terminal_ids)
        color = get_terminal_debug_color(info, problem)

        cv2.circle(out, (tx, ty), TERMINAL_RADIUS, color, -1)
        cv2.circle(out, (tx, ty), TERMINAL_RADIUS + 1, (0, 0, 0), 1)

        snap_point = info.get("snap_point")
        if snap_point is not None:
            sx, sy = map(int, snap_point)
            cv2.circle(out, (sx, sy), SNAP_RADIUS, SNAP_POINT_COLOR, -1)
            cv2.circle(out, (sx, sy), SNAP_RADIUS + 1, (255, 255, 255), 1)
            cv2.line(out, (tx, ty), (sx, sy), LINK_COLOR, 1)

        label_text = simple_id
        if problem:
            label_text += " [problem]"
        elif info.get("matched_label") is None:
            label_text += " [none]"
        elif info.get("is_suspicious", False):
            label_text += f" [d={info.get('snap_distance')}]"

        text_color = PROBLEM_TERMINAL_COLOR if problem else TEXT_COLOR
        draw_outlined_text(out, label_text, (tx + 8, max(16, ty - 6)), color=text_color)

    return out


# Disegna overlay sullo skeleton, utile per capire se il match cade davvero sul filo.
def draw_skeleton_overlay(
    skeleton_binary,
    terminals,
    terminal_match_debug,
    original_to_simple,
    problem_terminal_ids=None,
):
    out = cv2.cvtColor(skeleton_binary, cv2.COLOR_GRAY2BGR)
    problem_terminal_ids = set(problem_terminal_ids or [])

    for term in terminals:
        terminal_id = term["terminal_id"]
        simple_id = original_to_simple.get(terminal_id, terminal_id)
        info = terminal_match_debug.get(terminal_id, {})

        tx = int(round(term["x"]))
        ty = int(round(term["y"]))
        problem = is_problem_terminal(terminal_id, simple_id, problem_terminal_ids)
        color = get_terminal_debug_color(info, problem)

        cv2.circle(out, (tx, ty), TERMINAL_RADIUS, color, -1)
        cv2.circle(out, (tx, ty), TERMINAL_RADIUS + 1, (255, 255, 255), 1)

        snap_point = info.get("snap_point")
        if snap_point is not None:
            sx, sy = map(int, snap_point)
            cv2.circle(out, (sx, sy), SNAP_RADIUS, SNAP_POINT_COLOR, -1)
            cv2.circle(out, (sx, sy), SNAP_RADIUS + 1, (255, 255, 255), 1)
            cv2.line(out, (tx, ty), (sx, sy), LINK_COLOR, 1)

        label_text = simple_id
        if problem:
            label_text += " [problem]"
        text_color = PROBLEM_TERMINAL_COLOR if problem else TEXT_COLOR
        draw_outlined_text(out, label_text, (tx + 8, max(16, ty - 6)), color=text_color)

    return out
