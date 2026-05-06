from umutextstats.dimensions.base import BaseDimension
from umutextstats.dimensions.syllable_count import count_syllables_text
from umutextstats.text.tokenization import get_syllabifiable_words


class SyllablePerWordDimension(BaseDimension):
    def compute(self, df):
        return (
            df[self.input_column]
            .fillna("")
            .astype(str)
            .apply(self._compute_text)
        )

    def _compute_text(self, text: str) -> float:
        words = get_syllabifiable_words(text)

        if not words:
            return 0.0

        syllables = count_syllables_text(text)

        return syllables / len(words)