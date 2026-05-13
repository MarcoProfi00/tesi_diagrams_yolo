from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import base64
import mimetypes

# =========================
# CONFIGURAZIONE
# =========================

MODEL = "gpt-5.4"

PROBLEM = "Il circuito non produce audio sugli altoparlanti. Quali sono le cause più probabili?"

# Lo script si trova in: scripts/GPT/run_one_image.py
SCRIPT_DIR = Path(__file__).resolve().parent

# Root del progetto: salgo da scripts/GPT a cartella principale
PROJECT_ROOT = Path(__file__).resolve().parents[2]

CIRCUIT_NAME = "ic3"

CIRCUIT_DIR = (
    PROJECT_ROOT
    / "experiment_ai"
    / "circuiti_complessi"
    / "batch_v1"
    / CIRCUIT_NAME
)

# File di input
DATASHEET_PATH = CIRCUIT_DIR / "datasheet" / "datasheet.txt"
PROMPT_PATH = CIRCUIT_DIR / "prompt_img.txt"

# L'immagine si trova nella stessa cartella del JSON, es. ic3.jpg
IMAGE_PATH = CIRCUIT_DIR / f"{CIRCUIT_NAME}.jpg"

# Cartella risultati
RESULTS_DIR = CIRCUIT_DIR / "results_img"

# =========================
# SETUP
# =========================

load_dotenv(SCRIPT_DIR / ".env")
client = OpenAI()

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# =========================
# CONTROLLO FILE
# =========================

for path in [IMAGE_PATH, DATASHEET_PATH, PROMPT_PATH]:
    if not path.exists():
        raise FileNotFoundError(f"File non trovato: {path}")

# =========================
# LETTURA FILE
# =========================

datasheet = DATASHEET_PATH.read_text(encoding="utf-8")
prompt_template = PROMPT_PATH.read_text(encoding="utf-8")

prompt = (
    prompt_template
    .replace("[INSERIRE PROBLEMA]", PROBLEM)
    .replace("[INCOLLARE DATASHEET O ESTRATTO]", datasheet)
    .replace("[CARICARE O INSERIRE IMMAGINE]", "L'immagine del circuito è allegata come input_image.")
)

# =========================
# CODIFICA IMMAGINE
# =========================

mime_type, _ = mimetypes.guess_type(IMAGE_PATH)

if mime_type is None:
    mime_type = "image/jpeg"

with IMAGE_PATH.open("rb") as image_file:
    base64_image = base64.b64encode(image_file.read()).decode("utf-8")

image_data_url = f"data:{mime_type};base64,{base64_image}"

# =========================
# CHIAMATA API
# =========================

print(f"\nEseguo {MODEL} su immagine circuito {CIRCUIT_NAME}...")
print(f"IMMAGINE: {IMAGE_PATH}")
print(f"DATASHEET: {DATASHEET_PATH}")
print(f"PROMPT: {PROMPT_PATH}\n")

response = client.responses.create(
    model=MODEL,
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": prompt,
                },
                {
                    "type": "input_image",
                    "image_url": image_data_url,
                    "detail": "original",
                },
            ],
        }
    ],
    max_output_tokens=3000,
)

answer = response.output_text

# =========================
# SALVATAGGIO RISULTATO
# =========================

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = RESULTS_DIR / f"{CIRCUIT_NAME}_{MODEL}_{timestamp}.txt"

with output_path.open("w", encoding="utf-8") as f:
    f.write(f"MODELLO: {MODEL}\n")
    f.write(f"CIRCUITO: {CIRCUIT_NAME}\n")
    f.write(f"INPUT: immagine + datasheet\n")
    f.write(f"IMMAGINE: {IMAGE_PATH}\n")
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