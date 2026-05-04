import regex as re

from umutextstats.dimensions.syllable_count import count_syllables_text
from umutextstats.dimensions.word_count import WORD_REGEX


SENTENCE_REGEX = re.compile(r"[.!?]+", re.UNICODE)


def count_sentences(text: str) -> int:
    text = (text or "").strip()

    if not text:
        return 0

    count = len(SENTENCE_REGEX.findall(text))

    return count if count > 0 else 1


def add_common_features(
    df,
    input_column: str = "text_norm",
):
    text = df[input_column].fillna("").astype(str)

    df["text_length"] = text.str.len()

    df["words"] = text.apply(
        lambda value: [word.lower() for word in WORD_REGEX.findall(value)]
    )

    df["word_count"] = df["words"].apply(len)
    df["unique_word_count"] = df["words"].apply(lambda words: len(set(words)))
    df["sentence_count"] = text.apply(count_sentences)
    df["syllable_count"] = text.apply(count_syllables_text)

    return df