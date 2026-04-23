from .ids import (
    get_preferred_terminal_public_name,
    make_simple_component_id,
    make_simple_terminal_key,
)


# =========================================================
# COSTRUZIONE DEI COMPONENTI CANONICI
# =========================================================
# Produce una vista semplificata dei componenti.
# Nel JSON finale teniamo solo:
# - component_id
# - instance_id
# - class_name
# - terminals con terminal_id, name e relative_position
# state e state_confidence per componenti come lo switch
def build_canonical_components(components: list[dict]):
    canonical_components = []

    for comp in components:
        class_name = comp.get("class_name")
        instance_id = comp.get("instance_id")

        canonical_terminals = []
        for term in comp.get("terminals", []):
            canonical_terminals.append({
                "terminal_id": make_simple_terminal_key(term),
                "name": get_preferred_terminal_public_name(term),
                "relative_position": term.get("relative_position"),
            })

        canonical_component = {
            "component_id": make_simple_component_id(instance_id, class_name),
            "instance_id": instance_id,
            "class_name": class_name,
            "terminals": canonical_terminals,
        }

        if comp.get("state") is not None:
            canonical_component["state"] = comp.get("state")
            canonical_component["state_confidence"] = comp.get("state_confidence")

        canonical_components.append(canonical_component)

    return canonical_components
