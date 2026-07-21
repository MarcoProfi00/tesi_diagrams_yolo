"""
Costruzione del preview di input per l'agente read-only.

Questo modulo contiene la prima logica concreta dello step 11:

- leggere 10_diagnostic_context.json;
- risolvere i path degli artefatti indicati dal manifest;
- caricare i file principali prodotti dagli step 01-08;
- creare un Markdown ordinato per controllare cosa ricevera l'agente.

Il modulo non chiama API esterne, non esegue ngspice, non modifica netlist e non
applica scenari. Serve solo a preparare un input leggibile e verificabile.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_OUTPUT_NAME = "11_agent_input_preview.md"
MAX_ARTIFACT_CHARS = 12000

ARTIFACT_ORDER = [
    "graph",
    "node_map",
    "values_bound",
    "component_rules",
    "netlist",
    "spice_emit_report",
    "spice_run",
    "ngspice_stdout",
    "ngspice_stderr",
    "tran_csv",
]


def load_json(path: Path) -> dict[str, Any]:
    """Legge un file JSON e restituisce un dizionario."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root is not an object: {path}")
    return data


def resolve_manifest_path(
    batch_name: str | None,
    circuit_id: str | None,
    context_path: str | Path | None,
    experiment_name: str | None = None,
) -> Path:
    """Trova il manifest 10 partendo da batch/circuito oppure da path diretto."""
    if context_path is not None:
        return Path(context_path)

    if not batch_name or not circuit_id:
        raise ValueError("Provide either --context or both --batch and --circuit.")

    if experiment_name:
        return (
            PROJECT_ROOT
            / "outputs"
            / "pipeline2.0"
            / batch_name
            / experiment_name
            / circuit_id
            / "10_diagnostic_context.json"
        )

    return (
        PROJECT_ROOT
        / "outputs"
        / "pipeline2.0"
        / batch_name
        / circuit_id
        / "10_diagnostic_context.json"
    )


