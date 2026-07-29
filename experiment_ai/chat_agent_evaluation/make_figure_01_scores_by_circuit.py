#!/usr/bin/env python3
"""Genera in PNG le figure principali dei risultati CHAT–AGENT.

Lo script legge ``_aggregate/pairs.csv`` e ``criteria_summary.csv``. Non
contiene punteggi o circuiti hardcoded.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import re
import statistics
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Patch


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_AGGREGATE_DIR = SCRIPT_DIR / "_aggregate"
DEFAULT_OUTPUT_DIR = DEFAULT_AGGREGATE_DIR / "figures"

CHAT_COLOR = "#356E9F"
AGENT_COLOR = "#D9822B"
TEXT_COLOR = "#202832"
GRID_COLOR = "#DCE2E7"
SEPARATOR_COLOR = "#AEB8C2"
WHITE = "#FFFFFF"

CRITERIA = (
    "task_achievement",
    "technical_correctness",
    "scenario_quality",
    "evidence_interpretation",
    "conclusion_quality",
)
CRITERION_LABELS_EN = {
    "task_achievement": "Goal achievement",
    "technical_correctness": "Technical correctness",
    "scenario_quality": "Scenario quality",
    "evidence_interpretation": "Evidence interpretation",
    "conclusion_quality": "Conclusion quality",
}
CRITERION_LABELS_EN_MULTILINE = {
    "task_achievement": "Goal\nachievement",
    "technical_correctness": "Technical\ncorrectness",
    "scenario_quality": "Scenario\nquality",
    "evidence_interpretation": "Evidence\ninterpretation",
    "conclusion_quality": "Conclusion\nquality",
}
CRITERION_LABELS_IT = {
    "task_achievement": "Obiettivo raggiunto",
    "technical_correctness": "Correttezza tecnica",
    "scenario_quality": "Qualità degli scenari",
    "evidence_interpretation": "Interpretazione delle evidenze",
    "conclusion_quality": "Qualità della conclusione",
}


class FigureDataError(ValueError):
    """Indica dati aggregati mancanti o incoerenti."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genera i grafici principali dei risultati CHAT–AGENT."
    )
    parser.add_argument(
        "--aggregate-dir",
        type=Path,
        default=DEFAULT_AGGREGATE_DIR,
        help="Cartella contenente pairs.csv e criteria_summary.csv.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Cartella in cui salvare figura e caption.",
    )
    return parser.parse_args()


