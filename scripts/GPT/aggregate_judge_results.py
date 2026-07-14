#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aggrega tutti i risultati del judge dei circuiti in un unico dataset.

Struttura attesa, ad esempio:
experiment_ai/circuiti_complessi/batch_v1/
  ic2/judge_results/ic2__judge_summary_....json
  ic3/judge_results/ic3__judge_summary_....json
  ...

Supporta sia:
- JSON summary = lista di run [{metadata, judge_result, judge_usage}, ...]
- JSON singolo = {metadata, judge_result, judge_usage}

Output principali:
- all_runs.csv                 una riga per ogni run circuit/modello/input
- all_runs.json                stesso contenuto in JSON
- aggregate_by_model.csv
- aggregate_by_model_input.csv
- aggregate_by_circuit.csv
- aggregate_by_input_type.csv
- deltas_image_vs_json.csv     delta score per circuito e modello
- criteria_long.csv            formato lungo per heatmap criterio/modello/circuito

Uso:
python aggregate_judge_results.py --root "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\experiment_ai\\circuiti_complessi\\batch_v1"

Opzionale:
python aggregate_judge_results.py --root "...\\batch_v1" --out "...\\batch_v1\\_aggregate"
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import defaultdict
from pathlib import Path
from statistics import mean, median, pstdev
from typing import Any, Dict, Iterable, List, Optional, Tuple


