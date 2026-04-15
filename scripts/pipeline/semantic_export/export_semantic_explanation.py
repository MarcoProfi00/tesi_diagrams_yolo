from __future__ import annotations

from collections import defaultdict, deque
from itertools import combinations
from typing import Any


GROUND_COMPONENT_CLASSES = {"gnd"}
SUPPLY_COMPONENT_CLASSES = {"battery", "voltage_source", "current_source"}
EXTERNAL_INTERFACE_CLASSES = {"terminal"}
ACTIVE_COMPONENT_TOKENS = {"mosfet", "transistor", "opamp"}
PASSIVE_COMPONENT_CLASSES = {"resistor", "capacitor", "inductor", "diode"}
CONTROL_TERMINAL_NAMES = {
    "g",
    "gate",
    "b",
    "base",
    "ctrl",
    "control",
    "in",
    "in+",
    "in-",
    "input",
    "non_inverting_input",
    "inverting_input",
}
OUTPUT_TERMINAL_NAMES = {
    "d",
    "drain",
    "c",
    "collector",
    "out",
    "output",
    "s",
    "source",
    "e",
    "emitter",
}
TERMINAL_NAME_EXPANSIONS = {
    "g": "gate",
    "d": "drain",
    "s": "source",
    "b": "base",
    "c": "collector",
    "e": "emitter",
}

MAX_FUNCTIONAL_PATHS = 5
MAX_BRANCH_SUMMARIES = 8
MAX_MARKDOWN_BRANCHES = 6
MAX_MARKDOWN_PATTERNS = 10
MAX_MARKDOWN_TERMINAL_FACTS = 10

IMPORTANCE_PRIORITY = {"high": 3, "medium": 2, "low": 1}
PATH_PRIORITY = {
    "source_to_interface_path": 5,
    "device_to_interface_path": 4,
    "external_interface_to_device_path": 3,
    "ground_to_device_path": 2,
    "interface_bridge_path": 1,
}


def normalize_token(value: Any) -> str:
    """Normalizza token in un formato interno coerente."""
    return str(value or "").strip().lower().replace(" ", "_").replace("-", "_")


def join_or_none(values: list[Any]) -> str:
    """Unisce una lista di valori leggibili oppure restituisce none se non ci sono elementi utili."""
    cleaned = [str(value) for value in values if value is not None and str(value) != ""]
    if not cleaned:
        return "none"
    return ", ".join(cleaned)


def joined_with_and(values: list[Any]) -> str:
    """Compone una lista in una frase piu naturale usando and nell'ultimo collegamento."""
    cleaned = [str(value) for value in values if value is not None and str(value) != ""]
    if not cleaned:
        return "none"
    if len(cleaned) == 1:
        return cleaned[0]
    if len(cleaned) == 2:
        return f"{cleaned[0]} and {cleaned[1]}"
    return f"{', '.join(cleaned[:-1])}, and {cleaned[-1]}"


def titleize_label(value: str | None) -> str:
    """Converte label in un'etichetta con formattazione leggibile."""
    token = str(value or "").replace("_", " ").strip()
    return token.capitalize() if token else "Path"


def human_component_name(instance_id: str | None, class_name: str | None) -> str:
    """Restituisce un nome leggibile del componente combinando classe e instance_id quando disponibili."""
    if class_name and instance_id:
        return f"{class_name} {instance_id}"
    return class_name or instance_id or "Unknown component"


def terminal_display_id(term: dict) -> str | None:
    """Restituisce l'identificatore piu leggibile da mostrare per un terminale."""
    return term.get("display_terminal_id") or term.get("terminal_id")


def terminal_human_name(term: dict) -> str | None:
    """Restituisce il nome piu parlante disponibile per un terminale."""
    return (
        term.get("display_name")
        or term.get("semantic_terminal_name")
        or term.get("name")
        or term.get("display_terminal_id")
        or term.get("terminal_id")
    )


def expanded_terminal_name(raw_name: str | None) -> str:
    """Espande abbreviazioni e terminali numerici in etichette piu parlanti per i testi descrittivi."""
    if not raw_name:
        return "terminal"
    token = normalize_token(raw_name)
    if token in TERMINAL_NAME_EXPANSIONS:
        return TERMINAL_NAME_EXPANSIONS[token]
    if token.startswith("t") and token[1:].isdigit():
        return f"terminal {raw_name}"
    return str(raw_name)


def terminal_role_text(term: dict) -> str:
    """Restituisce il nome piu adatto da usare quando il terminale va descritto in linguaggio naturale."""
    raw_name = (
        term.get("semantic_terminal_name")
        or term.get("display_name")
        or term.get("name")
        or term.get("display_terminal_id")
        or term.get("terminal_id")
    )
    return expanded_terminal_name(raw_name)


def is_ground_component(class_name: str | None) -> bool:
    """Riconosce se il componente appartiene alla famiglia delle masse."""
    return normalize_token(class_name) in GROUND_COMPONENT_CLASSES


def is_supply_component(class_name: str | None) -> bool:
    """Riconosce se il componente rappresenta una sorgente o alimentazione."""
    return normalize_token(class_name) in SUPPLY_COMPONENT_CLASSES


def is_external_interface_component(class_name: str | None) -> bool:
    """Riconosce se il componente e usato come interfaccia esterna del circuito."""
    return normalize_token(class_name) in EXTERNAL_INTERFACE_CLASSES


def is_active_component(class_name: str | None) -> bool:
    """Riconosce se il componente appartiene alla famiglia dei dispositivi attivi."""
    token = normalize_token(class_name)
    return any(active_token in token for active_token in ACTIVE_COMPONENT_TOKENS) or token in {"switch", "relay"}


def is_passive_component(class_name: str | None) -> bool:
    """Riconosce se il componente appartiene alla famiglia dei dispositivi passivi."""
    return normalize_token(class_name) in PASSIVE_COMPONENT_CLASSES


def infer_source_component_kind(class_name: str | None) -> str:
    """Inferisce source component kind dalle evidenze disponibili."""
    if is_ground_component(class_name):
        return "ground"
    if is_supply_component(class_name):
        return "supply"
    if is_external_interface_component(class_name):
        return "external_interface"
    if is_active_component(class_name):
        return "active_component"
    if is_passive_component(class_name):
        return "passive_component"
    return "generic_component"


def representative_terminal(terminals: list[dict]) -> dict:
    """Sceglie il terminale piu rappresentativo di un gruppo per descrizioni e riepiloghi."""
    return sorted(
        terminals,
        key=lambda item: (
            str(item.get("semantic_terminal_name") or ""),
            str(item.get("display_terminal_id") or item.get("terminal_id") or ""),
        ),
    )[0]


