# src/umutextstats/dimensions/average_word_length.py

from umutextstats.dimensions.base import BaseDimension
from umutextstats.dimensions.word_count import WORD_REGEX


class AverageWordLengthDimension(BaseDimension):
    def compute(self, df):
        texts = df[self.input_column].fillna("").astype(str)

        def avg_word_length(text: str) -> float:
            words = WORD_REGEX.findall(text)

            if not words:
                return 0.0

            return sum(len(word) for word in words) / len(words)

        return texts.apply(avg_word_length)