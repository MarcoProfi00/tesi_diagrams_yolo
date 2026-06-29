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
        "New diagnostic scenarios may be suggested only as future SPICE-verifiable hypotheses, not as already verified facts.",
        "Already executed scenarios must be interpreted from the executed scenario evidence, not re-imagined.",
        "Use general electronics and SPICE knowledge only to interpret the provided evidence, not to create missing evidence.",
        "If the evidence is insufficient, say exactly what is missing.",
        "Do not describe a branch as floating unless the evidence shows a floating or singleton node with no DC reference path.",
        "If a branch has a resistive path to ground but no active source, describe it as not driven or not powered.",
    ]


def is_executed_scenario_question(user_problem: str) -> bool:
    """Riconosce domande che chiedono di interpretare scenari gia eseguiti."""
    text = user_problem.lower()
    scenario_words = ("scenario", "scenari")
    outcome_words = (
        "risolve",
        "risolto",
        "risolutivo",
        "migliore",
        "quale",
        "conferma",
        "parziale",
        "partially",
        "resolved",
        "outcome",
    )
    return any(word in text for word in scenario_words) and any(word in text for word in outcome_words)


def build_executed_scenario_answer_format() -> list[str]:
    """Formato speciale quando l'utente chiede degli scenari gia eseguiti."""
    return [
        "La domanda riguarda scenari gia eseguiti.",
        "Non proporre nuovi scenari in questa risposta, a meno che l'utente lo chieda esplicitamente.",
        "Rispondi in Markdown usando esattamente queste sezioni:",
        "",
        "1. **Risposta diretta**",
        "   Indica subito quale scenario ha l'outcome piu forte.",
        "   Se esiste uno scenario con `diagnostic_outcome.status = resolved_candidate` e `stop_automation = true`, dillo chiaramente.",
        "",
        "2. **Perche quello scenario risolve meglio**",
        "   Usa `scenario_comparison.json`: cita le grandezze cambiate, valori base, valori scenario e delta quando sono rilevanti.",
        "",
        "3. **Perche gli altri scenari non bastano**",
        "   Spiega per ogni altro scenario perche e solo parziale, diagnostico o di isolamento.",
        "",
        "4. **Conclusione operativa**",
        "   Spiega se l'automazione dovrebbe fermarsi o continuare, usando `stop_automation`.",
        "",
        "`Richiede immagine: si/no`",
    ]


def build_answer_format(user_problem: str = "") -> list[str]:
    """Definisce la struttura obbligatoria della risposta finale."""
    if is_executed_scenario_question(user_problem):
        return build_executed_scenario_answer_format()

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
        "   Se la domanda dell'utente riguarda scenari gia eseguiti, usa questa sezione per riassumere gli scenari eseguiti e indicare quale outcome e piu forte.",
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
        "If executed scenario evidence is available, use it to answer questions about which scenario explains or resolves the problem.",
        "When discussing executed scenarios, distinguish the controlled action from the diagnostic outcome.",
        "For questions about which scenario resolves the problem, do not merely list scenarios: identify the strongest scenario and justify it from scenario_comparison.json.",
        "Treat `resolved_candidate` with `stop_automation=true` as the strongest executed-scenario outcome.",
        "Treat `partially_resolved` as supporting diagnostic evidence, not as the main resolving scenario when a resolved_candidate exists.",
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


def build_executed_scenario_index(executed_scenarios: list[dict[str, Any]]) -> list[str]:
    """Crea un indice breve degli scenari gia disponibili."""
    if not executed_scenarios:
        return ["No executed scenarios are available in the manifest."]

    lines: list[str] = []
    for scenario in executed_scenarios:
        outcome = scenario.get("diagnostic_outcome") or {}
        summary = scenario.get("comparison_summary") or {}
        lines.append(
            "- "
            f"`{scenario.get('scenario_id')}`: "
            f"title=`{scenario.get('title')}`, "
            f"status=`{scenario.get('status')}`, "
            f"spice=`{scenario.get('spice_status')}`, "
            f"outcome=`{outcome.get('status')}`, "
            f"stop_automation=`{outcome.get('stop_automation')}`, "
            f"changed=`{summary.get('changed_count')}/{summary.get('requested_count')}`"
        )
    return lines


def build_scenario_outcome_summary_section(summary: dict[str, Any]) -> list[str]:
    """Inserisce nel prompt una sintesi computata degli outcome scenario."""
    if not summary or not summary.get("available"):
        return ["No scenario outcome summary available."]

    return [
        "```json",
        json.dumps(summary, indent=2, ensure_ascii=False),
        "```",
        "",
        "Interpretation rule for scenario questions:",
        "- The best scenario is the one indicated by `best_scenario_id`, unless direct evidence contradicts it.",
        "- A `resolved_candidate` with `stop_automation=true` is the main resolving candidate.",
        "- `partially_resolved` scenarios can confirm supporting hypotheses but should not be presented as the scenario that solved the problem when a resolved candidate exists.",
    ]


def build_executed_scenario_sections(executed_scenarios: list[dict[str, Any]]) -> list[str]:
    """Carica gli artefatti principali degli scenari eseguiti."""
    if not executed_scenarios:
        return ["No executed scenario evidence available.", ""]

    lines: list[str] = []
    for scenario in executed_scenarios:
        scenario_id = scenario.get("scenario_id") or "scenario"
        lines.extend(
            [
                f"### {scenario_id}",
                "",
                f"- Title: `{scenario.get('title')}`",
                f"- Scenario dir: `{scenario.get('scenario_dir')}`",
                f"- Status: `{scenario.get('status')}`",
                f"- SPICE status: `{scenario.get('spice_status')}`",
                "",
            ]
        )

        artifacts = scenario.get("artifacts") or {}
        for artifact_name in (
            "scenario_definition",
            "scenario_status",
            "controlled_scenario_report",
            "scenario_comparison",
        ):
            metadata = artifacts.get(artifact_name) or {}
            lines.extend([f"#### {artifact_name}", ""])
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
                        "> Scenario evidence truncated for prompt size.",
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
    executed_scenarios = manifest.get("executed_scenarios") or []
    scenario_outcome_summary = manifest.get("scenario_outcome_summary") or {}
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
            "## Executed scenarios index",
            "",
            *build_executed_scenario_index(executed_scenarios),
            "",
            "## Scenario outcome summary",
            "",
            *build_scenario_outcome_summary_section(scenario_outcome_summary),
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
            "## Executed scenario evidence",
            "",
            *build_executed_scenario_sections(executed_scenarios),
            "",
            "## Required answer format",
            "",
            *build_answer_format(user_problem),
            "",
            "## Final task",
            "",
            "Analyze the user problem using the evidence above.",
            "Explain what the simulation result means, whether it supports the user problem, and what can or cannot be concluded.",
            "If ngspice failed, focus on the error evidence and explain why the current circuit is not diagnostically reliable.",
            "If ngspice succeeded, connect the simulated node voltages, currents, skipped components and warnings to the user problem.",
            "If the question is about already executed scenarios, use the executed scenario evidence and clearly identify the strongest outcome.",
            "When suggesting new future diagnostic scenarios, present them only as controlled SPICE-verifiable hypotheses.",
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
