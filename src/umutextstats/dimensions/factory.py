from __future__ import annotations

from umutextstats.config.models import DimensionConfig
from umutextstats.dimensions.input_resolution import (
    get_explicit_input_column,
)
from umutextstats.dimensions.registry import resolve_dimension


def build_runtime_dimension(
    dimension: DimensionConfig,
    default_input_column: str = "text_norm",
):
    if not dimension.class_name:
        return None

    dimension_cls = resolve_dimension(dimension.class_name)

    if dimension_cls is None:
        return None

    return build_dimension_instance(
        dimension=dimension,
        dimension_cls=dimension_cls,
        default_input_column=default_input_column,
    )


def build_dimension_instance(
    dimension: DimensionConfig,
    dimension_cls,
    default_input_column: str = "text_norm",
):
    input_column = (
        get_explicit_input_column(dimension)
        or default_input_column
    )

    if hasattr(dimension_cls, "from_config"):
        if get_explicit_input_column(dimension):
            return dimension_cls.from_config(
                dimension=dimension,
                input_column=input_column,
            )

        return dimension_cls.from_config(
            dimension=dimension,
        )

    return dimension_cls(
        key=dimension.key,
        input_column=input_column,
    )