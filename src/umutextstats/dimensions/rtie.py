# src/umutextstats/dimensions/rtie.py

from __future__ import annotations

import statistics

from umutextstats.config.params import param
from umutextstats.dimensions.dimension_input import DimensionInput
from umutextstats.inspection.scalar_inspectable_dimension import (
    ScalarInspectableDimension,
)
from umutextstats.text.patterns import SENTENCE_SPAN_REGEX
from umutextstats.text.tokenization import get_lexical_tokens


class RTIEBaseDimension(ScalarInspectableDimension):
    def __init__(
        self,
        key: str,
        input_column: str = "text_norm",
        separator: str = "by-chunks",
        chunk_size: int = 1000,
    ):
        super().__init__(key=key, input_column=input_column)
        self.separator = separator or "by-chunks"
        self.chunk_size = int(chunk_size or 1000)

    @classmethod
    def from_config(
        cls,
        dimension,
        input_column: str = "text_norm",
    ):
        return cls(
            key=dimension.key,
            input_column=input_column,
            separator=param(dimension, "separator", "by-chunks"),
            chunk_size=int(param(dimension, "chunk_size", 1000) or 1000),
        )

    def compute_single(
        self,
        item: DimensionInput,
    ) -> float:
        return self._compute_text(self.get_text(item))

    def compute(self, df):
        return (
            df[self.input_column]
            .fillna("")
            .astype(str)
            .apply(self._compute_text)
        )

    def _ratios(self, text: str) -> list[float]:
        if self.separator == "whole":
            return [self._ttr_whole(text)]

        if self.separator == "by-sentence":
            return self._ttr_by_sentence(text)

        return self._ttr_by_chunks(text)

    def _ttr_whole(self, text: str) -> float:
        words = self._words(text)

        if not words:
            return 0.0

        return len(set(words)) / len(words)

    def _ttr_by_chunks(self, text: str) -> list[float]:
        words = self._words(text)

        if not words:
            return []

        ratios = []

        for start in range(0, len(words), self.chunk_size):
            chunk = words[start:start + self.chunk_size]

            if chunk:
                ratios.append(len(set(chunk)) / len(chunk))

        return ratios

    def _ttr_by_sentence(self, text: str) -> list[float]:
        ratios = []

        for sentence in self._sentences(text):
            words = self._words(sentence)

            if words:
                ratios.append(len(set(words)) / len(words))
            else:
                ratios.append(0.0)

        return ratios

    def _words(self, text: str) -> list[str]:
        return get_lexical_tokens(text)

    def _sentences(self, text: str) -> list[str]:
        return [
            match.group(0).strip()
            for match in SENTENCE_SPAN_REGEX.finditer(text)
            if match.group(0).strip()
        ]

    def inspection_debug_text(self) -> str:
        return (
            f"Separator: {self.separator}\n"
            f"Chunk size: {self.chunk_size}"
        )


class RTIEDimension(RTIEBaseDimension):
    def _compute_text(self, text: str) -> float:
        ratios = self._ratios(text)

        if not ratios:
            return 0.0

        return sum(ratios) / len(ratios)


class RTIEDeviationDimension(RTIEBaseDimension):
    def _compute_text(self, text: str) -> float:
        ratios = self._ratios(text)

        if len(ratios) <= 1:
            return 0.0

        return statistics.pstdev(ratios)