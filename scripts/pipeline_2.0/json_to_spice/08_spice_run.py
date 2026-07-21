"""
Esecuzione opzionale di ngspice.

Questo modulo lancia ngspice sulle netlist generate quando il circuito e
simulabile e il simulatore e disponibile nel sistema.

La pipeline non deve fallire se ngspice manca o se la simulazione non converge.
In questi casi deve produrre un risultato strutturato con lo stato dell'errore.

Responsabilita:

- verificare disponibilita di ngspice;
- eseguire netlist in batch mode;
- raccogliere log, errori e codice di uscita;
- pulire l'eventuale CSV transitorio e generare il grafico disponibile;
- restituire il report poi salvato come `08_spice_run.json`.
"""

from __future__ import annotations

import csv
import html
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


NGSPICE_CANDIDATES = (
    "ngspice_con",
    "ngspice_con.exe",
    "ngspice",
    "ngspice.exe",
)


def find_ngspice_executable(executable: str | None = None) -> str | None:
    """
    Trova l'eseguibile ngspice da usare.

    Su Windows la versione console spesso si chiama ngspice_con.exe, mentre su
    Linux/Mac di solito basta ngspice. Se l'utente passa un path esplicito,
    proviamo prima quello.
    """
    candidates = (executable,) if executable else NGSPICE_CANDIDATES
    for candidate in candidates:
        if not candidate:
            continue
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
        candidate_path = Path(candidate)
        if candidate_path.exists():
            return str(candidate_path)
    return None


def build_report(
    status: str,
    netlist_path: Path,
    command: list[str] | None = None,
    exit_code: int | None = None,
    stdout_path: Path | None = None,
    stderr_path: Path | None = None,
    tran_raw_csv_path: Path | None = None,
    tran_csv_path: Path | None = None,
    tran_plot_path: Path | None = None,
    tran_plot_png_path: Path | None = None,
    tran_plot_svg_path: Path | None = None,
    message: str | None = None,
) -> dict[str, Any]:
    """Costruisce il report JSON dello step 08 con messaggi in inglese."""
    return {
        "source_format": "pipeline2.0_spice_run",
        "status": status,
        "netlist_path": str(netlist_path),
        "command": command,
        "exit_code": exit_code,
        "stdout_path": str(stdout_path) if stdout_path else None,
        "stderr_path": str(stderr_path) if stderr_path else None,
        "tran_raw_csv_path": str(tran_raw_csv_path) if tran_raw_csv_path else None,
        "tran_csv_path": str(tran_csv_path) if tran_csv_path else None,
        "tran_plot_path": str(tran_plot_path) if tran_plot_path else None,
        "tran_plot_png_path": str(tran_plot_png_path) if tran_plot_png_path else None,
        "tran_plot_svg_path": str(tran_plot_svg_path) if tran_plot_svg_path else None,
        "message": message,
    }


def write_text(path: str | Path, text: str) -> Path:
    """Scrive un file di testo creando la cartella padre se necessario."""
    text_path = Path(path)
    text_path.parent.mkdir(parents=True, exist_ok=True)
    text_path.write_text(text, encoding="utf-8")
    return text_path


def split_data_line(line: str) -> list[str]:
    """Divide una riga dati gestendo sia CSV puliti sia output wrdata."""
    if "," in line:
        return [part.strip() for part in line.split(",")]
    return line.split()


def parse_tran_csv(path: str | Path) -> tuple[list[str], list[float], dict[str, list[float]]]:
    """Legge dati transient da CSV pulito o da wrdata ngspice."""
    csv_path = Path(path)
    lines = [line.strip() for line in csv_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(lines) < 2:
        return [], [], {}

    headers = split_data_line(lines[0])
    value_indices: list[int] = []
    value_names: list[str] = []
    seen_time = False
    for index, name in enumerate(headers):
        if name.lower() == "time":
            if not seen_time:
                seen_time = True
            continue
        value_indices.append(index)
        value_names.append(name)

    times: list[float] = []
    series: dict[str, list[float]] = {name: [] for name in value_names}

    for line in lines[1:]:
        parts = split_data_line(line)
        if len(parts) < len(headers):
            continue
        try:
            times.append(float(parts[0]))
            for name, index in zip(value_names, value_indices):
                series[name].append(float(parts[index]))
        except ValueError:
            continue

    return value_names, times, series


def write_clean_tran_csv(raw_csv_path: str | Path, clean_csv_path: str | Path) -> Path | None:
    """Scrive un CSV pulito con una sola colonna time e separatore virgola."""
    names, times, series = parse_tran_csv(raw_csv_path)
    if not times or not names:
        return None

    output_path = Path(clean_csv_path)
    with output_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["time", *names])
        for row_index, time_value in enumerate(times):
            writer.writerow([time_value, *[series[name][row_index] for name in names]])
    return output_path