def read_pairs(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise FigureDataError(
            f"File non trovato: {path}. Eseguire prima aggregate_results.py."
        )

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        raw_rows = list(csv.DictReader(handle))
    if not raw_rows:
        raise FigureDataError(f"Nessun risultato presente in {path}")

    required = {
        "circuit_id",
        "chat_score",
        "agent_score",
        "chat_user_turns",
    }
    required.update(
        f"{mode}_{criterion}"
        for mode in ("chat", "agent")
        for criterion in CRITERIA
    )
    if not required.issubset(raw_rows[0]):
        missing = ", ".join(sorted(required - set(raw_rows[0])))
        raise FigureDataError(f"Campi mancanti in pairs.csv: {missing}")

    seen: set[str] = set()
    rows: list[dict[str, Any]] = []
    for raw in raw_rows:
        circuit_id = (raw.get("circuit_id") or "").strip()
        if not circuit_id:
            raise FigureDataError("Trovato un circuit_id vuoto in pairs.csv")
        if circuit_id in seen:
            raise FigureDataError(f"Circuito duplicato in pairs.csv: {circuit_id}")
        seen.add(circuit_id)

        try:
            chat_score = float(raw["chat_score"])
            agent_score = float(raw["agent_score"])
        except (TypeError, ValueError) as exc:
            raise FigureDataError(
                f"Punteggio non numerico per il circuito {circuit_id}"
            ) from exc
        for mode, score in (("CHAT", chat_score), ("AGENT", agent_score)):
            if not 0 <= score <= 100:
                raise FigureDataError(
                    f"Punteggio {mode} fuori scala per {circuit_id}: {score}"
                )

        try:
            chat_user_turns = int(raw["chat_user_turns"])
        except (TypeError, ValueError) as exc:
            raise FigureDataError(
                f"Numero di turni CHAT non valido per {circuit_id}"
            ) from exc
        if chat_user_turns < 1:
            raise FigureDataError(
                f"Turni CHAT insufficienti per {circuit_id}: {chat_user_turns}"
            )

        criterion_scores: dict[str, dict[str, int]] = {"chat": {}, "agent": {}}
        for mode in ("chat", "agent"):
            for criterion in CRITERIA:
                field = f"{mode}_{criterion}"
                try:
                    score = int(raw[field])
                except (TypeError, ValueError) as exc:
                    raise FigureDataError(
                        f"Punteggio non intero per {circuit_id}/{field}"
                    ) from exc
                if not 0 <= score <= 4:
                    raise FigureDataError(
                        f"Punteggio fuori scala per {circuit_id}/{field}: {score}"
                    )
                criterion_scores[mode][criterion] = score

        rows.append(
            {
                "circuit_id": circuit_id,
                "chat_score": chat_score,
                "agent_score": agent_score,
                "chat_user_turns": chat_user_turns,
                "criteria": criterion_scores,
            }
        )
    return rows


def read_criteria(path: Path) -> tuple[list[dict[str, Any]], int]:
    if not path.is_file():
        raise FigureDataError(
            f"File non trovato: {path}. Eseguire prima aggregate_results.py."
        )

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        raw_rows = list(csv.DictReader(handle))
    if not raw_rows:
        raise FigureDataError(f"Nessun risultato presente in {path}")

    required = {"mode", "criterion", "mean_score_0_4", "n"}
    if not required.issubset(raw_rows[0]):
        missing = ", ".join(sorted(required - set(raw_rows[0])))
        raise FigureDataError(f"Campi mancanti in criteria_summary.csv: {missing}")

    selected = [
        row for row in raw_rows if (row.get("analysis_set") or "all") == "all"
    ]
    lookup = {
        ((row.get("mode") or "").strip(), (row.get("criterion") or "").strip()): row
        for row in selected
    }

    output: list[dict[str, Any]] = []
    sample_sizes: set[int] = set()
    for criterion in CRITERIA:
        scores: dict[str, float] = {}
        for mode in ("chat", "agent"):
            row = lookup.get((mode, criterion))
            if row is None:
                raise FigureDataError(
                    f"Riga mancante per {mode}/{criterion} in criteria_summary.csv"
                )
            try:
                score = float(row["mean_score_0_4"])
                sample_size = int(row["n"])
            except (TypeError, ValueError) as exc:
                raise FigureDataError(
                    f"Valori non numerici per {mode}/{criterion}"
                ) from exc
            if not 0 <= score <= 4:
                raise FigureDataError(
                    f"Punteggio medio fuori scala per {mode}/{criterion}: {score}"
                )
            if sample_size <= 0:
                raise FigureDataError(
                    f"Campione non valido per {mode}/{criterion}: {sample_size}"
                )
            scores[mode] = score
            sample_sizes.add(sample_size)

        output.append(
            {
                "criterion": criterion,
                "chat_score": scores["chat"],
                "agent_score": scores["agent"],
            }
        )

    if len(sample_sizes) != 1:
        raise FigureDataError(
            "Numero di valutazioni non uniforme in criteria_summary.csv"
        )
    return output, sample_sizes.pop()


def circuit_group(circuit_id: str) -> str:
    match = re.match(r"([A-Za-z]+)", circuit_id)
    return match.group(1).upper() if match else circuit_id.upper()


def format_score(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return f"{value:.1f}"


def format_mean(value: float) -> str:
    """Formato italiano usato nelle didascalie della tesi."""
    return f"{value:.2f}".replace(".", ",")


def format_mean_figure(value: float) -> str:
    """Formato internazionale usato nel testo interno delle figure."""
    return f"{value:.2f}"


def configure_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.labelsize": 11,
            "axes.labelcolor": TEXT_COLOR,
            "axes.edgecolor": "#8C97A2",
            "axes.linewidth": 0.8,
            "xtick.color": TEXT_COLOR,
            "ytick.color": TEXT_COLOR,
            "text.color": TEXT_COLOR,
            "figure.facecolor": WHITE,
            "axes.facecolor": WHITE,
            "savefig.facecolor": WHITE,
            "savefig.bbox": "tight",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )


def add_score_label(
    ax: plt.Axes,
    score: float,
    x_position: float,
    horizontal_alignment: str,
) -> None:
    """Scrive il valore nella barra, o sopra se la barra è molto corta."""
    if score >= 15:
        y_position = score - 3.0
        vertical_alignment = "top"
        color = WHITE
    else:
        y_position = score + 1.0
        vertical_alignment = "bottom"
        color = TEXT_COLOR

    ax.text(
        x_position,
        y_position,
        format_score(score),
        ha=horizontal_alignment,
        va=vertical_alignment,
        fontsize=8.5,
        fontweight="semibold",
        color=color,
        zorder=5,
    )


def save_figure(fig: plt.Figure, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=320)
    plt.close(fig)


def make_figure_01(
    rows: list[dict[str, Any]],
    output_dir: Path,
) -> tuple[float, float]:
    chat_mean = statistics.fmean(row["chat_score"] for row in rows)
    agent_mean = statistics.fmean(row["agent_score"] for row in rows)

    fig, ax = plt.subplots(figsize=(12.4, 5.6))

    x_positions = list(range(len(rows)))
    bar_width = 0.38

    ax.bar(
        [value - bar_width / 2 for value in x_positions],
        [row["chat_score"] for row in rows],
        width=bar_width,
        color=CHAT_COLOR,
        edgecolor=WHITE,
        linewidth=0.6,
        zorder=3,
    )
    ax.bar(
        [value + bar_width / 2 for value in x_positions],
        [row["agent_score"] for row in rows],
        width=bar_width,
        color=AGENT_COLOR,
        edgecolor=WHITE,
        linewidth=0.6,
        zorder=3,
    )

    for index, row in enumerate(rows):
        # I valori partono dal confine condiviso e si sviluppano verso
        # l'interno delle rispettive barre, evitando testi come "100100".
        add_score_label(ax, row["chat_score"], index - 0.035, "right")
        add_score_label(ax, row["agent_score"], index + 0.035, "left")

    groups = [circuit_group(row["circuit_id"]) for row in rows]
    for index in range(1, len(groups)):
        if groups[index] != groups[index - 1]:
            ax.axvline(
                index - 0.5,
                color=SEPARATOR_COLOR,
                linewidth=1.0,
                linestyle=(0, (3, 3)),
                zorder=2,
            )

    ax.set_xticks(
        x_positions,
        [row["circuit_id"].upper() for row in rows],
    )
    ax.set_xlim(-0.6, len(rows) - 0.4)
    ax.set_ylim(0, 104)
    ax.set_yticks(range(0, 101, 20))
    ax.set_xlabel("Circuit", labelpad=10)
    ax.set_ylabel("Judge score (0–100)", labelpad=10)
    ax.grid(axis="y", color=GRID_COLOR, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.suptitle(
        "CHAT and AGENT scores by circuit",
        x=0.50,
        y=0.975,
        ha="center",
        va="top",
        fontsize=15,
        fontweight="semibold",
        color=TEXT_COLOR,
    )
    legend_handles = [
        Patch(
            facecolor=CHAT_COLOR,
            edgecolor="none",
            label=f"CHAT · mean {format_mean_figure(chat_mean)}",
        ),
        Patch(
            facecolor=AGENT_COLOR,
            edgecolor="none",
            label=f"AGENT · mean {format_mean_figure(agent_mean)}",
        ),
    ]
    ax.legend(
        handles=legend_handles,
        loc="lower center",
        bbox_to_anchor=(0.5, 1.005),
        ncol=2,
        frameon=False,
        handlelength=1.6,
        columnspacing=2.4,
        fontsize=9.5,
    )

    fig.subplots_adjust(left=0.08, right=0.98, top=0.88, bottom=0.13)
    output_path = output_dir / "fig01_punteggi_chat_agent_per_circuito.png"
    save_figure(fig, output_path)
    return chat_mean, agent_mean


def add_criterion_label(
    ax: plt.Axes,
    score: float,
    y_position: float,
) -> None:
    if score >= 0.65:
        x_position = score - 0.07
        horizontal_alignment = "right"
        color = WHITE
    else:
        x_position = score + 0.05
        horizontal_alignment = "left"
        color = TEXT_COLOR

    ax.text(
        x_position,
        y_position,
        format_mean_figure(score),
        ha=horizontal_alignment,
        va="center",
        fontsize=9,
        fontweight="semibold",
        color=color,
        zorder=5,
    )


def make_figure_02(
    rows: list[dict[str, Any]],
    output_dir: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(8.8, 4.7))

    y_positions = list(range(len(rows)))
    bar_height = 0.34
    vertical_offset = bar_height / 2

    ax.barh(
        [value - vertical_offset for value in y_positions],
        [row["chat_score"] for row in rows],
        height=bar_height,
        color=CHAT_COLOR,
        edgecolor=WHITE,
        linewidth=0.6,
        zorder=3,
    )
    ax.barh(
        [value + vertical_offset for value in y_positions],
        [row["agent_score"] for row in rows],
        height=bar_height,
        color=AGENT_COLOR,
        edgecolor=WHITE,
        linewidth=0.6,
        zorder=3,
    )

    for index, row in enumerate(rows):
        add_criterion_label(ax, row["chat_score"], index - vertical_offset)
        add_criterion_label(ax, row["agent_score"], index + vertical_offset)

    ax.set_yticks(
        y_positions,
        [CRITERION_LABELS_EN[row["criterion"]] for row in rows],
    )
    ax.invert_yaxis()
    ax.set_xlim(0, 4.05)
    ax.set_xticks([0, 1, 2, 3, 4])
    ax.set_xlabel("Average score (0–4)", labelpad=10)
    ax.grid(axis="x", color=GRID_COLOR, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.suptitle(
        "Average judge scores by evaluation criterion",
        x=0.50,
        y=0.975,
        ha="center",
        va="top",
        fontsize=15,
        fontweight="semibold",
        color=TEXT_COLOR,
    )
    ax.legend(
        handles=[
            Patch(facecolor=CHAT_COLOR, edgecolor="none", label="CHAT"),
            Patch(facecolor=AGENT_COLOR, edgecolor="none", label="AGENT"),
        ],
        loc="lower center",
        bbox_to_anchor=(0.5, 1.005),
        ncol=2,
        frameon=False,
        handlelength=1.6,
        columnspacing=2.4,
        fontsize=9.5,
    )

    fig.subplots_adjust(left=0.28, right=0.97, top=0.82, bottom=0.16)
    output_path = output_dir / "fig02_valutazione_media_criteri.png"
    save_figure(fig, output_path)


def make_figure_03(
    rows: list[dict[str, Any]],
    output_dir: Path,
) -> None:
    chat_matrix = [
        [row["criteria"]["chat"][criterion] for criterion in CRITERIA]
        for row in rows
    ]
    agent_matrix = [
        [row["criteria"]["agent"][criterion] for criterion in CRITERIA]
        for row in rows
    ]

    fig = plt.figure(figsize=(11.8, 7.4))
    grid = fig.add_gridspec(
        1,
        3,
        width_ratios=(1, 1, 0.055),
        wspace=0.12,
    )
    chat_ax = fig.add_subplot(grid[0, 0])
    agent_ax = fig.add_subplot(grid[0, 1], sharey=chat_ax)
    colorbar_ax = fig.add_subplot(grid[0, 2])

    color_map = plt.get_cmap("Blues")
    chat_image = chat_ax.imshow(
        chat_matrix,
        cmap=color_map,
        vmin=0,
        vmax=4,
        aspect="auto",
        interpolation="nearest",
    )
    agent_ax.imshow(
        agent_matrix,
        cmap=color_map,
        vmin=0,
        vmax=4,
        aspect="auto",
        interpolation="nearest",
    )

    x_labels = [CRITERION_LABELS_EN_MULTILINE[item] for item in CRITERIA]
    circuit_labels = [row["circuit_id"].upper() for row in rows]
    for ax, panel_title, matrix in (
        (chat_ax, "CHAT", chat_matrix),
        (agent_ax, "AGENT", agent_matrix),
    ):
        ax.set_title(
            panel_title,
            fontsize=12,
            fontweight="semibold",
            color=TEXT_COLOR,
            pad=10,
        )
        ax.set_xticks(range(len(CRITERIA)), x_labels)
        ax.tick_params(axis="x", labelsize=8.5, length=0, pad=8)
        ax.tick_params(axis="y", length=0, pad=7)

        ax.set_xticks(
            [value - 0.5 for value in range(1, len(CRITERIA))],
            minor=True,
        )
        ax.set_yticks(
            [value - 0.5 for value in range(1, len(rows))],
            minor=True,
        )
        ax.grid(which="minor", color=WHITE, linewidth=1.4)
        ax.tick_params(which="minor", bottom=False, left=False)
        for spine in ax.spines.values():
            spine.set_visible(False)

        for row_index, values in enumerate(matrix):
            for column_index, value in enumerate(values):
                text_color = WHITE if value >= 3 else TEXT_COLOR
                ax.text(
                    column_index,
                    row_index,
                    str(value),
                    ha="center",
                    va="center",
                    fontsize=8.5,
                    fontweight="semibold",
                    color=text_color,
                )

    chat_ax.set_yticks(range(len(rows)), circuit_labels)
    chat_ax.tick_params(axis="y", labelsize=8.5)
    agent_ax.tick_params(axis="y", labelleft=False)

    groups = [circuit_group(row["circuit_id"]) for row in rows]
    for index in range(1, len(groups)):
        if groups[index] != groups[index - 1]:
            for ax in (chat_ax, agent_ax):
                ax.axhline(
                    index - 0.5,
                    color=SEPARATOR_COLOR,
                    linewidth=1.2,
                    linestyle=(0, (3, 3)),
                )

    colorbar = fig.colorbar(chat_image, cax=colorbar_ax, ticks=[0, 1, 2, 3, 4])
    colorbar.set_label("Judge score (0–4)", fontsize=10, labelpad=10)
    colorbar.ax.tick_params(labelsize=9)
    colorbar.outline.set_edgecolor("#8C97A2")
    colorbar.outline.set_linewidth(0.8)

    fig.suptitle(
        "Criterion scores by circuit and interaction mode",
        x=0.50,
        y=0.975,
        ha="center",
        va="top",
        fontsize=15,
        fontweight="semibold",
        color=TEXT_COLOR,
    )
    fig.subplots_adjust(left=0.09, right=0.94, top=0.89, bottom=0.14)
    output_path = output_dir / "fig03_criterion_scores_heatmap.png"
    save_figure(fig, output_path)


def add_bar_value(
    ax: plt.Axes,
    x_position: float,
    value: float,
    vertical_offset: float,
) -> None:
    """Mostra il valore sopra la barra, incluso il caso di valore nullo."""
    y_position = value + vertical_offset if value > 0 else vertical_offset
    ax.text(
        x_position,
        y_position,
        format_mean_figure(value),
        ha="center",
        va="bottom",
        fontsize=10,
        fontweight="semibold",
        color=TEXT_COLOR,
        zorder=5,
    )


def make_figure_04(
    rows: list[dict[str, Any]],
    output_dir: Path,
) -> tuple[float, float, float, float]:
    """Confronta qualità media e quantità di guida umana intermedia."""
    chat_score_mean = statistics.fmean(row["chat_score"] for row in rows)
    agent_score_mean = statistics.fmean(row["agent_score"] for row in rows)

    # Ogni run CHAT include la richiesta iniziale. Sottraendola restano i
    # messaggi con cui l'utente guida scenari, verifiche e conclusione.
    chat_intermediate_messages = statistics.fmean(
        row["chat_user_turns"] - 1 for row in rows
    )
    # Per definizione del workflow AGENT, dopo la richiesta iniziale non
    # vengono inviati altri messaggi dell'utente.
    agent_intermediate_messages = 0.0

    fig, (score_ax, messages_ax) = plt.subplots(
        1,
        2,
        figsize=(9.2, 4.9),
    )
    x_positions = [0, 1]
    colors = [CHAT_COLOR, AGENT_COLOR]
    bar_width = 0.58

    score_values = [chat_score_mean, agent_score_mean]
    score_ax.bar(
        x_positions,
        score_values,
        width=bar_width,
        color=colors,
        edgecolor=WHITE,
        linewidth=0.7,
        zorder=3,
    )
    for x_position, value in zip(x_positions, score_values, strict=True):
        add_bar_value(score_ax, x_position, value, 1.5)

    score_ax.set_title(
        "Mean judge score",
        fontsize=11.5,
        fontweight="semibold",
        pad=10,
    )
    score_ax.set_ylabel("Score (0–100)", labelpad=8)
    score_ax.set_ylim(0, 105)
    score_ax.set_yticks(range(0, 101, 20))

    message_values = [chat_intermediate_messages, agent_intermediate_messages]
    messages_ax.bar(
        x_positions,
        message_values,
        width=bar_width,
        color=colors,
        edgecolor=WHITE,
        linewidth=0.7,
        zorder=3,
    )
    for x_position, value in zip(x_positions, message_values, strict=True):
        add_bar_value(messages_ax, x_position, value, 0.10)

    message_axis_max = max(5.0, chat_intermediate_messages * 1.25)
    messages_ax.set_title(
        "Mean intermediate user messages",
        fontsize=11.5,
        fontweight="semibold",
        pad=10,
    )
    messages_ax.set_ylabel("Messages per circuit", labelpad=8)
    messages_ax.set_xlabel(
        "Initial request excluded",
        fontsize=9,
        color="#5E6974",
        labelpad=8,
    )
    messages_ax.set_ylim(0, message_axis_max)
    messages_ax.set_yticks(
        range(0, int(message_axis_max) + 1),
    )

    for ax in (score_ax, messages_ax):
        ax.set_xticks(x_positions, ["CHAT", "AGENT"])
        ax.grid(axis="y", color=GRID_COLOR, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    fig.suptitle(
        "Quality and autonomy trade-off",
        x=0.50,
        y=0.975,
        ha="center",
        va="top",
        fontsize=15,
        fontweight="semibold",
        color=TEXT_COLOR,
    )
    fig.legend(
        handles=[
            Patch(facecolor=CHAT_COLOR, edgecolor="none", label="CHAT"),
            Patch(facecolor=AGENT_COLOR, edgecolor="none", label="AGENT"),
        ],
        loc="upper center",
        bbox_to_anchor=(0.5, 0.89),
        ncol=2,
        frameon=False,
        handlelength=1.6,
        columnspacing=2.4,
        fontsize=9.5,
    )
    fig.subplots_adjust(left=0.09, right=0.98, top=0.76, bottom=0.17, wspace=0.34)

    output_path = output_dir / "fig04_quality_autonomy_tradeoff.png"
    save_figure(fig, output_path)
    return (
        chat_score_mean,
        agent_score_mean,
        chat_intermediate_messages,
        agent_intermediate_messages,
    )


def write_caption_01(
    output_dir: Path,
    circuit_count: int,
    chat_mean: float,
    agent_mean: float,
) -> Path:
    difference = chat_mean - agent_mean
    content = f"""# Didascalia — Figura 1

**Figura 1 – Confronto dei punteggi complessivi ottenuti dalle modalità CHAT e
AGENT nei {circuit_count} circuiti analizzati.** Per ciascun circuito sono
riportate le valutazioni assegnate dal judge GPT-5.5 alle due esecuzioni, su
una scala da 0 a 100. Ogni coppia di barre rappresenta quindi un confronto
diretto sullo stesso caso sperimentale: la barra blu identifica CHAT e quella
arancione AGENT. I separatori tratteggiati distinguono i batch A, B e C.
Valori più elevati indicano una migliore
qualità complessiva della diagnosi o della verifica. CHAT ottiene un punteggio
medio di {format_mean(chat_mean)}, mentre AGENT raggiunge
{format_mean(agent_mean)}, con una differenza media di
{format_mean(difference)} punti a favore della modalità interattiva. La
rappresentazione consente inoltre di osservare la variabilità delle
prestazioni tra i singoli circuiti.

*Fonte: elaborazione propria sui risultati sperimentali.*
"""
    path = output_dir / "fig01_caption.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def write_caption_02(
    output_dir: Path,
    rows: list[dict[str, Any]],
    sample_size: int,
) -> Path:
    gaps = {
        row["criterion"]: row["chat_score"] - row["agent_score"]
        for row in rows
    }
    closest = min(gaps, key=lambda criterion: abs(gaps[criterion]))
    largest = max(gaps, key=lambda criterion: gaps[criterion])
    lookup = {row["criterion"]: row for row in rows}

    content = f"""# Didascalia — Figura 2

**Figura 2 – Punteggi medi ottenuti dalle modalità CHAT e AGENT nei cinque
criteri utilizzati dal judge.** Ogni criterio è valutato su una scala da 0 a
4 e contribuisce per il 20% al punteggio complessivo; i valori rappresentano
la media delle {sample_size} valutazioni disponibili per ciascuna modalità.
Il risultato più simile riguarda
{CRITERION_LABELS_IT[closest].lower()} ({format_mean(lookup[closest]["chat_score"])}
per CHAT e {format_mean(lookup[closest]["agent_score"])} per AGENT). Lo scarto
maggiore emerge invece nella
{CRITERION_LABELS_IT[largest].lower()} ({format_mean(gaps[largest])} punti a
favore di CHAT). Il confronto suggerisce che la principale differenza tra le
modalità non risieda nella scelta degli scenari, ma soprattutto
nell'interpretazione tecnica dei risultati e nella formulazione della
conclusione finale.

*Fonte: elaborazione propria sui risultati sperimentali.*
"""
    path = output_dir / "fig02_caption.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def write_caption_03(
    output_dir: Path,
    circuit_count: int,
) -> Path:
    content = f"""# Didascalia — Figura 3

**Figura 3 – Punteggi assegnati dal judge ai cinque criteri per ciascun
circuito e modalità di interazione.** Le due heatmap riportano le
{circuit_count} valutazioni CHAT e le {circuit_count} valutazioni AGENT
utilizzando la stessa scala cromatica da 0 a 4; valori e tonalità più elevate
indicano una valutazione migliore. I numeri nelle celle rendono disponibile
anche il valore esatto, mentre i separatori tratteggiati distinguono i batch
A, B e C. La figura permette di verificare se le differenze medie osservate
derivino da un comportamento diffuso oppure da specifici circuiti e criteri,
evidenziando sia i casi in cui le due modalità risultano equivalenti sia
quelli in cui la modalità autonoma incontra difficoltà localizzate.

*Fonte: elaborazione propria sui risultati sperimentali.*
"""
    path = output_dir / "fig03_caption.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def write_caption_04(
    output_dir: Path,
    circuit_count: int,
    chat_score_mean: float,
    agent_score_mean: float,
    chat_intermediate_messages: float,
    agent_intermediate_messages: float,
) -> Path:
    score_difference = chat_score_mean - agent_score_mean
    content = f"""# Didascalia — Figura 4

**Figura 4 – Compromesso osservato tra qualità del risultato e autonomia
operativa nelle modalità CHAT e AGENT.** Il pannello di sinistra riporta il
punteggio medio assegnato dal judge alle {circuit_count} esecuzioni di ciascuna
modalità. Il pannello di destra mostra il numero medio di messaggi intermedi
inviati dall'utente dopo la richiesta iniziale, che non viene conteggiata.
CHAT ottiene un punteggio medio di {format_mean(chat_score_mean)} e richiede
{format_mean(chat_intermediate_messages)} messaggi intermedi per circuito.
AGENT raggiunge un punteggio medio di {format_mean(agent_score_mean)} e,
per definizione del workflow autonomo, non richiede messaggi intermedi
({format_mean(agent_intermediate_messages)}). Nel benchmark analizzato,
l'autonomia completa è quindi associata a una riduzione media di
{format_mean(score_difference)} punti rispetto a CHAT. Le decisioni interne
dell'AGENT non vengono confrontate con i messaggi CHAT, perché rappresentano
grandezze operative differenti.

*Fonte: elaborazione propria sui risultati sperimentali.*
"""
    path = output_dir / "fig04_caption.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def main() -> int:
    args = parse_args()
    aggregate_dir = args.aggregate_dir.resolve()
    output_dir = args.output_dir.resolve()

    pair_rows = read_pairs(aggregate_dir / "pairs.csv")
    criterion_rows, criterion_sample_size = read_criteria(
        aggregate_dir / "criteria_summary.csv"
    )
    configure_style()
    chat_mean, agent_mean = make_figure_01(pair_rows, output_dir)
    make_figure_02(criterion_rows, output_dir)
    make_figure_03(pair_rows, output_dir)
    (
        tradeoff_chat_mean,
        tradeoff_agent_mean,
        chat_intermediate_messages,
        agent_intermediate_messages,
    ) = make_figure_04(pair_rows, output_dir)
    caption_01 = write_caption_01(
        output_dir,
        len(pair_rows),
        chat_mean,
        agent_mean,
    )
    caption_02 = write_caption_02(
        output_dir,
        criterion_rows,
        criterion_sample_size,
    )
    caption_03 = write_caption_03(output_dir, len(pair_rows))
    caption_04 = write_caption_04(
        output_dir,
        len(pair_rows),
        tradeoff_chat_mean,
        tradeoff_agent_mean,
        chat_intermediate_messages,
        agent_intermediate_messages,
    )

    print(f"Figure salvate in: {output_dir}")
    print("Formato: PNG 320 dpi")
    print(f"Caption Figura 1: {caption_01}")
    print(f"Caption Figura 2: {caption_02}")
    print(f"Caption Figura 3: {caption_03}")
    print(f"Caption Figura 4: {caption_04}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
