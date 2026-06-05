from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import time

# =========================
# CONFIGURAZIONE
# =========================

# gpt-4o-mini
# gpt-4.1-mini
# gpt-4.1-nano
# gpt-5-nano
# gpt-5-mini
# gpt-5.4-nano
# gpt-5.4-mini
# gpt-5.4
MODEL = "gpt-5.4"

PROBLEM = "Quando alimento il circuito, la lampada dovrebbe lampeggiare, ma resta fissa o non si accende affatto. Quale potrebbe essere il problema?"

BATCH_NAME = "batch_v2"

# Lo script si trova in: scripts/GPT/run_one_json.py
SCRIPT_DIR = Path(__file__).resolve().parent

# Root del progetto: salgo da scripts/GPT a cartella principale
PROJECT_ROOT = Path(__file__).resolve().parents[2]

CIRCUIT_NAME = "c17"

CIRCUIT_DIR = (
    PROJECT_ROOT
    / "experiment_ai"
    / "circuiti_complessi"
    / BATCH_NAME
    / CIRCUIT_NAME
)

# File di input
JSON_PATH = CIRCUIT_DIR / f"{CIRCUIT_NAME}.json"
DATASHEET_DIR = CIRCUIT_DIR / "datasheet"
PROMPT_PATH = CIRCUIT_DIR / "prompt_json.txt"

# Cartella risultati
RESULTS_DIR = CIRCUIT_DIR / "results_json"

NO_DATASHEET_TEXT = (
    "Datasheet non presente: il circuito non contiene circuiti integrati o "
    "componenti che richiedono un datasheet dedicato. Analizzare il circuito "
    "usando il JSON, i collegamenti del graph e le informazioni visibili nello schema."
)

# =========================
# SETUP
# =========================

load_dotenv(SCRIPT_DIR / ".env")
client = OpenAI()

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# =========================
# CONTROLLO FILE
# =========================

for path in [JSON_PATH, PROMPT_PATH]:
    if not path.exists():
        raise FileNotFoundError(f"File non trovato: {path}")

DATASHEET_PATHS = sorted(DATASHEET_DIR.glob("*.txt")) if DATASHEET_DIR.exists() else []

# =========================
# LETTURA FILE
# =========================

circuit_json = JSON_PATH.read_text(encoding="utf-8")
datasheet = (
    "\n\n---\n\n".join(
        path.read_text(encoding="utf-8")
        for path in DATASHEET_PATHS
    )
    if DATASHEET_PATHS
    else NO_DATASHEET_TEXT
)
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

print(f"\nEseguo {MODEL} su circuito {CIRCUIT_NAME}...")
print(f"JSON: {JSON_PATH}")
if DATASHEET_PATHS:
    print("DATASHEET:")
    for path in DATASHEET_PATHS:
        print(f"- {path}")
else:
    print("DATASHEET: non presente")
print(f"PROMPT: {PROMPT_PATH}\n")

start_time = time.perf_counter()

request_kwargs = {
    "model": MODEL,
    "input": prompt,
    "max_output_tokens": 10000,
}

# I modelli GPT-5 usano reasoning tokens.
# Con effort basso riduciamo rischio di risposta vuota, costo e latenza.
if MODEL.startswith("gpt-5"):
    request_kwargs["reasoning"] = {"effort": "low"}

response = client.responses.create(**request_kwargs)

end_time = time.perf_counter()
latency_seconds = end_time - start_time

answer = response.output_text

# =========================
# SALVATAGGIO RISULTATO
# =========================

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = RESULTS_DIR / f"{CIRCUIT_NAME}_{MODEL}_{timestamp}.txt"

with output_path.open("w", encoding="utf-8") as f:
    f.write(f"MODELLO: {MODEL}\n")
    f.write(f"CIRCUITO: {CIRCUIT_NAME}\n")
    f.write(f"INPUT: JSON + datasheet\n")
    f.write(f"JSON: {JSON_PATH}\n")
    if DATASHEET_PATHS:
        f.write("DATASHEET:\n")
        for path in DATASHEET_PATHS:
            f.write(f"- {path}\n")
    else:
        f.write("DATASHEET: non presente\n")
    f.write(f"PROBLEMA: {PROBLEM}\n")
    f.write(f"LATENCY_SECONDS: {latency_seconds:.3f}\n\n")

    if response.usage:
        f.write("USAGE:\n")
        f.write(str(response.usage))
        f.write("\n\n")

    f.write("RISPOSTA:\n")
    f.write(answer)

print("Risposta salvata in:")
print(output_path)

print(f"\nLatency seconds: {latency_seconds:.3f}")

if response.usage:
    print("\nToken usage:")
    print(response.usage)

print("\n--- RISPOSTA MODELLO ---\n")
print(answer)
