from pathlib import Path
import json
import re
import statistics
from collections import defaultdict

# =========================
# CONFIGURAZIONE
# =========================

CIRCUIT_NAME = "c17"
BATCH_NAME = "batch_v2"

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = Path(__file__).resolve().parents[2]

CIRCUIT_DIR = (
    PROJECT_ROOT
    / "experiment_ai"
    / "circuiti_complessi"
    / BATCH_NAME
    / CIRCUIT_NAME
)

JUDGE_RESULTS_DIR = CIRCUIT_DIR / "judge_results"
OUTPUT_MD = JUDGE_RESULTS_DIR / f"{CIRCUIT_NAME}_judge_tables.md"

MODEL_ORDER = [
    "gpt-4o-mini",
    "gpt-4.1-mini",
    "gpt-4.1-nano",
    "gpt-5-nano",
    "gpt-5-mini",
    "gpt-5.4-nano",
    "gpt-5.4-mini",
    "gpt-5.4",
]

INPUT_ORDER = [
    "JSON + datasheet",
    "JSON + immagine + datasheet",
]

CRITERIA = [
    "circuit_understanding",
    "datasheet_use",
    "json_image_use",
    "diagnostic_accuracy",
    "cause_priority",
    "practical_checks",
    "hallucination_absence",
]

CRITERIA_IT = {
    "circuit_understanding": "Comprensione circuito",
    "datasheet_use": "Uso datasheet",
    "json_image_use": "Uso JSON/immagine",
    "diagnostic_accuracy": "Accuratezza diagnostica",
    "cause_priority": "Priorità cause",
    "practical_checks": "Controlli pratici",
    "hallucination_absence": "Assenza allucinazioni",
}

# Prezzi judge gpt-5.5 per 1M token.
# Modifica questi valori se usi un judge diverso.
JUDGE_PRICE_INPUT = 5.00
JUDGE_PRICE_OUTPUT = 30.00

# Prezzi stimati modelli sotto test per 1M token.
# Verifica sempre sulla pagina pricing ufficiale OpenAI se cambiano.
MODEL_PRICES = {
    "gpt-4o-mini": {
        "input": 0.15,
        "output": 0.60,
    },
    "gpt-4.1-mini": {
        "input": 0.40,
        "output": 1.60,
    },
    "gpt-4.1-nano": {
        "input": 0.10,
        "output": 0.40,
    },
    "gpt-5-nano": {
        "input": 0.05,
        "output": 0.40,
    },
    "gpt-5-mini": {
        "input": 0.25,
        "output": 2.00,
    },
    "gpt-5.4-nano": {
        "input": 0.20,
        "output": 1.25,
    },
    "gpt-5.4-mini": {
        "input": 0.75,
        "output": 4.50,
    },
    "gpt-5.4": {
        "input": 2.50,
        "output": 15.00,
    },
}


def mean(values):
    return sum(values) / len(values) if values else 0


def median(values):
    return statistics.median(values) if values else 0


def std(values):
    return statistics.pstdev(values) if len(values) > 1 else 0


def pct(values):
    return 100 * sum(1 for v in values if v) / len(values) if values else 0


def fmt(value, digits=2):
    if value == "" or value is None:
        return ""
    if isinstance(value, bool):
        return "Sì" if value else "No"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def escape_md(value):
    text = str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def md_table(headers, rows, align=None):
    if align is None:
        align = ["---"] * len(headers)

    out = []
    out.append("| " + " | ".join(headers) + " |")
    out.append("| " + " | ".join(align) + " |")

    for row in rows:
        out.append("| " + " | ".join(escape_md(v) for v in row) + " |")

    return "\n".join(out)


