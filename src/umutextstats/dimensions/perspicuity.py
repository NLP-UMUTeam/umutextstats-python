from umutextstats.dimensions.base import BaseDimension
from umutextstats.dimensions.syllable_count import count_syllables_text
from umutextstats.text.sentence import count_sentences
from umutextstats.text.tokenization import get_lexical_tokens


class PerspicuityDimension(BaseDimension):
    def compute(self, df):
        return (
            df[self.input_column]
            .fillna("")
            .astype(str)
            .apply(self._compute_text)
        )

    def _compute_text(self, text: str) -> float:
        word_count = len(get_lexical_tokens(text))
        syllables_count = count_syllables_text(text)
        sentences_count = count_sentences(text)

        if word_count == 0 or sentences_count == 0:
            return 0.0

        return (
            206.835
            - (62.3 * (syllables_count / word_count))
            - (word_count / sentences_count)
        )