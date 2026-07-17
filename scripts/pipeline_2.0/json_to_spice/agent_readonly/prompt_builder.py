"""
Costruzione del prompt per l'agente diagnostico read-only.

Questo modulo prepara il file 11_agent_prompt.md, cioe il testo che potra essere
mandato al modello AI nella prima versione dell'agente.

Il prompt resta separato dal preview:

- il preview serve a noi per vedere tutti gli artefatti caricati;
- il prompt serve al futuro modello AI per rispondere in modo controllato.

La versione corrente non chiama ancora OpenAI. Genera solo un prompt locale e
verificabile, con istruzioni stabili ed evidenze caricate dagli output 01-08.
"""

from __future__ import annotations

import json
import unicodedata
from pathlib import Path
from typing import Any

from agent_readonly.preview_builder import (
    artifact_language,
    limit_text,
    load_json,
    read_artifact_text,
    resolve_artifact_path,
)
from agent_readonly.scenario_prompt import (
    build_scenario_answer_format,
    build_scenario_guidance,
    build_scenario_operating_rules,
)


DEFAULT_PROMPT_OUTPUT_NAME = "11_agent_prompt.md"
MAX_PROMPT_ARTIFACT_CHARS = 9000

# Lo step 10 non compare qui perche e il manifest usato per costruire il prompt,
# non una evidenza tecnica da analizzare come graph, node map o stdout/stderr.
PROMPT_ARTIFACT_ORDER = [
    "graph",
    "node_map",
    "values_bound",
    "component_rules",
    "netlist",
    "spice_emit_report",
    "spice_run",
    "ngspice_stdout",
    "ngspice_stderr",
    "tran_csv",
]


def build_system_instructions() -> list[str]:
    """Restituisce le istruzioni stabili per il modello AI."""
    return [
        "You are a read-only diagnostic assistant for electronic circuits.",
        "Your task is to explain the Pipeline 2.0 and ngspice results using only the provided evidence.",
        "The final answer must be written in Italian.",
        "Keep technical identifiers exactly as provided, for example node names, component IDs and file names.",
        "Do not invent component values, electrical connections, SPICE models, node voltages, currents or simulation results.",
        "Do not assume that a component exists if it is not present in the Graph JSON or in the generated netlist.",
        "Do not modify the netlist, do not execute SPICE and do not apply scenarios.",
        "New diagnostic scenarios may be suggested only as future SPICE-verifiable hypotheses, not as already verified facts.",
        "Already executed scenarios must be interpreted from the executed scenario evidence, not re-imagined.",
        "Use general electronics and SPICE knowledge only to interpret the provided evidence, not to create missing evidence.",
        "If the evidence is insufficient, say exactly what is missing.",
        "Do not describe a branch as floating unless the evidence shows a floating or singleton node with no DC reference path.",
        "If a branch has a resistive path to ground but no active source, describe it as not driven or not powered.",
    ]


def normalize_matching_text(text: str) -> str:
    """Normalizza testo libero per match robusti su input utente italiani."""
    lowered = text.lower()
    normalized = unicodedata.normalize("NFKD", lowered)
    without_accents = "".join(char for char in normalized if not unicodedata.combining(char))
    return without_accents


def is_executed_scenario_question(user_problem: str) -> bool:
    """Riconosce domande che chiedono di interpretare scenari gia eseguiti."""
    text = normalize_matching_text(user_problem)
    scenario_words = ("scenario", "scenari")
    outcome_words = (
        "risolve",
        "risolto",
        "risolutivo",
        "migliore",
        "conferma",
        "parziale",
        "partially",
        "resolved",
        "outcome",
    )
    return any(word in text for word in scenario_words) and any(word in text for word in outcome_words)


def is_next_scenario_request(user_problem: str) -> bool:
    """Riconosce domande che chiedono cosa provare dopo gli scenari eseguiti."""
    text = normalize_matching_text(user_problem)
    scenario_words = ("scenario", "scenari")
    executed_outcome_words = (
        "outcome",
        "resolved",
        "partially",
        "parziale",
        "migliore",
        "piu forte",
        "risolve meglio",
        "ha risolto",
        "ha spiegato meglio",
    )
    if any(word in text for word in scenario_words) and any(word in text for word in executed_outcome_words):
        return False

    direct_phrases = (
        "quale scenario self-contained",
        "che scenario",
        "proponi uno scenario",
        "proporresti uno scenario",
        "quale scenario proporresti",
        "prossimo scenario",
    )
    if any(phrase in text for phrase in direct_phrases):
        return True

    next_words = (
        "adesso",
        "ora",
        "dopo",
        "prossimo",
        "successivo",
        "combin",
        "insieme",
        "provare",
        "proviamo",
        "proporre",
        "proponi",
        "proposta",
        "proporresti",
        "self-contained",
        "fare",
        "risolvere",
        "non hanno risolto",
        "non risolve",
        "non basta",
    )
    return any(word in text for word in scenario_words) and any(word in text for word in next_words)


