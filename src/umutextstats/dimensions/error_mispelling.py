from umutextstats.dimensions.base import BaseDimension
from umutextstats.text.tokenization import get_lexical_tokens
from umutextstats.utils.spellchecker_cache import get_cached_spellchecker


class ErrorMispellingDimension(BaseDimension):
    def __init__(
        self,
        key: str,
        input_column: str = "text_norm",
        language: str = "es",
        missing_value: float | str = "",
    ):
        super().__init__(key=key, input_column=input_column)
        self.missing_value = missing_value

        try:
            from spellchecker import SpellChecker
        except ImportError:
            self.spellchecker = None
            return

        self.spellchecker = get_cached_spellchecker(language)

    def compute(self, df):
        if not self.spellchecker.available():
            return [self.missing_value] * len(df)

        return (
            df[self.input_column]
            .fillna("")
            .astype(str)
            .apply(self._compute_text)
        )

    def _compute_text(self, text: str) -> float:
        words = get_lexical_tokens (text)

        if not words:
            return 0.0

        errors = sum(
            1
            for word in words
            if not self.spellchecker.is_known(word)
        )

        return (100 * errors) / len(words)