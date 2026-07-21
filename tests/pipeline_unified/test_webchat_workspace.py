"""Test delle copie isolate e delle sorgenti geometriche della webchat."""

from __future__ import annotations

from contextlib import contextmanager
import importlib.util
import json
from pathlib import Path
import shutil
import sys
from types import SimpleNamespace
import unittest
import uuid


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LAUNCHER_PATH = PROJECT_ROOT / "scripts" / "pipeline_unified" / "run_pipeline.py"
JSON_TO_SPICE_DIR = PROJECT_ROOT / "scripts" / "pipeline_2.0" / "json_to_spice"
TEST_TEMP_ROOT = PROJECT_ROOT / "outputs" / ".test_tmp"
TEST_TEMP_ROOT.mkdir(parents=True, exist_ok=True)
if str(JSON_TO_SPICE_DIR) not in sys.path:
    sys.path.insert(0, str(JSON_TO_SPICE_DIR))

from viewer_core.model_builder import load_geometry_seed  # noqa: E402


@contextmanager
def writable_test_directory():
    """Crea una root temporanea confinata agli output di test."""
    path = TEST_TEMP_ROOT / f"webchat_{uuid.uuid4().hex}"
    path.mkdir(parents=True)
    try:
        yield path
    finally:
        shutil.rmtree(path)