def has_executed_scenario_evidence(summary: dict[str, Any] | None) -> bool:
    """Indica se il manifest contiene davvero almeno uno scenario gia eseguito."""
    if not isinstance(summary, dict):
        return False
    scenario_budget = summary.get("_scenario_budget")
    if isinstance(scenario_budget, dict):
        try:
            return int(scenario_budget.get("executed_scenarios_count") or 0) > 0
        except (TypeError, ValueError):
            return False
    return False


def is_final_conclusion_request(user_problem: str) -> bool:
    """Riconosce domande che chiedono una sintesi o conclusione finale."""
    text = normalize_matching_text(user_problem)

    direct_phrases = (
        "dammi una conclusione finale",
        "qual e la conclusione finale piu probabile",
        "qual e la diagnosi finale piu probabile",
        "che cosa abbiamo capito finora",
        "riassumi cosa hanno mostrato gli scenari",
        "con questi scenari, qual e la conclusione",
        "a questo punto, qual e la conclusione piu probabile",
        "alla luce degli scenari eseguiti, cosa sembra piu probabile",
        "dopo questi test, cosa possiamo concludere",
        "ha senso continuare con altri scenari oppure possiamo gia concludere",
        "conviene fermarsi qui e tirare le conclusioni",
        "siamo arrivati a una conclusione oppure serve ancora altro",
        "a questo punto possiamo concludere che",
        "possiamo concludere che",
        "quindi possiamo concludere che",
        "mi sembra di poter concludere che",
    )
    if any(phrase in text for phrase in direct_phrases):
        return True

    final_words = (
        "conclusione finale",
        "diagnosi finale",
        "tirare le conclusioni",
        "cosa possiamo concludere",
        "cosa abbiamo capito",
        "riassumi",
        "serve ancora altro",
        "possiamo gia concludere",
        "possiamo concludere che",
    )
    scenario_context_words = ("scenario", "scenari", "test", "netlist", "rami finali", "pwr", "ac_input", "vac")
    return any(word in text for word in final_words) and any(word in text for word in scenario_context_words)




def has_strong_topology_failure(summary: dict[str, Any] | None) -> bool:
    """Rileva i casi in cui il graph estratto non sembra affidabile per scenari solo elettrici."""
    if not summary:
        return False

    if summary.get("spice_status") != "failed":
        return False

    signals = 0
    if int(summary.get("ground_groups_count") or 0) == 0:
        signals += 1
    if int(summary.get("singleton_nodes_count") or 0) >= 2:
        signals += 1
    if int(summary.get("skipped_components_count") or 0) >= 2:
        signals += 1
    if int(summary.get("unsupported_components") or 0) >= 1:
        signals += 1
    if int(summary.get("rules_missing_components") or 0) >= 2:
        signals += 1

    return signals >= 2


def build_executed_scenario_answer_format() -> list[str]:
    """Formato speciale quando l'utente chiede degli scenari gia eseguiti."""
    return [
        "La domanda riguarda scenari gia eseguiti.",
        "Non proporre nuovi scenari in questa risposta, a meno che l'utente lo chieda esplicitamente.",
        "Rispondi in Markdown usando esattamente queste sezioni:",
        "",
        "1. **Risposta diretta**",
        "   Indica subito quale scenario ha l'outcome piu forte.",
        "   Se esiste uno scenario con `diagnostic_outcome.status = resolved_candidate` e `stop_automation = true`, dillo chiaramente.",
        "",
        "2. **Perche quello scenario risolve meglio**",
        "   Usa `scenario_comparison.json`: cita le grandezze cambiate, valori base, valori scenario e delta quando sono rilevanti.",
        "",
        "3. **Perche gli altri scenari non bastano**",
        "   Spiega per ogni altro scenario perche e solo parziale, diagnostico o di isolamento.",
        "",
        "4. **Conclusione provvisoria**",
        "   Riassumi in 2-3 frasi la lettura diagnostica piu forte emersa finora.",
        "",
        "5. **Conclusione operativa**",
        "   Spiega se l'automazione dovrebbe fermarsi o continuare, usando `stop_automation`.",
        "",
        "`Richiede immagine: si/no`",
    ]


