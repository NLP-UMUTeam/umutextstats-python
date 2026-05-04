import re

from umutextstats.dimensions.base import BaseDimension


WORD_REGEX = re.compile(r"\b[a-záéíóúüñ]+\b", re.IGNORECASE)


class WordCountDimension(BaseDimension):
    def compute(self, df):
        if "word_count" in df.columns:
            return df["word_count"]

        return (
            df[self.input_column]
            .fillna("")
            .astype(str)
            .apply(lambda text: len(WORD_REGEX.findall(text)))
        )