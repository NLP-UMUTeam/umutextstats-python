import unicodedata

import regex as re

from umutextstats.config.params import dictionary_param
from umutextstats.dictionaries import DictionaryLoader
from umutextstats.dimensions.dimension_input import DimensionInput
from umutextstats.inspection.iterable_inspectable_dimension import IterableInspectableDimension
from umutextstats.text.patterns import ENCLITIC_REGEX
from umutextstats.text.tokenization import get_lexical_tokens


def remove_accents(text: str) -> str:
    text = unicodedata.normalize("NFD", text)

    return "".join(
        ch
        for ch in text
        if unicodedata.category(ch) != "Mn"
    )


class EncliticsPersonalPronounsDictionary(IterableInspectableDimension):
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
        return cls(
            key=dimension.key,
            dictionary_name=dictionary_param(dimension),
            input_column=input_column,
        )

    def compute_single(
        self,
        item: DimensionInput,
    ) -> float:
        text = self.get_text(item)
        count = self._count_text(text)

        total_words = len(get_lexical_tokens(text))

        if total_words == 0:
            return 0.0

        return (100 * count) / total_words

    def compute(self, df):
        texts = df[self.input_column].fillna("").astype(str)

        counts = texts.apply(self._count_text)
        total_words = texts.apply(
            lambda text: len(get_lexical_tokens(text))
        )

        result = (
            100 * counts / total_words.replace(0, 1)
        ).astype(float)

        result[total_words == 0] = 0.0

        return result

    def iter_matches(self, text: str):
        text = "" if text is None else str(text)
        normalized_text = remove_accents(text.lower())

        for pattern in self.patterns:
            for match in pattern.finditer(normalized_text):
                yield match

    def _count_text(self, text: str) -> int:
        if not text:
            return 0

        return sum(1 for _ in self.iter_matches(text))

    def inspection_debug_text(self) -> str:
        return (
            f"Loaded dictionary: {self.dictionary_name}\n"
            f"Compiled patterns: {len(self.patterns)}\n"
            "Text is lowercased and accents are removed before matching"
        )