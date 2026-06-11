from dataclasses import dataclass

import pandas as pd

from umutextstats.config.params import param
from umutextstats.inspection.iterable_inspectable_dimension import (
    IterableInspectableDimension,
)
from umutextstats.text.patterns import NER_ITEM_REGEX


NER_NORMALIZER_WORDS = "words"
NER_NORMALIZER_ENTITIES = "entities"


@dataclass(frozen=True)
class NERMatch:
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


class NERTaggingTag(IterableInspectableDimension):
    """
    Compute the percentage of NER entities matching a configured tag.

    The denominator can be either:
    - the number of detected entities
    - the number of whitespace-separated words in the tagged NER string
    """

    def __init__(
        self,
        key: str,
        tag: str | None = None,
        input_column: str = "tagged_ner",
        normalizer: str = NER_NORMALIZER_ENTITIES,
    ):
        super().__init__(key=key, input_column=input_column)
        self.tag = tag
        self.normalizer = normalizer

    @classmethod
    def from_config(
        cls,
        dimension,
        input_column: str = "tagged_ner",
    ):
        """
        Build the dimension from configuration.
        """
        return cls(
            key=dimension.key,
            tag=param(dimension, "tag"),
            input_column=param(
                dimension,
                "input_column",
                input_column,
            ),
            normalizer=param(
                dimension,
                "normalizer",
                NER_NORMALIZER_ENTITIES,
            ),
        )

    def compute_single(
        self,
        row: pd.Series,
    ) -> float:
        """
        Compute the NER tag percentage for a single row.
        """
        return self._compute_text(
            self.get_text(row)
        )

    def compute(
        self,
        df: pd.DataFrame,
    ) -> pd.Series:
        """
        Compute the NER tag percentage for all rows.
        """
        return self.get_text_series(df).apply(
            self._compute_text
        )

    def iter_matches(
        self,
        tagged_ner: str,
    ):
        """
        Yield matching NER entities for inspection.
        """
        tagged_ner = "" if tagged_ner is None else str(tagged_ner)

        for match in NER_ITEM_REGEX.finditer(tagged_ner):
            tag = match.group("tag") or ""
            text = match.group("text") or ""

            if self.tag and tag != self.tag:
                continue

            yield NERMatch(
                text=text,
                start_pos=match.start(),
                end_pos=match.end(),
            )

    def _compute_text(
        self,
        tagged_ner: str,
    ) -> float:
        """
        Compute the percentage of entities matching the configured NER tag.
        """
        tagged_ner = "" if tagged_ner is None else str(tagged_ner)

        if not self.tag:
            return 0.0

        entities = self._parse_entities(tagged_ner)

        matches = sum(
            1
            for entity in entities
            if entity["tag"] == self.tag
        )

        denominator = self._get_denominator(
            tagged_ner=tagged_ner,
            entities=entities,
        )

        if denominator == 0:
            return 0.0

        return (100 * matches) / denominator

    def _get_denominator(
        self,
        tagged_ner: str,
        entities: list[dict[str, str]],
    ) -> int:
        """
        Return the denominator according to the configured normalizer.
        """
        if self.normalizer == NER_NORMALIZER_ENTITIES:
            return len(entities)

        if self.normalizer == NER_NORMALIZER_WORDS:
            return len(tagged_ner.split())

        raise ValueError(f"Unknown NER normalizer: {self.normalizer}")

    def _parse_entities(
        self,
        tagged_ner: str,
    ) -> list[dict[str, str]]:
        """
        Parse tagged NER text into entity dictionaries.
        """
        if not tagged_ner:
            return []

        return [
            {
                "tag": match.group("tag") or "",
                "text": match.group("text") or "",
            }
            for match in NER_ITEM_REGEX.finditer(tagged_ner)
        ]

    def inspection_debug_text(self) -> str:
        """
        Return configuration details used during inspection.
        """
        return (
            f"NER tag: {self.tag}\n"
            f"Input column: {self.input_column}\n"
            f"Normalizer: {self.normalizer}"
        )