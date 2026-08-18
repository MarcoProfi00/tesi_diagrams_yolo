"""Compatibilita' per gli import storici del vocabolario componenti viewer."""

from viewer_core.component_library import (
    COMPONENT_SPECS,
    component_spec,
    normalize_component_type,
)


__all__ = ["COMPONENT_SPECS", "component_spec", "normalize_component_type"]
