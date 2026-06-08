from dataclasses import dataclass

from umutextstats.config.params import param
from umutextstats.dimensions.dimension_input import DimensionInput
from umutextstats.inspection.iterable_inspectable_dimension import (
    IterableInspectableDimension,
)
from umutextstats.text.patterns import NER_ITEM_REGEX


@dataclass(frozen=True)
class NERMatch:
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
    def __init__(
        self,
        key: str,
        tag: str | None = None,
        input_column: str = "tagged_ner",
    ):
        super().__init__(key=key, input_column=input_column)
        self.tag = tag

    @classmethod
    def from_config(
        cls,
        dimension,
        input_column: str = "tagged_ner",
    ):
        return cls(
            key=dimension.key,
            tag=param(dimension, "tag"),
            input_column=param(
                dimension,
                "input_column",
                "tagged_ner",
            ),
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

    def iter_matches(self, tagged_ner: str):
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
        entities = self._parse_entities(tagged_ner)

        if not entities:
            return 0.0

        if not self.tag:
            return 0.0

        matches = sum(
            1
            for entity in entities
            if entity["tag"] == self.tag
        )

        return (100 * matches) / len(entities)

    def _parse_entities(
        self,
        tagged_ner: str,
    ) -> list[dict[str, str]]:
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
        return (
            f"NER tag: {self.tag}\n"
            f"Input column: {self.input_column}"
        )