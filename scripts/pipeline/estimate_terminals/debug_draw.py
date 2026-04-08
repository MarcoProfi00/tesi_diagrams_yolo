import cv2

from .config import *
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