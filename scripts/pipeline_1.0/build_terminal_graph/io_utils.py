# =========================================================
# UTILITY BASE
# =========================================================
# Carica una immagine binaria da disco.
from pathlib import Path

import cv2
import numpy as np


def resolve_existing_image_path(path: Path) -> Path:
    if path.exists():
        return path

    # Some historical step-04 JSON files were moved between pipeline folders
    # without rewriting absolute debug paths.  Prefer the matching pipeline1.0
    # artifact when the original pipeline2.0 path no longer exists.
    path_text = str(path)
    if "outputs\\pipeline2.0\\" in path_text:
        fallback = Path(path_text.replace("outputs\\pipeline2.0\\", "outputs\\pipeline1.0\\"))
        if fallback.exists():
            return fallback

    return path


# Legge img in Grayscale
# Controlla se esiste
# Normalizza con una codifica coerente 255
def load_binary_image(path: Path) -> np.ndarray:
    resolved_path = resolve_existing_image_path(path)
    img = cv2.imread(str(resolved_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Immagine non trovata o non leggibile: {path}")

    # Normalizziamo a 0/255 per evitare ambiguità.
    return np.where(img > 0, 255, 0).astype(np.uint8)
