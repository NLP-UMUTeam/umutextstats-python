from umutextstats.config.params import dictionary_param, percentage_param
from umutextstats.dictionaries import DictionaryLoader
from umutextstats.dimensions.dimension_input import DimensionInput
from umutextstats.inspection.scalar_inspectable_dimension import (
    ScalarInspectableDimension,
)
from umutextstats.text.tokenization import get_lexical_tokens


AUX_VERB_HABER = {
    "ha",
    "habe",
    "habed",
    "haber",
    "habido",
    "habiendo",
    "habremos",
    "habrá",
    "habrán",
    "habrás",
    "habré",
    "habréis",
    "habría",
    "habríais",
    "habríamos",
    "habrían",
    "habrías",
    "habéis",
    "había",
    "habíais",
    "habíamos",
    "habían",
    "habías",
    "han",
    "has",
    "hay",
    "haya",
    "hayamos",
    "hayan",
    "hayas",
    "hayáis",
    "he",
    "hemos",
    "hube",
    "hubiera",
    "hubierais",
    "hubieran",
    "hubieras",
    "hubiere",
    "hubiereis",
    "hubieren",
    "hubieres",
    "hubieron",
    "hubiese",
    "hubieseis",
    "hubiesen",
    "hubieses",
    "hubimos",
    "hubiste",
    "hubisteis",
    "hubiéramos",
    "hubiéremos",
    "hubiésemos",
    "hubo",
}


class VerbPerDictionary(ScalarInspectableDimension):
    def __init__(
        self,
        key: str,
        dictionary_name: str,
        input_column: str = "text_norm",
        percentage: bool = True,
        dictionary_loader: DictionaryLoader | None = None,
    ):
        super().__init__(key=key, input_column=input_column)

        self.dictionary_name = dictionary_name
        self.percentage = percentage
        self.dictionary_loader = dictionary_loader or DictionaryLoader()

        dictionary_names = [
            name.strip()
            for name in dictionary_name.split("|")
            if name.strip()
        ]

        words = []

        for name in dictionary_names:
            entries = self.dictionary_loader.load(name)
            words.extend(entries.words)

        self.words = {
            entry.lower()
            for entry in words
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

    def _compute_text(
        self,
        text: str,
    ) -> float:
        words = get_lexical_tokens(text)
        total_words = len(words)

        if total_words == 0:
            return 0.0

        occurrences = 0
        aux_verb = ""

        for word in words:
            word = word.lower()
            candidate = f"{aux_verb}{word}"

            if candidate in self.words:
                occurrences += 1

            if word in AUX_VERB_HABER:
                aux_verb = f"{word} "
            else:
                aux_verb = ""

        if not self.percentage:
            return occurrences

        return (100 * occurrences) / total_words

    def inspection_debug_text(self) -> str:
        return (
            f"Loaded dictionary: {self.dictionary_name}\n"
            f"Dictionary entries: {len(self.words)}\n"
            "Matches simple verbs and haber + participle/periphrastic entries"
        )