def build_next_scenario_answer_format() -> list[str]:
    """Formato speciale quando l'utente chiede quale scenario provare dopo."""
    return [
        "La domanda chiede cosa provare dopo gli scenari gia eseguiti.",
        "Usa gli executed scenario evidence: non ripartire dalla sola base run.",
        "Rispondi in Markdown usando esattamente queste sezioni:",
        "",
        "1. **Stato degli scenari eseguiti**",
        "   Riassumi scenario per scenario: outcome, cosa ha cambiato, cosa non ha risolto.",
        "",
        "2. **Ragionamento sul prossimo scenario**",
        "   Spiega quali ipotesi precedenti sono utili e quali no.",
        "   Non scartare uno scenario solo perche e `not_resolved`: valuta se e irrilevante oppure se e una condizione abilitante.",
        "   Uno scenario `not_resolved` puo essere abilitante se chiude uno switch, crea un riferimento, completa un percorso di corrente o prepara un'altra azione.",
        "   Non combinare tutti gli scenari automaticamente.",
        "   Combina solo azioni supportate da evidenze complementari.",
        "",
        "3. **Scenari proposti**",
        "   Proponi un solo prossimo scenario, oppure dichiara che serve un dato mancante.",
        "   Lo scenario deve essere eseguibile e self-contained.",
        "   Il singolo scenario deve iniziare con `**scenario_X - Titolo naturale**`.",
        "   Usa sempre i campi leggibili `Ipotesi`, `Cosa cambia`, `Cosa verifichiamo`, `Come lo leggiamo`, `Se non basta`.",
        "   Ogni scenario riparte dalla base run: se la nuova ipotesi richiede una condizione abilitante gia vista in uno scenario precedente, reincludi quell'azione nello stesso array `actions`.",
        "   Se e combinato, ogni azione necessaria deve comparire nello stesso array `actions`.",
        "",
        "4. **Cosa mi aspetto di verificare**",
        "   Indica quali grandezze o warning devono cambiare per considerarlo utile.",
        "",
        "5. **Blocco tecnico per pipeline**",
        "   Includi un blocco JSON breve con `scenario_id`, `title`, `hypothesis`, `actions`, `rerun_from`, `analysis`, `compare`.",
        "   Se lo scenario coinvolge piu rami, carichi o uscite, inserisci in `compare` almeno una grandezza osservabile per ciascuno di essi.",
        "   Usa solo primitive supportate: scenari elettrici / di pilotaggio (`drive_node_voltage`, `set_initial_node_voltage`, `add_voltage_source_between_nodes`, `change_source_value`, `change_component_value`, `close_switch`) e scenari topologici controllati (`connect_nodes`, `add_resistor_between_nodes`, `feed_nodes_from_source_node`).",
        "   Non usare `unknown` nei valori.",
        "",
        "6. **Conclusione provvisoria**",
        "   Chiudi con una sintesi breve: che cosa abbiamo capito finora e perche questo e il prossimo scenario migliore.",
        "",
        "`Richiede immagine: si/no`",
    ]


def build_final_conclusion_after_budget_answer_format() -> list[str]:
    """Formato usato quando il budget scenari e terminato."""
    return [
        "Il budget scenari e esaurito: non proporre nuovi scenari.",
        "Rispondi in Markdown usando esattamente queste sezioni:",
        "",
        "1. **Stato finale degli scenari eseguiti**",
        "   Riassumi in breve gli scenari eseguiti e quale evidenza hanno prodotto.",
        "",
        "2. **Conclusione finale**",
        "   Indica la conclusione diagnostica piu forte raggiunta finora.",
        "",
        "3. **Cosa e stato risolto e cosa no**",
        "   Distingui tra problema risolto, causa localizzata, limite topologico o risultato inconclusivo.",
        "",
        "4. **Motivazione tecnica**",
        "   Giustifica la conclusione con i file scenario e base piu importanti.",
        "",
        "5. **Prossimo passo fuori budget**",
        "   Spiega quale sarebbe il passo successivo solo come sviluppo futuro, senza proporre un nuovo scenario eseguibile.",
        "",
        "`Richiede immagine: si/no`",
    ]


