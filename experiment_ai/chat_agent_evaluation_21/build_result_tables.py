#!/usr/bin/env python3
"""Genera le tabelle finali dai 42 risultati ufficiali del judge."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path
from statistics import mean, median
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent
JUDGE_RESULTS = ROOT / "judge_results"
DATASET_RUNS = ROOT / "dataset" / "runs.csv"
OUTPUT_ROOT = ROOT / "results"
TABLES_DIR = OUTPUT_ROOT / "tables"

MODES = ("chat", "agent")
CRITERIA = (
    "diagnostic_correctness",
    "test_quality",
    "evidence_interpretation",
    "goal_achievement",
    "conclusion_quality",
)
CRITERION_LABELS = {
    "diagnostic_correctness": "Correttezza diagnostica",
    "test_quality": "Qualità dei test",
    "evidence_interpretation": "Interpretazione delle evidenze",
    "goal_achievement": "Raggiungimento dell'obiettivo",
    "conclusion_quality": "Qualità della conclusione",
}
OUTCOME_ORDER = (
    "success",
    "partial_success",
    "failure",
    "inconclusive",
    "technical_failure",
)
OUTCOME_LABELS = {
    "success": "Successo",
    "partial_success": "Successo parziale",
    "failure": "Fallimento",
    "inconclusive": "Inconcludente",
    "technical_failure": "Fallimento tecnico",
}
CRITICAL_ERRORS = (
    "false_success",
    "unsupported_claim",
    "wrong_interpretation",
)

# Prezzi GPT-5.5 usati per la stima registrata in questa valutazione.
# I reasoning token sono gia' inclusi negli output token.
INPUT_USD_PER_MILLION = 5.0
CACHED_INPUT_USD_PER_MILLION = 0.5
OUTPUT_USD_PER_MILLION = 30.0


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_dataset_runs() -> dict[tuple[str, str], dict[str, str]]:
    with DATASET_RUNS.open("r", encoding="utf-8-sig", newline="") as handle:
        return {
            (row["circuit_id"], row["mode"]): row
            for row in csv.DictReader(handle)
        }


def parse_usage(raw: str) -> dict[str, int]:
    def value(pattern: str) -> int:
        match = re.search(pattern, raw or "")
        return int(match.group(1)) if match else 0

    input_tokens = value(r"input_tokens=(\d+)")
    cached_tokens = value(r"cached_tokens=(\d+)")
    output_tokens = value(r"output_tokens=(\d+)")
    reasoning_tokens = value(r"reasoning_tokens=(\d+)")
    return {
        "input_tokens": input_tokens,
        "cached_input_tokens": cached_tokens,
        "noncached_input_tokens": max(0, input_tokens - cached_tokens),
        "output_tokens": output_tokens,
        "reasoning_tokens": reasoning_tokens,
    }


def estimated_cost(usage: dict[str, int]) -> float:
    return (
        usage["noncached_input_tokens"] * INPUT_USD_PER_MILLION
        + usage["cached_input_tokens"] * CACHED_INPUT_USD_PER_MILLION
        + usage["output_tokens"] * OUTPUT_USD_PER_MILLION
    ) / 1_000_000


def as_int(value: str | int | None) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def load_runs() -> list[dict[str, Any]]:
    objective = read_dataset_runs()
    runs: list[dict[str, Any]] = []
    circuit_dirs = sorted(path for path in JUDGE_RESULTS.iterdir() if path.is_dir())
    for circuit_dir in circuit_dirs:
        circuit_id = circuit_dir.name
        for mode in MODES:
            judge_path = circuit_dir / f"{mode}_judge.json"
            if not judge_path.exists():
                raise FileNotFoundError(f"Risultato richiesto non trovato: {judge_path}")
            judged = read_json(judge_path)
            source = objective[(circuit_id, mode)]
            criteria = judged["criteria"]
            usage = parse_usage(str(judged["metadata"].get("usage") or ""))
            critical = list(judged.get("critical_errors") or [])
            row: dict[str, Any] = {
                "circuit_id": circuit_id,
                "mode": mode,
                "outcome": judged["outcome"],
                "outcome_label_it": OUTCOME_LABELS[judged["outcome"]],
                "outcome_reason": judged["outcome_reason"],
                "useful_result": judged["outcome"] in {"success", "partial_success"},
                "total_score": int(judged["total_score"]),
                "maximum_score": int(judged["maximum_score"]),
                **{
                    f"score_{criterion}": int(criteria[criterion]["score"])
                    for criterion in CRITERIA
                },
                **{
                    f"reason_{criterion}": str(criteria[criterion]["reason"])
                    for criterion in CRITERIA
                },
                "critical_error_count": len(critical),
                "critical_errors": "|".join(critical),
                **{
                    f"critical_{error}": error in critical
                    for error in CRITICAL_ERRORS
                },
                "confidence": judged["confidence"],
                "decisive_evidence": " | ".join(judged["decisive_evidence"]),
                "scenarios_proposed": as_int(source.get("scenarios_proposed")),
                "scenarios_executed": as_int(source.get("scenarios_executed")),
                "successful_spice_runs": as_int(source.get("successful_spice_runs")),
                "failed_spice_runs": as_int(source.get("failed_spice_runs")),
                "intermediate_user_turns": as_int(source.get("intermediate_user_turns")),
                "agent_decisions_count": as_int(source.get("agent_decisions_count")),
                "judge_model": judged["metadata"]["judge_model"],
                "reasoning_effort": judged["metadata"]["reasoning_effort"],
                "latency_seconds": float(judged["metadata"]["latency_seconds"]),
                "packet_sha256": judged["metadata"]["packet_sha256"],
                "prompt_sha256": judged["metadata"]["prompt_sha256"],
                "response_schema_sha256": judged["metadata"]["response_schema_sha256"],
                **usage,
                "estimated_cost_usd": estimated_cost(usage),
            }
            runs.append(row)
    if len(runs) != 42:
        raise ValueError(f"Attese 42 run, trovate {len(runs)}")
    return runs


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: (
                        bool_text(value)
                        if isinstance(value, bool)
                        else f"{value:.6f}"
                        if isinstance(value, float)
                        else value
                    )
                    for key, value in row.items()
                    if key in fields
                }
            )


def build_scores_only_markdown(runs: list[dict[str, Any]]) -> str:
    """Restituisce la tabella compatta con i soli punteggi delle 42 run."""
    headers = [
        "Circuito",
        "Modalità",
        "Correttezza diagnostica",
        "Qualità dei test",
        "Interpretazione evidenze",
        "Raggiungimento obiettivo",
        "Qualità conclusione",
        "Totale",
    ]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in runs:
        values = [
            row["circuit_id"],
            row["mode"].upper(),
            row["score_diagnostic_correctness"],
            row["score_test_quality"],
            row["score_evidence_interpretation"],
            row["score_goal_achievement"],
            row["score_conclusion_quality"],
            row["total_score"],
        ]
        lines.append("| " + " | ".join(map(str, values)) + " |")
    return "\n".join(lines) + "\n"


def mode_rows(runs: list[dict[str, Any]], mode: str) -> list[dict[str, Any]]:
    return runs if mode == "overall" else [row for row in runs if row["mode"] == mode]


def build_mode_summary(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for mode in (*MODES, "overall"):
        selected = mode_rows(runs, mode)
        outcomes = Counter(row["outcome"] for row in selected)
        usage_keys = (
            "input_tokens",
            "cached_input_tokens",
            "noncached_input_tokens",
            "output_tokens",
            "reasoning_tokens",
        )
        result.append(
            {
                "mode": mode,
                "runs": len(selected),
                "success_count": outcomes["success"],
                "partial_success_count": outcomes["partial_success"],
                "failure_count": outcomes["failure"],
                "inconclusive_count": outcomes["inconclusive"],
                "technical_failure_count": outcomes["technical_failure"],
                "useful_result_count": sum(row["useful_result"] for row in selected),
                "success_rate": outcomes["success"] / len(selected),
                "useful_result_rate": sum(row["useful_result"] for row in selected)
                / len(selected),
                "mean_total_score": mean(row["total_score"] for row in selected),
                "median_total_score": median(row["total_score"] for row in selected),
                "critical_run_count": sum(row["critical_error_count"] > 0 for row in selected),
                "critical_run_rate": sum(row["critical_error_count"] > 0 for row in selected)
                / len(selected),
                **{
                    key: sum(row[key] for row in selected)
                    for key in usage_keys
                },
                "estimated_cost_usd": sum(row["estimated_cost_usd"] for row in selected),
                "prompt_sha256_values": "|".join(
                    sorted({row["prompt_sha256"] for row in selected})
                ),
            }
        )
    return result


def build_criteria_summary(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for mode in (*MODES, "overall"):
        selected = mode_rows(runs, mode)
        for criterion in CRITERIA:
            values = [row[f"score_{criterion}"] for row in selected]
            criterion_mean = mean(values)
            result.append(
                {
                    "mode": mode,
                    "criterion": criterion,
                    "criterion_label_it": CRITERION_LABELS[criterion],
                    "mean_score": criterion_mean,
                    "maximum_score": 2,
                    "normalized_percentage": criterion_mean / 2,
                    "score_0_count": values.count(0),
                    "score_1_count": values.count(1),
                    "score_2_count": values.count(2),
                }
            )
    return result


def build_outcome_summary(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for mode in (*MODES, "overall"):
        selected = mode_rows(runs, mode)
        counts = Counter(row["outcome"] for row in selected)
        for outcome in OUTCOME_ORDER:
            result.append(
                {
                    "mode": mode,
                    "outcome": outcome,
                    "outcome_label_it": OUTCOME_LABELS[outcome],
                    "count": counts[outcome],
                    "rate": counts[outcome] / len(selected),
                }
            )
    return result


def build_critical_summary(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for mode in (*MODES, "overall"):
        selected = mode_rows(runs, mode)
        for error in CRITICAL_ERRORS:
            count = sum(row[f"critical_{error}"] for row in selected)
            result.append(
                {
                    "mode": mode,
                    "critical_error": error,
                    "run_count": count,
                    "run_rate": count / len(selected),
                }
            )
    return result


def build_paired(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    indexed = {(row["circuit_id"], row["mode"]): row for row in runs}
    result = []
    for circuit_id in sorted({row["circuit_id"] for row in runs}):
        chat = indexed[(circuit_id, "chat")]
        agent = indexed[(circuit_id, "agent")]
        delta = agent["total_score"] - chat["total_score"]
        relation = "agent_higher" if delta > 0 else "chat_higher" if delta < 0 else "equal"
        result.append(
            {
                "circuit_id": circuit_id,
                "chat_outcome": chat["outcome"],
                "chat_score": chat["total_score"],
                "chat_useful": chat["useful_result"],
                "chat_critical_errors": chat["critical_errors"],
                "agent_outcome": agent["outcome"],
                "agent_score": agent["total_score"],
                "agent_useful": agent["useful_result"],
                "agent_critical_errors": agent["critical_errors"],
                "agent_minus_chat_score": delta,
                "score_relation_descriptive": relation,
                "at_least_one_mode_useful": chat["useful_result"] or agent["useful_result"],
                "both_modes_useful": chat["useful_result"] and agent["useful_result"],
            }
        )
    return result


def percent(value: float) -> str:
    return f"{value * 100:.1f}%".replace(".", ",")


def decimal(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}".replace(".", ",")


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def build_markdown(
    runs: list[dict[str, Any]],
    modes: list[dict[str, Any]],
    criteria: list[dict[str, Any]],
    critical: list[dict[str, Any]],
    paired: list[dict[str, Any]],
) -> str:
    mode_index = {row["mode"]: row for row in modes}
    criteria_index = {
        (row["mode"], row["criterion"]): row for row in criteria
    }
    critical_index = {
        (row["mode"], row["critical_error"]): row for row in critical
    }

    summary_table = markdown_table(
        [
            "Modalità",
            "Run",
            "Successi",
            "Parziali",
            "Fallimenti",
            "Risultati utili",
            "Media /10",
            "Run con criticità",
        ],
        [
            [
                "CHAT" if mode == "chat" else "AGENT" if mode == "agent" else "Complessivo",
                mode_index[mode]["runs"],
                f'{mode_index[mode]["success_count"]} ({percent(mode_index[mode]["success_rate"])})',
                mode_index[mode]["partial_success_count"],
                mode_index[mode]["failure_count"],
                f'{mode_index[mode]["useful_result_count"]} ({percent(mode_index[mode]["useful_result_rate"])})',
                decimal(mode_index[mode]["mean_total_score"]),
                f'{mode_index[mode]["critical_run_count"]} ({percent(mode_index[mode]["critical_run_rate"])})',
            ]
            for mode in ("chat", "agent", "overall")
        ],
    )

    paired_table = markdown_table(
        ["Circuito", "CHAT", "Punti", "AGENT", "Punti", "Δ A−C", "Criticità AGENT"],
        [
            [
                row["circuit_id"],
                OUTCOME_LABELS[row["chat_outcome"]],
                row["chat_score"],
                OUTCOME_LABELS[row["agent_outcome"]],
                row["agent_score"],
                f'{row["agent_minus_chat_score"]:+d}',
                row["agent_critical_errors"].replace("|", ", ") or "—",
            ]
            for row in paired
        ],
    )

    criteria_table = markdown_table(
        ["Criterio", "CHAT /2", "AGENT /2", "Complessivo /2"],
        [
            [
                CRITERION_LABELS[criterion],
                decimal(criteria_index[("chat", criterion)]["mean_score"]),
                decimal(criteria_index[("agent", criterion)]["mean_score"]),
                decimal(criteria_index[("overall", criterion)]["mean_score"]),
            ]
            for criterion in CRITERIA
        ],
    )

    critical_table = markdown_table(
        ["Errore critico", "CHAT", "AGENT", "Totale"],
        [
            [
                error,
                critical_index[("chat", error)]["run_count"],
                critical_index[("agent", error)]["run_count"],
                critical_index[("overall", error)]["run_count"],
            ]
            for error in CRITICAL_ERRORS
        ],
    )

    cost_table = markdown_table(
        ["Modalità", "Input", "Input cached", "Output", "Reasoning*", "Costo stimato USD"],
        [
            [
                "CHAT" if mode == "chat" else "AGENT" if mode == "agent" else "Totale",
                mode_index[mode]["input_tokens"],
                mode_index[mode]["cached_input_tokens"],
                mode_index[mode]["output_tokens"],
                mode_index[mode]["reasoning_tokens"],
                decimal(mode_index[mode]["estimated_cost_usd"], 4),
            ]
            for mode in ("chat", "agent", "overall")
        ],
    )

    chat_hash = mode_index["chat"]["prompt_sha256_values"]
    agent_hash = mode_index["agent"]["prompt_sha256_values"]
    return f"""# Tabelle finali della valutazione CHAT–AGENT

