from __future__ import annotations

import pandas as pd

from umutextstats.config.params import param
from umutextstats.dimensions.base import BaseDimension


class CompositeDimension(BaseDimension):
    def __init__(
        self,
        key: str,
        children: list[str],
        strategy: str = "CompositeStrategyNone",
        input_column: str = "text_norm",
    ):
        super().__init__(key=key, input_column=input_column)
        self.children = children
        self.strategy = strategy or "CompositeStrategyNone"

    @classmethod
    def from_config(
        cls,
        dimension,
        input_column: str = "text_norm",
    ):
        return cls(
            key=dimension.key,
            children=[child.key for child in dimension.children],
            strategy=dimension.strategy or "CompositeStrategyNone",
            input_column=input_column,
        )

    def compute(self, df):
        return self.compute_from_data(
            data={column: df[column] for column in df.columns},
            n_rows=len(df),
        )

    def compute_from_data(
        self,
        data: dict[str, pd.Series],
        n_rows: int,
    ):
        child_keys = [
            key
            for key in self.children
            if key in data
        ]

        if not child_keys:
            return pd.Series([0.0] * n_rows)

        child_df = pd.DataFrame(
            {
                key: data[key]
                for key in child_keys
            }
        )

        child_df = (
            child_df
            .apply(pd.to_numeric, errors="coerce")
            .fillna(0)
        )

        strategy = self.strategy.upper()

        if strategy == "COMPOSITESTRATEGYNONE":
            return pd.Series([None] * n_rows)

        if strategy == "COMPOSITESTRATEGYSUM":
            return child_df.sum(axis=1)

        if strategy == "COMPOSITESTRATEGYAVG":
            return child_df.mean(axis=1)

        if strategy == "COMPOSITESTRATEGYMAX":
            return child_df.max(axis=1)

        if strategy == "COMPOSITESTRATEGYMIN":
            return child_df.min(axis=1)

        return child_df.sum(axis=1)