def load_launcher_module():
    """Carica l'orchestratore senza installarlo come package."""
    spec = importlib.util.spec_from_file_location("pipeline_unified_webchat_test", LAUNCHER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare il launcher: {LAUNCHER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class WebWorkspaceTests(unittest.TestCase):
    """Protegge separazione delle sessioni e provenienza della geometria."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.launcher = load_launcher_module()

    def build_source_plan(self, root: Path) -> dict:
        """Prepara una piccola base deterministica senza simulare ngspice."""
        circuit_id = "circuito_demo"
        base_dir = root / "pipeline2.0" / circuit_id
        base_dir.mkdir(parents=True)
        for filename, content in (
            ("01_graph.json", "{}\n"),
            ("03_node_map.json", "{}\n"),
            ("07_netlist.cir", "* test\n.end\n"),
            ("08_spice_run.json", '{"status": "success", "exit_code": 0}\n'),
        ):
            (base_dir / filename).write_text(content, encoding="utf-8")

        image_path = root / "input" / "images" / f"{circuit_id}.png"
        image_path.parent.mkdir(parents=True)
        image_path.write_bytes(b"immagine")
        estimate_path = root / "pipeline1.0" / "03_estimate_terminals" / f"{circuit_id}.json"
        graph_path = root / "pipeline1.0" / "05_build_terminal_graph" / f"{circuit_id}.json"
        estimate_path.parent.mkdir(parents=True)
        graph_path.parent.mkdir(parents=True)
        estimate_path.write_text("{}\n", encoding="utf-8")
        graph_path.write_text("{}\n", encoding="utf-8")

        base_files = {
            path.name: self.launcher.sha256_file(path)
            for path in base_dir.iterdir()
        }
        fingerprints = {
            "input_image": self.launcher.sha256_file(image_path),
            "terminal_estimates": self.launcher.sha256_file(estimate_path),
            "terminal_graph": self.launcher.sha256_file(graph_path),
            "graph": base_files["01_graph.json"],
            "values": "valori-test",
            "base_files": base_files,
        }
        return {
            "circuit_id": circuit_id,
            "base_dir": base_dir,
            "workspace_image": image_path,
            "terminal_estimates": estimate_path,
            "terminal_graph": graph_path,
            "base_files": base_files,
            "fingerprints": fingerprints,
        }

    @staticmethod
    def fake_webchat_module() -> SimpleNamespace:
        """Sostituisce soltanto la generazione pesante, non il bootstrap testato."""
        def write_json_artifact(run_dir: Path, filename: str):
            path = run_dir / filename
            path.write_text("{}\n", encoding="utf-8")
            return {}

        def write_svg(run_dir: Path):
            path = run_dir / "15_viewer.svg"
            path.write_text("<svg/>\n", encoding="utf-8")
            return path.read_text(encoding="utf-8")

        def write_context(**kwargs):
            path = Path(kwargs["output_dir"]) / "10_diagnostic_context.json"
            path.write_text("{}\n", encoding="utf-8")
            return path

        return SimpleNamespace(
            load_or_build_viewer_model=lambda run_dir: write_json_artifact(
                run_dir, "13_viewer_model.json"
            ),
            load_or_build_viewer_layout=lambda run_dir: write_json_artifact(
                run_dir, "14_viewer_layout.json"
            ),
            load_or_build_viewer_svg=write_svg,
            write_chat_context=write_context,
        )

    def test_chat_and_agent_are_independent_copies_of_the_same_base(self) -> None:
        """Una modifica nella sessione CHAT non deve comparire nella sessione AGENT."""
        with writable_test_directory() as root:
            plan = self.build_source_plan(root)
            webchat = self.fake_webchat_module()
            chat_dir = root / "web" / "chat" / plan["circuit_id"]
            agent_dir = root / "web" / "agent" / plan["circuit_id"]

            self.launcher.prepare_web_session(
                chat_dir, "chat", plan, webchat, "batch_test", "workspace_test", False
            )
            (chat_dir / "solo_chat.txt").write_text("stato chat\n", encoding="utf-8")
            self.launcher.prepare_web_session(
                agent_dir, "agent", plan, webchat, "batch_test", "workspace_test", False
            )

            self.assertTrue((chat_dir / "solo_chat.txt").is_file())
            self.assertFalse((agent_dir / "solo_chat.txt").exists())
            for filename, expected_hash in plan["base_files"].items():
                self.assertEqual(self.launcher.sha256_file(chat_dir / filename), expected_hash)
                self.assertEqual(self.launcher.sha256_file(agent_dir / filename), expected_hash)

    def test_existing_session_rejects_a_changed_base(self) -> None:
        """History e scenari non possono essere riusati dopo una variazione della base."""
        with writable_test_directory() as root:
            plan = self.build_source_plan(root)
            webchat = self.fake_webchat_module()
            chat_dir = root / "web" / "chat" / plan["circuit_id"]
            self.launcher.prepare_web_session(
                chat_dir, "chat", plan, webchat, "batch_test", "workspace_test", False
            )
            changed_plan = dict(plan)
            changed_plan["fingerprints"] = dict(plan["fingerprints"])
            changed_plan["fingerprints"]["graph"] = "graph-modificato"

            with self.assertRaisesRegex(ValueError, "sorgenti della sessione sono cambiate"):
                self.launcher.prepare_web_session(
                    chat_dir,
                    "chat",
                    changed_plan,
                    webchat,
                    "batch_test",
                    "workspace_test",
                    False,
                )

    def test_scenario_viewer_uses_pipeline1_geometry_from_the_same_workspace(self) -> None:
        """Anche una run scenario risale agli step 03 e 05 dichiarati dalla base."""
        with writable_test_directory() as root:
            plan = self.build_source_plan(root)
            circuit_id = plan["circuit_id"]
            plan["terminal_estimates"].write_text(
                json.dumps(
                    {
                        "image_id": circuit_id,
                        "image_width": 100,
                        "image_height": 80,
                        "components": [
                            {
                                "instance_id": "1.1",
                                "class_name": "Resistor",
                                "bbox": [10, 20, 40, 35],
                                "terminals": [
                                    {"name": "pin1", "x": 10, "y": 27},
                                    {"name": "pin2", "x": 40, "y": 27},
                                ],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            plan["terminal_graph"].write_text(
                json.dumps(
                    {
                        "components": [
                            {
                                "component_id": "resistor1.1",
                                "instance_id": "1.1",
                                "class_name": "Resistor",
                                "terminals": [
                                    {"terminal_id": "r1", "name": "pin1"},
                                    {"terminal_id": "r2", "name": "pin2"},
                                ],
                            }
                        ],
                        "graph": {},
                    }
                ),
                encoding="utf-8",
            )
            session_dir = root / "web" / "chat" / circuit_id
            session_dir.mkdir(parents=True)
            descriptor = self.launcher.build_run_sources_descriptor(session_dir, "chat", plan)
            (session_dir / "pipeline2_sources.json").write_text(
                json.dumps(descriptor),
                encoding="utf-8",
            )
            scenario_run = session_dir / "scenarios" / "scenario_1" / "run"
            scenario_run.mkdir(parents=True)

            geometry = load_geometry_seed(
                scenario_run,
                circuit_id,
                {"component_terminal_nodes": {"resistor1.1": {"pin1": "N001", "pin2": "N002"}}},
            )

            self.assertEqual(geometry["status"], "loaded")
            self.assertEqual(
                Path(geometry["source_files"]["terminal_estimates"]).resolve(),
                plan["terminal_estimates"].resolve(),
            )
            self.assertIn("resistor1.1", geometry["components"])


if __name__ == "__main__":
    unittest.main()
