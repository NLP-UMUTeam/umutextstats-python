from umutextstats.dimensions.dimension_input import DimensionInput
from umutextstats.inspection.scalar_inspectable_dimension import (
    ScalarInspectableDimension,
)
from umutextstats.text.syllables import count_syllables_text
from umutextstats.text.sentence import count_sentences
from umutextstats.text.tokenization import get_lexical_tokens


class PerspicuityDimension(ScalarInspectableDimension):
    def compute_single(self, item: DimensionInput) -> float:
        return self._compute_text(self.get_text(item))

    def compute(self, df):
        return (
            df[self.input_column]
            .fillna("")
            .astype(str)
            .apply(self._compute_text)
        )

    def _compute_text(self, text: str) -> float:
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
        return (
            "Formula: 206.835 - "
            "62.3 * (syllables / words) - "
            "(words / sentences)"
        )