def build_final_conclusion_on_request_answer_format() -> list[str]:
    """Formato usato quando l'utente chiede una conclusione finale prima del budget finale."""
    return [
        "L'utente chiede una conclusione finale o una sintesi dei test eseguiti.",
        "Usa come evidenza principale gli scenari gia eseguiti e la base run.",
        "Non proporre automaticamente un nuovo scenario in questa risposta.",
        "Proponi un ulteriore scenario solo se e davvero l'unico test decisivo rimasto e dichiaralo esplicitamente come ultimo possibile passo utile.",
        "Se decidi di fermarti, non includere alcun blocco JSON scenario e non usare `actions: []` come segnaposto.",
        "Rispondi in Markdown usando esattamente queste sezioni:",
        "",
        "1. **Stato degli scenari eseguiti**",
        "   Riassumi in breve che cosa ha mostrato ogni scenario eseguito.",
        "",
        "2. **Ipotesi rafforzate e ipotesi indebolite**",
        "   Spiega quali ipotesi sono state supportate dai test e quali invece hanno perso forza.",
        "",
        "3. **Conclusione finale**",
        "   Dai la conclusione piu forte raggiungibile con le evidenze attuali.",
        "",
        "4. **Cosa non e stato dimostrato**",
        "   Dichiara cosa resta non verificato o non concludibile dai dati attuali.",
        "",
        "5. **Conviene continuare?**",
        "   Spiega se ha senso fare un altro scenario oppure se e piu corretto fermarsi qui.",
        "   Se suggerisci un altro scenario, deve essere chiaramente motivato come ultimo test davvero informativo.",
        "",
        "`Richiede immagine: si/no`",
    ]


def build_topology_failure_answer_format() -> list[str]:
    """Formato speciale per circuiti falliti con forti segnali di errore topologico."""
    return [
        "Il circuito e in modalita di fallimento topologico: le evidenze strutturate indicano che il Graph JSON o la topologia estratta non sono ancora abbastanza affidabili.",
        "Rispondi in Markdown usando esattamente queste sezioni:",
        "",
        "1. **Stato della simulazione**",
        "   Spiega che ngspice non ha prodotto una simulazione affidabile e riassumi il tipo di fallimento.",
        "",
        "2. **Evidenze di errore topologico**",
        "   Elenca le prove strutturate piu forti: mancanza di ground, nodi singleton, componenti critici saltati, sorgenti spezzate, rami isolati o warning che rendono il graph poco affidabile.",
        "",
        "3. **Diagnosi rispetto al problema utente**",
        "   Collega il fallimento topologico al sintomo utente e spiega perche il problema non puo essere attribuito con fiducia a una sola causa elettrica.",
        "",
        "4. **Scenari di correzione proposti**",
        "   Proponi al massimo 3 scenari candidati.",
        "   In questa modalita gli scenari possono essere anche di correzione topologica o graph-correction.",
        "   Ogni scenario deve dire chiaramente se e `eseguibile ora` oppure `futuro / non ancora eseguibile`.",
        "   Se non e eseguibile ora, spiega quale informazione o quale correzione del graph servirebbe prima di rieseguire SPICE.",
        "   Non proporre solo prove elettriche semplici se le evidenze dicono che la topologia di base non e affidabile.",
        "",
        "5. **Limiti e dato mancante**",
        "   Spiega qual e il dato mancante piu importante per sbloccare la diagnosi, per esempio l'immagine reale o una correzione della topologia riconosciuta.",
        "",
        "6. **Conclusione provvisoria**",
        "   Riassumi in modo netto perche il collo di bottiglia attuale e topologico e non ancora una diagnosi elettrica conclusiva.",
        "",
        *build_scenario_answer_format(),
        "",
        "Alla fine aggiungi una riga:",
        "",
        "`Richiede immagine: si/no`",
        "",
        "In questa modalita, se la correzione topologica dipende davvero dall'immagine, usa normalmente `si`.",
    ]


def build_answer_format(user_problem: str = "", summary: dict[str, Any] | None = None) -> list[str]:
    """Definisce la struttura obbligatoria della risposta finale."""
    scenario_budget = summary.get("_scenario_budget") if isinstance(summary, dict) else None
    if isinstance(scenario_budget, dict) and scenario_budget.get("budget_exhausted"):
        return build_final_conclusion_after_budget_answer_format()
    if is_final_conclusion_request(user_problem):
        return build_final_conclusion_on_request_answer_format()
    if is_next_scenario_request(user_problem):
        return build_next_scenario_answer_format()
    if is_executed_scenario_question(user_problem) and has_executed_scenario_evidence(summary):
        return build_executed_scenario_answer_format()
    if has_strong_topology_failure(summary):
        return build_topology_failure_answer_format()

    return [
        "Rispondi in Markdown usando esattamente queste sezioni:",
        "",
        "1. **Stato della simulazione**",
        "   Spiega se ngspice e stato eseguito correttamente oppure no.",
        "",
        "2. **Evidenze principali**",
        "   Elenca le prove piu importanti, citando componenti, nodi, netlist, stdout/stderr o report.",
        "",
        "3. **Diagnosi rispetto al problema utente**",
        "   Collega le evidenze al problema scritto dall'utente.",
        "",
        "4. **Limiti della diagnosi**",
        "   Dichiara cosa non si puo concludere dai dati disponibili.",
        "",
        "5. **Scenari proposti**",
        "   Proponi al massimo 3 scenari diagnostici candidati, pensati per essere trasformati in una nuova simulazione SPICE.",
        "   In questa prima risposta proponi solo scenari semplici di primo passaggio, non scenari combinati.",
        "   Non proporre semplici consigli generici: ogni scenario deve essere una ipotesi verificabile.",
        "   Non presentarli come certamente risolutivi: sono candidati da testare.",
        "   Ogni scenario iniziale deve testare una singola ipotesi principale ed essere leggibile da solo.",
        "   Se servono piu scenari, ordinali dal piu semplice al piu utile.",
        "   Se la domanda dell'utente riguarda scenari gia eseguiti, usa questa sezione per riassumere gli scenari eseguiti e indicare quale outcome e piu forte.",
        "   Se dai dati disponibili non serve uno scenario, scrivi: `Nessuno scenario necessario dai dati disponibili.`",
        "",
        "6. **Conclusione provvisoria**",
        "   Chiudi con una sintesi breve della diagnosi piu probabile in questo momento e del perche gli scenari proposti sono i passi successivi migliori.",
        "",
        *build_scenario_answer_format(),
        "",
        "Alla fine aggiungi una riga:",
        "",
        "`Richiede immagine: si/no`",
        "",
        "Metti `si` solo se gli output strutturati indicano una probabile incoerenza del Graph JSON oppure se SPICE non e eseguibile in modo utile.",
        "Se l'immagine sarebbe solo una verifica opzionale, metti comunque `no` e cita la verifica opzionale nei limiti.",
    ]


