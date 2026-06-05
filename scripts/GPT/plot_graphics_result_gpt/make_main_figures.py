#!/usr/bin/env python3
"""
make_main_figures.py

Script unico per generare i grafici principali della tesi a partire dai CSV
aggregati del judge.

Contiene:
    Figura 1 - Score medio per modello
    Figura 2 - Score medio per modello e tipo di input
    Figura 3 - Delta dell'immagine per circuito
    Figura 4 - Score medio per circuito
    Figura 5 - Heatmap modello × circuito
    Figura 6 - Top-1 e Top-3 accuracy per modello
    Figura 7 - Errori gravi medi per modello
    Figura 8 - Score vs Costo

Esempio uso:
    python make_main_figures.py --input-dir "C:/.../batch_v1/_aggregate"

Output default:
    <input-dir>/figures_main/

Per ogni figura vengono salvati:
    - PNG
    - una caption in figure_captions.md

Nota:
    Le caption vengono salvate fuori dall'immagine, così il grafico resta pulito
    e la descrizione può essere copiata direttamente nella tesi.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter


# -----------------------------------------------------------------------------
# Configurazione generale
# -----------------------------------------------------------------------------

MAX_SCORE = 21

# Ordine di fallback se un modello non è presente nel file aggregate_by_model.csv.
# Normalmente l'ordine delle figure viene ricavato dallo score medio della Figura 1.
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

INPUT_TYPE_ORDER = [
    "JSON + datasheet",
    "JSON + immagine + datasheet",
]

INPUT_TYPE_LABELS = {
    "JSON + datasheet": "JSON + datasheet",
    "JSON + immagine + datasheet": "JSON + immagine + datasheet",
}

# Caption pronte per la tesi.
FIGURE_CAPTIONS = {
    "fig01_score_medio_per_modello": (
        "Figura 1 — Score medio per modello sui circuiti analizzati. "
        "Il grafico riporta il punteggio medio assegnato dal judge a ciascun modello, "
        "aggregando tutte le run disponibili e considerando entrambe le modalità di input. "
        "I modelli sono ordinati in modo decrescente rispetto allo score medio. "
        "Il risultato consente di confrontare la qualità diagnostica complessiva dei modelli: "
        "un valore più alto indica una maggiore capacità di individuare correttamente la causa "
        "del problema, usare datasheet e rappresentazione topologica, proporre controlli pratici "
        "e ridurre errori o allucinazioni."
    ),
    "fig02_score_modello_input_type": (
        "Figura 2 — Confronto dello score medio per modello e tipo di input. "
        "Il grafico confronta, per ciascun modello, le prestazioni ottenute usando solo "
        "JSON + datasheet rispetto alla configurazione JSON + immagine + datasheet. "
        "Le barre affiancate permettono di valutare se l'informazione visiva produce un "
        "miglioramento effettivo rispetto alla sola rappresentazione topologica del circuito. "
        "Differenze ridotte tra le due barre indicano che il JSON/graph conserva già gran parte "
        "dell'informazione diagnostica utile; differenze positive o negative evidenziano invece "
        "i casi in cui l'immagine aiuta oppure introduce rumore nella diagnosi."
    ),
    "fig03_delta_immagine_per_circuito": (
        "Figura 3 — Variazione dello score con l'aggiunta dell'immagine per ciascun circuito. "
        "Il grafico mostra, per ogni circuito, la differenza media tra lo score ottenuto con "
        "JSON + immagine + datasheet e lo score ottenuto con il solo JSON + datasheet, "
        "aggregando i modelli testati. Valori positivi indicano che l'immagine migliora la "
        "prestazione media; valori prossimi a zero indicano un contributo limitato; valori "
        "negativi indicano che l'immagine può introdurre confusione o distrarre il modello. "
        "Il risultato evidenzia che l'effetto dell'informazione visiva non è sistematico e che "
        "la rappresentazione topologica in JSON contiene già una parte rilevante dell'informazione diagnostica."
    ),
    "fig04_score_medio_per_circuito": (
        "Figura 4 — Difficoltà relativa dei circuiti analizzati. "
        "Il grafico riporta lo score medio ottenuto su ciascun circuito, aggregando tutti i modelli "
        "e le modalità di input. I circuiti sono ordinati in modo decrescente rispetto al punteggio medio. "
        "Valori più alti indicano casi in cui la diagnosi è risultata più agevole, ad esempio perché il guasto "
        "topologico è più evidente, il JSON è più informativo o il datasheet supporta direttamente il ragionamento. "
        "Valori più bassi indicano invece circuiti più critici, caratterizzati da maggiore complessità, "
        "ambiguità tra JSON e immagine o diagnosi meno dirette."
    ),
    "fig05_heatmap_modello_circuito": (
        "Figura 5 — Robustezza dei modelli sui diversi circuiti. "
        "La heatmap mostra lo score medio ottenuto da ciascun modello su ciascun circuito, aggregando le due modalità "
        "di input. Le righe sono ordinate dal modello con score medio complessivo più alto a quello più basso, mentre "
        "le colonne seguono l'ordine dei circuiti dalla Figura 4. Ogni cella permette di osservare se un modello mantiene "
        "prestazioni elevate in modo stabile o se presenta cali su specifiche tipologie circuitali. Questo grafico integra "
        "la media globale dei modelli mostrando la robustezza rispetto ai singoli casi di test."
    ),
    "fig06_top1_top3_accuracy_modello": (
        "Figura 6 — Accuratezza Top-1 e Top-3 per modello. "
        "Il grafico confronta, per ciascun modello, la percentuale di risposte in cui la causa principale indicata "
        "coincide con quella attesa (Top-1) e la percentuale di risposte in cui la causa corretta compare almeno tra "
        "le prime tre ipotesi diagnostiche (Top-3). Una Top-1 elevata indica maggiore affidabilità nella diagnosi "
        "principale; una Top-3 elevata indica che il modello è comunque utile come supporto al troubleshooting, anche "
        "quando non assegna la priorità corretta alla causa più probabile. Una distanza ampia tra Top-1 e Top-3 segnala "
        "che il modello tende a includere la causa corretta, ma fatica a ordinarla correttamente."
    ),
    "fig07_errori_gravi_medi_per_modello": (
        "Figura 7 — Errori gravi medi per modello. "
        "Il grafico riporta il numero medio di errori gravi commessi da ciascun modello nelle run "
        "valutate dal judge. Per errori gravi si intendono risposte potenzialmente fuorvianti per il "
        "troubleshooting, ad esempio diagnosi basate su collegamenti inventati, interpretazioni errate "
        "dei pin o conclusioni tecnicamente fuorvianti rispetto all’input fornito. Valori più bassi "
        "indicano una maggiore affidabilità pratica del modello, mentre valori più alti segnalano un "
        "rischio maggiore di produrre indicazioni diagnostiche scorrette o pericolose."
    ),
    "fig08_score_vs_costo": (
        "Il grafico mette in relazione, per ciascun modello, il costo medio per diagnosi e lo score medio ottenuto sui circuiti analizzati. L'asse del costo è riportato in scala logaritmica per rendere leggibili modelli con ordini di grandezza diversi nel prezzo. Colori distinti identificano le principali famiglie di modelli e le etichette consentono il confronto diretto tra i punti. I modelli collocati nella parte alta a sinistra del grafico offrono il miglior compromesso tra qualità diagnostica e costo economico."
    ),
    "fig09_costo_medio_per_modello": (
        "Figura 9 â€” Costo medio del modello per diagnosi. "
        "Il grafico riporta il costo medio stimato del solo modello generativo per ciascuna diagnosi, escludendo il costo del judge. "
        "I modelli sono ordinati dal meno costoso al piÃ¹ costoso, cosÃ¬ da rendere immediato il confronto economico diretto tra le diverse alternative. "
        "La figura evidenzia il divario di costo tra modelli nano, mini e modello di fascia piÃ¹ alta."
    ),
}


# -----------------------------------------------------------------------------
# Utility
# -----------------------------------------------------------------------------

def ensure_columns(df: pd.DataFrame, required_columns: Iterable[str], filename: str) -> None:
    """Controlla che il CSV contenga le colonne necessarie."""
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(
            f"Nel file {filename} mancano queste colonne: {missing}\n"
            f"Colonne trovate: {list(df.columns)}"
        )


def read_csv(input_dir: Path, filename: str, required_columns: Iterable[str]) -> pd.DataFrame:
    """Legge un CSV dalla cartella aggregata e valida le colonne richieste."""
    path = input_dir / filename
    if not path.exists():
        raise FileNotFoundError(f"File non trovato: {path}")

    df = pd.read_csv(path)
    ensure_columns(df, required_columns, filename)
    return df


def save_figure(fig: plt.Figure, output_dir: Path, basename: str) -> None:
    """Salva la figura in PNG."""
    output_dir.mkdir(parents=True, exist_ok=True)

    png_path = output_dir / f"{basename}.png"
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"[OK] Salvato: {png_path}")


def write_captions(output_dir: Path, generated_basenames: list[str]) -> None:
    """
    Scrive un file Markdown con le caption delle figure generate.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    md_path = output_dir / "figure_captions.md"

    lines_md = ["# Caption figure principali\n"]

    for basename in generated_basenames:
        caption = FIGURE_CAPTIONS.get(basename)
        if not caption:
            continue

        lines_md.append(f"## {basename}\n")
        lines_md.append(caption + "\n")

    md_path.write_text("\n".join(lines_md), encoding="utf-8")
    print(f"[OK] Salvato: {md_path}")


