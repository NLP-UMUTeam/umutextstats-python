from __future__ import annotations

from dataclasses import dataclass

import regex as re

from umutextstats.config.params import param
from umutextstats.dimensions.dimension_input import DimensionInput
from umutextstats.inspection.iterable_inspectable_dimension import (
    IterableInspectableDimension,
)
from umutextstats.text.patterns import POS_ITEM_REGEX
from umutextstats.text.tokenization import get_lexical_tokens


VERB_FORM_BY_MODE = {
    "infinitive": "VerbForm=Inf",
    "gerund": "VerbForm=Ger",
    "participe": "VerbForm=Part",
    "participle": "VerbForm=Part",
}


@dataclass(frozen=True)
class PeriphrasisMatch:
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


class PeriphrasisDimension(IterableInspectableDimension):
    def __init__(
        self,
        key: str,
        auxiliar_verbs: str,
        input_column: str = "text_norm",
        tagged_pos_column: str = "tagged_pos",
    ):
        super().__init__(key=key, input_column=input_column)
        self.tagged_pos_column = tagged_pos_column
        self.auxiliar_verbs = self._parse_auxiliar_verbs(auxiliar_verbs)

    @classmethod
    def from_config(
        cls,
        dimension,
        input_column: str = "text_norm",
    ):
        return cls(
            key=dimension.key,
            auxiliar_verbs=param(dimension, "auxiliar_verbs", ""),
            input_column=input_column,
            tagged_pos_column=param(
                dimension,
                "tagged_pos_column",
                "tagged_pos",
            ),
        )

    def compute_single(
        self,
        item: DimensionInput,
    ) -> int:
        text = self.get_text(item)
        tagged_pos = self._get_tagged_pos(item)

        return self._compute_text(
            text=text,
            tagged_pos=tagged_pos,
        )

    def compute(self, df):
        return df.apply(self._compute_row, axis=1)

    def _compute_row(self, row) -> int:
        text = str(row.get(self.input_column, "") or "")
        tagged_pos = str(row.get(self.tagged_pos_column, "") or "")

        return self._compute_text(
            text=text,
            tagged_pos=tagged_pos,
        )

    def _compute_text(
        self,
        text: str,
        tagged_pos: str,
    ) -> int:
        return sum(
            1
            for _ in self._iter_periphrases(
                text=text,
                tagged_pos=tagged_pos,
            )
        )

    def inspect(self, item: DimensionInput):
        text = self.get_text(item)
        tagged_pos = self._get_tagged_pos(item)

        matches = [
            self._to_inspect_match(match)
            for match in self._iter_periphrases(
                text=text,
                tagged_pos=tagged_pos,
            )
        ]

        from umutextstats.inspection.models import DimensionInspection

        return DimensionInspection(
            key=self.key,
            class_name=self.__class__.__name__,
            pattern=None,
            dictionary=None,
            matches=matches,
            discarded_matches=[],
            debug_text=self._build_debug_text(item),
        )

    def iter_matches(self, text: str):
        # No se puede inspeccionar correctamente solo con text,
        # porque esta dimensión necesita tagged_pos.
        return []

    def _iter_periphrases(
        self,
        text: str,
        tagged_pos: str,
    ):
        words = get_lexical_tokens(text)
        tagged_words = self._parse_tagged_pos(tagged_pos)

        if not words or not tagged_words:
            return

        index = 0

        while index < len(words):
            matched = False

            for aux in self.auxiliar_verbs:
                if words[index] not in aux["forms"]:
                    continue

                next_index = index + 1

                if aux["linker_variants"]:
                    matched_linker = self._match_linker(
                        words=words,
                        start_index=next_index,
                        linker_variants=aux["linker_variants"],
                    )

                    if matched_linker is None:
                        continue

                    next_index += matched_linker

                if next_index >= len(words):
                    continue

                if next_index >= len(tagged_words):
                    continue

                if not self._matches_verb_mode(
                    tagged_words[next_index],
                    aux["mode"],
                ):
                    continue

                yield PeriphrasisMatch(
                    text=" ".join(words[index: next_index + 1]),
                    start_pos=index,
                    end_pos=next_index + 1,
                )

                index = next_index
                matched = True
                break

            index += 1

    def _get_tagged_pos(
        self,
        item: DimensionInput,
    ) -> str:
        tagged_pos = item.get_annotation(self.tagged_pos_column)

        if tagged_pos is not None:
            return str(tagged_pos)

        value = item.get(self.tagged_pos_column, "")

        return "" if value is None else str(value)

    def _parse_auxiliar_verbs(
        self,
        raw: str,
    ) -> list[dict]:
        auxiliaries = []

        if not raw:
            return auxiliaries

        for part in raw.split(","):
            part = part.strip()

            if not part or "+" not in part:
                continue

            left, mode = part.split("+", 1)
            mode = mode.strip()

            if mode not in VERB_FORM_BY_MODE:
                continue

            linker_variants = []

            linker_match = re.search(r"\((.*?)\)", left)

            if linker_match:
                linker_variants = [
                    linker.strip().lower().split()
                    for linker in linker_match.group(1).split("|")
                    if linker.strip()
                ]

            verb = re.sub(r"\([^)]+\)", "", left).strip().lower()

            forms = {
                verb,
                f"{verb}me",
                f"{verb}te",
                f"{verb}se",
                f"{verb}nos",
                f"{verb}on",
            }

            auxiliaries.append(
                {
                    "verb": verb,
                    "forms": forms,
                    "linker_variants": linker_variants,
                    "mode": mode,
                }
            )

        return auxiliaries

    def _match_linker(
        self,
        words,
        start_index: int,
        linker_variants: list[list[str]],
    ) -> int | None:
        for linker_tokens in linker_variants:
            end_index = start_index + len(linker_tokens)

            if tuple(words[start_index:end_index]) == tuple(linker_tokens):
                return len(linker_tokens)

        return None

    def _parse_tagged_pos(
        self,
        tagged_text: str,
    ) -> list[dict[str, str]]:
        if not tagged_text:
            return []

        items = []

        for sentence in tagged_text.split(" || "):
            for raw_item in sentence.split(", "):
                match = POS_ITEM_REGEX.fullmatch(raw_item.strip())

                if not match:
                    continue

                items.append(
                    {
                        "word": match.group("word") or "",
                        "tag": match.group("tag") or "",
                        "feats": match.group("feats") or "",
                    }
                )

        return items

    def _matches_verb_mode(
        self,
        item: dict[str, str],
        mode: str,
    ) -> bool:
        if item["tag"] not in {"VERB", "AUX"}:
            return False

        expected = VERB_FORM_BY_MODE.get(mode)

        if not expected:
            return False

        return expected in item["feats"]

    def inspection_debug_text(self) -> str:
        return (
            f"Auxiliary patterns: {len(self.auxiliar_verbs)}\n"
            f"Tagged POS column: {self.tagged_pos_column}"
        )