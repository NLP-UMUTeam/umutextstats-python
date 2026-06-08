from dataclasses import dataclass

import regex as re

from umutextstats.config.params import param
from umutextstats.dimensions.dimension_input import DimensionInput
from umutextstats.inspection.scalar_inspectable_dimension import ScalarInspectableDimension
from umutextstats.inspection.iterable_inspectable_dimension import (
    IterableInspectableDimension,
)
from umutextstats.text.patterns import LEXICAL_TOKEN_REGEX
from umutextstats.text.syllables import count_syllables_text


@dataclass(frozen=True)
class CharacterMatch:
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
    def compute_single(
        self,
        item: DimensionInput,
    ) -> int:
        return len(
            LEXICAL_TOKEN_REGEX.findall(
                self.get_text(item)
            )
        )

    def compute(self, df):
        if "word_count" in df.columns:
            return df["word_count"]

        return (
            df[self.input_column]
            .fillna("")
            .astype(str)
            .apply(
                lambda text: len(
                    LEXICAL_TOKEN_REGEX.findall(text)
                )
            )
        )
    

class CharacterFrequencyDimension(IterableInspectableDimension):
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
        chars = param(dimension, "character", "")

        if chars == "SPACE":
            chars = " "

        return cls(
            key=dimension.key,
            chars=chars,
            input_column=input_column,
        )

    def iter_matches(self, text: str):
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

    def compute_single(
        self,
        item: DimensionInput,
    ) -> float:
        text = self.get_text(item)

        if not text:
            return 0.0

        count = self._count_chars(text)

        return (100 * count) / len(text)

    def compute(self, df):
        texts = (
            df[self.input_column]
            .fillna("")
            .astype(str)
        )

        counts = texts.apply(self._count_chars)
        total_length = texts.str.len()

        result = (
            100 * counts / total_length.replace(0, 1)
        ).astype(float)

        result[total_length == 0] = 0.0

        return result

    def _count_chars(
        self,
        text: str,
    ) -> int:
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
    def compute_single(
        self,
        item: DimensionInput,
    ) -> int:
        return count_syllables_text(
            self.get_text(item)
        )

    def compute(self, df):
        if "syllable_count" in df.columns:
            return df["syllable_count"]

        return (
            df[self.input_column]
            .fillna("")
            .astype(str)
            .apply(count_syllables_text)
        )


class SentenceCountDimension(ScalarInspectableDimension):
    def compute_single(
        self,
        item: DimensionInput,
    ) -> int:
        text = self.get_text(item).strip()

        if not text:
            return 0

        count = len(
            re.findall(
                r"[.!?]+",
                text,
            )
        )

        return count if count > 0 else 1

    def compute(self, df):
        if "sentence_count" in df.columns:
            return df["sentence_count"]

        text = (
            df[self.input_column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        sentence_count = text.str.count(r"[.!?]+")

        return sentence_count.where(
            (text == "") | (sentence_count > 0),
            1,
        )