def annotate_bars(ax: plt.Axes, digits: int = 2, dy: float = 0.25, fontsize: int = 9) -> None:
    """Scrive il valore sopra ogni barra."""
    for patch in ax.patches:
        height = patch.get_height()
        if pd.isna(height):
            continue

        x = patch.get_x() + patch.get_width() / 2
        y = height
        ax.text(
            x,
            y + dy,
            f"{height:.{digits}f}",
            ha="center",
            va="bottom",
            fontsize=fontsize,
        )


def annotate_delta_bars(ax: plt.Axes, digits: int = 2, dy: float = 0.10, fontsize: int = 9) -> None:
    """
    Scrive il valore sulle barre di un grafico con valori positivi e negativi.
    Le barre positive hanno il valore sopra; le barre negative sotto.
    """
    for patch in ax.patches:
        height = patch.get_height()
        if pd.isna(height):
            continue

        x = patch.get_x() + patch.get_width() / 2

        if height >= 0:
            y = height + dy
            va = "bottom"
        else:
            y = height - dy
            va = "top"

        ax.text(
            x,
            y,
            f"{height:.{digits}f}",
            ha="center",
            va=va,
            fontsize=fontsize,
        )


def clean_axes(ax: plt.Axes) -> None:
    """Piccole pulizie comuni per rendere i grafici più leggibili."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)


def get_model_order(input_dir: Path) -> list[str]:
    """
    Restituisce l'ordine dei modelli basato sullo score medio complessivo.

    Questo mantiene coerente la Figura 2 con la Figura 1: i modelli sono ordinati
    dal migliore al peggiore secondo lo score medio aggregato.
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
        return df.sort_values("total_score_mean", ascending=False)["model"].tolist()
    except Exception:
        return PREFERRED_MODEL_ORDER


def get_circuit_order(input_dir: Path) -> list[str]:
    """
    Restituisce l'ordine dei circuiti basato sullo score medio complessivo.

    Questo mantiene coerente la Figura 5 con la Figura 4: i circuiti sono ordinati
    dal punteggio medio più alto al più basso.
    """
    try:
        df = read_csv(
            input_dir,
            "aggregate_by_circuit.csv",
            required_columns=["circuit", "total_score_mean"],
        )
        df = df[["circuit", "total_score_mean"]].copy()
        df["total_score_mean"] = pd.to_numeric(df["total_score_mean"], errors="coerce")
        df = df.dropna(subset=["total_score_mean"])
        return df.sort_values("total_score_mean", ascending=False)["circuit"].tolist()
    except Exception:
        return []


def set_common_score_axis(ax: plt.Axes) -> None:
    """Imposta l'asse Y comune per gli score del judge."""
    ax.set_ylim(0, MAX_SCORE + 1.4)
    ax.set_yticks([0, 3, 6, 9, 12, 15, 18, 21])


# -----------------------------------------------------------------------------
# Figura 1 - Score medio per modello
# -----------------------------------------------------------------------------

def fig01_score_medio_per_modello(input_dir: Path, output_dir: Path) -> str:
    """
    Bar chart ordinato per score medio decrescente.

    File richiesto:
        aggregate_by_model.csv

    Colonne usate:
        model
        total_score_mean

    Legenda:
        Non necessaria, perché il grafico contiene una sola serie:
        score medio per modello.
    """
    basename = "fig01_score_medio_per_modello"

    df = read_csv(
        input_dir,
        "aggregate_by_model.csv",
        required_columns=["model", "total_score_mean"],
    )

    plot_df = df[["model", "total_score_mean"]].copy()
    plot_df["total_score_mean"] = pd.to_numeric(plot_df["total_score_mean"], errors="coerce")
    plot_df = plot_df.dropna(subset=["total_score_mean"])
    plot_df = plot_df.sort_values("total_score_mean", ascending=False)

    fig, ax = plt.subplots(figsize=(10, 5.8))

    ax.bar(plot_df["model"], plot_df["total_score_mean"])

    ax.set_title("Score medio per modello su tutti i circuiti", fontsize=14, pad=14)
    ax.set_xlabel("Modello")
    ax.set_ylabel("Score medio (0–21)")
    set_common_score_axis(ax)

    ax.tick_params(axis="x", rotation=35)
    for label in ax.get_xticklabels():
        label.set_horizontalalignment("right")

    annotate_bars(ax, digits=2)
    clean_axes(ax)

    fig.tight_layout()
    save_figure(fig, output_dir, basename)

    return basename


# -----------------------------------------------------------------------------
# Figura 2 - Score medio per modello e tipo di input
# -----------------------------------------------------------------------------

def fig02_score_modello_input_type(input_dir: Path, output_dir: Path) -> str:
    """
    Grouped bar chart con due barre per modello:
        - JSON + datasheet
        - JSON + immagine + datasheet

    File richiesto:
        aggregate_by_model_input.csv

    Colonne usate:
        model
        input_type
        total_score_mean
    """
    basename = "fig02_score_modello_input_type"

    df = read_csv(
        input_dir,
        "aggregate_by_model_input.csv",
        required_columns=["model", "input_type", "total_score_mean"],
    )

    plot_df = df[["model", "input_type", "total_score_mean"]].copy()
    plot_df["total_score_mean"] = pd.to_numeric(plot_df["total_score_mean"], errors="coerce")
    plot_df = plot_df.dropna(subset=["total_score_mean"])

    model_order = [m for m in get_model_order(input_dir) if m in set(plot_df["model"])]

    pivot = (
        plot_df
        .pivot_table(
            index="model",
            columns="input_type",
            values="total_score_mean",
            aggfunc="mean",
        )
        .reindex(model_order)
    )

    for input_type in INPUT_TYPE_ORDER:
        if input_type not in pivot.columns:
            pivot[input_type] = pd.NA
    pivot = pivot[INPUT_TYPE_ORDER]

    fig, ax = plt.subplots(figsize=(11.5, 6.2))

    x = list(range(len(pivot.index)))
    width = 0.38

    offsets = [-width / 2, width / 2]
    for offset, input_type in zip(offsets, INPUT_TYPE_ORDER):
        values = pd.to_numeric(pivot[input_type], errors="coerce")
        ax.bar(
            [i + offset for i in x],
            values,
            width=width,
            label=INPUT_TYPE_LABELS.get(input_type, input_type),
        )

    ax.set_title("Confronto tra JSON-only e JSON + immagine per modello", fontsize=14, pad=18)
    ax.set_xlabel("Modello")
    ax.set_ylabel("Score medio (0–21)")
    set_common_score_axis(ax)

    ax.set_xticks(x)
    ax.set_xticklabels(pivot.index)
    ax.tick_params(axis="x", rotation=35)
    for label in ax.get_xticklabels():
        label.set_horizontalalignment("right")

    # Valori sopra le barre: utili perché le differenze sono spesso piccole.
    annotate_bars(ax, digits=2, dy=0.22, fontsize=8)

    ax.legend(
        title="Tipo di input",
        frameon=False,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.08),
        ncol=2,
    )

    clean_axes(ax)
    fig.tight_layout()
    save_figure(fig, output_dir, basename)

    return basename


# -----------------------------------------------------------------------------
# Figura 3 - Delta dell'immagine per circuito
# -----------------------------------------------------------------------------

def fig03_delta_immagine_per_circuito(input_dir: Path, output_dir: Path) -> str:
    """
    Bar chart del delta medio per circuito:

        delta = score(JSON + immagine + datasheet) - score(JSON + datasheet)

    File richiesto:
        deltas_image_vs_json.csv

    Colonne usate:
        circuit
        delta_score_img_minus_json
    """
    basename = "fig03_delta_immagine_per_circuito"

    df = read_csv(
        input_dir,
        "deltas_image_vs_json.csv",
        required_columns=["circuit", "delta_score_img_minus_json"],
    )

    plot_df = df[["circuit", "delta_score_img_minus_json"]].copy()
    plot_df["delta_score_img_minus_json"] = pd.to_numeric(
        plot_df["delta_score_img_minus_json"],
        errors="coerce",
    )
    plot_df = plot_df.dropna(subset=["delta_score_img_minus_json"])

    # Media del delta per circuito, aggregando tutti i modelli testati.
    plot_df = (
        plot_df
        .groupby("circuit", as_index=False)["delta_score_img_minus_json"]
        .mean()
        .sort_values("delta_score_img_minus_json", ascending=False)
    )

    fig, ax = plt.subplots(figsize=(9.8, 5.8))

    ax.bar(plot_df["circuit"], plot_df["delta_score_img_minus_json"])

    # Linea di riferimento: sopra 0 l'immagine migliora, sotto 0 peggiora.
    ax.axhline(0, linewidth=1.2, color="black", alpha=0.85)

    ax.set_title("Variazione dello score con l'aggiunta dell'immagine", fontsize=14, pad=14)
    ax.set_xlabel("Circuito")
    ax.set_ylabel("Δ score (img+JSON − JSON)")

    min_delta = float(plot_df["delta_score_img_minus_json"].min())
    max_delta = float(plot_df["delta_score_img_minus_json"].max())
    y_min = min(-1.0, min_delta - 0.45)
    y_max = max(1.0, max_delta + 0.45)
    ax.set_ylim(y_min, y_max)

    annotate_delta_bars(ax, digits=2, dy=0.10, fontsize=9)
    clean_axes(ax)

    fig.tight_layout()
    save_figure(fig, output_dir, basename)

    return basename




# -----------------------------------------------------------------------------
# Figura 4 - Score medio per circuito
# -----------------------------------------------------------------------------

