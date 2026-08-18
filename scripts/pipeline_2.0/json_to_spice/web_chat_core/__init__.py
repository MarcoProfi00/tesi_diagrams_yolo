"""Servizi interni e riusabili della webchat Pipeline 2.0."""

from .io_utils import (
    escape_block,
    is_safe_path_name,
    read_json_safe,
    read_text_safe,
    unescape_html_entities,
)

__all__ = [
    "escape_block",
    "is_safe_path_name",
    "read_json_safe",
    "read_text_safe",
    "unescape_html_entities",
]
