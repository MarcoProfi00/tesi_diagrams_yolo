import cv2
import numpy as np


# =========================================================
# STATO SWITCH: OPEN / CLOSED
# =========================================================
# Lo stato dello switch e' una proprieta' del componente, non un arco del
# grafo. Qui stimiamo se i due contatti del simbolo sono connessi dallo
# stesso tratto grafico nel binary locale del componente.

SWITCH_STATE_WINDOW_MARGIN = 10
SWITCH_STATE_CONTACT_RADIUS = 8
SWITCH_STATE_DILATE_ITERATIONS = 1
SWITCH_STATE_AXIS_ALIGN_TOL = 8.0
SWITCH_STATE_AXIS_NEAR_TOUCH_GAP = 6.0


# Clamp di una finestra dentro i limiti immagine.
def _clamp_window(x1, y1, x2, y2, w, h):
    return (
        max(0, min(w, int(round(x1)))),
        max(0, min(h, int(round(y1)))),
        max(0, min(w, int(round(x2)))),
        max(0, min(h, int(round(y2)))),
    )


# Trova il pixel foreground piu' vicino al terminale dentro una piccola ROI.
def _nearest_foreground_point(binary, x, y, radius):
    h, w = binary.shape[:2]
    x1, y1, x2, y2 = _clamp_window(
        float(x) - radius,
        float(y) - radius,
        float(x) + radius + 1,
        float(y) + radius + 1,
        w,
        h,
    )

    roi = binary[y1:y2, x1:x2]
    ys, xs = np.where(roi > 0)
    if len(xs) == 0:
        return None

    abs_xs = xs + x1
    abs_ys = ys + y1
    d2 = (abs_xs - float(x)) ** 2 + (abs_ys - float(y)) ** 2
    best_idx = int(np.argmin(d2))

    return int(abs_xs[best_idx]), int(abs_ys[best_idx]), float(np.sqrt(d2[best_idx]))


# Calcola la distanza minima tra due label locali.
def _min_component_distance(labels, label_a, label_b):
    ys_a, xs_a = np.where(labels == int(label_a))
    ys_b, xs_b = np.where(labels == int(label_b))

    if len(xs_a) == 0 or len(xs_b) == 0:
        return None

    points_a = np.column_stack((xs_a, ys_a)).astype(np.float32)
    best = None

    for xb, yb in zip(xs_b, ys_b):
        d2 = (points_a[:, 0] - float(xb)) ** 2 + (points_a[:, 1] - float(yb)) ** 2
        dist = float(np.sqrt(np.min(d2)))
        if best is None or dist < best:
            best = dist

    return best


# Restituisce i due terminali dello switch ordinati in modo stabile.
def _get_switch_terminal_pair(component):
    terminals = component.get("terminals", [])
    if len(terminals) != 2:
        return None

    return sorted(terminals, key=lambda term: str(term.get("terminal_id", "")))


def _terminals_are_axis_aligned(term_a, term_b):
    side_a = str(term_a.get("relative_position") or "")
    side_b = str(term_b.get("relative_position") or "")
    x_a = float(term_a.get("x", 0.0))
    y_a = float(term_a.get("y", 0.0))
    x_b = float(term_b.get("x", 0.0))
    y_b = float(term_b.get("y", 0.0))
    tol = float(SWITCH_STATE_AXIS_ALIGN_TOL)

    if {side_a, side_b} == {"left", "right"}:
        return abs(y_a - y_b) <= tol
    if {side_a, side_b} == {"top", "bottom"}:
        return abs(x_a - x_b) <= tol

    return False


# Stima open/closed per uno switch.
def estimate_switch_open_closed_state(binary, component):
    terminals = _get_switch_terminal_pair(component)
    bbox = component.get("bbox")

    if terminals is None or not bbox or len(bbox) != 4:
        return {
            "state": "unknown",
            "confidence": 0.0,
            "debug": {
                "state_strategy": "switch_open_closed",
                "reason": "missing_two_terminals_or_bbox",
            },
        }

    h, w = binary.shape[:2]
    x1, y1, x2, y2 = map(float, bbox)
    margin = float(SWITCH_STATE_WINDOW_MARGIN)
    wx1, wy1, wx2, wy2 = _clamp_window(x1 - margin, y1 - margin, x2 + margin, y2 + margin, w, h)

    local = np.where(binary[wy1:wy2, wx1:wx2] > 0, 255, 0).astype(np.uint8)
    if SWITCH_STATE_DILATE_ITERATIONS > 0:
        kernel = np.ones((3, 3), dtype=np.uint8)
        local = cv2.dilate(local, kernel, iterations=SWITCH_STATE_DILATE_ITERATIONS)

    _, labels, _, _ = cv2.connectedComponentsWithStats(local, connectivity=8)

    contact_infos = []
    for terminal in terminals:
        nearest = _nearest_foreground_point(
            local,
            float(terminal["x"]) - wx1,
            float(terminal["y"]) - wy1,
            SWITCH_STATE_CONTACT_RADIUS,
        )

        if nearest is None:
            contact_infos.append({
                "terminal_id": terminal.get("terminal_id"),
                "label": None,
                "point": None,
                "distance": None,
            })
            continue

        px, py, dist = nearest
        contact_infos.append({
            "terminal_id": terminal.get("terminal_id"),
            "label": int(labels[py, px]),
            "point": [int(px + wx1), int(py + wy1)],
            "distance": round(float(dist), 3),
        })

    label_a = contact_infos[0]["label"]
    label_b = contact_infos[1]["label"]

    if label_a is None or label_b is None or label_a == 0 or label_b == 0:
        state = "unknown"
        confidence = 0.0
        gap = None
        reason = "missing_contact_foreground"
    elif int(label_a) == int(label_b):
        state = "closed"
        confidence = 0.95
        gap = 0.0
        reason = "contacts_share_connected_component"
    else:
        gap = _min_component_distance(labels, int(label_a), int(label_b))
        if (
            gap is not None
            and float(gap) <= float(SWITCH_STATE_AXIS_NEAR_TOUCH_GAP)
            and _terminals_are_axis_aligned(terminals[0], terminals[1])
        ):
            state = "closed"
            confidence = 0.75
            reason = "axis_aligned_contacts_nearly_touch"
        else:
            state = "open"
            confidence = min(0.95, 0.55 + float(gap or 0.0) / 30.0)
            reason = "contacts_on_separate_connected_components"

    return {
        "state": state,
        "confidence": round(float(confidence), 4),
        "debug": {
            "state_strategy": "switch_open_closed",
            "reason": reason,
            "window": [int(wx1), int(wy1), int(wx2), int(wy2)],
            "contact_radius": int(SWITCH_STATE_CONTACT_RADIUS),
            "dilate_iterations": int(SWITCH_STATE_DILATE_ITERATIONS),
            "axis_align_tol": float(SWITCH_STATE_AXIS_ALIGN_TOL),
            "axis_near_touch_gap_threshold": float(SWITCH_STATE_AXIS_NEAR_TOUCH_GAP),
            "contacts": contact_infos,
            "component_gap": None if gap is None else round(float(gap), 3),
        },
    }
