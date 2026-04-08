from pathlib import Path


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