def build_terminal_and_net_indexes(data: dict):
    """Prepara indici rapidi di componenti, terminali e net insieme alla mappa net -> terminali."""
    components = data.get("components", [])
    terminals = data.get("terminals", [])
    nets = data.get("nets", [])

    component_index = {
        str(comp["instance_id"]): comp
        for comp in components
        if comp.get("instance_id") is not None
    }
    terminal_index = {
        str(term["terminal_id"]): term
        for term in terminals
        if term.get("terminal_id") is not None
    }
    net_index = {
        str(net["net_id"]): net
        for net in nets
        if net.get("net_id") is not None
    }

    net_to_terminal_ids: dict[str, list[str]] = {}
    for term in terminals:
        terminal_id = term.get("terminal_id")
        matched_net_id = term.get("matched_net_id")
        if terminal_id is None or matched_net_id is None:
            continue
        net_to_terminal_ids.setdefault(str(matched_net_id), []).append(str(terminal_id))

    for net_id, terminal_ids in list(net_to_terminal_ids.items()):
        net_to_terminal_ids[net_id] = sorted(set(terminal_ids))

    return component_index, terminal_index, net_index, net_to_terminal_ids


def build_terminal_statement(term: dict, peer_terminals: list[dict]) -> str:
    """Genera una frase breve che descrive come un terminale e collegato nel diagramma."""
    comp_text = human_component_name(term.get("instance_id"), term.get("component_class_name"))
    terminal_name = terminal_human_name(term)
    net_id = term.get("matched_net_id")

    if net_id is None:
        return f"{comp_text} terminal {terminal_name} is currently unmatched to any net."

    if not peer_terminals:
        return f"{comp_text} terminal {terminal_name} is the only modeled terminal on net {net_id}."

    peer_components = sorted({
        human_component_name(peer.get("instance_id"), peer.get("component_class_name"))
        for peer in peer_terminals
    })
    return (
        f"{comp_text} terminal {terminal_name} is connected on net {net_id} "
        f"with {join_or_none(peer_components)}."
    )


def build_terminal_semantic_entries(
    terminals: list[dict],
    terminal_index: dict[str, dict],
    net_to_terminal_ids: dict[str, list[str]],
) -> tuple[dict[str, list[dict]], list[dict]]:
    """Costruisce le schede semantiche dei terminali arricchendole con peer, net e frasi descrittive."""
    terminal_entries_by_component: dict[str, list[dict]] = defaultdict(list)
    terminal_facts: list[dict] = []

    for term in sorted(terminals, key=lambda item: str(item.get("terminal_id") or "")):
        terminal_id = str(term.get("terminal_id"))
        net_id = term.get("matched_net_id")
        peer_terminals: list[dict] = []

        if net_id is not None:
            # Qui costruiamo esplicitamente la vista locale del terminale:
            # stessa net, stessi peer, stessa frase che poi verra riusata ovunque.
            for peer_terminal_id in net_to_terminal_ids.get(str(net_id), []):
                if peer_terminal_id == terminal_id:
                    continue
                peer = terminal_index.get(peer_terminal_id, {})
                peer_terminals.append({
                    "terminal_id": peer.get("terminal_id"),
                    "display_terminal_id": terminal_display_id(peer),
                    "instance_id": peer.get("instance_id"),
                    "component_class_name": peer.get("component_class_name"),
                    "terminal_name": terminal_human_name(peer),
                    "semantic_terminal_name": peer.get("semantic_terminal_name"),
                })

        statement = build_terminal_statement(term, peer_terminals)
        terminal_entry = {
            "terminal_id": terminal_id,
            "display_terminal_id": terminal_display_id(term),
            "terminal_name": terminal_human_name(term),
            "semantic_terminal_name": term.get("semantic_terminal_name"),
            "semantic_slot": term.get("semantic_slot"),
            "semantic_confidence": term.get("semantic_confidence"),
            "semantic_evidence_type": term.get("semantic_evidence_type"),
            "semantic_resolution_mode": term.get("semantic_resolution_mode"),
            "semantic_role_family": term.get("semantic_role_family"),
            "semantic_polarity": term.get("semantic_polarity"),
            "semantic_direction": term.get("semantic_direction"),
            "relative_position": term.get("relative_position"),
            "net_id": net_id,
            "net_index": term.get("matched_net_index"),
            "match_status": term.get("match_status"),
            "match_confidence": term.get("match_confidence"),
            "is_suspicious_match": term.get("is_suspicious_match", False),
            "peer_terminals": peer_terminals,
            "statement": statement,
        }
        instance_id = str(term.get("instance_id") or "")
        terminal_entries_by_component[instance_id].append(terminal_entry)

        terminal_facts.append({
            "terminal_id": terminal_id,
            "display_terminal_id": terminal_display_id(term),
            "instance_id": term.get("instance_id"),
            "component_class_name": term.get("component_class_name"),
            "terminal_name": terminal_human_name(term),
            "semantic_terminal_name": term.get("semantic_terminal_name"),
            "semantic_slot": term.get("semantic_slot"),
            "semantic_confidence": term.get("semantic_confidence"),
            "semantic_evidence_type": term.get("semantic_evidence_type"),
            "semantic_resolution_mode": term.get("semantic_resolution_mode"),
            "semantic_role_family": term.get("semantic_role_family"),
            "semantic_polarity": term.get("semantic_polarity"),
            "semantic_direction": term.get("semantic_direction"),
            "net_id": net_id,
            "match_status": term.get("match_status"),
            "statement": statement,
        })

    return terminal_entries_by_component, terminal_facts


def build_component_connected_components(terminal_entries: list[dict], instance_id: str) -> list[dict]:
    """Ricostruisce quali altri componenti risultano adiacenti al componente corrente tramite le net condivise."""
    peer_groups: dict[str, dict] = {}
    for entry in terminal_entries:
        for peer in entry.get("peer_terminals", []):
            peer_instance_id = str(peer.get("instance_id") or "")
            if not peer_instance_id or peer_instance_id == instance_id:
                continue
            group = peer_groups.setdefault(
                peer_instance_id,
                {
                    "instance_id": peer_instance_id,
                    "component_class_name": peer.get("component_class_name"),
                    "via_net_ids": set(),
                },
            )
            if entry.get("net_id") is not None:
                group["via_net_ids"].add(str(entry["net_id"]))

    connected_components = [
        {
            "instance_id": item["instance_id"],
            "component_class_name": item.get("component_class_name"),
            "via_net_ids": sorted(item["via_net_ids"]),
        }
        for item in peer_groups.values()
    ]
    connected_components.sort(key=lambda item: str(item.get("instance_id") or ""))
    return connected_components


