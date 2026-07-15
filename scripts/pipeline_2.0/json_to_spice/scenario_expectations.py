"""Criteri condivisi per verificare gli esiti degli scenari controllati."""

from __future__ import annotations

from typing import Final


COMPARISON_TOLERANCE: Final = 1e-12
ALLOWED_EXPECTATIONS: Final = frozenset(
    {
        "activated",
        "deactivated",
        "changed",
        "unchanged",
        "increased",
        "decreased",
        "magnitude_increased",
        "magnitude_decreased",
        "nonzero",
    }
)


def expectation_matches(
    expectation: str,
    base_value: float | None,
    scenario_value: float | None,
    change: str,
) -> bool | None:
    """Verifica un criterio atteso; restituisce None quando manca una misura."""
    if base_value is None or scenario_value is None:
        return None

    normalized = str(expectation or "").strip().lower()
    if normalized == "activated":
        return change == "activated"
    if normalized == "deactivated":
        return change == "deactivated"
    if normalized == "changed":
        return change in {"activated", "deactivated", "changed"}
    if normalized == "unchanged":
        return change == "unchanged"
    if normalized == "increased":
        return scenario_value > base_value + COMPARISON_TOLERANCE
    if normalized == "decreased":
        return scenario_value < base_value - COMPARISON_TOLERANCE
    if normalized == "magnitude_increased":
        return abs(scenario_value) > abs(base_value) + COMPARISON_TOLERANCE
    if normalized == "magnitude_decreased":
        return abs(scenario_value) < abs(base_value) - COMPARISON_TOLERANCE
    if normalized == "nonzero":
        return abs(scenario_value) >= COMPARISON_TOLERANCE
    return False
