import pandas as pd

from umutextstats.dimensions.mixins import TextComputeMixin
from umutextstats.inspection.scalar_inspectable_dimension import (
    ScalarInspectableDimension,
)
from umutextstats.text.patterns import SENTENCE_SPAN_REGEX
from umutextstats.text.syllables import count_syllables_text
from umutextstats.text.tokenization import get_lexical_tokens


class ReadabilityDimension(TextComputeMixin, ScalarInspectableDimension):
    """
    Compute the readability score for the configured input text.

    Formula:

        206.84
        - 60 * (syllables / words)
        - 102 * (sentences / words)
    """

    def _compute_text(
        self,
        text: str,
    ) -> float:
        """
        Compute readability from plain text.
        """
        word_count = len(get_lexical_tokens(text))
        syllables_count = count_syllables_text(text)
        sentences_count = self._count_sentences(text)

        if word_count == 0 or sentences_count == 0:
            return 0.0

        return (
            206.84
            - (60 * (syllables_count / word_count))
            - (102 * (sentences_count / word_count))
        )

    def _count_sentences(
        self,
        text: str,
    ) -> int:
        """
        Count sentence spans.

        Empty text returns 0. Non-empty text without sentence spans
        returns 1.
        """
        text = text.strip()

        if not text:
            return 0

        count = len(SENTENCE_SPAN_REGEX.findall(text))

        if count == 0:
            return 1

        return count

    def inspection_debug_text(self) -> str:
        """
        Return the formula used by this dimension.
        """
        return (
            "Formula: "
            "206.84 - "
            "60 * (syllables / words) - "
            "102 * (sentences / words)"
        )