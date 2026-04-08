"""
08_visualize_graph.py

Scopo:
    Generare visualizzazioni del grafo esportato dal passo 07.

Viste prodotte:
    - full graph
    - component -> net
    - overlay sul diagramma
    - index.html batch

Output:
    - PNG statiche
    - HTML interattive
    - dashboard index.html
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from graph_viz.config import (
    INPUT_DIR,
    OUTPUT_DIR,
    FULL_PNG_DIR,
    FULL_HTML_DIR,
    COMPONENT_NET_PNG_DIR,
    COMPONENT_NET_HTML_DIR,
    OVERLAY_DIR,
    SAVE_FULL_PNG,
    SAVE_FULL_HTML,
    SAVE_COMPONENT_NET_PNG,
    SAVE_COMPONENT_NET_HTML,
    SAVE_OVERLAY,
    SAVE_INDEX_HTML,
)
from graph_viz.io_utils import load_graph_json
from graph_viz.render_component_net import draw_component_net_png, draw_component_net_html
from graph_viz.render_overlay import draw_overlay
from graph_viz.dashboard import save_index_html
from graph_viz.render_full import draw_full_html, draw_full_png




# =========================================================
# MAIN
# =========================================================
def main() -> None:
    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"Cartella input non trovata: {INPUT_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if SAVE_FULL_PNG:
        FULL_PNG_DIR.mkdir(parents=True, exist_ok=True)
    if SAVE_FULL_HTML:
        FULL_HTML_DIR.mkdir(parents=True, exist_ok=True)
    if SAVE_COMPONENT_NET_PNG:
        COMPONENT_NET_PNG_DIR.mkdir(parents=True, exist_ok=True)
    if SAVE_COMPONENT_NET_HTML:
        COMPONENT_NET_HTML_DIR.mkdir(parents=True, exist_ok=True)
    if SAVE_OVERLAY:
        OVERLAY_DIR.mkdir(parents=True, exist_ok=True)

    json_files = sorted(INPUT_DIR.glob("*_graph.json"))
    if not json_files:
        raise FileNotFoundError(f"Nessun file *_graph.json trovato in: {INPUT_DIR}")

    print(f"Input directory : {INPUT_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"File trovati    : {len(json_files)}\\n")

    index_rows: list[dict[str, Any]] = []

    for i, json_path in enumerate(json_files, start=1):
        graph_data = load_graph_json(json_path)
        summary = graph_data.get("graph_summary", {})
        diagram_id = graph_data.get("graph_metadata", {}).get("diagram_id", json_path.stem.replace("_graph", ""))

        full_png_name = f"{diagram_id}_full_graph.png"
        full_html_name = f"{diagram_id}_full_graph.html"
        component_net_png_name = f"{diagram_id}_component_net.png"
        component_net_html_name = f"{diagram_id}_component_net.html"
        overlay_png_name = f"{diagram_id}_overlay.png"

        if SAVE_FULL_PNG:
            draw_full_png(graph_data, FULL_PNG_DIR / full_png_name)
        if SAVE_FULL_HTML:
            draw_full_html(graph_data, FULL_HTML_DIR / full_html_name)
        if SAVE_COMPONENT_NET_PNG:
            draw_component_net_png(graph_data, COMPONENT_NET_PNG_DIR / component_net_png_name)
        if SAVE_COMPONENT_NET_HTML:
            draw_component_net_html(graph_data, COMPONENT_NET_HTML_DIR / component_net_html_name)
        if SAVE_OVERLAY:
            draw_overlay(graph_data, OVERLAY_DIR / overlay_png_name)

        index_rows.append(
            {
                "diagram_id": diagram_id,
                "n_nodes_total": summary.get("n_nodes_total", 0),
                "n_edges_total": summary.get("n_edges_total", 0),
                "n_suspicious_terminal_matches": summary.get("n_suspicious_terminal_matches", 0),
                "full_png": full_png_name if SAVE_FULL_PNG else None,
                "full_html": full_html_name if SAVE_FULL_HTML else None,
                "component_net_png": component_net_png_name if SAVE_COMPONENT_NET_PNG else None,
                "component_net_html": component_net_html_name if SAVE_COMPONENT_NET_HTML else None,
                "overlay_png": overlay_png_name if SAVE_OVERLAY else None,
            }
        )

        print(
            f"[{i}/{len(json_files)}] {json_path.name} -> "
            f"nodes={summary.get('n_nodes_total')}, edges={summary.get('n_edges_total')}, "
            f"suspicious={summary.get('n_suspicious_terminal_matches', 0)}"
        )

    if SAVE_INDEX_HTML:
        index_path = OUTPUT_DIR / "index.html"
        save_index_html(index_rows, index_path)
        print(f"\nIndex HTML salvato in: {index_path}")

    print("\nCompletato.")
    if SAVE_FULL_PNG:
        print(f"Full PNG salvati in         : {FULL_PNG_DIR}")
    if SAVE_FULL_HTML:
        print(f"Full HTML salvati in        : {FULL_HTML_DIR}")
    if SAVE_COMPONENT_NET_PNG:
        print(f"Component-Net PNG salvati in: {COMPONENT_NET_PNG_DIR}")
    if SAVE_COMPONENT_NET_HTML:
        print(f"Component-Net HTML salvati in: {COMPONENT_NET_HTML_DIR}")
    if SAVE_OVERLAY:
        print(f"Overlay PNG salvati in      : {OVERLAY_DIR}")


if __name__ == "__main__":
    main()
