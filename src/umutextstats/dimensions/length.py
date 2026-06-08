from umutextstats.dimensions.dimension_input import DimensionInput
from umutextstats.inspection.scalar_inspectable_dimension import (
    ScalarInspectableDimension,
)
from umutextstats.text.tokenization import get_lexical_tokens


class LengthDimension(ScalarInspectableDimension):
    def compute_single(
        self,
        item: DimensionInput,
    ) -> int:
        return len(self.get_text(item))

    def compute(self, df):
        if "text_length" in df.columns:
            return df["text_length"]

        return (
            df[self.input_column]
            .fillna("")
            .astype(str)
            .str.len()
        )


class AverageWordLengthDimension(ScalarInspectableDimension):
    def compute_single(
        self,
        item: DimensionInput,
    ) -> float:
        return self._compute_text(self.get_text(item))

    def compute(self, df):
        return (
            df[self.input_column]
            .fillna("")
            .astype(str)
            .apply(self._compute_text)
        )

    def _compute_text(self, text: str) -> float:
        words = get_lexical_tokens(text)

        if not words:
            return 0.0

        return sum(len(word) for word in words) / len(words)
    


class WordLengthDimension(ScalarInspectableDimension):
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

    def compute(self, df):
        return (
            df[self.input_column]
            .fillna("")
            .astype(str)
            .apply(self._compute_text)
        )

    def _compare(self, value: int) -> bool:
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

        # fallback
        return value == self.length

    def _compute_text(self, text: str) -> float:
        words = get_lexical_tokens (text)
        total_words = len(words)

        if total_words == 0:
            return 0.0

        fit_words = sum(
            1 for word in words
            if self._compare(len(word))
        )

        if not self.percentage:
            return fit_words

        return (100 * fit_words) / total_words