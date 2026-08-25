"""Test dell'orchestrazione completa senza eseguire le pipeline reali."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
from unittest import mock
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LAUNCHER_PATH = PROJECT_ROOT / "scripts" / "pipeline_unified" / "run_pipeline.py"


def load_launcher_module():
    """Carica l'orchestratore senza richiedere un package installato."""
    spec = importlib.util.spec_from_file_location("pipeline_unified_all", LAUNCHER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare il launcher: {LAUNCHER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def all_args(**overrides):
    """Crea gli argomenti minimi di una prova completa su un circuito."""
    values = {
        "workspace": "demo_a09_all",
        "input_dir": "data/batchPipeline2.0/batchDemo",
        "circuit": "a09",
        "all": False,
        "open_circuit": None,
        "host": "127.0.0.1",
        "port": 8765,
        "ngspice_executable": "ngspice",
        "prepare_only": True,
        "no_browser": False,
        "force": False,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


class AllCommandTests(unittest.TestCase):
    """Verifica ordine, mapping e arresto delle tre fasi pubbliche."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.launcher = load_launcher_module()

    def test_single_circuit_runs_the_three_existing_commands_in_order(self) -> None:
        """Il comando completo coordina gli handler senza duplicarne la logica."""
        calls: list[tuple[str, argparse.Namespace]] = []

        def record(name):
            def handler(args):
                calls.append((name, args))
                return 0

            return handler

        with (
            mock.patch.object(self.launcher, "graph_command", side_effect=record("graph")),
            mock.patch.object(self.launcher, "spice_command", side_effect=record("spice")),
            mock.patch.object(self.launcher, "webchat_command", side_effect=record("webchat")),
        ):
            result = self.launcher.all_command(all_args())

        self.assertEqual(result, 0)
        self.assertEqual([name for name, _ in calls], ["graph", "spice", "webchat"])
        self.assertEqual(calls[0][1].circuit, "a09")
        self.assertEqual(calls[1][1].circuit, "a09")
        self.assertEqual(calls[2][1].circuit, "a09")
        self.assertTrue(calls[2][1].prepare_only)

    def test_failure_stops_before_later_stages(self) -> None:
        """Una fase fallita impedisce di usare output incompleti nelle successive."""
        with (
            mock.patch.object(self.launcher, "graph_command", return_value=7),
            mock.patch.object(self.launcher, "spice_command") as spice,
            mock.patch.object(self.launcher, "webchat_command") as webchat,
        ):
            result = self.launcher.all_command(all_args())

        self.assertEqual(result, 7)
        spice.assert_not_called()
        webchat.assert_not_called()

    def test_batch_requires_the_circuit_to_open(self) -> None:
        """Il batch non sceglie implicitamente quale viewer mostrare."""
        with self.assertRaisesRegex(ValueError, "--open-circuit"):
            self.launcher.all_command(
                all_args(circuit=None, all=True, open_circuit=None)
            )

    def test_single_circuit_rejects_a_different_open_circuit(self) -> None:
        """La selezione singola resta univoca in tutte le fasi."""
        with self.assertRaisesRegex(ValueError, "stesso circuito"):
            self.launcher.all_command(all_args(open_circuit="b02"))


if __name__ == "__main__":
    unittest.main()
