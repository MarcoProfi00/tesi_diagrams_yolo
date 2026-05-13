from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# =========================
# CONFIGURAZIONE
# =========================

MODEL = "gpt-5.4-nano"

PROBLEM = "Il circuito non produce audio sugli altoparlanti. Quali sono le cause più probabili?"

# Lo script si trova in: scripts/GPT/run_one_json.py
SCRIPT_DIR = Path(__file__).resolve().parent

# Root del progetto: salgo da scripts/GPT a cartella principale
PROJECT_ROOT = Path(__file__).resolve().parents[2]

CIRCUIT_DIR = (
    PROJECT_ROOT
    / "experiment_ai"
    / "circuiti_complessi"
    / "batch_v1"
    / "ic3"
)

# File di input
JSON_PATH = CIRCUIT_DIR / "ic3.json"
DATASHEET_PATH = CIRCUIT_DIR / "datasheet" / "datasheet.txt"
PROMPT_PATH = CIRCUIT_DIR / "prompt_json.txt"

# Cartella risultati
RESULTS_DIR = CIRCUIT_DIR / "results_json"

# =========================
# SETUP
# =========================

load_dotenv(SCRIPT_DIR / ".env")
client = OpenAI()

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# =========================
# CONTROLLO FILE
# =========================

for path in [JSON_PATH, DATASHEET_PATH, PROMPT_PATH]:
    if not path.exists():
        raise FileNotFoundError(f"File non trovato: {path}")

# =========================
# LETTURA FILE
# =========================

circuit_json = JSON_PATH.read_text(encoding="utf-8")
datasheet = DATASHEET_PATH.read_text(encoding="utf-8")
prompt_template = PROMPT_PATH.read_text(encoding="utf-8")

# Sostituisce i placeholder presenti nel prompt
prompt = (
    prompt_template
    .replace("[INSERIRE PROBLEMA]", PROBLEM)
    .replace("[INCOLLARE DATASHEET O ESTRATTO]", datasheet)
    .replace("[INCOLLARE JSON]", circuit_json)
)


# =========================
# CHIAMATA API
# =========================

print(f"\nEseguo {MODEL} su circuito ic3...")
print(f"JSON: {JSON_PATH}")
print(f"DATASHEET: {DATASHEET_PATH}")
print(f"PROMPT: {PROMPT_PATH}\n")

response = client.responses.create(
    model=MODEL,
    input=prompt,
    max_output_tokens=3000,
)

answer = response.output_text

# =========================
# SALVATAGGIO RISULTATO
# =========================

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = RESULTS_DIR / f"ic3_{MODEL}_{timestamp}.txt"

with output_path.open("w", encoding="utf-8") as f:
    f.write(f"MODELLO: {MODEL}\n")
    f.write(f"CIRCUITO: ic3\n")
    f.write(f"PROBLEMA: {PROBLEM}\n\n")

    if response.usage:
        f.write("USAGE:\n")
        f.write(str(response.usage))
        f.write("\n\n")

    f.write("RISPOSTA:\n")
    f.write(answer)

print("Risposta salvata in:")
print(output_path)

if response.usage:
    print("\nToken usage:")
    print(response.usage)

print("\n--- RISPOSTA MODELLO ---\n")
print(answer)