"""
Esecuzione opzionale di ngspice.

Questo modulo lancia ngspice sulle netlist generate quando il circuito e
simulabile e il simulatore e disponibile nel sistema.

La pipeline non deve fallire se ngspice manca o se la simulazione non converge.
In questi casi deve produrre un risultato strutturato con lo stato dell'errore.

Responsabilita previste:

- verificare disponibilita di ngspice;
- eseguire netlist in batch mode;
- raccogliere log, errori e codice di uscita;
- estrarre risultati .op, .tran o .measure quando disponibili;
- salvare spice_results.json.
"""

from __future__ import annotations

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
        "message": message,
    }


def write_text(path: str | Path, text: str) -> Path:
    """Scrive un file di testo creando la cartella padre se necessario."""
    text_path = Path(path)
    text_path.parent.mkdir(parents=True, exist_ok=True)
    text_path.write_text(text, encoding="utf-8")
    return text_path


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

    command = [ngspice_path, "-b", str(netlist_path)]

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

    status = "success" if completed.returncode == 0 else "failed"
    return build_report(
        status=status,
        netlist_path=netlist_path,
        command=command,
        exit_code=completed.returncode,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        message="ngspice completed successfully." if status == "success" else "ngspice exited with errors.",
    )
