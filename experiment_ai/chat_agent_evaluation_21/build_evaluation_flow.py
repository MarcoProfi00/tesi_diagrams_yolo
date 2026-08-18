#!/usr/bin/env python3
"""Genera la Figura 2: valutazione di una singola esecuzione."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle


ROOT = Path(__file__).resolve().parent
FIGURES_DIR = ROOT / "results" / "figures"

INK = "#243746"
MUTED = "#60717E"
LINE = "#526574"
BLUE = "#2F6B9A"
BLUE_TINT = "#F2F7FB"
TEAL = "#237A78"
TEAL_TINT = "#F1F9F7"
PURPLE = "#6655A3"
PURPLE_TINT = "#F6F4FB"
GREEN = "#3A7D57"
GREEN_TINT = "#F2F8F4"
AMBER = "#B56B16"
AMBER_TINT = "#FFF8EC"
RED = "#B84A4A"

# Gerarchia tipografica condivisa da tutti gli elementi con la stessa funzione.
# Le dimensioni sono allineate a quelle della Figura 1 per una lettura uniforme
# quando le due immagini vengono riportate nello stesso capitolo.
FONT_PANEL_TITLE = 12.6
FONT_STEP_NUMBER = 11.2
FONT_CARD_TITLE = 11.2
FONT_ROLE = 8.8
FONT_BODY = 9.0
FONT_OUTPUT_TITLE = 11.2
FONT_OUTPUT_BODY = 9.0
FONT_JUDGE_TITLE = 11.8
FONT_FOOTER_VALUE = 11.5
FONT_FOOTER_TEXT = 9.2


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
        ha="center", va="center", fontsize=FONT_STEP_NUMBER,
        fontweight="bold", color="white", zorder=3,
    )
    ax.text(
        x + 0.64, y + h - 0.34, title,
        ha="left", va="center", fontsize=FONT_PANEL_TITLE,
        fontweight="bold", color=color, zorder=3,
    )


def card(ax, x: float, y: float, w: float, h: float, color: str,
         title: str, role: str, bullets: tuple[str, ...], *,
         title_size: float = FONT_CARD_TITLE) -> None:
    center_x = x + w / 2
    ax.add_patch(
        FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.025,rounding_size=0.10",
            linewidth=1.35,
            edgecolor=color,
            facecolor="white",
            zorder=4,
        )
    )
    ax.text(
        center_x, y + h - 0.38, title,
        ha="center", va="center", fontsize=title_size,
        fontweight="bold", color=INK, zorder=7,
    )
    role_width = min(max(1.28, 0.083 * len(role)), w - 0.44)
    role_x = center_x - role_width / 2
    ax.add_patch(
        FancyBboxPatch(
            (role_x, y + h - 0.865), role_width, 0.36,
            boxstyle="round,pad=0.01,rounding_size=0.06",
            linewidth=0, facecolor=color, alpha=0.12, zorder=5,
        )
    )
    ax.text(
        center_x, y + h - 0.685, role,
        ha="center", va="center", fontsize=FONT_ROLE,
        fontweight="bold", color=color, zorder=7,
    )
    start_y = y + h - 1.12
    for index, line in enumerate(bullets):
        yy = start_y - index * 0.35
        ax.add_patch(Circle((x + 0.29, yy), 0.035, color=color, zorder=6))
        ax.text(
            x + 0.43, yy, line,
            ha="left", va="center", fontsize=FONT_BODY,
            color=MUTED, zorder=7,
        )


def output_card(ax, x: float, y: float, w: float, h: float, color: str,
                tint: str, title: str, lines: tuple[str, ...],
                icon: str) -> None:
    ax.add_patch(
        FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.025,rounding_size=0.10",
            linewidth=1.3,
            edgecolor=color,
            facecolor=tint,
            zorder=4,
        )
    )
    icon_x, icon_y = x + 0.42, y + h / 2
    if icon == "score":
        for idx, height in enumerate((0.25, 0.43, 0.61)):
            ax.add_patch(Rectangle(
                (icon_x - 0.23 + idx * 0.18, icon_y - 0.30),
                0.10, height, facecolor=color, edgecolor="none", zorder=6,
            ))
    elif icon == "outcome":
        ax.add_patch(Circle((icon_x, icon_y), 0.27, facecolor="white",
                            edgecolor=color, linewidth=1.25, zorder=6))
        ax.plot([icon_x - 0.13, icon_x - 0.02, icon_x + 0.17],
                [icon_y - 0.01, icon_y - 0.13, icon_y + 0.13],
                color=color, linewidth=1.6, solid_capstyle="round", zorder=7)
    elif icon == "warning":
        triangle = Polygon(
            [[icon_x, icon_y + 0.30], [icon_x - 0.30, icon_y - 0.24],
             [icon_x + 0.30, icon_y - 0.24]],
            closed=True, facecolor="white", edgecolor=color,
            linewidth=1.25, zorder=6,
        )
        ax.add_patch(triangle)
        ax.text(icon_x, icon_y - 0.06, "!", ha="center", va="center",
                fontsize=11, fontweight="bold", color=color, zorder=7)
    else:
        raise ValueError(f"Icona output non supportata: {icon}")

    ax.text(x + 0.88, y + h - 0.34, title,
            ha="left", va="center", fontsize=FONT_OUTPUT_TITLE,
            fontweight="bold", color=INK, zorder=7)
    for index, line in enumerate(lines):
        ax.text(x + 0.88, y + h - 0.72 - index * 0.28, line,
                ha="left", va="center", fontsize=FONT_OUTPUT_BODY,
                color=MUTED, zorder=7)


def arrow(ax, start: tuple[float, float], end: tuple[float, float], *,
          color: str = LINE, linewidth: float = 1.45,
          dashed: bool = False, zorder: int = 3) -> None:
    ax.add_patch(
        FancyArrowPatch(
            start, end, arrowstyle="-|>", mutation_scale=11,
            linewidth=linewidth, color=color,
            linestyle=(0, (4, 3)) if dashed else "solid",
            shrinkA=0, shrinkB=0, zorder=zorder,
        )
    )


def polyline_arrow(ax, points: list[tuple[float, float]], *,
                   color: str = LINE, linewidth: float = 1.4,
                   dashed: bool = False, zorder: int = 2) -> None:
    linestyle = (0, (4, 3)) if dashed else "solid"
    for start, end in zip(points[:-2], points[1:-1], strict=True):
        ax.plot([start[0], end[0]], [start[1], end[1]],
                color=color, linewidth=linewidth, linestyle=linestyle,
                solid_capstyle="round", zorder=zorder)
    arrow(ax, points[-2], points[-1], color=color, linewidth=linewidth,
          dashed=dashed, zorder=zorder)


def icon_packet(ax, cx: float, cy: float, color: str) -> None:
    ax.add_patch(Rectangle((cx - 0.31, cy - 0.36), 0.62, 0.72,
                           fill=False, edgecolor=color, linewidth=1.25, zorder=6))
    ax.text(cx - 0.18, cy, "{", ha="center", va="center",
            fontsize=16, color=color, zorder=7)
    ax.text(cx + 0.18, cy, "}", ha="center", va="center",
            fontsize=16, color=color, zorder=7)
    for yy in (cy + 0.18, cy, cy - 0.18):
        ax.add_patch(Circle((cx - 0.03, yy), 0.023, color=color, zorder=7))
        ax.plot([cx + 0.04, cx + 0.20], [yy, yy],
                color=color, linewidth=1.0, zorder=7)


def icon_judge(ax, cx: float, cy: float, color: str) -> None:
    beam_y = cy + 0.17
    pan_y = cy - 0.13
    linewidth = 1.35

    # Montante, base e perno centrale.
    ax.plot([cx, cx], [cy - 0.36, cy + 0.32],
            color=color, linewidth=linewidth, zorder=6)
    ax.plot([cx - 0.25, cx + 0.25], [cy - 0.36, cy - 0.36],
            color=color, linewidth=linewidth, solid_capstyle="round", zorder=6)
    ax.add_patch(Circle((cx, cy + 0.34), 0.045, facecolor="white",
                        edgecolor=color, linewidth=1.2, zorder=7))
    ax.add_patch(Polygon(
        [[cx, beam_y - 0.10], [cx - 0.08, beam_y], [cx + 0.08, beam_y]],
        closed=True, facecolor="white", edgecolor=color,
        linewidth=1.1, zorder=7,
    ))

    # Traversa orizzontale e due piatti simmetrici con doppi tiranti.
    ax.plot([cx - 0.48, cx + 0.48], [beam_y, beam_y],
            color=color, linewidth=linewidth, solid_capstyle="round", zorder=6)
    for pan_cx in (cx - 0.36, cx + 0.36):
        ax.plot([pan_cx, pan_cx - 0.18], [beam_y, pan_y],
                color=color, linewidth=1.05, zorder=6)
        ax.plot([pan_cx, pan_cx + 0.18], [beam_y, pan_y],
                color=color, linewidth=1.05, zorder=6)
        ax.add_patch(Polygon(
            [[pan_cx - 0.20, pan_y], [pan_cx + 0.20, pan_y],
             [pan_cx + 0.13, pan_y - 0.12], [pan_cx - 0.13, pan_y - 0.12]],
            closed=True, facecolor="white", edgecolor=color,
            linewidth=1.15, zorder=6,
        ))


def build_figure() -> tuple[Path, Path, Path]:
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
    })

    fig, ax = plt.subplots(figsize=(16.0, 8.9), facecolor="white")
    fig.subplots_adjust(left=0.015, right=0.985, top=0.985, bottom=0.02)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 8.9)
    ax.set_aspect("equal")
    ax.axis("off")

    panel(ax, 0.25, 0.45, 4.30, 8.00, BLUE, BLUE_TINT,
          "1", "ARTEFATTI DI UNA ESECUZIONE")
    panel(ax, 4.75, 0.45, 6.40, 8.00, PURPLE, PURPLE_TINT,
          "2", "PREPARAZIONE E GIUDIZIO")
    panel(ax, 11.35, 0.45, 4.40, 8.00, TEAL, TEAL_TINT,
          "3", "RISULTATO STRUTTURATO")

    card(
        ax, 0.68, 4.78, 3.63, 2.72, BLUE,
        "Summary della traiettoria", "OGGETTO DA VALUTARE",
        (
            "sintomo e simulazione di base",
            "scenari, azioni e run SPICE",
            "confronti base–scenario",
            "risposta o conclusione finale",
        ),
    )
    card(
        ax, 0.68, 1.38, 3.63, 2.72, TEAL,
        "Ground truth tecnica", "RIFERIMENTO INDIPENDENTE",
        (
            "evidenze richieste e assunzioni",
            "condizioni di successo",
            "soluzioni tecnicamente ammissibili",
            "limiti e conclusioni non supportate",
        ),
    )

    # Le due fonti vengono mantenute distinte fino alla costruzione del packet.
    polyline_arrow(ax, [(4.31, 6.14), (4.45, 6.14), (4.45, 5.12), (5.12, 5.12)],
                   color=BLUE)
    polyline_arrow(ax, [(4.31, 2.74), (4.45, 2.74), (4.45, 3.72), (5.12, 3.72)],
                   color=TEAL)

    # Packet compatto e anonimo.
    ax.add_patch(FancyBboxPatch(
        (5.12, 3.22), 2.25, 2.40,
        boxstyle="round,pad=0.025,rounding_size=0.10",
        linewidth=1.35, edgecolor=PURPLE, facecolor="white", zorder=4,
    ))
    icon_packet(ax, 6.245, 4.95, PURPLE)
    ax.text(6.245, 4.42, "Judge packet", ha="center", va="center",
            fontsize=FONT_CARD_TITLE, fontweight="bold", color=INK, zorder=7)
    ax.text(6.245, 4.08, "summary + riferimento", ha="center", va="center",
            fontsize=FONT_BODY, color=MUTED, zorder=7)
    for yy, label in ((3.70, "campi rilevanti"),
                      (3.46, "modalità anonimizzata")):
        ax.add_patch(Circle((5.47, yy), 0.030, color=PURPLE, zorder=6))
        ax.text(5.59, yy, label, ha="left", va="center",
                fontsize=FONT_BODY, color=MUTED, zorder=7)

    arrow(ax, (7.37, 4.42), (7.72, 4.42), color=PURPLE)

    # Judge con rubric fissa.
    ax.add_patch(FancyBboxPatch(
        (7.72, 1.68), 3.15, 5.50,
        boxstyle="round,pad=0.025,rounding_size=0.12",
        linewidth=1.45, edgecolor=PURPLE, facecolor="white", zorder=4,
    ))
    icon_judge(ax, 9.295, 6.48, PURPLE)
    ax.text(9.295, 5.92, "LLM judge", ha="center", va="center",
            fontsize=FONT_JUDGE_TITLE, fontweight="bold", color=INK, zorder=7)
    ax.text(9.295, 5.60, "prompt, rubric e schema fissati", ha="center", va="center",
            fontsize=FONT_BODY, color=MUTED, zorder=7)

    criteria = (
        "Correttezza diagnostica",
        "Qualità dei test",
        "Interpretazione delle evidenze",
        "Raggiungimento dell'obiettivo",
        "Qualità della conclusione",
    )
    for index, criterion in enumerate(criteria):
        yy = 5.06 - index * 0.56
        ax.add_patch(FancyBboxPatch(
            (8.05, yy - 0.18), 0.55, 0.35,
            boxstyle="round,pad=0.01,rounding_size=0.08",
            linewidth=0, facecolor=PURPLE, alpha=0.13, zorder=5,
        ))
        ax.text(8.325, yy, "0–2", ha="center", va="center",
                fontsize=FONT_BODY, fontweight="bold", color=PURPLE, zorder=7)
        ax.text(8.76, yy, criterion, ha="left", va="center",
                fontsize=FONT_BODY, color=INK, zorder=7)

    ax.plot([8.05, 10.54], [2.10, 2.10], color="#DDD8ED", linewidth=1.0, zorder=5)
    ax.text(9.295, 1.90, "giudizio motivato dalle evidenze",
            ha="center", va="center", fontsize=FONT_BODY,
            fontweight="bold", color=PURPLE, zorder=7)

    # Tre famiglie di output, salvate nello stesso JSON del judge.
    output_card(
        ax, 11.78, 5.62, 3.72, 1.67, BLUE, BLUE_TINT,
        "Punteggi", ("cinque criteri da 0 a 2", "totale complessivo: 0–10"),
        "score",
    )
    output_card(
        ax, 11.78, 3.50, 3.72, 1.67, GREEN, GREEN_TINT,
        "Esito sintetico", ("success · partial_success · failure",
                            "inconclusive · technical_failure"),
        "outcome",
    )
    output_card(
        ax, 11.78, 1.38, 3.72, 1.67, RED, AMBER_TINT,
        "Eventuali criticità", ("false_success · unsupported_claim",
                                "wrong_interpretation"),
        "warning",
    )

    polyline_arrow(ax, [(10.87, 5.20), (11.12, 5.20), (11.12, 6.45), (11.78, 6.45)],
                   color=BLUE)
    arrow(ax, (10.87, 4.34), (11.78, 4.34), color=GREEN)
    polyline_arrow(ax, [(10.87, 3.48), (11.12, 3.48), (11.12, 2.21), (11.78, 2.21)],
                   color=RED)

    # Ripetizione del protocollo sul corpus completo.
    ax.add_patch(FancyBboxPatch(
        (5.18, 0.72), 5.53, 0.62,
        boxstyle="round,pad=0.02,rounding_size=0.10",
        linewidth=1.0, edgecolor=PURPLE, facecolor="#EEEAF8", zorder=4,
    ))
    ax.text(5.52, 1.03, "×42", ha="left", va="center",
            fontsize=FONT_FOOTER_VALUE, fontweight="bold", color=PURPLE, zorder=7)
    ax.text(6.25, 1.03,
            "stesso protocollo: 21 circuiti × 2 modalità",
            ha="left", va="center", fontsize=FONT_FOOTER_TEXT,
            fontweight="bold", color=INK, zorder=7)

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    png_path = FIGURES_DIR / "fig02_processo_valutazione.png"
    pdf_path = FIGURES_DIR / "fig02_processo_valutazione.pdf"
    svg_path = FIGURES_DIR / "fig02_processo_valutazione.svg"
    metadata = {
        "Title": "Processo di valutazione di una singola esecuzione",
        "Subject": "Summary e ground truth verso il risultato strutturato del judge",
        "Creator": "build_evaluation_flow.py",
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
