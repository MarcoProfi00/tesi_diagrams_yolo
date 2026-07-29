#!/usr/bin/env python3
"""Genera la figura temporale usata nel caso qualitativo c02.

La figura legge direttamente il CSV transitorio della run base e mostra
soltanto le correnti dei due LED, così da rendere visibile la loro relazione
temporale senza il rumore delle altre grandezze circuitali.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


SCRIPT_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = SCRIPT_DIR.parents[1]
DEFAULT_CSV = (
    REPOSITORY_ROOT
    / "outputs"
    / "demo_workspaces"
    / "chat_agent_evaluation"
    / "web"
    / "chat"
    / "c02"
    / "08_tran.csv"
)
DEFAULT_OUTPUT = (
    SCRIPT_DIR
    / "_aggregate"
    / "figures"
    / "fig08_c02_base_led_currents.png"
)

LED_1_COLUMN = "@dled12_1[id]"
LED_2_COLUMN = "@dled12_2[id]"
CHAT_COLOR = "#356E9F"
AGENT_COLOR = "#D9822B"
TEXT_COLOR = "#202832"
GRID_COLOR = "#DCE2E7"
STARTUP_COLOR = "#EEF2F5"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genera il grafico delle correnti LED della run base c02."
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=DEFAULT_CSV,
        help="CSV transitorio da leggere.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="File PNG da generare.",
    )
    return parser.parse_args()


def read_transient(path: Path) -> tuple[list[float], list[float], list[float]]:
    if not path.is_file():
        raise FileNotFoundError(f"CSV transitorio non trovato: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"time", LED_1_COLUMN, LED_2_COLUMN}
        available = set(reader.fieldnames or ())
        if not required.issubset(available):
            missing = ", ".join(sorted(required - available))
            raise ValueError(f"Colonne mancanti nel CSV: {missing}")

        time_s: list[float] = []
        led_1_ma: list[float] = []
        led_2_ma: list[float] = []
        for row in reader:
            time_s.append(float(row["time"]))
            led_1_ma.append(1000.0 * float(row[LED_1_COLUMN]))
            led_2_ma.append(1000.0 * float(row[LED_2_COLUMN]))

    if not time_s:
        raise ValueError(f"Il CSV non contiene campioni: {path}")
    return time_s, led_1_ma, led_2_ma


def make_figure(
    time_s: list[float],
    led_1_ma: list[float],
    led_2_ma: list[float],
    output: Path,
) -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 11,
            "axes.labelcolor": TEXT_COLOR,
            "axes.edgecolor": TEXT_COLOR,
            "xtick.color": TEXT_COLOR,
            "ytick.color": TEXT_COLOR,
            "text.color": TEXT_COLOR,
        }
    )

    figure, axis = plt.subplots(figsize=(12.4, 5.8), facecolor="white")
    axis.set_facecolor("white")

    axis.axvspan(
        0.0,
        0.05,
        color=STARTUP_COLOR,
        alpha=1.0,
        zorder=0,
        label="Symmetric start-up",
    )
    axis.plot(
        time_s,
        led_1_ma,
        color=CHAT_COLOR,
        linewidth=2.0,
        label="LED 1 current",
        zorder=3,
    )
    axis.plot(
        time_s,
        led_2_ma,
        color=AGENT_COLOR,
        linewidth=2.0,
        label="LED 2 current",
        zorder=2,
    )

    maximum_current = max(max(led_1_ma), max(led_2_ma))
    axis.set_xlim(min(time_s), max(time_s))
    axis.set_ylim(-0.45, maximum_current * 1.12)
    axis.set_xlabel("Time [s]", labelpad=9)
    axis.set_ylabel("LED current [mA]", labelpad=9)
    axis.set_title(
        "c02 — Base transient: alternating LED currents",
        fontsize=16,
        fontweight="semibold",
        loc="center",
        pad=17,
    )

    axis.grid(True, which="major", color=GRID_COLOR, linewidth=0.8, alpha=0.9)
    axis.set_axisbelow(True)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)

    legend = axis.legend(
        loc="upper right",
        ncols=3,
        frameon=True,
        borderpad=0.7,
        handlelength=2.5,
    )
    legend.get_frame().set_edgecolor(GRID_COLOR)
    legend.get_frame().set_linewidth(0.8)
    legend.get_frame().set_facecolor("white")
    legend.get_frame().set_alpha(0.96)

    output.parent.mkdir(parents=True, exist_ok=True)
    figure.tight_layout()
    figure.savefig(output, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(figure)


def main() -> None:
    args = parse_args()
    time_s, led_1_ma, led_2_ma = read_transient(args.csv.resolve())
    make_figure(time_s, led_1_ma, led_2_ma, args.output.resolve())
    print(f"Figura generata: {args.output.resolve()}")


if __name__ == "__main__":
    main()
