# tests/test_dimensions_character_count.py

import pandas as pd

from umutextstats.dimensions.character_count import CharacterCountDimension


def compute(texts, chars):
    df = pd.DataFrame({"text_norm": texts})
    dim = CharacterCountDimension(key="chars", chars=chars)
    return list(dim.compute(df))


def test_single_character_count_percentage():
    assert compute(["hola"], "a") == [25.0]


def test_multiple_character_count_percentage():
    assert compute(["banana"], "an") == [83.33333333333333]


def test_no_matches():
    assert compute(["hola"], "z") == [0.0]


def test_empty_text():
    assert compute([""], "a") == [0.0]


def test_empty_chars():
    assert compute(["hola"], "") == [0.0]


def test_multiple_rows():
    result = compute(["hola", "banana", ""], "a")

    assert result == [25.0, 50.0, 0.0]


def test_accents():
    assert compute(["camión"], "ó") == [16.666666666666668]