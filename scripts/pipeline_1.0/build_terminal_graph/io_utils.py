# =========================================================
# UTILITY BASE
# =========================================================
# Carica una immagine binaria da disco.
from pathlib import Path

import cv2
import numpy as np

# Legge l'immagine in scala di grigi.
# Controlla se esiste
# Normalizza con una codifica coerente 255
def load_binary_image(path: Path) -> np.ndarray:
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(
            "Immagine non trovata o non leggibile. "
            f"Path nel JSON: {path}. "
            "Se punta a una pipeline non più esistente, rigenera il passo 04."
        )

    # Normalizziamo a 0/255 per evitare ambiguità.
    return np.where(img > 0, 255, 0).astype(np.uint8)
