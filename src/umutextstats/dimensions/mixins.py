# src/umutextstats/dimensions/mixins.py

from typing import Any

import pandas as pd


class TextComputeMixin:
    """
    Mixin for dimensions that compute their value from a single text-like
    input column.

    Classes using this mixin must provide `_compute_text(text)`.
    The actual input column is resolved by `get_text()` and
    `get_text_series()`, which come from BaseDimension.
    """

    def compute_single(
        self,
        row: pd.Series,
    ) -> Any:
        """
        Compute the dimension for a single row.
        """
        return self._compute_text(
            self.get_text(row)
        )

    def compute(
        self,
        df: pd.DataFrame,
    ) -> pd.Series:
        """
        Compute the dimension for all rows.
        """
        return self.get_text_series(df).apply(
            self._compute_text
        )