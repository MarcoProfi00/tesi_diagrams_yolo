from pathlib import Path
import json
import re
import csv
import statistics
import argparse
from collections import defaultdict

# ============================================================
# make_graph_csvs.py
#
# Legge i file judge_summary_*.json e genera CSV "flat" e aggregati
# utili per grafici:
# - score medio per modello
# - score medio per input type
# - score per modello/input type
# - delta immagine
# - costo medio
# - latenza media
# - quality per dollar
# - quality per second
# - heatmap modello x circuito
# - heatmap modello x criterio
# - top-1/top-3 accuracy
# - errori/allucinazioni
# ============================================================

# =========================
# CONFIGURAZIONE PREZZI
# =========================
# Prezzi stimati per 1M token.
# Aggiornali se cambiano i prezzi API.
# cost_usd = input_tokens/1M * input + output_tokens/1M * output
# Nota: per semplicità il costo principale usa "input" e "output".
# Se cached_tokens è presente, viene calcolato anche cost_usd_cached.

MODEL_PRICES = {
    "gpt-4o-mini": {
        "input": 0.15,
        "cached_input": 0.075,
        "output": 0.60,
    },
    "gpt-4.1-mini": {
        "input": 0.40,
        "cached_input": 0.10,
        "output": 1.60,
    },
    "gpt-4.1-nano": {
        "input": 0.10,
        "cached_input": 0.025,
        "output": 0.40,
    },
    "gpt-5-nano": {
        "input": 0.05,
        "cached_input": 0.005,
        "output": 0.40,
    },
    "gpt-5-mini": {
        "input": 0.25,
        "cached_input": 0.025,
        "output": 2.00,
    },
    "gpt-5.4-nano": {
        "input": 0.20,
        "cached_input": 0.02,
        "output": 1.25,
    },
    "gpt-5.4-mini": {
        "input": 0.75,
        "cached_input": 0.075,
        "output": 4.50,
    },
    "gpt-5.4": {
        "input": 2.50,
        "cached_input": 0.25,
        "output": 15.00,
    },
    "gpt-5.5": {
        "input": 5.00,
        "cached_input": 0.50,
        "output": 30.00,
    },
}

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

# =========================
# FUNZIONI BASE
# =========================

def mean(values):
    values = [v for v in values if isinstance(v, (int, float))]
    return sum(values) / len(values) if values else ""

def median(values):
    values = [v for v in values if isinstance(v, (int, float))]
    return statistics.median(values) if values else ""

def std(values):
    values = [v for v in values if isinstance(v, (int, float))]
    return statistics.pstdev(values) if len(values) > 1 else 0 if len(values) == 1 else ""

def pct_true(values):
    values = [v for v in values if isinstance(v, bool)]
    return 100 * sum(1 for v in values if v) / len(values) if values else ""

def safe_float(x):
    try:
        if x == "" or x is None:
            return ""
        return float(x)
    except Exception:
        return ""

def safe_int(x):
    try:
        if x == "" or x is None:
            return ""
        return int(x)
    except Exception:
        return ""