## Scopo e sorgenti

Questa cartella raccoglie le tabelle derivate dai 42 risultati ufficiali in
`judge_results`: 21 circuiti valutati una volta in modalità CHAT e una volta in
modalità AGENT. I risultati pilota presenti in
`judge_results_process_calibrated` non entrano in nessuna tabella.

Il sistema viene valutato prima nel complesso e successivamente per modalità.
Il confronto CHAT–AGENT è descrittivo: serve a mostrare il diverso comportamento
della modalità guidata e di quella autonoma, non a stabilire un vincitore.

## Scala di valutazione

Ogni run riceve cinque punteggi interi compresi tra 0 e 2:

- **0 — errato o assente:** il criterio non è soddisfatto oppure è contrario
  alle evidenze;
- **1 — utile ma incompleto:** esiste un contributo corretto, ma con omissioni,
  limiti o errori rilevanti;
- **2 — corretto e verificato:** il criterio è soddisfatto con evidenze
  sufficienti.

I cinque criteri sono:

1. **Correttezza diagnostica:** correttezza della causa, del comportamento o
   della localizzazione individuata.
2. **Qualità dei test:** pertinenza e capacità degli scenari eseguiti di
   distinguere le ipotesi importanti.
3. **Interpretazione delle evidenze:** correttezza con cui misure SPICE,
   transitori e confronti vengono letti.
