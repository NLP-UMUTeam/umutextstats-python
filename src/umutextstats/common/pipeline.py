from umutextstats.cache import CacheManager
from umutextstats.common.features import add_common_features


def add_common_features_cached(
    df,
    input_path: str,
    input_column: str = "text_norm",
    use_cache: bool = True,
    cache: CacheManager | None = None,
):
    cache = cache or CacheManager()

    params = {
        "input_column": input_column,
        "features": [
            "text_length",
            "words",
            "word_count",
            "unique_word_count",
            "sentence_count",
            "syllable_count",
        ],
    }

    key = cache.build_key(input_path, "common", params)

    if use_cache:
        cached = cache.load("common", key)
        if cached is not None:
            return cached

    df = add_common_features(
        df,
        input_column=input_column,
    )

    if use_cache:
        cache.save(df, "common", key)

    return df