#!/usr/bin/env python3
"""Genera le figure del capitolo dei risultati dai CSV ufficiali."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, MaxNLocator


ROOT = Path(__file__).resolve().parent
TABLES_DIR = ROOT / "results" / "tables"
FIGURES_DIR = ROOT / "results" / "figures"

MODE_ORDER = ("chat", "agent", "overall")
MODE_LABELS = {
    "chat": "CHAT",
    "agent": "AGENT",
    "overall": "Complessivo",
}
OUTCOME_ORDER = ("success", "partial_success", "failure")
OUTCOME_LABELS = {
    "success": "Successo",
    "partial_success": "Successo parziale",
    "failure": "Fallimento",
}
OUTCOME_COLORS = {
    "success": "#2E7D32",
    "partial_success": "#F9A825",
    "failure": "#C62828",
}
MODE_COLORS = {
    "chat": "#2F6B9A",
    "agent": "#E67E22",
}
CRITERION_ORDER = (
    "diagnostic_correctness",
    "test_quality",
    "evidence_interpretation",
    "goal_achievement",
    "conclusion_quality",
)
CRITERION_LABELS = {
    "diagnostic_correctness": "Correttezza diagnostica",
    "test_quality": "Qualità dei test",
    "evidence_interpretation": "Interpretazione delle evidenze",
    "goal_achievement": "Raggiungimento dell'obiettivo",
    "conclusion_quality": "Qualità della conclusione",
}


def italian_percent(value: float) -> str:
    return f"{value * 100:.1f}%".replace(".", ",")


def read_outcomes() -> dict[str, dict[str, dict[str, float | int]]]:
    path = TABLES_DIR / "table_05_outcome_summary.csv"
    data: dict[str, dict[str, dict[str, float | int]]] = {
        mode: {} for mode in MODE_ORDER
    }
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            mode = row["mode"]
            outcome = row["outcome"]
            if mode in data:
                data[mode][outcome] = {
                    "count": int(row["count"]),
                    "rate": float(row["rate"]),
                }

    expected_totals = {"chat": 21, "agent": 21, "overall": 42}
    for mode in MODE_ORDER:
        missing = set(OUTCOME_ORDER) - set(data[mode])
        if missing:
            raise ValueError(f"Esiti mancanti per {mode}: {sorted(missing)}")
        total = sum(int(data[mode][outcome]["count"]) for outcome in data[mode])
        if total != expected_totals[mode]:
            raise ValueError(
                f"Totale non valido per {mode}: {total}, atteso {expected_totals[mode]}"
            )
        omitted = {"inconclusive", "technical_failure"}
        if any(int(data[mode].get(outcome, {}).get("count", 0)) for outcome in omitted):
            raise ValueError(
                "Il grafico deve essere esteso: sono presenti esiti inconcludenti "
                "o fallimenti tecnici non nulli."
            )

    for outcome in OUTCOME_ORDER:
        combined = int(data["chat"][outcome]["count"]) + int(
            data["agent"][outcome]["count"]
        )
        if combined != int(data["overall"][outcome]["count"]):
            raise ValueError(f"Aggregato complessivo incoerente per {outcome}")
    return data


def read_criteria() -> dict[str, dict[str, float]]:
    path = TABLES_DIR / "table_04_criteria_summary.csv"
    data: dict[str, dict[str, float]] = {"chat": {}, "agent": {}}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            mode = row["mode"]
            criterion = row["criterion"]
            if mode in data and criterion in CRITERION_ORDER:
                maximum = float(row["maximum_score"])
                score = float(row["mean_score"])
                if maximum != 2:
                    raise ValueError(
                        f"Massimo inatteso per {mode}/{criterion}: {maximum}"
                    )
                if not 0 <= score <= maximum:
                    raise ValueError(
                        f"Media fuori scala per {mode}/{criterion}: {score}"
                    )
                data[mode][criterion] = score

    for mode in ("chat", "agent"):
        missing = set(CRITERION_ORDER) - set(data[mode])
        if missing:
            raise ValueError(f"Criteri mancanti per {mode}: {sorted(missing)}")
    return data


def read_paired_scores() -> list[dict[str, int | str]]:
    path = TABLES_DIR / "table_02_paired_results.csv"
    rows: list[dict[str, int | str]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            chat_score = int(row["chat_score"])
            agent_score = int(row["agent_score"])
            if not 0 <= chat_score <= 10 or not 0 <= agent_score <= 10:
                raise ValueError(
                    f"Punteggio fuori scala per {row['circuit_id']}: "
                    f"CHAT={chat_score}, AGENT={agent_score}"
                )
            rows.append(
                {
                    "circuit_id": row["circuit_id"],
                    "chat_score": chat_score,
                    "agent_score": agent_score,
                }
            )

    if len(rows) != 21:
        raise ValueError(f"Attesi 21 circuiti, trovati {len(rows)}")
    circuit_ids = [str(row["circuit_id"]) for row in rows]
    if len(set(circuit_ids)) != len(circuit_ids):
        raise ValueError("Sono presenti identificativi di circuito duplicati")
    return rows


def build_outcome_distribution() -> tuple[Path, Path]:
    data = read_outcomes()
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 11,
            "axes.titlesize": 18,
            "axes.labelsize": 12,
            "xtick.labelsize": 10,
            "ytick.labelsize": 12,
        }
    )

    fig, ax = plt.subplots(figsize=(12.4, 6.6), facecolor="white")
    fig.subplots_adjust(left=0.16, right=0.82, top=0.75, bottom=0.20)

    y_positions = {"chat": 2.4, "agent": 1.2, "overall": 0.0}
    totals = {"chat": 21, "agent": 21, "overall": 42}

    for mode in MODE_ORDER:
        y = y_positions[mode]
        left = 0.0
        for outcome in OUTCOME_ORDER:
            count = int(data[mode][outcome]["count"])
            rate = float(data[mode][outcome]["rate"])
            width = rate * 100
            if width > 0:
                ax.barh(
                    y,
                    width,
                    left=left,
                    height=0.58,
                    color=OUTCOME_COLORS[outcome],
                    edgecolor="white",
                    linewidth=1.5,
                    zorder=3,
                )
                if width >= 12:
                    text_color = "white" if outcome == "success" else "#242424"
                    ax.text(
                        left + width / 2,
                        y,
                        f"{count}\n({italian_percent(rate)})",
                        ha="center",
                        va="center",
                        color=text_color,
                        fontsize=11,
                        fontweight="bold",
                        linespacing=1.15,
                        zorder=4,
                    )
                else:
                    ax.annotate(
                        f"Fallimento: {count} ({italian_percent(rate)})",
                        xy=(left + width / 2, y + 0.02),
                        xytext=(95.0, y + 0.43),
                        ha="right",
                        va="bottom",
                        fontsize=9.5,
                        fontweight="bold",
                        color=OUTCOME_COLORS["failure"],
                        arrowprops={
                            "arrowstyle": "-",
                            "color": OUTCOME_COLORS["failure"],
                            "linewidth": 1.1,
                        },
                        zorder=5,
                    )
            left += width

        useful_count = sum(
            int(data[mode][outcome]["count"])
            for outcome in ("success", "partial_success")
        )
        useful_rate = useful_count / totals[mode]
        ax.text(
            111.5,
            y,
            f"{useful_count}/{totals[mode]}\n({italian_percent(useful_rate)})",
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold",
            color="#263238",
            linespacing=1.2,
        )

    ax.text(
        111.5,
        3.03,
        "Risultati\nutili",
        ha="center",
        va="bottom",
        fontsize=10.5,
        fontweight="bold",
        color="#263238",
    )
    ax.axvline(100, color="#B0BEC5", linewidth=1.0, zorder=2)
    ax.axvline(104, color="#CFD8DC", linewidth=0.9, zorder=2)

    ax.set_xlim(0, 120)
    ax.set_ylim(-0.65, 3.25)
    ax.set_yticks([y_positions[mode] for mode in MODE_ORDER])
    ax.set_yticklabels(
        [
            f"{MODE_LABELS[mode]}\n(n = {totals[mode]})"
            for mode in MODE_ORDER
        ]
    )
    ax.set_xticks(range(0, 101, 20))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{int(value)}%"))
    ax.set_xlabel("Percentuale delle esecuzioni")
    ax.grid(axis="x", color="#E4E8EB", linewidth=0.9, zorder=1)
    ax.tick_params(axis="y", length=0, pad=10)
    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.suptitle(
        "Distribuzione degli esiti per modalità",
        x=0.49,
        y=0.965,
        fontsize=20,
        fontweight="bold",
        color="#1F2933",
    )
    legend_handles = [
        Patch(facecolor=OUTCOME_COLORS[outcome], label=OUTCOME_LABELS[outcome])
        for outcome in OUTCOME_ORDER
    ]
    fig.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.49, 0.885),
        ncol=3,
        frameon=False,
        fontsize=11,
        handlelength=1.5,
        columnspacing=2.5,
    )
    fig.text(
        0.16,
        0.075,
        "Risultato utile = successo + successo parziale. "
        "Le percentuali sono calcolate sulle esecuzioni della singola riga.",
        ha="left",
        va="center",
        fontsize=9.5,
        color="#52606D",
    )

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    png_path = FIGURES_DIR / "fig03_distribuzione_esiti.png"
    pdf_path = FIGURES_DIR / "fig03_distribuzione_esiti.pdf"
    metadata = {
        "Title": "Distribuzione degli esiti per modalità",
        "Subject": "Valutazione CHAT e AGENT su 21 circuiti",
        "Creator": "build_result_figures.py",
    }
    fig.savefig(png_path, dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(pdf_path, bbox_inches="tight", facecolor="white", metadata=metadata)
    plt.close(fig)
    return png_path, pdf_path


def build_criteria_means() -> tuple[Path, Path]:
    data = read_criteria()
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 11,
            "axes.titlesize": 18,
            "axes.labelsize": 12,
            "xtick.labelsize": 10,
            "ytick.labelsize": 11.5,
        }
    )

    fig, ax = plt.subplots(figsize=(12.4, 6.8), facecolor="white")
    fig.subplots_adjust(left=0.31, right=0.91, top=0.78, bottom=0.15)

    y_positions = list(range(len(CRITERION_ORDER)))
    bar_height = 0.30
    offset = 0.18
    for mode, y_offset in (("chat", -offset), ("agent", offset)):
        scores = [data[mode][criterion] for criterion in CRITERION_ORDER]
        bars = ax.barh(
            [position + y_offset for position in y_positions],
            scores,
            height=bar_height,
            color=MODE_COLORS[mode],
            edgecolor="white",
            linewidth=1.0,
            label=MODE_LABELS[mode],
            zorder=3,
        )
        for bar, score in zip(bars, scores, strict=True):
            ax.text(
                score + 0.035,
                bar.get_y() + bar.get_height() / 2,
                f"{score:.2f}".replace(".", ","),
                ha="left",
                va="center",
                fontsize=10.5,
                fontweight="bold",
                color=MODE_COLORS[mode],
                zorder=4,
            )

    ax.set_xlim(0, 2.08)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(
        [CRITERION_LABELS[criterion] for criterion in CRITERION_ORDER]
    )
    ax.invert_yaxis()
    ax.set_xticks([0, 0.5, 1.0, 1.5, 2.0])

    def score_tick(value: float, _: int) -> str:
        if value.is_integer():
            return str(int(value))
        return f"{value:.1f}".replace(".", ",")

    ax.xaxis.set_major_formatter(FuncFormatter(score_tick))
    ax.set_xlabel("Punteggio medio (scala 0–2)", labelpad=12)
    ax.grid(axis="x", color="#E4E8EB", linewidth=0.9, zorder=1)
    ax.axvline(2, color="#B0BEC5", linewidth=1.0, zorder=2)
    ax.tick_params(axis="y", length=0, pad=12)
    ax.tick_params(axis="x", colors="#455A64")
    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.suptitle(
        "Punteggio medio per criterio",
        x=0.54,
        y=0.955,
        fontsize=20,
        fontweight="bold",
        color="#1F2933",
    )
    legend_handles = [
        Patch(facecolor=MODE_COLORS[mode], label=MODE_LABELS[mode])
        for mode in ("chat", "agent")
    ]
    fig.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.54, 0.885),
        ncol=2,
        frameon=False,
        fontsize=11.5,
        handlelength=1.6,
        columnspacing=3.0,
    )

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    png_path = FIGURES_DIR / "fig04_punteggi_medi_criteri.png"
    pdf_path = FIGURES_DIR / "fig04_punteggi_medi_criteri.pdf"
    metadata = {
        "Title": "Punteggio medio per criterio",
        "Subject": "Confronto descrittivo CHAT e AGENT sui cinque criteri",
        "Creator": "build_result_figures.py",
    }
    fig.savefig(png_path, dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(pdf_path, bbox_inches="tight", facecolor="white", metadata=metadata)
    plt.close(fig)
    return png_path, pdf_path


def build_score_distribution() -> tuple[Path, Path]:
    rows = read_paired_scores()
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 11,
            "axes.titlesize": 18,
            "axes.labelsize": 12,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
        }
    )

    fig, ax = plt.subplots(figsize=(12.4, 6.8), facecolor="white")
    fig.subplots_adjust(left=0.11, right=0.94, top=0.78, bottom=0.15)

    score_values = list(range(11))
    bar_width = 0.36
    offset = 0.20
    distributions = {
        "chat": Counter(int(row["chat_score"]) for row in rows),
        "agent": Counter(int(row["agent_score"]) for row in rows),
    }

    for mode, x_offset in (("chat", -offset), ("agent", offset)):
        counts = [distributions[mode][score] for score in score_values]
        bars = ax.bar(
            [score + x_offset for score in score_values],
            counts,
            width=bar_width,
            color=MODE_COLORS[mode],
            edgecolor="white",
            linewidth=1.0,
            label=MODE_LABELS[mode],
            zorder=3,
        )
        for bar, count in zip(bars, counts, strict=True):
            if count == 0:
                continue
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                count + 0.13,
                str(count),
                ha="center",
                va="bottom",
                fontsize=10.5,
                fontweight="bold",
                color=MODE_COLORS[mode],
                zorder=4,
            )

    maximum_count = max(max(distribution.values()) for distribution in distributions.values())
    ax.set_xlim(-0.65, 10.65)
    ax.set_ylim(0, maximum_count + 1.15)
    ax.set_xticks(score_values)
    ax.set_xlabel("Punteggio totale (scala 0–10)", labelpad=12)
    ax.set_ylabel("Numero di circuiti", labelpad=12)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(axis="y", color="#E4E8EB", linewidth=0.9, zorder=1)
    ax.tick_params(axis="x", colors="#455A64")
    ax.tick_params(axis="y", colors="#455A64")
    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.suptitle(
        "Distribuzione dei punteggi totali",
        x=0.525,
        y=0.955,
        fontsize=20,
        fontweight="bold",
        color="#1F2933",
    )
    legend_handles = [
        Patch(
            facecolor=MODE_COLORS[mode],
            label=f"{MODE_LABELS[mode]} (n = {len(rows)})",
        )
        for mode in ("chat", "agent")
    ]
    fig.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.525, 0.885),
        ncol=2,
        frameon=False,
        fontsize=11.5,
        handlelength=1.6,
        columnspacing=3.0,
    )

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    png_path = FIGURES_DIR / "fig05_distribuzione_punteggi_totali.png"
    pdf_path = FIGURES_DIR / "fig05_distribuzione_punteggi_totali.pdf"
    metadata = {
        "Title": "Distribuzione dei punteggi totali",
        "Subject": "Distribuzione CHAT e AGENT sui punteggi da 0 a 10",
        "Creator": "build_result_figures.py",
    }
    fig.savefig(png_path, dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(pdf_path, bbox_inches="tight", facecolor="white", metadata=metadata)
    plt.close(fig)
    return png_path, pdf_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--figure",
        choices=("outcomes", "criteria", "scores", "all"),
        default="outcomes",
        help="Figura da generare (default: outcomes).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.figure in {"outcomes", "all"}:
        png_path, pdf_path = build_outcome_distribution()
        print(f"Generato PNG: {png_path}")
        print(f"Generato PDF: {pdf_path}")
    if args.figure in {"criteria", "all"}:
        png_path, pdf_path = build_criteria_means()
        print(f"Generato PNG: {png_path}")
        print(f"Generato PDF: {pdf_path}")
    if args.figure in {"scores", "all"}:
        png_path, pdf_path = build_score_distribution()
        print(f"Generato PNG: {png_path}")
        print(f"Generato PDF: {pdf_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
