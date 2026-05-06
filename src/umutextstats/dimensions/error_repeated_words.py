from umutextstats.dimensions.base import BaseDimension
from umutextstats.text.sentence import get_sentences
from umutextstats.text.tokenization import get_lexical_tokens


class ErrorMiscTwoOrMoreEqualWordsDimension(BaseDimension):
    def compute(self, df):
        return (
            df[self.input_column]
            .fillna("")
            .astype(str)
            .apply(self._compute_text)
        )

    def _compute_text(self, text: str) -> float:
        sentences = get_sentences(text)
        total_sentences = len(sentences)

        if total_sentences == 0:
            return 0.0

        occurrences = sum(
            self._count_repeated_words(sentence)
            for sentence in sentences
        )

        return (100 * occurrences) / total_sentences

    def _count_repeated_words(self, sentence: str) -> int:
        words = get_lexical_tokens(sentence)

        occurrences = 0

        for index in range(1, len(words)):
            word = words[index]
            previous = words[index - 1]

            if word.startswith("http"):
                continue

            if word == previous:
                occurrences += 1

        return occurrences