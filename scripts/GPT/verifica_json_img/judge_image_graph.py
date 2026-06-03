from __future__ import annotations

import argparse
import base64
import csv
import json
import mimetypes
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from dotenv import load_dotenv
from openai import OpenAI


# ============================================================
# Judge Image <-> Graph JSON
#
# Input:
#   verify_json_img/
#     prompt.txt
#     batchA/images/a01.png
#     batchA/json/a01.json
#     batchB/images/...
#     batchB/json/...
#     batchC1/images/...
#     batchC1/json/...
#     batchC2/images/...
#     batchC2/json/...
#
# Output predefinito:
#   Se si analizza un solo batch:
#     verify_json_img/batchA/output_gpt5_5/
#     verify_json_img/batchB/output_gpt5_5/
#     verify_json_img/batchC1/output_gpt5_5/
#     verify_json_img/batchC2/output_gpt5_5/
#
#   Se si analizzano piu batch insieme senza --out-dir:
#     verify_json_img/output_gpt5_5/
#
#   Contenuto:
#     judge_results.jsonl
#     judge_results.csv
#     judge_report.md
#     raw_responses/*.json
#     plots/*.png
# ============================================================

DEFAULT_MODEL = "gpt-5.5"
DEFAULT_OUTPUT_DIR_NAME = "output_gpt5_5"
IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".webp"]
VALID_BATCH_LABELS = {"A", "B", "C1", "C2", "unknown"}
DECISION_LEVELS = ["VERY_HIGH", "HIGH", "MEDIUM", "LOW"]
LEGACY_DECISION_MAP = {
    "PASS": "VERY_HIGH",
    "MINOR_ISSUES": "HIGH",
    "NEEDS_PATCH": "MEDIUM",
    "FAIL": "LOW",
}

SCRIPT_DIR = Path(__file__).resolve().parent
# Se lo script si trova in experiment_ai/scripts/GPT/verifica_json_img,
# parents[3] punta a experiment_ai. Se la struttura è diversa, usare --root.
try:
    DEFAULT_EXPERIMENT_ROOT = Path(__file__).resolve().parents[3]
except IndexError:
    DEFAULT_EXPERIMENT_ROOT = Path.cwd()
DEFAULT_VERIFY_ROOT = DEFAULT_EXPERIMENT_ROOT / "verify_json_img"


JUDGE_RESULT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "circuit_id": {"type": "string"},
        "batch": {"type": "string", "enum": ["A", "B", "C1", "C2", "unknown"]},
        "image_file": {"type": "string"},
        "json_file": {"type": "string"},
        "image_graph_fidelity_score": {"type": "integer", "minimum": 0, "maximum": 100},
        "decision": {"type": "string", "enum": DECISION_LEVELS},
        "usable_as_graph_base": {"type": "boolean"},
        "scores": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "components": {"type": "integer", "minimum": 0, "maximum": 25},
                "terminals_pins": {"type": "integer", "minimum": 0, "maximum": 20},
                "graph_connections": {"type": "integer", "minimum": 0, "maximum": 45},
                "visible_semantics": {"type": "integer", "minimum": 0, "maximum": 10},
            },
            "required": ["components", "terminals_pins", "graph_connections", "visible_semantics"],
        },
        "error_counts": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "critical": {"type": "integer", "minimum": 0},
                "major": {"type": "integer", "minimum": 0},
                "minor": {"type": "integer", "minimum": 0},
            },
            "required": ["critical", "major", "minor"],
        },
        "critical_errors": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "type": {"type": "string"},
                    "description": {"type": "string"},
                    "image_evidence": {"type": "string"},
                    "json_evidence": {"type": "string"},
                },
                "required": ["type", "description", "image_evidence", "json_evidence"],
            },
        },
        "major_errors": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "type": {"type": "string"},
                    "description": {"type": "string"},
                    "image_evidence": {"type": "string"},
                    "json_evidence": {"type": "string"},
                },
                "required": ["type", "description", "image_evidence", "json_evidence"],
            },
        },
        "minor_errors": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "type": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["type", "description"],
            },
        },
        "missing_from_json": {"type": "array", "items": {"type": "string"}},
        "extra_in_json": {"type": "array", "items": {"type": "string"}},
        "wrong_graph_connections": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "expected_from_image": {"type": "string"},
                    "found_in_json": {"type": "string"},
                    "severity": {"type": "string", "enum": ["critical", "major", "minor"]},
                },
                "required": ["expected_from_image", "found_in_json", "severity"],
            },
        },
        "uncertain_points": {"type": "array", "items": {"type": "string"}},
        "short_explanation": {"type": "string"},
    },
    "required": [
        "circuit_id",
        "batch",
        "image_file",
        "json_file",
        "image_graph_fidelity_score",
        "decision",
        "usable_as_graph_base",
        "scores",
        "error_counts",
        "critical_errors",
        "major_errors",
        "minor_errors",
        "missing_from_json",
        "extra_in_json",
        "wrong_graph_connections",
        "uncertain_points",
        "short_explanation",
    ],
}


