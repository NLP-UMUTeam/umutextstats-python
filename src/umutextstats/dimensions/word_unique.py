import pandas as pd

from umutextstats.config.params import percentage_param
from umutextstats.inspection.scalar_inspectable_dimension import (
    ScalarInspectableDimension,
)
from umutextstats.text.tokenization import get_lexical_tokens


class WordUniqueDimension(ScalarInspectableDimension):
    """
    Count unique lexical words or compute their percentage over total words.
    """

    def __init__(
        self,
        key: str,
        input_column: str = "text_norm",
        percentage: bool = True,
    ):
        super().__init__(key=key, input_column=input_column)
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
        return cls(
            key=dimension.key,
            input_column=input_column,
            percentage=percentage_param(dimension),
        )

    def compute_single(
        self,
        row: pd.Series,
    ):
        """
        Compute unique word count or percentage for a single row.
        """
        return self._compute_text(
            self.get_text(row)
        )

    def compute(
        self,
        df: pd.DataFrame,
    ) -> pd.Series:
        """
        Compute unique word count or percentage for all rows.
        """
        return self.get_text_series(df).apply(
            self._compute_text
        )

    def _compute_text(
        self,
        text: str,
    ):
        """
        Compute unique lexical words from plain text.
        """
        words = get_lexical_tokens(text)
        total_words = len(words)

        if total_words == 0:
            return 0.0

        unique_words = len(set(words))

        if not self.percentage:
            return unique_words

        return (100 * unique_words) / total_words

    def inspection_debug_text(self) -> str:
        """
        Return configuration details used during inspection.
        """
        return f"Percentage: {self.percentage}"