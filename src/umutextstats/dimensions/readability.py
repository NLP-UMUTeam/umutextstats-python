from umutextstats.dimensions.dimension_input import DimensionInput
from umutextstats.text.syllables import count_syllables_text
from umutextstats.text.tokenization import get_lexical_tokens
from umutextstats.text.patterns import SENTENCE_SPAN_REGEX
from umutextstats.inspection.scalar_inspectable_dimension import (
    ScalarInspectableDimension,
)


class ReadabilityDimension(ScalarInspectableDimension):
    def compute(self, df):
        return (
            df[self.input_column]
            .fillna("")
            .astype(str)
            .apply(self._compute_text)
        )

    def _compute_text(self, text: str) -> float:
        word_count = len(get_lexical_tokens (text))
        syllables_count = count_syllables_text(text)
        sentences_count = self._count_sentences(text)

        if word_count == 0 or sentences_count == 0:
            return 0.0

        return (
            206.84
            - (60 * (syllables_count / word_count))
            - (102 * (sentences_count / word_count))
        )

    def _count_sentences(self, text: str) -> int:
        text = text.strip()

        if not text:
            return 0

        count = len(SENTENCE_SPAN_REGEX.findall(text))

        if count == 0:
            return 1

        return count
    

    def compute_single(
        self,
        item: DimensionInput,
    ) -> float:
        return self._compute_text(
            self.get_text(item)
        )
    
    def inspection_debug_text(self) -> str:
        return (
            "Formula: "
            "206.84 - "
            "60 * (syllables / words) - "
            "102 * (sentences / words)"
        )