4. **Raggiungimento dell'obiettivo:** misura in cui la richiesta dell'utente è
   stata soddisfatta.
5. **Qualità della conclusione:** chiarezza, correttezza e prudenza della
   risposta finale.

La somma produce un punteggio descrittivo compreso tra **0 e 10**. L'esito non
dipende meccanicamente dal totale: una falsa correzione centrale può determinare
`failure` anche quando alcuni test ricevono credito.

## Esiti

- **Successo (`success`):** obiettivo raggiunto con conclusione corretta e prove
  sufficienti.
- **Successo parziale (`partial_success`):** almeno un contributo corretto e
  materialmente utile, ma obiettivo incompleto o conclusione con limiti
  rilevanti.
- **Fallimento (`failure`):** nessun risultato concretamente utilizzabile oppure
  falsa soluzione contraria alle evidenze come risultato sostanziale.
- **Inconcludente (`inconclusive`):** dati insufficienti per una decisione.
- **Fallimento tecnico (`technical_failure`):** traiettoria non valutabile.

Nel seguito, **risultato utile** indica esclusivamente `success +
partial_success`. Non significa che la diagnosi sia sempre completamente
corretta: un successo parziale può richiedere supervisione, soprattutto quando
sono presenti errori critici.

## Errori critici

- `false_success`: viene dichiarata una soluzione non realmente dimostrata;
- `unsupported_claim`: viene affermata una causa o un effetto non sostenuto;
- `wrong_interpretation`: una misura viene interpretata in modo incompatibile
  con le evidenze.