def voltage_series_names(names: list[str]) -> list[str]:
    """Seleziona le sole tensioni per il grafico, lasciando le correnti nel CSV."""
    selected = [name for name in names if re.fullmatch(r"v\(.+\)", name, flags=re.IGNORECASE)]
    # Compatibilita' con vecchi CSV che non riportano la forma `v(NODO)`.
    return selected or names


def write_tran_png(csv_path: str | Path, plot_path: str | Path) -> Path | None:
    """Crea un grafico PNG con matplotlib se disponibile."""
    names, times, series = parse_tran_csv(csv_path)
    if not times or not names:
        return None

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    plotted_names = voltage_series_names(names)
    figure, axis = plt.subplots(figsize=(11, 6.2), dpi=140)
    for name in plotted_names:
        axis.plot(times, series[name], linewidth=1.8, label=name)

    axis.set_title("Transient analysis")
    axis.set_xlabel("time [s]")
    axis.set_ylabel("voltage [V]")
    axis.grid(True, which="both", linewidth=0.5, alpha=0.35)
    axis.legend(loc="best")
    figure.tight_layout()

    output_path = Path(plot_path)
    figure.savefig(output_path)
    plt.close(figure)
    return output_path


def points_to_polyline(
    times: list[float],
    values: list[float],
    min_time: float,
    max_time: float,
    min_value: float,
    max_value: float,
    width: int,
    height: int,
    margin: int,
) -> str:
    """Converte una serie numerica in punti SVG."""
    time_span = max(max_time - min_time, 1e-12)
    value_span = max(max_value - min_value, 1e-12)
    points: list[str] = []

    for time_value, y_value in zip(times, values):
        x = margin + ((time_value - min_time) / time_span) * (width - 2 * margin)
        y = height - margin - ((y_value - min_value) / value_span) * (height - 2 * margin)
        points.append(f"{x:.2f},{y:.2f}")

    return " ".join(points)