@dataclass(frozen=True)
class CircuitPair:
    circuit_id: str
    batch_label: str
    batch_dir: Path
    image_path: Path
    json_path: Path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def encode_image_data_url(image_path: Path) -> str:
    mime_type, _ = mimetypes.guess_type(str(image_path))
    if mime_type is None:
        mime_type = "image/jpeg"

    with image_path.open("rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    return f"data:{mime_type};base64,{encoded}"


def safe_json_parse(text: str) -> Any:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()
    return json.loads(cleaned)


def normalize_decision_label(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    if text in DECISION_LEVELS or text == "PARSE_ERROR":
        return text
    return LEGACY_DECISION_MAP.get(text, text)


def infer_batch_label(batch_dir_name: str) -> str:
    name = batch_dir_name.strip()
    lower = name.lower()

    if lower.startswith("batch"):
        label = name[5:]
    else:
        label = name

    label = label.upper()
    return label if label in VALID_BATCH_LABELS else "unknown"


def normalize_batch_arg(batch: Optional[str]) -> Optional[str]:
    if not batch:
        return None
    b = batch.strip()
    if b.lower().startswith("batch"):
        b = b[5:]
    return b.upper()


def find_image_for_stem(images_dir: Path, stem: str) -> Optional[Path]:
    for ext in IMAGE_EXTENSIONS:
        candidate = images_dir / f"{stem}{ext}"
        if candidate.exists():
            return candidate
    # fallback case-insensitive
    candidates = [p for p in images_dir.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS]
    for path in candidates:
        if path.stem.lower() == stem.lower():
            return path
    return None


def discover_pairs(root: Path, batch_filter: Optional[str], only_ids: Optional[set[str]]) -> List[CircuitPair]:
    if not root.exists():
        raise FileNotFoundError(f"Root non trovata: {root}")

    pairs: List[CircuitPair] = []
    batch_dirs = sorted([p for p in root.iterdir() if p.is_dir()])

    for batch_dir in batch_dirs:
        images_dir = batch_dir / "images"
        json_dir = batch_dir / "json"
        if not images_dir.exists() or not json_dir.exists():
            continue

        batch_label = infer_batch_label(batch_dir.name)
        if batch_filter and batch_label != batch_filter:
            continue

        for json_path in sorted(json_dir.glob("*.json")):
            circuit_id = json_path.stem
            if only_ids and circuit_id.lower() not in only_ids:
                continue

            image_path = find_image_for_stem(images_dir, circuit_id)
            if image_path is None:
                print(f"[WARN] immagine non trovata per {json_path}", file=sys.stderr)
                continue

            pairs.append(
                CircuitPair(
                    circuit_id=circuit_id,
                    batch_label=batch_label,
                    batch_dir=batch_dir,
                    image_path=image_path,
                    json_path=json_path,
                )
            )

    return pairs


def build_user_text(prompt_template: str, pair: CircuitPair, graph_json_text: str) -> str:
    return f"""{prompt_template.strip()}

---
METADATI DA USARE NELL'OUTPUT
- circuit_id: {pair.circuit_id}
- batch: {pair.batch_label}
- image_file: {pair.image_path.name}
- json_file: {pair.json_path.name}

IMPORTANTE:
- Usa esattamente questi metadati nei campi circuit_id, batch, image_file e json_file.
- Valuta il Graph JSON originale riportato sotto.
- Non trasformare il campo graph in altri formati.

GRAPH JSON ORIGINALE:
```json
{graph_json_text}
```
"""


def call_judge(
    client: OpenAI,
    model: str,
    prompt_template: str,
    pair: CircuitPair,
    image_detail: str,
    max_output_tokens: int,
    reasoning_effort: str,
) -> Dict[str, Any]:
    graph_json_text = read_text(pair.json_path)

    # Controllo solo tecnico: il file deve essere JSON valido.
    # Il contenuto non viene modificato né trasformato.
    try:
        json.loads(graph_json_text)
        input_json_valid = True
        input_json_error = None
    except Exception as exc:
        input_json_valid = False
        input_json_error = str(exc)

    user_text = build_user_text(prompt_template, pair, graph_json_text)
    image_data_url = encode_image_data_url(pair.image_path)

    request_kwargs: Dict[str, Any] = {
        "model": model,
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": user_text},
                    {"type": "input_image", "image_url": image_data_url, "detail": image_detail},
                ],
            }
        ],
        "max_output_tokens": max_output_tokens,
        "text": {
            "format": {
                "type": "json_schema",
                "name": "image_graph_judge_result",
                "strict": True,
                "schema": JUDGE_RESULT_SCHEMA,
            }
        },
    }

    if model.startswith("gpt-5"):
        request_kwargs["reasoning"] = {"effort": reasoning_effort}

    start = time.perf_counter()
    response = client.responses.create(**request_kwargs)
    latency = time.perf_counter() - start

    raw_text = (response.output_text or "").strip()

    parsed_ok = True
    parse_error = None
    try:
        judge_result = safe_json_parse(raw_text)
    except Exception as exc:
        parsed_ok = False
        parse_error = str(exc)
        judge_result = {
            "parse_error": parse_error,
            "raw_judge_output": raw_text,
        }

    return {
        "metadata": {
            "circuit_id": pair.circuit_id,
            "batch": pair.batch_label,
            "batch_dir": pair.batch_dir.name,
            "image_path": str(pair.image_path),
            "json_path": str(pair.json_path),
            "image_file": pair.image_path.name,
            "json_file": pair.json_path.name,
            "judge_model": model,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "judge_latency_seconds": round(latency, 3),
            "input_json_valid": input_json_valid,
            "input_json_error": input_json_error,
            "parsed_ok": parsed_ok,
            "parse_error": parse_error,
        },
        "judge_usage": str(response.usage) if response.usage else None,
        "judge_result": judge_result,
        "raw_model_output": raw_text,
    }


