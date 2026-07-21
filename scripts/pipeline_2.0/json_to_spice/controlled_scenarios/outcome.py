"""Classificazione prudente dell'esito diagnostico di uno scenario."""

from __future__ import annotations

from typing import Any

from scenario_expectations import MIN_MEANINGFUL_RELATIVE_CHANGE


def evaluate_diagnostic_outcome(
    summary: dict[str, Any],
    analysis: str = "op",
    intent: str = "diagnostic",
) -> dict[str, Any]:
    """
    Valuta in modo prudente se uno scenario sembra risolvere il problema.

    Questa non e una diagnosi semantica definitiva: e un criterio automatico
    semplice basato sui confronti SPICE richiesti dallo scenario. Serve per
    capire se l'automazione puo fermarsi o se conviene provare un altro scenario.
    """
    # Solo la dichiarazione esplicita `correction` puo autorizzare lo stop.
    # Valori mancanti o non riconosciuti restano diagnostici per evitare che
    # una semplice precondizione elettrica venga scambiata per sintomo risolto.
    intent = "correction" if str(intent).strip().lower() == "correction" else "diagnostic"

    requested = int(summary.get("requested_count") or 0)
    changed = int(summary.get("changed_count") or 0)
    activated = int(summary.get("activated_count") or 0)
    missing = int(summary.get("missing_count") or 0)
    expected = int(summary.get("expected_count") or 0)
    expectations_met = int(summary.get("expectations_met_count") or 0)
    expectations_missing = int(summary.get("expectations_missing_count") or 0)
    meaningful_improvements = int(summary.get("meaningful_improvement_count") or 0)
    quality_required = bool(summary.get("quality_required"))
    quality_available = bool(summary.get("quality_available"))
    quality_improved = bool(summary.get("quality_improved"))
    quality_acceptable = bool(summary.get("quality_acceptable"))
    quality_output_preserved = bool(summary.get("quality_output_preserved"))
    base_thd = summary.get("base_thd")
    scenario_thd = summary.get("scenario_thd")
    gain_required = bool(summary.get("gain_required"))
    gain_available = bool(summary.get("gain_available"))
    gain_sufficient = bool(summary.get("gain_sufficient"))
    scenario_gain = summary.get("scenario_gain")
    min_gain_ratio = summary.get("min_gain_ratio")

    if expected > 0 and expectations_missing > 0:
        status = "partially_resolved"
        technical_label = "Partially resolved"
        label = "Criteri verificati solo in parte"
        reason = (
            "Almeno una misura necessaria ai criteri di successo non e disponibile "
            "negli output SPICE dello scenario."
        )
        stop_automation = False
    elif gain_required and not gain_available:
        status = "partially_resolved" if intent == "correction" else "unknown"
        technical_label = "Signal gain unavailable"
        label = "Trasferimento del segnale non misurabile"
        reason = (
            "Lo scenario richiede una soglia minima di trasferimento, ma il "
            "rapporto Vpp uscita/ingresso non e disponibile."
        )
        stop_automation = False
    elif gain_required and not gain_sufficient:
        status = "partially_resolved" if intent == "correction" else "not_resolved"
        technical_label = "Signal gain below threshold"
        label = "Trasferimento del segnale insufficiente"
        reason = (
            "Il rapporto Vpp uscita/ingresso resta sotto la soglia dichiarata "
            f"dallo scenario ({float(scenario_gain):.6g} < {float(min_gain_ratio):.6g})."
        )
        stop_automation = False
    elif intent == "correction" and quality_required and not quality_available:
        status = "partially_resolved"
        technical_label = "Signal quality unavailable"
        label = "Qualita del segnale non misurabile"
        reason = (
            "La correzione riguarda la distorsione, ma non e stato possibile "
            "calcolare la THD su oscillazioni complete della sorgente SIN."
        )
        stop_automation = False
    elif intent == "correction" and quality_required and not quality_improved:
        status = "partially_resolved"
        technical_label = "Distortion not improved"
        label = "Distorsione non migliorata abbastanza"
        reason = (
            "La THD dell'uscita non diminuisce almeno del 20% rispetto alla base "
            f"({float(base_thd):.1%} -> {float(scenario_thd):.1%})."
        )
        stop_automation = False
    elif intent == "correction" and quality_required and not quality_acceptable:
        status = "partially_resolved"
        technical_label = "Residual distortion"
        label = "Distorsione ridotta ma ancora elevata"
        reason = (
            "La THD migliora, ma resta sopra la soglia del 10% richiesta per "
            f"una correzione risolutiva ({float(base_thd):.1%} -> "
            f"{float(scenario_thd):.1%})."
        )
        stop_automation = False
    elif intent == "correction" and quality_required and not quality_output_preserved:
        status = "partially_resolved"
        technical_label = "Output not preserved"
        label = "Segnale utile non preservato"
        reason = (
            "La distorsione diminuisce, ma il guadagno fondamentale o la "
            "componente utile dell'uscita risultano troppo ridotti."
        )
        stop_automation = False
    elif (
        intent == "correction"
        and expected > 0
        and expectations_met == expected
        and meaningful_improvements == 0
    ):
        status = "partially_resolved"
        technical_label = "Improvement too small"
        label = "Variazione non ancora significativa"
        reason = (
            "I criteri direzionali sono soddisfatti, ma nessun effetto correttivo "
            f"raggiunge la soglia relativa del {MIN_MEANINGFUL_RELATIVE_CHANGE:.0%}."
        )
        stop_automation = False
    elif expected > 0 and expectations_met == expected:
        status = "resolved_candidate"
        technical_label = "Candidate resolved"
        label = "Criteri di successo soddisfatti"
        reason = (
            "Tutti i comportamenti attesi dichiarati dallo scenario sono "
            "verificati dagli output SPICE."
        )
        stop_automation = True
    elif expected > 0 and expectations_met == 0:
        status = "not_resolved"
        technical_label = "Not resolved"
        label = "Criteri di successo non soddisfatti"
        reason = (
            "Nessuno dei comportamenti attesi dichiarati dallo scenario e "
            "stato verificato."
        )
        stop_automation = False
    elif expected > 0:
        status = "partially_resolved"
        technical_label = "Partially resolved"
        label = "Criteri verificati solo in parte"
        reason = "Solo una parte dei comportamenti attesi dichiarati dallo scenario e stata verificata."
        stop_automation = False
    elif requested == 0:
        status = "unknown"
        technical_label = "Outcome unknown"
        label = "Esito non determinabile"
        reason = "Lo scenario non definisce grandezze di confronto sufficienti per valutarne l'esito."
        stop_automation = False
    elif missing == requested:
        status = "unknown"
        technical_label = "Outcome unknown"
        label = "Confronto incompleto"
        reason = "Nessuna delle grandezze richieste e disponibile negli output SPICE dello scenario."
        stop_automation = False
    elif changed == 0:
        status = "not_resolved"
        technical_label = "Not resolved"
        label = "Scenario non informativo"
        reason = "Le grandezze richieste non cambiano rispetto alla run base, quindi questo test non aggiunge evidenza utile."
        stop_automation = False
    elif missing > 0:
        status = "partially_resolved"
        technical_label = "Partially resolved"
        label = "Ipotesi confermata sul ramo testato"
        reason = (
            "Lo scenario conferma utilmente l'ipotesi sulle grandezze disponibili, "
            "anche se almeno un confronto richiesto resta mancante o incompleto."
        )
        stop_automation = False
    elif analysis == "tran" and changed == requested:
        status = "partially_resolved"
        technical_label = "Partially resolved"
        label = "Ipotesi confermata sul ramo testato"
        reason = (
            "Le forme d'onda richieste cambiano tutte nel transitorio, quindi l'ipotesi e supportata, "
            "ma questo da solo non basta per fermare automaticamente la diagnosi."
        )
        stop_automation = False
    elif changed == requested and activated > 0:
        status = "resolved_candidate"
        technical_label = "Candidate resolved"
        label = "Ipotesi fortemente confermata"
        reason = "Tutte le grandezze richieste cambiano e almeno una grandezza prima inattiva si attiva davvero."
        stop_automation = True
    else:
        status = "partially_resolved"
        technical_label = "Partially resolved"
        label = "Ipotesi confermata sul ramo testato"
        reason = (
            "Lo scenario modifica il comportamento del circuito in modo utile, "
            "ma l'evidenza resta locale o non abbastanza forte per fermarsi automaticamente."
        )
        stop_automation = False

    # Un test diagnostico puo confermare una causa, ma non rappresenta una correzione.
    if intent == "diagnostic" and stop_automation:
        status = "partially_resolved"
        technical_label = "Diagnostic hypothesis confirmed"
        label = "Ipotesi diagnostica confermata"
        reason = (
            "I criteri dichiarati dal test diagnostico sono soddisfatti, ma lo "
            "scenario non applica una correzione del sintomo utente."
        )
        stop_automation = False

    user_message = {
        "resolved_candidate": "Lo scenario fornisce una conferma forte dell'ipotesi testata.",
        "partially_resolved": "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato.",
        "not_resolved": "Lo scenario non ha prodotto un cambiamento utile rispetto alla base.",
        "unknown": "Non ci sono abbastanza dati per valutare con affidabilita l'esito dello scenario.",
    }.get(status, "Lo scenario produce un risultato tecnico che richiede ancora interpretazione.")

    next_step = (
        "Ci sono gia evidenze forti per fermarsi qui e passare alla conclusione diagnostica."
        if stop_automation
        else "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
    )

    return {
        "status": status,
        "technical_label": technical_label,
        "label": label,
        "reason": reason,
        "user_message": user_message,
        "stop_automation": stop_automation,
        "confidence": "medium" if status == "resolved_candidate" else "low",
        "next_step": next_step,
    }
