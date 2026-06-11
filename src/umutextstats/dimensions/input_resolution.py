# src/umutextstats/dimensions/input_resolution.py

from typing import Any


def get_explicit_input_column(dimension):
    input_column = getattr(dimension, "input_column", None)

    if input_column:
        return input_column

    if hasattr(dimension, "params"):
        return dimension.params.get("input_column")

    return None