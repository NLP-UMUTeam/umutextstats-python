# src/umutextstats/config/params.py

from __future__ import annotations

from umutextstats.config.models import DimensionConfig


def param(dimension: DimensionConfig, name: str, default=None):
    value = dimension.params.get(name)

    if value is not None:
        return value

    return getattr(dimension, name, default)


def bool_value(value, default: bool = False) -> bool:
    if value is None:
        return default

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "y"}

    return bool(value)


def dictionary_param(dimension: DimensionConfig) -> str:
    return (
        dimension.params.get("dictionary")
        or dimension.params.get("dictionaries")
        or getattr(dimension, "dictionary", None)
        or ""
    )


def percentage_param(dimension: DimensionConfig) -> bool:
    value = dimension.params.get("percentage", None)
    return bool_value(value, default=dimension.percentage)


def disabled_regexp_param(dimension: DimensionConfig) -> bool:
    value = (
        dimension.params.get("disabledregexp")
        if "disabledregexp" in dimension.params
        else dimension.params.get("disabled_regexp", None)
    )

    return bool_value(value, default=dimension.disabled_regexp)


def split_param_list(value: str) -> list[str]:
    return [
        item.strip()
        for item in str(value).split("|")
        if item.strip()
    ]