def fig04_score_medio_per_circuito(input_dir: Path, output_dir: Path) -> str:
    """
    Bar chart ordinato per score medio decrescente.

    File richiesto:
        aggregate_by_circuit.csv

    Colonne usate:
        circuit
        total_score_mean
    """
    basename = "fig04_score_medio_per_circuito"

    df = read_csv(
        input_dir,
        "aggregate_by_circuit.csv",
        required_columns=["circuit", "total_score_mean"],
    )

    plot_df = df[["circuit", "total_score_mean"]].copy()
    plot_df["total_score_mean"] = pd.to_numeric(plot_df["total_score_mean"], errors="coerce")
    plot_df = plot_df.dropna(subset=["total_score_mean"])
    plot_df = plot_df.sort_values("total_score_mean", ascending=False)

    fig, ax = plt.subplots(figsize=(9.8, 5.8))

    ax.bar(plot_df["circuit"], plot_df["total_score_mean"])

    ax.set_title("Difficoltà relativa dei circuiti analizzati", fontsize=14, pad=14)
    ax.set_xlabel("Circuito")
    ax.set_ylabel("Score medio (0–21)")
    set_common_score_axis(ax)

    annotate_bars(ax, digits=2, dy=0.25, fontsize=9)
    clean_axes(ax)

    fig.tight_layout()
    save_figure(fig, output_dir, basename)

    return basename




# -----------------------------------------------------------------------------
# Figura 5 - Heatmap modello × circuito
# -----------------------------------------------------------------------------

def fig05_heatmap_modello_circuito(input_dir: Path, output_dir: Path) -> str:
    """
    Heatmap dello score medio per coppia modello-circuito.

    File richiesto:
        all_runs.csv

    Colonne usate:
        model
        circuit
        total_score

    Valore della cella:
        media di total_score, aggregando le due modalità di input.
    """
    basename = "fig05_heatmap_modello_circuito"

    df = read_csv(
        input_dir,
        "all_runs.csv",
        required_columns=["model", "circuit", "total_score"],
    )

    plot_df = df[["model", "circuit", "total_score"]].copy()
    plot_df["total_score"] = pd.to_numeric(plot_df["total_score"], errors="coerce")
    plot_df = plot_df.dropna(subset=["total_score"])

    model_order = [m for m in get_model_order(input_dir) if m in set(plot_df["model"])]
    circuit_order = [c for c in get_circuit_order(input_dir) if c in set(plot_df["circuit"])]

    if not model_order:
        model_order = (
            plot_df.groupby("model")["total_score"]
            .mean()
            .sort_values(ascending=False)
            .index
            .tolist()
        )

    if not circuit_order:
        circuit_order = (
            plot_df.groupby("circuit")["total_score"]
            .mean()
            .sort_values(ascending=False)
            .index
            .tolist()
        )

    pivot = (
        plot_df
        .pivot_table(
            index="model",
            columns="circuit",
            values="total_score",
            aggfunc="mean",
        )
        .reindex(index=model_order, columns=circuit_order)
    )

    fig, ax = plt.subplots(figsize=(10.5, 6.4))

    im = ax.imshow(pivot.values, vmin=0, vmax=MAX_SCORE, aspect="auto")

    ax.set_title("Robustezza dei modelli sui diversi circuiti", fontsize=14, pad=14)
    ax.set_xlabel("Circuito")
    ax.set_ylabel("Modello")

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)

    for i, model in enumerate(pivot.index):
        for j, circuit in enumerate(pivot.columns):
            value = pivot.loc[model, circuit]
            label = "" if pd.isna(value) else f"{value:.1f}"
            ax.text(j, i, label, ha="center", va="center", fontsize=8)

    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Score medio (0–21)")

    fig.tight_layout()
    save_figure(fig, output_dir, basename)

    return basename




# -----------------------------------------------------------------------------
# Figura 6 - Top-1 e Top-3 accuracy per modello
# -----------------------------------------------------------------------------

def fig06_top1_top3_accuracy_modello(input_dir: Path, output_dir: Path) -> str:
    """
    Grouped bar chart con due barre per modello:
        - Top-1 accuracy
        - Top-3 accuracy

    File richiesto:
        aggregate_by_model.csv

    Colonne usate:
        model
        top1_correct_rate
        top3_contains_correct_rate

    Nota:
        Se i valori sono tra 0 e 1, vengono convertiti automaticamente in percentuale.
    """
    basename = "fig06_top1_top3_accuracy_modello"

    df = read_csv(
        input_dir,
        "aggregate_by_model.csv",
        required_columns=["model", "top1_correct_rate", "top3_contains_correct_rate"],
    )

    plot_df = df[["model", "top1_correct_rate", "top3_contains_correct_rate"]].copy()
    plot_df["top1_correct_rate"] = pd.to_numeric(plot_df["top1_correct_rate"], errors="coerce")
    plot_df["top3_contains_correct_rate"] = pd.to_numeric(plot_df["top3_contains_correct_rate"], errors="coerce")
    plot_df = plot_df.dropna(subset=["top1_correct_rate", "top3_contains_correct_rate"])

    model_order = [m for m in get_model_order(input_dir) if m in set(plot_df["model"])]
    plot_df = plot_df.set_index("model").reindex(model_order).dropna(subset=["top1_correct_rate", "top3_contains_correct_rate"])

    # I CSV aggregati di solito salvano i rate come frazioni 0-1.
    # Se invece fossero già percentuali 0-100, non li modifichiamo.
    if plot_df[["top1_correct_rate", "top3_contains_correct_rate"]].max().max() <= 1.0:
        plot_df["top1_correct_rate"] = plot_df["top1_correct_rate"] * 100.0
        plot_df["top3_contains_correct_rate"] = plot_df["top3_contains_correct_rate"] * 100.0

    fig, ax = plt.subplots(figsize=(11.5, 6.2))

    x = list(range(len(plot_df.index)))
    width = 0.38

    ax.bar(
        [i - width / 2 for i in x],
        plot_df["top1_correct_rate"],
        width=width,
        label="Top-1 accuracy",
    )
    ax.bar(
        [i + width / 2 for i in x],
        plot_df["top3_contains_correct_rate"],
        width=width,
        label="Top-3 accuracy",
    )

    ax.set_title("Accuratezza Top-1 e Top-3 per modello", fontsize=14, pad=18)
    ax.set_xlabel("Modello")
    ax.set_ylabel("Accuracy (%)")
    ax.set_ylim(0, 108)
    ax.set_yticks([0, 20, 40, 60, 80, 100])

    ax.set_xticks(x)
    ax.set_xticklabels(plot_df.index)
    ax.tick_params(axis="x", rotation=35)
    for label in ax.get_xticklabels():
        label.set_horizontalalignment("right")

    annotate_bars(ax, digits=1, dy=1.6, fontsize=8)

    ax.legend(
        title="Metrica",
        frameon=False,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.08),
        ncol=2,
    )

    clean_axes(ax)
    fig.tight_layout()
    save_figure(fig, output_dir, basename)

    return basename

# -----------------------------------------------------------------------------
# Figura 6 - Errori gravi per modello
# -----------------------------------------------------------------------------

def fig07_errori_gravi_medi_per_modello(input_dir: Path, output_dir: Path) -> str:
    """
    Bar chart del numero medio di errori gravi per modello.

    File richiesto:
        aggregate_by_model.csv

    Colonne usate:
        model
        major_errors_n_mean

    Interpretazione:
        Valori più bassi sono migliori.
    """
    basename = "fig07_errori_gravi_medi_per_modello"

    df = read_csv(
        input_dir,
        "aggregate_by_model.csv",
        required_columns=["model", "major_errors_n_mean"],
    )

    plot_df = df[["model", "major_errors_n_mean"]].copy()
    plot_df["major_errors_n_mean"] = pd.to_numeric(plot_df["major_errors_n_mean"], errors="coerce")
    plot_df = plot_df.dropna(subset=["major_errors_n_mean"])
    plot_df = plot_df.sort_values("major_errors_n_mean", ascending=True)

    fig, ax = plt.subplots(figsize=(10.6, 5.8))
    ax.bar(plot_df["model"], plot_df["major_errors_n_mean"])

    ax.set_title("Errori gravi medi per modello", fontsize=14, pad=14)
    ax.set_xlabel("Modello")
    ax.set_ylabel("Numero medio di errori gravi")

    y_max = float(plot_df["major_errors_n_mean"].max()) if len(plot_df) else 1.0
    ax.set_ylim(0, max(1.0, y_max + 0.35))

    ax.tick_params(axis="x", rotation=35)
    for label in ax.get_xticklabels():
        label.set_horizontalalignment("right")

    annotate_bars(ax, digits=2, dy=0.03)
    clean_axes(ax)

    fig.tight_layout()
    save_figure(fig, output_dir, basename)
    return basename

# -----------------------------------------------------------------------------
# Figura 8 - Score vs costo
# -----------------------------------------------------------------------------

