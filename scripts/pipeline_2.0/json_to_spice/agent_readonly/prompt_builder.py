"""
Costruzione del prompt per l'agente diagnostico read-only.

Questo modulo prepara il file 11_agent_prompt.md, cioe il testo che potra essere
mandato al modello AI nella prima versione dell'agente.

Il prompt resta separato dal preview:

- il preview serve a noi per vedere tutti gli artefatti caricati;
- il prompt serve al futuro modello AI per rispondere in modo controllato.

La versione corrente non chiama ancora OpenAI. Genera solo un prompt locale e
verificabile, con istruzioni stabili ed evidenze caricate dagli output 01-08.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent_readonly.preview_builder import (
    artifact_language,
    limit_text,
    load_json,
    read_artifact_text,
    resolve_artifact_path,
)
from agent_readonly.scenario_prompt import (
    build_scenario_answer_format,
    build_scenario_guidance,
    build_scenario_operating_rules,
)


DEFAULT_PROMPT_OUTPUT_NAME = "11_agent_prompt.md"
MAX_PROMPT_ARTIFACT_CHARS = 9000

# Lo step 10 non compare qui perche e il manifest usato per costruire il prompt,
# non una evidenza tecnica da analizzare come graph, node map o stdout/stderr.
PROMPT_ARTIFACT_ORDER = [
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


def build_system_instructions() -> list[str]:
    """Restituisce le istruzioni stabili per il modello AI."""
    return [
        "You are a read-only diagnostic assistant for electronic circuits.",
        "Your task is to explain the Pipeline 2.0 and ngspice results using only the provided evidence.",
        "The final answer must be written in Italian.",
        "Keep technical identifiers exactly as provided, for example node names, component IDs and file names.",
        "Do not invent component values, electrical connections, SPICE models, node voltages, currents or simulation results.",
        "Do not assume that a component exists if it is not present in the Graph JSON or in the generated netlist.",
        "Do not modify the netlist, do not execute SPICE and do not apply scenarios.",
        "Diagnostic scenarios may be suggested only as future SPICE-verifiable hypotheses, not as already verified facts.",
        "Use general electronics and SPICE knowledge only to interpret the provided evidence, not to create missing evidence.",
        "If the evidence is insufficient, say exactly what is missing.",
        "Do not describe a branch as floating unless the evidence shows a floating or singleton node with no DC reference path.",
        "If a branch has a resistive path to ground but no active source, describe it as not driven or not powered.",
    ]


def build_answer_format() -> list[str]:
    """Definisce la struttura obbligatoria della risposta finale."""
    return [
        "Rispondi in Markdown usando esattamente queste sezioni:",
        "",
        "1. **Stato della simulazione**",
        "   Spiega se ngspice e stato eseguito correttamente oppure no.",
        "",
        "2. **Evidenze principali**",
        "   Elenca le prove piu importanti, citando componenti, nodi, netlist, stdout/stderr o report.",
        "",
        "3. **Diagnosi rispetto al problema utente**",
        "   Collega le evidenze al problema scritto dall'utente.",
        "",
        "4. **Limiti della diagnosi**",
        "   Dichiara cosa non si puo concludere dai dati disponibili.",
        "",
        "5. **Scenari diagnostici proposti**",
        "   Proponi al massimo 3 scenari diagnostici candidati, pensati per essere trasformati in una nuova simulazione SPICE.",
        "   Non proporre semplici consigli generici: ogni scenario deve essere una ipotesi verificabile.",
        "   Non presentarli come certamente risolutivi: sono candidati da testare.",
        "   Se servono piu scenari, ordinali dal piu semplice al piu utile.",
        "   Se dai dati disponibili non serve uno scenario, scrivi: `Nessuno scenario necessario dai dati disponibili.`",
        "",
        *build_scenario_answer_format(),
        "",
        "Alla fine aggiungi una riga:",
        "",
        "`Richiede immagine: si/no`",
        "",
        "Metti `si` solo se gli output strutturati indicano una probabile incoerenza del Graph JSON oppure se SPICE non e eseguibile in modo utile.",
        "Se l'immagine sarebbe solo una verifica opzionale, metti comunque `no` e cita la verifica opzionale nei limiti.",
    ]


def build_prompt_operating_rules() -> list[str]:
    """Definisce regole operative adatte al prompt gia caricato."""
    return [
        "Treat the evidence sections below as the only technical evidence available in this prompt.",
        "When useful, cite component IDs, node IDs, file names or artifact sections.",
        "Use the original artifact paths only as traceability references.",
        "If an artifact is missing or truncated, mention the limitation before drawing conclusions from it.",
        "Do not use the original image unless the structured evidence suggests that the Graph JSON may be wrong.",
        "If image access is needed, explain which structured evidence justifies it.",
        "Request image access only for strong structured reasons: Graph JSON warnings, suspicious or missing connections, important singleton nodes, missing critical components, unsupported critical topology, or ngspice failure caused by topology/convergence issues.",
        "If ngspice succeeds and graph/node-map evidence is internally coherent, do not request the image by default.",
        "In read-only mode, do not modify netlists, do not change values and do not execute scenarios.",
        *build_scenario_operating_rules(),
    ]


def build_artifact_index(artifacts: dict[str, Any]) -> list[str]:
    """Crea l'indice degli artefatti disponibili nel prompt."""
    lines = []
    for artifact_name, metadata in artifacts.items():
        availability = "available" if metadata.get("available") else "missing"
        lines.append(
            f"- `{artifact_name}`: {availability}, path=`{metadata.get('path')}`"
        )
    return lines


