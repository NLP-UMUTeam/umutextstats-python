import pandas as pd

from umutextstats.inspection.iterable_inspectable_dimension import (
    IterableInspectableDimension,
)
from umutextstats.text.sentence import count_sentences
from umutextstats.text.tokenization import get_lexical_tokens


class WordPerSentenceDimension(IterableInspectableDimension):
    """
    Compute the average number of lexical words per sentence.
    """

    def compute_single(
        self,
        row: pd.Series,
    ) -> float:
        """
        Compute words per sentence for a single row.
        """
        return self._compute_text(
            self.get_text(row)
        )

    def compute(
        self,
        df: pd.DataFrame,
    ) -> pd.Series:
        """
        Compute words per sentence for all rows.
        """
        return self.get_text_series(df).apply(
            self._compute_text
        )

    def _compute_text(
        self,
        text: str,
    ) -> float:
        """
        Compute the average number of lexical words per sentence.
        """
        total_words = len(
            get_lexical_tokens(text)
        )

        if total_words == 0:
            return 0.0

        total_sentences = count_sentences(text)

        if total_sentences == 0:
            return 0.0

        return total_words / total_sentences