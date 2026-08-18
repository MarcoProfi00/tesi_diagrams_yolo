#!/usr/bin/env python3
"""Genera la Figura 1: flusso complessivo dell'applicativo."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle


ROOT = Path(__file__).resolve().parent
FIGURES_DIR = ROOT / "results" / "figures"

INK = "#243746"
MUTED = "#5F6F7C"
LINE = "#526574"
BLUE = "#2F6B9A"
BLUE_TINT = "#F2F7FB"
TEAL = "#237A78"
TEAL_TINT = "#F1F9F7"
PURPLE = "#6655A3"
PURPLE_TINT = "#F6F4FB"
ORANGE = "#C66A1B"

# Gerarchia tipografica unica per tutta la figura. Le costanti evitano che
# elementi con la stessa funzione visiva abbiano dimensioni diverse.
FONT_PANEL_TITLE = 11.5
FONT_STEP_NUMBER = 10.3
FONT_NODE_TITLE = 10.2
FONT_NODE_SUBTITLE = 8.0
FONT_AUXILIARY = 9.0
FONT_FLOW_LABEL = 7.9


def panel(ax, x: float, y: float, w: float, h: float, color: str, tint: str,
          number: str, title: str) -> None:
    ax.add_patch(
        FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.025,rounding_size=0.13",
            linewidth=1.15,
            edgecolor=color,
            facecolor=tint,
            zorder=0,
        )
    )
    ax.add_patch(Circle((x + 0.34, y + h - 0.34), 0.19, color=color, zorder=2))
    ax.text(
        x + 0.34, y + h - 0.34, number,
        ha="center", va="center", color="white", fontsize=FONT_STEP_NUMBER,
        fontweight="bold", zorder=3,
    )
    ax.text(
        x + 0.64, y + h - 0.34, title,
        ha="left", va="center", color=color, fontsize=FONT_PANEL_TITLE,
        fontweight="bold", zorder=3,
    )


def node(ax, x: float, y: float, w: float, h: float, color: str,
         title: str, subtitle: str = "", *, title_size: float = FONT_NODE_TITLE,
         subtitle_size: float = FONT_NODE_SUBTITLE, fill: str = "white") -> None:
    ax.add_patch(
        FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.025,rounding_size=0.09",
            linewidth=1.35,
            edgecolor=color,
            facecolor=fill,
            zorder=4,
        )
    )
    center_x = x + w / 2
    # Nei nodi senza sottotitolo la singola etichetta occupa il centro reale
    # del riquadro; negli altri resta allineata alla gerarchia titolo/sottotitolo.
    title_y = y + (h / 2 if not subtitle else 0.48)
    ax.text(
        center_x, title_y,
        title, ha="center", va="center", color=INK,
        fontsize=title_size, fontweight="bold", zorder=7,
    )
    if subtitle:
        ax.text(
            center_x, y + 0.19,
            subtitle, ha="center", va="center", color=MUTED,
            fontsize=subtitle_size, zorder=7,
        )


def mode_node(ax, x: float, y: float, color: str, title: str,
              subtitle: str, icon_kind: str) -> None:
    w, h = 2.30, 1.02
    ax.add_patch(
        FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.025,rounding_size=0.09",
            linewidth=1.35,
            edgecolor=color,
            facecolor="white",
            zorder=4,
        )
    )
    icon_x = x + 0.38
    icon_y = y + h / 2
    if icon_kind == "chat":
        icon_chat(ax, icon_x, icon_y, color)
    elif icon_kind == "agent":
        icon_robot(ax, icon_x, icon_y, color)
    else:
        raise ValueError(f"Icona modalità non supportata: {icon_kind}")
    ax.text(
        x + 1.43, y + 0.66, title,
        ha="center", va="center", color=INK,
        fontsize=FONT_NODE_TITLE, fontweight="bold", zorder=7,
    )
    ax.text(
        x + 1.43, y + 0.33, subtitle,
        ha="center", va="center", color=MUTED,
        fontsize=FONT_NODE_SUBTITLE, zorder=7,
    )


def arrow(ax, start: tuple[float, float], end: tuple[float, float], *,
          color: str = LINE, dashed: bool = False, connectionstyle: str = "arc3",
          linewidth: float = 1.45, zorder: int = 3) -> None:
    ax.add_patch(
        FancyArrowPatch(
            start, end,
            arrowstyle="-|>", mutation_scale=11,
            linewidth=linewidth, color=color,
            linestyle=(0, (4, 3)) if dashed else "solid",
            connectionstyle=connectionstyle,
            shrinkA=0, shrinkB=0, zorder=zorder,
        )
    )


def polyline_arrow(ax, points: list[tuple[float, float]], *, color: str,
                   dashed: bool = False, linewidth: float = 1.4,
                   zorder: int = 2) -> None:
    style = (0, (4, 3)) if dashed else "solid"
    for start, end in zip(points[:-2], points[1:-1], strict=True):
        ax.plot(
            [start[0], end[0]], [start[1], end[1]],
            color=color, linewidth=linewidth, linestyle=style,
            solid_capstyle="round", zorder=zorder,
        )
    arrow(
        ax, points[-2], points[-1], color=color, dashed=dashed,
        linewidth=linewidth, zorder=zorder,
    )


def icon_image(ax, cx: float, cy: float, color: str) -> None:
    ax.add_patch(Rectangle((cx - 0.28, cy - 0.23), 0.56, 0.46,
                           fill=False, edgecolor=color, linewidth=1.25, zorder=6))
    xs = [cx - 0.19, cx - 0.12, cx - 0.05, cx + 0.02, cx + 0.09, cx + 0.16]
    ys = [cy + 0.03, cy + 0.11, cy - 0.05, cy + 0.11, cy - 0.05, cy + 0.03]
    ax.plot(xs, ys, color=color, linewidth=1.25, zorder=6)
    ax.plot([cx - 0.19, cx - 0.19], [cy + 0.03, cy - 0.13],
            color=color, linewidth=1.25, zorder=6)
    ax.plot([cx + 0.16, cx + 0.16], [cy + 0.03, cy - 0.13],
            color=color, linewidth=1.25, zorder=6)


def icon_detection(ax, cx: float, cy: float, color: str) -> None:
    for dx, dy, size in ((-0.20, 0.08, 0.19), (0.08, 0.10, 0.23), (-0.03, -0.18, 0.21)):
        ax.add_patch(Rectangle((cx + dx, cy + dy), size, size,
                               fill=False, edgecolor=color, linewidth=1.2, zorder=6))
    ax.plot([cx - 0.12, cx + 0.03, cx + 0.18],
            [cy - 0.02, cy - 0.07, cy + 0.05],
            color=color, linewidth=1.1, zorder=6)


def icon_graph(ax, cx: float, cy: float, color: str) -> None:
    points = [(cx - 0.22, cy + 0.10), (cx + 0.20, cy + 0.16),
              (cx - 0.06, cy - 0.20), (cx + 0.25, cy - 0.15)]
    for i, j in ((0, 1), (0, 2), (1, 2), (1, 3), (2, 3)):
        ax.plot([points[i][0], points[j][0]], [points[i][1], points[j][1]],
                color=color, linewidth=1.1, zorder=6)
    for px, py in points:
        ax.add_patch(Circle((px, py), 0.055, facecolor="white",
                            edgecolor=color, linewidth=1.25, zorder=7))


def icon_transform(ax, cx: float, cy: float, color: str) -> None:
    ax.add_patch(Rectangle((cx - 0.30, cy - 0.20), 0.22, 0.40,
                           fill=False, edgecolor=color, linewidth=1.2, zorder=6))
    ax.add_patch(Rectangle((cx + 0.08, cy - 0.20), 0.22, 0.40,
                           fill=False, edgecolor=color, linewidth=1.2, zorder=6))
    arrow(ax, (cx - 0.03, cy), (cx + 0.04, cy), color=color,
          linewidth=1.1, zorder=6)
    ax.plot([cx - 0.25, cx - 0.13], [cy + 0.10, cy + 0.10],
            color=color, linewidth=1.0, zorder=6)
    ax.plot([cx + 0.13, cx + 0.25], [cy - 0.08, cy - 0.08],
            color=color, linewidth=1.0, zorder=6)


def icon_document(ax, cx: float, cy: float, color: str) -> None:
    ax.add_patch(Rectangle((cx - 0.23, cy - 0.27), 0.46, 0.54,
                           fill=False, edgecolor=color, linewidth=1.2, zorder=6))
    for offset, width in ((0.13, 0.27), (0.02, 0.31), (-0.09, 0.22), (-0.20, 0.29)):
        ax.plot([cx - 0.15, cx - 0.15 + width], [cy + offset, cy + offset],
                color=color, linewidth=1.05, zorder=6)


def icon_wave(ax, cx: float, cy: float, color: str) -> None:
    ax.plot([cx - 0.30, cx - 0.30, cx + 0.31],
            [cy + 0.23, cy - 0.23, cy - 0.23],
            color=color, linewidth=1.1, zorder=6)
    xs = [cx - 0.26 + idx * 0.03 for idx in range(18)]
    ys = [cy + 0.13 * __import__("math").sin(idx * 0.92) for idx in range(18)]
    ax.plot(xs, ys, color=color, linewidth=1.3, zorder=6)


def icon_viewer(ax, cx: float, cy: float, color: str) -> None:
    ax.add_patch(Rectangle((cx - 0.34, cy - 0.24), 0.68, 0.48,
                           fill=False, edgecolor=color, linewidth=1.2, zorder=6))
    ax.plot([cx - 0.25, cx - 0.10, cx + 0.02, cx + 0.23],
            [cy + 0.07, cy + 0.15, cy - 0.11, cy + 0.10],
            color=color, linewidth=1.15, zorder=6)
    for px, py in ((cx - 0.25, cy + 0.07), (cx - 0.10, cy + 0.15),
                   (cx + 0.02, cy - 0.11), (cx + 0.23, cy + 0.10)):
        ax.add_patch(Circle((px, py), 0.035, facecolor="white",
                            edgecolor=color, linewidth=1.0, zorder=7))


def icon_brain(ax, cx: float, cy: float, color: str) -> None:
    points = [(cx - 0.25, cy + 0.10), (cx, cy + 0.23), (cx + 0.25, cy + 0.08),
              (cx - 0.19, cy - 0.16), (cx + 0.10, cy - 0.20), (cx + 0.28, cy - 0.10)]
    for i, j in ((0, 1), (1, 2), (0, 3), (1, 4), (2, 5), (3, 4), (4, 5)):
        ax.plot([points[i][0], points[j][0]], [points[i][1], points[j][1]],
                color=color, linewidth=1.05, zorder=6)
    for px, py in points:
        ax.add_patch(Circle((px, py), 0.045, facecolor="white",
                            edgecolor=color, linewidth=1.15, zorder=7))


def icon_chat(ax, cx: float, cy: float, color: str) -> None:
    ax.add_patch(FancyBboxPatch((cx - 0.30, cy - 0.17), 0.60, 0.36,
                                boxstyle="round,pad=0.015,rounding_size=0.05",
                                fill=False, edgecolor=color, linewidth=1.2, zorder=6))
    ax.add_patch(Polygon([[cx - 0.14, cy - 0.17], [cx - 0.23, cy - 0.29],
                          [cx - 0.02, cy - 0.17]], closed=True,
                         fill=False, edgecolor=color, linewidth=1.2, zorder=6))
    for dx in (-0.13, 0.0, 0.13):
        ax.add_patch(Circle((cx + dx, cy + 0.01), 0.025, color=color, zorder=7))


def icon_robot(ax, cx: float, cy: float, color: str) -> None:
    ax.add_patch(FancyBboxPatch((cx - 0.27, cy - 0.19), 0.54, 0.38,
                                boxstyle="round,pad=0.015,rounding_size=0.06",
                                fill=False, edgecolor=color, linewidth=1.2, zorder=6))
    ax.plot([cx, cx], [cy + 0.19, cy + 0.29], color=color, linewidth=1.1, zorder=6)
    ax.add_patch(Circle((cx, cy + 0.31), 0.025, color=color, zorder=7))
    ax.add_patch(Circle((cx - 0.11, cy + 0.02), 0.032, color=color, zorder=7))
    ax.add_patch(Circle((cx + 0.11, cy + 0.02), 0.032, color=color, zorder=7))
    ax.plot([cx - 0.10, cx + 0.10], [cy - 0.10, cy - 0.10],
            color=color, linewidth=1.1, zorder=6)


def icon_compare(ax, cx: float, cy: float, color: str) -> None:
    ax.add_patch(Rectangle((cx - 0.31, cy - 0.20), 0.22, 0.40,
                           fill=False, edgecolor=color, linewidth=1.15, zorder=6))
    ax.add_patch(Rectangle((cx + 0.09, cy - 0.20), 0.22, 0.40,
                           fill=False, edgecolor=color, linewidth=1.15, zorder=6))
    arrow(ax, (cx - 0.04, cy), (cx + 0.05, cy), color=color,
          linewidth=1.05, zorder=6)


def icon_check(ax, cx: float, cy: float, color: str) -> None:
    ax.add_patch(Circle((cx, cy), 0.28, facecolor="white",
                        edgecolor=color, linewidth=1.3, zorder=6))
    ax.plot([cx - 0.14, cx - 0.03, cx + 0.17],
            [cy - 0.01, cy - 0.13, cy + 0.13],
            color=color, linewidth=1.7, solid_capstyle="round", zorder=7)


def build_figure() -> tuple[Path, Path, Path]:
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
    })

    fig, ax = plt.subplots(figsize=(16.0, 9.2), facecolor="white")
    fig.subplots_adjust(left=0.015, right=0.985, top=0.985, bottom=0.02)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9.2)
    ax.set_aspect("equal")
    ax.axis("off")

    panel(ax, 0.25, 5.10, 5.05, 3.78, BLUE, BLUE_TINT,
          "1", "RICOSTRUZIONE DALLO SCHEMA")
    panel(ax, 5.50, 5.10, 10.25, 3.78, TEAL, TEAL_TINT,
          "2", "MODELLAZIONE E SIMULAZIONE ELETTRICA")
    panel(ax, 0.25, 0.25, 15.50, 4.55, PURPLE, PURPLE_TINT,
          "3", "DIAGNOSI ASSISTITA DA INTELLIGENZA ARTIFICIALE")

    # Fase 1: immagine -> Pipeline 1.0 -> Graph JSON.
    node(ax, 0.58, 6.12, 1.30, 1.65, BLUE, "Schema", "immagine")
    icon_image(ax, 1.23, 7.21, BLUE)
    node(ax, 2.15, 6.12, 1.65, 1.65, BLUE, "Pipeline 1.0", "YOLO + topologia")
    icon_detection(ax, 2.98, 7.22, BLUE)
    node(ax, 4.08, 6.12, 0.95, 1.65, BLUE, "Graph", "JSON")
    icon_graph(ax, 4.55, 7.22, BLUE)
    arrow(ax, (1.88, 6.95), (2.15, 6.95))
    arrow(ax, (3.80, 6.95), (4.08, 6.95))

    # Fase 2: traduzione elettrica, netlist, simulazione e viewer.
    node(ax, 5.84, 6.12, 1.68, 1.65, TEAL, "Pipeline 2.0", "mapping elettrico")
    icon_transform(ax, 6.68, 7.22, TEAL)
    node(ax, 7.93, 6.12, 1.34, 1.65, TEAL, "Netlist", "SPICE")
    icon_document(ax, 8.60, 7.22, TEAL)
    node(ax, 9.68, 6.12, 1.50, 1.65, TEAL, "ngspice", "OP / TRAN")
    icon_wave(ax, 10.43, 7.22, TEAL)
    node(ax, 11.59, 6.12, 3.82, 1.65, TEAL, "Viewer ed evidenze", "circuito + misure SPICE")
    icon_viewer(ax, 13.50, 7.22, TEAL)
    arrow(ax, (5.03, 6.95), (5.84, 6.95))
    arrow(ax, (7.52, 6.95), (7.93, 6.95))
    arrow(ax, (9.27, 6.95), (9.68, 6.95))
    arrow(ax, (11.18, 6.95), (11.59, 6.95))

    # Input ausiliari della Pipeline 2.0.
    node(ax, 5.89, 5.32, 1.18, 0.54, TEAL, "values.yaml", "",
         title_size=FONT_AUXILIARY)
    node(ax, 7.20, 5.32, 2.20, 0.54, TEAL, "Macromodelli SPICE per IC", "",
         title_size=FONT_AUXILIARY)
    arrow(ax, (6.48, 5.86), (6.48, 6.12), color=TEAL, linewidth=1.15)
    polyline_arrow(
        ax,
        [(8.30, 5.86), (8.30, 5.98), (7.17, 5.98), (7.17, 6.12)],
        color=TEAL, linewidth=1.15, zorder=3,
    )

    # Fase 3: sintomo, ragionamento LLM, scelta della modalità e diagnosi.
    node(ax, 0.62, 1.45, 1.72, 1.55, PURPLE, "Sintomo", "domanda utente")
    icon_chat(ax, 1.48, 2.53, PURPLE)
    node(ax, 2.82, 1.45, 2.02, 1.55, PURPLE, "Agente diagnostico", "LLM + contesto tecnico")
    icon_brain(ax, 3.83, 2.53, PURPLE)
    arrow(ax, (2.34, 2.22), (2.82, 2.22))

    diamond = Polygon(
        [[5.85, 3.01], [6.65, 2.22], [5.85, 1.43], [5.05, 2.22]],
        closed=True, facecolor="white", edgecolor=PURPLE,
        linewidth=1.35, zorder=4,
    )
    ax.add_patch(diamond)
    ax.text(5.85, 2.33, "Modalità", ha="center", va="center",
            fontsize=FONT_NODE_TITLE, fontweight="bold", color=INK, zorder=7)
    ax.text(5.85, 2.09, "scelta dall'utente", ha="center", va="center",
            fontsize=FONT_NODE_SUBTITLE, color=MUTED, zorder=7)
    arrow(ax, (4.84, 2.22), (5.05, 2.22))

    mode_node(ax, 7.08, 2.64, BLUE, "CHAT", "scelta guidata", "chat")
    mode_node(ax, 7.08, 0.80, ORANGE, "AGENT", "azione autonoma", "agent")
    polyline_arrow(ax, [(6.65, 2.22), (6.84, 2.22), (6.84, 3.15), (7.08, 3.15)],
                   color=BLUE, linewidth=1.35, zorder=3)
    polyline_arrow(ax, [(6.65, 2.22), (6.84, 2.22), (6.84, 1.31), (7.08, 1.31)],
                   color=ORANGE, linewidth=1.35, zorder=3)

    node(ax, 9.62, 1.45, 2.25, 1.55, PURPLE, "Verifica di scenario", "copia isolata e confronto")
    icon_compare(ax, 10.75, 2.53, PURPLE)
    polyline_arrow(ax, [(9.38, 3.15), (9.50, 3.15), (9.50, 2.52), (9.62, 2.52)],
                   color=BLUE, linewidth=1.35, zorder=3)
    polyline_arrow(ax, [(9.38, 1.31), (9.50, 1.31), (9.50, 1.88), (9.62, 1.88)],
                   color=ORANGE, linewidth=1.35, zorder=3)

    node(ax, 12.50, 1.45, 2.62, 1.55, PURPLE, "Diagnosi motivata", "causa, evidenze e correzione")
    icon_check(ax, 13.81, 2.53, PURPLE)
    arrow(ax, (11.87, 2.22), (12.50, 2.22), color=PURPLE)

    # Collegamenti tra simulatore e agente: contesto iniziale e ciclo di test.
    polyline_arrow(
        ax,
        [(12.80, 6.12), (12.80, 4.22), (3.83, 4.22), (3.83, 3.00)],
        color=LINE, linewidth=1.35, zorder=2,
    )
    ax.text(7.95, 4.28, "contesto circuitale e risultati della simulazione",
            ha="center", va="bottom", fontsize=FONT_FLOW_LABEL, color=MUTED, zorder=5)

    polyline_arrow(
        ax,
        [(10.75, 3.00), (10.75, 4.00), (10.43, 4.00), (10.43, 6.12)],
        color=ORANGE, dashed=True, linewidth=1.35, zorder=2,
    )
    ax.text(10.97, 4.95, "nuova run SPICE",
            ha="center", va="center", fontsize=FONT_FLOW_LABEL, color=ORANGE,
            zorder=5)

    # Legenda minimale: distingue il flusso ordinario dal ciclo iterativo.
    ax.plot([13.25, 14.00], [4.35, 4.35], color=LINE, linewidth=1.45, zorder=5)
    arrow(ax, (13.78, 4.35), (14.00, 4.35), color=LINE, linewidth=1.45, zorder=5)
    ax.text(14.08, 4.35, "flusso principale", ha="left", va="center",
            fontsize=FONT_FLOW_LABEL, color=MUTED, zorder=5)
    ax.plot([13.25, 14.00], [4.08, 4.08], color=ORANGE, linewidth=1.35,
            linestyle=(0, (4, 3)), zorder=5)
    arrow(ax, (13.78, 4.08), (14.00, 4.08), color=ORANGE, dashed=True,
          linewidth=1.35, zorder=5)
    ax.text(14.08, 4.08, "ciclo di verifica", ha="left", va="center",
            fontsize=FONT_FLOW_LABEL, color=MUTED, zorder=5)

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    png_path = FIGURES_DIR / "fig01_flusso_applicativo.png"
    pdf_path = FIGURES_DIR / "fig01_flusso_applicativo.pdf"
    svg_path = FIGURES_DIR / "fig01_flusso_applicativo.svg"
    metadata = {
        "Title": "Flusso complessivo dell'applicativo",
        "Subject": "Dallo schema circuitale alla diagnosi assistita da AI",
        "Creator": "build_application_flow.py",
    }
    fig.savefig(png_path, dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(pdf_path, bbox_inches="tight", facecolor="white", metadata=metadata)
    svg_metadata = {
        "Title": metadata["Title"],
        "Description": metadata["Subject"],
        "Creator": metadata["Creator"],
    }
    fig.savefig(svg_path, bbox_inches="tight", facecolor="white", metadata=svg_metadata)
    plt.close(fig)
    return png_path, pdf_path, svg_path


def main() -> int:
    for path in build_figure():
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
