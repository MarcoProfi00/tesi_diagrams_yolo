"""Test del preflight integrato senza dipendere dai programmi del PC."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import subprocess
import sys
from unittest import mock
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LAUNCHER_PATH = PROJECT_ROOT / "scripts" / "pipeline_unified" / "run_pipeline.py"


def load_launcher_module():
    """Carica il launcher da file senza richiedere un package installato."""
    spec = importlib.util.spec_from_file_location(
        "pipeline_unified_preflight",
        LAUNCHER_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare il launcher: {LAUNCHER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def preflight_args(*, require_openai: bool = False) -> argparse.Namespace:
    """Crea gli argomenti del controllo sul batch demo canonico."""
    return argparse.Namespace(
        input_dir="data/batchPipeline2.0/batchDemo",
        ngspice_executable=None,
        tesseract_executable=None,
        require_openai=require_openai,
    )


class PreflightCommandTests(unittest.TestCase):
    """Verifica contratto CLI, successo tecnico e opzionalita' OpenAI."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.launcher = load_launcher_module()

    def test_parser_exposes_portable_preflight_defaults(self) -> None:
        """Il nuovo PC puo' lanciare il controllo senza fornire path personali."""
        args = self.launcher.build_parser().parse_args(["preflight"])

        self.assertIs(args.handler, self.launcher.preflight_command)
        self.assertEqual(args.input_dir, "data/batchPipeline2.0/batchDemo")
        self.assertIsNone(args.ngspice_executable)
        self.assertIsNone(args.tesseract_executable)
        self.assertFalse(args.require_openai)

    def run_with_external_checks_mocked(self, *, require_openai: bool) -> int:
        """Lascia reali asset/hash/YAML e sostituisce soltanto processi esterni."""
        tesseract_result = subprocess.CompletedProcess(
            args=["tesseract", "--list-langs"],
            returncode=0,
            stdout="List of available languages in test:\neng\nosd\n",
            stderr="",
        )
        with (
            mock.patch.object(
                self.launcher,
                "_run_preflight_process",
                return_value=(True, "controllo simulato OK"),
            ),
            mock.patch.object(
                self.launcher,
                "_resolve_executable",
                return_value=sys.executable,
            ),
            mock.patch.object(self.launcher.shutil, "which", return_value="git"),
            mock.patch.object(
                self.launcher,
                "_local_openai_key_is_configured",
                return_value=False,
            ),
            mock.patch.object(
                self.launcher,
                "_easyocr_cache_status",
                return_value=(True, "cache simulata OK"),
            ),
            mock.patch.object(self.launcher.subprocess, "run", return_value=tesseract_result),
        ):
            return self.launcher.preflight_command(
                preflight_args(require_openai=require_openai)
            )

    def test_technical_preflight_does_not_require_openai(self) -> None:
        """Graph, SPICE e viewer sono pronti anche senza una API key locale."""
        self.assertEqual(self.run_with_external_checks_mocked(require_openai=False), 0)

    def test_require_openai_turns_missing_key_into_failure(self) -> None:
        """L'opzione AGENT rende esplicita e verificabile la credenziale mancante."""
        self.assertEqual(self.run_with_external_checks_mocked(require_openai=True), 1)


if __name__ == "__main__":
    unittest.main()
