from pathlib import Path
import re

import pandas as pd
import matplotlib.pyplot as plt


BASE_DIR = Path(__file__).resolve().parent.parent
MD_FILE = BASE_DIR / "notes" / "results_comparison_summary.md"
OUTPUT_BAR_FILE = BASE_DIR / "notes" / "bar_chart_map5095.png"
OUTPUT_SCATTER_FILE = BASE_DIR / "notes" / "scatter_precision_recall.png"

START_MARKER = "# 1. Tabella master di tutti gli esperimenti completati"
END_MARKER = "# 2. Ranking globale per metrica"


def extract_master_table(md_text: str) -> pd.DataFrame:
    """Estrae la tabella master dal markdown e la converte in DataFrame."""
    try:
        start = md_text.index(START_MARKER)
        end = md_text.index(END_MARKER)
    except ValueError as e:
        raise RuntimeError(
            "Non riesco a trovare i marker della tabella master nel markdown."
        ) from e

    section = md_text[start:end]

    table_lines = [
        line.strip()
        for line in section.splitlines()
        if line.strip().startswith("|")
    ]

    if len(table_lines) < 3:
        raise RuntimeError("Tabella markdown non trovata o incompleta.")

    header = [cell.strip() for cell in table_lines[0].strip("|").split("|")]
    rows = []

    for line in table_lines[2:]:  # salta header + separatore
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) == len(header):
            rows.append(cells)

    if not rows:
        raise RuntimeError("Nessuna riga valida trovata nella tabella master.")

    return pd.DataFrame(rows, columns=header)


def clean_numeric_column(series: pd.Series) -> pd.Series:
    """Pulisce una colonna numerica letta da markdown."""
    return pd.to_numeric(
        series.astype(str)
        .str.replace(",", ".", regex=False)
        .str.replace(r"[^0-9.\-]", "", regex=True),
        errors="coerce",
    )


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Pulisce le colonne numeriche utili ai grafici."""
    numeric_cols = ["Precision", "Recall", "F1-score", "mAP@0.5", "mAP@0.5:0.95"]
    for col in numeric_cols:
        if col not in df.columns:
            raise RuntimeError(f"Colonna mancante nella tabella: {col}")
        df[col] = clean_numeric_column(df[col])

    return df


def make_bar_chart_map5095(df: pd.DataFrame) -> None:
    """Crea il bar chart orizzontale per mAP@0.5:0.95."""
    plot_df = df[["Exp ID", "Modello", "Augmentation", "mAP@0.5:0.95"]].copy()
    plot_df = plot_df.dropna(subset=["mAP@0.5:0.95"])

    if plot_df.empty:
        raise RuntimeError("Nessun valore valido trovato per mAP@0.5:0.95.")

    plot_df["Label"] = (
        plot_df["Exp ID"] + " - " + plot_df["Modello"] + " - " + plot_df["Augmentation"]
    )
    plot_df = plot_df.sort_values("mAP@0.5:0.95", ascending=True)

    plt.figure(figsize=(12, 8))
    bars = plt.barh(plot_df["Label"], plot_df["mAP@0.5:0.95"])

    plt.xlabel("mAP@0.5:0.95")
    plt.ylabel("Esperimento")
    plt.title("Confronto mAP@0.5:0.95 tra tutti gli esperimenti")
    plt.grid(axis="x", alpha=0.3)

    for bar, value in zip(bars, plot_df["mAP@0.5:0.95"]):
        plt.text(
            value + 0.002,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.4f}",
            va="center",
            fontsize=9,
        )

    plt.tight_layout()
    plt.savefig(OUTPUT_BAR_FILE, dpi=200, bbox_inches="tight")
    plt.show()

    print(f"Bar chart salvato in: {OUTPUT_BAR_FILE.resolve()}")


def make_scatter_precision_recall(df: pd.DataFrame) -> None:
    """Crea lo scatter plot Precision vs Recall."""
    plot_df = df[["Exp ID", "Modello", "Precision", "Recall"]].copy()
    plot_df = plot_df.dropna(subset=["Precision", "Recall"])

    if plot_df.empty:
        raise RuntimeError("Nessun valore valido trovato per Precision/Recall.")

    plt.figure(figsize=(10, 8))

    # Un marker diverso per famiglia
    markers = {
        "YOLOv7": "o",
        "YOLOv8": "s",
        "YOLOv11": "^",
    }

    for model_name, group in plot_df.groupby("Modello"):
        plt.scatter(
            group["Recall"],
            group["Precision"],
            marker=markers.get(model_name, "o"),
            s=80,
            label=model_name,
        )

        # Etichette dei punti
        for _, row in group.iterrows():
            plt.annotate(
                row["Exp ID"],
                (row["Recall"], row["Precision"]),
                textcoords="offset points",
                xytext=(5, 5),
                fontsize=9,
            )

    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Scatter plot Precision vs Recall")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_SCATTER_FILE, dpi=200, bbox_inches="tight")
    plt.show()

    print(f"Scatter plot salvato in: {OUTPUT_SCATTER_FILE.resolve()}")


def main() -> None:
    if not MD_FILE.exists():
        raise FileNotFoundError(f"File markdown non trovato: {MD_FILE}")

    md_text = MD_FILE.read_text(encoding="utf-8")
    df = extract_master_table(md_text)
    df = prepare_dataframe(df)

    make_bar_chart_map5095(df)
    make_scatter_precision_recall(df)


if __name__ == "__main__":
    main()