Un errore critico impedisce il successo pieno quando compromette il risultato,
ma può coesistere con un successo parziale se la traiettoria conserva un
contributo indipendente e utile.

## Risultati principali

{summary_table}

Il sistema completa tecnicamente tutte le run e produce un risultato utile in
**41/42 casi (97,6%)**. CHAT produce un risultato utile in 21/21 casi; AGENT in
20/21. Il singolo fallimento semantico è c02 in modalità AGENT.

## Risultati appaiati per circuito

{paired_table}

La colonna Δ A−C è la differenza descrittiva tra punteggio AGENT e punteggio
CHAT. Valori positivi indicano un punteggio AGENT maggiore, valori negativi un
punteggio CHAT maggiore.

## Punteggio medio dei criteri

{criteria_table}

La qualità dei test è il punto più forte di AGENT. La qualità della conclusione
è invece il criterio più debole: la modalità autonoma riesce generalmente a
eseguire prove pertinenti, ma è più fragile nell'attribuzione causale e nella
sintesi finale.

## Frequenza degli errori critici

{critical_table}

Le occorrenze non coincidono con il numero di run critiche, perché una stessa
run può contenere più categorie di errore.

## Token e costo del judge

{cost_table}

Nota: i reasoning token sono già compresi negli output token e non vengono
addebitati una seconda volta. La stima usa 5 USD/M token input non cached,
0,50 USD/M cached input e 30 USD/M output per GPT-5.5.

