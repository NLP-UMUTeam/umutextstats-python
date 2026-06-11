import pandas as pd

from umutextstats.inspection.scalar_inspectable_dimension import (
    ScalarInspectableDimension,
)
from umutextstats.text.sentence import count_sentences
from umutextstats.text.syllables import count_syllables_text
from umutextstats.text.tokenization import get_lexical_tokens


class PerspicuityDimension(ScalarInspectableDimension):
    """
    Compute the Fernández-Huerta perspicuity score.

    Higher values indicate easier texts, while lower values indicate
    more complex texts.

    Formula:

        206.835
        - 62.3 * (syllables / words)
        - (words / sentences)
    """

    def compute_single(
        self,
        row: pd.Series,
    ) -> float:
        """
        Compute the perspicuity score for a single row.
        """
        return self._compute_text(self.get_text(row))

    def compute(
        self,
        df: pd.DataFrame,
    ) -> pd.Series:
        """
        Compute the perspicuity score for all rows.
        """
        return self.get_text_series(df).apply(
            self._compute_text
        )

    def _compute_text(
        self,
        text: str,
    ) -> float:
        """
        Compute the perspicuity score from raw text.
        """
        word_count = len(get_lexical_tokens(text))
        syllables_count = count_syllables_text(text)
        sentences_count = count_sentences(text)

        if word_count == 0 or sentences_count == 0:
            return 0.0

        return (
            206.835
            - (62.3 * (syllables_count / word_count))
            - (word_count / sentences_count)
        )

    def inspection_debug_text(self) -> str:
        """
        Return the formula used by this dimension.
        """
        return (
            "Formula: 206.835 - "
            "62.3 * (syllables / words) - "
            "(words / sentences)"
        )