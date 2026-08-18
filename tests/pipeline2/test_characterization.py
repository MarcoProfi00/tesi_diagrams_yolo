"""Golden test degli output tecnici e visuali della Pipeline 2.0."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

from tests.pipeline2.helpers import (
    JSON_TO_SPICE_DIR,
    PIPELINE2_SCRIPT_DIR,
    PROJECT_ROOT,
    copy_validated_run,
    isolated_directory,
    load_baseline,
    load_numbered_module,
    stable_digest,
    validated_run_dir,
)


for import_path in (PIPELINE2_SCRIPT_DIR, JSON_TO_SPICE_DIR):
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

import run_pipeline2  # noqa: E402  # Import dopo la preparazione dei path di test.
from viewer_core.layout_builder import build_viewer_layout  # noqa: E402
from viewer_core.model_builder import build_viewer_model  # noqa: E402
from viewer_core.svg_renderer import render_svg  # noqa: E402


BASELINE = load_baseline()
EXPECTED_CORE_CASES = {
    "a01", "a02", "a04", "a05", "a06", "a07", "a08", "a09", "a10",
    "b02", "b03", "b04", "b05", "b06", "b10",
}
EXPECTED_VIEWER_CASES = {"a01", "a04", "a05", "b02", "b03", "b04", "b05", "b06", "b10"}
EXPECTED_SCENARIO_CASES = {
    "b02/scenario_1",
    "b03/scenario_5",
    "b04/scenario_2",
    "b05/scenario_6",
    "b06/scenario_2",
    "b10/scenario_1",
}


class BaselineInventoryTests(unittest.TestCase):
    """Impedisce che un caso sparisca dal manifest senza essere notato."""

    def test_characterization_inventory_is_complete(self) -> None:
        """Verifica gli inventari approvati per core, viewer, scenari e pagine."""
        self.assertEqual(set(BASELINE["core_cases"]), EXPECTED_CORE_CASES)
        self.assertEqual(set(BASELINE["viewer_cases"]), EXPECTED_VIEWER_CASES)
        self.assertEqual(set(BASELINE["scenario_cases"]), EXPECTED_SCENARIO_CASES)
        self.assertEqual(set(BASELINE["web_page_cases"]), {"b02", "b06"})
        self.assertEqual(set(BASELINE["agent_web_page_cases"]), {"b02"})


class CorePipelineCharacterizationTests(unittest.TestCase):
    """Protegge gli step 01-07 su tutti i circuiti gia validati."""

    def build_current_outputs(
        self,
        batch: str,
        experiment: str,
        circuit: str,
    ) -> dict[str, object]:
        """Rigenera in memoria gli artefatti senza scrivere negli output reali."""
        run_dir = validated_run_dir(batch, experiment, circuit)
        raw_graph = json.loads((run_dir / "01_graph.json").read_text(encoding="utf-8"))
        normalized = run_pipeline2.normalize.normalize_circuit_graph(raw_graph)
        node_map = run_pipeline2.node_map.build_node_map(normalized)

        values_path = (
            PROJECT_ROOT
            / "metadata"
            / "pipeline2_manual_values"
            / batch
            / f"{circuit}_values.yaml"
        )
        values_data = run_pipeline2.values.load_simple_yaml(values_path)
        values_bound = run_pipeline2.values.build_values_bound(
            normalized_circuit=normalized,
            node_map=node_map,
            values_data=values_data,
            values_source=values_path,
        )

        classes_path = PROJECT_ROOT / "metadata" / "pipeline2_spice_classes.yaml"
        classes_data = run_pipeline2.values.load_simple_yaml(classes_path)
        rules = run_pipeline2.component_rules.build_component_rules(
            values_bound=values_bound,
            spice_classes=classes_data,
            spice_classes_source=classes_path,
        )
        models_data = run_pipeline2.values.load_simple_yaml(
            PROJECT_ROOT / "metadata" / "pipeline2_spice_models.yaml"
        )
        emitted = run_pipeline2.spice_emit.build_spice_netlist(rules, models_data)

        return {
            "normalized": normalized,
            "node_map": node_map,
            "values": values_bound,
            "rules": rules,
            "netlist": emitted["netlist_text"],
            "emit_report": emitted["report"],
        }

    def test_all_validated_core_outputs_match_the_baseline(self) -> None:
        """Blocca variazioni involontarie di topologia, valori, regole e netlist."""
        for circuit, expected in BASELINE["core_cases"].items():
            with self.subTest(circuit=circuit):
                generated = self.build_current_outputs(
                    expected["batch"],
                    expected["experiment"],
                    circuit,
                )
                for artifact_name, artifact in generated.items():
                    self.assertEqual(
                        stable_digest(artifact),
                        expected[artifact_name],
                        f"Artefatto cambiato: {circuit}/{artifact_name}",
                    )


class ViewerCharacterizationTests(unittest.TestCase):
    """Protegge modello, layout e simboli SVG su componenti rappresentativi."""

    def test_representative_viewers_match_the_baseline(self) -> None:
        """Confronta l'intera catena viewer in una copia isolata della run."""
        for circuit, expected in BASELINE["viewer_cases"].items():
            with self.subTest(circuit=circuit):
                with isolated_directory(f"viewer_{circuit}") as temporary_root:
                    run_dir = copy_validated_run(
                        expected["batch"],
                        expected["experiment"],
                        circuit,
                        temporary_root,
                    )
                    model = build_viewer_model(run_dir)
                    (run_dir / "13_viewer_model.json").write_text(
                        json.dumps(model, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8",
                    )
                    layout = build_viewer_layout(run_dir)
                    svg = render_svg(model, layout)

                    self.assertEqual(
                        stable_digest(model, temporary_root),
                        expected["viewer_model"],
                    )
                    self.assertEqual(
                        stable_digest(layout, temporary_root),
                        expected["viewer_layout"],
                    )
                    self.assertEqual(
                        stable_digest(svg, temporary_root),
                        expected["viewer_svg"],
                    )
                    self.assertIn("<svg", svg)
                    self.assertNotIn("{{", svg)


class ScenarioCharacterizationTests(unittest.TestCase):
    """Protegge confronti OP/TRAN lavorando soltanto su copie temporanee."""

    @classmethod
    def setUpClass(cls) -> None:
        """Carica una sola volta lo step 12 numerato."""
        cls.step12 = load_numbered_module("12_controlled_scenarios.py")

    def test_representative_scenario_comparisons_match_the_baseline(self) -> None:
        """Verifica parser, metriche e outcome senza toccare le run validate."""
        with isolated_directory("scenario_characterization") as temporary_root:
            copied_circuits: dict[str, Path] = {}
            for key, expected_digest in BASELINE["scenario_cases"].items():
                circuit, scenario_id = key.split("/", 1)
                run_metadata = BASELINE["core_cases"][circuit]
                with self.subTest(circuit=circuit, scenario=scenario_id):
                    circuit_dir = copied_circuits.get(circuit)
                    if circuit_dir is None:
                        circuit_dir = copy_validated_run(
                            run_metadata["batch"],
                            run_metadata["experiment"],
                            circuit,
                            temporary_root,
                        )
                        copied_circuits[circuit] = circuit_dir

                    scenario_dir = circuit_dir / "scenarios" / scenario_id
                    status_path = scenario_dir / "scenario_status.json"
                    status = json.loads(status_path.read_text(encoding="utf-8"))
                    status["base_output_dir"] = str(circuit_dir)
                    status_path.write_text(
                        json.dumps(status, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8",
                    )
                    scenario = json.loads(
                        (scenario_dir / "scenario.json").read_text(encoding="utf-8")
                    )
                    comparison = self.step12.build_scenario_comparison(
                        scenario_dir,
                        scenario,
                    )
                    self.assertEqual(
                        stable_digest(comparison, temporary_root),
                        expected_digest,
                    )


class WebPageCharacterizationTests(unittest.TestCase):
    """Protegge la pagina self-contained prima di estrarre gli asset inline."""

    @classmethod
    def setUpClass(cls) -> None:
        """Carica una sola volta l'entry point web numerato."""
        cls.web_chat = load_numbered_module("09_web_chat.py")

    def assert_pages_match_the_baseline(
        self,
        case_group: str,
        workspace_mode: str,
    ) -> None:
        """Renderizza un gruppo di pagine in copie isolate e confronta l'HTML."""
        for circuit, expected_digest in BASELINE[case_group].items():
            run_metadata = BASELINE["core_cases"][circuit]
            with self.subTest(circuit=circuit, workspace_mode=workspace_mode):
                with isolated_directory(
                    f"web_page_{workspace_mode}_{circuit}"
                ) as temporary_root:
                    output_dir = copy_validated_run(
                        run_metadata["batch"],
                        run_metadata["experiment"],
                        circuit,
                        temporary_root,
                        workspace_mode=workspace_mode,
                    )
                    page = self.web_chat.render_page(
                        run_metadata["batch"],
                        circuit,
                        output_dir,
                        experiment=run_metadata["experiment"],
                        workspace_mode=workspace_mode,
                        available_workspace_modes=("chat", "agent"),
                    )
                    self.assertEqual(
                        stable_digest(page, temporary_root),
                        expected_digest,
                    )
                    self.assertNotIn("{{", page)
                    self.assertIn("Pipeline 2.0", page)

    def test_representative_chat_pages_match_the_baseline(self) -> None:
        """Protegge l'HTML completo della modalita CHAT."""
        self.assert_pages_match_the_baseline("web_page_cases", "chat")

    def test_representative_agent_pages_match_the_baseline(self) -> None:
        """Protegge l'HTML completo della modalita AGENT."""
        self.assert_pages_match_the_baseline("agent_web_page_cases", "agent")


if __name__ == "__main__":
    unittest.main()
