import pandas as pd
import regex as re

from umutextstats.config.params import param, percentage_param
from umutextstats.inspection.iterable_inspectable_dimension import (
    IterableInspectableDimension,
)


class PatternDimension(IterableInspectableDimension):
    """
    Count regex matches in the configured input column.

    If `percentage` is enabled, the result is normalized by text length.
    """

    def __init__(
        self,
        key: str,
        pattern: str,
        input_column: str = "text_norm",
        percentage: bool = False,
    ):
        super().__init__(key=key, input_column=input_column)
        self.pattern = pattern
        self.percentage = percentage

        # Compile once at initialization time for better runtime performance.
        try:
            self.regex = re.compile(pattern, re.IGNORECASE)
        except re.error as exc:
            raise ValueError(
                f"Invalid regex in PatternDimension '{key}': {pattern!r}. "
                f"Regex error: {exc}"
            ) from exc

    @classmethod
    def from_config(
        cls,
        dimension,
        input_column: str = "text_norm",
    ):
        """
        Build the dimension from configuration.
        """
        return cls(
            key=dimension.key,
            pattern=param(dimension, "pattern", ""),
            input_column=input_column,
            percentage=percentage_param(dimension),
        )

    def compute_single(
        self,
        row: pd.Series,
    ) -> float | int:
        """
        Compute regex match count or percentage for a single row.
        """
        text = self.get_text(row)
        count = self.count_matches(text)

        if not self.percentage:
            return count

        if not text:
            return 0.0

        return (100 * count) / len(text)

    def compute(
        self,
        df: pd.DataFrame,
    ) -> pd.Series:
        """
        Compute regex match count or percentage for all rows.
        """
        texts = self.get_text_series(df)
        counts = texts.apply(self.count_matches)

        if not self.percentage:
            return counts

        total = texts.str.len()

        result = (
            100 * counts / total.replace(0, 1)
        ).astype(float)

        result[total == 0] = 0.0

        return result

    def iter_matches(
        self,
        text: str,
    ):
        """
        Yield regex matches for inspection.
        """
        text = "" if text is None else str(text)

        yield from self.regex.finditer(text)

    def count_matches(
        self,
        text: str,
    ) -> int:
        """
        Count regex matches in a text.
        """
        return sum(
            1
            for _ in self.iter_matches(text)
        )