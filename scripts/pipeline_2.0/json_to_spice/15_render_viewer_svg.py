"""Espone lo step 15 che renderizza il viewer SVG di una run."""

from __future__ import annotations

import argparse
from pathlib import Path

from viewer_core.contracts import VIEWER_SVG_NAME
from viewer_core.svg_renderer import render_svg, write_viewer_svg


# Mantiene importabili le due funzioni pubbliche usate dagli altri script.
__all__ = ["render_svg", "write_viewer_svg"]


def main() -> None:
    """Legge la cartella della run e avvia il renderer SVG interno."""
    parser = argparse.ArgumentParser(description="Renderizza il viewer SVG generale della Pipeline 2.0.")
    parser.add_argument("--run-dir", required=True, help="Cartella run con gli artefatti 13 e 14.")
    args = parser.parse_args()

    # La risoluzione completa del percorso resta responsabilita del renderer.
    run_dir = Path(args.run_dir)
    write_viewer_svg(run_dir)
    print(f"Scritto {run_dir / VIEWER_SVG_NAME}")


if __name__ == "__main__":
    main()
