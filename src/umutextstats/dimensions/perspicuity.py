import pandas as pd

from umutextstats.dimensions.mixins import TextComputeMixin
from umutextstats.inspection.scalar_inspectable_dimension import (
    ScalarInspectableDimension,
)
from umutextstats.text.sentence import count_sentences
from umutextstats.text.syllables import count_syllables_text
from umutextstats.text.tokenization import get_lexical_tokens


class PerspicuityDimension(TextComputeMixin, ScalarInspectableDimension):
    """
    Compute the Fernández-Huerta perspicuity score.

    Higher values indicate easier texts, while lower values indicate
    more complex texts.

    Formula:

        206.835
        - 62.3 * (syllables / words)
        - (words / sentences)
    """

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