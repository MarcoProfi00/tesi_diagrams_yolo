"""Test rapidi del comando ``graph`` senza avviare YOLO."""

from __future__ import annotations

from contextlib import contextmanager
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
import uuid


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LAUNCHER_PATH = PROJECT_ROOT / "scripts" / "pipeline_unified" / "run_pipeline.py"
TEST_TEMP_ROOT = PROJECT_ROOT / "outputs" / ".test_tmp"
TEST_TEMP_ROOT.mkdir(parents=True, exist_ok=True)


@contextmanager
def writable_test_directory():
    """Crea una directory temporanea scrivibile dentro il workspace."""
    path = TEST_TEMP_ROOT / f"case_{uuid.uuid4().hex}"
    path.mkdir(parents=True)
    try:
        yield path
    finally:
        # Il target deriva sempre da TEST_TEMP_ROOT e da un UUID locale.
        shutil.rmtree(path)


def load_launcher_module():
    """Carica il launcher da file senza richiedere un package installato."""
    spec = importlib.util.spec_from_file_location("pipeline_unified_launcher", LAUNCHER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare il launcher: {LAUNCHER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GraphSelectionTests(unittest.TestCase):
    """Verifica la selezione generale di una immagine o di un batch."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.launcher = load_launcher_module()

    def test_discover_and_select_one_circuit(self) -> None:
        """Un identificativo seleziona soltanto l'immagine con lo stesso stem."""
        with writable_test_directory() as input_dir:
            (input_dir / "a01.jpg").write_bytes(b"a01")
            (input_dir / "b02.png").write_bytes(b"b02")
            (input_dir / "note.txt").write_text("ignorato", encoding="utf-8")

            available = self.launcher.discover_images(input_dir)
            selected = self.launcher.select_images(available, "b02", False)

            self.assertEqual(sorted(available), ["a01", "b02"])
            self.assertEqual(list(selected), ["b02"])

    def test_select_all_keeps_every_supported_image(self) -> None:
        """La selezione batch conserva tutte e sole le immagini supportate."""
        with writable_test_directory() as input_dir:
            (input_dir / "a01.jpg").write_bytes(b"a01")
            (input_dir / "a02.webp").write_bytes(b"a02")

            available = self.launcher.discover_images(input_dir)
            selected = self.launcher.select_images(available, None, True)

            self.assertEqual(sorted(selected), ["a01", "a02"])

    def test_duplicate_stems_are_rejected(self) -> None:
        """Due estensioni con lo stesso stem non possono indicare due circuiti."""
        with writable_test_directory() as input_dir:
            (input_dir / "a01.jpg").write_bytes(b"jpg")
            (input_dir / "a01.png").write_bytes(b"png")

            with self.assertRaisesRegex(ValueError, "Due immagini"):
                self.launcher.discover_images(input_dir)


class GraphCliTests(unittest.TestCase):
    """Verifica il contratto CLI senza produrre output di pipeline."""

    def test_graph_dry_run_does_not_create_workspace(self) -> None:
        """Il dry-run controlla il piano ma non crea la directory richiesta."""
        with writable_test_directory() as input_dir:
            (input_dir / "demo01.jpg").write_bytes(b"demo")
            workspace_id = f"unittest_{uuid.uuid4().hex}"
            workspace_dir = (
                PROJECT_ROOT / "outputs" / "demo_workspaces" / workspace_id
            )

            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(LAUNCHER_PATH),
                    "graph",
                    "--workspace",
                    workspace_id,
                    "--input-dir",
                    str(input_dir),
                    "--circuit",
                    "demo01",
                    "--dry-run",
                ],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Dry-run", result.stdout)
            self.assertFalse(workspace_dir.exists())

    def test_graph_requires_an_existing_circuit(self) -> None:
        """Un identificativo assente produce un errore chiaro prima di YOLO."""
        with writable_test_directory() as input_dir:
            (input_dir / "demo01.jpg").write_bytes(b"demo")

            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(LAUNCHER_PATH),
                    "graph",
                    "--workspace",
                    "unittest_missing",
                    "--input-dir",
                    str(input_dir),
                    "--circuit",
                    "missing",
                    "--dry-run",
                ],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Circuito 'missing' non trovato", result.stderr)