def classify_external_interface(terminal_entries: list[dict]) -> tuple[str, float, str, str | None, list[str]]:
    """Stima se un'interfaccia esterna si comporta piu come ingresso, uscita o ponte tra piu net."""
    connected_nets = sorted({
        str(entry.get("net_id"))
        for entry in terminal_entries
        if entry.get("net_id") is not None
    })
    peer_semantics = {
        normalize_token(peer.get("semantic_terminal_name") or peer.get("terminal_name") or peer.get("display_terminal_id"))
        for entry in terminal_entries
        for peer in entry.get("peer_terminals", [])
    }
    has_control_like = bool(peer_semantics & CONTROL_TERMINAL_NAMES)
    has_output_like = bool(peer_semantics & OUTPUT_TERMINAL_NAMES)

    if len(connected_nets) >= 2:
        return (
            "external_interface",
            0.82,
            "medium",
            "bridge_interface",
            [f"The interface bridges multiple nets ({join_or_none(connected_nets)})."],
        )
    if has_control_like and not has_output_like:
        return (
            "external_interface",
            0.76,
            "medium",
            "input_interface",
            ["The interface reaches at least one control-like terminal such as gate/base/input."],
        )
    if has_output_like and not has_control_like:
        return (
            "external_interface",
            0.74,
            "low",
            "possible_output_interface",
            ["The interface reaches output-like terminals, but topology alone cannot prove output direction."],
        )
    if has_control_like and has_output_like:
        return (
            "external_interface",
            0.64,
            "low",
            "unspecified_interface",
            ["The interface reaches mixed control-like and output-like terminals, so a more specific direction would be too aggressive."],
        )
    return (
        "external_interface",
        0.68,
        "low",
        "unspecified_interface",
        ["The symbol behaves as an external access point, but topology alone does not disambiguate input vs output."],
    )


def infer_component_role(component: dict, terminal_entries: list[dict], connected_components: list[dict]) -> dict:
    """Assegna al componente un ruolo funzionale plausibile usando classe, terminali e vicinato topologico."""
    class_name = component.get("class_name")
    instance_id = component.get("instance_id")
    connected_net_ids = sorted({
        str(entry.get("net_id"))
        for entry in terminal_entries
        if entry.get("net_id") is not None
    })
    interface_kind = None

    if is_ground_component(class_name):
        role_hypothesis = "ground_reference"
        confidence = 1.0
        role_specificity = "high"
        why_role_was_assigned = ["Direct fact from explicit GND component class."]
        evidence_type = "topological_fact"
    elif is_supply_component(class_name):
        role_hypothesis = "power_source"
        confidence = 0.98
        role_specificity = "high"
        why_role_was_assigned = ["Direct fact from explicit source component class."]
        evidence_type = "topological_fact"
    elif is_external_interface_component(class_name):
        (
            role_hypothesis,
            confidence,
            role_specificity,
            interface_kind,
            why_role_was_assigned,
        ) = classify_external_interface(terminal_entries)
        evidence_type = "heuristic_inference"
    elif is_active_component(class_name):
        role_hypothesis = "active_component"
        confidence = 0.72
        role_specificity = "low"
        why_role_was_assigned = [
            "Component class indicates an active controllable device, but topology alone does not prove its exact circuit function.",
        ]
        evidence_type = "heuristic_inference"
    elif is_passive_component(class_name):
        role_hypothesis = "passive_component"
        confidence = 0.76
        role_specificity = "medium"
        why_role_was_assigned = [
            "Component class indicates a passive or directional device; the exact electrical purpose depends on the larger circuit context.",
        ]
        evidence_type = "heuristic_inference"
    elif normalize_token(class_name) == "meter":
        role_hypothesis = "measurement_or_observation_point"
        confidence = 0.78
        role_specificity = "medium"
        why_role_was_assigned = ["Component class explicitly suggests a measurement element."]
        evidence_type = "heuristic_inference"
    else:
        role_hypothesis = "generic_circuit_element"
        confidence = 0.55
        role_specificity = "low"
        why_role_was_assigned = ["No stronger class-based semantic rule was triggered."]
        evidence_type = "heuristic_inference"

    peer_summary = "; ".join(
        f"{human_component_name(item.get('instance_id'), item.get('component_class_name'))} via {join_or_none(item.get('via_net_ids', []))}"
        for item in connected_components
    ) or "no other modeled components"

    return {
        "instance_id": instance_id,
        "class_name": class_name,
        "role_hypothesis": role_hypothesis,
        "role_specificity": role_specificity,
        "description_label": role_hypothesis,
        "description_specificity": role_specificity,
        "description_basis": why_role_was_assigned,
        "confidence": confidence,
        "evidence_type": evidence_type,
        "interface_kind": interface_kind,
        "connected_nets": connected_net_ids,
        "connected_components": connected_components,
        "why_role_was_assigned": why_role_was_assigned,
        "natural_language": (
            f"{human_component_name(instance_id, class_name)} is described as {role_hypothesis.replace('_', ' ')}. "
            f"It is connected to nets {join_or_none(connected_net_ids)} and to {peer_summary}."
        ),
    }


def infer_net_role(net: dict, connected_terminals: list[dict], connected_components: list[dict]) -> dict:
    """Inferisce net role dalle evidenze disponibili."""
    net_id = str(net.get("net_id"))
    n_components = len(connected_components)
    has_ground = any(is_ground_component(item.get("component_class_name")) for item in connected_components)
    has_supply = any(is_supply_component(item.get("component_class_name")) for item in connected_components)
    has_external = any(is_external_interface_component(item.get("component_class_name")) for item in connected_components)
    has_active = any(is_active_component(item.get("component_class_name")) for item in connected_components)
    terminal_semantics = {
        normalize_token(term.get("semantic_terminal_name") or term.get("display_name") or term.get("name"))
        for term in connected_terminals
    }
    has_control_like = bool(terminal_semantics & CONTROL_TERMINAL_NAMES)
    has_output_like = bool(terminal_semantics & OUTPUT_TERMINAL_NAMES)

    if int(net.get("n_connected_terminals", 0) or 0) <= 1:
        role_hypothesis = "single_terminal_stub"
        role_specificity = "high"
        confidence = 0.96
        why_role_was_assigned = ["Only one modeled terminal reaches this net."]
    elif has_ground:
        role_hypothesis = "ground_return"
        role_specificity = "high"
        confidence = 1.0
        why_role_was_assigned = ["An explicit ground symbol is attached to this net."]
    elif has_supply:
        role_hypothesis = "source_connected_branch"
        role_specificity = "medium"
        confidence = 0.88
        why_role_was_assigned = ["An explicit source component is attached to this net."]
    elif n_components >= 4 or (n_components >= 3 and has_active and has_control_like and has_output_like):
        role_hypothesis = "shared_internal_branch"
        role_specificity = "medium"
        confidence = 0.70
        why_role_was_assigned = ["The net behaves like a multi-device internal junction and its terminal semantics are mixed or widely shared."]
    elif has_external and has_active and has_output_like and not has_control_like:
        role_hypothesis = "external_interface_branch"
        role_specificity = "medium"
        confidence = 0.74
        why_role_was_assigned = ["The net reaches an external interface and output-like active-device terminals."]
    elif has_external and has_control_like and not has_output_like:
        role_hypothesis = "external_control_branch"
        role_specificity = "medium"
        confidence = 0.74
        why_role_was_assigned = ["The net reaches an external interface and at least one control-like terminal."]
    elif has_external:
        role_hypothesis = "external_interface_branch"
        role_specificity = "low"
        confidence = 0.68
        why_role_was_assigned = ["The net reaches at least one explicit external interface."]
    elif n_components >= 3 and has_active:
        role_hypothesis = "shared_internal_branch"
        role_specificity = "medium"
        confidence = 0.72
        why_role_was_assigned = ["The net behaves like a shared internal junction between multiple components."]
    else:
        role_hypothesis = "local_interconnect"
        role_specificity = "low"
        confidence = 0.60
        why_role_was_assigned = ["The net connects a small local group without stronger semantic evidence."]

    alias = f"{role_hypothesis}_{net_id}"
    comp_text = ", ".join(
        human_component_name(item.get("instance_id"), item.get("component_class_name"))
        for item in connected_components
    ) or "no modeled components"

    return {
        "net_id": net_id,
        "alias": alias,
        "role_hypothesis": role_hypothesis,
        "role_specificity": role_specificity,
        "description_label": role_hypothesis,
        "description_specificity": role_specificity,
        "description_basis": why_role_was_assigned,
        "confidence": confidence,
        "evidence_type": "heuristic_inference" if role_hypothesis != "ground_return" else "topological_fact",
        "why_role_was_assigned": why_role_was_assigned,
        "connected_components": connected_components,
        "natural_language": f"Net {net_id} is described as {role_hypothesis.replace('_', ' ')}. It connects {comp_text}.",
    }


