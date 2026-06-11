import pandas as pd

from umutextstats.config.params import percentage_param
from umutextstats.dimensions.mixins import TextComputeMixin
from umutextstats.inspection.scalar_inspectable_dimension import (
    ScalarInspectableDimension,
)
from umutextstats.text.tokenization import get_lexical_tokens


class WordUniqueDimension(TextComputeMixin, ScalarInspectableDimension):
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
        return cls(
            key=dimension.key,
            input_column=input_column,
            percentage=percentage_param(dimension),
        )

    def _compute_text(
        self,
        text: str,
    ):
        words = get_lexical_tokens(text)
        total_words = len(words)

        if total_words == 0:
            return 0.0

        unique_words = len(set(words))

        if not self.percentage:
            return unique_words

        return (100 * unique_words) / total_words

    def inspection_debug_text(self) -> str:
        return f"Percentage: {self.percentage}"