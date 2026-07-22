"""Controlli condivisi sulle azioni degli scenari Pipeline 2.0."""

from __future__ import annotations

from typing import Any


SINGLE_TARGET_ASSIGNMENT_ACTIONS = frozenset(
    {
        "change_source_value",
        "change_component_value",
        "drive_node_voltage",
        "set_initial_node_voltage",
    }
)


def repeated_target_assignments(actions: Any) -> list[dict[str, Any]]:
    """Trova assegnazioni ripetute che nella stessa run si sovrascriverebbero."""
    if not isinstance(actions, list):
        return []

    seen: dict[tuple[str, str], tuple[int, str]] = {}
    conflicts: list[dict[str, Any]] = []
    for index, action in enumerate(actions, start=1):
        if not isinstance(action, dict):
            continue
        action_type = str(action.get("type") or "").strip()
        if action_type not in SINGLE_TARGET_ASSIGNMENT_ACTIONS:
            continue
        target = str(action.get("target") or "").strip()
        if not target:
            continue
        key = (action_type, target.casefold())
        previous = seen.get(key)
        if previous is None:
            seen[key] = (index, target)
            continue
        conflicts.append(
            {
                "type": action_type,
                "target": previous[1],
                "first_index": previous[0],
                "second_index": index,
            }
        )
    return conflicts


def repeated_assignment_message(conflict: dict[str, Any]) -> str:
    """Spiega il conflitto indicando come rappresentare punti operativi diversi."""
    return (
        f"azioni {conflict.get('first_index')} e {conflict.get('second_index')}: "
        f"{conflict.get('type')} assegna piu volte il target "
        f"'{conflict.get('target')}'; usa scenari separati per valori statici "
        "diversi oppure una sola sorgente PWL/SIN per una variazione temporale"
    )
