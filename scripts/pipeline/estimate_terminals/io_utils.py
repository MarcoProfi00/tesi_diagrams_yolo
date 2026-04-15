from pathlib import Path

import cv2
import yaml

from .config import *
# =========================================================
# I/O HELPERS
# =========================================================
def io_load_yaml(path: Path):
    """Gestisce io load yaml all'interno di questo modulo della pipeline."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def io_load_class_metadata(class_terminals_path: Path):
    """Gestisce io load class metadata all'interno di questo modulo della pipeline."""
    data = io_load_yaml(class_terminals_path)
    return {int(k): v for k, v in data.items()}

def img_build_foreground_binary(image_bgr):
    """Gestisce img build foreground binary all'interno di questo modulo della pipeline."""
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return binary
