# src/umutextstats/dimensions/words_per_sentence.py

import regex as re

from umutextstats.dimensions.base import BaseDimension
from umutextstats.dimensions.word_count import WORD_REGEX


SENTENCE_REGEX = re.compile(r"[.!?]+", re.UNICODE)


class WordPerSentenceDimension(BaseDimension):
    def compute(self, df):
        return (
            df[self.input_column]
            .fillna("")
            .astype(str)
            .apply(self._compute_text)
        )

    def _compute_text(self, text: str) -> float:
        words = WORD_REGEX.findall(text)
        total_words = len(words)

        if total_words == 0:
            return 0.0

        sentences = self._count_sentences(text)

        if sentences == 0:
            return 0.0

        return total_words / sentences

    def _count_sentences(self, text: str) -> int:
        text = text.strip()

        if not text:
            return 0

        count = len(SENTENCE_REGEX.findall(text))

        # Igual que en otras dimensiones: mínimo 1 frase
        return count if count > 0 else 1