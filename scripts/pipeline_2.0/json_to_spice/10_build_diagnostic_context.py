"""
Costruzione del manifest diagnostico per l'agente.

Questo modulo crea un file leggero che indica all'agente dove trovare gli
output reali della Pipeline 2.0.

Lo step 10 non duplica Graph JSON, node map, netlist, stdout o stderr dentro un
unico file enorme. Mantiene invece una mappa ordinata dei file prodotti dagli
step 01-08, con un piccolo riepilogo tecnico e alcune regole operative.

Responsabilita:

- elencare gli artefatti disponibili e mancanti;
- indicare il ruolo di ogni file nella diagnosi;
- salvare uno stato minimo di SPICE e della netlist;
- dichiarare la policy sull'immagine originale;
- preparare un manifest semplice per lo step 11/agente read-only.

L'output principale e 10_diagnostic_context.json.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ARTIFACTS = {
    "graph": {
        "step": "01",
        "filename": "01_graph.json",
        "role": "Graph JSON copied from Pipeline 1.0.",
    },
    "normalized_circuit": {
        "step": "02",
        "filename": "02_normalized_circuit.json",
        "role": "Normalized circuit representation used by Pipeline 2.0.",
    },
    "node_map": {
        "step": "03",
        "filename": "03_node_map.json",
        "role": "Maps component terminals to SPICE node names.",
    },
    "values_bound": {
        "step": "04",
        "filename": "04_values_bound.json",
        "role": "Values and labels bound to graph components.",
    },
    "component_rules": {
        "step": "06",
        "filename": "06_component_rules.json",
        "role": "SPICE conversion rules for each component.",
    },
    "netlist": {
        "step": "07",
        "filename": "07_netlist.cir",
        "role": "Generated SPICE netlist.",
    },
    "spice_emit_report": {
        "step": "07",
        "filename": "07_spice_emit_report.json",
        "role": "Report of emitted, skipped and warning components.",
    },
    "spice_run": {
        "step": "08",
        "filename": "08_spice_run.json",
        "role": "Structured ngspice execution report.",
    },
    "ngspice_stdout": {
        "step": "08",
        "filename": "08_ngspice_stdout.txt",
        "role": "Raw ngspice stdout log.",
    },
    "ngspice_stderr": {
        "step": "08",
        "filename": "08_ngspice_stderr.txt",
        "role": "Raw ngspice stderr log.",
    },
    "tran_csv": {
        "step": "08",
        "filename": "08_tran.csv",
        "role": "Clean transient CSV, when .tran data is available.",
    },
    "tran_plot_png": {
        "step": "08",
        "filename": "08_tran_plot.png",
        "role": "Transient plot PNG, when generated.",
    },
    "tran_plot_svg": {
        "step": "08",
        "filename": "08_tran_plot.svg",
        "role": "Transient plot SVG fallback, when generated.",
    },
}


def read_json_safe(path: Path) -> dict[str, Any]:
    """Legge un JSON se esiste e se e valido, altrimenti restituisce {}."""
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def relative_or_absolute(path: Path, project_root: Path | None = None) -> str:
    """Restituisce un path relativo al progetto quando possibile."""
    if project_root is None:
        return str(path)
    try:
        return str(path.relative_to(project_root))
    except ValueError:
        return str(path)


def build_artifact_manifest(
    output_dir: Path,
    project_root: Path | None = None,
) -> dict[str, Any]:
    """Crea la lista degli artefatti disponibili per il circuito."""
    artifacts: dict[str, Any] = {}

    for key, metadata in ARTIFACTS.items():
        path = output_dir / str(metadata["filename"])
        artifacts[key] = {
            "step": metadata["step"],
            "available": path.exists(),
            "path": relative_or_absolute(path, project_root) if path.exists() else None,
            "role": metadata["role"],
        }

    return artifacts


def find_image_path(
    project_root: Path | None,
    batch_name: str,
    circuit_id: str,
) -> Path | None:
    """Trova l'immagine originale senza includerla nel manifest."""
    if project_root is None:
        return None

    image_dir = project_root / "data" / batch_name
    for extension in (".jpg", ".jpeg", ".png", ".bmp"):
        candidate = image_dir / f"{circuit_id}{extension}"
        if candidate.exists():
            return candidate
    return None


