"""Utility di input/output per il passo 05."""

from pathlib import Path

import cv2
import numpy as np


def load_binary_image(path: Path) -> np.ndarray:
    """
    Carica una immagine binaria da disco e la normalizza a 0/255.

    Lo step 05 assume che skeleton e maschere siano immagini binarie coerenti.
    Questa funzione evita ambiguita' tra 1/255 o valori intermedi.
    """
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(
            "Immagine non trovata o non leggibile. "
            f"Path nel JSON: {path}. "
            "Se punta a una pipeline non piu' esistente, rigenera il passo 04."
        )

    return np.where(img > 0, 255, 0).astype(np.uint8)
