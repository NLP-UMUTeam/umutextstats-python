from umutextstats.config.params import param
from umutextstats.dimensions.dimension_input import DimensionInput
from umutextstats.inspection.scalar_inspectable_dimension import (
    ScalarInspectableDimension,
)
from umutextstats.utils.fasttext_loader import FastTextLoader


class LanguageDimension(ScalarInspectableDimension):
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

    @classmethod
    def from_config(
        cls,
        dimension,
        input_column: str = "text_norm",
    ):
        return cls(
            key=dimension.key,
            language=param(dimension, "language", ""),
            input_column=input_column,
        )

    def compute_single(
        self,
        item: DimensionInput,
    ) -> float | str:
        if self.model is None:
            return self.missing_value

        return self._compute_text(self.get_text(item))

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
                return float(prob)

        return 0.0

    def inspection_debug_text(self) -> str:
        return f"Target language: {self.language}"