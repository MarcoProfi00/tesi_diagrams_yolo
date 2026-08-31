"""Utility di input/output per il passo 05."""

from pathlib import Path

import cv2
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[3]
LEGACY_PROJECT_PATH_ANCHORS = {
    "data",
    "experiment_ai",
    "metadata",
    "notes",
    "outputs",
    "scripts",
    "tests",
}


def resolve_artifact_path(path: str | Path) -> Path:
    """Riloca nella clone corrente un artefatto salvato da un altro PC."""
    raw_value = str(path)
    expanded = Path(raw_value).expanduser()
    if expanded.is_file():
        return expanded.resolve()

    if not expanded.is_absolute() and "\\" not in raw_value:
        project_candidate = (PROJECT_ROOT / expanded).resolve()
        try:
            project_candidate.relative_to(PROJECT_ROOT)
        except ValueError:
            pass
        else:
            return project_candidate

    # pathlib su macOS/Linux non riconosce come assoluti i vecchi path con
    # drive Windows. Recuperiamo la prima cartella nota interna al progetto e
    # manteniamo comunque il risultato confinato nella root della clone.
    parts = [part for part in raw_value.replace("\\", "/").split("/") if part]
    for index, part in enumerate(parts):
        if part.lower() not in LEGACY_PROJECT_PATH_ANCHORS:
            continue
        candidate = (PROJECT_ROOT / Path(*parts[index:])).resolve()
        try:
            candidate.relative_to(PROJECT_ROOT)
        except ValueError:
            continue
        return candidate

    return expanded


def load_binary_image(path: Path) -> np.ndarray:
    """
    Carica una immagine binaria da disco e la normalizza a 0/255.

    Lo step 05 assume che skeleton e maschere siano immagini binarie coerenti.
    Questa funzione evita ambiguita' tra 1/255 o valori intermedi.
    """
    resolved_path = resolve_artifact_path(path)
    img = cv2.imread(str(resolved_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(
            "Immagine non trovata o non leggibile. "
            f"Path risolto: {resolved_path}. "
            "Se punta a una pipeline non piu' esistente, rigenera il passo 04."
        )

    return np.where(img > 0, 255, 0).astype(np.uint8)
