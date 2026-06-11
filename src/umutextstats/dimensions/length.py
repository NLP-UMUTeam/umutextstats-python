import pandas as pd

from umutextstats.config.params import param
from umutextstats.inspection.scalar_inspectable_dimension import (
    ScalarInspectableDimension,
)
from umutextstats.text.tokenization import get_lexical_tokens


class LengthDimension(ScalarInspectableDimension):
    """
    Count the number of characters in the configured input column.
    """

    def compute_single(
        self,
        row: pd.Series,
    ) -> int:
        """
        Compute text length for a single row.
        """
        return len(self.get_text(row))

    def compute(
        self,
        df: pd.DataFrame,
    ) -> pd.Series:
        """
        Compute text length for all rows.

        If the DataFrame already contains `text_length`, reuse it.
        """
        if "text_length" in df.columns:
            return df["text_length"]

        return self.get_text_series(df).str.len()


class AverageWordLengthDimension(ScalarInspectableDimension):
    """
    Compute the average length of lexical words in the configured text.
    """

    def compute_single(
        self,
        row: pd.Series,
    ) -> float:
        """
        Compute average word length for a single row.
        """
        return self._compute_text(self.get_text(row))

    def compute(
        self,
        df: pd.DataFrame,
    ) -> pd.Series:
        """
        Compute average word length for all rows.
        """
        return self.get_text_series(df).apply(
            self._compute_text
        )

    def _compute_text(
        self,
        text: str,
    ) -> float:
        """
        Compute average lexical token length.
        """
        words = get_lexical_tokens(text)

        if not words:
            return 0.0

        return sum(len(word) for word in words) / len(words)


class WordLengthDimension(ScalarInspectableDimension):
    """
    Count or compute the percentage of words whose length matches a condition.

    Supported comparators are: >, >=, <, <=, =, ==.
    """

    def __init__(
        self,
        key: str,
        length: int,
        comparator: str = "=",
        input_column: str = "text_norm",
        percentage: bool = True,
    ):
        super().__init__(key=key, input_column=input_column)

        self.length = int(length)
        self.comparator = comparator or "="
        self.percentage = percentage

    @classmethod
    def from_config(
        cls,
        dimension,
        input_column: str = "text_norm",
    ):
        """
        Build the dimension from configuration.
        """
        percentage = str(
            param(dimension, "percentage", True)
        ).lower() not in {
            "0",
            "false",
            "no",
        }

        return cls(
            key=dimension.key,
            length=int(param(dimension, "length", 0)),
            comparator=param(dimension, "comparator", "="),
            input_column=input_column,
            percentage=percentage,
        )

    def compute_single(
        self,
        row: pd.Series,
    ) -> float:
        """
        Compute the word-length score for a single row.
        """
        return self._compute_text(self.get_text(row))

    def compute(
        self,
        df: pd.DataFrame,
    ) -> pd.Series:
        """
        Compute the word-length score for all rows.
        """
        return self.get_text_series(df).apply(
            self._compute_text
        )

    def _compare(
        self,
        value: int,
    ) -> bool:
        """
        Compare a word length against the configured threshold.
        """
        if self.comparator == ">":
            return value > self.length

        if self.comparator == ">=":
            return value >= self.length

        if self.comparator == "<":
            return value < self.length

        if self.comparator == "<=":
            return value <= self.length

        if self.comparator in {"=", "=="}:
            return value == self.length

        return value == self.length

    def _compute_text(
        self,
        text: str,
    ) -> float:
        """
        Count or compute the percentage of words matching the length rule.
        """
        words = get_lexical_tokens(text)
        total_words = len(words)

        if total_words == 0:
            return 0.0

        fit_words = sum(
            1
            for word in words
            if self._compare(len(word))
        )

        if not self.percentage:
            return fit_words

        return (100 * fit_words) / total_words