def flatten_for_csv(record: Dict[str, Any]) -> Dict[str, Any]:
    meta = record.get("metadata", {})
    jr = record.get("judge_result", {})

    scores = jr.get("scores", {}) if isinstance(jr, dict) else {}
    counts = jr.get("error_counts", {}) if isinstance(jr, dict) else {}

    return {
        "circuit_id": jr.get("circuit_id", meta.get("circuit_id", "")),
        "batch": jr.get("batch", meta.get("batch", "")),
        "image_file": jr.get("image_file", meta.get("image_file", "")),
        "json_file": jr.get("json_file", meta.get("json_file", "")),
        "score": jr.get("image_graph_fidelity_score", ""),
        "decision": normalize_decision_label(
            jr.get("decision", "PARSE_ERROR" if not meta.get("parsed_ok", True) else "")
        ),
        "usable_as_graph_base": jr.get("usable_as_graph_base", ""),
        "components_score": scores.get("components", ""),
        "terminals_pins_score": scores.get("terminals_pins", ""),
        "graph_connections_score": scores.get("graph_connections", ""),
        "visible_semantics_score": scores.get("visible_semantics", ""),
        "critical_errors_count": counts.get("critical", ""),
        "major_errors_count": counts.get("major", ""),
        "minor_errors_count": counts.get("minor", ""),
        "missing_from_json_count": len(jr.get("missing_from_json", [])) if isinstance(jr.get("missing_from_json", []), list) else "",
        "extra_in_json_count": len(jr.get("extra_in_json", [])) if isinstance(jr.get("extra_in_json", []), list) else "",
        "wrong_graph_connections_count": len(jr.get("wrong_graph_connections", [])) if isinstance(jr.get("wrong_graph_connections", []), list) else "",
        "judge_latency_seconds": meta.get("judge_latency_seconds", ""),
        "input_json_valid": meta.get("input_json_valid", ""),
        "parsed_ok": meta.get("parsed_ok", ""),
        "short_explanation": jr.get("short_explanation", "") if isinstance(jr, dict) else "",
    }