def build_prompt_operating_rules() -> list[str]:
    """Definisce regole operative adatte al prompt gia caricato."""
    return [
        "Treat the evidence sections below as the only technical evidence available in this prompt.",
        "When useful, cite component IDs, node IDs, file names or artifact sections.",
        "Use the original artifact paths only as traceability references.",
        "If an artifact is missing or truncated, mention the limitation before drawing conclusions from it.",
        "Keep the user-facing structure stable across answers: use explicit headings such as `Scenari proposti`, `Conclusione provvisoria` and `Conclusione finale` whenever they are relevant.",
        "The ordinary reasoning should stay concise and readable; the scenario list should look operational, not like a long free-form essay.",
        "If executed scenario evidence is available, use it to answer questions about which scenario explains or resolves the problem.",
        "When discussing executed scenarios, distinguish the controlled action from the diagnostic outcome.",
        "For questions about which scenario resolves the problem, do not merely list scenarios: identify the strongest scenario and justify it from scenario_comparison.json.",
        "Treat `resolved_candidate` with `stop_automation=true` as the strongest executed-scenario outcome.",
        "Treat `partially_resolved` as supporting diagnostic evidence, not as the main resolving scenario when a resolved_candidate exists.",
        "Treat `not_resolved` as not sufficient by itself, not automatically useless.",
        "A `not_resolved` scenario may still be an enabling condition for a combined scenario when it closes a switch, creates a reference path, completes a current path, or supplies a precondition missing in another scenario.",
        "In the initial answer for a circuit, propose only first-pass scenarios and do not propose combined scenarios.",
        "Combined scenarios are allowed only after scenario evidence exists and the user explicitly asks what to try next.",
        "Every next scenario must be executable from the base run on its own, because scenario runs do not inherit modifications from earlier scenario folders.",
        "If a next scenario needs an enabling condition demonstrated by an earlier scenario, include that enabling action again in the new scenario JSON.",
        "If the user asks what to try next after executed scenarios, propose the next most informative scenario based on scenario_comparison.json.",
        "If the user explicitly asks for a final conclusion, a final diagnosis, a summary of executed scenarios, or whether it makes sense to stop, switch to final-conclusion mode instead of default next-scenario mode.",
        "For LED blinking symptoms, use `led_profiles` as primary temporal evidence: compare state, regular_period, frequency_hz, duty_cycle, on_fraction and pulse_count.",
        "Do not claim that a pulse-regularity metric is missing when `led_profiles` is available.",
        "In final-conclusion mode, use the executed scenarios and their comparisons as the primary evidence, together with the base run.",
        "In final-conclusion mode, do not automatically generate another scenario just because the budget is not exhausted.",
        "In final-conclusion mode, suggest one more scenario only if it is clearly the single remaining decisive test and explain why the already executed scenarios are not enough without it.",
        "In final-conclusion mode, if the executed evidence already points to a structural limit, a topological ambiguity, or an inconclusive but bounded diagnosis, say that clearly instead of forcing another electrical scenario.",
        "When final-conclusion mode does not identify a decisive executable test, do not output a scenario JSON block and do not create a placeholder scenario with an empty actions array.",
        "If one executed scenario already changed the nodes, branches or currents most closely tied to the user symptom, prefer extending that proven direction before proposing a weaker exploratory source-value change.",
        "Prefer a minimal combined scenario built around the strongest symptom-linked evidence before proposing a generic source-value variation, unless the source itself is the strongest evidence-backed hypothesis.",
        "Prefer `change_component_value` when the hypothesis can be tested by varying the value of an already emitted resistor, capacitor, inductor or equivalent simple component.",
        "Use `change_source_value` only for existing SPICE sources, not for passive components.",
        "Use `add_voltage_source_between_nodes` when the base netlist lacks a realistic external excitation and the natural diagnostic move is to power the circuit from existing interface nodes such as connector pins, supply labels or input/return nodes.",
        "Prefer `add_voltage_source_between_nodes` over `drive_node_voltage` when the goal is to energize the whole circuit or a whole input path, not only to isolate a single internal branch node.",
        "Use `drive_node_voltage` mainly for controlled isolation tests or when no more natural value/source/state action is available.",
        "Use `set_initial_node_voltage` only with `analysis: tran` to break an artificial symmetric initial state; it emits a temporary `.ic` constraint, adds no source and must not be used to power the circuit.",
        "Use `add_resistor_between_nodes` when the hypothesis is not a missing ideal continuity, but a missing or too-weak resistive branch such as a pull-up, pull-down, shunt or additional bias path between two existing nodes.",
        "For `add_resistor_between_nodes`, provide a concrete resistor value and prefer simple plausible values already present in the circuit scale, for example `1k`, `10k`, `33k`, `47k`, `100k`, rather than arbitrary uncommon numbers.",
        "Do not use `add_resistor_between_nodes` when the real hypothesis is only to vary the value of an already emitted resistor; in that case prefer `change_component_value`.",
        "Use `feed_nodes_from_source_node` when a node is already powered in the base run, or made powered by another action in the same scenario, and the hypothesis is that this supply should propagate to one or more target branch-input nodes.",
        "Prefer `feed_nodes_from_source_node` over multiple separate `connect_nodes` only when the diagnostic idea is explicitly supply propagation from one source node to one or more targets.",
        "Do not use `feed_nodes_from_source_node` when the base netlist has no active source node; in that case prefer `add_voltage_source_between_nodes` for realistic circuit excitation, or `drive_node_voltage` only for a later isolation test.",
        "Never exceed the scenario budget declared in the manifest.",
        "If `scenario_budget.last_scenario_available` is true, propose only one final executable scenario.",
        "If `scenario_budget.budget_exhausted` is true, do not propose any new scenario and provide a final diagnostic conclusion.",
        "If no executed scenario resolved the problem, consider combined scenarios when previous outcomes provide complementary evidence, including `not_resolved` actions that are electrically enabling.",
        "Do not combine every previous scenario blindly; explain why each included action is useful and why excluded actions are not included.",
        "A next combined scenario must be self-contained and use only supported action types.",
        "A next combined scenario should repeat only the enabling actions it actually needs, not every previously proposed or executed action.",
        "If ngspice failed and the structured evidence shows strong topology problems, do not remain in simple electrical-scenario mode.",
        "Strong topology problems include signals such as no ground/reference, critical singleton nodes, skipped critical components, isolated branches, split sources, or Graph JSON warnings that make the extracted circuit untrustworthy.",
        "In that case, explain the failure first, request the real image, and prefer topology-correction or graph-correction scenarios over simple node-driving or source-value scenarios.",
        "Do not use the original image unless the structured evidence suggests that the Graph JSON may be wrong.",
        "If image access is needed, explain which structured evidence justifies it.",
        "Request image access only for strong structured reasons: Graph JSON warnings, suspicious or missing connections, important singleton nodes, missing critical components, unsupported critical topology, or ngspice failure caused by topology/convergence issues.",
        "When ngspice failed and multiple strong topology signals are present, `Richiede immagine: si` should normally be the expected outcome.",
        "If ngspice succeeds and graph/node-map evidence is internally coherent, do not request the image by default.",
        "If ngspice failed with strong topology signals, the initial scenarios may be graph-correction or topology-correction proposals, and they may be marked as future/not yet executable when appropriate.",
        "In topology-failure mode, do not force every scenario into the current executable primitive set if the real bottleneck is an untrustworthy graph.",
        "In read-only mode, do not modify netlists, do not change values and do not execute scenarios.",
        *build_scenario_operating_rules(),
    ]


