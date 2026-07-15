"""Definisce nomi e versioni condivisi dagli step 13, 14 e 15."""

from pathlib import Path


# La root viene calcolata qui per evitare dipendenze dalla posizione dei singoli builder.
PROJECT_ROOT = Path(__file__).resolve().parents[4]

NETLIST_NAME = "07_netlist.cir"
VIEWER_MODEL_NAME = "13_viewer_model.json"
VIEWER_LAYOUT_NAME = "14_viewer_layout.json"
VIEWER_SVG_NAME = "15_viewer.svg"

VIEWER_MODEL_SCHEMA_VERSION = 10
VIEWER_LAYOUT_SCHEMA_VERSION = 30
VIEWER_RENDER_VERSION = 9
