from umutextstats.config.params import param
from umutextstats.dimensions.dimension_input import DimensionInput
from umutextstats.inspection.scalar_inspectable_dimension import (
    ScalarInspectableDimension,
)
from umutextstats.text.patterns import (
    URL_REGEX,
    LEADING_MENTION_REGEX,
    WORD_TOKEN_REGEX,
)


class WordCase(ScalarInspectableDimension):
    def __init__(
        self,
        key: str,
        comparator: str = "upper",
        input_column: str = "text_raw",
    ):
        super().__init__(key=key, input_column=input_column)
        self.comparator = comparator or "upper"

    @classmethod
    def from_config(
        cls,
        dimension,
        input_column: str = "text_raw",
    ):
        return cls(
            key=dimension.key,
            comparator=(
                param(dimension, "word_comparator")
                or param(dimension, "comparator")
                or "upper"
            ),
            input_column="text_raw",
        )

    def compute_single(
        self,
        item: DimensionInput,
    ) -> float:
        return self._compute_text(self.get_text(item))

    def compute(self, df):
        return (
            df[self.input_column]
            .fillna("")
            .astype(str)
            .apply(self._compute_text)
        )

    def _compute_text(
        self,
        text: str,
    ) -> float:
        text = URL_REGEX.sub("", text)
        text = LEADING_MENTION_REGEX.sub("", text).strip()

        words = WORD_TOKEN_REGEX.findall(text)

        if self.comparator == "title":
            words = [
                word
                for index, word in enumerate(words)
                if index == 0 or len(word) > 3
            ]

        total_words = 0
        fit_words = 0

        for word in words:
            if word.isdigit():
                continue

            if word.startswith("@"):
                continue

            total_words += 1

            if self._fits(word):
                fit_words += 1

        if total_words == 0:
            return 0.0

        return (100 * fit_words) / total_words

    def _fits(
        self,
        word: str,
    ) -> bool:
        if self.comparator == "lower":
            return word == word.lower()

        if self.comparator == "title":
            return word == word.title()

        return word == word.upper()

    def inspection_debug_text(self) -> str:
        return f"Comparator: {self.comparator}"