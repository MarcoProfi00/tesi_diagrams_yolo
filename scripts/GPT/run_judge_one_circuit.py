from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import base64
import mimetypes
import time
import json
import re

# =========================
# CONFIGURAZIONE
# =========================
JUDGE_MODEL = "gpt-5.5"
CIRCUIT_NAME = "ic15"

# Lo stesso problema usato per generare gli output del circuito
PROBLEM = "Il circuito si accende, ma la tensione in uscita non e' corretta. Quale potrebbe essere il problema?"

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = Path(__file__).resolve().parents[2]

CIRCUIT_DIR = (
    PROJECT_ROOT
    / "experiment_ai"
    / "circuiti_complessi"
    / "batch_v1"
    / CIRCUIT_NAME
)

JSON_PATH = CIRCUIT_DIR / f"{CIRCUIT_NAME}.json"
IMAGE_PATH = CIRCUIT_DIR / f"{CIRCUIT_NAME}.jpg"
DATASHEET_DIR = CIRCUIT_DIR / "datasheet"
JUDGE_PROMPT_PATH = SCRIPT_DIR / "prompt_judge.txt"

RESULTS_JSON_DIR = CIRCUIT_DIR / "results_json"
RESULTS_JSON_IMG_DIR = CIRCUIT_DIR / "results_json_img"
JUDGE_RESULTS_DIR = CIRCUIT_DIR / "judge_results"

# =========================
# SETUP
# =========================

load_dotenv(SCRIPT_DIR / ".env")
client = OpenAI()

JUDGE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# =========================
# FUNZIONI
# =========================

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def encode_image_data_url(image_path: Path) -> str:
    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type is None:
        mime_type = "image/jpeg"

    with image_path.open("rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

    return f"data:{mime_type};base64,{base64_image}"


def parse_header_field(text: str, field: str) -> str:
    pattern = rf"^{re.escape(field)}:\s*(.*)$"
    match = re.search(pattern, text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def extract_answer(result_text: str) -> str:
    marker = "RISPOSTA:"
    if marker not in result_text:
        return result_text.strip()
    return result_text.split(marker, 1)[1].strip()


def safe_json_parse(text: str):
    cleaned = text.strip()

    # Rimuove eventuali fence markdown se il modello le produce per errore
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

    return json.loads(cleaned)


def build_judge_prompt(
    template: str,
    input_type: str,
    problem: str,
    datasheet: str,
    circuit_json: str,
    model_output: str,
) -> str:
    return (
        template
        .replace("[INPUT_TYPE]", input_type)
        .replace("[PROBLEM]", problem)
        .replace("[DATASHEET]", datasheet)
        .replace("[JSON]", circuit_json)
        .replace("[MODEL_OUTPUT]", model_output)
    )


def judge_one_file(result_path: Path, input_type: str, context):
    result_text = read_text(result_path)

    model_under_test = parse_header_field(result_text, "MODELLO")
    circuit = parse_header_field(result_text, "CIRCUITO")
    model_output = extract_answer(result_text)

    if not model_output:
        print(f"ATTENZIONE: output vuoto, salto o giudico come risposta vuota: {result_path.name}")

    judge_prompt = build_judge_prompt(
        template=context["judge_prompt_template"],
        input_type=input_type,
        problem=context["problem"],
        datasheet=context["datasheet"],
        circuit_json=context["circuit_json"],
        model_output=model_output,
    )

    request_kwargs = {
        "model": JUDGE_MODEL,
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": judge_prompt,
                    },
                    {
                        "type": "input_image",
                        "image_url": context["image_data_url"],
                        "detail": "original",
                    },
                ],
            }
        ],
        "max_output_tokens": 2500,
    }

    # GPT-5.5 supporta reasoning.effort.
    # Uso low per contenere costo e latenza.
    if JUDGE_MODEL.startswith("gpt-5"):
        request_kwargs["reasoning"] = {"effort": "low"}

    print(f"\nJudge su: {result_path.name}")
    print(f"Input type: {input_type}")
    print(f"Modello sotto valutazione: {model_under_test}")

    start_time = time.perf_counter()
    response = client.responses.create(**request_kwargs)
    end_time = time.perf_counter()

    latency_seconds = end_time - start_time
    judge_text = response.output_text.strip()

    parsed_ok = True
    try:
        judge_json = safe_json_parse(judge_text)
    except Exception as e:
        parsed_ok = False
        judge_json = {
            "parse_error": str(e),
            "raw_judge_output": judge_text,
        }

    output_data = {
        "metadata": {
            "circuit": circuit or CIRCUIT_NAME,
            "evaluated_file": str(result_path),
            "model_under_test": model_under_test,
            "input_type": input_type,
            "judge_model": JUDGE_MODEL,
            "judge_latency_seconds": round(latency_seconds, 3),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "parsed_ok": parsed_ok,
        },
        "judge_usage": str(response.usage) if response.usage else None,
        "judge_result": judge_json,
    }

    output_path = JUDGE_RESULTS_DIR / f"{result_path.stem}__judge_{JUDGE_MODEL}.json"

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"Salvato judge: {output_path}")
    print(f"Judge latency seconds: {latency_seconds:.3f}")

    return output_data


# =========================
# CONTROLLO FILE
# =========================

required_paths = [
    JSON_PATH,
    IMAGE_PATH,
    DATASHEET_DIR,
    JUDGE_PROMPT_PATH,
]

for path in required_paths:
    if not path.exists():
        raise FileNotFoundError(f"File non trovato: {path}")

DATASHEET_PATHS = sorted(DATASHEET_DIR.glob("*.txt"))

if not DATASHEET_PATHS:
    raise FileNotFoundError(f"Nessun file datasheet .txt trovato in: {DATASHEET_DIR}")

# =========================
# LETTURA CONTESTO
# =========================

context = {
    "circuit_json": read_text(JSON_PATH),
    "datasheet": "\n\n---\n\n".join(
        read_text(path)
        for path in DATASHEET_PATHS
    ),
    "judge_prompt_template": read_text(JUDGE_PROMPT_PATH),
    "image_data_url": encode_image_data_url(IMAGE_PATH),
    "problem": PROBLEM,
}

# =========================
# RACCOLTA OUTPUT DA GIUDICARE
# =========================

result_files = []

if RESULTS_JSON_DIR.exists():
    for path in sorted(RESULTS_JSON_DIR.glob("*.txt")):
        result_files.append((path, "JSON + datasheet"))

if RESULTS_JSON_IMG_DIR.exists():
    for path in sorted(RESULTS_JSON_IMG_DIR.glob("*.txt")):
        result_files.append((path, "JSON + immagine + datasheet"))

if not result_files:
    raise FileNotFoundError("Nessun file risultato trovato in results_json o results_json_img.")

print(f"\nCircuito: {CIRCUIT_NAME}")
print(f"File da giudicare: {len(result_files)}")
print(f"Judge model: {JUDGE_MODEL}")
print("Datasheet:")
for path in DATASHEET_PATHS:
    print(f"- {path}")

# =========================
# ESECUZIONE JUDGE
# =========================

all_results = []

for result_path, input_type in result_files:
    judged = judge_one_file(result_path, input_type, context)
    all_results.append(judged)

# =========================
# SALVATAGGIO INDICE COMPLETO
# =========================

summary_path = JUDGE_RESULTS_DIR / f"{CIRCUIT_NAME}__judge_summary_{JUDGE_MODEL}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

with summary_path.open("w", encoding="utf-8") as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)

print("\nCompletato.")
print(f"Summary salvato in: {summary_path}")
