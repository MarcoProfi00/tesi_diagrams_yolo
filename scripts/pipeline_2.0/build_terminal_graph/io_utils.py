# =========================================================
# UTILITY BASE
# =========================================================
# Carica una immagine binaria da disco.
from pathlib import Path

import cv2
import numpy as np


def load_binary_image(path: Path) -> np.ndarray:
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Immagine non trovata o non leggibile: {path}")

    # Normalizziamo a 0/255 per evitare ambiguità.
    return np.where(img > 0, 255, 0).astype(np.uint8)