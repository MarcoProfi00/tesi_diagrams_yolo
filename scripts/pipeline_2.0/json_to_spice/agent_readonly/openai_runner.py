"""
Runner OpenAI minimale per l'agente read-only.

Questo modulo prende il prompt gia generato dallo step 11 e, solo quando
l'utente passa esplicitamente il flag --run-agent, chiama OpenAI e salva la
risposta in Markdown.

La logica resta volutamente semplice:

- non modifica gli output originali;
- non crea scenari;
- non esegue ngspice;
- non stampa mai la API key;
- usa OPENAI_API_KEY dall'ambiente o da file .env locali gia presenti.
"""

from __future__ import annotations

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_RESPONSE_OUTPUT_NAME = "11_agent_response.md"
DEFAULT_MODEL = "gpt-5.4"
SUPPORTED_MODEL_HINTS = [
    "gpt-5.4",
    "gpt-5.5",
    "gpt-5.4-mini",
    "gpt-5-mini",
]
DEFAULT_ENV_FILES = [
    PROJECT_ROOT / ".env",
    PROJECT_ROOT / "scripts" / "GPT" / ".env",
]


def load_env_file(path: Path) -> None:
    """
    Carica variabili semplici da un file .env.

    Il parser e minimale per evitare dipendenze aggiuntive: supporta righe del
    tipo CHIAVE=valore e ignora commenti o righe vuote.
    """
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def load_default_env_files() -> None:
    """Carica i file .env noti senza sovrascrivere variabili gia presenti."""
    for env_path in DEFAULT_ENV_FILES:
        load_env_file(env_path)


def resolve_model(model: str | None = None) -> str:
    """Sceglie il modello da usare, preferendo argomento CLI e variabile env."""
    return model or os.environ.get("OPENAI_MODEL") or DEFAULT_MODEL


def supported_model_hint() -> str:
    """Restituisce una lista leggibile dei modelli consigliati."""
    return ", ".join(SUPPORTED_MODEL_HINTS)


def read_prompt(prompt_path: str | Path) -> str:
    """Legge il prompt Markdown generato dallo step 11."""
    return Path(prompt_path).read_text(encoding="utf-8")


def extract_response_text(response: object) -> str:
    """
    Estrae il testo dalla risposta OpenAI.

    Le versioni recenti del client espongono output_text. Il fallback serve solo
    a produrre un errore leggibile se la forma della risposta cambia.
    """
    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str) and output_text.strip():
        return output_text

    raise RuntimeError("OpenAI response did not contain output_text.")


def call_openai(prompt: str, model: str) -> str:
    """Chiama OpenAI con il prompt completo e restituisce il testo generato."""
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "Python package 'openai' is not installed. Install it before using --run-agent."
        ) from exc

    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY not found. Set it in the environment or in a local .env file."
        )

    client = OpenAI()
    response = client.responses.create(
        model=model,
        input=prompt,
    )
    return extract_response_text(response)


def write_agent_response(
    prompt_path: str | Path,
    model: str | None = None,
    output_path: str | Path | None = None,
) -> Path:
    """
    Esegue la chiamata OpenAI e salva la risposta Markdown.

    Questa funzione viene chiamata solo se l'utente usa --run-agent.
    """
    load_default_env_files()

    prompt_file = Path(prompt_path)
    selected_model = resolve_model(model)
    destination = (
        Path(output_path)
        if output_path
        else prompt_file.parent / DEFAULT_RESPONSE_OUTPUT_NAME
    )

    prompt = read_prompt(prompt_file)
    response_text = call_openai(prompt=prompt, model=selected_model)
    destination.write_text(response_text.rstrip() + "\n", encoding="utf-8")
    return destination
