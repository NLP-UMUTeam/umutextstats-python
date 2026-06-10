from __future__ import annotations

import pandas as pd

from umutextstats.config.params import param, split_param_list
from umutextstats.dimensions.base import BaseDimension
from umutextstats.dimensions.dimension_input import DimensionInput
from umutextstats.inspection.models import DimensionInspection


class RatioDimension(BaseDimension):
    def __init__(
        self,
        key: str,
        numerator: list[str] | str,
        denominator: list[str] | str,
        input_column: str = "text_norm",
        scale: float = 1.0,
        zero_division: float = 0.0,
    ):
        super().__init__(key=key, input_column=input_column)
        self.numerator = self._as_list(numerator)
        self.denominator = self._as_list(denominator)
        self.scale = float(scale)
        self.zero_division = float(zero_division)

    @classmethod
    def from_config(
        cls,
        dimension,
        input_column: str = "text_norm",
    ):
        return cls(
            key=dimension.key,
            numerator=split_param_list(
                param(dimension, "numerator", "")
            ),
            denominator=split_param_list(
                param(dimension, "denominator", "")
            ),
            input_column=input_column,
            scale=float(param(dimension, "scale") or 1.0),
            zero_division=float(
                param(dimension, "zero_division") or 0.0
            ),
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
    ) -> pd.Series:
        numerator = self._sum_data_keys(
            data=data,
            keys=self.numerator,
            n_rows=n_rows,
        )

        denominator = self._sum_data_keys(
            data=data,
            keys=self.denominator,
            n_rows=n_rows,
        )

        missing = [
            key
            for key in self.numerator + self.denominator
            if key not in data
        ]

        if missing:
            raise ValueError(
                f"Missing columns for RatioDimension '{self.key}': "
                f"{', '.join(missing)}"
            )

        result = numerator / denominator.replace(0, pd.NA)

        result = (
            pd.to_numeric(result, errors="coerce")
            .fillna(self.zero_division)
        )

        return result * self.scale

    def compute_single(
        self,
        item: DimensionInput,
    ) -> float:
        numerator = self._sum_item_keys(item, self.numerator)
        denominator = self._sum_item_keys(item, self.denominator)

        return self._safe_ratio(
            numerator=numerator,
            denominator=denominator,
        )

    def inspect(
        self,
        item: DimensionInput,
    ) -> DimensionInspection:
        numerator = self._sum_item_keys(item, self.numerator)
        denominator = self._sum_item_keys(item, self.denominator)

        value = self._safe_ratio(
            numerator=numerator,
            denominator=denominator,
        )

        return DimensionInspection(
            key=self.key,
            class_name=self.__class__.__name__,
            pattern=None,
            dictionary=None,
            matches=[],
            discarded_matches=[],
            debug_text=(
                f"Value: {value}\n"
                f"Numerator keys: {self._format_keys(self.numerator)}\n"
                f"Numerator value: {numerator}\n"
                f"Denominator keys: {self._format_keys(self.denominator)}\n"
                f"Denominator value: {denominator}\n"
                f"Scale: {self.scale}\n"
                f"Zero division: {self.zero_division}"
            ),
        )

    def _safe_ratio(
        self,
        numerator: float,
        denominator: float,
    ) -> float:
        if denominator == 0:
            return self.zero_division

        return (numerator / denominator) * self.scale

    def _sum_data_keys(
        self,
        data: dict[str, pd.Series],
        keys: list[str],
        n_rows: int,
    ) -> pd.Series:
        if not keys:
            return pd.Series([0.0] * n_rows)

        frame = pd.DataFrame(
            {
                key: data.get(
                    key,
                    pd.Series([0.0] * n_rows),
                )
                for key in keys
            }
        )

        return (
            frame
            .apply(pd.to_numeric, errors="coerce")
            .fillna(0)
            .sum(axis=1)
        )

    def _sum_item_keys(
        self,
        item: DimensionInput,
        keys: list[str],
    ) -> float:
        total = 0.0

        for key in keys:
            try:
                total += float(item.get(key, 0) or 0)
            except (TypeError, ValueError):
                continue

        return total

    def _as_list(
        self,
        value: list[str] | str,
    ) -> list[str]:
        if isinstance(value, list):
            return value

        return split_param_list(value)

    def _format_keys(
        self,
        keys: list[str],
    ) -> str:
        return " + ".join(keys) if keys else "0"