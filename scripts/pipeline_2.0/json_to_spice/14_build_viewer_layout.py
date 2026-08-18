"""Entry point dello step 14: calcola il layout generale del viewer."""

from __future__ import annotations

import argparse
from pathlib import Path

from viewer_core.contracts import VIEWER_LAYOUT_NAME
from viewer_core.layout_builder import build_viewer_layout, write_viewer_layout


def main() -> None:
    """Legge il modello dello step 13 e salva componenti, nodi e percorsi."""
    parser = argparse.ArgumentParser(
        description="Genera il layout viewer Pipeline 2.0 per una cartella run."
    )
    parser.add_argument(
        "--run-dir",
        required=True,
        help="Cartella run che contiene 13_viewer_model.json.",
    )
    args = parser.parse_args()
    run_dir = Path(args.run_dir)
    layout = write_viewer_layout(run_dir)
    print(f"Scritto {run_dir / VIEWER_LAYOUT_NAME}")
    print(f"Componenti posizionati: {len(layout.get('components') or {})}")


__all__ = ["build_viewer_layout", "write_viewer_layout"]


if __name__ == "__main__":
    main()