def branch_importance_for_net_role(role_hypothesis: str, connected_components: list[dict]) -> str:
    """Gestisce branch importance for net role all'interno di questo modulo della pipeline."""
    if role_hypothesis in {"source_connected_branch", "external_interface_branch", "external_control_branch"}:
        return "high"
    if role_hypothesis in {"shared_internal_branch", "external_interface_branch"} or len(connected_components) >= 4:
        return "medium"
    return "low"


def build_branch_summaries(net_roles: list[dict]) -> list[dict]:
    """Costruisce branch summaries a partire dagli input correnti della pipeline."""
    summary_seed: list[dict] = []
    for net_role in net_roles:
        role_hypothesis = str(net_role.get("role_hypothesis"))
        if role_hypothesis not in {
            "source_connected_branch",
            "external_interface_branch",
            "external_control_branch",
            "external_interface_branch",
            "shared_internal_branch",
            "single_terminal_stub",
        }:
            continue

        connected_components = net_role.get("connected_components", [])
        connected_ids = [str(item.get("instance_id")) for item in connected_components if item.get("instance_id")]
        importance = branch_importance_for_net_role(role_hypothesis, connected_components)
        net_id = net_role.get("net_id")
        role_text = role_hypothesis.replace("_", " ")
        component_text = join_or_none([
            human_component_name(item.get("instance_id"), item.get("component_class_name"))
            for item in connected_components
        ])

        summary_seed.append({
            "anchor_net": net_id,
            "branch_kind": role_hypothesis,
            "connected_components": connected_ids,
            "importance": importance,
            "natural_language": f"Net {net_id} forms {('an' if role_text[:1] in 'aeiou' else 'a')} {role_text} connecting {component_text}.",
        })

    summary_seed.sort(
        key=lambda item: (
            -IMPORTANCE_PRIORITY.get(str(item.get("importance")), 0),
            str(item.get("anchor_net") or ""),
        )
    )
    summaries: list[dict] = []
    for index, item in enumerate(summary_seed[:MAX_BRANCH_SUMMARIES], start=1):
        entry = dict(item)
        entry["branch_id"] = f"B{index}"
        summaries.append(entry)
    return summaries


def build_component_relation_groups(
    nets: list[dict],
    net_roles_by_id: dict[str, dict],
    terminal_index: dict[str, dict],
    net_to_terminal_ids: dict[str, list[str]],
) -> list[dict]:
    """Costruisce component relation groups a partire dagli input correnti della pipeline."""
    groups: list[dict] = []
    for net in sorted(nets, key=lambda item: int(item.get("net_index") or 0)):
        net_id = str(net.get("net_id"))
        connected_terminals = [
            terminal_index[terminal_id]
            for terminal_id in net_to_terminal_ids.get(net_id, [])
            if terminal_id in terminal_index
        ]
        component_map: dict[str, list[dict]] = defaultdict(list)
        for term in connected_terminals:
            instance_id = str(term.get("instance_id") or "")
            if instance_id:
                component_map[instance_id].append(term)

        if len(component_map) < 2:
            continue

        net_role = net_roles_by_id.get(net_id, {})
        component_bits = []
        for instance_id, terms in sorted(component_map.items()):
            rep_term = representative_terminal(terms)
            component_bits.append(
                f"{human_component_name(instance_id, rep_term.get('component_class_name'))} {terminal_role_text(rep_term)}"
            )

        groups.append({
            "net_id": net_id,
            "summary": (
                f"{net_id} is a {str(net_role.get('role_hypothesis', 'local_interconnect')).replace('_', ' ')} connecting "
                f"{join_or_none(component_bits)}."
            ),
            "connected_components": sorted(component_map.keys()),
            "importance": branch_importance_for_net_role(
                str(net_role.get("role_hypothesis")),
                net_role.get("connected_components", []),
            ),
            "role_hypothesis": net_role.get("role_hypothesis"),
        })

    groups.sort(
        key=lambda item: (
            -IMPORTANCE_PRIORITY.get(str(item.get("importance")), 0),
            str(item.get("net_id") or ""),
        )
    )
    return groups


