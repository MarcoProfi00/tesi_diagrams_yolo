from pathlib import Path

# =========================================================
# PATHS / INPUT-OUTPUT
# =========================================================
PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_DIR = PROJECT_ROOT / "outputs" / "topology_v3.1_mosfet_transistor" / "07_export_graph" / "graph_json"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "topology_v3.1_mosfet_transistor" / "08_visualize_graph"

# =========================================================
# OUTPUT SUBDIRECTORIES
# =========================================================
FULL_PNG_DIR = OUTPUT_DIR / "full_png"
FULL_HTML_DIR = OUTPUT_DIR / "full_html"
COMPONENT_NET_PNG_DIR = OUTPUT_DIR / "component_net_png"
COMPONENT_NET_HTML_DIR = OUTPUT_DIR / "component_net_html"
OVERLAY_DIR = OUTPUT_DIR / "overlay"

# =========================================================
# SAVE FLAGS
# =========================================================
SAVE_FULL_PNG = True
SAVE_FULL_HTML = True
SAVE_COMPONENT_NET_PNG = True
SAVE_COMPONENT_NET_HTML = True
SAVE_OVERLAY = True
SAVE_INDEX_HTML = True

# =========================================================
# VIEW OPTIONS
# =========================================================
# Alleggerisce la vista completa: i terminali restano nel grafo ma il testo può stare solo in hover.
SHOW_TERMINAL_LABELS_IN_FULL_PNG = False
SHOW_TERMINAL_LABELS_IN_FULL_HTML = False

# =========================================================
# STYLE CONSTANTS
# =========================================================
NODE_COLORS = {
    "Diagram": "#4C78A8",
    "Component": "#54A24B",
    "Terminal": "#F58518",
    "Net": "#B279A2",
}

EDGE_COLORS = {
    "HAS_COMPONENT": "#BDBDBD",
    "HAS_NET": "#D0D0D0",
    "HAS_TERMINAL": "#B07D62",
    "CONNECTED_TO": "#E45756",
}

LAYER_X = {
    "Diagram": 0.0,
    "Component": 2.0,
    "Terminal": 4.0,
    "Net": 6.0,
}

REL_POS_ORDER = {
    "top": 0,
    "left": 1,
    "right": 2,
    "bottom": 3,
}