## File CSV prodotti

### `table_01_run_results.csv`

Una riga per ciascuna delle 42 run. Contiene:

- identificativo del circuito e modalità;
- esito, risultato utile e punteggio totale;
- cinque punteggi individuali;
- numero e tipi di errori critici;
- scenari proposti/eseguiti e run SPICE riuscite/fallite;
- turni intermedi dell'utente oppure decisioni autonome;
- modello, latenza, token, costo e hash di provenienza.

### `table_02_paired_results.csv`

Una riga per circuito con CHAT e AGENT affiancati. È la base per grafici a
barre appaiate, differenze di punteggio e conteggio dei casi in cui entrambe le
modalità forniscono un risultato utile.

### `table_03_mode_summary.csv`

Tre righe: CHAT, AGENT e complessivo. Riporta esiti, tassi, media, mediana,
criticità, token, costo e hash del prompt.

### `table_04_criteria_summary.csv`

Distribuzione 0/1/2 e media di ciascun criterio per CHAT, AGENT e totale. È la
base per un grafico a barre dei cinque criteri.

### `table_05_outcome_summary.csv`

Conteggi e percentuali dei cinque esiti. È la base per grafici a barre o barre
impilate.

### `table_06_critical_errors.csv`

Numero e frequenza delle tre categorie di errore critico per modalità e nel
complesso.

## Campi principali dei CSV

- `circuit_id`: identificativo del circuito;
- `mode`: `chat` oppure `agent`;
- `outcome`: esito semantico del judge;
- `useful_result`: vero per successo o successo parziale;
- `total_score`: somma dei cinque criteri, massimo 10;
- `score_*`: punteggio 0–2 del criterio indicato;
- `outcome_reason`: motivazione sintetica dell'esito;
- `reason_*`: motivazione assegnata dal judge al singolo criterio;
- `decisive_evidence`: evidenze considerate decisive dal judge;
- `critical_errors`: categorie separate dal carattere `|`;
- `scenarios_proposed` / `scenarios_executed`: prove pianificate ed eseguite;
- `successful_spice_runs` / `failed_spice_runs`: riuscita tecnica degli scenari;
- `intermediate_user_turns`: interventi intermedi dell'utente in CHAT;
- `agent_decisions_count`: decisioni autonome in AGENT;
- `latency_seconds`: durata della chiamata al judge, non dell'intera diagnosi;
- `input_tokens`, `cached_input_tokens`, `output_tokens`: consumo del judge;
- `reasoning_tokens`: quota di ragionamento già inclusa negli output token;
- `estimated_cost_usd`: costo stimato della chiamata al judge;
- `packet_sha256`, `prompt_sha256`, `response_schema_sha256`: identificatori
  riproducibili degli input e del protocollo.

## Provenienza e limite di comparabilità

Hash prompt CHAT:

```text
{chat_hash}
```

Hash prompt AGENT:

```text
{agent_hash}
```

