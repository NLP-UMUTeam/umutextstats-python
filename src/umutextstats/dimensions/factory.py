from __future__ import annotations

from umutextstats.dimensions.input_resolution import resolve_input_column
from umutextstats.dimensions.registry import resolve_dimension
from umutextstats.config.models import DimensionConfig


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
    
    input_column = resolve_input_column(
        dimension,
        default_input_column=default_input_column,
    )

    
    if hasattr(dimension_cls, "from_config"):
        return dimension_cls.from_config(
            dimension=dimension,
            input_column=input_column,
        )


    return dimension_cls(
        key=dimension.key,
        input_column=input_column,
    )