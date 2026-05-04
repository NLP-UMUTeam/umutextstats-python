from umutextstats.dimensions.base import BaseDimension


class SentenceCountDimension(BaseDimension):
    def compute(self, df):
        if "sentence_count" in df.columns:
            return df["sentence_count"]

        text = df[self.input_column].fillna("").astype(str).str.strip()
        sentence_count = text.str.count(r"[.!?]+")
        return sentence_count.where((text == "") | (sentence_count > 0), 1)