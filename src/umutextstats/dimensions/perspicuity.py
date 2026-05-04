# src/umutextstats/dimensions/perspicuity.py

import regex as re

from umutextstats.dimensions.base import BaseDimension
from umutextstats.dimensions.syllable_count import count_syllables_text
from umutextstats.dimensions.word_count import WORD_REGEX


SENTENCE_REGEX = re.compile(r"[.!?]+", re.UNICODE)


class PerspicuityDimension(BaseDimension):
    def compute(self, df):
        return (
            df[self.input_column]
            .fillna("")
            .astype(str)
            .apply(self._compute_text)
        )

    def _compute_text(self, text: str) -> float:
        word_count = len(WORD_REGEX.findall(text))
        syllables_count = count_syllables_text(text)
        sentences_count = self._count_sentences(text)

        if word_count == 0 or sentences_count == 0:
            return 0.0

        return (
            206.835
            - (62.3 * (syllables_count / word_count))
            - (word_count / sentences_count)
        )

    def _count_sentences(self, text: str) -> int:
        text = text.strip()

        if not text:
            return 0

        count = len(SENTENCE_REGEX.findall(text))

        if count == 0:
            return 1

        return count