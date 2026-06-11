from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from spylls.hunspell import Dictionary

from umutextstats.dimensions.enclitics_personal_pronouns import remove_accents
from umutextstats.inspection.iterable_inspectable_dimension import (
    IterableInspectableDimension,
)
from umutextstats.inspection.scalar_inspectable_dimension import (
    ScalarInspectableDimension,
)
from umutextstats.text.patterns import (
    INITIAL_TOKEN_EXCLUSING_NUMBERS_REGEX,
    INITIAL_TOKEN_REGEX,
    MENTION_REGEX,
    REPEATED_WORD_REGEX,
    SENTENCE_SPAN_REGEX,
    WORD_RE,
)
from umutextstats.text.sentence import get_sentences
from umutextstats.text.tokenization import get_lexical_tokens
from umutextstats.utils.accent_map import load_accent_map


AMBIGUOUS_DIACRITIC_WORDS = {
    "el", "tu", "mi", "si", "se", "te", "de",
    "mas", "aun", "solo",
}


@dataclass(frozen=True)
class SimpleMatch:
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


class ErrorCapitalizationStartingWithLowerCaseDimension(
    IterableInspectableDimension
):
    START_SYMBOLS = {"¿", "¡", "[", '"', "'", "-", "—", "_"}

    def __init__(
        self,
        key: str,
        input_column: str = "text_raw",
    ):
        super().__init__(key=key, input_column=input_column)

    def compute_single(
        self,
        row: pd.Series,
    ) -> float:
        return self._compute_text(self.get_text(row))

    def compute(
        self,
        df: pd.DataFrame,
    ) -> pd.Series:
        return self.get_text_series(df).apply(self._compute_text)

    def iter_sentences(self, text: str):
        text = "" if text is None else str(text)

        for match in SENTENCE_SPAN_REGEX.finditer(text):
            sentence = match.group(0).strip()

            if not sentence:
                continue

            if not any(char.isalpha() for char in sentence):
                continue

            yield SimpleMatch(
                sentence,
                match.start(),
                match.end(),
            )

    def iter_matches(self, text: str):
        for sentence_match in self.iter_sentences(text):
            if self._starts_with_lowercase(sentence_match.group(0)):
                yield sentence_match

    def _compute_text(self, text: str) -> float:
        sentences = list(self.iter_sentences(text))

        if not sentences:
            return 0.0

        errors = sum(
            1
            for sentence in sentences
            if self._starts_with_lowercase(sentence.group(0))
        )

        return (100 * errors) / len(sentences)

    def _starts_with_lowercase(self, sentence: str) -> bool:
        sentence = MENTION_REGEX.sub("", sentence).strip()

        if not sentence:
            return False

        for char in sentence:
            if char in self.START_SYMBOLS or char.isspace():
                continue

            if not char.isalpha():
                return False

            return char == char.lower() and char != char.upper()

        return False


class ErrorMispellingAccentsDimension(IterableInspectableDimension):
    def __init__(
        self,
        key: str,
        input_column: str = "text",
        language: str = "es",
        accent_map_path: str | None = None,
        percentage: bool = True,
    ):
        super().__init__(key=key, input_column=input_column)
        self.percentage = percentage
        self.accent_map = load_accent_map(
            language=language,
            path=accent_map_path,
        )

    def compute_single(
        self,
        row: pd.Series,
    ) -> float:
        return self._compute_text(self.get_text(row))

    def compute(
        self,
        df: pd.DataFrame,
    ) -> pd.Series:
        return self.get_text_series(df).apply(self._compute_text)

    def iter_matches(self, text: str):
        for match in WORD_RE.finditer("" if text is None else str(text)):
            word = match.group(0)

            if self._is_accent_error(word):
                yield SimpleMatch(word, match.start(), match.end())

    def _compute_text(self, text: str) -> float:
        words = get_lexical_tokens(text)

        if not words:
            return 0.0

        occurrences = sum(
            1
            for word in words
            if self._is_accent_error(word)
        )

        if not self.percentage:
            return occurrences

        return (100 * occurrences) / len(words)

    def _is_accent_error(self, word: str) -> bool:
        if word in AMBIGUOUS_DIACRITIC_WORDS:
            return False

        plain = remove_accents(word)

        if plain != word:
            return False

        return word in self.accent_map