def build_image_access(
    project_root: Path | None,
    batch_name: str,
    circuit_id: str,
) -> dict[str, Any]:
    """Definisce quando l'agente puo richiedere l'immagine originale."""
    image_path = find_image_path(project_root, batch_name, circuit_id)
    return {
        "included_by_default": False,
        "can_be_requested": image_path is not None,
        "path": relative_or_absolute(image_path, project_root) if image_path else None,
        "policy": (
            "Only request the image if structured outputs suggest that the "
            "Graph JSON may be incomplete or wrong."
        ),
    }


def build_summary(output_dir: Path) -> dict[str, Any]:
    """Estrae un riepilogo minimo senza duplicare i file completi."""
    node_map = read_json_safe(output_dir / "03_node_map.json")
    values_bound = read_json_safe(output_dir / "04_values_bound.json")
    component_rules = read_json_safe(output_dir / "06_component_rules.json")
    emit_report = read_json_safe(output_dir / "07_spice_emit_report.json")
    spice_run = read_json_safe(output_dir / "08_spice_run.json")

    return {
        "spice_status": spice_run.get("status"),
        "spice_exit_code": spice_run.get("exit_code"),
        "spice_message": spice_run.get("message"),
        "emitted_elements": emit_report.get("emitted_elements"),
        "skipped_elements": emit_report.get("skipped_elements"),
        "emit_warnings_count": len(emit_report.get("warnings") or []),
        "skipped_components_count": len(emit_report.get("skipped_components") or []),
        "node_count": (node_map.get("stats") or {}).get("nodes_count"),
        "ground_groups_count": (node_map.get("stats") or {}).get("ground_groups_count"),
        "singleton_nodes_count": (node_map.get("stats") or {}).get("singleton_nodes_count"),
        "bound_components": (values_bound.get("stats") or {}).get("bound_components"),
        "missing_components": (values_bound.get("stats") or {}).get("missing_components"),
        "unsupported_components": (values_bound.get("stats") or {}).get("unsupported_components"),
        "spice_ready_components": (component_rules.get("stats") or {}).get("spice_ready_components"),
        "rules_missing_components": (component_rules.get("stats") or {}).get("missing_components"),
        "has_tran_csv": (output_dir / "08_tran.csv").exists(),
        "has_tran_plot": (output_dir / "08_tran_plot.png").exists() or (output_dir / "08_tran_plot.svg").exists(),
    }


def build_agent_rules() -> list[str]:
    """Regole semplici per lo step 11/agente."""
    return [
        "Treat this file as a manifest, not as the full diagnostic evidence.",
        "Load the referenced artifacts needed for the answer.",
        "Use graph, node map, component rules, netlist, stdout and stderr as evidence.",
        "Do not invent values, connections, models or simulation results.",
        "Do not use the image unless image_access is explicitly requested.",
        "If Graph JSON inconsistency is suspected, explain which structured outputs suggest it.",
        "In read-only mode, do not modify netlists and do not execute scenarios.",
    ]


def build_diagnostic_context(
    output_dir: str | Path,
    batch_name: str,
    circuit_id: str,
    project_root: str | Path | None = None,
    user_problem: str | None = None,
) -> dict[str, Any]:
    """
    Costruisce il manifest diagnostico leggero.

    Il manifest indica dove sono gli output veri. Lo step 11 decidera quali file
    caricare per costruire il prompt dell'agente.
    """
    circuit_dir = Path(output_dir)
    root = Path(project_root) if project_root is not None else None

    return {
        "source_format": "pipeline2.0_diagnostic_context_manifest",
        "batch_name": batch_name,
        "circuit_id": circuit_id,
        "user_problem": user_problem,
        "pipeline2_output_dir": relative_or_absolute(circuit_dir, root),
        "summary": build_summary(circuit_dir),
        "artifacts": build_artifact_manifest(circuit_dir, root),
        "image_access": build_image_access(root, batch_name, circuit_id),
        "agent_mode": "graph_grounded_readonly",
        "agent_rules": build_agent_rules(),
    }
