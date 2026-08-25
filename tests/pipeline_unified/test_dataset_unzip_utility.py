"""Regressioni del layout usato dagli script dataset storici."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest
import zipfile


PROJECT_ROOT = Path(__file__).resolve().parents[2]
UNZIP_SCRIPT = PROJECT_ROOT / "scripts" / "utils" / "unzip_dataset.py"


def load_unzip_module():
    spec = importlib.util.spec_from_file_location("dataset_unzip_utility", UNZIP_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare lo script: {UNZIP_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DatasetUnzipUtilityTests(unittest.TestCase):
    """Mantiene coerenti archivio, estrazione e consumer del dataset RGB."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.utility = load_unzip_module()

    def test_archive_extracts_under_its_stem(self) -> None:
        """Il layout estratto coincide con quello cercato dagli altri script."""
        self.assertEqual(
            self.utility.OUT_DIR,
            (
                PROJECT_ROOT
                / "data"
                / "datasets"
                / "dataset_v3"
                / "rf_yolo_1024_rgb"
            ),
        )

    def test_versioned_archive_has_safe_expected_layout(self) -> None:
        """Il controllo preventivo accetta il vero ZIP senza estrarlo."""
        with zipfile.ZipFile(self.utility.SRC_ZIP, "r") as archive:
            self.utility.validate_members(archive.infolist())

    def test_v1_rgb_archive_infers_the_directory_used_by_consumers(self) -> None:
        """L'archivio senza wrapper viene estratto sotto il proprio stem."""
        source = (
            PROJECT_ROOT
            / "data"
            / "datasets"
            / "dataset_v1"
            / "rf_yolov7_1024_rgb_v1.zip"
        )
        with zipfile.ZipFile(source, "r") as archive:
            prefix = self.utility.validate_members(archive.infolist(), source.parent)

        self.assertEqual(prefix, Path())
        self.assertEqual(
            self.utility.infer_output_directory(source, prefix),
            source.with_suffix(""),
        )

    def test_wrapped_archive_avoids_a_duplicate_stem_directory(self) -> None:
        """Uno ZIP gia' avvolto nella cartella dataset si estrae nel parent."""
        source = (
            PROJECT_ROOT
            / "data"
            / "datasets"
            / "dataset_v1"
            / "rf_yolov7_1024_gray_v1.zip"
        )
        with zipfile.ZipFile(source, "r") as archive:
            prefix = self.utility.validate_members(archive.infolist(), source.parent)

        self.assertEqual(prefix, Path(source.stem))
        self.assertEqual(
            self.utility.infer_output_directory(source, prefix),
            source.parent,
        )

    def test_parent_traversal_is_rejected(self) -> None:
        """Un membro ZIP non puo' scrivere fuori dalla destinazione."""
        malicious = zipfile.ZipInfo("../escape.txt")
        with self.assertRaisesRegex(ValueError, "Path non sicuro"):
            self.utility.validate_members([malicious])


if __name__ == "__main__":
    unittest.main()
