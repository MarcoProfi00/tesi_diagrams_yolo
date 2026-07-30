"""Test del collegamento generale fra workspace, YAML e Pipeline 2.0."""

from __future__ import annotations

from contextlib import contextmanager
import importlib.util
import json
from pathlib import Path
import shutil
import unittest
import uuid


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LAUNCHER_PATH = PROJECT_ROOT / "scripts" / "pipeline_unified" / "run_pipeline.py"
TEST_TEMP_ROOT = PROJECT_ROOT / "outputs" / ".test_tmp"
TEST_TEMP_ROOT.mkdir(parents=True, exist_ok=True)


@contextmanager
def writable_test_directory():
    """Crea e rimuove una directory temporanea confinata al workspace."""
    path = TEST_TEMP_ROOT / f"spice_{uuid.uuid4().hex}"
    path.mkdir(parents=True)
    try:
        yield path
    finally:
        # Il target e' sempre figlio della root di test e usa un UUID locale.
        shutil.rmtree(path)


def load_launcher_module():
    """Carica l'orchestratore senza richiedere un package Python installato."""
    spec = importlib.util.spec_from_file_location("pipeline_unified_spice", LAUNCHER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare il launcher: {LAUNCHER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SpiceWorkspaceTests(unittest.TestCase):
    """Protegge la provenienza degli input della fase SPICE."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.launcher = load_launcher_module()
        cls.pipeline2 = cls.launcher.load_pipeline2_module()

    def prepare_case(self, root: Path, circuit_id: str) -> tuple[Path, dict]:
        """Prepara un workspace minimo con Graph e YAML omonimi."""
        batch_dir = root / "batch_arbitrario"
        values_dir = batch_dir / "values"
        values_dir.mkdir(parents=True)
        (values_dir / f"{circuit_id}_values.yaml").write_text(
            f"circuit_id: {circuit_id}\n",
            encoding="utf-8",
        )

        workspace = root / "workspace"
        graph_path = (
            workspace
            / "pipeline1.0"
            / "06_graph_report"
            / circuit_id
            / f"{circuit_id}.json"
        )
        graph_path.parent.mkdir(parents=True)
        graph_path.write_text("{}\n", encoding="utf-8")
        manifest = {
            "workspace_id": "workspace_test",
            "input_dir": str(batch_dir),
            "values_dir": str(values_dir),
            "circuits": {
                circuit_id: {
                    "pipeline1": {
                        "status": "completed",
                        # Questo path intenzionalmente errato dimostra che la
                        # fase SPICE usa il Graph appena creato nel workspace.
                        "graph_json": "outputs/pipeline1.0/storico/non_usare.json",
                    }
                }
            },
        }
        return workspace, manifest

    def test_plan_uses_fresh_workspace_graph_for_an_arbitrary_circuit(self) -> None:
        """Nessun prefisso o circuito noto viene codificato nel resolver."""
        with writable_test_directory() as root:
            circuit_id = "circuito_x7"
            workspace, manifest = self.prepare_case(root, circuit_id)

            plans = self.launcher.build_spice_plans(
                workspace,
                manifest,
                [circuit_id],
                self.pipeline2,
            )

            expected_graph = (
                workspace
                / "pipeline1.0"
                / "06_graph_report"
                / circuit_id
                / f"{circuit_id}.json"
            ).resolve()
            self.assertEqual(plans[0]["graph_path"], expected_graph)
            self.assertEqual(
                plans[0]["values_path"].name,
                f"{circuit_id}_values.yaml",
            )
            self.assertTrue(plans[0]["spice_models_sha256"])

    def test_plan_rejects_a_yaml_for_a_different_circuit(self) -> None:
        """Un file omonimo non puo' dichiarare valori per un altro circuito."""
        with writable_test_directory() as root:
            circuit_id = "demo01"
            workspace, manifest = self.prepare_case(root, circuit_id)
            values_path = root / "batch_arbitrario" / "values" / "demo01_values.yaml"
            values_path.write_text("circuit_id: altro_circuito\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "dichiara circuit_id"):
                self.launcher.build_spice_plans(
                    workspace,
                    manifest,
                    [circuit_id],
                    self.pipeline2,
                )

    def test_completed_state_requires_matching_hashes_and_artifacts(self) -> None:
        """Una run viene saltata solo quando input e output sono ancora completi."""
        with writable_test_directory() as root:
            output_dir = root / "pipeline2.0" / "demo01"
            output_dir.mkdir(parents=True)
            for filename in self.launcher.PIPELINE2_REQUIRED_ARTIFACTS:
                (output_dir / filename).write_text("test\n", encoding="utf-8")
            (output_dir / "08_spice_run.json").write_text(
                json.dumps({"status": "success", "exit_code": 0}),
                encoding="utf-8",
            )
            plan = {
                "graph_sha256": "graph-hash",
                "values_sha256": "values-hash",
                "spice_models_sha256": "models-hash",
                "output_dir": output_dir,
            }
            state = {
                "status": "completed",
                "graph_sha256": "graph-hash",
                "values_sha256": "values-hash",
                "spice_models_sha256": "models-hash",
            }

            self.assertTrue(self.launcher.pipeline2_state_is_current(state, plan))
            state["values_sha256"] = "modificato"
            self.assertFalse(self.launcher.pipeline2_state_is_current(state, plan))


class DemoValuesTests(unittest.TestCase):
    """Verifica che il Batch Demo riusi esattamente i valori gia' validati."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.launcher = load_launcher_module()
        cls.pipeline2 = cls.launcher.load_pipeline2_module()

    def test_demo_values_match_the_validated_yaml_files(self) -> None:
        """Le copie autosufficienti non devono cambiare nessun parametro."""
        cases = {
            "a04": "batchA",
            "a08": "batchA",
            "a09": "batchA",
            "b02": "batchB",
            "b03": "batchB",
        }
        for circuit_id, source_batch in cases.items():
            with self.subTest(circuit_id=circuit_id):
                batch_copy = (
                    PROJECT_ROOT
                    / "data"
                    / "batchDemo"
                    / "values"
                    / f"{circuit_id}_values.yaml"
                )
                validated = (
                    PROJECT_ROOT
                    / "metadata"
                    / "pipeline2_manual_values"
                    / source_batch
                    / f"{circuit_id}_values.yaml"
                )
                self.assertEqual(
                    self.pipeline2.values.load_simple_yaml(batch_copy),
                    self.pipeline2.values.load_simple_yaml(validated),
                )


if __name__ == "__main__":
    unittest.main()
