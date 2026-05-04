from umutextstats.dimensions.base import BaseDimension


class LengthDimension(BaseDimension):
    def compute(self, df):
        if "text_length" in df.columns:
            return df["text_length"]

        return df[self.input_column].fillna("").astype(str).str.len()