def build_artifact_index(artifacts: dict[str, Any]) -> list[str]:
    """Crea l'indice degli artefatti disponibili nel prompt."""
    lines = []
    for artifact_name, metadata in artifacts.items():
        availability = "available" if metadata.get("available") else "missing"
        lines.append(
            f"- `{artifact_name}`: {availability}, path=`{metadata.get('path')}`"
        )
    return lines


def build_evidence_sections(artifacts: dict[str, Any]) -> list[str]:
    """Carica gli artefatti selezionati e li inserisce come evidenze."""
    lines: list[str] = []

    for artifact_name in PROMPT_ARTIFACT_ORDER:
        metadata = artifacts.get(artifact_name) or {}
        lines.extend([f"### {artifact_name}", ""])

        if not metadata.get("available"):
            lines.extend(["Evidence not available.", ""])
            continue

        path = resolve_artifact_path(metadata.get("path"))
        if path is None or not path.exists():
            lines.extend(["Evidence listed in the manifest, but the file was not found.", ""])
            continue

        text = read_artifact_text(path)
        text, truncated = limit_text(text, MAX_PROMPT_ARTIFACT_CHARS)
        language = artifact_language(path)

        lines.extend(
            [
                f"- Role: {metadata.get('role')}",
                f"- Path: `{metadata.get('path')}`",
                "",
                f"```{language}",
                text,
                "```",
                "",
            ]
        )

        if truncated:
            lines.extend(
                [
                    "> Evidence truncated for prompt size. Use only the visible evidence, and mention if more detail may be needed.",
                    "",
                ]
            )

    return lines