def build_component_to_component_relations(
    nets: list[dict],
    net_roles_by_id: dict[str, dict],
    terminal_index: dict[str, dict],
    net_to_terminal_ids: dict[str, list[str]],
) -> list[dict]:
    """Costruisce component to component relations a partire dagli input correnti della pipeline."""
    relations: list[dict] = []
    for net in sorted(nets, key=lambda item: int(item.get("net_index") or 0)):
        net_id = str(net.get("net_id"))
        connected_terminals = [
            terminal_index[terminal_id]
            for terminal_id in net_to_terminal_ids.get(net_id, [])
            if terminal_id in terminal_index
        ]

        component_map: dict[str, list[dict]] = defaultdict(list)
        for term in connected_terminals:
            instance_id = str(term.get("instance_id") or "")
            if instance_id:
                component_map[instance_id].append(term)

        component_ids = sorted(component_map.keys())
        if len(component_ids) < 2:
            continue

        selected_pairs: list[tuple[str, str]] = []
        if len(component_ids) <= 3:
            selected_pairs = list(combinations(component_ids, 2))
        else:
            role = str(net_roles_by_id.get(net_id, {}).get("role_hypothesis") or "")
            anchor_ids = [
                component_id
                for component_id in component_ids
                if infer_source_component_kind(component_map[component_id][0].get("component_class_name"))
                in {"supply", "external_interface", "active_component"}
            ]
            if not anchor_ids:
                anchor_ids = component_ids[:2]
            seen_pairs = set()
            for anchor_id in anchor_ids:
                for other_id in component_ids:
                    if other_id == anchor_id:
                        continue
                    pair = tuple(sorted((anchor_id, other_id)))
                    if pair in seen_pairs:
                        continue
                    seen_pairs.add(pair)
                    selected_pairs.append(pair)
                    if role == "shared_internal_branch" and len(selected_pairs) >= 4:
                        break
                if role == "shared_internal_branch" and len(selected_pairs) >= 4:
                    break

        for left_id, right_id in selected_pairs:
            left_term = representative_terminal(component_map[left_id])
            right_term = representative_terminal(component_map[right_id])
            relations.append({
                "from_component": left_id,
                "from_terminal": left_term.get("display_terminal_id") or left_term.get("terminal_id"),
                "to_component": right_id,
                "to_terminal": right_term.get("display_terminal_id") or right_term.get("terminal_id"),
                "via_net": net_id,
                "relation_type": "electrical_connection",
                "evidence_type": "topological_fact",
                "confidence": 1.0,
                "natural_language": (
                    f"{human_component_name(left_id, left_term.get('component_class_name'))} "
                    f"{terminal_role_text(left_term)} is electrically tied to "
                    f"{human_component_name(right_id, right_term.get('component_class_name'))} "
                    f"{terminal_role_text(right_term)} through net {net_id}."
                ),
            })

    return relations


def build_component_net_adjacency(terminals: list[dict]) -> dict[tuple[str, str], set[tuple[str, str]]]:
    """Costruisce component net adjacency a partire dagli input correnti della pipeline."""
    adjacency: dict[tuple[str, str], set[tuple[str, str]]] = defaultdict(set)
    for term in terminals:
        instance_id = term.get("instance_id")
        net_id = term.get("matched_net_id")
        if instance_id is None or net_id is None:
            continue

        comp_node = ("component", str(instance_id))
        net_node = ("net", str(net_id))
        adjacency[comp_node].add(net_node)
        adjacency[net_node].add(comp_node)
    return adjacency


def shortest_path_to_targets(
    adjacency: dict[tuple[str, str], set[tuple[str, str]]],
    start: tuple[str, str],
    target_nodes: set[tuple[str, str]],
    max_depth: int = 10,
) -> list[tuple[str, str]] | None:
    """Gestisce shortest path to targets all'interno di questo modulo della pipeline."""
    if start in target_nodes:
        return [start]

    queue = deque([(start, [start])])
    visited = {start}
    while queue:
        node, path = queue.popleft()
        if len(path) > max_depth:
            continue

        for neighbor in sorted(adjacency.get(node, set())):
            if neighbor in visited:
                continue
            next_path = path + [neighbor]
            if neighbor in target_nodes:
                return next_path
            visited.add(neighbor)
            queue.append((neighbor, next_path))

    return None


def path_sequence_to_objects(
    path: list[tuple[str, str]],
    component_index: dict[str, dict],
    net_roles_by_id: dict[str, dict],
) -> list[dict]:
    """Gestisce path sequence to objects all'interno di questo modulo della pipeline."""
    sequence = []
    for kind, node_id in path:
        if kind == "component":
            comp = component_index.get(node_id, {})
            sequence.append({
                "node_type": "component",
                "id": node_id,
                "label": human_component_name(node_id, comp.get("class_name")),
                "class_name": comp.get("class_name"),
            })
        else:
            net_role = net_roles_by_id.get(node_id, {})
            sequence.append({
                "node_type": "net",
                "id": node_id,
                "label": f"{node_id} ({str(net_role.get('role_hypothesis') or '').replace('_', ' ')})",
                "role_hypothesis": net_role.get("role_hypothesis"),
            })
    return sequence


def add_functional_path(
    candidates: list[dict],
    seen_signatures: set[tuple[str, ...]],
    path_type: str,
    path: list[tuple[str, str]] | None,
    component_index: dict[str, dict],
    net_roles_by_id: dict[str, dict],
    confidence: float,
    evidence_type: str,
) -> None:
    """Gestisce add functional path all'interno di questo modulo della pipeline."""
    if not path:
        return

    signature = tuple(f"{kind}:{node_id}" for kind, node_id in path)
    reverse_signature = tuple(reversed(signature))
    if signature in seen_signatures or reverse_signature in seen_signatures:
        return

    seen_signatures.add(signature)
    sequence = path_sequence_to_objects(path, component_index, net_roles_by_id)
    start_label = sequence[0]["label"]
    end_label = sequence[-1]["label"]
    joined = " -> ".join(step["label"] for step in sequence)

    candidates.append({
        "path_type": path_type,
        "priority": PATH_PRIORITY.get(path_type, 0),
        "start": start_label,
        "end": end_label,
        "sequence": sequence,
        "confidence": confidence,
        "evidence_type": evidence_type,
        "natural_language": f"{titleize_label(path_type)}: {joined}.",
    })


