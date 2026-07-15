"""Costruzione del prompt separato per l'agente autonomo."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .contracts import ALLOWED_ACTION_TYPES, MAX_SCENARIOS_PER_DECISION


ARTIFACT_NAMES = (
    "03_node_map.json",
    "06_component_rules.json",
    "07_netlist.cir",
    "07_spice_emit_report.json",
    "08_ngspice_stdout.txt",
    "08_ngspice_stderr.txt",
    "10_diagnostic_context.json",
)


def read_text_limited(path: Path, limit: int = 30000) -> str:
    """Legge un artefatto limitandone la dimensione nel prompt."""
    if not path.exists() or not path.is_file():
        return "[not available]"
    text = path.read_text(encoding="utf-8", errors="replace")
    return text if len(text) <= limit else text[:limit] + "\n[truncated]"


def collect_evidence(output_dir: Path) -> dict[str, str]:
    """Raccoglie gli artefatti tecnici necessari alla decisione autonoma."""
    return {name: read_text_limited(output_dir / name) for name in ARTIFACT_NAMES}


def build_autonomous_prompt(
    output_dir: Path,
    state: dict[str, Any],
    remaining_budget: int,
) -> str:
    """Costruisce un prompt JSON-only grounded sugli output della run."""
    evidence = collect_evidence(output_dir)
    allowed = ", ".join(sorted(ALLOWED_ACTION_TYPES))
    history = json.dumps(state.get("iterations") or [], indent=2, ensure_ascii=False)
    artifacts = "\n\n".join(
        f"## {name}\n```text\n{content}\n```"
        for name, content in evidence.items()
    )
    return f"""# Pipeline 2.0 - agente diagnostico autonomo controllato

Sei il controller diagnostico di una pipeline Graph JSON -> SPICE/ngspice.
Devi scegliere il prossimo test controllato oppure fermarti con una conclusione.

## Sintomo utente
{state.get('symptom')}

## Vincoli obbligatori
- Rispondi con un solo oggetto JSON valido, senza Markdown o testo esterno.
- Non inventare nodi, componenti, valori o risultati.
- Usa soltanto queste primitive: {allowed}.
- Ogni scenario deve essere self-contained e partire dalla base run.
- Puoi proporre al massimo {MAX_SCENARIOS_PER_DECISION} scenari indipendenti.
- Budget residuo: {remaining_budget} run scenario.
- Se il budget e zero devi restituire decision=stop.
- Non usare resolved_candidate come prova automatica di soluzione definitiva.
- Distingui una soluzione da una semplice localizzazione della causa.
- Ogni scenario deve avere una lista compare non vuota con grandezze osservabili.
- Per scenari con piu rami o uscite, includi in compare almeno una grandezza per ciascuno.
- Se l'obiettivo richiede di attivare o spegnere un componente, includi in compare
  almeno una misura diretta del componente, preferendo i(NOME_SPICE).
- Se l'obiettivo richiede di mantenere invariato un altro componente, includi in
  compare anche una sua misura diretta: le sole tensioni di nodo non ne verificano lo stato.
- Ricava NOME_SPICE dalla netlist 07_netlist.cir; non usare l'id Graph JSON dentro i(...) o p(...).
- Richiedi p(NOME_SPICE) soltanto se la potenza dello stesso dispositivo e gia
  disponibile negli output ngspice forniti; non aggiungere misure ridondanti.
- Ogni scenario deve avere un oggetto expect non vuoto. Le chiavi devono essere
  grandezze presenti in compare e i valori ammessi sono: activated, deactivated,
  changed, unchanged, increased, decreased, magnitude_increased,
  magnitude_decreased, nonzero.
- Usa expect per descrivere sia l'effetto cercato sia i vincoli da preservare,
  per esempio corrente del target activated e corrente del componente protetto unchanged.
- Per una run .tran usa le tracce disponibili e confronta almeno l'uscita o il ramo
  direttamente coinvolto nell'obiettivo, oltre agli eventuali nodi intermedi.
- Non dichiarare verified_correction se i confronti non misurano direttamente sia
  il componente target sia gli eventuali componenti che devono restare attivi.
- Preferisci modifiche minime su componenti, valori e collegamenti gia esistenti.
- Usa nuove sorgenti o nuovi rami resistivi solo quando le evidenze tecniche li giustificano.
- Usa feed_nodes_from_source_node solo da un nodo che gli output mostrano gia alimentato.
- Usa connect_nodes per una ipotesi di continuita mancante senza attribuire a un nodo il ruolo di sorgente.
- Non proporre connect_nodes e feed_nodes_from_source_node sulla stessa relazione tra nodi nella stessa decisione.
- Considera add_resistor_between_nodes una ipotesi distinta: aggiunge un vero accoppiamento resistivo, non un filo quasi ideale.

## Schema delle azioni consentite
- drive_node_voltage: type, target, value
- change_source_value: type, target, value
- change_component_value: type, target, value
- close_switch: type, target, resistance opzionale
- connect_nodes: type, from, to, resistance opzionale
- feed_nodes_from_source_node: type, source_node, target_nodes, resistance opzionale
- add_voltage_source_between_nodes: type, positive, negative, value
- add_resistor_between_nodes: type, from, to, value

## Formati ammessi
{{"decision":"run_scenarios","reason":"...","scenarios":[{{"title":"...","hypothesis":"...","actions":[{{"type":"close_switch","target":"...","resistance":"1m"}}],"compare":["i(RTARGET)","i(DPROTECTED)"],"expect":{{"i(RTARGET)":"activated","i(DPROTECTED)":"unchanged"}}}}]}}

oppure

{{"decision":"stop","reason":"...","final_status":"resolved|localized|partially_localized|topology_issue|inconclusive","final_answer":"Sintesi breve della conclusione.","final_cause":"Causa tecnica individuata, senza ripetizioni.","verified_correction":"Correzione verificata dagli scenari, oppure stringa vuota se non verificata."}}

## Decisioni e risultati precedenti
```json
{history}
```

## Evidenze tecniche correnti
{artifacts}
"""


def write_autonomous_prompt(output_dir: Path, prompt: str, decision_number: int) -> Path:
    """Salva il prompt di una decisione per garantire tracciabilita."""
    path = output_dir / "experiment_chat" / f"autonomous_prompt_{decision_number}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(prompt, encoding="utf-8")
    return path