def parse_header_field(text, field):
    pattern = rf"^{re.escape(field)}:\s*(.*)$"
    match = re.search(pattern, text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""

def parse_usage_text(usage_text, prefix=""):
    """
    Estrae token da stringhe tipo:
    ResponseUsage(input_tokens=5702, input_tokens_details=InputTokensDetails(cached_tokens=4864), output_tokens=...)
    """
    result = {
        f"{prefix}input_tokens": "",
        f"{prefix}cached_input_tokens": "",
        f"{prefix}output_tokens": "",
        f"{prefix}reasoning_tokens": "",
        f"{prefix}total_tokens": "",
    }

    if not usage_text:
        return result

    patterns = {
        f"{prefix}input_tokens": r"input_tokens=(\d+)",
        f"{prefix}cached_input_tokens": r"cached_tokens=(\d+)",
        f"{prefix}output_tokens": r"output_tokens=(\d+)",
        f"{prefix}reasoning_tokens": r"reasoning_tokens=(\d+)",
        f"{prefix}total_tokens": r"total_tokens=(\d+)",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, usage_text)
        if match:
            result[key] = int(match.group(1))

    return result

def parse_original_result_file(path_str):
    """
    Legge il .txt prodotto dal modello sotto test e ricava:
    - latenza modello
    - token usage
    - problema
    """
    path = Path(path_str)

    base = {
        "model_latency_seconds": "",
        "model_input_tokens": "",
        "model_cached_input_tokens": "",
        "model_output_tokens": "",
        "model_reasoning_tokens": "",
        "model_total_tokens": "",
        "problem": "",
    }

    if not path.exists():
        return base

    text = path.read_text(encoding="utf-8")

    latency_match = re.search(r"LATENCY_SECONDS:\s*([\d.]+)", text)
    if latency_match:
        base["model_latency_seconds"] = float(latency_match.group(1))

    base["problem"] = parse_header_field(text, "PROBLEMA")

    usage_match = re.search(r"USAGE:\s*\n(.+?)\n\nRISPOSTA:", text, flags=re.DOTALL)
    usage_text = usage_match.group(1).strip() if usage_match else ""

    base.update(parse_usage_text(usage_text, prefix="model_"))

    return base

def cost_usd(model, input_tokens, output_tokens):
    if model not in MODEL_PRICES:
        return ""

    if input_tokens == "" or output_tokens == "":
        return ""

    p = MODEL_PRICES[model]

    return (
        input_tokens / 1_000_000 * p["input"]
        + output_tokens / 1_000_000 * p["output"]
    )

def cost_usd_cached(model, input_tokens, cached_input_tokens, output_tokens):
    if model not in MODEL_PRICES:
        return ""

    if input_tokens == "" or output_tokens == "":
        return ""

    cached = cached_input_tokens if isinstance(cached_input_tokens, int) else 0
    non_cached = max(input_tokens - cached, 0)

    p = MODEL_PRICES[model]
    cached_price = p.get("cached_input", p["input"])

    return (
        non_cached / 1_000_000 * p["input"]
        + cached / 1_000_000 * cached_price
        + output_tokens / 1_000_000 * p["output"]
    )

def latest_summary_per_circuit(judge_results_dir, circuit_name):
    files = sorted(
        judge_results_dir.glob(f"{circuit_name}__judge_summary_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return files[0] if files else None

def discover_summary_files(batch_dir, circuit_filter=None):
    """
    Cerca l'ultimo judge_summary per ogni circuito.
    """
    summary_files = []

    if circuit_filter:
        judge_dir = batch_dir / circuit_filter / "judge_results"
        summary = latest_summary_per_circuit(judge_dir, circuit_filter)
        if summary:
            summary_files.append(summary)
        return summary_files

    for circuit_dir in sorted(batch_dir.iterdir()):
        if not circuit_dir.is_dir():
            continue

        judge_dir = circuit_dir / "judge_results"
        if not judge_dir.exists():
            continue

        summary = latest_summary_per_circuit(judge_dir, circuit_dir.name)
        if summary:
            summary_files.append(summary)

    return summary_files

def flatten_entry(entry):
    metadata = entry.get("metadata", {})
    judge_result = entry.get("judge_result", {})
    scores = judge_result.get("scores", {})

    row = {
        "circuit": metadata.get("circuit", ""),
        "model": metadata.get("model_under_test", ""),
        "input_type": metadata.get("input_type", ""),
        "judge_model": metadata.get("judge_model", ""),
        "judge_latency_seconds": safe_float(metadata.get("judge_latency_seconds", "")),
        "evaluated_file": metadata.get("evaluated_file", ""),
        "evaluated_filename": Path(metadata.get("evaluated_file", "")).name,
        "parsed_ok": metadata.get("parsed_ok", ""),
        "score": judge_result.get("total_score", ""),
        "max_score": judge_result.get("max_score", 21),
        "normalized_score": judge_result.get("normalized_score", ""),
        "verdict": judge_result.get("verdict", ""),
        "top1_correct": judge_result.get("top1_correct", False),
        "top3_contains_correct": judge_result.get("top3_contains_correct", False),
        "major_errors_count": len(judge_result.get("major_errors", [])),
        "hallucinations_count": len(judge_result.get("hallucinations", [])),
        "missed_points_count": len(judge_result.get("missed_important_points", [])),
        "model_primary_cause": judge_result.get("model_primary_cause", ""),
        "short_explanation": judge_result.get("short_explanation", ""),
    }

    for c in CRITERIA:
        row[c] = scores.get(c, "")

    # Dati del modello sotto test dal .txt originale
    row.update(parse_original_result_file(row["evaluated_file"]))

    # Dati usage del judge dal summary JSON
    row.update(parse_usage_text(entry.get("judge_usage", ""), prefix="judge_"))

    # Costi
    row["model_cost_usd"] = cost_usd(
        row["model"],
        row["model_input_tokens"],
        row["model_output_tokens"],
    )
    row["model_cost_usd_cached"] = cost_usd_cached(
        row["model"],
        row["model_input_tokens"],
        row["model_cached_input_tokens"],
        row["model_output_tokens"],
    )
    row["judge_cost_usd"] = cost_usd(
        row["judge_model"],
        row["judge_input_tokens"],
        row["judge_output_tokens"],
    )
    row["judge_cost_usd_cached"] = cost_usd_cached(
        row["judge_model"],
        row["judge_input_tokens"],
        row["judge_cached_input_tokens"],
        row["judge_output_tokens"],
    )

    # Metriche derivate utili per grafici
    if isinstance(row["model_cost_usd"], (int, float)) and row["model_cost_usd"] > 0:
        row["quality_per_dollar"] = row["score"] / row["model_cost_usd"]
    else:
        row["quality_per_dollar"] = ""

    if isinstance(row["model_latency_seconds"], (int, float)) and row["model_latency_seconds"] > 0:
        row["quality_per_second"] = row["score"] / row["model_latency_seconds"]
    else:
        row["quality_per_second"] = ""

    return row

def model_sort_key(model):
    return MODEL_ORDER.index(model) if model in MODEL_ORDER else 999

def input_sort_key(input_type):
    return INPUT_ORDER.index(input_type) if input_type in INPUT_ORDER else 999

def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

def group_by(rows, keys):
    grouped = defaultdict(list)
    for r in rows:
        grouped[tuple(r[k] for k in keys)].append(r)
    return grouped

def aggregate_rows(rows, group_keys):
    grouped = group_by(rows, group_keys)
    out = []

    for key_tuple, group in grouped.items():
        row = {k: v for k, v in zip(group_keys, key_tuple)}

        scores = [safe_float(r["score"]) for r in group if r["score"] != ""]
        latencies = [safe_float(r["model_latency_seconds"]) for r in group if r["model_latency_seconds"] != ""]
        costs = [safe_float(r["model_cost_usd"]) for r in group if r["model_cost_usd"] != ""]
        costs_cached = [safe_float(r["model_cost_usd_cached"]) for r in group if r["model_cost_usd_cached"] != ""]

        row.update({
            "n": len(group),
            "score_mean": mean(scores),
            "score_median": median(scores),
            "score_std": std(scores),
            "top1_accuracy_pct": pct_true([r["top1_correct"] for r in group]),
            "top3_accuracy_pct": pct_true([r["top3_contains_correct"] for r in group]),
            "major_errors_mean": mean([r["major_errors_count"] for r in group]),
            "hallucinations_mean": mean([r["hallucinations_count"] for r in group]),
            "missed_points_mean": mean([r["missed_points_count"] for r in group]),
            "model_cost_mean_usd": mean(costs),
            "model_cost_mean_usd_cached": mean(costs_cached),
            "model_latency_mean_seconds": mean(latencies),
        })

        if isinstance(row["model_cost_mean_usd"], (int, float)) and row["model_cost_mean_usd"] > 0:
            row["quality_per_dollar"] = row["score_mean"] / row["model_cost_mean_usd"]
        else:
            row["quality_per_dollar"] = ""

        if isinstance(row["model_latency_mean_seconds"], (int, float)) and row["model_latency_mean_seconds"] > 0:
            row["quality_per_second"] = row["score_mean"] / row["model_latency_mean_seconds"]
        else:
            row["quality_per_second"] = ""

        for c in CRITERIA:
            row[f"{c}_mean"] = mean([safe_float(r[c]) for r in group if r[c] != ""])

        out.append(row)

    def sort_key(r):
        return (
            r.get("circuit", ""),
            model_sort_key(r.get("model", "")),
            input_sort_key(r.get("input_type", "")),
        )

    return sorted(out, key=sort_key)

def make_delta_by_model_input(rows):
    """
    Per ogni circuito e modello:
    delta_score = score(JSON + immagine + datasheet) - score(JSON + datasheet)
    """
    pivot = defaultdict(dict)

    for r in rows:
        pivot[(r["circuit"], r["model"])][r["input_type"]] = r

    out = []

    for (circuit, model), d in pivot.items():
        json_row = d.get("JSON + datasheet")
        img_row = d.get("JSON + immagine + datasheet")

        if not json_row or not img_row:
            continue

        score_json = safe_float(json_row["score"])
        score_img = safe_float(img_row["score"])

        row = {
            "circuit": circuit,
            "model": model,
            "score_json": score_json,
            "score_json_img": score_img,
            "delta_score_image": score_img - score_json,
            "top1_json": json_row["top1_correct"],
            "top1_json_img": img_row["top1_correct"],
            "top3_json": json_row["top3_contains_correct"],
            "top3_json_img": img_row["top3_contains_correct"],
            "cost_json_usd": json_row["model_cost_usd"],
            "cost_json_img_usd": img_row["model_cost_usd"],
            "delta_cost_image_usd": img_row["model_cost_usd"] - json_row["model_cost_usd"]
                if isinstance(img_row["model_cost_usd"], (int, float)) and isinstance(json_row["model_cost_usd"], (int, float))
                else "",
            "latency_json_seconds": json_row["model_latency_seconds"],
            "latency_json_img_seconds": img_row["model_latency_seconds"],
            "delta_latency_image_seconds": img_row["model_latency_seconds"] - json_row["model_latency_seconds"]
                if isinstance(img_row["model_latency_seconds"], (int, float)) and isinstance(json_row["model_latency_seconds"], (int, float))
                else "",
        }

        out.append(row)

    return sorted(out, key=lambda r: (r["circuit"], model_sort_key(r["model"])))

def make_heatmap_model_circuit(rows):
    agg = aggregate_rows(rows, ["model", "circuit"])

    return [
        {
            "model": r["model"],
            "circuit": r["circuit"],
            "score_mean": r["score_mean"],
            "n": r["n"],
        }
        for r in agg
    ]

def make_heatmap_model_criteria(rows):
    agg = aggregate_rows(rows, ["model"])

    out = []
    for r in agg:
        for c in CRITERIA:
            out.append({
                "model": r["model"],
                "criterion": c,
                "criterion_label": CRITERIA_IT[c],
                "score_mean": r[f"{c}_mean"],
            })

    return sorted(out, key=lambda r: (model_sort_key(r["model"]), r["criterion"]))

# =========================
# MAIN
# =========================

def main():
    parser = argparse.ArgumentParser(
        description="Genera CSV per grafici a partire dai judge_summary JSON."
    )

    parser.add_argument(
        "--batch-dir",
        default=None,
        help="Path della cartella batch_v1. Se omesso, viene calcolato da scripts/GPT.",
    )

    parser.add_argument(
        "--circuit",
        default=None,
        help="Circuito specifico da processare, es. ic3. Se omesso, processa tutti i circuiti con judge_results.",
    )

    parser.add_argument(
        "--out-dir",
        default=None,
        help="Cartella output CSV. Default: batch_v1/analysis_csv oppure circuito/analysis_csv.",
    )

    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    project_root = Path(__file__).resolve().parents[2]

    batch_dir = Path(args.batch_dir) if args.batch_dir else (
        project_root / "experiment_ai" / "circuiti_complessi" / "batch_v1"
    )

    summary_files = discover_summary_files(batch_dir, circuit_filter=args.circuit)

    if not summary_files:
        raise FileNotFoundError("Nessun judge_summary trovato.")

    rows = []

    for summary_path in summary_files:
        print(f"Leggo: {summary_path}")

        with summary_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        for entry in data:
            rows.append(flatten_entry(entry))

    rows = sorted(
        rows,
        key=lambda r: (
            r["circuit"],
            model_sort_key(r["model"]),
            input_sort_key(r["input_type"]),
        )
    )

    if args.out_dir:
        out_dir = Path(args.out_dir)
    elif args.circuit:
        out_dir = batch_dir / args.circuit / "analysis_csv"
    else:
        out_dir = batch_dir / "analysis_csv"

    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Flat table: una riga per run
    flat_fields = [
        "circuit",
        "model",
        "input_type",
        "score",
        "max_score",
        "normalized_score",
        "verdict",
        "top1_correct",
        "top3_contains_correct",
        "major_errors_count",
        "hallucinations_count",
        "missed_points_count",
        *CRITERIA,
        "model_latency_seconds",
        "model_input_tokens",
        "model_cached_input_tokens",
        "model_output_tokens",
        "model_reasoning_tokens",
        "model_total_tokens",
        "model_cost_usd",
        "model_cost_usd_cached",
        "quality_per_dollar",
        "quality_per_second",
        "judge_model",
        "judge_latency_seconds",
        "judge_input_tokens",
        "judge_cached_input_tokens",
        "judge_output_tokens",
        "judge_reasoning_tokens",
        "judge_total_tokens",
        "judge_cost_usd",
        "judge_cost_usd_cached",
        "evaluated_filename",
        "problem",
        "model_primary_cause",
        "short_explanation",
    ]

    write_csv(out_dir / "runs_flat.csv", rows, flat_fields)

    # 2. Aggregazioni
    by_model = aggregate_rows(rows, ["model"])
    by_input = aggregate_rows(rows, ["input_type"])
    by_model_input = aggregate_rows(rows, ["model", "input_type"])
    by_circuit = aggregate_rows(rows, ["circuit"])
    by_circuit_model = aggregate_rows(rows, ["circuit", "model"])
    by_circuit_input = aggregate_rows(rows, ["circuit", "input_type"])

    agg_fields = [
        "circuit",
        "model",
        "input_type",
        "n",
        "score_mean",
        "score_median",
        "score_std",
        "top1_accuracy_pct",
        "top3_accuracy_pct",
        "major_errors_mean",
        "hallucinations_mean",
        "missed_points_mean",
        "model_cost_mean_usd",
        "model_cost_mean_usd_cached",
        "model_latency_mean_seconds",
        "quality_per_dollar",
        "quality_per_second",
        *[f"{c}_mean" for c in CRITERIA],
    ]

    write_csv(out_dir / "summary_by_model.csv", by_model, agg_fields)
    write_csv(out_dir / "summary_by_input_type.csv", by_input, agg_fields)
    write_csv(out_dir / "summary_by_model_input.csv", by_model_input, agg_fields)
    write_csv(out_dir / "summary_by_circuit.csv", by_circuit, agg_fields)
    write_csv(out_dir / "summary_by_circuit_model.csv", by_circuit_model, agg_fields)
    write_csv(out_dir / "summary_by_circuit_input.csv", by_circuit_input, agg_fields)

    # 3. Delta immagine
    delta_rows = make_delta_by_model_input(rows)
    write_csv(
        out_dir / "delta_image_by_model.csv",
        delta_rows,
        [
            "circuit",
            "model",
            "score_json",
            "score_json_img",
            "delta_score_image",
            "top1_json",
            "top1_json_img",
            "top3_json",
            "top3_json_img",
            "cost_json_usd",
            "cost_json_img_usd",
            "delta_cost_image_usd",
            "latency_json_seconds",
            "latency_json_img_seconds",
            "delta_latency_image_seconds",
        ],
    )

    # 4. Heatmap model x circuit
    heatmap_mc = make_heatmap_model_circuit(rows)
    write_csv(
        out_dir / "heatmap_model_circuit.csv",
        heatmap_mc,
        ["model", "circuit", "score_mean", "n"],
    )

    # 5. Heatmap model x criteria
    heatmap_mcrit = make_heatmap_model_criteria(rows)
    write_csv(
        out_dir / "heatmap_model_criteria.csv",
        heatmap_mcrit,
        ["model", "criterion", "criterion_label", "score_mean"],
    )

    print("\nCSV generati in:")
    print(out_dir)

    print("\nFile principali:")
    for name in [
        "runs_flat.csv",
        "summary_by_model.csv",
        "summary_by_input_type.csv",
        "summary_by_model_input.csv",
        "delta_image_by_model.csv",
        "heatmap_model_circuit.csv",
        "heatmap_model_criteria.csv",
    ]:
        print(f"- {out_dir / name}")

if __name__ == "__main__":
    main()
