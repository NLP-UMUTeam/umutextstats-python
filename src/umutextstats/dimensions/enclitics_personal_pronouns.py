import unicodedata

import pandas as pd
import regex as re

from umutextstats.config.params import dictionary_param
from umutextstats.dictionaries import DictionaryLoader
from umutextstats.inspection.iterable_inspectable_dimension import (
    IterableInspectableDimension,
)
from umutextstats.text.patterns import ENCLITIC_REGEX
from umutextstats.text.tokenization import get_lexical_tokens


def remove_accents(text: str) -> str:
    """
    Remove accent marks from a text using Unicode normalization.
    """
    text = unicodedata.normalize("NFD", text)

    return "".join(
        ch
        for ch in text
        if unicodedata.category(ch) != "Mn"
    )


class EncliticsPersonalPronounsDictionary(IterableInspectableDimension):
    """
    Compute the percentage of words containing enclitic personal pronouns.

    Dictionary entries are used as base verbs. Patterns are compiled once
    during initialization for better runtime performance.
    """

    def __init__(
        self,
        key: str,
        dictionary_name: str,
        input_column: str = "text_norm",
        dictionary_loader: DictionaryLoader | None = None,
    ):
        super().__init__(key=key, input_column=input_column)

        self.dictionary_name = dictionary_name
        self.dictionary = dictionary_name
        self.dictionary_loader = dictionary_loader or DictionaryLoader()

        dictionary_names = [
            name.strip()
            for name in dictionary_name.split("|")
            if name.strip()
        ]

        verbs = []

        for name in dictionary_names:
            entries = self.dictionary_loader.load(name)
            verbs.extend(entries.words)

        self.verbs = [
            remove_accents(verb.lower())
            for verb in verbs
        ]

        # Compile all regex patterns once. This avoids rebuilding them
        # for every row during compute() or compute_single().
        self.patterns = [
            re.compile(
                rf"(?<!\p{{L}}){re.escape(verb)}"
                rf"{ENCLITIC_REGEX}(?!\p{{L}})",
                re.IGNORECASE,
            )
            for verb in self.verbs
        ]

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
        )

    def compute_single(
        self,
        row: pd.Series,
    ) -> float:
        """
        Compute the enclitic pronoun percentage for a single row.
        """
        text = self.get_text(row)
        count = self._count_text(text)

        total_words = len(
            get_lexical_tokens(text)
        )

        if total_words == 0:
            return 0.0

        return (100 * count) / total_words

    def compute(
        self,
        df: pd.DataFrame,
    ) -> pd.Series:
        """
        Compute the enclitic pronoun percentage for all rows.
        """
        texts = self.get_text_series(df)

        counts = texts.apply(self._count_text)
        total_words = texts.apply(
            lambda text: len(get_lexical_tokens(text))
        )

        result = (
            100 * counts / total_words.replace(0, 1)
        ).astype(float)

        result[total_words == 0] = 0.0

        return result

    def iter_matches(
        self,
        text: str,
    ):
        """
        Yield matches over normalized text.

        The inspected spans refer to the normalized text, because accents
        are removed before matching.
        """
        text = "" if text is None else str(text)
        normalized_text = remove_accents(text.lower())

        for pattern in self.patterns:
            yield from pattern.finditer(normalized_text)

    def _count_text(
        self,
        text: str,
    ) -> int:
        """
        Count enclitic pronoun matches in a text.
        """
        if not text:
            return 0

        return sum(
            1
            for _ in self.iter_matches(text)
        )

    def inspection_debug_text(self) -> str:
        """
        Return configuration details used during inspection.
        """
        return (
            f"Loaded dictionary: {self.dictionary_name}\n"
            f"Compiled patterns: {len(self.patterns)}\n"
            "Text is lowercased and accents are removed before matching"
        )