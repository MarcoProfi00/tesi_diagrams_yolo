#!/usr/bin/env python3
"""Genera le figure di sintesi per la verifica immagine-Graph JSON.

Le figure sono ricavate esclusivamente dai CSV finali dei quattro batch.
Il Batch A usa l'output curato documentato nel relativo README.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D


PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = (
    PROJECT_ROOT
    / "notes"
    / "second_part_pipeline_topologica"
    / "figures"
    / "verify_json_img"
)

BATCH_FILES = {
    "A": PROJECT_ROOT
    / "experiment_ai"
    / "verify_json_img"
    / "batchA"
    / "output_gpt5_4_final_curated"
    / "judge_results.csv",
    "B": PROJECT_ROOT
    / "experiment_ai"
    / "verify_json_img"
    / "batchB"
    / "output_gpt5_4"
    / "judge_results.csv",
    "C1": PROJECT_ROOT
    / "experiment_ai"
    / "verify_json_img"
    / "batchC1"
    / "output_gpt5_4"
    / "judge_results.csv",
    "C2": PROJECT_ROOT
    / "experiment_ai"
    / "verify_json_img"
    / "batchC2"
    / "output_gpt5_4"
    / "judge_results.csv",
}

DECISION_COLORS = {
    "VERY_HIGH": "#0072B2",
    "HIGH": "#E69F00",
    "MEDIUM": "#D55E00",
    "LOW": "#6A3D9A",
}

ANNOTATED_CASES = {"a03", "a09", "b06", "c08", "c09"}


def load_final_results() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for batch, csv_path in BATCH_FILES.items():
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV finale non trovato: {csv_path}")

        frame = pd.read_csv(csv_path)
        frame["batch_group"] = batch
        frame["score"] = pd.to_numeric(frame["score"], errors="raise")
        frames.append(frame)

    results = pd.concat(frames, ignore_index=True)
    if len(results) != 38:
        raise ValueError(f"Attesi 38 risultati finali, trovati {len(results)}")
    return results


def make_score_distribution(results: pd.DataFrame) -> None:
    batch_order = list(BATCH_FILES)
    values = [
        results.loc[results["batch_group"] == batch, "score"].to_numpy()
        for batch in batch_order
    ]

    fig, ax = plt.subplots(figsize=(10.8, 6.6))

    # Fasce qualitative molto leggere: il significato non dipende solo dal colore,
    # perché soglie e nomi sono riportati anche testualmente.
    ax.axhspan(0, 55, color="#6A3D9A", alpha=0.035, zorder=0)
    ax.axhspan(55, 75, color="#D55E00", alpha=0.055, zorder=0)
    ax.axhspan(75, 90, color="#E69F00", alpha=0.055, zorder=0)
    ax.axhspan(90, 100, color="#0072B2", alpha=0.045, zorder=0)

    boxplot = ax.boxplot(
        values,
        tick_labels=batch_order,
        widths=0.52,
        patch_artist=True,
        showfliers=False,
        medianprops={"color": "#111111", "linewidth": 2.0},
        whiskerprops={"color": "#555555", "linewidth": 1.3},
        capprops={"color": "#555555", "linewidth": 1.3},
        boxprops={"edgecolor": "#555555", "linewidth": 1.3},
    )
    for box in boxplot["boxes"]:
        box.set_facecolor("#D9E2EC")
        box.set_alpha(0.72)

    for batch_index, batch in enumerate(batch_order, start=1):
        subset = (
            results.loc[results["batch_group"] == batch]
            .sort_values(["score", "circuit_id"])
            .reset_index(drop=True)
        )
        count = len(subset)
        if count == 1:
            offsets = [0.0]
        else:
            offsets = [(-0.17 + i * 0.34 / (count - 1)) for i in range(count)]

        for offset, row in zip(offsets, subset.itertuples(index=False)):
            x = batch_index + offset
            color = DECISION_COLORS.get(row.decision, "#555555")
            ax.scatter(
                x,
                row.score,
                s=54,
                color=color,
                edgecolor="white",
                linewidth=0.8,
                zorder=3,
            )
            if row.circuit_id in ANNOTATED_CASES:
                ax.annotate(
                    f"{batch}/{row.circuit_id} ({int(row.score)})",
                    xy=(x, row.score),
                    xytext=(5, -12 if row.circuit_id == "c09" else 7),
                    textcoords="offset points",
                    fontsize=8.6,
                    fontweight="semibold",
                    color="#222222",
                )

    for threshold in (55, 75, 90):
        ax.axhline(
            threshold,
            color="#666666",
            linewidth=0.9,
            linestyle=(0, (4, 4)),
            alpha=0.75,
            zorder=1,
        )

    ax.text(4.44, 95, "VERY HIGH", va="center", fontsize=8.5, color="#444444")
    ax.text(4.44, 82.5, "HIGH", va="center", fontsize=8.5, color="#444444")
    ax.text(4.44, 65, "MEDIUM", va="center", fontsize=8.5, color="#444444")

    legend_handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="none",
            markerfacecolor=color,
            markeredgecolor="white",
            markersize=7.5,
            label=label.replace("_", " "),
        )
        for label, color in DECISION_COLORS.items()
        if label != "LOW"
    ]
    ax.legend(
        handles=legend_handles,
        title="Decisione del judge",
        loc="lower left",
        ncol=3,
        frameon=True,
        fontsize=8.5,
        title_fontsize=9,
    )

    ax.set_title("Distribuzione degli score di fedeltà per batch", pad=13, fontsize=15)
    ax.set_xlabel("Batch", fontsize=11)
    ax.set_ylabel("Score di fedeltà immagine–Graph JSON", fontsize=11)
    ax.set_ylim(50, 101)
    ax.set_xlim(0.55, 4.72)
    ax.set_yticks(range(50, 101, 5))
    ax.grid(axis="y", color="#B8B8B8", linewidth=0.6, alpha=0.45)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stem = OUTPUT_DIR / "fig01_distribuzione_score_per_batch"
    fig.savefig(stem.with_suffix(".png"), dpi=300, bbox_inches="tight")
    fig.savefig(stem.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)


def make_decision_distribution(results: pd.DataFrame) -> None:
    batch_order = list(BATCH_FILES)
    decision_order = ["VERY_HIGH", "HIGH", "MEDIUM", "LOW"]
    display_groups = [*batch_order, "Totale"]

    counts_by_group: dict[str, dict[str, int]] = {}
    sizes: dict[str, int] = {}
    for group in display_groups:
        subset = results if group == "Totale" else results.loc[results["batch_group"] == group]
        sizes[group] = len(subset)
        counts_by_group[group] = {
            decision: int((subset["decision"] == decision).sum())
            for decision in decision_order
        }

    fig, ax = plt.subplots(figsize=(10.2, 6.2))
    x_positions = list(range(len(display_groups)))
    bottoms = [0.0] * len(display_groups)

    for decision in decision_order:
        percentages = [
            counts_by_group[group][decision] / sizes[group] * 100
            for group in display_groups
        ]
        bars = ax.bar(
            x_positions,
            percentages,
            bottom=bottoms,
            width=0.66,
            color=DECISION_COLORS[decision],
            edgecolor="white",
            linewidth=1.1,
            label=decision.replace("_", " "),
        )

        for index, (bar, group, percentage) in enumerate(
            zip(bars, display_groups, percentages)
        ):
            count = counts_by_group[group][decision]
            if count == 0:
                continue
            label = f"{count}\n({percentage:.1f}%)".replace(".", ",")
            text_color = "#111111" if decision == "HIGH" else "white"
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bottoms[index] + percentage / 2,
                label,
                ha="center",
                va="center",
                fontsize=9.2,
                fontweight="semibold",
                color=text_color,
            )

        bottoms = [bottom + value for bottom, value in zip(bottoms, percentages)]

    for x, group in zip(x_positions, display_groups):
        ax.text(
            x,
            101.5,
            f"N = {sizes[group]}",
            ha="center",
            va="bottom",
            fontsize=9,
            color="#444444",
        )

    ax.set_title("Distribuzione delle decisioni qualitative per batch", pad=16, fontsize=15)
    ax.set_xlabel("Batch", fontsize=11)
    ax.set_ylabel("Percentuale di circuiti", fontsize=11)
    ax.set_xticks(x_positions, display_groups)
    ax.set_ylim(0, 106)
    ax.set_yticks(range(0, 101, 10), [f"{value}%" for value in range(0, 101, 10)])
    ax.grid(axis="y", color="#B8B8B8", linewidth=0.6, alpha=0.45)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(
        title="Decisione del judge",
        loc="lower center",
        bbox_to_anchor=(0.5, -0.22),
        ncol=4,
        frameon=False,
        fontsize=9,
        title_fontsize=9.5,
    )
    fig.tight_layout()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stem = OUTPUT_DIR / "fig02_distribuzione_decisioni_per_batch"
    fig.savefig(stem.with_suffix(".png"), dpi=300, bbox_inches="tight")
    fig.savefig(stem.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    results = load_final_results()
    make_score_distribution(results)
    make_decision_distribution(results)
    print(f"Figure salvate in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