# -----------------------------------------------------------------------------
# Prezzi opzionali
# -----------------------------------------------------------------------------
# Prezzi stimati modelli sotto test per 1M token.
# Fonte: pagina pricing ufficiale OpenAI.
# Tariffe standard, non Batch API.
MODEL_PRICES_PER_1M = {
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

# Prezzo del modello judge.
JUDGE_PRICES_PER_1M = {
    "gpt-5.5": {
        "input": 5.00,
        "output": 30.00,
    },
}

CRITERIA = [
    "circuit_understanding",
    "datasheet_use",
    "json_image_use",
    "diagnostic_accuracy",
    "cause_priority",
    "practical_checks",
    "hallucination_absence",
]

# -----------------------------------------------------------------------------
# Arrotondamenti output
# -----------------------------------------------------------------------------

ROUNDING_RULES = {
    # Score
    "normalized_score": 3,
    "total_score": 2,
    "max_score": 2,

    # Criteri judge
    "circuit_understanding": 2,
    "datasheet_use": 2,
    "json_image_use": 2,
    "diagnostic_accuracy": 2,
    "cause_priority": 2,
    "practical_checks": 2,
    "hallucination_absence": 2,

    # Latenze
    "model_latency_seconds": 2,
    "judge_latency_seconds": 2,

    # Costi
    "model_cost_usd": 6,
    "judge_cost_usd": 6,
    "model_cost_usd_total": 6,
    "judge_cost_usd_total": 6,
    "total_cost_usd": 6,
}


def round_for_export(value: Any, digits: int) -> Any:
    if value is None or value == "":
        return ""
    try:
        return round(float(value), digits)
    except Exception:
        return value


def format_rows_for_export(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    formatted = []
    for row in rows:
        new_row = dict(row)

        for key, digits in ROUNDING_RULES.items():
            if key in new_row:
                new_row[key] = round_for_export(new_row[key], digits)

        # Arrotonda automaticamente anche le colonne aggregate:
        # es. total_score_mean, model_cost_usd_mean, normalized_score_std, ecc.
        for key in list(new_row.keys()):
            if key.endswith(("_mean", "_median", "_std", "_rate")):
                if "cost" in key:
                    new_row[key] = round_for_export(new_row[key], 6)
                elif "latency" in key:
                    new_row[key] = round_for_export(new_row[key], 2)
                else:
                    new_row[key] = round_for_export(new_row[key], 3)

        return_row = new_row
        formatted.append(return_row)

    return formatted

# Colonne mantenute nel file all_runs.csv / all_runs.json.
# Le colonne tecniche di tracciamento interno come timestamp, parsed_ok,
# source_json, evaluated_file ed evaluated_file_found non vengono esportate.
ALL_RUNS_COLUMNS = [
    "circuit",
    "model",
    "input_type",
    "judge_model",
    "verdict",
    "total_score",
    "max_score",
    "normalized_score",
    "top1_correct",
    "top3_contains_correct",
    "major_errors_n",
    "hallucinations_n",
    "missed_points_n",
    "strengths_n",
    "circuit_understanding",
    "datasheet_use",
    "json_image_use",
    "diagnostic_accuracy",
    "cause_priority",
    "practical_checks",
    "hallucination_absence",
    "model_primary_cause",
    "short_explanation",
    "model_latency_seconds",
    "model_input_tokens",
    "model_output_tokens",
    "model_total_tokens",
    "model_reasoning_tokens",
    "model_cached_tokens",
    "model_cost_usd",
    "judge_latency_seconds",
    "judge_input_tokens",
    "judge_output_tokens",
    "judge_total_tokens",
    "judge_reasoning_tokens",
    "judge_cached_tokens",
    "judge_cost_usd",
]

ALL_RUNS_COLUMN_DESCRIPTIONS = {
    "circuit": "Identificativo del circuito valutato, ad esempio ic2, ic3, ic15.",
    "model": "Modello che ha prodotto la diagnosi sotto valutazione.",
    "input_type": "Tipo di input fornito al modello sotto test: solo JSON + datasheet oppure JSON + immagine + datasheet.",
    "judge_model": "Modello usato come judge automatico per valutare la risposta.",
    "verdict": "Giudizio sintetico del judge. Di solito 'Sì' indica risposta valida, 'Parziale' indica risposta utile ma incompleta o con errori.",
    "total_score": "Punteggio totale assegnato dal judge alla risposta del modello.",
    "max_score": "Punteggio massimo possibile per quella valutazione, normalmente 21.",
    "normalized_score": "Score normalizzato tra 0 e 1, calcolato come total_score / max_score.",
    "top1_correct": "Vale 1 se la causa principale indicata dal modello coincide con la causa principale attesa; vale 0 altrimenti.",
    "top3_contains_correct": "Vale 1 se la causa corretta compare almeno tra le prime tre ipotesi del modello; vale 0 altrimenti.",
    "major_errors_n": "Numero di errori gravi individuati dal judge nella risposta.",
    "hallucinations_n": "Numero di affermazioni non supportate, inventate o non deducibili dai dati forniti.",
    "missed_points_n": "Numero di aspetti importanti che il modello avrebbe dovuto menzionare ma ha omesso.",
    "strengths_n": "Numero di punti di forza individuati dal judge nella risposta.",
    "circuit_understanding": "Sotto-punteggio 0-3: quanto il modello ha capito struttura e funzione del circuito.",
    "datasheet_use": "Sotto-punteggio 0-3: quanto il modello ha usato correttamente le informazioni del datasheet.",
    "json_image_use": "Sotto-punteggio 0-3: quanto il modello ha usato correttamente JSON e, quando presente, immagine.",
    "diagnostic_accuracy": "Sotto-punteggio 0-3: accuratezza tecnica della diagnosi proposta.",
    "cause_priority": "Sotto-punteggio 0-3: corretto ordine di priorità delle cause probabili.",
    "practical_checks": "Sotto-punteggio 0-3: utilità e concretezza dei controlli pratici suggeriti.",
    "hallucination_absence": "Sotto-punteggio 0-3: assenza di allucinazioni o affermazioni non supportate.",
    "model_primary_cause": "Causa principale dichiarata dal modello sotto valutazione, secondo il judge.",
    "short_explanation": "Breve spiegazione del judge sul motivo del punteggio assegnato.",
    "model_latency_seconds": "Tempo di esecuzione della diagnosi del modello sotto test, in secondi.",
    "model_input_tokens": "Token di input consumati dal modello sotto test.",
    "model_output_tokens": "Token di output prodotti dal modello sotto test.",
    "model_total_tokens": "Token totali consumati dal modello sotto test.",
    "model_reasoning_tokens": "Token di reasoning del modello sotto test, quando disponibili.",
    "model_cached_tokens": "Token cached del modello sotto test, quando disponibili.",
    "model_cost_usd": "Costo stimato della singola diagnosi del modello sotto test, in dollari.",
    "judge_latency_seconds": "Tempo impiegato dal judge per valutare quella run, in secondi.",
    "judge_input_tokens": "Token di input consumati dal judge.",
    "judge_output_tokens": "Token di output prodotti dal judge.",
    "judge_total_tokens": "Token totali consumati dal judge.",
    "judge_reasoning_tokens": "Token di reasoning del judge, quando disponibili.",
    "judge_cached_tokens": "Token cached del judge, quando disponibili.",
    "judge_cost_usd": "Costo stimato della singola valutazione del judge, in dollari.",
}



# -----------------------------------------------------------------------------
# Utility
# -----------------------------------------------------------------------------

def safe_float(x: Any) -> Optional[float]:
    if x is None:
        return None
    try:
        if isinstance(x, str):
            x = x.strip().replace(",", ".")
        return float(x)
    except Exception:
        return None


def safe_int(x: Any) -> Optional[int]:
    if x is None:
        return None
    try:
        return int(float(str(x).strip()))
    except Exception:
        return None


def bool_to_int(x: Any) -> Optional[int]:
    if x is None:
        return None
    if isinstance(x, bool):
        return int(x)
    if isinstance(x, str):
        return 1 if x.strip().lower() in {"true", "sì", "si", "yes", "1"} else 0
    return int(bool(x))


def len_if_list(x: Any) -> int:
    return len(x) if isinstance(x, list) else 0


def parse_response_usage(usage: Any) -> Dict[str, Optional[int]]:
    """Estrae input/output/total/reasoning tokens da ResponseUsage string o dict."""
    out = {
        "input_tokens": None,
        "output_tokens": None,
        "total_tokens": None,
        "reasoning_tokens": None,
        "cached_tokens": None,
    }
    if not usage:
        return out

    if isinstance(usage, dict):
        out["input_tokens"] = safe_int(usage.get("input_tokens"))
        out["output_tokens"] = safe_int(usage.get("output_tokens"))
        out["total_tokens"] = safe_int(usage.get("total_tokens"))
        details_in = usage.get("input_tokens_details") or {}
        details_out = usage.get("output_tokens_details") or {}
        if isinstance(details_in, dict):
            out["cached_tokens"] = safe_int(details_in.get("cached_tokens"))
        if isinstance(details_out, dict):
            out["reasoning_tokens"] = safe_int(details_out.get("reasoning_tokens"))
        return out

    s = str(usage)
    patterns = {
        "input_tokens": r"\binput_tokens=(\d+)",
        "output_tokens": r"\boutput_tokens=(\d+)",
        "total_tokens": r"\btotal_tokens=(\d+)",
        "reasoning_tokens": r"\breasoning_tokens=(\d+)",
        "cached_tokens": r"\bcached_tokens=(\d+)",
    }
    for key, pat in patterns.items():
        m = re.search(pat, s)
        if m:
            out[key] = int(m.group(1))
    return out


def estimate_cost(model: str, input_tokens: Optional[int], output_tokens: Optional[int], price_table: Dict[str, Dict[str, float]]) -> Optional[float]:
    """Costo stimato se il modello è nel price table, altrimenti None."""
    if not model or input_tokens is None or output_tokens is None:
        return None
    price = price_table.get(model)
    if not price:
        return None
    return (input_tokens / 1_000_000) * price.get("input", 0.0) + (output_tokens / 1_000_000) * price.get("output", 0.0)


def find_json_files(root: Path) -> List[Path]:
    """Trova JSON dentro judge_results o judge_result."""
    files: List[Path] = []
    for folder_name in ("judge_results", "judge_result"):
        files.extend(root.glob(f"**/{folder_name}/*.json"))
    # Dedup e ordine stabile
    return sorted(set(files))


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def extract_runs_from_json(data: Any) -> List[Dict[str, Any]]:
    """Ritorna tutte le run {metadata, judge_result, judge_usage} trovate."""
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict) and "metadata" in x and "judge_result" in x]

    if isinstance(data, dict):
        if "metadata" in data and "judge_result" in data:
            return [data]
        # Supporto per possibili wrapper diversi
        for key in ("runs", "results", "evaluations", "items", "data"):
            val = data.get(key)
            if isinstance(val, list):
                runs = [x for x in val if isinstance(x, dict) and "metadata" in x and "judge_result" in x]
                if runs:
                    return runs
    return []


