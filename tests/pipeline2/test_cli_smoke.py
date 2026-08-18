"""Smoke test degli entry point pubblici della Pipeline 2.0."""

from __future__ import annotations

import subprocess
import sys
import unittest

from tests.pipeline2.helpers import JSON_TO_SPICE_DIR, PIPELINE2_SCRIPT_DIR


ENTRY_POINTS = (
    PIPELINE2_SCRIPT_DIR / "run_pipeline2.py",
    PIPELINE2_SCRIPT_DIR / "prepare_experiment_outputs.py",
    JSON_TO_SPICE_DIR / "09_web_chat.py",
    JSON_TO_SPICE_DIR / "11_agent_readonly.py",
    JSON_TO_SPICE_DIR / "12_controlled_scenarios.py",
    JSON_TO_SPICE_DIR / "13_build_viewer_model.py",
    JSON_TO_SPICE_DIR / "14_build_viewer_layout.py",
    JSON_TO_SPICE_DIR / "15_render_viewer_svg.py",
    JSON_TO_SPICE_DIR / "16_autonomous_diagnosis.py",
)


class CliSmokeTests(unittest.TestCase):
    """Verifica che spostamenti interni non rompano gli script pubblici."""

    def test_all_public_entry_points_support_help(self) -> None:
        """Ogni comando deve importarsi e terminare correttamente con --help."""
        for script in ENTRY_POINTS:
            with self.subTest(script=script.name):
                completed = subprocess.run(
                    [sys.executable, "-B", str(script), "--help"],
                    capture_output=True,
                    text=True,
                    timeout=20,
                    check=False,
                )
                self.assertEqual(
                    completed.returncode,
                    0,
                    completed.stderr or completed.stdout,
                )


if __name__ == "__main__":
    unittest.main()
