from umutextstats.dimensions.base import BaseDimension
from umutextstats.text.tokenization import get_lexical_tokens


class AverageWordLengthDimension(BaseDimension):
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