def fig08_score_vs_costo(input_dir: Path, output_dir: Path) -> str:
    """
    Scatter plot del compromesso qualità-costo per modello.

    File richiesto:
        aggregate_by_model.csv

    Colonne usate:
        model
        model_cost_usd_mean
        total_score_mean
    """
    basename = "fig08_score_vs_costo"

    df = read_csv(
        input_dir,
        "aggregate_by_model.csv",
        required_columns=["model", "model_cost_usd_mean", "total_score_mean"],
    )

    plot_df = df[["model", "model_cost_usd_mean", "total_score_mean"]].copy()
    plot_df["model_cost_usd_mean"] = pd.to_numeric(plot_df["model_cost_usd_mean"], errors="coerce")
    plot_df["total_score_mean"] = pd.to_numeric(plot_df["total_score_mean"], errors="coerce")
    plot_df = plot_df.dropna(subset=["model_cost_usd_mean", "total_score_mean"])

    # Ordina i punti per score decrescente come riferimento logico generale.
    plot_df = plot_df.sort_values(["total_score_mean", "model_cost_usd_mean"], ascending=[False, True])

    family_colors = {
        "gpt-5.4": "#1f77b4",
        "gpt-5": "#2ca02c",
        "gpt-4.1": "#ff7f0e",
        "gpt-4o": "#9467bd",
    }

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

    plot_df["family"] = plot_df["model"].map(get_family)
    plot_df["color"] = plot_df["family"].map(family_colors).fillna("#4c4c4c")

    low_max = 0.022
    high_min = 0.06
    plot_df["cost_label"] = plot_df["model_cost_usd_mean"].map(lambda v: f"${v:.3f}")

    fig, (ax_left, ax_right) = plt.subplots(
        1,
        2,
        figsize=(11.2, 6.5),
        sharey=True,
        gridspec_kw={"width_ratios": [4.7, 1.5], "wspace": 0.05},
    )

    left_df = plot_df[plot_df["model_cost_usd_mean"] <= low_max].copy()
    right_df = plot_df[plot_df["model_cost_usd_mean"] >= high_min].copy()

    for ax, subset in ((ax_left, left_df), (ax_right, right_df)):
        ax.scatter(
            subset["model_cost_usd_mean"],
            subset["total_score_mean"],
            s=95,
            c=subset["color"],
            edgecolors="white",
            linewidths=0.9,
            zorder=3,
        )

    fig.suptitle("Compromesso qualita-costo per modello", fontsize=14, y=0.98)
    fig.supxlabel("Costo medio per diagnosi (USD)")
    ax_left.set_ylabel("Score medio (0-21)")

    ax_left.set_ylim(0, MAX_SCORE + 0.6)
    ax_left.set_yticks([0, 3, 6, 9, 12, 15, 18, 21])
    ax_left.set_xlim(0, 0.0225)
    ax_right.set_xlim(0.068, 0.0785)

    ax_left.set_xticks([0.0, 0.005, 0.010, 0.015, 0.020])
    ax_left.set_xticklabels(["0.000", "0.005", "0.010", "0.015", "0.020"])
    ax_right.set_xticks([0.070, 0.075])
    ax_right.set_xticklabels(["0.070", "0.075"])

    ax_left.spines["right"].set_visible(False)
    ax_right.spines["left"].set_visible(False)
    ax_right.tick_params(labelleft=False, left=False)

    d = 0.012
    kwargs = dict(transform=ax_left.transAxes, color="k", clip_on=False, linewidth=1.0)
    ax_left.plot((1 - d, 1 + d), (-d, +d), **kwargs)
    ax_left.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)
    kwargs.update(transform=ax_right.transAxes)
    ax_right.plot((-d, +d), (-d, +d), **kwargs)
    ax_right.plot((-d, +d), (1 - d, 1 + d), **kwargs)

    label_offsets = {
        "gpt-5.4": (10, 10),
        "gpt-5.4-mini": (8, 12),
        "gpt-5-mini": (8, 12),
        "gpt-4.1-mini": (-6, 12),
        "gpt-5.4-nano": (-6, 10),
        "gpt-5-nano": (8, 10),
        "gpt-4.1-nano": (8, 10),
        "gpt-4o-mini": (8, 10),
    }

    def annotate_points(ax, subset):
        for _, row in subset.iterrows():
            label = f"{row['model']}\n{row['cost_label']}"
            dx, dy = label_offsets.get(row["model"], (8, 8))
            ha = "left" if dx >= 0 else "right"
            ax.annotate(
                label,
                (row["model_cost_usd_mean"], row["total_score_mean"]),
                textcoords="offset points",
                xytext=(dx, dy),
                ha=ha,
                va="bottom",
                fontsize=8.3,
                bbox={
                    "boxstyle": "round,pad=0.2",
                    "facecolor": "white",
                    "edgecolor": "none",
                    "alpha": 0.92,
                },
                zorder=4,
            )

    annotate_points(ax_left, left_df)
    annotate_points(ax_right, right_df)

    legend_handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            markerfacecolor=color,
            markeredgecolor="white",
            markeredgewidth=0.9,
            markersize=7.5,
            label=family,
        )
        for family, color in family_colors.items()
    ]
    ax_left.legend(
        handles=legend_handles,
        title="Famiglia modello",
        loc="upper left",
        frameon=False,
    )

    for ax in (ax_left, ax_right):
        clean_axes(ax)
        ax.grid(axis="x", alpha=0.18)
    clean_axes(ax)

    fig.tight_layout()
    save_figure(fig, output_dir, basename)

    return basename


# -----------------------------------------------------------------------------
# Figura 2 - Score medio per modello e tipo di input
# -----------------------------------------------------------------------------

def fig02_score_modello_input_type(input_dir: Path, output_dir: Path) -> str:
    """
    Grouped bar chart con due barre per modello:
        - JSON + datasheet
        - JSON + immagine + datasheet

    File richiesto:
        aggregate_by_model_input.csv

    Colonne usate:
        model
        input_type
        total_score_mean
    """
    basename = "fig02_score_modello_input_type"

    df = read_csv(
        input_dir,
        "aggregate_by_model_input.csv",
        required_columns=["model", "input_type", "total_score_mean"],
    )

    plot_df = df[["model", "input_type", "total_score_mean"]].copy()
    plot_df["total_score_mean"] = pd.to_numeric(plot_df["total_score_mean"], errors="coerce")
    plot_df = plot_df.dropna(subset=["total_score_mean"])

    model_order = [m for m in get_model_order(input_dir) if m in set(plot_df["model"])]

    pivot = (
        plot_df
        .pivot_table(
            index="model",
            columns="input_type",
            values="total_score_mean",
            aggfunc="mean",
        )
        .reindex(model_order)
    )

    for input_type in INPUT_TYPE_ORDER:
        if input_type not in pivot.columns:
            pivot[input_type] = pd.NA
    pivot = pivot[INPUT_TYPE_ORDER]

    fig, ax = plt.subplots(figsize=(11.5, 6.2))

    x = list(range(len(pivot.index)))
    width = 0.38

    offsets = [-width / 2, width / 2]
    for offset, input_type in zip(offsets, INPUT_TYPE_ORDER):
        values = pd.to_numeric(pivot[input_type], errors="coerce")
        ax.bar(
            [i + offset for i in x],
            values,
            width=width,
            label=INPUT_TYPE_LABELS.get(input_type, input_type),
        )

    ax.set_title("Confronto tra JSON-only e JSON + immagine per modello", fontsize=14, pad=18)
    ax.set_xlabel("Modello")
    ax.set_ylabel("Score medio (0–21)")
    set_common_score_axis(ax)

    ax.set_xticks(x)
    ax.set_xticklabels(pivot.index)
    ax.tick_params(axis="x", rotation=35)
    for label in ax.get_xticklabels():
        label.set_horizontalalignment("right")

    # Valori sopra le barre: utili perché le differenze sono spesso piccole.
    annotate_bars(ax, digits=2, dy=0.22, fontsize=8)

    ax.legend(
        title="Tipo di input",
        frameon=False,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.08),
        ncol=2,
    )

    clean_axes(ax)
    fig.tight_layout()
    save_figure(fig, output_dir, basename)

    return basename


# -----------------------------------------------------------------------------
# Figura 3 - Delta dell'immagine per circuito
# -----------------------------------------------------------------------------

def fig03_delta_immagine_per_circuito(input_dir: Path, output_dir: Path) -> str:
    """
    Bar chart del delta medio per circuito:

        delta = score(JSON + immagine + datasheet) - score(JSON + datasheet)

    File richiesto:
        deltas_image_vs_json.csv

    Colonne usate:
        circuit
        delta_score_img_minus_json
    """
    basename = "fig03_delta_immagine_per_circuito"

    df = read_csv(
        input_dir,
        "deltas_image_vs_json.csv",
        required_columns=["circuit", "delta_score_img_minus_json"],
    )

    plot_df = df[["circuit", "delta_score_img_minus_json"]].copy()
    plot_df["delta_score_img_minus_json"] = pd.to_numeric(
        plot_df["delta_score_img_minus_json"],
        errors="coerce",
    )
    plot_df = plot_df.dropna(subset=["delta_score_img_minus_json"])

    # Media del delta per circuito, aggregando tutti i modelli testati.
    plot_df = (
        plot_df
        .groupby("circuit", as_index=False)["delta_score_img_minus_json"]
        .mean()
        .sort_values("delta_score_img_minus_json", ascending=False)
    )

    fig, ax = plt.subplots(figsize=(9.8, 5.8))

    ax.bar(plot_df["circuit"], plot_df["delta_score_img_minus_json"])

    # Linea di riferimento: sopra 0 l'immagine migliora, sotto 0 peggiora.
    ax.axhline(0, linewidth=1.2, color="black", alpha=0.85)

    ax.set_title("Variazione dello score con l'aggiunta dell'immagine", fontsize=14, pad=14)
    ax.set_xlabel("Circuito")
    ax.set_ylabel("Δ score (img+JSON − JSON)")

    min_delta = float(plot_df["delta_score_img_minus_json"].min())
    max_delta = float(plot_df["delta_score_img_minus_json"].max())
    y_min = min(-1.0, min_delta - 0.45)
    y_max = max(1.0, max_delta + 0.45)
    ax.set_ylim(y_min, y_max)

    annotate_delta_bars(ax, digits=2, dy=0.10, fontsize=9)
    clean_axes(ax)

    fig.tight_layout()
    save_figure(fig, output_dir, basename)

    return basename