def resolve_evaluated_file(evaluated_file: str, root: Path) -> Optional[Path]:
    """Prova a risolvere il path Windows dell'output modello; fallback su ricerca per basename."""
    if not evaluated_file:
        return None

    p = Path(evaluated_file)
    if p.exists():
        return p

    # Path Windows su Linux: cerca solo il nome del file dentro root
    basename = evaluated_file.replace("\\", "/").split("/")[-1]
    if not basename:
        return None
    matches = list(root.rglob(basename))
    if matches:
        return matches[0]
    return None


def parse_model_output_txt(path: Optional[Path]) -> Dict[str, Optional[float | int | str]]:
    """Legge LATENCY_SECONDS e USAGE dal .txt prodotto dal modello sotto valutazione."""
    out: Dict[str, Optional[float | int | str]] = {
        "model_latency_seconds": None,
        "model_input_tokens": None,
        "model_output_tokens": None,
        "model_total_tokens": None,
        "model_reasoning_tokens": None,
        "model_cached_tokens": None,
    }
    if path is None or not path.exists():
        return out

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return out

    m = re.search(r"LATENCY_SECONDS:\s*([0-9]+(?:\.[0-9]+)?)", text)
    if m:
        out["model_latency_seconds"] = float(m.group(1))

    m = re.search(r"USAGE:\s*\n\s*(ResponseUsage\([^\n]+\))", text)
    if not m:
        m = re.search(r"(ResponseUsage\([^\n]+\))", text)
    if m:
        usage = parse_response_usage(m.group(1))
        out["model_input_tokens"] = usage["input_tokens"]
        out["model_output_tokens"] = usage["output_tokens"]
        out["model_total_tokens"] = usage["total_tokens"]
        out["model_reasoning_tokens"] = usage["reasoning_tokens"]
        out["model_cached_tokens"] = usage["cached_tokens"]

    return out


