"""
Funzioni di input/output della pipeline 2.0.

Questo modulo gestisce lettura e scrittura dei file usati dalla nuova pipeline:

- Graph JSON in input dalla pipeline_1.0;
- values.yaml;
- device_profiles.yaml;
- node_map.json;
- conversion_report.json;
- missing_parameters.json;
- spice_netlist.cir;
- spice_results.json;
- electrical_check_report.json;
- diagnostic_context.json.

L'obiettivo e centralizzare i percorsi, il caricamento e il salvataggio degli
artefatti, evitando che ogni modulo gestisca i file in modo diverso.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PIPELINE1_ROOT = PROJECT_ROOT / "outputs" / "pipeline1.0"
PIPELINE2_ROOT = PROJECT_ROOT / "outputs" / "pipeline2.0"


def ensure_dir(path: str | Path) -> Path:
    """Crea una directory se non esiste e restituisce il Path normalizzato."""
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def load_json(path: str | Path) -> dict[str, Any]:
    """Legge un file JSON e restituisce un dizionario."""
    json_path = Path(path)
    if not json_path.exists():
        raise FileNotFoundError(f"JSON non trovato: {json_path}")
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Il JSON deve contenere un oggetto alla radice: {json_path}")
    return data


def write_json(path: str | Path, data: Any) -> Path:
    """Scrive un oggetto Python in JSON formattato."""
    json_path = Path(path)
    ensure_dir(json_path.parent)
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return json_path


def resolve_pipeline1_graph_json(batch_name: str, circuit_id: str) -> Path:
    """
    Restituisce il path del Graph JSON finale prodotto dal passo 06.

    Esempio:
    outputs/pipeline1.0/batchA/06_graph_report/a01/a01.json
    """
    return (
        PIPELINE1_ROOT
        / batch_name
        / "06_graph_report"
        / circuit_id
        / f"{circuit_id}.json"
    )


def resolve_pipeline2_circuit_dir(batch_name: str, circuit_id: str) -> Path:
    """
    Restituisce la cartella output della pipeline 2.0 per un circuito.

    Esempio:
    outputs/pipeline2.0/batchA/a01
    """
    return PIPELINE2_ROOT / batch_name / circuit_id


def copy_source_graph(input_path: str | Path, output_dir: str | Path) -> Path:
    """
    Copia il Graph JSON sorgente nella cartella della pipeline 2.0.

    La copia viene chiamata 01_graph.json per mantenere allineato il nome
    dell'output allo step che lo produce nella pipeline 2.0.
    """
    source = Path(input_path)
    if not source.exists():
        raise FileNotFoundError(f"Graph JSON sorgente non trovato: {source}")

    destination_dir = ensure_dir(output_dir)
    destination = destination_dir / "01_graph.json"
    shutil.copy2(source, destination)
    return destination


def prepare_circuit_output(batch_name: str, circuit_id: str) -> Path:
    """Crea e restituisce la cartella output per un circuito."""
    return ensure_dir(resolve_pipeline2_circuit_dir(batch_name, circuit_id))