def write_tran_plot(csv_path: str | Path, plot_path: str | Path) -> Path | None:
    """Crea un grafico SVG minimale dai dati transitori esportati."""
    names, times, series = parse_tran_csv(csv_path)
    if not times or not names:
        return None

    plotted_names = voltage_series_names(names)
    all_values = [value for name in plotted_names for value in series.get(name, [])]
    if not all_values:
        return None

    width = 1100
    height = 620
    margin = 70
    min_time = min(times)
    max_time = max(times)
    min_value = min(all_values)
    max_value = max(all_values)
    if min_value == max_value:
        min_value -= 1
        max_value += 1

    colors = ["#0f766e", "#b45309", "#2563eb", "#be123c", "#4d7c0f", "#7c3aed"]
    polylines: list[str] = []
    legend: list[str] = []

    for index, name in enumerate(plotted_names):
        color = colors[index % len(colors)]
        polyline = points_to_polyline(
            times,
            series[name],
            min_time,
            max_time,
            min_value,
            max_value,
            width,
            height,
            margin,
        )
        polylines.append(
            f'<polyline points="{polyline}" fill="none" stroke="{color}" stroke-width="2" />'
        )
        legend_y = 34 + index * 24
        legend.append(
            f'<text x="880" y="{legend_y}" fill="{color}" font-size="16">{html.escape(name)}</text>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="#f8fafc"/>
  <text x="{margin}" y="36" fill="#0f172a" font-size="22" font-family="Verdana">Transient analysis</text>
  <line x1="{margin}" y1="{height - margin}" x2="{width - margin}" y2="{height - margin}" stroke="#334155" stroke-width="1"/>
  <line x1="{margin}" y1="{margin}" x2="{margin}" y2="{height - margin}" stroke="#334155" stroke-width="1"/>
  <text x="{margin}" y="{height - 24}" fill="#334155" font-size="14" font-family="Verdana">time: {min_time:.6g}s to {max_time:.6g}s</text>
  <text x="{margin}" y="{margin - 16}" fill="#334155" font-size="14" font-family="Verdana">voltage: {min_value:.6g}V to {max_value:.6g}V</text>
  {''.join(polylines)}
  {''.join(legend)}
</svg>
'''
    return write_text(plot_path, svg)


def run_ngspice(
    output_dir: str | Path,
    netlist_filename: str = "07_netlist.cir",
    executable: str | None = None,
    timeout_seconds: int = 30,
) -> dict[str, Any]:
    """
    Esegue ngspice in batch mode su una netlist gia generata.

    Questo modulo non interpreta gli errori: salva solo esito, log e codice di
    uscita. L'interpretazione resta responsabilita dello step 09.
    """
    circuit_dir = Path(output_dir)
    netlist_path = circuit_dir / netlist_filename
    stdout_path = circuit_dir / "08_ngspice_stdout.txt"
    stderr_path = circuit_dir / "08_ngspice_stderr.txt"
    tran_csv_path = circuit_dir / "08_tran.csv"
    tran_raw_csv_path = circuit_dir / "08_tran_raw.csv"
    tran_clean_csv_path = circuit_dir / "08_tran.csv"
    tran_png_path = circuit_dir / "08_tran_plot.png"
    tran_plot_path = circuit_dir / "08_tran_plot.svg"

    if not netlist_path.exists():
        return build_report(
            status="netlist_not_found",
            netlist_path=netlist_path,
            message="Netlist file not found.",
        )

    ngspice_path = find_ngspice_executable(executable)
    if ngspice_path is None:
        return build_report(
            status="ngspice_not_found",
            netlist_path=netlist_path,
            message="ngspice executable not found in PATH.",
        )

    # ngspice viene eseguito con cwd nella cartella del circuito, quindi gli
    # passiamo solo il nome della netlist. In questo modo funziona sia con
    # output_dir assoluti sia con output_dir relativi.
    command = [ngspice_path, "-b", netlist_path.name]

    try:
        # Lo step 08 registra il risultato grezzo, senza correggere il circuito.
        completed = subprocess.run(
            command,
            cwd=str(circuit_dir),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        write_text(stdout_path, exc.stdout or "")
        write_text(stderr_path, exc.stderr or "")
        return build_report(
            status="timeout",
            netlist_path=netlist_path,
            command=command,
            stdout_path=stdout_path,
            stderr_path=stderr_path,
            message="ngspice execution timed out.",
        )

    write_text(stdout_path, completed.stdout)
    write_text(stderr_path, completed.stderr)
    generated_png_path = None
    generated_svg_path = None
    cleaned_csv_path = None
    if tran_csv_path.exists():
        shutil.copyfile(tran_csv_path, tran_raw_csv_path)
        cleaned_csv_path = write_clean_tran_csv(tran_raw_csv_path, tran_clean_csv_path)
        plot_source_path = cleaned_csv_path or tran_raw_csv_path
        generated_png_path = write_tran_png(plot_source_path, tran_png_path)
        if generated_png_path is not None and tran_plot_path.exists():
            tran_plot_path.unlink()
        if generated_png_path is None:
            generated_svg_path = write_tran_plot(plot_source_path, tran_plot_path)

    status = "success" if completed.returncode == 0 else "failed"
    return build_report(
        status=status,
        netlist_path=netlist_path,
        command=command,
        exit_code=completed.returncode,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        tran_raw_csv_path=tran_raw_csv_path if tran_raw_csv_path.exists() else None,
        tran_csv_path=cleaned_csv_path,
        tran_plot_path=generated_png_path or generated_svg_path,
        tran_plot_png_path=generated_png_path,
        tran_plot_svg_path=generated_svg_path,
        message="ngspice completed successfully." if status == "success" else "ngspice exited with errors.",
    )
