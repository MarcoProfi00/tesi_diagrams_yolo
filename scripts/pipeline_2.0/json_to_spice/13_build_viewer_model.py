"""Entry point dello step 13: costruisce il modello dati del viewer."""

from __future__ import annotations

import argparse
from pathlib import Path

from viewer_core.contracts import VIEWER_MODEL_NAME
from viewer_core.model_builder import build_viewer_model, write_viewer_model


def main() -> None:
    """Legge la cartella run e salva il modello elettrico e strutturale."""
    parser = argparse.ArgumentParser(
        description="Genera il viewer model Pipeline 2.0 per una cartella run."
    )
    parser.add_argument(
        "--run-dir",
        required=True,
        help="Cartella run che contiene 07_netlist.cir.",
    )
    args = parser.parse_args()
    run_dir = Path(args.run_dir)
    model = write_viewer_model(run_dir)
    print(f"Scritto {run_dir / VIEWER_MODEL_NAME}")
    print(f"Componenti: {len(model.get('netlist_components') or [])}")


__all__ = ["build_viewer_model", "write_viewer_model"]


if __name__ == "__main__":
    main()
