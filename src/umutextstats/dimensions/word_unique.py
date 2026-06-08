from umutextstats.config.params import percentage_param
from umutextstats.dimensions.dimension_input import DimensionInput
from umutextstats.inspection.scalar_inspectable_dimension import (
    ScalarInspectableDimension,
)
from umutextstats.text.tokenization import get_lexical_tokens


class WordUniqueDimension(ScalarInspectableDimension):
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

    def compute_single(
        self,
        item: DimensionInput,
    ):
        return self._compute_text(
            self.get_text(item)
        )

    def compute(self, df):
        return (
            df[self.input_column]
            .fillna("")
            .astype(str)
            .apply(self._compute_text)
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