def resolve_artifact_path(path_value: str | None) -> Path | None:
    """Converte un path del manifest in path assoluto del workspace."""
    if not path_value:
        return None

    path = Path(path_value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def read_artifact_text(path: Path) -> str:
    """Legge un artefatto come testo, formattando i JSON per renderli leggibili."""
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        return json.dumps(data, indent=2, ensure_ascii=False)
    return path.read_text(encoding="utf-8", errors="replace")


def limit_text(text: str, max_chars: int = MAX_ARTIFACT_CHARS) -> tuple[str, bool]:
    """Limita testi troppo lunghi, mantenendo esplicito il taglio."""
    if len(text) <= max_chars:
        return text, False
    return text[:max_chars].rstrip(), True


def artifact_language(path: Path) -> str:
    """Sceglie il linguaggio Markdown piu adatto per il blocco codice."""
    suffix = path.suffix.lower()
    if suffix == ".json":
        return "json"
    if suffix in {".cir", ".spice", ".ckt"}:
        return "spice"
    if suffix == ".csv":
        return "csv"
    return "text"


def build_agent_input_preview(
    manifest: dict[str, Any],
    user_problem: str,
) -> str:
    """
    Crea una vista Markdown leggibile delle evidenze ricevute dall'agente.

    Il preview affianca il prompt effettivo e rende verificabili ordine,
    contenuto e limiti senza modificare la richiesta inviata al modello.
    """
    lines: list[str] = []
    summary = manifest.get("summary") or {}
    artifacts = manifest.get("artifacts") or {}
    executed_scenarios = manifest.get("executed_scenarios") or []
    scenario_outcome_summary = manifest.get("scenario_outcome_summary") or {}
    image_access = manifest.get("image_access") or {}

    lines.extend(
        [
            "# Agent input preview",
            "",
            "This file is a local preview of the evidence that will be provided to the read-only diagnostic agent.",
            "The agent remains read-only: it can inspect base outputs and existing scenario artifacts, but it does not modify files.",
            "",
            "## User problem",
            "",
            user_problem.strip() or "No user problem provided.",
            "",
            "## Circuit",
            "",
            f"- Batch: `{manifest.get('batch_name')}`",
            f"- Circuit: `{manifest.get('circuit_id')}`",
            f"- Agent mode: `{manifest.get('agent_mode')}`",
            "",
            "## Technical summary",
            "",
            "```json",
            json.dumps(summary, indent=2, ensure_ascii=False),
            "```",
            "",
            "## Image policy",
            "",
            f"- Included by default: `{image_access.get('included_by_default')}`",
            f"- Can be requested: `{image_access.get('can_be_requested')}`",
            f"- Path: `{image_access.get('path')}`",
            f"- Policy: {image_access.get('policy')}",
            "",
            "## Agent rules",
            "",
        ]
    )

    for rule in manifest.get("agent_rules") or []:
        lines.append(f"- {rule}")

    lines.extend(
        [
            "",
            "## Scenario outcome summary",
            "",
            "```json",
            json.dumps(scenario_outcome_summary, indent=2, ensure_ascii=False),
            "```",
            "",
        ]
    )

    lines.extend(["", "## Executed scenarios", ""])
    if not executed_scenarios:
        lines.extend(["No executed scenarios are available in this manifest.", ""])
    else:
        for scenario in executed_scenarios:
            outcome = scenario.get("diagnostic_outcome") or {}
            summary_data = scenario.get("comparison_summary") or {}
            lines.extend(
                [
                    f"### {scenario.get('scenario_id')}",
                    "",
                    f"- Title: `{scenario.get('title')}`",
                    f"- Status: `{scenario.get('status')}`",
                    f"- SPICE status: `{scenario.get('spice_status')}`",
                    f"- Outcome: `{outcome.get('status')}`",
                    f"- Stop automation: `{outcome.get('stop_automation')}`",
                    f"- Comparison: `{summary_data.get('changed_count')}/{summary_data.get('requested_count')}` changed",
                    f"- LED profiles: `{json.dumps(scenario.get('led_profiles') or {}, ensure_ascii=False)}`",
                    "",
                ]
            )

            for artifact_name, metadata in (scenario.get("artifacts") or {}).items():
                if not metadata.get("available"):
                    continue
                path = resolve_artifact_path(metadata.get("path"))
                if path is None or not path.exists():
                    continue

                text = read_artifact_text(path)
                text, truncated = limit_text(text)
                language = artifact_language(path)
                lines.extend(
                    [
                        f"#### {artifact_name}",
                        "",
                        f"- Role: {metadata.get('role')}",
                        f"- Path: `{metadata.get('path')}`",
                        "",
                        f"```{language}",
                        text,
                        "```",
                        "",
                    ]
                )
                if truncated:
                    lines.extend(
                        [
                            "> Scenario artifact truncated in this preview.",
                            "",
                        ]
                    )

    lines.extend(["", "## Loaded artifacts", ""])

    for artifact_key in ARTIFACT_ORDER:
        metadata = artifacts.get(artifact_key) or {}
        if not metadata.get("available"):
            lines.extend(
                [
                    f"### {artifact_key}",
                    "",
                    "Artifact not available.",
                    "",
                ]
            )
            continue

        path = resolve_artifact_path(metadata.get("path"))
        if path is None or not path.exists():
            lines.extend(
                [
                    f"### {artifact_key}",
                    "",
                    "Artifact listed in the manifest, but the file was not found.",
                    "",
                ]
            )
            continue

        text = read_artifact_text(path)
        text, truncated = limit_text(text)
        language = artifact_language(path)

        lines.extend(
            [
                f"### {artifact_key}",
                "",
                f"- Step: `{metadata.get('step')}`",
                f"- Role: {metadata.get('role')}",
                f"- Path: `{metadata.get('path')}`",
                "",
                f"```{language}",
                text,
                "```",
                "",
            ]
        )
        if truncated:
            lines.extend(
                [
                    "> Artifact truncated in this preview. The original file remains available through the manifest path.",
                    "",
                ]
            )

    return "\n".join(lines).rstrip() + "\n"


def write_agent_input_preview(
    context_path: str | Path,
    user_problem: str,
    output_path: str | Path | None = None,
) -> Path:
    """Legge il manifest 10 e salva il preview Markdown dello step 11."""
    manifest_path = Path(context_path)
    manifest = load_json(manifest_path)
    destination = Path(output_path) if output_path else manifest_path.parent / DEFAULT_OUTPUT_NAME
    preview = build_agent_input_preview(manifest, user_problem)
    destination.write_text(preview, encoding="utf-8")
    return destination