La calibrazione AGENT attribuisce esplicitamente credito alle parti corrette
dell'intera traiettoria autonoma, senza trasformare una conclusione errata in
successo pieno. Poiché gli hash dei prompt sono differenti, il confronto dei
punteggi CHAT–AGENT deve essere presentato come **secondario e descrittivo**.
Le valutazioni principali per modalità restano invece pienamente interpretabili.

## Limiti della valutazione

- È disponibile una sola traiettoria per modalità e circuito: non viene stimata
  la variabilità tra nuove generazioni del modello linguistico.
- Il judge è un modello linguistico; ground truth, casi anomali e calibrazione
  sono stati quindi controllati manualmente.
- Le simulazioni dimostrano il comportamento dei modelli SPICE e delle
  assunzioni adottate, non garantiscono automaticamente il comportamento di un
  circuito fisico.
- Un successo parziale con errore critico va interpretato come supporto utile
  ma bisognoso di supervisione, non come diagnosi definitiva.

## Grafici consigliati

Le tabelle permettono di generare, senza ulteriori valutazioni API:

1. distribuzione degli esiti CHAT, AGENT e complessivi;
2. punteggio CHAT e AGENT per ciascun circuito;
3. media dei cinque criteri per modalità;
4. heatmap dei cinque criteri sulle 42 run;
5. frequenza degli errori critici;
6. relazione tra autonomia operativa e qualità finale.
"""


def main() -> int:
    runs = load_runs()
    mode_summary = build_mode_summary(runs)
    criteria_summary = build_criteria_summary(runs)
    outcome_summary = build_outcome_summary(runs)
    critical_summary = build_critical_summary(runs)
    paired = build_paired(runs)

    run_fields = [
        "circuit_id",
        "mode",
        "outcome",
        "outcome_label_it",
        "outcome_reason",
        "useful_result",
        "total_score",
        "maximum_score",
        *[f"score_{criterion}" for criterion in CRITERIA],
        *[f"reason_{criterion}" for criterion in CRITERIA],
        "critical_error_count",
        "critical_errors",
        *[f"critical_{error}" for error in CRITICAL_ERRORS],
        "confidence",
        "decisive_evidence",
        "scenarios_proposed",
        "scenarios_executed",
        "successful_spice_runs",
        "failed_spice_runs",
        "intermediate_user_turns",
        "agent_decisions_count",
        "judge_model",
        "reasoning_effort",
        "latency_seconds",
        "input_tokens",
        "cached_input_tokens",
        "noncached_input_tokens",
        "output_tokens",
        "reasoning_tokens",
        "estimated_cost_usd",
        "packet_sha256",
        "prompt_sha256",
        "response_schema_sha256",
    ]
    paired_fields = list(paired[0])
    mode_fields = list(mode_summary[0])
    criteria_fields = list(criteria_summary[0])
    outcome_fields = list(outcome_summary[0])
    critical_fields = list(critical_summary[0])
    scores_only_fields = [
        "circuit_id",
        "mode",
        "score_diagnostic_correctness",
        "score_test_quality",
        "score_evidence_interpretation",
        "score_goal_achievement",
        "score_conclusion_quality",
        "total_score",
    ]

    write_csv(TABLES_DIR / "table_01_run_results.csv", runs, run_fields)
    write_csv(TABLES_DIR / "table_02_paired_results.csv", paired, paired_fields)
    write_csv(TABLES_DIR / "table_03_mode_summary.csv", mode_summary, mode_fields)
    write_csv(TABLES_DIR / "table_04_criteria_summary.csv", criteria_summary, criteria_fields)
    write_csv(TABLES_DIR / "table_05_outcome_summary.csv", outcome_summary, outcome_fields)
    write_csv(TABLES_DIR / "table_06_critical_errors.csv", critical_summary, critical_fields)
    write_csv(TABLES_DIR / "table_07_scores_only.csv", runs, scores_only_fields)

    markdown = build_markdown(
        runs,
        mode_summary,
        criteria_summary,
        critical_summary,
        paired,
    )
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    (OUTPUT_ROOT / "RESULTS_TABLES.md").write_text(markdown, encoding="utf-8")
    (OUTPUT_ROOT / "SCORES_ONLY.md").write_text(
        build_scores_only_markdown(runs), encoding="utf-8"
    )
    print(f"Generate 7 tabelle CSV in: {TABLES_DIR}")
    print(f"Generato report: {OUTPUT_ROOT / 'RESULTS_TABLES.md'}")
    print(f"Generata tabella punteggi: {OUTPUT_ROOT / 'SCORES_ONLY.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