def build_executed_scenario_index(executed_scenarios: list[dict[str, Any]]) -> list[str]:
    """Crea un indice breve degli scenari gia disponibili."""
    if not executed_scenarios:
        return ["No executed scenarios are available in the manifest."]

    lines: list[str] = []
    for scenario in executed_scenarios:
        outcome = scenario.get("diagnostic_outcome") or {}
        summary = scenario.get("comparison_summary") or {}
        lines.append(
            "- "
            f"`{scenario.get('scenario_id')}`: "
            f"title=`{scenario.get('title')}`, "
            f"status=`{scenario.get('status')}`, "
            f"spice=`{scenario.get('spice_status')}`, "
            f"outcome=`{outcome.get('status')}`, "
            f"stop_automation=`{outcome.get('stop_automation')}`, "
            f"changed=`{summary.get('changed_count')}/{summary.get('requested_count')}`"
        )
        led_profiles = scenario.get("led_profiles") or {}
        if led_profiles:
            lines.append(f"  LED profiles: `{json.dumps(led_profiles, ensure_ascii=False)}`")
    return lines


def build_scenario_outcome_summary_section(summary: dict[str, Any]) -> list[str]:
    """Inserisce nel prompt una sintesi computata degli outcome scenario."""
    if not summary or not summary.get("available"):
        return ["No scenario outcome summary available."]

    return [
        "```json",
        json.dumps(summary, indent=2, ensure_ascii=False),
        "```",
        "",
        "Interpretation rule for scenario questions:",
        "- Use `best_scenario_id` only when `ranking_status` is `verified_best`.",
        "- If `ranking_status` is `no_verified_best`, compare direct symptom-linked evidence instead of inventing a winner.",
        "- `changed_count` alone proves only a numerical difference, not an improvement.",
        "- A `resolved_candidate` with `stop_automation=true` is the main resolving candidate.",
        "- `partially_resolved` scenarios can confirm supporting hypotheses but should not be presented as the scenario that solved the problem when a resolved candidate exists.",
    ]


def build_executed_scenario_sections(executed_scenarios: list[dict[str, Any]]) -> list[str]:
    """Carica gli artefatti principali degli scenari eseguiti."""
    if not executed_scenarios:
        return ["No executed scenario evidence available.", ""]

    lines: list[str] = []
    for scenario in executed_scenarios:
        scenario_id = scenario.get("scenario_id") or "scenario"
        lines.extend(
            [
                f"### {scenario_id}",
                "",
                f"- Title: `{scenario.get('title')}`",
                f"- Scenario dir: `{scenario.get('scenario_dir')}`",
                f"- Status: `{scenario.get('status')}`",
                f"- SPICE status: `{scenario.get('spice_status')}`",
                "",
            ]
        )

        artifacts = scenario.get("artifacts") or {}
        for artifact_name in (
            "scenario_definition",
            "scenario_status",
            "controlled_scenario_report",
            "scenario_comparison",
        ):
            metadata = artifacts.get(artifact_name) or {}
            lines.extend([f"#### {artifact_name}", ""])
            if not metadata.get("available"):
                lines.extend(["Evidence not available.", ""])
                continue

            path = resolve_artifact_path(metadata.get("path"))
            if path is None or not path.exists():
                lines.extend(["Evidence listed in the manifest, but the file was not found.", ""])
                continue

            text = read_artifact_text(path)
            text, truncated = limit_text(text, MAX_PROMPT_ARTIFACT_CHARS)
            language = artifact_language(path)
            lines.extend(
                [
                    f"- Role: {metadata.get('role')}",
                    f"- Path: `{metadata.get('path')}`",
                    "",
                    f"```{language}",
                    text,
                    "```",
                    "",
                ]
            )
            if truncated:
                lines.extend(
                    [
                        "> Scenario evidence truncated for prompt size.",
                        "",
                    ]
                )

    return lines


