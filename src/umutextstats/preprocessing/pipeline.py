from umutextstats.cache import CacheManager
from umutextstats.preprocessing import preprocess_dataframe
from umutextstats.preprocessing.normalizer import TextNormalizer, default_normalizer


def preprocess_dataframe_cached(
    df,
    input_path: str,
    input_column: str = "text_raw",
    output_column: str = "text_norm",
    normalizer: TextNormalizer | None = None,
    show_progress: bool = True,
    use_cache: bool = True,
    write_cache: bool = True,
    cache: CacheManager | None = None,
    head: int | None = None,
):
    normalizer = normalizer or default_normalizer()
    cache = cache or CacheManager()

    params = {
        "input_column": input_column,
        "output_column": output_column,
        "normalizer": repr([step.__class__.__name__ for step in normalizer.steps]),
        "cache_version": 2,
        "head": head,
    }

    key = None

    if use_cache or write_cache:
        key = cache.build_key(input_path, "preprocess", params)

    if use_cache and key is not None:
        cached = cache.load("preprocess", key)
        if cached is not None:
            if output_column in cached.columns:
                df[output_column] = cached[output_column]
                return df

    df = preprocess_dataframe(
        df,
        input_column=input_column,
        output_column=output_column,
        normalizer=normalizer,
        show_progress=show_progress,
    )

    if write_cache and key is not None:
        cache.save(
            df[[output_column]],
            "preprocess",
            key,
        )

    return df