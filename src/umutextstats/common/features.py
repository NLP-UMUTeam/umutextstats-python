# src/umutextstats/common/features.py

from __future__ import annotations

import regex as re

from umutextstats.cache import CacheManager
from umutextstats.text.syllables import count_syllables_text
from umutextstats.text.sentence import count_sentences
from umutextstats.text.tokenization import get_lexical_tokens

COMMON_FEATURE_COLUMNS = [
    "text_length",
    "words",
    "word_count",
    "unique_word_count",
    "sentence_count",
    "syllable_count",
]



def add_common_features(
    df,
    input_column: str = "text_norm",
):
    text = df[input_column].fillna("").astype(str)

    df["text_length"] = text.str.len()

    df["words"] = text.apply(
        lambda value: [word.lower() for word in get_lexical_tokens (value)]
    )

    df["word_count"] = df["words"].apply(len)
    df["unique_word_count"] = df["words"].apply(lambda words: len(set(words)))
    df["sentence_count"] = text.apply(count_sentences)
    df["syllable_count"] = text.apply(count_syllables_text)

    return df


def add_common_features_cached(
    df,
    input_path: str,
    input_column: str = "text_norm",
    use_cache: bool = True,
    write_cache: bool = True,
    cache: CacheManager | None = None,
    head: int | None = None,
):
    cache = cache or CacheManager()

    params = {
        "input_column": input_column,
        "columns": COMMON_FEATURE_COLUMNS,
        "cache_version": 1,
        "head": head,
    }

    key = None

    if use_cache or write_cache:
        key = cache.build_key(input_path, "common_features", params)

    if use_cache and key is not None:
        cached = cache.load("common_features", key)

        if cached is not None:
            for column in COMMON_FEATURE_COLUMNS:
                if column in cached.columns:
                    df[column] = cached[column]
            return df

    df = add_common_features(
        df,
        input_column=input_column,
    )

    if write_cache and key is not None:
        cache.save(
            df[COMMON_FEATURE_COLUMNS],
            "common_features",
            key,
        )

    return df