# -----------------------------------------------------------------------------
# Figura 4 - Score medio per circuito
# -----------------------------------------------------------------------------

def fig04_score_medio_per_circuito(input_dir: Path, output_dir: Path) -> str:
    """
    Bar chart ordinato per score medio decrescente.

    File richiesto:
        aggregate_by_circuit.csv

    Colonne usate:
        circuit
        total_score_mean
    """
    basename = "fig04_score_medio_per_circuito"

    df = read_csv(
        input_dir,
        "aggregate_by_circuit.csv",
        required_columns=["circuit", "total_score_mean"],
    )

    plot_df = df[["circuit", "total_score_mean"]].copy()
    plot_df["total_score_mean"] = pd.to_numeric(plot_df["total_score_mean"], errors="coerce")
    plot_df = plot_df.dropna(subset=["total_score_mean"])
    plot_df = plot_df.sort_values("total_score_mean", ascending=False)

    fig, ax = plt.subplots(figsize=(9.8, 5.8))

    ax.bar(plot_df["circuit"], plot_df["total_score_mean"])

    ax.set_title("Difficoltà relativa dei circuiti analizzati", fontsize=14, pad=14)
    ax.set_xlabel("Circuito")
    ax.set_ylabel("Score medio (0–21)")
    set_common_score_axis(ax)

    annotate_bars(ax, digits=2, dy=0.25, fontsize=9)
    clean_axes(ax)

    fig.tight_layout()
    save_figure(fig, output_dir, basename)

    return basename




# -----------------------------------------------------------------------------
# Figura 5 - Heatmap modello × circuito
# -----------------------------------------------------------------------------

def fig05_heatmap_modello_circuito(input_dir: Path, output_dir: Path) -> str:
    """
    Heatmap dello score medio per coppia modello-circuito.

    File richiesto:
        all_runs.csv

    Colonne usate:
        model
        circuit
        total_score

    Valore della cella:
        media di total_score, aggregando le due modalità di input.
    """
    basename = "fig05_heatmap_modello_circuito"

    df = read_csv(
        input_dir,
        "all_runs.csv",
        required_columns=["model", "circuit", "total_score"],
    )

    plot_df = df[["model", "circuit", "total_score"]].copy()
    plot_df["total_score"] = pd.to_numeric(plot_df["total_score"], errors="coerce")
    plot_df = plot_df.dropna(subset=["total_score"])

    model_order = [m for m in get_model_order(input_dir) if m in set(plot_df["model"])]
    circuit_order = [c for c in get_circuit_order(input_dir) if c in set(plot_df["circuit"])]

    if not model_order:
        model_order = (
            plot_df.groupby("model")["total_score"]
            .mean()
            .sort_values(ascending=False)
            .index
            .tolist()
        )

    if not circuit_order:
        circuit_order = (
            plot_df.groupby("circuit")["total_score"]
            .mean()
            .sort_values(ascending=False)
            .index
            .tolist()
        )

    pivot = (
        plot_df
        .pivot_table(
            index="model",
            columns="circuit",
            values="total_score",
            aggfunc="mean",
        )
        .reindex(index=model_order, columns=circuit_order)
    )

    fig, ax = plt.subplots(figsize=(10.5, 6.4))

    im = ax.imshow(pivot.values, vmin=0, vmax=MAX_SCORE, aspect="auto")

    ax.set_title("Robustezza dei modelli sui diversi circuiti", fontsize=14, pad=14)
    ax.set_xlabel("Circuito")
    ax.set_ylabel("Modello")

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)

    for i, model in enumerate(pivot.index):
        for j, circuit in enumerate(pivot.columns):
            value = pivot.loc[model, circuit]
            label = "" if pd.isna(value) else f"{value:.1f}"
            ax.text(j, i, label, ha="center", va="center", fontsize=8)

    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Score medio (0–21)")

    fig.tight_layout()
    save_figure(fig, output_dir, basename)

    return basename




# -----------------------------------------------------------------------------
# Figura 6 - Top-1 e Top-3 accuracy per modello
# -----------------------------------------------------------------------------

def fig06_top1_top3_accuracy_modello(input_dir: Path, output_dir: Path) -> str:
    """
    Grouped bar chart con due barre per modello:
        - Top-1 accuracy
        - Top-3 accuracy

    File richiesto:
        aggregate_by_model.csv

    Colonne usate:
        model
        top1_correct_rate
        top3_contains_correct_rate

    Nota:
        Se i valori sono tra 0 e 1, vengono convertiti automaticamente in percentuale.
    """
    basename = "fig06_top1_top3_accuracy_modello"

    df = read_csv(
        input_dir,
        "aggregate_by_model.csv",
        required_columns=["model", "top1_correct_rate", "top3_contains_correct_rate"],
    )

    plot_df = df[["model", "top1_correct_rate", "top3_contains_correct_rate"]].copy()
    plot_df["top1_correct_rate"] = pd.to_numeric(plot_df["top1_correct_rate"], errors="coerce")
    plot_df["top3_contains_correct_rate"] = pd.to_numeric(plot_df["top3_contains_correct_rate"], errors="coerce")
    plot_df = plot_df.dropna(subset=["top1_correct_rate", "top3_contains_correct_rate"])

    model_order = [m for m in get_model_order(input_dir) if m in set(plot_df["model"])]
    plot_df = plot_df.set_index("model").reindex(model_order).dropna(subset=["top1_correct_rate", "top3_contains_correct_rate"])

    # I CSV aggregati di solito salvano i rate come frazioni 0-1.
    # Se invece fossero già percentuali 0-100, non li modifichiamo.
    if plot_df[["top1_correct_rate", "top3_contains_correct_rate"]].max().max() <= 1.0:
        plot_df["top1_correct_rate"] = plot_df["top1_correct_rate"] * 100.0
        plot_df["top3_contains_correct_rate"] = plot_df["top3_contains_correct_rate"] * 100.0

    fig, ax = plt.subplots(figsize=(11.5, 6.2))

    x = list(range(len(plot_df.index)))
    width = 0.38

    ax.bar(
        [i - width / 2 for i in x],
        plot_df["top1_correct_rate"],
        width=width,
        label="Top-1 accuracy",
    )
    ax.bar(
        [i + width / 2 for i in x],
        plot_df["top3_contains_correct_rate"],
        width=width,
        label="Top-3 accuracy",
    )

    ax.set_title("Accuratezza Top-1 e Top-3 per modello", fontsize=14, pad=18)
    ax.set_xlabel("Modello")
    ax.set_ylabel("Accuracy (%)")
    ax.set_ylim(0, 108)
    ax.set_yticks([0, 20, 40, 60, 80, 100])

    ax.set_xticks(x)
    ax.set_xticklabels(plot_df.index)
    ax.tick_params(axis="x", rotation=35)
    for label in ax.get_xticklabels():
        label.set_horizontalalignment("right")

    annotate_bars(ax, digits=1, dy=1.6, fontsize=8)

    ax.legend(
        title="Metrica",
        frameon=False,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.08),
        ncol=2,
    )

    clean_axes(ax)
    fig.tight_layout()
    save_figure(fig, output_dir, basename)

    return basename

# -----------------------------------------------------------------------------
# Figura 6 - Errori gravi per modello
# -----------------------------------------------------------------------------

def fig07_errori_gravi_medi_per_modello(input_dir: Path, output_dir: Path) -> str:
    """
    Bar chart del numero medio di errori gravi per modello.

    File richiesto:
        aggregate_by_model.csv

    Colonne usate:
        model
        major_errors_n_mean

    Interpretazione:
        Valori più bassi sono migliori.
    """
    basename = "fig07_errori_gravi_medi_per_modello"

    df = read_csv(
        input_dir,
        "aggregate_by_model.csv",
        required_columns=["model", "major_errors_n_mean"],
    )

    plot_df = df[["model", "major_errors_n_mean"]].copy()
    plot_df["major_errors_n_mean"] = pd.to_numeric(plot_df["major_errors_n_mean"], errors="coerce")
    plot_df = plot_df.dropna(subset=["major_errors_n_mean"])
    plot_df = plot_df.sort_values("major_errors_n_mean", ascending=True)

    fig, ax = plt.subplots(figsize=(10.6, 5.8))
    ax.bar(plot_df["model"], plot_df["major_errors_n_mean"])

    ax.set_title("Errori gravi medi per modello", fontsize=14, pad=14)
    ax.set_xlabel("Modello")
    ax.set_ylabel("Numero medio di errori gravi")

    y_max = float(plot_df["major_errors_n_mean"].max()) if len(plot_df) else 1.0
    ax.set_ylim(0, max(1.0, y_max + 0.35))

    ax.tick_params(axis="x", rotation=35)
    for label in ax.get_xticklabels():
        label.set_horizontalalignment("right")

    annotate_bars(ax, digits=2, dy=0.03)
    clean_axes(ax)

    fig.tight_layout()
    save_figure(fig, output_dir, basename)
    return basename

# -----------------------------------------------------------------------------
# Figura 8 - Score vs costo
# -----------------------------------------------------------------------------