def build_evidence_sections(artifacts: dict[str, Any]) -> list[str]:
    """Carica gli artefatti selezionati e li inserisce come evidenze."""
    lines: list[str] = []

    for artifact_name in PROMPT_ARTIFACT_ORDER:
        metadata = artifacts.get(artifact_name) or {}
        lines.extend([f"### {artifact_name}", ""])

        if not metadata.get("available"):
            lines.extend(["Evidence not available.", ""])
            continue

        path = resolve_artifact_path(metadata.get("path"))
        if path is None or not path.exists():
            lines.extend(["Evidence listed in the manifest, but the file was not found.", ""])
            continue

        text = read_artifact_text(path)
        text, truncated = limit_text(text, MAX_PROMPT_ARTIFACT_CHARS)
        language = artifact_language(path)

        lines.extend(
            [
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
                    "> Evidence truncated for prompt size. Use only the visible evidence, and mention if more detail may be needed.",
                    "",
                ]
            )

    return lines


def build_agent_prompt(
    manifest: dict[str, Any],
    user_problem: str,
) -> str:
    """
    Crea il prompt Markdown per l'agente read-only.

    Il prompt include istruzioni, problema utente, riepilogo tecnico, policy
    immagine, indice artefatti ed evidenze selezionate.
    """
    summary = manifest.get("summary") or {}
    artifacts = manifest.get("artifacts") or {}
    image_access = manifest.get("image_access") or {}

    lines = [
        "# Diagnostic agent prompt",
        "",
        "## System instructions",
        "",
        *[f"- {instruction}" for instruction in build_system_instructions()],
        "",
        "## Operating rules",
        "",
        *[f"- {rule}" for rule in build_prompt_operating_rules()],
    ]

    lines.extend(
        [
            "",
            "## User problem",
            "",
            user_problem.strip() or "No user problem provided.",
            "",
            "## Circuit metadata",
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
            "## Available artifacts",
            "",
            *build_artifact_index(artifacts),
            "",
            "## Image access policy",
            "",
            f"- Included by default: `{image_access.get('included_by_default')}`",
            f"- Can be requested: `{image_access.get('can_be_requested')}`",
            f"- Path: `{image_access.get('path')}`",
            f"- Policy: {image_access.get('policy')}",
            "",
            "## Diagnostic scenario meaning",
            "",
            *build_scenario_guidance(),
            "",
            "## Evidence to analyze",
            "",
            *build_evidence_sections(artifacts),
            "",
            "## Required answer format",
            "",
            *build_answer_format(),
            "",
            "## Final task",
            "",
            "Analyze the user problem using the evidence above.",
            "Explain what the simulation result means, whether it supports the user problem, and what can or cannot be concluded.",
            "If ngspice failed, focus on the error evidence and explain why the current circuit is not diagnostically reliable.",
            "If ngspice succeeded, connect the simulated node voltages, currents, skipped components and warnings to the user problem.",
            "Suggest future diagnostic scenarios only as controlled SPICE-verifiable hypotheses; do not claim that they have already been executed.",
            "Keep scenarios natural and minimally invasive before proposing topology or Graph JSON corrections.",
        ]
    )

    return "\n".join(lines).rstrip() + "\n"


def write_agent_prompt(
    context_path: str | Path,
    user_problem: str,
    output_path: str | Path | None = None,
) -> Path:
    """Legge il manifest 10 e salva il prompt dello step 11."""
    manifest_path = Path(context_path)
    manifest = load_json(manifest_path)
    destination = Path(output_path) if output_path else manifest_path.parent / DEFAULT_PROMPT_OUTPUT_NAME
    prompt = build_agent_prompt(manifest, user_problem)
    destination.write_text(prompt, encoding="utf-8")
    return destination
