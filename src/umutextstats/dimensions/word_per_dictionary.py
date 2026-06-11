from __future__ import annotations

from collections import Counter

import numpy as np
import pandas as pd
import regex as re

from umutextstats.config.params import (
    dictionary_param,
    disabled_regexp_param,
    param,
    percentage_param,
)
from umutextstats.dictionaries import DictionaryLoader
from umutextstats.inspection.iterable_inspectable_dimension import (
    IterableInspectableDimension,
)
from umutextstats.text.patterns import LEXICAL_TOKEN_REGEX, POS_ITEM_REGEX
from umutextstats.text.tokenization import get_lexical_tokens


class WordPerDictionary(IterableInspectableDimension):
    def __init__(
        self,
        key: str,
        dictionary_name: str,
        input_column: str = "text_norm",
        pos_tag: str | list[str] | None = None,
        pos_input_column: str | None = "tagged_pos",
        percentage: bool = True,
        use_regex: bool = True,
        dictionary_loader: DictionaryLoader | None = None,
    ):
        super().__init__(key=key, input_column=input_column)

        self.dictionary_name = dictionary_name
        self.dictionary = dictionary_name
        self.percentage = percentage
        self.use_regex = use_regex
        self.pos_input_column = pos_input_column
        self.dictionary_loader = dictionary_loader or DictionaryLoader()

        if isinstance(pos_tag, str):
            pos_tag = [pos_tag]

        self.pos_tag = pos_tag or None

        dictionary_names = [
            name.strip()
            for name in dictionary_name.split("|")
            if name.strip()
        ]

        entries = []
        exceptions = []

        for name in dictionary_names:
            dictionary_entries = self.dictionary_loader.load(name)
            entries.extend(dictionary_entries.words)
            exceptions.extend(dictionary_entries.exceptions)

        self.entries = entries
        self.exceptions = exceptions

        # Compile dictionary patterns once at initialization time.
        # This is important because this dimension may run over many rows.
        if self.use_regex:
            self.patterns = self._compile_patterns(self.entries, kind="word")
            self.exception_patterns = self._compile_patterns(
                self.exceptions,
                kind="exception",
            )
            self.words = None
            self.exception_words = None
        else:
            self.patterns = None
            self.exception_patterns = None
            self.words = {word.lower() for word in self.entries}
            self.exception_words = {
                word.lower()
                for word in self.exceptions
            }

    @classmethod
    def from_config(
        cls,
        dimension,
        input_column: str = "text_norm",
    ):
        return cls(
            key=dimension.key,
            dictionary_name=dictionary_param(dimension),
            input_column=input_column,
            percentage=percentage_param(dimension),
            use_regex=not disabled_regexp_param(dimension),
            pos_tag=param(dimension, "pos_tag", None),
            pos_input_column=param(
                dimension,
                "pos_input_column",
                "tagged_pos",
            ),
        )

    def compute_single(
        self,
        row: pd.Series,
    ) -> float:
        """
        Compute the dictionary count or percentage for a single row.
        """
        text = self.get_text(row)

        if self.pos_tag:
            tagged_pos = self._get_tagged_pos(row)
            count = self._count_text_with_pos(text, tagged_pos)
        else:
            count = self._count_text(text)

        if not self.percentage:
            return count

        word_total = self._get_word_total(
            row=row,
            text=text,
        )

        if word_total == 0:
            return 0.0

        return (100.0 * count) / word_total

    def compute(
        self,
        df: pd.DataFrame,
    ) -> pd.Series:
        """
        Compute the dictionary count or percentage for all rows.

        Regex patterns are compiled once in `__init__`; this method only
        applies those already compiled patterns to the input texts.
        """
        texts = self.get_text_series(df)

        if self.pos_tag:
            tagged_texts = self.get_text_series(
                df=df,
                column=self.pos_input_column or "tagged_pos",
            )

            counts = pd.Series(
                (
                    self._count_text_with_pos(text, tagged_pos)
                    for text, tagged_pos in zip(texts, tagged_texts)
                ),
                index=df.index,
            )
        else:
            counts = texts.apply(self._count_text)

        if not self.percentage:
            return counts

        word_totals = self._get_word_totals(
            df=df,
            texts=texts,
        )

        counts_array = counts.to_numpy(dtype=float)
        word_totals_array = word_totals.to_numpy(dtype=float)
        percentages = np.zeros_like(counts_array, dtype=float)

        np.divide(
            100.0 * counts_array,
            word_totals_array,
            out=percentages,
            where=word_totals_array != 0,
        )

        return pd.Series(percentages, index=df.index)

    def inspect(
        self,
        row: pd.Series,
    ):
        """
        Inspect positive and discarded dictionary matches for a single row.
        """
        text = self.get_text(row)

        if self.pos_tag:
            tagged_pos = self._get_tagged_pos(row)

            matches_iter = self.iter_positive_matches_with_pos(
                text=text,
                tagged_pos=tagged_pos,
            )
            discarded_iter = self.iter_exception_matches_with_pos(
                text=text,
                tagged_pos=tagged_pos,
            )
        else:
            matches_iter = self.iter_positive_matches(text)
            discarded_iter = self.iter_exception_matches(text)

        matches = [
            self._to_inspect_match(match)
            for match in matches_iter
        ]

        discarded_matches = [
            self._to_inspect_match(match)
            for match in discarded_iter
        ]

        return self._build_inspection(
            matches=matches,
            discarded_matches=discarded_matches,
        )

    def iter_matches(
        self,
        text: str,
    ):
        yield from self.iter_positive_matches(text)

    def iter_discarded_matches(
        self,
        text: str,
    ):
        yield from self.iter_exception_matches(text)

    def iter_positive_matches(
        self,
        text: str,
    ):
        text = "" if text is None else str(text)

        if self.use_regex:
            for pattern in self.patterns:
                yield from pattern.finditer(text)
            return

        for match in LEXICAL_TOKEN_REGEX.finditer(text):
            if match.group(0).lower() in self.words:
                yield match

    def iter_exception_matches(
        self,
        text: str,
    ):
        text = "" if text is None else str(text)

        if self.use_regex:
            for pattern in self.exception_patterns:
                yield from pattern.finditer(text)
            return

        for match in LEXICAL_TOKEN_REGEX.finditer(text):
            if match.group(0).lower() in self.exception_words:
                yield match

    def iter_positive_matches_with_pos(
        self,
        text: str,
        tagged_pos: str,
    ):
        if not self.pos_tag:
            yield from self.iter_positive_matches(text)
            return

        allowed = self._allowed_pos_counter(tagged_pos)

        for match in self.iter_positive_matches(text):
            word = match.group(0).lower()

            if allowed[word] <= 0:
                continue

            allowed[word] -= 1
            yield match

    def iter_exception_matches_with_pos(
        self,
        text: str,
        tagged_pos: str,
    ):
        if not self.pos_tag:
            yield from self.iter_exception_matches(text)
            return

        allowed = self._allowed_pos_counter(tagged_pos)

        for match in self.iter_exception_matches(text):
            word = match.group(0).lower()

            if allowed[word] <= 0:
                continue

            allowed[word] -= 1
            yield match

    def _compile_patterns(
        self,
        entries: list[str],
        kind: str,
    ):
        """
        Compile dictionary entries once.

        The compiled regex objects are reused by compute, compute_single,
        and inspection methods.
        """
        patterns = []

        for line_number, entry in enumerate(entries, start=1):
            pattern = rf"(?<!\p{{L}}){entry}(?!\p{{L}})"

            try:
                patterns.append(re.compile(pattern, re.IGNORECASE))
            except re.error as exc:
                raise ValueError(
                    f"Invalid regex in dictionary '{self.dictionary_name}' "
                    f"({kind}) at line {line_number}: {entry!r}. "
                    f"Compiled pattern: {pattern!r}. "
                    f"Regex error: {exc}"
                ) from exc

        return patterns

    def _count_text(
        self,
        text: str,
    ) -> int:
        if not text:
            return 0

        if self.use_regex:
            positive_count = self._count_regex_patterns(
                text=text,
                patterns=self.patterns,
            )
            exception_count = self._count_regex_patterns(
                text=text,
                patterns=self.exception_patterns,
            )
        else:
            positive_count = self._count_plain_words(
                text=text,
                words=self.words,
            )
            exception_count = self._count_plain_words(
                text=text,
                words=self.exception_words,
            )

        return max(positive_count - exception_count, 0)

    def _count_text_with_pos(
        self,
        text: str,
        tagged_pos: str,
    ) -> int:
        if not text or not tagged_pos:
            return 0

        available = self._allowed_pos_counter(tagged_pos)

        if not available:
            return 0

        if self.use_regex:
            positive_count = self._count_regex_pos_matches(
                text=text,
                patterns=self.patterns,
                available=available.copy(),
            )
            exception_count = self._count_regex_pos_matches(
                text=text,
                patterns=self.exception_patterns,
                available=available.copy(),
            )
        else:
            positive_count = self._count_plain_pos_matches(
                text=text,
                words=self.words,
                available=available.copy(),
            )
            exception_count = self._count_plain_pos_matches(
                text=text,
                words=self.exception_words,
                available=available.copy(),
            )

        return max(positive_count - exception_count, 0)

    def _count_regex_patterns(
        self,
        text: str,
        patterns,
    ) -> int:
        return sum(
            len(pattern.findall(text))
            for pattern in patterns
        )

    def _count_regex_pos_matches(
        self,
        text: str,
        patterns,
        available: Counter,
    ) -> int:
        count = 0

        for pattern in patterns:
            for match in pattern.finditer(text):
                matched = match.group(0).lower()

                if available[matched] <= 0:
                    continue

                available[matched] -= 1
                count += 1

        return count

    def _count_plain_words(
        self,
        text: str,
        words: set[str],
    ) -> int:
        return sum(
            1
            for word in get_lexical_tokens(text)
            if word.lower() in words
        )

    def _count_plain_pos_matches(
        self,
        text: str,
        words: set[str],
        available: Counter,
    ) -> int:
        count = 0

        for word in get_lexical_tokens(text):
            word = word.lower()

            if available[word] <= 0:
                continue

            available[word] -= 1

            if word in words:
                count += 1

        return count

    def _allowed_pos_counter(
        self,
        tagged_pos: str,
    ) -> Counter:
        return Counter(
            item["word"].lower()
            for item in self._parse_tagged_pos(tagged_pos)
            if item["tag"] in self.pos_tag
        )

    def _parse_tagged_pos(
        self,
        tagged_pos: str,
    ) -> list[dict[str, str]]:
        if not tagged_pos:
            return []

        items = []

        for sentence in tagged_pos.split(" || "):
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

    def _get_tagged_pos(
        self,
        row: pd.Series,
    ) -> str:
        return self.get_text(
            row=row,
            column=self.pos_input_column or "tagged_pos",
        )

    def _get_word_total(
        self,
        row: pd.Series,
        text: str,
    ) -> int:
        word_count = self.get_value(
            row=row,
            column="word_count",
        )

        if word_count is not None:
            try:
                return int(word_count)
            except (TypeError, ValueError):
                pass

        return len(get_lexical_tokens(text))

    def _get_word_totals(
        self,
        df: pd.DataFrame,
        texts: pd.Series,
    ) -> pd.Series:
        if "word_count" in df.columns:
            return pd.to_numeric(
                df["word_count"],
                errors="coerce",
            ).fillna(0)

        return texts.apply(
            lambda text: len(get_lexical_tokens(text))
        )

    def _build_inspection(
        self,
        matches,
        discarded_matches,
    ):
        from umutextstats.inspection.models import DimensionInspection

        return DimensionInspection(
            key=self.key,
            class_name=self.__class__.__name__,
            pattern=None,
            dictionary=self.dictionary_name,
            matches=matches,
            discarded_matches=discarded_matches,
            debug_text=self.inspection_debug_text(),
        )

    def inspection_debug_text(self) -> str:
        parts = [
            f"Loaded dictionary: {self.dictionary_name}",
            f"Use regex: {self.use_regex}",
            f"Percentage: {self.percentage}",
        ]

        if self.pos_tag:
            parts.append(f"POS filter: {', '.join(self.pos_tag)}")
            parts.append(f"POS input column: {self.pos_input_column}")

        return "\n".join(parts)