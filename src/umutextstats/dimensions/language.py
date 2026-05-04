# src/umutextstats/dimensions/language.py

from umutextstats.dimensions.base import BaseDimension
from umutextstats.utils.fasttext_loader import FastTextLoader


class LanguageDimension(BaseDimension):
    def __init__(
        self,
        key: str,
        language: str,
        input_column: str = "text_norm",
        missing_value: float | str = "",
    ):
        super().__init__(key=key, input_column=input_column)
        self.language = language.lower()
        self.missing_value = missing_value
        self.model = FastTextLoader.get_model()

    def compute(self, df):
        if self.model is None:
            return [self.missing_value] * len(df)

        return (
            df[self.input_column]
            .fillna("")
            .astype(str)
            .apply(self._compute_text)
        )

    def _compute_text(self, text: str) -> float:
        if not text.strip():
            return 0.0

        labels, probs = self.model.predict(text, k=2)

        for label, prob in zip(labels, probs):
            code = label.replace("__label__", "")
            if code == self.language:
                return prob

        return 0.0