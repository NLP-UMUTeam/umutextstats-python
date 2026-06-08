# tests/test_dimensions_word_length.py

import pandas as pd

from umutextstats.dimensions.length import WordLengthDimension


def compute(texts, length, comparator="=", percentage=True):
    df = pd.DataFrame({"text_norm": texts})

    dim = WordLengthDimension(
        key="word_length",
        length=length,
        comparator=comparator,
        percentage=percentage,
    )

    return list(dim.compute(df))


def test_greater_equal():
    assert compute(["hola mundo"], 5, ">=") == [50.0]


def test_greater():
    assert compute(["hola mundo"], 4, ">") == [50.0]


def test_less():
    assert compute(["hola mundo"], 5, "<") == [50.0]


def test_equal():
    assert compute(["hola mundo"], 4, "=") == [50.0]


def test_without_percentage():
    assert compute(["hola mundo"], 5, ">=", percentage=False) == [1]


def test_empty():
    assert compute([""], 5) == [0.0]