class WorkspaceManifestTests(unittest.TestCase):
    """Verifica la persistenza minima necessaria tra due comandi separati."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.launcher = load_launcher_module()

    def test_snapshot_and_manifest_preserve_the_image_contract(self) -> None:
        """Il manifest conserva path e hash della copia usata dalla pipeline."""
        with writable_test_directory() as test_dir:
            source_dir = test_dir / "source"
            source_dir.mkdir()
            source_image = source_dir / "demo01.jpg"
            source_image.write_bytes(b"immagine-demo")
            workspace_dir = test_dir / "workspace"
            manifest_path = workspace_dir / "workspace_manifest.json"

            manifest = self.launcher.read_manifest(manifest_path, "demo_test")
            snapshots = self.launcher.snapshot_images(
                {"demo01": source_image},
                workspace_dir / "input" / "images",
                manifest,
                force=False,
            )
            self.launcher.write_manifest(manifest_path, manifest)
            reloaded = self.launcher.read_manifest(manifest_path, "demo_test")

            self.assertTrue(snapshots["demo01"].is_file())
            self.assertEqual(
                reloaded["circuits"]["demo01"]["image_sha256"],
                self.launcher.sha256_file(source_image),
            )
            self.assertEqual(
                reloaded["circuits"]["demo01"]["pipeline1"]["status"],
                "pending",
            )

    def test_schema_v2_serializes_project_paths_as_repo_relative(self) -> None:
        """Un clone in un'altra directory non deve ereditare path del PC origine."""
        with writable_test_directory() as test_dir:
            manifest_path = test_dir / "workspace_manifest.json"
            manifest = {
                "schema_version": 1,
                "workspace_id": "portable_test",
                "input_dir": str(
                    PROJECT_ROOT / "data" / "batchPipeline2.0" / "batchDemo"
                ),
                "circuits": {
                    "a09": {
                        "source_image": str(
                            PROJECT_ROOT
                            / "data"
                            / "batchPipeline2.0"
                            / "batchDemo"
                            / "a09.jpg"
                        ),
                        "pipeline2": {
                            "artifacts": {
                                "graph": str(
                                    PROJECT_ROOT
                                    / "outputs"
                                    / "demo_workspaces"
                                    / "portable_test"
                                    / "pipeline2.0"
                                    / "a09"
                                    / "01_graph.json"
                                )
                            }
                        },
                    }
                },
            }

            self.launcher.write_manifest(manifest_path, manifest)
            serialized = json.loads(manifest_path.read_text(encoding="utf-8"))

            self.assertEqual(serialized["schema_version"], 2)
            self.assertEqual(
                serialized["input_dir"],
                "data/batchPipeline2.0/batchDemo",
            )
            self.assertEqual(
                serialized["circuits"]["a09"]["source_image"],
                "data/batchPipeline2.0/batchDemo/a09.jpg",
            )
            self.assertEqual(
                serialized["circuits"]["a09"]["pipeline2"]["artifacts"]["graph"],
                "outputs/demo_workspaces/portable_test/pipeline2.0/a09/01_graph.json",
            )

    def test_historical_batch_demo_alias_resolves_to_canonical_directory(self) -> None:
        """Il vecchio alias relativo continua a trovare il Batch Demo trasferito."""
        resolved = self.launcher.resolve_manifest_path(
            "data/batchDemo/values/a09_values.yaml"
        )

        self.assertEqual(
            resolved,
            (
                PROJECT_ROOT
                / "data"
                / "batchPipeline2.0"
                / "batchDemo"
                / "values"
                / "a09_values.yaml"
            ).resolve(),
        )

    def test_relative_path_normalization_preserves_leading_dots(self) -> None:
        """Directory nascoste e parent traversal non perdono caratteri iniziali."""
        self.assertEqual(
            self.launcher._canonical_legacy_relative_path(Path(".tmp/easyocr")),
            Path(".tmp/easyocr"),
        )
        self.assertEqual(
            self.launcher._canonical_legacy_relative_path(Path("../outside")),
            Path("../outside"),
        )

    def test_old_windows_absolute_path_is_rebased_to_current_clone(self) -> None:
        """Un manifest del vecchio PC viene ricondotto alla root del clone attuale."""
        old_path = (
            r"R:\old_machine\tesi_diagrams_yolo\data\batchDemo"
            r"\values\a09_values.yaml"
        )

        resolved = self.launcher.resolve_manifest_path(old_path)

        self.assertEqual(
            resolved,
            (
                PROJECT_ROOT
                / "data"
                / "batchPipeline2.0"
                / "batchDemo"
                / "values"
                / "a09_values.yaml"
            ).resolve(),
        )

    def test_absolute_local_legacy_alias_is_canonicalized(self) -> None:
        """Anche un alias assoluto sotto la root corrente usa il batch canonico."""
        legacy_path = (
            PROJECT_ROOT / "data" / "batchDemo" / "values" / "a09_values.yaml"
        )

        resolved = self.launcher.resolve_manifest_path(legacy_path)

        self.assertEqual(
            resolved,
            (
                PROJECT_ROOT
                / "data"
                / "batchPipeline2.0"
                / "batchDemo"
                / "values"
                / "a09_values.yaml"
            ).resolve(),
        )


if __name__ == "__main__":
    unittest.main()