def row_from_run(run: Dict[str, Any], json_path: Path, root: Path) -> Dict[str, Any]:
    meta = run.get("metadata", {}) or {}
    jr = run.get("judge_result", {}) or {}
    scores = jr.get("scores", {}) or {}

    evaluated_file = meta.get("evaluated_file", "")
    evaluated_path = resolve_evaluated_file(evaluated_file, root)
    model_output = parse_model_output_txt(evaluated_path)

    judge_usage = parse_response_usage(run.get("judge_usage"))

    model = meta.get("model_under_test", "")
    judge_model = meta.get("judge_model", "")

    row: Dict[str, Any] = {
        "circuit": meta.get("circuit", ""),
        "model": model,
        "input_type": meta.get("input_type", ""),
        "judge_model": judge_model,
        "_timestamp": meta.get("timestamp", ""),
        "verdict": jr.get("verdict", ""),
        "total_score": safe_float(jr.get("total_score")),
        "max_score": safe_float(jr.get("max_score")),
        "normalized_score": safe_float(jr.get("normalized_score")),
        "top1_correct": bool_to_int(jr.get("top1_correct")),
        "top3_contains_correct": bool_to_int(jr.get("top3_contains_correct")),
        "major_errors_n": len_if_list(jr.get("major_errors")),
        "hallucinations_n": len_if_list(jr.get("hallucinations")),
        "missed_points_n": len_if_list(jr.get("missed_important_points")),
        "strengths_n": len_if_list(jr.get("strengths")),
        "model_primary_cause": jr.get("model_primary_cause", ""),
        "short_explanation": jr.get("short_explanation", ""),
        "judge_latency_seconds": safe_float(meta.get("judge_latency_seconds")),
        "judge_input_tokens": judge_usage["input_tokens"],
        "judge_output_tokens": judge_usage["output_tokens"],
        "judge_total_tokens": judge_usage["total_tokens"],
        "judge_reasoning_tokens": judge_usage["reasoning_tokens"],
        "judge_cached_tokens": judge_usage["cached_tokens"],
    }

    for c in CRITERIA:
        row[c] = safe_float(scores.get(c))

    row.update(model_output)

    row["model_cost_usd"] = estimate_cost(
        model,
        safe_int(row.get("model_input_tokens")),
        safe_int(row.get("model_output_tokens")),
        MODEL_PRICES_PER_1M,
    )
    row["judge_cost_usd"] = estimate_cost(
        judge_model,
        safe_int(row.get("judge_input_tokens")),
        safe_int(row.get("judge_output_tokens")),
        JUDGE_PRICES_PER_1M,
    )

    return row