def save_jsonl(path: Path, records: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def save_csv(path: Path, records: List[Dict[str, Any]]) -> None:
    rows = [flatten_for_csv(r) for r in records]
    if not rows:
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def save_markdown_report(path: Path, records: List[Dict[str, Any]]) -> None:
    rows = [flatten_for_csv(r) for r in records]

    lines: List[str] = []
    lines.append("# Report verifica immagine ↔ Graph JSON")
    lines.append("")
    lines.append(f"Generato: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    if rows:
        lines.append("## Tabella sintetica")
        lines.append("")
        lines.append("| Circuito | Batch | Score | Fedeltà | Critici | Maggiori | Minori | Usabile come graph base |")
        lines.append("|---|---:|---:|---|---:|---:|---:|---|")
        for row in rows:
            lines.append(
                f"| {row['circuit_id']} | {row['batch']} | {row['score']} | {row['decision']} | "
                f"{row['critical_errors_count']} | {row['major_errors_count']} | {row['minor_errors_count']} | "
                f"{row['usable_as_graph_base']} |"
            )
        lines.append("")

    lines.append("## Dettagli per circuito")
    lines.append("")
    for record in records:
        meta = record.get("metadata", {})
        jr = record.get("judge_result", {})
        cid = jr.get("circuit_id", meta.get("circuit_id", "unknown"))
        lines.append(f"### {cid}")
        lines.append("")
        if not meta.get("parsed_ok", True):
            lines.append(f"Parse error: `{meta.get('parse_error')}`")
            lines.append("")
            continue

        lines.append(f"- Batch: `{jr.get('batch', '')}`")
        lines.append(f"- Score: `{jr.get('image_graph_fidelity_score', '')}`")
        lines.append(f"- Fedeltà: `{normalize_decision_label(jr.get('decision', ''))}`")
        lines.append(f"- Usabile come graph base: `{jr.get('usable_as_graph_base', '')}`")
        lines.append(f"- Spiegazione: {jr.get('short_explanation', '')}")
        lines.append("")

        for label, key in [
            ("Errori critici", "critical_errors"),
            ("Errori maggiori", "major_errors"),
            ("Errori minori", "minor_errors"),
            ("Punti incerti", "uncertain_points"),
        ]:
            values = jr.get(key, [])
            if values:
                lines.append(f"**{label}:**")
                for value in values:
                    if isinstance(value, dict):
                        desc = value.get("description") or value.get("expected_from_image") or str(value)
                    else:
                        desc = str(value)
                    lines.append(f"- {desc}")
                lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def make_plots(csv_path: Path, plots_dir: Path) -> None:
    try:
        import pandas as pd
        import matplotlib.pyplot as plt
    except Exception as exc:
        print(f"[WARN] plot saltati: pandas/matplotlib non disponibili ({exc})", file=sys.stderr)
        return

    if not csv_path.exists():
        return

    df = pd.read_csv(csv_path)
    if df.empty:
        return

    plots_dir.mkdir(parents=True, exist_ok=True)

    # Converte colonne numeriche dove possibile.
    numeric_cols = [
        "score",
        "components_score",
        "terminals_pins_score",
        "graph_connections_score",
        "visible_semantics_score",
        "critical_errors_count",
        "major_errors_count",
        "minor_errors_count",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    palette = {
        "VERY_HIGH": "#2F8F5B",
        "HIGH": "#79A83B",
        "MEDIUM": "#E89A00",
        "LOW": "#C66A1C",
        "PARSE_ERROR": "#6C757D",
    }
    edge_palette = {
        "VERY_HIGH": "#236B43",
        "HIGH": "#567625",
        "MEDIUM": "#A86D00",
        "LOW": "#8A4713",
        "PARSE_ERROR": "#495057",
    }
    subscore_palette = {
        "components_score": "#3A86FF",
        "terminals_pins_score": "#8338EC",
        "graph_connections_score": "#FB5607",
        "visible_semantics_score": "#2A9D8F",
    }
    error_palette = {
        "critical_errors_count": "#9B2226",
        "major_errors_count": "#D95D39",
        "minor_errors_count": "#F0A202",
    }

    def style_axes(ax) -> None:
        ax.set_facecolor("#FFFDF8")
        ax.grid(axis="x", color="#E8E2D8", linewidth=0.8, alpha=0.9)
        ax.set_axisbelow(True)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#B7ADA1")
        ax.spines["bottom"].set_color("#B7ADA1")

    # 1) Score per circuito con fedeltà
    score_df = df.dropna(subset=["score"]).copy()
    if not score_df.empty:
        if "decision" in score_df.columns:
            score_df["decision"] = score_df["decision"].map(normalize_decision_label)
        score_df = score_df.sort_values(["score", "batch", "circuit_id"], ascending=[True, True, True])
        labels = score_df["batch"].astype(str) + "/" + score_df["circuit_id"].astype(str)
        colors = [palette.get(decision, "#6C757D") for decision in score_df.get("decision", [])]

        fig_height = max(5.6, 0.52 * len(score_df))
        fig, ax = plt.subplots(figsize=(11.5, fig_height))
        fig.patch.set_facecolor("#FFF8F0")
        ax.axvspan(0, 60, color="#F1DDC5", alpha=0.3, zorder=0)
        ax.axvspan(60, 80, color="#F4E8BF", alpha=0.26, zorder=0)
        ax.axvspan(80, 90, color="#DCECD7", alpha=0.24, zorder=0)
        ax.axvspan(90, 100, color="#CDE4D3", alpha=0.28, zorder=0)
        bar_edges = [edge_palette.get(decision, "#6C757D") for decision in score_df.get("decision", [])]
        bars = ax.barh(
            labels,
            score_df["score"],
            color=colors,
            edgecolor=bar_edges,
            linewidth=1.2,
            height=0.78,
        )
        for threshold in (60, 80, 90):
            ax.axvline(threshold, linewidth=0.6, color="#D8C9B8", alpha=0.45, zorder=1)
        ax.set_xlim(0, 100)
        ax.set_xlabel("Image-Graph fidelity score")
        ax.set_ylabel("Circuito")
        ax.set_title("Score per circuito con fedeltà")
        style_axes(ax)
        ax.invert_yaxis()
        for bar, score, decision in zip(bars, score_df["score"], score_df["decision"]):
            ax.text(
                min(float(score) + 1.2, 98.5),
                bar.get_y() + bar.get_height() / 2,
                f"{int(score)}  {decision}",
                va="center",
                ha="left",
                fontsize=9.5,
                fontweight="medium",
                color="#3A332D",
            )
        fig.tight_layout()
        fig.savefig(plots_dir / "01_score_per_circuito.png", dpi=200)
        plt.close(fig)

    # 2) Profilo errori per circuito
    error_cols = ["critical_errors_count", "major_errors_count", "minor_errors_count"]
    available_error_cols = [c for c in error_cols if c in df.columns]
    errors_df = df.dropna(subset=available_error_cols, how="all").copy() if available_error_cols else df.iloc[0:0].copy()
    if available_error_cols and not errors_df.empty:
        if "decision" in errors_df.columns:
            errors_df["decision"] = errors_df["decision"].map(normalize_decision_label)
        errors_df = errors_df.sort_values(
            available_error_cols + ["score", "batch", "circuit_id"],
            ascending=[False] * len(available_error_cols) + [True, True, True],
        )
        labels = errors_df["batch"].astype(str) + "/" + errors_df["circuit_id"].astype(str)

        fig_height = max(5.6, 0.52 * len(errors_df))
        fig, ax = plt.subplots(figsize=(11.5, fig_height))
        fig.patch.set_facecolor("#FFF8F0")
        left = None
        for col in error_cols:
            if col not in errors_df.columns:
                continue
            values = errors_df[col].fillna(0)
            bars = ax.barh(
                labels,
                values,
                left=left,
                color=error_palette[col],
                edgecolor="#8A8175",
                linewidth=0.5,
                label=col.replace("_count", "").replace("_", " "),
            )
            for bar, value in zip(bars, values):
                if value > 0:
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        bar.get_y() + bar.get_height() / 2,
                        f"{int(value)}",
                        ha="center",
                        va="center",
                        fontsize=9,
                        color="#2E2A26",
                    )
            left = values if left is None else left + values
        ax.set_xlabel("Numero errori")
        ax.set_ylabel("Circuito")
        ax.set_title("Profilo errori per circuito")
        style_axes(ax)
        ax.invert_yaxis()
        ax.legend(title="Severita", loc="lower right", frameon=False)
        fig.tight_layout()
        fig.savefig(plots_dir / "02_media_sottopunteggi_per_batch.png", dpi=200)
        plt.close(fig)

    # 3) Breakdown sottopunteggi per circuito
    sub_cols = ["components_score", "terminals_pins_score", "graph_connections_score", "visible_semantics_score"]
    available_sub_cols = [c for c in sub_cols if c in df.columns]
    subs_df = df.dropna(subset=available_sub_cols, how="all").copy() if available_sub_cols else df.iloc[0:0].copy()
    if available_sub_cols and not subs_df.empty:
        if "decision" in subs_df.columns:
            subs_df["decision"] = subs_df["decision"].map(normalize_decision_label)
        subs_df = subs_df.sort_values(["score", "batch", "circuit_id"], ascending=[True, True, True])
        labels = subs_df["batch"].astype(str) + "/" + subs_df["circuit_id"].astype(str)

        fig_height = max(5.8, 0.56 * len(subs_df))
        fig, ax = plt.subplots(figsize=(12.6, fig_height))
        fig.patch.set_facecolor("#FFF8F0")
        left = None
        max_scores = {
            "components_score": 25,
            "terminals_pins_score": 20,
            "graph_connections_score": 45,
            "visible_semantics_score": 10,
        }
        pretty_names = {
            "components_score": "components",
            "terminals_pins_score": "terminals_pins",
            "graph_connections_score": "graph_connections",
            "visible_semantics_score": "visible_semantics",
        }
        for col in sub_cols:
            if col not in subs_df.columns:
                continue
            values = subs_df[col].fillna(0)
            bars = ax.barh(
                labels,
                values,
                left=left,
                color=subscore_palette[col],
                edgecolor="#8A8175",
                linewidth=0.5,
                label=f"{pretty_names[col]} / {max_scores[col]}",
            )
            for bar, value in zip(bars, values):
                if value >= 4:
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        bar.get_y() + bar.get_height() / 2,
                        f"{int(value)}",
                        ha="center",
                        va="center",
                        fontsize=8.5,
                        color="#1F1B18",
                    )
            left = values if left is None else left + values

        ax.set_xlim(0, 100)
        ax.set_xlabel("Contributo al punteggio totale")
        ax.set_ylabel("Circuito")
        ax.set_title("Breakdown sottopunteggi per circuito")
        style_axes(ax)
        ax.invert_yaxis()
        ax.legend(title="Sottopunteggio", bbox_to_anchor=(1.02, 1), loc="upper left", frameon=False)
        fig.tight_layout()
        fig.savefig(plots_dir / "03_distribuzione_decisioni_per_batch.png", dpi=200)
        plt.close(fig)


def load_existing_raw(raw_path: Path) -> Optional[Dict[str, Any]]:
    if not raw_path.exists():
        return None
    try:
        return json.loads(raw_path.read_text(encoding="utf-8"))
    except Exception:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Verifica immagine <-> Graph JSON con un judge multimodale.")
    parser.add_argument("--root", type=Path, default=DEFAULT_VERIFY_ROOT, help="Cartella verify_json_img")
    parser.add_argument("--prompt", type=Path, default=None, help="Path prompt.txt. Default: <root>/prompt.txt")
    parser.add_argument("--out-dir", type=Path, default=None, help="Cartella output. Default: <batch>/output_gpt5_5 se analizzi un solo batch, altrimenti <root>/output_gpt5_5")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Modello judge")
    parser.add_argument("--batch", default=None, help="Batch da eseguire: A, B, C1, C2 oppure batchA/batchB/...")
    parser.add_argument("--only", default=None, help="Circuiti da eseguire, separati da virgola. Esempio: a01,c16")
    parser.add_argument("--limit", type=int, default=None, help="Limita il numero di circuiti")
    parser.add_argument("--resume", action="store_true", help="Riusa raw_responses già presenti")
    parser.add_argument("--dry-run", action="store_true", help="Mostra le coppie trovate senza chiamare l'API")
    parser.add_argument("--no-plots", action="store_true", help="Non generare grafici")
    parser.add_argument("--detail", choices=["low", "high", "auto"], default="high", help="Dettaglio immagine inviato al modello")
    parser.add_argument("--max-output-tokens", type=int, default=3500)
    parser.add_argument("--reasoning-effort", choices=["none", "low", "medium", "high", "xhigh"], default="low")
    args = parser.parse_args()

    root: Path = args.root.resolve()
    prompt_path: Path = args.prompt.resolve() if args.prompt else (root / "prompt.txt")

    # L'output viene deciso dopo aver scoperto le coppie:
    # - se stai analizzando un solo batch, finisce dentro quel batch;
    # - se stai analizzando più batch insieme, finisce nella root verify_json_img;
    # - se passi --out-dir, viene usato esattamente quel percorso.
    requested_out_dir: Optional[Path] = args.out_dir.resolve() if args.out_dir else None

    # Carica .env da più posizioni utili, senza sovrascrivere variabili già presenti.
    for env_path in [SCRIPT_DIR / ".env", root / ".env", DEFAULT_EXPERIMENT_ROOT / ".env", Path.cwd() / ".env"]:
        if env_path.exists():
            load_dotenv(env_path, override=False)

    if not os.getenv("OPENAI_API_KEY") and not args.dry_run:
        raise RuntimeError(
            "OPENAI_API_KEY non trovata. Inseriscila in un file .env vicino allo script, nella root, "
            "oppure esportala come variabile d'ambiente."
        )

    if not prompt_path.exists():
        raise FileNotFoundError(f"prompt.txt non trovato: {prompt_path}")

    prompt_template = read_text(prompt_path)
    batch_filter = normalize_batch_arg(args.batch)
    only_ids = {x.strip().lower() for x in args.only.split(",") if x.strip()} if args.only else None

    pairs = discover_pairs(root=root, batch_filter=batch_filter, only_ids=only_ids)
    if args.limit is not None:
        pairs = pairs[: args.limit]

    if not pairs:
        print("Nessuna coppia immagine/json trovata.")
        return 1

    if requested_out_dir is not None:
        out_dir = requested_out_dir
    else:
        unique_batch_dirs = sorted({pair.batch_dir.resolve() for pair in pairs})
        if len(unique_batch_dirs) == 1:
            out_dir = unique_batch_dirs[0] / DEFAULT_OUTPUT_DIR_NAME
        else:
            out_dir = root / DEFAULT_OUTPUT_DIR_NAME

    raw_dir = out_dir / "raw_responses"
    plots_dir = out_dir / "plots"

    print(f"Root: {root}")
    print(f"Prompt: {prompt_path}")
    print(f"Output: {out_dir}")
    print(f"Modello: {args.model}")
    print(f"Coppie trovate: {len(pairs)}")
    for pair in pairs:
        print(f"- [{pair.batch_label}] {pair.circuit_id}: {pair.image_path.name} + {pair.json_path.name}")

    if args.dry_run:
        return 0

    client = OpenAI()
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    all_records: List[Dict[str, Any]] = []

    for idx, pair in enumerate(pairs, start=1):
        raw_path = raw_dir / f"{pair.circuit_id}__judge_{args.model.replace('.', '_')}.json"

        if args.resume:
            existing = load_existing_raw(raw_path)
            if existing is not None:
                print(f"\n[{idx}/{len(pairs)}] {pair.circuit_id}: uso risultato esistente")
                all_records.append(existing)
                continue

        print(f"\n[{idx}/{len(pairs)}] Judge su {pair.circuit_id} ({pair.batch_label})")
        try:
            record = call_judge(
                client=client,
                model=args.model,
                prompt_template=prompt_template,
                pair=pair,
                image_detail=args.detail,
                max_output_tokens=args.max_output_tokens,
                reasoning_effort=args.reasoning_effort,
            )
        except Exception as exc:
            print(f"[ERRORE] {pair.circuit_id}: {exc}", file=sys.stderr)
            record = {
                "metadata": {
                    "circuit_id": pair.circuit_id,
                    "batch": pair.batch_label,
                    "image_path": str(pair.image_path),
                    "json_path": str(pair.json_path),
                    "image_file": pair.image_path.name,
                    "json_file": pair.json_path.name,
                    "judge_model": args.model,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "parsed_ok": False,
                    "parse_error": str(exc),
                    "api_error": True,
                },
                "judge_usage": None,
                "judge_result": {
                    "parse_error": str(exc),
                    "raw_judge_output": "",
                },
                "raw_model_output": "",
            }

        write_json(raw_path, record)
        all_records.append(record)

        row = flatten_for_csv(record)
        print(
            f"[{pair.circuit_id}] score={row.get('score')} decision={row.get('decision')} "
            f"usable={row.get('usable_as_graph_base')} "
            f"critical={row.get('critical_errors_count')} major={row.get('major_errors_count')} minor={row.get('minor_errors_count')}"
        )

    jsonl_path = out_dir / "judge_results.jsonl"
    csv_path = out_dir / "judge_results.csv"
    report_path = out_dir / "judge_report.md"

    save_jsonl(jsonl_path, all_records)
    save_csv(csv_path, all_records)
    save_markdown_report(report_path, all_records)

    if not args.no_plots:
        make_plots(csv_path, plots_dir)

    print("\nCompletato.")
    print(f"JSONL:  {jsonl_path}")
    print(f"CSV:    {csv_path}")
    print(f"Report: {report_path}")
    if not args.no_plots:
        print(f"Plots:  {plots_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
