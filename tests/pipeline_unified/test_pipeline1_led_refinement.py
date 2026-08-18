"""Regressioni visive della distinzione generale tra LED e diodo."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

import cv2


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PIPELINE1_DIR = PROJECT_ROOT / "scripts" / "pipeline_1.0"
STEP01_PATH = PIPELINE1_DIR / "01_detect_components.py"
VERIFICATION_ROOT = PROJECT_ROOT / "experiment_ai" / "verify_json_img"


def load_step01_module():
    """Carica lo step 01 mantenendo disponibili i suoi moduli locali."""
    sys.path.insert(0, str(PIPELINE1_DIR))
    spec = importlib.util.spec_from_file_location("pipeline1_step01_led_test", STEP01_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare lo step 01: {STEP01_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LedRefinementRegressionTests(unittest.TestCase):
    """Protegge esempi reali senza introdurre eccezioni nel codice produttivo."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.step01 = load_step01_module()
        cls.b03_binary = cls._load_binary(
            VERIFICATION_ROOT / "batchB" / "images" / "b03.jpg"
        )

    @classmethod
    def _load_binary(cls, image_path: Path):
        """Carica una fixture e applica la binarizzazione usata dalla pipeline."""
        image = cv2.imread(str(image_path))
        if image is None:
            raise FileNotFoundError(f"Fixture immagine non trovata: {image_path}")
        return cls.step01.img_build_foreground_binary(image)

    def test_real_led_markers_are_preserved(self) -> None:
        """Le due forme di freccia LED gia' supportate restano riconosciute."""
        cases = (
            (
                VERIFICATION_ROOT / "batchA" / "images" / "a03.jpg",
                [505, 109, 561, 239],
            ),
            (
                VERIFICATION_ROOT / "batchA" / "images" / "a07.png",
                [918, 375, 1002, 456],
            ),
        )
        for image_path, diode_box in cases:
            with self.subTest(image=image_path.name):
                image_binary = self._load_binary(image_path)
                self.assertTrue(
                    self.step01.is_led_like_diode_box(image_binary, diode_box)
                )

    def test_b03_diode_labels_are_not_treated_as_led_arrows(self) -> None:
        """Testi e rami attorno ai sei diodi B03 non diventano marker LED."""
        diode_boxes = (
            [420.17, 267.70, 468.00, 317.23],
            [577.32, 602.60, 611.41, 664.98],
            [580.23, 340.97, 613.77, 391.89],
            [581.49, 458.37, 613.33, 514.27],
            [986.26, 396.38, 1017.83, 453.21],
            [987.22, 546.69, 1017.36, 607.65],
        )
        for diode_box in diode_boxes:
            with self.subTest(box=diode_box):
                self.assertFalse(
                    self.step01.is_led_like_diode_box(self.b03_binary, diode_box)
                )


if __name__ == "__main__":
    unittest.main()