def build_agent_prompt(
    manifest: dict[str, Any],
    user_problem: str,
) -> str:
    """
    Crea il prompt Markdown per l'agente read-only.

    Il prompt include istruzioni, problema utente, riepilogo tecnico, policy
    immagine, indice artefatti ed evidenze selezionate.
    """
    summary = manifest.get("summary") or {}
    artifacts = manifest.get("artifacts") or {}
    executed_scenarios = manifest.get("executed_scenarios") or []
    scenario_outcome_summary = manifest.get("scenario_outcome_summary") or {}
    scenario_budget = manifest.get("scenario_budget") or {}
    image_access = manifest.get("image_access") or {}
    answer_summary = dict(summary)
    answer_summary["_scenario_budget"] = scenario_budget

    lines = [
        "# Diagnostic agent prompt",
        "",
        "## System instructions",
        "",
        *[f"- {instruction}" for instruction in build_system_instructions()],
        "",
        "## Operating rules",
        "",
        *[f"- {rule}" for rule in build_prompt_operating_rules()],
    ]

    lines.extend(
        [
            "",
            "## User problem",
            "",
            user_problem.strip() or "No user problem provided.",
            "",
            "## Circuit metadata",
            "",
            f"- Batch: `{manifest.get('batch_name')}`",
            f"- Circuit: `{manifest.get('circuit_id')}`",
            f"- Agent mode: `{manifest.get('agent_mode')}`",
            "",
            "## Technical summary",
            "",
            "```json",
            json.dumps(summary, indent=2, ensure_ascii=False),
            "```",
            "",
            "## Available artifacts",
            "",
            *build_artifact_index(artifacts),
            "",
            "## Executed scenarios index",
            "",
            *build_executed_scenario_index(executed_scenarios),
            "",
            "## Scenario outcome summary",
            "",
            *build_scenario_outcome_summary_section(scenario_outcome_summary),
            "",
            "## Scenario budget",
            "",
            "```json",
            json.dumps(scenario_budget, indent=2, ensure_ascii=False),
            "```",
            "",
            "## Image access policy",
            "",
            f"- Included by default: `{image_access.get('included_by_default')}`",
            f"- Can be requested: `{image_access.get('can_be_requested')}`",
            f"- Path: `{image_access.get('path')}`",
            f"- Policy: {image_access.get('policy')}",
            "",
            "## Diagnostic scenario meaning",
            "",
            *build_scenario_guidance(),
            "",
            "## Evidence to analyze",
            "",
            *build_evidence_sections(artifacts),
            "",
            "## Executed scenario evidence",
            "",
            *build_executed_scenario_sections(executed_scenarios),
            "",
            "## Required answer format",
            "",
            *build_answer_format(user_problem, answer_summary),
            "",
            "## Final task",
            "",
            "Analyze the user problem using the evidence above.",
            "Explain what the simulation result means, whether it supports the user problem, and what can or cannot be concluded.",
            "If ngspice failed, focus on the error evidence and explain why the current circuit is not diagnostically reliable.",
            "If ngspice failed with strong topology evidence, switch to topology-correction reasoning and make it explicit when a proposed scenario is future/not yet executable.",
            "If ngspice succeeded, connect the simulated node voltages, currents, skipped components and warnings to the user problem.",
            "If the question is about already executed scenarios, use the executed scenario evidence and clearly identify the strongest outcome.",
            "When suggesting new future diagnostic scenarios, present them only as controlled SPICE-verifiable hypotheses.",
            "Keep scenarios natural and minimally invasive before proposing topology or Graph JSON corrections.",
        ]
    )

    return "\n".join(lines).rstrip() + "\n"


def write_agent_prompt(
    context_path: str | Path,
    user_problem: str,
    output_path: str | Path | None = None,
) -> Path:
    """Legge il manifest 10 e salva il prompt dello step 11."""
    manifest_path = Path(context_path)
    manifest = load_json(manifest_path)
    destination = Path(output_path) if output_path else manifest_path.parent / DEFAULT_PROMPT_OUTPUT_NAME
    prompt = build_agent_prompt(manifest, user_problem)
    destination.write_text(prompt, encoding="utf-8")
    return destination
