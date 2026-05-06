from umutextstats.dimensions.base import BaseDimension
from umutextstats.text.tokenization import get_lexical_tokens


class WordUniqueDimension(BaseDimension):
    def __init__(
        self,
        key: str,
        input_column: str = "text_norm",
        percentage: bool = True,
    ):
        super().__init__(key=key, input_column=input_column)
        self.percentage = percentage

    def compute(self, df):
        return (
            df[self.input_column]
            .fillna("")
            .astype(str)
            .apply(self._compute_text)
        )

    def _compute_text(self, text: str):
        words = get_lexical_tokens(text)
        total_words = len(words)

        if total_words == 0:
            return 0.0

        unique_words = len(set(words))

        if not self.percentage:
            return unique_words

        return (100 * unique_words) / total_words