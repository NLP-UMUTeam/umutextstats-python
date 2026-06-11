from dataclasses import dataclass

import pandas as pd
import regex as re

from umutextstats.inspection.iterable_inspectable_dimension import (
    IterableInspectableDimension,
)
from umutextstats.inspection.scalar_inspectable_dimension import (
    ScalarInspectableDimension,
)
from umutextstats.config.params import param
from umutextstats.text.patterns import LEXICAL_TOKEN_REGEX
from umutextstats.text.syllables import count_syllables_text


@dataclass(frozen=True)
class CharacterMatch:
    """
    Regex-like match object used by the inspection layer.
    """

    text: str
    start_pos: int
    end_pos: int

    def group(self, index: int = 0) -> str:
        if index != 0:
            raise IndexError(index)

        return self.text

    def start(self) -> int:
        return self.start_pos

    def end(self) -> int:
        return self.end_pos


class WordCountDimension(ScalarInspectableDimension):
    """
    Count lexical tokens in the configured input column.
    """

    def compute_single(
        self,
        row: pd.Series,
    ) -> int:
        """
        Compute word count for a single row.
        """
        return len(
            LEXICAL_TOKEN_REGEX.findall(
                self.get_text(row)
            )
        )

    def compute(
        self,
        df: pd.DataFrame,
    ) -> pd.Series:
        """
        Compute word count for all rows.

        If the DataFrame already contains `word_count`, reuse it.
        """
        if "word_count" in df.columns:
            return df["word_count"]

        return self.get_text_series(df).apply(
            lambda text: len(
                LEXICAL_TOKEN_REGEX.findall(text)
            )
        )


class CharacterFrequencyDimension(IterableInspectableDimension):
    """
    Compute the percentage of selected characters in the configured text.

    The `character` config can be a literal character, a group of characters,
    or `SPACE`, which is converted to a single space. If `chars` is `\\s`,
    whitespace is matched through a compiled regex.
    """

    def __init__(
        self,
        key: str,
        chars: str,
        input_column: str = "text_norm",
    ):
        super().__init__(
            key=key,
            input_column=input_column,
        )

        self.raw_chars = chars or ""

        # Compile only once. This avoids recompiling on every row.
        if self.raw_chars == r"\s":
            self.pattern = re.compile(r"\s")
            self.chars = None
        else:
            self.pattern = None
            self.chars = set(self.raw_chars)

    @classmethod
    def from_config(
        cls,
        dimension,
        input_column: str = "text_norm",
    ):
        """
        Build the dimension from configuration.
        """
        chars = param(dimension, "character", "")

        if chars == "SPACE":
            chars = " "

        return cls(
            key=dimension.key,
            chars=chars,
            input_column=input_column,
        )

    def compute_single(
        self,
        row: pd.Series,
    ) -> float:
        """
        Compute character frequency for a single row.
        """
        text = self.get_text(row)

        if not text:
            return 0.0

        count = self._count_chars(text)

        return (100 * count) / len(text)

    def compute(
        self,
        df: pd.DataFrame,
    ) -> pd.Series:
        """
        Compute character frequency for all rows.
        """
        texts = self.get_text_series(df)

        counts = texts.apply(self._count_chars)
        total_length = texts.str.len()

        result = (
            100 * counts / total_length.replace(0, 1)
        ).astype(float)

        result[total_length == 0] = 0.0

        return result

    def iter_matches(
        self,
        text: str,
    ):
        """
        Yield matching characters for inspection.
        """
        text = "" if text is None else str(text)

        if not text:
            return

        if self.pattern is not None:
            yield from self.pattern.finditer(text)
            return

        if not self.chars:
            return

        for index, char in enumerate(text):
            if char in self.chars:
                yield CharacterMatch(
                    text=char,
                    start_pos=index,
                    end_pos=index + 1,
                )

    def _count_chars(
        self,
        text: str,
    ) -> int:
        """
        Count selected characters in a text.
        """
        if not text:
            return 0

        if self.pattern is not None:
            return len(self.pattern.findall(text))

        if not self.chars:
            return 0

        return sum(
            text.count(char)
            for char in self.chars
        )


class SyllableCountDimension(ScalarInspectableDimension):
    """
    Count syllables in the configured input column.
    """

    def compute_single(
        self,
        row: pd.Series,
    ) -> int:
        """
        Compute syllable count for a single row.
        """
        return count_syllables_text(
            self.get_text(row)
        )

    def compute(
        self,
        df: pd.DataFrame,
    ) -> pd.Series:
        """
        Compute syllable count for all rows.

        If the DataFrame already contains `syllable_count`, reuse it.
        """
        if "syllable_count" in df.columns:
            return df["syllable_count"]

        return self.get_text_series(df).apply(
            count_syllables_text
        )


class SentenceCountDimension(ScalarInspectableDimension):
    """
    Count sentences using sentence-ending punctuation.

    Empty texts return 0. Non-empty texts without punctuation return 1.
    """

    def compute_single(
        self,
        row: pd.Series,
    ) -> int:
        """
        Compute sentence count for a single row.
        """
        text = self.get_text(row).strip()

        if not text:
            return 0

        count = len(
            re.findall(
                r"[.!?]+",
                text,
            )
        )

        return count if count > 0 else 1

    def compute(
        self,
        df: pd.DataFrame,
    ) -> pd.Series:
        """
        Compute sentence count for all rows.

        If the DataFrame already contains `sentence_count`, reuse it.
        """
        if "sentence_count" in df.columns:
            return df["sentence_count"]

        text = self.get_text_series(df).str.strip()
        sentence_count = text.str.count(r"[.!?]+")

        return sentence_count.where(
            (text == "") | (sentence_count > 0),
            1,
        )