def build_functional_paths(
    component_roles: list[dict],
    net_roles: list[dict],
    component_index: dict[str, dict],
    terminals: list[dict],
) -> list[dict]:
    """Costruisce functional paths a partire dagli input correnti della pipeline."""
    adjacency = build_component_net_adjacency(terminals)
    net_roles_by_id = {str(item.get("net_id")): item for item in net_roles}

    supply_nodes = {
        ("component", str(item["instance_id"]))
        for item in component_roles
        if item.get("role_hypothesis") == "power_source"
    }
    ground_nodes = {
        ("component", str(item["instance_id"]))
        for item in component_roles
        if item.get("role_hypothesis") == "ground_reference"
    }
    input_nodes = {
        ("component", str(item["instance_id"]))
        for item in component_roles
        if item.get("interface_kind") == "input_interface"
    }
    output_nodes = {
        ("component", str(item["instance_id"]))
        for item in component_roles
        if item.get("interface_kind") in {"possible_output_interface", "bridge_interface"}
    }
    bridge_interfaces = [
        item for item in component_roles
        if item.get("interface_kind") == "bridge_interface"
    ]
    active_nodes = {
        ("component", str(item["instance_id"]))
        for item in component_roles
        if item.get("role_hypothesis") == "active_component"
    }

    candidates: list[dict] = []
    seen_signatures: set[tuple[str, ...]] = set()

    for start in sorted(input_nodes):
        add_functional_path(
            candidates,
            seen_signatures,
            "external_interface_to_device_path",
            shortest_path_to_targets(adjacency, start, active_nodes - {start}),
            component_index,
            net_roles_by_id,
            0.72,
            "heuristic_inference",
        )

    for start in sorted(supply_nodes):
        add_functional_path(
            candidates,
            seen_signatures,
            "source_to_interface_path",
            shortest_path_to_targets(adjacency, start, output_nodes - {start}),
            component_index,
            net_roles_by_id,
            0.78,
            "heuristic_inference",
        )

    for end in sorted(output_nodes):
        path = shortest_path_to_targets(adjacency, end, active_nodes - {end})
        if path:
            add_functional_path(
                candidates,
                seen_signatures,
                "device_to_interface_path",
                list(reversed(path)),
                component_index,
                net_roles_by_id,
                0.74,
                "heuristic_inference",
            )

    for start in sorted(ground_nodes):
        add_functional_path(
            candidates,
            seen_signatures,
            "ground_to_device_path",
            shortest_path_to_targets(adjacency, start, active_nodes - {start}),
            component_index,
            net_roles_by_id,
            0.68,
            "heuristic_inference",
        )

    for component_role in bridge_interfaces:
        instance_id = str(component_role.get("instance_id"))
        connected_nets = list(component_role.get("connected_nets", []))
        if len(connected_nets) < 2:
            continue
        ordered_nets = sorted(connected_nets)[:2]
        add_functional_path(
            candidates,
            seen_signatures,
            "interface_bridge_path",
            [("net", ordered_nets[0]), ("component", instance_id), ("net", ordered_nets[1])],
            component_index,
            net_roles_by_id,
            0.84,
            "topological_fact",
        )

    candidates.sort(
        key=lambda item: (
            -int(item.get("priority", 0)),
            -float(item.get("confidence", 0.0)),
            str(item.get("start") or ""),
            str(item.get("end") or ""),
        )
    )

    paths: list[dict] = []
    for index, item in enumerate(candidates[:MAX_FUNCTIONAL_PATHS], start=1):
        entry = dict(item)
        entry["path_id"] = f"P{index}"
        entry.pop("priority", None)
        paths.append(entry)
    return paths