def fig08_score_vs_costo(input_dir: Path, output_dir: Path) -> str:
    """
    Scatter plot del compromesso qualità-costo per modello.

    File richiesto:
        aggregate_by_model.csv

    Colonne usate:
        model
        model_cost_usd_mean
        total_score_mean
    """
    basename = "fig08_score_vs_costo"

    df = read_csv(
        input_dir,
        "aggregate_by_model.csv",
        required_columns=["model", "model_cost_usd_mean", "total_score_mean"],
    )

    plot_df = df[["model", "model_cost_usd_mean", "total_score_mean"]].copy()
    plot_df["model_cost_usd_mean"] = pd.to_numeric(
        plot_df["model_cost_usd_mean"],
        errors="coerce",
    )
    plot_df["total_score_mean"] = pd.to_numeric(
        plot_df["total_score_mean"],
        errors="coerce",
    )

    plot_df = plot_df.dropna(subset=["model_cost_usd_mean", "total_score_mean"])
    plot_df = plot_df[plot_df["model_cost_usd_mean"] > 0].copy()

    # Conversione in centesimi di dollaro:
    # 0.018 USD = 1.8 centesimi.
    plot_df["cost_cents"] = plot_df["model_cost_usd_mean"] * 100.0

    family_colors = {
        "gpt-5.4": "#1f77b4",   # blu
        "gpt-5": "#2ca02c",     # verde
        "gpt-4.1": "#ff7f0e",   # arancione
        "gpt-4o": "#9467bd",    # viola
        "Altro": "#4c4c4c",
    }

    family_order = ["gpt-5.4", "gpt-5", "gpt-4.1", "gpt-4o", "Altro"]

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

    plot_df["family"] = plot_df["model"].map(get_family)

    # Ordine logico per disegnare prima i modelli più economici e poi quelli più costosi.
    plot_df = plot_df.sort_values("cost_cents", ascending=True)

    fig, ax = plt.subplots(figsize=(12.2, 6.8))

    # Disegno separato per famiglia: così la legenda è pulita.
    for family in family_order:
        family_df = plot_df[plot_df["family"] == family]
        if family_df.empty:
            continue

        ax.scatter(
            family_df["cost_cents"],
            family_df["total_score_mean"],
            s=105,
            color=family_colors.get(family, "#4c4c4c"),
            edgecolors="white",
            linewidths=1.1,
            alpha=0.95,
            label=family,
            zorder=3,
        )

    ax.set_title("Compromesso qualità-costo per modello", fontsize=14, pad=16)
    ax.set_xlabel("Costo medio per diagnosi (centesimi di USD, scala log)")
    ax.set_ylabel("Score medio (0–21)")

    ax.set_ylim(0, MAX_SCORE + 0.7)
    ax.set_yticks([0, 3, 6, 9, 12, 15, 18, 21])

    # Scala log: utile perché i costi variano molto tra nano, mini e modello grande.
    ax.set_xscale("log")

    x_min = float(plot_df["cost_cents"].min())
    x_max = float(plot_df["cost_cents"].max())
    ax.set_xlim(x_min * 0.75, x_max * 1.45)

    # Tick leggibili in centesimi.
    candidate_ticks = [0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10]
    visible_ticks = [t for t in candidate_ticks if x_min * 0.75 <= t <= x_max * 1.45]
    if visible_ticks:
        ax.set_xticks(visible_ticks)

    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:g}"))

    # Offset manuali per ridurre sovrapposizioni.
    # dx, dy sono in punti tipografici rispetto al punto.
    label_offsets = {
        "gpt-5.4": (-42, 8),
        "gpt-5.4-mini": (6, 8),
        "gpt-5.4-nano": (6, 7),

        "gpt-5-mini": (6, -14),
        "gpt-5-nano": (6, 7),

        "gpt-4.1-mini": (6, 8),
        "gpt-4.1-nano": (6, -14),

        "gpt-4o-mini": (6, 7),
    }

    for _, row in plot_df.iterrows():
        model = row["model"]
        x = row["cost_cents"]
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
            fontsize=8.3,
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

    ax.legend(
        title="Famiglia modello",
        frameon=True,
        fancybox=True,
        facecolor="white",
        edgecolor="#dddddd",
        framealpha=0.92,
        loc="upper left",
        bbox_to_anchor=(0.02, 0.96),
    )

    # Griglia leggera: utile su scala log.
    ax.grid(axis="y", alpha=0.25)
    ax.grid(axis="x", which="major", alpha=0.18)
    ax.grid(axis="x", which="minor", alpha=0.08)
    ax.set_axisbelow(True)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()
    save_figure(fig, output_dir, basename)

    return basename


# -----------------------------------------------------------------------------
# Figura 9 - Costo medio per modello
# -----------------------------------------------------------------------------

def fig09_costo_medio_per_modello(input_dir: Path, output_dir: Path) -> str:
    """
    Bar chart orizzontale del costo medio del modello per diagnosi.

    File richiesto:
        aggregate_by_model.csv

    Colonne usate:
        model
        model_cost_usd_mean
    """
    basename = "fig09_costo_medio_per_modello"

    df = read_csv(
        input_dir,
        "aggregate_by_model.csv",
        required_columns=["model", "model_cost_usd_mean"],
    )

    plot_df = df[["model", "model_cost_usd_mean"]].copy()
    plot_df["model_cost_usd_mean"] = pd.to_numeric(plot_df["model_cost_usd_mean"], errors="coerce")
    plot_df = plot_df.dropna(subset=["model_cost_usd_mean"])
    plot_df = plot_df.sort_values("model_cost_usd_mean", ascending=True)

    family_colors = {
        "gpt-5.4": "#1f77b4",
        "gpt-5": "#2ca02c",
        "gpt-4.1": "#ff7f0e",
        "gpt-4o": "#9467bd",
    }

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

    colors = [family_colors.get(get_family(model), "#4c4c4c") for model in plot_df["model"]]

    fig, ax = plt.subplots(figsize=(10.6, 5.8))

    ax.barh(plot_df["model"], plot_df["model_cost_usd_mean"], color=colors)

    ax.set_title("Costo medio del modello per diagnosi", fontsize=14, pad=14)
    ax.set_xlabel("Costo medio del modello per diagnosi (USD)")
    ax.set_ylabel("Modello")

    max_cost = float(plot_df["model_cost_usd_mean"].max()) if len(plot_df) else 0.0
    ax.set_xlim(0, max_cost * 1.14 if max_cost > 0 else 0.01)

    for patch in ax.patches:
        width = patch.get_width()
        y = patch.get_y() + patch.get_height() / 2
        ax.text(
            width + max_cost * 0.015,
            y,
            f"{width:.4f}",
            va="center",
            ha="left",
            fontsize=8.5,
        )

    ax.grid(axis="x", alpha=0.25)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()
    save_figure(fig, output_dir, basename)

    return basename



# -----------------------------------------------------------------------------
# Revisioni finali per le figure principali
# -----------------------------------------------------------------------------

FIGURE_CAPTIONS.update(
    {
        "fig01_score_medio_per_modello": (
            "Figura 1 - Score medio per modello sui circuiti analizzati. "
            "Il grafico riporta il punteggio medio assegnato dal judge a ciascun modello, aggregando tutte le run "
            "disponibili e considerando entrambe le modalita di input. I modelli sono ordinati dal migliore al "
            "peggiore rispetto allo score medio. Un valore piu alto indica una migliore capacita diagnostica complessiva."
        ),
        "fig02_score_modello_input_type": (
            "Figura 2 - Effetto dell'immagine per modello. "
            "Il grafico collega, per ciascun modello, lo score medio ottenuto con JSON + datasheet "
            "e con JSON + immagine + datasheet. Lo spostamento verso destra indica un miglioramento "
            "con l'aggiunta dell'immagine; lo spostamento verso sinistra indica un peggioramento. "
            "Le etichette numeriche riportano il delta tra le due modalita, rendendo immediato capire "
            "quali modelli beneficiano dell'informazione visiva e quali no."
        ),
        "fig03_delta_immagine_per_circuito": (
            "Figura 3 - Variazione dello score con l'aggiunta dell'immagine per circuito. "
            "Le barre verdi indicano circuiti in cui JSON + immagine + datasheet migliora lo score medio "
            "rispetto a JSON + datasheet; le barre rosse indicano circuiti in cui l'immagine peggiora la "
            "prestazione media. La linea orizzontale a zero separa i miglioramenti dai peggioramenti e "
            "permette di vedere che l'effetto dell'immagine dipende dal circuito, non e sistematico."
        ),
        "fig04_score_medio_per_circuito": (
            "Figura 4 - Score medio per circuito. "
            "Il grafico ordina i circuiti dal punteggio medio piu alto al piu basso, aggregando tutti i modelli "
            "e le due modalita di input. Un valore alto indica un caso mediamente piu semplice per i modelli; "
            "un valore basso evidenzia un circuito piu critico, con diagnosi meno immediata o maggiore ambiguita."
        ),
        "fig05_heatmap_modello_circuito": (
            "Figura 5 - Robustezza dei modelli sui diversi circuiti. "
            "La heatmap mostra lo score medio ottenuto da ciascun modello su ciascun circuito, aggregando le due "
            "modalita di input. Le righe sono ordinate dal modello con score medio complessivo piu alto a quello "
            "piu basso, mentre le colonne seguono la difficolta media dei circuiti. Il grafico permette di vedere "
            "se un modello e stabile su piu circuiti o se crolla su casi specifici."
        ),
        "fig06_top1_top3_accuracy_modello": (
            "Figura 6 - Accuratezza Top-1 e Top-3 per modello. "
            "Il grafico confronta, per ciascun modello, la percentuale di diagnosi corrette al primo tentativo "
            "(Top-1) e la percentuale di casi in cui la causa corretta compare almeno tra le prime tre ipotesi "
            "(Top-3). Una Top-1 elevata indica maggiore affidabilita nella diagnosi principale; una Top-3 elevata "
            "indica utilita come supporto al troubleshooting anche quando la causa corretta non viene messa al primo posto."
        ),
        "fig07_errori_gravi_medi_per_modello": (
            "Figura 7 - Errori gravi medi per modello. "
            "Il grafico riporta il numero medio di errori gravi commessi da ciascun modello nelle run valutate dal judge. "
            "Valori piu bassi indicano maggiore affidabilita pratica; valori piu alti segnalano un rischio maggiore di "
            "indicazioni diagnostiche scorrette o fuorvianti."
        ),
        "fig08_score_vs_costo": (
            "Figura 8 - Compromesso tra score medio e costo per diagnosi. "
            "Il costo e mostrato in USD reali, senza scala logaritmica. I modelli sono divisi in due pannelli con la "
            "stessa scala verticale: a sinistra la fascia economica, a destra la fascia alta. In questo modo il grafico "
            "mantiene leggibili le differenze tra modelli economici senza nascondere il costo molto piu alto del modello "
            "di fascia superiore."
        ),
        "fig09_costo_medio_per_modello": (
            "Figura 9 - Costo medio del modello per diagnosi. "
            "Il grafico riporta il costo medio stimato del solo modello generativo per ciascuna diagnosi, escludendo "
            "il costo del judge. I modelli sono ordinati dal meno costoso al piu costoso, cosi da rendere immediato "
            "il confronto economico diretto tra le diverse alternative."
        ),
    }
)