class ErrorMispellingDimension(IterableInspectableDimension):
    def __init__(
        self,
        key: str,
        input_column: str = "text",
        language: str = "es_ES",
        dictionary_path: str = "/usr/share/hunspell/es_ES",
        missing_value: float | str = "",
    ):
        super().__init__(key=key, input_column=input_column)
        self.language = language
        self.dictionary_path = dictionary_path
        self.missing_value = missing_value
        self.dictionary = None
        self._known_cache: dict[str, bool] = {}

        aff_path = Path(f"{dictionary_path}.aff")
        dic_path = Path(f"{dictionary_path}.dic")

        if aff_path.exists() and dic_path.exists():
            self.dictionary = Dictionary.from_files(dictionary_path)

    def compute_single(
        self,
        row: pd.Series,
    ) -> float | str:
        if self.dictionary is None:
            return self.missing_value

        return self._compute_text(self.get_text(row))

    def compute(
        self,
        df: pd.DataFrame,
    ) -> pd.Series:
        if self.dictionary is None:
            return pd.Series(
                [self.missing_value] * len(df),
                index=df.index,
            )

        return self.get_text_series(df).apply(self._compute_text)

    def iter_matches(self, text: str):
        text = "" if text is None else str(text)

        if self.dictionary is None:
            return

        for match in WORD_RE.finditer(text):
            word = match.group(0)
            word_norm = word.lower()

            if not self._should_check_word(word, word_norm):
                continue

            if not self._is_known(word_norm):
                yield SimpleMatch(word, match.start(), match.end())

    def _compute_text(self, text: str) -> float:
        text = "" if text is None else str(text)
        checked = 0
        errors = 0

        for match in WORD_RE.finditer(text):
            word = match.group(0)
            word_norm = word.lower()

            if not self._should_check_word(word, word_norm):
                continue

            checked += 1

            if not self._is_known(word_norm):
                errors += 1

        if checked == 0:
            return 0.0

        return (100 * errors) / checked

    def _should_check_word(
        self,
        word: str,
        word_norm: str,
    ) -> bool:
        if not word:
            return False

        if len(word_norm) <= 1:
            return False

        if not word.isalpha():
            return False

        if word.isupper() and len(word) > 1:
            return False

        if any(c.islower() for c in word) and any(
            c.isupper()
            for c in word[1:]
        ):
            return False

        return True

    def _is_known(
        self,
        word_norm: str,
    ) -> bool:
        if word_norm not in self._known_cache:
            self._known_cache[word_norm] = self.dictionary.lookup(word_norm)

        return self._known_cache[word_norm]


class ErrorMiscTwoOrMoreEqualWordsDimension(ScalarInspectableDimension):
    def compute_single(
        self,
        row: pd.Series,
    ) -> int:
        return self._compute_text(self.get_text(row))

    def compute(
        self,
        df: pd.DataFrame,
    ) -> pd.Series:
        return self.get_text_series(df).apply(self._compute_text)

    def _compute_text(
        self,
        text: str,
    ) -> int:
        sentences = get_sentences(text)

        if not sentences:
            return 0

        return sum(
            self._count_repeated_words(sentence)
            for sentence in sentences
        )

    def _count_repeated_words(
        self,
        sentence: str,
    ) -> int:
        return sum(
            1
            for _ in REPEATED_WORD_REGEX.finditer(sentence)
        )


class ErrorStyleSentencesStartingWithNumbers(IterableInspectableDimension):
    def __init__(
        self,
        key: str,
        input_column: str = "text_raw",
    ):
        super().__init__(key=key, input_column=input_column)

    def compute_single(
        self,
        row: pd.Series,
    ) -> float:
        return self._compute_text(self.get_text(row))

    def compute(
        self,
        df: pd.DataFrame,
    ) -> pd.Series:
        return self.get_text_series(df).apply(self._compute_text)

    def iter_matches(self, text: str):
        for match in SENTENCE_SPAN_REGEX.finditer(text):
            sentence = match.group(0).strip()

            if not sentence or not any(char.isalnum() for char in sentence):
                continue

            if self._starts_with_number(sentence):
                yield SimpleMatch(sentence, match.start(), match.end())

    def _compute_text(
        self,
        text: str,
    ) -> float:
        sentences = self._split_sentences(text)

        if not sentences:
            return 0.0

        occurrences = sum(
            1
            for sentence in sentences
            if self._starts_with_number(sentence)
        )

        return (100 * occurrences) / len(sentences)

    def _split_sentences(
        self,
        text: str,
    ) -> list[str]:
        sentences = []

        for match in SENTENCE_SPAN_REGEX.finditer(text):
            sentence = match.group(0).strip()

            if not sentence:
                continue

            if not any(char.isalnum() for char in sentence):
                continue

            sentences.append(sentence)

        return sentences

    def _starts_with_number(
        self,
        sentence: str,
    ) -> bool:
        match = INITIAL_TOKEN_REGEX.search(sentence)

        if not match:
            return False

        return match.group(0)[0].isdigit()


class ErrorStyleSentencesStartingWithTheSameWord(ScalarInspectableDimension):
    def __init__(
        self,
        key: str,
        input_column: str = "text_raw",
    ):
        super().__init__(key=key, input_column=input_column)

    def compute_single(
        self,
        row: pd.Series,
    ) -> float:
        return self._compute_text(self.get_text(row))

    def compute(
        self,
        df: pd.DataFrame,
    ) -> pd.Series:
        return self.get_text_series(df).apply(self._compute_text)

    def _compute_text(
        self,
        text: str,
    ) -> float:
        sentences = self._split_sentences(text)

        if not sentences:
            return 0.0

        first_words = [
            first_word
            for sentence in sentences
            if (first_word := self._first_word(sentence)) is not None
        ]

        stats = Counter(first_words)

        occurrences = sum(
            count
            for count in stats.values()
            if count > 1
        )

        return (100 * occurrences) / len(sentences)

    def _split_sentences(
        self,
        text: str,
    ) -> list[str]:
        sentences = []

        for match in SENTENCE_SPAN_REGEX.finditer(text):
            sentence = match.group(0).strip()

            if not sentence:
                continue

            if not any(char.isalpha() for char in sentence):
                continue

            sentences.append(sentence)

        return sentences

    def _first_word(
        self,
        sentence: str,
    ) -> str | None:
        match = INITIAL_TOKEN_EXCLUSING_NUMBERS_REGEX.search(sentence)

        if not match:
            return None

        return match.group(0).lower()