def build_structural_patterns(
    data: dict,
    component_roles: list[dict],
    net_roles: list[dict],
    terminal_entries_by_component: dict[str, list[dict]],
    terminal_index: dict[str, dict],
) -> list[dict]:
    """Costruisce structural patterns a partire dagli input correnti della pipeline."""
    terminals = data.get("terminals", [])
    patterns: list[dict] = []

    for term in terminals:
        if term.get("is_suspicious_match", False):
            target = terminal_display_id(term) or term.get("terminal_id")
            patterns.append({
                "pattern_type": "suspicious_terminal_match",
                "target": target,
                "description": (
                    f"{human_component_name(term.get('instance_id'), term.get('component_class_name'))} "
                    f"{terminal_role_text(term)} was flagged as a suspicious terminal-to-net match."
                ),
                "evidence_type": "topological_fact",
            })

    for term in terminals:
        if term.get("matched_net_id") is None:
            target = terminal_display_id(term) or term.get("terminal_id")
            patterns.append({
                "pattern_type": "unmatched_terminal",
                "target": target,
                "description": (
                    f"{human_component_name(term.get('instance_id'), term.get('component_class_name'))} "
                    f"{terminal_role_text(term)} is unmatched."
                ),
                "evidence_type": "topological_fact",
            })

    for net_role in net_roles:
        if net_role.get("role_hypothesis") != "single_terminal_stub":
            continue
        net_id = str(net_role.get("net_id"))
        terminal_id = None
        for term in terminals:
            if str(term.get("matched_net_id")) == net_id:
                terminal_id = term.get("terminal_id")
                break
        terminal = terminal_index.get(str(terminal_id), {})
        patterns.append({
            "pattern_type": "single_terminal_stub",
            "target": net_id,
            "description": (
                f"Net {net_id} currently touches only "
                f"{human_component_name(terminal.get('instance_id'), terminal.get('component_class_name'))} "
                f"{terminal_role_text(terminal)}."
            ),
            "evidence_type": "topological_fact",
        })

    for component_role in component_roles:
        class_name = component_role.get("class_name")
        instance_id = str(component_role.get("instance_id"))
        if is_ground_component(class_name):
            continue

        entries = terminal_entries_by_component.get(instance_id, [])
        net_to_entries: dict[str, list[dict]] = defaultdict(list)
        for entry in entries:
            net_id = entry.get("net_id")
            if net_id is not None:
                net_to_entries[str(net_id)].append(entry)

        for net_id, same_net_entries in sorted(net_to_entries.items()):
            if len(same_net_entries) < 2:
                continue

            issue_type = (
                "collapsed_passive_component"
                if normalize_token(class_name) == "resistor"
                else "multiple_terminals_same_net"
            )
            terminal_names = [
                terminal_human_name({"display_name": entry.get("display_terminal_id"), "name": entry.get("terminal_name")})
                or entry.get("display_terminal_id")
                for entry in same_net_entries
            ]
            patterns.append({
                "pattern_type": issue_type,
                "target": instance_id,
                "description": (
                    f"{human_component_name(instance_id, class_name)} has terminals {join_or_none(terminal_names)} "
                    f"on the same net {net_id}."
                ),
                "net_id": net_id,
                "evidence_type": "topological_fact",
            })

    for net_role in net_roles:
        net_id = str(net_role.get("net_id"))
        connected_components = net_role.get("connected_components", [])
        n_components = len(connected_components)
        if str(net_role.get("role_hypothesis")) == "shared_internal_branch" and n_components >= 5:
            patterns.append({
                "pattern_type": "high_degree_shared_branch",
                "target": net_id,
                "description": f"Net {net_id} is a shared internal branch touching {n_components} modeled components.",
                "n_connected_components": n_components,
                "evidence_type": "topological_fact",
            })

    deduped: list[dict] = []
    seen = set()
    for pattern in patterns:
        key = (
            str(pattern.get("pattern_type")),
            str(pattern.get("target")),
            str(pattern.get("description")),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(pattern)

    deduped.sort(
        key=lambda item: (
            str(item.get("pattern_type") or ""),
            str(item.get("target") or ""),
        )
    )
    return deduped


def build_component_descriptions(component_roles: list[dict]) -> list[dict]:
    """Costruisce component descriptions a partire dagli input correnti della pipeline."""
    return [
        {
            "instance_id": role.get("instance_id"),
            "class_name": role.get("class_name"),
            "description_label": role.get("description_label"),
            "description_specificity": role.get("description_specificity"),
            "description_basis": role.get("description_basis", []),
            "confidence": role.get("confidence"),
            "evidence_type": role.get("evidence_type"),
            "interface_kind": role.get("interface_kind"),
            "connected_nets": role.get("connected_nets", []),
            "connected_components": role.get("connected_components", []),
            "natural_language": role.get("natural_language"),
        }
        for role in component_roles
    ]


def build_net_descriptions(net_roles: list[dict]) -> list[dict]:
    """Costruisce net descriptions a partire dagli input correnti della pipeline."""
    return [
        {
            "net_id": role.get("net_id"),
            "alias": role.get("alias"),
            "description_label": role.get("description_label"),
            "description_specificity": role.get("description_specificity"),
            "description_basis": role.get("description_basis", []),
            "confidence": role.get("confidence"),
            "evidence_type": role.get("evidence_type"),
            "connected_components": role.get("connected_components", []),
            "natural_language": role.get("natural_language"),
        }
        for role in net_roles
    ]


def build_functional_path_descriptions(functional_paths: list[dict]) -> list[dict]:
    """Costruisce functional path descriptions a partire dagli input correnti della pipeline."""
    return [
        {
            "path_id": path.get("path_id"),
            "path_type": path.get("path_type"),
            "start": path.get("start"),
            "end": path.get("end"),
            "sequence": path.get("sequence", []),
            "confidence": path.get("confidence"),
            "evidence_type": path.get("evidence_type"),
            "natural_language": path.get("natural_language"),
        }
        for path in functional_paths
    ]


def build_terminal_fact_descriptions(terminal_facts: list[dict]) -> list[dict]:
    """Costruisce terminal fact descriptions a partire dagli input correnti della pipeline."""
    return [
        {
            "terminal_id": fact.get("terminal_id"),
            "display_terminal_id": fact.get("display_terminal_id"),
            "instance_id": fact.get("instance_id"),
            "component_class_name": fact.get("component_class_name"),
            "terminal_name": fact.get("terminal_name"),
            "semantic_terminal_name": fact.get("semantic_terminal_name"),
            "semantic_slot": fact.get("semantic_slot"),
            "semantic_confidence": fact.get("semantic_confidence"),
            "semantic_evidence_type": fact.get("semantic_evidence_type"),
            "semantic_resolution_mode": fact.get("semantic_resolution_mode"),
            "semantic_role_family": fact.get("semantic_role_family"),
            "semantic_polarity": fact.get("semantic_polarity"),
            "semantic_direction": fact.get("semantic_direction"),
            "net_id": fact.get("net_id"),
            "match_status": fact.get("match_status"),
            "description": fact.get("statement"),
        }
        for fact in terminal_facts
    ]


def build_semantic_explanation(
    data: dict,
    pipeline_variant: str,
    source_stage: str,
) -> dict:
    """Costruisce semantic explanation a partire dagli input correnti della pipeline."""
    components = data.get("components", [])
    terminals = data.get("terminals", [])
    nets = data.get("nets", [])
    connections = data.get("connections", [])

    component_index, terminal_index, _, net_to_terminal_ids = build_terminal_and_net_indexes(data)
    terminal_entries_by_component, terminal_facts = build_terminal_semantic_entries(
        terminals,
        terminal_index,
        net_to_terminal_ids,
    )

    component_roles: list[dict] = []
    for component in sorted(components, key=lambda item: str(item.get("instance_id") or "")):
        instance_id = str(component.get("instance_id") or "")
        terminal_entries = terminal_entries_by_component.get(instance_id, [])
        connected_components = build_component_connected_components(terminal_entries, instance_id)
        component_roles.append(infer_component_role(component, terminal_entries, connected_components))

    net_roles: list[dict] = []
    for net in sorted(nets, key=lambda item: int(item.get("net_index") or 0)):
        net_id = str(net.get("net_id"))
        connected_terminals = [
            terminal_index[terminal_id]
            for terminal_id in net_to_terminal_ids.get(net_id, [])
            if terminal_id in terminal_index
        ]
        connected_components_map: dict[str, dict] = {}
        for term in connected_terminals:
            instance_id = str(term.get("instance_id") or "")
            if not instance_id:
                continue
            connected_components_map.setdefault(
                instance_id,
                {
                    "instance_id": instance_id,
                    "component_class_name": term.get("component_class_name"),
                },
            )
        connected_components = sorted(
            connected_components_map.values(),
            key=lambda item: str(item.get("instance_id") or ""),
        )
        net_roles.append(infer_net_role(net, connected_terminals, connected_components))

    net_roles_by_id = {str(item.get("net_id")): item for item in net_roles}
    branch_summaries = build_branch_summaries(net_roles)
    component_relation_groups = build_component_relation_groups(
        nets,
        net_roles_by_id,
        terminal_index,
        net_to_terminal_ids,
    )
    component_to_component_relations = build_component_to_component_relations(
        nets,
        net_roles_by_id,
        terminal_index,
        net_to_terminal_ids,
    )
    functional_paths = build_functional_paths(
        component_roles,
        net_roles,
        component_index,
        terminals,
    )
    structural_patterns = build_structural_patterns(
        data,
        component_roles,
        net_roles,
        terminal_entries_by_component,
        terminal_index,
    )
    component_descriptions = build_component_descriptions(component_roles)
    net_descriptions = build_net_descriptions(net_roles)
    functional_path_descriptions = build_functional_path_descriptions(functional_paths)
    terminal_fact_descriptions = build_terminal_fact_descriptions(terminal_facts)

    main_inputs = [
        {
            "instance_id": role.get("instance_id"),
            "class_name": role.get("class_name"),
            "reason": join_or_none(role.get("description_basis", [])),
            "confidence": role.get("confidence"),
        }
        for role in component_roles
        if role.get("interface_kind") == "input_interface"
    ]
    main_outputs = [
        {
            "instance_id": role.get("instance_id"),
            "class_name": role.get("class_name"),
            "reason": join_or_none(role.get("description_basis", [])),
            "confidence": role.get("confidence"),
        }
        for role in component_roles
        if role.get("interface_kind") in {"possible_output_interface", "bridge_interface"}
    ]
    supplies = [
        {
            "instance_id": role.get("instance_id"),
            "class_name": role.get("class_name"),
            "connected_nets": role.get("connected_nets", []),
        }
        for role in component_roles
        if role.get("role_hypothesis") == "power_source"
    ]
    grounds = [
        {
            "instance_id": role.get("instance_id"),
            "class_name": role.get("class_name"),
            "connected_nets": role.get("connected_nets", []),
        }
        for role in component_roles
        if role.get("role_hypothesis") == "ground_reference"
    ]

    notes = [
        (
            f"{len(components)} components, {len(terminals)} terminals, {len(nets)} nets, and "
            f"{len(connections)} terminal-to-net connections were summarized deterministically from the extracted topology."
        ),
    ]
    if structural_patterns:
        notes.append(
            f"{len(structural_patterns)} structural pattern(s) were recorded as direct descriptive observations."
        )

    return {
        "diagram_metadata": {
            "diagram_id": data.get("image_id"),
            "image_name": data.get("image_name"),
            "pipeline_variant": pipeline_variant,
            "source_json_stage": source_stage,
        },
        "summary": {
            "n_components": len(components),
            "n_terminals": len(terminals),
            "n_nets": len(nets),
            "n_connections": len(connections),
            "main_inputs": main_inputs,
            "main_outputs": main_outputs,
            "supplies": supplies,
            "grounds": grounds,
            "notes": notes,
        },
        "component_descriptions": component_descriptions,
        "net_descriptions": net_descriptions,
        "branch_summaries": branch_summaries,
        "component_to_component_relations": component_to_component_relations,
        "component_relation_groups": component_relation_groups,
        "functional_paths": functional_path_descriptions,
        "structural_patterns": structural_patterns,
        "terminal_facts": terminal_fact_descriptions,
    }


def build_semantic_llm_context(semantic_data: dict) -> str:
    """Costruisce semantic llm context a partire dagli input correnti della pipeline."""
    metadata = semantic_data.get("diagram_metadata", {})
    summary = semantic_data.get("summary", {})
    branch_summaries = semantic_data.get("branch_summaries", [])
    functional_paths = semantic_data.get("functional_paths", [])
    component_descriptions = semantic_data.get("component_descriptions", [])
    net_descriptions = semantic_data.get("net_descriptions", [])
    component_relation_groups = semantic_data.get("component_relation_groups", [])
    structural_patterns = semantic_data.get("structural_patterns", [])
    terminal_facts = semantic_data.get("terminal_facts", [])

    lines: list[str] = []
    lines.append("# Purpose")
    lines.append(
        "This document summarizes the extracted circuit topology in a descriptive form. "
        "Facts come directly from the graph when possible, while descriptive labels remain cautious heuristic summaries of the observed topology."
    )

    lines.append("")
    lines.append("# Overview")
    lines.append(
        f"Diagram `{metadata.get('diagram_id')}` (`{metadata.get('image_name')}`) from pipeline variant "
        f"`{metadata.get('pipeline_variant')}` was exported from `{metadata.get('source_json_stage')}`."
    )
    lines.append(
        f"The topology contains {summary.get('n_components', 0)} components, {summary.get('n_terminals', 0)} terminals, "
        f"{summary.get('n_nets', 0)} nets, and {summary.get('n_connections', 0)} terminal-to-net connections."
    )
    if summary.get("supplies"):
        supply_text = join_or_none(
            [human_component_name(item.get("instance_id"), item.get("class_name")) for item in summary.get("supplies", [])]
        )
        lines.append(f"Explicit power sources: {supply_text}.")
    if summary.get("grounds"):
        ground_text = join_or_none(
            [human_component_name(item.get("instance_id"), item.get("class_name")) for item in summary.get("grounds", [])]
        )
        lines.append(f"Explicit ground references: {ground_text}.")
    if summary.get("main_inputs"):
        input_text = join_or_none(
            [human_component_name(item.get("instance_id"), item.get("class_name")) for item in summary.get("main_inputs", [])]
        )
        lines.append(f"Possible external inputs: {input_text}.")
    if summary.get("main_outputs"):
        output_text = join_or_none(
            [human_component_name(item.get("instance_id"), item.get("class_name")) for item in summary.get("main_outputs", [])]
        )
        lines.append(f"Possible external outputs or bridge interfaces: {output_text}.")

    lines.append("")
    lines.append("# Main Branches")
    if branch_summaries:
        for branch in branch_summaries[:MAX_MARKDOWN_BRANCHES]:
            lines.append(
                f"- `{branch.get('anchor_net')}` ({branch.get('branch_kind')}, importance={branch.get('importance')}): "
                f"{branch.get('natural_language')}"
            )
    else:
        lines.append("- No branch summary was produced from the current topology.")

    lines.append("")
    lines.append("# Component Descriptions")
    if component_descriptions:
        for description in component_descriptions:
            lines.append(
                f"- `{description.get('instance_id')}` ({description.get('class_name')}): "
                f"{str(description.get('description_label') or '').replace('_', ' ')} "
                f"[specificity={description.get('description_specificity')}, confidence={description.get('confidence'):.2f}] "
                f"{description.get('natural_language')}"
            )
    else:
        lines.append("- No component description data available.")

    lines.append("")
    lines.append("# Net Descriptions")
    if net_descriptions:
        for description in net_descriptions:
            lines.append(
                f"- `{description.get('net_id')}`: {str(description.get('description_label') or '').replace('_', ' ')} "
                f"[specificity={description.get('description_specificity')}, confidence={description.get('confidence'):.2f}] "
                f"Basis: {join_or_none(description.get('description_basis', []))}"
            )
    else:
        lines.append("- No net description data available.")

    lines.append("")
    lines.append("# Aggregated Relations")
    if component_relation_groups:
        for group in component_relation_groups[:8]:
            lines.append(f"- `{group.get('net_id')}`: {group.get('summary')}")
    else:
        lines.append("- No aggregated branch relations available.")

    lines.append("")
    lines.append("# Functional Paths")
    if functional_paths:
        for path in functional_paths:
            lines.append(
                f"- `{path.get('path_id')}` `{path.get('path_type')}`: {path.get('natural_language')} "
                f"Confidence: {path.get('confidence'):.2f} ({path.get('evidence_type')})."
            )
    else:
        lines.append("- No functional path summary was produced from the current topology.")

    lines.append("")
    lines.append("# Structural Patterns")
    if structural_patterns:
        for pattern in structural_patterns[:MAX_MARKDOWN_PATTERNS]:
            lines.append(
                f"- `{pattern.get('pattern_type')}` on `{pattern.get('target')}`: {pattern.get('description')}"
            )
    else:
        lines.append("- No structural pattern was recorded from the current topology.")

    lines.append("")
    lines.append("# Terminal Facts")
    if terminal_facts:
        for fact in terminal_facts[:MAX_MARKDOWN_TERMINAL_FACTS]:
            lines.append(
                f"- `{fact.get('display_terminal_id') or fact.get('terminal_id')}`: {fact.get('description')}"
            )
    else:
        lines.append("- No terminal fact summary available.")

    lines.append("")
    lines.append("# Companion Files")
    lines.append("- `*_graph.json` remains the technical source of truth.")
    lines.append("- `*_semantic_explanation.json` contains the deterministic semantic summary used to build this markdown.")
    return "\n".join(lines).strip() + "\n"
