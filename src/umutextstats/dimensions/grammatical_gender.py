import pandas as pd

from umutextstats.config.params import (
    dictionary_param,
    disabled_regexp_param,
    param,
    percentage_param,
)
from umutextstats.dimensions.word_per_dictionary import WordPerDictionary
from umutextstats.text.patterns import POS_ITEM_REGEX


ALLOWED_POS = {
    "DET",
    "ADJ",
    "NOUN",
    "PROPN",
    "PRON",
    "VERB",
    "AUX",
}


class GrammaticalGenderDimension(WordPerDictionary):
    """
    Count dictionary matches only among POS-filtered words.

    This dimension uses `tagged_pos_column` to extract words whose POS tag
    belongs to `ALLOWED_POS`, then applies the dictionary matching logic
    inherited from WordPerDictionary.
    """

    def __init__(
        self,
        key: str,
        dictionary_name: str,
        input_column: str = "text_norm",
        tagged_pos_column: str = "tagged_pos",
        percentage: bool = True,
        use_regex: bool = True,
        dictionary_loader=None,
    ):
        super().__init__(
            key=key,
            dictionary_name=dictionary_name,
            input_column=input_column,
            percentage=percentage,
            use_regex=use_regex,
            dictionary_loader=dictionary_loader,
        )
        self.tagged_pos_column = tagged_pos_column

    @classmethod
    def from_config(
        cls,
        dimension,
        input_column: str = "text_norm",
    ):
        """
        Build the dimension from configuration.
        """
        return cls(
            key=dimension.key,
            dictionary_name=dictionary_param(dimension),
            input_column=input_column,
            tagged_pos_column=param(
                dimension,
                "tagged_pos_column",
                "tagged_pos",
            ),
            percentage=percentage_param(dimension),
            use_regex=not disabled_regexp_param(dimension),
        )

    def compute_single(
        self,
        row: pd.Series,
    ) -> float:
        """
        Compute the gender dictionary score for a single row.
        """
        tagged_pos = self.get_text(
            row=row,
            column=self.tagged_pos_column,
        )

        return self._compute_tagged_pos(tagged_pos)

    def compute(
        self,
        df: pd.DataFrame,
    ) -> pd.Series:
        """
        Compute the gender dictionary score for all rows.
        """
        return self.get_text_series(
            df=df,
            column=self.tagged_pos_column,
        ).apply(self._compute_tagged_pos)

    def _compute_tagged_pos(
        self,
        tagged_pos: str,
    ) -> float:
        """
        Compute dictionary matches over words filtered by POS tag.
        """
        filtered_words = self._get_words_filtered_by_pos(tagged_pos)
        total_words = len(filtered_words)

        if total_words == 0:
            return 0.0

        filtered_text = " ".join(filtered_words)
        count = self._count_text(filtered_text)

        if not self.percentage:
            return count

        return (100 * count) / total_words

    def _get_words_filtered_by_pos(
        self,
        tagged_text: str,
    ) -> list[str]:
        """
        Extract lowercase words whose POS tag is allowed.
        """
        words = []

        if not tagged_text:
            return words

        for sentence in tagged_text.split(" || "):
            for raw_item in sentence.split(", "):
                match = POS_ITEM_REGEX.fullmatch(raw_item.strip())

                if not match:
                    continue

                word = match.group("word") or ""
                tag = match.group("tag") or ""

                if tag in ALLOWED_POS:
                    words.append(word.lower())

        return words

    def inspection_debug_text(self) -> str:
        """
        Return configuration details used during inspection.
        """
        return (
            f"Loaded dictionary: {self.dictionary_name}\n"
            f"Allowed POS: {', '.join(sorted(ALLOWED_POS))}\n"
            f"Tagged POS column: {self.tagged_pos_column}\n"
            f"Use regex: {self.use_regex}\n"
            f"Percentage: {self.percentage}"
        )