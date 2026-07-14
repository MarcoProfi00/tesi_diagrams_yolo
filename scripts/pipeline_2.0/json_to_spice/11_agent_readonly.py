"""
Agente diagnostico in sola lettura.

Questo modulo e la prima base concreta dell'agente AI.

Di default non chiama nessun modello esterno. Legge il manifest prodotto dallo
step 10, carica gli artefatti principali della Pipeline 2.0 e prepara un file
Markdown con l'input che verra poi dato all'agente.

La logica deve restare generale per tutti i batch: l'agente non deve conoscere
casi speciali come a01, a02 o a10, ma deve usare solo il contesto fornito dalla
pipeline.

Responsabilita della versione corrente:

- leggere 10_diagnostic_context.json;
- leggere una domanda o un sintomo dell'utente;
- risolvere i path degli artefatti indicati dal manifest;
- caricare graph, node map, valori, regole, netlist e output ngspice;
- leggere anche gli eventuali scenari gia eseguiti indicizzati dal manifest;
- costruire un preview ordinato dell'input per il futuro modello AI;
- costruire il prompt controllato da mandare al modello AI;
- chiamare OpenAI solo se viene passato esplicitamente --run-agent;
- non eseguire scenari e non modificare la netlist.

Gli output base sono 11_agent_input_preview.md e 11_agent_prompt.md.
Con --run-agent viene prodotto anche 11_agent_response.md.
"""

from __future__ import annotations

import argparse

from agent_readonly.openai_runner import write_agent_response
from agent_readonly.prompt_builder import write_agent_prompt
from agent_readonly.preview_builder import (
    resolve_manifest_path,
    write_agent_input_preview,
)


def parse_args() -> argparse.Namespace:
    """Legge gli argomenti da terminale."""
    parser = argparse.ArgumentParser(
        description="Pipeline 2.0 step 11: build a read-only agent input preview."
    )
    parser.add_argument(
        "--context",
        default=None,
        help="Path diretto a 10_diagnostic_context.json.",
    )
    parser.add_argument(
        "--batch",
        default=None,
        help="Nome batch, per esempio batchA.",
    )
    parser.add_argument(
        "--circuit",
        default=None,
        help="ID circuito, per esempio a01.",
    )
    parser.add_argument(
        "--experiment",
        default=None,
        help=(
            "Nome esperimento opzionale. Se indicato, legge il contesto da "
            "outputs/pipeline2.0/<batch>/<experiment>/<circuit>/."
        ),
    )
    parser.add_argument(
        "--question",
        default="Explain the SPICE result and diagnose the circuit using the available evidence.",
        help="Problema o domanda dell'utente.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Path di output. Default: 11_agent_input_preview.md nella cartella circuito.",
    )
    parser.add_argument(
        "--prompt-output",
        default=None,
        help="Path prompt. Default: 11_agent_prompt.md nella cartella circuito.",
    )
    parser.add_argument(
        "--run-agent",
        action="store_true",
        help="Chiama OpenAI usando il prompt generato. Default: non chiama il modello.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help=(
            "Modello OpenAI da usare con --run-agent. "
            "Default: OPENAI_MODEL o gpt-5.4. "
            "Consigliati: gpt-5.4, gpt-5.5, gpt-5.4-mini, gpt-5-mini."
        ),
    )
    parser.add_argument(
        "--response-output",
        default=None,
        help="Path risposta agente. Default: 11_agent_response.md nella cartella circuito.",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point da terminale."""
    args = parse_args()
    context_path = resolve_manifest_path(args.batch, args.circuit, args.context, args.experiment)
    output_path = write_agent_input_preview(
        context_path=context_path,
        user_problem=args.question,
        output_path=args.output,
    )
    prompt_path = write_agent_prompt(
        context_path=context_path,
        user_problem=args.question,
        output_path=args.prompt_output,
    )
    print(f"agent input preview -> {output_path}")
    print(f"agent prompt -> {prompt_path}")

    if args.run_agent:
        response_path = write_agent_response(
            prompt_path=prompt_path,
            model=args.model,
            output_path=args.response_output,
        )
        print(f"agent response -> {response_path}")


if __name__ == "__main__":
    main()