def write_csv(path: Path, rows: List[Dict[str, Any]], fieldnames: Optional[List[str]] = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        keys = []
        seen = set()
        for r in rows:
            for k in r.keys():
                if k not in seen:
                    keys.append(k)
                    seen.add(k)
        fieldnames = keys
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def write_data_dictionary(out_dir: Path) -> None:
    """Crea un dizionario delle colonne per all_runs."""
    rows = [
        {
            "column": col,
            "description": ALL_RUNS_COLUMN_DESCRIPTIONS.get(col, ""),
        }
        for col in ALL_RUNS_COLUMNS
    ]
    write_csv(out_dir / "all_runs_data_dictionary.csv", rows, ["column", "description"])

    md_lines = [
        "# Dizionario colonne — all_runs",
        "",
        "| Colonna | Significato |",
        "| --- | --- |",
    ]
    for row in rows:
        col = str(row["column"]).replace("|", "\\|")
        desc = str(row["description"]).replace("|", "\\|")
        md_lines.append(f"| `{col}` | {desc} |")

    (out_dir / "all_runs_data_dictionary.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")


def numeric_values(rows: List[Dict[str, Any]], key: str) -> List[float]:
    vals = []
    for r in rows:
        v = safe_float(r.get(key))
        if v is not None and not math.isnan(v):
            vals.append(v)
    return vals



def sum_numeric(rows: List[Dict[str, Any]], key: str) -> float:
    """Somma una colonna numerica ignorando celle vuote/non numeriche."""
    return sum(numeric_values(rows, key))


def make_cost_summary(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Crea una riga riassuntiva con i costi totali dell'esperimento."""
    model_total = sum_numeric(rows, "model_cost_usd")
    judge_total = sum_numeric(rows, "judge_cost_usd")
    return [
        {
            "N": len(rows),
            "model_cost_usd_total": model_total,
            "judge_cost_usd_total": judge_total,
            "total_cost_usd": model_total + judge_total,
            "note": "Somma dei costi stimati sulle run aggregate. Usa --dedupe per evitare doppi conteggi se sono presenti sia summary JSON sia file judge singoli.",
        }
    ]


def make_cost_summary_by(rows: List[Dict[str, Any]], group_keys: List[str]) -> List[Dict[str, Any]]:
    """Crea riepiloghi costo per circuito/modello/input type."""
    groups: Dict[Tuple[Any, ...], List[Dict[str, Any]]] = defaultdict(list)
    for r in rows:
        groups[tuple(r.get(k, "") for k in group_keys)].append(r)

    out: List[Dict[str, Any]] = []
    for key_tuple, rs in sorted(groups.items()):
        row = {k: v for k, v in zip(group_keys, key_tuple)}
        row["N"] = len(rs)
        row["model_cost_usd_total"] = sum_numeric(rs, "model_cost_usd")
        row["judge_cost_usd_total"] = sum_numeric(rs, "judge_cost_usd")
        row["total_cost_usd"] = row["model_cost_usd_total"] + row["judge_cost_usd_total"]
        out.append(row)
    return out


def bool_values(rows: List[Dict[str, Any]], key: str) -> List[int]:
    vals = []
    for r in rows:
        v = r.get(key)
        if v is not None and v != "":
            vals.append(int(v))
    return vals


def aggregate(rows: List[Dict[str, Any]], group_keys: List[str]) -> List[Dict[str, Any]]:
    groups: Dict[Tuple[Any, ...], List[Dict[str, Any]]] = defaultdict(list)
    for r in rows:
        groups[tuple(r.get(k, "") for k in group_keys)].append(r)

    out: List[Dict[str, Any]] = []
    for key_tuple, rs in sorted(groups.items()):
        row = {k: v for k, v in zip(group_keys, key_tuple)}
        row["N"] = len(rs)

        for metric in [
            "total_score", "normalized_score", "major_errors_n", "hallucinations_n",
            "model_latency_seconds", "model_input_tokens", "model_output_tokens", "model_total_tokens",
            "model_cost_usd", "judge_latency_seconds", "judge_total_tokens", "judge_cost_usd",
        ]:
            vals = numeric_values(rs, metric)
            if vals:
                row[f"{metric}_mean"] = mean(vals)
                row[f"{metric}_median"] = median(vals)
                row[f"{metric}_std"] = pstdev(vals) if len(vals) > 1 else 0.0
            else:
                row[f"{metric}_mean"] = ""
                row[f"{metric}_median"] = ""
                row[f"{metric}_std"] = ""

        for b in ["top1_correct", "top3_contains_correct"]:
            vals = bool_values(rs, b)
            row[f"{b}_rate"] = mean(vals) if vals else ""

        for c in CRITERIA:
            vals = numeric_values(rs, c)
            row[f"{c}_mean"] = mean(vals) if vals else ""

        out.append(row)
    return out


def make_deltas(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Delta JSON+img - JSON per ogni circuito e modello."""
    by_key: Dict[Tuple[str, str], Dict[str, Dict[str, Any]]] = defaultdict(dict)
    for r in rows:
        circ = str(r.get("circuit", ""))
        model = str(r.get("model", ""))
        inp = str(r.get("input_type", ""))
        by_key[(circ, model)][inp] = r

    out = []
    for (circ, model), d in sorted(by_key.items()):
        r_json = d.get("JSON + datasheet")
        r_img = d.get("JSON + immagine + datasheet")
        if not r_json or not r_img:
            continue
        score_json = safe_float(r_json.get("total_score"))
        score_img = safe_float(r_img.get("total_score"))
        if score_json is None or score_img is None:
            continue
        out.append({
            "circuit": circ,
            "model": model,
            "score_json": score_json,
            "score_json_img": score_img,
            "delta_score_img_minus_json": score_img - score_json,
            "top1_json": r_json.get("top1_correct"),
            "top1_json_img": r_img.get("top1_correct"),
            "top3_json": r_json.get("top3_contains_correct"),
            "top3_json_img": r_img.get("top3_contains_correct"),
            "errors_json": r_json.get("major_errors_n"),
            "errors_json_img": r_img.get("major_errors_n"),
            "hallucinations_json": r_json.get("hallucinations_n"),
            "hallucinations_json_img": r_img.get("hallucinations_n"),
            "latency_json": r_json.get("model_latency_seconds"),
            "latency_json_img": r_img.get("model_latency_seconds"),
            "cost_json": r_json.get("model_cost_usd"),
            "cost_json_img": r_img.get("model_cost_usd"),
        })
    return out


def make_criteria_long(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for r in rows:
        for c in CRITERIA:
            out.append({
                "circuit": r.get("circuit", ""),
                "model": r.get("model", ""),
                "input_type": r.get("input_type", ""),
                "criterion": c,
                "score": r.get(c, ""),
                "total_score": r.get("total_score", ""),
            })
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggrega risultati judge di tutti i circuiti.")
    parser.add_argument("--root", required=True, help="Cartella batch_v1 che contiene ic2, ic3, ic7, ...")
    parser.add_argument("--out", default=None, help="Cartella output. Default: <root>/_aggregate")
    parser.add_argument("--dedupe", action="store_true", help="Deduplica per circuito+modello+input_type tenendo timestamp più recente")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out).expanduser().resolve() if args.out else root / "_aggregate"

    json_files = find_json_files(root)
    all_rows: List[Dict[str, Any]] = []

    for jp in json_files:
        try:
            data = load_json(jp)
            runs = extract_runs_from_json(data)
        except Exception as e:
            print(f"[WARN] Non riesco a leggere {jp}: {e}")
            continue
        if not runs:
            print(f"[WARN] Nessuna run valida in {jp}")
            continue
        for run in runs:
            all_rows.append(row_from_run(run, jp, root))

    if args.dedupe:
        best: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
        for r in all_rows:
            k = (str(r.get("circuit", "")), str(r.get("model", "")), str(r.get("input_type", "")))
            # timestamp ISO-like: string compare works sufficiently here
            if k not in best or str(r.get("_timestamp", "")) > str(best[k].get("_timestamp", "")):
                best[k] = r
        all_rows = list(best.values())

    all_rows = sorted(all_rows, key=lambda r: (str(r.get("circuit", "")), str(r.get("model", "")), str(r.get("input_type", ""))))

    # Esporta all_runs solo con le colonne utili per analisi/grafici.
    # Le colonne tecniche di tracciamento interno non vengono scritte.
    # I valori numerici vengono arrotondati solo in export, non prima dei calcoli.
    all_rows_rounded = format_rows_for_export(all_rows)

    all_rows_export = [
        {col: r.get(col, "") for col in ALL_RUNS_COLUMNS}
        for r in all_rows_rounded
    ]

    write_json(out_dir / "all_runs.json", all_rows_export)
    write_csv(out_dir / "all_runs.csv", all_rows_export, ALL_RUNS_COLUMNS)
    write_data_dictionary(out_dir)

    # Aggregazioni calcolate sui dati non arrotondati, poi arrotondate in export.
    agg_by_model = format_rows_for_export(aggregate(all_rows, ["model"]))
    agg_by_model_input = format_rows_for_export(aggregate(all_rows, ["model", "input_type"]))
    agg_by_circuit = format_rows_for_export(aggregate(all_rows, ["circuit"]))
    agg_by_circuit_input = format_rows_for_export(aggregate(all_rows, ["circuit", "input_type"]))
    agg_by_input_type = format_rows_for_export(aggregate(all_rows, ["input_type"]))
    deltas = format_rows_for_export(make_deltas(all_rows))
    criteria_long = format_rows_for_export(make_criteria_long(all_rows))
    cost_summary = format_rows_for_export(make_cost_summary(all_rows))
    cost_summary_by_circuit = format_rows_for_export(make_cost_summary_by(all_rows, ["circuit"]))
    cost_summary_by_model = format_rows_for_export(make_cost_summary_by(all_rows, ["model"]))
    cost_summary_by_input_type = format_rows_for_export(make_cost_summary_by(all_rows, ["input_type"]))

    write_csv(out_dir / "aggregate_by_model.csv", agg_by_model)
    write_csv(out_dir / "aggregate_by_model_input.csv", agg_by_model_input)
    write_csv(out_dir / "aggregate_by_circuit.csv", agg_by_circuit)
    write_csv(out_dir / "aggregate_by_circuit_input.csv", agg_by_circuit_input)
    write_csv(out_dir / "aggregate_by_input_type.csv", agg_by_input_type)
    write_csv(out_dir / "deltas_image_vs_json.csv", deltas)
    write_csv(out_dir / "criteria_long.csv", criteria_long)
    write_csv(out_dir / "cost_summary.csv", cost_summary, ["N", "model_cost_usd_total", "judge_cost_usd_total", "total_cost_usd", "note"])
    write_json(out_dir / "cost_summary.json", cost_summary)
    write_csv(out_dir / "cost_summary_by_circuit.csv", cost_summary_by_circuit)
    write_csv(out_dir / "cost_summary_by_model.csv", cost_summary_by_model)
    write_csv(out_dir / "cost_summary_by_input_type.csv", cost_summary_by_input_type)

    print("\nAggregazione completata.")
    print(f"Root: {root}")
    print(f"File JSON judge trovati: {len(json_files)}")
    print(f"Run aggregate: {len(all_rows)}")
    print(f"Output: {out_dir}")
    print("\nFile creati:")
    for p in sorted(out_dir.glob("*")):
        print(f"- {p.name}")

    model_cost_total = sum_numeric(all_rows, "model_cost_usd")
    judge_cost_total = sum_numeric(all_rows, "judge_cost_usd")
    total_cost = model_cost_total + judge_cost_total
    print("\nCosti stimati:")
    print(f"- Totale diagnosi modelli: ${model_cost_total:.6f}")
    print(f"- Totale judge:            ${judge_cost_total:.6f}")
    print(f"- Totale complessivo:     ${total_cost:.6f}")

    missing_latency = sum(1 for r in all_rows if r.get("model_latency_seconds") in (None, ""))
    if missing_latency:
        print(f"\n[WARN] {missing_latency} run senza latenza modello: controlla che i file .txt originali siano presenti sotto --root.")

    if not MODEL_PRICES_PER_1M:
        print("\n[INFO] MODEL_PRICES_PER_1M è vuoto: model_cost_usd resterà vuoto.")
        print("       Se vuoi i costi, copia nel dizionario i prezzi usati in make_judge_tables.py.")
    if not JUDGE_PRICES_PER_1M:
        print("[INFO] JUDGE_PRICES_PER_1M è vuoto: judge_cost_usd resterà vuoto.")


if __name__ == "__main__":
    main()
