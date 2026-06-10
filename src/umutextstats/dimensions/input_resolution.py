# src/umutextstats/dimensions/input_resolution.py

from collections.abc import Mapping
from typing import Any

from umutextstats.io.text import ensure_text


def resolve_input_column(
    dimension: Any,
    default_input_column: str = "text_norm",
) -> str:
    if getattr(dimension, "use_original_input", False):
        return "text_raw"

    input_column = getattr(dimension, "input_column", None)
    if input_column:
        return input_column

    if hasattr(dimension, "params"):
        input_column = dimension.params.get("input_column")
        if input_column:
            return input_column

    class_name = getattr(dimension, "class_name", None)

    if class_name == "POSTaggingTag":
        return "tagged_pos"

    if class_name == "NERTaggingTag":
        return "tagged_ner"

    return default_input_column


def dimension_requires_tagged_ner(dimension: Any) -> bool:
    """Return whether a dimension requires tagged_ner for inspection."""
    if dimension.class_name == "NERTaggingTag":
        return True

    if dimension.children:
        return any(
            dimension_requires_tagged_ner(child)
            for child in dimension.children
        )

    return False


def dimension_requires_tagged_pos(dimension: Any) -> bool:
    """Return whether a dimension requires tagged_pos for inspection."""
    if dimension.class_name == "POSTaggingTag":
        return True

    if dimension.class_name in {"WordPerDictionary", "VerbPerDictionary"}:
        return bool(
            getattr(dimension, "pos_tag", None)
            or dimension.params.get("pos_tag")
        )

    if dimension.children:
        return any(
            dimension_requires_tagged_pos(child)
            for child in dimension.children
        )

    return False


def resolve_dimension_input(dimension: Any, row: Mapping[str, Any]) -> str:
    """Resolve the concrete text representation for inspection/validation."""
    
    if dimension_requires_tagged_pos(dimension):
        return ensure_text(row.get("tagged_pos", ""))

    if dimension_requires_tagged_ner(dimension):
        return ensure_text(row.get("tagged_ner", ""))

    input_column = resolve_input_column(dimension)

    if input_column == "text_raw":
        return ensure_text(row.get("text_raw", row.get("text", "")))

    if input_column == "text_norm":
        return ensure_text(row.get("text_norm", row.get("text", "")))

    return ensure_text(row.get(input_column, ""))