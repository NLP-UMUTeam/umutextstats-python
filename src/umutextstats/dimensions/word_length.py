from umutextstats.dimensions.base import BaseDimension
from umutextstats.text.tokenization import get_lexical_tokens


class WordLengthDimension(BaseDimension):
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