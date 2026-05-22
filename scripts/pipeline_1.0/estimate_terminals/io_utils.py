from pathlib import Path

import cv2
import yaml

from .config import *
# =========================================================
# I/O HELPERS
# =========================================================
# Carica un file YAML.
def io_load_yaml(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# Carica i metadati delle classi indicizzati per class_id.
def io_load_class_metadata(class_terminals_path: Path):
    data = io_load_yaml(class_terminals_path)
    return {int(k): v for k, v in data.items()}

# Costruisce la binary foreground dell'immagine.
def img_build_foreground_binary(image_bgr):
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return binary
