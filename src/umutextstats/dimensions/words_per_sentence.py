from umutextstats.dimensions.base import BaseDimension
from umutextstats.text.sentence import count_sentences
from umutextstats.text.tokenization import get_lexical_tokens


class WordPerSentenceDimension(BaseDimension):
    def compute(self, df):
        return (
            df[self.input_column]
            .fillna("")
            .astype(str)
            .apply(self._compute_text)
        )

    def _compute_text(self, text: str) -> float:
        total_words = len(get_lexical_tokens(text))

        if total_words == 0:
            return 0.0

        total_sentences = count_sentences(text)

        if total_sentences == 0:
            return 0.0

        return total_words / total_sentences