def write_captions(output_dir: Path, generated_basenames: list[str]) -> None:
    """
    Scrive tutte le caption principali.

    Anche quando si rigenera una singola figura, il file markdown resta completo.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    md_path = output_dir / "figure_captions.md"

    lines_md = ["# Caption figure principali\n"]

    for basename, caption in FIGURE_CAPTIONS.items():
        lines_md.append(f"## {basename}\n")
        lines_md.append(caption + "\n")

    md_path.write_text("\n".join(lines_md), encoding="utf-8")
    print(f"[OK] Salvato: {md_path}")


def _model_family(model: str) -> str:
    if model.startswith("gpt-5.4"):
        return "gpt-5.4"
    if model.startswith("gpt-5"):
        return "gpt-5"
    if model.startswith("gpt-4.1"):
        return "gpt-4.1"
    if model.startswith("gpt-4o"):
        return "gpt-4o"
    return "Altro"


def _family_colors() -> dict[str, str]:
    return {
        "gpt-5.4": "#1f77b4",
        "gpt-5": "#2ca02c",
        "gpt-4.1": "#ff7f0e",
        "gpt-4o": "#9467bd",
        "Altro": "#4c4c4c",
    }


def fig02_score_modello_input_type(input_dir: Path, output_dir: Path) -> str:
    """
    Dumbbell plot dello score medio per modello e tipo di input.
    """
    basename = "fig02_score_modello_input_type"

    df = read_csv(
        input_dir,
        "aggregate_by_model_input.csv",
        required_columns=["model", "input_type", "total_score_mean"],
    )

    plot_df = df[["model", "input_type", "total_score_mean"]].copy()
    plot_df["total_score_mean"] = pd.to_numeric(plot_df["total_score_mean"], errors="coerce")
    plot_df = plot_df.dropna(subset=["total_score_mean"])

    pivot = plot_df.pivot_table(
        index="model",
        columns="input_type",
        values="total_score_mean",
        aggfunc="mean",
    )

    json_col = "JSON + datasheet"
    img_col = "JSON + immagine + datasheet"
    pivot = pivot.dropna(subset=[json_col, img_col])
    model_order = [m for m in get_model_order(input_dir) if m in set(pivot.index)]
    pivot = pivot.reindex(model_order)

    fig, ax = plt.subplots(figsize=(11.2, 6.3))
    y_positions = list(range(len(pivot.index)))

    for y, (model, row) in zip(y_positions, pivot.iterrows()):
        x_json = float(row[json_col])
        x_img = float(row[img_col])
        delta = x_img - x_json
        line_color = "#2ca02c" if delta >= 0 else "#d62728"
        end_x = max(x_json, x_img)

        ax.plot([x_json, x_img], [y, y], color=line_color, linewidth=3.0, alpha=0.72, zorder=1)
        ax.scatter(x_json, y, s=84, color="#1f77b4", edgecolors="white", linewidths=1.0, zorder=3)
        ax.scatter(x_img, y, s=84, color="#ff7f0e", edgecolors="white", linewidths=1.0, zorder=3)
        ax.text(
            min(end_x + 0.32, MAX_SCORE + 0.25),
            y,
            f"{delta:+.2f}",
            va="center",
            ha="left",
            fontsize=8.8,
            color=line_color,
            fontweight="bold",
        )

    ax.set_title("Effetto dell'immagine per modello", fontsize=14, pad=14)
    ax.set_xlabel("Score medio (0-21)")
    ax.set_ylabel("Modello")
    ax.set_yticks(y_positions)
    ax.set_yticklabels(pivot.index)
    ax.invert_yaxis()
    ax.set_xlim(0, MAX_SCORE + 0.85)
    ax.set_xticks([0, 3, 6, 9, 12, 15, 18, 21])

    legend_handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor="#1f77b4",
               markeredgecolor="white", markersize=9, label="JSON + datasheet"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor="#ff7f0e",
               markeredgecolor="white", markersize=9, label="JSON + immagine + datasheet"),
        Line2D([0], [0], color="#2ca02c", linewidth=3, label="migliora con immagine"),
        Line2D([0], [0], color="#d62728", linewidth=3, label="peggiora con immagine"),
    ]
    ax.legend(
        handles=legend_handles,
        frameon=True,
        facecolor="white",
        edgecolor="#dddddd",
        framealpha=0.94,
        loc="lower right",
    )

    ax.grid(axis="x", alpha=0.22)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()
    save_figure(fig, output_dir, basename)
    return basename


def fig03_delta_immagine_per_circuito(input_dir: Path, output_dir: Path) -> str:
    """
    Bar chart del delta immagine per circuito, con segno evidente.
    """
    basename = "fig03_delta_immagine_per_circuito"

    df = read_csv(
        input_dir,
        "deltas_image_vs_json.csv",
        required_columns=["circuit", "delta_score_img_minus_json"],
    )

    plot_df = df[["circuit", "delta_score_img_minus_json"]].copy()
    plot_df["delta_score_img_minus_json"] = pd.to_numeric(
        plot_df["delta_score_img_minus_json"],
        errors="coerce",
    )
    plot_df = plot_df.dropna(subset=["delta_score_img_minus_json"])
    plot_df = (
        plot_df
        .groupby("circuit", as_index=False)["delta_score_img_minus_json"]
        .mean()
    )

    plot_df = plot_df.sort_values("delta_score_img_minus_json", ascending=False)

    values = plot_df["delta_score_img_minus_json"]
    colors = ["#2ca02c" if value >= 0 else "#d62728" for value in values]

    fig, ax = plt.subplots(figsize=(10.4, 5.7))
    ax.bar(plot_df["circuit"], values, color=colors, width=0.68)
    ax.axhline(0, color="#222222", linewidth=1.0)

    max_abs = max(0.5, float(values.abs().max()))
    ax.set_ylim(-max_abs * 1.35, max_abs * 1.35)
    ax.set_title("Effetto dell'immagine per circuito", fontsize=14, pad=14)
    ax.set_xlabel("Circuito")
    ax.set_ylabel("Delta score (immagine - JSON)")

    ax.tick_params(axis="x", rotation=35)
    for label in ax.get_xticklabels():
        label.set_horizontalalignment("right")

    annotate_delta_bars(ax, digits=2, dy=max_abs * 0.07, fontsize=8.8)

    ax.legend(
        handles=[
            Line2D([0], [0], color="#2ca02c", linewidth=8, label="migliora"),
            Line2D([0], [0], color="#d62728", linewidth=8, label="peggiora"),
        ],
        frameon=True,
        facecolor="white",
        edgecolor="#dddddd",
        framealpha=0.94,
        loc="upper right",
    )
    ax.grid(axis="y", alpha=0.22)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()
    save_figure(fig, output_dir, basename)
    return basename


def fig04_score_medio_per_circuito(input_dir: Path, output_dir: Path) -> str:
    """
    Bar chart dello score medio per circuito.
    """
    basename = "fig04_score_medio_per_circuito"

    df = read_csv(
        input_dir,
        "aggregate_by_circuit.csv",
        required_columns=["circuit", "total_score_mean"],
    )

    plot_df = df[["circuit", "total_score_mean"]].copy()
    plot_df["total_score_mean"] = pd.to_numeric(plot_df["total_score_mean"], errors="coerce")
    plot_df = plot_df.dropna(subset=["total_score_mean"])
    plot_df = plot_df.sort_values("total_score_mean", ascending=False)

    fig, ax = plt.subplots(figsize=(10.4, 5.7))
    ax.bar(plot_df["circuit"], plot_df["total_score_mean"], color="#4c78a8", width=0.68)

    ax.set_title("Score medio per circuito", fontsize=14, pad=14)
    ax.set_xlabel("Circuito")
    ax.set_ylabel("Score medio (0-21)")
    set_common_score_axis(ax)

    ax.tick_params(axis="x", rotation=35)
    for label in ax.get_xticklabels():
        label.set_horizontalalignment("right")

    annotate_bars(ax, digits=2, dy=0.25, fontsize=8.8)
    clean_axes(ax)
    fig.tight_layout()
    save_figure(fig, output_dir, basename)
    return basename


def fig06_top1_top3_accuracy_modello(input_dir: Path, output_dir: Path) -> str:
    """
    Grouped bar chart Top-1 / Top-3 per modello.
    """
    basename = "fig06_top1_top3_accuracy_modello"

    df = read_csv(
        input_dir,
        "aggregate_by_model.csv",
        required_columns=["model", "top1_correct_rate", "top3_contains_correct_rate"],
    )

    plot_df = df[["model", "top1_correct_rate", "top3_contains_correct_rate"]].copy()
    plot_df["top1_correct_rate"] = pd.to_numeric(plot_df["top1_correct_rate"], errors="coerce")
    plot_df["top3_contains_correct_rate"] = pd.to_numeric(
        plot_df["top3_contains_correct_rate"],
        errors="coerce",
    )
    plot_df = plot_df.dropna(subset=["top1_correct_rate", "top3_contains_correct_rate"])

    if plot_df[["top1_correct_rate", "top3_contains_correct_rate"]].max().max() <= 1.0:
        plot_df["top1_correct_rate"] *= 100.0
        plot_df["top3_contains_correct_rate"] *= 100.0

    model_order = [m for m in get_model_order(input_dir) if m in set(plot_df["model"])]
    plot_df = (
        plot_df
        .set_index("model")
        .reindex(model_order)
        .dropna(subset=["top1_correct_rate", "top3_contains_correct_rate"])
    )

    fig, ax = plt.subplots(figsize=(11.5, 6.2))
    x_positions = list(range(len(plot_df.index)))
    width = 0.38

    ax.bar(
        [x - width / 2 for x in x_positions],
        plot_df["top1_correct_rate"],
        width=width,
        color="#1f77b4",
        label="Top-1",
    )
    ax.bar(
        [x + width / 2 for x in x_positions],
        plot_df["top3_contains_correct_rate"],
        width=width,
        color="#ff7f0e",
        label="Top-3",
    )

    ax.set_title("Accuratezza Top-1 e Top-3 per modello", fontsize=14, pad=14)
    ax.set_xlabel("Modello")
    ax.set_ylabel("Accuracy (%)")
    ax.set_ylim(0, 108)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.set_xticks(x_positions)
    ax.set_xticklabels(plot_df.index)
    ax.tick_params(axis="x", rotation=35)
    for label in ax.get_xticklabels():
        label.set_horizontalalignment("right")

    annotate_bars(ax, digits=1, dy=1.6, fontsize=8)
    ax.legend(
        frameon=True,
        facecolor="white",
        edgecolor="#dddddd",
        framealpha=0.94,
        loc="upper right",
    )

    ax.grid(axis="y", alpha=0.22)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()
    save_figure(fig, output_dir, basename)
    return basename


def fig08_score_vs_costo(input_dir: Path, output_dir: Path) -> str:
    """
    Scatter plot score-costo con costo reale in USD diviso per fascia.
    """
    basename = "fig08_score_vs_costo"

    df = read_csv(
        input_dir,
        "aggregate_by_model.csv",
        required_columns=["model", "model_cost_usd_mean", "total_score_mean"],
    )

    plot_df = df[["model", "model_cost_usd_mean", "total_score_mean"]].copy()
    plot_df["model_cost_usd_mean"] = pd.to_numeric(plot_df["model_cost_usd_mean"], errors="coerce")
    plot_df["total_score_mean"] = pd.to_numeric(plot_df["total_score_mean"], errors="coerce")
    plot_df = plot_df.dropna(subset=["model_cost_usd_mean", "total_score_mean"])
    plot_df = plot_df[plot_df["model_cost_usd_mean"] > 0].copy()
    plot_df["family"] = plot_df["model"].map(_model_family)

    colors = _family_colors()
    low_max = 0.022
    high_min = 0.060
    low_df = plot_df[plot_df["model_cost_usd_mean"] <= low_max].copy()
    high_df = plot_df[plot_df["model_cost_usd_mean"] > low_max].copy()

    fig, (ax_low, ax_high) = plt.subplots(
        1,
        2,
        sharey=True,
        figsize=(12.0, 6.2),
        gridspec_kw={"width_ratios": [3.1, 1.25], "wspace": 0.16},
    )

    for ax, subset_all in ((ax_low, low_df), (ax_high, high_df)):
        for family, color in colors.items():
            subset = subset_all[subset_all["family"] == family]
            if subset.empty:
                continue
            ax.scatter(
                subset["model_cost_usd_mean"],
                subset["total_score_mean"],
                s=105,
                color=color,
                edgecolors="white",
                linewidths=1.1,
                alpha=0.96,
                label=family,
                zorder=3,
            )

        ax.set_ylim(0, MAX_SCORE + 0.8)
        ax.set_yticks([0, 3, 6, 9, 12, 15, 18, 21])
        ax.grid(axis="y", alpha=0.22)
        ax.grid(axis="x", alpha=0.16)
        ax.set_axisbelow(True)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    ax_low.set_xlim(0, max(0.020, float(low_df["model_cost_usd_mean"].max()) * 1.18))
    ax_high.set_xlim(
        max(0.0, float(high_df["model_cost_usd_mean"].min()) * 0.93),
        float(high_df["model_cost_usd_mean"].max()) * 1.08,
    )
    ax_high.tick_params(axis="y", left=False, labelleft=False)

    ax_low.set_xticks([0, 0.005, 0.010, 0.015, 0.020])
    ax_high.set_xticks([0.070, 0.075])
    ax_low.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.3f}"))
    ax_high.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.3f}"))

    fig.suptitle("Compromesso score-costo per modello", fontsize=14, y=0.98)
    fig.supxlabel("Costo medio per diagnosi (USD)")
    ax_low.set_ylabel("Score medio (0-21)")
    ax_low.set_title("Fascia economica", fontsize=11, pad=9)
    ax_high.set_title("Fascia alta", fontsize=11, pad=9)

    label_offsets = {
        "gpt-5.4": (7, 7),
        "gpt-5.4-mini": (-18, 10),
        "gpt-5.4-nano": (7, 7),
        "gpt-5-mini": (7, 10),
        "gpt-5-nano": (7, 7),
        "gpt-4.1-mini": (-10, -20),
        "gpt-4.1-nano": (7, -14),
        "gpt-4o-mini": (7, 7),
    }

    for _, row in plot_df.iterrows():
        ax = ax_low if row["model_cost_usd_mean"] <= low_max else ax_high
        dx, dy = label_offsets.get(row["model"], (7, 7))
        ha = "right" if dx < 0 else "left"
        va = "top" if dy < 0 else "bottom"

        ax.annotate(
            row["model"],
            (row["model_cost_usd_mean"], row["total_score_mean"]),
            textcoords="offset points",
            xytext=(dx, dy),
            ha=ha,
            va=va,
            fontsize=8.2,
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

    handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=color,
               markeredgecolor="white", markersize=9, label=family)
        for family, color in colors.items()
        if family in set(plot_df["family"])
    ]
    ax_low.legend(
        handles=handles,
        title="Famiglia modello",
        frameon=True,
        facecolor="white",
        edgecolor="#dddddd",
        framealpha=0.94,
        loc="lower right",
    )

    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.16, top=0.88, wspace=0.05)
    save_figure(fig, output_dir, basename)
    return basename


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genera i grafici principali della tesi dai CSV aggregati."
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
        help="Cartella di output delle figure. Default: <input-dir>/figures_main.",
    )
    parser.add_argument(
        "--fig",
        choices=["all", "fig01", "fig02", "fig03", "fig04", "fig05", "fig06", "fig07", "fig08", "fig09"],
        default="all",
        help="Quale figura generare: all, fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08 oppure fig09.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_dir = args.input_dir.resolve()
    output_dir = args.output_dir.resolve() if args.output_dir else input_dir / "figures_main"

    generated_basenames: list[str] = []

    if args.fig in ("all", "fig01"):
        generated_basenames.append(fig01_score_medio_per_modello(input_dir, output_dir))

    if args.fig in ("all", "fig02"):
        generated_basenames.append(fig02_score_modello_input_type(input_dir, output_dir))

    if args.fig in ("all", "fig03"):
        generated_basenames.append(fig03_delta_immagine_per_circuito(input_dir, output_dir))

    if args.fig in ("all", "fig04"):
        generated_basenames.append(fig04_score_medio_per_circuito(input_dir, output_dir))

    if args.fig in ("all", "fig05"):
        generated_basenames.append(fig05_heatmap_modello_circuito(input_dir, output_dir))

    if args.fig in ("all", "fig06"):
        generated_basenames.append(fig06_top1_top3_accuracy_modello(input_dir, output_dir))

    if args.fig in ("all", "fig07"):
        generated_basenames.append(fig07_errori_gravi_medi_per_modello(input_dir, output_dir))

    if args.fig in ("all", "fig08"):
        generated_basenames.append(fig08_score_vs_costo(input_dir, output_dir))

    if args.fig in ("all", "fig09"):
        generated_basenames.append(fig09_costo_medio_per_modello(input_dir, output_dir))

    write_captions(output_dir, generated_basenames)

    print("\nGenerazione grafici completata.")
    print(f"Input dir:  {input_dir}")
    print(f"Output dir: {output_dir}")


if __name__ == "__main__":
    main()
