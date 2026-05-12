from .ids import (
    get_preferred_terminal_public_name,
    make_simple_component_id,
    make_simple_terminal_key,
)


def build_integrated_circuit_display_name(comp: dict):
    if comp.get("ic_marking") not in (None, ""):
        return str(comp.get("ic_marking"))
    if comp.get("component_subtype") not in (None, ""):
        return str(comp.get("component_subtype"))
    return None


def build_integrated_circuit_terminal_display_name(comp: dict, term: dict):
    parts = []
    component_display_name = build_integrated_circuit_display_name(comp)
    terminal_name = get_preferred_terminal_public_name(term)

    if component_display_name:
        parts.append(component_display_name)
    parts.append(str(terminal_name))

    if term.get("pin_number") not in (None, ""):
        parts.append(f"pin{term.get('pin_number')}")
    if term.get("pin_label_text") not in (None, ""):
        parts.append(str(term.get("pin_label_text")))

    return " ".join(parts)


# =========================================================
# COSTRUZIONE DEI COMPONENTI CANONICI
# =========================================================
# Produce una vista semplificata dei componenti.
# Nel JSON finale teniamo solo:
# - component_id
# - instance_id
# - class_name
# - terminals con terminal_id, name e relative_position
# Per Integrated_Circuit preserva anche le informazioni OCR gia' lette nel passo 03:
# - ic_marking o component_subtype
# - pin_number e/o pin_label
# state e state_confidence per componenti come lo switch
def build_canonical_components(components: list[dict]):
    canonical_components = []

    for comp in components:
        class_name = comp.get("class_name")
        instance_id = comp.get("instance_id")
        is_integrated_circuit = class_name == "Integrated_Circuit"

        canonical_terminals = []
        for term in comp.get("terminals", []):
            canonical_terminal = {
                "terminal_id": make_simple_terminal_key(term),
                "name": get_preferred_terminal_public_name(term),
                "relative_position": term.get("relative_position"),
            }

            if is_integrated_circuit:
                canonical_terminal["display_name"] = build_integrated_circuit_terminal_display_name(comp, term)
                if term.get("pin_number") not in (None, ""):
                    canonical_terminal["pin_number"] = term.get("pin_number")
                if term.get("pin_label_text") not in (None, ""):
                    canonical_terminal["pin_label"] = term.get("pin_label_text")

            canonical_terminals.append(canonical_terminal)

        canonical_component = {
            "component_id": make_simple_component_id(instance_id, class_name),
            "instance_id": instance_id,
            "class_name": class_name,
            "terminals": canonical_terminals,
        }

        if is_integrated_circuit:
            display_name = build_integrated_circuit_display_name(comp)
            if display_name is not None:
                canonical_component["display_name"] = display_name
            if comp.get("ic_marking") not in (None, ""):
                canonical_component["ic_marking"] = comp.get("ic_marking")
            if comp.get("component_subtype") not in (None, ""):
                canonical_component["component_subtype"] = comp.get("component_subtype")

        if comp.get("state") is not None:
            canonical_component["state"] = comp.get("state")
            canonical_component["state_confidence"] = comp.get("state_confidence")

        canonical_components.append(canonical_component)

    return canonical_components
