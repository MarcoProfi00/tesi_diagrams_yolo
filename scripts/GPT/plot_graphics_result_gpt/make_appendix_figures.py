#!/usr/bin/env python3
"""
make_appendix_figures.py

Script per generare i grafici secondari / da appendice della tesi a partire
dai CSV aggregati del judge.

Figure incluse:
    A1 - Score vs latenza
    A2 - Heatmap modello × criterio
    A3 - Stabilita score per modello

Input attesi nella cartella aggregata:
    - aggregate_by_model.csv
    - criteria_long.csv
    - all_runs.csv

Output default:
    <input-dir>/figures_appendix/

Per ogni figura vengono salvati:
    - PNG
    - una caption in figure_captions_appendix.md
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import pandas as pd
from matplotlib.lines import Line2D


# -----------------------------------------------------------------------------
# Configurazione generale
# -----------------------------------------------------------------------------

MAX_SCORE = 21

PREFERRED_MODEL_ORDER = [
    "gpt-5.4",
    "gpt-5.4-mini",
    "gpt-5-mini",
    "gpt-4.1-mini",
    "gpt-5.4-nano",
    "gpt-5-nano",
    "gpt-4.1-nano",
    "gpt-4o-mini",
]

CRITERION_ORDER = [
    "circuit_understanding",
    "datasheet_use",
    "json_image_use",
    "diagnostic_accuracy",
    "cause_priority",
    "practical_checks",
    "hallucination_absence",
]

CRITERION_LABELS = {
    "circuit_understanding": "Comprensione\ncircuito",
    "datasheet_use": "Uso\ndatasheet",
    "json_image_use": "Uso\nJSON/img",
    "diagnostic_accuracy": "Accuratezza\ndiagnosi",
    "cause_priority": "Priorità\ncause",
    "practical_checks": "Controlli\npratici",
    "hallucination_absence": "Assenza\nallucinazioni",
}

FAMILY_COLORS = {
    "gpt-5.4": "#1f77b4",
    "gpt-5": "#2ca02c",
    "gpt-4.1": "#ff7f0e",
    "gpt-4o": "#9467bd",
    "Altro": "#4c4c4c",
}

FAMILY_ORDER = ["gpt-5.4", "gpt-5", "gpt-4.1", "gpt-4o", "Altro"]


FIGURE_CAPTIONS = {
    "appendix_a1_score_vs_latenza": (
        "Figura A1 — Compromesso qualità-latenza per modello. "
        "Il grafico mette in relazione lo score medio ottenuto da ciascun modello con la latenza media "
        "di esecuzione. Ogni punto rappresenta un modello ed è colorato in base alla famiglia di appartenenza. "
        "I modelli collocati nella parte alta a sinistra offrono il miglior compromesso tra qualità diagnostica "
        "e tempo di risposta. Il grafico integra l’analisi qualità-costo, mostrando la praticabilità dei modelli "
        "in scenari in cui la rapidità della diagnosi è rilevante."
    ),
    "appendix_a2_heatmap_modello_criterio": (
        "Figura A2 — Prestazioni medie dei modelli sui criteri del judge. "
        "La heatmap riporta, per ciascun modello e per ciascun criterio di valutazione, lo score medio ottenuto "
        "nelle run analizzate. Le righe sono ordinate in base allo score medio complessivo dei modelli. Il grafico "
        "permette di osservare quali aspetti contribuiscono maggiormente alle prestazioni finali, distinguendo ad "
        "esempio tra comprensione del circuito, uso del datasheet, accuratezza diagnostica, priorità delle cause, "
        "controlli pratici e assenza di allucinazioni."
    ),
}


# -----------------------------------------------------------------------------
# Utility
# -----------------------------------------------------------------------------

def ensure_columns(df: pd.DataFrame, required_columns: Iterable[str], filename: str) -> None:
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(
            f"Nel file {filename} mancano queste colonne: {missing}\n"
            f"Colonne trovate: {list(df.columns)}"
        )


def read_csv(input_dir: Path, filename: str, required_columns: Iterable[str]) -> pd.DataFrame:
    path = input_dir / filename
    if not path.exists():
        raise FileNotFoundError(f"File non trovato: {path}")

    df = pd.read_csv(path)
    ensure_columns(df, required_columns, filename)
    return df


def save_figure(fig: plt.Figure, output_dir: Path, basename: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    png_path = output_dir / f"{basename}.png"
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] Salvato: {png_path}")


def write_captions(output_dir: Path, generated_basenames: list[str]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    md_path = output_dir / "figure_captions_appendix.md"

    lines_md = ["# Caption figure appendice\n"]

    for basename in generated_basenames:
        caption = FIGURE_CAPTIONS.get(basename)
        if not caption:
            continue
        lines_md.append(f"## {basename}\n")
        lines_md.append(caption + "\n")

    md_path.write_text("\n".join(lines_md), encoding="utf-8")
    print(f"[OK] Salvato: {md_path}")


def clean_axes(ax: plt.Axes) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)


def get_family(model: str) -> str:
    if model.startswith("gpt-5.4"):
        return "gpt-5.4"
    if model.startswith("gpt-5"):
        return "gpt-5"
    if model.startswith("gpt-4.1"):
        return "gpt-4.1"
    if model.startswith("gpt-4o"):
        return "gpt-4o"
    return "Altro"


def get_model_order(input_dir: Path) -> list[str]:
    """
    Ordine principale dei modelli: dal migliore al peggiore secondo lo score medio.
    """
    try:
        df = read_csv(
            input_dir,
            "aggregate_by_model.csv",
            required_columns=["model", "total_score_mean"],
        )
        df = df[["model", "total_score_mean"]].copy()
        df["total_score_mean"] = pd.to_numeric(df["total_score_mean"], errors="coerce")
        df = df.dropna(subset=["total_score_mean"])
        order = df.sort_values("total_score_mean", ascending=False)["model"].tolist()
        return order if order else PREFERRED_MODEL_ORDER
    except Exception:
        return PREFERRED_MODEL_ORDER


def dedupe_all_runs(df: pd.DataFrame) -> pd.DataFrame:
    """
    Evita che eventuali righe duplicate in all_runs.csv pesino due volte nei boxplot.
    """
    key_cols = [c for c in ["circuit", "model", "input_type"] if c in df.columns]
    if key_cols:
        return df.drop_duplicates(subset=key_cols, keep="first")
    return df.drop_duplicates()


# -----------------------------------------------------------------------------
# A1 - Score vs latenza
# -----------------------------------------------------------------------------

def appendix_a1_score_vs_latenza(input_dir: Path, output_dir: Path) -> str:
    """
    Scatter plot score medio vs latenza media.
    """
    basename = "appendix_a1_score_vs_latenza"

    df = read_csv(
        input_dir,
        "aggregate_by_model.csv",
        required_columns=["model", "model_latency_seconds_mean", "total_score_mean"],
    )

    plot_df = df[["model", "model_latency_seconds_mean", "total_score_mean"]].copy()
    plot_df["model_latency_seconds_mean"] = pd.to_numeric(
        plot_df["model_latency_seconds_mean"],
        errors="coerce",
    )
    plot_df["total_score_mean"] = pd.to_numeric(plot_df["total_score_mean"], errors="coerce")
    plot_df = plot_df.dropna(subset=["model_latency_seconds_mean", "total_score_mean"])
    plot_df = plot_df[plot_df["model_latency_seconds_mean"] >= 0].copy()
    plot_df["family"] = plot_df["model"].map(get_family)

    fig, ax = plt.subplots(figsize=(11.5, 6.4))

    for family in FAMILY_ORDER:
        family_df = plot_df[plot_df["family"] == family]
        if family_df.empty:
            continue

        ax.scatter(
            family_df["model_latency_seconds_mean"],
            family_df["total_score_mean"],
            s=105,
            color=FAMILY_COLORS.get(family, "#4c4c4c"),
            edgecolors="white",
            linewidths=1.1,
            alpha=0.95,
            label=family,
            zorder=3,
        )

    ax.set_title("Compromesso qualità-latenza per modello", fontsize=14, pad=16)
    ax.set_xlabel("Latenza media per diagnosi (secondi)")
    ax.set_ylabel("Score medio (0–21)")
    ax.set_ylim(0, MAX_SCORE + 0.7)
    ax.set_yticks([0, 3, 6, 9, 12, 15, 18, 21])

    x_min = float(plot_df["model_latency_seconds_mean"].min()) if len(plot_df) else 0
    x_max = float(plot_df["model_latency_seconds_mean"].max()) if len(plot_df) else 1
    margin = max(1.0, (x_max - x_min) * 0.15)
    ax.set_xlim(max(0, x_min - margin), x_max + margin)

    label_offsets = {
        "gpt-5.4": (-58, 10),
        "gpt-5.4-mini": (10, 12),
        "gpt-5.4-nano": (10, 10),
        "gpt-5-mini": (10, -20),
        "gpt-5-nano": (10, 10),
        "gpt-4.1-mini": (10, 12),
        "gpt-4.1-nano": (10, -20),
        "gpt-4o-mini": (10, 10),
    }

    for _, row in plot_df.iterrows():
        model = row["model"]
        x = row["model_latency_seconds_mean"]
        y = row["total_score_mean"]
        dx, dy = label_offsets.get(model, (10, 10))
        ha = "right" if dx < 0 else "left"
        va = "top" if dy < 0 else "bottom"

        ax.annotate(
            model,
            (x, y),
            textcoords="offset points",
            xytext=(dx, dy),
            ha=ha,
            va=va,
            fontsize=8.5,
            bbox={
                "boxstyle": "round,pad=0.20",
                "facecolor": "white",
                "edgecolor": "#dddddd",
                "linewidth": 0.4,
                "alpha": 0.92,
            },
            arrowprops={
                "arrowstyle": "-",
                "color": "#777777",
                "linewidth": 0.5,
                "alpha": 0.55,
            },
            zorder=4,
        )

    ax.legend(
        title="Famiglia modello",
        frameon=False,
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
    )

    clean_axes(ax)
    fig.tight_layout()
    save_figure(fig, output_dir, basename)

    return basename


# -----------------------------------------------------------------------------
# A2 - Heatmap modello × criterio
# -----------------------------------------------------------------------------

def appendix_a2_heatmap_modello_criterio(input_dir: Path, output_dir: Path) -> str:
    """
    Heatmap dello score medio per modello e criterio del judge.
    """
    basename = "appendix_a2_heatmap_modello_criterio"

    df = read_csv(
        input_dir,
        "criteria_long.csv",
        required_columns=["model", "criterion", "score"],
    )

    plot_df = df[["model", "criterion", "score"]].copy()
    plot_df["score"] = pd.to_numeric(plot_df["score"], errors="coerce")
    plot_df = plot_df.dropna(subset=["score"])

    model_order = [m for m in get_model_order(input_dir) if m in set(plot_df["model"])]
    criteria_order = [c for c in CRITERION_ORDER if c in set(plot_df["criterion"])]

    pivot = (
        plot_df
        .pivot_table(
            index="model",
            columns="criterion",
            values="score",
            aggfunc="mean",
        )
        .reindex(index=model_order, columns=criteria_order)
    )

    fig, ax = plt.subplots(figsize=(11.2, 6.5))

    im = ax.imshow(pivot.values, vmin=0, vmax=3, aspect="auto")

    ax.set_title("Prestazioni medie per criterio del judge", fontsize=14, pad=14)
    ax.set_xlabel("Criterio")
    ax.set_ylabel("Modello")

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels([CRITERION_LABELS.get(c, c) for c in pivot.columns])
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)

    for i, model in enumerate(pivot.index):
        for j, criterion in enumerate(pivot.columns):
            value = pivot.loc[model, criterion]
            label = "" if pd.isna(value) else f"{value:.2f}"
            ax.text(j, i, label, ha="center", va="center", fontsize=8)

    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Score medio criterio (0–3)")

    fig.tight_layout()
    save_figure(fig, output_dir, basename)

    return basename




# -----------------------------------------------------------------------------
# A3 - Stabilita score per modello
# -----------------------------------------------------------------------------

FIGURE_CAPTIONS.update(
    {
        "appendix_a1_score_vs_latenza": (
            "Figura A1 - Compromesso qualita-latenza per modello. "
            "Il grafico mette in relazione lo score medio ottenuto da ciascun modello con la latenza media "
            "di esecuzione. Ogni punto rappresenta un modello ed e colorato in base alla famiglia di appartenenza. "
            "I modelli collocati nella parte alta a sinistra offrono il miglior compromesso tra qualita diagnostica "
            "e tempo di risposta. Il grafico integra l'analisi qualita-costo, mostrando la praticabilita dei modelli "
            "in scenari in cui la rapidita della diagnosi e rilevante."
        ),
        "appendix_a2_heatmap_modello_criterio": (
            "Figura A2 - Prestazioni medie dei modelli sui criteri del judge. "
            "La heatmap riporta, per ciascun modello e per ciascun criterio di valutazione, lo score medio ottenuto "
            "nelle run analizzate. Le righe sono ordinate in base allo score medio complessivo dei modelli. Il grafico "
            "permette di osservare quali aspetti contribuiscono maggiormente alle prestazioni finali, distinguendo ad "
            "esempio tra comprensione del circuito, uso del datasheet, accuratezza diagnostica, priorita delle cause, "
            "controlli pratici e assenza di allucinazioni."
        ),
        "appendix_a3_stabilita_score_modello": (
            "Figura A3 - Mappa qualita-stabilita dei modelli. "
            "Il grafico mette in relazione lo score medio con la deviazione standard dello score. I modelli piu "
            "interessanti si trovano in alto a sinistra: ottengono un punteggio medio elevato e mostrano una minore "
            "variabilita tra le run. La figura integra la classifica per score medio distinguendo i modelli forti ma "
            "stabili da quelli piu irregolari."
        ),
    }
)


def write_captions(output_dir: Path, generated_basenames: list[str]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    md_path = output_dir / "figure_captions_appendix.md"

    lines_md = ["# Caption figure appendice\n"]

    for basename, caption in FIGURE_CAPTIONS.items():
        lines_md.append(f"## {basename}\n")
        lines_md.append(caption + "\n")

    md_path.write_text("\n".join(lines_md), encoding="utf-8")
    print(f"[OK] Salvato: {md_path}")


def appendix_a3_stabilita_score_modello(input_dir: Path, output_dir: Path) -> str:
    """
    Mappa qualita-stabilita: score medio vs deviazione standard.
    """
    basename = "appendix_a3_stabilita_score_modello"

    df = read_csv(
        input_dir,
        "aggregate_by_model.csv",
        required_columns=["model", "total_score_mean", "total_score_median", "total_score_std"],
    )

    plot_df = df[["model", "total_score_mean", "total_score_median", "total_score_std"]].copy()
    for column in ["total_score_mean", "total_score_median", "total_score_std"]:
        plot_df[column] = pd.to_numeric(plot_df[column], errors="coerce")
    plot_df = plot_df.dropna(subset=["total_score_mean", "total_score_median", "total_score_std"])

    model_order = [m for m in get_model_order(input_dir) if m in set(plot_df["model"])]
    plot_df = plot_df.set_index("model").reindex(model_order).dropna().reset_index()
    plot_df["family"] = plot_df["model"].map(get_family)

    fig, ax = plt.subplots(figsize=(10.8, 6.5))

    good_zone = Rectangle(
        (0, 18.15),
        2.35,
        MAX_SCORE + 0.3 - 18.15,
        facecolor="#2ca02c",
        edgecolor="#1b7f2a",
        linewidth=1.4,
        linestyle="--",
        alpha=0.13,
        zorder=0,
    )
    ax.add_patch(good_zone)
    ax.text(
        0.18,
        20.2,
        "zona migliore:\nalto score, bassa variabilita",
        ha="left",
        va="top",
        fontsize=9,
        color="#2f6b2f",
    )

    for family in FAMILY_ORDER:
        family_df = plot_df[plot_df["family"] == family]
        if family_df.empty:
            continue
        ax.scatter(
            family_df["total_score_std"],
            family_df["total_score_mean"],
            s=115,
            color=FAMILY_COLORS.get(family, "#4c4c4c"),
            edgecolors="white",
            linewidths=1.1,
            alpha=0.96,
            label=family,
            zorder=3,
        )

    label_offsets = {
        "gpt-5.4": (10, 8),
        "gpt-5.4-mini": (10, -16),
        "gpt-5-mini": (10, 8),
        "gpt-4.1-mini": (10, -15),
        "gpt-5.4-nano": (10, 8),
        "gpt-5-nano": (10, 8),
        "gpt-4.1-nano": (-10, -16),
        "gpt-4o-mini": (-10, 8),
    }

    for _, row in plot_df.iterrows():
        model = row["model"]
        dx, dy = label_offsets.get(model, (10, 8))
        ax.annotate(
            model,
            (row["total_score_std"], row["total_score_mean"]),
            textcoords="offset points",
            xytext=(dx, dy),
            ha="right" if dx < 0 else "left",
            va="top" if dy < 0 else "bottom",
            fontsize=8.5,
            bbox={
                "boxstyle": "round,pad=0.18",
                "facecolor": "white",
                "edgecolor": "#dddddd",
                "linewidth": 0.4,
                "alpha": 0.92,
            },
            arrowprops={
                "arrowstyle": "-",
                "color": "#777777",
                "linewidth": 0.5,
                "alpha": 0.55,
            },
            zorder=4,
        )

    ax.set_title("Mappa qualita-stabilita dei modelli", fontsize=14, pad=14)
    ax.set_xlabel("Deviazione standard dello score (piu bassa = piu stabile)")
    ax.set_ylabel("Score medio (0-21)")
    ax.set_xlim(0, max(4.4, float(plot_df["total_score_std"].max()) + 0.35))
    ax.set_ylim(11.8, MAX_SCORE + 0.3)
    ax.set_yticks([12, 15, 18, 21])

    ax.legend(
        title="Famiglia modello",
        frameon=True,
        facecolor="white",
        edgecolor="#dddddd",
        framealpha=0.94,
        loc="lower left",
    )

    ax.grid(axis="both", alpha=0.22)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()
    save_figure(fig, output_dir, basename)
    return basename


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genera i grafici secondari/appendice della tesi dai CSV aggregati."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("."),
        help="Cartella che contiene i CSV aggregati, es. batch_v1/_aggregate.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Cartella di output delle figure. Default: <input-dir>/figures_appendix.",
    )
    parser.add_argument(
        "--fig",
        choices=["all", "a1", "a2", "a3"],
        default="all",
        help="Quale figura generare: all, a1, a2 oppure a3.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_dir = args.input_dir.resolve()
    output_dir = args.output_dir.resolve() if args.output_dir else input_dir / "figures_appendix"

    generated_basenames: list[str] = []

    if args.fig in ("all", "a1"):
        generated_basenames.append(appendix_a1_score_vs_latenza(input_dir, output_dir))

    if args.fig in ("all", "a2"):
        generated_basenames.append(appendix_a2_heatmap_modello_criterio(input_dir, output_dir))

    if args.fig in ("all", "a3"):
        generated_basenames.append(appendix_a3_stabilita_score_modello(input_dir, output_dir))

    write_captions(output_dir, generated_basenames)

    print("\nGenerazione grafici appendice completata.")
    print(f"Input dir:  {input_dir}")
    print(f"Output dir: {output_dir}")


if __name__ == "__main__":
    main()
