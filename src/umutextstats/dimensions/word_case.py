import pandas as pd

from umutextstats.config.params import param
from umutextstats.inspection.scalar_inspectable_dimension import (
    ScalarInspectableDimension,
)
from umutextstats.text.patterns import (
    LEADING_MENTION_REGEX,
    URL_REGEX,
    WORD_TOKEN_REGEX,
)


class WordCase(ScalarInspectableDimension):
    """
    Compute the percentage of words matching a casing rule.

    Supported comparators:
    - "upper"
    - "lower"
    - "title"
    """

    def __init__(
        self,
        key: str,
        comparator: str = "upper",
        input_column: str = "text_raw",
    ):
        super().__init__(key=key, input_column=input_column)
        self.comparator = comparator or "upper"

    @classmethod
    def from_config(
        cls,
        dimension,
        input_column: str = "text_raw",
    ):
        """
        Build the dimension from configuration.
        """
        return cls(
            key=dimension.key,
            comparator=(
                param(dimension, "word_comparator")
                or param(dimension, "comparator")
                or "upper"
            ),
            input_column=input_column,
        )

    def compute_single(
        self,
        row: pd.Series,
    ) -> float:
        """
        Compute the casing percentage for a single row.
        """
        return self._compute_text(
            self.get_text(row)
        )

    def compute(
        self,
        df: pd.DataFrame,
    ) -> pd.Series:
        """
        Compute the casing percentage for all rows.
        """
        return self.get_text_series(df).apply(
            self._compute_text
        )

    def _compute_text(
        self,
        text: str,
    ) -> float:
        """
        Compute the percentage of words matching the configured casing rule.
        """
        text = URL_REGEX.sub("", text)
        text = LEADING_MENTION_REGEX.sub("", text).strip()

        words = WORD_TOKEN_REGEX.findall(text)

        if self.comparator == "title":
            words = [
                word
                for index, word in enumerate(words)
                if index == 0 or len(word) > 3
            ]

        total_words = 0
        fit_words = 0

        for word in words:
            if word.isdigit():
                continue

            if word.startswith("@"):
                continue

            total_words += 1

            if self._fits(word):
                fit_words += 1

        if total_words == 0:
            return 0.0

        return (100 * fit_words) / total_words

    def _fits(
        self,
        word: str,
    ) -> bool:
        """
        Check whether a word matches the configured casing rule.
        """
        if self.comparator == "lower":
            return word == word.lower()

        if self.comparator == "title":
            return word == word.title()

        return word == word.upper()

    def inspection_debug_text(self) -> str:
        """
        Return configuration details used during inspection.
        """
        return f"Comparator: {self.comparator}"