# tests/test_dimensions_word_unique.py

import pandas as pd

from umutextstats.dimensions.word_unique import WordUniqueDimension


def compute(texts, percentage=True):
    df = pd.DataFrame({"text_norm": texts})

    dim = WordUniqueDimension(
        key="unique",
        percentage=percentage,
    )

    return list(dim.compute(df))


def test_empty():
    assert compute([""]) == [0.0]


def test_all_unique():
    assert compute(["uno dos tres"]) == [100.0]


def test_with_repetition():
    assert compute(["uno uno dos"]) == [(100 * 2) / 3]


def test_without_percentage():
    assert compute(["uno uno dos"], percentage=False) == [2]


def test_case_insensitive():
    assert compute(["Hola hola"]) == [50.0]


def test_multiple_rows():
    assert compute(["uno dos", "", "uno uno"]) == [100.0, 0.0, 50.0]