# src/umutextstats/dimensions/error_mispelling_accents.py

from umutextstats.dimensions.base import BaseDimension
from umutextstats.dimensions.enclitics_personal_pronouns import remove_accents
from umutextstats.dimensions.word_count import WORD_REGEX


class ErrorMispellingAccentsDimension(BaseDimension):
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

        self.spellchecker = SpellChecker(language=language)

    def compute(self, df):
        if self.spellchecker is None:
            return [self.missing_value] * len(df)

        return (
            df[self.input_column]
            .fillna("")
            .astype(str)
            .apply(self._compute_text)
        )

    def _compute_text(self, text: str) -> float:
        words = WORD_REGEX.findall(text.lower())

        if not words:
            return 0.0

        occurrences = 0

        for word in words:
            if word in self.spellchecker:
                continue

            suggestion = self.spellchecker.correction(word)

            if not suggestion:
                continue

            if remove_accents(word) == remove_accents(suggestion):
                occurrences += 1

        return (100 * occurrences) / len(words)