def latest_summary_file():
    files = sorted(
        JUDGE_RESULTS_DIR.glob(f"{CIRCUIT_NAME}__judge_summary_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if not files:
        raise FileNotFoundError(f"Nessun judge summary trovato in: {JUDGE_RESULTS_DIR}")

    return files[0]


def parse_usage(usage_str):
    result = {
        "judge_input_tokens": "",
        "judge_output_tokens": "",
        "judge_total_tokens": "",
        "judge_reasoning_tokens": "",
    }

    if not usage_str:
        return result

    patterns = {
        "judge_input_tokens": r"input_tokens=(\d+)",
        "judge_output_tokens": r"output_tokens=(\d+)",
        "judge_total_tokens": r"total_tokens=(\d+)",
        "judge_reasoning_tokens": r"reasoning_tokens=(\d+)",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, usage_str)
        if match:
            result[key] = int(match.group(1))

    return result


def parse_original_result_file(path_str):
    path = Path(path_str)

    if not path.exists():
        return {
            "model_latency_seconds": "",
            "input_tokens": "",
            "output_tokens": "",
            "total_tokens": "",
        }

    text = path.read_text(encoding="utf-8")

    latency_match = re.search(r"LATENCY_SECONDS:\s*([\d.]+)", text)
    input_match = re.search(r"input_tokens=(\d+)", text)
    output_match = re.search(r"output_tokens=(\d+)", text)
    total_match = re.search(r"total_tokens=(\d+)", text)

    return {
        "model_latency_seconds": float(latency_match.group(1)) if latency_match else "",
        "input_tokens": int(input_match.group(1)) if input_match else "",
        "output_tokens": int(output_match.group(1)) if output_match else "",
        "total_tokens": int(total_match.group(1)) if total_match else "",
    }


def flatten_entry(entry):
    metadata = entry["metadata"]
    result = entry["judge_result"]
    scores = result["scores"]

    row = {
        "circuit": metadata.get("circuit", ""),
        "model": metadata.get("model_under_test", ""),
        "input_type": metadata.get("input_type", ""),
        "judge_model": metadata.get("judge_model", ""),
        "judge_latency_seconds": metadata.get("judge_latency_seconds", ""),
        "score": result.get("total_score", ""),
        "normalized_score": result.get("normalized_score", ""),
        "verdict": result.get("verdict", ""),
        "top1_correct": result.get("top1_correct", False),
        "top3_contains_correct": result.get("top3_contains_correct", False),
        "major_errors": len(result.get("major_errors", [])),
        "hallucinations": len(result.get("hallucinations", [])),
        "missed_important_points": len(result.get("missed_important_points", [])),
        "short_explanation": result.get("short_explanation", ""),
        "evaluated_file": Path(metadata.get("evaluated_file", "")).name,
    }

    for criterion in CRITERIA:
        row[criterion] = scores.get(criterion, 0)

    row.update(parse_original_result_file(metadata.get("evaluated_file", "")))
    row.update(parse_usage(entry.get("judge_usage", "")))

    return row


def sort_key(row):
    model_idx = MODEL_ORDER.index(row["model"]) if row["model"] in MODEL_ORDER else 999
    input_idx = INPUT_ORDER.index(row["input_type"]) if row["input_type"] in INPUT_ORDER else 999
    return model_idx, input_idx


def judge_cost(row):
    input_tokens = row.get("judge_input_tokens", "")
    output_tokens = row.get("judge_output_tokens", "")

    if input_tokens == "" or output_tokens == "":
        return ""

    return (
        input_tokens / 1_000_000 * JUDGE_PRICE_INPUT
        + output_tokens / 1_000_000 * JUDGE_PRICE_OUTPUT
    )

def model_cost(row):
    model = row.get("model", "")
    input_tokens = row.get("input_tokens", "")
    output_tokens = row.get("output_tokens", "")

    if model not in MODEL_PRICES:
        return ""

    if input_tokens == "" or output_tokens == "":
        return ""

    prices = MODEL_PRICES[model]

    return (
        input_tokens / 1_000_000 * prices["input"]
        + output_tokens / 1_000_000 * prices["output"]
    )


summary_path = latest_summary_file()

with summary_path.open("r", encoding="utf-8") as f:
    data = json.load(f)

rows = sorted([flatten_entry(entry) for entry in data], key=sort_key)

# =========================
# 1. RISULTATI DETTAGLIATI
# =========================

detailed_rows = []

for r in rows:
    detailed_rows.append([
        r["circuit"],
        f"`{r['model']}`",
        r["input_type"],
        r["score"],
        fmt(r["normalized_score"], 3),
        r["verdict"],
        fmt(r["top1_correct"]),
        fmt(r["top3_contains_correct"]),
        r["major_errors"],
        r["hallucinations"],
        fmt(r["model_latency_seconds"], 2),
        r["input_tokens"],
        r["output_tokens"],
        fmt(model_cost(r), 5),
    ])

table_detailed = md_table(
    [
        "Circuito",
        "Modello",
        "Input",
        "Score / 21",
        "Score norm.",
        "Verdict",
        "Top-1",
        "Top-3",
        "Errori gravi",
        "Allucinazioni",
        "Latenza modello (s)",
        "Input tokens",
        "Output tokens",
        "Costo modello ($)",
    ],
    detailed_rows,
    ["---", "---", "---", "---:", "---:", "---", "---", "---", "---:", "---:", "---:", "---:", "---:", "---:"],
)

# =========================
# 2. CONFRONTO JSON VS JSON+IMG
# =========================

pivot = defaultdict(dict)

for r in rows:
    pivot[r["model"]][r["input_type"]] = r

comparison_rows = []

for model in MODEL_ORDER:
    json_row = pivot.get(model, {}).get("JSON + datasheet")
    img_row = pivot.get(model, {}).get("JSON + immagine + datasheet")

    if not json_row and not img_row:
        continue

    if json_row and img_row:
        delta = img_row["score"] - json_row["score"]
        delta_text = f"{delta:+d}"
    else:
        delta_text = ""

    comparison_rows.append([
        f"`{model}`",
        json_row["score"] if json_row else "",
        img_row["score"] if img_row else "",
        delta_text,
        fmt(json_row["top1_correct"]) if json_row else "",
        fmt(img_row["top1_correct"]) if img_row else "",
        json_row["major_errors"] if json_row else "",
        img_row["major_errors"] if img_row else "",
    ])

table_comparison = md_table(
    [
        "Modello",
        "JSON + datasheet",
        "JSON + immagine + datasheet",
        "Delta immagine",
        "Top-1 JSON",
        "Top-1 JSON+img",
        "Errori JSON",
        "Errori JSON+img",
    ],
    comparison_rows,
    ["---", "---:", "---:", "---:", "---", "---", "---:", "---:"],
)

# =========================
# 3. AGGREGAZIONE PER INPUT
# =========================

by_input = defaultdict(list)

for r in rows:
    by_input[r["input_type"]].append(r)

input_rows = []

for input_type in INPUT_ORDER:
    group = by_input.get(input_type, [])

    if not group:
        continue

    scores = [r["score"] for r in group]
    latencies = [r["model_latency_seconds"] for r in group if r["model_latency_seconds"] != ""]

    input_rows.append([
        input_type,
        len(group),
        fmt(mean(scores), 2),
        fmt(median(scores), 2),
        fmt(std(scores), 2),
        f"{fmt(pct([r['top1_correct'] for r in group]), 1)}%",
        f"{fmt(pct([r['top3_contains_correct'] for r in group]), 1)}%",
        fmt(mean([r["major_errors"] for r in group]), 2),
        fmt(mean([r["hallucinations"] for r in group]), 2),
        fmt(mean(latencies), 2) if latencies else "",
    ])

table_by_input = md_table(
    [
        "Input type",
        "N",
        "Score medio",
        "Mediana",
        "Std",
        "Top-1 accuracy",
        "Top-3 accuracy",
        "Errori gravi medi",
        "Allucinazioni medie",
        "Latenza media modello (s)",
    ],
    input_rows,
    ["---", "---:", "---:", "---:", "---:", "---:", "---:", "---:", "---:", "---:"],
)

# =========================
# 4. AGGREGAZIONE PER MODELLO
# =========================

by_model = defaultdict(list)

for r in rows:
    by_model[r["model"]].append(r)

model_rows = []

for model in MODEL_ORDER:
    group = by_model.get(model, [])

    if not group:
        continue

    scores = [r["score"] for r in group]
    latencies = [r["model_latency_seconds"] for r in group if r["model_latency_seconds"] != ""]
    costs = [model_cost(r) for r in group if model_cost(r) != ""]

    model_rows.append([
        f"`{model}`",
        len(group),
        fmt(mean(scores), 2),
        fmt(median(scores), 2),
        fmt(std(scores), 2),
        f"{fmt(pct([r['top1_correct'] for r in group]), 1)}%",
        f"{fmt(pct([r['top3_contains_correct'] for r in group]), 1)}%",
        fmt(mean([r["major_errors"] for r in group]), 2),
        fmt(mean([r["hallucinations"] for r in group]), 2),
        fmt(mean(costs), 5) if costs else "",
        fmt(mean(latencies), 2) if latencies else "",
    ])

table_by_model = md_table(
    [
        "Modello",
        "N",
        "Score medio",
        "Mediana",
        "Std",
        "Top-1 accuracy",
        "Top-3 accuracy",
        "Errori gravi medi",
        "Allucinazioni medie",
        "Costo medio modello ($)",
        "Latenza media modello (s)",

    ],
    model_rows,
    ["---", "---:", "---:", "---:", "---:", "---:", "---:", "---:", "---:", "---:", "---:"],
)

# =========================
# 5. CRITERI MEDI PER MODELLO
# =========================

criteria_rows = []

for model in MODEL_ORDER:
    group = by_model.get(model, [])

    if not group:
        continue

    criteria_rows.append([
        f"`{model}`",
        *[fmt(mean([r[c] for r in group]), 2) for c in CRITERIA],
    ])

table_criteria = md_table(
    ["Modello"] + [CRITERIA_IT[c] for c in CRITERIA],
    criteria_rows,
    ["---"] + ["---:"] * len(CRITERIA),
)

# =========================
# 6. COSTO JUDGE
# =========================

judge_cost_rows = []
total_judge_cost = 0.0

for r in rows:
    cost = judge_cost(r)

    if cost != "":
        total_judge_cost += cost

    judge_cost_rows.append([
        f"`{r['model']}`",
        r["input_type"],
        r["judge_input_tokens"],
        r["judge_output_tokens"],
        r["judge_total_tokens"],
        fmt(cost, 4) if cost != "" else "",
        fmt(r["judge_latency_seconds"], 2),
    ])

table_judge_cost = md_table(
    [
        "Modello",
        "Input",
        "Judge input tokens",
        "Judge output tokens",
        "Judge total tokens",
        "Costo judge stimato ($)",
        "Latenza judge (s)",
    ],
    judge_cost_rows,
    ["---", "---", "---:", "---:", "---:", "---:", "---:"],
)

json_mean = mean([r["score"] for r in by_input["JSON + datasheet"]])
img_mean = mean([r["score"] for r in by_input["JSON + immagine + datasheet"]])
best = max(rows, key=lambda r: r["score"])
worst = min(rows, key=lambda r: r["score"])

markdown = f"""# Tabelle judge — {CIRCUIT_NAME}

File sorgente:

`{summary_path.name}`

## Sintesi rapida

- Esecuzioni valutate: **{len(rows)}**
- Score medio `JSON + datasheet`: **{json_mean:.2f} / 21**
- Score medio `JSON + immagine + datasheet`: **{img_mean:.2f} / 21**
- Delta medio dovuto all'immagine: **{img_mean - json_mean:+.2f} punti**
- Miglior run: **`{best['model']}`**, input **{best['input_type']}**, score **{best['score']} / 21**
- Peggior run: **`{worst['model']}`**, input **{worst['input_type']}**, score **{worst['score']} / 21**
- Costo judge stimato totale: **${total_judge_cost:.2f}**

---

## 1. Risultati dettagliati per run

{table_detailed}

---

## 2. Confronto JSON-only vs JSON + immagine

{table_comparison}

---

## 3. Aggregazione per input type

{table_by_input}

---

## 4. Aggregazione per modello

{table_by_model}

---

## 5. Score medi per criterio e modello

{table_criteria}

---

## 6. Token, costo e latenza del judge

{table_judge_cost}

---

## Nota sui costi

Il costo del modello rappresenta il costo operativo della diagnosi automatica, cioè quanto costerebbe eseguire il sistema di troubleshooting sul circuito.

Il costo del judge è riportato separatamente perché riguarda solo la fase di valutazione automatica offline e non farebbe parte del costo operativo del sistema finale.
"""


OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT_MD.open("w", encoding="utf-8") as f:
    f.write(markdown)

print("Markdown generato:")
print(OUTPUT_MD)
