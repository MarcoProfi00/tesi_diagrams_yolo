import cv2


def img_count_foreground_pixels(binary, x1, y1, x2, y2):
    h, w = binary.shape[:2]
    x1 = max(0, min(w, x1))
    y1 = max(0, min(h, y1))
    x2 = max(0, min(w, x2))
    y2 = max(0, min(h, y2))
    if x2 <= x1 or y2 <= y1:
        return 0
    return int(cv2.countNonZero(binary[y1:y2, x1:x2]))