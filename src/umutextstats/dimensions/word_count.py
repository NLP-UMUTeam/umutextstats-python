import regex as re

from umutextstats.dimensions.base import BaseDimension
from umutextstats.text.patterns import LEXICAL_TOKEN_REGEX


class WordCountDimension(BaseDimension):
    def compute(self, df):
        if "word_count" in df.columns:
            return df["word_count"]

        return (
            df[self.input_column]
            .fillna("")
            .astype(str)
            .apply(lambda text: len(LEXICAL_TOKEN_REGEX.findall(text)))
        )